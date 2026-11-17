"""02_blockout: Sirocco hoofdmassa's (asset-brief.md). Modelframe: meters, x = oost, y = noord, z = 0 = waterpeil/platform,
oorsprong = dakmidden (park 456,5; 191,2 uit de luchtfoto).
Bronnen:  doorsnede B-B (ref/eftepedia/Sirocco_doorsnede.jpg, draaischijf 14 m = 60,7 px/m): nok 11,6 m, dakrand 3,0 m,
          voorvleugel tot 7,4 m; luchtfoto: dak 17,7 m doorsnede, voorkant naar het ZZW (parkhoek -124 gr);
          bovenaanzicht draaischijf (ref/eftepedia_mc/Wolmonsieurcannibale.jpg): 3 subschijven x 3 boten + 3 losse boten.
Maakt ook de gate-renders: zijaanzicht in de stand van de doorsnede en bovenaanzicht in de stand van de luchtfoto.
Gebruik: blender --background --python build/02_blockout.py -- --master AR_Sirocco_master.blend [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = "phase:02_blockout"

# maten (m)
R_DAK = 8.85                 # luchtfoto
Z_NOK = 11.6                 # doorsnede
Z_RAND = 3.0                 # doorsnede, achterkant
Z_VLEUGEL = 7.4              # doorsnede, opgekrulde voorkant
VOOR = math.radians(-124.0)  # voorkant (parkhoek, 0 = oost)
VLEUGEL_HALF = math.radians(55.0)
R_SCHIJF = 7.0               # lemma: 14 m doorsnede
R_DEK = 8.6                  # vast dek tot onder de dakrand
R_PAAL = 8.0
N_PAAL = 16
R_SUB, R_SUBMID = 2.3, 3.8   # subschijven (bovenaanzicht)
R_BOOT = 0.8
Z_PLAT = 0.3                 # bovenkant platform boven het water


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a


def collectie(naam):
    c = bpy.data.collections.get(naam)
    if not c:
        c = bpy.data.collections.new(naam); bpy.context.scene.collection.children.link(c)
    return c


def obj(naam, bm, kleur):
    me = bpy.data.meshes.new(naam); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(naam, me); o["owner"] = OWNER
    collectie("LOW").objects.link(o)
    m = bpy.data.materials.get("klei_" + naam.split("_")[2]) or bpy.data.materials.new("klei_" + naam.split("_")[2])
    m.diffuse_color = (*kleur, 1); me.materials.append(m)
    return o


def cilinder(naam, c, r, h, kleur, seg=48):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
    bmesh.ops.translate(bm, vec=Vector(c) + Vector((0, 0, h / 2)), verts=bm.verts)
    return obj(naam, bm, kleur)


def ring(naam, r0, r1, z0, z1, kleur, seg=96):
    bm = bmesh.new()
    lagen = []
    for z in (z0, z1):
        lagen.append([[bm.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)] for r in (r0, r1)])
    for i in range(seg):
        j = (i + 1) % seg
        (bi, bu), (ti, tu) = lagen
        bm.faces.new((ti[i], tu[i], tu[j], ti[j]))
        bm.faces.new((bi[j], bu[j], bu[i], bi[i]))
        bm.faces.new((bu[i], bu[j], tu[j], tu[i]))
        bm.faces.new((bi[j], bi[i], ti[i], ti[j]))
    return obj(naam, bm, kleur)


def vleugel(theta):
    """0..1: hoeveel de dakrand op hoek theta opkrult (1 = midden voorkant)"""
    d = (theta - VOOR + math.pi) % (2 * math.pi) - math.pi
    if abs(d) >= VLEUGEL_HALF: return 0.0
    return math.cos(d / VLEUGEL_HALF * math.pi / 2) ** 2


def dak():
    bm = bmesh.new()
    NA, NR, DIK = 128, 28, 0.45
    def punt(i, k, dik):
        t = 2 * math.pi * i / NA
        w = vleugel(t)
        e = Z_RAND + (Z_VLEUGEL - Z_RAND) * w
        R = R_DAK + 0.8 * w
        u = k / NR                                 # 0 = nok, 1 = rand
        p = 1.55 - 0.65 * w                        # holle zwaai; voorkant vlakker naar de rand (opgekruld)
        z = e + (Z_NOK - e) * (1 - u) ** p - dik
        return (R * u * math.cos(t), R * u * math.sin(t), z)
    boven = [[bm.verts.new(punt(i, k, 0)) for i in range(NA)] for k in range(1, NR + 1)]
    onder = [[bm.verts.new(punt(i, k, DIK)) for i in range(NA)] for k in range(1, NR + 1)]
    top_b = bm.verts.new((0, 0, Z_NOK)); top_o = bm.verts.new((0, 0, Z_NOK - DIK))
    for i in range(NA):
        j = (i + 1) % NA
        bm.faces.new((top_b, boven[0][i], boven[0][j]))
        bm.faces.new((top_o, onder[0][j], onder[0][i]))
        for k in range(NR - 1):
            bm.faces.new((boven[k][i], boven[k + 1][i], boven[k + 1][j], boven[k][j]))
            bm.faces.new((onder[k][j], onder[k + 1][j], onder[k + 1][i], onder[k][i]))
        bm.faces.new((boven[-1][i], onder[-1][i], onder[-1][j], boven[-1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj("SI_blk_dak", bm, (0.55, 0.5, 0.42))
    # spits op de nok
    cilinder("SI_blk_spits", (0, 0, Z_NOK - 0.3), 0.18, 1.2, (0.3, 0.25, 0.2), 12)


def palen():
    bm = bmesh.new()
    for i in range(N_PAAL):
        t = 2 * math.pi * (i + 0.5) / N_PAAL
        w = vleugel(t)
        e = Z_RAND + (Z_VLEUGEL - Z_RAND) * w
        r = R_PAAL
        # hoogte: tot onder het dak op straal r
        u = r / (R_DAK + 0.8 * w); p = 1.55 - 0.65 * w
        top = e + (Z_NOK - e) * (1 - u) ** p - 0.45
        c = Vector((r * math.cos(t), r * math.sin(t), 0))
        res = bmesh.ops.create_cube(bm, size=1)
        bmesh.ops.scale(bm, vec=(0.32, 0.32, top), verts=res["verts"])
        bmesh.ops.translate(bm, vec=c + Vector((0, 0, top / 2)), verts=res["verts"])
    obj("SI_blk_palen", bm, (0.3, 0.22, 0.15))


def draaischijf():
    cilinder("SI_blk_schijf", (0, 0, Z_PLAT - 0.3), R_SCHIJF, 0.3, (0.2, 0.35, 0.65), 96)
    ring("SI_blk_dek", R_SCHIJF + 0.05, R_DEK, Z_PLAT - 0.3, Z_PLAT, (0.45, 0.33, 0.22))
    cilinder("SI_blk_ton", (0, 0, Z_PLAT), 0.6, 1.2, (0.45, 0.3, 0.18), 24)
    for s in range(3):
        a = VOOR + math.radians(90 + 120 * s)
        c = Vector((R_SUBMID * math.cos(a), R_SUBMID * math.sin(a), Z_PLAT))
        cilinder(f"SI_blk_sub{s}", c, R_SUB, 0.08, (0.25, 0.45, 0.75), 48)
        for b in range(3):
            ab = a + math.radians(120 * b)
            cilinder(f"SI_blk_boot{s}{b}", c + Vector((1.35 * math.cos(ab), 1.35 * math.sin(ab), 0.08)), R_BOOT, 1.0, (0.7, 0.2, 0.15), 24)
        a2 = a + math.radians(60)
        cilinder(f"SI_blk_bootlos{s}", (5.9 * math.cos(a2), 5.9 * math.sin(a2), Z_PLAT), R_BOOT, 1.0, (0.7, 0.2, 0.15), 24)


def water():
    ring("SI_blk_water", R_DEK, 13.0, -0.05, 0.0, (0.15, 0.3, 0.35), 96)


def render(uit):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
    sc.render.film_transparent = True
    cam_d = bpy.data.cameras.new("gatecam"); cam_d.type = "ORTHO"
    cam = bpy.data.objects.new("gatecam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    # zijaanzicht als de doorsnede: voorkant rechts, 60,7 px/m, waterlijn op y 930, draaischijfmidden op x 955
    f = Vector((math.cos(VOOR), math.sin(VOOR), 0)); d = Vector((0, 0, 1)).cross(f)
    sc.render.resolution_x, sc.render.resolution_y = 2000, 1419
    cam_d.ortho_scale = 2000 / 60.7
    mid = f * ((1000 - 955) / 60.7) + Vector((0, 0, (930 - 709.5) / 60.7))
    cam.location = mid - d * 60
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(uit, "blk_zij.png"); bpy.ops.render.render(write_still=True)
    # doorsnede zoals de tekening: alles voor het middenvlak wegknippen (clip_start = afstand tot het midden)
    cam_d.clip_start = 59.9; cam_d.clip_end = 200
    sc.render.filepath = os.path.join(uit, "blk_snede.png"); bpy.ops.render.render(write_still=True)
    cam_d.clip_start = 0.1
    # bovenaanzicht als de luchtfoto: 70 m, midden park (455,188) = model (-1.5,-3.2)
    sc.render.resolution_x = sc.render.resolution_y = 1400
    cam_d.ortho_scale = 70
    cam.location = (455 - 456.5, 188 - 191.2, 60); cam.rotation_euler = (0, 0, 0)
    sc.render.filepath = os.path.join(uit, "blk_boven.png"); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def main():
    a = args()
    master = os.path.abspath(a[a.index("--master") + 1]) if "--master" in a else os.path.join(D, "AR_Sirocco_master.blend")
    if os.path.exists(master):
        bpy.ops.wm.open_mainfile(filepath=master)
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.unit_settings.system = "METRIC"
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    dak(); palen(); draaischijf(); water()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=master)
    if "--render" in a:
        render(os.path.join(D, "review"))
    print("[02_blockout] klaar:", len([o for o in bpy.data.objects if o.get("owner") == OWNER]), "objecten")


main()
