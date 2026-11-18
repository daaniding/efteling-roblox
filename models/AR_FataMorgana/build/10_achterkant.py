"""10_achterkant: stap 9 — de achterkant (zuid) van het hoofdgebouw (AHN ref/ahn, luchtfoto ref/luchtfoto).
AHN (boven maaiveld): zuidgevel hal 8,1 m op y -339 (x -52..-37,5 en -28..-16), uitbouw tot y -341,2 over x -49,5..-37,5;
laag aanbouwtje 2,9 m x -45..-37,5, y -341..-344,5; laag blok 4,6 m x -26,5..-16,5, y -336..-346,5 tegen het blok bij de
minaret (5,4 m); schoorsteen 10,2 m rond (-28; -338,5). Losse waarden 4-9 m rond (-30; -341) en y < -348 zijn bomen.
Alles overlapt 0,2-0,4 m in de buurdelen, daken 8 cm boven de muren. Deel "achterkant".
Gebruik: blender --background --python build/10_achterkant.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]
L, prisma, quad, raam, spitsboog, vul, strip = (G3[k] for k in ("L", "prisma", "quad", "raam", "spitsboog", "vul", "strip"))
wand = G6["wand"]
OWNER = "phase:10_achterkant"
for r in T["KLEUR"]: T["G"][r] = bmesh.new()



def dak(x0, y0, x1, y1, z):
    quad("dak", [L(x0, y0) + Vector((0, 0, z)), L(x1, y0) + Vector((0, 0, z)), L(x1, y1) + Vector((0, 0, z)), L(x0, y1) + Vector((0, 0, z))])

def bouw():
    # zuidgevel van de hal (oost -> west: buiten = zuid) met uitbouw; getrapte kantelen en kroonlijst als de noordgevel
    zg = G3["muur"]([(-15.9, -339.3), (-37.5, -339.3), (-37.5, -341.4), (-49.7, -341.4), (-49.7, -339.3), (-51.9, -339.3)], 8.0, 0.5)
    vl, l = zg[0]
    for u in (3.0, 7.5): raam(vl, u, 0.55, 5.6, 6.7)                           # boven het lage blok
    for u in (13.0, 17.0, 20.5): raam(vl, u, 0.6, 4.6, 5.9)
    for u in (14.5, 19.0): raam(vl, u, 0.55, 1.5, 2.6)
    d = spitsboog(16.8, 1.3, 0.0, 1.9, 8); vul("deur", vl, d, 0.09); strip("lijst", vl, d, 0.2, 0.14)
    G3["muurlamp"](vl, 15.7, 2.1); G3["muurlamp"](vl, 17.9, 2.1)
    vl, l = zg[2]
    raam(vl, 2.5, 0.6, 4.6, 5.9); raam(vl, 9.7, 0.6, 4.6, 5.9)
    G3["erker"](vl, 6.1, 4.4, 1.3, 1.4, 0.7); G3["rooster"](vl, 6.1, 4.65, 1.1, 0.85, 0.73)
    # kern en dak van de uitbouw (dak sluit vlak aan op het haldak, zelfde hoogte, geen overlap)
    prisma("stuc", [L(-49.3, -340.95), L(-37.9, -340.95), L(-37.9, -338.8), L(-49.3, -338.8)], 0.0, 7.7)
    dak(-49.25, -340.9, -37.95, -339.0, 8.08)
    # schoorsteen op het haldak (AHN 10,2 m)
    prisma("stuc", [L(-28.7, -338.9), L(-27.3, -338.9), L(-27.3, -337.7), L(-28.7, -337.7)], 7.5, 9.9)
    prisma("lijst", [L(-28.85, -339.05), L(-27.15, -339.05), L(-27.15, -337.55), L(-28.85, -337.55)], 9.9, 10.15)

    # laag aanbouwtje (2,9 m) tegen de uitbouw
    wand([(-37.3, -341.0), (-37.3, -344.6)], 2.9, 0.4)
    wand([(-37.3, -344.6), (-45.2, -344.6)], 2.9, 0.4, ramen=[(0, 1.6, 0.9, 1.9), (0, 6.3, 0.9, 1.9)])
    wand([(-45.2, -344.6), (-45.2, -341.0)], 2.9, 0.4)
    prisma("stuc", [L(-44.8, -344.2), L(-37.7, -344.2), L(-37.7, -341.0), L(-44.8, -341.0)], 0.0, 2.6)
    dak(-44.75, -344.15, -37.75, -341.45, 2.98)
    av = G3["Vlak"](L(-37.3, -344.6), Vector((-1, 0, 0)), Vector((0, -1, 0)))
    d = spitsboog(3.95, 1.1, 0.0, 1.7, 8); vul("deur", av, d, 0.09); strip("lijst", av, d, 0.2, 0.14)

    # laag blok (4,6 m) tussen de hal en het blok bij de minaret; loopt beide in
    wand([(-15.8, -346.5), (-26.6, -346.5)], 4.6, 0.4, ramen=[(0, u, 1.6, 2.9) for u in (2.5, 5.4, 8.3)])
    wand([(-26.6, -346.5), (-26.6, -338.8)], 4.6, 0.4, ramen=[(0, 2.0, 1.6, 2.9)])
    prisma("stuc", [L(-26.2, -346.1), L(-15.9, -346.1), L(-15.9, -338.8), L(-26.2, -338.8)], 0.0, 4.3)
    dak(-26.15, -346.05, -15.95, -339.25, 4.68)
    bv = G3["Vlak"](L(-26.6, -346.5), Vector((0, 1, 0)), Vector((-1, 0, 0)))
    d = spitsboog(4.9, 1.2, 0.0, 1.8, 8); vul("deur", bv, d, 0.09); strip("lijst", bv, d, 0.2, 0.14)
    # oostkop van de hal boven het blok bij de minaret (was kaal boven 5,4 m); onderkant zit in dat blok
    ok = G3["muur"]([(-15.4, -321.0), (-15.4, -339.5)], 8.0, 0.5)
    vl, l = ok[0]; raam(vl, 6.0, 0.55, 6.0, 7.0); raam(vl, 12.0, 0.55, 6.0, 7.0)
    zk = G3["muur"]([(-2.1, -321.5), (-15.6, -321.5)], 8.0, 0.5)               # zuidkant hal boven datzelfde blok
    vl, l = zk[0]; raam(vl, 4.0, 0.55, 6.1, 7.1); raam(vl, 9.5, 0.55, 6.1, 7.1)
    # westkop van het blok bij de minaret (was een kale kern): gevel met kantelen
    wand([(-16.1, -349.95), (-16.1, -346.3)], 5.4, 0.4)


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in T["G"].items():
        if not bm.faces: continue
        vast = rol in T["OVERLAY"]
        if not vast and rol not in ("raam", "deur", "dak", "stucvlak"):
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        uvl = bm.loops.layers.uv.verify(); s = T["UVS"][rol]
        for f in ([] if vast else bm.faces):
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.y / s, co.z / s) if ax == 0 else (co.x / s, co.z / s) if ax == 1 else (co.x / s, co.y / s)
        me = bpy.data.meshes.new("FM_achterkant_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_achterkant_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "achterkant"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 1400, 800
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 24
    for naam, p, q in (("achterkant", L(-30.0, -372.0) + Vector((0, 0, 6.0)), L(-32.0, -340.0) + Vector((0, 0, 5.0))),
                       ("achterkant_zo", L(-4.0, -366.0) + Vector((0, 0, 9.0)), L(-30.0, -340.0) + Vector((0, 0, 5.0)))):
        cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(uit, naam + ".png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[10_achterkant] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "10_achterkant"); os.makedirs(uit, exist_ok=True); render(uit)


main()
