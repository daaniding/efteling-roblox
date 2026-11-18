"""04t_texturen: texturen voor de Archipel (1024 px, naadloos). Kleuren naar de foto's (Archipel_zonnig_2022, Archi-huisje-close,
Archi-loopbruggen, Archipel-boot, Archipel-alle-huisjes). Bronnen CC0: Poly Haven thatch_roof_angled, bamboo_wall,
weathered_planks; ambientCG Rubber004, Concrete012 (textures/ in de repo-root, zie BRON.txt).
Schrijft textures/AR_<rol>_kleur.png (+ _normaal).
  riet   : vers goudbruin riet, halmen langs v (v = van nok naar dakrand)     bamboe : bamboewand, stengels langs v
  plank  : verweerde planken (lichter, grijsbruin), planken langs v          stam   : geschilde grenen paal, nerf langs v
  beton  : licht beige beton met hier en daar een schelp- of zwemvliesafdruk (lemma), 1 textuur = 3 m
  epdm   : turquoise rubbergranulaat (droog: Archi-huisje-close)
  krul   : spiegel van het achterschip, donkerblauw met gouden krullen en noppen (Archipel_zonnig_2022)
Gebruik: python3 build/04t_texturen.py"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(D))
TX = os.path.join(ROOT, "textures")
T = os.path.join(D, "textures"); os.makedirs(T, exist_ok=True)
N = 1024
rng = np.random.default_rng(2022)


def laad(pad, n=N):
    return np.asarray(Image.open(os.path.join(TX, pad)).convert("RGB").resize((n, n), Image.LANCZOS)).astype(float) / 255.0


def opslaan(a, naam):
    Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(os.path.join(T, naam + ".png"))


def kleurgrade(a, doel, contrast=1.0, licht=1.0):
    """luminantie van a, op doelkleur gezet (behoudt structuur)"""
    l = a.mean(2, keepdims=True); m = l.mean()
    l = (l - m) * contrast + m
    return np.clip(l / m * np.array(doel)[None, None, :] * licht, 0, 1)


def naadloos(a):
    """randen in elkaar laten overlopen (kruisvervaging over 1/8)"""
    n = a.shape[0]; b = np.roll(np.roll(a, n // 2, 0), n // 2, 1)
    w = np.minimum(np.arange(n), n - 1 - np.arange(n)) / (n / 8); w = np.clip(w, 0, 1)
    m = np.minimum(w[:, None], w[None, :])[..., None]
    return a * m + b * (1 - m)


def ruis(n=N, schaal=64, octaven=4):
    out = np.zeros((n, n)); amp = 1.0; tot = 0
    for o in range(octaven):
        k = max(2, n // max(1, schaal // (2 ** o)))
        g = rng.random((k, k))
        im = Image.fromarray((np.tile(g, (2, 2)) * 255).astype(np.uint8)).resize((2 * n, 2 * n), Image.BICUBIC)
        out += amp * np.asarray(im.crop((n // 2, n // 2, n // 2 + n, n // 2 + n))) / 255.0; tot += amp; amp *= 0.5
    return out / tot


def normaal(pad, naam, sterkte=1.0):
    a = laad(pad)
    if sterkte != 1.0:
        a = a.copy(); a[..., :2] = (a[..., :2] - 0.5) * sterkte + 0.5
    opslaan(naadloos(a), naam)


# riet: de bron is grijs en loopt verticaal -> goudbruin; de bovenkant van de textuur = nok
r = laad("polyhaven/thatch_roof_angled/thatch_roof_angled_diff_1k.jpg")
r = kleurgrade(r, (0.74, 0.58, 0.36), contrast=1.35, licht=1.05)
var = ruis(schaal=256)[..., None]; r = r * (0.88 + 0.24 * var)
opslaan(naadloos(r), "AR_riet_kleur"); normaal("polyhaven/thatch_roof_angled/thatch_roof_angled_nor_gl_1k.jpg", "AR_riet_normaal", 1.3)

# bamboe: stengels staan in de bron verticaal; iets lichter en geler (Archi-huisje-close)
b = laad("polyhaven/bamboo_wall/bamboo_wall_diff_1k.jpg")
b = kleurgrade(b, (0.72, 0.56, 0.34), contrast=1.15, licht=1.08)
opslaan(naadloos(b), "AR_bamboe_kleur"); normaal("polyhaven/bamboo_wall/bamboo_wall_nor_gl_1k.jpg", "AR_bamboe_normaal")

# planken: verweerd, lichter grijsbruin (loopbruggen, vlonders, kisten krijgen een tint in Studio)
p = laad("polyhaven/weathered_planks/weathered_planks_diff_1k.jpg")
p = kleurgrade(p, (0.55, 0.45, 0.35), contrast=1.1, licht=1.15)
opslaan(naadloos(p), "AR_plank_kleur"); normaal("polyhaven/weathered_planks/weathered_planks_nor_gl_1k.jpg", "AR_plank_normaal")

# stam: geschilde grenen palen, honingkleurig met nerf langs v en een paar knoesten
x = np.linspace(0, 1, N, endpoint=False)
nerf = ruis(schaal=8, octaven=3)
nerf = np.asarray(Image.fromarray((nerf * 255).astype(np.uint8)).resize((N, N // 16)).resize((N, N), Image.BICUBIC)) / 255.0
lijnen = 0.5 + 0.5 * np.sin(2 * math.pi * (x[None, :] * 22 + nerf * 3.0))
s = np.zeros((N, N, 3)); basis = np.array((0.78, 0.6, 0.38))
s[:] = basis
s *= (0.86 + 0.12 * lijnen[..., None]) * (0.9 + 0.2 * ruis(schaal=128)[..., None])
img = Image.fromarray((np.clip(s, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(img)
for _ in range(7):
    cx, cy, rr = rng.integers(60, N - 60), rng.integers(60, N - 60), rng.integers(10, 22)
    d.ellipse([cx - rr, cy - rr * 1.6, cx + rr, cy + rr * 1.6], fill=(120, 84, 48)); d.ellipse([cx - rr // 3, cy - rr // 2, cx + rr // 3, cy + rr // 2], fill=(84, 56, 32))
img = img.filter(ImageFilter.GaussianBlur(1.2))
opslaan(naadloos(np.asarray(img) / 255.0), "AR_stam_kleur")
hn = 0.5 + 0.5 * np.sin(2 * math.pi * (x[None, :] * 22 + nerf * 3.0))
gx = np.roll(hn, -1, 1) - np.roll(hn, 1, 1)
nm = np.zeros((N, N, 3)); nm[..., 0] = 0.5 - gx * 0.6; nm[..., 1] = 0.5; nm[..., 2] = 1.0
opslaan(nm, "AR_stam_normaal")

# beton: Concrete012, licht beige; tegelt per 3 m (1024 px = 3 m); schelp- en zwemvliesafdrukken (lemma)
c = laad("ambientcg/Concrete012_Color.png")
c = kleurgrade(c, (0.86, 0.79, 0.66), contrast=0.9, licht=1.0)
c = c * (0.94 + 0.12 * ruis(schaal=512, octaven=2)[..., None])
img = Image.fromarray((np.clip(naadloos(c), 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(img)
schaduw = (178, 164, 138)
def schelp(cx, cy, s, hoek):
    for k in range(9):
        a = hoek + (k - 4) * 0.22
        d.line([(cx, cy), (cx + math.cos(a) * s, cy + math.sin(a) * s)], fill=schaduw, width=3)
    d.arc([cx - s, cy - s, cx + s, cy + s], math.degrees(hoek) - 55, math.degrees(hoek) + 55, fill=schaduw, width=4)
def vlies(cx, cy, s, hoek):
    pts = [(-0.25, 0), (0.25, 0), (0.55, 1.0), (0.2, 1.1), (0, 0.95), (-0.2, 1.1), (-0.55, 1.0)]
    ca, sa = math.cos(hoek), math.sin(hoek)
    d.polygon([(cx + s * (u * ca - v * sa), cy + s * (u * sa + v * ca)) for u, v in pts], outline=schaduw, width=4)
    for u in (-0.3, 0, 0.3):
        d.line([(cx, cy), (cx + s * (u * 1.6 * ca - 0.95 * sa), cy + s * (u * 1.6 * sa + 0.95 * ca))], fill=schaduw, width=2)
schelp(260, 300, 46, -1.2); schelp(780, 640, 38, 2.1); vlies(560, 180, 90, 0.4); vlies(620, 260, 90, 0.3); vlies(190, 760, 80, 2.6)
img = img.filter(ImageFilter.GaussianBlur(0.8))
opslaan(np.asarray(img) / 255.0, "AR_beton_kleur"); normaal("ambientcg/Concrete012_NormalGL.png", "AR_beton_normaal", 0.6)

# epdm: rubbergranulaat turquoise
e = laad("ambientcg/Rubber004/Rubber004_1K-JPG_Color.jpg")
e = kleurgrade(e, (0.24, 0.6, 0.6), contrast=1.6, licht=1.0)
opslaan(naadloos(e), "AR_epdm_kleur"); normaal("ambientcg/Rubber004/Rubber004_1K-JPG_NormalGL.jpg", "AR_epdm_normaal", 0.5)

# krul: spiegel van het achterschip (u = breedte, v = hoogte, 1 textuur per paneel): donkerblauw, gouden krullen boven,
# daaronder een band met ruiten en gouden noppen
K = Image.new("RGB", (N, N), (22, 36, 78)); d = ImageDraw.Draw(K)
GOUD, DGOUD = (214, 170, 72), (150, 108, 40)
d.rectangle([0, 0, N, 26], fill=GOUD); d.rectangle([0, 520, N, 548], fill=GOUD); d.rectangle([0, N - 30, N, N], fill=GOUD)
def krul(cx, cy, r0, richting):
    pts = []
    for k in range(120):
        t = k / 119 * 3.4 * math.pi; r = r0 * (1 - t / (3.6 * math.pi))
        pts.append((cx + richting * r * math.cos(t), cy + r * math.sin(t)))
    d.line(pts, fill=GOUD, width=14, joint="curve"); d.line(pts, fill=DGOUD, width=4)
for i in range(4):
    cx = 128 + i * 256
    krul(cx - 52, 200, 70, 1); krul(cx + 52, 200, 70, -1)
    d.line([(cx - 120, 330), (cx, 290), (cx + 120, 330)], fill=GOUD, width=12)
    krul(cx - 60, 400, 50, -1); krul(cx + 60, 400, 50, 1)
for i in range(9):
    for j in range(4):
        cx, cy = i * 128 + (64 if j % 2 else 0), 600 + j * 112
        d.polygon([(cx, cy - 52), (cx + 60, cy), (cx, cy + 52), (cx - 60, cy)], outline=(70, 110, 170), width=6)
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=GOUD, outline=DGOUD, width=3)
K = K.filter(ImageFilter.GaussianBlur(0.7))
k = np.asarray(K) / 255.0 * (0.9 + 0.15 * ruis(schaal=128)[..., None])
opslaan(k, "AR_krul_kleur")
print("[04t_texturen] klaar:", sorted(f for f in os.listdir(T) if f.startswith("AR_")))
