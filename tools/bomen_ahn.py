"""bomen_ahn: elke echte boom uit AHN (DSM - DTM = boomhoogte) + luchtfoto (april: loof kaal, naald groen).
Uit: reference/bomen/bomen.json  [{x, y (park-m), h (m), r (kroonstraal m), kleur [r,g,b], groep, soort}]
     reference/bomen/bomen_kaart.jpg (overlay op de luchtfoto)
Gebruik: .venv/bin/python tools/bomen_ahn.py"""
import os, sys, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from shapely.geometry import shape, Point
from shapely.prepared import prep

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'tools')); import geo
A = os.path.join(R, 'reference', 'ahn_sprookjesbos')
OUT = os.path.join(R, 'reference', 'bomen'); os.makedirs(OUT, exist_ok=True)
Image.MAX_IMAGE_PIXELS = None

# --- CHM in RD-raster (0,5 m)
def lees(n):
    a = np.array(Image.open(os.path.join(A, n)), dtype=np.float32); a[(a > 1e30) | (a < -100)] = np.nan; return a
dtm, dsm = lees('dtm_05m.tif'), lees('dsm_05m.tif')
f = dtm.copy(); gat = np.isnan(f); f[gat] = np.nanmean(dtm)
for _ in range(400):
    p = np.pad(f, 1, mode='edge'); f[gat] = ((p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) / 4)[gat]
chm = np.nan_to_num(dsm - f, nan=0.0); chm = np.clip(chm, 0, 45)
chs = ndimage.gaussian_filter(chm, 1.0)                        # lichte gladheid (0,5 m) tegen ruis in de kroon
bx = list(map(float, open(os.path.join(A, 'bbox.txt')).read().split()))   # RD x0 y0 x1 y1
def rd_van_pix(r, c): return bx[0] + (c + 0.5) * 0.5, bx[3] - (r + 0.5) * 0.5

# --- boomtoppen: lokale maxima met een venster dat met de hoogte meegroeit (hoge bomen = brede kronen)
toppen = []
for hmin, hmax, k in ((4, 10, 5), (10, 18, 7), (18, 45, 9)):
    mx = ndimage.maximum_filter(chs, size=k)
    sel = (chs == mx) & (chs >= hmin) & (chs < hmax)
    toppen += [tuple(p) for p in np.argwhere(sel)]
toppen = sorted(set(toppen), key=lambda p: -chs[p])
# te dichte toppen samenvoegen (binnen 0,25 x hoogte)
gekozen = []; bezet = np.zeros(chm.shape, bool)
for (r, c) in toppen:
    if bezet[r, c]: continue
    h = chs[r, c]; rad = max(2, int(0.25 * h / 0.5))
    gekozen.append((r, c))
    bezet[max(0, r - rad):r + rad + 1, max(0, c - rad):c + rad + 1] = True
# --- kronen: watershed (op -CHM) vanuit de toppen, alleen waar CHM > 3 m
mark = np.zeros(chm.shape, np.int32)
for i, (r, c) in enumerate(gekozen): mark[r, c] = i + 1
masker = chs > 3.0
inv = (chs.max() - chs) * 100
lab = ndimage.watershed_ift(np.clip(inv, 0, 65535).astype(np.uint16), np.where(masker, mark, -1).astype(np.int32))
lab[~masker] = 0
opp = ndimage.sum(np.ones_like(lab), lab, index=np.arange(1, len(gekozen) + 1))

# --- luchtfoto (park-m, 10 cm) voor de kleur van de kroon
lm = json.load(open(os.path.join(R, 'reference', 'paden', 'luchtfoto_10cm.json')))
foto = np.asarray(Image.open(os.path.join(R, 'reference', 'paden', 'luchtfoto_10cm.jpg')).convert('RGB'))
def kleur(x, y, rr):
    c0 = int((x - rr - lm['x0']) / 0.1); c1 = int((x + rr - lm['x0']) / 0.1); r0 = int((lm['y1'] - y - rr) / 0.1); r1 = int((lm['y1'] - y + rr) / 0.1)
    if c0 < 0 or r0 < 0 or c1 >= foto.shape[1] or r1 >= foto.shape[0]: return None
    return foto[r0:r1 + 1, c0:c1 + 1].reshape(-1, 3).mean(0)

zones = json.load(open(os.path.join(R, 'models', 'PR_Paden', 'ref_zones.json')))
rand = prep(shape(zones['rand_sprookjesbos']['poly']).buffer(25))   # 25 m buiten de rand: silhouet van het bos
bomen = []
for i, (r, c) in enumerate(gekozen):
    rx, ry = rd_van_pix(r, c); x, y = geo.rd_to_park(rx, ry)
    if not rand.contains(Point(x, y)): continue
    h = float(chs[r, c]); a = float(opp[i]) * 0.25
    rr = float(np.clip(max(math.sqrt(a / math.pi), 0.28 * h), 1.2, 0.45 * h + 1.5))   # gemeten kroon, minstens 0,28 x hoogte (watershed knipt kronen te klein)
    # dak i.p.v. boom: vlakke 'kroon' (weinig spreiding in hoogte) -> overslaan
    pix = chm[lab == i + 1]
    if len(pix) > 20 and np.std(pix) < 0.6 and h > 4: continue
    k = kleur(x, y, rr * 0.6)
    bomen.append({'x': round(x, 2), 'y': round(y, 2), 'h': round(h, 1), 'r': round(rr, 2), 'kleur': None if k is None else [int(v) for v in k]})

# --- groep (naald/loof) en soort: april-luchtfoto: naald = donker en groen; loof = kaal (bruin/grijs) of jong blad (lichtgroen)
rng = np.random.default_rng(1952)
hels = np.array([sum(b['kleur']) / 3 for b in bomen if b['kleur']]); hel_p30 = np.percentile(hels, 30)
for b in bomen:
    k = b['kleur']; vorm = b['h'] / max(b['r'], 0.5)
    if k is None: groen, hel = 0.0, 100.0
    else: groen = k[1] - (k[0] + k[2]) / 2; hel = sum(k) / 3
    naald = groen > 8 and hel < hel_p30          # alleen echt donkergroen = naaldboom (vers loof in april is lichter)
    if naald:
        b['groep'] = 'naald'; b['soort'] = 'spar' if rng.random() < 0.35 else 'den'   # vorm uit AHN is te grof om spar/den te scheiden
    else:
        b['groep'] = 'loof'; u = rng.random()
        if b['h'] < 11 and b['r'] < 3.2: b['soort'] = 'berk' if u < 0.5 else ('beuk' if u < 0.8 else 'kastanje')
        else: b['soort'] = 'beuk' if u < 0.5 else ('eik' if u < 0.88 else 'kastanje')
json.dump(bomen, open(os.path.join(OUT, 'bomen.json'), 'w'))

# --- kaart
S = 0.25
im = Image.fromarray(foto).resize((int(foto.shape[1] * 0.1 / S), int(foto.shape[0] * 0.1 / S)))
d = ImageDraw.Draw(im)
KL = {'beuk': (255, 140, 0), 'eik': (255, 230, 0), 'kastanje': (255, 60, 160), 'berk': (255, 255, 255), 'den': (0, 200, 255), 'spar': (0, 90, 255)}
for b in bomen:
    px, py = (b['x'] - lm['x0']) / S, (lm['y1'] - b['y']) / S; rp = b['r'] / S
    d.ellipse((px - rp, py - rp, px + rp, py + rp), outline=KL[b['soort']], width=2); d.ellipse((px - 2, py - 2, px + 2, py + 2), fill=KL[b['soort']])
f_ = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 24)
for j, (s, kl) in enumerate(KL.items()): d.rectangle((10, 10 + 32 * j, 34, 34 + 32 * j), fill=kl); d.text((42, 8 + 32 * j), s, fill='white', font=f_, stroke_width=2, stroke_fill='black')
im.save(os.path.join(OUT, 'bomen_kaart.jpg'), quality=82)
from collections import Counter
print(len(bomen), 'bomen', dict(Counter(b['soort'] for b in bomen)))
print('hoogte p10/p50/p90', np.percentile([b['h'] for b in bomen], [10, 50, 90]).round(1), 'kroonstraal p50', np.median([b['r'] for b in bomen]).round(1))
