"""
04_low: game-ready stam voor Roblox. HIGH-schorsdelen (stam, neus, oogleden, snijvlak) -> één mesh, gedecimeerd tot
~TRIS driehoeken, UV-uitgevouwen; daarop worden normal/AO/kleur/ruwheid gebakken (bake_maps.py). Ogen, iris, pupillen en
het donkere binnenwerk van mond en gaten worden lichte aparte meshes met effen kleur (geen bake).
Gebruik: Blender -b -P 04_low.py -- --master <blend> [--tris 26000]
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix, Euler

PHASE = "04_low"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix, "Euler": Euler,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})

NAME = "PR_Sprookjesboom"
BARK_PARTS = ("GEO_stam_glad", "GEO_nose",   # gladde stam: decimeren + uitvouwen geeft grote eilanden (schors wordt gebakken)
              "GEO_nose_cut", "GEO_lid_up.L", "GEO_lid_up.R", "GEO_lid_lo.L", "GEO_lid_lo.R")
FLAT_PARTS = {"GEO_eye": "Oogwit", "GEO_iris": "Iris", "GEO_pupil": "Pupil", "GEO_mouth_inside": "Holte", "GEO_Hole": "Holte"}


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def build(master, tris):
    open_master(master)
    clear_owned()
    hi = bpy.data.collections["HIGH"]
    parts = [bpy.data.objects[n] for n in BARK_PARTS if n in bpy.data.objects]
    low = join_meshes(f"{NAME}_Stam_LOD0", parts, "LOW")
    # decimeren in twee stappen (eerst grof plan, dan collapse tot het budget)
    t0 = tri_count(low)
    d = low.modifiers.new("Dec", "DECIMATE"); d.decimate_type = "COLLAPSE"; d.ratio = tris / max(t0, 1); d.use_collapse_triangulate = True
    apply_all_modifiers(low)
    bm = bmesh.new(); bm.from_mesh(low.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bmesh.ops.dissolve_degenerate(bm, dist=0.0005, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(low.data); bm.free()
    shade_smooth(low, math.radians(180))
    smart_uv(low, angle=72.0, margin=0.006, seams_from_sharp=False)
    assign(low, material("MAT_stam_baked", (0.5, 0.47, 0.42, 1), 0.85))
    log("stam LOD0 tris", tri_count(low), "van", t0)
    # effen delen: vereenvoudigde kopieën
    for o in list(hi.objects):
        for pre, role in FLAT_PARTS.items():
            if o.name.startswith(pre):
                c = duplicate(o, f"{NAME}_{role}_{o.name.split('_', 1)[1]}", "LOW")
                if tri_count(c) > 400:
                    dd = c.modifiers.new("Dec", "DECIMATE"); dd.ratio = 400 / tri_count(c); apply_all_modifiers(c)
                c["flat"] = True
                break
    for o in bpy.data.objects:
        if o.name.startswith("BLK_"): o.hide_render = True
    save_master(master)


if __name__ == "__main__":
    a = argv_after_dashes()
    build(a[a.index("--master") + 1], int(a[a.index("--tris") + 1]) if "--tris" in a else 26000)
