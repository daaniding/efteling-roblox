"""03e_kikker: een fonteinkikker van de Kikkerkoning naar Kikkerkoningontwerp2 (Pieck), Kikker1973, Kikkers-tuinslang (2023).
Zittende waterkikker, voorpoten gestrekt, kop omhoog, achterpoten opgevouwen langs het lijf; ~0.85 lang, ~0.55 hoog (tot de ogen).
Lijf = overlappende ellipsoiden/buizen -> voxel-remesh (unie) -> smooth (overgangen) -> decimate; huid gebakken: geelgroen met olijfgroene
vlekken, lichtere buik (BAKE_kikker, eigen UV). Ogen: crème ring + zwarte pupil (losse materialen).
Kijkt naar -Y, z=0 = onderkant. Gebruik: Blender -b -P 03e_kikker.py -- --out <kikker.blend> [--res 1024]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix, Euler
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
args = sys.argv[sys.argv.index("--") + 1:]; OUT = args[args.index("--out") + 1]
RES = int(args[args.index("--res") + 1]) if "--res" in args else 1024
bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.data.collections.new("FORMS"); bpy.context.scene.collection.children.link(col)


def ell(c, r, rot=(0, 0, 0), segs=24, rings=14):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    bmesh.ops.scale(bm, vec=r, verts=bm.verts)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Euler([math.radians(a) for a in rot]).to_matrix())
    bmesh.ops.translate(bm, vec=c, verts=bm.verts); return bm


def tube(pts, rads, segs=10):
    bm = bmesh.new(); P = [Vector(p) for p in pts]; rings = []
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        a = t.cross(Vector((0, 0, 1))); a = a.normalized() if a.length > 1e-3 else t.cross(Vector((1, 0, 0))).normalized(); b = t.cross(a)
        r = rads[i] if isinstance(rads, (list, tuple)) else rads
        rings.append([bm.verts.new(p + (a * math.cos(k * math.tau / segs) + b * math.sin(k * math.tau / segs)) * r) for k in range(segs)])
    for A, B in zip(rings, rings[1:]):
        for k in range(segs): bm.faces.new((A[k], A[(k + 1) % segs], B[(k + 1) % segs], B[k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


body = bmesh.new()
def add(bm):
    me = bpy.data.meshes.new("_t"); bm.to_mesh(me); bm.free(); body.from_mesh(me); bpy.data.meshes.remove(me)

# romp: schuin oplopend naar voren (zit rechtop op de voorpoten)
add(ell((0, 0.06, 0.22), (0.17, 0.25, 0.15), (-22, 0, 0)))
add(ell((0, 0.2, 0.15), (0.16, 0.14, 0.12)))                               # stuit
add(ell((0, -0.13, 0.33), (0.155, 0.14, 0.13), (-30, 0, 0)))               # borst/schouders
# kop: breed en plat, snuit rond
add(ell((0, -0.25, 0.42), (0.145, 0.14, 0.085), (-18, 0, 0)))
add(ell((0, -0.36, 0.43), (0.095, 0.08, 0.055), (-14, 0, 0)))
add(ell((0, -0.2, 0.34), (0.13, 0.1, 0.07)))                                # keel
for sx in (-1, 1): add(ell((sx * 0.128, -0.17, 0.4), (0.012, 0.034, 0.034)))      # trommelvlies (vlakke ronde bult)
# rugwallen (dorsolaterale plooien, Pieck)
for sx in (-1, 1): add(tube([(sx * 0.07, -0.2, 0.47), (sx * 0.1, -0.02, 0.41), (sx * 0.11, 0.16, 0.31), (sx * 0.08, 0.27, 0.22)], [0.012, 0.016, 0.015, 0.01], 8))
for sx in (-1, 1):
    # achterpoot: dij en onderbeen opgevouwen langs de flank, voet lang naar voren
    add(ell((sx * 0.165, 0.13, 0.13), (0.075, 0.2, 0.085), (-8, 0, sx * -18)))
    add(ell((sx * 0.215, 0.03, 0.075), (0.06, 0.19, 0.06), (6, 0, sx * 12)))
    add(ell((sx * 0.235, -0.13, 0.03), (0.055, 0.12, 0.028), (0, 0, sx * 20)))
    for k, a in enumerate((-12, 0, 12, 24, 36)):                             # tenen (zwemvliezen niet apart)
        aa = math.radians(sx * (20 + a)); base = Vector((sx * 0.235, -0.2, 0.02)); d = Vector((-math.sin(aa) * -1 * 0 + math.sin(aa), -math.cos(aa), 0))
        L = 0.07 + 0.03 * (k in (2, 3))
        add(tube([base, base + d * L * 0.6 + Vector((0, 0, 0.004)), base + d * L], [0.014, 0.011, 0.009], 8))
        add(ell(tuple(base + d * L), (0.012, 0.012, 0.009), segs=10, rings=6))
    # voorpoot: gestrekt, iets naar buiten, hand plat met 4 vingers
    add(tube([(sx * 0.1, -0.16, 0.3), (sx * 0.12, -0.21, 0.17), (sx * 0.135, -0.25, 0.04)], [0.055, 0.044, 0.036], 12))
    add(ell((sx * 0.14, -0.27, 0.018), (0.045, 0.045, 0.018)))
    for a in (-30, -8, 14, 36):
        aa = math.radians(a + sx * 10); base = Vector((sx * 0.14, -0.28, 0.015)); d = Vector((math.sin(aa) * sx, -math.cos(aa), 0))
        add(tube([base, base + d * 0.05, base + d * 0.075], [0.011, 0.009, 0.008], 8))
        add(ell(tuple(base + d * 0.078), (0.011, 0.011, 0.008), segs=10, rings=6))

me = bpy.data.meshes.new("kikker_lijf"); body.to_mesh(me); body.free()
ob = bpy.data.objects.new("BAKE_kikker", me); col.objects.link(ob)
bpy.context.view_layer.objects.active = ob; ob.select_set(True)
rm = ob.modifiers.new("remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.008
sm = ob.modifiers.new("smooth", "SMOOTH"); sm.factor = 0.6; sm.iterations = 8
dc = ob.modifiers.new("dec", "DECIMATE"); dc.ratio = 0.12
for m in list(ob.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
bpy.ops.object.shade_smooth()
tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)

# ogen: crème ring (oogbol) + zwarte pupil + trommelvlies
def los(name, bm, mat, color, rough=0.3):
    m_ = bpy.data.meshes.new(name); bm.to_mesh(m_); bm.free(); o = bpy.data.objects.new(name, m_); col.objects.link(o)
    mt = bpy.data.materials.get("MAT_" + mat) or bpy.data.materials.new("MAT_" + mat); mt.diffuse_color = color
    nt = mt.node_tree; b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"); b.inputs["Base Color"].default_value = color; b.inputs["Roughness"].default_value = rough
    o.data.materials.append(mt)
    for p in o.data.polygons: p.use_smooth = True
    return o
eb = bmesh.new(); pb = bmesh.new()
for sx in (-1, 1):
    ec = Vector((sx * 0.083, -0.255, 0.462)); n = Vector((sx * 0.8, -0.3, 0.5)).normalized()
    t = ell(tuple(ec), (0.046, 0.046, 0.042)); me_ = bpy.data.meshes.new("_e"); t.to_mesh(me_); t.free(); eb.from_mesh(me_); bpy.data.meshes.remove(me_)
    # pupil: platte zwarte lens in de oogbol (crème ring blijft rondom zichtbaar, Detailkikker1973)
    t = bmesh.new(); bmesh.ops.create_uvsphere(t, u_segments=18, v_segments=10, radius=1.0); bmesh.ops.scale(t, vec=(0.027, 0.027, 0.012), verts=t.verts)
    bmesh.ops.rotate(t, verts=t.verts, cent=(0, 0, 0), matrix=n.to_track_quat("Z", "Y").to_matrix()); bmesh.ops.translate(t, vec=ec + n * 0.04, verts=t.verts)
    me_ = bpy.data.meshes.new("_p"); t.to_mesh(me_); t.free(); pb.from_mesh(me_); bpy.data.meshes.remove(me_)
los("KK_oog__oogring", eb, "oogring", (0.86, 0.80, 0.56, 1), 0.2)
los("KK_pupil__pupil", pb, "pupil", (0.02, 0.02, 0.02, 1), 0.1)

# huid bakken: geelgroen, olijfgroene vlekken (ruis), lichtere geelachtige buik, donkere rug-tint
bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = ob; ob.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004, scale_to_bounds=True); bpy.ops.object.mode_set(mode="OBJECT")
m = bpy.data.materials.new("BAKE_kikker"); nt = m.node_tree; N = nt.nodes; Lk = nt.links; N.clear()
out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission"); tc = N.new("ShaderNodeTexCoord"); geo = N.new("ShaderNodeNewGeometry")
def lin(c): return tuple((v / 255) ** 2.2 for v in c) + (1,)
nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0; nz.inputs["Detail"].default_value = 3.0; Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].position = 0.52; rp.color_ramp.elements[1].position = 0.56
rp.color_ramp.elements[0].color = lin((182, 186, 52)); rp.color_ramp.elements[1].color = lin((92, 112, 38)); Lk.new(nz.outputs["Fac"], rp.inputs["Fac"])
nz2 = N.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 40.0; Lk.new(tc.outputs["Object"], nz2.inputs["Vector"])
mx2 = N.new("ShaderNodeMix"); mx2.data_type = "RGBA"; mx2.blend_type = "MULTIPLY"; mx2.inputs["Factor"].default_value = 0.18
Lk.new(rp.outputs["Color"], mx2.inputs[6]); Lk.new(nz2.outputs["Color"], mx2.inputs[7])
sep = N.new("ShaderNodeSeparateXYZ"); Lk.new(geo.outputs["Normal"], sep.inputs["Vector"])
br = N.new("ShaderNodeMapRange"); br.inputs["From Min"].default_value = -0.2; br.inputs["From Max"].default_value = -0.7; Lk.new(sep.outputs["Z"], br.inputs["Value"])
mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; Lk.new(br.outputs["Result"], mx.inputs["Factor"]); Lk.new(mx2.outputs[2], mx.inputs[6]); mx.inputs[7].default_value = lin((222, 214, 120))
Lk.new(mx.outputs[2], em.inputs["Color"]); Lk.new(em.outputs[0], out.inputs[0])
ob.data.materials.append(m)
img = bpy.data.images.new("TEX_kikker", RES, RES); tex = N.new("ShaderNodeTexImage"); tex.image = img; N.active = tex
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = 4
bpy.ops.object.bake(type="EMIT", margin=8)
os.makedirs(os.path.join(ROOT, "textures"), exist_ok=True)
img.filepath_raw = os.path.join(ROOT, "textures", "HP_kikker_kleur.png"); img.file_format = "PNG"; img.save()
# na het bakken: materiaal met de textuur (voor renders)
N.remove(em); bs = N.new("ShaderNodeBsdfPrincipled"); Lk.new(tex.outputs["Color"], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.3
Lk.new(bs.outputs[0], out.inputs[0]); m.diffuse_color = (0.45, 0.5, 0.08, 1)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("[03e_kikker] tris", tris, "afm", tuple(round(v, 3) for v in ob.dimensions))
