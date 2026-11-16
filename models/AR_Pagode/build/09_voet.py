"""09_voet: draaias, pijlers, hefcilinders, put met contragewicht en de sleuf naar de bak (stand OMHOOG).
Draai NA 08_arm.py; daarna 05_materials. Lokaal gondelframe (meter): +x = richting bak (park ESE), z omhoog.
Bronnen: ref/eftepedia/Pagode_tech.png (cilinders: voet 6.5 m richting bak en 6.7 m onder de as, kop 2.8 m boven de as op de
arm; 11 m lang), Pagodegewicht.jpg (contragewicht = groen betonblok), Pagode-cylinders.jpg (witte cilinders, groene put,
roosters, zwarte hekken), luchtfoto PDOK + AHN (ref/luchtfoto, ref/ahn): as op park (320.5, 58.5), grond NAP ~10.0,
sleufbodem NAP 8.8, sleuf ~2 m breed naar de bak (middelpunt bak 41 m van de as).
Gebruik: blender --background --python build/09_voet.py -- --master AR_Pagode_master.blend"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix

DEK = 2.2
Z_GROND = DEK - 45.0            # platform 45 m boven de grond (Eftepedia)
D_BAK = 41.0                    # as -> middelpunt bak (luchtfoto)
R_BAK_BUITEN = 8.9
SLEUF_DIEP = 1.2                # NAP 10.0 -> 8.8
OWNER = "phase:09_voet"


def col():
    return bpy.data.collections.get("LOW") or bpy.context.scene.collection


def doos(naam, c, s, rol, rot=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=s, verts=bm.verts)
    me = bpy.data.meshes.new(naam); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(naam, me); col().objects.link(o)
    o.location = c; o.rotation_euler = (0, 0, rot); o["rol"] = rol; o["owner"] = OWNER
    return o


def buis(naam, a, b, r, rol, seg=16):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
    me = bpy.data.meshes.new(naam); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(naam, me); col().objects.link(o)
    o.matrix_world = Matrix.Translation((a + b) / 2) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    o["rol"] = rol; o["owner"] = OWNER
    return o


def hek(naam, a, b, z, rol="hek"):
    """Zwart buishek (Pagode-cylinders.jpg): boven- en tussenregel + staanders om de 1.5 m, 1.1 m hoog."""
    a, b = Vector(a), Vector(b)
    buis(naam + "_boven", (a.x, a.y, z + 1.1), (b.x, b.y, z + 1.1), 0.03, rol, 8)
    buis(naam + "_midden", (a.x, a.y, z + 0.55), (b.x, b.y, z + 0.55), 0.02, rol, 8)
    n = max(1, int((b - a).length / 1.5))
    for i in range(n + 1):
        p = a + (b - a) * (i / n)
        buis(f"{naam}_staander_{i}", (p.x, p.y, z - 0.05), (p.x, p.y, z + 1.12), 0.03, rol, 8)


def build():
    a = sys.argv[sys.argv.index("--") + 1:]
    m = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=m)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    arm = bpy.data.objects["AR_Pagode_arm"]
    P = Vector(arm["draaias"]); zg = Z_GROND
    # richting van het lange armstuk (omhoog) en de arm-as boven de draaias
    knik = Vector(arm["knik"]); omhoog = (knik - P).normalized()

    # 1 put: binnenwanden + bodem (donker beton), van 9 m achter de as tot 7 m ervoor, 6 m breed, 10 m diep
    x0, x1, hy, diep = P.x - 9.0, P.x + 7.0, 3.0, 10.0
    doos("AR_Pagode_V_putbodem", ((x0 + x1) / 2, 0, zg - diep - 0.25), (x1 - x0 + 0.8, 2 * hy + 0.8, 0.5), "beton_donker")
    for nm, c, s in (("west", (x0 - 0.2, 0, zg - diep / 2 + 0.5), (0.4, 2 * hy + 0.8, diep + 1.0)),
                     ("oost", (x1 + 0.2, 0, zg - diep / 2 + 0.5), (0.4, 2 * hy + 0.8, diep + 1.0)),
                     ("noord", ((x0 + x1) / 2, hy + 0.2, zg - diep / 2 + 0.5), (x1 - x0, 0.4, diep + 1.0)),
                     ("zuid", ((x0 + x1) / 2, -hy - 0.2, zg - diep / 2 + 0.5), (x1 - x0, 0.4, diep + 1.0))):
        doos(f"AR_Pagode_V_putwand_{nm}", c, s, "beton_groen")      # bovenrand 0.5 m boven de grond (groen geverfd)
    # 2 roosters over de put (grijs staal), met een opening rond de arm (2.6 x 1.8 m) en voor de cilinders
    zr = zg + 0.45
    for nm, xa, xb, ya, yb in (("west", x0, P.x - 1.3, -hy, hy), ("oost", P.x + 7.0 - 0.01, x1, -hy, hy),
                               ("noord", P.x - 1.3, P.x + 7.0, 1.4, hy), ("zuid", P.x - 1.3, P.x + 7.0, -hy, -1.4)):
        if xb - xa > 0.05:
            doos(f"AR_Pagode_V_rooster_{nm}", ((xa + xb) / 2, (ya + yb) / 2, zr), (xb - xa, yb - ya, 0.08), "rooster")
    # 3 hekken rond de put (zwart, Pagode-cylinders.jpg)
    for nm, pa, pb in (("n", (x0, hy + 0.2), (x1, hy + 0.2)), ("z", (x0, -hy - 0.2), (x1, -hy - 0.2)),
                       ("w", (x0 - 0.2, -hy), (x0 - 0.2, hy))):
        hek(f"AR_Pagode_V_hek_{nm}", (pa[0], pa[1], 0), (pb[0], pb[1], 0), zg + 0.5)
    # 4 pijlers (groen beton) aan weerszijden van de arm, tot net boven de as
    for k, s in enumerate((-1, 1)):
        doos(f"AR_Pagode_V_pijler_{k}", (P.x, s * 1.75, (zg - 2 + P.z + 0.9) / 2), (3.0, 1.5, P.z + 0.9 - zg + 2), "beton_groen")
        buis(f"AR_Pagode_V_lager_{k}", (P.x, s * 0.95, P.z), (P.x, s * 2.65, P.z), 0.75, "staal", 24)     # lagerhuis
    buis("AR_Pagode_V_as", (P.x, -2.8, P.z), (P.x, 2.8, P.z), 0.42, "staal", 24)
    # 5 hefcilinders (wit, 11 m): voet in de put 6.5 m richting bak en 6.7 m onder de as, kop op de arm 2.8 m boven de as
    kop = P + omhoog * 2.8
    for k, s in enumerate((-1, 1)):
        voet = Vector((P.x + 6.5, s * 0.95, P.z - 6.7))
        kp = Vector((kop.x, s * 0.95, kop.z)); d = (kp - voet)
        mid = voet + d * 0.62
        buis(f"AR_Pagode_V_cilinder_{k}", voet, mid + d.normalized() * 0.3, 0.36, "wit_glans", 24)
        buis(f"AR_Pagode_V_zuigerstang_{k}", mid, kp, 0.17, "chroom", 16)
        buis(f"AR_Pagode_V_cilindervoet_{k}", (voet.x, s * 0.95 - 0.45, voet.z), (voet.x, s * 0.95 + 0.45, voet.z), 0.3, "staal")
        buis(f"AR_Pagode_V_cilinderkop_{k}", (kp.x, s * 0.95 - 0.35, kp.z), (kp.x, s * 0.95 + 0.35, kp.z), 0.22, "staal")
    # 6 contragewicht (groen beton, Pagodegewicht.jpg) aan het eind van de arm onder de as: 340 t ~ 6 x 4 x 6 m
    eind = P - omhoog * 5.0
    doos("AR_Pagode_V_contragewicht", (eind.x, 0, eind.z - 2.2), (6.0, 4.2, 5.6), "beton_groen")
    # 7 sleuf naar de bak: 2 m breed, bodem 1.2 m onder de grond, betonwanden; van de put tot de bakrand
    xs0, xs1 = x1 + 0.4, P.x + D_BAK - 11.6        # tot 11.6 m van het bakmidden; daar neemt 10_station het over
    doos("AR_Pagode_V_sleufbodem", ((xs0 + xs1) / 2, 0, zg - SLEUF_DIEP - 0.15), (xs1 - xs0, 2.4, 0.3), "grind")
    for k, s in enumerate((-1, 1)):
        doos(f"AR_Pagode_V_sleufwand_{k}", ((xs0 + xs1) / 2, s * 1.1, zg - SLEUF_DIEP / 2 + 0.1), (xs1 - xs0, 0.3, SLEUF_DIEP + 0.4), "beton_groen")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=m)
    print("[09_voet] as op (%.2f, %.2f), grond z %.2f (as %.1f m boven de grond), sleuf %.1f m" % (P.x, P.z, zg, P.z - zg, xs1 - xs0))


build()
