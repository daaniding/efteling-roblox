"""
05_bake Magische Klok (kopie van AR_Sneeuwwitje/build/05_bake.py): verweerde kleurtexturen (+ normal maps), 1024 px.
Rollen: baksteen (oude roodbruine handvorm, front.jpg/Magischeklokklok), stuc (kantelenmuur: grijs-beige, groene aanslag, vuil onderaan),
leien (houten schijfjes/leien grijsbruin met mos), steen. Groepen: baksteen_toren, baksteen_detail, stuc_N, stuc_W, leien, steen.
BAKE_klok / BAKE_ruiter hebben een getekende atlas (03a_atlas.py) en worden niet gebakken.
Gebruik: Blender -b -P 05_bake.py -- --master <master.blend> [--res 1024] [--samples 16]  ->  AR_Sneeuwwitje_baked.blend + textures/*.png
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
master = args[args.index("--master") + 1]
RES = int(args[args.index("--res") + 1]) if "--res" in args else 1024
SAMPLES = int(args[args.index("--samples") + 1]) if "--samples" in args else 16
DEEL = args[args.index("--deel") + 1] if "--deel" in args else "alles"   # kasteel | grot | alles: alleen dat deel bakken (sneller; de rest blijft zichtbaar voor de AO)
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(HERE))
TEX = os.path.join(HERE, "textures"); os.makedirs(TEX, exist_ok=True)
CONCRETE = os.path.join(REPO, "textures", "ambientcg", "Concrete012_Color.png")
RGB = {"baksteen": (150, 98, 76), "steen": (170, 166, 158), "leien": (112, 100, 90), "stuc": (186, 182, 166)}



def lin(c): return tuple((v / 255.0) ** 2.2 for v in c) + (1.0,)


bpy.ops.wm.open_mainfile(filepath=master)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
try: sc.cycles.use_denoising = False
except Exception: pass
for c in bpy.data.collections:
    lc = bpy.context.view_layer.layer_collection.children.get(c.name)
    if lc is not None: lc.exclude = c.name not in ("FORMS",)
forms = bpy.data.collections["FORMS"]
bakecol = bpy.data.collections.new("BAKED"); forms.children.link(bakecol)


def world_bm(o):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=False, depsgraph=dg)
    me.transform(o.matrix_world); bm = bmesh.new(); bm.from_mesh(me); bpy.data.meshes.remove(me); return bm


def build_material(name, role, img):
    m = bpy.data.materials.new("BAKE_" + name); nt = m.node_tree; nt.nodes.clear(); N = nt.nodes; L = nt.links
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); tc = N.new("ShaderNodeTexCoord")
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
    geo = N.new("ShaderNodeNewGeometry"); sp = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Position"], sp.inputs[0])
    sn = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sn.inputs[0])
    def wallvec():
        """2D-coordinaat in het muurvlak: (x of y, z) gemengd op |normaal.x| -> metselverband loopt goed om hoeken en ronde torens"""
        ax = N.new("ShaderNodeMath"); ax.operation = "ABSOLUTE"; L.new(sn.outputs["X"], ax.inputs[0])
        a = N.new("ShaderNodeCombineXYZ"); L.new(sp.outputs["X"], a.inputs[0]); L.new(sp.outputs["Z"], a.inputs[1])
        b = N.new("ShaderNodeCombineXYZ"); L.new(sp.outputs["Y"], b.inputs[0]); L.new(sp.outputs["Z"], b.inputs[1])
        mx = N.new("ShaderNodeMix"); mx.data_type = "VECTOR"; L.new(ax.outputs[0], mx.inputs["Factor"]); L.new(a.outputs[0], mx.inputs[4]); L.new(b.outputs[0], mx.inputs[5])
        return mx.outputs[1]
    bump = None
    if role in ("baksteen", "ruine"):
        br = N.new("ShaderNodeTexBrick"); L.new(wallvec(), br.inputs["Vector"])
        br.inputs["Scale"].default_value = 1.0; br.inputs["Brick Width"].default_value = 0.21; br.inputs["Row Height"].default_value = 0.068
        br.inputs["Mortar Size"].default_value = 0.009; br.inputs["Mortar Smooth"].default_value = 0.3; br.inputs["Bias"].default_value = 0.0; br.offset = 0.5
        if role == "baksteen":
            br.inputs["Color1"].default_value = lin((162, 104, 80)); br.inputs["Color2"].default_value = lin((136, 92, 74)); br.inputs["Mortar"].default_value = lin((176, 166, 150))   # oud roodbruin met grijze voeg (Magischeklokklok)
        else:
            br.inputs["Color1"].default_value = lin((196, 156, 120)); br.inputs["Color2"].default_value = lin((168, 128, 100)); br.inputs["Mortar"].default_value = lin((190, 180, 160))   # ruine: bruin/beige (Boekloc)
        col = br.outputs["Color"]
        vb = N.new("ShaderNodeTexVoronoi"); vb.inputs["Scale"].default_value = 9.0; L.new(wallvec(), vb.inputs["Vector"])      # per steen grijs/roze/geel
        col = mix(col, ramp(vb.outputs["Color"], (0.80, 0.82, 0.84, 1), (1.10, 1.06, 1.00, 1)), 1.0, "MULTIPLY")
        col = mix(col, ramp(noise(0.5, 3), (0.86, 0.86, 0.84, 1), (1.04, 1.04, 1.04, 1)), 1.0, "MULTIPLY")
        zr = N.new("ShaderNodeMapRange"); L.new(sp.outputs["Z"], zr.inputs["Value"]); zr.inputs["From Min"].default_value = 0.9; zr.inputs["From Max"].default_value = 0.0
        mm = N.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; L.new(zr.outputs[0], mm.inputs[0]); L.new(noise(2.0, 5), mm.inputs[1])
        col = mix(col, lin((110, 104, 88)), ramp(mm.outputs[0], (0, 0, 0, 1), (1, 1, 1, 1), 0.15, 0.5))                         # vuil onderaan
        if role == "ruine":
            col = mix(col, lin((96, 100, 70)), ramp(noise(1.6, 6, 0.6), (0, 0, 0, 1), (1, 1, 1, 1), 0.58, 0.7))                 # groen aanslag
        bump = (br.outputs["Fac"], 0.5)
    elif role == "stuc":   # kantelenmuur (Herauten-okt2009): grijs-beige stuc, groene aanslag in vlekken, donker vuil onderaan, scheurtjes
        col = mix(col, ramp(scan(CONCRETE, 0.5), (0.80, 0.80, 0.80, 1), (1.12, 1.12, 1.12, 1)), 1.0, "MULTIPLY")
        col = mix(col, ramp(noise(0.7, 4), (0.84, 0.88, 0.84, 1), (1.06, 1.05, 1.02, 1)), 1.0, "MULTIPLY")
        mr = N.new("ShaderNodeMapRange"); L.new(sn.outputs["Z"], mr.inputs["Value"]); mr.inputs["From Min"].default_value = 0.3; mr.inputs["From Max"].default_value = 0.9
        mm = N.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; L.new(mr.outputs[0], mm.inputs[0]); L.new(noise(1.6, 5, 0.6), mm.inputs[1])
        col = mix(col, lin((96, 110, 70)), ramp(mm.outputs[0], (0, 0, 0, 1), (1, 1, 1, 1), 0.32, 0.55))                          # mos op de kantelen
        col = mix(col, lin((118, 126, 92)), ramp(noise(0.9, 6, 0.65), (0, 0, 0, 1), (1, 1, 1, 1), 0.6, 0.72))                      # groene aanslag in vlekken
        zr = N.new("ShaderNodeMapRange"); L.new(sp.outputs["Z"], zr.inputs["Value"]); zr.inputs["From Min"].default_value = 0.8; zr.inputs["From Max"].default_value = -0.3
        mm2 = N.new("ShaderNodeMath"); mm2.operation = "MULTIPLY"; L.new(zr.outputs[0], mm2.inputs[0]); L.new(noise(2.5, 5), mm2.inputs[1])
        col = mix(col, lin((92, 86, 70)), ramp(mm2.outputs[0], (0, 0, 0, 1), (1, 1, 1, 1), 0.15, 0.55))                           # vuil/vocht onderaan
        bump = (scan(CONCRETE, 0.5), 0.3)
    elif role == "leien":
        vo = N.new("ShaderNodeTexVoronoi"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (7.0, 7.0, 9.0)
        L.new(tc.outputs["Object"], mp.inputs["Vector"]); L.new(mp.outputs[0], vo.inputs["Vector"])
        col = mix(col, ramp(vo.outputs["Color"], (0.78, 0.74, 0.74, 1), (1.18, 1.12, 1.05, 1)), 1.0, "MULTIPLY")
        col = mix(col, lin((78, 88, 56)), ramp(noise(1.4, 6, 0.6), (0, 0, 0, 1), (1, 1, 1, 1), 0.55, 0.68))                       # mos (Magklo)
        bump = (vo.outputs["Distance"], 0.25)
    else:   # steen
        col = mix(col, ramp(scan(CONCRETE, 0.6), (0.80, 0.80, 0.80, 1), (1.12, 1.12, 1.12, 1)), 1.0, "MULTIPLY")
        col = mix(col, ramp(noise(0.5, 3), (0.86, 0.86, 0.82, 1), (1.04, 1.04, 1.04, 1)), 1.0, "MULTIPLY")
        bump = (scan(CONCRETE, 0.6), 0.2)
    ao = N.new("ShaderNodeAmbientOcclusion"); ao.samples = 16; ao.inputs["Distance"].default_value = 0.5 if role in ("stuc", "leien", "baksteen") else 0.25
    col = mix(col, ramp(ao.outputs["AO"], (0.5,) * 3 + (1,), (1, 1, 1, 1)), 1.0, "MULTIPLY")
    L.new(col, em.inputs["Color"]); L.new(em.outputs[0], out.inputs[0])
    bsdf = N.new("ShaderNodeBsdfPrincipled"); bp = N.new("ShaderNodeBump")
    L.new(bump[0], bp.inputs["Height"]); bp.inputs["Strength"].default_value = bump[1]; bp.inputs["Distance"].default_value = 0.02
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
def add(g, role, bm): groups.setdefault(g, (role, []))[1].append(bm)
srcs = []
for o in list(forms.all_objects):
    if o.type != "MESH" or o.hide_render or not o.data.materials or not o.data.materials[0] or o.name.startswith("BAKE_"): continue
    mn = o.data.materials[0].name.replace("MAT_", "")
    if mn not in RGB: continue
    srcs.append(o); bm = world_bm(o); bm.normal_update()
    dead = [f for f in bm.faces if f.normal.z < -0.5 and f.calc_center_median().z < 0.1]
    # leien: onderkant van het overstek BEWAREN (van dichtbij onder de dakrand keek je anders door het dak heen)
    bmesh.ops.delete(bm, geom=list(set(dead)), context="FACES")
    if mn == "baksteen": add("baksteen_toren" if o.name.startswith("MK_toren") else "baksteen_detail", "baksteen", bm)
    elif mn == "stuc": add("stuc_N" if "_muur_N" in o.name else "stuc_W", "stuc", bm)
    else: add(mn, mn, bm)
for o in srcs: o.hide_render = True; o.hide_viewport = True
objs = []
for gname, (role, parts) in groups.items():
    bm = bmesh.new()
    for p in parts:
        me = bpy.data.meshes.new("_t"); p.to_mesh(me); p.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    if len(bm.faces) == 0: bm.free(); continue
    me = bpy.data.meshes.new("BAKE_" + gname); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("BAKE_" + gname, me); bakecol.objects.link(ob)
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003, scale_to_bounds=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    objs.append((gname, role, ob))
for gname, role, ob in objs:
    img = bpy.data.images.new("TEX_" + gname, RES, RES, alpha=False)
    m = build_material(gname, role, img); ob.data.materials.clear(); ob.data.materials.append(m)
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    switch(m, "EMIT"); bpy.ops.object.bake(type="EMIT", margin=6, use_clear=True)
    img.filepath_raw = os.path.join(TEX, "MK_%s_kleur.png" % gname); img.file_format = "PNG"; img.save()
    if role in ("baksteen", "stuc", "leien"):
        nimg = bpy.data.images.new("NRM_" + gname, RES, RES, alpha=False); nimg.colorspace_settings.name = "Non-Color"
        set_target(m, nimg); switch(m, "NORMAL"); sc.cycles.samples = 4
        bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT", margin=6, use_clear=True); sc.cycles.samples = SAMPLES
        nimg.filepath_raw = os.path.join(TEX, "MK_%s_normaal.png" % gname); nimg.file_format = "PNG"; nimg.save(); set_target(m, img)
    switch(m, "EMIT"); print("BAKED", gname, len(ob.data.polygons), flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "AR_MagischeKlok_baked.blend"))
print("KLAAR", [g for g, _, _ in objs])
