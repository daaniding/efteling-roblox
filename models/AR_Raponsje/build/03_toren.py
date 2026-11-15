"""03_toren De toren van Raponsje (2001): achtkantige gegroefde stucschacht met spitsboogfries, overkragende vakwerkverdieping met raam, spanendak, windvaan,
vlecht, rotsige sokkel + ruinemuur, vijvertje met keienrand en leuning, klimop, sprookjesboek. Maten: Tvdv-ontwerptekening (98 px/m, 10.01 m) - asset-brief.md.
Frame: oorsprong midden OSM 55423664, model = OSM-assen, -Y = zuid (raam naar het pad), z 0 = maaiveld. Gebruik: Blender -b -P 03_toren.py -- --master RA_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.88, 0.87, 0.84, 1), 0.9), "baksteen": ((0.55, 0.32, 0.25, 1), 0.9), "hout": ((0.3, 0.2, 0.13, 1), 0.8), "vakvlak": ((0.86, 0.84, 0.78, 1), 0.9),
        "lei": ((0.36, 0.3, 0.24, 1), 0.85), "rots": ((0.5, 0.48, 0.45, 1), 0.95), "ijzer": ((0.06, 0.06, 0.06, 1), 0.45), "glas": ((0.55, 0.62, 0.4, 1), 0.2),
        "venster": ((0.04, 0.04, 0.04, 1), 0.3), "vlecht": ((0.92, 0.82, 0.55, 1), 0.7), "klimop": ((0.14, 0.26, 0.12, 1), 0.7), "rank": ((0.25, 0.2, 0.15, 1), 0.9),
        "water": ((0.1, 0.14, 0.09, 1), 0.1), "modder": ((0.12, 0.1, 0.07, 1), 1.0), "leuning": ((0.2, 0.36, 0.38, 1), 0.6), "papier": ((0.92, 0.86, 0.7, 1), 0.9),
        "rood": ((0.62, 0.1, 0.1, 1), 0.5), "grind": ((0.86, 0.83, 0.76, 1), 0.95)}
N8 = 8
R0, R1 = 1.17, 1.12            # schacht halve breedte (over de vlakken) onder / boven (tekening 2.33 / 2.25 m)
Z0, Z1 = 0.9, 5.9              # schacht van sokkel tot boogfries-top
ZV0, ZV1 = 6.2, 7.4            # vakwerk
RV = 1.25                      # vakwerk halve breedte
EAVE_R, APEX, BOL, VAAN = 1.47 / math.cos(math.pi / 8), 8.6, 9.1, 10.01
WATER = [(-1.43, 1.16), (-1.96, 1.55), (-2.85, 0.52), (-3.03, -0.92), (-2.12, -2.46), (-0.15, -3.09), (1.28, -2.72), (2.06, -1.7), (1.53, -1.2), (1.03, -1.63),
         (0.41, -1.86), (-0.24, -1.87), (-0.87, -1.66), (-1.38, -1.24), (-1.71, -0.71), (-1.84, -0.07), (-1.74, 0.58)]
rr = random.Random(2001)


def oct_pts(r, z, rot=math.pi / 8):
    """achthoek met een VLAK naar -Y (r = afstand tot het vlak)"""
    R = r / math.cos(math.pi / 8)
    return [(R * math.cos(rot - math.pi / 2 + k * math.tau / 8), R * math.sin(rot - math.pi / 2 + k * math.tau / 8), z) for k in range(8)]


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ---------- schacht: per zijde een holle groef (concaaf vlak) tussen ribben, bovenaan spitsboogjes (Tvdv, Intro) ----------
    sch = bmesh.new()
    def add(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); sch.from_mesh(me_); bpy.data.meshes.remove(me_)
    nz, nu = 24, 10
    rings = []
    for iz in range(nz + 1):
        z = Z0 - 0.3 + (Z1 - Z0 + 0.3) * iz / nz; t = (z - Z0 + 0.3) / (Z1 - Z0 + 0.3); r = R0 + (R1 - R0) * t
        ring = []
        for k in range(8):
            a0 = -math.pi / 2 + (k - 0.5) * math.tau / 8
            for iu in range(nu):
                u = iu / nu; a = a0 + u * math.tau / 8
                Rc = r / math.cos(math.pi / 8) * (1 - 0.0) ; flat = r / math.cos(abs(u - 0.5) * math.tau / 8)
                depth = 0.13 * math.sin(math.pi * u) ** 0.7 * (0.0 if z > Z1 - 0.55 else 1.0)                  # groef, bovenaan dicht (boogjes)
                rad = flat - depth + 0.015 * noise.noise(Vector((math.cos(a) * 3, math.sin(a) * 3, z * 1.3)))
                ring.append(Vector((rad * math.cos(a), rad * math.sin(a), z)))
        rings.append(ring)
    V = [[sch.verts.new(p) for p in ring] for ring in rings]; M_ = len(V[0])
    for A, B in zip(V, V[1:]):
        for i in range(M_): sch.faces.new((A[i], A[(i + 1) % M_], B[(i + 1) % M_], B[i]))
    sch.faces.new(V[-1]); bmesh.ops.recalc_face_normals(sch, faces=sch.faces)
    put("schacht", "stuc", sch)
    # spitsboogfries: per zijde een spitsboogje als verdiepte nis net onder de vakwerkvloer + kraag
    for k in range(8):
        a = -math.pi / 2 + k * math.tau / 8
        c = Vector((math.cos(a), math.sin(a), 0)); tng = Vector((-math.sin(a), math.cos(a), 0))
        Mk = Matrix(((tng.x, 0, c.x, 0), (tng.y, 0, c.y, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
        pts = [(-0.32, Z1 - 0.62)] + [(-0.32 + 0.32 * (1 - math.cos(t * math.pi / 2)) ** 0.8 * 1.0, Z1 - 0.62 + 0.42 * math.sin(t * math.pi / 2)) for t in [i / 6 for i in range(1, 7)]]
        pts = pts + [(-x, z) for x, z in pts[::-1]]
        bm = boutline([(x, z) for x, z in pts], 0, 0.02)
        bmesh.ops.transform(bm, matrix=Matrix.Translation(c * (R1 - 0.005)) @ Mk @ Matrix.Rotation(math.radians(0), 4, "X"), verts=bm.verts)
        for v in bm.verts: v.co.z = v.co.z      # al in z
        put("fries", "venster", bm)
    put("fries", "stuc", blathe([(R1 / math.cos(math.pi / 8) + 0.02, Z1 - 0.12), (RV / math.cos(math.pi / 8) - 0.02, Z1 + 0.05), (RV / math.cos(math.pi / 8) - 0.02, ZV0 - 0.02), (0, ZV0 - 0.02), (0, Z1 - 0.12)], 8))
    # kale baksteenplekken in het stuc (Tvdv, Boekloc)
    for (a_deg, z, w, h) in ((-115, 4.6, 0.5, 0.35), (-70, 3.3, 0.45, 0.4), (-95, 2.1, 0.35, 0.25), (-30, 5.1, 0.4, 0.3), (-150, 2.8, 0.4, 0.35), (150, 4.0, 0.5, 0.4), (40, 2.5, 0.4, 0.3)):
        a = math.radians(a_deg); c = Vector((math.cos(a), math.sin(a), 0)); tng = Vector((-math.sin(a), math.cos(a), 0)); r = R0 + (R1 - R0) * (z - Z0) / (Z1 - Z0)
        p0 = c * (r - 0.005) + Vector((0, 0, z))
        for row in range(int(h / 0.08)):
            off = 0.06 if row % 2 else 0.0
            for col in range(int(w / 0.22)):
                q = p0 + tng * (-w / 2 + off + col * 0.22) + Vector((0, 0, -h / 2 + row * 0.08))
                bb = bz(-0.1, 0.1, -0.012, 0.012, -0.034, 0.034, 0.005)
                M2 = Matrix.Translation(q) @ Matrix(((tng.x, c.x, 0, 0), (tng.y, c.y, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
                put("baksteen", "baksteen", bb, M2)
    coll_box(0, 0, (Z1 + Z0) / 2, 2 * R0, 2 * R0, Z1 - Z0 + 1.0)
    # ---------- vakwerkverdieping: achtkant, overkragend, dikke balken, vakken gestuct; raam voor (Meisje_raponsje) ----------
    put("vakwerk", "hout", blathe([(RV / math.cos(math.pi / 8) + 0.08, ZV0 - 0.3), (RV / math.cos(math.pi / 8) + 0.1, ZV0), (0, ZV0), (0, ZV0 - 0.3)], 8))   # vloerbalken
    put("vakwerk", "vakvlak", blathe([(RV / math.cos(math.pi / 8), ZV0), (RV / math.cos(math.pi / 8), ZV1), (0, ZV1), (0, ZV0)], 8))
    P8 = oct_pts(RV + 0.025, 0)
    for k in range(8):
        a = Vector(P8[k][:2]); b = Vector(P8[(k + 1) % 8][:2])
        put("vakwerk", "hout", btube([(a.x, a.y, ZV0), (a.x, a.y, ZV1)], 0.07, 4))                               # hoekstijlen
        for z in (ZV0 + 0.05, ZV0 + 0.55, ZV1 - 0.05): put("vakwerk", "hout", btube([(a.x, a.y, z), (b.x, b.y, z)], 0.05, 4))
        m = (a + b) / 2
        if k != 0:                                                                                                # schoren (niet op de raamzijde)
            put("vakwerk", "hout", btube([(a.x, a.y, ZV0 + 0.55), (m.x, m.y, ZV1 - 0.05)], 0.04, 4)); put("vakwerk", "hout", btube([(m.x, m.y, ZV0 + 0.05), (m.x, m.y, ZV0 + 0.55)], 0.04, 4))
    for k in range(8):                                                                                            # consoles onder de overkraging
        a = -math.pi / 2 + (k + 0.5) * math.tau / 8; c = Vector((math.cos(a), math.sin(a)))
        put("vakwerk", "hout", btube([(c.x * R1, c.y * R1, ZV0 - 0.75), (c.x * (R1 + 0.05), c.y * (R1 + 0.05), ZV0 - 0.4), (c.x * (RV + 0.1), c.y * (RV + 0.1), ZV0 - 0.15)], 0.06, 5))
    # raam (zuidzijde = vlak naar -Y): rondboog met glas-in-lood boogje, luik open, plank-vensterbank, haak
    yf = -(RV + 0.03); wx = 0.32; wz0, wz1 = ZV0 + 0.25, ZV1 - 0.1
    put("raam", "venster", bz(-wx, wx, yf - 0.01, yf + 0.02, wz0, wz1 - 0.25))
    put("raam", "glas", boutline([(-wx, wz1 - 0.25)] + [(-wx * math.cos(math.pi * i / 10), wz1 - 0.25 + 0.22 * math.sin(math.pi * i / 10)) for i in range(11)], yf - 0.02, 0.02))
    put("raam", "hout", band([(-wx * math.cos(math.pi * i / 10), wz1 - 0.25 + 0.22 * math.sin(math.pi * i / 10)) for i in range(11)][::-1], 0.06, yf - 0.04, 0.05))
    for s in (-1, 1): put("raam", "hout", bz(s * wx - 0.04, s * wx + 0.04, yf - 0.04, yf + 0.01, wz0, wz1 - 0.25))
    put("raam", "hout", bz(-wx - 0.15, wx + 0.15, yf - 0.55, yf + 0.02, wz0 - 0.06, wz0))                       # uitstekende plank
    put("raam", "hout", bz(wx + 0.02, wx + 0.42, yf - 0.06, yf - 0.02, wz0, wz1 - 0.2))                         # open luik
    put("raam", "ijzer", btube([(-wx - 0.3, yf - 0.02, wz1 - 0.15), (-wx - 0.3, yf - 0.18, wz1 - 0.2), (-wx - 0.3, yf - 0.22, wz1 - 0.42), (-wx - 0.3, yf - 0.12, wz1 - 0.5)], 0.02, 5))   # haak
    # vlecht: van de vensterbank over de plank naar beneden tot ~1.9 m (Boekloc)
    vl = [Vector((0.02, yf - 0.4, wz0 + 0.02)), Vector((0.03, yf - 0.56, wz0 - 0.08))] + [Vector((0.03 + 0.02 * math.sin(i), yf - 0.58, wz0 - 0.08 - 0.42 * i)) for i in range(1, 11)]
    for a_, b_ in zip(vl, vl[1:]): put("vlecht", "vlecht", btube([a_, b_], 0.045, 6))
    for i in range(len(vl) - 1):
        m = (vl[i] + vl[i + 1]) / 2
        for k in range(2): put("vlecht", "vlecht", ell(m + Vector((0.02 * (-1) ** k, 0, 0.1 * k)), (0.05, 0.05, 0.09), 6, 4))
    # ---------- dak: achtkantig spanendak met overstek, bol, windvaan ----------
    E8 = oct_pts(1.47, ZV1)
    bm = bmesh.new(); vs = [bm.verts.new(p) for p in E8]; ap = bm.verts.new((0, 0, APEX))
    for k in range(8): bm.faces.new((vs[k], vs[(k + 1) % 8], ap))
    bm.faces.new(vs[::-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("dak", "lei", bm)
    for j in range(1, 9):                                                                                         # spanenrijen
        t = j / 9; ring = [Vector(p) * (1 - t) + Vector((0, 0, APEX)) * t + Vector((0, 0, 0.005)) for p in E8]
        for k in range(8): put("dak", "lei", btube([ring[k], ring[(k + 1) % 8]], 0.018, 4))
    for k in range(8): put("dak", "hout", btube([E8[k], (0, 0, APEX)], 0.04, 4))                               # graatlatten
    put("dak", "ijzer", blathe([(0.0, 0), (0.08, 0), (0.15, 0.12), (0.17, 0.25), (0.12, 0.38), (0.05, 0.45), (0.03, 0.5), (0, 0.5)], 12), TR(0, 0, APEX - 0.05))
    put("vaan", "ijzer", btube([(0, 0, BOL - 0.1), (0, 0, VAAN)], 0.018, 6))
    put("vaan", "ijzer", btube([(-0.55, 0, 9.55), (0.55, 0, 9.55)], 0.012, 4)); put("vaan", "ijzer", bz(-0.62, -0.5, -0.006, 0.006, 9.5, 9.6))
    put("vaan", "ijzer", btube([(0, -0.15, 9.45), (0, 0.15, 9.45)], 0.01, 4))
    bird = [(0.0, 0.0), (0.25, 0.05), (0.42, 0.28), (0.35, 0.05), (0.55, 0.0), (0.3, -0.06), (0.05, -0.05)]       # vogel op de pijl
    put("vaan", "ijzer", boutline(bird, -0.01, 0.02), TR(0.05, 0, 9.62))
    # ---------- sokkel: ruw gestapelde rotsen + stucen ruinemuur voor (Tvdv, Boekloc) ----------
    for k in range(34):
        a = rr.uniform(0, math.tau); r = rr.uniform(1.15, 1.7); sc = rr.uniform(0.25, 0.5)
        st = ell((0, 0, 0), (sc * rr.uniform(0.9, 1.3), sc * rr.uniform(0.7, 1.0), sc * rr.uniform(0.5, 0.8)), 8, 6)
        for v in st.verts: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * sc * 0.2
        put("sokkel", "rots", st, TR(r * math.cos(a), r * math.sin(a), rr.uniform(0.05, 0.9), rr.uniform(0, 360)))
    put("sokkel", "rots", blathe([(1.62, -0.1), (1.55, 0.5), (1.3, 0.95), (0, 0.95), (0, -0.1)], 8))
    rm = [(-1.45, 0.0), (-1.45, 1.55), (-1.15, 1.85), (-0.7, 1.72), (-0.3, 1.9), (0.15, 1.6), (0.55, 1.45), (0.9, 1.15), (1.15, 1.2), (1.3, 0.0)]   # ruinemuur, getrapte breukrand
    put("ruine", "stuc", organisch(boutline(rm, -1.95, 0.35), 0.04, 2, 0.4, 0.02, 1.4, 0.4))
    for (x, z) in ((-1.2, 1.65), (-0.45, 1.75), (0.35, 1.5), (1.0, 1.15), (-1.4, 0.9), (1.25, 0.5)):
        st = ell((0, 0, 0), (0.16, 0.12, 0.1), 6, 4); put("ruine", "rots", st, TR(x, -1.8, z, rr.uniform(0, 90)))
    for row in range(3):                                                                                          # baksteenplek in de ruine
        for col in range(3): put("ruine", "baksteen", bz(-0.1, 0.1, -0.012, 0.012, -0.034, 0.034, 0.005), TR(-0.1 + col * 0.22 + (0.11 if row % 2 else 0), -1.965, 1.2 + row * 0.08))
    coll_box(-0.07, -1.78, 0.9, 2.75, 0.4, 1.8)
    # ---------- klimopranken (Tvdv, Boekloc) ----------
    def rank(pts, r0):
        for a_, b_, i in zip(pts, pts[1:], range(len(pts))): put("rank", "rank", btube([a_, b_], r0 * (1 - 0.6 * i / len(pts)), 5))
    def opp(a_deg, z, d=0.02):
        a = math.radians(a_deg); r = R0 + (R1 - R0) * max(0, (z - Z0)) / (Z1 - Z0); return Vector((math.cos(a) * (r + d), math.sin(a) * (r + d), z))
    R1p = [opp(-150, 1.0), opp(-135, 2.0), opp(-115, 3.0), opp(-95, 3.7), opp(-70, 4.3), opp(-55, 5.2)]
    R2p = [opp(-35, 0.9), opp(-45, 1.8), opp(-60, 2.6), opp(-75, 3.3), opp(-90, 3.9)]
    rank(R1p, 0.05); rank(R2p, 0.04)
    def bij_rank(p):
        best = 9
        for poly in (R1p, R2p):
            for a_, b_ in zip(poly, poly[1:]):
                d = b_ - a_; t = max(0, min(1, (p - a_).dot(d) / d.length_squared)); best = min(best, (p - (a_ + d * t)).length)
        return best
    kb = bmesh.new()
    for _ in range(6000):
        a_deg = rr.uniform(-170, -20); z = rr.uniform(1.0, 5.4)
        c = opp(a_deg, z, 0.05)
        if bij_rank(c) > 0.32: continue                                                   # alleen langs de ranken (Tvdv)
        n = Vector((math.cos(math.radians(a_deg)), math.sin(math.radians(a_deg)), 0))
        t = n.cross(Vector((0, 0, 1))).normalized(); u = Vector((0, 0, 1)); s_ = rr.uniform(0.06, 0.11); ang = rr.uniform(0, math.tau)
        t2 = t * math.cos(ang) + u * math.sin(ang); u2 = -t * math.sin(ang) + u * math.cos(ang)
        f = kb.faces.new([kb.verts.new(p) for p in (c + t2 * s_, c + u2 * s_ * 1.2 + n * 0.02, c - t2 * s_, c - u2 * s_ * 0.6)])
        if f.normal.dot(n) < 0: f.normal_flip()
    put("klimop", "klimop", kb)
    # ---------- vijvertje (OSM 766787183) met water, keienrand en lage leuning (Boekloc) ----------
    def plaat(poly, z, mat, part, dz):
        bm = bmesh.new(); t_ = [bm.verts.new((x, y, z)) for x, y in poly]; b_ = [bm.verts.new((x, y, z - dz)) for x, y in poly]
        ft = bm.faces.new(t_); fb_ = bm.faces.new(b_[::-1])
        for i in range(len(poly)): bm.faces.new((t_[i], b_[i], b_[(i + 1) % len(poly)], t_[(i + 1) % len(poly)]))
        bmesh.ops.triangulate(bm, faces=[ft, fb_], ngon_method="EAR_CLIP"); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f_ in bm.faces:
            if abs(f_.normal.z) > 0.5 and (f_.calc_center_median().z > z - dz / 2) != (f_.normal.z > 0): f_.normal_flip()
        put(part, mat, bm)
    plaat(WATER, -0.12, "water", "vijver", 0.06)
    plaat([(x * 1.03, y * 1.03) for x, y in WATER], -0.45, "modder", "vijver", 0.08)
    buiten = [(-1.96, 1.55), (-2.85, 0.52), (-3.03, -0.92), (-2.12, -2.46), (-0.15, -3.09), (1.28, -2.72), (2.06, -1.7)]
    for a_, b_ in zip(buiten, buiten[1:]):                                                                        # keienrand rond de buitenkant
        A, B = Vector(a_), Vector(b_); L = (B - A).length; k = int(L / 0.32)
        for i in range(k + 1):
            p = A.lerp(B, i / max(1, k)); n = (p - Vector((-0.6, -0.9))).normalized() * 0.12; sc = rr.uniform(0.13, 0.2)
            st = ell((0, 0, 0), (sc * 1.2, sc, sc * 0.7), 7, 5)
            for v in st.verts: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * sc * 0.15
            put("vijver", "rots", st, TR(p.x + n.x, p.y + n.y, 0.06, rr.uniform(0, 360)))
    rail = [(Vector(p) + (Vector(p) - Vector((-0.6, -0.9))).normalized() * 0.45) for p in buiten]
    for a_, b_ in zip(rail, rail[1:]):
        put("leuning", "leuning", btube([(a_.x, a_.y, 0.55), (b_.x, b_.y, 0.55)], 0.02, 6))
        m = (a_ + b_) / 2; d = b_ - a_; coll_box(m.x, m.y, 0.45, d.length, 0.15, 0.9, math.degrees(math.atan2(d.y, d.x)))
    for p in rail: put("leuning", "leuning", btube([(p.x, p.y, 0.0), (p.x, p.y, 0.6)], 0.025, 6))
    # ---------- sprookjesboek op standaard (Boekloc: links voor, aan het pad) ----------
    MB = TR(-3.4, -3.9, 0.0, -25)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.035, 6), MB)
    for s in (-1, 1): put("boek", "ijzer", btube([(0, 0, 0.05), (s * 0.12, 0.05, 0.12), (s * 0.22, 0.0, 0.0)], 0.018, 5), MB)
    MBk = MB @ TR(0, 0, 0.9) @ Matrix.Rotation(math.radians(28), 4, "X")
    put("boek", "rood", bz(-0.42, 0.42, -0.28, 0.28, -0.04, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.26, 0.26, 0.0, 0.05, 0.01), MBk)
    coll_box(-3.4, -3.9, 0.5, 0.7, 0.5, 1.0, -25)
    # ---------- strook licht grind tussen leuning en pad 405848924 (y ~ -6) ----------
    plaat([(-4.4, -2.6), (-3.5, -3.3), (-0.2, -3.75), (1.6, -3.3), (2.8, -2.3), (3.6, -3.4), (2.6, -4.9), (-0.4, -5.1), (-4.6, -4.6)], 0.07, "grind", "plein", 0.12)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"RA_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": [(-4.4, -2.6), (-3.5, -3.3), (-0.2, -3.75), (1.6, -3.3), (2.8, -2.3), (3.6, -3.4), (2.6, -4.9), (-0.4, -5.1), (-4.6, -4.6)],
               "water": WATER}, open(os.path.join(out, "raponsje_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
