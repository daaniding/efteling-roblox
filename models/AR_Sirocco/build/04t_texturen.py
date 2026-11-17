"""04t_texturen: texturen voor de Sirocco (PIL, 1024 px, naadloos waar ze herhalen). Kleuren naar de foto's
(Sirocco-binnen.jpg, Overzicht_sirocco.jpg, Siro-boot-voor/achter.jpg, Siro-achter-close.jpg, Sirocco-meandering.jpg).
Riet: Poly Haven riet_01 (CC0, textures/polyhaven/riet_01), verkleind naar 1024 en grijzer/verweerd gemaakt.
Schrijft textures/SI_<rol>_kleur.png (+ _normaal waar zinvol).
Gebruik: python3 build/04t_texturen.py"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(D))
T = os.path.join(D, "textures"); os.makedirs(T, exist_ok=True)
N = 1024
rng = np.random.default_rng(2022)


def ruis(n=N, schaal=64, octaven=4, naadloos=True):
    """naadloze waarde-ruis 0..1"""
    out = np.zeros((n, n))
    amp, tot = 1.0, 0
    for o in range(octaven):
        k = max(2, n // (schaal // (2 ** o) or 1))
        g = rng.random((k, k))
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC) if not naadloos else \
            Image.fromarray((np.tile(g, (2, 2)) * 255).astype(np.uint8)).resize((2 * n, 2 * n), Image.BICUBIC).crop((n // 2, n // 2, n // 2 + n, n // 2 + n))
        out += np.asarray(im) / 255 * amp; tot += amp; amp *= 0.5
    return out / tot


def opslaan(arr, naam):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(os.path.join(T, f"SI_{naam}.png"))


def normaal_uit_hoogte(h, sterkte=2.0):
    gy, gx = np.gradient(h)
    nx, ny, nz = -gx * sterkte, -gy * sterkte, np.ones_like(h)
    l = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    return np.dstack([(nx / l + 1) * 127.5, (-ny / l + 1) * 127.5, (nz / l + 1) * 127.5])


# 1 riet: scan, grijzer en verweerd (foto: grijsbruin)
src = Image.open(os.path.join(ROOT, "textures/polyhaven/riet_01/riet_01_diff_2k.jpg")).convert("RGB").resize((N, N), Image.LANCZOS)
a = np.asarray(src).astype(float)
grijs = a.mean(axis=2, keepdims=True)
a = a * 0.45 + grijs * 0.55
a *= np.array([0.95, 0.93, 0.88])
opslaan(a, "riet_kleur")
Image.open(os.path.join(ROOT, "textures/polyhaven/riet_01/riet_01_nor_gl_2k.jpg")).resize((N, N), Image.LANCZOS).save(os.path.join(T, "SI_riet_normaal.png"))

# 2 platform: blauwgroen water met golfkrullen (Overzicht_sirocco.jpg), planaire UV over de hele schijf (14 m)
y, x = np.mgrid[0:N, 0:N] / N * 2 - 1
r = np.sqrt(x ** 2 + y ** 2); h = np.arctan2(y, x)
basis = np.dstack([0.16 + 0.10 * (1 - r), 0.38 + 0.12 * (1 - r), 0.55 + 0.05 * r])
krul = np.zeros_like(r)
for c in range(5):                                         # spiraalkrullen
    cx, cy = rng.uniform(-0.7, 0.7, 2); rr = np.sqrt((x - cx) ** 2 + (y - cy) ** 2); hh = np.arctan2(y - cy, x - cx)
    krul += np.exp(-((np.mod(rr * 14 - hh * 1.2, 2 * np.pi) - np.pi) ** 2) * 3) * np.exp(-rr * 3)
golf = 0.5 + 0.5 * np.sin(r * 38 + np.sin(h * 3) * 1.5 + ruis(schaal=128, octaven=2) * 4)
licht = (krul * 0.35 + golf * 0.12)[..., None]
vlek = ruis(schaal=256, octaven=3)[..., None]
kleur = basis * (0.85 + 0.25 * vlek) + licht * np.array([0.35, 0.45, 0.45])
kleur = np.clip(kleur, 0, 1) * 255
opslaan(kleur, "platform_kleur")

# 3 romp rood en romp hout: planken (u = rondom, v = hoogte), 1 textuur = 2 m rondom
def planken(kleur, donker, n_plank=8, horizontaal=True):
    arr = np.zeros((N, N, 3))
    # nerf: ruis die in de lengte van de plank is uitgerekt (lange strepen), plus wat grove vlekken
    st = rng.random((N, 24)) if horizontaal else rng.random((24, N))
    st = np.asarray(Image.fromarray((st * 255).astype(np.uint8)).resize((N, N), Image.BICUBIC)) / 255
    nerf = 0.7 * st + 0.3 * ruis(schaal=128, octaven=2)
    for i in range(n_plank):
        s0, s1 = int(i * N / n_plank), int((i + 1) * N / n_plank)
        tint = 0.85 + 0.25 * rng.random()
        if horizontaal:
            band = nerf[s0:s1, :]
            vlam = np.sin(np.linspace(0, rng.uniform(8, 20), N)[None, :] + band * 9) * 0.06
            arr[s0:s1, :] = (np.array(kleur) * tint * (0.9 + 0.2 * band[..., None] + vlam[..., None]))
            arr[s0:s0 + 4, :] = np.array(donker)
        else:
            band = nerf[:, s0:s1]
            arr[:, s0:s1] = (np.array(kleur) * tint * (0.9 + 0.2 * band[..., None]))
            arr[:, s0:s0 + 4] = np.array(donker)
    return arr
opslaan(planken((150, 34, 30), (60, 12, 10), 10, horizontaal=False), "romp_kleur")
opslaan(planken((168, 128, 80), (70, 48, 26), 7, horizontaal=True), "romp_hout_kleur")
opslaan(planken((44, 72, 128), (16, 28, 54), 9, horizontaal=False), "romp_blauw_kleur")      # blauw geschilderde planken (Siro-boot-voor.jpg, boot rechts)

# 4 schubben: blauwe vissenschubben met donkere randen (Siro-boot-voor.jpg)
im = Image.new("RGB", (N, N), (40, 80, 150)); d = ImageDraw.Draw(im)
S = 64
for rij in range(-1, N // (S // 2) + 2):
    for kol in range(-1, N // S + 2):
        cx = kol * S + (S // 2 if rij % 2 else 0); cy = rij * S // 2
        d.ellipse([cx - S // 2, cy - S // 2, cx + S // 2, cy + S // 2], fill=(70, 120, 190), outline=(25, 50, 100), width=4)
        d.ellipse([cx - S // 3, cy - S // 2 + 6, cx + S // 3, cy], fill=(110, 160, 215))
im.save(os.path.join(T, "SI_schubben_kleur.png"))

# 5 sierpaneel: blauw met gouden krullen (Siro-achter-close.jpg), u = 0..1 over het paneel, v = 0..1 over de hoogte
im = Image.new("RGB", (N, N), (28, 70, 150)); d = ImageDraw.Draw(im)
for k in range(9):
    cx = int((k + 0.5) * N / 9); cy = int(N * (0.35 + 0.25 * (k % 2)))
    for rr in range(70, 10, -14):
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], start=200 + k * 13, end=520 + k * 13, fill=(214, 168, 60), width=9)
d.rectangle([0, 0, N, 28], fill=(200, 155, 55)); d.rectangle([0, N - 28, N, N], fill=(200, 155, 55))
im = im.filter(ImageFilter.GaussianBlur(1.2)); im.save(os.path.join(T, "SI_sierpaneel_kleur.png"))

# 6 mand: vlechtwerk (rieten schalen)
h = np.zeros((N, N))
yy, xx = np.mgrid[0:N, 0:N]
h += (np.sin(xx / N * 2 * np.pi * 48) * np.sin(yy / N * 2 * np.pi * 24) > 0) * 0.5
h += np.sin(yy / N * 2 * np.pi * 24) * 0.3
kl = np.dstack([196 + h * 30, 168 + h * 25, 112 + h * 15]) * (0.85 + 0.15 * ruis(schaal=64, octaven=2))[..., None]
opslaan(kl, "mand_kleur")

# 7 net: gaas met ruiten, alfa
im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
S = 64
for k in range(-N // S, 2 * N // S):
    d.line([(k * S, 0), (k * S + N, N)], fill=(205, 210, 212, 255), width=6)
    d.line([(k * S + N, 0), (k * S, N)], fill=(205, 210, 212, 255), width=6)
im.save(os.path.join(T, "SI_net_kleur.png"))

# 8 beschot: donker grijsbruin, planken langs (foto: donker dakbeschot)
opslaan(planken((58, 54, 50), (25, 23, 22), 12, horizontaal=True), "beschot_kleur")

# 9 stam: ruw verweerd hout (grijsbruin met lichtere slijtplekken), isotroop voor doosprojectie
n1 = ruis(schaal=64, octaven=5); n2 = ruis(schaal=16, octaven=3)
kl = np.dstack([110 + n1 * 70, 86 + n1 * 55, 62 + n1 * 40]) * (0.8 + 0.3 * n2)[..., None]
opslaan(kl, "stam_kleur")
opslaan(normaal_uit_hoogte(n1 * 6 + n2 * 2, 1.5), "stam_normaal")
print("[04t_texturen] klaar:", sorted(f for f in os.listdir(T) if f.startswith("SI_")))
