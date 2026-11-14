"""03_stadje Het Meisje met de Zwavelstokjes (2004, Michel den Dulk): middeleeuws stadje op een kunstheuvel, naar Maquette_Mmdzs (indeling),
Meisjezij (voorgevel + vijver + trap), Zwavelstokjes4b (topgevel), Mmdz_bouw_stucwerk (poort + oprit) en OSM 279667968.
Modelframe: oorsprong = OSM-zwaartepunt, x = west (rechts voor de kijker), y = zuid (de diepte in), z op, z = 0 pad; heuvel HM = 0.9.
Voorkant (naar de vijver, noord) = -Y. Gebruik: Blender -b -P 03_stadje.py -- --master MZ_stadje_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
RNG = random.Random(2004)
MATS = {"stuc": ((0.86, 0.84, 0.8, 1), 0.9), "pannen": ((0.55, 0.26, 0.2, 1), 0.85), "natuursteen": ((0.5, 0.48, 0.44, 1), 0.95),
        "hout": ((0.25, 0.17, 0.11, 1), 0.8), "donker": ((0.03, 0.03, 0.03, 1), 0.9), "glasoranje": ((1.0, 0.62, 0.25, 1), 0.2),
        "ijzer": ((0.05, 0.05, 0.05, 1), 0.45), "goud": ((0.8, 0.6, 0.2, 1), 0.3), "water": ((0.1, 0.13, 0.1, 1), 0.05),
        "bodem": ((0.08, 0.07, 0.05, 1), 0.9), "leien": ((0.3, 0.27, 0.25, 1), 0.85), "venster": ((0.05, 0.05, 0.05, 1), 0.3),
        "dakplat": ((0.2, 0.2, 0.2, 1), 0.9), "grond": ((0.22, 0.2, 0.13, 1), 0.95), "klinker": ((0.5, 0.36, 0.28, 1), 0.9)}
HM = 0.9


def prisma(poly, z0, z1):
    bm = bmesh.new(); b = [bm.verts.new((x, y, z0)) for x, y in poly]; t = [bm.verts.new((x, y, z1)) for x, y in poly]
    n = len(poly); bm.faces.new(b[::-1]); bm.faces.new(t)
    for i in range(n): bm.faces.new((b[i], b[(i + 1) % n], t[(i + 1) % n], t[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], ngon_method="EAR_CLIP"); return bm


def toren(cx, cy, r, h, kegel=1.8, part="torens", kanteel=False, ramen=((0.0, 2.2), ), z0=HM, front=-math.pi / 2):
    """ronde gepleisterde toren (iets taps), getande consolelijst onder de goot, kegeldak met pannen en knop, of kantelen bovenop"""
    put(part, "stuc", organisch(blathe([(0, z0 - 0.3), (r * 1.08, z0 - 0.3), (r * 1.04, z0 + 0.6), (r, z0 + h * 0.75), (r, z0 + h), (0, z0 + h)], 20),
                                0.08, 3, 0.5, 0.03, 1.2, 0.1), TR(cx, cy))
    zr = z0 + h - 0.45
    put(part, "stuc", blathe([(0, zr), (r + 0.12, zr + 0.12), (r + 0.14, zr + 0.42), (0, zr + 0.42)], 20), TR(cx, cy))
    for k in range(18):                                                                                       # getande lijst (Mmdz_bouw_stucwerk)
        a = k * math.tau / 18
        put(part, "stuc", ell((cx + (r + 0.1) * math.cos(a), cy + (r + 0.1) * math.sin(a), zr + 0.02), (0.11, 0.11, 0.1), 6, 4))
    if kanteel:
        ring = [(cx + (r + 0.05) * math.cos(a), cy + (r + 0.05) * math.sin(a)) for a in [i * math.tau / 16 for i in range(17)]]
        kantelen(ring, z0 + h + 0.55, part, "stuc", d=0.28, merlon=0.36, gap=0.28, boog=False)
    else:
        put(part, "pannen", blathe([(0, z0 + h + 0.35), (r + 0.3, z0 + h + 0.25), (r + 0.25, z0 + h + 0.4), (r * 0.55, z0 + h + 0.4 + kegel * 0.55),
                                    (0, z0 + h + 0.4 + kegel)], 20), TR(cx, cy))
        put(part, "stuc", ell((cx, cy, z0 + h + 0.45 + kegel), (0.09, 0.09, 0.11), 8, 6))
    for (da, zz) in ramen:                                                                                    # raampje met lichtje
        a = front + da; Mw = Matrix.Translation((cx + r * math.cos(a), cy + r * math.sin(a), z0)) @ Matrix.Rotation(a + math.pi / 2, 4, "Z")
        put(part, "donker", boutline(arch_pts(0, zz, 0.32, 0.6, 6), -0.06, 0.12), Mw)
        put(part, "glasoranje", boutline(arch_pts(0, zz + 0.05, 0.22, 0.45, 6), -0.07, 0.02), Mw)
        put(part, "stuc", band(arch_pts(0, zz, 0.32, 0.6, 6), 0.06, -0.09, 0.08), Mw)
    coll_box(cx, cy, z0 + h / 2, 2 * r, 2 * r, h)


def dak(x0, x1, y0, y1, eave, nok, part="daken", langs="x", over=0.3):
    """zadeldak met pannen; nok langs x (evenwijdig aan de gevel) of langs y (topgevel naar voren)"""
    if langs == "x":
        prof = [(y0 - over, eave - 0.12), ((y0 + y1) / 2, nok), (y1 + over, eave - 0.12), (y1 + over, eave - 0.3), ((y0 + y1) / 2, nok - 0.2), (y0 - over, eave - 0.3)]
        put(part, "pannen", prism_x(prof, x0 - over * 0.6, x1 + over * 0.6))
        for xe in (x0, x1): put(part, "stuc", prism_x([(y0, eave - 0.1), ((y0 + y1) / 2, nok - 0.15), (y1, eave - 0.1)], xe - 0.05, xe + 0.05) if False else bmesh.new())
        put(part, "stuc", prism_x([(y0, eave - 0.15), ((y0 + y1) / 2, nok - 0.2), (y1, eave - 0.15)], x0, x1))
    else:
        M = Matrix.Rotation(math.radians(90), 4, "Z")
        prof = [(-(x1 + over), eave - 0.12), (-(x0 + x1) / 2, nok), (-(x0 - over), eave - 0.12), (-(x0 - over), eave - 0.3), (-(x0 + x1) / 2, nok - 0.2), (-(x1 + over), eave - 0.3)]
        put(part, "pannen", prism_x(prof, y0 - over * 0.6, y1 + over * 0.6), M)
        put(part, "stuc", prism_x([(-x1, eave - 0.15), (-(x0 + x1) / 2, nok - 0.2), (-x0, eave - 0.15)], y0, y1), M)


def blok(x0, x1, y0, y1, eave, part="blokken"):
    put(part, "stuc", organisch(bz(x0, x1, y0, y1, HM - 0.3, eave, 0.04), 0.09, 3, 0.5, 0.03, 1.2, 0.07))
    coll_box((x0 + x1) / 2, (y0 + y1) / 2, (HM + eave) / 2, x1 - x0, y1 - y0, eave - HM)


def raam_front(x, z, w=0.42, h=0.8, y=-2.74, licht=True, part="ramen", spits=False):
    pts = spits_pts(x, z, w, h, 6) if spits else arch_pts(x, z, w, h, 6)
    put(part, "donker", boutline(pts, y - 0.04, 0.1))
    if licht: put(part, "glasoranje", boutline(spits_pts(x, z + 0.05, w - 0.1, h - 0.1, 6) if spits else arch_pts(x, z + 0.05, w - 0.1, h - 0.1, 6), y - 0.05, 0.02))
    put(part, "stuc", band(pts, 0.07, y - 0.08, 0.08))
    put(part, "stuc", bz(x - w / 2 - 0.1, x + w / 2 + 0.1, y - 0.12, y, z - 0.08, z, 0.01))


def spits_torentje(cx, cy, r, zb, zt, spits, part="torentjes"):
    """torentje op consoles (Zwavelstokjes4b): kraagsteen-kegel, stuc schacht, raampje, puntige spits met knop"""
    put(part, "stuc", blathe([(0, zb - 0.9), (0.05, zb - 0.9), (r * 0.7, zb - 0.35), (r + 0.06, zb), (0, zb)], 12), TR(cx, cy))
    put(part, "stuc", blathe([(0, zb), (r, zb), (r, zt), (r + 0.08, zt), (r + 0.08, zt + 0.12), (0, zt + 0.12)], 12), TR(cx, cy))
    put(part, "pannen", blathe([(0, zt + 0.1), (r + 0.14, zt + 0.08), (r * 0.5, zt + spits * 0.5), (0, zt + spits)], 8), TR(cx, cy))
    put(part, "ijzer", btube([(cx, cy, zt + spits - 0.05), (cx, cy, zt + spits + 0.35)], 0.02, 5))
    put(part, "goud", ell((cx, cy, zt + spits + 0.12), (0.05, 0.05, 0.05), 8, 6))
    put(part, "donker", bz(cx - 0.06, cx + 0.06, cy - r - 0.01, cy - r + 0.05, (zb + zt) / 2 - 0.2, (zb + zt) / 2 + 0.2))


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ================= heuvel + keermuur van natuursteen + vijvertje (OSM 767716993) =================
    HEUVEL = [(-12.6, -1.4), (-10.4, -5.4), (-6.9, -3.45), (3.3, -3.45), (3.3, -4.35), (8.25, -4.35), (8.25, 1.2), (10.2, 1.2), (10.2, 6.6), (-8.3, 6.6), (-8.3, -0.6)]
    put("heuvel", "grond", prisma(HEUVEL, -0.2, HM))
    for (a, b) in zip(HEUVEL[1:7], HEUVEL[2:8]):                                                               # natuurstenen keermuur langs de voorkant
        d = Vector(b) - Vector(a); L = d.length; ang = math.atan2(d.y, d.x)
        M = Matrix.Translation((a[0], a[1], 0)) @ Matrix.Rotation(ang, 4, "Z")
        put("keermuur", "natuursteen", organisch(bz(-0.1, L + 0.1, -0.35, 0.1, -0.2, HM + 0.12, 0.05), 0.08, 2, 0.4, 0.05, 1.5, 0.12), M)
        coll_box((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, HM / 2, L, 0.45, HM, math.degrees(ang))
    VIJ = [(-1.88, -3.8), (-2.22, -7.12), (-3.35, -10.07), (-5.32, -11.15), (-8.64, -11.08), (-10.49, -10.44), (-10.72, -8.82), (-8.75, -8.16), (-5.78, -7.49), (-4.32, -5.39), (-3.59, -3.8)]
    put("vijver", "water", prisma(VIJ, -0.32, -0.28)); put("vijver", "bodem", prisma(VIJ, -0.9, -0.85))
    for i in range(len(VIJ)):
        a, b = VIJ[i], VIJ[(i + 1) % len(VIJ)]; L = math.hypot(b[0] - a[0], b[1] - a[1]); k = 0.0
        while k < L:
            t = k / L; x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t; s = RNG.uniform(0.25, 0.5)
            st = bbox(s * RNG.uniform(1.0, 1.6), s, s * RNG.uniform(0.5, 0.8), 0, 0, 0, s * 0.25)
            bmesh.ops.rotate(st, verts=st.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(RNG.uniform(0, math.tau), 3, "Z"))
            bmesh.ops.translate(st, vec=(x, y, -0.2 + RNG.uniform(-0.05, 0.12)), verts=st.verts); put("vijver", "natuursteen", st)
            k += RNG.uniform(0.4, 0.7)
    # ================= oprit naar de poort met lage gebogen muurtjes (Mmdz_bouw_stucwerk, Boekloc) =================
    G = Vector((-10.96, -3.28)); gd = Vector((-0.51, 0.86)); gn = Vector((-0.86, -0.51))                     # poortlijn en buitennormaal
    a0 = G + gn * 0.2; a1 = G + gn * 4.6
    bm = bmesh.new(); W2 = 1.15
    v = [bm.verts.new((*(a0 + gd * W2), HM)), bm.verts.new((*(a0 - gd * W2), HM)), bm.verts.new((*(a1 - gd * 1.5), 0.02)), bm.verts.new((*(a1 + gd * 1.5), 0.02))]
    vb = [bm.verts.new((p.co.x, p.co.y, -0.2)) for p in v]
    bm.faces.new(v); bm.faces.new(vb[::-1])
    for i in range(4): bm.faces.new((v[i], vb[i], vb[(i + 1) % 4], v[(i + 1) % 4]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("oprit", "klinker", bm)
    for sgn in (1, -1):
        pts = []
        for i in range(9):
            t = i / 8; p = a0.lerp(a1 + gn * 0.6, t) + gd * sgn * (W2 + 0.2 + 0.9 * t * t)
            pts.append((p.x, p.y, HM * (1 - t) + 0.05 + 0.55))
        for p, q in zip(pts, pts[1:]):
            d = Vector(q[:2]) - Vector(p[:2]); L = d.length; ang = math.atan2(d.y, d.x)
            M = Matrix.Translation((p[0], p[1], 0)) @ Matrix.Rotation(ang, 4, "Z")
            put("oprit", "stuc", organisch(bz(-0.05, L + 0.05, -0.17, 0.17, -0.2, (p[2] + q[2]) / 2, 0.05), 0.06, 3, 0.6, 0.02, 1.2, 0.3), M)
    # ================= poort met twee ronde torentjes + hoge ronde toren erachter =================
    T1 = G - gd * 1.95; T2 = G + gd * 1.95
    toren(T1.x, T1.y, 1.15, 3.6, kegel=1.6, ramen=((0.0, 2.6), ), front=math.atan2(gn.y, gn.x))
    toren(T2.x, T2.y, 1.15, 3.6, kegel=1.6, ramen=((0.0, 2.6), ), front=math.atan2(gn.y, gn.x))
    Mg = Matrix.Translation((G.x, G.y, HM)) @ Matrix.Rotation(math.atan2(gd.y, gd.x), 4, "Z")
    wall = [(-1.3, -0.05), (-0.72, -0.05)] + arch_pts(0, -0.05, 1.44, 2.65, 12)[1:-1] + [(0.72, -0.05), (1.3, -0.05), (1.3, 3.1), (-1.3, 3.1)]
    pb = boutline(wall, -0.25, 0.7); bmesh.ops.triangulate(pb, faces=[f for f in pb.faces if len(f.verts) > 4], ngon_method="EAR_CLIP"); put("poort", "stuc", pb, Mg)
    put("poort", "stuc", band(arch_pts(0, -0.05, 1.44, 2.65, 12), 0.16, -0.3, 0.08), Mg)
    put("poort", "donker", boutline(arch_pts(0, -0.05, 1.44, 2.65, 12), 0.35, 0.05), Mg)
    put("poort", "pannen", prism_x([(-0.6, 3.05), (0.1, 3.75), (0.8, 3.05), (0.8, 2.9), (0.1, 3.6), (-0.6, 2.9)], -1.5, 1.5), Mg @ Matrix.Rotation(math.radians(0), 4, "Z"))
    for sx in (-1, 1): put("poort", "ijzer", blathe([(0, 0.0), (0.06, 0.0), (0.06, 0.25), (0, 0.25)], 6), Mg @ Matrix.Translation((sx * 1.0, -0.32, 2.0)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    LAMPS_.append([round(G.x + gn.x * 0.6, 2), round(G.y + gn.y * 0.6, 2), HM + 2.6])
    toren(-9.2, -1.0, 1.6, 6.6, kegel=2.6, ramen=((-0.4, 2.6), (0.3, 4.6)))
    # ================= schuine muur poort -> voorgevel, kantelentorentje =================
    blok(-9.9, -6.9, -3.3, 0.6, 3.4)
    put("blokken", "stuc", bz(-9.9, -6.9, -3.5, -3.2, HM - 0.3, 3.4) if False else bmesh.new())
    dak(-9.9, -6.9, -3.6, 0.6, 3.4, 4.9, langs="x")
    toren(-6.35, -2.95, 1.05, 4.9, kanteel=True, ramen=((0.0, 2.4), (0.0, 4.0)))
    # ================= gaanderij met 3 rondbogen op zuiltjes (Maquette, Meisjezij) =================
    blok(-5.4, -1.6, -2.74, 1.2, 3.8); dak(-5.4, -1.6, -2.74, 1.2, 3.8, 5.6, langs="x")
    for k, x in enumerate((-4.6, -3.5, -2.4)):
        put("gaanderij", "donker", boutline(arch_pts(x, HM + 0.7, 0.9, 1.75, 10), -2.78, 0.3))
        for sx in (-0.5, 0.5):
            put("gaanderij", "stuc", blathe([(0, 0), (0.1, 0), (0.08, 0.1), (0.08, 1.15), (0.12, 1.25), (0, 1.25)], 10), TR(x + sx * 0.98 * (1 if True else 1) - (0 if sx < 0 else 0), -2.86, HM + 0.6))
        put("gaanderij", "stuc", band(arch_pts(x, HM + 0.7, 0.9, 1.75, 10), 0.08, -2.88, 0.12))
    put("gaanderij", "stuc", bz(-5.1, -1.9, -2.95, -2.74, HM + 0.45, HM + 0.62, 0.02))                        # borstwering
    # ================= midden: kantelenblok met twee spitsboogramen boven (Maquette, Meisjezij) =================
    blok(-1.6, 1.2, -2.74, 1.2, 4.6)
    kantelen([(-1.6, -2.78), (1.2, -2.78)], 5.35, "blokken", "stuc", d=0.3, merlon=0.4, gap=0.3, boog=True)
    for x in (-0.65, 0.35): raam_front(x, 3.2, 0.5, 1.0, spits=True)
    raam_front(-0.15, HM + 0.6, 0.38, 0.7, licht=False)
    # ================= grote topgevel met blinde spitsboog (Zwavelstokjes4b) =================
    GX0, GX1, GY = 1.2, 4.6, -3.25
    gpts = [(GX0, HM - 0.3), (GX1, HM - 0.3), (GX1, 4.7), ((GX0 + GX1) / 2, 8.0), (GX0, 4.7)]
    put("topgevel", "stuc", organisch(boutline(gpts, GY, 0.5), 0.08, 3, 0.5, 0.03, 1.2, 0.12))
    blok(GX0 + 0.05, GX1 - 0.05, GY + 0.4, 1.2, 4.7)
    dak(GX0 - 0.05, GX1 + 0.05, GY + 0.3, 1.2, 4.7, 7.85, langs="y")
    sa = spits_pts((GX0 + GX1) / 2, HM + 0.2, 2.5, 5.3, 10)
    put("topgevel", "stuc", band(sa, 0.22, GY - 0.12, 0.14))
    put("topgevel", "stuc", boutline([(x, z) for x, z in sa], GY + 0.12, 0.05) if False else bmesh.new())
    raam_front((GX0 + GX1) / 2, 3.4, 0.6, 1.3, y=GY + 0.06, spits=False)
    for i, x in enumerate((2.3, 2.9, 3.5)): raam_front(x, HM + 0.45, 0.32, 0.65, y=GY + 0.06, licht=(i == 1))
    put("topgevel", "stuc", bz(GX0 - 0.05, GX1 + 0.05, GY - 0.06, GY + 0.1, 4.6, 4.75, 0.01))
    spits_torentje(GX0 - 0.05, GY - 0.05, 0.38, 3.9, 5.8, 1.6); spits_torentje(GX1 + 0.05, GY - 0.05, 0.38, 3.9, 5.8, 1.6)
    # ================= rechtervleugel + uitgang met trap (OSM exit (8.8, 1.81)) =================
    blok(4.6, 8.13, -3.67, 1.2, 3.6); dak(4.6, 8.13, -3.67, 1.2, 3.6, 5.5, langs="x")
    for x in (5.4, 6.5, 7.5): raam_front(x, HM + 1.0, 0.36, 0.7, y=-3.67, licht=(x != 6.5))
    spits_torentje(8.13, -3.67, 0.36, 3.2, 4.8, 1.5)
    blok(8.13, 9.68, 1.81, 6.29, 3.3); dak(8.0, 9.8, 1.81, 6.29, 3.3, 4.8, langs="y")
    Mx = TR(8.9, 1.81, HM)
    put("uitgang", "donker", boutline(arch_pts(0, -0.05, 1.1, 2.2, 10), -0.06, 0.1), Mx)
    put("uitgang", "hout", boutline(arch_pts(0, -0.05, 1.0, 2.1, 10), -0.07, 0.02), Mx)
    put("uitgang", "stuc", band(arch_pts(0, -0.05, 1.1, 2.2, 10), 0.14, -0.12, 0.1), Mx)
    LAMPS_.append([8.9, 1.5, HM + 2.4])
    for i in range(6):                                                                                         # trap naar het pad (Meisjezij rechts)
        z = HM - (i + 1) * HM / 6
        put("trap", "natuursteen", bz(8.25, 9.65, 1.2 - (i + 1) * 0.5, 1.2 - i * 0.5, -0.2, z + HM / 6, 0.02))
    for x in (8.15, 9.75): put("trap", "stuc", organisch(bz(x - 0.15, x + 0.15, -1.9, 1.3, -0.2, HM + 0.45, 0.04), 0.06, 2, 0.5, 0.02, 1.2, 0.3))
    coll_box(9.75, -0.3, HM / 2 + 0.2, 0.3, 3.2, HM + 0.45, 0)
    # ================= hoge kantelenmuur achter (verbergt de loods van de Indische Waterlelies) + dichte loods =================
    BACK = [(-8.3, -0.6), (-8.3, 6.5), (10.0, 6.5), (10.0, 1.4)]
    for (a, b) in zip(BACK, BACK[1:]):
        d = Vector(b) - Vector(a); L = d.length; ang = math.atan2(d.y, d.x)
        M = Matrix.Translation((a[0], a[1], 0)) @ Matrix.Rotation(ang, 4, "Z")
        put("stadsmuur", "stuc", organisch(bz(-0.2, L + 0.2, -0.3, 0.3, HM - 0.3, 6.6, 0.05), 0.12, 3, 0.5, 0.04, 1.2, 0.05), M)
        coll_box((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 3.3, L, 0.6, 6.6, math.degrees(ang))
    kantelen(BACK, 7.25, "stadsmuur", "stuc", d=0.32, merlon=0.5, gap=0.38, boog=False)
    put("loods", "dakplat", bz(-8.0, 9.8, 1.0, 6.3, 6.0, 6.1))
    put("loods", "stuc", bz(-8.0, 9.8, 1.0, 6.3, HM, 6.0))
    for (x, y) in ((-8.3, 6.5), (10.0, 6.5)): toren(x, y, 0.9, 6.9, kegel=1.8, ramen=((0.0, 4.5), ))
    # ================= paden: klinkers voor de rechtervleugel, langs de vijver en bij de oprit (Meisjezij: rood-bruine klinkers) =================
    for poly in ([(-1.4, -4.45), (12.0, -4.45), (12.0, -9.5), (-1.4, -9.5)], [(-17.0, -11.4), (12.0, -11.4), (12.0, -14.5), (-17.0, -14.5)],
                 [(-17.0, -11.4), (-11.0, -11.4), (-11.0, -6.2), (-13.4, -3.0), (-17.0, -3.0)], [(-1.4, -9.5), (12.0, -9.5), (12.0, -11.4), (-1.4, -11.4)]):
        put("pad", "klinker", prisma(poly, -0.1, 0.04))
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        coll_box((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, -0.08, max(xs) - min(xs), max(ys) - min(ys), 0.24)
    # wegschrijven
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"MZ_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_}, open(os.path.join(out, "stadje_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
