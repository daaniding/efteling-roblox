"""03_papegaai De Sprekende Papegaai (Het Stoute Prinsesje, 1952): bakstenen muurtje met rondboognis (wit stuc), leien zadeldakje op houten schoren,
ara (groenvleugel-ara, 2005-kleuren: oranjerood, blauwgroen) op een knoestige tak die uit de nis groeit, bordje, klimop, gebogen lage leuning voor het
plantvak, strook licht grind tot het pad. Bronnen + maten: asset-brief.md. Frame: oorsprong midden OSM 55423808, -Y = naar het pad (ZW), z 0 = maaiveld.
Gebruik: Blender -b -P 03_papegaai.py -- --master PA_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"baksteen": ((0.5, 0.32, 0.25, 1), 0.9), "stuc": ((0.88, 0.86, 0.8, 1), 0.9), "pannen": ((0.55, 0.3, 0.2, 1), 0.85), "hout": ((0.3, 0.2, 0.13, 1), 0.8),
        "schors": ((0.36, 0.33, 0.28, 1), 0.95), "rood": ((0.75, 0.16, 0.08, 1), 0.6), "geel": ((0.9, 0.7, 0.15, 1), 0.6), "blauw": ((0.1, 0.35, 0.55, 1), 0.6),
        "groen": ((0.12, 0.45, 0.35, 1), 0.6), "wit": ((0.92, 0.9, 0.86, 1), 0.7), "zwart": ((0.05, 0.05, 0.05, 1), 0.5), "snavel": ((0.85, 0.82, 0.74, 1), 0.5),
        "oogrood": ((0.9, 0.08, 0.05, 1), 0.3), "bord": ((0.92, 0.88, 0.76, 1), 0.7), "ijzer": ((0.04, 0.05, 0.05, 1), 0.45), "leuning": ((0.16, 0.3, 0.27, 1), 0.6),
        "grind": ((0.86, 0.83, 0.76, 1), 0.95), "aarde": ((0.22, 0.16, 0.11, 1), 1.0), "rots": ((0.45, 0.45, 0.42, 1), 0.95)}
WY = 2.2                       # voorvlak muur
W, EAVE, RIDGE = 3.2, 3.4, 4.65   # Intro_papegaai: muur 550 px breed x 610 px hoog, dak ~30 graden met groot overstek
PIJ = 0.67                        # pijlerbreedte
NB, NTOP = W - 2 * PIJ, 3.2       # nisbreedte, top rondboog (vlak onder de dakvoet)
rr = random.Random(1952)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ---------- muur: pijlers + boog + achterwand (baksteen), nis-achterwand wit stuc ----------
    x0, x1 = -W / 2, W / 2
    put("muur", "baksteen", bz(x0, x0 + PIJ, WY, WY + 0.75, 0.0, EAVE))
    put("muur", "baksteen", bz(x1 - PIJ, x1, WY, WY + 0.75, 0.0, EAVE))
    put("muur", "baksteen", bz(x0, x1, WY + 0.45, WY + 0.75, 0.0, EAVE))                         # achterwand
    arch = [(x0 + PIJ, NTOP - NB / 2)] + [(-NB / 2 * math.cos(math.pi * k / 16), NTOP - NB / 2 + NB / 2 * math.sin(math.pi * k / 16)) for k in range(17)] + [(x1 - PIJ, NTOP - NB / 2), (x1 - PIJ, EAVE), (x0 + PIJ, EAVE)]
    put("muur", "baksteen", boutline(arch, WY, 0.46))
    # gemetselde rollaag om de boog
    put("muur", "baksteen", band([(-NB / 2 * math.cos(math.pi * k / 16), NTOP - NB / 2 + NB / 2 * math.sin(math.pi * k / 16)) for k in range(17)][::-1], 0.12, WY - 0.03, 0.1))
    put("nis", "stuc", bz(x0 + PIJ - 0.02, x1 - PIJ + 0.02, WY + 0.43, WY + 0.46, 0.25, NTOP))     # witte nis-achterwand (Intro)
    put("nis", "baksteen", bz(x0 + PIJ, x1 - PIJ, WY, WY + 0.46, 0.0, 0.25))                       # lage borstwering in de nis
    coll_box(0, WY + 0.37, EAVE / 2, W, 0.75, EAVE)
    # ---------- leien zadeldak (nok haaks op de muur, gevel naar voren) op houten schoren ----------
    ov = 0.75
    for s in (-1, 1):
        bm = bmesh.new(); xe = s * (W / 2 + ov); ze = EAVE - 0.12
        q = [(xe, WY - ov, ze), (0, WY - ov, RIDGE), (0, WY + 0.75 + 0.2, RIDGE), (xe, WY + 0.75 + 0.2, ze)]
        top = [bm.verts.new(p) for p in q]; bot = [bm.verts.new((p[0], p[1], p[2] - 0.1)) for p in q]
        bm.faces.new(top); bm.faces.new(bot[::-1])
        for i in range(4): bm.faces.new((top[i], bot[i], bot[(i + 1) % 4], top[(i + 1) % 4]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); put("dak", "pannen", bm)
        for k in range(12):                                                                      # pannenrijen
            t = k / 11; z = ze + 0.02 + t * (RIDGE - ze - 0.05); x = xe * (1 - t)
            put("dak", "pannen", btube([(x, WY - ov - 0.01, z), (x, WY + 0.95, z)], 0.035, 5))
    put("dak", "hout", bz(-0.08, 0.08, WY - ov - 0.05, WY + 0.98, RIDGE - 0.06, RIDGE + 0.06))
    gp = [(-W / 2 - ov, EAVE - 0.22), (0, RIDGE - 0.1), (W / 2 + ov, EAVE - 0.22)]               # houten windveren voor
    put("dak", "hout", band(gp, 0.16, WY - ov - 0.04, 0.06))
    put("dak", "hout", boutline([(-W / 2, EAVE), (0, RIDGE - 0.12), (W / 2, EAVE)], WY - 0.02, 0.05))   # gevelvulling hout
    for s in (-1, 1):                                                                            # schoren (Intro: gebogen houten consoles)
        x = s * (W / 2 - 0.1)
        put("dak", "hout", btube([(x, WY + 0.05, EAVE - 1.45), (x, WY - 0.25, EAVE - 0.85), (x, WY - 0.62, EAVE - 0.3)], 0.09, 6))   # zware gebogen console (Intro)
        put("dak", "hout", bz(x - 0.11, x + 0.11, WY - ov, WY + 0.15, EAVE - 0.38, EAVE - 0.16))
        put("dak", "hout", bz(x - 0.13, x + 0.13, WY - 0.12, WY + 0.02, EAVE - 1.6, EAVE - 1.3))
    # ---------- tak uit de nis (BoomPapegaai, Intro: knoestig, van midden-onder schuin omhoog naar links, naar de voeten van de ara) ----------
    tak = [Vector((0.05, WY + 0.3, 0.0)), Vector((0.1, WY + 0.2, 0.55)), Vector((-0.05, WY + 0.1, 1.05)), Vector((-0.2, WY + 0.0, 1.45)), Vector((-0.25, WY - 0.12, 1.72)), Vector((-0.42, WY - 0.15, 1.8))]
    for a_, b_, r in zip(tak, tak[1:], (0.12, 0.1, 0.085, 0.07, 0.055)): put("tak", "schors", btube([a_, b_], r, 8))
    put("tak", "schors", btube([Vector((0.1, WY + 0.2, 0.55)), Vector((0.45, WY + 0.05, 0.75)), Vector((0.62, WY + 0.0, 0.72))], 0.05, 6))   # zijtak rechts (Intro)
    put("tak", "schors", btube([Vector((0.05, WY + 0.25, 0.25)), Vector((-0.35, WY + 0.15, 0.35))], 0.06, 6))
    # ---------- ara (groenvleugel-ara, 2005): gebouwd rechtop in een eigen frame, dan schuin gezet (kop linksboven, vleugels omhoog-rechts, staart rechtsomlaag) ----------
    lijf = bmesh.new()
    def add(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); lijf.from_mesh(me_); bpy.data.meshes.remove(me_)
    add(ell((0.0, 0.0, 0.22), (0.13, 0.12, 0.23), 14, 10)); add(ell((0.0, -0.03, 0.47), (0.1, 0.1, 0.11), 12, 8)); add(ell((0.0, -0.02, 0.36), (0.08, 0.08, 0.08), 10, 8))
    put("ara", "rood", organisch(lijf, 0.012, 4, 0.5, 0.004, 20.0, 0.5))
    put("ara", "wit", ell((-0.07, -0.08, 0.48), (0.04, 0.05, 0.055), 8, 6))
    put("ara", "oogrood", ell((-0.08, -0.12, 0.5), (0.016, 0.012, 0.016), 6, 4))
    snb = blathe([(0, 0), (0.045, 0), (0.05, 0.03), (0.03, 0.08), (0.008, 0.11), (0, 0.11)], 10)
    for v in snb.verts: v.co.y *= 0.8
    put("ara", "snavel", snb, Matrix.Translation((-0.1, -0.07, 0.45)) @ Matrix.Rotation(math.radians(110), 4, "Y"))
    put("ara", "zwart", ell((-0.12, -0.07, 0.41), (0.03, 0.025, 0.02), 6, 4))
    for wy, (a0, a1) in ((0.06, (-15, 28)), (-0.07, (-25, 18))):                                   # na het kantelen: omhoog naar rechts                                  # twee vleugels, opgeheven (Intro)
        base = Vector((0.04, wy, 0.32))
        for k in range(10):
            ang = math.radians(a0 + (a1 - a0) * k / 9); L = 0.26 + 0.045 * k
            d = Vector((math.cos(ang), 0.0, math.sin(ang)))
            mat = "blauw" if k > 6 else ("groen" if k > 3 else "geel")
            fb = bz(0, L, -0.008, 0.008, -0.035, 0.035, 0.005)
            put("ara", mat, fb, Matrix.Translation(base + Vector((0, 0.004 * k, 0))) @ Vector((1, 0, 0)).rotation_difference(d).to_matrix().to_4x4())
        put("ara", "rood", ell(base + Vector((0.02, 0, 0.1)), (0.08, 0.03, 0.14), 8, 6))
    for k in range(5):                                                                           # staart: lang, rood met blauwe punt
        d = Vector((0.1 + 0.05 * (k - 2), 0.02, -1.0)).normalized(); L = 0.62 - abs(k - 2) * 0.07
        fb = bz(0, L, -0.006, 0.006, -0.028, 0.028, 0.004); M = Matrix.Translation((0.03, 0.02, 0.05)) @ Vector((1, 0, 0)).rotation_difference(d).to_matrix().to_4x4()
        put("ara", "rood", fb, M); put("ara", "blauw", bz(L * 0.65, L, -0.007, 0.007, -0.024, 0.024, 0.003), M)
    for sx in (-1, 1): put("ara", "zwart", btube([(sx * 0.04, -0.02, 0.05), (sx * 0.05, -0.04, -0.01)], 0.012, 5))
    MA = Matrix.Translation((-0.2, WY - 0.16, 1.82)) @ Matrix.Rotation(math.radians(-50), 4, "Y") @ Matrix.Scale(1.6, 4)   # voeten op de tak (Intro x 370, y 440)
    for key in [k for k in PARTS if k[0] == "ara"]: bmesh.ops.transform(PARTS[key], matrix=MA, verts=PARTS[key].verts)
    # ---------- bordje naast de nis (rechts, Intro) ----------
    Mb = TR(x1 - PIJ / 2 + 0.05, WY - 0.02, 2.3)
    put("bord", "bord", bz(-0.26, 0.26, -0.03, 0.0, -0.12, 0.12, 0.01), Mb)
    put("bord", "rood", bz(-0.27, 0.27, -0.035, -0.025, -0.13, -0.11), Mb); put("bord", "rood", bz(-0.27, 0.27, -0.035, -0.025, 0.11, 0.13), Mb)
    # ---------- klimop op de pijlers en de dakrand (eind60, 1973) ----------
    kb = bmesh.new()
    for _ in range(5200):                                                                       # dik in de klimop (eind60, 1973): pijlers, zijkanten, onderkant voorgevel
        side = rr.choice((-1, 1)); x = side * rr.uniform(W / 2 - PIJ - 0.15, W / 2 + 0.05); z = rr.uniform(0.0, EAVE - 0.1) ** 1.0 if rr.random() < 0.6 else rr.uniform(0.0, 1.4)
        if rr.random() < 0.15: x = rr.uniform(-W / 2, W / 2); z = rr.uniform(0.0, 0.45)
        if rr.random() < 0.5: y = WY - 0.03; n = Vector((0, -1, 0))
        else: y = WY + rr.uniform(0, 0.75); x = side * (W / 2 + 0.03); n = Vector((side, 0, 0))
        c = Vector((x, y, z)) + n * 0.02; t = n.cross(Vector((0, 0, 1))).normalized(); u = Vector((0, 0, 1)); s_ = rr.uniform(0.05, 0.09); a = rr.uniform(0, math.tau)
        t2 = t * math.cos(a) + u * math.sin(a); u2 = -t * math.sin(a) + u * math.cos(a)
        f = kb.faces.new([kb.verts.new(p) for p in (c + t2 * s_, c + u2 * s_ * 1.2 + n * 0.02, c - t2 * s_, c - u2 * s_ * 0.6)])
        if f.normal.dot(n) < 0: f.normal_flip()
    put("klimop", "groen", kb)
    # ---------- plantvak (OSM-cirkel r 2.7) met gebogen lage leuning (Papegaai_totaal, jaren 50) ----------
    RV = 2.65
    vak = [(RV * math.cos(math.radians(a)), RV * math.sin(math.radians(a))) for a in range(196, 345, 6)]
    vak = [(-W / 2 - 0.2, WY)] + vak + [(W / 2 + 0.2, WY)]
    bm = bmesh.new(); t_ = [bm.verts.new((x, y, 0.08)) for x, y in vak]; b_ = [bm.verts.new((x, y, -0.05)) for x, y in vak]
    ft = bm.faces.new(t_); fb_ = bm.faces.new(b_[::-1])
    for i in range(len(vak)): bm.faces.new((t_[i], b_[i], b_[(i + 1) % len(vak)], t_[(i + 1) % len(vak)]))
    bmesh.ops.triangulate(bm, faces=[ft, fb_], ngon_method="EAR_CLIP"); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f_ in bm.faces:
        if abs(f_.normal.z) > 0.5 and (f_.calc_center_median().z > 0) != (f_.normal.z > 0): f_.normal_flip()
    put("vak", "aarde", bm)
    for k in range(14):                                                                          # stenen in het vak (Reijnderspapegaai)
        a = rr.uniform(200, 340); r = rr.uniform(0.6, 2.2); sc = rr.uniform(0.12, 0.25)
        st = bz(-sc, sc, -sc * 0.7, sc * 0.7, -0.05, sc * 0.6, sc * 0.2)
        for v in st.verts: v.co += Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * sc * 0.25
        put("vak", "rots", st, TR(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0.05, rr.uniform(0, 360)))
    rail = [(RV + 0.1) * Vector((math.cos(math.radians(a)), math.sin(math.radians(a)))) for a in range(192, 349, 6)]
    rail = [Vector((-W / 2 - 0.35, WY - 0.05))] + rail + [Vector((W / 2 + 0.35, WY - 0.05))]
    for a, b in zip(rail, rail[1:]):
        put("hek", "leuning", btube([(a.x, a.y, 0.75), (b.x, b.y, 0.75)], 0.022, 6)); put("hek", "leuning", btube([(a.x, a.y, 0.38), (b.x, b.y, 0.38)], 0.016, 5))
        m = (a + b) / 2; d = b - a; coll_box(m.x, m.y, 0.55, d.length, 0.15, 1.1, math.degrees(math.atan2(d.y, d.x)))
    for i, p in enumerate(rail):
        if i % 3 == 0 or i == len(rail) - 1: put("hek", "leuning", btube([(p.x, p.y, 0.0), (p.x, p.y, 0.8)], 0.028, 6)); put("hek", "leuning", ell((p.x, p.y, 0.82), (0.045, 0.045, 0.045), 6, 4))
    # ---------- strook licht grind van de leuning tot het pad (405848924 loopt op y ~ -6) ----------
    pl = [(-4.6, -1.2), (-3.4, 0.6), (-2.3, 1.4)] + [((RV + 0.35) * math.cos(math.radians(a)), (RV + 0.35) * math.sin(math.radians(a))) for a in range(196, 345, 8)] + [(2.6, 1.6), (3.9, 0.4), (4.2, -2.6), (2.0, -4.6), (-0.6, -4.9), (-3.0, -3.6)]
    pl = [pl[0], pl[1], pl[2]] + pl[3:]
    # dichte plaat: buitenrand met een gat voor het vak -> als ring van vierhoeken tussen vak-boog en buitenrand is lastig; eenvoudig: hele plaat, vak ligt er 2 cm boven
    bm = bmesh.new()
    # strook tussen de leuning en de binnenrand van het pad 405848924 (bezoekers staan op het pad, direct tegen de leuning; eind60)
    outer = [(2.95 * math.cos(math.radians(a_)), 2.95 * math.sin(math.radians(a_))) for a_ in range(340, 199, -10)] + [(-3.4, -1.2), (-3.2, -3.8), (1.1, -4.65), (3.2, -5.2), (3.4, -1.3)]
    t_ = [bm.verts.new((x, y, 0.06)) for x, y in outer]; b_ = [bm.verts.new((x, y, -0.06)) for x, y in outer]
    ft = bm.faces.new(t_); fb_ = bm.faces.new(b_[::-1])
    for i in range(len(outer)): bm.faces.new((t_[i], b_[i], b_[(i + 1) % len(outer)], t_[(i + 1) % len(outer)]))
    bmesh.ops.triangulate(bm, faces=[ft, fb_], ngon_method="EAR_CLIP"); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f_ in bm.faces:
        if abs(f_.normal.z) > 0.5 and (f_.calc_center_median().z > 0) != (f_.normal.z > 0): f_.normal_flip()
    put("plein", "grind", bm)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        o = new_mesh_object(f"PA_{part}__{mat}", bm, "FORMS"); assign(o, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": outer, "vak": vak}, open(os.path.join(out, "papegaai_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
