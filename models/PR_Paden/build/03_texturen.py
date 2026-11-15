"""03_texturen (asfalt en rand: CC0 ambientCG Ground091/Ground076, zie textures/ambientcg/BRON.txt): naadloze PBR-texturen voor de paden, per steen opgebouwd (hoogteveld per steen -> normal map), kleuren uit de
referentiefoto (Kabouterdorp_pad.jpg: grijze klinkers, halfsteens, rijen haaks op het pad; joints donker zand).
Uit: textures/PD_<mat>_kleur.png, _normaal.png, _ruw.png (1024 px; rand heeft alfa)."""
import os, numpy as np
from PIL import Image
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(D, 'textures'); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(1952)


def ruis(shape, schaal, seed):
    """Periodieke ruis (FFT), 0..1, kenmerkende golflengte schaal (px)."""
    r = np.random.default_rng(seed); h, w = shape
    f = np.fft.fft2(r.standard_normal(shape))
    fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.fftfreq(w)[None, :]; k = np.sqrt(fx ** 2 + fy ** 2) * schaal
    n = np.real(np.fft.ifft2(f * np.exp(-k ** 2 * 2) * (k > 0)))
    return (n - n.min()) / (n.max() - n.min() + 1e-9)


def h2n(H, sterkte):
    gx = (np.roll(H, -1, 1) - np.roll(H, 1, 1)) * sterkte; gy = (np.roll(H, -1, 0) - np.roll(H, 1, 0)) * sterkte
    n = np.dstack([-gx, gy, np.ones_like(H)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    return ((n * 0.5 + 0.5) * 255).astype(np.uint8)


def opslaan(naam, kleur, H, ruw, sterkte, alfa=None):
    k = np.clip(kleur, 0, 255).astype(np.uint8)
    if alfa is not None: k = np.dstack([k, np.clip(alfa * 255, 0, 255).astype(np.uint8)])
    Image.fromarray(k).save(os.path.join(OUT, f'PD_{naam}_kleur.png'))
    Image.fromarray(h2n(H, sterkte)).save(os.path.join(OUT, f'PD_{naam}_normaal.png'))
    Image.fromarray(np.clip(ruw * 255, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f'PD_{naam}_ruw.png'))


def hashrand(a, b, seed):
    x = (a * 73856093) ^ (b * 19349663) ^ (seed * 83492791)
    return ((int(x) * 2654435761) % 4294967296) / 4294967296.0


def stenen(Wpx, Hpx, per_x, per_y, rij_h, steen_l, voeg, afr, palet, seed, bol=0.6, onregelmatig=0.0):
    """Halfsteensverband: rijen langs y (hoogte rij_h m), stenen langs x (lengte steen_l m). Periode per_x x per_y m."""
    x = (np.arange(Wpx) + 0.5) / Wpx * per_x; y = (np.arange(Hpx) + 0.5) / Hpx * per_y
    X, Y = np.meshgrid(x, y)
    nrij = int(round(per_y / rij_h)); nst = int(round(per_x / steen_l))
    rij = np.floor(Y / rij_h).astype(int) % nrij
    # per rij een eigen verspringing (halfsteens + kleine afwijking), per steen een kleine lengte-afwijking
    versp = np.array([((r % 2) * 0.5 + (hashrand(r, 7, seed) - 0.5) * 0.12 * (1 + onregelmatig * 4)) * steen_l for r in range(nrij)])
    xs = (X + versp[rij]) % per_x
    kol = np.floor(xs / steen_l).astype(int) % nst
    lx = xs - kol * steen_l; ly = Y - np.floor(Y / rij_h) * rij_h
    # steen-ID-afhankelijke maat
    sid_r = rij; sid_k = kol
    rnd = np.vectorize(lambda a, b, s: hashrand(int(a), int(b), s))
    keys = sid_r * 1000 + sid_k
    uk, inv = np.unique(keys, return_inverse=True)
    r1 = np.array([hashrand(k // 1000, k % 1000, seed) for k in uk])[inv].reshape(keys.shape)
    r2 = np.array([hashrand(k // 1000, k % 1000, seed + 1) for k in uk])[inv].reshape(keys.shape)
    r3 = np.array([hashrand(k // 1000, k % 1000, seed + 2) for k in uk])[inv].reshape(keys.shape)
    v = voeg * (1 + (r2 - 0.5) * (0.6 + onregelmatig * 2))
    # afstand tot de steenrand (afgeronde rechthoek)
    dx = np.minimum(lx, steen_l - lx) - v / 2; dy = np.minimum(ly, rij_h - ly) - v / 2
    hoek = np.sqrt(np.clip(afr - dx, 0, None) ** 2 + np.clip(afr - dy, 0, None) ** 2)
    rand = np.where((dx < afr) & (dy < afr), afr - hoek, np.minimum(dx, dy))
    rand = rand + (ruis(X.shape, 24, seed + 3) - 0.5) * afr * 0.9          # afgesleten, onregelmatige randen
    binnen = rand > 0
    H = np.where(binnen, np.clip(rand / afr, 0, 1) ** 0.5 * bol, -0.35)   # voeg duidelijk dieper dan de steen
    H += binnen * ((r1 - 0.5) * 0.25 + (lx / steen_l - 0.5) * (r3 - 0.5) * 0.3)   # scheve stenen
    H += ruis(X.shape, 6, seed + 4) * 0.08 * binnen
    # kleur
    pal = np.array(palet, float); ci = np.minimum((r1 * len(pal)).astype(int), len(pal) - 1)
    K = pal[ci] * (0.92 + 0.16 * r3[..., None])
    vlek = ruis(X.shape, 40, seed + 5)[..., None]; K = K * (0.9 + 0.2 * vlek)
    K = K * (0.93 + 0.1 * ruis(X.shape, 4, seed + 6)[..., None])           # korrel
    voegk = np.array([58, 53, 47.0]) * (0.8 + 0.35 * ruis(X.shape, 10, seed + 7)[..., None])   # donker: schaduw in de voeg
    mos = (ruis(X.shape, 30, seed + 8) > 0.72)[..., None] & (~binnen)[..., None]
    voegk = np.where(mos, np.array([72, 86, 50.0]), voegk)
    K = np.where(binnen[..., None], K, voegk)
    # randje van de steen iets donkerder (vuil), midden iets lichter (gesleten)
    K = K * np.where(binnen, 0.62 + 0.38 * np.clip(rand / (afr * 2.2), 0, 1) ** 0.7, 1)[..., None]   # ingebakken AO: steenrand loopt donker de voeg in
    ruw = np.where(binnen, 0.78 + 0.1 * r2 - 0.08 * np.clip(rand / afr, 0, 1), 0.96)
    return K, H, ruw


# klinker: 20 x 6,7 cm, rijen haaks op het pad (y = langs het pad), periode 2 m
PAL_KL = [(128, 124, 122), (138, 133, 130), (118, 114, 113), (150, 145, 140), (165, 158, 150), (104, 100, 100), (132, 118, 108), (142, 136, 136)]
K, H, R = stenen(1024, 1024, 2.0, 2.0, 2.0 / 30, 0.2, 0.006, 0.012, PAL_KL, 11)
opslaan('klinker', K, H, R, 4.0)
# kassei: grijze natuursteen-keien ~16 x 14 cm, onregelmatig, bol, brede zandvoeg
PAL_KS = [(112, 110, 108), (124, 121, 118), (98, 97, 98), (136, 130, 122), (108, 104, 100), (145, 140, 132)]
K, H, R = stenen(1024, 1024, 1.8, 1.8, 0.15, 0.18, 0.016, 0.035, PAL_KS, 21, bol=1.0, onregelmatig=0.6)
opslaan('kassei', K, H, R, 5.0)
# kantsteen: vierkante grijze stenen 20 x 20 cm langs de rand (x = langs de rand, y = 0 buiten .. 1 binnen, 0,22 m)
K, H, R = stenen(1024, 128, 2.0, 0.22, 0.22, 0.2, 0.01, 0.02, [(96, 95, 97), (108, 106, 106), (88, 88, 90), (118, 114, 110)], 31, bol=0.8)
opslaan('kantsteen', K[::-1], H[::-1], R[::-1], 3.5)   # UV v=0 (buitenrand) = onderste rij
# kassei_waaier: grijze kasseien (~10 cm) in waaierverband (bogen), periode 1,2 x 1,2 m (Herautenplein-foto's)
def waaier(Wpx, P, s, voeg, palet, seed):
    x = (np.arange(Wpx) + 0.5) / Wpx * P; X, Y = np.meshgrid(x, x)
    R = P * 0.76; best = np.full(X.shape, -1e9); dist = np.zeros(X.shape); ang = np.zeros(X.shape); cid = np.zeros(X.shape, int)
    k = 0
    for j in range(-2, 5):
        for i in range(-2, 4):
            cx = i * P + (j % 2) * P / 2; cy = j * P / 2
            for ox in (-P, 0, P):
                for oy in (-P, 0, P):
                    dx = X - (cx + ox); dy = Y - (cy + oy); r = np.hypot(dx, dy)
                    ok = (r <= R) & ((cy + oy) > best)
                    best = np.where(ok, cy + oy, best); dist = np.where(ok, r, dist); ang = np.where(ok, np.arctan2(dy, dx), ang)
                    cid = np.where(ok, k * 10 + (j % 2), cid); k += 1
    ring = np.floor(dist / s); fr = dist / s - ring
    sa = s * 0.8; boog = ang * np.maximum(dist, s * 0.5); off = (ring % 2) * 0.5 * sa
    st = np.floor((boog + off) / sa); fa = (boog + off) / sa - st
    keys = (cid * 131 + ring.astype(int) * 7919 + st.astype(int)) % 1000003
    uk, inv = np.unique(keys, return_inverse=True)
    r1 = np.array([hashrand(int(q), 3, seed) for q in uk])[inv].reshape(keys.shape)
    r2 = np.array([hashrand(int(q), 5, seed) for q in uk])[inv].reshape(keys.shape)
    v = voeg * (0.7 + 0.6 * r2)
    dxe = np.minimum(fa, 1 - fa) * sa - v / 2; dye = np.minimum(fr, 1 - fr) * s - v / 2
    rand = np.minimum(dxe, dye) + (ruis(X.shape, 10, seed + 3) - 0.5) * 0.012
    binnen = rand > 0
    H = np.where(binnen, np.clip(rand / 0.03, 0, 1) ** 0.5 * 1.0 + (r1 - 0.5) * 0.25, -0.35)
    pal = np.array(palet, float); ci = np.minimum((r1 * len(pal)).astype(int), len(pal) - 1)
    K = pal[ci] * (0.9 + 0.2 * r2[..., None]) * (0.92 + 0.12 * ruis(X.shape, 5, seed + 6)[..., None])
    voegk = np.array([60, 55, 48.0]) * (0.8 + 0.35 * ruis(X.shape, 10, seed + 7)[..., None])
    K = np.where(binnen[..., None], K * (0.62 + 0.38 * np.clip(rand / 0.025, 0, 1) ** 0.7)[..., None], voegk)
    ruw = np.where(binnen, 0.8 - 0.08 * np.clip(rand / 0.03, 0, 1), 0.96)
    return K, H, ruw
K, H, R = waaier(1024, 1.2, 0.1, 0.012, [(128, 124, 118), (140, 134, 126), (116, 113, 110), (150, 142, 132), (108, 104, 100), (158, 150, 138)], 61)
opslaan('waaier', K, H, R, 4.5)
# roze: roze-rode plein-klinkers (Herautenplein rond), in ringen gelegd via radiale UV; 20 x 10 cm, periode 2 m
K, H, R = stenen(1024, 1024, 2.0, 2.0, 0.1, 0.2, 0.006, 0.012, [(168, 118, 108), (178, 128, 116), (156, 108, 100), (186, 140, 126), (160, 120, 112), (146, 100, 94)], 71, bol=0.7)
opslaan('roze', K, H, R, 3.5)
# plavuis: lichte natuursteen-platen 40 x 40 cm (rond de fontein), periode 2 m
K, H, R = stenen(1024, 1024, 2.0, 2.0, 0.4, 0.4, 0.008, 0.01, [(190, 184, 172), (198, 192, 180), (182, 176, 166), (205, 198, 186)], 81, bol=0.4)
opslaan('plavuis', K, H, R, 2.5)
# asfalt: CC0-scan ambientCG Ground091 (grindachtige toplaag), donkerder en grijsbruin getint
AC = os.path.join(os.path.dirname(os.path.dirname(D)), 'textures', 'ambientcg')
lees = lambda n: np.asarray(Image.open(os.path.join(AC, n)).convert('RGB')).astype(float)
K = lees('Ground091_Color.png') * np.array([0.62, 0.6, 0.58])
nrm = lees('Ground091_NormalGL.png'); ruw = lees('Ground091_Roughness.png')[..., 0] / 255
Image.fromarray(np.clip(K, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'PD_asfalt_kleur.png'))
Image.fromarray(nrm.astype(np.uint8)).save(os.path.join(OUT, 'PD_asfalt_normaal.png'))
Image.fromarray(np.clip(ruw * 255, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'PD_asfalt_ruw.png'))
# rand: CC0-scan ambientCG Ground076 (bosgrond met naalden/blad), x = langs de padrand (2,4 m = 1024 px), y = 0 padkant .. 0,8 m
Wr, Hr = 1024, 340
K = lees('Ground076_Color.png')[:Hr]; K = (K * 0.45 + K.mean(2, keepdims=True) * 0.55) * np.array([0.62, 0.56, 0.52])   # donkerder, minder oranje (foto: donkere bosgrond)
nrm = lees('Ground076_NormalGL.png')[:Hr]; ruw = lees('Ground076_Roughness.png')[:Hr, :, 0] / 255
y = (np.arange(Hr)[:, None].repeat(Wr, 1) + 0.5) / Hr
grens = 0.5 + 0.4 * ruis((Hr, Wr), 40, 54)
alfa = np.clip((grens - y) / 0.3, 0, 1) ** 0.8
alfa = np.where(y < 0.08, 1.0, alfa)
Image.fromarray(np.flipud(np.dstack([np.clip(K, 0, 255), alfa * 255])).astype(np.uint8)).save(os.path.join(OUT, 'PD_rand_kleur.png'))   # UV v=0 (padkant) = onderste rij
Image.fromarray(nrm.astype(np.uint8)).save(os.path.join(OUT, 'PD_rand_normaal.png'))
Image.fromarray(np.clip(ruw * 255, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'PD_rand_ruw.png'))
print('texturen klaar', sorted(os.listdir(OUT)))
