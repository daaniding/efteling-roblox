"""03b_omgeving Klein Duimpje: rotseiland waar de reus op ligt, smalle gracht eromheen (OSM 55424075 tuin + 767716994 water),
losse kalksteenbrokken als rotsbed langs het plein, dode boomstronk achter het hoofd, praatstronk met koperen hoorn en perkament,
bordje op een standaard (Boekloc/Kleinduimpje-mei09/Sprookjereus/Overzicht-kleinduimpje-mei09).
Modelframe: oorsprong = OSM-punt Klein Duimpje, voorkant (open rotsrand naar het plein, ZO) = -Y, x = lichaamsas (hoofd +X, NO).
Gebruik: Blender -b -P 03b_omgeving.py -- --master KD_omgeving_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"natuursteen": ((0.62, 0.6, 0.55, 1), 0.85), "kalksteen": ((0.72, 0.68, 0.6, 1), 0.9), "schors": ((0.36, 0.3, 0.24, 1), 0.9),
        "hout": ((0.28, 0.2, 0.14, 1), 0.8), "koper": ((0.72, 0.5, 0.25, 1), 0.35), "papier": ((0.9, 0.85, 0.7, 1), 0.7),
        "water": ((0.12, 0.16, 0.1, 1), 0.1), "modder": ((0.16, 0.13, 0.1, 1), 0.95), "ijzer": ((0.08, 0.08, 0.08, 1), 0.5),
        "bordgroen": ((0.12, 0.3, 0.2, 1), 0.6), "binnen": ((0.05, 0.03, 0.02, 1), 0.9)}
N = Vector((0.43, -0.90)).normalized()                    # voorkant (OSM oost/noord)
XA = Vector((-N.y, N.x))
OSM = json.load(open(os.path.join(ROOT, "ref", "osm_lokaal.json")))


def m(p):  # OSM (oost, noord) -> model (x, y)
    p = Vector(p); return (round(p.dot(XA), 3), round(-p.dot(N), 3))


def way(i): return next(w for w in OSM["ways"] if w["id"] == i)["pts"]


EILAND = [m(p) for p in way("55424075")[:-1]]
WATER = [m(p) for p in way("767716994")[:-1]]
BUITEN = WATER[:6]                                         # buitenrand van de gracht (de rest van de ring is de eilandrand)


def steen(c, s, r, seed, mat="kalksteen", plat=0.7):
    """hoekige kalksteenbrok: ellipsoide met ruis, platte onderkant"""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1 if max(s) < 0.22 else 2, radius=1.0)
    for v in bm.verts:
        d = v.co.normalized(); k = 1 + 0.28 * noise.noise(d * 1.7 + Vector((seed, seed * 0.3, 0))) + 0.12 * noise.noise(d * 4.1 + Vector((0, seed, 1)))
        v.co = Vector((d.x * s[0], d.y * s[1], max(d.z * s[2] * plat, -0.1 * s[2]))) * k
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(r.uniform(0, math.tau), 3, "Z") @ Matrix.Rotation(r.uniform(-0.25, 0.25), 3, "X"))
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    put("rots", mat, bm)


def stronk(x, y, h, rad, seed, holte=False, part="stronk"):
    """dode boomstam met schorsgroeven, schuin afgebroken top (en een holte voor de hoorn)"""
    r = random.Random(seed); bm = bmesh.new(); ring = 20; rings = []
    nz = 14
    for k in range(nz + 1):
        z = h * k / nz; rr = []
        for j in range(ring):
            a = j / ring * math.tau
            g = 1 + 0.07 * math.sin(a * 9 + seed) + 0.05 * noise.noise(Vector((a * 2, z * 3, seed)))
            voet = 1 + 0.45 * max(0, 1 - z / (0.35 * h)) ** 2 * (1 + 0.4 * math.sin(a * 4 + seed))   # wortelaanzet
            top = h - 0.35 * h * (0.5 + 0.5 * math.cos(a)) * 0.6 if k == nz else z            # schuin gebroken
            rr.append(bm.verts.new((x + rad * g * voet * math.cos(a), y + rad * g * voet * math.sin(a), top if k == nz else z)))
        rings.append(rr)
    for A, B in zip(rings, rings[1:]):
        for j in range(ring): bm.faces.new((A[j], A[(j + 1) % ring], B[(j + 1) % ring], B[j]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    put(part, "schors", bm)
    coll_box(x, y, h / 2, rad * 2.2, rad * 2.2, h)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, rr) in MATS.items(): material("MAT_" + n, c, rr)
    r = random.Random(1998)
    xs = [p[0] for p in WATER]; ys = [p[1] for p in WATER]
    # ---- eiland: gestapelde rotsbrokken, hoger in het midden (bed onder de reus), lager naar de randen ----
    put("anker", "ijzer", bz(-0.01, 0.01, -0.01, 0.01, 0, 0.02))
    cx = sum(p[0] for p in EILAND) / len(EILAND); cy = sum(p[1] for p in EILAND) / len(EILAND)
    for k in range(1400):                                                    # rotsbed van kleine kalksteenbrokken (vuist tot hoofd)
        x, y = r.uniform(min(xs), max(xs)), r.uniform(min(ys) - 2.5, max(ys))
        op = inside(x, y, EILAND); voor = y < cy and not inside(x, y, WATER) and y > min(ys) - 2.2 and min(xs) + 0.5 < x < max(xs) - 0.5
        if not (op or voor): continue
        d = math.hypot((x - cx) / 3.2, (y - cy) / 2.6)
        s = r.uniform(0.09, 0.2) if r.random() < 0.8 else r.uniform(0.2, 0.32)
        z = (max(0.0, 0.32 * (1 - d * d)) if op else 0.0) + s * 0.2
        steen((x, y, z), (s * r.uniform(1.0, 1.5), s, s * r.uniform(0.7, 1.0)), r, k)
    for k, (x, y, s) in enumerate([(3.4, 1.0, 0.8), (2.6, -0.6, 0.75), (1.4, 1.5, 0.85), (0.3, 1.2, 0.8), (-0.8, 1.6, 0.7), (-2.4, 0.9, 0.6), (1.6, -1.4, 0.55), (-1.4, -2.2, 0.6), (4.0, 0.0, 0.6)]):
        steen((x, y, s * 0.35), (s * 1.3, s, s * 0.8), r, 100 + k, "natuursteen", 0.8)        # grote zwerfkeien (grijs) onder/achter de reus
    coll_box(cx, cy, 0.2, 6.5, 5.0, 0.4, 0)
    # ---- gracht: modderige bodem + wateroppervlak in de ring, oeverstenen langs de buitenrand ----
    def vlak(poly, z, mat, part):
        bm = bmesh.new(); vv = [bm.verts.new((x, y, z)) for x, y in poly]; bm.faces.new(vv)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="EAR_CLIP"); put(part, mat, bm)
    vlak(WATER, -0.32, "water", "water"); vlak(WATER, -0.75, "modder", "water")
    for (ax, ay), (bx, by) in zip(BUITEN, BUITEN[1:]):
        L = math.hypot(bx - ax, by - ay); k = 0.0
        while k < L:
            t = k / L; s = r.uniform(0.2, 0.36)
            steen((ax + (bx - ax) * t, ay + (by - ay) * t, -0.1), (s * 1.3, s, s * 0.8), r, int(k * 31 + ax * 7))
            k += r.uniform(0.35, 0.6)
    # ---- dode boomstronk achter het hoofd (Kduimpje_reus_zijaanzicht, Kleinduimpje-reus) ----
    stronk(4.0, 1.1, 2.6, 0.34, 7)
    # ---- praatstronk met koperen hoorn en perkament (Kleinduimpje-mei09, Sprookjereus) op het plein, links voor ----
    PX, PY = -3.2, -5.2
    stronk(PX, PY, 1.35, 0.38, 3, part="praatstronk")
    M = Matrix.Translation((PX, PY - 0.36, 0.6)) @ Matrix.Rotation(math.radians(90), 4, "X")
    put("praatstronk", "koper", blathe([(0.17, 0.0), (0.2, 0.0), (0.24, 0.12), (0.2, 0.14), (0.16, 0.06)], 20), M)      # hoornmond
    put("praatstronk", "binnen", blathe([(0.0, 0.02), (0.16, 0.02), (0.15, 0.05), (0.0, 0.05)], 16), M)
    Mp = Matrix.Translation((PX, PY - 0.3, 1.05)) @ Matrix.Rotation(math.radians(-12), 4, "X")
    put("praatstronk", "papier", bz(-0.42, 0.42, -0.1, -0.06, -0.16, 0.16, 0.01), Mp)                                       # perkament
    for sx in (-1, 1): put("praatstronk", "papier", btube([(sx * 0.42, -0.08, -0.17), (sx * 0.42, -0.08, 0.17)], 0.035, 8), Mp)
    # ---- bordje op een standaard voor de rotsrand (Boekloc) ----
    MB = Matrix.Translation((-5.0, -3.4, 0)) @ Matrix.Rotation(math.radians(8), 4, "Z")
    put("bord", "ijzer", btube([(0, 0, 0), (0, 0, 0.8)], 0.03, 8), MB)
    put("bord", "bordgroen", bz(-0.32, 0.32, -0.04, 0.0, 0.75, 1.05, 0.01), MB @ Matrix.Rotation(math.radians(-35), 4, "X"))
    put("bord", "papier", bz(-0.28, 0.28, -0.05, -0.04, 0.78, 1.02, 0.005), MB @ Matrix.Rotation(math.radians(-35), 4, "X"))
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"KD_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": []}, open(os.path.join(out, "omgeving_extra.json"), "w"))
    json.dump({"eiland": EILAND, "water": WATER}, open(os.path.join(ROOT, "ref", "osm_model.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(os.path.abspath(mm))
