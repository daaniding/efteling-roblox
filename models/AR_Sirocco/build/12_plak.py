"""12_plak: vult __LAMPEN__ en __VIJVER__ in roblox/plaats_sirocco.luau in -> roblox/plaats_sirocco_plak.luau (plakken in Studio)."""
import json, os, math
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = json.load(open(os.path.join(D, "exports", "export_info.json"))); o = json.load(open(os.path.join(D, "exports", "omgeving_info.json")))
lua = lambda pts: "{" + ", ".join("{" + ", ".join(f"{v:.3f}" for v in p) + "}" for p in pts) + "}"
import numpy as np
from PIL import Image
# terreinklassen per vierkante meter uit de luchtfoto (ref/luchtfoto: midden park (455; 188), 70 m, 0,05 m/px):
# v = verhard plein/pad, g = groen (plantvak), z = zand (Archipel); daarna meerderheidsfilter en handmatige plantvakken
a = np.asarray(Image.open(os.path.join(D, "ref", "luchtfoto", "luchtfoto.jpg")).convert("RGB")).astype(float)
px = a.shape[1] / 70.0
r, g, b = a[..., 0], a[..., 1], a[..., 2]; mx = a.max(2); mn = a.min(2); sat = (mx - mn) / (mx + 1)
veg = ((g > r * 0.98) & (g > b * 1.02) & (sat > 0.12)) | ((mx < 90) & (g >= r))
zand = (r > g * 1.08) & (r > b * 1.25) & (mx > 140)
K = np.zeros((70, 70), int)
for j in range(70):
    for i in range(70):
        sl = (slice(int(j * px), int((j + 1) * px)), slice(int(i * px), int((i + 1) * px)))
        K[j, i] = 1 if veg[sl].mean() > 0.4 else 2 if zand[sl].mean() > 0.45 else 0
for _ in range(2):
    K2 = K.copy()
    for j in range(1, 69):
        for i in range(1, 69):
            c = np.bincount(K[j - 1:j + 2, i - 1:i + 2].ravel(), minlength=3)
            if c.max() >= 6: K2[j, i] = c.argmax()
    K = K2
BEDDEN = [[(-15, 4), (-19, 7), (-20.5, 13), (-17, 19), (-11, 21.5), (-5, 22), (-6, 17), (-11, 14), (-13, 9)]]   # plantvak NW (kale bomen)
def binnen(x, y, P):
    c = False; j = len(P) - 1
    for i in range(len(P)):
        (xi, yi), (xj, yj) = P[i], P[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: c = not c
        j = i
    return c
rijen = []
for jj in range(-35, 35):              # model-y van -35 tot 34 (cel-midden +0,5)
    rij = ""
    for ii in range(-35, 35):
        x, y = ii + 0.5, jj + 0.5
        pi, pj = int(x + 456.5 - 420), int(223 - (y + 191.2))
        k = K[pj, pi] if 0 <= pi < 70 and 0 <= pj < 70 else 1
        if any(binnen(x, y, P) for P in BEDDEN): k = 1
        STRAND = [(-12.0, -6.0), (-11.2, -7.6), (-11.6, -8.8), (-12.6, -10.0), (-13.8, -11.6), (-14.6, -12.3), (-16.0, -11.7), (-17.0, -10.2),
                  (-17.3, -8.0), (-16.6, -6.0), (-14.6, -4.9), (-12.9, -4.6)]       # = 07_omgeving.STRAND
        if binnen(x, y, STRAND): rij += "z"; continue
        if binnen(x, y, [(-9.8, -15.2), (-9.6, -13.6), (-8.8, -12.0), (-7.5, -11.0), (-3.5, -11.0), (-3.6, -16.8), (-8.4, -16.6)]):
            rij += "a"; continue                                # plantvak met witte rand: donkere aarde (= 07_omgeving.BED_HAVEN)
        if math.hypot(x, y) < 17:      # band om de vijver: plein langs de west-/zuidkant, verder plantvak (luchtfoto)
            k = 0 if ((x < -11 and -13 < y < 7) or (x < -9.5 and y < -12.5) or y < -15.5) else 1
        rij += "vgz"[k]
    rijen.append(rij)
s = open(os.path.join(D, "roblox", "plaats_sirocco.luau")).read()
s = s.replace("__KLASSEN__", "{" + ", ".join(f'"{r}"' for r in rijen) + "}")
s = s.replace("__LAMPEN__", lua(e["lampen"] + o["lampen"])).replace("__VIJVER__", lua(o["vijver"]))
open(os.path.join(D, "roblox", "plaats_sirocco_plak.luau"), "w").write(s)
print("[12_plak]", len(e["lampen"]) + len(o["lampen"]), "lampen,", len(o["vijver"]), "vijverpunten")
