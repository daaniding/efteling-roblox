"""03_draak Draak Lichtgeraakt (1979): getrapt wit muurtje met rode pannetjes-dakjes, groene draak op de middenpijler, schatkist op een eilandje van breuksteen,
water in gebogen bekkens, rood Pieck-hek, laag groen hekje, takken + klimop, gouden ornamentjes, sprookjesboek, grindplein. Maten/frame: asset-brief.md.
Gebruik: Blender -b -P 03_draak.py -- --master DR_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.86, 0.84, 0.78, 1), 0.9), "pannen": ((0.62, 0.28, 0.16, 1), 0.7), "breuksteen": ((0.45, 0.45, 0.47, 1), 0.9), "water": ((0.1, 0.14, 0.09, 1), 0.1),
        "modder": ((0.12, 0.1, 0.07, 1), 1.0), "rand": ((0.5, 0.5, 0.5, 1), 0.9), "rood": ((0.7, 0.08, 0.06, 1), 0.5), "leuning": ((0.2, 0.36, 0.3, 1), 0.6),
        "draak": ((0.18, 0.42, 0.25, 1), 0.5), "buik": ((0.55, 0.62, 0.32, 1), 0.6), "stekel": ((0.45, 0.2, 0.45, 1), 0.5), "bek": ((0.7, 0.2, 0.2, 1), 0.5),
        "tand": ((0.95, 0.93, 0.85, 1), 0.4), "oog": ((0.95, 0.85, 0.2, 1), 0.3), "zwart": ((0.03, 0.03, 0.03, 1), 0.3), "vleugel": ((0.15, 0.32, 0.2, 1), 0.6),
        "kist": ((0.45, 0.18, 0.1, 1), 0.7), "goud": ((0.85, 0.65, 0.2, 1), 0.3), "juweel": ((0.2, 0.5, 0.9, 1), 0.1), "tak": ((0.3, 0.24, 0.18, 1), 0.9),
        "klimop": ((0.14, 0.26, 0.12, 1), 0.7), "ijzer": ((0.06, 0.06, 0.06, 1), 0.45), "papier": ((0.92, 0.86, 0.7, 1), 0.9), "grind": ((0.86, 0.83, 0.76, 1), 0.95)}
WY, WD = 2.2, 0.6
TREDEN = [(-1.6, 1.6, 4.6, 0.25), (1.35, 3.0, 3.4, 0.0), (-3.0, -1.35, 3.4, 0.0), (3.0, 4.45, 2.1, -0.05), (-4.35, -3.0, 2.1, -0.05)]   # x0, x1, hoogte, terugzet (Overzicht)
ISLAND = [(-2.93, -0.6), (-0.15, -2.45), (2.94, -1.36), (4.48, 2.21), (-4.34, 2.2)]
WATER = [(-0.15, -2.45), (2.94, -1.36), (4.48, 2.21), (6.37, 1.16), (4.27, -3.01), (1.26, -4.16), (-0.16, -2.97), (-1.29, -4.14), (-3.95, -2.46), (-5.84, 1.26), (-4.34, 2.2), (-2.93, -0.6)]
BUITEN = [(4.48, 2.21), (6.37, 1.16), (4.27, -3.01), (1.26, -4.16), (-0.16, -2.97), (-1.29, -4.14), (-3.95, -2.46), (-5.84, 1.26), (-4.34, 2.2)]
PLEIN = [(-6.7, 2.4), (-6.3, -2.4), (-4.2, -4.6), (-1.3, -5.2), (1.2, -5.2), (4.2, -4.7), (6.6, -2.4), (7.3, 1.5), (6.4, 2.6)]
rr = random.Random(1979)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    from mathutils.geometry import tessellate_polygon
    def plaat(poly, z, mat, part, dz, gat=None):                                                    # tessellate_polygon (even-odd): concaaf + gat zonder overlappende driehoeken
        lus = [poly] + ([gat] if gat else [])
        flat = [p for l in lus for p in l]
        tris = tessellate_polygon([[Vector((x, y, 0)) for x, y in l] for l in lus])
        bm = bmesh.new(); T = [bm.verts.new((x, y, z)) for x, y in flat]; B = [bm.verts.new((x, y, z - dz)) for x, y in flat]
        for t in tris:
            f = bm.faces.new([T[i] for i in t]); f.normal_update()
            if f.normal.z < 0: f.normal_flip()
            g = bm.faces.new([B[i] for i in t]); g.normal_update()
            if g.normal.z > 0: g.normal_flip()
        o = 0
        for l in lus:
            for i in range(len(l)):
                j = (i + 1) % len(l)
                try: bm.faces.new((T[o + i], B[o + i], B[o + j], T[o + j]))
                except ValueError: pass
            o += len(l)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); put(part, mat, bm)
    # ---------- getrapt muurtje met pannetjes-dakjes (Overzicht, Storing) ----------
    muur = bmesh.new()
    def addm(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); muur.from_mesh(me_); bpy.data.meshes.remove(me_)
    for (x0, x1, h, dy) in TREDEN:
        addm(bz(x0, x1, WY + dy, WY + WD + dy + (0.3 if h > 4 else 0), -0.1, h))
    put("muur", "stuc", organisch(muur, 0.035, 2, 0.4, 0.02, 1.5, 0.5))
    coll_box(0.05, WY + WD / 2, 1.5, 8.8, WD + 0.3, 3.0)
    for (x0, x1, h, dy) in TREDEN:                                                                       # dakje: twee hellingen met rijen holle pannen
        y0, y1 = WY + dy - 0.14, WY + WD + dy + (0.3 if h > 4 else 0) + 0.14; yc = (y0 + y1) / 2; rise = 0.28
        for s in (-1, 1):
            ye = y0 if s < 0 else y1
            bm = bmesh.new(); q = [(x0 - 0.1, ye, h - 0.02), (x1 + 0.1, ye, h - 0.02), (x1 + 0.1, yc, h + rise), (x0 - 0.1, yc, h + rise)]
            top = [bm.verts.new(p) for p in q]; bot = [bm.verts.new((p[0], p[1], p[2] - 0.05)) for p in q]
            bm.faces.new(top); bm.faces.new(bot[::-1])
            for i in range(4): bm.faces.new((top[i], bot[i], bot[(i + 1) % 4], top[(i + 1) % 4]))
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("dakjes", "pannen", bm)
            n = int((x1 - x0 + 0.2) / 0.16)
            for i in range(n + 1):
                x = x0 - 0.1 + (x1 - x0 + 0.2) * i / n
                put("dakjes", "pannen", btube([(x, ye - s * 0.03, h + 0.0), (x, yc, h + rise + 0.03)], 0.055, 6))
        put("dakjes", "pannen", btube([(x0 - 0.1, yc, h + rise + 0.04), (x1 + 0.1, yc, h + rise + 0.04)], 0.07, 8))   # nokpannen
    # ---------- gouden drakenornamentjes, takken en klimop tegen de muur ----------
    for x, z in ((-2.2, 2.6), (2.2, 2.6), (-3.7, 1.5), (3.7, 1.5)):
        orn = [(0, 0), (0.12, 0.1), (0.25, 0.05), (0.32, 0.18), (0.22, 0.28), (0.3, 0.38), (0.15, 0.36), (0.05, 0.22), (-0.08, 0.15)]
        put("orn", "goud", boutline(orn, WY - 0.03, 0.03), TR(x - 0.12, 0, z - 0.2))
    takken = [[(-1.9, 0.3), (-1.5, 1.3), (-1.0, 2.0), (-0.3, 2.4), (0.4, 2.2)], [(1.6, 0.2), (1.9, 1.0), (2.5, 1.6), (2.8, 2.1)], [(-0.8, 0.3), (-0.6, 1.1), (-1.1, 1.7)], [(-2.6, 0.3), (-2.9, 1.2), (-2.5, 2.2)]]
    kb = bmesh.new()
    for tk in takken:
        P = [Vector((x, WY - 0.08, z)) for x, z in tk]
        for i, (a, b) in enumerate(zip(P, P[1:])): put("takken", "tak", btube([a, b], 0.07 - 0.015 * i, 6))
        for _ in range(140):
            i = rr.randrange(len(P) - 1); t = rr.random(); c = P[i].lerp(P[i + 1], t) + Vector((rr.uniform(-0.25, 0.25), -0.04, rr.uniform(-0.25, 0.25)))
            s_ = rr.uniform(0.05, 0.09); a = rr.uniform(0, math.tau); t2 = Vector((math.cos(a), 0, math.sin(a))); u2 = Vector((-math.sin(a), 0, math.cos(a)))
            f = kb.faces.new([kb.verts.new(p) for p in (c + t2 * s_, c + u2 * s_ * 1.2 + Vector((0, -0.02, 0)), c - t2 * s_, c - u2 * s_ * 0.6)])
            if f.normal.y > 0: f.normal_flip()
    put("klimop", "klimop", kb)
    # ---------- eilandje van breuksteen + schatkist (Schatkist, Overzicht) ----------
    for k in range(120):
        x, y = rr.uniform(-4.2, 4.4), rr.uniform(-2.4, 2.15)
        if not inside(x, y, ISLAND): continue
        d_wall = WY - y; sc = rr.uniform(0.14, 0.3); z = rr.uniform(-0.05, 0.25) + max(0, 0.35 - 0.12 * d_wall)
        st = bz(-sc, sc, -sc * 0.7, sc * 0.7, -sc * 0.5, sc * 0.55, sc * 0.2)
        for v in st.verts: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * sc * 0.22
        put("eiland", "breuksteen", st, TR(x, y, z, rr.uniform(0, 360)))
    plaat(ISLAND, 0.12, "breuksteen", "eiland", 0.6)
    Mk = TR(-0.15, -1.25, 0.25, 8)
    put("kist", "kist", bz(-0.5, 0.5, -0.3, 0.3, 0.0, 0.42, 0.02), Mk)
    for x in (-0.45, -0.15, 0.15, 0.45): put("kist", "ijzer", bz(x - 0.03, x + 0.03, -0.31, 0.31, 0.0, 0.44), Mk)
    lid = bmesh.new()
    arc = [(0.3 * math.cos(math.pi * k / 8), 0.15 * math.sin(math.pi * k / 8)) for k in range(9)]
    A = [lid.verts.new((-0.5, y, z)) for y, z in arc]; B = [lid.verts.new((0.5, y, z)) for y, z in arc]
    for i in range(8): lid.faces.new((A[i], A[i + 1], B[i + 1], B[i]))
    lid.faces.new(A[::-1]); lid.faces.new(B)
    bmesh.ops.recalc_face_normals(lid, faces=lid.faces)
    put("kist", "kist", lid, Mk @ TR(0, 0.3, 0.42) @ Matrix.Rotation(math.radians(-70), 4, "X") @ TR(0, -0.3, 0))      # half open deksel
    put("kist", "goud", ell((0, 0, 0.42), (0.46, 0.27, 0.12), 12, 8), Mk)                                         # dukaten
    for k in range(40): put("kist", "goud", blathe([(0, 0), (0.04, 0), (0.04, 0.008), (0, 0.01)], 8), Mk @ TR(rr.uniform(-0.4, 0.4), rr.uniform(-0.22, 0.22), 0.48 + rr.uniform(0, 0.05)) @ Matrix.Rotation(rr.uniform(-0.6, 0.6), 4, "X"))
    for k in range(8): put("kist", "juweel", ell((rr.uniform(-0.35, 0.35), rr.uniform(-0.2, 0.2), 0.52), (0.03, 0.03, 0.02), 6, 4), Mk)
    put("kist", "goud", blathe([(0.09, 0), (0.1, 0.06), (0.09, 0.08), (0, 0.08)], 12), Mk @ TR(0.1, -0.05, 0.53))     # kroon
    for k in range(5): a = k * math.tau / 5; put("kist", "goud", btube([(0.1 + 0.09 * math.cos(a), -0.05 + 0.09 * math.sin(a), 0.6), (0.1 + 0.09 * math.cos(a), -0.05 + 0.09 * math.sin(a), 0.67)], 0.012, 4), Mk)
    coll_box(-0.15, -1.25, 0.5, 1.1, 0.7, 1.0, 8)
    # ---------- water + bodem + rand ----------
    plaat(WATER, -0.12, "water", "water", 0.06)
    plaat(WATER, -0.5, "modder", "water", 0.08)
    for a, b in zip(BUITEN, BUITEN[1:]):                                                               # stenen rand langs de buitenkant
        A, B = Vector(a), Vector(b); L = (B - A).length; k = int(L / 0.3)
        for i in range(k + 1):
            p = A.lerp(B, i / max(1, k)); sc = rr.uniform(0.11, 0.16)
            put("water", "rand", bz(-sc, sc, -0.1, 0.1, -0.05, 0.12, 0.03), TR(p.x, p.y, 0.0, math.degrees(math.atan2(B.y - A.y, B.x - A.x))))
    # ---------- hekken: rood Pieck-hek rond de kist, laag groen hekje langs de waterrand ----------
    def hek(pts, mat, h, r, post_every):
        P = [Vector(p) for p in pts]
        for a, b in zip(P, P[1:]):
            put("hek", mat, btube([(a.x, a.y, h), (b.x, b.y, h)], r, 6)); put("hek", mat, btube([(a.x, a.y, h * 0.55), (b.x, b.y, h * 0.55)], r * 0.8, 6))
            m = (a + b) / 2; d = b - a; coll_box(m.x, m.y, 0.5, d.length, 0.15, 1.0, math.degrees(math.atan2(d.y, d.x)))
        for i, p in enumerate(P):
            if i % post_every == 0 or i == len(P) - 1: put("hek", mat, btube([(p.x, p.y, -0.1), (p.x, p.y, h + 0.04)], r * 1.4, 6))
    rood = [(-1.45, -4.35), (-0.75, -3.2), (0.55, -3.2), (1.35, -4.35)]                                  # rood Pieck-hek om de plein-tong tussen de lobben
    hek(rood, "rood", 1.0, 0.035, 1)
    def uit(pts, d=0.28):                                                                            # groen hekje iets buiten de randstenen
        out = []
        for i, p in enumerate(pts):
            a_ = Vector(pts[max(0, i - 1)]); b_ = Vector(pts[min(len(pts) - 1, i + 1)]); t = (b_ - a_).normalized(); n = Vector((t.y, -t.x))
            out.append((p[0] + n.x * d, p[1] + n.y * d))
        return out
    hek(uit([(4.48, 2.21), (6.37, 1.16), (4.27, -3.01), (1.26, -4.16)]), "leuning", 0.55, 0.02, 1)
    hek(uit([(-1.29, -4.14), (-3.95, -2.46), (-5.84, 1.26), (-4.34, 2.2)]), "leuning", 0.55, 0.02, 1)
    # ---------- de draak (Overzicht, Kop, Ruststand): gehurkt bovenop de middenpijler, kop recht naar voren, vleugels wijd, staart rechts omlaag met speerpunt ----------
    MD = Matrix.Translation((0, WY + 0.65, 4.6 + 0.55)) @ Matrix.Scale(1.25, 4)
    def V(x, y, z): return Vector((x, y, z))
    dr = bmesh.new()
    def addd(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); dr.from_mesh(me_); bpy.data.meshes.remove(me_)
    addd(ell(V(0, 0, 0), (0.55, 0.75, 0.5), 16, 12)); addd(ell(V(0, -0.5, 0.2), (0.45, 0.4, 0.45), 14, 10))
    nek = [V(0, -0.55, 0.35), V(0, -0.85, 0.7), V(0, -0.98, 0.98)]
    for i, (a_, b_) in enumerate(zip(nek, nek[1:])): addd(btube([a_, b_], 0.3 - 0.04 * i, 10))
    H = V(0, -1.15, 1.05)
    addd(ell(H, (0.48, 0.45, 0.38), 14, 10)); addd(ell(H + V(0, -0.45, -0.04), (0.32, 0.34, 0.19), 12, 8))          # kop + snuit
    addd(ell(H + V(0, -0.36, -0.27), (0.22, 0.28, 0.08), 10, 6))                                                   # onderkaak (open bek)
    for s_ in (-1, 1):
        for pts in ([(0.35, -0.45, 0.0), (0.5, -0.72, -0.28), (0.45, -0.88, -0.45)], [(0.45, 0.35, -0.1), (0.62, 0.2, -0.38), (0.55, 0.0, -0.46)]):
            P = [V(s_ * p[0], p[1], p[2]) for p in pts]
            for a_, b_ in zip(P, P[1:]): addd(btube([a_, b_], 0.16, 8))
            addd(ell(P[-1] + V(0, -0.08, 0), (0.17, 0.22, 0.08), 8, 6))
    staart = [V(0, 0.7, -0.2), V(0.6, 0.85, -0.35), V(1.2, 0.45, -0.42), V(1.45, -0.2, -0.62), V(1.3, -0.62, -0.95), V(0.95, -0.72, -1.05)]
    for i, (a_, b_) in enumerate(zip(staart, staart[1:])): r_ = 0.22 - 0.032 * i; addd(btube([a_, b_], r_, 10)); addd(ell(b_, (r_, r_, r_), 8, 6))
    bmesh.ops.transform(dr, matrix=MD, verts=dr.verts)
    put("draak", "draak", organisch(dr, 0.022, 3, 0.5, 0.006, 8, 0.5))
    put("draak", "draak", boutline([(0, 0), (0.17, 0.25), (0, 0.5), (-0.17, 0.25)], -0.025, 0.05), MD @ Matrix.Translation(staart[-1]) @ Matrix.Rotation(math.radians(-90), 4, "Y"))   # speerpunt
    put("draak", "buik", ell(V(0, -0.72, 0.05), (0.32, 0.16, 0.36), 10, 8), MD)
    rug = [H + V(0, 0.15, 0.3)] + [p + V(0, 0.08, 0.27) for p in nek[::-1]] + [V(0, y, 0.48 - 0.12 * abs(y)) for y in (-0.3, 0.0, 0.3, 0.6)] + [p + V(0, 0, 0.2) for p in staart[1:4]]
    for p in rug: put("draak", "stekel", blathe([(0, 0), (0.09, 0), (0, 0.32)], 6), MD @ Matrix.Translation(p - V(0, 0, 0.05)))
    for s_ in (-1, 1):
        put("draak", "stekel", blathe([(0, 0), (0.07, 0), (0, 0.38)], 6), MD @ Matrix.Translation(H + V(s_ * 0.22, 0.12, 0.2)) @ Matrix.Rotation(math.radians(s_ * 35), 4, "Y"))   # hoorns
        put("draak", "oog", ell(H + V(s_ * 0.2, -0.25, 0.14), (0.1, 0.08, 0.1), 10, 8), MD)
        put("draak", "zwart", ell(H + V(s_ * 0.21, -0.33, 0.14), (0.025, 0.02, 0.065), 6, 4), MD)
    put("draak", "bek", ell(H + V(0, -0.5, -0.18), (0.2, 0.25, 0.07), 10, 6), MD)
    for k in range(10):
        t = k / 9; x = -0.18 + 0.36 * t; yy = -0.62 + 0.25 * abs(t - 0.5) * 2
        put("draak", "tand", blathe([(0, 0), (0.03, 0), (0, 0.11)], 5), MD @ Matrix.Translation(H + V(x, yy, -0.12)) @ Matrix.Rotation(math.pi, 4, "X"))
        put("draak", "tand", blathe([(0, 0), (0.025, 0), (0, 0.08)], 5), MD @ Matrix.Translation(H + V(x, yy + 0.04, -0.25)))
    put("draak", "bek", btube([H + V(0, -0.5, -0.2), H + V(0, -0.8, -0.3), H + V(0, -0.95, -0.4)], 0.035, 5), MD)
    for s_ in (-1, 1): put("draak", "bek", btube([H + V(0, -0.95, -0.4), H + V(s_ * 0.06, -1.05, -0.44)], 0.02, 4), MD)
    for s_ in (-1, 1):                                                                                  # vleugels: wijd en iets omhoog
        sh = V(s_ * 0.4, 0.1, 0.35); el = V(s_ * 1.3, 0.2, 0.85)
        tips = [V(s_ * 2.3, 0.3, 1.55), V(s_ * 3.3, 0.45, 1.15), V(s_ * 3.1, 0.55, 0.55), V(s_ * 2.0, 0.5, 0.2)]
        put("draak", "draak", btube([sh, el], 0.09, 6), MD)
        for t_ in tips[:3]: put("draak", "draak", btube([el, t_], 0.04, 5), MD)
        vb = bmesh.new(); vs = [vb.verts.new(p) for p in [sh, el] + tips]
        for i in range(1, len(vs) - 1): vb.faces.new((vs[0], vs[i], vs[i + 1]))
        bmesh.ops.solidify(vb, geom=vb.faces[:], thickness=0.03); bmesh.ops.recalc_face_normals(vb, faces=vb.faces)
        put("draak", "vleugel", vb, MD)
    # ---------- sprookjesboek (Boekloc: rechts voor aan de waterrand) + plein ----------
    MB = TR(5.6, -3.4, 0.0, 40)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.035, 6), MB)
    for s in (-1, 1): put("boek", "ijzer", btube([(0, 0, 0.05), (s * 0.12, 0.05, 0.12), (s * 0.22, 0.0, 0.0)], 0.018, 5), MB)
    MBk = MB @ TR(0, 0, 0.9) @ Matrix.Rotation(math.radians(28), 4, "X")
    put("boek", "rood", bz(-0.42, 0.42, -0.28, 0.28, -0.04, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.26, 0.26, 0.0, 0.05, 0.01), MBk)
    coll_box(5.6, -3.4, 0.5, 0.7, 0.5, 1.0, 40)
    plaat(PLEIN, 0.07, "grind", "plein", 0.12, gat=BUITEN)                                              # plein = buitenrand + waterrand (geen grind over het water)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"DR_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": PLEIN, "water": WATER, "eiland": ISLAND}, open(os.path.join(out, "draak_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
