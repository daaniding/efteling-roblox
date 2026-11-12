"""
10_eikentros: bladkaart (512x512 RGBA) met een tros echte eikenbladeren uit ambientCG LeafSet016 (CC0) voor de kruin van de
Sprookjesboom (Eftepedia: eikachtige boom, kunstblad). Zelfde opzet als textures/bomen/blad_eik.png (kaart = 0.95 m in de kruin,
blad ~10 cm). Bladeren: uitgeknipt via de opacity-kaart, zomergroen gemaakt (scan is lentegroen en van achteren belicht),
radiaal langs 5 takjes, onderste laag donkerder voor diepte.
Gebruik: python3 10_eikentros.py (venv met numpy, scipy, pillow)
"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D = os.path.join(REPO, "textures", "ambientcg", "LeafSet016")
col = np.asarray(Image.open(os.path.join(D, "LeafSet016_2K-PNG_Color.png")).convert("RGB"), np.float32) / 255
op = np.asarray(Image.open(os.path.join(D, "LeafSet016_2K-PNG_Opacity.png")).convert("L"), np.float32) / 255
lab, n = ndimage.label(op > 0.5)
leaves = []
for sl in ndimage.find_objects(lab):
    h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
    if h * w < 20000: continue
    rgb = col[sl]; a = op[sl]
    # zomergroen: donkerder en iets blauwer/verzadigder dan de lentescan
    g = rgb * np.array([0.46, 0.58, 0.40], np.float32)
    lum = rgb.mean(2, keepdims=True); g = g * 0.85 + lum * np.array([0.10, 0.16, 0.06]) * 0.15
    img = Image.fromarray((np.dstack([np.clip(g, 0, 1), a]) * 255).astype(np.uint8))
    leaves.append(img)   # steel onderaan (atlas: bladeren staan rechtop)
print("bladeren uit de atlas:", len(leaves))
rnd = random.Random(16)
W = 1024                                  # werk op 2x, schaal naar 512
card = Image.new("RGBA", (W, W), (0, 0, 0, 0))
dr = ImageDraw.Draw(card)
C = (W / 2, W / 2)
twigs = []
for k in range(7):                        # takjes vanuit het midden
    a = math.radians(k * 51.4 + rnd.uniform(-14, 14)); L = rnd.uniform(0.28, 0.40) * W
    end = (C[0] + math.cos(a) * L, C[1] + math.sin(a) * L); twigs.append((a, L))
    dr.line([C, end], fill=(70, 58, 40, 255), width=4)
LEAF_PX = 0.105 / 0.95 * W                # blad ~10.5 cm op een kaart van 0.95 m
placed = []
for layer in (0, 1):                      # 0 = onderlaag (donker), 1 = bovenlaag
    for (a, L) in twigs:
        for j in range(7 if layer == 0 else 5):
            t = rnd.uniform(0.06, 1.0); base = (C[0] + math.cos(a) * L * t, C[1] + math.sin(a) * L * t)
            side = rnd.choice((-1, 1)); ang = a + side * math.radians(rnd.uniform(15, 80))
            lf = rnd.choice(leaves); s = LEAF_PX * rnd.uniform(0.85, 1.25) / lf.height
            lf = lf.resize((max(8, int(lf.width * s)), max(8, int(lf.height * s))), Image.LANCZOS)
            if layer == 0:
                arr = np.asarray(lf, np.float32); arr[..., :3] *= 0.72; lf = Image.fromarray(arr.astype(np.uint8))
            # blad met de steel op het takje, punt naar buiten
            rot = lf.rotate(-math.degrees(ang) - 90, expand=True, resample=Image.BICUBIC)
            off = (math.cos(ang) * lf.height / 2, math.sin(ang) * lf.height / 2)
            pos = (int(base[0] + off[0] - rot.width / 2), int(base[1] + off[1] - rot.height / 2))
            card.alpha_composite(rot, pos); placed.append(1)
    for (a, L) in twigs:                  # eindknop: blaadjes aan de tip
        tip = (C[0] + math.cos(a) * L, C[1] + math.sin(a) * L)
        lf = rnd.choice(leaves); s = LEAF_PX * 0.9 / lf.height
        lf = lf.resize((int(lf.width * s), int(lf.height * s)), Image.LANCZOS)
        rot = lf.rotate(-math.degrees(a) - 90, expand=True, resample=Image.BICUBIC)
        card.alpha_composite(rot, (int(tip[0] + math.cos(a) * lf.height / 2 - rot.width / 2), int(tip[1] + math.sin(a) * lf.height / 2 - rot.height / 2)))
out = card.resize((512, 512), Image.LANCZOS)
# randpixels bijkleuren (geen witte/zwarte franjes bij alfa-filtering in Roblox)
arr = np.asarray(out, np.float32); a = arr[..., 3:4] / 255
rgb = arr[..., :3]; blur = np.asarray(Image.fromarray(rgb.astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32)
wsum = np.asarray(Image.fromarray((a[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32)[..., None] / 255
fill = np.where(wsum > 0.01, blur / np.maximum(wsum, 0.01) * 1.0, rgb)
rgb = np.where(a > 0.5, rgb, np.clip(fill, 0, 255))
Image.fromarray(np.dstack([rgb, arr[..., 3]]).astype(np.uint8)).save(os.path.join(REPO, "textures", "bomen", "blad_eik_echt.png"))
print("bladkaart:", len(placed), "+ 7 tips, opgeslagen textures/bomen/blad_eik_echt.png")
