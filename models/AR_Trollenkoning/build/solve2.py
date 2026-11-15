import math, sys, numpy as np
from scipy.optimize import least_squares
def mk(W, H, SENS):
    def proj(c, P):
        x, y, z, yaw, pitch, lens = c; f = lens / SENS * H
        d = np.array(P) - np.array([x, y, z])
        fw = np.array([-math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), math.sin(pitch)]); rt = np.array([math.cos(yaw), math.sin(yaw), 0.0]); up = np.cross(rt, fw)
        zc = d @ fw; return np.array([W / 2 + f * (d @ rt) / zc, H / 2 - f * (d @ up) / zc])
    def ray(c, px, py, zg=0.0):
        x, y, z, yaw, pitch, lens = c; f = lens / SENS * H
        fw = np.array([-math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), math.sin(pitch)]); rt = np.array([math.cos(yaw), math.sin(yaw), 0.0]); up = np.cross(rt, fw)
        d = fw + rt * (px - W / 2) / f - up * (py - H / 2) / f; t = (zg - z) / d[2]; return np.round(np.array([x, y]) + t * d[:2], 2)
    return proj, ray
def solve(proj, pts, guess):
    res = lambda c: np.concatenate([proj(c, P) - np.array(p) for P, p in pts])
    best = None
    for yaw in np.radians(np.arange(-70, 71, 10)):
        for d in (7, 10, 14):
            g = [-d * math.sin(-yaw) * -1 if False else d * math.sin(yaw) * -1 * -1, -d * math.cos(yaw), 1.5, yaw, 0.1, guess]
            g = [-(-d * math.sin(yaw)), -d * math.cos(yaw), 1.5, yaw, 0.1, guess]
            try: r = least_squares(res, g, bounds=([-40, -40, 0.3, -3.2, -0.6, 8], [40, 40, 6, 3.2, 0.8, 120]))
            except Exception: continue
            if best is None or r.cost < best.cost: best = r
    return best.x, res(best.x)
