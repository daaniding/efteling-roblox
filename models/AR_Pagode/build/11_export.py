"""11_export: Pagode -> twee FBX'en voor Roblox (1 unit = 1 m; in Studio ScaleTo(3)).
  exports/AR_Pagode_gondel.fbx  : collectie LOW (gondel, arm, voet) in het lokale frame; oorsprong = DRAAIAS (verschoven)
  exports/AR_Pagode_station.fbx : collectie STATION, oorsprong = middelpunt bak (park 360.0, 47.5), z = NAP - 10
Per materiaal samengevoegd, stukken <= LIMIT driehoeken, onderdeelnaam = materiaal (PG_<rol>_<n>), UV's behouden.
Bochten (curve-buizen) worden eerst mesh. Ankerblokje op z = -2 (Sprookjesboom-methode) geeft in Studio de oorsprong terug.
Uit ook: exports/export_info.json (driehoeken per deel, draaias, totaal).
Gebruik: blender --background --python build/11_export.py -- --master AR_Pagode_master.blend --uit exports"""
import bpy, bmesh, sys, os, json
from collections import defaultdict
from mathutils import Vector, Matrix

a = sys.argv[sys.argv.index("--") + 1:]
master = os.path.abspath(a[a.index("--master") + 1]); uit = os.path.abspath(a[a.index("--uit") + 1])
os.makedirs(uit, exist_ok=True)
LIMIT = 9500
bpy.ops.wm.open_mainfile(filepath=master)
for cu in bpy.data.curves:          # buizen (vlammen, krullen, ribben, hoorns) grover voor de game: 8-hoekig, 5 stappen per stuk
    cu.resolution_u = 5; cu.bevel_resolution = 1
dg = bpy.context.evaluated_depsgraph_get()
arm = bpy.data.objects["AR_Pagode_arm"]
AS = Vector(arm["draaias"])
info = {"draaias_lokaal": list(AS), "delen": {}}


seen = set()


def verzamel(collectie, verschuif):
    groepen = defaultdict(list)
    for o in bpy.data.collections[collectie].all_objects:
        if not o.name.startswith("AR_Pagode") or o.type not in ("MESH", "CURVE") or o.hide_render or o.name in seen:
            continue
        seen.add(o.name)
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        if len(me.polygons) == 0:
            bpy.data.meshes.remove(me); continue
        me.transform(Matrix.Translation(-verschuif) @ o.matrix_world)
        if not me.uv_layers: me.uv_layers.new(name="UVMap")
        if o.type == "CURVE" and me.uv_layers:     # buizen: effen kleur, UV mag constant
            for l in me.uv_layers[0].data: l.uv = (0.5, 0.5)
        mats = [m.name if m else "PG_rood" for m in me.materials] or ["PG_rood"]
        per = defaultdict(list)
        for p in me.polygons:
            per[mats[min(p.material_index, len(mats) - 1)]].append(p.index)
        for mn, polys in per.items():
            groepen[mn].append((me, polys))
    return groepen


def schrijf(groepen, naam):
    exp = bpy.data.collections.new("EXP_" + naam); bpy.context.scene.collection.children.link(exp)
    made = []

    def emit(mn, src, idx):
        bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
        for me, polys in src:
            uv = me.uv_layers[0].data; vmap = {}
            for pi in polys:
                p = me.polygons[pi]; vs = []
                for vi in p.vertices:
                    # eigen hoekpunten per vlak: Roblox voegt gedeelde hoekpunten samen en neemt dan de UV van het buurvlak
                    # (driehoeken met verschoven textuur op de klinkers); per vlak los = geen naad om samen te voegen
                    if p.use_smooth:             # gladde vormen (blobs) blijven gedeeld voor zachte schaduw
                        if vi not in vmap: vmap[vi] = bm.verts.new(me.vertices[vi].co)
                        vs.append(vmap[vi])
                    else:
                        vs.append(bm.verts.new(me.vertices[vi].co))
                try: f = bm.faces.new(vs)
                except ValueError: continue
                f.smooth = p.use_smooth
                for lp, li in zip(f.loops, p.loop_indices): lp[uvl].uv = uv[li].uv
        bmesh.ops.triangulate(bm, faces=bm.faces)
        achter = {"AR_Pagode_gondel": "", "AR_Pagode_station": "_st", "AR_Pagode_omgeving": "_om"}[naam]
        nm = f"{mn}_{idx}{achter}"                    # unieke namen over alle FBX'en (geen .001 in Roblox)
        me2 = bpy.data.meshes.new(nm); bm.to_mesh(me2); bm.free()
        mat = bpy.data.materials.get(mn) or bpy.data.materials.new(mn); me2.materials.append(mat)
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
    # anker
    abm = bmesh.new(); bmesh.ops.create_cube(abm, size=0.2); bmesh.ops.translate(abm, vec=(0, 0, -2), verts=abm.verts)
    ame = bpy.data.meshes.new("anker"); abm.to_mesh(ame); abm.free(); ame.uv_layers.new(name="UVMap")
    ame.materials.append(bpy.data.materials.get("MAT_anker") or bpy.data.materials.new("MAT_anker"))
    ao = bpy.data.objects.new("anker", ame); exp.objects.link(ao)
    for o in bpy.data.objects: o.select_set(False)
    for o in exp.objects: o.select_set(True)
    bpy.context.view_layer.objects.active = exp.objects[0]
    bpy.ops.export_scene.fbx(filepath=os.path.join(uit, naam + ".fbx"), use_selection=True, global_scale=1.0,
                             apply_scale_options='FBX_SCALE_ALL', apply_unit_scale=True, axis_forward='-Z', axis_up='Y',
                             object_types={'MESH'}, mesh_smooth_type='FACE', path_mode='STRIP', embed_textures=False, add_leaf_bones=False)
    info["delen"][naam] = dict(made)
    print("[11_export]", naam, len(made), "delen,", sum(t for _, t in made), "driehoeken")


schrijf(verzamel("LOW", AS), "AR_Pagode_gondel")
schrijf(verzamel("STATION", Vector((360.0, 47.5, 0.0))), "AR_Pagode_station")
schrijf(verzamel("OMGEVING", Vector((360.0, 47.5, 0.0))), "AR_Pagode_omgeving")
json.dump(info, open(os.path.join(uit, "export_info.json"), "w"), indent=1)
