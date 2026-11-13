"""Atlassen: textures/HG_pannenkoek_kleur.png (2x2 pannenkoeken, rand = buitenring) en textures/HG_snoep_kleur.png (4x4 tegels:
hart, koeken, krakeling, snoepjes, groen hout). Kleuren naar Hghuis-vk.jpeg / Hg_alg_2.jpg."""
import random, math
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
D = "/Users/daaniding/RobloxProjects/efteling-roblox/models/AR_HansGrietje/textures/"
rng = np.random.default_rng(7); random.seed(7)
def noise(n, s, amp):   # zachte ruis n x n
    a = rng.normal(0, 1, (n // s + 2, n // s + 2)); im = Image.fromarray(((a - a.min()) / np.ptp(a) * 255).astype("uint8")).resize((n, n), Image.BICUBIC)
    return (np.asarray(im, dtype=float) / 255 - 0.5) * 2 * amp

# ---- pannenkoeken 1024 (2x2 tegels van 512)
T = 512; A = np.zeros((2 * T, 2 * T, 3))
VAR = [((236, 176, 82), (176, 92, 34)), ((226, 150, 62), (160, 78, 30)), ((240, 192, 100), (190, 110, 44)), ((214, 124, 52), (140, 62, 24))]
yy, xx = np.mgrid[0:T, 0:T]; r = np.hypot(xx - T / 2, yy - T / 2) / (T / 2)
for i, (c0, c1) in enumerate(VAR):
    t = np.clip((r - 0.35) / 0.6, 0, 1) ** 1.6
    img = np.array(c0)[None, None, :] * (1 - t[..., None]) + np.array(c1)[None, None, :] * t[..., None]
    img *= (1 + noise(T, 24, 0.10))[..., None]                       # gebakken vlekken
    img *= (1 + noise(T, 6, 0.05))[..., None]
    sp = rng.random((T, T)) < 0.0007; spi = Image.fromarray((sp * 255).astype("uint8")).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5))
    img *= (1 - np.asarray(spi, dtype=float)[..., None] / 255 * 0.18)   # luchtgaatjes
    hl = np.clip(1 - np.hypot(xx - T * 0.42, yy - T * 0.38) / (T * 0.45), 0, 1) ** 2
    img += hl[..., None] * 18
    ring = np.clip((r - 0.86) / 0.12, 0, 1); img *= (1 - ring * 0.25)[..., None]   # donkere opstaande rand
    A[(i // 2) * T:(i // 2 + 1) * T, (i % 2) * T:(i % 2 + 1) * T] = img
Image.fromarray(np.clip(A, 0, 255).astype("uint8")).save(D + "HG_pannenkoek_kleur.png")

# ---- snoep 1024 (4x4 tegels van 256)
S = 256; B = Image.new("RGB", (4 * S, 4 * S), (240, 236, 226))
def tile(k): return ((k % 4) * S, (k // 4) * S)
def shaded(base, k, spots=None, edge=0.22, glaze=22):
    yy, xx = np.mgrid[0:S, 0:S]; r = np.hypot(xx - S / 2, yy - S / 2) / (S / 2)
    img = np.ones((S, S, 3)) * np.array(base)
    img *= (1 + noise(S, 16, 0.06))[..., None]
    img *= (1 - np.clip((r - 0.78) / 0.22, 0, 1) * edge)[..., None]
    img += (np.clip(1 - np.hypot(xx - S * 0.38, yy - S * 0.34) / (S * 0.35), 0, 1) ** 2)[..., None] * glaze
    if spots:
        col, dens, size = spots; sp = rng.random((S, S)) < dens
        m = np.asarray(Image.fromarray((sp * 255).astype("uint8")).filter(ImageFilter.MaxFilter(size)), dtype=float) / 255
        img = img * (1 - m[..., None]) + np.array(col) * m[..., None]
    B.paste(Image.fromarray(np.clip(img, 0, 255).astype("uint8")), tile(k))
shaded((236, 142, 168), 0, edge=0.18, glaze=34)                                   # 0 hart roze
shaded((214, 166, 78), 1, spots=((176, 120, 50), 0.003, 5), edge=0.3)             # 1 koek goud
shaded((228, 190, 112), 2, spots=((186, 136, 70), 0.003, 5), edge=0.3)            # 2 koek licht
shaded((170, 92, 44), 3, spots=((246, 240, 228), 0.002, 3), edge=0.25, glaze=30)  # 3 krakeling
CANDY = [((150, 214, 176), (230, 120, 150)), ((142, 192, 232), (250, 250, 250)), ((244, 222, 108), (236, 120, 70)), ((242, 160, 194), (250, 244, 236)),
         ((192, 160, 224), (250, 230, 120)), ((242, 160, 88), (250, 240, 220)), ((244, 240, 230), (230, 90, 120)), ((214, 72, 76), (250, 240, 230))]
for j, (c, d) in enumerate(CANDY):   # 4..11 rond snoepje met stip in het midden
    k = 4 + j; shaded(c, k, edge=0.2, glaze=30); dr = ImageDraw.Draw(B); x, y = tile(k)
    dr.ellipse([x + S * 0.36, y + S * 0.36, x + S * 0.64, y + S * 0.64], fill=d)
shaded((64, 98, 94), 12, edge=0.0, glaze=0)                                       # 12 teal verf (balken, biezen)
x0, y0 = tile(13); wood = np.ones((S, S, 3)) * np.array((70, 96, 86))               # 13 groen geverfd hout, verticale planken
wood *= (1 + noise(S, 8, 0.05))[..., None]
for px in range(0, S, S // 4): wood[:, px:px + 3] *= 0.55
B.paste(Image.fromarray(np.clip(wood, 0, 255).astype("uint8")), (x0, y0))
shaded((196, 112, 52), 14, edge=0.15, glaze=10)                                   # 14 oranje bies
shaded((246, 242, 234), 15, edge=0.1, glaze=10)                                   # 15 suikerwit
B.save(D + "HG_snoep_kleur.png"); print("atlassen klaar")
