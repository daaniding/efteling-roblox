"""18_route: de vaarroute van Fata Morgana met de scènekamers, ALLEEN als ruwe ruimtes (Daan 18 nov: "alleen ff de route maken met
de kamers niet hoe ze eruit zien"). Vorm uit de Eftepedia-plattegrond via build/18p_routeplan.py (ref/route_plan.npz) en build/18h_hoogte.py (ref/route_hoogte.npz):
  - vaargoot (blauw op de plattegrond, secties 1-14): bodem op z -3,7; water = Terrain-water tot z -3,2 (in Studio, plaats_routewater)
  - scènevlakken (zandkleur = de kamers waar later de scènes komen): verhoogd toneel tot z -2,6
  - muren langs de buitenrand van elke kamer en scheidingsmuren tussen kamers die op de plattegrond naast elkaar liggen maar ver uit
    elkaar op de route (bv. sectie 4 en 11); enkelzijdige vlakken naar de kamer; plafond per kamer (19 nov, Daan: "misschien moeten de kamers hoger"):
    tot onder het dak van het gebouwblok erboven (meestal z 7,25, bodemvlakken weg via 18k_knip), laag (z -0,05) onder de gang/het
    koepelgebouw waar je loopt; treden tussen hoogtes dicht; bij onze hal geen extra muur (die heeft al doorvaarten in de noord- en westmuur)
Nog niets aan aankleding of scènes. Modelstelsel = 02/03. Deel "route". Gebruik: blender --background --python build/18_route.py"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]
L, prisma = G3["L"], G3["prisma"]
OWNER = "phase:18_route"
KL = {"routebodem": (0.08, 0.09, 0.1), "toneel": (0.32, 0.27, 0.22), "routewand": (0.3, 0.27, 0.24), "routeplafond": (0.06, 0.06, 0.07), "plafondtrede": (0.06, 0.06, 0.07)}
for r, k in KL.items(): T["KLEUR"][r] = k; T["UVS"][r] = 4.0; T["G"][r] = bmesh.new()
ZB, ZW, ZT, ZP0, ZP1 = -3.7, -3.2, -2.6, -0.05, 0.12


def klem(x0, y0, x1, y1):
    """niets in onze instaphal laten uitsteken (doorvaarten stoppen in de muur)"""
    if x1 > -3.8 and y0 < -323.3:
        if x0 < -3.55: x1 = min(x1, -3.55)
        else: y0 = max(y0, -323.5)
    return x0, y0, x1, y1


def vlak(rol, pts, wil):
    bm = T["G"][rol]; f = bm.faces.new([bm.verts.new(q) for q in pts]); f.normal_update()
    if f.normal.dot(wil) < 0: f.normal_flip()


def plat(rol, x0, y0, x1, y1, z, op):
    x0, y0, x1, y1 = klem(x0, y0, x1, y1)
    if x1 - x0 < 0.01 or y1 - y0 < 0.01: return
    vlak(rol, [L(x0, y0) + Vector((0, 0, z)), L(x1, y0) + Vector((0, 0, z)), L(x1, y1) + Vector((0, 0, z)), L(x0, y1) + Vector((0, 0, z))],
         Vector((0, 0, 1 if op else -1)))


def wand(rol, seg, z0, z1, uitw, naar_binnen):
    """verticaal vlak langs een contourlijn; uitw = verschuiving naar buiten (m); normaal naar binnen of buiten"""
    ax, ay, bx, by, nx, ny = seg
    a, b, n = Vector((ax, ay, 0)), Vector((bx, by, 0)), Vector((nx, ny, 0))
    t = (b - a).normalized(); a -= t * 0.05; b += t * 0.05
    a += n * uitw; b += n * uitw
    pa, pb = L(a.x, a.y), L(b.x, b.y)
    vlak(rol, [pa + Vector((0, 0, z0)), pb + Vector((0, 0, z0)), pb + Vector((0, 0, z1)), pa + Vector((0, 0, z1))], -n if naar_binnen else n)


def rects(m, X0, Y1, S):
    uitr, open_ = [], {}
    for r in range(m.shape[0] + 1):
        runs = set()
        if r < m.shape[0]:
            row = m[r]; c = 0
            while c < len(row):
                if row[c]:
                    c0 = c
                    while c < len(row) and row[c]: c += 1
                    runs.add((c0, c))
                else: c += 1
        for k in list(open_):
            if k not in runs: uitr.append((k[0], open_.pop(k), k[1], r))
        for k in runs:
            if k not in open_: open_[k] = r
    return [(X0 + c0 * S, Y1 - r1 * S, X0 + c1 * S, Y1 - r0 * S) for (c0, r0, c1, r1) in uitr]


def schuif(a, dr, dc, vul):
    b = np.full_like(a, vul); H, W = a.shape
    b[max(dr, 0):H + min(dr, 0), max(dc, 0):W + min(dc, 0)] = a[max(-dr, 0):H + min(-dr, 0), max(-dc, 0):W + min(-dc, 0)]
    return b


def plafondraster(P):
    """plafond-z op het fijne raster (0,1 m): kamers + 0,3 m rand (over de muren heen); hoogte uit 18h (0,25 m-raster),
    randcellen nemen de LAAGSTE buurhoogte (nooit hoger dan een kamer ernaast, zodat er niets in de gang erboven uitsteekt)"""
    uni = P["blauw_fijn"] | P["zand_fijn"]; S, X0, Y1 = 0.1, float(P["X0"]), float(P["Y1"])
    Hh = np.load(os.path.join(D, "ref", "route_hoogte.npz")); hc = Hh["plafond"].copy()
    for _ in range(4):                                                      # lege grove cellen aan de rand: laagste buur (fijn kamerraster is ruimer)
        best = np.full(hc.shape, np.inf)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            q = schuif(hc, dr, dc, np.nan); best = np.fmin(best, np.where(np.isnan(q), np.inf, q))
        hc = np.where(np.isnan(hc) & np.isfinite(best), best, hc)
    rr = (np.arange(uni.shape[0]) * S / 0.25).astype(int).clip(0, hc.shape[0] - 1)
    cc = (np.arange(uni.shape[1]) * S / 0.25).astype(int).clip(0, hc.shape[1] - 1)
    h = hc[rr][:, cc]
    h = np.where(uni, np.nan_to_num(h, nan=ZP0), np.nan)
    h[uni & np.isnan(h)] = ZP0
    for _ in range(3):                                                      # 3 x 0,1 m rand
        best = np.full(h.shape, np.inf)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            b = schuif(h, dr, dc, np.nan); best = np.fmin(best, np.where(np.isnan(b), np.inf, b))
        h = np.where(np.isnan(h) & np.isfinite(best), best, h)
    return h, X0, Y1, S


def bouw():
    P = np.load(os.path.join(D, "ref", "route_plan.npz"))
    for x0, y0, x1, y1 in P["r_blauw"]: plat("routebodem", x0, y0, x1, y1, ZB, True)
    for x0, y0, x1, y1 in P["r_zand"]: plat("toneel", x0, y0, x1, y1, ZT, True)
    h, X0, Y1, S = plafondraster(P)
    niveaus = np.unique(h[~np.isnan(h)])
    for z in niveaus:                                                       # plafond per hoogte
        for x0, y0, x1, y1 in rects(np.isclose(h, z), X0, Y1, S): plat("routeplafond", x0, y0, x1, y1, z, False)
    # treden in het plafond: verticaal vlak op de grens van twee hoogtes, naar de hoge kant (die zie je van onderaf)
    hn = np.nan_to_num(h, nan=-99)
    for as_ in (0, 1):
        a = hn if as_ == 0 else hn.T
        for i in range(a.shape[0] - 1):
            boven, onder = a[i], a[i + 1]                                   # rij i en i+1 delen de rand
            j = 0
            while j < a.shape[1]:
                if boven[j] > -90 and onder[j] > -90 and abs(boven[j] - onder[j]) > 0.01:
                    j0, hb, ho = j, boven[j], onder[j]
                    while j < a.shape[1] and boven[j] == hb and onder[j] == ho: j += 1
                    zl, zh = min(hb, ho), max(hb, ho)
                    if as_ == 0:                                            # horizontale rand op y = Y1 - (i+1) S
                        yy = Y1 - (i + 1) * S; xa, xb = X0 + j0 * S, X0 + j * S
                        pa, pb = L(xa, yy), L(xb, yy); naar = Vector((0, 1 if hb > ho else -1, 0))
                    else:                                                   # verticale rand op x = X0 + (i+1) S
                        xx = X0 + (i + 1) * S; ya, yb = Y1 - j0 * S, Y1 - j * S
                        pa, pb = L(xx, ya), L(xx, yb); naar = Vector((-1 if hb > ho else 1, 0, 0))
                    nw = L(naar.x, naar.y) - L(0, 0); nw.z = 0
                    vlak("plafondtrede", [pa + Vector((0, 0, zl)), pb + Vector((0, 0, zl)), pb + Vector((0, 0, zh)), pa + Vector((0, 0, zh))], nw)
                else: j += 1
    for seg in P["toneelrand"]: wand("toneel", seg, ZB, ZT, 0.0, False)          # zijkant toneel naar het water
    hf = np.nan_to_num(h, nan=ZP0)
    for seg in P["muren"]:                                                  # muren tot het plafond van de kamer ernaast (hoogste langs de muur)
        ax, ay, bx, by, nx, ny = seg; top = ZP0
        for t in np.linspace(0, 1, 6):
            x, y = ax + (bx - ax) * t - nx * 0.15, ay + (by - ay) * t - ny * 0.15
            r, c = int((Y1 - y) / S), int((x - X0) / S)
            if 0 <= r < hf.shape[0] and 0 <= c < hf.shape[1]: top = max(top, hf[r, c])
        wand("routewand", seg, ZB - 0.05, top + 0.01, 0.05, True)


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol in KL:
        bm = T["G"][rol]
        if not bm.faces: continue
        bm.normal_update()                                                       # vlakken hebben al de goede kant
        uvl = bm.loops.layers.uv.verify()
        for f in bm.faces:
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co; lp[uvl].uv = (co.y / 4, co.z / 4) if ax == 0 else (co.x / 4, co.z / 4) if ax == 1 else (co.x / 4, co.y / 4)
        me = bpy.data.meshes.new("FM_route_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_route_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "route"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*KL[rol], 1); me.materials.append(m); col.objects.link(o)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[18_route] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")


main()
