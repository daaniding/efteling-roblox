"""07_koepelgebouw: stap 6 — het gebouwtje met de koepels tussen het ingangsgebouw en het hoofdgebouw.
Luchtfoto (ref/luchtfoto): laag blok met kantelen x -2..12,5, y -308,5..-318,5 (AHN 4,6 m), verhoogd vierkant x 5..11,5,
y -308,5..-315 (AHN 6 m), witte koepel ~4 m op de oosthoek van het hoofdgebouw rond (-3,5; -310,5) (AHN-top 13,9 m), kleine witte
koepel (~2 m) rond (-2,5; -316,5). Fmplein1986.jpg (achter het ingangsgebouw): vierkant hoektorentje met boogopeningen en een
crèmekleurige uikoepel met gouden spits, kleine witte koepel met gouden spits op een wit blokje, kantelenmuren met rechthoekige
kantelen. Modelstelsel = 02/03. Deel "koepelgebouw". Gebruik: blender --background --python build/07_koepelgebouw.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]
L, prisma, lathe, quad, strip, raam, Vlak, spitsboog, vul = (G3[k] for k in ("L", "prisma", "lathe", "quad", "strip", "raam", "Vlak", "spitsboog", "vul"))
wand = G6["wand"]
OWNER = "phase:07_koepelgebouw"
T["KLEUR"].update({"koepel_creme": (0.9, 0.84, 0.68), "wit": (0.95, 0.94, 0.9), "gangmuur": (0.92, 0.85, 0.72), "vloertegel": (0.65, 0.42, 0.33)})
T["UVS"].update({"koepel_creme": 2.0, "wit": 9.0, "gangmuur": 4.0, "vloertegel": 2.0})
for r in T["KLEUR"]: T["G"][r] = bmesh.new()


def spits(c, top, h=1.3, maan=False):
    lathe("goud", [(0.07, 0.0), (0.035, 0.1), (0.035, h), (0.0, h + 0.1)], top - 0.03, 10, (c.x, c.y))
    for dz, r in ((0.22, 0.11), (0.5, 0.08), (0.75, 0.06)):
        lathe("goud", [(r * math.sin(math.pi * k / 8), -r * math.cos(math.pi * k / 8)) for k in range(9)], top + dz, 12, (c.x, c.y))


def uikoepel(rol, c, z0, r, h):
    prof = [(r * 0.92, 0.0), (r * 1.05, 0.18 * h), (r * 1.08, 0.36 * h), (r * 0.95, 0.55 * h), (r * 0.66, 0.72 * h), (r * 0.36, 0.86 * h), (r * 0.12, 0.96 * h), (0.0, h)]
    lathe(rol, prof, z0, 32, (c.x, c.y))


def G6_kant(x0, lg):
    """rechthoekige kantelen op de latei boven de deur (zelfde stijl als de muur ernaast)"""
    vl = Vlak(L(x0 + lg, -316.0), Vector((-1, 0, 0)), Vector((0, -1, 0)))
    G6["kantelen_recht"](vl, lg, 2.8)


def bouw():
    # laag blok met kantelen (gevels tegen de klok in: noord west->oost, oost noord->zuid, zuid oost->west); loopt 0,3 m het
    # hoofdgebouw in (x -6,8)
    noord = wand([(-6.8, -308.5), (12.5, -308.5)], 4.6, 10.0, ramen=[(0, 9.0, 1.6, 2.9), (0, 12.5, 1.6, 2.9), (0, 16.5, 1.6, 2.9)])
    wand([(12.5, -308.5), (12.5, -318.5)], 4.6, 0.4, ramen=[(0, 5.0, 1.6, 2.9)])
    wand([(12.5, -318.5), (-6.8, -318.5)], 4.6, 0.4, ramen=[(0, 6.0, 1.6, 2.9), (0, 12.0, 1.6, 2.9)])
    quad("dak", [L(-6.6, -318.05) + Vector((0, 0, 4.68)), L(12.05, -318.05) + Vector((0, 0, 4.68)), L(12.05, -308.8) + Vector((0, 0, 4.68)), L(-6.6, -308.8) + Vector((0, 0, 4.68))])   # 8 cm boven de muren
    # laag bijgebouw tussen koepelgebouw en ingangsgebouw (AHN 2,7-3,1 m, luchtfoto donker dak): x 9,7..17,5, y -300,9..-316;
    # loopt 0,4 m het ingangsgebouw in; kern + dunne gevels + dak 8 cm boven de muren (Daan: "moet dit connecten of komt daar nog iets")
    # binnenkant (Daan: "de uitgang"; Eftepedia: sinds 1995 is de attractie-uitgang "via een halletje direct verbonden aan de winkel"):
    # het bijgebouw is hol en vormt dat halletje: van de open gang (binnenplaatsje) via een deur in de zuidgevel naar De Bazaar
    wand([(9.7, -300.9), (17.9, -300.9)], 2.8, 0.4, ramen=[(0, 2.5, 0.9, 2.0), (0, 5.5, 0.9, 2.0)])
    wand([(9.7, -308.5), (9.7, -300.9)], 2.8, 0.4, ramen=[(0, 3.8, 0.9, 2.0)])
    wand([(17.9, -316.0), (16.0, -316.0)], 2.8, 0.4)
    wand([(14.4, -316.0), (12.5, -316.0)], 2.8, 0.4)
    prisma("stuc", [L(14.3, -316.0), L(16.1, -316.0), L(16.1, -315.6), L(14.3, -315.6)], 2.3, 2.8)   # latei boven de deur
    G6_kant(14.4, 1.6)
    dz = Vlak(L(16.0, -316.0), Vector((-1, 0, 0)), Vector((0, -1, 0)))
    strip("lijst", dz, [(-0.1, 0.0), (-0.1, 2.38), (1.7, 2.38), (1.7, 0.0)], 0.18, 0.08)
    prisma("gangmuur", [L(12.5, -308.5), L(12.9, -308.5), L(12.9, -301.3), L(12.5, -301.3)], 0.0, 2.5)   # afsluiting westkant halletje
    prisma("vloertegel", [L(12.9, -315.6), L(17.6, -315.6), L(17.6, -301.3), L(12.9, -301.3)], -0.25, 0.12)
    prisma("vloertegel", [L(14.4, -316.05), L(16.0, -316.05), L(16.0, -315.55), L(14.4, -315.55)], -0.25, 0.12)  # drempel
    prisma("gangmuur", [L(12.5, -316.0), L(17.6, -316.0), L(17.6, -300.9), L(12.5, -300.9)], 2.45, 2.6)   # plafond halletje
    # open gang (binnenplaatsje) tussen de uitgang van de instaphal en het halletje: tegelvloer
    prisma("vloertegel", [L(12.5, -321.75), L(17.4, -321.75), L(17.4, -316.0), L(12.5, -316.0)], -0.25, 0.12)
    quad("dak", [L(10.15, -315.55) + Vector((0, 0, 2.88)), L(17.4, -315.55) + Vector((0, 0, 2.88)), L(17.4, -301.35) + Vector((0, 0, 2.88)), L(10.15, -301.35) + Vector((0, 0, 2.88))])
    # verhoogd vierkant (AHN 6 m), eenvoudige witte rand
    wand([(5.0, -308.3), (11.6, -308.3)], 6.0, 6.8)
    # hoektorentje op de oosthoek van het hoofdgebouw: vierkante voet tot boven het dak, open stage met boogopeningen,
    # hoofdgestel, crème uikoepel met gouden spits (top 13,9 m)
    c = L(-4.0, -310.6); hw = 2.0
    prisma("stuc", [c + Vector((sx * hw, sy * hw, 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 0.0, 8.7)
    zt0, zt1 = 8.7, 10.9
    for N in (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((-1, 0, 0)), Vector((0, -1, 0))):
        U = Vector((-N.y, N.x, 0)) * -1                 # buiten = links: U x V = -N
        vl = Vlak(c + N * hw - U * hw, U, N)
        for u0, u1 in ((0.0, 0.55), (2 * hw - 0.55, 2 * hw)):
            prisma("wit", [Vector((p.x, p.y, 0)) for p in (vl.p(u0, 0, 0), vl.p(u1, 0, 0), vl.p(u1, 0, -0.35), vl.p(u0, 0, -0.35))], zt0, zt1)
        om = spitsboog(hw, 2 * hw - 1.1, zt0, zt0 + 1.35, 10, 0.62)
        bovenk = lambda u: max([v for (a, v) in om[1:-1] if abs(a - u) < 0.2] or [zt0 + 1.35])
        us = [0.55 + (2 * hw - 1.1) * j / 20 for j in range(21)]
        def boog_v(u):
            pts = om[1:-1]
            for (a0, b0), (a1, b1) in zip(pts, pts[1:]):
                if min(a0, a1) <= u <= max(a0, a1) and a1 != a0: return b0 + (b1 - b0) * (u - a0) / (a1 - a0)
            return zt0 + 1.35
        for ua, ub in zip(us, us[1:]):
            ba, bb = boog_v(ua), boog_v(ub)
            quad("stucvlak", [vl.p(ua, ba, 0), vl.p(ub, bb, 0), vl.p(ub, zt1, 0), vl.p(ua, zt1, 0)][::-1])
            quad("stucvlak", [vl.p(ua, ba, -0.35), vl.p(ua, zt1, -0.35), vl.p(ub, zt1, -0.35), vl.p(ub, bb, -0.35)][::-1])
            quad("stucvlak", [vl.p(ua, ba, 0), vl.p(ua, ba, -0.35), vl.p(ub, bb, -0.35), vl.p(ub, bb, 0)][::-1])
        strip("lijst", vl, om[1:-1], 0.12, 0.06)
    prisma("raam", [c + Vector((sx * (hw - 0.6), sy * (hw - 0.6), 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], zt0, zt1 - 0.05)
    prisma("lijst", [c + Vector((sx * (hw + 0.15), sy * (hw + 0.15), 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], zt1, zt1 + 0.35)
    prisma("lijst", [c + Vector((sx * (hw - 0.1), sy * (hw - 0.1), 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], zt1 + 0.35, zt1 + 0.55)
    uikoepel("koepel_creme", c, zt1 + 0.55, 1.75, 2.35)
    spits(c, zt1 + 0.55 + 2.35, 1.0)
    # kleine witte koepel op een wit blokje (dak van het lage blok)
    c2 = L(-2.5, -316.3)
    prisma("wit", [c2 + Vector((sx * 0.85, sy * 0.85, 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 4.5, 5.6)
    prisma("lijst", [c2 + Vector((sx * 0.95, sy * 0.95, 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 5.6, 5.75)
    uikoepel("koepel_wit", c2, 5.75, 0.85, 1.05)
    spits(c2, 6.8, 0.9)


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
        me = bpy.data.meshes.new("FM_koepelgebouw_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_koepelgebouw_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "koepelgebouw"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 1200, 800
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 28
    p = L(26.0, -300.0) + Vector((0, 0, 3.0)); q = L(2.0, -312.0) + Vector((0, 0, 6.0))
    cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(uit, "koepelgebouw.png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[07_koepelgebouw] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "07_koepelgebouw"); os.makedirs(uit, exist_ok=True); render(uit)


main()
