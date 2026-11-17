"""23_uniform: medewerkerspak voor de Pagode-medewerker (Daan 17 nov: "geef hem echt een medewerkerspak aan").
Klassieke Roblox-kleding (Shirt + Pants, sjabloon 585 x 559), in de kleuren van de Pagode: donkergroene jas met gouden
knopen en biezen, bordeauxrode kraag, wit overhemd met das, naambadge PAGODE op de borst; broek donker antraciet met
gouden bies langs de buitenkant. Schrijft textures/MW_shirt.png en textures/MW_broek.png (upload als Image).
Gebruik: python3 build/23_uniform.py"""
import os
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 585, 559
GROEN = (22, 84, 64)
GROEN_D = (14, 58, 44)
GOUD = (214, 172, 82)
BORDEAUX = (122, 28, 40)
WIT = (236, 234, 228)
ANTRACIET = (40, 42, 48)
ANTRACIET_D = (30, 31, 36)

# sjabloonvlakken (x0, y0, x1, y1)
TORSO = {"voor": (231, 74, 359, 202), "achter": (427, 74, 555, 202), "links": (165, 74, 229, 202),
         "rechts": (361, 74, 425, 202), "boven": (231, 8, 359, 72), "onder": (231, 204, 359, 268)}
ARM_R = {"voor": (217, 355, 281, 483), "links": (19, 355, 83, 483), "achter": (85, 355, 149, 483),
         "rechts": (151, 355, 215, 483), "boven": (217, 289, 281, 353), "onder": (217, 485, 281, 549)}
ARM_L = {"voor": (308, 355, 372, 483), "links": (374, 355, 438, 483), "achter": (440, 355, 504, 483),
         "rechts": (506, 355, 570, 483), "boven": (308, 289, 372, 353), "onder": (308, 485, 372, 549)}


def stof(d, box, kleur, donker):
    """vlak met lichte keperstructuur (fijne diagonale lijntjes binnen het vlak), geen vlakke kleur"""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=kleur)
    lijn = tuple(int(c * 0.6 + dk * 0.4) for c, dk in zip(kleur, donker))
    for k in range(-(y1 - y0), x1 - x0, 3):
        a = (x0 + max(k, 0), y1 - max(-k, 0))                  # start onderrand of linkerrand
        lengte = min(x1 - a[0], a[1] - y0)
        d.line([a, (a[0] + lengte, a[1] - lengte)], fill=lijn, width=1)


def shirt():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    for box in list(TORSO.values()) + list(ARM_R.values()) + list(ARM_L.values()):
        stof(d, box, GROEN, GROEN_D)
    # voorkant: wit overhemd in een V, bordeaux das, bordeaux reverskraag met gouden bies, gouden knopen, naambadge
    x0, y0, x1, y1 = TORSO["voor"]; mx = (x0 + x1) // 2
    d.polygon([(mx - 26, y0), (mx + 26, y0), (mx, y0 + 62)], fill=WIT)
    d.polygon([(mx - 6, y0 + 6), (mx + 6, y0 + 6), (mx + 8, y0 + 46), (mx, y0 + 58), (mx - 8, y0 + 46)], fill=BORDEAUX)
    d.polygon([(mx - 6, y0), (mx + 6, y0), (mx + 4, y0 + 8), (mx - 4, y0 + 8)], fill=(96, 20, 30))
    for s in (-1, 1):
        rev = [(mx + s * 26, y0), (mx + s * 40, y0), (mx + s * 10, y0 + 70), (mx, y0 + 62)]
        d.polygon(rev, fill=BORDEAUX)
        d.line([(mx + s * 40, y0), (mx + s * 10, y0 + 70)], fill=GOUD, width=2)
    d.line([(mx, y0 + 62), (mx, y1)], fill=GROEN_D, width=2)                   # sluiting
    for k in range(3):
        y = y0 + 76 + k * 17
        d.ellipse([mx + 5, y - 4, mx + 13, y + 4], fill=GOUD, outline=(150, 112, 40))
        d.ellipse([mx - 13, y - 4, mx - 5, y + 4], fill=GOUD, outline=(150, 112, 40))
    d.rectangle([x0, y1 - 10, x1, y1], fill=GROEN_D)                            # onderrand jas
    d.line([(x0, y1 - 10), (x1, y1 - 10)], fill=GOUD, width=2)
    # naambadge links op de borst (vanuit de kijker rechts)
    bx0, by0 = mx + 30, y0 + 34
    d.rounded_rectangle([bx0, by0, bx0 + 30, by0 + 11], radius=2, fill=GOUD, outline=(150, 112, 40))
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", 7)
    except OSError:
        f = ImageFont.load_default()
    d.text((bx0 + 15, by0 + 6), "PAGODE", fill=GROEN_D, font=f, anchor="mm")
    # borstzakje rechts met gouden bies
    d.line([(mx - 52, y0 + 44), (mx - 30, y0 + 44)], fill=GOUD, width=2)
    # achterkant: middennaad, gouden bies onderaan
    x0, y0, x1, y1 = TORSO["achter"]; mx = (x0 + x1) // 2
    d.line([(mx, y0 + 20), (mx, y1)], fill=GROEN_D, width=2)
    d.rectangle([x0, y0, x1, y0 + 8], fill=BORDEAUX)                             # kraag achter
    d.rectangle([x0, y1 - 10, x1, y1], fill=GROEN_D)
    d.line([(x0, y1 - 10), (x1, y1 - 10)], fill=GOUD, width=2)
    for k in ("links", "rechts"):
        x0, y0, x1, y1 = TORSO[k]
        d.rectangle([x0, y1 - 10, x1, y1], fill=GROEN_D); d.line([(x0, y1 - 10), (x1, y1 - 10)], fill=GOUD, width=2)
    x0, y0, x1, y1 = TORSO["boven"]; d.rectangle([x0, y0 + 20, x1, y0 + 30], fill=BORDEAUX)
    # mouwen: gouden manchetband boven de pols (onderkant van de armvlakken), bordeaux omslag
    for arm in (ARM_R, ARM_L):
        for k in ("voor", "links", "achter", "rechts"):
            x0, y0, x1, y1 = arm[k]
            d.rectangle([x0, y1 - 16, x1, y1], fill=BORDEAUX)
            d.line([(x0, y1 - 17), (x1, y1 - 17)], fill=GOUD, width=3)
            d.line([(x0, y1 - 9), (x1, y1 - 9)], fill=GOUD, width=1)
    return im


def broek():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    for box in list(TORSO.values()) + list(ARM_R.values()) + list(ARM_L.values()):
        stof(d, box, ANTRACIET, ANTRACIET_D)
    # riem op de onderste torso (broekband)
    for k in ("voor", "achter", "links", "rechts"):
        x0, y0, x1, y1 = TORSO[k]
        d.rectangle([x0, y0 + 84, x1, y0 + 96], fill=(22, 22, 24))
    x0, y0, x1, y1 = TORSO["voor"]; mx = (x0 + x1) // 2
    d.rectangle([mx - 8, y0 + 84, mx + 8, y0 + 96], outline=GOUD, width=2)        # gesp
    # gouden bies langs de buitenkant van elke pijp, vouw voor
    for arm, buiten in ((ARM_R, "links"), (ARM_L, "rechts")):
        x0, y0, x1, y1 = arm[buiten]; mx = (x0 + x1) // 2
        d.line([(mx, y0), (mx, y1)], fill=GOUD, width=3)
        x0, y0, x1, y1 = arm["voor"]; mx = (x0 + x1) // 2
        d.line([(mx, y0 + 4), (mx, y1)], fill=ANTRACIET_D, width=1)
    return im


if __name__ == "__main__":
    shirt().save(os.path.join(D, "textures", "MW_shirt.png"))
    broek().save(os.path.join(D, "textures", "MW_broek.png"))
    print("[23_uniform] textures/MW_shirt.png, textures/MW_broek.png")
