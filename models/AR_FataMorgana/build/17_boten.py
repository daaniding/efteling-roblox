"""17_boten: stilliggende sloepen in de instaphal (Daan: stap 4; nog GEEN beweging).
Naar de video's (2025 POV 31-58 s): rode romp met een witte sierband en gouden rand langs de bovenkant, opgekrulde puntige voor- en
achtersteven, witte binnenkant met vijf witte banken met rugleuning, rode vloer. Eftepedia: veertien rode sloepen; hier drie: een
aan de draaischijf (oost), een in het zuidkanaal en een op weg naar de uitgang (noord). Maten: 6,0 x 1,9 m, diepgang 0,35 m.
Modelstelsel = 02/03. Deel "boten". Gebruik: blender --background --python build/17_boten.py"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py")
G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6)
G3 = G6["G3"]; T = G6["T"]
L, prisma = G3["L"], G3["prisma"]
OWNER = "phase:17_boten"
T["KLEUR"].update({"boot_rood": (0.6, 0.12, 0.1), "boot_wit": (0.95, 0.93, 0.88), "boot_vloer": (0.45, 0.08, 0.09), "goud": (0.87, 0.67, 0.32)})
T["UVS"].update({"boot_rood": 1.0, "boot_wit": 1.0, "boot_vloer": 1.0, "goud": 1.0})
EIGEN = ("boot_rood", "boot_wit", "boot_vloer", "goud")       # vlakken met een vaste normaal (geen recalc)
G = {r: bmesh.new() for r in EIGEN}

ZW = -3.2; LB, WB = 6.0, 1.9; ZB = ZW - 0.35; N = 28


def vlak(rol, pts, wil):
    bm = G[rol]; f = bm.faces.new([bm.verts.new(q) for q in pts]); f.normal_update()
    if f.normal.dot(wil) < 0: f.normal_flip()


def boot(cx, cy, koers):
    a = math.radians(koers); d = Vector((math.cos(a), math.sin(a), 0)); n = Vector((-d.y, d.x, 0))
    c = Vector((cx, cy, 0))
    def P(s, lat, z):                                      # s 0..1 langs de boot, lat dwars, z hoogte
        q = c + d * ((s - 0.5) * LB) + n * lat; return L(q.x, q.y) + Vector((0, 0, z))
    def w(s): return max(0.004, WB / 2 * math.sin(math.pi * s) ** 0.5)
    def zt(s): return ZW + 0.55 + 0.55 * abs(2 * s - 1) ** 5        # opgekrulde steven
    ss = [k / N for k in range(N + 1)]
    for s0, s1 in zip(ss, ss[1:]):
        for kant in (1, -1):
            # buitenkant: kim (schuin) en zijkant; witte sierband en gouden rand er net buiten
            for (l0, z0, l1, z1, rol, uit) in ((0.6, ZB, 1.0, ZB + 0.3, "boot_rood", 0.0), (1.0, ZB + 0.3, 1.0, None, "boot_rood", 0.0)):
                pa = P(s0, kant * w(s0) * l0, z0); pb = P(s1, kant * w(s1) * l0, z0)
                pc = P(s1, kant * w(s1) * l1, z1 if z1 is not None else zt(s1)); pd = P(s0, kant * w(s0) * l1, z1 if z1 is not None else zt(s0))
                vlak(rol, [pa, pb, pc, pd], n * kant + Vector((0, 0, -0.3)))
            for (dz0, dz1, rol, e) in ((-0.36, -0.13, "boot_wit", 0.012), (-0.13, -0.04, "goud", 0.02)):
                pa = P(s0, kant * (w(s0) + e), zt(s0) + dz0); pb = P(s1, kant * (w(s1) + e), zt(s1) + dz0)
                pc = P(s1, kant * (w(s1) + e), zt(s1) + dz1); pd = P(s0, kant * (w(s0) + e), zt(s0) + dz1)
                vlak(rol, [pa, pb, pc, pd], n * kant)
            # binnenkant wit (normaal naar binnen) en gouden boord bovenop; voor- en achterdekje dicht
            wi0, wi1 = max(0.01, w(s0) - 0.07), max(0.01, w(s1) - 0.07)
            if s0 < 0.12 or s1 > 0.88:
                vlak("boot_wit", [P(s0, 0, zt(s0) - 0.02), P(s1, 0, zt(s1) - 0.02), P(s1, kant * w(s1), zt(s1) - 0.02), P(s0, kant * w(s0), zt(s0) - 0.02)], Vector((0, 0, 1)))
                continue
            vlak("boot_wit", [P(s0, kant * wi0, ZB + 0.25), P(s1, kant * wi1, ZB + 0.25), P(s1, kant * wi1, zt(s1)), P(s0, kant * wi0, zt(s0))], -n * kant)
            vlak("goud", [P(s0, kant * wi0, zt(s0)), P(s1, kant * wi1, zt(s1)), P(s1, kant * w(s1), zt(s1)), P(s0, kant * w(s0), zt(s0))], Vector((0, 0, 1)))
        vlak("boot_rood", [P(s0, -0.6 * w(s0), ZB), P(s1, -0.6 * w(s1), ZB), P(s1, 0.6 * w(s1), ZB), P(s0, 0.6 * w(s0), ZB)], Vector((0, 0, -1)))
        wi0, wi1 = max(0.01, w(s0) - 0.07), max(0.01, w(s1) - 0.07)
        vlak("boot_vloer", [P(s0, -wi0, ZB + 0.25), P(s1, -wi1, ZB + 0.25), P(s1, wi1, ZB + 0.25), P(s0, wi0, ZB + 0.25)], Vector((0, 0, 1)))
    for se in (0.12, 0.88):                                              # schotje onder het dekje naar het bankengedeelte
        b = max(0.01, w(se) - 0.07); naar = d * (1 if se < 0.5 else -1)
        vlak("boot_wit", [P(se, -b, ZB + 0.25), P(se, b, ZB + 0.25), P(se, b, zt(se) - 0.02), P(se, -b, zt(se) - 0.02)], naar)
    # vijf banken met rugleuning (wit), de leuning naar de achtersteven
    for s in (0.24, 0.36, 0.48, 0.60, 0.72):
        b = w(s) - 0.09; zb_ = ZB + 0.25
        def doos(sa, sb, z0, z1):
            pts = [P(sa, -b, 0), P(sb, -b, 0), P(sb, b, 0), P(sa, b, 0)]
            for q in pts: q.z = 0.0
            prisma("boot_bank", pts, z0, z1)
        doos(s - 0.035, s + 0.035, zb_ + 0.36, zb_ + 0.42)              # zitting
        doos(s - 0.06, s - 0.035, zb_ + 0.42, zb_ + 0.85)               # rugleuning
        doos(s - 0.03, s + 0.03, zb_, zb_ + 0.36)                      # voet


def objecten():
    col = bpy.data.collections.get("LOW") or bpy.data.collections.new("LOW")
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for rol, bm in list(G.items()) + [("boot_bank", T["G"]["boot_bank"])]:
        if not bm.faces: continue
        if rol == "boot_bank":
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        uvl = bm.loops.layers.uv.verify()
        for f in bm.faces:
            for lp in f.loops: lp[uvl].uv = (lp.vert.co.x, lp.vert.co.z)
        me = bpy.data.meshes.new("FM_boten_" + rol); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("FM_boten_" + rol, me); o["owner"] = OWNER; o["rol"] = rol; o["deel"] = "boten"
        m = bpy.data.materials.get("FM_" + rol) or bpy.data.materials.new("FM_" + rol)
        m.diffuse_color = (*T["KLEUR"].get(rol, (0.95, 0.93, 0.88)), 1); me.materials.append(m); col.objects.link(o)


def main():
    bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]: bpy.data.objects.remove(o)
    T["G"]["boot_bank"] = bmesh.new(); T["KLEUR"]["boot_bank"] = (0.95, 0.93, 0.88)
    C0 = (6.3, -335.8)
    boot(C0[0] + 8.65 * math.cos(math.radians(-30)), C0[1] + 8.65 * math.sin(math.radians(-30)), 60)    # aan de schijf (oost)
    boot(C0[0] + 8.6 * math.cos(math.radians(-100)), C0[1] + 8.6 * math.sin(math.radians(-100)), -10)   # zuidkanaal
    boot(0.5, -326.0, 180)                                                                                # noord, naar de uitgang
    objecten()
    bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
    print("[17_boten] klaar:", sum(len(o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER), "vlakken")


main()
