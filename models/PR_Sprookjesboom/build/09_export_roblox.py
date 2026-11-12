"""
09_export_roblox Sprookjesboom: LOW -> per materiaal samengevoegd in stukken <= LIMIT driehoeken -> FBX (1 unit = 1 m).
UV's blijven zoals ze zijn (gebakken stam, bladkaarten, schors-UV op takken). Blokkering (BLK_) en verborgen objecten
gaan niet mee. Anker-blokje op z = -2 geeft in Studio de modeloorsprong terug (Blender (x,y,z) -> Roblox (-x,z,y)*3
na ScaleTo(3)... zie roblox/plaats_sprookjesboom.luau). In Studio: ScaleTo(3).
Gebruik: Blender -b -P 09_export_roblox.py -- --master <baked.blend> --out <fbx>
"""
import bpy, bmesh, sys, os
from collections import defaultdict

args = sys.argv[sys.argv.index("--") + 1:]
master = args[args.index("--master") + 1]; out = args[args.index("--out") + 1]
LIMIT = 9500
bpy.ops.wm.open_mainfile(filepath=master)
dg = bpy.context.evaluated_depsgraph_get()
groups = defaultdict(list)
for o in bpy.data.collections["LOW"].all_objects:
    if o.name.startswith(("BLK_", "CUT_", "P_")) or o.hide_render or o.type != "MESH": continue
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    if len(me.polygons) == 0:
        bpy.data.meshes.remove(me); continue
    me.transform(o.matrix_world)
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    mname = me.materials[0].name if me.materials and me.materials[0] else "MAT_default"
    groups[mname].append(me)
am = bpy.data.materials.get("MAT_anker") or bpy.data.materials.new("MAT_anker")
abm = bmesh.new(); bmesh.ops.create_cube(abm, size=0.2); bmesh.ops.translate(abm, vec=(0, 0, -2), verts=abm.verts)
ame = bpy.data.meshes.new("anker"); abm.to_mesh(ame); abm.free(); ame.materials.append(am); ame.uv_layers.new(name="UVMap")
groups["MAT_anker"].append(ame)
exp = bpy.data.collections.new("EXPORT_FBX"); bpy.context.scene.collection.children.link(exp)
made = []


def emit(mname, faces_src, idx):
    """faces_src: lijst (mesh, [polygon-indexen]) -> één object met behoud van UV."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    for me, polys in faces_src:
        uv = me.uv_layers.active.data
        vmap = {}
        for pi in polys:
            p = me.polygons[pi]
            vs = []
            for vi in p.vertices:
                if vi not in vmap: vmap[vi] = bm.verts.new(me.vertices[vi].co)
                vs.append(vmap[vi])
            try:
                f = bm.faces.new(vs)
            except ValueError:
                continue
            f.smooth = p.use_smooth
            for lp, li in zip(f.loops, p.loop_indices):
                lp[uvl].uv = uv[li].uv
    bmesh.ops.triangulate(bm, faces=bm.faces)
    name = f"{mname.replace('MAT_', '')}_{idx}"
    me2 = bpy.data.meshes.new(name); bm.to_mesh(me2); bm.free()
    me2.materials.append(bpy.data.materials[mname])
    ob = bpy.data.objects.new(name, me2); exp.objects.link(ob)
    made.append((name, len(me2.polygons)))


for mname, meshes in groups.items():
    chunk, ct, idx = [], 0, 0
    for me in meshes:
        cur = []
        for p in me.polygons:
            t = len(p.vertices) - 2
            if ct + t > LIMIT and (cur or chunk):
                if cur: chunk.append((me, cur))
                emit(mname, chunk, idx); idx += 1; chunk, cur, ct = [], [], 0
            cur.append(p.index); ct += t
        if cur: chunk.append((me, cur))
    if chunk: emit(mname, chunk, idx)
for o in bpy.data.objects:
    o.select_set(o.users_collection and o.users_collection[0] == exp)
bpy.context.view_layer.objects.active = exp.objects[0]
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, global_scale=1.0, apply_scale_options='FBX_SCALE_ALL', apply_unit_scale=True,
                         axis_forward='-Z', axis_up='Y', object_types={'MESH'}, mesh_smooth_type='FACE', use_mesh_modifiers=True,
                         path_mode='STRIP', embed_textures=False, add_leaf_bones=False)
for n, t in made: print("PART", n, t)
print("EXPORT parts", len(made), "tris", sum(t for _, t in made), "max", max(t for _, t in made), "bytes", os.path.getsize(out))
