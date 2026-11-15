"""03_nachtegaal De Chinese Nachtegaal (1999-2026, Ton van de Ven; Daan koos deze versie): ommuurd Ming-paleis (OSM 50911622): beige blok met licht
hellende muren, scheurtjes en doorpiepende bakstenen, blauwgroene friesbanden, roze balustrade op de dakrand (Chineseachtergaal1, Intro_nachtegaal),
pagodetorentje boven de uitgang met twee blauwe krulpannendaken, roze balustrade, rode zuiltjes en gouden spits (Bouw_Chinese_Nachtegaal_Toren,
Dakornament), ingangsuitbouw met grijsgroen pannendak en donkere deur (Nachtegaalingang, Voortuin_Uitbouw); ommuurde voortuin met maanpoort in de
noordmuur (Ingang-cn-boog, Nachtegaal2), kronkelend natuurstenen pad (licht grind), zwart grind, lavarotsen, vijvertje, lantaarns, stenen lantaarn,
blauwe potten, bankjes, houten raamwerk op een muurtje (west/zuid), rode dienstdeur; rotsen + watervalletje tegen de noordmuur; uitgangsmuur met poortje.
Frame: oorsprong = zwaartepunt 50911622 = studs (400.32, -526.62); model = OSM gedraaid met -8.2 graden; -Y = zuid, +Y = noord (vijver/Siertuin).
Interieur/show niet (gebouw gesloopt; buitenkant v1). Gebruik: Blender -b -P 03_nachtegaal.py -- --master CN_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.74, 0.68, 0.55, 1), 0.9), "baksteen": ((0.45, 0.42, 0.36, 1), 0.85), "fries": ((0.25, 0.5, 0.48, 1), 0.6), "roze": ((0.85, 0.62, 0.6, 1), 0.6),
        "blauwdak": ((0.2, 0.42, 0.55, 1), 0.5), "groendak": ((0.3, 0.42, 0.36, 1), 0.6), "rood": ((0.6, 0.12, 0.08, 1), 0.5), "goud": ((0.88, 0.66, 0.22, 1), 0.3),
        "donker": ((0.04, 0.035, 0.03, 1), 1.0), "rots": ((0.13, 0.12, 0.12, 1), 0.9), "zwartgrind": ((0.1, 0.1, 0.1, 1), 1.0), "grind": ((0.86, 0.83, 0.76, 1), 0.95),
        "water": ((0.12, 0.2, 0.2, 1), 0.1), "hout": ((0.36, 0.26, 0.16, 1), 0.85), "ijzer": ((0.06, 0.06, 0.06, 1), 0.45), "pot": ((0.08, 0.12, 0.3, 1), 0.3),
        "steen": ((0.6, 0.58, 0.54, 1), 0.85), "papier": ((0.92, 0.86, 0.7, 1), 0.9), "lamp": ((1.0, 0.85, 0.55, 1), 0.3)}
rr = random.Random(1999)
BLOK = [(-5.5, -8.78), (9.3, -8.77), (9.27, 1.67), (12.53, 1.68), (12.53, 7.29), (-5.11, 7.26), (-5.1, 4.17), (-5.5, 4.17)]
TUIN = [(-22.51, 9.1), (-20.46, 10.63), (-18.46, 12.12), (-5.12, 11.84), (-5.1, 7.26), (-5.1, 4.17), (-7.66, 4.17), (-7.66, -3.71), (-5.5, -3.7), (-5.5, -6.2), (-21.2, -6.2)]
PAD = [(-20.46, 10.63), (-18.63, 8.1), (-17.82, 5.44), (-18.07, 2.22), (-18.23, -0.19), (-17.7, -2.3), (-15.84, -2.61), (-13.4, -1.47), (-11.1, -0.73), (-7.66, -0.03)]
VIJVER = [(-16.21, 2.07), (-15.73, 3.04), (-14.83, 3.55), (-13.55, 3.33), (-13.01, 2.4), (-12.95, 1.49), (-13.67, 0.44), (-14.92, 0.4), (-15.88, 0.91)]
UITPAD = [(12.53, 4.37), (14.95, 4.36), (16.19, 6.4), (16.22, 15.45)]
ZB = 7.4                                                       # dakrand paleisblok


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
    def vlak(lussen, to3, depth, nrm):
        flat = [p for l in lussen for p in l]
        tris = tessellate_polygon([[Vector((u, v, 0)) for u, v in l] for l in lussen])
        bm = bmesh.new(); A = [bm.verts.new(to3(u, v)) for u, v in flat]; B = [bm.verts.new(Vector(to3(u, v)) + Vector(nrm) * depth) for u, v in flat]
        for t in tris:
            try: bm.faces.new([A[i] for i in t]); bm.faces.new([B[i] for i in reversed(t)])
            except ValueError: pass
        o = 0
        for l in lussen:
            for i in range(len(l)):
                j = (i + 1) % len(l)
                try: bm.faces.new((A[o + i], A[o + j], B[o + j], B[o + i]))
                except ValueError: pass
            o += len(l)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm
    def segs(poly, closed=True):
        n = len(poly); r = range(n if closed else n - 1)
        for i in r:
            A, B = Vector(poly[i]), Vector(poly[(i + 1) % n]); yield A, B
    def krul_dak(cx, cy, w, z0, z1, ov, curl, part, mat="blauwdak"):    # Chinees schilddak met opkrullende hoeken
        h = w / 2 + ov; N = 8
        bm = bmesh.new(); grid = []
        for j in range(N + 1):
            v = -1 + 2 * j / N; row = []
            for i in range(N + 1):
                u = -1 + 2 * i / N
                r = max(abs(u), abs(v)); z = z1 - (z1 - z0) * (r ** 0.8) + curl * (abs(u) * abs(v)) ** 3
                row.append(bm.verts.new((cx + u * h, cy + v * h, z)))
            grid.append(row)
        for j in range(N):
            for i in range(N): bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f in bm.faces:
            if f.normal.z < 0: f.normal_flip()
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.14); put(part, mat, bm)
        for k in range(N * 2):                                                                 # pannenribbels
            u = -1 + 2 * (k + 0.5) / (N * 2)
            for (a, b) in (((cx + u * h, cy - h), (cx + u * h * 0.15, cy)), ((cx + u * h, cy + h), (cx + u * h * 0.15, cy)), ((cx - h, cy + u * h), (cx, cy + u * h * 0.15)), ((cx + h, cy + u * h), (cx, cy + u * h * 0.15))):
                pa = Vector((a[0], a[1], 0)); pb = Vector((b[0], b[1], 0))
                pts = []
                for t in (0.0, 0.5, 0.9):
                    p = pa.lerp(pb, t); uu, vv = (p.x - cx) / h, (p.y - cy) / h; r = max(abs(uu), abs(vv))
                    pts.append(Vector((p.x, p.y, z1 - (z1 - z0) * (r ** 0.8) + curl * (abs(uu) * abs(vv)) ** 3 + 0.12)))
                put(part, mat, btube(pts, 0.035, 4))
        for sx in (-1, 1):
            for sy in (-1, 1): put(part, "goud", ell((cx + sx * h, cy + sy * h, z0 + curl + 0.12), (0.08, 0.08, 0.08), 6, 4))
    # ---------- paleisblok: licht hellende muren, friesband, balustrade ----------
    wand = bmesh.new()
    def addw(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); wand.from_mesh(me_); bpy.data.meshes.remove(me_)
    cx0 = sum(p[0] for p in BLOK) / len(BLOK); cy0 = sum(p[1] for p in BLOK) / len(BLOK)
    bm = bmesh.new(); n = len(BLOK)
    lo = [bm.verts.new((x, y, -0.1)) for x, y in BLOK]
    hi = [bm.verts.new((x + (cx0 - x) * 0.04, y + (cy0 - y) * 0.04, ZB)) for x, y in BLOK]
    for i in range(n): bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
    tr = tessellate_polygon([[Vector((v.co.x, v.co.y, 0)) for v in hi]])
    for t in tr: bm.faces.new([hi[i] for i in t])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); addw(bm)
    put("blok", "stuc", wand)
    coll_box(3.5, -0.75, ZB / 2, 18.0, 16.0, ZB)
    hiP = [(x + (cx0 - x) * 0.04, y + (cy0 - y) * 0.04) for x, y in BLOK]
    for A, B in segs(hiP):
        L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x); M_ = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
        nrm = Vector((math.sin(ang), -math.cos(ang), 0))                                                     # buitenkant (polygoon tegen de klok in)
        put("blok", "fries", bz(0.2, L_ - 0.2, -0.06, 0.02, ZB - 1.55, ZB - 1.0), M_ @ Matrix.Translation((0, -0.05, 0)))
        for k in range(int(L_ / 2.2)):
            u = 1.1 + k * 2.2
            if u < L_ - 0.8: put("blok", "goud", bz(u - 0.6, u + 0.6, -0.1, -0.05, ZB - 1.45, ZB - 1.1), M_)
        put("blok", "stuc", bz(-0.1, L_ + 0.1, -0.3, 0.2, ZB, ZB + 0.18), M_)                                # dakrandlijst
        put("balu", "roze", bz(0, L_, -0.08, 0.08, ZB + 0.18, ZB + 0.3), M_); put("balu", "roze", bz(0, L_, -0.09, 0.09, ZB + 0.85, ZB + 0.97), M_)
        for k in range(int(L_ / 0.45) + 1):
            u = min(k * 0.45, L_); put("balu", "roze", bz(u - 0.05, u + 0.05, -0.05, 0.05, ZB + 0.3, ZB + 0.85), M_)
        for k in range(int(L_ / 1.8) + 1):
            u = min(k * 1.8, L_); put("balu", "roze", bz(u - 0.1, u + 0.1, -0.1, 0.1, ZB + 0.18, ZB + 1.1), M_)
        put("blok", "baksteen", bz(-0.02, 0.8, -0.12, 0.0, 0.2, ZB - 1.7), M_)                                  # bakstenen hoek-tanding
        for k in range(14):
            z = 0.4 + k * 0.38; wq = 0.55 if k % 2 else 0.95
            put("blok", "baksteen", bz(0.0, wq, -0.16, -0.08, z, z + 0.3), M_)
        for _ in range(int(L_ / 4)):                                                                             # doorpiepende bakstenen
            u = rr.uniform(1.5, L_ - 1.5); z = rr.uniform(0.6, ZB - 2.2)
            for i in range(rr.randint(3, 6)):
                put("blok", "baksteen", bz(u + (i % 2) * 0.25, u + (i % 2) * 0.25 + 0.4, -0.12, -0.04, z + i * 0.2, z + i * 0.2 + 0.16), M_)
    # ---------- pagodetorentje boven de uitgang ----------
    TX, TY = 10.0, 4.4
    put("toren", "stuc", bz(TX - 2.3, TX + 2.3, TY - 2.3, TY + 2.3, ZB, ZB + 2.0))
    for s_ in (-1, 1):
        for t_ in (-1, 1): put("toren", "rood", bz(TX + s_ * 2.0 - 0.14, TX + s_ * 2.0 + 0.14, TY + t_ * 2.0 - 0.14, TY + t_ * 2.0 + 0.14, ZB, ZB + 2.0))
    for side in range(4):
        a = side * math.pi / 2
        M_ = Matrix.Translation((TX, TY, 0)) @ Matrix.Rotation(a, 4, "Z")
        put("toren", "fries", bz(-1.7, 1.7, -2.34, -2.3, ZB + 0.5, ZB + 1.7), M_)
        put("toren", "goud", bz(-1.5, 1.5, -2.38, -2.34, ZB + 0.6, ZB + 0.7), M_); put("toren", "goud", bz(-1.5, 1.5, -2.38, -2.34, ZB + 1.5, ZB + 1.6), M_)
    krul_dak(TX, TY, 4.6, ZB + 2.0, ZB + 3.0, 0.9, 0.6, "toren")
    put("toren", "stuc", bz(TX - 1.4, TX + 1.4, TY - 1.4, TY + 1.4, ZB + 2.8, ZB + 4.3))
    for side in range(4):
        a = side * math.pi / 2; M_ = Matrix.Translation((TX, TY, 0)) @ Matrix.Rotation(a, 4, "Z")
        put("toren", "roze", bz(-1.6, 1.6, -1.65, -1.55, ZB + 3.05, ZB + 3.15), M_); put("toren", "roze", bz(-1.6, 1.6, -1.65, -1.55, ZB + 3.6, ZB + 3.7), M_)
        for k in range(9): u = -1.6 + 0.4 * k; put("toren", "roze", bz(u - 0.04, u + 0.04, -1.63, -1.57, ZB + 3.1, ZB + 3.65), M_)
        put("toren", "donker", bz(-0.6, 0.6, -1.43, -1.4, ZB + 3.3, ZB + 4.1), M_)
    krul_dak(TX, TY, 2.8, ZB + 4.3, ZB + 5.6, 0.75, 0.5, "toren")
    put("toren", "goud", blathe([(0.25, 0), (0.18, 0.3), (0.22, 0.45), (0.1, 0.6), (0.14, 0.75), (0.05, 0.9), (0.04, 1.6), (0.0, 1.7)], 10), Matrix.Translation((TX, TY, ZB + 5.5)))
    for s_ in (-1, 1):                                                                                         # draakjes op de nok
        put("toren", "goud", btube([(TX + s_ * 0.3, TY, ZB + 5.6), (TX + s_ * 0.7, TY, ZB + 5.75), (TX + s_ * 0.9, TY, ZB + 5.55), (TX + s_ * 1.05, TY, ZB + 5.7)], 0.07, 6))
    # ---------- ingangsuitbouw (west), grijsgroen pannendak met gevel naar de tuin ----------
    AX0, AX1, AY0, AY1, AZ = -7.66, -5.4, -3.71, 4.17, 3.0
    ym = (AY0 + AY1) / 2
    addw2 = bmesh.new()
    gevel = [(AY0 - 0.1, -0.1), (AY1 + 0.1, -0.1), (AY1 + 0.1, AZ), (ym, AZ + 2.4), (AY0 - 0.1, AZ)]
    put("uitbouw", "stuc", vlak([gevel, [(ym - 1.15, 0.0), (ym + 1.15, 0.0), (ym + 1.15, 2.5), (ym - 1.15, 2.5)]], lambda u, v: (AX0, u, v), AX1 - AX0, (1, 0, 0)))
    put("uitbouw", "donker", bz(AX0 + 0.3, AX0 + 0.35, ym - 1.15, ym + 1.15, 0.0, 2.5))
    db = bmesh.new()
    for s_ in (-1, 1):
        q = [(AX0 - 0.7, ym + s_ * (ym - AY0 + 0.7), AZ - 0.25), (AX1 + 0.2, ym + s_ * (ym - AY0 + 0.7), AZ - 0.25), (AX1 + 0.2, ym, AZ + 2.55), (AX0 - 0.7, ym, AZ + 2.55)]
        A = [db.verts.new(p) for p in q]; B = [db.verts.new((p[0], p[1], p[2] + 0.18)) for p in q]
        db.faces.new(A); db.faces.new(B[::-1])
        for i in range(4): db.faces.new((A[i], A[(i + 1) % 4], B[(i + 1) % 4], B[i]))
        for k in range(14):
            t = (k + 0.5) / 14; y = ym + s_ * (ym - AY0 + 0.7) * (1 - t); z = AZ - 0.25 + 2.8 * t + 0.22
            put("uitbouw", "groendak", btube([(AX0 - 0.7, y, z), (AX1 + 0.2, y, z)], 0.05, 5))
    bmesh.ops.recalc_face_normals(db, faces=db.faces); put("uitbouw", "groendak", db)
    put("uitbouw", "groendak", btube([(AX0 - 0.75, ym, AZ + 2.8), (AX1 + 0.2, ym, AZ + 2.8)], 0.14, 8))
    put("uitbouw", "groendak", boutline([(-0.5, 0), (-0.15, 0.25), (0.0, 0.0), (0.15, 0.25), (0.5, 0), (0.0, 0.7)], -0.05, 0.1), Matrix.Translation((AX0 - 0.6, ym, AZ + 2.85)) @ Matrix.Rotation(math.pi / 2, 4, "Z"))
    put("uitbouw", "fries", bz(AX0 - 0.72, AX0 - 0.62, AY0 - 0.6, AY1 + 0.6, AZ - 0.45, AZ - 0.25))                # groene ornamentrand
    for k in range(9): yy = AY0 - 0.3 + k * (AY1 - AY0 + 0.6) / 8; put("uitbouw", "goud", ell((AX0 - 0.74, yy, AZ - 0.35), (0.03, 0.09, 0.08), 6, 4))
    for s_ in (-1, 1):
        put("uitbouw", "pot", blathe([(0.2, 0), (0.33, 0.25), (0.36, 0.5), (0.3, 0.75), (0.22, 0.85), (0.24, 0.9), (0.0, 0.9)], 12), Matrix.Translation((AX0 - 0.55, ym + s_ * 1.7, 0)))
        put("uitbouw", "ijzer", bz(AX0 - 0.08, AX0 - 0.02, ym + s_ * 1.5 - 0.05, ym + s_ * 1.5 + 0.05, 1.9, 2.4)); put("uitbouw", "lamp", bz(AX0 - 0.25, AX0 - 0.05, ym + s_ * 1.5 - 0.1, ym + s_ * 1.5 + 0.1, 1.95, 2.25))
    coll_box((AX0 + AX1) / 2, ym + 2.7, 1.5, AX1 - AX0, 2.6, 3.0); coll_box((AX0 + AX1) / 2, ym - 2.7, 1.5, AX1 - AX0, 2.6, 3.0)
    # ---------- tuinmuren: noordmuur met maanpoort, west/zuid muurtje met houten raamwerk, rode dienstdeur ----------
    noord = [(-5.12, 11.84), (-18.46, 12.12), (-20.46, 10.63), (-22.51, 9.1)]
    for A, B in segs(noord, False):
        L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x); M_ = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
        if abs(A.x + 18.46) < 0.1:                                                                              # segment met de maanpoort
            mid = L_ / 2; gat = [(mid + 1.15 * math.cos(k * math.tau / 24), 1.35 + 1.15 * math.sin(k * math.tau / 24)) for k in range(24)]
            put("muren", "stuc", vlak([[(-0.6, -0.1), (L_ + 0.6, -0.1), (L_ + 0.6, 2.9), (-0.6, 2.9)], gat], lambda u, v: (u, 0.0, v), 0.45, (0, 1, 0)), M_ @ Matrix.Translation((0, -0.22, 0)))
            put("muren", "stuc", vlak([[(mid + 1.35 * math.cos(k * math.tau / 24), 1.35 + 1.35 * math.sin(k * math.tau / 24)) for k in range(24)], gat], lambda u, v: (u, 0.0, v), 0.55, (0, 1, 0)), M_ @ Matrix.Translation((0, -0.27, 0)))
            for e in (-0.6, L_ + 0.6):
                put("muren", "stuc", bz(e - 0.3, e + 0.3, -0.35, 0.35, -0.1, 3.4), M_); put("muren", "groendak", bz(e - 0.4, e + 0.4, -0.45, 0.45, 3.4, 3.6), M_)
                put("muren", "ijzer", bz(e - 0.1, e + 0.1, -0.5, -0.35, 2.3, 2.7), M_); put("muren", "lamp", bz(e - 0.08, e + 0.08, -0.62, -0.5, 2.3, 2.6), M_)
            for k in range(int((L_ + 1.2) / 0.3)):
                u = -0.6 + k * 0.3; put("muren", "groendak", btube([(u, -0.4, 2.9), (u, 0, 3.15), (u, 0.4, 2.9)], 0.05, 5), M_)
        else:
            put("muren", "stuc", bz(0, L_, -0.22, 0.22, -0.1, 2.6), M_)
            for k in range(int(L_ / 0.3)):
                u = k * 0.3; put("muren", "groendak", btube([(u, -0.35, 2.6), (u, 0, 2.82), (u, 0.35, 2.6)], 0.05, 5), M_)
            m = (A + B) / 2; coll_box(m.x, m.y, 1.3, L_, 0.45, 2.6, math.degrees(ang))
    raam = [(-22.51, 9.1), (-21.2, -6.2), (-5.5, -6.2)]
    for A, B in segs(raam, False):
        L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x); M_ = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
        put("muren", "stuc", bz(0, L_, -0.2, 0.2, -0.1, 0.7), M_)
        for k in range(int(L_ / 1.6) + 1):
            u = min(k * 1.6, L_); put("muren", "hout", bz(u - 0.07, u + 0.07, -0.07, 0.07, 0.7, 2.3), M_)
        for z in (1.0, 1.5, 2.0, 2.3): put("muren", "hout", bz(0, L_, -0.04, 0.04, z - 0.03, z + 0.03), M_)
        m = (A + B) / 2; coll_box(m.x, m.y, 1.1, L_, 0.4, 2.3, math.degrees(ang))
    put("muren", "stuc", bz(-5.32, -4.9, 7.26, 11.84, -0.1, 2.6)); coll_box(-5.1, 9.55, 1.3, 0.42, 4.6, 2.6)
    put("muren", "rood", bz(-5.36, -5.3, 8.5, 9.4, 0.0, 2.0)); put("muren", "stuc", bz(-5.4, -5.3, 8.3, 9.6, 2.0, 2.3))
    # ---------- tuin: zwart grind, pad, lavarotsen, vijvertje, lantaarns, stenen lantaarn, bankjes, boek ----------
    plaat(TUIN, 0.04, 0.08, "tuin", "zwartgrind")
    pb = bmesh.new(); L_pts = [Vector(p) for p in PAD]
    left, right = [], []
    for i, p in enumerate(L_pts):
        a = L_pts[max(0, i - 1)]; b = L_pts[min(len(L_pts) - 1, i + 1)]; t = (b - a).normalized(); nn = Vector((-t.y, t.x)) * 0.95
        left.append(p + nn); right.append(p - nn)
    poly = [(v.x, v.y) for v in left] + [(v.x, v.y) for v in reversed(right)]
    plaat(poly, 0.08, 0.06, "tuin", "grind")
    for k in range(70):                                                                                         # lavarotsen in groepjes langs het pad
        base = Vector(rr.choice(PAD)); off = Vector((rr.uniform(-3.5, 3.5), rr.uniform(-3.5, 3.5)))
        p = base + off
        if min((p - Vector(q)).length for q in PAD) < 1.3: continue
        sc = rr.uniform(0.18, 0.45); st = bz(-sc, sc, -sc * 0.8, sc * 0.8, 0.0, sc * 1.1, sc * 0.2)
        for v in st.verts: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-0.6, 0.8))) * sc * 0.35
        put("rotsen", "rots", st, TR(p.x, p.y, 0.02, rr.uniform(0, 360)))
    plaat(VIJVER, 0.1, 0.06, "tuin", "water")
    for i in range(len(VIJVER)):
        p = Vector(VIJVER[i]); c = Vector((-14.6, 1.95)); q = c + (p - c) * 1.18; sc = rr.uniform(0.25, 0.4)
        put("rotsen", "rots", bz(-sc, sc, -sc, sc, 0, sc * 1.2, 0.08), TR(q.x, q.y, 0, rr.uniform(0, 90)))
    for (x, y) in ((-19.6, 5.7), (-20.2, 0.5), (-17.0, -3.7), (-12.0, 0.6), (-9.2, -1.4)):
        put("lantaarns", "ijzer", btube([(x, y, 0), (x, y, 1.6)], 0.04, 6)); put("lantaarns", "lamp", bz(x - 0.13, x + 0.13, y - 0.13, y + 0.13, 1.6, 1.9))
        put("lantaarns", "ijzer", blathe([(0.22, 0), (0.0, 0.22)], 6), Matrix.Translation((x, y, 1.9)))
    SL = Matrix.Translation((-8.9, 1.6, 0))
    put("lantaarns", "steen", blathe([(0.28, 0), (0.24, 0.12), (0.1, 0.2), (0.1, 0.65), (0.3, 0.7), (0.3, 0.78), (0.18, 0.8), (0.18, 1.1), (0.35, 1.15), (0.05, 1.4), (0.0, 1.45)], 6), SL)
    for (x, y, a) in ((-20.3, -0.02, 90), (-13.0, -4.26, 0)):
        put("bank", "steen", bz(-0.8, 0.8, -0.25, 0.25, 0.3, 0.42), TR(x, y, 0, a))
        for s_ in (-1, 1): put("bank", "steen", bz(s_ * 0.6 - 0.1, s_ * 0.6 + 0.1, -0.2, 0.2, 0.0, 0.3), TR(x, y, 0, a))
        coll_box(x, y, 0.2, 1.6 if a == 0 else 0.5, 0.5 if a == 0 else 1.6, 0.42)
    for (x, y) in ((-16.2, 6.4), (-11.4, -3.6), (-10.0, 2.6)):
        put("tuin", "pot", blathe([(0.18, 0), (0.28, 0.3), (0.22, 0.45), (0.0, 0.45)], 10), Matrix.Translation((x, y, 0)))
    MB = TR(-9.6, 3.2, 0, 250)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.035, 6), MB)
    MBk = MB @ TR(0, 0, 0.9) @ Matrix.Rotation(math.radians(28), 4, "X")
    put("boek", "rood", bz(-0.42, 0.42, -0.28, 0.28, -0.04, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.26, 0.26, 0.0, 0.05, 0.01), MBk)
    # ---------- rotsen + watervalletje tegen de noordmuur (Siertuinkant) ----------
    rw = bmesh.new()
    for k in range(16):
        x = rr.uniform(-2.5, 4.5); y = rr.uniform(7.4, 9.6); h = rr.uniform(0.6, 2.8) * (1.4 if abs(x - 1) < 1.2 else 1.0)
        b_ = bz(x - rr.uniform(0.5, 0.9), x + rr.uniform(0.5, 0.9), y - 0.6, y + 0.6, -0.1, h, 0.1)
        for v in b_.verts: v.co += Vector((rr.uniform(-0.2, 0.2), rr.uniform(-0.2, 0.2), rr.uniform(-0.2, 0.2)))
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); rw.from_mesh(me_); bpy.data.meshes.remove(me_)
    put("waterval", "rots", organisch(rw, 0.09, 2, 0.5, 0.12, 1.0, 0.3))
    put("waterval", "water", bz(0.6, 1.5, 9.65, 9.75, 0.3, 3.4)); plaat([(-1.5, 9.6), (3.6, 9.6), (3.8, 11.2), (-1.7, 11.2)], 0.1, 0.06, "waterval", "water")
    coll_box(1.0, 8.5, 1.2, 7.2, 2.4, 2.4)
    # ---------- uitgangspad + uitgangsmuur met poortje ----------
    uit = [(21.79, 15.0), (16.22, 15.45), (7.97, 15.47), (8.02, 12.11)]
    for A, B in segs(uit, False):
        L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x); M_ = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
        if abs(A.x - 21.79) < 0.1: L1 = L_ - 0.8
        else: L1 = L_
        put("muren", "stuc", bz(0, L1, -0.2, 0.2, -0.1, 2.4), M_)
        for k in range(int(L1 / 0.3)): u = k * 0.3; put("muren", "groendak", btube([(u, -0.32, 2.4), (u, 0, 2.6), (u, 0.32, 2.4)], 0.05, 5), M_)
        m = A.lerp(B, L1 / 2 / L_); coll_box(m.x, m.y, 1.2, L1, 0.4, 2.4, math.degrees(ang))
    put("muren", "stuc", vlak([[(-0.9, -0.1), (0.9, -0.1), (0.9, 3.0), (0.0, 3.5), (-0.9, 3.0)], [(-0.6, 0.0), (0.6, 0.0), (0.6, 2.2), (0.0, 2.6), (-0.6, 2.2)]], lambda u, v: (16.22 + u, 15.25, v), 0.4, (0, 1, 0)))
    pts = [Vector(p) for p in UITPAD]; left, right = [], []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]; t = (b - a).normalized(); nn = Vector((-t.y, t.x)) * 1.1
        left.append(p + nn); right.append(p - nn)
    plaat([(v.x, v.y) for v in left] + [(v.x, v.y) for v in reversed(right)], 0.07, 0.1, "uitpad", "grind")
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"CN_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "tuin": TUIN, "blok": BLOK, "pad": PAD}, open(os.path.join(out, "nachtegaal_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
