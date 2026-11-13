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
        "edelsteen": ((0.06, 0.32, 0.26, 1), 0.2), "vaandel": ((0.02, 0.025, 0.09, 1), 0.7), "oogwit": ((0.85, 0.84, 0.80, 1), 0.3),
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
    add("kant", tube([(0.07 * math.cos(t), -0.062 * math.sin(t), 1.5) for t in [i * math.tau / 24 for i in range(25)]], 0.024, 8, cap=False))
    add("kant", tube([(0.056 * math.cos(t), 0.004 - 0.054 * math.sin(t), 1.585) for t in [i * math.tau / 24 for i in range(25)]], 0.016, 8, cap=False))
    for sx in (-1, 1): add("kant", tube([(sx * 0.055, -0.07, 1.48), (sx * 0.035, -0.115, 1.38), (sx * 0.01, -0.13, 1.3)], [0.02, 0.022, 0.012], 6))
    add("kant", tube([(0.165, -0.025, 1.02), (0.175, -0.035, 0.99)], 0.045, 10)); add("kant", tube([(-0.125, -0.16, 1.12), (-0.115, -0.175, 1.095)], 0.045, 10))
    # pofmouwen
    for sx, c in ((1, (0.20, 0.01, 1.43)), (-1, (-0.20, 0.01, 1.43))): add("stof_rood", ellipsoid(c, (0.082, 0.08, 0.105), 20, 12))
    # medaillon aan ketting
    M = Matrix.Translation((0, -0.142, 1.19)) @ Matrix.Rotation(math.radians(90), 4, "X")
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.075, radius2=0.07, depth=0.015); add("goud", bm, M)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.058, radius2=0.058, depth=0.018); add("zwart", bm, M)
    lion = [(-0.03, -0.04), (0.0, -0.025), (0.03, -0.04), (0.025, 0.0), (0.035, 0.03), (0.015, 0.045), (0.0, 0.025), (-0.02, 0.035), (-0.03, 0.01)]
    bm = bmesh.new(); vs = [bm.verts.new((x, 0.0, z)) for x, z in lion]; f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0, -0.004, 0), verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)])
    add("goud", bm, Matrix.Translation((0, -0.153, 1.19)))
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
    # haar: schouderlang blond, golvend, gezicht vrij
    bm = ellipsoid((0, 0.012, 0), (0.1, 0.112, 0.128), 24, 16)
    kill = [f for f in bm.faces if f.calc_center_median().y < -0.04 and f.calc_center_median().z < 0.085 and abs(f.calc_center_median().x) < 0.08]
    kill += [f for f in bm.faces if f.calc_center_median().z < -0.02 and f.calc_center_median().y < -0.02 and abs(f.calc_center_median().x) < 0.1]
    bmesh.ops.delete(bm, geom=list(set(kill)), context="FACES")
    for v in bm.verts:
        if v.co.z < 0.0 and (v.co.y > -0.03 or abs(v.co.x) > 0.075):                                    # naar beneden tot op de schouders, uitlopend
            t = min(1.0, -v.co.z / 0.12); v.co.z -= t * 0.07; v.co.x *= 1 + 0.25 * t; v.co.y = v.co.y * (1 + 0.15 * t) + 0.01 * t
        v.co.x += 0.004 * math.sin(v.co.z * 60); v.co.y += 0.004 * math.cos(v.co.z * 60)
    for f in bm.faces: f.smooth = True
    sol = bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.012) if hasattr(bmesh.ops, "solidify") else None
    add("haar", bm, Matrix.Translation(hc) @ Matrix.Scale(1.08, 4))
    for k in range(22):                                                         # losse golvende lokken van kruin tot schouder, gezicht vrij
        a = math.radians(-125 + k * 250 / 21)                                   # 0 = achter (+y)
        ca, sa = math.sin(a), math.cos(a); pts = []
        for j in range(15):
            t = j / 14; r = 0.1 + 0.028 * t; z = 0.11 - t * 0.24
            w = 0.004 * math.sin(t * 7 + k * 0.7)
            pts.append(Vector((ca * (r + w), 0.012 + sa * (r + w), z)))
        rads = [0.016 * (1 - 0.55 * (j / 14) ** 2) + 0.004 for j in range(15)]
        add("haar", tube(pts, rads, 8), MH)
    # baret + pluim (pluim aan de rechterkant van de figuur = -X, krult omhoog en naar achter)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=28, radius1=0.125, radius2=0.115, depth=0.055)
    for f in bm.faces: f.smooth = True
    add("zwart", bm, Matrix.Translation((0, 0.0, 1.835)) @ Matrix.Rotation(math.radians(-8), 4, "Y") @ Matrix.Rotation(math.radians(6), 4, "X"))
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=28, radius1=0.135, radius2=0.135, depth=0.012); add("zwart", bm, Matrix.Translation((0, 0, 1.81)))
    for k in range(5):
        a = math.radians(-36 + k * 18); base = Vector((-0.075, 0.03, 1.79))
        pts = [base + Vector((0.11 * math.sin(a) * t + (-0.05 * math.sin(t * 2.6)), 0.06 * t + 0.03 * math.cos(a) * t, 0.22 * math.sin(t * 1.9) + 0.02))
               for t in [i / 9 for i in range(10)]]
        add("stof_rood", tube(pts, [0.018, 0.03, 0.04, 0.046, 0.048, 0.046, 0.042, 0.034, 0.024, 0.01], 12))
    # trompet (goud) schuin omlaag vanuit de rechterhand, vaandel eronder
    mp = Vector((-0.09, -0.2, 1.17)); bell = Vector((-0.42, -0.25, 0.66))
    d = (bell - mp); L = d.length; dn = d.normalized()
    add("goud", tube([mp + dn * (L * t) for t in (0, 0.2, 0.5, 0.8, 0.9, 0.97, 1.0)], [0.009, 0.011, 0.012, 0.016, 0.03, 0.055, 0.07], 12, cap=False))
    side = dn.cross(Vector((0, 1, 0))).normalized()
    top_a = mp + dn * (L * 0.35); top_b = mp + dn * (L * 0.82)
    bm = bmesh.new(); quad = [top_a, top_b, top_b + Vector((0, 0, -0.42)) + side * 0.02, top_a + Vector((0, 0, -0.42))]
    f = bm.faces.new([bm.verts.new(p) for p in quad]); r = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, 0.008, 0), verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    add("vaandel", bm)
    for (p, q) in ((quad[0], quad[1]), (quad[1], quad[2]), (quad[2], quad[3]), (quad[3], quad[0])): add("goud", tube([p, q], 0.008, 5))
    cen = (quad[0] + quad[2]) / 2 + Vector((0, -0.006, 0))                                              # gouden leeuw op het vaandel
    lw = [(-0.08, -0.12), (0.0, -0.08), (0.08, -0.12), (0.07, 0.0), (0.1, 0.09), (0.04, 0.13), (0.0, 0.07), (-0.06, 0.1), (-0.09, 0.03)]
    bm = bmesh.new(); f = bm.faces.new([bm.verts.new(cen + side * x + Vector((0, 0, z))) for x, z in lw]); add("goud", bm)
    for k in range(10):                                                                                 # franje
        p = quad[3].lerp(quad[2], k / 9); add("goud", tube([p, p + Vector((0, 0, -0.05))], 0.005, 4))
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
