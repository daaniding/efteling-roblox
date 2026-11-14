"""03_omgeving Roodkapje: hellingpad omhoog naar het huisje tussen rotsblokmuren (herbouw 2016: realistisch gemodelleerde ronde
grijze rotsblokken, Grootmoedershuisje_herbouwd / Pad_naar_roodkapje / Uitlooproodkapje2010), kijkplein met flagstones voor de
kijkramen (Roodkapje_kijkplein). OSM: pad 1074487763, muren 766787190/191/192. Zelfde frame als 03_huisje.
Padhoogte: 0 voor het huisje, aflopend naar ~-1.5 m (oost, bij de vijver) en -1.6 m (west, richting Pinokkio); maaiveld -1.9.
Pad = licht grind (Daan: paden altijd het lichte grind), kijkplein = flagstones.
Gebruik: Blender -b -P 03_omgeving.py -- --master RK_omgeving_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"grind": ((0.86, 0.83, 0.76, 1), 0.95), "flagstone": ((0.6, 0.55, 0.5, 1), 0.9), "rots": ((0.55, 0.55, 0.52, 1), 0.95)}
ZG = -1.9
def m(ox, oy): return (-0.995 * ox + 0.098 * oy, -0.098 * ox - 0.995 * oy)
CL = [((17.9, -2.76), 0.0), ((7.02, 3.52), 0.0), ((4.1, 3.89), 0.0), ((-2.98, 4.76), 0.0), ((-11.0, 1.03), 0.0),
      ((-13.34, 0.87), 0.0), ((-18.41, 3.16), 0.0)]   # Daan: pad gewoon vlak op het maaiveld, zoals bij de andere attracties
CL = [(m(*p), z) for p, z in CL]
NW = [m(*p) for p in [(19.6, -2.4), (18.44, -1.42), (7.76, 4.9), (-3.36, 6.23), (-11.09, 2.69), (-13.6, 2.5), (-17.6, 4.6)]]   # noordmuur (+verlengd)
ZW = [m(*p) for p in [(17.6, -4.4), (16.54, -3.83), (6.73, 2.26), (3.94, 2.7), (2.63, 2.81)]]                                  # zuidmuur oost
ZW2 = [m(*p) for p in [(-2.04, 3.27), (-3.09, 3.3), (-10.02, -0.18), (-13.0, -0.7), (-18.0, 1.4)]]                            # zuidmuur west


def proj(px, py):
    """dichtstbijzijnde punt op de padas -> (afstand, hoogte, richting)"""
    best = (1e9, 0, (1, 0))
    for (a, za), (b, zb) in zip(CL, CL[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy
        t = max(0, min(1, ((px - a[0]) * dx + (py - a[1]) * dy) / L2)); d = math.hypot(px - a[0] - t * dx, py - a[1] - t * dy)
        if d < best[0]: best = (d, za + (zb - za) * t, (dx / math.sqrt(L2), dy / math.sqrt(L2)), (a[0] + t * dx, a[1] + t * dy))
    return best


def padz(x, y): return proj(x, y)[1]


def inside(px, py, poly):
    c = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1): c = not c
    return c


def kei(c, sx, sy, sz, rot, seed):
    """rond grijs rotsblok: vervormde bol met grote zachte vlakken + kleine breukjes, platte onderkant"""
    r = random.Random(seed); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    o = Vector((r.uniform(0, 50), r.uniform(0, 50), r.uniform(0, 50)))
    for v in bm.verts:
        p = v.co.copy(); f = 1 + 0.22 * noise.noise(p * 0.9 + o) + 0.07 * noise.noise(p * 2.6 + o)
        v.co = Vector((p.x * sx, p.y * sy, p.z * sz)) * f
        if v.co.z < -sz * 0.55: v.co.z = -sz * 0.55
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z") @ Matrix.Rotation(r.uniform(-0.15, 0.15), 3, "X"))
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    for fc in bm.faces: fc.smooth = True
    return bm


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ---- gewoon grindpad (Daan): strook 3.4 m langs de vloeiende padas, 10 cm boven het terrein, geen rotsmuren ----
    def cr(p0, p1, p2, p3, t):
        return tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in range(3))
    P = [(a[0], a[1], z) for a, z in CL]; P = [P[0]] + P + [P[-1]]
    C = []
    for k in range(1, len(P) - 2):
        for t in range(8): C.append(cr(P[k - 1], P[k], P[k + 1], P[k + 2], t / 8))
    C.append(P[-2])
    W = 1.7; links, rechts = [], []
    for k, c in enumerate(C):
        a = C[max(k - 1, 0)]; b = C[min(k + 1, len(C) - 1)]; dx, dy = b[0] - a[0], b[1] - a[1]; L_ = math.hypot(dx, dy) or 1
        nx, ny = -dy / L_, dx / L_
        for side, lst in ((1, links), (-1, rechts)):
            x, y = c[0] + nx * W * side, c[1] + ny * W * side
            if -3.95 < x < -2.3 and y > -3.1: y = -3.1                     # niet over het bordes
            if -2.3 <= x <= 2.4 and y > -3.8: y = -2.3                     # tot tegen de voorgevel
            lst.append((x, y, padz(x, y) + 0.1))
    pb = bmesh.new()                                                                                   # dichte plaat 12 cm dik, bovenkant omhoog
    A = [pb.verts.new(v) for v in links]; B = [pb.verts.new(v) for v in rechts]
    A2 = [pb.verts.new((v[0], v[1], v[2] - 0.12)) for v in links]; B2 = [pb.verts.new((v[0], v[1], v[2] - 0.12)) for v in rechts]
    n_ = len(A)
    for k in range(n_ - 1):
        pb.faces.new((A[k], B[k], B[k + 1], A[k + 1])); pb.faces.new((A2[k], A2[k + 1], B2[k + 1], B2[k]))
        pb.faces.new((A[k], A[k + 1], A2[k + 1], A2[k])); pb.faces.new((B[k], B2[k], B2[k + 1], B[k + 1]))
    pb.faces.new((A[0], A2[0], B2[0], B[0])); pb.faces.new((A[-1], B[-1], B2[-1], A2[-1]))
    bmesh.ops.recalc_face_normals(pb, faces=pb.faces); pb.normal_update()
    top = [f for f in pb.faces if all(v in A or v in B for v in f.verts)]
    if sum(f.normal.z for f in top) < 0:
        for f in pb.faces: f.normal_flip()
    put("pad", "grind", pb)
    POLY = [(v[0], v[1]) for v in links] + [(v[0], v[1]) for v in rechts[::-1]]
    # padsegmenten voor de terreinvulling in Studio (schuine blokken): [x0,y0,z0,x1,y1,z1,breedte]
    segs = [[round(a[0], 2), round(a[1], 2), za, round(b[0], 2), round(b[1], 2), zb, 4.2] for (a, za), (b, zb) in zip(CL, CL[1:])]
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"RO_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "padsegmenten": segs, "poly": [[round(x, 2), round(y, 2)] for x, y in POLY]},
              open(os.path.join(out, "omgeving_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
