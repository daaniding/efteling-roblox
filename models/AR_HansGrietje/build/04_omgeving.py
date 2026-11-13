"""04_omgeving Hans en Grietje: voortuin tot het hoofdpad (collectie OMGEVING). Modelframe als 03_forms.
Lage witte tuinmuur met pijlers (taarten/puddingen) en reling, tuinhek met kruk + bordje, binnenhek met krulpoortje, snoeppad,
perken (aarde), 2 limonadefonteintjes, oven met vuur + houtstapel, tegels voor de kooi, wit grindpad, sprookjesboek op de hoek,
klinkerstrook (hoofdpad) met opsluitband alleen buiten. Snoep/taarten/puddingen = BAKE_snoepomg (snoepatlas).
Gebruik: Blender -b -P 04_omgeving.py -- --master AR_HansGrietje_master.blend
"""
import bpy, bmesh, sys, os, math, random, json, importlib.util
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("hg", os.path.join(HERE, "build", "03_forms.py")); hg = importlib.util.module_from_spec(spec); spec.loader.exec_module(hg)
hg.PHASE = "04_omgeving"; hg.OWNER_TAG = "phase:04_omgeving"
rnd = random.Random(23); hg.rnd = rnd
cube, prism_y, frustum = hg.cube, hg.prism_y, hg.frustum
MATS = {"pad": ((150, 142, 130), 1.0), "band": ((128, 126, 120), 0.9), "aarde": ((70, 52, 38), 1.0), "grind": ((232, 226, 214), 1.0),
        "tegels": ((150, 146, 136), 0.9), "steen": ((168, 166, 160), 0.9), "limonade": ((196, 40, 50), 0.1), "pannen": ((150, 78, 58), 0.8),
        "hout": ((96, 64, 40), 0.9), "papier": ((236, 226, 196), 0.9), "snoeppad": ((238, 232, 218), 0.9), "reling": ((40, 78, 66), 0.5), "terracotta": ((170, 92, 62), 0.9), "hekwit": ((238, 236, 228), 0.7)}


def sn_new():
    hg.SN = bmesh.new(); hg.SN_UV = hg.SN.loops.layers.uv.new("UVMap")


def uv_solid(me, k, M=Matrix()):   # hele mesh op de effen basiskleur van tegel k (ring r~0.6, naast de stip)
    vs = [hg.SN.verts.new(M @ v.co) for v in me.vertices]
    for p in me.polygons:
        try: f = hg.SN.faces.new([vs[i] for i in p.vertices])
        except ValueError: continue
        for l in f.loops: l[hg.SN_UV].uv = hg.tile_uv(k, 0.78 + rnd.random() * 0.04, 0.48 + rnd.random() * 0.04)


def me_of(bm):
    me = bpy.data.meshes.new("_t"); bm.to_mesh(me); bm.free(); return me


def offset_strip(pts, w0, w1):   # polylijn -> strook tussen zijdelingse offsets w0..w1 (links = +)
    L, R = [], []
    for i, p in enumerate(pts):
        a = Vector(pts[max(i - 1, 0)]); b = Vector(pts[min(i + 1, len(pts) - 1)]); d = (b - a).normalized(); n = Vector((-d.y, d.x))
        P = Vector(p); L.append(P + n * w1); R.append(P + n * w0)
    return L, R


COLL = []   # onzichtbare botsblokken [cx, cy, cz, sx, sy, sz, hoek_graden] (2.6 m hoog: niet erover springen)
def coll_seg(a, b, t=0.25, h=2.6):
    a, b = Vector(a), Vector(b); d = b - a; L = d.length
    if L < 0.05: return
    c = (a + b) / 2; COLL.append([round(c.x, 3), round(c.y, 3), round(h / 2, 3), round(L + 0.1, 3), t, h, round(math.degrees(math.atan2(d.y, d.x)), 2)])


def resample(pts, step):
    out = [Vector(pts[0])]; acc = 0.0
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b); L = (b - a).length; t = 0.0
        while acc + (L - t) >= step:
            t += step - acc; acc = 0.0; out.append(a.lerp(b, t / L))
        acc += L - t
    if (out[-1] - Vector(pts[-1])).length > step * 0.3: out.append(Vector(pts[-1]))
    return out


def white_fence(bm, center, w, keep, step=1.6, h=0.62):
    """laag wit hekje op zijdelingse offset w van een padlijn; alleen waar keep(p); paaltjes + 2 regels, botsblokken per vak"""
    L, _ = offset_strip(center, w, w); pts = resample([(p.x, p.y) for p in L], step)
    runs, cur = [], []
    for p in pts:
        if keep(p): cur.append(p)
        elif cur: runs.append(cur); cur = []
    if cur: runs.append(cur)
    for run in runs:
        if len(run) < 2: continue
        fence_run(bm, run, h)
    return [r for r in runs if len(r) >= 2]


def fence_run(bm, run, h=0.62):
    """paaltjes + 2 regels langs de punten van run, botsblok per vak"""
    for p in run:
        cube(bm, p.x - 0.045, p.x + 0.045, p.y - 0.045, p.y + 0.045, -0.05, h)
        cube(bm, p.x - 0.06, p.x + 0.06, p.y - 0.06, p.y + 0.06, h, h + 0.04)
    for a, b in zip(run, run[1:]):
        d = b - a; Lr = d.length; ang = math.atan2(d.y, d.x)
        for z in (0.28, h - 0.08):
            sg = bmesh.new(); cube(sg, 0, Lr, -0.022, 0.022, z, z + 0.06)
            bmesh.ops.transform(sg, matrix=Matrix.Translation((a.x, a.y, 0)) @ Matrix.Rotation(ang, 4, "Z"), verts=sg.verts); bm.from_mesh(me_of(sg))
        coll_seg(a, b)


def strip_mesh(bm, pts, w0, w1, z0, z1):
    L, R = offset_strip(pts, w0, w1)
    for i in range(len(pts) - 1):
        quad = [(R[i], R[i + 1], L[i + 1], L[i])]
        for q in quad:
            a = [bm.verts.new((p.x, p.y, z1)) for p in q]; b = [bm.verts.new((p.x, p.y, z0)) for p in q]
            bm.faces.new(a); bm.faces.new(b[::-1])
            for k in range(4): bm.faces.new((a[k], b[k], b[(k + 1) % 4], a[(k + 1) % 4]))


def smooth_path(pts, n=6):   # Catmull-Rom
    out = []
    P = [Vector(p) for p in pts]; P = [P[0]] + P + [P[-1]]
    for i in range(1, len(P) - 2):
        for t in [k / n for k in range(n)]:
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2]); return [(p.x, p.y) for p in out]


def wall_along(bm, pts, h=0.62, t=0.32):   # lage tuinmuur met ronde kap
    for i in range(len(pts) - 1):
        a, b = Vector(pts[i]), Vector(pts[i + 1]); d = b - a; L = d.length; ang = math.atan2(d.y, d.x)
        s = bmesh.new()
        prof = [(-t / 2, 0), (t / 2, 0), (t / 2, h - 0.06), (t * 0.3, h), (0, h + 0.03), (-t * 0.3, h), (-t / 2, h - 0.06)]
        prism_y(s, [(x, z) for x, z in prof], 0, L + 0.04)
        bmesh.ops.transform(s, matrix=Matrix.Translation((a.x, a.y, -0.05)) @ Matrix.Rotation(ang - math.pi / 2, 4, "Z"), verts=s.verts)
        bm.from_mesh(me_of(s))


def pillar(bm, x, y, h=0.95, w=0.5):
    cube(bm, x - w / 2, x + w / 2, y - w / 2, y + w / 2, -0.05, h - 0.08)
    cube(bm, x - w / 2 - 0.05, x + w / 2 + 0.05, y - w / 2 - 0.05, y + w / 2 + 0.05, h - 0.08, h)


def cake(x, y, z, kind):
    """taart (3 lagen, wit/rood/geel met snoepjes) of pudding (geribbelde roze puddingvorm, 2 lagen) op een bord"""
    plate = bmesh.new(); frustum(plate, x, y, 0.3, 0.32, z, z + 0.03, 16); uv_solid(me_of(plate), 15)
    if kind == "pudding":
        zz = z + 0.03
        for r0, r1, hh in ((0.24, 0.2, 0.2), (0.17, 0.12, 0.16)):
            b = bmesh.new(); segs = 24
            ring = lambda r, zc: [b.verts.new((x + r * (1 + 0.1 * (i % 2)) * math.cos(math.tau * i / segs), y + r * (1 + 0.1 * (i % 2)) * math.sin(math.tau * i / segs), zc)) for i in range(segs)]
            A, B = ring(r0, zz), ring(r1, zz + hh)
            b.faces.new(A[::-1]); b.faces.new(B)
            for i in range(segs): b.faces.new((A[i], A[(i + 1) % segs], B[(i + 1) % segs], B[i]))
            uv_solid(me_of(b), 0); zz += hh
        top = bmesh.new(); bmesh.ops.create_uvsphere(top, u_segments=10, v_segments=5, radius=0.06); bmesh.ops.translate(top, vec=(x, y, zz), verts=top.verts); uv_solid(me_of(top), 11)
    else:
        col = {"wit": 15, "rood": 11, "geel": 6}[kind]; zz = z + 0.03
        for r, hh in ((0.25, 0.14), (0.19, 0.13), (0.13, 0.12)):
            b = bmesh.new(); frustum(b, x, y, r, r, zz, zz + hh, 18); uv_solid(me_of(b), col)
            for i in range(10):   # snoepjes rond de laag
                a = math.tau * i / 10 + zz; hg.deco("snoep", Vector((x + math.cos(a) * r, y + math.sin(a) * r, zz + hh / 2)), Vector((math.cos(a), math.sin(a), 0)), 0.9)
            rim = bmesh.new(); frustum(rim, x, y, r + 0.015, r + 0.015, zz + hh - 0.02, zz + hh + 0.015, 18); uv_solid(me_of(rim), 7 if col == 15 else 15)
            zz += hh
        kers = bmesh.new(); bmesh.ops.create_uvsphere(kers, u_segments=8, v_segments=5, radius=0.045); bmesh.ops.translate(kers, vec=(x, y, zz + 0.03), verts=kers.verts); uv_solid(me_of(kers), 11)


def iron_fence(bm_out, pts, h=0.9, step=0.12, posts=1.6, z0=0.0):
    bm = bmesh.new()
    for i in range(len(pts) - 1):
        a, b = Vector(pts[i]), Vector(pts[i + 1]); L = (b - a).length; d = (b - a) / L; n = int(L / step)
        for k in range(n + 1):
            p = a + d * (k * L / n); cube(bm, p.x - 0.009, p.x + 0.009, p.y - 0.009, p.y + 0.009, 0, h)
        for z in (0.08, h - 0.04):
            s = bmesh.new(); cube(s, -0.015, L + 0.015, -0.02, 0.02, z, z + 0.035)
            bmesh.ops.transform(s, matrix=Matrix.Translation((a.x, a.y, 0)) @ Matrix.Rotation(math.atan2(d.y, d.x), 4, "Z"), verts=s.verts); bm.from_mesh(me_of(s))
        m = max(1, int(L / posts))
        for k in range(m + 1):
            p = a + d * (k * L / m); cube(bm, p.x - 0.025, p.x + 0.025, p.y - 0.025, p.y + 0.025, 0, h + 0.06)
            s = bmesh.new(); bmesh.ops.create_uvsphere(s, u_segments=8, v_segments=5, radius=0.04); bmesh.ops.translate(s, vec=(p.x, p.y, h + 0.1), verts=s.verts); bm.from_mesh(me_of(s))
    bmesh.ops.translate(bm, vec=(0, 0, z0), verts=bm.verts); bm_out.from_mesh(me_of(bm))


def scroll(bm, cx, y, z, r, turns=1.6, flip=1):   # smeedijzeren krul (spiraal) in het xz-vlak
    pts = []
    for i in range(30):
        t = i / 29 * turns * math.tau; rr = r * (1 - i / 34)
        pts.append(Vector((cx + flip * rr * math.cos(t), y, z + rr * math.sin(t))))
    for a, b in zip(pts, pts[1:]):
        d = b - a; L = d.length; s = bmesh.new(); cube(s, -0.011, 0.011, -0.011, 0.011, 0, L)
        ang = math.atan2(d.x, d.z); bmesh.ops.transform(s, matrix=Matrix.Translation(a) @ Matrix.Rotation(ang, 4, "Y"), verts=s.verts); bm.from_mesh(me_of(s))


def build(master):
    hg.open_master(master)
    if "OMGEVING" in bpy.data.collections:
        for o in list(bpy.data.collections["OMGEVING"].all_objects): bpy.data.objects.remove(o)
    for n, (c, r) in MATS.items():
        m = hg.material("MAT_" + n, tuple((v / 255) ** 2.2 for v in c) + (1,), r); m.diffuse_color = tuple((v / 255) ** 2.2 for v in c) + (1,)
    C = "OMGEVING"; B = {k: bmesh.new() for k in ("stuc", "pad", "aarde", "grind", "tegels", "steen", "limonade", "pannen", "hout", "papier",
                                                  "snoeppad", "ijzer", "donker", "vuur", "reling", "terracotta", "hekwit")}
    sn_new()
    # ---- hoofdpad: klinkerstrook langs de voorkant + schuine hoek (OSM 405848924), binnenrand tegen de muur, opsluitband alleen buiten
    # hoofdpad van grind (Daan), loop volgens OSM 405848924 + 55340110: rechts splitsing naar achteren en naar rechtsvoor, links naar achteren
    path = smooth_path([(19.4, -18.9), (15.4, -16.0), (11.2, -13.0), (3.0, -12.75), (-2.2, -12.45), (-6.0, -12.3), (-9.2, -10.1), (-11.0, -7.5), (-11.9, -3.0), (-12.3, 1.7), (-14.6, 4.7), (-17.5, 7.0)])
    strip_mesh(B["pad"], path, -1.45, 1.7, -0.05, 0.03)
    tak = smooth_path([(11.0, -12.4), (11.9, -6.0), (12.3, -1.5), (13.3, 5.0), (14.0, 8.7), (15.5, 12.0)])
    strip_mesh(B["pad"], tak, -1.5, 1.5, -0.05, 0.028)
    # ---- afbakening (Daan): laag wit hekje langs alle padranden waar geen muurtje/leuning staat, rondom het hele perceel
    COLL.clear()
    def tuinkant(p):    # hoofdpad, kant van de tuin: niet langs de tuinmuren/leuning/poort, niet bij de aansluiting van het zijpad
        if p.y < 1.0 and p.x < 5.7: return False
        if 9.3 < p.x < 12.9 and p.y > -14.5: return False
        return True
    rt = white_fence(B["hekwit"], path, -1.62, tuinkant)
    ro = white_fence(B["hekwit"], path, 1.87, lambda p: True)
    rp = white_fence(B["hekwit"], tak, 1.65, lambda p: p.y > -10.9)      # kant van het huis (-x)
    rm = white_fence(B["hekwit"], tak, -1.65, lambda p: p.y > -10.9)     # overkant (+x)
    # hoeken bij de aansluiting dicht: hekje langs het hoofdpad doorkoppelen naar het hekje langs het zijpad
    voor = [r for r in rt if r[-1].x < 10.5]; na = [r for r in rt if r[0].x > 11.5]
    if voor and rp: fence_run(B["hekwit"], [voor[-1][-1], rp[0][0]])
    if na and rm: fence_run(B["hekwit"], [rm[0][0], na[0][0]])
    nf = sum(len(r) for r in rt + ro + rp + rm)
    # gesloten wit poortje over het grindpad bij het hoofdpad (dienstpad)
    ga, gb = Vector((4.08, -11.25)), Vector((5.72, -11.22))
    for q in (ga, gb): cube(B["hekwit"], q.x - 0.07, q.x + 0.07, q.y - 0.07, q.y + 0.07, -0.05, 0.85); cube(B["hekwit"], q.x - 0.09, q.x + 0.09, q.y - 0.09, q.y + 0.09, 0.85, 0.9)
    for z in (0.15, 0.68): cube(B["hekwit"], ga.x, gb.x, -11.27, -11.21, z, z + 0.07)
    for i in range(1, 12):
        x = ga.x + (gb.x - ga.x) * i / 12; cube(B["hekwit"], x - 0.025, x + 0.025, -11.26, -11.22, 0.15, 0.62 + 0.1 * math.sin(math.pi * i / 12))
    coll_seg(ga, gb)
    # botsing langs leuning + tuinhek en het binnenhekje (de ijzeren meshes zelf botsen niet meer)
    coll_seg((-4.0, -11.02), (3.45, -11.15)); coll_seg((-4.05, -4.72), (2.65, -4.72), 0.2, 1.4)
    hg.log("wit hekje paaltjes", nf, "botsblokken", len(COLL))
    # ---- witte tuinmuur alleen om de linkerhoek (Boekloc_2024): dik, bolle kap, organisch; pijler met rode taart waar de leuning begint
    mb = bmesh.new()
    wl = smooth_path([(-4.3, -10.95), (-6.2, -10.85), (-8.6, -9.0), (-10.1, -6.6), (-10.7, -3.0), (-10.9, 0.8)])
    wall_along(mb, wl, h=0.6, t=0.44); pillar(mb, -4.3, -10.95, 1.0, 0.55)
    wr = smooth_path([(3.75, -11.15), (3.75, -10.0), (4.05, -8.6), (4.15, -7.0), (3.85, -5.7), (3.25, -4.9), (2.95, -4.72)])
    wall_along(mb, wr, h=0.6, t=0.42); pillar(mb, 3.75, -11.15, 1.0, 0.55)
    mo = hg.new_mesh_object("HO_muur__stuc", mb, C); hg.assign(mo, bpy.data.materials["MAT_stuc"])
    hg.apply_mod(mo, "REMESH", mode="VOXEL", voxel_size=0.04, use_smooth_shade=True)
    me = mo.data; bmw = bmesh.new(); bmw.from_mesh(me); bmw.normal_update()
    for v in bmw.verts: v.co += v.normal * (0.02 * hg.noise.noise(v.co * 1.5) + 0.006 * hg.noise.noise(v.co * 6.0))
    bmesh.ops.smooth_vert(bmw, verts=bmw.verts, factor=0.6, use_axis_x=True, use_axis_y=True, use_axis_z=True); bmw.to_mesh(me); bmw.free()
    hg.apply_mod(mo, "DECIMATE", decimate_type="COLLAPSE", ratio=0.12); hg.shade_smooth(mo, math.radians(50))
    cake(-4.3, -10.95, 1.0, "rood"); cake(3.75, -11.15, 1.0, "geel")
    # terracotta potten in het linkerperk (Boekloc)
    for px_, py_ in ((-8.6, -6.2), (-9.3, -4.2), (-7.7, -7.6), (-8.0, -2.4), (-6.6, -5.0), (-6.2, -8.6), (-9.5, -1.0), (-5.6, -3.0)):
        frustum(B["terracotta"], px_, py_, 0.17, 0.24, 0.0, 0.32, 12); frustum(B["terracotta"], px_, py_, 0.25, 0.25, 0.28, 0.34, 12)
    # ---- groene buisleuning langs de voorkant (Hghuis5), tuinhek met kruk bij het snoeppad (OSM-hek -2.42, -10.83)
    def tube(bm, a, b, r=0.024, segs=6):
        a, b = Vector(a), Vector(b); d = b - a; L = d.length; s2 = bmesh.new()
        bmesh.ops.create_cone(s2, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=L)
        q = d.normalized().to_track_quat("Z", "Y").to_matrix().to_4x4()
        bmesh.ops.transform(s2, matrix=Matrix.Translation((a + b) / 2) @ q, verts=s2.verts); bm.from_mesh(me_of(s2))
    for seg in ([(-4.0, -11.02), (-2.95, -11.02)], [(-1.88, -11.04), (0.8, -11.1), (3.45, -11.15)]):
        for (ax, ay), (bx_, by_) in zip(seg, seg[1:]):
            for z in (0.45, 0.95): tube(B["reling"], (ax, ay, z), (bx_, by_, z))
        for (px_, py_) in seg: tube(B["reling"], (px_, py_, -0.05), (px_, py_, 0.98), 0.03)
    iron_fence(B["reling"], [(-2.92, -11.02), (-1.92, -11.04)], h=0.95, step=0.11, posts=1.0)
    cube(B["reling"], -2.5, -2.36, -11.12, -10.98, 0.82, 0.86); cube(B["reling"], -2.36, -2.25, -11.14, -11.1, 0.78, 0.86)   # de kruk
    cube(B["hout"], -3.74, -3.7, -10.35, -10.31, 0, 0.95); s = bmesh.new(); bmesh.ops.create_circle(s, cap_ends=True, segments=16, radius=0.17)
    bmesh.ops.scale(s, vec=(1.0, 0.6, 1), verts=s.verts); bmesh.ops.rotate(s, verts=s.verts, matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
    bmesh.ops.translate(s, vec=(-3.72, -10.37, 0.98), verts=s.verts); uv_solid(me_of(s), 11)                      # rood ovaal bordje
    # ---- binnenhek y -4.7 met stucpijlers (taart wit links, pudding rechts) en krulpoortje x -0.85..0.05
    iron_fence(B["ijzer"], [(-4.05, -4.72), (-0.9, -4.7)], h=0.9); iron_fence(B["ijzer"], [(0.1, -4.7), (2.65, -4.72)], h=0.9)
    iron_fence(B["ijzer"], [(-0.85, -4.72), (0.05, -4.72)], h=0.95, step=0.1, posts=0.9)
    for f in (-1, 1): scroll(B["ijzer"], -0.4 + f * 0.13, -4.72, 1.1, 0.1, flip=f)   # fijne krulletjes (Hghuis-vk)
    s = bmesh.new()
    for i in range(16):
        a = math.pi * i / 15; cube(s, -0.4 + 0.47 * math.cos(a) - 0.012, -0.4 + 0.47 * math.cos(a) + 0.012, -4.735, -4.705, 0.95 + 0.38 * math.sin(a) - 0.012, 0.95 + 0.38 * math.sin(a) + 0.012)
    B["ijzer"].from_mesh(me_of(s))
    for x, k in ((-4.35, "wit"), (2.95, "pudding")): pillar(B["stuc"], x, -4.72, 0.85, 0.55); cake(x, -4.72, 0.85, k)
    # ---- snoeppad (OSM 766787179): tuinhek -> binnenhek -> trap, wit met bonte snoepjes
    sp = smooth_path([(-2.42, -11.1), (-2.6, -9.2), (-1.4, -7.3), (-0.45, -5.6), (-0.4, -4.4), (-0.1, -2.5)], 5)
    strip_mesh(B["snoeppad"], sp, -0.6, 0.6, -0.05, 0.035)
    L, R = offset_strip(sp, -0.52, 0.52); cnt = 0
    for i in range(len(sp) - 1):
        for _ in range(int((Vector(sp[i + 1]) - Vector(sp[i])).length * 26)):
            t = rnd.random(); w = rnd.random()
            a = R[i].lerp(R[i + 1], t); b = L[i].lerp(L[i + 1], t); p = a.lerp(b, w)
            hg.add_shape(hg.ellipse(rnd.uniform(0.05, 0.085), rnd.uniform(0.045, 0.08), 8), 0.006, rnd.randrange(4, 12), Matrix.Translation((p.x, p.y, 0.036)) @ Matrix.Rotation(rnd.random() * 6, 4, "Z"), dome=0.3); cnt += 1
    # ---- perken (aarde) in de voortuin, tegels voor de kooi, wit grindpad (OSM 766787178)
    bed = smooth_path([(-1.0, -10.7), (-5.7, -10.5), (-8.2, -8.7), (-9.6, -6.4), (-10.2, -3.0), (-10.3, 0.5), (-4.0, 0.5), (-3.6, -2.2), (-0.8, -2.6), (0.3, -4.3), (3.2, -4.6), (3.4, -10.6), (-1.0, -10.7)], 3)
    pts = [Vector((x, y, 0.012)) for x, y in bed[:-1]]
    r = bmesh.ops.contextual_create(B["aarde"], geom=[B["aarde"].verts.new(p) for p in pts]) if False else None
    bv = [B["aarde"].verts.new(p) for p in pts]; f = B["aarde"].faces.new(bv); bmesh.ops.triangulate(B["aarde"], faces=[f])
    for x0, y0 in [(1.3, -1.6), (1.8, -1.2), (2.3, -1.5), (2.8, -1.1), (1.6, -0.7), (2.2, -0.6), (2.8, -0.55), (3.3, -0.9), (3.6, -1.6), (3.1, -1.9), (2.5, -2.1)]:
        ps = [Vector((x0 + 0.24 * math.cos(math.tau * i / 7) * rnd.uniform(0.8, 1.15), y0 + 0.2 * math.sin(math.tau * i / 7) * rnd.uniform(0.8, 1.15), 0.035)) for i in range(7)]
        a = [B["tegels"].verts.new(p) for p in ps]; b = [B["tegels"].verts.new(p - Vector((0, 0, 0.06))) for p in ps]
        B["tegels"].faces.new(a); B["tegels"].faces.new(b[::-1])
        for i in range(7): B["tegels"].faces.new((a[i], b[i], b[(i + 1) % 7], a[(i + 1) % 7]))
    gp = smooth_path([(0.4, -2.7), (2.3, -2.6), (4.4, -3.7), (5.1, -6.5), (5.0, -9.2), (4.8, -11.0), (4.8, -11.9)], 5)
    strip_mesh(B["grind"], gp, -0.7, 0.7, -0.05, 0.022)
    # ---- limonadefonteintjes: ring van 6 grijze blokken, rood water, straaltje
    for fx, fy in ((-4.6, -7.4), (1.7, -8.3)):
        for i in range(6):
            a0 = math.tau * i / 6 + 0.06; a1 = math.tau * (i + 1) / 6 - 0.06; s = bmesh.new()
            ring = [(fx + rr * math.cos(a0 + (a1 - a0) * k / 3), fy + rr * math.sin(a0 + (a1 - a0) * k / 3)) for rr in (0.55,) for k in range(4)] + \
                   [(fx + 0.3 * math.cos(a1 - (a1 - a0) * k / 3), fy + 0.3 * math.sin(a1 - (a1 - a0) * k / 3)) for k in range(4)]
            vs = [s.verts.new((x, y, 0.2)) for x, y in ring]; vb = [s.verts.new((x, y, -0.02)) for x, y in ring]
            s.faces.new(vs); s.faces.new(vb[::-1])
            for k in range(8): s.faces.new((vs[k], vb[k], vb[(k + 1) % 8], vs[(k + 1) % 8]))
            bmesh.ops.recalc_face_normals(s, faces=s.faces); B["steen"].from_mesh(me_of(s))
        frustum(B["limonade"], fx, fy, 0.34, 0.34, 0.0, 0.13, 16)
        frustum(B["limonade"], fx, fy, 0.025, 0.012, 0.13, 0.42, 6)
    # ---- oven rechtsachter (Oven2016): witte romp, stenen boog met vuur, ijzeren deurtje, rood pannendak, houtstapel
    ox, oy = 5.85, 0.8
    s = bmesh.new(); hg.prism_y(s, [(ox - 0.75, -0.05), (ox + 0.75, -0.05), (ox + 0.62, 1.55), (ox, 2.0), (ox - 0.62, 1.55)], oy - 0.6, oy + 0.6)
    ob_tmp = me_of(s); B["stuc"].from_mesh(ob_tmp)
    for i in range(9):   # boog van grijze blokken rond de vuurmond (kijkt -y)
        a = math.pi * i / 8; cube(B["steen"], ox + 0.42 * math.cos(a) - 0.09, ox + 0.42 * math.cos(a) + 0.09, oy - 0.72, oy - 0.58, 0.1 + 0.42 * math.sin(a) - 0.07, 0.1 + 0.42 * math.sin(a) + 0.07)
    cube(B["donker"], ox - 0.32, ox + 0.32, oy - 0.62, oy - 0.6, 0.0, 0.42); cube(B["vuur"], ox - 0.22, ox + 0.22, oy - 0.64, oy - 0.62, 0.02, 0.2)
    cube(B["ijzer"], ox - 0.22, ox + 0.22, oy - 0.64, oy - 0.6, 0.8, 1.12); cube(B["ijzer"], ox + 0.22, ox + 0.34, oy - 0.66, oy - 0.62, 0.94, 0.98)
    for sgn in (-1, 1):
        s = bmesh.new(); hg.slab(s, [Vector((ox + sgn * 0.85, oy - 0.75, 1.5)), Vector((ox + sgn * 0.85, oy + 0.75, 1.5)), Vector((ox, oy + 0.75, 2.12)), Vector((ox, oy - 0.75, 2.12))], 0.07)
        bmesh.ops.recalc_face_normals(s, faces=s.faces); B["pannen"].from_mesh(me_of(s))
    for i in range(14):   # houtstapel naast de oven
        x = ox - 1.75 + (i % 5) * 0.2 + (0.1 if (i // 5) % 2 else 0); z = 0.09 + (i // 5) * 0.17
        s = bmesh.new(); bmesh.ops.create_cone(s, cap_ends=True, segments=8, radius1=0.09, radius2=0.09, depth=0.9)
        bmesh.ops.rotate(s, verts=s.verts, matrix=Matrix.Rotation(math.pi / 2, 3, "X")); bmesh.ops.translate(s, vec=(x, oy, z), verts=s.verts); B["hout"].from_mesh(me_of(s))
    # ---- sprookjesboek op de hoek (2024): standaard + open boek, kijkt naar het pad
    bx, by = -6.9, -9.9; ang = math.radians(-40)
    s = bmesh.new(); cube(s, -0.04, 0.04, -0.04, 0.04, 0, 0.75); cube(s, -0.5, 0.5, -0.32, 0.32, 0.75, 0.8)
    bmesh.ops.transform(s, matrix=Matrix.Translation((bx, by, 0)) @ Matrix.Rotation(ang, 4, "Z"), verts=s.verts); B["hout"].from_mesh(me_of(s))
    for sgn in (-1, 1):
        s = bmesh.new(); cube(s, 0, 0.45, -0.3, 0.3, 0, 0.05); bmesh.ops.rotate(s, verts=s.verts, matrix=Matrix.Rotation(sgn * 0.12, 3, "Y"))
        if sgn < 0: bmesh.ops.scale(s, vec=(-1, 1, 1), verts=s.verts)
        bmesh.ops.transform(s, matrix=Matrix.Translation((bx, by, 0.8)) @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Rotation(-0.45, 4, "X"), verts=s.verts)
        bmesh.ops.recalc_face_normals(s, faces=s.faces); B["papier"].from_mesh(me_of(s))
    # ---- objecten
    for k, bm in B.items():
        if len(bm.faces) == 0: bm.free(); continue
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ob = hg.new_mesh_object("HO_%s__%s" % (k, k), bm, C); hg.assign(ob, bpy.data.materials["MAT_" + k])
    me = bpy.data.meshes.new("BAKE_snoepomg"); hg.SN.to_mesh(me); ob = bpy.data.objects.new("BAKE_snoepomg", me); hg.col(C).objects.link(ob); hg.own(ob)
    ob.data.materials.append(hg.atlas_material("MAT_snoep", os.path.join(HERE, "textures", "HG_snoep_kleur.png")))
    for o in hg.col(C).all_objects: o["owner"] = "phase:04_omgeving"
    json.dump({"colliders": COLL, "lamps": []}, open(os.path.join(HERE, "exports", "omgeving_extra.json"), "w"))
    hg.save_master(master); hg.log("omgeving objects", len([o for o in bpy.data.objects if o.get("owner") == "phase:04_omgeving"]), "snoeppad", cnt,
                               "tris", sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in hg.col(C).objects))


if __name__ == "__main__":
    a = hg.argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
