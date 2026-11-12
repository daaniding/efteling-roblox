"""05_paden_polygonen: maakt nette padvlakken + opsluitbanden uit exports/omgeving_data.json (paden) en het OSM-plein.
Draai met een Python die shapely heeft (venv). Schrijft exports/paden_poly.json voor 06_paden.py (Blender).
Volgorde (bovenste wint bij overlap): klinkerrood > klinker > plein > grind. Waar materialen elkaar raken komt een opsluitband."""
import json, os
from shapely.geometry import LineString, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
HERE=os.path.dirname(os.path.abspath(__file__)); EXP=os.path.join(HERE,"..","exports")
d=json.load(open(os.path.join(EXP,"omgeving_data.json")))
PLEIN=[(-20.1,-51.71),(-18.61,-56.71),(-17.79,-59.05),(-15.78,-61.1),(-14.11,-63.08),(-10.49,-65.34),(-3.24,-67.5),(3.75,-66.81),(10.62,-63.1),(14.4,-59.43),(18.38,-61.1),(19.68,-59.14),(20.72,-56.43),(21.72,-51.24),(21.48,-46.45),(20.88,-41.49),(19.12,-35.31),(14.85,-35.31),(14.11,-36.85),(10.13,-34.23),(10.42,-32.2),(4.54,-29.55),(2.7,-30.22),(-0.64,-30.29),(-2.0,-30.44),(-6.4,-30.92),(-12.26,-33.65),(-15.97,-37.04),(-17.22,-39.06),(-18.73,-41.47),(-20.14,-46.51),(-20.12,-49.46)]
geo={"grind":[],"klinker":[],"klinkerrood":[],"plein":[]}   # plein (OSM 55344641, PLEIN hierboven) later bouwen samen met de rest van het Ton van de Venplein (Daan)
for p in d["paden"]:
    geo["grind"].append(   # alle paden hetzelfde lichte grind (Daan); plein blijft kasseien
        LineString(p["pts"]).buffer(p["w"]/2,quad_segs=10,join_style="round",cap_style="round"))
# terras en rijhal-vloer niet onder paden laten uitsteken
terras=Polygon([(-8.6,-5.0),(8.6,-5.0),(8.6,3.15),(-8.6,3.15)]).union(Polygon([(-8.35,-6.4),(8.35,-6.4),(8.35,-5.0),(-8.35,-5.0)]))
hal=Polygon([(6.75,8.85),(16.0,8.85),(16.0,30.7),(6.75,30.7)])
order=["klinkerrood","klinker","plein","grind"]
taken=terras.union(hal); out={}
for m in order:
    g=unary_union(geo[m]).difference(taken).buffer(0)
    g=g.simplify(0.02)
    taken=taken.union(g); out[m]=g
# opsluitbanden: alle randen van alle padvlakken, 14 cm breed
alles=unary_union([out[m] for m in order])
randen=alles.buffer(0).boundary.buffer(0.06,quad_segs=4,cap_style="flat")   # alleen buitenrand (pad->gras); paden lopen zonder band in elkaar over (Daan).difference(terras.buffer(-0.02)).difference(hal.buffer(-0.02))
def polys(g):
    if g.is_empty: return []
    gs=list(g.geoms) if hasattr(g,"geoms") else [g]
    return [{"ext":[list(map(lambda v:round(v,3),c)) for c in p.exterior.coords[:-1]],
             "holes":[[list(map(lambda v:round(v,3),c)) for c in r.coords[:-1]] for r in p.interiors]} for p in gs if p.area>0.01]
res={m:polys(out[m]) for m in order}; res["band"]=polys(randen)
json.dump(res,open(os.path.join(EXP,"paden_poly.json"),"w"))
print({k:(len(v),round(sum(Polygon(p["ext"],p["holes"]).area for p in v),1)) for k,v in res.items()})
