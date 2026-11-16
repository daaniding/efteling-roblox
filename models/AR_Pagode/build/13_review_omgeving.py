"""13_review_omgeving: renders van station + omgeving in het parkframe, vanaf dezelfde plekken als de video en de bovenfoto.
Camera's (park, z = NAP - 10, ooghoogte 1.6):
  plein    = video 0:05 (op het plein, kijkt naar de keermuur, het huisje en het bord)
  laan     = video 0:22 (in het laantje, muur links, tuin rechts)
  trap     = video 0:41 (onderaan de trapstrook, kijkt naar de tourniquets en het huisje)
  uitgang  = video 6:42 (pad oostkant, kijkt terug naar de uitgangstrap)
  boven    = Pagode-landing.jpg (vanuit de tempel boven de as, schuin omlaag)
Gebruik: blender --background --python build/13_review_omgeving.py -- --master AR_Pagode_master.blend --hdri <hdr> --uit review/12 [--samples 24]"""
import bpy, sys, os, math, argparse
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
p = argparse.ArgumentParser(); p.add_argument("--master"); p.add_argument("--hdri"); p.add_argument("--uit")
p.add_argument("--samples", type=int, default=24); p.add_argument("--alleen", default="plein,laan,trap,uitgang,boven")
arg = p.parse_args(a)
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(arg.master))
sc = bpy.context.scene
toon = set()
for cn in ("STATION", "OMGEVING"):
    c = bpy.data.collections.get(cn)
    if c: toon |= {o.name for o in c.all_objects}
for ob in bpy.data.objects:
    ob.hide_render = ob.name not in toon
# grondvlak op pleinhoogte (gras) zodat het niet zweeft
bpy.ops.mesh.primitive_plane_add(size=120, location=(360, 47.5, -0.45))
gr = bpy.context.active_object; mg = bpy.data.materials.new("gras_review"); mg.use_nodes = True
next(n for n in mg.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.05, 0.09, 0.03, 1)
gr.data.materials.append(mg)
w = bpy.data.worlds.new("lucht"); sc.world = w; w.use_nodes = True
nt = w.node_tree; bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(arg.hdri)
nt.links.new(env.outputs["Color"], bg.inputs["Color"])
try: sc.render.engine = "CYCLES"
except TypeError: pass
sc.cycles.samples = arg.samples; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "Standard"
os.makedirs(arg.uit, exist_ok=True)


def P(r, ang, z):
    t = math.radians(ang); return (360 + r * math.cos(t), 47.5 + r * math.sin(t), z)


CAMS = {
    "plein": (P(19.5, 86.0, 1.2), P(15.0, 104.0, 2.0), 24),
    "laan": (P(15.6, 104.6, 1.2), P(24.0, 113.0, 0.4), 24),
    "trap": (P(25.5, 110.5, 1.2), P(12.0, 115.0, 2.6), 26),
    "uitgang": (P(19.0, -10.0, 1.3), P(10.6, -20.0, 1.8), 24),
    "boven": ((322.0, 58.0, 47.0), (352.0, 56.0, 0.0), 30),
}
for naam in arg.alleen.split(","):
    pos, doel, lens = CAMS[naam]
    cam = bpy.data.cameras.new(naam); cam.lens = lens; cam.clip_end = 2000
    co = bpy.data.objects.new(naam, cam); sc.collection.objects.link(co)
    co.location = Vector(pos); co.rotation_euler = (Vector(doel) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = (1280, 720) if naam != "boven" else (1000, 1000)
    sc.render.filepath = os.path.join(arg.uit, naam + ".png")
    bpy.ops.render.render(write_still=True)
    print("[13_review]", naam)
