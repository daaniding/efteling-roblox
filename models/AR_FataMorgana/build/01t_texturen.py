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


# stuc (2048 px = 6 m, UV-maat in 02_toren): fijne structuur van Poly Haven red_plaster_weathered + yellow_plaster, 3 x 3 herhaald;
# daaroverheen grote, zachte okerkleurige vlekken met een donker randje zoals de "verouderde" muren op Fata2013.jpg
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
oker = np.array((0.87, 0.77, 0.60))[None, None, :]
g_ = groteruis(1100, 5)[..., None]; d_ = (g_ - g_.mean()) / g_.std() - 0.55
vlek = np.clip(d_ * 4 + 0.5, 0, 1)
rand = np.exp(-(d_ / 0.06) ** 2)
st = basis * (1 - vlek) + oker * vlek
st = st * (1 - 0.06 * rand) * (1 + 0.06 * detail)
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
print("[01t_texturen] klaar")
