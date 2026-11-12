"""
03b_forms_gijs: Holle Bolle Gijs zelf (buste met armen op de toonbank). Hoofd en romp als gefuseerde
organische massa's (voxel remesh + smooth + push), details apart. Maten: asset-brief.md (front.jpg).
"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix

PHASE = "03b_forms_gijs"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})
random.seed(9)

HOUSE_D = 1.30; FRONT = -HOUSE_D / 2
HEAD_W, HEAD_TOP, CHIN_Z, MOUTH_Z, EYE_Z = 0.55, 1.87, 1.43, 1.58, 1.69
SHOULDER_Z, SHOULDER_W, COUNTER_Z = 1.35, 0.94, 1.08
CY = FRONT + 0.12            # hoofdcentrum y (inferred)
HZ = (HEAD_TOP + CHIN_Z) / 2  # 1.65
FACE_Y = CY - 0.235          # voorste huid

MATS = {}
def M(name, rgb, rough=0.5, metal=0.0):
    if name not in MATS:
        MATS[name] = material("MAT_" + name, (*rgb, 1), rough, metal)
    return MATS[name]


def fused(name, parts, voxel, smooth_iter, collection="LOW"):
    """join -> voxel remesh -> smooth, toegepast, zodat push() op echte verts werkt."""
    ob = join_meshes(name, parts, collection)
    remesh_voxel(ob, voxel)
    sm = ob.modifiers.new("Smooth", "SMOOTH"); sm.factor = 0.6; sm.iterations = smooth_iter
    apply_all_modifiers(ob)
    for p in parts:
        bpy.data.objects.remove(p, do_unlink=True)
    return ob


def build(master):
    open_master(master)
    clear_owned()
    L = "LOW"
    m_skin = M("skin", (0.95, 0.70, 0.58), 0.35); m_blush = M("skin_blush", (0.92, 0.50, 0.45), 0.35)
    m_hair = M("hair_blond", (0.80, 0.60, 0.28), 0.4); m_shirt = M("shirt_red", (0.78, 0.15, 0.10), 0.35)
    m_white = M("cuff_white", (0.93, 0.92, 0.88), 0.4); m_black = M("mouth_black", (0.02, 0.02, 0.02), 0.9)
    m_lip = M("lip", (0.80, 0.40, 0.38), 0.3); m_eye_w = M("eye_white", (0.95, 0.95, 0.93), 0.1)
    m_iris = M("iris", (0.30, 0.42, 0.55), 0.2); m_pupil = M("pupil", (0.02, 0.02, 0.02), 0.2); m_brow = M("brow", (0.60, 0.42, 0.18), 0.5)

    # ---------- hoofd: gefuseerd
    parts = [
        sphere("P_skull", HEAD_W / 2 * 0.88, L, (0, CY, HZ + 0.015), u=32, v=16, scale=(1.0, 0.98, 1.04)),
        sphere("P_cheek.L", 0.135, L, (-0.145, CY - 0.10, MOUTH_Z - 0.01), u=24, v=12, scale=(1.0, 0.95, 0.9)),
        sphere("P_cheek.R", 0.135, L, (0.145, CY - 0.10, MOUTH_Z - 0.01), u=24, v=12, scale=(1.0, 0.95, 0.9)),
        sphere("P_jowl", 0.17, L, (0, CY - 0.05, CHIN_Z + 0.04), u=24, v=12, scale=(1.15, 0.85, 0.6)),
        sphere("P_chin", 0.07, L, (0, CY - 0.17, CHIN_Z + 0.05), u=16, v=8, scale=(1.3, 1.0, 0.8)),
        sphere("P_brow", 0.19, L, (0, CY - 0.07, EYE_Z + 0.07), u=24, v=12, scale=(1.05, 0.85, 0.5)),
        sphere("P_neck", 0.13, L, (0, CY + 0.02, CHIN_Z - 0.06), u=16, v=8, scale=(1.0, 1.0, 1.0)),
        sphere("P_mouth_mound", 0.085, L, (-0.01, CY - 0.19, MOUTH_Z), u=16, v=8, scale=(1.1, 0.8, 1.0)),
    ]
    head = fused("GEO_head", parts, 0.011, 6)
    # sculpt: oogkassen, mondholte, neusbrug, lachrimpels
    for s in (-1, 1):
        push(head, (s * 0.09, FACE_Y, EYE_Z), 0.075, -0.022)
        push(head, (s * 0.07, FACE_Y - 0.01, MOUTH_Z + 0.03), 0.05, -0.01)   # naso-labiale groef
    push(head, (-0.015, FACE_Y - 0.02, MOUTH_Z), 0.085, -0.045)               # mondholte
    push(head, (-0.015, FACE_Y - 0.02, MOUTH_Z), 0.05, -0.03)                 # dieper in het midden
    push(head, (0, FACE_Y, MOUTH_Z + 0.075), 0.035, 0.012)                    # neusbrug
    push(head, (0, FACE_Y - 0.01, MOUTH_Z - 0.09), 0.05, -0.012)              # kin-mondgroef
    sm = head.modifiers.new("Smooth2", "SMOOTH"); sm.factor = 0.5; sm.iterations = 2
    sub = head.modifiers.new("Sub", "SUBSURF"); sub.levels = 1; sub.render_levels = 1
    shade_smooth(head, math.radians(80)); assign(head, m_skin)
    # blos op de wangen: dunne schil
    for s in (-1, 1):
        b = sphere("GEO_blush" + (".L" if s < 0 else ".R"), 0.075, L, (s * 0.16, FACE_Y + 0.085, MOUTH_Z + 0.01), u=16, v=8, scale=(1.0, 0.55, 0.8))
        assign(b, m_blush); shade_smooth(b, math.radians(80))
    # ---------- mond: lippenring + zwart gat (pivot voor animatie onder de onderlip)
    bm = bmesh.new()
    R, r = 0.060, 0.030
    rings = []
    for i in range(24):
        t = i * 2 * math.pi / 24; c = Vector((R * math.cos(t) * 1.0, 0, R * math.sin(t) * 0.95))
        rings.append([bm.verts.new(c + Vector((math.cos(t) * r * math.cos(a), -r * math.sin(a), math.sin(t) * r * math.cos(a)))) for a in [k * 2 * math.pi / 10 for k in range(10)]])
    for i in range(24):
        a_, b_ = rings[i], rings[(i + 1) % 24]
        for k in range(10): bm.faces.new((a_[k], a_[(k + 1) % 10], b_[(k + 1) % 10], b_[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    lips = new_mesh_object("GEO_lips", bm, L, (-0.015, FACE_Y - 0.03, MOUTH_Z)); assign(lips, m_lip); shade_smooth(lips, math.radians(80))
    hole = cylinder("GEO_mouth_hole", 0.042, 0.24, L, segments=20, axis="Y", location=(-0.015, FACE_Y + 0.09, MOUTH_Z)); assign(hole, m_black)
    # ---------- neus
    nose = sphere("GEO_nose", 0.034, L, (0, FACE_Y - 0.012, MOUTH_Z + 0.075), u=16, v=8, scale=(1.0, 0.9, 0.85)); assign(nose, m_skin); shade_smooth(nose, math.radians(80))
    for s in (-1, 1):
        n = sphere("GEO_nostril" + (".L" if s < 0 else ".R"), 0.016, L, (s * 0.024, FACE_Y + 0.0, MOUTH_Z + 0.058), u=12, v=6); assign(n, m_skin); shade_smooth(n, math.radians(80))
    # ---------- ogen, oogleden, wenkbrauwen
    for s, side in ((-1, ".L"), (1, ".R")):
        ex, ey = s * 0.09, FACE_Y + 0.012
        e = sphere("GEO_eye" + side, 0.036, L, (ex, ey, EYE_Z), u=20, v=10); assign(e, m_eye_w); shade_smooth(e, math.radians(80))
        i_ = cylinder("GEO_iris" + side, 0.017, 0.004, L, segments=20, axis="Y", location=(ex + s * 0.004, ey - 0.0335, EYE_Z - 0.002)); assign(i_, m_iris)
        p_ = cylinder("GEO_pupil" + side, 0.008, 0.004, L, segments=14, axis="Y", location=(ex + s * 0.004, ey - 0.036, EYE_Z - 0.002)); assign(p_, m_pupil)
        lid = sphere("GEO_lid" + side, 0.040, L, (ex, ey + 0.004, EYE_Z + 0.012), u=20, v=10, scale=(1.05, 1.0, 0.7)); assign(lid, m_skin); shade_smooth(lid, math.radians(80))
        brow = curve_tube("GEO_brow" + side, [(ex - s * 0.065, ey - 0.008, EYE_Z + 0.06), (ex, ey - 0.022, EYE_Z + 0.082), (ex + s * 0.06, ey - 0.006, EYE_Z + 0.066)], 0.016, L, resolution=8, taper_to=0.45)
        brow.data.materials.append(m_brow)
        # oor
        ear = sphere("GEO_ear" + side, 0.052, L, (s * 0.255, CY + 0.02, HZ - 0.03), u=16, v=8, scale=(0.45, 1.0, 1.15)); assign(ear, m_skin); shade_smooth(ear, math.radians(80))
        ear_in = sphere("GEO_ear_in" + side, 0.03, L, (s * 0.245, CY + 0.02, HZ - 0.035), u=12, v=6, scale=(0.4, 0.8, 1.0)); assign(ear_in, m_blush); shade_smooth(ear_in, math.radians(80))
    # ---------- haar: kap + krullen
    # haarkap: iets groter dan de schedel, afgesneden onder de oogbrauwlijn (voorhoofd vrij) en boven de oren
    RC = HEAD_W / 2 * 0.88 + 0.022
    cap = sphere("GEO_hair_cap", RC, L, (0, CY + 0.01, HZ + 0.03), u=32, v=16, scale=(1.0, 0.98, 1.0))
    cutter = box("CUT_hair", (1.2, 1.2, 0.6), L, (0, CY, HZ + 0.03 - 0.30 + 0.06))           # alles onder z=HZ-0.21 weg
    front_cut = box("CUT_hair_front", (0.5, 0.4, 0.5), L, (0, CY - 0.30, EYE_Z + 0.09 - 0.25 + 0.0))  # voorhoofd vrij
    boolean(cap, cutter); boolean(cap, front_cut); assign(cap, m_hair); shade_smooth(cap, math.radians(80))
    # pony-krullen langs de rand van de kap en losse krullen bovenop
    def curl(name, c, nrm, size):
        nrm = Vector(nrm).normalized(); up = Vector((0, 0, 1)) if abs(nrm.z) < 0.9 else Vector((0, 1, 0))
        u = up.cross(nrm).normalized(); v = nrm.cross(u)
        pts = [tuple(Vector(c) + u * size * math.cos(a) + v * size * math.sin(a) + nrm * (0.6 * size + 0.15 * size * math.sin(2 * a))) for a in [k * 2 * math.pi / 7 for k in range(8)]]
        o = curve_tube(name, pts, size * 0.85, L, resolution=6, taper_to=0.75); o.data.materials.append(m_hair); return o
    k = 0
    for i in range(40):
        t = i * 2 * math.pi / 40 + random.uniform(-0.05, 0.05)
        el = math.radians(random.uniform(-15, 65)) if math.sin(t) < -0.3 else math.radians(random.uniform(-5, 75))
        if math.sin(t) < -0.3 and el < math.radians(10): el = math.radians(12)   # voorhoofd vrij
        nrm = Vector((math.cos(t) * math.cos(el), math.sin(t) * math.cos(el) * 0.98, math.sin(el)))
        c = Vector((0, CY + 0.01, HZ + 0.03)) + nrm * RC * 0.97
        curl("GEO_curl_%d" % k, c, nrm, random.uniform(0.016, 0.024)); k += 1
    for i in range(12):
        t = random.uniform(0, 2 * math.pi); el = math.radians(random.uniform(55, 88))
        nrm = Vector((math.cos(t) * math.cos(el), math.sin(t) * math.cos(el), math.sin(el)))
        c = Vector((0, CY + 0.01, HZ + 0.03)) + nrm * RC * 0.97
        curl("GEO_curl_%d" % k, c, nrm, random.uniform(0.018, 0.026)); k += 1
    # ---------- romp + armen (rood shirt), gefuseerd
    parts = [
        sphere("P_torso", 0.31, L, (0, CY + 0.12, SHOULDER_Z - 0.14), u=32, v=16, scale=(1.5, 0.9, 0.78)),
        sphere("P_belly", 0.28, L, (0, CY + 0.02, COUNTER_Z + 0.08), u=24, v=12, scale=(1.3, 0.9, 0.6)),
    ]
    for s in (-1, 1):
        parts.append(skin_chain("P_arm%d" % s, [(s * 0.34, CY + 0.10, SHOULDER_Z - 0.03, 0.125), (s * 0.47, CY - 0.06, 1.20, 0.115),
                                                 (s * 0.30, CY - 0.28, 1.17, 0.10), (s * 0.08, CY - 0.33, 1.175, 0.085)], collection=L, subdiv=2))
    body = fused("GEO_body", parts, 0.014, 5)
    shade_smooth(body, math.radians(80)); assign(body, m_shirt)
    # plooien bij de ellebogen en schouder
    for s in (-1, 1):
        push(body, (s * 0.47, CY - 0.06, 1.20), 0.09, 0.012)
        push(body, (s * 0.20, CY + 0.12, SHOULDER_Z - 0.26), 0.12, -0.015)
    # kraag wit
    bm = bmesh.new(); rings = []
    for i in range(28):
        t = i * 2 * math.pi / 28; c = Vector((0.15 * math.cos(t), CY + 0.02 + 0.14 * math.sin(t), CHIN_Z - 0.07 - 0.03 * math.sin(t)))
        rings.append([bm.verts.new(c + Vector((math.cos(t) * 0.028 * math.cos(a), math.sin(t) * 0.028 * math.cos(a), 0.028 * math.sin(a)))) for a in [k * 2 * math.pi / 8 for k in range(8)]])
    for i in range(28):
        a_, b_ = rings[i], rings[(i + 1) % 28]
        for k in range(8): bm.faces.new((a_[k], a_[(k + 1) % 8], b_[(k + 1) % 8], b_[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    collar = new_mesh_object("GEO_collar", bm, L); assign(collar, m_white); shade_smooth(collar, math.radians(80))
    # manchetten wit + handen
    for s, side in ((-1, ".L"), (1, ".R")):
        wrist = Vector((s * 0.11, CY - 0.33, 1.175))
        cuff = cylinder("GEO_cuff" + side, 0.092, 0.07, L, segments=20, axis="X", location=wrist + Vector((s * 0.03, 0, 0))); assign(cuff, m_white); shade_smooth(cuff, math.radians(80))
        palm = sphere("GEO_palm" + side, 0.065, L, wrist + Vector((-s * 0.06, -0.02, 0.0)), u=16, v=8, scale=(1.2, 0.8, 0.9)); assign(palm, m_skin); shade_smooth(palm, math.radians(80))
        for k in range(4):
            fz = 1.20 - k * 0.028; fy = CY - 0.36 - k * 0.006
            f = curve_tube("GEO_finger%s_%d" % (side, k), [(-s * 0.02 + s * 0.11, fy + 0.02, fz), (-s * 0.04 + s * 0.11, fy - 0.03, fz - 0.01), (-s * 0.10 + s * 0.11, fy - 0.04, fz - 0.02)], 0.014, L, resolution=6, taper_to=0.8)
            f.data.materials.append(m_skin)
        th = curve_tube("GEO_thumb" + side, [(s * 0.09, CY - 0.34, 1.21), (s * 0.05, CY - 0.37, 1.235), (s * 0.0, CY - 0.38, 1.24)], 0.015, L, resolution=6, taper_to=0.8); th.data.materials.append(m_skin)
    save_master(master)
    log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "objects")


if __name__ == "__main__":
    args = argv_after_dashes()
    master = args[args.index("--master") + 1] if "--master" in args else None
    if master:
        build(master)
