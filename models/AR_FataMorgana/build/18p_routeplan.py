"""18p_routeplan: vaarroute en scènekamers uit de Eftepedia-plattegrond (ref/eftepedia/Plattegrondfata.jpg) naar het modelstelsel.
Daan (18 nov): "alleen ff de route maken met de kamers niet hoe ze eruit zien"; daarna: "helemaal niet de kamer indelingen".
Kaart: blauw (+ donkere randlijn, tekst, rode stippels) = vaargoot, zandkleur = scènevlakken, lichtgroen = achter de schermen
(ook de DUNNE lichtgroene lijntjes tussen zandvlakken: dat zijn scheidingsmuren tussen kamers -> raster 0,1 m, geen dichtmaken).
Kamers: elk stukje vaargoot/scène krijgt de route-afstand (langs de rode stippellijn) van het dichtstbijzijnde blauw; waar twee
plekken met meer dan SCHEID m route-afstand verschil tegen elkaar liggen (bv. sectie 4 naast 11) komt een scheidingsmuur.
Schaal 23 px/m op de plattegrond van 2479 px breed, draaischijfmidden (1935, 995) = model (6,3; -335,8), noord boven (zoals 16).
Weg: onze instaphal (sectie 15, model 16), oostelijker dan x 12,4, en alles buiten het dak (ref/route_dak.npy, 18d_dakmasker),
behalve de door kantelenmuren omsloten strook tussen hal en koepelgebouw. Erbij: doorvaarten hal-noordwest en hal-zuidwest.
Uit: ref/route_plan.npz (masker, kamer-afstand, muurlijnen, toneelranden) + review/18_routeplan.png.
Gebruik: uvx --with opencv-python-headless --with numpy python -I build/18p_routeplan.py"""
import os, numpy as np, cv2
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
im = cv2.imread(os.path.join(D, "ref", "eftepedia", "Plattegrondfata.jpg"))[:, :, ::-1].astype(int)
F = im.shape[1] / 2479.0
R_, G_, B_ = im[..., 0], im[..., 1], im[..., 2]
licht = G_ > 185                                                            # lichtgroen + achtergrond
zand_px = (R_ > 175) & (G_ > 130) & (G_ <= 185) & (B_ > 80) & (B_ < 160)
rood_px = (R_ > 170) & (G_ < 110) & (B_ < 110)
rit_px = ~licht & ~zand_px                                                  # blauw, randlijnen, tekst, stippels
SCHEID = 9.0
S = 0.1; X0, X1, Y0, Y1 = -74.0, 13.0, -352.0, -294.0
xs = np.arange(X0 + S / 2, X1, S); ys = np.arange(Y1 - S / 2, Y0, -S)               # rij 0 = noord
gx, gy = np.meshgrid(xs, ys)
def naar_px(x, y): return ((x - 6.3) * 23 + 1935) * F, ((-335.8 - y) * 23 + 995) * F
px, py = naar_px(gx, gy)
ok = (px >= 0) & (px < im.shape[1] - 1) & (py >= 0) & (py < im.shape[0] - 1)
pxi = np.clip(px.astype(int), 0, im.shape[1] - 1); pyi = np.clip(py.astype(int), 0, im.shape[0] - 1)
mb = rit_px[pyi, pxi] & ok; mz = zand_px[pyi, pxi] & ok
dpx, dpy = px / F, py / F
uit = ((gx > -3.8) & (gy < -323.3)) | (gx > 12.4) | ((dpx > 1790) & (dpy > 715)) | ((dpx > 1475) & (dpy > 1020))
dakp = os.path.join(D, "ref", "route_dak.npy")
dak = np.load(dakp)                                                         # raster 0,25 m
dak = cv2.erode(dak.astype(np.uint8), np.ones((3, 3), np.uint8))
dak = cv2.resize(dak, (mb.shape[1], mb.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
dak |= (gx > -3.0) & (gy > -323.8) & (gy < -318.4)
mb &= ~uit & dak; mz &= ~uit & dak
mb = cv2.morphologyEx(mb.astype(np.uint8), cv2.MORPH_OPEN, np.ones((4, 4), np.uint8)) > 0   # letters, dunne randlijnen weg
mb |= (gx > -3.5) & (gx < -0.3) & (gy > -323.75) & (gy < -320.5)            # doorvaart hal-noordwest -> sectie 1
mb |= (gx > -15.5) & (gx < -3.4) & (gy > -346.3) & (gy < -343.0)            # sectie 14 -> hal-zuidwest
# alleen het grote vaargootstuk; zand alleen als het aan de vaargoot grenst
n, lab, st, _ = cv2.connectedComponentsWithStats(mb.astype(np.uint8), 8); mb = lab == (1 + np.argmax(st[1:, cv2.CC_STAT_AREA]))
naast = cv2.dilate(mb.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
n2, lab2, st2, _ = cv2.connectedComponentsWithStats(mz.astype(np.uint8), 8)
houd = np.zeros_like(mz)
for i in range(1, n2):
    m = lab2 == i
    if st2[i, cv2.CC_STAT_AREA] > 150 and (m & naast).any(): houd |= m
mz = houd & ~mb
gat = ~(mz | mb); n4, lab4, st4, _ = cv2.connectedComponentsWithStats(gat.astype(np.uint8), 4)
for i in range(1, n4):
    if st4[i, cv2.CC_STAT_AREA] < 250:                                     # letters van de kaart in de scènevlakken dicht (< 2,5 m2)
        m = lab4 == i
        if (cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & mz).sum() > 0.6 * (cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~m).sum():
            mz |= m
# route-afstand: rode stippels (middellijn) op volgorde, start bij de doorvaart hal-noordwest
nr, labr, str_, cen = cv2.connectedComponentsWithStats(rood_px.astype(np.uint8), 8)
pts = []
for i in range(1, nr):
    if 6 < str_[i, cv2.CC_STAT_AREA] < 200:
        cx, cy = cen[i]; x = (cx / F - 1935) / 23 + 6.3; y = -335.8 - (cy / F - 995) / 23
        if not (x > -3.8 and y < -323.3) and x < 12.4: pts.append((x, y))
pts = np.array(pts)
start = np.argmin(np.hypot(pts[:, 0] - (-2.0), pts[:, 1] - (-322.0)))
volg = [start]; over = set(range(len(pts))) - {start}
while over:
    a = pts[volg[-1]]; j = min(over, key=lambda k: np.hypot(*(pts[k] - a)))
    if np.hypot(*(pts[j] - a)) > 6.0: break
    volg.append(j); over.remove(j)
lijn = pts[volg]; boog = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(lijn, axis=0).T))])
print("middellijn: %d stippels, lengte %.0f m" % (len(lijn), boog[-1]))
uni = mb | mz
# per cel: route-afstand van de dichtstbijzijnde stippel, gemeten vanaf het dichtstbijzijnde blauw
_, lbl = cv2.distanceTransformWithLabels((~mb).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
rb, cb = np.nonzero(mb); blauwboog = np.zeros(len(rb))
bx, by = X0 + (cb + 0.5) * S, Y1 - (rb + 0.5) * S
for i0 in range(0, len(rb), 20000):
    d = np.hypot(bx[i0:i0 + 20000, None] - lijn[None, :, 0], by[i0:i0 + 20000, None] - lijn[None, :, 1])
    blauwboog[i0:i0 + 20000] = boog[np.argmin(d, axis=1)]
idx = np.zeros(mb.shape, np.int64); idx[rb, cb] = np.arange(len(rb))
lab_naar = {}                                                             # label -> index in de blauwe lijst
zl = lbl[rb, cb]; lab_naar = dict(zip(zl.tolist(), range(len(rb))))
kaart = np.vectorize(lambda l: lab_naar.get(l, 0))(lbl)
afst = np.where(uni, blauwboog[kaart], -1.0)
# scheidingsmuren: cellen waar een buur (binnen 0,3 m) een veel andere route-afstand heeft
muur = np.zeros_like(uni)
for dr in range(-3, 4):
    for dc in range(-3, 4):
        if dr == 0 and dc == 0: continue
        sh = np.roll(np.roll(afst, dr, 0), dc, 1); u2 = np.roll(np.roll(uni, dr, 0), dc, 1)
        muur |= mz & u2 & (np.abs(afst - sh) > SCHEID) & (afst > sh)        # alleen in scènevlakken, nooit in het water
uni2 = uni & ~muur; mb2 = mb & uni2; mz2 = mz & uni2
print("vaargoot %.0f m2, scène %.0f m2, scheidingsmuur %.1f m2" % (mb2.sum() * S * S, mz2.sum() * S * S, muur.sum() * S * S))
def m2(c, r): return (X0 + (c + 0.5) * S, Y1 - (r + 0.5) * S)
def binnen(m, x, y):
    c, r = int((x - X0) / S), int((Y1 - y) / S)
    return 0 <= r < m.shape[0] and 0 <= c < m.shape[1] and m[r, c]
def randen(m, skip_hal=True, eps=1.5):
    """contourlijnen van masker m: [ax, ay, bx, by, nx, ny] met n = naar buiten (weg van m)"""
    cs, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    uitl = []
    for cnt in cs:
        if len(cnt) < 4: continue
        ap = cv2.approxPolyDP(cnt, eps, True)[:, 0, :]
        for i in range(len(ap)):
            a = np.array(m2(*ap[i])); b = np.array(m2(*ap[(i + 1) % len(ap)]))
            d = b - a; L = np.hypot(*d)
            if L < 0.05: continue
            t = d / L; nrm = np.array((-t[1], t[0])); mid = (a + b) / 2
            if skip_hal and mid[0] > -4.1 and mid[1] < -323.0: continue
            if binnen(m, *(mid + nrm * 0.25)) and not binnen(m, *(mid - nrm * 0.25)): nrm = -nrm
            uitl.append([a[0], a[1], b[0], b[1], nrm[0], nrm[1]])
    return np.array(uitl)
muren = randen(uni2)                                                     # buitenmuren + scheidingsmuren van elke kamer
toneel = randen(mz2, skip_hal=False)                                     # zijkanten van de toneelvlakken
def rects(m):
    uitr, open_ = [], {}
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
            if k not in runs: uitr.append((k[0], open_.pop(k), k[1], r))
        for k in runs:
            if k not in open_: open_[k] = r
    return np.array([[X0 + c0 * S, Y1 - r1 * S, X0 + c1 * S, Y1 - r0 * S] for (c0, r0, c1, r1) in uitr])
lichten = []
for y in np.arange(Y1 - 3, Y0, -7.0):
    for x in np.arange(X0 + 3, X1, 7.0):
        if binnen(mb2, x, y) and not (x > -4 and y < -323): lichten.append((x, y))
# grof raster (0,25 m) voor het terrein-script
g = lambda m: cv2.resize(m.astype(np.uint8), (348, 232), interpolation=cv2.INTER_AREA) > 0
np.savez_compressed(os.path.join(D, "ref", "route_plan.npz"), blauw=g(mb2), zand=g(mz2), X0=X0, Y1=Y1, S=0.25, S_fijn=S,
                    blauw_fijn=mb2, zand_fijn=mz2, r_blauw=rects(mb2), r_zand=rects(mz2), r_uni=rects(cv2.dilate(uni.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0),
                    muren=muren, toneelrand=toneel, lichten=np.array(lichten), middellijn=lijn)
print("rechthoeken: blauw %d, zand %d, plafond %d; muurlijnen %d, toneelranden %d, lichten %d" % (
    len(rects(mb2)), len(rects(mz2)), len(rects(uni)), len(muren), len(toneel), len(lichten)))
vis = np.full(mb.shape + (3,), 235, np.uint8); vis[mz2] = (205, 165, 115); vis[mb2] = (20, 120, 175); vis[muur] = (200, 30, 30)
for (x, y) in lijn[::3]:
    c, r = int((x - X0) / S), int((Y1 - y) / S); cv2.circle(vis, (c, r), 2, (250, 250, 0), -1)
cv2.imwrite(os.path.join(D, "review", "18_routeplan.png"), vis[:, :, ::-1])
