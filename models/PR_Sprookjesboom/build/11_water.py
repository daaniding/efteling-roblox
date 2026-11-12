"""
11_water: textures en data voor levend, modderig water in het beekje van de Sprookjesboom (Eftepedia Boom_wortels.jpg: troebel
bruingroen, spiegelend; Rodosb.jpg: donker water tussen breuksteen).
 - water_rimpel.png  (512, naadloos): lichte rimpelglinsteringen met alfa, schuift snel (stroming)
 - water_slib.png    (512, naadloos): bruine slibwolken met alfa, schuift traag (troebelheid)
 - water_ring.png    (256): rimpelring voor particles (wortelvingers in het water, stenen)
 - water_kroos.png   (512): plukje kroos (eendenkroos) met alfa voor tegen de oevers
 - blad_los.png      (256): één los eikenblad (ambientCG LeafSet016) voor drijvende blaadjes
 - exports/beek_middellijn.json: middellijn van de beek (skelet van de OSM-vorm), stroomafwaarts west -> oost
Gebruik: python3 11_water.py (venv met numpy, scipy, pillow, shapely, scikit-image)
"""
import os, json, math, random
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, ".."); REPO = os.path.abspath(os.path.join(A, "..", ".."))
OUT = os.path.join(A, "textures", "water"); os.makedirs(OUT, exist_ok=True)
rnd = np.random.default_rng(7)
N = 512
yy, xx = np.mgrid[0:N, 0:N] / N * 2 * np.pi


def tile_noise(n_oct=5, base=3, seed=0):
    """naadloze ruis als som van sinussen met gehele frequenties."""
    r = np.random.default_rng(seed); f = np.zeros((N, N))
    for o in range(n_oct):
        k = base * 2 ** o
        for _ in range(6):
            kx, ky = r.integers(-k, k + 1), r.integers(-k, k + 1)
            if kx == 0 and ky == 0: continue
            f += np.sin(kx * xx + ky * yy + r.uniform(0, 6.28)) / (1.6 ** o)
    return (f - f.min()) / (f.max() - f.min())


def save(arr_rgb, alpha, name):
    Image.fromarray(np.dstack([np.clip(arr_rgb, 0, 255), np.clip(alpha, 0, 255)]).astype(np.uint8)).save(os.path.join(OUT, name))


# rimpels: gerekte golfjes (stroomrichting = U) met dunne lichte kammen
warp = tile_noise(4, 2, 1)
w = np.sin(6 * xx + 3 * np.sin(2 * yy + 6 * warp) + 2.0 * np.sin(4 * xx + 1)) * np.sin(14 * yy + 2 * np.sin(3 * xx + 5 * warp))
crest = np.clip((w - 0.55) / 0.45, 0, 1) ** 2
crest = ndimage.gaussian_filter(crest, 1.0, mode="wrap")
save(np.dstack([np.full((N, N), 225), np.full((N, N), 230), np.full((N, N), 220)]), crest * 150, "water_rimpel.png")
# slib: bruine wolken, half doorzichtig
s = tile_noise(5, 2, 2); s2 = tile_noise(4, 4, 3)
cloud = np.clip((s * 0.7 + s2 * 0.3 - 0.35) / 0.5, 0, 1)
rgb = np.dstack([92 + 30 * s2, 76 + 22 * s2, 44 + 14 * s2])
save(rgb, cloud * 120, "water_slib.png")
# rimpelring
M = 256; ry, rx = np.mgrid[0:M, 0:M] - M / 2 + 0.5; rr = np.sqrt(rx * rx + ry * ry) / (M / 2)
ring = np.exp(-((rr - 0.82) / 0.05) ** 2) * 0.9 + np.exp(-((rr - 0.62) / 0.04) ** 2) * 0.4
save(np.full((M, M, 3), 235), ring * 255 * (rr < 1), "water_ring.png")
# kroos: honderden kleine ronde blaadjes in een plukje
k = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = np.zeros((N, N, 4))
r2 = random.Random(5)
for i in range(2600):
    ang = r2.uniform(0, 6.28); d = abs(r2.gauss(0, 0.16)) * N
    if d > N * 0.46: continue
    cx, cy = N / 2 + math.cos(ang) * d, N / 2 + math.sin(ang) * d; rad = r2.uniform(3.0, 6.0)
    g = np.array([r2.uniform(70, 110), r2.uniform(125, 165), r2.uniform(30, 55)])
    x0, x1 = int(max(0, cx - rad - 1)), int(min(N, cx + rad + 2)); y0, y1 = int(max(0, cy - rad - 1)), int(min(N, cy + rad + 2))
    sy, sx = np.mgrid[y0:y1, x0:x1]; m = ((sx - cx) ** 2 + (sy - cy) ** 2) < rad * rad
    px[y0:y1, x0:x1][m] = [*(g * r2.uniform(0.85, 1.1)), 255]
save(px[..., :3], px[..., 3], "water_kroos.png")
# los eikenblad uit de atlas (zomergroen, zelfde kleurbehandeling als 10_eikentros.py)
D = os.path.join(REPO, "textures", "ambientcg", "LeafSet016")
col = np.asarray(Image.open(os.path.join(D, "LeafSet016_2K-PNG_Color.png")).convert("RGB"), np.float32) / 255
op = np.asarray(Image.open(os.path.join(D, "LeafSet016_2K-PNG_Opacity.png")).convert("L"), np.float32) / 255
lab, n = ndimage.label(op > 0.5); sl = ndimage.find_objects(lab)[0]
g = col[sl] * np.array([0.52, 0.55, 0.30]) + 0.04                     # beetje verkleurd (drijft al even)
leaf = Image.fromarray((np.dstack([np.clip(g, 0, 1), op[sl]]) * 255).astype(np.uint8))
leaf.thumbnail((256, 256)); bg = Image.new("RGBA", (256, 256), (0, 0, 0, 0)); bg.paste(leaf, ((256 - leaf.width) // 2, (256 - leaf.height) // 2)); bg.save(os.path.join(OUT, "blad_los.png"))
# middellijn: rasteriseer de beek, skelet, langste pad
from shapely.geometry import Polygon
from skimage.morphology import skeletonize
dat = json.load(open(os.path.join(A, "exports", "omgeving_data.json")))
poly = Polygon(dat["beek"][0]["ext"]).buffer(0)
res = 0.05; x0, y0, x1, y1 = poly.bounds
gx = np.arange(x0, x1, res); gy = np.arange(y0, y1, res)
from shapely import contains_xy
GX, GY = np.meshgrid(gx, gy); mask = contains_xy(poly, GX.ravel(), GY.ravel()).reshape(GX.shape)
sk = skeletonize(mask)
pts = list(zip(*np.nonzero(sk)))
idx = {p: i for i, p in enumerate(pts)}
nb = [[idx[(p[0] + dy, p[1] + dx)] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx) and (p[0] + dy, p[1] + dx) in idx] for p in pts]
def bfs(s):
    dist = {s: 0}; prev = {s: None}; q = [s]
    for u in q:
        for v in nb[u]:
            if v not in dist: dist[v] = dist[u] + 1; prev[v] = u; q.append(v)
    far = max(dist, key=dist.get); return far, prev
a, _ = bfs(0); b, prev = bfs(a)
path = []; u = b
while u is not None: path.append(pts[u]); u = prev[u]
line = [(float(gx[c]), float(gy[r])) for r, c in path]
if line[0][0] > line[-1][0]: line.reverse()                      # stroomafwaarts west -> oost (vijver in het westen)
from shapely.geometry import LineString
ls = LineString(line).simplify(0.08)
cl = [[round(x, 2), round(y, 2)] for x, y in ls.coords]
json.dump({"middellijn": cl, "lengte_m": round(ls.length, 1)}, open(os.path.join(A, "exports", "beek_middellijn.json"), "w"))
print("textures in", OUT, "| middellijn", len(cl), "punten,", round(ls.length, 1), "m")
