"""18_route: de vaarroute van Fata Morgana met de scènekamers, ALLEEN als ruwe ruimtes (Daan 18 nov: "alleen ff de route maken met
de kamers niet hoe ze eruit zien"). Vorm uit de Eftepedia-plattegrond via build/18p_routeplan.py (ref/route_plan.npz):
  - vaargoot (blauw op de plattegrond, secties 1-14): bodem op z -3,7; water = Terrain-water tot z -3,2 (in Studio, plaats_routewater)
  - scènevlakken (zandkleur = de kamers waar later de scènes komen): verhoogd toneel tot z -2,6
  - muren langs de buitenrand van elke kamer en scheidingsmuren tussen kamers die op de plattegrond naast elkaar liggen maar ver uit
    elkaar op de route (bv. sectie 4 en 11); enkelzijdige vlakken naar de kamer; plafond op z -0,05 (de route ligt onder de begane grond,
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


def vlak(rol, pts, wil):
    bm = T["G"][rol]; f = bm.faces.new([bm.verts.new(q) for q in pts]); f.normal_update()
    if f.normal.dot(wil) < 0: f.normal_flip()


def plat(rol, x0, y0, x1, y1, z, op):
    x0, y0, x1, y1 = klem(x0, y0, x1, y1)
    if x1 - x0 < 0.01 or y1 - y0 < 0.01: return
    vlak(rol, [L(x0, y0) + Vector((0, 0, z)), L(x1, y0) + Vector((0, 0, z)), L(x1, y1) + Vector((0, 0, z)), L(x0, y1) + Vector((0, 0, z))],
         Vector((0, 0, 1 if op else -1)))


def wand(rol, seg, z0, z1, uitw, naar_binnen):
    """verticaal vlak langs een contourlijn; uitw = verschuiving naar buiten (m); normaal naar binnen of buiten"""
    ax, ay, bx, by, nx, ny = seg
    a, b, n = Vector((ax, ay, 0)), Vector((bx, by, 0)), Vector((nx, ny, 0))
    t = (b - a).normalized(); a -= t * 0.05; b += t * 0.05
    a += n * uitw; b += n * uitw
    pa, pb = L(a.x, a.y), L(b.x, b.y)
    vlak(rol, [pa + Vector((0, 0, z0)), pb + Vector((0, 0, z0)), pb + Vector((0, 0, z1)), pa + Vector((0, 0, z1))], -n if naar_binnen else n)


def bouw():
    P = np.load(os.path.join(D, "ref", "route_plan.npz"))
    for x0, y0, x1, y1 in P["r_blauw"]: plat("routebodem", x0, y0, x1, y1, ZB, True)
    for x0, y0, x1, y1 in P["r_zand"]: plat("toneel", x0, y0, x1, y1, ZT, True)
    for x0, y0, x1, y1 in P["r_uni"]: plat("routeplafond", x0, y0, x1, y1, ZP0, False)
    for seg in P["toneelrand"]: wand("toneel", seg, ZB, ZT, 0.0, False)          # zijkant toneel naar het water
    for seg in P["muren"]: wand("routewand", seg, ZB - 0.05, ZP0 + 0.01, 0.05, True)   # muren en scheidingsmuren, naar de kamer


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol in KL:
        bm = T["G"][rol]
        if not bm.faces: continue
        bm.normal_update()                                                       # vlakken hebben al de goede kant
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
