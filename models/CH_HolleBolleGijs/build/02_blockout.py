"""
02_blockout: Holle Bolle Gijs huisje (Sprookjesbos). Meters, Z op, voorkant -Y, z=0 = bovenkant plateau.
Maten uit ref/front.jpg (420 px/m in weergave 1764x2073), zie asset-brief.md. "# inferred" = niet zichtbaar.
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

# ---- gemeten constanten (front.jpg)
HOUSE_W = 1.60      # muren buiten
HOUSE_D = 1.30      # inferred
EAVE_Z = 2.05       # goothoogte zijgevels
RIDGE_Z = 2.93      # nok
ROOF_SPAN = 2.10    # dakrand tot dakrand
ROOF_FRONT_OV = 0.30  # inferred
NICHE_W = 0.99; NICHE_TOP = 2.07; NICHE_D = 0.50  # inferred diepte
DOOR_W = 1.15; COUNTER_Z = 1.08
PILLAR_X = 1.38; PILLAR_W = 0.60; PILLAR_H = 1.10; CAP_W = 0.80; CAP_H = 0.10
WALL_H = 0.85; WALL_T = 0.35
PLAT_W = 2.64; PLAT_D = 1.20; STEP_H = 0.19   # plateau top z 0, straat z -0.19
SIGN_W, SIGN_H, SIGN_Z = 0.74, 0.22, 2.30
# Gijs
HEAD_W = 0.55; HEAD_TOP = 1.87; CHIN_Z = 1.43; MOUTH_Z = 1.58; EYE_Z = 1.69; SHOULDER_Z = 1.35; SHOULDER_W = 0.94


def build(master):
    open_master(master)
    clear_owned()
    L = "LOW"
    front = -HOUSE_D / 2
    # ---- plateau: halve ellips naar voren + rechthoek achter, trede eromheen
    bm = bmesh.new()
    pts = [(-PLAT_W / 2, 0.3)]
    for i in range(25):
        a = math.pi + i * math.pi / 24
        pts.append((math.cos(a) * PLAT_W / 2, 0.3 + math.sin(a) * PLAT_D))
    pts.append((PLAT_W / 2, 0.3))
    f = bm.faces.new([bm.verts.new((x, y, -STEP_H)) for x, y in pts])
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, 0, STEP_H), verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    new_mesh_object("BLK_plateau", bm, L)
    # ---- pilaren + kappen + tussenmuurtjes
    for s, side in ((-1, ".L"), (1, ".R")):
        box("BLK_pillar" + side, (PILLAR_W, PILLAR_W, PILLAR_H), L, (s * PILLAR_X, 0.0, 0), base_at_origin=True)
        box("BLK_cap" + side, (CAP_W, CAP_W, CAP_H), L, (s * PILLAR_X, 0.0, PILLAR_H), base_at_origin=True)
        inner = HOUSE_W / 2; outer = PILLAR_X - PILLAR_W / 2
        box("BLK_wall" + side, (outer - inner + 0.05, WALL_T, WALL_H), L, (s * (inner + outer) / 2, 0.0, 0), base_at_origin=True)
    # ---- huisromp: gevelprisma (voorgevel op y=front), iets taps (inferred)
    bm = bmesh.new()
    prof = [(-HOUSE_W / 2, 0), (HOUSE_W / 2, 0), (HOUSE_W / 2, EAVE_Z), (0, RIDGE_Z), (-HOUSE_W / 2, EAVE_Z)]
    a = [bm.verts.new((x, front, z)) for x, z in prof]; b = [bm.verts.new((x, -front, z)) for x, z in prof]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    for i in range(len(prof)):
        bm.faces.new((a[i], a[(i + 1) % len(prof)], b[(i + 1) % len(prof)], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    house = new_mesh_object("BLK_house", bm, L)
    # nis-uitsparing: boog (cilinder langs Y) + blok, diepte NICHE_D vanaf voorgevel
    rr = NICHE_W / 2
    cut_a = cylinder("CUT_niche_arch", rr, NICHE_D * 2, L, segments=48, axis="Y", location=(0, front, NICHE_TOP - rr))
    cut_b = box("CUT_niche_box", (NICHE_W, NICHE_D * 2, NICHE_TOP - rr), L, (0, front, 0), base_at_origin=True)
    boolean(house, cut_a); boolean(house, cut_b)
    # ---- dak: twee platen met overstek, dikte 0.12
    half = ROOF_SPAN / 2; fy = front - ROOF_FRONT_OV; by = -front + 0.15
    zE = EAVE_Z - 0.08; zR = RIDGE_Z + 0.06
    for s, side in ((-1, ".L"), (1, ".R")):
        bm = bmesh.new()
        q = [(s * half, fy, zE), (0, fy, zR), (0, by, zR), (s * half, by, zE)]
        f = bm.faces.new([bm.verts.new(p) for p in q])
        n = f.normal.copy(); n = n if n.z > 0 else -n
        r = bmesh.ops.extrude_face_region(bm, geom=[f])
        bmesh.ops.translate(bm, vec=n * 0.12, verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        new_mesh_object("BLK_roof" + side, bm, L)
    # ---- halve deur + toonbank
    box("BLK_door", (DOOR_W, 0.06, COUNTER_Z), L, (0, front - 0.02, 0), base_at_origin=True)
    box("BLK_counter", (DOOR_W + 0.06, 0.22, 0.07), L, (0, front - 0.06, COUNTER_Z))
    # ---- naambord
    box("BLK_sign", (SIGN_W, 0.03, SIGN_H), L, (0, front - 0.03, SIGN_Z), rotation=(0, math.radians(-4), 0))
    # ---- Gijs (buste), leunt met armen op de toonbank; gezicht iets voor de gevel
    cy = front + 0.12   # hoofdcentrum y (inferred: hoofd steekt uit de nis)
    hz = (HEAD_TOP + CHIN_Z) / 2
    sphere("BLK_skull", HEAD_W / 2 * 0.86, L, (0, cy, hz + 0.02), scale=(1.0, 0.95, 1.0))
    sphere("BLK_cheek.L", 0.13, L, (-0.15, cy - 0.10, MOUTH_Z - 0.02), scale=(1.0, 0.9, 0.9))
    sphere("BLK_cheek.R", 0.13, L, (0.15, cy - 0.10, MOUTH_Z - 0.02), scale=(1.0, 0.9, 0.9))
    sphere("BLK_jowl", 0.17, L, (0, cy - 0.04, CHIN_Z + 0.03), scale=(1.1, 0.8, 0.55))
    sphere("BLK_hair", HEAD_W / 2 * 0.92, L, (0, cy + 0.01, hz + 0.08), scale=(1.0, 0.95, 0.9))
    sphere("BLK_mouth_ring", 0.065, L, (-0.02, cy - 0.235, MOUTH_Z), scale=(1.0, 0.6, 0.95))
    sphere("BLK_mouth_hole", 0.035, L, (-0.02, cy - 0.26, MOUTH_Z), scale=(1.0, 0.5, 1.0))
    sphere("BLK_nose", 0.032, L, (0, cy - 0.245, MOUTH_Z + 0.07), scale=(1.0, 0.9, 0.85))
    sphere("BLK_eye.L", 0.035, L, (-0.09, cy - 0.205, EYE_Z))
    sphere("BLK_eye.R", 0.035, L, (0.09, cy - 0.205, EYE_Z))
    sphere("BLK_ear.L", 0.05, L, (-0.25, cy + 0.02, hz - 0.02), scale=(0.5, 1.0, 1.1))
    sphere("BLK_ear.R", 0.05, L, (0.25, cy + 0.02, hz - 0.02), scale=(0.5, 1.0, 1.1))
    # romp: schouders 0.94 breed op z 1.35, rood shirt; buik tegen de deur
    sphere("BLK_torso", 0.30, L, (0, cy + 0.10, SHOULDER_Z - 0.12), scale=(1.55, 0.9, 0.75))
    # armen gekruist op de toonbank: bovenarm schouder -> elleboog buiten, onderarm naar het midden
    for s, side in ((-1, ".L"), (1, ".R")):
        skin_chain("BLK_arm" + side, [(s * 0.36, cy + 0.08, SHOULDER_Z - 0.02, 0.12), (s * 0.47, cy - 0.10, 1.18, 0.11),
                                      (s * 0.20, cy - 0.30, 1.16, 0.095), (s * -0.05, cy - 0.34, 1.17, 0.08)],
                   collection=L, subdiv=2)
        box("BLK_hand" + side, (0.13, 0.10, 0.09), L, (s * 0.06, cy - 0.36, 1.19))
    save_master(master)
    log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "objects")


if __name__ == "__main__":
    args = argv_after_dashes()
    master = args[args.index("--master") + 1] if "--master" in args else None
    if master:
        build(master)
