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
                   "matglas": (0.93, 0.95, 0.96), "schildering": (0.8, 0.75, 0.6), "koepel_blauw": (0.45, 0.68, 0.84), "hekgroen": (0.25, 0.36, 0.32), "donker": (0.12, 0.13, 0.15)})
T["UVS"].update({"fries": 1.0, "rood": 1.0, "wit": 9.0, "vloertegel": 2.0, "matglas": 1.0, "schildering": 1.0, "koepel_blauw": 1.0, "hekgroen": 1.0, "donker": 1.0})
T["OVERLAY"] = tuple(T["OVERLAY"]) + ("fries", "schildering")
for r in T["KLEUR"]: T["G"][r] = bmesh.new()

X0, X1, YV, YA, YZ = 17.2, 58.0, -339.8, -347.0, -350.0     # voorkant palen, achterwand wachtrijhal, achterkant
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
        for du in ((1.5,) if k == 0 else (-1.5, 1.5)):
            r = spitsboog(c + du, 0.95, 2.25, 2.65, 10, 0.5)
            vul("matglas", aw, r, 0.03); strip("lijst", aw, r, 0.1, 0.12)
    # spitsboogdoorgang in de achterwand aan de westkant (video 2020: de rij loopt erlangs naar de veranda)
    db = spitsboog(1.25, 1.0, 0.0, 1.9, 8, 0.75); vul("raam", aw, db, 0.03); strip("wit", aw, db, 0.16, 0.1)
    # vloer (dambord tegels) en plafond met bollampen
    prisma("vloertegel", [L(X0, YA), L(X1, YA), L(X1, YV + 0.1), L(X0, YV + 0.1)], -0.25, 0.12)   # 12 cm boven het terrein
    quad("stucvlak", [L(X0, YA) + Vector((0, 0, 3.3)), L(X0, YV) + Vector((0, 0, 3.3)), L(X1, YV) + Vector((0, 0, 3.3)), L(X1, YA) + Vector((0, 0, 3.3))])
    for y in (-342.0, -345.6):
        x = X0 + 2.0
        while x < X1 - 1.0:
            p = L(x, y)
            lathe("lampmetaal", [(0.02, 0.0), (0.02, 0.35)], 2.95, 6, (p.x, p.y))
            lathe("matglas", [(r * 0.17, z) for r, z in ((0.0, -0.17), (0.7, -0.12), (1.0, 0.0), (0.7, 0.13), (0.3, 0.17))], 2.78, 12, (p.x, p.y))
            x += 3.4
    # hekken binnen (video "Verlengde wachtrij - Fata Morgana 2020"): banen evenwijdig aan de achterwand. Ingang van de rij in het
    # voorhek aan de westkant (x 20,8..22, naast de veranda en het ronde bord), baan 1 langs de voorkant naar het oosten, keren,
    # terug, keren, achterste baan naar het westen, dan door de gang langs de westmuur (x 17,4..19) de veranda in naar de zijdeur.
    def hek(xa, ya, xb, yb, rol="hekgroen", h=1.0, stap=2.4):
        a, b = L(xa, ya), L(xb, yb); d = (b - a); lg = d.length; t = d / lg; nn = Vector((-t.y, t.x, 0)) * 0.025
        prisma(rol, [a - nn, b - nn, b + nn, a + nn], h - 0.03, h + 0.03)
        k = max(1, round(lg / stap))
        for i in range(k + 1):
            q = a + d * (i / k)
            prisma(rol, [q + Vector((sx, sy, 0)) * 0.025 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 0.0, h)
    # Daan 18 nov ("de fences staan nog steeds verkeerd"; zijn foto): banen van voor naar achter (noord-zuid), 1,2 m breed, vast aan
    # het voorhek, keren afwisselend voor en achter (achter ~1,2 m vrij tot de achterwand). Daan: "je moet er aan het begin in, niet
    # aan het einde en dan teruglopen": ingang aan de OOSTkant (opening in het voorhek bij de oostelijkste baan), zigzag westwaarts,
    # de westelijkste baan komt achter uit in het westvak (x 17,2..22) en loopt noordwaarts de veranda in naar de zijdeur.
    YF, YR, YW = YV - 0.25, -345.6, YA + 0.24          # voorhek, einde van de hekken die achter open zijn, achterwand (pilasters)
    BW = 1.2; X0B = 22.0; K = 29                         # baanbreedte, westelijkste hek, aantal banen
    for k in range(K + 1):
        x = X0B + BW * k
        if k == K: hek(x, YF, x, YW)                                 # oostgrens: dicht
        elif k % 2 == 0: hek(x, YF, x, YR)                           # achter open (ook hek 0: uitloop naar het westvak)
        else: hek(x, YF - BW, x, YW)                                 # voor open
    XI = X0B + BW * (K - 1)                                          # ingang: opening in het voorhek tussen XI en XI + BW
    # voorhek tussen de palen: zwart smeedwerk met rode plaquettes met ster (video), opening voor de ingang bij x 20,8..22
    for xa, xb in ((20.7, XI), (XI + BW, X1 - 0.3)):
        for z in (0.1, 1.0):
            prisma("donker", [L(xa, YF - 0.025), L(xb, YF - 0.025), L(xb, YF + 0.025), L(xa, YF + 0.025)], z - 0.03, z + 0.03)
        x = xa
        while x <= xb + 0.01:
            prisma("donker", [L(x - 0.012, YF - 0.012), L(x + 0.012, YF - 0.012), L(x + 0.012, YF + 0.012), L(x - 0.012, YF + 0.012)], 0.1, 1.0)
            x += 0.13
        x = xa + 0.65
        while x < xb - 0.4:
            for rol, hw, n0, n1 in (("rood", 0.21, 0.03, 0.06), ("wit", 0.13, 0.06, 0.075), ("goud", 0.06, 0.075, 0.09)):
                prisma(rol, [L(x - hw, YF + n0), L(x + hw, YF + n0), L(x + hw, YF + n1), L(x - hw, YF + n1)], 0.55 - hw, 0.55 + hw)
            x += 2.6
    for xx in (XI, XI + BW):                             # ingangspaaltjes met crème bollen
        p = L(xx, YF)
        prisma("donker", [p + Vector((sx, sy, 0)) * 0.05 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 0.0, 1.1)
        lathe("wit", [(r * 0.09, z) for r, z in ((0.0, -0.09), (0.7, -0.06), (1.0, 0.0), (0.7, 0.06), (0.0, 0.09))], 1.2, 10, (p.x, p.y))

    # schuine luifel boven de palen (video 2020): aflopend dakvlak met de blauw-witte fries erop, rode randen, witte onderkant;
    # erachter de gevel van het blok tot het dak (4,3 m) met witte borstwering
    yv, ya_, zv, za_ = YV + 0.55, YV - 0.9, 3.22, 3.95
    bm = T["G"]["fries"]; uvl = bm.loops.layers.uv.verify(); lsch = math.hypot(yv - ya_, za_ - zv)
    pts = [L(X0 - 0.1, yv) + Vector((0, 0, zv + 0.08)), L(X1 + 0.1, yv) + Vector((0, 0, zv + 0.08)), L(X1 + 0.1, ya_) + Vector((0, 0, za_ + 0.08)), L(X0 - 0.1, ya_) + Vector((0, 0, za_ + 0.08))]
    uvs = [(-0.1 / 1.8, 0.0), ((lw + 0.1) / 1.8, 0.0), ((lw + 0.1) / 1.8, 1.0), (-0.1 / 1.8, 1.0)]
    f = bm.faces.new([bm.verts.new(q) for q in pts[::-1]])   # omgekeerd: normaal schuin omhoog en naar voren (plein)
    for lp, t in zip(f.loops, uvs[::-1]): lp[uvl].uv = t
    hb = T["G"]["wit"]
    bot = [hb.verts.new(L(x_, y_) + Vector((0, 0, z_))) for x_, y_, z_ in ((X0 - 0.1, yv, zv - 0.06), (X1 + 0.1, yv, zv - 0.06), (X1 + 0.1, ya_, za_ - 0.06), (X0 - 0.1, ya_, za_ - 0.06))]
    top = [hb.verts.new(L(x_, y_) + Vector((0, 0, z_))) for x_, y_, z_ in ((X0 - 0.1, yv, zv + 0.06), (X1 + 0.1, yv, zv + 0.06), (X1 + 0.1, ya_, za_ + 0.06), (X0 - 0.1, ya_, za_ + 0.06))]
    hb.faces.new(top); hb.faces.new(bot[::-1])
    for k in range(4):
        j = (k + 1) % 4; hb.faces.new([bot[k], bot[j], top[j], top[k]])
    prisma("rood", [L(X0 - 0.12, yv - 0.04), L(X1 + 0.12, yv - 0.04), L(X1 + 0.12, yv + 0.06), L(X0 - 0.12, yv + 0.06)], zv - 0.12, zv + 0.14)
    prisma("rood", [L(X0 - 0.12, ya_ - 0.02), L(X1 + 0.12, ya_ - 0.02), L(X1 + 0.12, ya_ + 0.1), L(X0 - 0.12, ya_ + 0.1)], za_ - 0.02, za_ + 0.16)
    prisma("stuc", [L(X0, YA), L(X1, YA), L(X1, ya_ - 0.05), L(X0, ya_ - 0.05)], 3.3, H - 0.3)
    prisma("wit", [L(X0 - 0.1, ya_ - 0.3), L(X1 + 0.1, ya_ - 0.3), L(X1 + 0.1, ya_ - 0.02), L(X0 - 0.1, ya_ - 0.02)], za_ + 0.1, H + 0.15)
    quad("dak", [L(X0 + 0.1, YZ + 0.1) + Vector((0, 0, H + 0.08)), L(X1 - 0.1, YZ + 0.1) + Vector((0, 0, H + 0.08)),
                 L(X1 - 0.1, ya_ - 0.35) + Vector((0, 0, H + 0.08)), L(X0 + 0.1, ya_ - 0.35) + Vector((0, 0, H + 0.08))])
    # rode palen (vierkant met voet en kopje), gouden bol op elke tweede paal
    n = int(lw / 3.0)
    for i in range(n + 1):
        x = X0 + 0.3 + (lw - 0.6) * i / n; p = L(x, YV - 0.05)
        prisma("rood", [p + Vector((a, b, 0)) * 0.12 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 0.0, 3.3)
        prisma("rood", [p + Vector((a, b, 0)) * 0.2 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 0.0, 0.25)
        prisma("rood", [p + Vector((a, b, 0)) * 0.19 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 3.12, 3.3)
        prisma("rood", [L(x - 0.06, YV - 0.05), L(x + 0.06, YV - 0.05), L(x + 0.06, YV + 0.5), L(x - 0.06, YV + 0.5)], 3.0, 3.12)   # console onder de luifel
        if i % 2 == 0:
            q = L(x, -340.75)
            prisma("goud", [q + Vector((a, b, 0)) * 0.08 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], H + 0.1, H + 0.25)
            lathe("goud", [(r * 0.15, z) for r, z in ((0.0, -0.15), (0.7, -0.1), (1.0, 0.0), (0.7, 0.11), (0.0, 0.17))], H + 0.4, 12, (q.x, q.y))
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
