"""maak_groen.py -> roblox/plaats_zeszwanen_groen.luau: bos rond de open plek (lemma: 'verborgen open plek in het bos', naaldbomen),
ondergroei tussen pad en bos, asters langs het water (lemma), varens tussen de rotsen. Klonen uit ServerStorage.BomenBronV3,
VVEchtePlanten/VVPlanten en de paarse bloem uit HerautenpleinGroen. Alles buiten water, pad, kasteel en hekken."""
import json, math, os, random
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = {e["id"]: e for e in json.load(open(D + "/ref/osm_model.json"))}
def P(i): p = [tuple(q) for q in O[i]["pts"]]; return p[:-1] if p[0] == p[-1] else p
def inside(px, py, poly):
    c = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi: c = not c
        j = i
    return c
def segdist(px, py, pts):
    b = 1e9
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-9; t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
        b = min(b, math.hypot(px - ax - t * dx, py - ay - t * dy))
    return b
VIJ = [P("961616757"), P("961616758"), P("961616760")]; PAD = P("961616754"); KAS = P("961616753")
VOET = [P(i) for i in ("1169016139", "1255787237", "1169016140", "1255787243", "729126648")]
ROTS = [P("961616756"), P("961616759")]
def d_water(x, y): return min(segdist(x, y, v + [v[0]]) for v in VIJ) * (-1 if any(inside(x, y, v) for v in VIJ) else 1)
def d_pad(x, y): return -1 if inside(x, y, PAD) else min(min(segdist(x, y, f) for f in VOET) - 0.95, segdist(x, y, PAD + [PAD[0]]))
def vrij(x, y, m_water, m_pad, m_kas=1.0):
    return d_water(x, y) > m_water and d_pad(x, y) > m_pad and not inside(x, y, KAS) and segdist(x, y, KAS + [KAS[0]]) > m_kas and not any(inside(x, y, r) for r in ROTS)
R = random.Random(2019); out = []
def zet(kind, x, y, s=1.0): out.append([kind, round(x, 2), round(y, 2), round(R.uniform(0, 360)), round(s, 2)])
# bomen: poisson-achtig, alleen in de rand/achter het kasteel (niet tussen pad en vijver aan de voorkant)
bomen = []
for _ in range(6000):
    x, y = R.uniform(-15, 24), R.uniform(-31, 12)
    voorkant = -22 < y < 2 and -9 < x < 14
    if voorkant or not vrij(x, y, 2.5, 1.8, 2.5): continue
    if all(math.hypot(x - bx, y - by) > 3.0 for bx, by in bomen):
        bomen.append((x, y))
        soort = R.choices(["den0", "den1", "beuk0", "beuk1", "kastanje0", "eik0", "berk0"], [4, 4, 2, 2, 1, 2, 1])[0]
        zet(soort, x, y, R.uniform(0.85, 1.15))
# ondergroei: rododendron/taxus/struik in de band tussen pad en bos
for _ in range(2500):
    x, y = R.uniform(-15, 24), R.uniform(-31, 12)
    if vrij(x, y, 1.2, 0.6, 1.0) and d_pad(x, y) < 5.5 and R.random() < 0.35:
        zet(R.choice(["rododendron0", "rododendron1", "taxus0", "taxus1", "struik0", "struik1", "PH_shrub_03_1", "PH_shrub_02_3"]), x, y, R.uniform(0.8, 1.2))
# asters langs het water (lemma: 'langs het water zijn uiteraard asters geplant'), in groepjes
for _ in range(9000):
    x, y = R.uniform(-15, 24), R.uniform(-31, 12)
    dw = d_water(x, y)
    if 0.25 < dw < 1.6 and d_pad(x, y) > 0.25 and not inside(x, y, KAS) and segdist(x, y, KAS + [KAS[0]]) > 0.6 and not any(inside(x, y, r) for r in ROTS):
        if R.random() < 0.35: zet("bloem_paars", x, y, R.uniform(0.9, 1.3))
# varens tussen de rotsen en op de oever
for r in ROTS + [P("961616753")]:
    for _ in range(400):
        x, y = R.uniform(-12, 12), R.uniform(-18, 8)
        if 0.1 < segdist(x, y, r + [r[0]]) < 1.2 and d_water(x, y) > 0.2 and d_pad(x, y) > 0.3 and not inside(x, y, KAS) and R.random() < 0.55:
            zet(R.choice(["PH_fern_02_0", "PH_fern_02_2", "PH_fern_02_3", "varen1"]), x, y, R.uniform(0.9, 1.3))
src = open(D + "/roblox/groen_template.luau").read().replace("@PLANTEN@", json.dumps(out).replace("[", "{").replace("]", "}"))
open(D + "/roblox/plaats_zeszwanen_groen.luau", "w").write(src)
from collections import Counter
print(len(out), Counter(o[0] for o in out).most_common())
