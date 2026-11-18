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


def parket(N=1024, sw=128, pw=64):
    """draaischijf (video 2025, 47 s): gelakte planken in visgraat (chevron), 1 textuur = 2 m, naadloos.
    Stroken van 0,25 m; per strook planken onder 45 graden, afwisselend links/rechts; eigen rng zodat de andere texturen gelijk blijven"""
    r2 = np.random.default_rng(141)
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    k = (x // sw).astype(int); xl = x % sw
    a = np.where(k % 2 == 0, y + xl, y - xl + sw)
    pid = (a // pw).astype(int); fr = (a % pw) / pw
    toon = r2.uniform(0.82, 1.12, (N // sw + 1, 64))
    t = toon[k, pid % 64]
    basis = np.array((150, 92, 52), np.float32)
    langs = np.where(k % 2 == 0, y - xl, y + xl)
    nerf = 0.95 + 0.05 * np.sin(fr * pw * 0.8 + pid * 1.7 + 1.5 * np.sin(langs * 0.04 + pid))
    im = basis[None, None, :] * (t * nerf)[..., None] + r2.normal(0, 4, (N, N, 1))
    naad = (fr < 0.035) | (xl < 2) | (xl > sw - 2)
    im[naad] = (84, 52, 32)
    Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)).save(os.path.join(T, "FM_parket_kleur.png"))


def bootplaket(N=256):
    """sierplaatje op de sloepen (video 2025, 34 s): donker vlak met een zilveren achtpuntige ster en vlechtwerk, naadloos niet nodig"""
    r3 = np.random.default_rng(142)
    im = Image.new("RGB", (N, N), (34, 32, 36)); d = ImageDraw.Draw(im)
    c = N / 2; zi = (196, 196, 204)
    for k in range(2):                                                  # twee gedraaide vierkanten = achtpuntige ster
        a0 = math.pi / 4 * k
        pts = [(c + 0.42 * N * math.cos(a0 + math.pi / 2 * j + math.pi / 4), c + 0.42 * N * math.sin(a0 + math.pi / 2 * j + math.pi / 4)) for j in range(4)]
        d.polygon(pts, outline=zi, width=10)
    d.ellipse([c - 0.13 * N, c - 0.13 * N, c + 0.13 * N, c + 0.13 * N], outline=zi, width=8)
    for j in range(8):
        a = math.pi / 4 * j
        d.line([(c + 0.13 * N * math.cos(a), c + 0.13 * N * math.sin(a)), (c + 0.3 * N * math.cos(a), c + 0.3 * N * math.sin(a))], fill=zi, width=6)
    d.rectangle([4, 4, N - 5, N - 5], outline=zi, width=6)
    a = np.asarray(im).astype(np.float32) + r3.normal(0, 4, (N, N, 1))
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)).save(os.path.join(T, "FM_bootplaket_kleur.png"))


def draaischijf(N=2048, R=7.5, RI=4.2, NS=24, pw=0.12):
    """bovenkant van de draaischijf (Eftepedia-foto Fata_draaischijf, video 2025 47 s), 1 textuur = de hele schijf (diameter 2R):
    binnen RI een gladde lichte vloer met een dunne ring, daarbuiten planken langs de omtrek in NS sectoren (veelhoekige ringen, met
    een visgraatnaad op de sectorgrens), donkere voegen; buiten R donker (rand)"""
    r4 = np.random.default_rng(143)
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    m = 2 * R / N; X = (x - N / 2) * m; Y = (y - N / 2) * m
    r = np.hypot(X, Y); a = np.arctan2(Y, X) % (2 * np.pi)
    sec = np.floor(a / (2 * np.pi / NS)); am = (sec + 0.5) * 2 * np.pi / NS
    rho = X * np.cos(am) + Y * np.sin(am)                               # afstand tot het midden loodrecht op de sectorkoorde
    tang = -X * np.sin(am) + Y * np.cos(am)
    rij = np.floor(rho / pw); fr = (rho / pw) % 1.0
    lengte = 0.9; stuk = np.floor((tang + 7 * rij) / lengte)
    toon = r4.uniform(0.85, 1.12, (int(R / pw) + 4, 64))
    t = toon[np.clip(rij.astype(int), 0, toon.shape[0] - 1), (stuk.astype(int) + int(sec.max()) * 5 + (sec.astype(int) * 5)) % 64]
    basis = np.array((156, 104, 66), np.float32)
    nerf = 0.95 + 0.05 * np.sin(tang * 9 + rij * 2.1)
    im = basis[None, None, :] * (t * nerf)[..., None]
    naad = (fr < 0.08) | ((tang + 7 * rij) / lengte % 1.0 < 0.012)
    dh = np.abs(((a / (2 * np.pi / NS)) % 1.0) - 0.0); dh = np.minimum(dh, 1 - dh) * (2 * np.pi / NS) * r
    naad |= dh < 0.02                                                   # sectorgrens
    im[naad] *= 0.62
    binnen = r < RI
    vloer = np.array((198, 178, 150), np.float32) * (0.97 + 0.03 * np.sin(r * 3))[..., None]
    im[binnen] = vloer[binnen]
    im[(np.abs(r - RI) < 0.05)] = (92, 64, 44)
    im[(np.abs(r - (RI - 0.35)) < 0.015)] = (160, 136, 108)
    im[r > R - 0.02] = (40, 40, 46)
    im += r4.normal(0, 3, (N, N, 1))
    Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)).save(os.path.join(T, "FM_draaischijf_kleur.png"))


tegelhal(); deurblad(); balustrade(); parket(); bootplaket(); draaischijf(); print("[14t_halletje] klaar")
