"""maak_plaatsscript.py -> roblox/plaats_klerenkeizer.luau (uitvoeren in Studio, Edit).
Zet decor + omgeving op de OSM-plek (oorsprong = midden lange vijver, OSM lokaal (1.2, 4.37) t.o.v. attractievlak 50911607),
fonteinen als waterstralen (ParticleEmitter), haagtextuur, lampen; Ground onder het plein (geen grassprieten door de klinkers)."""
import json, math, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = json.load(open(D + "/ref/osm_lokaal.json"))
ids = dict(l.split() for l in open(D + "/textures/asset_ids.txt") if len(l.split()) == 2)
cx, cy = O["oorsprong_osm_m"]
ox, oy = cx + 1.2, cy + 4.37                                   # midden vijver (OSM globaal, m)
n = (0.116, 0.993)                                             # voorkant-normaal (naar de bezoekers, noord), uit vijver 767716986 / muur 767716987
FX, FZ = n[0], -n[1]
fonteinen = json.load(open(D + "/exports/decor_extra.json"))["fonteinen"]
def tex(pre):
    out = []
    for k, v in ids.items():
        if k.startswith(pre) and k.endswith("_kleur"):
            nm = k[len(pre):-len("_kleur")]; nn = ids.get(f"{pre}{nm}_normaal")
            out.append(f"{nm} = {{{v}{', ' + nn if nn else ''}}}")
    return "{" + ", ".join(out) + "}"
src = open(D + "/roblox/plaats_template.luau").read()
for k, v in {"@DECOR@": ids["MODEL_decor"], "@OMG@": ids["MODEL_omgeving"], "@TEXD@": tex("KD_"),
             "@OX@": str(round(ox * 3, 2)), "@OZ@": str(round(-oy * 3, 2)), "@FX@": str(FX), "@FZ@": str(FZ),
             "@FONT@": json.dumps(fonteinen).replace("[", "{").replace("]", "}")}.items():
    src = src.replace(k, str(v))
open(D + "/roblox/plaats_klerenkeizer.luau", "w").write(src)
print("oorsprong studs", round(ox * 3, 2), round(-oy * 3, 2), "bytes", len(src), "fonteinen", len(fonteinen))
