"""Fotocamera oplossen uit grondpunten (bekende plattegrond), daarna hoogtes terugrekenen langs verticale lijnen.
Blender-conventie zoals cam_match.py: camera kijkt langs (-sin yaw, cos yaw), pitch omhoog, sensor verticaal."""
import math, sys, json
import numpy as np
from scipy.optimize import least_squares
W, H, LENS, SENS = 1100, 733, 8.8, 8.8
f = LENS / SENS * H     # px
def proj(cam, P):
    x, y, z, yaw, pitch = cam
    d = np.array(P) - np.array([x, y, z])
    fw = np.array([-math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), math.sin(pitch)])
    rt = np.array([math.cos(yaw), math.sin(yaw), 0.0])
    up = np.cross(rt, fw)
    zc = d @ fw; return np.array([W / 2 + f * (d @ rt) / zc, H / 2 - f * (d @ up) / zc])
XL, XR, YF, YB, PX0, PY0, PY1 = -1.45, 2.62, -2.35, 2.35, -2.2, 1.15, 2.45
G = [((XL - 0.1, YF - 0.1, 0), (640, 555)), ((PX0 - 0.1, PY1, 0), (402, 547)), ((XR + 0.1, YF - 0.1, 0), (700, 551)), ((XL - 0.1, PY0, 0), (475, 551))]
def res(c):
    cam = [c[0], c[1], 1.55, c[2], c[3]]
    return np.concatenate([proj(cam, P) - np.array(p) for P, p in G])
best = None
for yaw0 in np.radians(np.arange(-90, -20, 10)):
    for d in (8, 12, 16, 20):
        x0 = [-d * math.sin(-yaw0) * 1, -d * math.cos(yaw0), yaw0, 0.05]
        r = least_squares(res, x0)
        if best is None or r.cost < best.cost: best = r
c = best.x; cam = [c[0], c[1], 1.55, c[2], c[3]]
print("camera x %.2f y %.2f yaw %.1f pitch %.1f  rest(px)" % (c[0], c[1], math.degrees(c[2]), math.degrees(c[3])), np.round(res(c), 1))
def hoogte(x, y, py):
    lo, hi = -5, 30
    for _ in range(60):
        m = (lo + hi) / 2
        if proj(cam, (x, y, m))[1] > py: lo = m
        else: hi = m
    return (lo + hi) / 2
Q = {"kroonlijst-hoek (640,280)": (XL, YF, 280), "raam top (577,369)": (XL, -1.2, 369), "raam onder (577,497)": (XL, -1.2, 497),
     "pijler verspringing (402,342)": (PX0, PY1, 342), "koperkap top (402,305)": (PX0, PY1, 305), "schoorsteen kap top (415,147)": (-1.95, PY1, 147),
     "geveltop (670,122)": ((XL + XR) / 2, YF, 122), "deur top (680,352)": ((XL + XR) / 2 + 0.5, YF, 352)}
for k, (x, y, py) in Q.items(): print(k, "z = %.2f" % hoogte(x, y, py))
for k, P in (("raam links y?", None),): pass
# raam-randen in y: zoek y op de zijgevel waar x-pixel 486 / 577 valt (z 2)
for px in (486, 577, 640):
    lo, hi = -3, 3
    for _ in range(60):
        m = (lo + hi) / 2
        if proj(cam, (XL, m, 2.0))[0] < px: hi = m
        else: lo = m
    print("zijgevel pixel x", px, "-> y = %.2f" % ((lo + hi) / 2))
json.dump({"cam": cam}, open(sys.argv[1] if len(sys.argv) > 1 else "/dev/null", "w"))
