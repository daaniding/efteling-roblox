"""16_gondoletta: Gondoletta-oever naast de Pagode: rond havenbekken met platform, witte vakwerkloopbrug, rood-witte
balustrades, uitstapsteiger met wit hokje, Gondolettabootjes, paden (asfalt) langs het water, eilandjes en bomen rondom.
Bronnen: video fmEZsIkqsl8 (vanuit de tempel 4:10-4:15 en 5:05-5:10: rond bekken, vakwerkbrug, rood-witte hekken, steiger met
hokje, witte bootjes met dak; 6:39-6:42 vanaf het pad), luchtfoto PDOK (bekken midden (397, 52.5), kade r 14.5, platform
r 8.7, brug (385.6, 62) -> (392.8, 55.6), steiger (408-410.5, 54.5-61) + vlonder (403.5-411, 61-66), boten, eilanden).
Op de luchtfoto staat nog een witte tentkap op het platform; in de (nieuwere) video is die weg: video gaat voor.
Water zelf = Roblox-terrein (roblox/maak_water.py -> gondoletta_water.luau), waterpeil NAP 9.25.
Gebruik: blender --background --python build/16_gondoletta.py -- --master AR_Pagode_master.blend"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix

HIER = os.path.dirname(os.path.abspath(__file__))
# hulpfuncties uit 14_planten (bomen, kaarten) zonder diens build() te draaien
NS = {"__name__": "planten14", "__file__": os.path.join(HIER, "14_planten.py")}
bron = open(os.path.join(HIER, "14_planten.py")).read().rsplit("\nbuild()", 1)[0]
exec(compile(bron, "14_planten.py", "exec"), NS)
OWNER = "phase:16_gondoletta"; NS["OWNER"] = OWNER
obj, buis, blob, kaarten, loofboom, spar = NS["obj"], NS["buis"], NS["blob"], NS["kaarten"], NS["loofboom"], NS["spar"]
rnd = random.Random(16); NS["rnd"] = rnd

Z_P = -0.38                         # paden (NAP 9.62)
Z_W = -0.75                         # waterpeil NAP 9.25
BK = Vector((397.0, 52.5, 0))      # midden havenbekken
R_PLAT, R_KADE = 8.7, 14.5


def doos(naam, c, s, rol, rot=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=s, verts=bm.verts)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    return obj(naam, bm, rol)


def ring(naam, c, r0, r1, z0, z1, a0, a1, rol, seg=None):
    seg = seg or max(6, int(abs(a1 - a0) / 4))
    bm = bmesh.new(); rings = []
    for i in range(seg + 1):
        a = math.radians(a0 + (a1 - a0) * i / seg)
        rings.append([bm.verts.new((c.x + r * math.cos(a), c.y + r * math.sin(a), z)) for r, z in ((r0, z0), (r1, z0), (r1, z1), (r0, z1))])
    for i in range(seg):
        for k in range(4): bm.faces.new((rings[i][k], rings[i][(k + 1) % 4], rings[i + 1][(k + 1) % 4], rings[i + 1][k]))
    if abs(a1 - a0) < 359.9: bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(naam, bm, rol)


def strook(naam, pts, breed, z_top, z_bot, rol):
    """Pad als strook langs een lijn (park x, y), breedte in m."""
    bm = bmesh.new(); rings = []
    for i, (x, y) in enumerate(pts):
        a = Vector(pts[max(0, i - 1)]); b = Vector(pts[min(len(pts) - 1, i + 1)]); d = (b - a).normalized(); n = Vector((-d.y, d.x))
        rings.append([bm.verts.new((x + n.x * s * breed / 2, y + n.y * s * breed / 2, z)) for s, z in ((-1, z_bot), (1, z_bot), (1, z_top), (-1, z_top))])
    for i in range(len(rings) - 1):
        for k in range(4): bm.faces.new((rings[i][k], rings[i][(k + 1) % 4], rings[i + 1][(k + 1) % 4], rings[i + 1][k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(naam, bm, rol)


def roodwit_hek(naam, pts, z, h=1.0):
    """Rood-witte balustrade (video 4:10, 6:41): rode palen met witte dop om de 2 m, rode boven- en onderregel, witte planken."""
    for k in range(len(pts) - 1):
        a, b = Vector((*pts[k], z)), Vector((*pts[k + 1], z)); d = b - a; L = d.length
        if L < 0.1: continue
        rot = math.atan2(d.y, d.x); n = max(1, int(L / 2.0))
        for i in range(n + (1 if k == len(pts) - 2 else 0)):
            p = a + d * (i / n)
            doos(f"{naam}_{k:02d}_paal{i}", p + Vector((0, 0, (h + 0.1) / 2)), (0.12, 0.12, h + 0.1), "rood_hek", rot)
            doos(f"{naam}_{k:02d}_dop{i}", p + Vector((0, 0, h + 0.13)), (0.16, 0.16, 0.06), "wit", rot)
        m = (a + b) / 2
        doos(f"{naam}_{k:02d}_plank", m + Vector((0, 0, h * 0.55)), (L, 0.04, h * 0.62), "wit", rot)
        for nm, zz in (("boven", h - 0.02), ("onder", 0.18)):
            doos(f"{naam}_{k:02d}_{nm}", m + Vector((0, 0, zz)), (L, 0.07, 0.07), "rood_hek", rot)


def boog(c, r, a0, a1, stap=2.0):
    n = max(1, int(abs(math.radians(a1 - a0)) * r / stap))
    return [(c.x + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c.y + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def vakwerkbrug(naam, a, b, breed=2.2):
    """Witte vakwerkloopbrug naar het platform (video 4:10): licht gebogen dek, vakwerkzijkanten, bogen erover."""
    a, b = Vector(a), Vector(b); d = (b - a); L = d.length; u = d.normalized(); n = Vector((-u.y, u.x, 0)); rot = math.atan2(u.y, u.x)
    N = 10
    def zdek(t): return Z_P + 0.35 * math.sin(math.pi * t)
    for i in range(N):
        t0, t1 = i / N, (i + 1) / N; p0, p1 = a + d * t0, a + d * t1
        z0, z1 = zdek(t0), zdek(t1)
        doos(f"{naam}_dek{i}", (p0 + p1) / 2 + Vector((0, 0, (z0 + z1) / 2 - 0.08)), (L / N + 0.02, breed, 0.16), "vlonder", rot)
        for s in (-1, 1):
            q0 = p0 + n * s * breed / 2; q1 = p1 + n * s * breed / 2
            buis(f"{naam}_ligger{i}{s}", q0 + Vector((0, 0, z0)), q1 + Vector((0, 0, z1)), 0.05, "wit", 6)
            buis(f"{naam}_leuning{i}{s}", q0 + Vector((0, 0, z0 + 1.1)), q1 + Vector((0, 0, z1 + 1.1)), 0.04, "wit", 6)
            buis(f"{naam}_diag{i}{s}", q0 + Vector((0, 0, z0 + (1.1 if i % 2 else 0))), q1 + Vector((0, 0, z1 + (0 if i % 2 else 1.1))), 0.025, "wit", 4)
            buis(f"{naam}_stijl{i}{s}", q0 + Vector((0, 0, z0)), q0 + Vector((0, 0, z0 + 2.3)), 0.035, "wit", 6)
        # boog over het pad
        pts = []
        for k in range(7):
            f = k / 6; ang = math.pi * f
            pts.append(p0 + n * math.cos(ang) * breed / 2 + Vector((0, 0, z0 + 2.3 + math.sin(ang) * 0.6)))
        for k in range(6):
            buis(f"{naam}_boog{i}_{k}", pts[k], pts[k + 1], 0.03, "wit", 4)
    for s in (-1, 1):
        buis(f"{naam}_nok{s}", a + n * s * 0.5 + Vector((0, 0, Z_P + 2.85)), b + n * s * 0.5 + Vector((0, 0, Z_P + 2.85)), 0.03, "wit", 4)


def hokje(naam, p, rot):
    """Wit hokje op de steiger (video 5:05): 2 x 2.4 m, rode daklijst."""
    p = Vector(p)
    doos(f"{naam}_wand", p + Vector((0, 0, 1.15)), (2.0, 2.4, 2.3), "wit", rot)
    doos(f"{naam}_raam", p + Vector((0, 0, 1.45)) + Vector((math.cos(rot), math.sin(rot), 0)) * 1.01, (0.04, 1.6, 0.8), "glas", rot)
    doos(f"{naam}_dak", p + Vector((0, 0, 2.38)), (2.3, 2.7, 0.16), "rood_hek", rot)


def bootje(naam, p, rich):
    """Gondolettabootje (video 3:30-5:10, luchtfoto ~4.4 x 2.0 m): witte romp, plat wit dak op 4 staanders, bankjes."""
    p = Vector((p[0], p[1], Z_W)); rot = math.radians(rich)
    u = Vector((math.cos(rot), math.sin(rot), 0)); n = Vector((-u.y, u.x, 0))
    bm = bmesh.new()
    ond = []; bov = []
    for k in range(12):                       # spitse achthoekige romp in bovenaanzicht
        t = 2 * math.pi * k / 12; x, y = math.cos(t) * 2.2, math.sin(t) * 0.95
        if abs(x) > 1.5: y *= 0.6
        ond.append(bm.verts.new(p + u * x * 0.92 + n * y * 0.85 + Vector((0, 0, -0.25))))
        bov.append(bm.verts.new(p + u * x + n * y + Vector((0, 0, 0.35))))
    for k in range(12): bm.faces.new((ond[k], ond[(k + 1) % 12], bov[(k + 1) % 12], bov[k]))
    bm.faces.new(ond[::-1]); bm.faces.new(bov); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj(f"{naam}_romp", bm, "wit_glans")
    for sx in (-1, 1):
        for sy in (-1, 1):
            q = p + u * sx * 1.25 + n * sy * 0.7
            buis(f"{naam}_staander{sx}{sy}", q + Vector((0, 0, 0.35)), q + Vector((0, 0, 1.75)), 0.03, "wit", 6)
    doos(f"{naam}_dak", p + Vector((0, 0, 1.8)), (3.0, 1.75, 0.08), "wit", rot)
    for k in (-0.6, 0.0, 0.6):
        doos(f"{naam}_bank{k}", p + u * k + Vector((0, 0, 0.55)), (0.3, 1.5, 0.08), "rotan", rot)


def wilg(naam, voet, h=10.0, kroon=5.5):
    """Treurwilg (video 3:05, 6:41): stam, opgaande takken, hangende slierten als verticale kaarten (PG_wilg)."""
    voet = Vector(voet); top = voet + Vector((0, 0, h * 0.42))
    buis(f"{naam}_stam", voet, top, 0.38, "schors", 10, 0.26)
    for k in range(6):
        a = k * 1.05 + rnd.uniform(-0.3, 0.3)
        eind = top + Vector((math.cos(a) * kroon * 0.55, math.sin(a) * kroon * 0.55, h * 0.45))
        buis(f"{naam}_tak{k}", top, eind, 0.14, "schors", 6, 0.05)
    lijst = []
    for k in range(60):
        a = rnd.uniform(0, 6.28); rr = kroon * math.sqrt(rnd.uniform(0.15, 1.0))
        ztop = h * (0.95 - 0.35 * (rr / kroon) ** 2)
        hh = rnd.uniform(3.5, 5.5) * (0.6 + 0.4 * rr / kroon)
        c = voet + Vector((math.cos(a) * rr, math.sin(a) * rr, ztop - hh / 2))
        lijst.append((c, rnd.uniform(1.6, 2.4), hh, a + math.pi / 2, 0.0))
    kaarten(f"{naam}_slierten", lijst, "wilg")


def xw(y):
    """Westoever van het meer (luchtfoto)."""
    pts = [(-20, 386.0), (-10, 388.6), (0, 387.0), (10, 388.2), (20, 390.0), (30, 390.7), (40, 389.3), (45, 388.5)]
    for (y0, x0), (y1, x1) in zip(pts, pts[1:]):
        if y0 <= y <= y1: return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    return pts[0][1] if y < -20 else pts[-1][1]


def build():
    a = sys.argv[sys.argv.index("--") + 1:]
    m = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=m)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    # havenbekken: kademuur (ring), platform met rand, bodem onder water komt van het terrein
    ring("AR_Pagode_G_kade", BK, R_KADE, R_KADE + 0.6, Z_W - 1.0, Z_P + 0.02, 0, 360, "beton_licht", seg=96)
    ring("AR_Pagode_G_platform", BK, 0, R_PLAT, Z_W - 1.0, Z_P + 0.1, 0, 360, "beton_licht", seg=96)
    ring("AR_Pagode_G_platformrand", BK, R_PLAT - 0.25, R_PLAT + 0.05, Z_P + 0.1, Z_P + 0.22, 0, 360, "wit", seg=96)
    # rood-witte balustrade rond de noord-/westkant van het bekken (opening bij de brug ~140 graden) en langs de platformrand
    roodwit_hek("AR_Pagode_G_hek_bekken0", boog(BK, R_KADE + 0.3, 20, 126), Z_P)
    roodwit_hek("AR_Pagode_G_hek_bekken1", boog(BK, R_KADE + 0.3, 150, 250), Z_P)
    roodwit_hek("AR_Pagode_G_hek_platform", boog(BK, R_PLAT - 0.1, 155, 480), Z_P + 0.1)
    # vakwerkloopbrug van het pad naar het platform
    vakwerkbrug("AR_Pagode_G_brug", (385.6, 62.0, 0), (392.8, 55.6, 0))
    # uitstapsteiger + vlonder met hokje (oostkant)
    doos("AR_Pagode_G_vlonder", Vector((407.25, 63.5, Z_P - 0.08)), (7.5, 5.0, 0.2), "vlonder")
    doos("AR_Pagode_G_steiger", Vector((409.25, 57.75, Z_W + 0.45)), (2.5, 6.5, 0.18), "vlonder")
    for k, (x, y) in enumerate(((404, 61.2), (411, 61.2), (408.1, 54.8), (410.4, 54.8), (404, 65.8), (411, 65.8))):
        buis(f"AR_Pagode_G_paal{k}", (x, y, Z_W - 1.2), (x, y, Z_P - 0.1), 0.12, "schors", 8)
    hokje("AR_Pagode_G_hokje", (405.4, 64.4, Z_P + 0.02), math.radians(-90))
    roodwit_hek("AR_Pagode_G_hek_vlonder", [(403.6, 61.1), (407.9, 61.1)], Z_P + 0.02)
    roodwit_hek("AR_Pagode_G_hek_steiger", [(410.6, 61.0), (410.6, 55.0)], Z_W + 0.54)
    # paden langs het water (grijs asfalt, landing-foto): westoever en noordoever
    west = [(xw(y) - 3.2, y) for y in range(-20, 47, 3)] + [(383.0, 52.0), (382.5, 60.0)]
    strook("AR_Pagode_G_pad_west", west, 5.0, Z_P + 0.02, -0.95, "asfalt")
    noord = [(383.0, 66.5), (392.0, 69.5), (402.0, 70.5), (412.0, 70.0), (420.0, 73.0), (430.0, 77.0), (440.0, 79.0)]
    strook("AR_Pagode_G_pad_noord", noord, 6.0, Z_P + 0.02, -0.95, "asfalt")
    roodwit_hek("AR_Pagode_G_hek_west", [(xw(y) - 0.45, y) for y in range(-18, 41, 4)], Z_P + 0.02)
    roodwit_hek("AR_Pagode_G_hek_noord", [(412.0, 67.6), (420.0, 70.4), (430.0, 74.2)], Z_P + 0.02)
    # Gondolettabootjes (luchtfoto-plekken; een aan de steiger)
    for k, (x, y, r) in enumerate(((409.3, 43.6, 95), (417.9, 39.6, 80), (397.9, 26.8, 100), (423.6, 60.0, 70), (405.4, 5.7, 115),
                                    (412.4, 57.5, 90), (398.6, 63.6, 0), (387.9, -12.0, 160))):
        bootje(f"AR_Pagode_G_boot{k}", (x, y), r)
    # eilandjes: rand van stenen + bomen (grond = terrein)
    for k, (cx, cy, ax, ay) in enumerate(((414.3, 45.0, 2.4, 4.4), (397.5, 7.5, 2.6, 4.8))):
        for j in range(14):
            t = 2 * math.pi * j / 14
            blob(f"AR_Pagode_G_eilandsteen{k}_{j}", Vector((cx + math.cos(t) * ax, cy + math.sin(t) * ay, Z_W + 0.1)), (0.45, 0.35, 0.3), "breuksteen", 1, 0.25)
    loofboom("AR_Pagode_G_eilandboom0", Vector((414.3, 46.0, Z_P)), 9.0, 3.5)
    wilg("AR_Pagode_G_eilandwilg", Vector((397.8, 7.0, Z_P)), 9.0, 4.5)
    # treurwilgen langs het water (video: geelgroen)
    for k, (x, y, h) in enumerate(((388.0, -16.0, 11), (386.5, 18.0, 10), (424.0, 66.0, 11), (436.0, 71.0, 10), (384.0, 34.0, 9))):
        wilg(f"AR_Pagode_G_wilg{k}", Vector((x, y, Z_P)), h, h * 0.52)
    # bomenrand: oostoever (strook bomen), noord achter de Toko en het pad, west
    for k, (x, y, h, kr) in enumerate(((428.5, 12.0, 16, 6.5), (431.0, 26.0, 18, 7.5), (428.0, 40.0, 15, 6.0), (433.0, 52.0, 17, 7.0),
                                        (372.0, 99.0, 16, 6.5), (386.0, 101.0, 18, 7.0), (400.0, 96.0, 15, 6.0), (414.0, 92.0, 16, 6.5),
                                        (358.0, 104.0, 17, 7.0), (344.0, 98.0, 15, 6.0), (426.0, 86.0, 14, 5.5), (378.0, 4.0, 15, 6.0),
                                        (377.5, 26.0, 14, 5.5), (379.0, -14.0, 16, 6.5))):
        loofboom(f"AR_Pagode_G_boom{k}", Vector((x, y, Z_P)), h, kr)
    for k, (x, y, h) in enumerate(((436.0, 33.0, 21), (435.0, 18.0, 19), (393.0, 106.0, 22), (365.0, 92.0, 20), (430.0, 95.0, 19))):
        spar(f"AR_Pagode_G_spar{k}", Vector((x, y, Z_P)), h)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=m)
    print("[16_gondoletta] %d objecten" % len([o for o in bpy.data.objects if o.get("owner") == OWNER]))


build()
