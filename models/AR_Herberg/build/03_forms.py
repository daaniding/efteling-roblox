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
        "glaslamp": ((0.9, 0.8, 0.6, 1), 0.2), "zink": ((0.5, 0.52, 0.52, 1), 0.5), "vat": ((0.42, 0.28, 0.16, 1), 0.8), "goud": ((0.8, 0.6, 0.2, 1), 0.3)}
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


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ================= HOOFDHUIS: muren (stuc), natuurstenen plint, natuursteen in de gevelbaai =================
    put("muren", "stuc", bz(0.0, LX, 0.0, DY, -0.3, EAVE))
    put("muren", "natuursteen", bz(-0.04, LX + 0.04, -0.04, DY + 0.04, -0.3, 0.35, 0.02))                  # plint
    # gevelbaai links (steekt 0.6 m naar voren): natuursteen boven 1.25 m, puntgevel met houten beschot, steil rieten zadeldak
    BX0, BX1, BY = 0.0, 3.8, -0.6
    put("baai", "stuc", bz(BX0, BX1, BY, 0.1, -0.3, EAVE + 0.15))
    put("baai", "natuursteen", bz(BX0 - 0.03, BX1 + 0.03, BY - 0.03, 0.05, 1.25, EAVE + 0.15))
    put("baai", "natuursteen", bz(BX0 - 0.04, BX1 + 0.04, BY - 0.04, 0.1, -0.3, 0.35, 0.02))
    gx = (BX0 + BX1) / 2; GTOP = 6.2
    gev = [(BX0 + 0.1, EAVE + 0.15), (BX1 - 0.1, EAVE + 0.15), (gx, GTOP - 0.4)]
    put("baai", "hout", boutline(gev, BY + 0.02, 0.1))
    for k in range(12):                                                                          # verticale planken op de puntgevel
        xx = BX0 + 0.3 + k * (BX1 - BX0 - 0.6) / 11; hz = EAVE + 0.15 + (GTOP - 0.4 - EAVE - 0.15) * (1 - abs(xx - gx) / (gx - BX0 - 0.1))
        put("baai", "hout", bz(xx - 0.03, xx + 0.03, BY - 0.0, BY + 0.03, EAVE + 0.15, hz - 0.05))
    raam(gx - 0.32, gx + 0.32, 3.55, 4.25, BY, luiken=False)                                     # gevelraampje boven
    # rieten zadeldak van de gevelbaai: profiel (omgekeerde V met dikte) langs y geextrudeerd, randen afgerond (bevel)
    o, d = 0.4, 0.38
    prof = [(BX0 - o, EAVE - 0.05), (gx, GTOP + 0.15), (BX1 + o, EAVE - 0.05), (BX1 + o - 0.3, EAVE - 0.05 - d), (gx, GTOP + 0.15 - d * 1.3), (BX0 - o + 0.3, EAVE - 0.05 - d)]
    bm = boutline(prof, BY - 0.5, 4.2); bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], ngon_method="EAR_CLIP")
    bmesh.ops.bevel(bm, geom=[e for e in bm.edges if e.calc_face_angle(0) > 0.3], offset=0.12, segments=3, affect="EDGES", profile=0.6)
    put("dak_baai", "riet", bm)
    # windveren (houten randplanken langs de gevel, ontwerptekening)
    for sx_ in (-1, 1):
        a_ = (gx + sx_ * (gx - BX0 + o - 0.1), BY - 0.52, EAVE - 0.1); b_ = (gx, BY - 0.52, GTOP + 0.25)
        put("dak_baai", "hout", btube([a_, b_], 0.09, 4))
    # ================= HOOFDDAK: riet, schilddak, dikke ronde rand =================
    def rect(x0, x1, y0, y1, z): return [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    o = 0.55; d = 0.45
    top = [rect(-o + 3.6, LX + o, -o, DY + o, EAVE - 0.1), rect(4.4, LX - 2.0, DY / 2 - 0.15, DY / 2 + 0.15, RIDGE)]
    bot = [rect(-o + 4.1, LX + o - 0.5, -o + 0.5, DY + o - 0.5, EAVE - 0.1 - d), rect(4.4, LX - 2.0, DY / 2 - 0.15, DY / 2 + 0.15, RIDGE - d * 1.4)]
    # westdeel (boven de gevelbaai en erachter) als tweede schilddak, iets hoger nok
    for (t_, b__) in ((top, bot), ([rect(-o, 4.6, 0.4, DY + o, EAVE - 0.1), rect(1.6, 2.4, DY / 2 - 0.1, DY / 2 + 0.6, RIDGE + 0.2)],
                                   [rect(-o + 0.5, 4.1, 0.9, DY + o - 0.5, EAVE - 0.1 - d), rect(1.6, 2.4, DY / 2 - 0.1, DY / 2 + 0.6, RIDGE + 0.2 - d * 1.4)])):
        bm = bmesh.new(); vt = [[bm.verts.new(p) for p in r] for r in t_]; vb = [[bm.verts.new(p) for p in r] for r in b__]
        for k in range(4):
            bm.faces.new((vt[0][k], vt[0][(k + 1) % 4], vt[1][(k + 1) % 4], vt[1][k]))
            bm.faces.new((vb[0][(k + 1) % 4], vb[0][k], vb[1][k], vb[1][(k + 1) % 4]))
            bm.faces.new((vt[0][(k + 1) % 4], vt[0][k], vb[0][k], vb[0][(k + 1) % 4]))
        bm.faces.new(vt[1]); bm.faces.new(vb[1][::-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.bevel(bm, geom=[e for e in bm.edges if e.is_manifold and e.calc_face_angle(0) > 0.3], offset=0.14, segments=3, affect="EDGES", profile=0.6)
        put("dak", "riet", bm)
    # wenkbrauwdakkapel in het midden (golvende bult in het riet met een raampje)
    eb = ell((6.3, 0.15, EAVE + 0.7), (1.45, 0.75, 0.62), 32, 16)                              # wenkbrauw: een gladde boog in het riet
    bmesh.ops.delete(eb, geom=[v for v in eb.verts if v.co.z < EAVE + 0.45], context="VERTS"); put("dak", "riet", eb)
    put("ramen", "venster", bz(5.9, 6.7, -0.42, -0.3, EAVE + 0.75, EAVE + 1.15))
    put("ramen", "hout", bz(5.88, 6.72, -0.44, -0.42, EAVE + 0.93, EAVE + 0.97))
    # ================= TOREN: achthoek, stuc onder, houten beschot boven (overstek), pannendak met spits =================
    put("toren", "stuc", blathe([(0, -0.3), (TR1 + 0.04, -0.3), (TR1, 3.0), (0, 3.0)], 8), TR(TC.x, TC.y, 0, 22.5))
    put("toren", "natuursteen", blathe([(0, -0.3), (TR1 + 0.1, -0.3), (TR1 + 0.1, 0.35), (0, 0.35)], 8), TR(TC.x, TC.y, 0, 22.5))
    put("toren", "hout", blathe([(0, 2.9), (TR1 + 0.05, 2.9), (TR2, 3.15), (TR2, 5.85), (0, 5.85)], 8), TR(TC.x, TC.y, 0, 22.5))
    for k in range(48):                                                                          # planken (verticale latten)
        a = k * math.tau / 48; c, s = math.cos(a), math.sin(a)
        put("toren", "hout", btube([(TC.x + (TR2 + 0.02) * c, TC.y + (TR2 + 0.02) * s, 3.2), (TC.x + (TR2 + 0.02) * c, TC.y + (TR2 + 0.02) * s, 5.8)], 0.025, 4))
    lathe = [(TR2 + 0.45, 5.8), (TR2 + 0.15, 6.15), (1.6, 7.1), (0.8, 8.3), (0.05, 9.45)]
    rr = []; zr = []
    for (r, z) in lathe: rr.append(r); zr.append(z)
    put("toren", "pannen", blathe([(0, 5.7)] + lathe[:-1] + [(0.0, 9.45)], 8), TR(TC.x, TC.y, 0, 22.5))
    for i in range(14):                                                                          # pannenrijen (lijnen)
        t = i / 14; r = TR2 + 0.45 - (TR2 + 0.4) * t ** 0.9; z = 5.85 + 3.55 * t
        put("toren", "pannen", blathe([(r + 0.025, z - 0.02), (r + 0.03, z), (r - 0.02, z + 0.03)], 8), TR(TC.x, TC.y, 0, 22.5))
    put("toren", "zink", blathe([(0, 9.3), (0.06, 9.35), (0.06, 9.6), (0.12, 9.68), (0.0, 9.8)], 10), TR(TC.x, TC.y))
    put("toren", "goud", blathe([(0, 9.8), (0.015, 9.8), (0.015, 10.2), (0, 10.25)], 6), TR(TC.x, TC.y))
    put("toren", "goud", blathe([(0, 10.0), (0.05, 10.05), (0.05, 10.1), (0, 10.15)], 10), TR(TC.x, TC.y))
    deur_boog(TC.x, 1.0, 2.15, TC.y - TR1 * math.cos(math.pi / 8) + 0.02)                    # torendeur voor
    raam(TC.x - 0.24, TC.x + 0.24, 4.1, 4.7, TC.y - TR2 * math.cos(math.pi / 8) - 0.02, luiken=False)
    coll_box(TC.x, TC.y, 1.5, 2 * TR1, 2 * TR1, 3.0)
    # ================= deuren, ramen, schoorstenen, lantaarn, uithangbord =================
    deur_boog(1.2, 1.0, 2.15, BY)                                                                 # voordeur in de gevelbaai
    raam(2.6, 3.2, 1.1, 1.8, BY)
    raam(4.7, 5.6, 0.95, 1.85); raam(7.0, 7.9, 0.95, 1.85)
    # ronde stucschoorsteen met puntkap (midden achter de dakkapel) en vierkante schoorsteen links
    put("schoorsteen", "stuc", blathe([(0, 4.0), (0.62, 4.0), (0.55, 6.5), (0.38, 8.2), (0.44, 8.3), (0.44, 8.45), (0, 8.45)], 20), TR(5.2, 4.2))   # taps toelopend (ontwerp)
    put("schoorsteen", "pannen", blathe([(0, 8.7), (0.55, 8.68), (0.3, 9.2), (0.05, 9.75), (0, 9.8)], 16), TR(5.2, 4.2))
    for k in range(6): a = k * math.tau / 6; put("schoorsteen", "stuc", btube([(5.2 + 0.36 * math.cos(a), 4.2 + 0.36 * math.sin(a), 8.43), (5.2 + 0.36 * math.cos(a), 4.2 + 0.36 * math.sin(a), 8.72)], 0.06, 6))
    put("schoorsteen", "natuursteen", bz(0.6, 1.3, 2.6, 3.3, 4.0, 7.4, 0.02))
    put("schoorsteen", "zink", bz(0.5, 1.4, 2.5, 3.4, 7.4, 7.5)); put("schoorsteen", "zink", blathe([(0, 7.5), (0.42, 7.5), (0.05, 7.85), (0, 7.9)], 4), TR(0.95, 2.95, 0, 45))
    # lantaarn op een arm aan de linkerhoek van de baai
    lx, lz = BX0 - 0.05, 2.35
    put("lantaarn", "ijzer", btube([(lx, BY + 0.2, lz + 0.35), (lx - 0.45, BY + 0.2, lz + 0.35), (lx - 0.45, BY + 0.2, lz + 0.25)], 0.015, 6))
    put("lantaarn", "ijzer", blathe([(0, 0.34), (0.14, 0.3), (0.14, 0.28), (0.11, 0.26), (0.11, 0.0), (0.08, -0.04), (0, -0.05)], 4), TR(lx - 0.45, BY + 0.2, lz - 0.1))
    put("lantaarn", "glaslamp", blathe([(0, 0.01), (0.09, 0.01), (0.09, 0.25), (0, 0.25)], 4), TR(lx - 0.45, BY + 0.2, lz - 0.1))
    LAMPS_.append([round(lx - 0.45, 2), round(BY + 0.2, 2), lz + 0.02])
    # uithangbord aan een galg rechts aan de baai (Herbergbord): houten balk + schoor + bord (textuur)
    sx0 = BX1 + 0.05
    put("bord", "hout", bz(sx0, sx0 + 1.0, BY - 0.04, BY + 0.04, 2.55, 2.63)); put("bord", "hout", btube([(sx0, BY, 2.0), (sx0 + 0.55, BY, 2.58)], 0.03, 5))
    bmb = bmesh.new(); uvl = bmb.loops.layers.uv.new("UVMap")
    for sgn in (1, -1):
        cs = [(sx0 + 0.25, BY, 1.7), (sx0 + 0.9, BY, 1.7), (sx0 + 0.9, BY, 2.48), (sx0 + 0.25, BY, 2.48)]
        if sgn < 0: cs = cs[::-1]
        f = bmb.faces.new([bmb.verts.new((c[0], c[1] + 0.012 * sgn * -1, c[2])) for c in cs])
        uvs = ((0, 0), (1, 0), (1, 1), (0, 1)) if sgn > 0 else ((0, 1), (1, 1), (1, 0), (0, 0))
        for l, uv in zip(f.loops, uvs): l[uvl].uv = uv
    me = bpy.data.meshes.new("BAKE_bord"); bmb.to_mesh(me); bmb.free(); ob = bpy.data.objects.new("BAKE_bord", me); col("FORMS").objects.link(ob); own(ob)
    mt = bpy.data.materials.get("MAT_bordtex") or bpy.data.materials.new("MAT_bordtex"); ob.data.materials.append(mt)
    for xx in (sx0 + 0.32, sx0 + 0.83): put("bord", "ijzer", btube([(xx, BY, 2.48), (xx, BY, 2.55)], 0.008, 4))
    # vaten en een bankje voor de gevel (Herberg.jpg)
    for (x, y, rz) in ((4.25, -0.45, 0), (8.6, -0.5, 30), (9.25, -0.4, 0)):
        put("vaten", "vat", blathe([(0, 0), (0.24, 0), (0.29, 0.2), (0.3, 0.4), (0.29, 0.6), (0.24, 0.8), (0, 0.8)], 16), TR(x, y))
        for z in (0.1, 0.3, 0.5, 0.7): put("vaten", "ijzer", blathe([(0.27 + 0.03 * math.sin(z / 0.8 * math.pi), z - 0.02), (0.3 + 0.03 * math.sin(z / 0.8 * math.pi), z), (0.27 + 0.03 * math.sin(z / 0.8 * math.pi), z + 0.02)], 16), TR(x, y))
        coll_box(x, y, 0.4, 0.6, 0.6, 0.8)
    put("bankje", "hout", bz(5.4, 7.4, -0.55, -0.25, 0.42, 0.48, 0.01))
    for xx in (5.55, 7.25): put("bankje", "hout", bz(xx - 0.05, xx + 0.05, -0.52, -0.28, 0.0, 0.42))
    coll_box(LX / 2, DY / 2, 1.2, LX, DY, 2.4); coll_box(gx, BY / 2, 1.2, BX1 - BX0, -BY, 2.4)
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
