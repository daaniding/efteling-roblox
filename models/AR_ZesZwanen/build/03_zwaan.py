"""03_zwaan: zwanenboot De Zes Zwanen (1 asset, 6x geplaatst). Lokaal: vooruit = -Y, z = 0 waterlijn, midden romp op de oorsprong.
Bronnen: Zwaantekening2/Zwanenbootjesontwerp_ton (zijaanzicht), D6z_zwaan_closeup, Zwanenlageinstap, D6z_vaart_zwanen_klaar_voor_vertrek,
Efteling-blog (klei- en 3D-model). Maten (inferred uit foto's met kinderen/volwassenen): romp 3.0 x 1.45 m, vrijboord 0.55, kop 2.0 m,
vleugels achter tot 1.2 m met omkrullende slagpennen, rode kuip met houten bank, sjerp om de halsvoet (ranken), oranje snavel met zwarte knobbel.
Gebruik: Blender -b -P 03_zwaan.py -- --master ZZ_zwaan_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "zz_helpers.py")).read())
RNG = random.Random(6)
MATS = {"zwaan": ((0.9, 0.87, 0.78, 1), 0.35), "snavel": ((0.9, 0.42, 0.12, 1), 0.4), "zwart": ((0.03, 0.03, 0.03, 1), 0.4),
        "kuip": ((0.5, 0.08, 0.07, 1), 0.5), "hout": ((0.36, 0.24, 0.15, 1), 0.7), "oog": ((0.02, 0.02, 0.02, 1), 0.1), "goud": ((0.8, 0.6, 0.2, 1), 0.3)}


def loft(sections, n=24):
    """romp: doorsneden (y, halve breedte, bovenkant z, onderkant z, ronding) -> gesloten mesh langs y"""
    bm = bmesh.new(); rings = []
    for (y, hw, zt, zb, ex) in sections:
        ring = []
        for k in range(n):
            a = k * math.tau / n; c, s = math.cos(a), math.sin(a)
            x = hw * math.copysign(abs(c) ** (2 / ex), c)
            zc = (zt + zb) / 2; hz = (zt - zb) / 2
            z = zc + hz * math.copysign(abs(s) ** (2 / ex), s)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    for A, B in zip(rings, rings[1:]):
        for k in range(n): bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm


def taps(points, r0, r1, segs=12):
    """buis met aflopende straal r0 -> r1 (stukjes btube die overlappen)"""
    out = bmesh.new(); n = len(points)
    for i in range(n - 1):
        r = r0 + (r1 - r0) * (i + 0.5) / (n - 1)
        b = btube([points[i], points[i + 1]], r, segs)
        me_ = bpy.data.meshes.new("_t"); b.to_mesh(me_); b.free(); out.from_mesh(me_); bpy.data.meshes.remove(me_)
        s = ell(points[i + 1], (r * 0.98, r * 0.98, r * 0.98), segs, 8); me_ = bpy.data.meshes.new("_t"); s.to_mesh(me_); s.free(); out.from_mesh(me_); bpy.data.meshes.remove(me_)
    return out


def veer(base, tip, w, t=0.05, side=1):
    """platte slagpen: afgeplatte ellips van base naar tip, breedte w, dikte t"""
    b = Vector(base); e = Vector(tip); L = (e - b).length; m = (b + e) / 2
    f = ell((0, 0, 0), (w / 2, L / 2, t), 12, 6)
    d = (e - b).normalized(); rot = d.to_track_quat("Y", "Z").to_matrix().to_4x4()
    bmesh.ops.transform(f, matrix=Matrix.Translation(m) @ rot, verts=f.verts); return f


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ---- romp: de zijwanden lopen naar achteren op tot de opgeheven vleugels (achterwand 1.15 m) ----
    S = [(-1.74, 0.03, 0.35, 0.05, 2.0), (-1.66, 0.22, 0.6, -0.12, 2.0), (-1.45, 0.5, 0.72, -0.26, 2.2), (-1.0, 0.68, 0.62, -0.34, 2.4), (-0.4, 0.72, 0.62, -0.36, 2.6),
         (0.3, 0.72, 0.62, -0.36, 2.6), (0.9, 0.68, 0.72, -0.34, 2.4), (1.25, 0.58, 0.95, -0.3, 2.2), (1.52, 0.38, 1.08, -0.22, 2.0), (1.7, 0.14, 1.0, -0.05, 2.0), (1.78, 0.04, 0.85, 0.2, 2.0)]
    romp = loft(S, 32)
    def wand(y, z):                                                                                    # x van de buitenwand op (y, z)
        for (y0, w0, t0, b0, e0), (y1, w1, t1, b1, e1) in zip(S, S[1:]):
            if y0 <= y <= y1:
                f = (y - y0) / (y1 - y0); hw = w0 + (w1 - w0) * f; zt = t0 + (t1 - t0) * f; zb = b0 + (b1 - b0) * f; ex = e0 + (e1 - e0) * f
                hz = (zt - zb) / 2; zc = (zt + zb) / 2; s_ = max(-1.0, min(1.0, (z - zc) / hz))
                return hw * (max(0.0, 1 - abs(s_) ** ex)) ** (1 / ex), zt
        return 0.2, 0.5
    # ---- hals (S-curve, dik aan de voet) + kop ----
    hp = [(0, -1.12, 0.35), (0, -1.42, 0.82), (0, -1.47, 1.22), (0, -1.33, 1.58), (0, -1.2, 1.83), (0, -1.2, 1.95)]
    from mathutils.geometry import interpolate_bezier
    fijn = []
    for i in range(len(hp) - 1):                                                                       # Catmull-Rom -> 6 punten per stuk
        p0 = Vector(hp[max(i - 1, 0)]); p1 = Vector(hp[i]); p2 = Vector(hp[i + 1]); p3 = Vector(hp[min(i + 2, len(hp) - 1)])
        for k in range(6):
            t = k / 6; t2, t3 = t * t, t * t * t
            fijn.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)))
    fijn.append(hp[-1])
    hals = taps(fijn, 0.24, 0.105, 16)                                              # slanker (Studio: leek een gans)
    kop = merge(ell((0, -1.27, 2.0), (0.12, 0.2, 0.12), 18, 12), ell((0, -1.38, 1.95), (0.095, 0.11, 0.085), 14, 8))
    # ---- eerst romp + hals + kop glad samensmelten (borst en hals zijn glad, zoals de foto) ----
    glad = organisch(merge(romp, hals, kop), 0.02, 12, 0.8, 0.0, 1.0, 0.5)
    # ---- vleugel per zijde: krul voorin, vlak plekje dekveren, 6 lange gladde slagpennen die naar achteren omhoog zwaaien ----
    vl = bmesh.new()
    def voeg(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); vl.from_mesh(me_); bpy.data.meshes.remove(me_)
    # vleugelschild (zijaanzicht Zwaantekening2): ondergrens langs de romp, voorrand met krul, bovenrand loopt naar achter op tot 1.3 m
    VL = [(-0.3, 0.22), (-0.32, 0.42), (-0.2, 0.62), (0.05, 0.74), (0.45, 0.84), (0.85, 0.98), (1.2, 1.15), (1.45, 1.3), (1.62, 1.28), (1.7, 1.05), (1.72, 0.75), (1.66, 0.48), (1.5, 0.28), (1.1, 0.18), (0.4, 0.15)]
    for sd in (-1, 1):
        sch = bmesh.new(); vs_ = []
        for (y, z) in VL:
            x, _ = wand(max(-1.6, min(1.7, y)), min(z, 0.55))
            vs_.append((y, z, x))
        for k_, (dx) in enumerate((0.0, 0.13)):
            pass
        top = [sch.verts.new((sd * (x + 0.02 + 0.12 * max(0.0, z - 0.6)), y, z)) for (y, z, x) in vs_]
        bot = [sch.verts.new((sd * (x - 0.1 + 0.12 * max(0.0, z - 0.6)), y, z)) for (y, z, x) in vs_]
        n_ = len(vs_); sch.faces.new(top if sd > 0 else top[::-1]); sch.faces.new(bot[::-1] if sd > 0 else bot)
        for i in range(n_): sch.faces.new((top[i], top[(i + 1) % n_], bot[(i + 1) % n_], bot[i]))
        bmesh.ops.recalc_face_normals(sch, faces=sch.faces); bmesh.ops.triangulate(sch, faces=[f for f in sch.faces if len(f.verts) > 4], ngon_method="EAR_CLIP")
        sch.free()                                                                                     # (vlak schild gaf een kistvormige achterkant: weg)
        sp = []                                                                                        # krul (Pieck) voor-onder in de vleugel
        for i in range(26):
            t = i / 25; a_ = t * 2.4 * math.pi; rr = 0.2 * (1 - 0.8 * t)
            y = -0.05 + rr * math.cos(a_); z = 0.36 + rr * math.sin(a_)
            x, _ = wand(y, min(z, 0.55)); sp.append((sd * (x + 0.06 + 0.04 * (1 - t)), y, z))
        voeg(taps(sp, 0.06, 0.028, 8))
        for row in range(3):                                                                           # dekveren voorin de vleugel
            for k in range(5):
                y = 0.25 + k * 0.15 + 0.075 * (row % 2); z = 0.66 - row * 0.12 + 0.12 * k / 4
                x, zt = wand(y, 0.5)
                pet = ell((0, 0, 0), (0.02, 0.12, 0.075), 10, 6)
                bmesh.ops.transform(pet, matrix=Matrix.Translation((sd * (x + 0.06 + 0.12 * max(0.0, z - 0.6)), y + 0.05, z)) @ Matrix.Rotation(math.radians(-30), 4, "X"), verts=pet.verts)
                voeg(pet)
        for i in range(6):                                                                             # rij armpennen tussen dekveren en slagpennen
            t = i / 5; y0 = 0.15 + 0.3 * t; z0 = 0.72 - 0.06 * t
            x0, _ = wand(y0, 0.5)
            voeg(veer((sd * (x0 + 0.05), y0, z0), (sd * (x0 + 0.08), y0 + 0.55, z0 - 0.12 - 0.05 * t), 0.15, 0.04))
        for i in range(9):                                                                             # smallere, overlappende slagpennen op het schild: hun punten vormen de geschulpte achterrand
            t = i / 8
            y0 = 0.55 + 0.25 * t; z0 = 1.0 - 0.5 * t
            y1 = 1.45 + 0.35 * t; z1 = 1.36 - 0.88 * t
            x0, _ = wand(min(y0, 1.6), 0.5)
            f = veer((sd * (x0 + 0.07 + 0.1 * max(0.0, z0 - 0.6) + 0.01 * i), y0, z0), (sd * (x0 + 0.08 + 0.1 * max(0.0, z1 - 0.6) + 0.012 * i), y1, z1), 0.23, 0.05)
            voeg(f)
    body = merge(glad, vl)
    body = organisch(body, 0.014, 2, 0.4, 0.0, 1.0, 0.055)          # ~18k tris per zwaan (6x geplaatst)
    kuip_cut = organisch(bz(-0.5, 0.5, -0.86, 1.0, 0.14, 1.6), 0.03, 6, 0.7, 0.0)
    PARTS[("zwaan", "zwaan")] = body
    snij(lambda k: k == ("zwaan", "zwaan"), [kuip_cut])
    put("zwaan", "kuip", organisch(bz(-0.52, 0.52, -0.88, 1.04, 0.1, 0.18), 0.03, 4, 0.6, 0.0))      # rode bodem
    for sd in (-1, 1): put("zwaan", "kuip", bz(sd * 0.49 - 0.02, sd * 0.49 + 0.02, -0.82, 0.98, 0.15, 0.55))   # rode binnenwanden
    put("zwaan", "kuip", bz(-0.48, 0.48, 0.98, 1.0, 0.15, 0.95)); put("zwaan", "kuip", bz(-0.48, 0.48, -0.84, -0.82, 0.15, 0.55))
    put("zwaan", "hout", bz(-0.14, 0.14, -0.62, 0.8, 0.36, 0.42, 0.01))                              # bank in de lengte (achter elkaar zitten)
    for y in (-0.45, 0.65): put("zwaan", "hout", bz(-0.1, 0.1, y - 0.05, y + 0.05, 0.18, 0.36))
    # ---- snavel, knobbel, masker, ogen ----
    snavel = merge(ell((0, -1.5, 1.91), (0.055, 0.16, 0.045), 14, 8), ell((0, -1.62, 1.87), (0.04, 0.1, 0.034), 12, 8))
    put("zwaan", "snavel", organisch(snavel, 0.01, 4, 0.6, 0.0))
    put("zwaan", "zwart", organisch(merge(ell((0, -1.4, 1.95), (0.07, 0.07, 0.07), 12, 8), ell((0, -1.69, 1.85), (0.025, 0.03, 0.025), 8, 6)), 0.01, 3, 0.5, 0.0))
    for sd in (-1, 1):
        put("zwaan", "zwart", organisch(merge(ell((sd * 0.098, -1.33, 1.995), (0.022, 0.08, 0.04), 10, 8), ell((sd * 0.1, -1.25, 2.03), (0.018, 0.05, 0.025), 8, 6)), 0.008, 3, 0.5, 0.0))   # plat masker   # masker met krul
        put("zwaan", "oog", ell((sd * 0.112, -1.33, 2.0), (0.01, 0.016, 0.014), 8, 6))
    # ---- sjerp om de halsvoet: band met eigen UV (textuur met ranken, 03_textuur_sjerp.py) ----
    sj = bmesh.new(); uv = sj.loops.layers.uv.new("UVMap"); n = 36; RING = []
    for zz, s_ in ((0.42, 1.0), (0.7, 0.86)):
        RING.append([sj.verts.new((0.0, 0.0, 0.0)) for _ in range(n)])
    for (ring, zz, rr) in ((RING[0], 0.42, 0.33), (RING[1], 0.72, 0.29)):
        for k, v in enumerate(ring):
            a = k * math.tau / n
            v.co = Vector((rr * 1.12 * math.cos(a), -1.18 + rr * 0.95 * math.sin(a) - (0.06 if zz > 0.5 else 0), zz + 0.06 * math.sin(a)))
    for k in range(n):
        f = sj.faces.new((RING[0][k], RING[0][(k + 1) % n], RING[1][(k + 1) % n], RING[1][k]))
        for l_, (u, w) in zip(f.loops, ((k / n, 0), ((k + 1) / n, 0), ((k + 1) / n, 1), (k / n, 1))): l_[uv].uv = (u * 3, w)
    me = bpy.data.meshes.new("BAKE_sjerp"); sj.to_mesh(me); sj.free(); ob = bpy.data.objects.new("BAKE_sjerp", me); col("FORMS").objects.link(ob); own(ob)
    mt = bpy.data.materials.get("MAT_sjerptex") or bpy.data.materials.new("MAT_sjerptex"); ob.data.materials.append(mt)
    mod = ob.modifiers.new("dik", "SOLIDIFY"); mod.thickness = 0.03; mod.offset = 1.0
    coll_box(0, 0.05, 0.2, 1.5, 3.2, 0.9)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"ZW_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": []}, open(os.path.join(out, "zwaan_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
