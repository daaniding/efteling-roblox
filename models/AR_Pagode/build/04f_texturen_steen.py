"""04f_texturen_steen: atlas voor losse 3D-stenen (breuksteenmuren, randstenen langs het laantje) - video fmEZsIkqsl8 0:04-0:30.
PG_steen_kleur.png / PG_steen_normaal.png: 4 x 4 tegels van 256 px, elke tegel een andere steenkleur (grijs, grijsbruin, roest,
mauve, donker, beige, grijsgroen) met korrel, vlekken en korstmos. Een steen krijgt in 17_steenwerk een tegel (UV binnen de tegel,
marge 12 px), de zijkanten pakken de donkere tegelrand. Kleuren gemeten op de muur in de video (0:05 schaduw, 0:21 zon).
Gebruik: python3 build/04f_texturen_steen.py  (vanuit models/AR_Pagode)"""
import os
import numpy as np
from PIL import Image, ImageFilter

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(D, 'textures')
N, TG = 1024, 256
PAL = [(112, 106, 98), (138, 118, 98), (92, 90, 88), (150, 124, 110), (128, 96, 76), (70, 66, 62), (166, 154, 136), (104, 106, 90),
       (124, 116, 110), (142, 104, 88), (80, 76, 74), (134, 128, 116), (112, 90, 82), (156, 140, 118), (96, 98, 96), (120, 100, 84)]   # video 0:21-0:24: grijs, bruin, roest, mauve, donker, beige


def ruis(rng, sigma, n=N):
    a = (rng.random((n, n)) * 255).astype(np.uint8)
    return (np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(sigma)), float) - 128) / 128


def main():
    rng = np.random.default_rng(17)
    img = np.zeros((N, N, 3)); h = np.zeros((N, N))
    grof, mid, fijn = ruis(rng, 10), ruis(rng, 3), rng.normal(0, 1, (N, N))
    mos = ruis(rng, 4)
    yy, xx = np.mgrid[0:TG, 0:TG] / TG
    rand = np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy))           # 0 op de tegelrand
    for k in range(16):
        ty, tx = divmod(k, 4); sl = (slice(ty * TG, ty * TG + TG), slice(tx * TG, tx * TG + TG))
        base = np.array(PAL[k], float); base = (base * 0.8 + base.mean() * 0.2 + np.array([6, 0, -6])) * 1.14   # video 0:21 in de zon: licht grijsbeige   # video: vaal grijsbruin, weinig verzadiging
        g = grof[sl] * 3.0 + mid[sl] * 1.5
        laag = np.sin((yy + grof[sl] * 0.08) * rng.uniform(14, 26) * np.pi) * 0.5     # gelaagdheid (platte zandsteen/leisteen)
        kl = base[None, None, :] * (1 + g[..., None] * 0.07 + laag[..., None] * 0.05) + fijn[sl][..., None] * 5
        m = np.clip((mos[sl] - 0.35) * 4, 0, 1)[..., None] * rng.uniform(0.3, 0.8)    # korstmos: vaal grijsgroen
        kl = kl * (1 - m) + np.array([128, 130, 108]) * m
        donker = np.clip(rand / 0.12, 0, 1)[..., None]                                # tegelrand = zijkant van de steen
        kl = kl * (0.55 + 0.45 * donker)
        img[sl] = kl
        h[sl] = g * 0.5 + laag * 0.3 + fijn[sl] * 0.08
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(T, 'PG_steen_kleur.png'))
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 1.2; gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 1.2
    nz = 1 / np.sqrt(gx ** 2 + gy ** 2 + 1)
    Image.fromarray((np.stack([(-gx * nz + 1) / 2, (gy * nz + 1) / 2, (nz + 1) / 2], -1) * 255).astype(np.uint8)).save(os.path.join(T, 'PG_steen_normaal.png'))
    print('[04f] steenatlas klaar')


if __name__ == '__main__':
    main()
