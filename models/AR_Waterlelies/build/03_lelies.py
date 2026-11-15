"""03_lelies De Indische Waterlelies (1966, Anton Pieck / Peter Reijnders): helwit oosters voorplein (OSM 55441203) met rechthoekige vijver (55441202,
15.6 x 10.3 m) met witte rand en gouden lotusfontein, twee tempelwachters op witte sokkels met knots (Indischewaterlelies-voorplein-mei09, Iwplein77),
gaanderij met witte zuilen onder een overhangende grijze rotsmassa met leeuwenschilden tegen de achterwand (Waterlelies_Voorplein_2024, Lelies_leeuw),
witte muren rond het plein met bankjes en varenborders, grote dubbele deur met de Simurgh in de westmuur, rotstunnel met gouden naambord als toegang
(556674121, Waterlelies_Ingang_2024), groene showloods erachter (279667940; interieur/show later), grindplein.
Frame: oorsprong = midden vijver = OSM-park-m (36.66, 117.29) = studs (109.98, -351.87); model = OSM gedraaid met -12.3 graden; +Y = noord (gaanderij),
-Y = zuid. Gebruik: Blender -b -P 03_lelies.py -- --master WL_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.9, 0.9, 0.87, 1), 0.85), "rots": ((0.36, 0.37, 0.37, 1), 0.85), "water": ((0.32, 0.4, 0.36, 1), 0.1), "goud": ((0.88, 0.66, 0.22, 1), 0.3),
        "rood": ((0.66, 0.14, 0.08, 1), 0.5), "groen": ((0.12, 0.3, 0.22, 1), 0.6), "donker": ((0.12, 0.12, 0.12, 1), 0.9), "hout": ((0.32, 0.22, 0.14, 1), 0.8),
        "loods": ((0.16, 0.26, 0.18, 1), 0.7), "huid": ((0.85, 0.62, 0.4, 1), 0.5), "wit": ((0.95, 0.94, 0.9, 1), 0.5), "zwart": ((0.03, 0.03, 0.03, 1), 0.3),
        "grind": ((0.86, 0.83, 0.76, 1), 0.95), "modder": ((0.16, 0.12, 0.08, 1), 1.0), "blauw": ((0.2, 0.35, 0.55, 1), 0.5)}
rr = random.Random(1966)
VIJVER = [(7.83, 5.12), (7.77, -5.31), (-7.9, -5.09), (-7.67, 5.11)]
PLEIN = [(9.19, 5.12), (9.57, -9.21), (9.61, -10.92), (15.66, -12.72), (15.55, -15.8), (-16.43, -15.97), (-16.48, -8.1), (-16.5, 5.1), (-9.78, 5.1), (-7.67, 5.11), (7.83, 5.12)]
LOODS = [(4.4, 10.0), (4.4, 30.2), (19.66, 31.24), (31.66, 31.24), (31.71, 19.15), (8.32, 11.63), (8.32, 10.0)]
GANG = [(31.71, 19.15), (42.0, 19.9), (42.0, 16.9), (38.2, 16.4), (41.1, 15.6), (47.1, 10.6), (48.4, 10.56), (54.6, 6.3), (58.9, 5.3), (58.9, 2.35), (55.7, 2.5),
        (48.9, 7.2), (46.9, 7.35), (41.1, 11.3), (39.4, 11.66), (23.86, 11.64), (15.51, 11.64), (8.32, 11.63)]
GY0, GY1, GX0, GX1 = 5.4, 10.0, -12.5, 9.2            # gaanderij (strook tussen vijver en loods, OSM 1395767223)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    def plaat(poly, z, dz, part, mat, gat=None):
        lus = [poly] + ([gat] if gat else []); flat = [p for l in lus for p in l]
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
    def merge_into(dst, b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); dst.from_mesh(me_); bpy.data.meshes.remove(me_)
    def rotsblok(dst, x0, x1, y0, y1, z0, z1, n=1, j=0.35):
        for _ in range(n):
            b_ = bz(x0, x1, y0, y1, z0, z1, 0.1)
            for v in b_.verts: v.co += Vector((rr.uniform(-j, j), rr.uniform(-j, j), rr.uniform(-j, j)))
            merge_into(dst, b_)
    # ---------- vijver: witte rand, water, gouden lotusfontein ----------
    VX0, VX1, VY0, VY1 = -7.85, 7.8, -5.2, 5.12
    for (a, b) in ((( VX0, VY0), (VX1, VY0)), ((VX1, VY0), (VX1, VY1)), ((VX1, VY1), (VX0, VY1)), ((VX0, VY1), (VX0, VY0))):
        A, B = Vector(a), Vector(b); L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x)
        M_ = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
        put("vijver", "stuc", bz(-0.2, L_ + 0.2, -0.2, 0.2, -0.3, 0.42), M_); put("vijver", "stuc", bz(-0.25, L_ + 0.25, -0.27, 0.27, 0.42, 0.5), M_)
        m = (A + B) / 2; coll_box(m.x, m.y, 0.25, L_ + 0.4, 0.5, 0.5, math.degrees(ang))
    plaat([(VX0 + 0.2, VY0 + 0.2), (VX1 - 0.2, VY0 + 0.2), (VX1 - 0.2, VY1 - 0.2), (VX0 + 0.2, VY1 - 0.2)], 0.3, 0.05, "vijver", "water")
    plaat([(VX0 + 0.2, VY0 + 0.2), (VX1 - 0.2, VY0 + 0.2), (VX1 - 0.2, VY1 - 0.2), (VX0 + 0.2, VY1 - 0.2)], -0.2, 0.05, "vijver", "modder")
    F0 = Matrix.Translation((-0.6, 0.23, 0))
    put("fontein", "goud", blathe([(0.18, 0.2), (0.14, 0.7), (0.1, 0.75), (0.0, 0.75)], 12), F0)
    for ring, (r0, h, n_) in enumerate(((0.75, 0.75, 10), (0.5, 0.95, 8), (0.28, 1.15, 6))):
        for k in range(n_):
            a = k * math.tau / n_ + ring * 0.3
            pet = boutline([(-0.12, 0.0), (0.0, -0.02), (0.12, 0.0), (0.07, 0.35), (0.0, 0.5), (-0.07, 0.35)], -0.015, 0.03)
            put("fontein", "goud", pet, F0 @ Matrix.Translation((0, 0, h - 0.05)) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Translation((0, r0 * 0.45, 0)) @ Matrix.Rotation(math.radians(-55 + ring * 15), 4, "X"))
    put("fontein", "goud", ell((0, 0, 1.3), (0.08, 0.08, 0.12), 8, 6), F0)
    coll_box(-0.6, 0.23, 0.6, 0.6, 0.6, 1.2)
    # beeldje in de vijver (OSM artwork): gouden reiger op een sokkel
    MR = Matrix.Translation((-6.82, 0.01, 0))
    put("fontein", "stuc", bz(-0.3, 0.3, -0.3, 0.3, 0.0, 0.6), MR); put("fontein", "goud", ell((0, 0, 1.0), (0.12, 0.25, 0.16), 8, 6), MR)
    put("fontein", "goud", btube([(0, -0.15, 1.05), (0, -0.25, 1.45), (0, -0.4, 1.5)], 0.035, 6), MR); put("fontein", "goud", btube([(0.05, 0, 0.6), (0.05, 0, 0.88)], 0.02, 4), MR)
    # ---------- gaanderij: witte zuilen, hoofdgestel, achterwand met leeuwenschilden, overhangende rotsmassa ----------
    zx = [GX0 + 0.6 + k * (GX1 - GX0 - 1.2) / 6 for k in range(7)]
    for x in zx:
        put("gaanderij", "stuc", bz(x - 0.28, x + 0.28, GY0 - 0.28, GY0 + 0.28, -0.1, 0.35, 0.03))                # basement
        put("gaanderij", "stuc", bz(x - 0.2, x + 0.2, GY0 - 0.2, GY0 + 0.2, 0.35, 2.3, 0.02))
        put("gaanderij", "stuc", bz(x - 0.34, x + 0.34, GY0 - 0.34, GY0 + 0.34, 2.3, 2.55, 0.05))                 # kapiteel
        coll_box(x, GY0, 1.3, 0.45, 0.45, 2.6)
    put("gaanderij", "stuc", bz(GX0, GX1, GY0 - 0.35, GY0 + 0.35, 2.55, 2.95, 0.03))
    put("gaanderij", "stuc", bz(GX0, GX1, GY0 - 0.4, GY1, 2.95, 3.1))                                              # plafond
    put("gaanderij", "donker", bz(GX0, GX1, GY1 - 0.3, GY1, -0.1, 2.95))                                           # achterwand
    for x in zx[:-1]:
        cx = x + (zx[1] - zx[0]) / 2
        if abs(cx - 6.24) < 0.8: continue
        sh = boutline([(-0.38, 0.55), (0.38, 0.55), (0.42, 0.1), (0.0, -0.45), (-0.42, 0.1)], 0, 0.06)
        put("schilden", "rood", sh, Matrix.Translation((cx, GY1 - 0.34, 1.55)) @ Matrix.Rotation(math.pi, 4, "Z"))
        put("schilden", "goud", ell((cx, GY1 - 0.42, 1.65), (0.22, 0.05, 0.22), 10, 6)); put("schilden", "zwart", ell((cx, GY1 - 0.47, 1.68), (0.12, 0.02, 0.06), 8, 4))
    put("gaanderij", "goud", bz(5.5, 7.0, GY1 - 0.35, GY1 - 0.3, 0.0, 2.4)); put("gaanderij", "donker", bz(5.6, 6.9, GY1 - 0.38, GY1 - 0.34, 0.0, 2.3))   # deuren naar de grot
    plaat([(GX0, GY0 - 0.4), (GX1, GY0 - 0.4), (GX1, GY1), (GX0, GY1)], 0.08, 0.1, "gaanderij", "stuc")
    rm = bmesh.new()                                                                                               # rotsmassa boven de gaanderij
    for k in range(18):
        x0 = GX0 - 0.6 + k * (GX1 - GX0 + 1.2) / 18
        rotsblok(rm, x0 - 0.3, x0 + 1.3, GY0 - 0.9, GY1 + 0.6, 2.95, rr.uniform(4.0, 5.2), 1, 0.3)
        rotsblok(rm, x0, x0 + 1.0, GY0 - 1.1, GY0 - 0.3, rr.uniform(2.3, 2.75), 3.6, 1, 0.2)                      # grillige overhangende onderrand
        rotsblok(rm, x0 - 0.2, x0 + 1.2, GY1 - 0.5, GY1 + 1.5, 3.5, rr.uniform(5.5, 6.8), 1, 0.4)                 # hoger naar achter
    for (x0, x1, y0, y1, h) in ((GX0 - 4.6, GX0 + 0.3, GY0 - 0.6, GY1 + 1.0, 3.8), (-18.4, -16.7, -16.0, GY0, 3.2)):
        for k in range(6):
            rotsblok(rm, x0 + rr.uniform(0, 1), x1 - rr.uniform(0, 1), y0 + (y1 - y0) * k / 6, y0 + (y1 - y0) * (k + 1) / 6 + 0.4, -0.1, h + rr.uniform(-0.4, 0.8), 1, 0.35)
    put("rots", "rots", organisch(rm, 0.12, 3, 0.5, 0.25, 0.9, 0.25))
    coll_box((GX0 + GX1) / 2, GY1 + 0.4, 2.5, GX1 - GX0 + 1, 1.2, 5.0); coll_box(GX0 - 2.2, (GY0 + GY1) / 2, 1.8, 4.6, GY1 - GY0 + 1.6, 3.6)
    # ---------- tempelwachters (2x) op witte sokkels, knots voor zich ----------
    def wachter(M_W, kleur):
        w = {}
        def add(mat, b_, M=None):
            if M is not None: bmesh.ops.transform(b_, matrix=M, verts=b_.verts)
            w.setdefault(mat, bmesh.new()); merge_into(w[mat], b_)
        add("stuc", bz(-0.7, 0.7, -0.7, 0.7, -0.1, 1.0, 0.04))
        add(kleur, blathe([(0.36, 1.0), (0.42, 1.55), (0.32, 2.05), (0.0, 2.05)], 14))                        # rok
        for s_ in (-1, 1): add(kleur, btube([(s_ * 0.17, 0, 1.02), (s_ * 0.18, -0.02, 1.5)], 0.13, 8)); add("rood", ell((s_ * 0.18, -0.12, 1.06), (0.12, 0.2, 0.08), 8, 6))
        add(kleur, ell((0, 0, 2.45), (0.4, 0.3, 0.5), 12, 10))                                                  # borst/harnas
        add("goud", ell((0, -0.02, 2.05), (0.42, 0.32, 0.1), 12, 6))                                            # gordel
        for s_ in (-1, 1):
            add("goud", ell((s_ * 0.42, 0, 2.78), (0.2, 0.2, 0.16), 10, 6))                                     # schouderstukken
            add(kleur, btube([(s_ * 0.45, 0, 2.7), (s_ * 0.42, -0.25, 2.3), (s_ * 0.1, -0.42, 2.25)], 0.11, 8))
            add("huid", ell((s_ * 0.08, -0.45, 2.25), (0.1, 0.1, 0.09), 8, 6))
        H = Vector((0, -0.05, 3.15))
        add("huid", ell(H, (0.3, 0.28, 0.32), 12, 10)); add("huid", ell(H + Vector((0, -0.24, -0.05)), (0.09, 0.08, 0.1), 8, 6))
        for s_ in (-1, 1):
            add("wit", ell(H + Vector((s_ * 0.12, -0.25, 0.08)), (0.07, 0.03, 0.055), 8, 6)); add("zwart", ell(H + Vector((s_ * 0.12, -0.28, 0.08)), (0.03, 0.02, 0.03), 6, 4))
            add("wit", bz(s_ * 0.13 - 0.025, s_ * 0.13 + 0.025, -0.33 + H.y, -0.28 + H.y, H.z - 0.2, H.z - 0.1))  # slagtanden
            add("goud", ell(H + Vector((s_ * 0.31, 0, 0.0)), (0.05, 0.08, 0.14), 6, 4))                          # oorsieraden
        add("rood", bz(-0.12, 0.12, -0.31 + H.y, -0.27 + H.y, H.z - 0.2, H.z - 0.15))                          # mond
        add("goud", blathe([(0.33, 0), (0.33, 0.12), (0.26, 0.2), (0.24, 0.32), (0.18, 0.4), (0.17, 0.5), (0.12, 0.58), (0.11, 0.7), (0.06, 0.82), (0.04, 1.0), (0.0, 1.1)], 14), Matrix.Translation(H + Vector((0, 0.02, 0.2))))   # gelaagde kroon
        add("hout", btube([(0, -0.48, 0.95), (0, -0.48, 2.3)], 0.06, 8)); add("goud", ell((0, -0.48, 2.32), (0.1, 0.1, 0.07), 8, 6))
        for k in range(5): a = k * math.tau / 5; add("goud", ell((0.12 * math.cos(a), -0.48 + 0.12 * math.sin(a), 1.12), (0.11, 0.11, 0.11), 8, 6))   # knots-kop
        add("goud", ell((0, -0.48, 1.25), (0.12, 0.12, 0.1), 8, 6))
        for mat, bm in w.items(): put("wachters", mat, bm, M_W)
    wachter(Matrix.Translation((-13.0, 4.25, 0)) @ Matrix.Rotation(math.radians(-10), 4, "Z") @ Matrix.Scale(1.4, 4), "goud")
    wachter(Matrix.Translation((-8.55, 4.55, 0)) @ Matrix.Rotation(math.radians(10), 4, "Z") @ Matrix.Scale(1.4, 4), "rood")
    for x, y in ((-13.0, 4.25), (-8.55, 4.55)): coll_box(x, y, 1.0, 2.0, 2.0, 2.0)
    # ---------- witte muren rond het plein, bankjes, varenborder, Simurgh-deur ----------
    muren = [((-16.5, 5.0), (-16.5, -16.0)), ((-16.5, -16.0), (15.5, -16.0))]
    for a, b in muren:
        A, B = Vector(a), Vector(b); L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x)
        M_ = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
        if a[0] == b[0]:                                                                                           # westmuur met deur (gat 2.6 m breed)
            L1 = (L_ - 2.8) / 2
            for (u0, u1) in ((0, L1), (L1 + 2.8, L_)):
                put("muren", "stuc", bz(u0, u1, -0.25, 0.25, -0.1, 2.3), M_); put("muren", "stuc", bz(u0 - 0.05, u1 + 0.05, -0.3, 0.3, 2.3, 2.45), M_)
                coll_box((A.lerp(B, (u0 + u1) / 2 / L_)).x, (A.lerp(B, (u0 + u1) / 2 / L_)).y, 1.2, 0.5, u1 - u0, 2.4)
            dm = M_ @ Matrix.Translation((L1 + 1.4, 0, 0))                                                      # lokaal: x langs de muur, +y = pleinzijde
            for sx in (-1, 1): put("deur", "stuc", bz(sx * 1.4 - (0.32 if sx < 0 else 0), sx * 1.4 + (0.32 if sx > 0 else 0), -0.35, 0.45, -0.1, 3.0, 0.03), dm)
            put("deur", "stuc", boutline([(-1.75, 2.6), (1.75, 2.6), (1.75, 3.1), (0.9, 3.6), (0.0, 4.5), (-0.9, 3.6), (-1.75, 3.1)], -0.35, 0.8), dm)
            put("deur", "goud", boutline([(-0.25, 3.25), (0.25, 3.25), (0.0, 3.9)], 0.45, 0.04), dm)
            put("deur", "groen", bz(-1.4, 1.4, -0.1, 0.1, 0.0, 2.6), dm)
            put("deur", "donker", bz(-0.02, 0.02, 0.1, 0.12, 0.0, 2.6), dm)
            put("deur", "goud", boutline([(-0.9, 1.0), (-0.3, 1.45), (0.0, 2.35), (0.3, 1.45), (0.9, 1.0), (0.4, 1.15), (0.0, 0.55), (-0.4, 1.15)], 0.1, 0.05), dm)   # Simurgh
            put("deur", "wit", ell((0, 0.14, 2.1), (0.12, 0.03, 0.1), 8, 4), dm)
            coll_box((A.lerp(B, (L1 + 1.4) / L_)).x, (A.lerp(B, (L1 + 1.4) / L_)).y, 1.5, 0.6, 2.8, 3.0)
        else:
            put("muren", "stuc", bz(0, L_, -0.25, 0.25, -0.1, 2.3), M_); put("muren", "stuc", bz(-0.05, L_ + 0.05, -0.3, 0.3, 2.3, 2.45), M_)
            m = (A + B) / 2; coll_box(m.x, m.y, 1.2, L_, 0.5, 2.4, math.degrees(ang))
    for x in (-12.0, -6.0, 0.0, 6.0):                                                                               # bankjes langs de zuidmuur
        MB = Matrix.Translation((x, -15.2, 0))
        put("bank", "stuc", bz(-1.0, 1.0, -0.3, 0.3, 0.0, 0.42, 0.03), MB); put("bank", "hout", bz(-0.95, 0.95, -0.28, 0.28, 0.42, 0.48), MB)
        coll_box(x, -15.2, 0.25, 2.0, 0.6, 0.5)
    plaat([(-16.25, -15.75), (14.0, -15.75), (14.0, -14.65), (-15.15, -14.65), (-15.15, 4.9), (-16.25, 4.9)], 0.12, 0.15, "border", "modder")
    plaat([(-15.15, -14.65), (14.0, -14.65), (14.0, -14.55), (-15.05, -14.55), (-15.05, 4.9), (-15.15, 4.9)], 0.3, 0.3, "border", "stuc")
    bed = [(-16.2, -6.6), (-12.45, -6.6), (-12.45, 3.5), (-16.2, 3.5)]
    for a, b in zip(bed, bed[1:] + bed[:1]):
        A, B = Vector(a), Vector(b); L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x)
        M_ = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
        put("bed", "stuc", bz(-0.15, L_ + 0.15, -0.15, 0.15, -0.1, 0.55), M_); put("bed", "stuc", bz(-0.18, L_ + 0.18, -0.2, 0.2, 0.55, 0.62), M_)
    plaat(bed, 0.45, 0.5, "bed", "modder"); coll_box(-14.3, -1.55, 0.3, 3.8, 10.1, 0.6)
    # ---------- rotstunnel (toegang) met gouden naambord ----------
    tr = bmesh.new()
    for (x0, x1, y0, y1, h) in ((9.6, 21.0, -18.6, -15.7, 4.2), (9.4, 24.6, -12.6, -8.8, 4.6), (23.3, 25.6, -19.0, -12.6, 4.0), (9.0, 11.0, -12.8, -9.0, 3.4)):
        nx = max(1, int((x1 - x0) / 1.6)); ny = max(1, int((y1 - y0) / 1.6))
        for i in range(nx):
            for j in range(ny):
                rotsblok(tr, x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx + 0.3, y0 + (y1 - y0) * j / ny, y0 + (y1 - y0) * (j + 1) / ny + 0.3, -0.1, h + rr.uniform(-0.6, 0.9), 1, 0.3)
    for (x0, x1, y0, y1) in ((15.0, 23.6, -15.9, -12.4), (20.6, 23.6, -18.8, -15.6)):                             # dak over de tunnelgang
        rotsblok(tr, x0, x1, y0, y1, 2.9, 4.4, 2, 0.25)
    put("tunnel", "rots", organisch(tr, 0.12, 3, 0.5, 0.25, 0.9, 0.25))
    plaat([(14.8, -15.7), (23.4, -15.7), (23.4, -18.8), (20.8, -18.8), (20.8, -12.6), (14.8, -12.6)], 0.05, 0.1, "tunnel", "grind")
    for (x0, x1, y0, y1) in ((9.6, 21.0, -18.6, -15.7), (9.4, 24.6, -12.6, -8.8), (23.3, 25.6, -19.0, -12.6)):
        coll_box((x0 + x1) / 2, (y0 + y1) / 2, 2.0, x1 - x0, y1 - y0, 4.0)
    put("tunnel", "goud", boutline([(-1.3, 0), (1.3, 0), (1.45, 0.35), (1.3, 0.7), (-1.3, 0.7), (-1.45, 0.35)], 0, 0.08), Matrix.Translation((14.65, -14.1, 3.15)) @ Matrix.Rotation(math.pi / 2, 4, "Z"))
    for k in range(3): put("tunnel", "wit", bz(14.55, 14.6, -14.9 + k * 0.6, -14.5 + k * 0.6, 3.35, 3.5))     # letters (gestileerd)
    # ---------- groene showloods (interieur later) ----------
    plaat(LOODS, 7.5, 7.6, "loods", "loods"); plaat(GANG, 4.0, 4.1, "loods", "loods")
    coll_box(18.0, 21.0, 3.5, 26.0, 18.0, 7.0)
    # ---------- grindplein (gat voor de vijver) ----------
    plaat(PLEIN, 0.06, 0.12, "plein", "grind", gat=[(VX0 - 0.1, VY0 - 0.1), (VX1 + 0.1, VY0 - 0.1), (VX1 + 0.1, VY1 + 0.1), (VX0 - 0.1, VY1 + 0.1)])
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"WL_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": PLEIN, "vijver": VIJVER, "loods": LOODS}, open(os.path.join(out, "lelies_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
