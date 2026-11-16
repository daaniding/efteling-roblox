"""14_planten: beplanting rond de Pagode (video fmEZsIkqsl8, Pagode-landing.jpg, luchtfoto), parkframe zoals 12_omgeving.
  bamboe  : bosjes stengels + gekruiste bladkaarten (alpha), achter de tuin en aan het eind van het laantje (video 0:28-0:37)
  niwaki  : gesnoeide dennen met wolken (video 0:20-0:26 tuin, 0:04 achter het bord, 5:55 bij het oostpad)
  haag    : hoge haag aan weerszijden van de sleuf (Pagode-landing.jpg)
  perk    : bloemenperk aan de pleinkant (oranje, Pagode-landing.jpg)
  bomen   : grote eik aan het oostpad (video 6:35-6:40), sparren langs de zuidkant van de vlonder (video 6:15-6:30),
            loofbomen rond de tribune en op het plein (Pagode-landing.jpg, luchtfoto)
Bladkaarten: twee gekruiste vlakken, dubbelzijdig, UV 0..1 (uv_vast). Gebruik: blender --background --python build/14_planten.py -- --master AR_Pagode_master.blend"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix

OWNER = "phase:14_planten"
CX, CY = 360.0, 47.5
Z_I, Z_P = 1.3, -0.38
A_SLEUF = math.degrees(math.atan2(58.5 - CY, 320.5 - CX))
rnd = random.Random(11)


def a_c(r): return 104.0 + (r - 14.2) * 0.95
def aL(r): return a_c(r) - math.degrees(0.9 / r)


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


def pt(r, a, z=0.0):
    a = math.radians(a); return Vector((CX + r * math.cos(a), CY + r * math.sin(a), z))


def buis(naam, a, b, r, rol, seg=8, r2=None):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=d.length)
    bmesh.ops.transform(bm, matrix=Matrix.Translation((a + b) / 2) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=bm.verts)
    return obj(naam, bm, rol)


def blob(naam, c, s, rol, sub=2, ruw=0.12):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    for v in bm.verts:
        k = 1 + rnd.uniform(-ruw, ruw); v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, v.co.z * s[2] * k))
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    for f in bm.faces: f.smooth = True
    return obj(naam, bm, rol)


def takken(naam, lijst, rol="spar"):
    """Platte takkaarten (PG_spar): lijst van (basis, hoek, lengte, breedte, hang). Kaart van de stam naar buiten,
    licht hangend (2 stukken), dubbelzijdig; u = langs de tak."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    for basis, hoek, L, B, hang in lijst:
        u = Vector((math.cos(hoek), math.sin(hoek), 0)); n = Vector((-u.y, u.x, 0))
        rij = []
        for q in (0.0, 0.5, 1.0):
            c = basis + u * L * q - Vector((0, 0, hang * q * q))
            rij.append((c - n * B / 2, c + n * B / 2, q))
        for i in range(2):
            a0, a1, q0 = rij[i]; b0, b1, q1 = rij[i + 1]
            hoeken = [a0, b0, b1, a1]; uvs = [(q0, 0), (q1, 0), (q1, 1), (q0, 1)]
            for volg in (lambda x: x, lambda x: x[::-1]):
                f = bm.faces.new([bm.verts.new(p) for p in volg(hoeken)])
                for l, uv in zip(f.loops, volg(uvs)): l[uvl].uv = uv
    return obj(naam, bm, rol, uv_vast=True)


def kaarten(naam, lijst, rol):
    """lijst: (midden, breedte, hoogte, draaiing, kanteling). Elk: twee gekruiste vlakken, dubbelzijdig, in een mesh."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    for c, w, h, rot, kant in lijst:
        for extra in (0.0, math.pi / 2):
            r = rot + extra; t = Vector((math.cos(r), math.sin(r), 0)); n = Vector((-t.y, t.x, 0))
            up = (Vector((0, 0, 1)) * math.cos(kant) + n * math.sin(kant))
            hoeken = [c - t * w / 2 - up * h / 2, c + t * w / 2 - up * h / 2, c + t * w / 2 + up * h / 2, c - t * w / 2 + up * h / 2]
            uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
            for volg in (lambda x: x, lambda x: x[::-1]):
                vs = [bm.verts.new(p) for p in volg(hoeken)]
                f = bm.faces.new(vs)
                for l, uv in zip(f.loops, volg(uvs)): l[uvl].uv = uv
    return obj(naam, bm, rol, uv_vast=True)


def bamboebos(naam, c, z, n=7, h=4.5):
    c = Vector(c); stengels = []
    for k in range(n):
        p = c + Vector((rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), z))
        hh = h * rnd.uniform(0.8, 1.15); top = p + Vector((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), hh))
        buis(f"{naam}_stengel{k}", p, top, rnd.uniform(0.018, 0.03), "bamboestam", 6, 0.012)
        stengels.append((p, top))
    lijst = []
    for p, top in stengels:
        for q in (0.45, 0.62, 0.8, 0.95):
            m = p + (top - p) * q
            lijst.append((m + Vector((rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), 0)), rnd.uniform(1.0, 1.4), rnd.uniform(1.2, 1.7),
                          rnd.uniform(0, 3.14), rnd.uniform(-0.15, 0.15)))
    kaarten(f"{naam}_blad", lijst, "bamboe")


def niwaki(naam, voet, h=4.2, n_wolk=6):
    """Gesnoeide den: kronkelende stam, takken met platte naaldwolken (video 0:20-0:26)."""
    voet = Vector(voet); p = voet.copy(); punten = [p.copy()]
    richting = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)).normalized()
    for k in range(5):
        q = p + Vector((0, 0, h / 5)) + richting * rnd.uniform(0.15, 0.4) * (1 if k % 2 else -0.6)
        buis(f"{naam}_stam{k}", p, q, 0.16 * (1 - k / 7), "schors", 8, 0.16 * (1 - (k + 1) / 7))
        p = q; punten.append(p.copy())
    sprays = []
    for k in range(n_wolk):
        z = h * (0.35 + 0.65 * k / max(1, n_wolk - 1))
        basis = punten[min(5, int(z / h * 5))]
        hoek = rnd.uniform(0, 6.28) if k < n_wolk - 1 else 0
        L = rnd.uniform(0.9, 1.6) * (1.0 - 0.4 * k / n_wolk) if k < n_wolk - 1 else 0
        eind = Vector((basis.x + math.cos(hoek) * L, basis.y + math.sin(hoek) * L, voet.z + z))
        if L > 0: buis(f"{naam}_tak{k}", basis, eind, 0.06, "schors", 6, 0.035)
        s = rnd.uniform(0.7, 1.05) * (1.15 - 0.4 * k / n_wolk)
        wc = eind + Vector((0, 0, 0.12))
        blob(f"{naam}_wolk{k}", wc, (s * 0.85, s * 0.8, s * 0.32), "naald", 2, 0.1)
        sprays.extend((wc + Vector((0, 0, rnd.uniform(-0.05, 0.12))), j * 0.785 + rnd.uniform(-0.3, 0.3), s * 1.15, s * 0.7, 0.08) for j in range(8))

    takken(f"{naam}_naalden", sprays)


def spar(naam, voet, h=19.0):
    """Douglasspar (video 6:15-6:30): stam, smalle donkere kern, en per krans 7 hangende takkaarten (PG_spar)."""
    voet = Vector(voet)
    buis(f"{naam}_stam", voet, voet + Vector((0, 0, h * 0.97)), 0.36, "schors", 8, 0.05)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.6, radius2=0.08, depth=h * 0.72)
    bmesh.ops.translate(bm, vec=voet + Vector((0, 0, h * 0.25 + h * 0.36)), verts=bm.verts)
    for f in bm.faces: f.smooth = True
    obj(f"{naam}_kern", bm, "naald")
    lijst = []
    kransen = 15
    for k in range(kransen):
        t = k / kransen; z = h * (0.2 + 0.78 * t)
        L = 3.8 * (1 - t) ** 0.85 + 0.5
        for j in range(7):
            lijst.append((voet + Vector((0, 0, z)), j * 0.898 + k * 0.45 + rnd.uniform(-0.2, 0.2), L * rnd.uniform(0.85, 1.1), L * 0.55, L * 0.38))
    takken(f"{naam}_takken", lijst)


def loofboom(naam, voet, h=14.0, kroon=6.0):
    """Stam + gesteltakken + kroon: donkere kernblobs (geen doorkijk) met bladkaarten erover (Pagode-landing.jpg)."""
    voet = Vector(voet); top = voet + Vector((0, 0, h * 0.45))
    buis(f"{naam}_stam", voet, top, 0.42 * h / 14, "schors", 10, 0.3 * h / 14)
    mid = voet + Vector((0, 0, h * 0.62))
    for k in range(5):
        a = k * 1.26 + rnd.uniform(-0.3, 0.3)
        eind = mid + Vector((math.cos(a) * kroon * 0.55, math.sin(a) * kroon * 0.55, rnd.uniform(-0.5, 2.0)))
        buis(f"{naam}_tak{k}", top, eind, 0.18 * h / 14, "schors", 6, 0.07)
    for k in range(6):
        a = k * 1.05 + rnd.uniform(-0.4, 0.4); rr = kroon * rnd.uniform(0.25, 0.55)
        c = mid + Vector((math.cos(a) * rr, math.sin(a) * rr, rnd.uniform(-0.6, 1.8)))
        blob(f"{naam}_kern{k}", c, (kroon * 0.3, kroon * 0.3, kroon * 0.24), "haag", 1, 0.2)
    lijst = []
    for k in range(95):
        u, v = rnd.uniform(0, 6.28), rnd.uniform(-0.35, 1.0)
        rr = kroon * (0.75 + 0.25 * rnd.random()) * math.sqrt(1 - v * v * 0.6)
        c = mid + Vector((math.cos(u) * rr, math.sin(u) * rr, v * kroon * 0.7 + 0.6))
        lijst.append((c, rnd.uniform(2.2, 3.0), rnd.uniform(2.0, 2.8), rnd.uniform(0, 3.14), rnd.uniform(-0.5, 0.5)))
    kaarten(f"{naam}_blad", lijst, "blad")


def haag(naam, r0, r1, kant, h=2.3):
    """Haag langs de sleuf: strook in het sleufframe, kant +1 noord / -1 zuid, 0.7 m breed, 1.3-2.0 m van de as."""
    a = math.radians(A_SLEUF); u = Vector((math.cos(a), math.sin(a), 0)); n = Vector((-u.y, u.x, 0)) * kant
    c0 = Vector((CX, CY, 0)) + u * r0 + n * 1.75; c1 = Vector((CX, CY, 0)) + u * r1 + n * 1.75
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=((r1 - r0), 0.75, h), verts=bm.verts)
    for v in bm.verts:
        if v.co.z > 0: v.co.y *= 0.8
    bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).x) > 1], cuts=int(r1 - r0), use_grid_fill=True)
    for v in bm.verts:
        if v.co.z > 0: v.co.z += rnd.uniform(-0.12, 0.12)
        v.co.y += rnd.uniform(-0.06, 0.06)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, "Z"), verts=bm.verts)
    z = Z_I if r0 < 13 else Z_P
    bmesh.ops.translate(bm, vec=(c0 + c1) / 2 + Vector((0, 0, Z_P + h / 2)), verts=bm.verts)
    obj(naam, bm, "haag")


def build():
    a = sys.argv[sys.argv.index("--") + 1:]
    m = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=m)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    # bamboe: achter het onderpad (eind laantje) en als wand tussen tuin en terras
    k = 0
    for aa in range(103, 140, 3):
        bamboebos(f"AR_Pagode_P_bamboe{k:02d}", pt(27.6 + rnd.uniform(-0.2, 0.4), aa), Z_P); k += 1
    for r in (19.5, 21.5, 23.5, 25.5):
        bamboebos(f"AR_Pagode_P_bamboe{k:02d}", pt(r, aL(r) - math.degrees(5.6 / r)), Z_P - 0.1, 8, 4.0); k += 1
    bamboebos(f"AR_Pagode_P_bamboe{k:02d}", pt(14.5, 95.5, Z_P + 0.5), 0.0, 6, 1.6)     # in de pot naast het bord
    # niwaki: tuin (2), achter het bord, bij het oostpad
    niwaki("AR_Pagode_P_niwaki0", pt(20.0, aL(20.0) - math.degrees(2.6 / 20), Z_P - 0.1), 4.6, 7)
    niwaki("AR_Pagode_P_niwaki1", pt(23.8, aL(23.8) - math.degrees(2.0 / 23.8), Z_P - 0.1), 3.4, 5)
    niwaki("AR_Pagode_P_niwaki2", pt(18.0, aL(18.0) - math.degrees(3.4 / 18), Z_P - 0.1), 3.8, 6)
    niwaki("AR_Pagode_P_niwaki3", pt(12.4, 24.0, Z_P + 0.03), 3.6, 6)
    niwaki("AR_Pagode_P_niwaki4", pt(12.4, 44.0, Z_P + 0.03), 2.8, 5)
    # stenen in de tuin
    for j in range(10):
        r = rnd.uniform(16.5, 25); aa = aL(r) - math.degrees(rnd.uniform(0.8, 4.5) / r)
        blob(f"AR_Pagode_P_tuinsteen{j}", pt(r, aa, Z_P + 0.05), (rnd.uniform(0.25, 0.5), rnd.uniform(0.2, 0.4), rnd.uniform(0.15, 0.3)), "breuksteen", 1, 0.25)
    # haag langs de sleuf (beide kanten)
    haag("AR_Pagode_P_haag_noord", 11.6, 30.0, -1)
    haag("AR_Pagode_P_haag_zuid", 11.6, 30.0, 1)
    # bloemenperk: bloementapijt + losse pollen (oranje, Pagode-landing.jpg)
    bm = bmesh.new(); seg = 24; rings = []
    for i in range(seg + 1):
        aa = math.radians(56 + (99 - 56) * i / seg)
        rings.append([bm.verts.new(pt(r, math.degrees(aa), z)) for r, z in ((10.8, 1.38), (13.6, 1.38), (13.6, 1.62), (10.8, 1.62))])
    for i in range(seg):
        for q in range(4): bm.faces.new((rings[i][q], rings[i][(q + 1) % 4], rings[i + 1][(q + 1) % 4], rings[i + 1][q]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj("AR_Pagode_P_perk_tapijt", bm, "bloem")
    for j in range(26):
        blob(f"AR_Pagode_P_pol{j}", pt(rnd.uniform(11.2, 13.3), rnd.uniform(58, 97), 1.62), (rnd.uniform(0.3, 0.45),) * 2 + (0.28,), "bloem", 1, 0.2)
    # bomen
    loofboom("AR_Pagode_P_eik", pt(18.5, 18.0, Z_P), 17.0, 7.5)                 # grote eik aan het oostpad (video 6:35-6:40)
    for j, (r, aa, h) in enumerate(((12.6, -100, 21), (14.2, -76, 19), (13.2, -124, 22), (16.0, -56, 18), (17.5, -145, 20), (24, 172, 19), (31, 168, 21))):
        spar(f"AR_Pagode_P_spar{j}", pt(r, aa, Z_I if r < 15 else Z_P), h)
    for j, (r, aa, h, kr) in enumerate(((29.5, 120, 15, 6.5), (29.0, 140, 16, 7.0), (28.5, 155, 14, 6.0), (24.5, 64, 9, 4.0), (23.0, 36, 9, 4.0))):
        loofboom(f"AR_Pagode_P_boom{j}", pt(r, aa, Z_P), h, kr)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=m)
    print("[14_planten] %d objecten" % len([o for o in bpy.data.objects if o.get("owner") == OWNER]))


build()
