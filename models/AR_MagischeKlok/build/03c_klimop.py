"""03c_klimop Magische Klok: klimop als dichte massa's bladplakkaten (atlas textures/MK_klimop_kleur.png, 2x2 tegels, alpha).
Foto's (Boekloc, Herauten-okt2009, Magklo): muren voor ~70% begroeid in grote plukken, dichter onderaan, hangt over de kantelen;
stucplekken blijven zichtbaar (vooral boven tussen de kantelen); onderkant toren rondom dicht tot net onder het uurwerk.
Vrij houden: heraut + sokkel (achter de figuur) en het rode schildje. Object BAKE_klimop (eigen UV = geen bake).
Gebruik: Blender -b -P 03c_klimop.py -- --master AR_MagischeKlok_master.blend (na 03_forms)"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, noise
PHASE = "03c_klimop"; OWNER = "phase:" + PHASE
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
args = sys.argv[sys.argv.index("--") + 1:]; master = args[args.index("--master") + 1]
bpy.ops.wm.open_mainfile(filepath=master)
for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o, do_unlink=True)
rnd = random.Random(1984)
SHIFT = 1.2; WALL_H, WALL_T, KANT_W, KANT_GAP, KANT_H = 2.4, 0.5, 0.6, 0.5, 0.5
ARMS = {"N": (Vector((-1.33, -2.96)), Vector((-0.6997, -0.7149)), Vector((0.7149, -0.6997)), 14.45),
        "W": (Vector((0.96, -3.07)), Vector((0.6986, -0.7154)), Vector((-0.7154, -0.6986)), 17.25)}
HERAUT_S_ARM = {"N": (3.8, 8.0, 11.8), "W": (2.8, 5.3, 7.8)}
R_ROMP = 2.08 * 0.87
bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
CNT = [0]


def card(c, n, size, tilt=0.0, spin=None, hang=False):
    """vierkant bladplakkaat rond c, vlak loodrecht op n (n wijst van de muur af), random gedraaid en schuin naar voren gekanteld"""
    n = n.normalized(); up = Vector((0, 0, 1))
    t1 = up.cross(n); t1 = t1.normalized() if t1.length > 1e-4 else Vector((1, 0, 0)); t2 = n.cross(t1)
    a = rnd.uniform(0, math.tau) if spin is None else spin
    u = t1 * math.cos(a) + t2 * math.sin(a); v = n.cross(u)
    if tilt: v = (v * math.cos(tilt) + n * math.sin(tilt)).normalized()   # bovenrand naar voren: geeft volume
    h = size / 2
    if hang: v = Vector((0, 0, 1)); u = t1
    pts = [c - u * h - v * h, c + u * h - v * h, c + u * h + v * h, c - u * h + v * h]
    f = bm.faces.new([bm.verts.new(p) for p in pts])
    tx, ty = rnd.randrange(2), rnd.randrange(2)
    for l, (uu, vv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): l[uvl].uv = ((tx + uu) / 2, (ty + vv) / 2)
    CNT[0] += 1


def dens(s, z, seed):
    """0..1 begroeiing: grote plukken (ruis), dichter onderaan, ijler bovenin"""
    g = noise.noise(Vector((s * 0.33, z * 0.45, seed))) * 0.5 + 0.5
    g2 = noise.noise(Vector((s * 1.1, z * 1.3, seed + 7))) * 0.5 + 0.5
    return g * 0.7 + g2 * 0.3 + 0.36 - 0.07 * z


for name, (p0, u, n, L) in ARMS.items():
    p0 = p0 - n * SHIFT; seed = 3.1 if name == "N" else 8.7; HERAUT_S = HERAUT_S_ARM[name]
    P = lambda s, t, z: Vector((p0.x + u.x * s - n.x * t, p0.y + u.y * s - n.y * t, z))   # t > 0 = de muur in
    N3 = Vector((n.x, n.y, 0))
    # muurvlak (pleinkant): raster met jitter, kaart waar de dichtheid boven de drempel ligt
    s = 0.6
    while s < L - 0.1:
        z = -0.1
        while z < WALL_H + 0.05:
            ss = s + rnd.uniform(-0.17, 0.17); zz = z + rnd.uniform(-0.15, 0.15)
            near_h = min(abs(ss - h) for h in HERAUT_S)
            if near_h < 0.5 and zz < 2.55: z += 0.2; continue                 # heraut + sokkel vrij
            if any(h + 0.36 < ss < h + 0.78 and 1.68 < zz < 2.22 for h in HERAUT_S): z += 0.2; continue   # schildje vrij
            d = dens(ss, zz, seed)
            pr = min(1.0, max(0.0, (d - 0.5) / 0.16))                            # zachte rand: kans loopt op van 0.5 tot 0.66
            if rnd.random() < pr * pr * (3 - 2 * pr):
                layers = 1 + int(max(0.0, d - 0.58) * 12)
                for k in range(min(layers, 5)):
                    off = 0.03 + k * 0.08 + rnd.uniform(0, 0.06)
                    pil = 0.12 if near_h < 0.42 else 0.0                          # lisene steekt 0.12 uit
                    card(P(ss + rnd.uniform(-0.1, 0.1), -off - pil, zz + rnd.uniform(-0.08, 0.08)), N3, rnd.uniform(0.32, 0.5), rnd.uniform(0.15, 0.6))
            z += 0.2
        s += 0.2
    # over de bovenrand: op de muurkruin en over de kantelen, hangende gordijnen aan de pleinkant
    s = 0.6
    while s < L - 0.1:
        d = dens(s, WALL_H, seed)
        if d > 0.55:
            ztop = WALL_H + KANT_H if ((s - 0.9) % (KANT_W + KANT_GAP)) < KANT_W else WALL_H
            card(P(s, WALL_T / 2, ztop + 0.04), Vector((0, 0, 1)), rnd.uniform(0.4, 0.6), rnd.uniform(0, 0.4))
            card(P(s, -0.06, ztop - 0.12), N3, rnd.uniform(0.38, 0.55), rnd.uniform(0.3, 0.8))
            if d > 0.7:                                                          # sliert naar beneden
                for k in range(rnd.randint(1, 4)):
                    card(P(s + rnd.uniform(-0.1, 0.1), -0.05 - rnd.uniform(0, 0.06), ztop - 0.35 - k * 0.3), N3, rnd.uniform(0.28, 0.4), rnd.uniform(0.0, 0.3))
        s += 0.25
    # achterkant (buiten): lichter begroeid
    s = 0.6
    while s < L - 0.1:
        z = 0.0
        while z < WALL_H:
            if dens(s, z, seed + 20) > 0.7: card(P(s, WALL_T + 0.05, z), -N3, rnd.uniform(0.35, 0.5), rnd.uniform(0.1, 0.4))
            z += 0.35
        s += 0.35
# toren: rondom dicht tot ~2.0-2.7, klok vrij (zit erboven)
for k in range(220):
    a = rnd.uniform(0, math.tau)
    ztop = 1.9 + 0.7 * (noise.noise(Vector((math.cos(a) * 2, math.sin(a) * 2, 4.2))) * 0.5 + 0.5)
    for j in range(5):
        z = rnd.uniform(-0.1, ztop)
        r = R_ROMP + 0.04 + j * 0.06 + rnd.uniform(0, 0.05)
        c = Vector((r * math.cos(a), r * math.sin(a), z)); card(c, Vector((math.cos(a), math.sin(a), 0)), rnd.uniform(0.34, 0.5), rnd.uniform(0.2, 0.6))
me = bpy.data.meshes.new("BAKE_klimop"); bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new("BAKE_klimop", me); bpy.data.collections["FORMS"].objects.link(ob); ob["owner"] = OWNER
m = bpy.data.materials.get("MAT_klimop") or bpy.data.materials.new("MAT_klimop")
if bpy.app.version < (5, 0, 0): m.use_nodes = True
nt = m.node_tree; bsdf = next(nd for nd in nt.nodes if nd.type == "BSDF_PRINCIPLED")
tex = next((nd for nd in nt.nodes if nd.type == "TEX_IMAGE"), None) or nt.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(os.path.join(ROOT, "textures", "MK_klimop_kleur.png"), check_existing=True)
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"]); nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
ob.data.materials.append(m)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=master)
print("[03c_klimop] kaarten", CNT[0], "tris", CNT[0] * 2)
