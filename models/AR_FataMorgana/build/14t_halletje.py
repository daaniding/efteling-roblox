"""14t_halletje: texturen voor de zijdeur en het halletje in de minaretvoet (POV-video 2025 [4K POV] Fata Morgana, 25-30 s).
  FM_tegelhal_kleur : wandtegels van het halletje: terracotta/roodbruin met een ruitjesrooster van crème kruisjes en donkere
                      stipjes (zoals op de video), naadloos, 1 textuur = 1 m
  FM_deurblad_kleur : houten deurblad (honingkleurig, verticale nerf) met "Open" in crème letters
  FM_balustrade_kleur: balustrade van de gaanderij in de instaphal (video's 2020/2025): crème vlak met een taupe getrapt paneel en
                      een ronde crème rozet met bruin patroon; 1 textuur = 1 paneel (u) x balustradehoogte (v)
Gebruik: python3 build/14t_halletje.py"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); T = os.path.join(D, "textures")
rng = np.random.default_rng(14)


def tegelhal(N=1024, n=8):
    t = N // n
    im = Image.new("RGB", (N, N), (150, 62, 40)); d = ImageDraw.Draw(im)
    for i in range(n + 1):
        for j in range(n + 1):
            cx, cy = i * t, j * t
            # crème ruitje met kruisje op elk knooppunt
            r = t * 0.32
            d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=(232, 210, 178))
            r2 = t * 0.2
            d.polygon([(cx, cy - r2), (cx + r2, cy), (cx, cy + r2), (cx - r2, cy)], fill=(160, 70, 44))
            d.ellipse([cx - t * 0.06, cy - t * 0.06, cx + t * 0.06, cy + t * 0.06], fill=(70, 30, 22))
            # klein crème kruisje midden in elk vak
            mx, my = cx + t / 2, cy + t / 2; k = t * 0.12
            d.line([(mx - k, my), (mx + k, my)], fill=(226, 196, 160), width=max(2, t // 22))
            d.line([(mx, my - k), (mx, my + k)], fill=(226, 196, 160), width=max(2, t // 22))
    a = np.asarray(im).astype(np.float32) + rng.normal(0, 6, (N, N, 1))
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)).save(os.path.join(T, "FM_tegelhal_kleur.png"))


def deurblad(W=512, H=1024):
    x = np.linspace(0, 1, W)[None, :]; y = np.linspace(0, 1, H)[:, None]
    nerf = np.sin(x * 90 + np.sin(y * 7) * 2.0 + rng.normal(0, 0.15, (1, W)) * 3) * 0.5 + 0.5
    basis = np.array((190, 128, 62), np.float32)
    a = basis[None, None, :] * (0.86 + 0.16 * nerf[..., None]) + rng.normal(0, 4, (H, W, 1))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", 120)
    txt = "Open"; w = d.textlength(txt, font=f)
    laag = Image.new("RGBA", (int(w) + 20, 160), (0, 0, 0, 0)); dl = ImageDraw.Draw(laag)
    dl.text((10, 0), txt, font=f, fill=(246, 236, 214, 255))
    laag = laag.rotate(-12, expand=True)
    im.paste(laag, (int((W - laag.width) / 2), int(H * 0.22)), laag)
    im.save(os.path.join(T, "FM_deurblad_kleur.png"))


def balustrade(W=768, H=432):
    im = Image.new("RGB", (W, H), (232, 222, 200)); d = ImageDraw.Draw(im)
    m = 34; st = 22                                                    # rand, trapje
    pts = [(m + st, m), (W - m - st, m), (W - m - st, m + st), (W - m, m + st), (W - m, H - m - st), (W - m - st, H - m - st),
           (W - m - st, H - m), (m + st, H - m), (m + st, H - m - st), (m, H - m - st), (m, m + st), (m + st, m + st)]
    d.polygon(pts, fill=(150, 120, 96), outline=(120, 92, 70))
    cx, cy, r = W / 2, H / 2, H * 0.3
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(226, 214, 190), outline=(120, 92, 70), width=4)
    for k in range(12):                                                # rozetpatroon
        a = 2 * math.pi * k / 12
        d.line([(cx, cy), (cx + math.cos(a) * r * 0.85, cy + math.sin(a) * r * 0.85)], fill=(140, 104, 76), width=5)
    for rr in (0.25, 0.55, 0.8):
        d.ellipse([cx - r * rr, cy - r * rr, cx + r * rr, cy + r * rr], outline=(140, 104, 76), width=4)
    a = np.asarray(im).astype(np.float32) + rng.normal(0, 4, (H, W, 1))
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)).save(os.path.join(T, "FM_balustrade_kleur.png"))


tegelhal(); deurblad(); balustrade(); print("[14t_halletje] klaar")
