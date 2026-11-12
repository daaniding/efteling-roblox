"""
05_paddenstoelen: twee paddenstoelen als losse game-ready modellen (effen kleuren, geen textures).
 - klein (front.jpg, aan de voet van de Sprookjesboom): bolle roze-rode hoed met grote witte stippen, witte steel, 0.36 m hoog.
 - muzikaal (reference/fotos/Muzikale_paddenstoel/1-4.jpg, 18 OSM-punten): brede lage glanzend rode hoed 0.86 m,
   ruwe witte korststippen, korte witte steel; totaal 0.52 m hoog (zitpaddenstoel).
Elk type een eigen .blend met collectie LOW, oorsprong = midden op de grond. Export met 09_export_roblox.py.
Gebruik: Blender -b -P 05_paddenstoelen.py -- --outdir <map>
"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, Euler, noise

PHASE = "05_paddenstoelen"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix, "Euler": Euler,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})


def cap_profile(R, z_rim, z_top, bulge, under):
    """hoedprofiel (r, z): van top over de rand naar de onderkant (plaatjes)."""
    pts = []
    for i in range(14):
        a = i / 13 * (math.pi / 2 + 0.35)
        r = R * math.sin(min(a, math.pi / 2)) * (1 + (0.04 if a > math.pi / 2 else 0))
        z = z_rim + (z_top - z_rim) * (math.cos(a) ** bulge if a <= math.pi / 2 else -0.15 * math.sin(a - math.pi / 2))
        pts.append((r, z))
    pts += [(R * 0.92, z_rim - 0.012), (R * 0.55, under), (R * 0.12, under + 0.01), (0.0, under + 0.012)]
    return pts


def spots(cap, n, rmin, rmax, mat, rnd, crust=False, lift=0.006):
    """witte stippen: platte blobjes op het hoedoppervlak (via straal van buiten op de hoed)."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new(); bm.from_mesh(cap.data); bm.transform(cap.matrix_world); bvh = BVHTree.FromBMesh(bm); bm.free()
    obs = []
    for k in range(n):
        # gelijkmatig verdeeld over de bovenkant (fibonacci), met jitter
        t = (k + 0.5) / n; inc = math.acos(1 - t * 0.95); az = k * 2.39996 + rnd.uniform(-0.3, 0.3)
        d = Vector((math.sin(inc) * math.cos(az), math.sin(inc) * math.sin(az), math.cos(inc)))
        hit = bvh.ray_cast(cap.matrix_world.translation + d * 3, -d)
        if hit[0] is None: continue
        r = rnd.uniform(rmin, rmax)
        s = sphere(f"spot{k}", r, "LOW", (0, 0, 0), u=12 if not crust else 16, v=6 if not crust else 8, scale=(1, 1, 0.28 if not crust else 0.38))
        if crust:   # ruwe korst (muzikale paddenstoel): rand grillig, oppervlak hobbelig
            for v in s.data.vertices:
                v.co *= 1 + 0.35 * noise.noise(v.co * 18 + Vector((k, 0, 0)))
        rot = Vector((0, 0, 1)).rotation_difference(hit[1]).to_matrix().to_4x4()
        s.data.transform(Matrix.Rotation(rnd.uniform(0, 6.28), 4, "Z"))
        s.data.transform(rot); s.location = hit[0] + hit[1] * lift
        apply_transform(s); obs.append(s)
    j = join_meshes(cap.name.replace("hoed", "stippen"), obs, "LOW")
    for o in obs: bpy.data.objects.remove(o, do_unlink=True)
    assign(j, mat); shade_smooth(j, math.radians(70))
    return j


def make(kind, outdir):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rnd = random.Random(3)
    if kind == "klein":
        name = "PR_PaddenstoelKlein"
        R, z_rim, z_top, bulge, under = 0.165, 0.20, 0.36, 0.55, 0.185
        stem = [(0.0, 0.0), (0.062, 0.0), (0.050, 0.03), (0.043, 0.10), (0.040, 0.19), (0.0, 0.19)]
        c_cap, c_spot, c_stem, c_gill = (0.86, 0.47, 0.46, 1), (0.95, 0.93, 0.90, 1), (0.93, 0.91, 0.86, 1), (0.88, 0.80, 0.70, 1)
        ns, rmin, rmax, crust, rough_cap = 11, 0.028, 0.045, False, 0.45
    else:
        name = "PR_PaddenstoelMuziek"
        R, z_rim, z_top, bulge, under = 0.43, 0.20, 0.52, 0.75, 0.185
        stem = [(0.0, 0.0), (0.14, 0.0), (0.125, 0.04), (0.118, 0.12), (0.115, 0.19), (0.0, 0.19)]
        c_cap, c_spot, c_stem, c_gill = (0.62, 0.15, 0.07, 1), (0.92, 0.90, 0.85, 1), (0.86, 0.83, 0.75, 1), (0.80, 0.74, 0.64, 1)
        ns, rmin, rmax, crust, rough_cap = 30, 0.045, 0.085, True, 0.30
    m_cap = material("MAT_hoed", c_cap, rough_cap); m_spot = material("MAT_stip", c_spot, 0.8)
    m_stem = material("MAT_steel", c_stem, 0.75); m_gill = material("MAT_plaatjes", c_gill, 0.85)
    for m in (m_cap, m_spot, m_stem, m_gill):
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"); m.diffuse_color = b.inputs["Base Color"].default_value
    cap = profile_spin(f"{name}_hoed", cap_profile(R, z_rim, z_top, bulge, under), "LOW", steps=40)
    # muzikaal: hoed iets scheef en hobbelig (foto 1 en 3)
    if kind != "klein":
        for v in cap.data.vertices:
            v.co.z += 0.03 * noise.noise(v.co * 3.0) + 0.02 * v.co.x
            v.co.x *= 1.04
    bm = bmesh.new(); bm.from_mesh(cap.data)
    gills = [f for f in bm.faces if f.calc_center_median().z < z_rim - 0.005 and f.normal.z < -0.3]
    bm.to_mesh(cap.data); bm.free()
    cap.data.materials.append(m_cap); cap.data.materials.append(m_gill)
    for p in cap.data.polygons:
        c = sum((cap.data.vertices[i].co for i in p.vertices), Vector()) / len(p.vertices)
        p.material_index = 1 if (c.z < z_rim - 0.005 and p.normal.z < -0.3) else 0
    shade_smooth(cap, math.radians(60))
    st = profile_spin(f"{name}_steel", stem, "LOW", steps=24); assign(st, m_stem); shade_smooth(st, math.radians(60))
    spots(cap, ns, rmin, rmax, m_spot, rnd, crust)
    # hoed in losse delen per materiaal (export groepeert op eerste materiaal)
    bm = bmesh.new(); bm.from_mesh(cap.data)
    gill_faces = [f for f in bm.faces if f.material_index == 1]
    gm = bmesh.new(); vm = {}
    for f in gill_faces:
        vs = [vm.setdefault(v.index, gm.verts.new(v.co)) for v in f.verts]
        gm.faces.new(vs)
    bmesh.ops.delete(bm, geom=gill_faces, context="FACES")
    bm.to_mesh(cap.data); bm.free()
    cap.data.materials.pop(index=1)
    g = new_mesh_object(f"{name}_plaatjes", gm, "LOW"); assign(g, m_gill)
    os.makedirs(outdir, exist_ok=True)
    save_master(os.path.join(outdir, f"{name}.blend"))
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
    log(name, "tris", tris)


if __name__ == "__main__":
    a = argv_after_dashes()
    od = a[a.index("--outdir") + 1]
    for k in ("klein", "muziek"):
        make(k, od)
