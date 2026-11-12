"""
cam_match: render van de collectie(s) door de camera van ref/front.jpg en overlay op de foto.
Langnek front.jpg (staand 1000x1333): 28 mm-equiv (36 mm VERTICAAL), ooghoogte 1.6 m, ~12.7 m voor het figuurvlak, pitch +13.3 (horizon op 615/900).
Gebruik: Blender --background --python cam_match.py -- --master X.blend --out dir [--cols LOW] [--mode clay|mat] [--cam y,z,lens]
Daarna: python3 cam_match.py --compose dir  (maakt overlay.jpg: foto | render | overlay met randen)
"""
import sys, os, math


def blender_main(a):
    import bpy
    master = a[a.index("--master") + 1]; out = a[a.index("--out") + 1]
    cols = (a[a.index("--cols") + 1] if "--cols" in a else "LOW").split(",")
    mode = a[a.index("--mode") + 1] if "--mode" in a else "clay"
    cx, cy, cz, lens = (float(v) for v in (a[a.index("--cam") + 1] if "--cam" in a else "0,-12.4,1.6,28").split(","))
    sensor = float(a[a.index("--sensor") + 1]) if "--sensor" in a else 36.0
    tag = a[a.index("--tag") + 1] if "--tag" in a else ""
    yaw = math.radians(float(a[a.index("--yaw") + 1])) if "--yaw" in a else 0.0
    res = (a[a.index("--res") + 1] if "--res" in a else "675x900").split("x")
    pitch = math.radians(float(a[a.index("--pitch") + 1])) if "--pitch" in a else math.radians(13.3)
    bpy.ops.wm.open_mainfile(filepath=master)
    sc = bpy.context.scene
    for c in bpy.data.collections:
        lc = bpy.context.view_layer.layer_collection.children.get(c.name)
        if lc is not None:
            lc.exclude = c.name not in cols
    cam = bpy.data.objects.get("CAM_match")
    if cam is None:
        cam = bpy.data.objects.new("CAM_match", bpy.data.cameras.new("CAM_match")); sc.collection.objects.link(cam)
    cam.location = (cx * math.cos(yaw) - cy * math.sin(yaw), cx * math.sin(yaw) + cy * math.cos(yaw), cz); cam.rotation_euler = (math.radians(90) + pitch, 0, yaw)
    cam.data.lens = lens; cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = sensor; cam.data.clip_end = 200
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = int(res[0]), int(res[1]); sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    if mode == "mat":
        sc.render.engine = "CYCLES"; sc.cycles.samples = 48; sc.cycles.device = "CPU"
        try: sc.cycles.use_denoising = True
        except Exception: pass
        sun = bpy.data.objects.get("SUN_match")
        if sun is None:
            sun = bpy.data.objects.new("SUN_match", bpy.data.lights.new("SUN_match", "SUN")); sc.collection.objects.link(sun)
        sun.data.energy = 2.2; sc.view_settings.exposure = -0.4; sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
        w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
        bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND"); bg.inputs[0].default_value = (0.55, 0.62, 0.70, 1); bg.inputs[1].default_value = 0.35
    else:
        sc.render.engine = "BLENDER_WORKBENCH"
        for m in bpy.data.materials:   # viewportkleur = basiskleur van de shader (template zet die niet)
            b = next((n for n in (m.node_tree.nodes if m.node_tree else []) if n.type == "BSDF_PRINCIPLED"), None)
            if b is not None and not b.inputs["Base Color"].is_linked:
                m.diffuse_color = b.inputs["Base Color"].default_value
        sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "MATERIAL"; sh.show_cavity = True
    os.makedirs(out, exist_ok=True)
    sc.render.filepath = os.path.join(out, f"render_{mode}{tag}.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath)


def compose(d, ref, mode="clay"):
    from PIL import Image, ImageFilter, ImageChops
    r = Image.open(os.path.join(d, f"render_{mode}.png")).convert("RGBA")
    p = Image.open(ref).convert("RGB").resize(r.size)
    a = r.split()[3]
    over = p.copy(); over.paste(Image.blend(p, r.convert("RGB"), 0.55), mask=a)
    edge = a.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 40 else 0)
    red = Image.new("RGB", r.size, (255, 30, 30)); over.paste(red, mask=edge)
    flat = Image.new("RGB", r.size, (255, 255, 255)); flat.paste(r, mask=a)
    W, H = r.size
    s = Image.new("RGB", (W * 3, H), "white"); s.paste(p, (0, 0)); s.paste(flat, (W, 0)); s.paste(over, (2 * W, 0))
    s.thumbnail((2400, 2400)); s.save(os.path.join(d, f"compare_{mode}.jpg"), quality=82)
    print("COMPOSED", os.path.join(d, f"compare_{mode}.jpg"))
    return s


if __name__ == "__main__":
    if "--compose" in sys.argv:
        i = sys.argv.index("--compose")
        compose(sys.argv[i + 1], sys.argv[i + 2], sys.argv[i + 3] if len(sys.argv) > i + 3 else "clay")
    else:
        blender_main(sys.argv[sys.argv.index("--") + 1:])
