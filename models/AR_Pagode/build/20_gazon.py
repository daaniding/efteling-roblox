"""20_gazon: tileable gazontextuur (kleur + normaal) voor het Roblox-terrein rond de Pagode (Daan 17 nov: "het gras moet echt
mooier", "fris lichtgroen"). Procedureel (numpy), naadloos: alles met wrap-around. Schrijft textures/GZ_gazon_kleur.png en
GZ_gazon_normaal.png (1024 px). Gebruik: python3 build/20_gazon.py"""
import numpy as np, os
from PIL import Image
N = 1024; rng = np.random.default_rng(17)
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "textures")


def ruis(schaal, oct=4):
    """naadloze waarderuis: grove rasters opschalen met wrap (bilinear via FFT-vrije interpolatie)."""
    uit = np.zeros((N, N))
    for o in range(oct):
        g = max(2, int(schaal * 2 ** o)); r = rng.random((g, g))
        x = np.arange(N) * g / N; i0 = np.floor(x).astype(int); f = x - i0; f = f * f * (3 - 2 * f); i1 = (i0 + 1) % g
        a = r[i0][:, i0] * (1 - f)[None, :] + r[i0][:, i1] * f[None, :]
        b = r[i1][:, i0] * (1 - f)[None, :] + r[i1][:, i1] * f[None, :]
        uit += (a * (1 - f)[:, None] + b * f[:, None]) * 0.5 ** o
    return (uit - uit.min()) / (uit.max() - uit.min())


hoogte = np.zeros((N, N)); kleur = np.zeros((N, N, 3))
basis = np.array([86, 150, 58]) / 255.0
vlek = ruis(3, 4); fijn = ruis(24, 3)
kleur[:] = basis * (0.86 + 0.22 * vlek[..., None]) * (0.94 + 0.1 * fijn[..., None])
# sprietjes: korte, licht gebogen streepjes in verschillende groentinten, naadloos geplaatst
tinten = np.array([[70, 140, 46], [104, 172, 66], [124, 186, 78], [58, 120, 40], [140, 190, 88], [92, 160, 54]]) / 255.0
for _ in range(110000):
    x, y = rng.random(2) * N; L = rng.uniform(5, 14); hk = rng.normal(-np.pi / 2, 0.55)
    t = tinten[rng.integers(len(tinten))] * rng.uniform(0.9, 1.08); dik = rng.uniform(0.6, 1.3); kr = rng.normal(0, 0.04)
    for s in np.linspace(0, 1, int(L)):
        px, py = int(x + np.cos(hk + kr * s * L) * s * L) % N, int(y + np.sin(hk + kr * s * L) * s * L) % N
        w = 0.55 + 0.45 * s
        kleur[py, px] = kleur[py, px] * (1 - w * 0.85) + t * (w * 0.85)
        hoogte[py, px] = max(hoogte[py, px], s * dik)
        if dik > 1.0:
            qx = (px + 1) % N; kleur[py, qx] = kleur[py, qx] * 0.6 + t * 0.4; hoogte[py, qx] = max(hoogte[py, qx], s * dik * 0.7)
# zacht: kleine onscherpte (wrap) zodat het op afstand niet flikkert
def vervaag(a):
    return (a + np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1)) / 5
kleur = np.stack([vervaag(kleur[..., c]) for c in range(3)], -1) * 0.6 + kleur * 0.4
hoogte = vervaag(hoogte) + 0.25 * vlek
gx = (np.roll(hoogte, -1, 1) - np.roll(hoogte, 1, 1)) * 2.2; gy = (np.roll(hoogte, -1, 0) - np.roll(hoogte, 1, 0)) * 2.2
nrm = np.stack([-gx, gy, np.ones_like(gx)], -1); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
os.makedirs(D, exist_ok=True)
Image.fromarray((np.clip(kleur, 0, 1) * 255).astype(np.uint8)).save(os.path.join(D, "GZ_gazon_kleur.png"))
Image.fromarray(((nrm * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(D, "GZ_gazon_normaal.png"))
# controle: 2x2 tegel naast elkaar (naden zichtbaar?)
k = Image.open(os.path.join(D, "GZ_gazon_kleur.png")); t2 = Image.new("RGB", (2 * N, 2 * N))
for i in range(2):
    for j in range(2): t2.paste(k, (i * N, j * N))
t2.resize((1024, 1024)).save(os.path.join(D, "..", "review", "20_gazon_tegels.png"))
print("[20_gazon] klaar")
