"""04_omgeving De Prinses op de Erwt: het pleintje direct rond het huisje (eigen asset, eigen bake).
- plein in licht grind (Daan: paden/pleinen altijd het lichte grind), tot de border en de OSM-paden 1406396370 (voor) -- paden verder: later
- lage stucmuurtjes met afgeronde natuurstenen kap (Boekloc, Pleintje, Aanloop): links achter (tot hoekpijler, met smeedijzeren hekje naar het
  hotel) en dan naar voren tot de pijler bij het sprookjesboek; rechts achter met kwartronde, oplopende aansluiting op het huis (Achterkant),
  tot een bakstenen pijler en dan langs het pad naar voren (Aanloop)
- bakstenen pijlers met natuurstenen kap en knopvormige bol (Boekloc)
- Pieckbankjes (groene plank op twee bakstenen poten, Boekloc) op de 4 OSM-banken
- ronde border (OSM 1406396363) met opgemetselde bakstenen rand (Pleintje)
- schaakbordtegels met bakstenen rand voor het kijkraam en voor de deur (Plavuis, Exterieur)
- groen kastje met lantaarn (Stolp) en schuin groen bordkastje naast de deur (Exterieur)
- sprookjesboek op smeedijzeren standaard + lage groene buisleuning langs het perkje (Boekloc)
Frame = 03_huis (oorsprong midden OSM 1406396369, -Y = voorkant NO). Gebruik: Blender -b -P 04_omgeving.py -- --master PE_omgeving_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.86, 0.82, 0.72, 1), 0.9), "natuursteen": ((0.74, 0.66, 0.5, 1), 0.85), "baksteen": ((0.55, 0.32, 0.25, 1), 0.9),
        "grind": ((0.86, 0.83, 0.76, 1), 0.95), "tegelzwart": ((0.06, 0.06, 0.06, 1), 0.2), "tegelwit": ((0.9, 0.9, 0.88, 1), 0.2),
        "groen": ((0.16, 0.3, 0.27, 1), 0.6), "ijzer": ((0.04, 0.05, 0.05, 1), 0.45), "goud": ((0.8, 0.6, 0.22, 1), 0.3),
        "aarde": ((0.22, 0.16, 0.11, 1), 1.0), "hout": ((0.35, 0.22, 0.13, 1), 0.8), "papier": ((0.92, 0.86, 0.7, 1), 0.9),
        "rood": ((0.62, 0.1, 0.1, 1), 0.5), "lantaarnrood": ((0.75, 0.15, 0.08, 1), 0.3), "glaslamp": ((0.95, 0.93, 0.88, 1), 0.2)}
XL, XR, YF, YB = -1.95, 2.67, -2.35, 2.35          # huis (03_huis)
PX0, PY1 = -2.7, 2.45
WH = 1.0; WT = 0.36                                # muurtje: hoogte (Boekloc: ~2x de bank), dikte
BORDER = [(7.01, -7.07), (4.38, -8.94), (0.8, -9.76), (-1.74, -9.24), (-3.22, -8.11), (-3.67, -7.38), (-1.84, -6.73), (0.68, -7.34), (3.0, -7.27), (5.57, -6.47), (6.71, -6.19)]
# plein: achter de muurtjes, voor tot de border (OSM-pad 1406396370 loopt over het plein)
PLEIN = [(-9.45, 3.0), (7.6, 3.1), (11.6, -2.55), (11.0, -6.6), (9.61, -7.8), (7.01, -7.07), (6.71, -6.19), (5.57, -6.47), (3.0, -7.27), (0.68, -7.34),
         (-1.84, -6.73), (-3.67, -7.38), (-6.11, -7.48), (-8.6, -6.0), (-11.2, -3.1), (-10.1, 0.9)]
P1, P2, P2B = (-8.9, 2.85), (7.35, 2.75), (11.25, -2.65)       # bakstenen pijlers (P1 teruggerekend uit Pleintje: voet ~(-8.3..-9.1, 2.8..4.1))
GATE = (-6.6, -5.8)                                                                # hekje in het linker muurtje (Pleintje x 213-240 = X -7.0..-6.5; Boekloc rechts van de bank)
BANKEN = [((-7.7, 2.2), 0), ((4.73, 1.95), 0), ((3.87, -6.37), 0), ((0.38, -6.34), 0)]   # OSM-banken (achter: tegen de muur geschoven)


def muur(pts, h0=WH, h1=None, closed=False):
    """muurtje langs een polylijn: stucromp + afgeronde natuurstenen kap; h1 = hoogte aan het eind (oplopend)"""
    h1 = h0 if h1 is None else h1
    A = [Vector(p) for p in pts]; L_tot = sum((b - a).length for a, b in zip(A, A[1:])); acc = 0.0
    for a, b in zip(A, A[1:]):
        d = (b - a); L = d.length; u = d.normalized(); n = Vector((-u.y, u.x)); k = max(1, int(L / 0.5))
        for i in range(k):
            t0, t1 = i / k, (i + 1) / k
            p0, p1 = a + d * t0, a + d * t1
            z0 = h0 + (h1 - h0) * (acc + L * t0) / L_tot; z1 = h0 + (h1 - h0) * (acc + L * t1) / L_tot
            bm = bmesh.new()
            q = [p0 - n * WT / 2, p1 - n * WT / 2, p1 + n * WT / 2, p0 + n * WT / 2]; zs = [z0, z1, z1, z0]
            bot = [bm.verts.new((v.x, v.y, -0.05)) for v in q]; top = [bm.verts.new((v.x, v.y, z - 0.08)) for v, z in zip(q, zs)]
            bm.faces.new(bot[::-1]); bm.faces.new(top)
            for j in range(4): bm.faces.new((bot[j], bot[(j + 1) % 4], top[(j + 1) % 4], top[j]))
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("muur", "stuc", bm)
            # kap: halfrond profiel, iets breder
            prof = [(-WT / 2 - 0.05, -0.1), (-WT / 2 - 0.05, -0.04), (-WT / 2 + 0.02, 0.03), (0.0, 0.06), (WT / 2 - 0.02, 0.03), (WT / 2 + 0.05, -0.04), (WT / 2 + 0.05, -0.1)]
            bm = bmesh.new()
            R0 = [bm.verts.new((p0.x + n.x * o, p0.y + n.y * o, z0 + dz)) for o, dz in prof]; R1 = [bm.verts.new((p1.x + n.x * o, p1.y + n.y * o, z1 + dz)) for o, dz in prof]
            for j in range(len(prof) - 1): bm.faces.new((R0[j], R0[j + 1], R1[j + 1], R1[j]))
            bm.faces.new((R0[-1], R1[-1], R1[0], R0[0])); bm.faces.new(R0[::-1]); bm.faces.new(R1)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("kap", "natuursteen", bm)
        mid = (a + b) / 2; coll_box(mid.x, mid.y, 0.8, max(L, 0.3), WT, 1.6, math.degrees(math.atan2(u.y, u.x)))
        acc += L


def pijler(p, h=1.45):
    x, y = p
    put("pijler", "baksteen", bz(x - 0.3, x + 0.3, y - 0.3, y + 0.3, -0.05, h))
    put("pijler", "natuursteen", bz(x - 0.36, x + 0.36, y - 0.36, y + 0.36, -0.05, 0.25, 0.01))
    put("pijler", "natuursteen", bsweep([(0.0, 0.0), (0.06, 0.05), (0.06, 0.14), (0.02, 0.18), (0.0, 0.18)], x - 0.33, x + 0.33, y - 0.33, y + 0.33, h))
    # knopvormige bol met bladeren (Boekloc)
    put("pijler", "natuursteen", blathe([(0, 0), (0.14, 0), (0.12, 0.08), (0.22, 0.2), (0.25, 0.32), (0.2, 0.45), (0.1, 0.56), (0.05, 0.62), (0.03, 0.72), (0, 0.74)], 14), TR(x, y, h + 0.18))
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        put("pijler", "natuursteen", ell((x + 0.22 * math.cos(a), y + 0.22 * math.sin(a), h + 0.38), (0.06, 0.06, 0.16), 6, 6))
    coll_box(x, y, (h + 0.9) / 2, 0.6, 0.6, h + 0.9)


def bank(p, rot):
    """Pieckbankje: groene plank op twee bakstenen poten (Boekloc)"""
    M = TR(p[0], p[1], 0, rot)
    for s in (-1, 1):
        put("bank", "baksteen", bz(s * 0.75 - 0.18, s * 0.75 + 0.18, -0.2, 0.2, -0.02, 0.42), M)
    put("bank", "groen", bz(-1.05, 1.05, -0.24, 0.24, 0.42, 0.5, 0.01), M)
    c = M @ Vector((0, 0, 0)); coll_box(c.x, c.y, 0.25, 2.1 if rot == 0 else 0.5, 0.5 if rot == 0 else 2.1, 0.5)


def tegels(x0, x1, y0, y1, n_x, n_y, rand=0.1):
    """schaakbord (zwart/wit) met een rand van liggende bakstenen"""
    put("tegels", "baksteen", bz(x0 - rand, x1 + rand, y0 - rand, y1 + rand, 0.0, 0.11))
    dx, dy = (x1 - x0) / n_x, (y1 - y0) / n_y
    for i in range(n_x):
        for j in range(n_y):
            put("tegels", "tegelzwart" if (i + j) % 2 else "tegelwit", bz(x0 + i * dx + 0.003, x0 + (i + 1) * dx - 0.003, y0 + j * dy + 0.003, y0 + (j + 1) * dy - 0.003, 0.11, 0.125))


def plaat(poly, z, mat, part, dz=0.12):
    """dichte plaat met de bovenkant gecontroleerd omhoog (oorknippen via bmesh triangulate)"""
    bm = bmesh.new(); t_ = [bm.verts.new((x, y, z)) for x, y in poly]; b_ = [bm.verts.new((x, y, z - dz)) for x, y in poly]
    ft = bm.faces.new(t_); fb = bm.faces.new(b_[::-1]); N = len(poly)
    for i in range(N): bm.faces.new((t_[i], b_[i], b_[(i + 1) % N], t_[(i + 1) % N]))
    bmesh.ops.triangulate(bm, faces=[ft, fb], ngon_method="EAR_CLIP")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update()
    for f_ in bm.faces:
        if abs(f_.normal.z) > 0.5 and (f_.calc_center_median().z > z - dz / 2) != (f_.normal.z > 0): f_.normal_flip()
    put(part, mat, bm)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ---------- plein (grind), onder het huis door ----------
    plaat(PLEIN, 0.1, "grind", "plein", 0.14)
    # ---------- muurtjes ----------
    muur([(PX0 + 0.15, 2.64), (GATE[1] + 0.05, 2.75)]); muur([(GATE[0] - 0.05, 2.78), (P1[0] + 0.3, P1[1])])
    muur([(P1[0] - 0.3, P1[1] + 0.05), (-11.6, 3.55)])                                                    # loopt door achter het perkje (Pleintje links)
    # rechts: kwartronde oplopende aansluiting op de achtergevel (Achterkant: eindstuk tot ~2.4 m tegen het huis), dan recht tot P2, dan langs het pad
    arc_ = [(XR - 0.25 + 0.95 * math.sin(t), YB + 0.05 + 0.95 * (1 - math.cos(t)) * 0.0 + 0.4 * math.sin(t) * 0.0) for t in [0]]
    q = [(XR - 0.6 + 1.0 * math.sin(math.pi / 2 * k / 6), YB + 0.05 + 1.0 * (1 - math.cos(math.pi / 2 * k / 6)) * 0.4) for k in range(7)]
    muur(q, 2.4, WH + 0.05)
    put("muur", "stuc", bz(XR - 0.78, XR - 0.42, YB - 0.05, YB + 0.32, -0.05, 2.45))                         # oplopend eindstuk tegen de gevel
    put("kap", "natuursteen", bz(XR - 0.82, XR - 0.38, YB - 0.05, YB + 0.36, 2.42, 2.52, 0.02))
    muur([q[-1], (P2[0] - 0.3, P2[1])]); muur([(P2[0] + 0.2, P2[1] - 0.2), (P2B[0] - 0.2, P2B[1] + 0.25)])
    for p in (P1, P2, P2B): pijler(p)
    # smeedijzeren hekje naar het hotel (Boekloc: in het linker muurtje)
    gx0, gx1 = GATE[0], GATE[1]; gy = 2.77
    put("hek", "ijzer", btube([(gx0, gy, 0.1), (gx1, gy, 0.1)], 0.02, 5)); put("hek", "ijzer", btube([(gx0, gy, 1.05), (gx1, gy, 1.05)], 0.02, 5))
    for k in range(11):
        x = gx0 + (gx1 - gx0) * k / 10; put("hek", "ijzer", btube([(x, gy, 0.1), (x, gy, 1.15 + 0.08 * math.sin(math.pi * k / 10))], 0.012, 4))
    for x in (gx0, gx1): put("hek", "ijzer", btube([(x, gy, 0.0), (x, gy, 1.25)], 0.03, 6))
    coll_box((gx0 + gx1) / 2, gy, 0.6, gx1 - gx0, 0.1, 1.2)
    # ---------- banken ----------
    for p, r in BANKEN: bank(p, r)
    # ---------- border met opgemetselde bakstenen rand ----------
    B = [Vector(p) for p in BORDER]
    cx = sum(p.x for p in B) / len(B); cy = sum(p.y for p in B) / len(B)
    inner = [Vector((cx, cy)) + (p - Vector((cx, cy))) * 1.0 for p in B]
    for a, b in zip(B, B[1:] + B[:1]):
        d = b - a; u = d.normalized(); n = Vector((-u.y, u.x)); L = d.length
        bm = bmesh.new()
        q2 = [a, b, b + n * 0.3, a + n * 0.3]
        bot = [bm.verts.new((v.x, v.y, 0.0)) for v in q2]; top = [bm.verts.new((v.x, v.y, 0.48)) for v in q2]
        bm.faces.new(bot[::-1]); bm.faces.new(top)
        for j in range(4): bm.faces.new((bot[j], bot[(j + 1) % 4], top[(j + 1) % 4], top[j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("border", "baksteen", bm)
        mid = (a + b) / 2; coll_box(mid.x, mid.y, 0.24, L, 0.3, 0.48, math.degrees(math.atan2(u.y, u.x)))
    plaat(BORDER, 0.42, "aarde", "border", 0.4)
    # ---------- schaakbordtegels voor het kijkraam en de deur ----------
    tegels(XL - 1.0, XL - 0.12, -1.15, 1.05, 6, 14)                                                          # Exterieur: onder het kijkraam, tot de pijler
    tegels(-1.2, 2.5, YF - 1.1, YF - 0.12, 22, 6)                                                             # voor de deur
    # ---------- groen kastje met lantaarn + bordkastje (Exterieur, Stolp) ----------
    kx, ky = -0.95, YF - 0.45
    put("kastje", "groen", bz(kx - 0.32, kx + 0.32, ky - 0.28, ky + 0.28, 0.12, 0.72, 0.01))
    for i in range(5): put("kastje", "groen", bz(kx - 0.32 + i * 0.16 - 0.006, kx - 0.32 + i * 0.16 + 0.006, ky - 0.29, ky - 0.28, 0.14, 0.7))
    Ml = TR(kx, ky, 0.72)
    put("kastje", "goud", blathe([(0.16, 0), (0.16, 0.04), (0.12, 0.06), (0.12, 0.08), (0, 0.08)], 8), Ml)
    put("kastje", "lantaarnrood", blathe([(0.1, 0.08), (0.11, 0.38), (0, 0.38)], 8), Ml)
    for k in range(6):
        a = k * math.tau / 6; put("kastje", "goud", btube([(0.11 * math.cos(a), 0.11 * math.sin(a), 0.08), (0.11 * math.cos(a), 0.11 * math.sin(a), 0.4)], 0.01, 4), Ml)
    put("kastje", "goud", blathe([(0.15, 0.38), (0.09, 0.5), (0.04, 0.56), (0.05, 0.62), (0, 0.66)], 8), Ml); LAMPS_.append([kx, ky, 1.0])
    put("kastje", "groen", bz(kx - 0.22, kx + 0.22, ky - 0.62, ky - 0.32, 0.12, 0.42), )                     # schuin bordkastje
    put("kastje", "goud", bz(kx - 0.18, kx + 0.18, ky - 0.64, ky - 0.62, 0.2, 0.38))
    coll_box(kx, ky - 0.15, 0.6, 0.65, 0.9, 1.2)
    # ---------- sprookjesboek op smeedijzeren standaard + buisleuning langs het perkje (Boekloc) ----------
    MB = TR(-10.3, -1.8, 0.1, -70)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.035, 6), MB)
    for s in (-1, 1): put("boek", "ijzer", btube([(0, 0, 0.05), (s * 0.12, 0.05, 0.12), (s * 0.22, 0.0, 0.0)], 0.018, 5), MB); put("boek", "ijzer", btube([(0, 0, 0.6), (s * 0.12, -0.02, 0.5), (s * 0.08, 0, 0.35)], 0.012, 5), MB)
    MBk = MB @ TR(0, 0, 0.9) @ Matrix.Rotation(math.radians(-28), 4, "X")
    put("boek", "rood", bz(-0.42, 0.42, -0.28, 0.28, -0.04, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.26, 0.26, 0.0, 0.05, 0.01), MBk)
    coll_box(-10.3, -1.8, 0.5, 0.7, 0.5, 1.0, 20)
    R_ = [(-9.75, 2.3), (-10.75, 0.0), (-11.5, -2.9)]                                                        # lage groene buisleuning (perkrand)
    for (a, b) in zip(R_, R_[1:]):
        put("leuning", "groen", btube([(a[0], a[1], 0.62), (b[0], b[1], 0.62)], 0.02, 5))
        for t in (0.0, 0.5):
            p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            put("leuning", "groen", btube([(p[0], p[1], 0.0), (p[0], p[1], 0.64)], 0.02, 5))
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"PO_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": PLEIN, "border": BORDER}, open(os.path.join(out, "omgeving_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
