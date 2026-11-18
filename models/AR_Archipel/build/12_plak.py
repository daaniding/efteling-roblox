"""12_plak: vult __KADE__ en __LAMPEN__ in roblox/plaats_archipel.luau in -> roblox/plaats_archipel_plak.luau (plakken in Studio)."""
import json, os, sys
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, "build"))
import plan as P
e = json.load(open(os.path.join(D, "exports", "export_info.json")))
lua = lambda pts: "{" + ", ".join("{" + ", ".join(f"{v:.3f}" for v in p) + "}" for p in pts) + "}"
s = open(os.path.join(D, "roblox", "plaats_archipel.luau")).read()
s = s.replace("= __KADE__", "= " + lua(P.KADE)).replace("= __LAMPEN__", "= " + lua(e["lampen"]))
open(os.path.join(D, "roblox", "plaats_archipel_plak.luau"), "w").write(s)
print("[12_plak]", len(P.KADE), "kadepunten,", len(e["lampen"]), "lampen ->", len(s), "tekens")
