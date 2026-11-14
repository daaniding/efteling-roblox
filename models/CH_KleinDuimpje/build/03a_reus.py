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
RGB = {"huid": (226, 170, 140), "baard": (214, 216, 220), "haar": (170, 172, 176), "hemd": (222, 214, 172), "broek": (78, 104, 140),
       "vest": (120, 70, 40), "laars": (128, 74, 46), "zool": (54, 36, 26), "riem": (70, 42, 24), "messing": (190, 150, 70),
       "veter": (96, 60, 36), "lip": (190, 110, 100), "wenkbrauw": (190, 192, 196), "nagel": (236, 196, 176)}
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


def plooi(ob, a, b, r, diep, n=6):
    """plooigroef langs lijn a->b (reeks pushes naar binnen)"""
    a, b = V(a), V(b)
    for i in range(n + 1): push(ob, a + (b - a) * (i / n), r, -diep)


def frame(f, u):
    f = V(f).normalized(); u = (V(u) - f * V(u).dot(f)).normalized(); s = f.cross(u)
    return f, u, s


# ---------------- houding (ontwerpmaat; aan het eind x SCHAAL -> ~4.6 m lang, Eftepedia "vier meter lange reus") ----------------
SCHAAL = 0.56
HIP_N, HIP_F = V((0.1, -0.45, 1.05)), V((0.1, 0.6, 1.05))
KNEE_N, KNEE_F = V((-1.1, -0.65, 3.15)), V((-1.95, 0.55, 2.7))
ANK_N, ANK_F = V((-1.75, -1.55, 1.1)), V((-3.45, 0.05, 1.15))
TOE_N, TOE_F = V((-3.15, -2.1, 0.75)), V((-4.95, -0.35, 0.8))
SH_N, SH_F = V((2.6, -1.1, 2.05)), V((2.65, 1.15, 2.15))
EL_N, EL_F = V((1.85, -1.55, 1.45)), V((1.8, 1.15, 2.0))
WR_N, WR_F = V((0.95, -1.4, 1.95)), V((2.1, 0.4, 2.75))
HAND_N, HAND_F = V((0.6, -1.5, 1.95)), V((2.3, 0.05, 2.9))
HEAD = V((3.45, 0.1, 2.95))
FACE, HUP, HS = frame((0.05, -0.4, 0.92), (0.97, 0.0, -0.15))   # gezicht omhoog/naar het publiek, kruin naar +X (rust tegen de stronk)
HK = 0.82                                                        # hoofd kleiner t.o.v. lijf/laarzen (foto)


def hp(f, u, s):            # punt in het hoofdframe (hoofdmaten x HK)
    return HEAD + (FACE * f + HUP * u + HS * s) * HK


def lerp(a, b, t): return a + (b - a) * t


def build(master):
    if os.path.exists(master): open_master(master)
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in ("LOW", "REF"): col(c)
    clear_owned()

    # ===== huid: hoofd + nek + onderarmen + handen =====
    rotH = Matrix((HS, FACE, HUP)).transposed()          # kolommen: x=zij, y=voor, z=kruin
    skin = [ellb(HEAD + HUP * 0.05, (0.5, 0.52, 0.62), rotH),                     # schedel (kaal)
            ellb(hp(0.22, -0.32, 0), (0.42, 0.36, 0.34), rotH),                    # kaak/onderkant (onder de baard)
            ellb(hp(0.38, -0.12, 0.27), (0.17, 0.16, 0.17)), ellb(hp(0.38, -0.12, -0.27), (0.17, 0.16, 0.17)),   # wangen
            ellb(hp(0.47, 0.13, 0), (0.33, 0.1, 0.07), rotH),                     # wenkbrauwboog
            loft([(*hp(-0.15, -0.55, 0), 0.4), (*(HEAD - HUP * 0.85 + FACE * 0.05), 0.5), (*V((2.7, 0.05, 1.95)), 0.6)], 10, 20)]  # nek
    for s in (1, -1):                                                              # grote oren
        e = ellb(hp(-0.02, 0.0, s * 0.52), (0.06, 0.17, 0.26), rotH); skin.append(e)
    # onderarmen (hemdsmouw opgestroopt tot net onder de elleboog)
    for el, wr in ((EL_N, WR_N), (EL_F, WR_F)):
        skin.append(loft([(*lerp(el, wr, 0.12), 0.26), (*lerp(el, wr, 0.55), 0.25), (*wr, 0.19)], 10, 16))
    huid = fuse("GEO_huid", skin, 0.025, 6); tag(huid, "huid", "head")
    # sculpt: oogkassen, neusbrug, rimpels in het voorhoofd, gesloten ogen (wallen)
    for s in (1, -1):
        push(huid, hp(0.47, 0.03, s * 0.19), 0.12, -0.035)
        push(huid, hp(0.44, -0.06, s * 0.21), 0.08, 0.02)
        push(huid, hp(-0.02, 0.0, s * 0.56), 0.12, -0.03)              # oorschelp hol
    for k in range(3):
        plooi(huid, hp(0.5, 0.22 + k * 0.07, -0.22), hp(0.5, 0.22 + k * 0.07, 0.22), 0.035, 0.012, 8)

    # neus (dik en lang, naar boven), oogleden, lippen
    neus = fuse("GEO_neus", [ellb(hp(0.62, -0.08, 0), (0.15, 0.2, 0.2), rotH), ellb(hp(0.56, 0.06, 0), (0.08, 0.1, 0.16), rotH),
                             ellb(hp(0.56, -0.14, 0.11), (0.08, 0.09, 0.08)), ellb(hp(0.56, -0.14, -0.11), (0.08, 0.09, 0.08))], 0.018, 4)
    tag(neus, "huid", "head")
    for s in (1, -1):
        push(neus, hp(0.6, -0.2, s * 0.08), 0.05, -0.03)                          # neusgaten
        lid = ellb(hp(0.47, 0.03, s * 0.19), (0.11, 0.055, 0.07), rotH, 18, 10); lid.name = "GEO_ooglid"; tag(lid, "huid", "head"); shade_smooth(lid, 1.5)
        wb = loft([(*hp(0.5, 0.15, s * 0.07), 0.04), (*hp(0.52, 0.19, s * 0.2), 0.055), (*hp(0.46, 0.2, s * 0.33), 0.035)], 10, 10, wobble=0.25, seed=s)
        wb.name = "GEO_wenkbrauw"; tag(wb, "wenkbrauw", "head"); shade_smooth(wb, 1.5)
    lip = loft([(*hp(0.5, -0.3, -0.12), 0.03), (*hp(0.53, -0.31, 0), 0.04), (*hp(0.5, -0.3, 0.12), 0.03)], 10, 10)
    lip.name = "GEO_lip"; tag(lip, "lip", "head"); shade_smooth(lip, 1.5)

    # haar: grijze plukken boven de oren en achter op het hoofd
    haar = []
    for s in (1, -1):
        for k in range(7):
            b = hp(-0.15 - k * 0.04, 0.15 - k * 0.06, s * (0.42 + 0.02 * k))
            haar.append(loft([(*b, 0.07), (*(b + HS * s * 0.12 + FACE * R.uniform(-0.05, 0.08) + HUP * R.uniform(0.0, 0.1)), 0.05),
                              (*(b + HS * s * 0.22 + HUP * R.uniform(-0.05, 0.12)), 0.012)], 8, 10, wobble=0.2, seed=k))
    hr = fuse("GEO_haar", haar, 0.02, 3); tag(hr, "haar", "head")

    # baard: golvende strengen van de kaak over de borst (richting -X), snor met krullende punten
    strengen = []
    for k in range(26):
        a = (k / 25 - 0.5) * 2.4                                       # rond de kaak
        st = hp(0.28 + 0.12 * math.cos(a), -0.35, 0.4 * math.sin(a))
        L = 0.85 + 0.35 * math.cos(a) + R.uniform(-0.1, 0.1)
        d = (-HUP * 0.85 + FACE * 0.25).normalized()
        pts = []
        for i in range(6):
            t = i / 5; w = math.sin(t * 5.5 + k) * 0.06
            p = st + d * L * t + HS * (w + math.sin(a) * 0.12 * t) + FACE * (0.1 * math.sin(t * math.pi))
            pts.append((*p, 0.12 * (1 - t) + 0.02))
        strengen.append(loft(pts, 14, 10, wobble=0.15, seed=k))
    bd = fuse("GEO_baard", strengen, 0.022, 4, 0.5); tag(bd, "baard", "head")
    for k in range(10):                                                 # golfgroeven in de baard
        a = (k / 9 - 0.5) * 2.0; st = hp(0.4, -0.45, 0.35 * math.sin(a))
        plooi(bd, st, st - HUP * 0.75 + FACE * 0.1, 0.03, 0.018, 7)
    snor = []
    for s in (1, -1):
        snor.append(loft([(*hp(0.6, -0.24, s * 0.02), 0.06), (*hp(0.57, -0.28, s * 0.18), 0.07), (*hp(0.48, -0.26, s * 0.34), 0.05),
                          (*hp(0.42, -0.14, s * 0.42), 0.025)], 14, 12, wobble=0.12, seed=s + 5))
    sn = fuse("GEO_snor", snor, 0.016, 3); tag(sn, "baard", "head")

    # handen: grote handpalm + worstvingers, ineengelegd op de buik
    def hand(wr, c, vinger_dir, side):
        parts = [ellb(c, (0.22, 0.17, 0.09), Matrix.Rotation(math.atan2(vinger_dir.y, vinger_dir.x), 3, "Z"))]
        sd = V((-vinger_dir.y, vinger_dir.x, 0)).normalized()
        for i in range(4):
            b = c + vinger_dir * 0.16 + sd * (i - 1.5) * 0.085
            parts.append(loft([(*b, 0.05), (*(b + vinger_dir * 0.13 + V((0, 0, -0.02))), 0.046), (*(b + vinger_dir * 0.2 + V((0, 0, -0.1))), 0.04)], 8, 10))
        tb = c - vinger_dir * 0.05 + sd * side * 0.17
        parts.append(loft([(*tb, 0.055), (*(tb + vinger_dir * 0.14 + sd * side * 0.05), 0.045)], 8, 10))
        parts.append(loft([(*wr, 0.19), (*c, 0.15)], 6, 14))
        return parts
    hparts = hand(WR_N, HAND_N, V((0.9, 0.42, 0)).normalized(), -1) + hand(WR_F, HAND_F, V((0.25, -0.95, 0)).normalized(), 1)
    hd = fuse("GEO_handen", hparts, 0.02, 4); tag(hd, "huid")

    # ===== hemd: borst + buik + mouwen tot de elleboog =====
    hemd = [ellb(V((2.25, 0.05, 1.72)), (0.85, 1.08, 0.78)), ellb(V((1.3, -0.02, 1.5)), (1.05, 1.02, 0.95)),
            ellb(V((0.55, 0.0, 1.2)), (0.7, 0.98, 0.72))]
    for sh, el in ((SH_N, EL_N), (SH_F, EL_F)):
        hemd.append(loft([(*sh, 0.42), (*lerp(sh, el, 0.5), 0.36), (*lerp(sh, el, 1.1), 0.34)], 12, 18))
    hm = fuse("GEO_hemd", hemd, 0.03, 8); tag(hm, "hemd")
    for el, wr in ((EL_N, WR_N), (EL_F, WR_F)):                         # opgerolde manchet
        c = lerp(el, wr, 0.08); mo = loft([(*lerp(el, wr, -0.06), 0.33), (*lerp(el, wr, 0.12), 0.33)], 4, 20); mo.name = "GEO_manchet"; tag(mo, "hemd"); shade_smooth(mo, 1.2)
    for k in range(9):                                                   # plooien over buik en mouwen
        x = 0.7 + k * 0.22; plooi(hm, (x, -0.9, 1.7), (x + 0.15, -0.2, 2.45), 0.05, 0.02, 6)
    # kraag open met V-hals (lichte inkeping) en een rood sjaaltje onder de baard (foto: rode puntjes)
    push(hm, V((2.85, -0.25, 2.25)), 0.25, -0.06)

    # ===== leren vest (open aan de voorkant) =====
    vest = join_meshes("GEO_vest", [hm], "LOW")
    bm = bmesh.new(); bm.from_mesh(vest.data); bm.normal_update()
    weg = [f for f in bm.faces if (f.normal.z > 0.5 and 0.2 < f.calc_center_median().x < 2.95) or f.calc_center_median().x < 0.45
           or f.calc_center_median().z < 0.7 or (f.calc_center_median() - V((2.0, 0, 1.75))).length > 1.45]
    for f in bm.faces:
        p = f.calc_center_median()
        if (p - SH_N).length < 0.6 and p.x < 2.2 or (p - SH_F).length < 0.6 and p.x < 2.2: weg.append(f)   # geen mouwen
    bmesh.ops.delete(bm, geom=list(set(weg)), context="FACES")
    for v in bm.verts: v.co += v.normal * 0.045
    bm.to_mesh(vest.data); bm.free()
    so = vest.modifiers.new("dik", "SOLIDIFY"); so.thickness = 0.035; so.offset = 1; apply_all_modifiers(vest); tag(vest, "vest"); shade_smooth(vest, 1.0)

    # ===== riem met grote tas op de heup =====
    riem = loft([(*V((0.62, y, 1.2 + 0.72 * math.sqrt(max(0, 1 - (y / 1.03) ** 2)))), 0.06) for y in (-1.04, -0.9, -0.6, 0, 0.6, 0.9, 1.04)], 16, 8, flat=0.5)
    riem.name = "GEO_riem"; tag(riem, "riem"); shade_smooth(riem, 1.0)
    tas = fuse("GEO_tas", [ellb(V((0.3, -1.1, 1.25)), (0.42, 0.22, 0.38)), ellb(V((0.3, -1.08, 1.5)), (0.4, 0.2, 0.12))], 0.025, 5); tag(tas, "vest")
    flap = loft([(*V((0.3, -1.2, 1.55)), 0.36), (*V((0.3, -1.32, 1.2)), 0.3)], 6, 16, flat=0.18, up=V((0, 1, 0))); flap.name = "GEO_tasflap"; tag(flap, "riem"); shade_smooth(flap, 1.0)
    for dx in (-0.16, 0.16):
        g = ellb(V((0.3 + dx, -1.4, 1.27)), (0.06, 0.03, 0.06), None, 12, 8); g.name = "GEO_gesp"; tag(g, "messing")

    # ===== broek: zitvlak + dijen + schenen tot in de laars, wijd met plooien =====
    def been(hip, knee, ank):
        top = lerp(knee, ank, 0.42)
        return loft([(*hip, 0.62), (*lerp(hip, knee, 0.55), 0.6), (*knee, 0.52), (*lerp(knee, ank, 0.25), 0.48), (*top, 0.47)], 18, 20)
    br = fuse("GEO_broek", [ellb(V((0.2, 0.02, 1.05)), (0.85, 1.05, 0.68)), been(HIP_N, KNEE_N, ANK_N), been(HIP_F, KNEE_F, ANK_F)], 0.03, 8)
    tag(br, "broek")
    for knee, hip, ank in ((KNEE_N, HIP_N, ANK_N), (KNEE_F, HIP_F, ANK_F)):     # plooien bij de knie en over de dij
        for k in range(5):
            a = lerp(knee, hip, 0.12 + k * 0.08); plooi(br, a + V((0, -0.5, 0)), a + V((0.15, 0.5, 0.15)), 0.06, 0.035, 6)
        for k in range(3):
            a = lerp(knee, ank, 0.1 + k * 0.08); plooi(br, a + V((0, -0.5, 0)), a + V((0.1, 0.5, 0.1)), 0.05, 0.03, 6)

    # ===== laarzen: schacht met omgeslagen kraag, voet, zool met hak, veters =====
    def laars(knee, ank, toe, nm):
        top = lerp(knee, ank, 0.36)
        ax = (ank - knee).normalized(); fw = (toe - ank); fw.z = 0; fw.normalize()
        parts = [loft([(*top, 0.56), (*lerp(top, ank, 0.4), 0.5), (*ank, 0.44), (*(ank - ax * 0.12), 0.43)], 12, 22),
                 loft([(*(ank - ax * 0.2 - fw * 0.25), 0.36), (*(ank - ax * 0.3 + fw * 0.35), 0.4), (*lerp(ank, toe, 0.75) + V((0, 0, -0.05)), 0.34),
                       (*(toe + V((0, 0, 0.03))), 0.2)], 14, 20, flat=0.72)]
        ob = fuse(nm, parts, 0.03, 6); tag(ob, "laars")
        for k in range(6):                                                # leren rimpels in de schacht en op de wreef
            a = lerp(top, ank, 0.25 + k * 0.12); s = ax.cross(V((0, 0, 1))).normalized() if abs(ax.z) < 0.95 else V((1, 0, 0))
            plooi(ob, a + s * 0.55, a - s * 0.55 + ax * 0.08, 0.05, 0.03, 6)
        kraag = loft([(*(top - ax * 0.18), 0.64), (*(top + ax * 0.12), 0.62)], 4, 24, wobble=0.08, seed=len(nm)); kraag.name = nm + "_kraag"; tag(kraag, "laars"); shade_smooth(kraag, 1.2)
        # zool: plat blok onder de voet, hak achter
        bm = bmesh.new(); s = V((-fw.y, fw.x, 0))
        hiel, teen = ank - fw * 0.35, toe + fw * 0.12
        z0 = min(ank.z, toe.z) - 0.38
        for p, w in ((hiel, 0.3), (lerp(hiel, teen, 0.5), 0.36), (teen, 0.22)):
            pass
        pts = [hiel - s * 0.3, lerp(hiel, teen, 0.55) - s * 0.36, teen - s * 0.18, teen + fw * 0.08, teen + s * 0.18, lerp(hiel, teen, 0.55) + s * 0.36, hiel + s * 0.3, hiel - fw * 0.08]
        lo = [bm.verts.new((p.x, p.y, z0)) for p in pts]; hi = [bm.verts.new((p.x, p.y, z0 + 0.1)) for p in pts]
        bm.faces.new(lo[::-1]); bm.faces.new(hi)
        for i in range(len(pts)): bm.faces.new((lo[i], lo[(i + 1) % len(pts)], hi[(i + 1) % len(pts)], hi[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); zo = new_mesh_object(nm + "_zool", bm, "LOW"); tag(zo, "zool")
        hak = ellb(hiel + V((0, 0, -0.42)) , (0.26, 0.26, 0.1), None, 16, 8); hak.name = nm + "_hak"; tag(hak, "zool")
        # veters: kruislingse veter over de schacht-voorkant
        vo = (toe - ank); vo.z = 0; vo.normalize()
        for k in range(5):
            a = lerp(ank, top, 0.1 + k * 0.17) + vo * 0.45
            ve = loft([(*(a + s * 0.14), 0.02), (*(a + V((0, 0, 0.0)) + vo * 0.03), 0.022), (*(a - s * 0.14 + ax * 0.1), 0.02)], 6, 6)
            ve.name = nm + "_veter"; tag(ve, "veter")
    laars(KNEE_N, ANK_N, TOE_N, "GEO_laars_voor"); laars(KNEE_F, ANK_F, TOE_F, "GEO_laars_achter")

    for o in [o for o in bpy.data.objects if o.name.startswith("tmp")]: o.name = "GEO_deel"
    n = len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG])
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH")
    save_master(master); log("built", n, "tris", tris)


if __name__ == "__main__":
    a = argv_after_dashes(); build(os.path.abspath(a[a.index("--master") + 1]))
