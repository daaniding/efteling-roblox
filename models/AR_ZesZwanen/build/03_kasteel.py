"""03_kasteel De Zes Zwanen (2019): slot op gelaagde kunstrots. Modelframe (m): oorsprong = midden gebouw-footprint OSM 961616753,
voorkant naar de vijver = -Y, +X = rechts (zie ref/model_frame.json), z = 0 padniveau, waterlijn WL.
Bronnen/maten: asset-brief.md (D6z_exterieur_totaal 45 px/m op torendiepte, toren 15 m, plattegrond OSM, landschapsontwerp).
Gebruik: Blender -b -P 03_kasteel.py -- --master ZZ_kasteel_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "zz_helpers.py")).read())
RNG = random.Random(2019)
MATS = {"stuc": ((0.8, 0.79, 0.74, 1), 0.9), "natuursteen": ((0.62, 0.6, 0.55, 1), 0.9), "rots": ((0.5, 0.49, 0.45, 1), 0.95),
        "pannen": ((0.55, 0.26, 0.2, 1), 0.85), "leien": ((0.42, 0.27, 0.18, 1), 0.8), "hout": ((0.3, 0.24, 0.19, 1), 0.8),
        "venster": ((0.05, 0.05, 0.05, 1), 0.3), "glasoranje": ((1.0, 0.62, 0.25, 1), 0.2), "ijzer": ((0.05, 0.05, 0.05, 1), 0.45),
        "goud": ((0.8, 0.6, 0.2, 1), 0.3), "glaslamp": ((0.95, 0.8, 0.5, 1), 0.2), "donker": ((0.02, 0.02, 0.02, 1), 0.9), "groenhout": ((0.2, 0.29, 0.23, 1), 0.8), "lantaarnrood": ((0.55, 0.15, 0.1, 1), 0.6)}
T = Vector((3.55, 1.25))                        # torenmidden (foto: toren rijst links-achter uit het poortgebouw)
A = Vector((-2.95, -1.0)); ANG = 0.0            # linkervleugel: gevel evenwijdig aan de poortvoorzijde (foto: beide recht van voren), rechts tegen de toren
MW = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(math.radians(ANG), 4, "Z")
ZW = 3.6                                        # vleugel staat op de rots
LW, DW, GOOT, NOK = 5.25, 2.6, 5.8, 6.9


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ================= ROTS onder de vleugel en voor het slot (grot links, waar de bootjes naar buiten varen) =================
    ROCK = [(-6.4, -0.6), (-6.2, -2.7), (-5.5, -3.9), (-4.4, -4.6), (-3.1, -5.15), (-1.9, -5.7), (-0.5, -4.7), (0.8, -3.9), (2.0, -2.8),
            (2.5, -1.2), (2.4, 1.6), (0.4, 2.8), (-2.0, 3.5), (-6.2, 2.0)]
    trk_ = [(-0.29, 0.0), (-2.05, -0.89), (-3.44, -2.27), (-4.34, -4.01), (-4.65, -5.98)]
    def tunnel(x, y, z):                                                                               # geen blokken in de grot (vaarbaan)
        d = min(math.hypot(x - ax - t * (bx - ax), y - ay - t * (by - ay)) for (ax, ay), (bx, by) in zip(trk_, trk_[1:])
                for t in [max(0, min(1, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))])
        return d < (1.15 if z < 1.9 else 1.15 * math.sqrt(max(0.0, 1 - ((z - 1.9) / 0.75) ** 2))) and z < 2.65   # boog
    rk, kern = rotsblokken(ROCK, ZW + 0.15, front_edges=list(range(0, 9)), seed=3, slope=2.0, vrij=tunnel, voet=1.3)   # gestapelde hoekige blokken (foto)
    PARTS[("rots", "donker")] = kern
    # grot (uitvaart): boogtunnel langs de vaarbaan (OSM 837234781) van binnen het slot naar de vijver
    trk = [(-0.29, 0.0), (-2.05, -0.89), (-3.44, -2.27), (-4.34, -4.01), (-4.65, -5.98)]
    GROT = []
    for (ax, ay), (bx, by) in zip(trk, trk[1:]):
        ang = math.degrees(math.atan2(by - ay, bx - ax)); ln = math.hypot(bx - ax, by - ay)
        seg = boutline(arch_pts(0, WL - 0.6, 2.0, 2.9 + 0.6, 12), -0.1, ln + 0.2)                      # 2.0 breed, 2.55 boven water
        bmesh.ops.transform(seg, matrix=Matrix.Translation((ax, ay, 0)) @ Matrix.Rotation(math.radians(ang - 90), 4, "Z"), verts=seg.verts)
        GROT.append(seg)
    PARTS[("rots", "rots")] = rk
    put("rots", "donker", boutline(arch_pts(0, WL - 0.2, 1.7, 2.7, 10), 0, 0.05), Matrix.Translation((-0.4, -0.05, 0)) @ Matrix.Rotation(math.radians(math.degrees(math.atan2(-0.89, -1.76)) - 90), 4, "Z"))
    # ================= POORTGEBOUW (natuursteen, kantelen op boogfries, waterpoort in de schuine rechterzijde) =================
    GP = [(2.3, -2.43), (5.54, -2.43), (7.1, 0.31), (6.4, 1.6), (2.3, 1.6)]
    pb = boutline([(x, z) for x, z in [(0, 0)]], 0, 0) if False else None
    gb = bmesh.new(); vb = [gb.verts.new((x, y, WL - 0.5)) for x, y in GP]; vt = [gb.verts.new((x, y, 3.65)) for x, y in GP]
    n = len(GP); gb.faces.new(vb[::-1]); gb.faces.new(vt)
    for i in range(n): gb.faces.new((vb[i], vb[(i + 1) % n], vt[(i + 1) % n], vt[i]))
    bmesh.ops.recalc_face_normals(gb, faces=gb.faces)
    PARTS[("poort", "stuc")] = organisch(gb, 0.05, 3, 0.5, 0.03, 1.2, 0.3)                       # gepleisterd met doorschemerende steen (foto)
    kantelen([(2.3, -2.43), (5.54, -2.43), (7.1, 0.31)], 4.35, "poort", "stuc")
    # waterpoort: op de plek waar de vaarbaan de schuine zijde kruist (6.3, -1.6), spitsboog met diepe donkere doorvaart
    wp_ang = math.degrees(math.atan2(0.31 + 2.43, 7.1 - 5.54))
    WPM = Matrix.Translation((6.32, -1.03, 0)) @ Matrix.Rotation(math.radians(wp_ang), 4, "Z")
    put("poort", "donker", boutline(spits_pts(0, WL - 0.1, 1.75, 2.85), 0.25, 0.05), WPM)
    put("poort", "natuursteen", band(spits_pts(0, WL - 0.1, 1.75, 2.85), 0.22, -0.12, 0.2), WPM)
    # pilasters/hoeklisenen van grote blokken + plint
    for (x, y) in GP[:3]: put("poort", "natuursteen", bz(x - 0.3, x + 0.3, y - 0.3, y + 0.3, WL - 0.5, 3.75, 0.03))
    # ================= TOREN (stuc, rode ringlijsten, opgezwollen kop, dakrand, 2 uien, spits, vaan) =================
    prof = [(0, WL), (1.42, WL), (1.32, 3.0), (1.18, 5.5), (1.12, 6.9), (1.1, 7.0), (0, 7.0)]
    put("toren", "stuc", organisch(blathe(prof, 28), 0.05, 4, 0.5, 0.1, 0.55, 0.25), TR(T.x, T.y))      # bobbelig handgemodelleerd stuc
    kop = [(0, 6.95), (1.1, 6.95), (1.12, 8.1), (1.08, 8.25), (0, 8.25)]
    put("toren", "stuc", organisch(blathe(kop, 28), 0.05, 6, 0.6, 0.03, 1.2, 0.25), TR(T.x, T.y))
    kop2 = [(0, 8.4), (1.14, 8.4), (1.3, 8.75), (1.36, 9.1), (1.3, 9.35), (1.2, 9.45), (0, 9.45)]
    k2 = blathe(kop2, 28)
    for v in k2.verts:                                                                                 # zwanenkop: bult naar rechtsvoor
        a = math.atan2(v.co.y, v.co.x); bump = max(0.0, math.cos(a - math.radians(-5))) ** 6 * 0.55 * max(0.0, math.sin(math.pi * (v.co.z - 8.4) / 1.05))
        r = math.hypot(v.co.x, v.co.y)
        if r > 1e-4: v.co.x *= (r + bump) / r; v.co.y *= (r + bump) / r
    put("toren", "stuc", organisch(k2, 0.05, 6, 0.6, 0.03, 1.2, 0.25), TR(T.x, T.y))
    put("toren", "pannen", blathe([(0, 7.1), (1.3, 7.12), (1.35, 7.2), (1.2, 7.38), (0, 7.38)], 28), TR(T.x, T.y))             # rode ringlijst (foto 7.3 m)
    put("toren", "leien", blathe([(0, 8.18), (1.24, 8.2), (1.26, 8.42), (1.14, 8.46), (0, 8.46)], 28), TR(T.x, T.y))          # donkere leien band (8.4 m)
    for k in range(20):                                                                                # tandlijst onder de band
        a = k * math.tau / 20; put("toren", "stuc", bz(-0.04, 0.04, -0.05, 0.05, 8.08, 8.2), TR(T.x + 1.17 * math.cos(a), T.y + 1.17 * math.sin(a), 0, math.degrees(a)))
    # hoedendak: brede uitlopende rand (9.4 m) met pannen, daarna een bolle pannenkap tot 12.0, hals met dakkapelletje, kleine ui, spits, vaan
    hoed = [(0, 9.3), (1.82, 9.36), (1.86, 9.48), (1.55, 9.62), (1.32, 9.95), (1.3, 10.3), (1.42, 10.75), (1.38, 11.25), (1.1, 11.7), (0.65, 11.98), (0.42, 12.06), (0, 12.08)]
    put("toren", "pannen", blathe(hoed, 32), TR(T.x, T.y))
    for i_ in range(14):                                                                               # pannenrijen
        z = 9.5 + i_ / 13 * 2.45
        r = next((p0[0] + (p1[0] - p0[0]) * (z - p0[1]) / (p1[1] - p0[1]) for p0, p1 in zip(hoed, hoed[1:]) if p0[1] <= z <= p1[1]), 0.5)
        put("toren", "pannen", blathe([(r - 0.03, z - 0.04), (r + 0.04, z), (r - 0.02, z + 0.05)], 32), TR(T.x, T.y))
    for k in range(6):                                                                                 # pinakeltjes rond de dakvoet
        a = math.radians(30 + k * 60); px_, py_ = T.x + 1.6 * math.cos(a), T.y + 1.6 * math.sin(a)
        put("toren", "leien", blathe([(0, 9.45), (0.05, 9.45), (0.04, 9.9), (0.0, 10.25)], 6), TR(px_, py_))
    put("toren", "stuc", blathe([(0, 12.0), (0.36, 12.0), (0.32, 12.25), (0, 12.25)], 16), TR(T.x, T.y))                       # hals
    ui2 = [(0, 12.2), (0.5, 12.25), (0.6, 12.5), (0.5, 12.78), (0.2, 12.95), (0.08, 13.02), (0, 13.04)]
    put("toren", "pannen", blathe(ui2, 20), TR(T.x, T.y))
    put("toren", "leien", blathe([(0, 12.98), (0.08, 12.98), (0.06, 13.3), (0.12, 13.4), (0.05, 13.55), (0.03, 14.0), (0.08, 14.08), (0.0, 14.3)], 12), TR(T.x, T.y))
    put("toren", "goud", btube([(T.x, T.y, 14.25), (T.x, T.y, 15.0)], 0.018, 6))
    put("toren", "goud", organisch(merge(ell((T.x, T.y, 14.75), (0.22, 0.02, 0.14), 12, 8), ell((T.x - 0.2, T.y, 14.88), (0.06, 0.02, 0.06), 8, 6), ell((T.x + 0.2, T.y, 14.88), (0.06, 0.02, 0.06), 8, 6)), 0.012, 3, 0.5, 0.0))
    for k in range(4):                                                                                 # dakkapelletjes in de pannenkap
        a = math.radians(-90 + k * 90 - 25); cx_, cy_ = T.x + 1.38 * math.cos(a), T.y + 1.38 * math.sin(a)
        Mk = Matrix.Translation((cx_, cy_, 0)) @ Matrix.Rotation(a + math.pi / 2, 4, "Z")
        put("toren", "pannen", boutline([(-0.24, 10.45), (0.24, 10.45), (0.0, 11.0)], -0.12, 0.45), Mk)
        put("toren", "venster", bz(-0.1, 0.1, -0.14, -0.1, 10.5, 10.8), Mk)
    a = math.radians(-60); Mk = Matrix.Translation((T.x + 0.38 * math.cos(a), T.y + 0.38 * math.sin(a), 0)) @ Matrix.Rotation(a + math.pi / 2, 4, "Z")
    put("toren", "pannen", boutline([(-0.13, 12.05), (0.13, 12.05), (0.0, 12.35)], -0.1, 0.25), Mk); put("toren", "venster", bz(-0.06, 0.06, -0.12, -0.09, 12.07, 12.22), Mk)
    for (zz, a) in ((4.6, -100), (6.1, -70), (7.6, -110), (8.75, -40)):                               # smalle torenvensters
        a = math.radians(a); Mk = Matrix.Translation((T.x + 1.12 * math.cos(a), T.y + 1.12 * math.sin(a), 0)) @ Matrix.Rotation(a + math.pi / 2, 4, "Z")
        put("toren", "venster", boutline(arch_pts(0, zz, 0.28, 0.6, 6), -0.06, 0.08), Mk)
    # zijtorentje op de kop (ontwerp: romantiserend torentje links)
    st = Vector((T.x - 1.25, T.y - 0.2))
    put("toren", "stuc", blathe([(0, 8.3), (0.08, 8.3), (0.3, 8.7), (0.28, 9.4), (0, 9.4)], 16), TR(st.x, st.y))
    put("toren", "pannen", blathe([(0, 9.35), (0.36, 9.35), (0.2, 9.85), (0.04, 10.45), (0, 10.5)], 14), TR(st.x, st.y))
    coll_box(T.x, T.y, 2.0, 2.4, 2.4, 4.0)
    # ================= LINKERVLEUGEL (lokaal frame MW: x langs de gevel 0..LW, y de diepte in 0..DW) =================
    put("vleugel", "stuc", organisch(bz(0, LW, 0, DW, ZW - 0.6, GOOT + 0.05), 0.05, 5, 0.6, 0.03, 1.0, 0.2), MW)
    put("vleugel", "stuc", bz(-0.08, LW + 0.08, -0.12, DW + 0.08, GOOT - 0.25, GOOT - 0.1, 0.02), MW)                          # kroonlijst
    rp = [(-0.3, GOOT - 0.12), (DW / 2, NOK), (DW + 0.3, GOOT - 0.12), (DW + 0.3, GOOT - 0.3), (DW / 2, NOK - 0.2), (-0.3, GOOT - 0.3)]
    put("vleugel", "pannen", prism_x(rp, -0.2, LW + 0.2), MW)
    for x in (-0.25, LW + 0.25): put("vleugel", "stuc", prism_x([(0, GOOT - 0.12), (DW / 2, NOK - 0.05), (DW, GOOT - 0.12)], x - 0.05, x + 0.05), MW) if False else None
    for xg in (1.7, 3.45):                                                                            # klokgevels met bol + dwarsdakje
        bell = [(xg - 0.62, GOOT - 0.3), (xg + 0.62, GOOT - 0.3), (xg + 0.62, GOOT + 0.2), (xg + 0.42, GOOT + 0.45), (xg + 0.48, GOOT + 0.7),
                (xg + 0.28, GOOT + 0.95), (xg + 0.12, NOK + 0.05), (xg - 0.12, NOK + 0.05), (xg - 0.28, GOOT + 0.95), (xg - 0.48, GOOT + 0.7),
                (xg - 0.42, GOOT + 0.45), (xg - 0.62, GOOT + 0.2)]
        put("vleugel", "stuc", boutline(bell, -0.08, 0.35), MW)
        put("vleugel", "stuc", band(bell[2:] + [bell[0]], 0.05, -0.12, 0.06), MW) if False else None
        put("vleugel", "stuc", ell((xg, -0.05, NOK + 0.2), (0.13, 0.13, 0.13), 12, 8), MW)
        put("vleugel", "pannen", prism_x([(0.1, GOOT + 0.45), (0.0, NOK - 0.1), (0.1, NOK - 0.1)], xg - 0.5, xg + 0.5), MW) if False else None
        Mx = MW @ Matrix.Translation((xg, 0, 0)) @ Matrix.Rotation(math.radians(90), 4, "Z")
        put("vleugel", "pannen", prism_x([(-0.55, GOOT + 0.1), (0.0, NOK - 0.15), (0.55, GOOT + 0.1), (0.55, GOOT - 0.05), (0.0, NOK - 0.3), (-0.55, GOOT - 0.05)], 0.2, 1.4), Mx)
        gotisch_raam(xg, GOOT + 0.05, 0.4, 0.75, -0.08, "vleugel", MW)
    for xr in (0.85, 2.58, 4.35):
        gotisch_raam(xr, ZW + 0.75, 0.42, 1.05, 0.0, "vleugel", MW)
    for xr in (1.7, 3.45): gotisch_raam(xr, ZW + 0.75, 0.42, 1.05, 0.0, "vleugel", MW)
    for xp in (0.4, 1.25, 2.15, 3.0, 3.9, 4.85):                                                  # lisenen
        put("vleugel", "stuc", bz(xp - 0.08, xp + 0.08, -0.08, 0.02, ZW - 0.2, GOOT - 0.25, 0.01), MW)
    # erkertorentje op de linkervoorhoek: console-kegel, rond, spitse kegelspits + vaantje
    put("vleugel", "stuc", blathe([(0, ZW + 0.35), (0.06, ZW + 0.35), (0.45, ZW + 0.9), (0.45, GOOT + 0.55), (0, GOOT + 0.55)], 18), MW @ Matrix.Translation((0.05, -0.1, 0)))
    put("vleugel", "stuc", blathe([(0, GOOT + 0.5), (0.52, GOOT + 0.5), (0.52, GOOT + 0.62), (0, GOOT + 0.62)], 18), MW @ Matrix.Translation((0.05, -0.1, 0)))
    put("vleugel", "leien", blathe([(0, GOOT + 0.6), (0.5, GOOT + 0.6), (0.36, GOOT + 0.95), (0.3, GOOT + 1.1), (0.34, GOOT + 1.25), (0.12, 7.9), (0.03, 8.65), (0, 8.7)], 16), MW @ Matrix.Translation((0.05, -0.1, 0)))
    put("vleugel", "goud", btube([(0, 0, 8.6), (0, 0, 9.35)], 0.014, 6), MW @ Matrix.Translation((0.05, -0.1, 0)))
    put("vleugel", "goud", bz(0.0, 0.32, -0.006, 0.006, 9.05, 9.25), MW @ Matrix.Translation((0.05, -0.1, 0)))
    for zz in (ZW + 1.4, GOOT - 0.4): gotisch_raam(0, zz, 0.22, 0.5, -0.43, "vleugel", MW @ Matrix.Translation((0.05, -0.1, 0)))
    # pinakel-schoorsteen met bol rechts op de vleugel (foto px 495-515, bol op 7.8 m)
    Mp = MW @ Matrix.Translation((4.95, 0.55, 0))
    put("vleugel", "stuc", bz(-0.18, 0.18, -0.18, 0.18, GOOT - 0.3, 7.5, 0.02), Mp)
    put("vleugel", "stuc", bz(-0.24, 0.24, -0.24, 0.24, 7.45, 7.58, 0.02), Mp)
    put("vleugel", "stuc", ell((0, 0, 7.78), (0.17, 0.17, 0.17), 12, 8), Mp)
    coll_box(*(MW @ Vector((LW / 2, DW / 2, 0))).xy, ZW + 1.1, LW, DW, 2.2, ANG)
    # ================= DETAILS (hoofdfoto) =================
    # poort: hoekblokken (afwisselend lang/kort, steken 4 cm uit) op de hoeken en langs de waterpoort
    for (x, y) in GP[:3]:
        for i in range(9):
            z = WL - 0.2 + i * 0.44; lang = 0.62 if i % 2 else 0.4
            put("poort", "natuursteen", bz(x - lang / 2, x + lang / 2, y - 0.34, y + 0.34, z, z + 0.4, 0.04))
    sp_ = spits_pts(0, WL - 0.1, 1.75, 2.85, 8)
    for i, (px_, pz_) in enumerate(sp_[1:-1]):
        if i % 2: continue
        put("poort", "natuursteen", bz(px_ - 0.16, px_ + 0.16, -0.16, 0.06, pz_ - 0.16, pz_ + 0.16, 0.03), WPM)
    # lantaarns op palen op de poortmuur (foto: 3 stuks)
    for (lx, ly) in ((2.9, -2.35), (5.2, -2.35), (6.85, -0.1)):
        put("details", "ijzer", blathe([(0, 4.0), (0.07, 4.0), (0.05, 4.6), (0, 4.6)], 8), TR(lx, ly))
        put("details", "ijzer", blathe([(0, 4.55), (0.14, 4.58), (0.16, 4.65), (0, 4.65)], 6), TR(lx, ly, 0, 30))
        put("details", "glaslamp", blathe([(0, 4.65), (0.11, 4.65), (0.15, 5.0), (0, 5.0)], 6), TR(lx, ly, 0, 30))
        put("details", "ijzer", blathe([(0, 4.98), (0.2, 5.0), (0.16, 5.08), (0.04, 5.22), (0, 5.25)], 6), TR(lx, ly, 0, 30))
        put("details", "goud", ell((lx, ly, 5.29), (0.035, 0.035, 0.045), 8, 6))
        LAMPS_.append([lx, ly, 4.85])
    # vleugel: boogfries onder de goot, hoeklisenen, twee schoorsteentjes, muurlantaarn rechts
    x = 0.12
    while x < LW - 0.25:
        put("vleugel", "stuc", band(arch_pts(x + 0.14, GOOT - 0.62, 0.26, 0.3, 6), 0.035, -0.06, 0.05), MW); x += 0.36
    put("vleugel", "stuc", bz(-0.05, LW + 0.05, -0.1, 0.02, GOOT - 0.66, GOOT - 0.6), MW)
    for xc in (0.0, LW): put("vleugel", "stuc", bz(xc - 0.16, xc + 0.16, -0.12, 0.2, ZW - 0.3, GOOT - 0.2, 0.02), MW)
    for (xc, yc) in ((1.25, 1.6), (3.0, 1.9)):
        put("vleugel", "stuc", bz(xc - 0.16, xc + 0.16, yc - 0.16, yc + 0.16, GOOT + 0.3, NOK + 0.55, 0.02), MW)
        put("vleugel", "pannen", bz(xc - 0.21, xc + 0.21, yc - 0.21, yc + 0.21, NOK + 0.55, NOK + 0.63, 0.02), MW)
    Ml = MW @ Matrix.Translation((LW - 0.35, -0.02, 0))
    put("vleugel", "ijzer", btube([(0, 0, GOOT - 0.9), (0, -0.35, GOOT - 0.9), (0, -0.35, GOOT - 1.0)], 0.015, 6), Ml)
    put("vleugel", "ijzer", blathe([(0, 0.36), (0.05, 0.36), (0.15, 0.27), (0.1, 0.25), (0.1, 0.02), (0.06, -0.03), (0, -0.05)], 4), Ml @ Matrix.Translation((0, -0.35, GOOT - 1.45)))
    put("vleugel", "glaslamp", blathe([(0, 0.02), (0.095, 0.02), (0.095, 0.24), (0, 0.24)], 4), Ml @ Matrix.Translation((0, -0.35, GOOT - 1.45)))
    p_ = Ml @ Vector((0, -0.35, GOOT - 1.32)); LAMPS_.append([round(p_.x, 2), round(p_.y, 2), round(p_.z, 2)])
    # erkertorentje: consoleringen
    for zz in (ZW + 0.5, ZW + 0.7, GOOT + 0.25):
        put("vleugel", "stuc", blathe([(0, zz), (0.5, zz), (0.52, zz + 0.06), (0, zz + 0.06)], 18), MW @ Matrix.Translation((0.05, -0.1, 0)))
    # toren: vensteromlijstingen + klein balkonnetje onder de kop (foto)
    for (zz, a) in ((4.6, -100), (6.1, -70), (7.6, -110), (8.75, -40)):
        a = math.radians(a); Mk = Matrix.Translation((T.x + 1.14 * math.cos(a), T.y + 1.14 * math.sin(a), 0)) @ Matrix.Rotation(a + math.pi / 2, 4, "Z")
        put("toren", "stuc", band(arch_pts(0, zz, 0.28, 0.6, 6), 0.06, -0.09, 0.06), Mk)
        put("toren", "stuc", bz(-0.22, 0.22, -0.14, 0.0, zz - 0.07, zz, 0.01), Mk)
    # ================= ACHTERBOUW volgens de OSM-omtrek 961616753 (15.4 x 13.1 m; Efteling: 'slot 350 m2') =================
    # rechts: gepleisterde kantelenmuur met natuurstenen pijlers, ingang wandelgang (houten afdak, rode lantaarns) en de lage uitgangspoort
    # met gebogen pannenkap en bollen (D6z_wandelingang_slot, D6z_landschap_ingang_slot); links: lager blok bruine natuursteen met kantelen
    # (D6z_ontwerp_aanzicht_links: kantelen ~4.8 m boven maaiveld, ervoor een lager blok). Binnenkant komt later (Daan).
    def prisma(poly, z0, z1):
        bm = bmesh.new(); b = [bm.verts.new((x, y, z0)) for x, y in poly]; t = [bm.verts.new((x, y, z1)) for x, y in poly]
        n_ = len(poly); bm.faces.new(b[::-1]); bm.faces.new(t)
        for i in range(n_): bm.faces.new((b[i], b[(i + 1) % n_], t[(i + 1) % n_], t[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], ngon_method="EAR_CLIP"); return bm
    AR = [(6.41, 1.58), (5.55, 3.02), (3.96, 3.13), (2.97, 4.14), (3.81, 5.47), (4.22, 6.57), (1.63, 7.77), (-2.0, 4.83)]
    AL = [(-2.0, 4.83), (-3.71, 6.86), (-8.27, 3.23), (-6.62, 1.19)]
    put("achter", "stuc", organisch(prisma(AR + [(-1.0, 2.4), (2.3, 1.45)], -0.05, 4.0), 0.08, 3, 0.5, 0.03, 1.2, 0.1))
    put("achter", "natuursteen", prisma(AL + [(-3.0, 2.4), (-1.0, 2.4)], -0.05, 3.3))
    kantelen(AR, 4.35, "achter", "stuc"); kantelen(AL, 3.6, "achter", "natuursteen", boog=False)
    for (x, y) in AR[:7]:                                                                                   # natuurstenen hoekpijlers
        for i in range(10):
            z = -0.05 + i * 0.45; lang = 0.66 if i % 2 else 0.46
            put("achter", "natuursteen", bz(x - lang / 2, x + lang / 2, y - 0.3, y + 0.3, z, z + 0.42, 0.04))
        put("achter", "natuursteen", bz(x - 0.36, x + 0.36, y - 0.36, y + 0.36, 4.45, 4.62, 0.03))
    put("achter", "donker", prisma([(-4.6, 2.2), (-2.6, 2.2), (-2.6, 3.0), (-4.6, 3.0)], 0.0, 1.9)) if False else None
    def wandframe(a, b, naar):
        """matrix op het midden van muurstuk a-b, lokaal x langs de muur, lokaal -y naar buiten (richting punt 'naar')"""
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; ux, uy = b[0] - a[0], b[1] - a[1]; L = math.hypot(ux, uy)
        nx, ny = uy / L, -ux / L
        if (naar[0] - mx) * nx + (naar[1] - my) * ny < 0: nx, ny = -nx, -ny
        return Matrix.Translation((mx, my, 0)) @ Matrix.Rotation(math.atan2(nx, -ny), 4, "Z"), L
    # ingang wandelgang: donkere boogopening, houten afdak met pannen op gebogen schoren, twee rode lantaarns
    Mi, _ = wandframe((3.96, 3.13), (2.97, 4.14), (7.0, 5.0))
    put("achter", "donker", boutline(arch_pts(0, 0.0, 1.35, 2.35, 10), -0.04, 0.12), Mi)
    put("achter", "natuursteen", band(arch_pts(0, 0.0, 1.35, 2.35, 10), 0.16, -0.1, 0.12), Mi)
    put("achter", "hout", bz(-0.95, 0.95, -0.06, 0.0, 2.45, 3.25, 0.01), Mi)                                # groen-grijze planken boven de deur
    put("achter", "pannen", prism_x([(0.0, 3.4), (-1.1, 2.7), (-1.1, 2.6), (0.0, 3.28)], -1.05, 1.05), Mi)
    put("achter", "hout", prism_x([(0.0, 3.3), (-1.12, 2.62), (-1.12, 2.5), (0.0, 3.18)], -1.08, 1.08), Mi)
    for sx in (-0.9, 0.9):
        put("achter", "hout", btube([(sx, -0.05, 1.9), (sx, -0.5, 2.25), (sx, -0.95, 2.62)], 0.06, 6), Mi)
        Ml2 = Mi @ Matrix.Translation((sx * 1.18, -0.28, 0))
        put("achter", "ijzer", btube([(0, 0.28, 2.0), (0, 0.0, 2.0), (0, 0.0, 1.9)], 0.015, 5), Ml2)
        put("achter", "lantaarnrood", blathe([(0, 1.45), (0.1, 1.48), (0.1, 1.8), (0.14, 1.82), (0.02, 1.92), (0, 1.93)], 6), Ml2)
        put("achter", "glasoranje", blathe([(0, 1.5), (0.105, 1.5), (0.105, 1.78), (0, 1.78)], 6), Ml2)
        p_ = Ml2 @ Vector((0, 0, 1.65)); LAMPS_.append([round(p_.x, 2), round(p_.y, 2), round(p_.z, 2)])
    # uitgangspoort: lager gepleisterd portaal dat 0.7 m uitsteekt, boogopening, gebogen pannenkap, pijlers met stenen bollen
    Mu, _ = wandframe((3.81, 5.47), (4.22, 6.57), (8.0, 5.5))
    put("achter", "stuc", organisch(bz(-1.05, 1.05, -0.7, 0.05, -0.05, 2.75, 0.03), 0.04, 3, 0.4, 0.02, 1.0, 0.2), Mu)
    put("achter", "donker", boutline(arch_pts(0, 0.0, 1.2, 2.2, 10), -0.74, 0.8), Mu)
    put("achter", "stuc", band(arch_pts(0, 0.0, 1.2, 2.2, 10), 0.12, -0.78, 0.08), Mu)
    put("achter", "pannen", prism_x([(0.0, 3.05), (-0.45, 2.92), (-0.8, 2.74), (-0.8, 2.66), (-0.45, 2.82), (0.0, 2.95)], -1.1, 1.1), Mu @ Matrix.Translation((0, -0.32, 0)))
    for sx in (-1.25, 1.25):
        put("achter", "stuc", bz(sx - 0.22, sx + 0.22, -0.78, -0.3, -0.05, 3.1, 0.03), Mu)
        put("achter", "stuc", bz(sx - 0.27, sx + 0.27, -0.83, -0.25, 3.1, 3.22, 0.02), Mu)
        put("achter", "stuc", ell((sx, -0.54, 3.42), (0.2, 0.2, 0.2), 12, 8), Mu)
    # groene houten afscheiding achter de uitgang (backstage), 2.2 m
    for (a, b) in (((4.5, 6.9), (7.6, 6.75)), ((7.6, 6.75), (10.0, 6.6))):
        Mg, Lg = wandframe(a, b, (6.0, 3.0))
        put("achter", "groenhout", bz(-Lg / 2, Lg / 2, -0.03, 0.03, 0.0, 2.2), Mg)
        k = -Lg / 2
        while k < Lg / 2:
            put("achter", "groenhout", bz(k, k + 0.012, -0.045, -0.03, 0.05, 2.15), Mg); k += 0.14
        for xx in (-Lg / 2, Lg / 2): put("achter", "groenhout", bz(xx - 0.05, xx + 0.05, -0.05, 0.05, 0.0, 2.3), Mg)
        coll_box((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 1.1, Lg, 0.15, 2.2, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
    # lantaarn op de pijler naast de ingang (foto)
    lx, ly = 3.96, 3.13
    put("achter", "ijzer", blathe([(0, 4.62), (0.06, 4.62), (0.05, 5.15), (0, 5.15)], 8), TR(lx, ly))
    put("achter", "glaslamp", blathe([(0, 5.15), (0.11, 5.15), (0.15, 5.5), (0, 5.5)], 6), TR(lx, ly, 0, 30))
    put("achter", "ijzer", blathe([(0, 5.48), (0.2, 5.5), (0.16, 5.58), (0.04, 5.72), (0, 5.75)], 6), TR(lx, ly, 0, 30))
    LAMPS_.append([lx, ly, 5.35])
    for poly in (AR, AL):                                                                                 # muren als botsblokken (geen mesh-botsing op concave vormen)
        for a, b in zip(poly, poly[1:]):
            coll_box((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 2.2, math.hypot(b[0] - a[0], b[1] - a[1]) + 0.3, 0.6, 4.4, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
    coll_box(1.2, 4.6, 2.2, 4.0, 3.6, 4.4, 0); coll_box(-5.0, 3.6, 1.8, 3.4, 2.8, 3.6, 0)
    # ================= botsing rots/poort (grot en water niet beloopbaar) =================
    coll_box(4.6, -0.4, 1.7, 4.6, 4.0, 4.0)
    coll_box(-3.0, -1.0, 1.7, 6.5, 6.0, 4.0, ANG)
    # ================= grot uitsnijden uit de rots (elk tunnelstuk apart: een samengevoegde snijder met overlap gaf een lege rots) =================
    snij(lambda k: k == ("rots", "donker"), GROT)
    # ================= wegschrijven =================
    for (part, mat), bm in PARTS.items():
        ob = new_mesh_object(f"ZZ_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": [l for l in LAMPS_ if l]}, open(os.path.join(out, "kasteel_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
