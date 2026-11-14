"""review: huisje + omgeving samen, klei/materiaal (workbench) vanuit vaste standen -> review/<tag>/sheet.jpg
Gebruik: Blender -b -P review.py -- <tag>"""
import bpy, os, sys, math
from mathutils import Vector
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); tag = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.open_mainfile(filepath=os.path.join(D, "RK_huisje_master.blend"))
with bpy.data.libraries.load(os.path.join(D, "RK_omgeving_master.blend")) as (src, dst): dst.objects = [n for n in src.objects if n.startswith("RO_")]
col = bpy.data.collections.new("OMG"); bpy.context.scene.collection.children.link(col)
for o in dst.objects:
    if o: col.objects.link(o)
sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
for mt in bpy.data.materials:
    b = next((n for n in (mt.node_tree.nodes if mt.node_tree else []) if n.type == "BSDF_PRINCIPLED"), None)
    if b is not None and not b.inputs["Base Color"].is_linked: mt.diffuse_color = b.inputs["Base Color"].default_value
sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "MATERIAL"; sh.show_cavity = True; sh.show_shadows = True
w = sc.world or bpy.data.worlds.new("W"); sc.world = w
sc.render.resolution_x, sc.render.resolution_y = 900, 600
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
VIEWS = {"oost": ((-13, -9, 1.2), (0, -2, 1.5), 24), "west": ((12, -9, 0.6), (0, -2, 1.5), 24), "deurzijde": ((-9, 1.5, 0.8), (-2.5, 0.5, 0.5), 26),
         "achter": ((5, 11, 2.0), (0, 1, 1.0), 26), "boven": ((0, -2.5, 40), (0, -2.5, 0), 30), "kijkplein": ((-1.5, -6.2, 1.5), (0.2, -2.2, 1.6), 20)}
os.makedirs(os.path.join(D, "review", tag), exist_ok=True); files = []
for n, (p, t, lens) in VIEWS.items():
    cam.location = p; cam.data.lens = lens; cam.data.clip_end = 300
    cam.rotation_euler = (Vector(t) - Vector(p)).to_track_quat("-Z", "Y").to_euler()
    f = os.path.join(D, "review", tag, n + ".png"); sc.render.filepath = f; bpy.ops.render.render(write_still=True); files.append(f)
import subprocess; subprocess.run(["python3", os.path.join(D, "build", "sheet.py"), os.path.join(D, "review", tag)]); sys.exit(0)
ims = [Image.open(f).convert("RGB") for f in files]; W, H = ims[0].size
s = Image.new("RGB", (W * 3, H * 2), "white")
for i, (im, f) in enumerate(zip(ims, files)):
    s.paste(im, ((i % 3) * W, (i // 3) * H)); ImageDraw.Draw(s).text(((i % 3) * W + 8, (i // 3) * H + 8), os.path.basename(f), fill="black")
s.thumbnail((2100, 2100)); s.save(os.path.join(D, "review", tag, "sheet.jpg"), quality=82); print("SHEET")
