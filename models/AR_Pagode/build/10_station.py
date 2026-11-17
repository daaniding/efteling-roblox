"""10_station: station van de Pagode in PARKcoordinaten (meter, x oost, y noord, z = NAP - 10.0). Collectie STATION.
Bronnen: luchtfoto PDOK (ref/luchtfoto/pagode_10cm.jpg), AHN dtm (ref/ahn), Pagode-bak-2023.jpg, Pagode-landing.jpg,
Pagodebouw03.jpg, Pagode-ingang-wachttijd.jpeg, video 0:40-0:55.
  - bak: middelpunt (360.0, 47.5), binnen-r 8.1, breuksteenrand tot r 8.9; vloer NAP 9.35 (z -0.65), groen beton
  - instapniveau / loopring NAP 11.3 (z +1.3), houten vlonder r 8.9 -> 10.6, groen hek aan de bakzijde
  - sleuf komt aan de westkant binnen (richting draaias, 164.4 graden), daar geen tribune/vlonder
  - stalen trap + bordes in de bak (Pagode-bak-2023.jpg)
  - tribune, wachtrij, borden: zie 12_omgeving.py
Gebruik: blender --background --python build/10_station.py -- --master AR_Pagode_master.blend"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix

OWNER = "phase:10_station"
CX, CY = 360.0, 47.5
AS = (320.5, 58.5)
R_BIN, R_RAND, R_VL = 8.1, 8.9, 10.6
Z_VLOER, Z_INSTAP = -0.65, 1.3
A_SLEUF = math.degrees(math.atan2(AS[1] - CY, AS[0] - CX))       # ~164.4 graden


def col():
    c = bpy.data.collections.get("STATION")
    if not c:
        c = bpy.data.collections.new("STATION"); bpy.context.scene.collection.children.link(c)
    return c


def obj(naam, bm, rol):
    me = bpy.data.meshes.new(naam); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(naam, me); col().objects.link(o); o["rol"] = rol; o["owner"] = OWNER
    return o


def ringsector(naam, r0, r1, z0, z1, a0, a1, rol, seg=None):
    """Gesloten ringsegment (graden, park: 0 = oost, 90 = noord) rond het bakmidden."""
    seg = seg or max(8, int(abs(a1 - a0) / 3))
    bm = bmesh.new(); rings = []
    for i in range(seg + 1):
        a = math.radians(a0 + (a1 - a0) * i / seg); c, s = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((CX + r * c, CY + r * s, z)) for r, z in ((r0, z0), (r1, z0), (r1, z1), (r0, z1))])
    for i in range(seg):
        for k in range(4):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % 4], rings[i + 1][(k + 1) % 4], rings[i + 1][k]))
    if abs(a1 - a0) < 359.9:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(naam, bm, rol)


def doos(naam, c, s, rol, rot=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=s, verts=bm.verts)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    return obj(naam, bm, rol)


def buis(naam, a, b, r, rol, seg=10):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
    M = Matrix.Translation((a + b) / 2) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return obj(naam, bm, rol)


def boogpunt(r, a, z):
    a = math.radians(a); return (CX + r * math.cos(a), CY + r * math.sin(a), z)


def build():
    a = sys.argv[sys.argv.index("--") + 1:]
    m = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=m)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    ws0, ws1 = A_SLEUF - 7.5, A_SLEUF + 7.5          # opening voor de sleuf (2 m breed op r 8 = ~15 graden)
    # 1 bakvloer (groen beton) en breuksteenwand
    ringsector("AR_Pagode_S_bakvloer", 0.0, R_BIN + 0.05, Z_VLOER - 0.3, Z_VLOER, 0, 360, "beton_groen_licht", seg=96)
    ringsector("AR_Pagode_S_bakwand", R_BIN, R_RAND, Z_VLOER - 0.35, Z_INSTAP - 0.08, ws1, ws0 + 360, "natuursteen")
    for k, (a0, a1) in enumerate(((ws0, ws0 + 0.01), )):
        pass
    # sleufwanden in de opening van de bak (sluiten aan op 09_voet sleuf: 2 m breed, bodem z -1.2)
    for k, s in enumerate((-1, 1)):
        a = math.radians(A_SLEUF); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
        p0 = (CX + ux * (R_BIN - 0.4) + nx * s * 1.12, CY + uy * (R_BIN - 0.4) + ny * s * 1.12)
        p1 = (CX + ux * 11.7 + nx * s * 1.12, CY + uy * 11.7 + ny * s * 1.12)
        c = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (Z_INSTAP - 1.4) / 2)
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        doos(f"AR_Pagode_S_sleufwand_{k}", c, (L, 0.34, Z_INSTAP + 1.4), "natuursteen", rot=a)   # 4 cm dikker dan 09_voet: geen gelijk vlak
    a = math.radians(A_SLEUF); c = (CX + math.cos(a) * 9.85, CY + math.sin(a) * 9.85, -1.36)
    doos("AR_Pagode_S_sleufbodem", c, (3.8, 2.3, 0.3), "grind", rot=a)
    # 2 houten loopring op instaphoogte + onderbouw (beton) en groen hek aan de bakzijde
    ringsector("AR_Pagode_S_vlonder", R_RAND - 0.1, R_VL, Z_INSTAP - 0.12, Z_INSTAP, ws1, ws0 + 360, "vlonder")
    ringsector("AR_Pagode_S_onderbouw", R_RAND - 0.05, R_VL + 0.05, -1.0, Z_INSTAP - 0.06, ws1 + 0.4, ws0 + 360 - 0.4, "beton_groen")   # 6 cm in de vlonder
    # hek aan de bakzijde met openingen voor de poortjes (poorten.py): geen palen/regels in de opening, dikkere poortpalen ernaast
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import poorten as PT
    rH = R_RAND + 0.15
    n = int((360 - 15) / 4)
    for i in range(n + 1):
        ang = ws1 + (ws0 + 360 - ws1) * i / n
        if PT.in_poort(ang, rH, 0.2): continue
        buis(f"AR_Pagode_S_hekpaal_{i:03d}", boogpunt(rH, ang, Z_INSTAP - 0.05), boogpunt(rH, ang, Z_INSTAP + 1.1), 0.035, "groen")
    # stukken hek tussen sleuf en poortjes
    stukken, a0 = [], ws1
    for naam, a, _ in sorted(PT.POORTEN, key=lambda q: (PT.park(q[1]) - ws1) % 360):
        c = ws1 + (PT.park(a) - ws1) % 360; h = PT.half_hoek(rH)
        stukken.append((a0, c - h)); a0 = c + h
        for s_ in (-1, 1):
            buis(f"AR_Pagode_S_poortpaal_{naam}_{s_ + 1}", boogpunt(rH, c + s_ * h, Z_INSTAP - 0.05), boogpunt(rH, c + s_ * h, Z_INSTAP + 1.2), 0.06, "groen")
    stukken.append((a0, ws0 + 360))
    for k, (b0, b1) in enumerate(stukken):
        for nm, z in (("boven", 1.1), ("midden", 0.6), ("onder", 0.12)):
            ringsector(f"AR_Pagode_S_hekregel_{nm}_{k}", R_RAND + 0.11, R_RAND + 0.19, Z_INSTAP + z - 0.03, Z_INSTAP + z + 0.03, b0, b1, "groen")
    # 3 tribunetrap: verhuisd naar 12_omgeving.py (11 rijen naar video + AHN)
    # 4 stalen trap + bordes in de bak (Pagode-bak-2023.jpg): kolom, bordes 2.4 x 2.4 op z 3.6, trap vanaf de vloer
    bx, by = CX - 1.5, CY + 1.0
    buis("AR_Pagode_S_kolom", (bx, by, Z_VLOER - 0.05), (bx, by, 3.55), 0.25, "staal_groen", 16)
    doos("AR_Pagode_S_bordes", (bx, by, 3.6), (2.4, 2.4, 0.12), "rooster")
    for nm, c, s in (("n", (bx, by + 1.2, 4.15), (2.4, 0.05, 1.1)), ("o", (bx + 1.2, by, 4.15), (0.05, 2.4, 1.1)), ("z", (bx, by - 1.2, 4.15), (2.4, 0.05, 1.1))):
        doos(f"AR_Pagode_S_bordeshek_{nm}", c, s, "hek_open")
    # trap: 22 treden van (bx-6.5, by) op de vloer naar het bordes (west)
    for k in range(22):
        t = k / 21
        x = bx - 1.2 - 5.0 * (1 - t); z = Z_VLOER + (3.6 - Z_VLOER) * t
        doos(f"AR_Pagode_S_traptrede_{k:02d}", (x, by, z), (0.26, 1.0, 0.05), "rooster")
    for s in (-1, 1):
        buis(f"AR_Pagode_S_trapboom_{s}", (bx - 6.3, by + s * 0.55, Z_VLOER), (bx - 1.15, by + s * 0.55, 3.6), 0.08, "staal_groen", 8)
        buis(f"AR_Pagode_S_trapleuning_{s}", (bx - 6.3, by + s * 0.55, Z_VLOER + 1.0), (bx - 1.15, by + s * 0.55, 4.6), 0.03, "hek", 8)
    # 5 bord PAGODE: verhuisd naar 12_omgeving.py (staat bij het plein, video 0:13)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=m)
    print("[10_station] klaar, sleufrichting %.1f graden, %d objecten" % (A_SLEUF, len([o for o in bpy.data.objects if o.get("owner") == OWNER])))


build()
