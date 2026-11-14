"""03_omgeving Doornroosje: trappen van natuursteen (OSM steps 763240412 west, 55340094 oost) met lage stucmuren, terraspad om het kasteel
(763240411), poortgebouwen 414 en 415 (rondboog, zadeldak; Doornroosje_2026_Poortje, Poortjedoornroosje), rotswand van gestapelde blokken
aan de vijverkant onder de torens (Doornroosje-2024-15). Heuvel en vijver: terrein in Studio (roblox/terrein_doornroosje.luau).
Modelframe = OSM-assen (x oost, y noord), oorsprong = zwaartepunt 55423166, z = 0 voet van de heuvel. Gebruik: -- --master DR_omgeving_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.86, 0.84, 0.78, 1), 0.9), "pannen": ((0.5, 0.28, 0.2, 1), 0.85), "natuursteen": ((0.6, 0.58, 0.54, 1), 0.9),
        "rots": ((0.55, 0.55, 0.52, 1), 0.95), "hout": ((0.3, 0.32, 0.3, 1), 0.8), "binnen": ((0.12, 0.1, 0.08, 1), 0.9), "ijzer": ((0.06, 0.06, 0.06, 1), 0.5)}
Z0 = 4.5
OSM = json.load(open(os.path.join(ROOT, "ref", "osm_lokaal.json")))
def way(i): return next(w for w in OSM["ways"] if w["id"] == i)["pts"]


def resample(pts, step):
    out = [pts[0]]; acc = 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay); t = step - acc
        while t <= L: out.append((ax + (bx - ax) * t / L, ay + (by - ay) * t / L)); t += step
        acc = L - (t - step)
    if math.hypot(out[-1][0] - pts[-1][0], out[-1][1] - pts[-1][1]) > step * 0.3: out.append(pts[-1])
    return out


def trap(pts, z_a, z_b, breed=2.0, part="trap"):
    """trap langs een polylijn: treden van ~0.34 m diep, hoogte lineair van z_a naar z_b, muurtjes aan weerszijden"""
    P = resample(pts, 0.34); n = len(P) - 1; R = random.Random(len(pts))
    lz = []
    for i in range(n):
        (ax, ay), (bx, by) = P[i], P[i + 1]
        z = z_a + (z_b - z_a) * (i + 0.5) / n
        dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1e-6; ux, uy = dx / L, dy / L; nx, ny = -uy, ux
        cx, cy = (ax + bx) / 2, (ay + by) / 2
        M = Matrix.Translation((cx, cy, 0)) @ Matrix.Rotation(math.atan2(uy, ux), 4, "Z")
        put(part, "natuursteen", bz(-L / 2 - 0.02, L / 2 + 0.02, -breed / 2, breed / 2, min(z_a, z_b) - 0.4, z + R.uniform(-0.01, 0.01), 0.02), M)
        for s in (-1, 1):                                                                       # lage muurtjes (Doornroosje_2026_Trap_Omhoog)
            put(part, "stuc", bz(-L / 2 - 0.03, L / 2 + 0.03, s * breed / 2 - (0.0 if s > 0 else 0.35), s * breed / 2 + (0.35 if s > 0 else 0.0), min(z_a, z_b) - 0.4, z + 0.65, 0.04), M)
        lz.append((cx, cy, z, math.atan2(uy, ux), L))
    for cx, cy, z, a, L in lz[::3]:                                                             # botsing: per 3 treden een schuin blok
        coll_box(cx, cy, z - 0.2, L * 3.2, breed, 0.4, math.degrees(a))
    return lz


def poortgebouw(poly, part, hoog=3.2, nok=1.6):
    """poortgebouw: stuc doos op de OSM-omtrek met rondboogdoorgang langs de lange as, zadeldak van pannen"""
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    c = Vector((sum(xs) / len(xs), sum(ys) / len(ys)))
    a = Vector(poly[1]) - Vector(poly[0]); b = Vector(poly[2]) - Vector(poly[1])
    if a.length < b.length: a, b = b, a
    ang = math.atan2(a.y, a.x); L, W = a.length, b.length
    M = Matrix.Translation((c.x, c.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
    z0 = poort_z(c.x, c.y)
    put(part, "stuc", bz(-L / 2, L / 2, -W / 2, W / 2, z0 - 0.5, z0 + hoog), M)
    for s in (-1, 1):                                                                           # doorgang dwars door het gebouw (donker), boog aan beide kanten
        put(part, "binnen", boutline(arch_pts(0, z0, min(1.5, W * 0.6), 2.3, 10), s * (W / 2 + 0.005) - (0.06 if s > 0 else 0), 0.06), M @ Matrix.Rotation(math.pi / 2, 4, "Z") if False else M)
    Mr = M @ Matrix.Rotation(math.pi / 2, 4, "Z")
    for s in (-1, 1):
        put(part, "binnen", boutline(arch_pts(0, z0, min(1.6, W * 0.6), 2.4, 10), s * L / 2 - 0.05, 0.1), Mr)
        put(part, "stuc", band(arch_pts(0, z0, min(1.6, W * 0.6), 2.4, 10), 0.12, s * L / 2 - (0.12 if s < 0 else -0.02), 0.14), Mr)
    tiled_roof(part, (-L / 2 - 0.3, L / 2 + 0.3, -W / 2 - 0.35, W / 2 + 0.35), (-L / 2 - 0.3, L / 2 + 0.3, 0, 0), z0 + hoog - 0.05, z0 + hoog + nok, hips=False)
    for s in (-1, 1):                                                                           # gevels onder het zadeldak
        put(part, "stuc", prism_x([(-W / 2, z0 + hoog), (W / 2, z0 + hoog), (0, z0 + hoog + nok - 0.1)], s * L / 2 - 0.3, s * L / 2), M)
    bm_ = bmesh.new(); bmesh.ops.transform  # (placeholder for clarity)
    coll_box(c.x, c.y, z0 + hoog / 2, L, W, hoog, math.degrees(ang))


def poort_z(x, y): return 0.0 if y > 10 or x < -15 else Z0 * 0.15


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, rr) in MATS.items(): material("MAT_" + n, c, rr)
    put("anker", "ijzer", bz(-0.01, 0.01, -0.01, 0.01, 0, 0.02))
    # trappen: west van onder (poortgebouw 414) naar het terras, oost van het terras naar beneden (zuidoost)
    west = way("763240412"); oost = way("55340094")
    trap(west, 0.4, Z0, 2.0, "trap_w")
    trap(oost, Z0, 0.0, 2.2, "trap_o")
    # terraspad op kasteelhoogte (natuursteenplaveisel) om de westkant van het kasteel
    for (ax, ay), (bx, by) in zip(way("763240411"), way("763240411")[1:]):
        L = math.hypot(bx - ax, by - ay); M = Matrix.Translation(((ax + bx) / 2, (ay + by) / 2, 0)) @ Matrix.Rotation(math.atan2(by - ay, bx - ax), 4, "Z")
        put("terras", "natuursteen", bz(-L / 2 - 0.4, L / 2 + 0.4, -1.0, 1.0, Z0 - 0.5, Z0 + 0.04, 0.02), M)
        coll_box((ax + bx) / 2, (ay + by) / 2, Z0 - 0.2, L + 0.8, 2.0, 0.5, math.degrees(math.atan2(by - ay, bx - ax)))
    # poortgebouwen
    poortgebouw(way("763240414")[:-1], "poort414")
    poortgebouw(way("763240415")[:-1], "poort415", hoog=3.0, nok=1.4)
    # rotswand aan de vijverkant onder de torens: gestapelde kalksteenblokken (front = noordrand)
    ROTS = [(-10.6, 6.6), (-8.6, 3.6), (-7.6, 1.0), (-6.2, 1.2), (-4.6, 4.2), (-2.0, 4.9), (1.6, 4.9), (3.8, 4.5), (6.0, 4.6), (7.6, 6.2),
            (6.0, 8.6), (2.0, 8.9), (-2.5, 9.3), (-6.0, 8.8), (-9.0, 8.2)]
    blok, kern = rotsblokken(ROTS, Z0 - 0.3, front_edges=[9, 10, 11, 12, 13, 14], seed=1952, slope=1.5, maat=0.9)
    put("rots", "rots", blok); put("rots", "rots", kern)
    coll_box(-1.5, 6.5, Z0 / 2, 14, 3.5, Z0, 0)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"DO_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": []}, open(os.path.join(out, "omgeving_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(os.path.abspath(m))
