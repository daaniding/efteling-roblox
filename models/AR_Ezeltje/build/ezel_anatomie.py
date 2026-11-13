# ================= EZEL v2: anatomisch (Ezelclose, Ezel5, Ezeltje_nu, Peterendeezel = echte ezel) =================
# Wordt door 03_ezel.py ge-exec'd (gebruikt ell, tube, put, col, Z, Vector, math, bmesh, bpy, Euler). Kijkt naar -Y.
# Romp = doorsneden langs de rug (breedte, bovenkant, onderkant), hals/kop als lofts langs hun as, benen met gewrichten,
# alles samen voxel-remesh 7 mm -> licht smoothen -> decimate. Oren, ogen, manen, tuig en dekje los.

def loft_as(pts, secs, n=28, cap0=True, cap1=True, sq=2.4, up=Vector((0, 0, 1))):
    """lofts langs een as: pts = middelpunten, secs = (halve breedte x, halve diepte in het as-vlak); superellips (sq) per ring"""
    bm = bmesh.new(); P = [Vector(p) for p in pts]; rings = []
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        ax = Vector((1, 0, 0)); d = t.cross(ax).normalized()                          # d = 'diepte'-richting loodrecht op as en x
        w, h = secs[i]; ring = []
        for k in range(n):
            a = k * math.tau / n; c, s = math.cos(a), math.sin(a)
            cx = math.copysign(abs(c) ** (2 / sq), c); sy = math.copysign(abs(s) ** (2 / sq), s)
            ring.append(bm.verts.new(p + ax * (w * cx) + d * (h * sy)))
        rings.append(ring)
    for A, B in zip(rings, rings[1:]):
        for k in range(n): bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    if cap0: bm.faces.new(rings[0][::-1])
    if cap1: bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


# romp: (y, halve breedte, bovenkant, onderkant) — rug iets ingezakt, buik laag, schoft hoog en smal, kruis rond
ROMP = [(0.72, 0.08, 1.00, 0.84), (0.67, 0.17, 1.05, 0.72), (0.58, 0.225, 1.08, 0.65), (0.45, 0.245, 1.08, 0.60), (0.28, 0.26, 1.04, 0.55),
        (0.08, 0.27, 1.01, 0.52), (-0.12, 0.27, 1.01, 0.52), (-0.28, 0.255, 1.05, 0.55), (-0.40, 0.225, 1.09, 0.58), (-0.50, 0.19, 1.06, 0.63),
        (-0.58, 0.14, 1.01, 0.69), (-0.63, 0.07, 0.95, 0.77)]
def romp_sectie(y):
    for a, b in zip(ROMP, ROMP[1:]):
        if b[0] <= y <= a[0]:
            t = (a[0] - y) / (a[0] - b[0]); return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, 4))
    return ROMP[0][1:] if y > ROMP[0][0] else ROMP[-1][1:]
lijf = bmesh.new()
def voeg(bm):
    me_ = bpy.data.meshes.new("_t"); bm.to_mesh(me_); bm.free(); lijf.from_mesh(me_); bpy.data.meshes.remove(me_)
voeg(loft_as([(0, y, Z + (zt + zb) / 2) for y, w, zt, zb in ROMP], [(w, (zt - zb) / 2) for y, w, zt, zb in ROMP], 32, sq=2.05))
# hals: dik aan de borst, omlaag naar voren, smal en hoog (ezelhals)
HALS = [((0, -0.40, Z + 0.9), (0.18, 0.21)), ((0, -0.55, Z + 0.88), (0.155, 0.2)), ((0, -0.7, Z + 0.83), (0.125, 0.175)),
        ((0, -0.84, Z + 0.77), (0.105, 0.15)), ((0, -0.95, Z + 0.71), (0.09, 0.13)), ((0, -1.02, Z + 0.66), (0.085, 0.12))]
voeg(loft_as([p for p, s in HALS], [s for p, s in HALS], 28, sq=2.2))
# kop: lang, schedel breed bij de ogen, smalle neusrug, ronde snuit; as van de achterhoofdsknobbel schuin omlaag naar de snuit
KOP_A, KOP_B = Vector((0, -0.99, Z + 0.72)), Vector((0, -1.29, Z + 0.34))
KS = [(0.0, 0.075, 0.07), (0.12, 0.098, 0.095), (0.25, 0.1, 0.1), (0.42, 0.083, 0.088), (0.6, 0.068, 0.078), (0.78, 0.066, 0.075),
      (0.9, 0.074, 0.08), (0.97, 0.068, 0.07), (1.0, 0.045, 0.04)]
kop_pts = [KOP_A.lerp(KOP_B, t) for t, w, h in KS]
kd = (KOP_B - KOP_A).normalized(); kn = kd.cross(Vector((1, 0, 0))).normalized()          # kn = naar de voorkant/boven van de kop
kop_pts = [p + kn * (0.012 * math.sin(t * math.pi)) for p, (t, w, h) in zip(kop_pts, KS)]  # licht gebogen neusrug
voeg(loft_as(kop_pts, [(w, h) for t, w, h in KS], 28, sq=2.1))
voeg(ell(tuple(KOP_A.lerp(KOP_B, 0.3) - kn * 0.07), (0.085, 0.09, 0.1), (-40, 0, 0)))                  # kaken (ganache)
# onderkaak: mond iets open (Ezelclose): van de kaakhoek naar de kin, 12 graden omlaag gedraaid t.o.v. de snuit
kin = KOP_A.lerp(KOP_B, 0.97) - kn * 0.075 + Vector((0, 0.0, -0.035))
voeg(loft_as([KOP_A.lerp(KOP_B, 0.45) - kn * 0.075, KOP_A.lerp(KOP_B, 0.75) - kn * 0.085, kin], [(0.05, 0.035), (0.045, 0.03), (0.04, 0.026)], 20, sq=2.0))
# schouders en dijen (spierpartijen), voorbenen naar voren, achterbenen naar achter gestrekt
for sx in (-1, 1):
    voeg(ell((sx * 0.16, -0.41, Z + 0.83), (0.08, 0.14, 0.22), (18, 0, 0)))                     # schouderblad
    voeg(ell((sx * 0.12, -0.47, Z + 0.67), (0.07, 0.09, 0.1)))                                    # bovenarm / elleboog
    voeg(loft_as([(sx * 0.135, -0.48, Z + 0.62), (sx * 0.135, -0.58, Z + 0.47), (sx * 0.133, -0.68, Z + 0.37), (sx * 0.133, -0.71, Z + 0.33),
                  (sx * 0.132, -0.79, Z + 0.2), (sx * 0.132, -0.84, Z + 0.11), (sx * 0.132, -0.86, Z + 0.07)],
                 [(0.075, 0.085), (0.056, 0.06), (0.046, 0.052), (0.048, 0.052), (0.036, 0.04), (0.043, 0.047), (0.036, 0.04)], 18, sq=2.0))
    voeg(ell((sx * 0.14, 0.47, Z + 0.78), (0.115, 0.23, 0.29), (-20, 0, 0)))                     # dij / bil, loopt laag door naar de knie
    voeg(loft_as([(sx * 0.135, 0.52, Z + 0.62), (sx * 0.14, 0.68, Z + 0.46), (sx * 0.135, 0.82, Z + 0.37), (sx * 0.135, 0.85, Z + 0.33),
                  (sx * 0.133, 0.94, Z + 0.2), (sx * 0.132, 0.99, Z + 0.11), (sx * 0.132, 1.01, Z + 0.07)],
                 [(0.085, 0.1), (0.06, 0.07), (0.047, 0.056), (0.046, 0.05), (0.036, 0.04), (0.043, 0.047), (0.036, 0.04)], 18, sq=2.0))
voeg(loft_as([(0, 0.64, Z + 0.98), (0, 0.78, Z + 0.97), (0, 0.95, Z + 0.93), (0, 1.08, Z + 0.88)], [(0.04, 0.045), (0.028, 0.03), (0.022, 0.024), (0.018, 0.02)], 12))   # staart
# ---- spieren en botpunten (anatomie-details, Ezelclose + echte ezel) ----
for sx in (-1, 1):
    voeg(ell((sx * 0.075, -0.62, Z + 0.84), (0.055, 0.2, 0.075), (-28, 0, 0)))      # halsspier (brachiocephalicus) langs de onderkant van de hals
    voeg(ell((sx * 0.06, -0.78, Z + 0.86), (0.03, 0.16, 0.04), (-30, 0, 0)))        # bovenrand hals
    voeg(ell((sx * 0.13, -0.45, Z + 0.71), (0.065, 0.1, 0.13), (10, 0, 0)))         # triceps
    voeg(ell((sx * 0.07, -0.58, Z + 0.72), (0.065, 0.06, 0.09)))                       # borstspier
    voeg(ell((sx * 0.138, -0.57, Z + 0.52), (0.05, 0.06, 0.1), (-28, 0, 0)))     # onderarmspier
    voeg(ell((sx * 0.134, -0.705, Z + 0.35), (0.05, 0.048, 0.05)))                   # voorknie (carpus)
    voeg(ell((sx * 0.133, -0.835, Z + 0.11), (0.046, 0.054, 0.044)))                 # kogel voor
    voeg(ell((sx * 0.16, 0.34, Z + 0.98), (0.04, 0.05, 0.04)))                      # heupknobbel
    voeg(ell((sx * 0.105, 0.64, Z + 0.8), (0.075, 0.085, 0.19), (-28, 0, 0)))       # hamstrings (achterkant dij)
    voeg(ell((sx * 0.14, 0.66, Z + 0.52), (0.05, 0.06, 0.1), (32, 0, 0)))       # schenkel (gaskin)
    voeg(ell((sx * 0.135, 0.865, Z + 0.36), (0.035, 0.05, 0.04)))                    # hakpunt
    voeg(ell((sx * 0.133, 0.985, Z + 0.11), (0.046, 0.054, 0.044)))                  # kogel achter
voeg(loft_as([(0, -0.44, Z + 1.07), (0, -0.2, Z + 1.03), (0, 0.1, Z + 1.0), (0, 0.4, Z + 1.07), (0, 0.6, Z + 1.06)], [(0.03, 0.025)] * 5, 10))   # ruggengraat
# kop: kaakspier, wenkbrauwboog, lippen, kin
for sx in (-1, 1):
    voeg(ell(tuple(KOP_A.lerp(KOP_B, 0.32) + Vector((sx * 0.075, 0, 0)) - kn * 0.045), (0.035, 0.075, 0.075), (-40, 0, 0)))
    voeg(ell(tuple(KOP_A.lerp(KOP_B, 0.2) + Vector((sx * 0.075, 0, 0)) + kn * 0.06), (0.028, 0.045, 0.02), (-40, 0, 0)))
voeg(ell(tuple(KOP_A.lerp(KOP_B, 0.95) - kn * 0.04), (0.075, 0.05, 0.035), (-40, 0, 0)))          # bovenlip
voeg(ell(tuple(kin + kn * 0.005), (0.05, 0.04, 0.03), (-30, 0, 0)))                                  # onderlip / kin
me = bpy.data.meshes.new("ezel"); lijf.to_mesh(me); lijf.free()
hi = bpy.data.objects.new("_ezel_hi", me); col.objects.link(hi)
bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = hi; hi.select_set(True)
rm = hi.modifiers.new("remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.0045
sm = hi.modifiers.new("smooth", "SMOOTH"); sm.factor = 0.5; sm.iterations = 5
for m_ in list(hi.modifiers): bpy.ops.object.modifier_apply(modifier=m_.name)
# laag: kopie, decimeren (game-mesh)
ez = hi.copy(); ez.data = hi.data.copy(); ez.name = "BAKE_ezel"; col.objects.link(ez)
bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = ez; ez.select_set(True)
dc = ez.modifiers.new("dec", "DECIMATE"); dc.ratio = 18000 / max(1, len(ez.data.polygons))
bpy.ops.object.modifier_apply(modifier="dec"); bpy.ops.object.shade_smooth()
# hoog: vachtstructuur (fijne gestrekte ruis) als verplaatsing -> wordt een normal map op het lage model
tx_ = bpy.data.textures.new("vacht", "STUCCI"); tx_.noise_scale = 0.012; tx_.turbulence = 3.0
tx2 = bpy.data.textures.new("vacht2", "CLOUDS"); tx2.noise_scale = 0.05
bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = hi; hi.select_set(True)
for t_, st in ((tx_, 0.0018), (tx2, 0.0025)):
    dm = hi.modifiers.new("d", "DISPLACE"); dm.texture = t_; dm.strength = st; dm.mid_level = 0.5; dm.texture_coords = "OBJECT"
for m_ in list(hi.modifiers): bpy.ops.object.modifier_apply(modifier=m_.name)
# hoeven (blauwgrijs, Ezelclose): afgeknotte kegel schuin naar voren
for sx in (-1, 1):
    for (y, dy) in ((-0.87, -0.03), (1.015, -0.02)):
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.05, radius2=0.038, depth=0.075)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Euler((math.radians(-22 if y < 0 else 18), 0, 0)).to_matrix())
        bmesh.ops.translate(bm, vec=(sx * 0.132, y + dy, Z + 0.037), verts=bm.verts); put("hoef", bm)
# ogen: oogbol wit, donkere iris/pupil, oogleden als ring, iets uitpuilend (Ezelclose)
for sx in (-1, 1):
    ec = KOP_A.lerp(KOP_B, 0.24) + Vector((sx * 0.088, 0, 0)) + kn * 0.03
    put("oog", ell(tuple(ec), (0.03, 0.036, 0.034)))
    put("pupil", ell(tuple(ec + Vector((sx * 0.017, 0, 0)) - kd * 0.003), (0.018, 0.023, 0.021)))
    rp_ = [ec + Vector((sx * 0.008, 0, 0)) + (kd * math.cos(a) + kn * math.sin(a)) * 0.035 for a in [i * math.tau / 24 for i in range(25)]]
    put("ezelhuid", tube(rp_, 0.009, 6, cap=False))                                              # oogleden
    put("ezelhuid", tube([ec + Vector((sx * 0.01, 0, 0)) + (kd * math.cos(a) + kn * math.sin(a)) * 0.042 for a in [math.radians(v) for v in range(-20, 200, 20)]], 0.012, 6))   # bovenooglid
    for k in range(7):                                                                           # wimpers
        a = math.radians(30 + k * 20); r0 = ec + Vector((sx * 0.012, 0, 0)) + (kd * math.cos(a) + kn * math.sin(a)) * 0.045
        put("pupil", tube([r0, r0 + (kd * math.cos(a) + kn * math.sin(a)) * 0.018 + Vector((sx * 0.01, 0, 0))], [0.0025, 0.0008], 4))
    # neusgaten + mondspleet
    nc = KOP_A.lerp(KOP_B, 0.93) + Vector((sx * 0.05, 0, 0)) + kn * 0.03
    put("neus", ell(tuple(nc), (0.012, 0.022, 0.03), (-40, 0, sx * 15)))
    put("ezelhuid", tube([nc + Vector((sx * 0.006, 0, 0)) + (kd * math.cos(a) * 0.026 + kn * math.sin(a) * 0.034) for a in [i * math.tau / 16 for i in range(17)]], 0.008, 6, cap=False))   # neusvleugel
put("neus", tube([KOP_A.lerp(KOP_B, 0.72) - kn * 0.06 + Vector((sx * 0.045, 0, 0)) for sx in (-1,)] + [KOP_B - kn * 0.055 + Vector((0, 0, -0.01))] +
                 [KOP_A.lerp(KOP_B, 0.72) - kn * 0.06 + Vector((0.045, 0, 0))], 0.01, 6))
# oren: lang, holle bladvorm (gebogen plaat, solidify), schuin omhoog en iets naar achter/opzij
for sx in (-1, 1):
    base = KOP_A + Vector((sx * 0.055, 0.02, 0.02)); up_ = Vector((sx * 0.35, 0.25, 1.0)).normalized(); side = Vector((1, 0, 0))
    fw = up_.cross(side).normalized()
    bm = bmesh.new(); R = []
    for j in range(13):
        t = j / 12; L_ = 0.35 * t; w = 0.05 * math.sin(math.pi * min(1, t * 1.15)) ** 0.8 + 0.006
        row = []
        for k in range(9):
            u = -1 + 2 * k / 8; cup = 0.025 * (1 - u * u) * (1 - t)
            row.append(bm.verts.new(base + up_ * L_ + Vector((sx * 0, 0, 0)) + fw.cross(up_).normalized() * (u * w) - fw * cup))
        R.append(row)
    for j in range(12):
        for k in range(8): bm.faces.new((R[j][k], R[j][k + 1], R[j + 1][k + 1], R[j + 1][k]))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.012); put("ezelhuid", bm)
    for k in range(6):                                                                           # haren in de oorschelp
        q = base + up_ * (0.04 + 0.03 * k) - fw * 0.01
        put("manen", tube([q, q + up_ * 0.05 - fw * 0.012 + Vector((sx * 0.005, 0, 0))], [0.004, 0.001], 4))
    put("oorbinnen", ell(tuple(base + up_ * 0.12 - fw * 0.012), (0.03, 0.03, 0.09), (math.degrees(math.atan2(up_.y, up_.z)) * -1, sx * -18, 0)))
# opstaande korte manen (Ezelclose: kam van plukjes van achterhoofd tot schoft)
for i in range(44):
    t = i / 43; p = Vector(KOP_A) + Vector((0, 0.02, 0.06)) + (Vector((0, -0.38, Z + 1.06)) - Vector(KOP_A) - Vector((0, 0.02, 0.06))) * t
    p = Vector((0, p.y, p.z if i else p.z)); h = 0.05 + 0.02 * math.sin(t * math.pi)
    for dx in (-0.012, 0.012):
        put("manen", tube([p + Vector((dx, 0, -0.01)), p + Vector((dx * 1.6, 0.012 * math.sin(i * 1.7), h * (0.85 + 0.3 * ((i * 7) % 5) / 4)))], [0.013, 0.003], 6))
for k in range(9):                                                                  # voorlok tussen de oren
    a = -0.6 + 1.2 * k / 8; b = KOP_A + Vector((0.02 * a, -0.01, 0.04))
    put("manen", tube([b, b + kd * 0.05 + Vector((0.03 * a, 0, 0.02)), b + kd * 0.11 + Vector((0.04 * a, 0, -0.01))], [0.009, 0.007, 0.002], 6))
# staartpluim
for k in range(22):
    a = k * math.tau / 22; b = Vector((0, 1.06, Z + 0.88))
    put("manen", tube([b, b + Vector((0.025 * math.cos(a), 0.06, -0.04 + 0.02 * math.sin(a))), b + Vector((0.035 * math.cos(a), 0.09, -0.16))], [0.014, 0.012, 0.004], 6))
# ---- tuig: banden die strak om de romp liggen (romp-doorsnede + 8 mm), gouden nagels
def romp_band(y, a0=-math.pi, a1=math.pi, n=36, r=0.012, studs=True, dz=0.0):
    w, zt, zb = romp_sectie(y); cz = Z + (zt + zb) / 2 + dz; hh = (zt - zb) / 2; pts = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n; c, s = math.cos(a), math.sin(a)
        cx = math.copysign(abs(c) ** (2 / 2.05), c); sy = math.copysign(abs(s) ** (2 / 2.05), s)
        pts.append(Vector(((w + 0.008) * cx, y, cz + (hh + 0.008) * sy)))
    put("tuig", tube(pts, r, 6, cap=False))
    if studs:
        for p in pts[::3]: put("goud", ell(tuple(p + (p - Vector((0, y, cz))).normalized() * 0.008), (0.013, 0.013, 0.013), segs=8, rings=5))
def romp_lint(y, breed=0.075):
    w, zt, zb = romp_sectie(y); cz = Z + (zt + zb) / 2; hh = (zt - zb) / 2; bm = bmesh.new(); R = []
    for dy in (-breed / 2, breed / 2):
        ring = []
        for i in range(48):
            a = i * math.tau / 48; c, s_ = math.cos(a), math.sin(a)
            cx = math.copysign(abs(c) ** (2 / 2.05), c); sy = math.copysign(abs(s_) ** (2 / 2.05), s_)
            ring.append(bm.verts.new(((w + 0.01) * cx, y + dy, cz + (hh + 0.01) * sy)))
        R.append(ring)
    for k in range(48): bm.faces.new((R[0][k], R[0][(k + 1) % 48], R[1][(k + 1) % 48], R[1][k]))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.008); put("tuig", bm)
    for dy in (-breed / 2, breed / 2): romp_band(y + dy, r=0.007, studs=False)
    for i in range(0, 48, 3):
        a = i * math.tau / 48; c, s_ = math.cos(a), math.sin(a)
        cx = math.copysign(abs(c) ** (2 / 2.05), c); sy = math.copysign(abs(s_) ** (2 / 2.05), s_)
        put("goud", ell(((w + 0.022) * cx, y, cz + (hh + 0.022) * sy), (0.017, 0.017, 0.017), segs=10, rings=6))
romp_lint(-0.22)                                                                   # brede buikriem
romp_band(-0.52, math.pi * 0.85, math.pi * 2.15, studs=True, dz=0.0)             # borstriem (onder om de borst, wat lager)
romp_band(0.62, math.pi * 0.85, math.pi * 2.15, studs=True, dz=0.0)                # staartriem om de billen
put("tuig", tube([Vector((0, y, Z + romp_sectie(y)[1] + 0.008)) for y in (-0.36, -0.2, 0.0, 0.2, 0.4, 0.58)], 0.012, 6))   # rugriem
# halster: neusriem, wangriemen, frontriem, gouden rozetten (Ezelclose)
def kop_ring(t, extra=0.008, n=24, r=0.011):
    c = KOP_A.lerp(KOP_B, t); w_ = [s for s in KS if s[0] >= t][0]; pts = []
    for i in range(n + 1):
        a = i * math.tau / n; pts.append(c + Vector((1, 0, 0)) * ((w_[1] + extra) * math.cos(a)) + kn * ((w_[2] + extra) * math.sin(a)))
    put("tuig", tube(pts, r, 6, cap=False))
kop_ring(0.8)
for sx in (-1, 1):
    a_ = KOP_A.lerp(KOP_B, 0.8) + Vector((sx * 0.075, 0, 0)); b_ = KOP_A + Vector((sx * 0.08, 0.03, 0.0)) - kn * 0.02
    put("tuig", tube([a_, a_.lerp(b_, 0.5) + Vector((sx * 0.02, 0, 0)), b_], 0.011, 6))
    put("goud", ell(tuple(a_.lerp(b_, 0.42) + Vector((sx * 0.03, 0, 0))), (0.012, 0.03, 0.03)))
put("tuig", tube([KOP_A + Vector((-0.08, 0.03, 0.0)), KOP_A + Vector((0, 0.06, 0.05)), KOP_A + Vector((0.08, 0.03, 0.0))], 0.011, 6))
# ---- dekje: volgt de romp tussen y -0.33 en 0.25, hangt tot halverwege de flank
db = bmesh.new(); uvl = db.loops.layers.uv.new("UVMap"); NU, NV = 18, 10; V = []
for j in range(NV + 1):
    y = -0.38 + 0.68 * j / NV; w, zt, zb = romp_sectie(y); cz = Z + (zt + zb) / 2; hh = (zt - zb) / 2; row = []
    for i in range(NU + 1):
        a = math.radians(-25 + 230 * i / NU); c, s = math.cos(a), math.sin(a)
        cx = math.copysign(abs(c) ** (2 / 2.05), c); sy = math.copysign(abs(s) ** (2 / 2.05), s)
        row.append(db.verts.new(((w + 0.016) * cx, y, cz + (hh + 0.016) * sy)))
    V.append(row)
for j in range(NV):
    for i in range(NU):
        f = db.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
        for l, (ii, jj) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))): l[uvl].uv = (ii / NU, jj / NV)
bmesh.ops.solidify(db, geom=db.faces[:], thickness=0.006)
obj("BAKE_dekje", db, mat("dekje", (0.9, 0.85, 0.75, 1)), True)
