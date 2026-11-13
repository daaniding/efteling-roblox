"""04_omgeving Sneeuwwitje: voorplein, paden, bloemperken, bloembak, bloempotten, boekstandaard (OSM in modelcoordinaten, zie ref/model_frame.json).
Paden: 1169014963 (hoofdpad voor het kasteel), 1169014965, 1255787239/40 (kasteeluitgang -> grot), 1255787238 (grotuitgang -> park; sluit aan op het
Assepoester-hek 1255787242). Perken: 505382907 (voor grot/uitgang), 505382908 (zuid). Ondergrond: wit grind zoals Assepoester (Daan).
Straatmeubilair (bankjes, prullenbakken, lantaarnpalen) komt later apart (Daan)."""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "03_forms.py")).read().split("def build(master):")[0]
exec(_src)
TAG = "phase:04_omgeving_sw"
MATS.update({"klinker": ((0.80, 0.77, 0.71, 1), 0.95), "band": ((0.55, 0.53, 0.50, 1), 0.85), "aarde": ((0.20, 0.14, 0.10, 1), 1.0),
             "papier": ((0.90, 0.84, 0.66, 1), 0.8), "terracotta": ((0.62, 0.32, 0.20, 1), 0.85)})
COLLR = []
def collr(cx, cy, cz, sx, sy, sz, a=0.0): COLLR.append([round(v, 3) for v in (cx, cy, cz, sx, sy, sz, a)])


def catmull(pts, n=8):
    P = [pts[0]] + pts + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = (Vector(P[i - 1]), Vector(P[i]), Vector(P[i + 1]), Vector(P[i + 2]))
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(pts[-1])); return out


def ribbon(pts, w):
    L, R = [], []
    for i, p in enumerate(pts):
        a = Vector(pts[max(i - 1, 0)]); b = Vector(pts[min(i + 1, len(pts) - 1)])
        t = (b - a).normalized(); n = Vector((-t.y, t.x))
        L.append(tuple(Vector(p) + n * w / 2)); R.append(tuple(Vector(p) - n * w / 2))
    return L + R[::-1]


def slab(part, mat, ring, zt):
    bm = bmesh.new(); vs = [bm.verts.new((x, y, zt)) for x, y in ring]
    edges = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)
    bnd = [e for e in bm.edges if e.is_boundary]; r = bmesh.ops.extrude_edge_only(bm, edges=bnd)
    bmesh.ops.translate(bm, vec=(0, 0, -zt - 0.05), verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put(part, mat, bm)


def strip(part, mat, pts, w, zt):
    """pad als strook vierhoeken (geen vulling: in scherpe bochten klapte triangle_fill om -> zwarte driehoeken)"""
    bm = bmesh.new(); prev = None
    for i, p in enumerate(pts):
        a = Vector(pts[max(i - 1, 0)]); b = Vector(pts[min(i + 1, len(pts) - 1)])
        t = (b - a).normalized(); n = Vector((-t.y, t.x))
        l = bm.verts.new((p[0] + n.x * w / 2, p[1] + n.y * w / 2, zt)); r = bm.verts.new((p[0] - n.x * w / 2, p[1] - n.y * w / 2, zt))
        if prev:
            f = bm.faces.new((prev[1], r, l, prev[0]))
            if f.normal.z < 0: f.normal_flip()
        prev = (l, r)
    put(part, mat, bm)



def build(master):
    open_master(master)
    for o in [o for o in bpy.data.objects if o.get("owner") == TAG]: bpy.data.objects.remove(o, do_unlink=True)
    voor = set(o.name for o in bpy.data.objects)
    for n_, (c_, r_) in MATS.items(): material("MAT_" + n_, c_, r_)
    PARTS.clear()
    # voorplein (front.jpg: groot geplaveid plein voor de hele gevel) tot het hoofdpad
    plein = [(-7.6, 0.9), (7.4, 0.9), (8.6, 0.2), (10.1, -0.5), (10.5, -2.6), (8.4, -3.9), (4.2, -3.4), (-5.6, -5.8), (-9.2, -10.0), (-10.0, -6.0), (-9.4, 0.4)]
    slab("plein", "klinker", plein, 0.035)
    for pts, w in (([(-9.1, -21.8), (-9.5, -10.4), (-5.6, -5.0), (4.2, -2.4), (7.1, -4.2), (12.6, -7.5), (23.8, -10.0), (25.3, -10.4)], 4.0),   # 1169014963
                   ([(-9.1, -21.8), (3.4, -18.7), (7.3, -17.2), (11.5, -19.0)], 3.2),                                                       # 1169014965
                   ([(12.6, -7.5), (12.9, -13.6), (11.5, -19.0)], 3.0),                                                                      # 1169014964
                   ([(22.5, -7.2), (23.8, -10.0), (25.7, -16.1)], 2.6),                                                                      # 1255787238 grotuitgang
                   ([(7.1, -4.2), (8.6, -0.6)], 2.4)):                                                                                       # 1255787240
        strip("plein", "klinker", catmull(pts, 6), w, 0.034)
    # bloemperken (OSM-tuinen) met aarde; planten komen in Studio (06_planten)
    PERK_A = [(2.0, -5.1), (2.0, -7.1), (5.1, -7.7), (7.6, -9.5), (9.3, -12.1), (11.2, -11.3), (9.1, -8.0), (5.8, -5.8)]
    PERK_B = [(-5.3, -19.7), (-6.4, -17.7), (-6.8, -14.8), (-5.9, -11.8), (-4.7, -10.2), (-6.4, -9.1), (-7.7, -11.2), (-8.6, -14.5), (-8.1, -18.1), (-7.1, -20.5)]
    for P in (PERK_A, PERK_B):
        slab("perken", "aarde", P, 0.06)
        for a, b in zip(P, P[1:] + P[:1]):     # lage stenen rand
            L = math.hypot(b[0] - a[0], b[1] - a[1]); ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            put("perken", "band", bz(0, L + 0.08, -0.06, 0.06, 0, 0.12), TR(a[0], a[1], 0, ang))
    # gemetselde bloembak bij de ronde toren (front.jpg rechtsonder)
    bk = (-8.9, -2.2)   # zuidkant plein: niet voor de uitgangsdeur en niet op een looproute (Daan: pad vrij)
    put("bloembak", "baksteen", bz(bk[0] - 1.6, bk[0] + 1.6, bk[1] - 0.6, bk[1] + 0.6, 0, 0.62)); put("bloembak", "steen", bz(bk[0] - 1.65, bk[0] + 1.65, bk[1] - 0.65, bk[1] + 0.65, 0.62, 0.7, 0.01))
    put("bloembak", "aarde", bz(bk[0] - 1.5, bk[0] + 1.5, bk[1] - 0.5, bk[1] + 0.5, 0.7, 0.72)); collr(bk[0], bk[1], 0.35, 3.3, 1.3, 0.7)
    # bloempotten langs de gevel (front.jpg: oranje bloemen in houten/terracotta potten)
    POT = [(0, 0), (0.19, 0), (0.24, 0.36), (0.26, 0.38), (0, 0.38)]
    for px in (-6.6, -5.9, -3.75, -3.05, 0.95, 6.2):
        py = 0.2 if px < -2.46 else (1.0 if px < 3.4 else -0.3)
        put("potten", "terracotta", blathe(POT, 12), TR(px, py, 0)); put("potten", "aarde", blathe([(0, 0.34), (0.24, 0.34), (0.24, 0.35), (0, 0.35)], 12), TR(px, py, 0))
    # boekstandaard bij de grotingang (Boekloc_Sneeuwwitje.jpg)
    bx_, by_ = 9.0, 0.55
    put("boek", "ijzer", btube([(bx_, by_, 0), (bx_, by_, 0.95)], 0.022, 6))
    Mb = TR(bx_, by_, 0.97) @ Matrix.Rotation(math.radians(-25), 4, "X") @ TR(-bx_, -by_, -0.97) @ TR(0, 0, 0)
    put("boek", "goud", bz(bx_ - 0.3, bx_ + 0.3, by_ - 0.2, by_ + 0.2, 0.95, 0.98), TR(bx_, by_, 0) @ Matrix.Rotation(math.radians(70), 4, "Z") @ TR(-bx_, -by_, 0) @ Mb)
    put("boek", "papier", bz(bx_ - 0.27, bx_ + 0.27, by_ - 0.17, by_ + 0.17, 0.98, 1.0), TR(bx_, by_, 0) @ Matrix.Rotation(math.radians(70), 4, "Z") @ TR(-bx_, -by_, 0) @ Mb)
    collr(bx_, by_, 0.5, 0.6, 0.45, 1.0)
    # wegschrijven
    for (part, mat), bm in PARTS.items():
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        ob = new_mesh_object(f"SO_{part}__{mat}", bm, "OMGEVING"); assign(ob, bpy.data.materials["MAT_" + mat])
    for o in bpy.data.objects:
        if o.name not in voor: o["owner"] = TAG
    out = os.path.join(os.path.dirname(HERE), "exports")
    json.dump({"colliders": COLLR, "lamps": [], "perk_a": PERK_A, "perk_b": PERK_B, "plein": plein}, open(os.path.join(out, "omgeving_extra.json"), "w"))
    save_master(master); log("omgeving", len(PARTS), "colliders", len(COLLR))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
