"""23_s1d_jungle: sectie 1 (Jungle), stuk 1d: de donkere jungle na de scherpe bocht, met de slangen (Daan 19 nov: "Ja, 1d").
Referentie POV 2025 141-174 s (ref/video/s1/t141.5..t174, opgehelderd bekeken): na de haarspeldbocht vaart de boot door dichte, donkere
jungle: rood/oranje aangelichte bamboebladeren hangen over het water (149-156 s), kleine oranje vuurtjes laag bij het water (146-149 s,
Eftepedia: "open vuur"), een blauw verlichte rotswand rechts (151-156 s), varenpalmen met groenblauw accent (156-161 s), rode bloemtrossen
(164-169 s), roze aangelichte lianen die in bogen over het water hangen (164-174 s) en een knoestige, rood aangelichte boom; "Na enkele
meters hangen er slangen boven ons in de bomen" (Eftepedia; 171-174 s).
Kamer (route_plan): smalle gang y -322,5..-320 van x -3,7 tot 2 (geen gebouw erboven: plafond laag, z -0,05), daarna een brede poel
schuin naar het noordoosten tot de bocht bij (10; -313,8), plafond z 4,25 (onder het koepelgebouw). 1e/1f (tovenaar, poort) komen op
het westwaartse stuk (y > -314, x < 7) en blijven hier vrij.
Slangen = losse onderdelen slanga/slangb/slangc (FataMorganaS1Slangen laat ze traag zwaaien en de kop bewegen).
Helpers (strook, buis, palm, bamboe, struik) komen uit 22_s1c_jungle. Deel "junglenacht".
Gebruik: blender --background --python build/23_s1d_jungle.py"""
import bpy, bmesh, os, math, random, re
import numpy as np
from mathutils import Vector, Matrix, noise

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F22 = os.path.join(D, "build", "22_s1c_jungle.py")
src22 = open(F22).read()
exec(compile(src22[:src22.index("def oever():")], F22, "exec"))        # L, T, PAD, padafstand, P, tweezijdig, strook, buis, kruin, palm, bamboe, struik
OWNER = "phase:23_s1d_jungle"
PAD = np.c_[Q[:, 0] / 3, -Q[:, 1] / 3]                                   # vaarpad opnieuw, nu voor dit stuk
PAD = PAD[(PAD[:, 0] > -6) & (PAD[:, 0] < 14) & (PAD[:, 1] > -325) & (PAD[:, 1] < -308)]
KL = {"oever": (0.18, 0.15, 0.11), "stam": (0.37, 0.39, 0.24), "bamboe": (0.75, 0.55, 0.28), "palmblad": (1, 1, 1), "bamboeblad": (1, 1, 1),
      "breedblad": (1, 1, 1), "liaan": (1, 1, 1), "bloemrood": (1, 1, 1), "rots": (0.3, 0.29, 0.27), "boom": (0.3, 0.22, 0.15),
      "schaal": (0.35, 0.3, 0.26), "slanga": (1, 1, 1), "slangb": (1, 1, 1), "slangc": (1, 1, 1)}
G = {r: bmesh.new() for r in KL}
R = random.Random(1141)
ZW = -3.2

PL = np.load(os.path.join(D, "ref", "route_plan.npz")); POOL = PL["blauw_fijn"] | PL["zand_fijn"]
HH = np.load(os.path.join(D, "ref", "route_hoogte.npz")); PLAF = HH["plafond"]


def in_pool(x, y):
    r, c = int((-294.0 - y) / 0.1), int((x + 74.0) / 0.1)
    return 0 <= r < POOL.shape[0] and 0 <= c < POOL.shape[1] and POOL[r, c]


def in1d(x, y):
    return in_pool(x, y) and x > -3.7 and ((y < -314.2) or (x > 7.0 and y < -311.8))


def plafond(x, y):
    r, c = int((-294.0 - y) / 0.25), int((x + 74.0) / 0.25)
    v = PLAF[r, c] if 0 <= r < PLAF.shape[0] and 0 <= c < PLAF.shape[1] else np.nan
    return -0.05 if np.isnan(v) else float(v)


def randafstand(x, y, maxd=2.0):
    """afstand tot de rand van de poel (muur), grof"""
    for k in range(1, int(maxd / 0.15) + 1):
        d = k * 0.15
        for a in range(0, 360, 30):
            if not in_pool(x + d * math.cos(math.radians(a)), y + d * math.sin(math.radians(a))): return d
    return maxd


def vrij(x, y, z):
    if not in1d(x, y): return False
    if z < -0.9 and padafstand(x, y) < 1.35: return False
    return z < plafond(x, y) - 0.15


def oever():
    S = 0.25; xs = np.arange(-3.7, 12.6, S); ys = np.arange(-322.6, -311.6, S)
    Hh = np.full((len(ys), len(xs)), -99.0)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            if not in1d(x, y): continue
            dp = padafstand(x, y)
            Hh[j, i] = ZW - 0.35 + np.clip((dp - 1.5) / 1.2, 0, 1) * (0.55 + 0.35 * noise.noise(Vector((x * 0.6, y * 0.6, 1.3))))
    bm = G["oever"]; uvl = bm.loops.layers.uv.verify(); vs = {}
    def v(j, i):
        if (j, i) not in vs: vs[(j, i)] = bm.verts.new(P(xs[i], ys[j], max(Hh[j, i], ZW - 0.4)))
        return vs[(j, i)]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            q = [Hh[j, i], Hh[j, i + 1], Hh[j + 1, i + 1], Hh[j + 1, i]]
            if min(q) < -50 or max(q) < ZW - 0.02: continue
            f = bm.faces.new([v(j, i), v(j, i + 1), v(j + 1, i + 1), v(j + 1, i)]); f.normal_update()
            if f.normal.z < 0: f.normal_flip()
            for lp in f.loops: lp[uvl].uv = (lp.vert.co.x * 0.5, lp.vert.co.y * 0.5)
    return lambda x, y: max(ZW - 0.1, Hh[int(np.clip((y - ys[0]) / S, 0, len(ys) - 1)), int(np.clip((x - xs[0]) / S, 0, len(xs) - 1))])


def rotswand(cx, cy, breed, hoog, naar):
    """blauw aangelichte rotspartij (151-156 s): gebogen, ruw vlak, dubbelzijdig, kant naar het water"""
    bm = G["rots"]; n = Vector(naar).normalized(); t = Vector((-n.y, n.x, 0)); NU, NV = 14, 10
    vs = []
    for j in range(NV + 1):
        rij = []
        for i in range(NU + 1):
            u = (i / NU - 0.5) * breed; v = j / NV * hoog
            p = Vector((cx, cy, ZW - 0.3)) + t * u + Vector((0, 0, v))
            bol = 0.5 * math.sin(math.pi * i / NU) * math.sin(math.pi * min(1, j / NV * 1.2)) + 0.25 * (noise.noise(p * 1.4) + 0.4) + 0.12 * (1 - abs(noise.noise(p * 3.1))) ** 3
            rij.append(p + n * bol)
        vs.append(rij)
    for j in range(NV):
        for i in range(NU):
            q = [vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]]
            tweezijdig("rots", [P(*a) for a in q], [(i / NU, j / NV), ((i + 1) / NU, j / NV), ((i + 1) / NU, (j + 1) / NV), (i / NU, (j + 1) / NV)])


def knoestboom(voet, takken):
    """knoestige boom (174 s): dikke gedraaide stam, takken als buizen; takken = lijst van puntenlijsten"""
    v = Vector(voet); pts = []; rs = []
    for i in range(9):
        t = i / 8; p = v + Vector((0.25 * math.sin(t * 5.0), 0.2 * math.cos(t * 4.0), t * 3.4)); pts.append(p); rs.append(0.32 - 0.14 * t + 0.05 * math.sin(t * 9))
    buis("boom", pts, rs, 12)
    for tak in takken:
        tp = [Vector(p) for p in tak]; buis("boom", tp, [0.16 - 0.1 * k / (len(tp) - 1) for k in range(len(tp))], 8)
    return pts[-1]


def slang(rol, hang, lengte, fase):
    """hangende slang: één winding om de tak (bij hang), dan in een S-bocht naar beneden, kop omhoog gekruld; huid-UV langs de lengte"""
    bm = G[rol]; uvl = bm.loops.layers.uv.verify(); h = Vector(hang)
    pts = []
    N = 40
    for i in range(N + 1):
        t = i / N
        if t < 0.22:                                                     # winding om de tak (tak loopt langs x)
            a = t / 0.22 * 2 * math.pi + fase
            p = h + Vector((t * 0.6, 0.14 * math.cos(a), 0.14 * math.sin(a)))
        else:
            s = (t - 0.22) / 0.78; z = -s * lengte * 0.75
            p = h + Vector((0.13 + 0.15 * math.sin(s * 5 + fase), 0.18 * math.sin(s * 3.3 + fase), z))
            if s > 0.86: p.z += (s - 0.86) * lengte * 1.4; p.x += (s - 0.86) * 0.8   # kop krult omhoog/naar voren
        pts.append(p)
    ZIJ = 8; ringen = []
    for i, p in enumerate(pts):
        t = i / N; r = 0.055 * (0.35 + 0.65 * math.sin(math.pi * min(1, t * 1.05 + 0.03)) ** 0.5)
        if t > 0.94: r = 0.06                                            # kop
        d = (pts[min(i + 1, N)] - pts[max(i - 1, 0)]).normalized()
        a = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0)); u = d.cross(a).normalized(); w = d.cross(u)
        ringen.append([bm.verts.new(P(*(p + (u * math.cos(2 * math.pi * k / ZIJ) + w * math.sin(2 * math.pi * k / ZIJ)) * r))) for k in range(ZIJ)])
    for i in range(N):
        for k in range(ZIJ):
            f = bm.faces.new([ringen[i][k], ringen[i][(k + 1) % ZIJ], ringen[i + 1][(k + 1) % ZIJ], ringen[i + 1][k]])
            for lp, uv in zip(f.loops, [(k / ZIJ, i / N * 4), ((k + 1) / ZIJ, i / N * 4), ((k + 1) / ZIJ, (i + 1) / N * 4), (k / ZIJ, (i + 1) / N * 4)]): lp[uvl].uv = uv
    bm.faces.new(ringen[-1][::-1]); bm.normal_update()


def schaal(x, y, z):
    """stenen vuurschaal (vlam = Fire + licht in Studio, plaats_s1d)"""
    bm = G["schaal"]; prof = [(0.0, 0.0), (0.12, 0.0), (0.1, 0.18), (0.22, 0.3), (0.28, 0.42), (0.24, 0.45), (0.0, 0.36)]
    ZIJ = 12; rings = []
    for (r, h) in prof:
        rings.append([bm.verts.new(P(x + r * math.cos(2 * math.pi * k / ZIJ), y + r * math.sin(2 * math.pi * k / ZIJ), z + h)) for k in range(ZIJ)])
    for i in range(len(rings) - 1):
        for k in range(ZIJ):
            bm.faces.new([rings[i][k], rings[i][(k + 1) % ZIJ], rings[i + 1][(k + 1) % ZIJ], rings[i + 1][k]])
    bm.normal_update()


def liaanboog(a, b, zakken, rol="liaan"):
    """liaan die in een boog tussen twee punten hangt (164-174 s): smalle strook langs een kettinglijn"""
    a, b = Vector(a), Vector(b); n = 10; pts = []
    for i in range(n + 1):
        t = i / n; p = a.lerp(b, t); p.z -= zakken * 4 * t * (1 - t); pts.append(p)
    for i in range(n):
        p0, p1 = pts[i], pts[i + 1]; d = (p1 - p0).normalized(); zij = Vector((0, 0, 1)).cross(d).normalized() * 0.18
        tweezijdig(rol, [P(*(p0 - zij)), P(*(p0 + zij)), P(*(p1 + zij)), P(*(p1 - zij))], [(0, i / n), (1, i / n), (1, (i + 1) / n), (0, (i + 1) / n)])
        tweezijdig(rol, [P(*(p0 - Vector((0, 0, 0.18)))), P(*(p0 + Vector((0, 0, 0.18)))), P(*(p1 + Vector((0, 0, 0.18)))), P(*(p1 - Vector((0, 0, 0.18))))], [(0, i / n), (1, i / n), (1, (i + 1) / n), (0, (i + 1) / n)])


def bouw():
    oz = oever()
    # knoestboom met slangen boven het water (171-174 s), net voor de bocht; takken boven het pad (boven hoofdhoogte)
    top = knoestboom((10.6, -318.4, oz(10.6, -318.4) - 0.2), [
        [(10.7, -318.3, 2.2), (9.6, -317.6, 2.0), (8.4, -316.6, 1.6), (7.2, -315.6, 1.5)],
        [(10.5, -318.5, 2.8), (11.3, -316.8, 3.1), (11.0, -315.2, 3.3)],
        [(10.6, -318.4, 1.4), (9.4, -319.6, 1.7), (8.0, -320.0, 1.9)]])
    slang("slanga", (8.9, -317.0, 1.75), 1.9, 0.0)
    slang("slangb", (7.7, -316.0, 1.5), 1.6, 1.7)
    slang("slangc", (11.15, -316.0, 3.2), 1.8, 3.1)
    # blauw verlichte rotspartij rechts (zuid) van het brede stuk (151-156 s)
    rotswand(4.2, -321.9, 3.2, 2.8, (-0.4, 1.0, 0))
    rotswand(12.0, -315.6, 2.2, 3.4, (-1.0, 0.1, 0))
    # vuurschalen laag bij het water (146-149 s)
    for (x, y) in ((3.2, -317.6), (6.3, -319.9), (11.4, -317.2)):
        if in1d(x, y): schaal(x, y, oz(x, y) - 0.05)
    # bamboe (rood/oranje aangelicht) en varenpalmen
    for (cx, cy) in ((4.6, -317.2), (7.6, -319.6), (11.6, -319.6), (2.6, -319.4)):
        for _ in range(R.randint(4, 6)):
            x, y = cx + R.uniform(-0.5, 0.5), cy + R.uniform(-0.4, 0.4)
            if not vrij(x, y, ZW): continue
            hmax = min(5.5, plafond(x, y) - oz(x, y) - 0.2)
            if hmax > 1.5: bamboe((x, y, oz(x, y) - 0.1), R.uniform(0.6, 1.0) * hmax, R.uniform(0.05, 0.25), R.uniform(0, 2 * math.pi))
    for (x, y, h) in ((5.8, -319.3, 1.3), (9.2, -319.4, 1.8), (3.8, -317.9, 1.0), (12.0, -317.8, 2.2)):
        if vrij(x, y, ZW): palm((x, y, oz(x, y)), (x + 0.1, y + 0.1, oz(x, y) + h), 0.11, 0.08, 10, 1.4, 0.55, 0.5)
    # struiken en blad tegen de wanden
    n = 0; tries = 0
    while n < 150 and tries < 6000:
        tries += 1
        x, y = R.uniform(-3.7, 12.5), R.uniform(-322.6, -311.8); z = oz(x, y)
        if z < ZW + 0.05 or not vrij(x, y, z): continue
        struik(x, y, z - 0.05, R.uniform(0.5, 1.2)); n += 1
    n = 0; tries = 0
    while n < 120 and tries < 8000:
        tries += 1
        x, y = R.uniform(-3.7, 12.5), R.uniform(-322.6, -311.8)
        if not in1d(x, y) or randafstand(x, y, 0.5) > 0.35: continue
        z = R.uniform(ZW, plafond(x, y) - 0.3)
        if not vrij(x, y, z): continue
        mid = Vector((padafstand(x, y), 0, 0))
        k = int(np.argmin(np.hypot(PAD[:, 0] - x, PAD[:, 1] - y))); naar = Vector((PAD[k, 0] - x, PAD[k, 1] - y, 0)).normalized()
        strook(R.choice(("breedblad", "breedblad", "palmblad", "bamboeblad")), (x, y, z), (naar.x * 0.5, naar.y * 0.5, 0.9), R.uniform(0.7, 1.6), 0.9, 0.4, 3, R.uniform(-0.5, 0.5)); n += 1
    # rode bloemtrossen (164-169 s)
    n = 0; tries = 0
    while n < 14 and tries < 4000:
        tries += 1
        x, y = R.uniform(-3.7, 12.5), R.uniform(-322.6, -311.8); z = R.uniform(-1.0, min(2.5, plafond(x, y) - 0.4))
        if not vrij(x, y, z): continue
        a = R.uniform(0, 2 * math.pi)
        strook("bloemrood", (x, y, z), (math.cos(a) * 0.3, math.sin(a) * 0.3, 1.0), R.uniform(0.6, 1.0), 0.8, 0.2, 2, R.uniform(0, math.pi)); n += 1
    # overhangend bamboeblad / palmblad vanaf de wanden boven het water (149-156 s), boven hoofdhoogte
    n = 0; tries = 0
    while n < 80 and tries < 8000:
        tries += 1
        x, y = R.uniform(-3.7, 12.5), R.uniform(-322.6, -311.8)
        if not in1d(x, y) or randafstand(x, y, 0.5) > 0.3: continue
        zp = plafond(x, y); z = R.uniform(max(-0.7, zp - 2.5), zp - 0.15)
        k = int(np.argmin(np.hypot(PAD[:, 0] - x, PAD[:, 1] - y))); naar = Vector((PAD[k, 0] - x, PAD[k, 1] - y, 0)).normalized()
        strook(R.choice(("bamboeblad", "palmblad", "palmblad")), (x, y, z), (naar.x, naar.y, R.uniform(-0.1, 0.25)), R.uniform(1.6, 2.6), 0.7, 0.45, 5, R.uniform(-0.4, 0.4)); n += 1
    # lianen: in bogen over het water (roze aangelicht) en hangend
    for k in range(0, len(PAD), 3):
        x, y = PAD[k]
        if not in1d(x, y) or R.random() < 0.35: continue
        d = Vector((PAD[min(k + 1, len(PAD) - 1), 0] - x, PAD[min(k + 1, len(PAD) - 1), 1] - y, 0)).normalized(); dw = Vector((-d.y, d.x, 0))
        a = b = None
        for s in (1, -1):
            for q in range(1, 40):
                p = Vector((x, y, 0)) + dw * s * q * 0.15
                if not in1d(p.x, p.y): break
            if s == 1: a = Vector((x, y, 0)) + dw * (q - 1) * 0.15
            else: b = Vector((x, y, 0)) - dw * (q - 1) * 0.15
        zt = min(plafond(a.x, a.y), plafond(b.x, b.y)) - 0.2
        if zt < -0.4: continue
        liaanboog((a.x, a.y, zt), (b.x, b.y, zt - R.uniform(0, 0.3)), min(R.uniform(0.3, 0.9), zt + 0.75))
    n = 0; tries = 0
    while n < 50 and tries < 5000:
        tries += 1
        x, y = R.uniform(-3.7, 12.5), R.uniform(-322.6, -311.8)
        if not in1d(x, y): continue
        zp = plafond(x, y) - 0.05; lengte = R.uniform(1.2, 4.5)
        if padafstand(x, y) < 1.35: lengte = min(lengte, zp + 0.6)
        if lengte < 0.4: continue
        strook("liaan", (x, y, zp), (R.uniform(-0.1, 0.1), R.uniform(-0.1, 0.1), -1), lengte, 0.4, 0.0, 4, R.uniform(0, math.pi)); n += 1


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in G.items():
        if not bm.faces: continue
        me = bpy.data.meshes.new("FM_s1d_" + rol); bm.to_mesh(me); bm.free()
        if rol in ("stam", "bamboe", "oever", "rots", "boom", "schaal") or rol.startswith("slang"):
            for p in me.polygons: p.use_smooth = True
        o = bpy.data.objects.new("FM_s1d_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "junglenacht"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*KL[rol], 1); me.materials.append(m); col.objects.link(o)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[23_s1d_jungle] klaar:", {o.name: len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER})


main()
