"""01_vlakken: padvlakken Sprookjesbos uit de BGT (wegdeel, actueel), geknipt op het Sprookjesbos-gebied.
Uit: ../ref/paden.json (park-m) + review/vlakken_overlay.jpg.  Draai met de venv (shapely)."""
import sys, os, json, math
import numpy as np
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, box, mapping
from shapely.ops import unary_union, transform
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, os.path.join(R, 'tools')); import geo
P = lambda g: transform(lambda x, y, z=None: geo.wgs_to_park(y, x), g)
# Sprookjesbos-gebied: voetvlakken van alle v1-onderdelen + 15 m
units = json.load(open(os.path.join(R, 'reference/ahn_sprookjesbos/units_studio.json')))
gebied = unary_union([box(u[2] / 3 - 15, -u[5] / 3 - 15, u[4] / 3 + 15, -u[3] / 3 + 15) for u in units]).buffer(5).buffer(-5)
TYPE = {'betonstraatstenen': 'klinker', 'asfalt': 'asfalt', 'sierbestrating': 'klinker', 'beton element': 'klinker', None: 'klinker', 'tegels': 'klinker'}
per = {}
for f in json.load(open(os.path.join(R, 'reference/paden/bgt_wegdeel.json')))['features']:
    p = f['properties']
    if p.get('eind_registratie') is not None or p.get('functie') == 'parkeervlak': continue
    g = P(shape(f['geometry'])).buffer(0)
    g = g.intersection(gebied)
    if g.is_empty: continue
    per.setdefault(TYPE.get(p.get('plus_fysiek_voorkomen'), 'klinker'), []).append(g)
vl = {k: unary_union(v).buffer(0.05).buffer(-0.05) for k, v in per.items()}
# kasseien: OSM surface=sett lijnen -> 3 m breed, binnen de klinkervlakken
import xml.etree.ElementTree as ET
osm = ET.parse(os.path.join(R, 'reference/data/efteling_osm.xml')).getroot()
N = {n.get('id'): geo.wgs_to_park(float(n.get('lat')), float(n.get('lon'))) for n in osm.iter('node')}
tg = lambda e: {t.get('k'): t.get('v') for t in e.findall('tag')}
sett = []; lijnen = []
for w in osm.iter('way'):
    t = tg(w)
    if t.get('highway') not in ('footway', 'pedestrian', 'path', 'steps', 'service'): continue
    cs = [N[n.get('ref')] for n in w.findall('nd') if n.get('ref') in N]
    if len(cs) < 2: continue
    L = LineString(cs)
    if not L.intersects(gebied): continue
    lijnen.append({'id': w.get('id'), 'hw': t.get('highway'), 'surface': t.get('surface'), 'coords': [list(c) for c in cs]})
    if t.get('surface') == 'sett': sett.append(L.buffer(2.0))
# OSM-paden die de BGT mist (vooral binnen attractieterreinen): standaardbreedte, bron 'osm'
BREED = {'pedestrian': 3.5, 'footway': 2.2, 'path': 1.8, 'steps': 2.0}
bgt = unary_union(list(vl.values()))
ver = bgt.buffer(3.0)   # alleen stukken die > 3 m van een BGT-pad liggen tellen als 'ontbrekend'
extra = []
for l in lijnen:
    if l['hw'] not in BREED: continue
    lijn = LineString(l['coords']).intersection(gebied)
    mis = lijn.difference(ver)
    if mis.length < 3: continue
    # het ontbrekende stuk + 3,5 m terug langs de lijn, zodat het aansluit op het BGT-pad
    stuk = lijn.intersection(mis.buffer(3.5))
    extra.append(stuk.buffer(BREED[l['hw']] / 2, cap_style=1, join_style=1))
osm_extra = unary_union(extra).difference(unary_union(list(vl.values()))).buffer(-0.05).buffer(0.05) if extra else None
if osm_extra is not None and not osm_extra.is_empty:
    vl['klinker'] = unary_union([vl['klinker'], osm_extra]).buffer(0.02).buffer(-0.02)
    print('osm-aanvulling', round(osm_extra.area), 'm2')
if sett and 'klinker' in vl:
    k = unary_union(sett).intersection(vl['klinker'])
    vl['kassei'] = k; vl['klinker'] = vl['klinker'].difference(k).buffer(0)
out = {k: mapping(v) for k, v in vl.items()}
if osm_extra is not None: out_osm = mapping(osm_extra)
json.dump({'vlakken': out, 'osm_extra': out_osm if osm_extra is not None else None, 'osm_lijnen': lijnen, 'gebied': mapping(gebied)}, open(os.path.join(D, 'ref_paden.json'), 'w'))
for k, v in vl.items(): print(k, round(v.area), 'm2')
# overlay
im = Image.open(os.path.join(R, 'reference/paden/luchtfoto_10cm.jpg')).convert('RGB'); m = json.load(open(os.path.join(R, 'reference/paden/luchtfoto_10cm.json')))
dr = ImageDraw.Draw(im, 'RGBA')
Q = lambda c: ((c[0] - m['x0']) / m['px_m'], (m['y1'] - c[1]) / m['px_m'])
COL = {'klinker': (255, 60, 60, 100), 'asfalt': (60, 60, 255, 100), 'kassei': (255, 200, 0, 140)}
def polys(g): return [g] if isinstance(g, Polygon) else list(getattr(g, 'geoms', []))
for k, v in vl.items():
    mk = Image.new('L', im.size, 0); md = ImageDraw.Draw(mk)
    for pg in polys(v):
        if not isinstance(pg, Polygon): continue
        md.polygon([Q(c) for c in pg.exterior.coords], fill=COL[k][3])
        for h in pg.interiors: md.polygon([Q(c) for c in h.coords], fill=0)
    im.paste(Image.new('RGB', im.size, COL[k][:3]), (0, 0), mk)
    for pg in polys(v):
        if isinstance(pg, Polygon):
            dr.line([Q(c) for c in pg.exterior.coords], fill=(255, 255, 255, 255), width=2)
            for h in pg.interiors: dr.line([Q(c) for c in h.coords], fill=(255, 255, 255, 255), width=2)
if osm_extra is not None:
    for pg in polys(osm_extra):
        if isinstance(pg, Polygon): dr.line([Q(c) for c in pg.exterior.coords], fill=(0, 255, 0, 255), width=4)
dr.line([Q(c) for c in gebied.exterior.coords], fill=(255, 255, 0, 255), width=5)
for l in lijnen: dr.line([Q(c) for c in l['coords']], fill=(0, 255, 255, 200), width=3)
im.resize((im.width // 3, im.height // 3)).save(os.path.join(D, 'review', 'vlakken_overlay.jpg'), quality=85)
