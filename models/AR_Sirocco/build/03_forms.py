"""03_forms: Sirocco vormen naar de foto's (asset-brief.md). Zelfde modelframe als 02_blockout (m, x oost, y noord, z 0 = water,
oorsprong = dakmidden). Vervangt de blockout-massa's (die worden verborgen).
Bronnen: Sirocco-binnen.jpg / Overzicht_sirocco.jpg (balkconstructie: ruwe stammen, schoren, radiale spanten, ringbalken,
donkere dakbeschot onderkant; boten op eigen blauwe voet, mast met opgerold zeil), Siro-boot-voor/-achter.jpg (romp: rode
planken, blauwe schubben op de boeg, blauw snijwerkpaneel met gouden krullen achter, bakje handelswaar), Wolmonsieurcannibale.jpg
(indeling schijven), doorsnede B-B (dakvorm), luchtfoto (plek).
Rollen (ob["rol"]): riet, beschot, stam, platform, subschijf, voet, vlonder, romp, schubben, sierpaneel, goud, zeil, mast, touw,
kist, fruit_oranje, fruit_geel, fles, ton.
Gebruik: blender --background --python build/03_forms.py -- --master AR_Sirocco_master.blend"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = "phase:03_forms"
random.seed(1988)

# --- maten (zelfde als 02_blockout) ---
R_DAK, Z_NOK, Z_RAND, Z_VLEUGEL = 8.85, 11.6, 3.0, 7.4
VOOR = math.radians(-124.0); VLEUGEL_HALF = math.radians(55.0)
DIK_RIET = 0.45
R_SCHIJF, R_DEK, Z_PLAT = 7.0, 8.6, 0.3
R_PAAL, N_PAAL = 8.0, 16
R_SUB, R_SUBMID = 2.3, 3.8


def vleugel(t):
    d = (t - VOOR + math.pi) % (2 * math.pi) - math.pi
    if abs(d) >= VLEUGEL_HALF: return 0.0
    return math.cos(d / VLEUGEL_HALF * math.pi / 2) ** 2


def dak_z(r, t, onder=0.0):
    """hoogte van het dakoppervlak (boven) op straal r, hoek t; onder = diepte (onderkant = DIK_RIET)"""
    w = vleugel(t)
    e = Z_RAND + (Z_VLEUGEL - Z_RAND) * w
    R = R_DAK + 0.8 * w
    u = min(1.0, r / R); p = 1.55 - 0.65 * w
    return e + (Z_NOK - e) * (1 - u) ** p - onder


def dak_R(t): return R_DAK + 0.8 * vleugel(t)


# --- hulpfuncties ---
def collectie(naam):
    c = bpy.data.collections.get(naam)
    if not c:
        c = bpy.data.collections.new(naam); bpy.context.scene.collection.children.link(c)
    return c


def obj(naam, bm, rol):
    me = bpy.data.meshes.new(naam); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(naam, me); o["owner"] = OWNER; o["rol"] = rol
    collectie("LOW").objects.link(o)
    return o


def stam(bm, a, b, r0, r1=None, seg=8, ruw=0.12):
    """ruwe boomstam van a naar b (licht taps, onregelmatige doorsnede)"""
    a, b = Vector(a), Vector(b)
    r1 = r0 * 0.88 if r1 is None else r1
    as_ = (b - a); L = as_.length; z = as_.normalized()
    x = z.cross(Vector((0, 0, 1)) if abs(z.z) < 0.9 else Vector((1, 0, 0))).normalized(); y = z.cross(x)
    ringen = []
    n = max(2, int(L / 0.8) + 1)
    for k in range(n + 1):
        f = k / n
        c = a + as_ * f
        r = r0 + (r1 - r0) * f
        ring = []
        for i in range(seg):
            h = 2 * math.pi * i / seg
            rr = r * (1 + ruw * (random.random() - 0.5))
            ring.append(bm.verts.new(c + (x * math.cos(h) + y * math.sin(h)) * rr))
        ringen.append(ring)
    for k in range(n):
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((ringen[k][i], ringen[k][j], ringen[k + 1][j], ringen[k + 1][i]))
    bm.faces.new(ringen[0][::-1]); bm.faces.new(ringen[-1])


def cil(bm, c, r, h, seg=32, r_top=None):
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r_top is None else r_top, depth=h)
    bmesh.ops.translate(bm, vec=Vector(c) + Vector((0, 0, h / 2)), verts=res["verts"])
    return res["verts"]


def bol(bm, c, r, seg=10):
    res = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(4, seg // 2), radius=r)
    bmesh.ops.translate(bm, vec=Vector(c), verts=res["verts"])
    return res["verts"]


def doos(bm, c, s, rot=0.0):
    res = bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=s, verts=res["verts"])
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z"), verts=res["verts"])
    bmesh.ops.translate(bm, vec=Vector(c), verts=res["verts"])
    return res["verts"]


# --- dak ---
def dak():
    NA, NR = 160, 30
    bm = bmesh.new()
    def p(i, k, onder):
        t = 2 * math.pi * i / NA
        R = dak_R(t); r = R * k / NR
        # rafelige rand: riet steekt ongelijk uit
        if k == NR: r += 0.08 * math.sin(i * 7.3) + 0.05 * math.sin(i * 2.1)
        return (r * math.cos(t), r * math.sin(t), dak_z(min(r, R), t, onder))
    boven = [[bm.verts.new(p(i, k, 0)) for i in range(NA)] for k in range(1, NR + 1)]
    onder = [[bm.verts.new(p(i, k, DIK_RIET)) for i in range(NA)] for k in range(1, NR + 1)]
    tb = bm.verts.new((0, 0, Z_NOK)); to = bm.verts.new((0, 0, Z_NOK - DIK_RIET))
    for i in range(NA):
        j = (i + 1) % NA
        bm.faces.new((tb, boven[0][i], boven[0][j]))
        for k in range(NR - 1):
            bm.faces.new((boven[k][i], boven[k + 1][i], boven[k + 1][j], boven[k][j]))
        bm.faces.new((boven[-1][i], onder[-1][i], onder[-1][j], boven[-1][j]))      # rietrand
    obj("SI_dak_riet", bm, "riet")
    # onderkant: donker beschot (aparte rol), iets onder het riet
    bm = bmesh.new()
    ond = [[bm.verts.new(p(i, k, DIK_RIET)) for i in range(NA)] for k in range(1, NR + 1)]
    to = bm.verts.new((0, 0, Z_NOK - DIK_RIET))
    for i in range(NA):
        j = (i + 1) % NA
        bm.faces.new((to, ond[0][j], ond[0][i]))
        for k in range(NR - 1):
            bm.faces.new((ond[k][j], ond[k + 1][j], ond[k + 1][i], ond[k][i]))
    obj("SI_dak_beschot", bm, "beschot")
    # nokstuk: houten kegel + spits (Monsieurdakbedekking.jpg: nokkap)
    bm = bmesh.new()
    cil(bm, (0, 0, Z_NOK - 0.6), 0.55, 0.7, 16, 0.22)
    cil(bm, (0, 0, Z_NOK + 0.1), 0.12, 1.1, 8, 0.03)
    obj("SI_dak_nok", bm, "stam")


# --- balkconstructie ---
def constructie():
    bm = bmesh.new()
    ring_pts = []
    for i in range(N_PAAL):
        t = 2 * math.pi * (i + 0.5) / N_PAAL
        r = R_PAAL
        top = dak_z(r, t, DIK_RIET) - 0.35            # ringbalk onder het dak
        c = Vector((r * math.cos(t), r * math.sin(t), 0))
        stam(bm, c + Vector((0, 0, Z_PLAT - 0.1)), c + Vector((0, 0, top)), 0.17, 0.15)   # paal
        ring_pts.append(c + Vector((0, 0, top)))
        # schoren (Y-vorm uit de foto): van de paal schuin naar de ringbalk links en rechts
        for s in (-1, 1):
            t2 = t + s * math.radians(360 / N_PAAL * 0.38)
            top2 = dak_z(r, t2, DIK_RIET) - 0.35
            stam(bm, c + Vector((0, 0, top - 1.1)), Vector((r * math.cos(t2), r * math.sin(t2), top2)), 0.07, 0.06, 6)
        # schoor naar binnen (naar het spant)
        ri = r - 1.2
        stam(bm, c + Vector((0, 0, top - 1.0)), Vector((ri * math.cos(t), ri * math.sin(t), dak_z(ri, t, DIK_RIET) - 0.2)), 0.07, 0.06, 6)
    for i in range(N_PAAL):                           # ringbalk
        stam(bm, ring_pts[i], ring_pts[(i + 1) % N_PAAL], 0.14, 0.14, 8, 0.08)
    # radiale spanten: 32, langs de onderkant van het dak tot de nok
    N_SP = 16
    for i in range(N_SP):
        t = 2 * math.pi * i / N_SP
        punten = []
        R = dak_R(t)
        for k in range(9):
            r = 0.45 + (R - 0.25 - 0.45) * k / 8
            punten.append(Vector((r * math.cos(t), r * math.sin(t), dak_z(r, t, DIK_RIET) - 0.13)))
        for k in range(8):
            stam(bm, punten[k], punten[k + 1], 0.17, 0.16, 8, 0.06)
    # ringgordingen op 3 stralen
    for rr in (2.4, 4.3, 6.2):
        M = 16
        pts = [Vector((rr * math.cos(2 * math.pi * i / M), rr * math.sin(2 * math.pi * i / M), 0)) for i in range(M)]
        for p in pts: p.z = dak_z(rr, math.atan2(p.y, p.x), DIK_RIET) - 0.28
        for i in range(M):
            stam(bm, pts[i], pts[(i + 1) % M], 0.11, 0.11, 6, 0.06)
    obj("SI_constructie", bm, "stam")


# --- platform, draaischijf, ton ---
def platform():
    bm = bmesh.new(); cil(bm, (0, 0, Z_PLAT - 0.3), R_SCHIJF, 0.3, 96); obj("SI_schijf", bm, "platform")
    bm = bmesh.new()
    for s in range(3):
        a = VOOR + math.radians(90 + 120 * s)
        cil(bm, (R_SUBMID * math.cos(a), R_SUBMID * math.sin(a), Z_PLAT - 0.03), R_SUB, 0.13, 64)   # zakt 3 cm in de schijf: geen samenvallende vlakken (z-fighting)
    obj("SI_subschijven", bm, "subschijf")
    # vlonderdek rond de schijf (vast) tot onder de dakrand
    bm = bmesh.new(); seg = 128
    for z0, z1 in ((Z_PLAT - 0.35, Z_PLAT),):
        b = [[bm.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)] for r in (R_SCHIJF + 0.03, R_DEK) for z in (z0, z1)]
        bi0, bi1, bu0, bu1 = b
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((bi1[i], bu1[i], bu1[j], bi1[j]))
            bm.faces.new((bu0[i], bu0[j], bu1[j], bu1[i]))
            bm.faces.new((bi0[j], bi0[i], bi1[i], bi1[j]))
    obj("SI_vlonder", bm, "vlonder")
    # ton(nen) in het midden ("lijkt in de woelige baren te dobberen") + twee kleinere vaten
    bm = bmesh.new()
    for c, r, h in (((0, 0, Z_PLAT), 0.55, 1.1), ((0.85, 0.3, Z_PLAT), 0.35, 0.75), ((-0.5, 0.75, Z_PLAT), 0.32, 0.7)):
        v = cil(bm, c, r, h, 20)
        for vv in v:                                   # buik
            f = 1 - abs((vv.co.z - c[2]) / h - 0.5) * 2
            d = Vector((vv.co.x - c[0], vv.co.y - c[1], 0)); vv.co += d * 0.12 * f
    obj("SI_tonnen", bm, "ton")


# --- boten v2 (Daan 17 nov: "eerst nog even de boten verbeteren"; Siro-boot-voor/achter.jpg, Sirocco-bootjes.jpg, Sirocco-binnen.jpg)
# romp: tobbe die naar boven uitloopt, spitse boeg (lokaal +x), planken (hout / rood / blauw per boot); boeg: rode voorsteven die
# boven de rand omkrult, twee rode banden in een V met een driehoek blauwe schubben ertussen, witte golf aan de voet; dikke rode
# rand; achter een hoog blauw paneel met golvende bovenkant en gouden krullen; binnen donkerrood met bank rondom; midden een
# draaitafel met mast, ring met opgebonden zeildoek en vlaggetje; kist sinaasappels + fles achterin tegen het paneel.
BL, BB, BH = 0.95, 0.76, 0.86          # halve lengte, halve breedte (boven), randhoogte boven de voet
Z_VOET = 0.12


def romp_xy(t, u, krimp=0.0):
    """plattegrond op hoogte u (0 onder, 1 rand): ovaal met spitse boeg, naar boven uitlopend"""
    s = 0.80 + 0.20 * u ** 0.8 - krimp
    x = math.cos(t); y = math.sin(t)
    if x > 0: x = x * (1 + 0.28 * x ** 4)
    return Vector((BL * x * s, BB * y * s, 0))


def rand_z(t):
    x = math.cos(t)
    return Z_VOET + BH + 0.10 * max(0, x) ** 8 + 0.04 * max(0, -x) ** 2


def boeg_half(u):
    """halve breedte (m, in y) van de schubbendriehoek op hoogte u"""
    return 0.06 + 0.46 * u


def buis(bm, pts, r, seg=6):
    for k in range(len(pts) - 1):
        stam(bm, pts[k], pts[k + 1], r, r, seg, 0.0)


def boot(naam, c, rot, romp_rol="romp_hout"):
    bms = {r: bmesh.new() for r in ("romp", "schubben", "rood", "binnen", "sierpaneel", "goud", "golf", "voet", "zeil", "mast", "kist",
                                     "fruit_oranje", "fles")}
    M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(rot, 4, "Z")
    NT, NU = 48, 8
    cil(bms["voet"], (0, 0, -0.03), 1.08, Z_VOET + 0.03, 48)   # 3 cm in de vloer: geen z-fighting met schijf/subschijf
    # buitenschil, per vlak: schubben (driehoek op de boeg) of planken
    P = [[None] * NT for _ in range(NU + 1)]
    for k in range(NU + 1):
        u = k / NU
        for i in range(NT):
            t = 2 * math.pi * i / NT
            p = romp_xy(t, u); p.z = Z_VOET + 0.02 + u * (rand_z(t) - Z_VOET - 0.02)
            P[k][i] = p
    for k in range(NU):
        for i in range(NT):
            j = (i + 1) % NT
            q = (P[k][i] + P[k][j] + P[k + 1][j] + P[k + 1][i]) / 4
            u = (k + 0.5) / NU
            bm = bms["romp"]
            bm.faces.new([bm.verts.new(v) for v in (P[k][i], P[k][j], P[k + 1][j], P[k + 1][i])])
    # schubbendriehoek als eigen vlak precies tussen de rode banden, net voor de romp (geen trapjes)
    def t_bij_y(y, u):
        lo, hi = -math.pi / 2, math.pi / 2
        for _ in range(30):
            m = (lo + hi) / 2
            if romp_xy(m, u).y < y: lo = m
            else: hi = m
        return (lo + hi) / 2
    NUS, NYS = 12, 8
    G = []
    for k in range(NUS + 1):
        u = k / NUS; h = boeg_half(u); rij = []
        for j in range(NYS + 1):
            y = -h + 2 * h * j / NYS; t = t_bij_y(y, u)
            p = romp_xy(t, u); p.z = Z_VOET + 0.02 + u * (rand_z(t) - Z_VOET - 0.02)
            rij.append(p + Vector((p.x, p.y, 0)).normalized() * 0.025)      # 2,5 cm voor de romp (minder geeft z-gevecht in Roblox)
        G.append(rij)
    bm = bms["schubben"]
    uvl = bm.loops.layers.uv.verify()
    for k in range(NUS):
        for j in range(NYS):
            hoeken = (G[k][j], G[k][j + 1], G[k + 1][j + 1], G[k + 1][j])
            for volgorde in (hoeken, hoeken[::-1]):    # tweezijdig (achterkant zit in de romp, zie je niet)
                f = bm.faces.new([bm.verts.new(v) for v in volgorde])
                for lp in f.loops:                     # vlakke UV langs de boeg (lokaal y, z), altijd positief: 0,6 m per textuur
                    lp[uvl].uv = (2 + lp.vert.co.y / 0.6, lp.vert.co.z / 0.6)
    # binnenschil (donkerrood) + vloer + bank rondom
    Q = [[None] * NT for _ in range(NU + 1)]
    for k in range(NU + 1):
        u = k / NU
        for i in range(NT):
            t = 2 * math.pi * i / NT
            p = romp_xy(t, u, 0.09); p.z = max(Z_VOET + 0.25, Z_VOET + 0.02 + u * (rand_z(t) - Z_VOET - 0.02)); Q[k][i] = p
    bm = bms["binnen"]
    for k in range(NU):
        for i in range(NT):
            j = (i + 1) % NT
            bm.faces.new([bm.verts.new(v) for v in (Q[k][j], Q[k][i], Q[k + 1][i], Q[k + 1][j])])
    bm.faces.new([bm.verts.new(Vector((Q[0][i].x, Q[0][i].y, Z_VOET + 0.25))) for i in range(NT)])
    for i in range(NT):                                # bank: 0,45 m hoog, 0,35 m diep, niet voorin (boeg)
        t = 2 * math.pi * i / NT; t2 = 2 * math.pi * (i + 1) / NT
        if math.cos(t) > 0.45: continue
        a0 = romp_xy(t, 0.5, 0.10); a1 = romp_xy(t2, 0.5, 0.10)
        b0 = a0 * 0.62; b1 = a1 * 0.62
        z = Z_VOET + 0.45
        bm.faces.new([bm.verts.new(Vector((v.x, v.y, z))) for v in (a0, a1, b1, b0)])
        bm.faces.new([bm.verts.new(Vector((v.x, v.y, zz))) for v, zz in ((b0, z), (b1, z), (b1, Z_VOET + 0.25), (b0, Z_VOET + 0.25))])
    # dikke rode rand rondom (ook over de rand van de binnenschil)
    rand = [(P[NU][i] + Q[NU][i]) / 2 + Vector((0, 0, 0.02)) for i in range(NT)]
    buis(bms["rood"], rand + [rand[0]], 0.055, 8)
    # rode banden langs de schubbendriehoek (iets naar buiten) en de voorsteven met krul
    for s in (-1, 1):
        lijn = []
        for k in range(17):                            # exact op de rand van de driehoek: t zoeken waar y = boeg_half(u)
            u = k / 16; yb = boeg_half(u)
            lo, hi = 0.0, math.pi / 2
            for _ in range(30):
                m = (lo + hi) / 2
                if romp_xy(m, u).y < yb: lo = m
                else: hi = m
            t = s * (lo + hi) / 2
            p = romp_xy(t, u); p.z = Z_VOET + 0.02 + u * (rand_z(t) - Z_VOET - 0.02)
            n = Vector((p.x, p.y, 0)).normalized(); lijn.append(p + n * 0.03)
        buis(bms["rood"], lijn, 0.05, 8)
    voor = [P[k][0] + Vector((0.03, 0, 0)) for k in range(NU + 1)]
    top = voor[-1]
    krul = [top + Vector((0.02, 0, 0.12)), top + Vector((-0.02, 0, 0.26)), top + Vector((-0.12, 0, 0.32)), top + Vector((-0.2, 0, 0.26)),
            top + Vector((-0.17, 0, 0.17))]
    buis(bms["rood"], voor + krul, 0.06, 8)
    # witte golf aan de voet van de boeg (gekrulde schuimkop)
    for k in range(7):
        h = (k - 3) * 0.16
        p = romp_xy(h, 0.05) * 1.06; p.z = Z_VOET + 0.08 + 0.05 * (1 - abs(k - 3) / 3)
        v = bol(bms["golf"], p, 0.11 - 0.012 * abs(k - 3), 8)
        for vv in v: vv.co.z = p.z + (vv.co.z - p.z) * 0.6
    # achterpaneel: gebogen plank langs de achtersteven, golvende bovenkant (hoog in het midden), blauw met goud
    NP = 16
    tp0, tp1 = math.pi - 1.15, math.pi + 1.15
    rij_o, rij_b, rij_ob, rij_bb = [], [], [], []
    for k in range(NP + 1):
        f = k / NP; t = tp0 + (tp1 - tp0) * f
        p = romp_xy(t, 1.0, -0.01)
        top_z = rand_z(t) + 0.12 + 0.46 * math.sin(f * math.pi) ** 1.3 + 0.07 * math.sin(f * math.pi * 4)   # hoog achterpaneel
        rij_o.append(Vector((p.x, p.y, rand_z(t) - 0.25))); rij_b.append(Vector((p.x, p.y, top_z)))
        pi_ = romp_xy(t, 1.0, 0.07); rij_ob.append(Vector((pi_.x, pi_.y, rand_z(t) - 0.25))); rij_bb.append(Vector((pi_.x, pi_.y, top_z)))
    bm = bms["sierpaneel"]
    for k in range(NP):
        bm.faces.new([bm.verts.new(v) for v in (rij_o[k], rij_o[k + 1], rij_b[k + 1], rij_b[k])])
        bm.faces.new([bm.verts.new(v) for v in (rij_ob[k + 1], rij_ob[k], rij_bb[k], rij_bb[k + 1])])
        bm.faces.new([bm.verts.new(v) for v in (rij_b[k], rij_b[k + 1], rij_bb[k + 1], rij_bb[k])])
    rand_goud = [(rij_b[k] + rij_bb[k]) / 2 + Vector((0, 0, 0.02)) for k in range(NP + 1)]
    buis(bms["goud"], rand_goud, 0.045, 8)
    for e, s in ((rand_goud[0], 1), (rand_goud[-1], -1)):      # gouden krullen aan de uiteinden
        d = (Vector((0, 0, 0)) - Vector((e.x, e.y, 0))).normalized() * 0.0
        spir = [e + Vector((0, 0, -0.08 * j)) + Vector((math.cos(j * 1.4) * 0.07 * (1 - j / 6), math.sin(j * 1.4) * 0.07 * (1 - j / 6) * s, 0)) for j in range(6)]
        buis(bms["goud"], [e] + spir, 0.035, 6)
    # draaitafel in het midden + mast met ring van opgebonden zeildoek en vlaggetje
    cil(bms["goud"], (0.05, 0, Z_VOET + 0.25), 0.09, 0.45, 10)
    cil(bms["goud"], (0.05, 0, Z_VOET + 0.70), 0.34, 0.05, 20)
    stam(bms["mast"], (0.05, 0, Z_VOET + 0.75), (0.05, 0, 3.05), 0.035, 0.028, 8, 0.0)
    ring = [Vector((0.05 + 0.48 * math.cos(2 * math.pi * i / 10), 0.48 * math.sin(2 * math.pi * i / 10), 2.55)) for i in range(10)]
    buis(bms["mast"], ring + [ring[0]], 0.02, 5)
    mid = Vector((0.05, 0, 2.55))
    bmz = bms["zeil"]
    for i in range(10):                                # doek in gedrapeerde bogen tussen de ringpunten (Sirocco-bootjes.jpg)
        a, b = ring[i], ring[(i + 1) % 10]
        boven, onder = [], []
        for k in range(7):
            f = k / 6; zak = math.sin(f * math.pi)
            q = a.lerp(b, f); uit = (Vector((q.x, q.y, 0)) - Vector((mid.x, mid.y, 0))).normalized()
            rand_p = Vector((mid.x, mid.y, 0)) + uit * 0.5; rand_p.z = mid.z + 0.01      # vast aan de rand van het doekdak
            boven.append(rand_p)
            onder.append(rand_p + uit * (0.03 + 0.06 * zak) + Vector((0, 0, -0.08 - 0.22 * zak)))    # hangt door in een boog
        for k in range(6):                             # tweezijdig doek
            bmz.faces.new([bmz.verts.new(v) for v in (onder[k], onder[k + 1], boven[k + 1], boven[k])])
            bmz.faces.new([bmz.verts.new(v) for v in (boven[k], boven[k + 1], onder[k + 1], onder[k])])
    # plat doekdak over de ring (licht bol, iets overhangend): het opgerolde zeil als parasol (Sirocco-bootjes.jpg)
    NK = 20
    rand_d = [Vector((0.05 + 0.5 * math.cos(2 * math.pi * i / NK), 0.5 * math.sin(2 * math.pi * i / NK), 2.56 + 0.02 * math.sin(i * 2.7))) for i in range(NK)]
    tp = bmz.verts.new((0.05, 0, 2.68))
    for i in range(NK):
        bmz.faces.new((tp, bmz.verts.new(rand_d[i]), bmz.verts.new(rand_d[(i + 1) % NK])))
        bmz.faces.new((bmz.verts.new((0.05, 0, 2.67)), bmz.verts.new(rand_d[(i + 1) % NK] - Vector((0, 0, 0.01))), bmz.verts.new(rand_d[i] - Vector((0, 0, 0.01)))))
    doos(bms["zeil"], (0.05 + 0.13, 0, 2.98), (0.22, 0.012, 0.12))   # vlaggetje
    # kist met sinaasappels en een fles, achterin tegen het paneel
    kc = romp_xy(math.pi, 0.9, 0.16); kc.z = Z_VOET + 0.86
    doos(bms["kist"], kc, (0.28, 0.62, 0.24))
    for i in range(9):
        bol(bms["fruit_oranje"], kc + Vector((random.uniform(-0.08, 0.08), -0.26 + i * 0.065, 0.16 + random.uniform(0, 0.06))), 0.06, 8)
    cil(bms["fles"], kc + Vector((0.02, 0.2, 0.12)), 0.04, 0.3, 8, 0.015)
    out = []
    for rol, bm in bms.items():
        if not bm.verts: bm.free(); continue
        bm.transform(M)
        if rol not in ("romp", "schubben", "binnen", "sierpaneel", "zeil"):    # losse vlakken: richting klopt al (recalc draait ze willekeurig om)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        echte_rol = romp_rol if rol == "romp" else rol
        out.append(obj(f"SI_{naam}_{rol}", bm, echte_rol))
    return out


def boten():
    kleuren = ["romp_hout", "romp", "romp_blauw"]
    n = 0
    for s in range(3):
        a = VOOR + math.radians(90 + 120 * s)
        c = Vector((R_SUBMID * math.cos(a), R_SUBMID * math.sin(a), Z_PLAT + 0.10))
        for b in range(3):
            ab = a + math.radians(120 * b + 40)
            boot(f"boot{n:02d}", c + Vector((1.25 * math.cos(ab), 1.25 * math.sin(ab), 0)), ab + random.uniform(-1, 1), kleuren[n % 3]); n += 1
        a2 = a + math.radians(60)
        boot(f"boot{n:02d}", (5.75 * math.cos(a2), 5.75 * math.sin(a2), Z_PLAT), a2 + math.pi / 2, kleuren[n % 3]); n += 1


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    master = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=master)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    for o in bpy.data.objects:                          # blockout verbergen (water blijft tot de scène er is)
        if o.get("owner") == "phase:02_blockout" and o.name != "SI_blk_water":
            o.hide_render = True; o.hide_viewport = True
    dak(); constructie(); platform(); boten()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=master)
    tris = 0
    dg = bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.objects:
        if o.get("owner") == OWNER:
            tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    print("[03_forms] klaar:", len([o for o in bpy.data.objects if o.get("owner") == OWNER]), "objecten,", tris, "driehoeken")


main()
