"""
09_export_roblox Villa Volta: FORMS -> per materiaal samengevoegd in stukken <= 9000 driehoeken -> FBX (1 unit = 1 m).
Curves/tekst worden mesh. Blokkering en CUT_ objecten gaan niet mee. In Studio: ScaleTo(3).
"""
import bpy, bmesh, sys, os
from collections import defaultdict

args = sys.argv[sys.argv.index("--") + 1:]
master = args[args.index("--master") + 1]; out = args[args.index("--out") + 1]
LIMIT = 9000
bpy.ops.wm.open_mainfile(filepath=master)
dg = bpy.context.evaluated_depsgraph_get()
low = bpy.data.collections["FORMS"]
groups = defaultdict(list)
for o in low.all_objects:
    if o.name.startswith(("CUT_", "BLK_", "P_")) or o.get("owner") == "phase:02_blockout" or o.hide_render: continue
    if o.type not in ("MESH", "CURVE", "FONT"): continue
    ev = o.evaluated_get(dg)
    try:
        me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=False, depsgraph=dg)
    except RuntimeError:
        continue
    if len(me.polygons) == 0:
        bpy.data.meshes.remove(me); continue
    me.transform(o.matrix_world)
    mname = (o.data.materials[0].name if o.data.materials and o.data.materials[0] else "MAT_plaster")
    groups[(o.get("anim") or "static") + "__" + mname].append(me)
exp = bpy.data.collections.new("EXPORT"); bpy.context.scene.collection.children.link(exp)
made = []
for mname, meshes in groups.items():
    bm = bmesh.new(); tris = 0; idx = 0
    def flush():
        global bm, tris, idx
        if len(bm.verts) == 0: return
        bmesh.ops.triangulate(bm, faces=bm.faces)
        me = bpy.data.meshes.new(f"{mname}_{idx}"); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(f"{mname}_{idx}", me); exp.objects.link(ob); me.materials.append(bpy.data.materials[mname.split("__",1)[1]])
        made.append((ob.name, len(me.polygons))); bm = bmesh.new(); tris = 0; idx += 1
    for me in meshes:
        t = sum(len(p.vertices) - 2 for p in me.polygons)
        if t > LIMIT:   # te groot: decimeer dit deel apart
            tmpo = bpy.data.objects.new("_dec", me); bpy.context.scene.collection.objects.link(tmpo)
            d = tmpo.modifiers.new("Dec", "DECIMATE"); d.ratio = (LIMIT - 200) / t; d.use_collapse_triangulate = True
            me2 = bpy.data.meshes.new_from_object(tmpo.evaluated_get(bpy.context.evaluated_depsgraph_get()))
            bpy.data.objects.remove(tmpo, do_unlink=True); bpy.data.meshes.remove(me); me = me2
            t = sum(len(p.vertices) - 2 for p in me.polygons)
        if tris + t > LIMIT and tris > 0: flush()
        bm.from_mesh(me); tris += t; bpy.data.meshes.remove(me)
    flush()
for o in list(bpy.data.objects):
    o.select_set(o.name in [m[0] for m in made])
bpy.context.view_layer.objects.active = bpy.data.objects[made[0][0]]
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, global_scale=1.0, apply_scale_options='FBX_SCALE_ALL', apply_unit_scale=True,
                         axis_forward='-Z', axis_up='Y', object_types={'MESH'}, mesh_smooth_type='FACE', use_mesh_modifiers=True,
                         path_mode='COPY', embed_textures=False, add_leaf_bones=False)
print("EXPORT meshes", len(made), "tris", sum(m[1] for m in made), "max", max(m[1] for m in made), "bytes", os.path.getsize(out))
