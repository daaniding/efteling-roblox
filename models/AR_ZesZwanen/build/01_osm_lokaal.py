"""OSM rond De Zes Zwanen -> modelframe (m): oorsprong = midden kasteel-footprint (OSM 961616753), voorkant (naar de vijver) = -Y,
+X = rechts voor wie naar het kasteel kijkt (zoals Sneeuwwitje). Schrijft ref/model_frame.json + ref/osm_model.json + review/osm_model.png."""
import json, math
from PIL import Image, ImageDraw
R = "/Users/daaniding/RobloxProjects/efteling-roblox/models/AR_ZesZwanen"
o = json.load(open(R + "/ref/osm_lokaal.json"))
W = {e["id"]: e for e in o}
def cen(pts):
    p = pts[:-1] if pts[0] == pts[-1] else pts
    return (sum(a for a, _ in p) / len(p), sum(b for _, b in p) / len(p))
cx, cy = cen(W["961616753"]["pts"]); vx, vy = cen(W["961616757"]["pts"])
n = (vx - cx, vy - cy); L = math.hypot(*n); n = (n[0] / L, n[1] / L)        # voorkant-normaal (OSM)
r = (-n[1], n[0])                                                          # +X: rot90 ccw
def mf(p): d = (p[0] - cx, p[1] - cy); return [round(d[0] * r[0] + d[1] * r[1], 2), round(-(d[0] * n[0] + d[1] * n[1]), 2)]
out = []
for e in o:
    q = [mf(p) for p in e["pts"]]
    if min(math.hypot(*p) for p in q) < 40: out.append({"id": e["id"], "type": e["type"], "tags": e["tags"], "pts": q})
json.dump(out, open(R + "/ref/osm_model.json", "w"))
json.dump({"oorsprong_osm_m": [round(cx, 2), round(cy, 2)], "roblox_studs": [round(cx * 3, 2), round(-cy * 3, 2)],
           "voor_normaal_osm": [round(n[0], 4), round(n[1], 4)], "F_roblox": [round(n[0], 4), 0, round(-n[1], 4)]}, open(R + "/ref/model_frame.json", "w"), indent=1)
S = 16; X0, X1, Y0, Y1 = -30, 30, -32, 22
im = Image.new("RGB", ((X1 - X0) * S, (Y1 - Y0) * S), "white"); d = ImageDraw.Draw(im)
P = lambda p: ((p[0] - X0) * S, (Y1 - p[1]) * S)
for g in range(X0, X1 + 1, 2): d.line([P((g, Y0)), P((g, Y1))], fill=(235, 235, 235) if g % 10 else (190, 190, 190))
for g in range(Y0, Y1 + 1, 2): d.line([P((X0, g)), P((X1, g))], fill=(235, 235, 235) if g % 10 else (190, 190, 190))
for e in out:
    t = e["tags"]; pts = [P(p) for p in e["pts"]]
    if e["type"] == "node": x, y = pts[0]; d.ellipse([x - 5, y - 5, x + 5, y + 5], fill="red"); d.text((x + 6, y), (list(t.values()) or ["?"])[0][:12], fill="red"); continue
    if "water" in t.get("natural", ""): d.polygon(pts, fill="#bfe3fa", outline="#4aa3df")
    elif t.get("natural") == "rock": d.polygon(pts, fill="#c8c2b4", outline="#776")
    elif "building" in t: d.polygon(pts, fill="#e9a0a0" if t.get("name") == "De zes Zwanen" else "#f2d0a0", outline="black")
for e in out:
    t = e["tags"]; pts = [P(p) for p in e["pts"]]
    if e["type"] == "way" and len(pts) > 1 and not ("water" in t.get("natural", "") or t.get("natural") == "rock" or "building" in t):
        c = "blue" if t.get("railway") else ("purple" if t.get("barrier") == "fence" else ("green" if t.get("barrier") else "#a87"))
        d.line(pts, fill=c, width=3 if t.get("railway") != "narrow_gauge" or t.get("name") == "De zes Zwanen" else 2)
for g in range(X0, X1 + 1, 10): d.text(P((g, Y0 + 0.3)), str(g), fill="black")
for g in range(Y0, Y1 + 1, 10): d.text(P((X0 + 0.2, g)), str(g), fill="black")
im.save(R + "/review/osm_model.png"); print(json.load(open(R + "/ref/model_frame.json")))
