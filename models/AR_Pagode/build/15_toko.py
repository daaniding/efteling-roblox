"""15_toko: Toko Pagode (kiosk) met keuken, statafels en het terras met parasols, naast de Pagode.
Bronnen: video fmEZsIkqsl8 1:02 (ref/video_toko_102.jpg), 0:04-0:07 (terras rechts van het bord), luchtfoto PDOK
(kiosk achthoek, midden park (380.6, 79.3), ~12 m breed, een zijde naar de Pagode; keuken erachter; 3 parasols ~3.5 m),
Pagode-landing.jpg (rieten stoelen, ronde tafels). Lemma: "pleintje met terras voor het naastgelegen etablissement Toko Pagode".
Vorm (video): laag grijs schilddak, brede creme dakrand met rode zigzag, bolle lampjes onder de rand, rode palen met groene
kapitelen, verkoopramen met creme toonbank, groene panelen met witte bloem, en op het dak een witte klokkoepel met gouden band
en gouden spits. Parkframe en collectie zoals 12_omgeving (OMGEVING).
Gebruik: blender --background --python build/15_toko.py -- --master AR_Pagode_master.blend"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix

OWNER = "phase:15_toko"
CX, CY = 360.0, 47.5
Z_P = -0.38
TK = Vector((380.6, 79.3, Z_P))          # midden kiosk
A_VOOR = -106.0                           # richting van de zijde naar de Pagode (graden)
R_DAK = 6.1                               # buitenstraal dakrand (hoekpunt)
R_PAAL = 5.3
R_KERN = 4.4
rnd = random.Random(5)


def col():
    c = bpy.data.collections.get("OMGEVING")
    if not c:
        c = bpy.data.collections.new("OMGEVING"); bpy.context.scene.collection.children.link(c)
    return c


def obj(naam, bm, rol, uv_vast=False):
    me = bpy.data.meshes.new(naam); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(naam, me); col().objects.link(o); o["rol"] = rol; o["owner"] = OWNER
    if uv_vast: o["uv_vast"] = True
    return o


def doos(naam, c, s, rol, rot=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=s, verts=bm.verts)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    return obj(naam, bm, rol)


def buis(naam, a, b, r, rol, seg=8, r2=None):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=d.length)
    bmesh.ops.transform(bm, matrix=Matrix.Translation((a + b) / 2) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=bm.verts)
    return obj(naam, bm, rol)


def bol(naam, c, r, rol):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r); bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    for f in bm.faces: f.smooth = True
    return obj(naam, bm, rol)


def hoek(k, r, z=0.0):
    """Hoekpunt k van de achthoek (zijde 0 kijkt naar A_VOOR)."""
    a = math.radians(A_VOOR + 22.5 + 45 * k); return Vector((TK.x + r * math.cos(a), TK.y + r * math.sin(a), TK.z + z))


def lathe(naam, profiel, rol, seg=32, midden=None):
    """Draaivorm rond de verticale as door midden; profiel = [(r, z)] van onder naar boven."""
    midden = midden or TK
    bm = bmesh.new(); rings = []
    for r, z in profiel:
        rings.append([bm.verts.new((midden.x + r * math.cos(2 * math.pi * i / seg), midden.y + r * math.sin(2 * math.pi * i / seg), midden.z + z)) for i in range(seg)])
    for j in range(len(rings) - 1):
        for i in range(seg):
            bm.faces.new((rings[j][i], rings[j][(i + 1) % seg], rings[j + 1][(i + 1) % seg], rings[j + 1][i]))
    if profiel[0][0] > 0: bm.faces.new(rings[0][::-1])
    for f in bm.faces: f.smooth = True
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(naam, bm, rol)


def band(naam, r, z0, z1, rol):
    """Achthoekige band (dakrand) met UV langs de omtrek (2 m per tegel), dubbelzijdig dicht."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap"); s = 0.0
    for k in range(8):
        a, b = hoek(k, r), hoek(k + 1, r); L = (b - a).length
        for buiten in (True, False):
            q = [a + Vector((0, 0, z0)), b + Vector((0, 0, z0)), b + Vector((0, 0, z1)), a + Vector((0, 0, z1))]
            uvs = [(s / 2, 0), ((s + L) / 2, 0), ((s + L) / 2, 1), (s / 2, 1)]
            if not buiten: q, uvs = q[::-1], uvs[::-1]
            f = bm.faces.new([bm.verts.new(p) for p in q])
            for l, uv in zip(f.loops, uvs): l[uvl].uv = (uv[0] - math.floor(s / 2), uv[1])
        s += L
    return obj(naam, bm, rol, uv_vast=True)


def prisma8(naam, r0, z0, r1, z1, rol):
    """Afgeknotte achthoek (dak, sokkel)."""
    bm = bmesh.new()
    o = [bm.verts.new(hoek(k, r0, z0)) for k in range(8)]; b = [bm.verts.new(hoek(k, r1, z1)) for k in range(8)]
    for k in range(8): bm.faces.new((o[k], o[(k + 1) % 8], b[(k + 1) % 8], b[k]))
    bm.faces.new(o[::-1]); bm.faces.new(b)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(naam, bm, rol)


def kiosk():
    prisma8("AR_Pagode_T_sokkel", R_DAK - 0.2, -0.3, R_DAK - 0.2, 0.12, "klinker")
    # kern met verkoopramen per zijde: onderpaneel (groen met bloem), toonbank, raam, rode bovenband
    for k in range(8):
        a, b = hoek(k, R_KERN), hoek(k + 1, R_KERN); m = (a + b) / 2; t = (b - a); L = t.length; rot = math.atan2(t.y, t.x)
        n = Vector((math.cos(rot - math.pi / 2), math.sin(rot - math.pi / 2), 0))       # naar buiten
        if (m - TK).dot(n) < 0: n = -n
        voor = k in (0, 1, 7)
        doos(f"AR_Pagode_T_paneel{k}", m + Vector((0, 0, 0.62)), (L, 0.14, 1.0), "tokopaneel" if voor else "rood", rot)
        if voor:
            doos(f"AR_Pagode_T_toonbank{k}", m + n * 0.2 + Vector((0, 0, 1.15)), (L - 0.3, 0.55, 0.06), "wit", rot)
            doos(f"AR_Pagode_T_raam{k}", m - n * 0.05 + Vector((0, 0, 1.78)), (L - 0.2, 0.06, 1.2), "glas", rot)
            doos(f"AR_Pagode_T_binnen{k}", m - n * 0.6 + Vector((0, 0, 1.75)), (L - 0.4, 0.1, 1.3), "onderkant", rot)
        else:
            doos(f"AR_Pagode_T_wand{k}", m + Vector((0, 0, 1.75)), (L, 0.16, 1.3), "rood", rot)
        doos(f"AR_Pagode_T_bovenband{k}", m + Vector((0, 0, 2.55)), (L, 0.18, 0.3), "rood", rot)
    # palen (rood) met groene kapitelen, op de hoeken van de luifel
    for k in range(8):
        p = hoek(k, R_PAAL)
        doos(f"AR_Pagode_T_paal{k}", p + Vector((0, 0, 1.45)), (0.18, 0.18, 2.9), "rood")
        buis(f"AR_Pagode_T_kapiteel{k}", p + Vector((0, 0, 2.55)), p + Vector((0, 0, 2.9)), 0.08, "groen", 8, 0.24)
        doos(f"AR_Pagode_T_voet{k}", p + Vector((0, 0, 0.2)), (0.26, 0.26, 0.4), "groen")
    # luifelplafond, dakrand (creme met rode zigzag), lampjes onder de rand
    prisma8("AR_Pagode_T_plafond", R_DAK, 2.88, R_KERN - 0.1, 2.9, "wit")
    band("AR_Pagode_T_dakrand", R_DAK, 2.9, 3.5, "tokorand")
    for k in range(8):
        for q in (0.3, 0.7):
            p = hoek(k, R_DAK - 0.35) * (1 - q) + hoek(k + 1, R_DAK - 0.35) * q
            buis(f"AR_Pagode_T_lampsnoer{k}{q}", p + Vector((0, 0, 2.62)), p + Vector((0, 0, 2.9)), 0.01, "hek", 4)
            bol(f"AR_Pagode_T_lampje{k}{q}", p + Vector((0, 0, 2.55)), 0.11, "lamp")
    # laag grijs schilddak
    prisma8("AR_Pagode_T_dak", R_DAK + 0.05, 3.45, 2.35, 4.45, "dak_toko")
    # klokkoepel (wit) met gouden band en spits (video 1:02)
    prisma8("AR_Pagode_T_koepelvoet", 2.4, 4.4, 2.3, 4.8, "wit_glans")
    lathe("AR_Pagode_T_koepel", [(2.45, 4.78), (2.38, 4.95), (2.1, 5.25), (1.98, 5.7), (1.82, 6.3), (1.5, 6.95), (1.05, 7.55),
                                 (0.6, 8.0), (0.3, 8.3), (0.12, 8.45), (0.0, 8.5)], "wit_glans")
    lathe("AR_Pagode_T_koepelband", [(2.12, 5.2), (2.14, 5.3), (2.06, 5.36)], "goud")
    for i, (r0, z0, r1, z1) in enumerate(((0.16, 8.4, 0.12, 8.8), (0.2, 8.8, 0.05, 9.2), (0.11, 9.2, 0.02, 9.9))):
        buis(f"AR_Pagode_T_spits{i}", TK + Vector((0, 0, z0)), TK + Vector((0, 0, z1)), r0, "goud", 10, r1)
    bol("AR_Pagode_T_spitsbol", TK + Vector((0, 0, 9.0)), 0.16, "goud")


def keuken():
    """Keuken/achterbouw (luchtfoto: grijs dak achter de kiosk, gedraaid ~ -33 graden)."""
    c = Vector((387.5, 85.8, Z_P)); rot = math.radians(-33)
    doos("AR_Pagode_T_keuken", c + Vector((0, 0, 1.6)), (9.0, 6.0, 3.2), "rood", rot)
    doos("AR_Pagode_T_keukenband", c + Vector((0, 0, 3.05)), (9.1, 6.1, 0.3), "groen", rot)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=6.2, radius2=1.4, depth=1.4)
    bmesh.ops.scale(bm, vec=(1.0, 0.68, 1), verts=bm.verts)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot + math.pi / 4 * 0, 3, "Z"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=c + Vector((0, 0, 3.2 + 0.7)), verts=bm.verts)
    obj("AR_Pagode_T_keukendak", bm, "dak_toko")


def statafel(naam, p):
    buis(f"{naam}_poot", p, p + Vector((0, 0, 1.05)), 0.05, "groen", 8)
    buis(f"{naam}_voet", p, p + Vector((0, 0, 0.04)), 0.28, "groen", 12)
    buis(f"{naam}_blad", p + Vector((0, 0, 1.05)), p + Vector((0, 0, 1.09)), 0.38, "rood", 16)


def parasol(naam, p, r=1.75):
    buis(f"{naam}_stok", p, p + Vector((0, 0, 2.55)), 0.035, "wit", 8)
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap"); n = 8
    tp = p + Vector((0, 0, 2.75))
    rp = [p + Vector((r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), 2.3)) for i in range(n)]
    for i in range(n):
        for volg in (False, True):                  # voor- en achterkant met eigen hoekpunten
            vs = [rp[i], rp[(i + 1) % n], tp]; uvs = [(i / n, 0), ((i + 1) / n, 0), ((i + 0.5) / n, 1)]
            if volg: vs, uvs = vs[::-1], uvs[::-1]
            f = bm.faces.new([bm.verts.new(v) for v in vs])
            for l, uv in zip(f.loops, uvs): l[uvl].uv = uv
    obj(f"{naam}_doek", bm, "parasol", uv_vast=True)
    # tafel met 4 rieten stoelen (Pagode-landing.jpg)
    buis(f"{naam}_tafelpoot", p, p + Vector((0, 0, 0.72)), 0.04, "hek", 8)
    buis(f"{naam}_tafel", p + Vector((0, 0, 0.72)), p + Vector((0, 0, 0.75)), 0.42, "rotan", 16)
    for k in range(4):
        a = k * math.pi / 2 + rnd.uniform(-0.3, 0.3); q = p + Vector((math.cos(a) * 0.75, math.sin(a) * 0.75, 0))
        buis(f"{naam}_stoel{k}_zit", q, q + Vector((0, 0, 0.46)), 0.24, "rotan", 10, 0.26)
        rug = q + Vector((math.cos(a) * 0.2, math.sin(a) * 0.2, 0))
        doos(f"{naam}_stoel{k}_rug", rug + Vector((0, 0, 0.72)), (0.08, 0.5, 0.52), "rotan", a)


def build():
    a = sys.argv[sys.argv.index("--") + 1:]
    m = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=m)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    kiosk(); keuken()
    # statafels voor de kiosk (video 1:02)
    for k, (aa, rr) in enumerate(((-140, 7.2), (-118, 7.4), (-92, 7.2), (-68, 7.4))):
        statafel(f"AR_Pagode_T_statafel{k}", TK + Vector((rr * math.cos(math.radians(aa)), rr * math.sin(math.radians(aa)), 0)))
    # bloempotten met struikje bij de toonbank
    for k, aa in enumerate((-150, -62)):
        p = TK + Vector((7.0 * math.cos(math.radians(aa)), 7.0 * math.sin(math.radians(aa)), 0))
        buis(f"AR_Pagode_T_pot{k}", p, p + Vector((0, 0, 0.6)), 0.32, "rood", 12, 0.25)
        bol(f"AR_Pagode_T_struik{k}", p + Vector((0, 0, 1.0)), 0.5, "haag")
    # terras: 3 parasols met tafels en stoelen (luchtfoto)
    for k, (x, y) in enumerate(((365.8, 79.0), (370.0, 73.8), (372.5, 68.9))):   # derde parasol naar het terras (stond op het Pagodeplein bij de spawn)
        parasol(f"AR_Pagode_T_parasol{k}", Vector((x, y, Z_P)))
    # bestrating terras + kiosk (klinkers), in stukken (kleine UV's)
    for k in range(4):                          # 42..88 graden: blijft van het Gondolettawater af
        a0 = 42 + 11.5 * k
        bm = bmesh.new(); seg = 6; rings = []
        for i in range(seg + 1):
            ang = math.radians(a0 + 11.5 * i / seg)
            rings.append([bm.verts.new((CX + r * math.cos(ang), CY + r * math.sin(ang), z)) for r, z in ((24.0, -0.9), (41.0, -0.9), (41.0, Z_P), (24.0, Z_P))])
        for i in range(seg):
            for q in range(4): bm.faces.new((rings[i][q], rings[i][(q + 1) % 4], rings[i + 1][(q + 1) % 4], rings[i + 1][q]))
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        obj(f"AR_Pagode_T_terras{k}", bm, "klinker")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=m)
    print("[15_toko] %d objecten" % len([o for o in bpy.data.objects if o.get("owner") == OWNER]))


build()
