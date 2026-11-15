"""04_omgeving De Trollenkoning: vijvertje (OSM 55423661, r 2.9) met troebel water, keienrand + lage groene buisleuning langs het plein (Boekloc),
plein (wig tussen de paden 405848924 en 1406396368, tot hun binnenrand; Daan: licht grind) met 13 dierenriem-medaillons in een boog (lemma: vanaf
links vis ... tot weer vis rechts), wijzersteen (grote ronde kei met bronzen wijzerplaat + wijzer, 2023/wijzerensteen) met de trilsteen ervoor,
sprookjesboek op standaard. Frame = 03_boom. Gebruik: Blender -b -P 04_omgeving.py -- --master TK_omgeving_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"grind": ((0.86, 0.83, 0.76, 1), 0.95), "rots": ((0.45, 0.45, 0.42, 1), 0.95), "natuursteen": ((0.4, 0.4, 0.4, 1), 0.85),
        "brons": ((0.55, 0.4, 0.2, 1), 0.35), "groen": ((0.16, 0.3, 0.27, 1), 0.6), "water": ((0.1, 0.14, 0.09, 1), 0.1),
        "ijzer": ((0.04, 0.05, 0.05, 1), 0.45), "hout": ((0.35, 0.22, 0.13, 1), 0.8), "papier": ((0.92, 0.86, 0.7, 1), 0.9), "rood": ((0.62, 0.1, 0.1, 1), 0.5),
        "modder": ((0.12, 0.1, 0.07, 1), 1.0)}
RV = 2.9                                                                                # vijver
ARC = [(3.25 * math.cos(math.radians(a)), 3.25 * math.sin(math.radians(a))) for a in range(12, -151, -8)]
PLEIN = [(0.04, -8.55), (4.95, 0.6)] + ARC + [(-4.74, -2.34), (-0.9, -6.0)]
rr = random.Random(7)


def inside(px, py, poly):
    c = False; j = len(poly) - 1
    for i in range(len(poly)):
        (xi, yi), (xj, yj) = poly[i], poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi: c = not c
        j = i
    return c


def plaat(poly, z, mat, part, dz=0.12):
    bm = bmesh.new(); t_ = [bm.verts.new((x, y, z)) for x, y in poly]; b_ = [bm.verts.new((x, y, z - dz)) for x, y in poly]
    ft = bm.faces.new(t_); fb = bm.faces.new(b_[::-1]); N = len(poly)
    for i in range(N): bm.faces.new((t_[i], b_[i], b_[(i + 1) % N], t_[(i + 1) % N]))
    bmesh.ops.triangulate(bm, faces=[ft, fb], ngon_method="EAR_CLIP"); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update()
    for f_ in bm.faces:
        if abs(f_.normal.z) > 0.5 and (f_.calc_center_median().z > z - dz / 2) != (f_.normal.z > 0): f_.normal_flip()
    put(part, mat, bm)


def symbool(k):
    """eenvoudige reliefvorm per teken (lijnen in het medaillon): lijst polylijnen in eenheidscirkel"""
    t = [math.tau * i / 16 for i in range(17)]
    vis = [[(-0.5 + 0.9 * u, 0.25 * math.sin(u * math.pi) + 0.2) for u in [i / 8 for i in range(9)]], [(-0.5 + 0.9 * u, -0.25 * math.sin(u * math.pi) - 0.2) for u in [i / 8 for i in range(9)]]]
    vormen = [vis, [[(-0.5, 0.4), (0, -0.3), (0.5, 0.4)], [(-0.3, 0.6), (-0.5, 0.4)], [(0.3, 0.6), (0.5, 0.4)]],          # vissen, ram
              [[(0.45 * math.cos(a), 0.45 * math.sin(a) - 0.1) for a in t], [(-0.45, 0.35), (-0.2, 0.55)], [(0.45, 0.35), (0.2, 0.55)]],   # stier
              [[(-0.3, -0.5), (-0.3, 0.5)], [(0.3, -0.5), (0.3, 0.5)], [(-0.5, 0.5), (0.5, 0.5)], [(-0.5, -0.5), (0.5, -0.5)]],         # tweelingen
              [[(0.3 * math.cos(a) - 0.2, 0.3 * math.sin(a) + 0.2) for a in t[:12]], [(0.3 * math.cos(a) + 0.2, 0.3 * math.sin(a) - 0.2) for a in t[8:]]],   # kreeft
              [[(0.25 * math.cos(a) - 0.25, 0.25 * math.sin(a) + 0.2) for a in t], [(-0.05, 0.15), (0.2, -0.4), (0.5, -0.2)]],      # leeuw
              [[(-0.5, 0.5), (-0.5, -0.5)], [(-0.5, 0.4), (-0.15, 0.5), (-0.15, -0.5)], [(-0.15, 0.4), (0.2, 0.5), (0.2, -0.3), (0.5, -0.5)]],  # maagd
              [[(-0.5, -0.3), (0.5, -0.3)], [(-0.5, 0.0), (-0.2, 0.0), (-0.2, 0.3), (0.2, 0.3), (0.2, 0.0), (0.5, 0.0)]],            # weegschaal
              [[(-0.5, 0.5), (-0.5, -0.4)], [(-0.5, 0.4), (-0.15, 0.5), (-0.15, -0.4)], [(-0.15, 0.4), (0.2, 0.5), (0.2, -0.4), (0.45, -0.2)], [(0.35, -0.1), (0.45, -0.2), (0.4, -0.35)]],  # schorpioen
              [[(-0.45, -0.45), (0.45, 0.45)], [(0.1, 0.45), (0.45, 0.45), (0.45, 0.1)], [(-0.2, 0.1), (0.1, -0.2)]],                # boogschutter
              [[(-0.5, 0.3), (-0.25, -0.3), (0.0, 0.3), (0.2, -0.4)], [(0.2, -0.4), (0.45, -0.1), (0.3, 0.1)]],                       # steenbok
              [[(-0.5, 0.15), (-0.25, 0.35), (0.0, 0.15), (0.25, 0.35), (0.5, 0.15)], [(-0.5, -0.2), (-0.25, 0.0), (0.0, -0.2), (0.25, 0.0), (0.5, -0.2)]],   # waterman
              vis]                                                                                                                  # vissen
    return vormen[k % len(vormen)]


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ---------- vijver: troebel water (dikke plaat, Roblox toont alleen voorkanten) + modderbodem ----------
    circ = [(RV * math.cos(a * math.tau / 48), RV * math.sin(a * math.tau / 48)) for a in range(48)]
    plaat(circ, -0.18, "water", "water", 0.08)
    plaat([(x * 1.02, y * 1.02) for x, y in circ], -0.75, "modder", "water", 0.1)
    bm = bmesh.new(); top = [bm.verts.new((x * 1.03, y * 1.03, 0.0)) for x, y in circ]; bot = [bm.verts.new((x * 1.03, y * 1.03, -0.8)) for x, y in circ]
    for i in range(48): bm.faces.new((top[i], top[(i + 1) % 48], bot[(i + 1) % 48], bot[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:                                                               # oeverwand naar binnen gericht
        if f.normal.dot(f.calc_center_median().to_2d().to_3d()) > 0: f.normal_flip()
    put("water", "modder", bm)
    # ---------- keienrand langs het plein (Boekloc: afgeronde keien op een rij) ----------
    for a in range(-170, 15, 4):
        x, y = 3.12 * math.cos(math.radians(a)), 3.12 * math.sin(math.radians(a))
        k = ell((0, 0, 0), (0.22, 0.15, 0.12), 8, 6)
        for v in k.verts: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-0.5, 1))) * 0.025
        put("rand", "natuursteen", k, TR(x, y, 0.1, a + 90 + rr.uniform(-8, 8)))
    # keien achter rond (natuurlijke rand)
    for a in range(20, 171, 9):
        x, y = 3.05 * math.cos(math.radians(a)), 3.05 * math.sin(math.radians(a)); sc = rr.uniform(0.25, 0.45)
        k = ell((0, 0, 0), (sc, sc * 0.8, sc * 0.55), 8, 6)
        for v in k.verts: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * sc * 0.15
        put("oever", "rots", k, TR(x, y, 0.02, rr.uniform(0, 360)))
    # ---------- lage groene buisleuning achter de keienrand ----------
    pts = [(2.92 * math.cos(math.radians(a)), 2.92 * math.sin(math.radians(a))) for a in range(-172, 17, 6)]
    for (a, b) in zip(pts, pts[1:]):
        put("leuning", "groen", btube([(a[0], a[1], 0.62), (b[0], b[1], 0.62)], 0.022, 6))
        put("leuning", "groen", btube([(a[0], a[1], 0.32), (b[0], b[1], 0.32)], 0.015, 5))
    for i, p in enumerate(pts):
        if i % 3 == 0: put("leuning", "groen", btube([(p[0], p[1], 0.05), (p[0], p[1], 0.66)], 0.025, 6)); put("leuning", "groen", ell((p[0], p[1], 0.68), (0.04, 0.04, 0.04), 6, 4))
    for (a, b) in zip(pts[::3], pts[3::3]):
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); d = (b[0] - a[0], b[1] - a[1])
        coll_box(m[0], m[1], 0.5, math.hypot(*d), 0.15, 1.0, math.degrees(math.atan2(d[1], d[0])))
    # ---------- plein (licht grind) ----------
    plaat(PLEIN, 0.1, "grind", "plein", 0.14)
    # ---------- 13 dierenriem-medaillons in een boog (vanaf links vissen ... tot weer vissen rechts) ----------
    k = 0
    for i in range(13):
        a = math.radians(-132 + 66 * i / 12); r = 5.15
        x, y = r * math.cos(a), r * math.sin(a)
        if not inside(x, y, PLEIN): r = 4.6; x, y = r * math.cos(a), r * math.sin(a)
        M = TR(x, y, 0.067, math.degrees(a) + 90)                                     # 1 cm boven het grind (verzonken in de bestrating)
        put("medaillon", "natuursteen", blathe([(0, 0), (0.38, 0), (0.38, 0.03), (0.35, 0.035), (0, 0.035)], 24), M)
        put("medaillon", "natuursteen", blathe([(0.31, 0.03), (0.33, 0.03), (0.33, 0.05), (0.31, 0.05)], 24), M)     # ring
        for pl in symbool(i if i < 12 else 0):
            P = [Vector((px * 0.26, py * 0.26, 0.045)) for px, py in pl]
            for p0, p1 in zip(P, P[1:]):
                if (p1 - p0).length > 1e-4: put("medaillon", "brons", btube([p0, p1], 0.012, 4), M)
    # ---------- wijzersteen + trilsteen (2023, Trollenkoningwijzerensteen) ----------
    wx, wy = 3.25, -1.35                                                                 # 2023: op de keienrand, ~2.2 m rechts naast de stam; leuning loopt erachter door
    kei = ell((0, 0, 0.45), (0.72, 0.6, 0.55), 18, 12)
    for v in kei.verts:
        v.co += v.co.normalized() * 0.06 * noise.noise(v.co * 3.0); v.co.z = max(v.co.z, -0.05)
    put("wijzer", "rots", kei, TR(wx, wy, 0.0, 20))
    Mw = TR(wx, wy, 0.92, 20) @ Matrix.Rotation(math.radians(-22), 4, "X")
    put("wijzer", "brons", blathe([(0, 0), (0.42, 0), (0.44, 0.03), (0.42, 0.06), (0, 0.06)], 28), Mw)
    for i in range(12):
        a = i * math.tau / 12; put("wijzer", "brons", bz(-0.02, 0.02, 0.28, 0.38, 0.06, 0.08), Mw @ Matrix.Rotation(a, 4, "Z"))
    put("wijzer", "brons", blathe([(0, 0), (0.06, 0), (0.06, 0.05), (0, 0.06)], 10), Mw @ TR(0, 0, 0.06))
    put("wijzer", "brons", bz(-0.025, 0.025, 0.0, 0.36, 0.1, 0.12), Mw @ Matrix.Rotation(math.radians(40), 4, "Z"))     # koperen wijzer
    coll_box(wx, wy, 0.5, 1.3, 1.1, 1.0, 20)
    put("tril", "natuursteen", bz(-0.55, 0.55, -0.4, 0.4, 0.0, 0.17, 0.03), TR(wx + 0.45, wy - 0.95, 0.0, 20))          # hardstenen stapsteen
    # ---------- sprookjesboek op standaard (Boekloc: rechts op het plein bij de leuning) ----------
    MB = TR(4.15, 0.55, 0.1, 35)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.035, 6), MB)
    for s in (-1, 1): put("boek", "ijzer", btube([(0, 0, 0.05), (s * 0.12, 0.05, 0.12), (s * 0.22, 0.0, 0.0)], 0.018, 5), MB)
    MBk = MB @ TR(0, 0, 0.9) @ Matrix.Rotation(math.radians(28), 4, "X")
    put("boek", "hout", bz(-0.42, 0.42, -0.28, 0.28, -0.04, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.26, 0.26, 0.0, 0.05, 0.01), MBk)
    coll_box(4.15, 0.55, 0.5, 0.7, 0.5, 1.0, 35)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"TO_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": PLEIN, "vijver": RV}, open(os.path.join(out, "omgeving_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
