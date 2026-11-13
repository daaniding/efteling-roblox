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
L2, W2 = 0.9, 0.42                                                            # halve lengte (y, langs de ezel) / halve breedte (x) van het lijf
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
    x = sx * (W2 + 0.012); cs = [(x, -0.6 * sx, 0.76), (x, 0.6 * sx, 0.76), (x, 0.6 * sx, 1.3), (x, -0.6 * sx, 1.3)]
    f = bb.faces.new([bb.verts.new(c) for c in cs])
    for l, uv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): l[uvl].uv = uv
obj("BAKE_bord", bb, mat("bord", (0.8, 0.7, 0.4, 1)), False)

# ================= EZEL (staat op z = SH): anatomisch model in ezel_anatomie.py =================
Z = SH
exec(open(os.path.join(HERE, "ezel_anatomie.py")).read())

# ================= materialen + objecten =================
M = {"ijssel": ((0.62, 0.55, 0.42, 1), 0.9), "beton": ((0.78, 0.72, 0.58, 1), 0.85), "rood": ((0.55, 0.08, 0.06, 1), 0.5), "deur": ((0.42, 0.45, 0.36, 1), 0.6),
     "ijzer": ((0.05, 0.05, 0.05, 1), 0.4), "hoef": ((0.2, 0.19, 0.18, 1), 0.5), "oog": ((0.85, 0.84, 0.8, 1), 0.3), "pupil": ((0.02, 0.02, 0.02, 1), 0.2),
     "manen": ((0.35, 0.33, 0.31, 1), 0.8), "ezelhuid": ((0.62, 0.6, 0.56, 1), 0.7), "neus": ((0.18, 0.16, 0.15, 1), 0.6), "oorbinnen": ((0.45, 0.42, 0.4, 1), 0.8), "tuig": ((0.55, 0.06, 0.05, 1), 0.45), "goud": ((0.8, 0.6, 0.2, 1), 0.3)}
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
rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].color = lin((176, 170, 160)); rp.color_ramp.elements[1].color = lin((200, 194, 183)); Lk.new(nz.outputs["Fac"], rp.inputs["Fac"])
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
# AO-bake (diepte in plooien/oksels) en normal map van het hoge vachtmodel
bpy.data.objects["_ezel_hi"].hide_render = True                                 # hoog model mag de AO niet afdekken
ao = bpy.data.images.new("AO_ezel", 2048, 2048); tx.image = ao; sc.cycles.samples = 64
bpy.ops.object.bake(type="AO", margin=8)
nrm = bpy.data.images.new("NRM_ezel", 2048, 2048); nrm.colorspace_settings.name = "Non-Color"; tx.image = nrm; sc.cycles.samples = 1
hi = bpy.data.objects["_ezel_hi"]; hi.hide_render = False
bpy.ops.object.select_all(action="DESELECT"); hi.select_set(True); ez.select_set(True); bpy.context.view_layer.objects.active = ez
bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT", use_selected_to_active=True, cage_extrusion=0.012, max_ray_distance=0.03, margin=8)
nrm.filepath_raw = os.path.join(ROOT, "textures", "EZ_ezel_normaal.png"); nrm.file_format = "PNG"; nrm.save()
tx.image = img
import numpy as np
c_ = np.array(img.pixels[:]).reshape(-1, 4); a_ = np.array(ao.pixels[:]).reshape(2048, 2048, 4)[::2, ::2].reshape(-1, 4)
c_[:, :3] *= (0.45 + 0.55 * a_[:, :1]); img.pixels[:] = c_.ravel().tolist()
img.filepath_raw = os.path.join(ROOT, "textures", "EZ_ezel_kleur.png"); img.file_format = "PNG"; img.save()
bpy.data.objects.remove(hi, do_unlink=True)
N.remove(em); bs = N.new("ShaderNodeBsdfPrincipled"); Lk.new(tx.outputs["Color"], bs.inputs["Base Color"]); Lk.new(bs.outputs[0], out.inputs[0]); m.diffuse_color = (0.6, 0.58, 0.54, 1)
for o_, f_ in ((bpy.data.objects["BAKE_dekje"], "EZ_dekje_kleur.png"), (bpy.data.objects["BAKE_bord"], "EZ_bord_kleur.png")):
    mt = o_.data.materials[0]; n2 = mt.node_tree; b2 = next(n for n in n2.nodes if n.type == "BSDF_PRINCIPLED")
    t2 = n2.nodes.new("ShaderNodeTexImage"); t2.image = bpy.data.images.load(os.path.join(ROOT, "textures", f_)); n2.links.new(t2.outputs["Color"], b2.inputs["Base Color"])
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("[03_ezel] ezel tris", sum(len(p.vertices) - 2 for p in ez.data.polygons), "afm", tuple(round(v, 2) for v in ez.dimensions))
