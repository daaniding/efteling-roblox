"""maak_plaatsscript.py -> roblox/plaats_zwavelstokjes.luau (uitvoeren in Studio, Edit). Oorsprong = OSM-zwaartepunt 279667968."""
import json, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = json.load(open(D + "/ref/osm_lokaal.json")); M_ = json.load(open(D + "/ref/osm_model.json"))
ids = dict(l.split() for l in open(D + "/textures/asset_ids.txt") if len(l.split()) == 2)
cx, cy = O["oorsprong_osm_m"]; n = M_["n"]
def tex(pre):
    out = []
    for k, v in ids.items():
        if k.startswith(pre) and k.endswith("_kleur"):
            nm = k[len(pre):-len("_kleur")]; nn = ids.get(f"{pre}{nm}_normaal")
            out.append(f"{nm} = {{{v}{', ' + nn if nn else ''}}}")
    return "{" + ", ".join(out) + "}"
VIJ = M_["ways"]["767716993"]
src = open(D + "/roblox/plaats_template.luau").read()
for k, v in {"@STADJE@": ids["MODEL_stadje"], "@TEX@": tex("MZ_"), "@OX@": str(round(cx * 3, 2)), "@OZ@": str(round(-cy * 3, 2)),
             "@FX@": str(n[0]), "@FZ@": str(-n[1]), "@VIJ@": json.dumps(VIJ).replace("[", "{").replace("]", "}")}.items():
    src = src.replace(k, str(v))
open(D + "/roblox/plaats_zwavelstokjes.luau", "w").write(src); print("bytes", len(src))
