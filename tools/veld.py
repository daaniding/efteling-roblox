"""Het AHN-verschuivingsveld zoals het in Studio staat (ServerStorage.AHN_Delta.Veld), voor Python.
dy(X, Z) in studs; maaiveld in Studio = 2 + dy.  maaiveld_m(x, y) = maaiveld in Roblox-studs voor parkmeters.
Bron: reference/ahn_sprookjesbos/delta_8studs_rle.txt (zelfde codering/rooster als in Studio)."""
import os
import numpy as np

X0, Z0, C, NX, NZ = -280, -796, 8, 117, 145
_B = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
_I = {c: i for i, c in enumerate(_B)}


def _laad():
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reference', 'ahn_sprookjesbos', 'delta_8studs_rle.txt')
    G = []
    for line in open(p).read().split('\n'):
        if not line: continue
        row = []; prev = 500; k = 0
        while k < len(line):
            if line[k] == '!':
                v = _I[line[k + 1]] * 64 + _I[line[k + 2]]; n = _I[line[k + 3]]
                row += [v] * n; prev = v; k += 4
            else:
                prev = prev + _I[line[k]] - 32; row.append(prev); k += 1
        G.append(row)
    G = (np.array(G, dtype=np.float64) - 500) / 10
    assert G.shape == (NZ, NX), G.shape
    return G


G = _laad()


def dy(X, Z):
    """Vectorized: X, Z (studs) -> dy (studs). Buiten het rooster 0 (zoals in Studio)."""
    X = np.asarray(X, dtype=np.float64); Z = np.asarray(Z, dtype=np.float64)
    u = (X - X0) / C; v = (Z - Z0) / C
    buiten = (u < 0) | (v < 0) | (u > NX - 1) | (v > NZ - 1)
    u = np.clip(u, 0, NX - 1); v = np.clip(v, 0, NZ - 1)
    i = np.floor(u).astype(int); j = np.floor(v).astype(int); fu = u - i; fv = v - j
    i1 = np.minimum(i + 1, NX - 1); j1 = np.minimum(j + 1, NZ - 1)
    r = (G[j, i] * (1 - fu) + G[j, i1] * fu) * (1 - fv) + (G[j1, i] * (1 - fu) + G[j1, i1] * fu) * fv
    return np.where(buiten, 0.0, r)


def maaiveld_studs(x, y):
    """Parkmeters -> Roblox Y (studs) van het maaiveld."""
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    return 2.0 + dy(x * 3.0, -y * 3.0)
