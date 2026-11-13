"""01b_plan Magische Klok: OSM-lokaal -> modelframe (oorsprong torenmidden, klok naar -Y) + plattegrond review/plan.png en ref/osm_model.json."""
import json, math
from PIL import Image, ImageDraw
D = "/Users/daaniding/RobloxProjects/efteling-roblox/models/AR_MagischeKlok"
d = json.load(open(D + "/ref/osm_lokaal.json"))
C = (4.2, -2.3); ex = (-0.518, -0.855); ey = (0.855, -0.518)
T = lambda p: (round((p[0] - C[0]) * ex[0] + (p[1] - C[1]) * ex[1], 2), round((p[0] - C[0]) * ey[0] + (p[1] - C[1]) * ey[1], 2))
ways = [{"id": w["id"], "tags": w["tags"], "pts": [T(p) for p in w["pts"]]} for w in d["ways"]]
nodes = [{"id": n["id"], "tags": n["tags"], "p": T(n["p"])} for n in d["nodes"]]
json.dump({"frame": "model: oorsprong torenmidden, klok naar -Y, +X = ZZW", "ways": ways, "nodes": nodes}, open(D + "/ref/osm_model.json", "w"), indent=1)
S = 22; R = 26; W = 2 * R * S
im = Image.new("RGB", (W, W), "white"); dr = ImageDraw.Draw(im)
f = lambda p: (W / 2 + p[0] * S, W / 2 + p[1] * S)        # voorkant (-y, plein) boven
for g in range(-R, R + 1):
    c = (205, 205, 205) if g % 5 == 0 else (240, 240, 240)
    dr.line([f((g, -R)), f((g, R))], fill=c); dr.line([f((-R, g)), f((R, g))], fill=c)
for w in ways:
    t = w["tags"]
    c = (200, 60, 60) if "building" in t else (60, 60, 200) if "highway" in t else (40, 140, 40) if t.get("barrier") == "hedge" else (120, 200, 120) if "leisure" in t else (60, 160, 220) if "natural" in t else (160, 160, 160)
    dr.line([f(p) for p in w["pts"]], fill=c, width=3)
    nm = t.get("name") or t.get("highway") or t.get("barrier") or t.get("leisure") or ""
    if nm and w["pts"]: dr.text(f(w["pts"][0]), nm[:18], fill=c)
for n in nodes:
    x, y = f(n["p"]); dr.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(0, 0, 0)); dr.text((x + 6, y), (n["tags"].get("name") or n["tags"].get("highway") or n["tags"].get("amenity", ""))[:20], fill=(0, 0, 0))
dr.text((4, 4), "MODELFRAME Magische Klok: plein (-y) BOVEN, +x rechts (ZZW), raster 1 m, oorsprong = torenmidden", fill=(0, 0, 0))
im.save(D + "/review/plan_osm.png")
for w in ways:
    if any(k in w["tags"] for k in ("highway", "barrier", "leisure", "natural")) or "Prinsenpoort" in str(w["tags"]): print(w["id"], w["tags"].get("highway") or w["tags"].get("barrier") or w["tags"].get("leisure") or w["tags"].get("name"), w["pts"][:12])
for n in nodes: print("N", n["tags"].get("name") or n["tags"].get("highway") or n["tags"].get("amenity"), n["p"])
