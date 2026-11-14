"""03_huisje Repelsteeltje (1998, Ton van de Ven): gestuct huisje met boomstronk op het dak, wortels om natuurstenen hoeken, gebogen
houten hoed boven de deurgevel, kijkvenster met blauwgroene luiken, schoorsteen met pijp, tuintje met bolderkar, hekje, flagstone-pad.
Naar Repelsteeltje_exterieur, Repelsteeltjebouw-1998-01/-03 (persoon 1.8 m) en OSM 55424159 (5.8 x 4.1 m).
Modelframe: oorsprong = OSM-zwaartepunt, x = noordwest (rechts voor de kijker op het pad), y = zuidwest (de diepte in), z op.
Voorkant = lange zijde naar het pad = -Y. Gebruik: Blender -b -P 03_huisje.py -- --master RS_huisje_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
RNG = random.Random(1998)
MATS = {"stuc": ((0.86, 0.84, 0.78, 1), 0.9), "natuursteen": ((0.55, 0.52, 0.46, 1), 0.95), "lei": ((0.32, 0.29, 0.26, 1), 0.85),
        "hout": ((0.22, 0.15, 0.1, 1), 0.8), "schors": ((0.42, 0.32, 0.22, 1), 0.95), "blauwgroen": ((0.18, 0.36, 0.38, 1), 0.6),
        "venster": ((0.05, 0.06, 0.07, 1), 0.3), "glasoranje": ((1.0, 0.62, 0.25, 1), 0.2), "ijzer": ((0.05, 0.05, 0.05, 1), 0.45),
        "zink": ((0.62, 0.64, 0.64, 1), 0.4), "deurgroen": ((0.12, 0.28, 0.22, 1), 0.6), "flagstone": ((0.62, 0.5, 0.46, 1), 0.9),
        "papier": ((0.92, 0.86, 0.7, 1), 0.9), "rood": ((0.55, 0.12, 0.08, 1), 0.6), "baksteen": ((0.6, 0.38, 0.28, 1), 0.9), "lei2": ((0.4, 0.34, 0.3, 1), 0.85), "mos": ((0.3, 0.38, 0.16, 1), 0.95), "gordijn": ((0.85, 0.8, 0.66, 1), 0.9), "klimop": ((0.14, 0.26, 0.1, 1), 0.8), "brandhout": ((0.45, 0.32, 0.2, 1), 0.9)}
X0, X1, Y0, Y1 = -2.33, 3.49, -1.88, 2.2          # OSM-omtrek in het modelframe
EAVE, RIDGE = 2.5, 4.6               # overlay Repelsteeltje_exterieur: goot ~15% hoger dan eerst geschat
YC = (Y0 + Y1) / 2


def taps(points, r0, r1, n_per=3):
    """dikke, aflopende wortel/tak: bollen langs een polylijn (organisch samengesmolten)"""
    out = bmesh.new(); P = [Vector(p) for p in points]; tot = sum((b - a).length for a, b in zip(P, P[1:])); acc = 0.0
    for a, b in zip(P, P[1:]):
        L = (b - a).length; k = max(2, int(L / 0.12))
        for i in range(k):
            t = i / k; p = a.lerp(b, t); r = r0 + (r1 - r0) * (acc + L * t) / tot
            s = ell(p, (r, r, r), 8, 6); me_ = bpy.data.meshes.new("_t"); s.to_mesh(me_); s.free(); out.from_mesh(me_); bpy.data.meshes.remove(me_)
        acc += L
    return out


def keien(x, y, z0, z1, breed=0.9, seed=1):
    """losse ronde/hoekige natuurstenen keien gestapeld op een hoek (Repelsteeltje_exterieur): elk een vervormde bol met eigen vorm"""
    r = random.Random(seed); bm = bmesh.new(); z = z0
    while z < z1:
        s_ = r.uniform(0.17, 0.28); n = max(2, int(breed / (s_ * 1.7)))
        for i in range(n):
            px = x + r.uniform(-breed / 2, breed / 2); py = y + r.uniform(-breed / 2, breed / 2)
            st = ell((0, 0, 0), (s_ * r.uniform(1.0, 1.45), s_ * r.uniform(0.85, 1.15), s_ * r.uniform(0.62, 0.8)), 10, 7)
            for v in st.verts:                                                                  # breukvlakjes + bobbels
                v.co *= 1 + 0.12 * math.sin(v.co.x * 17 + seed) * math.cos(v.co.y * 13) + r.uniform(-0.03, 0.03)
                if v.co.z < -s_ * 0.45: v.co.z = -s_ * 0.45
            bmesh.ops.rotate(st, verts=st.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(r.uniform(0, math.tau), 3, "Z") @ Matrix.Rotation(r.uniform(-0.25, 0.25), 3, "X"))
            bmesh.ops.translate(st, vec=(px, py, z + s_ * 0.55), verts=st.verts)
            me_ = bpy.data.meshes.new("_t"); st.to_mesh(me_); st.free(); bm.from_mesh(me_); bpy.data.meshes.remove(me_)
        z += s_ * 1.05
    return bm

# ---- dakbulten: de leien zwellen op over de wortels en rond de stronk (Repelsteeltje_exterieur, bouw-03) ----
TXg, TYg = 0.15, (Y0 + Y1) / 2 + 0.15
OVRg = 0.38
WORT_XY = [(TXg - 0.7, TYg - 0.65, X0 + 0.55, Y0 - OVRg + 0.05), (TXg + 0.7, TYg - 0.6, X1 - 0.45, Y0 - OVRg + 0.05),
           (TXg - 0.6, TYg + 0.65, X0 + 0.65, Y1 + OVRg - 0.05), (TXg + 0.7, TYg + 0.6, X1 - 0.5, Y1 + OVRg - 0.05),
           (TXg - 0.9, TYg - 0.1, TXg - 1.85, TYg - 0.15), (TXg + 0.9, TYg + 0.2, TXg + 1.75, TYg + 0.35), (TXg - 0.1, TYg - 0.9, TXg - 0.25, TYg - 1.6)]
def wortel_xy(i, t):
    x0, y0, x1, y1 = WORT_XY[i]
    return x0 + (x1 - x0) * t + (0.25 * math.sin(t * 5.0) * (1 - t) if i < 4 else 0.0), y0 + (y1 - y0) * t
HOOD_CP = [((Y0 + Y1) - y_, z_) for (y_, z_) in [(Y0 - 0.55, 1.25), (Y0 - 0.25, 2.65), (Y0 + 0.5, 3.85), ((Y0 + Y1) / 2 - 0.3, 4.7), ((Y0 + Y1) / 2 + 0.6, 4.9), (Y1 - 0.4, 4.4), (Y1 + 0.2, 3.3)]][::-1]
def hoodz(y):
    pts = sorted(HOOD_CP)
    if y <= pts[0][0] or y >= pts[-1][0]: return None
    for (ya, za), (yb, zb) in zip(pts, pts[1:]):
        if ya <= y <= yb: return za + (zb - za) * (y - ya) / (yb - ya)
def basisz(y):
    ys = Y0 - OVRg if y < (Y0 + Y1) / 2 else Y1 + OVRg
    t = max(0.0, min(1.0, (y - ys) / ((Y0 + Y1) / 2 - ys))); return EAVE - 0.2 + (RIDGE - 0.02 - (EAVE - 0.2)) * t
def dakbult(x, y):
    """extra hoogte van het dakvlak: bult langs elke wortel (smaller/lager naar de goot), heuvel rond de stronk, lichte golving"""
    h = 0.0
    for i in range(len(WORT_XY)):
        best = 9.0; bt = 0.0
        for k in range(21):
            t = k / 20; wx, wy = wortel_xy(i, t); d = math.hypot(x - wx, y - wy)
            if d < best: best, bt = d, t
        amp = (0.24 if i < 4 else 0.14) * (1 - 0.6 * bt); wid = (0.42 if i < 4 else 0.3) * (1 - 0.35 * bt)
        h = max(h, amp * math.exp(-(best / wid) ** 2))
    ds = math.hypot(x - TXg, y - TYg); h = max(h, 0.42 * math.exp(-(max(0.0, ds - 0.9) / 0.65) ** 2))
    hz = hoodz(y)                                                                                     # links loopt het dak op naar de hoed (exterieur)
    if hz is not None and x < X0 + 1.6:
        f = max(0.0, min(1.0, (X0 + 1.6 - x) / 1.45)); f = f * f * (3 - 2 * f)
        h = max(h, (hz - 0.12 - basisz(y)) * f)
    return h + 0.045 * math.sin(x * 1.7 + y * 0.9) * math.sin(y * 2.3 - x * 0.4)

def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ================= muren: bobbelig gestuct, iets uitlopend aan de voet =================
    wb = bmesh.new(); bmesh.ops.create_cube(wb, size=1.0)
    for v in wb.verts:
        v.co.x = X0 + 0.1 + (v.co.x + 0.5) * (X1 - X0 - 0.2); v.co.y = Y0 + 0.1 + (v.co.y + 0.5) * (Y1 - Y0 - 0.2); v.co.z = -0.1 + (v.co.z + 0.5) * (EAVE + 0.1)
    put("muren", "stuc", organisch(wb, 0.06, 4, 0.6, 0.05, 1.0, 0.18))
    gp = [(Y0 + 0.1, EAVE - 0.05), (Y1 - 0.1, EAVE - 0.05), (YC, RIDGE - 0.1)]                                # kopgevels tot onder de nok
    for xg in (X0 + 0.1, X1 - 0.1):
        put("muren", "stuc", organisch(prism_x(gp, xg - 0.12, xg + 0.12), 0.06, 3, 0.5, 0.03, 1.0, 0.2))
    coll_box((X0 + X1) / 2, YC, 1.1, X1 - X0, Y1 - Y0, 2.2)
    # baksteen die door het stuc piept (scheuren) op de voorgevel en de deurgevel
    for (x, z) in ((-0.9, 0.5), (2.3, 1.4), (1.9, 0.35), (0.1, 1.85)):
        for i in range(5):
            put("muren", "baksteen", bz(x + (i % 2) * 0.11 - 0.1, x + (i % 2) * 0.11 + 0.1, Y0 + 0.06, Y0 + 0.09, z + i * 0.07, z + i * 0.07 + 0.055, 0.005))
    # stenen plint onder het kijkvenster (exterieur: baksteen/natuursteen band onderaan de voorgevel)
    put("muren", "natuursteen", organisch(bz(X0 + 0.6, X1 - 0.6, Y0 + 0.02, Y0 + 0.16, -0.1, 0.62, 0.03), 0.05, 2, 0.4, 0.03, 1.5, 0.3))
    # ================= natuurstenen keienhoeken =================
    for k, (x, y) in enumerate(((X0 + 0.2, Y0 + 0.2), (X1 - 0.2, Y0 + 0.2), (X0 + 0.2, Y1 - 0.2), (X1 - 0.2, Y1 - 0.2))):
        put("keien", "natuursteen", keien(x, y, -0.1, EAVE - 0.1, 0.85, seed=k + 3))
    put("keien", "natuursteen", keien(-1.3, Y0 + 0.15, -0.1, 0.6, 1.1, seed=11))
    # ================= leien dak met golvende goot, mos =================
    over = 0.38
    prof = [(Y0 - over, EAVE - 0.24), (YC, RIDGE - 0.06), (Y1 + over, EAVE - 0.24), (Y1 + over, EAVE - 0.36), (YC, RIDGE - 0.2), (Y0 - over, EAVE - 0.36)]
    put("dak", "hout", prism_x(prof, X0 + 0.2, X1 + over))                                              # donkere onderlaag/dakbeschot
    rng = random.Random(7)
    for side in (-1, 1):                                                                                 # losse leitjes in verspringende rijen
        ye = Y0 - over if side < 0 else Y1 + over
        P0 = Vector((0, ye, EAVE - 0.2)); P1 = Vector((0, YC, RIDGE - 0.02))
        es = (P1 - P0); L = es.length; es.normalize(); ex = Vector((1, 0, 0)); nrm = ex.cross(es) if side < 0 else es.cross(ex)
        rows = int(L / 0.15)
        for r in range(rows):
            sv = r * 0.15 + 0.1; xx = X0 + 0.2 + (0.1 if r % 2 else 0.0)
            while xx < X1 + over - 0.05:
                w = rng.uniform(0.16, 0.24)
                c = P0 + es * sv
                c = Vector((xx + w / 2, c.y, c.z)) + nrm * (0.035 + rng.uniform(0, 0.012))
                c.z += 0.07 * math.sin((xx + w / 2) * 2.1) * max(0.0, 1 - sv / 1.2) - 0.03 * max(0.0, 1 - sv / 1.2)   # golvende, doorzakkende goot
                c.z += dakbult(c.x, c.y)                                                              # bulten over wortels en rond de stronk
                sl = bmesh.new(); bmesh.ops.create_cube(sl, size=1.0); bmesh.ops.scale(sl, vec=(w - 0.015, 0.27, 0.02), verts=sl.verts)
                tilt = Matrix.Rotation(math.radians(6 + rng.uniform(-2, 3)), 4, "X") @ Matrix.Rotation(math.radians(rng.uniform(-4, 4)), 4, "Z")
                basis = Matrix(((ex.x, es.x * -side if False else (es.x), nrm.x, 0), (ex.y, es.y, nrm.y, 0), (ex.z, es.z, nrm.z, 0), (0, 0, 0, 1)))
                bmesh.ops.transform(sl, matrix=Matrix.Translation(c) @ basis @ tilt, verts=sl.verts)
                put("dak", "lei" if rng.random() < 0.82 else "lei2", sl)
                xx += w
        for k in range(30):                                                                              # mospollen (Repelsteeltje_exterieur: dik groen mos)
            sv = rng.uniform(0.2, L - 0.2); xx = rng.uniform(X0 + 0.4, X1 + 0.2)
            near = abs(xx - 0.15) < 1.6 and sv > L * 0.4
            if rng.random() < (0.9 if near else 0.45):
                c = P0 + es * sv; c = Vector((xx, c.y, c.z)) + nrm * 0.07; c.z += dakbult(c.x, c.y)
                for j in range(3):                                                                   # onregelmatige pol: 3 platte lobben
                    d_ = Vector((rng.uniform(-0.25, 0.25), 0, 0)) + es * rng.uniform(-0.15, 0.15)
                    put("dak", "mos", ell(c + d_ - nrm * 0.02, (rng.uniform(0.18, 0.4), rng.uniform(0.14, 0.3), 0.07), 10, 6))
    put("dak", "lei", btube([(X0 + 0.15, YC, RIDGE + 0.02), (X1 + over, YC, RIDGE + 0.02)], 0.08, 8))     # nokvorst
    # ================= gebogen houten hoed boven de deurgevel (bouw-1998-01) =================
    # vloeiende curve (Catmull-Rom door de controlepunten), laag eind links voor wie naar de deur kijkt (bouw-01)
    CP = [((Y0 + Y1) - y_, z_) for (y_, z_) in [(Y0 - 0.55, 1.25), (Y0 - 0.25, 2.65), (Y0 + 0.5, 3.85), (YC - 0.3, 4.7), (YC + 0.6, 4.9), (Y1 - 0.4, 4.4), (Y1 + 0.2, 3.3)]][::-1]
    def cr(p0, p1, p2, p3, t):
        return tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in range(2))
    ext = [CP[0]] + CP + [CP[-1]]; C = []
    for i in range(1, len(ext) - 2):
        for k in range(8): C.append(cr(ext[i - 1], ext[i], ext[i + 1], ext[i + 2], k / 8))
    C.append(CP[-1])
    def nrm_at(i):
        a_ = Vector(C[max(i - 1, 0)]); b_ = Vector(C[min(i + 1, len(C) - 1)]); t = (b_ - a_).normalized(); return Vector((-t.y, t.x)) if False else Vector((t.y, -t.x))
    XA, XB = X0 - 0.78, X0 + 0.32
    nb = 6; bw = (XB - XA) / nb
    for j in range(nb):                                                                                  # gebogen planken (onderkant zichtbaar, voegen ertussen)
        xa, xb = XA + j * bw + 0.012, XA + (j + 1) * bw - 0.012
        hood = bmesh.new(); top_ = []; bot_ = []
        for i, (cy_, cz_) in enumerate(C):
            nn = nrm_at(i)
            top_.append((hood.verts.new((xa, cy_, cz_)), hood.verts.new((xb, cy_, cz_))))
            bot_.append((hood.verts.new((xa, cy_ + nn.x * 0.07, cz_ + nn.y * 0.07)), hood.verts.new((xb, cy_ + nn.x * 0.07, cz_ + nn.y * 0.07))))
        for i in range(len(C) - 1):
            hood.faces.new((top_[i][0], top_[i + 1][0], top_[i + 1][1], top_[i][1])); hood.faces.new((bot_[i][1], bot_[i + 1][1], bot_[i + 1][0], bot_[i][0]))
            hood.faces.new((top_[i][0], bot_[i][0], bot_[i + 1][0], top_[i + 1][0])); hood.faces.new((top_[i][1], top_[i + 1][1], bot_[i + 1][1], bot_[i][1]))
        for i in (0, len(C) - 1): hood.faces.new((top_[i][0], top_[i][1], bot_[i][1], bot_[i][0]))
        bmesh.ops.recalc_face_normals(hood, faces=hood.faces); put("hoed", "hout", hood)
    put("hoed", "hout", btube([(XA - 0.04, cy_, cz_) for (cy_, cz_) in C], 0.1, 10))                    # dikke afgeronde windveer langs de rand (bouw-01)
    put("hoed", "hout", btube([(XB + 0.02, cy_, cz_) for (cy_, cz_) in C[2:-2]], 0.06, 8))
    top_i = max(range(len(C)), key=lambda i: C[i][1]); ty_, tz_ = C[top_i]                                # uitstekende balkkop bij de top (bouw-01)
    put("hoed", "hout", btube([(XA - 0.35, ty_ + 0.35, tz_ + 0.12), (XA + 0.2, ty_ + 0.05, tz_ - 0.05), (XB, ty_ - 0.15, tz_ - 0.15)], 0.12, 8))
    rng2 = random.Random(11)                                                                             # leitjes over de hoed (het dak loopt erover door)
    acc_s = 0.0
    for i in range(len(C) - 1):
        seg = math.hypot(C[i + 1][0] - C[i][0], C[i + 1][1] - C[i][1]); acc_s += seg
        if acc_s < 0.15: continue
        acc_s = 0.0
        cy_, cz_ = C[i]; nn = nrm_at(i); tdir = Vector((C[i + 1][0] - cy_, C[i + 1][1] - cz_)).normalized()
        xx = XA + 0.05 + (0.08 if i % 2 else 0.0)
        while xx < XB - 0.08:
            w = rng2.uniform(0.16, 0.22)
            sl = bmesh.new(); bmesh.ops.create_cube(sl, size=1.0); bmesh.ops.scale(sl, vec=(w - 0.015, 0.25, 0.02), verts=sl.verts)
            ey = Vector((0, tdir.x, tdir.y)); ez = Vector((0, -nn.x, -nn.y)); ex = Vector((1, 0, 0))
            basis = Matrix(((ex.x, ey.x, ez.x, 0), (ex.y, ey.y, ez.y, 0), (ex.z, ey.z, ez.z, 0), (0, 0, 0, 1)))
            cpos = Vector((xx + w / 2, cy_, cz_)) + ez * 0.03
            bmesh.ops.transform(sl, matrix=Matrix.Translation(cpos) @ basis @ Matrix.Rotation(math.radians(rng2.uniform(-5, 5)), 4, "Z"), verts=sl.verts)
            put("dak", "lei" if rng2.random() < 0.8 else "lei2", sl); xx += w
    # gevelveld dat precies tot onder de hoed doorloopt (geen kier tussen muur en hoed)
    def onder(i): nn = nrm_at(i); return (C[i][0] + nn.x * 0.06, C[i][1] + nn.y * 0.06)
    lo = [onder(i) for i in range(len(C))]
    binnen = sorted([p_ for p_ in lo if Y0 + 0.08 < p_[0] < Y1 - 0.08])
    def curvez(y):
        q = sorted(lo)
        for (ya, za), (yb, zb) in zip(q, q[1:]):
            if ya <= y <= yb: return za + (zb - za) * (y - ya) / max(yb - ya, 1e-6)
        return EAVE
    gw = [(Y0 + 0.08, EAVE - 0.3), (Y0 + 0.08, curvez(Y0 + 0.08))] + binnen + [(Y1 - 0.08, curvez(Y1 - 0.08)), (Y1 - 0.08, EAVE - 0.3)]
    gb_ = prism_x(gw, X0 - 0.06, X0 + 0.3); bmesh.ops.triangulate(gb_, faces=[f for f in gb_.faces if len(f.verts) > 4], ngon_method="EAR_CLIP")
    put("muren", "stuc", organisch(gb_, 0.05, 2, 0.4, 0.02, 1.0, 0.25))
    for kant in (0, 1):                                                                                   # steunberen onder de lage hoedpoten (bouw-01: stuc + keien tot de grond)
        poot = [p_ for p_ in lo if (p_[0] <= Y0 + 0.12 if kant == 0 else p_[0] >= Y1 - 0.12)]
        if len(poot) < 2: continue
        poot = sorted(poot)
        yin = Y0 + 0.12 if kant == 0 else Y1 - 0.12
        poly = ([(poot[0][0], 0.0)] + poot + [(yin, 0.0)]) if kant == 0 else ([(yin, 0.0)] + poot + [(poot[-1][0], 0.0)])
        sb = prism_x(poly, XA + 0.12, X0 + 0.35); bmesh.ops.triangulate(sb, faces=[f for f in sb.faces if len(f.verts) > 4], ngon_method="EAR_CLIP")
        put("muren", "stuc", organisch(sb, 0.06, 3, 0.5, 0.04, 1.2, 0.25))
        ym = sum(p_[0] for p_ in poot) / len(poot)
        put("keien", "natuursteen", keien((XA + X0) / 2 + 0.1, ym, -0.1, min(1.4, max(p_[1] for p_ in poot) - 0.3), 0.7, seed=50 + kant))
        coll_box((XA + X0) / 2 + 0.1, ym, 1.0, X0 + 0.35 - XA - 0.12, max(0.4, abs(poot[-1][0] - poot[0][0])), 2.0)
    # deur (rondboog) + rond raampje met stenen bloem
    Md = Matrix.Translation((X0 + 0.02, YC, 0)) @ Matrix.Rotation(math.radians(90), 4, "Z")
    put("deur", "venster", boutline(arch_pts(0, -0.02, 0.9, 1.95, 10), -0.12, 0.1), Md)                 # donkere dagkant
    for i in range(5):                                                                                   # 5 verticale planken met voeg
        x0_ = -0.41 + i * 0.164
        pl = [(x, z) for (x, z) in arch_pts(0, -0.02, 0.82, 1.88, 16) if x0_ - 1e-6 <= x <= x0_ + 0.156 + 1e-6]
        top = max([z for _, z in pl] + [1.4])
        put("deur", "deurgroen", bz(x0_ + 0.006, x0_ + 0.158, -0.1, -0.06, -0.02, top - 0.03, 0.006), Md)
    for zz in (0.35, 1.45):                                                                              # smeedijzeren hengsels
        put("deur", "ijzer", bz(-0.4, 0.15, -0.12, -0.1, zz - 0.035, zz + 0.035), Md)
        put("deur", "ijzer", ell((0.15, -0.11, zz), (0.06, 0.012, 0.05), 6, 4), Md)
    put("deur", "ijzer", btube([(0.24 + 0.06 * math.cos(t), -0.13, 0.95 + 0.06 * math.sin(t)) for t in [i * math.tau / 12 for i in range(13)]], 0.01, 5), Md)  # klopring
    for i, (x, z) in enumerate(arch_pts(0, -0.02, 1.02, 2.05, 9)[1:-1]):                                 # natuurstenen omlijsting (bouw-01: stenen rond de deur)
        if i % 1 == 0: put("deur", "natuursteen", ell((x * 1.08, -0.04, z + 0.04), (0.1, 0.09, 0.1 + 0.03 * (i % 2)), 8, 6), Md)
    for z in (0.15, 0.5, 0.85, 1.2):
        for sx in (-1, 1): put("deur", "natuursteen", ell((sx * 0.56, -0.04, z), (0.1 + 0.02 * (z > 0.6), 0.09, 0.14), 8, 6), Md)
    put("deur", "natuursteen", organisch(bz(-0.6, 0.6, 0.0, 0.45, -0.12, 0.1, 0.04), 0.04, 2, 0.4, 0.02, 1.5, 0.3), Md)      # stoepsteen
    rw = [(0.22 * math.cos(a), 3.25 + 0.22 * math.sin(a)) for a in [i * math.tau / 16 for i in range(16)]]
    put("deur", "venster", boutline(rw, 0.1, 0.04), Md)
    put("deur", "ijzer", btube([(0.2 * math.cos(a), 0.15, 3.25 + 0.2 * math.sin(a)) for a in [i * math.tau / 16 for i in range(17)]], 0.025, 5), Md)
    for k in range(6):
        a = k * math.tau / 6 + 0.3
        put("deur", "stuc", ell((0.42 * math.cos(a), 0.12, 3.25 + 0.42 * math.sin(a)), (0.17, 0.06, 0.15), 8, 6), Md)
    put("deur", "venster", bz(-0.95, -0.55, -0.1, -0.06, 0.9, 1.35), Md)                                     # klein zijraampje
    # ================= kijkvenster met blauwgroene kozijnen en luiken (exterieur) =================
    WX, WW, WZ0, WZ1 = 0.15, 1.5, 0.95, 2.0          # overlay: venster links van het midden, breder
    put("raam", "venster", bz(WX - WW / 2, WX + WW / 2, Y0 + 0.04, Y0 + 0.09, WZ0, WZ1))
    put("raam", "venster", bz(WX - WW / 2 - 0.02, WX + WW / 2 + 0.02, Y0 + 0.02, Y0 + 0.2, WZ0 - 0.02, WZ1 + 0.02) if False else bmesh.new())
    for (x0_, x1_, z0_, z1_) in ((WX - WW / 2 - 0.08, WX + WW / 2 + 0.08, WZ0 - 0.08, WZ0), (WX - WW / 2 - 0.08, WX + WW / 2 + 0.08, WZ1, WZ1 + 0.09),
                                  (WX - WW / 2 - 0.08, WX - WW / 2, WZ0, WZ1), (WX + WW / 2, WX + WW / 2 + 0.08, WZ0, WZ1), (WX - 0.04, WX + 0.04, WZ0, WZ1)):
        put("raam", "blauwgroen", bz(x0_, x1_, Y0 - 0.03, Y0 + 0.05, z0_, z1_, 0.008))
    for side in (-1, 1):                                                                                  # 2 ramen x 3x3 ruitjes met roeden
        xa, xb = (WX - WW / 2, WX - 0.04) if side < 0 else (WX + 0.04, WX + WW / 2)
        for i in (1, 2): put("raam", "blauwgroen", bz(xa + (xb - xa) * i / 3 - 0.012, xa + (xb - xa) * i / 3 + 0.012, Y0 + 0.0, Y0 + 0.05, WZ0, WZ1))
        for i in (1, 2): put("raam", "blauwgroen", bz(xa, xb, Y0 + 0.0, Y0 + 0.05, WZ0 + (WZ1 - WZ0) * i / 3 - 0.012, WZ0 + (WZ1 - WZ0) * i / 3 + 0.012))
    put("raam", "gordijn", bz(WX - WW / 2 + 0.02, WX - WW / 2 + 0.3, Y0 + 0.1, Y0 + 0.13, WZ0 + 0.05, WZ1 - 0.02))
    for sx in (-1, 1):                                                                                   # luiken: 4 planken, Z-schoor, hengsels, hartje
        xa = WX + sx * (WW / 2 + 0.08 + 0.32)
        for i in range(4):
            x0_ = xa - 0.3 + i * 0.15
            put("raam", "blauwgroen", bz(x0_ + 0.005, x0_ + 0.145, Y0 - 0.08, Y0 - 0.04, WZ0 - 0.06, WZ1 + 0.06, 0.006))
        for zz in (WZ0 + 0.15, WZ1 - 0.15):
            put("raam", "blauwgroen", bz(xa - 0.29, xa + 0.29, Y0 - 0.1, Y0 - 0.08, zz - 0.05, zz + 0.05))
            put("raam", "ijzer", bz(xa - sx * 0.3 - 0.02, xa - sx * 0.05, Y0 - 0.11, Y0 - 0.1, zz - 0.02, zz + 0.02))
        put("raam", "blauwgroen", btube([(xa - 0.25, Y0 - 0.095, WZ0 + 0.2), (xa + 0.25, Y0 - 0.095, WZ1 - 0.2)], 0.025, 5))
        put("raam", "venster", boutline([(xa + 0.06 * math.sin(t) ** 3, WZ1 - 0.32 + 0.05 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16)
                                         for t in [i * math.tau / 14 for i in range(14)]], Y0 - 0.115, 0.01))
    put("raam", "hout", bz(WX - WW / 2 - 0.12, WX + WW / 2 + 0.12, Y0 - 0.16, Y0 + 0.05, WZ0 - 0.13, WZ0 - 0.06, 0.01))   # vensterbank
    Mz = Matrix.Translation((X1 - 0.02, YC - 0.6, 0)) @ Matrix.Rotation(math.radians(-90), 4, "Z")
    put("raam", "venster", bz(-0.3, 0.3, -0.06, 0.0, 1.1, 1.75), Mz)
    for (a_, b_, c_, d_) in ((-0.36, 0.36, 1.03, 1.1), (-0.36, 0.36, 1.75, 1.82), (-0.36, -0.3, 1.1, 1.75), (0.3, 0.36, 1.1, 1.75), (-0.025, 0.025, 1.1, 1.75)):
        put("raam", "blauwgroen", bz(a_, b_, -0.09, -0.02, c_, d_), Mz)
    # ================= schoorsteen met pijp (rook in Roblox) =================
    SX, SY = X1 - 0.55, YC + 0.75
    put("schoorsteen", "stuc", organisch(blathe([(0, 3.0), (0.55, 3.0), (0.45, 4.1), (0.32, 5.0), (0, 5.0)], 10), 0.05, 3, 0.5, 0.02, 1.0, 0.25), TR(SX, SY))
    put("schoorsteen", "zink", btube([(SX, SY, 4.95), (SX, SY, 5.75)], 0.07, 10))
    put("schoorsteen", "zink", blathe([(0, 5.73), (0.2, 5.77), (0.18, 5.82), (0, 5.89)], 12), TR(SX, SY))
    json_rook = [SX, SY, 5.9]
    # ================= boomstronk op het dak met wortels om de hoeken =================
    TX, TY = 0.15, YC + 0.15
    st = blathe([(0, 3.7), (1.25, 3.7), (1.12, 3.95), (1.02, 4.3), (0.95, 4.8), (0.9, 5.3), (0.87, 5.8), (0.92, 6.0), (0.0, 6.0)], 48)
    bmesh.ops.subdivide_edges(st, edges=[e for e in st.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.2], cuts=3)
    for v in st.verts:                                                                          # verticale schorsgroeven, wortelaanzetten, rafelige top
        a_ = math.atan2(v.co.y, v.co.x); zz = v.co.z
        g = 1 + 0.045 * math.sin(26 * a_ + 1.5 * math.sin(zz * 2.3)) + 0.03 * math.sin(11 * a_ + zz) + 0.07 * max(0.0, 4.4 - zz) * math.sin(5 * a_)
        v.co.x *= g; v.co.y *= g
        if zz > 5.8: v.co.z += 0.2 * math.sin(3 * a_) + 0.12 * math.sin(7 * a_ + 2)
    bmesh.ops.translate(st, vec=(TX, TY, 0), verts=st.verts)
    put("stronk", "schors", st)
    put("stronk", "hout", blathe([(0, 5.95), (0.8, 5.95), (0.82, 6.0), (0, 6.02)], 32), TR(TX, TY, 0.02))   # jaarringen-schijf bovenop
    put("stronk", "schors", taps([(TX + 0.5, TY + 0.3, 5.8), (TX + 0.7, TY + 0.4, 6.3), (TX + 0.65, TY + 0.2, 6.65)], 0.18, 0.08))   # afgebroken tak
    OVR = 0.38
    def dakz(x, y):
        """hoogte van het leienoppervlak (bovenkant leitjes) op (x, y); onder de goot: None"""
        ys = Y0 - OVR if y < YC else Y1 + OVR
        t = (y - ys) / (YC - ys)
        if t < 0: return None
        return EAVE - 0.2 + (RIDGE - 0.02 - (EAVE - 0.2)) * min(t, 1.0) + 0.07 + dakbult(x, y)
    def wortelpad(x0, y0, x1, y1, xc, yc, r0):
        """wortel vanaf de stronkvoet over het dak (precies op de leien) naar de goot, dan langs de hoek naar beneden de grond in"""
        pts = []; n = 16
        for i in range(n + 1):
            t = i / n; x = x0 + (x1 - x0) * t + 0.25 * math.sin(t * 5.0) * (1 - t); y = y0 + (y1 - y0) * t
            z = dakz(x, y)
            if z is None: break
            r = r0 * (1 - 0.45 * t); pts.append((x, y, z + r * 0.55))
        ex, ey, ez = pts[-1]
        for (dx, dy, zz) in ((0.06, 0.0, ez - 0.35), (0.12, 0.0, EAVE - 0.6), (0.0, 0.0, 1.2), (0.0, 0.0, 0.4), (0.05, 0.0, -0.05)):   # langs de keienhoek omlaag
            pts.append((xc + (ex - xc) * 0.3 + dx, yc + (ey - yc) * 0.3 + dy * 0 + (0.18 if yc < YC else -0.18) * -1, zz))
        return pts
    WORT = [wortelpad(TX - 0.7, TY - 0.65, X0 + 0.55, Y0 - OVR + 0.05, X0 + 0.05, Y0 - 0.15, 0.3),
            wortelpad(TX + 0.7, TY - 0.6, X1 - 0.45, Y0 - OVR + 0.05, X1 - 0.05, Y0 - 0.15, 0.3),
            wortelpad(TX - 0.6, TY + 0.65, X0 + 0.65, Y1 + OVR - 0.05, X0 + 0.05, Y1 + 0.15, 0.28),
            wortelpad(TX + 0.7, TY + 0.6, X1 - 0.5, Y1 + OVR - 0.05, X1 - 0.05, Y1 + 0.15, 0.28)]
    for k, w in enumerate(WORT):
        put("wortels", "schors", organisch(taps(w, 0.3, 0.13), 0.045, 3, 0.5, 0.03, 2.0, 0.25))
    for (x1, y1) in ((TX - 1.6, TY - 0.1), (TX + 1.4, TY + 0.3), (TX - 0.2, TY - 1.3)):                    # korte wortelaanzetten over de leien
        pts = []
        for i in range(7):
            t = i / 6; x = TX + (x1 - TX) * (0.45 + 0.55 * t); y = TY + (y1 - TY) * (0.45 + 0.55 * t); z = dakz(x, y)
            if z is None: break
            pts.append((x, y, z + 0.1 * (1 - t) + 0.04))
        if len(pts) > 2: put("wortels", "schors", organisch(taps(pts, 0.2, 0.05), 0.04, 2, 0.5, 0.02, 2.0, 0.3))
    for k in range(4):                                                                                        # wortelvoeten die uitwaaieren in de grond
        x, y = WORT[k][-1][0], WORT[k][-1][1]
        for j in range(3):
            a = RNG.uniform(0, math.tau); put("wortels", "schors", organisch(taps([(x, y, 0.15), (x + 0.6 * math.cos(a), y + 0.6 * math.sin(a), -0.05)], 0.14, 0.05), 0.04, 2, 0.5, 0.02, 2.0, 0.3))
    # stronkvoet: kraag die precies op het dak aansluit (geen stronk die 'in' het dak steekt maar erop rust)
    kr = bmesh.new()
    for k in range(40):
        a = k * math.tau / 40
        for rr in (1.05, 1.25, 1.45):
            x = TX + rr * math.cos(a); y = TY + rr * math.sin(a); z = dakz(x, y) or (EAVE)
            st_ = ell((x, y, z + 0.08 * (1.6 - rr)), (0.16, 0.16, 0.1), 6, 4)
            me_ = bpy.data.meshes.new("_t"); st_.to_mesh(me_); st_.free(); kr.from_mesh(me_); bpy.data.meshes.remove(me_)
    put("stronk", "schors", organisch(kr, 0.05, 3, 0.6, 0.02, 2.0, 0.25))
    coll_box(TX, TY, 4.9, 2.0, 2.0, 2.2)
    # ================= DETAILS: afgebladderd stuc met verdiepte baksteen, sporenkoppen, klimop, brandhout, emmer =================
    def brokplek(cx, cz, w, h, nrm_axis, face, seed):
        """stuk afgevallen stuc: verdiept baksteenveld (rijen met voeg) met een opstaand stucrandje (Repelsteeltje_exterieur, bouw-03)"""
        r = random.Random(seed); pts = []
        for k in range(12):
            a = k * math.tau / 12; rr = 1 + r.uniform(-0.25, 0.2); pts.append((cx + w / 2 * rr * math.cos(a), cz + h / 2 * rr * math.sin(a)))
        rows = int(h / 0.075)
        for i in range(rows):
            zz = cz - h / 2 + i * 0.075 + 0.04; off = 0.06 if i % 2 else 0.0; xx = cx - w / 2 + off
            while xx < cx + w / 2:
                if inside(xx + 0.06, zz, pts):
                    if nrm_axis == "y": put("muren", "baksteen", bz(xx, xx + 0.11, face - 0.02, face + 0.01, zz - 0.03, zz + 0.03, 0.004))
                    else: put("muren", "baksteen", bz(face - 0.01, face + 0.02, xx, xx + 0.11, zz - 0.03, zz + 0.03, 0.004))
                xx += 0.125
        ring = [(p[0], p[1]) for p in pts] + [pts[0]]
        for (a_, b_) in zip(ring, ring[1:]):
            if nrm_axis == "y": put("muren", "stuc", btube([(a_[0], face - 0.025, a_[1]), (b_[0], face - 0.025, b_[1])], 0.025, 5))
            else: put("muren", "stuc", btube([(face - 0.025, a_[0], a_[1]), (face - 0.025, b_[0], b_[1])], 0.025, 5))
    for k, (cx_, cz_, w_, h_) in enumerate(((-1.25, 1.25, 0.7, 0.55), (2.35, 1.55, 0.6, 0.7), (1.85, 0.42, 0.55, 0.32), (-0.55, 2.2, 0.45, 0.3))):
        brokplek(cx_, cz_, w_, h_, "y", Y0 + 0.08, 30 + k)
    for k, (cy_, cz_, w_, h_) in enumerate(((YC + 0.9, 0.8, 0.5, 0.45), (YC - 1.1, 1.75, 0.4, 0.35))):
        brokplek(cy_, cz_, w_, h_, "x", X1 - 0.08, 40 + k)
    for k in range(13):                                                                                   # sporenkoppen onder de goot
        x = X0 + 0.45 + k * (X1 - X0 - 0.5) / 12
        for (yy, sg) in ((Y0 + 0.05, -1), (Y1 - 0.05, 1)):
            put("dak", "hout", bz(x - 0.05, x + 0.05, yy, yy + sg * 0.42, EAVE - 0.3, EAVE - 0.2, 0.01))
    for (yy, sg) in ((Y0 - 0.38, -1), (Y1 + 0.38, 1)):                                                    # windveer/goot-plank
        put("dak", "hout", bz(X0 + 0.2, X1 + 0.38, yy - 0.02, yy + 0.02, EAVE - 0.42, EAVE - 0.24))
    rk = random.Random(5)                                                                                 # klimop tegen de schoorsteengevel (exterieur rechts)
    for k in range(260):
        cy_ = rk.uniform(Y0 + 0.2, Y1 - 0.2); cz_ = rk.uniform(0.0, 2.2) * rk.random() ** 0.6
        if abs(cy_ - (YC - 0.6)) < 0.45 and 1.0 < cz_ < 1.85: continue
        lf = ell((X1 + 0.02 + rk.uniform(0, 0.08), cy_, cz_), (0.02, rk.uniform(0.05, 0.08), rk.uniform(0.04, 0.07)), 5, 3)
        bmesh.ops.rotate(lf, verts=lf.verts, cent=(X1, cy_, cz_), matrix=Matrix.Rotation(rk.uniform(-0.6, 0.6), 3, "Y"))
        put("klimop", "klimop", lf)
    for k in range(5): put("klimop", "hout", btube([(X1 + 0.03, Y0 + 0.4 + k * 0.7, 0.0), (X1 + 0.03, Y0 + 0.5 + k * 0.7 + rk.uniform(-0.3, 0.3), rk.uniform(1.2, 2.0))], 0.012, 4))
    for i in range(4):                                                                                    # houtstapel bij de achtergevel
        for j in range(6 - i):
            put("tuin", "brandhout", blathe([(0, -0.35), (0.07, -0.35), (0.07, 0.35), (0, 0.35)], 8),
                Matrix.Translation((X1 + 0.6, Y1 - 0.9 + j * 0.15 + i * 0.075, 0.08 + i * 0.13)) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    put("tuin", "hout", blathe([(0, 0), (0.14, 0), (0.17, 0.3), (0, 0.3)], 12), TR(X0 - 0.7, Y0 - 0.4))   # houten emmer
    put("tuin", "ijzer", blathe([(0.145, 0.08), (0.15, 0.08), (0.155, 0.11), (0.15, 0.11)], 12), TR(X0 - 0.7, Y0 - 0.4))
    # ================= tuintje: bolderkar, hark, keien, laag hekje langs het pad, flagstone-pad, sprookjesboek =================
    M = TR(X0 - 1.6, Y0 + 0.4, 0, 20)                                                                         # bolderkar (bouw-02)
    put("tuin", "hout", bz(-0.45, 0.45, -0.28, 0.28, 0.32, 0.36), M)
    for sy in (-1, 1): put("tuin", "hout", bz(-0.45, 0.45, sy * 0.28 - 0.02, sy * 0.28 + 0.02, 0.36, 0.6), M)
    for sx in (-1, 1): put("tuin", "hout", bz(sx * 0.45 - 0.02, sx * 0.45 + 0.02, -0.28, 0.28, 0.36, 0.6), M)
    for (wx, wy) in ((-0.3, -0.32), (-0.3, 0.32), (0.3, -0.32), (0.3, 0.32)):
        put("tuin", "rood", blathe([(0, -0.02), (0.17, -0.02), (0.17, 0.02), (0, 0.02)], 12), M @ Matrix.Translation((wx, wy, 0.18)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    put("tuin", "hout", btube([(0.45, 0, 0.42), (0.95, 0, 0.62)], 0.02, 5), M)
    put("tuin", "hout", btube([(X1 + 0.4, Y0 - 0.3, 0.0), (X1 + 0.15, Y0 - 0.25, 1.5)], 0.02, 5))           # hark tegen de muur
    put("tuin", "ijzer", bz(X1 + 0.02, X1 + 0.28, Y0 - 0.32, Y0 - 0.2, 1.45, 1.52))
    for k in range(9):
        x = RNG.uniform(X0 - 2.5, X1 + 1.5); y = RNG.uniform(Y0 - 1.6, Y0 - 0.6); s = RNG.uniform(0.15, 0.32)
        put("tuin", "natuursteen", ell((x, y, s * 0.3), (s * 1.3, s, s * 0.6), 8, 6))
    HEK = [(X0 - 3.5, Y0 - 1.9), (X0 + 0.5, Y0 - 1.95), (X1 + 0.5, Y0 - 1.9), (X1 + 2.8, Y0 - 1.6)]                   # laag blauwgroen hekje (Repelreus)
    for (a, b) in zip(HEK, HEK[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); Mh = Matrix.Translation((a[0], a[1], 0)) @ Matrix.Rotation(math.atan2(b[1] - a[1], b[0] - a[0]), 4, "Z")
        put("hek", "blauwgroen", btube([(0, 0, 0.62), (L, 0, 0.62)], 0.018, 6), Mh)
        k = 0.0
        while k <= L + 1e-3:
            put("hek", "blauwgroen", btube([(k, 0, 0.0), (k, 0, 0.66)], 0.018, 6), Mh); k += 1.25
        coll_box((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0.45, L, 0.12, 0.9, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
    PAD = [(-14.0, -4.0), (-3.5, -3.7), (11.0, -3.6), (11.0, -6.9), (-3.5, -7.0), (-9.0, -8.6), (-14.0, -9.0)]
    pb = bmesh.new(); vv = [pb.verts.new((x, y, 0.04)) for x, y in PAD]; vb = [pb.verts.new((x, y, -0.12)) for x, y in PAD]
    pb.faces.new(vv); pb.faces.new(vb[::-1])
    for i in range(len(PAD)): pb.faces.new((vv[i], vb[i], vb[(i + 1) % len(PAD)], vv[(i + 1) % len(PAD)]))
    bmesh.ops.recalc_face_normals(pb, faces=pb.faces); bmesh.ops.triangulate(pb, faces=[f for f in pb.faces if len(f.verts) > 4], ngon_method="EAR_CLIP")
    put("pad", "flagstone", pb)
    coll_box(-1.5, -5.4, -0.04, 25.0, 3.4, 0.2, 0); coll_box(-11.5, -6.5, -0.04, 5.0, 5.0, 0.2, 0)
    MB = TR(X0 - 3.0, Y0 - 1.5, 0, 160)                                                                       # sprookjesboek (Boekloc: voor het huisje)
    put("boek", "ijzer", btube([(0, 0, 0.03), (0, 0, 0.85)], 0.03, 6), MB)
    for a in (0, 120, 240):
        ca, sa_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        put("boek", "ijzer", btube([(0, 0, 0.25), (0.18 * ca, 0.18 * sa_, 0.08), (0.24 * ca, 0.24 * sa_, 0.0)], 0.018, 5), MB)
    MBk = MB @ TR(0, 0, 0.88) @ Matrix.Rotation(math.radians(-28), 4, "X")
    put("boek", "hout", bz(-0.42, 0.42, -0.3, 0.3, -0.03, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.27, 0.27, 0.0, 0.035, 0.008), MBk)
    coll_box(X0 - 3.0, Y0 - 1.5, 0.5, 0.6, 0.6, 1.0, 0)
    # wegschrijven
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"RS_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "rook": json_rook}, open(os.path.join(out, "huisje_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
