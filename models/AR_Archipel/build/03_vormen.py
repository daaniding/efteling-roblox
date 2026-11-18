"""03_vormen: de Archipel in echte vormen, met UV's per rol (vervangt de blockout; plan.py = plattegrond).
Modelstelsel: meters t.o.v. plan.OORSPRONG, x oost, y noord, z 0 = waterpeil. Elk object heeft "rol" (materiaal) en "deel"
(exportbestand: bad / hutten / decor).
Bronnen per onderdeel:
  paalhutten  : doorsnede-paalvissers.jpg (romp 2,5 m; vloer 1,3; dakrand 2,6; nok 5,3; spits 6,1), Archi-huisje-close.jpg
                (bamboewand, rondhout-palen, netten in de openingen, rieten dak in lagen), Archipel-alle-huisjes.jpg (hol
                uitlopende dakvorm, donkere puntopening in de voorgevel, pironnen), lemma (balkon + zeeslang op hut 2,
                klimtouw op hut 1 en 3, monstervis op hut 4, touw om de paalvoeten: Archi-loopbruggen.jpg)
  ronde hut   : Archipel-boot.jpg / Archi-water-siro.jpg (bamboe rond, rieten kegel in twee lagen met hoedje)
  loopbruggen : Archi-loopbruggen.jpg (twee liggers met losse dwarsplankjes, paaltjes, touwleuning)
  wrak        : Archipel_zonnig_2022.jpg, Archipel-boot.jpg (achterschip: spiegel met gouden krullen, ruitband, roodbruine
                planken; voorschip: blauwe schubben, gouden rand, hoog opgekrulde steven; omgevallen mast als balk; staande
                mast met lantaarn en wimpel; touw van mast naar voorschip)
  paalvisser  : Archipel_paalvisser.jpg (tulband, grijze baard, blauw hemd, rode sjerp, bordeauxbroek, hengel met vis)
  kisten/tonnen: Archipel-boot.jpg, Archi-water-siro.jpg (kisten blauwgrijs/roodbruin/hout met rond gat; lage tonnen met
                rood deksel; schatkist met bolle deksel)
Gebruik: blender --background --python build/03_vormen.py -- --master AR_Archipel_master.blend [--render]"""
import bpy, sys, os, math, random
from mathutils import Vector, Matrix
from collections import defaultdict

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, "build"))
import plan as P

OWNER = "phase:03_vormen"
rnd = random.Random(2022)

KLEI = {"beton": (0.86, 0.8, 0.68), "epdm": (0.3, 0.62, 0.62), "kade": (0.8, 0.76, 0.68), "aarde": (0.33, 0.27, 0.2),
        "water": (0.45, 0.78, 0.82), "riet": (0.74, 0.58, 0.36), "bamboe": (0.72, 0.58, 0.36), "raam": (0.1, 0.08, 0.06),
        "stam": (0.78, 0.6, 0.38), "plank": (0.55, 0.45, 0.35), "touw": (0.7, 0.6, 0.45), "net": (0.6, 0.5, 0.36),
        "piron": (0.2, 0.2, 0.22), "romp": (0.45, 0.2, 0.15), "schubben": (0.25, 0.45, 0.75), "krul": (0.1, 0.15, 0.35),
        "goud": (0.84, 0.66, 0.28), "mast": (0.35, 0.22, 0.15), "vlag": (0.7, 0.15, 0.12), "lantaarn": (0.3, 0.22, 0.12),
        "lantaarnglas": (1, 0.7, 0.3), "kist_blauw": (0.42, 0.52, 0.54), "kist_rood": (0.55, 0.3, 0.24), "kist_hout": (0.55, 0.42, 0.3),
        "ijzer": (0.18, 0.17, 0.16), "ton": (0.5, 0.33, 0.2), "tondeksel": (0.7, 0.22, 0.16), "huid": (0.82, 0.6, 0.45),
        "tulband": (0.92, 0.88, 0.78), "baard": (0.75, 0.74, 0.72), "hemd": (0.12, 0.2, 0.42), "sjerp": (0.85, 0.42, 0.15),
        "broek": (0.45, 0.12, 0.16), "hengel": (0.15, 0.1, 0.07), "vis": (0.9, 0.5, 0.2)}


class Bak:
    """verzamelt geometrie per (rol, deel, naam) met UV per hoek"""
    def __init__(self): self.d = defaultdict(lambda: ([], [], []))

    def vlak(self, sleutel, pts, uvs):
        v, f, u = self.d[sleutel]; i0 = len(v)
        v.extend(Vector(p) for p in pts); f.append(tuple(range(i0, i0 + len(pts)))); u.append([tuple(x) for x in uvs])

    def raster(self, sleutel, F, nu, nv, UV, gesloten_u=False, omdraaien=False):
        """parametrisch vlak F(i/nu, j/nv) -> punt; UV(i/nu, j/nv) -> uv"""
        v, f, u = self.d[sleutel]; i0 = len(v)
        cols = nu if gesloten_u else nu + 1
        for j in range(nv + 1):
            for i in range(cols): v.append(Vector(F(i / nu, j / nv)))
        for j in range(nv):
            for i in range(nu):
                i1 = (i + 1) % cols if gesloten_u else i + 1
                q = (i0 + j * cols + i, i0 + j * cols + i1, i0 + (j + 1) * cols + i1, i0 + (j + 1) * cols + i)
                uvq = [UV(i / nu, j / nv), UV((i + 1) / nu, j / nv), UV((i + 1) / nu, (j + 1) / nv), UV(i / nu, (j + 1) / nv)]
                if omdraaien: q = q[::-1]; uvq = uvq[::-1]
                f.append(q); u.append(uvq)

    def bouw(self, bad_zichtbaar=True):
        for (rol, deel, naam), (v, f, u) in self.d.items():
            me = bpy.data.meshes.new(naam); me.from_pydata([tuple(x) for x in v], [], f); me.validate()
            uvl = me.uv_layers.new(name="UVMap")
            k = 0
            for p, puv in zip(me.polygons, u):
                for li, uv in zip(p.loop_indices, puv): uvl.data[li].uv = uv
            o = bpy.data.objects.new(naam, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = deel
            col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
            if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
            col.objects.link(o)
            m = bpy.data.materials.get("AR_" + rol) or bpy.data.materials.new("AR_" + rol)
            m.diffuse_color = (*KLEI.get(rol, (0.7, 0.7, 0.7)), 1); me.materials.append(m)


B = Bak()


def M(p, z=0.0): return Vector((p[0] - P.OORSPRONG[0], p[1] - P.OORSPRONG[1], z))


def basis(a, b):
    a, b = Vector(a), Vector(b); d = (b - a); L = d.length; t = d / L
    h = Vector((0, 0, 1)) if abs(t.z) < 0.95 else Vector((1, 0, 0))
    x = t.cross(h).normalized(); y = t.cross(x)
    return a, t, x, y, L


def cil(sl, a, b, r0, r1=None, seg=12, uvu=0.6, uvv=1.5, doppen=True, ruw=0.0):
    """cilinder/kegelstomp van a naar b; u rond (omtrek / uvu), v langs de as (lengte / uvv)"""
    r1 = r0 if r1 is None else r1
    a, t, x, y, L = basis(a, b)
    om = 2 * math.pi * max(r0, r1)
    rs = [1 + ruw * (rnd.random() - 0.5) for _ in range(seg)]

    def F(s, h):
        k = round(s * seg) % seg; ang = 2 * math.pi * s; r = (r0 + (r1 - r0) * h) * rs[k]
        return a + t * (L * h) + (x * math.cos(ang) + y * math.sin(ang)) * r
    B.raster(sl, F, seg, 1 if r0 == r1 and not ruw else 3, lambda s, h: (s * om / uvu, h * L / uvv), gesloten_u=True)
    if doppen:
        for h, rr, sgn in ((0, r0, -1), (1, r1, 1)):
            c = a + t * (L * h)
            pts = [c + (x * math.cos(2 * math.pi * k / seg) + y * math.sin(2 * math.pi * k / seg)) * rr * rs[k] for k in range(seg)]
            uv = [(0.5 + 0.5 * math.cos(2 * math.pi * k / seg) * rr / uvu, 0.5 + 0.5 * math.sin(2 * math.pi * k / seg) * rr / uvu) for k in range(seg)]
            if sgn < 0: pts, uv = pts[::-1], uv[::-1]
            B.vlak(sl, pts, uv)


def doos(sl, c, sx, sy, sz, rot=0.0, uvs=1.2, kantel=None):
    """balk met middelpunt c, maten sx sy sz, draaiing om z (+ optioneel kantelmatrix); doosprojectie in wereldmaat"""
    R = Matrix.Rotation(rot, 3, "Z") @ (kantel or Matrix.Identity(3))
    c = Vector(c); h = Vector((sx / 2, sy / 2, sz / 2))
    hk = [Vector((i * h.x, j * h.y, k * h.z)) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)]
    w = [c + R @ p for p in hk]
    vlakken = [((0, 1, 3, 2), "x-"), ((4, 6, 7, 5), "x+"), ((0, 4, 5, 1), "y-"), ((2, 3, 7, 6), "y+"), ((0, 2, 6, 4), "z-"), ((1, 5, 7, 3), "z+")]
    for idx, ax in vlakken:
        pts = [w[i] for i in idx]; lp = [hk[i] for i in idx]
        if ax[0] == "x": uv = [((p.y + h.y) / uvs, (p.z + h.z) / uvs) for p in lp]
        elif ax[0] == "y": uv = [((p.x + h.x) / uvs, (p.z + h.z) / uvs) for p in lp]
        else: uv = [((p.x + h.x) / uvs, (p.y + h.y) / uvs) for p in lp]
        B.vlak(sl, pts, uv)


def buis(sl, pts, r, seg=8, uvu=0.3, uvv=0.6):
    """buis langs een polylijn (touw, rand)"""
    pts = [Vector(p) for p in pts]; n = len(pts)
    ringen = []
    for i in range(n):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        h = Vector((0, 0, 1)) if abs(t.z) < 0.95 else Vector((1, 0, 0))
        x = t.cross(h).normalized(); y = t.cross(x)
        ringen.append([pts[i] + (x * math.cos(2 * math.pi * k / seg) + y * math.sin(2 * math.pi * k / seg)) * r for k in range(seg)])
    lengte = [0.0]
    for i in range(1, n): lengte.append(lengte[-1] + (pts[i] - pts[i - 1]).length)
    for i in range(n - 1):
        for k in range(seg):
            k1 = (k + 1) % seg
            B.vlak(sl, [ringen[i][k], ringen[i][k1], ringen[i + 1][k1], ringen[i + 1][k]],
                   [(k / seg * 2 * math.pi * r / uvu, lengte[i] / uvv), ((k + 1) / seg * 2 * math.pi * r / uvu, lengte[i] / uvv),
                    ((k + 1) / seg * 2 * math.pi * r / uvu, lengte[i + 1] / uvv), (k / seg * 2 * math.pi * r / uvu, lengte[i + 1] / uvv)])


def bol(sl, c, rx, ry=None, rz=None, seg=12, ringen=8, uvs=0.5):
    ry = rx if ry is None else ry; rz = rx if rz is None else rz; c = Vector(c)
    def F(s, h):
        a = 2 * math.pi * s; b = math.pi * (h - 0.5)
        return c + Vector((math.cos(a) * math.cos(b) * rx, math.sin(a) * math.cos(b) * ry, math.sin(b) * rz))
    B.raster(sl, F, seg, ringen, lambda s, h: (s * 2 * math.pi * rx / uvs, h * math.pi * rz / uvs), gesloten_u=True)


# ---------------------------------------------------------------- bad: bodem, kade, maaiveld, water
RASTER = 0.3


def bad():
    xs = [p[0] for p in P.KADE]; ys = [p[1] for p in P.KADE]
    x0, y0 = min(xs) - 0.3, min(ys) - 0.3
    nx, ny = int((max(xs) + 0.3 - x0) / RASTER) + 1, int((max(ys) + 0.3 - y0) / RASTER) + 1
    H = {}
    def h(i, j):
        if (i, j) not in H:
            z = P.bodem(x0 + i * RASTER, y0 + j * RASTER); H[(i, j)] = P.Z_STRAND if z is None else z
        return H[(i, j)]
    for j in range(ny - 1):
        for i in range(nx - 1):
            cx, cy = x0 + (i + 0.5) * RASTER, y0 + (j + 0.5) * RASTER
            if not P.binnen(cx, cy, P.KADE): continue
            rol = "beton"
            pts, uv = [], []
            for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)):
                X, Y = x0 + (i + di) * RASTER, y0 + (j + dj) * RASTER
                pts.append(M((X, Y), h(i + di, j + dj))); uv.append((X / (3.0 if rol == "beton" else 2.0), Y / (3.0 if rol == "beton" else 2.0)))
            B.vlak((rol, "bad", "AR_bodem_" + rol), pts, uv)
    # EPDM: gladde overlay 1,5 cm boven het beton, rand precies langs DIEP en de schotel (constrained Delaunay)
    from mathutils.geometry import delaunay_2d_cdt
    from mathutils import Vector as V2
    sx, sy, sr = P.SCHOTEL
    for zone in (P.DIEP, [(sx + sr * math.cos(2 * math.pi * k / 48), sy + sr * math.sin(2 * math.pi * k / 48)) for k in range(48)]):
        rand = []
        for i in range(len(zone)):
            a, b = zone[i], zone[(i + 1) % len(zone)]; n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 0.2))
            rand += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
        xs_, ys_ = [p[0] for p in zone], [p[1] for p in zone]
        binnenp = [(x, y) for x in frange(min(xs_), max(xs_), 0.3) for y in frange(min(ys_), max(ys_), 0.3)
                   if P.binnen(x, y, zone) and P.afstand(x, y, zone) > 0.12]
        alle = rand + binnenp
        res = delaunay_2d_cdt([V2(p) for p in alle], [], [list(range(len(rand)))], 1, 1e-6)
        verts, faces = res[0], res[2]
        for f in faces:
            q = [verts[k] for k in f]
            pts = [M((v.x, v.y), (P.bodem(v.x, v.y) or 0) + 0.015) for v in q]
            if (pts[1] - pts[0]).cross(pts[2] - pts[0]).z < 0: pts = pts[::-1]; q = q[::-1]
            B.vlak(("epdm", "bad", "AR_bodem_epdm"), pts, [(v.x / 2.0, v.y / 2.0) for v in q])
    # kade: afgeronde betonrand langs KADE (boven 6 cm boven het maaiveld), aan de binnenkant tot onder de bodem
    ring(("kade", "bad", "AR_kade"), P.KADE, [(-0.14, -0.75), (-0.14, P.Z_MAAIVELD + 0.02), (-0.06, P.Z_MAAIVELD + 0.08),
                                             (0.18, P.Z_MAAIVELD + 0.08), (0.28, P.Z_MAAIVELD + 0.0), (0.28, P.Z_MAAIVELD - 0.3)], 1.5)
    # maaiveldrand: aarde buiten de kade, 2,2 m breed (dekt de uitgegraven terreincellen)
    ring(("aarde", "bad", "AR_maaiveld"), P.KADE, [(0.27, P.Z_MAAIVELD - 0.01), (2.4, P.Z_MAAIVELD - 0.01)], 2.0)
    # water: vlak in de kadevorm op z 0 (het strand ligt erboven; de kustlijn ontstaat vanzelf), ear clipping
    pts = [M(p) for p in P.KADE]
    for tri in oor(pts):
        q = [pts[k] for k in tri]
        if (q[1] - q[0]).cross(q[2] - q[0]).z < 0: q = q[::-1]
        B.vlak(("water", "bad", "AR_water"), q, [(p.x / 4, p.y / 4) for p in q])


def frange(a, b, st):
    out = []; x = a
    while x <= b: out.append(x); x += st
    return out


def oor(pts):
    """ear clipping (2D, xy), geeft driehoeken als indexdrietallen"""
    idx = list(range(len(pts)))
    opp = sum(pts[i].x * pts[(i + 1) % len(pts)].y - pts[(i + 1) % len(pts)].x * pts[i].y for i in idx)
    if opp < 0: idx.reverse()
    def kruis(a, b, c): return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
    tris = []
    while len(idx) > 3:
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = pts[i0], pts[i1], pts[i2]
            if kruis(a, b, c) <= 1e-9: continue
            if any(kruis(a, b, pts[j]) >= 0 and kruis(b, c, pts[j]) >= 0 and kruis(c, a, pts[j]) >= 0 for j in idx if j not in (i0, i1, i2)): continue
            tris.append((i0, i1, i2)); idx.pop(k); break
        else:
            break
    if len(idx) == 3: tris.append(tuple(idx))
    return tris


def ring(sl, poly, profiel, uvschaal):
    """profiel (afstand naar buiten, z) langs een gesloten veelhoek (parkcoordinaten)"""
    n = len(poly); pts = [M(p) for p in poly]
    opp = sum(pts[i].x * pts[(i + 1) % n].y - pts[(i + 1) % n].x * pts[i].y for i in range(n)); s = 1 if opp > 0 else -1
    nrm = []
    for i in range(n):
        t = ((pts[i] - pts[i - 1]).normalized() + (pts[(i + 1) % n] - pts[i]).normalized()).normalized()
        nrm.append(Vector((t.y, -t.x, 0)) * s)
    lengte = [0.0]
    for i in range(1, n + 1): lengte.append(lengte[-1] + (pts[i % n] - pts[i - 1]).length)
    prof_l = [0.0]
    for k in range(1, len(profiel)): prof_l.append(prof_l[-1] + math.hypot(profiel[k][0] - profiel[k - 1][0], profiel[k][1] - profiel[k - 1][1]))
    for i in range(n):
        i1 = (i + 1) % n
        if poly[i][1] >= P.KANAAL_EIND_Y and poly[i1][1] >= P.KANAAL_EIND_Y: continue     # open naar de Sirocco-vijver
        for k in range(len(profiel) - 1):
            (o0, z0), (o1, z1) = profiel[k], profiel[k + 1]
            q = [pts[i] + nrm[i] * o0 + Vector((0, 0, z0)), pts[i1] + nrm[i1] * o0 + Vector((0, 0, z0)),
                 pts[i1] + nrm[i1] * o1 + Vector((0, 0, z1)), pts[i] + nrm[i] * o1 + Vector((0, 0, z1))]
            uv = [(lengte[i] / uvschaal, prof_l[k] / uvschaal), (lengte[i + 1] / uvschaal, prof_l[k] / uvschaal),
                  (lengte[i + 1] / uvschaal, prof_l[k + 1] / uvschaal), (lengte[i] / uvschaal, prof_l[k + 1] / uvschaal)]
            B.vlak(sl, q[::-1], uv[::-1])


# ---------------------------------------------------------------- hutten
def superring(hx, hy, n=4.0):
    """punt op een afgeronde rechthoek (superellips) op hoek a"""
    def f(a):
        c, s = math.cos(a), math.sin(a)
        return (hx * math.copysign(abs(c) ** (2 / n), c), hy * math.copysign(abs(s) ** (2 / n), s))
    return f


def rieten_dak(naam, c, rot, ze, zn, e, top=(0.08, 0.08), lagen=(0.0, 0.2, 0.6), lip=0.075, dik=0.3, rond=7.0,
               opening=None, deel="hutten", rok=True):
    """hol uitlopend rieten dak: ringen van afgeronde rechthoeken van dakrand (halve breedte e, hoogte ze) tot de top (zn);
    elke laag steekt aan de onderkant 'lip' uit (dikke rietrand). opening = (halve breedte onder, hoogte als fractie):
    donkere puntopening in de voorgevel (+y lokaal)."""
    R = Matrix.Rotation(rot, 3, "Z"); c = Vector(c)
    SEG = 40

    def breedte(s):                       # basisprofiel: flauwe rok onderaan (tot s 0,2 naar 0,74), daarboven bijna recht en steil
        if rok:
            if s < 0.2: return 1 - 0.26 * (s / 0.2) ** 0.85
            return 0.74 * ((1 - s) / 0.8) ** 1.12
        return (1 - s) ** 1.3

    def laaglip(s):
        for k in range(len(lagen) - 1, -1, -1):
            if s >= lagen[k]:
                s1 = lagen[k + 1] if k + 1 < len(lagen) else 1.0
                return lip * (1 - (s - lagen[k]) / (s1 - lagen[k])) ** 2.2 * (1.0 if k == 0 else 0.85)
        return 0

    def punt(a, s, extra=0.0):
        hx = top[0] + (e - top[0]) * breedte(s) + laaglip(s) + extra
        hy = top[1] + (e - top[1]) * breedte(s) + laaglip(s) + extra
        x, y = superring(hx, hy, rond)(a)
        return c + R @ Vector((x, y, ze + (zn - ze) * s))
    # buitenhuid: s in fijne stappen, met een extra ring vlak onder elke laag (de rietrand)
    ss = sorted(set([i / 36 for i in range(37)] + [l + 0.004 for l in lagen[1:]] + [l - 0.004 for l in lagen[1:]]))
    rings = []
    for s in ss: rings.append(s)
    sl = ("riet", deel, naam + "_riet")
    v, f, u = B.d[sl]
    i0 = len(v)
    for s in rings:
        for k in range(SEG):
            v.append(punt(2 * math.pi * k / SEG, s))
    hoogte = [0.0]
    for j in range(1, len(rings)):
        a0, a1 = punt(0, rings[j - 1]), punt(0, rings[j]); hoogte.append(hoogte[-1] + (a1 - a0).length)
    om = 8 * e
    for j in range(len(rings) - 1):
        for k in range(SEG):
            k1 = (k + 1) % SEG
            q = (i0 + j * SEG + k, i0 + j * SEG + k1, i0 + (j + 1) * SEG + k1, i0 + (j + 1) * SEG + k)
            f.append(q)
            u.append([(k / SEG * om / 1.5, -hoogte[j] / 1.5), ((k + 1) / SEG * om / 1.5, -hoogte[j] / 1.5),
                      ((k + 1) / SEG * om / 1.5, -hoogte[j + 1] / 1.5), (k / SEG * om / 1.5, -hoogte[j + 1] / 1.5)])
    # onderkant: dikke dakrand (dik) en de onderzijde naar binnen tot boven de muur
    onder = [punt(2 * math.pi * k / SEG, 0) for k in range(SEG)]
    rand = [p - Vector((0, 0, dik)) + (p - c).to_2d().to_3d().normalized() * -0.04 for p in onder]
    binnen = [c + R @ Vector((*superring(e * 0.72, e * 0.72, rond)(2 * math.pi * k / SEG), ze + 0.05)) for k in range(SEG)]
    for k in range(SEG):
        k1 = (k + 1) % SEG
        B.vlak(sl, [rand[k], rand[k1], onder[k1], onder[k]], [(k * 0.15, 0), ((k + 1) * 0.15, 0), ((k + 1) * 0.15, 0.2), (k * 0.15, 0.2)])
        B.vlak(sl, [binnen[k], binnen[k1], rand[k1], rand[k]], [(k * 0.15, 0.4), ((k + 1) * 0.15, 0.4), ((k + 1) * 0.15, 0.8), (k * 0.15, 0.8)])
    # bovenkant dicht
    topring = [punt(2 * math.pi * k / SEG, 1.0) for k in range(SEG)]
    B.vlak(sl, topring, [(0.5 + 0.1 * math.cos(2 * math.pi * k / SEG), 0.5 + 0.1 * math.sin(2 * math.pi * k / SEG)) for k in range(SEG)])
    # donkere puntopening in de voorgevel: fijn raster op het dakvlak (+y), 3 cm voor het riet, met rietranden erlangs
    if opening:
        hb, hs = opening
        n_s, n_x = 14, 8
        def gevel(xf, s, extra):
            hx = top[0] + (e - top[0]) * breedte(s) + laaglip(s) + extra
            w = hb * (1 - s / hs)
            x = xf * w
            y = hx * max(0.0, 1 - abs(x / hx) ** rond) ** (1 / rond)
            return c + R @ Vector((x, y, ze + (zn - ze) * s))
        B.raster(("raam", deel, naam + "_gevelgat"), lambda xf, s: gevel(2 * xf - 1, s * hs * 0.999, 0.035), n_x, n_s,
                 lambda xf, s: (xf, s))
        for zij in (-1, 1):
            buis(sl, [gevel(zij, s * hs, 0.06) for s in [i / 12 for i in range(13)]], 0.11, 8, 0.4, 0.8)
    return punt


def piron(c, z, hoogte=0.95):
    sl = ("piron", "hutten", "AR_pironnen")
    c = Vector(c)
    cil(sl, c + Vector((0, 0, z - 0.25)), c + Vector((0, 0, z + 0.05)), 0.07, 0.05, 10)
    bol(sl, c + Vector((0, 0, z + 0.14)), 0.09, 0.09, 0.11, 10, 6)
    cil(sl, c + Vector((0, 0, z + 0.24)), c + Vector((0, 0, z + 0.36)), 0.035, 0.035, 8)
    bol(sl, c + Vector((0, 0, z + 0.44)), 0.065, 0.065, 0.08, 10, 6)
    cil(sl, c + Vector((0, 0, z + 0.5)), c + Vector((0, 0, z + hoogte)), 0.03, 0.004, 8)


def windvaan(c, z, soort, rot):
    """platte metalen silhouet op een staaf (zeeslang / monstervis), 1 m breed"""
    sl = ("piron", "hutten", "AR_windvanen")
    c = Vector(c); cil(sl, c + Vector((0, 0, z - 0.3)), c + Vector((0, 0, z + 1.2)), 0.03, 0.025, 8)
    if soort == "zeeslang":
        pts = []
        for k in range(25):
            t = k / 24; pts.append((-0.55 + 1.1 * t, 0.12 * math.sin(t * 2.6 * math.pi) * (1 - 0.3 * t)))
        boven = [(x, y + 0.07 * (1 - abs(x) * 0.6)) for x, y in pts]; onder = [(x, y - 0.07 * (1 - abs(x) * 0.6)) for x, y in pts]
        kop = [(0.55, 0.1), (0.72, 0.16), (0.8, 0.08), (0.7, 0.0), (0.55, -0.05)]
        omtrek = boven + kop + onder[::-1]
        vin = [(-0.2 + 0.1 * k, 0.12 * math.sin((0.35 + 0.1 * k) * 2.6 * math.pi) + 0.2) for k in range(6)]
    else:
        omtrek = [(-0.6, 0.0), (-0.75, 0.22), (-0.62, 0.02), (-0.75, -0.2), (-0.5, -0.03), (-0.1, -0.2), (0.3, -0.22), (0.55, -0.1),
                  (0.7, -0.14), (0.62, -0.02), (0.78, 0.08), (0.55, 0.14), (0.3, 0.26), (0.05, 0.34), (-0.1, 0.2), (-0.35, 0.12)]
        vin = None
    R = Matrix.Rotation(rot, 3, "Z")
    for dy in (0.012, -0.012):
        q = [c + R @ Vector((x, dy, z + 0.75 + y)) for x, y in omtrek]
        uv = [(x, y) for x, y in omtrek]
        B.vlak(sl, q if dy > 0 else q[::-1], uv if dy > 0 else uv[::-1])
    for i in range(len(omtrek)):
        a, b = omtrek[i], omtrek[(i + 1) % len(omtrek)]
        B.vlak(sl, [c + R @ Vector((a[0], -0.012, z + 0.75 + a[1])), c + R @ Vector((b[0], -0.012, z + 0.75 + b[1])),
                    c + R @ Vector((b[0], 0.012, z + 0.75 + b[1])), c + R @ Vector((a[0], 0.012, z + 0.75 + a[1]))], [(0, 0), (1, 0), (1, 0.05), (0, 0.05)])
    # windroos-kruis eronder
    for hk in (0, math.pi / 2):
        d = R @ Matrix.Rotation(hk, 3, "Z") @ Vector((0.35, 0, 0))
        cil(sl, c + Vector((0, 0, z + 0.35)) - d, c + Vector((0, 0, z + 0.35)) + d, 0.015, 0.015, 6)


def wand(sl, c, R, x0, x1, y, z0, z1, gaten=(), dik=0.07, uvs=1.2):
    """bamboewand in het lokale vlak y (van x0 tot x1, z0 tot z1), met rechthoekige gaten (gx0, gx1, gz0, gz1)"""
    xs = sorted(set([x0, x1] + [g[0] for g in gaten] + [g[1] for g in gaten]))
    zs = sorted(set([z0, z1] + [g[2] for g in gaten] + [g[3] for g in gaten]))
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            mx, mz = (xs[i] + xs[i + 1]) / 2, (zs[j] + zs[j + 1]) / 2
            if any(g[0] < mx < g[1] and g[2] < mz < g[3] for g in gaten): continue
            doos(sl, c + R @ Vector((mx, y, mz)), xs[i + 1] - xs[i], dik, zs[j + 1] - zs[j], 0, uvs,
                 kantel=R)
    return xs, zs


def brugzijde(h):
    """lokale wandzijde (+x, -x of -y) die naar het middenvlonder kijkt, of None als de hut niet aan een loopbrug ligt"""
    if h["naam"] not in ("hut2", "hut3", "hut4"): return None
    rot = math.radians(h["rot"]); d = M(P.VLONDER_MIDDEN) - M(h["c"])
    l = Matrix.Rotation(-rot, 3, "Z") @ d
    keuzes = {"+x": l.x, "-x": -l.x, "-y": -l.y}
    return max(keuzes, key=keuzes.get)


def brugpunt(h):
    rot = math.radians(h["rot"]); R = Matrix.Rotation(rot, 3, "Z"); hw = 2.5 * h["b"] / 3.0 / 2
    n = {"+x": Vector((1, 0, 0)), "-x": Vector((-1, 0, 0)), "-y": Vector((0, -1, 0))}[brugzijde(h)]
    return M(h["c"]) + R @ (n * (hw + 0.12))


def paalhut(h):
    naam = h["naam"]; c = M(h["c"]); rot = math.radians(h["rot"]); R = Matrix.Rotation(rot, 3, "Z")
    W = 2.5 * h["b"] / 3.0; hw = W / 2
    bz = brugzijde(h)
    DEUR = (-0.42, 0.42, zv_ := h["vloer"] + 0.04, h["vloer"] + 1.45)
    zv = h["vloer"]; zm = zv + 1.45; ze = zm + 0.12; zn = ze + 2.75
    grond = P.Z_STRAND if h.get("droog") else (P.bodem(*h["c"]) or 0)
    S = lambda x, y, z: c + R @ Vector((x, y, z))
    st = ("stam", "hutten", naam + "_palen")
    # hoekpalen tot de dakrand, dikke rondhout-palen
    for sx in (-1, 1):
        for sy in (-1, 1):
            cil(st, S(sx * (hw - 0.05), sy * (hw - 0.05), grond - 0.3), S(sx * (hw - 0.05), sy * (hw - 0.05), ze + 0.15), 0.135, 0.12, 12, ruw=0.06)
            if not h.get("droog"):         # touw om de voet (Archi-loopbruggen.jpg)
                cil(("touw", "hutten", naam + "_touw"), S(sx * (hw - 0.05), sy * (hw - 0.05), grond), S(sx * (hw - 0.05), sy * (hw - 0.05), 0.55), 0.165, 0.165, 12, 0.25, 0.25)
    # vloer: liggers + planken, steekt aan de voorkant 0,55 m uit (richel met reling)
    for sx in (-1, 1):
        cil(st, S(sx * (hw - 0.05), -hw - 0.1, zv - 0.12), S(sx * (hw - 0.05), hw + 0.65, zv - 0.12), 0.09, 0.09, 10)
    cil(st, S(-hw - 0.15, hw + 0.55, zv - 0.24), S(hw + 0.15, hw + 0.55, zv - 0.24), 0.08, 0.08, 10)
    for sx in (-1, 1):                     # paaltjes onder de richel
        cil(st, S(sx * (hw - 0.05), hw + 0.55, grond - 0.3), S(sx * (hw - 0.05), hw + 0.55, zv - 0.1), 0.1, 0.1, 10, ruw=0.05)
    doos(("plank", "hutten", naam + "_vloer"), S(0, 0.27, zv), W + 0.2, W + 0.75, 0.08, rot, 1.2)
    # wanden: bamboe tussen de hoekpalen; voor: deuropening tot de muurplaat, zijkanten raam met net, achter dicht
    bw = ("bamboe", "hutten", naam + "_wand")
    wand(bw, c, R, -hw + 0.08, hw - 0.08, hw - 0.04, zv + 0.04, zm, gaten=[(-0.42, 0.42, zv + 0.04, zm)])
    wand(bw, c, R, -hw + 0.08, hw - 0.08, -hw + 0.04, zv + 0.04, zm,
         gaten=[DEUR] if bz == "-y" else ([(-0.4, 0.4, zv + 0.55, zv + 1.15)] if h.get("klimtouw") else []))
    Rz = R @ Matrix.Rotation(math.pi / 2, 3, "Z")
    for zij in (-1, 1):
        # Rz draait lokaal x naar y: wand op lokale x = zij * hw ligt in het Rz-vlak y = -zij * hw
        deur = bz == ("+x" if zij > 0 else "-x")
        wand(bw, c, Rz, -hw + 0.08, hw - 0.08, -zij * (hw - 0.04), zv + 0.04, zm, gaten=[DEUR] if deur else [(-0.45, 0.45, zv + 0.5, zv + 1.15)])
        if deur: continue
        # net in het zijraam
        q = [S(zij * (hw - 0.02), y, z) for y, z in ((-0.45, zv + 0.5), (0.45, zv + 0.5), (0.45, zv + 1.15), (-0.45, zv + 1.15))]
        B.vlak(("net", "hutten", naam + "_net"), q if zij > 0 else q[::-1], [(0, 0), (0.9, 0), (0.9, 0.65), (0, 0.65)])
        B.vlak(("net", "hutten", naam + "_net"), q[::-1] if zij > 0 else q, [(0, 0.65), (0.9, 0.65), (0.9, 0), (0, 0)][::-1])
    # muurplaat en regels (rondhout rondom)
    for z in (zm + 0.04, zv + 0.08):
        for a, b in (((-hw, hw), (hw, hw)), ((-hw, -hw), (hw, -hw)), ((-hw, -hw), (-hw, hw)), ((hw, -hw), (hw, hw))):
            cil(st, S(a[0], a[1], z), S(b[0], b[1], z), 0.06, 0.06, 8)
    # reling op de richel: twee liggende stammen + net ertussen (Archi-huisje-close)
    for sx in (-1, 1):
        cil(st, S(sx * (hw - 0.05), hw + 0.55, zv), S(sx * (hw - 0.05), hw + 0.55, zv + 0.85), 0.07, 0.07, 8)
        cil(st, S(sx * (hw - 0.05), hw + 0.55, zv + 0.8), S(sx * (hw - 0.05), hw, zv + 0.8), 0.05, 0.05, 8)
    q = [S(sx * (hw - 0.05), hw + 0.55, z) for sx, z in ((-1, zv + 0.06), (-0.42 / (hw - 0.05), zv + 0.06), (-0.42 / (hw - 0.05), zv + 0.8), (-1, zv + 0.8))]
    for zij in (1, -1):
        qq = [S(zij * x, hw + 0.55, z) for x, z in (((hw - 0.05), zv + 0.06), (0.42, zv + 0.06), (0.42, zv + 0.8), ((hw - 0.05), zv + 0.8))]
        B.vlak(("net", "hutten", naam + "_net"), qq, [(0, 0), (0.6, 0), (0.6, 0.75), (0, 0.75)])
        B.vlak(("net", "hutten", naam + "_net"), qq[::-1], [(0, 0.75), (0.6, 0.75), (0.6, 0), (0, 0)])
        cil(st, S(zij * (hw - 0.05), hw + 0.55, zv + 0.8), S(zij * 0.42, hw + 0.55, zv + 0.8), 0.05, 0.05, 8)
        cil(st, S(zij * 0.42, hw + 0.55, zv), S(zij * 0.42, hw + 0.55, zv + 0.85), 0.055, 0.055, 8)
    # ladder van de grond naar de richel (voorkant), niet bij het balkon
    lad = ("stam", "hutten", naam + "_ladder")
    for sx in (-0.25, 0.25):
        cil(lad, S(sx, hw + 1.25, grond - 0.1), S(sx, hw + 0.62, zv + 0.05), 0.045, 0.045, 8)
    for k in range(1, 5):
        t = k / 5.0; y = hw + 1.25 + (0.62 - 1.25) * t; z = grond + (zv - grond) * t
        cil(lad, S(-0.3, y, z), S(0.3, y, z), 0.03, 0.03, 6)
    # dak
    spitsen = h.get("spitsen", 0) or 0
    top = (0.32, 0.1) if spitsen == 2 else (0.08, 0.08)
    e = h["b"] / 2 + 0.08
    rieten_dak(naam, c, rot, ze, zn, e, top=top, opening=(0.5, 0.62))
    if spitsen == 2:
        for sx in (-1, 1): piron(S(sx * 0.3, 0, 0), zn - 0.05)
    elif spitsen == 1 and not h.get("windvaan"):
        piron(S(0, 0, 0), zn - 0.05, 1.05)
    if h.get("windvaan"):
        piron(S(0, 0, 0), zn - 0.05, 0.6); windvaan(S(0, 0, 0), zn + 0.3, h["windvaan"], rot)
    # balkon (hut 2): aan de rechterzijkant, vloer + stammen reling
    if h.get("balkon"):
        doos(("plank", "hutten", naam + "_vloer"), S(hw + 0.45, 0, zv), 0.9, W * 0.8, 0.08, rot, 1.2)
        for y in (-W * 0.4, W * 0.4):
            cil(st, S(hw + 0.85, y, grond - 0.3), S(hw + 0.85, y, zv + 0.85), 0.08, 0.08, 10, ruw=0.05)
            cil(st, S(hw + 0.85, y, zv + 0.8), S(hw, y, zv + 0.8), 0.05, 0.05, 8)
        cil(st, S(hw + 0.85, -W * 0.4, zv + 0.8), S(hw + 0.85, W * 0.4, zv + 0.8), 0.055, 0.055, 8)
        cil(st, S(hw + 0.85, -W * 0.4, zv + 0.4), S(hw + 0.85, W * 0.4, zv + 0.4), 0.045, 0.045, 8)
    # klimtouw: van de dakrand aan de achterkant naar de grond, met knopen
    if h.get("klimtouw"):
        tw = ("touw", "hutten", naam + "_touw")
        top_p = S(0, -hw - 0.75, ze - 0.05); bot = S(0.15, -hw - 1.0, grond + 0.05)
        cil(st, S(0, -hw - 0.1, ze - 0.05), S(0, -hw - 0.95, ze - 0.05), 0.06, 0.06, 8)
        buis(tw, [top_p.lerp(bot, t) for t in [k / 10 for k in range(11)]], 0.045, 8)
        for k in range(1, 9):
            bol(tw, top_p.lerp(bot, k / 9), 0.08, 0.08, 0.07, 8, 5, 0.3)
    # lantaarn bovenin (lemma)
    lantaarn(S(0, 0, zm + 0.05), ("lantaarn", "hutten", naam + "_lantaarn"), ("lantaarnglas", "hutten", naam + "_lantaarnglas"))


def lantaarn(p, sl, slg, h=0.42):
    p = Vector(p)
    cil(sl, p + Vector((0, 0, -0.02)), p + Vector((0, 0, 0.35)), 0.01, 0.01, 6)
    cil(sl, p - Vector((0, 0, h * 0.62)), p - Vector((0, 0, h * 0.55)), 0.12, 0.12, 8)
    cil(slg, p - Vector((0, 0, h * 0.55)), p - Vector((0, 0, h * 0.15)), 0.1, 0.1, 8)
    cil(sl, p - Vector((0, 0, h * 0.15)), p - Vector((0, 0, h * 0.02)), 0.13, 0.03, 8)


def ronde_hut():
    h = P.RONDE_HUT; c = M(h["c"]); r = h["r"]
    z0 = P.Z_STRAND; zm = z0 + 2.0; ze = zm + 0.1; zn = ze + 2.6
    deur = math.radians(225)                # naar het bad (zuidwest)
    bw = ("bamboe", "hutten", "hut5_wand")
    SEG = 20
    for k in range(SEG):
        a0, a1 = 2 * math.pi * k / SEG, 2 * math.pi * (k + 1) / SEG
        am = (a0 + a1) / 2
        if abs((am - deur + math.pi) % (2 * math.pi) - math.pi) < 0.32: continue
        rr = r * 0.78
        p0 = c + Vector((math.cos(a0) * rr, math.sin(a0) * rr, 0)); p1 = c + Vector((math.cos(a1) * rr, math.sin(a1) * rr, 0))
        q = [p0 + Vector((0, 0, z0)), p1 + Vector((0, 0, z0)), p1 + Vector((0, 0, zm)), p0 + Vector((0, 0, zm))]
        uv = [(k * 0.43 / 1.2, z0 / 1.2), ((k + 1) * 0.43 / 1.2, z0 / 1.2), ((k + 1) * 0.43 / 1.2, zm / 1.2), (k * 0.43 / 1.2, zm / 1.2)]
        B.vlak(bw, q, uv)
        qi = [p + (c - p).normalized() * 0.06 * Vector((1, 1, 0)).length / 1.414 for p in q]
        B.vlak(bw, qi[::-1], uv[::-1])
    st = ("stam", "hutten", "hut5_palen")
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.2
        p = c + Vector((math.cos(a), math.sin(a), 0)) * r * 0.8
        cil(st, p + Vector((0, 0, z0 - 0.1)), p + Vector((0, 0, ze + 0.1)), 0.09, 0.08, 10, ruw=0.05)
    for dz in (zm + 0.03,):
        pts = [c + Vector((math.cos(2 * math.pi * k / 24) * r * 0.8, math.sin(2 * math.pi * k / 24) * r * 0.8, dz)) for k in range(25)]
        buis(st, pts, 0.06, 8, 0.4, 1.5)
    dak = rieten_dak("hut5", c, 0.0, ze, zn - 0.8, r * 1.18, top=(r * 0.42, r * 0.42), lagen=(0.0, 0.5), lip=0.15, rond=2.0, rok=False)
    rieten_dak("hut5_hoed", c, 0.0, zn - 0.95, zn + 0.25, r * 0.55, top=(0.05, 0.05), lagen=(0.0,), lip=0.1, rond=2.0, dik=0.2, rok=False)
    piron(c, zn + 0.2, 0.7)


def loopbruggen():
    vm = M(P.VLONDER_MIDDEN); zmid = 0.95
    st = ("stam", "hutten", "AR_loopbrug_palen"); pl = ("plank", "hutten", "AR_loopbrug_planken")
    grond = P.bodem(*P.VLONDER_MIDDEN) or -0.3
    for sx in (-1, 1):
        for sy in (-1, 1):
            cil(st, vm + Vector((sx * 0.75, sy * 0.75, grond - 0.3)), vm + Vector((sx * 0.75, sy * 0.75, zmid + 0.9)), 0.11, 0.1, 10, ruw=0.06)
            cil(("touw", "hutten", "AR_loopbrug_touw"), vm + Vector((sx * 0.75, sy * 0.75, grond)), vm + Vector((sx * 0.75, sy * 0.75, 0.5)), 0.14, 0.14, 10, 0.25, 0.25)
    for k in range(9):
        doos(pl, vm + Vector((0, -0.72 + k * 0.18, zmid)), 1.7, 0.15, 0.05, 0, 1.2)
    for sx in (-1, 1):
        cil(st, vm + Vector((sx * 0.6, -0.85, zmid - 0.08)), vm + Vector((sx * 0.6, 0.85, zmid - 0.08)), 0.07, 0.07, 8)
    hut_vloer = {h["naam"]: h for h in P.HUTTEN}
    for hn in ("hut2", "hut4", "hut3"):
        h = hut_vloer[hn]; A, Bp = vm.copy(), brugpunt(h)
        zA, zB = zmid, h["vloer"] - 0.02
        d = (Bp - A); L = d.length; t = d.normalized(); nrm = Vector((-t.y, t.x, 0))
        A = A + t * 0.85
        L2 = (Bp - A).length
        for zij in (-1, 1):
            cil(st, A + nrm * zij * 0.24 + Vector((0, 0, zA - 0.07)), Bp + nrm * zij * 0.24 + Vector((0, 0, zB - 0.07)), 0.055, 0.055, 8)
        n = int(L2 / 0.2)
        for k in range(n + 1):
            p = A.lerp(Bp, k / n); z = zA + (zB - zA) * k / n
            doos(pl, p + Vector((0, 0, z)), 0.62, 0.13, 0.045, math.atan2(t.y, t.x) - math.pi / 2 + rnd.uniform(-0.06, 0.06), 1.2)
        # paaltjes halverwege + touwleuning aan een kant
        mid = A.lerp(Bp, 0.5); zm_ = (zA + zB) / 2; g = P.bodem(*(P.OORSPRONG[0] + mid.x, P.OORSPRONG[1] + mid.y)) or -0.3
        for zij in (-1, 1):
            cil(st, mid + nrm * zij * 0.3 + Vector((0, 0, g - 0.3)), mid + nrm * zij * 0.3 + Vector((0, 0, zm_ + (0.9 if zij > 0 else 0))), 0.08, 0.075, 10, ruw=0.05)
        pts = [A.lerp(Bp, k / 8) + nrm * 0.3 + Vector((0, 0, zA + (zB - zA) * k / 8 + 0.85 - 0.12 * math.sin(math.pi * k / 8))) for k in range(9)]
        buis(("touw", "hutten", "AR_loopbrug_touw"), pts, 0.03, 6)


# ---------------------------------------------------------------- wrak
def romp(naam, c, rot, L, Bmax, H, achter=True, kantel=(0, 0)):
    """halve scheepsromp: U-doorsneden langs de lengte; achter=True: spiegel (vlak) aan het eind t=1, anders steven
    die omhoog krult. Breekrand aan t=0 gekarteld. Kantel: (slagzij, kop) in graden."""
    R = Matrix.Rotation(rot, 3, "Z") @ Matrix.Rotation(math.radians(kantel[0]), 3, "X") @ Matrix.Rotation(math.radians(kantel[1]), 3, "Y")
    c = Vector(c)
    NL, NS = 16, 14
    breuk = [0.15 * math.sin(k * 2.3) + 0.12 * math.sin(k * 5.1) for k in range(NS + 1)]
    def doorsnede(t, s, binnen=False):
        """t langs de romp 0..1, s rond de doorsnede 0 (bakboord boven) .. 1 (stuurboord boven)"""
        if achter:
            b = Bmax * (0.75 + 0.25 * math.sin(math.pi * min(1, t * 1.1)) ** 0.5) * (1 - 0.15 * t)
            zt = H * (0.55 + 0.45 * t ** 1.6)               # zeeg loopt op naar de spiegel
        else:
            b = Bmax * (1 - t ** 2.2) + 0.06
            zt = H * (0.5 + 0.5 * t ** 2.5)
        a = math.pi * s
        y = -math.cos(a) * b * (1 - 0.55 * math.sin(a) ** 4)      # rechte zijden, naar onderen een V-kiel
        z = -math.sin(a) ** 1.1 * H * 0.62 + zt - H * 0.35
        x = (t - 0.5) * L
        if not achter and t > 0.6:                          # steven: smal en krullend
            x += (t - 0.6) * 0.0
        if binnen:
            y *= 0.88; z += 0.08
        if t == 0: z = min(z, zt - H * 0.35 + breuk[int(round(s * NS))] - 0.1) if s in (0, 1) else z
        return c + R @ Vector((x, y, z))
    rol_buiten = "romp" if achter else "schubben"
    B.raster((rol_buiten, "decor", naam + "_buiten"), lambda t, s: doorsnede(t, s), NL, NS,
             lambda t, s: (t * L / (1.5 if achter else 0.8), s * 2.5 / (1.5 if achter else 0.8)), omdraaien=True)
    B.raster(("plank", "decor", naam + "_binnen"), lambda t, s: doorsnede(t, s, True), NL, NS, lambda t, s: (t * L / 1.2, s * 2.2 / 1.2))
    # gouden rand bovenlangs (beide zijden) en kartelrand voor
    for s in (0.0, 1.0):
        buis(("goud", "decor", naam + "_rand"), [doorsnede(k / NL, s).lerp(doorsnede(k / NL, s, True), 0.5) for k in range(NL + 1)], 0.06, 8)
    for k in range(NS):
        p0, p1 = doorsnede(0, k / NS), doorsnede(0, (k + 1) / NS); q0, q1 = doorsnede(0, k / NS, True), doorsnede(0, (k + 1) / NS, True)
        B.vlak(("plank", "decor", naam + "_binnen"), [p0, p1, q1, q0], [(0, 0), (0.1, 0), (0.1, 0.05), (0, 0.05)])
    if achter:
        # spiegel: vlak paneel op t=1 met krultextuur, iets breder, gouden lijst rondom
        ring_pts = [doorsnede(1, k / NS) for k in range(NS + 1)]
        top_l, top_r = ring_pts[0], ring_pts[-1]
        midden = (top_l + top_r) / 2 + R @ Vector((0, 0, 0.35))
        boog = [top_l.lerp(top_r, k / 10) + R @ Vector((0, 0, 0.35 * math.sin(math.pi * k / 10))) for k in range(11)]
        omtrek = boog + ring_pts[::-1][1:-1]
        zmin = min(p.z for p in omtrek); zmax = max(p.z for p in omtrek)
        ymin = min((R.inverted() @ (p - c)).y for p in omtrek); ymax = max((R.inverted() @ (p - c)).y for p in omtrek)
        uv = [(((R.inverted() @ (p - c)).y - ymin) / (ymax - ymin), (p.z - zmin) / (zmax - zmin)) for p in omtrek]
        off = R @ Vector((0.02, 0, 0))
        midp = sum(omtrek, Vector()) / len(omtrek)
        for i in range(len(omtrek)):
            a, b = omtrek[i], omtrek[(i + 1) % len(omtrek)]
            B.vlak(("krul", "decor", naam + "_spiegel"), [midp + off, a + off, b + off],
                   [(0.5, 0.5), uv[i], uv[(i + 1) % len(omtrek)]])
            B.vlak(("plank", "decor", naam + "_binnen"), [midp - off * 2, b - off * 2, a - off * 2],
                   [(0.5, 0.5), uv[(i + 1) % len(omtrek)], uv[i]])
        buis(("goud", "decor", naam + "_rand"), [p + off * 2 for p in boog], 0.07, 8)
        # krullen op de spiegelhoeken
        for p in (top_l, top_r):
            bol(("goud", "decor", naam + "_rand"), p + R @ Vector((0.05, 0, 0.1)), 0.12, 0.12, 0.12, 10, 6)
        # bankje binnenin
        doos(("plank", "decor", naam + "_binnen"), c + R @ Vector((L * 0.25, 0, -H * 0.05)), 0.4, Bmax * 1.5, 0.08, 0, 1.2, kantel=R)
    else:
        # voorsteven: krullende steven vanaf t=1 omhoog en terug, met goud
        p_top = doorsnede(1, 0.5)
        krul = []
        for k in range(14):
            a = k / 13 * 1.6 * math.pi; r = 0.55 * (1 - k / 18)
            krul.append(p_top + R @ Vector((0.25 + r * math.sin(a) * 0.9, 0, 0.1 + r * (1 - math.cos(a)) * 1.2)))
        buis(("schubben", "decor", naam + "_steven"), krul, 0.13, 10, 0.8, 0.8)
        buis(("goud", "decor", naam + "_rand"), [p + R @ Vector((0.06, 0, 0.06)) for p in krul], 0.04, 6)
        bol(("goud", "decor", naam + "_rand"), krul[-1], 0.13, 0.13, 0.13, 10, 6)


def wrak():
    w = P.WRAK
    x, y, r = w["achtersteven"]
    zb = P.bodem(x, y) or -0.4
    romp("AR_achterschip", M((x, y), zb + 0.7), math.radians(r), 2.3, 0.78, 1.6, True, kantel=(9, -7))
    x, y, r = w["voorsteven"]
    zb = P.bodem(x, y) or -0.4
    romp("AR_voorschip", M((x, y), zb + 0.8), math.radians(r), 2.0, 0.8, 1.9, False, kantel=(-12, 10))
    # omgevallen mast als evenwichtsbalk, op twee paaltjes (Archipel_zonnig_2022)
    (ax, ay), (bx, by) = w["balk"]
    za, zb2 = (P.bodem(ax, ay) or -0.4), (P.bodem(bx, by) or -0.4)
    ms = ("mast", "decor", "AR_balk")
    cil(ms, M((ax, ay), 0.5), M((bx, by), 0.42), 0.23, 0.2, 14, 0.9, 1.5, ruw=0.03)
    for t in (0.22, 0.78):
        p = M((ax + (bx - ax) * t, ay + (by - ay) * t))
        cil(ms, p + Vector((0, 0, (P.bodem(ax + (bx - ax) * t, ay + (by - ay) * t) or -0.4) - 0.2)), p + Vector((0, 0, 0.4)), 0.07, 0.07, 8)
    # staande mast: lantaarn, wimpel, ra-stompje, touw naar het voorschip
    x, y, hgt = w["mast"]; p = M((x, y)); g = P.bodem(x, y) or -0.4
    cil(("mast", "decor", "AR_mast"), p + Vector((0, 0, g - 0.3)), p + Vector((0, 0, hgt)), 0.15, 0.09, 14, 0.6, 1.5)
    bol(("goud", "decor", "AR_mast_goud"), p + Vector((0, 0, hgt + 0.08)), 0.1, 0.1, 0.1, 10, 6)
    cil(("mast", "decor", "AR_mast"), p + Vector((-0.6, 0, hgt - 1.6)), p + Vector((0.6, 0, hgt - 1.6)), 0.06, 0.05, 8)
    for zz in (1.2, 2.6):
        cil(("touw", "decor", "AR_mast_touw"), p + Vector((0, 0, zz - 0.15)), p + Vector((0, 0, zz + 0.15)), 0.17, 0.17, 10, 0.25, 0.25)
    vl = [p + Vector((0.08, 0, hgt - 0.1)), p + Vector((1.25, 0.1, hgt - 0.28)), p + Vector((0.08, 0, hgt - 0.5))]
    B.vlak(("vlag", "decor", "AR_wimpel"), vl, [(0, 1), (1, 0.5), (0, 0)]); B.vlak(("vlag", "decor", "AR_wimpel"), vl[::-1], [(0, 0), (1, 0.5), (0, 1)])
    arm = p + Vector((0, -0.45, hgt - 2.3))
    cil(("lantaarn", "decor", "AR_mast_lantaarn"), p + Vector((0, -0.1, hgt - 2.3)), arm, 0.02, 0.02, 6)
    lantaarn(arm, ("lantaarn", "decor", "AR_mast_lantaarn"), ("lantaarnglas", "decor", "AR_mast_lantaarnglas"), 0.5)
    vx, vy, _ = w["voorsteven"]
    buis(("touw", "decor", "AR_mast_touw"), [(p + Vector((0, 0, hgt - 1.7))).lerp(M((vx, vy), 1.5), k / 10) - Vector((0, 0, 0.3 * math.sin(math.pi * k / 10))) for k in range(11)], 0.025, 6)


def paalvisser():
    x, y, zs = P.PAALVISSER; p = M((x, y)); g = P.bodem(x, y) or -0.4
    st = ("stam", "decor", "AR_paalvisser_paal")
    cil(st, p + Vector((0, 0, g - 0.3)), p + Vector((0, 0, zs + 1.4)), 0.17, 0.14, 12, ruw=0.06)
    cil(("touw", "decor", "AR_paalvisser_touw"), p + Vector((0, 0, g)), p + Vector((0, 0, 0.6)), 0.21, 0.21, 12, 0.25, 0.25)
    # zitbalk (dwars) met schoorstok en voetsteun, vastgebonden met touw
    rv = Vector((0.0, 1.0, 0.0))               # figuur kijkt naar het oosten (+x), zitbalk noord-zuid
    cil(st, p + Vector((0.1, -0.75, zs)), p + Vector((0.1, 0.75, zs)), 0.06, 0.05, 8)
    cil(st, p + Vector((0.12, 0, zs - 0.9)), p + Vector((0.55, 0, zs - 0.55)), 0.04, 0.04, 6)
    cil(st, p + Vector((0.55, -0.35, zs - 0.62)), p + Vector((0.55, 0.35, zs - 0.62)), 0.035, 0.035, 6)
    for zz in (zs, zs - 0.62):
        cil(("touw", "decor", "AR_paalvisser_touw"), p + Vector((0, 0, zz - 0.06)), p + Vector((0, 0, zz + 0.06)), 0.18, 0.18, 10, 0.25, 0.25)
    f = p + Vector((0.26, 0, zs + 0.06))      # zitpunt
    hu, hm, ba, tu, sj, br = (("huid", "decor", "AR_figuur_huid"), ("hemd", "decor", "AR_figuur_hemd"), ("baard", "decor", "AR_figuur_baard"),
                              ("tulband", "decor", "AR_figuur_tulband"), ("sjerp", "decor", "AR_figuur_sjerp"), ("broek", "decor", "AR_figuur_broek"))
    # benen: dijen naar voren, onderbenen naar beneden (pofbroek), blote voeten op de voetsteun
    for sy in (-0.12, 0.12):
        heup = f + Vector((0, sy, 0.05)); knie = f + Vector((0.42, sy * 1.2, 0.02)); enkel = f + Vector((0.36, sy * 1.25, -0.55))
        cil(br, heup, knie, 0.11, 0.1, 10); bol(br, knie, 0.11, 0.11, 0.11, 10, 6); cil(br, knie, enkel + Vector((0, 0, 0.1)), 0.11, 0.075, 10)
        cil(hu, enkel + Vector((0, 0, 0.12)), enkel, 0.045, 0.045, 8); bol(hu, enkel + Vector((0.06, 0, -0.03)), 0.11, 0.05, 0.04, 8, 5)
    # romp, sjerp, hemd
    cil(sj, f + Vector((0, 0, 0.06)), f + Vector((-0.01, 0, 0.26)), 0.17, 0.16, 12)
    cil(hm, f + Vector((-0.01, 0, 0.25)), f + Vector((-0.03, 0, 0.62)), 0.16, 0.19, 12)
    cil(hu, f + Vector((0.06, 0, 0.5)), f + Vector((0.1, 0, 0.62)), 0.06, 0.04, 8)          # blote borst in de hals
    bol(hm, f + Vector((-0.03, 0, 0.62)), 0.2, 0.2, 0.08, 12, 6)
    # hoofd, baard, tulband
    kop = f + Vector((-0.01, 0, 0.8))
    cil(hu, f + Vector((-0.02, 0, 0.64)), kop, 0.06, 0.06, 8)
    bol(hu, kop + Vector((0, 0, 0.04)), 0.1, 0.095, 0.12, 12, 8)
    bol(hu, kop + Vector((0.1, 0, 0.03)), 0.03, 0.025, 0.04, 6, 4)                          # neus
    bol(ba, kop + Vector((0.07, 0, -0.06)), 0.07, 0.08, 0.1, 10, 6)
    for k, (rr, zz) in enumerate(((0.12, 0.1), (0.125, 0.15), (0.115, 0.2), (0.09, 0.245))):
        cil(tu, kop + Vector((-0.01, 0, zz - 0.03)), kop + Vector((-0.01, 0, zz + 0.03)), rr, rr * 0.97, 12)
    bol(tu, kop + Vector((-0.01, 0, 0.25)), 0.07, 0.07, 0.05, 10, 5)
    # armen: rechts houdt de hengel, links op de schoorstok
    for sy, hand in ((-0.2, f + Vector((0.32, -0.08, 0.38))), (0.2, f + Vector((0.25, 0.3, 0.3)))):
        sch = f + Vector((-0.02, sy, 0.58)); el = f + Vector((0.12, sy * 1.15, 0.36))
        cil(hm, sch, el, 0.065, 0.06, 8); cil(hu, el, hand, 0.05, 0.04, 8); bol(hu, hand, 0.05, 0.05, 0.05, 8, 5)
    hand = f + Vector((0.32, -0.08, 0.38))
    eind = hand + Vector((2.4, -0.6, 1.0))
    cil(("hengel", "decor", "AR_figuur_hengel"), hand - Vector((0.3, -0.07, 0.12)), eind, 0.022, 0.008, 6)
    vis = eind - Vector((0, 0, 1.3))
    cil(("hengel", "decor", "AR_figuur_hengel"), eind, vis + Vector((0, 0, 0.25)), 0.004, 0.004, 4, doppen=False)
    vv = ("vis", "decor", "AR_figuur_vis")
    bol(vv, vis, 0.07, 0.035, 0.22, 10, 7)
    B.vlak(vv, [vis - Vector((0, 0, 0.2)), vis + Vector((0.09, 0, -0.38)), vis + Vector((-0.09, 0, -0.38))], [(0.5, 1), (1, 0), (0, 0)])
    B.vlak(vv, [vis - Vector((0, 0, 0.2)), vis + Vector((-0.09, 0, -0.38)), vis + Vector((0.09, 0, -0.38))], [(0.5, 1), (0, 0), (1, 0)])


def klimpalen():
    for x, y, hgt in P.KLIMPALEN:
        p = M((x, y)); g = P.bodem(x, y) or -0.3
        cil(("stam", "decor", "AR_klimpalen"), p + Vector((0, 0, g - 0.3)), p + Vector((0, 0, hgt)), 0.16, 0.13, 12, ruw=0.06)
        cil(("touw", "decor", "AR_klimpalen_touw"), p + Vector((0, 0, g)), p + Vector((0, 0, 0.55)), 0.2, 0.2, 12, 0.25, 0.25)
        for k in range(int(hgt / 0.5)):                      # klimpennen
            a = k * 2.1; z = 0.7 + k * 0.42
            d = Vector((math.cos(a), math.sin(a), 0))
            cil(("stam", "decor", "AR_klimpalen"), p + d * 0.1 + Vector((0, 0, z)), p + d * 0.42 + Vector((0, 0, z + 0.05)), 0.035, 0.035, 6)


def kisten():
    rollen = ["kist_blauw", "kist_rood", "kist_hout"]
    for k, (x, y, r) in enumerate(P.KISTEN):
        g = P.bodem(x, y) or 0; rot = math.radians(r); rol = rollen[k % 3]
        hoog = 0.62 + (0.1 if k % 4 == 1 else 0)
        kist(M((x, y), g), rot, 0.82, 0.82, hoog, rol, gat=(k % 2 == 0))
        if k in (3, 8):                                       # gestapeld
            kist(M((x, y), g + hoog), rot + 0.4, 0.62, 0.62, 0.48, rollen[(k + 1) % 3], gat=False)
    x, y, r = P.SCHATKIST; g = P.bodem(x, y) or 0; rot = math.radians(r); c = M((x, y), g)
    R = Matrix.Rotation(rot, 3, "Z")
    doos(("kist_rood", "decor", "AR_schatkist"), c + Vector((0, 0, 0.22)), 0.8, 0.52, 0.44, rot, 1.2)
    B.raster(("kist_rood", "decor", "AR_schatkist"), lambda s, t: c + R @ Vector(((s - 0.5) * 0.8, -math.cos(math.pi * t) * 0.26, 0.44 + math.sin(math.pi * t) * 0.2)),
             1, 8, lambda s, t: (s * 0.8, t * 0.8), omdraaien=True)
    for zij in (-1, 1):
        q = [c + R @ Vector((zij * 0.4, -math.cos(math.pi * k / 8) * 0.26, 0.44 + math.sin(math.pi * k / 8) * 0.2)) for k in range(9)]
        B.vlak(("kist_rood", "decor", "AR_schatkist"), q if zij > 0 else q[::-1], [(k / 8, 0.5) for k in range(9)])
    for xb in (-0.3, 0.3):
        B.raster(("ijzer", "decor", "AR_schatkist_beslag"), lambda s, t: c + R @ Vector((xb + (s - 0.5) * 0.06, -math.cos(math.pi * t) * 0.275, 0.44 + math.sin(math.pi * t) * 0.215)),
                 1, 8, lambda s, t: (s, t), omdraaien=True)
    doos(("goud", "decor", "AR_schatkist_slot"), c + R @ Vector((0, 0.27, 0.42)), 0.1, 0.03, 0.12, rot, 0.3)


def kist(c, rot, sx, sy, sz, rol, gat=True):
    R = Matrix.Rotation(rot, 3, "Z")
    doos((rol, "decor", "AR_" + rol), c + Vector((0, 0, sz / 2)), sx, sy, sz, rot, 1.2)
    # latten op de ribben (donker hout)
    lat = ("ijzer" if rol == "kist_blauw" else "kist_hout", "decor", "AR_kist_latten") if False else ("kist_hout", "decor", "AR_kist_latten")
    for zx in (-1, 1):
        for zy in (-1, 1):
            doos(lat, c + R @ Vector((zx * (sx / 2 - 0.02), zy * (sy / 2 - 0.02), sz / 2)), 0.08, 0.08, sz + 0.02, rot, 1.2)
    for zz in (0.03, sz - 0.03):
        for zy in (-1, 1):
            doos(lat, c + R @ Vector((0, zy * (sy / 2 + 0.005), zz)), sx, 0.04, 0.07, rot, 1.2)
        for zx in (-1, 1):
            doos(lat, c + R @ Vector((zx * (sx / 2 + 0.005), 0, zz)), 0.04, sy, 0.07, rot, 1.2)
    if gat:                                                    # rond gat in een zijkant (Archipel-boot.jpg)
        pts = [c + R @ Vector((0.17 * math.cos(2 * math.pi * k / 14), sy / 2 + 0.012, sz * 0.55 + 0.17 * math.sin(2 * math.pi * k / 14))) for k in range(14)]
        B.vlak(("raam", "decor", "AR_kist_gaten"), pts, [(0.5 + 0.5 * math.cos(2 * math.pi * k / 14), 0.5 + 0.5 * math.sin(2 * math.pi * k / 14)) for k in range(14)])


def tonnen():
    for x, y in P.TONNEN:
        g = P.bodem(x, y) or 0; c = M((x, y), g)
        cil(("ton", "decor", "AR_tonnen"), c, c + Vector((0, 0, 0.42)), 0.4, 0.4, 18, 1.2, 1.2)
        for zz in (0.08, 0.34):
            cil(("ijzer", "decor", "AR_tonnen_banden"), c + Vector((0, 0, zz - 0.03)), c + Vector((0, 0, zz + 0.03)), 0.415, 0.415, 18)
        cil(("tondeksel", "decor", "AR_tonnen_deksel"), c + Vector((0, 0, 0.42)), c + Vector((0, 0, 0.45)), 0.36, 0.36, 18)


def ingang():
    pts = P.INGANG_VLONDER
    pl = ("plank", "decor", "AR_ingangsvlonder"); st = ("stam", "decor", "AR_ingangsvlonder_liggers")
    for a, b in zip(pts, pts[1:]):
        A, Bp = M(a), M(b); d = Bp - A; t = d.normalized(); n = int(d.length / 0.16)
        for k in range(n):
            p = A.lerp(Bp, (k + 0.5) / n)
            doos(pl, p + Vector((0, 0, P.Z_MAAIVELD + 0.08)), P.INGANG_BREEDTE, 0.145, 0.05, math.atan2(t.y, t.x) - math.pi / 2, 1.2)
        nr = Vector((-t.y, t.x, 0))
        for zij in (-0.9, 0, 0.9):
            cil(st, A + nr * zij + Vector((0, 0, P.Z_MAAIVELD)), Bp + nr * zij + Vector((0, 0, P.Z_MAAIVELD)), 0.06, 0.06, 6)


def render(uit):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True
    cam_d = bpy.data.cameras.new("gatecam"); cam = bpy.data.objects.new("gatecam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    for o in bpy.data.objects:
        if o.get("owner") == "phase:02_blockout": o.hide_render = True
    cam_d.type = "PERSP"; cam_d.lens = 24; sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    for naam, pos, doel, lens in (("vrm_alle", (467.2, 157.6, 1.7), (448.0, 157.5, 2.6), 26), ("vrm_zonnig", (463.6, 163.4, 1.7), (452.0, 154.5, 2.0), 24),
                                  ("vrm_hut", (447.6, 151.2, 1.6), (450.8, 154.6, 2.6), 24), ("vrm_wrak", (466.0, 153.5, 1.6), (461.0, 159.0, 1.0), 30),
                                  ("vrm_vogel", (468.0, 140.0, 16.0), (451.0, 159.0, 0.0), 28)):
        p = M(pos[:2], pos[2]); q = M(doel[:2], doel[2]); cam_d.lens = lens
        cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(uit, naam + ".png"); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def main():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    master = os.path.abspath(a[a.index("--master") + 1]) if "--master" in a else os.path.join(D, "AR_Archipel_master.blend")
    bpy.ops.wm.open_mainfile(filepath=master)
    for o in [o for o in bpy.data.objects if o.get("owner") in (OWNER, "phase:02_blockout")]:
        if o.get("owner") == OWNER: bpy.data.objects.remove(o)
        else: o.hide_render = True; o.hide_set(True)
    for me in [m for m in bpy.data.meshes if m.users == 0]: bpy.data.meshes.remove(me)
    bad()
    for h in P.HUTTEN: paalhut(h)
    ronde_hut(); loopbruggen(); wrak(); paalvisser(); klimpalen(); kisten(); tonnen(); ingang()
    B.bouw()
    bpy.ops.wm.save_as_mainfile(filepath=master)
    n = sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER)
    print("[03_vormen] klaar:", len([o for o in bpy.data.objects if o.get("owner") == OWNER]), "objecten,", n, "vlakken")
    if "--render" in a:
        uit = os.path.join(D, "review", "03_vormen"); os.makedirs(uit, exist_ok=True); render(uit)


main()
