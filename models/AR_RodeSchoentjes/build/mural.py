import random, os, math
def mural_png(path):
    """muurschildering (vrij naar Pieck, Karen2016): bleke wand, kasteel in lijnen, meisje in gele jurk dansend, bloemetjes"""
    from PIL import Image, ImageDraw
    W, H = 1024, 768; im = Image.new("RGB", (W, H), (226, 216, 192)); d = ImageDraw.Draw(im)
    r = random.Random(3)
    for _ in range(4000): x, y = r.randrange(W), r.randrange(H); c = r.randint(-10, 8); d.point((x, y), fill=(226 + c, 216 + c, 192 + c))
    lijn = (150, 130, 110)
    for (x0, w, h, dak) in ((300, 90, 300, 90), (400, 60, 240, 70), (470, 120, 200, 60), (600, 70, 260, 80), (690, 50, 190, 60), (230, 60, 200, 60)):
        y1 = 460; y0 = y1 - h
        d.rectangle([x0, y0, x0 + w, y1], outline=lijn, width=3, fill=(232, 224, 204))
        d.polygon([(x0 - 8, y0), (x0 + w / 2, y0 - dak), (x0 + w + 8, y0)], outline=lijn, fill=(205, 170, 150))
        for k in range(2): d.rectangle([x0 + w * 0.3, y0 + 40 + k * 60, x0 + w * 0.45, y0 + 70 + k * 60], outline=lijn, width=2)
    # Karen: gele wijde rok, wit schort, rood lijfje, wit kapje, armen gespreid
    cx, cy = 520, 470
    d.pieslice([cx - 170, cy - 40, cx + 170, cy + 230], 200, 340, fill=(232, 190, 60), outline=(150, 110, 40), width=3)
    d.polygon([(cx - 150, cy + 60), (cx + 150, cy + 40), (cx + 60, cy - 10), (cx - 60, cy - 5)], fill=(232, 190, 60), outline=(150, 110, 40))
    d.polygon([(cx - 45, cy + 5), (cx + 45, cy), (cx + 30, cy + 120), (cx - 30, cy + 125)], fill=(245, 242, 232), outline=(150, 140, 120))
    d.polygon([(cx - 30, cy - 90), (cx + 30, cy - 90), (cx + 40, cy + 5), (cx - 40, cy + 5)], fill=(190, 40, 30), outline=(120, 30, 20))
    d.ellipse([cx - 26, cy - 150, cx + 26, cy - 92], fill=(240, 205, 175), outline=(150, 110, 90))
    d.polygon([(cx - 32, cy - 128), (cx, cy - 175), (cx + 32, cy - 128)], fill=(250, 250, 245), outline=(150, 140, 120))
    for s in (-1, 1): d.line([(cx + s * 30, cy - 75), (cx + s * 110, cy - 120), (cx + s * 150, cy - 105)], fill=(240, 205, 175), width=14)
    for s in (-1, 1): d.ellipse([cx + s * 60 - 14, cy + 200, cx + s * 60 + 14, cy + 214], fill=(200, 20, 20))
    for _ in range(18):
        x, y = r.randint(200, 820), r.randint(560, 720); d.line([(x, y), (x + r.randint(-6, 6), y + 30)], fill=(90, 130, 90), width=2)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(90, 120, 190))
    im.save(path)



if __name__ == "__main__":
    mural_png(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "textures", "RD_mural_kleur.png"))
