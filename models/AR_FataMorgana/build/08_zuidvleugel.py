"""08_zuidvleugel: stap 7 — de zuidvleugel langs het plein met de overdekte buitenwachtrij (FataVoorplein1993.jpg; AHN ref/ahn).
AHN: x 17,2..58, y -339,8..-350, 4,3 m. Foto: lange zuilengang met rode palen, brede fries van blauw-wit tegelwerk (FM_fries) met
rode randen, gouden bollen op de palen, achterwand met witte boognissen en donkere doorkijkjes; plat dak.
Modelstelsel = 02/03. Deel "zuidvleugel". Gebruik: blender --background --python build/08_zuidvleugel.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]
L, prisma, lathe, quad, strip, raam, Vlak, spitsboog, vul = (G3[k] for k in ("L", "prisma", "lathe", "quad", "strip", "raam", "Vlak", "spitsboog", "vul"))
OWNER = "phase:08_zuidvleugel"
T["KLEUR"].update({"fries": (0.2, 0.3, 0.6), "rood": (0.73, 0.26, 0.16), "wit": (0.95, 0.94, 0.9), "vloertegel": (0.65, 0.42, 0.33),
                   "matglas": (0.93, 0.95, 0.96), "schildering": (0.8, 0.75, 0.6), "koepel_blauw": (0.45, 0.68, 0.84), "hekgroen": (0.25, 0.36, 0.32)})
T["UVS"].update({"fries": 1.0, "rood": 1.0, "wit": 9.0, "vloertegel": 2.0, "matglas": 1.0, "schildering": 1.0, "koepel_blauw": 1.0, "hekgroen": 1.0})
T["OVERLAY"] = tuple(T["OVERLAY"]) + ("fries", "schildering")
for r in T["KLEUR"]: T["G"][r] = bmesh.new()

X0, X1, YV, YA, YZ = 17.2, 58.0, -339.8, -349.4, -350.0     # voorkant palen, achterwand wachtrijhal (zo diep als het dak: AHN tot -350), achterkant
H = 4.3


def paneel(rol, vl, u0, u1, v0, v1, n, su, sv, dv=0.0):
    bm = T["G"][rol]; uvl = bm.loops.layers.uv.verify()
    pts = [vl.p(u0, v0, n), vl.p(u1, v0, n), vl.p(u1, v1, n), vl.p(u0, v1, n)][::-1]
    uv = [(u0 / su, (v0 - dv) / sv), (u1 / su, (v0 - dv) / sv), (u1 / su, (v1 - dv) / sv), (u0 / su, (v1 - dv) / sv)][::-1]
    f = bm.faces.new([bm.verts.new(p) for p in pts])
    for lp, t in zip(f.loops, uv): lp[uvl].uv = t


def bouw():
    # achterblok (kern) achter de wachtrijhal, tot de achterkant
    prisma("stuc", [L(X0, YZ), L(X1, YZ), L(X1, YA), L(X0, YA)], 0.0, H - 0.3)
    # achterwand van de wachtrijhal (foto Daan): pilasters met smalle spitse nis, per vak een geschilderd paneel met blauwe
    # tegelrand en twee hoge rondboogramen van matglas, lijsten op 1,15 en 2,1 m
    aw = Vlak(L(X0, YA), Vector((1, 0, 0)), Vector((0, 1, 0)))
    lw = X1 - X0
    prisma("wit", [L(X0, YA - 0.3), L(X1, YA - 0.3), L(X1, YA), L(X0, YA)], 0.0, 3.35)
    strip("lijst", aw, [(0.0, 1.15), (lw, 1.15)], 0.1, 0.05); strip("lijst", aw, [(0.0, 2.1), (lw, 2.1)], 0.08, 0.05)
    nvak = 8; bv = lw / nvak
    for k in range(nvak + 1):                               # pilasters
        u = k * bv; u0, u1 = max(0.0, u - 0.3), min(lw, u + 0.3)
        prisma("wit", [Vector((q.x, q.y, 0)) for q in (aw.p(u0, 0, -0.05), aw.p(u1, 0, -0.05), aw.p(u1, 0, 0.22), aw.p(u0, 0, 0.22))], 0.0, 3.3)
        pv = Vlak(aw.p(0, 0, 0.22), aw.U, aw.N)
        vul("raam", pv, spitsboog(u, 0.26, 1.3, 1.95, 6, 0.75), 0.03)
        prisma("lijst", [Vector((q.x, q.y, 0)) for q in (aw.p(u0 - 0.04, 0, -0.05), aw.p(u1 + 0.04, 0, -0.05), aw.p(u1 + 0.04, 0, 0.28), aw.p(u0 - 0.04, 0, 0.28))], 2.95, 3.1)
    for k in range(nvak):
        c = (k + 0.5) * bv
        # geschilderd paneel met rondboog, blauwe tegelrand
        om = spitsboog(c, 1.3, 1.3, 2.35, 10, 0.5)
        sch = T["G"]["schildering"]; uvl = sch.loops.layers.uv.verify()
        cu, cv = c, 1.95
        for (ua, va), (ub, vb) in zip(om, om[1:] + om[:1]):
            pts = [aw.p(cu, cv, 0.06), aw.p(ua, va, 0.06), aw.p(ub, vb, 0.06)]       # zelfde volgorde als vul(): normaal +N
            f = sch.faces.new([sch.verts.new(q) for q in pts])
            for lp, (uu, vv_) in zip(f.loops, ((cu, cv), (ua, va), (ub, vb))):
                lp[uvl].uv = ((uu - c + 0.65) / 1.3, (vv_ - 1.3) / 1.7)
        strip("koepel_blauw", aw, om + [om[0]], 0.12, 0.08)
        # twee hoge rondboogramen (matglas), diep in de muur
        for du in (-1.5, 1.5):
            r = spitsboog(c + du, 0.95, 2.25, 2.65, 10, 0.5)
            vul("matglas", aw, r, 0.03); strip("lijst", aw, r, 0.1, 0.12)
    # vloer (dambord tegels) en plafond met bollampen
    prisma("vloertegel", [L(X0, YA), L(X1, YA), L(X1, YV + 0.1), L(X0, YV + 0.1)], -0.25, 0.12)   # 12 cm boven het terrein
    quad("stucvlak", [L(X0, YA) + Vector((0, 0, 3.3)), L(X0, YV) + Vector((0, 0, 3.3)), L(X1, YV) + Vector((0, 0, 3.3)), L(X1, YA) + Vector((0, 0, 3.3))])
    for y in (-342.6, -347.0):
        x = X0 + 2.0
        while x < X1 - 1.0:
            p = L(x, y)
            lathe("lampmetaal", [(0.02, 0.0), (0.02, 0.35)], 2.95, 6, (p.x, p.y))
            lathe("matglas", [(r * 0.17, z) for r, z in ((0.0, -0.17), (0.7, -0.12), (1.0, 0.0), (0.7, 0.13), (0.3, 0.17))], 2.78, 12, (p.x, p.y))
            x += 3.4
    # groene hekken (Daan 18 nov: "de rij staat andersom, niet horizontaal maar verticaal, niet breed genoeg en sluit niet aan op de
    # hekken en de ingang"): banen van 1,2 m van voor naar achter (noord-zuid), afwisselend open bij de achterwand en bij de voorkant.
    # Ingang van de rij aan de oostkant (opening in het voorhek), zigzag naar het westen, uitloop bij de veranda (12_veranda) naar de
    # zijdeur in de minaret.
    def hek(xa, ya, xb, yb):
        a, b = L(xa, ya), L(xb, yb); d = (b - a); lg = d.length; t = d / lg; nn = Vector((-t.y, t.x, 0)) * 0.025
        prisma("hekgroen", [a - nn, b - nn, b + nn, a + nn], 0.97, 1.03)
        k = max(1, round(lg / 2.4))
        for i in range(k + 1):
            q = a + d * (i / k)
            prisma("hekgroen", [q + Vector((sx, sy, 0)) * 0.025 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 0.0, 1.0)
    YH, YB = -340.35, YA + 0.25              # voorhek (achter de palen), achterkant van de banen
    XW, XO = 21.0, 54.6                      # westelijkste en oostelijkste baanhek
    hek(XW, YH, XO - 1.2, YH)                # voorhek; tussen XO-1,2 en XO de ingang van de rij
    hek(XO, YH, XO, YB)                      # oostgrens van de banen
    n = round((XO - XW) / 1.2); bw = (XO - XW) / n
    for i in range(1, n):
        x = XO - i * bw
        if i % 2 == 1: hek(x, YH, x, YB + 1.25)          # baan 1 loopt naar achteren: keren bij de achterwand
        else: hek(x, YH - 1.25, x, YB)                    # keren aan de voorkant
    hek(XW, YH - 1.25, XW, YB)                            # laatste baan: uitloop aan de voorkant, westwaarts naar de veranda
    hek(X0 + 0.4, YB, XW, YB)                             # achterkant van de uitloop
    # dakrand boven de palen: lijst + fries (blauw-wit tegelwerk) + rode randen; dak
    vv = Vlak(L(X0, YV), Vector((1, 0, 0)), Vector((0, 1, 0)))
    prisma("wit", [L(X0 - 0.1, YV - 0.25), L(X1 + 0.1, YV - 0.25), L(X1 + 0.1, YV + 0.1), L(X0 - 0.1, YV + 0.1)], 3.3, H)
    paneel("fries", vv, -0.1, lw + 0.1, 3.42, 4.18, 0.14, 1.8, 0.76, 3.42)
    for z in (3.36, 4.24):
        prisma("rood", [L(X0 - 0.12, YV - 0.25), L(X1 + 0.12, YV - 0.25), L(X1 + 0.12, YV + 0.17), L(X0 - 0.12, YV + 0.17)], z - 0.05, z + 0.05)
    prisma("stuc", [L(X0, YA), L(X1, YA), L(X1, YV - 0.25), L(X0, YV - 0.25)], 3.3, H - 0.3)
    quad("dak", [L(X0 + 0.1, YZ + 0.1) + Vector((0, 0, H + 0.08)), L(X1 - 0.1, YZ + 0.1) + Vector((0, 0, H + 0.08)),
                 L(X1 - 0.1, YV - 0.2) + Vector((0, 0, H + 0.08)), L(X0 + 0.1, YV - 0.2) + Vector((0, 0, H + 0.08))])
    # rode palen (vierkant met voet en kopje), gouden bol op elke tweede paal
    n = int(lw / 3.0)
    for i in range(n + 1):
        x = X0 + 0.3 + (lw - 0.6) * i / n; p = L(x, YV - 0.05)
        prisma("rood", [p + Vector((a, b, 0)) * 0.12 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 0.0, 3.3)
        prisma("rood", [p + Vector((a, b, 0)) * 0.2 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 0.0, 0.25)
        prisma("rood", [p + Vector((a, b, 0)) * 0.19 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 3.12, 3.3)
        if i % 2 == 0:
            q = p + Vector((0, 0.02, 0))
            prisma("goud", [q + Vector((a, b, 0)) * 0.1 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], H + 0.05, H + 0.2)
            lathe("goud", [(r * 0.17, z) for r, z in ((0.0, -0.17), (0.7, -0.12), (1.0, 0.0), (0.7, 0.13), (0.0, 0.2))], H + 0.38, 12, (q.x, q.y))
            lathe("goud", [(0.03, 0.0), (0.0, 0.25)], H + 0.56, 6, (q.x, q.y))
    # oostkop en achterkant: gewone gevels met kantelen en verwering (tegen de klok in: buiten = links)
    G6["wand"]([(X1, YV), (X1, YZ)], H, 0.4)
    G6["wand"]([(X1, YZ), (X0, YZ)], H, 0.4, ramen=[(0, 8.0, 1.6, 2.9), (0, 20.0, 1.6, 2.9), (0, 32.0, 1.6, 2.9)])


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in T["G"].items():
        if not bm.faces: continue
        vast = rol in T["OVERLAY"]
        if not vast and rol not in ("raam", "deur", "dak", "stucvlak", "matglas"):
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        uvl = bm.loops.layers.uv.verify(); s = T["UVS"][rol]
        for f in ([] if vast else bm.faces):
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.y / s, co.z / s) if ax == 0 else (co.x / s, co.z / s) if ax == 1 else (co.x / s, co.y / s)
        me = bpy.data.meshes.new("FM_zuidvleugel_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_zuidvleugel_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "zuidvleugel"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 1400, 700
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 26
    p = L(52.0, -340.5) + Vector((0, 0, 1.7)); q = L(30.0, -348.0) + Vector((0, 0, 1.6))
    cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(uit, "zuidvleugel.png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[08_zuidvleugel] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "08_zuidvleugel"); os.makedirs(uit, exist_ok=True); render(uit)


main()
