"""03c_klimop Prinsenpoort: klimop als bladplakkaten (atlas textures/PP_klimop_kleur.png = klimop van de Magische Klok, 2x2 tegels, alpha).
Prinsenpoort.jpg (2003): rechtertoren bijna helemaal begroeid (tot onder de dakrand), linkertoren grotendeels, zijkanten van de middenpoort
begroeid; voorkant middenpoort (boog, lantaarn, schildje) en de torenvensters vrij. Object BAKE_klimop (eigen UV = geen bake).
Gebruik: Blender -b -P 03c_klimop.py -- --master AR_Prinsenpoort_master.blend (na 03_forms)"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, noise
OWNER = "phase:03c_klimop"
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
args = sys.argv[sys.argv.index("--") + 1:]; master = args[args.index("--master") + 1]
bpy.ops.wm.open_mainfile(filepath=master)
for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o, do_unlink=True)
rnd = random.Random(2003)
PW, PD, PH = 2.45, 2.2, 3.5; TX, TY, TR_, TH = 3.35, -1.2, 1.0, 4.05
bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap"); CNT = [0]


def card(c, n, size, tilt=0.0):
    n = n.normalized(); up = Vector((0, 0, 1)); t1 = up.cross(n); t1 = t1.normalized() if t1.length > 1e-4 else Vector((1, 0, 0)); t2 = n.cross(t1)
    a = rnd.uniform(0, math.tau); u = t1 * math.cos(a) + t2 * math.sin(a); v = n.cross(u)
    if tilt: v = (v * math.cos(tilt) + n * math.sin(tilt)).normalized()
    h = size / 2; pts = [c - u * h - v * h, c + u * h - v * h, c + u * h + v * h, c - u * h + v * h]
    f = bm.faces.new([bm.verts.new(p) for p in pts]); tx, ty = rnd.randrange(2), rnd.randrange(2)
    for l, (uu, vv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): l[uvl].uv = ((tx + uu) / 2, (ty + vv) / 2)
    CNT[0] += 1


def dens(a, b, seed): return (noise.noise(Vector((a * 0.5, b * 0.5, seed))) * 0.5 + 0.5) * 0.7 + (noise.noise(Vector((a * 1.3, b * 1.3, seed + 5))) * 0.5 + 0.5) * 0.3


# torens: rechts (+X) dicht tot ~3.9, links grotendeels tot ~3.4; venster (schuin voor-buiten op 2.62..3.33) vrij
for sx, top, drempel, seed in ((1, 3.95, 0.30, 1.0), (-1, 3.45, 0.46, 4.0)):
    cx = sx * TX; wa = math.atan2(-0.8, 0.6 * sx)
    for k in range(int(900 if sx > 0 else 650)):
        a = rnd.uniform(0, math.tau); z = rnd.uniform(-0.1, top)
        if abs(math.atan2(math.sin(a - wa), math.cos(a - wa))) < 0.32 and 2.5 < z < 3.45: continue        # venster vrij
        if sx < 0 and abs(math.atan2(math.sin(a - math.radians(225)), math.cos(a - math.radians(225)))) < 0.3 and z > 2.0: continue   # kooi
        nx, ny = math.cos(a), math.sin(a)
        px, py = cx + nx * TR_, TY + ny * TR_
        if abs(px) < PW + 0.05 and abs(py) < PD + 0.05: continue                                         # binnen de middenpoort
        if dens(a * 2, z, seed) < drempel + 0.08 * max(0, z - 2.5): continue
        r = TR_ + 0.03 + rnd.uniform(0, 0.16)
        card(Vector((cx + nx * r, TY + ny * r, z)), Vector((nx, ny, 0)), rnd.uniform(0.32, 0.5), rnd.uniform(0.2, 0.6))
# middenpoort: zijgevels buiten de torens (achterhelft) en de achtergevel naast de boog
for sx in (-1, 1):
    for k in range(260):
        y = rnd.uniform(-0.2 + TY + TR_, PD); z = rnd.uniform(-0.1, PH - 0.1)
        if dens(y, z, 9 + sx) < 0.42: continue
        card(Vector((sx * (PW + 0.03 + rnd.uniform(0, 0.14)), y, z)), Vector((sx, 0, 0)), rnd.uniform(0.32, 0.48), rnd.uniform(0.2, 0.6))
for k in range(220):
    x = rnd.choice((-1, 1)) * rnd.uniform(1.95, PW); z = rnd.uniform(-0.1, PH - 0.1)
    if dens(x, z, 13) < 0.38: continue
    card(Vector((x, PD + 0.03 + rnd.uniform(0, 0.14), z)), Vector((0, 1, 0)), rnd.uniform(0.32, 0.48), rnd.uniform(0.2, 0.6))
me = bpy.data.meshes.new("BAKE_klimop"); bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new("BAKE_klimop", me); bpy.data.collections["FORMS"].objects.link(ob); ob["owner"] = OWNER
m = bpy.data.materials.get("MAT_klimop") or bpy.data.materials.new("MAT_klimop")
if bpy.app.version < (5, 0, 0): m.use_nodes = True
nt = m.node_tree; bsdf = next(nd for nd in nt.nodes if nd.type == "BSDF_PRINCIPLED")
tex = next((nd for nd in nt.nodes if nd.type == "TEX_IMAGE"), None) or nt.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(os.path.join(ROOT, "textures", "PP_klimop_kleur.png"), check_existing=True)
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"]); nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
m.diffuse_color = (0.15, 0.3, 0.1, 1); ob.data.materials.append(m)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=master)
print("[03c_klimop] kaarten", CNT[0], "tris", CNT[0] * 2)
