"""03_forms Hans en Grietje: snoephuisje. Meters, Z op, gevel kijkt naar -Y, +X = rechts (ZZO), oorsprong midden BAG, z=0 maaiveld.
- Muren: een stucmassa (primitieven -> voxel remesh -> uitlopende voet + ruis -> decimeren -> openingen uitsnijden) = HG_muren__stuc.
- Daken: dakbasis (MAT_dakbasis) + losse pannenkoeken in rijen, onderste rij en windveren hangen over de rand (herbouw 2024) = BAKE_pannenkoek
  (vaste UV's naar textures/HG_pannenkoek_kleur.png, 2x2 varianten).
- Snoep (harten, koeken, krakelingen, snoepjes, mozaiek), houten deur/luiken, steunbalken = BAKE_snoep (UV's naar textures/HG_snoep_kleur.png 4x4).
  Voorgevel: posities uit ref/front.jpg via de fotocamera teruggerekend (straal door de pixel -> muuroppervlak). Overige gevels: verspreid.
- Figuren (Hans, Grietje, heks, kat, vogels) komen uit Roblox generate_mesh en worden in Studio geplaatst.
Gebruik: Blender -b -P 03_forms.py -- --master AR_HansGrietje_master.blend
"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree
PHASE = "03_forms"; OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix, "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns); globals().update({k: v for k, v in _ns.items() if callable(v)})
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rnd = random.Random(11)
COLS = {"stuc": ((236, 230, 214), 0.9), "dakbasis": ((142, 88, 46), 0.9), "ijzer": ((40, 52, 50), 0.5), "glas": ((30, 36, 34), 0.2),
        "lood": ((58, 60, 60), 0.4), "donker": ((10, 9, 8), 1.0), "vuur": ((255, 140, 40), 0.5), "teal": ((60, 94, 90), 0.6)}

# ------------------------------------------------------------------ hoofdmaten (asset-brief.md)
X0, X1, YF, YB = -3.15, 1.25, -1.25, 2.7          # hoofdhuis
EAVE, RIDGE, XR = 2.5, 5.6, -0.95                  # dakvoet, nok, noklijn x
RX0, RX1, RY0, RY1 = -3.45, 1.55, -1.45, 2.95      # dakrand (overstek)
TWR = (0.7, 2.2, 1.0)                              # toren cx, cy, r
DOOR = (-0.48, 0.13, 1.46, 2.82)                   # deur x0, x1, z0, z1 (front.jpg teruggerekend)
SLOPE = (RIDGE - EAVE) / (XR - RX0)


def roof_z(x):
    return RIDGE - abs(x - XR) * SLOPE


# ------------------------------------------------------------------ fotocamera (cam_match: --cam -0.3,-8.6,1.6,26 --sensor 25.4 --pitch 8)
CAM = Vector((-0.3, -8.6, 1.6)); _th = math.radians(98)
FWD = Vector((0, math.sin(_th), -math.cos(_th))); UP = Vector((0, math.cos(_th), math.sin(_th))); RIGHT = Vector((1, 0, 0)); KF = 12.7 / 26.0


def ray900(px, py):   # pixel in de 900 px versie van Hghuis-vk -> straalrichting
    u = (px / 900 * 1000 - 500) / 500 * KF; v = (500 - py / 900 * 1000) / 500 * KF
    return (FWD + RIGHT * u + UP * v).normalized()


def at_plane(px, py, yp):
    d = ray900(px, py); t = (yp - CAM.y) / d.y; p = CAM + d * t; return p.x, p.z


# ------------------------------------------------------------------ bmesh-hulpjes
def prism_y(bm, pts_xz, y0, y1):   # veelhoek in (x,z), geextrudeerd langs y
    a = [bm.verts.new((x, y0, z)) for x, z in pts_xz]; b = [bm.verts.new((x, y1, z)) for x, z in pts_xz]; n = len(pts_xz)
    bm.faces.new(a[::-1]); bm.faces.new(b)
    for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))


def prism_x(bm, pts_yz, x0, x1):
    a = [bm.verts.new((x0, y, z)) for y, z in pts_yz]; b = [bm.verts.new((x1, y, z)) for y, z in pts_yz]; n = len(pts_yz)
    bm.faces.new(a); bm.faces.new(b[::-1])
    for i in range(n): bm.faces.new((a[(i + 1) % n], a[i], b[i], b[(i + 1) % n]))


def cube(bm, x0, x1, y0, y1, z0, z1):
    prism_y(bm, [(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y0, y1)


def frustum(bm, cx, cy, r0, r1, z0, z1, segs=32):
    a = [bm.verts.new((cx + r0 * math.cos(2 * math.pi * i / segs), cy + r0 * math.sin(2 * math.pi * i / segs), z0)) for i in range(segs)]
    b = [bm.verts.new((cx + r1 * math.cos(2 * math.pi * i / segs), cy + r1 * math.sin(2 * math.pi * i / segs), z1)) for i in range(segs)]
    bm.faces.new(a[::-1]); bm.faces.new(b)
    for i in range(segs): bm.faces.new((a[i], a[(i + 1) % segs], b[(i + 1) % segs], b[i]))


def obj_from_bm(name, bm, mat, collection="FORMS"):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = new_mesh_object(name, bm, collection); assign(ob, bpy.data.materials["MAT_" + mat]); return ob


def apply_mod(ob, kind, **kw):
    m = ob.modifiers.new(kind, kind)
    for k, v in kw.items(): setattr(m, k, v)
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.view_layer.objects: o.select_set(o == ob)
    bpy.ops.object.modifier_apply(modifier=m.name)


# ------------------------------------------------------------------ muren
def walls():
    bm = bmesh.new()
    # hoofdhuis als vijfhoek langs y; gevelpunt net onder de dakbasis
    zt = lambda x: roof_z(x) - 0.10
    prism_y(bm, [(X0, -0.1), (X1, -0.1), (X1, zt(X1)), (XR, zt(XR)), (X0, zt(X0))], YF, YB)
    cube(bm, -1.27, -0.63, -1.33, -0.85, 4.4, 5.92)                                    # witte stapel op de gevelpunt
    # erker (muur onder het lessenaarsdak, dak van z 1.25 voor tot 2.45 tegen de gevel)
    prism_x(bm, [(-2.15, -0.1), (YF + 0.15, -0.1), (YF + 0.15, 2.3), (-2.15, 1.12)], -2.55, -0.42)
    # bordes + trap (drempel 1.42, 4 treden naar voren en rechts breder)
    cube(bm, -0.42, 0.32, -1.62, YF + 0.15, -0.1, 1.42)
    for i in range(4):
        cube(bm, -0.42, 0.32 + 0.18 * (i + 1), -1.62 - 0.27 * (i + 1), YF + 0.15, -0.1, 1.42 - 0.284 * (i + 1))
    # bonte schoorsteen links voor (snoepmozaiek), taps
    frustum(bm, -3.45, -1.0, 0.44, 0.34, -0.1, 4.45, 16)
    # toren met witte uitlopende kraag
    frustum(bm, TWR[0], TWR[1], TWR[2], TWR[2], -0.1, 4.6, 40)
    frustum(bm, TWR[0], TWR[1], TWR[2], 1.24, 4.45, 4.95, 40)
    # overstek op de zuidgevel + dakkapel
    cube(bm, X1 - 0.1, X1 + 0.27, -1.2, 0.05, 1.72, 2.75)
    prism_x(bm, [(-1.0, 2.3), (-0.08, 2.3), (-0.08, 3.38), (-0.54, 3.82), (-1.0, 3.38)], 0.1, 1.48)
    # kooi van Hans
    cube(bm, X1 - 0.1, 3.4, 0.0, 2.2, -0.1, 1.82)
    ob = obj_from_bm("HG_muren__stuc", bm, "stuc")
    apply_mod(ob, "REMESH", mode="VOXEL", voxel_size=0.05, use_smooth_shade=True)
    # uitlopende voet (Hg-achter) + golvend stucwerk
    me = ob.data; bm = bmesh.new(); bm.from_mesh(me); bm.normal_update()
    for v in bm.verts:
        n = v.normal; h = Vector((n.x, n.y, 0))
        if h.length > 0.3:
            h.normalize(); f = max(0.0, 1 - v.co.z / 1.1) ** 2
            v.co += h * (0.13 * f * (0.7 + 0.6 * (noise.noise(v.co * 0.9) + 0.5)))
        v.co += n * (0.022 * noise.noise(v.co * 1.8) + 0.007 * noise.noise(v.co * 7.0))
    for v in bm.verts:
        if v.co.z < 0: v.co.z = min(v.co.z, -0.05)
    bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.to_mesh(me); bm.free()
    apply_mod(ob, "DECIMATE", decimate_type="COLLAPSE", ratio=0.14)
    # openingen
    cb = bmesh.new()
    def arch_cut(x0, x1, z0, z1, ya, yb, n=10):
        w = (x1 - x0) / 2; cx = (x0 + x1) / 2; pts = [(x0, z0), (x1, z0), (x1, z1 - w)]
        for i in range(1, n): a = math.pi * i / n; pts.append((cx + w * math.cos(a), z1 - w + w * math.sin(a)))
        pts.append((x0, z1 - w)); prism_y(cb, pts, ya, yb)
    arch_cut(DOOR[0], DOOR[1], DOOR[2], DOOR[3], -1.9, YF + 0.13)                    # voordeur (nis 0.12)
    cx_, cz_ = at_plane(315, 430, YF)                                                 # katgat (rond, diep)
    pts = [(cx_ + 0.2 * math.cos(2 * math.pi * i / 14), cz_ + 0.14 * math.sin(2 * math.pi * i / 14)) for i in range(14)]
    prism_y(cb, pts, -1.9, YF + 0.45)
    wx0, wz1 = at_plane(360, 232, YF); wx1, wz0 = at_plane(410, 305, YF)             # bovenraam
    cube(cb, wx0, wx1, -1.9, YF + 0.1, wz0, wz1)
    bx0, bz1 = at_plane(262, 698, -2.15); bx1, bz0 = at_plane(372, 785, -2.15)       # erkerraam
    cube(cb, bx0, bx1, -2.6, -2.15 + 0.1, max(0.12, bz0), bz1)
    cube(cb, 1.85, 2.85, -0.5, 0.65, 0.5, 1.38)                                       # tralievenster kooi (diep)
    cube(cb, 1.3, 1.9, -0.72, -0.34, 2.62, 3.12)                                      # dakkapelraam (kijkt +x)
    a = math.radians(-35); tx, ty = TWR[0] + math.cos(a) * 1.0, TWR[1] + math.sin(a) * 1.0
    tb = bmesh.new(); prism_y(tb, [(-0.16, 3.45), (0.16, 3.45), (0.16, 3.95), (-0.16, 3.95)], -0.4, 0.4)
    bmesh.ops.transform(tb, matrix=Matrix.Translation((tx, ty, 0)) @ Matrix.Rotation(a + math.pi / 2, 4, "Z"), verts=tb.verts); cb.from_mesh(_bm_to_me(tb))
    cube(cb, -2.3, -1.6, YB - 0.4, YB + 0.5, 0.0, 1.6)                                # technische deur achter
    for xw in (-0.6, 0.2): cube(cb, xw - 0.18, xw + 0.18, YB - 0.4, YB + 0.5, 1.5, 2.0)   # glas-in-loodraampjes achter
    cube(cb, X0 - 0.5, X0 + 0.12, -0.6, 0.0, 1.35, 2.0)                               # raam noordgevel
    cut = obj_from_bm("CUT_openingen", cb, "donker"); cut.hide_render = True
    bo = ob.modifiers.new("open", "BOOLEAN"); bo.operation = "DIFFERENCE"; bo.object = cut; bo.solver = "EXACT"
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.view_layer.objects: o.select_set(o == ob)
    bpy.ops.object.modifier_apply(modifier=bo.name)
    bpy.data.objects.remove(cut)
    shade_smooth(ob, math.radians(50))
    return ob


# ------------------------------------------------------------------ dakbasis + pannenkoeken
PK = bmesh.new(); PK_UV = PK.loops.layers.uv.new("UVMap")
SN = bmesh.new(); SN_UV = SN.loops.layers.uv.new("UVMap")


def pancake(c, U, V, N, r, var, bend=None, segs=8, t=0.032):
    """Pannenkoek: schijf (segs-hoek, dikte t) in het vlak (U,V) rond c. bend(p) -> (p, n) buigt hem over een rand."""
    tu, tv = (var % 2) * 0.5, (var // 2) * 0.5
    ang0 = rnd.random() * math.tau; ov = 1.0 + rnd.random() * 0.15
    ring = []
    for i in range(segs):
        a = ang0 + math.tau * i / segs; rr = r * (1 + 0.06 * math.sin(3 * a + ang0))
        lx, ly = math.cos(a) * rr * ov, math.sin(a) * rr
        ring.append((lx, ly, math.cos(a - ang0) * 0.46, math.sin(a - ang0) * 0.46))
    def P(lx, ly, h, lift):
        p = c + U * lx + V * ly + N * lift; n = N
        if bend: p, n = bend(p, n)
        return p + n * h
    lift = lambda ly: 0.035 * (0.5 - ly / (2 * r)) + 0.02          # onderrand ligt hoger: dakpaneffect
    top = [PK.verts.new(P(lx, ly, t / 2, lift(ly))) for lx, ly, _, _ in ring]; ct = PK.verts.new(P(0, 0, t / 2 + 0.012, lift(0)))
    bot = [PK.verts.new(P(lx * 0.92, ly * 0.92, -t / 2, lift(ly))) for lx, ly, _, _ in ring]
    for i in range(segs):
        j = (i + 1) % segs
        f = PK.faces.new((ct, top[i], top[j]))
        for l, (uu, vv) in zip(f.loops, ((0.5, 0.5), (0.5 + ring[i][2], 0.5 + ring[i][3]), (0.5 + ring[j][2], 0.5 + ring[j][3]))):
            l[PK_UV].uv = (tu + uu * 0.5, tv + vv * 0.5)
        f = PK.faces.new((top[j], top[i], bot[i], bot[j]))
        for l, k in zip(f.loops, (j, i, i, j)):
            l[PK_UV].uv = (tu + (0.5 + ring[k][2] * 1.04) * 0.5, tv + (0.5 + ring[k][3] * 1.04) * 0.5)
    f = PK.faces.new(bot[::-1])
    for l in f.loops: l[PK_UV].uv = (tu + 0.25, tv + 0.25)


def edge_bend(O, U, V, N, LU, LV, edges, rho=0.06, maxa=1.15):
    """Buig punten die buiten de rand (u<0, u>LU, v<0) vallen over die rand naar beneden (hangende pannenkoeken)."""
    def f(p, n):
        d = p - O; u, v, w = d.dot(U), d.dot(V), d.dot(N)
        for kind in edges:
            if kind == "v0" and v < 0: s, axis, base = -v, -V, O + U * u
            elif kind == "u0" and u < 0: s, axis, base = -u, -U, O + V * v
            elif kind == "u1" and u > LU: s, axis, base = u - LU, U, O + U * LU + V * v
            else: continue
            th = min(s / rho, maxa); pt = base + axis * (rho * math.sin(th)) - N * (rho * (1 - math.cos(th))) + N * w
            nn = (N * math.cos(th) + axis * math.sin(th)).normalized()
            if s / rho > maxa: pt += (-N * math.sin(maxa) + axis * math.cos(maxa)) * (s - rho * maxa)
            return pt, nn
        return p, n
    return f


def pancakes_plane(O, U, V, LU, LV, edges=("v0",), rowh=0.19, colw=0.27, r=0.165, keep=None, overhang=0.11):
    N = U.cross(V).normalized(); bend = edge_bend(O, U, V, N, LU, LV, edges)
    nrow = int(LV / rowh) + 1; n = 0
    for k in range(nrow):
        v = k * rowh - (overhang if "v0" in edges else 0) + r * 0.6
        if v > LV - r * 0.4: break
        u0 = 0.0 if "u0" in edges else colw * 0.4      # windveer: pannenkoek met het hart op de rand (hangt half over)
        u1 = LU if "u1" in edges else LU - colw * 0.4
        m = max(1, round((u1 - u0) / colw)); step = (u1 - u0) / m
        us = [u0 + (i + 0.5 * (k % 2)) * step for i in range(m + 1)]
        us = [u for u in us if u <= u1 + 1e-6]
        if k % 2: us = [u0] + us + ([u1] if us[-1] < u1 - step * 0.3 else [])
        for u in us:
            uu = u + rnd.uniform(-0.03, 0.03); vv = v + rnd.uniform(-0.025, 0.025)
            c = O + U * uu + V * vv
            if keep is None or keep(c, uu, vv):
                pancake(c, U, V, N, r * rnd.uniform(0.9, 1.12), rnd.randrange(4), bend); n += 1
    return n


def slab(bm, pts, thick=0.08):   # dakbasis: vlak (lijst punten) met dikte naar binnen
    N = (pts[1] - pts[0]).cross(pts[2] - pts[0]).normalized()
    a = [bm.verts.new(p) for p in pts]; b = [bm.verts.new(p - N * thick) for p in pts]; k = len(pts)
    bm.faces.new(a); bm.faces.new(b[::-1])
    for i in range(k): bm.faces.new((a[(i + 1) % k], a[i], b[i], b[(i + 1) % k]))


def roofs():
    db = bmesh.new(); n = 0
    def not_in(c, *_):
        if (Vector((c.x, c.y)) - Vector(TWR[:2])).length < TWR[2] + 0.05: return False      # toren
        if -1.35 < c.x < -0.55 and c.y < -0.8 and c.z > 4.3: return False                   # stapel
        if 0.0 < c.x < 1.65 and -1.12 < c.y < 0.05 and c.z < 3.95: return False             # dakkapel
        return True
    L = math.hypot(XR - RX0, RIDGE - EAVE)
    # hoofddak noordkant (links) en zuidkant (rechts); U langs y, V omhoog naar de nok
    for side in (-1, 1):
        xe = RX0 if side < 0 else RX1
        O = Vector((xe, RY1 if side < 0 else RY0, EAVE)); Vt = (Vector((XR, O.y, RIDGE)) - O).normalized()
        U = Vector((0, -1 if side < 0 else 1, 0))
        slab(db, [O, O + U * (RY1 - RY0), O + U * (RY1 - RY0) + Vt * L, O + Vt * L])
        n += pancakes_plane(O + U.cross(Vt).normalized() * 0.0, U, Vt, RY1 - RY0, L - 0.05, edges=("v0", "u0", "u1"), keep=not_in)
    # nokpannenkoeken: plat gevouwen over de nok
    y = RY0 - 0.02
    while y < RY1:
        c = Vector((XR, y, RIDGE + 0.02))
        if not_in(c):
            Vt = Vector((0, 1, 0)); Uh = Vector((1, 0, 0))
            def fold(p, nrm, c=c):
                dx = p.x - c.x; return Vector((p.x, p.y, p.z - abs(dx) * SLOPE)), (Vector((-SLOPE if dx > 0 else SLOPE, 0, 1))).normalized() if abs(dx) > 1e-4 else nrm
            pancake(c, Uh, Vt, Vector((0, 0, 1)), 0.2, rnd.randrange(4), fold); n += 1
        y += 0.26
    # erkerdak (trapezium: voet x -2.64..-0.17 op y -2.42 z 1.25, boven x -2.42..-0.45 op y -1.3 z 2.45)
    O = Vector((-2.64, -2.42, 1.25)); U = Vector((1, 0, 0)); top = Vector((-2.64, -1.3, 2.45)); Vt = (top - O).normalized(); Lb = (top - O).length
    slab(db, [Vector((-2.64, -2.42, 1.25)), Vector((-0.17, -2.42, 1.25)), Vector((-0.45, -1.15, 2.6)), Vector((-2.42, -1.15, 2.6))])
    def bay_keep(c, uu, vv): t = vv / Lb; return -0.05 + 0.22 * t < uu < 2.47 - 0.28 * t
    n += pancakes_plane(O, U, Vt, 2.47, Lb, edges=("v0",), keep=bay_keep, r=0.17)
    # kooidak: voorschild (kijkt -y), zij (kijkt +x) en achter; nok langs x op z 2.72, y 1.1
    kz0, kz1, kx0, kx1, ky0, ky1, kr = 1.75, 2.72, 1.05, 3.62, -0.28, 2.42, 2.95
    pts_f = [Vector((kx0, ky0, kz0)), Vector((kx1, ky0, kz0)), Vector((kr, 1.07, kz1)), Vector((kx0, 1.07, kz1))]
    pts_s = [Vector((kx1, ky0, kz0)), Vector((kx1, ky1, kz0)), Vector((kr, 1.07, kz1))]
    pts_b = [Vector((kx1, ky1, kz0)), Vector((kx0, ky1, kz0)), Vector((kx0, 1.07, kz1)), Vector((kr, 1.07, kz1))]
    for pts in (pts_f, pts_s, pts_b): slab(db, pts)
    O = pts_f[0]; U = Vector((1, 0, 0)); Vt = (pts_f[3] - O).normalized(); Lf = (pts_f[3] - O).length
    n += pancakes_plane(O, U, Vt, kx1 - kx0, Lf, edges=("v0",), keep=lambda c, uu, vv: uu < (kx1 - kx0) - (kx1 - kr) * vv / Lf + 0.05, r=0.16)
    O = pts_s[0]; U = Vector((0, 1, 0)); apex = pts_s[2]; mid = (pts_s[0] + pts_s[1]) / 2; Vt = (apex - mid).normalized(); Ls = (apex - mid).length
    Vt = (Vt - U * Vt.dot(U)).normalized()
    n += pancakes_plane(O, U, Vt, ky1 - ky0, Ls, edges=("v0",), keep=lambda c, uu, vv: abs(uu - (1.07 - ky0)) < (1 - vv / Ls) * (ky1 - ky0) / 2 + 0.05, r=0.16)
    O = pts_b[0]; U = Vector((-1, 0, 0)); Vt = (pts_b[2] - O); Vt = (Vt - U * Vt.dot(U)).normalized(); Lb2 = (Vector((kx1, 1.07, kz1)) - Vector((kx1, ky1, kz0))).length
    n += pancakes_plane(O, U, Vt, kx1 - kx0, Lb2, edges=("v0",), keep=lambda c, uu, vv: uu > (kx1 - kr) * vv / Lb2 - 0.05, r=0.16)
    # dakkapel: zadeldakje, nok langs x op z 3.92
    for sgn in (-1, 1):
        ye = -0.54 + sgn * 0.62
        O = Vector((0.0 if sgn < 0 else 1.62, ye, 3.33)); U = Vector((1 if sgn < 0 else -1, 0, 0))
        Vt = (Vector((O.x, -0.54, 3.92)) - O).normalized(); Ld = (Vector((O.x, -0.54, 3.92)) - O).length
        slab(db, [O, O + U * 1.62, O + U * 1.62 + Vt * Ld, O + Vt * Ld])
        n += pancakes_plane(O, U, Vt, 1.62, Ld, edges=("v0", "u1") if sgn < 0 else ("v0", "u0"), r=0.14, rowh=0.16, colw=0.23)
    # torenkegel (vanaf de kraag op 4.95 tot de punt 6.7)
    cx, cy, rb, zb, zt = TWR[0], TWR[1], 1.34, 4.92, 6.72
    cone = bmesh.new(); bmesh.ops.create_cone(cone, cap_ends=True, segments=32, radius1=rb, radius2=0.02, depth=zt - zb)
    bmesh.ops.translate(cone, vec=(cx, cy, (zb + zt) / 2), verts=cone.verts)
    me = bpy.data.meshes.new("_c"); cone.to_mesh(me); cone.free(); db.from_mesh(me); bpy.data.meshes.remove(me)
    Ls = math.hypot(rb, zt - zb); k = 0; s = -0.08
    while s < Ls - 0.2:
        rr = rb * (1 - s / Ls); cnt = max(5, int(math.tau * rr / 0.25)); off = (k % 2) * 0.5
        for i in range(cnt):
            a = math.tau * (i + off) / cnt + rnd.uniform(-0.04, 0.04)
            radial = Vector((math.cos(a), math.sin(a), 0)); Vt = (Vector((0, 0, zt - zb)) - radial * rb).normalized(); U = Vector((-math.sin(a), math.cos(a), 0))
            base = Vector((cx, cy, zb)) + radial * rb
            c = base + Vt * (s + 0.1)
            def cbend(p, nrm, base=base, Vt=Vt, U=U):
                d = p - base; v = d.dot(Vt)
                if v >= 0: return p, nrm
                Nn = U.cross(Vt).normalized(); th = min(-v / 0.07, 1.6)
                return base + U * d.dot(U) - Vt * 0.07 * math.sin(th) - Nn * 0.07 * (1 - math.cos(th)) + Nn * d.dot(Nn), (Nn * math.cos(th) - Vt * math.sin(th)).normalized()
            pancake(c, U, Vt, U.cross(Vt).normalized(), 0.15 * (rr / rb) ** 0.35, rnd.randrange(4), cbend); n += 1
        s += 0.18; k += 1
    obj_from_bm("HG_dakbasis__dakbasis", db, "dakbasis")
    return n


# ------------------------------------------------------------------ snoep op de muren
def tile_uv(k, uu, vv):   # uu, vv in 0..1 binnen tegel k (4x4)
    return ((k % 4) * 0.25 + 0.01 + uu * 0.23, 1 - ((k // 4) * 0.25 + 0.01 + (1 - vv) * 0.23))


def add_shape(outline, depth, k, M, dome=0.4, uvk=None):
    """Plat snoepje: omtrek (lokaal xy, ~ -1..1) geextrudeerd (dikte depth), bovenkant iets bol; M = wereldmatrix (z = muurnormaal)."""
    n = len(outline); cz = SN.verts.new(M @ Vector((0, 0, depth * (1 + dome))))
    top = [SN.verts.new(M @ Vector((x, y, depth))) for x, y in outline]; bot = [SN.verts.new(M @ Vector((x * 1.02, y * 1.02, -depth * 0.6))) for x, y in outline]
    xs = [p[0] for p in outline]; ys = [p[1] for p in outline]; w = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    m = lambda x, y: tile_uv(k, 0.5 + x / w * 0.9, 0.5 + y / w * 0.9)
    for i in range(n):
        j = (i + 1) % n; f = SN.faces.new((cz, top[i], top[j]))
        for l, (x, y) in zip(f.loops, ((0, 0), outline[i], outline[j])): l[SN_UV].uv = m(x, y)
        f = SN.faces.new((top[j], top[i], bot[i], bot[j]))
        for l, (x, y) in zip(f.loops, (outline[j], outline[i], outline[i], outline[j])): l[SN_UV].uv = m(x * 1.05, y * 1.05)


def frame_at(p, nrm, rot=0.0):
    z = nrm.normalized(); up = Vector((0, 0, 1)) if abs(z.z) < 0.9 else Vector((0, 1, 0))
    x = up.cross(z).normalized(); y = z.cross(x)
    R = Matrix(((x.x, y.x, z.x, 0), (x.y, y.y, z.y, 0), (x.z, y.z, z.z, 0), (0, 0, 0, 1)))
    return Matrix.Translation(p) @ R @ Matrix.Rotation(rot, 4, "Z")


def ellipse(rx, ry, n=10, wob=0.0):
    return [(rx * math.cos(math.tau * i / n) * (1 + wob * math.sin(3 * i + 1)), ry * math.sin(math.tau * i / n) * (1 + wob * math.cos(2 * i))) for i in range(n)]


def heart(s):
    pts = []
    for i in range(16):
        t = math.tau * i / 16
        x = 16 * math.sin(t) ** 3; y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x / 17 * s, y / 17 * s))
    return pts[::-1] if sum(pts[i][0] * pts[(i + 1) % 16][1] - pts[(i + 1) % 16][0] * pts[i][1] for i in range(16)) < 0 else pts


def deco(kind, p, nrm, s=1.0, rot=None):
    rot = rnd.uniform(-0.5, 0.5) if rot is None else rot
    if kind == "hart":
        add_shape(heart(0.17 * s), 0.04, 0, frame_at(p, nrm, rnd.uniform(-0.12, 0.12)), dome=0.5)
    elif kind == "koek":
        add_shape(ellipse(0.2 * s, 0.135 * s, 12, 0.08), 0.045, rnd.choice((1, 1, 2)), frame_at(p, nrm, rot), dome=0.7)
    elif kind == "krakeling":
        M = frame_at(p, nrm, rot); r = 0.078 * s; n = 10
        for cx in (-0.45, 0.45):   # twee lussen + onderboog = krakeling
            ring = [(cx * r + r * 0.55 * math.cos(math.tau * i / n), r * 0.15 + r * 0.6 * math.sin(math.tau * i / n)) for i in range(n)]
            inner = [(cx * r + r * 0.28 * math.cos(math.tau * i / n), r * 0.15 + r * 0.32 * math.sin(math.tau * i / n)) for i in range(n)]
            o = [SN.verts.new(M @ Vector((x, y, 0.022))) for x, y in ring]; ii = [SN.verts.new(M @ Vector((x, y, 0.022))) for x, y in inner]
            ob_ = [SN.verts.new(M @ Vector((x, y, -0.01))) for x, y in ring]
            for i in range(n):
                j = (i + 1) % n
                for q in ((ii[i], o[i], o[j], ii[j]), (o[j], o[i], ob_[i], ob_[j])):
                    f = SN.faces.new(q)
                    for l in f.loops: l[SN_UV].uv = tile_uv(3, 0.3 + rnd.random() * 0.4, 0.3 + rnd.random() * 0.4)
    elif kind == "snoep":
        add_shape(ellipse(0.04 * s, 0.04 * s, 8), 0.018, rnd.randrange(4, 12), frame_at(p, nrm, rot), dome=0.6)
    elif kind == "mozaiek":
        add_shape(ellipse(0.095 * s, 0.085 * s, 8, 0.05), 0.026, rnd.randrange(4, 12), frame_at(p, nrm, rot), dome=0.5)
    elif kind == "oranje":
        add_shape(ellipse(0.05 * s, 0.035 * s, 8), 0.02, 14, frame_at(p, nrm, rot), dome=0.5)


def decorate(walls_ob):
    dg = bpy.context.evaluated_depsgraph_get(); bvh = BVHTree.FromObject(walls_ob, dg)
    placed = []
    def free(p, d):
        return all((p - q).length > d for q in placed)
    def put(kind, p, nrm, s=1.0, minsep=0.0, rot=None):
        if minsep and not free(p, minsep): return False
        deco(kind, p - nrm * 0.012, nrm, s, rot); placed.append(p.copy()); return True
    def hit_ray(o, d):
        h = bvh.ray_cast(o, d, 30)
        return (h[0], h[1]) if h[0] is not None else (None, None)
    def photo(kind, px, py, s=1.0, rot=None):
        p, n = hit_ray(CAM, ray900(px, py))
        if p is not None and n.y < -0.3: put(kind, p, n, s, rot=rot)
    # ---- voorgevel uit front.jpg (900 px)
    for px, py in ((370, 200), (410, 203), (400, 370), (440, 338), (485, 338), (527, 355), (558, 383)): photo("hart", px, py, 1.0)
    for px, py, s in ((283, 348, 1.15), (322, 376, 1.0), (262, 392, 1.15), (228, 424, 0.9), (254, 459, 0.95), (299, 467, 0.8), (339, 462, 0.75),
                      (405, 435, 0.85), (402, 466, 0.85), (418, 405, 0.9), (447, 380, 0.85), (478, 381, 0.85), (510, 393, 0.9), (536, 424, 0.9),
                      (543, 462, 0.9), (521, 498, 0.85), (360, 412, 0.7), (196, 470, 0.7)):
        photo("koek", px, py, s, rot=rnd.uniform(-0.3, 0.3))
    for py in (425, 458, 491): photo("krakeling", 149, py, 1.1, rot=0)
    for py in (385, 415, 445, 476): photo("krakeling", 641, py, 1.1, rot=0)
    for px, py in ((366, 92), (390, 97)): photo("krakeling", px, py, 1.3, rot=0)
    for px, py in ((210, 300), (186, 330), (276, 275), (306, 230), (450, 290), (470, 300), (520, 300), (566, 330), (596, 365)): photo("krakeling", px, py, 1.0)
    for px in (210, 252, 292, 336, 381, 430, 470): photo("koek", px, 826, 0.9, rot=0)          # rij koeken langs de voet van de erker
    # krakelingen langs de windveren (net onder de pannenkoekrand), voor en achter
    for yy, sgn in ((YF - 0.2, 1), (YB + 0.2, -1)):
        for side in (-1, 1):
            for i in range(1, 10):
                x = XR + side * (i * 0.3); z = roof_z(x) - 0.42
                if z < EAVE - 0.1: break
                p, n = hit_ray(Vector((x, yy - sgn * 1.0, z)), Vector((0, sgn, 0)))
                if p is not None: put("krakeling", p, n, 1.0, 0.1, rot=0)
    # ---- verspreid snoep (zij- en achtergevels, toren, kooi, stapel, trap)
    def scatter(n, src, kinds, sep):
        for _ in range(n * 6):
            if n <= 0: break
            o, d = src()
            p, nn = hit_ray(o, d)
            if p is None or p.z < 0.08: continue
            if roof_z(p.x) - 0.25 < p.z < roof_z(p.x) + 0.05 and X0 - 0.4 < p.x < X1 + 0.4 and RY0 < p.y < RY1 and p.z > EAVE - 0.3: continue
            if put(rnd.choice(kinds), p, nn, rnd.uniform(0.85, 1.15), sep): n -= 1
    K = ["snoep"] * 6 + ["krakeling", "koek"]
    scatter(150, lambda: (CAM + Vector((rnd.uniform(-0.2, 0.2), 0, rnd.uniform(-0.2, 0.2))), ray900(rnd.uniform(140, 650), rnd.uniform(150, 830))), ["snoep"], 0.11)
    scatter(45, lambda: (Vector((5, rnd.uniform(-1.3, 0.0), rnd.uniform(0.2, 2.5))), Vector((-1, 0, 0))), K, 0.16)          # zuidgevel
    scatter(60, lambda: (Vector((-6, rnd.uniform(-1.2, 2.6), rnd.uniform(0.2, 2.4))), Vector((1, 0, 0))), K, 0.17)          # noordgevel
    scatter(40, lambda: (Vector((rnd.uniform(-3.0, 1.2), 6, rnd.uniform(0.2, 4.5))), Vector((0, -1, 0))), ["koek", "snoep", "krakeling"], 0.2)   # achtergevel
    def tower_src():
        a = rnd.uniform(-2.6, 1.4); z = rnd.uniform(0.3, 4.3); d = Vector((math.cos(a), math.sin(a), 0))
        return Vector((TWR[0], TWR[1], z)) + d * 3, -d
    scatter(55, tower_src, ["koek", "snoep", "snoep", "krakeling"], 0.22)
    scatter(45, lambda: (Vector((rnd.uniform(1.3, 3.35), -3, rnd.uniform(0.15, 1.7))), Vector((0, 1, 0))), ["snoep", "snoep", "krakeling"], 0.13)   # kooi voor
    scatter(25, lambda: (Vector((6, rnd.uniform(0.0, 2.2), rnd.uniform(0.15, 1.7))), Vector((-1, 0, 0))), ["snoep", "krakeling"], 0.15)         # kooi zij
    for i in range(9):   # rij krakelingen onder de dakrand van de kooi (HG2016)
        p, n = hit_ray(Vector((1.55 + i * 0.22, -3, 1.6)), Vector((0, 1, 0)))
        if p is not None: put("krakeling", p, n, 1.0, 0.08, rot=0)
    # bonte schoorsteen: dicht mozaiek
    for k in range(25):
        z = 0.2 + k * 0.17
        for i in range(13):
            a = math.tau * (i + (k % 2) * 0.5) / 13; d = Vector((math.cos(a), math.sin(a), 0))
            p, n = hit_ray(Vector((-3.45, -1.0, z)) + d * 1.5, -d)
            if p is not None and (p - Vector((-3.45, -1.0, z))).length < 0.6: deco("mozaiek", p - n * 0.01, n, rnd.uniform(0.9, 1.15))
    return len(placed)


# ------------------------------------------------------------------ deur, luiken, ramen, steunbalken, lampen
def wood_panel(x0, x1, z0, z1, y, thick=0.05, arch=False, k=13, nseg=8):
    w = (x1 - x0) / 2; cx = (x0 + x1) / 2; pts = [(x0, z0), (x1, z0)]
    if arch:
        pts.append((x1, z1 - w))
        for i in range(1, nseg): a = math.pi * i / nseg; pts.append((cx + w * math.cos(a), z1 - w + w * math.sin(a)))
        pts.append((x0, z1 - w))
    else: pts += [(x1, z1), (x0, z1)]
    a = [SN.verts.new((x, y, z)) for x, z in pts]; b = [SN.verts.new((x, y + thick, z)) for x, z in pts]; n = len(pts)
    m = lambda x, z: tile_uv(k, (x - x0) / (x1 - x0 + 1e-6), (z - z0) / (z1 - z0 + 1e-6))
    f = SN.faces.new(a[::-1])
    for l, v in zip(f.loops, a[::-1]): l[SN_UV].uv = m(v.co.x, v.co.z)
    f = SN.faces.new(b)
    for l, v in zip(f.loops, b): l[SN_UV].uv = m(v.co.x, v.co.z)
    for i in range(n):
        j = (i + 1) % n; f = SN.faces.new((a[i], a[j], b[j], b[i]))
        for l in f.loops: l[SN_UV].uv = tile_uv(k, 0.05, 0.5)


def box_uv(x0, x1, y0, y1, z0, z1, k):
    bm = bmesh.new(); cube(bm, x0, x1, y0, y1, z0, z1)
    me = bpy.data.meshes.new("_b"); bm.to_mesh(me); bm.free(); add_mesh_uv(me, k); bpy.data.meshes.remove(me)


def add_mesh_uv(me, k, M=Matrix()):
    off = len(SN.verts); vs = [SN.verts.new(M @ v.co) for v in me.vertices]
    for p in me.polygons:
        try: f = SN.faces.new([vs[i] for i in p.vertices])
        except ValueError: continue
        for l in f.loops: l[SN_UV].uv = tile_uv(k, 0.2 + rnd.random() * 0.6, 0.2 + rnd.random() * 0.6)


def details(det):
    """det = bmesh voor MAT-onderdelen (ijzer, glas, lood, donker, vuur): lijst (mat, bm)."""
    # voordeur in de nis + luikje met vuurgloed (heks) + ring
    wood_panel(DOOR[0] + 0.01, DOOR[1] - 0.01, DOOR[2], DOOR[3] - 0.01, YF + 0.06, 0.05, arch=True)
    hx, hz = at_plane(455, 462, YF)
    cube(det["vuur"], hx - 0.08, hx + 0.08, YF + 0.03, YF + 0.06, hz - 0.08, hz + 0.08)
    for (a0, a1, b0, b1) in ((hx - 0.1, hx + 0.1, hz + 0.08, hz + 0.1), (hx - 0.1, hx + 0.1, hz - 0.1, hz - 0.08), (hx - 0.1, hx - 0.08, hz - 0.1, hz + 0.1), (hx + 0.08, hx + 0.1, hz - 0.1, hz + 0.1)):
        box_uv(a0, a1, YF + 0.02, YF + 0.05, b0, b1, 12)
    rx, rz = at_plane(458, 520, YF)
    t = bmesh.new(); bmesh.ops.create_circle(t, segments=10, radius=0.06); tor = bpy.data.meshes.new("_t")
    bm2 = bmesh.new(); r_ = 0.06
    for i in range(10):
        a = math.tau * i / 10; a2 = math.tau * (i + 1) / 10
        cube(bm2, rx + r_ * math.cos(a) - 0.012, rx + r_ * math.cos(a) + 0.012, YF + 0.0, YF + 0.03, rz + r_ * math.sin(a) - 0.012, rz + r_ * math.sin(a) + 0.012)
    det["ijzer"].from_mesh(_bm_to_me(bm2)); t.free(); bpy.data.meshes.remove(tor)
    # bovenraam: glas-in-lood (zeshoekjes) + open luik links, 3 cm voor de muur
    wx0, wz1 = at_plane(360, 232, YF); wx1, wz0 = at_plane(410, 305, YF)
    cube(det["glas"], wx0, wx1, YF + 0.05, YF + 0.07, wz0, wz1)
    lattice(det["lood"], wx0, wx1, wz0, wz1, YF + 0.03, 0.08)
    sx0, _ = at_plane(307, 232, YF); wood_panel(sx0, wx0 - 0.03, wz0 - 0.02, wz1 + 0.02, YF - 0.09, 0.04)
    # erkerraam: rooster met flessenglas + twee luiken
    bx0, bz1 = at_plane(262, 698, -2.15); bx1, bz0 = at_plane(372, 785, -2.15); bz0 = max(0.12, bz0)
    cube(det["glas"], bx0, bx1, -2.08, -2.06, bz0, bz1); lattice(det["lood"], bx0, bx1, bz0, bz1, -2.11, 0.09)
    lx0, _ = at_plane(190, 700, -2.15); lx1, _ = at_plane(258, 700, -2.15); wood_panel(lx0, lx1, bz0 - 0.02, bz1 + 0.04, -2.3, 0.04)
    rx0, _ = at_plane(381, 700, -2.15); rx1, _ = at_plane(445, 700, -2.15); wood_panel(rx0, rx1, bz0 - 0.02, bz1 + 0.04, -2.3, 0.04)
    # katgat: donkere binnenkant
    cx_, cz_ = at_plane(315, 430, YF); cube(det["donker"], cx_ - 0.25, cx_ + 0.25, YF + 0.35, YF + 0.4, cz_ - 0.2, cz_ + 0.2)
    # kooi: donkere binnenruimte + tralies (6) + lijst
    cube(det["donker"], 1.82, 2.88, 0.55, 0.6, 0.45, 1.42)
    for i in range(6):
        x = 1.92 + i * 0.17; cube(det["ijzer"], x - 0.018, x + 0.018, -0.05, -0.01, 0.5, 1.38)
    cube(det["ijzer"], 1.85, 2.85, -0.06, 0.0, 1.33, 1.37); cube(det["ijzer"], 1.85, 2.85, -0.06, 0.0, 0.52, 0.56)
    # dakkapelraam en torenraam: glas-in-lood
    cube(det["glas"], 1.36, 1.38, -0.72, -0.34, 2.62, 3.12)
    a = math.radians(-35); tx, ty = TWR[0] + math.cos(a) * 0.93, TWR[1] + math.sin(a) * 0.93
    tb = bmesh.new(); cube(tb, -0.16, 0.16, -0.01, 0.01, 3.45, 3.95); bmesh.ops.transform(tb, matrix=Matrix.Translation((tx, ty, 0)) @ Matrix.Rotation(a + math.pi / 2, 4, "Z"), verts=tb.verts)
    det["glas"].from_mesh(_bm_to_me(tb))
    # achter: technische deur (hout) + glas-in-lood raampjes; noordraam met luik
    wood_panel(-2.28, -1.62, 0.0, 1.58, YB - 0.14, 0.05, k=13)
    for xw in (-0.6, 0.2): cube(det["glas"], xw - 0.18, xw + 0.18, YB - 0.16, YB - 0.14, 1.5, 2.0)
    nb = bmesh.new(); cube(nb, X0 + 0.05, X0 + 0.07, -0.6, 0.0, 1.35, 2.0); det["glas"].from_mesh(_bm_to_me(nb))
    # steunbalken met gezichtjes (zuidgevel onder het overstek): gebogen teal balk met oranje bies + gezichtsknop
    for yb in (-1.02, -0.58, -0.14):
        pts = []
        for i in range(9):
            a = math.pi / 2 * i / 8; pts.append((X1 + 0.03 + 0.42 * (1 - math.cos(a)), 1.02 + 0.72 * math.sin(a)))
        for i in range(8):
            (xa, za), (xb, zb) = pts[i], pts[i + 1]
            seg = bmesh.new(); cube(seg, -0.05, 0.05, -0.055, 0.055, 0, 1)
            L = math.hypot(xb - xa, zb - za); ang = math.atan2(xb - xa, zb - za)
            M = Matrix.Translation((xa, yb, za)) @ Matrix.Rotation(ang, 4, "Y") @ Matrix.Scale(L + 0.03, 4, Vector((0, 0, 1)))
            me = _bm_to_me(seg); add_mesh_uv(me, 12 if i % 2 == 0 else 12, M); bpy.data.meshes.remove(me)
        knop = bmesh.new(); bmesh.ops.create_uvsphere(knop, u_segments=8, v_segments=6, radius=0.09)
        bmesh.ops.scale(knop, vec=(0.8, 1.0, 1.15), verts=knop.verts); me = _bm_to_me(knop)
        add_mesh_uv(me, 2, Matrix.Translation((X1 + 0.1, yb, 1.06))); bpy.data.meshes.remove(me)
    box_uv(X1 + 0.22, X1 + 0.32, -1.25, 0.06, 1.68, 1.8, 12)                          # balk onder het overstek
    for i in range(12):
        p = Vector((X1 + 0.325, -1.18 + i * 0.105, 1.74)); deco("krakeling", p, Vector((1, 0, 0)), 0.75, 0)
    # taartlampen: lantaarn (glas) met roze taartkap op een arm
    lamps = []
    for (p, nrm, col) in ((Vector((X0 - 0.1, -0.45, 2.0)), Vector((-1, 0, 0)), 7), (Vector((X0 - 0.1, 1.9, 1.9)), Vector((-1, 0, 0)), 8)):
        base = p + nrm * 0.28
        cube(det["ijzer"], min(p.x, base.x) - 0.02, max(p.x, base.x) + 0.02, p.y - 0.02, p.y + 0.02, p.z - 0.25, p.z - 0.21)
        cyl = bmesh.new(); bmesh.ops.create_cone(cyl, cap_ends=True, segments=8, radius1=0.08, radius2=0.12, depth=0.26)
        bmesh.ops.translate(cyl, vec=base + Vector((0, 0, -0.1)), verts=cyl.verts); det["glas"].from_mesh(_bm_to_me(cyl))
        dome = bmesh.new(); bmesh.ops.create_uvsphere(dome, u_segments=10, v_segments=6, radius=0.15)
        bmesh.ops.delete(dome, geom=[v for v in dome.verts if v.co.z < -0.01], context="VERTS"); bmesh.ops.scale(dome, vec=(1, 1, 1.3), verts=dome.verts)
        me = _bm_to_me(dome); add_mesh_uv(me, col, Matrix.Translation(base + Vector((0, 0, 0.03)))); bpy.data.meshes.remove(me)
        for i in range(6):
            a = math.tau * i / 6; deco("snoep", base + Vector((math.cos(a) * 0.12, math.sin(a) * 0.12, 0.12)), Vector((math.cos(a), math.sin(a), 0.6)), 0.9)
        lamps.append([round(base.x, 3), round(base.y, 3), round(base.z - 0.1, 3)])
    return lamps


def lattice(bm, x0, x1, z0, z1, y, step):
    nx = max(2, int((x1 - x0) / step)); nz = max(2, int((z1 - z0) / step))
    for i in range(nx + 1):
        x = x0 + (x1 - x0) * i / nx; cube(bm, x - 0.008, x + 0.008, y, y + 0.02, z0, z1)
    for k in range(nz + 1):
        z = z0 + (z1 - z0) * k / nz; cube(bm, x0, x1, y, y + 0.02, z - 0.008, z + 0.008)
    cube(bm, x0 - 0.03, x0, y - 0.01, y + 0.04, z0, z1); cube(bm, x1, x1 + 0.03, y - 0.01, y + 0.04, z0, z1)
    cube(bm, x0 - 0.03, x1 + 0.03, y - 0.01, y + 0.04, z0 - 0.03, z0); cube(bm, x0 - 0.03, x1 + 0.03, y - 0.01, y + 0.04, z1, z1 + 0.03)


def _bm_to_me(bm):
    me = bpy.data.meshes.new("_tmp"); bm.to_mesh(me); bm.free(); return me


def atlas_material(name, png):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = m.node_tree; nt.nodes.clear(); out = nt.nodes.new("ShaderNodeOutputMaterial"); b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    im = nt.nodes.new("ShaderNodeTexImage"); im.image = bpy.data.images.load(png, check_existing=True)
    nt.links.new(im.outputs[0], b.inputs["Base Color"]); nt.links.new(b.outputs[0], out.inputs[0]); b.inputs["Roughness"].default_value = 0.7
    m.diffuse_color = (0.8, 0.6, 0.4, 1); return m


def build(master):
    open_master(master); clear_owned()
    for c in ("LOW",):
        lc = bpy.context.view_layer.layer_collection.children.get(c)
        if lc: lc.exclude = True
    for n, (c, r) in COLS.items(): material("MAT_" + n, tuple((v / 255) ** 2.2 for v in c) + (1,), r)
    for n in COLS: bpy.data.materials["MAT_" + n].diffuse_color = tuple((v / 255) ** 2.2 for v in COLS[n][0]) + (1,)
    w = walls(); log("muren tris", sum(len(p.vertices) - 2 for p in w.data.polygons))
    npk = roofs(); log("pannenkoeken", npk)
    nd = decorate(w); log("snoep", nd)
    det = {k: bmesh.new() for k in ("ijzer", "glas", "lood", "donker", "vuur")}
    lamps = details(det)
    for k, bm in det.items():
        if len(bm.faces): obj_from_bm("HG_%s__%s" % (k, k), bm, k)
        else: bm.free()
    me = bpy.data.meshes.new("BAKE_pannenkoek"); PK.to_mesh(me); ob = bpy.data.objects.new("BAKE_pannenkoek", me); col("FORMS").objects.link(ob); own(ob)
    ob.data.materials.append(atlas_material("MAT_pannenkoek", os.path.join(HERE, "textures", "HG_pannenkoek_kleur.png")))
    me = bpy.data.meshes.new("BAKE_snoep"); SN.to_mesh(me); ob2 = bpy.data.objects.new("BAKE_snoep", me); col("FORMS").objects.link(ob2); own(ob2)
    ob2.data.materials.append(atlas_material("MAT_snoep", os.path.join(HERE, "textures", "HG_snoep_kleur.png")))
    import json
    json.dump({"colliders": [[-0.95, 0.72, 1.3, 4.5, 4.2, 2.6, 0], [2.3, 1.1, 0.9, 2.2, 2.3, 1.8, 0], [0.7, 2.2, 2.3, 2.0, 2.0, 4.6, 0], [0.05, -1.8, 0.7, 1.4, 1.4, 1.4, 0], [-1.5, -1.65, 0.5, 2.2, 1.0, 1.0, 0]],
               "lamps": lamps}, open(os.path.join(HERE, "exports", "huis_extra.json"), "w"))
    tris = lambda o: sum(len(p.vertices) - 2 for p in o.data.polygons)
    log("tris pannenkoek", tris(ob), "snoep", tris(ob2))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
