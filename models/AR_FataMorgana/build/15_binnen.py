"""15_binnen: binnenkant stap 2 — de gang van het halletje in de minaretvoet naar de instaphal (POV-video 2025, 30 s; video
"wachtrij + onride 2020": crèmekleurige gang, groene kielbogen, daarna de gaanderij rond de instaphal). De gang loopt vanaf de
groene kielboog in de westmuur van het halletje (04_minaret) naar het westen, binnen het (nu holle) kantelenblok (06_kantelen).
Aan het eind een groene kielboog met een donkere doorgang: daar komt de gaanderij van de instaphal (volgende stap).
Modelstelsel = 02/03. Deel "binnen". Gebruik: blender --background --python build/15_binnen.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]
L, prisma, lathe, quad, strip, raam, Vlak, spitsboog, vul = (G3[k] for k in ("L", "prisma", "lathe", "quad", "strip", "raam", "Vlak", "spitsboog", "vul"))
OWNER = "phase:15_binnen"
T["KLEUR"].update({"groen": (0.25, 0.58, 0.5), "poort": (0.05, 0.05, 0.07), "fries": (0.2, 0.3, 0.6), "rood": (0.73, 0.26, 0.16), "wit": (0.95, 0.94, 0.9), "vloertegel": (0.65, 0.42, 0.33),
                   "matglas": (0.93, 0.95, 0.96), "schildering": (0.8, 0.75, 0.6), "koepel_blauw": (0.45, 0.68, 0.84), "hekgroen": (0.25, 0.36, 0.32), "donker": (0.12, 0.13, 0.15), "hout": (0.32, 0.2, 0.12), "bord": (0.95, 0.91, 0.8), "bollamp": (1.0, 0.78, 0.5)})
T["UVS"].update({"groen": 1.0, "poort": 1.0, "fries": 1.0, "rood": 1.0, "wit": 9.0, "vloertegel": 2.0, "matglas": 1.0, "schildering": 1.0, "koepel_blauw": 1.0, "hekgroen": 1.0, "donker": 1.0, "bord": 1.0, "bollamp": 1.0})

for r in T["KLEUR"]: T["G"][r] = bmesh.new()

XO, XW = 17.7, 10.6           # oostkant (binnenkant westmuur halletje), westeinde gang
YS, YN = -330.2, -327.8        # binnenkant zuid- en noordwand (2,4 m breed)
HG = 3.0                       # hoogte gang


def bouw():
    # vloer (zelfde tegels als halletje en wachtrij; sluit aan op de halletjevloer bij x 17,7) en plafond
    prisma("vloertegel", [L(XW, YS), L(XO, YS), L(XO, YN), L(XW, YN)], -0.25, 0.12)
    prisma("wit", [L(XW - 0.2, YS - 0.2), L(17.25, YS - 0.2), L(17.25, YN + 0.2), L(XW - 0.2, YN + 0.2)], HG, HG + 0.15)
    # wanden: crème gepleisterd, plint en lijst op 1,1 m
    for y0, y1 in ((YS - 0.2, YS), (YN, YN + 0.2)):
        prisma("wit", [L(XW - 0.2, y0), L(17.25, y0), L(17.25, y1), L(XW - 0.2, y1)], 0.0, HG)
    for y, n in ((YS, 1), (YN, -1)):
        vl = Vlak(L(XW, y), Vector((1, 0, 0)) * n, Vector((0, n, 0)))
        lg = 17.2 - XW
        u0, u1 = (0.0, lg) if n == 1 else (-lg, 0.0)
        strip("lijst", vl, [(u0, 0.08), (u1, 0.08)], 0.16, 0.04)
        strip("lijst", vl, [(u0, 1.1), (u1, 1.1)], 0.06, 0.03)
    # westeinde: muur met een groene kielboog en een donkere doorgang (naar de gaanderij van de instaphal, volgende stap)
    prisma("wit", [L(XW - 0.2, YS - 0.2), L(XW, YS - 0.2), L(XW, YN + 0.2), L(XW - 0.2, YN + 0.2)], 0.0, HG)
    ve = Vlak(L(XW, -329.0), Vector((0, -1, 0)), Vector((1, 0, 0)))   # naar het oosten kijkend vlak, u = -(y + 329)
    w, vs = 1.6, 1.95
    boog = spitsboog(0.0, w, 0.0, vs, 10, 0.55)[1:-1]
    top = max(v for _, v in boog); hl = len(boog) // 2
    boog = [p for p in boog[:hl] if p[1] < top - 0.1] + [(0.0, top + 0.16)] + [p for p in boog[hl:] if p[1] < top - 0.1]
    om = [(-w / 2, 0.0)] + [(-w / 2, vs * k / 4) for k in range(1, 4)] + boog + [(w / 2, vs * k / 4) for k in range(3, 0, -1)] + [(w / 2, 0.0)]
    vul("poort", ve, om, 0.02)
    strip("groen", ve, om[1:-1], 0.22, 0.08); strip("groen", ve, [om[0], om[1]], 0.22, 0.08); strip("groen", ve, [om[-2], om[-1]], 0.22, 0.08)
    # twee wandlampjes (koper) tussen de lijsten
    for x in (12.6, 15.6):
        for y, n in ((YS, 1), (YN, -1)):
            p = L(x, y + 0.12 * n)
            lathe("goud", [(r, z) for r, z in ((0.0, 0.0), (0.05, 0.03), (0.09, 0.12), (0.08, 0.24), (0.04, 0.3), (0.0, 0.32))], 2.15, 8, (p.x, p.y))
            prisma("goud", [L(x - 0.015, y), L(x + 0.015, y), L(x + 0.015, y + 0.12 * n), L(x - 0.015, y + 0.12 * n)][:: n], 2.45, 2.48)


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in T["G"].items():
        if not bm.faces: continue
        vast = rol in T["OVERLAY"]
        if not vast and rol not in ("raam", "deur", "dak", "stucvlak", "poort"):
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        uvl = bm.loops.layers.uv.verify(); s = T["UVS"][rol]
        for f in ([] if vast else bm.faces):
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.y / s, co.z / s) if ax == 0 else (co.x / s, co.z / s) if ax == 1 else (co.x / s, co.y / s)
        me = bpy.data.meshes.new("FM_binnen_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_binnen_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "binnen"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = False
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 1100, 800
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 22
    p = L(20.6, -329.0) + Vector((0, 0, 1.6)); q = L(11.0, -329.0) + Vector((0, 0, 1.5))
    cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(uit, "gang.png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[15_binnen] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "15_binnen"); os.makedirs(uit, exist_ok=True); render(uit)


main()
