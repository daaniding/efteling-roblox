"""
05_bake Hans en Grietje: stuc-texturen (kleur + normaal, 1024 px) voor Roblox SurfaceAppearance. Opzet als AR_Sneeuwwitje/build/05_bake.py.
Stuc (Hghuis-vk, Hg-achter): roomwit, licht gevlekt, grijsgroen vuil onderaan en in de hoeken, AO van de snoepjes en pannenkoeken (alleen fijn, 0.3 m).
Groepen: stuc_voor / stuc_noord / stuc_zuid / stuc_achter (huis, per gevelrichting) en stuc_tuin (muren, pijlers, oven in OMGEVING).
Pannenkoeken en snoep hebben al een atlas (03a_atlas.py) en worden niet gebakken.
Gebruik: Blender -b -P 05_bake.py -- --master <master.blend> [--res 1024] [--samples 16]  ->  AR_HansGrietje_baked.blend + textures/HG_stuc_*.png
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
master = args[args.index("--master") + 1]
RES = int(args[args.index("--res") + 1]) if "--res" in args else 1024
SAMPLES = int(args[args.index("--samples") + 1]) if "--samples" in args else 16
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(HERE, "textures"); os.makedirs(TEX, exist_ok=True)
STUC = (238, 232, 216)


def lin(c): return tuple((v / 255.0) ** 2.2 for v in c) + (1.0,)


bpy.ops.wm.open_mainfile(filepath=master)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
try: sc.cycles.use_denoising = False
except Exception: pass
for c in bpy.data.collections:
    lc = bpy.context.view_layer.layer_collection.children.get(c.name)
    if lc is not None: lc.exclude = c.name not in ("FORMS", "OMGEVING")
BAKECOL = {}
for cn in ("FORMS", "OMGEVING"):
    bc = bpy.data.collections.new("BAKED_" + cn); bpy.data.collections[cn].children.link(bc); BAKECOL[cn] = bc


def world_bm(o):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=False, depsgraph=dg)
    me.transform(o.matrix_world); bm = bmesh.new(); bm.from_mesh(me); bpy.data.meshes.remove(me); return bm


def wall_class(f):
    n = f.normal
    if n.y < -0.5: return "voor"
    if n.x < -0.5: return "noord"
    if n.x > 0.5: return "zuid"
    if n.y > 0.5: return "achter"
    c = f.calc_center_median(); return "voor" if c.y < 0.7 else "achter"


def build_material(name, img):
    m = bpy.data.materials.new("BAKE_" + name); nt = m.node_tree; nt.nodes.clear(); N = nt.nodes; L = nt.links
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); tc = N.new("ShaderNodeTexCoord")
    base = N.new("ShaderNodeRGB"); base.outputs[0].default_value = lin(STUC); col = base.outputs[0]
    def mix(a, b, fac, blend="MIX"):
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = blend
        if isinstance(fac, float): mx.inputs["Factor"].default_value = fac
        else: L.new(fac, mx.inputs["Factor"])
        L.new(a, mx.inputs[6])
        if isinstance(b, tuple): mx.inputs[7].default_value = b
        else: L.new(b, mx.inputs[7])
        return mx.outputs[2]
    def ramp(src, c0, c1, p0=0.0, p1=1.0):
        r = N.new("ShaderNodeValToRGB"); r.color_ramp.elements[0].color = c0; r.color_ramp.elements[1].color = c1
        r.color_ramp.elements[0].position = p0; r.color_ramp.elements[1].position = p1; L.new(src, r.inputs[0]); return r.outputs[0]
    def noise(scale, detail=4, rough=0.5):
        n = N.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough; L.new(tc.outputs["Object"], n.inputs["Vector"]); return n.outputs["Fac"]
    geo = N.new("ShaderNodeNewGeometry"); sp = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Position"], sp.inputs[0])
    col = mix(col, ramp(noise(0.6, 3), (0.90, 0.89, 0.86, 1), (1.03, 1.03, 1.02, 1)), 1.0, "MULTIPLY")          # vlekkerig geverfd
    col = mix(col, ramp(noise(4.0, 6, 0.6), (0.93, 0.93, 0.92, 1), (1.02, 1.02, 1.02, 1)), 1.0, "MULTIPLY")       # fijne stucstructuur
    zr = N.new("ShaderNodeMapRange"); L.new(sp.outputs["Z"], zr.inputs["Value"]); zr.inputs["From Min"].default_value = 0.7; zr.inputs["From Max"].default_value = 0.0
    mm = N.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; L.new(zr.outputs[0], mm.inputs[0]); L.new(noise(2.2, 5), mm.inputs[1])
    col = mix(col, lin((150, 146, 120)), ramp(mm.outputs[0], (0, 0, 0, 1), (0.8, 0.8, 0.8, 1), 0.12, 0.5))         # grijsgroen vuil onderaan
    col = mix(col, lin((176, 178, 150)), ramp(noise(1.1, 5, 0.6), (0, 0, 0, 1), (0.45, 0.45, 0.45, 1), 0.6, 0.72))  # lichte groene aanslag
    ao = N.new("ShaderNodeAmbientOcclusion"); ao.samples = 16; ao.inputs["Distance"].default_value = 0.3
    col = mix(col, ramp(ao.outputs["AO"], (0.55, 0.53, 0.5, 1), (1, 1, 1, 1)), 1.0, "MULTIPLY")
    L.new(col, em.inputs["Color"]); L.new(em.outputs[0], out.inputs[0])
    bsdf = N.new("ShaderNodeBsdfPrincipled"); bp = N.new("ShaderNodeBump")
    L.new(noise(5.0, 8, 0.65), bp.inputs["Height"]); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.02
    L.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    tgt = N.new("ShaderNodeTexImage"); tgt.image = img; tgt.name = "TARGET"; N.active = tgt; tgt.select = True
    m["_em"] = em.name; m["_bsdf"] = bsdf.name
    return m


def set_target(m, img): m.node_tree.nodes["TARGET"].image = img; m.node_tree.nodes.active = m.node_tree.nodes["TARGET"]


def switch(m, mode):
    nt = m.node_tree; out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    src = nt.nodes[m["_em"]] if mode == "EMIT" else nt.nodes[m["_bsdf"]]
    for l in list(out.inputs[0].links): nt.links.remove(l)
    nt.links.new(src.outputs[0], out.inputs[0])


groups = {}
srcs = []
for cn in ("FORMS", "OMGEVING"):
    for o in list(bpy.data.collections[cn].all_objects):
        if o.type != "MESH" or o.hide_render or not o.data.materials or not o.data.materials[0] or o.data.materials[0].name != "MAT_stuc": continue
        srcs.append(o); bm = world_bm(o); bm.normal_update()
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z < -0.5 and f.calc_center_median().z < 0.1], context="FACES")   # onderkant op het maaiveld
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().z < -0.04], context="FACES")
        if cn == "FORMS":
            bm.faces.ensure_lookup_table(); buckets = {}
            for f in bm.faces: buckets.setdefault(wall_class(f), []).append(f.index)
            for cls, idx in buckets.items():
                sub = bm.copy(); sub.faces.ensure_lookup_table(); keep = set(idx)
                bmesh.ops.delete(sub, geom=[f for f in sub.faces if f.index not in keep], context="FACES")
                groups.setdefault(("stuc_" + cls, cn), []).append(sub)
            bm.free()
        else:
            groups.setdefault(("stuc_tuin", cn), []).append(bm)
for o in srcs: o.hide_render = True; o.hide_viewport = True
objs = []
for (gname, cn), parts in groups.items():
    bm = bmesh.new()
    for p in parts:
        me = bpy.data.meshes.new("_t"); p.to_mesh(me); p.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    if len(bm.faces) == 0: bm.free(); continue
    me = bpy.data.meshes.new("BAKE_" + gname); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("BAKE_" + gname, me); BAKECOL[cn].objects.link(ob)
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003, scale_to_bounds=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    for p in me.polygons: p.use_smooth = True
    objs.append((gname, ob))
for gname, ob in objs:
    img = bpy.data.images.new("TEX_" + gname, RES, RES, alpha=False)
    m = build_material(gname, img); ob.data.materials.clear(); ob.data.materials.append(m)
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    switch(m, "EMIT"); bpy.ops.object.bake(type="EMIT", margin=6, use_clear=True)
    img.filepath_raw = os.path.join(TEX, "HG_%s_kleur.png" % gname); img.file_format = "PNG"; img.save()
    nimg = bpy.data.images.new("NRM_" + gname, RES, RES, alpha=False); nimg.colorspace_settings.name = "Non-Color"
    set_target(m, nimg); switch(m, "NORMAL"); sc.cycles.samples = 4
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT", margin=6, use_clear=True); sc.cycles.samples = SAMPLES
    nimg.filepath_raw = os.path.join(TEX, "HG_%s_normaal.png" % gname); nimg.file_format = "PNG"; nimg.save(); set_target(m, img)
    switch(m, "EMIT"); print("BAKED", gname, len(ob.data.polygons), flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "AR_HansGrietje_baked.blend"))
print("KLAAR", [g for g, _ in objs])
