"""
03b_forms_rots: kunstrots (gelaagde platen, zitplateau, voetrichels), vijver (halve maan), randstenen, keien en kronkelend hekje.
Contouren uit ref/osm_lokaal.json (rots x0.85 naar front.jpg), hoogtes uit asset-brief.md. Alles statisch (anim = static).
"""
import bpy, bmesh, sys, os, math, json, random
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree

PHASE = "03b_forms_rots"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})
random.seed(1952)

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OSM = json.load(open(os.path.join(HERE, "ref", "osm_lokaal.json")))
FACING = Vector((0.6, -0.8)).normalized(); RIGHT = Vector((FACING.y, -FACING.x))
def osm_to_model(p):
    v = Vector(p); return (-v.dot(RIGHT), -v.dot(FACING))      # figuur kijkt naar -Y: zijn rechterhand is -X

SEAT_Z = 2.85; FOOT_Z = 2.05; FOOT_X = 1.60; Y = 0.30
WATER_Z = -0.35; ROCK_S = 0.85
FEET = [(-1.80, -2.15), (1.80, -2.15)]          # midden van de laarszolen (03a: enkel +- d*0.5)
HANDS = [(-2.25, 0.32), (2.25, 0.32)]


def inside(p, poly):
    x, y = p; c = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def edge_dist(p, poly):
    best = 1e9; P = Vector(p)
    for i in range(len(poly)):
        a = Vector(poly[i]); b = Vector(poly[(i + 1) % len(poly)]); ab = b - a
        t = max(0, min(1, (P - a).dot(ab) / ab.length_squared)); best = min(best, (P - (a + ab * t)).length)
    return best


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)


def rock_height(x, y, d):
    """hoogteveld: steile flanken, plateau 2.6, zitplek 2.85 achter, voetrichels 2.0 voor de knieën"""
    top = 2.55 + 0.25 * noise.noise(Vector((x * 0.35, y * 0.35, 1.7)))
    seat = smoothstep(1.9, 1.1, math.hypot(x / 1.25, (y - Y - 0.1) / 1.0)); top = top * (1 - seat) + SEAT_Z * seat
    for fx, fy in FEET:                               # vlakke richel onder elke laars, iets lager
        w = smoothstep(0.95, 0.55, math.hypot(x - fx, (y - fy) * 0.8)); top = top * (1 - w) + (FOOT_Z - 0.02) * w
    for hx, hy in HANDS:
        w = smoothstep(0.6, 0.3, math.hypot(x - hx, y - hy)); top = top * (1 - w) + 2.88 * w
    edge = smoothstep(0.0, 1.0, d) ** 0.45                   # steile flanken, breed plat bovenvlak (front.jpg)
    return WATER_Z - 0.25 + (top - WATER_Z + 0.25) * edge


def build(master):
    open_master(master)
    clear_owned()
    for o in list(bpy.data.objects):
        if o.name.startswith(("BLK_rots", "BLK_water", "BLK_rand")):
            o.hide_render = True; o.hide_viewport = True
    L = "LOW"
    m_rots = material("MAT_rots", (0.48, 0.50, 0.50, 1), 0.9)
    m_water = material("MAT_water", (0.06, 0.08, 0.05, 1), 0.05)
    m_steen = material("MAT_randsteen", (0.66, 0.63, 0.56, 1), 0.85)
    m_kei = material("MAT_kei", (0.58, 0.55, 0.50, 1), 0.85)
    m_hek = material("MAT_hek", (0.10, 0.18, 0.12, 1), 0.45, 0.6)

    # ================= rots: hoogteveld binnen de contour -> voxel remesh -> lagen + scheuren
    raw = [osm_to_model(p) for p in OSM["rots"][:-1]]
    cx = sum(p[0] for p in raw) / len(raw); cy = sum(p[1] for p in raw) / len(raw)
    poly = [(cx + (x - cx) * ROCK_S, cy + (y - cy) * ROCK_S) for x, y in raw]
    # voorkant iets naar voren trekken zodat de voetrichels op de rots liggen (front.jpg: laarzen op de rand)
    poly = [(x, y - 0.35 if y < cy else y) for x, y in poly]
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    S = 0.10
    nx = int((max(xs) - min(xs)) / S) + 3; ny = int((max(ys) - min(ys)) / S) + 3
    bm = bmesh.new(); grid_v = {}
    for i in range(nx):
        for j in range(ny):
            x = min(xs) - S + i * S; y = min(ys) - S + j * S
            if inside((x, y), poly):
                grid_v[(i, j)] = bm.verts.new((x, y, rock_height(x, y, edge_dist((x, y), poly))))
    for i in range(nx - 1):
        for j in range(ny - 1):
            q = [grid_v.get(k) for k in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
            if all(q):
                bm.faces.new(q)
    bnd = [e for e in bm.edges if e.is_boundary]
    r = bmesh.ops.extrude_edge_only(bm, edges=bnd)
    for v in [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]:
        v.co.z = WATER_Z - 0.6
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)   # dichte onderkant: remesh vraagt een gesloten vorm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    rots = new_mesh_object("GEO_rots", bm, L)
    remesh_voxel(rots, 0.06); apply_all_modifiers(rots)
    me = rots.data; bm = bmesh.new(); bm.from_mesh(me); bm.normal_update()
    for v in bm.verts:
        p = v.co.copy(); n = v.normal.copy()
        if p.z < WATER_Z - 0.3:
            continue
        hn = Vector((n.x, n.y, 0))
        top_w = smoothstep(0.55, 0.85, n.z)                    # bovenvlakken: zacht golvend
        side_w = 1 - top_w
        # gelaagde platen: zaagtand in z met variërende laagdikte -> overhangende richels
        lz = (p.z + 0.55 * noise.noise(p * 0.3)) / (0.55 + 0.2 * noise.noise(p * 0.2 + Vector((5, 0, 0))))
        saw = lz - math.floor(lz)
        strata = (0.5 - saw) * 0.11 * smoothstep(-0.3, 0.3, noise.noise(p * 0.45 + Vector((0, 9, 0))))   # richels alleen plaatselijk
        # grote blokken met scheuren (Voronoi, grof)
        vd = noise.voronoi(Vector((p.x * 0.55, p.y * 0.55, p.z * 0.30)), distance_metric="DISTANCE")[0]
        crack = -0.14 * smoothstep(0.18, 0.0, vd[1] - vd[0])
        bump = 0.06 * noise.fractal(p * 1.6, 0.6, 2.0, 4)
        if hn.length > 1e-4:
            hn.normalize()
        v.co += hn * (strata + crack) * side_w + n * bump + Vector((0, 0, 0.04 * noise.noise(p * 2.2))) * top_w
    bm.to_mesh(me); bm.free()
    sm = rots.modifiers.new("Smooth", "SMOOTH"); sm.factor = 0.3; sm.iterations = 1
    apply_all_modifiers(rots)
    nt = sum(len(p.vertices) - 2 for p in rots.data.polygons)
    decimate(rots, min(1.0, 16000 / max(1, nt))); apply_all_modifiers(rots)
    shade_smooth(rots, math.radians(48)); assign(rots, m_rots); rots["anim"] = "static"

    # ================= vijver: buitenboog uit OSM, water als vlak (onder de rots door)
    water = [osm_to_model(p) for p in OSM["water"][:-1]]
    WS = 0.88                                               # vijver aan de voorkant smaller dan OSM (front.jpg: rand op 0.79 van de hoogte)
    arc = [(cx + (x - cx) * WS, cy + (y - cy) * WS) for x, y in water[:11]]   # buitenboog (pleinzijde), van west naar oost
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, WATER_Z)) for x, y in arc]
    f = bm.faces.new(vs)
    if f.normal.z < 0: f.normal_flip()
    r = bmesh.ops.extrude_face_region(bm, geom=[f])                         # 8 cm dik: van boven en onder zichtbaar (Roblox toont alleen voorkanten)
    bmesh.ops.translate(bm, vec=(0, 0, -0.08), verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bmesh.ops.triangulate(bm, faces=bm.faces)
    wo = new_mesh_object("GEO_water", bm, L); assign(wo, m_water); wo["anim"] = "static"
    # dichte boog voor randstenen/hek: Catmull-Rom over de OSM-punten, vloeiend (WERKWIJZE: geen hoeken)
    def cr(p0, p1, p2, p3, t):
        return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
    A = [Vector(p) for p in arc]; A = [A[0] * 2 - A[1]] + A + [A[-1] * 2 - A[-2]]
    dense = []
    for i in range(1, len(A) - 2):
        for k in range(12):
            dense.append(cr(A[i - 1], A[i], A[i + 1], A[i + 2], k / 12))
    dense.append(A[-2])
    cum = [0.0]
    for a, b in zip(dense, dense[1:]): cum.append(cum[-1] + (b - a).length)
    def at(s, off):
        s = max(0, min(cum[-1] - 1e-4, s)); i = max(k for k in range(len(cum)) if cum[k] <= s)
        a, b = dense[i], dense[min(i + 1, len(dense) - 1)]; t = (s - cum[i]) / max(1e-6, (b - a).length)
        p = a.lerp(b, t); tan = (b - a).normalized(); out = Vector((tan.y, -tan.x))   # buitenkant = rechts van de looprichting
        if out.dot(p) < 0: out = -out
        return p + out * off, tan, out
    # randstenen: grote ronde stenen in een lage muur op de waterkant
    stones = []
    s = 0.0
    while s < cum[-1]:
        w = random.uniform(0.75, 1.2); p, tan, out = at(s + w / 2, 0.15 + random.uniform(-0.08, 0.08))
        st = bpy.data.meshes.new("_st"); b2 = bmesh.new(); bmesh.ops.create_icosphere(b2, subdivisions=2, radius=0.5)
        for v in b2.verts:
            v.co += v.co.normalized() * 0.12 * noise.noise(v.co * 2.5 + Vector((s, 0, 0)))
        h = random.uniform(0.28, 0.42)
        bmesh.ops.scale(b2, vec=(w, random.uniform(0.7, 1.0), h), verts=b2.verts)
        for v in b2.verts:                                  # platte bovenkant
            if v.co.z > h * 0.25: v.co.z = h * 0.25 + (v.co.z - h * 0.25) * 0.4
        ang = math.atan2(tan.y, tan.x)
        bmesh.ops.rotate(b2, cent=(0, 0, 0), matrix=Matrix.Rotation(ang + random.uniform(-0.15, 0.15), 3, "Z"), verts=b2.verts)
        bmesh.ops.translate(b2, vec=(p.x, p.y, -0.12 + h * 0.4), verts=b2.verts)
        b2.to_mesh(st); b2.free(); stones.append(st); s += w * 0.80
    keien = []
    s = 0.0
    while s < cum[-1]:                                      # rij kleine keien in het plein, voor het hek
        w = random.uniform(0.15, 0.24); p, tan, out = at(s, 1.05 + random.uniform(-0.05, 0.05))
        st = bpy.data.meshes.new("_kei"); b2 = bmesh.new(); bmesh.ops.create_icosphere(b2, subdivisions=1, radius=0.5)
        for v in b2.verts:
            v.co += v.co.normalized() * 0.1 * noise.noise(v.co * 3 + Vector((0, s, 0)))
        bmesh.ops.scale(b2, vec=(w, w * random.uniform(0.7, 1.0), w * 0.7), verts=b2.verts)
        bmesh.ops.translate(b2, vec=(p.x, p.y, 0.05), verts=b2.verts)
        b2.to_mesh(st); b2.free(); keien.append(st); s += w * 1.05
    for name, meshes, mat in (("GEO_randstenen", stones, m_steen), ("GEO_keien", keien, m_kei)):
        bm = bmesh.new()
        for me in meshes:
            bm.from_mesh(me); bpy.data.meshes.remove(me)
        o = new_mesh_object(name, bm, L); shade_smooth(o, math.radians(60)); assign(o, mat); o["anim"] = "static"
    # kronkelend hekje: palen + golvende bovenregel + onderregel, tussen randstenen en keien
    OFF = 0.62
    n_post = int(cum[-1] / 1.25)
    for k in range(n_post + 1):
        p, tan, out = at(k * cum[-1] / n_post, OFF)
        po = cylinder("GEO_hekpaal_%02d" % k, 0.025, 0.62, L, segments=8, location=(p.x, p.y, 0.31)); assign(po, m_hek)
        kn = sphere("GEO_hekknop_%02d" % k, 0.045, L, (p.x, p.y, 0.64), u=10, v=6); assign(kn, m_hek)
    top = []; bot = []
    N = int(cum[-1] / 0.08)
    for k in range(N + 1):
        ss = k * cum[-1] / N; p, tan, out = at(ss, OFF)
        top.append((p.x, p.y, 0.50 + 0.07 * math.sin(ss * 2 * math.pi / 0.625)))
        bot.append((p.x, p.y, 0.14))
    for name, pts in (("GEO_hekregel_boven", top), ("GEO_hekregel_onder", bot)):
        o = curve_tube(name, pts[::2], 0.018, L, resolution=3, bevel_res=2); o.data.materials.append(m_hek)
    for o in bpy.data.objects:
        if o.get("owner") == OWNER_TAG:
            o["anim"] = "static"
    save_master(master)
    log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "objects",
        "rots tris", sum(len(p.vertices) - 2 for p in rots.data.polygons))


if __name__ == "__main__":
    args = argv_after_dashes()
    master = args[args.index("--master") + 1] if "--master" in args else None
    if master:
        build(master)
