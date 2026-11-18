"""01t_texturen: texturen voor de gevels van Fata Morgana (Fata2013.jpg, Fatamorganaexterieur.jpg): warm beige stucwerk
met verticale vuilstrepen onder de kantelen, lichtere lijsten. Bron CC0: ambientCG Plaster002 (textures/ambientcg).
Schrijft textures/FM_stuc_kleur.png, FM_stuc_normaal.png, FM_lijst_kleur.png (1024, naadloos; 1 textuur = 2,5 m).
Gebruik: python3 build/01t_texturen.py"""
import os
import numpy as np
from PIL import Image

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(D))
T = os.path.join(D, "textures"); os.makedirs(T, exist_ok=True)
N = 1024
rng = np.random.default_rng(1986)


def laad(p): return np.asarray(Image.open(os.path.join(ROOT, "textures", p)).convert("RGB").resize((N, N), Image.LANCZOS)).astype(float) / 255


def opslaan(a, n): Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(os.path.join(T, n + ".png"))


def naadloos(a):
    n = a.shape[0]; b = np.roll(np.roll(a, n // 2, 0), n // 2, 1)
    w = np.clip(np.minimum(np.arange(n), n - 1 - np.arange(n)) / (n / 8), 0, 1)
    m = np.minimum(w[:, None], w[None, :])[..., None] if a.ndim == 3 else np.minimum(w[:, None], w[None, :])
    return a * m + b * (1 - m)


def ruis(schaal, oct=4):
    out = np.zeros((N, N)); amp = 1; tot = 0
    for o in range(oct):
        k = max(2, N // max(1, schaal // 2 ** o)); g = rng.random((k, k))
        im = Image.fromarray((np.tile(g, (2, 2)) * 255).astype(np.uint8)).resize((2 * N, 2 * N), Image.BICUBIC)
        out += amp * np.asarray(im.crop((N // 2, N // 2, N // 2 + N, N // 2 + N))) / 255; tot += amp; amp *= 0.5
    return out / tot


# stuc (2048 px = 9 m, UV-maat in 02_toren): fijne structuur van Poly Haven red_plaster_weathered + yellow_plaster, 3 x 3 herhaald;
# GEEN grote vlekken in de tegel (Daan 18 nov: "elke keer copy paste van hetzelfde ridleltje"): de verwering komt als losse
# overlays (FM_vlek1..4, FM_streep, FM_voet hieronder) die 02/03 willekeurig over de muren verdelen
N2 = 2048
def tegel3(pad):
    a = laad(pad); return np.tile(a, (3, 3, 1))[:N2, :N2] if a.shape[0] * 3 >= N2 else np.tile(a, (3, 3, 1))
def groteruis(schaal, oct=4):
    out = np.zeros((N2, N2)); amp = 1; tot = 0
    for o in range(oct):
        k = max(2, N2 // max(1, schaal // 2 ** o)); g = rng.random((k, k))
        im = Image.fromarray((np.tile(g, (2, 2)) * 255).astype(np.uint8)).resize((2 * N2, 2 * N2), Image.BICUBIC)
        out += amp * np.asarray(im.crop((N2 // 2, N2 // 2, N2 // 2 + N2, N2 // 2 + N2))) / 255; tot += amp; amp *= 0.5
    return out / tot
w = np.asarray(Image.fromarray((tegel3("polyhaven/red_plaster_weathered/red_plaster_weathered_diff_1k.jpg") * 255).astype(np.uint8)).resize((N2, N2))) / 255
y = np.asarray(Image.fromarray((tegel3("polyhaven/yellow_plaster/yellow_plaster_diff_1k.jpg") * 255).astype(np.uint8)).resize((N2, N2))) / 255
lw = w.mean(2, keepdims=True); lw = (lw - lw.mean()) / (lw.std() + 1e-6)
ly = y.mean(2, keepdims=True); ly = (ly - ly.mean()) / (ly.std() + 1e-6)
detail = 0.75 * lw + 0.35 * ly
basis = np.array((0.93, 0.87, 0.76))[None, None, :]
oker = np.array((0.89, 0.80, 0.65))[None, None, :]
g_ = groteruis(700, 4)[..., None]; vlek = np.zeros_like(g_)
st = basis * (1 + 0.045 * (g_ - g_.mean()) / g_.std()) * (1 + 0.05 * detail)
def naadloos2(a):
    n = a.shape[0]; b = np.roll(np.roll(a, n // 2, 0), n // 2, 1)
    ww = np.clip(np.minimum(np.arange(n), n - 1 - np.arange(n)) / (n / 8), 0, 1)
    m = np.minimum(ww[:, None], ww[None, :])[..., None]
    return a * m + b * (1 - m)
opslaan(naadloos2(st), "FM_stuc_kleur")
nm = np.tile(laad("polyhaven/red_plaster_weathered/red_plaster_weathered_nor_gl_1k.jpg"), (3, 3, 1))
nm = np.asarray(Image.fromarray((nm * 255).astype(np.uint8)).resize((N2, N2))) / 255; nm[..., :2] = (nm[..., :2] - 0.5) * 1.1 + 0.5
opslaan(nm, "FM_stuc_normaal")
ws = np.tile(laad("polyhaven/white_stucco/white_stucco_diff_1k.jpg"), (3, 3, 1)); ws = np.asarray(Image.fromarray((ws * 255).astype(np.uint8)).resize((N2, N2))) / 255
lj = (ws.mean(2, keepdims=True) / ws.mean()) * np.array((0.93, 0.88, 0.79))[None, None, :] * (1 + 0.04 * detail) * (1 - 0.1 * vlek * np.array((0.6, 0.9, 1.5))[None, None, :])
opslaan(naadloos2(lj), "FM_lijst_kleur")

# overlays (RGBA, 1024): verweringsvlekken, vuilstrepen onder de kantelen, vochtige voet
M_ = 1024
def blob(seed, schaal):
    r_ = np.random.default_rng(seed); out = np.zeros((M_, M_)); amp = 1; tot = 0
    for o in range(5):
        k = max(2, int(M_ / max(1, schaal / 2 ** o))); g = r_.random((k, k))
        out += amp * np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((M_, M_), Image.BICUBIC)) / 255; tot += amp; amp *= 0.55
    out /= tot
    yy, xx = np.mgrid[0:M_, 0:M_] / M_ - 0.5
    rr = np.clip(np.sqrt((xx * 1.25) ** 2 + (yy * 0.95) ** 2) * 2, 0, 1)
    return 1.7 * out - 1.2 * rr ** 3.2                  # grillig, naar de randen toe weg (geen harde kaartrand)
def rgba(kleur, a):
    img = np.zeros((M_, M_, 4)); img[..., :3] = kleur; img[..., 3] = np.clip(a, 0, 1); return img
for k in range(4):
    b_ = blob(100 + k, 380); d_ = b_ - np.percentile(b_, 70 - k * 4)
    binnen_ = np.clip(d_ * 18, 0, 1); rand_ = np.exp(-(d_ / 0.012) ** 2) * (d_ > -0.03)
    kl = np.zeros((M_, M_, 3)); kl[:] = (0.80, 0.67, 0.47)
    kl = kl * (1 - 0.25 * rand_[..., None]) * (0.92 + 0.16 * blob(200 + k, 90)[..., None])
    a = 0.5 * binnen_ + 0.45 * rand_
    Image.fromarray((np.clip(rgba(kl, a), 0, 1) * 255).astype(np.uint8)).save(os.path.join(T, f"FM_vlek{k + 1}_kleur.png"))
# vuilstrepen: van boven (kantelen) naar beneden uitlopend, grijsbruin
r_ = np.random.default_rng(7); a = np.zeros((M_, M_))
yy = np.linspace(0, 1, M_)[:, None]
for _ in range(26):
    c = r_.uniform(0.05, 0.95) * M_; w = r_.uniform(6, 34); L_ = r_.uniform(0.3, 1.0); s_ = r_.uniform(0.25, 0.7)
    x_ = np.arange(M_)[None, :]
    a += s_ * np.exp(-((x_ - c) / w) ** 2) * np.clip(1 - yy / L_, 0, 1) ** 1.5
a *= (0.7 + 0.6 * blob(300, 60)); a = np.clip(a, 0, 0.75) * np.clip(np.minimum(np.arange(M_), M_ - 1 - np.arange(M_))[None, :] / 80, 0, 1)
Image.fromarray((np.clip(rgba((0.6, 0.52, 0.42), a * 0.6), 0, 1) * 255).astype(np.uint8)).save(os.path.join(T, "FM_streep_kleur.png"))
# vochtige voet: donkere band onderaan met grillige bovenrand (v = 0 onder)
rand_y = 0.45 + 0.25 * (blob(400, 300).mean(0) - 0.2)
ya = np.linspace(1, 0, M_)[:, None]
a = np.clip((rand_y[None, :] - ya) * 6, 0, 1) * (0.55 + 0.3 * blob(401, 80)) * np.clip(np.minimum(np.arange(M_), M_ - 1 - np.arange(M_))[None, :] / 60, 0, 1)
Image.fromarray((np.clip(rgba((0.62, 0.53, 0.42), a * 0.75), 0, 1) * 255).astype(np.uint8)).save(os.path.join(T, "FM_voet_kleur.png"))
print("[01t_texturen] klaar")
