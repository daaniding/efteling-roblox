import sys, math, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]
r = ET.parse(src).getroot()
N = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in r.iter('node')}
def tags(e): return {t.get('k'): t.get('v') for t in e.findall('tag')}
ways = [(w, tags(w), [N[nd.get('ref')] for nd in w.findall('nd') if nd.get('ref') in N]) for w in r.iter('way')]
# bbox van sprookjesbos-attracties
pts = []
for w, t, c in ways:
    if 'sprookjesbos' in t.get('website', ''): pts += c
for n in r.iter('node'):
    if 'sprookjesbos' in tags(n).get('website', ''): pts.append(N[n.get('id')])
la = [p[0] for p in pts]; lo = [p[1] for p in pts]
m = 0.0006
la0, la1, lo0, lo1 = min(la)-m, max(la)+m, min(lo)-m*1.6, max(lo)+m*1.6
k = math.cos(math.radians(51.65))
W = 1400; H = int(W * (la1-la0) / ((lo1-lo0)*k))
img = Image.new('RGB', (W, H), (238, 236, 228)); d = ImageDraw.Draw(img)
P = lambda p: ((p[1]-lo0)/(lo1-lo0)*W, (la1-p[0])/(la1-la0)*H)
for w, t, c in ways:
    if t.get('landuse') == 'forest' or t.get('natural') == 'wood':
        if len(c) > 2: d.polygon([P(p) for p in c], fill=(200, 222, 195))
for w, t, c in ways:
    if t.get('natural') == 'water' or t.get('waterway'):
        if len(c) > 2 and c[0] == c[-1]: d.polygon([P(p) for p in c], fill=(160, 200, 230))
        else: d.line([P(p) for p in c], fill=(120, 170, 220), width=3)
    if t.get('building') or ('sprookjesbos' in t.get('website', '') and len(c) > 2):
        d.polygon([P(p) for p in c], fill=(185, 160, 140), outline=(120, 90, 70))
    if t.get('barrier') == 'hedge': d.line([P(p) for p in c], fill=(60, 120, 60), width=2)
COL = {'asphalt': (90, 90, 90), 'paving_stones': (200, 60, 50), 'sett': (150, 80, 160), 'fine_gravel': (220, 160, 40),
       'compacted': (220, 160, 40), 'sand': (230, 200, 90), 'wood': (140, 90, 40), 'concrete': (120, 140, 160), 'paved': (60, 60, 140)}
for w, t, c in ways:
    if t.get('highway') in ('footway', 'path', 'pedestrian', 'service', 'steps'):
        col = COL.get(t.get('surface'), (255, 255, 255))
        d.line([P(p) for p in c], fill=(40, 40, 40), width=7); d.line([P(p) for p in c], fill=col, width=5)
for n in r.iter('node'):
    t = tags(n); x, y = P(N[n.get('id')])
    if t.get('natural') == 'tree': d.ellipse([x-3, y-3, x+3, y+3], fill=(30, 110, 40))
    if t.get('highway') == 'street_lamp': d.rectangle([x-2, y-2, x+2, y+2], fill=(250, 220, 0))
try: f = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 15)
except: f = None
for w, t, c in ways:
    if 'sprookjesbos' in t.get('website', '') and c:
        x = sum(P(p)[0] for p in c)/len(c); y = sum(P(p)[1] for p in c)/len(c)
        d.text((x, y), t.get('name', ''), fill=(0, 0, 0), font=f, anchor='mm', stroke_width=2, stroke_fill=(255, 255, 255))
for n in r.iter('node'):
    t = tags(n)
    if 'sprookjesbos' in t.get('website', ''):
        x, y = P(N[n.get('id')]); d.text((x, y), t.get('name', ''), fill=(0, 0, 0), font=f, anchor='mm', stroke_width=2, stroke_fill=(255, 255, 255))
y = 10
for name, col in [('asfalt', COL['asphalt']), ('klinkers', COL['paving_stones']), ('kasseien (sett)', COL['sett']), ('fijn grind', COL['fine_gravel']),
                  ('zand', COL['sand']), ('hout', COL['wood']), ('beton', COL['concrete']), ('verhard (onbekend)', COL['paved']), ('niet getagd', (255, 255, 255))]:
    d.rectangle([10, y, 40, y+14], fill=col, outline=(0, 0, 0)); d.text((48, y-1), name, fill=(0, 0, 0), font=f); y += 20
img.save(out); print(W, H)
