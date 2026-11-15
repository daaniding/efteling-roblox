"""heuvels: v1-heuvels/plateaus uit Studio (reference/ahn_sprookjesbos/heuvels_studio.txt) als hoogte-aanvulling op het AHN-veld.
Gemeten in Studio (15 nov 2026): terreinhoogte op een raster van 3 stud naast de paden ('x' = onder/bij een pad, niet gemeten).
pas_toe(f) geeft een functie terug die f (veld.maaiveld_studs, park-m -> stud) aanvult: binnen een gebied wordt de hoogte
max(AHN, heuvel), met een overgang van 9 stud aan de rand van het gebied. Zo loopt een pad over de heuvel in plaats van erdoorheen."""
import os
import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BESTAND = os.path.join(R, 'reference', 'ahn_sprookjesbos', 'heuvels_studio.txt')
RAND = 9.0   # stud overgang aan de rand van een gebied


def lees():
    gebieden = []
    for blok in open(BESTAND).read().split('#'):
        regels = [r for r in blok.strip().splitlines() if r.strip()]
        if not regels: continue
        naam, x0, z0, st = regels[0].split('|'); x0, z0, st = float(x0), float(z0), float(st)
        pts, hs = [], []
        rij = [r.split(',') for r in regels[1:]]
        for j, r in enumerate(rij):
            for i, v in enumerate(r):
                if v != 'x': pts.append((x0 + i * st, z0 + j * st)); hs.append(float(v))
        nz, nx = len(rij), max(len(r) for r in rij)
        pts = np.array(pts); hs = np.array(hs)
        lin = LinearNDInterpolator(pts, hs); nn = NearestNDInterpolator(pts, hs)
        gx = np.arange(x0, x0 + (nx - 1) * st + 1e-6, 1.0); gz = np.arange(z0, z0 + (nz - 1) * st + 1e-6, 1.0)
        GX, GZ = np.meshgrid(gx, gz); GH = lin(GX, GZ); leeg = np.isnan(GH); GH[leeg] = nn(GX[leeg], GZ[leeg])
        from scipy.ndimage import gaussian_filter
        GH = gaussian_filter(GH, 6.0, mode='nearest')   # gladgestreken (sigma 6 stud): geen knikken in het pad
        from scipy.interpolate import RegularGridInterpolator
        rg = RegularGridInterpolator((gz, gx), GH, bounds_error=False, fill_value=None)
        gebieden.append({'naam': naam, 'X0': x0, 'X1': x0 + (nx - 1) * st, 'Z0': z0, 'Z1': z0 + (nz - 1) * st,
                         'lin': lambda X, Z, rg=rg: rg(np.column_stack([Z, X])), 'nn': nn})
    return gebieden


GEBIEDEN = lees()


def heuvel(X, Z):
    """Roblox X, Z (stud) -> (hoogte, gewicht 0..1); gewicht 0 buiten alle gebieden."""
    X = np.asarray(X, float); Z = np.asarray(Z, float)
    H = np.full(X.shape, -1e9); W = np.zeros(X.shape)
    for g in GEBIEDEN:
        binnen = (X >= g['X0']) & (X <= g['X1']) & (Z >= g['Z0']) & (Z <= g['Z1'])
        if not binnen.any(): continue
        h = g['lin'](X[binnen], Z[binnen]); leeg = np.isnan(h)
        if leeg.any(): h[leeg] = g['nn'](X[binnen][leeg], Z[binnen][leeg])
        d = np.minimum.reduce([X[binnen] - g['X0'], g['X1'] - X[binnen], Z[binnen] - g['Z0'], g['Z1'] - Z[binnen]])
        w = np.clip(d / RAND, 0, 1)
        beter = w > W[binnen]
        Hb = H[binnen]; Wb = W[binnen]; Hb[beter] = h[beter]; Wb[beter] = w[beter]; H[binnen] = Hb; W[binnen] = Wb
    return H, W


MAX_OP = 1e9   # Daan: pad over de heuvel (een grens hier liet het padennet uiteenvallen bij het Zwavelstokjes-plateau)


def steil_vlak(f, stap=1.5):
    """Shapely-vlak (park-m) waar de heuvel meer dan MAX_OP boven het AHN-veld uitsteekt: daar geen pad (v1-trappen/plateau)."""
    from shapely.geometry import box
    from shapely.ops import unary_union
    vakken = []
    for g in GEBIEDEN:
        xs = np.arange(g['X0'], g['X1'] + 1e-6, stap); zs = np.arange(g['Z0'], g['Z1'] + 1e-6, stap)
        X, Z = np.meshgrid(xs, zs); H, W = heuvel(X.ravel(), Z.ravel())
        basis = np.asarray(f(X.ravel() / 3, -Z.ravel() / 3), float)
        hoog = (W > 0.5) & (H - basis > MAX_OP)
        for x_, z_ in zip(X.ravel()[hoog], Z.ravel()[hoog]):
            px, py = x_ / 3, -z_ / 3; h = stap / 6
            vakken.append(box(px - h, py - h, px + h, py + h))
    return unary_union(vakken).buffer(0.6).buffer(-0.3) if vakken else None


def pas_toe(f):
    def g(x, y):
        x = np.asarray(x, float); y = np.asarray(y, float)
        basis = np.asarray(f(x, y), float)
        H, W = heuvel(3 * x, -3 * y)
        return basis + W * np.clip(H - basis, 0.0, MAX_OP)
    return g
