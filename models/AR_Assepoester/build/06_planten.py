"""06_planten: plantposities (modelmeters) voor Studio -> exports/planten.json en roblox/planten_tabel.luau.
Bronnen: BomenBronV3 (bomen/heesters, schaal ~3 zoals LangnekGroen), VVEchtePlanten (Poly Haven), VVPlanten (bloemen).
Regels (WERKWIJZE): niets in de looproute, ~0.7 m vrij van hagen, groene stroken langs paden beplanten, bos als achtergrond."""
import json, math, random, sys
sys.path.insert(0, "build")
D = json.load(open("exports/omgeving_extra.json"))
RNG = random.Random(1950)

def inside(px, py, poly):
    c = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi: c = not c
        j = i
    return c

def segd(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay; t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)

def polyd(p, pts): return min(segd(p, a, b) for a, b in zip(pts, pts[1:]))

def catmull(pts, n=8):
    P = [pts[0]] + pts + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t * t + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t ** 3) for c in (0, 1)))
    out.append(tuple(pts[-1])); return out

HEDGES = [([(-3.77, -6.75), (10.49, -6.6), (11.2, -7.6)], 0.95), ([(-7.21, -6.99), (-12.62, -7.26), (-13.71, 1.11), (-7.2, 1.0)], 0.95),
          ([(-7.25, -6.99), (-7.25, -1.75)], 0.85), ([(7.6, -0.4), (7.6, 3.6), (5.6, 4.9)], 0.85)]
ENTRY = catmull([(-5.3, -14.0), (-5.0, -10.0), (-5.1, -7.4), (-5.2, -5.8)], 6)
EXIT = catmull([(6.6, -4.4), (9.0, -4.3), (11.6, -3.4), (13.8, -3.3), (16.3, -3.9)], 8)
COURT = D["binnenplaats"]
HOUSE = [(-6.45, -0.1), (6.45, -0.1), (6.45, 16.4), (-6.45, 16.4)]
KLAROEN = [(3.4, 14.3), (13.8, 14.3), (13.8, 24.4), (3.4, 24.4)]
ROCKS = [(8.4, -5.9), (9.3, -6.1), (10.7, -2.2), (11.4, -1.6), (12.6, -5.4), (13.4, -5.7), (9.6, -2.4), (14.2, -1.9), (10.1, -2.75), (9.4, -1.9)]
SOLID = [(-6.75, -6.85, 0.6), (-4.15, -6.85, 0.6), (-2.6, -7.75, 0.9), (-7.25, -1.45, 0.5)]

def vrij(x, y, rad=0.3, hedge=0.7, path=0.15):
    if inside(x, y, COURT) or inside(x, y, HOUSE) or inside(x, y, KLAROEN): return False
    for pts, w in HEDGES:
        if polyd((x, y), pts) < w / 2 + hedge + rad * 0.5: return False
    if polyd((x, y), ENTRY) < 1.5 + path + rad * 0.6: return False
    if polyd((x, y), EXIT) < 1.3 + path + rad * 0.6: return False
    if any(math.hypot(x - a, y - b) < 0.55 + rad * 0.5 for a, b in ROCKS): return False
    if any(math.hypot(x - a, y - b) < r + rad * 0.5 for a, b, r in SOLID): return False
    if 15.3 < x < 15.9: return False                         # parkhek / uitgangsboog
    return True

P = []
def add(n, x, y, s, rot=None): P.append([n, round(x, 2), round(y, 2), round(s, 2), round(RNG.uniform(0, 360) if rot is None else rot)])
# A middenperk: rozen/bloemen dicht (tuin_nieuw.jpg)
for i in range(10):
    for j in range(5):
        x = -2.15 + i * 0.3 + RNG.uniform(-0.06, 0.06); y = -3.75 + j * 0.33 + RNG.uniform(-0.06, 0.06)
        add(RNG.choice(["bloem_rood", "bloem_rood", "bloem_roze", "bloem_wit", "PH_flower_gazania_%d" % RNG.randrange(8)]), x, y, RNG.uniform(1.0, 1.3))
# B grafje: paarse bloemen + maagdenpalm rond de zerk (nieuwepoort-aankomst-2023.jpg)
for k in range(46):
    x = RNG.uniform(-4.0, -1.0); y = RNG.uniform(-9.0, -7.05)
    if -3.25 < x < -1.95 and -8.45 < y < -7.05: continue
    if not vrij(x, y, 0.2, hedge=0.15, path=0.05): continue
    add(RNG.choice(["bloem_paars", "bloem_paars", "lavendel", "PH_periwinkle_plant_%d" % RNG.randrange(6)]), x, y, RNG.uniform(1.1, 1.5))
# bomen rondom (achtergrondbos, Daan: vol bos), heesters, varens
TREES = [(-10.5, -11.5), (-0.8, -12.8), (3.6, -10.2), (8.4, -9.8), (13.2, -9.2), (-16.2, -3.0), (-16.5, 4.2), (-10.5, 4.6), (11.6, 4.2),
         (15.8, 7.0), (-7.5, 17.0), (-3.0, 19.0), (-12.5, -15.5), (1.5, -16.5), (17.5, -8.0), (-17.5, -10.0)]
for k, (x, y) in enumerate(TREES):
    if vrij(x, y, 1.0, hedge=1.2): add(["beuk0", "eik0", "kastanje1", "beuk1", "den0", "eik1", "kastanje0", "den1", "berk0"][k % 9], x, y, RNG.uniform(2.6, 3.4))
def scatter(region, n, kinds, smin, smax, rad, tries=4000, hedge=0.7):
    x0, x1, y0, y1 = region; c = 0
    for _ in range(tries):
        if c >= n: break
        x = RNG.uniform(x0, x1); y = RNG.uniform(y0, y1)
        if not vrij(x, y, rad, hedge=hedge): continue
        if any(math.hypot(x - p[1], y - p[2]) < rad * 1.6 for p in P): continue
        add(RNG.choice(kinds), x, y, RNG.uniform(smin, smax)); c += 1
RODO = ["rododendron0", "rododendron1"]; SHRUB = ["PH_shrub_02_%d" % i for i in range(4)] + ["PH_shrub_03_%d" % i for i in range(4)]
FERN = ["PH_fern_02_%d" % i for i in range(4)]; LOW = ["PH_periwinkle_plant_%d" % i for i in range(6)] + ["PH_shrub_sorrel_01_%d" % i for i in range(6)]
# C langs het aanlooppad (buiten de hagen)
scatter((-9.5, -1.0, -15.5, -7.6), 10, RODO + ["taxus0", "taxus1"], 2.2, 2.9, 1.1)
scatter((-9.5, -1.0, -15.5, -7.6), 28, SHRUB, 1.0, 1.6, 0.55)
scatter((-9.5, -1.0, -15.5, -7.6), 40, FERN + LOW, 1.3, 2.0, 0.35)
# D uitgangstuin (D6z: dicht groen, jonge naaldbomen, rotsjes)
scatter((7.9, 15.2, -3.2, 3.8), 7, ["taxus0", "taxus1", "rododendron1"], 2.2, 3.0, 1.0)
scatter((7.9, 15.2, -3.2, 3.8), 26, SHRUB, 1.0, 1.7, 0.55)
scatter((7.9, 15.2, -3.2, 3.8), 45, FERN + LOW, 1.3, 2.1, 0.33)
scatter((6.8, 15.2, -6.25, -5.0), 10, FERN + LOW, 1.2, 1.8, 0.3, hedge=0.35)
# E dienstplaatsje: heesters langs de haag binnen
scatter((-13.0, -7.9, -6.4, 0.5), 6, RODO + ["taxus1"], 2.0, 2.6, 1.0, hedge=0.4)
# F rondom buiten de hagen (bosrand)
scatter((-18.0, 18.0, -17.5, -7.8), 22, RODO + SHRUB, 1.2, 2.6, 0.9)
scatter((-18.5, -14.6, -9.0, 10.0), 14, RODO + SHRUB + FERN, 1.2, 2.6, 0.8)
json.dump(P, open("exports/planten.json", "w"))
lua = "return {" + ",".join('{"%s",%s,%s,%s,%s}' % tuple(p) for p in P) + "}"
open("roblox/planten_tabel.luau", "w").write("-- gegenereerd door build/06_planten.py: {soort, x, y, schaal, draaiing} in modelmeters\n" + lua + "\n")
from collections import Counter
print(len(P), Counter(p[0].split("_")[0] if p[0].startswith("PH") is False else p[0][:9] for p in P).most_common(12))
