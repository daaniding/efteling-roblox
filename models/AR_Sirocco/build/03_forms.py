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
        cil(bm, (R_SUBMID * math.cos(a), R_SUBMID * math.sin(a), Z_PLAT), R_SUB, 0.06, 64)
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


# --- boten ---
def romp_punt(t, z_rel, schaal):
    """plattegrond van de romp: ovaal met een spitse boeg (t=0 = boeg, langs +x)"""
    L, B = 0.98, 0.74
    x = math.cos(t); y = math.sin(t)
    if x > 0: x = x * (1 + 0.30 * x ** 3)          # boeg puntiger/langer
    bol_ = 1 + 0.04 * (1 - abs(z_rel - 0.6) * 1.6)   # bijna rechte wanden (foto: lage tobbe)
    return Vector((L * x * schaal * bol_, B * y * schaal * bol_, 0))


def boot(naam, c, rot, romp_rol="romp"):
    bms = {r: bmesh.new() for r in ("romp", "schubben", "sierpaneel", "goud", "voet", "zeil", "mast", "kist", "fruit_oranje", "fles", "touw")}
    M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(rot, 4, "Z")
    NT, NZ = 40, 7
    # voet: blauwe schijf
    cil(bms["voet"], (0, 0, 0), 1.05, 0.14, 40)
    # romp: buiten- en binnenschil, randhoogte loopt op naar de achtersteven
    def rand_h(t):
        x = math.cos(t)
        return 0.88 + 0.12 * max(0, -x) ** 2 + 0.28 * max(0, x) ** 6     # achter iets hoger, boeg punt
    buiten, binnen = [], []
    for k in range(NZ + 1):
        zr = k / NZ
        sb = 0.86 + 0.14 * math.sin(zr * math.pi / 2)        # iets smaller onderaan
        rb, rbin = [], []
        for i in range(NT):
            t = 2 * math.pi * i / NT
            z = 0.14 + zr * (rand_h(t) - 0.14)
            p = romp_punt(t, zr, sb); rb.append((p.x, p.y, z))
            q = romp_punt(t, zr, sb - 0.09); rbin.append((q.x, q.y, max(0.32, z)))
        buiten.append(rb); binnen.append(rbin)
    # rode romp (onderste deel) en blauwe schubben (bovenste voorste deel) als aparte rollen
    for k in range(NZ):
        for i in range(NT):
            j = (i + 1) % NT
            t = 2 * math.pi * (i + 0.5) / NT
            rol = "schubben" if (math.cos(t) > 0.62 and 2 <= k <= NZ - 2) else "romp"     # schubben alleen op de boeg
            bm = bms[rol]
            vs = [bm.verts.new(v) for v in (buiten[k][i], buiten[k][j], buiten[k + 1][j], buiten[k + 1][i])]
            bm.faces.new(vs)
            vi = [bm.verts.new(v) for v in (binnen[k][j], binnen[k][i], binnen[k + 1][i], binnen[k + 1][j])]
            bm.faces.new(vi)
    bm = bms["romp"]                                   # bodem binnen + randkap
    vloer = [bm.verts.new((binnen[0][i][0], binnen[0][i][1], 0.32)) for i in range(NT)]
    bm.faces.new(vloer)
    # gouden rand bovenop (krullen = getande rand)
    bm = bms["goud"]
    for i in range(NT):
        j = (i + 1) % NT
        a0, a1 = Vector(buiten[-1][i]), Vector(buiten[-1][j]); b0, b1 = Vector(binnen[-1][i]), Vector(binnen[-1][j])
        h = 0.07 + 0.04 * (i % 2)
        vs = [bm.verts.new(v) for v in (a0, a1, b1, b0)]; bm.faces.new(vs)
        vs = [bm.verts.new(v) for v in (a0 + Vector((0, 0, h)), b0 + Vector((0, 0, h)), b1 + Vector((0, 0, h)), a1 + Vector((0, 0, h)))]; bm.faces.new(vs)
        vs = [bm.verts.new(v) for v in (a0, a0 + Vector((0, 0, h)), a1 + Vector((0, 0, h)), a1)]; bm.faces.new(vs)
    # blauw sierpaneel achter (achtersteven), golvende bovenkant met gouden krullen
    bm = bms["sierpaneel"]
    NP = 14
    pts_o, pts_b = [], []
    for k in range(NP + 1):
        u = k / NP
        t = math.pi + (u - 0.5) * math.radians(95)
        p = romp_punt(t, 1.0, 1.02)
        top = 1.0 + 0.24 * math.sin(u * math.pi) + 0.06 * math.sin(u * math.pi * 5)     # Siro-boot-achter.jpg: paneel net boven de rand
        pts_o.append((p.x, p.y, 0.85)); pts_b.append((p.x, p.y, top))
    for k in range(NP):
        vs = [bm.verts.new(v) for v in (pts_o[k], pts_o[k + 1], pts_b[k + 1], pts_b[k])]; bm.faces.new(vs)
        vs = [bm.verts.new(Vector(v) * Vector((0.93, 0.93, 1))) for v in (pts_o[k + 1], pts_o[k], pts_b[k], pts_b[k + 1])]; bm.faces.new(vs)
    for k in (0, NP // 2, NP):                          # gouden krullen op het paneel
        bol(bms["goud"], (pts_b[k][0] * 1.01, pts_b[k][1] * 1.01, pts_b[k][2] - 0.02), 0.07, 8)
    # mast met opgerold zeil (paraplu-vorm uit de foto) en vlaggetje
    mx = 0.1
    stam(bms["mast"], (mx, 0, 0.3), (mx, 0, 2.55), 0.04, 0.03, 6, 0.0)
    stam(bms["mast"], (mx, -0.55, 2.25), (mx, 0.55, 2.25), 0.025, 0.025, 6, 0.0)      # rondhout dwars
    for k in range(5):                                 # opgerold zeil: dikke bundel doek onder het rondhout, hangt door
        u = (k - 2) / 2.0
        v = bol(bms["zeil"], (mx + 0.02, u * 0.42, 2.12 - 0.12 * (1 - abs(u))), 0.15 - 0.03 * abs(u), 8)
        for vv in v: vv.co.z = 2.12 + (vv.co.z - 2.12) * 1.5
    v = bol(bms["zeil"], (mx + 0.03, 0.05, 1.82), 0.13, 8)                 # afhangende punt
    doos(bms["zeil"], (mx + 0.14, 0, 2.5), (0.24, 0.01, 0.12))           # vlaggetje
    stam(bms["touw"], (mx, 0, 2.5), (0.85, 0, 1.0), 0.01, 0.01, 4, 0.0)
    stam(bms["touw"], (mx, 0, 2.5), (-0.85, 0, 1.05), 0.01, 0.01, 4, 0.0)
    # bakje handelswaar achterop: houten kist met sinaasappels en flessen (Siro-fruitkistje.jpg)
    kc = romp_punt(math.pi, 1.0, 0.62); kc.z = 1.0
    doos(bms["kist"], kc, (0.3, 0.75, 0.28), 0)
    for i in range(7):
        bol(bms["fruit_oranje"], kc + Vector((random.uniform(-0.08, 0.08), -0.3 + i * 0.1, 0.18 + random.uniform(0, 0.05))), 0.07, 8)
    for s in (-0.12, 0.2):
        cil(bms["fles"], kc + Vector((0, s, 0.14)), 0.045, 0.32, 8, 0.02)
    # bankje rondom binnen (rood)
    for i in range(NT):
        j = (i + 1) % NT
        a = Vector(binnen[2][i]) * Vector((0.97, 0.97, 0)) + Vector((0, 0, 0.62)); b = Vector(binnen[2][j]) * Vector((0.97, 0.97, 0)) + Vector((0, 0, 0.62))
        a2 = a * Vector((0.72, 0.72, 1)); b2 = b * Vector((0.72, 0.72, 1))
        if math.cos(2 * math.pi * i / NT) < 0.55:
            vs = [bms["romp"].verts.new(v) for v in (a, b, b2, a2)]; bms["romp"].faces.new(vs)
    # stuurwiel in het midden (draaitafel van de teacup)
    cil(bms["goud"], (0.1, 0, 0.32), 0.07, 0.45, 8)
    cil(bms["goud"], (0.1, 0, 0.77), 0.32, 0.05, 16)
    out = []
    for rol, bm in bms.items():
        if not bm.verts: bm.free(); continue
        if rol == "romp": rol = romp_rol
        bm.transform(M)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        out.append(obj(f"SI_{naam}_{rol}", bm, rol))
    return out


def boten():
    n = 0
    for s in range(3):
        a = VOOR + math.radians(90 + 120 * s)
        c = Vector((R_SUBMID * math.cos(a), R_SUBMID * math.sin(a), Z_PLAT + 0.06))
        for b in range(3):
            ab = a + math.radians(120 * b + 40)
            boot(f"boot{n:02d}", c + Vector((1.25 * math.cos(ab), 1.25 * math.sin(ab), 0)), ab + random.uniform(-1, 1), "romp_hout" if n % 2 else "romp"); n += 1
        a2 = a + math.radians(60)
        boot(f"boot{n:02d}", (5.75 * math.cos(a2), 5.75 * math.sin(a2), Z_PLAT), a2 + math.pi / 2, "romp_hout" if n % 2 else "romp"); n += 1


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
