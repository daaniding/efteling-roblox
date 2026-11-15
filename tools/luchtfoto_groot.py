"""Luchtfoto (PDOK Actueel_orthoHR) van een park-rechthoek, noord boven, in parkmeters.
Gebruik: python3 tools/luchtfoto_groot.py x0 y0 x1 y1 px_m uit.jpg   (park-m; x oost, y noord)"""
import sys, os, io, json, urllib.request, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__)); import geo
x0, y0, x1, y1, PX = map(float, sys.argv[1:6]); out = sys.argv[6]
cs = [geo.park_to_rd(x, y) for x in (x0, x1) for y in (y0, y1)]
rx0 = min(c[0] for c in cs) - 3; rx1 = max(c[0] for c in cs) + 3; ry0 = min(c[1] for c in cs) - 3; ry1 = max(c[1] for c in cs) + 3
tw = int((rx1 - rx0) / PX); th = int((ry1 - ry0) / PX); T = 2000
img = Image.new('RGB', (tw, th))
for ty in range(0, th, T):
    for tx in range(0, tw, T):
        w = min(T, tw - tx); h = min(T, th - ty)
        url = ("https://service.pdok.nl/hwh/luchtfotorgb/wms/v1_0?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=Actueel_orthoHR&STYLES=&CRS=EPSG:28992"
               f"&BBOX={rx0+tx*PX},{ry1-(ty+h)*PX},{rx0+(tx+w)*PX},{ry1-ty*PX}&WIDTH={w}&HEIGHT={h}&FORMAT=image/jpeg")
        img.paste(Image.open(io.BytesIO(urllib.request.urlopen(url, timeout=120).read())).convert('RGB'), (tx, ty))
A = np.asarray(img)
W = int((x1 - x0) / PX); H = int((y1 - y0) / PX)
o = np.array(geo.park_to_rd(x0, y1)); ex = np.array(geo.park_to_rd(x0 + 1, y1)) - o; ey = np.array(geo.park_to_rd(x0, y1 + 1)) - o
jj, ii = np.meshgrid(np.arange(W), np.arange(H))
px_ = (jj + 0.5) * PX; py_ = -(ii + 0.5) * PX
RX = o[0] + px_ * ex[0] + py_ * ey[0]; RY = o[1] + px_ * ex[1] + py_ * ey[1]
c = np.clip(((RX - rx0) / PX).astype(int), 0, tw - 1); r = np.clip(((ry1 - RY) / PX).astype(int), 0, th - 1)
Image.fromarray(A[r, c]).save(out, quality=92)
json.dump({'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1, 'px_m': PX, 'rij0': 'noord (y1)', 'bron': 'PDOK Actueel_orthoHR 7,5 cm'},
          open(os.path.splitext(out)[0] + '.json', 'w'))
print(W, H)
