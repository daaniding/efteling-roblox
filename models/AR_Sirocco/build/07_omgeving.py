"""07_omgeving: scène rond de Sirocco (Daan 17 nov: "ja, omgeving bouwen"). Modelframe als 02/03 (m, x oost, y noord, z 0 = water).
Bronnen: luchtfoto in modelmeters (review/plan_luchtfoto_m.jpg), video xloCDJYf-Tw (f_004 hutje + plein, f_016 vlonder met ruwe
palen en gaas, f_028/f_034 zeilkap met lantaarns en bamboe kruisschoren, f_133 stenen uitgangsbrug, f_136 hutje met hek aan de
brug, f_142 haven met Sindbads boot, zandstrand met rotsen), Sirocco-meandering.jpg, Wachtrij-sirocco-lamp.jpg, lemma
(wachtrij: vlonder langs Archipel, dan turquoise zeil, bocht van 180 graden, meebuigend met de draaischijf naar het opstappunt).
Onderdelen: vijverbodem-rand (rotsen), wachtrijvlonder op palen met leuningen + gaas, zeilkap met schulprand en lantaarns,
rond hutje met rieten kegeldak bij de voorkant, stenen uitgangsbrug met muurtjes, haven: zeilboot (dhow) met latijnzeil (Sindbad
zelf komt later als figuur), meerpalen, boeien geel/blauw, zandstrand met rotsen, ingangsbord.
Schrijft ook exports/omgeving_info.json (vijverrand, wachtrij-looplijn, uitgangslijn, lampen) voor het plaatsscript en de bezoekers.
Gebruik: blender --background --python build/07_omgeving.py -- --master AR_Sirocco_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = "phase:07_omgeving"
random.seed(2022)
F = {"__file__": os.path.join(D, "build", "03_forms.py"), "__name__": "forms"}
exec(compile(open(os.path.join(D, "build", "03_forms.py")).read().replace("\nmain()\n", "\n"), "03_forms", "exec"), F)
stam, cil, bol, doos = F["stam"], F["cil"], F["bol"], F["doos"]
Z_PLAT, R_DEK = F["Z_PLAT"], F["R_DEK"]
Z_VLONDER = Z_PLAT                    # wachtrij op dekhoogte

# vijverrand (luchtfoto, tegen de klok in), modelmeters
# vijverrand, nagetrokken op de luchtfoto (review/vijver_zoom.jpg, 1 m-raster), tegen de klok in vanaf het noordoosten:
# smalle ring om het gebouw, ronde lob in het NW, plantvak dat er west in uitsteekt, inhammetje west (-14.9; 0), haven ZW tot de witte
# gebogen muur, plantvak tussen haven en brug, onder/oost van de brug tot y -13.3, oostrand langs de wachtrijvlonder, schiereiland
# (plantvak) binnen de haarspeld van de zeilkap
VIJVER = [(10.5, 10.8), (8.6, 11.1), (7.0, 10.6), (5.0, 11.25), (1.75, 12.6), (-2.0, 12.5), (-5.5, 11.9), (-6.2, 12.6), (-7.2, 13.3),
          (-8.9, 13.5), (-10.6, 13.2), (-11.6, 12.4), (-11.8, 11.2), (-11.2, 10.0), (-10.6, 8.9), (-11.0, 7.6), (-11.8, 6.0), (-12.8, 4.0),
          (-13.3, 2.5), (-14.6, 1.0), (-14.9, 0.0), (-14.6, -0.9), (-14.0, -1.8), (-13.2, -3.2), (-12.6, -4.8), (-12.0, -6.0),
          (-11.2, -7.6), (-11.6, -8.8), (-12.6, -10.0), (-13.8, -11.6), (-14.6, -12.3), (-13.0, -13.4), (-11.0, -14.8), (-9.8, -15.2),
          (-9.6, -13.6), (-8.8, -12.0), (-7.5, -11.0), (-3.5, -11.0), (-3.4, -13.3), (7.5, -13.3), (10.0, -11.5), (12.25, -9.25),
          (14.0, -6.25), (14.8, -2.5), (14.8, 1.25), (14.3, 3.8), (12.6, 4.0), (11.6, 6.0), (11.3, 9.3)]
STRAND = [(-12.0, -6.0), (-11.2, -7.6), (-11.6, -8.8), (-12.6, -10.0), (-13.8, -11.6), (-14.6, -12.3), (-16.0, -11.7), (-17.0, -10.2),
          (-17.3, -8.0), (-16.6, -6.0), (-14.6, -4.9), (-12.9, -4.6)]       # zandstrand west van de haven (luchtfoto: keien op licht zand)
STRAND_RAND = STRAND[:6]                              # het deel dat de vijverrand is
def in_poly(x, y, P):
    c = False; j = len(P) - 1
    for i in range(len(P)):
        (xi, yi), (xj, yj) = P[i], P[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: c = not c
        j = i
    return c
BEDRAND = [(-9.8, -15.2), (-9.6, -13.6), (-8.8, -12.0), (-7.5, -11.0), (-3.5, -11.0)]   # witte betonrand plantvak (World_of_Sinbad.jpg)
HAVENMUUR = [(-13.8, -11.6), (-14.6, -12.3), (-13.0, -13.4), (-11.0, -14.8), (-9.8, -15.2)]   # zandstenen zitmuur met boogje
BED_HAVEN = [(-9.8, -15.2), (-9.6, -13.6), (-8.8, -12.0), (-7.5, -11.0), (-3.5, -11.0), (-3.6, -16.8), (-8.4, -16.6)]
PLEINKANT = lambda x, y: (x < -11.0 and -13 < y < 7.0) or (x < -9.5 and y < -12.5)     # rand langs het plein (lichte band, witte muur)
# wachtrij: begin bij het plein (zuidoost, naast Archipel), noord langs de oostkant, zeilkap vanaf ZEIL_VANAF, bocht van 180
# graden en meebuigend met de draaischijf (r ~10.3) tot het opstappunt aan het dek
WACHTRIJ = [(5.8, -15.8), (8.0, -13.9), (11.0, -11.9), (13.8, -9.6), (15.6, -6.5), (15.9, -2.0), (15.9, 3.0), (15.75, 6.0)]
for a in range(0, 181, 20):                        # haarspeldbocht om het plantvak (luchtfoto: midden (12.0; 8.0), r 3.75)
    WACHTRIJ.append((12.0 + 3.75 * math.cos(math.radians(a)), 8.0 + 3.75 * math.sin(math.radians(a))))
for a in range(30, -59, -8):                       # meebuigend met de draaischijf naar het opstappunt (luchtfoto r ~10.2)
    WACHTRIJ.append((10.25 * math.cos(math.radians(a)), 10.25 * math.sin(math.radians(a))))
WACHTRIJ.append((8.62 * math.cos(math.radians(-62)), 8.62 * math.sin(math.radians(-62))))        # tot de dekrand (R_DEK 8,6): niet over het dek heen (z-fighting)
ZEIL_VANAF = 7                                     # index in WACHTRIJ waar de zeilkap begint
B_RIJ = 2.0                                        # breedte vlonder (Roblox: looppaden ~1,5x echt)
UITGANG_X = -2.0                                   # uitgangsbrug recht naar het zuiden (luchtfoto: muurtjes op x -3,5 en -0,5)
UITGANG = [(UITGANG_X, -8.1), (UITGANG_X, -17.3)]   # begint aan de dekrand; dek iets lager dan het gebouwdek (geen z-fighting)
HUT = (1.6, -8.5, 1.55)                             # rond hutje (luchtfoto: ronde lob aan de voorkant)
BOOT_SINDBAD = (-7.9, -8.5, math.radians(35))   # luchtfoto: boot schuin, boeg naar het noordoosten


def collectie(naam):
    c = bpy.data.collections.get(naam)
    if not c:
        c = bpy.data.collections.new(naam); bpy.context.scene.collection.children.link(c)
    return c


def obj(naam, bm, rol):
    me = bpy.data.meshes.new(naam); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(naam, me); o["owner"] = OWNER; o["rol"] = rol
    collectie("OMGEVING").objects.link(o)
    return o


def lijn_punten(pts, stap):
    """polylijn bemonsteren om de ~stap m: (punt, richting) """
    uit = []
    for i in range(len(pts) - 1):
        a, b = Vector((*pts[i], 0)), Vector((*pts[i + 1], 0)); d = b - a; L = d.length
        n = max(1, int(L / stap))
        for k in range(n):
            uit.append((a + d * (k / n), d.normalized()))
    uit.append((Vector((*pts[-1], 0)), (Vector((*pts[-1], 0)) - Vector((*pts[-2], 0))).normalized()))
    return uit


def strook(bm, pts, breedte, z, dik=0.12):
    """vlakke strook langs een polylijn (bovenkant omhoog), met zijkanten"""
    links, rechts = [], []
    for i, (x, y) in enumerate(pts):
        p = Vector((x, y, 0))
        d0 = (p - Vector((*pts[i - 1], 0))) if i > 0 else (Vector((*pts[1], 0)) - p)
        d1 = (Vector((*pts[i + 1], 0)) - p) if i < len(pts) - 1 else d0
        t = (d0.normalized() + d1.normalized()).normalized(); n = Vector((-t.y, t.x, 0))
        links.append(p + n * breedte / 2); rechts.append(p - n * breedte / 2)
    for i in range(len(pts) - 1):
        q = [links[i], rechts[i], rechts[i + 1], links[i + 1]]
        midden = sum(q, Vector()) / 4
        for zz, omhoog in ((z, True), (z - dik, False)):     # bovenkant wijst omhoog, onderkant omlaag (Roblox tekent achterkanten niet)
            f = bm.faces.new([bm.verts.new(Vector((v.x, v.y, zz))) for v in q])
            f.normal_update()
            if (f.normal.z > 0) != omhoog: f.normal_flip()
        for a, b in ((links[i], links[i + 1]), (rechts[i + 1], rechts[i])):
            f = bm.faces.new([bm.verts.new(v) for v in (Vector((a.x, a.y, z - dik)), Vector((b.x, b.y, z - dik)), Vector((b.x, b.y, z)), Vector((a.x, a.y, z)))])
            f.normal_update()
            uit = Vector(((a.x + b.x) / 2 - midden.x, (a.y + b.y) / 2 - midden.y, 0))
            if f.normal.dot(uit) < 0: f.normal_flip()      # zijkant naar buiten
    return links, rechts


def leuning(bms, rand, z, overdekt=False):
    """ruwe palen om de ~1,8 m, bovenregel + middenregel, gaas ertussen (video f_016); onder de zeilkap bamboe kruisschoren"""
    pts = [rand[0]]
    for p in rand[1:]:
        if (p - pts[-1]).length > 1.8 or p is rand[-1]: pts.append(p)
    for i, p in enumerate(pts):
        stam(bms["stam"], Vector((p.x, p.y, -0.6)), Vector((p.x, p.y, z + 1.15)), 0.09, 0.08, 8, 0.1)
        if i == 0: continue
        q = pts[i - 1]
        stam(bms["stam"], Vector((q.x, q.y, z + 1.05)), Vector((p.x, p.y, z + 1.05)), 0.06, 0.06, 6, 0.08)
        stam(bms["bamboe"], Vector((q.x, q.y, z + 0.55)), Vector((p.x, p.y, z + 0.55)), 0.035, 0.035, 6, 0.0)
        a0, a1 = Vector((q.x, q.y, z + 0.08)), Vector((p.x, p.y, z + 0.08))
        for vs in ((a0, a1, a1 + Vector((0, 0, 0.95)), a0 + Vector((0, 0, 0.95))),):
            bms["net"].faces.new([bms["net"].verts.new(v) for v in vs])
            bms["net"].faces.new([bms["net"].verts.new(v) for v in vs[::-1]])
        if overdekt:                                   # bamboe kruisschoren (f_028)
            stam(bms["bamboe"], Vector((q.x, q.y, z + 0.15)), Vector((p.x, p.y, z + 1.0)), 0.03, 0.03, 6, 0.0)
            stam(bms["bamboe"], Vector((q.x, q.y, z + 1.0)), Vector((p.x, p.y, z + 0.15)), 0.03, 0.03, 6, 0.0)


def zeilkap(bms, pts, z, lampen):
    """turquoise zeilkap over de wachtrij: palen buiten de leuning, dak licht schuin, schulprand met ornament (Sirocco-meandering.jpg)"""
    s = lijn_punten(pts, 2.4)
    boven_l, boven_r = [], []
    for k, (p, d) in enumerate(s):
        n = Vector((-d.y, d.x, 0))
        for zij, lst in ((1, boven_l), (-1, boven_r)):
            voet = p + n * zij * (B_RIJ / 2 + 0.15)
            h = 2.75 if zij == 1 else 2.55
            stam(bms["stam"], Vector((voet.x, voet.y, -0.6)), Vector((voet.x, voet.y, z + h + 0.15)), 0.1, 0.09, 8, 0.1)
            lst.append(Vector((voet.x, voet.y, z + h)))
        if k % 2 == 0:                                 # lantaarn aan de binnenpaal (Wachtrij-sirocco-lamp.jpg)
            lp = boven_r[-1] - n * 0.18 + Vector((0, 0, -0.55))
            cil(bms["lantaarn"], lp + Vector((0, 0, 0.18)), 0.1, 0.06, 6, 0.04)
            cil(bms["lantaarnglas"], lp - Vector((0, 0, 0.12)), 0.08, 0.3, 6, 0.1)
            lampen.append([lp.x, lp.y, lp.z])
    for i in range(len(s) - 1):
        a, b, c, e = boven_l[i], boven_l[i + 1], boven_r[i + 1], boven_r[i]
        for vs in ((a, e, c, b), (a, b, c, e)):        # tweezijdig doek
            bms["zeil_turkoois"].faces.new([bms["zeil_turkoois"].verts.new(v) for v in vs])
        for x0, x1 in ((a, b), (e, c)):               # schulprand (valletje met ornament), 0,4 m
            onder0, onder1 = x0 - Vector((0, 0, 0.42)), x1 - Vector((0, 0, 0.42))
            for vs in ((x0, x1, onder1, onder0), (onder0, onder1, x1, x0)):
                bms["zeilrand"].faces.new([bms["zeilrand"].verts.new(v) for v in vs])
        stam(bms["stam"], a, b, 0.07, 0.07, 6, 0.06); stam(bms["stam"], e, c, 0.07, 0.07, 6, 0.06)


def dekhek(bms):
    """hek rond de buitenrand van het vlonderdek (r 8,5) zodat niemand van het dek het water in loopt; open bij de instap
    (einde wachtrij, -62 graden) en de uitstap (brug, -106 graden)"""
    R = 8.5; open_ = [(-62, 8.5), (-106, 9.5)]
    def vrij(a): return all(abs((a - o + 180) % 360 - 180) > h for o, h in open_)
    stukken, huidig = [], []
    for k in range(361):
        a = -180 + k
        if vrij(a): huidig.append(Vector((R * math.cos(math.radians(a)), R * math.sin(math.radians(a)), 0)))
        elif huidig: stukken.append(huidig); huidig = []
    if huidig:
        if stukken and abs(math.degrees(math.atan2(stukken[0][0].y, stukken[0][0].x)) + 180) < 1.5: stukken[0] = huidig + stukken[0]
        else: stukken.append(huidig)
    for st in stukken:
        if len(st) > 3: leuning(bms, st, Z_PLAT)


def hutje(bms):
    """rond hutje aan de voorkant (f_004, f_136): bamboewand met ovale raampjes, rieten kegeldak met spitsje, hek naar de brug"""
    x, y, r = HUT
    v = cil(bms["bamboewand"], (x, y, Z_PLAT), r, 2.3, 24)
    for k in range(24):                                # bamboestokken als ribbels
        h = 2 * math.pi * k / 24
        stam(bms["bamboe"], Vector((x + (r + 0.03) * math.cos(h), y + (r + 0.03) * math.sin(h), Z_PLAT)),
             Vector((x + (r + 0.03) * math.cos(h), y + (r + 0.03) * math.sin(h), Z_PLAT + 2.3)), 0.04, 0.04, 6, 0.0)
    bm = bms["riet"]
    NA = 24; top = Vector((x, y, Z_PLAT + 5.2))
    rand = [Vector((x + (r + 0.6) * math.cos(2 * math.pi * k / NA), y + (r + 0.6) * math.sin(2 * math.pi * k / NA), Z_PLAT + 2.2)) for k in range(NA)]
    tv = bm.verts.new(top)
    for k in range(NA):
        bm.faces.new((tv, bm.verts.new(rand[k]), bm.verts.new(rand[(k + 1) % NA])))
        bm.faces.new((bm.verts.new(rand[k]), bm.verts.new(rand[k] - Vector((0, 0, 0.3))), bm.verts.new(rand[(k + 1) % NA] - Vector((0, 0, 0.3))), bm.verts.new(rand[(k + 1) % NA])))
    stam(bms["stam"], top - Vector((0, 0, 0.2)), top + Vector((0, 0, 0.9)), 0.08, 0.02, 8, 0.0)
    for k in range(4):                                 # ovale raampjes (donker)
        h = math.radians(30 + 90 * k)
        c = Vector((x + (r + 0.05) * math.cos(h), y + (r + 0.05) * math.sin(h), Z_PLAT + 1.5))
        vv = bol(bms["raam"], c, 0.25, 10)
        for q in vv:
            dd = q.co - c; q.co = c + Vector((dd.x * 0.35, dd.y * 0.35, dd.z * 1.3))


def brug(bms):
    """stenen uitgangsbrug met lage muurtjes en afdekstenen (f_133, f_136)"""
    a, b = UITGANG
    links, rechts = strook(bms["bestrating"], [a, b], 2.4, Z_PLAT - 0.05, 0.6)
    for zij in (-1, 1):
        x = UITGANG_X + zij * 1.35
        doos(bms["muur"], ((x), (a[1] + b[1]) / 2, Z_PLAT + 0.35), (0.3, abs(b[1] - a[1]), 0.9))
        doos(bms["afdek"], ((x), (a[1] + b[1]) / 2, Z_PLAT + 0.84), (0.4, abs(b[1] - a[1]) + 0.1, 0.1))
    # hek van twee latten-deuren bij het hutje (f_136), opengeslagen tegen de muurtjes zodat de looproute vrij is
    y0 = -8.6
    for zij in (-1, 1):
        x = UITGANG_X + zij * 1.05
        for k in range(7):
            yy = y0 - k * 0.16
            stam(bms["bamboe"], Vector((x, yy, Z_PLAT)), Vector((x, yy, Z_PLAT + 1.1)), 0.035, 0.035, 6, 0.0)
        stam(bms["bamboe"], Vector((x, y0, Z_PLAT + 0.9)), Vector((x, y0 - 1.0, Z_PLAT + 0.9)), 0.03, 0.03, 6, 0.0)


def vijverrand(bms):
    """natuurstenen band langs de hele rand (licht langs het plein en de witte havenmuur, grijs langs de plantvakken), losse
    keien alleen langs de plantvakken (luchtfoto: geen strand, het plein loopt tot aan de rand)"""
    pts = VIJVER + [VIJVER[0]]
    for k in range(len(pts) - 1):
        a, b = Vector((*pts[k], 0)), Vector((*pts[k + 1], 0)); m = (a + b) / 2
        d = (b - a); L = d.length; d = d.normalized(); n = Vector((d.y, -d.x, 0))
        if m.x < -11.0 and -12.6 < m.y < -5.5: continue      # strand: geen rand, het zand loopt het water in
        if pts[k] in HAVENMUUR and pts[k + 1] in HAVENMUUR: continue   # zandstenen muur, zie havenmuur()
        if pts[k] in BEDRAND and pts[k + 1] in BEDRAND:      # gladde witte betonrand om het plantvak
            c = m + n * 0.15
            doos(bms["witrand"], (c.x, c.y, 0.12), (L + 0.32, 0.3, 0.62), math.atan2(d.y, d.x))
            continue
        plein = PLEINKANT(m.x, m.y)
        rol = "afdek" if plein else "steen"
        c = m + n * 0.2
        doos(bms[rol], (c.x, c.y, 0.05 if plein else 0.0), (L + 0.35, 0.45 if plein else 0.5, 0.55 if plein else 0.5), math.atan2(d.y, d.x))
        if not plein:
            for p, _ in lijn_punten([pts[k], pts[k + 1]], 1.6)[:-1]:
                if random.random() < 0.6:
                    r = random.uniform(0.25, 0.42); cc = p + n * random.uniform(0.25, 0.5) + Vector((0, 0, 0.1))
                    vv = bol(bms["steen"], cc, r, 7)
                    for q in vv:
                        dd = q.co - cc; q.co = cc + Vector((dd.x * random.uniform(0.9, 1.3), dd.y * random.uniform(0.9, 1.3), dd.z * 0.55))


def havenmuur(bms):
    """zandstenen brug langs het plein aan de zuidwestkant van de haven (World_of_Sinbad.jpg: bezoekers zitten op de borstwering,
    het water loopt onder een boog door): muur 0,8 m dik tot 1,0 m boven het water, brede afdekstenen, vierkante pijlers met kap aan
    beide einden, ingemetselde stenen; in het midden een echte boogopening (r 0,8 m) met tunnel door de muur, boogstenen en sluitsteen;
    links en rechts van de boog een roostervenster met blauw licht"""
    random.seed(11)
    DIK, TOP = 0.8, 1.0
    segs = []
    for k in range(len(HAVENMUUR) - 1):
        a, b = Vector((*HAVENMUUR[k], 0)), Vector((*HAVENMUUR[k + 1], 0))
        d = b - a; L = d.length; d.normalize(); n = Vector((d.y, -d.x, 0))       # naar buiten (van de vijver af)
        if in_poly(((a + b) / 2 + n * 0.5).x, ((a + b) / 2 + n * 0.5).y, VIJVER): n = -n
        segs.append((a, b, d, n, L, math.atan2(d.y, d.x)))
    for k, (a, b, d, n, L, hoek) in enumerate(segs):
        m = (a + b) / 2
        boog = k == 2
        if not boog:
            c = m + n * DIK / 2
            doos(bms["zandsteen"], (c.x, c.y, (TOP - 0.45) / 2), (L + 0.8, DIK, TOP + 0.45), hoek)
        else:                                          # muur met boogopening: twee blokken naast de boog, latei erboven
            r = 0.8; zb = 0.0
            for zij in (-1, 1):
                lb = L / 2 - r
                c = m + d * zij * (r + lb / 2) + n * DIK / 2
                doos(bms["zandsteen"], (c.x, c.y, (TOP - 0.45) / 2), (lb + 0.4, DIK, TOP + 0.45), hoek)
            # boogvulling: ring van blokjes boven de boog tot de bovenkant
            for i2 in range(12):
                t0 = math.pi * i2 / 12; t1 = math.pi * (i2 + 1) / 12
                for t in (t0,):
                    pass
            NB = 14
            for i2 in range(NB):
                t0, t1 = math.pi * i2 / NB, math.pi * (i2 + 1) / NB
                for zz in (0, 1):
                    pass
            # vlakken: voorkant (vijverkant) en achterkant van de borstwering boven de boog, en de tunnel
            for kant, off in ((-1, 0.0), (1, DIK)):
                vs = []
                for i2 in range(NB + 1):
                    t = math.pi * i2 / NB
                    vs.append((m + d * r * math.cos(t) + n * off, zb + r * math.sin(t)))
                for i2 in range(NB):
                    (p0, z0), (p1, z1) = vs[i2], vs[i2 + 1]
                    q = [Vector((p0.x, p0.y, z0)), Vector((p1.x, p1.y, z1)), Vector((p1.x, p1.y, TOP)), Vector((p0.x, p0.y, TOP))]
                    f = bms["zandsteenvlak"].faces.new([bms["zandsteenvlak"].verts.new(v) for v in q]); f.normal_update()
                    if f.normal.dot(n * kant) < 0: f.normal_flip()
            for i2 in range(NB):                       # tunnel (donker, naar binnen gericht)
                t0, t1 = math.pi * i2 / NB, math.pi * (i2 + 1) / NB
                p0 = m + d * r * math.cos(t0); p1 = m + d * r * math.cos(t1)
                q = [Vector((p0.x, p0.y, zb + r * math.sin(t0))), Vector((p1.x, p1.y, zb + r * math.sin(t1))),
                     Vector((p1.x + n.x * DIK, p1.y + n.y * DIK, zb + r * math.sin(t1))), Vector((p0.x + n.x * DIK, p0.y + n.y * DIK, zb + r * math.sin(t0)))]
                f = bms["boog"].faces.new([bms["boog"].verts.new(v) for v in q]); f.normal_update()
                mid = sum(q, Vector()) / 4; naar_as = Vector((m.x - mid.x, m.y - mid.y, zb - mid.z)); naar_as -= n * naar_as.dot(n)
                if f.normal.dot(naar_as) < 0: f.normal_flip()
            achter = [Vector((pp.x + n.x * (DIK - 0.05), pp.y + n.y * (DIK - 0.05), zz)) for pp, zz in
                      [(m + d * r * math.cos(math.pi * i2 / NB), zb + r * math.sin(math.pi * i2 / NB)) for i2 in range(NB + 1)]]
            achter = [Vector((achter[0].x, achter[0].y, -0.4))] + achter + [Vector((achter[-1].x, achter[-1].y, -0.4))]
            f = bms["boog"].faces.new([bms["boog"].verts.new(v) for v in achter]); f.normal_update()   # donkere achterwand in de tunnel
            if f.normal.dot(-n) < 0: f.normal_flip()
            q = [m + d * r, m - d * r, m - d * r + n * DIK, m + d * r + n * DIK]     # donkere waterbodem in de tunnel (dekt het plein-terrein af)
            f = bms["boog"].faces.new([bms["boog"].verts.new(Vector((v.x, v.y, 0.31))) for v in q]); f.normal_update()
            if f.normal.z < 0: f.normal_flip()
            for zij in (-1, 1):                        # tunnelbodem-zijkanten onder water (donker)
                p = m + d * zij * r
                q = [Vector((p.x, p.y, -0.4)), Vector((p.x + n.x * DIK, p.y + n.y * DIK, -0.4)), Vector((p.x + n.x * DIK, p.y + n.y * DIK, zb)), Vector((p.x, p.y, zb))]
                f = bms["boog"].faces.new([bms["boog"].verts.new(v) for v in q]); f.normal_update()
                if f.normal.dot(-d * zij) < 0: f.normal_flip()
            for i2 in range(9):                        # boogstenen + grotere sluitsteen
                t = math.pi * (i2 + 0.5) / 9; rr = r + 0.15
                q = m + d * rr * math.cos(t) - n * 0.03 + Vector((0, 0, zb + rr * math.sin(t)))
                sl = i2 == 4
                v = doos(bms["afdek_zand"], (q.x, q.y, q.z), (0.24 if sl else 0.2, 0.1, 0.42 if sl else 0.32), hoek)
                bmesh.ops.rotate(bms["afdek_zand"], cent=q, matrix=Matrix.Rotation((t - math.pi / 2), 3, n), verts=v)
        c2 = m + n * (DIK / 2 - 0.02)
        doos(bms["afdek_zand"], (c2.x, c2.y, TOP + 0.07), (L + 0.9, DIK + 0.16, 0.14), hoek)       # afdekstenen
        for _ in range(int(L * 2.6)):                  # ingemetselde stenen (vijverkant)
            t = random.uniform(0.06, 0.94); z = random.uniform(0.0, TOP - 0.2); sx = random.uniform(0.2, 0.4); sz = random.uniform(0.14, 0.26)
            if boog and (abs(t - 0.5) * L < 1.15): continue
            if k in (1, 3) and abs(t - 0.5) * L < 0.4 and abs(z - 0.45) < 0.35: continue
            p = a + (b - a) * t - n * 0.025
            doos(bms["muursteen"], (p.x, p.y, z), (sx, 0.07, sz), hoek)
        if k in (1, 3):                                # roostervenster met blauw licht naast de boog
            p = m - n * 0.02
            doos(bms["boog"], (p.x, p.y, 0.45), (0.42, 0.04, 0.42), hoek)
            doos(bms["afdek_zand"], (p.x - n.x * 0.01, p.y - n.y * 0.01, 0.45), (0.56, 0.05, 0.56), hoek) if False else None
            for zz in (0.24, 0.66):
                doos(bms["afdek_zand"], (p.x - n.x * 0.02, p.y - n.y * 0.02, zz), (0.56, 0.08, 0.08), hoek)
            for zij in (-1, 1):
                q = p + d * zij * 0.25
                doos(bms["afdek_zand"], (q.x - n.x * 0.02, q.y - n.y * 0.02, 0.45), (0.08, 0.08, 0.5), hoek)
            q = p - n * 0.045
            doos(bms["blauwglas"], (q.x, q.y, 0.45), (0.32, 0.02, 0.32), hoek)
            for zij in (-0.08, 0.0, 0.08):             # tralies
                r2 = p + d * zij - n * 0.04
                stam(bms["paalmetaal"], Vector((r2.x, r2.y, 0.28)), Vector((r2.x, r2.y, 0.62)), 0.012, 0.012, 4, 0.0)
    for (a, b, d, n, L, hoek), eind in ((segs[0], 0), (segs[-1], 1)):   # pijlers met kap aan beide einden
        p = (a if eind == 0 else b) + n * DIK / 2 + (d * (-0.2) if eind == 0 else d * 0.2)
        doos(bms["zandsteen"], (p.x, p.y, (TOP + 0.35 - 0.45) / 2), (1.0, 1.0, TOP + 0.35 + 0.45), hoek)
        doos(bms["afdek_zand"], (p.x, p.y, TOP + 0.42), (1.16, 1.16, 0.14), hoek)
        doos(bms["afdek_zand"], (p.x, p.y, TOP + 0.55), (0.7, 0.7, 0.14), hoek)


def strand(bms):
    """zandstrand west van de haven (foto's eftepedia/Storm_effect_sindbad.jpg, videoframe 284 s, luchtfoto): vlak zand op
    pleinhoogte dat schuin het water in loopt (1,3 m tot 0,35 m onder water), grote ronde granieten keien, twee sierlijke
    meerpalen met koepelkap aan de waterkant"""
    Z = 0.30
    bm = bms["zand"]
    vs = [bm.verts.new((x, y, Z - (0.18 if (x, y) in STRAND_RAND else 0.0))) for x, y in STRAND]
    f = bm.faces.new(vs); bmesh.ops.triangulate(bm, faces=[f], ngon_method="EAR_CLIP")
    rand = [Vector((x, y, 0)) for x, y in STRAND_RAND]
    binnen = []
    for i, p in enumerate(rand):                       # punten 1,3 m het water in (naar binnen in de vijver)
        a = rand[max(0, i - 1)]; b = rand[min(len(rand) - 1, i + 1)]; d = (b - a).normalized(); n = Vector((-d.y, d.x, 0))
        if not in_poly((p + n * 0.5).x, (p + n * 0.5).y, VIJVER): n = -n
        binnen.append(p + n * 1.3)
    for i in range(len(rand) - 1):
        q = [Vector((rand[i].x, rand[i].y, Z - 0.18)), Vector((rand[i + 1].x, rand[i + 1].y, Z - 0.18)),
             Vector((binnen[i + 1].x, binnen[i + 1].y, -0.35)), Vector((binnen[i].x, binnen[i].y, -0.35))]
        bm.faces.new([bm.verts.new(v) for v in q])
    for f in bm.faces:
        f.normal_update()
        if f.normal.z < 0: f.normal_flip()
    random.seed(284)                                   # keien: rond, granietroze/grijs, half in het zand
    keien = [(-13.6, -6.2, 0.55), (-14.9, -7.0, 0.42), (-13.2, -7.9, 0.32), (-15.8, -8.4, 0.6), (-14.3, -9.0, 0.38), (-12.8, -9.3, 0.26),
             (-16.4, -10.0, 0.45), (-15.1, -10.6, 0.5), (-13.9, -10.3, 0.28), (-16.0, -6.4, 0.35), (-12.4, -6.6, 0.22), (-15.4, -11.6, 0.3),
             (-14.8, -5.6, 0.3), (-12.2, -8.4, 0.18)]
    for kx, ky, r in keien:
        c = Vector((kx, ky, Z + r * 0.15))
        v = bol(bms["kei"], c, r, 14)
        sx, sy = random.uniform(1.0, 1.35), random.uniform(0.85, 1.1); h = random.uniform(0.6, 0.8); rot = random.uniform(0, math.pi)
        fase = [random.uniform(0, 6.28) for _ in range(3)]
        for q in v:
            dd = q.co - c
            hk = math.atan2(dd.y, dd.x); el = math.asin(max(-1, min(1, dd.z / r)))
            bult = 1 + 0.10 * math.sin(2 * hk + fase[0]) + 0.07 * math.sin(3 * hk + fase[1]) * math.cos(el) + 0.06 * math.sin(2 * el + fase[2])
            dd = dd * bult
            dx, dy = dd.x * sx, dd.y * sy
            q.co = c + Vector((dx * math.cos(rot) - dy * math.sin(rot), dx * math.sin(rot) + dy * math.cos(rot), dd.z * h))
    for (mx, my) in ((-11.9, -7.3), (-13.4, -11.0)):  # sierlijke meerpalen (foto: houten paal met koepelkap)
        stam(bms["stam"], Vector((mx, my, -0.5)), Vector((mx, my, 1.7)), 0.13, 0.12, 8, 0.05)
        cil(bms["paalmetaal"], (mx, my, 1.55), 0.16, 0.1, 10)
        v = bol(bms["paalmetaal"], (mx, my, 1.7), 0.15, 10)
        cil(bms["paalmetaal"], (mx, my, 1.8), 0.05, 0.22, 8, 0.0)
        cil(bms["goud"], (mx, my, 1.2), 0.15, 0.08, 10)


def dhow_sindbad(bms):
    """Sindbads boot naar de foto's (ref/commons/Sinbad_in_Efteling.jpg, World_of_Sinbad.jpg, Sirocco_Efteling_World_of_Sinbad.jpg,
    eftepedia/Storm_effect_sindbad.jpg): 4,4 m lang, banaanvormige zeeg met hoge boeg en hogere achtersteven, ronde spanten;
    donkerrode planken, blauwe schubben onder aan de boeg, blauw sierpaneel met goud langs de achterzijde, gouden rand; achtersteven
    krult omhoog met een grote gouden veer; schuine mast met lange ra en creme latijnzeil met rood embleem (atlas gebied D);
    lading: gebonden balen, kruiken en een tonnetje op een houten dek. Sindbad zelf komt later als figuur."""
    x0, y0, rot = BOOT_SINDBAD
    M = Matrix.Translation((x0, y0, 0)) @ Matrix.Rotation(rot, 4, "Z")
    L, B = 2.2, 0.78
    def top(x): t = abs(x) / L; return 0.55 + (1.25 if x > 0 else 0.95) * t ** 2.4
    def bod(x): return -0.25 + 0.55 * (abs(x) / L) ** 2.2
    def w(x): return B * max(0.0, 1 - (abs(x) / L) ** 2.2) ** 0.55
    def p(x, f): return Vector((x, w(x) * math.sin(f), bod(x) + (top(x) - bod(x)) * (1 - math.cos(f))))
    NX, NF = 48, 20
    xs = [-L + 2 * L * k / NX for k in range(NX + 1)]
    xs[0] += 0.02; xs[-1] -= 0.02
    fs = [-math.pi / 2 + math.pi * k / NF for k in range(NF + 1)]
    uvbm = {}
    def vlak(rol, pts, uvs, richting=None, binnen=False):
        bm = uvbm.setdefault(rol, bmesh.new()); uvl = bm.loops.layers.uv.verify()
        f = bm.faces.new([bm.verts.new(M @ v) for v in pts])
        for lp, uv in zip(f.loops, uvs): lp[uvl].uv = uv
        f.normal_update()
        if richting is not None and f.normal.dot(richting) < 0: f.normal_flip()
    for a in range(NX):
        for b in range(NF):
            q = [p(xs[a], fs[b]), p(xs[a + 1], fs[b]), p(xs[a + 1], fs[b + 1]), p(xs[a], fs[b + 1])]
            c = sum(q, Vector()) / 4
            buiten = M.to_3x3() @ Vector((0, c.y, c.z - (bod(c.x) + 0.6 * (top(c.x) - bod(c.x)))))
            zt = top(c.x); xm = c.x
            if xm > 0.25 * L and c.z < zt - 0.22 - 0.15 * (xm / L):
                rol, uvs = "schubben", [(v.x / 0.55, v.z / 0.55) for v in q]
            elif -0.85 * L < xm < -0.1 * L and zt - 0.34 < c.z < zt - 0.06:
                rol = "sierpaneel"; uvs = [((v.x + 0.85 * L) / (0.75 * L), (v.z - (top(v.x) - 0.34)) / 0.28) for v in q]
            else:
                rol, uvs = "romp", [(v.x / 1.2, v.z / 0.9) for v in q]
            vlak(rol, q, uvs, buiten)
            qi = [v + (Vector((0, -v.y, 0.6 - v.z)).normalized() * 0.05) for v in q[::-1]]        # binnenkant
            vlak("romp", qi, [(v.x / 1.2, v.z / 0.9) for v in qi], -buiten)
    for a in range(NX):                               # boord (bovenkant van de wand) + gouden rand
        for zij in (-1, 1):
            f0, f1 = zij * math.pi / 2, zij * math.pi / 2
            u0, u1 = p(xs[a], f0), p(xs[a + 1], f0)
            i0 = u0 + Vector((0, -zij * 0.05, 0)); i1 = u1 + Vector((0, -zij * 0.05, 0))
            stam(bms["goud"], M @ (u0 + Vector((0, 0, 0.02))), M @ (u1 + Vector((0, 0, 0.02))), 0.035, 0.035, 6, 0.0)
    # dek
    zd = 0.22; dek = []
    for k in range(NX + 1):
        x = xs[k]
        if bod(x) < zd - 0.02:
            f = math.acos(max(-1, min(1, 1 - (zd - bod(x)) / (top(x) - bod(x)))))
            dek.append((x, w(x) * math.sin(f) - 0.04))
    for k in range(len(dek) - 1):
        (xa, wa), (xb, wb) = dek[k], dek[k + 1]
        q = [Vector((xa, -wa, zd)), Vector((xb, -wb, zd)), Vector((xb, wb, zd)), Vector((xa, wa, zd))]
        vlak("dhowdek", q, [(v.x / 1.0, v.y / 1.0) for v in q], M.to_3x3() @ Vector((0, 0, 1)))
    # boeg: punt die doorloopt; achtersteven krult omhoog met gouden veer
    bt = p(L - 0.02, 0); stam(bms["dhow"], M @ bt, M @ (bt + Vector((0.18, 0, 0.35))), 0.06, 0.03, 6, 0.0)
    st = p(-L + 0.02, 0); vorig = st
    for k in range(1, 9):
        t = k / 8; q = st + Vector((-0.25 * math.sin(t * 1.6), 0, 0.95 * t))
        stam(bms["dhow"], M @ vorig, M @ q, 0.07 - 0.03 * t, 0.07 - 0.03 * (t + 0.125), 6, 0.0); vorig = q
    vb = vorig                                        # veer: blad met nerf, licht gebogen, tweezijdig
    veer = [vb + Vector((0.12 * math.sin(math.pi * t) * (1 if z else -1) * 1.0 - 0.15 * t, 0, 1.6 * t)) for t in [k / 10 for k in range(11)] for z in (0, 1)]
    for k in range(10):
        a, b, c2, d2 = veer[2 * k], veer[2 * k + 2], veer[2 * k + 3], veer[2 * k + 1]
        for vs in ((a, b, c2, d2), (d2, c2, b, a)):
            bms["goud"].faces.new([bms["goud"].verts.new(M @ v) for v in vs])
    stam(bms["goud"], M @ vb, M @ (vb + Vector((-0.15, 0, 1.6))), 0.02, 0.008, 5, 0.0)
    # mast, ra, zeil
    mv = Vector((0.35, 0, zd)); mt = Vector((0.15, 0, 3.5))
    stam(bms["dhow"], M @ mv, M @ mt, 0.07, 0.05, 8, 0.0)
    ra0, ra1 = Vector((1.75, 0, 1.15)), Vector((-1.55, 0, 4.25))
    stam(bms["dhow"], M @ ra0, M @ ra1, 0.05, 0.035, 6, 0.0)
    stam(bms["touw"], M @ mt, M @ ra0.lerp(ra1, 0.55), 0.015, 0.015, 4, 0.0)
    schoot = Vector((-1.25, 0, 1.05))
    zeil = [ra0 + Vector((0, 0.06, 0)), ra1 + Vector((0, 0.06, 0)), schoot + Vector((0, 0.06, 0))]
    uvD = [(0.52, 1 - 1000 / 1024), (0.98, 1 - 340 / 1024), (0.98, 1 - 1000 / 1024)]
    uv_vlak("SI_om_dhow_zeil", "bordvlak", [([M @ v for v in zeil], uvD, M.to_3x3() @ Vector((0, -1, 0))),
                                            ([M @ (v + Vector((0, 0.01, 0))) for v in zeil], uvD, M.to_3x3() @ Vector((0, 1, 0)))])
    stam(bms["touw"], M @ schoot, M @ Vector((-1.6, 0, top(-1.6))), 0.012, 0.012, 4, 0.0)
    # lading: balen (gebonden), kruiken, tonnetje
    for (bx, by, bz, sx, sy, sz) in ((-0.55, 0.0, zd, 0.5, 0.42, 0.3), (-0.55, 0.0, zd + 0.3, 0.46, 0.4, 0.28), (-0.55, 0.0, zd + 0.58, 0.42, 0.36, 0.26),
                                     (-1.05, 0.05, zd, 0.4, 0.36, 0.28)):
        v = doos(bms["baal"], (bx, by, bz + sz / 2), (sx, sy, sz))
        bmesh.ops.transform(bms["baal"], matrix=M, verts=v)
        for t in (-0.25, 0.25):
            v = doos(bms["touw"], (bx + t * sx, by, bz + sz / 2), (0.03, sy + 0.02, sz + 0.02)); bmesh.ops.transform(bms["touw"], matrix=M, verts=v)
    for (kx, ky, h, r) in ((-0.05, 0.25, 0.6, 0.15), (0.05, -0.28, 0.45, 0.12), (-1.0, -0.3, 0.5, 0.13)):
        v = cil(bms["kruik"], (kx, ky, zd), r, h, 12)
        for q in v:
            t = (q.co.z - zd) / h; f = 0.55 + 0.6 * math.sin(math.pi * min(1.0, t * 1.2)) if t < 0.83 else 0.5
            q.co.x = kx + (q.co.x - kx) * f; q.co.y = ky + (q.co.y - ky) * f
        bmesh.ops.transform(bms["kruik"], matrix=M, verts=v)
    v = cil(bms["ton"], (0.75, 0.15, zd), 0.2, 0.42, 14); bmesh.ops.transform(bms["ton"], matrix=M, verts=v)
    for rol, bm in uvbm.items():
        o = obj(f"SI_om_dhow_{rol}", bm, rol); o["uv_klaar"] = 1


def haven(bms):
    """Sindbads zeilboot in de haven (dhow_sindbad), meerpalen, boeien (gele en blauwe stuiterballen)"""
    dhow_sindbad(bms)
    for (px, py) in ((-10.8, -7.0), (-5.5, -10.4), (3.5, -12.6), (11.8, -8.6)):     # meerpalen met touw (Meerpaal-pieck.jpg)
        stam(bms["stam"], Vector((px, py, -0.8)), Vector((px, py, 1.4)), 0.13, 0.11, 8, 0.12)
        cil(bms["touw"], (px, py, 0.9), 0.15, 0.18, 10)
    for (px, py, kl) in ((-5.0, -10.0, "boei_geel"), (-10.8, 3.2, "boei_blauw"), (-6.8, 10.6, "boei_geel"), (12.2, -3.0, "boei_blauw"),
                         (3.0, -11.8, "boei_blauw"), (-12.0, -2.5, "boei_geel")):
        bol(bms[kl], (px, py, 0.12), 0.38, 12)
        for k in range(4):                             # touwnet over de bal
            h = k * math.pi / 4
            pts = [Vector((px + 0.4 * math.cos(h) * math.sin(a), py + 0.4 * math.sin(h) * math.sin(a), 0.12 + 0.4 * math.cos(a))) for a in (0.2, 0.8, 1.4, 2.0)]
            for i in range(len(pts) - 1):
                stam(bms["touw"], pts[i], pts[i + 1], 0.015, 0.015, 4, 0.0)


BORD_OMTREK = [(0.12, -0.04), (0.28, -0.12), (0.42, -0.2), (0.6, -0.26), (2.15, -0.28), (2.4, -0.2), (2.52, -0.25), (2.72, -0.12),
               (3.05, 0.0), (2.74, 0.08), (2.58, 0.2), (2.44, 0.15), (2.22, 0.3), (0.62, 0.3), (0.45, 0.24), (0.3, 0.16), (0.12, 0.06)]
BORD_PAAL = (7.4, -16.9)                           # paal oost van de ingang; bord hangt naar links (west) boven de ingang
Z_GROND = 0.27                                     # pleinhoogte (Roblox Y ~1,0)


def uv_vlak(naam, rol, vlakken):
    """los object met eigen UV's: vlakken = [(punten, uvs, richting)], uvs in 0..1 (atlas SI_bord_kleur); de normaal wordt naar
    'richting' gedraaid (Roblox tekent achterkanten niet), daarna oor-triangulatie (hol bordprofiel); 05 laat de UV's staan"""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    for pts, uvs, richting in vlakken:
        f = bm.faces.new([bm.verts.new(v) for v in pts])
        for lp, uv in zip(f.loops, uvs): lp[uvl].uv = uv
        f.normal_update()
        if f.normal.dot(Vector(richting)) < 0: f.normal_flip()
    bmesh.ops.triangulate(bm, faces=bm.faces, ngon_method="EAR_CLIP")
    o = obj(naam, bm, rol); o["uv_klaar"] = 1
    return o


def lantaarn(bms, top, kap, lampen):
    """hangende Arabische lantaarn (videoframes): ophangring, koepel met spits, zeskantig glas, gouden banden, punt onder"""
    x, y, z = top
    cil(bms["goud"], (x, y, z - 0.06), 0.03, 0.06, 8)
    v = bol(bms[kap], (x, y, z - 0.17), 0.13, 10)
    for q in v:
        if q.co.z < z - 0.17: q.co.z = z - 0.17
    cil(bms[kap], (x, y, z - 0.08), 0.02, 0.1, 6, 0.0)
    cil(bms["goud"], (x, y, z - 0.21), 0.15, 0.04, 6)
    cil(bms["lantaarnglas"], (x, y, z - 0.52), 0.12, 0.31, 6, 0.135)
    for k in range(6):                             # stijlen
        h = 2 * math.pi * (k + 0.5) / 6
        stam(bms[kap], Vector((x + 0.125 * math.cos(h), y + 0.125 * math.sin(h), z - 0.52)),
             Vector((x + 0.14 * math.cos(h), y + 0.14 * math.sin(h), z - 0.21)), 0.012, 0.012, 4, 0.0)
    cil(bms["goud"], (x, y, z - 0.56), 0.14, 0.04, 6)
    cil(bms[kap], (x, y, z - 0.74), 0.0, 0.18, 6, 0.12)
    bol(bms["goud"], (x, y, z - 0.77), 0.03, 6)
    lampen.append([x, y, z - 0.37])


def ingangsbord(bms, lampen):
    """ingangsbord naar de video (xloCDJYf-Tw 12-16 s): donkerbruine metalen paal met sokkel, ringen en spits; pluimvormig bord
    met "Sirocco" en medaillon naar links boven de ingang; arm naar rechts met drie hangende lantaarns (groen, rood, groen);
    infobord met spitsboog op de paal. (Vazen en citroenmand weggehaald: Daan, stonden voor het pad.) Tekst en tekening zitten in textures/SI_bord_kleur.png (07t_bord.py)."""
    px, py = BORD_PAAL; g = Z_GROND
    m = "paalmetaal"
    cil(bms[m], (px, py, g), 0.24, 0.12, 12); cil(bms[m], (px, py, g + 0.12), 0.19, 0.7, 12)      # sokkel
    for zz in (g + 0.82, g + 1.1, g + 2.95, g + 4.85):                                               # ringen
        cil(bms[m], (px, py, zz), 0.11, 0.07, 12)
    cil(bms[m], (px, py, g + 0.8), 0.085, 4.9, 12, 0.07)                                             # paal
    bol(bms[m], (px, py, g + 5.75), 0.1, 10)                                                         # knop + spits
    cil(bms[m], (px, py, g + 5.8), 0.07, 0.3, 8, 0.0)
    cil(bms[m], (px, py, g + 5.0), 0.06, 0.06, 8)
    # arm met lantaarns (naar rechts/oost, iets naar achteren, licht omhoog)
    a0 = Vector((px, py, g + 5.15)); a1 = Vector((px + 1.55, py + 0.35, g + 5.45))
    stam(bms[m], a0, a1, 0.045, 0.04, 8, 0.0); bol(bms[m], a1, 0.07, 8)
    stam(bms[m], Vector((px, py, g + 4.7)), a0.lerp(a1, 0.35), 0.025, 0.025, 6, 0.0)               # schoor
    for t, val, kap in ((0.3, 0.55, "lamp_groen"), (0.6, 0.95, "lamp_rood"), (0.92, 0.35, "lamp_groen")):
        q = a0.lerp(a1, t)
        stam(bms["touw"], q, q - Vector((0, 0, val)), 0.012, 0.012, 4, 0.0)
        lantaarn(bms, q - Vector((0, 0, val)), kap, lampen)
    # pluimbord: voor- en achterkant met atlas (gebied A), rand rondom
    zc = g + 4.35; dik = 0.07
    def p3(u, z, y): return Vector((px - u, py + y, zc + z))
    def uvA(u, z, spiegel=False):
        x = (3.1 - u) / 3.1; x = 1 - x if spiegel else x
        return (x, 1 - (0.34 - z) / 0.66 * (320 / 1024))
    om = BORD_OMTREK
    voor = ([p3(u, z, -0.13 - dik / 2) for u, z in om], [uvA(u, z) for u, z in om])
    achter = ([p3(u, z, -0.13 + dik / 2) for u, z in om[::-1]], [uvA(u, z, True) for u, z in om[::-1]])
    uv_vlak("SI_om_bordvlak", "bordvlak", [(*voor, (0, -1, 0)), (*achter, (0, 1, 0))])
    for i in range(len(om)):                       # rand (goudbruin)
        (u0, z0), (u1, z1) = om[i], om[(i + 1) % len(om)]
        a, b = p3(u0, z0, -0.13 - dik / 2), p3(u1, z1, -0.13 - dik / 2)
        c, e = p3(u1, z1, -0.13 + dik / 2), p3(u0, z0, -0.13 + dik / 2)
        f = bms["bordrand"].faces.new([bms["bordrand"].verts.new(v) for v in (a, b, c, e)])
        f.normal_update(); mid = (a + c) / 2; uit = Vector((mid.x - (px - 1.5), 0, mid.z - zc))
        if f.normal.dot(uit) < 0: f.normal_flip()
    for zz in (zc - 0.12, zc + 0.12):              # beugels aan de paal
        stam(bms[m], Vector((px, py, zz)), Vector((px - 0.2, py - 0.13, zz)), 0.025, 0.025, 6, 0.0)
    # medaillon onder het bord (gebied B) met gouden krul
    mc = p3(1.45, -0.5, -0.13)
    cil_v = []
    R_M = 0.2; NM = 20
    ring = [(mc.x + R_M * math.cos(2 * math.pi * k / NM), mc.z + R_M * math.sin(2 * math.pi * k / NM)) for k in range(NM)]
    uvB = lambda k: (0.125 + 0.117 * math.cos(2 * math.pi * k / NM), 1 - (448 / 1024) + 0.117 * math.sin(2 * math.pi * k / NM))
    uvB2 = lambda k: (0.125 - 0.117 * math.cos(2 * math.pi * k / NM), 1 - (448 / 1024) + 0.117 * math.sin(2 * math.pi * k / NM))
    uv_vlak("SI_om_bordmedaillon", "bordvlak", [
        ([Vector((x, mc.y - 0.03, z)) for x, z in ring], [uvB2(k) for k in range(NM)], (0, -1, 0)),
        ([Vector((x, mc.y + 0.03, z)) for x, z in ring[::-1]], [uvB(k) for k in range(NM)][::-1], (0, 1, 0))])
    for k in range(NM):
        (x0, z0), (x1, z1) = ring[k], ring[(k + 1) % NM]
        f = bms["goud"].faces.new([bms["goud"].verts.new(v) for v in (Vector((x0, mc.y - 0.03, z0)), Vector((x0, mc.y + 0.03, z0)),
                                                                        Vector((x1, mc.y + 0.03, z1)), Vector((x1, mc.y - 0.03, z1)))])
        f.normal_update()
        if f.normal.dot(Vector(((x0 + x1) / 2 - mc.x, 0, (z0 + z1) / 2 - mc.z))) < 0: f.normal_flip()
    vorig = mc + Vector((0, 0, R_M))
    stam(bms["goud"], vorig, p3(1.45, -0.28, -0.13), 0.02, 0.02, 6, 0.0)
    vorig = mc - Vector((0, 0, R_M))
    for k in range(1, 9):                          # krul onder het medaillon
        t = k / 8; q = mc + Vector((0.12 * math.sin(t * 5.5), 0, -R_M - 0.18 * t + 0.05 * math.sin(t * 6)))
        stam(bms["goud"], vorig, q, 0.018, 0.012, 5, 0.0); vorig = q
    # infobord op de paal (gebied C), aan de zuidkant
    iy = py - 0.13; x0, x1, z0, z1 = px - 0.26, px + 0.26, g + 1.55, g + 2.55
    uvC = lambda x, z: (0.25 + (x - x0) / (x1 - x0) * 0.25, 1 - (320 + (z1 - z) / (z1 - z0) * 512) / 1024)
    vs = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    uv_vlak("SI_om_infobord", "bordvlak", [([Vector((x, iy - 0.002, z)) for x, z in vs], [uvC(x, z) for x, z in vs], (0, -1, 0))])
    doos(bms[m], (px, iy + 0.03, (z0 + z1) / 2), (0.56, 0.05, 1.04))


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    master = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=master)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    for o in bpy.data.objects:
        if o.name == "SI_blk_water": o.hide_render = True; o.hide_viewport = True
    rollen = ("stam", "bamboe", "net", "vlonder", "zeil_turkoois", "zeilrand", "lantaarn", "lantaarnglas", "bamboewand", "riet", "raam",
              "bestrating", "muur", "afdek", "steen", "touw", "boei_geel", "boei_blauw", "paalmetaal", "lamp_groen", "lamp_rood", "goud",
              "bordrand", "dhow", "baal", "kruik", "ton", "zand", "kei", "witrand", "zandsteen", "afdek_zand", "muursteen", "boog", "zandsteenvlak", "blauwglas")
    bms = {r: bmesh.new() for r in rollen}
    lampen = []
    links, rechts = strook(bms["vlonder"], WACHTRIJ, B_RIJ, Z_VLONDER)
    for p in WACHTRIJ[::2]:                            # palen onder de vlonder
        stam(bms["stam"], Vector((p[0], p[1], -0.8)), Vector((p[0], p[1], Z_VLONDER - 0.1)), 0.1, 0.1, 6, 0.1)
    leuning(bms, links[:ZEIL_VANAF + 1], Z_VLONDER); leuning(bms, rechts[:ZEIL_VANAF + 1], Z_VLONDER)
    leuning(bms, links[ZEIL_VANAF:], Z_VLONDER, True); leuning(bms, rechts[ZEIL_VANAF:], Z_VLONDER, True)   # ook langs het instapstuk
    zeilkap(bms, WACHTRIJ[ZEIL_VANAF:-2], Z_VLONDER, lampen)          # stopt voor de afslag naar het dek: geen paal in het pad
    dekhek(bms)
    hutje(bms); brug(bms); vijverrand(bms); havenmuur(bms); strand(bms); haven(bms); ingangsbord(bms, lampen)
    # waterplaat in de vorm van de vijver (dun, bovenkant omhoog)
    bmw = bmesh.new()
    vs = [bmw.verts.new((x, y, -0.04)) for x, y in VIJVER]
    bmw.faces.new(vs)
    bmesh.ops.triangulate(bmw, faces=bmw.faces)
    for f in bmw.faces:
        if f.normal.z < 0: f.normal_flip()
    obj("SI_om_water", bmw, "water")
    for rol, bm in bms.items():
        if not bm.verts: bm.free(); continue
        if rol not in ("net", "zeil_turkoois", "zeilrand", "vlonder", "bestrating", "riet", "bordrand", "goud", "zand", "boog", "zandsteenvlak"):
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        obj(f"SI_om_{rol}", bm, rol)
    info = {"vijver": VIJVER, "wachtrij": WACHTRIJ, "zeil_vanaf": ZEIL_VANAF, "uitgang": UITGANG, "hut": HUT, "lampen": lampen,
            "z_vlonder": Z_VLONDER, "breedte": B_RIJ}
    json.dump(info, open(os.path.join(D, "exports", "omgeving_info.json"), "w"), indent=1)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=master)
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER)
    print("[07_omgeving] klaar:", len([o for o in bpy.data.objects if o.get("owner") == OWNER]), "objecten,", tris, "driehoeken,", len(lampen), "lampen")


main()
