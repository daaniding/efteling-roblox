"""03_huisje Roodkapje: huisje van grootmoeder (Anton Pieck 1959-60, herbouw 2016 naar Karel Willemen).
Bronnen: ref/eftepedia/Aanzichten_Roodkapje.jpeg (aanzichten + plattegrond 1:100, ~30 px/m, GESPIEGELD t.o.v. de bouw),
Zijaanzicht_Roodkapje_2016.png (bordes, kelderdeur + houtgewelf, trap), RK-plattegrond.jpg (1:20 interieur, 4 zuilen voor),
Grootmoedershuisje_herbouwd.jpg (voorkant 2016), Roodkapje-zijgevel-mei2010.jpg (deurzijde), OSM 50911608 (BAG 4.7 x 6.1 m),
OSM bordes-pad 766787193, trap 766787194, poortje 7161368031, lamp 7165020178.
Modelframe: oorsprong = midden BAG-footprint, -Y = voorkant (noord, naar het pad), +X = west (rechts voor de kijker op het pad),
z = 0 = padniveau voor het huisje (= vloer kamer grootmoeder). Achter en opzij ligt het maaiveld op z = -1.9 (maat '180' op de tekening).
OSM -> model: X = -0.995*ox + 0.098*oy ; Y = -0.098*ox - 0.995*oy.
Gebruik: Blender -b -P 03_huisje.py -- --master RK_huisje_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
RNG = random.Random(1960)
MATS = {"stuc": ((0.9, 0.88, 0.82, 1), 0.9), "natuursteen": ((0.6, 0.57, 0.5, 1), 0.95), "lei": ((0.36, 0.26, 0.19, 1), 0.85),
        "hout": ((0.24, 0.15, 0.09, 1), 0.8), "balk": ((0.26, 0.16, 0.1, 1), 0.8), "zuil": ((0.78, 0.62, 0.3, 1), 0.6),
        "venster": ((0.04, 0.04, 0.05, 1), 0.3), "glasoranje": ((1.0, 0.7, 0.35, 1), 0.2), "ijzer": ((0.05, 0.05, 0.05, 1), 0.45),
        "pieckblauw": ((0.16, 0.33, 0.5, 1), 0.55), "tegel": ((0.66, 0.27, 0.16, 1), 0.7), "rood": ((0.62, 0.08, 0.06, 1), 0.7),
        "geel": ((0.86, 0.66, 0.12, 1), 0.6), "groen": ((0.12, 0.38, 0.2, 1), 0.6), "goud": ((0.8, 0.6, 0.2, 1), 0.3),
        "klimop": ((0.12, 0.24, 0.09, 1), 0.8), "brandhout": ((0.5, 0.36, 0.22, 1), 0.9), "zink": ((0.55, 0.57, 0.57, 1), 0.4),
        "interieur": ((0.3, 0.2, 0.14, 1), 0.9), "kijkglas": ((0.7, 0.75, 0.75, 1), 0.05), "gordijn": ((0.6, 0.1, 0.1, 1), 0.9), "glaslamp": ((0.95, 0.85, 0.6, 1), 0.2)}
X0, X1, Y0, Y1 = -2.35, 2.35, -2.2, 2.4      # muren (BAG-breedte 4.7; diepte muren 4.6 + overstek voor + toren achter = BAG 6.1)
YG = -3.3                                    # vakwerkgevel steekt 0.8 m over het pad (Grootmoedershuisje_herbouwd)
ZG = -1.9                                    # maaiveld achter/opzij
EAVE, RIDGE, XE = 2.35, 7.1, 2.95           # dakgoot, nok, goot steekt 0.5 m uit
YR0, YR1 = -3.48, 2.78                       # dak voor/achter
TOW = Vector((2.05, 2.35)); TR0 = 0.95       # ronde toren op de achterhoek rechts
BX0, BY0, BY1 = -3.75, -3.05, 1.7            # bordes (OSM-pad 766787193 op X -3.6 van Y -3.07 tot 1.7)


def roofz(x):       # bovenkant dakvlak op afstand |x| van de nok
    return EAVE + (XE - abs(x)) * (RIDGE - EAVE) / XE


def bell_pts(w=1.0, z0=2.2, n=10):
    """klokgevel (Roodkapje-zijgevel-mei2010, zijaanzicht 2016): rechte voet, S-schouders, smalle hals, ronde kop; (y,z) rond y=0"""
    R = [(w, z0), (w, z0 + 0.55)]
    for i in range(1, n + 1):                         # concave schouder naar binnen
        t = i / n; R.append((w - (w - 0.66) * (1 - math.cos(t * math.pi)) / 2 - 0.1 * math.sin(t * math.pi), z0 + 0.5 + 0.7 * t))
    R.append((0.66, z0 + 1.45))
    for i in range(1, n + 1):                         # ronde kop
        a = math.pi / 2 * i / n; R.append((0.66 * math.cos(a), z0 + 1.45 + 0.5 * math.sin(a)))
    return R + [(-y, z) for y, z in R[::-1]][1:-1]


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)

    # ================= muren: ruw wit gestuct, van het maaiveld (z -1.9) tot onder de goot =================
    wb = bmesh.new()
    for (xa, xb, ya, yb) in ((X0, X0 + 0.32, Y0, Y1), (X1 - 0.32, X1, Y0, Y1), (X0, X1, Y1 - 0.32, Y1)):          # zij- en achtermuur
        bmesh.ops.create_cube(wb, size=1.0)
    wb.free()
    mur = bmesh.new()
    def addb(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); mur.from_mesh(me_); bpy.data.meshes.remove(me_)
    addb(bz(X0, X0 + 0.34, Y0, Y1, ZG - 0.1, EAVE + 0.1))
    addb(bz(X1 - 0.34, X1, Y0, Y1, ZG - 0.1, EAVE + 0.1))
    addb(bz(X0, X1, Y1 - 0.34, Y1, ZG - 0.1, EAVE + 0.1))
    addb(prism_x([(Y1 - 0.34, EAVE), (Y1, EAVE), (Y1, EAVE + 0.01)], 0, 0.01)) if False else None
    # achtergevel-driehoek tot onder de nok
    gp = [(X0, EAVE - 0.05), (X1, EAVE - 0.05), (0.0, RIDGE - 0.15)]
    tri = bmesh.new(); va = [tri.verts.new((x, Y1 - 0.3, z)) for x, z in gp]; vb = [tri.verts.new((x, Y1, z)) for x, z in gp]
    tri.faces.new(va); tri.faces.new(vb[::-1])
    for i in range(3): tri.faces.new((va[i], vb[i], vb[(i + 1) % 3], va[(i + 1) % 3]))
    bmesh.ops.recalc_face_normals(tri, faces=tri.faces); addb(tri)
    # voormuur onder de kijkramen (verdwijnt achter het kijkplein) + boven de ramen + penanten bij de zuilen
    addb(bz(X0, X1, Y0, Y0 + 0.3, ZG - 0.1, 0.7))
    addb(bz(X0, X1, Y0, Y0 + 0.3, 1.86, 2.62))
    for xa, xb in ((X0, -1.66), (-0.74, -0.46), (0.46, 0.74), (1.66, X1)): addb(bz(xa, xb, Y0, Y0 + 0.3, 0.6, 1.95))
    # deuropening in de linkermuur blijft dicht (deur zit ervoor), venster boven de bordes komt in de klokgevel
    put("muren", "stuc", organisch(mur, 0.06, 3, 0.5, 0.025, 1.2, 0.12))
    coll_box(0, (Y0 + Y1) / 2, (ZG + EAVE) / 2, X1 - X0, Y1 - Y0, EAVE - ZG)

    # ================= kijkramen: drie grote ramen tussen vier bolle zuilen (RK-plattegrond, kijkplein-foto) =================
    for xc in (-1.2, 0.0, 1.2):
        put("ramen", "kijkglas", bz(xc - 0.46, xc + 0.46, Y0 + 0.24, Y0 + 0.26, 0.68, 1.88))                     # glas (donker, kamer erachter)
        put("ramen", "hout", bz(xc - 0.47, xc + 0.47, Y0 - 0.02, Y0 + 0.26, 0.62, 0.72, 0.01))                  # onderdorpel
        put("ramen", "hout", bz(xc - 0.47, xc + 0.47, Y0 - 0.12, Y0 + 0.02, 0.58, 0.66, 0.01))                  # vensterbank
        for s in (-1, 1):                                                                                         # rode gordijnen
            put("ramen", "gordijn", bz(xc + s * 0.44 - 0.1, xc + s * 0.44 + 0.1, Y0 + 0.3, Y0 + 0.36, 0.7, 1.86, 0.03))
        put("ramen", "gordijn", bz(xc - 0.46, xc + 0.46, Y0 + 0.3, Y0 + 0.36, 1.72, 1.86, 0.02))
    put("ramen", "interieur", bz(X0 + 0.35, X1 - 0.35, 1.2, 1.3, 0.0, 2.5))                                     # achterwand kamer
    put("ramen", "tegel", bz(X0 + 0.35, X1 - 0.35, Y0 + 0.3, 1.25, -0.02, 0.02))                                 # vloer rode tegels
    put("ramen", "interieur", bz(X0 + 0.35, X1 - 0.35, Y0 + 0.3, 1.25, 2.4, 2.45))                               # plafond
    LAMPS_.append([0.0, 0.2, 1.9])
    for xc in (-1.8, -0.6, 0.6, 1.8):                                                                             # bolle zuilen, oker (2016)
        prof = [(0, 0.66), (0.14, 0.66), (0.14, 0.74), (0.1, 0.78), (0.11, 0.95), (0.135, 1.2), (0.13, 1.45), (0.1, 1.68), (0.085, 1.76),
                (0.13, 1.79), (0.14, 1.86), (0, 1.86)]
        put("zuilen", "zuil", blathe(prof, 12), TR(xc, Y0 - 0.02, 0))
    # bloemenband boven de ramen (kleurrijk floraal patroon) en dikke houten balk erboven (2016)
    put("band", "stuc", bz(X0 + 0.15, X1 - 0.15, Y0 - 0.04, Y0 + 0.02, 1.9, 2.2, 0.01))
    for i in range(22):
        x = X0 + 0.3 + i * (X1 - X0 - 0.6) / 21
        put("band", "groen", ell((x, Y0 - 0.045, 2.05), (0.09, 0.012, 0.035), 8, 4))
        put("band", ("rood", "pieckblauw", "geel")[i % 3], ell((x + 0.05, Y0 - 0.05, 2.05 + 0.04 * (1 if i % 2 else -1)), (0.035, 0.012, 0.035), 8, 4))
    put("band", "balk", bz(X0 - 0.1, X1 + 0.1, Y0 - 0.16, Y0 + 0.05, 2.2, 2.42, 0.02))

    # ================= overstek met vakwerkgevel (Grootmoedershuisje_herbouwd) =================
    put("gevel", "balk", bz(X0 - 0.25, X1 + 0.25, YG - 0.04, Y0 + 0.1, 2.5, 2.7, 0.02))                          # vloer overstek
    for xj in (-2.2, -1.25, -0.4, 0.4, 1.25, 2.2):                                                                # balkkoppen
        put("gevel", "balk", bz(xj - 0.1, xj + 0.1, YG - 0.25, Y0, 2.52, 2.72, 0.02))
    for s in (-1, 1):                                                                                             # korbelen: schuine stijlen naar de gevelhoeken
        put("gevel", "balk", btube([(s * 2.3, Y0 - 0.05, 1.05), (s * 2.36, Y0 - 0.45, 1.75), (s * 2.42, YG + 0.05, 2.45)], 0.09, 6))
        put("gevel", "balk", btube([(s * 2.0, Y0 - 0.05, 1.95), (s * 2.0, YG + 0.2, 2.4)], 0.06, 6))
    gx = lambda z: XE - (z - EAVE) * XE / (RIDGE - EAVE) - 0.18                                                  # halve breedte onder het dak
    gpts = [(-2.48, 2.6), (2.48, 2.6), (min(2.48, gx(2.6)), max(2.6, EAVE + (XE - 2.48 - 0.18) * (RIDGE - EAVE) / XE)), (0.0, RIDGE - 0.22)]
    gpts = [(-2.5, 2.7), (2.5, 2.7), (2.5, 3.05), (0.0, RIDGE - 0.24), (-2.5, 3.05)]
    gb = bmesh.new(); va = [gb.verts.new((x, YG, z)) for x, z in gpts]; vb = [gb.verts.new((x, Y0 + 0.25, z)) for x, z in gpts]
    gb.faces.new(va[::-1]); gb.faces.new(vb)
    for i in range(len(gpts)): gb.faces.new((va[i], va[(i + 1) % len(gpts)], vb[(i + 1) % len(gpts)], vb[i]))
    bmesh.ops.recalc_face_normals(gb, faces=gb.faces)
    put("gevel", "stuc", organisch(gb, 0.04, 2, 0.4, 0.015, 1.5, 0.3))
    yv = YG - 0.05                                                                                                # vakwerk (donker eiken)
    def vk(a, b, w=0.11): put("gevel", "balk", btube([(a[0], yv, a[1]), (b[0], yv, b[1])], w / 1.6, 4))
    vk((-2.45, 2.68), (2.45, 2.68), 0.16); vk((-1.95, 3.75), (1.95, 3.75), 0.14)
    for s in (-1, 1):
        vk((s * 0.72, 2.68), (s * 0.72, 6.05), 0.13); vk((s * 1.6, 2.68), (s * 1.6, 3.75)); vk((s * 0.72, 3.75), (s * 1.55, 2.75), 0.11)
        vk((s * 0.72, 4.45), (s * 1.25, 3.85), 0.1); vk((s * 0.72, 5.9), (s * 0.3, 6.35), 0.09)
    # raam boven het pad met roeden en flakkerende kaars (sinds 2016 open)
    put("gevel", "glasoranje", bz(-0.42, 0.42, yv - 0.02, yv + 0.06, 4.62, 5.72))
    for k in (1, 2): put("gevel", "balk", bz(-0.42 + 0.84 * k / 3 - 0.015, -0.42 + 0.84 * k / 3 + 0.015, yv - 0.06, yv - 0.02, 4.62, 5.72))
    for k in (1, 2, 3): put("gevel", "balk", bz(-0.42, 0.42, yv - 0.06, yv - 0.02, 4.62 + 1.1 * k / 4 - 0.015, 4.62 + 1.1 * k / 4 + 0.015))
    put("gevel", "balk", bz(-0.52, 0.52, yv - 0.1, yv + 0.04, 4.52, 4.62, 0.01)); put("gevel", "balk", bz(-0.52, 0.52, yv - 0.1, yv + 0.04, 5.72, 5.84, 0.01))
    for s in (-1, 1): put("gevel", "balk", bz(s * 0.42 - (0.1 if s > 0 else 0) + (0 if s > 0 else 0), s * 0.42 + (0.1 if s > 0 else 0) - (0 if s > 0 else 0.1) * 0 + (0 if s > 0 else 0), yv - 0.1, yv + 0.04, 4.62, 5.72)) if False else None
    put("gevel", "balk", bz(-0.52, -0.42, yv - 0.1, yv + 0.04, 4.62, 5.72)); put("gevel", "balk", bz(0.42, 0.52, yv - 0.1, yv + 0.04, 4.62, 5.72))
    LAMPS_.append([0.0, YG + 0.3, 5.1])
    # windveren: brede gebogen donkere planken, aan de voet uitgezwaaid (foto 2016), houten spits op de top
    for s in (-1, 1):
        pts = []
        for i in range(13):
            t = i / 12; x = s * (XE + 0.12) * (1 - t); z = roofz(x) + 0.12 + 0.18 * math.sin(t * math.pi) * 0.5
            pts.append((x, z))
        pts.insert(0, (s * (XE + 0.6), EAVE - 0.5))
        put("gevel", "balk", band(pts if s > 0 else pts[::-1], 0.32, YR0 - 0.08, 0.14))
    put("gevel", "balk", blathe([(0, RIDGE - 0.1), (0.13, RIDGE), (0.11, RIDGE + 0.25), (0.05, RIDGE + 0.6), (0.075, RIDGE + 0.75), (0.02, RIDGE + 1.15), (0, RIDGE + 1.2)], 8), TR(0, YR0 - 0.02, 0))

    # ================= dak: grote bruine schubben in verspringende rijen, rechtlijnig (herbouw 2016) =================
    prof = [(-XE, EAVE - 0.06), (0, RIDGE - 0.02), (XE, EAVE - 0.06), (XE, EAVE - 0.2), (0, RIDGE - 0.18), (-XE, EAVE - 0.2)]
    YC_K, ZK_T = -0.35, 4.0                                                                               # klokgevel onderbreekt de goot links
    def onderlaag(pr, ya, yb):
        pb = bmesh.new(); va = [pb.verts.new((x, ya, z)) for x, z in pr]; vb = [pb.verts.new((x, yb, z)) for x, z in pr]
        pb.faces.new(va); pb.faces.new(vb[::-1])
        for i in range(len(pr)): pb.faces.new((va[i], vb[i], vb[(i + 1) % len(pr)], va[(i + 1) % len(pr)]))
        bmesh.ops.recalc_face_normals(pb, faces=pb.faces); put("dak", "hout", pb)
    xk_t = -(XE - (ZK_T - EAVE) * XE / (RIDGE - EAVE))
    onderlaag([(0, RIDGE - 0.02), (XE, EAVE - 0.06), (XE, EAVE - 0.2), (0, RIDGE - 0.18)], YR0 + 0.04, YR1)
    for ya, yb in ((YR0 + 0.04, YC_K - 1.08), (YC_K + 1.08, YR1)): onderlaag([(-XE, EAVE - 0.06), (0, RIDGE - 0.02), (0, RIDGE - 0.18), (-XE, EAVE - 0.2)], ya, yb)
    xw = X0 - 0.05; zw = roofz(xw)
    onderlaag([(xw, zw - 0.06), (0, RIDGE - 0.02), (0, RIDGE - 0.18), (xw, zw - 0.2)], YC_K - 1.08, YC_K + 1.08)
    BR = bell_pts(1.05, 2.05); BR = sorted([(z, y) for y, z in BR if y >= 0])
    def bell_hw(z):
        if z < BR[0][0] or z > BR[-1][0]: return -1.0
        for (za, ya), (zb, yb) in zip(BR, BR[1:]):
            if za <= z <= zb: return ya + (yb - ya) * (z - za) / max(1e-6, zb - za)
        return -1.0
    rng = random.Random(7)
    for side in (-1, 1):
        P0 = Vector((side * XE, 0, EAVE)); P1 = Vector((0, 0, RIDGE)); es = (P1 - P0); L = es.length; es.normalize()
        ey = Vector((0, 1, 0)); nrm = (es.cross(ey) if side < 0 else ey.cross(es)).normalized()
        if nrm.z < 0: nrm = -nrm
        rows = int(L / 0.17)
        for r in range(rows):
            sv = r * 0.17 + 0.06; yy = YR0 + (0.11 if r % 2 else 0.0)
            while yy < YR1 - 0.02:
                w = rng.uniform(0.2, 0.28); w = min(w, YR1 - yy)
                c = P0 + es * sv + nrm * (0.03 + rng.uniform(0, 0.01)); c = Vector((c.x, yy + w / 2, c.z))
                if side < 0 and abs(c.y - YC_K) < 1.1 and (c.x < X0 - 0.08 or abs(c.y - YC_K) < bell_hw(c.z) + 0.06): yy += w; continue
                sl = bmesh.new(); bmesh.ops.create_cube(sl, size=1.0); bmesh.ops.scale(sl, vec=(0.3, w - 0.018, 0.022), verts=sl.verts)
                ex_ = es; basis = Matrix(((ex_.x, 0, nrm.x, 0), (ex_.y, 1, nrm.y, 0), (ex_.z, 0, nrm.z, 0), (0, 0, 0, 1)))
                tilt = Matrix.Rotation(math.radians(-side * 0) , 4, "Y") @ Matrix.Rotation(math.radians(rng.uniform(-3, 3)), 4, "Z")
                # schub ligt met de onderrand iets op: draai om de rij-as (y) naar buiten
                lift = Matrix.Rotation(math.radians(5 + rng.uniform(-1.5, 2)) * (1 if side > 0 else -1), 4, "Y")
                bmesh.ops.transform(sl, matrix=Matrix.Translation(c) @ basis @ lift @ tilt, verts=sl.verts)
                put("dak", "lei", sl)
                yy += w
    put("dak", "balk", btube([(0, YR0, RIDGE + 0.04), (0, YR1, RIDGE + 0.04)], 0.08, 6))                        # nokbalk
    # platte donkere dakkapel als spiedend oog op het linkerdakvlak (Roodkapje-zijgevel)
    yk = 1.25; xk = -1.35; zk = roofz(xk)
    put("dakkapel", "lei", prism_x([(yk - 0.75, zk + 0.02), (yk, zk + 0.42), (yk + 0.75, zk + 0.02), (yk + 0.75, zk - 0.1), (yk - 0.75, zk - 0.1)], xk - 0.45, xk + 0.9))
    put("dakkapel", "venster", ell((xk - 0.45, yk, zk + 0.12), (0.03, 0.4, 0.09), 10, 6))
    put("dakkapel", "balk", ell((xk - 0.46, yk, zk + 0.2), (0.04, 0.48, 0.05), 10, 4))

    # ================= klokgevel met venster en windwijzer boven de voordeur (linkerzijde) =================
    yc = -0.35
    bp = bell_pts(1.05, 2.05)
    put("klokgevel", "stuc", organisch(prism_x([(yc + y, z) for y, z in bp], X0 - 0.12, -0.55), 0.04, 3, 0.5, 0.015, 1.4, 0.3))
    for y, z in bp[1:-1:3]: pass
    put("klokgevel", "venster", boutline(arch_pts(0, 3.2, 0.26, 0.58, 8), -0.04, 0.06),
        Matrix.Translation((X0 - 0.13, yc, 0)) @ Matrix.Rotation(math.radians(-90), 4, "Z"))
    put("klokgevel", "ijzer", btube([(X0 + 0.2, yc, 4.05), (X0 + 0.2, yc, 4.75)], 0.02, 6))
    put("klokgevel", "goud", bz(X0 + 0.19, X0 + 0.21, yc, yc + 0.32, 4.45, 4.66))
    put("klokgevel", "goud", ell((X0 + 0.2, yc, 4.75), (0.04, 0.04, 0.04), 8, 6))
    # voordeur Pieckblauw met stenen omlijsting (2016), raampje en klopper; afdakje met twee schoren; bel
    dp = arch_pts(0, 0.0, 0.95, 1.85, 12)
    MD = Matrix.Translation((X0 - 0.02, yc, 0)) @ Matrix.Rotation(math.radians(-90), 4, "Z")
    put("deur", "pieckblauw", boutline(dp, -0.04, 0.06), MD)
    for k in range(4): put("deur", "hout", bz(-0.475 + 0.95 * (k + 1) / 5 - 0.008, -0.475 + 0.95 * (k + 1) / 5 + 0.008, -0.05, -0.04, 0.05, 1.45), MD)
    put("deur", "venster", bz(-0.15, 0.15, -0.06, -0.04, 1.05, 1.35), MD)
    put("deur", "hout", bz(-0.01, 0.01, -0.07, -0.05, 1.05, 1.35), MD); put("deur", "hout", bz(-0.15, 0.15, -0.07, -0.05, 1.19, 1.21), MD)
    for zz in (0.3, 1.5): put("deur", "ijzer", bz(-0.45, 0.1, -0.065, -0.05, zz - 0.03, zz + 0.03), MD)
    put("deur", "ijzer", blathe([(0, 0), (0.05, 0), (0.05, 0.012), (0, 0.025)], 8), MD @ TR(0.3, -0.07, 0.95) @ Matrix.Rotation(math.radians(90), 4, "X"))
    put("deur", "natuursteen", organisch(band(dp, 0.17, -0.09, 0.12), 0.03, 2, 0.4, 0.02, 2.0, 0.4), MD)
    ca = [(yc - 0.75, 2.02), (yc + 0.75, 2.02)]
    put("afdak", "lei", prism_x([(yc - 0.8, 1.98), (yc + 0.8, 1.98), (yc + 0.8, 2.12), (yc, 2.32), (yc - 0.8, 2.12)], X0 - 0.68, X0 + 0.02) if False else
        bz(X0 - 0.68, X0 + 0.02, yc - 0.82, yc + 0.82, 1.98, 2.1))
    put("afdak", "lei", bmesh_tilt_roof(X0 - 0.7, X0 + 0.02, yc - 0.84, yc + 0.84, 2.1, 2.38))
    for s in (-1, 1):
        put("afdak", "balk", bz(X0 - 0.62, X0 - 0.5, yc + s * 0.68 - 0.05, yc + s * 0.68 + 0.05, 1.55, 1.98, 0.01))
        put("afdak", "balk", btube([(X0 - 0.02, yc + s * 0.68, 1.45), (X0 - 0.56, yc + s * 0.68, 1.95)], 0.035, 5))
    put("bel", "goud", blathe([(0, 0), (0.07, 0), (0.065, 0.03), (0.045, 0.1), (0.02, 0.13), (0, 0.135)], 10), TR(X0 - 0.3, yc + 0.98, 1.66))
    put("bel", "ijzer", btube([(X0 - 0.02, yc + 0.98, 1.95), (X0 - 0.3, yc + 0.98, 1.95), (X0 - 0.3, yc + 0.98, 1.8)], 0.012, 5))
    put("bel", "ijzer", btube([(X0 - 0.3, yc + 0.98, 1.66), (X0 - 0.3, yc + 0.98, 1.0)], 0.006, 4))           # koord

    # ================= bordes met oranjerode tegels, kelderdeur en houtgewelf eronder, trap naar achter =================
    bs = bmesh.new()
    me_ = bpy.data.meshes.new("_t"); b_ = bz(BX0, X0 + 0.05, BY0, BY1, ZG - 0.1, -0.06); b_.to_mesh(me_); b_.free(); bs.from_mesh(me_); bpy.data.meshes.remove(me_)
    put("bordes", "stuc", organisch(bs, 0.06, 3, 0.5, 0.03, 1.0, 0.14))
    put("bordes", "tegel", bz(BX0 - 0.04, X0 + 0.02, BY0, BY1 + 0.02, -0.08, 0.0))
    for i in range(1, 17): yy = BY0 + i * (BY1 - BY0) / 17; put("bordes", "natuursteen", bz(BX0 - 0.04, X0, yy - 0.006, yy + 0.006, -0.002, 0.004))
    put("bordes", "natuursteen", bz(BX0 - 0.1, BX0 + 0.06, BY0, BY1, -0.14, -0.02, 0.01))                             # rand
    MS = Matrix.Translation((BX0 - 0.01, 0, 0)) @ Matrix.Rotation(math.radians(-90), 4, "Z")                        # oostvlak (kijkt naar -X)
    for yy, w, h, kind in ((0.35, 0.9, 1.65, "deur"), (-1.6, 1.15, 1.4, "hout")):
        ap = [(x, z + ZG) for x, z in arch_pts(0, 0, w, h, 12)]
        Mk = MS @ TR(-yy, 0, 0)
        put("kelder", "natuursteen", organisch(band(ap, 0.16, -0.06, 0.12), 0.03, 2, 0.4, 0.025, 2.0, 0.4), Mk)
        if kind == "deur":
            put("kelder", "groen", boutline(ap, -0.045, 0.06), Mk)
            for k in range(4): put("kelder", "hout", bz(-w / 2 + w * (k + 1) / 5 - 0.008, -w / 2 + w * (k + 1) / 5 + 0.008, -0.055, -0.045, ZG + 0.05, ZG + h - 0.4), Mk)
            for zz in (ZG + 0.35, ZG + 1.2): put("kelder", "ijzer", btube([(-w / 2 + 0.05, -0.06, zz), (0.15, -0.06, zz), (0.25, -0.06, zz + 0.1)], 0.018, 5), Mk)
        else:
            put("kelder", "venster", boutline(ap, -0.02, 0.03), Mk)                                                  # donker gewelf
            rr = random.Random(5)
            for k in range(70):                                                                                   # opgestapeld brandhout
                x = rr.uniform(-w / 2 + 0.08, w / 2 - 0.08); z = ZG + 0.06 + rr.uniform(0, h - 0.35)
                if z - ZG > h - w / 2 and abs(x) > math.sqrt(max(0.0, (w / 2 - 0.08) ** 2 - (z - ZG - (h - w / 2)) ** 2)): continue
                rad = rr.uniform(0.045, 0.07)
                put("kelder", "brandhout", btube([(x, -0.12, z), (x, 0.05, z)], rad, 6), Mk)
    # trap (OSM 766787194): 11 treden van z 0 naar -1.9, van Y 1.7 naar 4.84, 0.95 breed tegen de bordesmuur
    TX0, TX1 = BX0 + 0.05, BX0 + 1.0
    n = 11
    for i in range(n):
        y0 = BY1 + i * (4.84 - BY1) / n; y1 = BY1 + (i + 1) * (4.84 - BY1) / n; z = -(i + 1) * 1.9 / (n + 0) + 0.0
        put("trap", "natuursteen", bz(TX0, TX1, y0 - 0.03, y1, ZG - 0.05, z + 0.0, 0.015))
        coll_box((TX0 + TX1) / 2, (y0 + y1) / 2, (ZG + z) / 2, TX1 - TX0, y1 - y0, z - ZG)
    put("trap", "stuc", organisch(prism_x([(BY1, -0.06), (4.9, ZG - 0.1), (BY1, ZG - 0.1)], TX1, TX1 + 0.3), 0.05, 2, 0.4, 0.02, 1.0, 0.3))
    coll_box((BX0 + X0) / 2, (BY0 + BY1) / 2, (ZG - 0.06) / 2, X0 - BX0, BY1 - BY0, -0.06 - ZG)
    # leuning met krullen langs de bordes en de trap af, ijzeren poortje naar het pad (OSM 7161368031)
    posts = [BY0 + 0.75 + k * 0.9 for k in range(6)]
    for yy in posts: put("leuning", "ijzer", btube([(BX0 + 0.06, yy, 0), (BX0 + 0.06, yy, 0.95)], 0.02, 6))
    put("leuning", "ijzer", btube([(BX0 + 0.06, BY0 + 0.75, 0.95), (BX0 + 0.06, BY1, 0.95)], 0.025, 6))
    for yy in posts[:-1]:
        for k in range(8):
            a = k / 8 * math.tau
            put("leuning", "ijzer", btube([(BX0 + 0.06, yy + 0.45 + 0.13 * math.cos(a), 0.45 + 0.13 * math.sin(a)),
                                          (BX0 + 0.06, yy + 0.45 + 0.13 * math.cos(a + math.tau / 8), 0.45 + 0.13 * math.sin(a + math.tau / 8))], 0.01, 4))
    put("leuning", "ijzer", btube([(BX0 + 0.06, BY1, 0.95), (BX0 + 0.06, 4.84, ZG + 0.95), (BX0 + 0.06, 5.0, ZG + 0.85),
                                   (BX0 + 0.06, 5.05, ZG + 0.7), (BX0 + 0.06, 4.95, ZG + 0.66)], 0.022, 6))
    put("leuning", "ijzer", btube([(BX0 + 0.06, 4.84, ZG), (BX0 + 0.06, 4.84, ZG + 0.95)], 0.02, 6))
    coll_box(BX0 + 0.06, (BY0 + 0.75 + BY1) / 2, 0.5, 0.1, BY1 - BY0 - 0.75, 1.0)
    gx0, gx1 = BX0 + 0.02, BX0 + 0.72                                                                               # poortje
    put("poort", "ijzer", btube([(gx0, BY0 + 0.04, 0), (gx0, BY0 + 0.04, 1.02)], 0.03, 6))
    put("poort", "ijzer", btube([(gx1, BY0 + 0.04, 0), (gx1, BY0 + 0.04, 1.02)], 0.03, 6))
    for z in (0.08, 0.9): put("poort", "ijzer", bz(gx0, gx1, BY0 + 0.025, BY0 + 0.055, z, z + 0.03))
    for k in range(1, 8): x = gx0 + (gx1 - gx0) * k / 8; put("poort", "ijzer", bz(x - 0.008, x + 0.008, BY0 + 0.03, BY0 + 0.05, 0.08, 0.95))
    put("poort", "ijzer", btube([(gx0, BY0 + 0.04, 0.93), (gx0 + 0.15, BY0 + 0.04, 1.06), ((gx0 + gx1) / 2, BY0 + 0.04, 1.1), (gx1 - 0.15, BY0 + 0.04, 1.06), (gx1, BY0 + 0.04, 0.93)], 0.012, 4))
    coll_box((gx0 + gx1) / 2, BY0 + 0.04, 0.5, gx1 - gx0, 0.08, 1.0)
    # vogelhuisje van Krakeeltje op een klimopbegroeide houten paal naast de bordes (figuur zelf komt later)
    vx, vy = BX0 + 0.15, BY0 + 0.4
    put("vogelhuis", "hout", btube([(vx, vy, -0.05), (vx, vy, 1.75)], 0.07, 7))
    rr = random.Random(3)
    for k in range(60):
        z = rr.uniform(0.0, 1.6); a = rr.uniform(0, math.tau)
        put("vogelhuis", "klimop", ell((vx + 0.08 * math.cos(a), vy + 0.08 * math.sin(a), z), (0.06, 0.06, 0.03), 6, 4))
    put("vogelhuis", "hout", bz(vx - 0.2, vx + 0.2, vy - 0.17, vy + 0.17, 1.75, 2.15, 0.01))
    put("vogelhuis", "venster", ell((vx - 0.205, vy, 2.0), (0.01, 0.06, 0.06), 8, 6))
    put("vogelhuis", "balk", btube([(vx - 0.3, vy, 1.92), (vx - 0.21, vy, 1.92)], 0.012, 5))
    put("vogelhuis", "groen", prism_x([(vy - 0.27, 2.12), (vy, 2.36), (vy + 0.27, 2.12), (vy + 0.27, 2.08), (vy, 2.31), (vy - 0.27, 2.08)], vx - 0.28, vx + 0.28) if False else
        bmesh_tilt_roof(vx - 0.28, vx + 0.28, vy - 0.27, vy + 0.27, 2.12, 2.38, axis="x"))
    put("vogelhuis", "zink", blathe([(0, 0), (0.08, 0), (0.09, 0.05), (0, 0.05)], 10), TR(vx + 0.05, vy - 0.27, 1.6))  # drinkbakje
    put("vogelhuis", "hout", bz(vx - 0.02, vx + 0.02, vy - 0.27, vy - 0.06, 1.6, 1.63))
    coll_box(vx, vy, 1.0, 0.2, 0.2, 2.0)

    # ================= gietijzeren straatlamp op de hoek boven het trappetje (OSM 7165020178) =================
    lx, ly, lz = X0 - 0.05, Y1 - 0.05, 2.0
    put("lamp", "ijzer", btube([(lx, ly, lz + 0.55), (lx - 0.5, ly + 0.3, lz + 0.55), (lx - 0.55, ly + 0.33, lz + 0.45)], 0.025, 6))
    put("lamp", "ijzer", btube([(lx, ly, lz + 0.1), (lx - 0.3, ly + 0.18, lz + 0.55)], 0.02, 5))
    ML = TR(lx - 0.55, ly + 0.33, lz - 0.12, 45)
    put("lamp", "ijzer", blathe([(0, 0.6), (0.06, 0.6), (0.2, 0.47), (0.17, 0.44), (0.14, 0.44), (0.14, 0.05), (0.1, 0.0), (0.03, -0.06), (0, -0.07)], 4), ML)
    put("lamp", "glaslamp", blathe([(0, 0.03), (0.13, 0.03), (0.13, 0.42), (0, 0.42)], 4), ML)
    LAMPS_.append([lx - 0.55, ly + 0.33, lz + 0.1])

    # ================= ronde toren op de achterhoek rechts (strakke kegel sinds 2016) + schoorsteen rechts =================
    tprof = [(0, ZG - 0.1), (1.02, ZG - 0.1), (0.98, ZG + 1.2), (0.93, 1.5), (0.9, 3.4), (0.95, 4.6), (0.92, 5.45), (0.98, 5.6), (0, 5.6)]
    put("toren", "stuc", organisch(blathe(tprof, 20), 0.06, 3, 0.5, 0.03, 1.0, 0.14), TR(TOW.x, TOW.y, 0))
    coll_box(TOW.x, TOW.y, (ZG + 5.6) / 2, 1.8, 1.8, 5.6 - ZG)
    for a, z in ((20, 0.9), (-40, 2.6), (60, 3.9), (-10, 4.6)):                                                    # smalle vensters
        Mw = TR(TOW.x, TOW.y, 0, -90 + a) @ Matrix.Translation((0, -0.93, 0))
        put("toren", "venster", bz(-0.08, 0.08, -0.04, 0.04, z, z + 0.45), Mw)
        put("toren", "natuursteen", bz(-0.12, 0.12, -0.06, 0.02, z - 0.06, z), Mw)
    for k in range(9):                                                                                             # kegeldak in schubbenrijen
        t0 = k / 9; t1 = (k + 1.25) / 9
        r0 = 1.18 * (1 - t0) + 0.02; r1 = 1.18 * (1 - t1) + 0.02; z0 = 5.55 + t0 * 1.85; z1 = 5.55 + t1 * 1.85
        put("torendak", "lei", blathe([(0, z0 - 0.05), (r0, z0 - 0.05), (r0 - 0.01, z0), (max(r1, 0.0), min(z1, 7.4)), (0, min(z1, 7.4))], 20), TR(TOW.x, TOW.y, 0))
    put("torendak", "ijzer", btube([(TOW.x, TOW.y, 7.35), (TOW.x, TOW.y, 8.15)], 0.022, 6))
    put("torendak", "goud", ell((TOW.x, TOW.y, 7.62), (0.06, 0.06, 0.06), 8, 6))
    put("torendak", "goud", bz(TOW.x - 0.01, TOW.x + 0.01, TOW.y, TOW.y + 0.42, 7.8, 8.05))
    put("torendak", "goud", ell((TOW.x, TOW.y, 8.15), (0.035, 0.035, 0.035), 8, 6))
    sch = bmesh.new()
    for b_ in (bz(X1 - 0.1, X1 + 0.52, -0.95, 0.45, ZG - 0.1, 2.1), bz(X1 - 0.05, X1 + 0.42, -0.8, 0.3, 2.0, 5.3)):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); sch.from_mesh(me_); bpy.data.meshes.remove(me_)
    put("schoorsteen", "stuc", organisch(sch, 0.06, 6, 0.6, 0.03, 1.0, 0.14))
    put("schoorsteen", "zink", btube([(X1 + 0.18, -0.25, 5.2), (X1 + 0.18, -0.25, 6.05)], 0.09, 10))
    put("schoorsteen", "zink", blathe([(0, 0.0), (0.24, 0.0), (0.0, 0.2)], 10), TR(X1 + 0.18, -0.25, 6.15))
    coll_box(X1 + 0.2, -0.25, (ZG + 5.3) / 2, 0.6, 1.4, 5.3 - ZG)

    # wegschrijven
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"RK_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_}, open(os.path.join(out, "huisje_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


def bmesh_tilt_roof(x0, x1, y0, y1, zlo, zhi, axis="y"):
    """klein zadeldakje: nok langs x (axis='y': loopt af naar y0/y1) of langs y (axis='x')"""
    bm = bmesh.new()
    if axis == "y":
        prof = [(y0, zlo), (y1, zlo), ((y0 + y1) / 2, zhi)]
        a = [bm.verts.new((x0, y, z)) for y, z in prof]; b = [bm.verts.new((x1, y, z)) for y, z in prof]
    else:
        prof = [(x0, zlo), (x1, zlo), ((x0 + x1) / 2, zhi)]
        a = [bm.verts.new((x, y0, z)) for x, z in prof]; b = [bm.verts.new((x, y1, z)) for x, z in prof]
    bm.faces.new(a); bm.faces.new(b[::-1])
    for i in range(3): bm.faces.new((a[i], b[i], b[(i + 1) % 3], a[(i + 1) % 3]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
