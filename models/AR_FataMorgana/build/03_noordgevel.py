"""03_noordgevel: stap 2 — de gevel aan het meer links en rechts van de grote toren (Fata2013.jpg, ref/ahn).
AHN (boven maaiveld NAP 8,7): westvleugel voorkant y -296,5 .. -299,5 (x -72,5 .. -43,5), oostvleugel y -292 .. -295,5
(x -36,5 .. -8), muren 8 m (dak NAP 16,7); witte koepel (-48,5; -301) tot 11,3 m; westtorentje (-70; -299,5) tot 11,3 m;
grijze zeskantige koepel (-26; -298) tot 12,8 m; gouden koepel op hoger blok (-15,5; -298) tot 13,1 m.
Foto: kleine getrapte kantelen op de muren, kroonlijst, losse spitsboogramen, deurtje, erker op consoles, galerij met
groen pannen afdak in de onderste verdieping links van de toren, gouden spitsen op de koepels.
Modelstelsel = 02_toren: oorsprong park (-40; -295) op het maaiveld. Rollen als de toren + koepel_wit, koepel_grijs, pannen.
Gebruik: blender --background --python build/03_noordgevel.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(D, "build", "02_toren.py")).read().rsplit("\nmain()", 1)[0]
T = {"__file__": os.path.join(D, "build", "02_toren.py")}; exec(compile(src, "02_toren.py", "exec"), T)
OWNER = "phase:03_noordgevel"
T["KLEUR"].update({"stucvlak": (0.86, 0.78, 0.66), "tegel": (0.62, 0.4, 0.3), "koepel_wit": (0.94, 0.93, 0.9), "koepel_grijs": (0.8, 0.8, 0.82), "pannen": (0.16, 0.42, 0.32),
                   "kade": (0.95, 0.93, 0.88), "dak": (0.22, 0.22, 0.23), "lampmetaal": (0.32, 0.16, 0.12), "lampglas": (1.0, 0.92, 0.75),
                   "cipres": (0.12, 0.22, 0.12), "hout": (0.32, 0.2, 0.12)})
T["UVS"].update({"stucvlak": 9.0, "tegel": 1.0, "koepel_wit": 2.0, "koepel_grijs": 2.0, "pannen": 1.0, "kade": 9.0, "dak": 4.0, "lampmetaal": 1.0, "lampglas": 1.0,
                 "cipres": 0.8, "hout": 1.0})
for r in T["KLEUR"]: T["G"][r] = bmesh.new()
quad, doos, strip, spitsboog, vul, raam, nis, lathe, bol, Vlak = (T[k] for k in ("quad", "doos", "strip", "spitsboog", "vul", "raam", "nis", "lathe", "bol", "Vlak"))
O = (-40.0, -295.0)
H = 8.0
DIEP = 6.0


def L(x, y): return Vector((x - O[0], y - O[1], 0))


def prisma(rol, onder, z0, z1):
    """verticaal prisma met grondvlak 'onder' (lijst van Vector, tegen de klok in)"""
    a = [p + Vector((0, 0, z0)) for p in onder]; b = [p + Vector((0, 0, z1)) for p in onder]
    quad(rol, b); quad(rol, a[::-1])
    for i in range(len(onder)):
        j = (i + 1) % len(onder); quad(rol, [a[i], a[j], b[j], b[i]])


def kantelen_rij(vl, lengte, z, w=0.5, h=0.62, dik=0.3, tussen=0.32):
    n = max(1, int((lengte + tussen) / (w + tussen))); st = (lengte - n * w) / max(1, n - 1)
    for k in range(n):
        uc = w / 2 + k * (w + st)
        for j, f in enumerate((1.0, 0.66, 0.33)):
            hw = w * f / 2
            prisma("stuc", [vl.p(uc - hw, 0, 0), vl.p(uc + hw, 0, 0), vl.p(uc + hw, 0, -dik), vl.p(uc - hw, 0, -dik)][::-1] if False else
                   [vl.p(uc - hw, 0, -dik), vl.p(uc + hw, 0, -dik), vl.p(uc + hw, 0, 0), vl.p(uc - hw, 0, 0)], z + h * j / 3, z + h * (j + 1) / 3)


def muur(punten, hoogte=H, diep=DIEP, kantel=True, kroon=True, uitsparing=None):
    """gevelmuur langs een polylijn (parkcoordinaten, van west naar oost; voorkant = noord); geeft de gevelvlakken.
    uitsparing = {segment: (u0, u1, h, d)}: onderste h m tussen u0 en u1 d m naar binnen (galerij)"""
    vlakken = []
    for i, ((ax, ay), (bx, by)) in enumerate(zip(punten, punten[1:])):
        a, b = L(ax, ay), L(bx, by); u = (b - a).normalized(); n = Vector((-u.y, u.x, 0))   # links van west->oost = noord
        if uitsparing and i in uitsparing:
            u0, u1, hh, dd = uitsparing[i]; lb = (b - a).length
            for s0, s1 in ((0, u0), (u1, lb)):
                if s1 - s0 > 0.01: prisma("stuc", [a + u * s0 - n * diep, a + u * s1 - n * diep, a + u * s1, a + u * s0], 0.0, hoogte)
            prisma("stuc", [a + u * u0 - n * diep, a + u * u1 - n * diep, a + u * u1, a + u * u0], hh, hoogte)
            prisma("stuc", [a + u * u0 - n * diep, a + u * u1 - n * diep, a + u * u1 - n * dd, a + u * u0 - n * dd], 0.0, hh)
        else:
            prisma("stuc", [a - n * diep, b - n * diep, b, a], 0.0, hoogte)
        vl = Vlak(a, u, n); lengte = (b - a).length; vlakken.append((vl, lengte))
        if kroon:
            strip("lijst", vl, [(0, hoogte - 0.7), (lengte, hoogte - 0.7)], 0.28, 0.16)
            strip("lijst", vl, [(0, 0.3), (lengte, 0.3)], 0.6, 0.08)
        if kantel: kantelen_rij(vl, lengte, hoogte)
        gat = [(uitsparing[i][0] - 0.2, uitsparing[i][1] + 0.2, -1, uitsparing[i][2] + 0.9)] if uitsparing and i in uitsparing else []
        T["verwering"](vl, 0.0, lengte, 0.0, hoogte - 0.75, int(ax * 7 + ay * 13) & 0xffff, gat)
    return vlakken


def koepel(rol, c, z0, r, hoogte, ui=0.12, spits=True, seg=36):
    """koepel met lichte uivorm op z0 (straal r, hoogte), gouden spits"""
    prof = []
    for k in range(13):
        t = k / 12; a = t * math.pi / 2
        rr = r * (math.cos(a) * (1 + ui * math.sin(2 * a) * 1.3)) if k < 12 else 0.0
        prof.append((max(0.0, rr), hoogte * math.sin(a) ** (0.9 + 0.6 * t)))
    lathe(rol, prof, z0, seg, (c.x, c.y))
    if spits:
        top = z0 + hoogte
        lathe("goud", [(0.09, 0.0), (0.04, 0.1), (0.04, 1.1), (0.0, 1.3)], top - 0.04, 10, (c.x, c.y))
        for dz, rr in ((0.25, 0.13), (0.6, 0.09)): T["bol"]("goud", top + dz, rr) if False else bol_op(c, top + dz, rr)


def bol_op(c, z, r):
    lathe("goud", [(r * math.sin(math.pi * k / 8), -r * math.cos(math.pi * k / 8)) for k in range(9)], z, 14, (c.x, c.y))


def trommel(rol, c, z0, z1, r, zijden=6, ramen=True):
    hk = [c + Vector((r * math.cos(2 * math.pi * k / zijden + math.pi / zijden), r * math.sin(2 * math.pi * k / zijden + math.pi / zijden), 0)) for k in range(zijden)]
    prisma(rol, hk, z0, z1)
    if ramen:
        for k in range(zijden):
            a, b = hk[k], hk[(k + 1) % zijden]; u = (b - a).normalized(); n = Vector((u.y, -u.x, 0))
            if n.dot((a + b) / 2 - c) < 0: n = -n
            vl = Vlak(a, u, n); lw = (b - a).length
            raam(vl, lw / 2, min(0.55, lw * 0.35), z0 + 0.35, z1 - 0.65)
    lathe("lijst", [(r * 1.0, 0.0), (r * 1.08, 0.0), (r * 1.08, 0.16), (r * 1.0, 0.16)], z1 - 0.08, zijden * 4, (c.x, c.y))


def blokje(c, b, z0, z1, kantel=True):
    hb = b / 2
    hk = [c + Vector((sx, sy, 0)) for sx, sy in ((-hb, -hb), (hb, -hb), (hb, hb), (-hb, hb))]
    prisma("stuc", hk, z0, z1)
    vls = []
    for k in range(4):
        a, bb = hk[k], hk[(k + 1) % 4]; u = (bb - a).normalized(); n = Vector((u.y, -u.x, 0))
        vl = Vlak(a, u, n); vls.append(vl)
        strip("lijst", vl, [(0, z1 - 0.45), (b, z1 - 0.45)], 0.22, 0.14)
        if kantel: kantelen_rij(vl, b, z1, 0.42, 0.5, 0.25, 0.25)
        T["verwering"](vl, 0.1, b - 0.1, z0 + 0.1, z1 - 0.5, int(c.x * 31 + c.y * 17 + k) & 0xffff)
    return vls


def erker(vl, u, z, w=1.6, h=1.5, d=0.8):
    """houten/stucco erker op consoles (Fata2013: op de westmuur en naast de toren)"""
    hk = [vl.p(u - w / 2, z, 0), vl.p(u + w / 2, z, 0), vl.p(u + w / 2, z, d), vl.p(u - w / 2, z, d)]
    prisma("lijst", [Vector((p.x, p.y, 0)) for p in hk], z, z + h)
    for k in range(3):
        f = 1 - k * 0.28
        prisma("lijst", [Vector((p.x, p.y, 0)) for p in [vl.p(u - w / 2 * f, 0, 0), vl.p(u + w / 2 * f, 0, 0), vl.p(u + w / 2 * f, 0, d * f), vl.p(u - w / 2 * f, 0, d * f)]],
               z - 0.18 * (k + 1), z - 0.18 * k)
    prisma("lijst", [Vector((p.x, p.y, 0)) for p in [vl.p(u - w / 2 - 0.1, 0, -0.01), vl.p(u + w / 2 + 0.1, 0, -0.01), vl.p(u + w / 2 + 0.1, 0, d + 0.1), vl.p(u - w / 2 - 0.1, 0, d + 0.1)]],
           z + h, z + h + 0.15)
    v2 = Vlak(vl.p(u - w / 2, 0, d + 0.001), vl.U, vl.N)
    raam(v2, 0.45, 0.42, z + 0.3, z + 0.95); raam(v2, w - 0.45, 0.42, z + 0.3, z + 0.95)


def galerij(vl, u0, u1, h=3.4, diep=1.6, n=5):
    """bogengalerij in de onderste verdieping (Fata2013, links van de toren): ronde zuilen met voet en kapiteel, een echte
    bogenwand (rondbogen eruit gesneden, archivolt), erachter een ruimte met tegelvloer, plafond en achterwand met deur en
    ramen, daarboven een groen pannendak met dikte op houten schoren (Daan 18 nov: de platte versie "ziet er niet uit")"""
    w = (u1 - u0) / n; vs = 2.25; dik = 0.35; ow = w - 0.34; r = ow / 2
    # bogenwand: per vak stroken van de boogrand tot de bovenkant
    for k in range(n):
        uc = u0 + (k + 0.5) * w; ul, ur = u0 + k * w, u0 + (k + 1) * w
        us = [ul + (ur - ul) * j / 24 for j in range(25)]
        def onder(u):
            d = abs(u - uc)
            return vs + math.sqrt(max(0.0, r * r - d * d)) if d < r else vs
        for ua, ub in zip(us, us[1:]):
            ba, bb = onder(ua), onder(ub)
            quad("stucvlak", [vl.p(ua, ba, 0), vl.p(ub, bb, 0), vl.p(ub, h, 0), vl.p(ua, h, 0)][::-1])
            quad("stucvlak", [vl.p(ua, ba, -dik), vl.p(ua, h, -dik), vl.p(ub, h, -dik), vl.p(ub, bb, -dik)][::-1])
            quad("stucvlak", [vl.p(ua, ba, 0), vl.p(ua, ba, -dik), vl.p(ub, bb, -dik), vl.p(ub, bb, 0)][::-1])
        boog = [(uc + r * math.cos(math.pi * j / 16), vs + r * math.sin(math.pi * j / 16)) for j in range(17)]
        strip("lijst", vl, boog, 0.14, 0.07)
    strip("lijst", vl, [(u0 - 0.1, h - 0.05), (u1 + 0.1, h - 0.05)], 0.22, 0.1)
    # zuilen
    for k in range(n + 1):
        p = vl.p(u0 + k * w, 0, -dik / 2)
        lathe("lijst", [(0.21, 0.0), (0.21, 0.12), (0.16, 0.2), (0.12, 0.28), (0.11, vs - 0.42), (0.14, vs - 0.34), (0.2, vs - 0.18),
                        (0.22, vs - 0.06), (0.22, vs), (0.0, vs)], 0.0, 12, (p.x, p.y))
    # ruimte erachter: tegelvloer, plafond, achterwand (licht stuc) met deur en ramen
    prisma("tegel", [Vector((q.x, q.y, 0)) for q in (vl.p(u0, 0, -dik), vl.p(u1, 0, -dik), vl.p(u1, 0, -diep), vl.p(u0, 0, -diep))], -0.25, 0.12)   # 12 cm boven het terrein (geen z-fighting)
    quad("stucvlak", [vl.p(u0, h - 0.02, -dik), vl.p(u0, h - 0.02, -diep), vl.p(u1, h - 0.02, -diep), vl.p(u1, h - 0.02, -dik)][::-1])
    va = Vlak(vl.p(0, 0, -diep + 0.01), vl.U, vl.N)
    deur = spitsboog((u0 + u1) / 2, 1.1, 0.0, 1.8, 8)
    vul("deur", va, deur, 0.09); strip("lijst", va, deur, 0.16, 0.1)
    for uu in (u0 + (u1 - u0) * 0.2, u0 + (u1 - u0) * 0.8): raam(va, uu, 0.55, 1.0, 2.0)
    # pannendak: schuin van de muur naar buiten, met dikte, op houten schoren
    t = 0.14; uit = 1.15
    a0, a1 = vl.p(u0 - 0.35, h + 0.95, 0.0), vl.p(u1 + 0.35, h + 0.95, 0.0)
    b0, b1 = vl.p(u0 - 0.35, h + 0.42, uit), vl.p(u1 + 0.35, h + 0.42, uit)
    dz = Vector((0, 0, t))
    quad("pannen", [a0 + dz, a1 + dz, b1 + dz, b0 + dz][::-1][::-1]); quad("pannen", [b0, b1, a1, a0])
    quad("pannen", [b0, b0 + dz, b1 + dz, b1][::-1]); quad("pannen", [a0, b0, b0 + dz, a0 + dz]); quad("pannen", [b1, a1, a1 + dz, b1 + dz])
    for k in range(0, n + 1):
        uu = u0 + k * w
        for (pa, pb) in ((vl.p(uu, h + 0.05, 0.0), vl.p(uu, h + 0.45, uit - 0.2)),):
            dd = (pb - pa); nn = dd.cross(vl.U).normalized() * 0.05; ss = vl.U * 0.05
            prisma("hout", [Vector((q.x, q.y, 0)) for q in (pa - ss, pa + ss, pa + ss, pa - ss)], 0, 0) if False else None
            for e in ((ss, nn), (nn, -ss), (-ss, -nn), (-nn, ss)):
                quad("hout", [pa + e[0], pb + e[0], pb + e[1], pa + e[1]])


def romp():
    """het hoofdvolume achter de gevels met plat dak (AHN: dak NAP 16,7 over x -73..-6, y -293..-339): toren, west- en
    oostvleugel horen bij één gebouw (Daan 18 nov: "het zit niet aan elkaar")"""
    # 2 m achter de gevellijn (gevelmuren zijn 6 m diep), zodat de galerij open blijft
    omtrek = [(-72.5, -299.0), (-43.5, -299.0), (-43.5, -297.0), (-36.5, -297.0),
              (-36.5, -294.5), (-30.0, -294.0), (-27.0, -296.0), (-21.0, -296.5), (-12.0, -297.5), (-8.0, -297.5), (-6.5, -315.0),
              (-2.3, -315.0), (-2.3, -321.3), (-15.7, -321.3), (-15.7, -339.0), (-73.0, -339.0)]   # AHN: hal 8,2 m tot x -2,5 en x -16
    pts = [L(x, y) for x, y in omtrek][::-1]                   # tegen de klok in
    prisma("stuc", pts, 0.0, H - 0.3)                         # kern onder het dak (geen dubbele vlakken)
    quad("dak", [p + Vector((0, 0, H + 0.08)) for p in pts])   # 8 cm boven de muurbovenkanten: geen z-fighting


def kade():
    """witte kademuur met pijlers en bolle bekroningen langs het water (Fata2013.jpg); waterlijn = terrein (plaats_noordgevel)"""
    lijn = [(-74.0, -292.8), (-46.5, -292.8), (-46.5, -288.8), (-38.0, -288.8), (-38.0, -286.7), (-4.0, -286.7)]   # looppad voor de toren (Daan: "het pad moet wel geconnect")
    for (ax, ay), (bx, by) in zip(lijn, lijn[1:]):
        a, b = L(ax, ay), L(bx, by); u = (b - a).normalized(); n = Vector((-u.y, u.x, 0)); lengte = (b - a).length
        prisma("kade", [a - n * 0.18, b - n * 0.18, b + n * 0.18, a + n * 0.18], -0.4, 1.0)
        prisma("kade", [a - n * 0.24 - u * 0.0, b - n * 0.24, b + n * 0.24, a + n * 0.24], 1.0, 1.1)
        k = int(lengte / 3.6)
        for i in range(k + 1):
            c = a + u * (lengte * i / max(1, k))
            prisma("kade", [c + Vector((sx, sy, 0)) * 0.27 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], -0.4, 1.45)
            prisma("kade", [c + Vector((sx, sy, 0)) * 0.33 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 1.45, 1.55)
            lathe("kade", [(0.12, 0.0), (0.16, 0.08), (0.2, 0.2), (0.18, 0.32), (0.08, 0.44), (0.03, 0.55), (0.0, 0.62)], 1.55, 12, (c.x, c.y))


def lantaarnpaal(x, y):
    """sierlantaarnpaal met glazen bollen (Fata2013.jpg, bij de galerij): voet, kannelure-zuil, drie armen met bollen"""
    c = L(x, y)
    lathe("lampmetaal", [(0.32, 0.0), (0.32, 0.25), (0.22, 0.35), (0.18, 0.9), (0.24, 1.0), (0.1, 1.15), (0.08, 3.4), (0.14, 3.5),
                         (0.14, 3.6), (0.06, 3.7), (0.05, 4.3), (0.0, 4.35)], 0.0, 12, (c.x, c.y))
    for k, (dx, dy, z) in enumerate(((0, 0, 4.55), (0.55, 0, 3.95), (-0.55, 0, 3.95))):
        p = c + Vector((dx, dy, 0))
        if k: lathe("lampmetaal", [(0.03, 0.0), (0.03, 0.05)], 3.6, 6, (p.x, p.y))
        if k:
            a, b = c + Vector((0, 0, 3.65)), p + Vector((0, 0, 3.75))
            d = (b - a); lengte = d.length; u = d.normalized(); nn = u.cross(Vector((0, 0, 1))).normalized() * 0.03
            prisma("lampmetaal", [a - nn, b - nn, b + nn, a + nn], 3.62, 3.68)
        lathe("lampglas", [(r * 0.24, z0) for r, z0 in ((0.0, -0.24), (0.7, -0.2), (1.0, 0.0), (0.7, 0.2), (0.0, 0.24))], z, 12, (p.x, p.y))
        lathe("lampmetaal", [(0.07, 0.0), (0.1, 0.06), (0.0, 0.14)], z + 0.22, 8, (p.x, p.y))


def cipres(x, y, h, seed=0):
    """Italiaanse cipres (Fata2013.jpg, voor de westmuur): kort stammetje, kruin uit veel onregelmatige bolletjes; breed onderin
    (max ~ een kwart van de hoogte), spits naar boven, rafelig silhouet (Daan 18 nov: de gladde spoel "ziet er niet uit")"""
    import random as _r
    r = _r.Random(seed); c = L(x, y)
    lathe("hout", [(0.09, 0.0), (0.07, 0.75)], 0.0, 8, (c.x, c.y))
    def breedte(t):                                        # t = 0 onderkant kruin .. 1 top
        return 0.55 * (min(1.0, t / 0.22) ** 0.6) * (1 - t) ** 0.85 + 0.07
    z0 = 0.45; hk = h - z0
    # kern: dichte spoel onder de kluiten, zodat er nergens gaten tussen zitten
    lathe("cipres", [(0.0, 0.0)] + [(breedte(t) * 0.62, t * hk * 0.97) for t in [k / 16 for k in range(1, 16)]] + [(0.0, hk)], z0 + 0.05, 12, (c.x, c.y))
    n = int(hk / 0.24)
    for k in range(n):
        t = (k + r.uniform(0, 0.6)) / n; z = z0 + t * hk
        for j in range(3 if t < 0.8 else 2):
            a = r.uniform(0, 2 * math.pi); off = breedte(t) * r.uniform(0.15, 0.55)
            rr = breedte(t) * r.uniform(0.55, 0.85)
            klont(c + Vector((math.cos(a) * off, math.sin(a) * off, z)), rr, rr * r.uniform(1.2, 1.7), r)


def klont(c, rx, rz, r, ringen=7, seg=12):
    """onregelmatig bolletje (bladkluit)"""
    ns = [[1 + r.uniform(-0.22, 0.22) for _ in range(seg)] for _ in range(ringen + 1)]
    pts = []
    for i in range(ringen + 1):
        b = math.pi * (i / ringen - 0.5)
        pts.append([c + Vector((math.cos(2 * math.pi * k / seg) * math.cos(b) * rx * ns[i][k], math.sin(2 * math.pi * k / seg) * math.cos(b) * rx * ns[i][k],
                                math.sin(b) * rz * (ns[i][k] if 0 < i < ringen else 1))) for k in range(seg)])
    for i in range(ringen):
        for k in range(seg):
            k1 = (k + 1) % seg
            quad("cipres", [pts[i][k], pts[i][k1], pts[i + 1][k1], pts[i + 1][k]])


def luifel(vl, u, z, w=1.0):
    """houten luifeltje boven een raam (Fata2013.jpg: bruine kapjes)"""
    a0, a1 = vl.p(u - w / 2, z + 0.35, 0.0), vl.p(u + w / 2, z + 0.35, 0.0)
    b0, b1 = vl.p(u - w / 2, z, 0.55), vl.p(u + w / 2, z, 0.55)
    prisma("hout", [Vector((p.x, p.y, 0)) for p in (a0, a1, b1, b0)], z - 0.04, z)
    quad("hout", [a0, a1, b1, b0]); quad("hout", [b0, b1, a1, a0])
    for p, q in ((a0, b0), (a1, b1)):                       # driehoekige zijwangen, dubbelzijdig
        r = p - Vector((0, 0, 0.35)); quad("hout", [p, q, r]); quad("hout", [r, q, p])


def muurlamp(vl, u, z):
    p = vl.p(u, z, 0.25)
    prisma("lampmetaal", [Vector((q.x, q.y, 0)) for q in (vl.p(u - 0.04, 0, 0), vl.p(u + 0.04, 0, 0), vl.p(u + 0.04, 0, 0.3), vl.p(u - 0.04, 0, 0.3))], z + 0.28, z + 0.34)
    lathe("lampglas", [(0.0, 0.0), (0.11, 0.05), (0.11, 0.3), (0.0, 0.36)], z - 0.1, 6, (p.x, p.y))
    lathe("lampmetaal", [(0.14, 0.0), (0.06, 0.12), (0.0, 0.2)], z + 0.26, 6, (p.x, p.y))


def rooster(vl, u, v0, w, h, n=0.06):
    """houten roosterwerk (mashrabiya) voor een raam"""
    for k in range(1, int(w / 0.12)):
        uu = u - w / 2 + k * 0.12
        prisma("hout", [Vector((q.x, q.y, 0)) for q in (vl.p(uu - 0.015, 0, n), vl.p(uu + 0.015, 0, n), vl.p(uu + 0.015, 0, n + 0.03), vl.p(uu - 0.015, 0, n + 0.03))], v0, v0 + h)
    for k in range(1, int(h / 0.12)):
        vv = v0 + k * 0.12
        prisma("hout", [Vector((q.x, q.y, 0)) for q in (vl.p(u - w / 2, 0, n), vl.p(u + w / 2, 0, n), vl.p(u + w / 2, 0, n + 0.03), vl.p(u - w / 2, 0, n + 0.03))], vv - 0.015, vv + 0.015)


def bouw():
    romp(); kade()
    # lantaarnpalen bij de galerij weggehaald (Daan 18 nov: "haal de lantaarnpalen weg")
    for k, (x, y, h) in enumerate(((-47.0, -296.2, 5.8), (-57.5, -296.1, 6.4), (-63.0, -296.2, 5.2))): cipres(x, y, h, k)
    # westvleugel (AHN-voorlijn), oostvleugel
    # recht (Daan 18 nov: "hoort dit schuin te gaan" — nee: de AHN-drempel pakte kantelen/dak, luchtfoto en Fata2013 tonen een rechte muur)
    west = muur([(-72.5, -297.0), (-66.0, -297.0), (-60.0, -297.0), (-51.0, -297.0), (-43.5, -297.0)])
    L0 = (L(-30.0, -292.0) - L(-36.5, -292.5)).length
    oost = muur([(-36.5, -292.5), (-30.0, -292.0), (-27.0, -294.0), (-21.0, -294.5), (-12.0, -295.5), (-8.0, -295.5)],
                uitsparing={0: (0.9, L0 - 0.2, 3.4, 1.9)})
    # westvleugel: ramen, deurtje, erker
    vl, l = west[1]; raam(vl, l * 0.5, 0.6, 4.3, 5.6)
    vl, l = west[2]; raam(vl, 2.5, 0.6, 4.3, 5.6); deur = spitsboog(6.2, 1.2, 0.0, 1.7, 8); vul("deur", vl, deur, 0.09); strip("lijst", vl, deur, 0.2, 0.14)
    vl, l = west[3]; erker(vl, l * 0.45, 5.0); rooster(vl, l * 0.45, 5.25, 1.4, 0.95, 0.83)
    luifel(vl, l * 0.85, 3.2, 1.1); raam(vl, l * 0.85, 0.6, 1.6, 2.6)
    vl, l = west[2]; muurlamp(vl, 4.9, 1.9); muurlamp(vl, 7.5, 1.9)
    vl, l = west[0]; raam(vl, l * 0.4, 0.55, 4.6, 5.8)
    # westtorentje: blokje op de hoek met turquoise koepel (tot 11,3 m)
    c = L(-70.0, -299.5); vls = blokje(c, 3.0, H, H + 1.6, kantel=False)
    for v in vls: raam(v, 1.5, 0.7, H + 0.25, H + 1.0)
    T["G"]["stuc"]; koepel("koepel", c, H + 1.6, 1.35, 1.75, 0.18)
    # witte koepel achter de westmuur (tot 11,3 m)
    c = L(-48.5, -301.0); trommel("stuc", c, H, H + 0.9, 1.9, 8, ramen=False); koepel("koepel_wit", c, H + 0.9, 1.95, 2.35, 0.1)
    # oostvleugel: galerij links van de toren, erker, ramen
    vl, l = oost[0]; galerij(vl, 0.9, l - 0.2, 3.4, 1.9, 5)
    raam(vl, l * 0.38, 0.55, 5.2, 6.5); raam(vl, l * 0.62, 0.55, 5.2, 6.5)
    vl, l = oost[2]; raam(vl, l * 0.3, 0.55, 5.2, 6.4); raam(vl, l * 0.7, 0.55, 5.2, 6.4)
    vl, l = oost[1]; erker(vl, l * 0.5, 4.8, 1.3, 1.4, 0.7); rooster(vl, l * 0.5, 5.05, 1.1, 0.85, 0.73)
    vl, l = oost[3]; raam(vl, l * 0.35, 0.6, 4.6, 5.9); raam(vl, l * 0.7, 0.6, 4.6, 5.9)
    # grijze zeskantige koepel (tot 12,8 m)
    c = L(-26.0, -298.0); trommel("stuc", c, H, H + 1.7, 2.3, 6); koepel("koepel_grijs", c, H + 1.7, 2.3, 3.1, 0.08)
    # gouden koepel op een hoger blok (tot 13,1 m)
    c = L(-15.5, -298.5); vls = blokje(c, 4.2, H, H + 2.3)
    for v in vls: raam(v, 1.3, 0.5, H + 0.6, H + 1.6); raam(v, 2.9, 0.5, H + 0.6, H + 1.6)
    trommel("stuc", c, H + 2.3, H + 2.75, 1.55, 8, ramen=False); koepel("goud", c, H + 2.75, 1.6, 2.35, 0.2)


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in T["G"].items():
        if not bm.faces: continue
        ov = rol in T["OVERLAY"]
        if not ov and rol not in ("raam", "deur", "dak", "stucvlak"): bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()                                   # vlakken zonder recalc hebben anders normaal (0,0,0) -> verkeerde UV-as
        uvl = bm.loops.layers.uv.verify(); s = T["UVS"][rol]
        for f in ([] if ov else bm.faces):
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.y / s, co.z / s) if ax == 0 else (co.x / s, co.z / s) if ax == 1 else (co.x / s, co.y / s)
        me = bpy.data.meshes.new("FM_gevel_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_gevel_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "noordgevel"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 30
    # zoals Fata2013.jpg: vanaf het meer, iets oostelijk
    for naam, pos, doel in (("gevel_meer", L(-22, -250) + Vector((0, 0, 2.5)), L(-42, -298) + Vector((0, 0, 7))),
                            ("gevel_west", L(-75, -270) + Vector((0, 0, 4)), L(-45, -298) + Vector((0, 0, 6)))):
        cam.location = pos; cam.rotation_euler = (doel - pos).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(uit, naam + ".png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[03_noordgevel] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "03_noordgevel"); os.makedirs(uit, exist_ok=True); render(uit)


main()
