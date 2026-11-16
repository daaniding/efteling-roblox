"""02_grasplukjes: eigen 3D-grasplukjes voor gemaaid gazon (Blender, headless).
Per plukje 50 sprieten: smalle, taps toelopende, licht gebogen strookjes (5 driehoeken; DoubleSided in Roblox).
Kleur via een kleurstrook-textuur (8 kolommen = 8 spriet-tinten; onder = voet donker, boven = punt licht), tinten
gemeten uit de CC0-grasfoto Grass004. Normalen half naar boven gebogen: zo licht gras op als een gazon i.p.v. losse plaatjes.
Gebruik: blender --background --python 02_grasplukjes.py -- <uitmap>"""
import bpy, bmesh, sys, os, math, random
import numpy as np
from mathutils import Vector
UIT = sys.argv[sys.argv.index("--") + 1]; os.makedirs(UIT, exist_ok=True)

# kleurstrook 64 x 256: 8 tinten, verloop voet -> punt
TINT = [  # (voet, midden, punt) in sRGB 0-255
    ((40, 52, 18), (72, 92, 34), (104, 122, 52)),
    ((44, 56, 20), (80, 100, 38), (116, 132, 58)),
    ((38, 50, 20), (66, 88, 36), (96, 118, 54)),
    ((46, 54, 18), (90, 102, 40), (128, 134, 62)),   # iets geler
    ((36, 50, 22), (60, 86, 40), (88, 114, 58)),     # iets blauwer/donker
    ((42, 54, 18), (78, 96, 34), (112, 126, 50)),
    ((48, 56, 22), (96, 104, 46), (138, 136, 76)),   # verdord puntje
    ((40, 52, 20), (74, 94, 36), (108, 126, 56)),
]
W, H = 64, 256
img = np.zeros((H, W, 4), np.float32)
for k, (a, b, c) in enumerate(TINT):
    for y in range(H):
        t = y / (H - 1)                      # 0 = voet (onderaan in UV), 1 = punt
        col = np.array(a) * (1 - t) * 2 if t < 0.5 else None
        if t < 0.5: col = np.array(a) + (np.array(b) - np.array(a)) * (t / 0.5)
        else: col = np.array(b) + (np.array(c) - np.array(b)) * ((t - 0.5) / 0.5)
        img[H - 1 - y, k * 8:(k + 1) * 8, :3] = col / 255.0
img[..., 3] = 1
bim = bpy.data.images.new("GR_sprietkleur", W, H)
bim.pixels = np.flipud(img).ravel().tolist()
bim.filepath_raw = os.path.join(UIT, "GR_sprietkleur.png"); bim.file_format = "PNG"; bim.save()

def plukje(naam, zaad, n=50, straal=0.15, hmin=0.05, hmax=0.11):
    rnd = random.Random(zaad)
    me = bpy.data.meshes.new(naam); bm = bmesh.new(); uvl = bm.loops.layers.uv.new()
    normalen = []
    for i in range(n):
        r = straal * math.sqrt(rnd.random()); a = rnd.random() * 2 * math.pi
        x0, y0 = r * math.cos(a), r * math.sin(a)
        h = rnd.uniform(hmin, hmax); w = rnd.uniform(0.008, 0.013)
        rich = rnd.random() * 2 * math.pi                          # vlak van de spriet
        dx, dy = math.cos(rich), math.sin(rich)                    # breedte-as
        buig = rnd.uniform(0.15, 0.55)                             # hoeveel hij overhelt
        bx, by = -dy, dx                                           # buigrichting loodrecht op de breedte
        if rnd.random() < 0.5: bx, by = -bx, -by
        kol = rnd.randrange(8); u0, u1 = (kol * 8 + 1) / W, (kol * 8 + 7) / W
        pts = []
        for s, t in enumerate((0.0, 0.4, 0.75, 1.0)):
            off = buig * h * t * t                                  # kromme
            cx, cy, cz = x0 + bx * off, y0 + by * off, h * t * (1 - 0.25 * buig * t)
            hw = w * (1 - t) ** 0.8 / 2
            pts.append(((cx - dx * hw, cy - dy * hw, cz), (cx + dx * hw, cy + dy * hw, cz), t))
        for kant in (0,):   # Roblox tekent MeshParts dubbelzijdig (DoubleSided): achterkant niet nodig
            vs = []
            for (l, rr, t) in pts:
                vs.append((bm.verts.new(l), bm.verts.new(rr), t))
            for s in range(3):
                (a1, b1, t1), (a2, b2, t2) = vs[s], vs[s + 1]
                quads = [(a1, b1, b2), (a1, b2, a2)] if s < 2 else [(a1, b1, a2)]
                for tri in quads:
                    if kant: tri = tuple(reversed(tri))
                    f = bm.faces.new(tri)
                    for lp in f.loops:
                        v = lp.vert; tt = v.co.z / h if h else 0
                        isl = any(v is q[0] for q in vs)
                        lp[uvl].uv = (u0 if isl else u1, min(1.0, max(0.0, tt)))
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(naam, me); bpy.context.collection.objects.link(ob)
    # normalen half naar boven
    me.calc_loop_triangles() if hasattr(me, "calc_loop_triangles") else None
    cn = []
    for p in me.polygons:
        nrm = Vector(p.normal); nrm = (nrm * 0.45 + Vector((0, 0, 1)) * 0.55).normalized()
        cn.extend([nrm] * len(p.loop_indices))
    try: me.normals_split_custom_set(cn)
    except Exception as e: print("normalen", e)
    mat = bpy.data.materials.get("GR_spriet") or bpy.data.materials.new("GR_spriet")
    me.materials.append(mat)
    return ob, len(me.polygons)

bpy.ops.wm.read_factory_settings(use_empty=True)
bim2 = bpy.data.images.load(os.path.join(UIT, "GR_sprietkleur.png"))
mat = bpy.data.materials.new("GR_spriet"); mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
tx = mat.node_tree.nodes.new("ShaderNodeTexImage"); tx.image = bim2
mat.node_tree.links.new(tx.outputs[0], bsdf.inputs[0])
uit = []
for k in range(3):
    ob, nf = plukje(f"GR_plukje{k}", 1000 + k)
    ob.location = (k * 0.4, 0, 0); uit.append((ob.name, nf))
for o in bpy.data.objects: o.select_set(True)
# los exporteren per plukje (oorsprong = midden voet)
for o in bpy.data.objects:
    for p in bpy.data.objects: p.select_set(p == o)
    loc = o.location.copy(); o.location = (0, 0, 0)
    bpy.ops.export_scene.fbx(filepath=os.path.join(UIT, o.name + ".fbx"), use_selection=True, global_scale=1.0,
                             apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y', object_types={'MESH'},
                             mesh_smooth_type='OFF', use_custom_props=False, add_leaf_bones=False)
    o.location = loc
# review-render
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(UIT, "GR_plukjes.blend"))
print("plukjes", uit)
