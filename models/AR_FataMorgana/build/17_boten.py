"""17_boten: stilliggende sloepen in de instaphal (Daan: stap 4, "maak de boot mooier"; nog GEEN beweging).
Naar de video's (2025 POV 34/47 s): glanzend rode romp met ronde kim, crème boord langs de bovenkant met donkere sierplaatjes in een
gouden kader (vlechtwerkster, FM_bootplaket), dunne gouden lijn eronder, opgekrulde voor- en achtersteven met een rood knopje met
witte ring, dekjes voor en achter, witte banken met hoge ronde rugleuning en zijschotten met sierplaatjes, rode vloer.
Eftepedia: veertien rode sloepen; hier drie stil: aan de draaischijf (oost), in het zuidkanaal en in het noordkanaal.
Maten: 6,0 x 1,9 m, diepgang 0,35 m. Modelstelsel = 02/03. Deel "boten". Gebruik: blender --background --python build/17_boten.py"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]
L, lathe = G3["L"], G3["lathe"]
OWNER = "phase:17_boten"
KL = {"boot_rood": (0.6, 0.12, 0.1), "boot_wit": (0.95, 0.93, 0.88), "boot_vloer": (0.45, 0.08, 0.09), "goud": (0.87, 0.67, 0.32),
      "boot_bank": (0.95, 0.93, 0.88), "boot_plaket": (1, 1, 1)}
G = {r: bmesh.new() for r in KL}
EIGEN = ("boot_rood", "boot_wit", "boot_vloer", "goud", "boot_plaket")   # vaste normalen (geen recalc)

ZW = -3.2; LB, WB = 6.0, 1.9; ZB = ZW - 0.2; N = 40          # vloer (ZB + 0,25) net boven het Terrain-water


AS = []                                                          # as van de huidige boot (punt, richting) voor romp-normalen


def vlak(rol, pts, wil, uvs=None, romp=0):
    """romp = 1 (buitenkant) of -1 (binnenkant): normaal weg van / naar de lengteas van de boot (klopt ook bij de smalle punten)"""
    bm = G[rol]; f = bm.faces.new([bm.verts.new(q) for q in pts]); f.normal_update()
    if romp and AS:
        c = sum(pts, Vector()) / len(pts); o, dd = AS[0]
        voet = o + dd * (c - o).dot(dd); h = c - voet; h.z = 0.0          # horizontaal weg van de as (ook bij de smalle punten)
        wil = h * romp + (Vector((0, 0, -0.2)) if romp > 0 else Vector())
    if f.normal.dot(wil) < 0: f.normal_flip()
    if uvs:
        uvl = bm.loops.layers.uv.verify()
        for lp in f.loops:
            q = lp.vert.co; best = min(range(len(pts)), key=lambda i: (pts[i] - q).length); lp[uvl].uv = uvs[best]


def doos(rol, pts8):
    """gesloten blok uit 8 hoekpunten (onder 0-3, boven 4-7)"""
    bm = G[rol]; v = [bm.verts.new(q) for q in pts8]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): bm.faces.new([v[i] for i in f])


def boot(cx, cy, koers):
    a = math.radians(koers); d = Vector((math.cos(a), math.sin(a), 0)); n = Vector((-d.y, d.x, 0))
    c = Vector((cx, cy, 0))
    o0 = L(cx, cy); d1 = L(cx + d.x, cy + d.y) - o0; d1.z = 0; AS[:] = [(o0, d1.normalized())]
    def P(s, lat, z):                                      # s 0..1 langs de boot, lat dwars, z hoogte
        q = c + d * ((s - 0.5) * LB) + n * lat; return L(q.x, q.y) + Vector((0, 0, z))
    def w(s): return max(0.004, WB / 2 * math.sin(math.pi * s) ** 0.45)
    def zt(s): return ZW + 0.6 + 0.6 * abs(2 * s - 1) ** 5          # opgekrulde steven
    PROF = [(0.0, 0.0), (0.55, 0.0), (0.82, 0.1), (0.96, 0.24), (1.0, 0.36)]   # ronde kim: (fractie van w, hoogte boven ZB)
    ss = [k / N for k in range(N + 1)]
    for s0, s1 in zip(ss, ss[1:]):
        for kant in (1, -1):
            for (l0, h0), (l1, h1) in zip(PROF, PROF[1:]):
                vlak("boot_rood", [P(s0, kant * w(s0) * l0, ZB + h0), P(s1, kant * w(s1) * l0, ZB + h0), P(s1, kant * w(s1) * l1, ZB + h1), P(s0, kant * w(s0) * l1, ZB + h1)],
                     n * kant, romp=1)
            vlak("boot_rood", [P(s0, kant * w(s0), ZB + 0.36), P(s1, kant * w(s1), ZB + 0.36), P(s1, kant * w(s1), zt(s1) - 0.3), P(s0, kant * w(s0), zt(s0) - 0.3)], n * kant, romp=1)
            vlak("goud", [P(s0, kant * (w(s0) + 0.008), zt(s0) - 0.33), P(s1, kant * (w(s1) + 0.008), zt(s1) - 0.33), P(s1, kant * (w(s1) + 0.008), zt(s1) - 0.3), P(s0, kant * (w(s0) + 0.008), zt(s0) - 0.3)], n * kant, romp=1)
            vlak("boot_wit", [P(s0, kant * w(s0), zt(s0) - 0.3), P(s1, kant * w(s1), zt(s1) - 0.3), P(s1, kant * w(s1), zt(s1)), P(s0, kant * w(s0), zt(s0))], n * kant, romp=1)
            wi0, wi1 = max(0.01, w(s0) - 0.08), max(0.01, w(s1) - 0.08)
            # dikke crème boord bovenop (afgerond met een schuin vlakje)
            vlak("boot_wit", [P(s0, kant * wi0, zt(s0) + 0.03), P(s1, kant * wi1, zt(s1) + 0.03), P(s1, kant * w(s1), zt(s1)), P(s0, kant * w(s0), zt(s0))], Vector((0, 0, 1)) + n * kant * 0.3)
            if s0 < 0.12 or s1 > 0.88:                                  # dekjes voor en achter
                vlak("boot_wit", [P(s0, 0, zt(s0) + 0.01), P(s1, 0, zt(s1) + 0.01), P(s1, kant * wi1, zt(s1) + 0.03), P(s0, kant * wi0, zt(s0) + 0.03)], Vector((0, 0, 1)))
                continue
            vlak("boot_wit", [P(s0, kant * wi0, ZB + 0.25), P(s1, kant * wi1, ZB + 0.25), P(s1, kant * wi1, zt(s1) + 0.03), P(s0, kant * wi0, zt(s0) + 0.03)], -n * kant, romp=-1)
        wi0, wi1 = max(0.01, w(s0) - 0.08), max(0.01, w(s1) - 0.08)
        if 0.12 <= s0 and s1 <= 0.88:
            vlak("boot_vloer", [P(s0, -wi0, ZB + 0.25), P(s1, -wi1, ZB + 0.25), P(s1, wi1, ZB + 0.25), P(s0, wi0, ZB + 0.25)], Vector((0, 0, 1)))
    for se in (0.12, 0.88):                                              # schotje onder de dekjes
        b = max(0.01, w(se) - 0.08); naar = d * (1 if se < 0.5 else -1)
        vlak("boot_wit", [P(se, -b, ZB + 0.25), P(se, b, ZB + 0.25), P(se, b, zt(se) + 0.03), P(se, -b, zt(se) + 0.03)], naar)
    # sierplaatjes in de crème boord (gouden kader + donker plaatje met ster), elke ~0,75 m
    for k in range(7):
        s = 0.2 + k * 0.1
        for kant in (1, -1):
            zm = zt(s) - 0.15; ds = 0.11 / LB
            for (rol, h, e, uv) in (("goud", 0.125, 0.012, None), ("boot_plaket", 0.1, 0.018, True)):
                dd = h / LB * 1.0
                pts = [P(s - dd, kant * (w(s) + e), zm - h), P(s + dd, kant * (w(s) + e), zm - h), P(s + dd, kant * (w(s) + e), zm + h), P(s - dd, kant * (w(s) + e), zm + h)]
                vlak(rol, pts, n * kant, [(0, 0), (1, 0), (1, 1), (0, 1)] if uv else None)
    # rood knopje met witte ring op de punt van voor- en achtersteven
    for se in (0.0, 1.0):
        tip = P(se, 0, zt(se) + 0.03)
        lathe("boot_kop", [(0.0, 0.0), (0.05, 0.01), (0.075, 0.06), (0.07, 0.12), (0.04, 0.16), (0.0, 0.17)], tip.z, 12, (tip.x, tip.y))
        lathe("boot_kopring", [(0.055, -0.02), (0.065, -0.02), (0.065, 0.02), (0.055, 0.02)], tip.z + 0.01, 12, (tip.x, tip.y))
    # vijf banken: zitting, hoge rugleuning met ronde bovenkant, zijschotten met sierplaatje; leuning naar de achtersteven
    for s in (0.24, 0.355, 0.47, 0.585, 0.70):
        b = w(s) - 0.12; z0 = ZB + 0.25
        def blok(rol, sa, sb, la, lb, za, zb):
            doos(rol, [P(sa, la, za), P(sb, la, za), P(sb, lb, za), P(sa, lb, za), P(sa, la, zb), P(sb, la, zb), P(sb, lb, zb), P(sa, lb, zb)])
        blok("boot_bank", s - 0.03, s + 0.035, -b, b, z0, z0 + 0.42)                 # zitting met voet
        blok("boot_bank", s - 0.055, s - 0.03, -b, b, z0 + 0.42, z0 + 0.85)          # rugleuning
        rr = 0.12                                                               # ronde bovenkant rugleuning (halve cilinder dwars)
        for j in range(6):
            a0, a1 = math.pi * j / 6, math.pi * (j + 1) / 6
            sm = s - 0.0425
            p0 = (sm - math.cos(a0) * 0.0125, z0 + 0.85 + math.sin(a0) * 0.05); p1 = (sm - math.cos(a1) * 0.0125, z0 + 0.85 + math.sin(a1) * 0.05)
            vlak("boot_wit", [P(p0[0], -b, p0[1]), P(p1[0], -b, p1[1]), P(p1[0], b, p1[1]), P(p0[0], b, p0[1])], Vector((0, 0, 1)))
        for kant in (1, -1):                                                    # zijschot met sierplaatje aan de gangkant
            blok("boot_bank", s - 0.055, s + 0.035, kant * (b - 0.05), kant * b, z0 + 0.42, z0 + 0.62)
            zc = z0 + 0.6; h = 0.09
            pts = [P(s - 0.0425 - 0.015, kant * (b + 0.004), zc - h), P(s - 0.0425 + 0.015, kant * (b + 0.004), zc - h),
                   P(s - 0.0425 + 0.015, kant * (b + 0.004), zc + h), P(s - 0.0425 - 0.015, kant * (b + 0.004), zc + h)]
            vlak("boot_plaket", pts, n * kant, [(0, 0), (1, 0), (1, 1), (0, 1)])


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    extra = {r: T["G"][r] for r in ("boot_kop", "boot_kopring")}
    for rol, bm in list(G.items()) + list(extra.items()):
        if not bm.faces: continue
        if rol not in EIGEN:
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        uvl = bm.loops.layers.uv.verify()
        if rol != "boot_plaket":
            for f in bm.faces:
                for lp in f.loops: lp[uvl].uv = (lp.vert.co.x, lp.vert.co.z)
        me = bpy.data.meshes.new("FM_boten_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_boten_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "boten"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*KL.get(rol, (0.8, 0.1, 0.1)), 1); me.materials.append(m); col.objects.link(o)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    for r in ("boot_kop", "boot_kopring"): T["G"][r] = bmesh.new(); T["KLEUR"][r] = (0.7, 0.1, 0.1); T["UVS"][r] = 1.0
    C0 = (6.3, -335.8)
    boot(C0[0] + 8.65 * math.cos(math.radians(-30)), C0[1] + 8.65 * math.sin(math.radians(-30)), 60)    # aan de schijf (oost)
    boot(C0[0] + 8.6 * math.cos(math.radians(-100)), C0[1] + 8.6 * math.sin(math.radians(-100)), -10)   # zuidkanaal
    boot(0.5, -326.0, 180)                                                                                # noord, naar de uitgang
    objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[17_boten] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")


main()
