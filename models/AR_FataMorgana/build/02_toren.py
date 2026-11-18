"""02_toren: de grote toren met turquoise koepel aan het meer (stap 1 van de buitenkant).
Plek en maten: AHN dsm_05m (ref/ahn): top NAP 27,3 bij park (-40; -295), dak complex NAP 16,7, water/maaiveld NAP 8,7; romp
~7 x 6 m. Vorm: Fata2013.jpg (1 px ~ 5 cm): onderblok 10 m met getrapte Moorse kantelen en hoger oplopende hoeklisenen,
twee spitsboognissen met raampje, portaal onder in het midden, lijstbanden; bovenstuk 4,6 m tot 14,4 m met twee boogramen per
zijde; trommel + turquoise koepel tot ~17,6 m; gouden spits met bollen.
Modelstelsel: meters, oorsprong = voet van de toren op het maaiveld (park -40; -295), x oost, y noord (voorkant = meer = +y).
Rollen: stuc, lijst, raam, deur, koepel, goud. Gebruik: blender --background --python build/02_toren.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(D, "AR_FataMorgana_master.blend")
OWNER = "phase:02_toren"
KLEUR = {"stuc": (0.86, 0.78, 0.66), "lijst": (0.93, 0.89, 0.81), "raam": (0.09, 0.09, 0.11), "deur": (0.3, 0.2, 0.13),
         "koepel": (0.16, 0.66, 0.7), "goud": (0.85, 0.66, 0.28)}
UVS = {"stuc": 9.0, "lijst": 9.0, "raam": 1.0, "deur": 1.0, "koepel": 2.0, "goud": 0.5}
OVERLAY = ("vlek1", "vlek2", "vlek3", "vlek4", "streep", "voet")
for r_ in OVERLAY: KLEUR[r_] = (0.8, 0.67, 0.47); UVS[r_] = 1.0
G = {r: bmesh.new() for r in KLEUR}
import random as _random
_laag = [0]


def overlay(rol, vl, u, v, w, h, fu=False, fv=False):
    """half doorzichtige verweringskaart op een gevel (eigen UV 0..1), elke kaart iets verder naar voren tegen z-fighting"""
    _laag[0] = (_laag[0] + 1) % 12; n = 0.03 + 0.004 * _laag[0]          # >= 3 cm voor de muur (z-fighting op afstand)
    bm = G[rol]; uvl = bm.loops.layers.uv.verify()
    pts = [vl.p(u - w / 2, v, n), vl.p(u + w / 2, v, n), vl.p(u + w / 2, v + h, n), vl.p(u - w / 2, v + h, n)]
    uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
    if fu: uv = [(1 - a, b) for a, b in uv]
    if fv: uv = [(a, 1 - b) for a, b in uv]
    pts, uv = pts[::-1], uv[::-1]                      # U x V wijst de muur in: omdraaien zodat de voorkant naar buiten kijkt
    f = bm.faces.new([bm.verts.new(p) for p in pts])
    for lp, t in zip(f.loops, uv): lp[uvl].uv = t


def verwering(vl, u0, u1, z0, z1, seed, gaten=()):
    """willekeurige vlekken, vuilstrepen onder de bovenrand en een vochtige voet (Daan 18 nov: geen copy-paste-patroon);
    gaten = [(u0, u1, z0, z1)]: openingen (galerij) waar geen kaart over mag"""
    r = _random.Random(seed); L = u1 - u0; H = z1 - z0
    def vrij(u, v, w, h): return not any(u + w / 2 > a and u - w / 2 < b and v + h > c and v < d for a, b, c, d in gaten)
    _ov = overlay
    def overlay_(rol, vl_, u, v, w, h, fu=False, fv=False):
        if vrij(u, v, w, h): _ov(rol, vl_, u, v, w, h, fu, fv)
    for _ in range(max(1, int(L * H / 9 * r.uniform(0.7, 1.3)))):
        w = r.uniform(1.4, min(4.8, L)); h = w * r.uniform(0.7, 1.7); h = min(h, H)
        u = r.uniform(u0 + w / 2, max(u0 + w / 2, u1 - w / 2)); v = r.uniform(z0, max(z0, z1 - h))
        overlay_("vlek%d" % r.randint(1, 4), vl, u, v, w, h, r.random() < 0.5, r.random() < 0.3)
    u = u0
    while u < u1 - 0.5:                                   # vuilstrepen onder de kroonlijst
        w = r.uniform(2.0, 4.0); h = r.uniform(1.2, min(3.2, H * 0.6)); uc = min(u + w / 2, u1 - w / 2)
        if r.random() < 0.6: overlay_("streep", vl, uc, z1 - h, w, h, r.random() < 0.5, True)
        u += w * r.uniform(1.0, 2.2)
    u = u0
    while u < u1 - 0.3:                                   # vochtige voet
        w = min(r.uniform(2.5, 4.0), L); uc = min(u + w / 2, u1 - w / 2)
        overlay_("voet", vl, uc, z0, w, r.uniform(0.9, 1.6), r.random() < 0.5); u += w * 0.8


def quad(rol, pts):
    bm = G[rol]; vs = [bm.verts.new(p) for p in pts]
    try: bm.faces.new(vs)
    except ValueError: pass


def doos(rol, x0, x1, y0, y1, z0, z1):
    c = [Vector((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        quad(rol, [c[i] for i in f])


class Vlak:
    """gevelvlak: oorsprong O (op de muur), U horizontaal, V omhoog, N naar buiten"""
    def __init__(self, O, U, N): self.O, self.U, self.N = Vector(O), Vector(U), Vector(N); self.V = Vector((0, 0, 1))
    def p(self, u, v, n=0.0): return self.O + self.U * u + self.V * v + self.N * n


def strip(rol, vl, pad, w=0.16, d=0.12):
    """lijst (rechthoekige doorsnede w x d) langs een 2D-pad (u, v) op een gevelvlak"""
    for (u0, v0), (u1, v1) in zip(pad, pad[1:]):
        t = Vector((u1 - u0, v1 - v0)); L = t.length
        if L < 1e-6: continue
        t /= L; nn = Vector((-t.y, t.x)) * (w / 2)
        a0, a1 = Vector((u0, v0)) - t * (w / 2) * 0.5, Vector((u1, v1)) + t * (w / 2) * 0.5
        hk = [a0 - nn, a1 - nn, a1 + nn, a0 + nn]
        bot = [vl.p(q.x, q.y, 0.0) for q in hk]; top = [vl.p(q.x, q.y, d) for q in hk]
        quad(rol, top)
        for i in range(4): quad(rol, [bot[i], bot[(i + 1) % 4], top[(i + 1) % 4], top[i]])


def spitsboog(xc, w, v0, vs, n=8, r_f=0.75):
    """omtrek van een spitsboog: (u, v) van linksonder via de top naar rechtsonder"""
    r = w * r_f; x0 = xc - w / 2
    ca = (w / 2 - r) / r; ta = math.acos(max(-1, min(1, ca)))
    links = [(x0 + r + r * math.cos(math.pi - (math.pi - ta) * k / n), vs + r * math.sin(math.pi - (math.pi - ta) * k / n)) for k in range(n + 1)]
    rechts = [(2 * xc - u, v) for u, v in links[::-1]]
    return [(x0, v0)] + links + rechts[1:] + [(xc + w / 2, v0)]


def vul(rol, vl, omtrek, n=0.09):
    """vlak gevuld met een waaier vanuit het midden (raam/deur), n voor de muur"""
    c = (sum(u for u, _ in omtrek) / len(omtrek), sum(v for _, v in omtrek) / len(omtrek))
    for a, b in zip(omtrek, omtrek[1:] + omtrek[:1]):
        quad(rol, [vl.p(*c, n), vl.p(*a, n), vl.p(*b, n)])


def raam(vl, xc, w, v0, vs):
    om = spitsboog(xc, w, v0, vs)
    vul("raam", vl, om, 0.09); strip("lijst", vl, om, 0.12, 0.08)
    strip("lijst", vl, [(xc - w / 2 - 0.12, v0 - 0.05), (xc + w / 2 + 0.12, v0 - 0.05)], 0.12, 0.12)


def nis(vl, xc, w, v0, vs, raam_w=0.55):
    om = spitsboog(xc, w, v0, vs, 10)
    strip("lijst", vl, om, 0.2, 0.14)                     # verhoogde boogrand: leest als verdiepte nis
    strip("lijst", vl, [(xc - w / 2 - 0.2, v0), (xc + w / 2 + 0.2, v0)], 0.16, 0.16)
    if raam_w: raam(vl, xc, raam_w, vs - 0.9, vs + 0.15)


def kantelen(vl, u0, u1, z, w=0.7, h=0.8, dik=0.35, tussen=0.38):
    """getrapte Moorse kantelen langs de bovenrand van een gevelvlak (3 treden)"""
    n = max(1, int((u1 - u0 + tussen) / (w + tussen)))
    st = (u1 - u0 - n * w) / max(1, n - 1) if n > 1 else 0
    for k in range(n):
        uc = u0 + w / 2 + k * (w + st) if n > 1 else (u0 + u1) / 2
        for j, f in enumerate((1.0, 0.68, 0.36)):
            a = vl.p(uc - w * f / 2, 0, -dik); b = vl.p(uc + w * f / 2, 0, 0)
            lo = Vector((min(a.x, b.x), min(a.y, b.y), z + h * j / 3)); hi = Vector((max(a.x, b.x), max(a.y, b.y), z + h * (j + 1) / 3))
            doos("stuc", lo.x, hi.x, lo.y, hi.y, lo.z, hi.z)


def borstwering(vl, h, z, vtop, dik=0.35, n=60):
    """muurtje bovenop een gevel: onderkant op z, bovenrand v = vtop(u) (golvend), van u=-h tot h, dikte naar binnen"""
    us = [-h + 2 * h * k / n for k in range(n + 1)]
    for a, b in zip(us, us[1:]):
        ta, tb = vtop(a), vtop(b)
        for nn in (0.0, -dik):
            q = [vl.p(a, z, nn), vl.p(b, z, nn), vl.p(b, tb, nn), vl.p(a, ta, nn)]
            quad("stuc", q if nn == 0 else q[::-1])
        quad("stuc", [vl.p(a, ta, 0), vl.p(b, tb, 0), vl.p(b, tb, -dik), vl.p(a, ta, -dik)])
    for u in (-h, h):
        quad("stuc", [vl.p(u, z, 0), vl.p(u, vtop(u), 0), vl.p(u, vtop(u), -dik), vl.p(u, z, -dik)])


def golfrand(h, z, hoog, laag, golf=0.12, periode=0.55):
    """Moorse bovenrand (Fata2013): hol oplopend naar de hoeken, met kleine golfjes erop"""
    def f(u):
        t = abs(u) / h
        return z + laag + (hoog - laag) * t ** 3.2 + golf * abs(math.sin(math.pi * u / periode))
    return f


def lobben(h, z, r=0.3, n=4):
    """ronde lobben met puntje (bovenstuk rond de koepel)"""
    w = 2 * h / n
    def f(u):
        k = min(n - 1, int((u + h) / w)); c = -h + (k + 0.5) * w; x = (u - c) / (w / 2)
        return z + r * math.sqrt(max(0.0, 1 - x * x)) * 1.6 + 0.08 + max(0.0, 0.18 * (1 - abs(x) * 6))
    return f


def blok(W, Dd, z0, z1, lisene, kantel_w, kantel_h, lisene_top, rand="golf"):
    """rechthoekig blok met hoeklisenen; geeft de 4 gevelvlakken (voor, rechts, achter, links)"""
    doos("stuc", -W / 2, W / 2, -Dd / 2, Dd / 2, z0, z1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = sorted((sx * W / 2, sx * (W / 2 - lisene))); y0, y1 = sorted((sy * Dd / 2, sy * (Dd / 2 - lisene)))
            doos("stuc", x0 - (0.12 if sx < 0 else 0), x1 + (0.12 if sx > 0 else 0), y0 - (0.12 if sy < 0 else 0), y1 + (0.12 if sy > 0 else 0), z0, lisene_top)
            # getrapte kap op de lisene
            cx, cy = sx * (W / 2 - lisene / 2), sy * (Dd / 2 - lisene / 2)
            for j, f in enumerate((1.15, 0.8, 0.45)):
                h = 0.22; s = (lisene + 0.24) * f / 2
                doos("stuc", cx - s, cx + s, cy - s, cy + s, lisene_top + h * j, lisene_top + h * (j + 1))
            lathe("stuc", [(0.14, 0.0), (0.0, 0.4)], lisene_top + 0.66, 8, (cx, cy))
            for c_ in [Vector((cx, cy, 0))]: pass
    vlakken = [Vlak((0, Dd / 2, 0), (1, 0, 0), (0, 1, 0)), Vlak((W / 2, 0, 0), (0, -1, 0), (1, 0, 0)),
               Vlak((0, -Dd / 2, 0), (-1, 0, 0), (0, -1, 0)), Vlak((-W / 2, 0, 0), (0, 1, 0), (-1, 0, 0))]
    breed = [W, Dd, W, Dd]
    for vl, b in zip(vlakken, breed):
        h = b / 2 - lisene
        f = golfrand(h, z1, lisene_top - z1 + 0.35, 0.3) if rand == "golf" else lobben(h, z1, 0.34)
        borstwering(vl, h, z1, f, 0.3)
    return vlakken, breed


def lathe(rol, profiel, z0, seg=32, c=(0, 0)):
    ringen = [[Vector((c[0] + r * math.cos(2 * math.pi * k / seg), c[1] + r * math.sin(2 * math.pi * k / seg), z0 + z)) for k in range(seg)] for r, z in profiel]
    for a, b in zip(ringen, ringen[1:]):
        for k in range(seg):
            quad(rol, [a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]])


def bol(rol, c, r, seg=16):
    lathe(rol, [(r * math.sin(math.pi * k / 8), -r * math.cos(math.pi * k / 8)) for k in range(9)], c, seg)


def bouw():
    # onderblok (7 x 6 x 10 m)
    W, Dd, H = 7.0, 6.0, 10.0
    vl, br = blok(W, Dd, 0.0, H, 0.7, 0.72, 0.85, H + 1.25)
    for v, b in zip(vl, br):
        h = b / 2 - 0.7
        strip("lijst", v, [(-h, 0.25), (h, 0.25)], 0.5, 0.1)            # plint
        strip("lijst", v, [(-h, 3.35), (h, 3.35)], 0.22, 0.14)          # band boven het portaal
        strip("lijst", v, [(-h, 9.55), (h, 9.55)], 0.3, 0.18)           # kroonlijst
    for k, (v, b) in enumerate(zip(vl, br)): verwering(v, -b / 2 + 0.7, b / 2 - 0.7, 0.0, 9.3, 11 + k)
    voor, rechts, achter, links = vl
    nis(voor, -1.45, 2.0, 3.75, 7.4); nis(voor, 1.45, 2.0, 3.75, 7.4)
    strip("lijst", voor, [(0, 3.5), (0, 9.4)], 0.18, 0.1)                # middenlisene tussen de nissen
    deur = spitsboog(0, 1.5, 0.0, 1.85, 8)
    vul("deur", voor, deur, 0.09); strip("lijst", voor, deur, 0.22, 0.15)
    for v in (rechts, links):
        nis(v, 0.0, 2.4, 3.75, 7.4)
    # bovenstuk (4,6 m) op het onderblok
    W2 = 4.6
    vl2, br2 = blok(W2, W2, H, 14.4, 0.5, 0.56, 0.68, 14.85, rand="lob")
    for k, v in enumerate(vl2): verwering(v, -W2 / 2 + 0.5, W2 / 2 - 0.5, H, 13.8, 21 + k)
    for v in vl2:
        h = W2 / 2 - 0.5
        strip("lijst", v, [(-h, H + 0.95), (h, H + 0.95)], 0.2, 0.12)
        strip("lijst", v, [(-h, 13.95), (h, 13.95)], 0.25, 0.15)
        raam(v, -0.62, 0.6, H + 1.4, H + 2.55); raam(v, 0.62, 0.6, H + 1.4, H + 2.55)
    # trommel, koepel, spits
    lathe("stuc", [(1.7, 0.0), (1.7, 0.75)], 14.4)
    lathe("lijst", [(1.7, 0.0), (1.82, 0.0), (1.82, 0.14), (1.7, 0.14)], 15.1)
    koepel = [(1.74, 0.0), (1.86, 0.25), (1.9, 0.55), (1.84, 0.9), (1.66, 1.25), (1.35, 1.6), (0.95, 1.88), (0.55, 2.1), (0.2, 2.28), (0.05, 2.36), (0.0, 2.38)]
    lathe("koepel", koepel, 15.24, 40)
    top = 15.24 + 2.36
    lathe("goud", [(0.14, 0.0), (0.05, 0.12), (0.05, 1.7), (0.0, 1.9)], top - 0.05, 12)
    for dz, r in ((0.35, 0.17), (0.8, 0.12), (1.18, 0.085)):
        bol("goud", top + dz, r)


def uv_en_objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in G.items():
        if not bm.faces: continue
        if rol not in OVERLAY and rol not in ("raam", "deur"):
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()                                   # vlakken zonder recalc hebben anders normaal (0,0,0) -> verkeerde UV-as
        uvl = bm.loops.layers.uv.verify(); s = UVS[rol]
        for f in ([] if rol in OVERLAY else bm.faces):
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.y / s, co.z / s) if ax == 0 else (co.x / s, co.z / s) if ax == 1 else (co.x / s, co.y / s)
        me = bpy.data.meshes.new("FM_toren_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_toren_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "toren"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*KLEUR[rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 1200, 1200
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 40
    for naam, pos in (("toren_voor", (2.0, 34.0, 4.0)), ("toren_schuin", (-20.0, 26.0, 6.0))):
        p = Vector(pos); q = Vector((0, 0, 9.0)); cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(uit, naam + ".png"); bpy.ops.render.render(write_still=True)


def main():
    if os.path.exists(MASTER): bpy.ops.wm.open_mainfile(filepath=MASTER)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); uv_en_objecten()
    bpy.ops.wm.save_as_mainfile(filepath=MASTER)
    print("[02_toren] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "02_toren"); os.makedirs(uit, exist_ok=True); render(uit)


main()
