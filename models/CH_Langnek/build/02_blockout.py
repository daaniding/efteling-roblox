"""
02_blockout: Langnek (reus op kunstrots) + vijver. Meters, Z op, figuur kijkt naar -Y, z=0 = pleinmaaiveld.
Maten uit asset-brief.md (ref/front.jpg via horizon-methode, 55 px/m) en ref/osm_lokaal.json. "# inferred" = niet zichtbaar.
"""
import bpy, bmesh, sys, os, math, json
from mathutils import Vector, Matrix

PHASE = "02_blockout"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OSM = json.load(open(os.path.join(HERE, "ref", "osm_lokaal.json")))
FACING = Vector((0.6, -0.8)).normalized()          # OSM (oost, noord): kijkrichting ZZO naar plein/Kogeloog
RIGHT = Vector((FACING.y, -FACING.x))               # rechterhand van de figuur


def osm_to_model(p):
    v = Vector(p)
    return (v.dot(RIGHT), -v.dot(FACING))


# ---- gemeten constanten (front.jpg, horizon-methode) -------------------------------------------
SEAT_Z = 2.85; FOOT_Z = 2.05; BELT_Z = 4.05; CAPE_LOW_Z = 4.70; SHOULDER_Z = 5.55; COLLAR_TOP = 5.85
SHOULDER_W = 2.40; COLLAR_D = 0.75
NECK_D = 0.38; NECK_OUT = 5.90; NECK_IN = 0.35          # zichtbare neklengte uit / in (overlay front.jpg: 267 px; Eftepedia zegt 4.8 m -> conflict, foto aangehouden)
HEAD_H = 1.60; HEAD_W = 1.30; EAR_W = 1.62          # overlay front.jpg
KNEE_X = 2.30; KNEE_Z = 3.40; FOOT_X = 1.60; BOOT_L = 1.00
HAND_X = 2.25; HAND_Z = 2.95
BODY_Y = 0.30                                            # heupen iets achter het rotsmidden (inferred)
WATER_Z = -0.35; RIM_H = 0.35                            # waterspiegel, randsteen (front.jpg)


def ell(name, c, r, col="LOW"):
    return sphere(name, 1.0, col, c, u=24, v=12, scale=r)


def limb(name, a, b, r, col="LOW"):
    a, b = Vector(a), Vector(b)
    o = cylinder(name, r, (b - a).length, col, segments=16, axis="Z", location=(a + b) / 2)
    o.rotation_mode = "QUATERNION"; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(b - a)
    return o


def build(master):
    open_master(master)
    clear_owned()
    L = "LOW"
    # ---------------- rots: OSM-contour, ringen naar binnen en omhoog (zitplateau achter)
    rots = [osm_to_model(p) for p in OSM["rots"][:-1]]
    cx = sum(p[0] for p in rots) / len(rots); cy = sum(p[1] for p in rots) / len(rots)
    ROCK_S = 0.85    # OSM-contour is ~20% breder dan de rots op front.jpg (6.4 m aan de voet) -> foto aangehouden
    rots = [(cx + (x - cx) * ROCK_S, cy + (y - cy) * ROCK_S) for x, y in rots]
    rings = [(1.00, WATER_Z - 0.2, 0.0), (0.98, 0.9, 0.0), (0.92, FOOT_Z - 0.1, 0.05), (0.80, 2.6, 0.12), (0.62, SEAT_Z - 0.02, 0.25)]   # brede heuvel, plat zitplateau (front.jpg)
    bm = bmesh.new(); vr = []
    for s, z, back in rings:
        vr.append([bm.verts.new((cx + (x - cx) * s, cy + (y - cy) * s + back, z)) for x, y in rots])
    n = len(rots)
    for a, b in zip(vr, vr[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(vr[-1]); bm.faces.new(list(reversed(vr[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    new_mesh_object("BLK_rots", bm, L)
    # ---------------- vijver: halve maan, water + randsteen
    water = [osm_to_model(p) for p in OSM["water"][:-1]]
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new((x, y, WATER_Z - 0.6)) for x, y in water])
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, 0, 0.6), verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    new_mesh_object("BLK_water", bm, L)
    outer = water[:12]                                   # buitenboog (vijverrand aan pleinzijde)
    for i, (a, b) in enumerate(zip(outer, outer[1:])):
        a, b = Vector((*a, 0)), Vector((*b, 0))
        o = box("BLK_rand_%02d" % i, ((b - a).length + 0.2, 0.6, RIM_H), L, (a + b) / 2, base_at_origin=True)
        o.rotation_euler.z = math.atan2((b - a).y, (b - a).x)
    # ---------------- figuur
    Y = BODY_Y
    ell("BLK_heup", (0, Y, SEAT_Z + 0.35), (1.0, 0.75, 0.45))
    ell("BLK_romp", (0, Y + 0.05, (SEAT_Z + SHOULDER_Z) / 2 + 0.1), (0.95, 0.6, 1.2))
    ell("BLK_cape", (0, Y + 0.05, SHOULDER_Z - 0.35), (SHOULDER_W / 2, 0.78, 0.6))
    cylinder("BLK_kraag", COLLAR_D / 2, COLLAR_TOP - (SHOULDER_Z - 0.1), L, segments=20, location=(0, Y + 0.05, (COLLAR_TOP + SHOULDER_Z - 0.1) / 2))
    for s, side in ((-1, ".L"), (1, ".R")):
        hip = (s * 0.6, Y - 0.1, SEAT_Z + 0.25); knee = (s * KNEE_X, Y - 1.6, KNEE_Z); ankle = (s * FOOT_X, Y - 2.0, FOOT_Z + 0.35)
        limb("BLK_dij" + side, hip, knee, 0.42); limb("BLK_scheen" + side, knee, ankle, 0.32)
        limb("BLK_laars" + side, ankle, (s * (FOOT_X + 0.45), Y - 1.9 - BOOT_L * 0.9, FOOT_Z + 0.1), 0.26)
        sh = (s * 1.0, Y + 0.1, SHOULDER_Z - 0.25); el = (s * 1.3, Y + 0.35, 4.15); ha = (s * HAND_X, Y + 0.1, HAND_Z + 0.12)
        limb("BLK_bovenarm" + side, sh, el, 0.26); limb("BLK_onderarm" + side, el, ha, 0.22)
        ell("BLK_hand" + side, (s * HAND_X, Y + 0.2, HAND_Z + 0.05), (0.28, 0.4, 0.1))
    # nek + hoofd in UIT-stand (zoals ref/front.jpg); animatie zet ze lager
    neck_top = COLLAR_TOP + NECK_OUT
    o = cylinder("BLK_nek", NECK_D / 2, NECK_OUT + 0.6, L, segments=16, location=(0, Y + 0.05, neck_top - (NECK_OUT + 0.6) / 2)); o["anim"] = "neck"
    o = ell("BLK_hoofd", (0, Y + 0.05, neck_top + HEAD_H / 2 - 0.08), (HEAD_W / 2, 0.55, HEAD_H / 2)); o["anim"] = "head"
    for s in (-1, 1):
        o = ell("BLK_oor%d" % s, (s * EAR_W / 2 * 0.92, Y + 0.12, neck_top + HEAD_H * 0.52), (0.09, 0.16, 0.24)); o["anim"] = "head"
    save_master(master)
    log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "objects")


if __name__ == "__main__":
    args = argv_after_dashes()
    master = args[args.index("--master") + 1] if "--master" in args else None
    if master:
        build(master)
