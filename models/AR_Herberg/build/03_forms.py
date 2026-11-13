"""03_forms Herberg De Ersteling (1999, ontwerp Henny Knoet) aan het Herautenplein, naar ref/Herberg.jpg (recht van voren), Herberg_exterieur,
Intro_tafeltjedekje en de ontwerptekening. OSM 55447978 (building=detached, hipped, 1 laag + dak).
Modelframe: x langs de voorgevel van links (west) naar rechts (oost, toren), y de diepte in (voorgevel y=0, gebouw bij +y), z op, z=0 maaiveld.
Kijkt naar -Y = naar het pleintje met het Ezeltje. Oorsprong = west-voorhoek OSM (8.21, -80.99) in het Herautenplein-frame.
Rieten daken = gesloten schaal + subsurf (dikke ronde rietrand). Gebruik: Blender -b -P 03_forms.py -- --master AR_Herberg_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
_src = open(os.path.join(HERE, "..", "..", "AR_Assepoester", "build", "03_forms.py")).read().split("# ---- ramen ----")[0]
exec(_src)
RNG = random.Random(1999)
MATS = {"stuc": ((0.88, 0.83, 0.72, 1), 0.9), "natuursteen": ((0.72, 0.6, 0.42, 1), 0.9), "riet": ((0.52, 0.42, 0.26, 1), 0.95),
        "hout": ((0.3, 0.24, 0.19, 1), 0.8), "pannen": ((0.55, 0.33, 0.25, 1), 0.85), "deur": ((0.28, 0.18, 0.11, 1), 0.7),
        "luik": ((0.36, 0.22, 0.13, 1), 0.7), "venster": ((0.05, 0.05, 0.05, 1), 0.3), "ijzer": ((0.05, 0.05, 0.05, 1), 0.45),
        "glaslamp": ((0.9, 0.8, 0.6, 1), 0.2), "zink": ((0.5, 0.52, 0.52, 1), 0.5), "leien": ((0.45, 0.38, 0.33, 1), 0.85), "vat": ((0.42, 0.28, 0.16, 1), 0.8), "goud": ((0.8, 0.6, 0.2, 1), 0.3)}
COLL = []; LAMPS_ = []
def coll_box(cx, cy, cz, sx, sy, sz, ang=0.0): COLL.append([round(v, 3) for v in (cx, cy, cz, sx, sy, sz, ang)])
LX, DY = 9.6, 8.0                       # hoofdhuis (gevelbreedte, diepte)
EAVE = 2.45; RIDGE = 6.9
TC = Vector((12.0, 2.3)); TR1, TR2 = 2.15, 2.4   # toren: midden, straal onder/boven


def schaal(rings, part, mat, sub=2):
    """gesloten dak-schaal uit ringen [(lijst punten)], buiten en binnen (offset omlaag), subsurf -> dik rond riet"""
    bm = bmesh.new(); R = [[bm.verts.new(p) for p in ring] for ring in rings]; n = len(rings[0])
    for A, B in zip(R, R[1:]):
        for k in range(n): bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    bm.faces.new(R[0][::-1]); bm.faces.new(R[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if sub: bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True, smooth=1.0)
    put(part, mat, bm)


def ell(c, r, segs=16, rings=10):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    bmesh.ops.scale(bm, vec=r, verts=bm.verts); bmesh.ops.translate(bm, vec=c, verts=bm.verts); return bm


def octagon(c, r, z, rot=math.pi / 8): return [(c.x + r * math.cos(rot + k * math.tau / 8), c.y + r * math.sin(rot + k * math.tau / 8), z) for k in range(8)]


def raam(x0, x1, z0, z1, y=0.0, luiken=True, rond=False, part="ramen"):
    """raam in de voorgevel (y vlak), donker glas met roeden, stenen omlijsting, bruine luiken"""
    put(part, "venster", bz(x0, x1, y - 0.04, y + 0.05, z0, z1))
    for xx in (x0 + (x1 - x0) / 2,): put(part, "hout", bz(xx - 0.02, xx + 0.02, y - 0.06, y - 0.04, z0, z1))
    put(part, "hout", bz(x0, x1, y - 0.06, y - 0.04, (z0 + z1) / 2 - 0.02, (z0 + z1) / 2 + 0.02))
    put(part, "natuursteen", bz(x0 - 0.08, x1 + 0.08, y - 0.07, y + 0.02, z0 - 0.1, z0, 0.01))           # vensterbank
    put(part, "natuursteen", bz(x0 - 0.08, x1 + 0.08, y - 0.06, y + 0.02, z1, z1 + 0.1, 0.01))           # latei
    if luiken:
        w = (x1 - x0) / 2
        for sx, xa in ((-1, x0 - w - 0.02), (1, x1 + 0.02)):
            put(part, "luik", bz(xa, xa + w, y - 0.08, y - 0.05, z0, z1, 0.005))
            for zz in (z0 + 0.12, z1 - 0.12): put(part, "ijzer", bz(xa + 0.02, xa + w - 0.02, y - 0.095, y - 0.08, zz - 0.015, zz + 0.015))


def deur_boog(xc, w, h, y=0.0, part="deuren"):
    dp = arch_pts(xc, 0, w, h, 12)
    put(part, "deur", boutline(dp, y - 0.04, 0.06))
    for k in range(5):
        xx = xc - w / 2 + w * (k + 0.5) / 5; put(part, "hout", bz(xx - 0.005, xx + 0.005, y - 0.05, y - 0.04, 0.05, h - 0.3))
    put(part, "natuursteen", band(dp, 0.14, y - 0.06, 0.08))
    put(part, "ijzer", blathe([(0, 0), (0.03, 0), (0.03, 0.01), (0, 0.02)], 8), TR(xc + w * 0.32, y - 0.08, 1.0) @ Matrix.Rotation(math.radians(90), 4, "X"))


def organisch(bm, voxel=0.05, iters=12, factor=0.8, disp=0.035, dscale=0.9, dec=0.35):
    """bmesh -> voxel-remesh (unie) -> smooth (ronde hoeken) -> lichte bobbels (displace) -> bmesh  (Efteling-stijl: zachte dikke vormen)"""
    me = bpy.data.meshes.new("_org"); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new("_org", me); bpy.context.scene.collection.objects.link(o)
    bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = o; o.select_set(True)
    rm = o.modifiers.new("r", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = voxel
    sm = o.modifiers.new("s", "SMOOTH"); sm.factor = factor; sm.iterations = iters
    if disp:
        tx = bpy.data.textures.get("_bobbel") or bpy.data.textures.new("_bobbel", "CLOUDS"); tx.noise_scale = dscale
        dm = o.modifiers.new("d", "DISPLACE"); dm.texture = tx; dm.strength = disp; dm.texture_coords = "OBJECT"
    dc = o.modifiers.new("dc", "DECIMATE"); dc.ratio = dec
    for m_ in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m_.name)
    out = bmesh.new(); out.from_mesh(o.data); bpy.data.objects.remove(o, do_unlink=True)
    for f in out.faces: f.smooth = True
    return out


def merge(*bms):
    out = bmesh.new()
    for b_ in bms:
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); out.from_mesh(me_); bpy.data.meshes.remove(me_)
    return out


def hip(x0, x1, y0, y1, zb, ze, rx0, rx1, ry, zr):
    """massief schilddak: onderrand (zb) -> dikke rietrand (ze) -> nok (rx0..rx1 op y=ry, hoogte zr)"""
    bm = bmesh.new()
    B = [bm.verts.new(p) for p in ((x0, y0, zb), (x1, y0, zb), (x1, y1, zb), (x0, y1, zb))]
    E = [bm.verts.new(p) for p in ((x0, y0, ze), (x1, y0, ze), (x1, y1, ze), (x0, y1, ze))]
    R0 = bm.verts.new((rx0, ry, zr)); R1 = bm.verts.new((rx1, ry, zr))
    bm.faces.new(B[::-1])
    for k in range(4): bm.faces.new((B[k], B[(k + 1) % 4], E[(k + 1) % 4], E[k]))
    bm.faces.new((E[0], E[1], R1, R0)); bm.faces.new((E[1], E[2], R1)); bm.faces.new((E[2], E[3], R0, R1)); bm.faces.new((E[3], E[0], R0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def ruit(x0, x1, z0, z1, y, cols=2, rows=3, fr=0.07, part="ramen", luiken=False):
    """raam in een vlak op y (voorkant -y): houten kozijn, donker glas iets verdiept, roeden cols x rows, optioneel bruine luiken"""
    put(part, "hout", bz(x0 - fr, x1 + fr, y - 0.06, y + 0.12, z0 - fr, z1 + fr, 0.01))
    put(part, "venster", bz(x0, x1, y - 0.075, y - 0.02, z0, z1))
    for c in range(1, cols): xx = x0 + (x1 - x0) * c / cols; put(part, "hout", bz(xx - 0.018, xx + 0.018, y - 0.1, y - 0.06, z0, z1))
    for r in range(1, rows): zz = z0 + (z1 - z0) * r / rows; put(part, "hout", bz(x0, x1, y - 0.1, y - 0.06, zz - 0.018, zz + 0.018))
    put(part, "hout", bz(x0 - fr - 0.04, x1 + fr + 0.04, y - 0.16, y - 0.04, z0 - fr - 0.06, z0 - fr, 0.01))      # vensterbank
    if luiken:
        w = (x1 - x0) / 2 + fr
        for xa in (x0 - fr - w - 0.01, x1 + fr + 0.01):
            put(part, "luik", bz(xa, xa + w, y - 0.1, y - 0.06, z0 - fr, z1 + fr, 0.005))
            for k in range(3): xx = xa + w * (k + 0.5) / 3; put(part, "luik", bz(xx - 0.004, xx + 0.004, y - 0.105, y - 0.1, z0 - fr, z1 + fr))
            for zz in (z0 + 0.1, z1 - 0.1): put(part, "ijzer", bz(xa + 0.02, xa + w - 0.02, y - 0.115, y - 0.1, zz - 0.015, zz + 0.015))


def lantaarn(x, y, z, arm=0.35):
    """zwarte smeedijzeren lantaarn aan een muurarm (arm steekt naar -y uit)"""
    put("lantaarn", "ijzer", btube([(x, y, z + 0.45), (x, y - arm, z + 0.45), (x, y - arm, z + 0.36)], 0.016, 6))
    put("lantaarn", "ijzer", btube([(x, y, z + 0.2), (x, y - arm * 0.6, z + 0.45)], 0.012, 5))
    put("lantaarn", "ijzer", blathe([(0, 0.36), (0.05, 0.36), (0.15, 0.27), (0.13, 0.25), (0.1, 0.25), (0.1, 0.02), (0.07, -0.03), (0.02, -0.07), (0, -0.07)], 4), TR(x, y - arm, z, 45))
    put("lantaarn", "glaslamp", blathe([(0, 0.02), (0.095, 0.02), (0.095, 0.24), (0, 0.24)], 4), TR(x, y - arm, z, 45))
    LAMPS_.append([round(x, 2), round(y - arm, 2), round(z + 0.13, 2)])


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ---- maten (m) uit ref/Intro_tafeltjedekje.jpg: 87.5 px/m op de gevel (gevel 10.0 m = BAG 0->2; ontwerptekening "6m" = ketel),
    #      x = (px - 75) / 87.5, z = (790 - py) / 87.5. y = diepte (+ het gebouw in), voorgevel y = 0.
    GW = 5.1; GY = -0.35            # gevelbaai x 0..5.1 (px 75..520), 0.35 naar voren (inferred: foto recht van voren)
    AX = 2.75; APEX = 5.55          # top van de rieten gevelkap (px 320, 305)
    EAV = 2.05                      # muurhoogte onder de rietrand (px 610-620)
    RIDGE = 4.45                    # nok met rode vorsten (py 418, nok ligt 3.6 m dieper dan de gevel -> perspectief x1.1)
    KO = [(-0.5, 1.85), (0.08, 2.74), (2.78, 5.8), (4.32, 3.9), (4.95, 2.74), (5.3, 2.02)]   # buitenrand kap (gemeten)
    KIL = [(-0.02, 1.62), (0.29, 2.4), (0.9, 3.54), (1.72, 4.46), (2.78, 5.32)]                   # binnenrand links (onder -> top)
    KIR = [(4.85, 1.8), (4.8, 2.4), (4.2, 3.45), (3.6, 4.4), (2.78, 5.32)]                       # binnenrand rechts
    def kz(pl, x):                                                                       # hoogte van de kap-binnenrand boven x
        for (x0, z0), (x1, z1) in zip(pl, pl[1:]):
            if min(x0, x1) <= x <= max(x0, x1) and x1 != x0: return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
        return pl[-1][1]
    def kx(pl, z):
        for (x0, z0), (x1, z1) in zip(pl, pl[1:]):
            if z0 <= z <= z1: return x0 + (x1 - x0) * (z - z0) / (z1 - z0)
        return pl[-1][0]
    T = Vector((12.25, 0.75)); TR0 = 1.95; TP = 2.3   # toren: BAG-omtrek = overstek (TP); voet r 1.7 (Herberg_exterieur)   # toren: BAG-punten 3..9 (x 10.0..14.6, diepte -1.4..+2.9)
    # ================= MUREN: zachte, licht bobbelige crème stucmassa (BAG-plattegrond: L-vorm) =================
    w = merge(bz(0.0, 4.25, 0.0, 6.1, -0.4, EAV + 0.2), bz(4.2, 5.5, 0.0, 5.39, -0.4, EAV + 0.2), bz(5.45, 10.4, 0.0, 8.58, -0.4, EAV + 0.2),
              bz(0.0, GW, GY, 0.3, -0.4, EAV + 0.2))
    put("muren", "stuc", organisch(w, 0.06, 12, 0.8, 0.045, 1.0, 0.1))
    tb = blathe([(0, -0.4), (TR0 + 0.06, -0.4), (TR0 + 0.03, 0.5), (TR0, 2.5), (0, 2.5)], 24); bmesh.ops.translate(tb, vec=(T.x, T.y, 0), verts=tb.verts)
    put("muren", "stuc", organisch(tb, 0.06, 10, 0.8, 0.035, 1.0, 0.15))
    # ================= GEVELDRIEHOEK: natuursteen (py 450-580) en donker plankwerk in de top (py 360-450) =================
    put("gevel", "natuursteen", boutline([(-0.25, EAV + 0.05), (GW + 0.2, EAV + 0.05), (AX, 5.65)], GY - 0.02, 1.2))   # tot onder de kap (geen kier links)           # lichte mortel tussen de stenen
    # natuursteen: een veld met de stenen-scan (stone_wall) i.p.v. losse kussenblokken (Daan: "lijkt niet op het echt")
    PT = EAV + 1.85                                                                     # plankwerk vanaf hier
    put("gevel", "hout", bz(kx(KIL, PT) - 0.2, kx(KIR, PT) + 0.2, GY - 0.04, GY + 0.06, PT - 0.1, PT + 0.03))
    for k in range(24):
        x = kx(KIL, PT) - 0.1 + k * (kx(KIR, PT) - kx(KIL, PT) + 0.2) / 23; hz = (kz(KIL, x) if x < AX else kz(KIR, x)) + 0.12                 # tot net onder de kap-binnenrand
        if hz > PT + 0.1: put("gevel", "hout", bz(x - 0.07, x + 0.07, GY - 0.05 - 0.02 * (k % 2), GY + 0.02, PT, hz, 0.01))
    put("gevel", "hout", organisch(bz(-0.05, GW + 0.05, GY - 0.22, GY + 0.15, EAV - 0.1, EAV + 0.2), 0.03, 4, 0.6, 0.0))   # dikke donkere balk
    ruit(AX - 0.42, AX + 0.42, EAV + 0.42, EAV + 1.55, GY - 0.02, cols=2, rows=3, fr=0.09, part="gevel")              # gevelraam (px 265-340)
    # ================= RIET: schilddak + achtervleugel + asymmetrische gevelkap + wenkbrauw, samen organisch =================
    rt = merge(hip(4.9, 10.5, -0.55, 6.65, EAV - 0.35, EAV + 0.1, 6.0, 9.6, 3.05, RIDGE + 0.12), hip(-0.55, 10.5, -0.2, 6.65, EAV - 0.35, EAV + 0.1, -0.15, 9.6, 3.05, RIDGE + 0.12),
               hip(4.8, 10.5, 2.0, 9.15, EAV - 0.35, EAV + 0.1, 6.6, 8.7, 5.6, RIDGE + 0.05))
    # gevelkap: links tot 1.6 m (px 40, 620), rechts tot 1.95 m op de middenrand (px 525, 605), 0.45 voor de gevel
    prof = [(x + (0.06 if x < AX else -0.06 if x > AX else 0), z + 0.05) for x, z in KO][::-1] + KIL[:-1] + [(AX, 5.32)] + KIR[::-1][1:]
    prof = [(x - 0.06 if x < AX else x + 0.06, z) for x, z in prof[:len(KO)]] + prof[len(KO):]
    kap = boutline(prof, GY - 0.55, 4.2); bmesh.ops.triangulate(kap, faces=[f for f in kap.faces if len(f.verts) > 4], ngon_method="EAR_CLIP")
    # wenkbrauw (px 590-825, top py 420): dikke boog die vanuit het riet omhoog golft
    WX, WZ = 7.25, 2.3
    outer = [(WX + 2.7 - 5.4 * i / 36, EAV - 0.15 + (RIDGE - 0.15 - EAV + 0.15) * math.exp(-(abs(2.7 - 5.4 * i / 36) / 1.35) ** 2.6)) for i in range(37)]   # golf: zijkanten lopen uit in de rietrand
    inner = [(WX + 1.02 * math.cos(math.radians(a)), WZ + 1.38 * math.sin(math.radians(a))) for a in range(180, -1, -10)]
    wb = boutline(outer + [(WX - 1.02, EAV - 0.15)] + inner + [(WX + 1.02, EAV - 0.15)], -0.55, 3.4); bmesh.ops.triangulate(wb, faces=[f for f in wb.faces if len(f.verts) > 4], ngon_method="EAR_CLIP")
    sk = [(2.3 + 0.95 * math.cos(math.radians(a)), 2.2 + 1.25 * math.sin(math.radians(a))) for a in range(0, 181, 15)]
    sk_in = [(2.3 + 0.6 * math.cos(math.radians(a)), 2.2 + 0.8 * math.sin(math.radians(a))) for a in range(180, -1, -15)]
    zk = boutline(sk + sk_in, -0.75, 2.0); bmesh.ops.triangulate(zk, faces=[f for f in zk.faces if len(f.verts) > 4], ngon_method="EAR_CLIP")
    bmesh.ops.transform(zk, matrix=Matrix.Translation((-0.3, 0, 0)) @ Matrix.Rotation(math.radians(-90), 4, "Z") @ Matrix.Translation((-2.3, 0, 0)) @ Matrix.Translation((-0.0, 0, 0)), verts=zk.verts)
    bmesh.ops.translate(zk, vec=(0, 2.4, 0), verts=zk.verts)
    rt = merge(rt, wb, zk)
    put("dak", "riet", organisch(kap, 0.055, 5, 0.6, 0.035, 0.6, 0.15))                       # gevelkap apart: scherpe A-top (foto)
    put("dak", "riet", organisch(rt, 0.07, 10, 0.7, 0.07, 0.6, 0.16))
    # wenkbrauw-kapel: donker plankwerk (px 625-800, py 485-550) met raampje (px 690-745)
    put("dak", "hout", boutline([(WX - 1.05, 2.4)] + [(WX + 1.05 * math.cos(math.radians(a)), WZ + 1.4 * math.sin(math.radians(a))) for a in range(180, -1, -15)] + [(WX + 1.05, 2.4)], 0.2, 1.0))
    for k in range(12): x = WX - 0.98 + k * 0.178; put("dak", "hout", bz(x - 0.075, x + 0.075, 0.14, 0.2, 2.4, WZ + 1.38 * math.sqrt(max(0.0, 1 - ((x - WX) / 1.05) ** 2)) - 0.04))
    ruit(7.0, 7.66, 2.86, 3.49, 0.16, cols=2, rows=2, fr=0.06, part="dak")
    # rode halfronde vorsten op de nok (px 60-915)
    for k in range(34):
        x = -0.15 + k * 9.75 / 33; put("dak", "pannen", btube([(x - 0.17, 3.05, RIDGE + 0.12), (x + 0.15, 3.05, RIDGE + 0.17)], 0.17, 10))
    # ================= KETEL op de gevelkap (px 295-345, py 225-290) met donkere nokpaal =================
    put("ketel", "ijzer", organisch(bz(AX - 0.16, AX + 0.16, GY - 0.55, GY - 0.2, APEX - 0.5, APEX + 0.35), 0.03, 4, 0.5, 0.0))
    put("ketel", "zink", blathe([(0, -0.02), (0.36, -0.04), (0.42, -0.08), (0.36, 0.02), (0, 0.06)], 16), TR(AX, GY - 0.38, APEX + 0.35))
    put("ketel", "ijzer", blathe([(0, 0.0), (0.12, 0.01), (0.25, 0.1), (0.29, 0.25), (0.26, 0.4), (0.2, 0.47), (0.24, 0.5), (0.22, 0.54), (0, 0.54)], 16), TR(AX, GY - 0.38, APEX + 0.4))
    put("ketel", "ijzer", btube([(AX - 0.24, GY - 0.38, APEX + 0.9), (AX - 0.1, GY - 0.38, APEX + 1.12), (AX + 0.1, GY - 0.38, APEX + 1.12), (AX + 0.24, GY - 0.38, APEX + 0.9)], 0.016, 5))
    put("ketel", "ijzer", btube([(AX + 0.25, GY - 0.38, APEX + 0.85), (AX + 0.55, GY - 0.38, APEX + 1.45)], 0.015, 5))      # pollepel (py 160-200)
    # ================= SCHOORSTEEN (px 385-460, stuc tot py 270, kap tot py 190) =================
    put("schoorsteen", "stuc", organisch(blathe([(0, 2.8), (0.47, 2.8), (0.44, 6.28), (0.47, 6.32), (0.47, 6.4), (0, 6.4)], 24), 0.04, 6, 0.6, 0.015, 2.0, 0.12), TR(3.97, 2.6))
    put("schoorsteen", "zink", blathe([(0, 6.36), (0.58, 6.36), (0.61, 6.46), (0.52, 6.52), (0.3, 6.9), (0.07, 7.32), (0, 7.4)], 20), TR(3.97, 2.6))
    for k in range(6): a = k * math.tau / 6; put("schoorsteen", "zink", btube([(3.97 + 0.42 * math.cos(a), 2.6 + 0.42 * math.sin(a), 6.36), (3.97 + 0.4 * math.cos(a), 2.6 + 0.4 * math.sin(a), 6.5)], 0.03, 4))
    # ================= OPENINGEN =================
    dp = arch_pts(1.83, -0.05, 1.44, 1.95, 16)                                           # open boogentree (px 172-298, top py 625)
    put("deuren", "venster", boutline(dp, GY - 0.06, 0.08)); put("deuren", "hout", band(dp, 0.11, GY - 0.12, 0.14))
    put("deuren", "hout", bz(1.62, 2.04, GY - 0.16, GY - 0.1, 1.97, 2.08, 0.01))                                    # naambordje boven de boog
    sp = arch_pts(3.83, 1.03, 0.36, 0.52, 8)                                             # smal boograampje (px 395-425)
    put("ramen", "venster", boutline(sp, GY - 0.06, 0.08)); put("ramen", "hout", band(sp, 0.06, GY - 0.1, 0.1))
    put("ramen", "hout", bz(3.83 - 0.014, 3.83 + 0.014, GY - 0.09, GY - 0.05, 1.03, 1.5))
    ruit(5.71, 6.51, 0.46, 1.49, -0.03, cols=2, rows=3, fr=0.07, luiken=True)            # middendeel, raam 1 (px 530-690)
    ruit(8.15, 8.95, 0.46, 1.49, -0.03, cols=2, rows=3, fr=0.07, luiken=True)            # raam 2 (luik px 755-780)
    lantaarn(0.75, GY - 0.05, 1.85)                                                      # links onder de kap (px 140, py 600-630)
    # paal met lantaarn (px 365, py 555) en het uithangbord eraan (dunne donkere strook px 355-375, py 590-700)
    put("bord", "hout", bz(3.27, 3.37, GY - 0.12, GY - 0.02, 1.0, 2.45, 0.01))
    lantaarn(3.32, GY - 0.12, 2.45, arm=0.05)
    put("bord", "hout", bz(3.27, 3.37, GY - 0.9, GY - 0.12, 2.02, 2.1, 0.01)); put("bord", "hout", btube([(3.32, GY - 0.12, 1.65), (3.32, GY - 0.6, 2.06)], 0.025, 5))
    for xx in (-0.3, -0.75): put("bord", "ijzer", btube([(3.32, GY + xx, 2.02), (3.32, GY + xx, 1.94)], 0.008, 4))
    bmb = bmesh.new(); uvl = bmb.loops.layers.uv.new("UVMap")
    for sgn in (1, -1):
        cs = [(3.32, GY - 0.9, 1.3), (3.32, GY - 0.2, 1.3), (3.32, GY - 0.2, 1.94), (3.32, GY - 0.9, 1.94)]
        if sgn < 0: cs = cs[::-1]
        f = bmb.faces.new([bmb.verts.new((c[0] + 0.015 * sgn, c[1], c[2])) for c in cs])
        uvs = ((1, 0), (0, 0), (0, 1), (1, 1)) if sgn > 0 else ((1, 1), (0, 1), (0, 0), (1, 0))
        for l, uv in zip(f.loops, uvs): l[uvl].uv = uv
    put("bord", "hout", bz(3.3, 3.34, GY - 0.93, GY - 0.17, 1.27, 1.97))
    me = bpy.data.meshes.new("BAKE_bord"); bmb.to_mesh(me); bmb.free(); ob = bpy.data.objects.new("BAKE_bord", me); col("FORMS").objects.link(ob); own(ob)
    mt = bpy.data.materials.get("MAT_bordtex") or bpy.data.materials.new("MAT_bordtex"); ob.data.materials.append(mt)
    # ================= TOREN: stuc onder, donker plankwerk op schoren met overstek (py 415-620), steil pannendak met spits =================
    put("toren", "hout", blathe([(0, 2.45), (TP - 0.04, 2.45), (TP, 4.6), (0, 4.6)], 8), TR(T.x, T.y, 0, 22.5))   # Herbergfris1: plankwerk 2.5-4.6 m
    for k in range(48):
        a = k * math.tau / 48; c_, s_ = math.cos(a), math.sin(a); rr = TP * math.cos(math.pi / 8) / math.cos(((a - math.pi / 8 - math.radians(22.5)) % (math.tau / 8)) - math.pi / 8)
        put("toren", "hout", bz(-0.05, 0.05, -0.02, 0.03, 2.5, 4.55), TR(T.x + (rr + 0.01) * c_, T.y + (rr + 0.01) * s_, 0, math.degrees(a) + 90))
    put("toren", "hout", blathe([(0, 2.32), (TP + 0.08, 2.32), (TP + 0.08, 2.48), (0, 2.48)], 8), TR(T.x, T.y, 0, 22.5))
    for k in range(8):
        a = math.radians(22.5) + k * math.tau / 8; c_, s_ = math.cos(a), math.sin(a)
        put("toren", "hout", btube([(T.x + (TR0 - 0.05) * c_, T.y + (TR0 - 0.05) * s_, 1.75), (T.x + (TP - 0.05) * c_, T.y + (TP - 0.05) * s_, 2.35)], 0.06, 4))
    put("toren", "leien", blathe([(0, 4.5), (TP + 0.7, 4.5), (TP + 0.67, 4.65), (TP + 0.05, 5.2), (1.2, 6.15), (0.35, 6.95), (0.0, 7.15)], 8), TR(T.x, T.y, 0, 22.5))
    for i_ in range(18):
        t = i_ / 18; r = TP + 0.67 - (TP + 0.5) * t ** 0.75; z = 4.65 + 2.35 * t
        put("toren", "leien", blathe([(r + 0.03, z - 0.03), (r + 0.045, z), (r - 0.03, z + 0.05)], 8), TR(T.x, T.y, 0, 22.5))
    put("toren", "zink", blathe([(0, 6.9), (0.16, 6.95), (0.18, 7.1), (0.08, 7.2), (0.11, 7.45), (0.05, 7.65), (0.08, 7.8), (0.03, 8.1), (0.0, 8.4)], 10), TR(T.x, T.y))
    put("toren", "goud", blathe([(0, 7.62), (0.1, 7.65), (0.1, 7.72), (0, 7.75)], 10), TR(T.x, T.y))
    for k in range(8):                                                                   # hoekribben (dikker riet-achtige pannen-ribben)
        a = k * math.tau / 8; c_, s_ = math.cos(a), math.sin(a)
        put("toren", "leien", btube([(T.x + (TP + 0.7) * c_, T.y + (TP + 0.7) * s_, 4.62), (T.x + (TP + 0.05) * c_, T.y + (TP + 0.05) * s_, 5.25), (T.x + 1.2 * c_, T.y + 1.2 * s_, 6.2), (T.x + 0.1 * c_, T.y + 0.1 * s_, 7.1)], 0.06, 5))
    DA = -55; MD = TR(T.x, T.y, 0, DA + 90) @ Matrix.Translation((0, -TR0 + 0.04, 0))        # torendeur rechtsvoor (Herberg_exterieur)
    td = arch_pts(0, -0.05, 0.95, 2.2, 12)   # Herbergfris1: 0.92 x 2.24 m
    put("deuren", "deur", boutline(td, -0.08, 0.3), MD); put("deuren", "hout", band(td, 0.09, -0.12, 0.3), MD)
    for k in range(5): xx = -0.38 + k * 0.19; put("deuren", "hout", bz(xx - 0.006, xx + 0.006, -0.1, -0.08, 0.05, 1.7), MD)
    a_ = math.radians(-118); px_, py_ = T.x + TR0 * math.cos(a_), T.y + TR0 * math.sin(a_)
    sp2 = arch_pts(0, 1.0, 0.36, 0.75, 8); MW = TR(px_, py_, 0, math.degrees(a_) + 90)
    put("ramen", "venster", boutline(sp2, -0.06, 0.12), MW); put("ramen", "hout", band(sp2, 0.06, -0.1, 0.12), MW)
    lantaarn(10.45, T.y - 0.95, 1.7, arm=0.3)                                            # px 965
    coll_box(T.x, T.y, 1.25, 2 * TR0, 2 * TR0, 2.5)
    # ================= vaten (px 330-400, Ø0.8) en een bankje =================
    for (x, y, s, hz) in ((3.5, GY - 0.55, 1.0, 0.66), (9.75, -0.45, 0.8, 1.35), (13.2, -1.6, 0.65, 0.9), (13.75, -1.15, 0.65, 0.9)):
        put("vaten", "vat", blathe([(0, 0), (0.33 * s, 0), (0.39 * s, 0.24 * s * hz), (0.41 * s, 0.47 * s * hz), (0.39 * s, 0.7 * s * hz), (0.33 * s, 0.94 * s * hz), (0, 0.94 * s * hz)], 18), TR(x, y))
        for zz in [z_ * hz for z_ in (0.12, 0.35, 0.59, 0.82)]: put("vaten", "ijzer", blathe([(0.35 * s + 0.06 * math.sin(zz * math.pi / (0.94 * hz)) * s, zz * s - 0.025), (0.37 * s + 0.06 * math.sin(zz * math.pi / (0.94 * hz)) * s, zz * s), (0.35 * s + 0.06 * math.sin(zz * math.pi / (0.94 * hz)) * s, zz * s + 0.025)], 18), TR(x, y))
        coll_box(x, y, 0.47 * s, 0.82 * s, 0.82 * s, 0.94 * s)
    put("bankje", "hout", bz(6.8, 7.95, -0.58, -0.22, 0.42, 0.49, 0.01))
    for xx in (6.92, 7.83): put("bankje", "hout", bz(xx - 0.05, xx + 0.05, -0.55, -0.25, 0.0, 0.42))
    coll_box(2.1, 3.05, 1.2, 4.25, 6.1, 2.4); coll_box(7.9, 4.29, 1.2, 4.9, 8.58, 2.4); coll_box(GW / 2, GY / 2, 1.2, GW, -GY, 2.4)
    # ================= wegschrijven =================
    for (part, mat), bm in PARTS.items():
        ob = new_mesh_object(f"HB_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_}, open(os.path.join(out, "herberg_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
