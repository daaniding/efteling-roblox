"""22t_s1c_texturen: texturen voor sectie 1c (jungle met fata morgana), naar POV 2025 129-140 s (ref/video/s1/t129.5..t140.5):
  - S1_achterdoek.png: geschilderde lucht: paars/violet boven, oranje-geel gloeiend in het midden, rood aan de randen onder,
    duinen onderaan, nevel (137 s)
  - S1_paleis.png (alfa): klein paleis op een duin: minaret links, roze middenkoepel, zijkoepeltjes, verlichte raampjes (137 s)
  - S1_palmblad.png, S1_bamboeblad.png, S1_breedblad.png, S1_liaan.png, S1_heliconia.png (alfa): bladkaarten
Eigen tekenwerk (PIL), geen foto's. Gebruik: python3 build/22t_s1c_texturen.py"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, "textures")
R = random.Random(19)


def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def achterdoek():
    W, H = 2048, 1024
    im = Image.new("RGB", (W, H)); px = im.load()
    stops = [(0.0, (40, 18, 70)), (0.25, (110, 50, 190)), (0.5, (190, 90, 200)), (0.68, (240, 150, 110)), (0.8, (255, 190, 90)), (1.0, (230, 90, 40))]
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                c = lerp(stops[i][1], stops[i + 1][1], (t - stops[i][0]) / (stops[i + 1][0] - stops[i][0])); break
        for x in range(W):
            u = abs(x / (W - 1) - 0.5) * 2
            rand = u ** 2.2                                        # randen roder en donkerder
            cc = lerp(c, (150, 30, 20), rand * 0.65 * t + rand * 0.25)
            px[x, y] = cc
    d = ImageDraw.Draw(im)
    for k, (h0, kl) in enumerate([(0.83, (120, 60, 50)), (0.88, (80, 35, 35)), (0.94, (45, 20, 25))]):   # duinen
        pts = [(0, H)]
        for x in range(0, W + 1, 16):
            y = H * h0 + 30 * math.sin(x / 260.0 + k * 1.7) + 18 * math.sin(x / 97.0 + k)
            pts.append((x, y))
        pts.append((W, H)); d.polygon(pts, fill=kl)
    nev = Image.new("L", (W, H), 0); dn = ImageDraw.Draw(nev)
    for _ in range(40):
        x, y = R.uniform(0, W), R.uniform(H * 0.55, H * 0.85); r = R.uniform(80, 260)
        dn.ellipse([x - r * 2, y - r * 0.4, x + r * 2, y + r * 0.4], fill=R.randint(30, 70))
    nev = nev.filter(ImageFilter.GaussianBlur(40))
    im = Image.composite(Image.new("RGB", (W, H), (255, 200, 170)), im, nev)
    for _ in range(140):                                           # sterren boven
        x, y = R.uniform(0, W), R.uniform(0, H * 0.3); ImageDraw.Draw(im).point((x, y), fill=(230, 210, 255))
    im.save(os.path.join(OUT, "S1_achterdoek.png"))


def paleis():
    W, H = 1024, 768
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    roze, paars, donker, licht = (235, 140, 175, 255), (150, 80, 170, 255), (90, 50, 110, 255), (255, 230, 150, 255)
    d.polygon([(40, 660), (200, 610), (520, 590), (840, 615), (990, 665), (1024, 768), (0, 768)], fill=(170, 90, 80, 255))   # duin
    d.rectangle([180, 430, 820, 640], fill=paars)                                                                       # onderbouw
    d.rectangle([150, 470, 260, 640], fill=paars); d.rectangle([740, 470, 860, 640], fill=paars)
    d.rectangle([215, 120, 255, 470], fill=roze); d.rectangle([205, 200, 265, 214], fill=donker)                         # minaret
    d.ellipse([208, 92, 262, 140], fill=roze); d.line([(235, 60), (235, 95)], fill=roze, width=5)
    d.ellipse([360, 240, 640, 470], fill=(240, 120, 150, 255)); d.rectangle([360, 355, 640, 470], fill=roze)            # middenkoepel
    d.polygon([(500, 170), (488, 250), (512, 250)], fill=roze)
    for cx in (300, 700):                                                                                                 # zijkoepels
        d.ellipse([cx - 60, 340, cx + 60, 450], fill=roze); d.rectangle([cx - 60, 395, cx + 60, 450], fill=roze)
        d.line([(cx, 300), (cx, 345)], fill=roze, width=4)
    d.rectangle([600, 300, 620, 430], fill=roze); d.ellipse([594, 285, 626, 315], fill=roze)                             # klein torentje
    for x in range(200, 820, 46):                                                                                         # kantelen
        d.rectangle([x, 418, x + 24, 432], fill=paars)
    for row, y in enumerate((480, 545)):                                                                                  # ramen
        for x in range(205, 800, 58):
            if R.random() < 0.8:
                d.rectangle([x, y, x + 18, y + 34], fill=licht); d.ellipse([x, y - 9, x + 18, y + 9], fill=licht)
    d.rectangle([475, 520, 525, 640], fill=licht); d.ellipse([475, 495, 525, 545], fill=licht)                          # poort
    glow = im.filter(ImageFilter.GaussianBlur(14)); out = Image.alpha_composite(glow, im)
    out.save(os.path.join(OUT, "S1_paleis.png"))


def blad_vorm(d, cx, cy, ang, lengte, breedte, kleur, punten=10):
    """lancetvormig blad vanaf (cx, cy) in richting ang"""
    pts_l, pts_r = [], []
    for i in range(punten + 1):
        t = i / punten; w = breedte * math.sin(math.pi * t ** 0.8) * (1 - 0.15 * t)
        x = cx + math.cos(ang) * lengte * t; y = cy + math.sin(ang) * lengte * t
        pts_l.append((x - math.sin(ang) * w, y + math.cos(ang) * w)); pts_r.append((x + math.sin(ang) * w, y - math.cos(ang) * w))
    d.polygon(pts_l + pts_r[::-1], fill=kleur)
    d.line([(cx, cy), (cx + math.cos(ang) * lengte * 0.95, cy + math.sin(ang) * lengte * 0.95)], fill=tuple(max(0, c - 40) for c in kleur[:3]) + (255,), width=2)


def groen(var=0):
    g = R.randint(90, 150); return (int(g * R.uniform(0.35, 0.6)) + var, g + var, int(g * R.uniform(0.2, 0.4)), 255)


def palmblad():
    """geveerd palmblad: as van onder naar boven, smalle blaadjes schuin naar buiten (kaart 512x1024, voet onder)"""
    W, H = 512, 1024; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line([(W / 2, H), (W / 2 + 10, 20)], fill=(70, 80, 30, 255), width=7)
    for i in range(46):
        t = i / 45; y = H - 40 - t * (H - 80); x = W / 2 + 10 * t
        L = 230 * math.sin(math.pi * (0.15 + 0.85 * t)) ** 0.7 + 20
        for s in (-1, 1):
            ang = -math.pi / 2 + s * (0.95 - 0.25 * t) + R.uniform(-0.08, 0.08)
            blad_vorm(d, x, y, ang, L, 9, groen())
    im.save(os.path.join(OUT, "S1_palmblad.png"))


def bamboeblad():
    W, H = 512, 512; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(5):
        x0, y0 = R.uniform(150, 360), R.uniform(300, 480)
        d.line([(x0, y0), (x0 + R.uniform(-60, 60), y0 - 200)], fill=(120, 110, 50, 255), width=3)
        for _ in range(8):
            t = R.random(); x = x0 + (R.uniform(-60, 60)) * t; y = y0 - 200 * t
            blad_vorm(d, x, y, R.uniform(-math.pi, 0), R.uniform(90, 150), 13, groen(10))
    im.save(os.path.join(OUT, "S1_bamboeblad.png"))


def breedblad():
    W, H = 512, 512; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for _ in range(9):
        blad_vorm(d, W / 2 + R.uniform(-30, 30), H - 10, -math.pi / 2 + R.uniform(-1.1, 1.1), R.uniform(250, 420), R.uniform(45, 75), groen(), 14)
    im.save(os.path.join(OUT, "S1_breedblad.png"))


def liaan():
    """hangende liaan met blaadjes (kaart 256x1024, top boven)"""
    W, H = 256, 1024; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(3):
        x = W / 2 + R.uniform(-50, 50); pts = []
        for y in range(0, H, 16):
            x += R.uniform(-6, 6); pts.append((x, y))
        d.line(pts, fill=(110, 120, 40, 255), width=4)
        for (x, y) in pts[2::2]:
            for s in (-1, 1):
                blad_vorm(d, x, y, math.pi / 2 + s * R.uniform(0.6, 1.2), R.uniform(35, 60), 11, (R.randint(120, 170), R.randint(160, 200), 50, 255))
    im.save(os.path.join(OUT, "S1_liaan.png"))


def heliconia():
    """hangende kreeftenklauw: rode/oranje schutbladen in zigzag met gele randen (kaart 256x512)"""
    W, H = 256, 512; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line([(W / 2, 0), (W / 2, H - 40)], fill=(90, 110, 40, 255), width=6)
    for i in range(9):
        y = 40 + i * 50; s = 1 if i % 2 else -1
        d.polygon([(W / 2, y), (W / 2 + s * 105, y + 10), (W / 2 + s * 20, y + 48)], fill=(230, 60, 30, 255))
        d.line([(W / 2 + s * 105, y + 10), (W / 2 + s * 20, y + 48)], fill=(255, 210, 60, 255), width=5)
    im.save(os.path.join(OUT, "S1_heliconia.png"))


for f in (achterdoek, paleis, palmblad, bamboeblad, breedblad, liaan, heliconia): f()
print("[22t] klaar")
