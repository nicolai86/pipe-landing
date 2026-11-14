#!/usr/bin/env python3
"""
Convert a Fusion 360 / Eagle / KiCad 3D PCB STEP assembly (and optional Eagle/Fusion .brd XML)
into the exact gzipped Three.js PBR mesh JSON (`*-mesh.json.gz`), gzipped STEP download (`*.step.gz`),
and optional 2D top-silkscreen SVG decal (`*-silkscreen.svg`) used by `build-guide.html` and
`hardware-thc.html`.

Usage:
  /opt/homebrew/Caskroom/miniconda/base/envs/fovnet_ml/bin/python scripts/convert_pcb_step.py \
      --step /path/to/board.step \
      --out-mesh assets/z-axis-thc-v2-mesh.json.gz \
      --out-step-gz assets/z-axis-thc-v2.step.gz \
      [--brd /path/to/board.brd --out-silkscreen assets/z-axis-thc-v2-silkscreen.svg]
"""

import argparse
import gzip
import html
import json
import math
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.Quantity import Quantity_Color
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_Label, TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from OCP.XCAFDoc import (
    XCAFDoc_ColorCurv,
    XCAFDoc_ColorGen,
    XCAFDoc_ColorSurf,
    XCAFDoc_ColorTool,
    XCAFDoc_DocumentTool,
    XCAFDoc_ShapeTool,
)


def classify_material(r: float, g: float, b: float) -> str:
    """Map sRGB [0..1] CAD face color to initPcbViewer() PBR material bucket."""
    mx = max(r, g, b)
    mn = min(r, g, b)
    chroma = mx - mn

    if g > 0.30 and g > r * 1.6 and g > b * 1.6:
        return "soldermask"
    if r > 0.90 and g > 0.90 and b > 0.90:
        return "silkscreen"
    if r > 0.85 and 0.55 <= g <= 0.85 and b < 0.30:
        return "copper"
    if 0.35 <= r <= 0.60 and 0.28 <= g <= 0.50 and 0.12 <= b <= 0.35 and (r - b) > 0.12:
        return "fr4"
    if 0.55 <= r <= 0.72 and 0.45 <= g <= 0.60 and 0.42 <= b <= 0.58 and r > g and chroma >= 0.06:
        return "ceramic"
    if b > 0.50 and b > r * 1.8:
        return "led"
    if mx <= 0.46 and chroma < 0.08:
        return "plastic"
    if mn >= 0.48 and mx <= 0.93 and chroma < 0.06:
        return "metal"
    return "default"


def generate_silkscreen_svg(brd_path: Path, out_svg_path: Path) -> None:
    """Extract top silkscreen (layers 21 tPlace & 25 tNames) from an Eagle/Fusion .brd XML file."""
    tree = ET.parse(brd_path)
    root = tree.getroot()
    board_el = root.find(".//board")
    if board_el is None:
        raise RuntimeError(f"No <board> element found in {brd_path}")

    # Determine board outline bounds from layer 20 (Dimension)
    bx_min, by_min, bx_max, by_max = 1e9, 1e9, -1e9, -1e9
    for w in board_el.findall("./plain/wire[@layer='20']"):
        for xk, yk in (("x1", "y1"), ("x2", "y2")):
            xv, yv = float(w.attrib[xk]), float(w.attrib[yk])
            bx_min = min(bx_min, xv)
            by_min = min(by_min, yv)
            bx_max = max(bx_max, xv)
            by_max = max(by_max, yv)

    if bx_max <= bx_min or by_max <= by_min:
        raise RuntimeError(f"Could not determine layer-20 board outline in {brd_path}")

    bw = bx_max - bx_min
    bh = by_max - by_min
    svg_w = 2048
    scale = svg_w / bw
    svg_h = max(1, int(round(bh * scale)))

    def map_pt(x_mm: float, y_mm: float):
        return (x_mm - bx_min) * scale, (by_max - y_mm) * scale

    packages = {}
    for lib in board_el.findall("./libraries/library"):
        lib_name = lib.attrib.get("name", "")
        for pkg in lib.findall("./packages/package"):
            packages[(lib_name, pkg.attrib.get("name", ""))] = pkg

    lines_svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">',
        '  <rect width="100%" height="100%" fill="none"/>',
    ]

    # Top plain silkscreen wires & texts (layers 21, 25)
    for w in board_el.findall("./plain/wire"):
        if w.attrib.get("layer") not in ("21", "25"):
            continue
        x1, y1 = map_pt(float(w.attrib["x1"]), float(w.attrib["y1"]))
        x2, y2 = map_pt(float(w.attrib["x2"]), float(w.attrib["y2"]))
        sw = max(2.4, float(w.attrib.get("width", "0.15")) * scale)
        lines_svg.append(
            f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#ffffff" stroke-width="{sw:.1f}" stroke-linecap="round"/>'
        )

    for t in board_el.findall("./plain/text"):
        if t.attrib.get("layer") not in ("21", "25") or not (t.text or "").strip():
            continue
        tx, ty = map_pt(float(t.attrib["x"]), float(t.attrib["y"]))
        fs = max(18.0, float(t.attrib.get("size", "1.0")) * scale * 1.15)
        rot_str = t.attrib.get("rot", "R0").lstrip("SMR")
        rot = float(rot_str) if rot_str else 0.0
        tr = f' transform="rotate({-rot:.1f} {tx:.1f} {ty:.1f})"' if abs(rot) > 0.1 else ""
        lines_svg.append(
            f'  <text x="{tx:.1f}" y="{ty:.1f}" font-family="monospace, sans-serif" '
            f'font-weight="bold" font-size="{fs:.1f}px" fill="#ffffff" '
            f'text-anchor="start" dominant-baseline="alphabetic"{tr}>{html.escape(t.text)}</text>'
        )

    # Element package silkscreen outlines & smashed attributes/names
    for el in board_el.findall("./elements/element"):
        rot_raw = el.attrib.get("rot", "R0")
        if "M" in rot_raw:
            continue  # Bottom-side mirrored component
        ex, ey = float(el.attrib["x"]), float(el.attrib["y"])
        deg = float(rot_raw.lstrip("SR") or "0")
        rad = math.radians(deg)
        ca, sa = math.cos(rad), math.sin(rad)

        pkg = packages.get((el.attrib.get("library", ""), el.attrib.get("package", "")))
        if pkg is not None:
            for w in pkg.findall("./wire"):
                if w.attrib.get("layer") != "21":
                    continue
                lx1, ly1 = float(w.attrib["x1"]), float(w.attrib["y1"])
                lx2, ly2 = float(w.attrib["x2"]), float(w.attrib["y2"])
                gx1, gy1 = ex + lx1 * ca - ly1 * sa, ey + lx1 * sa + ly1 * ca
                gx2, gy2 = ex + lx2 * ca - ly2 * sa, ey + lx2 * sa + ly2 * ca
                sx1, sy1 = map_pt(gx1, gy1)
                sx2, sy2 = map_pt(gx2, gy2)
                sw = max(2.4, float(w.attrib.get("width", "0.127")) * scale)
                lines_svg.append(
                    f'  <line x1="{sx1:.1f}" y1="{sy1:.1f}" x2="{sx2:.1f}" y2="{sy2:.1f}" '
                    f'stroke="#ffffff" stroke-width="{sw:.1f}" stroke-linecap="round"/>'
                )

        for attr in el.findall("./attribute"):
            if attr.attrib.get("name") != "NAME" or attr.attrib.get("layer") not in (None, "25", "21"):
                continue
            name_val = el.attrib.get("name", "")
            if not name_val:
                continue
            ax, ay = float(attr.attrib.get("x", ex)), float(attr.attrib.get("y", ey))
            sx, sy = map_pt(ax, ay)
            fs = max(18.0, float(attr.attrib.get("size", "0.8")) * scale * 1.15)
            arot_str = attr.attrib.get("rot", "R0").lstrip("SMR")
            arot = float(arot_str) if arot_str else 0.0
            tr = f' transform="rotate({-arot:.1f} {sx:.1f} {sy:.1f})"' if abs(arot) > 0.1 else ""
            lines_svg.append(
                f'  <text x="{sx:.1f}" y="{sy:.1f}" font-family="monospace, sans-serif" '
                f'font-weight="bold" font-size="{fs:.1f}px" fill="#ffffff" '
                f'text-anchor="middle" dominant-baseline="central"{tr}>{html.escape(name_val)}</text>'
            )

    lines_svg.append("</svg>\n")
    out_svg_path.parent.mkdir(parents=True, exist_ok=True)
    out_svg_path.write_text("\n".join(lines_svg), encoding="utf-8")
    print(f"Wrote silkscreen SVG: {out_svg_path} ({svg_w}x{svg_h})")


def convert_step_to_mesh_gz(
    step_path: Path,
    out_mesh_gz: Path,
    lin_deflection: float = 0.08,
    ang_deflection: float = 0.35,
) -> None:
    doc = TDocStd_Document(TCollection_ExtendedString("MDTV-XCAF"))
    reader = STEPCAFControl_Reader()
    reader.SetColorMode(True)
    reader.SetNameMode(True)

    status = reader.ReadFile(str(step_path))
    if int(status) != 1:
        raise RuntimeError(f"STEPCAFControl_Reader.ReadFile failed with status={status}")
    if not reader.Transfer(doc):
        raise RuntimeError("STEPCAFControl_Reader.Transfer failed")

    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    color_tool = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

    free_labels = TDF_LabelSequence()
    shape_tool.GetFreeShapes(free_labels)
    print(f"Loaded {step_path.name}: {free_labels.Length()} root XCAF label(s)")

    def get_srgb_shape(shape, fallback):
        if shape is None or shape.IsNull():
            return fallback
        col = Quantity_Color()
        for ctype in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen, XCAFDoc_ColorCurv):
            if color_tool.GetColor(shape, ctype, col):
                return (
                    round(Quantity_Color.Convert_LinearRGB_To_sRGB_s(col.Red()), 3),
                    round(Quantity_Color.Convert_LinearRGB_To_sRGB_s(col.Green()), 3),
                    round(Quantity_Color.Convert_LinearRGB_To_sRGB_s(col.Blue()), 3),
                )
        return fallback

    def get_srgb_label(label: TDF_Label, fallback):
        col = Quantity_Color()
        for ctype in (XCAFDoc_ColorSurf, XCAFDoc_ColorGen, XCAFDoc_ColorCurv):
            if XCAFDoc_ColorTool.GetColor_s(label, ctype, col):
                return (
                    round(Quantity_Color.Convert_LinearRGB_To_sRGB_s(col.Red()), 3),
                    round(Quantity_Color.Convert_LinearRGB_To_sRGB_s(col.Green()), 3),
                    round(Quantity_Color.Convert_LinearRGB_To_sRGB_s(col.Blue()), 3),
                )
        sh = XCAFDoc_ShapeTool.GetShape_s(label)
        return get_srgb_shape(sh, fallback)

    leaves = []

    def traverse(label: TDF_Label, parent_loc: TopLoc_Location, inherited_rgb):
        rgb = get_srgb_label(label, inherited_rgb)
        if XCAFDoc_ShapeTool.IsReference_s(label):
            ref = TDF_Label()
            if XCAFDoc_ShapeTool.GetReferredShape_s(label, ref):
                loc = parent_loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(label))
                traverse(ref, loc, rgb)
                return
        if XCAFDoc_ShapeTool.IsAssembly_s(label):
            comps = TDF_LabelSequence()
            XCAFDoc_ShapeTool.GetComponents_s(label, comps)
            for i in range(1, comps.Length() + 1):
                traverse(comps.Value(i), parent_loc, rgb)
            return
        sh = XCAFDoc_ShapeTool.GetShape_s(label)
        if sh is not None and not sh.IsNull():
            rgb = get_srgb_shape(sh, rgb)
            leaves.append((sh, parent_loc, rgb))

    ident = TopLoc_Location()
    for i in range(1, free_labels.Length() + 1):
        traverse(free_labels.Value(i), ident, (0.75, 0.75, 0.75))

    print(f"Leaf component instances: {len(leaves)}")

    # Tessellate each root assembly once in native C++ (parallel=True; OCCT automatically shares TShape meshes)
    for i in range(1, free_labels.Length() + 1):
        root_sh = XCAFDoc_ShapeTool.GetShape_s(free_labels.Value(i))
        if root_sh is not None and not root_sh.IsNull():
            BRepMesh_IncrementalMesh(root_sh, lin_deflection, False, ang_deflection, True)
    print(f"Tessellated {free_labels.Length()} root assembly shape(s) in parallel C++")

    buckets = {}
    global_min = [1e9, 1e9, 1e9]
    global_max = [-1e9, -1e9, -1e9]

    for sh, comp_loc, sh_rgb in leaves:
        sol_exp = TopExp_Explorer(sh, TopAbs_SOLID)
        sub_items = []
        while sol_exp.More():
            sol = sol_exp.Current()
            sol_exp.Next()
            sub_items.append((sol, get_srgb_shape(sol, sh_rgb)))
        if not sub_items:
            sub_items.append((sh, sh_rgb))

        for sub_sh, sub_rgb in sub_items:
            exp = TopExp_Explorer(sub_sh, TopAbs_FACE)
            while exp.More():
                face = TopoDS.Face_s(exp.Current())
                exp.Next()

                f_rgb = get_srgb_shape(face, sub_rgb)
                mat = classify_material(*f_rgb)
                bkey = (mat, f_rgb)
                if bkey not in buckets:
                    buckets[bkey] = {"positions": [], "normals": [], "indices": []}

                face_loc = TopLoc_Location()
                tri = BRep_Tool.Triangulation_s(face, face_loc)
                if tri is None:
                    continue

                total_trsf = comp_loc.Multiplied(face_loc).Transformation()
                is_rev = face.Orientation() == TopAbs_REVERSED
                has_normals = tri.HasNormals()

                b = buckets[bkey]
                base_idx = len(b["positions"]) // 3
                nb_nodes = tri.NbNodes()
                nb_tris = tri.NbTriangles()

                pts_cad = []
                for ni in range(1, nb_nodes + 1):
                    p = tri.Node(ni).Transformed(total_trsf)
                    x, y, z = p.X(), p.Y(), p.Z()
                    pts_cad.append((x, y, z))
                    if x < global_min[0]:
                        global_min[0] = x
                    if y < global_min[1]:
                        global_min[1] = y
                    if z < global_min[2]:
                        global_min[2] = z
                    if x > global_max[0]:
                        global_max[0] = x
                    if y > global_max[1]:
                        global_max[1] = y
                    if z > global_max[2]:
                        global_max[2] = z
                    b["positions"].extend([x, y, z])

                if has_normals:
                    for ni in range(1, nb_nodes + 1):
                        d = tri.Normal(ni).Transformed(total_trsf)
                        nx, ny, nz = d.X(), d.Y(), d.Z()
                        if is_rev:
                            nx, ny, nz = -nx, -ny, -nz
                        b["normals"].extend([nx, ny, nz])
                else:
                    vnorms = [[0.0, 0.0, 0.0] for _ in range(nb_nodes)]
                    for ti in range(1, nb_tris + 1):
                        t = tri.Triangle(ti)
                        i1, i2, i3 = t.Value(1) - 1, t.Value(2) - 1, t.Value(3) - 1
                        if is_rev:
                            i2, i3 = i3, i2
                        p1, p2, p3 = pts_cad[i1], pts_cad[i2], pts_cad[i3]
                        ux, uy, uz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
                        vx, vy, vz = p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2]
                        cx_n = uy * vz - uz * vy
                        cy_n = uz * vx - ux * vz
                        cz_n = ux * vy - uy * vx
                        for idx_v in (i1, i2, i3):
                            vnorms[idx_v][0] += cx_n
                            vnorms[idx_v][1] += cy_n
                            vnorms[idx_v][2] += cz_n
                    for vn in vnorms:
                        ln = math.hypot(vn[0], vn[1], vn[2])
                        if ln > 1e-12:
                            b["normals"].extend([vn[0] / ln, vn[1] / ln, vn[2] / ln])
                        else:
                            b["normals"].extend([0.0, 0.0, 1.0])

                for ti in range(1, nb_tris + 1):
                    t = tri.Triangle(ti)
                    i1, i2, i3 = t.Value(1) - 1, t.Value(2) - 1, t.Value(3) - 1
                    if is_rev:
                        i2, i3 = i3, i2
                    b["indices"].extend([base_idx + i1, base_idx + i2, base_idx + i3])

    span_x = global_max[0] - global_min[0]
    span_y = global_max[1] - global_min[1]
    span_z = global_max[2] - global_min[2]
    cx = 0.5 * (global_min[0] + global_max[0])
    cy = 0.5 * (global_min[1] + global_max[1])
    cz = 0.5 * (global_min[2] + global_max[2])
    print(f"CAD bounds (mm): dX={span_x:.3f}, dY={span_y:.3f}, dZ={span_z:.3f}")

    # CAD Z-up -> Three.js Y-up via Rx(-90 deg): (x - cx, z - cz, -(y - cy)) [det = +1]
    meshes_out = []
    fr4_min_x, fr4_max_x = 1e9, -1e9
    fr4_min_z, fr4_max_z = 1e9, -1e9
    fr4_max_y = -1e9

    for (mat, rgb), b in buckets.items():
        if not b["indices"]:
            continue
        pos = b["positions"]
        nrm = b["normals"]
        out_pos = [0.0] * len(pos)
        out_nrm = [0.0] * len(nrm)
        for i in range(0, len(pos), 3):
            tx = round(pos[i] - cx, 3)
            ty = round(pos[i + 2] - cz, 3)
            tz = round(-(pos[i + 1] - cy), 3)
            out_pos[i] = tx
            out_pos[i + 1] = ty
            out_pos[i + 2] = tz
            if mat == "fr4":
                if tx < fr4_min_x:
                    fr4_min_x = tx
                if tx > fr4_max_x:
                    fr4_max_x = tx
                if tz < fr4_min_z:
                    fr4_min_z = tz
                if tz > fr4_max_z:
                    fr4_max_z = tz
                if ty > fr4_max_y:
                    fr4_max_y = ty

        for i in range(0, len(nrm), 3):
            out_nrm[i] = round(nrm[i], 3)
            out_nrm[i + 1] = round(nrm[i + 2], 3)
            out_nrm[i + 2] = round(-nrm[i + 1], 3)

        name = f"Mat_{mat}_{rgb[0]}_{rgb[1]}_{rgb[2]}"
        meshes_out.append({
            "name": name,
            "material": mat,
            "color": list(rgb),
            "positions": out_pos,
            "normals": out_nrm,
            "indices": b["indices"],
        })
        print(f"  {name:34s}: {len(out_pos)//3:7d} verts, {len(b['indices'])//3:7d} tris")

    bounds_out = {
        "x": round(span_x, 2),
        "y": round(span_z, 2),
        "z": round(span_y, 2),
    }
    board_out = None
    if fr4_max_x > fr4_min_x:
        board_out = {
            "top_z": round(fr4_max_y, 3),
            "min_x": round(fr4_min_x, 3),
            "max_x": round(fr4_max_x, 3),
            "min_y": round(-fr4_max_z, 3),
            "max_y": round(-fr4_min_z, 3),
            "width": round(fr4_max_x - fr4_min_x, 3),
            "height": round(fr4_max_z - fr4_min_z, 3),
        }

    payload = {
        "solidCount": len(meshes_out),
        "bounds": bounds_out,
        "board": board_out,
        "meshes": meshes_out,
    }

    out_mesh_gz.parent.mkdir(parents=True, exist_ok=True)
    raw_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    with gzip.open(out_mesh_gz, "wb", compresslevel=9) as f:
        f.write(raw_json)
    gz_mb = out_mesh_gz.stat().st_size / (1024 * 1024)
    print(f"Wrote mesh JSON.GZ: {out_mesh_gz} ({len(raw_json)/1e6:.2f} MB raw -> {gz_mb:.2f} MB gz)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a 3D PCB STEP file (and optional Eagle/Fusion .brd) into Three.js WebGL assets."
    )
    parser.add_argument("--step", required=True, type=Path, help="Input 3D PCB .step file")
    parser.add_argument("--out-mesh", required=True, type=Path, help="Output *-mesh.json.gz path")
    parser.add_argument("--out-step-gz", type=Path, help="Optional output *.step.gz download archive path")
    parser.add_argument("--brd", type=Path, help="Optional Eagle/Fusion .brd XML file for 2D silkscreen text decal")
    parser.add_argument("--out-silkscreen", type=Path, help="Optional output *-silkscreen.svg path (requires --brd)")
    parser.add_argument("--lin-deflection", type=float, default=0.08, help="Linear mesh deflection in mm (default: 0.08)")
    parser.add_argument("--ang-deflection", type=float, default=0.35, help="Angular mesh deflection in rad (default: 0.35)")
    args = parser.parse_args()

    convert_step_to_mesh_gz(
        step_path=args.step,
        out_mesh_gz=args.out_mesh,
        lin_deflection=args.lin_deflection,
        ang_deflection=args.ang_deflection,
    )

    if args.out_step_gz:
        args.out_step_gz.parent.mkdir(parents=True, exist_ok=True)
        with args.step.open("rb") as f_in, gzip.open(args.out_step_gz, "wb", compresslevel=9) as f_out:
            shutil.copyfileobj(f_in, f_out)
        step_mb = args.out_step_gz.stat().st_size / (1024 * 1024)
        print(f"Wrote STEP.GZ: {args.out_step_gz} ({step_mb:.2f} MB gz)")

    if args.brd and args.out_silkscreen:
        generate_silkscreen_svg(args.brd, args.out_silkscreen)


if __name__ == "__main__":
    main()
