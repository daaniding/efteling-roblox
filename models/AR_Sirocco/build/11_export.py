"""11_export: Sirocco -> FBX'en voor Roblox (1 unit = 1 m; in Studio ScaleTo(3)), zelfde methode als AR_Pagode/build/11_export.py.
  exports/AR_Sirocco_gebouw.fbx : dak, constructie, vlonder, tonnen niet; decor, hek  (staat stil)
  exports/AR_Sirocco_rit.fbx    : draaischijf, subschijven, tonnen, 12 boten; per draaiend lichaam (rtm, rtsa..c, rtba..l)
  exports/AR_Sirocco_omgeving.fbx : wachtrij, zeilkap, hutje, brug, vijverrand, haven (07_omgeving)
Oorsprong = dakmidden op waterpeil (park 456,5; 191,2); per materiaal samengevoegd, stukken <= 9500 driehoeken, onderdeelnaam
SI_<rol>_<n>_<deel>, UV's per vlak los (geen gedeelde hoekpunten), ankerblokje op z = -2.
Uit ook exports/export_info.json (driehoeken per deel, lampen).
Gebruik: blender --background --python build/11_export.py -- --master AR_Sirocco_master.blend --uit exports"""
import bpy, bmesh, sys, os, json, math
from collections import defaultdict
from mathutils import Matrix

a = sys.argv[sys.argv.index("--") + 1:]
master = os.path.abspath(a[a.index("--master") + 1]); uit = os.path.abspath(a[a.index("--uit") + 1])
os.makedirs(uit, exist_ok=True)
LIMIT = 9500
VOOR = math.radians(-124.0)                # = 03_forms (subschijven op VOOR + 90 + 120 k)
bpy.ops.wm.open_mainfile(filepath=master)
dg = bpy.context.evaluated_depsgraph_get()
RIT_ROLLEN = {"platform", "subschijf", "ton", "voet", "romp", "romp_hout", "romp_blauw", "rood", "binnen", "golf", "schubben", "sierpaneel", "goud", "zeil", "mast", "kist",
              "fruit_oranje", "fles"}
info = {"delen": {}, "lampen": []}


def deel_van(o):
    if o.get("owner") == "phase:07_omgeving": return "omgeving"
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
        if deel != "rit":
            groepen["SI_" + o["rol"]].append((me, [p.index for p in me.polygons])); continue
        # rit: per draaiend lichaam apart (Daan 18 nov: de rit gaat draaien): m = hoofdschijf (schijf, tonnen, 3 losse boten draaien
        # mee als eigen boot), sa..sc = subschijven, ba..bl = boot00..11; onderdeelnaam SI_<rol>_<n>_rt<groep>
        if o.name.startswith("SI_boot"):
            groepen["SI_" + o["rol"] + "|b" + "abcdefghijkl"[int(o.name[7:9])]].append((me, [p.index for p in me.polygons]))
        elif o["rol"] == "subschijf":
            per = defaultdict(list)
            for p in me.polygons:
                c = p.center; h = math.atan2(c.y, c.x)
                s = min(range(3), key=lambda k: abs((h - (VOOR + math.radians(90 + 120 * k)) + math.pi) % (2 * math.pi) - math.pi))
                per[s].append(p.index)
            for k, polys in per.items(): groepen["SI_subschijf|s" + "abc"[k]].append((me, polys))
        else:
            groepen["SI_" + o["rol"] + "|m"].append((me, [p.index for p in me.polygons]))
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
        mat, _, grp = mn.partition("|")
        nm = f"{mat}_{idx}_{achter}{grp}"
        me2 = bpy.data.meshes.new(nm); bm.to_mesh(me2); bm.free()
        me2.materials.append(bpy.data.materials.get(mat) or bpy.data.materials.new(mat))
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
schrijf(verzamel("omgeving"), "AR_Sirocco_omgeving", "om")
json.dump(info, open(os.path.join(uit, "export_info.json"), "w"), indent=1)
