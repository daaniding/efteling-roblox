import sys, numpy as np
from PIL import Image
d = sys.argv[1]
dtm = np.array(Image.open(f"{d}/dtm_05m.tif"), dtype=np.float32)
dsm = np.array(Image.open(f"{d}/dsm_05m.tif"), dtype=np.float32)
bad = (dtm > 1e30) | (dtm < -100)
print('dtm gaten %', round(bad.mean()*100, 1))
# gaten (onder gebouwen/bomen) vullen met dichtstbijzijnde via iteratief gemiddelde
f = dtm.copy(); f[bad] = np.nan
for _ in range(200):
    if not np.isnan(f).any(): break
    p = np.pad(f, 1, mode='edge'); nb = np.stack([p[:-2,1:-1], p[2:,1:-1], p[1:-1,:-2], p[1:-1,2:]])
    m = np.nanmean(nb, axis=0); f = np.where(np.isnan(f), m, f)
v = f[~np.isnan(f)]
print('maaiveld m NAP: min %.2f  max %.2f  p5 %.2f  p95 %.2f' % (v.min(), v.max(), *np.percentile(v, [5, 95])))
s = dsm.copy(); s[(s > 1e30) | (s < -100)] = np.nan
chm = s - f
print('hoogte boven maaiveld p50/p90/max: %.1f %.1f %.1f' % tuple(np.nanpercentile(chm, [50, 90, 99.9])))
# bomen: lokale maxima > 6 m in 5x5 m venster
from numpy.lib.stride_tricks import sliding_window_view as swv
c = np.nan_to_num(chm, nan=0); k = 9
pad = np.pad(c, k//2, mode='constant'); mx = swv(pad, (k, k)).max(axis=(2, 3))
tops = (c == mx) & (c > 6)
print('boomtoppen (>6 m, venster 4.5 m):', int(tops.sum()))
# hillshade + hoogtekleur
gy, gx = np.gradient(f, 0.5)
sl = np.pi/2 - np.arctan(np.hypot(gx, gy)*3); asp = np.arctan2(-gx, gy)
az, alt = np.radians(315), np.radians(45)
hs = np.sin(alt)*np.sin(sl) + np.cos(alt)*np.cos(sl)*np.cos(az - asp)
n = (f - np.percentile(v, 1)) / (np.percentile(v, 99) - np.percentile(v, 1)); n = np.clip(n, 0, 1)
rgb = np.stack([0.2+0.8*n, 0.55+0.25*(1-abs(n-0.5)*2), 1-0.8*n], -1) * (0.45+0.55*np.clip(hs, 0, 1))[..., None]
img = (np.clip(rgb, 0, 1)*255).astype(np.uint8)
Image.fromarray(img).save(f"{d}/maaiveld_hillshade.png")
np.save(f"{d}/dtm_gevuld.npy", f); np.save(f"{d}/chm.npy", chm)
