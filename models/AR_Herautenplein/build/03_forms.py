"""03_forms Herautenplein + Kikkerkoningfontein (zonder kikkers: die komen via generate_mesh in Studio).
Indeling 1:1 uit OSM (ref/osm_lokaal.json, Prinsenpoort-frame: -Y = van de poort het plein op) + foto's (Herautenplein2010/april09/DVD,
Boekloc_Kikkerkoning, Kikkerkoningoverzicht, Intro_kikkerkoning, Rooster_kikkerkoning_2023). Zie asset-brief.md.
Gebruik: Blender -b -P 03_forms.py -- --master AR_Herautenplein_master.blend"""
import bpy, bmesh, sys, os, math, random, json
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
_src = open(os.path.join(HERE, "..", "..", "AR_Assepoester", "build", "03_forms.py")).read().split("# ---- ramen ----")[0]
exec(_src)
RNG = random.Random(1952)
MATS = {
    "baksteen": ((0.55, 0.36, 0.28, 1), 0.9), "steen": ((0.70, 0.68, 0.62, 1), 0.9), "kassei": ((0.45, 0.43, 0.40, 1), 0.9),
    "plavuis": ((0.42, 0.40, 0.38, 1), 0.9), "gras": ((0.18, 0.28, 0.10, 1), 0.9), "haag": ((0.10, 0.20, 0.08, 1), 0.9),
    "taxus": ((0.08, 0.16, 0.06, 1), 0.9), "bodem": ((0.20, 0.16, 0.11, 1), 1.0), "water": ((0.10, 0.12, 0.08, 1), 0.05),
    "rots": ((0.16, 0.13, 0.11, 1), 0.9), "goud": ((0.80, 0.60, 0.20, 1), 0.3), "hek": ((0.06, 0.16, 0.12, 1), 0.5),
    "hout": ((0.10, 0.22, 0.16, 1), 0.7), "paal": ((0.18, 0.11, 0.06, 1), 0.7), "ijzer": ((0.05, 0.06, 0.06, 1), 0.45),
    "glaslamp": ((0.9, 0.8, 0.6, 1), 0.2), "kant_papier": ((0.9, 0.88, 0.8, 1), 0.8), "rood": ((0.62, 0.08, 0.06, 1), 0.5),
    "ruwsteen": ((0.50, 0.49, 0.46, 1), 0.9), "binnenbak": ((0.55, 0.57, 0.55, 1), 0.6),
}
OSM = json.load(open(os.path.join(ROOT, "ref", "osm_lokaal.json")))
WAY = {w["id"]: [Vector(p) for p in w["pts"]] for w in OSM["ways"]}
LAMPEN = [Vector(n["p"]) for n in OSM["nodes"] if n["tags"].get("highway") == "street_lamp" and n["p"][1] < -5 and abs(n["p"][0]) < 20]
TUINEN = {"NW": "55443655", "NO": "55443656", "ZW": "55443657", "ZO": "55443649"}
FC = Vector((-0.22, -28.48))                                   # midden fontein (OSM-water 55350691)
COLL = []; LAMPS_ = []
def coll_box(cx, cy, cz, sx, sy, sz, ang=0.0): COLL.append([round(v, 3) for v in (cx, cy, cz, sx, sy, sz, ang)])


def omhoog(b_):
    b_.normal_update()
    for f_ in b_.faces:
        if f_.normal.z < -0.5: f_.normal_flip()
    b_.normal_update(); return b_


def vlak(poly, z, mat, part):
    """vlak loopvlak met dikke rand (onderkant tot -0.15), bovenkant naar boven"""
    b = bmesh.new(); top = [b.verts.new((p.x, p.y, z)) for p in poly]; bot = [b.verts.new((p.x, p.y, -0.15)) for p in poly]
    ft = b.faces.new(top)
    for i in range(len(poly)): b.faces.new((top[i], bot[i], bot[(i + 1) % len(poly)], top[(i + 1) % len(poly)]))
    bmesh.ops.triangulate(b, faces=[ft], ngon_method="EAR_CLIP"); bmesh.ops.recalc_face_normals(b, faces=b.faces); omhoog(b); put(part, mat, b)


def rand_box(a, b, w, z0, z1, mat, part, inset=0.0, ch=0.02, poly_c=None):
    """balk langs segment a-b (breedte w, hoogte z0..z1), optioneel 'inset' richting het middelpunt poly_c"""
    d = b - a; L = d.length; ang = math.degrees(math.atan2(d.y, d.x)); n = Vector((-d.y, d.x)).normalized()
    if poly_c is not None and (poly_c - (a + b) / 2).dot(n) < 0: n = -n
    o = a + n * inset
    put(part, mat, bz(-w / 2 * 0.0, L, -w / 2, w / 2, z0, z1, ch), TR(o.x, o.y, 0, ang))


def zwaartepunt(poly): return sum(poly[:-1], Vector((0.0, 0.0))) / (len(poly) - 1)


def ruwe_muur(a, b, h=0.6, w=0.42, part="muurtjes"):
    """laag droog gestapeld muurtje van ruwe natuursteen (Herautenplein-april09): lagen platte stenen + afdekstenen"""
    a, b = Vector(a), Vector(b); d = b - a; L = d.length; u = d.normalized(); ang = math.degrees(math.atan2(d.y, d.x)); k = 0.0
    while k < L - 0.05:
        ln = min(RNG.uniform(0.3, 0.55), L - k + 0.04); q = a + u * (k + ln / 2); z = -0.05
        while z < h - 0.12:
            hh = RNG.uniform(0.09, 0.15); off = RNG.uniform(-0.06, 0.06)
            put(part, "ruwsteen", bbox(ln + 0.03, w + RNG.uniform(-0.03, 0.03), hh, 0, 0, 0, 0.03), TR(q.x + u.x * off, q.y + u.y * off, z + hh / 2, ang + RNG.uniform(-4, 4)))
            z += hh - 0.01
        put(part, "ruwsteen", bbox(ln + 0.05, w + 0.06, 0.1, 0, 0, 0, 0.04), TR(q.x, q.y, z + 0.04, ang + RNG.uniform(-4, 4)))
        k += ln
    c = (a + b) / 2; coll_box(c.x, c.y, 0.4, L, w, 0.8, ang)


def galgenlantaarn(p, rz):
    lx, ly = p.x, p.y
    put("lantaarns", "paal", bz(lx - 0.09, lx + 0.09, ly - 0.09, ly + 0.09, 0, 3.3, 0.02))
    ax_ = Vector((math.cos(math.radians(rz)), math.sin(math.radians(rz))))
    for sg in (-1, 1):
        e_ = p + ax_ * sg * 0.8
        put("lantaarns", "paal", btube([(lx, ly, 3.0), (e_.x, e_.y, 3.0)], 0.05, 6))
        m_ = p + ax_ * sg * 0.45; put("lantaarns", "paal", btube([(lx + ax_.x * sg * 0.1, ly + ax_.y * sg * 0.1, 2.55), (m_.x, m_.y, 2.98)], 0.03, 5))
        c_ = p + ax_ * sg * 0.72
        put("lantaarns", "ijzer", btube([(c_.x, c_.y, 2.95), (c_.x, c_.y, 2.75)], 0.01, 4))
        put("lantaarns", "ijzer", blathe([(0, 2.72), (0.13, 2.68), (0.13, 2.66), (0.1, 2.64), (0.1, 2.36), (0.07, 2.32), (0, 2.3)], 6), TR(c_.x, c_.y, 0))
        put("lantaarns", "glaslamp", blathe([(0, 2.37), (0.085, 2.37), (0.085, 2.63), (0, 2.63)], 6), TR(c_.x, c_.y, 0))
        LAMPS_.append([round(c_.x, 2), round(c_.y, 2), 2.5])
    coll_box(lx, ly, 1.6, 0.2, 0.2, 3.2)


def bank(c, rz, L=2.4):
    M = TR(c.x, c.y, 0, rz)
    put("bankjes", "hout", bz(-L / 2, L / 2, -0.22, 0.22, 0.42, 0.49, 0.01), M)
    for xx in (-L / 2 + 0.2, L / 2 - 0.2): put("bankjes", "baksteen", bz(xx - 0.16, xx + 0.16, -0.2, 0.2, 0.0, 0.42), M)
    coll_box(c.x, c.y, 0.25, L if abs(math.sin(math.radians(rz))) < 0.5 else 0.45, 0.45 if abs(math.sin(math.radians(rz))) < 0.5 else L, 0.5)


def build(master):
    if os.path.exists(master): open_master(master)
    else: bpy.ops.wm.read_factory_settings(use_empty=True)
    clear_owned(); PARTS.clear(); COLL.clear(); LAMPS_.clear()
    for n, (c, r) in MATS.items(): material("MAT_" + n, c, r)
    ring = WAY["1169014962"]                                             # ringpad (sett): x -13.9..13.8, y -10.4..-46.6
    X0, X1, Y0, Y1 = -13.8 - 1.75, 13.8 + 1.75, -46.6 - 1.75, -10.45 + 1.75
    # ================= GRIND: het hele Herautenplein volgens OSM-relatie 2907394 (outer 369580589), met gaten voor het grachtje
    # van de fontein en het bosje; incl. het uitsteekseltje in de hoek van de Magische Klok (voor de 6 herauten) =================
    H_ = 3.98 + 0.16; fx, fy = FC.x, FC.y
    REL = json.load(open(os.path.join(ROOT, "ref", "plein_relatie.json")))
    outer = [Vector(p) for p in REL["outer"][0]["pts"][:-1]]
    INNER = {w["id"]: [Vector(p) for p in w["pts"][:-1]] for w in REL["inner"]}
    def prisma(poly, z0, z1):
        b = bmesh.new(); top = [b.verts.new((p.x, p.y, z1)) for p in poly]; bot = [b.verts.new((p.x, p.y, z0)) for p in poly]
        ft = b.faces.new(top); fb = b.faces.new(bot[::-1])
        for i in range(len(poly)): b.faces.new((top[i], bot[i], bot[(i + 1) % len(poly)], top[(i + 1) % len(poly)]))
        bmesh.ops.triangulate(b, faces=[ft, fb], ngon_method="EAR_CLIP"); bmesh.ops.recalc_face_normals(b, faces=b.faces); return b
    def obj_van(b, naam):
        me = bpy.data.meshes.new(naam); b.to_mesh(me); b.free(); o = bpy.data.objects.new(naam, me); bpy.context.scene.collection.objects.link(o); return o
    pv = obj_van(prisma(outer, -0.15, 0.08), "_plein")
    snij = [obj_van(prisma([Vector((fx - H_, fy - H_)), Vector((fx + H_, fy - H_)), Vector((fx + H_, fy + H_)), Vector((fx - H_, fy + H_))], -1, 1), "_gracht"),
            obj_van(prisma(INNER["505382909"], -1, 1), "_bosje")]
    for c_ in snij:
        md = pv.modifiers.new("b" + c_.name, "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = c_; md.solver = "EXACT"
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(pv.evaluated_get(dg))
    b = bmesh.new(); b.from_mesh(me); bpy.data.meshes.remove(me); omhoog(b); put("keien", "kassei", b)
    for o_ in [pv] + snij: bpy.data.objects.remove(o_, do_unlink=True)
    vlak([Vector((-1.6, -4.3)), Vector((1.6, -4.3)), Vector((1.6, -8.5)), Vector((-1.6, -8.5))], 0.08, "kassei", "keien")   # aanloop van de Prinsenpoort (OSM 967458491)
    # ================= ZUIDDEEL: hagen (h 1 m), gebogen bloemvakken met laag bakstenen muurtje (Herautenplein99), bankjes, bosje =================
    for hid in ("505382910", "505382911"):
        hp = INNER[hid]; put("hagen_zuid", "taxus", prisma(hp, 0.05, 1.0))
        xs = [p.x for p in hp]; ys = [p.y for p in hp]; coll_box((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, 0.5, max(xs) - min(xs), max(ys) - min(ys), 1.0)
    EZ = sum(INNER["55423191"], Vector((0.0, 0.0))) / len(INNER["55423191"])          # midden Ezeltje-strek-je
    BLOEMVAKKEN = []
    for gid in ("505382906", "505382907", "505382908"):
        gp = INNER[gid]; gc = sum(gp, Vector((0.0, 0.0))) / len(gp)
        for a, b_ in zip(gp, gp[1:] + gp[:1]):
            rand_box(a, b_, 0.22, -0.05, 0.4, "baksteen", "bloemvakken", inset=0.11, ch=0.01, poly_c=gc)
        put("bloemvakken", "bodem", prisma(gp, 0.05, 0.32))
        BLOEMVAKKEN.append([[round(p.x, 2), round(p.y, 2)] for p in gp])
        d_ = (EZ - gc); bc = gc + d_.normalized() * 1.25                                        # bankje aan de pleinkant van het vak, kijkt naar het Ezeltje
        bank(bc, math.degrees(math.atan2(d_.y, d_.x)) + 90, 2.6)

    # natuurstenen plaveisel rond de fontein (Boekloc_Kikkerkoning, Rooster 2023): het pleintje tussen de tuininhammen
    for (a0, a1, b0, b1) in ((-7.2, 7.2, fy + H_, -21.0), (-7.2, 7.2, -36.45, fy - H_), (-7.2, fx - H_, fy - H_, fy + H_), (fx + H_, 7.2, fy - H_, fy + H_)):
        vlak([Vector((a0, b1)), Vector((a1, b1)), Vector((a1, b0)), Vector((a0, b0))], 0.095, "plavuis", "plavuis")
    # ================= TUINVAKKEN =================
    for naam, wid in TUINEN.items():
        poly = WAY[wid][:-1]; c = zwaartepunt(WAY[wid])
        # gazon als losse rechthoeken (de vakken zijn haaks; oorknippen van de getrapte vorm gaf driehoeken buiten de haag)
        xs_ = sorted(set(round(p.x, 2) for p in poly)); ys_ = sorted(set(round(p.y, 2) for p in poly))
        def binnen_(px_, py_):
            c_ = False; pl = list(poly); j = len(pl) - 1
            for i in range(len(pl)):
                a_, b_ = pl[i], pl[j]
                if ((a_.y > py_) != (b_.y > py_)) and (px_ < (b_.x - a_.x) * (py_ - a_.y) / (b_.y - a_.y) + a_.x): c_ = not c_
                j = i
            return c_
        for i in range(len(xs_) - 1):
            for j in range(len(ys_) - 1):
                if xs_[i + 1] - xs_[i] < 0.3 or ys_[j + 1] - ys_[j] < 0.3: continue
                if binnen_((xs_[i] + xs_[i + 1]) / 2, (ys_[j] + ys_[j + 1]) / 2):
                    put("gazon", "gras", omhoog(bz(xs_[i] - 0.01, xs_[i + 1] + 0.01, ys_[j] - 0.01, ys_[j + 1] + 0.01, -0.15, 0.13)))
        for a, b in zip(WAY[wid], WAY[wid][1:]):                         # lage buxusrand op de tuinrand (iets naar binnen)
            m_ = (a + b) / 2
            if (abs(a.x - b.x) < 0.2 and abs(abs(m_.x) - 1.72) < 0.15) or (abs(a.y - b.y) < 0.2 and min(abs(m_.y + 26.48), abs(m_.y + 30.48)) < 0.15 and abs(m_.x) > 7.5):
                continue                                                        # hier staat het ruwe muurtje
            rand_box(a, b, 0.42, 0.1, 0.55, "haag", "hagen", inset=0.22, ch=0.08, poly_c=c)
        # hoge taxusblok langs de buitenzijde (x = ±11.7) met bloembak van baksteen ervoor (Herautenplein2010)
        sx = 1 if c.x > 0 else -1
        xo = max(sx * p.x for p in poly); ys = sorted(p.y for p in poly if abs(sx * p.x - xo) < 0.25)
        ya, yb = ys[0], ys[-1]
        xin = sx * (xo - 0.62)
        tx0, tx1 = sorted((xin, sx * (xo - 0.05)))
        put("taxus", "taxus", bz(tx0, tx1, ya + 0.15, yb - 0.15, 0.1, 1.35, 0.18))
        xb0, xb1 = sorted((sx * (xo + 0.05), sx * (xo + 0.85)))
        put("bakken", "baksteen", bz(xb0, xb1, ya + 0.3, yb - 0.3, -0.1, 0.38, 0.01))
        put("bakken", "bodem", omhoog(bz(xb0 + 0.1, xb1 - 0.1, ya + 0.4, yb - 0.4, 0.3, 0.36)))
        coll_box((xb0 + xb1) / 2 - sx * 0.3, (ya + yb) / 2, 0.7, 1.4, yb - ya, 1.4)
        # spiraaltopiary (4 lagen) midden in het gazon + twee bollen (Herautenplein-april09)
        tc = Vector((sx * 8.0, c.y + (2.0 if c.y < -28.5 else -2.0) * 0))
        tc = c.copy()
        for k, (r, h) in enumerate(((0.62, 0.42), (0.5, 0.38), (0.36, 0.34), (0.22, 0.3))):
            z0 = 0.13 + sum(hh for _, hh in ((0.62, 0.42), (0.5, 0.38), (0.36, 0.34), (0.22, 0.3))[:k])
            put("topiary", "taxus", blathe([(0, z0), (r * 0.8, z0 + 0.02), (r, z0 + h * 0.45), (r * 0.75, z0 + h), (0, z0 + h + 0.02)], 14), TR(tc.x, tc.y))
        coll_box(tc.x, tc.y, 0.8, 1.2, 1.2, 1.6)
    # ================= LAGE RUWE MUURTJES bij de ingangen van het middenkruis (Herautenplein-april09) =================
    for sx in (-1, 1):
        for sy in (-1, 1):
            yy = -26.48 if sy > 0 else -30.48
            ruwe_muur((sx * 12.0, yy + sy * 0.25), (sx * 7.75, yy + sy * 0.25))                  # oost/west-ingang (op de tuinrand)
            xx = 1.72 if sx > 0 else -1.72
            ruwe_muur((xx + sx * 0.25, -12.6 if sy > 0 else -36.55), (xx + sx * 0.25, -20.9 if sy > 0 else -44.4))   # middenpad noord/zuid
    # ================= GALGENLANTAARNS op de OSM-punten =================
    for p in LAMPEN: galgenlantaarn(p, 0 if abs(p.y + 12.6) < 1 or abs(p.y + 44.1) < 1 else 90)
    # ================= BANKJES langs de inhammen van het fonteinpleintje =================
    for sx in (-1, 1):
        for y in (-23.75, -33.2): bank(Vector((sx * 6.85, y)), 90)
    # ================= KIKKERKONINGFONTEIN =================
    cx, cy = FC.x, FC.y
    # grachtje rondom (OSM-water 8 x 8): natuurstenen rand, water laag
    G = 3.98; GB = 0.3
    for sx in (-1, 1):
        put("fontein", "steen", bz(cx + sx * G - GB / 2, cx + sx * G + GB / 2, cy - G - GB / 2, cy + G + GB / 2, -0.5, 0.14, 0.02))
        put("fontein", "steen", bz(cx - G - GB / 2, cx + G + GB / 2, cy + sx * G - GB / 2, cy + sx * G + GB / 2, -0.5, 0.14, 0.02))
    put("fontein", "water", omhoog(bz(cx - G, cx + G, cy - G, cy + G, -0.6, -0.22)))
    # gemetselde bak (verhoogd) met lichte natuurstenen afdekking, binnen een laag water
    B = 2.9; BH = 0.82
    put("fontein", "baksteen", bz(cx - B, cx + B, cy - B, cy + B, -0.6, BH))
    for sx in (-1, 1):
        put("fontein", "steen", bz(cx + sx * B - 0.3, cx + sx * B + 0.07, cy - B - 0.07, cy + B + 0.07, BH, BH + 0.12, 0.015))
        put("fontein", "steen", bz(cx - B - 0.07, cx + B + 0.07, cy + sx * B - 0.3, cy + sx * B + 0.07, BH, BH + 0.12, 0.015))
    put("fontein", "binnenbak", omhoog(bz(cx - B + 0.3, cx + B - 0.3, cy - B + 0.3, cy + B - 0.3, BH - 0.2, BH - 0.02)))
    # rotsblokken in een ring rond de spuitmond (Intro_kikkerkoning / Kikkers-tuinslang) + gouden bal
    for k in range(64):
        a = k * math.tau / 64 + RNG.uniform(-0.04, 0.04); r = RNG.uniform(0.55, 1.05); lay = k % 3
        s = (RNG.uniform(0.22, 0.38), RNG.uniform(0.18, 0.3), RNG.uniform(0.14, 0.26))
        z = BH - 0.02 + s[2] / 2 + (0.15 if lay == 2 and r < 0.85 else 0.0)
        put("fontein", "rots", bbox(*s, 0, 0, 0, 0.03), TR(cx + r * math.cos(a), cy + r * math.sin(a), z, math.degrees(a) + RNG.uniform(-25, 25)) @ Matrix.Rotation(math.radians(RNG.uniform(-14, 14)), 4, "X"))
    put("fontein", "ijzer", btube([(cx, cy, BH), (cx, cy, BH + 0.35)], 0.03, 6))
    put("fontein", "goud", blathe([(0, -0.3)] + [(0.3 * math.sin(t * math.pi / 10), -0.3 * math.cos(t * math.pi / 10)) for t in range(1, 10)] + [(0, 0.3)], 18), TR(cx, cy, BH + 0.68))
    coll_box(cx, cy, 0.5, 2 * G + 0.3, 2 * G + 0.3, 1.0)
    # laag groen hek om het grachtje (Boekloc_Kikkerkoning)
    HG = G + 0.35
    for sx in (-1, 1):
        for horiz in (True, False):
            if horiz: a, b = Vector((cx - HG, cy + sx * HG)), Vector((cx + HG, cy + sx * HG))
            else: a, b = Vector((cx + sx * HG, cy - HG)), Vector((cx + sx * HG, cy + HG))
            n = int((b - a).length / 1.2)
            for k in range(n + 1):
                p = a.lerp(b, k / n); put("hek", "hek", btube([(p.x, p.y, 0.05), (p.x, p.y, 0.62)], 0.022, 6))
            for z in (0.3, 0.58): put("hek", "hek", btube([(a.x, a.y, z), (b.x, b.y, z)], 0.016, 6))
    # sprookjesboek op een krulstandaard aan de westzijde
    bq = Vector((cx - HG - 0.6, cy)); MB = TR(bq.x, bq.y, 0, 90)
    put("boek", "ijzer", btube([(0, 0, 0), (0, 0, 0.85)], 0.03, 6), MB); put("boek", "ijzer", bz(-0.25, 0.25, -0.2, 0.2, 0, 0.03), MB)
    put("boek", "kant_papier", bz(-0.36, 0.36, -0.24, 0.24, 0, 0.04), MB @ TR(0, 0, 0.85) @ Matrix.Rotation(math.radians(-25), 4, "X"))
    put("boek", "rood", bz(-0.38, 0.38, -0.26, 0.26, -0.02, 0.0), MB @ TR(0, 0, 0.85) @ Matrix.Rotation(math.radians(-25), 4, "X"))
    # ================= wegschrijven =================
    for (part, mat), bm in PARTS.items():
        ob = new_mesh_object(f"HP_{part}__{mat}", bm, "FORMS"); assign(ob, bpy.data.materials["MAT_" + mat])
    out = os.path.join(ROOT, "exports"); os.makedirs(out, exist_ok=True)
    hoeken = [[round(cx + sx * (B - 0.15), 2), round(cy + sy * (B - 0.15), 2), BH + 0.12] for sx in (-1, 1) for sy in (-1, 1)]
    json.dump({"colliders": COLL, "lamps": LAMPS_, "kikkers": hoeken, "fontein": [cx, cy, G], "plein": [X0, X1, Y0, Y1],
               "bloembakken": [[sx * 12.15, ya_yb] for sx in (-1, 1) for ya_yb in ((-15.4, -26.5), (-30.5, -41.5))], "bloemvakken": BLOEMVAKKEN,
               "bosje": [[round(p.x, 2), round(p.y, 2)] for p in INNER["505382909"]], "ezeltje": [round(EZ.x, 2), round(EZ.y, 2)]},
              open(os.path.join(out, "plein_extra.json"), "w"))
    save_master(master); log("built", len([o for o in bpy.data.objects if o.get("owner") == OWNER_TAG]), "colliders", len(COLL),
                             "tris", sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.get("owner") == OWNER_TAG and o.type == "MESH"))


if __name__ == "__main__":
    a = argv_after_dashes(); m = a[a.index("--master") + 1] if "--master" in a else None
    if m: build(m)
