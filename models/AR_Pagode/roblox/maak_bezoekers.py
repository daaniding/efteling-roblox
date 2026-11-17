"""maak_bezoekers: vult de route (exports/bezoekersroute.json) in PagodeBezoekers.server.luau -> PagodeBezoekers.luau (plakklaar)."""
import json, os
R = os.path.dirname(os.path.abspath(__file__)); D = os.path.dirname(R)
route = json.load(open(os.path.join(D, "exports", "bezoekersroute.json")))
lua = "{" + ",".join("{%.2f,%.2f,%.2f}" % tuple(p) for p in route) + "}"
src = open(os.path.join(R, "PagodeBezoekers.server.luau")).read().replace("__ROUTE__", lua)
open(os.path.join(R, "PagodeBezoekers.luau"), "w").write(src)
print("PagodeBezoekers.luau", len(src), "tekens,", len(route), "punten")
