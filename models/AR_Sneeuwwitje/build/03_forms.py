"""03_forms Sneeuwwitje (kasteel): vormen over de blokkering. Meters, Z op, gevel kijkt naar -Y (oost), +X = noord, z=0 = plein.
Maten uit asset-brief.md (OSM 60095998 + ref/front.jpg op 84 px/m display). Hulpfuncties uit AR_Assepoester/build/03_forms.py.
Route (beloopbaar, OSM-entrances): spitsboogingang in de linkertoren -> zaal -> gang achter de weergang -> ronde toren -> uitgang (NO-kant).
Botsing: COLL_-blokken (exports/huis_extra.json), muren zelf botsen niet. Interieur (spiegelzaal) komt later (Daan)."""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "..", "..", "AR_Assepoester", "build", "03_forms.py")).read().split("# ---- ramen ----")[0]
_src = _src.replace('PHASE = "03_forms"', 'PHASE = "03_forms"')
exec(_src)
RNG = random.Random(1937)
MATS = {
    "baksteen": ((0.72, 0.60, 0.50, 1), 0.9), "steen": ((0.84, 0.80, 0.70, 1), 0.85), "pannen": ((0.42, 0.22, 0.15, 1), 0.85),
    "zink": ((0.36, 0.40, 0.42, 1), 0.45), "goud": ((0.80, 0.62, 0.22, 1), 0.3), "hout": ((0.36, 0.20, 0.12, 1), 0.7),
    "donker": ((0.025, 0.025, 0.025, 1), 1.0), "glas": ((0.09, 0.11, 0.11, 1), 0.2), "lood": ((0.20, 0.21, 0.22, 1), 0.5),
    "vloer": ((0.40, 0.36, 0.32, 1), 0.9), "schild": ((0.10, 0.12, 0.12, 1), 0.5), "rood": ((0.62, 0.10, 0.08, 1), 0.6),
    "ijzer": ((0.05, 0.06, 0.06, 1), 0.45),
}
COLL = []; LAMPS = []
def coll(x0, x1, y0, y1, z0, z1, a=0.0, cx=None, cy=None):
    if cx is None: COLL.append([round(v, 3) for v in ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0, 0.0)])
    else: COLL.append([round(v, 3) for v in (cx, cy, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0, a)])

TC = (5.45, 2.2); TR_ = 2.05            # ronde toren midden + straal (OSM)


def pointed_pts(x, z0, w, h, n=8):
    """gelijkzijdige spitsboog (open omtrek: linksonder -> top -> rechtsonder)"""
    zs = z0 + h - 0.866 * w
    L = [(x + w / 2 + w * math.cos(math.radians(a)), zs + w * math.sin(math.radians(a))) for a in [180 - 60 * i / n for i in range(n + 1)]]
    R = [(x - w / 2 + w * math.cos(math.radians(a)), zs + w * math.sin(math.radians(a))) for a in [60 - 60 * i / n for i in range(n + 1)]]
    return [(x - w / 2, z0)] + L + R[1:] + [(x + w / 2, z0)]


def cone_roof(part, cx, cy, r0, z0, z1, segs=32, course=0.17, lip=0.03, mat="pannen", bell=0.0):
    """kegeldak met pannenrijen (zaagtand per rij); bell > 0 laat de voet iets uitlopen (klokvorm, front.jpg ronde toren)"""
    n = max(3, round(math.hypot(r0, z1 - z0) / course))
    bm = bmesh.new(); rings = []
    def rad(t): return r0 * (1 - t) + bell * r0 * (1 - t) * t * 0.0
    def ring(r, z): return [bm.verts.new((cx + r * math.cos(k * math.tau / segs), cy + r * math.sin(k * math.tau / segs), z)) for k in range(segs)]
    rings.append(ring(r0 + lip, z0 - 0.05))
    for i in range(n):
        ta, tb = i / n, (i + 1) / n
        za = z0 + (z1 - z0) * (ta ** (1 - bell)); zb = z0 + (z1 - z0) * (tb ** (1 - bell))
        rings.append(ring(r0 * (1 - ta) + lip, za)); rings.append(ring(max(r0 * (1 - tb), 0.0005), zb))
    for a, b in zip(rings, rings[1:]):
        for k in range(segs): bm.faces.new((a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]))
    bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put(part, mat, bm)


def ring_band(part, mat, cx, cy, r, z0, z1, out=0.06, segs=48):
    put(part, mat, blathe([(r + out, z0), (r + out, z1), (r, z1)], segs), TR(cx, cy, 0))


def turret(cx, cy, r, z0, zc, zt, zf):
    """uitgekraagd hoektorentje: kraagsteen-kegel, romp, schietgaten, kegeldak, makelaar (front.jpg)"""
    put("torentjes", "baksteen", blathe([(0, z0 - 0.55), (r * 0.35, z0 - 0.55), (r, z0), (r, zc), (0, zc)], 16), TR(cx, cy, 0))
    for k in range(3):   # kraagringen
        zz = z0 - 0.45 + k * 0.15
        ring_band("torentjes", "steen", cx, cy, r * (0.5 + 0.17 * k), zz, zz + 0.06, 0.03, 16)
    ring_band("torentjes", "steen", cx, cy, r, zc - 0.12, zc, 0.05, 16)
    for a in (-90, 0, 180):
        put("torentjes", "donker", bz(-0.04, 0.04, -0.03, 0.02, zc - 0.85, zc - 0.5), TR(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), 0, a + 90))
    cone_roof("torentjes", cx, cy, r + 0.07, zc, zt, 16, 0.14)
    finial("makelaars", cx, cy, zt - 0.03, 0.55)
    put("makelaars", "zink", btube([(cx, cy, zt + 0.3), (cx, cy, zf)], 0.012, 5))


def merlons(x0, x1, y, z0, n, w=0.62, h=0.41, depth=0.4):
    step = (x1 - x0) / n
    for i in range(n):
        xa = x0 + i * step + (step - w) / 2
        put("kantelen", "baksteen", bz(xa, xa + w, y, y + depth, z0, z0 + h - 0.06))
        put("kantelen", "steen", bz(xa - 0.03, xa + w + 0.03, y - 0.03, y + depth + 0.03, z0 + h - 0.06, z0 + h, 0.01))


def shield(M, x, z, s=1.0, plume=True):
    """wapenschild met ridderhelm en pluim (Sneeuwwitjeschildboven / -schildjes)"""
    sh = [(x - 0.32 * s, z + 0.35 * s), (x + 0.32 * s, z + 0.35 * s), (x + 0.30 * s, z - 0.05 * s), (x + 0.18 * s, z - 0.28 * s), (x, z - 0.4 * s),
          (x - 0.18 * s, z - 0.28 * s), (x - 0.30 * s, z - 0.05 * s)]
    put("schilden", "schild", boutline(sh, -0.07, 0.06), M)
    put("schilden", "goud", band(sh + [sh[0]], 0.035 * s, -0.08, 0.02), M)
    put("schilden", "rood", boutline([(x - 0.12 * s, z + 0.12 * s), (x + 0.12 * s, z + 0.12 * s), (x + 0.1 * s, z - 0.12 * s), (x, z - 0.2 * s), (x - 0.1 * s, z - 0.12 * s)], -0.09, 0.02), M)
    if plume:
        put("schilden", "zink", blathe([(0, 0), (0.13 * s, 0.02 * s), (0.16 * s, 0.14 * s), (0.12 * s, 0.26 * s), (0, 0.3 * s)], 12), M @ TR(x, -0.08, z + 0.35 * s))
        for k in range(5):
            a = math.radians(-50 + k * 25)
            put("schilden", "rood" if k % 2 else "goud", btube([(x, -0.08, z + 0.6 * s), (x + 0.22 * s * math.sin(a), -0.08, z + 0.82 * s), (x + 0.38 * s * math.sin(a), -0.08, z + 0.72 * s)], 0.035 * s, 5), M)


def build(master):
    open_master(master); clear_owned()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    F = Matrix.Identity(4)
    cutters = []; wall = bmesh.new()
    def addwall(bm):
        me = bpy.data.meshes.new("_w"); bm.to_mesh(me); bm.free(); wall.from_mesh(me); bpy.data.meshes.remove(me)
    # ---------------- muren ----------------
    addwall(bz(-7.19, -2.46, 0.51, 5.77, 0, 3.82))                 # linkertoren voet (175..600 px)
    addwall(bz(-6.54, -2.79, 0.51, 5.77, 3.80, 6.75))              # romp boven de kraag
    addwall(bz(-5.76, -3.44, 0.51, 1.10, 6.73, 7.76))              # trapgevel trede 1
    addwall(bz(-5.25, -4.24, 0.51, 1.10, 7.74, 8.77))              # trede 2
    addwall(bz(-2.48, 4.70, 1.31, 4.14, 0, 4.19))                  # weergang, doorgetrokken tot in de ronde toren (achteraan zat een gat, Daan)
    bm = bmesh.new()                                                # topgevel onder het dak tot tegen de toren (dak loopt op van 4.17 naar de nok)
    pr = [(1.31, 4.1), (4.14, 4.1), (4.14, 5.12), (1.75, 4.17), (1.31, 4.17)]
    v0 = [bm.verts.new((3.40, y, z)) for y, z in pr]; v1 = [bm.verts.new((4.70, y, z)) for y, z in pr]
    bm.faces.new(v0); bm.faces.new(v1[::-1])
    for i in range(len(pr)): bm.faces.new((v0[i], v0[(i + 1) % len(pr)], v1[(i + 1) % len(pr)], v1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); addwall(bm)
    addwall(bz(-1.06, 3.25, 4.12, 9.28, 0, 4.42))                  # hal (achterbouw, inferred hoogte)
    addwall(bz(-7.19, -1.04, 5.75, 9.28, 0, 4.42))                 # achterbouw links (inferred)
    bm = blathe([(0, 0), (TR_, 0), (TR_, 5.37), (0, 5.37)], 48); bmesh.ops.translate(bm, vec=(TC[0], TC[1], 0), verts=bm.verts); addwall(bm)
    # ---------------- natuursteen: plint, banden, hoekblokken, afdekkingen ----------------
    # plint alleen aan de buitenkant (de zijkanten van de muurblokken liggen binnen: richel dwars door de gang, Daan)
    for (a0, a1, yy) in ((-7.24, -4.79 - 0.84, 0.51), (-4.79 + 0.84, -2.41, 0.51), (-2.46, 3.6, 1.31)):
        put("steen", "steen", bz(a0, a1, yy - 0.05, yy + 0.01, 0, 0.62)); put("steen", "steen", bz(a0, a1, yy - 0.03, yy + 0.01, 0.62, 0.7))
    put("steen", "steen", bz(-7.24, -7.13, 0.51, 5.77, 0, 0.7))                                  # zijgevel linkertoren (buiten)
    xa0 = math.degrees(math.atan2(0.5 - TC[1], 6.56 - TC[0]))          # plintring onderbroken bij de uitgang en de doorgang naar de gang (richel, Daan)
    for k in range(48):
        a = k * 360 / 48 + 3.75
        if abs((a - xa0 + 180) % 360 - 180) < 24 or abs((a - 180 + 180) % 360 - 180) < 42: continue
        put("steen", "steen", bz(-0.15, 0.15, -0.05, 0.01, 0, 0.7), TR(TC[0] + TR_ * math.cos(math.radians(a)), TC[1] + TR_ * math.sin(math.radians(a)), 0, a + 90))
    put("steen", "steen", bz(-2.46, 3.5, 1.24, 1.34, 3.58, 3.70))                                   # lichte band weergang (front.jpg 555 px)
    for (a0, a1, z0, z1) in ((-6.54, -2.79, 6.67, 6.79), (-5.76, -3.44, 7.70, 7.82), (-5.25, -4.24, 8.71, 8.83)):   # afdekking treden
        put("steen", "steen", bz(a0 - 0.05, a1 + 0.05, 0.44, 1.16, z0, z1, 0.01))
    for xq, sx in ((-7.19, 1), (-2.46, -1)):                                                          # hoekblokken voet linkertoren
        z = 0.7; i = 0
        while z < 3.3:
            lw = 0.42 if i % 2 == 0 else 0.26
            put("steen", "steen", bz(min(xq, xq + sx * lw), max(xq, xq + sx * lw), 0.47, 0.53, z, z + 0.26, 0.01)); z += 0.3; i += 1
    # ronde toren: boogfries + kroonlijst (front.jpg 410..455 px)
    ring_band("steen", "steen", TC[0], TC[1], TR_, 4.80, 4.92, 0.10)
    ring_band("steen", "steen", TC[0], TC[1], TR_, 5.22, 5.37, 0.14)
    for k in range(24):     # kleine rondboogjes van het fries
        a = k * math.tau / 24
        put("steen", "steen", bz(-0.06, 0.06, -0.08, 0.0, 4.6, 4.8), TR(TC[0] + (TR_ + 0.02) * math.cos(a), TC[1] + (TR_ + 0.02) * math.sin(a), 0, math.degrees(a) + 90))
        arcpts = arc(0, 4.98, 0.17, 180, 0, 5)
        put("steen", "steen", band(arcpts, 0.04, -0.06, 0.06), TR(TC[0] + (TR_ + 0.02) * math.cos(a + math.tau / 48), TC[1] + (TR_ + 0.02) * math.sin(a + math.tau / 48), 0, math.degrees(a + math.tau / 48) + 90))
    # ---------------- daken ----------------
    tiled_roof("dak_toren", (-6.54, -2.79, 1.10, 5.77), (-4.665, -4.665, 1.10, 5.77), 6.75, 8.45, hips=True)
    tiled_roof("dak_weergang", (-2.46, 3.5, 1.75, 9.3), (-1.4, 2.4, 5.5, 5.5), 4.17, 5.70)
    tiled_roof("dak_achter", (-7.19, -1.06, 5.77, 9.28), (-6.0, -2.2, 7.5, 7.5), 4.42, 5.8)
    cone_roof("dak_rond", TC[0], TC[1], TR_ + 0.24, 5.37, 8.65, 40, 0.18)
    finial("makelaars", TC[0], TC[1], 8.6, 0.8); put("makelaars", "zink", btube([(TC[0], TC[1], 9.1), (TC[0], TC[1], 9.5)], 0.015, 5))
    for xd in (-0.52, 0.97, 2.39):          # dakkapellen (front.jpg 735/860/980 px)
        yd = 2.05; zd = 4.45
        put("dakkapellen", "pannen", bz(xd - 0.3, xd + 0.3, yd, yd + 0.9, zd, zd + 0.85))
        put("dakkapellen", "donker", bz(xd - 0.15, xd + 0.15, yd - 0.02, yd + 0.01, zd + 0.25, zd + 0.7))
        tiled_roof("dakkapellen", (xd - 0.38, xd + 0.38, yd - 0.08, yd + 0.9), (xd, xd, yd - 0.08, yd + 0.9), zd + 0.85, zd + 1.4, course=0.14, lip=0.02, under=0.04, cap_top=False)
        finial("makelaars", xd, yd - 0.06, zd + 1.37, 0.45)
    # daktorentje (front.jpg 830..950 px)
    put("daktoren", "baksteen", blathe([(0, 4.4), (0.7, 4.4), (0.7, 6.3), (0, 6.3)], 20), TR(1.32, 3.6, 0))
    ring_band("daktoren", "steen", 1.32, 3.6, 0.7, 6.18, 6.3, 0.05, 20)
    put("daktoren", "donker", bz(-0.12, 0.12, -0.02, 0.02, 5.4, 5.95), TR(1.32, 3.6 - 0.69, 0))
    cone_roof("daktoren", 1.32, 3.6, 0.8, 6.3, 7.85, 20, 0.15)
    finial("makelaars", 1.32, 3.6, 7.82, 0.55)
    # ---------------- torentjes, kantelen, kroon ----------------
    turret(-7.25, 0.6, 0.57, 3.8, 5.65, 7.25, 7.9)
    turret(-2.13, 0.6, 0.57, 3.8, 5.65, 7.25, 7.9)
    merlons(-2.46, 3.5, 1.31, 4.17, 7)
    put("kroon", "goud", blathe([(0, 0), (0.12, 0), (0.08, 0.15), (0.2, 0.35), (0.22, 0.55), (0.12, 0.62), (0.05, 0.75), (0, 0.8)], 10), TR(-4.75, 0.8, 8.83))
    put("kroon", "goud", btube([(-4.75 + 0.25 * math.cos(t), 0.8, 9.85 + 0.25 * math.sin(t)) for t in [i * math.tau / 16 for i in range(17)]], 0.03, 5))
    put("kroon", "ijzer", btube([(-4.75, 0.48, 6.0), (-4.75, 0.48, 6.45)], 0.03, 4)); put("kroon", "ijzer", btube([(-4.95, 0.48, 6.22), (-4.55, 0.48, 6.22)], 0.03, 4))   # muuranker (front.jpg)
    # ---------------- openingen ----------------
    ex = -4.79; EW, EH = 1.67, 2.68                                  # ingang (spitsboog) - al 1.67 breed: speelbaar
    ep = pointed_pts(ex, 0, EW, EH, 10)
    cutters.append((boutline(ep, 0.2, 0.75), F))
    put("ingang", "steen", band(ep, 0.18, 0.43, 0.1), F)
    put("ingang", "vloer", bz(ex - EW / 2, ex + EW / 2, 0.2, 0.95, 0, 0.04))
    shield(TR(0, 0.51, 0), -4.69, 3.82, 1.0, plume=False)            # schild boven de ingang (front.jpg 345..420 px), plat zonder helm
    gp = pointed_pts(-4.69, 4.4, 0.6, 1.3, 6)                         # gevelraam
    cutters.append((boutline(gp, 0.3, 0.3), F)); put("ramen", "steen", band(gp, 0.1, 0.43, 0.09), F)
    put("ramen", "hout", boutline(gp, 0.56, 0.05), F)
    for xa in (-0.4, 2.27):                                          # blinde spitsbogen met bankje
        bp = pointed_pts(xa, 0, 1.7, 2.9, 10)
        cutters.append((boutline(bp, 1.0, 0.43), F))
        put("bogen", "steen", band(bp, 0.17, 1.23, 0.1), F)
        put("bogen", "hout", bz(xa - 0.62, xa + 0.62, 0.9, 1.26, 0.42, 0.48)); put("bogen", "steen", bz(xa - 0.55, xa - 0.35, 0.95, 1.22, 0, 0.42)); put("bogen", "steen", bz(xa + 0.35, xa + 0.55, 0.95, 1.22, 0, 0.42))   # bankje buiten voor de boog
    # ronde toren: raampje voor (front.jpg 1190..1225 px) en uitgangsdeur aan de NO-kant (OSM exit (6.56,0.5))
    def on_tower(ang_deg, d=0.3):
        a = math.radians(ang_deg); n = Vector((math.cos(a), math.sin(a), 0))
        return TR(TC[0] + n.x * (TR_ + d), TC[1] + n.y * (TR_ + d), 0, ang_deg + 90)
    wp = pointed_pts(0, 1.2, 0.42, 1.2, 6)
    cutters.append((boutline(wp, 0.0, 0.5), on_tower(-110))); put("ramen", "steen", band(wp, 0.08, 0.27, 0.07), on_tower(-110)); put("ramen", "hout", boutline(wp, 0.48, 0.04), on_tower(-110))
    xa_ = math.degrees(math.atan2(0.5 - TC[1], 6.56 - TC[0]))         # richting van de OSM-uitgang
    up = pointed_pts(0, 0, 1.35, 2.5, 10)
    cutters.append((boutline(up, -0.1, 0.9), on_tower(xa_)))
    put("uitgang", "steen", band(up, 0.15, 0.22, 0.12), on_tower(xa_))
    put("uitgang", "vloer", bz(-0.68, 0.68, 0.0, 0.75, 0, 0.04), on_tower(xa_))
    shield(on_tower(-150, 0.0), 0, 3.4, 0.8, plume=False)
    # binnen: route (overlappende snijvolumes, niet vlak tegen elkaar)
    cutters.append((bz(-6.89, -2.76, 0.81, 5.47, 0.0, 3.4), F))                       # zaal in de linkertoren
    cutters.append((bz(-2.95, 3.9, 1.61, 3.84, -0.03, 3.3), F))                        # gang achter de weergang
    bm = blathe([(0, -0.05), (TR_ - 0.32, -0.05), (TR_ - 0.32, 4.4), (0, 4.4)], 32); bmesh.ops.translate(bm, vec=(TC[0], TC[1], 0), verts=bm.verts)
    cutters.append((bm, F))                                                           # ronde toren binnen
    put("binnen", "vloer", bz(-6.89, -2.76, 0.81, 5.47, 0, 0.04)); put("binnen", "vloer", bz(-2.8, 3.8, 1.61, 3.84, 0, 0.041))
    put("binnen", "vloer", blathe([(0, 0), (TR_ - 0.32, 0), (TR_ - 0.32, 0.042), (0, 0.042)], 32), TR(TC[0], TC[1], 0))
    for p_ in ((-4.8, 3.2, 2.6), (0.5, 2.7, 2.5), (TC[0], TC[1], 3.2)): LAMPS.append(p_)
    # ---------------- muren snijden ----------------
    me = bpy.data.meshes.new("SW_muren__baksteen"); wall.to_mesh(me); wall.free()
    wob = bpy.data.objects.new("SW_muren__baksteen", me); col("FORMS").objects.link(wob); own(wob); assign(wob, bpy.data.materials["MAT_baksteen"])
    cut = bmesh.new()
    for bm, Mx in cutters:
        bmesh.ops.transform(bm, matrix=Mx, verts=bm.verts); m2 = bpy.data.meshes.new("_c"); bm.to_mesh(m2); bm.free(); cut.from_mesh(m2); bpy.data.meshes.remove(m2)
    cme = bpy.data.meshes.new("_cutter"); cut.to_mesh(cme); cut.free()
    cob = bpy.data.objects.new("_cutter", cme); col("FORMS").objects.link(cob)
    b = wob.modifiers.new("cut", "BOOLEAN"); b.object = cob; b.operation = "DIFFERENCE"; b.solver = "EXACT"; b.use_self = True; b.use_hole_tolerant = True
    apply_all_modifiers(wob); bpy.data.objects.remove(cob, do_unlink=True); bpy.data.meshes.remove(cme)
    # ---------------- botsblokken ----------------
    coll(-7.19, ex - EW / 2, 0.51, 0.81, 0, 4); coll(ex + EW / 2, -2.46, 0.51, 0.81, 0, 4)      # gevel naast de ingang
    coll(-7.19, -6.89, 0.51, 5.77, 0, 4); coll(-7.19, -1.04, 5.47, 9.28, 0, 4.4)               # zijwand + achterbouw
    coll(-2.76, -2.46, 0.81, 1.61, 0, 4); coll(-2.76, -1.06, 3.84, 5.47, 0, 4)                  # tussen zaal en gang
    coll(-2.46, 3.5, 1.31, 1.61, 0, 4.2); coll(-1.06, 3.25, 3.84, 9.28, 0, 4.4)                 # weergang voor + hal
    for k in range(20):    # ronde toren: ring van blokken, open bij de uitgang en de gang
        a = k * 360 / 20
        d = (a - xa_ + 180) % 360 - 180; g = (a - 180 + 180) % 360 - 180
        if abs(d) < 20 or abs(g) < 25: continue
        c = Vector((TC[0], TC[1], 0)) + Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0)) * (TR_ - 0.15)
        coll(-0.36, 0.36, -0.18, 0.18, 0, 5, a=a + 90, cx=c.x, cy=c.y)
    # ---------------- wegschrijven ----------------
    for (part, mat), bm in PARTS.items():
        ob = new_mesh_object(f"SW_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(os.path.dirname(HERE), "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": [[round(v, 2) for v in l] for l in LAMPS]}, open(os.path.join(out, "kasteel_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "colliders", len(COLL))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
