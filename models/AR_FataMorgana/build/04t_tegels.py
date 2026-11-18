"""04t_tegels: tegeltexturen voor de minaret (Fmplein1986.jpg, FataVoorplein1993.jpg), 1024 px, naadloos.
  FM_zellige_kleur  : Moors tegelwerk, achtpuntige sterren in turquoise/blauw/wit/groen (1 textuur = 1,2 m)
  FM_zigzag_kleur   : fries: rood met witte en zwarte zigzag, u = langs de band (1 textuur = 1,5 m breed, v = bandhoogte)
  FM_balkon_kleur   : balkonborstwering: wit met blauwe ruitjes en rand
Gebruik: python3 build/04t_tegels.py"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); T = os.path.join(D, "textures")
N = 1024
rng = np.random.default_rng(3)


def ster(d, cx, cy, r, kleur, rand=None):
    pts = []
    for k in range(16):
        a = math.pi * k / 8 + math.pi / 16; rr = r if k % 2 == 0 else r * 0.62
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=kleur, outline=rand)


def ruis_tint(im, s=0.06):
    a = np.asarray(im).astype(float)
    a *= 1 + s * (rng.random((a.shape[0] // 64 + 1, a.shape[1] // 64 + 1)).repeat(64, 0).repeat(64, 1)[:a.shape[0], :a.shape[1], None] - 0.5)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# zellige: raster van 4 x 4 cellen, ster per cel, kruisjes ertussen, witte voegen
im = Image.new("RGB", (N, N), (236, 232, 220)); d = ImageDraw.Draw(im)
c = N // 4
for i in range(5):
    for j in range(5):
        x, y = i * c, j * c
        ster(d, x, y, c * 0.46, (34, 128, 150), (240, 236, 226))
        ster(d, x, y, c * 0.22, (24, 60, 120))
        if i < 4 and j < 4:
            mx, my = x + c / 2, y + c / 2
            d.polygon([(mx, my - c * 0.2), (mx + c * 0.2, my), (mx, my + c * 0.2), (mx - c * 0.2, my)], fill=(52, 140, 92), outline=(240, 236, 226))
            d.ellipse([mx - 10, my - 10, mx + 10, my + 10], fill=(214, 170, 72))
for k in range(0, N, 4):
    pass
im = ruis_tint(im.filter(ImageFilter.GaussianBlur(0.8))); im.save(os.path.join(T, "FM_zellige_kleur.png"))

# zigzag-fries: rood met witte zigzag en zwarte lijntjes boven/onder
im = Image.new("RGB", (N, N // 4), (170, 44, 36)); d = ImageDraw.Draw(im); H = N // 4
d.rectangle([0, 0, N, 18], fill=(30, 26, 26)); d.rectangle([0, H - 18, N, H], fill=(30, 26, 26))
d.rectangle([0, 18, N, 30], fill=(232, 222, 200)); d.rectangle([0, H - 30, N, H - 18], fill=(232, 222, 200))
n = 8; w = N / n
for k in range(n):
    x = k * w
    d.polygon([(x, H - 40), (x + w / 2, 40), (x + w, H - 40), (x + w - 22, H - 40), (x + w / 2, 70), (x + 22, H - 40)], fill=(236, 226, 204))
    d.polygon([(x + w / 2 - 10, H - 40), (x + w / 2, H - 70), (x + w / 2 + 10, H - 40)], fill=(30, 90, 130))
im = ruis_tint(im.filter(ImageFilter.GaussianBlur(0.7))).resize((N, N)); im.save(os.path.join(T, "FM_zigzag_kleur.png"))

# balkon: wit met blauwe ruitjes en blauwe randen
im = Image.new("RGB", (N, N), (238, 236, 228)); d = ImageDraw.Draw(im)
d.rectangle([0, 0, N, 60], fill=(30, 70, 140)); d.rectangle([0, N - 60, N, N], fill=(30, 70, 140))
for i in range(8):
    for j in range(4):
        cx, cy = i * N / 8 + N / 16, 140 + j * (N - 280) / 3
        d.polygon([(cx, cy - 55), (cx + 55, cy), (cx, cy + 55), (cx - 55, cy)], fill=(40, 110, 170), outline=(20, 50, 100), width=4)
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(238, 236, 228))
im = ruis_tint(im.filter(ImageFilter.GaussianBlur(0.8))); im.save(os.path.join(T, "FM_balkon_kleur.png"))
print("[04t_tegels] klaar")

# fries van de buitenwachtrij (FataVoorplein1993.jpg): blauw met wit vlechtwerk van ruiten en achthoeken, rode/witte randjes
im = Image.new("RGB", (N, N), (34, 72, 150)); d = ImageDraw.Draw(im)
d.rectangle([0, 0, N, 70], fill=(180, 52, 40)); d.rectangle([0, 70, N, 100], fill=(236, 232, 220))
d.rectangle([0, N - 100, N, N - 70], fill=(236, 232, 220)); d.rectangle([0, N - 70, N, N], fill=(180, 52, 40))
n = 6; w = N / n; y0, y1 = 100, N - 100; ym = (y0 + y1) / 2; hh = (y1 - y0) / 2
for k in range(n + 1):
    cx = k * w
    d.polygon([(cx, y0 + 30), (cx + w / 2, ym), (cx, y1 - 30), (cx - w / 2, ym)], outline=(236, 236, 240), width=16)
    d.polygon([(cx, y0 + 90), (cx + w / 2 - 60, ym), (cx, y1 - 90), (cx - w / 2 + 60, ym)], fill=(60, 140, 200))
    d.ellipse([cx + w / 2 - 34, ym - 34, cx + w / 2 + 34, ym + 34], fill=(236, 236, 240))
    d.ellipse([cx + w / 2 - 14, ym - 14, cx + w / 2 + 14, ym + 14], fill=(214, 170, 72))
im = ruis_tint(im.filter(ImageFilter.GaussianBlur(0.8))); im.save(os.path.join(T, "FM_fries_kleur.png"))
print("[04t_tegels] fries klaar")
