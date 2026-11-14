"""03_decor De Nieuwe Kleren van de Keizer (2012, ontwerp Pim-Martijn Sanders): barok-rococo paleismuur met middenpoort, nispijlers met kuiven,
urnpijlers, lakei- & poorthuizen, gouden poort, achthoekige theekoepel met blauwe glazen koepel, voorbak met postamenten, lange vijver.
Maten uit de BOUWTEKENINGEN (ref/tekeningen: plattegrond_overzicht ~48.75 px/m met vijver 20000x2500, aanzicht1/2 met peilen) + foto's.
Modelframe: oorsprong = midden lange vijver, x = rechts voor de bezoeker (west), y = de diepte in (naar de muur, zuid), z op;
z = 0 bezoekerspad (600-P), decorpeil Z0 = 0.6 (0+P). Voorkant kijkt naar -Y. Gebruik: Blender -b -P 03_decor.py -- --master KK_decor_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
RNG = random.Random(2012)
MATS = {"pleister": ((0.9, 0.86, 0.76, 1), 0.85), "ornament": ((0.96, 0.95, 0.9, 1), 0.6), "goud": ((0.82, 0.62, 0.22, 1), 0.3),
        "koepelglas": ((0.45, 0.55, 0.75, 1), 0.15), "venster": ((0.12, 0.14, 0.18, 1), 0.2), "raamhout": ((0.94, 0.92, 0.86, 1), 0.5),
        "water": ((0.08, 0.1, 0.09, 1), 0.05), "bodem": ((0.06, 0.06, 0.06, 1), 0.9), "ijzer": ((0.04, 0.04, 0.04, 1), 0.45),
        "glaslamp": ((0.95, 0.8, 0.5, 1), 0.2), "donker": ((0.03, 0.03, 0.03, 1), 0.9), "gordijn": ((0.85, 0.82, 0.72, 1), 0.9)}
Z0 = 0.6                     # decorpeil (0+P) boven het bezoekerspad
WAND = 2.85                  # achtermuur 2850+P (aanzicht2)


def M_seg(a, b, z=0.0):
    """matrix: oorsprong in a, lokaal x langs a->b, lokaal -y naar de bezoeker (voorkant)"""
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    return Matrix.Translation((a[0], a[1], z)) @ Matrix.Rotation(ang, 4, "Z"), math.hypot(b[0] - a[0], b[1] - a[1]), math.degrees(ang)


def muur(a, b, h=WAND, t=0.36, part="muur", kroon=True):
    """gestucte muur van a naar b op decorpeil, met plint en kroonlijst (aanzicht: strakke lijsten)"""
    M, L, ang = M_seg(a, b, Z0)
    put(part, "pleister", bz(0, L, -t / 2, t / 2, -0.05, h), M)
    put(part, "ornament", bz(-0.02, L + 0.02, -t / 2 - 0.05, t / 2 + 0.05, -0.05, 0.28, 0.01), M)             # plint
    if kroon:
        put(part, "ornament", bz(-0.04, L + 0.04, -t / 2 - 0.07, t / 2 + 0.07, h - 0.12, h + 0.02, 0.01), M)  # kroonlijst
        put(part, "ornament", bz(0, L, -t / 2 - 0.035, t / 2 + 0.035, h - 0.24, h - 0.12, 0.01), M)
    coll_box((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, Z0 + h / 2, L + 0.1, t + 0.1, h, ang)


def paneel(M, x0, x1, z0, z1, y=-0.19, part="muur"):
    """verdiept/opgelegd paneel met lijst (de muurvlakken in Bouwnieuwe zijn in velden verdeeld)"""
    for (a, b, c, d) in ((x0, x1, z0, z0 + 0.05), (x0, x1, z1 - 0.05, z1), (x0, x0 + 0.05, z0, z1), (x1 - 0.05, x1, z0, z1)):
        put(part, "ornament", bz(a, b, y - 0.025, y + 0.01, c, d), M)


def urnkap(x, y, z, s=1.0, rz=0, part="urnen"):
    """getrapte vierkante kap met kussen en knop (Bouwnieuwe: de 'taartvormige' kappen op de pijlers)"""
    M = TR(x, y, z, rz)
    put(part, "ornament", bz(-0.5 * s, 0.5 * s, -0.5 * s, 0.5 * s, 0.0, 0.1 * s, 0.01), M)
    put(part, "ornament", bz(-0.42 * s, 0.42 * s, -0.42 * s, 0.42 * s, 0.1 * s, 0.3 * s, 0.02), M)
    put(part, "ornament", blathe([(0, 0.3 * s), (0.36 * s, 0.3 * s), (0.34 * s, 0.4 * s), (0.22 * s, 0.52 * s), (0.12 * s, 0.6 * s), (0, 0.62 * s)], 4), M @ Matrix.Rotation(math.pi / 4, 4, "Z"))
    put(part, "ornament", blathe([(0, 0.6 * s), (0.06 * s, 0.62 * s), (0.1 * s, 0.7 * s), (0.06 * s, 0.8 * s), (0, 0.84 * s)], 10), M)


def krul(M, x, z, r, sx=1, turns=1.4, y=-0.2, dik=0.045, part="ornament", mat="ornament"):
    """C-/S-krul: spiraal in het XZ-vlak (rococo-voluut)"""
    pts = []
    for i in range(26):
        t = i / 25; a = math.pi * 0.5 + sx * t * turns * math.tau; rr = r * (1 - 0.72 * t)
        pts.append((x + sx * rr * math.cos(a) * -1, y, z + rr * math.sin(a)))
    put(part, mat, btube(pts, dik * (1 - 0.4 * 0), 6), M)


def kuif(M, x, z, w=1.2, h=1.0, y=-0.12, part="ornament"):
    """rococo-bekroning: cartouche met gouden medaillon, twee grote C-krullen, schelp/vlam bovenop (DNKvdK-bouw, Kleermakers)"""
    put(part, "ornament", ell((x, y, z + h * 0.42), (w * 0.2, 0.09, h * 0.3), 14, 8), M)                              # cartouche
    put(part, "goud", ell((x, y - 0.07, z + h * 0.42), (w * 0.11, 0.04, h * 0.17), 12, 8), M)
    ring = [(x + w * 0.22 * math.cos(a), y - 0.06, z + h * 0.42 + h * 0.32 * math.sin(a)) for a in [i * math.tau / 20 for i in range(21)]]
    put(part, "ornament", btube(ring, 0.035, 6), M)
    for sx in (-1, 1):
        krul(M, x + sx * w * 0.36, z + h * 0.28, w * 0.2, sx=-sx, turns=1.2, y=y, dik=0.05)
        krul(M, x + sx * w * 0.2, z + h * 0.78, w * 0.12, sx=sx, turns=1.1, y=y, dik=0.035)
        put(part, "ornament", btube([(x + sx * w * 0.5, y, z + 0.02), (x + sx * w * 0.42, y, z + h * 0.18), (x + sx * w * 0.3, y, z + h * 0.2)], 0.045, 6), M)
    put(part, "ornament", btube([(x, y, z + h * 0.75), (x - 0.04, y, z + h * 0.9), (x, y, z + h), (x + 0.04, y, z + h * 0.9), (x, y, z + h * 0.75)], 0.04, 6), M)
    put(part, "ornament", bz(x - w * 0.5, x + w * 0.5, y - 0.08, y + 0.08, z - 0.04, z + 0.04, 0.01), M)


def kuif2(M, x, z, w=1.2, h=1.0, y=-0.12, part="ornament", kroon=False, guirlande=True):
    """rococo-bekroning v2 (Intro_nieuwekleren, Kleermakers): gebeeldhouwd -> bollen langs spiralen + cartouche, samengesmolten met
    voxel-remesh (organisch) tot vloeiende acanthuskrullen; goud medaillon met bloem, optioneel gouden kroon en gouden guirlande eronder."""
    acc = bmesh.new()
    def add(bm):
        me = bpy.data.meshes.new("_k"); bm.to_mesh(me); bm.free(); acc.from_mesh(me); bpy.data.meshes.remove(me)
    def spiraal(cx, cz, r, sx, turns, d0, d1, tilt=0.0, n=18):
        for i in range(n):
            t = i / (n - 1); a = math.pi * 0.5 + sx * t * turns * math.tau + tilt; rr = r * (1 - 0.75 * t); d = d0 + (d1 - d0) * t
            add(ell((x + cx - sx * rr * math.cos(a), y, z + cz + rr * math.sin(a)), (d, d * 0.9, d), 8, 6))
    add(bz(x - w * 0.5, x + w * 0.5, y - 0.1, y + 0.1, z - 0.05, z + 0.06))                                     # voet
    add(ell((x, y, z + h * 0.46), (w * 0.2, 0.1, h * 0.3), 16, 10))                                                # cartouche
    for i in range(22):                                                                                           # dikke lijst om de cartouche
        a = i * math.tau / 22; add(ell((x + w * 0.22 * math.cos(a), y - 0.05, z + h * 0.46 + h * 0.33 * math.sin(a)), (0.05, 0.05, 0.05), 6, 4))
    for sx in (-1, 1):
        spiraal(sx * w * 0.38, h * 0.3, w * 0.2, -sx, 1.25, 0.085, 0.03)                                         # grote C-krul onder
        spiraal(sx * w * 0.22, h * 0.82, w * 0.12, sx, 1.1, 0.06, 0.025)                                         # S-krul boven
        for k in range(7):                                                                                        # bladlobben langs de rand
            t = k / 6; add(ell((x + sx * (w * 0.5 - t * w * 0.25), y, z + 0.06 + t * h * 0.25), (0.06, 0.05, 0.04), 6, 4))
    for k in range(5):                                                                                            # schelp/waaier bovenop
        a = math.radians(55 + k * 17.5); add(ell((x + 0.12 * math.cos(a), y, z + h * 0.86 + 0.12 * math.sin(a)), (0.035, 0.04, 0.11), 6, 5))
    put(part, "ornament", organisch(acc, 0.028, 3, 0.55, 0.004, 3.0, 0.18), M)
    put(part, "goud", ell((x, y - 0.1, z + h * 0.46), (w * 0.12, 0.035, h * 0.18), 14, 8), M)                    # gouden medaillon
    put(part, "goud", btube([(x + w * 0.13 * math.cos(a), y - 0.12, z + h * 0.46 + h * 0.2 * math.sin(a)) for a in [i * math.tau / 20 for i in range(21)]], 0.012, 5), M)
    put(part, "ornament", ell((x, y - 0.13, z + h * 0.48), (0.035, 0.02, 0.05), 6, 4), M)                        # bloempje
    if kroon:                                                                                                     # gouden kroon (Intro: op de nispijler)
        kz = z + h + 0.05
        put(part, "goud", blathe([(0, kz), (0.15, kz), (0.17, kz + 0.06), (0.13, kz + 0.1), (0.15, kz + 0.2), (0, kz + 0.16)], 14), M @ Matrix.Translation((x, y, 0)))
        for k in range(8):
            a = k * math.tau / 8; put(part, "goud", ell((x + 0.15 * math.cos(a), y + 0.15 * math.sin(a), kz + 0.24), (0.025, 0.025, 0.04), 6, 4), M)
        put(part, "goud", ell((x, y, kz + 0.3), (0.04, 0.04, 0.05), 8, 6), M)
    if guirlande:                                                                                                 # gouden guirlande met kwasten onder de bekroning
        gz = z - 0.35
        for sx in (-1, 1):
            pts = [(x + sx * (0.05 + t * w * 0.38), y - 0.04, gz + 0.22 - 0.22 * math.sin(math.pi * t)) for t in [i / 10 for i in range(11)]]
            put(part, "goud", btube(pts, 0.035, 6), M)
            put(part, "goud", ell((x + sx * w * 0.43, y - 0.04, gz + 0.2), (0.05, 0.04, 0.05), 6, 4), M)
            put(part, "goud", ell((x + sx * w * 0.43, y - 0.04, gz - 0.02), (0.025, 0.025, 0.12), 6, 4), M)
        put(part, "goud", ell((x, y - 0.05, gz + 0.22), (0.06, 0.045, 0.06), 6, 4), M)
        put(part, "goud", ell((x, y - 0.05, gz - 0.05), (0.03, 0.03, 0.15), 6, 4), M)


def oeil(M, x, z, r=0.26, y=-0.22, part="ornament"):
    """oeil-de-boeuf: ronde lijst met donker hart en gouden guirlande eronder (DNKvdK-bouw, Hofdames)"""
    ring = [(x + r * math.cos(a), y, z + r * 1.08 * math.sin(a)) for a in [i * math.tau / 24 for i in range(25)]]
    put(part, "ornament", btube(ring, 0.05, 6), M)
    put(part, "pleister", boutline([(x + r * 0.85 * math.cos(a), z + r * 0.92 * math.sin(a)) for a in [i * math.tau / 16 for i in range(16)]], y + 0.02, 0.03), M)
    put(part, "ornament", ell((x, y - 0.02, z + r * 1.15), (0.07, 0.05, 0.08), 8, 6), M)
    g = [(x + r * 0.9 * math.cos(a), y - 0.04, z - r * 0.55 - 0.12 * math.sin(math.pi * (a - math.pi) / math.pi)) for a in [math.pi + i * math.pi / 10 for i in range(11)]]
    put(part, "goud", btube(g, 0.03, 5), M)


def pijler(cx, cy, rz, w, d, h, part="pijlers", nis=False, kap=True, kuif_h=0.0):
    """pijler met plint, pilasterlijsten, kroonlijst; optioneel een rondboognis (met fonteintje) en een kap of kuif"""
    M = TR(cx, cy, Z0, rz)
    put(part, "pleister", bz(-w / 2, w / 2, -d / 2, d / 2, -0.05, h), M)
    put(part, "ornament", bz(-w / 2 - 0.05, w / 2 + 0.05, -d / 2 - 0.05, d / 2 + 0.05, -0.05, 0.32, 0.01), M)
    put(part, "ornament", bz(-w / 2 - 0.08, w / 2 + 0.08, -d / 2 - 0.08, d / 2 + 0.08, h - 0.16, h, 0.01), M)
    put(part, "ornament", bz(-w / 2 - 0.04, w / 2 + 0.04, -d / 2 - 0.04, d / 2 + 0.04, h - 0.3, h - 0.16, 0.01), M)
    for sx in (-1, 1): put(part, "ornament", bz(sx * w / 2 - 0.09, sx * w / 2 + 0.09, -d / 2 - 0.03, -d / 2 + 0.02, 0.32, h - 0.3), M)
    if nis:
        nw, nh = min(0.62, w * 0.45), min(1.7, h * 0.56)
        put(part, "donker", boutline(arch_pts(0, 0.5, nw, nh, 10), -d / 2 - 0.005, 0.02), M)
        put(part, "ornament", band(arch_pts(0, 0.5, nw, nh, 10), 0.07, -d / 2 - 0.04, 0.05), M)
        put(part, "ornament", bz(-nw / 2 - 0.1, nw / 2 + 0.1, -d / 2 - 0.12, -d / 2 + 0.02, 0.36, 0.5, 0.01), M)          # bakje
        FONT.append(list((M @ Vector((0, -d / 2 - 0.05, 0.5))).to_tuple(3)) + [0.9])
    if kap: urnkap(cx, cy, Z0 + h, s=min(w, d) * 0.9, rz=rz, part=part)
    if kuif_h: kuif2(M, 0, h + 0.02, w * 1.15, kuif_h, y=-0.02, kroon=True)
    coll_box(cx, cy, Z0 + h / 2, w + 0.1, d + 0.1, h, rz)


def kruistoren(cx, cy, rz, s, h, part="poorthuis"):
    """lakei- & poorthuis: kruisvormige plattegrond (plattegrond: verspringende blokken onder 45 graden), pilasters, kap"""
    M = TR(cx, cy, Z0, rz)
    for (w, d) in ((s, s * 0.6), (s * 0.6, s)):
        put(part, "pleister", bz(-w / 2, w / 2, -d / 2, d / 2, -0.05, h), M)
        put(part, "ornament", bz(-w / 2 - 0.05, w / 2 + 0.05, -d / 2 - 0.05, d / 2 + 0.05, -0.05, 0.32, 0.01), M)
        put(part, "ornament", bz(-w / 2 - 0.08, w / 2 + 0.08, -d / 2 - 0.08, d / 2 + 0.08, h - 0.16, h, 0.01), M)
        put(part, "ornament", bz(-w / 2 - 0.04, w / 2 + 0.04, -d / 2 - 0.04, d / 2 + 0.04, h - 0.3, h - 0.16, 0.01), M)
    urnkap(cx, cy, Z0 + h, s=s * 0.55, rz=rz, part=part)
    coll_box(cx, cy, Z0 + h / 2, s, s, h, rz)


FONT = []


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear(); FONT.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ================= MIDDENPOORT (element C, plattegrond y 9.6-10.9; aanzicht1: 1.93 x 4.4 m, doorgang 1.07 x 3.5) =================
    GX, GY = 0.1, 10.0
    Mg = TR(GX, GY, Z0)
    W2, H, OW, OH = 0.97, 4.4, 1.07, 3.5
    poly = [(-W2, -0.05), (-OW / 2, -0.05)] + arch_pts(0, -0.05, OW, OH + 0.05, 14)[1:-1] + [(OW / 2, -0.05), (W2, -0.05), (W2, H), (-W2, H)]
    pb = boutline(poly, -0.45, 0.9)
    bmesh.ops.triangulate(pb, faces=[f for f in pb.faces if len(f.verts) > 4], ngon_method="EAR_CLIP"); put("poort", "pleister", pb, Mg)
    put("poort", "ornament", band(arch_pts(0, -0.05, OW, OH + 0.05, 14), 0.12, -0.5, 0.06), Mg)                        # archivolt
    put("poort", "ornament", ell((0, -0.53, OH + 0.12), (0.13, 0.06, 0.2), 10, 8), Mg)                                  # sluitsteen
    for sx in (-1, 1):
        put("poort", "ornament", bz(sx * W2 - (0.18 if sx > 0 else -0.0) - (0.0 if sx > 0 else 0.18), sx * W2 + (0.0 if sx > 0 else 0.18) - (0.0), -0.52, -0.42, 0.32, H - 0.3), Mg) if False else None
        x0 = sx * (W2 - 0.1)
        put("poort", "ornament", bz(x0 - 0.12, x0 + 0.12, -0.53, -0.43, 0.32, H - 0.32), Mg)                            # pilaster
        put("poort", "ornament", bz(x0 - 0.17, x0 + 0.17, -0.56, -0.43, -0.05, 0.36, 0.01), Mg)
        put("poort", "ornament", bz(x0 - 0.17, x0 + 0.17, -0.56, -0.43, H - 0.42, H - 0.3, 0.01), Mg)                   # kapiteel
        krul(Mg, sx * (W2 + 0.1), H - 1.2, 0.32, sx=-sx, turns=1.3, y=-0.3, dik=0.06)                                   # voluut tegen de pijler
    put("poort", "ornament", bz(-W2 - 0.1, W2 + 0.1, -0.58, 0.5, H - 0.3, H - 0.12, 0.01), Mg)                          # hoofdgestel
    put("poort", "ornament", bz(-W2 - 0.14, W2 + 0.14, -0.62, 0.54, H - 0.12, H, 0.01), Mg)
    kuif2(Mg, 0, H + 0.02, 2.2, 1.45, y=-0.25, guirlande=False)                                                          # grote bekroning
    put("poort", "ornament", bz(-0.4, 0.4, -0.58, -0.5, OH + 0.25, H - 0.38, 0.01), Mg)                                 # veld boven de boog
    kuif2(Mg, 0, OH + 0.3, 0.8, 0.55, y=-0.62, guirlande=False)
    coll_box(GX - 0.8, GY, Z0 + H / 2, 0.45, 0.9, H, 0); coll_box(GX + 0.8, GY, Z0 + H / 2, 0.45, 0.9, H, 0)
    # medaillonpijlers naast de poort (lager, oeil-de-boeuf met guirlande, krul tegen de poort)
    for sx in (-1, 1):
        px = GX + sx * 1.42
        pijler(px, GY - 0.1, 0, 0.82, 0.62, 3.35, part="poort", kap=False)
        Mp = TR(px, GY - 0.1, Z0)
        oeil(Mp, 0, 2.3, 0.24, y=-0.33)
        krul(Mp, -sx * 0.3, 3.55, 0.3, sx=sx, turns=1.25, y=-0.1, dik=0.055)
        put("poort", "ornament", ell((sx * 0.1, -0.1, 3.5), (0.16, 0.12, 0.12), 8, 6), Mp)
    # ================= nispijlers met kuif (plattegrond I/H: schuin, -3.4..-2.3 en 2.3..3.5 op y ~9.55) =================
    for sx, rz in ((-1, -14), (1, 14)):
        pijler(GX + sx * 2.95, 9.55, rz, 1.43, 0.75, 3.0, part="nispijlers", nis=True, kap=False, kuif_h=1.0)
    # muurtjes tussen poort-medaillonpijlers en nispijlers
    muur((GX - 1.83, 9.75), (GX - 2.3, 9.7), part="muur"); muur((GX + 1.83, 9.75), (GX + 2.3, 9.7), part="muur")
    # ================= achtermuur element B / D (y 11.3) met urnpijlers en paneelvelden =================
    for (a, b) in (((-5.4, 11.3), (-3.55, 11.2)), ((-3.55, 11.2), (-2.0, 10.6)), ((3.62, 11.2), (5.6, 11.3)), ((2.1, 10.6), (3.62, 11.2))):
        muur(a, b)
        M, L, _ = M_seg(a, b, Z0)
        paneel(M, 0.25, L - 0.25, 0.55, WAND - 0.45)
    for (ux, uy) in ((-4.05, 11.15), (4.4, 11.15)):
        pijler(ux, uy, 0, 0.95, 0.8, 3.0, part="urnpijlers")
    # schuine vleugels en de rest van de omtrek (plattegrond element B/D, lakei- & poorthuis)
    for (a, b) in (((-6.9, 8.9), (-5.4, 11.3)), ((5.6, 11.3), (6.4, 10.4)), ((6.4, 10.4), (7.0, 9.0)), ((7.0, 9.0), (7.0, 8.3)), ((7.0, 8.3), (9.6, 8.3)),
                   ((-10.6, 8.6), (-7.5, 8.6))):
        muur(a, b)
        M, L, _ = M_seg(a, b, Z0)
        if L > 1.2: paneel(M, 0.25, L - 0.25, 0.55, WAND - 0.45)
    kruistoren(-6.45, 9.65, 45, 1.65, 3.3)
    kruistoren(6.6, 9.65, 45, 1.65, 3.3)
    # ================= gouden poort (plattegrond 'POORT': twee draaivleugels op x -7.0, y 5.1-8.6; dnkgroot: verguld smeedwerk) =================
    for (y0, y1, sgn) in ((5.15, 6.85, 1), (6.9, 8.6, -1)):
        Mv = Matrix.Translation((-7.0, y0, Z0)) @ Matrix.Rotation(math.radians(90), 4, "Z")
        L = y1 - y0
        put("gouden_poort", "ijzer", bz(0, L, -0.03, 0.03, 0.08, 0.14), Mv); put("gouden_poort", "ijzer", bz(0, L, -0.03, 0.03, 2.55, 2.62), Mv)
        put("gouden_poort", "ijzer", bz(0, L, -0.03, 0.03, 1.2, 1.25), Mv)
        k = 0.06
        while k < L - 0.03:
            put("gouden_poort", "ijzer", bz(k - 0.012, k + 0.012, -0.012, 0.012, 0.1, 2.6), Mv)
            put("gouden_poort", "goud", blathe([(0, 0), (0.025, 0), (0, 0.08)], 4), Mv @ Matrix.Translation((k, 0, 2.6)))
            k += 0.13
        for zc in (0.65, 1.9):
            krul(Mv, L / 2 - 0.25, zc, 0.22, sx=1, turns=1.2, y=0.0, dik=0.022, part="gouden_poort", mat="goud")
            krul(Mv, L / 2 + 0.25, zc, 0.22, sx=-1, turns=1.2, y=0.0, dik=0.022, part="gouden_poort", mat="goud")
        kuif(Mv, L / 2, 2.62, 0.9, 0.6, y=0.0, part="gouden_poort") if False else None
        put("gouden_poort", "goud", ell((L / 2, 0, 2.95), (0.22, 0.04, 0.3), 12, 8), Mv)
        put("gouden_poort", "goud", btube([(0.05, 0, 2.62), (L / 2, 0, 3.05 if sgn else 3.05), (L - 0.05, 0, 2.62)], 0.025, 5), Mv)
    coll_box(-7.0, 6.87, Z0 + 1.3, 0.12, 3.5, 2.6, 0)
    # ================= links voor: lakei- & poorthuis met fonteinbak en grote voluut (Bouwnieuwe links), element A =================
    kruistoren(-6.6, 3.85, 45, 1.9, 3.0)
    pts = [(-8.1, 2.4), (-7.6, 2.15), (-6.6, 2.0), (-5.6, 2.15), (-5.1, 2.45)]
    for (a, b) in zip(pts, pts[1:]):                                                                                   # gebogen fonteinbak (plattegrond G)
        M, L, ang = M_seg(a, b, Z0)
        put("fonteinbak", "pleister", bz(0, L, -0.14, 0.14, -0.05, 0.72), M)
        put("fonteinbak", "ornament", bz(-0.03, L + 0.03, -0.18, 0.18, 0.72, 0.8, 0.01), M)
    put("fonteinbak", "water", boutline([(-7.9, 0), (-5.3, 0)] and [(x, z) for x, z in ((-7.9, 0.55), (-5.3, 0.55), (-5.3, 0.58), (-7.9, 0.58))], 2.2, 0.9))
    for sx in (-1, 1):
        Mk = TR(-6.6 + sx * 1.35, 3.0, Z0, 0)
        krul(Mk, 0, 1.7, 0.55, sx=sx, turns=1.35, y=0.0, dik=0.09, part="fonteinbak")
    FONT.append([-6.6, 2.7, Z0 + 0.6, 1.2])
    muur((-9.25, 3.15), (-7.55, 3.6), h=2.4); muur((-7.0, 4.95), (-7.0, 5.15), h=2.4)
    pijler(-9.25, 3.15, -14, 1.05, 0.75, 2.4, part="pijlers")
    # ================= theekoepel (achthoek, plattegrond midden (6.75, 3.4), 3.0 m; kroonlijst 3050+P; Keizer_vooraanzicht) =================
    KX, KY, KR = 6.75, 3.4, 1.5 / math.cos(math.pi / 8)
    Mk = TR(KX, KY, Z0, 22.5)
    put("koepel", "pleister", blathe([(0, -0.05), (KR + 0.08, -0.05), (KR + 0.08, 0.42), (KR, 0.42), (KR, 2.7), (0, 2.7)], 8), Mk)
    put("koepel", "ornament", blathe([(0, 0.36), (KR + 0.1, 0.36), (KR + 0.1, 0.44), (0, 0.44)], 8), Mk)
    put("koepel", "ornament", blathe([(0, 2.62), (KR + 0.06, 2.62), (KR + 0.06, 2.75), (KR + 0.2, 2.86), (KR + 0.24, 3.05), (0, 3.05)], 8), Mk)
    put("koepel", "pleister", blathe([(0, 3.05), (KR * 0.86, 3.05), (KR * 0.86, 3.28), (0, 3.28)], 8), Mk)              # attiek onder de koepel
    put("koepel", "ornament", blathe([(0, 3.26), (KR * 0.9, 3.26), (KR * 0.9, 3.34), (0, 3.34)], 8), Mk)
    dome = [(KR * 0.84 * math.cos(a), 3.34 + 1.45 * math.sin(a)) for a in [i * (math.pi / 2) / 10 for i in range(11)]]
    put("koepel", "koepelglas", blathe(dome + [(0, 3.34 + 1.45)], 8), Mk)
    for k in range(8):                                                                                                 # ribben
        a = math.radians(22.5 + k * 45)
        rib = [(KX + KR * 0.84 * math.cos(t2) * math.cos(a) * 1.01, KY + KR * 0.84 * math.cos(t2) * math.sin(a) * 1.01, Z0 + 3.34 + 1.45 * math.sin(t2) * 1.01)
               for t2 in [i * (math.pi / 2) / 10 for i in range(11)]]
        put("koepel", "ornament", btube(rib, 0.035, 5))
    put("koepel", "goud", blathe([(0, 4.78), (0.1, 4.8), (0.16, 4.9), (0.15, 5.02), (0.08, 5.08), (0.05, 5.14), (0.08, 5.18), (0, 5.2)], 12), TR(KX, KY, Z0))   # gouden theepot
    put("koepel", "goud", btube([(KX + 0.14, KY, Z0 + 4.92), (KX + 0.26, KY, Z0 + 5.0), (KX + 0.3, KY, Z0 + 5.06)], 0.025, 5))
    put("koepel", "goud", btube([(KX - 0.14, KY, Z0 + 5.02), (KX - 0.23, KY, Z0 + 4.96), (KX - 0.15, KY, Z0 + 4.88)], 0.02, 5))
    apo = 1.5
    for k in range(8):                                                                                                 # vensters op de 5 voorzijden, pilasters op de hoeken
        a = math.radians(-90 + (k - 2) * 45)                                                                           # k=2: recht naar de bezoeker (-y)
        Mf = Matrix.Translation((KX + apo * math.cos(a), KY + apo * math.sin(a), Z0)) @ Matrix.Rotation(a + math.pi / 2, 4, "Z")
        ca = math.radians(-90 + (k - 2) * 45 + 22.5)
        Mc = Matrix.Translation((KX + KR * math.cos(ca), KY + KR * math.sin(ca), Z0)) @ Matrix.Rotation(ca + math.pi / 2, 4, "Z")
        put("koepel", "ornament", bz(-0.08, 0.08, -0.06, 0.04, 0.42, 2.62), Mc)
        if k in (0, 1, 2, 3, 4):
            ww = 0.62 if k == 2 else 0.5
            put("koepel", "venster", bz(-ww / 2, ww / 2, -0.03, 0.0, 0.75, 2.35), Mf)
            put("koepel", "gordijn", bz(-ww / 2 + 0.03, ww / 2 - 0.03, 0.02, 0.04, 0.8, 2.3), Mf)                       # vitrage (Schimmen)
            put("koepel", "raamhout", bz(-ww / 2 - 0.07, ww / 2 + 0.07, -0.06, 0.01, 0.68, 0.76), Mf)
            put("koepel", "raamhout", bz(-ww / 2 - 0.07, ww / 2 + 0.07, -0.06, 0.01, 2.34, 2.42), Mf)
            for sx in (-1, 1): put("koepel", "raamhout", bz(sx * (ww / 2 + 0.035) - 0.035, sx * (ww / 2 + 0.035) + 0.035, -0.06, 0.01, 0.68, 2.42), Mf)
            for i in range(1, 3): put("koepel", "raamhout", bz(-ww / 2 + i * ww / 3 - 0.012, -ww / 2 + i * ww / 3 + 0.012, -0.05, -0.01, 0.76, 2.34), Mf)
            for i in range(1, 6): put("koepel", "raamhout", bz(-ww / 2, ww / 2, -0.05, -0.01, 0.76 + i * 1.58 / 6 - 0.012, 0.76 + i * 1.58 / 6 + 0.012), Mf)
            put("koepel", "ornament", bz(-ww / 2 - 0.12, ww / 2 + 0.12, -0.12, 0.0, 2.42, 2.52, 0.01), Mf)              # druiplijst
    if True:
        a = math.radians(-90); p = Vector((KX + apo * math.cos(a), KY + apo * math.sin(a) - 0.3, Z0 + 1.6))
        LAMPS_.append([round(p.x, 2), round(p.y, 2), round(p.z, 2)])                                                   # schimmenspel-gloed achter het raam
    coll_box(KX, KY, Z0 + 1.5, 3.1, 3.1, 3.0, 0)
    # muren rechts: koepel -> element E en koepel -> achter (plattegrond)
    muur((8.2, 3.9), (9.7, 3.05), h=2.4); muur((8.25, 4.95), (8.3, 5.2), h=WAND); muur((8.3, 5.2), (10.9, 5.2), h=WAND)
    pijler(10.2, 3.0, 14, 1.05, 0.75, 2.4, part="pijlers")
    # ================= voorbak met postamenten (plattegrond: 1770/1200/1770 en 1110/1535/1480) =================
    POSTS = [(-1.64, 4.25), (1.7, 4.25), (-3.47, 3.0), (-1.64, 3.0), (1.7, 3.0), (3.5, 3.0), (-3.47, 1.33), (3.5, 1.33)]
    for (x, y) in POSTS:
        put("voorbak", "pleister", bz(x - 0.21, x + 0.21, y - 0.21, y + 0.21, -0.05, 0.85), TR(0, 0, Z0))
        put("voorbak", "ornament", bz(x - 0.26, x + 0.26, y - 0.26, y + 0.26, 0.85, 0.95, 0.01), TR(0, 0, Z0))
        put("voorbak", "ornament", bz(x - 0.19, x + 0.19, y - 0.19, y + 0.19, 0.95, 1.02, 0.01), TR(0, 0, Z0))
    for (a, b) in (((-1.64, 4.25), (1.7, 4.25)), ((-1.64, 4.25), (-1.64, 3.0)), ((1.7, 4.25), (1.7, 3.0)), ((-3.47, 3.0), (-1.64, 3.0)),
                   ((1.7, 3.0), (3.5, 3.0)), ((-3.47, 3.0), (-3.47, 1.33)), ((3.5, 3.0), (3.5, 1.33))):
        M, L, ang = M_seg(a, b, Z0)
        put("voorbak", "pleister", bz(0.2, L - 0.2, -0.12, 0.12, -0.05, 0.55), M)
        put("voorbak", "ornament", bz(0.2, L - 0.2, -0.16, 0.16, 0.55, 0.62, 0.01), M)
        coll_box((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, Z0 + 0.4, L, 0.35, 0.8, ang)
    put("voorbak", "water", bz(-3.35, 3.38, 1.3, 2.95, Z0 + 0.38, Z0 + 0.42)); put("voorbak", "water", bz(-1.52, 1.58, 2.9, 4.13, Z0 + 0.38, Z0 + 0.42))
    put("voorbak", "bodem", bz(-3.4, 3.42, 1.25, 4.2, Z0 - 0.1, Z0 + 0.0))
    put("voorbak", "donker", bz(-3.3, 3.33, 1.24, 1.3, Z0 + 0.05, Z0 + 0.4))                                         # overloop (waterval naar de vijver)
    for x in (-1.05, -0.35, 0.35, 1.05): put("voorbak", "donker", bz(x - 0.18, x + 0.18, 2.97, 3.03, Z0 + 0.42, Z0 + 0.55))   # spuitmonden
    FONT.append([0.03, 2.2, Z0 + 0.42, 1.4])
    # ================= lange vijver (20000 x 2500, bodem 900-P) met twee fonteinen =================
    vb = bmesh.new(); r_ = 0.6; ring = []
    for (cx_, cy_, a0) in ((10 - r_, -1.25 + r_, -90), (10 - r_, 1.25 - r_, 0), (-10 + r_, 1.25 - r_, 90), (-10 + r_, -1.25 + r_, 180)):
        for i in range(7): a = math.radians(a0 + i * 15); ring.append((cx_ + r_ * math.cos(a), cy_ + r_ * math.sin(a)))
    VIJVER = ring
    def plaatv(poly, z0, z1):
        bm = bmesh.new(); b = [bm.verts.new((x, y, z0)) for x, y in poly]; t = [bm.verts.new((x, y, z1)) for x, y in poly]
        n = len(poly); bm.faces.new(b[::-1]); bm.faces.new(t)
        for i in range(n): bm.faces.new((b[i], b[(i + 1) % n], t[(i + 1) % n], t[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm
    put("vijver", "water", plaatv(VIJVER, Z0 - 0.12, Z0 - 0.08))
    put("vijver", "bodem", plaatv(VIJVER, Z0 - 1.5, Z0 - 1.45))
    n = len(VIJVER)
    for i in range(n):                                                                                                 # zwarte vijverrand (foto: strakke donkere kant)
        a, b = VIJVER[i], VIJVER[(i + 1) % n]
        M, L, ang = M_seg(a, b, 0)
        put("vijver", "bodem", bz(-0.01, L + 0.01, 0.0, 0.1, Z0 - 1.5, Z0 + 0.02), M)
    for x in (-8.1, 8.0): FONT.append([x, 0.0, Z0 - 0.08, 1.6])
    # wegschrijven
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"KK_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "fonteinen": FONT}, open(os.path.join(out, "decor_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
