"""03b_grot Sneeuwwitje: kunstrots-grot van de zeven dwergen met bakstenen ruines en beloopbare tunnel.
Modelcoordinaten als 03_forms. Vorm = OSM 60095997; ingang (10.42,-1.63) in een ruinemuur (Boekloc_Sneeuwwitje.jpg), uitgang (22.53,-7.16).
Rots (Sneeuwwitjegrot.jpg): grote ronde, gladde blokken met diepe naden, grijsgroen; ruinetorentje met klimop erboven (Grotvernieuwd.jpg).
Tunnel langs de buitenbocht (looproute); de toonzaal met de glazen kist (kijkramen) is interieur en komt later (Daan)."""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "03_forms.py")).read().split("def build(master):")[0]
_src = _src.replace('PHASE = "03_forms"', 'PHASE = "03b_grot"')
exec(_src)
RNG = random.Random(1952)
MATS.update({"rots": ((0.55, 0.57, 0.51, 1), 0.95), "ruine": ((0.66, 0.46, 0.34, 1), 0.92), "klimop": ((0.12, 0.25, 0.09, 1), 0.85), "pad": ((0.62, 0.58, 0.52, 1), 0.95)})
GROT = [(15.28, 2.26), (18.64, 1.76), (21.95, -1.88), (21.34, -2.42), (23.69, -6.61), (22.53, -7.16), (21.46, -7.62), (19.6, -6.57), (18.58, -6.61),
        (17.7, -6.55), (16.88, -6.4), (16.08, -6.16), (15.25, -5.83), (14.63, -5.5), (13.88, -5.0), (13.4, -4.59), (13.06, -4.28), (12.46, -3.62),
        (10.18, -2.96), (10.42, -1.63), (10.68, -0.31), (12.49, -0.51)]
PAD = [(8.8, -1.75), (10.6, -1.75), (12.6, -1.9), (14.5, -2.2), (16.4, -2.5), (18.4, -2.9), (20.3, -3.8), (21.6, -5.2), (22.5, -6.7), (23.0, -8.6)]   # midden van de rots: aan de buitenkant brak de rots open (Daan: gaten)
TW, TH = 2.2, 2.7          # tunnel breed (looproute ~1.5x) en hoog


def inside(px, py, poly):
    c = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi: c = not c
        j = i
    return c


def resample(pts, step):
    out = []
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b); n = max(1, int((b - a).length / step))
        for i in range(n): out.append(a + (b - a) * (i / n))
    out.append(Vector(pts[-1])); return out


def arch_tube(pts, w, h, z0=0.0, segs=10):
    """snijvolume: boogprofiel (recht tot h-w/2, halfrond erboven) langs een polylijn"""
    P = resample(pts, 0.4); bm = bmesh.new(); rings = []
    prof = [(-w / 2, z0 - 0.1), (w / 2, z0 - 0.1)] + [(w / 2 * math.cos(math.pi * k / segs), h - w / 2 + w / 2 * math.sin(math.pi * k / segs)) for k in range(segs + 1)]
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]); t = Vector((t.x, t.y)).normalized(); n = Vector((-t.y, t.x))
        rings.append([bm.verts.new((p.x + n.x * u, p.y + n.y * u, z)) for u, z in prof])
    m = len(prof)
    for A, B in zip(rings, rings[1:]):
        for k in range(m): bm.faces.new((A[k], A[(k + 1) % m], B[(k + 1) % m], B[k]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def segd(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def rock_mass():
    """kunstrots als hoogteveld binnen de OSM-vorm (Langnek-les): steile voorkant, grote platte blokken (voronoi) met diepe naden,
    blijft binnen de contour (drukt de ingangen niet dicht). Kolommen -> voxel remesh -> gladstrijken -> fijne ruis."""
    xs = [p[0] for p in GROT]; ys = [p[1] for p in GROT]; step = 0.2
    edges = [(a, b) for a, b in zip(GROT, GROT[1:] + GROT[:1]) if not max(a[0], b[0]) < 11.0]   # rand langs de ingangsmuur telt niet: rots vol tegen die muur (Daan); bij de uitgang wel (lage muur)
    padp = resample(PAD, 0.3)
    r = random.Random(5)
    cells = [(r.uniform(min(xs), max(xs)), r.uniform(min(ys), max(ys)), r.uniform(0.78, 1.12)) for _ in range(70)]
    bm = bmesh.new()
    x = min(xs)
    while x < max(xs):
        y = min(ys)
        while y < max(ys):
            if inside(x, y, GROT):
                d = min(segd((x, y), a, b) for a, b in edges)
                dd = sorted(((x - c[0]) ** 2 + (y - c[1]) ** 2, k) for k, c in enumerate(cells))
                f1, f2 = math.sqrt(dd[0][0]), math.sqrt(dd[1][0]); blk = cells[dd[0][1]][2]
                h = 3.9 * blk * (1 - math.exp(-d / 0.5)) * (0.88 + 0.12 * noise.noise(Vector((x * 0.35, y * 0.35, 0.3))))
                crev = max(0.0, 0.32 - (f2 - f1)) / 0.32
                dp = min((Vector((x, y)) - q).length for q in padp)
                if dp < TW / 2 + 0.9: h = max(h, TH + 0.95 + 0.5 * abs(noise.noise(Vector((x * 0.6, y * 0.6, 1.7)))) + 0.3 * blk)   # dikke laag rots boven de tunnel (gaten, Daan), niet vlak
                else: h -= 1.1 * crev ** 1.5
                if x < 11.2: h = min(h, 3.9)
                h = max(0.35, h)
                bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((x, y, (h - 0.3) / 2)) @ Matrix.Diagonal((step * 1.02, step * 1.02, h + 0.3, 1)))
            y += step
        x += step
    # voorkant: twee rijen grote bolle blokken langs de rand (Sneeuwwitjegrot.jpg), niet bij de in- en uitgang
    rr = random.Random(9)
    for e in resample(GROT + [GROT[0]], 1.05):
        if (e - Vector((10.42, -1.63))).length < 2.0 or (e - Vector((22.53, -7.16))).length < 2.0: continue
        cen = Vector((sum(xs) / len(xs), sum(ys) / len(ys))); inn = (cen - e).normalized()
        tng = Vector((-inn.y, inn.x))
        for row, (zc, rz) in enumerate(((0.95, rr.uniform(1.0, 1.35)), (2.35, rr.uniform(0.9, 1.3)))):
            c = e + inn * (0.45 + 0.25 * row) + tng * rr.uniform(-0.3, 0.3)
            sb = bmesh.new(); bmesh.ops.create_icosphere(sb, subdivisions=1, radius=1.0)   # grof: wordt na het samensmelten een hoekig-ronde plaat
            rx, ry = rr.uniform(0.8, 1.25), rr.uniform(0.5, 0.75)
            for v in sb.verts:
                q = v.co.copy(); v.co = Vector((q.x * rx, q.y * ry, q.z * rz))
            ang = math.atan2(tng.y, tng.x)
            bmesh.ops.rotate(sb, cent=(0, 0, 0), matrix=Matrix.Rotation(rr.uniform(-0.35, 0.35), 3, "X") @ Matrix.Rotation(rr.uniform(-0.3, 0.3), 3, "Y"), verts=sb.verts)
            bmesh.ops.rotate(sb, cent=(0, 0, 0), matrix=Matrix.Rotation(ang + rr.uniform(-0.3, 0.3), 3, "Z"), verts=sb.verts)
            bmesh.ops.translate(sb, vec=(c.x, c.y, zc), verts=sb.verts)
            me_ = bpy.data.meshes.new("_b"); sb.to_mesh(me_); sb.free(); bm.from_mesh(me_); bpy.data.meshes.remove(me_)
    me = bpy.data.meshes.new("SW_rots__rots"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("SW_rots__rots", me); col("FORMS").objects.link(ob); own(ob)
    remesh_voxel(ob, 0.09); apply_all_modifiers(ob)
    sm = ob.modifiers.new("glad", "SMOOTH"); sm.factor = 0.5; sm.iterations = 2; apply_all_modifiers(ob)
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.normal_update()
    for v in bm.verts:
        q = v.co * 0.9
        ridge = 1.0 - abs(noise.noise(q * 0.75 + Vector((7, 2, 5))))                       # plooien (Efteling-kunstrots)
        v.co += v.normal * (0.16 * ridge ** 3 - 0.06 + 0.05 * noise.noise(q * 2.2) + 0.02 * noise.noise(q * 6.0 + Vector((3, 1, 2))))
        if v.co.z < -0.05: v.co.z = -0.05
    bm.to_mesh(ob.data); bm.free()
    return ob


def ruin_wall(part, x0, y0, x1, y1, h, top_noise=1.0, thick=0.5, seed=0, z0=0.0):
    """bakstenen ruinemuur: een doorlopend stuk metselwerk met getrapt afgebrokkelde bovenrand (metselrij-stappen 6.8 cm)"""
    L = math.hypot(x1 - x0, y1 - y0); a = math.degrees(math.atan2(y1 - y0, x1 - x0)); M = TR(x0, y0, 0, a)
    rr = random.Random(seed); n = max(4, int(L / 0.24)); prof = [(0.0, z0)]
    for i in range(n):
        u0, u1 = L * i / n, L * (i + 1) / n
        hh = h - top_noise * 1.5 * max(0.0, noise.noise(Vector((u0 * 0.55 + seed * 3.1, 0.5, 0.2)))) - rr.uniform(0, 0.22)
        hh = max(z0 + 0.5, round(hh / 0.068) * 0.068)
        prof += [(u0, hh), (u1, hh)]
    prof.append((L, z0))
    put(part, "ruine", boutline(prof, -thick / 2, thick), M)
    return M, L


def ruin_tower(cx, cy, ro, ri, zb, htop, seed=0):
    """holle ruinetoren: ring van segmenten met gebroken, getrapte bovenrand"""
    segs = 30; rr = random.Random(seed)
    for k in range(segs):
        a0 = k * math.tau / segs; a1 = (k + 1) * math.tau / segs
        hh = htop - 1.5 * max(0.0, noise.noise(Vector((k * 0.45 + seed, 2.0, 0.0)))) - rr.uniform(0, 0.15)
        if k in (6, 7, 19): hh -= 1.0
        hh = round(hh / 0.068) * 0.068
        bm = bmesh.new()
        P = [(ro, a0), (ro, a1), (ri, a1), (ri, a0)]
        lo = [bm.verts.new((cx + rad * math.cos(a), cy + rad * math.sin(a), zb)) for rad, a in P]
        hi = [bm.verts.new((cx + rad * math.cos(a), cy + rad * math.sin(a), hh)) for rad, a in P]
        bm.faces.new(lo[::-1]); bm.faces.new(hi)
        for q in range(4): bm.faces.new((lo[q], lo[(q + 1) % 4], hi[(q + 1) % 4], hi[q]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("ruine", "ruine", bm)


def ivy_sheet(M, u0, u1, z0, z1, off, seed):
    """klimop: onregelmatig bladplakkaat net voor een muurvlak (lokaal y = -off), wordt in Roblox de haagtextuur"""
    bm = bmesh.new(); st = 0.14; nu = max(2, int((u1 - u0) / st)); nz = max(2, int((z1 - z0) / st)); grid = {}
    for i in range(nu + 1):
        for j in range(nz + 1):
            u = u0 + (u1 - u0) * i / nu; z = z0 + (z1 - z0) * j / nz
            m = noise.noise(Vector((u * 0.9 + seed, z * 0.9, seed * 0.3))) + 0.35 - 0.9 * ((z - z0) / (z1 - z0)) ** 2 * (1 if z > (z0 + z1) / 2 else 0)
            if m > 0.0: grid[(i, j)] = bm.verts.new((u, -off - 0.04 * max(0.0, noise.noise(Vector((u * 4, z * 4, seed)))), z))
    for i in range(nu):
        for j in range(nz):
            q = [grid.get(k) for k in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
            if all(q): bm.faces.new(q)
    if bm.faces: put("klimop", "klimop", bm, M)
    else: bm.free()


def build(master):
    open_master(master)
    TAG = "phase:03b_grot"     # eigen label: de hulpfuncties (uit Assepoester) labelen alles als phase:03_forms
    for o in [o for o in bpy.data.objects if o.get("owner") == TAG]: bpy.data.objects.remove(o, do_unlink=True)
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    COLL.clear(); LAMPS.clear()
    voor = set(o.name for o in bpy.data.objects)
    rots = rock_mass()
    cutters = [arch_tube(PAD, TW, TH)]
    # ruinemuur bij de ingang (Boekloc_Sneeuwwitje.jpg): 4.6 m, afgebrokkeld, rondboogtunnel (uitgesneden), nisje
    Mi, Li = ruin_wall("ruine", 10.0, -3.95, 10.3, 1.0, 4.7, 0.55, 0.6, seed=3)
    put("ruine", "steen", band(arch_pts(0, 0, TW, TH, 12), 0.12, -0.36, 0.06), TR(10.15, -1.8, 0, 92))
    put("ruine", "donker", bz(-0.25, 0.25, -0.33, -0.3, 2.9, 3.5), TR(10.2, -0.2, 0, 92))
    # lage ruinemuur van de ronde toren naar de grotingang (kasteel en grot zitten aan elkaar, Daan)
    Ml, Ll = ruin_wall("ruine", 6.9, 3.5, 10.3, 0.95, 1.9, 0.7, 0.45, seed=7)
    ang = math.atan2(0.95 - 3.5, 10.3 - 6.9); t = Vector((math.cos(ang), math.sin(ang))); nn = Vector((t.y, -t.x))
    for k in range(3):
        pp = Vector((6.9, 3.5)) + t * (1.2 + k * 0.9)
        COLL.append([round(pp.x, 3), round(pp.y, 3), 1.0, 1.0, 0.5, 2.0, round(math.degrees(ang), 2)])
    bc = Vector((6.9, 3.5)) + t * 2.1 + nn * 0.55
    put("ruine", "hout", bz(-0.6, 0.6, -0.2, 0.2, 0.42, 0.48), TR(bc.x, bc.y, 0, math.degrees(ang)))
    for u in (-0.45, 0.45): put("ruine", "steen", bz(u - 0.08, u + 0.08, -0.17, 0.17, 0, 0.42), TR(bc.x, bc.y, 0, math.degrees(ang)))
    # ruinemuur bij de uitgang (Sneeuwwitjegrot.jpg rechts)
    Mu, Lu = ruin_wall("ruine", 21.2, -8.3, 24.0, -6.4, 3.8, 1.1, 0.55, seed=11)
    # holle ruinetoren op de rots (Grotvernieuwd.jpg), raamgaten uitgesneden
    tc = Vector((15.6, -0.4))
    ruin_tower(tc.x, tc.y, 1.05, 0.78, 1.6, 7.0, seed=2)
    for a_, z_ in ((200, 4.7), (320, 5.1), (80, 4.5)):
        p_ = tc + Vector((math.cos(math.radians(a_)), math.sin(math.radians(a_)))) * 0.92
        cb = bz(-0.22, 0.22, -0.3, 0.3, z_, z_ + 0.8); bmesh.ops.transform(cb, matrix=TR(p_.x, p_.y, 0, a_ + 90), verts=cb.verts); cutters.append(cb)
    # klimop (Grotvernieuwd / Boekloc): plakkaten op toren en muren
    for k in range(9):
        a_ = k * 40 + 10
        Mt = TR(tc.x + 1.05 * math.cos(math.radians(a_)), tc.y + 1.05 * math.sin(math.radians(a_)), 0, a_ + 90)
        ivy_sheet(Mt, -0.45, 0.45, 2.6, 6.4 - 0.4 * (k % 3), 0.03, k)
    # (geen klimop op de muren: hing voor de ingang, Daan)
    # tunnelvloer + lampjes (lantaarn aan de ruinemuur, Sneeuwwitjegrot.jpg)
    padpoly = []
    P = resample(PAD, 0.5)
    L_, R_ = [], []
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]); t = Vector((t.x, t.y)).normalized(); nn = Vector((-t.y, t.x))
        L_.append((p.x + nn.x * TW / 2, p.y + nn.y * TW / 2)); R_.append((p.x - nn.x * TW / 2, p.y - nn.y * TW / 2))
    bm = bmesh.new(); vs = [bm.verts.new((x, y, 0.035)) for x, y in L_ + R_[::-1]]; bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=bm.faces); put("tunnel", "pad", bm)
    for p in (P[5], P[12], P[19], P[26]):
        LAMPS.append((p.x, p.y, 2.2))
    put("lantaarn", "ijzer", bz(9.62, 9.75, -0.55, -0.45, 2.7, 3.35))
    LAMPS.append((9.55, -0.5, 2.9))
    # ---------------- snijden: tunnel door rots en ruinemuren ----------------
    cut = bmesh.new()
    for bm in cutters:
        m2 = bpy.data.meshes.new("_c"); bm.to_mesh(m2); bm.free(); cut.from_mesh(m2); bpy.data.meshes.remove(m2)
    cme = bpy.data.meshes.new("_cutter"); cut.to_mesh(cme); cut.free()
    cob = bpy.data.objects.new("_cutter", cme); col("FORMS").objects.link(cob)
    for (part, mat), bm in list(PARTS.items()):
        ob = new_mesh_object(f"SW_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
        if part == "ruine" and mat == "ruine":
            b = ob.modifiers.new("cut", "BOOLEAN"); b.object = cob; b.operation = "DIFFERENCE"; b.solver = "EXACT"; b.use_self = True; b.use_hole_tolerant = True
            apply_all_modifiers(ob)
    PARTS.clear()
    assign(rots, bpy.data.materials["MAT_rots"])
    b = rots.modifiers.new("cut", "BOOLEAN"); b.object = cob; b.operation = "DIFFERENCE"; b.solver = "MANIFOLD" if "MANIFOLD" in [i.identifier for i in bpy.types.BooleanModifier.bl_rna.properties["solver"].enum_items] else "EXACT"
    apply_all_modifiers(rots)
    d = rots.modifiers.new("dec", "DECIMATE"); d.ratio = min(1.0, 16000 / max(1, len(rots.data.polygons))); apply_all_modifiers(rots)
    bpy.data.objects.remove(cob, do_unlink=True); bpy.data.meshes.remove(cme)
    # ---------------- botsblokken: rand van de rots (behalve in- en uitgang) + tunnelwanden ----------------
    E = resample(GROT + [GROT[0]], 0.9)
    for a, b2 in zip(E, E[1:]):
        m = (a + b2) / 2
        if (m - Vector((10.42, -1.63))).length < 1.6 or (m - Vector((22.53, -7.16))).length < 1.6: continue
        if min((Vector((m.x, m.y)) - Vector(q)).length for q in [(p.x, p.y) for p in P]) < TW / 2 + 0.2: continue
        L = (b2 - a).length
        if L < 0.05: continue
        COLL.append([round(m.x, 3), round(m.y, 3), 2.0, round(L + 0.3, 3), 0.8, 4.0, round(math.degrees(math.atan2(b2.y - a.y, b2.x - a.x)), 2)])
    for i in range(len(P) - 1):
        a, b2 = P[i], P[i + 1]; t = Vector((b2.x - a.x, b2.y - a.y)).normalized(); nn = Vector((-t.y, t.x)); m = (a + b2) / 2
        for s in (-1, 1):
            c = Vector((m.x, m.y)) + nn * s * (TW / 2 + 0.15)
            if not inside(c.x, c.y, GROT): continue
            COLL.append([round(c.x, 3), round(c.y, 3), 1.5, round((b2 - a).length + 0.2, 3), 0.3, 3.0, round(math.degrees(math.atan2(t.y, t.x)), 2)])
    out = os.path.join(os.path.dirname(HERE), "exports")
    json.dump({"colliders": COLL, "lamps": [[round(v, 2) for v in l] for l in LAMPS]}, open(os.path.join(out, "grot_extra.json"), "w"))
    for o in bpy.data.objects:
        if o.name not in voor: o["owner"] = TAG
    save_master(master); log("rots tris", len(rots.data.polygons), "colliders", len(COLL))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
