"""03_plaatsing: bomen.json (AHN) -> plaatsingsdata voor Studio.
Stamvoet niet op een pad of in een vijver (naar de dichtstbijzijnde vrije plek, max 4 m; anders boom overslaan).
Uit: models/VG_Bomen/exports/plaatsing.json [[soort, X, Z, schaalHoogte, schaalKroon, draaiing], ...] (X, Z in stud)."""
import os, json, math
import numpy as np
from shapely.geometry import Point, Polygon, shape
from shapely.ops import unary_union, nearest_points
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.dirname(os.path.dirname(D))
bomen = json.load(open(os.path.join(R, 'reference', 'bomen', 'bomen.json')))
maten = json.load(open(os.path.join(D, 'exports', 'maten.json')))
# paden (incl. stoeprand) uit het padennet
pm = json.load(open(os.path.join(R, 'models', 'PR_Paden', 'exports', 'paden_mesh.json')))
tris = []
for k, st in pm.items():
    if st['mat'] == 'rand': continue
    P = np.array(st['tri']).reshape(-1, 3, 3)
    for t in P:
        pg = Polygon([(-p[0], -p[1]) for p in t])
        if pg.area > 1e-6: tris.append(pg.buffer(0.02))
paden = unary_union(tris)
water = unary_union([shape(w['geom']) for w in json.load(open(os.path.join(R, 'reference', 'paden', 'water_park.json')))])
verboden = unary_union([paden.buffer(0.6), water.buffer(0.4)])
rng = np.random.default_rng(1952)
uit = []; geschoven = 0; weg = 0
for b in bomen:
    p = Point(b['x'], b['y'])
    if verboden.contains(p):
        q = nearest_points(verboden.boundary, p)[0]
        d = np.array(q.coords[0]) - np.array(p.coords[0]); L = np.linalg.norm(d)
        if L > 4.0: weg += 1; continue
        q = np.array(q.coords[0]) + (d / max(L, 1e-6)) * 0.3
        if verboden.contains(Point(*q)): weg += 1; continue
        x, y = q; geschoven += 1
    else: x, y = b['x'], b['y']
    s = b['soort']; H0 = maten['H0']; Rs = maten['soorten'][s]['r']
    sh = b['h'] / H0; sk = np.clip(b['r'] / Rs, 0.45, 1.6)
    uit.append([s, round(x * 3, 2), round(-y * 3, 2), round(float(sh), 3), round(float(sk), 3), int(rng.integers(0, 360))])
json.dump(uit, open(os.path.join(D, 'exports', 'plaatsing.json'), 'w'))
print(len(uit), 'bomen;', geschoven, 'van een pad/vijver geschoven,', weg, 'overgeslagen')
