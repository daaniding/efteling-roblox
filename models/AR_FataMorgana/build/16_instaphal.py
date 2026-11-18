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
T["OVERLAY"] = tuple(T["OVERLAY"]) + ("balustrade",)
T["KLEUR"].update({"balustrade": (0.6, 0.48, 0.38), "balmuur": (0.9, 0.86, 0.78), "onderwand": (0.35, 0.27, 0.2), "donkervloer": (0.3, 0.22, 0.17), "lichtlijst": (1.0, 0.8, 0.5), "soffit": (0.2, 0.15, 0.12), "boogvul": (0.2, 0.15, 0.12), "witlijn": (0.95, 0.95, 0.92), "lat": (0.62, 0.48, 0.34), "water": (0.12, 0.22, 0.26), "dekhout": (0.55, 0.38, 0.24), "plafond": (0.2, 0.16, 0.14), "rozet": (0.43, 0.27, 0.17), "gordijn": (0.84, 0.77, 0.63), "groenhek": (0.25, 0.58, 0.5), "groen": (0.25, 0.58, 0.5), "poort": (0.05, 0.05, 0.07), "gangmuur": (0.92, 0.85, 0.72), "gangpleister": (0.92, 0.85, 0.72), "groenneg": (0.25, 0.58, 0.5), "fries": (0.2, 0.3, 0.6), "rood": (0.73, 0.26, 0.16), "wit": (0.95, 0.94, 0.9), "vloertegel": (0.65, 0.42, 0.33),
                   "matglas": (0.93, 0.95, 0.96), "schildering": (0.8, 0.75, 0.6), "koepel_blauw": (0.45, 0.68, 0.84), "hekgroen": (0.25, 0.36, 0.32), "donker": (0.12, 0.13, 0.15), "hout": (0.32, 0.2, 0.12), "bord": (0.95, 0.91, 0.8), "bollamp": (1.0, 0.78, 0.5)})
T["UVS"].update({"balustrade": 1.0, "balmuur": 4.0, "onderwand": 4.0, "donkervloer": 2.0, "lichtlijst": 1.0, "soffit": 4.0, "boogvul": 1.0, "witlijn": 1.0, "lat": 1.0, "water": 4.0, "dekhout": 1.5, "plafond": 4.0, "rozet": 1.0, "gordijn": 2.0, "groenhek": 1.0, "groen": 1.0, "poort": 1.0, "gangmuur": 4.0, "gangpleister": 4.0, "groenneg": 1.0, "fries": 1.0, "rood": 1.0, "wit": 9.0, "vloertegel": 2.0, "matglas": 1.0, "schildering": 1.0, "koepel_blauw": 1.0, "hekgroen": 1.0, "donker": 1.0, "bord": 1.0, "bollamp": 1.0})

for r in T["KLEUR"]: T["G"][r] = bmesh.new()

O = (-40.0, -295.0)
# Instaphal volgens de PLATTEGROND van Eftepedia (ref/eftepedia/Plattegrondfata.jpg, sectie 15; schaal ~23 px/m, blok x -16..17,4 =
# plattegrond x 1470..2240) en de video's (2025 POV 30-76 s, 2020 396-424 s, Fata_draaischijf.jpg):
#  - rechthoekige hal met rondom een gaanderij (grijs op de plattegrond) op het niveau van het halletje (0,12 m)
#  - grote draaischijf (cirkel), water eromheen aan de noord-, oost- en zuidkant (onder de gaanderijen door)
#  - achthoekig controlehok IN HET MIDDEN van de schijf op een zuil, brug vanaf de westgaanderij, trap van het hok omlaag op de schijf
#  - boten komen binnen in het zuidwesten (van sectie 14) en vertrekken in het noordwesten (naar sectie 1, achter een gordijn)
#  - binnenkomst van de wachtrij in de noordoosthoek: de groene boog van het halletje komt direct uit op de gaanderij
XW, XE, YS, YN = -3.5, 16.6, -348.4, -323.6       # binnenkant van de hal (0,6 m binnen het afgeronde terrein op de celgrenzen)
GB = 2.6                                           # breedte gaanderij
XWI, XEI, YSI, YNI = XW + GB, XE - GB, YS + GB, YN - GB
C0 = (6.3, -335.8); RT = 7.5                       # draaischijf (plattegrond: midden 1935,995 px)
ZB, ZW, ZD = -3.7, -3.2, -2.9                      # bodem, water, dek (3 m onder de gaanderij)
HZ = 4.86
BY0, BY1 = -336.9, -334.7                          # brug westgaanderij -> controlehok
R8 = 1.8                                           # straal achthoekig controlehok
TY0, TY1 = -336.6, -335.0; TX0 = C0[0] + 1.75; NT = 18; TR = 0.26   # trap oostwaarts omlaag op de schijf


def box(rol, x0, y0, x1, y1, z0, z1):
    prisma(rol, [L(x0, y0), L(x1, y0), L(x1, y1), L(x0, y1)], z0, z1)


def vlak_uv(rol, pts, wil, uvs):
    bm = T["G"][rol]; uvl = bm.loops.layers.uv.verify()
    f = bm.faces.new([bm.verts.new(q) for q in pts]); f.normal_update()
    if f.normal.dot(wil) < 0:
        f.normal_flip()
    for lp in f.loops:
        q = lp.vert.co; best = min(range(4), key=lambda i: (pts[i] - q).length); lp[uvl].uv = uvs[best]


def schuinbox(rol, a, b, dz_onder, dz_boven, dik):
    d = b - a; t = Vector((d.x, d.y, 0)).normalized(); n_ = Vector((-t.y, t.x, 0)) * (dik / 2)
    bm = T["G"][rol]; o = Vector((0, 0, dz_onder)); bv = Vector((0, 0, dz_boven))
    v = [bm.verts.new(q) for q in (a - n_ + o, b - n_ + o, b + n_ + o, a + n_ + o, a - n_ + bv, b - n_ + bv, b + n_ + bv, a + n_ + bv)]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): bm.faces.new([v[i] for i in f])


def rand(xa, ya, xb, yb, gaten=()):
    """gaanderijrand van a naar b (hal ligt LINKS van a->b): balustrade met panelen, groene lijsten, palen met lantaarntjes,
    groene kielbogen, kroonlijst; gaten = [(u0, u1)] waar niets komt (brug)"""
    A, B = L(xa, ya), L(xb, yb); d = B - A; lg = d.length; t = d / lg; hal = Vector((-t.y, t.x, 0))
    n = max(1, round(lg / 1.6)); st = lg / n
    def open_(u0, u1): return any(u0 < g1 and u1 > g0 for g0, g1 in gaten)
    for i in range(n):
        u0, u1 = i * st, (i + 1) * st
        if open_(u0, u1): continue
        p0, p1 = A + t * u0, A + t * u1
        prisma("balmuur", [p0, p1, p1 - hal * 0.16, p0 - hal * 0.16], 0.14, 1.0)
        vlak_uv("balustrade", [p0 + hal * 0.005 + Vector((0, 0, 0.14)), p1 + hal * 0.005 + Vector((0, 0, 0.14)), p1 + hal * 0.005 + Vector((0, 0, 1.0)), p0 + hal * 0.005 + Vector((0, 0, 1.0))],
               hal, [(0, 0), (1, 0), (1, 1), (0, 1)])
        prisma("groen", [p0 + hal * 0.03, p1 + hal * 0.03, p1 - hal * 0.19, p0 - hal * 0.19], 1.0, 1.06)
        prisma("groen", [p0 + hal * 0.05, p1 + hal * 0.05, p1 - hal * 0.22, p0 - hal * 0.22], 0.0, 0.14)
        prisma("onderwand", [p0 + hal * 0.04, p1 + hal * 0.04, p1 - hal * 0.21, p0 - hal * 0.21], -0.45, 0.0)
        vl = Vlak(p0 - hal * 0.08, t, hal)
        bg = spitsboog(st / 2, st - 0.14, 2.35, 2.35, 8, 0.6)[1:-1]
        tp = max(v for _, v in bg); hl = len(bg) // 2
        bg = [p for p in bg[:hl] if p[1] < tp - 0.06] + [(st / 2, tp + 0.12)] + [p for p in bg[hl:] if p[1] < tp - 0.06]
        strip("groen", vl, bg, 0.07, 0.07)
        # donkere boogvulling: boven de kielboog tot het gaanderijplafond donker, zodat de gloed als boogvorm leest (video 2025, 40 s)
        rij = [(0.0, 2.35)] + sorted(bg) + [(st, 2.35)]
        for (ua, va), (ub, vb) in zip(rij, rij[1:]):
            if ub - ua < 1e-4: continue
            for nn, w_ in ((0.03, hal), (0.02, -hal)):
                vlak_uv("boogvul", [vl.p(ua, va, nn), vl.p(ub, vb, nn), vl.p(ub, 3.31, nn), vl.p(ua, 3.31, nn)], w_, [(0, 0), (1, 0), (1, 1), (0, 1)])
        prisma("soffit", [p0 + hal * 0.05, p1 + hal * 0.05, p1 - hal * 0.3, p0 - hal * 0.3], 3.2, 3.42)   # donker plafond boven de gaanderij (video)
    for i in range(n + 1):
        u = i * st
        if open_(u - 0.01, u + 0.01) and not (open_(u - 0.3, u) ^ open_(u, u + 0.3)): continue
        q = A + t * u - hal * 0.08
        prisma("groen", [q + Vector((sx, sy, 0)) * 0.05 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 1.0, 2.9)
        prisma("groen", [q + Vector((sx, sy, 0)) * 0.085 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 2.22, 2.35)   # kapiteel
        prisma("groen", [q + Vector((sx, sy, 0)) * 0.075 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 1.06, 1.16)   # voet
        lathe("goud", [(0.06, 0.0), (0.06, 0.04), (0.04, 0.06), (0.0, 0.08)], 2.9, 6, (q.x, q.y))
        lathe("bollamp", [(r * 0.07, z) for r, z in ((0.0, 0.0), (1.0, 0.03), (1.0, 0.16), (0.6, 0.2), (0.0, 0.22))], 2.98, 8, (q.x, q.y))
        if i % 2 == 0:                                                   # steunpaal onder de gaanderij (in het water)
            q2 = A + t * u - hal * 0.3
            prisma("groen", [q2 + Vector((sx, sy, 0)) * 0.09 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], ZB, -0.3)


def bouw():
    # muren: boven de gaanderij oud beige, eronder donker hout; openingen: halletje (oost, y -329), boten in (west, zuid) en uit (noord, west)
    def muur(x0, y0, x1, y1, onder=True):
        box("gangmuur", x0, y0, x1, y1, 0.0, HZ + 0.05)
        if onder: box("onderwand", x0, y0, x1, y1, ZB, 0.0)
    muur(XW - 0.25, YS - 0.25, XE + 0.25, YS)                                          # zuid
    UX0, UX1, UZ = 13.3, 14.9, 2.6                                                     # uitgangsdeur noordoost (naar de open gang)
    box("gangmuur", XW - 0.25, YN, UX0, YN + 0.25, 0.0, HZ + 0.05); box("gangmuur", UX1, YN, XE + 0.25, YN + 0.25, 0.0, HZ + 0.05)
    box("gangmuur", UX0, YN, UX1, YN + 0.25, UZ, HZ + 0.05)                             # noord boven, met de uitgangsdeur
    box("donkervloer", UX0, YN - 0.05, UX1, -321.75, -0.3, 0.12)                       # doorgang door de gevel naar buiten
    box("gangmuur", UX0 - 0.2, YN + 0.25, UX0, -322.0, 0.0, UZ + 0.2); box("gangmuur", UX1, YN + 0.25, UX1 + 0.2, -322.0, 0.0, UZ + 0.2)
    box("gangmuur", UX0 - 0.2, YN + 0.25, UX1 + 0.2, -322.0, UZ, UZ + 0.2)
    box("onderwand", XW + 3.0, YN, XE + 0.25, YN + 0.25, ZB, 0.0); box("onderwand", XW - 0.25, YN, XW + 0.2, YN + 0.25, ZB, 0.0)
    box("onderwand", XW + 0.2, YN, XW + 3.0, YN + 0.25, -0.4, 0.0)                     # boven de uitgang (noordwest)
    box("gangmuur", XW - 0.25, YS, XW, YN, 0.0, HZ + 0.05)                             # west boven
    box("onderwand", XW - 0.25, YS, XW, -346.3, ZB, 0.0); box("onderwand", XW - 0.25, -343.0, XW, YN, ZB, 0.0)
    box("onderwand", XW - 0.25, -346.3, XW, -343.0, -0.4, 0.0)                         # boven de inkomst (zuidwest)
    box("gangmuur", XE, YS, XE + 0.2, -329.8, 0.0, HZ + 0.05); box("gangmuur", XE, -328.2, XE + 0.2, YN, 0.0, HZ + 0.05)
    box("gangmuur", XE, -329.8, XE + 0.2, -328.2, 3.05, HZ + 0.05)                     # boven de doorgang naar het halletje
    box("onderwand", XE, YS, XE + 0.2, YN, ZB, 0.0)
    for (x0, y0, x1, y1) in ((XW - 1.0, YN + 0.25, XW + 3.2, YN + 1.4), (XW - 1.4, -346.5, XW - 0.25, -342.8)):   # donkere doorvaarten
        box("poort", x0, y0, x1, y1, ZW, 0.0)
    for k in range(14):                                                                # gordijn bij de uitgang (Eftepedia: beige gordijntje)
        x = XW + 0.3 + 0.18 * k
        box("gordijn", x, YN - 0.12 - (0.06 if k % 2 else 0.0), x + 0.18, YN - 0.02, ZW + 0.1, -0.42)
    quad("plafond", [L(XW, YN) + Vector((0, 0, HZ)), L(XE, YN) + Vector((0, 0, HZ)), L(XE, YS) + Vector((0, 0, HZ)), L(XW, YS) + Vector((0, 0, HZ))])
    box("donker", XW, YS, XE, YN, ZB - 0.2, ZB)
    box("water", XW, YS, XE, YN, ZW - 0.05, ZW)
    # gaanderijvloeren (geen overlappende hoeken) + doorgang naar het halletje
    box("donkervloer", XW, YNI, XE, YN, -0.3, 0.12)
    box("donkervloer", XW, YS, XE, YSI, -0.3, 0.12)
    box("donkervloer", XW, YSI, XWI, YNI, -0.3, 0.12)
    box("donkervloer", XEI, YSI, XE, YNI, -0.3, 0.12)
    box("donkervloer", XE - 0.05, -330.2, 17.75, -327.8, -0.3, 0.12)
    box("gangmuur", XE, -330.0, 17.25, -329.8, 0.0, 3.05); box("gangmuur", XE, -328.2, 17.25, -328.0, 0.0, 3.05)   # neggen van de doorgang
    box("gangmuur", XE, -330.0, 17.25, -328.0, 3.0, 3.2)
    # randen (hal links van de looprichting): noord (oost->west), west (noord->zuid, met de brug), zuid (west->oost), oost (zuid->noord)
    EX0, EX1 = C0[0] - 0.8, C0[0] + 0.8                                  # uittrap (links van het controlehok, vanaf de brug gezien)
    rand(XEI, YNI, XWI, YNI, gaten=[(XEI - EX1 - 0.1, XEI - EX0 + 0.1)])
    rand(XWI, YNI, XWI, YSI, gaten=[(YNI - BY1 - 0.05, YNI - BY0 + 0.05)])
    rand(XWI, YSI, XEI, YSI)
    rand(XEI, YSI, XEI, YNI)
    # gescheiden routes (Daan: "nu zou je rechts en links kunnen"; Eftepedia: in via de gaanderij, uit via een trap links van het
    # controlehok en een gaanderij): IN = oost (zuid van de doorgang) -> zuid -> west -> brug; UIT = trap -> noordgaanderij -> deur
    def afsluiting(x0, y0, x1, y1, wil):
        box("balmuur", x0, y0, x1, y1, 0.12, 1.0)
        lg = max(x1 - x0, y1 - y0)
        for w_ in (wil, -wil):
            if abs(w_.y) > 0:
                yy = (y1 + 0.005) if w_.y > 0 else (y0 - 0.005)
                pts = [L(x0, yy) + Vector((0, 0, 0.14)), L(x1, yy) + Vector((0, 0, 0.14)), L(x1, yy) + Vector((0, 0, 1.0)), L(x0, yy) + Vector((0, 0, 1.0))]
            else:
                xx = (x1 + 0.005) if w_.x > 0 else (x0 - 0.005)
                pts = [L(xx, y0) + Vector((0, 0, 0.14)), L(xx, y1) + Vector((0, 0, 0.14)), L(xx, y1) + Vector((0, 0, 1.0)), L(xx, y0) + Vector((0, 0, 1.0))]
            vlak_uv("balustrade", pts, w_, [(0, 0), (lg / 1.6, 0), (lg / 1.6, 1), (0, 1)])
        box("groen", x0 - 0.04, y0 - 0.04, x1 + 0.04, y1 + 0.04, 1.0, 1.07)
    afsluiting(XEI - 0.05, -327.75, XE, -327.6, Vector((0, -1, 0)))         # oostgaanderij noord van de doorgang
    afsluiting(XW, -333.4, XWI + 0.05, -333.25, Vector((0, -1, 0)))         # westgaanderij noord van de brug
    # brug van de westgaanderij naar het controlehok, met balustrades
    bx1 = C0[0] - R8 + 0.3
    box("donkervloer", XWI - 0.1, BY0, bx1, BY1, -0.3, 0.12)
    box("groen", XWI - 0.1, BY0 - 0.06, bx1, BY0, -0.45, 0.14); box("groen", XWI - 0.1, BY1, bx1, BY1 + 0.06, -0.45, 0.14)
    for y, kant in ((BY0, -1), (BY1, 1)):
        for k in range(int((bx1 - XWI) / 1.6) + 1):
            x0 = XWI + k * 1.6; x1 = min(bx1, x0 + 1.6)
            if x1 - x0 < 0.2: continue
            yy = y + kant * 0.0
            box("balmuur", x0, min(yy, yy - kant * 0.16), x1, max(yy, yy - kant * 0.16), 0.14, 1.0)
            for zijde in (1, -1):
                ya = yy + (0.005 if zijde * kant > 0 else -0.165) * kant
                pts = [L(x0, ya) + Vector((0, 0, 0.14)), L(x1, ya) + Vector((0, 0, 0.14)), L(x1, ya) + Vector((0, 0, 1.0)), L(x0, ya) + Vector((0, 0, 1.0))]
                vlak_uv("balustrade", pts, Vector((0, zijde * kant, 0)) * (1 if zijde > 0 else 1), [(0, 0), ((x1 - x0) / 1.6, 0), ((x1 - x0) / 1.6, 1), (0, 1)])
            box("groen", x0, min(yy, yy - kant * 0.2), x1, max(yy + kant * 0.04, yy - kant * 0.2), 1.0, 1.07)
    # achthoekig controlehok op een zuil in het midden van de schijf (groene palen en kielbogen, panelen onder, lampjes)
    c = L(*C0)
    hk = [c + Vector((R8 * math.cos(math.pi / 8 + k * math.pi / 4), R8 * math.sin(math.pi / 8 + k * math.pi / 4), 0)) for k in range(8)]
    prisma("donkervloer", hk, -0.3, 0.12)
    for k in range(8):
        a_, b_ = hk[k], hk[(k + 1) % 8]; t = (b_ - a_); lg = t.length; t /= lg; n_ = Vector((t.y, -t.x, 0))
        if n_.dot(a_ - c) < 0: n_ = -n_
        mid = (a_ + b_) / 2
        open_kant = abs(mid.x - c.x) > 1.2 and abs(mid.y - c.y) < 0.9          # west (brug) en oost (trap) open
        if not open_kant:
            prisma("balmuur", [a_, b_, b_ - n_ * 0.16, a_ - n_ * 0.16], 0.14, 1.0)
            vlak_uv("balustrade", [a_ + n_ * 0.005 + Vector((0, 0, 0.14)), b_ + n_ * 0.005 + Vector((0, 0, 0.14)), b_ + n_ * 0.005 + Vector((0, 0, 1.0)), a_ + n_ * 0.005 + Vector((0, 0, 1.0))],
                   n_, [(0, 0), (lg / 1.6, 0), (lg / 1.6, 1), (0, 1)])
            prisma("groen", [a_ + n_ * 0.05, b_ + n_ * 0.05, b_ - n_ * 0.22, a_ - n_ * 0.22], 1.0, 1.07)
        vl = Vlak(a_, t, n_)
        bg = spitsboog(lg / 2, lg - 0.14, 2.3, 2.3, 8, 0.6)[1:-1]
        tp = max(v for _, v in bg); hl = len(bg) // 2
        bg = [p for p in bg[:hl] if p[1] < tp - 0.06] + [(lg / 2, tp + 0.12)] + [p for p in bg[hl:] if p[1] < tp - 0.06]
        strip("groen", vl, bg, 0.08, 0.08)
        prisma("groen", [a_ + Vector((sx, sy, 0)) * 0.07 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], 0.12, 2.85)
        lathe("bollamp", [(r * 0.07, z) for r, z in ((0.0, 0.0), (1.0, 0.03), (1.0, 0.16), (0.6, 0.2), (0.0, 0.22))], 2.85, 8, (a_.x, a_.y))
    lathe("groen", [(R8 + 0.2, 0.0), (R8 + 0.25, 0.12), (R8 + 0.05, 0.25), (0.0, 0.28)], 2.85, 8, (c.x, c.y))      # dakje
    lathe("groen", [(0.0, 0.0), (0.6, 0.0), (1.3, -0.9), (0.3, -1.5), (0.3, -2.3), (0.7, -2.55), (0.7, -2.6), (0.0, -2.6)], -0.3, 16, (c.x, c.y))   # kegel + zuil tot het dek
    # trap van het controlehok oostwaarts omlaag op de schijf (panelenbalustrade aan beide kanten)
    for i in range(NT):
        x0 = TX0 + TR * i; ztop = 0.12 - (0.12 - ZD) * (i + 1) / NT
        box("donkervloer", x0, TY0, x0 + TR, TY1, ztop - 0.25, ztop)
    for y, kant in ((TY0, -1), (TY1, 1)):
        A, B = L(TX0, y) + Vector((0, 0, 0.12)), L(TX0 + TR * NT, y) + Vector((0, 0, ZD))
        schuinbox("balmuur", A + Vector((0, kant * 0.08, 0)), B + Vector((0, kant * 0.08, 0)), -0.3, 1.0, 0.16)
        schuinbox("groen", A + Vector((0, kant * 0.08, 0)), B + Vector((0, kant * 0.08, 0)), 1.0, 1.07, 0.24)
        ya = y + kant * 0.165
        vlak_uv("balustrade", [A + Vector((0, kant * 0.165, -0.25)), B + Vector((0, kant * 0.165, -0.25)), B + Vector((0, kant * 0.165, 0.95)), A + Vector((0, kant * 0.165, 0.95))],
               Vector((0, kant, 0)), [(0, 0), (2.9, 0), (2.9, 1), (0, 1)])
    # uittrap (Eftepedia: "Via een trap aan de linkerzijde van het controlehok en een gaanderij kunnen we de hal verlaten"):
    # van de schijf noordwaarts omhoog naar de noordgaanderij, panelenbalustrades aan beide kanten
    ny = 18; ry = (YNI - (-331.2)) / ny
    for i in range(ny):
        y0 = -331.2 + ry * i; ztop = ZD + (0.12 - ZD) * (i + 1) / ny
        box("donkervloer", EX0, y0, EX1, y0 + ry, ztop - 0.25, ztop)
    for x, kant in ((EX0, -1), (EX1, 1)):
        A, B = L(x, -331.2) + Vector((0, 0, ZD)), L(x, YNI) + Vector((0, 0, 0.12))
        schuinbox("balmuur", A + Vector((kant * 0.08, 0, 0)), B + Vector((kant * 0.08, 0, 0)), -0.3, 1.0, 0.16)
        schuinbox("groen", A + Vector((kant * 0.08, 0, 0)), B + Vector((kant * 0.08, 0, 0)), 1.0, 1.07, 0.24)
        vlak_uv("balustrade", [A + Vector((kant * 0.165, 0, -0.25)), B + Vector((kant * 0.165, 0, -0.25)), B + Vector((kant * 0.165, 0, 0.95)), A + Vector((kant * 0.165, 0, 0.95))],
               Vector((kant, 0, 0)), [(0, 0), (3.1, 0), (3.1, 1), (0, 1)])
    # draaischijf: houten dek (ringen planken), donkere rand, witte streepjes
    lathe("dekhout", [(0.0, 0.0), (RT, 0.0), (RT, -0.5), (0.0, -0.5)], ZD, 72, (c.x, c.y))
    lathe("donker", [(RT, 0.0), (RT + 0.1, 0.0), (RT + 0.1, -0.5), (RT, -0.5), (RT, 0.0)], ZD + 0.02, 72, (c.x, c.y))
    for rr in [1.2 + 0.62 * k for k in range(10)]:
        lathe("donker", [(rr - 0.015, 0.0), (rr + 0.015, 0.0)], ZD + 0.006, 72, (c.x, c.y))
    for k in range(36):
        if k % 2: continue
        a0 = math.radians(k * 10.0); a1 = math.radians(k * 10.0 + 6.0)
        pts = [c + Vector((math.cos(a) * r, math.sin(a) * r, 0)) for a, r in ((a0, RT - 0.75), (a0, RT - 0.65), (a1, RT - 0.65), (a1, RT - 0.75))]
        prisma("witlijn", pts, ZD, ZD + 0.012)
    # paddenstoelvormige lattenkap in twee lagen boven het controlehok (fijne radiale latten), ophanging
    for (r0, r1, z0, z1, n) in ((2.2, 7.8, 4.55, 3.8, 220), (1.0, 3.6, 3.95, 3.6, 110)):
        for k in range(n):
            a = 2 * math.pi * k / n; cc, ss = math.cos(a), math.sin(a); nn = Vector((-ss, cc, 0)) * 0.035
            p0 = c + Vector((cc * r0, ss * r0, z0)); p1 = c + Vector((cc * r1, ss * r1, z1))
            bm = T["G"]["lat"]; up = Vector((0, 0, 0.05))
            v = [bm.verts.new(q) for q in (p0 - nn, p1 - nn, p1 + nn, p0 + nn, p0 - nn + up, p1 - nn + up, p1 + nn + up, p0 + nn + up)]
            for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): bm.faces.new([v[i] for i in f])
        lathe("hout", [(r1, -0.05), (r1 + 0.12, -0.05), (r1 + 0.12, 0.12), (r1, 0.12)], z1, 72, (c.x, c.y))
        lathe("hout", [(r0 - 0.12, -0.05), (r0, -0.05), (r0, 0.12), (r0 - 0.12, 0.12)], z0, 48, (c.x, c.y))
    for k in range(6):
        a = 2 * math.pi * k / 6; q2 = c + Vector((math.cos(a) * 5.0, math.sin(a) * 5.0, 0))
        lathe("donker", [(0.02, 0.0), (0.02, HZ - 4.1)], 4.1, 6, (q2.x, q2.y))
    # lichtlijst langs de achterwanden boven de gaanderij (fel verlichte achterwand op de video)
    for (x0, y0, x1, y1) in ((XW, YN - 0.08, UX0 - 0.1, YN), (UX1 + 0.1, YN - 0.08, XE, YN), (XW, YS, XE, YS + 0.08), (XW, YS, XW + 0.08, YN), (XE - 0.08, YS, XE, -329.9), (XE - 0.08, -328.1, XE, YN)):
        box("lichtlijst", x0, y0, x1, y1, 3.0, 3.06)
    # donkerbruine band boven de gaanderij op de achterwanden (video: boven de verlichte bogen is alles donker)
    for (x0, y0, x1, y1) in ((XW, YN - 0.04, XE, YN), (XW, YS, XE, YS + 0.04), (XW, YS + 0.04, XW + 0.04, YN - 0.04), (XE - 0.04, YS + 0.04, XE, YN - 0.04)):
        box("soffit", x0, y0, x1, y1, 3.1, HZ)
    for (x0, y0, x1, y1) in ((XW + 0.04, YNI, XE - 0.04, YN - 0.04), (XW + 0.04, YS + 0.04, XE - 0.04, YSI),
                             (XW + 0.04, YSI, XWI, YNI), (XEI, YSI, XE - 0.04, YNI)):          # plafond van de gaanderijen
        box("soffit", x0, y0, x1, y1, 3.3, 3.39)


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in T["G"].items():
        if not bm.faces: continue
        vast = rol in T["OVERLAY"]
        if not vast and rol not in ("raam", "deur", "dak", "stucvlak", "poort", "gangpleister", "groenneg", "plafond", "boogvul"):
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
    for naam, p, q in (("hal_gaanderij", L(15.5, -324.0) + Vector((0, 0, 1.7)), L(2.0, -340.0) + Vector((0, 0, -1.5))),
                       ("hal_schijf", L(12.0, -340.0) + Vector((0, 0, -1.3)), L(0.0, -333.0) + Vector((0, 0, 0.5))),
                       ("hal_zuid", L(6.3, -348.0) + Vector((0, 0, 1.7)), L(6.3, -330.0) + Vector((0, 0, -1.0)))):
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
