"""03_omgeving De Nieuwe Kleren van de Keizer: paleistuin rond het decor, volgens de plattegrond (bouwtekening) en OSM.
Gazon op decorpeil (0+P = 0.6 m boven het pad) met een glooiing naar het Sprookjesbos-hekwerk (laag zwart smeedijzer met krullen, insprong in
het midden 4170), gesnoeide hagen (voor de muur ~1.1 m, achter 3.0 m 'beplanting in bakken', zijhagen 1.8 m 'tbv wegnemen zicht'), bolstruiken,
lichte bestrating waar de figuren rijden, kijkplein met klinkers, 4 bankjes voor de haag (OSM 8787). Modelframe als 03_decor.
Gebruik: Blender -b -P 03_omgeving.py -- --master KK_omgeving_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
RNG = random.Random(1837)
MATS = {"gras": ((0.2, 0.32, 0.12, 1), 0.95), "haag": ((0.1, 0.22, 0.08, 1), 0.9), "tegels": ((0.78, 0.74, 0.66, 1), 0.9),
        "klinker": ((0.55, 0.42, 0.34, 1), 0.9), "ijzer": ((0.04, 0.04, 0.04, 1), 0.45), "hout": ((0.22, 0.34, 0.24, 1), 0.7),
        "beton": ((0.6, 0.58, 0.54, 1), 0.9), "aarde": ((0.25, 0.2, 0.14, 1), 0.95), "goud": ((0.82, 0.62, 0.22, 1), 0.3)}
Z0 = 0.6
FENCE = [(-12.0, -4.1), (-3.2, -4.1), (-2.7, -3.45), (-2.1, -2.9), (2.1, -2.9), (2.7, -3.45), (3.2, -4.1), (12.0, -4.1)]


def plaat(poly, z0, z1):
    bm = bmesh.new(); b = [bm.verts.new((x, y, z0)) for x, y in poly]; t = [bm.verts.new((x, y, z1)) for x, y in poly]
    n = len(poly); bm.faces.new(b[::-1]); bm.faces.new(t)
    for i in range(n): bm.faces.new((b[i], b[(i + 1) % n], t[(i + 1) % n], t[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], ngon_method="EAR_CLIP"); return bm


def haag(a, b, h, t=0.7, z=Z0, part="hagen"):
    a, b = Vector(a), Vector(b); d = b - a; ang = math.degrees(math.atan2(d.y, d.x))
    put(part, "haag", bz(-t / 2 * 0.2, d.length + t / 2 * 0.2, -t / 2, t / 2, z - 0.05, z + h, 0.1), TR(a.x, a.y, 0, ang))
    c = (a + b) / 2; coll_box(c.x, c.y, z + h / 2, d.length, t, h, ang)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ================= gazon op decorpeil, met gat voor de vijver (20 x 2.5, hoeken r 0.6) =================
    lawn_front = [(x, y + 0.7) for x, y in FENCE]
    put("gazon", "gras", plaat(lawn_front[::-1] + [(-12.0, -1.25), (12.0, -1.25)][::-1] if False else
                               [(-12.0, -1.25), (12.0, -1.25)] + [p for p in lawn_front[::-1]], Z0 - 0.1, Z0))
    put("gazon", "gras", plaat([(-12.0, 1.25), (12.0, 1.25), (12.0, 13.0), (-12.0, 13.0)], Z0 - 0.1, Z0))
    put("gazon", "gras", plaat([(-12.0, -1.25), (-10.0, -1.25), (-10.0, 1.25), (-12.0, 1.25)], Z0 - 0.1, Z0))
    put("gazon", "gras", plaat([(10.0, -1.25), (12.0, -1.25), (12.0, 1.25), (10.0, 1.25)], Z0 - 0.1, Z0))
    r_ = 0.6
    for (cx_, cy_, sx, sy) in ((10 - r_, -1.25 + r_, 1, -1), (10 - r_, 1.25 - r_, 1, 1), (-10 + r_, 1.25 - r_, -1, 1), (-10 + r_, -1.25 + r_, -1, -1)):
        corner = (cx_ + sx * r_, cy_ + sy * r_)
        a0_, a1_ = math.atan2(sy, 0), math.atan2(0, sx)
        if a1_ - a0_ > math.pi: a1_ -= math.tau
        if a1_ - a0_ < -math.pi: a1_ += math.tau
        arcp = [(cx_ + r_ * math.cos(a0_ + (a1_ - a0_) * i / 6), cy_ + r_ * math.sin(a0_ + (a1_ - a0_) * i / 6)) for i in range(7)]
        poly = [corner] + arcp
        bm = plaat(poly, Z0 - 0.1, Z0); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("gazon", "gras", bm)
    for (x0, x1, y0, y1) in ((-12, 12, 1.25, 13.0), (-12, -10, -1.25, 1.25), (10, 12, -1.25, 1.25)):
        coll_box((x0 + x1) / 2, (y0 + y1) / 2, Z0 - 0.15, x1 - x0, y1 - y0, 0.3)
    # glooiing van het gazon naar het pad, achter het hekwerk
    for (a, b) in zip(FENCE, FENCE[1:]):
        bm = bmesh.new()
        v = [bm.verts.new((a[0], a[1], 0.0)), bm.verts.new((b[0], b[1], 0.0)), bm.verts.new((b[0], b[1] + 0.7, Z0)), bm.verts.new((a[0], a[1] + 0.7, Z0)),
             bm.verts.new((a[0], a[1] + 0.7, -0.1)), bm.verts.new((b[0], b[1] + 0.7, -0.1))]
        bm.faces.new((v[0], v[1], v[2], v[3])); bm.faces.new((v[0], v[3], v[4])); bm.faces.new((v[1], v[5], v[2])); bm.faces.new((v[0], v[4], v[5], v[1]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("gazon", "gras", bm)
    coll_box(0, -2.2, Z0 / 2, 4.6, 1.4, Z0, 0); coll_box(-7.6, -3.6, Z0 / 2, 9.0, 1.2, Z0, 0); coll_box(7.6, -3.6, Z0 / 2, 9.0, 1.2, Z0, 0)
    # ================= bestrating waar de figuren rijden (licht, DNKvdK-bouw) =================
    put("rijvloer", "tegels", plaat([(-7.0, 5.3), (7.2, 5.3), (7.2, 8.4), (6.6, 9.0), (2.6, 9.3), (-2.6, 9.3), (-6.6, 9.0), (-7.0, 8.4)], Z0 - 0.05, Z0 + 0.012))
    # ================= hagen =================
    haag((-5.4, 4.95), (5.6, 4.95), 1.15, 0.65)                                     # voor de muur (Keizer_vooraanzicht)
    haag((-8.6, 12.4), (8.8, 12.4), 3.0, 0.9)                                       # achter: beplanting in bakken 3000+P
    haag((-16.8, 3.9), (-7.8, 3.9), 1.8); haag((10.6, 3.9), (20.0, 3.9), 1.8)       # zijhagen tbv wegnemen zicht (decorpeil)
    haag((-17.7, -4.75), (-6.0, -4.75), 1.8, z=0.0); haag((6.0, -4.75), (17.5, -4.75), 1.8, z=0.0)   # langs het pad (OSM 8780/8781)
    haag((-8.65, -10.3), (7.34, -10.3), 1.1, 0.6, z=0.0)                            # achter de bankjes (OSM 8787)
    for (x, y, s) in ((4.6, 4.2, 0.55), (5.2, 4.55, 0.45), (8.9, 2.4, 0.5), (-4.7, 4.3, 0.5), (-4.1, 4.6, 0.42), (9.4, 4.4, 0.55)):   # bolstruiken
        put("hagen", "haag", ell((x, y, Z0 + s * 0.9), (s, s, s * 0.95), 14, 9))
    # ================= Sprookjesbos-hekwerk (laag zwart smeedijzer 0.6 m, krullen aan de uiteinden; aanzicht1) =================
    for (a, b) in zip(FENCE, FENCE[1:]):
        M, L, ang = (Matrix.Translation((a[0], a[1], 0)) @ Matrix.Rotation(math.atan2(b[1] - a[1], b[0] - a[0]), 4, "Z"),
                     math.hypot(b[0] - a[0], b[1] - a[1]), math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
        put("hek", "ijzer", btube([(0, 0, 0.62), (L, 0, 0.62)], 0.018, 6), M)
        put("hek", "ijzer", btube([(0, 0, 0.12), (L, 0, 0.12)], 0.012, 5), M)
        k = 0.0
        while k <= L + 1e-3:
            put("hek", "ijzer", btube([(k, 0, 0.0), (k, 0, 0.66)], 0.016, 6), M)
            put("hek", "goud", ell((k, 0, 0.68), (0.025, 0.025, 0.025), 8, 6), M)
            k += 1.2
        coll_box((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0.5, L, 0.12, 1.0, ang)
    for (e, d) in ((FENCE[0], 1), (FENCE[-1], -1)):
        pts = [(e[0] + d * (0.0 + 0.14 * math.sin(t)), e[1], 0.48 + 0.14 * math.cos(t)) for t in [i * 0.4 for i in range(16)]]
        put("hek", "ijzer", btube(pts, 0.016, 6))
    # ================= kijkplein (klinkers) en bankjes =================
    plein = [(-16.0, -10.0), (16.0, -10.0)] + [(x, y) for x, y in FENCE[::-1]] if False else None
    poly = [(-16.0, -10.0), (16.0, -10.0), (16.0, -4.1), (12.0, -4.1)] + [p for p in FENCE[::-1][1:-1]] + [(-12.0, -4.1), (-16.0, -4.1)]
    put("plein", "klinker", plaat(poly, -0.08, 0.04))
    coll_box(0, -7.05, -0.1, 32.0, 5.9, 0.28, 0)
    for x in (-4.5, -1.5, 1.5, 4.5):                                                # groene Efteling-bankjes, rug naar de haag
        M = TR(x, -9.65, 0)
        for sx in (-0.75, 0.75):
            put("bankjes", "ijzer", bz(sx - 0.03, sx + 0.03, -0.25, 0.25, 0.0, 0.44), M)
            put("bankjes", "ijzer", bz(sx - 0.03, sx + 0.03, 0.2, 0.26, 0.44, 0.9), M)
        for i in range(4): put("bankjes", "hout", bz(-0.9, 0.9, -0.24 + i * 0.12, -0.15 + i * 0.12, 0.42, 0.46, 0.005), M)
        for i in range(3): put("bankjes", "hout", bz(-0.9, 0.9, 0.24, 0.27, 0.55 + i * 0.12, 0.64 + i * 0.12, 0.005), M)
        coll_box(x, -9.65, 0.45, 1.9, 0.6, 0.9, 0)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"KO_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_}, open(os.path.join(out, "omgeving_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
