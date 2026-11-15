"""04_blender: paden_mesh.json -> Blender (PD_paden.blend), keuringsrenders en FBX voor Roblox.
Gebruik: Blender -b -P 04_blender.py -- [--render x y tx ty naam]... [--export]
  --render: camera op ooghoogte (1,6 m) op park-m (x,y) kijkend naar (tx,ty); naam 'boven' = bovenaanzicht rond (x,y), straal tx.
Blender-coördinaten: bx = -x_park, by = -y_park, bz = Roblox-Y/3 (zo komt Blender (x,y,z) in Roblox op (-x,z,y)*3 = (3x_park, Y, -3y_park))."""
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, os.path.join(R, 'tools')); import veld
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
T = os.path.join(D, 'textures')

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
PAD = bpy.data.collections.new('PADEN'); sc.collection.children.link(PAD)
HULP = bpy.data.collections.new('HULP'); sc.collection.children.link(HULP)


def materiaal(naam, alfa=False):
    m = bpy.data.materials.new('PD_' + naam); m.use_nodes = True
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    def img(suffix, kleur=True):
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(os.path.join(T, f'PD_{naam}_{suffix}.png'))
        if not kleur: n.image.colorspace_settings.name = 'Non-Color'
        return n
    k = img('kleur'); nt.links.new(k.outputs['Color'], b.inputs['Base Color'])
    if alfa:
        nt.links.new(k.outputs['Alpha'], b.inputs['Alpha'])
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    r = img('ruw', False); nt.links.new(r.outputs['Color'], b.inputs['Roughness'])
    nn = img('normaal', False); nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(nn.outputs['Color'], nm.inputs['Color'])
    nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m


MATS = {k: materiaal(k, k == 'rand') for k in ('klinker', 'kassei', 'asfalt', 'kantsteen', 'rand')}
data = json.load(open(os.path.join(D, 'exports', 'paden_mesh.json')))
ntri = 0
for naam, st in data.items():
    P = np.array(st['tri']); UV = np.array(st['uv'])
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap'); vm = {}
    for i in range(0, len(P), 3):
        vs = []
        for p in P[i:i + 3]:
            key = (round(p[0], 3), round(p[1], 3), round(p[2], 3))
            if key not in vm: vm[key] = bm.verts.new(key)
            vs.append(vm[key])
        if len(set(vs)) < 3: continue
        try: f = bm.faces.new(vs)
        except ValueError: continue
        for l, uv in zip(f.loops, UV[i:i + 3]): l[uvl].uv = (float(uv[0]), float(uv[1]))
    me = bpy.data.meshes.new(naam); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('PD_' + naam, me); ob.data.materials.append(MATS[st['mat']]); PAD.objects.link(ob)
    ntri += len(me.polygons)
print('PADEN objecten', len(data), 'driehoeken', ntri)


def terrein(cx, cy, r):
    """Hulpterrein (alleen voor renders) op het AHN-veld, 1 m raster, iets onder het pad."""
    xs = np.arange(cx - r, cx + r + 1, 1.0); ys = np.arange(cy - r, cy + r + 1, 1.0)
    X, Y = np.meshgrid(xs, ys); Z = veld.maaiveld_studs(X, Y) / 3 - 0.02
    bm = bmesh.new(); V = [[bm.verts.new((-X[j, i], -Y[j, i], Z[j, i])) for i in range(len(xs))] for j in range(len(ys))]
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1): bm.faces.new((V[j][i], V[j + 1][i], V[j + 1][i + 1], V[j][i + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.z < 0: f.normal_flip()
    me = bpy.data.meshes.new('terrein'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('HULP_terrein', me); HULP.objects.link(ob)
    m = bpy.data.materials.new('HULP_gras'); m.use_nodes = True; b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (0.09, 0.16, 0.05, 1); b.inputs['Roughness'].default_value = 0.95
    ob.data.materials.append(m)


def licht():
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND'); bg.inputs['Color'].default_value = (0.55, 0.65, 0.8, 1); bg.inputs['Strength'].default_value = 0.9
    s = bpy.data.objects.new('zon', bpy.data.lights.new('zon', 'SUN')); s.data.energy = 3.5
    s.rotation_euler = (math.radians(50), 0, math.radians(30)); HULP.objects.link(s)
    try: sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError: sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.view_settings.view_transform = 'AgX' if 'AgX' in [i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'


i = 0; renders = []
while '--render' in args[i:]:
    k = args.index('--render', i); x, y, tx, ty = map(float, args[k + 1:k + 5]); naam = args[k + 5]; renders.append((x, y, tx, ty, naam)); i = k + 6
if renders:
    licht()
    for x, y, tx, ty, naam in renders:
        for o in list(HULP.objects):
            if o.name.startswith('HULP_terrein'): bpy.data.objects.remove(o)
        cam = bpy.data.objects.new('cam_' + naam, bpy.data.cameras.new('cam_' + naam)); HULP.objects.link(cam); sc.camera = cam
        if naam.startswith('boven'):
            terrein(x, y, tx + 5)
            cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2 * tx; z = float(veld.maaiveld_studs(x, y)) / 3
            cam.location = (-x, -y, z + 60); cam.rotation_euler = (0, 0, math.radians(180))
            sc.render.resolution_x = sc.render.resolution_y = 1024
        else:
            terrein(x, y, 45)
            z = float(veld.maaiveld_studs(x, y)) / 3 + 1.6; zt = float(veld.maaiveld_studs(tx, ty)) / 3 + 0.6
            cam.data.lens = 24; cam.location = (-x, -y, z)
            d = Vector((-tx, -ty, zt)) - cam.location; cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
            sc.render.resolution_x, sc.render.resolution_y = 1280, 720
        sc.render.filepath = os.path.join(D, 'review', f'render_{naam}.png')
        bpy.ops.render.render(write_still=True); print('RENDER', sc.render.filepath)

if '--export' in args:
    for o in list(HULP.objects): bpy.data.objects.remove(o)
    am = bpy.data.materials.new('MAT_anker'); abm = bmesh.new(); bmesh.ops.create_cube(abm, size=0.2)
    bmesh.ops.translate(abm, vec=(0, 0, -2), verts=abm.verts); ame = bpy.data.meshes.new('anker'); abm.to_mesh(ame); abm.free()
    ame.materials.append(am); a = bpy.data.objects.new('MAT_anker', ame); PAD.objects.link(a)
    bpy.ops.object.select_all(action='DESELECT')
    for o in PAD.objects: o.select_set(True)
    bpy.context.view_layer.objects.active = a
    out = os.path.join(D, 'exports', 'PD_paden.fbx')
    bpy.ops.export_scene.fbx(filepath=out, use_selection=True, global_scale=1.0, apply_scale_options='FBX_SCALE_ALL', apply_unit_scale=True,
                             axis_forward='-Z', axis_up='Y', object_types={'MESH'}, mesh_smooth_type='FACE', use_mesh_modifiers=True,
                             path_mode='COPY', embed_textures=False, add_leaf_bones=False)
    print('EXPORT', out, os.path.getsize(out))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'PD_paden.blend'))
