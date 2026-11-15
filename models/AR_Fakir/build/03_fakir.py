"""03_fakir De Vliegende Fakir (1965, Peter Reijnders / Anton Pieck): paleis naar Perzische miniaturen (OSM 50911617): lage gaanderij met vijf gekartelde
ezelsrugbogen voor een witte wand met motiefjes, laag rood dak, hoge witte kantelenmuur erachter (32 kantelen), twee vierkante torens met brede rode luifels
op consoles, bovenverdieping met ezelsrugraam en de rafel-arm (tapijtsteun), achtkantige trommel met boogjes, uikoepel met gouden spits (Fakirpaleis,
Intro_fakir, Fakirvliegt, Fakir_1981); voortuin: middenvijver (184688429) met gouden fonteinvaas, L-vormig water om de torens (184688431/432), tulpenranden
(556546221/222), geplaveide binnentuin, grasrand (55441538), lange waterbak (184688428) als afstand, oosterse hekjes, plein (55350040, licht grind).
Frame: oorsprong = zwaartepunt 50911617 = studs (240.66, -638.46); model = OSM -7.3 graden; -Y = zuid (plein), +Y = noord. Figuren/vliegend tapijt later.
Gebruik: Blender -b -P 03_fakir.py -- --master FK_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.92, 0.9, 0.84, 1), 0.85), "pannen": ((0.62, 0.26, 0.2, 1), 0.7), "goud": ((0.88, 0.66, 0.22, 1), 0.3), "water": ((0.35, 0.6, 0.75, 1), 0.1),
        "bassin": ((0.45, 0.7, 0.85, 1), 0.5), "rood": ((0.66, 0.14, 0.1, 1), 0.5), "groen": ((0.15, 0.4, 0.3, 1), 0.6), "donker": ((0.08, 0.07, 0.07, 1), 0.9),
        "gras": ((0.2, 0.42, 0.12, 1), 1.0), "grind": ((0.86, 0.83, 0.76, 1), 0.95), "modder": ((0.16, 0.12, 0.08, 1), 1.0), "papier": ((0.92, 0.86, 0.7, 1), 0.9),
        "ijzer": ((0.06, 0.06, 0.06, 1), 0.45), "rand": ((0.7, 0.68, 0.62, 1), 0.85)}
rr = random.Random(1965)
GX0, GX1 = -8.21, 7.6
TW = (-12.42, -8.3, -3.32, 0.5); TO = (8.65, 12.49, -3.03, 0.98)
VIJVER = [(-4.55, -3.74), (3.57, -3.55), (3.7, -9.19), (-4.42, -9.37)]
WATER_W = [(-12.85, -7.26), (-12.1, -7.86), (-8.94, -7.85), (-7.83, -7.06), (-7.89, -0.07), (-8.35, -0.08), (-8.3, -3.29), (-12.4, -3.35), (-12.45, 0.48), (-12.97, 0.47)]
WATER_O = [(8.12, -6.87), (8.2, -0.11), (8.65, -0.12), (8.65, -3.02), (12.48, -3.04), (12.5, 0.96), (13.03, 0.96), (13.04, -7.09), (12.68, -7.61), (8.65, -7.44)]
BAK = [(-10.87, -15.17), (-10.81, -17.88), (11.76, -17.36), (11.69, -14.67)]
BINNEN = [(-13.27, -11.63), (13.64, -11.28), (13.46, 0.95), (7.6, 1.0), (7.6, 0.0), (-8.21, 0.0), (-8.21, 0.5), (-13.44, 0.46)]
GRAS = [(-15.61, 1.6), (-15.6, -18.4), (16.5, -18.4), (16.3, 1.6)]
PLEIN = [(-10.14, -33.85), (-10.55, -30.95), (-16.15, -26.9), (-15.6, -18.4), (16.5, -18.4), (13.31, -27.18), (13.71, -29.46), (-9.19, -35.97)]


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    def plaat(poly, z, dz, part, mat, gaten=()):
        lus = [poly] + list(gaten); flat = [p for l in lus for p in l]
        tris = tessellate_polygon([[Vector((x, y, 0)) for x, y in l] for l in lus])
        bm = bmesh.new(); Tt = [bm.verts.new((x, y, z)) for x, y in flat]; Bb = [bm.verts.new((x, y, z - dz)) for x, y in flat]
        for t in tris:
            f = bm.faces.new([Tt[i] for i in t]); f.normal_update()
            if f.normal.z < 0: f.normal_flip()
            g = bm.faces.new([Bb[i] for i in t]); g.normal_update()
            if g.normal.z > 0: g.normal_flip()
        o = 0
        for l in lus:
            for i in range(len(l)):
                j = (i + 1) % len(l)
                try: bm.faces.new((Tt[o + i], Bb[o + i], Bb[o + j], Tt[o + j]))
                except ValueError: pass
            o += len(l)
        put(part, mat, bm)
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
    def ezelsrug(cu, v0, w, h, n=8):                   # gekartelde ezelsrugboog (gat), punt bovenaan
        r = w / 2; vs = v0 + h - w * 0.75
        pts = [(cu + r, v0), (cu + r, vs)]
        for k in range(1, n + 1):                      # rechterhelft: holle boog naar de punt, met kleine kartels
            t = k / n; ang = math.pi * 0.5 * t
            x = cu + r * math.cos(ang) * (1 - 0.15 * t); z = vs + w * 0.55 * math.sin(ang) + (0.08 if k % 2 else 0)
            pts.append((x, z))
        pts.append((cu, v0 + h))
        left = [(2 * cu - x, z) for x, z in reversed(pts[1:-1])]
        return pts + left + [(cu - r, v0)]
    def dakschild(cx, cy, wx, wy, z0, z1, ov, part="dak", kind=0.0):   # laag schilddak (rood) met overstek
        bm = bmesh.new(); x0, x1, y0, y1 = cx - wx / 2 - ov, cx + wx / 2 + ov, cy - wy / 2 - ov, cy + wy / 2 + ov
        r = min(wx, wy) / 2 + ov; nx0, nx1 = cx - max(0.0, (wx - wy) / 2), cx + max(0.0, (wx - wy) / 2); ny0, ny1 = cy - max(0.0, (wy - wx) / 2), cy + max(0.0, (wy - wx) / 2)
        lo = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0))]
        hi = [bm.verts.new(p) for p in ((nx0, ny0, z1), (nx1, ny0, z1), (nx1, ny1, z1), (nx0, ny1, z1))]
        for i in range(4):
            j = (i + 1) % 4
            try: bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
            except ValueError: bm.faces.new((lo[i], lo[j], hi[i]))
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f in bm.faces:
            if f.normal.z < 0: f.normal_flip()
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.12); put(part, "pannen", bm)
        for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            put(part, "goud", btube([(a[0], a[1], z0 - 0.02), (b[0], b[1], z0 - 0.02)], 0.03, 5))
    wand = bmesh.new()
    def addw(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); wand.from_mesh(me_); bpy.data.meshes.remove(me_)
    # ---------- gaanderij: voorgevel met vijf ezelsrugbogen, binnenwand met motiefjes, laag rood dak ----------
    YF, YB, ZE = 0.0, 3.4, 3.4
    bogen = [GX0 + (GX1 - GX0) * (k + 0.5) / 5 for k in range(5)]
    addw(vlak([[(GX0, -0.1), (GX1, -0.1), (GX1, ZE), (GX0, ZE)]] + [ezelsrug(cx, 0.0, 2.3, 2.75) for cx in bogen], lambda u, v: (u, YF, v), 0.55, (0, 1, 0)))
    addw(bz(GX0, GX1, YB, YB + 0.3, -0.1, ZE))                                                                     # binnenwand
    for cx in bogen:                                                                                                 # motiefjes op de binnenwand
        for i in range(3):
            for j in range(4):
                put("motief", "rood" if (i + j) % 2 else "goud", boutline([(0, 0), (0.07, 0.12), (0, 0.24), (-0.07, 0.12)], 0, 0.02), Matrix.Translation((cx - 0.6 + 0.6 * i, YB - 0.02, 0.6 + 0.5 * j)) @ Matrix.Rotation(math.pi, 4, "Z"))
    put("gaanderij", "rand", bz(GX0, GX1, YF + 0.5, YB, 0.0, 0.08))
    for cx in bogen: put("gaanderij", "goud", bz(cx - 1.15, cx + 1.15, YF - 0.03, YF + 0.02, 0.62, 0.68))           # gouden lijstje
    dakschild((GX0 + GX1) / 2, (YF + YB + 0.3) / 2, GX1 - GX0 - 0.2, YB + 0.3 - YF, ZE, ZE + 0.65, 0.9)
    # ---------- hoge kantelenmuur erachter ----------
    MY0, MY1, MZ = 3.75, 4.6, 6.1
    addw(bz(GX0 - 0.4, GX1 + 0.4, MY0, MY1, -0.1, MZ))
    nk = 16
    for k in range(nk):
        x = GX0 - 0.4 + (GX1 - GX0 + 0.8) * (k + 0.5) / nk
        addw(bz(x - 0.28, x + 0.28, MY0, MY1, MZ, MZ + 0.5))
    for k in range(9):                                                                                              # voegenlijnen (blokpatroon)
        put("motief", "rand", bz(GX0 - 0.4, GX1 + 0.4, MY0 - 0.02, MY0, ZE + 0.85 + 0.25 * k, ZE + 0.87 + 0.25 * k))
    coll_box((GX0 + GX1) / 2, (YF + MY1) / 2, 1.8, GX1 - GX0, MY1 - YF, 3.6); coll_box((GX0 + GX1) / 2, (MY0 + MY1) / 2, 3.2, GX1 - GX0 + 0.8, MY1 - MY0, 6.4)
    # ---------- torens ----------
    for T_, s_ in ((TW, -1), (TO, 1)):
        x0, x1, y0, y1 = T_; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; w = x1 - x0; d = y1 - y0
        addw(vlak([[(x0, -0.1), (x1, -0.1), (x1, 3.6), (x0, 3.6)], ezelsrug(cx, 1.0, 0.9, 1.6)], lambda u, v: (u, y0, v), d, (0, 1, 0)))   # benedenverdieping met raam
        put("toren", "donker", bz(cx - 0.42, cx + 0.42, y0 + 0.25, y0 + 0.3, 1.0, 2.55))
        put("toren", "goud", bz(x0 - 0.02, x1 + 0.02, y0 - 0.02, y1 + 0.02, 0.95, 1.0))
        for side in (-1, 1):                                                                                         # sierpanelen links/rechts van het raam
            px = cx + side * w * 0.32
            put("toren", "rood", boutline([(-0.25, 0), (0.25, 0), (0.25, 0.8), (0.0, 1.15), (-0.25, 0.8)], 0, 0.03), Matrix.Translation((px, y0 - 0.02, 1.4)) @ Matrix.Rotation(math.pi, 4, "Z"))
            put("toren", "groen", boutline([(-0.15, 0.1), (0.15, 0.1), (0.15, 0.7), (0.0, 0.95), (-0.15, 0.7)], 0, 0.035), Matrix.Translation((px, y0 - 0.03, 1.4)) @ Matrix.Rotation(math.pi, 4, "Z"))
        dakschild(cx, cy, w, d, 3.6, 4.15, 1.05, "toren")
        for k in range(4):                                                                                          # consoles onder de luifel
            for sx in (-1, 1):
                put("toren", "stuc", bz(-0.08, 0.08, -0.75, 0.0, -0.45, 0.0), Matrix.Translation((cx + sx * (w / 2 - 0.4), y0, 3.6)) @ Matrix.Rotation(math.radians(30), 4, "X")) if k == 0 else None
        uw = w * 0.72; ux0, ux1, uy0, uy1 = cx - uw / 2, cx + uw / 2, cy - uw / 2, cy + uw / 2
        addw(vlak([[(ux0, 4.0), (ux1, 4.0), (ux1, 6.9), (ux0, 6.9)], ezelsrug(cx, 4.6, 1.05, 1.9)], lambda u, v: (u, uy0, v), uw, (0, 1, 0)))   # bovenverdieping
        put("toren", "donker", bz(cx - 0.48, cx + 0.48, uy0 + 0.3, uy0 + 0.35, 4.6, 6.4))
        put("toren", "rood", vlak([[(-0.6, 0), (0.6, 0), (0.6, 0.35), (-0.6, 0.35)]], lambda u, v: (cx + u, uy0 - 0.25, 4.6 + v), 0.3, (0, 1, 0)))   # vensterbank-kleed
        dakschild(cx, cy, uw, uw, 6.9, 7.5, 0.55, "toren")
        dr = blathe([(1.0, 7.45), (1.0, 8.5), (1.1, 8.55), (1.1, 8.65), (0.0, 8.65)], 8); put("toren", "stuc", dr, Matrix.Translation((cx, cy, 0)))
        for k in range(8):
            a = k * math.tau / 8 + math.pi / 8
            put("toren", "donker", boutline([(-0.2, 0), (0.2, 0), (0.2, 0.45), (0, 0.72), (-0.2, 0.45)], 0, 0.04), Matrix.Translation((cx + 1.0 * math.sin(a), cy - 1.0 * math.cos(a), 7.7)) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(math.pi, 4, "Z"))
        ui = [(0.0, 0), (1.0, 0.05), (1.3, 0.42), (1.32, 0.85), (1.12, 1.28), (0.75, 1.65), (0.38, 1.95), (0.14, 2.18), (0.0, 2.3)]
        put("toren", "stuc", blathe(ui, 16), Matrix.Translation((cx, cy, 8.6)))
        put("toren", "goud", blathe([(0.12, 0), (0.1, 0.2), (0.05, 0.3), (0.08, 0.38), (0.03, 0.5), (0.02, 1.05), (0.0, 1.1)], 8), Matrix.Translation((cx, cy, 10.85)))
        put("toren", "goud", btube([(cx + 1.12 * math.cos(a), cy + 1.12 * math.sin(a), 8.62) for a in [k * math.tau / 16 for k in range(17)]], 0.03, 5))
        ax = cx - s_ * (uw / 2)                                                                                     # rafel-arm (tapijtsteun) naar de muur toe
        put("arm", "stuc", btube([(ax, cy - 0.2, 5.6), (ax - s_ * 0.9, cy - 0.35, 5.75), (ax - s_ * 1.4, cy - 0.3, 5.95)], 0.12, 8))
        put("arm", "stuc", bz(min(ax - s_ * 1.6, ax - s_ * 0.7), max(ax - s_ * 1.6, ax - s_ * 0.7), cy - 0.7, cy + 0.1, 5.9, 6.0))
        for k in range(10):
            fx = ax - s_ * (0.75 + 0.09 * k)
            put("arm", "goud", btube([(fx, cy - 0.7, 5.9), (fx, cy - 0.72, 5.7)], 0.015, 4))
        coll_box(cx, cy, 2.0, w, d, 4.0)
    bmesh.ops.remove_doubles(wand, verts=wand.verts, dist=1e-4); put("muur", "stuc", wand)
    # ---------- voortuin: water, fontein, tulpenranden, plaveisel, gras, lange waterbak, hekjes ----------
    def bassin(poly, part):
        n = len(poly)
        for i in range(n):
            A, B = Vector(poly[i]), Vector(poly[(i + 1) % n]); L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x)
            put(part, "rand", bz(-0.12, L_ + 0.12, -0.15, 0.15, -0.2, 0.2), Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z"))
        plaat(poly, 0.08, 0.05, part, "water"); plaat(poly, -0.25, 0.05, part, "bassin")
    for p, nm in ((VIJVER, "vijver"), (WATER_W, "vijver"), (WATER_O, "vijver"), (BAK, "bak")): bassin(p, nm)
    MF = Matrix.Translation((-0.42, -6.46, 0))
    put("fontein", "goud", blathe([(0.35, 0), (0.3, 0.15), (0.12, 0.3), (0.1, 0.9), (0.2, 1.0), (0.32, 1.2), (0.38, 1.45), (0.3, 1.55), (0.12, 1.4), (0.0, 1.4)], 14), MF)
    for s_ in (-1, 1): put("fontein", "goud", btube([(s_ * 0.3, 0, 1.4), (s_ * 0.45, 0, 1.55), (s_ * 0.4, 0, 1.25)], 0.03, 5), MF)
    coll_box(-0.42, -6.46, 0.6, 0.8, 0.8, 1.2)
    plaat(BINNEN, 0.05, 0.1, "binnen", "grind", gaten=[VIJVER, [(-13.44, 0.46), (-13.29, -9.68), (-7.43, -9.6), (-7.47, -0.07)], [(7.58, 0.0), (7.72, -9.32), (13.61, -9.24), (13.46, 0.95)]])
    for G_, W_ in (([(-13.44, 0.46), (-13.29, -9.68), (-7.43, -9.6), (-7.47, -0.07)], WATER_W), ([(7.58, 0.0), (7.72, -9.32), (13.61, -9.24), (13.46, 0.95)], WATER_O)):
        plaat(G_, 0.12, 0.15, "tulpen", "modder", gaten=[W_])
    plaat(GRAS, 0.04, 0.08, "gras", "gras", gaten=[BINNEN, BAK])
    for sx in (-1, 1):                                                                                              # oosterse hekjes (ezelsrugboog-rooster)
        hx = sx * 15.6
        put("hek", "stuc", bz(hx - 0.25, hx + 0.25, -11.0, -10.5, -0.1, 2.0, 0.05)); put("hek", "stuc", ell((hx, -10.75, 2.15), (0.28, 0.28, 0.25), 8, 6))
        rooster = vlak([[(-11.0 + 0.0, 0.0), (-8.6, 0.0), (-8.6, 1.2), (-9.8, 1.9), (-11.0, 1.2)]] + [[(-10.7 + 0.35 * i, 0.15 + 0.35 * j), (-10.5 + 0.35 * i, 0.15 + 0.35 * j), (-10.5 + 0.35 * i, 0.35 + 0.35 * j), (-10.7 + 0.35 * i, 0.35 + 0.35 * j)] for i in range(6) for j in range(3)],
                       lambda u, v: (hx, u, v), 0.06, (1, 0, 0))
        put("hek", "stuc", rooster); coll_box(hx, -9.8, 1.0, 0.2, 2.4, 2.0)
    MB = TR(-12.0, -19.6, 0, 0)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.035, 6), MB)
    MBk = MB @ TR(0, 0, 0.9) @ Matrix.Rotation(math.radians(-28), 4, "X")
    put("boek", "rood", bz(-0.42, 0.42, -0.28, 0.28, -0.04, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.26, 0.26, 0.0, 0.05, 0.01), MBk)
    coll_box(-12.0, -19.6, 0.5, 0.6, 0.5, 1.0)
    plaat(PLEIN, 0.06, 0.12, "plein", "grind")
    for p in (BAK,):
        A, B = Vector(p[0]), Vector(p[2]); coll_box((A.x + B.x) / 2, (A.y + B.y) / 2, 0.2, abs(B.x - A.x) + 0.3, abs(B.y - A.y) + 0.3, 0.4)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"FK_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": PLEIN, "gras": GRAS, "binnen": BINNEN}, open(os.path.join(out, "fakir_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
