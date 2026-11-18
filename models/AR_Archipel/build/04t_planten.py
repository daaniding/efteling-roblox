"""04t_planten: getekende texturen voor de beplanting en de entree van de Archipel (video 4CKAjMsJHh8 0:00-0:45,
Archipel-na-ingang.jpg, Archipel-doorsnede-entree.jpg). Kaarten zijn RGBA (alfa), onderkant/steel = midden onder.
  AR_palmblad_kleur   : waaierblad van de Chinese waaierpalm (Trachycarpus), steel in het midden onder
  AR_bananenblad_kleur: bananenblad (Musa basjoo), nerf langs v, gescheurde randen; u = breedte, v = lengte
  AR_gember_kleur     : pol siergember/canna: smalle bladeren en rood-oranje bloemaren (lemma: zonsopgangkleuren)
  AR_palmstam_kleur   : stam vol bruine vezels (Poly Haven palm_bark, bruiner gemaakt + vezelstrepen)
  AR_bord_kleur       : ingangsbord "Archipel", donkerblauw met gouden rand en letters, puntige uiteinden (u 0..1 = breedte)
  AR_kaartsteen_kleur : donkere leisteen met ingekraste zeekaart (rots bij de ingang)
Gebruik: python3 build/04t_planten.py"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(D))
T = os.path.join(D, "textures")
R = random.Random(7)


def jit(c, k=16):
    return tuple(max(0, min(255, v + R.randint(-k, k))) for v in c[:3]) + tuple(c[3:])


def palmblad():
    N = 512; im = Image.new("RGBA", (N, N), (60, 90, 40, 0)); d = ImageDraw.Draw(im)
    cx, cy = N / 2, N - 40
    n = 34
    for k in range(n):
        a = math.radians(-172 + 164 * k / (n - 1)) + R.uniform(-0.02, 0.02)
        L = R.uniform(380, 450) * (0.82 + 0.18 * math.sin(math.pi * k / (n - 1)))
        w0, w1 = 9, 5
        ca, sa = math.cos(a), math.sin(a)
        nx, ny = -sa, ca
        p0 = (cx + ca * 30, cy + sa * 30)
        knik = R.uniform(0.7, 0.9)                         # de punt hangt een beetje (gesplitst blad)
        pm = (cx + ca * L * knik, cy + sa * L * knik)
        pe = (pm[0] + math.cos(a + R.uniform(-0.25, 0.25)) * L * (1 - knik), pm[1] + math.sin(a + 0.3) * L * (1 - knik))
        kleur = jit((70, 112, 46, 255), 14)
        d.polygon([(p0[0] + nx * w0 * 0.4, p0[1] + ny * w0 * 0.4), (pm[0] + nx * w0, pm[1] + ny * w0), pe,
                   (pm[0] - nx * w0, pm[1] - ny * w0), (p0[0] - nx * w0 * 0.4, p0[1] - ny * w0 * 0.4)], fill=kleur)
        d.line([p0, pm, pe], fill=jit((96, 134, 64, 255), 10), width=2)
    d.ellipse([cx - 34, cy - 30, cx + 34, cy + 20], fill=(84, 104, 52, 255))
    d.line([(cx, cy), (cx, N)], fill=(88, 96, 50, 255), width=10)
    im = im.filter(ImageFilter.GaussianBlur(0.6)); im.save(os.path.join(T, "AR_palmblad_kleur.png"))


def bananenblad():
    W, H = 256, 1024; im = Image.new("RGBA", (W, H), (80, 140, 50, 0)); d = ImageDraw.Draw(im)
    cx = W / 2
    pts_l, pts_r = [], []
    for k in range(41):
        t = k / 40; y = H - 10 - t * (H - 30)
        w = (W / 2 - 8) * (math.sin(math.pi * min(1, t * 1.05)) ** 0.6) * (1 if t < 0.97 else 0.4)
        pts_l.append((cx - w, y)); pts_r.append((cx + w, y))
    d.polygon(pts_l + pts_r[::-1], fill=(88, 150, 56, 255))
    for k in range(70):                                   # zijnerven
        y = H - 30 - k * 14; t = 1 - y / H
        for zij in (-1, 1):
            d.line([(cx, y), (cx + zij * (W / 2), y - 46)], fill=(108, 170, 70, 255), width=2)
    for k in range(9):                                    # scheuren tot de nerf (wind)
        y = R.uniform(150, H - 120); zij = R.choice((-1, 1))
        d.polygon([(cx + zij * 6, y), (cx + zij * W / 2, y - 30), (cx + zij * W / 2, y - 18)], fill=(0, 0, 0, 0))
    d.line([(cx, H), (cx, 20)], fill=(150, 190, 110, 255), width=7)
    a = np.asarray(im).astype(float)
    sh = np.linspace(0.85, 1.1, W)[None, :, None]; sh = np.where(np.arange(W)[None, :, None] < cx, sh[:, ::-1], sh)
    a[..., :3] *= sh
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); im.save(os.path.join(T, "AR_bananenblad_kleur.png"))


def gember():
    N = 512; im = Image.new("RGBA", (N, N), (60, 110, 50, 0)); d = ImageDraw.Draw(im)
    for k in range(26):                                   # bladeren, schuin omhoog vanuit de voet
        x0 = N / 2 + R.uniform(-70, 70); a = math.radians(R.uniform(-125, -55)); L = R.uniform(260, 430); B = R.uniform(16, 30)
        ca, sa = math.cos(a), math.sin(a); nx, ny = -sa, ca
        pts = []
        for i in range(9):
            t = i / 8; w = B * math.sin(math.pi * t) ** 0.7
            buig = 30 * t * t
            pts.append((x0 + ca * L * t + nx * w + buig * math.copysign(1, ca), N - 4 + sa * L * t + ny * w + buig * 0.6))
        for i in range(8, -1, -1):
            t = i / 8; w = B * math.sin(math.pi * t) ** 0.7; buig = 30 * t * t
            pts.append((x0 + ca * L * t - nx * w + buig * math.copysign(1, ca), N - 4 + sa * L * t - ny * w + buig * 0.6))
        d.polygon(pts, fill=jit((58, 112, 46, 255), 16))
    for k in range(6):                                    # bloemaren rood-oranje (siergember)
        x = N / 2 + R.uniform(-150, 150); y0 = R.uniform(40, 170)
        d.line([(x, N - 120), (x, y0 + 60)], fill=(70, 100, 44, 255), width=5)
        kl = R.choice([(214, 52, 34), (236, 108, 30), (226, 76, 30), (240, 150, 40)])
        for j in range(14):
            y = y0 + j * 7; w = 16 + 8 * math.sin(j / 13 * math.pi)
            d.ellipse([x - w / 2, y, x + w / 2, y + 14], fill=jit(kl + (255,), 14))
    im = im.filter(ImageFilter.GaussianBlur(0.5)); im.save(os.path.join(T, "AR_gember_kleur.png"))


def palmstam():
    a = np.asarray(Image.open(os.path.join(ROOT, "textures/polyhaven/palm_bark/palm_bark_diff_1k.jpg")).convert("RGB").resize((512, 512))).astype(float)
    l = a.mean(2, keepdims=True); a = l / l.mean() * np.array((96, 70, 46))[None, None, :]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    for k in range(900):                                  # losse vezels, schuin hangend
        x, y = R.uniform(0, 512), R.uniform(0, 512); L = R.uniform(10, 34)
        d.line([(x, y), (x + R.uniform(-5, 5), y + L)], fill=jit((70, 50, 32), 18), width=1)
    for y in range(0, 512, 64):                           # bladvoeten in ringen
        d.line([(0, y), (512, y + 6)], fill=(56, 40, 26), width=4)
    im.filter(ImageFilter.GaussianBlur(0.5)).save(os.path.join(T, "AR_palmstam_kleur.png"))


def bord():
    W, H = 1024, 256; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    BLAUW, GOUD = (30, 46, 92, 255), (214, 170, 80, 255)
    vorm = [(40, 40), (930, 40), (960, 20), (1000, 128), (960, 236), (930, 216), (40, 216), (60, 128)]
    d.polygon(vorm, fill=GOUD)
    binnen = [(56, 54), (922, 54), (948, 40), (980, 128), (948, 216), (922, 202), (56, 202), (74, 128)]
    d.polygon(binnen, fill=BLAUW)
    d.line(binnen + [binnen[0]], fill=(150, 116, 52, 255), width=3)
    f = None
    for pad in ("/System/Library/Fonts/Supplemental/Papyrus.ttc", "/System/Library/Fonts/Supplemental/Herculanum.ttf",
                "/System/Library/Fonts/Supplemental/Baskerville.ttc", "/Library/Fonts/Georgia.ttf"):
        if os.path.exists(pad):
            try: f = ImageFont.truetype(pad, 112); break
            except Exception: pass
    tekst = "Archipel"
    bb = d.textbbox((0, 0), tekst, font=f); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((W - tw) / 2 - bb[0], 128 - th / 2 - bb[1]), tekst, font=f, fill=GOUD)
    for x in (110, 880):
        d.ellipse([x - 16, 112, x + 16, 144], outline=GOUD, width=5)
    im.save(os.path.join(T, "AR_bord_kleur.png"))


def kaartsteen():
    N = 512
    a = np.asarray(Image.open(os.path.join(ROOT, "textures/polyhaven/cliff_side/cliff_side_diff_2k.jpg")).convert("RGB").resize((N, N))).astype(float) \
        if os.path.exists(os.path.join(ROOT, "textures/polyhaven/cliff_side/cliff_side_diff_2k.jpg")) else np.full((N, N, 3), 90.0)
    l = a.mean(2, keepdims=True); a = l / l.mean() * np.array((70, 72, 74))[None, None, :]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    LIJN = (150, 150, 140)
    for k in range(5):                                    # eilanden
        cx, cy, r = R.uniform(80, 430), R.uniform(80, 430), R.uniform(30, 70)
        pts = [(cx + r * (0.7 + 0.3 * R.random()) * math.cos(2 * math.pi * i / 14), cy + r * (0.7 + 0.3 * R.random()) * math.sin(2 * math.pi * i / 14)) for i in range(14)]
        d.polygon(pts, outline=LIJN, width=3)
    for k in range(4):
        d.line([(R.uniform(0, 512), R.uniform(0, 512)) for _ in range(5)], fill=LIJN, width=2, joint="curve")
    d.ellipse([360, 360, 470, 470], outline=LIJN, width=3)
    for k in range(8):
        a_ = 2 * math.pi * k / 8; d.line([(415, 415), (415 + 60 * math.cos(a_), 415 + 60 * math.sin(a_))], fill=LIJN, width=2)
    im.filter(ImageFilter.GaussianBlur(0.7)).save(os.path.join(T, "AR_kaartsteen_kleur.png"))


for fn in (palmblad, bananenblad, gember, palmstam, bord, kaartsteen): fn()
print("[04t_planten] klaar")
