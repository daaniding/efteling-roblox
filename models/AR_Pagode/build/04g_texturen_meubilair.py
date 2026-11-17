"""04g_texturen_meubilair: textuur voor het controlehuisje (video fmEZsIkqsl8 0:44-0:49).
  PG_huisrand_kleur.png : rode kroonrand met witte bloem-/krulmotieven, gouden stippenrij boven en onder (1 herhaling = 0.6 m).
Gebruik: python3 build/04g_texturen_meubilair.py  (vanuit models/AR_Pagode)"""
import os, math
from PIL import Image, ImageDraw

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(D, 'textures')


def huisrand():
    W, H = 512, 256
    im = Image.new('RGB', (W, H), (150, 24, 30)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 22], fill=(24, 110, 84)); d.rectangle([0, H - 22, W, H], fill=(24, 110, 84))     # groene randlijsten
    for y in (34, H - 34):
        for x in range(8, W, 32): d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(214, 170, 70))            # gouden stippen
    for k in range(2):                                     # twee motieven per herhaling, naadloos (W = 2 x 256)
        cx, cy = 128 + k * 256, H / 2
        for i in range(8):                                 # witte bloem: acht blaadjes
            a = i * math.pi / 4
            px, py = cx + 30 * math.cos(a), cy + 30 * math.sin(a)
            d.ellipse([px - 16, py - 11, px + 16, py + 11], fill=(236, 230, 214))
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(214, 170, 70))
        for s in (-1, 1):                                  # krullen naar de buren
            for j in range(10):
                t = j / 9; x = cx + s * (60 + 60 * t); y = cy + 22 * math.sin(t * math.pi * 1.5) * s
                d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(236, 230, 214))
    im.save(os.path.join(T, 'PG_huisrand_kleur.png'))


if __name__ == '__main__':
    huisrand(); print('[04g] huisrand klaar')
