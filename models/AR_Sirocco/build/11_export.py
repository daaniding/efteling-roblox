"""11_export: Sirocco -> FBX'en voor Roblox (1 unit = 1 m; in Studio ScaleTo(3)), zelfde methode als AR_Pagode/build/11_export.py.
  exports/AR_Sirocco_gebouw.fbx : dak, constructie, vlonder, tonnen niet; decor, hek  (staat stil)
  exports/AR_Sirocco_rit.fbx    : draaischijf, subschijven, tonnen, 12 boten       (draait later)
Oorsprong = dakmidden op waterpeil (park 456,5; 191,2); per materiaal samengevoegd, stukken <= 9500 driehoeken, onderdeelnaam
SI_<rol>_<n>_<deel>, UV's per vlak los (geen gedeelde hoekpunten), ankerblokje op z = -2.
Uit ook exports/export_info.json (driehoeken per deel, lampen).
Gebruik: blender --background --python build/11_export.py -- --master AR_Sirocco_master.blend --uit exports"""
import bpy, bmesh, sys, os, json
from collections import defaultdict
from mathutils import Matrix

a = sys.argv[sys.argv.index("--") + 1:]
master = os.path.abspath(a[a.index("--master") + 1]); uit = os.path.abspath(a[a.index("--uit") + 1])
os.makedirs(uit, exist_ok=True)
LIMIT = 9500
bpy.ops.wm.open_mainfile(filepath=master)
dg = bpy.context.evaluated_depsgraph_get()
RIT_ROLLEN = {"platform", "subschijf", "ton", "voet", "romp", "romp_hout", "schubben", "sierpaneel", "goud", "zeil", "mast", "kist",
              "fruit_oranje", "fles"}
info = {"delen": {}, "lampen": []}


def deel_van(o):
    if o.name.startswith("SI_boot") or o.get("rol") in ("platform", "subschijf", "ton"): return "rit"
    return "gebouw"


def verzamel(deel):
    groepen = defaultdict(list)
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render or "rol" not in o or deel_van(o) != deel: continue
        if o.get("lampen"): info["lampen"] += [list(map(float, l)) for l in o["lampen"]]
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        if not me.polygons: bpy.data.meshes.remove(me); continue
        me.transform(o.matrix_world)
        if not me.uv_layers: me.uv_layers.new(name="UVMap")
        groepen["SI_" + o["rol"]].append((me, [p.index for p in me.polygons]))
    return groepen


def schrijf(groepen, naam, achter):
    exp = bpy.data.collections.new("EXP_" + naam); bpy.context.scene.collection.children.link(exp)
    made = []

    def emit(mn, src, idx):
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
        nm = f"{mn}_{idx}_{achter}"
        me2 = bpy.data.meshes.new(nm); bm.to_mesh(me2); bm.free()
        me2.materials.append(bpy.data.materials.get(mn) or bpy.data.materials.new(mn))
        ob = bpy.data.objects.new(nm, me2); exp.objects.link(ob); made.append((nm, len(me2.polygons)))

    for mn, lijst in groepen.items():
        chunk, ct, idx = [], 0, 0
        for me, polys in lijst:
            cur = []
            for pi in polys:
                t = len(me.polygons[pi].vertices) - 2
                if ct + t > LIMIT and (cur or chunk):
                    if cur: chunk.append((me, cur))
                    emit(mn, chunk, idx); idx += 1; chunk, cur, ct = [], [], 0
                cur.append(pi); ct += t
            if cur: chunk.append((me, cur))
        if chunk: emit(mn, chunk, idx)
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


schrijf(verzamel("gebouw"), "AR_Sirocco_gebouw", "gb")
schrijf(verzamel("rit"), "AR_Sirocco_rit", "rt")
json.dump(info, open(os.path.join(uit, "export_info.json"), "w"), indent=1)
