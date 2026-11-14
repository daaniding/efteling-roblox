"""03_kasteel Doornroosje (Anton Pieck): zaal met trapgevel en arcade, binnenplaats met weergang/kantelen, vierkante toren (oostvleugel)
met tentdak, drie ronde torens (OSM 407/408/409) met uitlopende kegeldaken van pannenrijen en windvanen. Maten: asset-brief.md.
Modelframe = OSM-assen: x oost, y noord (m), oorsprong = zwaartepunt OSM 55423166, z = 0 maaiveld aan de voet van de heuvel; kasteelvloer Z0.
Gebruik: Blender -b -P 03_kasteel.py -- --master AR_Doornroosje_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.86, 0.84, 0.78, 1), 0.9), "pannen": ((0.5, 0.28, 0.2, 1), 0.85), "natuursteen": ((0.6, 0.58, 0.54, 1), 0.9),
        "hout": ((0.3, 0.32, 0.3, 1), 0.8), "venster": ((0.05, 0.05, 0.06, 1), 0.3), "glas": ((0.55, 0.5, 0.35, 1), 0.2),
        "ijzer": ((0.06, 0.06, 0.06, 1), 0.5), "goud": ((0.8, 0.62, 0.22, 1), 0.3), "binnen": ((0.12, 0.1, 0.08, 1), 0.9), "klimop": ((0.12, 0.22, 0.08, 1), 0.8), "lamp": ((1.0, 0.8, 0.5, 1), 0.3)}
RNG = random.Random(1952)
Z0 = 4.5                                     # kasteelvloer bovenop de rotsheuvel (Doornroosje-2024-15: kasteel ver boven de vijver)
TORENS = [("t409", -7.10, 2.85, 1.40, 4.8, 2.5), ("t408", -3.75, 5.45, 1.45, 5.4, 2.7), ("t407", 0.05, 5.70, 1.55, 6.0, 2.9)]   # naam, x, y, r, romp, dak


def ring_pts(cx, cy, r, z, n=24, a0=0.0): return [(cx + r * math.cos(a0 + k * math.tau / n), cy + r * math.sin(a0 + k * math.tau / n), z) for k in range(n)]


def kegeldak(part, cx, cy, z0, r, h, flare=0.9, course=0.16, segs=28):
    """kegeldak van pannenrijen: onderaan uitlopend (flare), elke rij een schuin bandje met een lip -> schaduwlijn per rij"""
    ov = 0.45                                                                    # brede overstek (Doornroosje-2024-15)
    prof = [(0.0, z0 - 0.06), (r + ov, z0 - 0.06)]
    n = max(6, int(math.hypot(r + ov, h) / course))
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        f = lambda t: (r + ov) * (1 - t) ** (1.0 + flare * (1 - t) ** 2), lambda t: z0 + h * t
        ra, za = f[0](t0), f[1](t0); rb, zb = f[0](t1), f[1](t1)
        prof += [(ra + 0.03, za), (rb, zb)]
    prof += [(0.0, z0 + h)]
    bm = blathe(prof, segs); bmesh.ops.translate(bm, vec=(cx, cy, 0), verts=bm.verts)
    for f in bm.faces: f.smooth = True
    put(part, "pannen", bm)
    put(part, "pannen", btube([(cx, cy, z0 + h - 0.05), (cx, cy, z0 + h + 0.25)], 0.05, 8))            # makelaar
    put(part, "ijzer", btube([(cx, cy, z0 + h + 0.2), (cx, cy, z0 + h + 1.1)], 0.02, 6))              # windvaanstang
    M = Matrix.Translation((cx, cy, z0 + h + 0.95)) @ Matrix.Rotation(RNG.uniform(0, 6.28), 4, "Z")
    put(part, "goud", bz(0.0, 0.5, -0.012, 0.012, -0.12, 0.18, 0.0), M)                                 # gouden ruiter-vaan (Kasteel_Doornroosje)
    put(part, "goud", ell((0.0, 0, 0.0), (0.05, 0.05, 0.05), 8, 6), M)


def glasraam(part, M, w, h):
    """rondboograam met glas-in-lood (amber) en ijzeren roeden, verdiept in de muur (Doornroosje_Ramen, -2024-07)"""
    if w < 0.2:                                                                                  # smal schietgat: donker
        put(part, "venster", boutline(arch_pts(0, 0, w, h, 8), -0.04, 0.1), M); return
    put(part, "glas", boutline(arch_pts(0, 0, w, h, 8), -0.07, 0.04), M)
    for k in range(1, 3): put(part, "ijzer", bz(-w / 2 + k * w / 3 - 0.012, -w / 2 + k * w / 3 + 0.012, -0.09, -0.07, 0.02, h - 0.05), M)
    for k in range(1, 4): put(part, "ijzer", bz(-w / 2 + 0.02, w / 2 - 0.02, -0.09, -0.07, k * h / 4.2 - 0.012, k * h / 4.2 + 0.012), M)
    put(part, "natuursteen", bz(-w / 2 - 0.08, w / 2 + 0.08, -0.12, 0.04, -0.07, 0.0, 0.01), M)        # vensterbank


def klimop(cx, cy, r, z0, h, ang, spread, n=90, seed=1):
    """klimop: plat bladtapijt tegen de torenvoet (losse blaadjes plat op het oppervlak, rafelige rand via ruis, dichter onderaan)"""
    R_ = random.Random(seed); bm = bmesh.new(); N_ = n * 9
    for _ in range(N_):
        t = R_.random() ** 1.4; a = ang + R_.uniform(-spread, spread); z = z0 + h * t
        edge = 0.55 + 0.45 * noise.noise(Vector((a * 2.2, z * 0.9, seed)))                       # rafelige omtrek
        if abs(a - ang) / spread > edge * (1.05 - 0.55 * t) or R_.random() < 0.05: continue
        nrm = Vector((math.cos(a), math.sin(a), 0)); rr = r + 0.03 + R_.uniform(0, 0.05)
        c = Vector((cx, cy, 0)) + nrm * rr + Vector((0, 0, z))
        lf = ell((0, 0, 0), (0.07 + R_.uniform(0, 0.04), 0.06 + R_.uniform(0, 0.03), 0.012), 6, 3)
        rot = Matrix((nrm.cross(Vector((0, 0, 1))), Vector((0, 0, 1)), nrm)).transposed().to_4x4() @ Matrix.Rotation(R_.uniform(0, 6.28), 4, "Z") @ Matrix.Rotation(R_.uniform(-0.5, 0.5), 4, "X")
        bmesh.ops.transform(lf, matrix=Matrix.Translation(c) @ rot, verts=lf.verts)
        me = bpy.data.meshes.new("_lf"); lf.to_mesh(me); lf.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    for f in bm.faces: f.smooth = True
    put("klimop", "klimop", bm)


def wandlamp(M):
    """zwarte smeedijzeren wandlantaarn op een arm (Doornroosje-2024-07)"""
    put("lampen", "ijzer", btube([(0, 0, 0), (0, -0.35, 0.1), (0, -0.42, 0.0)], 0.025, 6), M)
    put("lampen", "ijzer", blathe([(0, 0), (0.09, 0), (0.11, 0.05), (0.09, 0.3), (0.12, 0.33), (0.03, 0.42), (0, 0.45)], 6), M @ Matrix.Translation((0, -0.42, -0.4)))
    put("lampen", "lamp", blathe([(0, 0.06), (0.08, 0.06), (0.085, 0.28), (0, 0.28)], 6), M @ Matrix.Translation((0, -0.42, -0.4)))
    p_ = M @ Vector((0, -0.42, -0.25)); LAMPS_.append([round(p_.x, 3), round(p_.y, 3), round(p_.z, 3)])


def toren(part, cx, cy, r, romp, dak):
    """ronde gestuukte toren: licht taps, plint, gootlijst, smalle schietgaten en een rondboograampje naar buiten"""
    R_ = random.Random(int(cx * 100))
    prof = [(0, -0.6), (r * 1.08, -0.6), (r * 1.06, 0.5)]
    for k in range(1, 8):                                                                          # met de hand gestuukt: licht bollend en ingesnoerd
        t = k / 8; prof.append((r * (1.03 - 0.05 * t + 0.035 * math.sin(t * 5.0 + cx)), romp * t))
    prof += [(r + 0.14, romp - 0.08), (r + 0.16, romp), (0, romp)]
    bm = blathe(prof, 40)
    lean = Matrix.Rotation(R_.uniform(-0.025, 0.025), 4, "X") @ Matrix.Rotation(R_.uniform(-0.025, 0.025), 4, "Y")   # scheefstand ~1.5 graad
    bmesh.ops.transform(bm, matrix=Matrix.Translation((cx, cy, Z0)) @ lean, verts=bm.verts)
    for f in bm.faces: f.smooth = True                                                                # ronde toren zonder facetstrepen
    put(part, "stuc", bm)
    kegeldak(part, cx, cy, Z0 + romp, r + 0.1, dak)
    for k, (a, zr, w, h) in enumerate(((1.2, 0.55, 0.38, 0.75), (2.4, 0.35, 0.12, 0.5), (0.2, 0.75, 0.12, 0.45), (3.6, 0.6, 0.12, 0.45))):
        ang = a + (cx * 0.3); ox, oy = math.cos(ang), math.sin(ang); z = Z0 + romp * zr
        M = Matrix.Translation((cx + ox * (r - 0.06), cy + oy * (r - 0.06), z)) @ Matrix.Rotation(ang - math.pi / 2, 4, "Z")
        glasraam(part, M, w, h)
        put(part, "stuc", band(arch_pts(0, 0, w, h, 8), 0.06, -0.08, 0.08), M)                         # omlijsting
    coll_box(cx, cy, Z0 + romp / 2, r * 1.9, r * 1.9, romp)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, rr) in MATS.items(): material("MAT_" + n, c, rr)
    put("anker", "ijzer", bz(-0.01, 0.01, -0.01, 0.01, 0, 0.02))
    # ===== zaal (zuidblok): trapgevel west, pannendak oost-west, arcade met slaapkamer op het zuiden (Meting_1980, AanzichtKasteelBeneden) =====
    X0, X1, Y0, Y1 = -3.6, 0.85, -7.05, -3.9; GOOT = Z0 + 2.6; NOK = Z0 + 4.4
    put("zaal", "stuc", bz(X0, X1, Y0, Y1, -0.6, GOOT))
    yc = (Y0 + Y1) / 2
    for xg, s in ((X0, -1), (X1, 1)):                                                                   # gevels: west trapgevel, oost puntgevel
        if s < 0:
            for k in range(5):                                                                          # trapgevel: 5 treden per kant
                t0, t1 = k / 5, (k + 1) / 5
                for side in (-1, 1):
                    ya = yc + side * (Y1 - Y0) / 2 * (1 - t0); yb = yc + side * (Y1 - Y0) / 2 * (1 - t1)
                    put("zaal", "stuc", bz(xg - 0.05, xg + 0.35, min(ya, yb), max(ya, yb), GOOT, GOOT + (NOK - GOOT + 0.6) * t1 + 0.25))
            put("zaal", "stuc", bz(xg - 0.05, xg + 0.35, yc - 0.3, yc + 0.3, GOOT, NOK + 0.9))
        else:
            put("zaal", "stuc", prism_x([(Y0, GOOT), (Y1, GOOT), (yc, NOK)], xg - 0.35, xg + 0.05))
    tiled_roof("zaal", (X0 + 0.2, X1 + 0.25, Y0 - 0.35, Y1 + 0.35), (X0 + 0.2, X1 + 0.25, yc, yc), GOOT - 0.05, NOK, hips=False)
    for k in range(int((X1 - X0) / 0.32)):                                                                 # boogfries onder de goot (Meting_1980)
        x = X0 + 0.25 + k * 0.32
        put("zaal", "stuc", ell((x, Y0 - 0.06, GOOT - 0.25), (0.13, 0.08, 0.09), 8, 6))
    # arcade: drie rondbogen met zuiltjes, donker interieur erachter (slaapkamer Doornroosje)
    AX = [-2.3, -1.1, 0.1]
    for x in AX:
        put("zaal", "binnen", boutline(arch_pts(x, Z0 + 0.9, 1.0, 1.25, 10), Y0 + 0.05, 0.1))
        put("zaal", "stuc", band(arch_pts(x, Z0 + 0.9, 1.0, 1.25, 10), 0.09, Y0 - 0.08, 0.14))
    for x in (AX[0] - 0.55, -1.7, -0.5, AX[2] + 0.55):
        put("zaal", "natuursteen", blathe([(0, 0), (0.12, 0), (0.12, 0.08), (0.07, 0.12), (0.07, 1.05), (0.12, 1.12), (0.12, 1.2), (0, 1.2)], 12), TR(x, Y0 - 0.02, Z0 + 0.85))
    put("zaal", "natuursteen", bz(AX[0] - 0.7, AX[2] + 0.7, Y0 - 0.2, Y0 + 0.05, Z0 + 0.75, Z0 + 0.88, 0.02))   # vensterbank
    for x in (-3.0, 0.9):                                                                                    # kleine rondboogramen boven
        glasraam("zaal", Matrix.Translation((x, Y0 + 0.06, Z0 + 2.2)), 0.32, 0.6)
        put("zaal", "stuc", band(arch_pts(x, Z0 + 2.2, 0.32, 0.6, 8), 0.06, Y0 - 0.06, 0.08))
    put("zaal", "hout", boutline(arch_pts(-3.0, -0.0, 0.9, 1.6, 10), Y0 - 0.01, 0.08))                       # kelderdeur onder (Achterzijdedoonroosje)
    coll_box((X0 + X1) / 2, yc, (GOOT - 0.6) / 2, X1 - X0, Y1 - Y0, GOOT + 0.6)
    # ===== binnenplaats (smal noord-zuid blok) met weergang en kantelen (Doornroosje-2024-07, _Torens) =====
    BIN = [(-3.95, -3.9), (-0.2, -3.9), (-0.25, 0.9), (0.7, 1.2), (0.6, 2.9), (-1.3, 3.36), (-3.0, 3.14), (-3.96, 1.87)]
    HM = Z0 + 3.0
    for (ax, ay), (bx, by) in zip(BIN, BIN[1:] + BIN[:1]):
        L = math.hypot(bx - ax, by - ay); nx, ny = (by - ay) / L, -(bx - ax) / L
        bm = bmesh.new()
        q = [(ax, ay), (bx, by), (bx - nx * 0.45, by - ny * 0.45), (ax - nx * 0.45, ay - ny * 0.45)]
        lo = [bm.verts.new((x, y, -0.6)) for x, y in q]; hi = [bm.verts.new((x, y, HM)) for x, y in q]
        bm.faces.new(lo[::-1]); bm.faces.new(hi)
        for i in range(4): bm.faces.new((lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("muren", "stuc", bm)
        coll_box((ax + bx) / 2, (ay + by) / 2, (HM - 0.6) / 2, L, 0.5, HM + 0.6, math.degrees(math.atan2(by - ay, bx - ax)))
    kantelen(BIN + [BIN[0]], HM, "muren", "stuc", d=0.45)
    put("muren", "natuursteen", bz(-3.6, -0.5, -3.6, 2.6, Z0 - 0.05, Z0 + 0.02))                         # plaveisel binnenplaats
    # torentje met uitkragende zeskant-top op de binnenplaats (Doornroosje-2024-07)
    toren("torens", -1.6, 1.6, 0.95, 4.6, 2.0)
    # ===== oostvleugel: vierkante toren met tentdak (links in het noordaanzicht) =====
    EX0, EX1, EY0, EY1 = 3.0, 5.4, 1.85, 4.25; EH = Z0 + 5.6
    put("oost", "stuc", bz(EX0, EX1, EY0, EY1, -0.6, EH))
    put("oost", "stuc", bz(2.75, 5.4, 0.65, 1.95, -0.6, Z0 + 2.4))                                    # lagere aanbouw (rest van de OSM-vleugel), naast de trap
    tiled_roof("oost", (2.75, 5.55, 0.5, 2.1), (2.75, 5.55, 1.3, 1.3), Z0 + 2.35, Z0 + 3.3, hips=False)
    put("oost", "stuc", bz(EX0 - 0.12, EX1 + 0.12, EY0 - 0.12, EY1 + 0.12, EH - 0.25, EH))               # gootlijst
    tiled_roof("oost", (EX0 - 0.35, EX1 + 0.35, EY0 - 0.35, EY1 + 0.35), ((EX0 + EX1) / 2,) * 2 + ((EY0 + EY1) / 2,) * 2, EH - 0.05, EH + 3.4)
    kegel_top = ((EX0 + EX1) / 2, (EY0 + EY1) / 2)
    put("oost", "ijzer", btube([(kegel_top[0], kegel_top[1], EH + 3.3), (kegel_top[0], kegel_top[1], EH + 4.2)], 0.02, 6))
    for (x, y, nrm) in ((4.2, EY1, (0, 1)), (EX1, 3.05, (1, 0)), (EX0, 3.05, (-1, 0))):
        for zz, (w, h) in ((Z0 + 2.6, (0.4, 0.8)), (Z0 + 4.3, (0.12, 0.5))):
            ang = math.atan2(nrm[1], nrm[0]) - math.pi / 2
            M = Matrix.Translation((x - nrm[0] * 0.05, y - nrm[1] * 0.05, zz)) @ Matrix.Rotation(ang, 4, "Z")
            glasraam("oost", M, w, h)
            put("oost", "stuc", band(arch_pts(0, 0, w, h, 8), 0.06, -0.08, 0.08), M)
    coll_box((EX0 + EX1) / 2, (EY0 + EY1) / 2, (EH - 0.6) / 2, EX1 - EX0, EY1 - EY0, EH + 0.6)
    # verbindingsstuk tussen oostvleugel en zaal (OSM 166 midden) met poort (rondboog, AanzichtKasteelDoornroosje rechts)
    put("oost", "stuc", bz(0.4, 2.65, 1.95, 3.5, -0.6, Z0 + 3.4))                                  # poortgebouw boven de oosttrap
    put("oost", "binnen", boutline(arch_pts(1.45, Z0, 1.5, 2.4, 10), 1.93, 0.25))                      # poort naar de binnenplaats (zuidkant)
    put("oost", "stuc", band(arch_pts(1.45, Z0, 1.5, 2.4, 10), 0.14, 1.86, 0.18))
    kantelen([(0.4, 1.95), (2.65, 1.95)], Z0 + 3.4, "oost", "stuc", d=0.45)
    # ===== ronde torens 407/408/409 met weergang ertussen (noordzijde, over de vijver) =====
    for nm, x, y, r, romp, dak in TORENS: toren("torens", x, y, r, romp, dak)
    klimop(-7.10, 2.85, 1.42, Z0 - 0.3, 3.2, math.radians(110), 0.9, 110, 1)                         # klimop aan de vijverkant
    klimop(-3.75, 5.45, 1.47, Z0 - 0.3, 2.4, math.radians(80), 0.7, 80, 2)
    klimop(0.05, 5.70, 1.57, Z0 - 0.3, 1.8, math.radians(60), 0.6, 60, 3)
    klimop(4.2, 4.3, 1.4, Z0 - 0.3, 3.6, math.radians(90), 0.5, 90, 4)
    for x in (-3.3, 0.5):                                                                              # wandlampen naast de arcade
        wandlamp(Matrix.Translation((x, Y0 - 0.02, Z0 + 2.3)))
    wandlamp(Matrix.Translation((0.25, 1.9, Z0 + 2.6)) @ Matrix.Rotation(0, 4, "Z"))                     # naast de poort
    WALL = [(-7.1, 2.85), (-5.6, 4.6), (-3.75, 5.45), (-1.9, 6.0), (0.05, 5.7), (1.7, 4.6), (2.45, 4.0)]
    for (ax, ay), (bx, by) in zip(WALL, WALL[1:]):
        L = math.hypot(bx - ax, by - ay); nx, ny = (by - ay) / L, -(bx - ax) / L
        bm = bmesh.new(); q = [(ax, ay), (bx, by), (bx - nx * 0.5, by - ny * 0.5), (ax - nx * 0.5, ay - ny * 0.5)]
        lo = [bm.verts.new((x, y, -0.6)) for x, y in q]; hi = [bm.verts.new((x, y, Z0 + 2.6)) for x, y in q]
        bm.faces.new(lo[::-1]); bm.faces.new(hi)
        for i in range(4): bm.faces.new((lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("muren", "stuc", bm)
        coll_box((ax + bx) / 2, (ay + by) / 2, (Z0 + 2.0) / 2, L, 0.5, Z0 + 3.2, math.degrees(math.atan2(by - ay, bx - ax)))
    kantelen(WALL, Z0 + 2.6, "muren", "stuc", d=0.5)
    for (part, mat), bm in list(PARTS.items()):                                                   # stuc organisch: zachte dikke vormen, bobbels (Herberg-methode)
        if mat == "stuc" and len(bm.faces):
            PARTS[(part, mat)] = organisch(bm, voxel=0.04, iters=4, factor=0.5, disp=0.045, dscale=0.5, dec=0.11)
            log("organisch", part, len(PARTS[(part, mat)].faces))
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"DR_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_}, open(os.path.join(out, "kasteel_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(os.path.abspath(m))
