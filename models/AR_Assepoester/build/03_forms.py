"""03_forms Assepoester: echte vormen over de goedgekeurde blokkering (02_blockout).
Meters, Z op, gevel kijkt naar -Y (west), +X = zuid, z=0 = maaiveld. Maten: asset-brief.md (BAG + ref/front.jpg op 98 px/m).
Elk onderdeel wordt in een bmesh verzameld en als object AP_<deel>__<materiaal> in collectie FORMS gezet."""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix
PHASE = "03_forms"; OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix, "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns); globals().update({k: v for k, v in _ns.items() if callable(v)})
RNG = random.Random(9)

# ---- maten (zie 02_blockout.py en asset-brief.md) ----------------------------------------------
WING = (-6.34, -2.33, 0.90, 4.72)          # entreevleugel (achterkant tegen het hoofdhuis)
GAL_Y = 1.62
MAIN = (-3.80, 5.19, 4.72, 11.67)
BACK = (-3.30, 4.69, 11.67, 14.21)
TOWER = (2.42, 5.19, 4.42, 7.19)           # 0.30 voor het hoofdhuis (inferred)
PORCH = (3.25, 5.95, 0.0, 4.42)
WING_EAVE, WING_CORN, WING_TOP = 2.65, 3.03, 4.16
GAL_HIGH, GAL_LOW, PLINTH = 3.03, 2.10, 0.77
MAIN_EAVE, MAIN_CORN, MANS_BREAK, MANS_TOP = 5.30, 5.60, 6.42, 6.52
TOWER_CORN, TOWER_TOP, TOWER_FIN = 5.10, 7.65, 8.00
PORCH_EAVE, PORCH_TOP = 2.60, 2.86
BACK_H = 5.0

MATS = {
    "stuc": ((0.78, 0.77, 0.72, 1), 0.92), "omlijsting": ((0.85, 0.84, 0.79, 1), 0.85), "plint": ((0.56, 0.56, 0.53, 1), 0.9),
    "groen": ((0.17, 0.33, 0.33, 1), 0.7), "pannen": ((0.40, 0.22, 0.16, 1), 0.85), "baksteen": ((0.55, 0.26, 0.18, 1), 0.9),
    "hout": ((0.40, 0.20, 0.12, 1), 0.7), "glas": ((0.09, 0.11, 0.11, 1), 0.2), "lood": ((0.20, 0.21, 0.22, 1), 0.5),
    "zink": ((0.36, 0.43, 0.46, 1), 0.45), "kozijn": ((0.86, 0.83, 0.74, 1), 0.6), "donker": ((0.025, 0.025, 0.025, 1), 1.0),
    "achter": ((0.55, 0.55, 0.52, 1), 0.95),
}
PARTS = {}


def put(part, mat, bm, M=None):
    if M is not None: bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    key = (part, mat)
    if key not in PARTS: PARTS[key] = bmesh.new()
    me = bpy.data.meshes.new("_t"); bm.to_mesh(me); bm.free()
    PARTS[key].from_mesh(me); bpy.data.meshes.remove(me)


def TR(x=0, y=0, z=0, rz=0): return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z")


# ---- primitieven --------------------------------------------------------------------------------
def bbox(sx, sy, sz, cx=0, cy=0, cz=0, ch=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    if ch > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(ch, sx / 3, sy / 3, sz / 3), segments=1, affect="EDGES", profile=0.5)
    bmesh.ops.translate(bm, vec=(cx, cy, cz), verts=bm.verts); return bm


def bz(x0, x1, y0, y1, z0, z1, ch=0.0):
    return bbox(x1 - x0, y1 - y0, z1 - z0, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, ch)


def blathe(profile, segs=12):
    bm = bmesh.new(); vs = [bm.verts.new((max(r, 0.0), 0, z)) for r, z in profile]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=math.tau, steps=segs, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def boutline(pts_xz, y0, depth):
    """gesloten omtrek in het XZ-vlak op y0, geextrudeerd naar +Y over depth"""
    bm = bmesh.new(); vs = [bm.verts.new((x, y0, z)) for x, z in pts_xz]; f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f]); top = [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, depth, 0), verts=top); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def bsweep(profile, x0, x1, y0, y1, z0, back=True):
    """profiel [(uitsteek, z)] rond rechthoek x0..x1, y0..y1 (voor = y0). back=False: alleen voor + zijkanten."""
    bm = bmesh.new(); rings = []
    for o, z in profile:
        pts = [(x0 - o, y0 - o), (x1 + o, y0 - o), (x1 + o, y1 + o), (x0 - o, y1 + o)] if back else \
              [(x0 - o, y1), (x0 - o, y0 - o), (x1 + o, y0 - o), (x1 + o, y1)]
        rings.append([bm.verts.new((px, py, z0 + z)) for px, py in pts])
    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for i in range(n if back else n - 1):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def btube(points, r, segs=6):
    bm = bmesh.new(); P = [Vector(p) for p in points]; rings = []
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        a = t.cross(Vector((0, 0, 1)))
        if a.length < 1e-4: a = t.cross(Vector((1, 0, 0)))
        a.normalize(); b = t.cross(a)
        rings.append([bm.verts.new(p + (a * math.cos(k * math.tau / segs) + b * math.sin(k * math.tau / segs)) * r) for k in range(segs)])
    for A, B in zip(rings, rings[1:]):
        for k in range(segs): bm.faces.new((A[k], A[(k + 1) % segs], B[(k + 1) % segs], B[k]))
    bm.faces.new(rings[0]); bm.faces.new(list(reversed(rings[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def arc(cx, cz, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def arch_pts(x, z0, w, h, n=12):
    """rondboog-omtrek (open: linksonder -> over de boog -> rechtsonder)"""
    r = w / 2; zs = z0 + h - r
    return [(x - r, z0)] + arc(x, zs, r, 180, 0, n) + [(x + r, z0)]


def band(pts, s, y0, depth, rnd=None):
    """lijst langs een open omtrek, breedte s naar buiten (normaal in XZ), van y0 tot y0+depth"""
    bm = bmesh.new(); n = len(pts); inner = []; outer = []
    for i, (x, z) in enumerate(pts):
        a = Vector(pts[max(i - 1, 0)]); b = Vector(pts[min(i + 1, n - 1)])
        t = (b - a).normalized(); nrm = Vector((-t.y, t.x))      # links van de looprichting = buiten (looprichting met de klok mee)
        o = Vector((x, z)) + nrm * s
        inner.append((x, z)); outer.append((o.x, o.y))
    F = [[bm.verts.new((x, y0, z)) for x, z in L] for L in (inner, outer)]
    B = [[bm.verts.new((x, y0 + depth, z)) for x, z in L] for L in (inner, outer)]
    for i in range(n - 1):
        bm.faces.new((F[0][i], F[0][i + 1], F[1][i + 1], F[1][i]))
        bm.faces.new((B[0][i], B[1][i], B[1][i + 1], B[0][i + 1]))
        for k in (0, 1):
            bm.faces.new((F[k][i], B[k][i], B[k][i + 1], F[k][i + 1]))
    for i in (0, n - 1):
        bm.faces.new((F[0][i], F[1][i], B[1][i], B[0][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


# ---- daken: pannenrijen als zaagtand (een functie voor schild, lessenaar, mansarde, spits, dakkapel) ----
def tiled_roof(part, eave, top, z0, z1, course=0.20, lip=0.035, under=0.06, cap_top=True, hips=True, mat="pannen"):
    """eave = (x0,x1,y0,y1) op z0, top = (x0,x1,y0,y1) op z1 (mag ontaard zijn: nok of punt).
    Elke pannenrij is een schuin vlak met onderaan een lip naar buiten (lip) -> schaduwlijn per rij."""
    def rect(t, grow=0.0):
        r = [eave[i] + (top[i] - eave[i]) * t for i in range(4)]
        return (r[0] - grow, r[1] + grow, r[2] - grow, r[3] + grow)
    run = max(min(top[0] - eave[0], eave[1] - top[1], top[2] - eave[2], eave[3] - top[3]), 0.05)
    slope = math.hypot(run, z1 - z0)
    n = max(2, round(slope / course))
    bm = bmesh.new(); rings = []
    def ring(r, z): return [bm.verts.new(p) for p in ((r[0], r[2], z), (r[1], r[2], z), (r[1], r[3], z), (r[0], r[3], z))]
    rings.append(ring(rect(0, lip), z0 - under))           # dikte van de dakrand
    for i in range(n):
        ta, tb = i / n, (i + 1) / n
        if i > 0: rings.append(ring(rect(ta, lip), z0 + (z1 - z0) * ta))
        if i == 0: rings.append(ring(rect(0, lip), z0))
        rings.append(ring(rect(tb), z0 + (z1 - z0) * tb))
    for a, b in zip(rings, rings[1:]):
        for k in range(4):
            bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
    bm.faces.new(list(reversed(rings[0])))
    if cap_top: bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    put(part, mat, bm)
    if hips:   # hoekkepers (vorstpannen) van de dakvoet naar de top
        e, t = eave, top
        for (ex, ey), (tx, ty) in (((e[0], e[2]), (t[0], t[2])), ((e[1], e[2]), (t[1], t[2])), ((e[1], e[3]), (t[1], t[3])), ((e[0], e[3]), (t[0], t[3]))):
            if math.hypot(tx - ex, ty - ey) < 0.05: continue
            put(part, mat, btube([(ex, ey, z0 + 0.03), (tx, ty, z1 + 0.03)], 0.055, 6))
        if (t[1] - t[0]) > 0.05 and (t[3] - t[2]) < 0.05:
            put(part, mat, btube([(t[0], t[2], z1 + 0.03), (t[1], t[2], z1 + 0.03)], 0.065, 6))
        if (t[3] - t[2]) > 0.05 and (t[1] - t[0]) < 0.05:
            put(part, mat, btube([(t[0], t[2], z1 + 0.03), (t[0], t[3], z1 + 0.03)], 0.065, 6))


FINIAL = [(0, 0), (0.06, 0), (0.06, 0.05), (0.03, 0.08), (0.025, 0.2), (0.07, 0.26), (0.075, 0.31), (0.05, 0.36), (0.02, 0.4), (0.012, 0.65), (0, 0.7)]


def finial(part, x, y, z, s=1.0):
    put(part, "zink", blathe([(r * s, h * s) for r, h in FINIAL], 10), TR(x, y, z))


def dormer(part, x, yf, z0, w, h_wall, h_roof, depth=0.9, win=(0.30, 0.45)):
    """dakkapel: blauwgroene planken voorkant + wangen, klein raam, puntdak met makelaar (front.jpg)"""
    put(part, "groen", bz(x - w / 2, x + w / 2, yf, yf + depth, z0, z0 + h_wall))
    for k in range(-2, 3):   # planknaden
        put(part, "groen", bz(x + k * w / 5 - 0.008, x + k * w / 5 + 0.008, yf - 0.012, yf, z0, z0 + h_wall))
    ww, wh = win; zc = z0 + h_wall * 0.25
    put(part, "glas", bz(x - ww / 2, x + ww / 2, yf - 0.02, yf + 0.01, zc, zc + wh))
    put(part, "kozijn", bz(x - 0.012, x + 0.012, yf - 0.035, yf - 0.015, zc, zc + wh))
    put(part, "kozijn", bz(x - ww / 2, x + ww / 2, yf - 0.035, yf - 0.015, zc + wh * 0.5 - 0.012, zc + wh * 0.5 + 0.012))
    for b in (bz(x - ww / 2 - 0.05, x - ww / 2, yf - 0.05, yf, zc - 0.03, zc + wh + 0.03), bz(x + ww / 2, x + ww / 2 + 0.05, yf - 0.05, yf, zc - 0.03, zc + wh + 0.03),
              bz(x - ww / 2 - 0.05, x + ww / 2 + 0.05, yf - 0.06, yf, zc - 0.06, zc), bz(x - ww / 2 - 0.05, x + ww / 2 + 0.05, yf - 0.05, yf, zc + wh, zc + wh + 0.05)):
        put(part, "groen", b)
    o = 0.07; zt = z0 + h_wall
    tiled_roof(part, (x - w / 2 - o, x + w / 2 + o, yf - o, yf + depth), (x, x, yf - o, yf + depth), zt, zt + h_roof, course=0.14, lip=0.02, under=0.04, cap_top=False, mat="groen")
    finial(part, x, yf - o + 0.02, zt + h_roof - 0.02, 0.55)


# ---- ramen ---------------------------------------------------------------------------------------
def window_arched(M, x, z0, w, h, cutters, kind, s=0.10, depth=0.14):
    """rondboograam in een wandvlak (lokaal y=0, buiten = -Y). kind: 'luiken' (dicht, glas-in-lood in de boog),
    'open' (kozijn met roeden + opengeslagen luiken), 'lancet' (smal, glas-in-lood)"""
    pts = arch_pts(x, z0, w, h, 12)
    cutters.append((boutline(pts, -0.25, 0.25 + depth), M))
    r = w / 2; zs = z0 + h - r
    put("ramen", "omlijsting", band(pts, s, -0.045, 0.06), M)                                   # omlijsting
    put("ramen", "omlijsting", bz(x - w / 2 - s - 0.04, x + w / 2 + s + 0.04, -0.08, 0.02, z0 - 0.07, z0, 0.012), M)   # dorpel
    put("ramen", "omlijsting", bz(x - 0.06, x + 0.06, -0.07, 0.0, z0 + h - 0.03, z0 + h + s + 0.03, 0.01), M)        # sluitsteen
    if kind == "lancet":
        put("ramen", "glas", boutline(pts, depth - 0.03, 0.02), M)
        for k in range(1, 4):   # loodstrips
            zz = z0 + (zs - z0) * k / 4
            put("ramen", "lood", bz(x - r, x + r, depth - 0.045, depth - 0.03, zz - 0.008, zz + 0.008), M)
        put("ramen", "lood", bz(x - 0.008, x + 0.008, depth - 0.045, depth - 0.03, z0, z0 + h - 0.02), M)
        return
    # glas-in-lood in de boog
    put("ramen", "glas", boutline([(x - r, zs)] + arc(x, zs, r, 180, 0, 12)[1:-1] + [(x + r, zs)], depth - 0.04, 0.02), M)
    for a in (45, 90, 135):
        c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
        put("ramen", "kozijn", btube([(x, depth - 0.05, zs), (x + c * r * 0.97, depth - 0.05, zs + sn * r * 0.97)], 0.012, 4), M)
    put("ramen", "kozijn", bz(x - r, x + r, depth - 0.07, depth - 0.03, zs - 0.03, zs + 0.01), M)       # kalf
    if kind == "luiken":
        for sx in (-1, 1):
            xa, xb = sorted((x + sx * 0.006, x + sx * (r - 0.01)))
            put("ramen", "groen", bz(xa, xb, depth - 0.09, depth - 0.05, z0 + 0.01, zs - 0.03), M)
            for zz in (z0 + 0.15, zs - 0.18):   # klampen
                put("ramen", "groen", bz(xa + 0.02, xb - 0.02, depth - 0.105, depth - 0.09, zz - 0.03, zz + 0.03), M)
            for k in range(1, 3):    # plankvoegen
                xx = xa + (xb - xa) * k / 3
                put("ramen", "lood", bz(xx - 0.004, xx + 0.004, depth - 0.095, depth - 0.088, z0 + 0.01, zs - 0.03), M)
    else:   # open: glas + kozijn met roeden, luiken opengeslagen tegen de gevel
        put("ramen", "glas", bz(x - r, x + r, depth - 0.04, depth - 0.02, z0, zs), M)
        for b in (bz(x - r, x - r + 0.06, depth - 0.08, depth - 0.03, z0, zs), bz(x + r - 0.06, x + r, depth - 0.08, depth - 0.03, z0, zs),
                  bz(x - r, x + r, depth - 0.08, depth - 0.03, z0, z0 + 0.06), bz(x - 0.025, x + 0.025, depth - 0.08, depth - 0.03, z0, zs)):
            put("ramen", "kozijn", b, M)
        for k in (1, 2):
            zz = z0 + (zs - z0) * k / 3
            put("ramen", "kozijn", bz(x - r, x + r, depth - 0.07, depth - 0.035, zz - 0.012, zz + 0.012), M)
        for sx in (-1, 1):   # luiken naast het raam (front.jpg 712 / 860 px), recht, zo hoog als het raam
            xa, xb = sorted((x + sx * (w / 2 + s + 0.02), x + sx * (w / 2 + s + 0.02 + 0.42)))
            put("ramen", "groen", bz(xa, xb, -0.05, -0.008, z0 + 0.02, z0 + h - 0.05), M)
            for zz in (z0 + 0.2, z0 + h - 0.3):
                put("ramen", "groen", bz(xa + 0.03, xb - 0.03, -0.065, -0.05, zz - 0.03, zz + 0.03), M)


def cartouche(M, x, z):
    """ornamentkuifje boven een raam (front.jpg 460/585/740 px): schildje met krullen"""
    shield = [(x - 0.11, z), (x + 0.11, z), (x + 0.13, z + 0.12), (x + 0.07, z + 0.2), (x, z + 0.23), (x - 0.07, z + 0.2), (x - 0.13, z + 0.12)]
    put("ornament", "omlijsting", boutline(shield, -0.07, 0.07), M)
    for sx in (-1, 1):
        pts = [(x + sx * (0.13 + 0.06 * math.cos(a)), -0.05, z + 0.06 + 0.06 * math.sin(a)) for a in [i * math.tau / 8 for i in range(9)]]
        put("ornament", "omlijsting", btube(pts, 0.018, 5), M)


def build(master):
    open_master(master); clear_owned()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    F = Matrix.Identity(4)
    cutters = []
    wall = bmesh.new()
    def addwall(bm):
        me = bpy.data.meshes.new("_w"); bm.to_mesh(me); bm.free(); wall.from_mesh(me); bpy.data.meshes.remove(me)

    # ---------------- muren ----------------
    x0, x1, y0, y1 = WING
    addwall(bz(x0, x1, y0, y1, 0, WING_EAVE + 0.02))
    addwall(bz(MAIN[0], MAIN[1], MAIN[2], MAIN[3], 0, MAIN_EAVE + 0.02))
    addwall(bz(TOWER[0], TOWER[1], TOWER[2], TOWER[3], 0, TOWER_CORN - 0.23))
    addwall(bz(WING[1], PORCH[0], GAL_Y + 0.13, MAIN[2], 0, GAL_LOW + 0.1))         # gaanderijruimte (achter de planken)
    put("achterbouw", "achter", bz(BACK[0], BACK[1], BACK[2], BACK[3], 0, BACK_H))
    put("achterbouw", "achter", bz(BACK[0] - 0.05, BACK[1] + 0.05, BACK[2] - 0.05, BACK[3] + 0.05, BACK_H, BACK_H + 0.15))
    # portiek: zijwand rechts (stuc) tot de toren
    addwall(bz(PORCH[1] - 0.15, PORCH[1], 0.35, MAIN[2], 0, PORCH_EAVE))

    # ---------------- kroonlijsten (blauwgroen geverfd, front.jpg) ----------------
    CORN = [(0, 0), (0.03, 0.02), (0.03, 0.08), (0.08, 0.12), (0.12, 0.20), (0.15, 0.26), (0.15, 0.30)]
    put("kroonlijst", "groen", bsweep([(o, z * (MAIN_CORN - MAIN_EAVE) / 0.30) for o, z in CORN], MAIN[0], MAIN[1], MAIN[2], MAIN[3], MAIN_EAVE))
    put("kroonlijst", "groen", bsweep([(o * 0.6, z * (WING_CORN - WING_EAVE) / 0.30) for o, z in CORN], x0, x1, y0, y1, WING_EAVE, back=False))
    put("kroonlijst", "groen", bsweep([(o * 0.8, z * 0.25 / 0.30) for o, z in CORN], TOWER[0], TOWER[1], TOWER[2], TOWER[3], TOWER_CORN - 0.25))
    # hoekpilasters/lisenen in stuc op de hoeken van hoofdhuis en toren (front.jpg: lichte strook)
    for (xx, yy, sx) in ((MAIN[0], MAIN[2], 1), (TOWER[0], TOWER[2], 1), (TOWER[1], TOWER[2], -1)):
        put("lisenen", "omlijsting", bz(min(xx, xx + sx * 0.28), max(xx, xx + sx * 0.28), yy - 0.035, yy + 0.05, PLINTH if xx == MAIN[0] else 0.05, (MAIN_EAVE if xx == MAIN[0] else TOWER_CORN - 0.25) - 0.02))

    # ---------------- daken ----------------
    O = 0.12
    tiled_roof("dak_vleugel", (x0 - O, x1 + O, y0 - 0.25, y1), (-4.84, -3.83, (y0 - 0.25 + y1) / 2, (y0 - 0.25 + y1) / 2), WING_CORN, WING_TOP)
    for x in (-4.84, -3.83):
        finial("pinakels", x, (y0 - 0.25 + y1) / 2, WING_TOP + 0.02, 0.7)
    # gaanderij: lessenaarsdak van het hoofdhuis naar de goot voor de planken
    gx0, gx1 = WING[1], PORCH[0]
    tiled_roof("dak_gaanderij", (gx0 - 0.02, gx1 + 0.02, GAL_Y - 0.35, MAIN[2] + 0.05), (gx0 - 0.02, gx1 + 0.02, MAIN[2] + 0.0, MAIN[2] + 0.05),
               GAL_LOW, GAL_HIGH, hips=False)
    # bakstenen rand tegen het hoofdhuis (front.jpg: rode stenen met gaten)
    x = gx0 - 0.15
    while x < gx1 + 0.15:
        L = RNG.uniform(0.17, 0.24)
        if RNG.random() > 0.22:
            put("baksteenrand", "baksteen", bz(x, x + L, MAIN[2] - 0.13, MAIN[2] + 0.01, GAL_HIGH - 0.02, GAL_HIGH + RNG.uniform(0.07, 0.10), 0.01))
        x += L + 0.02
    # hoofdhuis: steile kraag (pannen) + vrijwel plat bovendak
    m0, m1, n0, n1 = MAIN[0] - 0.16, MAIN[1] + 0.16, MAIN[2] - 0.16, MAIN[3] + 0.16
    tiled_roof("dak_hoofd", (m0, m1, n0, n1), (m0 + 0.55, m1 - 0.55, n0 + 0.55, n1 - 0.55), MAIN_CORN, MANS_BREAK, cap_top=False)
    tiled_roof("dak_hoofd", (m0 + 0.55, m1 - 0.55, n0 + 0.55, n1 - 0.55), (m0 + 2.2, m1 - 2.2, n0 + 2.2, n1 - 2.2), MANS_BREAK, MANS_TOP, course=0.5, lip=0.0, under=0.0, hips=False)
    for xd in (-0.95, 0.45):    # dakkapellen front.jpg overlay 700 / 850 px
        dormer("dakkapellen", xd, MAIN[2] - 0.05, MAIN_CORN - 0.05, 0.60, 0.80, 0.55)
    for xc, h in ((-1.75, 6.89), (0.69, 6.70)):
        put("schoorstenen", "stuc", bz(xc - 0.19, xc + 0.19, MAIN[2] + 1.55, MAIN[2] + 1.95, 6.2, h - 0.08, 0.01))
        put("schoorstenen", "omlijsting", bz(xc - 0.23, xc + 0.23, MAIN[2] + 1.51, MAIN[2] + 1.99, h - 0.08, h, 0.01))
        put("schoorstenen", "baksteen", bz(xc - 0.09, xc + 0.09, MAIN[2] + 1.66, MAIN[2] + 1.84, h, h + 0.08))
    # toren: spits met pannen, dakkapel, makelaar
    t0, t1, u0, u1 = TOWER[0] - 0.14, TOWER[1] + 0.14, TOWER[2] - 0.14, TOWER[3] + 0.14
    cx, cy = (TOWER[0] + TOWER[1]) / 2, (TOWER[2] + TOWER[3]) / 2
    tiled_roof("dak_toren", (t0, t1, u0, u1), (cx, cx, cy, cy), TOWER_CORN, TOWER_TOP, course=0.18)
    dormer("dakkapellen", 3.71, TOWER[2] + 0.12, TOWER_CORN + 0.05, 0.50, 0.85, 0.55, depth=1.0, win=(0.24, 0.42))
    finial("makelaar", cx, cy, TOWER_TOP - 0.05, 0.6)
    put("makelaar", "zink", btube([(cx, cy, TOWER_TOP + 0.35), (cx, cy, TOWER_FIN + 0.05)], 0.012, 5))
    # portiek: lessenaar tegen de toren, houten goot
    px0, px1, py0, py1 = PORCH
    tiled_roof("dak_portiek", (px0 - 0.15, px1 + 0.08, py0 - 0.25, TOWER[2]), (px0 - 0.15, px1 + 0.08, TOWER[2] - 0.01, TOWER[2]), PORCH_EAVE, PORCH_TOP + 0.45, hips=False)
    put("portiek", "groen", bz(px0 - 0.15, px1 + 0.08, py0 - 0.30, py0 - 0.22, PORCH_EAVE - 0.18, PORCH_EAVE - 0.02))    # boeiboord

    # ---------------- gevelopeningen ----------------
    # entree: rondboog 1.08 x 2.14 met dikke omlijsting, gang erachter (donker)
    ex = -4.35
    pts = arch_pts(ex, 0, 1.08, 2.14, 16)
    cutters.append((boutline(pts, y0 - 0.3, 2.9), F))
    put("entree", "omlijsting", band(pts, 0.16, y0 - 0.06, 0.08), F)
    put("entree", "omlijsting", band([(px, pz) for px, pz in arch_pts(ex, 0, 1.08 + 0.32, 2.14 + 0.16, 16)], 0.05, y0 - 0.09, 0.05), F)
    put("entree", "donker", bz(ex - 0.6, ex + 0.6, y0 + 2.55, y0 + 2.6, 0, 2.3))
    put("entree", "plint", bz(ex - 0.54, ex + 0.54, y0 - 0.25, y0 + 2.6, 0, 0.03))
    for xw in (-5.72, -3.04):   # smalle boogramen front.jpg 205 / 485 px
        window_arched(TR(0, y0, 0), xw, 1.2, 0.50, 1.15, cutters, "lancet", s=0.09)
    window_arched(TR(x0, 0, 0, -90), -(y0 + 1.7), 1.2, 0.50, 1.15, cutters, "lancet", s=0.09)   # noordzijde vleugel (tuin_nieuw.jpg)
    # hoofdhuis verdieping (front.jpg overlay 492/625/785/940 px)
    MF = TR(0, MAIN[2], 0)
    for xw in (-2.97, -1.70, 1.32):
        window_arched(MF, xw, 3.7, 0.68, 1.20, cutters, "luiken")
        cartouche(MF, xw, 3.7 + 1.20 + 0.14)
    window_arched(MF, -0.17, 3.7, 0.86, 1.20, cutters, "open")
    cartouche(MF, -0.17, 3.7 + 1.20 + 0.14)
    MN = TR(MAIN[0], 0, 0, -90)     # noordgevel hoofdhuis (tuin_nieuw.jpg: twee ramen boven, inferred onder)
    for yw in (7.2, 9.6):
        window_arched(MN, -yw, 3.7, 0.68, 1.20, cutters, "luiken")
    # toren: smal boograam + boogdeur van de uitgang
    window_arched(TR(0, TOWER[2], 0), 3.95, 3.65, 0.34, 0.95, cutters, "lancet", s=0.08)
    dpts = arch_pts(4.55, 0, 0.92, 2.05, 12)
    cutters.append((boutline(dpts, TOWER[2] - 0.3, 1.3), F))
    put("uitgang", "omlijsting", band(dpts, 0.10, TOWER[2] - 0.04, 0.06), F)
    put("uitgang", "donker", bz(4.0, 5.1, TOWER[2] + 0.95, TOWER[2] + 1.0, 0, 2.1))

    # ---------------- muren afmaken: gaten snijden ----------------
    me = bpy.data.meshes.new("AP_muren__stuc"); wall.to_mesh(me); wall.free()
    wob = bpy.data.objects.new("AP_muren__stuc", me); col("FORMS").objects.link(wob); own(wob); assign(wob, bpy.data.materials["MAT_stuc"])
    cut = bmesh.new()
    for bm, M in cutters:
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts); m2 = bpy.data.meshes.new("_c"); bm.to_mesh(m2); bm.free(); cut.from_mesh(m2); bpy.data.meshes.remove(m2)
    cme = bpy.data.meshes.new("_cutter"); cut.to_mesh(cme); cut.free()
    cob = bpy.data.objects.new("_cutter", cme); col("FORMS").objects.link(cob)
    b = wob.modifiers.new("cut", "BOOLEAN"); b.object = cob; b.operation = "DIFFERENCE"; b.solver = "EXACT"
    apply_all_modifiers(wob); bpy.data.objects.remove(cob, do_unlink=True); bpy.data.meshes.remove(cme)

    # ---------------- gaanderij: plankengordijn op een stenen plint ----------------
    put("gaanderij", "plint", bz(gx0, gx1, GAL_Y - 0.06, GAL_Y + 0.14, 0, PLINTH - 0.04, 0.02))
    put("gaanderij", "plint", bz(gx0, gx1, GAL_Y - 0.09, GAL_Y + 0.14, PLINTH - 0.04, PLINTH, 0.015))
    x = gx0 + 0.02; i = 0
    while x < gx1 - 0.05:
        wdt = min(RNG.uniform(0.16, 0.22), gx1 - 0.02 - x)
        dy = 0.035 if i % 2 else 0.0                                   # om en om naar voren: plooien van een gordijn
        zb = PLINTH + 0.06 + RNG.uniform(-0.03, 0.05)                  # onderkant hangt onregelmatig (front.jpg)
        bm = bz(x, x + wdt, GAL_Y - 0.03 - dy, GAL_Y - 0.005 - dy, zb, GAL_LOW - 0.04)
        bmesh.ops.rotate(bm, cent=(x + wdt / 2, GAL_Y, GAL_LOW), matrix=Matrix.Rotation(math.radians(RNG.uniform(-1.5, 2.5)), 3, "X"), verts=bm.verts)
        put("gaanderij", "groen", bm)
        x += wdt + 0.008; i += 1
    put("gaanderij", "groen", bz(gx0, gx1, GAL_Y - 0.10, GAL_Y + 0.0, GAL_LOW - 0.16, GAL_LOW - 0.02))   # bovenregel

    # ---------------- portiek: stijlen, plankwand, deur ----------------
    for xp in (3.99, 5.88):    # houten stijlen front.jpg 1135 / 1320 px
        put("portiek", "hout", bz(xp - 0.08, xp + 0.08, py0 + 0.02, py0 + 0.18, 0, PORCH_EAVE - 0.18, 0.01))
    put("portiek", "hout", bz(px0 - 0.1, px1 + 0.05, py0 + 0.0, py0 + 0.18, PORCH_EAVE - 0.3, PORCH_EAVE - 0.18, 0.01))   # ligger
    for k in range(4):    # plankwand links (front.jpg 1080-1130 px)
        xa = 3.40 + k * 0.135
        put("portiek", "groen", bz(xa, xa + 0.13, py0 + 0.05, py0 + 0.09, 0.03, PORCH_EAVE - 0.3))
    put("portiek", "groen", bz(px0, px0 + 0.12, py0 + 0.05, TOWER[2], 0.0, PORCH_EAVE - 0.3))       # zijwand achter de plankwand
    for k in range(5):    # opengezette deur rechts (front.jpg 1250-1315 px)
        xa = 5.17 + k * 0.13
        put("portiek", "groen", bz(xa, xa + 0.125, py0 + 0.20, py0 + 0.24, 0.02, 2.15))
    for zz in (0.35, 1.8):
        put("portiek", "lood", bz(5.2, 5.8, py0 + 0.17, py0 + 0.2, zz - 0.03, zz + 0.03))
    put("portiek", "plint", bz(px0, px1, py0, TOWER[2], 0, 0.03))

    # ---------------- objecten wegschrijven ----------------
    for (part, mat), bm in PARTS.items():
        ob = new_mesh_object(f"AP_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
