"""04_minaret: stap 3 — de minaret op het plein (Fmplein1986.jpg, FataVoorplein1993.jpg; AHN-top 25,6 m bij park (19,5; -329)).
Maten (Fmplein1986: 25,6 px/m): onderblok 4,6 m breed tot 8,5 m (zandkleurig, hoekblokken, spitsboogdeur met rode omlijsting in
een tegelpaneel, boogvensters, rode zigzagfries), wit balkon met vier bollen; witte bovenschacht 3,2 m tot 17,8 m met
boogvenstertjes en donkere hoeklijnen; tweede balkon met blauwe tegelborstwering; lantaarntje met boogopeningen; geribde
turquoise koepel; gouden spits met halve maan. Deur naar het plein (oost, +x).
Modelstelsel = 02/03 (oorsprong park -40; -295). Deel "minaret".
Gebruik: blender --background --python build/04_minaret.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F3 = os.path.join(D, "build", "03_noordgevel.py")
G3 = {"__file__": F3, "__name__": "lib"}
exec(compile(open(F3).read().rsplit("\nmain()", 1)[0], F3, "exec"), G3)
T = G3["T"]; L, prisma, lathe, quad, strip, spitsboog, vul, raam, Vlak = (G3[k] for k in ("L", "prisma", "lathe", "quad", "strip", "spitsboog", "vul", "raam", "Vlak"))
OWNER = "phase:04_minaret"
VAST = ("zellige", "zigzag", "balkon")
T["KLEUR"].update({"zandsteen": (0.84, 0.72, 0.56), "wit": (0.95, 0.94, 0.9), "rood": (0.66, 0.18, 0.14), "zellige": (0.2, 0.5, 0.6),
                   "zigzag": (0.66, 0.18, 0.14), "balkon": (0.85, 0.88, 0.95), "donker": (0.12, 0.16, 0.22)})
T["UVS"].update({"zandsteen": 9.0, "wit": 9.0, "rood": 1.0, "zellige": 1.0, "zigzag": 1.0, "balkon": 1.0, "donker": 1.0})
T["OVERLAY"] = tuple(T["OVERLAY"]) + VAST
for r in T["KLEUR"]: T["G"][r] = bmesh.new()

C = L(19.5, -329.0)


def vlakken(hw):
    """vier gevels van een vierkant (halve breedte hw) om C: (Vlak, breedte); u loopt van -hw tot hw"""
    out = []
    for N in (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((-1, 0, 0)), Vector((0, -1, 0))):
        U = Vector((N.y, -N.x, 0))
        out.append(Vlak(C + N * hw, U, N))
    return out


def paneel(rol, vl, u0, u1, v0, v1, n, su, sv, du=0.0, dv=0.0):
    """vlak met eigen UV (tegels, friezen): u/su, v/sv"""
    bm = T["G"][rol]; uvl = bm.loops.layers.uv.verify()
    pts = [vl.p(u0, v0, n), vl.p(u1, v0, n), vl.p(u1, v1, n), vl.p(u0, v1, n)][::-1]
    uv = [((u0 + du) / su, (v0 - dv) / sv), ((u1 + du) / su, (v0 - dv) / sv), ((u1 + du) / su, (v1 - dv) / sv), ((u0 + du) / su, (v1 - dv) / sv)][::-1]
    f = bm.faces.new([bm.verts.new(p) for p in pts])
    for lp, t in zip(f.loops, uv): lp[uvl].uv = t


def blok(rol, hw, z0, z1):
    prisma(rol, [C + Vector((sx * hw, sy * hw, 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], z0, z1)


def band(rol, hw, z0, z1, n=0.02, su=1.5):
    for vl in vlakken(hw):
        paneel(rol, vl, -hw, hw, z0, z1, n, su, z1 - z0, 0.0, z0)


def balkon(hw, z, h_rand, rol_rand, bollen):
    """overstekend balkon: getrapte consoles, vloerplaat, borstwering (rondom), hoekpaaltjes met bollen"""
    for k, f in enumerate((0.25, 0.5, 0.75)):
        blok("lijst", hw - 0.4 + f * 0.55, z - 0.45 + k * 0.15, z - 0.3 + k * 0.15)
    blok("lijst", hw + 0.4, z, z + 0.16)
    hb = hw + 0.32
    for vl in vlakken(hb):
        prisma("wit", [Vector((p.x, p.y, 0)) for p in (vl.p(-hb, 0, 0), vl.p(hb, 0, 0), vl.p(hb, 0, -0.16), vl.p(-hb, 0, -0.16))], z + 0.16, z + 0.16 + h_rand)
        if rol_rand: paneel(rol_rand, vl, -hb + 0.25, hb - 0.25, z + 0.24, z + 0.08 + h_rand, 0.015, 1.0, h_rand - 0.16, 0.0, z + 0.24)
    blok("lijst", hb + 0.05, z + 0.16 + h_rand, z + 0.26 + h_rand) if False else None
    for vl in vlakken(hb):
        prisma("lijst", [Vector((p.x, p.y, 0)) for p in (vl.p(-hb - 0.05, 0, 0.05), vl.p(hb + 0.05, 0, 0.05), vl.p(hb + 0.05, 0, -0.22), vl.p(-hb - 0.05, 0, -0.22))],
               z + 0.16 + h_rand, z + 0.26 + h_rand)
    if bollen:
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = C + Vector((sx * (hb - 0.08), sy * (hb - 0.08), 0))
            prisma("wit", [p + Vector((a, b, 0)) * 0.17 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], z + 0.16, z + 0.36 + h_rand)
            lathe("wit", [(r * 0.2, zz) for r, zz in ((0.0, -0.2), (0.7, -0.15), (1.0, 0.0), (0.7, 0.15), (0.0, 0.22))], z + 0.62 + h_rand, 12, (p.x, p.y))


def bouw():
    # onderblok: zandsteen met hoekblokken (lijst), plint
    hw = 2.3
    blok("zandsteen", hw, 0.0, 8.4)
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        p = C + Vector((sx * (hw - 0.22), sy * (hw - 0.22), 0))
        for k in range(14):                                # om-en-om lange en korte hoekblokken
            z0 = k * 0.56; l = 0.55 if k % 2 == 0 else 0.4
            prisma("lijst", [p + Vector((a * (0.28 if k % 2 == 0 else 0.25), b * (0.28 if k % 2 == 0 else 0.25), 0)) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], z0, z0 + 0.52)
    blok("lijst", hw + 0.08, 0.0, 0.35)
    for i, vl in enumerate(vlakken(hw)):
        if i == 0:                                         # voorkant (oost): tegelpaneel met deur, vensters erboven
            paneel("zellige", vl, -1.25, 1.25, 0.35, 4.6, 0.02, 1.2, 1.2)
            strip("lijst", vl, [(-1.32, 0.35), (-1.32, 4.67), (1.32, 4.67), (1.32, 0.35)], 0.14, 0.08)
            deur = spitsboog(0, 1.25, 0.0, 2.15, 10, 0.62)
            vul("deur", vl, deur, 0.06); strip("rood", vl, deur, 0.22, 0.12)
            raam(vl, -0.55, 0.5, 5.6, 6.9); raam(vl, 0.55, 0.5, 5.6, 6.9)
            paneel("zellige", vl, -1.05, 1.05, 5.3, 7.35, 0.015, 1.2, 1.2)
        else:
            raam(vl, 0.0, 0.6, 5.6, 7.0)
            paneel("zellige", vl, -0.75, 0.75, 5.3, 7.4, 0.015, 1.2, 1.2)
    band("zigzag", hw, 7.75, 8.4, 0.03)
    balkon(hw, 8.55, 0.85, None, True)
    # bovenschacht: wit, donkere hoeklijnen, boogvenstertjes
    hs = 1.6
    blok("wit", hs, 8.7, 18.1)
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        p = C + Vector((sx * hs, sy * hs, 0))
        prisma("donker", [p + Vector((a, b, 0)) * 0.06 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 9.6, 17.3)
    for vl in vlakken(hs):
        raam(vl, 0.0, 0.42, 10.6, 11.7); raam(vl, 0.0, 0.42, 14.3, 15.4)
        strip("lijst", vl, [(-hs + 0.12, 9.7), (-hs + 0.12, 17.1), (hs - 0.12, 17.1), (hs - 0.12, 9.7)], 0.08, 0.04)
    band("zigzag", hs, 17.6, 18.1, 0.03)
    for k, f in enumerate((0.1, 0.22, 0.34, 0.46)):           # diepe consolezone onder het tweede balkon (Fmplein1986)
        blok("lijst", hs + f, 18.1 + k * 0.2, 18.3 + k * 0.2)
    balkon(hs, 18.9, 1.0, "balkon", False)
    # lantaarntje met boogopeningen
    hl = 1.0; z0 = 19.06
    for vl in vlakken(hl):
        prisma("wit", [Vector((p.x, p.y, 0)) for p in (vl.p(-hl, 0, 0), vl.p(-0.42, 0, 0), vl.p(-0.42, 0, -0.18), vl.p(-hl, 0, -0.18))], z0, z0 + 2.15)
        prisma("wit", [Vector((p.x, p.y, 0)) for p in (vl.p(0.42, 0, 0), vl.p(hl, 0, 0), vl.p(hl, 0, -0.18), vl.p(0.42, 0, -0.18))], z0, z0 + 2.15)
        prisma("wit", [Vector((p.x, p.y, 0)) for p in (vl.p(-0.42, 0, 0), vl.p(0.42, 0, 0), vl.p(0.42, 0, -0.18), vl.p(-0.42, 0, -0.18))], z0 + 1.7, z0 + 2.15)
        paneel("zellige", vl, -0.92, -0.5, z0 + 0.25, z0 + 1.9, 0.01, 1.2, 1.2); paneel("zellige", vl, 0.5, 0.92, z0 + 0.25, z0 + 1.9, 0.01, 1.2, 1.2)
        om = spitsboog(0, 0.84, z0, z0 + 1.35, 8, 0.6)
        strip("lijst", vl, om, 0.08, 0.05)
    blok("donker", 0.8, z0, z0 + 2.1)
    blok("lijst", hl + 0.12, z0 + 2.15, z0 + 2.34)
    # geribde turquoise koepel + spits met halve maan
    zk = z0 + 2.34
    lathe("lijst", [(0.98, 0.0), (0.98, 0.2), (0.9, 0.2)], zk, 24, (C.x, C.y))
    prof = [(0.95, 0.0), (1.07, 0.3), (1.1, 0.65), (1.04, 1.0), (0.86, 1.35), (0.6, 1.65), (0.34, 1.88), (0.14, 2.04), (0.05, 2.1), (0.0, 2.12)]
    SEG = 32
    ringen = [[C + Vector((r * (1 + 0.035 * math.cos(16 * math.pi * k / SEG)) * math.cos(2 * math.pi * k / SEG),
                           r * (1 + 0.035 * math.cos(16 * math.pi * k / SEG)) * math.sin(2 * math.pi * k / SEG), zk + 0.2 + z)) for k in range(SEG)] for r, z in prof]
    for a, b in zip(ringen, ringen[1:]):
        for k in range(SEG): quad("koepel", [a[k], a[(k + 1) % SEG], b[(k + 1) % SEG], b[k]])
    top = zk + 0.2 + 2.1
    lathe("goud", [(0.07, 0.0), (0.035, 0.1), (0.035, 2.0), (0.0, 2.1)], top - 0.05, 10, (C.x, C.y))
    for dz, r in ((0.3, 0.13), (0.7, 0.1), (1.05, 0.07)):
        lathe("goud", [(r * math.sin(math.pi * k / 8), -r * math.cos(math.pi * k / 8)) for k in range(9)], top + dz, 12, (C.x, C.y))
    # halve maan (vlak in het oost-west vlak, dubbelzijdig, met dikte)
    mz = top + 1.55; R1, R2 = 0.32, 0.25
    buiten = [(R1 * math.cos(a), R1 * math.sin(a)) for a in [math.pi * (0.15 + 0.7 * k / 16) * 2 - math.pi / 2 for k in range(17)]]
    binnen = [(R2 * math.cos(a) + 0.12, R2 * math.sin(a)) for a in [math.pi * (0.15 + 0.7 * k / 16) * 2 - math.pi / 2 for k in range(17)]][::-1]
    om = buiten + binnen
    for dy in (0.025, -0.025):
        pts = [C + Vector((x, dy, mz + y)) for x, y in om]
        cx = sum(p.x for p in pts) / len(pts); cz = sum(p.z for p in pts) / len(pts)
        for i in range(len(buiten) - 1):
            a, b = Vector((C.x + buiten[i][0], C.y + dy, mz + buiten[i][1])), Vector((C.x + buiten[i + 1][0], C.y + dy, mz + buiten[i + 1][1]))
            c_, d_ = Vector((C.x + binnen[-1 - i][0], C.y + dy, mz + binnen[-1 - i][1])), Vector((C.x + binnen[-2 - i][0], C.y + dy, mz + binnen[-2 - i][1]))
            q = [a, b, d_, c_]; quad("goud", q if dy > 0 else q[::-1])


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in T["G"].items():
        if not bm.faces: continue
        vast = rol in T["OVERLAY"]
        if not vast and rol not in ("raam", "deur"): bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        uvl = bm.loops.layers.uv.verify(); s = T["UVS"][rol]
        for f in ([] if vast else bm.faces):
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.y / s, co.z / s) if ax == 0 else (co.x / s, co.z / s) if ax == 1 else (co.x / s, co.y / s)
        me = bpy.data.meshes.new("FM_minaret_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_minaret_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "minaret"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 700, 1100
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 35
    for o in bpy.data.objects:
        if o.get("deel") not in ("minaret", None): o.hide_render = True
    p = L(45.0, -322.0) + Vector((0, 0, 1.7)); q = C + Vector((0, 0, 12.0))
    cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(uit, "minaret.png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[04_minaret] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "04_minaret"); os.makedirs(uit, exist_ok=True); render(uit)


main()
