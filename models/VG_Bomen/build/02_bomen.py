"""02_bomen: zes boomsoorten (stam+takken van schors, kroon van bladkaarten) op een vaste hoogte van 15 m.
Gebruik: Blender -b -P 02_bomen.py -- [--render] [--export]
Uit: models/VG_Bomen/VB_bomen.blend, exports/VB_bomen.fbx (objecten VB_<soort>_stam / VB_<soort>_kroon, oorsprong = stamvoet),
     exports/maten.json (per object bbox-min/-max in m; nodig om in Roblox op de stamvoet te plaatsen), review/render_bomen.png.
Blender-assen: z omhoog. Per soort: stam (taps, licht gebogen), hoofdtakken naar de kroonschil, kaarten vooral in de buitenste schil
(steel naar binnen, blad naar buiten), dubbelzijdig (Roblox toont alleen voorkanten)."""
import bpy, bmesh, os, sys, json, math, random
from mathutils import Vector, Matrix
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); T = os.path.join(D, 'textures')
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
H0 = 15.0

# vorm: stamhoogte (kroonbasis), kroon (type, straal, top), stamdikte, aantal kaarten, kaartgrootte, takken
SOORT = {
    'beuk':     dict(basis=4.5, kroon='ei', r=5.2, dik=0.62, kaarten=480, kaart=3.0, takken=9, krom=0.05),
    'eik':      dict(basis=3.5, kroon='breed', r=6.0, dik=0.75, kaarten=480, kaart=3.0, takken=8, krom=0.18),
    'kastanje': dict(basis=3.2, kroon='koepel', r=5.4, dik=0.66, kaarten=440, kaart=3.0, takken=8, krom=0.08),
    'berk':     dict(basis=5.0, kroon='smal', r=2.8, dik=0.32, kaarten=380, kaart=2.4, takken=7, krom=0.08),
    'den':      dict(basis=9.0, kroon='scherm', r=3.8, dik=0.48, kaarten=300, kaart=2.7, takken=6, krom=0.12),
    'spar':     dict(basis=1.2, kroon='kegel', r=3.2, dik=0.42, kaarten=560, kaart=2.5, takken=0, krom=0.0),
}

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
COL = bpy.data.collections.new('BOMEN'); sc.collection.children.link(COL)


def materiaal(naam, alfa):
    m = bpy.data.materials.new(naam); m.use_nodes = True; nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    def img(s, kleur=True):
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(os.path.join(T, f'{naam}_{s}.png'))
        if not kleur: n.image.colorspace_settings.name = 'Non-Color'
        return n
    k = img('kleur'); nt.links.new(k.outputs['Color'], b.inputs['Base Color'])
    if alfa:
        nt.links.new(k.outputs['Alpha'], b.inputs['Alpha'])
        try: m.surface_render_method = 'DITHERED'
        except Exception: pass
        try: b.inputs['Subsurface Weight'].default_value = 0.0
        except Exception: pass
    r = img('ruw', False); nt.links.new(r.outputs['Color'], b.inputs['Roughness'])
    nn = img('normaal', False); nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(nn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m


def buis(bm, uvl, pad, r0, r1, zijden=7, vtile=2.0):
    """Taps buisje langs punten pad (lijst Vector), van straal r0 naar r1. UV: u rond, v langs (1 tegel per vtile m)."""
    ringen = []; s = 0.0; lengte = [0.0]
    for a, b in zip(pad[:-1], pad[1:]): s += (b - a).length; lengte.append(s)
    for i, p in enumerate(pad):
        t = lengte[i] / max(s, 1e-6); r = r0 + (r1 - r0) * t
        d = (pad[min(i + 1, len(pad) - 1)] - pad[max(i - 1, 0)]).normalized()
        a = d.orthogonal().normalized(); b = d.cross(a).normalized()
        ring = [bm.verts.new(p + (a * math.cos(2 * math.pi * k / zijden) + b * math.sin(2 * math.pi * k / zijden)) * r) for k in range(zijden)]
        ringen.append((ring, lengte[i]))
    for (r_a, la), (r_b, lb) in zip(ringen[:-1], ringen[1:]):
        for k in range(zijden):
            k2 = (k + 1) % zijden
            f = bm.faces.new((r_a[k], r_a[k2], r_b[k2], r_b[k]))
            for l, (u, v) in zip(f.loops, ((k / zijden, la / vtile), ((k + 1) / zijden, la / vtile), ((k + 1) / zijden, lb / vtile), (k / zijden, lb / vtile))):
                l[uvl].uv = (u, v)


def schil(p, rnd):
    """Willekeurig punt in de kroon (park-m t.o.v. stamvoet), vooral in de buitenste schil."""
    vorm = p['kroon']; R = p['r']; B = p['basis']; Hk = H0 - B
    for _ in range(100):
        u = rnd.random() ** 0.35                       # 0..1, vooral naar buiten
        th = rnd.uniform(0, 2 * math.pi); ph = math.acos(rnd.uniform(-1, 1))
        x, y, z = math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)
        if vorm == 'ei':     c = Vector((x * R, y * R, B + Hk * 0.5 + z * Hk * 0.5))
        elif vorm == 'breed': c = Vector((x * R, y * R, B + Hk * 0.55 + z * Hk * 0.45))
        elif vorm == 'koepel': c = Vector((x * R, y * R, B + Hk * 0.45 + max(z, -0.6) * Hk * 0.55))
        elif vorm == 'smal': c = Vector((x * R, y * R, B + Hk * 0.5 + z * Hk * 0.5))
        elif vorm == 'scherm': c = Vector((x * R, y * R, B + Hk * 0.55 + z * Hk * 0.45 * 0.8))
        else:  # kegel: straal neemt lineair af naar de top
            zz = rnd.random() ** 0.8; rr = R * (1 - zz) * 1.05
            c = Vector((x * rr, y * rr, B + zz * (H0 - B)))
            mid = Vector((0, 0, c.z)); return mid + (c - mid) * u, mid
        mid = Vector((0, 0, c.z * 0.7 + (B + Hk * 0.5) * 0.3))
        return mid + (c - mid) * u, mid
    return Vector((0, 0, H0)), Vector((0, 0, H0))


def kaart_quad(bm, uvl, voet, richting, breed, lang, rnd, hang=0.0):
    """Bladkaart: steel op 'voet', groeit in 'richting'; vlak gedraaid om de groeirichting; dubbelzijdig."""
    d = richting.normalized()
    if hang: d = (d + Vector((0, 0, -hang))).normalized()
    zij = d.cross(Vector((0, 0, 1)))
    if zij.length < 1e-3: zij = Vector((1, 0, 0))
    zij.normalize(); zij = Matrix.Rotation(rnd.uniform(-0.9, 0.9), 3, d) @ zij
    a = voet - zij * breed / 2; b = voet + zij * breed / 2; c = b + d * lang; e = a + d * lang
    for orde in ((0, 1, 2, 3), (1, 0, 3, 2)):
        vs = [bm.verts.new(v) for v in (a, b, c, e)]   # eigen hoekpunten per kant (achterkant)
        f = bm.faces.new([vs[i] for i in orde])
        uv = {0: (0, 0), 1: (1, 0), 2: (1, 1), 3: (0, 1)}
        for l, i in zip(f.loops, orde): l[uvl].uv = uv[i]


maten = {}
for i, (s, p) in enumerate(SOORT.items()):
    rnd = random.Random(1952 + i)
    # --- stam en takken
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap')
    top = H0 * (0.92 if p['kroon'] != 'kegel' else 0.99)
    stam = [Vector((p['krom'] * math.sin(t * 2.3) * t * 2, p['krom'] * math.cos(t * 1.7) * t, t * top)) for t in [k / 10 for k in range(11)]]
    buis(bm, uvl, stam, p['dik'] / 2, p['dik'] * 0.12, 9)
    # wortelaanloop
    buis(bm, uvl, [Vector((0, 0, -0.3)), Vector((0, 0, 0.6))], p['dik'] * 0.75, p['dik'] / 2, 9)
    eindpunten = []
    for k in range(p['takken']):
        t0 = (p['basis'] + (top - p['basis']) * (0.05 + 0.6 * k / max(p['takken'], 1))) / top
        a = stam[0].lerp(stam[-1], t0) if False else Vector((stam[int(t0 * 10)].x, stam[int(t0 * 10)].y, t0 * top))
        doel, _ = schil(p, rnd); doel = Vector((doel.x, doel.y, max(doel.z, a.z + 0.5)))
        mid = a.lerp(doel, 0.5) + Vector((rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), 0.6 + p['krom'] * 3))
        pad = [a, a.lerp(mid, 0.5), mid, mid.lerp(doel, 0.5), doel]
        buis(bm, uvl, pad, p['dik'] * 0.28, p['dik'] * 0.05, 6)
        eindpunten.append(doel)
        for _ in range(2):   # zijtakjes
            b0 = mid.lerp(doel, rnd.uniform(0.2, 0.7)); b1 = b0 + (doel - a).normalized() * rnd.uniform(1.0, 2.2) + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.2, 0.8)))
            buis(bm, uvl, [b0, b0.lerp(b1, 0.5), b1], p['dik'] * 0.09, p['dik'] * 0.03, 5)
    if p['kroon'] == 'kegel':   # spar: kransen van korte, hangende takken
        for zk in [p['basis'] + j * 0.9 for j in range(int((H0 - p['basis']) / 0.9))]:
            rr = p['r'] * (1 - (zk - p['basis']) / (H0 - p['basis'])) * 0.95
            for q in range(5):
                th = q * 2 * math.pi / 5 + zk; e = Vector((math.cos(th) * rr, math.sin(th) * rr, zk - rr * 0.25))
                buis(bm, uvl, [Vector((0, 0, zk)), Vector((e.x * 0.5, e.y * 0.5, zk + 0.05)), e], p['dik'] * 0.08, p['dik'] * 0.02, 4)
    me = bpy.data.meshes.new(f'VB_{s}_stam'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(f'VB_{s}_stam', me); COL.objects.link(ob); me.materials.append(materiaal(f'VB_{s}_schors', False))
    # --- kroon: kaarten
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap')
    for k in range(p['kaarten']):
        c, mid = schil(p, rnd)
        naar_buiten = (c - mid); naar_buiten.z = naar_buiten.z * 0.6 + 0.35 * naar_buiten.length
        if naar_buiten.length < 1e-3: naar_buiten = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0.5))
        L = p['kaart'] * rnd.uniform(0.75, 1.15)
        hang = {'berk': 0.9, 'spar': 0.5, 'beuk': 0.15}.get(s, 0.05)
        voet = c - naar_buiten.normalized() * L * 0.45
        kaart_quad(bm, uvl, voet, naar_buiten, L * 0.85, L, rnd, hang)
    me = bpy.data.meshes.new(f'VB_{s}_kroon'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(f'VB_{s}_kroon', me); COL.objects.link(ob); me.materials.append(materiaal(f'VB_{s}_blad', True))
    for o in (f'VB_{s}_stam', f'VB_{s}_kroon'):
        obj = bpy.data.objects[o]; vs = [v.co for v in obj.data.vertices]
        maten[o] = {'min': [min(v[j] for v in vs) for j in range(3)], 'max': [max(v[j] for v in vs) for j in range(3)], 'tris': sum(len(f.vertices) - 2 for f in obj.data.polygons)}
    print(s, 'stam', maten[f'VB_{s}_stam']['tris'], 'kroon', maten[f'VB_{s}_kroon']['tris'], 'driehoeken')

os.makedirs(os.path.join(D, 'exports'), exist_ok=True); os.makedirs(os.path.join(D, 'review'), exist_ok=True)
json.dump({'H0': H0, 'objecten': maten, 'soorten': {s: {'r': p['r'], 'basis': p['basis']} for s, p in SOORT.items()}}, open(os.path.join(D, 'exports', 'maten.json'), 'w'), indent=1)

if '--render' in args:
    # rijtje naast elkaar, ooghoogte-achtig + zon
    for j, s in enumerate(SOORT):
        for o in ('stam', 'kroon'): bpy.data.objects[f'VB_{s}_{o}'].location = (j * 13 - 32, 0, 0)
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND'); bg.inputs['Color'].default_value = (0.62, 0.72, 0.86, 1); bg.inputs['Strength'].default_value = 1.0
    zon = bpy.data.objects.new('zon', bpy.data.lights.new('zon', 'SUN')); zon.data.energy = 3.0; zon.rotation_euler = (math.radians(45), 0, math.radians(35)); sc.collection.objects.link(zon)
    bpy.ops.mesh.primitive_plane_add(size=120); g = bpy.context.active_object
    gm = bpy.data.materials.new('gras'); gm.use_nodes = True; next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (0.1, 0.16, 0.05, 1); g.data.materials.append(gm)
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 28; cam.location = (0, -62, 9); cam.rotation_euler = (math.radians(86), 0, 0)
    try: sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError: sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = 1600, 700
    sc.render.filepath = os.path.join(D, 'review', 'render_bomen.png'); bpy.ops.render.render(write_still=True)
    for j, s in enumerate(SOORT):
        for o in ('stam', 'kroon'): bpy.data.objects[f'VB_{s}_{o}'].location = (0, 0, 0)
    for o in ('zon', 'cam', g.name): bpy.data.objects.remove(bpy.data.objects[o])

if '--export' in args:
    bpy.ops.object.select_all(action='DESELECT')
    for o in COL.objects: o.select_set(True)
    bpy.context.view_layer.objects.active = COL.objects[0]
    bpy.ops.export_scene.fbx(filepath=os.path.join(D, 'exports', 'VB_bomen.fbx'), use_selection=True, global_scale=1.0, apply_scale_options='FBX_SCALE_ALL',
                             apply_unit_scale=True, axis_forward='-Z', axis_up='Y', object_types={'MESH'}, mesh_smooth_type='FACE', path_mode='COPY', embed_textures=False, add_leaf_bones=False)
    print('EXPORT ok')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'VB_bomen.blend'))
