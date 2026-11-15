"""03_huis De Prinses op de Erwt (2025, Sander de Bruijn): klein hoog huisje als dependance van het Grand Hotel.
Klokgevel met S-voluten, consoles, beeldnis met kamerheer, makelaar met gouden spits; dubbele blauwgroene glasdeuren; lantaarnnissen;
groen koperen zadeldak met felsnaden en gouden kam; massieve schoorsteenpijler links-achter met koperen kap op de verspringing en
edelhert-windvaan; groot kijkraam in de linkerzijgevel met blauwgroen sierpaneel; natuurstenen plint; achtergevel met luik; regenpijp.
Bronnen: zie asset-brief.md (Theekoepeltje = ontwerp-vooraanzicht, Pleintje/Exterieur/Achterkant/Kamerheer, OSM 1406396369).
Frame: oorsprong midden OSM-vorm; -Y = voorkant (NO); -X = ZO (kijkraam); z 0 = maaiveld.
Gebruik: Blender -b -P 03_huis.py -- --master PE_huis_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.86, 0.82, 0.72, 1), 0.9), "natuursteen": ((0.74, 0.66, 0.5, 1), 0.85), "koper": ((0.33, 0.56, 0.48, 1), 0.5),
        "goud": ((0.8, 0.6, 0.22, 1), 0.3), "deur": ((0.13, 0.27, 0.27, 1), 0.5), "venster": ((0.03, 0.04, 0.05, 1), 0.15),
        "ijzer": ((0.04, 0.05, 0.05, 1), 0.45), "glaslamp": ((0.95, 0.93, 0.88, 1), 0.2), "lantaarnrood": ((0.75, 0.15, 0.08, 1), 0.3),
        "paneel": ((0.3, 0.5, 0.5, 1), 0.5), "rood": ((0.62, 0.1, 0.1, 1), 0.5), "huid": ((0.85, 0.66, 0.52, 1), 0.6),
        "zwart": ((0.05, 0.05, 0.05, 1), 0.6), "creme": ((0.9, 0.85, 0.72, 1), 0.7), "hout": ((0.35, 0.22, 0.13, 1), 0.8)}
# ---- maten (asset-brief.md) ----
XL, XR = -1.95, 2.67            # voorgevel 4.62 m (camera opgelost uit Exterieur) + pijler 0.75 + plint = OSM 5.44
XC = (XL + XR) / 2; HW = (XR - XL) / 2
YF, YB = -2.35, 2.35            # voorgevel / achtergevel (plint 0.1 erbuiten = OSM 4.89)
ZC = 5.5                        # kroonlijst-top (Pleintje 5.42, Exterieur 5.63, Aanloop 5.4-5.6)
RIDGE = 7.95                    # nok (Aanloop, dak ~52 graden)
APEX = 8.7; BAND = 7.5          # klokgevel-top (Exterieur 8.47, Aanloop 8.6, Pleintje 9.7), band onder de kap
SPIRE = 10.3                     # gouden spits (ontwerp: makelaar 0.38 B boven de top)
PLINT = 1.0                    # natuurstenen plint (Exterieur: tot onder het kijkraam)
DOOR_W, DOOR_H = 2.33, 4.1      # dubbele deur (Exterieur opgelost: 2.33 x 4.10)
PX0, PX1, PY0, PY1 = -2.7, -1.85, 1.15, 2.45      # schoorsteenpijler onder (Pleintje: steekt ~0.75 m uit de zijgevel)
PZ1 = 4.15; CX0 = -2.35; CHTOP = 8.0               # verspringing met koperen kap, schoorsteen tot 7.0 (Pleintje: ~ geveltop)
WIN_Y0, WIN_Y1, WIN_Z0, WIN_Z1 = -1.04, 0.95, 1.14, 3.7   # kijkraam linkerzijgevel (opgelost uit Pleintje), paneel tot ~4.4


def gable_outline():
    """klokgevel-omtrek (x relatief, z) rechts van onder naar de top, gespiegeld links.
    Exterieur-overlay: grote S-voluut vanaf de hoekconsole naar binnen, band op 7.5 (halve breedte 1.25), smalle spitse kap (halve breedte 0.85)."""
    k = (BAND - ZC) / 1.6
    r = [(HW, ZC), (HW, ZC + 0.3 * k), (HW - 0.1, ZC + 0.55 * k), (HW - 0.3, ZC + 0.75 * k), (HW - 0.55, ZC + 0.9 * k), (HW - 0.78, ZC + 1.08 * k),
         (1.18, BAND - 0.28), (1.12, BAND - 0.05), (1.25, BAND - 0.05), (1.25, BAND + 0.12), (0.85, BAND + 0.12)]
    hc = APEX - BAND - 0.12
    cap = [(0.85 * (1 - t) ** 0.85 * (1 + 0.25 * math.sin(math.pi * t)), BAND + 0.12 + hc * t) for t in [k_ / 12 for k_ in range(1, 12)]]
    right = r + cap + [(0.0, APEX)]
    left = [(-x, z) for x, z in reversed(right[:-1])]
    return right + left


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ---------- romp (vijfhoek met achtergevel-driehoek) + klokgevel ----------
    w = bmesh.new()
    def addb(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); w.from_mesh(me_); bpy.data.meshes.remove(me_)
    addb(boutline([(XL, 0.0), (XR, 0.0), (XR, ZC), (XC, RIDGE - 0.05), (XL, ZC)], YF, YB - YF))
    go = [(XC + x, z) for x, z in gable_outline()]
    addb(boutline([(XR, ZC - 0.3)] + go + [(XL, ZC - 0.3)], YF - 0.02, 0.34))          # klokgevel net voor de rompgevel (geen dubbel vlak)
    # pijler onder + schoorsteen
    addb(bz(PX0, PX1 + 0.12, PY0, PY1, 0.0, PZ1))
    addb(bz(CX0, PX1 + 0.35, PY0 + 0.05, PY1 - 0.05, PZ1 - 0.1, CHTOP - 0.25))
    put("romp", "stuc", w)
    coll_box(XC, 0.0, ZC / 2, XR - XL, YB - YF, ZC); coll_box((PX0 + PX1) / 2, (PY0 + PY1) / 2, PZ1 / 2, PX1 - PX0, PY1 - PY0, PZ1)
    # ---------- natuursteen: plint, kroonlijsten, gevellijsten, consoles ----------
    put("steen", "natuursteen", bsweep([(0.1, 0.0), (0.1, PLINT - 0.08), (0.14, PLINT - 0.04), (0.14, PLINT), (0.0, PLINT + 0.04)], XL, XR, YF, YB, 0.0))
    put("steen", "natuursteen", bsweep([(0.1, 0.0), (0.1, PLINT - 0.08), (0.14, PLINT - 0.04), (0.14, PLINT), (0.0, PLINT + 0.04)], PX0, PX1, PY0, PY1, 0.0))
    # zijkroonlijst langs de dakvoet (links/rechts/achter), voor tot de gevel
    prof = [(0.0, -0.22), (0.06, -0.16), (0.1, -0.08), (0.2, 0.0), (0.2, 0.06), (0.0, 0.06)]
    for x, s in ((XL, -1), (XR, 1)):
        bm = bmesh.new(); rings = []
        for o, z in prof:
            rings.append([bm.verts.new((x + s * o, y, ZC + z)) for y in (YF + 0.1, YB + 0.2)])
        for a, b in zip(rings, rings[1:]): bm.faces.new((a[0], a[1], b[1], b[0]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("steen", "natuursteen", bm)
    # consoles met uitkragende lijst op de gevelhoeken (Kamerheer, Exterieur)
    for s in (-1, 1):
        x0 = XC + s * (HW - 0.55); x1 = XC + s * (HW + 0.32)
        put("steen", "natuursteen", bz(min(x0, x1), max(x0, x1), YF - 0.42, YF + 0.32, ZC - 0.08, ZC + 0.08, 0.02))
        put("steen", "natuursteen", bz(min(x0, x1) + 0.06, max(x0, x1) - 0.06, YF - 0.36, YF + 0.3, ZC - 0.24, ZC - 0.08, 0.02))
        for xx in (x0 + s * 0.12, x1 - s * 0.14):
            put("steen", "natuursteen", bz(xx - 0.09, xx + 0.09, YF - 0.3, YF, ZC - 0.6, ZC - 0.24, 0.02))
    # gevellijst langs de klokgevel-omtrek
    put("steen", "natuursteen", band([(XC + x, z) for x, z in gable_outline()[::-1]], 0.13, YF - 0.06, 0.4))
    # voluten (krullen): onderaan bij de consoles en halverwege
    def spiraal(cx, cz, R, turns, s, y0):
        pts = []
        n = int(28 * turns)
        for i in range(n + 1):
            t = i / n; a = -s * (turns * math.tau * t) + (math.pi / 2 if s > 0 else math.pi / 2); r = R * (1 - 0.82 * t)
            pts.append((cx + s * r * math.cos(a), y0, cz + r * math.sin(a)))
        return pts
    for s in (-1, 1):                                                                         # voluten als opgerolde krullen (Exterieur, Kamerheer)
        for (dx, z, R, rt) in ((HW - 0.3, ZC + 0.45, 0.27, 0.075), (1.3, BAND - 0.42, 0.18, 0.055)):
            put("steen", "natuursteen", btube(spiraal(XC + s * dx, z, R, 1.6, s, YF - 0.1), rt, 7))
            put("steen", "natuursteen", blathe([(0, 0), (R * 0.95, 0), (R * 0.95, 0.06), (0, 0.08)], 14), Matrix.Translation((XC + s * dx, YF - 0.0, z)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    # makelaar + gouden spits
    put("steen", "natuursteen", blathe([(0, 0), (0.16, 0), (0.18, 0.08), (0.1, 0.2), (0.06, 0.3), (0, 0.32)], 12), TR(XC, YF + 0.16, APEX - 0.02))
    put("spits", "goud", blathe([(0, 0), (0.06, 0), (0.09, 0.1), (0.05, 0.2), (0.02, 0.35), (0.04, 0.42), (0.015, 0.5), (0.008, SPIRE - APEX - 0.3), (0, SPIRE - APEX - 0.28)], 10), TR(XC, YF + 0.16, APEX + 0.28))
    # schoorsteen-lijsten + kap
    put("steen", "natuursteen", bsweep([(0.0, 0.0), (0.08, 0.06), (0.08, 0.14), (0.0, 0.18)], CX0, PX1 + 0.35, PY0 + 0.05, PY1 - 0.05, 7.4))
    put("steen", "natuursteen", bsweep([(0.0, 0.0), (0.1, 0.08), (0.1, 0.2), (0.04, 0.26)], CX0, PX1 + 0.35, PY0 + 0.05, PY1 - 0.05, CHTOP - 0.26))
    put("steen", "natuursteen", bz(CX0 + 0.05, PX1 + 0.3, PY0 + 0.1, PY1 - 0.1, CHTOP - 0.02, CHTOP + 0.06))
    put("steen", "natuursteen", bsweep([(0.0, 0.0), (0.1, 0.06), (0.1, 0.14), (0.0, 0.18)], PX0, PX1, PY0, PY1, PZ1 - 0.18))
    # ---------- koperen dak + felsnaden + gouden kam ----------
    ov = 0.18; th = 0.1
    for s in (-1, 1):
        xe = (XL - ov) if s < 0 else (XR + ov); ze = ZC + 0.04 - ov * (RIDGE - ZC) / HW
        bm = bmesh.new(); y0, y1 = YF + 0.15, YB + 0.22
        q = [(xe, y0, ze), (XC, y0, RIDGE), (XC, y1, RIDGE), (xe, y1, ze)]
        top = [bm.verts.new(p) for p in q]; bot = [bm.verts.new((p[0], p[1], p[2] - th)) for p in q]
        bm.faces.new(top); bm.faces.new(bot[::-1])
        for i in range(4): bm.faces.new((top[i], bot[i], bot[(i + 1) % 4], top[(i + 1) % 4]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("dak", "koper", bm)
        n = int((y1 - y0) / 0.42)
        for k in range(1, n + 1):
            y = y0 + (y1 - y0) * k / (n + 1)
            put("dak", "koper", btube([(xe, y, ze + 0.01), (XC, y, RIDGE + 0.01)], 0.022, 4))
    put("dak", "koper", btube([(XC, YF + 0.15, RIDGE + 0.02), (XC, YB + 0.22, RIDGE + 0.02)], 0.06, 6))
    for k in range(9):                                                                # gouden nokkam met lelies (Achterkant)
        y = YF + 0.6 + k * (YB - YF - 0.5) / 8
        put("kam", "goud", btube([(XC, y, RIDGE + 0.05), (XC, y, RIDGE + 0.32)], 0.012, 4))
        put("kam", "goud", ell((XC, y, RIDGE + 0.36), (0.03, 0.03, 0.05), 6, 4))
    put("kam", "goud", btube([(XC, YF + 0.6, RIDGE + 0.12), (XC, YB - 0.1, RIDGE + 0.12)], 0.012, 4))
    # koperen kap over de verspringing van de pijler (Exterieur, Pleintje)
    bm = bmesh.new(); R = PX1 - CX0 + 0.0
    arcp = [(PX0 - 0.06 + (CX0 - PX0 + 0.06) * (1 - math.cos(t)), PZ1 + (0.75) * math.sin(t)) for t in [math.pi / 2 * k / 8 for k in range(9)]]
    A = [bm.verts.new((x, PY0 - 0.06, z)) for x, z in arcp]; B = [bm.verts.new((x, PY1 + 0.06, z)) for x, z in arcp]
    for i in range(len(arcp) - 1): bm.faces.new((A[i], A[i + 1], B[i + 1], B[i]))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.05); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("dak", "koper", bm)
    # ---------- voordeur (dubbel, blauwgroen met ruiten, segmentboog) in stenen omlijsting ----------
    dx0, dx1 = XC - DOOR_W / 2, XC + DOOR_W / 2
    dp = [(dx0, 0.12)] + [(XC + DOOR_W / 2 * math.cos(t), DOOR_H - 0.45 + 0.45 * math.sin(t)) for t in [math.pi - math.pi * k / 12 for k in range(13)]][::-1][::-1] + [(dx1, 0.12)]
    boog = lambda hw, rise, n=8: [(XC - hw + hw * t, DOOR_H - rise + rise * math.sin(t * math.pi / 2 * 0.8) / math.sin(0.4 * math.pi)) for t in [i / n for i in range(n + 1)]]
    dp_ = boog(DOOR_W / 2, 0.6); dp = [(dx0, 0.12)] + dp_ + [(2 * XC - x, z) for x, z in dp_[-2::-1]] + [(dx1, 0.12)]
    put("deur", "deur", boutline(dp, YF - 0.02, 0.06))
    put("deur", "deur", band(dp[::-1], 0.06, YF - 0.07, 0.09))                                  # smal groen kozijn (geen stenen omlijsting: Exterieur)
    for xs in (XC - 0.04, XC + 0.04): put("deur", "deur", bz(xs - 0.035, xs + 0.035, YF - 0.06, YF, 0.12, DOOR_H - 0.02))
    for side in (-1, 1):                                                              # ruiten 3 x 6 per deurvleugel
        xa = XC + (0.1 if side > 0 else -DOOR_W / 2 + 0.12); xb = XC + (DOOR_W / 2 - 0.12 if side > 0 else -0.1)
        za, zb = 1.1, DOOR_H - 0.55
        put("deur", "venster", bz(xa, xb, YF - 0.035, YF - 0.025, za, zb))
        for i in range(1, 3): xx = xa + (xb - xa) * i / 3; put("deur", "deur", bz(xx - 0.02, xx + 0.02, YF - 0.05, YF - 0.03, za, zb))
        for j in range(1, 6): zz = za + (zb - za) * j / 6; put("deur", "deur", bz(xa, xb, YF - 0.05, YF - 0.03, zz - 0.02, zz + 0.02))
        put("deur", "deur", bz(xa - 0.04, xb + 0.04, YF - 0.06, YF - 0.03, 0.25, 1.0))                  # paneel onder
        put("deur", "goud", ell((XC + side * 0.16, YF - 0.08, 1.15), (0.03, 0.03, 0.09), 6, 4))       # klinken
    g_ = [(x, z - 0.14) for x, z in boog(DOOR_W / 2 - 0.12, 0.5)]; put("deur", "venster", boutline(g_ + [(2 * XC - x, z) for x, z in g_[-2::-1]], YF - 0.04, 0.01))
    # ---------- lantaarnnissen naast de deur met rond medaillon (Exterieur, Speaker) ----------
    for s in (-1, 1):
        nx = XC + s * (DOOR_W / 2 + 0.66)
        npts = [(nx - 0.27, 1.45)] + [(nx - 0.27 * math.cos(math.pi * k / 10), 2.85 + 0.27 * math.sin(math.pi * k / 10)) for k in range(11)] + [(nx + 0.27, 1.45)]
        put("nis", "stuc", boutline(npts, YF - 0.005, 0.01))
        put("steen", "natuursteen", band(npts[::-1], 0.07, YF - 0.06, 0.08))
        put("steen", "natuursteen", bz(nx - 0.36, nx + 0.36, YF - 0.16, YF, 1.35, 1.45))
        put("nis", "venster", bz(nx - 0.23, nx + 0.23, YF - 0.022, YF - 0.012, 1.45, 2.95))   # donkere nis voor het gevelvlak             # donkere nis (diepte suggereren)
        put("nis", "paneel", blathe([(0, 0), (0.12, 0), (0.12, 0.03), (0, 0.04)], 12), Matrix.Translation((nx, YF - 0.02, 2.8)) @ Matrix.Rotation(math.radians(90), 4, "X"))
        put("nis", "goud", blathe([(0, 0), (0.14, 0), (0.14, 0.02), (0.12, 0.035), (0, 0.035)], 14), Matrix.Translation((nx, YF - 0.005, 2.8)) @ Matrix.Rotation(math.radians(90), 4, "X"))
        Ml = TR(nx, YF - 0.08, 1.45)                                                                 # rode lantaarn in de nis
        put("nis", "ijzer", bz(-0.08, 0.08, -0.08, 0.08, 0.0, 0.03)); put("nis", "lantaarnrood", bz(-0.06, 0.06, -0.06, 0.06, 0.03, 0.3), Ml)
        put("nis", "ijzer", blathe([(0.09, 0), (0.02, 0.12), (0, 0.14)], 6), Ml @ TR(0, 0, 0.3))
        LAMPS_.append([round(nx, 2), round(YF - 0.25, 2), 1.7])
    # ---------- beeldnis boven de deur met de kamerheer (Kamerheer.jpg) ----------
    bx = XC; bpts = [(bx - 0.33, 5.1)] + [(bx - 0.33 * math.cos(math.pi * k / 10), 6.1 + 0.33 * math.sin(math.pi * k / 10)) for k in range(11)] + [(bx + 0.33, 5.1)]
    put("nis", "venster", boutline(bpts, YF - 0.035, 0.01))
    put("steen", "natuursteen", band(bpts[::-1], 0.09, YF - 0.1, 0.12))
    put("steen", "natuursteen", blathe([(0.0, 0), (0.12, 0), (0.2, 0.18), (0.36, 0.3), (0.36, 0.38), (0, 0.38)], 12), TR(bx, YF - 0.12, 4.73))
    Mk = TR(bx, YF - 0.12, 5.11) @ Matrix.Scale(1.15, 4)                                                                     # kamerheer: rode broek, groen jasje, pet, koffers
    for s in (-1, 1):
        put("figuur", "rood", btube([(s * 0.06, 0, 0.02), (s * 0.06, 0, 0.42)], 0.05, 6), Mk); put("figuur", "zwart", ell((s * 0.06, -0.03, 0.03), (0.05, 0.08, 0.035), 6, 4), Mk)
    put("figuur", "paneel", ell((0, 0, 0.62), (0.15, 0.1, 0.24), 10, 8), Mk); put("figuur", "creme", ell((0, -0.06, 0.68), (0.06, 0.05, 0.14), 6, 6), Mk)
    put("figuur", "huid", ell((0, 0, 0.94), (0.08, 0.08, 0.1), 10, 8), Mk); put("figuur", "zwart", blathe([(0.09, 0), (0.09, 0.05), (0, 0.06)], 10), Mk @ TR(0, 0, 1.0))
    put("figuur", "rood", bz(0.08, 0.22, -0.08, 0.08, 1.02, 1.22), Mk @ Matrix.Rotation(math.radians(10), 4, "Y"))       # koffer op de schouder
    put("figuur", "hout", ell((0.14, -0.1, 0.45), (0.11, 0.08, 0.08), 8, 6), Mk); put("figuur", "paneel", btube([(-0.14, 0, 0.8), (-0.18, -0.05, 0.55)], 0.04, 6), Mk)
    # ---------- kijkraam linkerzijgevel met sierpaneel + gouden ornament, wandlamp, rooster ----------
    x = XL
    def zijvlak(y0, y1, z0, z1, mat, part, dx):
        return bz(x - dx - 0.01, x - dx, y0, y1, z0, z1)
    put("raam", "deur", bz(x - 0.08, x + 0.02, WIN_Y0 - 0.1, WIN_Y1 + 0.1, WIN_Z0 - 0.1, WIN_Z1 + 0.08))
    put("raam", "venster", bz(x - 0.1, x - 0.08, WIN_Y0, WIN_Y1, WIN_Z0, WIN_Z1))
    for i in range(1, 4): yy = WIN_Y0 + (WIN_Y1 - WIN_Y0) * i / 4; put("raam", "deur", bz(x - 0.13, x - 0.08, yy - 0.022, yy + 0.022, WIN_Z0, WIN_Z1))
    for j in range(1, 5): zz = WIN_Z0 + (WIN_Z1 - WIN_Z0) * j / 5; put("raam", "deur", bz(x - 0.13, x - 0.08, WIN_Y0, WIN_Y1, zz - 0.022, zz + 0.022))
    # sierpaneel boven het raam (Decoratie_Raam): blauwgroen geruit veld in een gebogen stenen lijst, gouden ornament
    pz0, pz1 = WIN_Z1 + 0.08, WIN_Z1 + 0.62
    pp = [(WIN_Y0 - 0.05, pz0), (WIN_Y0 - 0.05, pz0 + 0.2), (WIN_Y0 + 0.35, pz0 + 0.24), (WIN_Y0 + 0.6, pz1 - 0.1), (0.5 * (WIN_Y0 + WIN_Y1), pz1),
          (WIN_Y1 - 0.6, pz1 - 0.1), (WIN_Y1 - 0.35, pz0 + 0.24), (WIN_Y1 + 0.05, pz0 + 0.2), (WIN_Y1 + 0.05, pz0)]
    bm = boutline(pp, 0, 0.06); bmesh.ops.transform(bm, matrix=Matrix(((0, -1, 0, x - 0.0), (1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))), verts=bm.verts); put("raam", "paneel", bm)
    bm = band(pp[::-1], 0.07, 0, 0.1); bmesh.ops.transform(bm, matrix=Matrix(((0, -1, 0, x + 0.02), (1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))), verts=bm.verts); put("raam", "goud", bm)
    ym = 0.5 * (WIN_Y0 + WIN_Y1)
    put("raam", "goud", ell((x - 0.1, ym, pz1 + 0.1), (0.05, 0.12, 0.16), 8, 6))
    for s in (-1, 1): put("raam", "goud", ell((x - 0.1, ym + s * 0.12, pz1 + 0.02), (0.04, 0.1, 0.06), 8, 6))
    put("raam", "goud", bz(x - 0.04, x, -0.05 + ym - 0.6, ym + 0.6, 0.22, 0.5))                         # luchtrooster in de plint
    put("steen", "natuursteen", bz(x - 0.2, x, WIN_Y0 - 0.2, WIN_Y1 + 0.2, WIN_Z0 - 0.14, WIN_Z0 - 0.04, 0.01))  # dorpel
    ly = WIN_Y0 - 0.45                                                                                    # bol-wandlamp aan smeedijzeren arm
    put("lamp", "goud", btube([(x, ly, 3.75), (x - 0.25, ly, 3.8), (x - 0.32, ly, 3.72)], 0.02, 5)); put("lamp", "goud", bz(x - 0.03, x, ly - 0.08, ly + 0.08, 3.6, 3.9))
    put("lamp", "glaslamp", ell((x - 0.34, ly, 3.55), (0.2, 0.2, 0.2), 12, 8)); LAMPS_.append([round(x - 0.34, 2), round(ly, 2), 3.55])
    put("lamp", "goud", btube([(XR, -0.2, 3.75), (XR + 0.25, -0.2, 3.8), (XR + 0.32, -0.2, 3.72)], 0.02, 5))
    put("lamp", "glaslamp", ell((XR + 0.34, -0.2, 3.55), (0.2, 0.2, 0.2), 12, 8)); LAMPS_.append([round(XR + 0.34, 2), -0.2, 3.55])
    # ---------- achtergevel: blauwgroen luik hoog in de top, regenpijp ----------
    put("raam", "deur", bz(XC - 0.32, XC + 0.32, YB, YB + 0.06, 5.75, 6.95))
    for zz in (5.95, 6.75): put("raam", "ijzer", bz(XC - 0.28, XC + 0.15, YB + 0.06, YB + 0.08, zz - 0.02, zz + 0.02))
    put("pijp", "natuursteen", btube([(XL - 0.08, PY0 - 0.12, 0.05), (XL - 0.08, PY0 - 0.12, ZC - 0.3)], 0.045, 8))
    put("pijp", "natuursteen", blathe([(0.06, 0), (0.12, 0.14), (0.12, 0.22), (0, 0.22)], 8), TR(XL - 0.08, PY0 - 0.12, ZC - 0.3))
    # ---------- windvaan op de schoorsteen: krulsteun, gouden pot, stang, edelhert, geblokte vlag ----------
    cxp, cyp = (CX0 + PX1 + 0.35) / 2, (PY0 + PY1) / 2; z0 = CHTOP + 0.06
    for a in range(4):
        dxy = Vector((math.cos(a * math.pi / 2), math.sin(a * math.pi / 2), 0))
        put("vaan", "ijzer", btube([Vector((cxp, cyp, z0)) + dxy * 0.3, Vector((cxp, cyp, z0)) + dxy * 0.22 + Vector((0, 0, 0.25)), Vector((cxp, cyp, z0 + 0.5))], 0.02, 5))
    put("vaan", "goud", blathe([(0, 0), (0.08, 0), (0.12, 0.1), (0.08, 0.2), (0.05, 0.24), (0, 0.26)], 10), TR(cxp, cyp, z0 + 0.45))
    put("vaan", "goud", btube([(cxp, cyp, z0 + 0.7), (cxp, cyp, z0 + 2.1)], 0.02, 6))
    for (dz, ln) in ((1.0, 0.25), (1.15, 0.25)): pass
    put("vaan", "goud", btube([(cxp, cyp - 0.3, z0 + 1.2), (cxp, cyp + 0.3, z0 + 1.2)], 0.012, 4))  # windroos-armen
    put("vaan", "goud", btube([(cxp - 0.3, cyp, z0 + 1.2), (cxp + 0.3, cyp, z0 + 1.2)], 0.012, 4))
    Mh = TR(cxp, cyp, z0 + 1.55, 90)
    put("vaan", "goud", ell((0.12, 0, 0.12), (0.18, 0.025, 0.08), 8, 6), Mh)                             # hert: lijf, hals, kop, gewei, poten
    put("vaan", "goud", btube([(0.0, 0, 0.15), (-0.08, 0, 0.32)], 0.03, 5), Mh); put("vaan", "goud", ell((-0.12, 0, 0.34), (0.06, 0.02, 0.03), 6, 4), Mh)
    for g in (-0.04, 0.02): put("vaan", "goud", btube([(-0.08, 0, 0.37), (-0.04 + g, 0, 0.52), (0.04 + g, 0, 0.6)], 0.008, 4), Mh)
    for px_ in (0.0, 0.05, 0.2, 0.25): put("vaan", "goud", btube([(px_, 0, 0.08), (px_ + 0.02, 0, -0.08)], 0.01, 4), Mh)
    for i in range(4):                                                                                    # geblokte vlag (Windwijzer)
        for j in range(2):
            put("vaan", "goud" if (i + j) % 2 else "creme", bz(0.05 + i * 0.1, 0.15 + i * 0.1, -0.01, 0.01, 0.6 + j * 0.1, 0.7 + j * 0.1), TR(cxp, cyp, z0 + 1.2, 90))
    put("vaan", "goud", btube([(0, 0, 0.0), (0.42, 0, 0.0)], 0.01, 4), TR(cxp, cyp, z0 + 1.0, 90))       # pijl
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"PE_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_}, open(os.path.join(out, "huis_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
