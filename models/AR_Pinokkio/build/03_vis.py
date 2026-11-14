"""03_vis Pinokkio: de Monstervis in het haventje (Pinokkio_monstervis*.jpg, Monstervis-achter.jpg, Pinokkiohelevis.jpg, ontwerpschets MM).
Kop met enorme open bek (opgerolde bovenlip, hangende onderkaak, roze keel, witte haaktanden), gele ogen onder zware wenkbrauwen, wratten,
tentakels met knopjes op de kop, geschubd lijf in een boog met gerafelde rugvinnen dat het water in duikt; verderop de krullende staart met vin.
Lokaal: +X = kijkrichting van de vis, z = 0 waterlijn. Wordt in het modelframe gezet op OSM-node Monstervis (16.87, -6.77), kijkend naar het plein (-X).
Gebruik: Blender -b -P 03_vis.py -- --master PK_vis_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"visoranje": ((0.8, 0.36, 0.2, 1), 0.45), "vislicht": ((0.95, 0.6, 0.38, 1), 0.45), "mond": ((0.78, 0.32, 0.34, 1), 0.5),
        "keel": ((0.25, 0.06, 0.06, 1), 0.6), "tand": ((0.95, 0.93, 0.86, 1), 0.3), "oog": ((0.95, 0.84, 0.18, 1), 0.2), "pupil": ((0.02, 0.02, 0.02, 1), 0.2), "water": ((0.12, 0.16, 0.11, 1), 0.1)}
WATER = -0.15
POS = (16.87, -6.77); YAW = 180.0 + 8.0                       # kop naar het plein


def fuse(bms):
    out = bmesh.new()
    for b_ in bms:
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); out.from_mesh(me_); bpy.data.meshes.remove(me_)
    return out


def schubben(bm, voxel, sm_it, scale_cells, depth, dec):
    """voxel-remesh (unie) -> smooth -> voronoi-displace (schubben) -> decimate"""
    me = bpy.data.meshes.new("_s"); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new("_s", me); bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    rm = o.modifiers.new("r", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = voxel
    sm = o.modifiers.new("s", "SMOOTH"); sm.factor = 0.8; sm.iterations = sm_it
    if depth:
        tx = bpy.data.textures.get("_schub") or bpy.data.textures.new("_schub", "VORONOI"); tx.noise_scale = scale_cells; tx.distance_metric = "DISTANCE"
        tx.color_mode = "INTENSITY"
        dm = o.modifiers.new("d", "DISPLACE"); dm.texture = tx; dm.strength = depth; dm.texture_coords = "OBJECT"; dm.mid_level = 0.5
    dc = o.modifiers.new("dc", "DECIMATE"); dc.ratio = dec
    for m_ in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m_.name)
    out = bmesh.new(); out.from_mesh(o.data); bpy.data.objects.remove(o, do_unlink=True)
    for f in out.faces: f.smooth = True
    return out


def buis(points, r0, r1, segs=10, step=0.08):
    """organische aflopende buis: bollen langs de lijn (wordt samengesmolten)"""
    P = [Vector(p) for p in points]; tot = sum((b - a).length for a, b in zip(P, P[1:])); acc = 0.0; out = []
    for a, b in zip(P, P[1:]):
        L = (b - a).length; k = max(2, int(L / step))
        for i in range(k):
            t = i / k; p = a.lerp(b, t); r = r0 + (r1 - r0) * (acc + L * t) / tot
            out.append(ell(p, (r, r, r), segs, max(6, segs // 2 + 2)))
        acc += L
    return out


def cr(P, n=8):
    P = [Vector(p) for p in P]; P = [P[0]] + P + [P[-1]]; out = []
    for k in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[k - 1], P[k], P[k + 1], P[k + 2]
        for i in range(n):
            t = i / n; out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2]); return out


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    R = random.Random(2016)
    # ---------- lijf: boog van de kop naar achter, duikt het water in ----------
    rug = cr([(0.2, 0, 1.45), (-1.4, 0, 1.75), (-2.9, 0, 1.45), (-4.2, 0, 0.6), (-5.0, 0, -0.6)], 10)
    radii = [1.3, 1.18, 1.0, 0.82, 0.62]
    body = []
    for i, p in enumerate(rug):
        t = i / (len(rug) - 1); r = radii[min(4, int(t * 4))] * (1 - (t * 4 % 1)) + radii[min(4, int(t * 4) + 1)] * (t * 4 % 1)
        body.append(ell(p, (r * 1.0, r * 0.82, r * 0.92), 14, 9))
    # kop: schedel + bovenkaak met opgerolde lip, onderkaak hangt open
    body.append(ell((0.7, 0, 1.75), (1.35, 1.12, 1.0), 18, 12))
    body.append(ell((1.55, 0, 2.0), (0.9, 1.0, 0.55), 16, 10))                                   # bovenkaak
    body.append(ell((1.35, 0, 0.35), (1.05, 0.95, 0.42), 16, 10))                                # onderkaak
    for s in (-1, 1): body.append(ell((0.75, s * 0.78, 2.35), (0.42, 0.32, 0.26), 12, 8))         # wenkbrauwbogen
    for _ in range(170):                                                                          # wratten op kop en rug
        t = R.random(); p = rug[int(t * (len(rug) - 1) * 0.75)].copy()
        a = R.uniform(-1.2, 1.2); rr = 1.05 if t < 0.3 else 0.85
        q = p + Vector((R.uniform(-0.3, 0.3), math.sin(a) * rr * 0.82, math.cos(a) * rr * 0.92))
        if q.z > WATER + 0.3: body.append(ell(q, (R.uniform(0.05, 0.11),) * 3, 8, 6))
    lijf = schubben(fuse(body), 0.045, 3, 0.22, 0.075, 0.2)
    # bek uitsnijden: grote holte voor, zodat de keel zichtbaar is
    mond = ell((2.05, 0, 1.2), (1.25, 0.82, 0.62), 20, 12)
    me1 = bpy.data.meshes.new("_l"); lijf.to_mesh(me1); o1 = bpy.data.objects.new("_l", me1); bpy.context.scene.collection.objects.link(o1)
    me2 = bpy.data.meshes.new("_m"); mond.to_mesh(me2); o2 = bpy.data.objects.new("_m", me2); bpy.context.scene.collection.objects.link(o2)
    bo = o1.modifiers.new("b", "BOOLEAN"); bo.operation = "DIFFERENCE"; bo.object = o2; bo.solver = "EXACT"
    bpy.context.view_layer.objects.active = o1; bpy.ops.object.modifier_apply(modifier="b")
    lijf = bmesh.new(); lijf.from_mesh(o1.data); bpy.data.objects.remove(o1, do_unlink=True); bpy.data.objects.remove(o2, do_unlink=True)
    # onder de waterlijn weghalen (geen onzichtbare driehoeken)
    bmesh.ops.delete(lijf, geom=[v for v in lijf.verts if v.co.z < WATER - 0.35], context="VERTS")
    put("lijf", "visoranje", lijf)
    # keel en tong
    put("bek", "keel", ell((1.25, 0, 1.15), (0.5, 0.62, 0.55), 14, 10))
    put("bek", "mond", ell((1.55, 0, 0.72), (0.75, 0.6, 0.18), 14, 8))
    # lippen: dikke opgerolde rand rond de bek
    rand = [(1.95 + 0.25 * math.cos(a) ** 2, 0.86 * math.sin(a), 1.22 + 0.62 * math.cos(a) * (1.25 if math.cos(a) > 0 else 1.0)) for a in [i * math.tau / 28 for i in range(29)]]
    rand = [(x, y, z) for (x, y, z) in rand]
    lip = schubben(fuse(buis([(p[0], p[1], p[2]) for p in rand], 0.2, 0.2, 10, 0.07)), 0.04, 6, 0.3, 0.0, 0.25)
    put("bek", "vislicht", lip)
    # tanden: witte haaktanden boven (naar beneden) en onder (naar boven)
    for i in range(1, 28):
        a = i * math.tau / 28; x, y, z = rand[i]
        boven = math.cos(a) > 0
        L = R.uniform(0.18, 0.36) * (1.25 if abs(y) < 0.4 else 1.0)
        dirz = -1 if boven else 1
        base = Vector((x - 0.12, y * 0.92, z + dirz * 0.12))
        tip = base + Vector((0.08, -y * 0.08, dirz * L))
        put("bek", "tand", btube([base, base.lerp(tip, 0.6) + Vector((0.04, 0, 0)), tip], 0.055, 6) if False else cone(base, tip, 0.065))
    # ogen: gele bol met spleetpupil, half onder de wenkbrauw
    for s in (-1, 1):
        c = Vector((1.0, s * 0.88, 2.12))
        put("ogen", "oog", ell(c, (0.24, 0.24, 0.26), 14, 10))
        put("ogen", "pupil", ell(c + Vector((0.2, s * 0.08, 0)), (0.04, 0.05, 0.15), 8, 6))
    # tentakels met knopjes op de kop (Pinokkiohelevis)
    for k in range(13):
        a = (k / 12 - 0.5) * 2.0; base = Vector((0.4 - abs(a) * 0.4 + R.uniform(-0.2, 0.2), a * 0.55, 2.55 - abs(a) * 0.25))
        L = R.uniform(0.9, 1.6); up = Vector((R.uniform(-0.5, 0.2), a * 0.35, 1.0)).normalized()
        p1 = base + up * L * 0.5 + Vector((R.uniform(-0.2, 0.2), 0, 0)); p2 = base + up * L + Vector((R.uniform(-0.35, 0.1), R.uniform(-0.15, 0.15), -0.1))
        pts = cr([base, p1, p2], 5)
        t = schubben(fuse(buis(pts, 0.11, 0.045, 8, 0.05) + [ell(p2, (0.07, 0.07, 0.07), 8, 6)]), 0.03, 3, 0.3, 0.0, 0.3)
        put("tentakels", "vislicht", t)
    # rugvinnen: stekelige waaiers (stralen met knopjes, vlies ertussen) langs de rug (Pinokkio_monstervis_rjj)
    for k in range(7):
        t = 0.2 + k * 0.085; i = int(t * (len(rug) - 1)); p = rug[i]
        if p.z < 0.3: continue
        rr = radii[min(4, int(t * 4))]; basis = p + Vector((0, 0, rr * 0.85))
        n = 5; L0 = 1.0 + 0.5 * math.sin(k * 1.1)
        tips = []
        for j in range(n):
            a = math.radians(-55 + j * 110 / (n - 1)); tip = basis + Vector((math.sin(a) * L0 * 0.9 - 0.25, 0, math.cos(a) * L0))
            tips.append(tip)
            put("vinnen", "vislicht", btube([basis, (basis + tip) / 2 + Vector((0.05, 0, 0.05)), tip], 0.06, 6))
            put("vinnen", "vislicht", ell(tip, (0.075, 0.075, 0.075), 8, 6))
        vl = bmesh.new(); vs = [vl.verts.new(basis)] + [vl.verts.new(tp * 0.92 + basis * 0.08) for tp in tips]
        for j in range(n - 1): vl.faces.new((vs[0], vs[j + 1], vs[j + 2]))
        r_ = bmesh.ops.extrude_face_region(vl, geom=list(vl.faces)); bmesh.ops.translate(vl, vec=(0, 0.05, 0), verts=[g for g in r_["geom"] if isinstance(g, bmesh.types.BMVert)])
        bmesh.ops.recalc_face_normals(vl, faces=vl.faces); put("vinnen", "visoranje", vl)
    # borstvinnen bij de waterlijn
    for s in (-1, 1):
        put("vinnen", "vislicht", schubben(fuse([ell((-0.3, s * 1.15, 0.25), (0.65, 0.12, 0.35), 12, 8), ell((-0.8, s * 1.3, 0.05), (0.45, 0.1, 0.25), 10, 6)]), 0.04, 4, 0.3, 0.0, 0.3))
    # ---------- staart: steekt verderop uit het water en krult om, met waaiervin ----------
    sx, sy = -8.2, 1.8
    staart = cr([(sx + 1.2, sy, -0.7), (sx + 0.3, sy, 0.8), (sx - 0.4, sy, 2.3), (sx - 0.1, sy, 3.3), (sx + 0.7, sy, 3.6), (sx + 1.15, sy, 3.0), (sx + 0.7, sy, 2.45)], 7)
    sb = buis(staart, 0.85, 0.18, 12, 0.07)
    st = schubben(fuse(sb), 0.045, 3, 0.2, 0.065, 0.2)
    bmesh.ops.delete(st, geom=[v for v in st.verts if v.co.z < WATER - 0.35], context="VERTS")
    put("staart", "visoranje", st)
    eind = staart[-1]
    for k in range(5):                                                                            # waaiervin
        a = math.radians(-60 + k * 30); tip = eind + Vector((math.cos(a) * 0.9, 0, math.sin(a) * 0.9 - 0.2))
        put("staart", "vislicht", btube([eind, (eind + tip) / 2 + Vector((0, 0, 0.1)), tip], 0.05, 6))
    vl = bmesh.new(); ring = [eind + Vector((math.cos(math.radians(-60 + k * 7.5)) * 0.85, -0.02, math.sin(math.radians(-60 + k * 7.5)) * 0.85 - 0.2)) for k in range(17)]
    vs = [vl.verts.new(eind)] + [vl.verts.new(p) for p in ring]
    for k in range(16): vl.faces.new((vs[0], vs[k + 1], vs[k + 2]))
    r_ = bmesh.ops.extrude_face_region(vl, geom=list(vl.faces)); bmesh.ops.translate(vl, vec=(0, 0.05, 0), verts=[g for g in r_["geom"] if isinstance(g, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(vl, faces=vl.faces); put("staart", "vislicht", vl)
    # ---------- in het modelframe zetten ----------
    M = Matrix.Translation((POS[0], POS[1], 0)) @ Matrix.Rotation(math.radians(YAW), 4, "Z")
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        ob = new_mesh_object(f"PV_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    V = json.load(open(os.path.join(ROOT, "exports", "decor_extra.json")))["vijver"][:-1]          # waterplaat in de vorm van de vijver
    wb = bmesh.new(); t_ = [wb.verts.new((x, y, WATER)) for x, y in V]; b_ = [wb.verts.new((x, y, WATER - 0.1)) for x, y in V]
    wb.faces.new(t_); wb.faces.new(b_[::-1])
    for i in range(len(V)): wb.faces.new((t_[i], b_[i], b_[(i + 1) % len(V)], t_[(i + 1) % len(V)]))
    bmesh.ops.recalc_face_normals(wb, faces=wb.faces); wb.normal_update()
    if wb.faces[0].normal.z < 0:
        for f in wb.faces: f.normal_flip()
    bmesh.ops.triangulate(wb, faces=[f for f in wb.faces if len(f.verts) > 4], ngon_method="EAR_CLIP")
    ob = new_mesh_object("PV_water__water", wb, "FORMS"); assign(ob, bpy.data.materials["MAT_water"])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": [], "lamps": []}, open(os.path.join(out, "vis_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


def cone(base, tip, r):
    bm = bmesh.new(); d = (tip - base); L = d.length; d.normalize()
    a = d.cross(Vector((0, 0, 1))); a = a if a.length > 1e-3 else d.cross(Vector((1, 0, 0))); a.normalize(); b = d.cross(a)
    ring = [bm.verts.new(base + (a * math.cos(k * math.tau / 7) + b * math.sin(k * math.tau / 7)) * r) for k in range(7)]
    mid = [bm.verts.new(base + d * L * 0.55 + (a * math.cos(k * math.tau / 7) + b * math.sin(k * math.tau / 7)) * r * 0.55) for k in range(7)]
    t = bm.verts.new(tip)
    for k in range(7):
        bm.faces.new((ring[k], ring[(k + 1) % 7], mid[(k + 1) % 7], mid[k])); bm.faces.new((mid[k], mid[(k + 1) % 7], t))
    bm.faces.new(ring[::-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
