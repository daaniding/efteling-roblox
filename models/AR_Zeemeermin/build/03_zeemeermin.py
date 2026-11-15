"""03_zeemeermin De Kleine Zeemeermin (1970, beeld Ton van de Ven; decor = muur van de oude Liefdesbron): vijvertje (OSM 55423759) met betonnen binnenrand,
rotsstapel (766787182) met de zittende meermin (blond, groene geschubde staart met gele vin) en de grote spuwende vis onder haar linkerarm; wit gepleisterd
barok decor aan de achterrand (middenpaneel met krullen, dolfijn-reliëf, schelpbekken op een console, Cupido bovenop) met lage vleugelmuren; smeedijzeren hekjes
langs de zijkanten, breukstenen rand + lage blauwgroene leuning aan de padkant, sprookjesboek. Frame: oorsprong OSM-node 7161344475, model = OSM-assen,
-Y = zuid (naar het pad 405848924), z 0 = maaiveld. Gebruik: Blender -b -P 03_zeemeermin.py -- --master ZM_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.9, 0.9, 0.86, 1), 0.9), "natuursteen": ((0.6, 0.6, 0.58, 1), 0.85), "rots": ((0.35, 0.36, 0.36, 1), 0.7), "breuksteen": ((0.6, 0.6, 0.62, 1), 0.9),
        "water": ((0.1, 0.14, 0.09, 1), 0.1), "modder": ((0.12, 0.1, 0.07, 1), 1.0), "ijzer": ((0.06, 0.06, 0.06, 1), 0.45), "leuning": ((0.2, 0.36, 0.38, 1), 0.6),
        "huid": ((0.92, 0.76, 0.62, 1), 0.5), "haar": ((0.85, 0.7, 0.4, 1), 0.6), "staart": ((0.3, 0.55, 0.45, 1), 0.4), "vin": ((0.92, 0.82, 0.55, 1), 0.4),
        "vis": ((0.92, 0.85, 0.5, 1), 0.4), "visrug": ((0.3, 0.55, 0.6, 1), 0.4), "oog": ((0.05, 0.05, 0.05, 1), 0.2), "waterstraal": ((0.75, 0.85, 0.9, 1), 0.1),
        "papier": ((0.92, 0.86, 0.7, 1), 0.9), "rood": ((0.62, 0.1, 0.1, 1), 0.5), "grind": ((0.86, 0.83, 0.76, 1), 0.95)}
POND = [(-0.32, 2.24), (1.24, 2.21), (2.14, -1.63), (-0.32, -1.97), (-2.51, -0.88)]          # OSM 55423759
WY = 2.32                                                                                    # voorvlak decor (achterrand vijver)
rr = random.Random(1970)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    def plaat(poly, z, mat, part, dz):
        bm = bmesh.new(); t_ = [bm.verts.new((x, y, z)) for x, y in poly]; b_ = [bm.verts.new((x, y, z - dz)) for x, y in poly]
        ft = bm.faces.new(t_); fb_ = bm.faces.new(b_[::-1])
        for i in range(len(poly)): bm.faces.new((t_[i], b_[i], b_[(i + 1) % len(poly)], t_[(i + 1) % len(poly)]))
        bmesh.ops.triangulate(bm, faces=[ft, fb_], ngon_method="EAR_CLIP"); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f_ in bm.faces:
            if abs(f_.normal.z) > 0.5 and (f_.calc_center_median().z > z - dz / 2) != (f_.normal.z > 0): f_.normal_flip()
        put(part, mat, bm)
    C = Vector((sum(p[0] for p in POND) / 5, sum(p[1] for p in POND) / 5))
    # ---------- vijver: water, bodem, betonnen binnenrand (Zeemeermin-leeg) ----------
    plaat(POND, -0.15, "water", "vijver", 0.06)
    plaat([(C + (Vector(p) - C) * 1.02)[:] for p in POND], -0.55, "modder", "vijver", 0.08)
    for a, b in zip(POND, POND[1:] + POND[:1]):
        A, B = Vector(a), Vector(b); d = B - A; n = Vector((d.y, -d.x)).normalized()
        if n.dot(Vector(a) - C) < 0: n = -n
        bm = bmesh.new(); q = [A, B, B + n * 0.22, A + n * 0.22]
        bot = [bm.verts.new((v.x, v.y, -0.6)) for v in q]; top = [bm.verts.new((v.x, v.y, 0.18)) for v in q]
        bm.faces.new(bot[::-1]); bm.faces.new(top)
        for j in range(4): bm.faces.new((bot[j], bot[(j + 1) % 4], top[(j + 1) % 4], top[j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("rand", "natuursteen", bm)
    # breukstenen rand aan de padkant (Boekloc: grijze breuksteen op en voor de rand)
    for a, b in ((POND[2], POND[3]), (POND[3], POND[4])):
        A, B = Vector(a), Vector(b); L = (B - A).length; k = int(L / 0.28)
        for i in range(k + 1):
            p = A.lerp(B, i / k); n = (p - C).normalized(); sc = rr.uniform(0.15, 0.28)
            for layer in range(2):
                st = bz(-sc, sc, -sc * 0.7, sc * 0.7, -sc * 0.5, sc * 0.5, sc * 0.2)
                for v in st.verts: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * sc * 0.25
                q = p + n * rr.uniform(0.05, 0.45)
                put("rand", "breuksteen", st, TR(q.x, q.y, 0.12 + layer * 0.18 * rr.random(), rr.uniform(0, 360)))
    # ---------- rotsstapel midden (766787182) met ring van stenen in het water (Zeemeermin2024, -leeg) ----------
    RC = Vector((0.03, -0.07))
    for k in range(70):
        a = rr.uniform(0, math.tau); h = rr.random()
        r = 0.95 * (1 - 0.75 * h) + rr.uniform(-0.1, 0.1); z = -0.2 + 1.15 * h; sc = rr.uniform(0.16, 0.32) * (1 - 0.35 * h)
        st = ell((0, 0, 0), (sc * rr.uniform(1.0, 1.4), sc * rr.uniform(0.8, 1.1), sc * rr.uniform(0.55, 0.8)), 9, 7)
        for v in st.verts: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * sc * 0.12
        put("rotsen", "rots", st, TR(RC.x + r * math.cos(a), RC.y + r * math.sin(a), z, rr.uniform(0, 360)))
    put("rotsen", "rots", blathe([(1.0, -0.3), (0.85, 0.3), (0.55, 0.75), (0.3, 1.0), (0, 1.05), (0, -0.3)], 10), TR(RC.x, RC.y, 0))
    coll_box(RC.x, RC.y, 0.5, 2.0, 2.0, 1.0)
    # ---------- decor: middenpaneel met barokke top, dolfijn, schelpbekken, Cupido; vleugelmuren (Kzmm, Zeemeermin-leeg) ----------
    XC = 0.46
    top = [(-0.62, 0.0), (-0.62, 2.0), (-0.7, 2.15), (-0.58, 2.35), (-0.52, 2.6), (-0.42, 2.78), (-0.25, 2.9), (-0.15, 3.05), (0, 3.12)]
    outl = top + [(-x, z) for x, z in top[::-1][1:]]
    outl = [(XC + x, z) for x, z in outl]
    put("decor", "stuc", organisch(boutline(outl, WY, 0.35), 0.03, 2, 0.4, 0.008, 2.0, 0.5))
    put("decor", "natuursteen", band([(XC + x, z) for x, z in top[2:]] + [(XC - x, z) for x, z in top[2:][::-1][1:]], 0.07, WY - 0.05, 0.1))     # profiellijst langs de top
    for s in (-1, 1):                                                                              # krullen aan de zijkanten van het paneel
        for (z, r) in ((2.05, 0.13), (0.9, 0.11)):
            put("decor", "natuursteen", blathe([(0, 0), (r, 0), (r, 0.07), (0, 0.09)], 12), Matrix.Translation((XC + s * 0.66, WY - 0.02, z)) @ Matrix.Rotation(math.radians(90), 4, "X"))
        put("decor", "natuursteen", btube([(XC + s * 0.66, WY - 0.06, 0.95), (XC + s * 0.74, WY - 0.06, 1.5), (XC + s * 0.68, WY - 0.06, 2.0)], 0.04, 6))
    put("decor", "natuursteen", blathe([(0, 0), (0.06, 0.0), (0.07, 0.05), (0.02, 0.12), (0, 0.12)], 10), TR(XC, WY - 0.04, 3.1))   # voetstuk Cupido
    # dolfijn-reliëf (kop omlaag, spuit in het bekken)
    Md = TR(XC, WY - 0.08, 2.3)
    put("decor", "stuc", ell((0, 0, 0.12), (0.08, 0.06, 0.22), 10, 8), Md)
    put("decor", "stuc", ell((0, -0.02, -0.12), (0.06, 0.05, 0.1), 8, 6), Md)
    for s in (-1, 1): put("decor", "stuc", ell((s * 0.09, 0.0, 0.32), (0.08, 0.03, 0.05), 8, 6), Md)
    # schelpbekken op console
    put("decor", "natuursteen", blathe([(0.05, 0), (0.12, 0.05), (0.28, 0.25), (0.3, 0.3), (0.26, 0.32), (0, 0.15)], 16), Matrix.Translation((XC, WY - 0.3, 1.55)) @ Matrix.Scale(1.0, 4))
    for k in range(9):                                                                              # schelpribben
        a = math.pi * (k / 8); put("decor", "natuursteen", btube([(XC, WY - 0.3, 1.6), (XC + 0.28 * math.cos(a), WY - 0.3 - 0.28 * math.sin(a) * 0.6, 1.86)], 0.015, 4))
    put("decor", "natuursteen", blathe([(0.0, 0), (0.12, 0.0), (0.2, 0.3), (0.14, 0.5), (0, 0.55)], 10), TR(XC, WY - 0.18, 1.05))   # console
    put("decor", "waterstraal", btube([(XC, WY - 0.12, 2.15), (XC, WY - 0.2, 1.95), (XC, WY - 0.28, 1.8)], 0.02, 5))
    # Cupido (staand engeltje met vleugels, Cupido_zeemeermin)
    Mc = TR(XC, WY - 0.02, 3.22)
    lijf = bmesh.new()
    def addl(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); lijf.from_mesh(me_); bpy.data.meshes.remove(me_)
    for (c, r) in (((0, 0, 0.32), (0.09, 0.07, 0.13)), ((0, 0, 0.5), (0.075, 0.07, 0.075)), ((-0.04, 0, 0.12), (0.04, 0.04, 0.14)), ((0.04, 0, 0.12), (0.04, 0.04, 0.14)),
                   ((-0.1, 0, 0.36), (0.03, 0.03, 0.09)), ((0.1, -0.02, 0.38), (0.03, 0.03, 0.09))):
        addl(ell(c, r, 10, 8))
    put("cupido", "stuc", organisch(lijf, 0.012, 3, 0.5, 0.002, 20, 0.5), Mc)
    for s in (-1, 1):
        put("cupido", "stuc", boutline([(0, 0.3), (s * 0.12, 0.45), (s * 0.2, 0.62), (s * 0.12, 0.5), (s * 0.06, 0.38)], 0.04, 0.02), Mc)
    # vleugelmuren: lager, golvende bovenrand met lijst (Zeemeermin-leeg)
    for s, x_end in ((-1, -2.2), (1, 2.5)):
        x0 = XC + s * 0.62; L = abs(x_end - x0)
        prof = [(x0 + s * L * t, 1.3 - 0.45 * t + 0.12 * math.sin(math.pi * t) * (1 - t)) for t in [i / 10 for i in range(11)]]       # laag (Zeemeermin-leeg)
        outw = [(x0, 0.0)] + prof + [(x_end, 0.0)]
        if s < 0: outw = outw[::-1]
        put("decor", "stuc", boutline(outw, WY + 0.05, 0.28))
        put("decor", "natuursteen", band(prof if s > 0 else prof[::-1], 0.06, WY, 0.38))
        put("decor", "natuursteen", blathe([(0, 0), (0.12, 0), (0.12, 0.08), (0, 0.11)], 12), Matrix.Translation((x_end, WY + 0.0, 0.95)) @ Matrix.Rotation(math.radians(90), 4, "X"))
        coll_box((x0 + x_end) / 2, WY + 0.19, 0.9, L, 0.3, 1.8)
    coll_box(XC, WY + 0.17, 1.5, 1.3, 0.35, 3.0)
    # ---------- hekjes: smeedijzer langs de zijkanten (Zeemeermin-leeg), lage leuning aan de padkant (Boekloc) ----------
    def hek(a, b, mat, h, spijlen=True):
        A, B = Vector(a), Vector(b); L = (B - A).length
        put("hek", mat, btube([(A.x, A.y, h), (B.x, B.y, h)], 0.02, 5)); put("hek", mat, btube([(A.x, A.y, 0.15), (B.x, B.y, 0.15)], 0.015, 5))
        k = int(L / (0.13 if spijlen else 1.1))
        for i in range(k + 1):
            p = A.lerp(B, i / max(1, k)); put("hek", mat, btube([(p.x, p.y, 0.05), (p.x, p.y, h + (0.06 if spijlen else 0.02))], 0.011 if spijlen else 0.022, 4))
        m = (A + B) / 2; d = B - A; coll_box(m.x, m.y, 0.5, L, 0.15, 1.0, math.degrees(math.atan2(d.y, d.x)))
    off = lambda p, q: tuple((C + (Vector(p) - C) * q)[:])
    hek(off((-2.2, WY), 1.0), off(POND[4], 1.12), "ijzer", 0.85)
    hek(off((2.5, WY), 1.0), off(POND[2], 1.12), "ijzer", 0.85)
    hek(off(POND[4], 1.18), off(POND[3], 1.18), "leuning", 0.55, False); hek(off(POND[3], 1.18), off(POND[2], 1.18), "leuning", 0.55, False)
    # ---------- de meermin: zittend op de rotsen, bovenlijf rechtop, hoofd iets naar links, rechterarm leunt op de rots, staart krult naar voren-rechts ----------
    MZ = TR(RC.x - 0.05, RC.y + 0.05, 0.95, -20) @ Matrix.Scale(1.35, 4)                # zittend ~1.3 m hoog (Kzmm: hoofd t.h.v. de onderste krullen)
    body = bmesh.new()
    def addb(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); body.from_mesh(me_); bpy.data.meshes.remove(me_)
    for (c, r) in (((0, 0, 0.18), (0.16, 0.12, 0.18)), ((0, 0.0, 0.42), (0.17, 0.11, 0.16)), ((0, 0, 0.6), (0.14, 0.1, 0.08)),
                   ((-0.06, -0.08, 0.47), (0.065, 0.06, 0.06)), ((0.06, -0.08, 0.47), (0.065, 0.06, 0.06)),                # borsten
                   ((0, 0, 0.7), (0.05, 0.05, 0.07)), ((-0.02, -0.01, 0.84), (0.09, 0.1, 0.12))):                         # hals, hoofd
        addb(ell(c, r, 12, 10))
    for (a, b, r) in ((((-0.17, 0, 0.6)), (-0.28, -0.05, 0.36), 0.055), ((-0.28, -0.05, 0.36), (-0.33, -0.12, 0.08), 0.048),     # rechterarm leunt op de rots (Kzmm)
                      ((0.17, 0, 0.6), (0.27, 0.02, 0.4), 0.055), ((0.27, 0.02, 0.4), (0.25, -0.05, 0.28), 0.048)):            # linkerarm om de vis
        addb(btube([Vector(a), Vector(b)], r, 8))
    put("meermin", "huid", organisch(body, 0.012, 3, 0.5, 0.002, 20, 0.5), MZ)
    hb = bmesh.new()                                                                                # lang blond haar over de rug en de schouders
    def addh(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); hb.from_mesh(me_); bpy.data.meshes.remove(me_)
    addh(ell((-0.02, 0.02, 0.88), (0.105, 0.11, 0.12), 12, 10))
    for k in range(9):
        a = math.radians(-70 + k * 17.5); x, y = 0.09 * math.sin(a), 0.06 + 0.04 * math.cos(a)
        addh(btube([Vector((x, y, 0.9)), Vector((x * 1.5, y + 0.05, 0.7)), Vector((x * 1.8, y + 0.06 - 0.03 * abs(k - 4) / 4, 0.38))], 0.042, 6))
    put("meermin", "haar", organisch(hb, 0.012, 2, 0.4, 0.003, 20, 0.5), MZ)
    tl = [Vector((0, 0, 0.12)), Vector((0.05, -0.12, 0.02)), Vector((0.12, -0.32, -0.08)), Vector((0.32, -0.45, -0.22)), Vector((0.55, -0.42, -0.35)), Vector((0.72, -0.28, -0.42))]
    for i, (a, b) in enumerate(zip(tl, tl[1:])):                                                    # staart (groen geschubd)
        r = 0.15 * (1 - i / len(tl)) + 0.035; put("meermin", "staart", btube([a, b], r, 10), MZ)
        put("meermin", "staart", ell(b, (r, r, r), 10, 8), MZ)
    for s in (-1, 1):                                                                               # gele staartvin (waaier)
        fin = boutline([(0, 0), (s * 0.12, 0.28), (s * 0.05, 0.36), (s * 0.18, 0.4), (s * 0.24, 0.12)], -0.01, 0.02)
        put("meermin", "vin", fin, MZ @ Matrix.Translation(tl[-1]) @ Matrix.Rotation(math.radians(60), 4, "Z") @ Matrix.Rotation(math.radians(80), 4, "X"))
    # de grote vis onder haar linkerarm, bek omlaag, spuwt water (Kzmm)
    MV = MZ @ TR(0.42, -0.06, 0.36, 20) @ Matrix.Rotation(math.radians(62), 4, "Y") @ Matrix.Scale(0.9, 4)   # rechtop, bek omlaag (Kzmm)
    put("vis", "vis", ell((0, 0, 0), (0.34, 0.18, 0.2), 14, 10), MV)
    put("vis", "visrug", ell((0, 0.05, 0.08), (0.3, 0.12, 0.13), 12, 8), MV)
    put("vis", "vis", ell((0.3, 0, -0.02), (0.16, 0.16, 0.15), 12, 10), MV)                                   # grote kop
    for s in (-1, 1):
        put("vis", "oog", ell((0.3, s * 0.11, 0.03), (0.04, 0.02, 0.04), 8, 6), MV)
        put("vis", "vin", boutline([(0, 0), (0.12, 0.15), (0.2, 0.05), (0.18, -0.08)], -0.01, 0.02), MV @ TR(0.05, s * 0.18, 0.0) @ Matrix.Rotation(math.radians(90 * s), 4, "X"))
    put("vis", "vin", boutline([(0, 0), (-0.2, 0.22), (-0.24, 0.0), (-0.2, -0.22)], -0.01, 0.02), MV @ TR(-0.32, 0, 0) @ Matrix.Rotation(math.radians(90), 4, "X"))
    put("vis", "vin", boutline([(0, 0), (0.1, 0.18), (0.25, 0.15), (0.3, 0.0)], -0.01, 0.02), MV @ TR(-0.15, 0, 0.18) @ Matrix.Rotation(math.radians(90), 4, "X"))
    m0 = MV @ Vector((0.42, 0, -0.08)); put("vis", "waterstraal", btube([m0, m0 + Vector((0.12, -0.05, -0.4)), m0 + Vector((0.2, -0.1, -1.0))], 0.03, 6))
    # ---------- sprookjesboek (Boekloc: links voor) + strook licht grind tot het pad ----------
    MB = TR(-2.6, -2.3, 0.0, 30)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.035, 6), MB)
    for s in (-1, 1): put("boek", "ijzer", btube([(0, 0, 0.05), (s * 0.12, 0.05, 0.12), (s * 0.22, 0.0, 0.0)], 0.018, 5), MB)
    MBk = MB @ TR(0, 0, 0.9) @ Matrix.Rotation(math.radians(28), 4, "X")
    put("boek", "rood", bz(-0.42, 0.42, -0.28, 0.28, -0.04, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.26, 0.26, 0.0, 0.05, 0.01), MBk)
    coll_box(-2.6, -2.3, 0.5, 0.7, 0.5, 1.0, 30)
    PLEIN = [(-3.4, -1.2), (-0.4, -2.75), (2.7, -2.25), (3.2, -3.4), (-0.95, -4.5), (-3.8, -3.0)]
    plaat(PLEIN, 0.07, "grind", "plein", 0.12)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"ZM_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": PLEIN, "vijver": POND}, open(os.path.join(out, "zeemeermin_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
