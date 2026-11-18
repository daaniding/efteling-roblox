"""02_blockout: Archipel hoofdmassa's (asset-brief.md, plan.py). Modelstelsel: meters t.o.v. plan.OORSPRONG (park 452; 160),
x oost, y noord, z 0 = waterpeil.
Maakt: betonbodem (hoogteveld uit plan.bodem, EPDM-zone apart), waterplaat, kademuur, maaiveldrand, 4 paalhutten + ronde hut als
blokken, loopbruggen, wrak (2 helften + balk + mast), palen, kisten, tonnen, ingangsvlonder.
Maten hutten: doorsnede-paalvissers.jpg (romp 2,5 m = 185 px): vloer 1,28, dakrand 2,6, nok 5,3, spits 6,1 m.
Gebruik: blender --background --python build/02_blockout.py -- --master AR_Archipel_master.blend [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, "build"))
import plan as P

OWNER = "phase:02_blockout"
RASTER = 0.3


def collectie(naam):
    c = bpy.data.collections.get(naam)
    if not c:
        c = bpy.data.collections.new(naam); bpy.context.scene.collection.children.link(c)
    return c


def mat(naam, kleur):
    m = bpy.data.materials.get(naam) or bpy.data.materials.new(naam)
    m.diffuse_color = (*kleur, 1); return m


def obj(naam, bm, kleur, rol=None):
    me = bpy.data.meshes.new(naam); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(naam, me); o["owner"] = OWNER
    if rol: o["rol"] = rol
    collectie("LOW").objects.link(o)
    me.materials.append(mat("klei_" + (rol or naam), kleur))
    return o


def M(p): return Vector((p[0] - P.OORSPRONG[0], p[1] - P.OORSPRONG[1], 0))


def doos(bm, c, sx, sy, sz, rot=0.0):
    r = bmesh.ops.create_cube(bm, size=1.0)
    vs = r["verts"]
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=vs)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(rot, 3, "Z"), verts=vs)
    bmesh.ops.translate(bm, vec=Vector(c), verts=vs)


def cil(bm, a, b, r, seg=12):
    a, b = Vector(a), Vector(b); d = b - a
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
    q = d.normalized().to_track_quat("Z", "Y")
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=q.to_matrix(), verts=res["verts"])
    bmesh.ops.translate(bm, vec=(a + b) / 2, verts=res["verts"])


def kegel(bm, c, r0, r1, h, seg=4, rot=math.pi / 4):
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r0, radius2=r1, depth=h)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(rot, 3, "Z"), verts=res["verts"])
    bmesh.ops.translate(bm, vec=Vector(c) + Vector((0, 0, h / 2)), verts=res["verts"])


def bodem():
    xs = [p[0] for p in P.KADE]; ys = [p[1] for p in P.KADE]
    x0, x1, y0, y1 = min(xs) - 0.3, max(xs) + 0.3, min(ys) - 0.3, max(ys) + 0.3
    nx, ny = int((x1 - x0) / RASTER) + 1, int((y1 - y0) / RASTER) + 1
    bm_b, bm_e = bmesh.new(), bmesh.new()
    cache = {}

    def hoogte(i, j):
        if (i, j) not in cache:
            x, y = x0 + i * RASTER, y0 + j * RASTER
            z = P.bodem(x, y)
            cache[(i, j)] = P.Z_STRAND if z is None else z
        return cache[(i, j)]
    vmaps = ({}, {})
    for j in range(ny - 1):
        for i in range(nx - 1):
            cx, cy = x0 + (i + 0.5) * RASTER, y0 + (j + 0.5) * RASTER
            if not P.binnen(cx, cy, P.KADE): continue
            e = P.is_epdm(cx, cy)
            bm = bm_e if e else bm_b; vm = vmaps[1 if e else 0]
            vs = []
            for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)):
                k = (i + di, j + dj)
                if k not in vm:
                    vm[k] = bm.verts.new((x0 + k[0] * RASTER - P.OORSPRONG[0], y0 + k[1] * RASTER - P.OORSPRONG[1], hoogte(*k)))
                vs.append(vm[k])
            bm.faces.new(vs)
    for bm in (bm_b, bm_e):
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts, edges=bm.edges)
    obj("AR_bodem_beton", bm_b, (0.86, 0.8, 0.68), "beton")
    obj("AR_bodem_epdm", bm_e, (0.35, 0.68, 0.66), "epdm")


def ring_langs(pts, binnen_off, buiten_off, z0, z1):
    """band langs een gesloten veelhoek (parkcoordinaten), offsets naar buiten positief"""
    bm = bmesh.new(); n = len(pts)
    # oriëntatie: tegen de klok in -> buitennormaal = (dy, -dx)
    opp = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    s = 1 if opp > 0 else -1
    lagen = []
    for i in range(n):
        a, b, c = Vector(M(pts[i - 1])), Vector(M(pts[i])), Vector(M(pts[(i + 1) % n]))
        t = ((b - a).normalized() + (c - b).normalized()).normalized()
        nrm = Vector((t.y, -t.x, 0)) * s
        lagen.append([bm.verts.new(b + nrm * o + Vector((0, 0, z))) for o, z in
                      ((binnen_off, z0), (binnen_off, z1), (buiten_off, z1), (buiten_off, z0))])
    for i in range(n):
        A, B = lagen[i], lagen[(i + 1) % n]
        for k in range(4):
            try: bm.faces.new((A[k], B[k], B[(k + 1) % 4], A[(k + 1) % 4]))
            except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def kade():
    obj("AR_kade", ring_langs(P.KADE, -0.12, 0.25, -0.7, P.Z_MAAIVELD + 0.06), (0.8, 0.76, 0.68), "kade")
    obj("AR_maaiveld", ring_langs(P.KADE, 0.25, 2.2, P.Z_MAAIVELD - 0.02, P.Z_MAAIVELD), (0.36, 0.3, 0.22), "aarde")


def water():
    bm = bmesh.new()
    vs = [bm.verts.new(M(p)) for p in P.KADE]
    f = bm.faces.new(vs)
    if f.normal.z < 0: f.normal_flip()
    obj("AR_water", bm, (0.45, 0.78, 0.82), "water")


def paalhut(h):
    c = M(h["c"]); rot = math.radians(h["rot"]); b, d = h["b"], h["d"]
    romp = 2.5 * b / 3.0
    zv = h["vloer"]; zr = zv + 1.32; zn = zr + 2.7
    vloer_z = 0 if h.get("droog") else P.bodem(*h["c"]) or 0
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = c + Vector((sx * romp * 0.42, sy * romp * 0.42, 0)); cil(bm, p + Vector((0, 0, vloer_z - 0.3)), p + Vector((0, 0, zv)), 0.13)
    obj(h["naam"] + "_palen", bm, (0.6, 0.45, 0.28), "paal")
    bm = bmesh.new(); doos(bm, c + Vector((0, 0, zv + 0.66)), romp, romp, 1.32, rot)
    obj(h["naam"] + "_romp", bm, (0.78, 0.66, 0.42), "bamboewand")
    bm = bmesh.new(); kegel(bm, c + Vector((0, 0, zr - 0.1)), b * 0.62, 0.12, zn - zr + 0.1, 4, rot + math.pi / 4)
    for k in range(h.get("spitsen", 0) or 0):
        off = Vector((0, 0, 0)) if h.get("spitsen") == 1 else Vector((math.cos(rot) * (k - 0.5) * 0.55, math.sin(rot) * (k - 0.5) * 0.55, 0))
        cil(bm, c + off + Vector((0, 0, zn - 0.3)), c + off + Vector((0, 0, zn + 0.8)), 0.05, 6)
    obj(h["naam"] + "_dak", bm, (0.62, 0.5, 0.32), "riet")


def ronde_hut():
    h = P.RONDE_HUT; c = M(h["c"]); r = h["r"]
    bm = bmesh.new(); kegel(bm, c + Vector((0, 0, P.Z_STRAND)), r * 0.8, r * 0.8, 2.1, 24, 0)
    obj("hut5_romp", bm, (0.78, 0.66, 0.42), "bamboewand")
    bm = bmesh.new(); kegel(bm, c + Vector((0, 0, 2.1)), r * 1.15, 0.1, 2.6, 24, 0)
    obj("hut5_dak", bm, (0.62, 0.5, 0.32), "riet")


def loopbruggen():
    bm = bmesh.new()
    vm = M(P.VLONDER_MIDDEN); doos(bm, vm + Vector((0, 0, 1.0)), 1.6, 1.6, 0.12)
    for a, b in P.LOOPBRUGGEN:
        A, B = M(a), M(b); d = B - A
        doos(bm, (A + B) / 2 + Vector((0, 0, 1.1)), 0.55, d.length, 0.08, math.atan2(d.y, d.x) - math.pi / 2)
    obj("AR_loopbruggen", bm, (0.55, 0.42, 0.28), "plank")


def wrak():
    w = P.WRAK; bm = bmesh.new()
    for k, (sx, sy, sz) in (("achtersteven", (2.4, 1.9, 2.0)), ("voorsteven", (2.2, 1.4, 2.2))):
        x, y, r = w[k]; doos(bm, M((x, y)) + Vector((0, 0, sz / 2 - 0.4)), sx, sy, sz, math.radians(r))
    obj("AR_wrak", bm, (0.4, 0.27, 0.18), "romp")
    bm = bmesh.new()
    A, B = M(w["balk"][0]), M(w["balk"][1]); cil(bm, A + Vector((0, 0, 0.55)), B + Vector((0, 0, 0.55)), 0.24, 12)
    x, y, hgt = w["mast"]; cil(bm, M((x, y)) + Vector((0, 0, -0.4)), M((x, y)) + Vector((0, 0, hgt)), 0.14, 10)
    obj("AR_mast", bm, (0.42, 0.28, 0.2), "mast")


def palen():
    bm = bmesh.new()
    for x, y, hgt in P.KLIMPALEN + [P.PAALVISSER]:
        cil(bm, M((x, y)) + Vector((0, 0, -0.4)), M((x, y)) + Vector((0, 0, hgt + (0.9 if (x, y, hgt) == P.PAALVISSER else 0))), 0.16, 10)
    obj("AR_palen", bm, (0.72, 0.55, 0.34), "paal")
    x, y, hgt = P.PAALVISSER; bm = bmesh.new(); doos(bm, M((x, y)) + Vector((0.25, 0, hgt + 0.55)), 0.4, 0.45, 1.1)
    obj("AR_paalvisser", bm, (0.3, 0.3, 0.6), "figuur")


def kisten():
    bm = bmesh.new()
    for x, y, r in P.KISTEN:
        z = P.bodem(x, y) or 0; doos(bm, M((x, y)) + Vector((0, 0, z + 0.3)), 0.8, 0.8, 0.62, math.radians(r))
    x, y, r = P.SCHATKIST; z = P.bodem(x, y) or 0; doos(bm, M((x, y)) + Vector((0, 0, z + 0.25)), 0.75, 0.5, 0.5, math.radians(r))
    obj("AR_kisten", bm, (0.52, 0.38, 0.24), "kist")
    bm = bmesh.new()
    for x, y in P.TONNEN:
        z = P.bodem(x, y) or 0; kegel(bm, M((x, y)) + Vector((0, 0, z)), 0.36, 0.36, 0.42, 16, 0)
    obj("AR_tonnen", bm, (0.6, 0.3, 0.2), "ton")


def ingang():
    bm = bmesh.new(); pts = P.INGANG_VLONDER
    for a, b in zip(pts, pts[1:]):
        A, B = M(a), M(b); d = B - A
        doos(bm, (A + B) / 2 + Vector((0, 0, P.Z_MAAIVELD + 0.05)), P.INGANG_BREEDTE, d.length + 0.1, 0.1, math.atan2(d.y, d.x) - math.pi / 2)
    obj("AR_ingangsvlonder", bm, (0.5, 0.4, 0.3), "plank")


def render(uit):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
    sc.display.shading.show_shadows = True
    sc.render.film_transparent = True
    cam_d = bpy.data.cameras.new("gatecam"); cam_d.type = "ORTHO"
    cam = bpy.data.objects.new("gatecam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    # bovenaanzicht als ref/luchtfoto_2022 (36 m, midden park 450; 161)
    sc.render.resolution_x = sc.render.resolution_y = 1440
    cam_d.ortho_scale = 36
    cam.location = (450 - P.OORSPRONG[0], 161 - P.OORSPRONG[1], 60); cam.rotation_euler = (0, 0, 0)
    sc.render.filepath = os.path.join(uit, "blk_boven.png"); bpy.ops.render.render(write_still=True)
    # perspectief zoals Archipel_zonnig_2022.jpg / Archipel-boot.jpg: vanaf het strand oost bij het wrak naar het westen
    cam_d.type = "PERSP"; cam_d.lens = 26; sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    for naam, pos, doel in (("blk_oost", (467.8, 161.8, 1.65), (450.0, 156.5, 2.4)), ("blk_zuidoost", (457.5, 147.0, 1.7), (447.0, 160.0, 2.0)),
                            ("blk_noord", (452.0, 171.5, 4.0), (450.0, 155.0, 1.0))):
        p = Vector((pos[0] - P.OORSPRONG[0], pos[1] - P.OORSPRONG[1], pos[2]))
        q = Vector((doel[0] - P.OORSPRONG[0], doel[1] - P.OORSPRONG[1], doel[2]))
        cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(uit, naam + ".png"); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def main():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    master = os.path.abspath(a[a.index("--master") + 1]) if "--master" in a else os.path.join(D, "AR_Archipel_master.blend")
    if os.path.exists(master):
        bpy.ops.wm.open_mainfile(filepath=master)
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.unit_settings.system = "METRIC"
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o)
    bodem(); kade(); water()
    for h in P.HUTTEN: paalhut(h)
    ronde_hut(); loopbruggen(); wrak(); palen(); kisten(); ingang()
    bpy.ops.wm.save_as_mainfile(filepath=master)
    if "--render" in a:
        uit = os.path.join(D, "review", "02_blockout"); os.makedirs(uit, exist_ok=True); render(uit)
    print("[02_blockout] klaar:", len([o for o in bpy.data.objects if o.get("owner") == OWNER]), "objecten")


main()
