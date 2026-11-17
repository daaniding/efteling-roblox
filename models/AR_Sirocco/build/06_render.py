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
         "bamboe": (0.75, 0.62, 0.35), "net": (0.75, 0.78, 0.8), "zeil_turkoois": (0.15, 0.6, 0.58), "zeilrand": (0.1, 0.45, 0.45), "bamboewand": (0.7, 0.58, 0.35),
         "raam": (0.05, 0.05, 0.05), "bestrating": (0.55, 0.5, 0.44), "muur": (0.5, 0.45, 0.4), "afdek": (0.62, 0.58, 0.52), "steen": (0.45, 0.42, 0.38),
         "boei_geel": (0.95, 0.8, 0.1), "boei_blauw": (0.1, 0.3, 0.7), "bord": (0.4, 0.28, 0.16), "dhow": (0.4, 0.28, 0.16), "zeil_dhow": (0.92, 0.85, 0.6), "water": (0.13, 0.22, 0.2), "dhowdek": (0.45, 0.32, 0.2), "baal": (0.85, 0.8, 0.66), "kruik": (0.6, 0.35, 0.2), "bordvlak": (0.9, 0.87, 0.78), "paalmetaal": (0.34, 0.21, 0.17), "zand": (0.84, 0.76, 0.6), "kei": (0.6, 0.52, 0.48), "witrand": (0.9, 0.89, 0.85), "zandsteen": (0.8, 0.68, 0.5), "afdek_zand": (0.88, 0.8, 0.64), "muursteen": (0.6, 0.5, 0.4), "boog": (0.08, 0.07, 0.06), "zandsteenvlak": (0.8, 0.68, 0.5), "blauwglas": (0.3, 0.75, 0.85)}

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
