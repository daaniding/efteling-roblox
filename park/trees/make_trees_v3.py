"""
Realistische low/mid-poly bomen voor Roblox, 1 unit = 1 m.
- Recursieve vertakking (stam -> takken -> twijgen) als buizen met cilindrische UV's voor schors.
- Bladeren als dubbelzijdige kaarten (quads) met UV 0..1 voor een bladcluster-textuur met alpha.
- Texturen worden hier gerenderd: bladclusters (ortho render, transparante film) en schors (procedureel gebakken).
Soorten: eik, beuk, berk, kastanje (breed, grof blad), den (naaldclusters). Struiken: rododendron, taxus, varenpol.
Gebruik: Blender --background --python make_trees_v2.py -- <outdir>
"""
import bpy, bmesh, math, random, sys, os
from mathutils import Vector, Matrix

OUT = sys.argv[sys.argv.index("--") + 1]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_homefile(use_empty=True)
sc = bpy.context.scene
random.seed(11)

# ------------------------------------------------------------------ materialen
def mat(name, rgb, rough=0.8):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    return m

def image_mat(name, img_path, alpha=True):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(img_path)
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    if alpha:
        nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"]); m.blend_method = "CLIP"
        if hasattr(m, "shadow_method"): m.shadow_method = "CLIP"
    b.inputs["Roughness"].default_value = 0.75
    m.use_backface_culling = False
    return m

# ------------------------------------------------------------------ textuur: bladcluster renderen
def render_leaf_cluster(path, leaf_color, kind="broad", n=28, size=512):
    """Rendert een cluster blaadjes/naalden op transparante achtergrond naar PNG."""
    s2 = bpy.data.scenes.new("LeafRender"); bpy.context.window.scene = s2 if bpy.context.window else None
    s2.render.engine = "BLENDER_EEVEE"; s2.render.film_transparent = True
    s2.render.resolution_x = size; s2.render.resolution_y = size; s2.render.image_settings.color_mode = "RGBA"
    s2.view_settings.view_transform = "Standard"
    cam = bpy.data.objects.new("LC", bpy.data.cameras.new("LC")); s2.collection.objects.link(cam)
    cam.data.type = "ORTHO"; cam.data.ortho_scale = 1.0; cam.location = (0, 0, 5); s2.camera = cam
    sun = bpy.data.objects.new("LS", bpy.data.lights.new("LS", "SUN")); s2.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(20), math.radians(10), 0); sun.data.energy = 3.0
    w = bpy.data.worlds.new("LW"); s2.world = w; w.use_nodes = True
    bgn = next(nn for nn in w.node_tree.nodes if nn.type == "BACKGROUND"); bgn.inputs[0].default_value = (0.6, 0.7, 0.6, 1); bgn.inputs[1].default_value = 0.6
    lm = bpy.data.materials.new("LeafTex"); lm.use_nodes = True; nt = lm.node_tree
    b = next(nn for nn in nt.nodes if nn.type == "BSDF_PRINCIPLED"); b.inputs["Roughness"].default_value = 0.6
    # kleurvariatie per blad via Object Info random
    oi = nt.nodes.new("ShaderNodeObjectInfo"); ramp = nt.nodes.new("ShaderNodeValToRGB")
    c = leaf_color; ramp.color_ramp.elements[0].color = (c[0] * 0.65, c[1] * 0.7, c[2] * 0.6, 1); ramp.color_ramp.elements[1].color = (min(1, c[0] * 1.25), min(1, c[1] * 1.2), min(1, c[2] * 1.1), 1)
    nt.links.new(oi.outputs["Random"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    # nerf: lichte streep door bump van gradient
    lm.use_backface_culling = False
    rnd = random.Random(7)
    for i in range(n):
        bm = bmesh.new()
        if kind == "broad":
            # bladvorm: ovaal met punt, 16 punten
            pts = []
            for k in range(16):
                t = k / 16 * 2 * math.pi
                r = 0.5 * (1 + 0.25 * math.cos(t) - 0.15 * math.cos(2 * t))
                pts.append((r * math.sin(t) * 0.55, r * math.cos(t) * 1.0 + 0.1, 0))
            bm.faces.new([bm.verts.new(p) for p in pts])
            scale = rnd.uniform(0.16, 0.26)
        elif kind == "lobed":   # eik: gelobd blad
            pts = []
            for k in range(28):
                t = k / 28 * 2 * math.pi
                r = 0.5 * (1 + 0.18 * math.cos(t) + 0.22 * abs(math.sin(3.5 * t)) * (1 - 0.5 * math.cos(t)))
                pts.append((r * math.sin(t) * 0.6, r * math.cos(t) + 0.1, 0))
            bm.faces.new([bm.verts.new(p) for p in pts]); scale = rnd.uniform(0.18, 0.28)
        elif kind == "palmate":  # kastanje: 5 vingers
            for f in range(5):
                a = math.radians(-60 + f * 30); L = 0.55 if f in (1, 2, 3) else 0.42
                q = [(0, 0.05), (0.08, 0.25 * L / 0.55), (0.055, L), (0, L + 0.07), (-0.055, L), (-0.08, 0.25 * L / 0.55)]
                bm.faces.new([bm.verts.new((x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), 0)) for x, y in q])
            scale = rnd.uniform(0.3, 0.42)
        else:  # naalden: bundel dunne strookjes
            for f in range(9):
                a = math.radians(rnd.uniform(-70, 70)); L = rnd.uniform(0.35, 0.6)
                q = [(-0.012, 0), (0.012, 0), (0.006, L), (-0.006, L)]
                bm.faces.new([bm.verts.new((x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), 0)) for x, y in q])
            scale = rnd.uniform(0.25, 0.35)
        me = bpy.data.meshes.new("leaf"); bm.to_mesh(me); bm.free(); me.materials.append(lm)
        o = bpy.data.objects.new("leaf%d" % i, me); s2.collection.objects.link(o)
        ang = rnd.uniform(0, 2 * math.pi); rad = rnd.uniform(0, 0.36) if i > 0 else 0
        o.location = (rad * math.cos(ang), rad * math.sin(ang), rnd.uniform(0, 0.4))
        o.rotation_euler = (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), rnd.uniform(0, 2 * math.pi))
        o.scale = (scale, scale, scale)
    s2.render.filepath = path
    bpy.ops.render.render(write_still=True, scene=s2.name)
    for o in list(s2.collection.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(s2)

# ------------------------------------------------------------------ textuur: schors bakken
def bake_bark(path, base, dark, size=512, stretch=6.0):
    """Procedurele schors (verticaal gerekte voronoi + noise) gebakken naar een tegelbare PNG via emissie-render."""
    s2 = bpy.data.scenes.new("BarkRender"); s2.render.engine = "BLENDER_EEVEE"
    s2.render.resolution_x = size; s2.render.resolution_y = size; s2.view_settings.view_transform = "Standard"
    cam = bpy.data.objects.new("BC", bpy.data.cameras.new("BC")); s2.collection.objects.link(cam)
    cam.data.type = "ORTHO"; cam.data.ortho_scale = 1.0; cam.location = (0, 0, 2); s2.camera = cam
    m = bpy.data.materials.new("BarkTex"); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 1.0 / stretch, 1.0)
    vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = "DISTANCE_TO_EDGE"; vor.inputs["Scale"].default_value = 14.0
    noi = nt.nodes.new("ShaderNodeTexNoise"); noi.inputs["Scale"].default_value = 14.0; noi.inputs["Detail"].default_value = 8.0; noi.inputs["Roughness"].default_value = 0.7
    mix = nt.nodes.new("ShaderNodeMixRGB"); mix.blend_type = "MULTIPLY"; mix.inputs["Fac"].default_value = 0.7
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = 0.22; ramp.color_ramp.elements[1].color = (*base, 1)
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], vor.inputs["Vector"]); nt.links.new(tc.outputs["UV"], noi.inputs["Vector"])
    nt.links.new(vor.outputs["Distance"], mix.inputs[1]); nt.links.new(noi.outputs["Fac"], mix.inputs[2]); nt.links.new(mix.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"]); nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5); me = bpy.data.meshes.new("bq"); bm.to_mesh(me); bm.free()
    uv = me.uv_layers.new();
    for li, co in zip(me.polygons[0].loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[li].uv = co
    me.materials.append(m); o = bpy.data.objects.new("bq", me); s2.collection.objects.link(o)
    s2.render.filepath = path; bpy.ops.render.render(write_still=True, scene=s2.name)
    bpy.data.objects.remove(o, do_unlink=True); bpy.data.scenes.remove(s2)

# ------------------------------------------------------------------ boomgenerator
class TreeSpec:
    def __init__(self, **k): self.leaf_from = 0.5; self.__dict__.update(k)

def tube_segment(bm, uv_layer, p0, p1, r0, r1, segs, v0, v1, ring_prev=None):
    """Voegt een conische buis toe tussen p0 en p1; geeft de bovenring terug voor aansluiting. UV: u rondom, v langs."""
    d = (p1 - p0); L = d.length
    if L < 1e-6: return ring_prev
    z = d.normalized(); up = Vector((0, 0, 1)) if abs(z.z) < 0.95 else Vector((1, 0, 0))
    x = up.cross(z).normalized(); y = z.cross(x)
    ring1 = [bm.verts.new(p1 + (x * math.cos(a) + y * math.sin(a)) * r1) for a in [i * 2 * math.pi / segs for i in range(segs)]]
    if ring_prev is None:
        ring0 = [bm.verts.new(p0 + (x * math.cos(a) + y * math.sin(a)) * r0) for a in [i * 2 * math.pi / segs for i in range(segs)]]
    else:
        ring0 = ring_prev
    for i in range(segs):
        f = bm.faces.new((ring0[i], ring0[(i + 1) % segs], ring1[(i + 1) % segs], ring1[i]))
        us = [i / segs, (i + 1) / segs, (i + 1) / segs, i / segs]; vs = [v0, v0, v1, v1]
        for loop, u, v in zip(f.loops, us, vs): loop[uv_layer].uv = (u, v)
    return ring1

def grow(spec, rnd):
    """Bouwt takken (bm_wood) en bladkaarten (bm_leaf). Recursief, met zwaartekracht/fototropie per soort."""
    bm_w = bmesh.new(); uvw = bm_w.loops.layers.uv.new("UVMap")
    bm_l = bmesh.new(); uvl = bm_l.loops.layers.uv.new("UVMap")
    leaves = []
    def branch(p, d, length, radius, level, vstart):
        n = max(3, int(length / 0.9))
        pos = p.copy(); dirv = d.copy(); ring = None; v = vstart
        pts = []
        for k in range(n):
            t = k / n
            # kromming: zwaartekracht omlaag voor zware takken, naar boven voor twijgen
            g = Vector((0, 0, -spec.gravity * (1 - t) if level > 0 else 0.0))
            up = Vector((0, 0, spec.phototropism * level))
            wobble = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.3, 0.6))) * spec.wobble
            dirv = (dirv + g * 0.15 + up * 0.08 + wobble * 0.12).normalized()
            seg = length / n
            newpos = pos + dirv * seg
            r0 = radius * (1 - t * spec.taper); r1 = radius * (1 - (t + 1 / n) * spec.taper)
            segs = 7 if level == 0 else (5 if level == 1 else 3)
            if radius > 0.012:
                ring = tube_segment(bm_w, uvw, pos, newpos, r0, r1, segs, v, v + seg / (2 * math.pi * max(r0, 0.05)) * 0.5, ring)
                v += seg / (2 * math.pi * max(r0, 0.05)) * 0.5
            pts.append((pos.copy(), newpos.copy(), dirv.copy(), r1, t))
            pos = newpos
        # kinderen
        if level < spec.levels:
            nchild = int(spec.children[level] * rnd.uniform(0.8, 1.25))
            for c in range(nchild):
                i = rnd.randint(max(1, int(n * spec.child_start)), n - 1)
                p0, p1, dv, r1, t = pts[i]
                ang = rnd.uniform(0, 2 * math.pi)
                # richting: weg van de ouder onder spreidingshoek
                side = dv.cross(Vector((0, 0, 1)) if abs(dv.z) < 0.95 else Vector((1, 0, 0))).normalized()
                side = side.rotated if False else side
                rot = Matrix.Rotation(ang, 4, dv)
                side = (rot @ side).normalized()
                spread = math.radians(spec.spread[level] * rnd.uniform(0.75, 1.25))
                cd = (dv * math.cos(spread) + side * math.sin(spread)).normalized()
                cl = length * spec.child_len[level] * rnd.uniform(0.7, 1.15) * (1 - 0.35 * t)
                cr = max(0.008, r1 * spec.child_rad * rnd.uniform(0.8, 1.1))
                branch(p1.copy(), cd, cl, cr, level + 1, 0.0)
        # bladeren op de buitenste niveaus
        if level >= spec.leaf_level:
            for (p0, p1, dv, r1, t) in pts:
                if level < spec.levels and t < spec.leaf_from: continue
                cnt = spec.leaves_per_seg if level == spec.levels else max(1, spec.leaves_per_seg // 2)
                for _ in range(cnt):
                    leaves.append((p1 + Vector((rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), rnd.uniform(-0.3, 0.5))) * spec.leaf_size, dv))
    trunk_dir = Vector((rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05), 1)).normalized()
    branch(Vector((0, 0, 0)), trunk_dir, spec.height, spec.trunk_r, 0, 0.0)
    # wortelaanzet: verbrede ring onderaan
    # bladkaarten: gekruiste quads (2 vlakken per cluster), willekeurig gedraaid
    S = spec.leaf_size
    for (c, dv) in leaves:
        for k in range(2):
            a = rnd.uniform(0, math.pi); tilt = rnd.uniform(-0.6, 0.6)
            R = Matrix.Rotation(a, 3, "Z") @ Matrix.Rotation(tilt, 3, "X")
            corners = [Vector((-S * 1.2, 0, -S * 0.3)), Vector((S * 1.2, 0, -S * 0.3)), Vector((S * 1.2, 0, S * 2.0)), Vector((-S * 1.2, 0, S * 2.0))]
            if k == 1: corners = [Vector((0, cc.x, cc.z)) for cc in corners]
            vs = [bm_l.verts.new(c + R @ cc) for cc in corners]
            f = bm_l.faces.new(vs)
            for loop, uvco in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]): loop[uvl].uv = uvco
    bmesh.ops.recalc_face_normals(bm_w, faces=bm_w.faces)
    return bm_w, bm_l, len(leaves)

SPECIES = {
    "eik":      TreeSpec(height=5.5, trunk_r=0.42, taper=0.55, levels=3, children=(5, 4, 3), spread=(48, 42, 40), child_len=(0.85, 0.7, 0.55), child_start=0.35, child_rad=0.55, gravity=0.25, phototropism=0.25, wobble=0.45, leaf_level=1, leaf_from=0.55, leaves_per_seg=3, leaf_size=0.78, leaf_kind="lobed", leaf_color=(0.22, 0.40, 0.14), bark=((0.36, 0.30, 0.24), (0.14, 0.11, 0.08))),
    "beuk":     TreeSpec(height=8.0, trunk_r=0.36, taper=0.6, levels=3, children=(6, 4, 3), spread=(36, 38, 40), child_len=(0.7, 0.65, 0.5), child_start=0.3, child_rad=0.5, gravity=0.15, phototropism=0.35, wobble=0.3, leaf_level=1, leaf_from=0.5, leaves_per_seg=3, leaf_size=0.70, leaf_kind="broad", leaf_color=(0.26, 0.46, 0.16), bark=((0.52, 0.50, 0.46), (0.30, 0.29, 0.26))),
    "berk":     TreeSpec(height=9.0, trunk_r=0.22, taper=0.7, levels=3, children=(6, 4, 3), spread=(30, 40, 45), child_len=(0.6, 0.6, 0.5), child_start=0.35, child_rad=0.45, gravity=0.55, phototropism=0.05, wobble=0.35, leaf_level=1, leaf_from=0.5, leaves_per_seg=3, leaf_size=0.54, leaf_kind="broad", leaf_color=(0.40, 0.62, 0.22), bark=((0.90, 0.90, 0.86), (0.18, 0.17, 0.15))),
    "kastanje": TreeSpec(height=6.0, trunk_r=0.45, taper=0.5, levels=3, children=(5, 4, 3), spread=(45, 40, 38), child_len=(0.9, 0.7, 0.55), child_start=0.3, child_rad=0.55, gravity=0.3, phototropism=0.3, wobble=0.4, leaf_level=1, leaf_from=0.5, leaves_per_seg=3, leaf_size=0.92, leaf_kind="palmate", leaf_color=(0.20, 0.42, 0.15), bark=((0.34, 0.27, 0.22), (0.12, 0.09, 0.07))),
    "den":      TreeSpec(height=12.0, trunk_r=0.32, taper=0.75, levels=2, children=(26, 4), spread=(84, 60), child_len=(0.36, 0.45), child_start=0.38, child_rad=0.32, gravity=0.6, phototropism=0.1, wobble=0.15, leaf_level=1, leaf_from=0.1, leaves_per_seg=3, leaf_size=0.62, leaf_kind="needle", leaf_color=(0.16, 0.34, 0.18), bark=((0.42, 0.26, 0.16), (0.16, 0.10, 0.06))),
}
SHRUBS = {
    "rododendron": TreeSpec(height=2.0, trunk_r=0.08, taper=0.5, levels=2, children=(10, 5), spread=(55, 50), child_len=(0.8, 0.7), child_start=0.1, child_rad=0.6, gravity=-0.1, phototropism=0.3, wobble=0.5, leaf_level=1, leaf_from=0.3, leaves_per_seg=3, leaf_size=0.55, leaf_kind="broad", leaf_color=(0.14, 0.32, 0.12), bark=((0.30, 0.24, 0.18), (0.12, 0.09, 0.07))),
    "taxus":       TreeSpec(height=2.6, trunk_r=0.10, taper=0.6, levels=2, children=(12, 5), spread=(50, 45), child_len=(0.7, 0.6), child_start=0.1, child_rad=0.55, gravity=-0.05, phototropism=0.4, wobble=0.4, leaf_level=1, leaf_from=0.2, leaves_per_seg=3, leaf_size=0.52, leaf_kind="needle", leaf_color=(0.10, 0.26, 0.12), bark=((0.40, 0.26, 0.18), (0.16, 0.10, 0.07))),
    "struik":      TreeSpec(height=1.5, trunk_r=0.06, taper=0.5, levels=2, children=(11, 4), spread=(60, 50), child_len=(0.9, 0.7), child_start=0.05, child_rad=0.6, gravity=-0.15, phototropism=0.2, wobble=0.6, leaf_level=1, leaf_from=0.3, leaves_per_seg=3, leaf_size=0.46, leaf_kind="broad", leaf_color=(0.30, 0.50, 0.18), bark=((0.34, 0.27, 0.20), (0.14, 0.10, 0.07))),
}

# texturen
tex = {}
for kind, col, nm in (("lobed", (0.22, 0.40, 0.14), "blad_eik"), ("broad", (0.26, 0.46, 0.16), "blad_beuk"), ("broad", (0.40, 0.62, 0.22), "blad_berk"), ("palmate", (0.20, 0.42, 0.15), "blad_kastanje"), ("needle", (0.16, 0.34, 0.18), "naald_den"), ("broad", (0.14, 0.32, 0.12), "blad_rodo"), ("needle", (0.10, 0.26, 0.12), "naald_taxus"), ("broad", (0.30, 0.50, 0.18), "blad_struik")):
    p = os.path.join(OUT, nm + ".png"); render_leaf_cluster(p, col, kind); tex[nm] = p
bark_tex = {}
for nm, (base, dark), st in (("schors_eik", SPECIES["eik"].bark, 6.0), ("schors_beuk", SPECIES["beuk"].bark, 3.0), ("schors_berk", SPECIES["berk"].bark, 1.2), ("schors_den", SPECIES["den"].bark, 5.0)):
    p = os.path.join(OUT, nm + ".png"); bake_bark(p, base, dark, stretch=st); bark_tex[nm] = p
leafmap = {"eik": "blad_eik", "beuk": "blad_beuk", "berk": "blad_berk", "kastanje": "blad_kastanje", "den": "naald_den", "rododendron": "blad_rodo", "taxus": "naald_taxus", "struik": "blad_struik"}
barkmap = {"eik": "schors_eik", "beuk": "schors_beuk", "berk": "schors_berk", "kastanje": "schors_eik", "den": "schors_den", "rododendron": "schors_eik", "taxus": "schors_den", "struik": "schors_eik"}
mats_leaf = {k: image_mat("MAT_" + k, tex[k]) for k in tex}
mats_bark = {k: image_mat("MAT_" + k, bark_tex[k], alpha=False) for k in bark_tex}

# bomen bouwen: 2 varianten per soort
stats = []
x = 0.0
all_specs = list(SPECIES.items()) + list(SHRUBS.items())
for name, spec in all_specs:
    for var in range(2):
        rnd = random.Random(hash((name, var)) & 0xffff)
        bm_w, bm_l, nl = grow(spec, rnd)
        mw = bpy.data.meshes.new("w"); bm_w.to_mesh(mw); bm_w.free(); mw.materials.append(mats_bark[barkmap[name]])
        ml = bpy.data.meshes.new("l"); bm_l.to_mesh(ml); bm_l.free(); ml.materials.append(mats_leaf[leafmap[name]])
        for p in mw.polygons: p.use_smooth = True
        ow = bpy.data.objects.new(f"{name}{var}__MAT_{barkmap[name]}", mw); ol = bpy.data.objects.new(f"{name}{var}__MAT_{leafmap[name]}", ml)
        for o in (ow, ol): sc.collection.objects.link(o); o.location = (x, 0, 0)
        stats.append((name, var, len(mw.polygons) * 2, len(ml.polygons) * 2, nl))
        x += max(4.0, spec.height * 0.9)
print("STATS", stats)
# export FBX: alle objecten, op hun plek (later per boom teruggezet naar oorsprong in Studio via PivotTo)
for o in sc.objects: o.select_set(True)
for o in sc.objects: o.location = (0, 0, 0)   # elke boom op de oorsprong voor de export
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "EftelingTrees_v3.fbx"), use_selection=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y', object_types={'MESH'}, mesh_smooth_type='FACE', add_leaf_bones=False, path_mode='COPY', embed_textures=False)
# proefrender: rij bomen
i = 0
for name, spec in all_specs:
    for var in range(2):
        for o in sc.objects:
            if o.name.startswith(f"{name}{var}__"): o.location = (i * 7.0 - 60, 0, 0)
        i += 1
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (-6, -40, 7); cam.rotation_euler = (math.radians(84), 0, 0); cam.data.lens = 24
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sc.collection.objects.link(sun); sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(30)); sun.data.energy = 3
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; bgn = next(nn for nn in w.node_tree.nodes if nn.type == "BACKGROUND"); bgn.inputs[0].default_value = (0.55, 0.7, 0.9, 1); bgn.inputs[1].default_value = 0.9
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=100); mg = bpy.data.meshes.new("g"); bm.to_mesh(mg); bm.free(); mg.materials.append(mat("ground", (0.25, 0.32, 0.14))); g = bpy.data.objects.new("g", mg); sc.collection.objects.link(g)
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x = 2000; sc.render.resolution_y = 700; sc.view_settings.view_transform = "Standard"
sc.render.filepath = os.path.join(OUT, "preview_trees_v3.png"); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "trees_v3.blend"))
print("DONE")
