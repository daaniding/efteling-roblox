"""maak_plaatsscript: vult asset-ids, texturen en botsblokken (uit exports/*_extra.json) in plaats_template.luau -> plaats_roodkapje.luau"""
import json, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ids = dict(l.split() for l in open(os.path.join(D, "textures", "asset_ids.txt")) if l.strip())
def tex(pre):
    out = {}
    for k, v in ids.items():
        if k.startswith(pre + "_") and k.endswith("_kleur"):
            n = k[len(pre) + 1:-6]; out[n] = (v, ids.get(f"{pre}_{n}_normaal"))
    return "{" + ", ".join(f"{n} = {{{c}, {nm or 'nil'}}}" for n, (c, nm) in sorted(out.items())) + "}"
def lua(v):
    if isinstance(v, list): return "{" + ", ".join(lua(x) for x in v) + "}"
    return repr(round(v, 3)) if isinstance(v, float) else str(v)
eh = json.load(open(os.path.join(D, "exports", "huisje_extra.json"))); eo = json.load(open(os.path.join(D, "exports", "omgeving_extra.json")))
t = open(os.path.join(D, "roblox", "plaats_template.luau")).read()
t = (t.replace("%HUIS%", ids["MODEL_huisje"]).replace("%OMG%", ids["MODEL_omgeving"]).replace("%TEXH%", tex("RK")).replace("%TEXO%", tex("RO"))
      .replace("%COLLH%", lua(eh["colliders"])).replace("%COLLO%", lua(eo["colliders"])).replace("%SEG%", lua(eo["padsegmenten"]))
      .replace("%POLY%", lua(eo["poly"])))
open(os.path.join(D, "roblox", "plaats_roodkapje.luau"), "w").write(t)
print("plaats_roodkapje.luau", len(t), "bytes")
