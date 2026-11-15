"""04_zichtrand: struikenstrook langs elke padrand zodat je vanaf een pad nooit een ander pad ziet (Daan).
Op ooghoogte kijk je onder de kronen door; wat zicht blokkeert is ondergroei. Elke zichtlijn die het pad verlaat
moet door de strook achter de padrand. Niet in de scene van een attractie (daar moet je kijken), niet tussen twee
paden die vlak naast elkaar liggen, niet in water. In Studio vervalt een plek als er al een struik binnen 2 m staat.
Uit: exports/zichtrand.b64 (per plek 8 tekens: X 16 | Z 16 | draaiing 6 | maat 4 | rij 1 ...), exports/zichtrand_kaart.jpg"""
import os, json, math
import numpy as np
from shapely.geometry import Polygon, Point, box, shape, LineString
from shapely.ops import unary_union
from shapely.prepared import prep
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.dirname(os.path.dirname(D))
pm = json.load(open(os.path.join(R, 'models', 'PR_Paden', 'exports', 'paden_mesh.json')))
tris = []
for k, st in pm.items():
    if st['mat'] == 'rand': continue
    for t in np.array(st['tri']).reshape(-1, 3, 3):
        pg = Polygon([(-p[0], -p[1]) for p in t])
        if pg.area > 1e-6: tris.append(pg.buffer(0.03))
U = unary_union(tris).buffer(0.1).buffer(-0.1)
water = unary_union([shape(w['geom']) for w in json.load(open(os.path.join(R, 'reference', 'paden', 'water_park.json')))])
units = json.load(open(os.path.join(R, 'reference', 'ahn_sprookjesbos', 'units_studio.json')))
# scene van een attractie: de unit-kaders (zonder losse planten/water-kaders), iets ingekort zodat de rand van de scene wel dicht kan
scenes = unary_union([box(u[2] / 3, -u[5] / 3, u[4] / 3, -u[3] / 3).buffer(-2) for u in units
                      if not any(w in u[0] for w in ('Planten', 'Water', 'Extra', 'Stenen', 'Paddenstoelen')) and (u[4] - u[2]) * (u[5] - u[3]) > 200])
rand = shape(json.load(open(os.path.join(R, 'models', 'PR_Paden', 'ref_zones.json')))['rand_sprookjesbos']['poly'])
verboden = prep(unary_union([U.buffer(1.2), water.buffer(0.5), scenes]))
binnen = prep(rand.buffer(-1))
punten = []
for rij, (afst, stap) in enumerate(((1.9, 2.1), (3.2, 2.6))):
    lijn = U.buffer(afst, join_style=1).boundary
    for g in (lijn.geoms if hasattr(lijn, 'geoms') else [lijn]):
        L = g.length; n = max(1, int(L / stap))
        for i in range(n):
            t = (i + (0.5 if rij else 0)) / n * L
            p = g.interpolate(t)
            if verboden.contains(p) or not binnen.contains(p): continue
            punten.append((p.x, p.y, rij))
rng = np.random.default_rng(7)
A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
uit = []
for x, y, rij in punten:
    X = int(round((x * 3 + 2000) * 10)); Z = int(round((-y * 3 + 2000) * 10)); r = int(rng.integers(0, 64)); m = int(rng.integers(0, 16))
    v = ((((X << 16 | Z) << 6 | r) << 4 | m) << 1 | rij)   # 43 bit -> 8 tekens
    uit.append(''.join(A[(v >> (6 * i)) & 63] for i in range(8)))
open(os.path.join(D, 'exports', 'zichtrand.b64'), 'w').write(''.join(uit))
# kaart
lm = json.load(open(os.path.join(R, 'reference', 'paden', 'luchtfoto_10cm.json'))); Image.MAX_IMAGE_PIXELS = None
foto = Image.open(os.path.join(R, 'reference', 'paden', 'luchtfoto_10cm.jpg')).convert('RGB'); S = 0.25
im = foto.resize((int(foto.width * 0.1 / S), int(foto.height * 0.1 / S))); d = ImageDraw.Draw(im)
px = lambda x, y: ((x - lm['x0']) / S, (lm['y1'] - y) / S)
for pg in (U.geoms if hasattr(U, 'geoms') else [U]): d.polygon([px(*c) for c in pg.exterior.coords], outline=(200, 200, 200))
for pg in (scenes.geoms if hasattr(scenes, 'geoms') else [scenes]): d.polygon([px(*c) for c in pg.exterior.coords], outline=(255, 0, 255))
for x, y, rij in punten:
    a, b = px(x, y); d.ellipse((a - 2, b - 2, a + 2, b + 2), fill=(0, 255, 0) if rij == 0 else (255, 200, 0))
im.save(os.path.join(D, 'review', 'zichtrand_kaart.jpg'), quality=82)
print(len(punten), 'struikplekken (rij 1:', sum(1 for p in punten if p[2] == 0), ', rij 2:', sum(1 for p in punten if p[2] == 1), '), padrandlengte', round(U.boundary.length), 'm')
