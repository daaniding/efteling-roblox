"""17_steenwerk: de breuksteenmuren en randstenen van ingang en wachtrij als losse 3D-stenen (Daan: "de scene is niet het niveau
van de attractie"). Draai NA 12_omgeving.py (gebruikt diens maten en hulpfuncties) en VOOR 05_materials.py.
Video fmEZsIkqsl8 (0:04-0:12 plein, 0:20-0:30 laantje, 0:39 tribune, 6:40 uitgang):
  - droog gestapelde platte stenen in horizontale lagen: 20-55 cm breed, 9-20 cm hoog, steken 1-6 cm uit, donkere voegen;
  - bovenop een rafelige rand van grotere platte dekstenen;
  - rotsblokken 25-50 cm als rand van het laantje (tuinkant) en langs het onderpad;
  - grijze natuurstenen neuzen op de tribunerijen (0:39).
De gladde muren van 12_omgeving blijven als achterwand (rol "voeg": donker, zit achter de stenen).
Stenen per muur in een object; UV in de steenatlas (04f_texturen_steen.py), tegel per steen -> obj["uv_vast"].
Gebruik: blender --background --python build/17_steenwerk.py -- --master AR_Pagode_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix

HIER = os.path.dirname(os.path.abspath(__file__))
NS = {"__name__": "omgeving12", "__file__": os.path.join(HIER, "12_omgeving.py")}
bron = open(os.path.join(HIER, "12_omgeving.py")).read().rsplit("\nbuild()", 1)[0]
exec(compile(bron, "12_omgeving.py", "exec"), NS)
OWNER = "phase:17_steenwerk"; NS["OWNER"] = OWNER
pt, aL, aR, aW, ztop, ringsector = NS["pt"], NS["aL"], NS["aR"], NS["aW"], NS["ztop"], NS["ringsector"]
Z_I, Z_P, R_BO, R_VL, N_RIJ, A_ZUID = NS["Z_I"], NS["Z_P"], NS["R_BO"], NS["R_VL"], NS["N_RIJ"], NS["A_ZUID"]
rnd = random.Random(17)
TRIS = [0]
_mj = os.path.join(os.path.dirname(HIER), "exports", "omgeving_meubilair.json")
MEUBEL = [Vector((x, y, 0)) for _, x, y, _ in json.load(open(_mj))] if os.path.exists(_mj) else []


def botst(c, L):
    """Rotsblok niet op een lantaarn, bak, bordpaal of bank zetten (12_omgeving schrijft hun plekken weg)."""
    return any((Vector((c.x, c.y, 0)) - m).length < L * 0.6 + 0.35 for m in MEUBEL)
ROTS_TEGELS = [0, 2, 4, 5, 7, 8, 10, 12, 14, 15]           # geen lichte beige tegels voor losse rotsen (video: grijs, mossig)


def tegel_uv(k, fu, fv, marge=0.05):
    """fu, fv in 0..1 binnen de tegel; marge houdt de mipmaps binnen de tegel."""
    ty, tx = divmod(k, 4)
    return ((tx + marge + (1 - 2 * marge) * fu) / 4, 1 - (ty + marge + (1 - 2 * marge) * (1 - fv)) / 4)


def muursteen(bm, uv, c, xa, ya, w, h, d):
    """Steen in een muur: voorkant 3x3 raster (midden bol), zijkanten schuin naar een grotere achterring (geen achterkant).
    c = midden voorkant-achterkant, xa = langs de muur, ya = naar buiten (z omhoog). 24 driehoeken."""
    za = xa.cross(ya).normalized() * -1
    if za.z < 0: za = -za
    k = rnd.randrange(16); j = lambda s: rnd.uniform(-s, s)
    voor = {}
    for i in (-1, 0, 1):
        for q in (-1, 0, 1):
            x = i * w / 2 * 0.97 + j(w * 0.06); z = q * h / 2 * 0.93 + j(h * 0.1)
            y = d / 2 - 0.012 * (abs(i) + abs(q)) + j(0.014)
            voor[(i, q)] = (bm.verts.new(c + xa * x + ya * y + za * z), (0.5 + x / w, 0.5 + z / h))
    ring = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
    achter = {}
    for i, q in ring:
        x = i * w / 2 * 1.02 + j(w * 0.03); z = q * h / 2 * 1.04 + j(h * 0.05)
        achter[(i, q)] = bm.verts.new(c + xa * x + ya * (-d / 2) + za * z)
    def vlak(vs, uvs):
        f = bm.faces.new(vs); f.smooth = True
        for l, (fu, fv) in zip(f.loops, uvs): l[uv].uv = tegel_uv(k, min(1, max(0, fu)), min(1, max(0, fv)))
        f.normal_update()
        if f.normal.dot(f.calc_center_median() - c) < 0: f.normal_flip()   # Roblox tekent alleen de voorkant: altijd naar buiten (UV gaat mee)
    for i in (-1, 0):
        for q in (-1, 0):
            sl = [(i, q), (i + 1, q), (i + 1, q + 1), (i, q + 1)]
            vlak([voor[s][0] for s in sl], [voor[s][1] for s in sl])
    for n in range(8):
        a, b = ring[n], ring[(n + 1) % 8]
        ua, ub = voor[a][1], voor[b][1]
        ra = (0.5 + a[0] * 0.5, 0.5 + a[1] * 0.5); rb = (0.5 + b[0] * 0.5, 0.5 + b[1] * 0.5)
        vlak([achter[a], achter[b], voor[b][0], voor[a][0]], [ra, rb, ub, ua])
    TRIS[0] += 24


def blok(bm, uv, c, s, rot, afrond=0.55, bodem=None):
    """Rond rotsblok/dekseen: kubus 1x onderverdeeld (26 punten), deels naar een ellipsoide getrokken, verschoven. 48 driehoeken.
    s = (lengte, breedte, hoogte), rot = Matrix 3x3; UV doosprojectie binnen een tegel."""
    t = bmesh.new(); bmesh.ops.create_cube(t, size=2.0)
    bmesh.ops.subdivide_edges(t, edges=t.edges[:], cuts=1, use_grid_fill=True)
    k = rnd.choice(ROTS_TEGELS)
    for v in t.verts:
        n = v.co.normalized(); v.co = v.co * (1 - afrond) + n * 1.15 * afrond
        v.co += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * (0.16 + 0.12 * afrond)
        v.co = Vector((v.co.x * s[0] / 2, v.co.y * s[1] / 2, v.co.z * s[2] / 2))
        if bodem is not None and v.co.z < bodem: v.co.z = bodem
    vmap = {}
    for v in t.verts: vmap[v] = bm.verts.new(c + rot @ v.co)
    for f in t.faces:
        nf = bm.faces.new([vmap[v] for v in f.verts]); nf.smooth = True
        nn = f.normal; ax = max(range(3), key=lambda i: abs(nn[i]))
        for l, ol in zip(nf.loops, f.loops):
            p = ol.vert.co; a, b = [(1, 2), (0, 2), (0, 1)][ax]
            l[uv].uv = tegel_uv(k, 0.5 + p[a] / max(s[a], 0.01) * 0.9, 0.5 + p[b] / max(s[b], 0.01) * 0.9)
        nf.normal_update()
        if nf.normal.dot(nf.calc_center_median() - c) < 0: nf.normal_flip()   # gespiegelde rot (det -1) keert de vlakken om (UV gaat mee)
    t.free(); TRIS[0] += 48


class Lijn:
    """Polylijn van de muurvoorkant met per punt z0 (voet) en z1 (bovenkant), naar buiten gerichte normaal; s = booglengte."""
    def __init__(self, punten):          # punten: [(Vector xy, z0, z1, normaal Vector)]
        self.p = punten; self.s = [0.0]
        for i in range(1, len(punten)): self.s.append(self.s[-1] + (punten[i][0] - punten[i - 1][0]).length)
        self.L = self.s[-1]

    def op(self, s):
        s = min(max(s, 0), self.L)
        for i in range(1, len(self.s)):
            if s <= self.s[i] or i == len(self.s) - 1:
                f = (s - self.s[i - 1]) / max(self.s[i] - self.s[i - 1], 1e-6); a, b = self.p[i - 1], self.p[i]
                n = (a[3] * (1 - f) + b[3] * f).normalized(); tg = (b[0] - a[0]).normalized()
                return a[0] * (1 - f) + b[0] * f, a[1] * (1 - f) + b[1] * f, a[2] * (1 - f) + b[2] * f, n, tg


def muurvlak(naam, lijn, dikte=None, caps=True):
    """Horizontale lagen platte stenen over de hele voorkant; daarboven dekstenen (rafelige bovenrand)."""
    bm = bmesh.new(); uv = bm.loops.layers.uv.verify()
    zmin = min(p[1] for p in lijn.p); zmax = max(p[2] for p in lijn.p)
    z = zmin - 0.03
    while z < zmax:
        h = rnd.uniform(0.09, 0.17) if rnd.random() < 0.75 else rnd.uniform(0.17, 0.24)   # video 0:21: 8-9 lagen op ~1.3 m
        s = rnd.uniform(-0.3, 0.0)
        while s < lijn.L:
            kans = rnd.random()                      # maatmix uit de video: kleine vulstenen, gewone, lange dunne platen
            if kans < 0.2: w, fh = rnd.uniform(0.09, 0.16), rnd.uniform(0.6, 0.9)
            elif kans < 0.9: w, fh = rnd.uniform(0.16, 0.32), rnd.uniform(0.8, 1.0)
            else: w, fh = rnd.uniform(0.34, 0.5), rnd.uniform(0.55, 0.75)
            sc = s + w / 2
            if 0 <= sc <= lijn.L:
                p, z0, z1, n, tg = lijn.op(sc)
                hh = h * fh; onder = rnd.random() < 0.5
                zc = z + hh / 2 if onder else z + h - hh / 2
                plaats = [(sc, zc, w * rnd.uniform(0.95, 1.0), hh)]
                rest = h - hh - 0.008                      # vulstenen in de rest van de laag (video: kleine stenen tussen de platen)
                if rest > 0.04:
                    zf = z + h - rest / 2 if onder else z + rest / 2
                    nv = 1 if w < 0.3 else 2
                    for q in range(nv):
                        wf = w / nv - 0.01
                        plaats.append((s + wf / 2 + q * (wf + 0.01), zf, wf * rnd.uniform(0.85, 1.0), rest))
                for sx, zz, ww, hz in plaats:
                    p, z0, z1, n, tg = lijn.op(sx)
                    if zz + hz / 2 > z1 + 0.01:                # te hoog: inkrimpen tot onder de dekstenen (anders gat in de bovenste laag)
                        onderkant = zz - hz / 2; hz = z1 + 0.01 - onderkant; zz = onderkant + hz / 2
                    if hz > 0.04 and zz - hz / 2 > z0 - 0.08:
                        d = rnd.uniform(0.1, 0.16); pr = rnd.uniform(0.0, 0.045)
                        rot = Matrix.Rotation(rnd.uniform(-0.1, 0.1), 3, n) @ Matrix.Rotation(rnd.uniform(-0.08, 0.08), 3, Vector((0, 0, 1)))
                        muursteen(bm, uv, Vector((p.x, p.y, zz)) + n * (pr - d / 2), rot @ tg, rot @ n, ww, hz, d)
            s += w + rnd.uniform(0.004, 0.014)
        z += h + rnd.uniform(0.004, 0.012)
    if caps and dikte:
        s = 0.0
        while s < lijn.L:
            w = rnd.uniform(0.16, 0.42); sc = min(s + w / 2, lijn.L)
            p, z0, z1, n, tg = lijn.op(sc)
            h = rnd.uniform(0.06, 0.15)
            c = Vector((p.x, p.y, z1 + h * 0.35 + rnd.uniform(-0.015, 0.02))) - n * (dikte / 2 - 0.03)
            rot = Matrix((tg, n, Vector((0, 0, 1)))).transposed() @ Matrix.Rotation(rnd.uniform(-0.25, 0.25), 3, "Z") @ Matrix.Rotation(rnd.uniform(-0.12, 0.12), 3, "Y")
            blok(bm, uv, c, (w, dikte * rnd.uniform(0.9, 1.15), h), rot, afrond=0.25)
            s += w * rnd.uniform(0.72, 0.88)
    o = NS["obj"](naam, bm, "steen"); o["uv_vast"] = True
    return o


def boog_lijn(r, a0, a1, z0, z1, buiten=True, stap=0.15):
    n = max(2, int(abs(math.radians(a1 - a0)) * r / stap))
    out = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n; p = pt(r, a); rr = math.radians(a)
        nr = Vector((math.cos(rr), math.sin(rr), 0)) * (1 if buiten else -1)
        out.append((Vector((p.x, p.y, 0)), z0, z1, nr))
    return Lijn(out)


def rotsrij(naam, punten, z, maat=(0.25, 0.5)):
    """Rij rotsblokken langs een lijn (punten Vector), half in de grond."""
    bm = bmesh.new(); uv = bm.loops.layers.uv.verify()
    lijn = Lijn([(Vector((p.x, p.y, 0)), z, z, Vector((0, 0, 1))) for p in punten])
    s = 0.0
    while s < lijn.L:
        L = rnd.uniform(*maat); p, _, _, _, tg = lijn.op(s + L / 2)
        B = L * rnd.uniform(0.6, 0.9); H = L * rnd.uniform(0.5, 0.8)
        rot = Matrix.Rotation(math.atan2(tg.y, tg.x) + rnd.uniform(-0.4, 0.4), 3, "Z") @ Matrix.Rotation(rnd.uniform(-0.15, 0.15), 3, "X")
        if not botst(p, L): blok(bm, uv, Vector((p.x, p.y, z + H * 0.25)), (L, B, H), rot, afrond=0.3, bodem=-H * 0.3)
        s += L * rnd.uniform(0.7, 0.9)
    o = NS["obj"](naam, bm, "steen"); o["uv_vast"] = True
    return o


def build():
    a = sys.argv[sys.argv.index("--") + 1:]
    m = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=m)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    # oude lowpoly rotsblokken van 12 weg; gladde muren worden donkere achterwand
    for o in [o for o in bpy.data.objects if o.get("owner") == "phase:12_omgeving"]:
        if o.name.startswith(("AR_Pagode_O_rand_", "AR_Pagode_O_muursteen_")):
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.get("rol") == "breuksteen":
            o["rol"] = "voeg"
    for o in [o for o in bpy.data.objects if o.get("owner") == "phase:14_planten" and o.name.startswith("AR_Pagode_P_tuinsteen")]:
        bpy.data.objects.remove(o, do_unlink=True)          # gladde blobs -> rotsblokken hieronder

    # 1 keermuur langs het plein (voorkant r 14.15, 54 graden tot de kop van het laantje), dikte 0.4
    a_eind = aW(14.5)
    muurvlak("AR_Pagode_S_pleinmuur", boog_lijn(R_BO + 0.15, 54.0, a_eind, Z_P, Z_I + 0.25), dikte=0.4)
    # 1b plantvak voor de pleinmuur (video 0:05): lage stenen voormuur ~0.5 m, 0.9 m ervoor; bovenop aarde met rotsjes
    muurvlak("AR_Pagode_S_pleinvoor", boog_lijn(R_BO + 1.05, 56.0, 96.0, Z_P, Z_P + 0.5), dikte=0.3)
    ringsector("AR_Pagode_S_plantvak", R_BO + 0.15, R_BO + 0.95, Z_P - 0.4, Z_P + 0.46, 56.0, 96.0, "aarde")
    bm = bmesh.new(); uv = bm.loops.layers.uv.verify()
    for j in range(26):
        aa = rnd.uniform(57, 95); L = rnd.uniform(0.25, 0.55)
        blok(bm, uv, pt(rnd.uniform(14.4, 14.95), aa, Z_P + 0.46 + L * 0.1), (L, L * 0.75, L * 0.55), Matrix.Rotation(rnd.uniform(0, 6.3), 3, "Z"), afrond=0.6, bodem=-L * 0.2)
    o = NS["obj"]("AR_Pagode_S_plantvak_rots", bm, "steen"); o["uv_vast"] = True

    # 2 laanmuur, kant van het laantje (hoek aR(r)), bovenkant schuin met de rijen; normaal naar het laantje
    st = [(R_BO, Z_I + 0.25)] + [(14.5 + t, ztop(t) + 0.3) for t in range(N_RIJ)] + [(25.0, ztop(N_RIJ - 1) + 0.3)]
    def ztop_r(r):
        for i in range(1, len(st)):
            if r <= st[i][0]: f = (r - st[i - 1][0]) / (st[i][0] - st[i - 1][0]); return st[i - 1][1] * (1 - f) + st[i][1] * f
        return st[-1][1]
    pts = []
    r = R_BO + 0.2
    while r <= 25.0:
        p = pt(r, aR(r)); ar = math.radians(aR(r))
        pts.append((Vector((p.x, p.y, 0)), Z_P, ztop_r(r), Vector((math.sin(ar), -math.cos(ar), 0))))
        r += 0.15
    muurvlak("AR_Pagode_S_laanmuur", Lijn(pts), dikte=0.42)
    # trapkant van de laanmuur (laag, ~0.3 m boven de rijen): alleen een laag stenen
    pts = []
    r = R_BO + 0.5
    while r <= 25.0:
        p = pt(r, aW(r)); ar = math.radians(aW(r)); t = min(N_RIJ - 1, max(0, int(r - 14.0)))
        pts.append((Vector((p.x, p.y, 0)), ztop(t), ztop_r(r), Vector((-math.sin(ar), math.cos(ar), 0))))
        r += 0.15
    muurvlak("AR_Pagode_S_laanmuur_trap", Lijn(pts), caps=False)
    # 3 uitgang: keermuur langs de vlonder (voorkant r 11.0), twee stukken naast de trap
    A_UIT = -20.0; gat = math.degrees(1.3 / 10.8)
    for k, (a0, a1) in enumerate(((-52.0, A_UIT - gat), (A_UIT + gat, 54.0))):
        muurvlak(f"AR_Pagode_S_oostmuur{k}", boog_lijn(11.0, a0, a1, Z_P + 0.03, Z_I + 0.12), dikte=0.38)
        rotsrij(f"AR_Pagode_S_oostvoet{k}", [pt(11.35, a0 + (a1 - a0) * i / 12) for i in range(13)], Z_P + 0.03, (0.3, 0.6))

    # 4 rotsblokken: tuinkant van het laantje (video 0:21-0:30) en buitenrand van het onderpad (0:24)
    rotsrij("AR_Pagode_S_laanrand", [pt(r, aL(r) - math.degrees(0.22 / r)) for r in [17.9 + 0.5 * i for i in range(16)]], Z_P, (0.28, 0.5))   # pas na het aanlooppad
    rotsrij("AR_Pagode_S_onderrand", [pt(27.0, aL(25.9) + (A_ZUID - aL(25.9)) * i / 30) for i in range(31)], Z_P, (0.28, 0.5))

    # rotsen in de tuin tussen laantje en bamboe (video 0:21-0:24), half in het gras
    bm = bmesh.new(); uv = bm.loops.layers.uv.verify()
    for j in range(14):
        r = rnd.uniform(18.2, 25.0); aa = aL(r) - math.degrees(rnd.uniform(0.8, 4.5) / r); L = rnd.uniform(0.35, 0.8)
        if botst(pt(r, aa), L): continue
        blok(bm, uv, pt(r, aa, Z_P + L * 0.1), (L, L * rnd.uniform(0.6, 0.9), L * rnd.uniform(0.45, 0.7)),
             Matrix.Rotation(rnd.uniform(0, 6.3), 3, "Z") @ Matrix.Rotation(rnd.uniform(-0.3, 0.3), 3, "X"), afrond=0.6, bodem=-L * 0.2)
    o = NS["obj"]("AR_Pagode_S_tuinrotsen", bm, "steen"); o["uv_vast"] = True

    # 5 natuurstenen neuzen op de tribunerijen (video 0:39): grijze band op de buitenrand van elke rij
    for t in range(N_RIJ):
        r1 = 15.0 + t; rm = r1 - 0.11
        ringsector(f"AR_Pagode_S_neus_{t:02d}", r1 - 0.2, r1 + 0.005, ztop(t) - 0.16, ztop(t) + 0.012, aW(rm) - 0.05, A_ZUID, "graniet")

    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=m)
    print("[17_steenwerk] %d objecten, ~%d driehoeken stenen" % (len([o for o in bpy.data.objects if o.get("owner") == OWNER]), TRIS[0]))


build()
