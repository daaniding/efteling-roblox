"""03_decor Pinokkio (2016): La Bottega di Geppetto, muur met groene poort, nis van Vos en Kat met tonnen en touwnet, haventje (kade, hek met
net, boei, meerpaal), plein. Bronnen: Pinokkio_ontwerp_huisje.jpg (vooraanzicht, 4.9 m breed = BAG), Pinokkiowerkplaats.jpg, Botega_rjj.jpg,
Pinokkiototaal.jpg, Pinokkio_kat_en_vos_2021.jpg, Pinokkio_monstervis*.jpg, OSM 405610268 (bottega), 405610269 (nis), 405610270 (vijver),
766787185/186 (hekken), 766787189 (muur), 405610267 (plein).
Modelframe: oorsprong = zwaartepunt BAG 405610268 = studs (149.16, 182.31); -Y = voorkant (NNW, naar het plein); +X = rechts voor de kijker;
z = 0 maaiveld. OSM -> model: X = -0.931*ox - 0.364*oy ; Y = 0.364*ox - 0.931*oy.
Gebruik: Blender -b -P 03_decor.py -- --master PK_decor_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.86, 0.8, 0.68, 1), 0.9), "pannen": ((0.55, 0.32, 0.22, 1), 0.85), "hout": ((0.24, 0.16, 0.1, 1), 0.8), "balk": ((0.22, 0.15, 0.1, 1), 0.8),
        "teal": ((0.26, 0.46, 0.46, 1), 0.6), "venster": ((0.05, 0.06, 0.07, 1), 0.3), "glasoranje": ((1.0, 0.72, 0.4, 1), 0.2), "ijzer": ((0.06, 0.06, 0.06, 1), 0.45),
        "natuursteen": ((0.74, 0.7, 0.62, 1), 0.9), "flagstone": ((0.66, 0.6, 0.52, 1), 0.9), "baksteen": ((0.55, 0.3, 0.22, 1), 0.9), "goud": ((0.8, 0.6, 0.2, 1), 0.3),
        "bord": ((0.85, 0.75, 0.55, 1), 0.7), "touw": ((0.6, 0.5, 0.34, 1), 0.95), "vat": ((0.4, 0.27, 0.15, 1), 0.8), "wit": ((0.92, 0.92, 0.9, 1), 0.6),
        "blauw": ((0.2, 0.42, 0.7, 1), 0.5), "grind": ((0.86, 0.83, 0.76, 1), 0.95), "rood": ((0.7, 0.15, 0.1, 1), 0.6)}
def m(ox, oy): return (-0.931 * ox - 0.364 * oy, 0.364 * ox - 0.931 * oy)
OSM = json.load(open(os.path.join(ROOT, "ref", "osm_lokaal.json")))
def way(i): return [m(*p) for p in next(w for w in OSM["ways"] if w["id"] == i)["pts"]]
X0, X1, YF, YB = -2.8, 2.1, -1.2, 2.08          # huis (gevel op -1.2; luifel tot -2.7 = BAG-voorkant)
YL = -2.7; EAVE = 3.1; RIDGE = 5.6; XC = (X0 + X1) / 2


def plaat(poly, z, dik, part, mat):
    bm = bmesh.new(); t = [bm.verts.new((x, y, z)) for x, y in poly]; b = [bm.verts.new((x, y, z - dik)) for x, y in poly]
    bm.faces.new(t); bm.faces.new(b[::-1])
    for i in range(len(poly)): bm.faces.new((t[i], b[i], b[(i + 1) % len(poly)], t[(i + 1) % len(poly)]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update()
    if sum(f.normal.z for f in bm.faces[:1]) < 0:
        for f in bm.faces: f.normal_flip()
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], ngon_method="EAR_CLIP")
    put(part, mat, bm)


def gesneden_kolom(x, y, h):
    """houtsnijwerk-kolom met 5 uilen (PinokkioKolomUilen): blok-voet, getordeerde schacht met koppen, kapiteel met krul"""
    put("luifel", "hout", bz(x - 0.17, x + 0.17, y - 0.17, y + 0.17, 0, 0.55, 0.02))
    put("luifel", "balk", blathe([(0, 0.55), (0.11, 0.55), (0.12, 0.62), (0.09, 0.7), (0.0, 0.7)], 10), TR(x, y, 0))
    for k in range(5):
        z = 0.7 + k * (h - 1.0) / 5
        put("luifel", "balk", blathe([(0, z), (0.085, z), (0.1, z + 0.08), (0.11, z + 0.2), (0.095, z + (h - 1.0) / 5 - 0.06), (0.0, z + (h - 1.0) / 5)], 10), TR(x, y, 0))
        for s in (-1, 1): put("luifel", "balk", ell((x + s * 0.045, y - 0.095, z + 0.2), (0.03, 0.02, 0.03), 6, 4))           # uilenogen
        put("luifel", "balk", ell((x, y - 0.1, z + 0.14), (0.02, 0.025, 0.035), 6, 4))
    put("luifel", "balk", blathe([(0, h - 0.3), (0.1, h - 0.3), (0.16, h - 0.12), (0.2, h), (0, h)], 10), TR(x, y, 0))
    coll_box(x, y, h / 2, 0.36, 0.36, h)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ================= bottega: gestucte muren met boogramen, dubbele deur, zijdeur =================
    mur = bmesh.new()
    def addb(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); mur.from_mesh(me_); bpy.data.meshes.remove(me_)
    addb(bz(X0, X0 + 0.3, YF, YB, -0.1, EAVE + 0.15)); addb(bz(X1 - 0.3, X1, YF, YB, -0.1, EAVE + 0.15)); addb(bz(X0, X1, YB - 0.3, YB, -0.1, EAVE + 0.15))
    # voorgevel met openingen: raam links (x -1.95..-1.05), deur (-0.7..0.7 -> verschoven naar XC), raam rechts
    xs = [(X0, -1.95 + XC), (-1.05 + XC, -0.7 + XC), (0.7 + XC, 1.05 + XC), (1.95 + XC, X1)]
    for a, b in xs: addb(bz(a, b, YF, YF + 0.3, -0.1, EAVE + 0.15))
    for a, b in ((-1.95 + XC, -1.05 + XC), (1.05 + XC, 1.95 + XC)):
        addb(bz(a, b, YF, YF + 0.3, -0.1, 0.75)); addb(bz(a, b, YF, YF + 0.3, 2.15, EAVE + 0.15))
    addb(bz(-0.7 + XC, 0.7 + XC, YF, YF + 0.3, 2.25, EAVE + 0.15))
    # zijgevels tot onder het dak (driehoek rechts en links)
    for xg in (X0, X1 - 0.3):
        tri = bmesh.new(); pts = [(YF - 0.05, EAVE), (YB + 0.05, EAVE), ((YF + YB) / 2, RIDGE - 0.15)]
        va = [tri.verts.new((xg, y, z)) for y, z in pts]; vb = [tri.verts.new((xg + 0.3, y, z)) for y, z in pts]
        tri.faces.new(va); tri.faces.new(vb[::-1])
        for i in range(3): tri.faces.new((va[i], vb[i], vb[(i + 1) % 3], va[(i + 1) % 3]))
        bmesh.ops.recalc_face_normals(tri, faces=tri.faces); addb(tri)
    put("muren", "stuc", organisch(mur, 0.05, 3, 0.5, 0.025, 1.2, 0.14))
    coll_box(XC, (YF + YB) / 2, 1.6, X1 - X0, YB - YF, 3.2)
    for xc in (-1.5 + XC, 1.5 + XC):                                                                     # boogramen met roeden en vensterbank
        ap = arch_pts(xc, 0.75, 0.9, 1.4, 10)
        put("ramen", "venster", boutline(ap, YF + 0.12, 0.04))
        put("ramen", "teal", band(ap, 0.07, YF + 0.06, 0.1))
        for k in (1, 2): put("ramen", "teal", bz(xc - 0.45 + 0.9 * k / 3 - 0.015, xc - 0.45 + 0.9 * k / 3 + 0.015, YF + 0.04, YF + 0.08, 0.75, 1.95))
        for k in (1, 2, 3): put("ramen", "teal", bz(xc - 0.45, xc + 0.45, YF + 0.04, YF + 0.08, 0.75 + k * 0.3 - 0.015, 0.75 + k * 0.3 + 0.015))
        put("ramen", "hout", bz(xc - 0.55, xc + 0.55, YF - 0.22, YF + 0.05, 0.62, 0.72, 0.01))
        for s in (-1, 1): put("ramen", "hout", bz(xc + s * 0.42 - 0.04, xc + s * 0.42 + 0.04, YF - 0.2, YF, 0.45, 0.62))
        LAMPS_.append([round(xc, 2), YF + 0.8, 1.4])
    dp = arch_pts(XC, 0.0, 1.4, 2.25, 10)                                                                 # dubbele deur, glas met roeden
    put("deur", "teal", boutline(dp, YF + 0.1, 0.06))
    for s in (-1, 1):
        for r_ in range(4):
            for c_ in range(2):
                x0 = XC + s * 0.08 + (0 if s > 0 else -0.6) + c_ * 0.28 + 0.04; z0 = 0.9 + r_ * 0.3
                put("deur", "venster", bz(x0, x0 + 0.22, YF + 0.06, YF + 0.1, z0, z0 + 0.25))
    put("deur", "hout", bz(XC - 0.01, XC + 0.01, YF + 0.04, YF + 0.1, 0, 2.0))
    for s in (-1, 1): put("deur", "ijzer", ell((XC + s * 0.08, YF + 0.03, 1.05), (0.035, 0.035, 0.035), 8, 6))
    put("deur", "hout", bz(XC - 0.6, XC + 0.6, YF - 0.05, YF + 0.06, 1.9, 1.96))                       # CHIUSO-bordje
    put("deur", "bord", bz(XC + 0.12, XC + 0.45, YF + 0.02, YF + 0.04, 1.3, 1.55))
    # zijdeur rechts met uithangbord (trekpopje) aan een krularm, bakstenen stoepje
    Md = Matrix.Translation((X1 + 0.01, -0.08, 0)) @ Matrix.Rotation(math.radians(-90), 4, "Z")
    put("deur", "teal", boutline(arch_pts(0, 0, 0.85, 2.1, 10), -0.05, 0.06), Md)
    put("deur", "baksteen", bz(X1, X1 + 0.6, -0.65, 0.5, 0, 0.18, 0.01)); put("deur", "baksteen", bz(X1, X1 + 0.32, -0.65, 0.5, 0.18, 0.34, 0.01))
    put("bord", "ijzer", btube([(X1 + 0.01, -0.85, 2.55), (X1 + 0.75, -0.85, 2.55), (X1 + 0.85, -0.85, 2.48)], 0.02, 6))
    put("bord", "ijzer", btube([(X1 + 0.01, -0.85, 2.2), (X1 + 0.45, -0.85, 2.55)], 0.015, 5))
    put("bord", "teal", bz(X1 + 0.35, X1 + 0.95, -0.88, -0.82, 1.85, 2.48, 0.01))
    put("bord", "bord", bz(X1 + 0.42, X1 + 0.88, -0.89, -0.81, 1.92, 2.4))
    put("bord", "rood", ell((X1 + 0.65, -0.895, 2.15), (0.06, 0.01, 0.12), 8, 6))
    # ================= luifel op 4 gesneden kolommen, met naambord =================
    HL = 2.55
    for xk in (-1.96, -0.8, 0.85, 1.96): gesneden_kolom(xk + XC, YL + 0.18, HL)
    put("luifel", "balk", bz(X0 - 0.1, X1 + 0.1, YL - 0.02, YL + 0.36, HL, HL + 0.28, 0.02))                  # lijstbalk
    for xk in (-1.96, -0.8, 0.85, 1.96):                                                                         # boogjes met booguil tussen de kolommen
        pass
    for a, b in ((-1.96, -0.8), (-0.8, 0.85), (0.85, 1.96)):
        xa, xb = a + XC + 0.12, b + XC - 0.12; mid = (xa + xb) / 2
        pts = [(xa + (xb - xa) * i / 10, HL - 0.05 - 0.28 * math.sin(math.pi * i / 10)) for i in range(11)]
        put("luifel", "balk", band(pts[::-1], 0.08, YL + 0.12, 0.12))
        put("luifel", "balk", ell((mid, YL + 0.1, HL - 0.12), (0.22, 0.06, 0.1), 10, 6))
    for k in range(6):                                                                                            # balkjes naar de gevel
        x = X0 + 0.2 + k * (X1 - X0 - 0.4) / 5; put("luifel", "balk", bz(x - 0.06, x + 0.06, YL + 0.1, YF + 0.1, HL + 0.05, HL + 0.22))
    put("luifel", "flagstone", bz(X0 - 0.15, X1 + 0.15, YL - 0.1, YF + 0.05, 0.0, 0.05))                  # flagstones onder de luifel
    rr = random.Random(4)
    for k in range(40): x = rr.uniform(X0, X1); y = rr.uniform(YL - 0.05, YF); put("luifel", "natuursteen", bz(x - 0.004, x + 0.004, YL - 0.1, YF, 0.05, 0.052) if rr.random() < 0 else bz(x - 0.25, x + 0.25, y - 0.003, y + 0.003, 0.05, 0.053))
    lp = [(YL - 0.25, HL + 0.15), (YF + 0.15, HL + 0.62), (YF + 0.15, HL + 0.74), (YL - 0.25, HL + 0.27)]
    put("luifeldak", "hout", prism_x(lp, X0 - 0.25, X1 + 0.25))
    tiles(X0 - 0.25, X1 + 0.25, (YL - 0.25, HL + 0.27), (YF + 0.15, HL + 0.74), "luifeldak", seed=2)
    # naambord LA BOTTEGA DI GEPPETTO op de luifel (Pinokkiowerkplaats)
    put("naambord", "blauw", bz(XC - 1.15, XC + 1.15, YL + 0.1, YL + 0.16, HL + 0.45, HL + 1.15, 0.02))
    put("naambord", "bord", bz(XC - 1.07, XC + 1.07, YL + 0.08, YL + 0.12, HL + 0.52, HL + 1.05))
    put("naambord", "rood", bz(XC - 1.0, XC + 1.0, YL + 0.075, YL + 0.08, HL + 0.56, HL + 0.6))
    put("naambord", "goud", ell((XC, YL + 0.075, HL + 0.95), (0.18, 0.01, 0.07), 10, 6))
    cu = bpy.data.curves.new("_txt", "FONT"); cu.body = "LA BOTTEGA DI GEPPETTO"; cu.size = 0.16; cu.extrude = 0.008; cu.align_x = "CENTER"
    to = bpy.data.objects.new("_txt", cu); bpy.context.scene.collection.objects.link(to)
    to.rotation_euler = (math.radians(90), 0, 0); to.location = (XC, YL + 0.07, HL + 0.7)
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    tme = bpy.data.meshes.new_from_object(to.evaluated_get(dg)); tme.transform(to.matrix_world)
    tb = bmesh.new(); tb.from_mesh(tme); bpy.data.meshes.remove(tme); bpy.data.objects.remove(to, do_unlink=True)
    bmesh.ops.triangulate(tb, faces=tb.faces[:]); put("naambord", "hout", tb)
    # ================= hoofddak: golvend pannendak met opkrullende randen, dakkapel, schoorsteen, windwijzer =================
    def dakz(x, y, side):
        t = abs(y - (YF + YB) / 2) / ((YB - YF) / 2 + 0.35)
        base = RIDGE - (RIDGE - EAVE) * t
        e = (x - XC) / ((X1 - X0) / 2 + 0.3)
        return base + 0.25 * e ** 4 + 0.08 * math.sin(x * 1.3) * t                       # randen krullen op (ontwerptekening)
    rows = 18
    for side in (-1, 1):
        ys = (YF + YB) / 2; ye = YF - 0.35 if side < 0 else YB + 0.35
        for r_ in range(rows):
            t0 = r_ / rows
            y = ys + (ye - ys) * (1 - t0); yy2 = ys + (ye - ys) * (1 - (r_ + 1.3) / rows)
            xx = X0 - 0.3 + (0.1 if r_ % 2 else 0)
            while xx < X1 + 0.3:
                w = random.uniform(0.2, 0.26)
                cx = xx + w / 2; za = dakz(cx, y, side); zb = dakz(cx, yy2, side)
                bm = bmesh.new()
                q = [(xx, y, za + 0.04), (xx + w - 0.015, y, dakz(xx + w, y, side) + 0.04), (xx + w - 0.015, yy2, dakz(xx + w, yy2, side) + 0.07), (xx, yy2, zb + 0.07)]
                v = [bm.verts.new(p) for p in q] + [bm.verts.new((p[0], p[1], p[2] - 0.035)) for p in q]
                for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([v[i] for i in f])
                bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("dak", "pannen", bm)
                xx += w
    ond = bmesh.new()                                                                                      # dakbeschot (dicht)
    N = 14; P = [[ond.verts.new((X0 - 0.3 + (X1 - X0 + 0.6) * i / N, YF - 0.35 + (YB - YF + 0.7) * j / N, 0)) for j in range(N + 1)] for i in range(N + 1)]
    for i in range(N + 1):
        for j in range(N + 1):
            v = P[i][j]; v.co.z = dakz(v.co.x, v.co.y, 0) - 0.02
    for i in range(N):
        for j in range(N): ond.faces.new((P[i][j], P[i + 1][j], P[i + 1][j + 1], P[i][j + 1]))
    r_ = bmesh.ops.extrude_face_region(ond, geom=list(ond.faces)); top = [g for g in r_["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(ond, vec=(0, 0, -0.12), verts=top); bmesh.ops.recalc_face_normals(ond, faces=ond.faces); put("dak", "hout", ond)
    put("dak", "pannen", btube([(X0 - 0.3, (YF + YB) / 2, dakz(X0 - 0.3, (YF + YB) / 2, 0) + 0.06), (XC, (YF + YB) / 2, RIDGE + 0.06), (X1 + 0.3, (YF + YB) / 2, dakz(X1 + 0.3, (YF + YB) / 2, 0) + 0.06)], 0.08, 6))
    # windveren rechts (zijgevel met planken)
    for side in (-1, 1):
        pts = [(X1 + 0.32, YF - 0.35 if side < 0 else YB + 0.35, EAVE - 0.05), (X1 + 0.32, (YF + YB) / 2, RIDGE + 0.2)]
        put("dak", "bord", btube([(p[0], p[1], p[2]) for p in pts], 0.07, 4))
    # dakkapel: blauwgroen planken, 2 raampjes met luiken, puntdak
    dx0, dx1, dy = XC - 0.85, XC + 0.85, YF - 0.1; dz0 = dakz(XC, dy, 0) - 0.3
    put("dakkapel", "teal", bz(dx0, dx1, dy, dy + 1.2, dz0, dz0 + 1.25))
    for k in range(9): x = dx0 + k * (dx1 - dx0) / 8; put("dakkapel", "hout", bz(x - 0.008, x + 0.008, dy - 0.01, dy, dz0, dz0 + 1.25))
    gp = [(dx0 - 0.15, dz0 + 1.2), (dx1 + 0.15, dz0 + 1.2), (XC, dz0 + 2.0)]
    put("dakkapel", "teal", prism_x([(0, 0)], 0, 0) if False else bmesh_gevel(gp, dy - 0.02, dy + 1.2))
    for s in (-1, 1):
        put("dakkapel", "bord", btube([(XC + s * (0.85 + 0.25), dy - 0.12, dz0 + 1.15), (XC, dy - 0.12, dz0 + 2.08)], 0.06, 4))
        put("dakkapel", "pannen", bz(min(XC, XC + s * 1.1), max(XC, XC + s * 1.1), dy - 0.1, dy + 1.3, dz0 + 1.6 - 0.4 * 0, dz0 + 1.62) if False else
            roof_side(XC, XC + s * 1.1, dy - 0.15, dy + 1.4, dz0 + 2.1, dz0 + 1.15))
    for xc in (XC - 0.32, XC + 0.32):
        put("dakkapel", "venster", bz(xc - 0.22, xc + 0.22, dy - 0.04, dy, dz0 + 0.3, dz0 + 0.95))
        put("dakkapel", "hout", bz(xc - 0.01, xc + 0.01, dy - 0.06, dy - 0.04, dz0 + 0.3, dz0 + 0.95)); put("dakkapel", "hout", bz(xc - 0.22, xc + 0.22, dy - 0.06, dy - 0.04, dz0 + 0.62, dz0 + 0.64))
    for s in (-1, 1): put("dakkapel", "teal", bz(XC + s * 0.62 - 0.17, XC + s * 0.62 + 0.17, dy - 0.07, dy - 0.04, dz0 + 0.28, dz0 + 0.98, 0.005))
    put("dakkapel", "ijzer", btube([(XC, dy - 0.05, dz0 + 2.0), (XC, dy - 0.05, dz0 + 2.6)], 0.015, 5))
    LAMPS_.append([round(XC, 2), dy + 0.4, round(dz0 + 0.6, 2)])
    sch = organisch(bz(X0 - 0.15, X0 + 0.45, YB - 1.4, YB - 0.7, -0.1, RIDGE + 1.1), 0.05, 6, 0.6, 0.03, 1.0, 0.18)   # schoorsteen links achter
    put("schoorsteen", "stuc", sch)
    put("schoorsteen", "pannen", roof_side(X0 - 0.25, X0 + 0.55, YB - 1.5, YB - 0.6, RIDGE + 1.45, RIDGE + 1.15, as_hood=True))
    put("windwijzer", "ijzer", btube([(X1 - 0.6, (YF + YB) / 2, RIDGE + 0.1), (X1 - 0.6, (YF + YB) / 2, RIDGE + 1.1)], 0.015, 5))
    put("windwijzer", "ijzer", bz(X1 - 0.9, X1 - 0.3, (YF + YB) / 2 - 0.005, (YF + YB) / 2 + 0.005, RIDGE + 0.82, RIDGE + 1.0))
    # ================= muur met groene poort naar de nis (OSM 766787189) =================
    W = way("766787189")
    seg = [Vector((p[0], p[1])) for p in W]
    GX = 5.13; stukken = []
    for a, b in zip(seg, seg[1:]):                                                                          # muur open bij de poort
        if a.x < GX - 0.7 < b.x: t = (GX - 0.7 - a.x) / (b.x - a.x); stukken.append((a, a.lerp(b, t)))
        elif a.x < GX + 0.7 < b.x: t = (GX + 0.7 - a.x) / (b.x - a.x); stukken.append((a.lerp(b, t), b))
        elif a.x >= GX - 0.7 and b.x <= GX + 0.7: continue
        else: stukken.append((a, b))
    for a, b in stukken:
        L = (b - a).length; d = (b - a).normalized(); ang = math.degrees(math.atan2(d.y, d.x)); mid = (a + b) / 2
        put("muur", "stuc", organisch(bz(-L / 2 - 0.1, L / 2 + 0.1, -0.15, 0.15, -0.1, 1.75), 0.05, 2, 0.4, 0.02, 1.2, 0.3), TR(mid.x, mid.y, 0, ang))
        coll_box(mid.x, mid.y, 1.0, L, 0.35, 2.0, ang)
    gx = 5.13; gy = 1.67                                                                                      # poort op het OSM-dienstingangpunt
    for s in (-1, 1):
        px = gx + s * 0.95
        put("poort", "stuc", organisch(bz(px - 0.22, px + 0.22, gy - 0.22, gy + 0.22, -0.1, 2.05), 0.04, 2, 0.4, 0.015, 1.2, 0.35))
        put("poort", "natuursteen", bz(px - 0.26, px + 0.26, gy - 0.26, gy + 0.26, 2.05, 2.15, 0.01))
        put("poort", "natuursteen", ell((px, gy, 2.32), (0.15, 0.15, 0.15), 10, 8))
    gpts = [(gx - 0.73 + 1.46 * i / 12, 1.85 + 0.2 * math.sin(math.pi * i / 12)) for i in range(13)]
    gb = bmesh.new(); top_ = [gb.verts.new((x, gy - 0.04, z)) for x, z in gpts]; bot = [gb.verts.new((x, gy - 0.04, 0.05)) for x, z in gpts]
    ver = top_ + bot[::-1]; gb.faces.new(ver); r2 = bmesh.ops.extrude_face_region(gb, geom=list(gb.faces))
    bmesh.ops.translate(gb, vec=(0, 0.08, 0), verts=[g for g in r2["geom"] if isinstance(g, bmesh.types.BMVert)]); bmesh.ops.recalc_face_normals(gb, faces=gb.faces)
    put("poort", "teal", gb)
    for k in range(1, 9): x = gx - 0.73 + 1.46 * k / 9; put("poort", "hout", bz(x - 0.006, x + 0.006, gy - 0.05, gy - 0.04, 0.05, 1.85))
    for z in (0.4, 1.5):
        for s in (-1, 1): put("poort", "ijzer", btube([(gx + s * 0.7, gy - 0.06, z), (gx + s * 0.15, gy - 0.06, z), (gx + s * 0.08, gy - 0.06, z + 0.05)], 0.02, 5))
    coll_box(gx, gy, 1.0, 2.4, 0.3, 2.0)
    # ================= nis van Vos en Kat (OSM 405610269) =================
    nx, ny = 8.13, -0.07; nang = math.degrees(math.atan2(0.55 - 1.82, 7.87 - 7.32)) + 90
    Mn = TR(nx, ny, 0, -30)
    nb = bz(-0.8, 0.8, -0.45, 0.45, -0.1, 2.6)
    put("nis", "stuc", organisch(nb, 0.04, 2, 0.4, 0.02, 1.2, 0.3), Mn)
    ap = [(x, z) for x, z in arch_pts(0, 0.9, 0.95, 1.35, 10)]
    put("nis", "venster", boutline(ap, -0.47, 0.05), Mn)
    put("nis", "natuursteen", band(ap, 0.1, -0.5, 0.08), Mn)
    put("nis", "natuursteen", bz(-0.6, 0.6, -0.6, -0.4, 0.82, 0.92, 0.01), Mn)
    put("nis", "pannen", roof_side(0.0, -1.0, -0.65, 0.65, 3.25, 2.55), Mn); put("nis", "pannen", roof_side(0.0, 1.0, -0.65, 0.65, 3.25, 2.55), Mn)
    put("nis", "bord", bz(-0.5, 0.5, -0.47, -0.45, 2.15, 2.5), Mn)
    coll_box(nx, ny, 1.3, 1.7, 1.0, 2.6, -30)
    rr = random.Random(9)
    for k, (dx, dy, s_) in enumerate([(-0.5, -1.0, 1.0), (0.2, -1.2, 0.9), (0.85, -0.85, 1.1), (-1.1, -1.3, 0.85), (0.5, -1.7, 0.8), (-0.2, -1.6, 1.0), (1.2, -1.4, 0.9)]):
        ww = Mn @ Vector((dx, dy, 0))
        h = 0.95 * s_; r0 = 0.32 * s_
        prof = [(0, 0), (r0 * 0.88, 0), (r0, h * 0.25), (r0 * 1.06, h * 0.5), (r0, h * 0.75), (r0 * 0.88, h), (0, h)]
        put("tonnen", "vat", blathe(prof, 14), TR(ww.x, ww.y, 0, rr.uniform(0, 360)))
        for zz in (0.1, 0.3, 0.7, 0.9): put("tonnen", "ijzer", blathe([(r0 * (0.9 + 0.16 * math.sin(math.pi * zz)) + 0.012, h * zz - 0.02), (r0 * (0.9 + 0.16 * math.sin(math.pi * zz)) + 0.012, h * zz + 0.02), (0, h * zz + 0.02), (0, h * zz - 0.02)], 14), TR(ww.x, ww.y, 0))
        coll_box(ww.x, ww.y, h / 2, r0 * 2, r0 * 2, h)
    # touwnet-hek met ijzeren palen (OSM 766787185) en hek langs het haventje (OSM 766787186)
    for wid, hh in (("766787185", 0.95), ("766787186", 1.05)):
        P_ = [Vector(p) for p in way(wid)]
        for a, b in zip(P_, P_[1:]):
            L = (b - a).length; n_ = max(1, int(L / 1.4 + 0.5))
            for k in range(n_ + 1):
                p = a.lerp(b, k / n_)
                put("hekken", "ijzer", btube([(p.x, p.y, 0), (p.x, p.y, hh)], 0.035, 6)); put("hekken", "ijzer", ell((p.x, p.y, hh + 0.05), (0.06, 0.06, 0.06), 8, 6))
            put("hekken", "ijzer", btube([(a.x, a.y, hh), (b.x, b.y, hh)], 0.025, 6)); put("hekken", "ijzer", btube([(a.x, a.y, 0.12), (b.x, b.y, 0.12)], 0.02, 5))
            d = (b - a).normalized(); nn = Vector((-d.y, d.x))
            m_ = max(2, int(L / 0.16))
            for k in range(m_ + 1):                                                                            # net: diagonale touwtjes
                for s in (-1, 1):
                    t0 = k / m_; t1 = min(1.0, max(0.0, t0 + s * 0.1))
                    p0 = a.lerp(b, t0); p1 = a.lerp(b, t1)
                    put("hekken", "touw", btube([(p0.x, p0.y, 0.14), (p1.x, p1.y, hh - 0.02)], 0.008, 3))
            ang = math.degrees(math.atan2(d.y, d.x)); mid = (a + b) / 2; coll_box(mid.x, mid.y, 0.6, L, 0.15, 1.2, ang)
    # reddingsboei aan het havenhek en gestreepte meerpaal (Pinokkioboei, Pinokkio_monstervis)
    bx, by = 11.6, -5.75
    put("haven", "wit", blathe([(0.22, -0.07), (0.32, -0.04), (0.34, 0.0), (0.32, 0.04), (0.22, 0.07), (0.2, 0.0)], 18), TR(bx, by, 0.75) @ Matrix.Rotation(math.radians(90), 4, "X") @ Matrix.Rotation(math.radians(0), 4, "Z"))
    for k in range(4):
        a = k * math.pi / 2
        put("haven", "rood", bz(-0.06, 0.06, -0.08, 0.08, -0.36, -0.18), TR(bx, by, 0.75) @ Matrix.Rotation(a, 4, "Y") @ Matrix.Rotation(math.radians(90), 4, "X"))
    for k in range(10):
        put("haven", "blauw" if k % 2 else "wit", blathe([(0, 0), (0.09, 0), (0.09, 0.3), (0, 0.3)], 10), TR(15.4, -12.2, k * 0.3))
    put("haven", "goud", ell((15.4, -12.2, 3.08), (0.12, 0.12, 0.12), 10, 8))
    # kademuurtje van witte natuursteen langs het plein-deel van de vijver
    V = way("405610270")
    for i in range(len(V) - 1):
        a, b = Vector(V[i]), Vector(V[i + 1])
        L = (b - a).length
        if L < 0.05: continue
        n_ = max(1, int(L / 0.55))
        for k in range(n_):
            p = a.lerp(b, (k + 0.5) / n_); d = (b - a).normalized()
            put("haven", "natuursteen", bz(-L / n_ / 2 - 0.02, L / n_ / 2 + 0.02, -0.22, 0.22, -0.35, 0.12, 0.03), TR(p.x, p.y, 0, math.degrees(math.atan2(d.y, d.x)) + random.uniform(-3, 3)))
    # ================= plein in licht grind (OSM 405610267) =================
    plaat(way("405610267")[:-1][::-1], 0.1, 0.12, "plein", "grind")
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"PK_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "vijver": [[round(x, 2), round(y, 2)] for x, y in V], "plein": [[round(x, 2), round(y, 2)] for x, y in way("405610267")]},
              open(os.path.join(out, "decor_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


def bmesh_gevel(pts, y0, y1):
    bm = bmesh.new(); a = [bm.verts.new((x, y0, z)) for x, z in pts]; b = [bm.verts.new((x, y1, z)) for x, z in pts]
    bm.faces.new(a); bm.faces.new(b[::-1])
    for i in range(len(pts)): bm.faces.new((a[i], b[i], b[(i + 1) % len(pts)], a[(i + 1) % len(pts)]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def roof_side(xr, xe, y0, y1, zr, ze, as_hood=False):
    """dakvlak (dikte 0.08) van nok (x = xr, z = zr) naar goot (x = xe, z = ze) over y0..y1"""
    bm = bmesh.new()
    q = [(xr, y0, zr), (xe, y0, ze), (xe, y1, ze), (xr, y1, zr)]
    v = [bm.verts.new(p) for p in q] + [bm.verts.new((p[0], p[1], p[2] - 0.08)) for p in q]
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def tiles(x0, x1, p0, p1, part, seed=1):
    """pannenrijen op een lessenaarsdak van (y0,z0) naar (y1,z1) over x0..x1"""
    r = random.Random(seed); (y0, z0), (y1, z1) = p0, p1; L = math.hypot(y1 - y0, z1 - z0); n = int(L / 0.17)
    for k in range(n):
        t0 = k / n; t1 = min(1, (k + 1.35) / n)
        ya, za = y0 + (y1 - y0) * t0, z0 + (z1 - z0) * t0 + 0.04; yb, zb = y0 + (y1 - y0) * t1, z0 + (z1 - z0) * t1 + 0.06
        xx = x0 + (0.1 if k % 2 else 0)
        while xx < x1:
            w = min(r.uniform(0.2, 0.26), x1 - xx)
            put(part, "pannen", roof_side(xx, xx + w - 0.015, ya, yb, za, zb) if False else _tile(xx, xx + w - 0.015, ya, yb, za, zb))
            xx += w


def _tile(xa, xb, ya, yb, za, zb):
    bm = bmesh.new(); q = [(xa, ya, za), (xb, ya, za), (xb, yb, zb), (xa, yb, zb)]
    v = [bm.verts.new(p) for p in q] + [bm.verts.new((p[0], p[1], p[2] - 0.03)) for p in q]
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
