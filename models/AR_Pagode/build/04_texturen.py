"""04_texturen: eigen (getekende) texturen voor de Pagode-gondel, 1024 px, kleur + hoogte -> normaal.
Kleuren gekozen uit ref/boven.jpg (luchtfoto, zon) en ref/video_zij_station.jpg (video 6:50), als albedo (zonder zon).
Uit: textures/PG_<naam>_kleur.png, PG_<naam>_normaal.png
Gebruik: python3 build/04_texturen.py"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UIT = os.path.join(D, 'textures'); os.makedirs(UIT, exist_ok=True)
N = 1024
rng = np.random.default_rng(1987)

ORANJE = (200, 92, 45); ORANJE_D = (150, 60, 30)
GROEN = (28, 128, 104); ROOD = (176, 38, 36); ROOD_D = (110, 22, 30)
WIT = (236, 232, 222); GOUD = (212, 160, 70); BLAUW = (52, 104, 150); ROZE = (196, 98, 92)


def ruis(sigma, amp):
    r = rng.normal(0, 1, (N, N)).astype(np.float32)
    r = np.asarray(Image.fromarray(((r - r.min()) / np.ptp(r) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sigma))).astype(np.float32)
    return (r / 255 - 0.5) * amp


def opslaan(naam, kleur, hoogte, sterkte=4.0):
    k = np.clip(kleur, 0, 255).astype(np.uint8)
    Image.fromarray(k).save(os.path.join(UIT, f'PG_{naam}_kleur.png'))
    h = hoogte.astype(np.float32)
    gy, gx = np.gradient(h)
    nx, ny, nz = -gx * sterkte, gy * sterkte, np.ones_like(h)          # OpenGL (+Y)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    nrm = np.stack([nx / l, ny / l, nz / l], -1) * 0.5 + 0.5
    Image.fromarray((nrm * 255).astype(np.uint8)).save(os.path.join(UIT, f'PG_{naam}_normaal.png'))



def kanok(d, dh, x, y, hoek, lengte, dikte, kleur, hv, diepte=0, spiegel=1):
    """Thais rankwerk: een spiraalrank met druppelblaadjes, die zelf weer kleinere ranken afsplitst."""
    pts = []
    for i in range(28):
        t = i / 27
        a = hoek + spiegel * t * 3.6
        rr = lengte * (1 - 0.75 * t)
        x += math.cos(a) * rr / 14; y += math.sin(a) * rr / 14
        pts.append((x, y))
        w = max(2, dikte * (1 - 0.8 * t))
        d.ellipse([x - w, y - w, x + w, y + w], fill=kleur); dh.ellipse([x - w, y - w, x + w, y + w], fill=hv)
        if i % 5 == 3:   # blaadje naar buiten
            bl = dikte * 2.6 * (1 - 0.6 * t); ba = a - spiegel * 1.2
            bx, by = x + math.cos(ba) * bl, y + math.sin(ba) * bl
            for j in range(6):
                q = j / 5; r_ = bl * 0.42 * math.sin(math.pi * (0.15 + 0.85 * q))
                px, py = x + (bx - x) * q, y + (by - y) * q
                d.ellipse([px - r_, py - r_, px + r_, py + r_], fill=kleur); dh.ellipse([px - r_, py - r_, px + r_, py + r_], fill=hv - 20)
        if diepte < 2 and i in (9, 17):
            kanok(d, dh, x, y, a + spiegel * 1.9, lengte * 0.45, dikte * 0.6, kleur, hv - 15, diepte + 1, -spiegel)
    return pts

def pannen():
    """Geglazuurde schubpannen (Pagode_1999.jpg / video 6:25): ronde onderkant, 9 x 12 per textuur (= 1.5 x 1.5 m)."""
    k = np.zeros((N, N, 3), np.float32)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    nx, ny = 9, 12
    cw, ch = N / nx, N / ny
    h = np.zeros((N, N), np.float32); kl = np.zeros((N, N, 3), np.float32)
    # teken van boven naar onder; elke rij overlapt de vorige (onderste rij ligt bovenop)
    for r in range(ny + 1):
        off = (r % 2) * 0.5
        u = xx / cw + off; ci = np.floor(u); fu = u - ci - 0.5
        v = (yy - (r - 1) * ch) / ch          # 0..1.6 binnen deze rij
        d2 = (fu / 0.5) ** 2 + ((v - 0.55) / 1.05) ** 2
        schub = (d2 < 1.0) & (v > -0.6) & (v < 1.6)
        hv = np.sqrt(np.clip(1 - d2, 0, 1)) * (0.6 + 0.4 * np.clip(v, 0, 1))
        var = (((ci * 37 + r * 11) % 23) / 23 - 0.5) * 0.25
        glans = np.clip(1 - ((fu + 0.15) ** 2 * 8 + (v - 0.95) ** 2 * 3), 0, 1) * 0.35
        for c in range(3):
            kl[..., c] = np.where(schub, ORANJE[c] * (1 + var) * (0.72 + 0.4 * np.clip(v, 0, 1)) + 255 * glans * 0.5, kl[..., c])
        h = np.where(schub, hv + r * 0.0, h)
    rand = h < 0.05
    kl[rand] = np.array(ORANJE_D) * 0.55
    kl += ruis(1.5, 14)[..., None]
    opslaan('pannen', kl, h + ruis(2, 0.04), 4.0)


def sierveld():
    """Driehoekig gevelveld (video 6:20/6:45, Pagode_1999): rood vlak met goud-oranje kanok-rankwerk, teal kern.
    UV: u = 0..1 over de basis, v = 0 (voet) .. 1 (punt)."""
    img = Image.new('RGB', (N, N), (172, 46, 32)); hgt = Image.new('L', (N, N), 30)
    d = ImageDraw.Draw(img); dh = ImageDraw.Draw(hgt)
    cx = N / 2
    GO, OR = (226, 158, 66), (230, 120, 44)
    for s_ in (-1, 1):   # symmetrisch rankwerk vanuit het midden naar de hoeken
        kanok(d, dh, cx + s_ * 30, N - 150, math.pi / 2 + s_ * 1.2 if s_ < 0 else math.pi / 2 - 1.2, 420, 13, OR, 190, spiegel=-s_)
        kanok(d, dh, cx + s_ * 60, N - 420, -math.pi / 2 + s_ * 0.9 if s_ < 0 else -math.pi / 2 - 0.9, 260, 10, GO, 210, spiegel=s_)
    for r, kl, hv in ((140, GO, 215), (112, (28, 112, 96), 160), (70, OR, 200), (30, GO, 230)):   # druppel in het midden
        d.ellipse([cx - r * 0.72, N - 380 - r, cx + r * 0.72, N - 380 + r * 0.9], fill=kl); dh.ellipse([cx - r * 0.72, N - 380 - r, cx + r * 0.72, N - 380 + r * 0.9], fill=hv)
    d.polygon([(cx, N - 380 - 230), (cx - 50, N - 380 - 120), (cx + 50, N - 380 - 120)], fill=GO); dh.polygon([(cx, N - 380 - 230), (cx - 50, N - 380 - 120), (cx + 50, N - 380 - 120)], fill=220)
    for w, kl, hv in ((30, GO, 235), (12, (120, 30, 24), 20)):   # gouden kader + donkere lijn
        d.line([(0, N - 1), (cx, 0), (N - 1, N - 1)], fill=kl, width=w); dh.line([(0, N - 1), (cx, 0), (N - 1, N - 1)], fill=hv, width=w)
    d.rectangle([0, N - 34, N, N], fill=GO); dh.rectangle([0, N - 34, N, N], fill=230)
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    h = np.asarray(hgt.filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255
    k = np.asarray(img).astype(np.float32) * (0.7 + 0.45 * h[..., None]) + ruis(1, 10)[..., None]
    opslaan('sierveld', k, h, 7.0)


def windveer():
    """Rode windveer (video 6:45 / frame 405): vooral rood, langs de binnenrand een fijne witte krullenrand, goudbies buiten.
    u = langs de veer (herhaalt per 1 m), v = over de breedte (0 = buitenrand, 1 = binnenrand)."""
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    v = yy / N; u = xx / N
    k = np.zeros((N, N, 3), np.float32); k[:] = (168, 30, 30)
    h = np.full((N, N), 0.5, np.float32)
    fu = (u * 6) % 1.0
    krul = (np.abs(v - (0.86 - 0.08 * np.sin(fu * 2 * math.pi))) < 0.045) | (((fu - 0.5) ** 2 + ((v - 0.80) / 1.6) ** 2) < 0.012)
    k[krul] = WIT; h[krul] = 0.85
    k[v > 0.95] = WIT; h[v > 0.95] = 0.8
    k[(v > 0.03) & (v < 0.08)] = GOUD; h[(v > 0.03) & (v < 0.08)] = 0.9
    k += ruis(1, 10)[..., None]
    opslaan('windveer', k, h, 3.0)


def trommel():
    """Een paneel van de 16-hoekige trommel (Pagode-toren-close.jpg): roze vlak met blauw-wit kanok-rankwerk en gouden
    omlijning, blauwe bovenband met gouden ranken. u = 0..1 over een zijvlak, v = 0 (onder) .. 1 (boven)."""
    img = Image.new('RGB', (N, N), ROZE); hg = Image.new('L', (N, N), 50)
    d = ImageDraw.Draw(img); dh = ImageDraw.Draw(hg)
    cx = N / 2
    d.rectangle([0, 0, N, 290], fill=BLAUW); dh.rectangle([0, 0, N, 290], fill=80)
    for s_ in (-1, 1):
        kanok(d, dh, cx, 150, math.pi + 0.3 if s_ < 0 else -0.3, 300, 9, GOUD, 210, spiegel=s_)
    d.rectangle([0, 290, N, 318], fill=GOUD); dh.rectangle([0, 290, N, 318], fill=230)
    WB = (200, 214, 226)
    for s_ in (-1, 1):
        kanok(d, dh, cx + s_ * 20, 380, math.pi / 2 + (0.9 if s_ < 0 else -0.9), 380, 12, BLAUW, 180, spiegel=-s_)
        kanok(d, dh, cx + s_ * 40, 900, -math.pi / 2 + (0.8 if s_ < 0 else -0.8), 300, 10, WB, 190, spiegel=s_)
    for r, kl, hv in ((150, GOUD, 215), (124, BLAUW, 160), (80, WB, 200), (36, GOUD, 230)):
        d.ellipse([cx - r * 0.7, 640 - r, cx + r * 0.7, 640 + r], fill=kl); dh.ellipse([cx - r * 0.7, 640 - r, cx + r * 0.7, 640 + r], fill=hv)
    d.rectangle([0, N - 36, N, N], fill=GOUD); dh.rectangle([0, N - 36, N, N], fill=220)
    d.rectangle([0, 0, 14, N], fill=GOUD); d.rectangle([N - 14, 0, N, N], fill=GOUD)
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    h = np.asarray(hg.filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255
    k = np.asarray(img).astype(np.float32) * (0.75 + 0.35 * h[..., None]) + ruis(1, 8)[..., None]
    opslaan('trommel', k, h, 6.0)


def sierrand():
    """Sierrand rond het platform (video 6:50, foto van onder): wit met rode golf/bloem-band. u herhaalt per 1 m."""
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    u, v = xx / N, yy / N
    k = np.zeros((N, N, 3), np.float32); k[:] = WIT; h = np.full((N, N), 0.5, np.float32)
    golf = 0.5 + 0.18 * np.sin(u * 2 * math.pi * 4)
    band = np.abs(v - golf) < 0.07
    k[band] = (160, 40, 38); h[band] = 0.8
    stip = ((u * 4) % 1 - 0.5) ** 2 + ((v - (1 - golf)) * 1.5) ** 2 < 0.02
    k[stip] = (160, 40, 38)
    for a, b in ((0.0, 0.08), (0.92, 1.0)):
        m = (v >= a) & (v <= b); k[m] = (130, 30, 30); h[m] = 0.3
    k += ruis(1, 8)[..., None]
    opslaan('sierrand', k, h, 2.5)


def kernwand():
    """Rode binnenwand (video 6:45): verticale planken met oranje vlam-sjablonen. u herhaalt per 1.2 m."""
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    u, v = xx / N, yy / N
    k = np.zeros((N, N, 3), np.float32); k[:] = ROOD_D; h = np.full((N, N), 0.5, np.float32)
    naad = ((u * 6) % 1.0) < 0.03
    k[naad] *= 0.6; h[naad] = 0.2
    pu = (u * 6) % 1.0 - 0.5
    for vc in (0.18, 0.36):        # twee rijen vlammetjes bovenaan
        vl = (pu ** 2 * 30 + ((v - vc) / 0.09) ** 2) < 1.0
        k[vl] = (226, 120, 40); h[vl] = 0.7
    k += ruis(1, 6)[..., None]
    opslaan('kernwand', k, h, 2.0)


def arm():
    """Zijvlak van de hefarm (ref/eftepedia/Pagode.jpg): creme, oranje randstrepen, in het midden een rij spitse oranje
    bladmotieven (punt omhoog) met creme hart en rode kern. u = langs de arm (1 textuur = 1.6 m), v = over de breedte."""
    img = Image.new('RGB', (N, N), (234, 224, 204)); hg = Image.new('L', (N, N), 90)
    d = ImageDraw.Draw(img); dh = ImageDraw.Draw(hg)
    OR, RD, CR = (214, 100, 50), (176, 52, 38), (234, 224, 204)
    for y0, y1 in ((60, 120), (904, 964)):
        d.rectangle([0, y0, N, y1], fill=OR); dh.rectangle([0, y0, N, y1], fill=140)
    def blad(cx, cy, L, W, kl, hv):
        pts = []
        for i in range(41):
            t = i / 40 * 2 * math.pi
            x = math.cos(t); y = math.sin(t)
            w = W * (1 - 0.55 * max(0, x)) * abs(y) ** 0.9 * (1 if y >= 0 else -1)
            pts.append((cx + x * L, cy + w))
        d.polygon(pts, fill=kl); dh.polygon(pts, fill=hv)
    # u loopt langs de arm (x in de textuur): blad met de punt naar +u (omhoog langs de arm)
    for cx in (N * 0.25, N * 0.75):
        blad(cx, N / 2, 230, 230, OR, 180)
        blad(cx - 20, N / 2, 150, 150, CR, 120)
        blad(cx - 40, N / 2, 80, 80, RD, 200)
    img = img.filter(ImageFilter.GaussianBlur(1.0))
    h = np.asarray(hg.filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255
    k = np.asarray(img).astype(np.float32) * (0.85 + 0.2 * h[..., None]) + ruis(1.2, 9)[..., None]
    opslaan('arm', k, h, 2.5)


for f in (pannen, sierveld, windveer, trommel, sierrand, kernwand, arm):
    f(); print('textuur', f.__name__)
