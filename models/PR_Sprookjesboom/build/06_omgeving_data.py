"""
06_omgeving_data: omgeving van de Sprookjesboom uit OSM (ref/osm_lokaal.json, meters t.o.v. het stamhart, x oost, y noord).
Draai met een Python die shapely heeft (venv). Schrijft exports/omgeving_data.json voor 06_omgeving.py (Blender) en de Studio-scripts.
 - paving: plein (pedestrian area) + paden (footways 3.4 m breed, Daan), afgerond, vrij van de beekgeul; opsluitband alleen buitenrand
 - beek: smalle waterloop uit OSM (natural=water, 40 punten) gladgemaakt; water = beek + 0.45 m (oever in het terrein)
 - stenen langs de waterlijn (2 rijen), keien op het gras voor de boom (front.jpg), bankjes (OSM, zonder rugleuning), prullenbak (riet)
 - planten: rododendrons achter/naast de boom (front.jpg, front_wide.jpg), bosbodem, borders langs paden, grasplukjes op de oever
 - vrij: punten waar geen horizonboom mag staan (paden, plein, beek, rond de stam)
"""
import json, math, os, random
from shapely.geometry import LineString, Polygon, Point, MultiPolygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "..")
d = json.load(open(os.path.join(A, "ref", "osm_lokaal.json")))
rnd = random.Random(2026)
R_SCENE = 15.0          # Daan: alleen de scène bij de boom, geen paden door het park
scene = Point(0, 0).buffer(R_SCENE, quad_segs=32)


def chaikin(pts, it=2):
    for _ in range(it):
        q = []
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            q += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        pts = q
    return pts


# ---- beek: grootste water-polygoon die voor de boom langs loopt
waters = [Polygon(w["pts"]) for w in d["wegen"] if w["tags"].get("natural") == "water" and len(w["pts"]) > 3]
beek = max((p for p in waters if p.distance(Point(0, 0)) < 8), key=lambda p: p.area)
beek = Polygon(chaikin(list(beek.buffer(0.15).buffer(-0.15).exterior.coords)[:-1], 2)).buffer(0)
water = beek.buffer(0.25, quad_segs=12)        # front_wide.jpg: water ~1.9 m breed
geul = beek.buffer(1.0, quad_segs=12)          # oever: niets bestraat/beplant binnen 1 m van de beek
# ---- paving
paths = []
for w in d["wegen"]:
    tg = w["tags"]
    if "highway" not in tg or tg.get("area") != "yes" or len(w["pts"]) < 3: continue   # alleen het pleintje (geen paden)
    pl = Polygon(w["pts"]).buffer(0.6).buffer(-0.6)
    if pl.distance(Point(0, 0)) < 8: paths.append(pl)
paving = unary_union(paths).intersection(scene).difference(geul).buffer(0.3).buffer(-0.3).simplify(0.02)
band = paving.boundary.buffer(0.07, quad_segs=4, cap_style="flat").intersection(scene.buffer(-0.2))
# ---- stamvoet (wortellobben ~ r 2.7, grote voeten tot 3.2)
stam = Point(0, 0).buffer(2.9)


def polys(g):
    if g.is_empty: return []
    gs = list(g.geoms) if hasattr(g, "geoms") else [g]
    return [{"ext": [[round(x, 3), round(y, 3)] for x, y in p.exterior.coords[:-1]],
             "holes": [[[round(x, 3), round(y, 3)] for x, y in r.coords[:-1]] for r in p.interiors]} for p in gs if p.area > 0.02]


def ring_pts(ring, step):
    L = ring.length; n = max(8, int(L / step))
    return [ring.interpolate(i * L / n) for i in range(n)]


# ---- stenen langs de waterlijn: punt + richting naar buiten
stenen = []
wr = water.exterior
for row, (off, step, rmin, rmax) in enumerate(((-0.10, 0.30, 0.08, 0.15), (0.06, 0.20, 0.11, 0.22), (0.26, 0.21, 0.10, 0.21),
                                               (0.46, 0.24, 0.09, 0.19), (0.66, 0.34, 0.07, 0.15))):
    for p in ring_pts(wr, step):
        q = wr.interpolate(wr.project(p) + 0.05); nx, ny = q.y - p.y, -(q.x - p.x)
        L = math.hypot(nx, ny) or 1; nx, ny = nx / L, ny / L
        if water.contains(Point(p.x + nx * 0.1, p.y + ny * 0.1)): nx, ny = -nx, -ny
        o = off + rnd.uniform(-0.06, 0.06)
        x, y = p.x + nx * o, p.y + ny * o
        if Point(x, y).within(scene.buffer(-1)):
            stenen.append([round(x, 3), round(y, 3), round(rnd.uniform(rmin, rmax), 3), rnd.randint(0, 5), rnd.randint(0, 359)])
# ---- keien op het gras voor de boom (front.jpg: ~10 stenen tussen stam en beek, front_wide.jpg)
keien = []
while len(keien) < 12:
    a = rnd.uniform(math.radians(-170), math.radians(-10)); r = rnd.uniform(2.9, 5.0)
    x, y = r * math.cos(a), r * math.sin(a)
    if not geul.buffer(-0.5).contains(Point(x, y)) and not paving.buffer(0.3).contains(Point(x, y)):
        keien.append([round(x, 2), round(y, 2), round(rnd.uniform(0.18, 0.42), 2), rnd.randint(0, 5), rnd.randint(0, 359)])
# ---- bankjes (OSM amenity=bench, geen rugleuning): kijken naar de boom als die dichtbij is, anders naar het pad
banken = []
for p in d["punten"]:
    if p["tags"].get("amenity") != "bench": continue
    x, y = p["x"], p["y"]
    if not paving.buffer(0.5).contains(Point(x, y)): continue          # alleen de bankjes op het pleintje
    pt = Point(x, y)
    if pt.distance(geul) < 0.8:                     # niet in de oever
        far = geul.buffer(0.9).exterior; q = far.interpolate(far.project(pt)); x, y = q.x, q.y
    if math.hypot(x, y) < 15: ang = math.degrees(math.atan2(-y, -x))
    else:
        q = paving.exterior.interpolate(paving.exterior.project(Point(x, y))) if paving.geom_type == "Polygon" else None
        ang = math.degrees(math.atan2((q.y - y) if q else 0, (q.x - x) if q else 1))
    banken.append([round(x, 2), round(y, 2), round(ang, 1)])
bak = []   # prullenbak staat aan het hoofdpad (16, -10): buiten de scène
# ---- planten
vrij_plant = unary_union([paving.buffer(0.15), water.buffer(0.35), stam, Point(0, 0).buffer(R_SCENE).difference(scene.buffer(-1))])
for x, y, *_ in banken: vrij_plant = vrij_plant.union(Point(x, y).buffer(1.2))
planten = []      # [soort, x, y, schaal, draai]


def add(soort, x, y, s):
    planten.append([soort, round(x, 2), round(y, 2), round(s, 2), rnd.randint(0, 359)])


# rododendrons: boog achter en naast de boom (front.jpg: links en rechts achter de stam, 2.5-3 m hoog)
for k in range(16):
    a = math.radians(-15 + k * 210 / 15 + rnd.uniform(-5, 5)); r = rnd.uniform(4.2, 7.0)
    x, y = r * math.cos(a), r * math.sin(a)
    if not vrij_plant.contains(Point(x, y)): add("rodo", x, y, rnd.uniform(1.35, 1.75))
for k in range(14):       # tweede rij verder naar achter
    a = math.radians(10 + k * 160 / 13 + rnd.uniform(-6, 6)); r = rnd.uniform(8.0, 11.5)
    x, y = r * math.cos(a), r * math.sin(a)
    if not vrij_plant.contains(Point(x, y)): add(rnd.choice(["rodo", "rodo", "taxus", "struik"]), x, y, rnd.uniform(1.1, 1.6))
# bodemlaag: raster met jitter; soort hangt af van de plek
gx = 0.55
y0 = -R_SCENE
while y0 < R_SCENE:
    x0 = -R_SCENE
    while x0 < R_SCENE:
        x, y = x0 + rnd.uniform(-0.25, 0.25), y0 + rnd.uniform(-0.25, 0.25)
        pt = Point(x, y); r = math.hypot(x, y)
        x0 += gx
        if vrij_plant.contains(pt) or r > R_SCENE - 1: continue
        dpad = paving.distance(pt); dbeek = water.distance(pt)
        if dbeek < 1.4 and rnd.random() < 0.55:                       # oever: gras en varens
            add(rnd.choice(["gras", "gras", "varen", "brandnetel"]), x, y, rnd.uniform(0.9, 1.5))
        elif dpad < 1.0 and rnd.random() < 0.45:                      # border langs het pad
            add(rnd.choice(["maagdenpalm", "zuring", "struikje", "maagdenpalm"]), x, y, rnd.uniform(1.0, 1.5))
        elif y > 3.5 and r < 13 and rnd.random() < 0.30:              # achter de boom: bosbodem onder de rododendrons
            add(rnd.choice(["varen", "varen", "brandnetel", "maagdenpalm"]), x, y, rnd.uniform(1.2, 2.0))
        elif r < 3.6 and y < 0 and rnd.random() < 0.10:               # voet van de boom: losse plukjes tussen de paddenstoelen
            add("gras", x, y, rnd.uniform(0.8, 1.2))
        elif dpad > 3.0 and dbeek > 3.0 and r > 9 and rnd.random() < 0.035:   # verder weg: bosgroepjes
            soort = rnd.choice(["varen", "struik", "brandnetel", "struikje"])
            for j in range(rnd.randint(3, 7)):
                add(soort, x + rnd.gauss(0, 0.5), y + rnd.gauss(0, 0.5), rnd.uniform(1.0, 1.8))
    y0 += gx
planten = [p for p in planten if not vrij_plant.contains(Point(p[1], p[2]))]
# ---- laag zwart hekje langs de pleinrand aan de waterkant (Sprookjesboomopening.jpg, KindbijSprookjesboom.JPG)
hek = []
if not paving.is_empty:
    pl = max(paving.geoms, key=lambda g: g.area) if hasattr(paving, "geoms") else paving
    ring = pl.exterior.parallel_offset(0.25, "left" if pl.exterior.is_ccw else "right") if False else pl.buffer(-0.25).exterior
    run = []
    for q in ring_pts(ring, 1.2):
        if water.distance(q) < 1.9: run.append([round(q.x, 2), round(q.y, 2)])
        elif run:
            if len(run) > 1: hek.append(run)
            run = []
    if len(run) > 1: hek.append(run)
# ---- bodembedekker: dicht tapijt op de oever aan de boomkant (Sprookjesboomoverview.jpg)
tapijt_vlak = Point(0, 0).buffer(6.0).difference(water.buffer(0.55)).difference(Point(0, 0).buffer(2.6)).difference(paving.buffer(0.3))
y0 = -6.5
while y0 < 6.5:
    x0 = -6.5
    while x0 < 6.5:
        x, y = x0 + rnd.uniform(-0.12, 0.12), y0 + rnd.uniform(-0.12, 0.12); x0 += 0.34
        if y < 2.0 and tapijt_vlak.contains(Point(x, y)) and rnd.random() < 0.85:
            planten.append(["maagdenpalm", round(x, 2), round(y, 2), round(rnd.uniform(0.75, 1.1), 2), rnd.randint(0, 359)])
    y0 += 0.34
# ---- wortelboogjes die uit de oever steken (Sprookjesboomoverview.jpg, Rodosb.jpg)
stubs = []
while len(stubs) < 9:
    a_ = rnd.uniform(math.radians(-175), math.radians(-5)); r_ = rnd.uniform(3.0, 5.6)
    x, y = r_ * math.cos(a_), r_ * math.sin(a_)
    if water.distance(Point(x, y)) > 0.5 and not paving.buffer(0.4).contains(Point(x, y)) and all(math.hypot(x - s[0], y - s[1]) > 1.2 for s in stubs):
        stubs.append([round(x, 2), round(y, 2), round(math.degrees(a_) + rnd.uniform(-50, 50), 1), round(rnd.uniform(0.5, 0.9), 2)])
# ---- roeptoeter (tonderzwammen op een stompje) aan de pleinkant bij het hekje, dicht bij de wortel met klauwen
toeter = None
if hek:
    allp = [q for run in hek for q in run]
    tx, ty = min(allp, key=lambda q: math.hypot(q[0] - 1.6, q[1] + 6.4))
    toeter = [round(tx, 2), round(ty - 0.55, 2), round(math.degrees(math.atan2(-ty, -tx)), 1)]
# ---- lantaarns: klassieke zwarte Efteling-lantaarn op de pleinrand, zo ver mogelijk van het water (Sprookjesboomopening.jpg)
lant = []
if not paving.is_empty:
    cand = sorted(ring_pts(pl.buffer(-0.4).exterior, 0.5), key=lambda q: -water.distance(q))
    for q in cand:
        if all(math.hypot(q.x - l[0], q.y - l[1]) > 7 for l in lant): lant.append([round(q.x, 2), round(q.y, 2)])
        if len(lant) == 2: break
for x, y, *_ in stubs: vrij_plant = vrij_plant.union(Point(x, y).buffer(0.6))
planten = [p for p in planten if not (p[0] != "maagdenpalm" and any(math.hypot(p[1] - s[0], p[2] - s[1]) < 0.6 for s in stubs))]
# ---- vrij voor horizonbomen: punten op een raster in paden/plein/beek/stam
vrij_boom = unary_union([paving.buffer(0.5), geul, Point(0, 0).buffer(7.5)])
vrij = []
for i in range(-80, 81):
    for j in range(-80, 81):
        x, y = i * 0.5, j * 0.5
        if vrij_boom.contains(Point(x, y)) and (i % 3 == 0 and j % 3 == 0): vrij.append([x, y])
out = {"paving": polys(paving), "band": polys(band), "water": polys(water), "beek": polys(beek),
       "stenen": stenen, "keien": keien, "banken": banken, "bak": bak, "planten": planten, "vrij": vrij,
       "hek": hek, "stubs": stubs, "toeter": toeter, "lantaarns": lant}
os.makedirs(os.path.join(A, "exports"), exist_ok=True)
json.dump(out, open(os.path.join(A, "exports", "omgeving_data.json"), "w"))
from collections import Counter
print("paving m2", round(paving.area), "band", len(out["band"]), "beek breed ~", round(beek.area / (beek.length / 2), 2), "m, water m2", round(water.area, 1))
print("stenen", len(stenen), "keien", len(keien), "banken", len(banken), "bak", len(bak), "vrij-punten", len(vrij))
print("planten", len(planten), Counter(p[0] for p in planten))
print("hek-stukken", [len(r) for r in hek], "stubs", len(stubs), "toeter", toeter, "lantaarns", lant)
