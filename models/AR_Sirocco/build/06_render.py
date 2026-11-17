"""06_render: klei/kleur-render van de Sirocco vanuit een standpunt (vergelijken met een foto).
Gebruik: blender --background --python build/06_render.py -- --master AR_Sirocco_master.blend --uit review/x.png
         --cam x,y,z --doel x,y,z [--lens 24] [--res 1600x1000] [--klei]
Kleuren per rol (ob["rol"]) als de textuur er nog niet is."""
import bpy, sys, os, math
from mathutils import Vector

KLEUR = {"riet": (0.55, 0.50, 0.40), "beschot": (0.12, 0.11, 0.10), "stam": (0.33, 0.25, 0.18), "platform": (0.18, 0.38, 0.62),
         "subschijf": (0.22, 0.45, 0.70), "voet": (0.12, 0.32, 0.62), "vlonder": (0.30, 0.24, 0.18), "romp": (0.55, 0.10, 0.08), "romp_hout": (0.60, 0.45, 0.28), "romp_blauw": (0.15, 0.25, 0.5), "rood": (0.62, 0.1, 0.08), "binnen": (0.3, 0.05, 0.05), "golf": (0.9, 0.93, 0.97),
         "schubben": (0.25, 0.42, 0.70), "sierpaneel": (0.12, 0.25, 0.60), "goud": (0.75, 0.55, 0.20), "zeil": (0.80, 0.74, 0.62),
         "mast": (0.45, 0.32, 0.20), "touw": (0.6, 0.55, 0.45), "kist": (0.35, 0.25, 0.16), "fruit_oranje": (0.95, 0.45, 0.05),
         "fles": (0.30, 0.18, 0.08), "ton": (0.42, 0.28, 0.16),
         "mand": (0.72, 0.62, 0.42), "fruit_geel": (0.95, 0.8, 0.1), "fruit_groen": (0.25, 0.55, 0.15), "lampion_oranje": (0.95, 0.5, 0.1),
         "lampion_rood": (0.75, 0.12, 0.1), "lampion_petrol": (0.1, 0.4, 0.45), "lantaarn": (0.6, 0.45, 0.2), "lantaarnglas": (1.0, 0.7, 0.3),
         "bamboe": (0.75, 0.62, 0.35), "net": (0.75, 0.78, 0.8)}

a = sys.argv[sys.argv.index("--") + 1:]
def arg(n, d=None): return a[a.index(n) + 1] if n in a else d
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(arg("--master")))
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"
sc.display.shading.color_type = "SINGLE" if "--klei" in a else "OBJECT"
sc.display.shading.show_shadows = True; sc.display.shading.show_cavity = True
sc.display.shading.cavity_type = "BOTH"
for o in bpy.data.objects:
    if o.type == "MESH":
        o.color = (*KLEUR.get(o.get("rol", ""), (0.6, 0.6, 0.6)), 1)
w, h = (int(v) for v in arg("--res", "1600x1000").split("x"))
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.world = sc.world or bpy.data.worlds.new("w")
cd = bpy.data.cameras.new("rc"); cd.lens = float(arg("--lens", "24")); cd.clip_end = 500
cam = bpy.data.objects.new("rc", cd); sc.collection.objects.link(cam); sc.camera = cam
p = Vector([float(v) for v in arg("--cam").split(",")]); t = Vector([float(v) for v in arg("--doel").split(",")])
cam.location = p; cam.rotation_euler = (t - p).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = os.path.abspath(arg("--uit"))
bpy.ops.render.render(write_still=True)
print("[06_render]", sc.render.filepath)
