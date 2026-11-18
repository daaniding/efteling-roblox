"""11_export: Fata Morgana-delen -> FBX voor Roblox (1 unit = 1 m; in Studio ScaleTo(3)), methode van AR_Sirocco/AR_Archipel.
Per deel ("toren", ...) een FBX exports/AR_FataMorgana_<deel>.fbx met onderdelen FM_<rol>_<n>_<deel>, ankerblokje op z = -2.
Gebruik: blender --background --python build/11_export.py -- --deel toren"""
import bpy, bmesh, sys, os

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = sys.argv[sys.argv.index("--") + 1:]
deel = a[a.index("--deel") + 1]
uit = os.path.join(D, "exports"); os.makedirs(uit, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(D, "AR_FataMorgana_master.blend"))
exp = bpy.data.collections.new("EXP_" + deel); bpy.context.scene.collection.children.link(exp)
for o in [o for o in bpy.data.objects if o.get("deel") == deel and o.type == "MESH"]:
    me = o.data.copy(); me.transform(o.matrix_world)
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.triangulate(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(f"FM_{o['rol']}_0_{deel}", me); exp.objects.link(ob)
abm = bmesh.new(); bmesh.ops.create_cube(abm, size=0.2); bmesh.ops.translate(abm, vec=(0, 0, -2), verts=abm.verts)
ame = bpy.data.meshes.new("anker"); abm.to_mesh(ame); abm.free(); ame.uv_layers.new(name="UVMap")
exp.objects.link(bpy.data.objects.new("anker_" + deel, ame))
for o in bpy.data.objects: o.select_set(False)
for o in exp.objects: o.select_set(True)
bpy.context.view_layer.objects.active = exp.objects[0]
bpy.ops.export_scene.fbx(filepath=os.path.join(uit, f"AR_FataMorgana_{deel}.fbx"), use_selection=True, global_scale=1.0,
                         apply_scale_options='FBX_SCALE_ALL', apply_unit_scale=True, axis_forward='-Z', axis_up='Y',
                         object_types={'MESH'}, mesh_smooth_type='FACE', path_mode='STRIP', embed_textures=False, add_leaf_bones=False)
print("[11_export]", deel, [(o.name, len(o.data.polygons)) for o in exp.objects])
