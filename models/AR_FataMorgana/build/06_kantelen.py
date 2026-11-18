"""06_kantelen: stap 5 — de kantelenmuren bij de minaret (Fmplein1986.jpg, Fatamorganaingang1987.jpg; AHN ref/ahn).
  lage muur  : tussen het ingangsgebouw en de minaret, x 16,5, y -314,2 .. -326,7, 3,3 m hoog (AHN 2,7-3,4 m), rechthoekige kantelen
  hoog blok  : links (zuid) van de minaret, oostgevel x 17,1 van y -322 tot -336 (achter de minaret door), 5,4 m hoog (AHN), terug
               tot het hoofdgebouw (x -6,5); rechthoekige kantelen, een paar boogvensters, verweringsvlekken (02_toren.verwering)
Modelstelsel = 02/03 (oorsprong park -40; -295). Deel "kantelen". Gebruik: blender --background --python build/06_kantelen.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F3 = os.path.join(D, "build", "03_noordgevel.py")
G3 = {"__file__": F3, "__name__": "lib"}
exec(compile(open(F3).read().rsplit("\nmain()", 1)[0], F3, "exec"), G3)
T = G3["T"]; L, prisma, lathe, quad, strip, raam, Vlak, muur = (G3[k] for k in ("L", "prisma", "lathe", "quad", "strip", "raam", "Vlak", "muur"))
OWNER = "phase:06_kantelen"
for r in T["KLEUR"]: T["G"][r] = bmesh.new()


def kantelen_recht(vl, lengte, z, w=0.55, h=0.6, dik=0.4, tussen=0.45):
    """eenvoudige rechthoekige kantelen (Fmplein1986: de muur links van de minaret)"""
    n = max(1, int((lengte + tussen) / (w + tussen))); st = (lengte - n * w) / max(1, n - 1)
    for k in range(n):
        u0 = k * (w + st)
        prisma("stuc", [Vector((p.x, p.y, 0)) for p in (vl.p(u0, 0, -dik), vl.p(u0 + w, 0, -dik), vl.p(u0 + w, 0, 0), vl.p(u0, 0, 0))], z, z + h)


def wand(punten, hoogte, diep, ramen=()):
    vls = muur(punten, hoogte, diep, kantel=False, kroon=True)
    for vl, l in vls:
        kantelen_recht(vl, l, hoogte)
        G3["strip"]("lijst", vl, [(0, hoogte + 0.02), (l, hoogte + 0.02)], 0.14, 0.06)
    for i, u, v0, v1 in ramen:
        vl, l = vls[i]; raam(vl, u, 0.55, v0, v1)
    return vls


def bouw():
    # lage muur ingang -> minaret (noord naar zuid: voorkant = oost, naar het plein)
    # loopt 0,4 m het ingangsgebouw en 0,2 m de minaret in (Daan: "je laat nog steeds een beetje ruimte zitten")
    wand([(17.9, -313.6), (17.9, -326.9)], 3.3, 0.5, ramen=[(0, 6.6, 1.2, 2.2)])
    # hoog blok: oostgevel noord en zuid van de minaret, achter de minaret door gevuld
    wand([(17.5, -322.0), (17.5, -326.9)], 5.4, 24.0)
    wand([(17.5, -331.1), (17.5, -336.0)], 5.4, 24.0, ramen=[(0, 2.6, 2.6, 3.9)])
    prisma("stuc", [L(-6.5, -331.4), L(17.4, -331.4), L(17.4, -326.6), L(-6.5, -326.6)], 0.0, 5.38)
    # noordgevel van het blok (naar de binnenplaats, west -> oost: voorkant = noord) en zuidgevel (oost -> west: voorkant = zuid)
    wand([(-6.5, -322.0), (17.5, -322.0)], 5.4, 0.4, ramen=[(0, 8.0, 2.6, 3.9), (0, 15.0, 2.6, 3.9)])
    wand([(17.5, -336.0), (-6.5, -336.0)], 5.4, 0.4, ramen=[(0, 6.0, 2.6, 3.9), (0, 12.0, 2.6, 3.9)])
    quad("dak", [L(-6.4, -335.6) + Vector((0, 0, 5.36)), L(16.7, -335.6) + Vector((0, 0, 5.36)), L(16.7, -322.4) + Vector((0, 0, 5.36)), L(-6.4, -322.4) + Vector((0, 0, 5.36))])


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in T["G"].items():
        if not bm.faces: continue
        vast = rol in T["OVERLAY"]
        if not vast and rol not in ("raam", "deur", "dak"):
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        uvl = bm.loops.layers.uv.verify(); s = T["UVS"][rol]
        for f in ([] if vast else bm.faces):
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.y / s, co.z / s) if ax == 0 else (co.x / s, co.z / s) if ax == 1 else (co.x / s, co.y / s)
        me = bpy.data.meshes.new("FM_kantelen_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_kantelen_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "kantelen"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 1200, 800
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 28
    for o in bpy.data.objects:
        if o.get("deel") not in ("kantelen", "minaret", "ingang", None): o.hide_render = True
    p = L(42.0, -327.0) + Vector((0, 0, 1.7)); q = L(18.0, -325.0) + Vector((0, 0, 5.0))
    cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(uit, "kantelen.png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[06_kantelen] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "06_kantelen"); os.makedirs(uit, exist_ok=True); render(uit)


main()
