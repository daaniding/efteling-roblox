"""
03a_forms_building: het huisje in echte vormen. Bakstenen, dakpannen, planken, tegels als geometrie.
Maten: zie 02_blockout.py / asset-brief.md. Objecten gaan in LOW (leveringsgeometrie, mid-poly).
"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix

PHASE = "03a_forms_building"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})
random.seed(5)

HOUSE_W, HOUSE_D, EAVE_Z, RIDGE_Z = 1.60, 1.30, 2.05, 2.93
ROOF_SPAN, ROOF_FRONT_OV = 2.10, 0.30
NICHE_W, NICHE_TOP, NICHE_D = 0.99, 2.07, 0.50
DOOR_W, COUNTER_Z = 1.15, 1.08
PILLAR_X, PILLAR_W, PILLAR_H, CAP_W, CAP_H = 1.38, 0.60, 1.10, 0.80, 0.10
WALL_H, WALL_T = 0.85, 0.35
PLAT_W, PLAT_D, STEP_H = 2.64, 1.20, 0.19
SIGN_W, SIGN_H, SIGN_Z = 0.74, 0.22, 2.30
FRONT = -HOUSE_D / 2

MATS = {}
def M(name, rgb, rough=0.8, metal=0.0):
    if name not in MATS:
        MATS[name] = material("MAT_" + name, (*rgb, 1), rough, metal)
    return MATS[name]


def merge_into(bm, tmp, matrix):
    bmesh.ops.transform(tmp, matrix=matrix, verts=tmp.verts)
    me = bpy.data.meshes.new("_t"); tmp.to_mesh(me); tmp.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)


def bricks_on_box(bm_by_mat, center, size, courses_z0, courses_z1, brick=(0.21, 0.05), joint=0.012, depth=0.1, faces="all"):
    """Legt metselwerk op de vier zijvlakken van een blok (center, size). Halfsteensverband."""
    bl, bh = brick
    cx, cy, cz = center; sx, sy, sz = size
    nz = int((courses_z1 - courses_z0) / (bh + joint))
    sides = []
    if faces in ("all", "front"): sides.append(("y", -1))
    if faces == "all": sides += [("y", 1), ("x", -1), ("x", 1)]
    for axis, sgn in sides:
        L = sx if axis == "y" else sy
        n = int(L / (bl + joint))
        for k in range(nz):
            z = courses_z0 + k * (bh + joint) + bh / 2
            off = (bl + joint) / 2 if k % 2 else 0
            for i in range(n + 1):
                u = -L / 2 + off + i * (bl + joint) + bl / 2
                blen = bl
                if u + bl / 2 > L / 2 + 0.001:            # laatste steen inkorten
                    blen = L / 2 - (u - bl / 2)
                    if blen < 0.04: continue
                    u = u - (bl - blen) / 2
                tmp = bmesh.new(); bmesh.ops.create_cube(tmp, size=1.0)
                jitter = random.uniform(-0.004, 0.004)
                if axis == "y":
                    sc = (blen, depth, bh * random.uniform(0.96, 1.0)); pos = (cx + u, cy + sgn * (sy / 2 - depth / 2 + 0.006 + jitter), z)
                else:
                    sc = (depth, blen, bh * random.uniform(0.96, 1.0)); pos = (cx + sgn * (sx / 2 - depth / 2 + 0.006 + jitter), cy + u, z)
                bmesh.ops.scale(tmp, vec=sc, verts=tmp.verts)
                key = random.choice(["brick_a", "brick_a", "brick_b", "brick_c"])
                merge_into(bm_by_mat[key], tmp, Matrix.Translation(pos))


def build(master):
    open_master(master)
    clear_owned()
    # blokkering uit beeld (blijft in bestand)
    for o in bpy.data.objects:
        if o.get("owner") == "phase:02_blockout":
            o.hide_render = True; o.hide_viewport = True; o.hide_set(True) if hasattr(o, "hide_set") else None
    L = "LOW"
    m_plaster = M("plaster", (0.72, 0.70, 0.64), 0.9)
    m_mortar = M("mortar", (0.62, 0.58, 0.52), 0.95)
    m_ba = M("brick_a", (0.55, 0.30, 0.22), 0.85); m_bb = M("brick_b", (0.46, 0.24, 0.18), 0.85); m_bc = M("brick_c", (0.62, 0.38, 0.26), 0.85)
    m_stone = M("stone_cap", (0.58, 0.57, 0.53), 0.8)
    m_tile_w = M("tile_white", (0.90, 0.88, 0.80), 0.4); m_tile_k = M("tile_black", (0.08, 0.08, 0.09), 0.4)
    m_roof_r = M("roof_red", (0.60, 0.22, 0.15), 0.75); m_roof_g = M("roof_grey", (0.35, 0.35, 0.37), 0.7)
    m_green = M("wood_green", (0.18, 0.36, 0.33), 0.5); m_fascia = M("fascia_green", (0.25, 0.40, 0.38), 0.6)
    m_iron = M("iron", (0.06, 0.06, 0.07), 0.5, 0.6); m_sign = M("sign_cream", (0.90, 0.82, 0.62), 0.6)
    m_dark = M("niche_dark", (0.05, 0.05, 0.05), 1.0); m_text = M("text_black", (0.05, 0.04, 0.03), 0.6)

    # ---------- plateau: betonnen kern + dambordtegels + gebogen bakstenen trede
    bm = bmesh.new()
    pts = [(-PLAT_W / 2, 0.3)]
    for i in range(33):
        a = math.pi + i * math.pi / 32
        pts.append((math.cos(a) * PLAT_W / 2, 0.3 + math.sin(a) * PLAT_D))
    pts.append((PLAT_W / 2, 0.3))
    f = bm.faces.new([bm.verts.new((x, y, -STEP_H)) for x, y in pts])
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, 0, STEP_H - 0.012), verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    assign(new_mesh_object("GEO_plateau_core", bm, L), m_mortar)
    # tegels 0.15 m, alleen binnen de ellips en tussen de pilaren
    bw = bmesh.new(); bk = bmesh.new()
    T = 0.15
    for i in range(-9, 9):
        for j in range(-1, 8):
            x = (i + 0.5) * T; y = 0.3 - (j + 0.5) * T
            inside = (y >= 0.3 - PLAT_D + 0.02) and ((x / (PLAT_W / 2 - 0.02)) ** 2 + ((0.3 - y) / (PLAT_D - 0.02)) ** 2 <= 1.0 or y > 0.25)
            if not inside or abs(x) > PLAT_W / 2 - 0.08: continue
            tmp = bmesh.new(); bmesh.ops.create_cube(tmp, size=1.0); bmesh.ops.scale(tmp, vec=(T - 0.004, T - 0.004, 0.012), verts=tmp.verts)
            merge_into(bw if (i + j) % 2 == 0 else bk, tmp, Matrix.Translation((x, y, -0.006)))
    assign(new_mesh_object("GEO_tiles_white", bw, L), m_tile_w); assign(new_mesh_object("GEO_tiles_black", bk, L), m_tile_k)
    # trede: staande bakstenen langs de gebogen rand
    bricks = {"brick_a": bmesh.new(), "brick_b": bmesh.new(), "brick_c": bmesh.new()}
    arc_len = math.pi * (PLAT_W / 2 + PLAT_D) / 2
    n = int(arc_len / 0.062)
    for i in range(n + 1):
        a = math.pi + i * math.pi / n
        x = math.cos(a) * (PLAT_W / 2 + 0.03); y = 0.3 + math.sin(a) * (PLAT_D + 0.03)
        tmp = bmesh.new(); bmesh.ops.create_cube(tmp, size=1.0); bmesh.ops.scale(tmp, vec=(0.05, 0.105, STEP_H - 0.01), verts=tmp.verts)
        rot = Matrix.Rotation(a + math.pi / 2, 4, "Z")
        merge_into(bricks[random.choice(["brick_a", "brick_a", "brick_b", "brick_c"])], tmp, Matrix.Translation((x, y, -STEP_H / 2)) @ rot)
    # ---------- pilaren, kappen, tussenmuurtjes (metselwerk)
    for s, side in ((-1, ".L"), (1, ".R")):
        pc = (s * PILLAR_X, 0.0, PILLAR_H / 2)
        assign(box("GEO_pillar_core" + side, (PILLAR_W - 0.02, PILLAR_W - 0.02, PILLAR_H), L, (s * PILLAR_X, 0.0, 0), base_at_origin=True), m_mortar)
        bricks_on_box(bricks, pc, (PILLAR_W, PILLAR_W, PILLAR_H), 0.0, PILLAR_H)
        cap = box("GEO_cap" + side, (CAP_W, CAP_W, CAP_H), L, (s * PILLAR_X, 0.0, PILLAR_H), base_at_origin=True)
        bevel(cap, 0.02, 3); assign(cap, m_stone)
        inner = HOUSE_W / 2 - 0.02; outer = PILLAR_X - PILLAR_W / 2 + 0.02
        wl = outer - inner; wx = s * (inner + outer) / 2
        assign(box("GEO_wall_core" + side, (wl, WALL_T - 0.02, WALL_H), L, (wx, 0.0, 0), base_at_origin=True), m_mortar)
        bricks_on_box(bricks, (wx, 0.0, WALL_H / 2), (wl, WALL_T, WALL_H), 0.0, WALL_H)
        # rollaag bovenop het muurtje (staande stenen)
        nb = int(wl / 0.062)
        for i in range(nb):
            tmp = bmesh.new(); bmesh.ops.create_cube(tmp, size=1.0); bmesh.ops.scale(tmp, vec=(0.05, WALL_T, 0.105), verts=tmp.verts)
            merge_into(bricks[random.choice(["brick_a", "brick_b"])], tmp, Matrix.Translation((wx - wl / 2 + 0.031 + i * 0.062, 0, WALL_H + 0.052)))
    for k, b in bricks.items():
        assign(new_mesh_object("GEO_bricks_" + k, b, L), MATS[k])
    # ---------- huisromp: pleister, ronde hoeken, lichte bobbels
    bm = bmesh.new()
    prof = [(-HOUSE_W / 2, 0), (HOUSE_W / 2, 0), (HOUSE_W / 2, EAVE_Z), (0, RIDGE_Z), (-HOUSE_W / 2, EAVE_Z)]
    a = [bm.verts.new((x, FRONT, z)) for x, z in prof]; b = [bm.verts.new((x, -FRONT, z)) for x, z in prof]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    for i in range(len(prof)):
        bm.faces.new((a[i], a[(i + 1) % len(prof)], b[(i + 1) % len(prof)], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    house = new_mesh_object("GEO_house", bm, L); assign(house, m_plaster)
    bv = house.modifiers.new("Bevel", "BEVEL"); bv.width = 0.06; bv.segments = 4
    rr = NICHE_W / 2
    cut_a = cylinder("CUT_niche_arch", rr, NICHE_D * 2, L, segments=64, axis="Y", location=(0, FRONT, NICHE_TOP - rr))
    cut_b = box("CUT_niche_box", (NICHE_W, NICHE_D * 2, NICHE_TOP - rr), L, (0, FRONT, 0), base_at_origin=True)
    boolean(house, cut_a); boolean(house, cut_b)
    sub = house.modifiers.new("Sub", "SUBSURF"); sub.subdivision_type = "SIMPLE"; sub.levels = 3; sub.render_levels = 3
    tex = bpy.data.textures.get("TEX_plaster") or bpy.data.textures.new("TEX_plaster", "CLOUDS"); tex.noise_scale = 0.35; tex.noise_depth = 3
    d = house.modifiers.new("Disp", "DISPLACE"); d.texture = tex; d.strength = 0.02; d.mid_level = 0.5
    shade_smooth(house, math.radians(60))
    # nis achterwand + vloer
    assign(box("GEO_niche_back", (NICHE_W + 0.1, 0.05, NICHE_TOP + 0.05), L, (0, FRONT + NICHE_D + 0.02, 0), base_at_origin=True), m_dark)
    # ---------- dak: onderplaat + pannen + windveren + nokvorsten
    half = ROOF_SPAN / 2; fy = FRONT - ROOF_FRONT_OV; by = -FRONT + 0.15
    zE = EAVE_Z - 0.08; zR = RIDGE_Z + 0.04
    tiles_r = bmesh.new(); tiles_g = bmesh.new()
    for s, side in ((-1, ".L"), (1, ".R")):
        bm = bmesh.new()
        q = [(s * half, fy, zE), (0, fy, zR), (0, by, zR), (s * half, by, zE)]
        f = bm.faces.new([bm.verts.new(p) for p in q]); nrm = f.normal.copy(); nrm = nrm if nrm.z > 0 else -nrm
        r = bmesh.ops.extrude_face_region(bm, geom=[f])
        bmesh.ops.translate(bm, vec=nrm * 0.05, verts=[g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        assign(new_mesh_object("GEO_roof_deck" + side, bm, L), m_fascia)
        # pannen: S-profiel pan 0.24 breed x 0.33 lang, rijen van onder naar boven, overlappend
        slope = Vector((s * -half, 0, zR - zE)).normalized(); along = Vector((0, 1, 0)); nrm = along.cross(slope).normalized()
        if nrm.z < 0: nrm = -nrm
        slen = Vector((half, 0, zR - zE)).length
        nrow = int((slen - 0.12) / 0.27) + 1; ncol = int((by - fy) / 0.24) + 1
        for ri in range(nrow):
            for ci in range(ncol):
                tmp = bmesh.new()
                # pan als gebogen plaatje: grid 4x2 met golf in x
                bmesh.ops.create_grid(tmp, x_segments=6, y_segments=2, size=0.5)
                for v in tmp.verts:
                    v.co.x *= 0.24; v.co.y *= 0.33
                    v.co.z = 0.018 * math.sin((v.co.x / 0.24 + 0.5) * 2 * math.pi) + 0.008 * (v.co.y / 0.33 + 0.5)
                r2 = bmesh.ops.extrude_face_region(tmp, geom=tmp.faces[:])
                bmesh.ops.translate(tmp, vec=(0, 0, -0.012), verts=[g for g in r2["geom"] if isinstance(g, bmesh.types.BMVert)])
                bmesh.ops.recalc_face_normals(tmp, faces=tmp.faces)
                base = Vector((s * half, fy, zE)) + slope * (ri * 0.27 + 0.05) + along * (ci * 0.24 + 0.12 + (0.12 if ri % 2 else 0)) + nrm * (0.05 + 0.02 + 0.004 * ri)
                frame = Matrix((along, slope, nrm)).transposed().to_4x4()
                tilt = Matrix.Rotation(math.radians(random.uniform(-2, 2)), 4, "Z")
                merge_into(tiles_r if random.random() < 0.6 else tiles_g, tmp, Matrix.Translation(base) @ frame @ tilt)
        # windveer (gevelplank) langs de voorste dakrand
        bm = bmesh.new()
        p0 = Vector((s * half + s * 0.02, fy - 0.012, zE + 0.02)); p1 = Vector((0, fy - 0.012, zR + 0.045)); d = p1 - p0
        bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(d.length - 0.03, 0.025, 0.11), verts=bm.verts)
        ang = math.atan2(d.z, d.x)
        bmesh.ops.transform(bm, matrix=Matrix.Translation((p0 + p1) / 2 - d.normalized() * 0.015 + Vector((0, 0, 0.03))) @ Matrix.Rotation(-ang, 4, "Y"), verts=bm.verts)
        assign(new_mesh_object("GEO_fascia" + side, bm, L), m_fascia)
    assign(new_mesh_object("GEO_tiles_red", tiles_r, L), m_roof_r); assign(new_mesh_object("GEO_tiles_grey", tiles_g, L), m_roof_g)
    # nokvorsten
    bm = bmesh.new()
    for i in range(int((by - fy) / 0.3) + 1):
        tmp = bmesh.new(); bmesh.ops.create_cone(tmp, cap_ends=True, segments=12, radius1=0.085, radius2=0.085, depth=0.29)
        bmesh.ops.recalc_face_normals(tmp, faces=tmp.faces)
        merge_into(bm, tmp, Matrix.Translation((0, fy + 0.15 + i * 0.3, zR + 0.03)) @ Matrix.Rotation(math.pi / 2, 4, "X") @ Matrix.Diagonal((1.0, 0.55, 1.0, 1.0)))
    assign(new_mesh_object("GEO_ridge", bm, L), m_roof_r)
    # nokblok waar de windveren samenkomen
    assign(box("GEO_fascia_apex", (0.09, 0.03, 0.14), L, (0, fy - 0.014, zR + 0.03)), m_fascia)
    # ---------- halve deur: planken, scharnierbanden, toonbank
    bm = bmesh.new(); np_ = 7; pw = DOOR_W / np_
    for i in range(np_):
        tmp = bmesh.new(); bmesh.ops.create_cube(tmp, size=1.0); bmesh.ops.scale(tmp, vec=(pw - 0.006, 0.05, COUNTER_Z - 0.03), verts=tmp.verts)
        merge_into(bm, tmp, Matrix.Translation((-DOOR_W / 2 + pw * (i + 0.5), FRONT - 0.03, (COUNTER_Z - 0.03) / 2 + 0.01)))
    door = new_mesh_object("GEO_door_planks", bm, L); assign(door, m_green); bevel(door, 0.004, 2)
    for z in (0.55,):
        strap = box("GEO_door_strap", (DOOR_W * 0.55, 0.012, 0.05), L, (-DOOR_W * 0.12, FRONT - 0.062, z)); assign(strap, m_iron)
    for i in range(5):
        assign(cylinder("GEO_bolt_%d" % i, 0.012, 0.01, L, segments=10, axis="Y", location=(-DOOR_W * 0.38 + i * 0.12, FRONT - 0.07, 0.55)), m_iron)
    counter = box("GEO_counter", (DOOR_W + 0.08, 0.26, 0.07), L, (0, FRONT - 0.07, COUNTER_Z + 0.02)); bevel(counter, 0.015, 3); assign(counter, m_green)
    # ---------- naambord met 3D-tekst
    sign = box("GEO_sign", (SIGN_W, 0.03, SIGN_H), L, (0, FRONT - 0.045, SIGN_Z), rotation=(0, math.radians(-4), 0)); bevel(sign, 0.01, 3); assign(sign, m_sign)
    cu = bpy.data.curves.new("TXT_sign", "FONT"); cu.body = "holle Bolle Gijs"; cu.size = 0.10; cu.extrude = 0.003; cu.align_x = "CENTER"; cu.align_y = "CENTER"
    txt = bpy.data.objects.new("GEO_sign_text", cu); col(L).objects.link(txt); own(txt)
    txt.location = (0.0, FRONT - 0.066, SIGN_Z + 0.0); txt.rotation_euler = (math.radians(90), 0, 0)
    txt.data.materials.append(m_text)
    save_master(master)
    log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "objects")


if __name__ == "__main__":
    args = argv_after_dashes()
    master = args[args.index("--master") + 1] if "--master" in args else None
    if master:
        build(master)
