"""
03_forms_stam: Sprookjesboom stam (HIGH): stam als één loft met wortelvoeten als vloeiende lobben, takken gefuseerd,
gesculpt gezicht, schors als geometrie (golvende rimpels zoals op front.jpg, op takken dwars op de tak), gaten,
ogen, neus-stomp, mondholte. Maten: asset-brief.md.
Gebruik: Blender -b -P 03_forms_stam.py -- --master <blend> [--voxel 0.015]
"""
import bpy, bmesh, sys, os, math, random
import numpy as np
from mathutils import Vector, Matrix, Euler, noise
from mathutils.bvhtree import BVHTree

PHASE = "03_forms_stam"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix, "Euler": Euler,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})
random.seed(4)

# ---- maten (asset-brief.md, front.jpg 118 px/m; front_wide.jpg)
# kale stambreedte zonder wortellobben
TRUNK = [(-0.15, 2.80), (0.40, 2.70), (1.00, 2.52), (1.50, 2.30), (2.00, 2.12),
         (2.35, 2.00), (3.00, 2.00), (3.40, 2.08), (3.80, 2.30), (4.15, 2.45)]
DEPTH = 0.90                       # inferred: doorsnede 0.9 x breedte
EYE_Z, EYE_DX = 2.35, 0.37         # ogen hart-op-hart 0.74 (front.jpg 82 px / cos 20); oogwit 0.32 breed, 0.19 open
NOSE_Z, MOUTH_Z = 2.05, 1.45
NOSE_DIR = Vector((-0.45, -0.78, -0.43)).normalized()   # face close-up front.jpg: snijvlak kijkt naar links-voren, punt z ~2.0
# wortellobben: (hoek graden (-90 = voren), extra straal op maaiveld, hoogte waar de lob verdwijnt, boogbreedte m)
# (front.jpg met camera 20 gr rechts teruggerekend: grote voet rechts op -15, voet met gat rechtsvoor -50, linksvoor -130, grote voet links -165)
ROOTS = [(-15, 1.05, 1.50, 0.40), (-52, 0.85, 1.30, 0.36), (-130, 0.90, 1.30, 0.36), (-165, 1.05, 1.40, 0.40),
         (40, 0.65, 1.10, 0.38), (95, 0.75, 1.20, 0.40), (140, 0.60, 1.10, 0.38), (205, 0.60, 1.10, 0.36)]
# hoofdtakken tot hun eerste splitsing; 03_forms_kruin gaat verder vanaf het laatste punt
LIMBS = [
    ("L_low", [(-0.55, 0.0, 3.0), (-1.4, -0.15, 3.55), (-2.4, -0.3, 3.95), (-3.6, -0.45, 4.15)], 0.38),
    ("R_low", [(0.55, 0.0, 3.2), (1.4, 0.05, 3.45), (2.5, 0.1, 3.6), (3.7, 0.15, 3.75)], 0.36),
    ("C_left", [(-0.35, -0.1, 3.7), (-0.8, -0.25, 4.6), (-1.35, -0.35, 5.5), (-1.9, -0.4, 6.3)], 0.40),
    ("C_mid", [(0.1, -0.15, 3.7), (0.2, -0.35, 4.8), (0.32, -0.48, 5.8), (0.40, -0.5, 6.6)], 0.38),
    ("C_right", [(0.45, 0.0, 3.7), (0.95, -0.05, 4.6), (1.6, -0.1, 5.4), (2.2, -0.12, 6.1)], 0.38),
    ("Back", [(0.0, 0.35, 3.7), (0.12, 1.1, 4.5), (0.22, 2.0, 5.2), (0.3, 2.9, 5.8)], 0.38),
]
# gaten: (naam, azimut graden vanaf voren (+ = rechts), z, straal binnen, rand)  front.jpg teruggerekend (camera 20 gr)
HOLES = [("Hole_R", 48, 0.68, 0.12, 0.24), ("Hole_L", -40, 0.70, 0.10, 0.19), ("Hole_owl", -31, 3.52, 0.09, 0.16)]


def mesh_arrays(ob):
    me = ob.data; n = len(me.vertices)
    co = np.empty(n * 3, np.float32); me.vertices.foreach_get("co", co)
    me.update(); nr = np.empty(n * 3, np.float32); me.vertices.foreach_get("normal", nr)
    return co.reshape(-1, 3), nr.reshape(-1, 3)


def set_co(ob, co):
    ob.data.vertices.foreach_set("co", co.astype(np.float32).ravel()); ob.data.update()


def npush(ob, center, radius, strength, direction=None):
    """push met numpy; radius mag (rx, ry, rz) zijn (ellipsoide)."""
    co, nr = mesh_arrays(ob)
    r = np.array(radius if hasattr(radius, "__len__") else (radius,) * 3, np.float32)
    t = np.sqrt((((co - np.array(center, np.float32)) / r) ** 2).sum(1))
    w = np.where(t < 1, (1 - t * t) ** 2, 0.0)[:, None]
    d = nr if direction is None else np.array(direction, np.float32)[None, :]
    set_co(ob, co + d * w * strength)


def surf_y(bvh, x, z):
    hit = bvh.ray_cast(Vector((x, -6, z)), Vector((0, 1, 0)))
    return hit[0].y if hit[0] is not None else -1.0


def surf_at(bvh, phi_deg, z):
    """oppervlaktepunt op azimut phi (0 = voren/-Y, + = rechts/+X) en hoogte z, straal van buiten naar de as."""
    p = math.radians(phi_deg); o = Vector((6 * math.sin(p), -6 * math.cos(p), z))
    hit = bvh.ray_cast(o, (Vector((0, 0, z)) - o).normalized())
    return hit[0] if hit[0] is not None else Vector((math.sin(p), -math.cos(p), z))


def bvh_of(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); t = BVHTree.FromBMesh(bm); bm.free(); return t


def noise_arr(co, scale, off=(0, 0, 0)):
    s = scale; ox, oy, oz = off
    return np.fromiter((noise.noise(Vector((a * s + ox, b * s + oy, c * s + oz))) for a, b, c in co), np.float32, len(co))


def trunk_radius(theta, z):
    """straal van de stam inclusief wortellobben (lobben = gaussische uitstulpingen die naar boven verdwijnen)."""
    w = float(np.interp(z, [t[0] for t in TRUNK], [t[1] for t in TRUNK])) / 2
    r0 = w * DEPTH / math.sqrt((DEPTH * math.cos(theta)) ** 2 + math.sin(theta) ** 2)   # ellips in poolcoord.
    r0 *= 1 + 0.035 * math.sin(3 * theta + z) + 0.025 * math.sin(5 * theta + 2 * z)
    add = 0.0
    for ang, L, h, arc in ROOTS:
        if z >= h: continue
        d = (theta - math.radians(ang) + math.pi) % (2 * math.pi) - math.pi
        u = max(0.0, z) / h
        add += L * (1 - u) ** 2.6 * math.exp(-((d * r0) / (arc * (1 + 0.4 * u))) ** 2)   # stam recht tot ~1 m, dan uitwaaieren
    return r0 + add


def fused_trunk():
    NT, zs = 160, np.linspace(-0.15, 4.15, 70)
    secs = []
    for z in zs:
        sec = []
        for i in range(NT):
            a = 2 * math.pi * i / NT; r = trunk_radius(a, z)
            sec.append((r * math.cos(a), r * math.sin(a), z))
        secs.append(sec)
    parts = [loft("P_trunk", secs, "HIGH")]
    for n, pts, r in LIMBS:
        parts.append(curve_tube(f"P_limb_{n}", pts, r, "HIGH", taper_to=0.62))
    # bolle tenen: wortels die op de grond uitlopen (front.jpg, front_wide.jpg)
    for i, (ang, L, h, arc) in enumerate(ROOTS):
        a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
        r0 = trunk_radius(a, 0.6) - L * 0.55
        pts = [(r0 * ca, r0 * sa, 0.75), ((r0 + 0.55 * L) * ca, (r0 + 0.55 * L) * sa, 0.28),
               ((r0 + 1.0 * L) * ca, (r0 + 1.0 * L) * sa, 0.10), ((r0 + 1.15 * L) * ca, (r0 + 1.15 * L) * sa, 0.02)]
        parts.append(curve_tube(f"P_toe{i}", pts, 0.20 + 0.12 * L, "HIGH", taper_to=0.55))
    # wangen, kin, voorhoofd als massa's die door de remesh opgaan in de stam (front.jpg)
    for s in (-1, 1):
        parts.append(sphere(f"P_cheek{s}", 0.34, "HIGH", (s * 0.45, -0.86, 1.72), u=24, v=12, scale=(1.0, 0.60, 0.95)))
    parts.append(sphere("P_chin", 0.40, "HIGH", (0, -0.88, 1.20), u=24, v=12, scale=(1.0, 0.62, 0.55)))
    parts.append(sphere("P_brow", 0.50, "HIGH", (0, -0.64, 2.60), u=24, v=12, scale=(1.05, 0.72, 0.42)))
    ob = join_meshes("GEO_stam", parts, "HIGH")
    for p in parts:
        d = p.data; bpy.data.objects.remove(p, do_unlink=True)
        if isinstance(d, bpy.types.Curve): bpy.data.curves.remove(d)
        elif d.users == 0: bpy.data.meshes.remove(d)
    remesh_voxel(ob, 0.035)
    sm = ob.modifiers.new("Smooth", "SMOOTH"); sm.factor = 0.8; sm.iterations = 18
    apply_all_modifiers(ob)
    # onderkant plat op z -0.12 (gesloten houden voor de tweede remesh)
    co, _ = mesh_arrays(ob); co[:, 2] = np.maximum(co[:, 2], -0.12); set_co(ob, co)
    return ob


def sculpt_face(ob):
    bvh = bvh_of(ob)
    S = lambda x, z: surf_y(bvh, x, z)
    for s in (-1, 1):
        x = s * EYE_DX
        npush(ob, (x, S(x, EYE_Z), EYE_Z), (0.22, 0.30, 0.16), -0.12)                       # oogkas
        npush(ob, (x + s * 0.02, S(x, EYE_Z + 0.17), EYE_Z + 0.17), (0.24, 0.22, 0.09), 0.08)   # zwaar bovenooglid tot z+0.08
        npush(ob, (x, S(x, EYE_Z - 0.17), EYE_Z - 0.17), (0.19, 0.20, 0.07), 0.04)          # wal onder het oog
        npush(ob, (s * 0.33, S(s * 0.33, 1.58), 1.58), (0.06, 0.20, 0.24), -0.06)          # lachplooi naast de mond
        npush(ob, (s * 0.62, S(s * 0.62, 2.40), 2.40), (0.12, 0.20, 0.05), -0.03)          # kraaienpootjes
    npush(ob, (0, S(0, 2.25), 2.25), (0.14, 0.25, 0.20), 0.06)                               # neuswortel
    # mond: brede open lach (0.56 breed, 0.16 open), mondhoeken omhoog
    for i in range(15):
        x = -0.30 + i * 0.0429; q = (abs(x) / 0.30) ** 2
        z = MOUTH_Z + 0.05 * q - 0.03 * (1 - q)            # bovenrand vlak, onderrand rond (D op zijn kant)
        npush(ob, (x, S(x, z), z), (0.08, 0.45, 0.10 - 0.05 * q), -0.36)
    npush(ob, (0, S(0, MOUTH_Z), MOUTH_Z), (0.22, 0.45, 0.08), -0.15)
    npush(ob, (0, S(0, MOUTH_Z + 0.10), MOUTH_Z + 0.10), (0.30, 0.2, 0.045), 0.05)        # bovenlip-rol
    npush(ob, (0, S(0, MOUTH_Z - 0.16), MOUTH_Z - 0.16), (0.32, 0.2, 0.08), 0.11)         # dikke onderlip-rol (front.jpg)
    npush(ob, (0, S(0, MOUTH_Z - 0.38), MOUTH_Z - 0.38), (0.30, 0.2, 0.14), 0.06)         # kin
    npush(ob, (0, S(0, 1.10), 1.10), (0.22, 0.2, 0.05), -0.04)                              # kinplooi
    for n, phi, z, rin, rim in HOLES:
        c = surf_at(bvh, phi, z)
        npush(ob, c, rim * 1.25, 0.06)
        npush(ob, c, rin * 1.15, -0.32)


def bark(ob):
    """schors als geometrie: blokvormige platen (krokodillenhuid, front.jpg) met diepe scheuren ertussen.
    Platen liggen in rijen: horizontaal op de stam, concentrisch om ogen/wangen/mond, dwars op de takken."""
    co, nr = mesh_arrays(ob)
    n = len(co); x, y, z = co[:, 0], co[:, 1], co[:, 2]
    th = np.arctan2(y, x)
    n1 = noise_arr(co, 1.3); n2 = noise_arr(co, 3.2, (7, 0, 0)); n3 = noise_arr(co, 2.2, (-3, 0, 5)); n4 = noise_arr(co, 8.0, (1, 2, 3))
    # (u, v): u langs de rij, v dwars op de rij. Stam: u = omtrek, v = hoogte
    u = th * 1.2; v = z.copy(); w_trunk = np.ones(n, np.float32)
    for k, (name, pts, r) in enumerate(LIMBS):
        p0 = np.array(pts[0], np.float32); p1 = np.array(pts[-1], np.float32)
        ax = p1 - p0; L = np.linalg.norm(ax); ax /= L
        e1 = np.cross(ax, [0, 0, 1]).astype(np.float32)
        if np.linalg.norm(e1) < 1e-3: e1 = np.array([1, 0, 0], np.float32)
        e1 /= np.linalg.norm(e1); e2 = np.cross(ax, e1)
        rel = co - p0; t = rel @ ax
        pv = rel - t[:, None] * ax[None, :]; perp = np.linalg.norm(pv, axis=1)
        wl = np.clip((t - 0.25) / 0.5, 0, 1) * ((t < L + 0.6) & (perp < r * 1.6))
        take = wl > 0.5
        u = np.where(take, np.arctan2(pv @ e2, pv @ e1) * r + 37.0 * (k + 1), u)
        v = np.where(take, t * 0.9 + 0.3 * (pv @ e2), v)              # rijen schuin om de tak
        w_trunk = np.minimum(w_trunk, 1 - wl)
    face = (np.clip(1 - np.abs(x) / 0.95, 0, 1) * np.clip((z - 0.95) / 0.3, 0, 1) * np.clip((3.35 - z) / 0.3, 0, 1)
            * np.clip(-nr[:, 1] * 2, 0, 1) * w_trunk)
    feats = [(-EYE_DX, EYE_Z, 0.30), (EYE_DX, EYE_Z, 0.30), (0.0, MOUTH_Z, 0.36)]   # geen ringen op de wangen
    best_w = np.zeros(n, np.float32); bu = u.copy(); bv = v.copy()
    for fx, fz, fr in feats:
        rr = np.sqrt((x - fx) ** 2 + (z - fz) ** 2)
        wf = np.exp(-(rr / fr) ** 2) * face
        take = wf > best_w
        bv = np.where(take, rr + fz, bv); bu = np.where(take, np.arctan2(z - fz, x - fx) * np.maximum(rr, 0.05) + 13 * fx, bu)
        best_w = np.where(take, wf, best_w)
    wfeat = (best_w * 1.6 > 0.5)
    brow = face * np.clip((z - 2.45) / 0.2, 0, 1) * np.clip((3.3 - z) / 0.3, 0, 1)
    v = v - brow * 0.10 * np.exp(-((np.abs(x) - EYE_DX) / 0.25) ** 2)        # bogen boven de ogen
    u = np.where(wfeat, bu, u); v = np.where(wfeat, bv, v)
    v = v + 0.13 * n1 + 0.045 * n2 + 0.015 * n4                             # rijen golven sterk (front.jpg)
    u = u + 0.18 * n2 + 0.06 * n3
    PL = 0.28 - 0.05 * face; PH = 0.078 - 0.014 * face                        # plaatmaat (m): lang en laag; gezicht iets fijner
    U = u / PL; VV = v / PH
    row = np.floor(VV); fr = VV - row
    sm = lambda a: (lambda c: c * c * (3 - 2 * c))(np.clip(a, 0, 1))
    plate_h = sm(np.minimum(fr, 1 - fr) / (0.10 + 0.04 * n4))                # doorlopende horizontale scheur
    edge = np.empty(n, np.float32); hgt = np.empty(n, np.float32)
    for i in range(n):
        ds, ps = noise.voronoi(Vector((float(U[i]), float(row[i]) * 3.17 + 0.5, 0.0)), distance_metric="DISTANCE")
        edge[i] = ds[1] - ds[0]
        q = ps[0]; hgt[i] = math.sin(q.x * 12.9898 + row[i] * 78.233) * 43758.5453 % 1.0   # vaste hoogte per plaat
    plate_v = sm(edge / 0.06)                                                 # korte verticale scheurtjes
    plate = np.minimum(plate_h, plate_v)
    dome = 4 * fr * (1 - fr) * np.clip(edge / 0.4, 0, 1)
    lipmask = np.exp(-((x / 0.34) ** 2 + ((z - MOUTH_Z) / 0.17) ** 2)) * face   # lippen en mondholte glad
    depth = 0.022 * (1 - 0.35 * face) * (0.45 + 0.55 * w_trunk) * (1 - 0.85 * lipmask)
    d = depth * (plate * (0.55 + 0.25 * dome + 0.20 * hgt) - (1 - plate) * 1.0)
    d += 0.010 * n2 + 0.004 * n4                                              # bobbels
    set_co(ob, co + nr * d[:, None])
    # vertexkleur: scheuren donker, plaatranden licht, vlekkerig grijsbeige (front.jpg)
    cav = np.clip(0.15 + 0.85 * plate, 0, 1) * (0.85 + 0.15 * dome)
    tone = 0.93 + 0.12 * n1 + 0.06 * (hgt - 0.5) + 0.04 * n4
    base = np.array([0.58, 0.52, 0.44], np.float32)   # warm grijsbeige (front.jpg)
    colr = base[None, :] * (0.30 + 0.80 * cav[:, None]) * tone[:, None]
    me = ob.data
    if "Col" in me.color_attributes: me.color_attributes.remove(me.color_attributes["Col"])
    ca = me.color_attributes.new("Col", "FLOAT_COLOR", "POINT")
    ca.data.foreach_set("color", np.concatenate([np.clip(colr, 0, 1), np.ones((n, 1), np.float32)], 1).ravel())


def carve(ob, bvh):
    """scherpe openingen na de schors: mond als liggende D (front.jpg: 0.58 breed, 0.16 open, bovenrand vlak),
    gaten als ronde openingen met een opstaande ring. Geen remesh meer erna, dus de randen blijven strak."""
    co, nr = mesh_arrays(ob)
    x, y, z = co[:, 0], co[:, 1], co[:, 2]
    sm = lambda a: (lambda c: c * c * (3 - 2 * c))(np.clip(a, 0, 1))
    # mond
    my = surf_y(bvh, 0, MOUTH_Z)
    q = np.clip((x / 0.29) ** 2, 0, 1)
    zt = MOUTH_Z + 0.05 + 0.035 * q
    zb = MOUTH_Z + 0.05 - 0.17 * (1 - q) ** 0.8
    inside_d = np.minimum.reduce([zt - z, z - zb, (1 - q) * 0.29])          # >0 binnen de D (meter, benadering)
    front = (nr[:, 1] < -0.2) & (y < my + 0.12) & (np.abs(x) < 0.33)
    w = sm(inside_d / 0.025) * front
    co[:, 1] += w * 0.26                                                      # naar achteren de stam in
    # gaten
    for n, phi, hz, rin, rim in HOLES:
        c = surf_at(bvh, phi, hz); nrm = Vector((c.x, c.y, 0)).normalized()
        cn = np.array(c, np.float32); nn = np.array(nrm, np.float32)
        rel = co - cn; along = rel @ nn; lat = np.linalg.norm(rel - along[:, None] * nn[None, :], axis=1)
        near = np.abs(along) < 0.30
        hole_w = sm((rin - lat) / 0.03) * near
        ring_w = np.exp(-((lat - rin * 1.35) / (rim * 0.35)) ** 2) * near * (1 - hole_w)
        co += (-hole_w * 0.40 + ring_w * 0.09)[:, None] * nn[None, :]
    set_co(ob, co)


def bark_material():
    m = bpy.data.materials.get("MAT_bark") or bpy.data.materials.new("MAT_bark")
    if m.node_tree is None: m.use_nodes = True
    nt = m.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = "Col"; at.attribute_type = "GEOMETRY"
    nt.links.new(at.outputs["Color"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.85
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    m.diffuse_color = (0.50, 0.47, 0.42, 1)
    return m


def ring_material():
    """snijvlak van de neus: lichte houtkleur met jaarringen (Wave RINGS), wordt naar basiskleur gebakken."""
    m = bpy.data.materials.get("MAT_nose_cut") or bpy.data.materials.new("MAT_nose_cut")
    if m.node_tree is None: m.use_nodes = True
    nt = m.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord"); wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "RINGS"; wv.inputs["Scale"].default_value = 9.0; wv.inputs["Distortion"].default_value = 3.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.44, 0.38, 0.30, 1); ramp.color_ramp.elements[1].color = (0.70, 0.63, 0.52, 1)
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"]); nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.8
    nt.links.new(bsdf.outputs[0], out.inputs[0]); m.diffuse_color = (0.62, 0.56, 0.46, 1)
    return m


def nose_stub(base):
    """afgezaagde takstomp (front.jpg): ~0.34 dik, steekt ~0.45 uit, wijst naar links-voren-omlaag; snijvlak met jaarringen."""
    prof = [(0.0, -0.30), (0.22, -0.30), (0.21, -0.05), (0.19, 0.10), (0.21, 0.24), (0.225, 0.34), (0.205, 0.43), (0.18, 0.47), (0.0, 0.47)]
    ob = profile_spin("GEO_nose", prof, "HIGH", steps=48)
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=4, use_grid_fill=True); bm.to_mesh(ob.data); bm.free()
    co, nr = mesh_arrays(ob)
    nz = noise_arr(co, 9.0)
    side = (co[:, 2] < 0.465).astype(np.float32)
    ring = 0.5 - 0.5 * np.cos((co[:, 2] + 0.025 * nz) * 2 * np.pi / 0.055)
    set_co(ob, co + nr * ((0.4 * ring - (1 - ring) ** 4) * 0.014 * side + 0.007 * nz)[:, None])
    ob.data.transform(Vector((0, 0, 1)).rotation_difference(NOSE_DIR).to_matrix().to_4x4())
    ob.location = base
    apply_transform(ob)
    return ob


def build(master, voxel):
    open_master(master)
    clear_owned()
    for o in bpy.data.objects:
        if o.name.startswith("BLK_"): o.hide_render = True; o.hide_set(True)
    t = fused_trunk()
    sculpt_face(t)
    remesh_voxel(t, 0.02); apply_all_modifiers(t)
    carve(t, bvh_of(t))                 # mond en gaten uitsnijden vóór de fijne remesh: gladde, strakke randen
    remesh_voxel(t, voxel)
    sm = t.modifiers.new("Smooth", "SMOOTH"); sm.factor = 0.5; sm.iterations = 2
    apply_all_modifiers(t)
    bark(t)
    mb = bark_material(); assign(t, mb); shade_smooth(t, math.radians(180))
    bvh = bvh_of(t); S = lambda x, z: surf_y(bvh, x, z)
    # neus: basis net onder het oppervlak tussen de ogen
    nb = Vector((0.0, S(0.0, 2.12) + 0.10, 2.12))   # wortel onder de ooglijn (face close-up)
    nose = nose_stub(nb); assign(nose, material("MAT_bark_plain", (0.50, 0.47, 0.42, 1), 0.85)); shade_smooth(nose, math.radians(50))
    cut = cylinder("GEO_nose_cut", 0.172, 0.012, "HIGH", segments=48)
    cut.data.transform(Vector((0, 0, 1)).rotation_difference(NOSE_DIR).to_matrix().to_4x4())
    cut.location = nb + NOSE_DIR * 0.472; assign(cut, ring_material())
    # ogen: wit + iris + pupil, half onder het zware ooglid (0.32 breed)
    m_w = material("MAT_eye_white", (0.90, 0.88, 0.82, 1), 0.25)
    m_i = material("MAT_eye_iris", (0.66, 0.42, 0.20, 1), 0.3)   # face close-up: bruin-oranje
    m_p = material("MAT_eye_pupil", (0.03, 0.03, 0.03, 1), 0.2)
    m_lid = material("MAT_bark_plain", (0.50, 0.47, 0.42, 1), 0.85)
    for s, nm in ((-1, "L"), (1, "R")):
        x = s * EYE_DX
        y_lid = min(S(x, EYE_Z + 0.12), S(x, EYE_Z - 0.12))
        y = y_lid + 0.025 + 0.16 * 0.8           # oogvoorkant net achter de ooglidranden
        e = sphere(f"GEO_eye.{nm}", 0.16, "HIGH", (x, y, EYE_Z - 0.02), u=40, v=20, scale=(1.0, 0.8, 0.78))
        assign(e, m_w); shade_smooth(e, math.radians(180))
        fy = y - 0.16 * 0.8
        ir = sphere(f"GEO_iris.{nm}", 0.062, "HIGH", (x - s * 0.025, fy + 0.004, EYE_Z - 0.03), u=24, v=12, scale=(1, 0.3, 1)); assign(ir, m_i); shade_smooth(ir, math.radians(180))
        pu = sphere(f"GEO_pupil.{nm}", 0.032, "HIGH", (x - s * 0.025, fy - 0.010, EYE_Z - 0.03), u=16, v=8, scale=(1, 0.3, 1)); assign(pu, m_p); shade_smooth(pu, math.radians(180))
        socket(f"SOCKET_eye.{nm}", (x, y, EYE_Z))
        # dikke oogleden (schorsrollen) die het oog tot een amandel van ~0.10 hoog afdekken
        for part, keep in (("lid_up", lambda c: c.z > 0.045 - 1.2 * c.x * c.x), ("lid_lo", lambda c: c.z < -0.055 + 1.2 * c.x * c.x)):
            sh = sphere(f"GEO_{part}.{nm}", 0.178, "HIGH", (x, y, EYE_Z - 0.02), u=48, v=24, scale=(1.0, 0.86, 0.92))
            bm = bmesh.new(); bm.from_mesh(sh.data)
            bmesh.ops.delete(bm, geom=[vv for vv in bm.verts if not keep(vv.co) or vv.co.y > 0.06], context="VERTS")
            bm.to_mesh(sh.data); bm.free()
            sf = sh.modifiers.new("Solid", "SOLIDIFY"); sf.thickness = 0.06; sf.offset = 1.0
            sb = sh.modifiers.new("Sub", "SUBSURF"); sb.levels = 2; sb.render_levels = 2
            apply_all_modifiers(sh); assign(sh, m_lid); shade_smooth(sh, math.radians(180))
    m_dark = material("MAT_hollow_dark", (0.04, 0.03, 0.025, 1), 0.95)
    # mond: donker D-vlak in de opening (zelfde D als carve), net achter de lippen
    lip_y = min(S(0, MOUTH_Z + 0.12), S(0, MOUTH_Z - 0.14))
    D = [(x * 0.29, MOUTH_Z + 0.05 + 0.035 * x * x) for x in [i / 10 for i in range(-10, 11)]]
    D += [(x * 0.29, MOUTH_Z + 0.05 - 0.17 * (1 - x * x) ** 0.8) for x in [i / 10 for i in range(9, -10, -1)]]
    mo = profile_extrude("GEO_mouth_inside", [(px * 1.04, pz) for px, pz in D], 0.03, "HIGH", location=(0, lip_y + 0.13, 0),
                         rotation=(math.radians(90), 0, 0))
    assign(mo, m_dark)
    socket("SOCKET_mouth", (0, lip_y, MOUTH_Z))
    for n, phi, z, rin, rim in HOLES:
        c_rim = surf_at(bvh, phi, z + rin * 1.7)                        # oppervlak net boven het gat = ringhoogte
        nrm = Vector((math.sin(math.radians(phi)), -math.cos(math.radians(phi)), 0))
        cen = Vector((0, 0, z)) + nrm * (Vector((c_rim.x, c_rim.y, 0)).length - 0.12)
        h = cylinder(f"GEO_{n}_inside", rin * 1.05, 0.02, "HIGH", segments=24)
        h.data.transform(Vector((0, 0, 1)).rotation_difference(nrm).to_matrix().to_4x4()); h.location = cen
        assign(h, m_dark)
    log("stam verts", len(t.data.vertices), "faces", len(t.data.polygons))
    save_master(master)


if __name__ == "__main__":
    a = argv_after_dashes()
    build(a[a.index("--master") + 1], float(a[a.index("--voxel") + 1]) if "--voxel" in a else 0.015)
