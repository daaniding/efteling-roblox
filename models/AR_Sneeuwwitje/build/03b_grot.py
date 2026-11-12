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
PAD = [(8.8, -1.75), (10.6, -1.8), (12.7, -2.25), (14.5, -3.4), (16.3, -4.1), (18.4, -4.55), (20.3, -4.85), (21.8, -5.8), (22.6, -7.3), (23.0, -8.6)]
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


def rock_mass():
    """grote ronde blokken binnen de OSM-vorm -> voxel remesh -> naden/ruis"""
    bm = bmesh.new()
    xs = [p[0] for p in GROT]; ys = [p[1] for p in GROT]
    pts = []
    for _ in range(4000):
        x = RNG.uniform(min(xs), max(xs)); y = RNG.uniform(min(ys), max(ys))
        if inside(x, y, GROT) and all((Vector((x, y)) - q).length > 1.0 for q in pts): pts.append(Vector((x, y)))
    edge = resample(GROT + [GROT[0]], 1.1)
    for e in edge:        # rand: blokken iets naar binnen, hoog en bol
        c = Vector((sum(xs) / len(xs), sum(ys) / len(ys)))
        d = (c - Vector((e.x, e.y))).normalized() * 0.55
        pts.append(Vector((e.x, e.y)) + d)
    for p in pts:
        r = RNG.uniform(0.95, 1.6); h = RNG.uniform(2.6, 4.3)
        if p.x < 11.5 or p.x > 22.2: h *= 0.75
        sb = bmesh.new(); bmesh.ops.create_icosphere(sb, subdivisions=2, radius=1.0)
        for v in sb.verts: v.co = Vector((v.co.x * r * RNG.uniform(0.9, 1.2), v.co.y * r, (v.co.z * 0.5 + 0.5) * h))
        bmesh.ops.rotate(sb, cent=(0, 0, 0), matrix=Matrix.Rotation(RNG.uniform(0, math.tau), 3, "Z"), verts=sb.verts)
        bmesh.ops.translate(sb, vec=(p.x, p.y, -0.3), verts=sb.verts)
        me = bpy.data.meshes.new("_b"); sb.to_mesh(me); sb.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new("SW_rots__rots"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("SW_rots__rots", me); col("FORMS").objects.link(ob); own(ob)
    remesh_voxel(ob, 0.12); apply_all_modifiers(ob)
    bm = bmesh.new(); bm.from_mesh(ob.data)
    for v in bm.verts:     # gladde bulten + enkele diepe naden (Efteling-kunstrots)
        q = v.co * 0.8
        n1 = noise.noise(q * 0.9); n2 = noise.noise(q * 2.6 + Vector((5, 1, 2)))
        seam = max(0.0, 0.18 - abs(noise.noise(q * 0.55 + Vector((9, 4, 1))))) * 1.8
        nrm = v.normal
        v.co += nrm * (0.22 * n1 + 0.06 * n2 - seam)
        if v.co.z < 0: v.co.z = -0.05 if v.co.z > -0.4 else v.co.z
    bm.to_mesh(ob.data); bm.free()
    return ob


def ruin_wall(part, x0, y0, x1, y1, h, top_noise=0.9, thick=0.55, seed=0):
    """bakstenen ruinemuur van (x0,y0) naar (x1,y1) met afgebrokkelde, getrapte bovenrand"""
    L = math.hypot(x1 - x0, y1 - y0); a = math.degrees(math.atan2(y1 - y0, x1 - x0)); M = TR(x0, y0, 0, a)
    n = max(3, int(L / 0.32)); r = random.Random(seed)
    for i in range(n):
        u0 = L * i / n; u1 = L * (i + 1) / n
        hh = h - top_noise * max(0, noise.noise(Vector((u0 * 0.7 + seed, 0, 0)))) - r.uniform(0, 0.25)
        put(part, "ruine", bz(u0, u1 + 0.002, -thick / 2, thick / 2, 0, max(0.6, hh)), M)
    return M, L


def build(master):
    open_master(master)
    TAG = "phase:03b_grot"     # eigen label: de hulpfuncties (uit Assepoester) labelen alles als phase:03_forms
    for o in [o for o in bpy.data.objects if o.get("owner") == TAG]: bpy.data.objects.remove(o, do_unlink=True)
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    COLL.clear(); LAMPS.clear()
    voor = set(o.name for o in bpy.data.objects)
    rots = rock_mass()
    cutters = [arch_tube(PAD, TW, TH)]
    # ruinemuur bij de ingang (Boekloc_Sneeuwwitje.jpg): 4.5 m, getrapt, rondboogtunnel, nisje; lage ruinemuur ernaast met bankje
    Mi, Li = ruin_wall("ruine", 10.05, -3.9, 10.25, 0.9, 4.6, 1.6, 0.6, seed=3)
    ap = arch_pts(0, 0, TW, TH, 12)
    put("ruine", "steen", band(ap, 0.12, -0.36, 0.06), TR(10.15, -1.8, 0, 92))
    put("ruine", "ruine", boutline([(-0.25, 2.9), (0.25, 2.9)] + arc(0, 3.3, 0.25, 0, 180, 6)[1:-1] + [(-0.25, 2.9)], -0.4, 0.15), TR(10.15, -0.2, 0, 92))   # nisje
    # lage ruinemuur van de ronde toren naar de grotingang (Sneeuwwitjezijaanzicht / Boekloc: kasteel en grot zitten aan elkaar, Daan)
    Ml, Ll = ruin_wall("ruine", 6.95, 3.45, 10.25, 0.95, 1.9, 0.9, 0.45, seed=7)
    ang = math.atan2(0.95 - 3.45, 10.25 - 6.95); t = Vector((math.cos(ang), math.sin(ang))); nn = Vector((t.y, -t.x))   # nn wijst naar het pad (oost)
    for k in range(3):
        pp = Vector((6.95, 3.45)) + t * (1.2 + k * 0.9)
        COLL.append([round(pp.x, 3), round(pp.y, 3), 1.0, 1.0, 0.5, 2.0, round(math.degrees(ang), 2)])
    bc = Vector((6.95, 3.45)) + t * 2.1 + nn * 0.55                                                  # bankje tegen het muurtje
    put("ruine", "hout", bz(-0.6, 0.6, -0.2, 0.2, 0.42, 0.48), TR(bc.x, bc.y, 0, math.degrees(ang)))
    for u in (-0.45, 0.45): put("ruine", "steen", bz(u - 0.08, u + 0.08, -0.17, 0.17, 0, 0.42), TR(bc.x, bc.y, 0, math.degrees(ang)))
    # ruinemuur bij de uitgang (Sneeuwwitjegrot.jpg rechts)
    Mu, Lu = ruin_wall("ruine", 21.3, -8.2, 23.95, -6.45, 3.6, 1.2, 0.55, seed=11)
    # ruinetorentje met klimop op de rots (Grotvernieuwd.jpg)
    tc = Vector((15.6, -0.6)); zb = 2.6
    for k in range(18):
        a0 = k * math.tau / 18; a1 = (k + 1) * math.tau / 18
        hh = 6.9 - 1.3 * max(0, noise.noise(Vector((k * 0.6, 3, 0)))) - (0.9 if k in (4, 5, 11) else 0)
        p0 = tc + Vector((math.cos(a0), math.sin(a0))) * 1.05; p1 = tc + Vector((math.cos(a1), math.sin(a1))) * 1.05
        bm = bz(0, (p1 - p0).length + 0.01, -0.22, 0.22, zb, hh)
        put("ruine", "ruine", bm, TR(p0.x, p0.y, 0, math.degrees(math.atan2(p1.y - p0.y, p1.x - p0.x))))
    for k, (a, z) in enumerate(((200, 4.6), (320, 5.0), (80, 4.4))):     # raamgaten (donker)
        p = tc + Vector((math.cos(math.radians(a)), math.sin(math.radians(a)))) * 1.27
        put("ruine", "donker", bz(-0.22, 0.22, -0.02, 0.02, z, z + 0.75), TR(p.x, p.y, 0, a + 90))
    for k in range(70):    # klimop: plukjes bladeren tegen toren en muren
        if k < 45: a = RNG.uniform(0, math.tau); p = tc + Vector((math.cos(a), math.sin(a))) * 1.25; z = RNG.uniform(zb, 6.3)
        else: u = RNG.uniform(0, 1); p = Vector((10.05 + 0.2 * u, -3.9 + 4.8 * u)) + Vector((-0.32, 0)); z = RNG.uniform(1.5, 4.2)
        b = bmesh.new(); bmesh.ops.create_icosphere(b, subdivisions=1, radius=1.0)
        s = RNG.uniform(0.25, 0.5)
        for v in b.verts: v.co = Vector((v.co.x * s, v.co.y * s * 0.6, v.co.z * s * 0.8))
        bmesh.ops.translate(b, vec=(p.x, p.y, z), verts=b.verts); put("klimop", "klimop", b)
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
