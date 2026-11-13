"""03b_heraut Magische Klok: een heraut (betoverde prins, ~2.05 m met pluim) naar Herauten-Efteling-6.jpg / MagischeKlokheraut.jpg,
zes keer geplaatst op de sokkels (posities uit exports/klok_extra.json 'herauten', kijkend naar het plein).
Maten op de frontfoto (408 px/m, voeten 850 px): zoom rok 0.61, riem 0.92, schouders 1.49, kin 1.57, kruin 1.85, baret 1.90, pluim ~2.08.
Lichaam: skin-modifier (benen/armen/romp) + subsurf; kleding, hoofd, haar, baret, pluim, trompet en vaandel als losse vormen.
Houding (rust): rechterhand houdt de trompet schuin omlaag met het vaandel eraan, linkerhand in de zij.
Gebruik: Blender -b -P 03b_heraut.py -- --master AR_MagischeKlok_master.blend (na 03_forms)"""
import bpy, bmesh, sys, os, math, json, random
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OWNER = "phase:03b_heraut"
args = sys.argv[sys.argv.index("--") + 1:]; master = args[args.index("--master") + 1]
bpy.ops.wm.open_mainfile(filepath=master)
for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o, do_unlink=True)
rnd = random.Random(1984)
MATS = {"stof_rood": ((0.42, 0.05, 0.04, 1), 0.7), "zwart": ((0.012, 0.012, 0.014, 1), 0.35), "goud": ((0.80, 0.58, 0.18, 1), 0.3),
        "huid": ((0.78, 0.52, 0.38, 1), 0.55), "haar": ((0.72, 0.52, 0.22, 1), 0.6), "kant": ((0.78, 0.78, 0.76, 1), 0.7),
        "edelsteen": ((0.06, 0.32, 0.26, 1), 0.2), "vaandel": ((0.09, 0.04, 0.22, 1), 0.7), "oranje": ((0.80, 0.38, 0.10, 1), 0.7), "franje": ((0.02, 0.02, 0.07, 1), 0.8), "oogwit": ((0.85, 0.84, 0.80, 1), 0.3),
        "iris": ((0.08, 0.20, 0.45, 1), 0.2), "lip": ((0.55, 0.20, 0.16, 1), 0.5), "riem": ((0.45, 0.06, 0.05, 1), 0.5)}
for n, (c, r) in MATS.items():
    m = bpy.data.materials.get("MAT_" + n) or bpy.data.materials.new("MAT_" + n)
    if bpy.app.version < (5, 0, 0): m.use_nodes = True
    b = next(nd for nd in m.node_tree.nodes if nd.type == "BSDF_PRINCIPLED"); b.inputs["Base Color"].default_value = c; b.inputs["Roughness"].default_value = r
    if n == "goud": b.inputs["Metallic"].default_value = 0.9
    m.diffuse_color = c
PARTS = {}


def add(mat, bm, M=None, smooth=True):
    if M is not None: bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    if smooth:
        for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new("_t"); bm.to_mesh(me); bm.free()
    PARTS.setdefault(mat, bmesh.new()).from_mesh(me); bpy.data.meshes.remove(me)


def ellipsoid(c, r, segs=20, rings=12):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    bmesh.ops.scale(bm, vec=r, verts=bm.verts); bmesh.ops.translate(bm, vec=c, verts=bm.verts); return bm


def tube(pts, rads, segs=10, cap=True):
    bm = bmesh.new(); P = [Vector(p) for p in pts]; rings = []
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        a = t.cross(Vector((0, 0, 1))); a = a.normalized() if a.length > 1e-3 else t.cross(Vector((1, 0, 0))).normalized(); b = t.cross(a)
        r = rads[i] if isinstance(rads, (list, tuple)) else rads
        rings.append([bm.verts.new(p + (a * math.cos(k * math.tau / segs) + b * math.sin(k * math.tau / segs)) * r) for k in range(segs)])
    for A, B in zip(rings, rings[1:]):
        for k in range(segs): bm.faces.new((A[k], A[(k + 1) % segs], B[(k + 1) % segs], B[k]))
    if cap: bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def loft(rings_spec, segs, mat_of_seg=None, closed_top=False, closed_bottom=False):
    """ringen [(z, rx, ry, cy, ruis)] -> per segment een materiaal (strepen); geeft {mat: bm}"""
    out = {}
    R = []
    for z, rx, ry, cy, fold in rings_spec:
        R.append([Vector((rx * math.cos(k * math.tau / segs + math.pi / 2) * (1 + fold * math.cos(8 * k * math.tau / segs)),
                          cy + ry * math.sin(k * math.tau / segs + math.pi / 2) * (1 + fold * math.cos(8 * k * math.tau / segs)) * -1, z)) for k in range(segs)])
    for i in range(len(R) - 1):
        for k in range(segs):
            mat = mat_of_seg(k) if mat_of_seg else "zwart"
            bm = out.setdefault(mat, bmesh.new())
            vs = [bm.verts.new(p) for p in (R[i][k], R[i][(k + 1) % segs], R[i + 1][(k + 1) % segs], R[i + 1][k])]
            bm.faces.new(vs)
    for bm in out.values():
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f in bm.faces: f.smooth = True
    return out


def skin_body():
    """benen + armen + romp via skin-modifier, subsurf 1; alles rood (maillot/mouwen), romp verdwijnt onder de tuniek"""
    J = {"bek": (0, 0, 0.95), "hL": (0.095, 0, 0.92), "hR": (-0.095, 0, 0.92), "kL": (0.105, -0.015, 0.5), "kR": (-0.10, -0.005, 0.5),
         "aL": (0.115, 0.01, 0.1), "aR": (-0.10, 0.015, 0.1), "bo": (0, 0, 1.25), "ne": (0, 0, 1.48),
         "sL": (0.19, 0.01, 1.44), "sR": (-0.19, 0.01, 1.44), "eL": (0.34, 0.07, 1.17), "eR": (-0.27, -0.06, 1.17),
         "wL": (0.17, -0.03, 0.97), "wR": (-0.11, -0.17, 1.09)}
    R = {"bek": (0.15, 0.11), "hL": (0.085, 0.085), "hR": (0.085, 0.085), "kL": (0.052, 0.055), "kR": (0.052, 0.055), "aL": (0.037, 0.04), "aR": (0.037, 0.04),
         "bo": (0.16, 0.11), "ne": (0.052, 0.052), "sL": (0.07, 0.07), "sR": (0.07, 0.07), "eL": (0.045, 0.045), "eR": (0.045, 0.045), "wL": (0.033, 0.033), "wR": (0.033, 0.033)}
    E = [("bek", "hL"), ("bek", "hR"), ("hL", "kL"), ("hR", "kR"), ("kL", "aL"), ("kR", "aR"), ("bek", "bo"), ("bo", "ne"), ("bo", "sL"), ("bo", "sR"),
         ("sL", "eL"), ("sR", "eR"), ("eL", "wL"), ("eR", "wR")]
    names = list(J); me = bpy.data.meshes.new("_skin"); me.from_pydata([J[n] for n in names], [(names.index(a), names.index(b)) for a, b in E], [])
    ob = bpy.data.objects.new("_skin", me); bpy.context.scene.collection.objects.link(ob)
    sk = ob.modifiers.new("skin", "SKIN"); sk.use_smooth_shade = True
    sv = me.skin_vertices[0].data
    for i, n in enumerate(names): sv[i].radius = R[n]
    sv[names.index("bek")].use_root = True
    # kuit: extra punt tussen knie en enkel voor de bolling
    ob.modifiers.new("sub", "SUBSURF").levels = 2
    dg = bpy.context.evaluated_depsgraph_get(); m2 = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob); bm = bmesh.new(); bm.from_mesh(m2); bpy.data.meshes.remove(m2)
    for v in bm.verts:                                                          # kuiten voller, dijen iets breder
        z = v.co.z
        if 0.18 < z < 0.45: s = 1 + 0.25 * math.sin((z - 0.18) / 0.27 * math.pi); v.co.x = math.copysign(abs(v.co.x - math.copysign(0.105, v.co.x)) * s, v.co.x - math.copysign(0.105, v.co.x)) + math.copysign(0.105, v.co.x); v.co.y *= 1 + 0.15 * (s - 1)
    bm.normal_update()
    for v in bm.verts:                                                          # kreukels in de mouwen (Herauten-Efteling-6)
        if v.co.z > 0.96 and abs(v.co.x) > 0.13:
            v.co += v.normal * (0.006 * math.sin(v.co.z * 85 + v.co.x * 30) + 0.003 * math.sin(v.co.z * 190))
    for f in bm.faces: f.smooth = True
    return bm


def g(a, b, s): return math.exp(-((a - b) / s) ** 2)


LEEUW = [(0.35, 0.95), (0.55, 0.85), (0.6, 0.7), (0.78, 0.78), (0.72, 0.55), (0.5, 0.5), (0.55, 0.35), (0.82, 0.32), (0.76, 0.14), (0.45, 0.15),
         (0.35, -0.1), (0.45, -0.45), (0.72, -0.72), (0.56, -0.95), (0.2, -0.7), (0.0, -0.42), (-0.2, -0.75), (-0.36, -0.95), (-0.52, -0.84),
         (-0.3, -0.5), (-0.2, -0.1), (-0.45, 0.0), (-0.75, 0.3), (-0.82, 0.72), (-0.6, 0.92), (-0.66, 0.6), (-0.5, 0.36), (-0.25, 0.25),
         (-0.1, 0.5), (0.05, 0.75), (0.2, 0.92)]   # klimmende Brabantse leeuw (vaandel + medaillon), kop rechtsboven, staart links


def plaat(poly, o, e1, e2, nrm, sx, sz, dikte):
    """vlakke uitgesneden vorm (concaaf mag) in het vlak e1/e2 rond o, dikte langs nrm"""
    bm = bmesh.new(); vs = [bm.verts.new(o + e1 * (x * sx) + e2 * (z * sz)) for x, z in poly]; f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=nrm * dikte, verts=[v for v in r["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="EAR_CLIP"); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def kant_ring(c, ax, r0, r1, ln, n=28, schulp=10, golf=0.12):
    """uitlopende kanten kraag/manchet: ring r0 op c naar r1 op c+ax*ln, geschulpte rand, iets golvend, dubbelzijdig"""
    ax = Vector(ax).normalized(); a = ax.cross(Vector((0, 0, 1))); a = a.normalized() if a.length > 1e-3 else Vector((1, 0, 0)); b = ax.cross(a)
    bm = bmesh.new(); R = []
    for j in range(4):
        t = j / 3; ring = []
        for k in range(n):
            ang = k * math.tau / n; r = r0 + (r1 - r0) * t; r *= 1 + golf * t * math.sin(ang * 6)
            l = ln * t * (1 - 0.18 * t * (0.5 + 0.5 * math.cos(ang * schulp)))
            ring.append(bm.verts.new(Vector(c) + ax * l + (a * math.cos(ang) + b * math.sin(ang)) * r))
        R.append(ring)
    for A, B in zip(R, R[1:]):
        for k in range(n): bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.005); return bm


def hand(wrist, fwd, palm_n, curl, thumb_curl=0.4):
    """hand met handpalm, 4 vingers (3 kootjes) en duim; fwd = richting van de vingers, palm_n = normaal van de handpalm"""
    fwd = Vector(fwd).normalized(); pn = Vector(palm_n); pn = (pn - fwd * pn.dot(fwd)).normalized(); sd = fwd.cross(pn)
    W = Vector(wrist); out = []
    R = Matrix((sd, pn, fwd)).transposed()
    pb = ellipsoid((0, 0, 0), (0.04, 0.017, 0.048), 14, 10); bmesh.ops.transform(pb, matrix=Matrix.Translation(W + fwd * 0.045) @ R.to_4x4(), verts=pb.verts); out.append(pb)
    for i, (off, ln) in enumerate(((-0.027, 0.075), (-0.009, 0.085), (0.009, 0.08), (0.026, 0.065))):
        p = W + fwd * 0.088 + sd * off; d = fwd.copy(); pts = [p.copy()]
        for j in range(3):
            ang = curl * (0.8 + 0.2 * j); d = (d * math.cos(ang) - pn * math.sin(ang)).normalized(); p = p + d * (ln / 3); pts.append(p.copy())
        out.append(tube(pts, [0.0095, 0.009, 0.008, 0.007], 7))
    p = W + fwd * 0.035 + sd * 0.035 - pn * 0.005; d = (fwd * 0.5 + sd * 0.7 - pn * 0.3).normalized(); pts = [p.copy()]
    for j in range(2):
        d = (d * math.cos(thumb_curl) - pn * math.sin(thumb_curl)).normalized(); p = p + d * 0.03; pts.append(p.copy())
    out.append(tube(pts, [0.011, 0.0095, 0.008], 7))
    return out


def herald():
    global PARTS
    PARTS = {}
    add("stof_rood", skin_body())
    # ---- tuniek: lijfje + uitlopende rok, verticale strepen zwart/goud (breder zwart), gouden zoom
    stripe = lambda k: "goud" if k % 2 else "zwart"
    body = loft([(0.61, 0.245, 0.20, 0.0, 0.05), (0.70, 0.215, 0.175, 0.0, 0.04), (0.82, 0.185, 0.145, 0.0, 0.022), (0.93, 0.165, 0.125, 0.0, 0.005),
                 (1.08, 0.175, 0.13, -0.005, 0.0), (1.25, 0.20, 0.14, -0.01, 0.0), (1.40, 0.205, 0.13, 0.0, 0.0), (1.47, 0.12, 0.09, 0.0, 0.0), (1.50, 0.06, 0.055, 0.0, 0.0)],
                24, stripe)
    for m_, bm in body.items(): add(m_, bm)
    add("goud", tube([(0.245 * math.cos(t) * (1 + 0.05 * math.cos(8 * t)), -0.20 * math.sin(t) * (1 + 0.05 * math.cos(8 * t)), 0.625) for t in [i * math.tau / 48 for i in range(49)]], 0.018, 6, cap=False))
    # riem met groene stenen en gesp
    add("riem", loft([(0.895, 0.175, 0.135, 0, 0), (0.955, 0.175, 0.135, 0, 0)], 32)["zwart"])
    for k in range(-2, 3):
        a = math.radians(90 + k * 26); add("edelsteen", ellipsoid((0.178 * math.cos(a), -0.138 * math.sin(a), 0.925), (0.022, 0.012, 0.016), 8, 6))
    # kanten V-kraag + manchetten
    # grote kanten kraag (Intro_magischeklok): ligt over de schouders, loopt voor in een V naar beneden, geschulpte rand
    bm = bmesh.new(); RI, RO = [], []
    for k in range(36):
        a = k * math.tau / 36; fr = max(0.0, -math.sin(a)) ** 3                    # voorkant (-Y)
        sch = 0.012 * (0.5 + 0.5 * math.cos(a * 18))
        RI.append(bm.verts.new((0.062 * math.cos(a), 0.058 * math.sin(a) - 0.002, 1.56 - 0.02 * fr)))
        RO.append(bm.verts.new(((0.15 - 0.07 * fr + sch) * math.cos(a), (0.13 + 0.02 * fr + sch) * math.sin(a), 1.47 - 0.13 * fr + 0.01 * math.cos(a * 18))))
    for k in range(36): bm.faces.new((RI[k], RI[(k + 1) % 36], RO[(k + 1) % 36], RO[k]))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.006); add("kant", bm)
    add("kant", kant_ring((0.0, 0.004, 1.585), (0, 0, -1), 0.054, 0.062, 0.03, 24, 12, 0.05))                     # opstaand randje
    add("kant", kant_ring((0.162, -0.028, 1.035), (0.06, -0.06, -0.99), 0.04, 0.068, 0.07, 24, 10))               # manchetten, wijd uitlopend over de hand
    add("kant", kant_ring((-0.145, -0.148, 1.106), (0.16, -0.11, -0.08), 0.04, 0.068, 0.07, 24, 10))
    # pofmouwen
    for sx, c in ((1, (0.20, 0.01, 1.43)), (-1, (-0.20, 0.01, 1.43))): add("stof_rood", ellipsoid(c, (0.082, 0.08, 0.105), 20, 12))
    # medaillon aan ketting
    M = Matrix.Translation((0, -0.142, 1.19)) @ Matrix.Rotation(math.radians(90), 4, "X")
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.088, radius2=0.083, depth=0.016); add("goud", bm, M)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.068, radius2=0.068, depth=0.018); add("zwart", bm, M)
    add("goud", plaat(LEEUW, Vector((0, -0.151, 1.19)), Vector((-1, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0)), 0.05, 0.052, 0.005))
    add("goud", tube([(-0.07, -0.05, 1.49), (-0.06, -0.12, 1.33), (-0.02, -0.145, 1.26), (0, -0.145, 1.265)], 0.007, 5, cap=False))
    add("goud", tube([(0.07, -0.05, 1.49), (0.06, -0.12, 1.33), (0.02, -0.145, 1.26), (0, -0.145, 1.265)], 0.007, 5, cap=False))
    # handen (huid): linker in de zij, rechter om de trompet
    for bm in hand((0.168, -0.035, 0.975), (-0.25, -0.55, -0.8), (-1, 0.2, 0), 0.25, 0.3): add("huid", bm)        # in de zij
    for bm in hand((-0.105, -0.165, 1.095), (0.05, -0.75, -0.25), (-0.6, -0.2, 0.75), 1.15, 0.9): add("huid", bm)  # om de trompet
    # schoenen: zwart, puntig (Herauten-Efteling-6)
    for sx, rot in ((1, 18), (-1, -8)):
        bm = ellipsoid((0, -0.07, 0.045), (0.048, 0.15, 0.048), 20, 10)
        for v in bm.verts:
            if v.co.y < -0.12: v.co.z += (-0.12 - v.co.y) * 0.3; v.co.x *= max(0.12, 1 - (-0.12 - v.co.y) * 7)
            if v.co.z < 0.0: v.co.z = 0.0
        bm2 = tube([(0, 0.0, 0.03), (0, 0.0, 0.13)], [0.046, 0.04], 14)
        me = bpy.data.meshes.new("_s"); bm2.to_mesh(me); bm2.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
        kx = 0.115 if sx > 0 else -0.10
        add("zwart", bm, Matrix.Translation((kx, 0.01, 0)) @ Matrix.Rotation(math.radians(rot), 4, "Z"))
    # ---- hoofd
    hc = Vector((0, -0.01, 1.70)); MH = Matrix.Translation(hc) @ Matrix.Scale(1.08, 4)
    bm = ellipsoid((0, 0, 0), (0.088, 0.105, 0.122), 36, 26)
    for v in bm.verts:                                                          # gezicht modelleren (Herauten-Efteling-6: smal, rechte neus, volle lippen)
        x, y, z = v.co
        if z < 0: x *= 1 - 0.28 * (-z / 0.122) ** 1.5; y *= 1 - 0.12 * (-z / 0.122)
        f = max(0.0, -y / 0.105) ** 2; ax = abs(x)
        y += f * 0.009 * g(ax, 0.035, 0.017) * g(z, 0.022, 0.014)              # oogkassen
        y -= f * 0.006 * g(z, 0.047, 0.012) * g(ax, 0.035, 0.03)                # wenkbrauwboog
        y -= f * 0.026 * g(x, 0, 0.011) * g(z, -0.008, 0.032)                   # neus
        y -= f * 0.008 * g(ax, 0.013, 0.008) * g(z, -0.036, 0.01)               # neusvleugels
        y -= f * 0.006 * g(ax, 0.056, 0.02) * g(z, 0.0, 0.02); x *= 1 + 0.04 * g(z, 0.0, 0.03)   # jukbeenderen
        y += f * 0.004 * g(x, 0, 0.026) * g(z, -0.06, 0.005)                    # mondspleet
        y -= f * 0.005 * g(x, 0, 0.022) * (g(z, -0.053, 0.007) + g(z, -0.068, 0.007))   # lippen
        y -= f * 0.011 * g(x, 0, 0.026) * g(z, -0.106, 0.016)                   # kin
        v.co = Vector((x, y, z))
    add("huid", bm, MH)
    add("huid", tube([(0, 0, 1.47), (0, -0.005, 1.6)], 0.05, 12))                                     # hals
    for sx in (-1, 1):
        add("oogwit", ellipsoid((sx * 0.035, -0.081, 0.022), (0.013, 0.012, 0.011), 12, 8), MH)
        add("iris", ellipsoid((sx * 0.035, -0.0925, 0.022), (0.0065, 0.002, 0.0065), 10, 6), MH)
        add("haar", tube([(sx * 0.054, -0.088, 0.046), (sx * 0.035, -0.1, 0.052), (sx * 0.014, -0.102, 0.047)], 0.004, 5), MH)
    add("lip", ellipsoid((0, -0.093, -0.06), (0.021, 0.006, 0.0075), 12, 6), MH)
    # haar: schouderlang blond, vol en golvend tot op de kraag (Intro_magischeklok / MagischeKlokheraut), gezicht vrij
    bm = ellipsoid((0, 0.012, 0), (0.1, 0.112, 0.128), 24, 16)
    kill = [f for f in bm.faces if f.calc_center_median().y < -0.04 and f.calc_center_median().z < 0.085 and abs(f.calc_center_median().x) < 0.08]
    kill += [f for f in bm.faces if f.calc_center_median().z < -0.02 and f.calc_center_median().y < -0.02 and abs(f.calc_center_median().x) < 0.1]
    bmesh.ops.delete(bm, geom=list(set(kill)), context="FACES")
    for v in bm.verts:
        if v.co.z < 0.0 and (v.co.y > -0.03 or abs(v.co.x) > 0.075):                                    # naar beneden tot op de schouders, uitlopend
            t = min(1.0, -v.co.z / 0.12); v.co.z -= t * 0.12; v.co.x *= 1 + 0.38 * t; v.co.y = v.co.y * (1 + 0.25 * t) + 0.015 * t
        v.co.x += 0.005 * math.sin(v.co.z * 55); v.co.y += 0.005 * math.cos(v.co.z * 55)
    for f in bm.faces: f.smooth = True
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.012)
    add("haar", bm, Matrix.Translation(hc) @ Matrix.Scale(1.08, 4))
    for k in range(32):                                                         # dikke golvende lokken van kruin tot op de kraag, eind iets naar buiten
        a = math.radians(-118 + k * 236 / 31)                                   # 0 = achter (+y)
        ca, sa = math.sin(a), math.cos(a); voor = max(0.0, (abs(math.degrees(a)) - 80) / 40); pts = []
        zend = -0.25 + 0.06 * voor
        for j in range(17):
            t = j / 16; r = 0.102 + 0.055 * t ** 1.3 + 0.025 * max(0.0, t - 0.8) / 0.2
            w = 0.022 * math.sin(t * 8 + k * 1.9) * (0.3 + 0.7 * t)
            pts.append(Vector((ca * (r + w), 0.012 + sa * (r + w) + 0.02 * t * (1 - voor), 0.11 - t * (0.11 - zend))))
        rads = [0.022 * (1 - 0.55 * (j / 16) ** 2) + 0.006 for j in range(17)]
        add("haar", tube(pts, rads, 8), MH)
    # baret: zachte, platte zwarte baret, iets scheef naar achter (foto), met band
    bm = ellipsoid((0, 0, 0), (0.14, 0.145, 0.058), 32, 14)
    for v in bm.verts:
        if v.co.z < 0: v.co.z *= 0.7; v.co.x *= 0.92 + 0.08 * (1 + v.co.z / 0.058); v.co.y *= 0.92 + 0.08 * (1 + v.co.z / 0.058)
    add("zwart", bm, Matrix.Translation((0.004, 0.014, 1.835)) @ Matrix.Rotation(math.radians(-7), 4, "Y") @ Matrix.Rotation(math.radians(9), 4, "X"))
    add("zwart", tube([(0.112 * math.cos(t), 0.008 + 0.118 * math.sin(t), 1.8 + 0.012 * math.sin(t)) for t in [i * math.tau / 40 for i in range(41)]], 0.013, 8, cap=False))
    # pluim: dikke rozet van gekrulde donkerrode veren boven op de baret, voor/midden (Intro_magischeklok)
    C = Vector((-0.015, 0.0, 1.885)); Z = Vector((0, 0, 1))
    for c_, r_ in (((0, 0, 0.0), (0.06, 0.06, 0.045)), ((0.035, 0.02, 0.01), (0.045, 0.045, 0.04)), ((-0.04, 0.025, 0.012), (0.045, 0.045, 0.04)),
                   ((0.0, -0.04, 0.0), (0.045, 0.04, 0.035)), ((0.0, 0.05, 0.02), (0.04, 0.045, 0.035))):
        add("stof_rood", ellipsoid(C + Vector(c_) * 1.25, tuple(x * 1.25 for x in r_), 14, 9))
    for k in range(18):
        phi = k * 2.39996; rd = Vector((math.cos(phi), math.sin(phi), 0)); b = C + rd * (0.012 + 0.03 * ((k * 7) % 5) / 4) + Z * 0.02
        rr0 = 0.062 + 0.022 * ((k * 3) % 4) / 3; pts = []
        for j in range(13):
            t = j / 12; ang = -0.2 + t * 4.0; rr = rr0 * (1 - 0.5 * t)
            pts.append(b + rd * (0.03 * t + rr * math.sin(ang)) + Z * (rr * (1 - math.cos(ang)) * 0.75))
        add("stof_rood", tube(pts, [0.01, 0.018, 0.024, 0.026, 0.026, 0.024, 0.021, 0.018, 0.015, 0.012, 0.009, 0.006, 0.003], 10))
    # trompet (goud) schuin omlaag vanuit de rechterhand, grote beker
    mp = Vector((-0.09, -0.2, 1.17)); bell = Vector((-0.42, -0.25, 0.66))
    d = (bell - mp); L = d.length; dn = d.normalized()
    add("goud", tube([mp + dn * (L * t) for t in (0, 0.2, 0.5, 0.78, 0.88, 0.95, 0.99, 1.0)], [0.01, 0.012, 0.013, 0.017, 0.03, 0.058, 0.085, 0.092], 16, cap=False))
    add("goud", tube([mp + dn * (L * 0.62), mp + dn * (L * 0.64)], 0.02, 12))                       # ring
    # vaandel (Intro_magischeklok): hangt recht onder de trompet, paars met gouden klimmende leeuw, brede oranje rand, donkere franje
    hd = Vector((dn.x, dn.y, 0)).normalized(); nrm = Vector((hd.y, -hd.x, 0)); top = mp + dn * (L * 0.58) + nrm * 0.03
    W2, H = 0.135, 0.33; e1 = hd; e2 = Vector((0, 0, 1))
    rect = lambda w, h: [(-w, 0), (w, 0), (w, -h), (-w, -h)]
    add("oranje", plaat(rect(1, 1), top - nrm * 0.004, e1, e2, nrm, W2, H, 0.008), smooth=False)
    for sg in (-1, 1):
        o = top + e2 * -0.028 + nrm * (0.0045 * sg) - nrm * (0.0 if sg > 0 else 0.0)
        add("vaandel", plaat(rect(1, 1), o, e1, e2, nrm * sg, W2 - 0.028, H - 0.056, 0.002), smooth=False)
        add("goud", plaat(LEEUW, top + e2 * (-H / 2) + nrm * (0.0065 * sg), e1 * (sg * -1), e2, nrm * sg, 0.085, 0.11, 0.002), smooth=False)
    for k in range(28):                                                                                 # franje
        p = top + e1 * (-W2 + 2 * W2 * k / 27) + e2 * -H
        add("franje", tube([p, p + Vector((0.002 * math.sin(k), 0, -0.06))], 0.0045, 4), smooth=False)
    add("goud", tube([top + e1 * -(W2 + 0.02), top + e1 * (W2 + 0.02)], 0.007, 8))                    # stok
    for sg in (-1, 1):                                                                                   # lussen om de trompet
        q = top + e1 * (sg * W2 * 0.7); tp = mp + dn * (L * (0.58 + sg * 0.7 * W2 / L / max(0.2, hd.dot(dn))))
        add("oranje", tube([q, q.lerp(tp, 0.5) - nrm * 0.01, tp], 0.008, 6))
    return {m: bm for m, bm in PARTS.items()}


H = herald()
info = json.load(open(os.path.join(ROOT, "exports", "klok_extra.json")))
col = bpy.data.collections["FORMS"]; tris = 0
for i, (x, y, z, ang, arm) in enumerate(info["herauten"]):
    M = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(ang + 90), 4, "Z")   # figuur kijkt naar -Y -> draaien naar de plein-normaal
    for mat, src in H.items():
        bm = src.copy(); bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        me = bpy.data.meshes.new(f"MK_heraut{i}_{mat}"); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(f"MK_heraut{i}_{mat}__{mat}", me); col.objects.link(ob); ob["owner"] = OWNER
        ob.data.materials.append(bpy.data.materials["MAT_" + mat]); tris += sum(len(p.vertices) - 2 for p in me.polygons)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=master)
print("[03b_heraut] herauten", len(info["herauten"]), "tris", tris)
