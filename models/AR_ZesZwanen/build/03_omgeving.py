"""03_omgeving De Zes Zwanen: vijvers (OSM 961616757/758/760) met troebel water op een donkere bodem en natuurstenen oever,
rotseiland (961616756) en westoever (961616759) met lantaarns, maaiveld + bruin betonpad (961616754 + voetpaden), kade,
bordeauxrood controlehokje op ijsselsteentjes (961616755), Pieck-blauwe hekken (1255787244 + vijverrand), houten galgenlantaarn.
Modelframe als 03_kasteel. Gebruik: Blender -b -P 03_omgeving.py -- --master ZZ_omgeving_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "zz_helpers.py")).read())
RNG = random.Random(75000)
MATS = {"water": ((0.12, 0.18, 0.12, 1), 0.05), "bodem": ((0.1, 0.09, 0.07, 1), 0.9), "rots": ((0.5, 0.49, 0.45, 1), 0.95),
        "grond": ((0.22, 0.2, 0.13, 1), 0.95), "beton": ((0.42, 0.33, 0.26, 1), 0.9), "steentjes": ((0.72, 0.6, 0.36, 1), 0.9),
        "bordeaux": ((0.4, 0.06, 0.08, 1), 0.6), "creme": ((0.88, 0.82, 0.68, 1), 0.7), "dak": ((0.12, 0.12, 0.13, 1), 0.8),
        "hekblauw": ((0.28, 0.4, 0.42, 1), 0.5), "goud": ((0.8, 0.6, 0.2, 1), 0.3), "ijzer": ((0.05, 0.05, 0.05, 1), 0.45),
        "glaslamp": ((0.95, 0.8, 0.5, 1), 0.2), "hout": ((0.36, 0.22, 0.13, 1), 0.7), "venster": ((0.05, 0.05, 0.05, 1), 0.3), "oeversteen": ((0.6, 0.52, 0.42, 1), 0.9), "kern": ((0.08, 0.08, 0.08, 1), 0.95)}
O = {e["id"]: e for e in json.load(open(os.path.join(ROOT, "ref", "osm_model.json")))}
def P(i): pts = [tuple(p) for p in O[i]["pts"]]; return pts[:-1] if pts[0] == pts[-1] else pts
VIJVERS = [P("961616757"), P("961616758"), P("961616760")]
KASTEEL = P("961616753")
PAD = P("961616754")
VOETPADEN = [P(i) for i in ("1169016139", "1255787237", "1169016140", "1255787243", "729126648")]


def segdist(px, py, pts):
    best = 1e9
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-9
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2)); best = min(best, math.hypot(px - ax - t * dx, py - ay - t * dy))
    return best


def plaat(poly, z0, z1):
    """verticaal geextrudeerde veelhoek (ear-clip voor concave vormen)"""
    bm = bmesh.new(); b = [bm.verts.new((x, y, z0)) for x, y in poly]; t = [bm.verts.new((x, y, z1)) for x, y in poly]
    n = len(poly); bm.faces.new(b[::-1]); bm.faces.new(t)
    for i in range(n): bm.faces.new((b[i], b[(i + 1) % n], t[(i + 1) % n], t[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], ngon_method="EAR_CLIP"); return bm


def hek(pts, h=1.0, part="hek", gat=None):
    """Pieck-blauw sierhek: palen 1.6 m met gouden bol, boven- en onderregel, spijlen 0.12 m met speerpuntjes"""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay); ang = math.degrees(math.atan2(by - ay, bx - ax))
        M = Matrix.Translation((ax, ay, 0)) @ Matrix.Rotation(math.radians(ang), 4, "Z")
        put(part, "hekblauw", bz(0, L, -0.02, 0.02, h - 0.06, h - 0.02), M); put(part, "hekblauw", bz(0, L, -0.02, 0.02, 0.12, 0.16), M)
        put(part, "hekblauw", bz(0, L, -0.015, 0.015, h - 0.32, h - 0.29), M)
        for k in range(int(L / 0.12)):
            x = 0.06 + k * 0.12; put(part, "hekblauw", bz(x - 0.009, x + 0.009, -0.009, 0.009, 0.12, h + 0.05), M)
            put(part, "hekblauw", blathe([(0, 0), (0.018, 0), (0.0, 0.06)], 4), M @ Matrix.Translation((x, 0, h + 0.03)))
            if k % 2 == 0: put(part, "hekblauw", ell((x + 0.06, 0, h - 0.18), (0.035, 0.008, 0.06), 8, 4), M)            # krulletjes
        for k in range(int(L / 1.6) + 1):
            x = min(L, k * 1.6)
            put(part, "hekblauw", bz(x - 0.04, x + 0.04, -0.04, 0.04, 0.0, h + 0.05), M)
            put(part, "goud", ell((x, 0, h + 0.13), (0.055, 0.055, 0.055), 10, 6), M)
        coll_box((ax + bx) / 2, (ay + by) / 2, h / 2, L, 0.12, h, ang)


def lantaarn_paal(x, y, z0, h=3.0, kleur="ijzer"):
    """klassieke straatlantaarn op een paal (eiland: zwart, kade: Pieck-blauw) met gouden accenten"""
    put("lampen", kleur, blathe([(0, 0), (0.12, 0), (0.12, 0.25), (0.06, 0.35), (0.05, h - 0.2), (0.08, h - 0.1), (0, h - 0.1)], 10), TR(x, y, z0))
    put("lampen", kleur, blathe([(0, h - 0.12), (0.15, h - 0.08), (0.17, h), (0, h)], 6), TR(x, y, z0, 30))
    put("lampen", "glaslamp", blathe([(0, h), (0.13, h), (0.17, h + 0.42), (0, h + 0.42)], 6), TR(x, y, z0, 30))
    put("lampen", kleur, blathe([(0, h + 0.4), (0.24, h + 0.42), (0.2, h + 0.5), (0.05, h + 0.66), (0, h + 0.7)], 6), TR(x, y, z0, 30))
    put("lampen", "goud", ell((x, y, z0 + h + 0.74), (0.04, 0.04, 0.05), 8, 6))
    LAMPS_.append([round(x, 2), round(y, 2), round(z0 + h + 0.2, 2)])
    coll_box(x, y, z0 + h / 2, 0.25, 0.25, h)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ================= maaiveld (gras/bosgrond) en pad als raster: alles wat geen water of kasteel is =================
    C = 0.5; X0, X1, Y0, Y1 = -13.0, 22.0, -28.0, 9.0
    gr = bmesh.new(); pd = bmesh.new()
    nx, ny = int((X1 - X0) / C), int((Y1 - Y0) / C)
    for i in range(nx):
        for j in range(ny):
            cx, cy = X0 + (i + 0.5) * C, Y0 + (j + 0.5) * C
            if any(inside(cx, cy, v) for v in VIJVERS) or inside(cx, cy, KASTEEL): continue
            pad = inside(cx, cy, PAD) or any(segdist(cx, cy, f) < 0.95 for f in VOETPADEN)
            oever = any(segdist(cx, cy, v + [v[0]]) < 1.45 for v in VIJVERS)                              # oevergrond dekt het uitgegraven terrein af
            if pad or not oever: continue                                                                 # pad = eigen plaat, rest = terreingras
            bm_, z = gr, 0.025
            q = [bm_.verts.new((X0 + i * C, Y0 + j * C, z)), bm_.verts.new((X0 + (i + 1) * C, Y0 + j * C, z)),
                 bm_.verts.new((X0 + (i + 1) * C, Y0 + (j + 1) * C, z)), bm_.verts.new((X0 + i * C, Y0 + (j + 1) * C, z))]
            bm_.faces.new(q)
    for bm_ in (gr, pd):
        bmesh.ops.remove_doubles(bm_, verts=bm_.verts, dist=1e-4)
        r_ = bmesh.ops.extrude_face_region(bm_, geom=bm_.faces[:]); vv = [g for g in r_["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm_, vec=(0, 0, -0.08), verts=vv); bmesh.ops.recalc_face_normals(bm_, faces=bm_.faces)
    PARTS[("grond", "grond")] = gr; pd.free()
    put("pad", "beton", plaat(PAD, -0.05, 0.07))                                                          # bruin beton (OSM-vlak, gladde rand)
    for f in VOETPADEN:                                                                                    # voetpaden: strook 1.9 m + ronde knikken
        for (ax, ay), (bx, by) in zip(f, f[1:]):
            L = math.hypot(bx - ax, by - ay); ang = math.degrees(math.atan2(by - ay, bx - ax))
            put("pad", "beton", bz(0, L, -0.95, 0.95, -0.05, 0.065), Matrix.Translation((ax, ay, 0)) @ Matrix.Rotation(math.radians(ang), 4, "Z"))
        for (x, y) in f: put("pad", "beton", blathe([(0, -0.05), (0.95, -0.05), (0.95, 0.065), (0, 0.065)], 16), TR(x, y))
    # ================= vijvers: water (dikke plaat), modderbodem, oeverwand en losse Franse natuurstenen =================
    for v in VIJVERS:
        put("water", "water", plaat(v, WL - 0.12, WL))
        put("water", "bodem", plaat(v, WL - 1.0, WL - 0.9))
        n = len(v)
        for i in range(n):                                                                             # oeverwand van maaiveld tot de bodem
            (ax, ay), (bx, by) = v[i], v[(i + 1) % n]
            L = math.hypot(bx - ax, by - ay); ang = math.degrees(math.atan2(by - ay, bx - ax))
            put("water", "bodem", bz(0, L, -0.06, 0.06, WL - 1.0, 0.0), Matrix.Translation((ax, ay, 0)) @ Matrix.Rotation(math.radians(ang), 4, "Z"))
            k = 0.0
            while k < L:                                                                               # oeverstenen, half in het water
                t = k / L; x, y = ax + (bx - ax) * t, ay + (by - ay) * t
                if not (inside(x, y + 0.6, KASTEEL) or (y > -2.6 and -6.5 < x < 7.2 and v is VIJVERS[0])):
                    s = RNG.uniform(0.22, 0.45)
                    st = bbox(s * RNG.uniform(1.0, 1.6), s, s * RNG.uniform(0.5, 0.8), 0, 0, 0, s * 0.25)
                    bmesh.ops.rotate(st, verts=st.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(RNG.uniform(0, math.tau), 3, "Z"))
                    bmesh.ops.translate(st, vec=(x, y, WL + RNG.uniform(-0.05, 0.15)), verts=st.verts)
                    put("oever", "oeversteen" if RNG.random() < 0.55 else "rots", st)
                k += RNG.uniform(0.35, 0.6)
    # ================= rotseiland en westoever (gelaagde kalksteen, als het kasteel) =================
    for (pid, hm, sd) in (("961616756", 2.3, 11), ("961616759", 2.8, 12)):
        rk, kern = rotsblokken(P(pid), hm, seed=sd, slope=1.9, voet=0.6, maat=0.8)                 # gestapelde blokken als het kasteel
        put("rots", "rots", rk); put("rots", "kern", kern)
    lantaarn_paal(1.9, -5.7, 1.35, 2.6); lantaarn_paal(4.1, -6.3, 1.3, 2.6)                             # zwarte lantaarns op het eiland (foto)
    # ================= kade (instap) langs de zuidrand van de vijver =================
    KADE = [(-0.95, -13.14), (1.88, -12.9), (4.07, -13.27), (6.05, -12.52), (7.65, -11.13), (7.95, -11.5), (6.3, -12.95), (4.1, -13.75), (1.9, -13.4), (-0.95, -13.6)]
    put("kade", "beton", plaat(KADE, -0.3, 0.06))
    for (ax, ay), (bx, by) in zip(KADE[:5], KADE[1:5]):                                                 # natuurstenen kaderand
        L = math.hypot(bx - ax, by - ay); ang = math.degrees(math.atan2(by - ay, bx - ax))
        put("kade", "oeversteen", bz(0, L, -0.12, 0.12, -0.25, 0.1, 0.02), Matrix.Translation((ax, ay, 0)) @ Matrix.Rotation(math.radians(ang), 4, "Z"))
    lantaarn_paal(-1.35, -12.85, 0.06, 3.0, "hekblauw"); lantaarn_paal(2.2, -12.7, 0.06, 3.0, "hekblauw")   # bij het hokje (foto: niet in de zichtlijn)
    # ================= controlehokje (bordeauxrood op ijsselsteentjes, crème sierlijsten, geschulpte daklijst) =================
    H = P("961616755")
    hx, hy = sum(p[0] for p in H) / len(H), sum(p[1] for p in H) / len(H)
    ha = math.degrees(math.atan2(1.88 - -0.87, -12.9 - -12.52)) if False else math.degrees(math.atan2(-12.9 + 12.52, 1.88 + 0.87))
    MH = Matrix.Translation((hx, hy, 0)) @ Matrix.Rotation(math.radians(ha), 4, "Z")
    W2, D2 = 1.35, 1.0
    put("hokje", "steentjes", bz(-W2, W2, -D2, D2, 0.0, 0.55, 0.01), MH)
    put("hokje", "bordeaux", bz(-W2 + 0.04, W2 - 0.04, -D2 + 0.04, D2 - 0.04, 0.55, 2.35), MH)
    for xa in (-W2 - 0.01, W2 - 0.09):                                                                 # crème hoekstijlen (niet de hele zijwand)
        for ya in (-D2 - 0.01, D2 - 0.09): put("hokje", "creme", bz(xa, xa + 0.1, ya, ya + 0.1, 0.55, 2.35), MH)
    put("hokje", "creme", bz(-W2 - 0.03, W2 + 0.03, -D2 - 0.03, D2 + 0.03, 0.55, 0.62), MH)
    put("hokje", "creme", bz(-W2 - 0.06, W2 + 0.06, -D2 - 0.06, D2 + 0.06, 2.3, 2.42), MH)
    for (x0, x1, y0) in ((-1.0, 0.0, -D2), (0.25, 1.05, -D2), (-0.8, 0.8, D2)):                     # ramen (kade- en padzijde)
        put("hokje", "venster", bz(x0, x1, y0 - 0.02, y0 + 0.02, 1.15, 2.0), MH)
        put("hokje", "creme", bz(x0 - 0.06, x1 + 0.06, y0 - 0.05, y0 + 0.05, 1.08, 1.15), MH); put("hokje", "creme", bz(x0 - 0.06, x1 + 0.06, y0 - 0.05, y0 + 0.05, 2.0, 2.07), MH)
        for xm in ((x0 + x1) / 2,): put("hokje", "creme", bz(xm - 0.02, xm + 0.02, y0 - 0.04, y0 + 0.04, 1.15, 2.0), MH)
    put("hokje", "hout", bz(-W2 - 0.03, -W2 + 0.02, -0.45, 0.45, 0.6, 2.25), MH)                       # deur zijkant
    rp = [(-D2 - 0.35, 2.42), (0.0, 3.05), (D2 + 0.35, 2.42), (D2 + 0.35, 2.32), (0.0, 2.92), (-D2 - 0.35, 2.32)]
    put("hokje", "dak", prism_x(rp, -W2 - 0.35, W2 + 0.35), MH)
    for sd in (-1, 1):                                                                                 # geschulpte crème daklijst
        for k in range(14):
            x = -W2 - 0.3 + k * (2 * W2 + 0.6) / 13
            put("hokje", "creme", ell((x, sd * (D2 + 0.36), 2.33), (0.1, 0.015, 0.09), 8, 4), MH)
    put("hokje", "creme", bz(-0.45, 0.45, -D2 - 0.06, -D2 - 0.03, 2.45, 2.85), MH) if False else None
    put("hokje", "creme", bz(-0.42, 0.42, -D2 - 0.07, -D2 - 0.04, 0.75, 1.0), MH)                      # bordje 'Koninklijke Garde'
    coll_box(hx, hy, 1.2, 2 * W2, 2 * D2, 2.4, ha)
    # ================= hekken: wachtrij (OSM) en langs de vijverrand bij de kade =================
    hek(P("1255787244")[:6]); hek(P("1255787244")[6:])
    hek([(-7.84, -16.83), (-6.61, -16.58), (-5.17, -15.7), (-3.85, -13.81), (-2.89, -13.55), (-0.95, -13.6)])
    # houten galgenlantaarn linksvoor (foto) en de OSM-lantaarn aan het begin van het pad
    for (gx, gy, ga) in ((-8.4, -15.2, 20), (-3.52, -23.88, -30)):
        M = Matrix.Translation((gx, gy, 0)) @ Matrix.Rotation(math.radians(ga), 4, "Z")
        put("lampen", "hout", bz(-0.1, 0.1, -0.1, 0.1, 0.0, 3.2, 0.01), M); put("lampen", "hout", bz(-0.08, 1.0, -0.07, 0.07, 3.0, 3.14, 0.01), M)
        put("lampen", "hout", btube([(0.0, 0, 2.5), (0.55, 0, 3.02)], 0.045, 6), M)
        put("lampen", "ijzer", btube([(0.85, 0, 3.0), (0.85, 0, 2.8)], 0.012, 5), M)
        put("lampen", "ijzer", blathe([(0, 0.0), (0.12, 0.02), (0.14, 0.05), (0.1, 0.05), (0.1, 0.38), (0.16, 0.42), (0.04, 0.55), (0, 0.56)], 4), M @ Matrix.Translation((0.85, 0, 2.22)))
        put("lampen", "glaslamp", blathe([(0, 0.05), (0.095, 0.05), (0.095, 0.37), (0, 0.37)], 4), M @ Matrix.Translation((0.85, 0, 2.22)))
        p_ = M @ Vector((0.85, 0, 2.45)); LAMPS_.append([round(p_.x, 2), round(p_.y, 2), round(p_.z, 2)])
        coll_box(gx, gy, 1.6, 0.25, 0.25, 3.2)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"ZO_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_}, open(os.path.join(out, "omgeving_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
