"""Stap 1 'Verzamelen' van de 1-op-1-werkwijze: luchtfoto + hoogte + OSM voor een plek in het park.

Gebruik:  python3 tools/uitsnede.py <naam> <x_park_m> <y_park_m> [straal_m=40] [uitmap]
  of      python3 tools/uitsnede.py <naam> studs <X> <Z> [straal_m=40] [uitmap]
Schrijft naar <uitmap> (standaard reference/uitsnede/<naam>/):
  luchtfoto.jpg      PDOK Actueel_orthoHR (7,5 cm/px), noord boven, 1 px = 5 cm
  hoogte.png         AHN4 DTM maaiveld (kleur) met hoogtelijnen per 0,25 m
  overlay.jpg        luchtfoto + OSM-paden (kleur = verharding), gebouwen, bomen, lantaarns + meterraster (10 m)
  meta.json          randen in park-m, RD en studs; min/max maaiveld
Alles in parkmeters (x oost, y noord); Roblox X = 3x, Z = -3y.
"""
import sys, os, json, math, urllib.request, io
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import geo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = sys.argv[1:]
naam = a[0]
if a[1] == 'studs':
    cx, cy = geo.studs_to_park(float(a[2]), float(a[3])); rest = a[4:]
else:
    cx, cy = float(a[1]), float(a[2]); rest = a[3:]
R = float(rest[0]) if rest else 40.0
out = rest[1] if len(rest) > 1 else os.path.join(ROOT, 'reference', 'uitsnede', naam)
os.makedirs(out, exist_ok=True)
PX = 0.05  # m per pixel
W = int(2 * R / PX)

# --- luchtfoto: in RD ophalen (iets ruimer) en terugzetten naar het park-raster
corners = [geo.park_to_rd(cx + sx * R, cy + sy * R) for sx in (-1, 1) for sy in (-1, 1)]
rx0 = min(c[0] for c in corners) - 2; rx1 = max(c[0] for c in corners) + 2
ry0 = min(c[1] for c in corners) - 2; ry1 = max(c[1] for c in corners) + 2
def wms(bx0, by0, bx1, by1, w, h):
    url = ("https://service.pdok.nl/hwh/luchtfotorgb/wms/v1_0?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap"
           f"&LAYERS=Actueel_orthoHR&STYLES=&CRS=EPSG:28992&BBOX={bx0},{by0},{bx1},{by1}&WIDTH={w}&HEIGHT={h}&FORMAT=image/jpeg")
    return Image.open(io.BytesIO(urllib.request.urlopen(url, timeout=60).read())).convert('RGB')
# WMS-tegels van max 2000 px
tw = int((rx1 - rx0) / PX); th = int((ry1 - ry0) / PX)
rdimg = Image.new('RGB', (tw, th))
T = 2000
for ty in range(0, th, T):
    for tx in range(0, tw, T):
        w = min(T, tw - tx); h = min(T, th - ty)
        rdimg.paste(wms(rx0 + tx * PX, ry1 - (ty + h) * PX, rx0 + (tx + w) * PX, ry1 - ty * PX, w, h), (tx, ty))
RA = np.asarray(rdimg)
# park-raster -> RD -> pixel (afbeelding is bijna een verschuiving + mini-draaiing; lineair benaderen uit 3 punten)
o = np.array(geo.park_to_rd(cx, cy)); ex = np.array(geo.park_to_rd(cx + 1, cy)) - o; ey = np.array(geo.park_to_rd(cx, cy + 1)) - o
ii, jj = np.meshgrid(np.arange(W), np.arange(W), indexing='ij')   # ii = rij, jj = kolom (zonder 'ij' gespiegeld beeld, fout t/m 18 nov)
px_ = (jj + 0.5) * PX - R; py_ = R - (ii + 0.5) * PX
RX = o[0] + px_ * ex[0] + py_ * ey[0]; RY = o[1] + px_ * ex[1] + py_ * ey[1]
col = np.clip(((RX - rx0) / PX).astype(int), 0, tw - 1); row = np.clip(((ry1 - RY) / PX).astype(int), 0, th - 1)
foto = Image.fromarray(RA[row, col])
foto.save(os.path.join(out, 'luchtfoto.jpg'), quality=90)

# --- AHN maaiveld uit de Sprookjesbos-uitsnede (of park/relief), bilineair
import struct
tif = os.path.join(ROOT, 'reference', 'ahn_sprookjesbos', 'dtm_05m.tif')
bbox = list(map(float, open(os.path.join(ROOT, 'reference', 'ahn_sprookjesbos', 'bbox.txt')).read().split()))
D = np.array(Image.open(tif), dtype=np.float32)
D[(D > 1e30) | (D < -100)] = np.nan
gat = np.isnan(D)
F = D.copy(); F[gat] = np.nanmean(D)
for _ in range(300):
    P = np.pad(F, 1, mode='edge'); F[gat] = ((P[:-2, 1:-1] + P[2:, 1:-1] + P[1:-1, :-2] + P[1:-1, 2:]) / 4)[gat]
HS = 0.5  # m per hoogtepixel in de uitvoer
HW = int(2 * R / HS)
hi, hj = np.meshgrid(np.arange(HW), np.arange(HW), indexing='ij')
hx = (hj + 0.5) * HS - R; hy = R - (hi + 0.5) * HS
HRX = o[0] + hx * ex[0] + hy * ey[0]; HRY = o[1] + hx * ex[1] + hy * ey[1]
c = (HRX - bbox[0]) / 0.5 - 0.5; r = (bbox[3] - HRY) / 0.5 - 0.5
c0 = np.clip(np.floor(c).astype(int), 0, F.shape[1] - 2); r0 = np.clip(np.floor(r).astype(int), 0, F.shape[0] - 2)
fc = np.clip(c - c0, 0, 1); fr = np.clip(r - r0, 0, 1)
H = F[r0, c0] * (1 - fc) * (1 - fr) + F[r0, c0 + 1] * fc * (1 - fr) + F[r0 + 1, c0] * (1 - fc) * fr + F[r0 + 1, c0 + 1] * fc * fr
G = gat[r0, c0]
lo, hi_ = float(np.percentile(H, 1)), float(np.percentile(H, 99))
t = np.clip((H - lo) / max(hi_ - lo, 0.1), 0, 1)
rgb = np.stack([60 + 190 * t, 120 + 80 * (1 - abs(t - 0.5) * 2), 200 - 170 * t], -1).astype(np.uint8)
rgb[G] = (rgb[G] * 0.6).astype(np.uint8)  # opgevulde gaten (gebouw/water) donkerder
img = Image.fromarray(rgb).resize((800, 800), Image.NEAREST); d = ImageDraw.Draw(img)
Hs = np.array(Image.fromarray(H).resize((800, 800), Image.BILINEAR))
lv = np.floor(Hs / 0.25)
edge = (lv[1:, :-1] != lv[:-1, :-1]) | (lv[:-1, 1:] != lv[:-1, :-1])
A = np.asarray(img).copy(); A[:-1, :-1][edge] = (30, 30, 30); img = Image.fromarray(A); d = ImageDraw.Draw(img)
try: f = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 14)
except Exception: f = None
d.text((8, 8), f"{naam}: maaiveld {lo:.2f}..{hi_:.2f} m NAP, lijnen per 0,25 m, donker = opgevuld gat", fill=(0, 0, 0), font=f,
       stroke_width=2, stroke_fill=(255, 255, 255))
img.save(os.path.join(out, 'hoogte.png'))

# --- OSM-overlay
osm = ET.parse(os.path.join(ROOT, 'reference', 'data', 'efteling_osm.xml')).getroot()
N = {n.get('id'): geo.wgs_to_park(float(n.get('lat')), float(n.get('lon'))) for n in osm.iter('node')}
tg = lambda e: {t.get('k'): t.get('v') for t in e.findall('tag')}
ov = foto.copy(); d = ImageDraw.Draw(ov)
P = lambda p: ((p[0] - cx + R) / PX, (cy + R - p[1]) / PX)
COL = {'asphalt': (90, 90, 90), 'paving_stones': (230, 60, 50), 'sett': (170, 80, 200), 'fine_gravel': (240, 180, 40),
       'compacted': (240, 180, 40), 'gravel': (240, 180, 40), 'sand': (240, 210, 90), 'wood': (150, 90, 40), 'paved': (60, 60, 200)}
for w in osm.iter('way'):
    t = tg(w); cs = [N[n.get('ref')] for n in w.findall('nd') if n.get('ref') in N]
    if len(cs) < 2 or all(abs(p[0] - cx) > R * 1.5 or abs(p[1] - cy) > R * 1.5 for p in cs): continue
    if t.get('building') or t.get('tourism') == 'attraction':
        d.line([P(p) for p in cs], fill=(255, 255, 255), width=4)
    elif t.get('natural') == 'water':
        d.line([P(p) for p in cs], fill=(80, 170, 255), width=4)
    elif t.get('highway'):
        d.line([P(p) for p in cs], fill=COL.get(t.get('surface'), (255, 255, 255)), width=6)
for nid, p in N.items():
    pass
for n in osm.iter('node'):
    t = tg(n)
    if not t: continue
    p = N[n.get('id')]
    if abs(p[0] - cx) > R or abs(p[1] - cy) > R: continue
    x, y = P(p)
    if t.get('natural') == 'tree': d.ellipse([x - 8, y - 8, x + 8, y + 8], outline=(40, 255, 60), width=3)
    elif t.get('highway') == 'street_lamp': d.rectangle([x - 6, y - 6, x + 6, y + 6], fill=(255, 230, 0))
    elif t.get('amenity') in ('bench', 'waste_basket'): d.rectangle([x - 5, y - 5, x + 5, y + 5], fill=(255, 120, 0))
for m in range(-int(R // 10) * 10, int(R) + 1, 10):
    d.line([P((cx + m, cy - R)), P((cx + m, cy + R))], fill=(255, 255, 255), width=1)
    d.line([P((cx - R, cy + m)), P((cx + R, cy + m))], fill=(255, 255, 255), width=1)
ov.save(os.path.join(out, 'overlay.jpg'), quality=88)

X0, Z0 = geo.park_to_studs(cx - R, cy + R); X1, Z1 = geo.park_to_studs(cx + R, cy - R)
json.dump({'naam': naam, 'midden_park_m': [cx, cy], 'straal_m': R, 'pixel_m_luchtfoto': PX,
           'rd_midden': list(o), 'studs_box': [X0, Z0, X1, Z1],
           'maaiveld_NAP_p1_p99': [lo, hi_], 'maaiveld_NAP_midden': float(H[HW // 2, HW // 2])},
          open(os.path.join(out, 'meta.json'), 'w'), indent=1)
print(out, 'maaiveld', round(lo, 2), round(hi_, 2))
