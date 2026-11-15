"""03_loggia De Rode Schoentjes (1953, Anton Pieck): open loggia met rondbogen op gele zuilen, laag pannendak met groene boeiboord en klossen,
achterwand met muurschildering (Karen in gele jurk voor een kasteel), kaarsen op krularmen, kroonluchter, verhoogde dansvloer met geruite
glastegels en zigzagrand, groen hekje, rode bakstenen vloer, kunstrots links en achter met twee schildjes met Franse lelie, sprookjesboek.
Bronnen: Boekloc_RodeSchoentjes.jpg (hoofdfoto), Intro_rodeschoentjes.jpg, Rode-Schoentjes-weg.jpg, Karen2016.jpg, Ontwerp_muurschildering.jpg,
OSM 50911610 (7.45 x 4.96 m incl. rots). Modelframe: oorsprong = midden OSM-vorm = studs (49.59, 141.45); -Y = voorkant (NO, naar het pad);
z = 0 maaiveld. OSM -> model: X = -0.589*ox + 0.808*oy ; Y = -0.808*ox - 0.589*oy.
Gebruik: Blender -b -P 03_loggia.py -- --master RD_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
exec(open(os.path.join(HERE, "..", "..", "AR_ZesZwanen", "build", "zz_helpers.py")).read())
MATS = {"stuc": ((0.85, 0.8, 0.68, 1), 0.9), "zuil": ((0.82, 0.72, 0.48, 1), 0.7), "pannen": ((0.55, 0.3, 0.2, 1), 0.85), "groen": ((0.12, 0.33, 0.3, 1), 0.6),
        "rots": ((0.55, 0.55, 0.52, 1), 0.95), "baksteen": ((0.6, 0.3, 0.22, 1), 0.9), "tegelA": ((0.35, 0.55, 0.55, 1), 0.15), "tegelB": ((0.82, 0.86, 0.84, 1), 0.15),
        "zigzagdonker": ((0.18, 0.12, 0.2, 1), 0.6), "creme": ((0.9, 0.86, 0.74, 1), 0.7), "ijzer": ((0.05, 0.05, 0.05, 1), 0.45), "kaars": ((0.95, 0.93, 0.85, 1), 0.6),
        "vlam": ((1.0, 0.7, 0.3, 1), 0.2), "rood": ((0.7, 0.08, 0.06, 1), 0.4), "goud": ((0.8, 0.6, 0.2, 1), 0.3), "hout": ((0.3, 0.2, 0.12, 1), 0.8),
        "papier": ((0.92, 0.86, 0.7, 1), 0.9), "grind": ((0.86, 0.83, 0.76, 1), 0.95)}
LX0, LX1, LY0, LY1 = 0.0, 3.6, -2.1, 0.5           # loggia 3.6 breed x 2.6 diep (Rode-Schoentjes-weg: brede lage voorboog ~3.2 m tussen de zuilen)
HC = 2.45; HA = 3.35; EAVE = 3.8; TOP = 4.15        # segmentbogen: kapiteel 2.45, kruin voor 3.35 (vooraanzicht)


def mural_png(path):
    """muurschildering (vrij naar Pieck, Karen2016): bleke wand, kasteel in lijnen, meisje in gele jurk dansend, bloemetjes"""
    from PIL import Image, ImageDraw
    W, H = 1024, 768; im = Image.new("RGB", (W, H), (226, 216, 192)); d = ImageDraw.Draw(im)
    r = random.Random(3)
    for _ in range(4000): x, y = r.randrange(W), r.randrange(H); c = r.randint(-10, 8); d.point((x, y), fill=(226 + c, 216 + c, 192 + c))
    lijn = (150, 130, 110)
    for (x0, w, h, dak) in ((300, 90, 300, 90), (400, 60, 240, 70), (470, 120, 200, 60), (600, 70, 260, 80), (690, 50, 190, 60), (230, 60, 200, 60)):
        y1 = 460; y0 = y1 - h
        d.rectangle([x0, y0, x0 + w, y1], outline=lijn, width=3, fill=(232, 224, 204))
        d.polygon([(x0 - 8, y0), (x0 + w / 2, y0 - dak), (x0 + w + 8, y0)], outline=lijn, fill=(205, 170, 150))
        for k in range(2): d.rectangle([x0 + w * 0.3, y0 + 40 + k * 60, x0 + w * 0.45, y0 + 70 + k * 60], outline=lijn, width=2)
    # Karen: gele wijde rok, wit schort, rood lijfje, wit kapje, armen gespreid
    cx, cy = 520, 470
    d.pieslice([cx - 170, cy - 40, cx + 170, cy + 230], 200, 340, fill=(232, 190, 60), outline=(150, 110, 40), width=3)
    d.polygon([(cx - 150, cy + 60), (cx + 150, cy + 40), (cx + 60, cy - 10), (cx - 60, cy - 5)], fill=(232, 190, 60), outline=(150, 110, 40))
    d.polygon([(cx - 45, cy + 5), (cx + 45, cy), (cx + 30, cy + 120), (cx - 30, cy + 125)], fill=(245, 242, 232), outline=(150, 140, 120))
    d.polygon([(cx - 30, cy - 90), (cx + 30, cy - 90), (cx + 40, cy + 5), (cx - 40, cy + 5)], fill=(190, 40, 30), outline=(120, 30, 20))
    d.ellipse([cx - 26, cy - 150, cx + 26, cy - 92], fill=(240, 205, 175), outline=(150, 110, 90))
    d.polygon([(cx - 32, cy - 128), (cx, cy - 175), (cx + 32, cy - 128)], fill=(250, 250, 245), outline=(150, 140, 120))
    for s in (-1, 1): d.line([(cx + s * 30, cy - 75), (cx + s * 110, cy - 120), (cx + s * 150, cy - 105)], fill=(240, 205, 175), width=14)
    for s in (-1, 1): d.ellipse([cx + s * 60 - 14, cy + 200, cx + s * 60 + 14, cy + 214], fill=(200, 20, 20))
    for _ in range(18):
        x, y = r.randint(200, 820), r.randint(560, 720); d.line([(x, y), (x + r.randint(-6, 6), y + 30)], fill=(90, 130, 90), width=2)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(90, 120, 190))
    im.save(path)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    # ---------- loggia: achterwand + zijwand links, bogen voor en rechts op zuilen ----------
    w = bmesh.new()
    def addb(b_):
        me_ = bpy.data.meshes.new("_t"); b_.to_mesh(me_); b_.free(); w.from_mesh(me_); bpy.data.meshes.remove(me_)
    addb(bz(LX0 - 0.15, LX1 + 0.15, LY1, LY1 + 0.3, -0.05, EAVE))                                     # achterwand met de schildering (Rode-Schoentjes-weg)
    # bogenwanden boven de zuilen: voor (langs x) en rechts (langs y), boog uitgespaard
    def boogwand(xa, xb, y0, y1, langs_x=True, rise=0.9):
        pts = []
        c = (xb - xa); R = (c * c / 4 + rise * rise) / (2 * rise); mid = (xa + xb) / 2
        for i in range(17):
            x = xa + c * i / 16; pts.append((x, HC + rise - R + math.sqrt(max(0.0, R * R - (x - mid) ** 2))))
        poly = [(xa, HC), (xa, EAVE), (xb, EAVE), (xb, HC)] + pts[::-1][1:-1]
        bm = bmesh.new(); a_ = [bm.verts.new((x, y0, z)) for x, z in poly]; b_ = [bm.verts.new((x, y1, z)) for x, z in poly]
        bm.faces.new(a_[::-1]); bm.faces.new(b_)
        for i in range(len(poly)): bm.faces.new((a_[i], a_[(i + 1) % len(poly)], b_[(i + 1) % len(poly)], b_[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        if not langs_x: bmesh.ops.transform(bm, matrix=Matrix.Translation((LX1, 0, 0)) @ Matrix.Rotation(math.radians(90), 4, "Z") @ Matrix.Translation((-0, 0, 0)), verts=bm.verts)
        return bm
    addb(boogwand(LX0 + 0.32, LX1 - 0.32, LY0 - 0.15, LY0 + 0.15))
    rb = boogwand(LY0 + 0.32, LY1 - 0.32, -0.15, 0.15, rise=0.75)                                                 # rechterzijde: in x-z gebouwd, draaien naar y-z
    for v in rb.verts: x, y, z = v.co; v.co = Vector((LX1 - 0.16 + y, x, z))                          # zijboog RECHTS (Boekloc, negentig-2)
    addb(rb)
    lb = boogwand(LY0 + 0.32, LY1 - 0.32, -0.15, 0.15, rise=0.75)                                     # ook links een boog (vooraanzicht: 4 zuilen)
    for v in lb.verts: x, y, z = v.co; v.co = Vector((LX0 + 0.16 + y, x, z))
    addb(lb)
    put("loggia", "stuc", organisch(w, 0.04, 2, 0.4, 0.015, 1.5, 0.2))
    coll_box((LX0 + LX1) / 2, LY1 + 0.15, 1.7, LX1 - LX0, 0.3, 3.4)
    # zuilen (gele, Toscaans): voor links, voor rechts (hoek), achter rechts
    prof = [(0, 0), (0.24, 0), (0.24, 0.16), (0.19, 0.22), (0.16, 0.34), (0.15, HC - 0.32), (0.16, HC - 0.24), (0.22, HC - 0.12), (0.24, HC), (0, HC)]
    for (x, y) in ((LX0 + 0.16, LY0), (LX1 - 0.16, LY0), (LX1 - 0.16, LY1 - 0.16), (LX0 + 0.16, LY1 - 0.16)):
        put("zuilen", "zuil", blathe(prof, 14), TR(x, y, 0)); put("zuilen", "zuil", bz(x - 0.24, x + 0.24, y - 0.24, y + 0.24, HC - 0.02, HC + 0.12, 0.01))
        coll_box(x, y, HC / 2, 0.4, 0.4, HC)
    # dak: laag schilddak met pannen, groene boeiboord met klossen (Boekloc)
    o = 0.35
    put("dak", "groen", bsweep([(o, 0.0), (o, 0.16)], LX0 - 0.15, LX1 + 0.15, LY0 - 0.15, LY1 + 0.35, EAVE - 0.02))
    for k in range(12):
        t = k / 11
        for (x, y, rot) in ((LX0 - 0.15 + t * (LX1 - LX0 + 0.3), LY0 - 0.15 - 0.12, 0), (LX1 + 0.15 + 0.12, LY0 - 0.15 + t * (LY1 - LY0 + 0.5), 90)):
            put("dak", "groen", bz(-0.06, 0.06, -0.14, 0.14, -0.12, 0.02), TR(x, y, EAVE - 0.0, rot))
    put("dak", "pannen", hip(LX0 - 0.15 - o, LX1 + 0.15 + o, LY0 - 0.15 - o, LY1 + 0.35 + o, EAVE + 0.14, EAVE + 0.2, LX0 + 0.9, LX1 - 0.9, (LY0 + LY1) / 2, TOP))
    for k in range(16):                                                                               # pannenrijen (ribbels)
        t = k / 15; z = EAVE + 0.22 + t * (TOP - EAVE - 0.25)
        sx = (LX1 - LX0 + 0.3 + 2 * o) / 2 * (1 - t * 0.85); sy = (LY1 - LY0 + 0.5 + 2 * o) / 2 * (1 - t)
        cx, cy = (LX0 + LX1) / 2, (LY0 + LY1 + 0.2) / 2
        put("dak", "pannen", bsweep([(0.0, 0.0), (0.0, 0.03)], cx - sx, cx + sx, cy - sy, cy + sy, z))
    # ---------- vloer, dansvloer, hekje ----------
    put("vloer", "baksteen", bz(LX0 - 0.3, LX1 + 0.35, LY0 - 0.35, LY1, 0.0, 0.08))
    for k in range(18): x = LX0 - 0.3 + k * 0.22; put("vloer", "creme", bz(x - 0.006, x + 0.006, LY0 - 0.35, LY1, 0.08, 0.083))
    dx0, dx1, dy0, dy1, dh = LX0 + 0.62, LX1 - 0.62, LY0 + 0.85, LY1 - 0.3, 0.9
    put("dansvloer", "creme", bz(dx0, dx1, dy0, dy1, 0.08, dh - 0.05))
    n = 14                                                                                            # zigzagrand
    for side in range(4):
        for k in range(n):
            if side < 2:
                xa = dx0 + (dx1 - dx0) * k / n; xb = dx0 + (dx1 - dx0) * (k + 1) / n; y = dy0 - 0.005 if side == 0 else dy1 + 0.005
                tri = [(xa, y, dh - 0.12), (xb, y, dh - 0.12), ((xa + xb) / 2, y, dh - 0.42)]
            else:
                ya = dy0 + (dy1 - dy0) * k / n; yb = dy0 + (dy1 - dy0) * (k + 1) / n; x = dx0 - 0.005 if side == 2 else dx1 + 0.005
                tri = [(x, ya, dh - 0.12), (x, yb, dh - 0.12), (x, (ya + yb) / 2, dh - 0.42)]
            bm = bmesh.new(); bm.faces.new([bm.verts.new(p) for p in tri]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm2 = bmesh.new(); bm2.from_mesh((lambda me: (bm.to_mesh(me), me)[1])(bpy.data.meshes.new("_z"))); bm.free()
            r_ = bmesh.ops.extrude_face_region(bm2, geom=list(bm2.faces)); off = Vector((0, -0.01 if side == 0 else 0.01, 0)) if side < 2 else Vector((-0.01 if side == 2 else 0.01, 0, 0))
            bmesh.ops.translate(bm2, vec=off, verts=[g for g in r_["geom"] if isinstance(g, bmesh.types.BMVert)]); bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces)
            put("dansvloer", "zigzagdonker", bm2)
    put("dansvloer", "creme", bz(dx0 - 0.06, dx1 + 0.06, dy0 - 0.06, dy1 + 0.06, dh - 0.08, dh - 0.02, 0.01))
    gx, gy = 12, 8                                                                                    # geruite glazen dansvloer
    for i in range(gx):
        for j in range(gy):
            xa = dx0 + (dx1 - dx0) * i / gx; ya = dy0 + (dy1 - dy0) * j / gy
            put("dansvloer", "tegelA" if (i + j) % 2 else "tegelB", bz(xa + 0.006, xa + (dx1 - dx0) / gx - 0.006, ya + 0.006, ya + (dy1 - dy0) / gy - 0.006, dh - 0.02, dh))
    for s, (x, y, a) in enumerate(((1.45, -0.85, 20), (1.85, -0.6, -15))):                              # de dansende rode schoentjes
        Ms = TR(x, y, dh, a)
        put("schoentjes", "rood", ell((0, 0, 0.04), (0.12, 0.045, 0.04), 10, 6), Ms)
        put("schoentjes", "rood", btube([(0.08, 0, 0.0), (0.09, 0, 0.09)], 0.012, 5), Ms)
        put("schoentjes", "rood", ell((-0.04, 0, 0.08), (0.04, 0.03, 0.03), 8, 6), Ms)
    coll_box((dx0 + dx1) / 2, (dy0 + dy1) / 2, dh / 2, dx1 - dx0, dy1 - dy0, dh)
    hx0, hx1, hy0, hy1, hh = dx0 - 0.3, dx1 + 0.3, dy0 - 0.35, LY1 - 0.05, 1.0                      # groen hekje rond de dansvloer
    for (a, b) in (((hx0, hy1), (hx0, hy0)), ((hx0, hy0), (hx1, hy0)), ((hx1, hy0), (hx1, hy1))):                 # muur sluit de achterkant
        A, B = Vector(a), Vector(b); L = (B - A).length; k = int(L / 0.11)
        for i in range(k + 1):
            p = A.lerp(B, i / k); put("hek", "groen", btube([(p.x, p.y, 0.08), (p.x, p.y, hh)], 0.012, 4))
        for z in (0.12, hh - 0.04): put("hek", "groen", btube([(A.x, A.y, z), (B.x, B.y, z)], 0.02, 5))
        for i in range(int(L / 1.0) + 1):
            p = A.lerp(B, min(1, i / max(1, int(L / 1.0)))); put("hek", "groen", btube([(p.x, p.y, 0.08), (p.x, p.y, hh + 0.05)], 0.03, 6))
        mid = (A + B) / 2; coll_box(mid.x, mid.y, 0.55, max(0.1, abs(B.x - A.x)), max(0.1, abs(B.y - A.y)), 1.1)
    put("hek", "groen", ell(((dx0 + dx1) / 2, hy0 - 0.02, 0.6), (0.13, 0.02, 0.13), 10, 8)); put("hek", "goud", ell(((dx0 + dx1) / 2, hy0 - 0.03, 0.6), (0.09, 0.01, 0.09), 10, 8))
    # ---------- muurschildering, kaarsen, kroonluchter ----------
    tex = os.path.join(ROOT, "textures", "RD_mural_kleur.png"); os.makedirs(os.path.dirname(tex), exist_ok=True)
    try: mural_png(tex)
    except ImportError: pass                                                                         # PIL ontbreekt in Blender: build/mural.py maakt hem
    mb = bmesh.new(); uv = mb.loops.layers.uv.new()
    q = [(LX0 + 0.3, LY1 - 0.01, 0.95), (LX1 - 0.3, LY1 - 0.01, 0.95), (LX1 - 0.3, LY1 - 0.01, 3.3), (LX0 + 0.3, LY1 - 0.01, 3.3)]
    f = mb.faces.new([mb.verts.new(p) for p in q])
    for l_, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): l_[uv].uv = (u, v)
    bmesh.ops.recalc_face_normals(mb, faces=mb.faces); mb.normal_update()
    if f.normal.y > 0: f.normal_flip()
    mob = new_mesh_object("BAKE_mural", mb, "FORMS")
    for s in (-1, 1):                                                                               # kaarsen op krularmen
        x = (LX0 + LX1) / 2 + s * 0.85
        put("kaarsen", "ijzer", btube([(x, LY1, 1.55), (x, LY1 - 0.18, 1.55), (x - s * 0.06, LY1 - 0.25, 1.6), (x, LY1 - 0.28, 1.66)], 0.015, 5))
        put("kaarsen", "kaars", btube([(x, LY1 - 0.18, 1.58), (x, LY1 - 0.18, 1.86)], 0.025, 8)); put("kaarsen", "vlam", ell((x, LY1 - 0.18, 1.9), (0.015, 0.015, 0.035), 6, 4))
        LAMPS_.append([round(x, 2), LY1 - 0.25, 1.95])
    cx, cy = (LX0 + LX1) / 2 + 0.55, (LY0 + LY1) / 2 + 0.55
    put("kaarsen", "ijzer", btube([(cx, cy, HA + 0.2), (cx, cy, 2.55)], 0.012, 5))
    put("kaarsen", "ijzer", blathe([(0.22, 0.0), (0.24, 0.02), (0.05, 0.05), (0, 0.05)], 12), TR(cx, cy, 2.5))
    for k in range(5):
        a = k * math.tau / 5; px, py = cx + 0.22 * math.cos(a), cy + 0.22 * math.sin(a)
        put("kaarsen", "kaars", btube([(px, py, 2.52), (px, py, 2.66)], 0.016, 6)); put("kaarsen", "vlam", ell((px, py, 2.69), (0.01, 0.01, 0.025), 6, 4))
    LAMPS_.append([round(cx, 2), round(cy, 2), 2.6])
    # ---------- kunstrots links en achter (gestapelde blokken) met schildjes met Franse lelie ----------
    # rechte muur achter de loggia, symmetrisch: links en rechts even laag, in het midden boven het dak uit (Boekloc + Daan)
    # stenen muur (Daan: "gewoon een rechte muur van steen"): grote liggende blokken in lagen, verspringende voegen, getrapte bovenrand.
    rr = random.Random(53)
    def steenwand(a, b, d, hoogte, seed):
        """rechte wand van a naar b (voorvlak), dikte d naar achter; hoogte(t) = max hoogte op positie t (0..1)"""
        r = random.Random(seed); A, B = Vector(a), Vector(b); L = (B - A).length; u = (B - A).normalized(); n = Vector((-u.y, u.x))   # n = achter
        out = bmesh.new(); z = 0.0; rij = 0
        while True:
            hz = r.uniform(0.62, 0.92); t = -r.uniform(0, 0.6) if rij % 2 else 0.0; any_ = False
            while t < L:
                w = r.uniform(1.2, 2.2); t0, t1 = max(0.0, t), min(L, t + w)
                hm = hoogte(((t0 + t1) / 2) / L)
                if z + hz * 0.5 < hm:
                    uit = r.uniform(-0.06, 0.1)
                    bb = bz(t0 + 0.025, t1 - 0.025, -uit, d, z + 0.025, z + hz - 0.025, 0.05)
                    for v in bb.verts: v.co += Vector((r.uniform(-0.03, 0.03), r.uniform(-0.03, 0.03), r.uniform(-0.03, 0.03)))
                    M_ = Matrix(((u.x, n.x, 0, A.x), (u.y, n.y, 0, A.y), (0, 0, 1, 0), (0, 0, 0, 1)))
                    bmesh.ops.transform(bb, matrix=M_, verts=bb.verts)
                    me_ = bpy.data.meshes.new("_t"); bb.to_mesh(me_); bb.free(); out.from_mesh(me_); bpy.data.meshes.remove(me_); any_ = True
                t += w
            z += hz; rij += 1
            if not any_ or z > 6: break
        kern = bz(0.15, L - 0.15, 0.25, d - 0.1, 0, 0.5, 0); M_ = Matrix(((u.x, n.x, 0, A.x), (u.y, n.y, 0, A.y), (0, 0, 1, 0), (0, 0, 0, 1)))
        return out
    # symmetrisch rond het midden van de loggia (Daan: "de muur is symmetrisch, rechts loopt hij hetzelfde af als links")
    MX = (LX0 + LX1) / 2; HALF = MX + 3.74                                                                      # linkereind -3.74 (Boekloc) -> rechtereind gespiegeld
    prof = lambda t: 2.4 + 2.6 * min(1.0, min(t, 1.0 - t) / 0.42)                                               # laag aan beide uiteinden, achter de loggia boven het dak
    put("rots", "rots", organisch(steenwand((MX - HALF, LY1 + 0.3), (MX + HALF, LY1 + 0.3), 1.2, prof, 53), 0.035, 1, 0.4, 0.035, 0.45, 0.25))
    coll_box(MX, LY1 + 0.9, 2.2, 2 * HALF, 1.2, 4.4)
    for (x, y, rot) in ((MX - 2.5, LY1 + 0.25, 0), (MX + 2.5, LY1 + 0.25, 0)):                                         # schildjes (luidsprekers)
        M_ = TR(x, y, 1.95, rot)
        sh = [(-0.2, 0.2), (0.2, 0.2), (0.2, -0.05), (0.0, -0.25), (-0.2, -0.05)]
        put("schild", "rood", boutline(sh, -0.05, 0.05), M_); put("schild", "goud", band(sh + [sh[0]], 0.03, -0.07, 0.05), M_)
        put("schild", "goud", ell((0, -0.08, 0.02), (0.05, 0.02, 0.12), 8, 6), M_)
        for s in (-1, 1): put("schild", "goud", ell((s * 0.07, -0.08, 0.04), (0.06, 0.02, 0.035), 8, 6), M_)
    # sprookjesboek op smeedijzeren standaard links voor de rots (Boekloc)
    MB = TR(-1.1, -0.9, 0, 10)
    put("boek", "ijzer", btube([(-0.25, 0, 0), (-0.25, 0, 0.8)], 0.025, 6), MB); put("boek", "ijzer", btube([(0.25, 0, 0), (0.25, 0, 0.8)], 0.025, 6), MB)
    put("boek", "ijzer", btube([(-0.25, 0, 0.4), (0, 0, 0.55), (0.25, 0, 0.4)], 0.015, 5), MB)
    MBk = MB @ TR(0, 0, 0.84) @ Matrix.Rotation(math.radians(-25), 4, "X")
    put("boek", "hout", bz(-0.42, 0.42, -0.26, 0.26, -0.03, 0.0, 0.01), MBk)
    for sx in (-1, 1): put("boek", "papier", bz(0.02 if sx > 0 else -0.4, 0.4 if sx > 0 else -0.02, -0.24, 0.24, 0.0, 0.035, 0.008), MBk)
    coll_box(-1.1, -0.9, 0.5, 0.7, 0.4, 1.0, 10)
    # pleintje voor de loggia in licht grind (OSM-pad 405848924 loopt erlangs)
    pl = [(-4.5, -2.6), (5.5, -2.6), (6.8, -6.2), (-4.5, -6.0)]
    bm = bmesh.new(); t_ = [bm.verts.new((x, y, 0.1)) for x, y in pl]; b_ = [bm.verts.new((x, y, -0.02)) for x, y in pl]
    bm.faces.new(t_); bm.faces.new(b_[::-1])
    for i in range(4): bm.faces.new((t_[i], b_[i], b_[(i + 1) % 4], t_[(i + 1) % 4]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update()
    if bm.faces[0].normal.z < 0:
        for f_ in bm.faces: f_.normal_flip()
    put("plein", "grind", bm)
    # voetpad (OSM 405848924) langs de loggia: links aansluitend op het Pinokkio-plein (PLEIN-hoek 8.09,-7.49 in Pinokkio-frame),
    # rechts door tot de splitsing richting De Prinses op de Erwt (21.58,-20.06). Breedte 3.2 m, iets lager dan het pleintje.
    PAD = [(-22.2, -13.6), (-21.26, -12.89), (-9.43, -4.75), (-3.18, -4.16), (4.83, -6.13), (13.15, -11.8), (21.58, -20.06), (22.3, -20.8)]
    for _ in range(3):
        q = [PAD[0]]
        for a_, b2 in zip(PAD, PAD[1:]): q += [(0.75 * a_[0] + 0.25 * b2[0], 0.75 * a_[1] + 0.25 * b2[1]), (0.25 * a_[0] + 0.75 * b2[0], 0.25 * a_[1] + 0.75 * b2[1])]
        PAD = q + [PAD[-1]]
    bm = bmesh.new(); top, bot = [], []
    for i, (x, y) in enumerate(PAD):
        a_, b2 = PAD[max(0, i - 1)], PAD[min(len(PAD) - 1, i + 1)]; tx, ty = b2[0] - a_[0], b2[1] - a_[1]; L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L * 1.6, tx / L * 1.6
        top.append((bm.verts.new((x + nx, y + ny, 0.08)), bm.verts.new((x - nx, y - ny, 0.08))))
        bot.append((bm.verts.new((x + nx, y + ny, -0.04)), bm.verts.new((x - nx, y - ny, -0.04))))
    for i in range(len(PAD) - 1):
        bm.faces.new((top[i][0], top[i][1], top[i + 1][1], top[i + 1][0])); bm.faces.new((bot[i][0], bot[i + 1][0], bot[i + 1][1], bot[i][1]))
        bm.faces.new((top[i][0], top[i + 1][0], bot[i + 1][0], bot[i][0])); bm.faces.new((top[i][1], bot[i][1], bot[i + 1][1], top[i + 1][1]))
    bm.faces.new((top[0][0], bot[0][0], bot[0][1], top[0][1])); bm.faces.new((top[-1][0], top[-1][1], bot[-1][1], bot[-1][0]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f_ in bm.faces:
        if abs(f_.normal.z) > 0.5 and (f_.calc_center_median().z > 0) != (f_.normal.z > 0): f_.normal_flip()
    put("pad", "grind", bm)
    for (part, mat), bm in PARTS.items():
        if len(bm.faces) == 0: continue
        ob = new_mesh_object(f"RD_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    json.dump({"colliders": COLL, "lamps": LAMPS_, "plein": pl, "pad": [list(p) for p in PAD]}, open(os.path.join(out, "loggia_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "tris",
                             sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); mm = a[a.index("--master") + 1] if "--master" in a else None
    if mm: build(mm)
