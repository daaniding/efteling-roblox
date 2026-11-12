"""Maakt plaats_sprookjesboom.luau uit plaats_template.luau + asset_ids.json + OSM-punten van de muzikale paddenstoelen.
Gebruik: python3 maak_plaatsscript.py   (leest asset_ids.json naast dit bestand)"""
import csv, json, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ids = json.load(open(os.path.join(HERE, "asset_ids.json")))
rnd = random.Random(11)
# kleine paddenstoelen aan de voet (front.jpg / front_high.jpg): twee groepjes links- en rechtsvoor, tussen de wortelvoeten
KLEIN = [(-2.45, -1.05, 1.00), (-2.15, -1.60, 0.85), (-1.75, -2.00, 1.15), (-2.85, -0.45, 0.80), (-1.30, -2.30, 0.90),
         (-3.00, -1.35, 0.70), (2.00, -1.65, 1.10), (2.45, -1.20, 0.95), (1.65, -2.05, 0.80), (2.95, -0.55, 0.85),
         (2.65, -1.75, 0.70), (-0.55, -2.55, 0.75)]
# x1.4: front.jpg hoed ~0.38 m breed, ~0.45 m hoog (model is 0.33 x 0.36 m)
klein = "{" + ", ".join("{%.2f, %.2f, %.2f, %d}" % (x, y, s * 1.4, rnd.randint(0, 359)) for x, y, s in KLEIN) + "}"
muz = []
for r in csv.DictReader(open(os.path.join(REPO, "reference", "data", "efteling_objecten_meters.csv"))):
    if r["naam"].startswith("Muzikale Paddenstoel"):
        x, y = float(r["x_min"]), float(r["y_min"])
        muz.append("{%.2f, %.2f, %d}" % (x * 3, -y * 3, rnd.randint(0, 359)))
lua_ids = "{" + ", ".join(f"{k} = {v}" for k, v in ids.items()) + "}"
t = open(os.path.join(HERE, "plaats_template.luau")).read()
t = t.replace("__IDS__", lua_ids).replace("__KLEIN__", klein).replace("__MUZIEK__", "{" + ", ".join(muz) + "}")
open(os.path.join(HERE, "plaats_sprookjesboom.luau"), "w").write(t)
print("geschreven", len(t), "tekens,", len(muz), "muzikale paddenstoelen")
