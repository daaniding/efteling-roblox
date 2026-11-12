"""
08_extra: losse modellen rond de Sprookjesboom (Eftepedia: "rode eekhoorn, wild konijn, grote bonte specht"; weerstation achter de boom;
rododendrons bloeien paars, ref/eftepedia/Rodosb.jpg). Elk dier = gefuseerde massa's (voxel remesh + smooth, zoals Gijs), kleurvlakken
per face (Roblox kent geen vertexkleuren) en dan per materiaal gesplitst. Echte maten: specht 0.23 m, eekhoorn 0.22 m + staart 0.18 m,
konijn zittend 0.25 m hoog. Oorsprong = waar het dier steunt (poten / buikmidden), voorkant -Y.
Schrijft PR_SprookjesboomExtra.blend (collectie LOW): objecten met prefix SPECHT_, EEKHOORN_, KONIJN_, TROS_, WEER_.
Gebruik: Blender -b -P 08_extra.py -- --outdir <map>
"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, Euler, noise

PHASE = "08_extra"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix, "Euler": Euler,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})
rnd = random.Random(12)


def M(name, rgb, rough=0.8):
    m = material("MAT_" + name, (*rgb, 1), rough); m.diffuse_color = (*rgb, 1); return m


def fuse(name, parts, voxel, it=8):
    ob = join_meshes(name, parts, "LOW")
    for p in parts: bpy.data.objects.remove(p, do_unlink=True)
    remesh_voxel(ob, voxel)
    sm = ob.modifiers.new("Smooth", "SMOOTH"); sm.factor = 0.7; sm.iterations = it
    apply_all_modifiers(ob)
    return ob


def paint_split(ob, prefix, rule, mats):
    """rule(center, normal) -> index in mats; splitst in één object per materiaal (prefix_<mat>)."""
    for m in mats: ob.data.materials.append(m)
    for p in ob.data.polygons:
        p.material_index = rule(p.center, p.normal)
    bm0 = bmesh.new(); bm0.from_mesh(ob.data)
    for mi, m in enumerate(mats):
        b = bm0.copy(); bmesh.ops.delete(b, geom=[f for f in b.faces if f.material_index != mi], context="FACES")
        if len(b.faces) == 0: b.free(); continue
        o = new_mesh_object(f"{prefix}_{m.name[4:]}", b, "LOW"); o.data.materials.clear(); assign(o, m); shade_smooth(o, math.radians(70))
    bm0.free(); bpy.data.objects.remove(ob, do_unlink=True)


def specht():
    """grote bonte specht, verticaal tegen de stam (+Y = stam), voeten op z 0 (Boom_specht.jpg)."""
    zw, wi, ro, sn = M("specht_zwart", (0.03, 0.03, 0.035), 0.5), M("specht_wit", (0.92, 0.90, 0.85), 0.6), M("specht_rood", (0.78, 0.06, 0.06), 0.5), M("specht_snavel", (0.30, 0.30, 0.32), 0.4)
    parts = [sphere("p_lijf", 0.045, "LOW", (0, -0.035, 0.09), u=24, v=12, scale=(0.85, 0.85, 1.55)),
             sphere("p_kop", 0.034, "LOW", (0, -0.055, 0.185), u=24, v=12, scale=(0.9, 1.0, 0.95)),
             sphere("p_nek", 0.03, "LOW", (0, -0.045, 0.15), u=16, v=8)]
    for s in (-1, 1):
        parts.append(sphere(f"p_vleugel{s}", 0.035, "LOW", (s * 0.03, -0.02, 0.09), u=16, v=8, scale=(0.45, 0.9, 1.9)))
    ob = fuse("SPECHT_lijf", parts, 0.004, 6)
    def rule(c, n):
        if c.z > 0.205 and c.y > -0.06 and c.y < -0.02: return 2                         # rode nekvlek
        if c.z < 0.03 and n.y < 0: return 2                                                 # rode onderstaartdekveren
        if c.z > 0.17 and n.y < -0.3 and abs(c.x) > 0.012: return 1                        # witte wangen
        if 0.07 < c.z < 0.13 and abs(c.x) > 0.034 and c.y > -0.04: return 1                 # witte schoudervlek
        if n.y < -0.4 and c.z < 0.16: return 1                                              # lichte buik
        return 0
    paint_split(ob, "SPECHT", rule, [zw, wi, ro])
    sn_ob = cylinder("SPECHT_snavel", 0.009, 0.045, "LOW", segments=8, radius_top=0.001, axis="Y", location=(0, -0.105, 0.19)); assign(sn_ob, sn)
    st = box("SPECHT_staart", (0.035, 0.012, 0.08), "LOW", (0, 0.0, 0.0)); st.rotation_euler.x = math.radians(-12); apply_transform(st); assign(st, zw)
    for s in (-1, 1):
        e = sphere(f"SPECHT_oog{s}", 0.006, "LOW", (s * 0.026, -0.072, 0.195), u=8, v=4); assign(e, zw)


def eekhoorn():
    """rode eekhoorn rechtop zittend, staart als S over de rug, pluimpjes op de oren; zit op z 0."""
    ro, wi, zw, nb = M("eekhoorn_rood", (0.66, 0.28, 0.09), 0.85), M("eekhoorn_buik", (0.93, 0.88, 0.78), 0.85), M("eekhoorn_oog", (0.02, 0.02, 0.02), 0.2), M("eekhoorn_neus", (0.15, 0.08, 0.06), 0.4)
    parts = [sphere("p_lijf", 0.055, "LOW", (0, 0, 0.075), u=24, v=12, scale=(0.8, 0.85, 1.3)),
             sphere("p_heup", 0.058, "LOW", (0, 0.015, 0.045), u=24, v=12, scale=(1.0, 1.0, 0.75)),
             sphere("p_kop", 0.036, "LOW", (0, -0.025, 0.165), u=24, v=12, scale=(0.9, 1.15, 0.9)),
             sphere("p_snuit", 0.017, "LOW", (0, -0.066, 0.156), u=16, v=8, scale=(0.9, 1.3, 0.85))]
    for s in (-1, 1):
        parts.append(sphere(f"p_oor{s}", 0.012, "LOW", (s * 0.022, -0.012, 0.205), u=10, v=6, scale=(0.6, 0.4, 1.6)))
        parts.append(sphere(f"p_voorpoot{s}", 0.008, "LOW", (s * 0.014, -0.052, 0.118), u=10, v=6, scale=(1, 1.2, 1.6)))
        parts.append(sphere(f"p_achterpoot{s}", 0.03, "LOW", (s * 0.035, -0.01, 0.03), u=16, v=8, scale=(0.7, 1.4, 0.8)))
    ob = fuse("EEKHOORN_lijf", parts, 0.0035, 6)
    paint_split(ob, "EEKHOORN", lambda c, n: 1 if (n.y < -0.5 and 0.05 < c.z < 0.14 and abs(c.x) < 0.035) else 0, [ro, wi])
    # staart: dikke S-vormige pluim
    pts = [(0, 0.06, 0.03), (0, 0.11, 0.07), (0, 0.12, 0.14), (0, 0.09, 0.20), (0, 0.10, 0.25), (0, 0.14, 0.27)]
    t = curve_tube("EEKHOORN_staartc", pts, 0.032, "LOW", taper_to=1.0)
    for i, p in enumerate(t.data.splines[0].points): p.radius = [0.6, 1.0, 1.15, 1.1, 0.95, 0.6][i]
    t2 = join_meshes("EEKHOORN_staart", [t], "LOW"); bpy.data.objects.remove(t, do_unlink=True)
    for v in t2.data.vertices: v.co += v.normal * 0.006 * noise.noise(v.co * 90)
    assign(t2, ro); shade_smooth(t2, math.radians(80))
    for s in (-1, 1):
        e = sphere(f"EEKHOORN_oog{s}", 0.007, "LOW", (s * 0.029, -0.038, 0.176), u=10, v=6); assign(e, zw)
        pl = cylinder(f"EEKHOORN_pluim{s}", 0.004, 0.025, "LOW", segments=6, radius_top=0.0005, location=(s * 0.022, -0.012, 0.235)); assign(pl, ro)
    nz = sphere("EEKHOORN_neus", 0.005, "LOW", (0, -0.088, 0.160), u=8, v=4); assign(nz, nb)


def konijn():
    """wild konijn zittend (grijsbruin, witte staart), oorsprong onder het midden."""
    br, wi, zw = M("konijn_bruin", (0.44, 0.36, 0.27), 0.9), M("konijn_wit", (0.92, 0.90, 0.86), 0.9), M("konijn_oog", (0.03, 0.02, 0.02), 0.2)
    parts = [sphere("p_lijf", 0.10, "LOW", (0, 0.04, 0.10), u=24, v=12, scale=(0.9, 1.15, 0.95)),
             sphere("p_borst", 0.07, "LOW", (0, -0.05, 0.12), u=24, v=12, scale=(0.9, 0.9, 1.1)),
             sphere("p_kop", 0.05, "LOW", (0, -0.10, 0.20), u=24, v=12, scale=(0.85, 1.15, 0.9)),
             sphere("p_snuit", 0.026, "LOW", (0, -0.15, 0.182), u=16, v=8, scale=(0.9, 1.0, 0.9))]
    for s in (-1, 1):
        parts.append(sphere(f"p_dij{s}", 0.055, "LOW", (s * 0.06, 0.06, 0.05), u=16, v=8, scale=(0.6, 1.3, 0.9)))
        parts.append(sphere(f"p_voet{s}", 0.022, "LOW", (s * 0.06, -0.01, 0.012), u=12, v=6, scale=(0.8, 2.8, 0.5)))
        parts.append(sphere(f"p_voorpoot{s}", 0.014, "LOW", (s * 0.028, -0.085, 0.03), u=10, v=6, scale=(1, 1.3, 1.4)))
    ob = fuse("KONIJN_lijf", parts, 0.005, 6)
    paint_split(ob, "KONIJN", lambda c, n: 1 if (n.z < -0.6) else 0, [br, wi])
    for s in (-1, 1):
        o = sphere(f"KONIJN_oor{s}", 0.022, "LOW", (s * 0.022, -0.07, 0.30), u=16, v=8, scale=(0.55, 0.3, 3.0))
        o.rotation_euler = (math.radians(-20), math.radians(s * 12), 0); apply_transform(o); assign(o, br)
        e = sphere(f"KONIJN_oog{s}", 0.011, "LOW", (s * 0.043, -0.105, 0.215), u=10, v=6); assign(e, zw)
    st = sphere("KONIJN_staart", 0.025, "LOW", (0, 0.16, 0.08), u=12, v=6); assign(st, wi)


def tros():
    """rododendron-bloemtros (Rodosb.jpg): 11 trompetbloempjes in een koepel, 0.15 m, lila met donkere vlek."""
    pe, hart = M("tros_lila", (0.66, 0.42, 0.74), 0.6), M("tros_hart", (0.42, 0.18, 0.40), 0.6)
    for k in range(11):
        a = k * 2.39996; incl = 0.0 if k == 0 else math.radians(35 + 30 * (k % 2))
        d = Vector((math.sin(incl) * math.cos(a), math.sin(incl) * math.sin(a), math.cos(incl)))
        f = profile_spin(f"TROS_bloem{k}", [(0.0, 0.0), (0.006, 0.0), (0.010, 0.02), (0.022, 0.034), (0.030, 0.038), (0.026, 0.040), (0.0, 0.030)], "LOW", steps=10)
        for v in f.data.vertices:   # vijf lobben
            ang = math.atan2(v.co.y, v.co.x); v.co.x *= 1 + 0.18 * math.cos(5 * ang); v.co.y *= 1 + 0.18 * math.cos(5 * ang)
        f.data.transform(Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4())
        f.location = d * 0.035 + Vector((0, 0, 0.02)); apply_transform(f); assign(f, pe)
    for k in range(3):
        h = sphere(f"TROS_hart{k}", 0.008, "LOW", (rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.02), 0.075), u=8, v=4); assign(h, hart)


def weerstation():
    """klein weerstation achter de boom (Eftepedia): paal met kruisarm, windmeter (3 bakjes) + windvaan, regenmeter, thermometerhutje."""
    me, wi, gr = M("weer_metaal", (0.55, 0.57, 0.58), 0.4), M("weer_wit", (0.90, 0.90, 0.88), 0.6), M("weer_groen", (0.15, 0.26, 0.18), 0.6)
    p = cylinder("WEER_paal", 0.03, 2.2, "LOW", segments=10, location=(0, 0, 1.1)); assign(p, me)
    a = cylinder("WEER_arm", 0.012, 0.8, "LOW", segments=8, axis="X", location=(0, 0, 2.1)); assign(a, me)
    for k in range(3):   # windmeter links
        ang = math.radians(120 * k); c = Vector((-0.4 + math.cos(ang) * 0.09, math.sin(ang) * 0.09, 2.24))
        cup = sphere(f"WEER_bakje{k}", 0.025, "LOW", tuple(c), u=12, v=6, scale=(1, 1, 1)); assign(cup, me)
        s_ = cylinder(f"WEER_spaak{k}", 0.004, 0.09, "LOW", segments=6, axis="X", location=(-0.4 + math.cos(ang) * 0.045, math.sin(ang) * 0.045, 2.24))
        s_.rotation_euler.z = ang; apply_transform(s_); assign(s_, me)
    as_ = cylinder("WEER_as", 0.006, 0.14, "LOW", segments=6, location=(-0.4, 0, 2.17)); assign(as_, me)
    v = box("WEER_vaan", (0.18, 0.005, 0.07), "LOW", (0.45, 0, 2.22)); assign(v, me)
    vs = cylinder("WEER_vaanas", 0.005, 0.14, "LOW", segments=6, location=(0.4, 0, 2.17)); assign(vs, me)
    # thermometerhutje (Stevenson): wit kastje op vier pootjes, rechts naast de paal
    h = box("WEER_hut", (0.38, 0.30, 0.42), "LOW", (0.7, 0.2, 1.31)); assign(h, wi)
    for i in range(6):
        l = box(f"WEER_lamel{i}", (0.39, 0.012, 0.025), "LOW", (0.7, 0.2 - 0.152, 1.14 + i * 0.065)); assign(l, wi)
    d = box("WEER_dak", (0.46, 0.38, 0.03), "LOW", (0.7, 0.2, 1.54)); assign(d, wi)
    for sx in (-1, 1):
        for sy in (-1, 1):
            leg = box(f"WEER_poot{sx}{sy}", (0.035, 0.035, 1.1), "LOW", (0.7 + sx * 0.16, 0.2 + sy * 0.12, 0.55)); assign(leg, gr)
    r = cylinder("WEER_regenmeter", 0.08, 0.32, "LOW", segments=16, location=(-0.6, 0.1, 0.96)); assign(r, wi)
    rp = cylinder("WEER_regenpaal", 0.025, 0.8, "LOW", segments=8, location=(-0.6, 0.1, 0.4)); assign(rp, gr)


if __name__ == "__main__":
    a = argv_after_dashes(); od = a[a.index("--outdir") + 1]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    specht(); eekhoorn(); konijn(); tros(); weerstation()
    os.makedirs(od, exist_ok=True)
    save_master(os.path.join(od, "PR_SprookjesboomExtra.blend"))
    n = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
    log("objecten", len(bpy.data.objects), "tris", n)
