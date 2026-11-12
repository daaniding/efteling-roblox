"""
03a_forms_figuur: Langnek zelf. Organische massa's gefuseerd (voxel remesh + smooth) en gesculpt met push();
kleding als eigen schillen die met raycasts op de romp passen. Maten: asset-brief.md + 02_blockout.py (overlay front.jpg).
anim-tags: body (statisch), neck (schuift verticaal), head (schuift mee + yaw om de nekas), irisL / irisR (yaw om het oogcentrum).
"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree

PHASE = "03a_forms_figuur"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})
random.seed(52)

# ---- constanten (zelfde als 02_blockout, overlay front.jpg) --------------------------------------
SEAT_Z = 2.85; FOOT_Z = 2.05; BELT_Z = 4.05; CAPE_LOW_Z = 4.70; SHOULDER_Z = 5.55; COLLAR_TOP = 5.85
NECK_D = 0.38; NECK_OUT = 5.90
HEAD_H = 1.60; HEAD_W = 1.30
KNEE_X = 2.30; KNEE_Z = 3.40; FOOT_X = 1.60
HAND_X = 2.25; HAND_Z = 2.95
Y = 0.30                                   # lichaamsas (y)
CY = Y + 0.05                              # nek/hoofd-as
NECK_TOP = COLLAR_TOP + NECK_OUT           # 11.75
HC = NECK_TOP + HEAD_H / 2 - 0.08          # hoofdcentrum 12.47

MATS = {}
def M(name, rgb, rough=0.5, metal=0.0):
    if name not in MATS:
        MATS[name] = material("MAT_" + name, (*rgb, 1), rough, metal)
    return MATS[name]


def fused(name, parts, voxel, smooth_iter, collection="LOW"):
    ob = join_meshes(name, parts, collection)
    remesh_voxel(ob, voxel)
    sm = ob.modifiers.new("Smooth", "SMOOTH"); sm.factor = 0.6; sm.iterations = smooth_iter
    apply_all_modifiers(ob)
    for p in parts:
        bpy.data.objects.remove(p, do_unlink=True)
    return ob


def ell(name, c, r, u=24, v=12):
    return sphere(name, 1.0, "LOW", c, u=u, v=v, scale=r)


def smooth_obj(ob, mat, angle=80):
    shade_smooth(ob, math.radians(angle)); assign(ob, mat); return ob


def tube(name, pts, r, mat, taper=None, res=8):
    o = curve_tube(name, pts, r, "LOW", resolution=res, taper_to=taper)
    o.data.materials.append(mat); return o


def bvh_of(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    return BVHTree.FromObject(ob, dg)


def surface_ring(bvh, center, n, z_off=0.0, pad=0.0):
    """punten op het oppervlak rond een horizontale doorsnede (raycast van buiten naar binnen)."""
    pts = []
    c = Vector(center)
    for i in range(n):
        t = i * 2 * math.pi / n
        d = Vector((math.cos(t), math.sin(t), 0))
        hit = bvh.ray_cast(c + d * 4.0, -d, 8.0)
        p = hit[0] if hit[0] is not None else c + d * 0.8
        pts.append(p + d * pad + Vector((0, 0, z_off)))
    return pts


def band(name, bvh, center, h, t, n, mat):
    """riem/kraag: band met hoogte h en dikte t strak om het oppervlak op hoogte center.z"""
    inner = surface_ring(bvh, center, n, 0, 0.005)
    c = Vector(center)
    secs = []
    for dz, dr in ((-h / 2, 0), (-h / 2, t), (h / 2, t), (h / 2, 0)):
        secs.append([p + (p - c).normalized() * dr + Vector((0, 0, dz)) for p in inner])
    bm = bmesh.new(); rings = [[bm.verts.new(p) for p in s] for s in secs]
    for a, b in zip(rings, rings[1:] + rings[:1]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_mesh_object(name, bm, "LOW"); return smooth_obj(o, mat, 50)


def build(master):
    open_master(master)
    clear_owned()
    for o in list(bpy.data.objects):           # blokkering van de figuur verbergen (rots/water blijven tot 03b)
        if o.name.startswith("BLK_") and not o.name.startswith(("BLK_rots", "BLK_water", "BLK_rand")):
            o.hide_render = True; o.hide_viewport = True
    L = "LOW"
    m_skin = M("huid", (0.86, 0.58, 0.42), 0.45); m_lip = M("lip", (0.72, 0.46, 0.36), 0.4)
    m_tun = M("tuniek", (0.85, 0.65, 0.18), 0.6); m_broek = M("broek", (0.18, 0.36, 0.38), 0.5)
    m_cape = M("cape", (0.66, 0.16, 0.10), 0.5); m_laars = M("laars", (0.70, 0.18, 0.12), 0.4)
    m_riem = M("riem", (0.32, 0.18, 0.08), 0.55); m_gesp = M("gesp", (0.55, 0.42, 0.20), 0.35, 0.6)
    m_touw = M("touw", (0.80, 0.70, 0.50), 0.8); m_haar = M("haar", (0.12, 0.11, 0.11), 0.8)
    m_wit = M("oogwit", (0.95, 0.94, 0.90), 0.15); m_iris = M("iris", (0.16, 0.09, 0.05), 0.25)
    m_pupil = M("pupil", (0.02, 0.02, 0.02), 0.2); m_dark = M("binnen", (0.10, 0.04, 0.03), 0.9)

    # ================= broek: bekken + dijen + onderbenen, gefuseerd
    parts = [ell("P_bekken", (0, Y + 0.05, SEAT_Z + 0.38), (0.98, 0.72, 0.48))]
    legs = {}
    for s in (-1, 1):
        hip = Vector((s * 0.58, Y - 0.15, SEAT_Z + 0.30)); knee = Vector((s * KNEE_X, Y - 1.62, KNEE_Z))
        ankle = Vector((s * FOOT_X, Y - 2.02, FOOT_Z + 0.42)); legs[s] = (hip, knee, ankle)
        calf = knee.lerp(ankle, 0.3) + Vector((0, 0.10, 0))
        parts.append(skin_chain("P_been%d" % s, [(*hip, 0.44), (*hip.lerp(knee, 0.5), 0.40), (*knee, 0.33), (*calf, 0.33), (*ankle, 0.22)], collection=L, subdiv=2))
    broek = fused("GEO_broek", parts, 0.035, 6)
    for s in (-1, 1):                                       # knieschijf en plooien achter de knie
        hip, knee, ankle = legs[s]
        push(broek, knee + Vector((0, -0.18, 0.2)), 0.25, 0.04)
        push(broek, hip.lerp(knee, 0.75) + Vector((0, 0, -0.30)), 0.22, -0.03)
        push(broek, knee.lerp(ankle, 0.15) + Vector((s * 0.15, 0.25, 0)), 0.18, -0.03)
    smooth_obj(broek, m_broek)

    # ================= tuniek: romp + buik + rok over de schoot
    parts = [
        ell("P_romp", (0, Y + 0.05, 4.30), (0.90, 0.60, 1.25)),
        ell("P_buik", (0, Y - 0.12, 3.85), (0.86, 0.58, 0.62)),
        ell("P_borst", (0, Y - 0.02, 4.85), (0.86, 0.56, 0.55)),
    ]
    tun = fused("GEO_tuniek", parts, 0.03, 6)
    smooth_obj(tun, m_tun)
    # rok: kegel vanaf de heup, gedrapeerd over de dijen (raycast omlaag op de broek), hangt tussen de knieën
    bb = bvh_of(broek)
    K, NT = 12, 72
    secs = []
    for k in range(K + 1):
        ring = []
        for i in range(NT):
            t = i * 2 * math.pi / NT
            front = max(0.0, -math.sin(t))
            R = 1.0 + k * (0.075 + 0.05 * front)
            x = 0.97 * R * math.cos(t); y = Y - 0.05 + 0.70 * R * math.sin(t) - front * k * 0.02
            z = 3.80 - k * 0.11
            hit = bb.ray_cast(Vector((x, y, 6.0)), Vector((0, 0, -1)), 6.0)[0]
            if hit is not None:
                z = max(z, hit.z + 0.05)
            zmin = 2.90 if y > Y - 1.2 else 2.90 - (Y - 1.2 - y) * 1.1
            ring.append(Vector((x, y, max(z, zmin))))
        secs.append(ring)
    rok = loft("GEO_rok", secs, L, cap_ends=False)
    sol = rok.modifiers.new("Dik", "SOLIDIFY"); sol.thickness = 0.04; sol.offset = 1
    sub = rok.modifiers.new("Sub", "SUBSURF"); sub.levels = 1; apply_all_modifiers(rok)
    for i in range(18):                                     # plooien vanaf de zoom
        t = i * 2 * math.pi / 18
        hp = secs[K][int(i * NT / 18)]
        push(rok, hp, 0.22, 0.03 if i % 2 else -0.03)
    smooth_obj(rok, m_tun, 60)
    bt = bvh_of(tun)
    band("GEO_riem", bt, (0, Y - 0.05, BELT_Z), 0.17, 0.045, 48, m_riem)
    hit = bt.ray_cast(Vector((0, -3, BELT_Z)), Vector((0, 1, 0)), 6)[0]
    g = box("GEO_gesp", (0.22, 0.06, 0.22), L, hit + Vector((0, -0.05, 0))); assign(g, m_gesp)
    g2 = box("GEO_gesp_gat", (0.13, 0.07, 0.11), L, hit + Vector((0, -0.065, 0))); assign(g2, m_riem)
    for k, z in enumerate((4.25, 4.43, 4.60)):              # knopen tussen riem en cape
        hp = bt.ray_cast(Vector((0, -3, z)), Vector((0, 1, 0)), 6)[0]
        if hp is not None:
            b = sphere("GEO_knoop_%d" % k, 0.045, L, hp + Vector((0, -0.015, 0)), u=12, v=6, scale=(1, 0.6, 1)); smooth_obj(b, m_riem)

    # ================= mouwen (geel) + handen plat op de rots
    for s, side in ((-1, ".L"), (1, ".R")):
        sh = (s * 0.92, Y + 0.10, 5.22, 0.31); el = (s * 1.30, Y + 0.32, 4.15, 0.25); wr = (s * 2.02, Y + 0.12, HAND_Z + 0.20, 0.19)
        mouw = skin_chain("GEO_mouw" + side, [sh, el, wr], collection=L, subdiv=2); apply_all_modifiers(mouw)
        push(mouw, el[:3], 0.25, 0.03)
        smooth_obj(mouw, m_tun)
        cuff = cylinder("GEO_manchet" + side, 0.22, 0.12, L, segments=24, location=Vector(wr[:3]))
        cuff.rotation_mode = "QUATERNION"; cuff.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(wr[:3]) - Vector(el[:3]))
        smooth_obj(cuff, m_tun, 40)
        hx = s * HAND_X; hy = Y + 0.02; hz = HAND_Z + 0.07
        palm = ell("P_palm" + side, (hx, hy, hz), (0.23, 0.27, 0.085))
        pp = [palm]
        for k in range(4):                                  # vingers naar buiten-voren, plat gespreid
            a = math.radians(-60 + k * 22) * (1 if s > 0 else -1)
            d = Vector((s * math.cos(math.radians(-30 + k * 20)), -math.sin(math.radians(30 + k * 12)) * 0.9, 0)).normalized()
            base = Vector((hx, hy, hz)) + d * 0.18
            pp.append(skin_chain("P_vinger%s%d" % (side, k), [(*base, 0.055), (*(base + d * 0.16 + Vector((0, 0, -0.02))), 0.048), (*(base + d * 0.28 + Vector((0, 0, -0.045))), 0.04)], collection=L, subdiv=1))
        tb = Vector((hx - s * 0.12, hy - 0.18, hz))
        pp.append(skin_chain("P_duim" + side, [(*tb, 0.06), (*(tb + Vector((-s * 0.10, -0.14, -0.03))), 0.05), (*(tb + Vector((-s * 0.14, -0.25, -0.05))), 0.042)], collection=L, subdiv=1))
        hand = fused("GEO_hand" + side, pp, 0.02, 4); smooth_obj(hand, m_skin)

    # ================= laarzen (rood, puntneus, omgeslagen schacht, veters)
    for s, side in ((-1, ".L"), (1, ".R")):
        hip, knee, ankle = legs[s]
        toe = Vector((s * (FOOT_X + 0.42), Y - 2.95, FOOT_Z + 0.16))
        d = (toe - ankle); d.z = 0; d.normalize()
        side_v = Vector((d.y, -d.x, 0))
        secs = []
        stations = [  # (t langs de voet, breedte, hoogte boven zool, z-lift)
            (-0.18, 0.24, 0.62, 0.0), (0.0, 0.27, 0.55, 0.0), (0.25, 0.28, 0.42, 0.0), (0.5, 0.27, 0.30, 0.0),
            (0.72, 0.22, 0.22, 0.02), (0.88, 0.13, 0.15, 0.07), (1.0, 0.035, 0.05, 0.15)]
        L_foot = 1.05
        for t, w, hgt, lift in stations:
            c = Vector((ankle.x, ankle.y, FOOT_Z)) + d * (t * L_foot) + Vector((0, 0, lift))
            ring = []
            for i in range(16):
                a = i * 2 * math.pi / 16
                ring.append(c + side_v * (w * math.cos(a)) + Vector((0, 0, hgt / 2 + hgt / 2 * math.sin(a))) + d * (0.04 * math.sin(a) if t < 0.1 else 0))
            secs.append(ring)
        boot = loft("GEO_laars" + side, secs, L); push(boot, Vector((ankle.x, ankle.y, FOOT_Z)) + d * 0.45 + Vector((0, 0, 0.42)), 0.2, -0.02)
        smooth_obj(boot, m_laars, 60)
        top = Vector((ankle.x, ankle.y, FOOT_Z)) - d * 0.06 + Vector((0, 0, 0.62))
        omslag = cylinder("GEO_omslag" + side, 0.31, 0.16, L, segments=24, location=top, radius_top=0.34); smooth_obj(omslag, m_laars, 40)
        zool = loft("GEO_zool" + side, [[p + Vector((0, 0, -0.02)) for p in secs[k][9:16] + secs[k][0:1]] for k in range(len(secs))], L, close_sections=False, cap_ends=False)
        assign(zool, m_riem)
        for k in range(4):                                   # veters kruislings over de wreef
            c = Vector((ankle.x, ankle.y, FOOT_Z)) + d * (0.12 + k * 0.1) + Vector((0, 0, 0.53 - k * 0.07))
            tube("GEO_veter%s%d" % (side, k), [c - side_v * 0.12, c + Vector((0, 0, 0.03)) - d * 0.03, c + side_v * 0.12], 0.018, m_touw)

    # ================= cape (rood) met opstaande kraag en touw
    secs = []
    prof = [(5.66, 0.46, 0.42), (5.52, 0.80, 0.60), (5.36, 1.12, 0.74), (5.12, 1.30, 0.84), (4.90, 1.37, 0.88), (CAPE_LOW_Z, 1.40, 0.90)]
    for zi, (z, a, b) in enumerate(prof):
        ring = []
        for i in range(48):
            t = i * 2 * math.pi / 48
            zz = z + (0.05 * math.sin(7 * t) if zi == len(prof) - 1 else 0)
            front_dip = -0.06 * max(0, -math.sin(t)) ** 4 if zi == len(prof) - 1 else 0
            ring.append(Vector((a * math.cos(t), CY + b * math.sin(t), zz + front_dip)))
        secs.append(ring)
    cape = loft("GEO_cape", secs, L, cap_ends=False)
    sol = cape.modifiers.new("Dik", "SOLIDIFY"); sol.thickness = 0.05; sol.offset = 1
    sub = cape.modifiers.new("Sub", "SUBSURF"); sub.levels = 1; apply_all_modifiers(cape)
    for i in range(14):                                      # plooien in de cape
        t = i * 2 * math.pi / 14
        push(cape, (1.35 * math.cos(t), CY + 0.88 * math.sin(t), 4.85), 0.16, 0.035 if i % 2 else -0.03)
    smooth_obj(cape, m_cape, 60)
    kraag = profile_spin("GEO_kraag", [(0.38, 5.50), (0.42, 5.62), (0.44, 5.80), (0.47, 5.93), (0.50, 5.97), (0.48, 6.00), (0.43, 5.96), (0.40, 5.85), (0.36, 5.55)], L, steps=40, location=(0, CY, 0))
    smooth_obj(kraag, m_cape, 50)
    binnen = cylinder("GEO_kraag_binnen", 0.40, 0.04, L, segments=32, location=(0, CY, 5.80)); assign(binnen, m_dark)
    # touw: om de kraagvoet, knoop voor, twee hangende einden met knoopjes
    ring = [(0.48 * math.cos(t), CY + 0.48 * math.sin(t), 5.72 + 0.02 * math.sin(3 * t)) for t in [k * 2 * math.pi / 24 for k in range(25)]]
    tube("GEO_touw_ring", ring, 0.035, m_touw)
    knot = Vector((0, CY - 0.52, 5.68))
    kn = sphere("GEO_touw_knoop", 0.085, L, knot, u=16, v=8, scale=(1.2, 0.8, 1.0)); smooth_obj(kn, m_touw)
    for s in (-1, 1):
        lus = [knot + Vector((s * 0.05, 0, 0)), knot + Vector((s * 0.20, -0.08, 0.06)), knot + Vector((s * 0.22, -0.06, -0.10)), knot + Vector((s * 0.05, -0.03, -0.05))]
        tube("GEO_touw_lus%d" % s, lus, 0.03, m_touw)
        end = [knot + Vector((s * 0.03, -0.02, -0.05)), knot + Vector((s * 0.10, -0.22, -0.25)), knot + Vector((s * 0.06, -0.42, -0.52)), knot + Vector((s * 0.12, -0.48, -0.78))]
        tube("GEO_touw_eind%d" % s, end, 0.03, m_touw)
        kk = sphere("GEO_touw_eindknoop%d" % s, 0.05, L, end[-1], u=12, v=6); smooth_obj(kk, m_touw)

    # ================= nek (rigide, schuift)
    neck_len = NECK_TOP - (COLLAR_TOP - 0.75) + 0.30
    nek = cylinder("GEO_nek", NECK_D / 2, neck_len, L, segments=28, location=(0, CY, (COLLAR_TOP - 0.75) + neck_len / 2), radius_top=NECK_D / 2 * 0.95)
    smooth_obj(nek, m_skin, 40); nek["anim"] = "neck"

    # ================= hoofd (v2: naar de foto-uitsnede van front.jpg en Winterlangnek.jpg)
    FY = CY - 0.50                                           # voorkant gezicht
    parts = [
        ell("P_schedel", (0, CY + 0.05, HC + 0.18), (0.62, 0.58, 0.62), 32, 16),
        ell("P_gezicht", (0, CY - 0.08, HC - 0.20), (0.56, 0.45, 0.48), 32, 16),
        ell("P_wang.L", (-0.36, CY - 0.22, HC - 0.18), (0.22, 0.20, 0.24)),
        ell("P_wang.R", (0.36, CY - 0.22, HC - 0.18), (0.22, 0.20, 0.24)),
        ell("P_wenkbrauwboog", (0, CY - 0.34, HC + 0.30), (0.50, 0.16, 0.13)),
        ell("P_kaak", (0, CY - 0.12, HC - 0.48), (0.50, 0.38, 0.24)),
        ell("P_kaakhoek.L", (-0.38, CY - 0.05, HC - 0.52), (0.14, 0.22, 0.14)),
        ell("P_kaakhoek.R", (0.38, CY - 0.05, HC - 0.52), (0.14, 0.22, 0.14)),
        ell("P_kin", (0, CY - 0.30, HC - 0.68), (0.20, 0.14, 0.12)),
        ell("P_bovenlip", (0, CY - 0.43, HC - 0.36), (0.30, 0.10, 0.09)),
    ]
    head = fused("GEO_hoofd", parts, 0.014, 14)
    def lijn(a, b, n, r, st):                                 # doorlopende groef/rug langs een lijn (geen losse putjes)
        a, b = Vector(a), Vector(b)
        for k in range(n + 1):
            push(head, a.lerp(b, k / n), r, st / max(1, n * 0.35))
    for s in (-1, 1):
        push(head, (s * 0.27, FY + 0.08, HC + 0.10), 0.24, -0.06)              # oogkassen (ruimte voor de bolle ogen)
        push(head, (s * 0.27, FY + 0.02, HC + 0.36), 0.16, 0.035)              # bolling boven de ogen (geen wenkbrauwhaar, front.jpg)
        push(head, (s * 0.33, FY + 0.12, HC - 0.06), 0.12, 0.03)               # jukbeenderen
        push(head, (s * 0.30, FY + 0.16, HC - 0.30), 0.12, -0.025)             # holle wangen onder het jukbeen
        lijn((s * 0.16, FY - 0.03, HC - 0.18), (s * 0.36, FY + 0.10, HC - 0.62), 10, 0.05, -0.06)   # diepe naso-labiale plooi (front.jpg)
        push(head, (s * 0.31, FY + 0.16, HC - 0.62), 0.11, 0.025)              # hangwangen
        push(head, (s * 0.42, FY + 0.22, HC + 0.12), 0.12, -0.02)              # slapen
    for z in (0.47, 0.56, 0.64):                                               # diepe voorhoofdsrimpels, licht gebogen
        for s in (-1, 1):
            lijn((s * 0.02, FY + 0.12 - (z - 0.47) * 0.35, HC + z + 0.03), (s * 0.34, FY + 0.17 - (z - 0.47) * 0.35, HC + z - 0.03), 14, 0.03, -0.06)
    sm = head.modifiers.new("Smooth2", "SMOOTH"); sm.factor = 0.4; sm.iterations = 2
    apply_all_modifiers(head); smooth_obj(head, m_skin)
    bh = bvh_of(head)
    def op_gezicht(x, z, uit=0.0):                            # punt op het gezicht (raycast van voren)
        hit = bh.ray_cast(Vector((x, CY - 3, z)), Vector((0, 1, 0)), 6)[0]
        return (hit if hit is not None else Vector((x, FY, z))) + Vector((0, -uit, 0))
    # mond: brede lippen, hoeken omlaag, donkere spleet ertussen
    MZ = HC - 0.43
    def mz(x): return MZ - 1.5 * x * x                      # sterk hangende hoeken (grimas)
    W = 0.33
    xs = [-W + k * (2 * W / 14) for k in range(15)]
    holte = [op_gezicht(x * 0.8, mz(x * 0.8) - 0.06 * (1 - (x / W) ** 2), -0.035) for x in xs]
    tube("GEO_mondholte", holte, 0.06, m_dark, res=12)
    tube("GEO_bovenlip", [op_gezicht(x, mz(x) + 0.03 - 0.02 * (x / W) ** 2, 0.025) for x in xs], 0.045, m_lip, res=12)
    tube("GEO_onderlip", [op_gezicht(x * 0.92, mz(x * 0.92) - 0.13 * (1 - (x / W) ** 2) - 0.035, 0.06) for x in xs], 0.07, m_lip, res=12)
    # neus: lang, de knol hangt tot vlak boven de lip
    np_ = [ell("P_neusrug", (0, FY - 0.04, HC + 0.02), (0.10, 0.10, 0.18)), ell("P_neuspunt", (0, FY - 0.17, HC - 0.13), (0.15, 0.15, 0.14)),
           ell("P_neusvleugel.L", (-0.13, FY - 0.06, HC - 0.18), (0.08, 0.08, 0.07)), ell("P_neusvleugel.R", (0.13, FY - 0.06, HC - 0.18), (0.08, 0.08, 0.07))]
    neus = fused("GEO_neus", np_, 0.012, 4)
    for s in (-1, 1): push(neus, (s * 0.07, FY - 0.10, HC - 0.25), 0.04, -0.02)   # neusgaten
    smooth_obj(neus, m_skin)
    # ogen: groot, bol, wijd open (wit rondom de iris zichtbaar)
    ER_ = 0.20
    for s, side in ((-1, ".L"), (1, ".R")):
        ec = Vector((s * 0.27, FY - 0.03, HC + 0.12))
        wit = sphere("GEO_oogwit" + side, ER_, L, ec, u=32, v=16); smooth_obj(wit, m_wit)
        iris = cylinder("GEO_iris" + side, 0.088, 0.012, L, segments=32, axis="Y", location=ec + Vector((0, -(ER_ - 0.004), 0))); assign(iris, m_iris)
        pup = cylinder("GEO_pupil" + side, 0.048, 0.012, L, segments=20, axis="Y", location=ec + Vector((0, -(ER_ + 0.004), 0))); assign(pup, m_pupil)
        hl = sphere("GEO_glans" + side, 0.016, L, ec + Vector((-0.035, -(ER_ + 0.008), 0.04)), u=10, v=6); assign(hl, m_wit)
        for o in (iris, pup, hl): o["anim"] = "iris" + ("L" if s < 0 else "R")
        rim = []                                            # dikke huidring rondom de oogbol (front.jpg: ogen als in een bril)
        for k in range(33):
            ph = k * 2 * math.pi / 32
            rim.append(ec + Vector((math.cos(ph) * 0.205, 0.06 + 0.015 * math.sin(ph), math.sin(ph) * 0.215)))
        tube("GEO_lidrand" + side, rim, 0.05, m_skin, res=10)
        wal = sphere("GEO_traanzak" + side, 0.17, L, ec + Vector((0, 0.0, -0.22)), u=24, v=12, scale=(1.15, 0.6, 0.35)); smooth_obj(wal, m_skin)
        # oor: groot, plat, iets naar voren gedraaid (front.jpg)
        oc = Vector((s * 0.66, CY + 0.06, HC - 0.02))
        oor = ell("P_oor" + side, oc, (0.11, 0.22, 0.33)); oorl = ell("P_oorlel" + side, oc + Vector((0, -0.03, -0.27)), (0.07, 0.10, 0.10))
        oor = fused("GEO_oor" + side, [oor, oorl], 0.011, 3)
        push(oor, oc + Vector((s * 0.11, -0.03, 0.03)), 0.17, -0.09)            # schelp, dikke rand blijft staan
        oor.matrix_world = Matrix.Translation(oc) @ Matrix.Rotation(math.radians(-s * 24), 4, "Z") @ Matrix.Translation(-oc) @ oor.matrix_world   # draaien om het oor zelf (niet om de wereldoorsprong: dan zweefde het los)
        smooth_obj(oor, m_skin)
        # haar: bossige donkere plukken achter en boven de oren
        hp = []
        for k in range(9):
            c = Vector((s * random.uniform(0.50, 0.64), CY + random.uniform(0.10, 0.42), HC + random.uniform(-0.12, 0.30)))
            hp.append(ell("P_haar%s%d" % (side, k), c, (random.uniform(0.10, 0.15), random.uniform(0.12, 0.18), random.uniform(0.10, 0.16))))
        haar = fused("GEO_haar" + side, hp, 0.014, 2)
        bm = bmesh.new(); bm.from_mesh(haar.data); bm.normal_update()
        for v in bm.verts:                                  # pluizig: ruis langs de normaal
            v.co += v.normal * 0.035 * noise.noise(v.co * 14)
        bm.to_mesh(haar.data); bm.free(); smooth_obj(haar, m_haar)

    # hoofd ~25 graden voorover: hij kijkt omlaag naar de bezoekers (front.jpg: gezicht naar de camera ver onder hem)
    PIV = Vector((0, CY, NECK_TOP + 0.05))
    R = Matrix.Translation(PIV) @ Matrix.Rotation(math.radians(25), 4, "X") @ Matrix.Translation(-PIV)
    for o in list(bpy.data.objects):
        if o.get("owner") == OWNER_TAG and (o.name.startswith(("GEO_hoofd", "GEO_mond", "GEO_bovenlip", "GEO_onderlip", "GEO_neus", "GEO_oogwit",
                "GEO_iris", "GEO_pupil", "GEO_glans", "GEO_lidrand", "GEO_traanzak", "GEO_oor", "GEO_haar"))):
            o.matrix_world = R @ o.matrix_world
    # anim-tags
    for o in bpy.data.objects:
        if o.get("owner") != OWNER_TAG or "anim" in o.keys():
            continue
        n = o.name
        if n.startswith(("GEO_hoofd", "GEO_mond", "GEO_bovenlip", "GEO_onderlip", "GEO_neus", "GEO_oogwit", "GEO_ooglid", "GEO_lidrand", "GEO_traanzak", "GEO_wenkbrauw", "GEO_oor", "GEO_haar")):
            o["anim"] = "head"
        else:
            o["anim"] = "body"
    save_master(master)
    log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "objects")


if __name__ == "__main__":
    args = argv_after_dashes()
    master = args[args.index("--master") + 1] if "--master" in args else None
    if master:
        build(master)
