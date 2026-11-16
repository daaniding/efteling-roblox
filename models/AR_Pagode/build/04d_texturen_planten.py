"""04d_texturen_planten: getekende plant-texturen voor de omgeving van de Pagode (video fmEZsIkqsl8, Pagode-landing.jpg).
  PG_bamboe_kleur.png  (RGBA, kaart)  : bamboebladeren in waaiers aan dunne twijgjes, transparante achtergrond (video 0:28-0:37)
  PG_blad_kleur.png    (RGBA, kaart)  : loofblad-tak (eik/heester), transparant
  PG_naald_kleur.png   (RGB, tegel)   : dennennaalden in plukjes, voor de bonsai-wolken en de sparren (video 0:20, 5:55)
  PG_haag_kleur.png    (RGB, tegel)   : dichte kleine blaadjes (haag langs de sleuf, Pagode-landing.jpg)
  PG_bloem_kleur.png   (RGB, tegel)   : oranje/gele bloemen tussen groen (bloemenperk, Pagode-landing.jpg)
  PG_schors_kleur.png  (RGB, tegel)   : grijsbruine schors met verticale groeven
Gebruik: python3 build/04d_texturen_planten.py  (vanuit models/AR_Pagode)"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(D, 'textures')
R = random.Random(3)


def jit(c, k=18):
    return tuple(max(0, min(255, v + R.randint(-k, k))) for v in c)


def blad(d, x, y, ang, L, B, kleur, punt=0.5):
    """Lancetvormig blad als polygoon (lengte L, breedte B, richting ang)."""
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for i in range(13):
        t = i / 12; w = B * math.sin(math.pi * t ** punt) * (1 - t) ** 0.3
        pts.append((t * L, w))
    pts += [(t, -w) for t, w in reversed(pts[1:-1])]
    d.polygon([(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts], fill=kleur)


def bamboe():
    W = H = 1024
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(46):
        x0, y0 = R.uniform(80, 940), R.uniform(60, 900)
        ang0 = R.uniform(-2.6, -0.6)
        d.line([(x0, y0), (x0 + 120 * math.cos(ang0), y0 + 120 * math.sin(ang0))], fill=(96, 110, 52, 255), width=4)
        for j in range(R.randint(5, 8)):
            a = math.pi / 2 + R.uniform(-1.1, 1.1)          # bamboebladeren hangen
            blad(d, x0 + R.uniform(-20, 20), y0 + R.uniform(-20, 20), a, R.uniform(110, 170), R.uniform(12, 18),
                 jit((88, 124, 44) if R.random() < 0.6 else (122, 146, 58), 22) + (255,), 0.45)
    im.save(os.path.join(T, 'PG_bamboe_kleur.png'))


def loofblad():
    W = H = 1024
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(48):
        x0, y0 = R.uniform(80, 940), R.uniform(80, 940)
        for j in range(R.randint(8, 14)):
            a = R.uniform(0, 6.28)
            blad(d, x0 + R.uniform(-60, 60), y0 + R.uniform(-60, 60), a, R.uniform(60, 95), R.uniform(22, 32),
                 jit((58, 92, 34) if R.random() < 0.55 else (86, 120, 44), 20) + (255,), 0.8)
    im.save(os.path.join(T, 'PG_blad_kleur.png'))


def tegel(naam, basis, fn, n):
    W = H = 1024
    im = Image.new('RGB', (W, H), basis); d = ImageDraw.Draw(im)
    for _ in range(n):
        x, y = R.uniform(0, W), R.uniform(0, H)
        for ox in (-W, 0, W):
            for oy in (-H, 0, H):
                fn(d, x + ox, y + oy)
    im = im.filter(ImageFilter.GaussianBlur(0.7))
    im.save(os.path.join(T, naam))


def naald(d, x, y):
    c = jit((36, 62, 30) if R.random() < 0.6 else (54, 84, 38), 14)
    for j in range(16):
        a = R.uniform(0, 6.28); L = R.uniform(14, 30)
        d.line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], fill=c, width=2)


def haagblad(d, x, y):
    blad(d, x, y, R.uniform(0, 6.28), R.uniform(12, 20), R.uniform(5, 8), jit((52, 86, 30) if R.random() < 0.6 else (78, 110, 40), 18), 0.8)


def bloem(d, x, y):
    if R.random() < 0.45:
        blad(d, x, y, R.uniform(-2.2, -0.9), R.uniform(26, 40), 6, jit((60, 100, 40), 16), 0.6)
    else:
        c = jit(R.choice([(236, 110, 24), (246, 160, 30), (226, 70, 20), (250, 196, 50)]), 14)
        r = R.uniform(7, 12); d.ellipse([x - r, y - r, x + r, y + r], fill=c)
        d.ellipse([x - r * 0.4, y - r * 0.4, x + r * 0.4, y + r * 0.4], fill=jit((180, 60, 10), 10))


def schors(d, x, y):
    c = jit((78, 70, 62), 14)
    d.line([(x, y), (x + R.uniform(-6, 6), y + R.uniform(40, 120))], fill=c, width=R.randint(2, 5))


def breuksteen():
    """Breuksteenmuur (video 0:04-0:30): platte stenen 20-40 x 8-15 cm (textuur = 2 m), bruin/grijs/roestig, diepe donkere voegen.
    Voronoi met platte (horizontaal gerekte) maat, naadloos; normaal uit de hoogte (steen bol, voeg diep)."""
    import numpy as np
    N = 1024; rng = np.random.default_rng(5)
    cols, rows = 6, 18
    pts = []
    for j in range(rows):
        for i in range(cols):
            pts.append(((i + 0.5 + rng.uniform(-0.45, 0.45) + rng.uniform(0, 1) * (j % 2)) / cols, (j + 0.5 + rng.uniform(-0.25, 0.25)) / rows))
    pts = np.array(pts) % 1.0
    yy, xx = np.mgrid[0:N, 0:N] / N
    d1 = np.full((N, N), 9.0); d2 = np.full((N, N), 9.0); idx = np.zeros((N, N), int)
    for k, (px, py) in enumerate(pts):
        dx = np.abs(xx - px); dx = np.minimum(dx, 1 - dx); dy = np.abs(yy - py); dy = np.minimum(dy, 1 - dy)
        d = np.sqrt((dx * 0.36) ** 2 + dy ** 2) * rng.uniform(0.85, 1.15)
        nieuw = d < d1
        d2 = np.where(nieuw, d1, np.minimum(d2, d)); idx = np.where(nieuw, k, idx); d1 = np.where(nieuw, d, d1)
    rand = d2 - d1                                     # afstand tot de voeg
    pal = np.array([(92, 78, 66), (110, 94, 80), (78, 70, 64), (120, 88, 66), (96, 84, 80), (70, 60, 52), (128, 110, 92), (104, 72, 56)], float)
    kl = pal[rng.integers(0, len(pal), len(pts))][idx] * rng.uniform(0.85, 1.12, len(pts))[idx][..., None]
    from PIL import ImageFilter as _F
    vlek = np.asarray(Image.fromarray((rng.random((N, N)) * 255).astype(np.uint8)).filter(_F.GaussianBlur(3)), float)
    ruis = (rng.normal(0, 6, (N, N)) + (vlek - 128) * 0.35)[..., None]
    voeg = np.clip(rand / 0.012, 0, 1)[..., None]
    img = kl * (0.55 + 0.45 * voeg) + ruis
    img = img * voeg + np.array([28, 24, 22]) * (1 - voeg)
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(T, 'PG_breuksteen_kleur.png'))
    h = np.clip(rand / 0.02, 0, 1) + rng.normal(0, 0.03, (N, N))
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 2.5; gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 2.5
    nz = 1 / np.sqrt(gx ** 2 + gy ** 2 + 1)
    nrm = np.stack([(-gx * nz + 1) / 2, (gy * nz + 1) / 2, (nz + 1) / 2], -1) * 255
    Image.fromarray(nrm.astype(np.uint8)).save(os.path.join(T, 'PG_breuksteen_normaal.png'))


def spartak():
    """Platte sparrentak (Douglas, video 6:15-6:30): hoofdtwijg van links (stam) naar rechts, zijtwijgen schuin naar voren,
    korte naalden; transparante achtergrond. u = lengte van de tak."""
    W, H = 1024, 512
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def twijg(x0, y0, ang, L, dikte, diepte):
        x1, y1 = x0 + L * math.cos(ang), y0 + L * math.sin(ang)
        d.line([(x0, y0), (x1, y1)], fill=(70, 58, 40, 255), width=dikte)
        n = int(L / 5)
        for i in range(n):
            t = i / n; px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for s in (-1, 1):
                a = ang + s * R.uniform(0.7, 1.1); ln = R.uniform(9, 15) * (1 - 0.5 * t)
                d.line([(px, py), (px + ln * math.cos(a), py + ln * math.sin(a))], fill=jit((34, 64, 30) if R.random() < 0.6 else (52, 86, 38), 12) + (255,), width=2)
        if diepte:
            for i in range(1, 9):
                t = i / 9.5; px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                for s in (-1, 1):
                    twijg(px, py, ang + s * R.uniform(0.6, 0.9), L * (1 - t) * R.uniform(0.35, 0.5), max(1, dikte - 2), diepte - 1)
    twijg(10, H / 2, 0.0, W - 30, 6, 2)
    im.save(os.path.join(T, 'PG_spar_kleur.png'))


if __name__ == '__main__':
    spartak(); breuksteen(); bamboe(); loofblad()
    tegel('PG_naald_kleur.png', (30, 50, 26), naald, 2600)
    tegel('PG_haag_kleur.png', (34, 58, 22), haagblad, 9000)
    tegel('PG_bloem_kleur.png', (44, 72, 30), bloem, 5000)
    tegel('PG_schors_kleur.png', (58, 52, 46), schors, 2200)
    print('[04d] plant-texturen klaar')
