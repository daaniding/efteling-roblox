"""
03_forms_kruin: takken en bladkaarten van de Sprookjesboom (LOW = direct game-ready, geen bake nodig).
Takken groeien door vanaf het eind van de hoofdtakken (03_forms_stam.LIMBS) en vertakken binnen de kruin uit de
asset-brief: koepel 13 x 11 m, top 9.0 m, onderkant 4.6 m midden tot 3.2 m aan de rand (front_wide.jpg).
Bladkaarten: textures/bomen/blad_eik.png (echte bladtros, Roblox-asset 136241132523803; zelfde als Villa Volta-bomen).
Gebruik: Blender -b -P 03_forms_kruin.py -- --master <blend> [--seed 7]
"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, Euler, Quaternion

PHASE = "03_forms_kruin"
OWNER_TAG = "phase:" + PHASE
TEMPLATE = os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src = open(TEMPLATE).read().split("# ARGS AND FILE HANDLING", 1)[1]
_ns = {"bpy": bpy, "bmesh": bmesh, "sys": sys, "os": os, "math": math, "Vector": Vector, "Matrix": Matrix, "Euler": Euler,
       "PHASE": PHASE, "OWNER_TAG": OWNER_TAG}
exec(_src, _ns)
globals().update({k: v for k, v in _ns.items() if callable(v)})

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LEAF_TEX = os.path.join(REPO, "textures", "bomen", "blad_eik.png")
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location("stam_maten", os.path.join(HERE, "03_forms_stam.py"))
_src_stam = open(os.path.join(HERE, "03_forms_stam.py")).read()
LIMBS = eval(_src_stam.split("LIMBS = ", 1)[1].split("\n]\n", 1)[0] + "\n]")

CROWN_C = Vector((0.0, 0.3, 6.1)); CROWN_R = Vector((6.5, 5.5, 2.9))
CARD = 0.95                       # bladkaart (m); tros op de textuur is 0.4 m breed -> blaadjes ~8 cm


def floor_z(x, y):
    rr = math.hypot(x, y - 0.3)
    return max(3.2, 4.6 - 0.04 * rr * rr)


def inside(p, margin=1.0):
    q = Vector(((p.x - CROWN_C.x) / CROWN_R.x, (p.y - CROWN_C.y) / CROWN_R.y, (p.z - CROWN_C.z) / CROWN_R.z))
    return q.length < margin and p.z > floor_z(p.x, p.y) - 0.2


def pull_inside(p):
    """punt terug in de kruin trekken (ellipsoide, boven de holle onderkant)."""
    q = Vector(((p.x - CROWN_C.x) / CROWN_R.x, (p.y - CROWN_C.y) / CROWN_R.y, (p.z - CROWN_C.z) / CROWN_R.z))
    if q.length > 0.97:
        q = q * (0.97 / q.length)
        p = Vector((CROWN_C.x + q.x * CROWN_R.x, CROWN_C.y + q.y * CROWN_R.y, CROWN_C.z + q.z * CROWN_R.z))
    p.z = max(p.z, floor_z(p.x, p.y) + 0.1)
    return p


class Builder:
    def __init__(self):
        self.bm = bmesh.new(); self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.lbm = bmesh.new(); self.luv = self.lbm.loops.layers.uv.new("UVMap")
        self.tips = []

    def tube(self, a, b, ra, rb, sides):
        d = (b - a); L = d.length
        if L < 1e-4: return
        z = d / L; x = z.orthogonal().normalized(); y = z.cross(x)
        ring = []
        for p, r, v in ((a, ra, 0.0), (b, rb, L)):
            ring.append([self.bm.verts.new(p + (x * math.cos(2 * math.pi * i / sides) + y * math.sin(2 * math.pi * i / sides)) * r)
                         for i in range(sides)])
        for i in range(sides):
            j = (i + 1) % sides
            f = self.bm.faces.new((ring[0][i], ring[0][j], ring[1][j], ring[1][i]))
            for lp, (u, v) in zip(f.loops, ((i / sides, 0), ((i + 1) / sides, 0), ((i + 1) / sides, L), (i / sides, L))):
                lp[self.uv].uv = (u * 2 * math.pi * max(ra, rb) / 0.5, v / 0.5)   # 1 UV = 0.5 m schors

    def card(self, c, normal, size, rnd):
        n = normal.normalized(); t = n.orthogonal().normalized()
        t.rotate(Quaternion(n, rnd.uniform(0, 2 * math.pi))); b = n.cross(t)
        h = size / 2
        vs = [self.lbm.verts.new(c + (t * sx + b * sy) * h) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        f = self.lbm.faces.new(vs)
        for lp, uv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
            lp[self.luv].uv = uv

    def grow(self, p, d, r, depth, rnd, outward):
        """één tak: segment, dan 2-3 kinderen; twijgen (r < 0.035) worden bladtrossen."""
        if r < 0.028 or depth > 8:
            self.tips.append(p.copy()); return
        L = max(0.45, 2.6 * r ** 0.55)
        # richting: eigen richting + naar buiten/omhoog + klein beetje zwaartekracht bij de onderste takken
        want = (d * 1.0 + outward * 0.55 + Vector((0, 0, 0.25))).normalized()
        want.rotate(Euler((rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), rnd.uniform(-0.3, 0.3))))
        q = pull_inside(p + want * L)
        d2 = (q - p).normalized()
        sides = 10 if r > 0.20 else (7 if r > 0.08 else 5)
        self.tube(p, q, r, r * 0.86, sides)
        n = 3 if (r > 0.12 and rnd.random() < 0.35) else 2
        for k in range(n):
            ang = rnd.uniform(0.40, 0.75)
            axis = d2.orthogonal().normalized(); axis.rotate(Quaternion(d2, rnd.uniform(0, 2 * math.pi) + k * math.pi))
            cd = d2.copy(); cd.rotate(Quaternion(axis, ang))
            out2 = (q - CROWN_C); out2.z *= 0.6; out2 = out2.normalized()
            self.grow(q, cd, r * 0.86 * (0.72 if k == 0 else 0.62), depth + 1, rnd, out2)


def leaf_material():
    m = bpy.data.materials.get("MAT_leaf") or bpy.data.materials.new("MAT_leaf")
    if m.node_tree is None: m.use_nodes = True
    nt = m.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(LEAF_TEX, check_existing=True)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"]); nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.7
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    try: m.surface_render_method = "DITHERED"
    except Exception: pass
    m.diffuse_color = (0.30, 0.42, 0.22, 1)
    return m


def build(master, seed):
    open_master(master)
    clear_owned()
    for o in bpy.data.objects:
        if o.name == "BLK_crown" or o.name.startswith("BLK_limb"): o.hide_render = True; o.hide_set(True)
    rnd = random.Random(seed)
    B = Builder()
    for name, pts, r in LIMBS:
        a = Vector(pts[-2]); b = Vector(pts[-1]); d = (b - a).normalized()
        r_end = r * 0.62
        outward = (b - CROWN_C); outward.z *= 0.6; outward = outward.normalized()
        # twee tot drie hoofdvertakkingen per limb, zodat de kruin vol raakt
        for k in range(3 if name.startswith("C") or name == "Back" else 2):
            cd = d.copy(); cd.rotate(Euler((rnd.uniform(-0.45, 0.45), rnd.uniform(-0.45, 0.45), rnd.uniform(-0.6, 0.6))))
            B.grow(b, cd, r_end * (0.8 if k == 0 else 0.62), 0, rnd, outward)
    # extra binnentakken die de kruin van binnen vullen (vanaf de vork, front_wide.jpg)
    for k in range(6):
        a = rnd.uniform(0, 2 * math.pi)
        start = Vector((0.4 * math.cos(a), 0.35 * math.sin(a), 4.1))
        B.grow(start, Vector((math.cos(a) * 0.5, math.sin(a) * 0.5, 1.0)).normalized(), 0.13, 1, rnd,
               Vector((math.cos(a), math.sin(a), 0.6)).normalized())
    # bladtrossen: rond elke twijgpunt, kaart kijkt naar buiten met spreiding
    for tip in B.tips:
        out = (tip - CROWN_C); out = Vector((out.x / CROWN_R.x, out.y / CROWN_R.y, out.z / CROWN_R.z)).normalized()
        for k in range(rnd.randint(6, 9)):
            c = tip + Vector((rnd.gauss(0, 0.45), rnd.gauss(0, 0.45), rnd.gauss(0, 0.30)))
            c = pull_inside(c)
            nrm = (out + Vector((rnd.gauss(0, 0.6), rnd.gauss(0, 0.6), rnd.gauss(0.2, 0.5)))).normalized()
            B.card(c, nrm, CARD * rnd.uniform(0.8, 1.2), rnd)
    # kruinvulling: kaarten in een schil zodat er geen gaten zijn waar geen twijg eindigt (front_wide.jpg: dichte kruin)
    for k in range(1100):
        u = rnd.uniform(-1, 1); a = rnd.uniform(0, 2 * math.pi); s = rnd.uniform(0.84, 0.99)
        q = Vector((math.sqrt(1 - u * u) * math.cos(a), math.sqrt(1 - u * u) * math.sin(a), u)) * s
        c = Vector((CROWN_C.x + q.x * CROWN_R.x, CROWN_C.y + q.y * CROWN_R.y, CROWN_C.z + q.z * CROWN_R.z))
        if c.z < floor_z(c.x, c.y) + 0.9: continue          # onderin open: takken zichtbaar (front_wide.jpg)
        nrm = (q + Vector((rnd.gauss(0, 0.5), rnd.gauss(0, 0.5), rnd.gauss(0.15, 0.4)))).normalized()
        B.card(c, nrm, CARD * rnd.uniform(0.85, 1.25), rnd)
    br = new_mesh_object("GEO_takken", B.bm, "LOW")
    assign(br, material("MAT_branch", (0.47, 0.44, 0.39, 1), 0.85)); shade_smooth(br, math.radians(70))
    lv = new_mesh_object("GEO_blad", B.lbm, "LOW")
    assign(lv, leaf_material())
    log("takken tris", sum(len(p.vertices) - 2 for p in br.data.polygons), "bladkaarten", len(lv.data.polygons), "twijgen", len(B.tips))
    save_master(master)


if __name__ == "__main__":
    a = argv_after_dashes()
    build(a[a.index("--master") + 1], int(a[a.index("--seed") + 1]) if "--seed" in a else 7)
