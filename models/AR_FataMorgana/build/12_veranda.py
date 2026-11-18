"""12_veranda: stap 11 — de overdekte wachtrij links van de minaret (POV-video 2025 [4K POV] Fata Morgana, Eftepedia: "op drukke
dagen moet men aanschuiven in een overdekte ruimte aan de linkerzijde van de toren, om via een zijdeur de minaret te betreden").
AHN: x 17,5..20,6, y -331,5..-338,8, dak 2,8 m, tegen de kantelenmuur (5,4 m); sluit zuidelijk aan op de zuidvleugel.
Video: rode palen met voet en kopje, blauw-witte fries (FM_fries) met rode randen langs de dakrand, aflopend dak met houten
onderkant, betegelde vloer, zwarte hekken met crèmekleurige bollen langs de open kant, ingang op de zuidoosthoek.
Modelstelsel = 02/03. Deel "veranda". Gebruik: blender --background --python build/12_veranda.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]
L, prisma, lathe, quad, strip, raam, Vlak, spitsboog, vul = (G3[k] for k in ("L", "prisma", "lathe", "quad", "strip", "raam", "Vlak", "spitsboog", "vul"))
OWNER = "phase:12_veranda"
T["KLEUR"].update({"fries": (0.2, 0.3, 0.6), "rood": (0.73, 0.26, 0.16), "wit": (0.95, 0.94, 0.9), "donker": (0.12, 0.13, 0.15), "vloertegel": (0.65, 0.42, 0.33), "goud": (0.87, 0.67, 0.32), "koepel_blauw": (0.45, 0.68, 0.84)})
T["UVS"].update({"fries": 1.0, "rood": 1.0, "wit": 9.0, "donker": 1.0, "vloertegel": 2.0, "goud": 1.0, "koepel_blauw": 1.0})
T["OVERLAY"] = tuple(T["OVERLAY"]) + ("fries",)
for r in T["KLEUR"]: T["G"][r] = bmesh.new()

XM, XV = 17.3, 20.45          # achterkant (in de kantelenmuur), lijn van de palen
YN, YZ = -331.1, -339.65       # noord (in de minaretvoet), zuid (tegen de zuidvleugel)
ZV, ZA = 2.45, 3.15            # onderkant dakrand voor, dak bij de muur


def paneel(rol, vl, u0, u1, v0, v1, n, su, sv, dv=0.0):
    bm = T["G"][rol]; uvl = bm.loops.layers.uv.verify()
    pts = [vl.p(u0, v0, n), vl.p(u1, v0, n), vl.p(u1, v1, n), vl.p(u0, v1, n)][::-1]
    uv = [(u0 / su, (v0 - dv) / sv), (u1 / su, (v0 - dv) / sv), (u1 / su, (v1 - dv) / sv), (u0 / su, (v1 - dv) / sv)][::-1]
    f = bm.faces.new([bm.verts.new(p) for p in pts])
    for lp, t in zip(f.loops, uv): lp[uvl].uv = t


def bouw():
    vv = Vlak(L(XV, YN), Vector((0, -1, 0)), Vector((1, 0, 0)))            # voorkant (oost), u van noord naar zuid
    lw = YN - YZ
    # betegelde vloer, 12 cm boven het terrein
    prisma("vloertegel", [L(XM, YZ), L(XV + 0.25, YZ), L(XV + 0.25, YN), L(XM, YN)], -0.25, 0.12)   # zelfde tegels als de wachtrijhal
    # rode palen (voet, schacht, kopje), gelijk verdeeld
    n = 3
    for i in range(n):                                   # de hoekpaal is de eerste paal van de wachtrijhal (08): geen dubbele paal
        p = L(XV, YN - 0.35 - (lw - 0.7) * i / n)
        for hw, z0, z1 in ((0.2, 0.0, 0.25), (0.11, 0.0, ZV), (0.18, ZV - 0.16, ZV)):
            prisma("rood", [p + Vector((a, b, 0)) * hw for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], z0, z1)
    # dakrand: witte balk, fries (blauw-wit tegelwerk) met rode randen boven en onder
    prisma("wit", [L(XV - 0.15, YZ), L(XV + 0.12, YZ), L(XV + 0.12, YN), L(XV - 0.15, YN)], ZV, ZV + 0.55)
    paneel("fries", vv, 0.0, lw, ZV + 0.06, ZV + 0.5, 0.13, 1.8, 0.44, ZV + 0.06)
    for z in (ZV + 0.03, ZV + 0.53):
        prisma("rood", [L(XV - 0.16, YZ), L(XV + 0.16, YZ), L(XV + 0.16, YN), L(XV - 0.16, YN)], z - 0.04, z + 0.04)
    # aflopend dak: houten plaat (onderkant zichtbaar) met donker dakvlak erop
    za, zb = ZV + 0.6, ZA
    for rol, d0, d1 in (("hout", 0.0, 0.1),):
        hk = [L(XV + 0.22, YZ), L(XV + 0.22, YN), L(XM, YN), L(XM, YZ)]
        zz = [za, za, zb, zb]
        bm = T["G"]["hout"]
        bot = [bm.verts.new(p + Vector((0, 0, z + d0))) for p, z in zip(hk, zz)]
        top = [bm.verts.new(p + Vector((0, 0, z + d1))) for p, z in zip(hk, zz)]
        bm.faces.new(top); bm.faces.new(bot[::-1])
        for k in range(4):
            j = (k + 1) % 4; bm.faces.new([bot[k], bot[j], top[j], top[k]])
    quad("dak", [L(XV + 0.2, YZ + 0.02) + Vector((0, 0, za + 0.12)), L(XV + 0.2, YN - 0.02) + Vector((0, 0, za + 0.12)),
                 L(XM, YN - 0.02) + Vector((0, 0, zb + 0.12)), L(XM, YZ + 0.02) + Vector((0, 0, zb + 0.12))])   # tegen de klok in: normaal omhoog
    # hekken langs de open kant met cremekleurige bollen; opening voor de ingang op de zuidoosthoek
    h0, h1 = YN - 0.6, YZ + 1.6
    m = int((h0 - h1) / 1.2)
    for i in range(m + 1):
        y = h0 - (h0 - h1) * i / m; p = L(XV + 0.05, y)
        prisma("donker", [p + Vector((a, b, 0)) * 0.04 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 0.0, 1.05)
        lathe("wit", [(r * 0.07, z) for r, z in ((0.0, -0.07), (0.7, -0.05), (1.0, 0.0), (0.7, 0.05), (0.0, 0.07))], 1.13, 10, (p.x, p.y))
    for z in (0.12, 0.98):
        prisma("donker", [L(XV + 0.02, h1), L(XV + 0.08, h1), L(XV + 0.08, h0), L(XV + 0.02, h0)], z - 0.025, z + 0.025)
    k = int((h0 - h1) / 0.13)
    for i in range(1, k):
        y = h0 - (h0 - h1) * i / k
        prisma("donker", [L(XV + 0.035, y - 0.01), L(XV + 0.065, y - 0.01), L(XV + 0.065, y + 0.01), L(XV + 0.035, y + 0.01)], 0.12, 0.98)
    # geen tussenhek: de rij komt uit de wachtrijhal (zuid) en loopt rechtdoor naar de zijdeur in de minaret (noord)
    # opening op de zuidoosthoek (ingang op rustige dagen, POV-video 2025) afgesloten met paaltjes en een touw (video 2020;
    # Daan: "afsluiten met touw"), zodat de rij via de ingang aan de oostkant door de wachtrijhal loopt
    palen = [YZ + 0.1, (YZ + h1) / 2, h1]
    for y in palen[:2]:
        p = L(XV + 0.05, y)
        lathe("donker", [(0.11, 0.0), (0.11, 0.04), (0.035, 0.07), (0.03, 0.92), (0.05, 0.95), (0.0, 0.97)], 0.0, 10, (p.x, p.y))
        lathe("goud", [(r * 0.06, z) for r, z in ((0.0, -0.06), (0.7, -0.04), (1.0, 0.0), (0.7, 0.04), (0.0, 0.06))], 1.02, 10, (p.x, p.y))
    for ya, yb in zip(palen, palen[1:]):                 # doorhangend touw (12 stukjes)
        pts = []
        for k in range(13):
            t = k / 12; y = ya + (yb - ya) * t
            pts.append(L(XV + 0.05, y) + Vector((0, 0, 0.9 - 0.14 * 4 * t * (1 - t))))
        for a, b in zip(pts, pts[1:]):
            d = (b - a); m = (a + b) / 2; hl = d.length / 2 + 0.01
            t_ = d.normalized(); z_ = Vector((0, 0, 1)); x_ = t_.cross(z_).normalized() * 0.018; zz = x_.cross(t_).normalized() * 0.018
            bm = T["G"]["hout"]
            ring_a = [bm.verts.new(m - t_ * hl + x_ * sx + zz * sz) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            ring_b = [bm.verts.new(m + t_ * hl + x_ * sx + zz * sz) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            for k in range(4):
                j = (k + 1) % 4
                f = bm.faces.new([ring_a[k], ring_a[j], ring_b[j], ring_b[k]])
                if f.calc_center_median().__sub__(m).dot(f.normal) < 0: f.normal_flip()
            fa = bm.faces.new(ring_a[::-1]); fb = bm.faces.new(ring_b)
            if fa.normal.dot(-t_) < 0: fa.normal_flip()
            if fb.normal.dot(t_) < 0: fb.normal_flip()
    # bord met de wachttijd voor de opening, op het plein (POV-video 2025: schildvormig bord met krul erboven)
    q = L(21.0, -339.15)
    prisma("donker", [q + Vector((a, b, 0)) * 0.04 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 0.0, 1.95)
    prisma("wit", [q + Vector((-0.03, -0.38, 0)), q + Vector((0.03, -0.38, 0)), q + Vector((0.03, 0.38, 0)), q + Vector((-0.03, 0.38, 0))], 0.95, 1.85)
    prisma("koepel_blauw", [q + Vector((-0.04, -0.42, 0)), q + Vector((0.04, -0.42, 0)), q + Vector((0.04, 0.42, 0)), q + Vector((-0.04, 0.42, 0))], 0.9, 0.95)
    prisma("goud", [q + Vector((-0.05, -0.45, 0)), q + Vector((0.05, -0.45, 0)), q + Vector((0.05, 0.45, 0)), q + Vector((-0.05, 0.45, 0))], 1.85, 2.0)
    for dy in (-0.45, 0.45):
        lathe("goud", [(r * 0.07, z) for r, z in ((0.0, -0.07), (0.7, -0.05), (1.0, 0.0), (0.7, 0.05), (0.0, 0.07))], 1.93, 8, (q.x, q.y + dy))


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in T["G"].items():
        if not bm.faces: continue
        vast = rol in T["OVERLAY"]
        if not vast and rol not in ("raam", "deur", "dak", "stucvlak", "hout"):
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        uvl = bm.loops.layers.uv.verify(); s = T["UVS"][rol]
        for f in ([] if vast else bm.faces):
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.y / s, co.z / s) if ax == 0 else (co.x / s, co.z / s) if ax == 1 else (co.x / s, co.y / s)
        me = bpy.data.meshes.new("FM_veranda_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_veranda_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "veranda"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 1400, 700
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 26
    p = L(27.0, -341.5) + Vector((0, 0, 1.7)); q = L(19.0, -333.0) + Vector((0, 0, 1.8))
    cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(uit, "veranda.png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[12_veranda] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "12_veranda"); os.makedirs(uit, exist_ok=True); render(uit)


main()
