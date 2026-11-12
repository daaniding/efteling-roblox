"""Vult HUIS, OMG en TEX in roblox/plaats_assepoester.luau uit textures/asset_ids.txt en exports/omgeving_id.txt (na build/bouw_alles.sh)."""
import re, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ids = dict(l.split() for l in open(os.path.join(D, "textures", "asset_ids.txt")) if l.strip())
omg = open(os.path.join(D, "exports", "omgeving_id.txt")).read().strip()
tex = {}
for k, v in ids.items():
    if k == "MODEL": continue
    name, kind = k.replace("Assepoester_", "").rsplit("_", 1)
    tex.setdefault(name, [None, None])[0 if kind == "kleur" else 1] = v
t = "{" + ", ".join("%s = {%s%s}" % (k, v[0], (", " + v[1]) if v[1] else "") for k, v in sorted(tex.items())) + "}"
p = os.path.join(D, "roblox", "plaats_assepoester.luau"); s = open(p).read()
s = re.sub(r"local HUIS = \d+", "local HUIS = " + ids["MODEL"], s)
s = re.sub(r"local OMG = \d+", "local OMG = " + omg, s)
s = re.sub(r"local TEX = \{.*?\}\}", "local TEX = " + t, s, flags=re.S)
open(p, "w").write(s); print("HUIS", ids["MODEL"], "OMG", omg)
