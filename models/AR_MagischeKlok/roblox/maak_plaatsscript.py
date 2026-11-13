"""Vult MODEL en TEX in roblox/plaats_magischeklok.luau uit textures/asset_ids.txt (na build/bouw_alles.sh)."""
import re, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ids = dict(l.split() for l in open(os.path.join(D, "textures", "asset_ids.txt")) if l.strip())
tex = {}
for k, v in ids.items():
    if k == "MODEL": continue
    name, kind = k.replace("MK_", "").rsplit("_", 1)
    tex.setdefault(name, [None, None])[0 if kind == "kleur" else 1] = v
t = "{" + ", ".join("%s = {%s%s}" % (k, v[0], (", " + v[1]) if v[1] else "") for k, v in sorted(tex.items())) + "}"
p = os.path.join(D, "roblox", "plaats_magischeklok.luau"); s = open(p).read()
s = re.sub(r"local MODEL = \d+", "local MODEL = " + ids["MODEL"], s)
s = re.sub(r"local TEX = \{.*?\}\}", "local TEX = " + t, s, flags=re.S)
import json
coll = json.load(open(os.path.join(D, "exports", "klok_extra.json")))["colliders"]
s = re.sub(r"local COLL = \{.*?\}\}", "local COLL = {" + ", ".join("{" + ", ".join(str(v) for v in c) + "}" for c in coll) + "}", s, flags=re.S)
open(p, "w").write(s); print("MODEL", ids["MODEL"], "TEX", len(tex), "COLL", len(coll))
