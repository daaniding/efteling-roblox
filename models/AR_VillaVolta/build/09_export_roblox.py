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
COLN = args[args.index("--col") + 1] if "--col" in args else "FORMS"
low = bpy.data.collections[COLN]
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
    # UV's: kubusprojectie in wereldmeters (1 UV = 2 m), zodat Roblox-materialen op MeshParts goed tegelen
    _b = bmesh.new(); _b.from_mesh(me); _uv = _b.loops.layers.uv.verify()
    for _f in _b.faces:
        _n = _f.normal; _ax = max(range(3), key=lambda i: abs(_n[i]))
        for _l in _f.loops:
            _c = _l.vert.co; _u, _v = [(_c.y, _c.z), (_c.x, _c.z), (_c.x, _c.y)][_ax]
            _l[_uv].uv = (_u / 2.0, _v / 2.0)
    _b.to_mesh(me); _b.free()
    mname = (o.data.materials[0].name if o.data.materials and o.data.materials[0] else "MAT_plaster")
    groups[(o.get("anim") or "static") + "__" + mname].append(me)
am = bpy.data.materials.get("MAT_anker") or bpy.data.materials.new("MAT_anker")
abm = bmesh.new(); bmesh.ops.create_cube(abm, size=0.2); bmesh.ops.translate(abm, vec=(0, 0, -2), verts=abm.verts)
ame = bpy.data.meshes.new("anker"); abm.to_mesh(ame); abm.free(); ame.materials.append(am)
groups["static__MAT_anker"].append(ame)
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
        if t > LIMIT:   # te groot: in stukken knippen (niet decimeren, dan gaat detail verloren)
            src = bmesh.new(); src.from_mesh(me); src.faces.ensure_lookup_table(); uvl = src.loops.layers.uv.active
            chunk = []; ct = 0
            def emit(fs):
                nb = bmesh.new(); vm = {}; nuv = nb.loops.layers.uv.new("UVMap") if uvl else None
                for f in fs:
                    vs = []
                    for v in f.verts:
                        if v not in vm: vm[v] = nb.verts.new(v.co)
                        vs.append(vm[v])
                    try: nf = nb.faces.new(vs)
                    except ValueError: continue
                    nf.smooth = f.smooth; nf.material_index = f.material_index
                    if uvl:
                        for l_new, l_old in zip(nf.loops, f.loops): l_new[nuv].uv = l_old[uvl].uv
                m2 = bpy.data.meshes.new("_chunk"); nb.to_mesh(m2); nb.free(); return m2
            parts = []
            for f in src.faces:
                chunk.append(f); ct += len(f.verts) - 2
                if ct >= LIMIT - 200: parts.append(emit(chunk)); chunk = []; ct = 0
            if chunk: parts.append(emit(chunk))
            src.free(); bpy.data.meshes.remove(me)
            for m2 in parts:
                t2 = sum(len(p.vertices) - 2 for p in m2.polygons)
                if tris + t2 > LIMIT and tris > 0: flush()
                bm.from_mesh(m2); tris += t2; bpy.data.meshes.remove(m2)
            continue
        if tris + t > LIMIT and tris > 0: flush()
        bm.from_mesh(me); tris += t; bpy.data.meshes.remove(me)
    flush()
# botsblokken en lichtpunten als losse onderdelen meesturen (geen lange datalijsten meer plakken in Studio)
if "--extra" in args:
    import json, math
    from mathutils import Matrix
    d = json.load(open(args[args.index("--extra") + 1]))
    em = bpy.data.materials.get("MAT_botsing") or bpy.data.materials.new("MAT_botsing")
    lm = bpy.data.materials.get("MAT_lichtpunt") or bpy.data.materials.new("MAT_lichtpunt")
    for k, c in enumerate(d["colliders"]):
        b = bmesh.new(); bmesh.ops.create_cube(b, size=1.0); bmesh.ops.scale(b, vec=(c[3], c[4], c[5]), verts=b.verts)
        bmesh.ops.transform(b, matrix=Matrix.Translation((c[0], c[1], c[2])) @ Matrix.Rotation(math.radians(c[6]), 4, "Z"), verts=b.verts)
        me = bpy.data.meshes.new(f"COLL_{k}"); b.to_mesh(me); b.free(); me.materials.append(em)
        ob = bpy.data.objects.new(f"COLL_{k}", me); exp.objects.link(ob); made.append((ob.name, 12))
    for k, l in enumerate(d["lamps"]):
        b = bmesh.new(); bmesh.ops.create_cube(b, size=0.06); bmesh.ops.translate(b, vec=(l[0], l[1], l[2]), verts=b.verts)
        me = bpy.data.meshes.new(f"LAMP_{k}"); b.to_mesh(me); b.free(); me.materials.append(lm)
        ob = bpy.data.objects.new(f"LAMP_{k}", me); exp.objects.link(ob); made.append((ob.name, 12))
for o in list(bpy.data.objects):
    o.select_set(o.name in [m[0] for m in made])
bpy.context.view_layer.objects.active = bpy.data.objects[made[0][0]]
bpy.ops.export_scene.fbx(filepath=out, use_selection=True, global_scale=1.0, apply_scale_options='FBX_SCALE_ALL', apply_unit_scale=True,
                         axis_forward='-Z', axis_up='Y', object_types={'MESH'}, mesh_smooth_type='FACE', use_mesh_modifiers=True,
                         path_mode='COPY', embed_textures=False, add_leaf_bones=False)
print("EXPORT meshes", len(made), "tris", sum(m[1] for m in made), "max", max(m[1] for m in made), "bytes", os.path.getsize(out))
