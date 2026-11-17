"""12_omgeving: ingang, wachtrij, tribune, bordes, uitgang en straatmeubilair rond de Pagode (scene-brief.md).
Parkframe zoals 10_station: meter, x oost, y noord, z = NAP - 10.0; hoeken in graden rond het bakmidden (360, 47.5), 0 = oost.
Collectie OMGEVING (eigen FBX, zelfde oorsprong als het station).
Bronnen: video fmEZsIkqsl8 (0:03-0:62 in, 5:55-6:57 uit), Pagode-landing.jpg, luchtfoto PDOK, AHN-DTM:
  plein NAP 9.6 | tribune 11 rijen van r 14 (11.3) naar r 25 (9.65) | bordes r 10.6-14 op 11.3 | laantje schuin langs de
  noordkant van de tribune (r 14 bij 104 graden -> r 25 bij 115 graden) | uitgang: trap aan de oostkant (-20 graden).
Schrijft ook exports/omgeving_lampen.json (lantaarnposities, park) voor de PointLights in Studio.
Gebruik: blender --background --python build/12_omgeving.py -- --master AR_Pagode_master.blend"""
import bpy, bmesh, sys, os, math, json, random
from mathutils import Vector, Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OWNER = "phase:12_omgeving"
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CX, CY = 360.0, 47.5
Z_I, Z_P = 1.3, -0.38                 # instapniveau (NAP 11.3), plein/laantje (NAP 9.62)
R_VL, R_BO = 10.62, 14.0              # bordes van vlonderrand tot tribune
N_RIJ = 11
A_ZUID = 156.5                        # zuidrand tribune (sleufopening begint bij 156.9)
A_RAIL = 152.6                        # eind wachtrijrelingen (daarna looppad langs de sleufhaag)
rnd = random.Random(7)
LAMPEN = []


def ztop(t):                          # bovenkant rij t (0 = bovenste, bij het bordes)
    return Z_I - 0.15 * (t + 1)


def a_c(r):                           # hartlijn laantje (graden)
    return 104.0 + (r - 14.2) * 0.95


B_LAAN = 1.5                          # halve breedte laantje: 3 m (echt 1.8 m; Roblox-avatar is 1.27 m breed, Daan 17 nov: "breder")
B_TRAP = 2.2                          # breedte trapstrook (echt ~1.5 m)
RAIL_T = (2, 4, 6, 8, 10)             # wachtrijreling op elke tweede rij: banen van ~2 m (echt elke rij, 1 m)


def aL(r): return a_c(r) - math.degrees(B_LAAN / r)       # laantje, tuinkant
def aR(r): return a_c(r) + math.degrees(B_LAAN / r)       # laantje, tribunekant
def aW(r): return aR(r) + math.degrees(0.42 / r)          # einde muur
def aS(r): return aW(r) + math.degrees(B_TRAP / r)        # einde trapstrook (begin zigzag)


PLAATS = []
HEKKEN = []                           # (a, b, hoogte) van elk hek-/relingstuk: onzichtbare botsing in Roblox


def vrij(naam, p, rad, bewust=False):
    """Registreer meubilair voor de looppadcontrole (bewust=True: hoort in de looproute, zoals tourniquets en paaltjes)."""
    PLAATS.append((naam, Vector(p), rad, bewust))


def looppad(q):
    """Is punt q (park x, y) een looppad? Laantje, trapstrook, de banen tussen de wachtrijrelingen, het bordes, het onderpad
    en het pad langs de uitgangsmuur. Randstroken tegen muren en hekken tellen niet mee (daar mag meubilair staan)."""
    r = math.hypot(q.x - CX, q.y - CY); a = math.degrees(math.atan2(q.y - CY, q.x - CX))
    if 14.15 < r < 25.0 and aL(r) < a < aR(r): return "laantje"
    if 14.95 < r < 17.0 and 88.3 < a < aL(r): return "aanlooppad"          # randstroken langs muur en gras vrij voor pot, bak, palen
    if 14.2 < r < 25.0 and aW(r) + math.degrees(0.35 / r) < a < aS(r) - math.degrees(0.1 / r): return "trapstrook"
    if 14.2 < r < 25.0 and aS(r) + math.degrees(0.1 / r) < a < A_ZUID - math.degrees(0.1 / r):
        if min(abs(r - (14.12 + t)) for t in RAIL_T) > 0.12: return "wachtrijbaan"
    if R_VL + 0.05 < r < 13.55 and 99.5 < a < A_ZUID: return "bordes"
    if 25.0 < r < 26.45 and aL(25.9) < a < A_ZUID: return "onderpad"
    if 11.75 < r < R_BO + 0.15 and -52.0 < a < 54.0: return "pad uitgang"
    return None


def controle():
    fout = []
    for naam, p, rad, bewust in PLAATS:
        if bewust: continue
        for dx, dy in ((0, 0), (0.4, 0), (-0.4, 0), (0, 0.4), (0, -0.4)):
            w = looppad(p + Vector((dx * rad, dy * rad, 0)))
            if w: fout.append(f"{naam} op ({p.x:.2f}, {p.y:.2f}): {w}"); break
    return fout


def col():
    c = bpy.data.collections.get("OMGEVING")
    if not c:
        c = bpy.data.collections.new("OMGEVING"); bpy.context.scene.collection.children.link(c)
    return c


def obj(naam, bm, rol):
    me = bpy.data.meshes.new(naam); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(naam, me); col().objects.link(o); o["rol"] = rol; o["owner"] = OWNER
    return o


def pt(r, a, z=0.0):
    a = math.radians(a); return Vector((CX + r * math.cos(a), CY + r * math.sin(a), z))


def ringsector(naam, r0, r1, z0, z1, a0, a1, rol, seg=None):
    seg = seg or max(4, int(abs(a1 - a0) / 2.5))
    bm = bmesh.new(); rings = []
    for i in range(seg + 1):
        a = math.radians(a0 + (a1 - a0) * i / seg); c, s = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((CX + r * c, CY + r * s, z)) for r, z in ((r0, z0), (r1, z0), (r1, z1), (r0, z1))])
    for i in range(seg):
        for k in range(4):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % 4], rings[i + 1][(k + 1) % 4], rings[i + 1][k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(naam, bm, rol)


def doos(naam, c, s, rol, rot=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=s, verts=bm.verts)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    return obj(naam, bm, rol)


def buis(naam, a, b, r, rol, seg=8, r2=None):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=d.length)
    M = Matrix.Translation((a + b) / 2) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return obj(naam, bm, rol)


def bol(naam, c, r, rol="goud"):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    return obj(naam, bm, rol)


def steen(naam, c, s, rol="breuksteen"):
    """Losse rotsblok: icosfeer met verschoven punten (video 0:22-0:35, randen van het laantje)."""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * s[0] * rnd.uniform(0.8, 1.15), v.co.y * s[1] * rnd.uniform(0.8, 1.15), v.co.z * s[2] * rnd.uniform(0.75, 1.1)))
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rnd.uniform(0, 6.3), 3, "Z"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    return obj(naam, bm, rol)


def paalkop(naam, p, h, rol, dik=0.06):
    """Paal zoals in de video (0:04-0:44): voetplaat, vierkante paal, kraag onder de top, hals en gouden bol."""
    doos(f"{naam}_voet", p + Vector((0, 0, 0.02)), (dik * 1.9, dik * 1.9, 0.04), rol)
    doos(f"{naam}", p + Vector((0, 0, h / 2)), (dik, dik, h), rol)
    doos(f"{naam}_kraag", p + Vector((0, 0, h - 0.06)), (dik * 1.45, dik * 1.45, 0.035), rol)
    buis(f"{naam}_hals", p + Vector((0, 0, h)), p + Vector((0, 0, h + 0.05)), dik * 0.35, rol, 8)
    bol(f"{naam}_bol", p + Vector((0, 0, h + 0.05 + dik * 0.9)), dik * 0.95)


def spijlenhek(naam, pts, h=1.1, rol="hek"):
    """Spijlenhek (video 0:04-0:26, 0:40, 6:40): palen met kraag en gouden bol om de ~2 m, dubbele bovenregel, onderregel,
    vierkante spijlen om de 11 cm. pts: lijst Vector (voet van het hek); volgt de lijn, ook schuin."""
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]; d = b - a; L = d.length
        if L < 0.05: continue
        HEKKEN.append([list(a), list(b), h + 0.08])
        rot = math.atan2(d.y, d.x)
        for nm, z in (("o", 0.1), ("b", h), ("b2", h - 0.11)):
            buis(f"{naam}_{k:02d}_regel{nm}", a + Vector((0, 0, z)), b + Vector((0, 0, z)), 0.018, rol, 4)
        n = max(1, int(L / 0.11))
        for i in range(1, n):
            p = a + d * (i / n)
            doos(f"{naam}_{k:02d}_sp{i:03d}", p + Vector((0, 0, (h + 0.1) / 2)), (0.016, 0.016, h - 0.1), rol, rot)
        np_ = max(1, int(L / 2.0))
        for i in range(np_ + (1 if k == len(pts) - 2 else 0)):
            paalkop(f"{naam}_{k:02d}_paal{i}", a + d * (i / np_), h + 0.08, rol, 0.06)


def reling(naam, pts, rol="reling", spijlen=False):
    """Wachtrijreling (video 0:22-0:44): twee buizen op 0.45 en 0.95 m, palen om de ~1.8 m met voetplaat, kraag en bol.
    spijlen=True: paneel met spijlen (langs de trapstrook, video 0:39-0:41)."""
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]; d = b - a; L = d.length
        if L < 0.05: continue
        HEKKEN.append([list(a), list(b), 1.07])
        rot = math.atan2(d.y, d.x)
        for nm, z in (("o", 0.45 if not spijlen else 0.1), ("b", 0.95)):
            buis(f"{naam}_{k:02d}_{nm}", a + Vector((0, 0, z)), b + Vector((0, 0, z)), 0.024, rol, 6)
        if spijlen:
            n = max(1, int(L / 0.11))
            for i in range(1, n):
                doos(f"{naam}_{k:02d}_sp{i:03d}", a + d * (i / n) + Vector((0, 0, 0.525)), (0.016, 0.016, 0.85), rol, rot)
        np_ = max(1, int(L / 1.8))
        for i in range(np_ + (1 if k == len(pts) - 2 else 0)):
            paalkop(f"{naam}_{k:02d}_paal{i}", a + d * (i / np_), 1.02, rol, 0.055)


def boog(r, a0, a1, z, stap=2.0):
    n = max(1, int(abs(math.radians(a1 - a0)) * r / stap))
    return [pt(r, a0 + (a1 - a0) * i / n, z) for i in range(n + 1)]


def kolom(naam, c, rx, ry, h, rol, rot=0.0, seg=16):
    """Ovale kolom (tourniquet, afvalbak met ronde hoeken)."""
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=1.0, radius2=1.0, depth=h)
    bmesh.ops.scale(bm, vec=(rx, ry, 1), verts=bm.verts)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector(c) + Vector((0, 0, h / 2)), verts=bm.verts)
    for fc in bm.faces: fc.smooth = abs(fc.normal.z) < 0.5
    return obj(naam, bm, rol)


def lantaarn(naam, p):
    """Klassieke zwarte lantaarnpaal (video 0:02 plein, 0:18-0:24 langs de trapstrook, 6:53): uitlopende voet, slanke paal met
    ringen, vierkante lantaarn die naar boven breder wordt, kap met knop. Licht op ~2.95 m."""
    p = Vector(p); R = "hek"
    buis(f"{naam}_voet", p, p + Vector((0, 0, 0.55)), 0.13, R, 8, 0.07)
    buis(f"{naam}_ring0", p + Vector((0, 0, 0.55)), p + Vector((0, 0, 0.6)), 0.09, R, 8)
    buis(f"{naam}_paal", p + Vector((0, 0, 0.6)), p + Vector((0, 0, 2.62)), 0.05, R, 8, 0.04)
    buis(f"{naam}_ring1", p + Vector((0, 0, 2.6)), p + Vector((0, 0, 2.68)), 0.075, R, 8)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=0.15, radius2=0.21, depth=0.44)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 4, 3, "Z"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=p + Vector((0, 0, 2.92)), verts=bm.verts); obj(f"{naam}_glas", bm, "lamp")
    for sx in (-1, 1):
        for sy in (-1, 1):
            buis(f"{naam}_stijl{sx}{sy}", p + Vector((sx * 0.105, sy * 0.105, 2.7)), p + Vector((sx * 0.15, sy * 0.15, 3.14)), 0.014, R, 4)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=0.27, radius2=0.03, depth=0.22)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 4, 3, "Z"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=p + Vector((0, 0, 3.25)), verts=bm.verts); obj(f"{naam}_kap", bm, R)
    bol(f"{naam}_knop", p + Vector((0, 0, 3.4)), 0.04, R)
    LAMPEN.append([round(p.x, 3), round(p.y, 3), round(p.z + 2.92, 3)])


def lantaarn_sier(naam, p):
    """Sierlijke bronzen lantaarnpaal bij de tourniquets (video 0:39-0:46): brede geribde voet met ringen, paal met
    verdikkingen, kapiteel, zeshoekige lantaarn met bolle kap en spits. Licht op ~3.3 m."""
    p = Vector(p); R = "brons"
    buis(f"{naam}_plint", p, p + Vector((0, 0, 0.12)), 0.2, R, 8)
    buis(f"{naam}_voet", p + Vector((0, 0, 0.12)), p + Vector((0, 0, 0.95)), 0.16, R, 8, 0.09)
    for k, z in enumerate((0.35, 0.95, 1.6, 2.6)):
        buis(f"{naam}_ring{k}", p + Vector((0, 0, z - 0.03)), p + Vector((0, 0, z + 0.03)), 0.12 if k < 2 else 0.085, R, 8)
    buis(f"{naam}_paal", p + Vector((0, 0, 0.95)), p + Vector((0, 0, 2.9)), 0.06, R, 8, 0.05)
    buis(f"{naam}_kapiteel", p + Vector((0, 0, 2.9)), p + Vector((0, 0, 3.05)), 0.07, R, 8, 0.13)
    buis(f"{naam}_glas", p + Vector((0, 0, 3.05)), p + Vector((0, 0, 3.5)), 0.15, "lamp", 6, 0.19)
    for k in range(6):
        a = k * math.pi / 3
        buis(f"{naam}_stijl{k}", p + Vector((math.cos(a) * 0.155, math.sin(a) * 0.155, 3.05)), p + Vector((math.cos(a) * 0.195, math.sin(a) * 0.195, 3.5)), 0.013, R, 4)
    buis(f"{naam}_kap", p + Vector((0, 0, 3.5)), p + Vector((0, 0, 3.7)), 0.24, R, 6, 0.05)
    buis(f"{naam}_spits", p + Vector((0, 0, 3.7)), p + Vector((0, 0, 3.9)), 0.035, "goud", 6, 0.0)
    LAMPEN.append([round(p.x, 3), round(p.y, 3), round(p.z + 3.28, 3)])


def afvalbak(naam, p, rot, hoog=False):
    """Groene afvalbak (video 0:02 plein: hoog met grijze kap; 0:49-0:52 bordes: met gouden embleem en lijsten)."""
    p = Vector(p); f = Vector((math.cos(rot), math.sin(rot), 0)); t = Vector((-f.y, f.x, 0))
    H = 1.15 if hoog else 0.95
    doos(f"{naam}_plint", p + Vector((0, 0, 0.04)), (0.5, 0.46, 0.08), "staal_groen", rot)
    doos(f"{naam}_bak", p + Vector((0, 0, H / 2)), (0.46, 0.42, H - 0.04), "staal_groen", rot)
    doos(f"{naam}_deksel", p + Vector((0, 0, H + 0.03)), (0.52, 0.48, 0.07), "staal" if hoog else "staal_groen", rot)
    doos(f"{naam}_gleuf", p + f * 0.215 + Vector((0, 0, H - 0.14)), (0.03, 0.3, 0.08), "beton_donker", rot)
    for s_ in (-1, 1):                                       # lijsten (verdiept paneel)
        doos(f"{naam}_lijst{s_}", p + f * 0.215 + t * s_ * 0.17 + Vector((0, 0, H * 0.45)), (0.02, 0.03, H * 0.6), "goud" if not hoog else "staal_groen", rot)
    buis(f"{naam}_embleem", p + f * 0.21 + Vector((0, 0, H * 0.48)), p + f * 0.235 + Vector((0, 0, H * 0.48)), 0.09, "goud", 12)


def paaltje(naam, p):
    """Zwart paaltje (video 0:04-0:13, kop van het laantje)."""
    p = Vector(p)
    buis(f"{naam}", p, p + Vector((0, 0, 0.85)), 0.045, "hek", 8)
    bol(f"{naam}_bol", p + Vector((0, 0, 0.88)), 0.055, "hek")


def bankje(naam, p, rot):
    """Parkbank: rode houten latten op gietijzeren zijstukken met armleuning (Pagode-landing.jpg)."""
    p = Vector(p); f = Vector((math.cos(rot), math.sin(rot), 0)); t = Vector((-f.y, f.x, 0))
    for k in range(4):
        doos(f"{naam}_zit{k}", p + f * (0.18 - k * 0.115) + Vector((0, 0, 0.45)), (0.09, 1.8, 0.035), "rood", rot)
    for k in range(3):
        c = p - f * (0.25 + k * 0.02) + Vector((0, 0, 0.6 + k * 0.13))
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(0.03, 1.8, 0.09), verts=bm.verts)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z") @ Matrix.Rotation(0.18, 3, "Y"), verts=bm.verts)
        bmesh.ops.translate(bm, vec=c, verts=bm.verts); obj(f"{naam}_rug{k}", bm, "rood")
    for s_ in (-1, 1):
        q = p + t * s_ * 0.8
        doos(f"{naam}_voorpoot{s_}", q + f * 0.2 + Vector((0, 0, 0.3)), (0.05, 0.05, 0.6), "hek", rot)
        doos(f"{naam}_achterpoot{s_}", q - f * 0.24 + Vector((0, 0, 0.47)), (0.05, 0.05, 0.94), "hek", rot)
        doos(f"{naam}_leuning{s_}", q + Vector((0, 0, 0.64)), (0.5, 0.05, 0.04), "hek", rot)
        doos(f"{naam}_dwars{s_}", q + Vector((0, 0, 0.42)), (0.48, 0.05, 0.04), "hek", rot)


def tourniquet(naam, p, rot):
    """Tourniquetkolom (video 0:44-0:47): zwart, ovaal, ~1.1 m, rond groen licht bovenop, lichtblauw bordje met pijl."""
    p = Vector(p); f = Vector((math.cos(rot), math.sin(rot), 0))
    kolom(f"{naam}", p, 0.13, 0.11, 1.08, "hek", rot)
    kolom(f"{naam}_kap", p + Vector((0, 0, 1.08)), 0.14, 0.12, 0.04, "hek", rot)
    kolom(f"{naam}_licht", p + Vector((0, 0, 1.12)), 0.075, 0.075, 0.015, "lamp_groen", rot, 12)
    doos(f"{naam}_bordje", p + f * 0.118 + Vector((0, 0, 0.72)), (0.012, 0.17, 0.3), "bord_blauw", rot)


def controlehuisje(naam, hc, rot):
    """Controlehuisje (video 0:44-0:49): groen frame, rode onderpanelen met groene lijst, glazen bovenhelft met roeden,
    een opengeklapt raam aan de voorkant, toonbank, rode kroonrand met witte motieven (PG_huisrand) en gouden knoppen."""
    f = Vector((math.cos(rot), math.sin(rot), 0)); tg = Vector((-f.y, f.x, 0)); B, D = 1.7, 1.5
    doos(f"{naam}_vloer", hc + Vector((0, 0, 0.05)), (D + 0.06, B + 0.06, 0.1), "groen", rot)
    doos(f"{naam}_binnen", hc + Vector((0, 0, 1.35)), (D - 0.2, B - 0.2, 2.5), "onderkant", rot)
    for zijde, (n, breed) in enumerate(((f, B), (-f, B), (tg, D), (-tg, D))):
        t2 = Vector((-n.y, n.x, 0)); c = hc + n * ((D if breed == B else B) / 2)
        r2 = math.atan2(n.y, n.x)
        doos(f"{naam}_paneel{zijde}", c + Vector((0, 0, 0.6)), (0.04, breed - 0.1, 0.95), "rood", r2)
        for k, sx in enumerate((-1, 1)):
            doos(f"{naam}_plijst{zijde}{k}", c + n * 0.025 + t2 * sx * (breed / 2 - 0.15) + Vector((0, 0, 0.6)), (0.02, 0.06, 0.8), "groen", r2)
        for nm, z in (("o", 0.2), ("b", 1.0)):
            doos(f"{naam}_plat{zijde}{nm}", c + n * 0.025 + Vector((0, 0, z)), (0.02, breed - 0.24, 0.06), "groen", r2)
        doos(f"{naam}_glas{zijde}", c + Vector((0, 0, 1.68)), (0.02, breed - 0.1, 1.2), "glas", r2)
        for k in (-1, 0, 1):
            doos(f"{naam}_roede{zijde}{k}", c + n * 0.015 + t2 * k * breed / 3.2 + Vector((0, 0, 1.68)), (0.03, 0.045, 1.2), "groen", r2)
        doos(f"{naam}_dorpel{zijde}", c + n * 0.03 + Vector((0, 0, 1.1)), (0.08, breed, 0.07), "groen", r2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            doos(f"{naam}_stijl{sx}{sy}", hc + f * sx * D / 2 + tg * sy * B / 2 + Vector((0, 0, 1.25)), (0.1, 0.1, 2.5), "groen", rot)
    # opengeklapt raam (scharnier links voor), 70 graden naar buiten
    sch = hc + f * (D / 2 + 0.02) + tg * (B / 2 - 0.05)
    dirp = Vector((math.cos(rot - math.radians(20)), math.sin(rot - math.radians(20)), 0)); rn = rot + math.radians(70)
    doos(f"{naam}_raam", sch + dirp * 0.38 + Vector((0, 0, 1.75)), (0.03, 0.72, 0.95), "glas", rn)
    for nm, z in (("o", 1.27), ("b", 2.23)):
        doos(f"{naam}_raamlijst{nm}", sch + dirp * 0.38 + Vector((0, 0, z)), (0.045, 0.76, 0.06), "groen", rn)
    doos(f"{naam}_toonbank", hc + f * (D / 2 + 0.12) + Vector((0, 0, 1.1)), (0.26, B - 0.2, 0.05), "groen", rot)
    # kroonrand: rode band met motieven (textuur), groene kroonlijst, plat dak
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    z0, z1 = 2.48, 2.82; omtrek = 0.0
    hoeken = [hc + f * sx * (D / 2 + 0.08) + tg * sy * (B / 2 + 0.08) for sx, sy in ((1, -1), (1, 1), (-1, 1), (-1, -1))]
    for i in range(4):
        a_, b_ = hoeken[i], hoeken[(i + 1) % 4]; L = (b_ - a_).length
        vs = [bm.verts.new(a_ + Vector((0, 0, z0))), bm.verts.new(b_ + Vector((0, 0, z0))), bm.verts.new(b_ + Vector((0, 0, z1))), bm.verts.new(a_ + Vector((0, 0, z1)))]
        fc = bm.faces.new(vs); fc.normal_update()
        if fc.normal.dot(((a_ + b_) / 2) - hc) < 0: fc.normal_flip()
        for l in fc.loops:
            q = (l.vert.co - a_); q.z = 0; u = (omtrek + q.length) / 0.6; v = (l.vert.co.z - hc.z - z0) / (z1 - z0)
            l[uvl].uv = (u, v)
        omtrek += L
    o = obj(f"{naam}_rand", bm, "huisrand"); o["uv_vast"] = True
    doos(f"{naam}_lijst", hc + Vector((0, 0, 2.86)), (D + 0.3, B + 0.3, 0.08), "groen", rot)
    doos(f"{naam}_dak", hc + Vector((0, 0, 2.95)), (D + 0.2, B + 0.2, 0.1), "dak_donker", rot)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p_ = hc + f * sx * (D / 2 + 0.12) + tg * sy * (B / 2 + 0.12)
            buis(f"{naam}_pinakel{sx}{sy}", p_ + Vector((0, 0, 2.9)), p_ + Vector((0, 0, 3.12)), 0.04, "goud", 6, 0.005)
    bol(f"{naam}_knop", hc + Vector((0, 0, 3.08)), 0.09)


def bord_mesh(naam, omtrek, breed, hoog, dik, oorsprong, rot, rol):
    """Bord met eigen omtrek (u, v in 0..1), geextrudeerd; voor- en achterkant krijgen de textuur (achterkant gespiegeld)."""
    f = Vector((math.cos(rot), math.sin(rot), 0)); t = Vector((-f.y, f.x, 0))
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    voor = [bm.verts.new(oorsprong + t * ((u - 0.5) * breed) + f * (dik / 2) + Vector((0, 0, v * hoog))) for u, v in omtrek]
    acht = [bm.verts.new(oorsprong + t * ((u - 0.5) * breed) - f * (dik / 2) + Vector((0, 0, v * hoog))) for u, v in omtrek]
    fv = bm.faces.new(voor); fa = bm.faces.new(acht[::-1])
    n = len(omtrek)
    for i in range(n):
        j = (i + 1) % n
        fz = bm.faces.new((voor[i], acht[i], acht[j], voor[j]))
        for l in fz.loops: l[uvl].uv = (0.002, 0.002)
    uvmap = {v: uv for v, uv in zip(voor, omtrek)}
    for l in fv.loops:
        u, v = uvmap[l.vert]; l[uvl].uv = (u, v)           # t wijst naar rechts voor wie ervoor staat
    uvmap = {v: uv for v, uv in zip(acht, omtrek)}
    for l in fa.loops:
        u, v = uvmap[l.vert]; l[uvl].uv = (1 - u, v)       # achterkant: gespiegeld zodat de tekst leesbaar is
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj(naam, bm, rol); o["uv_vast"] = True
    return o


def build():
    a = sys.argv[sys.argv.index("--") + 1:]
    m = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=m)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    from importlib import util
    spec = util.spec_from_file_location("tex", os.path.join(D, "build", "04c_texturen_omgeving.py")); tex = util.module_from_spec(spec)
    spec.loader.exec_module(tex)

    # A1 bordes (klinkers, op instapniveau) en bloemenperk aan de pleinkant (Pagode-landing.jpg)
    ringsector("AR_Pagode_O_bordes", R_VL, R_BO + 0.02, -0.9, Z_I, 99.5, A_ZUID, "klinker")
    ringsector("AR_Pagode_O_perk", R_VL, 13.75, -0.9, Z_I + 0.12, 54.0, 99.5, "aarde")
    # A2 tribune: 11 rijen van 1 m, elk 15 cm lager (AHN: r 14 -> 25 van NAP 11.3 naar 9.65)
    for t in range(N_RIJ):
        r0, r1 = 14.0 + t, 15.0 + t; rm = (r0 + r1) / 2
        ringsector(f"AR_Pagode_O_rij_{t:02d}", r0 - 0.02, r1, -1.2, ztop(t), aW(rm) - 0.1, A_ZUID, "klinker")
        # laantje (klinkers, pleinhoogte)
    # muur tussen laantje en trapstrook: een stuk, bovenkant loopt schuin met de rijen mee (video 0:20-0:30)
    stations = [(R_BO, Z_I + 0.25)] + [(14.5 + t, ztop(t) + 0.3) for t in range(N_RIJ)] + [(25.0, ztop(N_RIJ - 1) + 0.3)]
    bm = bmesh.new(); rings = []
    for r, zt in stations:
        rings.append([bm.verts.new(pt(r, aa, z)) for aa, z in ((aR(r), -0.95), (aW(r), -0.95), (aW(r), zt), (aR(r), zt))])
    for i in range(len(rings) - 1):
        for q in range(4): bm.faces.new((rings[i][q], rings[i][(q + 1) % 4], rings[i + 1][(q + 1) % 4], rings[i + 1][q]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj("AR_Pagode_O_laanmuur", bm, "breuksteen")
    ringsector("AR_Pagode_O_laan_kop", R_BO + 0.15, 14.0 + 0.01, -0.9, Z_P, aL(14.1) - 0.4, aR(14.1) + 0.05, "klinker", seg=2)
    # laantje als EEN doorlopende strook met vloeiende randen (losse stukken per rij gaven zaagtanden waar het gras doorkwam);
    # tuinkant loopt 0.6 m door tot onder de rotsrand en de reling, tribunekant tot onder de laanmuur
    def strook(naam, stations, z):
        bm = bmesh.new(); rings = []
        for r, al, ar in stations:
            rings.append([bm.verts.new(pt(r, aa, zz)) for aa, zz in ((al, -0.9), (ar, -0.9), (ar, z), (al, z))])
        for i in range(len(rings) - 1):
            for q in range(4): bm.faces.new((rings[i][q], rings[i][(q + 1) % 4], rings[i + 1][(q + 1) % 4], rings[i + 1][q]))
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return obj(naam, bm, "klinker")
    st_ = []
    r = 14.0
    while r < 25.0 + 1e-6:
        links = aL(r) + 0.05 if r < 17.6 else aL(r) - math.degrees(0.6 / r)
        if abs(r - 17.6) < 1e-6: st_.append((r, aL(r) + 0.05, aR(r) + 0.05))
        st_.append((r, links, aR(r) + 0.05)); r = round(r + 0.25, 4)
    for k in range(0, len(st_) - 1, 12):                     # in stukken (kleine UV-getallen per object)
        strook(f"AR_Pagode_O_laan_{k // 12:02d}", st_[k:k + 13], Z_P)
    a_onder0 = aL(25.0) - math.degrees(0.6 / 25.0)
    ringsector("AR_Pagode_O_onderpad", 25.0, 27.15, -0.9, Z_P + 0.02, a_onder0, A_ZUID, "klinker")   # tot onder het buitenhek (r 26.95)
    # A3 keermuur langs het plein (1.7 m hoog, video 0:04-0:12) tot voorbij de kop van het laantje, met spijlenhek erop
    a_muur_eind = aW(14.5)
    ringsector("AR_Pagode_O_pleinmuur", 13.75, R_BO + 0.15, -0.95, Z_I + 0.25, 54.0, a_muur_eind, "breuksteen")
    spijlenhek("AR_Pagode_O_hek_plein", boog(13.95, 54.0, a_muur_eind, Z_I + 0.25))
    # hek op de laanmuur, schuin met de rijen mee
    lijn = [pt(R_BO + 0.15, (aR(14.2) + aW(14.2)) / 2, Z_I + 0.25)]
    for t in range(N_RIJ):
        rm = 14.5 + t; lijn.append(pt(rm, (aR(rm) + aW(rm)) / 2, ztop(t) + 0.3))
    lijn.append(pt(25.0, (aR(25.0) + aW(25.0)) / 2, ztop(N_RIJ - 1) + 0.3))      # tot het eind van de laanmuur
    spijlenhek("AR_Pagode_O_hek_laan", lijn)
    # lage reling + rotsblokken aan de tuinkant van het laantje (video 0:22-0:35)
    reling("AR_Pagode_O_reling_tuin", [pt(r, aL(r) - math.degrees(0.15 / r), Z_P) for r in (16.0, 19.0, 22.0, 25.0)])
    for k in range(22):
        r = 16.0 + k * 0.45
        steen(f"AR_Pagode_O_rand_{k:02d}", pt(r, aL(r) - math.degrees(0.35 / r), Z_P + 0.05), (0.28, 0.22, 0.16))
    # A4 wachtrijrelingen: zigzag over de rijen (keerpunten om en om), radiale reling langs de trapstrook
    for t in RAIL_T:
        r = 14.0 + t + 0.12
        z = ztop(t) if t < N_RIJ else Z_P + 0.02
        gat = math.degrees(2.0 / r)                   # keerpunten 2 m breed
        a0, a1 = aS(r), A_ZUID - math.degrees(0.1 / r)        # van de trapreling tot het zuidhek: geen strook langs de zuidkant (sluiproute, Daan)
        if (t // 2) % 2: a1 -= gat
        else: a0 += gat
        reling(f"AR_Pagode_O_rij_reling_{t:02d}", boog(r, a0, a1, z))
    R_OPEN = 14.0 + 2 + 0.12                                  # bovenste baan (rij 0 en 1) helemaal open naar de trapkop: 1.9 m (Daan: "lastig om doorheen te komen")
    rl = [pt(R_OPEN, aS(R_OPEN), ztop(2))] + [pt(14.5 + t, aS(14.5 + t), ztop(t)) for t in range(3, N_RIJ)] + [pt(24.95, aS(24.95), ztop(N_RIJ - 1))]   # tot het eind van de rijen
    reling("AR_Pagode_O_trap_reling", rl, spijlen=True)          # paneel met spijlen langs de trapstrook (video 0:39-0:41)
    # hek tussen bordes en tribune (Pagode-landing.jpg), open bij de trapstrook en bij het zuidpad
    spijlenhek("AR_Pagode_O_hek_bordes", boog(R_BO + 0.05, aS(14.2) + 0.2, A_RAIL - 2.0, Z_I))     # dicht tot de trapstrook: alles via de tourniquets

    # A5 lantaarns, elk op een plek uit de video, NOOIT op een looppad (zie controle onderaan)
    for k, r in enumerate((19.0, 23.0)):             # klassiek, op de trapstrook tegen het hek op de laanmuur (0:18-0:24)
        p = pt(r, aW(r) + math.degrees(0.2 / r), ztop(int(r - 14.0))); lantaarn(f"AR_Pagode_O_lamp_trap{k}", p); vrij(f"lamp_trap{k}", p, 0.13)
    for k, r in enumerate((R_OPEN + 0.08, 18.6)):     # sierlijk brons, op de trapreling (0:39-0:46); niet meer in de doorgang
        p = pt(r, aS(r), ztop(int(r - 14.0))); lantaarn_sier(f"AR_Pagode_O_lamp_sier{k}", p); vrij(f"lamp_sier{k}", p, 0.2)
    p = pt(20.12, A_RAIL, ztop(6)); lantaarn("AR_Pagode_O_lamp_zuid", p)   # op het eind van de reling, naast het zuidpad; vrij("lamp_zuid", p, 0.13)
    p = pt(13.8, 140.0, Z_I); lantaarn("AR_Pagode_O_lamp_bordes", p); vrij("lamp_bordes", p, 0.13)
    p = pt(17.8, 89.0, Z_P); lantaarn("AR_Pagode_O_lamp_plein", p); vrij("lamp_plein", p, 0.13)      # hoek plein/tuin (0:02)

    # B1 dubbele tourniquet bovenaan de trapstrook, controlehuisje er vlak achter (video 0:44-0:47: trap loopt recht op de
    # tourniquets af, het huisje staat erachter, daarna splitst de rij naar links en rechts)
    a_t = (aW(14.2) + aS(14.2)) / 2
    for k, s_ in enumerate((-1, 1)):
        aa = a_t + s_ * math.degrees(0.93 / 13.5); p = pt(13.5, aa, Z_I)         # 1.86 m hart op hart: 1.60 m vrije doorgang (19_maatcontrole)
        tourniquet(f"AR_Pagode_O_tourniquet{k}", p, math.radians(aa)); vrij(f"tourniquet{k}", p, 0.13, bewust=True)
        # kort hekje van de tourniquet naar de rand van de trapstrook (niet om de tourniquets heen lopen)
        rand = aW(14.2) if s_ < 0 else aS(14.2)
        spijlenhek(f"AR_Pagode_O_tourniquethek{k}", [p, pt(14.25, rand, Z_I)], h=1.0)
    # huisje opzij (kloksgewijs), uit de looplijn: na de tourniquets loop je tegen de klok in naar de poortjes (Daan: "ik kom gelijk
    # tegen dat huisje aan"); raam naar de tourniquets, met botsing rondom
    hc = pt(11.42, 106.0, Z_I); rot_h = math.radians(106.0)          # recht op het station, raam naar buiten (naar de tourniquets)
    controlehuisje("AR_Pagode_O_huis", hc, rot_h); vrij("huis", hc, 0.8, bewust=True)
    fh = Vector((math.cos(rot_h), math.sin(rot_h), 0)); th = Vector((-fh.y, fh.x, 0))
    hoeken = [hc + fh * sx * 0.78 + th * sy * 0.88 for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    for k in range(4): HEKKEN.append([list(hoeken[k]), list(hoeken[(k + 1) % 4]), 2.6])

    # B2 ingangsbord PAGODE over de kop van het laantje (video 0:13-0:19): linkerpaal tegen de laanmuur, rechterpaal in de
    # tuinrand met het regelbordje; bord een kwartslag naar het plein gedraaid (gezien vanaf het plein, 0:02-0:12)
    # je loopt over het plein naar het westen, onder het bord door, en slaat dan rechtsaf het laantje in (0:02-0:20):
    # bord staat dwars op die looprichting, voorkant naar het plein; linkerpaal tegen de pleinmuur, rechterpaal aan de tuinrand
    A_BORD = aL(14.38) - math.degrees(0.3 / 14.38)                 # beide palen buiten het laantje
    pl = pt(14.38, A_BORD, Z_P)
    pr = pt(17.3, A_BORD, Z_P)
    as_ = pr - pl; as_.z = 0; breed = as_.length + 0.3
    fz = Vector((-as_.y, as_.x, 0)).normalized()
    if fz.dot(pt(18.0, 88.0) - pl) < 0: fz = -fz                       # voorkant naar het plein
    rot = math.atan2(fz.y, fz.x); mid = (pl + pr) / 2
    for k, p in enumerate((pl, pr)):
        buis(f"AR_Pagode_O_bordpaal{k}", p + Vector((0, 0, -0.3)), p + Vector((0, 0, 3.35)), 0.06, "hek", 8)
        paalkop(f"AR_Pagode_O_bordpaal{k}_kop", p + Vector((0, 0, 3.3)), 0.12, "hek", 0.1)
        vrij(f"bordpaal{k}", p, 0.06)
    bord_mesh("AR_Pagode_O_ingangsbord", tex.BORD_OMTREK(48), breed, 1.05, 0.07, mid + Vector((0, 0, 2.2)), rot, "ingangsbord")
    doos("AR_Pagode_O_regelbord", pr + fz * 0.05 + Vector((0, 0, 1.45)), (0.02, 0.3, 0.55), "bord_blauw", rot)
    for k, dt in enumerate((-0.55, 0.0, 0.55)):                     # paaltjes in de mond van het laantje (0:04-0:13)
        if dt == 0.0: continue                                        # twee paaltjes, 1.6 m ertussen (avatar 1.27 m)
        p = pt(16.2, a_c(16.2) + math.degrees(dt * 1.45 / 16.2), Z_P); paaltje(f"AR_Pagode_O_paaltje{k}", p); vrij(f"paaltje{k}", p, 0.05, bewust=True)
    # afvalbakken: hoge bak rechts van het bord op het plein (0:02), groene bakken met embleem tegen de hekken (0:49-0:52)
    aa = A_BORD - 1.2; p = pt(17.15, aa, Z_P); afvalbak("AR_Pagode_O_bak_plein", p, math.radians(aa - 90), hoog=True); vrij("bak_plein", p, 0.3)   # rechts voor het bord
    for naam, r, aa, z in (("bak_bordes", 13.72, 101.5, Z_I), ("bak_zuid", 13.72, 151.0, Z_I), ("bak_onder", 26.65, 155.6, Z_P + 0.02)):
        p = pt(r, aa, z); afvalbak(f"AR_Pagode_O_{naam}", p, math.radians(aa + 180)); vrij(naam, p, 0.3)
    # grote donkerrode pot met bamboe links van het bord, tegen de pleinmuur (0:02-0:12); bamboe zelf in 14_planten
    p = pt(14.62, A_BORD - 1.7, Z_P)
    buis("AR_Pagode_O_pot", p, p + Vector((0, 0, 0.2)), 0.26, "rood", 16, 0.38)
    buis("AR_Pagode_O_pot_buik", p + Vector((0, 0, 0.2)), p + Vector((0, 0, 0.62)), 0.38, "rood", 16, 0.3)
    buis("AR_Pagode_O_pot_rand", p + Vector((0, 0, 0.62)), p + Vector((0, 0, 0.68)), 0.32, "rood", 16)
    vrij("pot", p, 0.38)
    # rode bankjes voor het plantvak (Pagode-landing.jpg), rug naar de muur
    for k, aa in enumerate((70.0, 82.0)):
        p = pt(15.75, aa, Z_P); bankje(f"AR_Pagode_O_bank{k}", p, math.radians(aa)); vrij(f"bank{k}", p, 0.4)

    # C uitgang aan de oostkant (video 6:15-6:45): keermuur langs de vlonder, trap naar het pad, hek, uitgangsbord
    A_UIT = -20.0; gat = math.degrees(1.3 / 10.8)
    for k, (a0, a1) in enumerate(((-52.0, A_UIT - gat), (A_UIT + gat, 54.0))):
        ringsector(f"AR_Pagode_O_oostmuur{k}", R_VL, 11.0, -1.0, Z_I + 0.12, a0, a1, "breuksteen")
        spijlenhek(f"AR_Pagode_O_hek_oost{k}", boog(10.82, a0 + 0.3, a1 - 0.3, Z_I + 0.12))
    for k in range(4):                     # in stukken: kleine UV-getallen per object (precisie in Roblox)
        ringsector(f"AR_Pagode_O_pad_oost{k}", 11.0, R_BO + 0.15, -0.9, Z_P + 0.03, -52.0 + 26.5 * k, -52.0 + 26.5 * (k + 1), "klinker")
    for k in range(5):
        ringsector(f"AR_Pagode_O_plein{k}", R_BO + 0.15, 24.0, -0.9, Z_P, -52.0 + 28.0 * k, -52.0 + 28.0 * (k + 1), "klinker")
    # aanlooppad van het plein naar het laantje: brede klinkerstrook (r 14.15-17.5) die het laantje naadloos raakt
    bm = bmesh.new(); rings = []
    rs = [R_BO + 0.15 + (17.5 - R_BO - 0.15) * i / 6 for i in range(7)]
    for r in rs:
        rings.append([bm.verts.new(pt(r, aa, z)) for aa, z in ((88.0, -0.9), (aL(r) + 0.05, -0.9), (aL(r) + 0.05, Z_P), (88.0, Z_P))])
    for i in range(len(rings) - 1):
        for q in range(4): bm.faces.new((rings[i][q], rings[i][(q + 1) % 4], rings[i + 1][(q + 1) % 4], rings[i + 1][q]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj("AR_Pagode_O_plein_kop", bm, "klinker")
    # granieten opsluitband waar de klinkers aan het gras grenzen (nette rand, video 0:02: rand langs de tuin)
    ringsector("AR_Pagode_O_band_kop", 17.5, 17.68, -0.6, Z_P + 0.03, 88.0, aL(17.6), "graniet", seg=6)
    bm = bmesh.new(); a0 = math.radians(88.0); u = Vector((math.cos(a0), math.sin(a0), 0)); n = Vector((-u.y, u.x, 0))
    vs = []
    for r, z in ((17.5, -0.6), (24.0, -0.6), (24.0, Z_P + 0.03), (17.5, Z_P + 0.03)):
        c = Vector((CX, CY, z)) + u * r
        vs.append((c - n * 0.0, c + n * 0.18))
    ring = [bm.verts.new(a) for a, _ in vs] + [bm.verts.new(b) for _, b in vs]
    for qd in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([ring[i] for i in qd])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); obj("AR_Pagode_O_band_tuin", bm, "graniet")
    rot = math.radians(A_UIT); f = Vector((math.cos(rot), math.sin(rot), 0)); tg = Vector((-f.y, f.x, 0))
    for k in range(9):
        r0 = R_VL - 0.02 + 0.33 * k
        zt = Z_I - (Z_I - Z_P - 0.03) * (k + 1) / 9
        c = pt(r0 + 0.33 / 2 + 0.01, A_UIT, (zt - 1.0) / 2)
        doos(f"AR_Pagode_O_uittrede_{k}", c, (0.35, 2.5, zt + 1.0), "klinker", rot)
    for s in (-1, 1):
        a_ = pt(R_VL, A_UIT, Z_I + 0.9) + tg * s * 1.15; b_ = pt(R_VL + 3.0, A_UIT, Z_P + 0.9) + tg * s * 1.15
        HEKKEN.append([list(a_ - Vector((0, 0, 0.9))), list(b_ - Vector((0, 0, 0.9))), 1.0])     # leuning uitgangstrap: botsing
        hb = pt(10.82, A_UIT + s * (gat + 0.3), Z_I + 0.12)                                       # aansluiting op het hek op de uitgangsmuur
        HEKKEN.append([list(hb), list(a_ - Vector((0, 0, 0.9))), 1.0])
        buis(f"AR_Pagode_O_uitleuning{s}_aansluiting", hb + Vector((0, 0, 0.9)), a_, 0.025, "hek", 6)
        buis(f"AR_Pagode_O_uitleuning{s}", a_, b_, 0.025, "hek", 6)
        for q in (0.0, 0.5, 1.0):
            p = a_ + (b_ - a_) * q
            buis(f"AR_Pagode_O_uitleuning{s}_paal{q}", p - Vector((0, 0, 0.92)), p, 0.025, "hek", 6)
    bord_mesh("AR_Pagode_O_uitgangsbord", [(0, 0), (1, 0), (1, 0.82), (0.5, 0.96), (0, 0.82)], 0.55, 1.15, 0.05,
              pt(10.5, A_UIT - 12.0, Z_I + 0.75), rot + math.pi, "uitgangsbord")     # tegen het hek, rand van de vlonder
    buis("AR_Pagode_O_uitgangspaal", pt(10.5, A_UIT - 12.0, Z_I) - f * 0.04, pt(10.5, A_UIT - 12.0, Z_I + 0.8) - f * 0.04, 0.035, "hek", 6)
    for k, aa in enumerate((A_UIT - 8.0, A_UIT + 30.0)):          # aan de voet van de keermuur, niet midden op het pad
        p = pt(11.55, aa, Z_P + 0.03); lantaarn(f"AR_Pagode_O_lamp_uit{k}", p); vrij(f"lamp_uit{k}", p, 0.13)
    p = pt(11.6, A_UIT + 9.0, Z_P + 0.03); afvalbak("AR_Pagode_O_bak_uit", p, rot); vrij("bak_uit", p, 0.3)
    # losse rotsblokken aan de voet van de muren (lemma: natuursteenranden en rotsblokken, video 5:55)
    for k in range(14):
        aa = rnd.uniform(-50, 50)
        if abs(aa - A_UIT) < 9: continue
        steen(f"AR_Pagode_O_muursteen_{k:02d}", pt(11.25, aa, Z_P + 0.1), (0.4, 0.3, 0.3))

    json.dump(LAMPEN, open(os.path.join(D, "exports", "omgeving_lampen.json"), "w"))
    json.dump(HEKKEN, open(os.path.join(D, "exports", "omgeving_hekken.json"), "w"))
    json.dump([[n, round(p.x, 3), round(p.y, 3), rad] for n, p, rad, _ in PLAATS], open(os.path.join(D, "exports", "omgeving_meubilair.json"), "w"))
    fout = controle()
    for regel in fout: print("[12_omgeving] OP LOOPPAD:", regel)
    assert not fout, "meubilair op een looppad"
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=m)
    print("[12_omgeving] %d objecten, %d lantaarns" % (len([o for o in bpy.data.objects if o.get("owner") == OWNER]), len(LAMPEN)))


build()
