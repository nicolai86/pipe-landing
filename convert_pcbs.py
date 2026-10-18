import zipfile, gzip, json, os, sys, math
import xml.etree.ElementTree as ET
import OCP.STEPCAFControl
import OCP.TDocStd
import OCP.XCAFDoc
import OCP.Quantity
import OCP.Bnd
import OCP.BRepBndLib
import OCP.TopExp
import OCP.TopAbs
import OCP.BRepMesh
import OCP.BRep
import OCP.TopoDS
import OCP.TopLoc

def lin_to_srgb(c):
    c = max(0.0, min(1.0, float(c)))
    return round(12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1.0 / 2.4)) - 0.055, 3)

def classify_material(srgb_col):
    r, g, b = srgb_col
    if r > 0.92 and g > 0.92 and b > 0.92:
        return 'silkscreen'
    if g > 0.38 and r < 0.25 and b < 0.25:
        return 'soldermask'
    if r > 0.85 and g > 0.50 and b < 0.25:
        return 'copper'
    if b > 0.45 and r < 0.35:
        return 'led'
    if abs(r - g) < 0.06 and abs(g - b) < 0.06:
        if r > 0.45:
            return 'metal'
        else:
            return 'plastic'
    if 0.40 <= r <= 0.75 and 0.35 <= g <= 0.65 and 0.35 <= b <= 0.65:
        return 'ceramic'
    if 0.35 <= r <= 0.55 and 0.30 <= g <= 0.50 and 0.15 <= b <= 0.35:
        return 'fr4'
    return 'default'

def parse_brd_to_svg(xml_root):
    # Board dimensions from layer 20
    dim_wires = [w for w in xml_root.findall('.//plain/wire') if w.attrib.get('layer') == '20']
    if not dim_wires:
        return None, None
    xs = [float(w.attrib['x1']) for w in dim_wires] + [float(w.attrib['x2']) for w in dim_wires]
    ys = [float(w.attrib['y1']) for w in dim_wires] + [float(w.attrib['y2']) for w in dim_wires]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    w = max_x - min_x
    h = max_y - min_y
    
    scale = 2048.0 / w
    img_w = int(w * scale)
    img_h = int(h * scale)
    
    def tx(x): return (float(x) - min_x) * scale
    def ty(y): return (max_y - float(y)) * scale # SVG y-down
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{img_w}" height="{img_h}" viewBox="0 0 {img_w} {img_h}">',
        '  <rect width="100%" height="100%" fill="none"/>'
    ]
           
    # Plain wires (layer 21)
    for wire in xml_root.findall('.//plain/wire'):
        if wire.attrib.get('layer') in ['21']:
            x1, y1 = tx(wire.attrib['x1']), ty(wire.attrib['y1'])
            x2, y2 = tx(wire.attrib['x2']), ty(wire.attrib['y2'])
            sw = max(1.5, float(wire.attrib.get('width', 0.15)) * scale)
            svg.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#ffffff" stroke-width="{sw:.1f}" stroke-linecap="round"/>')

    # Plain circles (layer 21)
    for c in xml_root.findall('.//plain/circle'):
        if c.attrib.get('layer') in ['21']:
            cx, cy = tx(c.attrib['x']), ty(c.attrib['y'])
            r = float(c.attrib['radius']) * scale
            sw = max(1.5, float(c.attrib.get('width', 0.15)) * scale)
            svg.append(f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="#ffffff" stroke-width="{sw:.1f}"/>')

    # Plain rectangles (layer 21)
    for r in xml_root.findall('.//plain/rectangle'):
        if r.attrib.get('layer') in ['21']:
            x1, x2 = float(r.attrib['x1']), float(r.attrib['x2'])
            y1, y2 = float(r.attrib['y1']), float(r.attrib['y2'])
            sx, sy = tx(min(x1, x2)), ty(max(y1, y2))
            rw, rh = abs(x2 - x1) * scale, abs(y2 - y1) * scale
            svg.append(f'  <rect x="{sx:.1f}" y="{sy:.1f}" width="{rw:.1f}" height="{rh:.1f}" fill="#ffffff"/>')

    # Plain texts (layer 21 & 25)
    for t in xml_root.findall('.//plain/text'):
        if t.attrib.get('layer') in ['21', '25']:
            x, y = tx(t.attrib['x']), ty(t.attrib['y'])
            size = float(t.attrib.get('size', 1.0)) * scale * 0.95
            rot_str = t.attrib.get('rot', 'R0')
            rot = float(rot_str[1:]) if rot_str.startswith('R') else 0
            align = t.attrib.get('align', '')
            anchor = 'middle' if 'center' in align else ('end' if 'right' in align else 'start')
            baseline = 'central' if 'center' in align else 'alphabetic'
            trans = f'transform="rotate({-rot} {x:.1f} {y:.1f})"' if rot != 0 else ''
            txt = t.text or ''
            svg.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-family="monospace, sans-serif" font-weight="bold" font-size="{size:.1f}px" fill="#ffffff" text-anchor="{anchor}" dominant-baseline="{baseline}" {trans}>{txt}</text>')

    # Packages
    packages = {}
    for lib in xml_root.findall('.//libraries/library'):
        lib_name = lib.attrib['name']
        for pkg in lib.findall('.//package'):
            packages[(lib_name, pkg.attrib['name'])] = pkg

    # Placed Elements
    for el in xml_root.findall('.//elements/element'):
        el_name = el.attrib['name']
        lib_name = el.attrib.get('library', '')
        pkg_name = el.attrib.get('package', '')
        ex = float(el.attrib['x'])
        ey = float(el.attrib['y'])
        erot_str = el.attrib.get('rot', 'R0')
        erot = float(erot_str[1:]) if erot_str.startswith('R') else (float(erot_str[2:]) if erot_str.startswith('MR') else 0)
        rad = math.radians(erot)
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        
        def transform_pt(px, py):
            rx = px * cos_r - py * sin_r + ex
            ry = px * sin_r + py * cos_r + ey
            return tx(rx), ty(ry)
            
        pkg = packages.get((lib_name, pkg_name))
        if pkg is not None:
            for wire in pkg.findall('.//wire'):
                if wire.attrib.get('layer') in ['21']:
                    x1, y1 = transform_pt(float(wire.attrib['x1']), float(wire.attrib['y1']))
                    x2, y2 = transform_pt(float(wire.attrib['x2']), float(wire.attrib['y2']))
                    sw = max(1.5, float(wire.attrib.get('width', 0.15)) * scale)
                    svg.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#ffffff" stroke-width="{sw:.1f}" stroke-linecap="round"/>')
            for c in pkg.findall('.//circle'):
                if c.attrib.get('layer') in ['21']:
                    cx, cy = transform_pt(float(c.attrib['x']), float(c.attrib['y']))
                    r = float(c.attrib['radius']) * scale
                    sw = max(1.5, float(c.attrib.get('width', 0.15)) * scale)
                    svg.append(f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="#ffffff" stroke-width="{sw:.1f}"/>')
            for t in pkg.findall('.//text'):
                if t.attrib.get('layer') in ['25', '21']:
                    txt = t.text or ''
                    if txt == '>NAME': txt = el_name
                    elif txt == '>VALUE': continue
                    px = float(t.attrib['x'])
                    py = float(t.attrib['y'])
                    size = float(t.attrib.get('size', 0.8)) * scale * 0.95
                    trot_str = t.attrib.get('rot', 'R0')
                    trot = float(trot_str[1:]) if trot_str.startswith('R') else 0
                    tot_rot = erot + trot
                    x, y = transform_pt(px, py)
                    align = t.attrib.get('align', '')
                    anchor = 'middle' if 'center' in align else ('end' if 'right' in align else 'start')
                    baseline = 'central' if 'center' in align else 'alphabetic'
                    trans = f'transform="rotate({-tot_rot} {x:.1f} {y:.1f})"' if tot_rot != 0 else ''
                    svg.append(f'  <text x="{x:.1f}" y="{y:.1f}" font-family="monospace, sans-serif" font-weight="bold" font-size="{size:.1f}px" fill="#ffffff" text-anchor="{anchor}" dominant-baseline="{baseline}" {trans}>{txt}</text>')

    svg.append('</svg>')
    return '\n'.join(svg), {
        'min_x': min_x, 'max_x': max_x,
        'min_y': min_y, 'max_y': max_y,
        'width': round(w, 2), 'height': round(h, 2)
    }

def export_step_mesh(step_path, out_gz_path, brd_source=None, out_svg_path=None):
    print(f'=== Processing {step_path} -> {out_gz_path} ===')
    doc = OCP.TDocStd.TDocStd_Document(OCP.TCollection.TCollection_ExtendedString('XmlOcaf'))
    reader = OCP.STEPCAFControl.STEPCAFControl_Reader()
    reader.SetColorMode(True)
    reader.SetLayerMode(True)
    reader.SetNameMode(True)
    reader.ReadFile(step_path)
    reader.Transfer(doc)

    color_tool = OCP.XCAFDoc.XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    shape_tool = OCP.XCAFDoc.XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())

    free_labels = OCP.TDF.TDF_LabelSequence()
    shape_tool.GetFreeShapes(free_labels)
    root = shape_tool.GetShape_s(free_labels.Value(1))

    # Center computation
    b_all = OCP.Bnd.Bnd_Box()
    OCP.BRepBndLib.BRepBndLib.Add_s(root, b_all)
    cx = (b_all.CornerMin().X() + b_all.CornerMax().X()) / 2.0
    cy = (b_all.CornerMin().Y() + b_all.CornerMax().Y()) / 2.0
    cz = (b_all.CornerMin().Z() + b_all.CornerMax().Z()) / 2.0
    dx_all = b_all.CornerMax().X() - b_all.CornerMin().X()
    dy_all = b_all.CornerMax().Y() - b_all.CornerMin().Y()
    dz_all = b_all.CornerMax().Z() - b_all.CornerMin().Z()

    # Detect the board substrate solid to determine board top z
    board_top_z = cz
    board_min_x, board_max_x = -dx_all/2, dx_all/2
    board_min_y, board_max_y = -dy_all/2, dy_all/2
    exp_b = OCP.TopExp.TopExp_Explorer(root, OCP.TopAbs.TopAbs_SOLID)
    while exp_b.More():
        sb = exp_b.Current()
        bb = OCP.Bnd.Bnd_Box()
        OCP.BRepBndLib.BRepBndLib.Add_s(sb, bb)
        xmin, ymin, zmin, xmax, ymax, zmax = bb.Get()
        bdx, bdy, bdz = xmax - xmin, ymax - ymin, zmax - zmin
        if bdx > 30 and bdy > 30 and bdz < 2.0:
            board_top_z = zmax
            board_min_x, board_max_x = xmin, xmax
            board_min_y, board_max_y = ymin, ymax
            break
        exp_b.Next()

    # Meshing with fine linear deflection (0.15mm chordal, 0.4 angular)
    mesh_tool = OCP.BRepMesh.BRepMesh_IncrementalMesh(root, 0.15, False, 0.4, True)
    mesh_tool.Perform()

    empty_loc = OCP.TopLoc.TopLoc_Location()
    c_obj = OCP.Quantity.Quantity_Color()

    exp = OCP.TopExp.TopExp_Explorer(root, OCP.TopAbs.TopAbs_SOLID)
    groups = {} # mat_key -> dict of buffers

    while exp.More():
        s = exp.Current()
        s_unloc = s.Located(empty_loc)
        
        solid_col = None
        for ctype in [OCP.XCAFDoc.XCAFDoc_ColorSurf, OCP.XCAFDoc.XCAFDoc_ColorGen, OCP.XCAFDoc.XCAFDoc_ColorCurv]:
            if color_tool.GetColor(s_unloc, ctype, c_obj) or color_tool.GetColor(s, ctype, c_obj):
                solid_col = (
                    lin_to_srgb(c_obj.Red()),
                    lin_to_srgb(c_obj.Green()),
                    lin_to_srgb(c_obj.Blue())
                )
                break

        face_exp = OCP.TopExp.TopExp_Explorer(s, OCP.TopAbs.TopAbs_FACE)
        while face_exp.More():
            f = face_exp.Current()
            face = OCP.TopoDS.TopoDS.Face_s(f)
            f_unloc = face.Located(empty_loc)
            
            face_col = None
            for ctype in [OCP.XCAFDoc.XCAFDoc_ColorSurf, OCP.XCAFDoc.XCAFDoc_ColorGen, OCP.XCAFDoc.XCAFDoc_ColorCurv]:
                if color_tool.GetColor(f_unloc, ctype, c_obj) or color_tool.GetColor(face, ctype, c_obj):
                    face_col = (
                        lin_to_srgb(c_obj.Red()),
                        lin_to_srgb(c_obj.Green()),
                        lin_to_srgb(c_obj.Blue())
                    )
                    break
                    
            eff_col = face_col or solid_col or (0.12, 0.12, 0.14)
            mat_type = classify_material(eff_col)
            mat_key = (eff_col, mat_type)

            loc = OCP.TopLoc.TopLoc_Location()
            tri = OCP.BRep.BRep_Tool.Triangulation_s(face, loc)
            if tri is not None:
                trsf = loc.Transformation()
                is_reversed = (face.Orientation() == OCP.TopAbs.TopAbs_REVERSED)
                if trsf.IsNegative():
                    is_reversed = not is_reversed

                has_normals = tri.HasNormals()
                n_nodes = tri.NbNodes()
                
                if mat_key not in groups:
                    groups[mat_key] = {
                        'positions': [],
                        'normals': [],
                        'indices': [],
                        'vert_offset': 0
                    }
                grp = groups[mat_key]
                v_base = grp['vert_offset']

                for k in range(1, n_nodes + 1):
                    p = tri.Node(k).Transformed(trsf)
                    grp['positions'].append(round(p.X() - cx, 3))
                    grp['positions'].append(round(p.Z() - cz, 3))
                    grp['positions'].append(round(-(p.Y() - cy), 3))

                    if has_normals:
                        nv = tri.Normal(k).Transformed(trsf)
                        sign = -1.0 if is_reversed else 1.0
                        grp['normals'].append(round(sign * nv.X(), 3))
                        grp['normals'].append(round(sign * nv.Z(), 3))
                        grp['normals'].append(round(-sign * nv.Y(), 3))
                    else:
                        grp['normals'].extend([0.0, 1.0, 0.0])

                n_triangles = tri.NbTriangles()
                for k in range(1, n_triangles + 1):
                    t = tri.Triangle(k)
                    i1, i2, i3 = t.Get()
                    if is_reversed:
                        grp['indices'].extend([v_base + i1 - 1, v_base + i3 - 1, v_base + i2 - 1])
                    else:
                        grp['indices'].extend([v_base + i1 - 1, v_base + i2 - 1, v_base + i3 - 1])

                grp['vert_offset'] += n_nodes
            face_exp.Next()
        exp.Next()

    meshes = []
    for (col, mat_type), grp in groups.items():
        if len(grp['positions']) > 0:
            meshes.append({
                'name': f'Mat_{mat_type}_{col[0]}_{col[1]}_{col[2]}',
                'material': mat_type,
                'color': list(col),
                'positions': grp['positions'],
                'normals': grp['normals'],
                'indices': grp['indices']
            })

    # Optional silkscreen parsing from .brd
    brd_info = None
    if brd_source and out_svg_path:
        xml_root = None
        if isinstance(brd_source, tuple):
            zip_path, brd_name = brd_source
            with zipfile.ZipFile(zip_path) as z:
                with z.open(brd_name) as f:
                    xml_root = ET.parse(f).getroot()
        elif os.path.exists(brd_source):
            xml_root = ET.parse(brd_source).getroot()
            
        if xml_root is not None:
            svg_content, b_info = parse_brd_to_svg(xml_root)
            if svg_content and out_svg_path:
                with open(out_svg_path, 'w', encoding='utf-8') as f_svg:
                    f_svg.write(svg_content)
                brd_info = b_info
                print(f'  Silkscreen SVG saved to {out_svg_path} ({len(svg_content)} bytes)')

    out_data = {
        'solidCount': len(meshes),
        'bounds': {'x': round(dx_all, 2), 'y': round(dz_all, 2), 'z': round(dy_all, 2)},
        'board': {
            'top_z': round(board_top_z - cz, 3),
            'min_x': round(board_min_x - cx, 3),
            'max_x': round(board_max_x - cx, 3),
            'min_y': round(board_min_y - cy, 3),
            'max_y': round(board_max_y - cy, 3),
            'width': round(board_max_x - board_min_x, 2),
            'height': round(board_max_y - board_min_y, 2)
        },
        'meshes': meshes
    }
    with gzip.open(out_gz_path, 'wt', encoding='utf-8') as f_out:
        json.dump(out_data, f_out)
    print(f'Done {out_gz_path}: {len(meshes)} material meshes, file size {os.path.getsize(out_gz_path) / 1024:.1f} KB\n')

if __name__ == '__main__':
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(SCRIPT_DIR, 'assets')

    # 1. RS422 Splitter
    export_step_mesh(
        '/tmp/test_rs422.step',
        os.path.join(ASSETS_DIR, 'rs422-splitter-mesh.json.gz'),
        brd_source=(os.path.join(ASSETS_DIR, 'RS422-splitter-v1.zip'), 'RS422-splitter-v1.brd'),
        out_svg_path=os.path.join(ASSETS_DIR, 'rs422-splitter-silkscreen.svg')
    )
    # 2. CSLab IP-M HAT
    export_step_mesh(
        '/tmp/test_cslab.step',
        os.path.join(ASSETS_DIR, 'cslab-ip-m-mesh.json.gz'),
        brd_source=(os.path.join(ASSETS_DIR, 'cslab-ip-m-v3.zip'), 'CS_IP-M-v3.brd'),
        out_svg_path=os.path.join(ASSETS_DIR, 'cslab-ip-m-silkscreen.svg')
    )
    # 3. THC Controller
    export_step_mesh(
        '/tmp/test_thc.step',
        os.path.join(ASSETS_DIR, 'z-axis-thc-mesh.json.gz'),
        brd_source='/Users/nicolai86/Workspace/plasma-z-axis/hardware/v1/z-axis-v1.brd',
        out_svg_path=os.path.join(ASSETS_DIR, 'z-axis-thc-silkscreen.svg')
    )

