"""11_export: Archipel -> FBX'en voor Roblox (1 unit = 1 m; in Studio ScaleTo(3)), methode van AR_Sirocco/build/11_export.py
maar zonder spiegeling (plan.py staat in het echte park).
  exports/AR_Archipel_bad.fbx    : betonbodem, EPDM, kade, maaiveldrand, waterplaat
  exports/AR_Archipel_hutten.fbx : 4 paalhutten, ronde hut, loopbruggen
  exports/AR_Archipel_decor.fbx  : wrak, mast, balk, paalvisser, klimpalen, kisten, tonnen, ingangsvlonder
Oorsprong = plan.OORSPRONG op waterpeil; per rol samengevoegd, stukken <= 9500 driehoeken, onderdeelnaam AR_<rol>_<n>_<deel>,
ankerblokje op z = -2. Schrijft ook exports/export_info.json (driehoeken per deel, lampen = middens van lantaarnglas).
Gebruik: blender --background --python build/11_export.py -- --master AR_Archipel_master.blend --uit exports"""
import bpy, bmesh, sys, os, json
from collections import defaultdict

a = sys.argv[sys.argv.index("--") + 1:]
master = os.path.abspath(a[a.index("--master") + 1]); uit = os.path.abspath(a[a.index("--uit") + 1])
os.makedirs(uit, exist_ok=True)
LIMIT = 9500
bpy.ops.wm.open_mainfile(filepath=master)
dg = bpy.context.evaluated_depsgraph_get()
info = {"delen": {}, "lampen": []}
AFK = {"bad": "bd", "hutten": "ht", "decor": "dc"}


def verzamel(deel):
    groepen = defaultdict(list)
    for o in bpy.data.objects:
        if o.type != "MESH" or "rol" not in o or o.get("deel") != deel or o.get("owner") != "phase:03_vormen": continue
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        if not me.polygons: bpy.data.meshes.remove(me); continue
        me.transform(o.matrix_world)
        if o["rol"] == "lantaarnglas":
            # elke lantaarn = 1 cilinder van 8 zijden + 2 doppen = 10 vlakken; midden per lantaarn
            ps = list(me.polygons)
            for k in range(0, len(ps), 10):
                cs = [p.center for p in ps[k:k + 10]]
                info["lampen"].append([sum(c[i] for c in cs) / len(cs) for i in range(3)])
        if not me.uv_layers: me.uv_layers.new(name="UVMap")
        groepen["AR_" + o["rol"]].append((me, [p.index for p in me.polygons]))
    return groepen


def schrijf(groepen, naam, achter):
    exp = bpy.data.collections.new("EXP_" + naam); bpy.context.scene.collection.children.link(exp)
    made = []

    def emit(mat, src, idx):
        bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
        for me, polys in src:
            uv = me.uv_layers[0].data
            for pi in polys:
                p = me.polygons[pi]
                vs = [bm.verts.new(me.vertices[vi].co) for vi in p.vertices]
                try: f = bm.faces.new(vs)
                except ValueError: continue
                for lp, li in zip(f.loops, p.loop_indices): lp[uvl].uv = uv[li].uv
        bmesh.ops.triangulate(bm, faces=bm.faces)
        nm = f"{mat}_{idx}_{achter}"
        me2 = bpy.data.meshes.new(nm); bm.to_mesh(me2); bm.free()
        me2.materials.append(bpy.data.materials.get(mat) or bpy.data.materials.new(mat))
        ob = bpy.data.objects.new(nm, me2); exp.objects.link(ob); made.append((nm, len(me2.polygons)))

    for mat, lijst in groepen.items():
        chunk, ct, idx = [], 0, 0
        for me, polys in lijst:
            cur = []
            for pi in polys:
                t = len(me.polygons[pi].vertices) - 2
                if ct + t > LIMIT and (cur or chunk):
                    if cur: chunk.append((me, cur))
                    emit(mat, chunk, idx); idx += 1; chunk, cur, ct = [], [], 0
                cur.append(pi); ct += t
            if cur: chunk.append((me, cur))
        if chunk: emit(mat, chunk, idx)
    abm = bmesh.new(); bmesh.ops.create_cube(abm, size=0.2); bmesh.ops.translate(abm, vec=(0, 0, -2), verts=abm.verts)
    ame = bpy.data.meshes.new("anker"); abm.to_mesh(ame); abm.free(); ame.uv_layers.new(name="UVMap")
    ame.materials.append(bpy.data.materials.get("MAT_anker") or bpy.data.materials.new("MAT_anker"))
    ao = bpy.data.objects.new("anker_" + achter, ame); exp.objects.link(ao)
    for o in bpy.data.objects: o.select_set(False)
    for o in exp.objects: o.select_set(True)
    bpy.context.view_layer.objects.active = exp.objects[0]
    bpy.ops.export_scene.fbx(filepath=os.path.join(uit, naam + ".fbx"), use_selection=True, global_scale=1.0,
                             apply_scale_options='FBX_SCALE_ALL', apply_unit_scale=True, axis_forward='-Z', axis_up='Y',
                             object_types={'MESH'}, mesh_smooth_type='FACE', path_mode='STRIP', embed_textures=False, add_leaf_bones=False)
    info["delen"][naam] = dict(made)
    print("[11_export]", naam, len(made), "delen,", sum(t for _, t in made), "driehoeken")


for deel in ("bad", "hutten", "decor"):
    schrijf(verzamel(deel), "AR_Archipel_" + deel, AFK[deel])
json.dump(info, open(os.path.join(uit, "export_info.json"), "w"), indent=1)
