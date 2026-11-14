"""OSM rond Het Meisje met de Zwavelstokjes -> lokale meters (oorsprong = midden vlak 279667968, x = oost, y = noord) + overzichtsplaatje."""
import xml.etree.ElementTree as ET, math, json
from PIL import Image, ImageDraw
R = "/Users/daaniding/RobloxProjects/efteling-roblox"
OUT = R + "/models/AR_Zwavelstokjes/ref"
LAT0, LON0 = 51.6500, 5.0455
def xy(lat, lon): return ((lon - LON0) * 111320 * math.cos(math.radians(LAT0)), (lat - LAT0) * 110574)
root = ET.parse(R + "/reference/data/efteling_osm.xml").getroot()
nodes = {n.get("id"): n for n in root.iter("node")}
P = {i: xy(float(n.get("lat")), float(n.get("lon"))) for i, n in nodes.items()}
w0 = next(w for w in root.iter("way") if w.get("id") == "279667968")
pts = [P[nd.get("ref")] for nd in w0.iter("nd")]
cx = sum(p[0] for p in pts[:-1]) / (len(pts) - 1); cy = sum(p[1] for p in pts[:-1]) / (len(pts) - 1)
RAD = 45
ways = []
for w in root.iter("way"):
    ps = [P[nd.get("ref")] for nd in w.iter("nd") if nd.get("ref") in P]
    if not ps or min(math.hypot(x - cx, y - cy) for x, y in ps) > RAD: continue
    tags = {t.get("k"): t.get("v") for t in w.iter("tag")}
    ways.append({"id": w.get("id"), "tags": tags, "pts": [[round(x - cx, 2), round(y - cy, 2)] for x, y in ps]})
pnodes = []
for i, n in nodes.items():
    tags = {t.get("k"): t.get("v") for t in n.iter("tag")}
    if not tags: continue
    x, y = P[i]
    if math.hypot(x - cx, y - cy) < RAD: pnodes.append({"id": i, "tags": tags, "p": [round(x - cx, 2), round(y - cy, 2)]})
json.dump({"oorsprong_osm_m": [round(cx, 2), round(cy, 2)], "roblox_studs": [round(cx * 3, 2), round(-cy * 3, 2)],
           "info": "x = oost (m), y = noord (m) t.o.v. midden vlak 279667968", "ways": ways, "nodes": pnodes},
          open(OUT + "/osm_lokaal.json", "w"), indent=1, ensure_ascii=False)
S = 12; W = 2 * RAD * S
im = Image.new("RGB", (W, W), "white"); d = ImageDraw.Draw(im)
f = lambda p: (W / 2 + p[0] * S, W / 2 - p[1] * S)
for g in range(-RAD, RAD + 1, 5):
    d.line([f((g, -RAD)), f((g, RAD))], fill=(230, 230, 230)); d.line([f((-RAD, g)), f((RAD, g))], fill=(230, 230, 230))
for w in ways:
    t = w["tags"]; c = (120, 120, 120)
    if "building" in t: c = (200, 60, 60)
    elif t.get("barrier") == "hedge": c = (40, 140, 40)
    elif "barrier" in t: c = (140, 80, 0)
    elif "highway" in t: c = (60, 60, 200)
    elif "water" in t.get("natural", "") or "water" in t.get("water", ""): c = (0, 150, 220)
    d.line([f(p) for p in w["pts"]], fill=c, width=3)
    m = w["pts"][len(w["pts"]) // 2]; d.text(f(m), (t.get("name") or t.get("building") or t.get("barrier") or t.get("highway") or t.get("natural") or t.get("amenity") or "")[:14] + " " + w["id"][-4:], fill=c)
for n in pnodes:
    x, y = f(n["p"]); d.ellipse([x - 4, y - 4, x + 4, y + 4], fill="red"); d.text((x + 5, y), list(n["tags"].values())[0][:14], fill="red")
im.save(R + "/models/AR_Zwavelstokjes/review/osm.png")
print(len(ways), "ways", len(pnodes), "nodes; oorsprong", round(cx, 2), round(cy, 2))
for w in ways:
    t = w["tags"]
    if any(k in t for k in ("building", "barrier", "natural", "water", "amenity", "man_made")) or t.get("name"):
        print(w["id"], {k: v for k, v in t.items() if k in ("building", "barrier", "natural", "water", "name", "amenity", "man_made", "highway")}, w["pts"][:6], "..." if len(w["pts"]) > 6 else "")
