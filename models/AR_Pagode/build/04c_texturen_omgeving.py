"""04c_texturen_omgeving: borden van de wachtrij, getekend naar video fmEZsIkqsl8 (0:13-0:19 ingangsbord, 6:49-6:52 uitgangsbord).
  PG_ingangsbord_kleur.png: lichtblauw veld, donkerteal rand met oranje binnenlijn, golvende bovenkant met oranje ornament,
                            'PAGODE' wijnrood met oranje omlijning, oranje krul eronder. Vorm = BORD_OMTREK (ook gebruikt door 12_omgeving).
  PG_uitgangsbord_kleur.png: staand bord, lichtblauw, teal rand, spitse bovenkant met oranje ruit, 'UITGANG' + 'EXIT AUSGANG SORTIE'.
Gebruik: python3 build/04c_texturen_omgeving.py  (vanuit models/AR_Pagode)"""
import os, math
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:          # in Blender alleen BORD_OMTREK nodig
    Image = None

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(D, 'textures')
BLAUW = (128, 196, 212); TEAL = (24, 86, 98); ORANJE = (232, 140, 44); WIJN = (122, 26, 52); DONKER = (34, 48, 58)
FONT = '/System/Library/Fonts/Supplemental/BigCaslon.ttf'


def bord_boven(u):
    """Bovenrand van het ingangsbord (0..1 breed, hoogte 0..1): krul omhoog aan de uiteinden, boog in het midden."""
    return (0.80 + 0.16 * math.exp(-((u - 0.5) / 0.085) ** 2) + 0.05 * math.exp(-((u - 0.5) / 0.22) ** 2)
            + 0.13 * math.exp(-(u / 0.03) ** 2) + 0.13 * math.exp(-((1 - u) / 0.03) ** 2) - 0.03 * math.sin(u * math.pi) ** 8)


def BORD_OMTREK(n=64):
    """Omtrek (u, v) tegen de klok in, begint linksonder."""
    pts = [(0.0, 0.0), (1.0, 0.0)]
    for i in range(n, -1, -1):
        u = i / n; pts.append((u, bord_boven(u)))
    return pts


def tekst(d, xy, s, f, vul, rand=None, rw=0):
    if rand: d.text(xy, s, font=f, fill=vul, anchor='mm', stroke_width=rw, stroke_fill=rand)
    else: d.text(xy, s, font=f, fill=vul, anchor='mm')


def ingangsbord():
    W, H = 2048, 768
    im = Image.new('RGB', (W, H), TEAL); d = ImageDraw.Draw(im)
    P = lambda u, v: (u * W, (1 - v) * H)
    om = [P(u, v) for u, v in BORD_OMTREK(160)]
    d.polygon(om, fill=TEAL)
    # binnenvelden: oranje lijn en blauw veld, ingesprongen
    def inset(k):
        pts = [(0.0 + k, k * 1.6)] + [(1.0 - k, k * 1.6)]
        for i in range(160, -1, -1):
            u = k + (1 - 2 * k) * i / 160; pts.append((u, bord_boven(u) - k * 1.6))
        return [P(u, v) for u, v in pts]
    d.polygon(inset(0.022), fill=ORANJE); d.polygon(inset(0.030), fill=BLAUW)
    # ornament in de boog: oranje spits blad + krullen
    cx = W / 2; top = (1 - bord_boven(0.5) + 0.07) * H
    d.polygon([(cx, top), (cx - 46, top + 70), (cx, top + 120), (cx + 46, top + 70)], fill=ORANJE)
    d.polygon([(cx, top + 22), (cx - 24, top + 70), (cx, top + 98), (cx + 24, top + 70)], fill=WIJN)
    for s in (-1, 1):
        d.line([(cx + s * 50, top + 70), (cx + s * 150, top + 95)], fill=ORANJE, width=10)
    f = ImageFont.truetype(FONT, 300)
    tekst(d, (W / 2, H * 0.53), 'PAGODE', f, WIJN, ORANJE, 9)
    # oranje krul onder de tekst
    y = H * 0.80
    d.line([(cx - 260, y), (cx - 40, y)], fill=ORANJE, width=10); d.line([(cx + 40, y), (cx + 260, y)], fill=ORANJE, width=10)
    d.ellipse([cx - 22, y - 22, cx + 22, y + 22], fill=ORANJE)
    for s in (-1, 1):
        d.arc([cx + s * 300 - 40, y - 40, cx + s * 300 + 40, y + 40], 0, 360, fill=ORANJE, width=10)
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    im.save(os.path.join(T, 'PG_ingangsbord_kleur.png'))


def uitgangsbord():
    W, H = 512, 1024
    im = Image.new('RGB', (W, H), TEAL); d = ImageDraw.Draw(im)
    d.polygon([(30, 1000), (482, 1000), (482, 180), (256, 40), (30, 180)], fill=ORANJE)
    d.polygon([(44, 986), (468, 986), (468, 188), (256, 58), (44, 188)], fill=BLAUW)
    d.polygon([(256, 120), (226, 160), (256, 200), (286, 160)], fill=ORANJE)
    tekst(d, (256, 330), 'UITGANG', ImageFont.truetype(FONT, 70), DONKER)
    d.line([(90, 400), (422, 400)], fill=ORANJE, width=6)
    for k, s in enumerate(('EXIT', 'AUSGANG', 'SORTIE')):
        tekst(d, (256, 480 + 80 * k), s, ImageFont.truetype(FONT, 54), DONKER)
    im.save(os.path.join(T, 'PG_uitgangsbord_kleur.png'))


def uitgangsboog():
    """breed bord boven de uitgangstrap (Daan 17 nov: "het moet duidelijk zijn waar de exit is"): zelfde huisstijl, pijl naar beneden."""
    W, H = 1024, 320
    im = Image.new('RGB', (W, H), TEAL); d = ImageDraw.Draw(im)
    d.rectangle([14, 14, W - 15, H - 15], fill=ORANJE); d.rectangle([26, 26, W - 27, H - 27], fill=BLAUW)
    tekst(d, (512, 130), 'UITGANG', ImageFont.truetype(FONT, 104), WIJN, ORANJE, 3)
    tekst(d, (512, 245), 'EXIT  ·  AUSGANG  ·  SORTIE', ImageFont.truetype(FONT, 40), DONKER)
    for x in (96, 928):                      # groene pijlen naar beneden (de trap af)
        d.rectangle([x - 16, 70, x + 16, 170], fill=(30, 140, 70)); d.polygon([(x - 44, 165), (x + 44, 165), (x, 250)], fill=(30, 140, 70))
    im.save(os.path.join(T, 'PG_uitgangsboog_kleur.png'))


if __name__ == '__main__':
    ingangsbord(); uitgangsbord(); uitgangsboog(); print('[04c] borden klaar')
