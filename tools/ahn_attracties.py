import sys, math, xml.etree.ElementTree as ET, numpy as np
sys.path.insert(0, sys.argv[3])
osm, ahndir, _ , out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
exec(open(sys.argv[3] + '/ahn_get.py').read().split('r = ET.parse')[0])  # haalt wgs_to_rd
f = np.load(ahndir + '/dtm_gevuld.npy')
x0, y0, x1, y1 = map(int, open(ahndir + '/bbox.txt').read().split())
H, W = f.shape
def h(xr, yr):
    c = int((xr - x0) / 0.5); r = int((y1 - yr) / 0.5)
    if 0 <= r < H and 0 <= c < W:
        win = f[max(0, r-4):r+5, max(0, c-4):c+5]; return float(np.nanmedian(win))
    return float('nan')
r = ET.parse(osm).getroot()
N = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in r.iter('node')}
T = lambda e: {t.get('k'): t.get('v') for t in e.findall('tag')}
ox, oy = wgs_to_rd(51.65, 5.0455)
rows = []
for w in r.iter('way'):
    t = T(w)
    if 'sprookjesbos' in t.get('website', ''):
        pts = [N[n.get('ref')] for n in w.findall('nd') if n.get('ref') in N]
        la = sum(p[0] for p in pts)/len(pts); lo = sum(p[1] for p in pts)/len(pts)
        rows.append((t.get('name', '?'), la, lo))
for n in r.iter('node'):
    t = T(n)
    if 'sprookjesbos' in t.get('website', ''): rows.append((t.get('name', '?'), *N[n.get('id')]))
seen = {}
for name, la, lo in rows: seen.setdefault(name, (la, lo))
ref = h(ox, oy)
lines = ['naam;maaiveld_m_NAP;t.o.v._parkoorsprong_m;studs_Y_relatief']
for name, (la, lo) in sorted(seen.items(), key=lambda kv: kv[0]):
    xr, yr = wgs_to_rd(la, lo); z = h(xr, yr)
    lines.append(f"{name};{z:.2f};{z-ref:+.2f};{(z-ref)*3:+.1f}")
open(out, 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines)); print('parkoorsprong maaiveld', round(ref, 2))
