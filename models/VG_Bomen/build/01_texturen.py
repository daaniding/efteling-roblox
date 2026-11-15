"""01_texturen: bladtwijg-kaarten (alfa) en schors per boomsoort, procedureel (geen downloads).
Uit: models/VG_Bomen/textures/VB_<soort>_blad_{kleur,normaal,ruw}.png (1024, alfa in kleur) en VB_<soort>_schors_{kleur,normaal,ruw}.png (512).
Bladkaart = een twijg met blaadjes, getekend van onder (steel) naar boven; de kaart in Blender staat met de steel naar de tak."""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(D, 'textures'); os.makedirs(OUT, exist_ok=True)

SOORTEN = {
    # blad: vorm, lengte (px), breedte, aantal, kleuren (lente/zomer, Sprookjesbos-video mei)
    'beuk':     dict(vorm='ovaal', L=84, B=50, n=190, kl=[(72, 112, 38), (88, 132, 44), (62, 98, 34), (102, 140, 52)], schors=(118, 116, 110), ribbel=0.15),
    'eik':      dict(vorm='eik', L=96, B=56, n=150, kl=[(58, 92, 34), (70, 106, 38), (50, 82, 30), (82, 116, 44)], schors=(92, 84, 74), ribbel=0.9),
    'kastanje': dict(vorm='hand', L=130, B=44, n=11, kl=[(60, 104, 40), (74, 120, 46), (54, 92, 36)], schors=(96, 86, 78), ribbel=0.6),
    'berk':     dict(vorm='driehoek', L=56, B=42, n=260, kl=[(102, 140, 56), (118, 156, 62), (90, 128, 50)], schors=(214, 210, 200), ribbel=0.25),
    'den':      dict(vorm='naald', L=130, B=6, n=900, kl=[(46, 74, 40), (56, 86, 46), (40, 66, 36)], schors=(132, 92, 66), ribbel=0.8),
    'spar':     dict(vorm='sparnaald', L=46, B=5, n=1600, kl=[(30, 58, 34), (38, 68, 40), (26, 50, 30)], schors=(96, 78, 64), ribbel=0.5),
}
rng = np.random.default_rng(1952)


def blad_poly(vorm, L, B):
    t = np.linspace(0, 1, 24)
    if vorm == 'ovaal':
        w = B / 2 * np.sin(np.pi * t) ** 0.8
    elif vorm == 'eik':
        w = B / 2 * (0.55 + 0.45 * np.abs(np.sin(t * np.pi * 4.5))) * np.sin(np.pi * t) ** 0.6
    elif vorm == 'driehoek':
        w = B / 2 * np.minimum(t * 2.2, 1) * (1 - t) ** 0.8 * 1.6
    else:
        w = B / 2 * np.sin(np.pi * t) ** 0.9
    links = [(-wi, -ti * L) for wi, ti in zip(w, t)]; rechts = [(wi, -ti * L) for wi, ti in zip(w[::-1], t[::-1])]
    return links + rechts


def kaart(s, p, N=1024):
    kleur = Image.new('RGBA', (N, N), (0, 0, 0, 0)); hoogte = Image.new('L', (N, N), 0)
    dk = ImageDraw.Draw(kleur); dh = ImageDraw.Draw(hoogte)
    # twijg: hoofdsteel van onder-midden omhoog met zijtwijgjes
    steel = [(N / 2 + 18 * math.sin(i / 7), N - 10 - i * (N - 60) / 40) for i in range(41)]
    sk = tuple(int(c * 0.55) for c in p['schors'])
    dk.line(steel, fill=sk + (255,), width=7 if p['vorm'] in ('den', 'spar', 'naald', 'sparnaald') else 5)
    ankers = []
    nz = 14 if p['vorm'] != 'hand' else 7
    for j in range(nz):
        a = steel[int(5 + j * 34 / nz)]; kant = 1 if j % 2 else -1
        ang = math.radians(90 + kant * (40 + rng.uniform(-10, 15))); ln = rng.uniform(0.28, 0.42) * N * (1 - j / nz * 0.45)
        e = (a[0] + math.cos(ang) * ln * -kant * -1 * kant, a[1] - abs(math.sin(ang)) * ln * 0.55)
        e = (a[0] + kant * ln * 0.85, a[1] - ln * 0.5)
        dk.line([a, e], fill=sk + (255,), width=3)
        ankers += [(a[0] + (e[0] - a[0]) * u, a[1] + (e[1] - a[1]) * u, kant) for u in np.linspace(0.1, 1, 10)]
    ankers += [(x, y, 0) for x, y in steel[6::2]]
    if p['vorm'] == 'hand':   # kastanje: per anker een handvormig blad van 7 vingers
        for (x, y, kant) in ankers[::5]:
            for f in range(7):
                ang = math.radians(-90 + (f - 3) * 26 + rng.uniform(-6, 6)); L = p['L'] * (1 - abs(f - 3) * 0.12)
                pts = [(x + px * math.cos(ang + math.pi / 2) - py * math.sin(ang + math.pi / 2), y + px * math.sin(ang + math.pi / 2) + py * math.cos(ang + math.pi / 2)) for px, py in blad_poly('ovaal', L, p['B'])]
                c = p['kl'][rng.integers(len(p['kl']))]; c = tuple(int(v * rng.uniform(0.85, 1.12)) for v in c)
                dk.polygon(pts, fill=c + (255,)); dh.polygon(pts, fill=int(rng.uniform(120, 220)))
    else:
        for i in range(p['n']):
            x, y, kant = ankers[rng.integers(len(ankers))]
            if p['vorm'] in ('naald', 'sparnaald'):
                ang = math.radians(rng.uniform(0, 360)) if p['vorm'] == 'naald' else math.radians(-90 + kant * 50 + rng.uniform(-35, 35))
                L = p['L'] * rng.uniform(0.7, 1.1)
                e = (x + math.cos(ang) * L, y + math.sin(ang) * L)
                c = p['kl'][rng.integers(len(p['kl']))]; c = tuple(int(v * rng.uniform(0.85, 1.15)) for v in c)
                dk.line([(x, y), e], fill=c + (255,), width=int(p['B'])); dh.line([(x, y), e], fill=int(rng.uniform(140, 230)), width=int(p['B']))
                continue
            ang = math.radians(-90 + kant * rng.uniform(25, 75) + rng.uniform(-20, 20)) if kant else math.radians(rng.uniform(-150, -30))
            L = p['L'] * rng.uniform(0.75, 1.15); B = p['B'] * rng.uniform(0.8, 1.1)
            pts = [(x + px * math.cos(ang + math.pi / 2) - py * math.sin(ang + math.pi / 2), y + px * math.sin(ang + math.pi / 2) + py * math.cos(ang + math.pi / 2)) for px, py in blad_poly(p['vorm'], L, B)]
            c = p['kl'][rng.integers(len(p['kl']))]; c = tuple(int(v * rng.uniform(0.82, 1.15)) for v in c)
            dk.polygon(pts, fill=c + (255,)); dh.polygon(pts, fill=int(rng.uniform(110, 230)))
            # nerf
            mx, my = x + math.cos(ang) * L * 0.85, y + math.sin(ang) * L * 0.85
            dk.line([(x, y), (mx, my)], fill=tuple(int(v * 0.8) for v in c) + (255,), width=2)
    # randschaduw (zelfschaduw tussen de blaadjes) en lichte verloop naar de punt
    a = np.asarray(kleur).astype(float); al = a[..., 3] / 255
    h = np.asarray(hoogte.filter(ImageFilter.GaussianBlur(2))).astype(float) / 255
    ao = 0.72 + 0.28 * h; a[..., :3] *= ao[..., None]
    a[..., 3] = np.where(al > 0.5, 255, 0)   # harde alfa (Roblox AlphaMode Transparency: geen halfdoorzichtige randen)
    kl = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    gy, gx = np.gradient(h * 6); n = np.dstack([-gx, gy, np.ones_like(h)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    nm = Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8))
    ruw = Image.fromarray(np.full((N, N), 200, np.uint8))
    kl.save(os.path.join(OUT, f'VB_{s}_blad_kleur.png')); nm.save(os.path.join(OUT, f'VB_{s}_blad_normaal.png')); ruw.save(os.path.join(OUT, f'VB_{s}_blad_ruw.png'))


def ruis(shape, schaal, seed):
    r = np.random.default_rng(seed); h, w = shape
    f = np.fft.fft2(r.standard_normal(shape)); fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.fftfreq(w)[None, :]
    k = np.sqrt((fx * schaal[0]) ** 2 + (fy * schaal[1]) ** 2)
    n = np.real(np.fft.ifft2(f * np.exp(-k ** 2 * 2) * (k > 0))); return (n - n.min()) / (n.max() - n.min() + 1e-9)


def schors(s, p, N=512):
    # u = rond de stam, v = langs de stam; ribbels in de lengte (eik, den diep; beuk glad; berk wit met donkere banden)
    R1 = ruis((N, N), (6, 40), sum(map(ord, s))); R2 = ruis((N, N), (8, 8), sum(map(ord, s)) + 1)
    H = (1 - p['ribbel']) * R2 + p['ribbel'] * R1
    c = np.array(p['schors'], float)
    K = c * (0.7 + 0.5 * H[..., None])
    if s == 'berk':   # donkere horizontale lenticellen/banden
        band = ruis((N, N), (60, 3), 7) > 0.8
        K = np.where(band[..., None], np.array([40, 38, 36.0]), K)
    if s == 'den':    # bovenstam oranjerood (alleen kleurzweem, v hoog = boven)
        K = K * np.linspace(1.0, 1.15, N)[:, None, None] * np.array([1.05, 0.95, 0.9])
    gy, gx = np.gradient(H * (3 + 6 * p['ribbel'])); n = np.dstack([-gx, gy, np.ones_like(H)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    Image.fromarray(np.clip(K, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f'VB_{s}_schors_kleur.png'))
    Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(OUT, f'VB_{s}_schors_normaal.png'))
    Image.fromarray(np.clip(180 + 60 * H, 0, 255).astype(np.uint8)).save(os.path.join(OUT, f'VB_{s}_schors_ruw.png'))


for s, p in SOORTEN.items():
    kaart(s, p); schors(s, p); print('klaar', s)
