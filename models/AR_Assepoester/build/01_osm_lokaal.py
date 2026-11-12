"""OSM rond Assepoester -> lokale meters (oorsprong = midden gebouw-footprint) + overzichtsplaatje."""
import xml.etree.ElementTree as ET, math, json, sys
from PIL import Image, ImageDraw
R = "/Users/daaniding/RobloxProjects/efteling-roblox"
OUT = R + "/models/AR_Assepoester/ref"
LAT0, LON0 = 51.6500, 5.0455
def xy(lat, lon): return ((lon-LON0)*111320*math.cos(math.radians(LAT0)), (lat-LAT0)*110574)
root = ET.parse(R + "/reference/data/efteling_osm.xml").getroot()
nodes = {n.get("id"): n for n in root.iter("node")}
P = {i: xy(float(n.get("lat")), float(n.get("lon"))) for i, n in nodes.items()}
bld = next(w for w in root.iter("way") if any(t.get("k")=="name" and t.get("v")=="Assepoester" for t in w.iter("tag")))
pts = [P[nd.get("ref")] for nd in bld.iter("nd")]
cx = sum(p[0] for p in pts[:-1])/(len(pts)-1); cy = sum(p[1] for p in pts[:-1])/(len(pts)-1)
RAD = 40
ways = []
for w in root.iter("way"):
    ps = [P[nd.get("ref")] for nd in w.iter("nd") if nd.get("ref") in P]
    if not ps or min(math.hypot(x-cx, y-cy) for x, y in ps) > RAD: continue
    tags = {t.get("k"): t.get("v") for t in w.iter("tag")}
    ways.append({"id": w.get("id"), "tags": tags, "pts": [[round(x-cx, 2), round(y-cy, 2)] for x, y in ps]})
pnodes = []
for i, n in nodes.items():
    tags = {t.get("k"): t.get("v") for t in n.iter("tag")}
    if not tags: continue
    x, y = P[i]
    if math.hypot(x-cx, y-cy) < RAD: pnodes.append({"id": i, "tags": tags, "p": [round(x-cx, 2), round(y-cy, 2)]})
json.dump({"oorsprong_osm_m": [round(cx, 2), round(cy, 2)], "roblox_studs": [round(cx*3, 2), round(-cy*3, 2)],
           "info": "x = oost (m), y = noord (m) t.o.v. midden Assepoester-footprint", "ways": ways, "nodes": pnodes},
          open(OUT + "/osm_lokaal.json", "w"), indent=1, ensure_ascii=False)
S = 12; W = 2*RAD*S
im = Image.new("RGB", (W, W), "white"); d = ImageDraw.Draw(im)
f = lambda p: (W/2 + p[0]*S, W/2 - p[1]*S)
for g in range(-RAD, RAD+1, 5):
    d.line([f((g, -RAD)), f((g, RAD))], fill=(230, 230, 230)); d.line([f((-RAD, g)), f((RAD, g))], fill=(230, 230, 230))
for w in ways:
    t = w["tags"]; c = (120, 120, 120)
    if "building" in t: c = (200, 60, 60)
    elif t.get("barrier") in ("hedge",): c = (40, 140, 40)
    elif "barrier" in t: c = (140, 80, 0)
    elif "highway" in t: c = (60, 60, 200)
    elif t.get("natural") == "water" or "water" in t: c = (0, 160, 220)
    d.line([f(p) for p in w["pts"]], fill=c, width=3)
    lab = t.get("name") or t.get("barrier") or t.get("highway") or t.get("building") or t.get("natural") or t.get("landuse") or ""
    d.text(f(w["pts"][0]), lab[:20], fill=c)
for n in pnodes:
    x, y = f(n["p"]); d.ellipse([x-4, y-4, x+4, y+4], fill=(0, 0, 0))
    d.text((x+5, y), "/".join(f"{k}={v}" for k, v in n["tags"].items() if k in ("barrier", "highway", "natural", "amenity", "tourism", "man_made", "entrance", "name"))[:30], fill=(0, 0, 0))
d.text((5, 5), "N boven, raster 5 m, oorsprong midden Assepoester", fill=(0, 0, 0))
im.save(OUT + "/osm_overzicht.png")
print(len(ways), len(pnodes), cx, cy)
for w in ways: print(w["id"], {k: v for k, v in w["tags"].items() if k in ("building","barrier","highway","name","natural","landuse","leisure","wall","material","area")}, len(w["pts"]))
for n in pnodes: print("N", n["p"], n["tags"])
