"""06_render: materiaalrenders van de gondel onder de echte lucht (HDRI, zoals in de game), Cycles.
Camera's: 'onder' = maatfoto (16 graden omhoog, 200 mm, ver), 'station' = video 6:45 (gondel beneden, ooghoogte, 26 mm),
'boven' = luchtfoto Pagode2012 (schuin van boven).
Gebruik: blender --background --python build/06_render.py -- --master AR_Pagode_master.blend --hdri <hdr> --uit review/05 [--samples 48]"""
import bpy, sys, os, math, argparse
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
p = argparse.ArgumentParser(); p.add_argument("--master"); p.add_argument("--hdri"); p.add_argument("--uit"); p.add_argument("--samples", type=int, default=48)
p.add_argument("--alleen", default="onder,station,boven")
arg = p.parse_args(a)
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(arg.master))
sc = bpy.context.scene
for ob in bpy.data.objects:
    ob.hide_render = not (ob.name.startswith("AR_Pagode") and ob.type in ("MESH", "CURVE"))
w = bpy.data.worlds.new("lucht"); sc.world = w; w.use_nodes = True
nt = w.node_tree; bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(arg.hdri)
nt.links.new(env.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 1.0
try: sc.render.engine = "CYCLES"
except TypeError: pass
sc.cycles.samples = arg.samples; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "Standard"   # AgX bleekt verzadigd rood/oranje uit; Standard ligt dichter bij Roblox
os.makedirs(arg.uit, exist_ok=True)
CAMS = {
    # naam: (positie, kijkpunt, lens, resolutie)
    "onder": ((0, -150, -42), (0, 0, 6.5), 200, (1000, 952)),
    "station": ((0, -14.5, 3.4), (0, 0, 5.6), 26, (1280, 720)),
    "boven": ((-6, -26, 26), (0, 0, 5.0), 35, (1280, 853)),
}
for naam in arg.alleen.split(","):
    pos, doel, lens, res = CAMS[naam]
    cam = bpy.data.cameras.new(naam); cam.lens = lens; cam.clip_end = 1000
    co = bpy.data.objects.new(naam, cam); sc.collection.objects.link(co); co.location = pos
    d = Vector(doel) - Vector(pos); co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.camera = co; sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(os.path.abspath(arg.uit), f"mat_{naam}.png")
    bpy.ops.render.render(write_still=True)
    print("[06_render]", sc.render.filepath)
