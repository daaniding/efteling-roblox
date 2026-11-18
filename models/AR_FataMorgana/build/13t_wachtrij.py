"""13t_wachtrij: texturen voor de overdekte wachtrijhal (foto wachtrij van Daan, 18 nov; POV-video 2025).
  FM_vloertegel_kleur : vloer: dambord van terracotta en lichte oker tegels (0,25 m) met voegen en kleurverschil per tegel,
                        naadloos, 1 textuur = 2 m
  FM_schildering_kleur: eigen (niet nagemaakte) pastelschildering voor de wandpanelen: woestijn met duinen, palmen en een
                        koepelstad in de verte; geen kopie van de Efteling-schilderingen
Gebruik: python3 build/13t_wachtrij.py"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); T = os.path.join(D, "textures")
rng = np.random.default_rng(13)


def vloer(N=1024, n=8):
    t = N // n
    im = np.zeros((N, N, 3), np.float32)
    a, b = np.array((158, 78, 60)), np.array((196, 146, 112))
    for i in range(n):
        for j in range(n):
            c = (a if (i + j) % 2 == 0 else b) * (0.9 + 0.16 * rng.random()) + rng.normal(0, 4, 3)
            im[i * t:(i + 1) * t, j * t:(j + 1) * t] = c
    im += rng.normal(0, 7, (N, N, 1))                               # korrel
    g = np.zeros((N, N), bool)                                       # voegen
    for k in range(n + 1):
        for d in range(-3, 4):
            g[(k * t + d) % N, :] = True; g[:, (k * t + d) % N] = True
    im[g] = (120, 104, 90)
    out = Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    out.save(os.path.join(T, "FM_vloertegel_kleur.png"))


def schildering(W=512, H=640):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):                                               # lucht: warm pastel naar lichtblauw
        f = y / H
        d.line([(0, y), (W, y)], fill=(int(150 + 90 * f), int(190 + 30 * f), int(215 - 40 * f)))
    for k, (yb, kl) in enumerate(((0.62, (232, 206, 160)), (0.72, (218, 182, 132)), (0.84, (204, 160, 112)))):
        pts = [(0, H)] + [(x, H * yb + 18 * math.sin(x / W * math.pi * (2 + k) + k)) for x in range(0, W + 1, 8)] + [(W, H)]
        d.polygon(pts, fill=kl)
    # koepelstad in de verte
    for cx, w, h in ((150, 46, 40), (210, 30, 60), (260, 60, 34), (330, 36, 50)):
        y0 = H * 0.62
        d.rectangle([cx - w // 2, y0 - h, cx + w // 2, y0 + 4], fill=(236, 226, 206))
        d.ellipse([cx - w // 2, y0 - h - w // 2, cx + w // 2, y0 - h + w // 2], fill=(120, 170, 190))
    d.rectangle([380, H * 0.62 - 120, 392, H * 0.62 + 4], fill=(236, 226, 206))
    d.ellipse([376, H * 0.62 - 134, 396, H * 0.62 - 114], fill=(120, 170, 190))
    # palmen op de voorgrond
    for px, py, s in ((90, H * 0.86, 1.0), (430, H * 0.9, 0.8)):
        d.line([(px, py), (px + 14 * s, py - 190 * s)], fill=(110, 80, 52), width=int(10 * s))
        tx, ty = px + 14 * s, py - 190 * s
        for a in range(0, 360, 40):
            r = math.radians(a)
            d.line([(tx, ty), (tx + 70 * s * math.cos(r), ty + 30 * s * math.sin(r) + 20 * s)], fill=(70, 120, 70), width=int(9 * s))
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    a = np.asarray(im).astype(np.float32) + rng.normal(0, 5, (H, W, 1))  # schilderkorrel
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(T, "FM_schildering_kleur.png"))


vloer(); schildering(); print("[13t_wachtrij] klaar")
