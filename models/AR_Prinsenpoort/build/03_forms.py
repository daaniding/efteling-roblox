"""03_forms Prinsenpoort: middenpoort met rondboog + schilddak + klokkentorentje, twee ronde torens met kegeldak en gouden prins,
bruggetje met lage muurtjes, grachtje voor de poort. Maten: asset-brief.md (1957-foto + OSM 967458492).
Meters, Z op, z=0 maaiveld, -Y = voorkant (plein), oorsprong = midden OSM-footprint.
Hulpfuncties uit AR_Assepoester/build/03_forms.py. Gebruik: Blender -b -P 03_forms.py -- --master AR_Prinsenpoort_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
_src = open(os.path.join(HERE, "..", "..", "AR_Assepoester", "build", "03_forms.py")).read().split("# ---- ramen ----")[0]
exec(_src)
RNG = random.Random(1952)
MATS = {
    "baksteen": ((0.55, 0.36, 0.28, 1), 0.9), "steen": ((0.58, 0.57, 0.54, 1), 0.9), "leien": ((0.36, 0.25, 0.19, 1), 0.85),
    "kassei": ((0.45, 0.43, 0.40, 1), 0.9), "goud": ((0.80, 0.60, 0.20, 1), 0.3), "ijzer": ((0.05, 0.06, 0.06, 1), 0.45),
    "hout": ((0.10, 0.22, 0.16, 1), 0.7), "venster": ((0.03, 0.03, 0.03, 1), 0.3), "glaslamp": ((0.9, 0.8, 0.6, 1), 0.2),
    "brons": ((0.30, 0.24, 0.14, 1), 0.35), "water": ((0.10, 0.12, 0.08, 1), 0.05), "bodem": ((0.20, 0.16, 0.11, 1), 1.0),
    "gras": ((0.18, 0.28, 0.10, 1), 0.9), "kraai": ((0.02, 0.02, 0.025, 1), 0.4), "snavel": ((0.15, 0.12, 0.08, 1), 0.5),
}
COLL = []; LAMPS_ = []
def coll_box(cx, cy, cz, sx, sy, sz, ang=0.0): COLL.append([round(v, 3) for v in (cx, cy, cz, sx, sy, sz, ang)])

PW, PD, PH = 2.45, 2.2, 3.5            # middenpoort halve breedte, halve diepte, dakvoet
AW, AH = 3.1, 2.85                     # boog
TX, TY, TR_, TH = 3.35, -1.2, 1.0, 4.05   # torens
BR_Y1 = -4.25                          # einde brug (pleinkant)
GR_Y0, GR_Y1, GR_X = -2.45, -3.95, 4.8    # grachtje


def lathe_course(part, mat, prof, segs, course, lip=0.03):
    """dak langs profiel [(r, z)] van voet naar top, met zaagtand per rij (schubben/pannen)"""
    pts = [Vector((r, z)) for r, z in prof]; L = sum((b - a).length for a, b in zip(pts, pts[1:])); n = max(3, round(L / course))
    def at(t):
        d = t * L
        for a, b in zip(pts, pts[1:]):
            l = (b - a).length
            if d <= l: return a.lerp(b, d / l)
            d -= l
        return pts[-1]
    bm = bmesh.new()
    def ring(r, z): return [bm.verts.new((r * math.cos(k * math.tau / segs), r * math.sin(k * math.tau / segs), z)) for k in range(segs)]
    rings = [ring(pts[0].x + lip, pts[0].y - 0.06)]
    for i in range(n):
        a = at(i / n); b = at((i + 1) / n); jit = 0.008 * math.sin(i * 2.3)
        rings.append(ring(a.x + lip + jit, a.y)); rings.append(ring(max(b.x, 0.001), b.y))
    for A, B in zip(rings, rings[1:]):
        for k in range(segs): bm.faces.new((A[k], A[(k + 1) % segs], B[(k + 1) % segs], B[k]))
    bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def earclip(bm):
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], ngon_method="EAR_CLIP"); return bm


def omhoog(b_):
    b_.normal_update()
    for f_ in b_.faces:
        if f_.normal.z < -0.5: f_.normal_flip()
    b_.normal_update(); return b_


def ruwe_stenen(pts, h=0.12, w=0.46, z0=0.0, part="brug"):
    """grove natuurstenen afdekking langs een polylijn"""
    for a_, b_ in zip(pts, pts[1:]):
        a_, b_ = Vector(a_), Vector(b_); d_ = b_ - a_; L_ = d_.length; ang = math.degrees(math.atan2(d_.y, d_.x)); k = 0.0
        while k < L_ - 0.02:
            ln = min(RNG.uniform(0.32, 0.55), L_ - k + 0.04); q = a_ + d_.normalized() * (k + ln / 2)
            put(part, "steen", bbox(ln + 0.04, w + RNG.uniform(-0.03, 0.04), h + RNG.uniform(0, 0.05), 0, 0, 0, 0.045), TR(q.x, q.y, z0 + h / 2, ang + RNG.uniform(-5, 5)))
            k += ln


def prins_silhouet():
    """gouden prins te paard (vlak silhouet, xz), ~0.42 breed"""
    return [(-0.2, 0.0), (-0.17, 0.0), (-0.15, 0.1), (-0.08, 0.12), (0.06, 0.12), (0.1, 0.0), (0.13, 0.0), (0.13, 0.12), (0.17, 0.16),
            (0.21, 0.22), (0.2, 0.26), (0.15, 0.25), (0.12, 0.2), (0.08, 0.22), (0.04, 0.22), (0.04, 0.3), (0.06, 0.36), (0.02, 0.4),
            (-0.02, 0.37), (-0.01, 0.3), (-0.02, 0.22), (-0.12, 0.21), (-0.2, 0.17), (-0.24, 0.1)]


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ================= MIDDENPOORT: muurmassief met boog door de hele diepte =================
    ap = arch_pts(0, -0.35, AW, AH + 0.35, 18)                              # linksonder -> over de boog -> rechtsonder
    front = [(-PW, -0.35)] + ap + [(PW, -0.35), (PW, PH), (-PW, PH)]
    put("poort", "baksteen", earclip(boutline(front, -PD, 2 * PD)))
    for y0 in (-PD - 0.05, PD - 0.01):                                        # bakstenen boogrand voor en achter (rollaag)
        put("poort", "baksteen", band(ap[1:-1], 0.32, y0, 0.06))
    put("poort", "baksteen", bz(-PW - 0.06, PW + 0.06, -PD - 0.06, PD + 0.06, PH - 0.16, PH, 0.01))      # lijst onder de dakvoet
    put("poort", "kassei", omhoog(bz(-AW / 2 + 0.02, AW / 2 - 0.02, -PD - 0.02, PD + 0.4, -0.2, 0.1)))   # keien in de doorgang
    # wapenschildje boven de boog (steen, neutraal)
    sh = [(-0.2, 3.22), (0.2, 3.22), (0.2, 2.98), (0.14, 2.86), (0.0, 2.8), (-0.14, 2.86), (-0.2, 2.98)]
    put("poort", "steen", boutline(sh, -PD - 0.09, 0.08))
    # muurlantaarn links van de boog (2003)
    lx, lz = -1.98, 2.25
    put("lantaarn", "ijzer", btube([(lx, -PD, lz + 0.42), (lx, -PD - 0.32, lz + 0.42), (lx, -PD - 0.32, lz + 0.32)], 0.015, 6))
    put("lantaarn", "ijzer", blathe([(0, 0.34), (0.13, 0.3), (0.13, 0.28), (0.1, 0.26), (0.1, 0.0), (0.07, -0.04), (0, -0.05)], 6), TR(lx, -PD - 0.32, lz))
    put("lantaarn", "glaslamp", blathe([(0, 0.01), (0.085, 0.01), (0.085, 0.25), (0, 0.25)], 6), TR(lx, -PD - 0.32, lz))
    LAMPS_.append([lx, round(-PD - 0.32, 2), lz + 0.12])
    # nis met groen luik links in de doorgang (PrinsenpoortLuik)
    nx = -AW / 2
    put("poort", "baksteen", bz(nx - 0.06, nx + 0.02, -0.75, 0.05, 0.92, 1.0))                                    # vensterbank
    put("luik", "baksteen", bz(nx - 0.02, nx + 0.06, -0.78, 0.08, 1.0, 1.68))                              # gemetselde omlijsting (steekt iets uit)
    put("luik", "venster", bz(nx + 0.06, nx + 0.07, -0.68, -0.02, 1.04, 1.6))
    for y0, y1 in ((-0.67, -0.36), (-0.34, -0.03)):
        put("luik", "hout", bz(nx + 0.07, nx + 0.1, y0, y1, 1.05, 1.58))
    # ================= TORENS =================
    for sx in (-1, 1):
        cx = sx * TX
        put("torens", "baksteen", blathe([(0, -0.4), (TR_ + 0.08, -0.4), (TR_ + 0.06, 0.6), (TR_, 1.6), (TR_, TH - 0.22), (TR_ + 0.08, TH - 0.22), (TR_ + 0.08, TH), (0, TH)], 40), TR(cx, TY))
        put("dak", "leien", lathe_course("dak", "leien", [(TR_ + 0.3, TH), (TR_ + 0.1, TH + 0.35), (0.72, TH + 1.15), (0.36, TH + 2.0), (0.04, 6.75)], 40, 0.13, 0.03), TR(cx, TY))
        put("dak", "leien", blathe([(TR_ + 0.3, TH - 0.06), (TR_ + 0.3, TH - 0.02), (TR_ - 0.02, TH - 0.02), (TR_ - 0.02, TH - 0.06)], 40), TR(cx, TY))   # onderkant overstek
        put("spits", "goud", blathe([(0, 6.6), (0.05, 6.62), (0.06, 6.72), (0.035, 6.8), (0.012, 6.82), (0.012, 7.35), (0, 7.36)], 10), TR(cx, TY))
        put("spits", "goud", blathe([(0, 6.86), (0.045, 6.9), (0.045, 6.95), (0, 6.99)], 10), TR(cx, TY))
        put("spits", "goud", earclip(boutline([(x + 0.0, z + 7.0) for x, z in prins_silhouet()], -0.008, 0.016)), TR(cx, TY, 0, 90 if sx > 0 else 0))
        # venster schuin naar voren-buiten
        a = math.atan2(-0.8, 0.6 * sx); ca, sa = math.cos(a), math.sin(a)
        Mw = Matrix.Translation((cx + ca * (TR_ - 0.02), TY + sa * (TR_ - 0.02), 0)) @ Matrix.Rotation(a - math.pi / 2, 4, "Z")
        put("torens", "venster", bz(-0.17, 0.17, -0.12, 0.06, 2.7, 3.25), Mw)
        put("torens", "steen", bz(-0.23, 0.23, -0.1, 0.03, 2.62, 2.7), Mw)
        put("torens", "steen", bz(-0.23, 0.23, -0.1, 0.03, 3.25, 3.33), Mw)
        coll_box(cx, TY, 2.0, 2 * TR_ + 0.1, 2 * TR_ + 0.1, 4.0, 0)
    # vogelkooi met kraai aan de linkertoren (voor-buiten)
    a = math.radians(225); kc = Vector((-TX + math.cos(a) * (TR_ + 0.45), TY + math.sin(a) * (TR_ + 0.45), 2.35))
    root = Vector((-TX + math.cos(a) * TR_, TY + math.sin(a) * TR_, 3.05))
    put("kooi", "ijzer", btube([root, Vector((kc.x, kc.y, 3.05))], 0.018, 6))
    put("kooi", "ijzer", btube([Vector((kc.x, kc.y, 3.05)), Vector((kc.x, kc.y, 2.82))], 0.008, 4))
    for k in range(12):
        t = k * math.tau / 12; p = Vector((kc.x + 0.17 * math.cos(t), kc.y + 0.17 * math.sin(t), 0))
        put("kooi", "ijzer", btube([(p.x, p.y, kc.z - 0.2), (p.x, p.y, kc.z + 0.2), (kc.x + 0.05 * math.cos(t), kc.y + 0.05 * math.sin(t), kc.z + 0.42)], 0.007, 4))
    for z in (kc.z - 0.2, kc.z + 0.2):
        put("kooi", "ijzer", btube([(kc.x + 0.17 * math.cos(t), kc.y + 0.17 * math.sin(t), z) for t in [i * math.tau / 24 for i in range(25)]], 0.009, 4))
    put("kooi", "ijzer", blathe([(0, -0.215), (0.18, -0.215), (0.18, -0.195), (0, -0.195)], 16), TR(kc.x, kc.y, kc.z))
    put("kraai", "kraai", blathe([(0, 0), (0.05, 0.02), (0.06, 0.08), (0.045, 0.14), (0, 0.16)], 10), TR(kc.x, kc.y, kc.z - 0.17) @ Matrix.Rotation(math.radians(-20), 4, "Y"))
    put("kraai", "kraai", blathe([(0, 0), (0.035, 0.01), (0.04, 0.04), (0.03, 0.07), (0, 0.075)], 10), TR(kc.x + 0.05, kc.y, kc.z - 0.03))
    put("kraai", "snavel", blathe([(0, 0), (0.012, 0), (0, 0.06)], 6), TR(kc.x + 0.085, kc.y, kc.z - 0.0) @ Matrix.Rotation(math.radians(90), 4, "Y"))
    put("kraai", "kraai", bz(-0.12, -0.02, -0.02, 0.02, -0.15, -0.13), TR(kc.x, kc.y, kc.z))
    # ================= MIDDENDAK + klokkentorentje =================
    tiled_roof("dak", (-PW - 0.3, PW + 0.3, -PD - 0.3, PD + 0.3), (-1.0, 1.0, 0.0, 0.0), PH, 6.0, course=0.14, lip=0.03, mat="leien")
    put("dak", "leien", bz(-PW - 0.3, PW + 0.3, -PD - 0.3, PD + 0.3, PH - 0.12, PH - 0.06))                 # onderkant overstek
    for sx_ in (-1, 1):
        for sy_ in (-1, 1): put("torentje", "hout", bz(sx_ * 0.2 - 0.035, sx_ * 0.2 + 0.035, sy_ * 0.2 - 0.035, sy_ * 0.2 + 0.035, 5.95, 6.4))
    put("torentje", "leien", bz(-0.26, 0.26, -0.26, 0.26, 5.85, 5.98))
    put("torentje", "brons", blathe([(0, 6.02), (0.05, 6.02), (0.07, 6.07), (0.09, 6.2), (0.13, 6.28), (0.12, 6.3), (0, 6.3)], 14))
    tiled_roof("torentje", (-0.34, 0.34, -0.34, 0.34), (0, 0, 0, 0), 6.4, 6.95, course=0.09, lip=0.02, mat="leien", hips=False)
    put("torentje", "goud", blathe([(0, 6.9), (0.04, 6.94), (0.045, 7.0), (0.01, 7.05), (0.01, 7.4), (0, 7.41)], 10))
    coll_box(-PW + 0.45, 0, 2.0, 0.9, 2 * PD, 4.0); coll_box(PW - 0.45, 0, 2.0, 0.9, 2 * PD, 4.0)
    # ================= BRUGGETJE =================
    BW = AW / 2
    put("brug", "kassei", omhoog(bz(-BW, BW, BR_Y1, -PD + 0.02, -0.2, 0.12)))
    put("brug", "baksteen", bz(-BW - 0.35, BW + 0.35, GR_Y1 + 0.05, GR_Y0 - 0.05, -0.75, -0.2))               # boogdek boven het water (onderkant)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * BW, sx * (BW + 0.36)))
        put("brug", "baksteen", bz(x0, x1, BR_Y1 - 0.15, -PD + 0.02, -0.7, 0.5))
        ruwe_stenen([(sx * (BW + 0.18), -PD + 0.0), (sx * (BW + 0.18), BR_Y1 - 0.15)], 0.13, 0.46, 0.48)
        put("brug", "steen", bbox(0.62, 0.55, 0.6, sx * (BW + 0.2), BR_Y1 - 0.42, 0.25, 0.12))                # grote eindsteen (1957-foto)
        c_ = (sx * (BW + 0.18), (BR_Y1 - 0.15 - PD) / 2); coll_box(c_[0], c_[1], 0.5, 0.4, -PD - BR_Y1 + 0.15, 1.0)
    # ================= GRACHTJE: modderbed + waterspiegel + grasoevers (terrein wordt in Studio uitgegraven) =================
    def stadion(x0, x1, y0, y1, n=12):
        r = (y0 - y1) / 2; yc = (y0 + y1) / 2; pts = []
        for k in range(n + 1): t = -math.pi / 2 + math.pi * k / n; pts.append(Vector((x1 + r * math.cos(t), yc + r * math.sin(t))))
        for k in range(n + 1): t = math.pi / 2 + math.pi * k / n; pts.append(Vector((x0 + r * math.cos(t), yc + r * math.sin(t))))
        return pts
    inner = stadion(-GR_X + 0.75, GR_X - 0.75, GR_Y0, GR_Y1)
    cen = Vector((0, (GR_Y0 + GR_Y1) / 2))
    wb = bmesh.new(); wv = [wb.verts.new((p.x, p.y, -0.2)) for p in inner]; wb.faces.new(wv); omhoog(earclip(wb)); put("gracht", "water", wb)
    # oever: van de waterlijn schuin omhoog naar het maaiveld (+5 cm), ring rond het water; brugzone overslaan (daar zit het brugdek)
    ob_ = bmesh.new(); rings = []
    xa, xb = -GR_X + 0.75, GR_X - 0.75
    for (grow, z) in ((-0.15, -0.55), (0.0, -0.17), (0.35, -0.02), (0.75, 0.05), (1.05, 0.05)):
        ring = []
        for p in inner:
            nearest = Vector((min(max(p.x, xa), xb), cen.y)); d = (p - nearest).normalized()
            q = p + d * grow
            ring.append(ob_.verts.new((q.x, q.y, z)))
        rings.append(ring)
    n_ = len(inner)
    for A, B in zip(rings, rings[1:]):
        for k in range(n_): ob_.faces.new((A[k], A[(k + 1) % n_], B[(k + 1) % n_], B[k]))
    bmesh.ops.recalc_face_normals(ob_, faces=ob_.faces); omhoog(ob_)
    bodem = [f for f in ob_.faces if f.calc_center_median().z < -0.18]; gras = [f for f in ob_.faces if f.calc_center_median().z >= -0.18]
    b2 = ob_.copy(); bmesh.ops.delete(ob_, geom=bodem, context="FACES"); put("gracht", "gras", ob_)
    bmesh.ops.delete(b2, geom=[f for f in b2.faces if f.calc_center_median().z >= -0.18], context="FACES"); put("gracht", "bodem", b2)
    bb = bmesh.new(); bv = [bb.verts.new((p.x, p.y, -0.55)) for p in inner]; bb.faces.new(bv); omhoog(earclip(bb)); put("gracht", "bodem", bb)
    # ================= wegschrijven =================
    for (part, mat), bm in PARTS.items():
        ob = new_mesh_object(f"PP_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "gracht": {"y0": GR_Y0, "y1": GR_Y1, "x": GR_X}}, open(os.path.join(out, "poort_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "colliders", len(COLL),
                             "tris", sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
