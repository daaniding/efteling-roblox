"""06_planten Sneeuwwitje: plantposities (modelmeters) -> roblox/planten_tabel.luau. Bronnen als Assepoester (BomenBronV3, VVEchtePlanten, VVPlanten).
Perken (Sneeuwwitjegrot.jpg / Grotvernieuwd.jpg): banden rood (salvia), wit, geel; bloembak bij de ronde toren rood (front.jpg); potten oranje.
Bos achter en naast kasteel en grot (Sprookjesbos: dicht), varens/rododendrons tegen de rots, niets op paden of plein."""
import json, math, random
D = json.load(open("exports/omgeving_extra.json")); RNG = random.Random(1937)
def inside(px, py, poly):
    c = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi: c = not c
        j = i
    return c
def segd(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)
PADEN = [([(-9.1, -21.8), (-9.5, -10.4), (-5.6, -5.0), (4.2, -2.4), (7.1, -4.2), (12.6, -7.5), (23.8, -10.0), (25.3, -10.4)], 2.0),
         ([(-9.1, -21.8), (3.4, -18.7), (7.3, -17.2), (11.5, -19.0)], 1.6), ([(12.6, -7.5), (12.9, -13.6), (11.5, -19.0)], 1.5),
         ([(22.5, -7.2), (23.8, -10.0), (25.7, -16.1)], 1.3), ([(7.1, -4.2), (8.6, -0.6)], 1.2)]
KASTEEL = [(-7.6, 0.2), (7.8, 0.2), (7.8, 9.6), (-7.6, 9.6)]
GROT = [(15.28, 2.26), (18.64, 1.76), (21.95, -1.88), (21.34, -2.42), (23.69, -6.61), (22.53, -7.16), (21.46, -7.62), (19.6, -6.57), (16.08, -6.16), (13.4, -4.59), (12.46, -3.62), (10.18, -2.96), (10.42, -1.63), (10.68, -0.31), (12.49, -0.51)]
def vrij(x, y, rad=0.3, pad=0.25):
    if inside(x, y, D["plein"]) or inside(x, y, KASTEEL) or inside(x, y, GROT): return False
    for pts, hw in PADEN:
        if min(segd((x, y), a, b) for a, b in zip(pts, pts[1:])) < hw + pad + rad * 0.5: return False
    if segd((x, y), (6.95, 3.45), (10.25, 0.95)) < 0.6 + rad * 0.5: return False       # ruinemuurtje
    if abs(x - 7.6) < 1.9 and abs(y + 1.6) < 0.9: return False                       # bloembak
    return True
P = []
def add(n, x, y, s, z=0.0): P.append([n, round(x, 2), round(y, 2), round(s, 2), RNG.randrange(360), round(z, 2)])
# perken: kleurbanden evenwijdig aan de lange rand (Sneeuwwitjegrot.jpg)
for perk in ("perk_a", "perk_b"):
    poly = D[perk]; xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    for i in range(400):
        x = RNG.uniform(min(xs), max(xs)); y = RNG.uniform(min(ys), max(ys))
        if not inside(x, y, poly) or any(math.hypot(x - q[1], y - q[2]) < 0.28 for q in P): continue
        band = int((x * 0.55 + y * 0.83) / 0.9) % 3
        kind = ["bloem_rood", "bloem_wit", "bloem_geel"][band] if RNG.random() > 0.15 else RNG.choice(["PH_flower_gazania_%d" % k for k in range(8)])
        add(kind, x, y, RNG.uniform(1.1, 1.45), 0.06)
for k in range(18):       # bloembak rood
    add("bloem_rood", 6.1 + (k % 9) * 0.35, -1.85 + (k // 9) * 0.5, RNG.uniform(1.0, 1.25), 0.72)
for px in (-6.6, -5.9, -3.75, -3.05, 0.95, 6.2):   # potten oranje
    py = 0.2 if px < -2.46 else (1.0 if px < 3.4 else -0.3)
    add(RNG.choice(["PH_flower_ursinia_%d" % k for k in range(5)]), px, py, 0.9, 0.36)
# bos: bomen achter/naast, heesters en varens tegen de rots
TREES = [(-12, 2), (-12.5, 9), (-6, 13), (1, 13.5), (8, 12), (13, 7), (19, 6.5), (25, 2), (27, -5), (-13, -5), (-14, -14), (17, -13), (21, -16), (3, -13), (-2, -26)]
SOORT = ["beuk0", "eik0", "kastanje1", "den0", "beuk1", "eik1", "kastanje0", "den1", "berk0"]
for k, (x, y) in enumerate(TREES):
    if vrij(x, y, 1.2, 1.0): add(SOORT[k % 9], x, y, RNG.uniform(2.6, 3.4))
def scatter(region, n, kinds, smin, smax, rad):
    x0, x1, y0, y1 = region; c = 0
    for _ in range(5000):
        if c >= n: break
        x = RNG.uniform(x0, x1); y = RNG.uniform(y0, y1)
        if not vrij(x, y, rad) or any(math.hypot(x - q[1], y - q[2]) < rad * 1.5 for q in P): continue
        add(RNG.choice(kinds), x, y, RNG.uniform(smin, smax)); c += 1
RODO = ["rododendron0", "rododendron1", "taxus0", "taxus1"]; SHRUB = ["PH_shrub_02_%d" % i for i in range(4)] + ["PH_shrub_03_%d" % i for i in range(4)]
FERN = ["PH_fern_02_%d" % i for i in range(4)]; LOW = ["PH_periwinkle_plant_%d" % i for i in range(6)]
scatter((-13, 26, 0, 14), 26, RODO, 2.0, 2.8, 1.1)               # achter kasteel en grot
scatter((-13, 26, 0, 14), 30, SHRUB, 1.1, 1.8, 0.6)
scatter((9, 25, -9, 3), 40, FERN + LOW, 1.3, 2.0, 0.35)           # tegen de rots
scatter((-12, -8, -10, 1), 16, SHRUB + FERN, 1.1, 1.8, 0.5)       # zuidkant
scatter((13, 26, -18, -9), 20, RODO + SHRUB, 1.2, 2.6, 0.9)       # tussen grot en parkpad
json.dump(P, open("exports/planten.json", "w"))
open("roblox/planten_tabel.luau", "w").write("-- {soort, x, y, schaal, draaiing, z} modelmeters, gegenereerd door build/06_planten.py\nreturn {" + ",".join('{"%s",%s,%s,%s,%s,%s}' % tuple(p) for p in P) + "}\n")
print(len(P))
