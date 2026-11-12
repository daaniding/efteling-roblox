"""
05_bake Assepoester: verweerde kleurtexturen (+ normal maps) voor Roblox SurfaceAppearance (max 1024 px per textuur).
Bronnen voor de look: front.jpg, Boekloc_nieuw, tuin_nieuw (stuc met vlekken, scheurtjes, groenig vuil onderaan,
plekken waar het pleister is afgevallen en baksteen zichtbaar is, bemoste oude pannen, verweerde blauwgroene verf).
Groepen (elk 1 textuur): stuc_voor/noord/zuid/achter/binnen (muren per gevelrichting; binnen = vlakken in hal/gang/keuken),
pannen_hoofd (hoofddak + toren), pannen_laag (vleugel, gaanderij, portiek), groen, omlijsting, plint.
Methode (Langnek 04_bake): bronnen samenvoegen, smart UV, EMIT-bake van kleur x lagen x AO; bronnen verbergen zodat de
AO tegen de rest van het huis (origineel of al gebakken) rekent. Normal map: Cycles NORMAL-bake van een bump-shader.
Gebruik: Blender -b -P 05_bake.py -- --master <master.blend> [--res 1024] [--samples 24]  ->  AR_Assepoester_baked.blend + textures/*.png
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
master = args[args.index("--master") + 1]
RES = int(args[args.index("--res") + 1]) if "--res" in args else 1024
SAMPLES = int(args[args.index("--samples") + 1]) if "--samples" in args else 24
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(HERE))
TEX = os.path.join(HERE, "textures"); os.makedirs(TEX, exist_ok=True)
PLASTER = os.path.join(REPO, "textures", "ambientcg", "Plaster002_Color.png")
CONCRETE = os.path.join(REPO, "textures", "ambientcg", "Concrete012_Color.png")

RGB = {"stuc": (200, 196, 182), "pannen": (146, 86, 64), "groen": (60, 100, 100), "omlijsting": (212, 208, 194), "plint": (150, 146, 136)}
# binnenruimtes (03_forms HALL/GANG/ROOM, iets ruimer): vlakken met het midden hierin = binnenmuur
INSIDE = [(-6.1, -2.25, 1.15, 4.47, -0.1, 2.5), (-2.75, 3.5, 1.75, 4.85, -0.1, 2.3), (-3.55, 4.95, 4.97, 11.42, -0.1, 3.45)]


def lin(c):
    return tuple((v / 255.0) ** 2.2 for v in c) + (1.0,)


bpy.ops.wm.open_mainfile(filepath=master)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
try: sc.cycles.use_denoising = False
except Exception: pass
for c in bpy.data.collections:     # alleen het huis telt mee (blokkering en tuin niet; tuin staat los in Roblox)
    lc = bpy.context.view_layer.layer_collection.children.get(c.name)
    if lc is not None: lc.exclude = c.name not in ("FORMS",)
forms = bpy.data.collections["FORMS"]
bakecol = bpy.data.collections.new("BAKED"); forms.children.link(bakecol)


def world_bm(o):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=False, depsgraph=dg)
    me.transform(o.matrix_world); bm = bmesh.new(); bm.from_mesh(me); bpy.data.meshes.remove(me); return bm


def wall_class(f):
    c = f.calc_center_median(); n = f.normal
    for (x0, x1, y0, y1, z0, z1) in INSIDE:
        if x0 < c.x < x1 and y0 < c.y < y1 and z0 < c.z < z1: return "binnen"
    if n.y < -0.5: return "voor"
    if n.x < -0.5: return "noord"
    if n.x > 0.5: return "zuid"
    if n.y > 0.5: return "achter"
    return "voor" if c.y < 6 else "achter"      # boven/onder (dagkanten van ramen): bij de dichtstbijzijnde gevel


def build_material(name, role, img):
    m = bpy.data.materials.new("BAKE_" + name); nt = m.node_tree; nt.nodes.clear(); N = nt.nodes; L = nt.links
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    tc = N.new("ShaderNodeTexCoord")
    base = N.new("ShaderNodeRGB"); base.outputs[0].default_value = lin(RGB[role]); col = base.outputs[0]
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
    def noise(scale, detail=4, rough=0.5, vec=None):
        n = N.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough; L.new(vec or tc.outputs["Object"], n.inputs["Vector"]); return n.outputs["Fac"]
    def scan(path, scale):
        im = N.new("ShaderNodeTexImage"); im.image = bpy.data.images.load(path, check_existing=True); im.projection = "BOX"; im.projection_blend = 0.3
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
        L.new(tc.outputs["Object"], mp.inputs["Vector"]); L.new(mp.outputs[0], im.inputs["Vector"])
        bw = N.new("ShaderNodeRGBToBW"); L.new(im.outputs["Color"], bw.inputs[0]); return bw.outputs[0]
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Position"], sep.inputs[0])
    nsep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], nsep.inputs[0])
    bumpsrc = None
    if role == "stuc":
        col = mix(col, ramp(scan(PLASTER, 0.7), (0.80, 0.80, 0.80, 1), (1.12, 1.12, 1.12, 1)), 1.0, "MULTIPLY")            # pleisterscan
        col = mix(col, ramp(noise(0.35, 3), (0.86, 0.86, 0.80, 1), (1.05, 1.05, 1.06, 1), 0.3, 0.75), 1.0, "MULTIPLY")      # grote vlekken
        # vuil onderaan: groenig grijs, tot ~0.9 m, rafelig
        zr = N.new("ShaderNodeMapRange"); L.new(sep.outputs["Z"], zr.inputs["Value"]); zr.inputs["From Min"].default_value = 0.95; zr.inputs["From Max"].default_value = 0.05
        nz = noise(2.2, 5); mm = N.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; L.new(zr.outputs[0], mm.inputs[0]); L.new(nz, mm.inputs[1])
        mr = N.new("ShaderNodeMapRange"); L.new(mm.outputs[0], mr.inputs["Value"]); mr.inputs["From Min"].default_value = 0.12; mr.inputs["From Max"].default_value = 0.45
        col = mix(col, lin((118, 116, 98)), mr.outputs[0])
        # regenstrepen: verticale banden, alleen in vlekken
        wv = N.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "X"; wv.inputs["Scale"].default_value = 9.0
        wv.inputs["Distortion"].default_value = 3.0; wv.inputs["Detail"].default_value = 4; L.new(tc.outputs["Object"], wv.inputs["Vector"])
        st = N.new("ShaderNodeMath"); st.operation = "MULTIPLY"; L.new(ramp(wv.outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.55, 0.95), st.inputs[0]); L.new(noise(0.9, 3), st.inputs[1])
        col = mix(col, lin((150, 146, 132)), st.outputs[0])
        # afgevallen pleister met baksteen eronder (onderste 1.3 m, kleine plekken)
        br = N.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 4.5; br.inputs["Mortar Size"].default_value = 0.012
        br.inputs["Color1"].default_value = lin((150, 74, 54)); br.inputs["Color2"].default_value = lin((122, 62, 46)); br.inputs["Mortar"].default_value = lin((170, 160, 140))
        L.new(tc.outputs["Object"], br.inputs["Vector"])
        hz = N.new("ShaderNodeMapRange"); L.new(sep.outputs["Z"], hz.inputs["Value"]); hz.inputs["From Min"].default_value = 1.5; hz.inputs["From Max"].default_value = 0.3
        pm = N.new("ShaderNodeMath"); pm.operation = "MULTIPLY"; L.new(noise(1.3, 6, 0.6), pm.inputs[0]); L.new(hz.outputs[0], pm.inputs[1])
        patch = ramp(pm.outputs[0], (0, 0, 0, 1), (1, 1, 1, 1), 0.52, 0.56)
        col = mix(col, br.outputs["Color"], patch)
        # haarscheurtjes: rand van voronoicellen, alleen waar een vlekkenmasker ze toelaat
        vo = N.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"; vo.inputs["Scale"].default_value = 1.6
        dn = N.new("ShaderNodeTexNoise"); dn.inputs["Scale"].default_value = 3.0; L.new(tc.outputs["Object"], dn.inputs["Vector"])
        dv = N.new("ShaderNodeVectorMath"); dv.operation = "ADD"; L.new(tc.outputs["Object"], dv.inputs[0]); L.new(dn.outputs["Color"], dv.inputs[1])
        L.new(dv.outputs[0], vo.inputs["Vector"])
        crack = ramp(vo.outputs["Distance"], (1, 1, 1, 1), (0, 0, 0, 1), 0.0, 0.012)
        cm = N.new("ShaderNodeMath"); cm.operation = "MULTIPLY"; L.new(crack, cm.inputs[0]); L.new(ramp(noise(0.8, 2), (0, 0, 0, 1), (1, 1, 1, 1), 0.5, 0.62), cm.inputs[1])
        col = mix(col, lin((96, 92, 82)), cm.outputs[0])
        bs = N.new("ShaderNodeMath"); bs.operation = "SUBTRACT"; L.new(scan(PLASTER, 0.7), bs.inputs[0]); L.new(cm.outputs[0], bs.inputs[1])
        bumpsrc = (bs.outputs[0], 0.35)
    elif role == "pannen":
        vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 1.0
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (4.5, 4.5, 6.0); L.new(tc.outputs["Object"], mp.inputs["Vector"]); L.new(mp.outputs[0], vo.inputs["Vector"])
        col = mix(col, ramp(vo.outputs["Color"], (0.78, 0.74, 0.74, 1), (1.18, 1.12, 1.05, 1)), 1.0, "MULTIPLY")      # kleur per pan
        col = mix(col, ramp(noise(0.6, 3), (0.80, 0.80, 0.82, 1), (1.06, 1.03, 1.0, 1), 0.3, 0.7), 1.0, "MULTIPLY")    # verkleuring
        moss = ramp(noise(1.4, 6, 0.6), (0, 0, 0, 1), (1, 1, 1, 1), 0.56, 0.68)
        col = mix(col, lin((84, 92, 52)), moss)                                                                         # mos
        lich = ramp(noise(14.0, 2), (0, 0, 0, 1), (1, 1, 1, 1), 0.72, 0.76)
        col = mix(col, lin((170, 168, 140)), lich)                                                                      # korstmos-stipjes
        bumpsrc = (vo.outputs["Distance"], 0.25)
    elif role == "groen":
        wv = N.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "X"; wv.inputs["Scale"].default_value = 18
        wv.inputs["Distortion"].default_value = 8; wv.inputs["Detail"].default_value = 3; L.new(tc.outputs["Object"], wv.inputs["Vector"])
        col = mix(col, ramp(wv.outputs["Fac"], (0.82, 0.84, 0.84, 1), (1.06, 1.05, 1.04, 1)), 1.0, "MULTIPLY")       # nerf
        worn = ramp(noise(2.6, 6, 0.65), (0, 0, 0, 1), (1, 1, 1, 1), 0.58, 0.66)
        col = mix(col, lin((126, 122, 104)), worn)                                                                      # afgesleten verf
        col = mix(col, ramp(noise(0.5, 2), (0.82, 0.84, 0.86, 1), (1.04, 1.04, 1.04, 1)), 1.0, "MULTIPLY")
        bumpsrc = (wv.outputs["Fac"], 0.15)
    else:   # omlijsting, plint: steen
        col = mix(col, ramp(scan(CONCRETE, 0.6), (0.78, 0.78, 0.78, 1), (1.12, 1.12, 1.12, 1)), 1.0, "MULTIPLY")
        col = mix(col, ramp(noise(0.5, 3), (0.86, 0.86, 0.82, 1), (1.04, 1.04, 1.04, 1)), 1.0, "MULTIPLY")
        bumpsrc = (scan(CONCRETE, 0.6), 0.2)
    ao = N.new("ShaderNodeAmbientOcclusion"); ao.samples = 16; ao.inputs["Distance"].default_value = 0.5 if role in ("stuc", "pannen") else 0.2
    col = mix(col, ramp(ao.outputs["AO"], (0.42, 0.42, 0.42, 1), (1, 1, 1, 1)), 1.0, "MULTIPLY")
    L.new(col, em.inputs["Color"]); L.new(em.outputs[0], out.inputs[0])
    # normal-bake opstelling (wordt pas gekoppeld bij de NORMAL-bake)
    bsdf = N.new("ShaderNodeBsdfPrincipled"); bump = N.new("ShaderNodeBump")
    L.new(bumpsrc[0], bump.inputs["Height"]); bump.inputs["Strength"].default_value = bumpsrc[1]; bump.inputs["Distance"].default_value = 0.02
    L.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    tgt = N.new("ShaderNodeTexImage"); tgt.image = img; tgt.name = "TARGET"; N.active = tgt; tgt.select = True
    m["_em"] = em.name; m["_bsdf"] = bsdf.name
    return m


def set_target(m, img):
    m.node_tree.nodes["TARGET"].image = img; m.node_tree.nodes.active = m.node_tree.nodes["TARGET"]


def switch(m, mode):
    nt = m.node_tree; out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    src = nt.nodes[m["_em"]] if mode == "EMIT" else nt.nodes[m["_bsdf"]]
    for l in list(out.inputs[0].links): nt.links.remove(l)
    nt.links.new(src.outputs[0], out.inputs[0])


# ---------------- groepen verzamelen ----------------
groups = {}     # naam -> (rol, [bm-stukken])
def add(gname, role, bm):
    groups.setdefault(gname, (role, []))[1].append(bm)

srcs = []
for o in list(forms.objects):
    if o.type != "MESH" or not o.data.materials or not o.data.materials[0]: continue
    mn = o.data.materials[0].name.replace("MAT_", "")
    if mn not in RGB: continue
    srcs.append(o)
    bm = world_bm(o)
    # onzichtbare vlakken niet bakken (zwart, verspilde UV-ruimte): onderkanten op het maaiveld, bovenkanten van muren onder de daken,
    # onderkanten van daken (behalve het portiek: dat is het plafond, gaat naar de planken)
    bm.normal_update()
    dead = []; under = []
    for f in bm.faces:
        c = f.calc_center_median(); n = f.normal
        if n.z < -0.5 and c.z < 0.1: dead.append(f)
        elif mn == "stuc" and n.z > 0.5 and any(abs(c.z - t) < 0.05 for t in (2.2, 2.6, 2.67, 4.87, 5.32)): dead.append(f)
        elif mn == "pannen" and n.z < -0.5:
            (under if o.name.startswith("AP_dak_portiek") else dead).append(f)
    if under:
        ub = bm.copy(); ub.faces.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        keep = {f.index for f in under}
        bmesh.ops.delete(ub, geom=[f for f in ub.faces if f.index not in keep], context="FACES")
        add("groen", "groen", ub)
    bmesh.ops.delete(bm, geom=list(set(dead) | set(under)), context="FACES")
    if mn == "stuc" and o.name.startswith("AP_muren"):
        bm.faces.ensure_lookup_table()
        buckets = {}
        for f in bm.faces: buckets.setdefault(wall_class(f), []).append(f.index)
        for cls, idx in buckets.items():
            sub = bm.copy(); sub.faces.ensure_lookup_table(); keep = set(idx)
            bmesh.ops.delete(sub, geom=[f for f in sub.faces if f.index not in keep], context="FACES")
            add("stuc_" + cls, "stuc", sub)
        bm.free()
    elif mn == "stuc":
        add("stuc_voor", "stuc", bm)            # schoorstenen
    elif mn == "pannen":
        add("pannen_hoofd" if o.name.startswith(("AP_dak_hoofd", "AP_dak_toren")) else "pannen_laag", "pannen", bm)
    else:
        add(mn, mn, bm)

for o in srcs: o.hide_render = True; o.hide_viewport = True
# eerst alle gebakken objecten maken (zichtbaar), dan bakken: AO rekent tegen het hele huis
objs = []
for gname, (role, parts) in groups.items():
    bm = bmesh.new()
    for p in parts:
        me = bpy.data.meshes.new("_t"); p.to_mesh(me); p.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new("BAKE_" + gname); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("BAKE_" + gname, me); bakecol.objects.link(ob); ob["rol"] = role
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003, scale_to_bounds=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    objs.append((gname, role, ob))

report = []
for gname, role, ob in objs:
    img = bpy.data.images.new("TEX_" + gname, RES, RES, alpha=False)
    m = build_material(gname, role, img); ob.data.materials.clear(); ob.data.materials.append(m)
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    switch(m, "EMIT"); bpy.ops.object.bake(type="EMIT", margin=6, use_clear=True)
    img.filepath_raw = os.path.join(TEX, "Assepoester_%s_kleur.png" % gname); img.file_format = "PNG"; img.save()
    if role in ("stuc", "pannen"):
        nimg = bpy.data.images.new("NRM_" + gname, RES, RES, alpha=False); nimg.colorspace_settings.name = "Non-Color"
        set_target(m, nimg); switch(m, "NORMAL")
        sc.cycles.samples = 4
        bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT", margin=6, use_clear=True)
        sc.cycles.samples = SAMPLES
        nimg.filepath_raw = os.path.join(TEX, "Assepoester_%s_normaal.png" % gname); nimg.file_format = "PNG"; nimg.save()
        set_target(m, img)
    switch(m, "EMIT")
    report.append((gname, len(ob.data.polygons)))
    print("BAKED", gname, len(ob.data.polygons), flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "AR_Assepoester_baked.blend"))
print("KLAAR", report)
