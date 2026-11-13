"""OSM lokaal -> modelframe Hans en Grietje. Model: meters, gevel kijkt naar -Y (WNW), +X = rechts (ZZO), oorsprong = midden BAG-footprint.
Modelas +X = OSM (-0.332,-0.944), +Y = OSM (0.944,-0.332). Schrijft ref/osm_model.json + ref/osm_model.png."""
import json, math
from PIL import Image, ImageDraw
D = "/Users/daaniding/RobloxProjects/efteling-roblox/models/AR_HansGrietje/ref"
d = json.load(open(D + "/osm_lokaal.json"))
ex, ey = (-0.332, -0.944), (0.944, -0.332)
T = lambda p: [round(p[0]*ex[0] + p[1]*ex[1], 2), round(p[0]*ey[0] + p[1]*ey[1], 2)]
ways = [{"id": w["id"], "tags": w["tags"], "pts": [T(p) for p in w["pts"]]} for w in d["ways"]]
nodes = [{"id": n["id"], "tags": n["tags"], "p": T(n["p"])} for n in d["nodes"]]
json.dump({"frame": "model: x rechts (ZZO), y diep (OSO), gevel naar -y", "oorsprong_studs": d["roblox_studs"], "ways": ways, "nodes": nodes}, open(D + "/osm_model.json", "w"), indent=1)
S = 25; R = 16; W = 2*R*S
im = Image.new("RGB", (W, W), "white"); dr = ImageDraw.Draw(im)
f = lambda p: (W/2 + p[0]*S, W/2 + p[1]*S)   # +y omlaag in beeld = achter het huis; voorkant (-y) boven
for g in range(-R, R+1):
    c = (200, 200, 200) if g % 5 == 0 else (238, 238, 238)
    dr.line([f((g, -R)), f((g, R))], fill=c); dr.line([f((-R, g)), f((R, g))], fill=c)
for w in ways:
    t = w["tags"]; c = (200, 60, 60) if "building" in t else (60, 60, 200) if "highway" in t else (40, 140, 40)
    dr.line([f(p) for p in w["pts"]], fill=c, width=3)
for n in nodes:
    x, y = f(n["p"]); dr.ellipse([x-5, y-5, x+5, y+5], fill=(0, 0, 0)); dr.text((x+6, y), n["tags"].get("barrier") or n["tags"].get("amenity", ""), fill=(0, 0, 0))
dr.text((4, 4), "MODELFRAME: voorkant (-y) BOVEN, +x rechts, raster 1 m", fill=(0, 0, 0))
im.save(D + "/osm_model.png")
for w in ways:
    if "highway" in w["tags"]: print(w["id"], w["pts"])
