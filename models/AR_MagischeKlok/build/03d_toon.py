"""03d_toon Magische Klok: Slimme Toon (Slimme-Toon.jpg 2016 + SlimmeToonontwerp.jpg, Pieck 'schaal 1:2').
Zit op de krul van de klokkenstoel linksvoor (gezien vanaf het plein), benen naar de klok, trekt met beide handen aan het klokkentouw.
Groen jak met rode kraag en rode riem, rode maillot, zwarte puntschoenen, blond pagekopje, grijsgroen hoedje met omgeslagen rand en
rode krulveer. Op de foto even hoog als de klok (~0.42 m van zitvlak tot hoedje), zitvlak ~0.1 m boven de loden trommel.
Wereldmaten na 03_forms (K = 0.87, zmap): trommel-top z 6.68, krulstijlen op r 0.435 (45/135/225/315 graden), klok 6.86..7.25.
Lichaam: skin-modifier (benen rood, romp + armen groen) + subsurf; kleding/hoofd/hoed als losse vormen (zoals 03b_heraut).
Gebruik: Blender -b -P 03d_toon.py -- --master AR_MagischeKlok_master.blend (na 03_forms)"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OWNER = "phase:03d_toon"
args = sys.argv[sys.argv.index("--") + 1:]; master = args[args.index("--master") + 1]
bpy.ops.wm.open_mainfile(filepath=master)
for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o, do_unlink=True)
MATS = {"toon_groen": ((0.25, 0.42, 0.36, 1), 0.7), "toon_rood": ((0.70, 0.30, 0.22, 1), 0.7), "huid": ((0.85, 0.66, 0.52, 1), 0.6),
        "haar": ((0.80, 0.62, 0.30, 1), 0.7), "zwart": ((0.012, 0.012, 0.014, 1), 0.35), "toon_hoed": ((0.20, 0.27, 0.26, 1), 0.7),
        "kant": ((0.78, 0.78, 0.76, 1), 0.7), "oogwit": ((0.85, 0.84, 0.80, 1), 0.3), "iris": ((0.08, 0.20, 0.45, 1), 0.2)}
for n, (c, r) in MATS.items():
    m = bpy.data.materials.get("MAT_" + n) or bpy.data.materials.new("MAT_" + n)
    if bpy.app.version < (5, 0, 0): m.use_nodes = True
    b = next(nd for nd in m.node_tree.nodes if nd.type == "BSDF_PRINCIPLED"); b.inputs["Base Color"].default_value = c; b.inputs["Roughness"].default_value = r
    m.diffuse_color = c
PARTS = {}


def add(mat, bm, M=None, smooth=True):
    if M is not None: bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    if smooth:
        for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new("_t"); bm.to_mesh(me); bm.free()
    PARTS.setdefault(mat, bmesh.new()).from_mesh(me); bpy.data.meshes.remove(me)


def ellipsoid(c, r, segs=16, rings=10):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    bmesh.ops.scale(bm, vec=r, verts=bm.verts); bmesh.ops.translate(bm, vec=c, verts=bm.verts); return bm


def tube(pts, rads, segs=8, cap=True):
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


def loft(rings_spec, segs=20):
    """ringen [(z, rx, ry, cy)] -> gesloten mantel (boven/onder dicht)"""
    bm = bmesh.new(); R = []
    for z, rx, ry, cy in rings_spec:
        R.append([bm.verts.new((rx * math.cos(k * math.tau / segs), cy + ry * math.sin(k * math.tau / segs), z)) for k in range(segs)])
    for A, B in zip(R, R[1:]):
        for k in range(segs): bm.faces.new((A[k], A[(k + 1) % segs], B[(k + 1) % segs], B[k]))
    bm.faces.new(R[0][::-1]); bm.faces.new(R[-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def skin(J, R, E, root, sub=2):
    names = list(J); me = bpy.data.meshes.new("_skin"); me.from_pydata([J[n] for n in names], [(names.index(a), names.index(b)) for a, b in E], [])
    ob = bpy.data.objects.new("_skin", me); bpy.context.scene.collection.objects.link(ob)
    sk = ob.modifiers.new("skin", "SKIN"); sk.use_smooth_shade = True
    sv = me.skin_vertices[0].data
    for i, n in enumerate(names): sv[i].radius = R[n]
    sv[names.index(root)].use_root = True
    ob.modifiers.new("sub", "SUBSURF").levels = sub
    dg = bpy.context.evaluated_depsgraph_get(); m2 = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob); bm = bmesh.new(); bm.from_mesh(m2); bpy.data.meshes.remove(m2); return bm


def toon():
    """lokaal: zitvlak in de oorsprong, kijkt naar -Y, Z op, ongeschaald ~0.31 m hoog (wordt x1.35)"""
    # benen (rood): dijen vooruit, onderbenen hangen schuin omlaag over de trommelrand (links iets verder gestrekt, zoals de foto)
    J = {"bek": (0, 0.0, 0.03), "hL": (0.035, -0.005, 0.025), "hR": (-0.035, -0.005, 0.025), "kL": (0.042, -0.125, 0.03), "kR": (-0.04, -0.115, 0.045),
         "aL": (0.046, -0.205, -0.065), "aR": (-0.046, -0.175, -0.05)}
    R = {"bek": (0.036, 0.03), "hL": (0.03, 0.03), "hR": (0.03, 0.03), "kL": (0.021, 0.021), "kR": (0.021, 0.021), "aL": (0.015, 0.015), "aR": (0.015, 0.015)}
    add("toon_rood", skin(J, R, [("bek", "hL"), ("bek", "hR"), ("hL", "kL"), ("hR", "kR"), ("kL", "aL"), ("kR", "aR")], "bek"))
    # romp + armen (groen): armen omhoog naar voren, handen boven elkaar om het touw
    J = {"bek": (0, 0.005, 0.04), "bo": (0, 0.008, 0.12), "ne": (0, 0.01, 0.19), "sL": (0.05, 0.01, 0.175), "sR": (-0.05, 0.01, 0.175),
         "eL": (0.062, -0.06, 0.145), "eR": (-0.06, -0.055, 0.17), "wL": (0.012, -0.125, 0.205), "wR": (-0.01, -0.13, 0.25)}
    R = {"bek": (0.04, 0.03), "bo": (0.042, 0.03), "ne": (0.014, 0.014), "sL": (0.018, 0.018), "sR": (0.018, 0.018), "eL": (0.013, 0.013),
         "eR": (0.013, 0.013), "wL": (0.01, 0.01), "wR": (0.01, 0.01)}
    add("toon_groen", skin(J, R, [("bek", "bo"), ("bo", "ne"), ("bo", "sL"), ("bo", "sR"), ("sL", "eL"), ("sR", "eR"), ("eL", "wL"), ("eR", "wR")], "bek"))
    # jak: wijd uitlopende rok over de dijen (ontwerp: groen jak tot halverwege de dij), getailleerd, schouders
    add("toon_groen", loft([(-0.005, 0.072, 0.085, -0.045), (0.03, 0.062, 0.058, -0.02), (0.06, 0.042, 0.034, 0.0), (0.11, 0.044, 0.032, 0.004),
                            (0.165, 0.05, 0.03, 0.008), (0.19, 0.032, 0.022, 0.01), (0.198, 0.012, 0.012, 0.01)], 24))
    # rode riem en grote rode puntkraag (foto + ontwerp)
    add("toon_rood", loft([(0.052, 0.045, 0.037, 0.0), (0.064, 0.045, 0.037, 0.0)], 24))
    bm = bmesh.new(); ring_i = []; ring_o = []
    for k in range(24):
        a = k * math.tau / 24; pt = 1.0 + 0.6 * max(0.0, math.cos(4 * a)) ** 6        # vier punten
        ring_i.append(bm.verts.new((0.016 * math.cos(a), 0.01 + 0.016 * math.sin(a), 0.205)))
        ring_o.append(bm.verts.new((0.05 * pt * math.cos(a), 0.01 + 0.042 * pt * math.sin(a), 0.172)))
    for k in range(24): bm.faces.new((ring_i[k], ring_i[(k + 1) % 24], ring_o[(k + 1) % 24], ring_o[k]))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.004); add("toon_rood", bm)
    # handen + touwgrepen, schoenen (puntig, zwart)
    for w in ((0.012, -0.13, 0.208), (-0.01, -0.135, 0.253)): add("huid", ellipsoid(w, (0.011, 0.013, 0.012), 10, 6))
    for a, d in (((0.046, -0.205, -0.065), (0.0, -0.06, -0.012)), ((-0.046, -0.175, -0.05), (0.0, -0.06, -0.02))):
        A = Vector(a); D = Vector(d); add("zwart", tube([A + Vector((0, 0.01, 0)), A + D * 0.4, A + D * 0.8, A + D + Vector((0, 0, 0.012))], [0.014, 0.016, 0.01, 0.003], 8))
    # hoofd: iets naar voren gebogen, kijkt naar de klok; neus, oogjes
    hc = Vector((0, -0.012, 0.236))
    add("huid", ellipsoid(hc, (0.031, 0.034, 0.039), 18, 12)); add("huid", ellipsoid(hc + Vector((0, -0.033, -0.004)), (0.006, 0.008, 0.009), 8, 6))
    for sx in (-1, 1):
        add("oogwit", ellipsoid(hc + Vector((sx * 0.012, -0.03, 0.006)), (0.006, 0.003, 0.004), 8, 5))
        add("iris", ellipsoid(hc + Vector((sx * 0.012, -0.032, 0.006)), (0.003, 0.002, 0.003), 6, 4))
    add("huid", ellipsoid(Vector((0, 0.002, 0.198)), (0.012, 0.012, 0.016), 8, 6))                    # hals
    # blond pagekopje: kap over het hoofd, gezicht vrij, onderrand in krullen tot net boven de kraag
    bm = ellipsoid(hc + Vector((0, 0.006, 0.004)), (0.036, 0.039, 0.042), 22, 14)
    dead = [f for f in bm.faces if (f.calc_center_median().y < hc.y - 0.012 and f.calc_center_median().z < hc.z + 0.024) or f.calc_center_median().z < hc.z - 0.036]
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    for v in bm.verts:
        if v.co.z < hc.z - 0.01: v.co.x *= 1.08; v.co.y = hc.y + (v.co.y - hc.y) * 1.06
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.004); add("haar", bm)
    # hoedje: grijsgroen, opstaande omgeslagen rand, iets achterover, met rode krulveer naar achter (foto + ontwerp)
    Mh = Matrix.Translation(hc + Vector((0, 0.006, 0.032))) @ Matrix.Rotation(math.radians(14), 4, "X") @ Matrix.Rotation(math.radians(-8), 4, "Y")
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=0.036, radius2=0.03, depth=0.026); bmesh.ops.translate(bm, vec=(0, 0, 0.013), verts=bm.verts)
    add("toon_hoed", bm, Mh.copy())
    bm = bmesh.new(); ri = []; ro = []
    for k in range(20):
        a = k * math.tau / 20; up = 0.012 + 0.012 * max(0.0, -math.sin(a))      # rand voor hoger opgeslagen
        ri.append(bm.verts.new((0.036 * math.cos(a), 0.036 * math.sin(a), 0.0))); ro.append(bm.verts.new((0.05 * math.cos(a), 0.052 * math.sin(a), up)))
    for k in range(20): bm.faces.new((ri[k], ri[(k + 1) % 20], ro[(k + 1) % 20], ro[k]))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.004); add("toon_hoed", bm, Mh.copy())
    base = (Mh @ Vector((0.01, 0.025, 0.02)))
    pts = [base + Vector((0.004 * t, 0.07 * t, 0.06 * math.sin(t * 2.2))) + Vector((0, 0.02 * math.sin(t * 6) * t, -0.02 * (1 - math.cos(t * 6)) * t * t)) for t in [i / 11 for i in range(12)]]
    add("toon_rood", tube(pts, [0.006, 0.01, 0.014, 0.016, 0.016, 0.015, 0.013, 0.011, 0.009, 0.007, 0.005, 0.002], 10))
    return {m: bm for m, bm in PARTS.items()}


T = toon()
SC = 1.35
# zit links van de klok, voor de stijl linksvoor (die loopt achter zijn rug langs), kijkt opzij naar de klok: vanaf het plein in profiel (foto)
seat = Vector((-0.31, -0.43, 6.78))
f = Vector((1.0, 0.12)).normalized(); th = math.atan2(f.x, -f.y)                # lokaal -Y -> richting de klok
M = Matrix.Translation(seat) @ Matrix.Rotation(th, 4, "Z") @ Matrix.Scale(SC, 4)
col = bpy.data.collections["FORMS"]; tris = 0
# zitkrul (lood, zoals de krulstijlen): spiraal onder zijn zitvlak in het vlak van zijn kijkrichting, staart naar de voet van de stijl linksvoor
fv = Vector((f.x, f.y, 0)); cz = seat + Vector((0, 0, -0.055)) - fv * 0.01; pts = []
for i in range(25):
    t = i / 24; ang = math.pi / 2 + t * 1.6 * math.tau; r = 0.055 * (1 - 0.65 * t)
    pts.append(cz + fv * (r * math.cos(ang)) + Vector((0, 0, r * math.sin(ang))))
krul = tube([Vector((-0.31, -0.31, 6.68)), Vector((-0.31, -0.38, 6.74)), pts[0] - fv * 0.03] + pts, 0.014, 6)
T.setdefault("lood", bmesh.new())
me_k = bpy.data.meshes.new("_k"); krul.to_mesh(me_k); krul.free(); T["lood"].from_mesh(me_k); bpy.data.meshes.remove(me_k)
for v in T["lood"].verts: v.co = M.inverted() @ v.co   # wordt hieronder weer met M getransformeerd
# klokkentouw: van de handen naar de klepelarm boven de klok
hand = M @ Vector((0.0, -0.132, 0.23)); top = Vector((-0.09, -0.05, 7.22))
rope = tube([hand + Vector((0, 0, -0.06)), hand, hand.lerp(top, 0.5), top], 0.0045, 6)
T.setdefault("kant", bmesh.new())
me_ = bpy.data.meshes.new("_r"); rope.to_mesh(me_); rope.free(); bmr = bmesh.new(); bmr.from_mesh(me_); bpy.data.meshes.remove(me_)
for mat, src in T.items():
    bm = src.copy()
    if len(bm.verts): bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    if mat == "kant":
        me2 = bpy.data.meshes.new("_r2"); bmr.to_mesh(me2); bm.from_mesh(me2); bpy.data.meshes.remove(me2)
    me = bpy.data.meshes.new(f"MK_toon_{mat}"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(f"MK_toon_{mat}__{mat}", me); col.objects.link(ob); ob["owner"] = OWNER
    ob.data.materials.append(bpy.data.materials["MAT_" + mat]); tris += sum(len(p.vertices) - 2 for p in me.polygons)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=master)
print("[03d_toon] seat", tuple(round(v, 3) for v in seat), "tris", tris)
