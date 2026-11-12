"""
09_export_roblox (Langnek, overgenomen van Gijs): LOW -> per anim-groep + materiaal samengevoegd in stukken <= 9000 driehoeken -> FBX (1 unit = 1 m).
Curves/tekst worden mesh. Blokkering en CUT_ objecten gaan niet mee. In Studio: ScaleTo(3).
"""
import bpy, bmesh, sys, os
from collections import defaultdict

args = sys.argv[sys.argv.index("--") + 1:]
master = args[args.index("--master") + 1]; out = args[args.index("--out") + 1]
LIMIT = 9000
CAPS = {"GEO_hoofd": 9000, "GEO_broek": 6000, "GEO_tuniek": 5000, "GEO_rok": 4000, "GEO_rots": 12000, "GEO_oor": 1400,
        "GEO_neus": 1200, "GEO_hekregel": 1500, "GEO_touw_ring": 1200, "GEO_hand": 1800, "GEO_cape": 4000}
def cap_for(name):
    if name.startswith("BAKE_"): return 10 ** 9      # gebakken meshes: al op budget in 04_bake, niet decimeren (UV/textuur)
    return next((v for k, v in CAPS.items() if name.startswith(k)), 3000)


def knip(me, limit):
    """te grote (gebakken) mesh in stukken <= limit driehoeken knippen; UV's blijven."""
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.triangulate(bm, faces=bm.faces); bm.faces.ensure_lookup_table()
    n = len(bm.faces); stukken = []
    for a in range(0, n, limit):
        b2 = bm.copy(); b2.faces.ensure_lookup_table()
        weg = [f for i, f in enumerate(b2.faces) if not (a <= i < a + limit)]
        bmesh.ops.delete(b2, geom=weg, context="FACES")
        m2 = bpy.data.meshes.new(me.name + "_k"); b2.to_mesh(m2); b2.free()
        for mt in me.materials: m2.materials.append(mt)
        stukken.append(m2)
    bm.free(); return stukken
bpy.ops.wm.open_mainfile(filepath=master)
dg = bpy.context.evaluated_depsgraph_get()
low = bpy.data.collections["LOW"]
groups = defaultdict(list)
for o in list(low.all_objects):   # vaste lijst: het decimeren voegt tijdelijk objecten toe
    if o.name.startswith(("CUT_", "BLK_", "P_")) or o.get("owner") == "phase:02_blockout" or o.hide_render: continue
    if o.type not in ("MESH", "CURVE", "FONT"): continue
    dg = bpy.context.evaluated_depsgraph_get()      # opnieuw per object: decimeren hieronder maakt de oude depsgraph ongeldig
    ev = o.evaluated_get(dg)
    try:
        me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=False, depsgraph=dg)
    except RuntimeError:
        continue
    if len(me.polygons) == 0:
        bpy.data.meshes.remove(me); continue
    me.transform(o.matrix_world)
    t0 = sum(len(p.vertices) - 2 for p in me.polygons); cap = cap_for(o.name)
    if t0 > cap:                                   # driehoekenplafond per object (budget asset-brief)
        tmpo = bpy.data.objects.new("_cap", me); bpy.context.scene.collection.objects.link(tmpo)
        d = tmpo.modifiers.new("Dec", "DECIMATE"); d.ratio = cap / t0; d.use_collapse_triangulate = True
        me2 = bpy.data.meshes.new_from_object(tmpo.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(tmpo, do_unlink=True); bpy.data.meshes.remove(me); me = me2
    mname = (o.data.materials[0].name if o.data.materials and o.data.materials[0] else "MAT_rots")
    groups[(o.get("anim") or "static") + "__" + mname].append(me)
# anker op (0,0,-2): geeft in Studio de modeloorsprong terug (zie AR_VillaVolta plaats_template)
am = bpy.data.meshes.new("_anker"); ab = bmesh.new(); bmesh.ops.create_cube(ab, size=0.2); bmesh.ops.translate(ab, vec=(0, 0, -2), verts=ab.verts); ab.to_mesh(am); ab.free()
if "MAT_anker" not in bpy.data.materials: bpy.data.materials.new("MAT_anker")
groups["static__MAT_anker"].append(am)
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
        for p in me.polygons: p.use_smooth = True
        for e in me.edges: e.use_edge_sharp = False          # geen harde randen uit shade_smooth: gaven facetten in Roblox
        if "sharp_edge" in me.attributes: me.attributes.remove(me.attributes["sharp_edge"])
        made.append((ob.name, len(me.polygons))); bm = bmesh.new(); tris = 0; idx += 1
    for me in meshes:
        t = sum(len(p.vertices) - 2 for p in me.polygons)
        if t > LIMIT and me.uv_layers:   # gebakken mesh: knippen i.p.v. decimeren
            for st in knip(me, LIMIT - 200):
                if tris > 0: flush()
                bm.from_mesh(st); tris = sum(len(p.vertices) - 2 for p in st.polygons); bpy.data.meshes.remove(st); flush()
            bpy.data.meshes.remove(me); continue
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
import json
json.dump({"stukken": made}, open(out.replace(".fbx", "_stukken.json"), "w"), indent=1)
print("EXPORT meshes", len(made), "tris", sum(m[1] for m in made), "max", max(m[1] for m in made), "bytes", os.path.getsize(out))
