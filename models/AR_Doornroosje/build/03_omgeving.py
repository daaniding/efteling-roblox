"""03_omgeving Doornroosje: trappen van natuursteen (OSM steps 763240412 west, 55340094 oost) met lage stucmuren, terraspad om het kasteel
(763240411), poortgebouwen 414 en 415 (rondboog, zadeldak; Doornroosje_2026_Poortje, Poortjedoornroosje), rotswand van gestapelde blokken
aan de vijverkant onder de torens (Doornroosje-2024-15). Heuvel en vijver: terrein in Studio (roblox/terrein_doornroosje.luau).
Modelframe = OSM-assen (x oost, y noord), oorsprong = zwaartepunt 55423166, z = 0 voet van de heuvel. Gebruik: -- --master DR_omgeving_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.86, 0.84, 0.78, 1), 0.9), "pannen": ((0.5, 0.28, 0.2, 1), 0.85), "natuursteen": ((0.6, 0.58, 0.54, 1), 0.9),
        "rots": ((0.55, 0.55, 0.52, 1), 0.95), "kei": ((0.48, 0.48, 0.47, 1), 0.9), "muur": ((0.8, 0.77, 0.69, 1), 0.9), "dekst": ((0.72, 0.7, 0.64, 1), 0.9), "lamp": ((1.0, 0.8, 0.5, 1), 0.3), "wapenrood": ((0.55, 0.08, 0.06, 1), 0.5), "goud": ((0.8, 0.62, 0.22, 1), 0.3), "hout": ((0.3, 0.32, 0.3, 1), 0.8), "binnen": ((0.12, 0.1, 0.08, 1), 0.9), "ijzer": ((0.06, 0.06, 0.06, 1), 0.5)}
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


def trap(pts, z_a, z_b, breed=2.0, part="trap", lantaarns=True):
    """echt pad (Doornroosje_2026_Trap_*, Doornroosje_Trap_2022): doorlopend grijs keienpad met brede treden en lage optreden (~0.14 m),
    lage crème muurtjes (~0.75 m) die de helling glad volgen met een onregelmatige rij dekstenen, lantaarnpalen langs de route."""
    P = resample(pts, 0.2); R = random.Random(len(pts) * 7)
    S_ = [0.0]
    for (ax, ay), (bx, by) in zip(P, P[1:]): S_.append(S_[-1] + math.hypot(bx - ax, by - ay))
    Ltot = S_[-1]; rise = z_b - z_a; nstep = max(1, int(abs(rise) / 0.14)); tread = Ltot / nstep
    def zpad(s): return z_a + rise * min(nstep, math.floor(s / tread + 1e-6)) / nstep          # trapjes
    def zglad(s): return z_a + rise * s / Ltot                                                  # muurtop volgt glad
    def frame(i):
        j0, j1 = max(i - 1, 0), min(i + 1, len(P) - 1)
        dx, dy = P[j1][0] - P[j0][0], P[j1][1] - P[j0][1]; L = math.hypot(dx, dy) or 1e-6
        return dx / L, dy / L, -dy / L, dx / L
    # loopvlak: per segment een vierkant op traphoogte + optrede waar de hoogte springt
    bm = bmesh.new(); prev = None
    for i in range(len(P)):
        ux, uy, nx, ny = frame(i); x, y = P[i]; z = zpad(S_[i]) + R.uniform(-0.006, 0.006)
        w = breed / 2 + R.uniform(-0.03, 0.03)
        l = bm.verts.new((x - nx * w, y - ny * w, z)); r_ = bm.verts.new((x + nx * w, y + ny * w, z))
        if prev:
            pl, pr, pz = prev
            if abs(pz - z) > 0.02:                                                              # optrede
                l2 = bm.verts.new((l.co.x, l.co.y, pz)); r2 = bm.verts.new((r_.co.x, r_.co.y, pz))
                bm.faces.new((pl, pr, r2, l2)); bm.faces.new((l2, r2, r_, l))
            else: bm.faces.new((pl, pr, r_, l))
        prev = (l, r_, z)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.z < 0: f.normal_flip()
    so = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])                                   # dikte: plaat van 0.5 m
    bmesh.ops.translate(bm, vec=(0, 0, -0.5), verts=[v for v in so["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    put(part, "kei", bm)
    # muurtjes: buitenkant tot ver onder het maaiveld, bovenkant glad op +0.75, dekstenen onregelmatig
    for sgn in (-1, 1):
        wb = bmesh.new(); rings = []
        for i in range(0, len(P), 2):
            ux, uy, nx, ny = frame(i); x, y = P[i]; zt = zglad(S_[i]) + 0.72 + 0.04 * math.sin(i * 0.7)
            zi = min(zpad(S_[i]), zglad(S_[i])) - 0.6
            a_ = (x + sgn * nx * (breed / 2 - 0.02), y + sgn * ny * (breed / 2 - 0.02)); b_ = (x + sgn * nx * (breed / 2 + 0.38), y + sgn * ny * (breed / 2 + 0.38))
            rings.append([wb.verts.new((a_[0], a_[1], zi)), wb.verts.new((a_[0], a_[1], zt)), wb.verts.new((b_[0], b_[1], zt)), wb.verts.new((b_[0], b_[1], zi - 1.4))])
        for A, B in zip(rings, rings[1:]):
            for k in range(4): wb.faces.new((A[k], A[(k + 1) % 4], B[(k + 1) % 4], B[k]))
        wb.faces.new(rings[0][::-1]); wb.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(wb, faces=wb.faces); put(part, "muur", wb)
        s_ = R.uniform(0, 0.4)
        while s_ < Ltot - 0.3:                                                                   # dekstenen: brokken van 0.35-0.7 m, ongelijk hoog
            i = min(range(len(S_)), key=lambda k: abs(S_[k] - s_)); ux, uy, nx, ny = frame(i); x, y = P[i]
            ln = R.uniform(0.35, 0.7); hh = R.uniform(0.1, 0.24); zt = zglad(s_) + 0.72
            M = Matrix.Translation((x + sgn * nx * (breed / 2 + 0.18), y + sgn * ny * (breed / 2 + 0.18), zt + hh / 2 - 0.02)) @ Matrix.Rotation(math.atan2(uy, ux) + R.uniform(-0.08, 0.08), 4, "Z")
            st = bbox(ln, 0.46 + R.uniform(-0.04, 0.06), hh, 0, 0, 0, min(ln, hh) * 0.35)
            for v in st.verts: v.co += Vector((R.uniform(-0.03, 0.03), R.uniform(-0.03, 0.03), R.uniform(-0.025, 0.025)))
            for f in st.faces: f.smooth = True
            put(part, "dekst", st, M); s_ += ln + R.uniform(0.0, 0.05)
    # botsing: schuine blokken langs de loopvlakken + muren
    for i in range(0, len(P) - 3, 3):
        ux, uy, nx, ny = frame(i); x, y = P[i]; s0 = S_[i]
        coll_box(x, y, zpad(s0) - 0.25, 0.8, breed, 0.5, math.degrees(math.atan2(uy, ux)))
        for sgn in (-1, 1): coll_box(x + sgn * nx * (breed / 2 + 0.18), y + sgn * ny * (breed / 2 + 0.18), zglad(s0) + 0.1, 0.8, 0.4, 1.6, math.degrees(math.atan2(uy, ux)))
    if lantaarns:                                                                               # zwarte lantaarnpalen (Doornroosje_Trap_2022)
        s_ = 3.0
        while s_ < Ltot - 1:
            i = min(range(len(S_)), key=lambda k: abs(S_[k] - s_)); ux, uy, nx, ny = frame(i); x, y = P[i]
            px, py, pz = x - nx * (breed / 2 + 0.75), y - ny * (breed / 2 + 0.75), zglad(s_) - 0.3
            put(part, "ijzer", btube([(px, py, pz), (px, py, pz + 2.6)], 0.045, 8))
            put(part, "ijzer", blathe([(0, 0), (0.1, 0), (0.12, 0.05), (0.1, 0.32), (0.13, 0.35), (0.04, 0.45), (0, 0.48)], 6), TR(px, py, pz + 2.55))
            put(part, "lamp", blathe([(0, 0.06), (0.09, 0.06), (0.095, 0.3), (0, 0.3)], 6), TR(px, py, pz + 2.55))
            LAMPS_.append([round(px, 3), round(py, 3), round(pz + 2.75, 3)])
            s_ += 8.5


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
    for s in (-1, 1):                                                                           # wapenschilden naast de boog (Doornroosje_2026_Poortje, Doornroosjewapen)
        for sx in (-1, 1):
            Mw = Mr @ Matrix.Translation((sx * (min(1.6, W * 0.6) / 2 + 0.38), s * (L / 2 + 0.03), z0 + 1.9))
            sch = [(-0.22, 0.25), (0.22, 0.25), (0.22, -0.05), (0.0, -0.3), (-0.22, -0.05)]
            put(part, "wapenrood", boutline(sch, -0.02 if s > 0 else 0.0, 0.04), Mw)
            put(part, "goud", boutline([(x * 0.55, y * 0.55 + 0.03) for x, y in sch], -0.045 if s > 0 else 0.025, 0.02), Mw)
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
    # terraspad op kasteelhoogte: vlak keienpad met muurtjes
    trap(way("763240411"), Z0, Z0 + 0.001, 2.0, "terras", lantaarns=False)
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
    json.dump({"colliders": COLL, "lamps": LAMPS_}, open(os.path.join(out, "omgeving_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(os.path.abspath(m))
