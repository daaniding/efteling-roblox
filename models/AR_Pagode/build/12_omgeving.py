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


def aL(r): return a_c(r) - math.degrees(0.9 / r)          # laantje, tuinkant
def aR(r): return a_c(r) + math.degrees(0.9 / r)          # laantje, tribunekant
def aW(r): return aR(r) + math.degrees(0.42 / r)          # einde muur
def aS(r): return aW(r) + math.degrees(1.5 / r)           # einde trapstrook (begin zigzag)


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


def spijlenhek(naam, pts, h=1.1, rol="hek"):
    """Zwart spijlenhek (video 0:04-0:26, 6:40): palen met gouden bol om de ~2 m, boven-/onderregel, spijlen om de 12 cm.
    pts: lijst Vector (voet van het hek); hek volgt de lijn, ook schuin."""
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]; d = b - a; L = d.length
        if L < 0.05: continue
        rot = math.atan2(d.y, d.x)
        for nm, z in (("o", 0.1), ("b", h)):
            buis(f"{naam}_{k:02d}_regel{nm}", a + Vector((0, 0, z)), b + Vector((0, 0, z)), 0.022, rol, 4)
        n = max(1, int(L / 0.12))
        for i in range(1, n):
            p = a + d * (i / n)
            doos(f"{naam}_{k:02d}_sp{i:03d}", p + Vector((0, 0, (h + 0.1) / 2)), (0.018, 0.018, h - 0.08), rol, rot)
        np_ = max(1, int(L / 2.0))
        for i in range(np_ + (1 if k == len(pts) - 2 else 0)):
            p = a + d * (i / np_)
            doos(f"{naam}_{k:02d}_paal{i}", p + Vector((0, 0, (h + 0.12) / 2)), (0.06, 0.06, h + 0.12), rol, rot)
            bol(f"{naam}_{k:02d}_bol{i}", p + Vector((0, 0, h + 0.19)), 0.055)


def reling(naam, pts, rol="reling"):
    """Wachtrijreling (video 0:22-0:44): donkergroene buizen op 0.5 en 1.0 m, palen om de ~2 m met crèmegouden bol."""
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]; d = b - a; L = d.length
        if L < 0.05: continue
        for nm, z in (("o", 0.5), ("b", 1.0)):
            buis(f"{naam}_{k:02d}_{nm}", a + Vector((0, 0, z)), b + Vector((0, 0, z)), 0.024, rol, 6)
        np_ = max(1, int(L / 2.0))
        for i in range(np_ + (1 if k == len(pts) - 2 else 0)):
            p = a + d * (i / np_)
            buis(f"{naam}_{k:02d}_paal{i}", p, p + Vector((0, 0, 1.05)), 0.03, rol, 6)
            bol(f"{naam}_{k:02d}_bol{i}", p + Vector((0, 0, 1.1)), 0.05)


def boog(r, a0, a1, z, stap=2.0):
    n = max(1, int(abs(math.radians(a1 - a0)) * r / stap))
    return [pt(r, a0 + (a1 - a0) * i / n, z) for i in range(n + 1)]


def lantaarn(naam, p):
    """Bronzen lantaarnpaal met oosterse kap (video 0:38-0:44, 6:53): voet, paal 2.6 m, lantaarn 0.32 x 0.32 x 0.45, kap + pinakel."""
    p = Vector(p)
    buis(f"{naam}_voet", p, p + Vector((0, 0, 0.5)), 0.14, "brons", 8, 0.08)
    buis(f"{naam}_paal", p + Vector((0, 0, 0.45)), p + Vector((0, 0, 2.65)), 0.055, "brons", 8)
    buis(f"{naam}_kraag", p + Vector((0, 0, 2.6)), p + Vector((0, 0, 2.7)), 0.12, "brons", 8)
    doos(f"{naam}_glas", p + Vector((0, 0, 2.93)), (0.28, 0.28, 0.42), "lamp")
    for sx in (-1, 1):
        for sy in (-1, 1):
            doos(f"{naam}_stijl{sx}{sy}", p + Vector((sx * 0.15, sy * 0.15, 2.93)), (0.035, 0.035, 0.46), "brons")
    buis(f"{naam}_kap", p + Vector((0, 0, 3.15)), p + Vector((0, 0, 3.4)), 0.26, "brons", 4, 0.02)
    buis(f"{naam}_pinakel", p + Vector((0, 0, 3.38)), p + Vector((0, 0, 3.55)), 0.025, "goud", 6)
    LAMPEN.append([round(p.x, 3), round(p.y, 3), round(p.z + 2.93, 3)])


def afvalbak(naam, p, rot):
    p = Vector(p)
    doos(f"{naam}_bak", p + Vector((0, 0, 0.48)), (0.5, 0.5, 0.96), "staal_groen", rot)
    doos(f"{naam}_deksel", p + Vector((0, 0, 0.99)), (0.58, 0.58, 0.06), "staal_groen", rot)
    f = Vector((math.cos(rot), math.sin(rot), 0))
    buis(f"{naam}_embleem", p + f * 0.25 + Vector((0, 0, 0.55)), p + f * 0.262 + Vector((0, 0, 0.55)), 0.13, "goud", 12)


def bankje(naam, p, rot):
    p = Vector(p); f = Vector((math.cos(rot), math.sin(rot), 0)); t = Vector((-f.y, f.x, 0))
    doos(f"{naam}_zit", p + Vector((0, 0, 0.45)), (0.45, 1.8, 0.06), "rood", rot)
    doos(f"{naam}_rug", p - f * 0.22 + Vector((0, 0, 0.75)), (0.05, 1.8, 0.45), "rood", rot)
    for s in (-1, 1):
        doos(f"{naam}_poot{s}", p + t * s * 0.75 + Vector((0, 0, 0.22)), (0.42, 0.06, 0.44), "hek", rot)


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
        ringsector(f"AR_Pagode_O_laan_{t:02d}", r0 - 0.01, r1, -0.9, Z_P, aL(rm) - 0.15, aR(rm) + 0.05, "klinker", seg=2)
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
    ringsector("AR_Pagode_O_onderpad", 25.0, 26.8, -0.9, Z_P + 0.02, aL(25.9) - 0.2, A_ZUID, "klinker")
    # A3 keermuur langs het plein (1.7 m hoog, video 0:04-0:12) tot voorbij de kop van het laantje, met spijlenhek erop
    a_muur_eind = aW(14.5)
    ringsector("AR_Pagode_O_pleinmuur", 13.75, R_BO + 0.15, -0.95, Z_I + 0.25, 54.0, a_muur_eind, "breuksteen")
    spijlenhek("AR_Pagode_O_hek_plein", boog(13.95, 54.0, a_muur_eind, Z_I + 0.25))
    # hek op de laanmuur, schuin met de rijen mee
    lijn = [pt(R_BO + 0.15, (aR(14.2) + aW(14.2)) / 2, Z_I + 0.25)]
    for t in range(N_RIJ):
        rm = 14.5 + t; lijn.append(pt(rm, (aR(rm) + aW(rm)) / 2, ztop(t) + 0.3))
    spijlenhek("AR_Pagode_O_hek_laan", lijn)
    # lage reling + rotsblokken aan de tuinkant van het laantje (video 0:22-0:35)
    reling("AR_Pagode_O_reling_tuin", [pt(r, aL(r) - math.degrees(0.15 / r), Z_P) for r in (16.0, 19.0, 22.0, 25.0)])
    for k in range(22):
        r = 16.0 + k * 0.45
        steen(f"AR_Pagode_O_rand_{k:02d}", pt(r, aL(r) - math.degrees(0.35 / r), Z_P + 0.05), (0.28, 0.22, 0.16))
    # A4 wachtrijrelingen: zigzag over de rijen (keerpunten om en om), radiale reling langs de trapstrook
    for t in range(1, N_RIJ + 1):
        r = 14.0 + t + 0.12
        z = ztop(t) if t < N_RIJ else Z_P + 0.02
        gat = math.degrees(1.4 / r)
        a0, a1 = aS(r) + 0.3, A_RAIL
        if t % 2: a1 -= gat
        else: a0 += gat
        reling(f"AR_Pagode_O_rij_reling_{t:02d}", boog(r, a0, a1, z))
    rl = [pt(R_BO + 0.2, aS(14.2), Z_I)] + [pt(14.5 + t, aS(14.5 + t), ztop(t)) for t in range(N_RIJ)]
    reling("AR_Pagode_O_trap_reling", rl)
    # hek tussen bordes en tribune (Pagode-landing.jpg), open bij de trapstrook en bij het zuidpad
    spijlenhek("AR_Pagode_O_hek_bordes", boog(R_BO + 0.05, aS(14.2) + 2.0, A_RAIL - 2.0, Z_I))
    # A5 lantaarns langs de trapstrook, bij het zuidpad, op het plein, in de tuin
    for k, r in enumerate((17.5, 22.5)):
        lantaarn(f"AR_Pagode_O_lamp_trap{k}", pt(r, (aW(r) + aS(r)) / 2 + 0.6, ztop(int(r - 14.0))))
    lantaarn("AR_Pagode_O_lamp_zuid", pt(20.5, 154.8, ztop(6)))
    lantaarn("AR_Pagode_O_lamp_bordes", pt(13.3, 140.0, Z_I))
    lantaarn("AR_Pagode_O_lamp_plein0", pt(15.2, 88.0, Z_P))
    lantaarn("AR_Pagode_O_lamp_plein1", pt(15.2, 62.0, Z_P))
    lantaarn("AR_Pagode_O_lamp_tuin", pt(21.0, aL(21.0) - 6.0, Z_P + 0.3))

    # B1 controlehuisje (video 0:44-0:47, Pagode-landing.jpg): groen frame, rode onderpanelen, glas, rode band, donker dak
    hc = pt(12.0, 116.5, Z_I); rot = math.radians(116.5)
    f = Vector((math.cos(rot), math.sin(rot), 0)); tg = Vector((-f.y, f.x, 0))
    doos("AR_Pagode_O_huis_vloer", hc + Vector((0, 0, 0.06)), (1.95, 2.15, 0.12), "groen", rot)
    doos("AR_Pagode_O_huis_onder", hc + Vector((0, 0, 0.62)), (1.8, 2.0, 1.0), "rood", rot)
    doos("AR_Pagode_O_huis_binnen", hc + Vector((0, 0, 1.65)), (1.6, 1.8, 1.05), "onderkant", rot)
    doos("AR_Pagode_O_huis_glas", hc + Vector((0, 0, 1.67)), (1.84, 2.04, 1.1), "glas", rot)
    for sx in (-1, 1):
        for sy in (-1, 1):
            doos(f"AR_Pagode_O_huis_stijl{sx}{sy}", hc + f * sx * 0.92 + tg * sy * 1.02 + Vector((0, 0, 1.2)), (0.12, 0.12, 2.4), "groen", rot)
    for nm, z in (("r1", 1.14), ("r2", 2.24)):
        doos(f"AR_Pagode_O_huis_{nm}", hc + Vector((0, 0, z)), (1.9, 2.1, 0.08), "groen", rot)
    doos("AR_Pagode_O_huis_stijlmid", hc + f * 0.93 + Vector((0, 0, 1.68)), (0.07, 0.07, 1.1), "groen", rot)
    doos("AR_Pagode_O_huis_band", hc + Vector((0, 0, 2.43)), (2.1, 2.3, 0.3), "rood", rot)
    for nm, z in (("b0", 2.29), ("b1", 2.58)):
        doos(f"AR_Pagode_O_huis_{nm}", hc + Vector((0, 0, z)), (2.16, 2.36, 0.045), "groen", rot)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=1.75, radius2=0.08, depth=0.75)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot + math.pi / 4, 3, "Z"), verts=bm.verts)
    bmesh.ops.scale(bm, vec=(1, 1, 1), verts=bm.verts)
    bmesh.ops.translate(bm, vec=hc + Vector((0, 0, 2.6 + 0.375)), verts=bm.verts)
    obj("AR_Pagode_O_huis_dak", bm, "dak_donker")
    buis("AR_Pagode_O_huis_pinakel", hc + Vector((0, 0, 3.3)), hc + Vector((0, 0, 3.62)), 0.06, "goud", 8, 0.015)
    bol("AR_Pagode_O_huis_knop", hc + Vector((0, 0, 3.36)), 0.09)
    # B2 dubbele tourniquet voor het huisje, bovenaan de trapstrook (video 0:44-0:47)
    for k, aa in enumerate((112.4, 114.2)):
        p = pt(13.35, aa, Z_I); r_ = math.radians(aa)
        doos(f"AR_Pagode_O_tourniquet{k}", p + Vector((0, 0, 0.5)), (0.3, 0.24, 1.0), "hek", r_)
        doos(f"AR_Pagode_O_tourniquet{k}_licht", p + Vector((0, 0, 1.03)), (0.26, 0.2, 0.06), "lamp_groen", r_)
        doos(f"AR_Pagode_O_tourniquet{k}_bordje", p + Vector((math.cos(r_), math.sin(r_), 0)) * 0.125 + Vector((0, 0, 0.68)), (0.01, 0.18, 0.28), "bord_blauw", r_)
    # B3 ingangsbord PAGODE over de kop van het laantje (video 0:13-0:19), dwars op het laantje
    pa, pb = pt(14.6, a_c(14.6)), pt(16.6, a_c(16.6)); lr = (pb - pa).normalized()
    mid = pt(14.9, a_c(14.9), Z_P)
    rot = math.atan2(lr.y, lr.x) + math.pi            # voorkant naar het plein
    tg = Vector((-lr.y, lr.x, 0))
    for k, s in enumerate((-1, 1)):
        p = mid + tg * s * 1.5
        buis(f"AR_Pagode_O_bordpaal{k}", p + Vector((0, 0, -0.3)), p + Vector((0, 0, 3.35)), 0.065, "hek", 8)
        buis(f"AR_Pagode_O_bordpaal{k}_kap", p + Vector((0, 0, 3.35)), p + Vector((0, 0, 3.45)), 0.085, "brons", 8)
        bol(f"AR_Pagode_O_bordpaal{k}_bol", p + Vector((0, 0, 3.55)), 0.11)
    bord_mesh("AR_Pagode_O_ingangsbord", tex.BORD_OMTREK(48), 2.8, 1.05, 0.07, mid + Vector((0, 0, 2.2)), rot, "ingangsbord")
    doos("AR_Pagode_O_regelbord", mid + tg * 1.5 + Vector((0, 0, 1.45)) - lr * 0.08, (0.02, 0.3, 0.5), "bord_blauw", rot)
    afvalbak("AR_Pagode_O_bak_plein", pt(14.7, 97.5, Z_P), math.radians(97.5))
    afvalbak("AR_Pagode_O_bak_bordes", pt(12.9, 101.5, Z_I), math.radians(101.5 + 180))
    afvalbak("AR_Pagode_O_bak_zuid", pt(13.4, 151.0, Z_I), math.radians(151 + 180))
    afvalbak("AR_Pagode_O_bak_onder", pt(25.9, 155.6, Z_P + 0.02), math.radians(155.6 + 180))
    # bloempot met bamboe naast het bord (video 0:04-0:12); de bamboe zelf komt met de beplanting
    buis("AR_Pagode_O_pot", pt(15.7, 95.0, Z_P), pt(15.7, 95.0, Z_P + 0.62), 0.36, "rood", 12, 0.28)   # voor het plantvak (17)
    # rode bankjes langs de pleinmuur (Pagode-landing.jpg)
    for k, aa in enumerate((70.0, 82.0)):
        bankje(f"AR_Pagode_O_bank{k}", pt(15.75, aa, Z_P), math.radians(aa))

    # C uitgang aan de oostkant (video 6:15-6:45): keermuur langs de vlonder, trap naar het pad, hek, uitgangsbord
    A_UIT = -20.0; gat = math.degrees(1.3 / 10.8)
    for k, (a0, a1) in enumerate(((-52.0, A_UIT - gat), (A_UIT + gat, 54.0))):
        ringsector(f"AR_Pagode_O_oostmuur{k}", R_VL, 11.0, -1.0, Z_I + 0.12, a0, a1, "breuksteen")
        spijlenhek(f"AR_Pagode_O_hek_oost{k}", boog(10.82, a0 + 0.3, a1 - 0.3, Z_I + 0.12))
    for k in range(4):                     # in stukken: kleine UV-getallen per object (precisie in Roblox)
        ringsector(f"AR_Pagode_O_pad_oost{k}", 11.0, R_BO + 0.15, -0.9, Z_P + 0.03, -52.0 + 26.5 * k, -52.0 + 26.5 * (k + 1), "klinker")
    for k in range(5):
        ringsector(f"AR_Pagode_O_plein{k}", R_BO + 0.15, 24.0, -0.9, Z_P, -52.0 + 28.0 * k, -52.0 + 28.0 * (k + 1), "klinker")
    ringsector("AR_Pagode_O_plein_kop", R_BO + 0.15, 16.2, -0.9, Z_P, 88.0, aL(15.2) - 0.1, "klinker", seg=3)
    rot = math.radians(A_UIT); f = Vector((math.cos(rot), math.sin(rot), 0)); tg = Vector((-f.y, f.x, 0))
    for k in range(9):
        r0 = R_VL - 0.02 + 0.33 * k
        zt = Z_I - (Z_I - Z_P - 0.03) * (k + 1) / 9
        c = pt(r0 + 0.33 / 2 + 0.01, A_UIT, (zt - 1.0) / 2)
        doos(f"AR_Pagode_O_uittrede_{k}", c, (0.35, 2.5, zt + 1.0), "klinker", rot)
    for s in (-1, 1):
        a_ = pt(R_VL, A_UIT, Z_I + 0.9) + tg * s * 1.15; b_ = pt(R_VL + 3.0, A_UIT, Z_P + 0.9) + tg * s * 1.15
        buis(f"AR_Pagode_O_uitleuning{s}", a_, b_, 0.025, "hek", 6)
        for q in (0.0, 0.5, 1.0):
            p = a_ + (b_ - a_) * q
            buis(f"AR_Pagode_O_uitleuning{s}_paal{q}", p - Vector((0, 0, 0.92)), p, 0.025, "hek", 6)
    bord_mesh("AR_Pagode_O_uitgangsbord", [(0, 0), (1, 0), (1, 0.82), (0.5, 0.96), (0, 0.82)], 0.55, 1.15, 0.05,
              pt(10.35, A_UIT - 12.0, Z_I + 0.75), rot + math.pi, "uitgangsbord")
    buis("AR_Pagode_O_uitgangspaal", pt(10.35, A_UIT - 12.0, Z_I) - f * 0.04, pt(10.35, A_UIT - 12.0, Z_I + 0.8) - f * 0.04, 0.035, "hek", 6)
    lantaarn("AR_Pagode_O_lamp_uit0", pt(14.0, A_UIT - 8.0, Z_P + 0.03))
    lantaarn("AR_Pagode_O_lamp_uit1", pt(14.0, A_UIT + 30.0, Z_P + 0.03))
    afvalbak("AR_Pagode_O_bak_uit", pt(11.3, A_UIT + 9.0, Z_P + 0.03), rot)
    # losse rotsblokken aan de voet van de muren (lemma: natuursteenranden en rotsblokken, video 5:55)
    for k in range(14):
        aa = rnd.uniform(-50, 50)
        if abs(aa - A_UIT) < 9: continue
        steen(f"AR_Pagode_O_muursteen_{k:02d}", pt(11.25, aa, Z_P + 0.1), (0.4, 0.3, 0.3))

    json.dump(LAMPEN, open(os.path.join(D, "exports", "omgeving_lampen.json"), "w"))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=m)
    print("[12_omgeving] %d objecten, %d lantaarns" % (len([o for o in bpy.data.objects if o.get("owner") == OWNER]), len(LAMPEN)))


build()
