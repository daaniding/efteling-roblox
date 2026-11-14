"""
03a_reus: de slapende reus van Klein Duimpje (1998). Maten/houding uit Kduimpje_reus_zijaanzicht, Kleinduimpje-reus(-1997),
Reus-Efteling-airbrush, Model_reus (zie asset-brief.md). Modelframe: meters, z op, voorkant (rotsrand naar het plein) = -Y,
lichaamsas langs X met het hoofd op +X en de laarzen op -X. Rots-ondergrond: 03b_omgeving.py.
Organische massa's per materiaal gefuseerd (voxel remesh + smooth), daarna met push() gesculpt.
Gebruik: Blender -b -P 03a_reus.py -- --master CH_KleinDuimpje_master.blend
"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, noise

PHASE = "03a_reus"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1].split("def build(scene, args):", 1)[0]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})
R = random.Random(1998)
V = Vector

# ---------------- kleuren (geschilderd polyester, foto's) ----------------
RGB = {"huid": (232, 194, 166), "baard": (78, 78, 82), "haar": (124, 118, 112), "hemd": (232, 222, 194), "broek": (96, 116, 146), "binnen": (70, 24, 22),
       "vest": (120, 70, 40), "laars": (150, 100, 86), "zool": (54, 36, 26), "riem": (70, 42, 24), "messing": (190, 150, 70),
       "veter": (96, 60, 36), "rood": (150, 36, 36), "lip": (200, 120, 108), "wenkbrauw": (70, 68, 70), "nagel": (150, 108, 100)}
MATS = {}
def M(n):
    if n not in MATS:
        c = RGB[n]; MATS[n] = material("MAT_" + n, tuple((v / 255) ** 2.2 for v in c) + (1,), 0.55 if n != "messing" else 0.35, 0.8 if n == "messing" else 0.0)
    return MATS[n]


def tag(ob, mat, anim="body"):
    ob["anim"] = anim; assign(ob, M(mat)); return ob


# ---------------- bouwstenen ----------------
def ellb(c, r, rot=None, u=28, v=16):
    """ellipsoide als bmesh-object; rot = Matrix 3x3 (kolommen = lokale assen)"""
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    S = Matrix.Diagonal((r[0], r[1], r[2], 1)); T = Matrix.Translation(c) @ (rot.to_4x4() if rot else Matrix()) @ S
    bmesh.ops.transform(bm, matrix=T, verts=bm.verts)
    return new_mesh_object("tmp", bm, "LOW")


def crom(pts, n):
    """Catmull-Rom door punten (x,y,z,r) -> n samples"""
    P = [V(p[:3]) for p in pts]; Rr = [p[3] for p in pts]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]; Rr = [Rr[0]] + Rr + [Rr[-1]]
    out = []
    seg = len(pts) - 1
    for k in range(n):
        t = k / (n - 1) * seg; i = min(int(t), seg - 1); u = t - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        p = 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)
        r = Rr[i + 1] + (Rr[i + 2] - Rr[i + 1]) * (u * u * (3 - 2 * u))
        out.append((p, r))
    return out


def loft(pts, n=24, ring=18, flat=1.0, up=V((0, 0, 1)), wobble=0.0, seed=0):
    """buis met variabele straal langs een Catmull-Rom; flat < 1 plet de doorsnede in de 'up'-richting"""
    sm = crom(pts, n); bm = bmesh.new(); rings = []
    for k, (p, r) in enumerate(sm):
        t = (sm[min(k + 1, n - 1)][0] - sm[max(k - 1, 0)][0]).normalized()
        a = up - t * up.dot(t)
        if a.length < 1e-4: a = V((1, 0, 0)) - t * t.x
        a.normalize(); b = t.cross(a)
        rr = []
        for j in range(ring):
            ang = j / ring * math.tau
            w = 1 + wobble * noise.noise(V((k * 0.37, j * 0.61, seed)))
            rr.append(bm.verts.new(p + (a * math.cos(ang) * flat + b * math.sin(ang)) * r * w))
        rings.append(rr)
    for A, B in zip(rings, rings[1:]):
        for j in range(ring): bm.faces.new((A[j], A[(j + 1) % ring], B[(j + 1) % ring], B[j]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_object("tmp", bm, "LOW")


def fuse(name, parts, voxel, it=8, fac=0.6):
    ob = join_meshes(name, parts, "LOW"); remesh_voxel(ob, voxel)
    if it:
        sm = ob.modifiers.new("Smooth", "SMOOTH"); sm.factor = fac; sm.iterations = it
    apply_all_modifiers(ob)
    for p in parts: bpy.data.objects.remove(p, do_unlink=True)
    shade_smooth(ob, math.radians(80)); return ob


_BVH = {}
PLOOI = {}


def plooi(ob, a, b, r, diep, n=6):
    """plooigroef langs a->b: lijn eerst op het oppervlak geprojecteerd, toegepast in apply_plooien (doorlopende groef, geen putjes)"""
    from mathutils.bvhtree import BVHTree
    if ob.name not in _BVH:
        bm = bmesh.new(); bm.from_mesh(ob.data); _BVH[ob.name] = BVHTree.FromBMesh(bm); bm.free()
    bvh = _BVH[ob.name]; a, b = V(a), V(b)
    m = max(3, int((b - a).length / (r * 0.5)) + 1)
    pts = []
    for i in range(m + 1):
        q = bvh.find_nearest(a + (b - a) * (i / m))[0]
        if q is not None: pts.append(tuple(q))
    if len(pts) >= 2: PLOOI.setdefault(ob.name, []).append((pts, r, diep))


def apply_plooien(ob):
    import numpy as np
    folds = PLOOI.pop(ob.name, []); _BVH.pop(ob.name, None)
    if not folds: return
    me = ob.data; n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64); me.vertices.foreach_get("co", co); co = co.reshape(n, 3)
    nr = np.empty(n * 3, dtype=np.float64); me.vertices.foreach_get("normal", nr); nr = nr.reshape(n, 3)
    disp = np.zeros(n)
    for pts, r, diep in folds:
        P = np.array(pts); lo = P.min(0) - r; hi = P.max(0) + r
        idx = np.where(np.all((co >= lo) & (co <= hi), axis=1))[0]
        if len(idx) == 0: continue
        c = co[idx]; dmin = np.full(len(idx), 1e9); tpos = np.zeros(len(idx)); L = len(P) - 1
        for k in range(L):
            A, B = P[k], P[k + 1]; AB = B - A; l2 = max(AB @ AB, 1e-12)
            t = np.clip(((c - A) @ AB) / l2, 0, 1); d = np.linalg.norm(c - (A + t[:, None] * AB), axis=1)
            better = d < dmin; dmin[better] = d[better]; tpos[better] = (k + t[better]) / L
        w = np.clip(1 - (dmin / r) ** 2, 0, 1) ** 2 * np.sqrt(np.clip(np.sin(np.pi * tpos), 0, 1))
        disp[idx] = np.maximum(disp[idx], w * diep)
    co -= nr * disp[:, None]
    me.vertices.foreach_set("co", co.ravel()); me.update()


def frame(f, u):
    f = V(f).normalized(); u = (V(u) - f * V(u).dot(f)).normalized(); s = f.cross(u)
    return f, u, s


# ---------------- houding (ontwerpmaat; aan het eind x SCHAAL -> ~4.6 m lang, Eftepedia "vier meter lange reus") ----------------
SCHAAL = 1.0                                                     # foto: Duimpje (kleuter) haalt de halve laarsschacht; past op het OSM-eiland (8 m)
LIFT = -0.12
HIP_N, HIP_F = V((0.1, -0.45, 1.05)), V((0.1, 0.6, 1.05))
KNEE_N, KNEE_F = V((-1.4, -0.75, 3.15)), V((-2.4, 0.55, 2.9))
ANK_N, ANK_F = V((-1.75, -2.45, 0.85)), V((-4.4, 0.1, 1.4))
TOE_N, TOE_F = V((-2.85, -2.9, 0.45)), V((-6.0, -0.3, 1.0))
SH_N, SH_F = V((2.05, -1.1, 2.4)), V((2.1, 1.15, 2.5))
EL_N, EL_F = V((1.6, -1.6, 1.5)), V((1.2, 1.2, 2.1))
WR_N, WR_F = V((0.95, -1.5, 1.85)), V((1.45, 0.35, 2.75))
HAND_N, HAND_F = V((0.6, -1.65, 1.85)), V((1.55, -0.2, 2.82))
HEAD = V((2.5, 0.1, 3.2))
FACE, HUP, HS = frame((0.05, -0.22, 0.97), (1.0, 0.0, -0.05))   # gezicht omhoog/naar het publiek, kruin naar +X (rust tegen de stronk)
HK = 1.1                                                        # hoofd kleiner t.o.v. lijf/laarzen (foto)


def hp(f, u, s):            # punt in het hoofdframe (hoofdmaten x HK)
    return HEAD + (FACE * f + HUP * u + HS * s) * HK


def lerp(a, b, t): return a + (b - a) * t


def ellh(c, r, rot=None, u=28, v=16):
    return ellb(c, tuple(x * HK for x in r), rot, u, v)


def build(master):
    if os.path.exists(master): open_master(master)
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in ("LOW", "REF"): col(c)
    clear_owned()

    # ===== huid: hoofd + nek + onderarmen (profiel kijkt recht omhoog, kruin naar de stronk; close-up Commons 4019765619) =====
    rotH = Matrix((HS, FACE, HUP)).transposed()          # kolommen: x=zij, y=voor (omhoog), z=kruin (+X)
    skin = [ellh(HEAD + HUP * 0.06 * HK, (0.52, 0.5, 0.6), rotH),                    # kale schedel, lang naar de kruin
            ellh(hp(0.14, -0.4, 0), (0.42, 0.36, 0.36), rotH),                    # kaak/kin (onder de baard)
            ellh(hp(0.36, -0.13, 0.28), (0.19, 0.17, 0.18)), ellh(hp(0.36, -0.13, -0.28), (0.19, 0.17, 0.18)),   # bolle wangen
            ellh(hp(0.45, 0.13, 0), (0.36, 0.12, 0.09), rotH),                    # wenkbrauwboog
            ellh(hp(0.47, -0.3, 0), (0.22, 0.1, 0.09), rotH),                     # bovenlip-bult (onder de snor)
            ellb(lerp(hp(-0.1, -0.45, 0), V((2.0, 0.05, 2.8)), 0.5), (0.4, 0.46, 0.34))]     # nek: een volume tussen kaak en borst
    for s_ in (1, -1):                                                              # grote oren
        skin.append(ellh(hp(-0.05, -0.02, s_ * 0.53), (0.07, 0.2, 0.28), rotH))
    for el, wr in ((EL_N, WR_N), (EL_F, WR_F)):                                     # onderarmen (mouw opgestroopt)
        skin.append(loft([(*lerp(el, wr, 0.12), 0.26), (*lerp(el, wr, 0.55), 0.25), (*wr, 0.19)], 10, 16))
    huid = fuse("GEO_huid", skin, 0.022, 6); tag(huid, "huid", "head")
    for s_ in (1, -1):
        push(huid, hp(0.47, 0.02, s_ * 0.2), 0.12, -0.04)                         # oogkassen
        push(huid, hp(-0.05, -0.02, s_ * 0.6), 0.13, -0.05)                       # oorschelp hol
        plooi(huid, hp(0.48, -0.04, s_ * 0.12), hp(0.45, -0.02, s_ * 0.3), 0.022, 0.018, 6)   # ooglidplooi
        plooi(huid, hp(0.44, -0.18, s_ * 0.2), hp(0.36, -0.3, s_ * 0.34), 0.03, 0.02, 6)      # neus-lipplooi
    for k in range(3):
        plooi(huid, hp(0.5, 0.24 + k * 0.07, -0.24), hp(0.5, 0.24 + k * 0.07, 0.24), 0.03, 0.014, 8)   # voorhoofdrimpels
    # grote neus die omhoog steekt, open snurkende mond met dikke onderlip
    neus = fuse("GEO_neus", [loft([(*hp(0.47, 0.08, 0), 0.08), (*hp(0.6, -0.02, 0), 0.11), (*hp(0.7, -0.12, 0), 0.15)], 10, 16),
                             ellh(hp(0.72, -0.14, 0), (0.16, 0.17, 0.16), rotH),
                             ellh(hp(0.6, -0.21, 0.11), (0.09, 0.09, 0.08)), ellh(hp(0.6, -0.21, -0.11), (0.09, 0.09, 0.08))], 0.016, 4)
    tag(neus, "huid", "head")
    for s_ in (1, -1): push(neus, hp(0.63, -0.25, s_ * 0.07), 0.05, -0.035)
    mond = ellh(hp(0.47, -0.41, 0), (0.15, 0.07, 0.08), rotH, 18, 10); mond.name = "GEO_mond"; tag(mond, "binnen", "head")
    lip = loft([(*hp(0.48, -0.47, -0.15), 0.035), (*hp(0.55, -0.5, 0), 0.065), (*hp(0.48, -0.47, 0.15), 0.035)], 12, 12)
    lip.name = "GEO_lip"; tag(lip, "lip", "head"); shade_smooth(lip, 1.5)
    for s_ in (1, -1):
        lid = ellh(hp(0.46, 0.02, s_ * 0.2), (0.11, 0.05, 0.065), rotH, 18, 10); lid.name = "GEO_ooglid"; tag(lid, "huid", "head"); shade_smooth(lid, 1.5)
        wb = loft([(*hp(0.5, 0.15, s_ * 0.06), 0.05), (*hp(0.55, 0.2, s_ * 0.18), 0.07), (*hp(0.52, 0.22, s_ * 0.3), 0.06), (*hp(0.44, 0.17, s_ * 0.38), 0.03)],
                  14, 12, wobble=0.35, seed=s_)
        wb.name = "GEO_wenkbrauw"; tag(wb, "wenkbrauw", "head"); shade_smooth(wb, 1.5)
    # grijsbruin haar boven en achter het oor
    haar = []
    for s_ in (1, -1):
        for k in range(8):
            b = hp(-0.12 - k * 0.035, 0.12 - k * 0.05, s_ * (0.44 + 0.015 * k))
            haar.append(loft([(*b, 0.07), (*(b + HS * s_ * 0.1 + FACE * R.uniform(-0.06, 0.06) + HUP * R.uniform(0.0, 0.08)), 0.05),
                              (*(b + HS * s_ * 0.18 + HUP * R.uniform(-0.05, 0.1)), 0.012)], 8, 10, wobble=0.2, seed=k))
    hr = fuse("GEO_haar", haar, 0.02, 3); tag(hr, "haar", "head")
    # donkere baard: wig van strengen van de kaak over de borst (naar -X), smaller naar de punt
    strengen = []
    for k in range(60):
        sv = (k / 59 - 0.5) * 0.9                                        # breedte over de kaak
        st = hp(0.12 + 0.2 * (1 - abs(sv) / 0.45), -0.5 - 0.08 * abs(sv), sv)
        L = 1.0 + 0.3 * (1 - abs(sv) / 0.45) + R.uniform(-0.1, 0.1)
        pts = []
        for i in range(8):
            t = i / 7; w = math.sin(t * 6.0 + k * 0.7) * 0.05
            d = V((-0.75, 0.0, -0.25 - 0.75 * t)).normalized()           # eerst langs de kin, dan over de borst omlaag
            p = st + V((-0.75, 0, -0.45)) * L * t + V((0, 0, -0.35 * t * t)) + HS * (w - sv * HK * 0.5 * t)
            pts.append((*p, 0.15 * (1 - t) ** 0.65 + 0.025))
        strengen.append(loft(pts, 18, 10, wobble=0.18, seed=k))
    bd = fuse("GEO_baard", strengen, 0.02, 3, 0.45); tag(bd, "baard", "head")
    for k in range(14):                                                 # diepe strenggroeven
        sv = (k / 13 - 0.5) * 0.7; st = hp(0.22, -0.55, sv)
        plooi(bd, st, st + V((-0.75, 0, -0.75)) * (1.0 - abs(sv)) + HS * (-sv * 0.5), 0.028, 0.03, 8)
    # donkere hangsnor over de mondhoeken
    snor = []
    for s_ in (1, -1):
        snor.append(loft([(*hp(0.6, -0.27, s_ * 0.03), 0.085), (*hp(0.56, -0.33, s_ * 0.2), 0.09), (*hp(0.47, -0.42, s_ * 0.3), 0.075),
                          (*hp(0.37, -0.55, s_ * 0.32), 0.05), (*hp(0.3, -0.66, s_ * 0.3), 0.018)], 16, 12, wobble=0.18, seed=s_ + 5))
    sn = fuse("GEO_snor", snor, 0.016, 3); tag(sn, "baard", "head")
    for s_ in (1, -1): plooi(sn, hp(0.6, -0.3, s_ * 0.05), hp(0.36, -0.58, s_ * 0.31), 0.02, 0.02, 8)

    # handen (close-up): brede handpalm, vingers in drie kootjes met knokkels, donkere nagels; voor = over de tasklep, achter = vuist op de borst
    nagels = []
    def hand(wr, c, fd, side, krul):
        fd = fd.normalized(); up = V((0, 0, 1)); sd = fd.cross(up).normalized() * side; up = sd.cross(fd).normalized() * side
        rot = Matrix((sd, fd, up)).transposed()
        parts = [ellb(c, (0.2, 0.22, 0.085), rot), loft([(*wr, 0.18), (*(c - fd * 0.12), 0.15)], 6, 14)]
        for i, (off, ln) in enumerate(((-0.13, 0.9), (-0.045, 1.0), (0.045, 0.97), (0.125, 0.8))):
            b0 = c + fd * 0.19 + sd * off + up * 0.01
            parts.append(ellb(b0 + up * 0.03, (0.05, 0.05, 0.04)))                                   # knokkel
            pts = [b0]; d = fd.copy(); p = b0
            for k, L in enumerate((0.15, 0.1, 0.08)):
                ang = krul * (k + 1) * 0.55
                d = (fd * math.cos(ang) - up * math.sin(ang)).normalized()
                p = p + d * L * ln; pts.append(p)
            rr = (0.055, 0.05, 0.045, 0.04)
            parts.append(loft([(*q, rr[j]) for j, q in enumerate(pts)], 12, 12))
            nn = d.cross(sd).normalized()
            if nn.dot(up) < 0: nn = -nn
            ng = ellb(pts[-1] - d * 0.025 + nn * 0.03, (0.034, 0.045, 0.012), Matrix((sd, d, nn)).transposed(), 12, 8); nagels.append(ng)
        tb = c - fd * 0.04 - sd * 0.19
        tp = [tb, tb + fd * 0.12 - sd * 0.06 + up * 0.02, tb + fd * 0.22 - sd * 0.02 + up * 0.0]
        parts.append(loft([(*tp[0], 0.065), (*tp[1], 0.055), (*tp[2], 0.045)], 10, 12))
        return parts
    hparts = hand(WR_N, HAND_N, V((-0.15, -1.0, -0.25)), -1, 0.75) + hand(WR_F, HAND_F, V((0.1, -1.0, 0.15)), 1, 1.35)
    hd = fuse("GEO_handen", hparts, 0.018, 3); tag(hd, "huid")
    for k in range(4): pass
    ng = join_meshes("GEO_nagels", nagels, "LOW")
    for o in nagels: bpy.data.objects.remove(o, do_unlink=True)
    tag(ng, "nagel"); shade_smooth(ng, 1.5)

    # ===== hemd: borst + buik + mouwen tot de elleboog =====
    hemd = [ellb(V((1.95, 0.05, 2.05)), (0.9, 1.12, 0.85)), ellb(V((1.3, -0.02, 1.62)), (1.08, 1.05, 1.0)),
            ellb(V((0.55, 0.0, 1.2)), (0.7, 0.98, 0.72))]
    for sh, el in ((SH_N, EL_N), (SH_F, EL_F)):
        hemd.append(loft([(*sh, 0.42), (*lerp(sh, el, 0.5), 0.36), (*lerp(sh, el, 1.1), 0.34)], 12, 18))
    hm = fuse("GEO_hemd", hemd, 0.03, 8); tag(hm, "hemd")
    for el, wr in ((EL_N, WR_N), (EL_F, WR_F)):                         # opgerolde manchet
        c = lerp(el, wr, 0.08); mo = loft([(*lerp(el, wr, -0.06), 0.33), (*lerp(el, wr, 0.12), 0.33)], 4, 20); mo.name = "GEO_manchet"; tag(mo, "hemd"); shade_smooth(mo, 1.2)
    for k in range(11):                                                  # diagonale plooien over buik en flank (trekken naar de oksel)
        x = 0.55 + k * 0.17; plooi(hm, (x, -1.0, 1.6), (x + 0.45, -0.15, 2.65), 0.07, 0.05, 9)
    for k in range(5):                                                   # plooien aan de verre kant en onder de borst
        x = 0.8 + k * 0.3; plooi(hm, (x, 0.3, 2.55), (x + 0.3, 1.0, 1.9), 0.065, 0.045, 8)
    for sh, el in ((SH_N, EL_N), (SH_F, EL_F)):                          # pofmouw: schuine ringplooien rond de bovenarm
        ax_ = (el - sh).normalized(); s1 = ax_.cross(V((0, 0, 1))).normalized(); s2 = ax_.cross(s1)
        for k in range(4):
            c = lerp(sh, el, 0.25 + k * 0.18)
            for j in range(6):
                t0, t1 = j / 6 * math.tau, (j + 0.8) / 6 * math.tau
                q1 = c + (s1 * math.cos(t0) + s2 * math.sin(t0)) * 0.4 + ax_ * 0.1 * math.cos(t0)
                q2 = c + (s1 * math.cos(t1) + s2 * math.sin(t1)) * 0.4 + ax_ * 0.1 * math.cos(t1)
                plooi(hm, q1, q2, 0.06, 0.05, 3)
    push(hm, V((2.45, -0.25, 3.0)), 0.3, -0.07)                          # open kraag
    for el, wr in ((EL_N, WR_N), (EL_F, WR_F)):                          # rode rand aan de opgerolde mouw
        b2 = loft([(*lerp(el, wr, 0.1), 0.345), (*lerp(el, wr, 0.15), 0.345)], 4, 22); b2.name = "GEO_bies"; tag(b2, "rood")

    # ===== riem met grote tas op de heup =====
    riem = loft([(*V((0.62, y, 1.2 + 0.72 * math.sqrt(max(0, 1 - (y / 1.03) ** 2)))), 0.06) for y in (-1.04, -0.9, -0.6, 0, 0.6, 0.9, 1.04)], 16, 8, flat=0.5)
    riem.name = "GEO_riem"; tag(riem, "riem"); shade_smooth(riem, 1.0)
    tas = fuse("GEO_tas", [ellb(V((0.45, -1.75, 0.95)), (0.85, 0.45, 0.62)), ellb(V((0.45, -1.7, 1.52)), (0.8, 0.4, 0.17))], 0.025, 6); tag(tas, "vest")
    for k in range(4): plooi(tas, (-0.15 + k * 0.38, -2.15, 0.55), (-0.05 + k * 0.38, -2.1, 1.3), 0.05, 0.02, 5)
    flap = loft([(*V((0.45, -1.78, 1.55)), 0.64), (*V((0.45, -2.15, 1.12)), 0.58)], 6, 18, flat=0.16, up=V((0, 1, 0))); flap.name = "GEO_tasflap"; tag(flap, "riem"); shade_smooth(flap, 1.0)
    for dx in (-0.3, 0.3):
        g = ellb(V((0.45 + dx, -2.18, 1.15)), (0.08, 0.04, 0.08), None, 12, 8); g.name = "GEO_gesp"; tag(g, "messing")
        st = loft([(*V((0.45 + dx, -2.05, 1.55)), 0.05), (*V((0.45 + dx, -2.2, 1.2)), 0.05)], 4, 8, flat=0.35, up=V((0, 1, 0))); st.name = "GEO_tasriem"; tag(st, "riem")

    # ===== broek: zitvlak + dijen + schenen tot in de laars, wijd met plooien =====
    def been(hip, knee, ank):
        top = lerp(knee, ank, 0.42)
        return loft([(*hip, 0.7), (*lerp(hip, knee, 0.55), 0.64), (*knee, 0.55), (*lerp(knee, ank, 0.25), 0.48), (*top, 0.44)], 18, 22)
    br = fuse("GEO_broek", [ellb(V((0.2, 0.05, 1.05)), (0.95, 1.15, 0.72)), been(HIP_N, KNEE_N, ANK_N), been(HIP_F, KNEE_F, ANK_F)], 0.03, 8)
    tag(br, "broek")
    for knee, hip, ank in ((KNEE_N, HIP_N, ANK_N), (KNEE_F, HIP_F, ANK_F)):     # plooien bij de knie en over de dij
        for k in range(5):
            a = lerp(knee, hip, 0.1 + k * 0.09 + R.uniform(-0.03, 0.03)); tw = V((R.uniform(-0.2, 0.25), 0, R.uniform(-0.1, 0.2)))
            plooi(br, a + V((0, -0.6, 0)) - tw, a + V((0.15, 0.6, 0.15)) + tw, R.uniform(0.06, 0.09), R.uniform(0.035, 0.06), 7)
        for k in range(3):
            a = lerp(knee, ank, 0.1 + k * 0.08); plooi(br, a + V((0, -0.6, 0)), a + V((0.1, 0.6, 0.1)), 0.065, 0.045, 7)

    # ===== laarzen: schacht met omgeslagen kraag, voet, zool met hak, veters =====
    def laars(knee, ank, toe, nm):
        top = lerp(knee, ank, 0.36)
        ax = (ank - knee).normalized(); fw = (toe - ank); fw.z = 0; fw.normalize()
        parts = [loft([(*top, 0.52), (*lerp(top, ank, 0.4), 0.48), (*ank, 0.43), (*(ank - ax * 0.12), 0.42)], 12, 24),
                 loft([(*(ank - ax * 0.22 - fw * 0.36), 0.3), (*(ank - ax * 0.26 - fw * 0.16), 0.4), (*(ank - ax * 0.28 + fw * 0.22), 0.42),
                       (*(lerp(ank, toe, 0.55) + V((0, 0, -0.1))), 0.4), (*(lerp(ank, toe, 0.85) + V((0, 0, -0.08))), 0.36),
                       (*(toe + fw * 0.1 + V((0, 0, 0.0))), 0.22)], 20, 24, flat=0.62)]
        ob = fuse(nm, parts, 0.03, 6); tag(ob, "laars")
        s1 = ax.cross(V((0, 0, 1))).normalized() if abs(ax.z) < 0.95 else V((1, 0, 0)); s2 = ax.cross(s1).normalized()
        for k in range(7):                                                # gekreukte leren schacht: scheve boogrimpels rond de schacht
            c = lerp(top, ank, 0.18 + k * 0.11 + R.uniform(-0.03, 0.03)); t0 = R.uniform(-0.6, 0.6); sp = R.uniform(1.6, 2.6); tilt = R.uniform(-0.12, 0.12)
            arc = [c + (s1 * math.cos(t0 + sp * u) + s2 * math.sin(t0 + sp * u)) * 0.75 + ax * tilt * math.sin(sp * u * 2) for u in (i / 8 for i in range(9))]
            for q1, q2 in zip(arc, arc[1:]): plooi(ob, q1, q2, 0.09, 0.1, 2)
        veters = nm.endswith("achter")                                    # foto: verste laars = veterlaars met tong, voorste = omgeslagen kraag
        if not veters:                                                    # zware omgeslagen leren kraag die over de schacht hangt
            kraag = loft([(*(top - ax * 0.4), 0.6), (*(top - ax * 0.2), 0.64), (*(top + ax * 0.02), 0.62), (*(top + ax * 0.14), 0.56)], 10, 32, wobble=0.22, seed=len(nm))
            kraag.name = nm + "_kraag"; tag(kraag, "laars"); shade_smooth(kraag, 1.2)
            for k in range(7):                                            # hangende plooien in de kraag
                ang = k / 7 * math.tau; s1 = ax.cross(V((0, 0, 1))).normalized(); s2 = ax.cross(s1)
                d = s1 * math.cos(ang) + s2 * math.sin(ang)
                plooi(kraag, top - ax * 0.38 + d * 0.66, top + ax * 0.1 + d * 0.64, 0.05, 0.045, 6)
        else:
            rand = loft([(*(top - ax * 0.05), 0.54), (*(top + ax * 0.08), 0.52)], 4, 28); rand.name = nm + "_rand"; tag(rand, "laars"); shade_smooth(rand, 1.2)
        # neusstuk-naad en een rand (welt) boven de zool
        vo = (toe - ank); vo.z = 0; vo.normalize(); sd = V((-vo.y, vo.x, 0))
        cap = lerp(ank, toe, 0.62) + V((0, 0, -0.02))
        plooi(ob, cap + sd * 0.4 + V((0, 0, -0.08)), cap + V((0, 0, 0.22)), 0.025, 0.02, 6); plooi(ob, cap - sd * 0.4 + V((0, 0, -0.08)), cap + V((0, 0, 0.22)), 0.025, 0.02, 6)
        if veters:                                                        # vetersluiting naar het publiek: haken, kruisveter, tong
            ld = (vo + V((0, -0.9, 0.5))); ld = (ld - ax * ld.dot(ax)).normalized(); lw = ax.cross(ld).normalized()
            for k in range(7):
                c = lerp(ank, top, 0.08 + k * 0.13) + ld * 0.44
                for sg in (1, -1):
                    h = loft([(*(c + lw * sg * 0.17 - ld * 0.02), 0.03), (*(c + lw * sg * 0.17 + ld * 0.05), 0.03)], 3, 8); h.name = nm + "_haak"; tag(h, "messing")
                c2 = lerp(ank, top, 0.08 + (k + 1) * 0.13) + ld * 0.45
                if k < 6:
                    for sg in (1, -1):
                        ve = loft([(*(c + lw * sg * 0.17 + ld * 0.04), 0.022), (*(lerp(c, c2, 0.5) + ld * 0.06), 0.024), (*(c2 - lw * sg * 0.17 + ld * 0.04), 0.022)], 8, 8)
                        ve.name = nm + "_veter"; tag(ve, "veter")
            tong = loft([(*(lerp(ank, top, 0.7) + ld * 0.38), 0.17), (*(top + ld * 0.4 - ax * 0.22), 0.19), (*(top + ld * 0.52 - ax * 0.38), 0.15)], 8, 16, flat=0.25, up=ld)
            tong.name = nm + "_tong"; tag(tong, "laars"); shade_smooth(tong, 1.2)
            plooi(ob, lerp(ank, top, 0.05) + ld * 0.4, top + ld * 0.4, 0.05, 0.035, 8)             # spleet van de sluiting
        # zool: onderkant van de voet plat slaan en daaronder een zool + hak met dezelfde omtrek
        s = V((-fw.y, fw.x, 0)); hiel = ank - fw * 0.45
        seg = [lerp(hiel, toe + fw * 0.2, t / 20) for t in range(21)] if not nm.endswith("achter") else []   # liggende laars: geen platte zool
        me = ob.data; vs = [v for v in me.vertices if min((v.co - q).length for q in seg) < 0.62] if seg else []
        zb = (min(v.co.z for v in vs) + 0.06) if vs else 0
        bodem = []
        for v in vs:
            if v.co.z < zb: v.co.z = zb; bodem.append(v.co.copy())
        import mathutils.geometry as G
        hull = [bodem[i] for i in G.convex_hull_2d([(p.x, p.y) for p in bodem])] if len(bodem) > 3 else []
        if hull:
            c = sum(hull, V()) / len(hull); hull = [c + (p - c) * 1.04 for p in hull]
            bm = bmesh.new(); lo = [bm.verts.new((p.x, p.y, zb - 0.1)) for p in hull]; hi = [bm.verts.new((p.x, p.y, zb + 0.012)) for p in hull]
            bm.faces.new(lo[::-1]); bm.faces.new(hi)
            for i in range(len(hull)): bm.faces.new((lo[i], lo[(i + 1) % len(hull)], hi[(i + 1) % len(hull)], hi[i]))
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces); zo = new_mesh_object(nm + "_zool", bm, "LOW"); tag(zo, "zool")
            hak = loft([(*(hiel + fw * 0.05 + V((0, 0, zb - hiel.z - 0.1))), 0.3), (*(hiel + fw * 0.05 + V((0, 0, zb - hiel.z - 0.26))), 0.28)], 4, 16)
            hak.name = nm + "_hak"; tag(hak, "zool")
    laars(KNEE_N, ANK_N, TOE_N, "GEO_laars_voor"); laars(KNEE_F, ANK_F, TOE_F, "GEO_laars_achter")

    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"]: apply_plooien(o)
    for o in [o for o in bpy.data.objects if o.name.startswith("tmp")]: o.name = "GEO_deel"
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"]:
        o.data.transform(Matrix.Translation((0, 0, LIFT)) @ Matrix.Scale(SCHAAL, 4))
    n = len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG])
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH")
    save_master(master); log("built", n, "tris", tris)


if __name__ == "__main__":
    a = argv_after_dashes(); build(os.path.abspath(a[a.index("--master") + 1]))
