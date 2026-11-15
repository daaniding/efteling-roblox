"""03_kabouterdorp Het Kabouterdorp (1952-1980, Anton Pieck / Ton van de Ven / Henny Knoet): paddenstoelendorp langs het hoofdpad (OSM 1074483532).
- Paddenstoelenparcours (NW): twee vliegenzwammen (OSM 55444984, 55445041) met lage doorgangen, bruggetje over het beekje (767397169), derde zwam = morielje,
  tafeltje met vier krukjes, waslijntje, laag poortje met hartjesbord; vijvertje (767397170).
- Kabouterboom (OSM-boom "De Gouden Stemvork"): holle boom met Pieck-gezicht, wortels met kijkruitjes, deurtje.
- Loze vissertje (oostvijver 763240399): overhangende paddenstoel boven het water met bootje; langwerpig morieljehuis (55444985) met poortje en trap.
- Grote vliegenzwam van de schrijvende kabouter (763240405, steel r 3 m, hoed tot de ring 763240404): bovenverdieping via houten bordes, luikenraam,
  houten trap omlaag naar het pleintje aan het beekje.
- Huisje met waterrad: pannendak + klokgevel, rechts een morieljehoed, waterrad in het beekje, bruggetje, hekje, stro-afdakje van het wasvrouwtje.
- Grote Kabouterhuis (55444983, doorloop): organische gestucte muren, links morieljekegel, rechts uitwaaierend vliegenzwamdak, balkonnetje, klokkentorentje,
  loden schoorsteentje, twee poortjes (hoefijzer), traliewerk; vijver (763240398).
- Paden (licht grind), bosgrond. Kabouters/animatie later.
Frame: oorsprong = zwaartepunt 55423167 = studs (458.25, -63.78); model = OSM-assen (x oost, y noord); Roblox F = (0, 0, 1) (= model -Y, zuid).
Gebruik: Blender -b -P 03_kabouterdorp.py -- --master KD_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.82, 0.78, 0.68, 1), 0.9), "steel": ((0.9, 0.87, 0.78, 1), 0.85), "rood": ((0.72, 0.1, 0.06, 1), 0.45), "wit": ((0.95, 0.94, 0.9, 1), 0.6),
        "zwam": ((0.45, 0.3, 0.18, 1), 0.85), "plaat": ((0.85, 0.78, 0.62, 1), 0.9), "hout": ((0.32, 0.22, 0.14, 1), 0.85), "riet": ((0.42, 0.33, 0.24, 1), 0.95),
        "pannen": ((0.6, 0.27, 0.18, 1), 0.7), "schors": ((0.3, 0.25, 0.2, 1), 0.95), "donker": ((0.05, 0.04, 0.03, 1), 1.0), "groen": ((0.18, 0.36, 0.2, 1), 0.6),
        "ijzer": ((0.06, 0.06, 0.06, 1), 0.45), "lood": ((0.35, 0.36, 0.38, 1), 0.5), "water": ((0.12, 0.18, 0.15, 1), 0.1), "modder": ((0.14, 0.1, 0.07, 1), 1.0),
        "grind": ((0.86, 0.83, 0.76, 1), 0.95), "glas": ((0.5, 0.6, 0.45, 1), 0.1), "papier": ((0.92, 0.86, 0.7, 1), 0.9), "doek": ((0.85, 0.8, 0.7, 1), 0.9),
        "breuksteen": ((0.5, 0.48, 0.44, 1), 0.9)}
rr = random.Random(1952)
HOOFDPAD = [(-8.11, 36.56), (-5.82, 31.33), (-4.82, 29.28), (-3.59, 19.72), (-3.25, 14.84), (-2.22, 6.19), (-2.4, 3.97), (4.66, -5.64), (5.73, -9.14), (8.73, -29.62)]
ZIJPADEN = [[(-3.59, 19.72), (-8.84, 19.77), (-16.23, 21.93), (-18.77, 22.24), (-21.42, 22.7), (-22.33, 22.8)],
            [(-3.25, 14.84), (3.01, 16.22), (10.68, 17.37)], [(-2.22, 6.19), (3.66, 6.92), (6.86, 7.58)], [(-0.32, 29.72), (3.96, 29.5)],
            [(-2.4, 3.97), (-5.31, -0.87), (-6.52, -3.35), (-6.67, -4.37), (-5.55, -8.41), (-1.67, -9.36), (2.08, -9.52), (5.73, -9.14)],
            [(3.66, 6.92), (7.15, 1.93), (6.39, -2.97), (4.66, -5.64)]]
VIJVER_NW = [(-6.9, 28.13), (-5.98, 23.11), (-10.56, 23.26), (-18.06, 24.59), (-14.73, 26.98)]
VIJVER_O = [(13.45, 12.25), (13.2, 14.38), (10.34, 13.06), (7.94, 10.57), (7.33, 8.89), (8.56, 4.93), (11.57, 3.42), (15.25, 3.87), (17.75, 6.21), (18.56, 8.49), (16.59, 9.26)]
VIJVER_ZW = [(-8.83, -4.93), (-10.27, -3.46), (-6.83, -1.44), (-4.15, -1.56), (-1.46, -3.36), (0.66, -5.98), (1.19, -8.92), (1.14, -12.16), (-2.15, -13.36), (-5.29, -13.0), (-5.33, -10.18), (-4.46, -10.37), (-3.88, -10.02), (-2.88, -10.01), (-2.32, -10.16), (-1.89, -10.01), (-1.67, -9.36), (-1.72, -8.07), (-2.14, -7.67), (-4.04, -4.62), (-6.52, -3.35), (-7.18, -3.01)]
GKH = [(-8.83, -4.93), (-9.31, -7.38), (-8.98, -8.58), (-7.51, -10.06), (-5.43, -9.93), (-3.88, -10.02), (-1.89, -10.01), (-1.67, -9.36), (-1.72, -8.07), (-2.14, -7.67), (-4.04, -4.62), (-6.52, -3.35), (-7.18, -3.01)]
MORIELJEHUIS = [(13.45, 12.25), (11.8, 10.87), (10.43, 9.17), (11.62, 7.97), (12.23, 8.34), (13.02, 7.37), (13.02, 6.63), (13.84, 6.01), (14.74, 6.04), (15.26, 6.58), (15.28, 7.12), (15.02, 7.47), (16.59, 9.26)]


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    def plaat(poly, z, dz, part, mat, gaten=()):
        lus = [poly] + list(gaten); flat = [p for l in lus for p in l]
        tris = tessellate_polygon([[Vector((x, y, 0)) for x, y in l] for l in lus])
        bm = bmesh.new(); Tt = [bm.verts.new((x, y, z)) for x, y in flat]; Bb = [bm.verts.new((x, y, z - dz)) for x, y in flat]
        for t in tris:
            f = bm.faces.new([Tt[i] for i in t]); f.normal_update()
            if f.normal.z < 0: f.normal_flip()
            g = bm.faces.new([Bb[i] for i in t]); g.normal_update()
            if g.normal.z > 0: g.normal_flip()
        o = 0
        for l in lus:
            for i in range(len(l)):
                j = (i + 1) % len(l)
                try: bm.faces.new((Tt[o + i], Bb[o + i], Bb[o + j], Tt[o + j]))
                except ValueError: pass
            o += len(l)
        put(part, mat, bm)
    def strook(pts, w, z, part, mat):
        P = [Vector(p) for p in pts]; L, R = [], []
        for i, p in enumerate(P):
            a = P[max(0, i - 1)]; b = P[min(len(P) - 1, i + 1)]; t = (b - a).normalized(); nn = Vector((-t.y, t.x)) * w / 2
            L.append(p + nn); R.append(p - nn)
        plaat([(v.x, v.y) for v in L] + [(v.x, v.y) for v in reversed(R)], z, 0.1, part, mat)
    def vijver(poly, part):
        plaat(poly, 0.0, 0.05, part, "water"); plaat(poly, -0.45, 0.05, part, "modder")
        n = len(poly)
        for i in range(n):
            A, B = Vector(poly[i]), Vector(poly[(i + 1) % n]); L_ = (B - A).length; k = max(1, int(L_ / 0.45))
            for j in range(k):
                p = A.lerp(B, (j + 0.5) / k); sc = rr.uniform(0.15, 0.26)
                put(part, "breuksteen", bz(-sc, sc, -sc * 0.8, sc * 0.8, -0.15, sc * 0.7, 0.05), TR(p.x, p.y, 0, rr.uniform(0, 90)))
    def hoed(c, r, h, part, stippen=True, rood=True):   # vliegenzwamhoed (koepel) met plaatjes en witte stippen
        prof = [(0.0, h), (r * 0.35, h * 0.97), (r * 0.65, h * 0.85), (r * 0.88, h * 0.6), (r * 1.0, h * 0.28), (r * 0.98, h * 0.08), (r * 0.9, 0.0), (r * 0.5, h * 0.1), (0.0, h * 0.15)]
        put(part, "rood" if rood else "zwam", blathe(prof[:7], 24), Matrix.Translation(c))
        put(part, "plaat", blathe([(r * 0.9, 0.0), (r * 0.5, h * 0.12), (0.0, h * 0.18)], 24), Matrix.Translation(c))
        if stippen:
            for k in range(int(r * 9)):
                t = rr.uniform(0.05, 0.85); a = rr.uniform(0, math.tau)
                rad = r * math.sin(t * math.pi * 0.5) * 0.98; z = h * (1 - 0.72 * t ** 1.6)
                s = rr.uniform(0.07, 0.16) * (r / 2)
                put(part, "wit", ell((c.x + rad * math.cos(a), c.y + rad * math.sin(a), c.z + z), (s, s, s * 0.5), 6, 4))
    def morielje(c, r, h, part, rek=1.0):           # morieljehoed: spits, bruin, honingraat-ribbels
        prof = [(0.0, h), (r * 0.3, h * 0.92), (r * 0.65, h * 0.7), (r * 0.92, h * 0.4), (r * 1.0, h * 0.15), (r * 0.95, 0.0)]
        M_ = Matrix.Translation(c) @ Matrix.Scale(rek, 4, Vector((1, 0, 0)))
        put(part, "zwam", blathe(prof, 18), M_)
        for k in range(1, 6):
            t = k / 6; zr = h * (1 - t * 0.85); rad = r * (0.3 + 0.7 * math.sin(t * math.pi * 0.5)) * 1.02
            put(part, "donker", btube([(rad * math.cos(a), rad * math.sin(a), zr) for a in [i * math.tau / 18 for i in range(19)]], 0.035, 4), M_)
        for k in range(12):
            a = k * math.tau / 12; pts = []
            for t in (0.05, 0.3, 0.55, 0.8, 1.0):
                rad = r * (0.3 + 0.7 * math.sin(t * math.pi * 0.5)) * 1.02; pts.append((rad * math.cos(a), rad * math.sin(a), h * (1 - t * 0.85)))
            put(part, "donker", btube(pts, 0.03, 4), M_)
    def raampje(c, ang, w, h, part, luik=True):     # raampje met luikjes (hartjes), loodrecht op richting ang
        M_ = Matrix.Translation(c) @ Matrix.Rotation(ang, 4, "Z")
        put(part, "donker", bz(-0.04, 0.02, -w / 2, w / 2, 0, h), M_); put(part, "hout", bz(0.0, 0.06, -w / 2 - 0.05, w / 2 + 0.05, -0.06, 0.0), M_)
        if luik:
            for s in (-1, 1):
                put(part, "groen", bz(0.02, 0.07, s * w / 2, s * (w / 2 + w * 0.5), 0, h), M_)
                put(part, "donker", ell((0.08, s * (w / 2 + w * 0.25), h * 0.6), (0.01, 0.04, 0.04), 4, 3), M_)
    def deurtje(c, ang, w, h, part, open_=False):
        M_ = Matrix.Translation(c) @ Matrix.Rotation(ang, 4, "Z")
        put(part, "donker" if open_ else "hout", bz(-0.05, 0.05, -w / 2, w / 2, 0, h - w / 2), M_)
        put(part, "donker" if open_ else "hout", ell((0, 0, h - w / 2), (0.05, w / 2, w / 2), 10, 6), M_)
    # ---------- paden + bosgrond-randen ----------
    strook(HOOFDPAD, 3.2, 0.06, "paden", "grind")
    for zp in ZIJPADEN: strook(zp, 1.6, 0.065, "paden", "grind")
    # ---------- 1. paddenstoelenparcours (NW) ----------
    for (cx, cy, rs, hs, rh, hh) in ((-17.55, 21.5, 1.4, 2.3, 2.3, 1.3), (-22.4, 22.6, 1.0, 1.9, 1.7, 1.0)):
        c = Vector((cx, cy, 0))
        put("parcours", "steel", blathe([(rs * 1.12, 0), (rs * 1.05, hs * 0.3), (rs, hs * 0.75), (rs * 0.95, hs), (0, hs)], 20), Matrix.Translation(c))
        hoed(c + Vector((0, 0, hs - 0.1)), rh, hh, "parcours")
        for a in (math.radians(20), math.radians(200)):                                        # lage doorgangen (kinderen)
            deurtje(c + Vector((rs * math.cos(a), rs * math.sin(a), 0)), a, 0.75, 1.35, "parcours", True)
        raampje(c + Vector((rs * math.cos(1.6), rs * math.sin(1.6), 1.2)), 1.6, 0.4, 0.45, "parcours")
        put("parcours", "ijzer", bz(cx - 0.12, cx + 0.12, cy + 0.6, cy + 0.84, hs + hh * 0.6, hs + hh + 0.6)) if rs > 1.2 else None
        put("parcours", "ijzer", btube([(cx + rs * 0.9, cy - rs * 0.3, 1.9), (cx + rs * 1.2, cy - rs * 0.35, 1.9)], 0.02, 4)); put("parcours", "lood", ell((cx + rs * 1.25, cy - rs * 0.35, 1.75), (0.09, 0.09, 0.12), 6, 4))   # lantaarntje
        coll_box(cx, cy, hs / 2, rs * 1.8, rs * 1.8, hs)
    c3 = Vector((-13.8, 19.3, 0))                                                             # derde zwam: morielje
    put("parcours", "steel", blathe([(0.9, 0), (0.8, 0.9), (0.75, 1.6), (0, 1.6)], 16), Matrix.Translation(c3))
    morielje(c3 + Vector((0, 0, 1.5)), 1.15, 2.6, "parcours")
    deurtje(c3 + Vector((0.0, -0.85, 0)), -math.pi / 2, 0.7, 1.3, "parcours", True); deurtje(c3 + Vector((0.0, 0.85, 0)), math.pi / 2, 0.7, 1.3, "parcours", True)
    coll_box(c3.x - 0.65, c3.y, 0.8, 0.3, 1.4, 1.6); coll_box(c3.x + 0.65, c3.y, 0.8, 0.3, 1.4, 1.6)
    put("parcours", "hout", bz(-0.6, 0.6, -0.5, 0.5, 0.0, 0.06), TR(-20.1, 23.8, 0.45, 75))                        # bruggetje over het beekje
    for s in (-1, 1): put("parcours", "hout", btube([(-0.6, s * 0.5, 0.5), (0.6, s * 0.5, 0.5)], 0.03, 4), TR(-20.1, 23.8, 0.45, 75))
    strook([(-23.44, 25.05), (-20.34, 24.32), (-18.06, 24.59)], 0.9, 0.02, "parcours", "water")
    MT = Matrix.Translation((-11.0, 18.0, 0))                                                    # tafeltje met krukjes
    put("parcours", "hout", blathe([(0.5, 0.55), (0.5, 0.6), (0.0, 0.6)], 12), MT); put("parcours", "hout", btube([(0, 0, 0), (0, 0, 0.55)], 0.06, 6), MT)
    for k in range(4):
        a = k * math.tau / 4 + 0.4; put("parcours", "hout", blathe([(0.16, 0.3), (0.16, 0.34), (0.0, 0.34)], 8), MT @ Matrix.Translation((0.85 * math.cos(a), 0.85 * math.sin(a), 0)))
        put("parcours", "hout", btube([(0.85 * math.cos(a), 0.85 * math.sin(a), 0), (0.85 * math.cos(a), 0.85 * math.sin(a), 0.3)], 0.04, 5), MT)
    for p in ((-12.6, 20.9), (-9.6, 21.6)): put("parcours", "hout", btube([(p[0], p[1], -0.1), (p[0], p[1], 1.5)], 0.04, 5))
    put("parcours", "touw" if False else "hout", btube([(-12.6, 20.9, 1.45), (-11.1, 21.25, 1.35), (-9.6, 21.6, 1.45)], 0.008, 4))
    for k, t in enumerate((0.25, 0.5, 0.72)):
        p = Vector((-12.6, 20.9, 1.4)).lerp(Vector((-9.6, 21.6, 1.4)), t); put("parcours", "doek", bz(-0.12, 0.12, -0.01, 0.01, -0.3, 0.0), Matrix.Translation(p) @ Matrix.Rotation(0.23, 4, "Z"))
    put("parcours", "hout", bz(-0.6, 0.6, -0.03, 0.03, 0.0, 0.7), TR(-6.8, 20.2, 0, 90))                          # laag poortje + hartjesbord
    put("parcours", "rood", boutline([(0, 0.0), (0.22, 0.18), (0.18, 0.32), (0.0, 0.24), (-0.18, 0.32), (-0.22, 0.18)], -0.02, 0.03), TR(-6.8, 20.2, 0.75, 90))
    vijver(VIJVER_NW, "vijvers")
    # ---------- 2. kabouterboom (holle boom met gezicht) ----------
    KB = Vector((-6.64, 16.95, 0)); kb = bmesh.new()
    def addk(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); kb.from_mesh(me_); bpy.data.meshes.remove(me_)
    addk(blathe([(1.55, -0.1), (1.35, 0.6), (1.1, 1.6), (0.95, 3.0), (0.85, 4.4), (0.0, 4.4)], 16))
    for k in range(7):                                                                          # wortels
        a = k * math.tau / 7 + 0.3; addk(btube([(1.0 * math.cos(a), 1.0 * math.sin(a), 0.7), (2.0 * math.cos(a + 0.15), 2.0 * math.sin(a + 0.15), 0.15), (2.6 * math.cos(a + 0.2), 2.6 * math.sin(a + 0.2), -0.05)], 0.32, 7))
    for (a, l, z) in ((0.4, 2.8, 4.0), (2.4, 2.6, 4.2), (4.2, 2.4, 3.9)):                       # dikke takken
        addk(btube([(0.4 * math.cos(a), 0.4 * math.sin(a), z), (l * 0.5 * math.cos(a), l * 0.5 * math.sin(a), z + 1.0), (l * math.cos(a + 0.2), l * math.sin(a + 0.2), z + 1.8)], 0.38, 8))
    put("boom", "schors", organisch(kb, 0.08, 3, 0.5, 0.12, 1.2, 0.3), Matrix.Translation(KB))
    gz = Vector((0.9, -0.95, 0)).normalized()                                                   # gezicht naar het pad (zuidoost)
    def G(u, v, z): return KB + gz * (1.05 + u) + Vector((-gz.y, gz.x, 0)) * v + Vector((0, 0, z))
    for s in (-1, 1):
        put("boom", "donker", ell(G(0.0, s * 0.32, 2.75), (0.08, 0.16, 0.12), 8, 6)); put("boom", "schors", ell(G(0.06, s * 0.32, 2.95), (0.12, 0.22, 0.08), 8, 6))
    put("boom", "schors", ell(G(0.16, 0, 2.45), (0.16, 0.12, 0.28), 8, 6)); put("boom", "donker", ell(G(0.02, 0, 1.95), (0.08, 0.32, 0.1), 8, 6))
    for s in (-1, 1): put("boom", "glas", ell(G(0.05, s * 0.55, 0.35), (0.05, 0.14, 0.1), 8, 4))                  # kijkruitjes tussen de wortels
    deurtje(KB + gz.cross(Vector((0, 0, 1))) * -1.15 + Vector((0, 0, 0)), math.atan2(-gz.x, gz.y), 0.55, 1.0, "boom")
    coll_box(KB.x, KB.y, 2.0, 2.4, 2.4, 4.0)
    # ---------- 3. loze vissertje: overhangende paddenstoel boven de oostvijver + bootje ----------
    vijver(VIJVER_O, "vijvers")
    ov = bmesh.new(); pts = [Vector((9.0, 4.6, -0.1)), Vector((9.5, 5.2, 1.4)), Vector((10.4, 5.8, 2.5)), Vector((11.2, 6.1, 3.0))]
    for a, b in zip(pts, pts[1:]): me_ = bpy.data.meshes.new("_t"); bb = btube([a, b], 0.6, 12); bb.to_mesh(me_); bb.free(); ov.from_mesh(me_); bpy.data.meshes.remove(me_)
    put("vissertje", "steel", organisch(ov, 0.06, 2, 0.5, 0.03, 1.0, 0.4))
    hoed(Vector((11.4, 6.2, 2.9)), 2.1, 0.9, "vissertje")
    MBt = TR(11.6, 5.6, 0.02, 25)
    put("vissertje", "hout", blathe([(0.0, 0.0), (0.35, 0.05), (0.45, 0.3), (0.0, 0.3)], 12), MBt @ Matrix.Scale(2.2, 4, Vector((1, 0, 0))))
    put("vissertje", "hout", btube([(11.6, 5.6, 0.6), (13.4, 4.4, 1.9)], 0.015, 4)); put("vissertje", "zwam", ell((13.5, 4.3, 0.06), (0.06, 0.06, 0.08), 6, 4))   # hengel + dennenappel-dobber
    put("vissertje", "hout", bz(-0.55, 0.55, -0.02, 0.02, 0.0, 0.7), TR(8.6, 3.6, 0, 20)); put("vissertje", "papier", bz(-0.3, 0.3, -0.03, -0.02, 0.35, 0.65), TR(8.6, 3.6, 0, 20))
    coll_box(9.3, 4.9, 0.8, 1.2, 1.2, 1.6)
    # morieljehuis (OSM 55444985): gestucte voet met lange morieljehoed, poortje + trapje
    cxm = sum(p[0] for p in MORIELJEHUIS) / len(MORIELJEHUIS); cym = sum(p[1] for p in MORIELJEHUIS) / len(MORIELJEHUIS)
    mw = bmesh.new(); Lp = [Vector(p) for p in MORIELJEHUIS]
    lo = [mw.verts.new((p.x, p.y, -0.1)) for p in Lp]; hi = [mw.verts.new((p.x + (cxm - p.x) * 0.08, p.y + (cym - p.y) * 0.08, 1.9)) for p in Lp]
    for i in range(len(Lp)): mw.faces.new((lo[i], lo[(i + 1) % len(Lp)], hi[(i + 1) % len(Lp)], hi[i]))
    for t in tessellate_polygon([[Vector((v.co.x, v.co.y, 0)) for v in hi]]): mw.faces.new([hi[i] for i in t]); mw.faces.new([lo[i] for i in reversed(t)])
    bmesh.ops.recalc_face_normals(mw, faces=mw.faces); put("morieljehuis", "stuc", organisch(mw, 0.06, 2, 0.4, 0.04, 1.0, 0.35))
    mang = math.atan2(12.25 - 6.6, 13.45 - 14.3)
    morielje(Vector((cxm, cym, 1.75)), 2.0, 3.6, "morieljehuis", rek=1.0)
    deurtje(Vector((10.9, 8.6, 0.0)), math.radians(225), 0.8, 1.55, "morieljehuis")
    raampje(Vector((15.6, 8.6, 1.0)), math.radians(-30), 0.45, 0.5, "morieljehuis")
    for k in range(5): put("morieljehuis", "hout", bz(-0.5, 0.5, -0.15, 0.15, 0.0, 0.18 + k * 0.2), TR(10.4 - 0.3 * k, 8.1 - 0.3 * k, 0, 45))
    coll_box(cxm, cym, 1.0, 4.0, 4.0, 2.0)
    # ---------- 4. grote vliegenzwam (schrijvende kabouter): steel r 3, bordes, luikenraam, trap omlaag ----------
    GV = Vector((9.27, 24.84, 0))
    put("grotezwam", "steel", blathe([(3.25, -0.1), (3.1, 1.5), (3.0, 3.4), (2.9, 4.4), (0, 4.4)], 28), Matrix.Translation(GV))
    hoed(GV + Vector((0, 0, 4.25)), 4.75, 2.3, "grotezwam")
    raampje(GV + Vector((3.0, 0.4, 2.3)), 0.12, 0.8, 0.85, "grotezwam")                                       # luikenraam (foto-plek)
    raampje(GV + Vector((-2.2, -2.05, 0.9)), math.radians(223), 0.45, 0.5, "grotezwam")
    for a in (math.radians(140), math.radians(300)): raampje(GV + Vector((3.05 * math.cos(a), 3.05 * math.sin(a), 3.2)), a, 0.35, 0.4, "grotezwam")
    deurtje(GV + Vector((-1.95, 2.25, 2.0)), math.radians(131), 0.85, 1.8, "grotezwam", True)                 # bovendeur aan het bordes
    deurtje(GV + Vector((0.71, -2.85, 2.0)), math.radians(-76), 0.8, 1.7, "grotezwam", True)                  # uitgang naar de trap
    put("grotezwam", "hout", bz(-1.2, 1.2, -0.9, 0.9, 1.9, 2.0), TR(6.72, 27.79, 0, 140))                     # bordes + trap op
    for k in range(6): put("grotezwam", "hout", bz(-0.6, 0.6, -0.17, 0.17, 0.0, 0.32 * (k + 1)), TR(6.72 - 0.4 * (k + 1) * 0.84, 27.79 + 0.4 * (k + 1) * 0.54, 0, 58))
    for k in range(10):                                                                                     # houten trap omlaag (zuid)
        t = (k + 0.5) / 10; p = Vector((9.98, 22.03)).lerp(Vector((10.68, 17.6)), t)
        put("grotezwam", "hout", bz(-0.65, 0.65, -0.24, 0.24, 0.0, 2.0 * (1 - t) + 0.05), TR(p.x, p.y, 0, -9))
    for s in (-1, 1): put("grotezwam", "hout", btube([(9.98 + s * 0.68, 22.03, 2.9), (10.68 + s * 0.68, 17.6, 0.9)], 0.04, 5))
    coll_box(GV.x, GV.y, 2.2, 5.6, 5.6, 4.4)
    # ---------- 5. huisje met waterrad aan het beekje ----------
    strook([(12.6, 23.4), (13.4, 19.5), (13.9, 16.4), (13.4, 14.2)], 1.0, 0.03, "beek", "water")
    HW = Matrix.Translation((15.6, 18.2, 0)) @ Matrix.Rotation(math.radians(-8), 4, "Z")
    put("waterrad", "stuc", bz(-1.6, 1.6, -1.2, 1.2, -0.1, 2.0, 0.05), HW)
    put("waterrad", "stuc", boutline([(-1.2, 2.0), (1.2, 2.0), (1.0, 2.6), (0.5, 2.9), (0.5, 3.4), (0.0, 3.6), (-0.5, 3.4), (-0.5, 2.9), (-1.0, 2.6)], -1.25, 0.25), HW)   # klokgevel
    db = bmesh.new()
    for s in (-1, 1):
        q = [(-1.8, s * 1.45, 1.85), (1.8, s * 1.45, 1.85), (1.8, 0, 3.0), (-1.8, 0, 3.0)]
        A = [db.verts.new(p) for p in q]; B = [db.verts.new((p[0], p[1], p[2] + 0.14)) for p in q]
        db.faces.new(A); db.faces.new(B[::-1])
        for i in range(4): db.faces.new((A[i], A[(i + 1) % 4], B[(i + 1) % 4], B[i]))
    bmesh.ops.recalc_face_normals(db, faces=db.faces); put("waterrad", "pannen", db, HW)
    morielje(Vector((0, 0, 0)), 1.0, 2.4, "waterrad");
    for (part, mat), bm_ in list(PARTS.items()):
        pass
    deurtje(Vector((15.6 - 0.2, 16.95, 0)), -math.pi / 2, 0.75, 1.55, "waterrad")
    raampje(Vector((14.2, 18.4, 0.9)), math.pi, 0.4, 0.45, "waterrad")
    MR = Matrix.Translation((13.9, 17.4, 0.9)) @ Matrix.Rotation(math.pi / 2, 4, "Y")                         # waterrad
    put("waterrad", "hout", btube([(1.0 * math.cos(a), 1.0 * math.sin(a), -0.15) for a in [k * math.tau / 20 for k in range(21)]], 0.05, 5), MR)
    put("waterrad", "hout", btube([(1.0 * math.cos(a), 1.0 * math.sin(a), 0.15) for a in [k * math.tau / 20 for k in range(21)]], 0.05, 5), MR)
    for k in range(10):
        a = k * math.tau / 10; put("waterrad", "hout", bz(-0.04, 0.04, -0.18, 0.18, 0.0, 1.05), MR @ Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(-math.pi / 2, 4, "X"))
    put("waterrad", "hout", btube([(14.0, 17.4, 0.9), (14.4, 17.4, 0.9)], 0.07, 6))
    put("waterrad", "hout", bz(-0.55, 0.55, -0.45, 0.45, 0.0, 0.06), TR(13.6, 15.6, 0.3, 10))                 # bruggetje
    put("waterrad", "hout", bz(-0.04, 0.04, -0.5, 0.5, 0.0, 0.9), TR(14.6, 16.1, 0, 0))                       # hekje met kruk
    for k in range(5): put("waterrad", "hout", bz(-0.02, 0.02, -0.04, 0.04, 0.0, 0.9), TR(14.6, 15.7 + k * 0.2, 0, 0))
    for (x, y) in ((12.3, 20.2), (13.9, 20.5), (12.4, 21.6), (14.0, 21.9)): put("waterrad", "hout", btube([(x, y, -0.1), (x, y, 1.9)], 0.05, 5))   # stro-afdakje wasvrouwtje
    put("waterrad", "riet", boutline([(-1.0, 1.8), (1.0, 1.8), (0.0, 2.5)], -1.0, 2.0), TR(13.15, 21.05, 0, 90))
    put("waterrad", "hout", bz(-0.9, 0.9, -0.8, 0.8, 0.25, 0.3), TR(13.15, 21.05, 0, 8)); put("waterrad", "hout", blathe([(0.3, 0.3), (0.35, 0.6), (0.0, 0.6)], 10), Matrix.Translation((13.4, 21.0, 0)))
    put("waterrad", "wit", ell((13.4, 21.0, 0.62), (0.28, 0.28, 0.06), 8, 4))
    coll_box(15.6, 18.2, 1.0, 3.2, 2.4, 2.0, -8)
    # ---------- 6. Grote Kabouterhuis (doorloop) ----------
    vijver(VIJVER_ZW, "vijvers")
    gx = sum(p[0] for p in GKH) / len(GKH); gy = sum(p[1] for p in GKH) / len(GKH)
    gw = bmesh.new(); Lp = [Vector(p) for p in GKH]
    lo = [gw.verts.new((p.x, p.y, -0.1)) for p in Lp]; hi = [gw.verts.new((p.x + (gx - p.x) * 0.06, p.y + (gy - p.y) * 0.06, 2.5)) for p in Lp]
    for i in range(len(Lp)): gw.faces.new((lo[i], lo[(i + 1) % len(Lp)], hi[(i + 1) % len(Lp)], hi[i]))
    for t in tessellate_polygon([[Vector((v.co.x, v.co.y, 0)) for v in hi]]): gw.faces.new([hi[i] for i in t]); gw.faces.new([lo[i] for i in reversed(t)])
    bmesh.ops.recalc_face_normals(gw, faces=gw.faces)
    put("grootkabouterhuis", "stuc", organisch(gw, 0.07, 3, 0.5, 0.08, 0.9, 0.35))
    morielje(Vector((-7.2, -6.6, 2.3)), 1.9, 4.0, "grootkabouterhuis")
    hoed(Vector((-3.6, -7.6, 2.35)), 3.3, 1.2, "grootkabouterhuis")
    for (p, a) in (((-6.75, -3.65, 0.0), math.radians(118)), ((-1.75, -9.2, 0.0), math.radians(-10))):
        deurtje(Vector(p), a, 1.0, 2.0, "grootkabouterhuis", True)
    put("grootkabouterhuis", "ijzer", btube([(-6.95 + 0.25 * math.cos(t), -3.55, 2.2 + 0.25 * math.sin(t)) for t in [k * math.pi / 8 for k in range(9)]], 0.025, 4))   # hoefijzer
    for (p, a) in (((-8.8, -6.6, 1.0), math.pi), ((-3.0, -5.6, 1.0), math.radians(50))):
        M_ = Matrix.Translation(p) @ Matrix.Rotation(a, 4, "Z")
        put("grootkabouterhuis", "donker", bz(-0.04, 0.02, -0.5, 0.5, 0.0, 0.8), M_)
        for k in range(5): put("grootkabouterhuis", "ijzer", bz(0.0, 0.04, -0.4 + 0.2 * k - 0.015, -0.4 + 0.2 * k + 0.015, 0.0, 0.8), M_)
    put("grootkabouterhuis", "hout", bz(-0.7, 0.7, -0.3, 0.3, 2.5, 2.6), TR(-4.0, -4.6, 0, 50)); put("grootkabouterhuis", "hout", btube([(-4.6, -4.95, 2.6), (-3.4, -4.25, 2.6)], 0.03, 4))   # balkonnetje
    raampje(Vector((-4.2, -4.5, 2.7)), math.radians(140), 0.45, 0.55, "grootkabouterhuis")
    put("grootkabouterhuis", "hout", bz(-0.35, 0.35, -0.35, 0.35, 0.0, 0.9), TR(-3.6, -7.6, 3.5)); put("grootkabouterhuis", "pannen", blathe([(0.55, 0), (0.0, 0.7)], 4), Matrix.Translation((-3.6, -7.6, 4.4)) @ Matrix.Rotation(math.pi / 4, 4, "Z"))   # klokkentorentje
    put("grootkabouterhuis", "lood", ell((-3.6, -7.6, 3.9), (0.15, 0.15, 0.18), 8, 6))
    put("grootkabouterhuis", "lood", btube([(-8.4, -8.2, 2.0), (-8.5, -8.3, 4.6), (-8.3, -8.35, 5.0)], 0.13, 7))                                       # loden schoorsteentje
    for (x, y, z) in ((-7.2, -6.6, 6.35), (-3.6, -7.6, 5.15)): put("grootkabouterhuis", "ijzer", btube([(x, y, z), (x, y, z + 0.6)], 0.015, 4)); put("grootkabouterhuis", "ijzer", boutline([(0, 0), (0.35, 0.05), (0.3, 0.2), (0, 0.18)], -0.01, 0.02), TR(x, y, z + 0.4))
    coll_box(-8.3, -6.9, 1.3, 1.2, 4.0, 2.6); coll_box(-4.6, -9.8, 1.3, 3.5, 0.6, 2.6); coll_box(-2.6, -6.2, 1.3, 1.0, 3.2, 2.6, 30)
    # ---------- bordje + sprookjesboek ----------
    MB = TR(-1.6, 24.2, 0, 90)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.035, 6), MB)
    MBk = MB @ TR(0, 0, 0.9) @ Matrix.Rotation(math.radians(28), 4, "X")
    put("boek", "rood", bz(-0.42, 0.42, -0.28, 0.28, -0.04, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.26, 0.26, 0.0, 0.05, 0.01), MBk)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"KD_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "vijvers": [VIJVER_NW, VIJVER_O, VIJVER_ZW], "hoofdpad": HOOFDPAD, "zijpaden": ZIJPADEN}, open(os.path.join(out, "kabouterdorp_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
