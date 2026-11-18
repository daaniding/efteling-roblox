"""18p_routeplan: vaarroute en scènekamers uit de Eftepedia-plattegrond (ref/eftepedia/Plattegrondfata.jpg) naar het modelstelsel.
Daan (18 nov): "je hebt de blue print dus je weet de route dus alleen ff de route maken met de kamers niet hoe ze eruit zien".
Kaart: blauw = vaargoot (secties 1-14), zandkleur = scènevlakken (kamers), lichtgroen = achter de schermen.
Schaal 23 px/m op de plattegrond van 2479 px breed, draaischijfmidden (1935, 995) = model (6,3; -335,8), boven = noord (zoals 16).
Weg uit de kaart: de instaphal (sectie 15, eigen model 16), alles oostelijker dan x 12,4 (binnenplaats/uitgang/Bazaar).
Toegevoegd: doorvaart hal-noordwest -> sectie 1 en sectie 14 -> hal-zuidwest (onze hal is smaller dan op de plattegrond).
Uit: ref/route_plan.npz (raster 0,25 m: blauw, zand) + review/18_routeplan.png. Gebruik: python3 build/18p_routeplan.py (uvx opencv)"""
import os, numpy as np, cv2
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
im = cv2.imread(os.path.join(D, "ref", "eftepedia", "Plattegrondfata.jpg"))[:, :, ::-1].astype(int)
F = im.shape[1] / 2479.0
R_, G_, B_ = im[..., 0], im[..., 1], im[..., 2]
blauw = (R_ < 45) & (B_ > 95)
zand = (R_ > 180) & (G_ > 135) & (G_ < 195) & (B_ > 85) & (B_ < 155)
k = np.ones((7, 7), np.uint8)
blauw = cv2.morphologyEx(blauw.astype(np.uint8), cv2.MORPH_CLOSE, k) > 0          # tekst, streepjes en stippels dicht
zand = cv2.morphologyEx(zand.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
S = 0.25; X0, X1, Y0, Y1 = -74.0, 13.0, -352.0, -294.0
xs = np.arange(X0 + S / 2, X1, S); ys = np.arange(Y1 - S / 2, Y0, -S)               # rij 0 = noord
gx, gy = np.meshgrid(xs, ys)
px = ((gx - 6.3) * 23 + 1935) * F; py = ((-335.8 - gy) * 23 + 995) * F
ok = (px >= 0) & (px < im.shape[1] - 1) & (py >= 0) & (py < im.shape[0] - 1)
pxi = np.clip(px.astype(int), 0, im.shape[1] - 1); pyi = np.clip(py.astype(int), 0, im.shape[0] - 1)
mb = blauw[pyi, pxi] & ok; mz = zand[pyi, pxi] & ok
# uitsluiten: onze instaphal (+ muren), en oostelijk van x 12,4 (binnenplaats, uitganghalletje, Bazaar)
uit = ((gx > -3.8) & (gy < -323.3)) | (gx > 12.4)
# plattegrond-hal is breder dan de onze: zuidlob van sectie 15 en de hal-rand op de kaart weg
dpx = px / F; dpy = py / F
uit |= ((dpx > 1790) & (dpy > 715)) | ((dpx > 1475) & (dpy > 1020))
mb &= ~uit; mz &= ~uit
# doorvaarten naar onze hal: noordwest (x -3,5..-0,3 door de noordmuur) en zuidwest (sectie 14 -> westmuur y -346,3..-343,0)
mb |= (gx > -3.5) & (gx < -0.3) & (gy > -323.75) & (gy < -320.5)
mb |= (gx > -15.5) & (gx < -3.4) & (gy > -346.3) & (gy < -343.0)
# kleine eilandjes weg, alleen het grote vaargootstuk + zand dat eraan grenst
n, lab, st, _ = cv2.connectedComponentsWithStats(mb.astype(np.uint8), 8)
groot = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); mb = lab == groot
naast = cv2.dilate(mb.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
n2, lab2, st2, _ = cv2.connectedComponentsWithStats(mz.astype(np.uint8), 8)
houd = np.zeros_like(mz)
for i in range(1, n2):
    m = lab2 == i
    if st2[i, cv2.CC_STAT_AREA] > 40 and (m & naast).any(): houd |= m
mz = houd & ~mb
# alleen onder het dak (ref/route_dak.npy uit 18d_dakmasker), behalve de door kantelenmuren omsloten strook tussen hal en koepelgebouw
dakp = os.path.join(D, "ref", "route_dak.npy")
if os.path.exists(dakp):
    dak = np.load(dakp) | ((gx > -3.0) & (gy > -323.8) & (gy < -318.4))
    dak = cv2.erode(dak.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0     # muren (0,4 m) ook onder het dak
    mb &= dak | ((gx > -3.6) & (gy < -323.3)); mz &= dak
    n, lab, st, _ = cv2.connectedComponentsWithStats(mb.astype(np.uint8), 8); mb = lab == (1 + np.argmax(st[1:, cv2.CC_STAT_AREA]))
uni = cv2.morphologyEx((mb | mz).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0   # lichte omlijningen op de kaart dicht
gat = ~uni; n3, lab3, st3, _ = cv2.connectedComponentsWithStats(gat.astype(np.uint8), 4)
for i in range(1, n3):
    if st3[i, cv2.CC_STAT_AREA] < 160: uni |= lab3 == i                 # kleine gaatjes (< 10 m2) dicht
uni &= (~uit | mb) & (dak | mb if os.path.exists(dakp) else True)       # niet in onze hal (doorvaarten blijven), niet buiten het dak
mz = uni & ~mb
def rects(m):
    """gulzig samenvoegen tot rechthoeken (rij-runs, verticaal gelijke runs samen): [x0, y0, x1, y1] in meters"""
    uit, open_ = [], {}
    for r in range(m.shape[0] + 1):
        runs = set()
        if r < m.shape[0]:
            row = m[r]; c = 0
            while c < len(row):
                if row[c]:
                    c0 = c
                    while c < len(row) and row[c]: c += 1
                    runs.add((c0, c))
                else: c += 1
        for k in list(open_):
            if k not in runs: uit.append((k[0], open_.pop(k), k[1], r))
        for k in runs:
            if k not in open_: open_[k] = r
    return np.array([[X0 + c0 * S, Y1 - r1 * S, X0 + c1 * S, Y1 - r0 * S] for (c0, r0, c1, r1) in uit])
# muren: contouren van kamers+vaargoot, vereenvoudigd; per zijde de buitenkant bepalen; langs onze hal geen muur (die is er al)
cs, _ = cv2.findContours(uni.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
def m2(c, r): return (X0 + (c + 0.5) * S, Y1 - (r + 0.5) * S)
def binnen(x, y):
    c, r = int((x - X0) / S), int((Y1 - y) / S)
    return 0 <= r < uni.shape[0] and 0 <= c < uni.shape[1] and uni[r, c]
muren = []
for cnt in cs:
    ap = cv2.approxPolyDP(cnt, 1.2, True)[:, 0, :]
    for i in range(len(ap)):
        a = np.array(m2(*ap[i])); b = np.array(m2(*ap[(i + 1) % len(ap)]))
        d = b - a; L = np.hypot(*d)
        if L < 0.05: continue
        t = d / L; nrm = np.array((-t[1], t[0])); mid = (a + b) / 2
        if mid[0] > -4.1 and mid[1] < -323.0: continue
        if binnen(*(mid + nrm * 0.4)) and not binnen(*(mid - nrm * 0.4)): nrm = -nrm
        muren.append([a[0], a[1], b[0], b[1], nrm[0], nrm[1]])
# werklicht: elke ~7 m een punt op de vaargoot
lichten = []
for y in np.arange(Y1 - 3, Y0, -7.0):
    for x in np.arange(X0 + 3, X1, 7.0):
        c, r = int((x - X0) / S), int((Y1 - y) / S)
        if 0 <= r < mb.shape[0] and 0 <= c < mb.shape[1] and mb[r, c] and not (x > -4 and y < -323): lichten.append((x, y))
np.savez_compressed(os.path.join(D, "ref", "route_plan.npz"), blauw=mb, zand=mz, X0=X0, Y1=Y1, S=S,
                    r_blauw=rects(mb), r_zand=rects(mz), r_uni=rects(uni), muren=np.array(muren), lichten=np.array(lichten))
print("rechthoeken: blauw %d, zand %d, plafond %d; muurstukken %d; lichten %d" % (len(rects(mb)), len(rects(mz)), len(rects(uni)), len(muren), len(lichten)))
print("vaargoot %.0f m2, scènevlakken %.0f m2, raster %s" % (mb.sum() * S * S, mz.sum() * S * S, mb.shape))
# controlebeeld: zand = bruin, blauw = blauw, onze hal + uitgang + gebouwen-omtrek erover
vis = np.full(mb.shape + (3,), 235, np.uint8); vis[mz] = (205, 165, 115); vis[mb] = (20, 120, 175)
def rect(x0, y0, x1, y1, kl):
    c0, r0 = int((x0 - X0) / S), int((Y1 - y1) / S); c1, r1 = int((x1 - X0) / S), int((Y1 - y0) / S)
    cv2.rectangle(vis, (c0, r0), (c1, r1), kl, 2)
rect(-3.5, -348.4, 16.6, -323.6, (200, 0, 0))            # instaphal
rect(12.5, -321.75, 17.4, -316.0, (0, 150, 0))           # binnenplaats uitgang
rect(-6.8, -318.5, 12.5, -308.5, (120, 0, 160))          # laag blok koepelgebouw
rect(-73.3, -339.4, -51.8, -324.9, (120, 120, 120))      # hoog westblok
cv2.imwrite(os.path.join(D, "review", "18_routeplan.png"), cv2.resize(vis, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)[:, :, ::-1])
