"""05_materials: Blender-materialen AR_<rol> met de texturen uit 04t (en de Sirocco-texturen voor romp, schubben, net),
zelfde tint als in Studio (roblox/plaats_archipel.luau, tabel R). Alleen voor de review-renders; Studio krijgt de texturen
via SurfaceAppearance. Rendert daarna met texturen (Workbench, kleur = textuur).
Gebruik: blender --background --python build/05_materials.py -- --master AR_Archipel_master.blend [--render]"""
import bpy, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SI = os.path.join(os.path.dirname(D), "AR_Sirocco", "textures")
sys.path.insert(0, os.path.join(D, "build"))
import plan as P

# rol -> (textuurbestand of None, tint/kleur)
TEX = {
    "beton": ("AR_beton_kleur", (1, 1, 1)), "kade": ("AR_beton_kleur", (0.95, 0.93, 0.9)), "epdm": ("AR_epdm_kleur", (1, 1, 1)),
    "riet": ("AR_riet_kleur", (1, 1, 1)), "bamboe": ("AR_bamboe_kleur", (1, 1, 1)), "stam": ("AR_stam_kleur", (1, 1, 1)),
    "plank": ("AR_plank_kleur", (1, 1, 1)), "krul": ("AR_krul_kleur", (1, 1, 1)),
    "romp": (os.path.join(SI, "SI_romp_kleur"), (0.72, 0.5, 0.42)), "schubben": (os.path.join(SI, "SI_schubben_kleur"), (1, 1, 1)),
    "net": (os.path.join(SI, "SI_net_kleur"), (1, 1, 1)), "touw": (os.path.join(SI, "SI_mand_kleur"), (0.95, 0.85, 0.7)),
    "mast": ("AR_stam_kleur", (0.5, 0.36, 0.28)), "kist_blauw": ("AR_plank_kleur", (0.72, 0.95, 1.0)),
    "kist_rood": ("AR_plank_kleur", (1.25, 0.72, 0.6)), "kist_hout": ("AR_plank_kleur", (1.05, 0.95, 0.85)), "ton": ("AR_plank_kleur", (1.1, 0.8, 0.6)),
}


def materiaal(m):
    rol = m.name[3:]
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    if rol in TEX:
        f, tint = TEX[rol]
        pad = f if os.path.isabs(f) else os.path.join(D, "textures", f)
        img = bpy.data.images.load(pad + ".png", check_existing=True)
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs[0].default_value = 1.0
        mix.inputs[7].default_value = (*tint, 1)
        nt.links.new(tx.outputs[0], mix.inputs[6]); nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
        nt.nodes.active = tx
        if rol == "net": nt.links.new(tx.outputs[0], bsdf.inputs["Alpha"]); m.blend_method = "CLIP" if hasattr(m, "blend_method") else None
    else:
        bsdf.inputs["Base Color"].default_value = m.diffuse_color


def render(uit):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"; sc.display.shading.show_shadows = True
    sc.render.film_transparent = True
    cam_d = bpy.data.cameras.new("gatecam"); cam = bpy.data.objects.new("gatecam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    for o in bpy.data.objects:
        if o.get("owner") == "phase:02_blockout": o.hide_render = True
    cam_d.type = "PERSP"; sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    M = lambda p, z: Vector((p[0] - P.OORSPRONG[0], p[1] - P.OORSPRONG[1], z))
    for naam, pos, doel, lens in (("mat_alle", (467.2, 157.6, 1.7), (448.0, 157.5, 2.6), 26), ("mat_zonnig", (463.6, 163.4, 1.7), (452.0, 154.5, 2.0), 24),
                                  ("mat_hut", (455.5, 152.0, 1.6), (449.0, 155.5, 2.8), 26), ("mat_wrak", (466.0, 153.5, 1.6), (461.0, 159.0, 1.0), 30),
                                  ("mat_vogel", (468.0, 140.0, 16.0), (451.0, 159.0, 0.0), 28)):
        p = M(pos[:2], pos[2]); q = M(doel[:2], doel[2]); cam_d.lens = lens
        cam.location = p; cam.rotation_euler = (q - p).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(uit, naam + ".png"); bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def main():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    master = os.path.abspath(a[a.index("--master") + 1]) if "--master" in a else os.path.join(D, "AR_Archipel_master.blend")
    bpy.ops.wm.open_mainfile(filepath=master)
    for m in bpy.data.materials:
        if m.name.startswith("AR_"): materiaal(m)
    bpy.ops.wm.save_as_mainfile(filepath=master)
    if "--render" in a:
        uit = os.path.join(D, "review", "05_materials"); os.makedirs(uit, exist_ok=True); render(uit)
    print("[05_materials] klaar")


main()
