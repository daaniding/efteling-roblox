"""
07_data_png: omgeving_data.json -> exports/omgeving_data.png (2 RGBA-pixels per record) voor Studio (EditableImage).
Record: px1 = (soort, x_hi, x_lo, y_hi), px2 = (y_lo, schaal*100, draai/360*255, 200 + groep).
x, y in centimeter + 40000 (bereik -400..+255 m). Groepen: 0 plant, 1 oeversteen, 2 kei, 3 vrij-punt, 4 beek-omtrek, 5 water-omtrek.
Soorten (planten): zie SOORTEN; stenen: prototype 0-5.
"""
import json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "..")
d = json.load(open(os.path.join(A, "exports", "omgeving_data.json")))
SOORTEN = ["rodo", "taxus", "struik", "varen", "brandnetel", "maagdenpalm", "zuring", "struikje", "gras"]
recs = []


def rec(soort, x, y, s, rot, groep):
    xi = int(round(x * 100)) + 40000; yi = int(round(y * 100)) + 40000
    recs.append([(soort, xi >> 8, xi & 255, yi >> 8), (yi & 255, min(255, int(round(s * 100))), int(rot / 360 * 255) % 256, 200 + groep)])   # alpha nooit 0 (upload kan transparante pixels leegmaken)


for s, x, y, sc, r in d["planten"]: rec(SOORTEN.index(s), x, y, sc, r, 0)
for x, y, rad, k, r in d["stenen"]: rec(k, x, y, rad, r, 1)
for x, y, rad, k, r in d["keien"]: rec(k, x, y, rad, r, 2)
for x, y in d["vrij"]: rec(0, x, y, 0, 0, 3)
for p in d["beek"]:
    for x, y in p["ext"]: rec(0, x, y, 0, 0, 4)
W = 256; n = len(recs) * 2; H = (n + W - 1) // W
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = im.load()
for i, (a, b) in enumerate(recs):
    for j, c in enumerate((a, b)):
        k = i * 2 + j; px[k % W, k // W] = c
im.save(os.path.join(A, "exports", "omgeving_data.png"))
print("records", len(recs), "png", W, "x", H, {g: sum(1 for r in recs if r[1][3] == 200 + g) for g in range(6)})
