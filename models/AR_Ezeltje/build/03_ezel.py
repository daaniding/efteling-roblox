"""03_ezel: Ezeltje Strek Je (Herautenplein) — wonderezel op sokkel naar Ezel5/Ezel7/Ezeltje_nu/Ezelachter/Ezel.png (Pieck-tekening).
Sokkel: basis van ijsselsteentjes, sierbeton (crème) met krullen op de hoeken van de korte zijden, gouden cartouches "Ezeltje strekje" op de
lange zijden, muntdeurtje achter (staartkant), dekplaat met rode rand. Ezel: grijs, gestrekte houding (voorpoten naar voren, achterpoten naar
achter, kop laag vooruit, staart recht naar achter), rood tuig met gouden nagels, crème dekje met Pieck-ornament en zigzagfranje.
Lijf = ellipsoiden/buizen -> voxel-remesh -> smooth -> decimate; huid gebakken (BAKE_ezel). Model kijkt naar -Y, z=0 = maaiveld.
Gebruik: Blender -b -P 03_ezel.py -- --out <AR_Ezeltje.blend>"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix, Euler
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
args = sys.argv[sys.argv.index("--") + 1:]; OUT = args[args.index("--out") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.data.collections.new("FORMS"); bpy.context.scene.collection.children.link(col)
SH = 1.66                                                                     # bovenkant sokkel (ezel staat hierop)


def ell(c, r, rot=(0, 0, 0), segs=24, rings=14):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    bmesh.ops.scale(bm, vec=r, verts=bm.verts)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Euler([math.radians(a) for a in rot]).to_matrix())
    bmesh.ops.translate(bm, vec=c, verts=bm.verts); return bm


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


def box(x0, x1, y0, y1, z0, z1, bev=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(x1 - x0, y1 - y0, z1 - z0), verts=bm.verts)
    if bev > 0: bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bev, segments=2, affect="EDGES", profile=0.5)
    bmesh.ops.translate(bm, vec=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), verts=bm.verts); return bm


PARTS = {}
def put(mat, bm, M=None):
    if M is not None: bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    me = bpy.data.meshes.new("_t"); bm.to_mesh(me); bm.free(); PARTS.setdefault(mat, bmesh.new()).from_mesh(me); bpy.data.meshes.remove(me)


def mat(name, color, rough=0.6, metal=0.0):
    m = bpy.data.materials.get("MAT_" + name) or bpy.data.materials.new("MAT_" + name); m.diffuse_color = color
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"); b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal; return m


def obj(name, bm, material, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); col.objects.link(o)
    o.data.materials.append(material)
    for p in o.data.polygons: p.use_smooth = smooth
    return o


# ================= SOKKEL =================
L2, W2 = 0.68, 0.42                                                            # halve lengte (y, langs de ezel) / halve breedte (x) van het lijf
put("ijssel", box(-W2 - 0.3, W2 + 0.3, -L2 - 0.3, L2 + 0.3, -0.1, 0.36, 0.03))           # basis ijsselsteentjes
put("beton", box(-W2 - 0.2, W2 + 0.2, -L2 - 0.2, L2 + 0.2, 0.36, 0.5, 0.025))           # plint
put("beton", box(-W2, W2, -L2, L2, 0.5, 1.42, 0.02))                                      # lijf
put("beton", box(-W2 - 0.08, W2 + 0.08, -L2 - 0.08, L2 + 0.08, 0.5, 0.6, 0.02))          # voetlijst
put("beton", box(-W2 - 0.1, W2 + 0.1, -L2 - 0.1, L2 + 0.1, 1.38, 1.47, 0.02))            # kroonlijst onder
put("beton", box(-W2 - 0.16, W2 + 0.16, -L2 - 0.16, L2 + 0.16, 1.47, 1.6, 0.03))         # kroonlijst boven
put("rood", box(-W2 - 0.17, W2 + 0.17, -L2 - 0.17, L2 + 0.17, 1.6, SH, 0.01))           # dekplaat met rode rand (Ezel5)
put("beton", box(-W2 - 0.12, W2 + 0.12, -L2 - 0.12, L2 + 0.12, 1.6, SH + 0.005, 0.01))   # crème middenveld van de dekplaat
for sy in (-1, 1):                                                             # krullen (voluten) op de hoeken van de korte zijden
    for sx in (-1, 1):
        pts = []
        for i in range(25):
            t = i / 24
            if t < 0.35:                                                       # onderaan een spiraal naar buiten
                a = t / 0.35 * 1.6 * math.pi; r = 0.11 * (1 - 0.6 * t / 0.35)
                pts.append((sx * (W2 + 0.02 + r * (1 + math.cos(a)) * 0.6), sy * (L2 + 0.03 + r * (1 - math.sin(a)) * 0.4), 0.6 + r * (1 - math.cos(a))))
            else:                                                              # S-curve omhoog naar de kroonlijst
                u = (t - 0.35) / 0.65
                pts.append((sx * (W2 + 0.02 + 0.07 * math.sin(u * math.pi)), sy * (L2 + 0.03 + 0.04 * math.sin(u * math.pi * 2)), 0.72 + u * 0.66))
        put("beton", tube(pts, [0.045 - 0.015 * (i / 24) for i in range(25)], 10))
# muntdeurtje achter (staartkant, +Y): groengrijs paneel met gleuf
put("deur", box(-0.2, 0.2, L2, L2 + 0.025, 0.66, 1.26, 0.01))
put("ijzer", box(-0.03, 0.03, L2 + 0.025, L2 + 0.04, 1.05, 1.15, 0.0))
# cartouches op de lange zijden (+X en -X): eigen UV naar EZ_bord_kleur.png
bb = bmesh.new(); uvl = bb.loops.layers.uv.new("UVMap")
for sx in (-1, 1):
    x = sx * (W2 + 0.012); cs = [(x, -0.5 * sx, 0.78), (x, 0.5 * sx, 0.78), (x, 0.5 * sx, 1.27), (x, -0.5 * sx, 1.27)]
    f = bb.faces.new([bb.verts.new(c) for c in cs])
    for l, uv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): l[uvl].uv = uv
obj("BAKE_bord", bb, mat("bord", (0.8, 0.7, 0.4, 1)), False)

# ================= EZEL (staat op z = SH) =================
Z = SH
body = bmesh.new()
def add(bm):
    me = bpy.data.meshes.new("_t"); bm.to_mesh(me); bm.free(); body.from_mesh(me); bpy.data.meshes.remove(me)
add(ell((0, 0.05, Z + 0.78), (0.225, 0.52, 0.26), (-4, 0, 0)))                  # romp
add(ell((0, -0.4, Z + 0.75), (0.21, 0.22, 0.24)))                               # borst
add(ell((0, 0.43, Z + 0.83), (0.225, 0.24, 0.24)))                             # kruis
add(tube([(0, -0.45, Z + 0.88), (0, -0.7, Z + 0.78), (0, -0.92, Z + 0.6), (0, -1.02, Z + 0.5)], [0.17, 0.14, 0.12, 0.1], 14))   # hals
add(ell((0, -1.13, Z + 0.42), (0.105, 0.22, 0.125), (38, 0, 0)))             # kop (naar beneden-voren)
add(ell((0, -1.28, Z + 0.3), (0.085, 0.1, 0.09)))                              # snuit
add(ell((0, -1.25, Z + 0.25), (0.075, 0.09, 0.05)))                            # onderkaak
for sx in (-1, 1):
    add(tube([(sx * 0.05, -1.02, Z + 0.52), (sx * 0.08, -0.97, Z + 0.68), (sx * 0.11, -0.93, Z + 0.84)], [0.035, 0.04, 0.012], 10))   # oren
    # voorbenen gestrekt naar voren
    add(ell((sx * 0.11, -0.42, Z + 0.58), (0.09, 0.12, 0.18)))
    add(tube([(sx * 0.11, -0.45, Z + 0.55), (sx * 0.12, -0.6, Z + 0.3), (sx * 0.13, -0.72, Z + 0.07)], [0.075, 0.056, 0.05], 12))
    # achterbenen gestrekt naar achter
    add(ell((sx * 0.125, 0.45, Z + 0.62), (0.11, 0.19, 0.24), (15, 0, 0)))
    add(tube([(sx * 0.12, 0.52, Z + 0.48), (sx * 0.12, 0.7, Z + 0.3), (sx * 0.12, 0.8, Z + 0.07)], [0.08, 0.056, 0.05], 12))
add(tube([(0, 0.6, Z + 0.92), (0, 0.85, Z + 0.88), (0, 1.12, Z + 0.8)], [0.04, 0.03, 0.025], 10))   # staart recht naar achter
me = bpy.data.meshes.new("ezel"); body.to_mesh(me); body.free()
ez = bpy.data.objects.new("BAKE_ezel", me); col.objects.link(ez)
bpy.context.view_layer.objects.active = ez; ez.select_set(True)
rm = ez.modifiers.new("remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.012
sm = ez.modifiers.new("smooth", "SMOOTH"); sm.factor = 0.6; sm.iterations = 10
dc = ez.modifiers.new("dec", "DECIMATE"); dc.ratio = 0.15
for m_ in list(ez.modifiers): bpy.ops.object.modifier_apply(modifier=m_.name)
bpy.ops.object.shade_smooth()
# hoeven, manen, staartpluim, ogen
for sx in (-1, 1):
    for y in (-0.72, 0.8):
        put("hoef", tube([(sx * (0.13 if y < 0 else 0.12), y, Z + 0.0), (sx * (0.13 if y < 0 else 0.12), y, Z + 0.07)], [0.05, 0.043], 12))
    put("oog", ell((sx * 0.085, -1.14, Z + 0.48), (0.025, 0.03, 0.022)))
    put("pupil", ell((sx * 0.1, -1.15, Z + 0.48), (0.012, 0.018, 0.014)))
put("manen", tube([(0, -0.48, Z + 1.0), (0, -0.72, Z + 0.9), (0, -0.92, Z + 0.7), (0, -1.0, Z + 0.6)], [0.035, 0.035, 0.03, 0.02], 8))
put("manen", ell((0, 1.17, Z + 0.78), (0.05, 0.09, 0.05)))
# rood tuig met gouden nagels: borstriem, buikriem, staartriem, halster
def band(c, rx, rz, yfun, n=32, a0=0.0, a1=math.tau, r=0.013):
    pts = [(c[0] + rx * math.sin(a), c[1] + yfun(a), c[2] + rz * math.cos(a)) for a in [a0 + (a1 - a0) * i / n for i in range(n + 1)]]
    put("tuig", tube(pts, r, 6, cap=False))
    for i in range(0, n + 1, 3):
        put("goud", ell(pts[i], (0.014, 0.014, 0.014), segs=8, rings=5))
band((0, -0.18, Z + 0.78), 0.2, 0.235, lambda a: 0.0)                                                    # buikriem
band((0, -0.5, Z + 0.77), 0.185, 0.21, lambda a: -0.12 * max(0.0, -math.cos(a)) - 0.0, 28, math.pi * 0.25, math.pi * 1.75)   # borstriem
band((0, 0.55, Z + 0.84), 0.2, 0.215, lambda a: 0.12 * max(0.0, -math.cos(a)), 28, -math.pi * 0.25 + math.pi, math.pi * 2.75)   # staartriem
put("tuig", tube([(0, -0.45, Z + 1.0), (0, -0.18, Z + 1.025), (0, 0.4, Z + 1.04), (0, 0.6, Z + 0.97)], 0.013, 6))
for sx in (-1, 1): put("tuig", tube([(sx * 0.09, -1.3, Z + 0.32), (sx * 0.1, -1.08, Z + 0.5), (sx * 0.06, -1.0, Z + 0.58)], 0.014, 6))
band((0, -1.28, Z + 0.31), 0.095, 0.095, lambda a: 0.0, 20, r=0.016)                                    # neusriem
# dekje over de rug (Pieck-ornament, zigzagfranje) met eigen UV
db = bmesh.new(); uvl = db.loops.layers.uv.new("UVMap"); NU, NV = 16, 8; V = []
for j in range(NV + 1):
    y = -0.32 + 0.62 * j / NV; row = []
    for i in range(NU + 1):
        th = math.radians(-82 + 164 * i / NU); rx, rz = 0.225, 0.258
        row.append(db.verts.new((rx * math.sin(th), y, Z + 0.78 + rz * math.cos(th) + 0.012)))
    V.append(row)
for j in range(NV):
    for i in range(NU):
        f = db.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
        for l, (ii, jj) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))): l[uvl].uv = (ii / NU, jj / NV)
bmesh.ops.solidify(db, geom=db.faces[:], thickness=0.006)
obj("BAKE_dekje", db, mat("dekje", (0.9, 0.85, 0.75, 1)), True)

# ================= materialen + objecten =================
M = {"ijssel": ((0.62, 0.55, 0.42, 1), 0.9), "beton": ((0.78, 0.72, 0.58, 1), 0.85), "rood": ((0.55, 0.08, 0.06, 1), 0.5), "deur": ((0.42, 0.45, 0.36, 1), 0.6),
     "ijzer": ((0.05, 0.05, 0.05, 1), 0.4), "hoef": ((0.2, 0.19, 0.18, 1), 0.5), "oog": ((0.85, 0.84, 0.8, 1), 0.3), "pupil": ((0.02, 0.02, 0.02, 1), 0.2),
     "manen": ((0.35, 0.33, 0.31, 1), 0.8), "tuig": ((0.55, 0.06, 0.05, 1), 0.45), "goud": ((0.8, 0.6, 0.2, 1), 0.3)}
for name, bm in PARTS.items():
    c, r = M[name]; obj(f"EZ_{name}__{name}", bm, mat(name, c, r, 0.9 if name == "goud" else 0.0))
# huid bakken: lichtgrijs-beige, lichtere buik en snuit, subtiele ruis
bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = ez; ez.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004, scale_to_bounds=True); bpy.ops.object.mode_set(mode="OBJECT")
m = bpy.data.materials.new("BAKE_ezel"); nt = m.node_tree; N = nt.nodes; Lk = nt.links; N.clear()
out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); tc = N.new("ShaderNodeTexCoord"); geo = N.new("ShaderNodeNewGeometry")
def lin(c): return tuple((v / 255) ** 2.2 for v in c) + (1,)
nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14.0; Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].color = lin((166, 160, 150)); rp.color_ramp.elements[1].color = lin((190, 184, 172)); Lk.new(nz.outputs["Fac"], rp.inputs["Fac"])
sep = N.new("ShaderNodeSeparateXYZ"); Lk.new(geo.outputs["Normal"], sep.inputs["Vector"])
br = N.new("ShaderNodeMapRange"); br.inputs["From Min"].default_value = -0.2; br.inputs["From Max"].default_value = -0.8; Lk.new(sep.outputs["Z"], br.inputs["Value"])
mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; Lk.new(br.outputs["Result"], mx.inputs["Factor"]); Lk.new(rp.outputs["Color"], mx.inputs[6]); mx.inputs[7].default_value = lin((214, 208, 196))
sp = N.new("ShaderNodeSeparateXYZ"); Lk.new(geo.outputs["Position"], sp.inputs["Vector"])                 # snuit lichter (y < -1.2)
sn = N.new("ShaderNodeMapRange"); sn.inputs["From Min"].default_value = -1.18; sn.inputs["From Max"].default_value = -1.3; Lk.new(sp.outputs["Y"], sn.inputs["Value"])
mx2 = N.new("ShaderNodeMix"); mx2.data_type = "RGBA"; Lk.new(sn.outputs["Result"], mx2.inputs["Factor"]); Lk.new(mx.outputs[2], mx2.inputs[6]); mx2.inputs[7].default_value = lin((222, 218, 208))
Lk.new(mx2.outputs[2], em.inputs["Color"]); Lk.new(em.outputs[0], out.inputs[0]); ez.data.materials.append(m)
img = bpy.data.images.new("TEX_ezel", 1024, 1024); tx = N.new("ShaderNodeTexImage"); tx.image = img; N.active = tx
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = 4
bpy.ops.object.bake(type="EMIT", margin=8)
img.filepath_raw = os.path.join(ROOT, "textures", "EZ_ezel_kleur.png"); img.file_format = "PNG"; img.save()
N.remove(em); bs = N.new("ShaderNodeBsdfPrincipled"); Lk.new(tx.outputs["Color"], bs.inputs["Base Color"]); Lk.new(bs.outputs[0], out.inputs[0]); m.diffuse_color = (0.6, 0.58, 0.54, 1)
for o_, f_ in ((bpy.data.objects["BAKE_dekje"], "EZ_dekje_kleur.png"), (bpy.data.objects["BAKE_bord"], "EZ_bord_kleur.png")):
    mt = o_.data.materials[0]; n2 = mt.node_tree; b2 = next(n for n in n2.nodes if n.type == "BSDF_PRINCIPLED")
    t2 = n2.nodes.new("ShaderNodeTexImage"); t2.image = bpy.data.images.load(os.path.join(ROOT, "textures", f_)); n2.links.new(t2.outputs["Color"], b2.inputs["Base Color"])
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("[03_ezel] ezel tris", sum(len(p.vertices) - 2 for p in ez.data.polygons), "afm", tuple(round(v, 2) for v in ez.dimensions))
