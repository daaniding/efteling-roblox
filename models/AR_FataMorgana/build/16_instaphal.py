"""16_instaphal: binnenkant stap 3 — de instaphal met de draaischijf (Eftepedia "Wachtrij en instaphal"; video's 2020/2025).
Eftepedia: grote ruimte met centraal een draaischijf; een gaanderij met ezelsrugbogen volgt de muren en gaat halverwege richting de
draaischijf; langs het controlehok een trap af naar de draaischijf; veertien rode sloepen. Video: groene kielbogen en zuilen,
balustrade met crème panelen en bruine rozetten, rij lampjes, grote ronde houten lattenkap boven de draaischijf, water rond de
schijf, uitgang naar de rit achter een beige gordijn. Hier: in het holle kantelenblok (06), gaanderij op vloerniveau (0,12 m,
sluit aan op de gang 15_binnen), draaischijf in een verdiepte bak (dek -1,8 m, water -2,1 m). Nog GEEN beweging (Daan).
Modelstelsel = 02/03. Deel "instaphal". Gebruik: blender --background --python build/16_instaphal.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]
L, prisma, lathe, quad, strip, raam, Vlak, spitsboog, vul = (G3[k] for k in ("L", "prisma", "lathe", "quad", "strip", "raam", "Vlak", "spitsboog", "vul"))
OWNER = "phase:16_instaphal"
T["KLEUR"].update({"water": (0.12, 0.22, 0.26), "dekhout": (0.55, 0.38, 0.24), "plafond": (0.2, 0.16, 0.14), "rozet": (0.43, 0.27, 0.17), "gordijn": (0.84, 0.77, 0.63), "groenhek": (0.25, 0.58, 0.5), "groen": (0.25, 0.58, 0.5), "poort": (0.05, 0.05, 0.07), "gangmuur": (0.92, 0.85, 0.72), "gangpleister": (0.92, 0.85, 0.72), "groenneg": (0.25, 0.58, 0.5), "fries": (0.2, 0.3, 0.6), "rood": (0.73, 0.26, 0.16), "wit": (0.95, 0.94, 0.9), "vloertegel": (0.65, 0.42, 0.33),
                   "matglas": (0.93, 0.95, 0.96), "schildering": (0.8, 0.75, 0.6), "koepel_blauw": (0.45, 0.68, 0.84), "hekgroen": (0.25, 0.36, 0.32), "donker": (0.12, 0.13, 0.15), "hout": (0.32, 0.2, 0.12), "bord": (0.95, 0.91, 0.8), "bollamp": (1.0, 0.78, 0.5)})
T["UVS"].update({"water": 4.0, "dekhout": 1.5, "plafond": 4.0, "rozet": 1.0, "gordijn": 2.0, "groenhek": 1.0, "groen": 1.0, "poort": 1.0, "gangmuur": 4.0, "gangpleister": 4.0, "groenneg": 1.0, "fries": 1.0, "rood": 1.0, "wit": 9.0, "vloertegel": 2.0, "matglas": 1.0, "schildering": 1.0, "koepel_blauw": 1.0, "hekgroen": 1.0, "donker": 1.0, "bord": 1.0, "bollamp": 1.0})

for r in T["KLEUR"]: T["G"][r] = bmesh.new()

O = (-40.0, -295.0)
XW_, XE_ = -15.0, 10.4          # binnenkant west- en oostmuur van de hal (west 0,5 m naar binnen: afgerond terrein van buiten blijft achter de muur)
YS_, YN_ = -348.9, -322.6        # binnenkant zuid- en noordmuur (zuid 0,5 m naar binnen, idem)
GB = 2.6                         # breedte gaanderij (noord- en oostkant)
XB, YB = XE_ - GB, YN_ - GB      # rand van de bak (x 7,8 / y -325,2)
ZB, ZW, ZD = -2.6, -2.1, -1.8    # bodem bak, waterpeil, dek draaischijf
CX, CY = (XW_ + XB) / 2, (YS_ + YB) / 2   # midden draaischijf
RS = 8.5                         # straal draaischijf
HZ = 4.86                        # plafond (onder de dakplaat van het kantelenblok)
LX0, LX1 = -5.0, -2.7            # bordes + trap (vanaf de noordgaanderij naar de schijf)


def box(rol, x0, y0, x1, y1, z0, z1):
    prisma(rol, [L(x0, y0), L(x1, y0), L(x1, y1), L(x0, y1)], z0, z1)


def bouw():
    # muren (oud beige pleister, tot onder in de bak), plafond donker
    box("gangmuur", XW_ - 0.2, YS_ - 0.2, XW_, YN_ + 0.2, ZB, HZ + 0.05)                 # west
    box("gangmuur", XW_ - 0.2, YS_ - 0.2, XE_ + 0.2, YS_, ZB, HZ + 0.05)                 # zuid
    box("gangmuur", XW_ - 0.2, YN_, XE_ + 0.2, YN_ + 0.2, 0.0, HZ + 0.05)                # noord
    for y0, y1 in ((YS_ - 0.2, -329.8), (-328.2, YN_ + 0.2)):                         # oost, met de opening van de gang
        box("gangmuur", XE_, y0, XE_ + 0.2, y1, 0.0 if y1 > -329 else ZB, HZ + 0.05)
    box("gangmuur", XE_, -329.8, XE_ + 0.2, -328.2, 3.05, HZ + 0.05)
    quad("plafond", [L(XW_, YN_) + Vector((0, 0, HZ)), L(XE_, YN_) + Vector((0, 0, HZ)), L(XE_, YS_) + Vector((0, 0, HZ)), L(XW_, YS_) + Vector((0, 0, HZ))])
    # gaanderij: vloer (noord + oost), bakwand eronder (donkergroen met een band crème panelen met bruine rozetten)
    box("vloertegel", XW_, YB, XE_, YN_, -0.25, 0.12)
    box("vloertegel", XB, YS_, XE_, YB, -0.25, 0.12)
    box("donker", XW_, YB - 0.2, XB, YB, ZB, 0.0)                                     # bakwand noord
    box("donker", XB, YS_, XB + 0.2, YB, ZB, 0.0)                                     # bakwand oost
    for x in [XW_ + 0.9 + 1.3 * k for k in range(int((XB - XW_ - 1.2) / 1.3) + 1)]:   # panelen noordbakwand
        box("wit", x - 0.5, YB - 0.24, x + 0.5, YB - 0.2, -0.95, -0.25)
        box("rozet", x - 0.16, YB - 0.27, x + 0.16, YB - 0.24, -0.76, -0.44)
    for y in [YS_ + 0.9 + 1.3 * k for k in range(int((YB - YS_ - 1.2) / 1.3) + 1)]:   # panelen oostbakwand
        box("wit", XB + 0.2, y - 0.5, XB + 0.24, y + 0.5, -0.95, -0.25)
        box("rozet", XB + 0.24, y - 0.16, XB + 0.27, y + 0.16, -0.76, -0.44)
    # bak: bodem, water, draaischijf (houten dek met donkere rand), naaf
    box("donker", XW_, YS_, XB, YB, ZB - 0.2, ZB)
    box("water", XW_, YS_, XB, YB, ZW - 0.05, ZW)
    lathe("dekhout", [(0.0, 0.0), (RS, 0.0), (RS, -0.6), (0.0, -0.6)], ZD, 64, (L(CX, CY).x, L(CX, CY).y))   # gesloten schijf
    lathe("donker", [(RS, 0.0), (RS + 0.12, 0.0), (RS + 0.12, -0.55), (RS, -0.55), (RS, 0.0)], ZD + 0.02, 64, (L(CX, CY).x, L(CX, CY).y))
    for k in range(32):                                                               # planknaden (radiaal)
        a = 2 * math.pi * k / 32; c, s_ = math.cos(a), math.sin(a)
        p0 = L(CX, CY) + Vector((c * 1.0, s_ * 1.0, 0)); p1 = L(CX, CY) + Vector((c * (RS - 0.1), s_ * (RS - 0.1), 0)); nn = Vector((-s_, c, 0)) * 0.015
        prisma("donker", [p0 - nn, p1 - nn, p1 + nn, p0 + nn], ZD, ZD + 0.01)
    lathe("goud", [(0.0, 0.0), (0.9, 0.0), (0.9, 0.08), (0.5, 0.12), (0.0, 0.14)], ZD, 24, (L(CX, CY).x, L(CX, CY).y))
    # balustrade langs de gaanderijrand (crème, 1,0 m) met groene kielbogen en zuilen tot een balk met lampjes
    def balustrade(xa, ya, xb, yb, open_=()):
        A, B = L(xa, ya), L(xb, yb); d = B - A; lg = d.length; t = d / lg; n_ = Vector((-t.y, t.x, 0))
        stappen = max(1, round(lg / 2.6)); st = lg / stappen
        for i in range(stappen):
            u0, u1 = i * st, (i + 1) * st
            if any(u0 < o1 and u1 > o0 for o0, o1 in open_): continue
            pa, pb = A + t * (u0 + 0.12), A + t * (u1 - 0.12)
            prisma("wit", [pa - n_ * 0.08, pb - n_ * 0.08, pb + n_ * 0.08, pa + n_ * 0.08], 0.12, 1.0)
            prisma("lijst", [pa - n_ * 0.12, pb - n_ * 0.12, pb + n_ * 0.12, pa + n_ * 0.12], 1.0, 1.08)
        for i in range(stappen + 1):                                                 # zuilen
            q = A + t * (i * st)
            lathe("groen", [(0.13, 0.0), (0.13, 0.12), (0.09, 0.2), (0.08, 2.4), (0.12, 2.5), (0.15, 2.62), (0.0, 2.64)], 0.12, 10, (q.x, q.y))
        for i in range(stappen):                                                     # kielbogen tussen de zuilen
            vl = Vlak(A + t * (i * st), t, n_)
            bg = spitsboog(st / 2, st - 0.3, 2.2, 2.2, 8, 0.6)[1:-1]
            tp = max(v for _, v in bg); hl = len(bg) // 2
            bg = [p for p in bg[:hl] if p[1] < tp - 0.08] + [(st / 2, min(tp + 0.14, 3.32))] + [p for p in bg[hl:] if p[1] < tp - 0.08]
            strip("groen", vl, bg, 0.14, 0.12)
        prisma("gangmuur", [A - n_ * 0.15, B - n_ * 0.15, B + n_ * 0.15, A + n_ * 0.15], 3.35, 3.6)   # balk
        for i in range(stappen):                                                     # lampjes op de balk
            q = A + t * ((i + 0.5) * st) + n_ * 0.18
            lathe("bollamp", [(r * 0.09, z) for r, z in ((0.0, -0.09), (0.7, -0.06), (1.0, 0.0), (0.7, 0.07), (0.0, 0.09))], 3.48, 10, (q.x, q.y))
    balustrade(XW_, YB - 0.1, XB + 0.1, YB - 0.1, open_=[(LX0 - XW_ - 0.2, LX1 - XW_ + 0.2)])   # noordrand (west -> oost)
    balustrade(XB + 0.1, YB - 0.1, XB + 0.1, YS_, open_=())                                     # oostrand (noord -> zuid)
    # bordes en trap naar de draaischijf (tegels; groene leuningen)
    box("vloertegel", LX0, YB - 1.0, LX1, YB, -0.25, 0.12)
    n = 12; ya = YB - 1.0
    for i in range(n):
        y0, y1 = ya - 0.26 * i, ya - 0.26 * (i + 1)
        box("vloertegel", LX0, y1, LX1, y0, ZD - 0.4 if i == n - 1 else 0.12 - 0.16 * (i + 1) - 0.2, 0.12 - 0.16 * (i + 1))
    yt = ya - 0.26 * n
    for x in (LX0, LX1):
        for z0, y0, z1, y1 in ((0.12, YB, 0.12, ya), (0.12, ya, ZD, yt)):
            a, b = L(x, y0) + Vector((0, 0, z0 + 1.0)), L(x, y1) + Vector((0, 0, z1 + 1.0))
            d = b - a; t = d.normalized(); sd = Vector((0.03, 0, 0)); up = Vector((0, 0, 0.03))
            bm = T["G"]["groenhek"]
            vs_ = [bm.verts.new(p) for p in (a - sd - up, b - sd - up, b + sd - up, a + sd - up, a - sd + up, b - sd + up, b + sd + up, a + sd + up)]
            for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([vs_[i] for i in f])
            for k in range(4):
                q = a + d * (k / 3)
                box("groenhek", (q.x / 1 + O[0]) - 0.03, (q.y + O[1]) - 0.03, (q.x + O[0]) + 0.03, (q.y + O[1]) + 0.03, q.z - 1.0, q.z)
    # controlehokje naast het bordes (Eftepedia: "langs het controlehok")
    box("gangmuur", LX1 + 0.3, YB - 1.6, LX1 + 1.7, YB - 0.1, -0.25 + 0.37, 2.3)
    box("raam", LX1 + 0.45, YB - 1.62, LX1 + 1.55, YB - 1.6, 1.1, 1.9)
    box("groen", LX1 + 0.2, YB - 1.7, LX1 + 1.8, YB, 2.3, 2.45)
    # grote ronde houten lattenkap boven de draaischijf
    zk = 3.9; c0 = L(CX, CY)
    lathe("hout", [(RS + 0.6, 0.0), (RS + 0.75, 0.0), (RS + 0.75, 0.25), (RS + 0.6, 0.25)], zk, 64, (c0.x, c0.y))
    lathe("hout", [(0.0, -0.3), (1.1, -0.1), (1.1, 0.3), (0.0, 0.4)], zk, 24, (c0.x, c0.y))
    for k in range(64):
        a = 2 * math.pi * k / 64; c, s_ = math.cos(a), math.sin(a); nn = Vector((-s_, c, 0)) * 0.05
        p0 = c0 + Vector((c * 1.1, s_ * 1.1, 0)); p1 = c0 + Vector((c * (RS + 0.6), s_ * (RS + 0.6), 0))
        prisma("hout", [p0 - nn, p1 - nn, p1 + nn, p0 + nn], zk + 0.05, zk + 0.15)
    for k in range(6):                                                                # ophanging
        a = 2 * math.pi * k / 6; q = c0 + Vector((math.cos(a) * 4.5, math.sin(a) * 4.5, 0))
        lathe("donker", [(0.02, 0.0), (0.02, HZ - zk - 0.15)], zk + 0.15, 6, (q.x, q.y))
    # uitgang naar de rit: opening in de zuidmuur achter een beige gordijn (Eftepedia: "klein beige gordijntje")
    gx0, gx1 = CX - 2.0, CX + 2.0
    box("poort", gx0, YS_ - 0.02, gx1, YS_ + 0.01, ZW, 1.4)
    box("gordijn", gx0 + 0.05, YS_ + 0.05, gx1 - 0.05, YS_ + 0.12, ZW + 0.05, 1.3)
    for k in range(9):
        x = gx0 + 0.25 + (gx1 - gx0 - 0.5) * k / 8
        box("gordijn", x - 0.08, YS_ + 0.12, x + 0.08, YS_ + 0.2, ZW + 0.05, 1.3)    # plooien
    box("groen", gx0 - 0.2, YS_, gx1 + 0.2, YS_ + 0.25, 1.4, 1.6)


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in T["G"].items():
        if not bm.faces: continue
        vast = rol in T["OVERLAY"]
        if not vast and rol not in ("raam", "deur", "dak", "stucvlak", "poort", "gangpleister", "groenneg", "plafond"):
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        uvl = bm.loops.layers.uv.verify(); s = T["UVS"][rol]
        for f in ([] if vast else bm.faces):
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.y / s, co.z / s) if ax == 0 else (co.x / s, co.z / s) if ax == 1 else (co.x / s, co.y / s)
        me = bpy.data.meshes.new("FM_instaphal_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_instaphal_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "instaphal"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = False
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 1400, 800
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 18
    for o in bpy.data.objects:
        if o.get("deel") == "kantelen" or o.get("rol") == "plafond": o.hide_render = True
    for naam, p, q in (("hal_gaanderij", L(9.2, -324.0) + Vector((0, 0, 1.7)), L(-6.0, -340.0) + Vector((0, 0, -1.0))),
                       ("hal_schijf", L(-3.85, -334.0) + Vector((0, 0, -0.2)), L(-3.85, -324.0) + Vector((0, 0, 1.5)))):
        cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(uit, naam + ".png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[16_instaphal] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "16_instaphal"); os.makedirs(uit, exist_ok=True); render(uit)


main()
