import sys, math, xml.etree.ElementTree as ET, urllib.request
src, outdir = sys.argv[1], sys.argv[2]
def wgs_to_rd(lat, lon):
    dphi = 0.36*(lat-52.15517440); dlam = 0.36*(lon-5.38720621)
    x = 155000 + 190094.945*dlam - 11832.228*dphi*dlam - 114.221*dphi**2*dlam - 32.391*dlam**3 - 0.705*dphi - 2.340*dphi**3*dlam - 0.608*dphi*dlam**3 + 0.008*dlam**2 + 0.148*dphi**2*dlam**3
    y = 463000 + 309056.544*dphi + 3638.893*dlam**2 + 73.077*dphi**2 - 157.984*dphi*dlam**2 + 59.788*dphi**3 + 0.433*dlam - 6.439*dphi**2*dlam**2 - 0.032*dphi*dlam + 0.092*dlam**4 - 0.054*dphi*dlam**4
    return x, y
r = ET.parse(src).getroot()
N = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in r.iter('node')}
T = lambda e: {t.get('k'): t.get('v') for t in e.findall('tag')}
pts = []
for w in r.iter('way'):
    if 'sprookjesbos' in T(w).get('website', ''): pts += [N[n.get('ref')] for n in w.findall('nd') if n.get('ref') in N]
for n in r.iter('node'):
    if 'sprookjesbos' in T(n).get('website', ''): pts.append(N[n.get('id')])
rd = [wgs_to_rd(*p) for p in pts]
m = 80
x0, x1 = int(min(p[0] for p in rd)-m), int(max(p[0] for p in rd)+m)
y0, y1 = int(min(p[1] for p in rd)-m), int(max(p[1] for p in rd)+m)
print('RD bbox', x0, y0, x1, y1, 'size m', x1-x0, y1-y0)
print('park origin RD', wgs_to_rd(51.65, 5.0455))
for cov in ('dtm_05m', 'dsm_05m'):
    url = (f"https://service.pdok.nl/rws/ahn/wcs/v1_0?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&COVERAGEID={cov}"
           f"&FORMAT=image/tiff&SUBSET=x({x0},{x1})&SUBSET=y({y0},{y1})")
    urllib.request.urlretrieve(url, f"{outdir}/{cov}.tif")
open(f"{outdir}/bbox.txt", 'w').write(f"{x0} {y0} {x1} {y1}\n")
