"""04e_texturen_toko: Toko Pagode, getekend naar video fmEZsIkqsl8 1:02 (ref/video_toko_102.jpg).
  PG_tokorand_kleur.png  : dakrand, creme met rode zigzag tussen twee rode lijnen (u = langs de rand, 1 tegel = 2 m)
  PG_tokopaneel_kleur.png: groen paneel onder de toonbank met witte achtbladige bloem in een wit kader
  PG_parasol_kleur.png   : rode parasolstof met witte krullen (u rond, v van rand naar top)
Gebruik: python3 build/04e_texturen_toko.py"""
import os, math
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); T = os.path.join(D, 'textures')
ROOD = (150, 28, 36); CREME = (236, 228, 210); GROEN = (30, 120, 88); WIT = (240, 238, 228)

def rand():
    W, H = 1024, 256
    im = Image.new('RGB', (W, H), CREME); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 26], fill=ROOD); d.rectangle([0, H - 26, W, H], fill=ROOD)
    d.rectangle([0, 34, W, 40], fill=ROOD); d.rectangle([0, H - 40, W, H - 34], fill=ROOD)
    n = 16; pts = []
    for i in range(n * 2 + 1):
        pts.append((i * W / (n * 2), 80 if i % 2 == 0 else 176))
    d.line(pts, fill=ROOD, width=14, joint='curve')
    pts2 = [(x, y + (24 if y < 128 else -24)) for x, y in pts]
    d.line(pts2, fill=(196, 150, 70), width=5)
    im.save(os.path.join(T, 'PG_tokorand_kleur.png'))

def paneel():
    W = H = 512
    im = Image.new('RGB', (W, H), GROEN); d = ImageDraw.Draw(im)
    d.rectangle([28, 28, W - 28, H - 28], outline=WIT, width=10)
    cx = cy = W / 2
    for k in range(8):
        a = k * math.pi / 4
        x, y = cx + math.cos(a) * 95, cy + math.sin(a) * 95
        d.ellipse([x - 52, y - 52, x + 52, y + 52], fill=WIT)
    d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill=GROEN)
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=WIT)
    im.save(os.path.join(T, 'PG_tokopaneel_kleur.png'))

def parasol():
    W, H = 1024, 512
    im = Image.new('RGB', (W, H), (176, 30, 40)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 30], fill=(150, 22, 32))
    for k in range(8):
        x = (k + 0.5) * W / 8
        for j, r in enumerate((60, 38, 18)):
            d.arc([x - r, 200 - r, x + r, 200 + r], 30 + j * 40, 330 - j * 20, fill=WIT, width=7)
        d.arc([x - 30, 340, x + 30, 400], 180, 360, fill=WIT, width=6)
    im.save(os.path.join(T, 'PG_parasol_kleur.png'))

if __name__ == '__main__':
    rand(); paneel(); parasol(); print('[04e] toko-texturen klaar')
