"""
02_blockout: Sprookjesboom primaire massa's. Maten uit asset-brief.md (front.jpg, 118 px/m; Eftepedia 9 x 13 m).
Blender: X = rechts gezien van voren (oost), -Y = voorkant (zuid), Z omhoog, oorsprong = stamhart op maaiveld.
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix

PHASE = "02_blockout"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})

# stambreedte (front.jpg) per hoogte; diepte = 0.9 x breedte (inferred)
TRUNK = [(0.00, 3.70), (0.30, 3.30), (0.70, 2.80), (1.00, 2.60), (1.50, 2.35), (2.00, 2.12),
         (2.35, 2.00), (3.00, 2.00), (3.60, 2.20), (4.10, 2.60)]
DEPTH = 0.90
EYE_Z, EYE_DX, NOSE_Z, MOUTH_Z = 2.35, 0.35, 2.03, 1.45


def trunk_loft():
    secs = []
    for z, w in TRUNK:
        rx, ry = w / 2, w / 2 * DEPTH
        secs.append([(rx * math.cos(a), ry * math.sin(a), z) for a in
                     [2 * math.pi * i / 32 for i in range(32)]])
    return loft("BLK_trunk", secs, "LOW")


def build(master):
    open_master(master)
    clear_owned()
    clay = material("MAT_blk_bark", (0.55, 0.52, 0.47, 1), 0.85)
    leaf = material("MAT_blk_leaf", (0.30, 0.40, 0.20, 1), 0.8)
    t = trunk_loft(); assign(t, clay)
    # wortelvoeten: (richting graden vanaf +X tegen de klok, lengte, dikte aan de stam)
    roots = [(-60, 1.9, 0.75), (-120, 1.3, 0.6), (200, 1.2, 0.6), (-15, 1.2, 0.55), (95, 1.0, 0.6), (150, 1.0, 0.5)]
    for i, (ang, L, d) in enumerate(roots):
        a = math.radians(ang)
        r0 = 1.0
        p0 = (r0 * math.cos(a), r0 * DEPTH * math.sin(a), 0.55)
        p1 = ((r0 + L) * math.cos(a), (r0 + L) * DEPTH * math.sin(a), 0.08)
        o = curve_tube(f"BLK_root{i}", [p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0.25), p1], d / 2, "LOW", taper_to=0.25)
        assign(o, clay)
    # gezicht: neusknobbel, wangen, mondwal, oogkassen-wallen
    nose = sphere("BLK_nose", 0.18, "LOW", (0, -0.98, NOSE_Z), u=16, v=8, scale=(1.0, 1.3, 0.95)); assign(nose, clay)
    for s in (-1, 1):
        e = sphere(f"BLK_eye{'.L' if s < 0 else '.R'}", 0.12, "LOW", (s * EYE_DX, -0.86, EYE_Z), u=16, v=8); assign(e, clay)
        c = sphere(f"BLK_cheek{'.L' if s < 0 else '.R'}", 0.32, "LOW", (s * 0.42, -0.80, 1.72), u=16, v=8, scale=(1, 0.6, 1)); assign(c, clay)
    lip = sphere("BLK_chin", 0.38, "LOW", (0, -0.86, 1.28), u=16, v=8, scale=(1.0, 0.55, 0.5)); assign(lip, clay)
    # hoofdtakken (front.jpg + front_wide.jpg)
    limbs = [
        ("L_low", [(-0.8, 0.0, 3.3), (-2.5, -0.3, 3.9), (-4.5, -0.5, 3.9), (-6.2, -0.6, 3.4)], 0.48),
        ("R_low", [(0.8, 0.0, 3.6), (2.5, -0.2, 4.1), (4.5, -0.3, 4.0), (6.2, -0.4, 3.6)], 0.45),
        ("C_left", [(-0.5, -0.1, 4.0), (-1.2, -0.3, 5.5), (-2.4, -0.4, 7.0), (-3.2, -0.5, 8.0)], 0.42),
        ("C_mid", [(0.1, -0.2, 4.0), (0.3, -0.4, 5.8), (0.5, -0.5, 7.5), (0.6, -0.4, 8.6)], 0.40),
        ("C_right", [(0.6, 0.0, 4.0), (1.4, -0.1, 5.4), (2.6, -0.2, 6.8), (3.6, -0.3, 7.8)], 0.40),
        ("Back", [(0.0, 0.5, 4.0), (0.2, 1.6, 5.2), (0.3, 3.0, 6.5), (0.4, 4.0, 7.4)], 0.40),
    ]
    for n, pts, r in limbs:
        o = curve_tube(f"BLK_limb_{n}", pts, r, "LOW", taper_to=0.35); assign(o, clay)
    # kruin: brede koepel 13 x 11 m, z 3.0..9.0, holle onderkant rond de vork
    cr = sphere("BLK_crown", 1.0, "LOW", (0, 0.3, 6.1), u=48, v=24, scale=(6.5, 5.5, 2.9)); assign(cr, leaf)
    bm = bmesh.new(); bm.from_mesh(cr.data)
    for v in bm.verts:   # onderkant afvlakken tot z 4.4 in het midden, zijkanten hangen tot ~3.6
        wz = v.co.z * 2.9 + 6.1
        rr = math.hypot(v.co.x * 6.5, v.co.y * 5.5 + 0.3)
        floor = max(3.2, 4.6 - 0.04 * rr ** 2)   # front_wide.jpg: blad boven gezicht vanaf ~4.3-4.6, zijkanten tot ~3.2
        if wz < floor:
            v.co.z = (floor - 6.1) / 2.9
    bm.to_mesh(cr.data); bm.free()
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"]:
        shade_smooth(o, math.radians(60))
    save_master(master)


if __name__ == "__main__":
    a = argv_after_dashes()
    build(a[a.index("--master") + 1])
