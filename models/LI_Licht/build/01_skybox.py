"""01_skybox: equirect-HDRI (Poly Haven, CC0) -> 6 Roblox-skyboxvlakken (1024 px), zon gedraaid naar de Roblox-zon.
Vlakken (in Studio gemeten met testplaatjes, 16 nov): Lf=+X, Rt=-X, Ft=-Z, Bk=+Z, rechtop en niet gespiegeld;
Up: beeld-boven=+X, beeld-rechts=-Z; Dn: beeld-boven=-X, beeld-rechts=-Z.
Gebruik: python3 01_skybox.py <hdr> <uitmap> <zon_x> <zon_y> <zon_z> [belichting] [ophelder]
ophelder: versterking van de lucht recht tegenover de zon (bv. 2.2), vloeiend naar 1 bij de zon (Daan: andere kant te donker)."""
import sys, os, math
import numpy as np, cv2
from PIL import Image
hdr, uit = sys.argv[1], sys.argv[2]
zon = np.array([float(a) for a in sys.argv[3:6]]); zon /= np.linalg.norm(zon)
EV = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
OPH = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
N = 1024
im = cv2.imread(hdr, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_COLOR)[:, :, ::-1].astype(np.float32)
im = np.nan_to_num(im, nan=0, posinf=1e5)
H, W, _ = im.shape
lum = im @ np.array([0.2126, 0.7152, 0.0722], np.float32)
y, x = np.unravel_index(np.argmax(lum), lum.shape)
lon_s = ((x + 0.5) / W - 0.5) * 2 * math.pi
# rotatie om Y zodat de HDRI-zon (lon_s) naar de Roblox-zon wijst. eigen frame: lon 0 = -Z, oplopend naar +X
lon_r = math.atan2(zon[0], -zon[2])
rot = lon_r - lon_s

def richting(face, s, t):
    o = np.ones_like(s)
    return {'Lf': (o, -t, s), 'Rt': (-o, -t, -s), 'Ft': (s, -t, -o), 'Bk': (-s, -t, o),
            'Up': (-t, o, -s), 'Dn': (t, -o, -s)}[face]

c = (np.arange(N) + 0.5) / N * 2 - 1
S, T = np.meshgrid(c, c)
# belichting: mediaan van de bovenste helft -> ~0,18 lineair (middengrijs), dan zachte schouder (filmisch)
boven = lum[: H // 2]
k = 0.21 / np.median(boven) * 2 ** EV
def tonemap(v):
    v = v * k
    a, b, cc, d, e = 2.51, 0.03, 2.43, 0.59, 0.14            # ACES-benadering (Narkowicz)
    v = np.clip((v * (a * v + b)) / (v * (cc * v + d) + e), 0, 1)
    return np.where(v <= 0.0031308, 12.92 * v, 1.055 * np.power(v, 1 / 2.4) - 0.055)
# horizonkleur per windrichting: mediaan van de band 1-4 graden boven de horizon, uitgesmeerd over ~10 graden
band = im[int(H * 0.5 - H * 4 / 180): int(H * 0.5 - H * 1 / 180)]
_m = np.median(band, axis=0).astype(np.float32); _p = W // 2
HOR_LON = cv2.GaussianBlur(np.concatenate([_m[-_p:], _m, _m[:_p]])[None], (0, 0), sigmaX=W / 10)[0][_p:-_p]
HOR_LON = np.minimum(HOR_LON, np.percentile(HOR_LON, 50, axis=0) * 4)   # zon-piek temmen
os.makedirs(uit, exist_ok=True)
for f in ('Ft', 'Bk', 'Lf', 'Rt', 'Up', 'Dn'):
    dx, dy, dz = richting(f, S, T)
    n = np.sqrt(dx * dx + dy * dy + dz * dz); dx, dy, dz = dx / n, dy / n, dz / n
    lon = np.arctan2(dx, -dz) - rot
    lat = np.arcsin(np.clip(dy, -1, 1))
    u = ((lon / (2 * math.pi) + 0.5) % 1.0) * W - 0.5
    v = (0.5 - lat / math.pi) * H - 0.5
    px = cv2.remap(im, u.astype(np.float32), v.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    # onder de horizon: geen gespiegelde 'zee' maar de nevelkleur van de horizonband, iets donkerder naar beneden
    w = np.clip(-dy / 0.06, 0, 1)[..., None]
    # vlak onder de horizon nevel, verder omlaag 'grond'. (Middaglucht kloofendal is gemaakt met 0.3 + 0.7*exp(-x/0.06)
    # en een vaste horizonkleur; schemerlucht belfast met deze versie.)
    donker = 0.15 + 0.85 * np.exp(-np.clip(-dy, 0, 1) / 0.04)
    hor = HOR_LON[np.clip(u.round().astype(int), 0, W - 1) % W]
    px = px * (1 - w) + hor * donker[..., None] * w
    if OPH != 1.0:   # anti-zonkant ophelderen
        cosz = dx * zon[0] + dy * zon[1] + dz * zon[2]
        px = px * (1 + (OPH - 1) * ((1 - cosz) / 2) ** 1.2)[..., None]
    Image.fromarray((tonemap(px) * 255 + 0.5).astype(np.uint8)).save(os.path.join(uit, f'{f}.png'))
print('zon in HDRI lon %.1f elev %.1f; gedraaid %.1f graden; k=%.4f' % (math.degrees(lon_s), 90 - 180 * (y + 0.5) / H, math.degrees(rot), k))
