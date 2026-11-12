"""04_omgeving Assepoester: binnenplaats + tuin zoals in de Efteling (ref/osm_model.json + Eftepedia-foto's).
Modelcoordinaten als 03_forms (gevel kijkt naar -Y = west, +X = zuid). Collectie OMGEVING.
Bronnen: OSM-hagen 1255787235 (lange haag langs de binnenplaats) en 1255787236 (U rond het dienstplaatsje), voetpaden
729126648 (aanloop door de haagopening), 683933436/55867430 (uitgang langs de haag naar het parkpad op x 15.6), hek 1255787242.
Foto's: Assepoester_tuin_nieuw (perk met buxusrand + lantaarns), nieuwepoort-aankomst-2023 (haagopening, pijler, grafje),
Assepoesterkolom / tuinhek_oud (pijlers met vaas en smeedijzeren hek), Assepoes-dienstpoort (blauwgroene plankenpoort, kist),
Boekloc_nieuw (boekstandaard, kist, pompoenen, lantaarn op krul), D6z (uitgangsboog, galgje-lantaarn, rotsjes, mand).
Inferred: haaghoogtes (2.6 m), exacte plek van perk/grafje/dienstpoort, vorm van de uitgangsboog."""
import bpy, bmesh, sys, os, math, json, random
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "03_forms.py")).read().split("def build(master):")[0]
_src = _src.replace('PHASE = "03_forms"', 'PHASE = "04_omgeving"')
exec(_src)
RNG = random.Random(2009)
MATS.update({
    "haag": ((0.09, 0.20, 0.08, 1), 0.9), "buxus": ((0.13, 0.28, 0.10, 1), 0.9), "klinker": ((0.47, 0.32, 0.26, 1), 0.9),
    "band": ((0.55, 0.53, 0.50, 1), 0.85), "ijzer": ((0.05, 0.06, 0.06, 1), 0.45), "aarde": ((0.20, 0.14, 0.10, 1), 1.0),
    "lamp": ((1.0, 0.82, 0.50, 1), 0.3), "rots": ((0.55, 0.50, 0.44, 1), 0.95), "kist": ((0.32, 0.19, 0.11, 1), 0.7),
    "papier": ((0.90, 0.84, 0.66, 1), 0.8), "goud": ((0.74, 0.58, 0.26, 1), 0.35), "mand": ((0.55, 0.40, 0.22, 1), 0.9),
})
COLLR = []
def collr(cx, cy, cz, sx, sy, sz, a=0.0): COLLR.append([round(v, 3) for v in (cx, cy, cz, sx, sy, sz, a)])
LAMPS = []


def haag(pts, w, h, mat="haag"):
    """geschoren haag met diepte (Villa Volta 04_omgeving): doorlopende vorm, ronde bovenkant, ruisbobbels"""
    P = [Vector((x, y, 0)) for x, y in pts]
    seq = []
    for a_, b_ in zip(P, P[1:]):
        L = (b_ - a_).length; n = max(1, int(L / 0.12))
        for i in range(n): seq.append(a_ + (b_ - a_) * (i / n))
    seq.append(P[-1])
    r = min(w / 2 * 0.9, 0.22)
    zr = [z_ for z_ in (0.0, 0.12, 0.25, 0.38, 0.5, 0.62, 0.75) if z_ * h < h - r - 0.02]
    prof = [(-w / 2, z_ * h) for z_ in zr] + [(-w / 2, h - r)] + [(-w / 2 + r - r * math.cos(t), h - r + r * math.sin(t)) for t in (math.radians(30), math.radians(60))]
    prof += [(-w / 2 + r, h)] + [(u, h) for u in (-w / 6, w / 6)] + [(w / 2 - r, h)]
    prof += [(w / 2 - r + r * math.cos(t), h - r + r * math.sin(t)) for t in (math.radians(60), math.radians(30))] + [(w / 2, h - r)] + [(w / 2, z_ * h) for z_ in reversed(zr)]
    pn = [(-1, 0)] * len(zr) + [(-1, 0.2), (-0.8, 0.6), (-0.5, 0.85), (-0.2, 1), (0, 1), (0, 1), (0.2, 1), (0.5, 0.85), (0.8, 0.6), (1, 0.2)] + [(1, 0)] * len(zr)
    bm = bmesh.new(); rings = []; N = len(seq)
    for i, c in enumerate(seq):
        t = seq[min(i + 1, N - 1)] - seq[max(i - 1, 0)]; t.z = 0; t.normalize()
        side = Vector((-t.y, t.x, 0)); ring = []
        for (u, z), (nu, nz) in zip(prof, pn):
            q = c + side * u + Vector((0, 0, z))
            d = 0.05 * noise.noise(q * 2.4) + 0.035 * noise.noise(q * 7.0 + Vector((3.1, 1.7, 0.4))) + 0.015 * noise.noise(q * 16.0) + 0.035
            d *= min(1.0, z / 0.15) if z < 0.15 else 1.0
            nv = side * nu + Vector((0, 0, nz)); nv.normalize()
            ring.append(bm.verts.new(q + nv * d))
        rings.append(ring)
    M = len(prof)
    for A, B in zip(rings, rings[1:]):
        for k in range(M - 1): bm.faces.new((A[k], B[k], B[k + 1], A[k + 1]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    put("hagen", mat, bm)
    for p_, q_ in zip(pts, pts[1:]):
        L = math.hypot(q_[0] - p_[0], q_[1] - p_[1])
        if L > 0.05: collr((p_[0] + q_[0]) / 2, (p_[1] + q_[1]) / 2, h / 2, L + w * 0.5, w, h, math.degrees(math.atan2(q_[1] - p_[1], q_[0] - p_[0])))


def slab(part, mat, ring, zt, holes=()):
    bm = bmesh.new(); edges = []
    for rg in [ring] + list(holes):
        vs = [bm.verts.new((x, y, zt)) for x, y in rg]
        edges += [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)
    if holes:   # triangle_fill vult ook de gaten: driehoeken met het zwaartepunt in een gat weghalen
        def inside(px, py, poly):
            c = False; j = len(poly) - 1
            for i in range(len(poly)):
                xi, yi = poly[i]; xj, yj = poly[j]
                if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi: c = not c
                j = i
            return c
        dead = [f for f in bm.faces if any(inside(f.calc_center_median().x, f.calc_center_median().y, hl) for hl in holes)]
        bmesh.ops.delete(bm, geom=dead, context="FACES")
    bnd = [e for e in bm.edges if e.is_boundary]
    r = bmesh.ops.extrude_edge_only(bm, edges=bnd)
    bmesh.ops.translate(bm, vec=(0, 0, -zt - 0.05), verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    put(part, mat, bm)


def catmull(pts, n=8):
    P = [pts[0]] + pts + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = (Vector(P[i - 1]), Vector(P[i]), Vector(P[i + 1]), Vector(P[i + 2]))
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(pts[-1])); return out


def ribbon(pts, w):
    """polygon van een pad met breedte w langs een polylijn"""
    L, R = [], []
    for i, p in enumerate(pts):
        a = Vector(pts[max(i - 1, 0)]); b = Vector(pts[min(i + 1, len(pts) - 1)])
        t = (b - a).normalized(); n = Vector((-t.y, t.x))
        L.append(tuple(Vector(p) + n * w / 2)); R.append(tuple(Vector(p) - n * w / 2))
    return L + R[::-1]


def lantern_head(x, y, z, s=1.0, part="lantaarns"):
    """open lantaarn: glas tussen vier stijltjes (Villa Volta)"""
    put(part, "ijzer", blathe([(0, 0), (0.06 * s, 0), (0.1 * s, 0.04 * s), (0.13 * s, 0.06 * s), (0.13 * s, 0.08 * s), (0, 0.08 * s)], 8), TR(x, y, z))
    for k in range(4):
        a = math.radians(45 + 90 * k); r = 0.13 * s
        put(part, "ijzer", btube([(x + r * math.cos(a), y + r * math.sin(a), z + 0.07 * s), (x + r * 1.15 * math.cos(a), y + r * 1.15 * math.sin(a), z + 0.37 * s)], 0.012 * s, 4))
    put(part, "lamp", blathe([(0, 0.08 * s), (0.1 * s, 0.08 * s), (0.125 * s, 0.36 * s), (0, 0.36 * s)], 8), TR(x, y, z))
    put(part, "ijzer", blathe([(0, 0.36 * s), (0.19 * s, 0.36 * s), (0.19 * s, 0.39 * s), (0.11 * s, 0.48 * s), (0.04 * s, 0.55 * s), (0.03 * s, 0.6 * s), (0.05 * s, 0.64 * s), (0, 0.7 * s)], 8), TR(x, y, z))
    LAMPS.append((x, y, z + 0.25 * s))


def lantern_post(x, y, h=1.9):
    """smal ijzeren paaltje met lantaarn (tuin_nieuw.jpg: in de hoeken van het perk)"""
    put("lantaarns", "ijzer", blathe([(0, 0), (0.09, 0), (0.09, 0.06), (0.05, 0.1), (0.035, 0.3), (0.03, h), (0.05, h + 0.03), (0, h + 0.03)], 8), TR(x, y, 0))
    lantern_head(x, y, h + 0.02, 0.85)
    collr(x, y, h / 2, 0.2, 0.2, h)


def curl_lantern(x, y, h=1.65, rz=0):
    """lantaarn aan een krul (Boekloc_nieuw.jpg): staander met omgekrulde top"""
    M = TR(x, y, 0, rz)
    put("lantaarns", "ijzer", btube([(0, 0, 0), (0, 0, h), (0.05, 0, h + 0.12), (0.16, 0, h + 0.14), (0.22, 0, h + 0.06)], 0.022, 6), M)
    put("lantaarns", "ijzer", blathe([(0, 0), (0.1, 0), (0.1, 0.04), (0, 0.06)], 8), M)
    c = M @ Vector((0.22, 0, h - 0.42)); lantern_head(c.x, c.y, c.z, 0.75)
    put("lantaarns", "ijzer", btube([(0.22, 0, h + 0.06), (0.22, 0, h - 0.42 + 0.5)], 0.008, 4), M)
    collr(x, y, h / 2, 0.15, 0.15, h)


def gallows_lantern(x, y, rz=0):
    """houten galg met hangende lantaarn (D6z_landschap: bij de uitgang)"""
    M = TR(x, y, 0, rz)
    put("lantaarns", "hout", bz(-0.08, 0.08, -0.08, 0.08, 0, 2.6, 0.015), M)
    put("lantaarns", "hout", bz(-0.08, 0.95, -0.06, 0.06, 2.45, 2.57, 0.01), M)
    put("lantaarns", "hout", btube([(0.0, 0, 2.0), (0.5, 0, 2.48)], 0.04, 6), M)
    put("lantaarns", "ijzer", btube([(0.85, 0, 2.45), (0.85, 0, 2.15)], 0.008, 4), M)
    c = M @ Vector((0.85, 0, 1.70)); lantern_head(c.x, c.y, c.z, 0.9)
    put("lantaarns", "rots", bz(-0.25, 0.25, -0.25, 0.25, 0, 0.08, 0.02), M)
    collr(x, y, 1.3, 0.2, 0.2, 2.6)


URN = [(0, 0), (0.11, 0), (0.11, 0.05), (0.06, 0.08), (0.05, 0.14), (0.10, 0.2), (0.18, 0.3), (0.2, 0.4), (0.17, 0.47), (0.2, 0.5), (0.2, 0.54),
       (0.1, 0.57), (0.12, 0.62), (0.08, 0.68), (0.04, 0.72), (0.05, 0.76), (0, 0.82)]


def pillar(x, y, h=2.15, w=0.55, rz=0):
    """stucpijler met paneel, medaillon, kapstuk en vaas met bladkrans (Assepoesterkolom.jpg)"""
    M = TR(x, y, 0, rz)
    put("pijlers", "omlijsting", bz(-w / 2 - 0.05, w / 2 + 0.05, -w / 2 - 0.05, w / 2 + 0.05, 0, 0.35, 0.02), M)      # voet
    put("pijlers", "stuc", bz(-w / 2, w / 2, -w / 2, w / 2, 0.35, h - 0.25), M)
    t = 0.015    # paneel (lijst) op elke zijde
    for sx in (-1, 1):
        put("pijlers", "omlijsting", bz(min(sx * w / 2, sx * (w / 2 + t)), max(sx * w / 2, sx * (w / 2 + t)), -w / 2 + 0.1, w / 2 - 0.1, 0.55, h - 0.75), M)
        put("pijlers", "omlijsting", bz(-w / 2 + 0.1, w / 2 - 0.1, min(sx * w / 2, sx * (w / 2 + t)), max(sx * w / 2, sx * (w / 2 + t)), 0.55, h - 0.75), M)
    for (a, b) in ((0, -1), (0, 1), (-1, 0), (1, 0)):                                                                    # medaillon
        bm = blathe([(0, 0), (0.1, 0), (0.1, 0.03), (0.07, 0.045), (0, 0.045)], 12)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X" if a == 0 else "Y"), verts=bm.verts)
        if (a == 0 and b < 0) or (a < 0): bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi, 3, "Z"), verts=bm.verts)
        put("pijlers", "omlijsting", bm, M @ TR(a * (w / 2 + 0.015), b * (w / 2 + 0.015), h - 0.5))
    put("pijlers", "omlijsting", bz(-w / 2 - 0.06, w / 2 + 0.06, -w / 2 - 0.06, w / 2 + 0.06, h - 0.25, h - 0.15, 0.02), M)     # kapstuk
    put("pijlers", "omlijsting", bz(-w / 2 - 0.09, w / 2 + 0.09, -w / 2 - 0.09, w / 2 + 0.09, h - 0.15, h, 0.025), M)
    bm = blathe([(r * 1.15, z * 1.15) for r, z in URN], 14)
    for v in bm.verts:       # bladkrans: ribbels in de buik
        if 0.2 < v.co.z < 0.62:
            a = math.atan2(v.co.y, v.co.x); v.co.x *= 1 + 0.07 * math.cos(8 * a); v.co.y *= 1 + 0.07 * math.cos(8 * a)
    put("pijlers", "omlijsting", bm, M @ TR(0, 0, h))
    c = M @ Vector((0, 0, 0)); collr(c.x, c.y, (h + 0.9) / 2, w + 0.1, w + 0.1, h + 0.9, rz)


def iron_gate(p, q, h=1.9, open_deg=0.0):
    """smeedijzeren hekvleugel van p naar q (spijlen met speerpunt, boog bovenaan, krul) (tuinhek_oud.jpg)"""
    L = math.hypot(q[0] - p[0], q[1] - p[1]); a = math.atan2(q[1] - p[1], q[0] - p[0]) + math.radians(open_deg)
    M = TR(p[0], p[1], 0, math.degrees(a))
    for zz in (0.12, h * 0.5, h * 0.82):
        put("hekken", "ijzer", btube([(0.03, 0, zz), (L - 0.03, 0, zz)], 0.016, 5), M)
    n = max(3, int(L / 0.12))
    for i in range(n + 1):
        u = 0.03 + (L - 0.06) * i / n; top = h * 0.82 + 0.22 * math.sin(math.pi * u / L) ** 1.2 + 0.08
        put("hekken", "ijzer", btube([(u, 0, 0.05), (u, 0, top)], 0.011, 4), M)
        put("hekken", "ijzer", blathe([(0, 0), (0.025, 0.0), (0, 0.09)], 4), M @ TR(u, 0, top))
    pts = [(u, 0, h * 0.82 + 0.22 * math.sin(math.pi * u / L) ** 1.2) for u in [0.03 + (L - 0.06) * k / 12 for k in range(13)]]
    put("hekken", "ijzer", btube(pts, 0.016, 5), M)
    for k in range(2):     # krullen in het middenveld
        cx = L * (0.3 + 0.4 * k)
        put("hekken", "ijzer", btube([(cx + 0.12 * math.cos(t) * (1 - t / 9), 0, h * 0.66 + 0.12 * math.sin(t) * (1 - t / 9)) for t in [i * 0.5 for i in range(14)]], 0.009, 4), M)


def plank_gate(cx, cy, w, h=2.2, rz=0):
    """blauwgroene plankenpoort met boogtop, gehengen en bordje (Assepoes-dienstpoort.jpg); lokaal x langs de poort"""
    M = TR(cx, cy, 0, rz)
    x = -w / 2; i = 0
    while x < w / 2 - 0.01:
        pw = min(0.17, w / 2 - x)
        top = h - 0.22 + 0.22 * math.cos(math.pi * (x + pw / 2) / w) ** 2
        put("poort", "groen", bz(x, x + pw - 0.006, -0.035 - 0.006 * (i % 2), 0.035, 0.05, top), M)
        x += pw; i += 1
    for zz in (0.45, 1.15, 1.8):
        for sx in (-1, 1):
            put("poort", "ijzer", bz(sx * w / 2 - (0.7 if sx > 0 else 0), sx * w / 2 + (0.7 if sx < 0 else 0), -0.06, -0.035, zz - 0.035, zz + 0.035), M)
    put("poort", "papier", blathe([(0, 0), (0.17, 0), (0.17, 0.02), (0, 0.02)], 14), M @ TR(0, -0.05, 1.42) @ Matrix.Rotation(math.radians(90), 4, "X"))
    put("poort", "ijzer", bz(-0.04, 0.04, -0.07, -0.035, 0.95, 1.08), M)
    c = M @ Vector((0, 0, 0)); collr(c.x, c.y, h / 2, w, 0.15, h, rz)


def chest(x, y, rz=0, s=1.0, part="kisten"):
    """houten kist met bolle deksel en ijzerbeslag (dienstpoort/Boekloc)"""
    M = TR(x, y, 0, rz); w, d, h = 0.95 * s, 0.55 * s, 0.5 * s
    put(part, "kist", bz(-w / 2, w / 2, -d / 2, d / 2, 0, h, 0.01), M)
    bm = bmesh.new(); ring = []
    for k in range(9):
        a = math.pi * k / 8; ring.append((d / 2 * math.cos(a), h + 0.17 * s * math.sin(a)))
    prof = [(yy, zz) for yy, zz in ring]
    bm = bmesh.new()
    L = [bm.verts.new((-w / 2, yy, zz)) for yy, zz in prof]; Rr = [bm.verts.new((w / 2, yy, zz)) for yy, zz in prof]
    for i in range(len(prof) - 1): bm.faces.new((L[i], L[i + 1], Rr[i + 1], Rr[i]))
    bm.faces.new(L); bm.faces.new(Rr[::-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    put(part, "kist", bm, M)
    for u in (-w / 2 + 0.08, -0.05 * s, w / 2 - 0.08):
        put(part, "ijzer", bz(u - 0.025, u + 0.025, -d / 2 - 0.01, d / 2 + 0.01, 0, h + 0.01), M)
        put(part, "ijzer", btube([(u, d / 2 * math.cos(math.pi * k / 8) * 1.03, h + 0.17 * s * math.sin(math.pi * k / 8) * 1.03 + 0.005) for k in range(9)], 0.012, 4), M)
    c = M @ Vector((0, 0, 0)); collr(c.x, c.y, (h + 0.17 * s) / 2, w, d, h + 0.17 * s, rz)


PUMP = [(0, 0), (0.12, 0.01), (0.2, 0.06), (0.23, 0.13), (0.2, 0.21), (0.12, 0.25), (0.03, 0.26), (0, 0.26)]


def pumpkin(x, y, s=1.0, z=0.0):
    bm = blathe([(r * s, h * s) for r, h in PUMP], 12)
    for v in bm.verts:
        a = math.atan2(v.co.y, v.co.x); v.co.x *= 1 + 0.07 * math.cos(6 * a); v.co.y *= 1 + 0.07 * math.cos(6 * a)
    put("pompoenen", "pompoen", bm, TR(x, y, z))
    put("pompoenen", "balk", btube([(x, y, z + 0.24 * s), (x + 0.03, y, z + 0.32 * s)], 0.022 * s, 4))


def rock(x, y, r, h, seed):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    for v in bm.verts:
        q = v.co.copy(); d = 1 + 0.22 * noise.noise(q * 1.7 + Vector((seed, 0, 0))) + 0.08 * noise.noise(q * 4 + Vector((0, seed, 0)))
        v.co = Vector((q.x * r * d, q.y * r * d * 0.85, max(q.z, -0.25) * h * d))
    bmesh.ops.translate(bm, vec=(x, y, h * 0.2), verts=bm.verts); put("rotsen", "rots", bm)
    collr(x, y, h / 2, r * 1.4, r * 1.2, h)


def build(master):
    open_master(master); clear_owned()
    for n_, (c_, r_) in MATS.items(): material("MAT_" + n_, c_, r_)
    # ---------------- bestrating: klinkers op de binnenplaats, uitgangspad naar het parkpad (x 15.6) ----------------
    BED = (-2.65, 1.05, -4.25, -1.95)        # middenperk (tuin_nieuw.jpg): 3.7 x 2.3 m, voor de gaanderij
    bed_ring = [(BED[0], BED[2]), (BED[1], BED[2]), (BED[1], BED[3]), (BED[0], BED[3])]
    court = [(-6.95, -6.0), (7.2, -6.0), (7.2, -0.25), (5.95, -0.25), (5.95, 0.0), (3.25, 0.0), (3.25, 1.53), (-2.33, 1.53), (-2.33, 0.88), (-6.95, 0.88)]
    slab("bestrating", "klinker", court, 0.04, holes=[bed_ring])
    # aanloop door de haagopening (voetpad 729126648) en het uitgangspad (683933436) als lint met klinkers
    slab("bestrating", "klinker", ribbon(catmull([(-5.3, -14.0), (-5.0, -10.0), (-5.1, -7.4), (-5.2, -5.8)], 6), 3.0), 0.035)
    exitpath = catmull([(6.6, -4.4), (9.0, -4.3), (11.6, -3.4), (13.8, -3.3), (16.3, -3.9)], 8)
    slab("bestrating", "klinker", ribbon(exitpath, 2.6), 0.035)
    # opsluitband rond de binnenplaats aan de haagkant
    put("bestrating", "band", bz(-6.95, 7.2, -6.12, -6.0, 0.0, 0.07))
    # ---------------- middenperk: buxusrand, aarde, lantaarns op de hoeken ----------------
    slab("perk", "aarde", bed_ring, 0.06)
    e = 0.2
    haag([(BED[0] + e, BED[2] + e), (BED[1] - e, BED[2] + e), (BED[1] - e, BED[3] - e), (BED[0] + e, BED[3] - e), (BED[0] + e, BED[2] + e + 0.02)], 0.36, 0.42, "buxus")
    lantern_post(BED[0] - 0.25, BED[2] - 0.25); lantern_post(BED[1] + 0.25, BED[3] + 0.25)
    # ---------------- hagen (taxus, 2.6 m) langs OSM ----------------
    H = 2.6
    haag([(-3.77, -6.75), (10.49, -6.6)], 0.95, H)                                          # 1255787235
    haag([(10.49, -6.6), (11.2, -7.6)], 0.95, H)
    haag([(-7.21, -6.99), (-12.62, -7.26), (-13.71, 1.11), (-6.3, 1.05)], 0.95, H)         # 1255787236, doorgetrokken tot de vleugel (Daan: sloot niet aan)
    haag([(-7.25, -6.99), (-7.25, -1.75)], 0.85, H)                                         # scheiding binnenplaats / dienstplaatsje (inferred)
    haag([(7.6, -0.4), (7.6, 3.6), (5.6, 4.9)], 0.85, 2.2)                                  # tegen de zuidkant van het huis (inferred, sluit de binnenplaats af)
    # ---------------- tuiningang: pijlers met vaas + smeedijzeren hek (open) ----------------
    pillar(-6.75, -6.85); pillar(-4.15, -6.85)
    iron_gate((-6.43, -6.85), (-5.47, -6.85), open_deg=-80)
    iron_gate((-3.87 + 0.0, -6.85), (-4.83 + 0.0, -6.85), open_deg=80)
    # ---------------- dienstpoort naast de vleugel (dienstpoort.jpg: haag - poort - vleugelmuur) ----------------
    pillar(-7.25, -1.45, h=2.15, w=0.5)
    plank_gate(-7.15, -0.20, 2.05, rz=90)      # op x -7.15 van y -1.22 tot 0.82 (tot de hoek van de vleugel)
    # ---------------- grafje van de moeder (nieuwepoort-aankomst-2023.jpg): zerk met vleugels + lantaarn ----------------
    gx, gy = -2.6, -7.75
    put("grafje", "omlijsting", bz(gx - 0.55, gx + 0.55, gy - 0.6, gy + 0.6, 0, 0.18, 0.02))
    put("grafje", "omlijsting", bz(gx - 0.3, gx + 0.3, gy + 0.32, gy + 0.46, 0.18, 0.95, 0.02))
    put("grafje", "omlijsting", boutline(arc(gx, 0.95, 0.3, 0, 180, 10), gy + 0.32, 0.14))       # ronde kop
    for sx in (-1, 1):   # vleugels bovenop (zerk.jpg)
        wing = [(gx, 1.0), (gx + sx * 0.18, 1.18), (gx + sx * 0.42, 1.24), (gx + sx * 0.48, 1.14), (gx + sx * 0.36, 1.08), (gx + sx * 0.44, 1.02), (gx + sx * 0.3, 0.98), (gx + sx * 0.32, 0.92), (gx + sx * 0.12, 0.9)]
        if sx < 0: wing = wing[::-1]
        put("grafje", "omlijsting", boutline([(px, pz) for px, pz in wing], gy + 0.34, 0.1))
    put("grafje", "omlijsting", blathe([(0, 0), (0.12, 0), (0.12, 0.05), (0, 0.06)], 10), TR(gx, gy + 0.39, 1.0))
    lantern_head(gx + 0.22, gy - 0.25, 0.18, 0.8)
    collr(gx, gy, 0.6, 1.1, 1.2, 1.2)
    # ---------------- rekwisieten: kisten, boekstandaard, pompoenen, lantaarn op krul ----------------
    chest(-5.95, 0.42, rz=0)                    # links van de entree (Boekloc_nieuw)
    chest(-6.55, -0.9, rz=90, s=0.9)            # bij de dienstpoort (dienstpoort.jpg)
    chest(-1.6, 1.15, rz=0, s=0.85)             # onder het gordijn (front.jpg)
    put("kisten", "kist", bz(-0.9, -0.55, 1.2, 1.5, 0, 0.3, 0.01)); collr(-0.72, 1.35, 0.15, 0.35, 0.3, 0.3)
    bx_, by_ = -3.25, 0.5                       # boekstandaard rechts van de entree
    put("boek", "ijzer", btube([(bx_, by_, 0), (bx_, by_, 0.95)], 0.022, 6))
    for k in range(3):
        a = k * math.tau / 3 + 0.3
        put("boek", "ijzer", btube([(bx_, by_, 0.15), (bx_ + 0.22 * math.cos(a), by_ + 0.22 * math.sin(a), 0.0)], 0.016, 4))
    put("boek", "goud", bz(bx_ - 0.3, bx_ + 0.3, by_ - 0.2, by_ + 0.2, 0.95, 0.98), TR(bx_, by_, 0.97) @ Matrix.Rotation(math.radians(-25), 4, "X") @ TR(-bx_, -by_, -0.97))
    for sx in (-1, 1):
        put("boek", "papier", bz(bx_ + sx * 0.005, bx_ + sx * 0.27, by_ - 0.17, by_ + 0.17, 0.98, 1.0), TR(bx_, by_, 0.97) @ Matrix.Rotation(math.radians(-25), 4, "X") @ TR(-bx_, -by_, -0.97))
    collr(bx_, by_, 0.5, 0.6, 0.45, 1.0)
    for (qx, qy, sc) in ((0.3, 1.15, 1.0), (0.65, 1.2, 0.8), (0.05, 1.3, 0.7), (3.75, -0.25, 1.05), (4.0, -0.05, 0.8), (2.95, 1.25, 0.9)):
        pumpkin(qx, qy, sc, 0.04)
    curl_lantern(1.25, 1.2, rz=180)
    # ---------------- uitgang: rotsjes, mand, galgje-lantaarn, stucboog in het parkhek (D6z) ----------------
    for k, (rx, ry, rr, rh) in enumerate(((8.4, -5.9, 0.45, 0.35), (9.3, -6.1, 0.35, 0.28), (10.7, -2.2, 0.55, 0.45), (11.4, -1.6, 0.4, 0.3),
                                          (12.6, -5.4, 0.5, 0.4), (13.4, -5.7, 0.35, 0.25), (9.6, -2.4, 0.3, 0.22), (14.2, -1.9, 0.45, 0.35))):
        rock(rx, ry, rr, rh, k * 7.3)
    put("mand", "mand", blathe([(0, 0), (0.18, 0), (0.24, 0.22), (0.25, 0.26), (0.21, 0.26), (0.2, 0.04), (0, 0.04)], 14), TR(10.1, -2.75, 0))
    put("mand", "mand", btube([(10.1 + 0.22 * math.cos(math.pi * k / 10), -2.75, 0.26 + 0.18 * math.sin(math.pi * k / 10)) for k in range(11)], 0.012, 4))
    gallows_lantern(9.4, -1.9, rz=-100)
    # stucboog in het hek op x 15.6 (D6z: dikke gepleisterde boog), hek aan weerskanten (1255787242)
    ax, ay = 15.6, -3.9; AW, AH = 1.9, 2.55
    arch_ = arch_pts(0, 0, AW, AH, 14)
    outer = [(-AW / 2 - 0.55, 0), (-AW / 2 - 0.55, AH + 0.45), (AW / 2 + 0.55, AH + 0.45), (AW / 2 + 0.55, 0)]
    MA = TR(ax, ay, 0, 90)
    put("uitgangsboog", "stuc", boutline(outer + arch_[::-1], -0.3, 0.6), MA)     # muur met boogopening (U-vorm)
    put("uitgangsboog", "omlijsting", bz(-AW / 2 - 0.62, AW / 2 + 0.62, -0.36, 0.36, AH + 0.45, AH + 0.58, 0.02), MA)
    put("uitgangsboog", "omlijsting", band(arch_, 0.1, -0.33, 0.66), MA)
    for u in (-AW / 2 - 0.28, AW / 2 + 0.28):
        c = MA @ Vector((u, 0, 0)); collr(c.x, c.y, 1.5, 0.6, 0.56, 3.0)
    for (p_, q_) in (((15.62, -5.4), (15.66, -13.26)), ((15.57, -2.4), (15.52, 2.02))):
        L = math.hypot(q_[0] - p_[0], q_[1] - p_[1]); n = int(L / 2.0) + 1
        for i in range(n):
            a_ = (p_[0] + (q_[0] - p_[0]) * i / n, p_[1] + (q_[1] - p_[1]) * i / n); b_ = (p_[0] + (q_[0] - p_[0]) * (i + 1) / n, p_[1] + (q_[1] - p_[1]) * (i + 1) / n)
            iron_gate(a_, b_, h=1.25)
            put("hekken", "ijzer", blathe([(0, 0), (0.05, 0), (0.04, 1.45), (0.07, 1.5), (0, 1.62)], 8), TR(a_[0], a_[1], 0))
        collr((p_[0] + q_[0]) / 2, (p_[1] + q_[1]) / 2, 0.75, 0.12, L, 1.5)
    # ---------------- objecten ----------------
    n = 0; tris = 0
    for (part, mat), bm in PARTS.items():
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        ob = new_mesh_object(f"AO_{part}__{mat}", bm, "OMGEVING"); assign(ob, bpy.data.materials["MAT_" + mat])
        n += 1; tris += sum(len(p.vertices) - 2 for p in ob.data.polygons)
    out = os.path.join(HERE, "..", "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLLR, "lamps": [[round(v, 2) for v in l] for l in LAMPS],
               "perk": bed_ring, "binnenplaats": court}, open(os.path.join(out, "omgeving_extra.json"), "w"))
    save_master(master); log("objects", n, "tris~", tris, "colliders", len(COLLR), "lamps", len(LAMPS))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
