"""02_mesh: padvlakken -> driehoeksnetten per tegel (24 m) en materiaal, op het AHN-veld (zelfde veld als het Studio-terrein).
Materialen: klinker / kassei / asfalt (looplaag), kantsteen (rand 0,22 m binnen de padrand), rand (bosgrond-strook 0,8 m buiten het pad).
UV klinker/kassei: langs de dichtstbijzijnde (gladde) OSM-middellijn: u = s - v*theta(s) (rijen blijven haaks op het pad, ook in bochten),
v = afstand dwars. Pleinen (> 5 m van een lijn): vlak in wereld-meters. Kantsteen/rand: langs de padrand.
Uit: exports/paden_mesh.json (Blender-coördinaten: bx = -x_park, by = -y_park, bz = Roblox-Y / 3).  Draai met de venv (shapely)."""
import sys, os, json, math
import numpy as np
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, box, Point
from shapely.ops import unary_union, triangulate
from shapely.prepared import prep
from shapely.strtree import STRtree
import shapely
from PIL import Image, ImageDraw
from scipy import ndimage
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, os.path.join(R, 'tools')); import veld

BAND, FRINGE, CELL, TEGEL = 0.22, 0.8, 1.0, 24.0
TOP = {'klinker': 0.18, 'kassei': 0.18, 'asfalt': 0.15, 'kantsteen': 0.22}   # studs boven het maaiveld
PERIODE = {'klinker': 2.0, 'kassei': 1.8, 'asfalt': 3.0, 'kantsteen': 2.0, 'rand': 2.4}
SKIRT = 0.9 / 3   # m omlaag langs de buitenrand

d = json.load(open(os.path.join(D, 'ref_paden.json')))
VL = {k: shape(g).buffer(0).simplify(0.08).buffer(0) for k, g in d['vlakken'].items()}
U = unary_union(list(VL.values())).buffer(0.2, join_style=2).buffer(-0.2, join_style=2).buffer(0)   # naden tussen BGT-vlakken dicht
def zonder_gaatjes(g, min_opp=6.0):
    out = []
    for pg in ([g] if isinstance(g, Polygon) else list(g.geoms)):
        out.append(Polygon(pg.exterior, [h for h in pg.interiors if Polygon(h).area >= min_opp]))
    return unary_union(out)
U = zonder_gaatjes(U)
# typevlakken mee laten groeien tot U (anders kale plekjes in de gedichte naden)
rest = U.difference(unary_union(list(VL.values())))
VL['klinker'] = unary_union([VL.get('klinker', Polygon()), rest]).intersection(U).buffer(0)
Ui = U.buffer(-BAND, join_style=2).buffer(0)
# kasseien alleen op het (zij)pad met surface=sett zelf; de grens ligt langs de rand van aansluitende klinkerpaden
def _hw(line):
    return 1.5
_sett = [LineString(l['coords']) for l in d['osm_lijnen'] if l.get('surface') == 'sett' and len(l['coords']) >= 2]
_ander = [LineString(l['coords']) for l in d['osm_lijnen'] if l.get('surface') != 'sett' and l['hw'] in ('footway', 'pedestrian', 'path') and len(l['coords']) >= 2]
if _sett:
    sz = unary_union([g.buffer(3.0) for g in _sett]).intersection(U)
    # halve breedte per klinkerpad: gemeten in het BGT-vlak (afstand tot de rand), anders 1,5 m
    hulp = []
    for g in _ander:
        sp = [g.interpolate(t) for t in np.arange(0, g.length, 1.0)]
        dd = [U.exterior.distance(q) if isinstance(U, Polygon) else U.boundary.distance(q) for q in sp[:40]]
        hw = float(np.clip(np.percentile(dd, 80) + 0.2, 1.0, 5.0)) if dd else 1.5
        hulp.append(g.buffer(hw))
    ks = sz.difference(unary_union(hulp)).buffer(-0.1).buffer(0.1) if hulp else sz
    allp = unary_union([VL.get('klinker', Polygon()), VL.get('kassei', Polygon())])
    VL['kassei'] = ks.intersection(allp).buffer(0); VL['klinker'] = allp.difference(VL['kassei']).buffer(0)
SURF = {k: v.intersection(Ui).buffer(0) for k, v in VL.items()}
SURF['kantsteen'] = U.difference(Ui).buffer(0)
SURF['rand'] = U.buffer(FRINGE).difference(U).buffer(0)

# --- afstand tot de padrand (raster 0,1 m) voor bolling en rand-v
minx, miny, maxx, maxy = U.buffer(FRINGE + 1).bounds; RS = 0.1
W = int((maxx - minx) / RS) + 1; H = int((maxy - miny) / RS) + 1
mk = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mk)
def polys(g): return [g] if isinstance(g, Polygon) else [p for p in getattr(g, 'geoms', []) if isinstance(p, Polygon)]
Q = lambda c: ((c[0] - minx) / RS, (maxy - c[1]) / RS)
for pg in polys(U):
    md.polygon([Q(c) for c in pg.exterior.coords], fill=1)
    for h in pg.interiors: md.polygon([Q(c) for c in h.coords], fill=0)
M = np.asarray(mk).astype(bool)
DIN = ndimage.distance_transform_edt(M) * RS; DUIT = ndimage.distance_transform_edt(~M) * RS
def afst(x, y, binnen=True):
    j = np.clip(((x - minx) / RS).astype(int), 0, W - 1); i = np.clip(((maxy - y) / RS).astype(int), 0, H - 1)
    return (DIN if binnen else DUIT)[i, j]

# --- gladde middellijnen
def chaikin(c, n=3):
    c = np.asarray(c, float)
    for _ in range(n):
        if len(c) < 3: break
        q = 0.75 * c[:-1] + 0.25 * c[1:]; r = 0.25 * c[:-1] + 0.75 * c[1:]
        c = np.vstack([c[:1], np.column_stack([q, r]).reshape(-1, 2), c[-1:]])
    return c
# --- OSM-stukken die in elkaars verlengde liggen samenvoegen tot doorlopende paden (anders springt het verband bij elke knip)
WEGEN = [np.asarray(l['coords'], float) for l in d['osm_lijnen'] if len(l['coords']) >= 2]
eind = {}
for i, c in enumerate(WEGEN):
    for e, (p, q) in enumerate(((c[0], c[1]), (c[-1], c[-2]))):
        dv = q - p; n = np.hypot(*dv)
        if n < 1e-6: continue
        eind.setdefault((round(p[0], 2), round(p[1], 2)), []).append((i, e, dv / n))
link = {}
for key, ends in eind.items():
    paren = sorted(((float(np.dot(a[2], b[2])), a, b) for ai, a in enumerate(ends) for b in ends[ai + 1:] if a[0] != b[0]), key=lambda t: t[0])
    vrij = set((a[0], a[1]) for a in ends)
    for dot, a, b in paren:
        if dot > -0.75: break                       # alleen doorlopen als de bocht < ~40 graden is
        if (a[0], a[1]) in vrij and (b[0], b[1]) in vrij:
            link[(a[0], a[1])] = (b[0], b[1]); link[(b[0], b[1])] = (a[0], a[1]); vrij -= {(a[0], a[1]), (b[0], b[1])}
gezien = set(); KETENS = []
for i in range(len(WEGEN)):
    if i in gezien: continue
    # terug naar het begin van de keten
    cur, e = i, 0; stap = 0
    while (cur, e) in link and stap < 500:
        j, ej = link[(cur, e)]
        if j == i: break
        cur, e = j, 1 - ej; stap += 1
    # vooruit opbouwen; (cur, e) = begin-uiteinde van de eerste weg
    pts = []; stap = 0
    while cur not in gezien and stap < 500:
        gezien.add(cur); c = WEGEN[cur] if e == 0 else WEGEN[cur][::-1]
        pts += list(c if not pts else c[1:])
        nxt = link.get((cur, 1 - e))
        if not nxt: break
        cur, e = nxt; stap += 1
    KETENS.append(np.array(pts))
print('osm-wegen', len(WEGEN), '-> doorlopende paden', len(KETENS))
LIJN = []
for c in KETENS:
    c = chaikin(c)
    seg = np.diff(c, axis=0); L = np.hypot(seg[:, 0], seg[:, 1]); ok = L > 1e-6
    c = np.vstack([c[:1], c[1:][ok]]); seg = np.diff(c, axis=0); L = np.hypot(seg[:, 0], seg[:, 1])
    if len(L) == 0: continue
    s = np.concatenate([[0], np.cumsum(L)]); ang = np.unwrap(np.arctan2(seg[:, 1], seg[:, 0]))
    th = np.concatenate([[0], np.cumsum(np.diff(ang))]) if len(ang) > 1 else np.zeros(1)
    thv = np.concatenate([[th[0]], (th[:-1] + th[1:]) / 2 if len(th) > 1 else [], [th[-1]]])
    g = LineString(c)
    sp = shapely.get_coordinates(shapely.line_interpolate_point(g, np.arange(0, g.length, 0.5)))
    din = afst(sp[:, 0], sp[:, 1]) if len(sp) else np.zeros(1)
    din = din[din > 0]
    h = float(np.clip(np.percentile(din, 90) + 0.4, 1.0, 6.0)) if len(din) else 1.5   # halve padbreedte rond deze lijn
    LIJN.append({'geom': g, 's': s, 'th': thv, 'ang': ang, 'c': c, 'h': h, 'L': g.length})
# --- vloeiend verbandveld: richting = gewogen gemiddelde van de (gericht gemaakte) middellijnen, daarna u/v via Poisson (kleinste kwadraten)
#     zodat het halfsteensverband overal doorloopt en bij vorken/kruisingen geleidelijk uitwaaiert (geen harde naden).
from scipy.sparse import coo_matrix, vstack as svstack, identity
from scipy.sparse.linalg import lsqr
# richting van elke keten afstemmen op de keten waar hij op aansluit (langste eerst)
volg = sorted(range(len(LIJN)), key=lambda k: -LIJN[k]['L']); gericht = {volg[0]}
def tang(li, pt):
    g = LIJN[li]['geom']; s0 = g.project(Point(pt)); a = g.interpolate(max(s0 - 0.5, 0)); b = g.interpolate(min(s0 + 0.5, g.length))
    v = np.array([b.x - a.x, b.y - a.y]); return v / (np.hypot(*v) + 1e-9)
veranderd = True
while veranderd:
    veranderd = False
    for li in volg:
        if li in gericht: continue
        c = LIJN[li]['c']
        for e, pt in ((0, c[0]), (1, c[-1])):
            for lj in gericht:
                if LIJN[lj]['geom'].distance(Point(pt)) < 1.5:
                    ta = tang(lj, pt); tb = tang(li, pt)
                    if float(np.dot(ta, tb)) < 0:   # omdraaien
                        l = LIJN[li]; l['c'] = l['c'][::-1]; l['geom'] = LineString(l['c'])
                    gericht.add(li); veranderd = True; break
            if li in gericht: break
RS2 = 0.25
W2 = int((maxx - minx) / RS2) + 1; H2 = int((maxy - miny) / RS2) + 1
ii2, jj2 = np.mgrid[0:H2, 0:W2]
M2 = M[np.clip(((ii2 + 0.5) * RS2 / RS).astype(int), 0, H - 1), np.clip(((jj2 + 0.5) * RS2 / RS).astype(int), 0, W - 1)]
TX = np.zeros((H2, W2)); TY = np.zeros((H2, W2)); WT = np.zeros((H2, W2))
for l in LIJN:
    g = l['geom']; ss = np.arange(0, g.length, 0.2)
    if len(ss) < 2: continue
    q = shapely.get_coordinates(shapely.line_interpolate_point(g, ss)); dq = np.gradient(q, axis=0); dq /= (np.hypot(dq[:, 0], dq[:, 1])[:, None] + 1e-9)
    ri = np.clip(((maxy - q[:, 1]) / RS2).astype(int), 0, H2 - 1); ci = np.clip(((q[:, 0] - minx) / RS2).astype(int), 0, W2 - 1)
    np.add.at(TX, (ri, ci), dq[:, 0]); np.add.at(TY, (ri, ci), dq[:, 1]); np.add.at(WT, (ri, ci), 1)
def glad(sig):
    a = ndimage.gaussian_filter(TX, sig / RS2); b = ndimage.gaussian_filter(TY, sig / RS2); w = ndimage.gaussian_filter(WT, sig / RS2)
    return a, b, w
a1, b1, w1 = glad(1.5); a2, b2, w2 = glad(6.0)
mix = np.clip(w1 / (w1.max() * 0.02 + 1e-12), 0, 1)
FX = a1 * mix + a2 * (1 - mix) * (w1.max() / (w2.max() + 1e-12)); FY = b1 * mix + b2 * (1 - mix) * (w1.max() / (w2.max() + 1e-12))
nrm = np.hypot(FX, FY) + 1e-12; FX /= nrm; FY /= nrm
# brede pleinen (> ~6 m breed): één rechte verbandrichting langs de lange as van het plein, zacht overgaand naar de padrichting
DIN2 = DIN[np.clip(((ii2 + 0.5) * RS2 / RS).astype(int), 0, H - 1), np.clip(((jj2 + 0.5) * RS2 / RS).astype(int), 0, W - 1)]
breed = ndimage.binary_dilation(DIN2 > 3.0, iterations=int(4 / RS2)) & M2
lab, nlab = ndimage.label(breed)
PX = np.zeros((H2, W2)); PY = np.zeros((H2, W2))
for k in range(1, nlab + 1):
    sel = lab == k
    if sel.sum() < 200: continue
    yy, xx = np.nonzero(sel); pts = np.column_stack([xx * RS2, -yy * RS2]); pts -= pts.mean(0)
    ev, evec = np.linalg.eigh(np.cov(pts.T)); ax = evec[:, np.argmax(ev)]
    if float((FX[sel] * ax[0] + FY[sel] * ax[1]).sum()) < 0: ax = -ax
    PX[sel] = ax[0]; PY[sel] = ax[1]
sw = ndimage.gaussian_filter(np.clip((DIN2 - 2.5) / 2.0, 0, 1) * (np.hypot(PX, PY) > 0), 2.0 / RS2)
FX = FX * (1 - sw) + PX * sw; FY = FY * (1 - sw) + PY * sw
nrm = np.hypot(FX, FY) + 1e-12; FX /= nrm; FY /= nrm
idx = -np.ones((H2, W2), int); idx[M2] = np.arange(M2.sum()); N2 = int(M2.sum())
def poisson(gx, gy):
    rows, cols, vals, b = [], [], [], []; r = 0
    # horizontaal: kolom j -> x
    m = M2[:, :-1] & M2[:, 1:]; I, J = np.nonzero(m)
    k = np.arange(len(I)) + r; rows += [k, k]; cols += [idx[I, J + 1], idx[I, J]]; vals += [np.ones(len(I)), -np.ones(len(I))]
    b.append(RS2 * (gx[I, J] + gx[I, J + 1]) / 2); r += len(I)
    # verticaal: rij i -> -y
    m = M2[:-1, :] & M2[1:, :]; I, J = np.nonzero(m)
    k = np.arange(len(I)) + r; rows += [k, k]; cols += [idx[I + 1, J], idx[I, J]]; vals += [np.ones(len(I)), -np.ones(len(I))]
    b.append(-RS2 * (gy[I, J] + gy[I + 1, J]) / 2); r += len(I)
    A = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(r, N2)).tocsr()
    A = svstack([A, identity(N2, format='csr') * 1e-3]); bb = np.concatenate(b + [np.zeros(N2)])
    x = lsqr(A, bb, atol=1e-7, btol=1e-7, iter_lim=6000)[0]
    out = np.zeros((H2, W2)); out[M2] = x
    # buiten het masker: dichtstbijzijnde waarde (randpunten van driehoeken)
    _, (ri, ci) = ndimage.distance_transform_edt(~M2, return_indices=True); return out[ri, ci]
UFLD = poisson(FX, FY); VFLD = poisson(-FY, FX)
def veld_uv(P):
    fi = (maxy - P[:, 1]) / RS2 - 0.5; fj = (P[:, 0] - minx) / RS2 - 0.5
    return ndimage.map_coordinates(UFLD, [fi, fj], order=1, mode='nearest'), ndimage.map_coordinates(VFLD, [fi, fj], order=1, mode='nearest')
print('verbandveld klaar', N2, 'pixels')
TREE = STRtree([l['geom'] for l in LIJN])
RINGS = []
for pg in polys(U):
    RINGS.append(LineString(pg.exterior.coords))
    for h in pg.interiors: RINGS.append(LineString(h.coords))
RTREE = STRtree(RINGS)

def lijn_uv(li, P):
    """P: (n,2) -> (u, v) langs lijn li."""
    l = LIJN[li]; g = l['geom']; pts = shapely.points(P)
    s = shapely.line_locate_point(g, pts)
    q = shapely.get_coordinates(shapely.line_interpolate_point(g, s))
    k = np.clip(np.searchsorted(l['s'], s, side='right') - 1, 0, len(l['ang']) - 1)
    a = l['ang'][k]; t = np.column_stack([np.cos(a), np.sin(a)])
    rel = P - q; v = t[:, 0] * rel[:, 1] - t[:, 1] * rel[:, 0]
    # buiten het lijnstuk (s op 0 of L): ook langs-component meenemen
    along = (rel * t).sum(1); s = s + np.where((s <= 1e-6) | (s >= l['s'][-1] - 1e-6), along, 0)
    th = np.interp(s, l['s'], l['th'])
    return s - v * th, v

def tri_vlak(poly, cell):
    """Driehoeken (lijst van 3x2) die poly bedekken: raster + knippen aan de rand."""
    out = []; pp = prep(poly)
    x0, y0, x1, y1 = poly.bounds
    for gx in np.arange(math.floor(x0 / cell) * cell, x1, cell):
        for gy in np.arange(math.floor(y0 / cell) * cell, y1, cell):
            c = box(gx, gy, gx + cell, gy + cell)
            if not pp.intersects(c): continue
            if pp.contains(c):
                a, b, cc, dd = (gx, gy), (gx + cell, gy), (gx + cell, gy + cell), (gx, gy + cell)
                out += [(a, b, cc), (a, cc, dd)]; continue
            piece = c.intersection(poly)
            for pg in polys(piece):
                if pg.area < 1e-4: continue
                ext = list(pg.exterior.coords)[:-1]
                if not pg.interiors and Polygon(ext).convex_hull.area - pg.area < 1e-6:
                    for i in range(1, len(ext) - 1): out.append((ext[0], ext[i], ext[i + 1]))
                else:
                    for t in triangulate(pg):
                        if pg.contains(t.representative_point()):
                            out.append(tuple(t.exterior.coords)[:3])
    return out

res = {}
for mat, geom in SURF.items():
    if geom.is_empty: continue
    T = np.array(tri_vlak(geom, CELL if mat in TOP and mat != 'kantsteen' else 2.5), dtype=float)      # (n,3,2)
    if len(T) == 0: continue
    # tegen de klok in (bovenkant omhoog)
    cr = (T[:, 1, 0] - T[:, 0, 0]) * (T[:, 2, 1] - T[:, 0, 1]) - (T[:, 1, 1] - T[:, 0, 1]) * (T[:, 2, 0] - T[:, 0, 0])
    T[cr < 0] = T[cr < 0][:, [0, 2, 1]]
    T = T[np.abs(cr) > 1e-8]
    C = T.mean(1); P = T.reshape(-1, 2)
    # hoogte
    Y = veld.maaiveld_studs(P[:, 0], P[:, 1])
    if mat in TOP:
        Y = Y + TOP[mat]
        if mat in ('klinker', 'kassei', 'asfalt'): Y = Y + 0.075 * np.minimum(afst(P[:, 0], P[:, 1]) / 1.5, 1)   # bolling 2,5 cm
    else:   # rand: van +0,10 aan de padkant naar +0,03 buiten
        Y = Y + 0.10 - 0.07 * np.clip(afst(P[:, 0], P[:, 1], False) / FRINGE, 0, 1)
    # UV
    UV = np.zeros((len(P), 2))
    if mat in ('klinker', 'kassei'):
        u, v = veld_uv(P); per = PERIODE[mat]
        UV = np.column_stack([v / per, u / per])
    elif mat == 'asfalt':
        UV = P / PERIODE[mat]
    else:   # kantsteen / rand: langs de padrand
        near = RTREE.query_nearest(shapely.points(C))
        own = np.zeros(len(T), int); own[near[0]] = near[1]
        for ri in np.unique(own):
            sel = np.where(own == ri)[0]; ps = T[sel].reshape(-1, 2); ring = RINGS[ri]
            u = shapely.line_locate_point(ring, shapely.points(ps)).reshape(-1, 3)
            Lr = ring.length
            span = u.max(1) - u.min(1); wrap = span > Lr / 2
            u[wrap] = np.where(u[wrap] < Lr / 2, u[wrap] + Lr, u[wrap])
            dv = (afst(ps[:, 0], ps[:, 1], True) / BAND) if mat == 'kantsteen' else (afst(ps[:, 0], ps[:, 1], False) / FRINGE)
            UV[np.repeat(sel * 3, 3) + np.tile([0, 1, 2], len(sel))] = np.column_stack([u.reshape(-1) / PERIODE[mat], np.clip(dv, 0, 1)])
    # tegels
    tid = np.floor(C / TEGEL).astype(int)
    for key in set(map(tuple, tid)):
        sel = np.where((tid[:, 0] == key[0]) & (tid[:, 1] == key[1]))[0]
        k = f"{mat}_{key[0]}_{key[1]}"
        res[k] = {'mat': mat, 'tegel': [int(key[0]), int(key[1])],
                  'tri': np.round(np.column_stack([-T[sel].reshape(-1, 2)[:, 0], -T[sel].reshape(-1, 2)[:, 1], Y.reshape(-1, 3)[sel].reshape(-1) / 3]), 3).tolist(),
                  'uv': np.round(UV.reshape(-1, 3, 2)[sel].reshape(-1, 2), 4).tolist()}
    print(mat, len(T), 'driehoeken')
# rokken langs de buitenrand van de kantsteen (verticaal omlaag)
sk = []
for ring in RINGS:
    c = np.asarray(ring.coords)
    for a, b in zip(c[:-1], c[1:]):
        L = math.dist(a, b); n = max(1, int(L / 1.0))
        for i in range(n):
            p0 = a + (b - a) * i / n; p1 = a + (b - a) * (i + 1) / n
            sk.append((p0, p1))
sk = np.array(sk)
if len(sk):
    y0 = veld.maaiveld_studs(sk[:, 0, 0], sk[:, 0, 1]) + TOP['kantsteen']; y1 = veld.maaiveld_studs(sk[:, 1, 0], sk[:, 1, 1]) + TOP['kantsteen']
    C = sk.mean(1); tid = np.floor(C / TEGEL).astype(int)
    for key in set(map(tuple, tid)):
        sel = np.where((tid[:, 0] == key[0]) & (tid[:, 1] == key[1]))[0]
        tri = []; uv = []
        for i in sel:
            (ax, ay), (bx, by) = sk[i]
            dx, dy_ = bx - ax, by - ay; Ln = math.hypot(dx, dy_) or 1
            mx, my = (ax + bx) / 2 - dy_ / Ln * 0.15, (ay + by) / 2 + dx / Ln * 0.15   # punt links van a->b
            if not afst(np.array([mx]), np.array([my]))[0] > 0:   # pad ligt rechts: omdraaien zodat de normaal naar buiten wijst
                (ax, ay), (bx, by) = (bx, by), (ax, ay); ta, tb = y1[i] / 3, y0[i] / 3
            else: ta, tb = y0[i] / 3, y1[i] / 3
            A = (-ax, -ay, ta); B = (-bx, -by, tb); A2 = (-ax, -ay, ta - SKIRT); B2 = (-bx, -by, tb - SKIRT)
            tri += [A, A2, B2, A, B2, B]; uv += [(0, 1), (0, 0), (0.1, 0), (0, 1), (0.1, 0), (0.1, 1)]
        k = f"kantsteen_{key[0]}_{key[1]}"
        res.setdefault(k, {'mat': 'kantsteen', 'tegel': [int(key[0]), int(key[1])], 'tri': [], 'uv': []})
        res[k]['tri'] += np.round(np.array(tri), 3).tolist(); res[k]['uv'] += uv
os.makedirs(os.path.join(D, 'exports'), exist_ok=True)
json.dump(res, open(os.path.join(D, 'exports', 'paden_mesh.json'), 'w'))
print('stukken', len(res), 'max driehoeken', max(len(v['tri']) // 3 for v in res.values()))
