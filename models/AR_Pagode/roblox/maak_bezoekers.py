"""maak_bezoekers: vult de route (exports/bezoekersroute.json) in PagodeBezoekers.server.luau -> PagodeBezoekers.luau (plakklaar)."""
import json, os
R = os.path.dirname(os.path.abspath(__file__)); D = os.path.dirname(R)
route = json.load(open(os.path.join(D, "exports", "bezoekersroute.json")))
lua = "{" + ",".join("{%.2f,%.2f,%.2f}" % tuple(p) for p in route) + "}"
src = open(os.path.join(R, "PagodeBezoekers.server.luau")).read().replace("__ROUTE__", lua)
wb = json.load(open(os.path.join(D, "exports", "wachttijdbord.json")))
src = src.replace("__WACHTTIJDBORD__", "{midden = {%.4f, %.4f, %.4f}, normaal = {%.5f, %.5f}, breed = %.2f, hoog = %.2f}" % (*wb["midden"], *wb["normaal"], wb["breed"], wb["hoog"]))
open(os.path.join(R, "PagodeBezoekers.luau"), "w").write(src)
print("PagodeBezoekers.luau", len(src), "tekens,", len(route), "punten")
