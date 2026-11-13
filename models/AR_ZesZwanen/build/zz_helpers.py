"""Gedeelde helpers De Zes Zwanen: Herberg/Assepoester-primitieven + gotische boog, kantelen, gelaagde kunstrots, prisma.
Gebruik in een bouwscript: exec(open(os.path.join(HERE, "zz_helpers.py")).read())"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
_hb = open(os.path.join(HERE, "..", "..", "AR_Herberg", "build", "03_forms.py")).read().split("def build(master):")[0]
exec(_hb)
WL = -0.35                                      # waterlijn (padniveau z = 0)


def prism_x(pts_yz, x0, x1):
    """profiel in (y, z) langs x geextrudeerd van x0 tot x1"""
    bm = bmesh.new(); a = [bm.verts.new((x0, y, z)) for y, z in pts_yz]; b = [bm.verts.new((x1, y, z)) for y, z in pts_yz]
    n = len(pts_yz)
    for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(a[::-1]); bm.faces.new(b)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def spits_pts(xc, z0, w, h, n=8):
    """gotische spitsboog-omtrek (open: linksonder -> top -> rechtsonder); boogstraal 0.85 w"""
    r = w * 0.85; ta = math.acos((w / 2 - r) / r); zs = z0 + h - r * math.sin(ta)
    cl = xc - w / 2 + r
    L = [(cl + r * math.cos(math.pi + (ta - math.pi) * i / n), zs + r * math.sin(math.pi + (ta - math.pi) * i / n)) for i in range(n + 1)]
    R_ = [(2 * xc - x, z) for x, z in L[::-1]][1:]
    return [(xc - w / 2, z0)] + L + R_ + [(xc + w / 2, z0)]


def gotisch_raam(xc, z0, w, h, y, part, M=None, licht=True, omlijst="stuc"):
    pts = spits_pts(xc, z0, w, h)
    put(part, "glasoranje" if licht else "venster", boutline(pts, y - 0.02, 0.06), M)
    put(part, omlijst, band(pts, 0.07, y - 0.06, 0.08), M)
    put(part, omlijst, bz(xc - w / 2 - 0.1, xc + w / 2 + 0.1, y - 0.1, y + 0.02, z0 - 0.08, z0, 0.01), M)
    put(part, "ijzer", bz(xc - 0.012, xc + 0.012, y - 0.035, y - 0.02, z0, z0 + h - 0.05), M)


def kantelen(pts, z_top, part, mat, d=0.35, merlon=0.42, gap=0.3, boog=True, M=None):
    """kantelenrij langs een open lijn in xy: boogfries (romaanse boogjes op consoles) + uitkraging + borstwering + merlons"""
    L = [Vector(p) for p in pts]
    for a, b in zip(L, L[1:]):
        t = (b - a); ln = t.length; t.normalize()
        ang = math.degrees(math.atan2(t.y, t.x))
        Mseg = Matrix.Translation((a.x, a.y, 0)) @ Matrix.Rotation(math.radians(ang), 4, "Z")
        if M is not None: Mseg = M @ Mseg
        put(part, mat, bz(-0.15, ln + 0.15, -0.18, d, z_top - 0.75, z_top - 0.42, 0.02), Mseg)
        if boog:
            x = 0.15
            while x < ln - 0.3:
                put(part, mat, band(arch_pts(x + 0.18, z_top - 1.05, 0.3, 0.32, 6), 0.05, -0.2, 0.06), Mseg); x += 0.42
            for i in range(int((ln - 0.3) / 0.42) + 1):
                x = 0.15 + 0.42 * i - 0.03
                put(part, mat, bz(x - 0.06, x + 0.06, -0.18, 0.0, z_top - 1.0, z_top - 0.75), Mseg)
        put(part, mat, bz(-0.15, ln + 0.15, -0.16, d - 0.05, z_top - 0.42, z_top - 0.3), Mseg)
        n_ = max(1, int((ln + 0.3) / (merlon + gap)))
        for i in range(n_):
            x = -0.15 + i * (ln + 0.3) / n_
            put(part, mat, bz(x, x + merlon, -0.16, d - 0.05, z_top - 0.3, z_top, 0.015), Mseg)


def inside(px, py, poly):
    c = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi: c = not c
        j = i
    return c


def rotsmassa(poly, hmax, front_edges=None, step=0.42, seed=1, cell=0.22, zmin=None, slope=1.25):
    """gelaagde kalksteen-kunstrots ('sedimentair kalkgesteente'): gesloten hoogteveld-raster, terrassen per laag, ruis.
    Buiten poly ligt het raster op zmin (onder water) zodat de rand een steile wand wordt; onderkant dicht."""
    zmin = WL - 0.4 if zmin is None else zmin
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    x0, y0 = min(xs) - 2 * cell, min(ys) - 2 * cell
    nx = int((max(xs) - min(xs)) / cell) + 5; ny = int((max(ys) - min(ys)) / cell) + 5
    E = front_edges or list(range(len(poly)))
    def dist(px, py):
        best = 1e9
        for i in E:
            ax, ay = poly[i]; bx, by = poly[(i + 1) % len(poly)]
            dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-9
            t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2)); best = min(best, math.hypot(px - ax - t * dx, py - ay - t * dy))
        return best
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=nx, y_segments=ny, size=0.5)
    for v in bm.verts:
        u_, w_ = v.co.x + 0.5, v.co.y + 0.5
        px, py = x0 + u_ * nx * cell, y0 + w_ * ny * cell
        if inside(px, py, poly):
            n1 = noise.noise(Vector((px * 0.35 + seed, py * 0.35, 0.3))); n2 = noise.noise(Vector((px * 1.3, py * 1.3 + seed, 1.7)))
            h = min(hmax, 0.25 + dist(px, py) * slope + n1 * 0.9)
            lay = math.floor(h / step); frac = h / step - lay
            h = max(zmin + 0.25, lay * step + step * min(1.0, frac * 3.5) * 0.35 + n2 * 0.05)          # terrassen: vlak + korte stap
        else:
            h = zmin
        v.co = Vector((px, py, h))
    rand = [e for e in bm.edges if e.is_boundary]
    ex = bmesh.ops.extrude_edge_only(bm, edges=rand)
    nv = [g for g in ex["geom"] if isinstance(g, bmesh.types.BMVert)]
    for v in nv: v.co.z = zmin - 0.3
    ne = [g for g in ex["geom"] if isinstance(g, bmesh.types.BMEdge) and all(vv in nv for vv in g.verts)]
    bmesh.ops.holes_fill(bm, edges=ne, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def snij(keys_filter, cutter_bms):
    """boolean DIFFERENCE (EXACT) van alle PARTS waarvoor keys_filter(key) waar is met de cutters"""
    cobs = []
    for i, c in enumerate(cutter_bms):
        cm = bpy.data.meshes.new("_cut%d" % i); c.to_mesh(cm); c.free(); co = bpy.data.objects.new("_cut%d" % i, cm); bpy.context.scene.collection.objects.link(co); cobs.append(co)
    for key in [k for k in PARTS if keys_filter(k)]:
        me_ = bpy.data.meshes.new("_s"); PARTS[key].to_mesh(me_); PARTS[key].free(); o_ = bpy.data.objects.new("_s", me_); bpy.context.scene.collection.objects.link(o_)
        for co in cobs:
            md = o_.modifiers.new("b", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = co; md.solver = "EXACT"
        bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = o_; o_.select_set(True)
        for m_ in list(o_.modifiers): bpy.ops.object.modifier_apply(modifier=m_.name)
        nb = bmesh.new(); nb.from_mesh(o_.data); PARTS[key] = nb; bpy.data.objects.remove(o_, do_unlink=True)
    for co in cobs: bpy.data.objects.remove(co, do_unlink=True)


def rotsblokken(poly, hmax, front_edges=None, seed=1, slope=1.4, kern_mat=True, vrij=None, voet=0.25, maat=1.0):
    """kunstrots van gestapelde hoekige kalksteenblokken (D6z-foto's): per laag (0.35-0.65 m) onregelmatige blokken 0.6-1.5 m,
    licht gekanteld en verschoven, gefacetteerd (afgeschuinde randen + verschoven hoekpunten), met donkere kern erachter.
    Hoogte-envelop zoals rotsmassa: 0.25 + afstand tot de voorranden * slope + ruis, max hmax. Geeft (blokken_bm, kern_bm)."""
    R = random.Random(seed); E = front_edges or list(range(len(poly)))
    def dist(px, py):
        best = 1e9
        for i in E:
            ax, ay = poly[i]; bx, by = poly[(i + 1) % len(poly)]
            dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-9
            t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2)); best = min(best, math.hypot(px - ax - t * dx, py - ay - t * dy))
        return best
    def env(px, py):
        return min(hmax, voet + dist(px, py) * slope + noise.noise(Vector((px * 0.35 + seed, py * 0.35, 0.3))) * 0.7)
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    blok = bmesh.new()
    z = WL - 0.45; lay = 0
    while z < hmax - 0.15:
        h = R.uniform(0.45, 0.85) * maat; cell = R.uniform(1.2, 1.8) * maat
        off = R.uniform(0, cell)
        y = min(ys) - cell + off * 0.5
        while y < max(ys) + cell:
            x = min(xs) - cell + (off if lay % 2 else 0)
            while x < max(xs) + cell:
                cx, cy = x + R.uniform(-0.15, 0.15) * cell, y + R.uniform(-0.15, 0.15) * cell
                if inside(cx, cy, poly) and env(cx, cy) > z + h * 0.5 and not (vrij and vrij(cx, cy, z + h / 2)):
                    sx, sy = cell * R.uniform(0.75, 1.2), cell * R.uniform(0.7, 1.15)
                    b = bbox(sx, sy, h * R.uniform(0.85, 1.1), 0, 0, 0, min(sx, sy, h) * R.uniform(0.2, 0.38))
                    for v in b.verts:                                                                   # facetten: hoekpunten verschuiven
                        v.co += Vector((R.uniform(-0.12, 0.12), R.uniform(-0.12, 0.12), R.uniform(-0.07, 0.07)))
                    M = (Matrix.Translation((cx, cy, z + h / 2)) @ Matrix.Rotation(R.uniform(-0.25, 0.25), 4, "Z")
                         @ Matrix.Rotation(R.uniform(-0.08, 0.08), 4, "X") @ Matrix.Rotation(R.uniform(-0.08, 0.08), 4, "Y"))
                    bmesh.ops.transform(b, matrix=M, verts=b.verts)
                    me_ = bpy.data.meshes.new("_t"); b.to_mesh(me_); b.free(); blok.from_mesh(me_); bpy.data.meshes.remove(me_)
                x += cell
            y += cell * 0.95
        z += h; lay += 1
    kern = rotsmassa(poly, hmax - 0.35, front_edges=front_edges, seed=seed, step=0.5, slope=slope * 0.85)
    for v in kern.verts:                                                                                 # kern iets terug: alleen in de voegen zichtbaar
        if v.co.z > WL: v.co.z -= 0.25
    return blok, kern
