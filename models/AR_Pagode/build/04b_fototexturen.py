"""04b_fototexturen: sierpanelen uit echte beelden (Daan 16 nov: "uit echte foto's"), rechtgetrokken naar de UV van het model.
- sierveld: video fmEZsIkqsl8 (Eftelwesley, "Ontdek de Efteling - Pagode") op 6:45 (frame 405, 1920x1080), middelste gevel recht
  van voren; driehoek (voet links, voet rechts, punt) -> textuur (0,1), (1,1), (0.5,0).
- trommel: ref/eftepedia/Pagode-toren-close.jpg (3024x1690), middelste paneel van de achthoekige trommel (vierhoek).
- pannen: getekend ruitrooster (video 6:45: oranje ruiten met dunne lichte voegen).
Bronnen staan in ../BRON.txt. Uit: textures/PG_sierveld_*, PG_trommel_*, PG_pannen_* (overschrijft de getekende versies).
Gebruik: python3 build/04b_fototexturen.py <pad naar videoframe 405>"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter, ImageOps

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(D, 'textures'); N = 1024


def normaal_uit(kleur, sterkte=3.0, blur=1.5):
    g = np.asarray(ImageOps.grayscale(kleur).filter(ImageFilter.GaussianBlur(blur))).astype(np.float32) / 255
    gy, gx = np.gradient(g)
    nx, ny, nz = -gx * sterkte * 10, gy * sterkte * 10, np.ones_like(g)
    l = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    return Image.fromarray(((np.stack([nx / l, ny / l, nz / l], -1) * 0.5 + 0.5) * 255).astype(np.uint8))


def perspectief(bron, quad, maat):
    """quad = 4 punten in de bron (linksboven, rechtsboven, rechtsonder, linksonder) -> rechthoek maat."""
    W, H = maat
    dst = [(0, 0), (W, 0), (W, H), (0, H)]
    A, B = [], []
    for (x, y), (u, v) in zip(quad, dst):
        A.append([u, v, 1, 0, 0, 0, -x * u, -x * v]); B.append(x)
        A.append([0, 0, 0, u, v, 1, -y * u, -y * v]); B.append(y)
    c = np.linalg.solve(np.array(A, float), np.array(B, float))
    return bron.transform((W, H), Image.PERSPECTIVE, tuple(c), Image.BICUBIC)


def affien_driehoek(bron, tri, maat):
    """tri = (voet links, voet rechts, punt) in de bron -> textuur met voet onderaan en punt bovenmidden."""
    W, H = maat
    dst = [(0, H), (W, H), (W / 2, 0)]
    A, B = [], []
    for (x, y), (u, v) in zip(tri, dst):
        A.append([u, v, 1, 0, 0, 0]); B.append(x)
        A.append([0, 0, 0, u, v, 1]); B.append(y)
    c = np.linalg.solve(np.array(A, float), np.array(B, float))
    return bron.transform((W, H), Image.AFFINE, tuple(c), Image.BICUBIC)


def ophelderen(im, factor):
    a = np.asarray(im).astype(np.float32) * factor
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


frame = Image.open(sys.argv[1]).convert('RGB')
# sierveld: gemeten op frame 405 (1920 breed): voet links (504,284), voet rechts (883,284), punt (693,29)
sv = affien_driehoek(frame, [(504, 284), (883, 284), (693, 29)], (N, N))
sv = ophelderen(sv, 1.10)                              # video licht onderbelicht in de schaduw van de goot
sv.save(os.path.join(T, 'PG_sierveld_kleur.png')); normaal_uit(sv, 3.0).save(os.path.join(T, 'PG_sierveld_normaal.png'))

# trommel: Pagode-toren-close.jpg, middelste paneel: LB (1285,273) RB (1928,273) RO (2020,1214) LO (1256,1218)
tr_bron = Image.open(os.path.join(D, 'ref', 'eftepedia', 'Pagode-toren-close.jpg')).convert('RGB')
tr = perspectief(tr_bron, [(1285, 273), (1928, 273), (2020, 1214), (1256, 1218)], (N, N))
tr = ophelderen(tr, 1.25)                              # bewolkte, donkere foto
tr.save(os.path.join(T, 'PG_trommel_kleur.png')); normaal_uit(tr, 3.0).save(os.path.join(T, 'PG_trommel_normaal.png'))

# pannen: ruitrooster, 10 x 10 ruiten per textuur (1.5 m), oranje met lichte voegen en lichte glazuurvariatie
yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
u = (xx + yy) / N * 10; v = (xx - yy) / N * 10
fu, fv = u - np.floor(u), v - np.floor(v)
voeg = (np.minimum(fu, 1 - fu) < 0.045) | (np.minimum(fv, 1 - fv) < 0.045)
rng = np.random.default_rng(3)
var = rng.normal(0, 1, (64, 64)).astype(np.float32)
idx = ((np.floor(u) * 7 + np.floor(v) * 13) % 64).astype(int)
vv = var[idx, (np.floor(v) % 64).astype(int)] * 0.06
glans = np.exp(-((fu - 0.35) ** 2 + (fv - 0.35) ** 2) * 18) * 0.18
k = np.zeros((N, N, 3), np.float32)
basis = np.array([226, 92, 28], np.float32)   # verzadigd oranje (luchtfoto)
for c in range(3):
    k[..., c] = basis[c] * (1 + vv) * (0.92 + 0.12 * (fu + fv) / 2) + 255 * glans
k[voeg] = (226, 170, 140)
k = np.clip(k, 0, 255).astype(np.uint8)
im = Image.fromarray(k)
im.save(os.path.join(T, 'PG_pannen_kleur.png'))
h = np.where(voeg, 0.0, 0.6 + 0.4 * np.minimum(np.minimum(fu, 1 - fu), np.minimum(fv, 1 - fv)) * 4).astype(np.float32)
gy, gx = np.gradient(h); l = np.sqrt((gx * 6) ** 2 + (gy * 6) ** 2 + 1)
Image.fromarray(((np.stack([-gx * 6 / l, gy * 6 / l, 1 / l], -1) * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(T, 'PG_pannen_normaal.png'))
print('fototexturen klaar')
