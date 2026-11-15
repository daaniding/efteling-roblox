"""03_boom De Trollenkoning (1988): holle, afgebroken boomstronk in een vijvertje, met holte (spitsboog) met dicht rood fluwelen gordijn boven een
houten troonkist, drie reuzenzwammen boven de holte, een trapje kleine zwammen rechts, een bel aan een korte tak, wortels en stenen in het water,
klimop op de bovenstam. Bronnen + maten: asset-brief.md. Frame: oorsprong midden OSM 766787184, -Y = holte (ZO), z 0 = maaiveld.
Gebruik: Blender -b -P 03_boom.py -- --master TK_boom_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"schors": ((0.36, 0.36, 0.3, 1), 0.95), "zwam": ((0.62, 0.5, 0.38, 1), 0.8), "zwamplaat": ((0.8, 0.72, 0.6, 1), 0.85), "gordijn": ((0.45, 0.04, 0.06, 1), 0.7),
        "goud": ((0.8, 0.6, 0.22, 1), 0.3), "hout": ((0.5, 0.36, 0.22, 1), 0.8), "rots": ((0.45, 0.45, 0.42, 1), 0.95), "brons": ((0.55, 0.4, 0.2, 1), 0.35),
        "touw": ((0.6, 0.5, 0.35, 1), 0.9), "klimop": ((0.12, 0.24, 0.1, 1), 0.7), "donker": ((0.04, 0.03, 0.03, 1), 0.9)}
H_TOP = 8.9                                   # gemiddelde breukhoogte (Boomtrollenkoning: ~2.2 x de grote zwam)
HOL_W, HOL_Z0, HOL_Z1 = 1.5, 1.7, 4.0         # holte: breedte, gordijn-onderkant, top (Boomtrollenkoning: 0.6 x stambreedte); opening loopt door tot HOL_ZB
HOL_ZB = 0.5
rr = random.Random(1988)


def R_of(z, phi):
    """stamstraal: taps + wortelvoet met 6 steunwortels + verticale groeven"""
    zc = max(z, -0.4)
    r = 1.12 + 0.22 * (1 - min(zc, 9) / 9) + 0.62 * math.exp(-(zc + 0.4) / 0.85)
    lob = max(0.0, math.cos(4.5 * (phi - 0.35) + 0.4 * math.sin(phi * 2))) ** 8
    r += math.exp(-(zc + 0.4) / 1.7) * (0.95 * lob - 0.18 * (1 - lob))                       # 9 losse wortelribben met diepe groeven ertussen (Boomtrollenkoning)
    r += 0.07 * noise.noise(Vector((math.cos(phi) * 1.6, math.sin(phi) * 1.6, z * 0.35)))
    r += 0.035 * math.sin(phi * 19 + 2.0 * noise.noise(Vector((phi, z * 0.5, 0.3))))
    return r


def top_of(phi):
    return H_TOP + 1.1 * noise.noise(Vector((math.cos(phi) * 2.2, math.sin(phi) * 2.2, 4.1))) + 0.9 * max(0, math.sin(phi * 3 + 1.0)) ** 6


def stam():
    bm = bmesh.new(); N = 56; zs = [-0.5 + 0.18 * k for k in range(int((H_TOP + 2.2) / 0.18))]
    rings = []
    for z in zs:
        ring = []
        for i in range(N):
            phi = i / N * math.tau; zt = top_of(phi); zz = min(z, zt); r = R_of(zz, phi) * (0.92 if z >= zt else 1.0)
            ring.append(bm.verts.new((r * math.cos(phi), r * math.sin(phi), zz)))
        rings.append(ring)
    for A, B in zip(rings, rings[1:]):
        for i in range(N): bm.faces.new((A[i], A[(i + 1) % N], B[(i + 1) % N], B[i]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def wortels():
    out = bmesh.new()
    for k in range(10):
        phi = (k / 7 * math.tau + 0.35) if k < 7 else rr.uniform(0, math.tau); L = rr.uniform(2.4, 2.95)
        pts = []
        for t in [i / 7 for i in range(8)]:
            r = 1.0 + (L - 1.0) * t; z = 1.9 * (1 - t) ** 1.8 - 0.35 * t
            wob = 0.15 * math.sin(t * 5 + k)
            pts.append(Vector(((r) * math.cos(phi + wob * 0.2), (r) * math.sin(phi + wob * 0.2), z)))
        for a, b, t in zip(pts, pts[1:], [i / 7 for i in range(7)]):
            seg = btube([a, b], 0.38 * (1 - t) + 0.08, 8)
            me = bpy.data.meshes.new("_w"); seg.to_mesh(me); seg.free(); out.from_mesh(me); bpy.data.meshes.remove(me)
    return out


def zwam(cx, cy, cz, R, H, tilt, rot, part="zwam", lamellen=True):
    """beugelzwam: bolle hoed met omkrullende rand; onderkant met plaatjes die van de rand naar de stam omhoog lopen (Boomtrollenkoning)"""
    M = TR(cx, cy, cz, rot) @ Matrix.Rotation(math.radians(tilt), 4, "X")
    top = [(0, 0.5 * H), (R * 0.96, 0.12 * H), (R * 1.02, 0.18 * H), (R * 1.03, 0.32 * H), (R * 0.96, 0.52 * H), (R * 0.8, 0.74 * H), (R * 0.55, 0.9 * H), (R * 0.25, 0.98 * H), (0, 1.0 * H)]
    put(part, "zwam", blathe(top, 30), M.copy())
    zu = lambda r: 0.45 * H - 0.33 * H * (r / R) ** 1.2                                   # onderkant: rand laag, naar het midden omhoog
    bot = [(0, zu(0) + 0.03), (0, zu(0))] + [(R * u, zu(R * u)) for u in (0.2, 0.45, 0.7, 0.9, 0.97)] + [(R * 0.97, 0.12 * H + 0.01)]
    put(part, "zwamplaat", blathe(bot[1:] + [(0, zu(0) + 0.04)], 30), M.copy())
    if lamellen:
        n = 52
        for k in range(n):
            a = k / n * math.tau
            fb = bmesh.new(); pts = [(R * u, zu(R * u)) for u in (0.18, 0.4, 0.6, 0.8, 0.95)]
            V0 = [fb.verts.new((x, -0.006, z + 0.005)) for x, z in pts]; V1 = [fb.verts.new((x, 0.006, z + 0.005)) for x, z in pts]
            V2 = [fb.verts.new((x, 0.0, z - 0.025 * H - 0.02)) for x, z in pts]
            for i in range(len(pts) - 1):
                fb.faces.new((V0[i], V0[i + 1], V2[i + 1], V2[i])); fb.faces.new((V1[i + 1], V1[i], V2[i], V2[i + 1]))
            bmesh.ops.recalc_face_normals(fb, faces=fb.faces)
            put(part, "zwamplaat", fb, M @ Matrix.Rotation(a, 4, "Z"))


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ---------- stam + wortels -> een organische massa ----------
    s = stam(); w = wortels()
    me = bpy.data.meshes.new("_w"); w.to_mesh(me); w.free(); s.from_mesh(me); bpy.data.meshes.remove(me)
    body = organisch(s, 0.055, 3, 0.45, 0.045, 2.2, 0.34)
    ob = new_mesh_object("TK_stam__schors", body, "FORMS"); assign(ob, bpy.data.materials["MAT_schors"])
    # holte uitsnijden (spitsboog, tot ~0.45 m achter het hart)
    hp = [(-HOL_W / 2, HOL_Z0)] + [(-HOL_W / 2 * math.cos(t * math.pi / 2) ** 0.7 * (1 if t < 1 else 0), HOL_Z1 - 1.0 + 1.0 * math.sin(t * math.pi / 2)) for t in [k / 8 for k in range(9)]]
    hp = [(-HOL_W / 2 * 0.92, HOL_ZB), (-HOL_W / 2, HOL_Z1 - 1.2)] + [(-HOL_W / 2 * (1 - t) ** 0.75, HOL_Z1 - 1.2 + 1.2 * math.sin(t * math.pi / 2)) for t in [k / 10 for k in range(1, 11)]]
    hp = hp + [(-x, z) for x, z in hp[::-1]]
    seen = []; hp2 = []
    for p in hp:
        if not seen or (abs(p[0] - seen[-1][0]) > 1e-4 or abs(p[1] - seen[-1][1]) > 1e-4): hp2.append(p); seen.append(p)
    cut = boutline(hp2[:-1] if hp2[0] == hp2[-1] else hp2, -3.0, 2.55)
    cme = bpy.data.meshes.new("CUT_hol"); cut.to_mesh(cme); cut.free(); cob = bpy.data.objects.new("CUT_hol", cme); bpy.context.scene.collection.objects.link(cob)
    md = ob.modifiers.new("hol", "BOOLEAN"); md.object = cob; md.operation = "DIFFERENCE"; md.solver = "EXACT"
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier="hol"); bpy.data.objects.remove(cob)
    coll_box(0, 0.25, 4.0, 2.6, 2.4, 8.0)
    # ---------- troonkist + gordijn (dicht: zo staat hij als niemand een sterrenbeeld kiest) ----------
    put("hol", "hout", bz(-HOL_W / 2 * 0.9, HOL_W / 2 * 0.9, -1.05, -0.4, HOL_ZB - 0.1, HOL_Z0, 0.02))                       # kist onder de holte (2023: licht hout)
    for x in (-0.4, 0.0, 0.4): put("hol", "hout", bz(x - 0.16, x + 0.16, -1.07, -1.05, HOL_ZB + 0.1, HOL_Z0 - 0.1))           # paneeltjes
    put("hol", "donker", bz(-HOL_W / 2, HOL_W / 2, -0.47, -0.42, HOL_Z0, HOL_Z1))                                     # achterwand
    gb = bmesh.new(); nx, nz = 40, 14
    V = [[gb.verts.new((-HOL_W / 2 - 0.05 + (HOL_W + 0.1) * i / nx, -0.78 + 0.055 * math.sin(i / nx * math.pi * 11) * (1 - 0.3 * j / nz), HOL_Z0 + (HOL_Z1 - HOL_Z0 - 0.05) * j / nz)) for j in range(nz + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(nz): gb.faces.new((V[i][j], V[i + 1][j], V[i + 1][j + 1], V[i][j + 1]))
    bmesh.ops.solidify(gb, geom=gb.faces[:], thickness=0.03); bmesh.ops.recalc_face_normals(gb, faces=gb.faces)
    put("hol", "gordijn", gb)
    put("hol", "goud", btube([(-HOL_W / 2, -0.8, HOL_Z1 - 0.45), (HOL_W / 2, -0.8, HOL_Z1 - 0.45)], 0.025, 6))
    LAMPS_.append([0.0, -1.0, 3.0])
    # ---------- reuzenzwammen (Boekloc, 2023, Boomtrollenkoning) + trapje kleine zwammen rechts ----------
    zwam(0.0, -1.0, 4.6, 1.5, 1.55, 8, 0)                                     # Boomtrollenkoning: 1.23 x stambreedte, onderkant ~0.6 boven de holte
    zwam(-1.45, -0.55, 3.6, 0.88, 0.85, 10, 30)
    zwam(1.45, -0.6, 3.72, 0.92, 0.88, 10, -30)
    for k in range(7):                                                          # trapje: van de stam rechts (z 2.0) schuin naar buiten omlaag over de wortel
        t = k / 6; zwam(1.15 + 0.75 * t + rr.uniform(-0.08, 0.08), -0.65 - 0.35 * t, 2.0 - 1.65 * t + rr.uniform(-0.06, 0.06), 0.34 + 0.05 * math.sin(k), 0.12, 12, -45 + 15 * t, "zwammetjes", False)
    # ---------- tak met de bel (Trollenkoning_1988; Van de Ven-schets: touw aan de klepel) ----------
    tak = [Vector((0.95, -0.5, 3.0)), Vector((1.45, -0.7, 3.2)), Vector((1.85, -0.85, 3.3)), Vector((2.05, -0.9, 3.25))]
    for a, b, rad in zip(tak, tak[1:], (0.16, 0.11, 0.07)): put("tak", "schors", btube([a, b], rad, 8))
    bx, by = 1.7, -0.8
    put("bel", "touw", btube([(bx, by, 3.3), (bx, by, 3.1)], 0.015, 5))
    put("bel", "brons", blathe([(0.02, 0.38), (0.06, 0.37), (0.1, 0.3), (0.13, 0.15), (0.18, 0.03), (0.2, 0.0), (0.17, 0.0), (0.0, 0.05)], 16), TR(bx, by, 2.72))
    put("bel", "brons", ell((bx, by, 2.7), (0.04, 0.04, 0.04), 8, 6))
    put("bel", "touw", btube([(bx, by, 2.68), (bx + 0.04, by - 0.05, 2.0), (bx + 0.02, by - 0.08, 1.4)], 0.012, 5))
    for k in range(6):                                                                   # afgebroken splinters naast de klimop (Boomtrollenkoning)
        phi = 0.6 + k * 0.55; r = R_of(H_TOP, phi) * 0.75; zt = top_of(phi)
        sp_ = blathe([(0.0, 0.0), (0.22, 0.0), (0.12, 0.6), (0.03, 1.1 + 0.3 * math.sin(k)), (0, 1.15 + 0.3 * math.sin(k))], 6)
        for v in sp_.verts: v.co.x *= 1.6
        put("tak", "schors", sp_, TR(r * math.cos(phi), r * math.sin(phi), zt - 0.3, math.degrees(phi)))
    # ---------- klimop op de bovenstam (2023) ----------
    kb = bmesh.new()
    for _ in range(2600):
        phi = rr.uniform(0, math.tau); z = rr.uniform(5.3, top_of(phi) - 0.2)
        if math.sin(phi) < -0.55 and z < 6.0: continue                                       # niet over de zwammen/holte
        r = R_of(z, phi) + 0.06; c = Vector((r * math.cos(phi), r * math.sin(phi), z)); n = Vector((math.cos(phi), math.sin(phi), 0))
        t = n.cross(Vector((0, 0, 1))).normalized(); u = Vector((0, 0, 1)); s_ = rr.uniform(0.07, 0.13); a = rr.uniform(0, math.tau)
        t2 = t * math.cos(a) + u * math.sin(a); u2 = -t * math.sin(a) + u * math.cos(a)
        q = [c + t2 * s_, c + u2 * s_ * 1.2 + n * 0.03, c - t2 * s_, c - u2 * s_ * 0.6]
        f = kb.faces.new([kb.verts.new(p) for p in q])
    bmesh.ops.recalc_face_normals(kb, faces=kb.faces)
    for f in kb.faces:
        if f.normal.dot(f.calc_center_median().to_2d().to_3d().normalized()) < 0: f.normal_flip()
    put("klimop", "klimop", kb)
    # ---------- stenen in het vijvertje rond de voet (Boomtrollenkoning) ----------
    for k in range(70):                                                                  # hoekige leisteenachtige brokken (Boomtrollenkoning)
        phi = rr.uniform(0, math.tau); r = rr.uniform(1.7, 2.75); sc = rr.uniform(0.14, 0.3)
        st = bz(-sc, sc, -sc * rr.uniform(0.5, 0.8), sc * rr.uniform(0.5, 0.8), -sc * 0.5, sc * rr.uniform(0.4, 0.9), sc * 0.15)
        for v in st.verts: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * sc * 0.25
        put("stenen", "rots", st, TR(r * math.cos(phi), r * math.sin(phi), -0.3 + sc * 0.3, rr.uniform(0, 360)))
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"TK_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_}, open(os.path.join(out, "boom_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
