import sys, numpy as np, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
osm, ahn, scr = sys.argv[1], sys.argv[2], sys.argv[3]
exec(open(scr + '/ahn_get.py').read().split('r = ET.parse')[0])
x0, y0, x1, y1 = map(int, open(ahn + '/bbox.txt').read().split())
chm = np.nan_to_num(np.load(ahn + '/chm.npy'), nan=0)
H, W = chm.shape
r = ET.parse(osm).getroot()
N = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in r.iter('node')}
T = lambda e: {t.get('k'): t.get('v') for t in e.findall('tag')}
img = Image.new('L', (W, H), 0); d = ImageDraw.Draw(img)
P = lambda p: ((wgs_to_rd(*p)[0]-x0)/0.5, (y1-wgs_to_rd(*p)[1])/0.5)
for w in r.iter('way'):
    t = T(w)
    if t.get('highway') in ('footway', 'path', 'pedestrian', 'steps'):
        c = [P(N[n.get('ref')]) for n in w.findall('nd') if n.get('ref') in N]
        if len(c) > 1: d.line(c, fill=255, width=6)
pad = np.array(img) > 0
# afstandsveld via iteratieve dilatie (city-block benadering met 8-buren)
dist = np.full((H, W), 1e9); dist[pad] = 0
from scipy import ndimage
dist = ndimage.distance_transform_edt(~pad) * 0.5
# studiegebied: rond de sprookjesbos-attracties (convex hull + 40 m)
pts = []
for w in r.iter('way'):
    if 'sprookjesbos' in T(w).get('website', ''): pts += [P(N[n.get('ref')]) for n in w.findall('nd') if n.get('ref') in N]
for n in r.iter('node'):
    if 'sprookjesbos' in T(n).get('website', ''): pts.append(P(N[n.get('id')]))
from scipy.spatial import ConvexHull
hp = np.array(pts); hull = hp[ConvexHull(hp).vertices]
m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon([tuple(p) for p in hull], fill=255)
area = ndimage.distance_transform_edt(np.array(m) == 0) * 0.5 <= 40
k = 9
from numpy.lib.stride_tricks import sliding_window_view as swv
mx = swv(np.pad(chm, k//2), (k, k)).max(axis=(2, 3)); tops = (chm == mx) & (chm > 6) & area
A = area.sum() * 0.25 / 1e4
print(f"studiegebied {A:.1f} ha, boomtoppen {tops.sum()}")
for a, b in [(0, 5), (5, 20), (20, 40), (40, 80), (80, 1e9)]:
    z = area & (dist >= a) & (dist < b)
    print(f"{a:>3}-{b if b < 1e8 else '...':>4} m van pad: {z.sum()*0.25/1e4:5.1f} ha ({z.sum()/area.sum()*100:4.1f}%), bomen {int((tops & z).sum())}")
vis = np.zeros((H, W, 3), np.uint8); vis[area] = (230, 230, 220)
for (a, b), col in zip([(0, 5), (5, 20), (20, 40), (40, 1e9)], [(200, 60, 50), (240, 160, 40), (120, 180, 90), (40, 90, 50)]):
    vis[area & (dist >= a) & (dist < b)] = col
vis[pad] = (20, 20, 20); vis[tops] = (255, 255, 255)
im = Image.fromarray(vis); im.thumbnail((700, 900)); im.save(scr + '/zichtzone.png')
