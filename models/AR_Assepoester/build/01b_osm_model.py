"""OSM rond Assepoester in modelcoordinaten (gevel -Y = west, +X = zuid) + plattegrondplaatje ref/plan_model.png."""
import json, math
from PIL import Image, ImageDraw
D = "/Users/daaniding/RobloxProjects/efteling-roblox/models/AR_Assepoester/ref/"
d = json.load(open(D + "osm_lokaal.json"))
a = math.atan2(0.74, 3.94); u = (-math.sin(a), math.cos(a)); f = (-math.cos(a), -math.sin(a))
X0, Y0 = 0.5935059151915971, -7.50008084397333
def M(p): return (round(-(p[0]*u[0]+p[1]*u[1]) - X0, 2), round(-(p[0]*f[0]+p[1]*f[1]) - Y0, 2))
out = {"ways": [], "nodes": []}
for w in d["ways"]:
    out["ways"].append({"id": w["id"], "tags": w["tags"], "pts": [M(p) for p in w["pts"]]})
for n in d["nodes"]:
    out["nodes"].append({"tags": n["tags"], "p": M(n["p"])})
json.dump(out, open(D + "osm_model.json", "w"), indent=1, ensure_ascii=False)
S = 20; R = 30; W = 2*R*S
im = Image.new("RGB", (W, W), "white"); dr = ImageDraw.Draw(im)
P = lambda p: (W/2 + p[0]*S, W/2 + p[1]*S)     # x naar rechts (zuid), y naar beneden (oost/achter); west = boven
for g in range(-R, R+1, 2):
    c = (215, 215, 215) if g % 10 else (170, 170, 170)
    dr.line([P((g, -R)), P((g, R))], fill=c); dr.line([P((-R, g)), P((R, g))], fill=c)
for w in out["ways"]:
    t = w["tags"]; c = (130, 130, 130); wd = 2
    if "building" in t: c = (200, 50, 50); wd = 3
    elif t.get("barrier") == "hedge": c = (30, 140, 30); wd = 5
    elif "barrier" in t: c = (150, 80, 0); wd = 4
    elif "highway" in t: c = (60, 60, 210)
    elif t.get("natural") == "water": c = (0, 160, 220)
    elif t.get("leisure") == "garden" or t.get("natural") == "shrubbery": c = (120, 200, 90)
    dr.line([P(p) for p in w["pts"]], fill=c, width=wd)
    if any(abs(p[0]) < R and abs(p[1]) < R for p in w["pts"]):
        q = min(w["pts"], key=lambda p: abs(p[0]) + abs(p[1]))
        dr.text(P(q), (t.get("name") or t.get("barrier") or t.get("highway") or t.get("building") or t.get("leisure") or t.get("natural") or "") + " " + w["id"][-4:], fill=c)
for n in out["nodes"]:
    x, y = P(n["p"]); dr.ellipse([x-5, y-5, x+5, y+5], fill="black")
    dr.text((x+6, y), "/".join(f"{k}={v}" for k, v in n["tags"].items() if k in ("entrance", "barrier", "highway", "amenity", "name"))[:28], fill="black")
dr.text((4, 4), "MODEL: west (gevel kijkt) = boven, zuid (+x) = rechts, raster 2 m", fill="black")
im.save(D + "plan_model.png")
for w in out["ways"]:
    if any(abs(p[0]) < 22 and -22 < p[1] < 22 for p in w["pts"]):
        print(w["id"], {k: v for k, v in w["tags"].items() if k in ("building","barrier","highway","name","leisure","natural","area","surface","width")}, w["pts"])
for n in out["nodes"]:
    if abs(n["p"][0]) < 22 and abs(n["p"][1]) < 22: print("N", n["p"], n["tags"])
