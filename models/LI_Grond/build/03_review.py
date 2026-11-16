import bpy, sys, os, random, math
UIT = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.open_mainfile(filepath=os.path.join(UIT, "GR_plukjes.blend"))
src = [o for o in bpy.data.objects if o.name.startswith("GR_plukje")]
rnd = random.Random(3)
for i in range(1400):
    s = rnd.choice(src); o = bpy.data.objects.new(f"k{i}", s.data); bpy.context.collection.objects.link(o)
    o.location = (rnd.uniform(-1.2, 1.2), rnd.uniform(-0.3, 2.6), 0); o.rotation_euler[2] = rnd.random() * 6.28
    sc = rnd.uniform(0.8, 1.25); o.scale = (sc, sc, sc)
for s in src: s.hide_render = True
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0)); g = bpy.context.object
gm = bpy.data.materials.new("bodem"); gm.use_nodes = True
b = next(n for n in gm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
tx = gm.node_tree.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(os.path.join(os.path.dirname(UIT), "textures", "GR_gras004_kleur.png"))
mp = gm.node_tree.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (4, 4, 4)
tc = gm.node_tree.nodes.new("ShaderNodeTexCoord")
gm.node_tree.links.new(tc.outputs["UV"], mp.inputs[0]); gm.node_tree.links.new(mp.outputs[0], tx.inputs[0]); gm.node_tree.links.new(tx.outputs[0], b.inputs[0])
g.data.materials.append(gm)
cam = bpy.data.cameras.new("c"); cam.lens = 24; co = bpy.data.objects.new("c", cam); bpy.context.collection.objects.link(co)
co.location = (0, -1.2, 1.55); co.rotation_euler = (math.radians(62), 0, 0); bpy.context.scene.camera = co
sun = bpy.data.lights.new("s", "SUN"); sun.energy = 4; so = bpy.data.objects.new("s", sun); bpy.context.collection.objects.link(so)
so.rotation_euler = (math.radians(42), 0, math.radians(150))
w = bpy.context.scene.world or bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.7, 1.0, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.2
sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y = 1200, 700
try: sc.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError: sc.render.engine = "BLENDER_EEVEE"
sc.render.filepath = os.path.join(os.path.dirname(UIT), "review", "plukjes_render.png")
bpy.ops.render.render(write_still=True)
