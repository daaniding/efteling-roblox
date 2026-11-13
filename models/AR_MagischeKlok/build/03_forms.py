"""03_forms Magische Klok: klokkentoren + twee kantelenmuren + slotgrachtje + sokkels/schildjes + voorgrondmuurtje.
Meters, Z op, z=0 maaiveld, klok kijkt naar -Y (WNW), +X = ZZW, oorsprong = midden toren (asset-brief.md).
Hulpfuncties uit AR_Assepoester/build/03_forms.py (put, bz, blathe, btube, band, boutline, TR, PARTS, ...).
Atlas-objecten (naam BAKE_ + eigen UV) slaan de bake over: BAKE_klok (MK_klok_kleur), BAKE_ruiter (MK_ruiter_kleur, alpha).
Herauten: build/03b_heraut.py. Gebruik: Blender -b -P 03_forms.py -- --master AR_MagischeKlok_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
_src = open(os.path.join(HERE, "..", "..", "AR_Assepoester", "build", "03_forms.py")).read().split("# ---- ramen ----")[0]
exec(_src)
RNG = random.Random(1952)
MATS = {
    "baksteen": ((0.55, 0.36, 0.28, 1), 0.9), "stuc": ((0.66, 0.63, 0.56, 1), 0.9), "leien": ((0.30, 0.26, 0.23, 1), 0.85),
    "kern": ((0.52, 0.53, 0.52, 1), 0.8), "lood": ((0.42, 0.44, 0.45, 1), 0.5), "ijzer": ((0.05, 0.06, 0.06, 1), 0.45),
    "brons": ((0.30, 0.24, 0.14, 1), 0.35), "goud": ((0.80, 0.60, 0.20, 1), 0.3), "pannen": ((0.50, 0.26, 0.18, 1), 0.85),
    "klokhout": ((0.12, 0.25, 0.24, 1), 0.6), "hout": ((0.10, 0.22, 0.16, 1), 0.7), "steen": ((0.58, 0.57, 0.54, 1), 0.9),
    "rood": ((0.62, 0.08, 0.06, 1), 0.5), "bodem": ((0.20, 0.16, 0.11, 1), 1.0), "water": ((0.10, 0.12, 0.08, 1), 0.05),
    "klinker": ((0.45, 0.43, 0.40, 1), 0.9), "toon_groen": ((0.25, 0.42, 0.36, 1), 0.7), "toon_rood": ((0.70, 0.30, 0.22, 1), 0.7),
    "huid": ((0.85, 0.66, 0.52, 1), 0.6), "haar": ((0.80, 0.62, 0.30, 1), 0.7),
    "haag": ((0.10, 0.20, 0.08, 1), 0.9), "mand": ((0.42, 0.30, 0.16, 1), 0.9), "paal": ((0.18, 0.11, 0.06, 1), 0.7), "glaslamp": ((0.9, 0.8, 0.6, 1), 0.2), "kant_papier": ((0.9, 0.88, 0.8, 1), 0.8),
}
COLL = []; HERAUTEN = []; LAMPS_ = []; PLEIN = {}
def coll_box(cx, cy, cz, sx, sy, sz, ang=0.0): COLL.append([round(v, 3) for v in (cx, cy, cz, sx, sy, sz, ang)])

# ------------------------------------------------------------------ maten (asset-brief.md)
R_ROMP, Z_ROMP = 2.08, 3.35            # bakstenen romp
R_KERN, Z_BAND = 1.75, 3.95            # ruiterband
R_DAK = 2.55; Z_TOP_DAK = 5.9
KZ0, KZ1 = 2.75, 3.92                 # uurwerk (front.jpg: onderkant op kantelhoogte)
WALL_H, WALL_T = 2.4, 0.5
KANT_W, KANT_GAP, KANT_H = 0.6, 0.5, 0.5
ARMS = {   # binnenvlak-start, richting, plein-normaal, lengte (vanaf de start)
    "N": (Vector((-1.33, -2.96)), Vector((-0.6997, -0.7149)), Vector((0.7149, -0.6997)), 14.45),
    "W": (Vector((0.96, -3.07)), Vector((0.6986, -0.7154)), Vector((-0.7154, -0.6986)), 17.25),
}
HERAUT_S = {"N": (3.8, 8.0, 11.8), "W": (2.8, 5.3, 7.8)}   # afstand langs de arm (overzicht-okt2009: west dicht bij de toren, noord ver uit elkaar)
SHIFT = 1.2                           # front.jpg: de toren staat helemaal voor de muren -> binnenvlakken 1.2 m achter de OSM-lijn
for _k, (_p, _u, _n, _L) in list(ARMS.items()): ARMS[_k] = (_p - _n * SHIFT, _u, _n, _L)


def arm_M(name, s=0.0, t=0.0, z=0.0):
    """matrix: lokaal x = langs de muur, y = de muur in (weg van het plein), z omhoog; oorsprong op het binnenvlak op afstand s"""
    p0, u, n, L = ARMS[name]; b = -n; o = p0 + u * s + b * t
    return Matrix(((u.x, b.x, 0, o.x), (u.y, b.y, 0, o.y), (0, 0, 1, z), (0, 0, 0, 1)))


def lathe_course(part, mat, prof, segs, course, lip=0.03):
    """dak langs een profiel [(r, z)] van voet naar top, met zaagtand per rij (leien/schijfjes)"""
    pts = [Vector((r, z)) for r, z in prof]; L = sum((b - a).length for a, b in zip(pts, pts[1:])); n = max(3, round(L / course))
    def at(t):
        d = t * L
        for a, b in zip(pts, pts[1:]):
            l = (b - a).length
            if d <= l: return a.lerp(b, d / l)
            d -= l
        return pts[-1]
    bm = bmesh.new()
    def ring(r, z): return [bm.verts.new((r * math.cos(k * math.tau / segs), r * math.sin(k * math.tau / segs), z)) for k in range(segs)]
    rings = [ring(pts[0].x + lip, pts[0].y - 0.06)]
    for i in range(n):
        a = at(i / n); b = at((i + 1) / n)
        jit = 0.008 * math.sin(i * 2.3)
        rings.append(ring(a.x + lip + jit, a.y)); rings.append(ring(max(b.x, 0.001), b.y))
    for A, B in zip(rings, rings[1:]):
        for k in range(segs): bm.faces.new((A[k], A[(k + 1) % segs], B[(k + 1) % segs], B[k]))
    bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put(part, mat, bm)


def uv_rect_object(name, bm, img, mat_name, alpha=False):
    """bmesh met UV (laag 'UVMap' al gezet) -> object BAKE_<name> met atlasmateriaal"""
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); col("FORMS").objects.link(ob); own(ob)
    m = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    if bpy.app.version < (5, 0, 0): m.use_nodes = True
    nt = m.node_tree; bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None) or nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(img, check_existing=True)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if alpha: nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.6; ob.data.materials.append(m); return ob


def quad_uv(bm, corners, uvs):
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    f = bm.faces.new([bm.verts.new(c) for c in corners])
    for l, uv in zip(f.loops, uvs): l[uvl].uv = uv
    return f


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); HERAUTEN.clear(); LAMPS_.clear(); PLEIN.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ================= TOREN =================
    put("toren", "baksteen", blathe([(0, -0.45), (R_ROMP, -0.45), (R_ROMP, Z_ROMP - 0.1), (R_ROMP + 0.07, Z_ROMP - 0.1), (R_ROMP + 0.07, Z_ROMP), (R_KERN, Z_ROMP), (0, Z_ROMP)], 48))
    put("toren", "kern", blathe([(0, Z_ROMP - 0.02), (R_KERN, Z_ROMP - 0.02), (R_KERN, Z_BAND + 0.05), (0, Z_BAND + 0.05)], 32))
    put("toren", "steen", blathe([(R_KERN + 0.02, Z_ROMP), (R_ROMP - 0.02, Z_ROMP), (R_ROMP - 0.02, Z_ROMP + 0.04), (R_KERN + 0.02, Z_ROMP + 0.04)], 48))   # looprand
    for k in range(8):                                                     # staanders (ijzer)
        a = k * math.tau / 8 + math.tau / 16
        put("toren", "ijzer", btube([(1.98 * math.cos(a), 1.98 * math.sin(a), Z_ROMP), (2.02 * math.cos(a), 2.02 * math.sin(a), Z_BAND + 0.02)], 0.022, 6))
    put("toren", "ijzer", btube([(1.92 * math.cos(t), 1.92 * math.sin(t), Z_ROMP + 0.06) for t in [i * math.tau / 40 for i in range(41)]], 0.018, 5))   # rail
    # dak: leien, licht bolle klok-vorm
    lathe_course("dak", "leien", [(R_DAK, Z_BAND), (2.15, 4.3), (1.72, 4.78), (1.28, 5.28), (0.95, 5.64), (0.72, Z_TOP_DAK)], 56, 0.11, 0.025)
    put("dak", "leien", blathe([(R_DAK - 0.02, Z_BAND - 0.05), (R_DAK - 0.02, Z_BAND - 0.01), (R_KERN, Z_BAND - 0.01), (R_KERN, Z_BAND - 0.05)], 56))   # onderkant overstek
    put("dak", "lood", blathe([(0, Z_TOP_DAK - 0.1), (0.74, Z_TOP_DAK - 0.1), (0.74, 6.12), (0.62, 6.15), (0.6, 6.3), (0, 6.3)], 32))   # loden trommels
    # klokkenstoel: 4 krulstijlen, klokje, kegeldakje, bol + vaan (Slimme-Toon.jpg)
    for k in range(4):
        a = k * math.tau / 4 + math.tau / 8; c, s = math.cos(a), math.sin(a)
        pts = [(0.5 * c, 0.5 * s, 6.3), (0.36 * c, 0.36 * s, 6.55), (0.38 * c, 0.38 * s, 6.8), (0.46 * c, 0.46 * s, 7.0)]
        put("stoel", "lood", btube(pts, 0.025, 6))
        put("stoel", "lood", btube([(0.5 * c + 0.12 * math.cos(t) * c, 0.5 * s + 0.12 * math.cos(t) * s, 6.42 + 0.12 * math.sin(t)) for t in [i * math.pi / 6 for i in range(-3, 10)]], 0.018, 5))
    put("stoel", "brons", blathe([(0, 6.48), (0.07, 6.48), (0.1, 6.55), (0.12, 6.72), (0.2, 6.84), (0.18, 6.87), (0, 6.87)], 20), TR(0, 0, 0))
    put("stoel", "ijzer", btube([(0, 0, 6.87), (0, 0, 7.0)], 0.02, 5))
    lathe_course("stoel", "pannen", [(0.6, 7.0), (0.42, 7.2), (0.2, 7.42), (0.02, 7.55)], 20, 0.06, 0.015)
    put("stoel", "goud", blathe([(0, 7.52), (0.05, 7.55), (0.06, 7.6), (0.05, 7.65), (0, 7.68)], 12))
    put("stoel", "ijzer", btube([(0, 0, 7.66), (0, 0, 7.95)], 0.01, 5))
    put("stoel", "ijzer", boutline([(0.0, 7.8), (0.26, 7.82), (0.3, 7.88), (0.24, 7.92), (0.0, 7.9)], -0.005, 0.01))   # vaantje
    # Slimme Toon (eenvoudig, zit op de krul aan de voorkant, trekt aan het touw)
    tx, ty = 0.0, -0.55
    put("toon", "toon_groen", blathe([(0, 0), (0.09, 0.02), (0.1, 0.18), (0.07, 0.26), (0, 0.27)], 10), TR(tx, ty, 6.42))
    put("toon", "huid", blathe([(0, 0), (0.06, 0.01), (0.07, 0.07), (0.05, 0.12), (0, 0.13)], 10), TR(tx, ty, 6.7))
    put("toon", "toon_rood", btube([(tx - 0.05, ty, 6.44), (tx - 0.06, ty - 0.2, 6.44), (tx - 0.06, ty - 0.24, 6.32)], 0.035, 6))
    put("toon", "toon_rood", btube([(tx + 0.05, ty, 6.44), (tx + 0.06, ty - 0.2, 6.44), (tx + 0.06, ty - 0.24, 6.32)], 0.035, 6))
    put("toon", "toon_groen", btube([(tx + 0.08, ty, 6.62), (tx + 0.1, ty + 0.2, 6.78), (tx + 0.04, ty + 0.4, 6.75)], 0.025, 6))
    put("toon", "toon_rood", blathe([(0, 0), (0.07, 0), (0.02, 0.14), (0, 0.15)], 8), TR(tx, ty, 6.82))
    put("toon", "rood", btube([(tx, ty, 6.94), (tx + 0.08, ty + 0.08, 7.02), (tx + 0.18, ty + 0.1, 7.0)], 0.018, 5))
    put("toon", "ijzer", btube([(tx + 0.04, ty + 0.4, 6.75), (0.0, 0.0, 6.72)], 0.004, 4))
    # uurwerk op de voorkant (-Y): kast, kroonlijst, wijzerplaat (atlas), gouden wijzers
    yk = -math.sqrt(R_ROMP ** 2 - 0.75 ** 2)                              # romp-oppervlak aan de rand van de kast
    put("klok", "klokhout", bz(-0.75, 0.75, yk - 0.14, yk + 0.4, KZ0, KZ1))
    put("klok", "klokhout", bz(-0.82, 0.82, yk - 0.2, yk + 0.4, KZ1, KZ1 + 0.08, 0.01))
    put("klok", "klokhout", bz(-0.79, -0.6, yk - 0.18, yk + 0.4, KZ0 - 0.04, KZ0 + 0.02)); put("klok", "klokhout", bz(0.6, 0.79, yk - 0.18, yk + 0.4, KZ0 - 0.04, KZ0 + 0.02))
    bm = bmesh.new(); yf = yk - 0.141
    quad_uv(bm, [(-0.75, yf, KZ0), (0.75, yf, KZ0), (0.75, yf, KZ1), (-0.75, yf, KZ1)], [(0, 0), (1, 0), (1, 1), (0, 1)])
    uv_rect_object("BAKE_klok", bm, os.path.join(ROOT, "textures", "MK_klok_kleur.png"), "MAT_klokplaat")
    zc = (KZ0 + KZ1) / 2; yh = yf - 0.02
    put("klok", "goud", blathe([(0, 0), (0.06, 0), (0.06, 0.02), (0, 0.03)], 12), Matrix.Translation((0, yh + 0.01, zc)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    for ang, ln, w in ((-60, 0.34, 0.045), (40, 0.5, 0.03)):              # uur- en minuutwijzer (2 over 10 zoals Magischeklokklok)
        a = math.radians(ang); tip = (ln * math.sin(a), zc + ln * math.cos(a))
        nx, nz = math.cos(a) * w, -math.sin(a) * w
        put("klok", "goud", boutline([(-nx * 0.5, zc - nz * 0.5), (tip[0] * 0.7 - nx, zc + (tip[1] - zc) * 0.7 - nz), (tip[0], tip[1]), (tip[0] * 0.7 + nx, zc + (tip[1] - zc) * 0.7 + nz), (nx * 0.5, zc + nz * 0.5)], yh - 0.012, 0.012))
    # ruitertjes: 8 dubbelzijdige alpha-plaatjes op de rail (Ruitertje0)
    bm = bmesh.new()
    for k in range(8):
        a = k * math.tau / 8; cx, cy = 1.9 * math.cos(a), 1.9 * math.sin(a); tx_, ty_ = -math.sin(a), math.cos(a)
        w, h = 0.52, 0.52; z0 = Z_ROMP + 0.02
        c = [(cx - tx_ * w / 2, cy - ty_ * w / 2, z0), (cx + tx_ * w / 2, cy + ty_ * w / 2, z0), (cx + tx_ * w / 2, cy + ty_ * w / 2, z0 + h), (cx - tx_ * w / 2, cy - ty_ * w / 2, z0 + h)]
        quad_uv(bm, c, [(0, 0), (1, 0), (1, 1), (0, 1)])                   # buitenkant (rijdt met de klok mee, kop vooruit)
        quad_uv(bm, c[::-1], [(0, 1), (1, 1), (1, 0), (0, 0)][::-1])
    uv_rect_object("BAKE_ruiter", bm, os.path.join(ROOT, "textures", "MK_ruiter_kleur.png"), "MAT_ruiter", alpha=True)
    # achterdeur (Achterdeklok.jpg): groene rondboogdeur aan de +Y-kant
    dp = arch_pts(0, 0, 0.9, 1.9, 10)
    put("toren", "hout", boutline(dp, 0, 0.06), TR(0, R_ROMP + 0.0, 0) @ Matrix.Rotation(math.pi, 4, "Z"))
    put("toren", "steen", band(dp, 0.12, 0.0, 0.05), TR(0, R_ROMP + 0.02, 0) @ Matrix.Rotation(math.pi, 4, "Z"))
    for k in range(16): coll_box(1.9 * math.cos(k * math.tau / 16), 1.9 * math.sin(k * math.tau / 16), 2.2, 0.85, 0.5, 4.4, math.degrees(k * math.tau / 16) + 90)
    # ================= MUREN =================
    for name, (p0, u, n, L) in ARMS.items():
        s0 = -4.2                                                          # loopt tot in de toren
        M = arm_M(name)
        put("muur_" + name, "stuc", bz(s0, L, 0, WALL_T, -0.45, WALL_H), M)
        put("muur_" + name, "stuc", bz(L - 0.05, L + 0.25, -0.12, WALL_T + 0.12, -0.45, WALL_H + KANT_H + 0.05), M)   # eindpijler
        put("muur_" + name, "stuc", bz(L - 0.1, L + 0.3, -0.17, WALL_T + 0.17, WALL_H + KANT_H + 0.05, WALL_H + KANT_H + 0.12, 0.01), M)
        s = 0.9                                                            # kantelen (vanaf de toren)
        while s + KANT_W < L - 0.1:
            put("muur_" + name, "stuc", bz(s, s + KANT_W, 0, WALL_T, WALL_H - 0.02, WALL_H + KANT_H), M)
            s += KANT_W + KANT_GAP
        for hs in HERAUT_S[name]:                                          # lisenen + sokkels + schildjes
            hp = p0 + u * hs + n * 0.49; HERAUTEN.append([round(hp.x, 3), round(hp.y, 3), 0.43, round(math.degrees(math.atan2(n.y, n.x)), 2), name])
            put("muur_" + name, "stuc", bz(hs - 0.35, hs + 0.35, -0.12, 0.05, -0.45, WALL_H + KANT_H), M)
            put("sokkels", "baksteen", bz(hs - 0.36, hs + 0.36, -0.86, -0.12, -0.45, 0.35), M)
            put("sokkels", "steen", bz(hs - 0.4, hs + 0.4, -0.9, -0.1, 0.35, 0.43, 0.01), M)
            sh = [(hs + 0.42, 2.15), (hs + 0.72, 2.15), (hs + 0.71, 1.93), (hs + 0.65, 1.8), (hs + 0.57, 1.74), (hs + 0.49, 1.8), (hs + 0.43, 1.93)]
            put("schildjes", "rood", boutline(sh, -0.17, 0.05), M)
            put("schildjes", "goud", band(sh + [sh[0]], 0.012, -0.175, 0.02), M)
            lel = [(hs + 0.57, 2.08), (hs + 0.6, 2.0), (hs + 0.64, 1.95), (hs + 0.6, 1.93), (hs + 0.57, 1.82), (hs + 0.54, 1.93), (hs + 0.5, 1.95), (hs + 0.54, 2.0)]
            put("schildjes", "goud", boutline(lel, -0.185, 0.015), M)
        # gracht: natuurlijk slootje (Herauten-okt2009): geen bak of losse stenen; terrein vormt de oever (uitgegraven in Studio),
        # hier alleen een donker modderbed en een waterspiegel met afgeronde koppen die iets onder de oever ligt
        g0, g1 = 1.2, L - 0.4
        if name == "W": put("gracht", "bodem", bz(g0 - 0.3, g1 + 0.3, -2.6, -0.7, -0.5, -0.42), M)
        wbm = bmesh.new(); ring = []
        for k in range(40 if name == "W" else 0):    # gracht alleen langs de westmuur (overzicht-okt2009)                                                    # stadionvorm: rechte zijden, ronde koppen
            ang = k * math.tau / 40; ca, sa = math.cos(ang), math.sin(ang)
            sx = (g1 if ca > 0 else g0) + ca * 0.6; ty = -1.65 + sa * 0.6
            ring.append(wbm.verts.new((sx, ty, -0.2)))
        if ring: wbm.faces.new(ring); put("gracht", "water", wbm, M)
        # botsing: muur (hoog, niet erover) + grachtrand
        c = p0 + u * ((s0 + L) / 2) - n * (WALL_T / 2); ang = math.degrees(math.atan2(u.y, u.x))
        coll_box(c.x, c.y, 2.0, L - s0, WALL_T + 0.1, 4.0, ang)
    # ================= HERAUTENPLEIN v3 (MagischeKloktotaal, Herauten-overzicht-okt2009, Boekloc 2016, Herautenplein1974) =================
    # groot grindveld in een band langs beide muren (t 2.6..7.5): achter een laag muurtje van ruwe natuursteen evenwijdig aan de kasteelmuren,
    # bij de toren in een bocht (Boekloc), aan de westkant uitlopend op de gracht; voor een buxushaag evenwijdig aan het pad (chevron, de 'Z'
    # op de totaalfoto) met aan de binnenkant lange lage groene bankjes; rieten manden op het grind; galgenlantaarn op de hoek bij de noordingang.
    # Ingangen: het noordeinde (naar de Prinsenpoort/het pad) open, en aan het westeinde tussen haag en grachtmuurtje.
    p0N, uN, nN, _ = ARMS["N"]; p0W, uW, nW, _ = ARMS["W"]
    NP = lambda s_, t_: p0N + uN * s_ + nN * t_
    WP = lambda s_, t_: p0W + uW * s_ + nW * t_
    def snijpunt(tn, tw):                                                     # punt met afstand tn tot de noordmuur en tw tot de westmuur
        a11, a12, b1 = nN.x, nN.y, tn + p0N.dot(nN); a21, a22, b2 = nW.x, nW.y, tw + p0W.dot(nW)
        det = a11 * a22 - a12 * a21; return Vector(((b1 * a22 - a12 * b2) / det, (a11 * b2 - b1 * a21) / det))
    TB, TF, SNE, SWE = 2.6, 7.5, 12.0, 9.5                                     # achterrand, voorrand, eind noord, eind west
    # achterrand: noord -> bocht om de toren -> west (+ uitloop in de gracht)
    na, wa = NP(1.4, TB), WP(1.4, TB + 0.1)
    a0, a1 = math.atan2(na.y, na.x), math.atan2(wa.y, wa.x)
    if a1 < a0: a1 += math.tau
    if a1 - a0 > math.pi: a0, a1 = a1, a0 + math.tau
    arc_ = [Vector((math.cos(a0 + (a1 - a0) * k / 8), math.sin(a0 + (a1 - a0) * k / 8))) * (na.length + (wa.length - na.length) * k / 8) for k in range(9)]
    if (arc_[0] - na).length > 0.5: arc_ = arc_[::-1]
    back = [NP(SNE, TB), NP(7.0, TB)] + arc_ + [WP(5.0, TB + 0.1), WP(SWE, TB + 0.1), WP(SWE + 0.5, TB - 0.2), WP(SWE + 0.7, TB - 0.6)]
    C = snijpunt(TF, TF)
    front = [WP(SWE, TF), C, NP(SNE, TF)]
    # grind: band tussen achter- en voorrand (oor-snijden voor de concave chevron)
    poly = [NP(SNE, TB)] + back[1:-2] + [WP(SWE, TB + 0.1), WP(SWE, TF), C, NP(SNE, TF)]
    gb = bmesh.new(); gv = [gb.verts.new((q.x, q.y, 0.02)) for q in poly]; gf = gb.faces.new(gv)
    bmesh.ops.triangulate(gb, faces=[gf], ngon_method="EAR_CLIP"); put("plein", "klinker", gb)
    # muurtje van ruwe natuursteen: twee lagen blokken + afdekstenen, licht onregelmatig
    def stenen_muur(pts, h=0.5):
        for a_, b_ in zip(pts, pts[1:]):
            d_ = b_ - a_; L_ = d_.length; ang = math.degrees(math.atan2(d_.y, d_.x)); k = 0.0
            while k < L_:
                ln = min(RNG.uniform(0.32, 0.55), L_ - k + 0.05); q = a_ + d_.normalized() * (k + ln / 2)
                z = -0.05; lay = 0
                while z < h - 0.12:
                    hh = RNG.uniform(0.17, 0.25); off = RNG.uniform(-0.05, 0.05) if lay else 0
                    put("plein", "steen", bbox(ln + 0.03, RNG.uniform(0.36, 0.44), hh, 0, 0, 0, 0.045), TR(q.x + off * d_.normalized().x, q.y + off * d_.normalized().y, z + hh / 2, ang + RNG.uniform(-6, 6)))
                    z += hh - 0.01; lay += 1
                put("plein", "steen", bbox(ln + 0.06, 0.46, 0.12, 0, 0, 0, 0.05), TR(q.x, q.y, z + 0.05, ang + RNG.uniform(-5, 5)))
                k += ln
    stenen_muur(back)
    # lange lage groene bankjes langs de binnenkant van de voorrand (volgen de knik = de 'Z' van de totaalfoto)
    bank = [WP(SWE - 0.4, TF - 0.45), snijpunt(TF - 0.45, TF - 0.45), NP(SNE - 0.4, TF - 0.45)]
    for a_, b_ in zip(bank, bank[1:]):
        d_ = b_ - a_; L_ = d_.length; ang = math.degrees(math.atan2(d_.y, d_.x)); Mb = TR(a_.x, a_.y, 0, ang)
        put("bankjes", "hout", bz(0.0, L_, -0.22, 0.22, 0.42, 0.48, 0.01), Mb)                          # zitplank (doorlopend)
        nst = max(2, int(L_ / 1.6) + 1)
        for k in range(nst):
            xx = 0.2 + (L_ - 0.4) * k / (nst - 1); put("bankjes", "baksteen", bz(xx - 0.15, xx + 0.15, -0.17, 0.17, 0.0, 0.42), Mb)   # gemetselde poten
    # buxushaag aan de buitenkant (chevron) + westeinde (laat een ingang bij de gracht), noordeinde open
    haag_lijn = [WP(SWE + 0.35, TB + 2.3), WP(SWE + 0.35, TF + 0.45), snijpunt(TF + 0.45, TF + 0.45), NP(SNE - 0.2, TF + 0.45)]
    for a_, b_ in zip(haag_lijn, haag_lijn[1:]):
        d_ = b_ - a_; L_ = d_.length; ang = math.degrees(math.atan2(d_.y, d_.x))
        put("haag", "haag", bz(-0.25, L_ + 0.25, -0.28, 0.28, -0.05, 0.62, 0.07), TR(a_.x, a_.y, 0, ang))
    # rieten manden op het grind (totaalfoto: 4)
    for q in (NP(9.5, 5.2), NP(5.0, 5.4), WP(4.2, 5.6), WP(7.6, 5.0)):
        put("manden", "mand", blathe([(0, 0), (0.2, 0), (0.24, 0.42), (0.21, 0.42), (0.18, 0.04), (0, 0.04)], 16), TR(q.x, q.y, 0))
        put("manden", "mand", ring_band_bm(q, 0.24, 0.4, 0.45), None) if False else None
    # sprookjesboek in de bocht bij de toren, met de rug naar het muurtje (Boekloc)
    mid = arc_[4]; bq = mid * (1 + 0.6 / mid.length); ba = math.degrees(math.atan2(mid.y, mid.x)) - 90
    MB = TR(bq.x, bq.y, 0, ba)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.03, 6), MB); put("boek", "ijzer", bz(-0.25, 0.25, -0.2, 0.2, 0, 0.03), MB)
    put("boek", "kant_papier", bz(-0.36, 0.36, -0.24, 0.24, 0, 0.04), MB @ TR(0, 0, 0.85) @ Matrix.Rotation(math.radians(-25), 4, "X"))
    put("boek", "rood", bz(-0.38, 0.38, -0.26, 0.26, -0.02, 0.0), MB @ TR(0, 0, 0.85) @ Matrix.Rotation(math.radians(-25), 4, "X"))
    # galgenlantaarn op de hoek bij de noordingang, buiten de haag (totaalfoto links)
    lq = NP(SNE + 0.4, TF + 1.0); lx, ly = lq.x, lq.y; la = math.degrees(math.atan2(uN.y, uN.x))
    put("lantaarn", "paal", bz(lx - 0.09, lx + 0.09, ly - 0.09, ly + 0.09, 0, 3.3, 0.02))
    for sg in (-1, 1):
        ax_ = Vector((math.cos(math.radians(la)), math.sin(math.radians(la))))
        e_ = Vector((lx, ly)) + ax_ * sg * 0.8
        put("lantaarn", "paal", btube([(lx, ly, 3.0), (e_.x, e_.y, 3.0)], 0.05, 6))
        m_ = Vector((lx, ly)) + ax_ * sg * 0.45; put("lantaarn", "paal", btube([(lx + ax_.x * sg * 0.1, ly + ax_.y * sg * 0.1, 2.55), (m_.x, m_.y, 2.98)], 0.03, 5))
        c_ = Vector((lx, ly)) + ax_ * sg * 0.72
        put("lantaarn", "ijzer", btube([(c_.x, c_.y, 2.95), (c_.x, c_.y, 2.75)], 0.01, 4))
        put("lantaarn", "ijzer", blathe([(0, 2.72), (0.13, 2.68), (0.13, 2.66), (0.1, 2.64), (0.1, 2.36), (0.07, 2.32), (0, 2.3)], 6), TR(c_.x, c_.y, 0))
        put("lantaarn", "glaslamp", blathe([(0, 2.37), (0.085, 2.37), (0.085, 2.63), (0, 2.63)], 6), TR(c_.x, c_.y, 0))
        LAMPS_.append([round(c_.x, 2), round(c_.y, 2), 2.5])
    # rozenperk in het gras voorbij het westeinde (overzicht-okt2009)
    rc = WP(13.2, 5.6)
    put("perk", "bodem", bz(-1.9, 1.9, -1.0, 1.0, -0.05, 0.04), TR(rc.x, rc.y, 0, math.degrees(math.atan2(uW.y, uW.x))))
    PLEIN.update({"TB": TB, "TF": TF, "SNE": SNE, "SWE": SWE, "C": [round(C.x, 3), round(C.y, 3)], "perk": [round(rc.x, 3), round(rc.y, 3)], "lamp": [round(lx, 3), round(ly, 3)]})
    # front.jpg: toren ~13% smaller t.o.v. de muren (hoogtes kloppen) -> alleen in x/y schalen
    K = 0.87
    for (part, mat), bm in PARTS.items():
        if part in ("toren", "dak", "stoel", "toon", "klok"): bmesh.ops.scale(bm, vec=(K, K, 1), verts=bm.verts)
    def zmap(z):   # front.jpg (49.6 px/m op dakdiepte): romp tot 4.07, band 0.44, dak 1.77, rest schuift mee
        if z <= Z_ROMP: return z if z < 0 else z * 4.07 / Z_ROMP
        if z <= Z_BAND: return 4.07 + (z - Z_ROMP) * 0.44 / (Z_BAND - Z_ROMP)
        if z <= Z_TOP_DAK: return 4.51 + (z - Z_BAND) * 1.77 / (Z_TOP_DAK - Z_BAND)
        return 6.28 + (z - Z_TOP_DAK)
    for (part, mat), bm in PARTS.items():
        if part in ("toren", "dak", "stoel", "toon"):
            for v in bm.verts: v.co.z = zmap(v.co.z)
    for v in bpy.data.objects["BAKE_ruiter"].data.vertices: v.co.z = zmap(v.co.z)
    for nm in ("BAKE_klok", "BAKE_ruiter"):
        for v in bpy.data.objects[nm].data.vertices: v.co.x *= K; v.co.y *= K
    for c in COLL[:16]: c[0] *= K; c[1] *= K
    # ================= wegschrijven =================
    for (part, mat), bm in PARTS.items():
        ob = new_mesh_object(f"MK_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "herauten": HERAUTEN, "plein": PLEIN}, open(os.path.join(out, "klok_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "colliders", len(COLL),
                             "tris", sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
