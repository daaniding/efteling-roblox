"""
06_omgeving: meshes rond de Sprookjesboom uit exports/omgeving_data.json (06_omgeving_data.py).
 - plein + paden (klinkers, 3 cm boven het maaiveld, UV 1 = 2 m) met opsluitband alleen op de buitenrand
 - wortel met klauwen die aan de pleinkant uit het beekje kruipt + wortel van de boom die de oever in duikt (front_wide.jpg, Eftepedia)
 - lage houten bankjes zonder rugleuning (OSM), rieten prullenbak (OSM material=reed)
 - 6 kei-prototypes (elk eigen materiaal -> los onderdeel in Roblox) voor oeverstenen en keien
Water en geul zitten in het Roblox-terrein (roblox/plaats_omgeving.luau). Schrijft PR_SprookjesboomOmgeving.blend en
PR_SprookjesboomStenen.blend (collectie LOW), export met 09_export_roblox.py.
Gebruik: Blender -b -P 06_omgeving.py -- --outdir <map>
"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, Euler, noise

PHASE = "06_omgeving"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix, "Euler": Euler,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "..", "exports", "omgeving_data.json")))
rnd = random.Random(7)


def M(name, rgb, rough=0.8):
    m = material("MAT_" + name, (*rgb, 1), rough)
    m.diffuse_color = (*rgb, 1)
    return m


def flat_polys(name, polys, z_top, z_bot, mat):
    """polygonen met gaten -> plaat (bovenkant z_top, zijkant tot z_bot), UV bovenkant = xy / 2 m."""
    bm = bmesh.new()
    for p in polys:
        loops = [p["ext"]] + p["holes"]
        edges = []
        for ring in loops:
            vs = [bm.verts.new((x, y, z_top)) for x, y in ring]
            edges += [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
        res = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)
        tops = [f for f in res["geom"] if isinstance(f, bmesh.types.BMFace)]
        for f in tops:
            if f.normal.z < 0: f.normal_flip()
        # zijkanten
        bnd = [e for e in edges if len(e.link_faces) == 1]
        ext = bmesh.ops.extrude_edge_only(bm, edges=bnd)
        bmesh.ops.translate(bm, vec=(0, 0, z_bot - z_top), verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        ax = max(range(3), key=lambda i: abs(f.normal[i]))
        for lp in f.loops:
            c = lp.vert.co; u, v = [(c.y, c.z), (c.x, c.z), (c.x, c.y)][ax]
            lp[uv].uv = (u / 2, v / 2)
    ob = new_mesh_object(name, bm, "LOW"); assign(ob, mat); shade_smooth(ob, math.radians(30))
    return ob


def tube_mesh(name, pts, radii, mat, sides=10, rough=0.03, seed=0):
    """buis door punten met straal per punt (bmesh, gesloten uiteinde) en wat ruis: wortels/klauwen."""
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap"); rings = []
    pts = [Vector(p) for p in pts]
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        x = t.orthogonal().normalized(); y = t.cross(x)
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides
            q = p + (x * math.cos(a) + y * math.sin(a)) * radii[i]
            q += (q - p).normalized() * radii[i] * rough * 8 * noise.noise(q * 6 + Vector((seed, 0, 0)))
            ring.append(bm.verts.new(q))
        rings.append(ring)
    L = 0.0
    for i in range(len(rings) - 1):
        seg = (pts[i + 1] - pts[i]).length
        for k in range(sides):
            j = (k + 1) % sides
            f = bm.faces.new((rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]))
            for lp, (u, v) in zip(f.loops, ((k / sides, L), ((k + 1) / sides, L), ((k + 1) / sides, L + seg), (k / sides, L + seg))):
                lp[uv].uv = (u * 2 * math.pi * radii[i] / 0.5, v / 0.5)
        L += seg
    tip = bm.verts.new(pts[-1] + (pts[-1] - pts[-2]).normalized() * radii[-1] * 0.8)
    for k in range(sides):
        bm.faces.new((rings[-1][k], rings[-1][(k + 1) % sides], tip))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_mesh_object(name, bm, "LOW"); assign(ob, mat); shade_smooth(ob, math.radians(70))
    return ob


def smooth_path(ctrl, n=10):
    """Catmull-Rom door controlepunten."""
    P = [Vector(c) for c in ctrl]; P = [P[0]] + P + [P[-1]]; out = []
    for i in range(1, len(P) - 2):
        for s in range(n):
            t = s / n; p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2]); return out


def beek():
    """geul als hoogteveld (raster 0.15 m) rond de OSM-beek: bodem -0.55, waterlijn -0.32 op 0.25 m buiten de beekrand,
    oever tot het maaiveld op 0.95 m, grasrand tot 1.6 m die aan de buitenkant 2 cm onder het terrein duikt (naadloos).
    Plus het wateroppervlak (beek + 0.25 m) op -0.32. front_wide.jpg: water ~0.3-0.5 m onder het gras, stenen oevers."""
    import numpy as np
    poly = np.array(D["beek"][0]["ext"], float); n = len(poly)
    keepp = np.r_[True, np.hypot(*(poly[1:] - poly[:-1]).T) > 1e-4]; poly = poly[keepp]   # dubbele punten weg
    A0 = poly; B0 = np.roll(poly, -1, axis=0); AB = B0 - A0; L2 = np.maximum((AB ** 2).sum(1), 1e-9)
    def sdist(P):
        out = np.empty(len(P))
        for s in range(0, len(P), 4000):
            Q = P[s:s + 4000]
            t = np.clip(((Q[:, None, :] - A0[None]) * AB[None]).sum(2) / L2[None], 0, 1)
            C = A0[None] + t[..., None] * AB[None]
            dmin = np.sqrt(((Q[:, None, :] - C) ** 2).sum(2)).min(1)
            yi, yj = A0[None, :, 1], B0[None, :, 1]
            cross = ((yi > Q[:, None, 1]) != (yj > Q[:, None, 1])) & (Q[:, None, 0] < (B0[None, :, 0] - A0[None, :, 0]) * (Q[:, None, 1] - yi) / np.where(yj - yi == 0, 1e-9, yj - yi) + A0[None, :, 0])
            inside = cross.sum(1) % 2 == 1
            out[s:s + 4000] = np.where(inside, -dmin, dmin)
        return out
    G = 0.15; R = 1.6
    xs = np.arange(poly[:, 0].min() - R - G, poly[:, 0].max() + R + G, G); ys = np.arange(poly[:, 1].min() - R - G, poly[:, 1].max() + R + G, G)
    X, Y = np.meshgrid(xs, ys); P = np.stack([X.ravel(), Y.ravel()], 1)
    d = sdist(P).reshape(X.shape)
    def zf(dd):
        z = np.where(dd < 0.0, -0.55, -0.55 + 0.23 * np.clip(dd / 0.25, 0, 1))                 # bodem -> waterlijn
        bank = np.clip((dd - 0.25) / 0.70, 0, 1); bank = bank * bank * (3 - 2 * bank)
        z = np.where(dd >= 0.25, -0.32 + 0.34 * bank, z)                                       # oever tot +0.02
        z = np.where(dd > 1.30, 0.02 - 0.04 * np.clip((dd - 1.30) / 0.30, 0, 1), z)            # rand duikt onder het terrein
        return z
    Z = zf(d) + 0.015 * np.sin(X * 7.1) * np.cos(Y * 6.3) * (d > 0.3) * (d < 1.0)
    keep = d < R
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap"); vid = {}
    def V(i, j):
        k = (i, j)
        if k not in vid: vid[k] = bm.verts.new((X[i, j], Y[i, j], Z[i, j]))
        return vid[k]
    m_bed = M("beekbodem", (0.20, 0.17, 0.13), 0.9); m_oever = M("oever", (0.30, 0.25, 0.19), 0.95); m_gras = M("gras", (0.33, 0.45, 0.20), 0.95)
    mats = [m_bed, m_oever, m_gras]
    faces_mat = []
    for i in range(X.shape[0] - 1):
        for j in range(X.shape[1] - 1):
            if keep[i, j] and keep[i + 1, j] and keep[i, j + 1] and keep[i + 1, j + 1]:
                f = bm.faces.new((V(i, j), V(i, j + 1), V(i + 1, j + 1), V(i + 1, j)))
                dc = (d[i, j] + d[i + 1, j + 1]) / 2
                f.material_index = 0 if dc < 0.30 else (1 if dc < 1.0 else 2)
                for lp in f.loops: lp[uv].uv = (lp.vert.co.x / 2, lp.vert.co.y / 2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.z < 0: f.normal_flip()
    # per materiaal een los object (export groepeert op materiaal)
    for mi, mat in enumerate(mats):
        b2 = bm.copy(); bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.material_index != mi], context="FACES")
        ob = new_mesh_object(f"GEO_geul_{mat.name}", b2, "LOW"); assign(ob, mat); shade_smooth(ob, math.radians(60))
    bm.free()
    flat_polys("GEO_water", D["water"], -0.32, -0.33, M("water", (0.16, 0.22, 0.18), 0.05))


def omgeving(outdir):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    m_pave = M("klinker", (0.60, 0.53, 0.46), 0.85); m_band = M("band", (0.46, 0.45, 0.43), 0.9)
    m_bark = M("branch", (0.47, 0.44, 0.39), 0.85)
    m_hout = M("hout", (0.34, 0.24, 0.15), 0.75); m_hout2 = M("hout_kops", (0.52, 0.40, 0.27), 0.8)
    m_riet = M("riet", (0.62, 0.48, 0.28), 0.9); m_rand = M("ijzer", (0.18, 0.20, 0.18), 0.5); m_zwart = M("hollow_dark", (0.05, 0.04, 0.03), 0.95)
    flat_polys("GEO_paving", D["paving"], 0.03, -0.12, m_pave)
    flat_polys("GEO_band", D["band"], 0.06, -0.12, m_band)
    try:
        beek()
    except Exception:
        import traceback; traceback.print_exc(); raise
    # wortel van de boom de oever in (rechtervoet -> beek), en de wortel die aan de pleinkant weer opduikt met klauwen
    r1 = smooth_path([(1.7, -1.5, 0.45), (2.4, -2.4, 0.30), (3.0, -3.3, 0.05), (3.4, -3.9, -0.40)])
    tube_mesh("GEO_wortel_in", r1, [0.26 - 0.10 * i / (len(r1) - 1) for i in range(len(r1))], m_bark, 12, seed=1)
    # waterkant aan de zuidkant van de beek bij x ~ 3.6: punt uit de data (stenen-rij 0 die het dichtst bij (3.6, -5.2) ligt)
    sx, sy = min(((s[0], s[1]) for s in D["stenen"]), key=lambda q: math.hypot(q[0] - 3.6, q[1] - 5.6 * -1))
    r2 = smooth_path([(sx - 0.15, sy + 0.35, -0.45), (sx, sy, 0.10), (sx + 0.15, sy - 0.55, 0.30), (sx + 0.25, sy - 1.05, 0.22)])
    rad2 = [0.22 - 0.05 * i / (len(r2) - 1) for i in range(len(r2))]
    tube_mesh("GEO_wortel_uit", r2, rad2, m_bark, 12, seed=2)
    # tweede wortel die over het beekje boogt en met de vingers in het water hangt (Boom_wortels.jpg)
    wx, wy = min(((s[0], s[1]) for s in D["stenen"]), key=lambda q: math.hypot(q[0] + 2.2, q[1] + 3.6))
    r3 = smooth_path([(-1.5, -2.0, 0.40), (wx * 0.8, wy * 0.85, 0.55), (wx, wy - 0.5, 0.30)])
    tube_mesh("GEO_wortel_poel", r3, [0.20 - 0.07 * i / (len(r3) - 1) for i in range(len(r3))], m_bark, 12, seed=11)
    hand = Vector(r3[-1])
    for k in range(5):
        a = math.radians(rnd.uniform(0, 360)); dd = Vector((math.cos(a) * 0.25, math.sin(a) * 0.25, 0))
        f = smooth_path([hand, hand + dd * 0.5 + Vector((0, 0, -0.15)), hand + dd + Vector((0, 0, -0.55)), hand + dd * 1.1 + Vector((0, 0, -0.75))], 6)
        tube_mesh(f"GEO_poelvinger{k}", f, [0.07 - 0.045 * i / (len(f) - 1) for i in range(len(f))], m_bark, 7, seed=30 + k)
    palm = Vector(r2[-1])
    for k, ang in enumerate((-60, -30, 0, 30, 60)):     # klauwvingers die op de grond rusten (front_wide.jpg)
        a = math.radians(-90 + ang + rnd.uniform(-6, 6)); L = rnd.uniform(0.55, 0.85)
        d = Vector((math.cos(a), math.sin(a), 0))
        f = smooth_path([palm, palm + d * L * 0.35 + Vector((0, 0, 0.10)), palm + d * L * 0.75 + Vector((0, 0, 0.05)),
                         palm + d * L + Vector((0, 0, -0.04))], 6)
        tube_mesh(f"GEO_klauw{k}", f, [0.10 - 0.06 * i / (len(f) - 1) for i in range(len(f))], m_bark, 8, seed=3 + k)
    # bankjes: zitplank 1.8 x 0.40, hoogte 0.40 (laag, OSM backrest=no), twee boomstamvoetjes
    for i, (x, y, ang) in enumerate(D["banken"]):
        rot = Matrix.Rotation(math.radians(ang), 4, "Z"); base = Matrix.Translation((x, y, 0))
        parts = [box(f"P_zit{i}", (0.40, 1.80, 0.07), "LOW", (0, 0, 0.365))]
        for s in (-0.62, 0.62):
            parts.append(cylinder(f"P_poot{i}{s}", 0.13, 0.33, "LOW", segments=14, location=(0, s, 0.165)))
        for p in parts:
            p.data.transform(base @ rot @ Matrix.Translation(p.location)); p.location = (0, 0, 0)
        plank = parts[0]; assign(plank, m_hout); bevel(plank, 0.012, 2); apply_all_modifiers(plank)
        for p in parts[1:]: assign(p, m_hout2)
        plank.name = f"GEO_bank{i}"
        for j, p in enumerate(parts[1:]): p.name = f"GEO_bankpoot{i}_{j}"
    # rieten prullenbak met ijzeren rand
    for i, (x, y) in enumerate(D["bak"]):
        b = profile_spin(f"GEO_bak{i}", [(0.0, 0.0), (0.23, 0.0), (0.26, 0.40), (0.28, 0.78), (0.265, 0.78), (0.245, 0.10), (0.0, 0.10)], "LOW", steps=28, location=(x, y, 0))
        assign(b, m_riet)
        r = cylinder(f"GEO_bakrand{i}", 0.29, 0.04, "LOW", segments=28, location=(x, y, 0.78)); assign(r, m_rand)
        z = cylinder(f"GEO_bakbinnen{i}", 0.245, 0.01, "LOW", segments=20, location=(x, y, 0.55)); assign(z, m_zwart)
    extra(m_bark, m_rand)
    os.makedirs(outdir, exist_ok=True)
    save_master(os.path.join(outdir, "PR_SprookjesboomOmgeving.blend"))


def extra(m_bark, m_ijzer):
    """hekje, wortelboogjes, roeptoeter, lantaarns (Eftepedia-foto's in ref/eftepedia)."""
    # laag zwart kniehekje: ronde paaltjes 0.55 m om de 1.2 m, twee buisleuningen (Sprookjesboomopening.jpg)
    for k, run in enumerate(D.get("hek", [])):
        for i, (x, y) in enumerate(run):
            po = cylinder(f"GEO_hekpaal{k}_{i}", 0.025, 0.58, "LOW", segments=8, location=(x, y, 0.29)); assign(po, m_ijzer)
            kn = sphere(f"GEO_hekknop{k}_{i}", 0.035, "LOW", (x, y, 0.59), u=8, v=4); assign(kn, m_ijzer)
        for h in (0.25, 0.50):
            pts = [(x, y, h) for x, y in run]
            tube_mesh(f"GEO_hekbuis{k}_{h}", pts, [0.014] * len(pts), m_ijzer, 6, rough=0.0)
    # wortelboogjes: kromme wortels die uit de grond komen en er weer in duiken
    for i, (x, y, ang, L) in enumerate(D.get("stubs", [])):
        a = math.radians(ang); d = Vector((math.cos(a), math.sin(a), 0)); c = Vector((x, y, 0))
        h = rnd.uniform(0.18, 0.32)
        pts = smooth_path([c - d * L * 0.55 + Vector((0, 0, -0.10)), c - d * L * 0.25 + Vector((0, 0, h * 0.8)),
                           c + d * L * 0.15 + Vector((0, 0, h)), c + d * L * 0.55 + Vector((0, 0, -0.08))], 6)
        r0 = rnd.uniform(0.07, 0.12)
        tube_mesh(f"GEO_wortelboog{i}", pts, [r0 * (1 - 0.35 * j / (len(pts) - 1)) for j in range(len(pts))], m_bark, 9, seed=20 + i)
    # roeptoeter: stompje met tonderzwam-plankjes en een trechter van zwammen (KindbijSprookjesboom.JPG)
    tt = D.get("toeter")
    if tt:
        x, y, ang = tt; m_zwam = M("zwam", (0.62, 0.50, 0.36), 0.85); m_zwam2 = M("zwam_rand", (0.86, 0.80, 0.68), 0.8)
        st = tube_mesh("GEO_toeterstomp", smooth_path([(x, y, -0.05), (x + 0.02, y, 0.45), (x + 0.04, y + 0.02, 0.80)], 6),
                       [0.17, 0.16, 0.15, 0.14, 0.14, 0.13, 0.13, 0.12, 0.12, 0.12, 0.11, 0.11, 0.11], m_bark, 12, seed=40)
        for j, (zz, aa, rr) in enumerate(((0.30, 20, 0.16), (0.48, 150, 0.14), (0.62, 260, 0.12))):   # plankjes
            sh = sphere(f"GEO_zwamplank{j}", rr, "LOW", (x + math.cos(math.radians(aa)) * 0.15, y + math.sin(math.radians(aa)) * 0.15, zz), u=16, v=8, scale=(1, 1, 0.28))
            assign(sh, m_zwam); rim = cylinder(f"GEO_zwamrand{j}", rr * 0.98, 0.015, "LOW", segments=16, location=sh.location - Vector((0, 0, 0.005))); assign(rim, m_zwam2)
        a = math.radians(ang)
        hoorn = profile_spin("GEO_toeterhoorn", [(0.0, 0.0), (0.06, 0.0), (0.07, 0.12), (0.10, 0.22), (0.17, 0.30), (0.24, 0.34), (0.22, 0.35), (0.15, 0.31), (0.08, 0.23), (0.0, 0.20)], "LOW", steps=20)
        hoorn.data.transform(Matrix.Rotation(math.radians(70), 4, "Y")); hoorn.data.transform(Matrix.Rotation(a, 4, "Z"))
        hoorn.location = (x + 0.02, y + 0.02, 0.80); apply_transform(hoorn); assign(hoorn, m_zwam)
    # klassieke zwarte lantaarn: voet, taps paaltje, kap met 4 ruiten, dakje met knop (Sprookjesboomopening.jpg)
    m_glas = M("lampglas", (0.95, 0.88, 0.62), 0.2)
    for i, (x, y) in enumerate(D.get("lantaarns", [])):
        v = profile_spin(f"GEO_lantaarnpaal{i}", [(0, 0), (0.16, 0), (0.16, 0.10), (0.10, 0.18), (0.075, 0.30), (0.055, 2.40), (0.085, 2.46), (0.085, 2.52), (0, 2.52)], "LOW", steps=12, location=(x, y, 0))
        assign(v, m_ijzer)
        g = box(f"GEO_lantaarnglas{i}", (0.26, 0.26, 0.40), "LOW", (x, y, 2.74)); assign(g, m_glas)
        for sx in (-1, 1):
            for sy in (-1, 1):
                s_ = box(f"GEO_lantaarnstijl{i}{sx}{sy}", (0.03, 0.03, 0.44), "LOW", (x + sx * 0.14, y + sy * 0.14, 2.74)); assign(s_, m_ijzer)
        dk = profile_spin(f"GEO_lantaarndak{i}", [(0, 2.94), (0.24, 2.94), (0.20, 2.99), (0.06, 3.14), (0.03, 3.20), (0.05, 3.25), (0, 3.30)], "LOW", steps=4, location=(x, y, 0))
        dk.rotation_euler.z = math.radians(45); apply_transform(dk); assign(dk, m_ijzer)
        bd = box(f"GEO_lantaarnbodem{i}", (0.32, 0.32, 0.05), "LOW", (x, y, 2.53)); assign(bd, m_ijzer)


def stenen(outdir):
    """6 hoekige breuksteen-prototypes (lichtgrijs/blauwig, Boom_wortels.jpg/Rodosb.jpg), 1 m doorsnede, oorsprong onderin."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cols = [(0.70, 0.71, 0.73), (0.62, 0.64, 0.68), (0.74, 0.73, 0.71), (0.56, 0.58, 0.62), (0.78, 0.78, 0.79), (0.66, 0.66, 0.66)]
    for k in range(6):
        bm = bmesh.new()
        pts = []
        for i in range(26):    # willekeurige punten op een afgeplatte ellipsoide -> convex omhulsel = gebroken steen met facetten
            u = rnd.uniform(-1, 1); a = rnd.uniform(0, 2 * math.pi); s = math.sqrt(1 - u * u)
            pts.append(Vector((s * math.cos(a) * rnd.uniform(0.85, 1.15), s * math.sin(a) * rnd.uniform(0.6, 0.95), u * rnd.uniform(0.45, 0.75))) * 0.5)
        for q in pts: bm.verts.new(q)
        bmesh.ops.convex_hull(bm, input=bm.verts)
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.025, segments=1, affect="EDGES")
        mn = min(v.co.z for v in bm.verts)
        for v in bm.verts: v.co.z -= mn
        ob = new_mesh_object(f"steen{k}", bm, "LOW"); assign(ob, M(f"steen{k}", cols[k], 0.85)); shade_smooth(ob, math.radians(35))
    save_master(os.path.join(outdir, "PR_SprookjesboomStenen.blend"))


if __name__ == "__main__":
    a = argv_after_dashes(); od = a[a.index("--outdir") + 1]
    omgeving(od); stenen(od)
