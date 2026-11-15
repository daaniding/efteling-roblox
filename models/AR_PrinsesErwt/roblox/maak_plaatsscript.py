"""maak_plaatsscript.py: vult asset-ids (textures/asset_ids.txt) + botsing/lampen (exports/*_extra.json) in en schrijft plaats_prinseserwt.luau."""
import json, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ids = dict(l.split()[:2] for l in open(os.path.join(D, "textures", "asset_ids.txt")) if l.strip())
def tex(pre):
    out = {}
    for k, v in ids.items():
        if k.startswith(pre + "_") and k.endswith("_kleur"):
            n = k[len(pre) + 1:-6]; nrm = ids.get(f"{pre}_{n}_normaal")
            out[n] = [v] + ([nrm] if nrm else [])
    return "{" + ", ".join(f"{k} = {{{', '.join(v)}}}" for k, v in sorted(out.items())) + "}"
hx = json.load(open(os.path.join(D, "exports", "huis_extra.json"))); ox = json.load(open(os.path.join(D, "exports", "omgeving_extra.json")))
lua = lambda L: "{" + ", ".join("{" + ", ".join(str(round(v, 3)) for v in c) + "}" for c in L) + "}"
src = open(os.path.join(D, "roblox", "plaats_template.luau")).read()
src = (src.replace("@HUIS@", ids["MODEL_huis"]).replace("@OMG@", ids["MODEL_omgeving"]).replace("@TEXH@", tex("PE")).replace("@TEXO@", tex("PO"))
       .replace("@COLLH@", lua(hx["colliders"])).replace("@COLLO@", lua(ox["colliders"])).replace("@PLEIN@", lua(ox["plein"])))
open(os.path.join(D, "roblox", "plaats_prinseserwt.luau"), "w").write(src)
print("ok", len(src), "tekens")
