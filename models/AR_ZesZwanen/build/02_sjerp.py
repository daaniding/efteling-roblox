"""02_sjerp: sjerp-texturen voor de zwanen (band met gouden ranken), twee kleuren (rood zoals D6z_zwaan_plaatsing/klaar_voor_vertrek, teal zoals het ontwerp)."""
import math
from PIL import Image, ImageDraw, ImageFilter
W, H = 1024, 256
for naam, grond, rand in (("rood", (150, 28, 30), (220, 170, 70)), ("teal", (34, 92, 96), (214, 168, 72))):
    im = Image.new("RGB", (W, H), grond); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 26], fill=rand); d.rectangle([0, H - 26, W, H], fill=rand)
    d.rectangle([0, 26, W, 32], fill=(40, 30, 20)); d.rectangle([0, H - 32, W, H - 26], fill=(40, 30, 20))
    for k in range(8):                                                                   # golvende rank met krullen en blaadjes
        x0 = k * W / 8
        pts = [(x0 + t * W / 8, H / 2 + 42 * math.sin(t * math.tau)) for t in [i / 40 for i in range(41)]]
        d.line(pts, fill=rand, width=9)
        for (cx, cy, sgn) in ((x0 + W / 32, H / 2 + 30, 1), (x0 + 3 * W / 32, H / 2 - 30, -1)):
            for i in range(30):
                a = i / 29 * 1.7 * math.tau; r = 26 * (1 - i / 34)
                d.ellipse([cx + r * math.cos(a) - 4, cy + sgn * r * math.sin(a) - 4, cx + r * math.cos(a) + 4, cy + sgn * r * math.sin(a) + 4], fill=rand)
        d.ellipse([x0 + W / 16 - 10, H / 2 - 10, x0 + W / 16 + 10, H / 2 + 10], fill=(240, 236, 220))
    im = im.filter(ImageFilter.SMOOTH)
    im.save(f"/Users/daaniding/RobloxProjects/efteling-roblox/models/AR_ZesZwanen/textures/ZW_sjerp_{naam}.png")
print("sjerp ok")
