"""06_omgeving: rond het bad (deel "omgeving"): keien, paaltjesrand, beplanting, entree. Draai NA 03_vormen (gebruikt Bak).
Bronnen: video 4CKAjMsJHh8 0:00-0:45 (bord "Archipel" aan een donkere lantaarnpaal, regelbord, kaartrots met kist, ton en
kisten, bamboehekken met gaas, plantvakken met paaltjesrand, waaierpalmen, bananen, bamboe; ronde keien op het strand),
Archipel-doorsnede-entree.jpg (lantaarns, banieren, bamboehek), lemma (keien om op te zitten; tropische beplanting met
rood/oranje bloeiende siergember; zitgelegenheid ontbreekt).
Gebruik: blender --background --python build/06_omgeving.py -- --master AR_Archipel_master.blend [--render]"""
import bpy, sys, os, math, random
from mathutils import Vector, Matrix

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, "build"))
import plan as P
import importlib.util
spec = importlib.util.spec_from_file_location("vormen_lib", os.path.join(D, "build", "03_vormen.py"))
V = importlib.util.module_from_spec(spec)
sys.argv_bak = sys.argv; sys.argv = [sys.argv[0]]           # 03_vormen.main() niet uitvoeren bij import
src = open(os.path.join(D, "build", "03_vormen.py")).read().replace("\nmain()\n", "\n")
exec(compile(src, "03_vormen.py", "exec"), V.__dict__)
sys.argv = sys.argv_bak

OWNER = "phase:06_omgeving"
V.OWNER = OWNER
B = V.B
M, cil, doos, buis, bol = V.M, V.cil, V.doos, V.buis, V.bol
rnd = random.Random(1808)
V.KLEI.update({"palmblad": (0.3, 0.45, 0.2), "palmstam": (0.38, 0.28, 0.18), "bananenblad": (0.35, 0.58, 0.22), "bananenstam": (0.4, 0.5, 0.25),
               "gember": (0.3, 0.45, 0.2), "bamboeblad": (0.35, 0.5, 0.22), "bamboestengel": (0.62, 0.62, 0.3), "struik": (0.25, 0.4, 0.18),
               "kei": (0.62, 0.58, 0.52), "paaltje": (0.5, 0.4, 0.3), "hekbamboe": (0.8, 0.66, 0.36), "gaas": (0.5, 0.5, 0.5),
               "pad": (0.72, 0.58, 0.52), "lantaarnpaal": (0.2, 0.16, 0.14), "bord": (0.15, 0.2, 0.4), "kaartsteen": (0.3, 0.3, 0.32),
               "banier_groen": (0.1, 0.3, 0.2), "banier_blauw": (0.1, 0.15, 0.4)})
SL = lambda rol, naam=None: (rol, "omgeving", "AR_" + (naam or rol))


def kaart(rol, voet, d, s, L, W, kromming=0.0, nseg=1):
    """dubbelzijdige bladkaart vanaf voet langs richting d (lengte L), breedte W langs s; kromming laat de punt hangen"""
    voet, d, s = Vector(voet), Vector(d).normalized(), Vector(s).normalized()
    up = d.cross(s).normalized()
    pts = []
    for k in range(nseg + 1):
        t = k / nseg
        pts.append(voet + d * (L * t) - up * (kromming * L * t * t) + Vector((0, 0, -kromming * L * t * t * 0.6)))
    for k in range(nseg):
        a, b = pts[k], pts[k + 1]; t0, t1 = k / nseg, (k + 1) / nseg
        q = [a - s * W / 2, a + s * W / 2, b + s * W / 2, b - s * W / 2]
        uv = [(0, t0), (1, t0), (1, t1), (0, t1)]
        B.vlak(SL(rol, rol), q, uv); B.vlak(SL(rol, rol), q[::-1], uv[::-1])


def palm(c, h):
    c = Vector(c); scheef = Vector((rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), 0))
    pts = [c + scheef * (t * t) + Vector((0, 0, h * t)) for t in (0, 0.33, 0.66, 1.0)]
    for a, b, r0, r1 in zip(pts, pts[1:], (0.16, 0.15, 0.14), (0.15, 0.14, 0.13)):
        cil(SL("palmstam"), a, b, r0, r1, 10, 0.6, 1.0, ruw=0.12)
    top = pts[-1]
    n = 18
    for k in range(n):
        az = k * 2.39996 + rnd.uniform(-0.1, 0.1)
        el = math.radians(70 - 95 * (k / (n - 1)) ** 0.8)
        d = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)))
        steel = top + d * 0.55
        cil(SL("palmstam", "palmsteel"), top, steel, 0.02, 0.015, 5, 0.3, 0.5, doppen=False)
        s = d.cross(Vector((0, 0, 1))).normalized()
        kaart("palmblad", steel - d * 0.08, d, s, 0.95, 1.0, 0.12, 2)


def banaan(c, h):
    c = Vector(c)
    cil(SL("bananenstam"), c, c + Vector((0, 0, h)), 0.11, 0.08, 10, 0.5, 1.0)
    top = c + Vector((0, 0, h))
    for k in range(7):
        az = k * 2.39996 + rnd.uniform(-0.2, 0.2); el = math.radians(rnd.uniform(35, 70))
        d = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)))
        s = d.cross(Vector((0, 0, 1))).normalized()
        kaart("bananenblad", top - Vector((0, 0, 0.15 * k)), d, s, rnd.uniform(1.3, 1.8), 0.5, 0.35, 5)


def gemberpol(c, h=1.3):
    c = Vector(c); a0 = rnd.uniform(0, math.pi)
    for k in range(3):
        a = a0 + k * math.pi / 3; s = Vector((math.cos(a), math.sin(a), 0))
        q = [c - s * h * 0.5, c + s * h * 0.5, c + s * h * 0.5 + Vector((0, 0, h)), c - s * h * 0.5 + Vector((0, 0, h))]
        uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
        B.vlak(SL("gember"), q, uv); B.vlak(SL("gember"), q[::-1], uv[::-1])


def bamboebos(c, n=11, h=4.5):
    c = Vector(c)
    for k in range(n):
        p = c + Vector((rnd.uniform(-0.45, 0.45), rnd.uniform(-0.45, 0.45), 0)); hh = h * rnd.uniform(0.7, 1.1)
        top = p + Vector((rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), hh))
        cil(SL("bamboestengel"), p, top, 0.03, 0.02, 6, 0.3, 1.0, doppen=False)
        for j in range(3):
            q = p.lerp(top, 0.55 + 0.17 * j); a = rnd.uniform(0, math.pi)
            s = Vector((math.cos(a), math.sin(a), 0))
            for s2 in (s, Vector((-s.y, s.x, 0))):
                quad = [q - s2 * 0.55 - Vector((0, 0, 0.5)), q + s2 * 0.55 - Vector((0, 0, 0.5)), q + s2 * 0.55 + Vector((0, 0, 0.6)), q - s2 * 0.55 + Vector((0, 0, 0.6))]
                uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
                B.vlak(SL("bamboeblad"), quad, uv); B.vlak(SL("bamboeblad"), quad[::-1], uv[::-1])


def struik(c, d=1.0, h=0.9):
    c = Vector(c)
    for k in range(4):
        a = k * math.pi / 4 + rnd.uniform(-0.2, 0.2); s = Vector((math.cos(a), math.sin(a), 0))
        q = [c - s * d / 2, c + s * d / 2, c + s * d / 2 + Vector((0, 0, h)), c - s * d / 2 + Vector((0, 0, h))]
        uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
        B.vlak(SL("struik"), q, uv); B.vlak(SL("struik"), q[::-1], uv[::-1])
    for k in range(2):
        z = h * (0.45 + 0.35 * k); a = rnd.uniform(0, math.pi)
        q = [c + Vector((math.cos(a + j * math.pi / 2) * d * 0.55, math.sin(a + j * math.pi / 2) * d * 0.55, z)) for j in range(4)]
        uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
        B.vlak(SL("struik"), q, uv); B.vlak(SL("struik"), q[::-1], uv[::-1])


def kei(c, r, plat=0.6):
    """afgeronde kei: vervormde bol, onderkant 30 % in de grond"""
    c = Vector(c); sl = SL("kei")
    seg, ring = 12, 7
    ruis = [[rnd.uniform(0.88, 1.1) for _ in range(seg)] for _ in range(ring + 1)]
    sx, sy = r * rnd.uniform(0.9, 1.2), r * rnd.uniform(0.75, 1.0); rot = rnd.uniform(0, math.pi)
    R_ = Matrix.Rotation(rot, 3, "Z")
    def F(s, t):
        a = 2 * math.pi * s; b = math.pi * (t * 0.85 - 0.35)
        k = min(ring, int(round(t * ring))); j = int(round(s * seg)) % seg; f = ruis[k][j]
        return c + R_ @ Vector((math.cos(a) * math.cos(b) * sx * f, math.sin(a) * math.cos(b) * sy * f, (math.sin(b) + 0.35) * r * plat))
    B.raster(sl, F, seg, ring, lambda s, t: (s * 2 * math.pi * r / 1.2, t * math.pi * r / 1.2), gesloten_u=True)
    B.vlak(sl, [F(1 - k / seg, 1.0) for k in range(seg)], [(0.5, 0.5)] * seg)


def ring_punten(stap, off):
    """punten op afstand off buiten de kade, elke 'stap' meter (parkcoordinaten, met buitennormaal)"""
    pts = P.KADE; n = len(pts); uit = []
    opp = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)); sg = 1 if opp > 0 else -1
    rest = 0.0
    for i in range(n):
        a, b = Vector(pts[i] + (0,)), Vector(pts[(i + 1) % n] + (0,)); L = (b - a).length; t = (b - a) / L
        nrm = Vector((t.y, -t.x, 0)) * sg
        x = rest
        while x < L:
            p = a + t * x; uit.append((p + nrm * off, nrm, t)); x += stap
        rest = x - L
    return uit


def in_ingang(x, y): return 451.5 < x < 461.5 and 140 < y < 150.5


def beplanting():
    gezet = []
    for laag, (off0, off1, stap) in enumerate(((0.9, 2.2, 1.25), (2.6, 4.6, 1.6), (5.0, 7.0, 2.4))):
        for p, nrm, t in ring_punten(stap, 0):
            off = rnd.uniform(off0, off1); q = p + nrm * off + t * rnd.uniform(-0.4, 0.4)
            x, y = q.x, q.y
            if y > 169.4 and x < 461: continue                     # wachtrijvlonder Sirocco
            if y > 171.5: continue                                  # onder de wachtrijbrug
            if in_ingang(x, y) or P.binnen(x, y, P.KADE): continue
            if any((q - g).length < 0.9 for g in gezet): continue
            gezet.append(q)
            z = P.Z_MAAIVELD; c = M((x, y), z)
            r = rnd.random()
            if laag == 0:
                if r < 0.45: gemberpol(c, rnd.uniform(1.0, 1.5))
                elif r < 0.75: struik(c, rnd.uniform(0.8, 1.2), rnd.uniform(0.6, 1.0))
                elif r < 0.9: banaan(c, rnd.uniform(1.4, 2.2))
                else: palm(c, rnd.uniform(2.0, 3.0))
            elif laag == 1:
                if r < 0.25: palm(c, rnd.uniform(2.5, 4.2))
                elif r < 0.5: banaan(c, rnd.uniform(1.8, 2.6))
                elif r < 0.7: bamboebos(c, rnd.randint(8, 13), rnd.uniform(3.5, 5.0))
                elif r < 0.85: gemberpol(c, rnd.uniform(1.2, 1.6))
                else: struik(c, rnd.uniform(1.0, 1.6), rnd.uniform(0.9, 1.4))
            else:
                if r < 0.45: bamboebos(c, rnd.randint(10, 15), rnd.uniform(4.0, 5.5))
                elif r < 0.75: struik(c, rnd.uniform(1.4, 2.0), rnd.uniform(1.2, 1.8))
                else: palm(c, rnd.uniform(3.0, 4.5))
    return len(gezet)


def keien():
    n = 0
    for p, nrm, t in ring_punten(1.9, 0):
        q = p - nrm * rnd.uniform(0.45, 1.1) + t * rnd.uniform(-0.5, 0.5)
        x, y = q.x, q.y
        if y > 169.0 or in_ingang(x, y) or not P.binnen(x, y, P.KADE): continue
        if P.binnen(x, y, P.WATER) and P.afstand(x, y, P.WATER) > 0.6: continue
        if any(math.hypot(x - h["c"][0], y - h["c"][1]) < 2.2 for h in P.HUTTEN): continue
        if rnd.random() < 0.3: continue
        z = P.bodem(x, y) or P.Z_STRAND
        kei(M((x, y), z), rnd.uniform(0.28, 0.5), rnd.uniform(0.55, 0.75)); n += 1
    return n


def paaltjesrand():
    """lage rand van verticale paaltjes buiten langs de kade aan de achterkant (west/zuidwest), video 0:45"""
    for p, nrm, t in ring_punten(0.13, 0.42):
        x, y = p.x, p.y
        if not (x < 447.5 and 146.5 < y < 169.0): continue
        h = 0.45 + 0.12 * ((round(x * 7.7 + y * 3.1)) % 3) / 2
        c = M((x, y), P.Z_MAAIVELD - 0.1)
        cil(SL("paaltje"), c, c + Vector((0, 0, h + 0.1)), 0.055, 0.055, 6, 0.35, 0.6)


def bamboehek(a, b, h=1.0):
    A, Bp = M(a, P.Z_MAAIVELD), M(b, P.Z_MAAIVELD); d = Bp - A; n = max(1, int(d.length / 1.6))
    for k in range(n + 1):
        p = A.lerp(Bp, k / n); cil(SL("hekbamboe"), p - Vector((0, 0, 0.1)), p + Vector((0, 0, h + 0.08)), 0.05, 0.045, 8, 0.3, 0.6)
    for z in (0.15, h * 0.55, h):
        cil(SL("hekbamboe"), A + Vector((0, 0, z)), Bp + Vector((0, 0, z)), 0.035, 0.035, 6, 0.3, 0.6, doppen=False)
    q = [A + Vector((0, 0, 0.15)), Bp + Vector((0, 0, 0.15)), Bp + Vector((0, 0, h)), A + Vector((0, 0, h))]
    uv = [(0, 0), (d.length / 0.5, 0), (d.length / 0.5, (h - 0.15) / 0.5), (0, (h - 0.15) / 0.5)]
    B.vlak(SL("gaas"), q, uv); B.vlak(SL("gaas"), q[::-1], uv[::-1])


def ingang():
    # pad: van de ingangsvlonder naar het zuidoosten (aansluiting op de parkpaden komt later)
    pad = [(455.0, 146.2), (456.2, 143.6), (458.0, 141.2)]
    for a, b in zip(pad, pad[1:]):
        A, Bp = M(a, P.Z_MAAIVELD + 0.03), M(b, P.Z_MAAIVELD + 0.03); d = Bp - A; t = d.normalized(); nrm = Vector((-t.y, t.x, 0))
        q = [A - nrm * 1.6, Bp - nrm * 1.6, Bp + nrm * 1.6, A + nrm * 1.6]
        B.vlak(SL("pad"), q, [(p.x / 3, p.y / 3) for p in q])
        for zij in (-1, 1):
            bamboehek((a[0] + nrm.x * zij * 1.75, a[1] + nrm.y * zij * 1.75), (b[0] + nrm.x * zij * 1.75, b[1] + nrm.y * zij * 1.75))
    # lantaarnpaal met het bord "Archipel" (video 0:06-0:12): donkere paal 4,2 m, arm naar het pad, drie lantaarns
    lp = M((453.6, 145.0)); sl = SL("lantaarnpaal")
    cil(sl, lp + Vector((0, 0, P.Z_MAAIVELD - 0.2)), lp + Vector((0, 0, 4.2)), 0.09, 0.07, 10)
    cil(sl, lp + Vector((0, 0, P.Z_MAAIVELD)), lp + Vector((0, 0, P.Z_MAAIVELD + 0.5)), 0.16, 0.12, 10)
    V.piron(lp, 4.15, 0.75)
    arm = Vector((0.55, -0.83, 0)).normalized()
    cil(sl, lp + Vector((0, 0, 3.75)), lp + arm * 1.0 + Vector((0, 0, 3.75)), 0.035, 0.035, 6)
    for k, dz in enumerate((0.0, 0.25, -0.15)):
        V.lantaarn(lp + arm * (0.35 + 0.3 * k) + Vector((0, 0, 3.7 + dz)), SL("lantaarn", "ingang_lantaarn"), SL("lantaarnglas", "ingang_lantaarnglas"), 0.5)
    # bord: dubbelzijdig vlak 2,2 x 0,55 m op 3,2 m, naar het pad gericht (loodrecht op de arm)
    s = arm; mid = lp + s * 1.2 + Vector((0, 0, 3.2))
    q = [mid - s * 1.1 - Vector((0, 0, 0.28)), mid + s * 1.1 - Vector((0, 0, 0.28)), mid + s * 1.1 + Vector((0, 0, 0.28)), mid - s * 1.1 + Vector((0, 0, 0.28))]
    n_ = s.cross(Vector((0, 0, 1))) * 0.02
    B.vlak(SL("bord"), [p + n_ for p in q], [(0, 0), (1, 0), (1, 1), (0, 1)])
    B.vlak(SL("bord"), [p - n_ for p in q[::-1]], [(1, 1), (0, 1), (0, 0), (1, 0)][::-1][::-1])
    cil(sl, lp + Vector((0, 0, 3.5)), lp + Vector((0, 0, 3.5)) + s * 0.1, 0.02, 0.02, 4)
    # regelbord aan de paal en banieren (doorsnede-entree)
    doos(SL("bord", "regelbord"), lp + Vector((0.1, 0.12, 2.0)), 0.05, 0.5, 0.75, math.radians(-35), 1.0)
    for k, (rol, hoek) in enumerate((("banier_groen", 0.3), ("banier_blauw", 3.4))):
        cil(sl, lp + Vector((0, 0, 2.95)), lp + Vector((math.cos(hoek) * 0.45, math.sin(hoek) * 0.45, 2.95)), 0.015, 0.015, 4)
    # kaartrots met kist, ton en kisten (video 0:06)
    c = M((457.9, 145.3), P.Z_MAAIVELD); R_ = Matrix.Rotation(math.radians(-35), 3, "Z")
    def F(s_, t_):
        a = 2 * math.pi * s_; w = 0.9 * (1 - 0.55 * t_) * (1 + 0.08 * math.sin(7 * a)); dd = 0.35 * (1 - 0.4 * t_)
        top = 2.3 + 0.35 * math.sin(3 * a + 1)
        return c + R_ @ Vector((math.cos(a) * w, math.sin(a) * dd, t_ * top))
    B.raster(SL("kaartsteen"), F, 16, 6, lambda s_, t_: (s_ * 2, t_ * 1.5), gesloten_u=True)
    V.kist(c + R_ @ Vector((0.2, 0.75, 0)), math.radians(-35), 0.7, 0.5, 0.45, "kist_rood", gat=False)
    V.lantaarn(c + R_ @ Vector((0.2, 0.75, 0.75)), SL("lantaarn", "ingang_lantaarn"), SL("lantaarnglas", "ingang_lantaarnglas"), 0.35)
    tc = c + R_ @ Vector((1.0, 0.55, 0))
    cil(SL("ton", "ingang_ton"), tc, tc + Vector((0, 0, 0.75)), 0.3, 0.3, 14, 1.2, 1.2)
    for zz in (0.12, 0.62): cil(SL("ijzer", "ingang_banden"), tc + Vector((0, 0, zz - 0.03)), tc + Vector((0, 0, zz + 0.03)), 0.31, 0.31, 14)
    for k in range(3):
        V.kist(c + R_ @ Vector((1.25, -0.1, 0.5 * k)), math.radians(-35 + 8 * k), 0.55, 0.55, 0.48, "kist_hout", gat=False)


def render(uit):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True
    cam_d = bpy.data.cameras.new("gatecam"); cam = bpy.data.objects.new("gatecam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    cam_d.type = "PERSP"; sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    for naam, pos, doel, lens in (("omg_vogel", (472.0, 136.0, 22.0), (452.0, 159.0, 0.0), 26), ("omg_ingang", (459.5, 139.5, 1.7), (452.0, 150.0, 2.2), 24)):
        p = M(pos[:2], pos[2]); q = M(doel[:2], doel[2]); cam_d.lens = lens
        cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(uit, naam + ".png"); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def main():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    master = os.path.abspath(a[a.index("--master") + 1]) if "--master" in a else os.path.join(D, "AR_Archipel_master.blend")
    bpy.ops.wm.open_mainfile(filepath=master)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    for me in [m for m in bpy.data.meshes if m.users == 0]: bpy.data.meshes.remove(me)
    np_ = beplanting(); nk = keien(); paaltjesrand(); ingang()
    B.bouw()
    bpy.ops.wm.save_as_mainfile(filepath=master)
    n = sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER)
    print("[06_omgeving] klaar:", np_, "planten,", nk, "keien,", n, "vlakken")
    if "--render" in a:
        uit = os.path.join(D, "review", "06_omgeving"); os.makedirs(uit, exist_ok=True); render(uit)


main()
