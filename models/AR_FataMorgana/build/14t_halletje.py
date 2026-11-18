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
    """video 2025 (40 s): crème balustrade met een band van bruine rechthoeken (crème binnenlijn, ruitjes) afgewisseld met crème
    vierkanten met een bruine ruit; 1 textuur = 1 paneel van 1,6 m, de vierkanten liggen half op de naad (naadloos)"""
    cr, br, dk = (234, 222, 198), (146, 100, 74), (110, 72, 52)
    im = Image.new("RGB", (W, H), cr); d = ImageDraw.Draw(im)
    for y in (26, H - 34): d.rectangle([0, y, W, y + 8], fill=br)                       # randlijnen boven/onder
    y0, y1 = 70, H - 78; hh = y1 - y0
    x0, x1 = int(W * 0.5 - W * 0.27), int(W * 0.5 + W * 0.27)                           # bruine rechthoek in het midden
    d.rectangle([x0, y0, x1, y1], fill=br, outline=dk, width=4)
    d.rectangle([x0 + 18, y0 + 18, x1 - 18, y1 - 18], outline=cr, width=5)
    cx, cy = W / 2, (y0 + y1) / 2
    for k in range(-3, 4):                                                              # ruitjes in de rechthoek
        r = 18; px = cx + k * 44
        d.polygon([(px, cy - r), (px + r, cy), (px, cy + r), (px - r, cy)], outline=cr, width=3)
    for ex in (0, W):                                                                   # vierkant met ruit, half op de naad
        s_ = hh / 2
        d.rectangle([ex - s_, y0, ex + s_, y1], outline=br, width=6)
        d.polygon([(ex, y0 + 14), (ex + s_ - 14, cy), (ex, y1 - 14), (ex - s_ + 14, cy)], fill=br)
        d.polygon([(ex, cy - 22), (ex + 22, cy), (ex, cy + 22), (ex - 22, cy)], fill=cr)
    a = np.asarray(im).astype(np.float32) + rng.normal(0, 4, (H, W, 1))
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)).save(os.path.join(T, "FM_balustrade_kleur.png"))


tegelhal(); deurblad(); balustrade(); print("[14t_halletje] klaar")
