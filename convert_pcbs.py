import zipfile, gzip, json, os, sys
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

def export_step_mesh(step_path, out_gz_path):
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

    # Mesh with deflection (0.2mm chordal deflection, linear deflection 0.5)
    mesh_tool = OCP.BRepMesh.BRepMesh_IncrementalMesh(root, 0.2, False, 0.5, True)
    mesh_tool.Perform()

    exp = OCP.TopExp.TopExp_Explorer(root, OCP.TopAbs.TopAbs_SOLID)
    meshes = []
    idx = 0
    c_obj = OCP.Quantity.Quantity_Color()

    while exp.More():
        s = exp.Current()
        b = OCP.Bnd.Bnd_Box()
        OCP.BRepBndLib.BRepBndLib.Add_s(s, b)
        xmin, ymin, zmin, xmax, ymax, zmax = b.Get()
        dx, dy, dz = xmax - xmin, ymax - ymin, zmax - zmin
        fp = dx * dy

        # Check color
        c_val = None
        for ctype in [OCP.XCAFDoc.XCAFDoc_ColorGen, OCP.XCAFDoc.XCAFDoc_ColorSurf, OCP.XCAFDoc.XCAFDoc_ColorCurv]:
            if color_tool.GetColor(s, ctype, c_obj):
                c_val = [round(c_obj.Red(), 3), round(c_obj.Green(), 3), round(c_obj.Blue(), 3)]
                break

        # Fallback layer / component material classification
        # Fusion 360 green is (0.0, 0.216, 0.0)
        if c_val is None:
            if fp > 1200 and dz < 2.0:
                c_val = [0.0, 0.216, 0.0] # Emerald green FR4
            elif dz < 0.25 and fp < 25:
                c_val = [0.78, 0.65, 0.35] # Copper/gold landing pad
            elif dz > 1.0 and dx < 2.2 and dy < 2.2:
                c_val = [0.72, 0.72, 0.75] # Via hole / ring
            elif dz > 0.5:
                c_val = [0.12, 0.12, 0.14] # Matte IC chip
            else:
                c_val = [0.65, 0.65, 0.68]

        # Extract triangulation from faces
        positions = []
        normals = []
        indices = []
        vert_offset = 0

        face_exp = OCP.TopExp.TopExp_Explorer(s, OCP.TopAbs.TopAbs_FACE)
        while face_exp.More():
            f = face_exp.Current()
            face = OCP.TopoDS.TopoDS.Face_s(f)
            loc = OCP.TopLoc.TopLoc_Location()
            tri = OCP.BRep.BRep_Tool.Triangulation_s(face, loc)
            if tri is not None:
                trsf = loc.Transformation()
                has_normals = tri.HasNormals()
                n_nodes = tri.NbNodes()
                
                for k in range(1, n_nodes + 1):
                    p = tri.Node(k).Transformed(trsf)
                    # Convert to Three.js coordinates (CAD X,Y,Z -> Three X, Z_up->Y, -Y->Z)
                    positions.append(round(p.X() - cx, 3))
                    positions.append(round(p.Z() - cz, 3))
                    positions.append(round(-(p.Y() - cy), 3))

                    if has_normals:
                        nv = tri.Normal(k)
                        normals.append(round(nv.X(), 3))
                        normals.append(round(nv.Z(), 3))
                        normals.append(round(-nv.Y(), 3))
                    else:
                        normals.extend([0.0, 1.0, 0.0])

                n_triangles = tri.NbTriangles()
                for k in range(1, n_triangles + 1):
                    t = tri.Triangle(k)
                    i1, i2, i3 = t.Get()
                    indices.append(vert_offset + i1 - 1)
                    indices.append(vert_offset + i2 - 1)
                    indices.append(vert_offset + i3 - 1)

                vert_offset += n_nodes
            face_exp.Next()

        if len(positions) > 0:
            meshes.append({
                'name': f'Part_{idx}',
                'positions': positions,
                'normals': normals,
                'indices': indices,
                'color': c_val
            })
        idx += 1
        exp.Next()

    out_data = {
        'solidCount': len(meshes),
        'bounds': {'x': round(dx_all, 2), 'y': round(dz_all, 2), 'z': round(dy_all, 2)},
        'meshes': meshes
    }
    with gzip.open(out_gz_path, 'wt', encoding='utf-8') as f_out:
        json.dump(out_data, f_out)
    print(f'Done {out_gz_path}: {len(meshes)} meshes, file size {os.path.getsize(out_gz_path) / 1024 / 1024:.2f} MB')

if __name__ == '__main__':
    # 1. RS422 Splitter
    export_step_mesh('/tmp/test_rs422.step', 'assets/rs422-splitter-mesh.json.gz')
    # 2. CSLab IP-M HAT
    export_step_mesh('/tmp/test_cslab.step', 'assets/cslab-ip-m-mesh.json.gz')
    # 3. THC Controller
    export_step_mesh('/tmp/test_thc.step', 'assets/z-axis-thc-mesh.json.gz')
