"""21_bomen: boomposities rond de Pagode uit de luchtfoto (Daan 17 nov: "bomen, maar het moet echt realistisch").
Boomkronen = donker, gevlekt groen op ref/luchtfoto/pagode_10cm.jpg (geen water: water_*.npy, geen grijs/dak), dan Poisson-
schijven (4.5 m), nooit op de route (bestrating/tribune/laantje/bordes zoals maak_plaatsscript 'bebouwd'), station, armsleuf,
uitgangspad of binnen 1.5 m van een hek (exports/omgeving_hekken.json). Soort: donker/blauwgroen = den, lichter = loofboom.
Schrijft exports/bomen.json: [[x, y, soort, hoogte_m, draai], ...] (parkframe). Gebruik: python3 build/21_bomen.py"""
import json, math, os, numpy as np
from PIL import Image
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
meta = json.load(open(os.path.join(D, "ref", "luchtfoto", "pagode_10cm.json")))
im = np.asarray(Image.open(os.path.join(D, "ref", "luchtfoto", "pagode_10cm.jpg")).convert("RGB")).astype(float)
H, W, _ = im.shape
x0, y1, pm = meta["x0"], meta["y1"], meta["px_m"]
def pix(x, y): return int((y1 - y) / pm), int((x - x0) / pm)
CX, CY = 360.0, 47.5
hek = json.load(open(os.path.join(D, "exports", "omgeving_hekken.json")))
rng = np.random.default_rng(7)

def bebouwd(x, y):
    dx, dy = x - CX, y - CY; r = math.hypot(dx, dy); a = math.degrees(math.atan2(dy, dx)) % 360
    aL = 104.0 + (r - 14.2) * 0.95 - math.degrees(1.5 / max(r, 1))
    ux, uy = math.cos(math.radians(-15.5615)), math.sin(math.radians(-15.5615))
    lx, ly = (x - 320.5) * ux + (y - 58.5) * uy, -(x - 320.5) * uy + (y - 58.5) * ux
    if lx > -12 and lx < 34 and abs(ly) < 6.5: return True                       # armsleuf + voet + ruimte voor de arm
    return (r < 13.0 or (r < 29.0 and a > aL - 5 and a < 160) or (r < 15.5 and a > 50 and a < 160)
            or (r < 17.0 and (a > 300 or a < 60)) or (r < 19.5 and 85 <= a < aL + 2))

def bij_hek(x, y, marge=1.5):
    for a_, b_, _ in hek:
        ax, ay, bx, by = a_[0], a_[1], b_[0], b_[1]; vx, vy = bx - ax, by - ay; L = vx * vx + vy * vy
        t = 0 if L == 0 else max(0, min(1, ((x - ax) * vx + (y - ay) * vy) / L))
        if math.hypot(ax + t * vx - x, ay + t * vy - y) < marge: return True
    return False

# kroonmasker: groen overheerst, niet te licht (gras/paden), wat textuur
R, G, B = im[..., 0], im[..., 1], im[..., 2]; V = im.mean(-1)
groen = (G > R * 1.02) & (G > B * 0.95) & (V < 115)
from scipy.ndimage import uniform_filter
tex = np.sqrt(np.maximum(uniform_filter(V ** 2, 9) - uniform_filter(V, 9) ** 2, 0))
kroon = groen & (tex > 9)
kroon = uniform_filter(kroon.astype(float), 25) > 0.45                         # 2.5 m venster: echte kronen, geen losse plukjes
# kale loofbomen (winterfoto, video: grote kale eiken/beuken boven de wachtrij): grijsbruin met fijne takstructuur
sat = (im.max(-1) - im.min(-1)) / (im.max(-1) + 1)
kaal = (tex > 13) & (V < 150) & (sat < 0.35) & ~groen
kaal = uniform_filter(kaal.astype(float), 31) > 0.5
try:
    wm = np.load(os.path.join(D, "ref", "luchtfoto", "water_370_440_-20_80.npy"))
except Exception:
    wm = None


pts = []
for _ in range(60000):
    x, y = rng.uniform(x0 + 2, meta["x1"] - 2), rng.uniform(meta["y0"] + 2, y1 - 2)
    if math.hypot(x - CX, y - CY) > 40: continue
    if x < 334 and y < 27: continue                                              # gebouwen van de buurattractie (zuidwest)
    if math.hypot(x - 318, y - 47) < 10 or math.hypot(x - 393, y - 52) < 10: continue   # daken buurattracties (ster west, Gondoletta-station oost)
    if wm is not None and 370 <= x < 440 and -20 <= y < 80:                      # water (1 m raster, rij 0 = noord)
        ri, ci = int(79 - (y + 20)) if False else int(80 - y - 1), int(x - 370)
        if 0 <= ri < wm.shape[0] and 0 <= ci < wm.shape[1] and wm[ri, ci]: continue
    i, j = pix(x, y)
    groenkroon = kroon[i, j]
    if not (groenkroon or kaal[i, j]) or bebouwd(x, y): continue
    if any(math.hypot(x - p[0], y - p[1]) < (4.5 if groenkroon else 6.0) for p in pts): continue
    if bij_hek(x, y): continue
    win = im[max(0, i - 20):i + 20, max(0, j - 20):j + 20].reshape(-1, 3)
    v, bl = win.mean(), (win[:, 2] / (win[:, 1] + 1)).mean()
    soort = "den" if groenkroon and (v < 62 or bl > 0.92) else "loof"
    r_ = math.hypot(x - CX, y - CY)
    hoogte = float(rng.uniform(24, 30) if soort == "den" and r_ < 24 else rng.uniform(19, 25) if soort == "den" else rng.uniform(16, 23))   # video: sparren naast het station zo hoog als de gondel
    pts.append([round(x, 2), round(y, 2), soort, round(hoogte, 1), round(float(rng.uniform(0, 6.283)), 2)])
# grote eik aan het oostpad (video 6:35-6:40; op de winterluchtfoto kaal, dus niet als kroon herkend)
ex, ey = CX + 18.5 * math.cos(math.radians(18)), CY + 18.5 * math.sin(math.radians(18))
pts = [p for p in pts if math.hypot(p[0] - ex, p[1] - ey) > 6] + [[round(ex, 2), round(ey, 2), "loof", 22.0, 1.1]]
# gondelbaan: de gondel (straal 8.5 m) zwaait van het station naar boven boven de arm (richting draaias). Een boom naast die
# baan mag niet hoger zijn dan de onderkant van de gondel daar (arm 38.6 m vanaf de as op 4.2 m hoogte), min 3 m marge
AX, AY = 320.5, 58.5; L_ARM = 38.6
ux, uy = (AX - CX), (AY - CY); dA = math.hypot(ux, uy); ux, uy = ux / dA, uy / dA
for p in pts:
    vx, vy = p[0] - CX, p[1] - CY; langs = vx * ux + vy * uy; dwars = abs(-vx * uy + vy * ux)
    if dwars < 8.5 + 5.0 and 0 < langs < dA:
        hor = max(0.0, dA - langs); th = math.asin(min(1.0, hor / L_ARM)); gondel_onder = 4.2 + L_ARM * math.cos(th) - 3.0
        p[3] = round(min(p[3], max(8.0, gondel_onder - 3.0)), 1)
json.dump(pts, open(os.path.join(D, "exports", "bomen.json"), "w"))
print("[21_bomen] %d bomen (%d den, %d loof)" % (len(pts), sum(p[2] == "den" for p in pts), sum(p[2] == "loof" for p in pts)))
# controlebeeld
from PIL import ImageDraw
c = Image.open(os.path.join(D, "ref", "luchtfoto", "pagode_10cm.jpg")).convert("RGB"); d = ImageDraw.Draw(c)
for x, y, s, h, _ in pts:
    i, j = pix(x, y); k = (255, 80, 80) if s == "den" else (255, 255, 0); d.ellipse((j - 14, i - 14, j + 14, i + 14), outline=k, width=4)
i, j = pix(CX, CY)
for r in (13, 29, 46): d.ellipse((j - r * 10, i - r * 10, j + r * 10, i + r * 10), outline=(255, 0, 255), width=3)
c.crop((pix(CX - 48, CY + 48)[1], pix(CX - 48, CY + 48)[0], pix(CX + 48, CY - 48)[1], pix(CX + 48, CY - 48)[0])).resize((480, 480)).save(os.path.join(D, "review", "21_bomen.jpg"))
