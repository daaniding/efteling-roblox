"""22_s1c_jungle: sectie 1 (Jungle), stuk 1c: de jungle met de fata morgana (Daan 19 nov: "Ja, 1c").
Referentie POV 2025 129-140 s (ref/video/s1/t129.5..t140.5, crop paleis 137 s): na de grot een donkere poel met dichte jungle aan
alle kanten; recht vooruit, tussen de planten door, een geschilderd achterdoek met paarse lucht, oranje gloed en een klein roze paleis
op een duin (dat "even te zien is en snel weer verdwijnt", Eftepedia). Voor het doek: een grote, schuin opgaande palmstam van linksonder
naar rechtsboven (mosgroen), oranje aangelichte bamboestammen links, een waaierpalm rechts voor het doek, rode heliconia's, grote
bladeren, varens en hangende geelgroene lianen; boven alles donker bladerdak.
Kamer (route_plan): x -11,75..-3,6, y -329,2..-320 (poel), plafond z 4,5. Vaarpad = haarspeldbocht (roblox/FataMoganaVaart, gelezen
uit roblox/FataMorganaVaart.server.luau). Alles lager dan z -0,9 (hoofdhoogte in de sloep) blijft >= 1,35 m van het vaarpad.
Achterdoek en paleis zijn platte panelen met een zelflichtende afbeelding: die maakt plaats_s1c.luau in Studio (geen mesh).
Rollen: oever, stam, bamboe, palmblad, bamboeblad, breedblad, liaan, heliconia (bladkaarten dubbelzijdig, alfa-texturen uit 22t).
Modelstelsel = 02/03. Deel "junglegroen". Gebruik: blender --background --python build/22_s1c_jungle.py"""
import bpy, bmesh, os, math, random, re
import numpy as np
from mathutils import Vector, Matrix, noise

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]; L = G3["L"]
OWNER = "phase:22_s1c_jungle"
KL = {"oever": (0.18, 0.15, 0.11), "stam": (0.37, 0.39, 0.24), "bamboe": (0.75, 0.55, 0.28), "palmblad": (1, 1, 1),
      "bamboeblad": (1, 1, 1), "breedblad": (1, 1, 1), "liaan": (1, 1, 1), "heliconia": (1, 1, 1)}
G = {r: bmesh.new() for r in KL}
R = random.Random(1986)
ZW = -3.2
XA, XB, YA, YB = -11.6, -3.75, -329.1, -320.1         # poel (binnen de muren)
ZP = 4.4                                               # net onder het plafond (4,5)
XDOEK = -11.45                                         # achterdoek (plaats_s1c)

# vaarpad (modelmeters) uit het vaarscript
src = open(os.path.join(D, "roblox", "FataMorganaVaart.server.luau")).read()
Q = np.array(list(map(float, re.search(r"local P = \{([^}]*)\}", src).group(1).split(",")))).reshape(-1, 2)
PAD = np.c_[Q[:, 0] / 3, -Q[:, 1] / 3]
PAD = PAD[(PAD[:, 0] < -1) & (PAD[:, 0] > -13) & (PAD[:, 1] > -331) & (PAD[:, 1] < -318)]


def padafstand(x, y):
    return float(np.min(np.hypot(PAD[:, 0] - x, PAD[:, 1] - y)))


def vrij(x, y, z):
    """mag hier iets staan? laag (< z -0,9) alleen >= 1,35 m van het pad; niets in de grot (x > -5,8 bij y -327,8..-325,2)"""
    if x > -5.9 and -328.0 < y < -325.0: return False
    if z < -0.9 and padafstand(x, y) < 1.35: return False
    return XA - 0.1 < x < XB and YA < y < YB


def P(x, y, z): return L(x, y) + Vector((0, 0, z))


def tweezijdig(rol, pts, uvs):
    bm = G[rol]; uvl = bm.loops.layers.uv.verify()
    for omgekeerd in (False, True):
        vs = [bm.verts.new(p) for p in pts]; u = list(uvs)
        if omgekeerd: vs = vs[::-1]; u = u[::-1]
        f = bm.faces.new(vs)
        for lp, uv in zip(f.loops, u): lp[uvl].uv = uv


def strook(rol, basis, richting, lengte, breedte, buig, n=6, draai=0.0):
    """gebogen bladkaart vanaf basis (park x, y, z) in richting (park, genormaliseerd 3D), buigt naar beneden (zwaartekracht);
    v = 0 aan de voet, 1 aan de punt; breedte loodrecht op de richting, horizontaal, met draai om de as"""
    d = Vector(richting).normalized()
    zij = Vector((-d.y, d.x, 0)); zij = zij.normalized() if zij.length > 1e-4 else Vector((1, 0, 0))
    zij = Matrix.Rotation(draai, 3, d) @ zij
    p = Vector(basis); punten = []
    for i in range(n + 1):
        punten.append(p.copy())
        t = i / n
        stap = (d + Vector((0, 0, -buig * t * 1.6))).normalized() * (lengte / n)
        p = p + stap
    for i in range(n):
        w0 = breedte * (0.35 + 0.65 * math.sin(math.pi * min(1, (i / n) * 0.9 + 0.1)))
        w1 = breedte * (0.35 + 0.65 * math.sin(math.pi * min(1, ((i + 1) / n) * 0.9 + 0.1)))
        a, b = punten[i], punten[i + 1]
        q = [a - zij * w0 / 2, a + zij * w0 / 2, b + zij * w1 / 2, b - zij * w1 / 2]
        tweezijdig(rol, [P(*v) for v in q], [(0, i / n), (1, i / n), (1, (i + 1) / n), (0, (i + 1) / n)])


def buis(rol, punten, stralen, zijden=10, ringen=True):
    """kegelvormige stam langs punten (park), straal per punt; dicht onder/boven niet nodig (staat in water/kruin)"""
    bm = G[rol]; uvl = bm.loops.layers.uv.verify(); ring_vs = []
    for i, (p, r) in enumerate(zip(punten, stralen)):
        d = (punten[min(i + 1, len(punten) - 1)] - punten[max(i - 1, 0)]).normalized()
        a = Vector((1, 0, 0)) if abs(d.x) < 0.9 else Vector((0, 1, 0)); u = d.cross(a).normalized(); v = d.cross(u)
        ring_vs.append([bm.verts.new(P(*(p + (u * math.cos(2 * math.pi * k / zijden) + v * math.sin(2 * math.pi * k / zijden)) * r))) for k in range(zijden)])
    for i in range(len(ring_vs) - 1):
        for k in range(zijden):
            f = bm.faces.new([ring_vs[i][k], ring_vs[i][(k + 1) % zijden], ring_vs[i + 1][(k + 1) % zijden], ring_vs[i + 1][k]])
            for lp, uv in zip(f.loops, [(k / zijden, i), ((k + 1) / zijden, i), ((k + 1) / zijden, i + 1), (k / zijden, i + 1)]): lp[uvl].uv = uv
    bm.normal_update()


def kruin(top, n, lengte, breedte, buig, kantel=0.35):
    for k in range(n):
        a = 2 * math.pi * k / n + R.uniform(-0.25, 0.25)
        d = Vector((math.cos(a), math.sin(a), R.uniform(0.15, 0.55))).normalized()
        strook("palmblad", top, d, lengte * R.uniform(0.85, 1.15), breedte, buig * R.uniform(0.8, 1.2), 6, R.uniform(-kantel, kantel))


def palm(voet, top, r0, r1, bladen, lengte, breedte=0.55, buig=0.7):
    voet, top = Vector(voet), Vector(top)
    pts, rs = [], []
    for i in range(11):
        t = i / 10; p = voet.lerp(top, t)
        p += Vector((0, 0, 0)) + (top - voet).cross(Vector((0, 0, 1))).normalized() * 0.25 * math.sin(math.pi * t) if (top - voet).cross(Vector((0, 0, 1))).length > 1e-3 else Vector()
        pts.append(p); rs.append(r0 + (r1 - r0) * t)
    buis("stam", pts, rs, 12)
    kruin(pts[-1], bladen, lengte, breedte, buig)


def bamboe(voet, hoogte, helling, richting):
    v = Vector(voet); d = Vector((math.cos(richting) * math.sin(helling), math.sin(richting) * math.sin(helling), math.cos(helling)))
    pts = [v + d * hoogte * i / 8 for i in range(9)]; buis("bamboe", pts, [0.05] * 9, 8)
    for i in range(5, 9):                                                # bladpluimen bovenaan
        for _ in range(2):
            a = R.uniform(0, 2 * math.pi)
            strook("bamboeblad", pts[i], (math.cos(a), math.sin(a), R.uniform(-0.2, 0.3)), R.uniform(0.6, 1.0), 0.6, 0.5, 3, R.uniform(-0.6, 0.6))


def struik(x, y, z, grootte):
    for k in range(R.randint(3, 5)):
        a = R.uniform(0, 2 * math.pi)
        strook("breedblad", (x, y, z), (math.cos(a) * 0.6, math.sin(a) * 0.6, 1.0), grootte * R.uniform(0.8, 1.2), grootte * 0.9, 0.35, 3, R.uniform(-0.5, 0.5))


def oever():
    """oeverheuvels uit het water langs de randen, laag waar het pad dichtbij is; kale bodem onder water niet nodig"""
    S = 0.25; xs = np.arange(XA, XB + 1e-6, S); ys = np.arange(YA, YB + 1e-6, S)
    H = np.zeros((len(ys), len(xs)))
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            dp = padafstand(x, y); rand = min(x - XA, XB - x, y - YA, YB - y)
            h = ZW - 0.35 + np.clip((dp - 1.5) / 1.2, 0, 1) * (0.55 + 0.35 * noise.noise(Vector((x * 0.6, y * 0.6, 0.3))))
            if x > -5.9 and -328.2 < y < -324.8: h = ZW - 0.4                     # grotmond
            if x < XDOEK + 1.6 and -328.0 < y < -324.6: h = min(h, ZW + 0.1)     # zicht op het paleis laag houden
            H[j, i] = h
    bm = G["oever"]; uvl = bm.loops.layers.uv.verify()
    vs = [[bm.verts.new(P(x, y, H[j, i])) for i, x in enumerate(xs)] for j, y in enumerate(ys)]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            if max(H[j, i], H[j, i + 1], H[j + 1, i], H[j + 1, i + 1]) < ZW - 0.02: continue
            f = bm.faces.new([vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]])
            f.normal_update()
            if f.normal.z < 0: f.normal_flip()
            for lp in f.loops: lp[uvl].uv = (lp.vert.co.x * 0.5, lp.vert.co.y * 0.5)
    return H, xs, ys


def hoogte(H, xs, ys, x, y):
    i = int(np.clip((x - xs[0]) / 0.25, 0, len(xs) - 1)); j = int(np.clip((y - ys[0]) / 0.25, 0, len(ys) - 1)); return H[j, i]


def bouw():
    H, xs, ys = oever()
    oz = lambda x, y: max(ZW - 0.1, hoogte(H, xs, ys, x, y))
    # grote schuine palmstam: van linksonder (zuid, achter) naar rechtsboven, voor het doek langs (video 133-140 s)
    palm((-9.9, -328.6, oz(-9.9, -328.6)), (-8.0, -323.0, 3.9), 0.24, 0.16, 11, 2.4, 0.6, 0.8)
    # waaierpalm rechts voor het doek (137 s), kruin laag
    palm((-10.2, -324.0, oz(-10.2, -324.0)), (-10.0, -324.2, -0.9), 0.12, 0.1, 12, 1.5, 0.55, 0.5)
    palm((-10.9, -321.0, oz(-10.9, -321.0)), (-10.6, -321.3, 1.6), 0.15, 0.11, 10, 2.0, 0.55, 0.7)
    palm((-8.6, -320.6, oz(-8.6, -320.6)), (-8.4, -320.9, 2.8), 0.16, 0.12, 10, 2.2, 0.55, 0.7)
    palm((-11.0, -328.6, oz(-11.0, -328.6)), (-10.8, -328.3, 0.6), 0.14, 0.1, 9, 1.8, 0.55, 0.6)
    # bamboe links bij de grotuitgang (129-135 s, oranje aangelicht) en achterin
    for (cx, cy) in ((-7.5, -328.5), (-9.0, -328.9), (-11.2, -322.6), (-6.4, -320.5)):
        for _ in range(R.randint(4, 6)):
            x, y = cx + R.uniform(-0.4, 0.4), cy + R.uniform(-0.3, 0.3)
            if not vrij(x, y, ZW): continue
            bamboe((x, y, oz(x, y) - 0.1), R.uniform(4.0, 6.5), R.uniform(0.05, 0.28), R.uniform(0, 2 * math.pi))
    # struiken en varens op de oevers
    n = 0
    while n < 170:
        x, y = R.uniform(XA, XB), R.uniform(YA, YB); z = oz(x, y)
        if z < ZW + 0.05 or not vrij(x, y, z): continue
        if x < XDOEK + 1.6 and -327.8 < y < -324.8 and R.random() < 0.8: continue    # zicht op het paleis
        struik(x, y, z - 0.05, R.uniform(0.6, 1.3)); n += 1
    # heliconia's (hangend, rood/oranje) aan de oeverrand
    n = 0
    while n < 15:
        x, y = R.uniform(XA, XB), R.uniform(YA, YB); z = oz(x, y) + R.uniform(0.6, 1.4)
        if not vrij(x, y, z - 1.0) or oz(x, y) < ZW: continue
        a = R.uniform(0, 2 * math.pi)
        strook("heliconia", (x, y, z), (0.15 * math.cos(a), 0.15 * math.sin(a), -1), 0.8, 0.4, 0.0, 2, R.uniform(0, math.pi)); n += 1
    # lianen vanaf het bladerdak; boven het pad eindigen ze boven hoofdhoogte
    n = 0
    while n < 75:
        x, y = R.uniform(XA, XB), R.uniform(YA, YB)
        if x > -5.9 and -328.0 < y < -325.0: continue
        lengte = R.uniform(2.5, 5.5)
        if padafstand(x, y) < 1.35: lengte = min(lengte, ZP - (-0.6))
        strook("liaan", (x, y, ZP), (R.uniform(-0.1, 0.1), R.uniform(-0.1, 0.1), -1), lengte, 0.45, 0.0, 4, R.uniform(0, math.pi)); n += 1
    # bladerdak: palmbladen vanaf de wanden schuin omlaag de kamer in, hoog boven het pad
    for k in range(95):
        kant = R.choice(("w", "z", "n"))
        if kant == "w": x, y = XA + 0.1, R.uniform(YA, YB)
        elif kant == "z": x, y = R.uniform(XA, -6.2), YA + 0.1
        else: x, y = R.uniform(XA, XB), YB - 0.1
        z = R.uniform(1.5, ZP - 0.2)
        d = Vector((-3.0 - x, -325.0 - y, R.uniform(-0.2, 0.2))).normalized()
        strook("palmblad", (x, y, z), d, R.uniform(2.0, 3.2), 0.7, 0.6, 6, R.uniform(-0.4, 0.4))
    # blad tegen de wanden (zij- en achterwanden dicht, video: nergens kale muur), van de oever tot halverwege
    for k in range(120):
        kant = R.choice(("w", "z", "n", "n", "z"))
        if kant == "w": x, y = XA + 0.15, R.uniform(YA, YB)
        elif kant == "z": x, y = R.uniform(XA, -6.0), YA + 0.15
        else: x, y = R.uniform(XA, XB), YB - 0.15
        if kant == "w" and -327.6 < y < -324.8: continue                        # het doek met het paleis vrij laten
        z = R.uniform(ZW - 0.1, 2.5)
        if not vrij(x, y, z): continue
        naar = Vector((-7.0 - x, -325.0 - y, 0)).normalized()
        strook(R.choice(("breedblad", "breedblad", "palmblad")), (x, y, z), (naar.x * 0.5, naar.y * 0.5, 1.0), R.uniform(0.8, 1.8), 0.9, 0.4, 3, R.uniform(-0.5, 0.5))


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in G.items():
        if not bm.faces: continue
        me = bpy.data.meshes.new("FM_s1c_" + rol); bm.to_mesh(me); bm.free()
        if rol in ("stam", "bamboe", "oever"):
            for p in me.polygons: p.use_smooth = True
        o = bpy.data.objects.new("FM_s1c_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "junglegroen"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*KL[rol], 1); me.materials.append(m); col.objects.link(o)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[22_s1c_jungle] klaar:", {o.name: len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER})


main()
