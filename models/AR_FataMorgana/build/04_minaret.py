"""04_minaret: stap 3 — de minaret op het plein (Fmplein1986.jpg, FataVoorplein1993.jpg; AHN-top 25,6 m bij park (19,5; -329)).
Maten (Fmplein1986: 25,6 px/m): onderblok 4,6 m breed tot 8,5 m (zandkleurig, hoekblokken, spitsboogdeur met rode omlijsting in
een tegelpaneel, boogvensters, rode zigzagfries), wit balkon met vier bollen; witte bovenschacht 3,2 m tot 17,8 m met
boogvenstertjes en donkere hoeklijnen; tweede balkon met blauwe tegelborstwering; lantaarntje met boogopeningen; geribde
turquoise koepel; gouden spits met halve maan. Deur naar het plein (oost, +x).
Modelstelsel = 02/03 (oorsprong park -40; -295). Deel "minaret".
Gebruik: blender --background --python build/04_minaret.py -- [--render]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F3 = os.path.join(D, "build", "03_noordgevel.py")
G3 = {"__file__": F3, "__name__": "lib"}
exec(compile(open(F3).read().rsplit("\nmain()", 1)[0], F3, "exec"), G3)
T = G3["T"]; L, prisma, lathe, quad, strip, spitsboog, vul, raam, Vlak = (G3[k] for k in ("L", "prisma", "lathe", "quad", "strip", "spitsboog", "vul", "raam", "Vlak"))
OWNER = "phase:04_minaret"
VAST = ("zellige", "zigzag", "balkon", "fries", "tegelhal", "deurblad")
EIGEN = ("raam", "deur", "poort", "poortrand", "zandvlak", "gangwand", "groenneg")                 # vaste windingsrichting, geen recalc
T["KLEUR"].update({"zandsteen": (0.84, 0.72, 0.56), "wit": (0.95, 0.94, 0.9), "rood": (0.66, 0.18, 0.14), "zellige": (0.2, 0.5, 0.6),
                   "zigzag": (0.66, 0.18, 0.14), "balkon": (0.85, 0.88, 0.95), "donker": (0.12, 0.16, 0.22),
                   "fries": (0.2, 0.3, 0.6), "poort": (0.05, 0.05, 0.07), "poortrand": (0.95, 0.94, 0.9),
                   "tegelhal": (0.6, 0.27, 0.18), "deurblad": (0.75, 0.5, 0.25), "vloertegel": (0.65, 0.42, 0.33), "zandvlak": (0.84, 0.72, 0.56), "botsing": (1.0, 0.0, 1.0), "groen": (0.25, 0.58, 0.5), "groenneg": (0.25, 0.58, 0.5), "gangwand": (0.96, 0.92, 0.84)})
T["UVS"].update({"zandsteen": 9.0, "wit": 9.0, "rood": 1.0, "zellige": 1.0, "zigzag": 1.0, "balkon": 1.0, "donker": 1.0, "fries": 1.0, "poort": 1.0, "poortrand": 1.0, "tegelhal": 1.0, "deurblad": 1.0, "vloertegel": 2.0, "zandvlak": 9.0, "botsing": 1.0, "groen": 1.0, "groenneg": 1.0, "gangwand": 9.0})
T["OVERLAY"] = tuple(T["OVERLAY"]) + VAST
for r in T["KLEUR"]: T["G"][r] = bmesh.new()

C = L(19.5, -329.0)


def vlakken(hw):
    """vier gevels van een vierkant (halve breedte hw) om C: (Vlak, breedte); u loopt van -hw tot hw"""
    out = []
    for N in (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((-1, 0, 0)), Vector((0, -1, 0))):
        U = Vector((N.y, -N.x, 0))
        out.append(Vlak(C + N * hw, U, N))
    return out


def paneel(rol, vl, u0, u1, v0, v1, n, su, sv, du=0.0, dv=0.0):
    """vlak met eigen UV (tegels, friezen): u/su, v/sv"""
    bm = T["G"][rol]; uvl = bm.loops.layers.uv.verify()
    pts = [vl.p(u0, v0, n), vl.p(u1, v0, n), vl.p(u1, v1, n), vl.p(u0, v1, n)][::-1]
    uv = [((u0 + du) / su, (v0 - dv) / sv), ((u1 + du) / su, (v0 - dv) / sv), ((u1 + du) / su, (v1 - dv) / sv), ((u0 + du) / su, (v1 - dv) / sv)][::-1]
    f = bm.faces.new([bm.verts.new(p) for p in pts])
    for lp, t in zip(f.loops, uv): lp[uvl].uv = t


def blok(rol, hw, z0, z1):
    prisma(rol, [C + Vector((sx * hw, sy * hw, 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], z0, z1)


def band(rol, hw, z0, z1, n=0.02, su=1.5):
    for vl in vlakken(hw):
        paneel(rol, vl, -hw, hw, z0, z1, n, su, z1 - z0, 0.0, z0)


def balkon(hw, z, h_rand, rol_rand, bollen):
    """overstekend balkon: getrapte consoles, vloerplaat, borstwering (rondom), hoekpaaltjes met bollen"""
    for k, f in enumerate((0.25, 0.5, 0.75)):
        blok("lijst", hw - 0.4 + f * 0.55, z - 0.45 + k * 0.15, z - 0.3 + k * 0.15)
    blok("lijst", hw + 0.4, z, z + 0.16)
    hb = hw + 0.32
    for vl in vlakken(hb):
        prisma("wit", [Vector((p.x, p.y, 0)) for p in (vl.p(-hb, 0, 0), vl.p(hb, 0, 0), vl.p(hb, 0, -0.16), vl.p(-hb, 0, -0.16))], z + 0.16, z + 0.16 + h_rand)
        if rol_rand: paneel(rol_rand, vl, -hb + 0.25, hb - 0.25, z + 0.24, z + 0.08 + h_rand, 0.04, 1.0, h_rand - 0.16, 0.0, z + 0.24)
    blok("lijst", hb + 0.05, z + 0.16 + h_rand, z + 0.26 + h_rand) if False else None
    for vl in vlakken(hb):
        prisma("lijst", [Vector((p.x, p.y, 0)) for p in (vl.p(-hb - 0.05, 0, 0.05), vl.p(hb + 0.05, 0, 0.05), vl.p(hb + 0.05, 0, -0.22), vl.p(-hb - 0.05, 0, -0.22))],
               z + 0.16 + h_rand, z + 0.26 + h_rand)
    if bollen:
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = C + Vector((sx * (hb - 0.08), sy * (hb - 0.08), 0))
            prisma("wit", [p + Vector((a, b, 0)) * 0.17 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], z + 0.16, z + 0.36 + h_rand)
            lathe("wit", [(r * 0.2, zz) for r, zz in ((0.0, -0.2), (0.7, -0.15), (1.0, 0.0), (0.7, 0.15), (0.0, 0.22))], z + 0.62 + h_rand, 12, (p.x, p.y))


def vlak_n(rol, pts, wil, uvs=None):
    """vlak met vaste windingsrichting: normaal wijst naar 'wil' (Vector); optioneel eigen UV"""
    pts = [p for i, p in enumerate(pts) if (p - pts[i - 1]).length > 1e-6]
    if len(pts) < 3: return
    nrm = (pts[1] - pts[0]).cross(pts[2] - pts[0])
    if len(pts) > 3 and nrm.length < 1e-9: nrm = (pts[2] - pts[0]).cross(pts[3] - pts[0])
    if nrm.dot(wil) < 0: pts = pts[::-1]; uvs = uvs[::-1] if uvs else None
    bm = T["G"][rol]; f = bm.faces.new([bm.verts.new(p) for p in pts])
    if uvs:
        uvl = bm.loops.layers.uv.verify()
        for lp, t in zip(f.loops, uvs): lp[uvl].uv = t


def schulpboog(w, vs, r_f=0.85, lobben=9, diep=0.11, n=72):
    """geschulpte (veelpassige) spitsboog: (u, v) van de linkerneg via de top naar de rechterneg; de lobben bollen naar
    buiten, de punten ertussen wijzen naar binnen (Fmplein1986, POV-video 2025)"""
    basis = spitsboog(0, w, 0.0, vs, n // 2, r_f)[1:-1]
    # booglengte-parameter
    ls = [0.0]
    for a, b in zip(basis, basis[1:]): ls.append(ls[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    S = ls[-1]; out = []
    for k in range(n + 1):
        s_ = S * k / n
        j = max(0, min(len(basis) - 2, next((i for i in range(len(ls) - 1) if ls[i + 1] >= s_), len(ls) - 2)))
        t = (s_ - ls[j]) / max(1e-9, ls[j + 1] - ls[j])
        a, b = basis[j], basis[j + 1]; u = a[0] + (b[0] - a[0]) * t; v = a[1] + (b[1] - a[1]) * t
        tu, tv = b[0] - a[0], b[1] - a[1]; L_ = math.hypot(tu, tv) or 1.0
        nu, nv = -tv / L_, tu / L_                                   # links van de looprichting = buiten (boog loopt links -> rechts)
        if nv < 0 and abs(u) < 0.05: nu, nv = -nu, -nv
        x = (s_ / S) * lobben; f = abs(math.sin(math.pi * (x - int(x)))) ** 0.6
        out.append((u + nu * diep * f, v + nv * diep * f))
    return out


def poort(vl, P=0.3, w=1.8, vs=1.9, pu=1.15, ph=4.9):
    """grote ingangspoort in de minaretvoet: vooruitstekend tegelpaneel (P m) met een geschulpte spitsboog-opening, diepe
    neggen, donkere doorgang, witte geschulpte rand, witte buitenboog met kielpunt, tegelfries erboven, zandstenen
    pijlers en kroonlijst"""
    vp = Vlak(vl.p(0, 0, P), vl.U, vl.N)
    boog = schulpboog(w, vs)
    om = [(-w / 2, 0.0)] + [(-w / 2, vs * k / 6) for k in range(1, 6)] + boog + [(w / 2, vs * k / 6) for k in range(5, 0, -1)] + [(w / 2, 0.0)]
    c = (0.0, 1.5)
    def raak(p):
        du, dv = p[0] - c[0], p[1] - c[1]; ts = []
        if du < -1e-9: ts.append(((-pu - c[0]) / du, "l"))
        if du > 1e-9: ts.append(((pu - c[0]) / du, "r"))
        if dv < -1e-9: ts.append(((0.0 - c[1]) / dv, "o"))
        if dv > 1e-9: ts.append(((ph - c[1]) / dv, "b"))
        t, kant = min(ts)
        return (c[0] + du * t, c[1] + dv * t), kant
    hoek = {("l", "b"): (-pu, ph), ("b", "l"): (-pu, ph), ("b", "r"): (pu, ph), ("r", "b"): (pu, ph),
            ("l", "o"): (-pu, 0.0), ("o", "l"): (-pu, 0.0), ("r", "o"): (pu, 0.0), ("o", "r"): (pu, 0.0)}
    hits = [raak(p) for p in om]
    for i in range(len(om) - 1):
        (h0, k0), (h1, k1) = hits[i], hits[i + 1]
        rand = [om[i], om[i + 1], h1] + ([hoek[(k1, k0)]] if k0 != k1 and (k1, k0) in hoek else []) + [h0]
        vlak_n("zellige", [vp.p(u, v, 0) for u, v in rand], vl.N, [(u / 1.2, v / 1.2) for u, v in rand])
    # neggen (wit) en donkere achterkant
    for (ua, va), (ub, vb) in zip(om, om[1:]):
        mu, mv = (ua + ub) / 2, (va + vb) / 2
        wil = vl.U * (c[0] - mu) + Vector((0, 0, c[1] - mv))
        vlak_n("poortrand", [vp.p(ua, va, 0), vp.p(ub, vb, 0), vl.p(ub, vb, 0.12), vl.p(ua, va, 0.12)], wil)
    vlak_n("poort", [vl.p(-w / 2 - 0.05, 0, 0.12), vl.p(w / 2 + 0.05, 0, 0.12), vl.p(w / 2 + 0.05, vs + 1.6, 0.12), vl.p(-w / 2 - 0.05, vs + 1.6, 0.12)], vl.N)
    # witte geschulpte rand op het paneel en witte buitenboog met kielpunt
    strip("wit", vp, boog, 0.16, 0.05)
    strip("wit", vp, [(-w / 2, 0.0), (-w / 2, vs)], 0.16, 0.05); strip("wit", vp, [(w / 2, 0.0), (w / 2, vs)], 0.16, 0.05)
    buiten = spitsboog(0, w + 0.55, 0.0, vs, 12, 0.85)[1:-1]
    top = max(v for _, v in buiten); buiten = [p for p in buiten if p[1] < top - 0.12]
    hlft = len(buiten) // 2
    buiten = buiten[:hlft] + [(0.0, top + 0.3)] + buiten[hlft:]
    strip("wit", vp, [(-(w + 0.55) / 2, 0.0)] + buiten + [((w + 0.55) / 2, 0.0)], 0.12, 0.05)
    # tegelfries boven de boog met lijsten
    vlak_n("fries", [vp.p(-pu + 0.08, 3.85, 0.02), vp.p(pu - 0.08, 3.85, 0.02), vp.p(pu - 0.08, 4.65, 0.02), vp.p(-pu + 0.08, 4.65, 0.02)], vl.N,
           [((-pu + 0.08) / 1.8, 0.0), ((pu - 0.08) / 1.8, 0.0), ((pu - 0.08) / 1.8, 1.0), ((-pu + 0.08) / 1.8, 1.0)])
    strip("lijst", vp, [(-pu, 3.78), (pu, 3.78)], 0.12, 0.08); strip("lijst", vp, [(-pu, 4.72), (pu, 4.72)], 0.12, 0.08)
    # zandstenen pijlers en kroonlijst (vooruitstekend portaal)
    for a, b in ((-pu - 0.25, -pu), (pu, pu + 0.25)):
        prisma("lijst", [Vector((q.x, q.y, 0)) for q in (vl.p(a, 0, -0.02), vl.p(b, 0, -0.02), vl.p(b, 0, P + 0.06), vl.p(a, 0, P + 0.06))], 0.0, ph + 0.05)
    prisma("lijst", [Vector((q.x, q.y, 0)) for q in (vl.p(-pu - 0.32, 0, -0.02), vl.p(pu + 0.32, 0, -0.02), vl.p(pu + 0.32, 0, P + 0.14), vl.p(-pu - 0.32, 0, P + 0.14))], ph, ph + 0.22)
    # bovenkant en onderkant van het portaal (tussen muur en paneel)
    vlak_n("zellige", [vl.p(-pu, ph, 0), vl.p(pu, ph, 0), vl.p(pu, ph, P), vl.p(-pu, ph, P)], Vector((0, 0, -1)), [(0, 0), (1, 0), (1, 0.25), (0, 0.25)])


def zijdeur_en_halletje(hw, HZ=3.2, t=0.5):   # t 0,5: de hoekblokken (tot 1,8 m uit het midden) blijven binnen de muur
    """minaretvoet onderin hol (POV-video 2025, 25-30 s): zijdeur in de zuidgevel vanuit de overdekte wachtrij (veranda),
    kielboog met dikke witte omlijsting, houten deurblad "Open" dat naar buiten open staat, en een halletje met
    roodbruine tegelwanden, wit plafond en tegelvloer. De rest van de toren (boven HZ) blijft een massief blok."""
    blok("zandsteen", hw, HZ, 8.4)
    x0, x1, y0, y1 = C.x - hw, C.x + hw, C.y - hw, C.y + hw          # modelcoordinaten
    def kast(ax, ay, bx, by): prisma("zandsteen", [Vector((ax, ay, 0)), Vector((bx, ay, 0)), Vector((bx, by, 0)), Vector((ax, by, 0))], 0.0, HZ)
    kast(x1 - t, y0, x1, y1); kast(x0 + t, y1 - t, x1 - t, y1)   # oost, noord (west: muur met de groene kielboog, hieronder)
    # zuidmuur met deuropening: vlakken met gat (waaier vanuit de deur), buiten en binnen, plus witte neggen
    vz = vlakken(hw)[3]                                              # zuid: u = 19,5 - x (park), n naar buiten (-y)
    # Daan: "hier past toch geen 1 Roblox-character in" -> 1,6 m breed (4,8 studs), top ~3,0 m net onder het verandadak
    uc, w, vs = 0.5, 1.6, 1.95                                       # deur bij park-x 19,0 (in de veranda)
    boog = spitsboog(uc, w, 0.0, vs, 10, 0.55)[1:-1]
    top = max(v for _, v in boog); hlft = len(boog) // 2
    boog = [p for p in boog[:hlft] if p[1] < top - 0.1] + [(uc, top + 0.16)] + [p for p in boog[hlft:] if p[1] < top - 0.1]   # kielpunt
    om = [(uc - w / 2, 0.0)] + [(uc - w / 2, vs * k / 4) for k in range(1, 4)] + boog + [(uc + w / 2, vs * k / 4) for k in range(3, 0, -1)] + [(uc + w / 2, 0.0)]
    c = (uc, 1.1)
    def raak(p, pu0, pu1, ph):
        du, dv = p[0] - c[0], p[1] - c[1]; ts = []
        if du < -1e-9: ts.append(((pu0 - c[0]) / du, "l"))
        if du > 1e-9: ts.append(((pu1 - c[0]) / du, "r"))
        if dv < -1e-9: ts.append(((0.0 - c[1]) / dv, "o"))
        if dv > 1e-9: ts.append(((ph - c[1]) / dv, "b"))
        tt, kant = min(ts); return (c[0] + du * tt, c[1] + dv * tt), kant
    for n_, wil, rol, uvs in ((0.0, vz.N, "zandvlak", None), (-t, -vz.N, "tegelhal", 1.0)):
        pu0, pu1 = (-hw, hw) if n_ == 0 else (-hw + t, hw - t)
        ph = HZ if n_ == 0 else HZ - 0.04
        hoek = {("l", "b"): (pu0, ph), ("b", "l"): (pu0, ph), ("b", "r"): (pu1, ph), ("r", "b"): (pu1, ph),
                ("l", "o"): (pu0, 0.0), ("o", "l"): (pu0, 0.0), ("r", "o"): (pu1, 0.0), ("o", "r"): (pu1, 0.0)}
        hits = [raak(p, pu0, pu1, ph) for p in om]
        nn = n_ if n_ == 0 else n_ - 0.02                              # tegels 2 cm voor de binnenkant
        for i in range(len(om) - 1):
            (h0, k0), (h1, k1) = hits[i], hits[i + 1]
            rand = [om[i], om[i + 1], h1] + ([hoek[(k1, k0)]] if k0 != k1 and (k1, k0) in hoek else []) + [h0]
            vlak_n(rol, [vz.p(u, v, nn) for u, v in rand], wil, [(u / uvs, v / uvs) for u, v in rand] if uvs else None)
    for (ua, va), (ub, vb) in zip(om, om[1:]):                       # neggen
        mu, mv = (ua + ub) / 2, (va + vb) / 2
        vlak_n("poortrand", [vz.p(ua, va, 0), vz.p(ub, vb, 0), vz.p(ub, vb, -t - 0.02), vz.p(ua, va, -t - 0.02)], vz.U * (c[0] - mu) + Vector((0, 0, c[1] - mv)))
    strip("wit", vz, om[1:-1], 0.26, 0.1)                             # dikke witte omlijsting
    strip("wit", vz, [om[0], om[1]], 0.26, 0.1); strip("wit", vz, [om[-2], om[-1]], 0.26, 0.1)
    # westmuur met de groene kielboog naar de gang (POV-video 2025, 30 s: groen omlijste kielboog met hek en bollen)
    vw = vlakken(hw)[2]                                              # west: u = y - C.y, n naar buiten (-x, de gang in)
    om2 = [(-w / 2, 0.0)] + [(-w / 2, vs * k / 4) for k in range(1, 4)] + [(u - uc, v) for u, v in boog] + [(w / 2, vs * k / 4) for k in range(3, 0, -1)] + [(w / 2, 0.0)]
    c2 = (0.0, 1.1)
    def raak2(p, pu0, pu1, ph):
        du, dv = p[0] - c2[0], p[1] - c2[1]; ts = []
        if du < -1e-9: ts.append(((pu0 - c2[0]) / du, "l"))
        if du > 1e-9: ts.append(((pu1 - c2[0]) / du, "r"))
        if dv < -1e-9: ts.append(((0.0 - c2[1]) / dv, "o"))
        if dv > 1e-9: ts.append(((ph - c2[1]) / dv, "b"))
        tt, kant = min(ts); return (c2[0] + du * tt, c2[1] + dv * tt), kant
    for n_, wil, rol, uvs in ((0.0, vw.N, "gangwand", None), (-t - 0.02, -vw.N, "tegelhal", 1.0)):
        pu0, pu1 = (-hw, hw) if n_ == 0 else (-hw + t, hw - t)
        ph = HZ if n_ == 0 else HZ - 0.04
        hoek = {("l", "b"): (pu0, ph), ("b", "l"): (pu0, ph), ("b", "r"): (pu1, ph), ("r", "b"): (pu1, ph),
                ("l", "o"): (pu0, 0.0), ("o", "l"): (pu0, 0.0), ("r", "o"): (pu1, 0.0), ("o", "r"): (pu1, 0.0)}
        hits = [raak2(p, pu0, pu1, ph) for p in om2]
        for i in range(len(om2) - 1):
            (h0, k0), (h1, k1) = hits[i], hits[i + 1]
            rand = [om2[i], om2[i + 1], h1] + ([hoek[(k1, k0)]] if k0 != k1 and (k1, k0) in hoek else []) + [h0]
            vlak_n(rol, [vw.p(u, v, n_) for u, v in rand], wil, [(u / uvs, v / uvs) for u, v in rand] if uvs else None)
    for (ua, va), (ub, vb) in zip(om2, om2[1:]):
        mu, mv = (ua + ub) / 2, (va + vb) / 2
        vlak_n("groenneg", [vw.p(ua, va, 0), vw.p(ub, vb, 0), vw.p(ub, vb, -t - 0.02), vw.p(ua, va, -t - 0.02)], vw.U * (c2[0] - mu) + Vector((0, 0, c2[1] - mv)))
    vbin = Vlak(vw.p(0, 0, -t - 0.02), -vw.U, -vw.N)                 # binnenkant (halletje): u' = -u
    for vl_, pad in ((vw, om2), (vbin, [(-u, v) for u, v in om2])):
        strip("groen", vl_, pad[1:-1], 0.22, 0.08); strip("groen", vl_, [pad[0], pad[1]], 0.22, 0.08); strip("groen", vl_, [pad[-2], pad[-1]], 0.22, 0.08)
    for a, b, z0, z1 in ((y0, C.y - w / 2, 0.0, HZ), (C.y + w / 2, y1, 0.0, HZ), (C.y - w / 2, C.y + w / 2, vs + 1.1, HZ)):
        prisma("botsing", [Vector((x0, a, 0)), Vector((x0 + t, a, 0)), Vector((x0 + t, b, 0)), Vector((x0, b, 0))], z0, z1)
    # binnenwanden noord, oost: tegels; plafond wit; vloer tegels (sluit aan op de verandavloer)
    hz = HZ - 0.04
    for a, b, wil in (((x0 + t, y1 - t - 0.02), (x1 - t, y1 - t - 0.02), Vector((0, -1, 0))),
                      ((x1 - t - 0.02, y1 - t), (x1 - t - 0.02, y0 + t), Vector((-1, 0, 0)))):
        A, B = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0)); lg = (B - A).length
        vlak_n("tegelhal", [A, B, B + Vector((0, 0, hz)), A + Vector((0, 0, hz))], wil, [(0, 0), (lg, 0), (lg, hz), (0, hz)])
    vlak_n("gangwand", [Vector((x0 + t, y0 + t, hz)), Vector((x1 - t, y0 + t, hz)), Vector((x1 - t, y1 - t, hz)), Vector((x0 + t, y1 - t, hz))], Vector((0, 0, -1)))   # plafond oud beige (Daan: "binnen overal die kleur")
    prisma("vloertegel", [Vector((x0 + t, L(0, -331.1).y + 0, 0)) * 0 + Vector((x0 + t, L(19.5, -331.1).y, 0)), Vector((x1 - t, L(19.5, -331.1).y, 0)),
                          Vector((x1 - t, y1 - t, 0)), Vector((x0 + t, y1 - t, 0))], -0.25, 0.12)
    # deurblad: hangt aan de westelijke neg en staat naar buiten open (haaks op de muur, de veranda in)
    xs = C.x - (uc + w / 2) + 0.03                                     # scharnierkant (park-x 18,45)
    ya, yb = y0 - 0.05, y0 - 0.05 - (w - 0.04)
    prisma("deur", [Vector((xs - 0.03, yb, 0)), Vector((xs + 0.03, yb, 0)), Vector((xs + 0.03, ya, 0)), Vector((xs - 0.03, ya, 0))], 0.03, vs + 0.45)
    for dx, wil in ((0.035, Vector((1, 0, 0))), (-0.035, Vector((-1, 0, 0)))):
        pts = [Vector((xs + dx, ya, 0.03)), Vector((xs + dx, yb, 0.03)), Vector((xs + dx, yb, vs + 0.45)), Vector((xs + dx, ya, vs + 0.45))]
        uvs = [(1, 0), (0, 0), (0, 1), (1, 1)] if dx > 0 else [(0, 0), (1, 0), (1, 1), (0, 1)]   # "Open" leesbaar vanuit de rij (oostkant)
        vlak_n("deurblad", pts, wil, uvs)
    prisma("goud", [Vector((xs + 0.03, yb + 0.12, 0)), Vector((xs + 0.09, yb + 0.12, 0)), Vector((xs + 0.09, yb + 0.26, 0)), Vector((xs + 0.03, yb + 0.26, 0))], 1.0, 1.04)   # klink
    # koperen filigraanlamp aan het plafond (Eftepedia: "aan het plafond is een lamp van koperfiligraan uit Marokko te vinden")
    lathe("goud", [(0.015, 0.0), (0.015, 0.45)], hz - 0.45, 6, (C.x, C.y))
    lathe("goud", [(r, z) for r, z in ((0.0, 0.0), (0.06, 0.02), (0.16, 0.12), (0.2, 0.26), (0.17, 0.4), (0.08, 0.5), (0.04, 0.56), (0.0, 0.6))], hz - 1.05, 8, (C.x, C.y))
    # botsing: de zuidmuur bestaat alleen uit gevelvlakken (botsen niet); onzichtbare blokken naast en boven de deur
    yb0, yb1 = y0, y0 + t
    for a, b, z0, z1 in ((x0, C.x - uc - w / 2, 0.0, HZ), (C.x - uc + w / 2, x1, 0.0, HZ), (C.x - uc - w / 2, C.x - uc + w / 2, vs + 1.1, HZ)):
        prisma("botsing", [Vector((a, yb0, 0)), Vector((b, yb0, 0)), Vector((b, yb1, 0)), Vector((a, yb1, 0))], z0, z1)
    # plint rondom, met een opening voor de deur
    for a, b in (((x0 - 0.08, y1 - 0.08), (x1 + 0.08, y1 + 0.08)), ((x1 - 0.08, y0 - 0.08), (x1 + 0.08, y1 + 0.08)),   # westkant: binnen (gang), geen plint
                 ((x0 - 0.08, y0 - 0.08), (C.x - uc - w / 2 - 0.15, y0 + 0.08)), ((C.x - uc + w / 2 + 0.15, y0 - 0.08), (x1 + 0.08, y0 + 0.08))):
        prisma("lijst", [Vector((a[0], a[1], 0)), Vector((b[0], a[1], 0)), Vector((b[0], b[1], 0)), Vector((a[0], b[1], 0))], 0.0, 0.35)


def bouw():
    # onderblok: zandsteen met hoekblokken (lijst), plint
    hw = 2.3
    zijdeur_en_halletje(hw)
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        p = C + Vector((sx * (hw - 0.22), sy * (hw - 0.22), 0))
        for k in range(14):                                # om-en-om lange en korte hoekblokken
            z0 = k * 0.56; l = 0.55 if k % 2 == 0 else 0.4
            prisma("lijst", [p + Vector((a * (0.28 if k % 2 == 0 else 0.25), b * (0.28 if k % 2 == 0 else 0.25), 0)) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], z0, z0 + 0.52)
    for i, vl in enumerate(vlakken(hw)):
        if i == 0:                                         # voorkant (oost): tegelpaneel met deur, vensters erboven
            poort(vl)                                      # grote poort (Eftepedia: hoofdingang op rustige dagen)
            raam(vl, -0.55, 0.5, 5.6, 6.9); raam(vl, 0.55, 0.5, 5.6, 6.9)
            paneel("zellige", vl, -1.05, 1.05, 5.3, 7.35, 0.04, 1.2, 1.2)
        else:
            raam(vl, 0.0, 0.6, 5.6, 7.0)
            paneel("zellige", vl, -0.75, 0.75, 5.3, 7.4, 0.04, 1.2, 1.2)
    band("zigzag", hw, 7.75, 8.4, 0.05)
    balkon(hw, 8.55, 0.85, None, True)
    # bovenschacht: wit, donkere hoeklijnen, boogvenstertjes
    hs = 1.6
    blok("wit", hs, 8.7, 18.1)
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        p = C + Vector((sx * hs, sy * hs, 0))
        prisma("donker", [p + Vector((a, b, 0)) * 0.06 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 9.6, 17.3)
    for vl in vlakken(hs):
        raam(vl, 0.0, 0.42, 10.6, 11.7); raam(vl, 0.0, 0.42, 14.3, 15.4)
        strip("lijst", vl, [(-hs + 0.12, 9.7), (-hs + 0.12, 17.1), (hs - 0.12, 17.1), (hs - 0.12, 9.7)], 0.08, 0.04)
    band("zigzag", hs, 17.6, 18.1, 0.05)
    for k, f in enumerate((0.1, 0.22, 0.34, 0.46)):           # diepe consolezone onder het tweede balkon (Fmplein1986)
        blok("lijst", hs + f, 18.1 + k * 0.2, 18.3 + k * 0.2)
    balkon(hs, 18.9, 1.0, "balkon", False)
    # lantaarntje met boogopeningen
    hl = 1.0; z0 = 19.06
    for vl in vlakken(hl):
        prisma("wit", [Vector((p.x, p.y, 0)) for p in (vl.p(-hl, 0, 0), vl.p(-0.42, 0, 0), vl.p(-0.42, 0, -0.18), vl.p(-hl, 0, -0.18))], z0, z0 + 2.15)
        prisma("wit", [Vector((p.x, p.y, 0)) for p in (vl.p(0.42, 0, 0), vl.p(hl, 0, 0), vl.p(hl, 0, -0.18), vl.p(0.42, 0, -0.18))], z0, z0 + 2.15)
        prisma("wit", [Vector((p.x, p.y, 0)) for p in (vl.p(-0.42, 0, 0), vl.p(0.42, 0, 0), vl.p(0.42, 0, -0.18), vl.p(-0.42, 0, -0.18))], z0 + 1.7, z0 + 2.15)
        paneel("zellige", vl, -0.92, -0.5, z0 + 0.25, z0 + 1.9, 0.04, 1.2, 1.2); paneel("zellige", vl, 0.5, 0.92, z0 + 0.25, z0 + 1.9, 0.04, 1.2, 1.2)
        om = spitsboog(0, 0.84, z0, z0 + 1.35, 8, 0.6)
        strip("lijst", vl, om, 0.08, 0.05)
    blok("donker", 0.8, z0, z0 + 2.1)
    blok("lijst", hl + 0.12, z0 + 2.15, z0 + 2.34)
    # geribde turquoise koepel + spits met halve maan
    zk = z0 + 2.34
    lathe("lijst", [(0.98, 0.0), (0.98, 0.2), (0.9, 0.2)], zk, 24, (C.x, C.y))
    prof = [(0.95, 0.0), (1.07, 0.3), (1.1, 0.65), (1.04, 1.0), (0.86, 1.35), (0.6, 1.65), (0.34, 1.88), (0.14, 2.04), (0.05, 2.1), (0.0, 2.12)]
    SEG = 32
    ringen = [[C + Vector((r * (1 + 0.035 * math.cos(16 * math.pi * k / SEG)) * math.cos(2 * math.pi * k / SEG),
                           r * (1 + 0.035 * math.cos(16 * math.pi * k / SEG)) * math.sin(2 * math.pi * k / SEG), zk + 0.2 + z)) for k in range(SEG)] for r, z in prof]
    for a, b in zip(ringen, ringen[1:]):
        for k in range(SEG): quad("koepel", [a[k], a[(k + 1) % SEG], b[(k + 1) % SEG], b[k]])
    top = zk + 0.2 + 2.1
    lathe("goud", [(0.07, 0.0), (0.035, 0.1), (0.035, 2.0), (0.0, 2.1)], top - 0.05, 10, (C.x, C.y))
    for dz, r in ((0.3, 0.13), (0.7, 0.1), (1.05, 0.07)):
        lathe("goud", [(r * math.sin(math.pi * k / 8), -r * math.cos(math.pi * k / 8)) for k in range(9)], top + dz, 12, (C.x, C.y))
    # halve maan (vlak in het oost-west vlak, dubbelzijdig, met dikte)
    mz = top + 1.55; R1, R2 = 0.32, 0.25
    buiten = [(R1 * math.cos(a), R1 * math.sin(a)) for a in [math.pi * (0.15 + 0.7 * k / 16) * 2 - math.pi / 2 for k in range(17)]]
    binnen = [(R2 * math.cos(a) + 0.12, R2 * math.sin(a)) for a in [math.pi * (0.15 + 0.7 * k / 16) * 2 - math.pi / 2 for k in range(17)]][::-1]
    om = buiten + binnen
    for dy in (0.025, -0.025):
        pts = [C + Vector((x, dy, mz + y)) for x, y in om]
        cx = sum(p.x for p in pts) / len(pts); cz = sum(p.z for p in pts) / len(pts)
        for i in range(len(buiten) - 1):
            a, b = Vector((C.x + buiten[i][0], C.y + dy, mz + buiten[i][1])), Vector((C.x + buiten[i + 1][0], C.y + dy, mz + buiten[i + 1][1]))
            c_, d_ = Vector((C.x + binnen[-1 - i][0], C.y + dy, mz + binnen[-1 - i][1])), Vector((C.x + binnen[-2 - i][0], C.y + dy, mz + binnen[-2 - i][1]))
            q = [a, b, d_, c_]; quad("goud", q if dy > 0 else q[::-1])


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in T["G"].items():
        if not bm.faces: continue
        vast = rol in T["OVERLAY"]
        if not vast and rol not in EIGEN: bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        uvl = bm.loops.layers.uv.verify(); s = T["UVS"][rol]
        for f in ([] if vast else bm.faces):
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (co.y / s, co.z / s) if ax == 0 else (co.x / s, co.z / s) if ax == 1 else (co.x / s, co.y / s)
        me = bpy.data.meshes.new("FM_minaret_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_minaret_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "minaret"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"][rol], 1); me.materials.append(m); col.objects.link(o)


def render(uit):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = 700, 1100
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cd.lens = 35
    for o in bpy.data.objects:
        if o.get("deel") not in ("minaret", None): o.hide_render = True
    p = L(45.0, -322.0) + Vector((0, 0, 1.7)); q = C + Vector((0, 0, 12.0))
    cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(uit, "minaret.png"); bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    bouw(); objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[04_minaret] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")
    if "--render" in sys.argv:
        uit = os.path.join(D, "review", "04_minaret"); os.makedirs(uit, exist_ok=True); render(uit)


main()
