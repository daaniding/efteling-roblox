"""03_geitjes De Wolf en de Zeven Geitjes (1957, Anton Pieck): huisje op de OSM-plattegrond 55423662 (8.45 x 7.45 m, uitsparing NW) als twee rietgedekte
blokken met een overdekte doorgang ertussen (OSM-voetpad 397496612 loopt er oost-west doorheen), krullende stucgevels die boven het riet uitsteken,
breuksteen in het stucwerk, golvende nok met rode pannen, dakkapel, hoge schoorsteen, nis met wapenschild (knolraap) op de oostgevel, het bebaarde
gezicht op de NW-hoek (7GeitjesAvond / ext1976), gaanderij met groene zuiltjes in de uitsparing (kijkvenster + groene deur van de wolf: Dewolf),
achterdeur met spitse kap (Achterkant), achtertuin met put, puthaal, wagenwiel, vogelhuisje en waslijn (Voorstudie, achterkant-2009), afdakje van
moeder geit met lage stucmuur en plankenhek bij de aftakking van het bospaadje (Boekloc, Moeder-geit), sprookjesboek, grindplein.
Frame: oorsprong = zwaartepunt 55423662 = studs (300.3, -127.23); model = OSM gedraaid met +7.27 graden (gevels assen-recht); +Y = noord (hoofdpad),
-Y = zuid (achtertuin). Gebruik: Blender -b -P 03_geitjes.py -- --master GT_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.82, 0.82, 0.74, 1), 0.9), "breuksteen": ((0.45, 0.43, 0.4, 1), 0.9), "riet": ((0.42, 0.33, 0.24, 1), 0.95), "pannen": ((0.66, 0.3, 0.18, 1), 0.7),
        "groen": ((0.1, 0.24, 0.2, 1), 0.6), "venster": ((0.5, 0.32, 0.14, 1), 0.2), "glas": ((0.15, 0.17, 0.15, 1), 0.1), "hout": ((0.3, 0.22, 0.15, 1), 0.85),
        "rood": ((0.66, 0.12, 0.08, 1), 0.5), "ijzer": ((0.06, 0.06, 0.06, 1), 0.45), "papier": ((0.92, 0.86, 0.7, 1), 0.9), "grind": ((0.86, 0.83, 0.76, 1), 0.95),
        "doek": ((0.85, 0.82, 0.72, 1), 0.9), "donker": ((0.04, 0.035, 0.03, 1), 1.0), "touw": ((0.55, 0.45, 0.3, 1), 0.9)}
rr = random.Random(1957)
SB = (-3.7, 4.76, -3.96, -0.35)          # zuidblok (woonkamer + slaapkamer)
NB = (-2.29, 4.76, 1.25, 3.48)           # noordblok (aan het hoofdpad)
PLEIN = [(-12.5, 3.0), (-7.6, -0.75), (-4.9, -0.75), (-4.9, -0.4), (5.4, -0.4), (5.4, -0.8), (7.2, -0.9), (11.3, 0.9), (12.2, 2.1), (8.8, 5.4), (2.0, 7.8), (-4.6, 7.7)]
PAD = [(18.28, -5.95), (11.59, 1.81), (8.52, 4.49), (1.93, 6.77), (-4.46, 6.65), (-11.96, 2.89), (-14.56, 1.37), (-17.58, -0.95), (-23.15, -5.4)]


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)

    def vlak(lussen, to3, depth, nrm):
        """polygoon met gaten (even-odd, tessellate_polygon) in een 2D-vlak, geextrudeerd langs nrm over depth"""
        flat = [p for l in lussen for p in l]
        tris = tessellate_polygon([[Vector((u, v, 0)) for u, v in l] for l in lussen])
        bm = bmesh.new(); A = [bm.verts.new(to3(u, v)) for u, v in flat]; B = [bm.verts.new(Vector(to3(u, v)) + Vector(nrm) * depth) for u, v in flat]
        for t in tris:
            try: bm.faces.new([A[i] for i in t]); bm.faces.new([B[i] for i in reversed(t)])
            except ValueError: pass
        o = 0
        for l in lussen:
            for i in range(len(l)):
                j = (i + 1) % len(l)
                try: bm.faces.new((A[o + i], A[o + j], B[o + j], B[o + i]))
                except ValueError: pass
            o += len(l)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm

    def boog(cu, v0, w, h, n=10):                         # gesloten rondboog-gat (u, v), tegen de klok in
        r = w / 2; vs = v0 + h - r
        return [(cu + r, v0)] + [(cu + r * math.cos(math.pi * k / n), vs + r * math.sin(math.pi * k / n)) for k in range(n + 1)] + [(cu - r, v0)]

    def rechth(u0, u1, v0, v1): return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]

    wand = bmesh.new()
    def addw(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); wand.from_mesh(me_); bpy.data.meshes.remove(me_)
    T = 0.35
    def gevel_y(y, x0, x1, ze, zt, gaten, rich):        # langsgevel in het XZ-vlak op y, dikte naar binnen (rich = +1/-1)
        addw(vlak([rechth(x0, x1, -0.1, ze)] + gaten, lambda u, v: (u, y, v), T, (0, rich, 0)))
    def gevel_x(x, y0, y1, ze, top, gaten, rich):       # kopgevel in het YZ-vlak op x met krullende top (top = [(y, z), ...] van y1 naar y0)
        addw(vlak([[(y0, -0.1), (y1, -0.1)] + top] + gaten, lambda u, v: (x, u, v), T, (rich, 0, 0)))
    def krultop(ya, yb, ze, zn, ov=0.45, flare=(True, True)):
        """Pieck-gevel boven het riet uit: volgt de daklijn + 0.5 m, uitlopende schouders bij de goot, kopje boven de nok. Punten van yb naar ya."""
        ym = (ya + yb) / 2; hd = (yb - ya) / 2 + ov
        def dakz(y):
            t = max(0.0, min(1.0, 1 - abs(y - ym) / hd)); return (ze - ov * 0.6) + (zn - (ze - ov * 0.6)) * t ** 0.9 + 0.12 * math.sin(math.pi * t)
        half = []
        for s_, yr, fl in ((1, yb, flare[1]), (-1, ya, flare[0])):
            pts = [(yr, ze - 0.35)]
            if fl: pts += [(yr + s_ * ov * 0.8, ze - 0.15), (yr + s_ * ov * 0.8, ze + 0.3), (yr + s_ * ov * 0.25, ze + 0.5)]
            for k in range(1, 9):
                y = yr - s_ * ((yb - ya) / 2 - 0.3) * k / 8
                pts.append((y, dakz(y) + 0.55 + 0.06 * math.sin(k * 1.7)))
            pts += [(ym + s_ * 0.3, zn + 1.0), (ym + s_ * 0.18, zn + 1.15)]
            half.append(pts)
        return half[0] + half[1][::-1]
    def nb(v): return v

    # ---------- zuidblok ----------
    x0, x1, y0, y1 = SB; ZE_S, ZN_S = 2.45, 5.9
    gevel_y(y0, x0, x1, ZE_S, None, [rechth(0.05, 1.05, 0.0, 2.05), rechth(1.95, 3.0, 0.85, 1.85), rechth(-2.7, -1.9, 0.9, 1.7)], +1)   # achter: deur + 2 ramen
    gevel_y(y1 - T, x0, x1, ZE_S, None, [rechth(-3.35, -2.55, 0.0, 2.0), boog(-0.4, 0.75, 1.1, 1.35), boog(1.6, 0.75, 1.1, 1.35), boog(3.45, 0.75, 1.0, 1.3)], +1)   # doorgang: wolfdeur + kijkramen
    gevel_x(x0, y0, y1, ZE_S, krultop(y0, y1, ZE_S, ZN_S, 0.5), [rechth(-2.5, -1.7, 1.0, 1.8)], +1)
    # ---------- noordblok ----------
    X0, X1, Y0, Y1 = NB; ZE_N, ZN_N = 2.35, 5.0
    gevel_y(Y0, X0, X1, ZE_N, None, [boog(0.6, 0.75, 1.0, 1.3), boog(2.6, 0.75, 1.0, 1.3)], +1)
    gevel_y(Y1 - T, X0, X1, ZE_N, None, [boog(-1.1, 0.6, 0.95, 1.45), boog(0.45, 0.6, 0.95, 1.45), boog(2.0, 0.6, 0.95, 1.45), boog(3.55, 0.6, 0.95, 1.45)], +1)  # hoofdpad: boogvensters
    gevel_x(X0, Y0, Y1, ZE_N, krultop(Y0, Y1, ZE_N, ZN_N, 0.45), [rechth(1.75, 3.0, 0.7, 1.9)], +1)        # kijkvenster aan de gaanderij
    # ---------- oostgevel over beide blokken + doorgang (boog) ----------
    oy0, oy1 = y0 - 0.12, Y1 + 0.12
    top = krultop(Y0, oy1, ZE_N, ZN_N, 0.45, (False, True))
    top_s = krultop(oy0, y1, ZE_S, ZN_S, 0.5, (True, False))
    omtrek = [(oy0, -0.1), (oy1, -0.1)] + top + [(Y0 - 0.05, 3.2), (y1 + 0.05, 3.2)] + top_s
    addw(vlak([omtrek, boog((y1 + Y0) / 2, -0.05, Y0 - y1 - 0.2, 2.45)], lambda u, v: (x1 - T, u, v), T + 0.12, (1, 0, 0)))
    # binnenkant doorgang: muurtjes die de daken dragen boven de doorgang + vloer
    put("muur", "stuc", organisch(wand, 0.05, 2, 0.4, 0.02, 1.4, 0.18))
    coll_box((x0 + x1) / 2, (y0 + y1) / 2, 1.5, x1 - x0, y1 - y0, 3.0); coll_box((X0 + X1) / 2, (Y0 + Y1) / 2, 1.5, X1 - X0, Y1 - Y0, 3.0)
    # breuksteen in het stucwerk (vooral onderaan en rond de hoeken: 7GeitjesAvond)
    def stenen(n, pts_fn):
        for _ in range(n):
            p, nrm, t = pts_fn(); s = rr.uniform(0.07, 0.15)
            st = bz(-s, s, -0.03, 0.025, -s * 0.6, s * 0.6, s * 0.3)
            for v in st.verts: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-0.4, 0.4), rr.uniform(-1, 1))) * s * 0.25
            put("stenen", "breuksteen", st, Matrix.Translation(p) @ Matrix.Rotation(math.atan2(nrm[0], -nrm[1]), 4, "Z") @ Matrix.Rotation(rr.uniform(-0.4, 0.4), 4, "Y"))
    def langs_y(y, xa, xb, s):
        def f():
            x = rr.uniform(xa, xb); z = min(rr.expovariate(2.4), 2.0)
            return Vector((x, y - s * 0.02, z)), (0, -s), 0
        return f
    def langs_x(x, ya, yb, s):
        def f():
            y = rr.uniform(ya, yb); z = min(rr.expovariate(2.4), 2.0)
            return Vector((x + s * 0.02, y, z)), (s, 0), 0
        return f
    stenen(45, langs_y(Y1, X0, X1, -1)); stenen(40, langs_y(y0, x0, x1, 1)); stenen(30, langs_x(x0, y0, y1, -1)); stenen(30, langs_x(x1 + 0.12, oy0, oy1, 1))
    stenen(25, langs_x(X0, Y0, Y1, -1)); stenen(18, langs_y(y1, x0, x1, -1))
    # ramen: groene kozijnen, glas met warm licht erachter
    def raam_y(cx, z0, w, h, y, s, boogje=True):
        put("ramen", "venster", bz(cx - w / 2, cx + w / 2, y + s * 0.15, y + s * 0.2, z0, z0 + h))
        put("ramen", "glas", bz(cx - w / 2, cx + w / 2, y + s * 0.1, y + s * 0.12, z0, z0 + h - (w / 2 if boogje else 0)))
        for k in range(1, 3): put("ramen", "groen", bz(cx - w / 2 + w * k / 3 - 0.025, cx - w / 2 + w * k / 3 + 0.025, y + s * 0.09, y + s * 0.13, z0, z0 + h - (w / 2 if boogje else 0)))
        put("ramen", "groen", bz(cx - w / 2, cx + w / 2, y + s * 0.09, y + s * 0.13, z0 + h * 0.45 - 0.025, z0 + h * 0.45 + 0.025))
    for cx in (-1.1, 0.45, 2.0, 3.55): raam_y(cx, 0.6, 0.95, 1.45, Y1, -1)
    for cx in (0.6, 2.6): raam_y(cx, 0.75, 1.0, 1.3, Y0, 1)
    for cx in (-0.4, 1.6, 3.45): raam_y(cx, 0.75, 1.05, 1.32, y1, -1)
    raam_y(2.47, 0.85, 1.05, 1.0, y0, 1, False); raam_y(-2.3, 0.9, 0.8, 0.8, y0, 1, False)
    put("ramen", "venster", bz(X0 + 0.15, X0 + 0.2, 1.75, 3.0, 0.7, 1.9)); put("ramen", "glas", bz(X0 - 0.12, X0 - 0.1, 1.75, 3.0, 0.7, 1.9))
    for k in range(1, 4): put("ramen", "groen", bz(X0 - 0.13, X0 - 0.09, 1.75 + 1.25 * k / 4 - 0.025, 1.75 + 1.25 * k / 4 + 0.025, 0.7, 1.9))
    for zz in (1.1, 1.5): put("ramen", "groen", bz(X0 - 0.13, X0 - 0.09, 1.75, 3.0, zz - 0.02, zz + 0.02))
    # deuren: wolfdeur (gaanderij), achterdeur met spitse kap
    put("deuren", "groen", bz(-3.35, -2.55, y1 - 0.08, y1 - 0.02, 0.0, 2.0)); put("deuren", "ijzer", ell((-2.65, y1 + 0.0, 1.0), (0.04, 0.04, 0.04), 6, 4))
    put("deuren", "groen", bz(0.05, 1.05, y0 - 0.02, y0 + 0.05, 0.0, 2.05))
    for s_ in (-1, 1): put("deuren", "groen", bz(0.55 + s_ * 0.62 - 0.07, 0.55 + s_ * 0.62 + 0.07, y0 - 0.12, y0, 0.0, 2.2))
    put("deuren", "groen", boutline([(-0.25, 2.1), (1.35, 2.1), (0.55, 3.25)], y0 - 0.32, 0.32))                                  # spitse kap
    # nis met wapenschild (knolraap) op de oostgevel + windvaan
    put("nis", "donker", bz(x1 + 0.13, x1 + 0.15, -2.45, -1.65, 3.25, 4.1)); put("nis", "rood", boutline([(-0.25, 0.35), (0.25, 0.35), (0.25, 0.0), (0, -0.25), (-0.25, 0.0)], 0, 0.05), Matrix.Translation((x1 + 0.2, -2.05, 3.45)) @ Matrix.Rotation(-math.pi / 2, 4, "Z"))
    put("nis", "doek", ell((x1 + 0.27, -2.05, 3.55), (0.04, 0.09, 0.12), 8, 6))
    # ---------- daken: riet met golvende nok en rode nokpannen ----------
    def rietdak(xa, xb, ya, yb, ze, zn, ov, golf, part="dak"):
        ym = (ya + yb) / 2; hd = (yb - ya) / 2 + ov; NU, NV = 28, 7
        bm = bmesh.new(); rows = []
        for s in (-1, 1):
            g = []
            for j in range(NV + 1):
                t = j / NV; row = []
                for i in range(NU + 1):
                    x = xa + 0.2 + (xb - xa - 0.4) * i / NU
                    wv = golf * math.sin((x - xa) / (xb - xa) * math.tau * 1.0 + 0.6)
                    y = ym + s * hd * (1 - t); z = (ze - ov * 0.6) + (zn + wv - (ze - ov * 0.6)) * (t ** 0.9) + 0.12 * math.sin(math.pi * t)
                    row.append(bm.verts.new((x, y, z)))
                g.append(row)
            for j in range(NV):
                for i in range(NU):
                    f = bm.faces.new((g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]))
            rows.append(g)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f in bm.faces:
            if f.normal.z < 0: f.normal_flip()
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.32)
        for v in bm.verts: v.co.z += rr.uniform(-0.015, 0.015)
        put(part, "riet", bm)
        nok = [Vector((xa + 0.2 + (xb - xa - 0.4) * i / NU, ym, zn + golf * math.sin((xa + 0.2 + (xb - xa - 0.4) * i / NU - xa) / (xb - xa) * math.tau + 0.6) + 0.3)) for i in range(NU + 1)]
        put(part, "pannen", btube(nok, 0.2, 8))
        for i in range(0, NU + 1, 1):
            p = nok[i]; put(part, "pannen", btube([p + Vector((0, -0.34, -0.12)), p + Vector((0, 0, 0.06)), p + Vector((0, 0.34, -0.12))], 0.075, 6))
    rietdak(x0 - 0.05, x1 + 0.05, y0, y1, ZE_S, ZN_S, 0.5, 0.18)
    rietdak(X0 - 0.05, X1 + 0.05, Y0, Y1, ZE_N, ZN_N, 0.45, 0.14)
    put("dak", "riet", bz(X0, x1, y1 - 0.05, Y0 + 0.05, 2.75, 3.0))                                                       # plat rietje boven de doorgang
    # dakkapel op het noorddak (ext1981 / Avond)
    dk = bz(2.15, 3.15, 2.3, 3.5, 2.2, 3.3, 0.06); put("dakkapel", "stuc", dk); raam_y(2.65, 2.45, 0.55, 0.6, 3.6, -1, False)
    put("dakkapel", "riet", boutline([(1.95, 3.2), (3.35, 3.2), (2.65, 3.9)], 2.1, 1.6))
    # schoorsteen (hoog, op de oostelijke kopgevel van het zuidblok)
    put("schoorsteen", "stuc", organisch(bz(4.2, 5.05, -2.5, -1.6, 4.8, 7.7, 0.08), 0.035, 2, 0.4, 0.015, 1.5, 0.5))
    put("schoorsteen", "stuc", bz(4.1, 5.15, -2.6, -1.5, 7.6, 7.8, 0.03))
    put("schoorsteen", "ijzer", btube([(4.62, -2.05, 7.8), (4.62, -2.05, 8.6)], 0.025, 5)); put("schoorsteen", "ijzer", boutline([(0, 0), (0.45, 0.05), (0.4, 0.22), (0, 0.18)], -0.01, 0.02), TR(4.62, -2.05, 8.3))
    # ---------- het bebaarde gezicht op de NW-hoek (Avond, ext1976) ----------
    gz = bmesh.new()
    def addg(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); gz.from_mesh(me_); bpy.data.meshes.remove(me_)
    C = Vector((X0 - 0.05, Y1 + 0.05, 0)); d = Vector((-0.707, 0.707, 0))                                                   # kijkt schuin naar het hoofdpad (NW)
    q = Vector((0.707, 0.707, 0))
    addg(bz(X0 - 0.6, X0 + 0.4, Y1 - 0.4, Y1 + 0.6, -0.1, 3.0, 0.2))                                                   # hoekpijler
    def P(u, h, v): return C + d * (u * 1.7 + 0.05) + q * h * 1.7 + Vector((0, 0, 0.35 + (v - 0.35) * 1.45))
    addg(ell(P(0.45, 0, 1.95), (0.5, 0.7, 0.3), 12, 8))                                                                    # voorhoofd
    for s_ in (-1, 1): addg(ell(P(0.55, s_ * 0.19, 1.75), (0.2, 0.29, 0.12), 10, 6))                                        # wenkbrauwen
    addg(ell(P(0.6, 0, 1.5), (0.22, 0.16, 0.38), 10, 8))                                                                     # neus
    for s_ in (-1, 1): addg(ell(P(0.52, s_ * 0.22, 1.42), (0.2, 0.22, 0.2), 10, 6))                                        # wangen
    for s_ in (-1, 1): addg(btube([P(0.58, s_ * 0.05, 1.28), P(0.6, s_ * 0.25, 1.22), P(0.55, s_ * 0.38, 1.05)], 0.05, 6))  # snor
    for k in range(9):                                                                                                       # lange baard in strengen
        h = -0.32 + 0.64 * k / 8; L_ = 1.0 - 0.5 * abs(h) / 0.32
        addg(btube([P(0.5, h, 1.2), P(0.55 - 0.05 * abs(h), h * 0.9, 0.85), P(0.5, h * 0.6 + 0.04 * math.sin(k), 1.2 - L_)], 0.11, 6))
    put("gezicht", "stuc", organisch(gz, 0.025, 3, 0.5, 0.01, 2.0, 0.22))
    for s_ in (-1, 1): put("gezicht", "donker", ell(P(0.56, s_ * 0.17, 1.62), (0.07, 0.1, 0.05), 6, 4))
    # ---------- gaanderij in de uitsparing: groene zuiltjes, afdakje, leuning ----------
    for yy in (-0.2, 1.55, 3.3):
        put("gaanderij", "groen", blathe([(0.09, 0), (0.09, 0.15), (0.06, 0.2), (0.06, 0.9), (0.08, 1.0), (0.05, 1.1), (0.05, 2.1), (0.09, 2.25), (0, 2.3)], 10), TR(-4.55, yy, 0))
    put("gaanderij", "groen", bz(-4.65, -4.45, -0.35, 3.45, 2.25, 2.4))
    put("gaanderij", "riet", boutline([(-4.95, 2.3), (-2.3, 3.05), (-2.3, 3.3), (-4.95, 2.55)], -0.5, 4.15))   # lessenaarsdakje (XZ, langs Y)
    put("gaanderij", "groen", btube([(-4.55, 1.55, 0.95), (-4.55, 3.3, 0.95)], 0.035, 6))
    for k in range(7): yy = 1.65 + k * 0.24; put("gaanderij", "groen", bz(-4.58, -4.52, yy - 0.025, yy + 0.025, 0, 0.95))
    coll_box(-4.55, 2.4, 0.5, 0.15, 1.9, 1.0)
    # ---------- achtertuin: put, puthaal, wagenwiel, vogelhuisje, waslijn (Voorstudie, achterkant-2009) ----------
    put("tuin", "breuksteen", organisch(blathe([(0.78, 0), (0.78, 0.72), (0.6, 0.72), (0.6, 0.1), (0, 0.1)], 18), 0.04, 1, 0.3, 0.03, 0.8, 0.5), TR(1.6, -8.2, 0))
    put("tuin", "donker", bz(-0.5, 0.5, -0.5, 0.5, 0.42, 0.45), TR(1.6, -8.2, 0, 45))
    coll_box(1.6, -8.2, 0.5, 1.6, 1.6, 1.0)
    put("tuin", "hout", btube([(3.7, -9.4, -0.2), (3.7, -9.4, 2.2), (3.55, -9.4, 2.65)], 0.11, 7)); put("tuin", "hout", btube([(3.7, -9.4, 2.2), (3.85, -9.4, 2.65)], 0.08, 6))
    pa, pb = Vector((6.3, -10.8, 0.9)), Vector((1.65, -8.25, 4.4)); put("tuin", "hout", btube([pa, pb], 0.06, 6))
    put("tuin", "touw", btube([pb, pb - Vector((0, 0, 3.0))], 0.012, 4)); put("tuin", "hout", blathe([(0.13, 0), (0.15, 0.28), (0, 0.28)], 10), TR(pb.x, pb.y, pb.z - 3.3))
    coll_box(3.7, -9.4, 1.2, 0.3, 0.3, 2.4)
    put("tuin", "hout", btube([(-0.8, -6.6, -0.2), (-0.8, -6.6, 0.95)], 0.07, 6))
    put("tuin", "rood", btube([(-0.8 + 0.55 * math.cos(a), -6.6 + 0.55 * math.sin(a), 1.0) for a in [k * math.tau / 20 for k in range(21)]], 0.04, 6))
    for k in range(8): a = k * math.tau / 8; put("tuin", "rood", btube([(-0.8, -6.6, 1.0), (-0.8 + 0.53 * math.cos(a), -6.6 + 0.53 * math.sin(a), 1.0)], 0.02, 4))
    put("tuin", "hout", btube([(6.2, -5.4, -0.2), (6.2, -5.4, 2.2)], 0.06, 6)); put("tuin", "hout", bz(5.98, 6.42, -5.62, -5.18, 2.2, 2.6))
    put("tuin", "riet", blathe([(0.36, 0), (0.0, 0.7)], 8), TR(6.2, -5.4, 2.58))
    for (px, py) in ((-3.2, -7.2), (-0.2, -10.0)): put("tuin", "hout", btube([(px, py, -0.2), (px, py, 1.9)], 0.05, 6))
    put("tuin", "touw", btube([(-3.2, -7.2, 1.85), (-1.7, -8.6, 1.72), (-0.2, -10.0, 1.85)], 0.008, 4))
    for k, t in enumerate((0.2, 0.42, 0.66)):
        p = Vector((-3.2, -7.2, 1.8)).lerp(Vector((-0.2, -10.0, 1.8)), t); ang = math.atan2(-2.8, 3.0)
        put("tuin", "doek", bz(-0.22, 0.22, -0.01, 0.01, -0.55, 0.0), Matrix.Translation(p) @ Matrix.Rotation(ang, 4, "Z"))
    # ---------- afdakje van moeder geit + lage stucmuur + plankenhek + boek (Boekloc, Moeder-geit) ----------
    MG = TR(13.3, -1.1, 0, -48)
    for sx in (-1, 1):
        for sy in (-1, 1): put("moedergeit", "hout", bz(sx * 1.05 - 0.07, sx * 1.05 + 0.07, sy * 0.75 - 0.07, sy * 0.75 + 0.07, 0, 2.1), MG)
    put("moedergeit", "hout", bz(-1.2, 1.2, -0.85, 0.85, 2.05, 2.15), MG)
    rb = bmesh.new()
    for s_ in (-1, 1):
        q4 = [(-1.55, s_ * 1.25, 1.95), (1.55, s_ * 1.25, 1.95), (1.55, 0, 3.0), (-1.55, 0, 3.0)]
        A = [rb.verts.new(p) for p in q4]; B = [rb.verts.new((p[0], p[1], p[2] + 0.3)) for p in q4]
        rb.faces.new(A); rb.faces.new(B[::-1])
        for i in range(4): rb.faces.new((A[i], A[(i + 1) % 4], B[(i + 1) % 4], B[i]))
    bmesh.ops.recalc_face_normals(rb, faces=rb.faces); put("moedergeit", "riet", rb, MG)
    put("moedergeit", "pannen", btube([(-1.6, 0, 3.32), (1.6, 0, 3.32)], 0.18, 8), MG)
    for i in range(11): x = -1.5 + 0.3 * i; put("moedergeit", "pannen", btube([(x, -0.3, 3.2), (x, 0, 3.4), (x, 0.3, 3.2)], 0.07, 6), MG)
    put("moedergeit", "stuc", organisch(merge(*[bz(-2.6 + 1.05 * k, -1.5 + 1.05 * k, 1.1 + 0.25 * math.sin(k), 1.45 + 0.25 * math.sin(k), -0.1, 0.62) for k in range(5)]), 0.04, 2, 0.4, 0.02, 1.2, 0.5), MG)
    coll_box(13.3, -1.1, 0.5, 2.4, 1.8, 1.0, -48)
    hek = [(9.4, 2.4), (11.6, 0.1), (13.6, -2.7), (15.6, -5.3), (17.2, -7.4)]
    for a, b in zip(hek, hek[1:]):
        A, B = Vector(a), Vector(b); L_ = (B - A).length; n = int(L_ / 0.24); ang = math.degrees(math.atan2(B.y - A.y, B.x - A.x))
        for i in range(n):
            p = A.lerp(B, (i + 0.5) / n); h = rr.uniform(0.55, 0.75)
            put("hek", "hout", bz(-0.11, 0.11, -0.025, 0.025, -0.1, h), TR(p.x, p.y, 0, ang + rr.uniform(-3, 3)))
        put("hek", "hout", bz(0, L_, -0.05, 0.0, 0.3, 0.42), TR(A.x, A.y, 0, ang) @ TR(0, 0.06, 0))
        m = (A + B) / 2; coll_box(m.x, m.y, 0.5, L_, 0.15, 1.0, ang)
    MB = TR(14.9, -3.1, 0, 132)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.035, 6), MB)
    MBk = MB @ TR(0, 0, 0.9) @ Matrix.Rotation(math.radians(28), 4, "X")
    put("boek", "rood", bz(-0.42, 0.42, -0.28, 0.28, -0.04, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.26, 0.26, 0.0, 0.05, 0.01), MBk)
    # ---------- plein (licht grind) ----------
    tris = tessellate_polygon([[Vector((x, y, 0)) for x, y in PLEIN]])
    bm = bmesh.new(); Tt = [bm.verts.new((x, y, 0.06)) for x, y in PLEIN]; Bb = [bm.verts.new((x, y, -0.06)) for x, y in PLEIN]
    for t in tris:
        f = bm.faces.new([Tt[i] for i in t]); f.normal_update()
        if f.normal.z < 0: f.normal_flip()
        g = bm.faces.new([Bb[i] for i in t]); g.normal_update()
        if g.normal.z > 0: g.normal_flip()
    for i in range(len(PLEIN)):
        j = (i + 1) % len(PLEIN); bm.faces.new((Tt[i], Bb[i], Bb[j], Tt[j]))
    put("plein", "grind", bm)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"GT_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": PLEIN}, open(os.path.join(out, "geitjes_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
