"""03a_atlas Magische Klok: getekende texturen (PIL), geen bake nodig.
- textures/MK_klok_kleur.png: voorkant uurwerk (1.5 x 1.45 m), Piecksblauw, witte Romeinse cijfers, krullen in de hoeken, stijlen met rode bloempjes
  (Magischeklokklok.jpg). Wijzers zijn geometrie (goud).
- textures/MK_ruiter_kleur.png: ruitertje (wit paard, rood-wit gestreept dekkleed, ridder met helm en lans), RGBA met alpha (Ruitertje0.JPG).
Gebruik: python3 build/03a_atlas.py"""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "textures"); os.makedirs(D, exist_ok=True)

# ---------------- uurwerk ----------------
W, H = 1024, 990                          # verhouding 1.5 : 1.45
BLAUW, LICHT, WIT, ROOD, GOUD = (44, 92, 88), (58, 110, 104), (236, 236, 226), (196, 70, 50), (214, 170, 70)
im = Image.new("RGB", (W, H), BLAUW); d = ImageDraw.Draw(im)
sw = 118                                   # stijlen links en rechts
for x0 in (0, W - sw):
    d.rectangle([x0, 0, x0 + sw, H], fill=LICHT); d.rectangle([x0 + 8, 8, x0 + sw - 8, H - 8], outline=WIT, width=5)
    for k in range(9):                     # rode bloempjes met witte rankjes
        cy = 70 + k * (H - 140) / 8; cx = x0 + sw / 2
        for a in range(5):
            t = a * math.tau / 5; d.ellipse([cx + 15 * math.cos(t) - 9, cy + 15 * math.sin(t) - 9, cx + 15 * math.cos(t) + 9, cy + 15 * math.sin(t) + 9], fill=ROOD)
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=GOUD)
        if k < 8: d.arc([cx - 30, cy + 10, cx + 30, cy + 95], 200, 340, fill=WIT, width=4)
d.rectangle([0, 0, W - 1, H - 1], outline=(30, 64, 60), width=10)
cx, cy, R = W / 2, H / 2, 380
for (qx, qy) in ((sw + 60, 60), (W - sw - 60, 60), (sw + 60, H - 60), (W - sw - 60, H - 60)):   # krullen in de hoeken
    sx = 1 if qx < cx else -1; sy = 1 if qy < cy else -1
    for k in range(3):
        r = 40 + 26 * k
        d.arc([qx - r, qy - r, qx + r, qy + r], 0, 360, fill=WIT, width=5) if k == 0 else d.arc([qx - r, qy - r, qx + r, qy + r], 0 if sx > 0 else 90, 270 if sx > 0 else 360, fill=WIT, width=5)
    d.ellipse([qx - 16, qy - 16, qx + 16, qy + 16], fill=WIT); d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=BLAUW)
d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=WIT, width=8)
d.ellipse([cx - R + 120, cy - R + 120, cx + R - 120, cy + R - 120], outline=WIT, width=7)
ROM = ["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
try: font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf", 78)
except Exception: font = ImageFont.load_default()
for i, s in enumerate(ROM):                # cijfers radiaal, voet naar het midden
    a = math.radians(i * 30); tile = Image.new("RGBA", (220, 110), (0, 0, 0, 0)); td = ImageDraw.Draw(tile)
    bb = td.textbbox((0, 0), s, font=font); td.text(((220 - (bb[2] - bb[0])) / 2 - bb[0], (110 - (bb[3] - bb[1])) / 2 - bb[1]), s, fill=WIT, font=font)
    tile = tile.rotate(-i * 30, expand=True, resample=Image.BICUBIC)
    px = cx + (R - 62) * math.sin(a); py = cy - (R - 62) * math.cos(a)
    im.paste(tile, (int(px - tile.width / 2), int(py - tile.height / 2)), tile)
for m in range(60):                        # minuutstreepjes
    a = math.radians(m * 6); r0 = R - 8; r1 = R - (22 if m % 5 == 0 else 14)
    d.line([cx + r0 * math.sin(a), cy - r0 * math.cos(a), cx + r1 * math.sin(a), cy - r1 * math.cos(a)], fill=WIT, width=4)
im = im.filter(ImageFilter.SMOOTH)
im.save(os.path.join(D, "MK_klok_kleur.png"))

# ---------------- ruitertje ----------------
S = 512; r = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(r)
WITP, ZW, RO, HUID, GRIJS = (238, 234, 222, 255), (30, 28, 26, 255), (190, 40, 36, 255), (226, 186, 150, 255), (150, 150, 150, 255)
# paard (springend, kop links)
d.polygon([(150, 250), (330, 240), (380, 270), (395, 330), (360, 345), (170, 350), (130, 320)], fill=WITP)      # romp
d.polygon([(150, 255), (95, 175), (70, 150), (40, 165), (55, 190), (95, 210), (120, 290)], fill=WITP)          # hals + kop
d.polygon([(70, 150), (80, 128), (92, 150)], fill=WITP); d.ellipse([60, 160, 70, 170], fill=ZW)
for (x0, y0, x1, y1) in ((170, 340, 120, 440), (215, 345, 200, 455), (330, 340, 400, 430), (365, 335, 455, 400)):   # benen
    d.line([x0, y0, x1, y1], fill=WITP, width=22); d.ellipse([x1 - 13, y1 - 9, x1 + 13, y1 + 11], fill=ZW)
d.line([390, 280, 470, 330, 485, 380], fill=WITP, width=16)                                                   # staart
# dekkleed: rood-wit verticaal gestreept tot over de benen
for k in range(10):
    x = 140 + k * 26; d.polygon([(x, 245), (x + 26, 244), (x + 30, 385), (x + 4, 386)], fill=RO if k % 2 else WITP)
d.polygon([(140, 245), (400, 240), (400, 250), (140, 256)], fill=(200, 160, 60, 255))                         # gouden rand
# ruiter
d.polygon([(235, 120), (300, 120), (310, 240), (225, 240)], fill=RO)                                          # tuniek
d.rectangle([248, 120, 286, 240], fill=WITP)
d.ellipse([240, 60, 296, 122], fill=GRIJS); d.rectangle([248, 88, 290, 96], fill=ZW)                         # helm met vizier
d.polygon([(268, 60), (300, 20), (320, 30), (282, 66)], fill=RO)                                              # pluim
d.line([300, 150, 40, 60], fill=(120, 80, 40, 255), width=9); d.polygon([(40, 60), (10, 48), (36, 72)], fill=GRIJS)   # lans
d.line([300, 255, 300, 300], fill=ZW, width=12)                                                               # been
r.save(os.path.join(D, "MK_ruiter_kleur.png"))
print("atlassen klaar")
