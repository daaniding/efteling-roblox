"""09_westkant: stap 8 — de westkant van het hoofdgebouw (AHN ref/ahn, luchtfoto ref/luchtfoto).
AHN (boven maaiveld): hal 8,2 m, westgevel rond x -72,5; hoger westblok 10,1 m over x -73..-52, y -325..-338 met een
torentje op de noordwesthoek (top 12,4 m) en een hogere hoek zuidwest (11,2 m); steunblok 8,8 m tegen de gevel op
x -74,5..-73, y -334..-338; laag aanbouwtje 3,2 m op x -77,5..-73,5, y -310..-321 (luchtfoto: donker plat dak).
De witte ronde vorm op de luchtfoto bij (-78; -333) staat niet in het AHN (0 m): parasol/tent, niet gebouwd.
Alles overlapt 0,2-0,4 m in de buurdelen (geen kieren), daken 8 cm boven de muurbovenkanten (geen z-fighting).
Modelstelsel = 02/03. Deel "westkant". Gebruik: blender --background --python build/09_westkant.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]
L, prisma, quad, raam, spitsboog, vul, strip = (G3[k] for k in ("L", "prisma", "quad", "raam", "spitsboog", "vul", "strip"))
wand = G6["wand"]
OWNER = "phase:09_westkant"
for r in T["KLEUR"]: T["G"][r] = bmesh.new()

XW = -73.3          # buitenkant westgevel (romp eindigt op x -73; muur 0,5 diep loopt er 0,2 in)


def dak(x0, y0, x1, y1, z):
    quad("dak", [L(x0, y0) + Vector((0, 0, z)), L(x1, y0) + Vector((0, 0, z)), L(x1, y1) + Vector((0, 0, z)), L(x0, y1) + Vector((0, 0, z))])


def bouw():
    # westgevel van de hal (zuid -> noord: buiten = west), zelfde getrapte kantelen en kroonlijst als de noordgevel
    hal = G3["muur"]([(XW, -325.2), (XW, -296.9)], 8.0, 0.5)
    vl, l = hal[0]
    for u in (2.2, 18.6, 26.2): raam(vl, u, 0.6, 4.6, 5.9)                 # bovenste rij
    for u in (6.5, 9.8, 13.1): raam(vl, u, 0.55, 4.8, 6.0)                       # boven het aanbouwtje
    for u in (18.6, 26.2): raam(vl, u, 0.55, 1.5, 2.6)
    G3["erker"](vl, 22.4, 4.6, 1.3, 1.4, 0.7); G3["rooster"](vl, 22.4, 4.85, 1.1, 0.85, 0.73)

    # hoger westblok (10,1 m): dunne gevels rondom, kern alleen boven het haldak, dak 8 cm boven de muren
    wand([(-73.4, -324.9), (-51.8, -324.9)], 10.1, 0.5, ramen=[(0, 6.0, 8.6, 9.4), (0, 12.0, 8.6, 9.4), (0, 18.0, 8.6, 9.4)])
    wand([(-51.8, -324.9), (-51.8, -339.4)], 10.1, 0.5, ramen=[(0, 7.2, 8.6, 9.4)])
    wand([(-51.8, -339.4), (-73.4, -339.4)], 10.1, 0.5,
         ramen=[(0, u, 6.2, 7.6) for u in (3.5, 8.0, 12.5, 17.0)] + [(0, u, 2.0, 3.4) for u in (5.7, 14.7)])
    wand([(-73.4, -339.4), (-73.4, -324.9)], 10.1, 0.5, ramen=[(0, 7.0, 6.4, 7.8)])
    prisma("stuc", [L(-72.95, -338.95), L(-52.25, -338.95), L(-52.25, -325.35), L(-72.95, -325.35)], 7.7, 9.8)
    dak(-72.85, -338.85, -52.35, -325.45, 10.18)
    # deur in de zuidgevel (achterkant, dienstingang)
    zg = G3["Vlak"](L(-51.8, -339.4), Vector((-1, 0, 0)), Vector((0, -1, 0)))
    d = spitsboog(10.2, 1.4, 0.0, 2.0, 8); vul("deur", zg, d, 0.09); strip("lijst", zg, d, 0.2, 0.14)

    # torentje op de noordwesthoek met witte koepel (AHN-top 12,4 m) en hogere hoek zuidwest (11,2 m)
    c = L(-72.3, -326.0); vls = G3["blokje"](c, 2.4, 10.1, 11.0, kantel=False)
    for v in vls: raam(v, 1.2, 0.5, 10.25, 10.65)
    G3["koepel"]("koepel_wit", c, 11.0, 1.05, 1.3, 0.12)
    G3["blokje"](L(-72.4, -338.4), 2.2, 10.1, 11.2)

    # steunblok tegen de westgevel (8,8 m), loopt 0,4 m het westblok in
    wand([(-73.0, -334.2), (-74.8, -334.2)][::-1], 8.8, 0.4)                    # noord (west -> oost)
    wand([(-74.8, -338.6), (-74.8, -334.2)], 8.8, 0.4, ramen=[(0, 2.2, 5.0, 6.2)])  # west (zuid -> noord)
    wand([(-73.0, -338.6), (-74.8, -338.6)], 8.8, 0.4)                          # zuid (oost -> west)
    prisma("stuc", [L(-74.45, -338.25), L(-73.0, -338.25), L(-73.0, -334.55), L(-74.45, -334.55)], 0.0, 8.5)
    dak(-74.4, -338.2, -73.5, -334.6, 8.88)

    # laag aanbouwtje (3,2 m) tegen de westgevel, loopt 0,3 m de gevel in
    wand([(-77.6, -309.6), (-73.0, -309.6)], 3.2, 0.4, ramen=[(0, 2.3, 1.0, 2.1)])
    wand([(-77.6, -321.2), (-77.6, -309.6)], 3.2, 0.4, ramen=[(0, 2.4, 1.0, 2.1), (0, 9.2, 1.0, 2.1)])
    wand([(-73.0, -321.2), (-77.6, -321.2)], 3.2, 0.4)
    prisma("stuc", [L(-77.2, -320.8), L(-73.0, -320.8), L(-73.0, -310.0), L(-77.2, -310.0)], 0.0, 2.9)
    dak(-77.15, -320.75, -73.4, -310.05, 3.28)
    wv = G3["Vlak"](L(-77.6, -321.2), Vector((0, 1, 0)), Vector((-1, 0, 0)))
    d = spitsboog(5.8, 1.2, 0.0, 1.8, 8); vul("deur", wv, d, 0.09); strip("lijst", wv, d, 0.2, 0.14)
    G3["muurlamp"](wv, 4.7, 2.0); G3["muurlamp"](wv, 6.9, 2.0)


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
        me = bpy.data.meshes.new("FM_westkant_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_westkant_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "westkant"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 1400, 800
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 24
    for naam, p, q in (("westkant", L(-100.0, -330.0) + Vector((0, 0, 6.0)), L(-70.0, -318.0) + Vector((0, 0, 5.0))),
                       ("westkant_zw", L(-92.0, -356.0) + Vector((0, 0, 8.0)), L(-66.0, -330.0) + Vector((0, 0, 6.0)))):
        cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(uit, naam + ".png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[09_westkant] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "09_westkant"); os.makedirs(uit, exist_ok=True); render(uit)


main()
