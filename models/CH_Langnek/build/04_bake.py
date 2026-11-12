"""
04_bake: geschilderde kleurtexturen voor Roblox (SurfaceAppearance.ColorMap).
Per groep (lijf, hoofd, nek, rots, rand) worden de LOW-objecten samengevoegd (zelfde driehoekenplafonds als de export),
UV-uitgevouwen en wordt een EMIT-bake gemaakt van: Studio-kleur (lineair) x AO (plooien/scheuren) x fijne variatie,
plus per rol: stofstructuur (kleding), blos (huid), betonscan + lagen + vuil + mos (rots, ambientCG Concrete012, CC0).
Ogen, iris, mondholte, hek, gesp en water blijven effen (geen bake). Resultaat: CH_Langnek_baked.blend + textures/*.png.
Gebruik: Blender -b -P 04_bake.py -- --master <master.blend> [--res 2048] [--samples 24]
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
master = args[args.index("--master") + 1]
RES = int(args[args.index("--res") + 1]) if "--res" in args else 2048
SAMPLES = int(args[args.index("--samples") + 1]) if "--samples" in args else 24
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(HERE))
TEX = os.path.join(HERE, "textures"); os.makedirs(TEX, exist_ok=True)
CONCRETE = os.path.join(REPO, "textures", "ambientcg", "Concrete012_Color.png")

# Studio-kleuren (sRGB 0-255) = doelkleur na de bake (getemperd, zie roblox/plaats_langnek.luau)
RGB = {"huid": (206, 154, 124), "lip": (172, 112, 94), "tuniek": (190, 154, 82), "broek": (60, 90, 94), "cape": (138, 52, 40),
       "laars": (144, 58, 44), "riem": (84, 50, 26), "touw": (196, 176, 134), "haar": (44, 40, 40), "binnen": (30, 14, 10),
       "rots": (128, 130, 126), "randsteen": (172, 166, 152), "kei": (152, 146, 136)}
FLAT = {"MAT_oogwit", "MAT_iris", "MAT_pupil", "MAT_binnen", "MAT_hek", "MAT_water", "MAT_gesp"}
STOF = {"tuniek", "broek", "cape", "touw"}
CAPS = {"GEO_hoofd": 9000, "GEO_broek": 6000, "GEO_tuniek": 5000, "GEO_rok": 4000, "GEO_rots": 14000, "GEO_oor": 1400,
        "GEO_neus": 1200, "GEO_touw_ring": 1200, "GEO_hand": 1800, "GEO_cape": 4000, "GEO_randstenen": 6000, "GEO_keien": 3000}
GROUPS = [  # naam, filter(o, matnaam), resolutie
    ("lijf", lambda o, m: o.get("anim") == "body", RES),
    ("hoofd", lambda o, m: o.get("anim") == "head", RES),
    ("nek", lambda o, m: o.get("anim") == "neck", 512),
    ("rots", lambda o, m: o.name.startswith("GEO_rots"), RES),
    ("rand", lambda o, m: o.name.startswith(("GEO_randstenen", "GEO_keien")), 1024),
]


def lin(c):
    return tuple((v / 255.0) ** 2.2 for v in c) + (1.0,)


def cap_for(name):
    return next((v for k, v in CAPS.items() if name.startswith(k)), 3000)


bpy.ops.wm.open_mainfile(filepath=master)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
try:
    sc.cycles.use_denoising = False
except Exception:
    pass
low = bpy.data.collections["LOW"]
bakecol = bpy.data.collections.new("BAKED"); low.children.link(bakecol)


def world_mesh(o):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=False, depsgraph=dg)
    me.transform(o.matrix_world)
    t0 = sum(len(p.vertices) - 2 for p in me.polygons); cap = cap_for(o.name)
    if t0 > cap:
        tmp = bpy.data.objects.new("_cap", me); sc.collection.objects.link(tmp)
        d = tmp.modifiers.new("Dec", "DECIMATE"); d.ratio = cap / t0; d.use_collapse_triangulate = True
        me2 = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(tmp, do_unlink=True); bpy.data.meshes.remove(me); me = me2
    return me


def blush_weights(bm, pts):
    """kleurattribuut 'blos' (0..1) op afstand van neus/wangen/oren (huid wordt daar roder, zoals beschilderd)"""
    lay = bm.verts.layers.float_color.new("blos")
    for v in bm.verts:
        w = 0.0
        for c, r, s in pts:
            d = (v.co - c).length / r
            if d < 1: w = max(w, s * (1 - d * d) ** 2)
        v[lay] = (w, w, w, 1.0)


def bake_material(src, name, img, extra):
    """maakt een bake-materiaal: Emission = kleur x AO x variatie (+ extra per rol); actieve image-node = doel."""
    m = bpy.data.materials.new("BAKE_" + name + "_" + src.name)
    nt = m.node_tree; nt.nodes.clear()
    N = nt.nodes; Ln = nt.links
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); Ln.new(em.outputs[0], out.inputs[0])
    key = src.name.replace("MAT_", "")
    base = N.new("ShaderNodeRGB"); base.outputs[0].default_value = lin(RGB.get(key, (128, 128, 128)))
    col = base.outputs[0]
    def mul(a, b, fac=1.0, blend="MULTIPLY"):
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = blend; mx.inputs["Factor"].default_value = fac
        Ln.new(a, mx.inputs[6]);
        if isinstance(b, tuple): mx.inputs[7].default_value = b
        else: Ln.new(b, mx.inputs[7])
        return mx.outputs[2]
    tc = N.new("ShaderNodeTexCoord")
    # fijne variatie in de verf
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 6
    Ln.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = N.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color = (0.86, 0.86, 0.86, 1); ramp.color_ramp.elements[1].color = (1.08, 1.08, 1.08, 1)
    Ln.new(nz.outputs["Fac"], ramp.inputs[0])
    col = mul(col, ramp.outputs[0])
    if extra == "stof":                                     # stofstructuur: fijne ruis in twee richtingen
        w1 = N.new("ShaderNodeTexWave"); w1.inputs["Scale"].default_value = 260; w1.wave_type = "BANDS"; w1.bands_direction = "X"
        w2 = N.new("ShaderNodeTexWave"); w2.inputs["Scale"].default_value = 260; w2.wave_type = "BANDS"; w2.bands_direction = "Z"
        for w in (w1, w2): Ln.new(tc.outputs["Object"], w.inputs["Vector"])
        r1 = N.new("ShaderNodeValToRGB"); r1.color_ramp.elements[0].color = (0.9, 0.9, 0.9, 1)
        mixw = N.new("ShaderNodeMix"); mixw.data_type = "FLOAT"; mixw.inputs[0].default_value = 0.5
        Ln.new(w1.outputs["Fac"], mixw.inputs[2]); Ln.new(w2.outputs["Fac"], mixw.inputs[3]); Ln.new(mixw.outputs[0], r1.inputs[0])
        col = mul(col, r1.outputs[0])
    if extra == "huid":                                     # blos uit het kleurattribuut
        at = N.new("ShaderNodeVertexColor"); at.layer_name = "blos"
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MIX"
        Ln.new(at.outputs["Color"], mx.inputs["Factor"]); Ln.new(col, mx.inputs[6]); mx.inputs[7].default_value = lin((196, 104, 88))
        col = mx.outputs[2]
    if extra in ("rots", "rand"):                           # betonscan (box-projectie), lagen, mos bovenop
        im = N.new("ShaderNodeTexImage"); im.image = bpy.data.images.load(CONCRETE, check_existing=True)
        im.projection = "BOX"; im.projection_blend = 0.25
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.45, 0.45, 0.45)
        Ln.new(tc.outputs["Object"], mp.inputs["Vector"]); Ln.new(mp.outputs[0], im.inputs["Vector"])
        bw = N.new("ShaderNodeRGBToBW"); Ln.new(im.outputs["Color"], bw.inputs[0])
        r2 = N.new("ShaderNodeValToRGB"); r2.color_ramp.elements[0].color = (0.62, 0.62, 0.62, 1); r2.color_ramp.elements[1].color = (1.25, 1.25, 1.25, 1)
        Ln.new(bw.outputs[0], r2.inputs[0]); col = mul(col, r2.outputs[0])
        if extra == "rots":
            wv = N.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "Z"; wv.inputs["Scale"].default_value = 1.4
            wv.inputs["Distortion"].default_value = 6; wv.inputs["Detail"].default_value = 3
            Ln.new(tc.outputs["Object"], wv.inputs["Vector"])
            r3 = N.new("ShaderNodeValToRGB"); r3.color_ramp.elements[0].color = (0.88, 0.90, 0.92, 1); r3.color_ramp.elements[1].color = (1.06, 1.03, 0.98, 1)
            Ln.new(wv.outputs["Fac"], r3.inputs[0]); col = mul(col, r3.outputs[0])
            geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); Ln.new(geo.outputs["Normal"], sep.inputs[0])
            mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.55; mr.inputs["From Max"].default_value = 0.9
            Ln.new(sep.outputs["Z"], mr.inputs["Value"])
            nm = N.new("ShaderNodeTexNoise"); nm.inputs["Scale"].default_value = 1.6; Ln.new(tc.outputs["Object"], nm.inputs["Vector"])
            mm = N.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; Ln.new(mr.outputs[0], mm.inputs[0]); Ln.new(nm.outputs["Fac"], mm.inputs[1])
            mc = N.new("ShaderNodeMapRange"); mc.inputs["From Min"].default_value = 0.25; mc.inputs["From Max"].default_value = 0.55
            Ln.new(mm.outputs[0], mc.inputs["Value"])
            mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MIX"
            Ln.new(mc.outputs[0], mx.inputs["Factor"]); Ln.new(col, mx.inputs[6]); mx.inputs[7].default_value = lin((86, 100, 58))
            col = mx.outputs[2]
    # AO: donker in plooien, scheuren en onder de cape (geschilderd beeld: vuil zakt in de holtes)
    ao = N.new("ShaderNodeAmbientOcclusion"); ao.samples = 16; ao.inputs["Distance"].default_value = 0.35 if extra in ("rots", "rand") else 0.18
    ra = N.new("ShaderNodeValToRGB")
    ra.color_ramp.elements[0].color = (0.30, 0.30, 0.30, 1) if extra in ("rots", "rand") else (0.45, 0.45, 0.45, 1)
    ra.color_ramp.elements[1].color = (1, 1, 1, 1)
    Ln.new(ao.outputs["AO"], ra.inputs[0]); col = mul(col, ra.outputs[0])
    Ln.new(col, em.inputs["Color"])
    tgt = N.new("ShaderNodeTexImage"); tgt.image = img; N.active = tgt; tgt.select = True
    return m


report = []
for gname, filt, res in GROUPS:
    srcs = []
    for o in list(low.all_objects):
        if o.hide_render or o.type not in ("MESH", "CURVE") or o.name.startswith(("BLK_", "CUT_", "P_")):
            continue
        mname = o.data.materials[0].name if o.data.materials and o.data.materials[0] else "MAT_rots"
        if mname in FLAT or not filt(o, mname):
            continue
        srcs.append((o, mname))
    if not srcs:
        continue
    # samenvoegen met materiaal-index per bron
    mats = []
    bm = bmesh.new()
    for o, mname in srcs:
        me = world_mesh(o)
        mi = mats.index(mname) if mname in mats else (mats.append(mname) or len(mats) - 1)
        for p in me.polygons: p.material_index = mi
        bm.from_mesh(me); bpy.data.meshes.remove(me)
        o.hide_render = True; o.hide_viewport = True              # vervangen door de gebakken versie
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    if gname == "hoofd":
        hc = Vector((0, 0, 0)); cnt = 0
        for v in bm.verts: hc += v.co; cnt += 1
        hc /= max(1, cnt)
        nose = min(bm.verts, key=lambda v: v.co.y).co.copy()       # verste punt naar voren = neuspunt
        blush_weights(bm, [(nose, 0.28, 0.75), (nose + Vector((-0.36, 0.25, 0.0)), 0.26, 0.45), (nose + Vector((0.36, 0.25, 0.0)), 0.26, 0.45)])
    me = bpy.data.meshes.new("BAKE_" + gname); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("BAKE_" + gname, me); bakecol.objects.link(ob)
    ob["anim"] = {"lijf": "body", "hoofd": "head", "nek": "neck"}.get(gname, "static")
    for p in me.polygons: p.use_smooth = True
    # UV
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004, scale_to_bounds=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    img = bpy.data.images.new("TEX_" + gname, res, res, alpha=False)
    extra_of = lambda mn: "huid" if mn in ("MAT_huid", "MAT_lip") and gname == "hoofd" else ("stof" if mn.replace("MAT_", "") in STOF else
                ("rots" if gname == "rots" else ("rand" if gname == "rand" else "")))
    for mn in mats:
        me.materials.append(bake_material(bpy.data.materials[mn], gname, img, extra_of(mn)))
    bpy.ops.object.bake(type="EMIT", margin=8, use_clear=True)
    img.filepath_raw = os.path.join(TEX, "Langnek_%s_kleur.png" % gname); img.file_format = "PNG"; img.save()
    # leveringsmateriaal: alleen de textuur (voor export/preview)
    me.materials.clear()
    dm = bpy.data.materials.new("TEX_" + gname); nt = dm.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"); ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = img
    nt.links.new(ti.outputs["Color"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.7
    me.materials.append(dm)
    for p in me.polygons: p.material_index = 0
    report.append((gname, len(srcs), sum(len(p.vertices) - 2 for p in me.polygons), res))
    print("GEBAKKEN", gname, report[-1])

out = master.replace("_master.blend", "_baked.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
print("KLAAR", out, report)
