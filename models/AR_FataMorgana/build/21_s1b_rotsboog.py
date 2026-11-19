"""21_s1b_rotsboog: sectie 1 (Jungle), stuk 1b: de rotsgrot direct achter het gordijn (Daan 19 nov: "Ja, 1b").
Referentie POV 2025 (ref/video/s1/t124.5..t131): achter het gordijn ligt meteen een lage, korte grot van donkergrijze rots met
grillige, gelaagde breuklijnen in het plafond (126,5-128,5 s); de boot vaart er in ~3 s doorheen (ongeveer 2 m) en ziet door de
onregelmatige boog de jungle met het paleis in de verte. Boog ~3,6 m breed, top ~2,5 m boven het water, zijwanden bijna recht.
Opbouw (modelmeters, hal-westmuur x -3,5, gordijn x -3,62, vaarpad y -326,5):
  - tunnel: binnenvlak van x -3,72 tot -5,7, onregelmatige boogdoorsnede, normaal naar binnen
  - oostrand: ring tussen de boog en de muuropening (y -328,9..-324,1, tot z -0,4) op x -3,72, kant hal (zichtbaar als het gordijn open is)
  - westkant: rotswand op x -5,7 rond de boog (y -329,7..-323,3, z -3,6..1,3), uitgebold naar de jungle, kant jungle
Vrije ruimte voor de sloep (1,9 m breed): |y + 326,5| >= 1,3 tot z -1,8, top >= z -0,95.
Verplaatsing = gelaagde ruis (mathutils.noise) + horizontale breukbanden. Materiaal in Studio: Rock, donker warmgrijs.
Modelstelsel = 02/03. Deel "junglerots". Gebruik: blender --background --python build/21_s1b_rotsboog.py [-- --render]"""
import bpy, bmesh, os, sys, math
from mathutils import Vector, noise

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]; L = G3["L"]
OWNER = "phase:21_s1b_rotsboog"
KL = {"rots": (0.3, 0.29, 0.27)}
ZW, ZB = -3.2, -3.7
YC = -326.5
X0, X1 = -3.72, -5.7                 # tunnel oost (achter het gordijn) -> west (jungle)
W, ZTOP = 1.8, -0.75                 # halve breedte, top van de boog
NP, NX = 64, 14                      # punten over de boog, ringen langs de tunnel


def P(x, y, z): return L(x, y) + Vector((0, 0, z))


def fbm(p, okt=4):
    s, a, f = 0.0, 1.0, 1.0
    for _ in range(okt):
        s += a * noise.noise(p * f); a *= 0.5; f *= 2.1
    return s


def richel(p):
    """scherpe ruggen (1 - |ruis|): hoekige, gebroken rotsvlakken"""
    return (1.0 - abs(noise.noise(p))) ** 3


def breuk(p):
    """horizontale lagen met scherpe randjes (gelaagde rots, video 127,5 s)"""
    t = p.z * 2.4 + 0.6 * noise.noise(p * 0.7 + Vector((3.1, 0, 0)))
    fr = t - math.floor(t)
    return 0.12 * (fr ** 4)


def profiel(t):
    """t 0..1 over de boog (zuid onder -> top -> noord onder): (dy, z) van de kale boog"""
    th = math.pi * t
    c, s = math.cos(th), math.sin(th)
    dy = -W * math.copysign(abs(c) ** 0.55, c)
    z = (ZB - 0.2) + (ZTOP - ZB + 0.2) * (abs(s) ** 0.65)
    return dy, z


def grot_punt(t, x):
    """punt op het tunnelvlak met ruis, naar buiten (in de rots) verschoven; vrije ruimte bewaakt"""
    dy, z = profiel(t)
    n = Vector((0, dy, z - (ZB - 0.2) * 0.0 - (-2.6)))          # ruwe richting weg van de as (y = YC, z = -2,6)
    n = n.normalized() if n.length > 1e-6 else Vector((0, 0, 1))
    p = Vector((x, YC + dy, z))
    d = 0.26 * (fbm(p * 1.1) + 0.5) + 0.14 * richel(p * 2.3) + breuk(p)
    q = p + Vector((0, n.y, n.z)) * d
    if q.z < -1.8 and abs(q.y - YC) < 1.3: q.y = YC + math.copysign(1.3, q.y - YC)
    if abs(q.y - YC) < 1.0 and q.z < -0.95: q.z = max(q.z, -0.95)
    return q


G = {"rots": bmesh.new()}


def rooster(rij, naar):
    """rij = lijst van ringen (lijst van Vector); vlakken tussen opeenvolgende ringen, normaal richting naar(p)"""
    bm = G["rots"]; uvl = bm.loops.layers.uv.verify()
    vs = [[bm.verts.new(P(*q)) for q in ring] for ring in rij]
    for j in range(len(vs) - 1):
        for i in range(len(vs[j]) - 1):
            f = bm.faces.new([vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]])
            f.normal_update()
            c = sum((v.co for v in f.verts), Vector()) / 4
            if f.normal.dot(naar(c)) < 0: f.normal_flip()
            for lp in f.loops:
                co = lp.vert.co; lp[uvl].uv = (co.x * 0.5 + co.y * 0.5, co.z * 0.5)


def rand_punt(t, xv, y0, y1, z0, z1):
    """punt op de rechthoekige buitenrand (y0..y1, z0..z1) die hoort bij t over de boog (zuid onder -> top -> noord onder)"""
    hoogte = z1 - z0; breed = y1 - y0; omtrek = 2 * hoogte + breed
    s = t * omtrek
    if s < hoogte: return Vector((xv, y0, z0 + s))
    if s < hoogte + breed: return Vector((xv, y0 + (s - hoogte), z1))
    return Vector((xv, y1, z1 - (s - hoogte - breed)))


def bouw():
    ts = [i / NP for i in range(NP + 1)]
    xs = [X0 + (X1 - X0) * j / NX for j in range(NX + 1)]
    tunnel = [[grot_punt(t, x) for t in ts] for x in xs]
    as_ = lambda c: Vector((0, YC, -2.6))
    # tunnel: normaal naar de as (in Blender-wereld: as = L(x, YC) op hoogte -2,6)
    def naar_as(c):
        a = L(0, 0); ex = L(1, 0) - a; ey = L(0, 1) - a
        M = [[ex.x, ey.x], [ex.y, ey.y]]; det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
        dx, dyw = c.x - a.x, c.y - a.y
        px = (M[1][1] * dx - M[0][1] * dyw) / det
        mid = P(px, YC, -2.0)
        return mid - c
    rooster(tunnel, naar_as)
    # oostrand: van de tunnelmond naar de muuropening, kant hal (+x park)
    oost = L(1, 0) - L(0, 0); oost.z = 0
    ringen = []
    for k in range(5):
        f = k / 4
        ring = []
        for i, t in enumerate(ts):
            a = tunnel[0][i]; b = rand_punt(t, X0, -328.9, -324.1, ZB - 0.3, -0.4)
            q = a.lerp(b, f); q.x = X0 + 0.04 * f
            ring.append(q)
        ringen.append(ring)
    rooster(ringen, lambda c: oost)
    # westkant: rotswand rond de boog, uitgebold naar de jungle (-x park)
    west = -oost
    ringen = []
    for k in range(10):
        f = k / 9
        ring = []
        for i, t in enumerate(ts):
            a = tunnel[-1][i]; b = rand_punt(t, X1, -329.7, -323.3, ZB - 0.3, 1.3)
            q = a.lerp(b, f)
            bol = 0.12 + 0.2 * (fbm(q * 1.2 + Vector((7, 0, 0))) + 0.5) + 0.16 * richel(q * 2.0) + breuk(q) * 1.5
            q.x = X1 - min(0.5, max(0.0, bol)) * (1.0 - 0.5 * f)     # max 0,5 m de jungle in (haarspeldbocht vlak erachter)
            ring.append(q)
        ringen.append(ring)
    rooster(ringen, lambda c: west)


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in G.items():
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
        # dubbelzijdig: Roblox tekent maar één kant (Blender beide, dus de renders logen); kopie met omgekeerde normaal
        oud = list(bm.faces); uvl = bm.loops.layers.uv.verify()
        for f in oud:
            nv = [bm.verts.new(v.co) for v in reversed(f.verts)]
            uvs = [lp[uvl].uv.copy() for lp in reversed(f.loops)]
            g = bm.faces.new(nv)
            for lp, uv in zip(g.loops, uvs): lp[uvl].uv = uv
        me = bpy.data.meshes.new("FM_s1_" + rol); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
        o = bpy.data.objects.new("FM_s1_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "junglerots"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*KL[rol], 1); me.materials.append(m); col.objects.link(o)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[21_s1b_rotsboog] klaar:", {o.name: len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER})


main()
