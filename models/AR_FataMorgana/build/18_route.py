"""18_route: de vaarroute van Fata Morgana met de scènekamers, ALLEEN als ruwe ruimtes (Daan 18 nov: "alleen ff de route maken met
de kamers niet hoe ze eruit zien"). Vorm uit de Eftepedia-plattegrond via build/18p_routeplan.py (ref/route_plan.npz):
  - vaargoot (blauw op de plattegrond, secties 1-14): bodem op z -3,7; water = Terrain-water tot z -3,2 (in Studio, plaats_routewater)
  - scènevlakken (zandkleur = de kamers waar later de scènes komen): verhoogd toneel tot z -2,6
  - muren langs de buitenrand van vaargoot+kamers (0,3 m dik), plafond z -0,05..0,12 (de route ligt onder de begane grond,
    op hetzelfde waterpeil als de instaphal); bij onze hal geen extra muur (die heeft al doorvaarten in de noord- en westmuur)
Nog niets aan aankleding of scènes. Modelstelsel = 02/03. Deel "route". Gebruik: blender --background --python build/18_route.py"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]
L, prisma = G3["L"], G3["prisma"]
OWNER = "phase:18_route"
KL = {"routebodem": (0.08, 0.09, 0.1), "toneel": (0.32, 0.27, 0.22), "routewand": (0.3, 0.27, 0.24), "routeplafond": (0.06, 0.06, 0.07)}
for r, k in KL.items(): T["KLEUR"][r] = k; T["UVS"][r] = 4.0; T["G"][r] = bmesh.new()
ZB, ZW, ZT, ZP0, ZP1 = -3.7, -3.2, -2.6, -0.05, 0.12


def klem(x0, y0, x1, y1):
    """niets in onze instaphal laten uitsteken (doorvaarten stoppen in de muur)"""
    if x1 > -3.8 and y0 < -323.3:
        if x0 < -3.55: x1 = min(x1, -3.55)
        else: y0 = max(y0, -323.5)
    return x0, y0, x1, y1


def box(rol, x0, y0, x1, y1, z0, z1):
    x0, y0, x1, y1 = klem(x0, y0, x1, y1)
    if x1 - x0 < 0.01 or y1 - y0 < 0.01: return
    prisma(rol, [L(x0, y0), L(x1, y0), L(x1, y1), L(x0, y1)], z0, z1)


def bouw():
    P = np.load(os.path.join(D, "ref", "route_plan.npz"))
    for x0, y0, x1, y1 in P["r_blauw"]: box("routebodem", x0, y0, x1, y1, ZB - 0.2, ZB)
    for x0, y0, x1, y1 in P["r_zand"]: box("toneel", x0, y0, x1, y1, ZB - 0.2, ZT)
    for x0, y0, x1, y1 in P["r_uni"]: box("routeplafond", x0, y0, x1, y1, ZP0, ZP1)
    for ax, ay, bx, by, nx, ny in P["muren"]:
        a, b = Vector((ax, ay, 0)), Vector((bx, by, 0)); t = (b - a).normalized(); n = Vector((nx, ny, 0))
        a -= t * 0.15; b += t * 0.15                                      # hoeken dicht
        prisma("routewand", [L(*(a + n * 0.12).xy), L(*(b + n * 0.12).xy), L(*(b + n * 0.42).xy), L(*(a + n * 0.42).xy)], ZB - 0.2, ZP1)


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol in KL:
        bm = T["G"][rol]
        if not bm.faces: continue
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update()
        uvl = bm.loops.layers.uv.verify()
        for f in bm.faces:
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co; lp[uvl].uv = (co.y / 4, co.z / 4) if ax == 0 else (co.x / 4, co.z / 4) if ax == 1 else (co.x / 4, co.y / 4)
        me = bpy.data.meshes.new("FM_route_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_route_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "route"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*KL[rol], 1); me.materials.append(m); col.objects.link(o)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[18_route] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")


main()
