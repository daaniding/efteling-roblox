"""03_holle Vrouw Holle: het huisje (OSM 1109001371, 6.17 x 8.85 m + aanbouw oost) met steil rietdak dat over de gevels krult, wit stuc, bezoekersgevel (zuid,
naar de put): twee boogdeurtjes met stenen omlijsting en loerende gezichtjes, raam met bloembak, bovenin het luikenraam van Vrouw Holle, spoor van goud en pek
onder de deuren, voortuintje met laag bakstenen muurtje + smeedijzeren hekje + emmer met mattenklopper; noordgevel met grote dubbele boogdeur en rond
raampje; schoorsteen, haan op de nok; de put (OSM 55424650): bakstenen put met natuurstenen rand en stalen kijkrooster, fiks houten pannendak op twee zware
staanders met schoren, twee heksen-windvanen, groene projectorkist; grindpleinen (huis + rond pleintje bij de put), sprookjesboek.
Frame: oorsprong = zwaartepunt 1109001371 = studs (2.73, -90.69); model = OSM gedraaid met -6.8 graden; -Y = zuid (bezoekersgevel/put).
Gebruik: Blender -b -P 03_holle.py -- --master VH_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.84, 0.84, 0.78, 1), 0.9), "riet": ((0.42, 0.33, 0.24, 1), 0.95), "baksteen": ((0.5, 0.26, 0.18, 1), 0.85), "natuursteen": ((0.72, 0.66, 0.52, 1), 0.85),
        "groen": ((0.12, 0.3, 0.3, 1), 0.6), "glas": ((0.12, 0.14, 0.13, 1), 0.1), "donker": ((0.04, 0.035, 0.03, 1), 1.0), "hout": ((0.22, 0.16, 0.11, 1), 0.85),
        "dakhout": ((0.2, 0.18, 0.15, 1), 0.9), "ijzer": ((0.06, 0.06, 0.06, 1), 0.45), "goud": ((0.9, 0.7, 0.2, 1), 0.25), "pek": ((0.02, 0.02, 0.02, 1), 0.15),
        "rood": ((0.66, 0.12, 0.08, 1), 0.5), "papier": ((0.92, 0.86, 0.7, 1), 0.9), "grind": ((0.86, 0.83, 0.76, 1), 0.95), "modder": ((0.18, 0.13, 0.09, 1), 1.0),
        "haan": ((0.55, 0.25, 0.1, 1), 0.5)}
rr = random.Random(1952)
X0, X1, Y0, Y1 = -4.88, 1.29, -5.53, 3.32           # hoofdhuis (OSM)
XC = (X0 + X1) / 2
PUT = Vector((10.15, -20.4, 0))
PLEIN_HUIS = [(-10.7, -2.0), (-10.5, 4.9), (-6.0, 13.6), (0.9, 10.3), (4.1, 6.7), (7.1, 0.9), (7.2, -6.2), (5.3, -13.9), (-0.6, -12.3), (-4.6, -10.0), (-6.6, -8.8), (-9.2, -5.7)]
PLEIN_PUT = [(10.5 + 5.9 * math.cos(k * math.tau / 24), -19.1 + 5.9 * math.sin(k * math.tau / 24)) for k in range(24)]
STROOK = [(3.0, -12.2), (6.4, -12.6), (7.3, -15.6), (4.4, -16.6)]


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)

    def vlak(lussen, to3, depth, nrm):
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
    def boog(cu, v0, w, h, n=10):
        r = w / 2; vs = v0 + h - r
        return [(cu + r, v0)] + [(cu + r * math.cos(math.pi * k / n), vs + r * math.sin(math.pi * k / n)) for k in range(n + 1)] + [(cu - r, v0)]
    def rechth(u0, u1, v0, v1): return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    def cirkel(cu, cv, r, n=14): return [(cu + r * math.cos(k * math.tau / n), cv + r * math.sin(k * math.tau / n)) for k in range(n)]

    wand = bmesh.new()
    def addw(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); wand.from_mesh(me_); bpy.data.meshes.remove(me_)
    T = 0.4; ZE, ZN, OV = 1.95, 5.7, 0.9
    HD = (X1 - X0) / 2 + OV
    def dakz(x):                                         # onderkant riet boven x (dwars op de nok)
        t = max(0.0, min(1.0, 1 - abs(x - XC) / HD)); return (ZE - OV * 0.75) + (ZN - (ZE - OV * 0.75)) * t ** 0.92 + 0.1 * math.sin(math.pi * t)
    def gevel_top(xa, xb, n=12):
        return [(xa + (xb - xa) * k / n, dakz(xa + (xb - xa) * k / n) - 0.12) for k in range(n + 1)]
    # zuidgevel (bezoekers): 2 boogdeurtjes, raam met bloembak, luikenraam boven
    DL, DR, DW, DH = -3.35, -0.35, 0.85, 1.95
    zuid = [[(X1, -0.1)] + gevel_top(X1, X0) + [(X0, -0.1)]][0]
    addw(vlak([zuid[::-1], boog(DL, 0.0, DW, DH), boog(DR, 0.0, DW, DH), rechth(XC - 0.45, XC + 0.45, 0.95, 1.75), rechth(XC - 0.38, XC + 0.38, 3.2, 4.05)],
              lambda u, v: (u, Y0, v), T, (0, 1, 0)))
    # noordgevel: dubbele boogdeur, rond raampje, twee kleine ramen
    noord = [(X0, -0.1), (X1, -0.1)] + gevel_top(X1, X0)
    addw(vlak([noord, boog(XC, 0.0, 1.7, 2.35), cirkel(XC, 3.8, 0.27), rechth(X0 + 0.7, X0 + 1.25, 0.9, 1.5), rechth(X1 - 1.25, X1 - 0.7, 0.9, 1.5)],
              lambda u, v: (u, Y1 - T, v), T, (0, 1, 0)))
    # langsgevels
    addw(vlak([rechth(Y0, Y1, -0.1, ZE), rechth(-3.6, -3.0, 0.9, 1.55), rechth(-0.6, 0.0, 0.9, 1.55), rechth(1.8, 2.4, 0.9, 1.55)], lambda u, v: (X0, u, v), T, (1, 0, 0)))
    addw(vlak([rechth(Y0, Y1, -0.1, ZE), rechth(-3.9, -3.3, 0.9, 1.55)], lambda u, v: (X1 - T, u, v), T, (1, 0, 0)))
    # aanbouw oost (OSM 1.29..2.30, iets ruimer)
    AX1, AY0, AY1 = 2.7, -0.75, 2.95
    addw(bz(X1 - 0.1, AX1, AY0, AY0 + T, -0.1, 1.95)); addw(bz(X1 - 0.1, AX1, AY1 - T, AY1, -0.1, 1.95))
    addw(vlak([rechth(AY0, AY1, -0.1, 1.95), rechth(0.5, 1.2, 0.85, 1.45)], lambda u, v: (AX1 - T, u, v), T, (1, 0, 0)))
    for cx_, cy_ in ((X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1)):                                  # bolle hoeksteunen (Boekloc)
        hb = bz(cx_ - 0.45, cx_ + 0.45, cy_ - 0.45, cy_ + 0.45, -0.1, ZE + 0.1)
        for v in hb.verts:
            if v.co.z > 1.0: v.co.x = cx_ + (v.co.x - cx_) * 0.45; v.co.y = cy_ + (v.co.y - cy_) * 0.45
        addw(hb)
    put("muur", "stuc", organisch(wand, 0.05, 2, 0.45, 0.025, 1.3, 0.2))
    coll_box(XC, (Y0 + Y1) / 2, 1.5, X1 - X0, Y1 - Y0, 3.0); coll_box((X1 + AX1) / 2, (AY0 + AY1) / 2, 1.0, AX1 - X1, AY1 - AY0, 2.0)
    # ---------- rietdak: steil, krult over de gevels, rietrol langs de windveren ----------
    def rietdak(ya, yb, xa, xb, ze, zn, ov, golf, uit):
        xm = (xa + xb) / 2; hd = (xb - xa) / 2 + ov; NU, NV = 26, 9
        bm = bmesh.new()
        for s in (-1, 1):
            g = []
            for j in range(NV + 1):
                t = j / NV; row = []
                for i in range(NU + 1):
                    y = ya - uit + (yb - ya + 2 * uit) * i / NU
                    e = abs((y - (ya + yb) / 2) / ((yb - ya) / 2 + uit))
                    x = xm + s * hd * (1 - t); z = (ze - ov * 0.75) + (zn + golf * math.sin(i * 0.7) * t - (ze - ov * 0.75)) * (t ** 0.92) + 0.1 * math.sin(math.pi * t)
                    z -= 0.35 * max(0.0, e - 0.85) / 0.15 * (1 - t)          # rietrand buigt omlaag over de gevels
                    row.append(bm.verts.new((x, y, z + 0.06)))
                g.append(row)
            for j in range(NV):
                for i in range(NU): bm.faces.new((g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]))
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f in bm.faces:
            if f.normal.z < 0: f.normal_flip()
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.35)
        put("dak", "riet", bm)
        for yy in (ya - uit, yb + uit):                                  # rietrol langs beide windveren
            P = [Vector((xm + s * hd * (1 - j / 10), yy, (ze - ov * 0.75) + (zn - (ze - ov * 0.75)) * ((j / 10) ** 0.92) + 0.1 * math.sin(math.pi * j / 10) - 0.15)) for s in (-1, 1) for j in (range(11) if s < 0 else range(10, -1, -1))]
            put("dak", "riet", btube(P, 0.24, 8))
        put("dak", "riet", btube([Vector((xm, ya - uit, zn + 0.32)), Vector((xm, yb + uit, zn + 0.32))], 0.26, 10))      # nokrol
    rietdak(Y0, Y1, X0, X1, ZE, ZN, OV, 0.04, 0.35)
    # aanbouw: klein dwarsdakje van riet (nok oost-west), loopt in het grote dak
    yc_ = (AY0 + AY1) / 2; hw = (AY1 - AY0) / 2 + 0.5
    lb = bmesh.new()
    for s_ in (-1, 1):
        q = [(X1 - 1.2, yc_ + s_ * hw, 1.55), (AX1 + 0.45, yc_ + s_ * hw, 1.55), (AX1 + 0.45, yc_, 3.25), (X1 - 1.2, yc_, 3.25)]
        A = [lb.verts.new(p) for p in q]; B = [lb.verts.new((p[0], p[1], p[2] + 0.3)) for p in q]
        lb.faces.new(A); lb.faces.new(B[::-1])
        for i in range(4): lb.faces.new((A[i], A[(i + 1) % 4], B[(i + 1) % 4], B[i]))
    bmesh.ops.recalc_face_normals(lb, faces=lb.faces); put("dak", "riet", lb)
    put("dak", "riet", btube([(X1 - 1.2, yc_, 3.55), (AX1 + 0.45, yc_, 3.55)], 0.2, 8))
    put("muur2", "stuc", vlak([[(AY0, 1.9), (AY1, 1.9), (yc_, 3.15)]], lambda u, v: (AX1 - 0.3, u, v), 0.3, (1, 0, 0)))
    # schoorsteen + haan op de nok
    put("schoorsteen", "stuc", organisch(bz(-2.2, -1.5, 0.9, 1.6, 4.2, 6.5, 0.06), 0.035, 2, 0.4, 0.015, 1.5, 0.5))
    put("schoorsteen", "stuc", bz(-2.3, -1.4, 0.8, 1.7, 6.45, 6.6, 0.03))
    H = Vector((XC, Y0 - 0.15, ZN + 0.62))
    put("haan", "haan", ell(H, (0.12, 0.22, 0.14), 8, 6)); put("haan", "rood", ell(H + Vector((0, -0.2, 0.14)), (0.05, 0.06, 0.07), 6, 4))
    put("haan", "haan", ell(H + Vector((0, -0.2, 0.1)), (0.06, 0.08, 0.09), 8, 6)); put("haan", "donker", boutline([(0, 0), (0.1, 0.32), (-0.05, 0.36), (-0.12, 0.1)], -0.02, 0.04), Matrix.Translation(H + Vector((0, 0.2, 0))) @ Matrix.Rotation(math.pi / 2, 4, "Z"))
    put("haan", "ijzer", btube([H - Vector((0, 0, 0.45)), H - Vector((0, 0, 0.1))], 0.02, 5))
    # ---------- zuidgevel: deuren, stenen omlijsting met gezichtjes, raam met bloembak, luikenraam ----------
    for cx in (DL, DR):
        put("deuren", "groen", vlak([boog(cx, 0.0, DW - 0.02, DH - 0.01)], lambda u, v: (u, Y0 + 0.12, v), 0.06, (0, 1, 0)))
        for k in range(3): put("deuren", "ijzer", bz(cx - 0.3, cx + 0.3, Y0 + 0.08, Y0 + 0.11, 0.35 + k * 0.6, 0.39 + k * 0.6))
        r_ = DW / 2 + 0.16; zs = DH - DW / 2
        for k in range(9):                                                                        # natuursteen boogstenen
            a = math.pi * k / 8; p = Vector((cx + r_ * math.cos(a), Y0 - 0.06, zs + r_ * math.sin(a)))
            st = ell(p, (0.16, 0.08, 0.13), 8, 6) if k not in (0, 4, 8) else ell(p, (0.2, 0.1, 0.18), 10, 8)
            put("omlijsting", "natuursteen", st)
            if k in (0, 4, 8):                                                                    # loerend gezichtje (VrouwHollestenen)
                for s_ in (-1, 1): put("omlijsting", "donker", ell(p + Vector((s_ * 0.065, -0.09, 0.04)), (0.03, 0.02, 0.018), 6, 4))
                put("omlijsting", "donker", bz(p.x - 0.07, p.x + 0.07, p.y - 0.1, p.y - 0.08, p.z - 0.08, p.z - 0.06))
                put("omlijsting", "natuursteen", ell(p + Vector((0, -0.1, -0.01)), (0.03, 0.03, 0.045), 6, 4))
    for cx, mat in ((DL, "goud"), (DR, "pek")):                                                   # spoor van goud (Rita) en pek (Mina)
        sp = bmesh.new()
        for k in range(6): sp_ = ell((cx + rr.uniform(-0.25, 0.25), Y0 - 0.25 - k * 0.22, 0.02), (rr.uniform(0.12, 0.22), rr.uniform(0.1, 0.18), 0.025), 8, 4); put("spoor", mat, sp_)
        put("spoor", mat, bz(cx - 0.28, cx + 0.28, Y0 + 0.05, Y0 + 0.14, 0.0, 0.05))
    put("ramen", "glas", bz(XC - 0.45, XC + 0.45, Y0 + 0.16, Y0 + 0.18, 0.95, 1.75))
    for k in (1, 2): put("ramen", "groen", bz(XC - 0.45 + 0.3 * k - 0.02, XC - 0.45 + 0.3 * k + 0.02, Y0 + 0.12, Y0 + 0.16, 0.95, 1.75))
    put("ramen", "groen", bz(XC - 0.45, XC + 0.45, Y0 + 0.12, Y0 + 0.16, 1.33, 1.37))
    put("ramen", "groen", bz(XC - 0.55, XC + 0.55, Y0 - 0.12, Y0 + 0.05, 0.86, 0.95)); put("ramen", "groen", bz(XC - 0.5, XC + 0.5, Y0 - 0.32, Y0 - 0.05, 0.62, 0.86))   # bloembak
    put("ramen", "groen", bz(XC - 0.6, XC + 0.6, Y0 - 0.08, Y0 + 0.05, 1.75, 1.85))
    put("ramen", "donker", bz(XC - 0.38, XC + 0.38, Y0 + 0.3, Y0 + 0.33, 3.2, 4.05))           # luikenraam: open, donker binnen
    for s_ in (-1, 1):                                                                            # open luiken
        put("ramen", "groen", bz(min(0, s_ * 0.38), max(0, s_ * 0.38), -0.03, 0.03, 3.2, 4.05), Matrix.Translation((XC + s_ * 0.38, Y0 - 0.02, 0)) @ Matrix.Rotation(math.radians(-s_ * 60), 4, "Z"))
    put("ramen", "groen", bz(XC - 0.5, XC + 0.5, Y0 - 0.15, Y0 + 0.05, 3.1, 3.2))
    # noordgevel: dubbele deur, rond raampje, ramen
    put("deuren", "groen", vlak([boog(XC, 0.0, 1.68, 2.34)], lambda u, v: (u, Y1 - 0.12, v), 0.06, (0, 1, 0)))
    put("deuren", "donker", bz(XC - 0.015, XC + 0.015, Y1 - 0.07, Y1 - 0.05, 0.0, 2.3))
    for k in range(13):
        a = math.pi * k / 12; r_ = 1.0; p = Vector((XC + r_ * math.cos(a), Y1 + 0.05, 2.35 - 0.85 + r_ * math.sin(a)))
        put("omlijsting", "natuursteen", ell(p, (0.17, 0.08, 0.14), 8, 6))
    put("ramen", "glas", vlak([cirkel(XC, 3.8, 0.27)], lambda u, v: (u, Y1 - 0.18, v), 0.02, (0, 1, 0)))
    for xx in (X0 + 0.97, X1 - 0.97): put("ramen", "glas", bz(xx - 0.27, xx + 0.27, Y1 - 0.2, Y1 - 0.18, 0.9, 1.5))
    for (yy) in (-3.3, -0.3, 2.1): put("ramen", "glas", bz(X0 + 0.16, X0 + 0.18, yy - 0.3, yy + 0.3, 0.9, 1.55))
    put("ramen", "glas", bz(X1 - 0.2, X1 - 0.18, -3.9, -3.3, 0.9, 1.55)); put("ramen", "glas", bz(AX1 - 0.2, AX1 - 0.18, -0.25 + 0.5, -0.25 + 1.2, 0.85, 1.45))
    # ---------- voortuintje: laag bakstenen muurtje, smeedijzeren hekje, poortje, emmer met mattenklopper ----------
    tuin = [(X0 - 0.2, Y0), (X0 - 0.6, -8.7), (-2.35, -9.0), None, (-1.25, -9.0), (X1 + 0.9, -8.75), (X1 + 0.9, Y0 + 0.4)]
    seg = [[tuin[0], tuin[1], tuin[2]], [tuin[4], tuin[5], tuin[6]]]
    for s_ in seg:
        for a, b in zip(s_, s_[1:]):
            A, B = Vector(a), Vector(b); L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x)
            M_ = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
            put("tuin", "baksteen", bz(-0.15, L_ + 0.15, -0.15, 0.15, -0.1, 0.32), M_); put("tuin", "baksteen", bz(-0.19, L_ + 0.19, -0.18, 0.18, 0.32, 0.38), M_)
            put("tuin", "ijzer", btube([(0, 0, 0.66), (L_, 0, 0.66)], 0.016, 5), M_)
            for k in range(int(L_ / 0.14)): put("tuin", "ijzer", btube([(0.07 + k * 0.14, 0, 0.38), (0.07 + k * 0.14, 0, 0.66)], 0.008, 4), M_)
            m = (A + B) / 2; coll_box(m.x, m.y, 0.4, L_, 0.35, 0.8, math.degrees(ang))
        for p in s_: put("tuin", "baksteen", bz(p[0] - 0.22, p[0] + 0.22, p[1] - 0.22, p[1] + 0.22, -0.1, 0.62))
    put("tuin", "ijzer", btube([(-2.3, -9.0, 0.1), (-2.3, -9.0, 0.66), (-1.3, -9.0, 0.66), (-1.3, -9.0, 0.1), (-2.3, -9.0, 0.1)], 0.015, 5))
    for k in range(6): put("tuin", "ijzer", btube([(-2.2 + k * 0.16, -9.0, 0.1), (-2.2 + k * 0.16, -9.0, 0.66)], 0.008, 4))
    put("tuin", "ijzer", blathe([(0.13, 0), (0.16, 0.3), (0, 0.3)], 10), TR(X1 + 0.6, -8.75, 0.38))
    put("tuin", "hout", btube([(X1 + 0.6, -8.75, 0.55), (X1 + 0.75, -8.8, 1.05)], 0.015, 4)); put("tuin", "hout", btube([(X1 + 0.75 + 0.12 * math.cos(a), -8.8, 1.16 + 0.12 * math.sin(a)) for a in [k * math.tau / 10 for k in range(11)]], 0.01, 4))
    bed = [(X0 - 0.4, Y0 - 0.1), (X0 - 0.75, -8.5), (X1 + 0.7, -8.55), (X1 + 0.7, Y0 - 0.1)]
    tr_ = tessellate_polygon([[Vector((x, y, 0)) for x, y in bed]]); bm = bmesh.new(); V_ = [bm.verts.new((x, y, 0.12)) for x, y in bed]
    for t in tr_: bm.faces.new([V_[i] for i in t])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("tuin", "modder", bm)
    # sprookjesboek
    MB = TR(3.0, -9.6, 0, 200)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.035, 6), MB)
    MBk = MB @ TR(0, 0, 0.9) @ Matrix.Rotation(math.radians(28), 4, "X")
    put("boek", "rood", bz(-0.42, 0.42, -0.28, 0.28, -0.04, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.26, 0.26, 0.0, 0.05, 0.01), MBk)
    coll_box(3.0, -9.6, 0.5, 0.6, 0.5, 1.0, 20)
    # ---------- de put (Holleput, Ontwerp_put_pieck) ----------
    MP = Matrix.Translation(PUT)
    put("put", "baksteen", blathe([(0.95, -0.1), (0.95, 0.72), (0.72, 0.72), (0.72, 0.2), (0, 0.2)], 20), MP)
    put("put", "natuursteen", blathe([(1.02, 0.7), (1.02, 0.84), (0.68, 0.84), (0.68, 0.7)], 20), MP)
    put("put", "glas", blathe([(0.7, 0.8), (0, 0.8)], 16), MP)
    put("put", "ijzer", btube([(0.69 * math.cos(a), 0.69 * math.sin(a), 0.86) for a in [k * math.tau / 20 for k in range(21)]], 0.025, 5), MP)
    put("put", "ijzer", btube([(0.38 * math.cos(a), 0.38 * math.sin(a), 0.86) for a in [k * math.tau / 16 for k in range(17)]], 0.02, 5), MP)
    for k in range(8): a = k * math.tau / 8; put("put", "ijzer", btube([(0, 0, 0.86), (0.69 * math.cos(a), 0.69 * math.sin(a), 0.86)], 0.018, 4), MP)
    coll_box(PUT.x, PUT.y, 0.5, 2.0, 2.0, 1.0)
    for s_ in (-1, 1):                                                                            # zware staanders met schoren
        px = s_ * 1.45
        put("put", "hout", bz(px - 0.13, px + 0.13, -0.13, 0.13, -0.1, 3.35), MP); coll_box(PUT.x + px, PUT.y, 1.5, 0.3, 0.3, 3.0)
        for sy in (-1, 1): put("put", "hout", btube([(px, 0, 2.0), (px, sy * 1.25, 2.55)], 0.06, 6), MP)
        put("put", "hout", btube([(px, 0, 2.3), (px - s_ * 0.8, 0, 3.3)], 0.06, 6), MP)
    put("put", "hout", bz(-2.25, 2.25, -0.1, 0.1, 3.3, 3.5), MP)                                  # nokbalk
    for sy in (-1, 1): put("put", "hout", bz(-2.25, 2.25, sy * 1.25 - 0.07, sy * 1.25 + 0.07, 2.5, 2.62), MP)
    db = bmesh.new()
    for s_ in (-1, 1):
        q = [(-2.5, s_ * 2.1, 2.2), (2.5, s_ * 2.1, 2.2), (2.5, 0, 3.62), (-2.5, 0, 3.62)]
        A = [db.verts.new(p) for p in q]; B = [db.verts.new((p[0], p[1], p[2] + 0.12)) for p in q]
        db.faces.new(A); db.faces.new(B[::-1])
        for i in range(4): db.faces.new((A[i], A[(i + 1) % 4], B[(i + 1) % 4], B[i]))
        for k in range(8):                                                                         # pannenrijen
            t = (k + 0.5) / 8; y = s_ * 2.1 * (1 - t); z = 2.2 + 1.42 * t + 0.14
            put("putdak", "dakhout", bz(-2.5, 2.5, y - 0.04, y + 0.04, z - 0.03, z + 0.03), MP)
    bmesh.ops.recalc_face_normals(db, faces=db.faces); put("putdak", "dakhout", db, MP)
    put("putdak", "dakhout", btube([(-2.55, 0, 3.75), (2.55, 0, 3.75)], 0.1, 6), MP)
    for s_ in (-1, 1):                                                                            # heksen-windvanen
        put("putdak", "ijzer", btube([(s_ * 2.2, 0, 3.8), (s_ * 2.2, 0, 4.5)], 0.015, 4), MP)
        put("putdak", "ijzer", boutline([(-0.3, 0.0), (0.35, 0.05), (0.15, 0.12), (0.05, 0.35), (-0.05, 0.12), (-0.35, 0.1)], -0.01, 0.02), MP @ TR(s_ * 2.2, 0, 4.4))
    put("put", "groen", bz(0.9, 2.1, -1.55, -0.95, -0.1, 0.9, 0.02), MP); coll_box(PUT.x + 1.5, PUT.y - 1.25, 0.5, 1.2, 0.6, 1.0)
    # ---------- grind ----------
    for poly, z, nm in ((PLEIN_HUIS, 0.06, "huis"), (PLEIN_PUT, 0.065, "put"), (STROOK, 0.07, "strook")):
        tris = tessellate_polygon([[Vector((x, y, 0)) for x, y in poly]])
        bm = bmesh.new(); Tt = [bm.verts.new((x, y, z)) for x, y in poly]; Bb = [bm.verts.new((x, y, z - 0.12)) for x, y in poly]
        for t in tris:
            f = bm.faces.new([Tt[i] for i in t]); f.normal_update()
            if f.normal.z < 0: f.normal_flip()
            g = bm.faces.new([Bb[i] for i in t]); g.normal_update()
            if g.normal.z > 0: g.normal_flip()
        for i in range(len(poly)):
            j = (i + 1) % len(poly); bm.faces.new((Tt[i], Bb[i], Bb[j], Tt[j]))
        put("plein", "grind", bm)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"VH_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": PLEIN_HUIS, "plein_put": PLEIN_PUT, "strook": STROOK}, open(os.path.join(out, "holle_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
