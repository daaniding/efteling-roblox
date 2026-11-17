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
PLEINKANT = lambda x, y: (x < -11.0 and -13 < y < 7.0) or (x < -9.5 and y < -12.5)     # rand langs het plein (lichte band, witte muur)
# wachtrij: begin bij het plein (zuidoost, naast Archipel), noord langs de oostkant, zeilkap vanaf ZEIL_VANAF, bocht van 180
# graden en meebuigend met de draaischijf (r ~10.3) tot het opstappunt aan het dek
WACHTRIJ = [(5.8, -15.8), (8.0, -13.9), (11.0, -11.9), (13.8, -9.6), (15.6, -6.5), (15.9, -2.0), (15.9, 3.0), (15.75, 6.0)]
for a in range(0, 181, 20):                        # haarspeldbocht om het plantvak (luchtfoto: midden (12.0; 8.0), r 3.75)
    WACHTRIJ.append((12.0 + 3.75 * math.cos(math.radians(a)), 8.0 + 3.75 * math.sin(math.radians(a))))
for a in range(30, -61, -8):                       # meebuigend met de draaischijf naar het opstappunt (luchtfoto r ~10.2)
    WACHTRIJ.append((10.25 * math.cos(math.radians(a)), 10.25 * math.sin(math.radians(a))))
WACHTRIJ.append((7.0 * math.cos(math.radians(-62)), 7.0 * math.sin(math.radians(-62))))          # het dek op (opening in het gaashek)
ZEIL_VANAF = 7                                     # index in WACHTRIJ waar de zeilkap begint
B_RIJ = 2.0                                        # breedte vlonder (Roblox: looppaden ~1,5x echt)
UITGANG_X = -2.0                                   # uitgangsbrug recht naar het zuiden (luchtfoto: muurtjes op x -3,5 en -0,5)
UITGANG = [(UITGANG_X, -6.6), (UITGANG_X, -17.3)]
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
    links, rechts = strook(bms["bestrating"], [a, b], 2.4, Z_PLAT + 0.02, 0.6)
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


def haven(bms):
    """Sindbads zeilboot (dhow, latijnzeil) in de haven, meerpalen, boeien (gele en blauwe stuiterballen)"""
    x, y, rot = BOOT_SINDBAD
    M = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(rot, 4, "Z")
    bm = bmesh.new()
    NT, L, B = 24, 2.6, 0.95
    ringen = []
    for k, (zz, sch) in enumerate(((-0.25, 0.55), (0.15, 0.9), (0.6, 1.0))):
        ring = []
        for i in range(NT):
            t = 2 * math.pi * i / NT; cx, cy = math.cos(t), math.sin(t)
            punt = abs(cx) ** 0.6 * (1 if cx >= 0 else -1)
            ring.append(Vector((L * punt * sch, B * cy * sch * (1 - 0.35 * abs(cx) ** 4), zz + 0.35 * abs(cx) ** 3 * (k / 2))))
        ringen.append(ring)
    for k in range(2):
        for i in range(NT):
            j = (i + 1) % NT
            bm.faces.new([bm.verts.new(v) for v in (ringen[k][i], ringen[k][j], ringen[k + 1][j], ringen[k + 1][i])])
    bm.faces.new([bm.verts.new(v + Vector((0, 0, -0.25))) for v in ringen[1]])     # dek
    bm.transform(M); obj("SI_om_dhow_romp", bm, "dhow")
    bm2 = bmesh.new()
    stam(bm2, Vector((0.2, 0, 0.3)), Vector((0.2, 0, 4.2)), 0.07, 0.05, 8, 0.0)
    ra, rb = Vector((-2.4, 0, 1.4)), Vector((1.9, 0, 4.6))                        # ra van het latijnzeil
    stam(bm2, ra, rb, 0.05, 0.04, 6, 0.0)
    bm2.transform(M); obj("SI_om_dhow_mast", bm2, "mast")
    bm3 = bmesh.new()
    zeil = [ra + Vector((0.1, 0, 0)), rb - Vector((0.1, 0, 0.05)), Vector((0.4, 0, 0.95))]
    for vs in (zeil, zeil[::-1]):
        bm3.faces.new([bm3.verts.new(v) for v in vs])
    bm3.transform(M); obj("SI_om_dhow_zeil", bm3, "zeil_dhow")
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


def ingangsbord(bms):
    """houten paal met bord SIROCCO bij het begin van de wachtrij (video f_007); tekst komt in Roblox (SurfaceGui)"""
    x, y = WACHTRIJ[0][0] - 1.6, WACHTRIJ[0][1] + 0.3
    stam(bms["stam"], Vector((x, y, -0.3)), Vector((x, y, 3.4)), 0.11, 0.09, 8, 0.1)
    doos(bms["bord"], (x + 0.55, y, 2.9), (1.1, 0.08, 0.45), math.radians(35))


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    master = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=master)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    for o in bpy.data.objects:
        if o.name == "SI_blk_water": o.hide_render = True; o.hide_viewport = True
    rollen = ("stam", "bamboe", "net", "vlonder", "zeil_turkoois", "zeilrand", "lantaarn", "lantaarnglas", "bamboewand", "riet", "raam",
              "bestrating", "muur", "afdek", "steen", "touw", "boei_geel", "boei_blauw", "bord")
    bms = {r: bmesh.new() for r in rollen}
    lampen = []
    links, rechts = strook(bms["vlonder"], WACHTRIJ, B_RIJ, Z_VLONDER)
    for p in WACHTRIJ[::2]:                            # palen onder de vlonder
        stam(bms["stam"], Vector((p[0], p[1], -0.8)), Vector((p[0], p[1], Z_VLONDER - 0.1)), 0.1, 0.1, 6, 0.1)
    leuning(bms, links[:ZEIL_VANAF + 1], Z_VLONDER); leuning(bms, rechts[:ZEIL_VANAF + 1], Z_VLONDER)
    leuning(bms, links[ZEIL_VANAF:-1], Z_VLONDER, True); leuning(bms, rechts[ZEIL_VANAF:-1], Z_VLONDER, True)
    zeilkap(bms, WACHTRIJ[ZEIL_VANAF:-1], Z_VLONDER, lampen)
    hutje(bms); brug(bms); vijverrand(bms); haven(bms); ingangsbord(bms)
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
        if rol not in ("net", "zeil_turkoois", "zeilrand", "vlonder", "bestrating", "riet"):
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
