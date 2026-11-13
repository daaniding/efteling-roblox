"""maak_plaatsscript.py -> roblox/plaats_zeszwanen.luau (plakken/uitvoeren in Studio).
Zet de drie modellen (kasteel, omgeving, 6 zwanen) op de OSM-plek, graaft terrein onder de vijvers weg (4-stud cellen),
maakt Ground onder pad + oevergrond (geen grassprieten door de meshes), haalt oude bomen/layout in de plek weg."""
import json, math, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FR = json.load(open(D + "/ref/model_frame.json")); O = {e["id"]: e for e in json.load(open(D + "/ref/osm_model.json"))}
ids = dict(l.split() for l in open(D + "/textures/asset_ids.txt"))
S = 3; OX, OZ = FR["roblox_studs"]; FX, _, FZ = FR["F_roblox"]; A0 = math.atan2(-FX, -FZ)
def wereld(x, y):                                                    # modelframe (m) -> Roblox X,Z (zelfde als lokaal() in Luau)
    lx, lz = -x * S, y * S
    return OX + lx * math.cos(A0) + lz * math.sin(A0), OZ - lx * math.sin(A0) + lz * math.cos(A0)
def model(X, Z):
    dx, dz = X - OX, Z - OZ
    lx = dx * math.cos(A0) - dz * math.sin(A0); lz = dx * math.sin(A0) + dz * math.cos(A0)
    return -lx / S, lz / S
def P(i): p = [tuple(q) for q in O[i]["pts"]]; return p[:-1] if p[0] == p[-1] else p
def inside(px, py, poly):
    c = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi: c = not c
        j = i
    return c
def segdist(px, py, pts):
    b = 1e9
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-9; t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
        b = min(b, math.hypot(px - ax - t * dx, py - ay - t * dy))
    return b
VIJ = [P("961616757"), P("961616758"), P("961616760")]; PAD = P("961616754")
VOET = [P(i) for i in ("1169016139", "1255787237", "1169016140", "1255787243", "729126648")]
graaf, grond = [], []
xs, zs = zip(*[wereld(x, y) for x in (-14, 23) for y in (-29, 10)])
for i in range(int(min(xs) // 4) - 1, int(max(xs) // 4) + 2):
    for j in range(int(min(zs) // 4) - 1, int(max(zs) // 4) + 2):
        mx, my = model(i * 4 + 2, j * 4 + 2)
        if any(inside(mx, my, v) for v in VIJ): graaf.append(f"{i},{j}")
        elif inside(mx, my, PAD) or any(segdist(mx, my, f) < 1.4 for f in VOET) or any(segdist(mx, my, v + [v[0]]) < 2.0 for v in VIJ): grond.append(f"{i},{j}")
ZW = json.load(open(D + "/exports/zwanen.json"))
def tex(pre):
    out = []
    for k, v in ids.items():
        if k.startswith(pre) and k.endswith("_kleur"):
            n = k[len(pre):-len("_kleur")]; nm = ids.get(f"{pre}{n}_normaal")
            out.append(f"{n} = {{{v}{', ' + nm if nm else ''}}}")
    return "{" + ", ".join(out) + "}"
src = open(D + "/roblox/plaats_template.luau").read()
for k, v in {"@KASTEEL@": ids["MODEL_kasteel"], "@OMG@": ids["MODEL_omgeving"], "@ZWAAN@": ids["MODEL_zwaan"], "@TEXK@": tex("ZK_"), "@TEXO@": tex("ZO_"),
             "@SJERP@": "{%s, %s}" % (ids["ZW_sjerp_rood"], ids["ZW_sjerp_teal"]), "@OX@": str(OX), "@OZ@": str(OZ), "@FX@": str(FX), "@FZ@": str(FZ),
             "@GRAAF@": ";".join(graaf), "@GROND@": ";".join(grond), "@ZWANEN@": json.dumps(ZW).replace("[", "{").replace("]", "}")}.items():
    src = src.replace(k, v)
open(D + "/roblox/plaats_zeszwanen.luau", "w").write(src)
print("graaf", len(graaf), "grond", len(grond), "bytes", len(src))
