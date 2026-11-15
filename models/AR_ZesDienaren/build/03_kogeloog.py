"""03_kogeloog De Zes Dienaren: het Kogeloog-gebouwtje tegenover Langnek (Langnek zelf staat al: models/CH_Langnek). Witte, licht geknikte arcade
(OSM 50911609) met ronde bogen op Toscaanse zuilen, bakstenen voetmuurtjes, rood (bemost) pannendak, barokke krulgevel in het midden met blauw schildje,
lint "Kogeloog", buste van de geblinddoekte Kogeloog met steek en veren tussen twee siervazen (Kogeloog2010, Schets_kogeloog_overkapping_pieck,
Kogeloog_Borstbeeld); binnen: zes ovale schilderijen van de dienaren (Dienaar_*), horecaluik met Pieck-ornament, bankjes, houten plafond, rode
tegelvloer, lantaarns; plein met maaskeitjes (OSM 766787197, licht grind).
Frame: oorsprong = zwaartepunt 50911609 = studs (485.37, 150.69); model = OSM-assen (x oost, y noord); voorkant kijkt naar het NW (Langnek).
Gebruik: Blender -b -P 03_kogeloog.py -- --master KG_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.9, 0.88, 0.82, 1), 0.85), "pannen": ((0.55, 0.3, 0.2, 1), 0.75), "baksteen": ((0.5, 0.28, 0.2, 1), 0.85), "tegel": ((0.55, 0.25, 0.18, 1), 0.6),
        "hout": ((0.36, 0.25, 0.16, 1), 0.8), "goud": ((0.88, 0.66, 0.22, 1), 0.3), "blauw": ((0.15, 0.3, 0.6, 1), 0.5), "rood": ((0.66, 0.12, 0.08, 1), 0.5),
        "zwart": ((0.04, 0.04, 0.04, 1), 0.4), "huid": ((0.9, 0.74, 0.62, 1), 0.5), "wit": ((0.95, 0.94, 0.9, 1), 0.5), "groen": ((0.2, 0.45, 0.3, 1), 0.5),
        "ijzer": ((0.06, 0.06, 0.06, 1), 0.45), "lamp": ((1.0, 0.85, 0.55, 1), 0.3), "grind": ((0.86, 0.83, 0.76, 1), 0.95), "schilderij": ((0.75, 0.62, 0.35, 1), 0.6)}
rr = random.Random(1952)
VOOR = [(-9.1, -3.81), (-2.19, -0.8), (1.79, 2.14), (5.57, 8.13)]        # NW-rand (arcade)
ACHTER = [(-8.16, -7.01), (0.03, -3.87), (3.76, -1.13), (8.3, 6.35)]    # ZO-rand (achterwand)
PLEIN = [(5.57, 8.13), (-0.38, 13.38), (-5.51, 17.12), (-9.35, 16.31), (-9.88, 13.83), (-11.33, 11.74), (-13.48, 10.37), (-15.99, 9.93), (-18.48, 10.46),
         (-19.82, 2.8), (-19.45, -2.61), (-19.13, -5.16), (-16.79, -4.6), (-15.24, -4.24), (-15.01, -5.27), (-12.38, -8.22), (-8.16, -7.01), (-9.1, -3.81),
         (-2.19, -0.8), (1.79, 2.14)]
ZK, ZE, ZN = 2.0, 3.35, 4.55                                             # kapiteel, goot, nok


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    def plaat(poly, z, dz, part, mat):
        tris = tessellate_polygon([[Vector((x, y, 0)) for x, y in poly]])
        bm = bmesh.new(); Tt = [bm.verts.new((x, y, z)) for x, y in poly]; Bb = [bm.verts.new((x, y, z - dz)) for x, y in poly]
        for t in tris:
            f = bm.faces.new([Tt[i] for i in t]); f.normal_update()
            if f.normal.z < 0: f.normal_flip()
            g = bm.faces.new([Bb[i] for i in t]); g.normal_update()
            if g.normal.z > 0: g.normal_flip()
        for i in range(len(poly)):
            j = (i + 1) % len(poly); bm.faces.new((Tt[i], Bb[i], Bb[j], Tt[j]))
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
    tot = sum((Vector(b) - Vector(a)).length for a, b in zip(VOOR, VOOR[1:])); acc = 0.0; midden = None
    for si, (a, b, c, d) in enumerate(zip(VOOR, VOOR[1:], ACHTER, ACHTER[1:])):
        A, B, C, D = Vector(a), Vector(b), Vector(c), Vector(d)
        L_ = (B - A).length; ang = math.atan2(B.y - A.y, B.x - A.x)
        M_ = Matrix.Translation((A.x, A.y, 0)) @ Matrix.Rotation(ang, 4, "Z")              # lokaal: x langs de voorgevel, +y = naar binnen/achter? (links van de looprichting)
        diep = abs(((C + D) / 2 - (A + B) / 2).dot(Vector((-math.sin(ang), math.cos(ang)))))
        inw = 1 if ((C + D) / 2 - (A + B) / 2).dot(Vector((-math.sin(ang), math.cos(ang)))) > 0 else -1
        n_ = max(2, round(L_ / 2.4)); step = L_ / n_
        gaten = []
        for k in range(n_):
            cx = (k + 0.5) * step; r = step / 2 - 0.28
            gaten.append([(cx + r, 0.0)] + [(cx + r * math.cos(math.pi * i / 10), ZK + r * 0.0 + r * math.sin(math.pi * i / 10)) for i in range(11)] + [(cx - r, 0.0)])
        put("arcade", "stuc", vlak([[(0, -0.1), (L_, -0.1), (L_, ZE), (0, ZE)]] + gaten, lambda u, v: (u, 0.0, v), inw * 0.4, (0, 1, 0)), M_)
        for k in range(n_ + 1):                                                            # Toscaanse zuilen voor de pijlers
            x = k * step
            put("arcade", "stuc", blathe([(0.28, 0), (0.28, 0.12), (0.2, 0.2), (0.18, 0.3), (0.15, ZK - 0.25), (0.2, ZK - 0.15), (0.26, ZK - 0.05), (0.26, ZK), (0.0, ZK)], 12), M_ @ Matrix.Translation((x, inw * -0.12, 0)))
            coll_box(*(Matrix(M_) @ Vector((x, 0.0, 0))).xy, 1.2, 0.5, 0.5, 2.4, math.degrees(ang))
            if k in (1, n_ - 1):
                put("lampen", "ijzer", bz(-0.05, 0.05, inw * -0.5, inw * -0.3, 1.9, 2.0), M_ @ Matrix.Translation((x, 0, 0)))
                put("lampen", "lamp", bz(-0.14, 0.14, inw * -0.62, inw * -0.38, 1.55, 1.95), M_ @ Matrix.Translation((x, 0, 0)))
                put("lampen", "ijzer", blathe([(0.2, 0), (0.0, 0.18)], 6), M_ @ Matrix.Translation((x, inw * -0.5, 1.95)))
        if si in (0, 2):                                                                     # bakstenen voetmuurtjes aan de uiteinden
            for k in ((0, 1) if si == 0 else (n_ - 1, n_)):
                pass
            k0 = 0 if si == 0 else n_ - 1
            put("arcade", "baksteen", bz(k0 * step + 0.25, (k0 + 1) * step - 0.25, inw * -0.05, inw * 0.35, -0.1, 0.75), M_)
        put("arcade", "stuc", vlak([[(-0.3, -0.1), (L_ + 0.3, -0.1), (L_ + 0.3, ZE), (-0.3, ZE)]], lambda u, v: (u, inw * diep, v), inw * 0.3, (0, 1, 0)), M_)   # achterwand
        coll_box(*(Matrix(M_) @ Vector((L_ / 2, inw * (diep + 0.15), 0))).xy, 1.5, L_, 0.4, 3.0, math.degrees(ang))
        plaat([tuple((Matrix(M_) @ Vector((u, v, 0))).xy) for u, v in ((0, 0), (L_, 0), (L_, inw * diep), (0, inw * diep))], 0.08, 0.1, "vloer", "tegel")
        put("arcade", "hout", bz(-0.2, L_ + 0.2, inw * 0.2 if inw > 0 else inw * diep, inw * diep if inw > 0 else inw * 0.2, ZE - 0.15, ZE - 0.05), M_)   # houten plafond
        # dak: zadeldak langs het segment, pannenrijen
        db = bmesh.new(); ov = 0.55; ym = inw * diep / 2; hw = diep / 2 + ov
        for s_ in (-1, 1):
            q = [(-0.4, ym + s_ * hw, ZE - 0.15), (L_ + 0.4, ym + s_ * hw, ZE - 0.15), (L_ + 0.4, ym, ZN), (-0.4, ym, ZN)]
            Av = [db.verts.new(p) for p in q]; Bv = [db.verts.new((p[0], p[1], p[2] + 0.12)) for p in q]
            db.faces.new(Av); db.faces.new(Bv[::-1])
            for i in range(4): db.faces.new((Av[i], Av[(i + 1) % 4], Bv[(i + 1) % 4], Bv[i]))
            for k in range(int((L_ + 0.8) / 0.28)):
                x = -0.4 + 0.14 + k * 0.28
                put("dak", "pannen", btube([(x, ym + s_ * hw, ZE - 0.02), (x, ym + s_ * hw * 0.5, (ZE + ZN) / 2 + 0.08), (x, ym, ZN + 0.12)], 0.07, 5), M_)
        bmesh.ops.recalc_face_normals(db, faces=db.faces); put("dak", "pannen", db, M_)
        put("dak", "pannen", btube([(-0.4, ym, ZN + 0.15), (L_ + 0.4, ym, ZN + 0.15)], 0.13, 8), M_)
        # schilderijen + bankjes aan de achterwand
        for k in range(n_):
            cx = (k + 0.5) * step; sc_ = 0.55
            put("schilderij", "zwart", ell((cx, inw * (diep - 0.04), 1.75), (sc_ * 0.95, 0.05, sc_ * 0.72), 16, 6), M_)
            put("schilderij", "goud", ell((cx, inw * (diep - 0.07), 1.75), (sc_ * 0.88, 0.05, sc_ * 0.66), 16, 6), M_)
            put("schilderij", "schilderij", ell((cx, inw * (diep - 0.1), 1.75), (sc_ * 0.8, 0.05, sc_ * 0.6), 16, 6), M_)
            put("schilderij", "rood", boutline([(-0.25, 0), (0.25, 0), (0.15, 0.22), (0, 0.3), (-0.15, 0.22)], 0, 0.04), M_ @ Matrix.Translation((cx, inw * (diep - 0.1), 2.15)))
            put("bank", "hout", bz(cx - 0.8, cx + 0.8, inw * (diep - 0.55), inw * (diep - 0.15), 0.42, 0.48), M_)
            for s_ in (-1, 1): put("bank", "stuc", bz(cx + s_ * 0.65 - 0.08, cx + s_ * 0.65 + 0.08, inw * (diep - 0.5), inw * (diep - 0.2), 0.0, 0.42), M_)
        if midden is None and acc + L_ >= tot / 2:
            t = (tot / 2 - acc); midden = (M_, t, inw, diep, ang)
        acc += L_
    # ---------- middengevel: barokke krulgevel, schildje, lint, buste, siervazen, horecaluik ----------
    M_, t, inw, diep, ang = midden
    G = M_ @ Matrix.Translation((t, inw * -0.05, 0))
    krul = [(-1.9, ZE - 0.2), (1.9, ZE - 0.2), (1.9, ZE + 0.35), (1.55, ZE + 0.5), (1.2, ZE + 0.9), (0.85, ZE + 1.05), (0.75, ZE + 1.5), (0.4, ZE + 1.65), (0.0, ZE + 1.8),
            (-0.4, ZE + 1.65), (-0.75, ZE + 1.5), (-0.85, ZE + 1.05), (-1.2, ZE + 0.9), (-1.55, ZE + 0.5), (-1.9, ZE + 0.35)]
    put("gevel", "stuc", vlak([krul], lambda u, v: (u, 0.0, v), inw * 0.5, (0, 1, 0)), G)
    for s_ in (-1, 1):
        put("gevel", "stuc", btube([(s_ * 1.55, 0, ZE + 0.55), (s_ * 1.25, inw * -0.05, ZE + 0.95), (s_ * 0.95, inw * -0.05, ZE + 0.92), (s_ * 1.0, inw * -0.05, ZE + 0.75)], 0.08, 6), G)
        put("gevel", "stuc", blathe([(0.18, 0), (0.22, 0.15), (0.12, 0.3), (0.18, 0.45), (0.12, 0.6), (0.04, 0.7), (0.0, 0.75)], 10), G @ Matrix.Translation((s_ * 1.75, inw * 0.25, ZE + 0.4)))   # siervazen
    put("gevel", "blauw", boutline([(-0.25, 0.3), (0.25, 0.3), (0.25, 0.0), (0, -0.25), (-0.25, 0.0)], 0, 0.04), G @ Matrix.Translation((0, inw * -0.04, ZE + 1.05)))
    put("gevel", "goud", boutline([(-1.0, 0.0), (1.0, 0.0), (1.15, 0.12), (1.0, 0.24), (-1.0, 0.24), (-1.15, 0.12)], 0, 0.04), G @ Matrix.Translation((0, inw * -0.05, ZE + 0.3)))   # lint "Kogeloog"
    for k in range(8): put("gevel", "rood", bz(-0.6 + k * 0.17, -0.6 + k * 0.17 + 0.09, inw * -0.07, inw * -0.05, ZE + 0.36, ZE + 0.48), G)
    put("gevel", "stuc", bz(-0.32, 0.32, -0.3, 0.3, ZE + 1.8, ZE + 2.1), G @ Matrix.Translation((0, inw * 0.25, 0)))   # sokkel buste
    B0 = G @ Matrix.Translation((0, inw * 0.25, ZE + 2.1))
    put("buste", "rood", ell((0, 0, 0.32), (0.45, 0.3, 0.35), 14, 10), B0)                                      # rode jas
    put("buste", "wit", ell((0, inw * -0.22, 0.42), (0.14, 0.08, 0.2), 8, 6), B0)                                # jabot
    put("buste", "huid", ell((0, 0, 0.9), (0.2, 0.2, 0.25), 12, 10), B0)
    put("buste", "huid", ell((0, inw * -0.2, 0.85), (0.05, 0.08, 0.06), 6, 4), B0)
    put("buste", "zwart", bz(-0.22, 0.22, inw * -0.22, inw * -0.14, 0.92, 1.02), B0)                           # blinddoek
    put("buste", "wit", ell((0.18, 0.02, 0.92), (0.08, 0.1, 0.12), 6, 4), B0); put("buste", "wit", ell((-0.18, 0.02, 0.92), (0.08, 0.1, 0.12), 6, 4), B0)   # pruik
    put("buste", "zwart", boutline([(-0.35, 0), (0.35, 0), (0.0, 0.25)], -0.25, 0.5), B0 @ Matrix.Translation((0, 0, 1.08)))   # steek
    for k, (col, a) in enumerate((("rood", -0.5), ("groen", 0.0), ("rood", 0.5))):
        put("buste", col, btube([(0, 0.05, 1.2), (0.25 * math.sin(a), 0.1, 1.5), (0.4 * math.sin(a) + 0.05, 0.2, 1.7)], 0.05, 5), B0)   # veren
    put("luik", "hout", bz(-0.9, 0.9, inw * (diep - 0.02), inw * (diep + 0.02), 0.85, 1.85), M_ @ Matrix.Translation((t, 0, 0)))
    put("luik", "hout", bz(-1.0, 1.0, inw * (diep - 0.35), inw * (diep - 0.02), 0.85, 0.92), M_ @ Matrix.Translation((t, 0, 0)))
    put("luik", "goud", boutline([(-0.9, 0), (0.9, 0), (0.7, 0.35), (0.3, 0.45), (0.0, 0.6), (-0.3, 0.45), (-0.7, 0.35)], 0, 0.05), M_ @ Matrix.Translation((t, inw * (diep - 0.08), 1.95)))
    put("luik", "papier" if "papier" in MATS else "wit", bz(-0.45, 0.45, inw * (diep - 0.14), inw * (diep - 0.12), 2.1, 2.35), M_ @ Matrix.Translation((t, 0, 0)))
    # ---------- plein (maaskeitjes -> licht grind) ----------
    plaat(PLEIN, 0.05, 0.1, "plein", "grind")
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"KG_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": PLEIN}, open(os.path.join(out, "kogeloog_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
