"""07t_bord: atlas voor het ingangsbord van de Sirocco (videoframes xloCDJYf-Tw 12-16 s: pluimvormig cremekleurig bord met
"Sirocco" in blauw, goudbruine rand, rond gouden medaillon met schip eronder, infobord op de paal met spitsboog en pictogrammen).
Indeling (1024 px): A bord voorkant y 0-320 | B medaillon x 0-256, y 320-576 | C infobord x 256-512, y 320-832.
De omtrek van het bord komt uit 07_omgeving (BORD_OMTREK) zodat rand en tekst precies op de vorm vallen.
Schrijft textures/SI_bord_kleur.png. Gebruik: python3 build/07t_bord.py"""
import os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = 1024
random.seed(7)
# moet gelijk zijn aan 07_omgeving.BORD_OMTREK (u = m vanaf de paal naar links, z = m t.o.v. het bordmidden)
BORD_OMTREK = [(0.12, -0.04), (0.28, -0.12), (0.42, -0.2), (0.6, -0.26), (2.15, -0.28), (2.4, -0.2), (2.52, -0.25), (2.72, -0.12),
               (3.05, 0.0), (2.74, 0.08), (2.58, 0.2), (2.44, 0.15), (2.22, 0.3), (0.62, 0.3), (0.45, 0.24), (0.3, 0.16), (0.12, 0.06)]
U_MAX, Z_MIN, Z_MAX = 3.1, -0.32, 0.34
FONT = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"


def a_px(u, z):
    """bordcoordinaat -> pixel in gebied A (links = west = grote u, zodat de tekst vanaf de zuidkant leesbaar is)"""
    return ((U_MAX - u) / U_MAX * N, (Z_MAX - z) / (Z_MAX - Z_MIN) * 320)


im = Image.new("RGB", (N, N), (60, 40, 30))
d = ImageDraw.Draw(im)
# A: perkament, rand, binnenlijn, tekst
poly = [a_px(u, z) for u, z in BORD_OMTREK]
d.polygon(poly, fill=(226, 210, 172))
for _ in range(9000):                                   # perkamentvlekjes
    x, y = random.uniform(0, N), random.uniform(0, 320); c = random.randint(-14, 8)
    d.point((x, y), fill=(214 + c, 196 + c, 156 + c))
d.line(poly + [poly[0]], fill=(150, 112, 58), width=16)
cx = sum(p[0] for p in poly) / len(poly); cy = sum(p[1] for p in poly) / len(poly)
binnen = [(cx + (x - cx) * 0.93, cy + (y - cy) * 0.80) for x, y in poly]
d.line(binnen + [binnen[0]], fill=(196, 160, 82), width=5)
f = ImageFont.truetype(FONT, 150)
tekst = "Sirocco"
bb = d.textbbox((0, 0), tekst, font=f)
tx, ty = a_px(1.45, 0.0)
d.text((tx - (bb[2] - bb[0]) / 2 + 3, ty - (bb[3] - bb[1]) / 2 - bb[1] + 3), tekst, font=f, fill=(20, 34, 70))      # schaduw
d.text((tx - (bb[2] - bb[0]) / 2, ty - (bb[3] - bb[1]) / 2 - bb[1]), tekst, font=f, fill=(42, 78, 150))
# B: medaillon (goud, cremekleurig vlak, schip met bol zeil)
d.ellipse([8, 328, 248, 568], fill=(196, 150, 60), outline=(120, 86, 30), width=6)
d.ellipse([34, 354, 222, 542], fill=(232, 220, 186), outline=(150, 112, 40), width=4)
d.polygon([(70, 470), (186, 470), (170, 500), (86, 500)], fill=(170, 124, 46))                 # romp
d.line([(128, 470), (128, 392)], fill=(150, 108, 40), width=5)                                   # mast
d.polygon([(132, 396), (176, 458), (132, 458)], fill=(196, 152, 66))                             # zeil
d.polygon([(124, 404), (88, 458), (124, 458)], fill=(186, 140, 56))
d.arc([60, 488, 196, 528], 10, 170, fill=(150, 108, 40), width=4)                                # golf
# C: infobord (donkerbruin kader, cremekleurige spitsboog, pictogrammen)
d.rectangle([256, 320, 512, 832], fill=(70, 46, 34))
d.rectangle([266, 330, 502, 822], outline=(150, 112, 58), width=4)
boog = [(300, 800)] + [(384 + 84 * math.cos(math.radians(a)), 470 - 110 * math.sin(math.radians(a)) ** 0.7) for a in range(180, -1, -10)] + [(468, 800)]
boog = [(300, 800), (300, 470)] + [(384 - 84 * math.cos(math.radians(a)), 470 - 120 * math.sin(math.radians(a))) for a in range(0, 181, 10)] + [(468, 470), (468, 800)]
d.polygon(boog, fill=(232, 216, 178))
d.line([(384, 340), (384, 352)], fill=(196, 160, 82), width=6)
kleuren = [(232, 140, 40), (232, 140, 40), (60, 90, 160), (60, 90, 160), (60, 90, 160), (60, 90, 160), (190, 40, 40), (60, 90, 160)]
for k, kl in enumerate(kleuren):
    x = 350 + (k % 2) * 68; y = 500 + (k // 2) * 70
    d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(250, 246, 236), outline=kl, width=6)
    d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=kl)
im = im.filter(ImageFilter.GaussianBlur(0.6))
im.save(os.path.join(D, "textures", "SI_bord_kleur.png"))
print("[07t_bord] textures/SI_bord_kleur.png")
