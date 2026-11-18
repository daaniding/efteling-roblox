"""05_ingang: stap 4 — het ingangsgebouw met de blauwe koepel (FataVoorplein1993.jpg, Fatamorganaingang1987.jpg, Fmplein1986.jpg).
Plek/maten: luchtfoto (ref/luchtfoto) blok x 17,5..24,5, y -301..-314, blauwe koepel ~5 m doorsnee bij (20,5; -310,5); AHN: dakrand
3,6 m, koepeltop ~5,7-6 m. Vorm: wit, gelijkvloers, golvende Moorse dakrand met dikke rood-oranje rand en een grote kielboog boven de
ingang (oostgevel, naar het plein), voorportaal met rode zuilen en bogen met rode randen, donkere ingang, winkelraam met roedes,
hemelsblauwe koepel met gouden spits.
Modelstelsel = 02/03 (oorsprong park -40; -295). Deel "ingang". Gebruik: blender --background --python build/05_ingang.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F3 = os.path.join(D, "build", "03_noordgevel.py")
G3 = {"__file__": F3, "__name__": "lib"}
exec(compile(open(F3).read().rsplit("\nmain()", 1)[0], F3, "exec"), G3)
T = G3["T"]; L, prisma, lathe, quad, strip, spitsboog, vul, raam, Vlak, buis = (G3[k] for k in ("L", "prisma", "lathe", "quad", "strip", "spitsboog", "vul", "raam", "Vlak", "buis")) if "buis" in G3 else (*(G3[k] for k in ("L", "prisma", "lathe", "quad", "strip", "spitsboog", "vul", "raam", "Vlak")), None)
OWNER = "phase:05_ingang"
T["KLEUR"].update({"wit": (0.95, 0.94, 0.9), "rood": (0.8, 0.3, 0.18), "koepel_blauw": (0.45, 0.68, 0.84), "witvlak": (0.95, 0.94, 0.9)})
T["UVS"].update({"wit": 9.0, "rood": 1.0, "koepel_blauw": 2.0, "witvlak": 9.0})
for r in T["KLEUR"]: T["G"][r] = bmesh.new()

X0, X1, Y0, Y1 = 17.5, 24.5, -314.0, -301.0
H = 3.0                     # muur tot de dakrand
KOEPEL = (20.5, -310.5)


def vlak_vanaf(a, b):
    """gevelvlak van a naar b (parkcoordinaten), tegen de klok in rond het gebouw: voorkant = links van a->b (naar buiten),
    zelfde conventie als 03_noordgevel (anders kijken losse vlakken naar binnen)"""
    A, B = L(*a), L(*b); u = (B - A).normalized(); n = Vector((-u.y, u.x, 0))
    return Vlak(A, u, n), (B - A).length


def ogee(t):
    """kielboog-bult 0..1 voor t in [-1, 1]: hol uitlopend, puntig aan de top"""
    x = max(0.0, 1 - abs(t))
    return x ** 1.6 * (1.15 - 0.15 * x)


def dakrand(vl, lengte, hoog_mid=0.0):
    """golvende Moorse dakrand op een gevel: kleine bulten om de ~2,2 m, optioneel een grote kielboog in het midden;
    witte borstwering (dikte 0,25) met een dikke rode rand erop"""
    n = max(2, round(lengte / 2.2)); w = lengte / n
    def vtop(u):
        k = min(n - 1, max(0, int(u / w))); c = (k + 0.5) * w
        v = H + 0.3 + 0.38 * ogee((u - c) / (w / 2))
        if hoog_mid:
            d = (u - lengte / 2) / (lengte * 0.28)
            if abs(d) < 1: v = max(v, H + 0.3 + hoog_mid * ogee(d))
        return v
    us = [lengte * j / 80 for j in range(81)]
    dik = 0.25
    for ua, ub in zip(us, us[1:]):
        ta, tb = vtop(ua), vtop(ub)
        quad("witvlak", [vl.p(ua, H, 0), vl.p(ub, H, 0), vl.p(ub, tb, 0), vl.p(ua, ta, 0)][::-1])
        quad("witvlak", [vl.p(ua, H, -dik), vl.p(ua, ta, -dik), vl.p(ub, tb, -dik), vl.p(ub, H, -dik)][::-1])
    # rode rand: buis langs de bovenkant (iets naar voren)
    pad = [vl.p(u, vtop(u) + 0.02, -dik / 2) for u in us]
    G3_buis(pad, 0.12)


def G3_buis(pts, r, seg=8, rol="rood"):
    n = len(pts); ringen = []
    for i in range(n):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        h = Vector((0, 0, 1)) if abs(t.z) < 0.95 else Vector((1, 0, 0))
        x = t.cross(h).normalized(); y = t.cross(x)
        ringen.append([pts[i] + (x * math.cos(2 * math.pi * k / seg) + y * math.sin(2 * math.pi * k / seg)) * r for k in range(seg)])
    for i in range(n - 1):
        for k in range(seg):
            quad(rol, [ringen[i][k], ringen[i][(k + 1) % seg], ringen[i + 1][(k + 1) % seg], ringen[i + 1][k]])


def kielboog(xc, w, v0, vs, hb, n=10):
    """omtrek van een kielboog (ogee): van linksonder via de punt naar rechtsonder"""
    links = [(xc - w / 2 + (w / 2) * (1 - math.cos(math.pi / 2 * t)) ** 0.85 * 1.0, vs + hb * (math.sin(math.pi / 2 * t) ** 1.4)) for t in [k / n for k in range(n + 1)]]
    links = [(xc - w / 2 + w / 2 * t ** 1.3, vs + hb * (1 - (1 - t) ** 2.2)) for t in [k / n for k in range(n + 1)]]
    rechts = [(2 * xc - u, v) for u, v in links[::-1]][1:]
    return [(xc - w / 2, v0)] + links + rechts + [(xc + w / 2, v0)]


def zuil(p, h, r=0.17):
    lathe("rood", [(r * 1.4, 0.0), (r * 1.4, 0.14), (r, 0.24), (r * 0.95, h - 0.32), (r * 1.25, h - 0.22), (r * 1.5, h - 0.08), (r * 1.5, h), (0.0, h)], 0.0, 14, (p.x, p.y))


def bouw():
    # hoofdblok: witte muren tot de dakrand, plint, dak (dak-rol)
    hk = [L(X0, Y0), L(X1, Y0), L(X1, Y1), L(X0, Y1)]
    prisma("wit", hk, 0.0, H)
    prisma("lijst", [L(X0 - 0.06, Y0 - 0.06), L(X1 + 0.06, Y0 - 0.06), L(X1 + 0.06, Y1 + 0.06), L(X0 - 0.06, Y1 + 0.06)], 0.0, 0.3)
    quad("dak", [L(X0 + 0.2, Y0 + 0.2) + Vector((0, 0, H + 0.02)), L(X1 - 0.2, Y0 + 0.2) + Vector((0, 0, H + 0.02)),
                 L(X1 - 0.2, Y1 - 0.2) + Vector((0, 0, H + 0.02)), L(X0 + 0.2, Y1 - 0.2) + Vector((0, 0, H + 0.02))])
    oost, lo = vlak_vanaf((X1, Y1), (X1, Y0))          # voorkant naar het plein (u van noord naar zuid)
    noord, ln = vlak_vanaf((X0, Y1), (X1, Y1))
    west, lw = vlak_vanaf((X0, Y0), (X0, Y1))
    zuid, lz = vlak_vanaf((X1, Y0), (X0, Y0))
    dakrand(oost, lo, 1.25); dakrand(noord, ln, 0.6); dakrand(west, lw); dakrand(zuid, lz, 0.6)
    # oostgevel: voorportaal (rode zuilen, bogenwand met kielbogen en rode randen), ingang, winkelraam, raampje
    uc = lo / 2; diep = 1.5; hz = 2.2; HP = 3.3            # HP: bovenkant portaal (boven de hoogste boog)
    zuilen_u = [uc - 3.3, uc - 1.25, uc + 1.25, uc + 3.3]
    for u in zuilen_u:
        zuil(oost.p(u, 0, diep - 0.2), hz)
    # bogenwand voor (van zuil tot zuil), dak van het portaal
    bw = Vlak(oost.p(0, 0, diep), oost.U, oost.N)
    vakken = list(zip(zuilen_u, zuilen_u[1:]))
    for a, b in vakken:
        w = b - a; c = (a + b) / 2; groot = abs(c - uc) < 0.1
        om = kielboog(c, w - 0.4, hz, hz - (0.0 if groot else 0.1), 0.9 if groot else 0.6)
        # boogvlak: stroken tussen boogrand en bovenkant (H)
        def onder(u):
            pts = om[1:-1]
            for (u0, v0), (u1, v1) in zip(pts, pts[1:]):
                if min(u0, u1) <= u <= max(u0, u1) and u1 != u0:
                    return v0 + (v1 - v0) * (u - u0) / (u1 - u0)
            return hz
        us = [a + (b - a) * j / 24 for j in range(25)]
        for ua, ub in zip(us, us[1:]):
            ba, bb = onder(ua), onder(ub)
            quad("witvlak", [bw.p(ua, ba, 0), bw.p(ub, bb, 0), bw.p(ub, HP, 0), bw.p(ua, HP, 0)][::-1])
            quad("witvlak", [bw.p(ua, ba, -0.25), bw.p(ua, HP, -0.25), bw.p(ub, HP, -0.25), bw.p(ub, bb, -0.25)][::-1])
            quad("witvlak", [bw.p(ua, ba, 0), bw.p(ua, ba, -0.25), bw.p(ub, bb, -0.25), bw.p(ub, bb, 0)][::-1])
        G3_buis([bw.p(u, v + 0.05, 0.05) for u, v in om[1:-1]], 0.09)
    # zijkanten en dak van het portaal
    for u in (zuilen_u[0] - 0.2, zuilen_u[-1] + 0.2):
        prisma("wit", [Vector((p.x, p.y, 0)) for p in (oost.p(u - 0.12, 0, 0), oost.p(u + 0.12, 0, 0), oost.p(u + 0.12, 0, diep), oost.p(u - 0.12, 0, diep))], hz, HP)
    prisma("wit", [Vector((p.x, p.y, 0)) for p in (oost.p(zuilen_u[0] - 0.35, 0, 0), oost.p(zuilen_u[-1] + 0.35, 0, 0), oost.p(zuilen_u[-1] + 0.35, 0, diep + 0.12), oost.p(zuilen_u[0] - 0.35, 0, diep + 0.12))], HP - 0.02, HP + 0.15)
    G3_buis([oost.p(zuilen_u[0] - 0.35, HP + 0.16, diep + 0.14), oost.p(zuilen_u[-1] + 0.35, HP + 0.16, diep + 0.14)], 0.09)
    quad("tegel", [oost.p(zuilen_u[0] - 0.35, 0.03, 0), oost.p(zuilen_u[-1] + 0.35, 0.03, 0), oost.p(zuilen_u[-1] + 0.35, 0.03, diep + 0.1), oost.p(zuilen_u[0] - 0.35, 0.03, diep + 0.1)][::-1][::-1])
    # achter het portaal: ingang (donker), winkelraam rechts, raampje links
    deur = kielboog(uc, 1.9, 0.0, 1.95, 0.6)
    vul("raam", oost, deur, 0.09); G3_buis([oost.p(u, v, 0.08) for u, v in deur], 0.07)
    for k in range(4):                                          # winkelraam met roedes
        pass
    wu = uc + 2.3
    quad("raam", [oost.p(wu - 0.6, 0.7, 0.09), oost.p(wu + 0.6, 0.7, 0.09), oost.p(wu + 0.6, 2.05, 0.09), oost.p(wu - 0.6, 2.05, 0.09)][::-1])
    for k in range(5):
        u = wu - 0.6 + 1.2 * k / 4
        prisma("wit", [Vector((p.x, p.y, 0)) for p in (oost.p(u - 0.03, 0, 0.09), oost.p(u + 0.03, 0, 0.09), oost.p(u + 0.03, 0, 0.14), oost.p(u - 0.03, 0, 0.14))], 0.7, 2.05)
    for k in range(4):
        v = 0.7 + 1.35 * k / 3
        prisma("wit", [Vector((p.x, p.y, 0)) for p in (oost.p(wu - 0.6, 0, 0.09), oost.p(wu + 0.6, 0, 0.09), oost.p(wu + 0.6, 0, 0.14), oost.p(wu - 0.6, 0, 0.14))], v - 0.03, v + 0.03)
    G3_buis([oost.p(wu - 0.68, 0.62, 0.1), oost.p(wu + 0.68, 0.62, 0.1), oost.p(wu + 0.68, 2.13, 0.1), oost.p(wu - 0.68, 2.13, 0.1), oost.p(wu - 0.68, 0.62, 0.1)], 0.06)
    raam(oost, uc - 2.3, 0.6, 0.9, 1.9)
    # buiten het portaal: raampjes met rode omlijsting op de oostgevel en de zijkanten
    for vl, l in ((oost, lo), (noord, ln), (zuid, lz), (west, lw)):
        for u in ([0.9, l - 0.9] if vl is oost else [l * 0.3, l * 0.7]):
            om = kielboog(u, 0.6, 0.9, 1.7, 0.3, 8)
            vul("raam", vl, om, 0.09); G3_buis([vl.p(a, b, 0.08) for a, b in om], 0.05)
    # blauwe koepel op een lage trommel met rode ring + gouden spits
    c = L(*KOEPEL)
    lathe("wit", [(2.35, 0.0), (2.35, 0.35)], H, 40, (c.x, c.y))
    lathe("rood", [(2.3, 0.0), (2.42, 0.0), (2.42, 0.14), (2.3, 0.14)], H + 0.3, 40, (c.x, c.y))
    prof = [(2.32, 0.0), (2.34, 0.3), (2.25, 0.8), (2.0, 1.3), (1.6, 1.75), (1.1, 2.1), (0.55, 2.35), (0.15, 2.45), (0.0, 2.47)]
    lathe("koepel_blauw", prof, H + 0.44, 40, (c.x, c.y))
    top = H + 0.44 + 2.45
    lathe("goud", [(0.08, 0.0), (0.04, 0.1), (0.04, 1.0), (0.0, 1.1)], top - 0.03, 10, (c.x, c.y))
    for dz, r in ((0.25, 0.12), (0.55, 0.09)):
        lathe("goud", [(r * math.sin(math.pi * k / 8), -r * math.cos(math.pi * k / 8)) for k in range(9)], top + dz, 12, (c.x, c.y))


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in T["G"].items():
        if not bm.faces: continue
        vast = rol in T["OVERLAY"]
        if not vast and rol not in ("raam", "deur", "dak", "witvlak", "tegel"):
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        uvl = bm.loops.layers.uv.verify(); s = T["UVS"][rol]
        for f in ([] if vast else bm.faces):
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.y / s, co.z / s) if ax == 0 else (co.x / s, co.z / s) if ax == 1 else (co.x / s, co.y / s)
        me = bpy.data.meshes.new("FM_ingang_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_ingang_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "ingang"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 1200, 800
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 30
    for o in bpy.data.objects:
        if o.get("deel") not in ("ingang", "minaret", None): o.hide_render = True
    p = L(36.0, -318.0) + Vector((0, 0, 1.7)); q = L(21.0, -307.5) + Vector((0, 0, 2.6))
    cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(uit, "ingang.png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[05_ingang] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "05_ingang"); os.makedirs(uit, exist_ok=True); render(uit)


main()
