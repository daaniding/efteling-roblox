import sys,math,json,csv,numpy as np
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
S,R=sys.argv[1],sys.argv[2]
LAT0,LON0=51.6500,5.0455
KX=111320*math.cos(math.radians(LAT0)); KY=110574
def rd(lat,lon):
    dphi=0.36*(lat-52.15517440); dlam=0.36*(lon-5.38720621)
    Rp=[(0,1,190094.945),(1,1,-11832.228),(2,1,-114.221),(0,3,-32.391),(1,0,-0.705),(3,1,-2.340),(1,3,-0.608),(0,2,-0.008),(2,3,0.148)]
    Sp=[(1,0,309056.544),(0,2,3638.893),(2,0,73.077),(1,2,-157.984),(3,0,59.788),(0,1,0.433),(2,2,-6.439),(1,1,-0.032),(0,4,0.092),(1,4,-0.054)]
    return (155000+sum(c*dphi**p*dlam**q for p,q,c in Rp), 463000+sum(c*dphi**p*dlam**q for p,q,c in Sp))
A=np.load(f"{S}/ahn/dtm.npy")
# gaten vullen (gebouwen/water): herhaald gemiddelde van buren
F=A.copy(); m=np.isnan(F)
F[m]=np.nanmean(A)
for it in range(400):
    P=np.pad(F,1,mode='edge'); avg=(P[:-2,1:-1]+P[2:,1:-1]+P[1:-1,:-2]+P[1:-1,2:])/4
    F[m]=avg[m]
# lokaal raster 1 m
X0,X1,Y0,Y1=-150,300,-150,330
xs=np.arange(X0,X1+1,1.0); ys=np.arange(Y1,Y0-1,-1.0)  # rij 0 = noord
gx,gy=np.meshgrid(xs,ys)
lat=LAT0+gy/KY; lon=LON0+gx/KX
# rd vectorized
dphi=0.36*(lat-52.15517440); dlam=0.36*(lon-5.38720621)
Rp=[(0,1,190094.945),(1,1,-11832.228),(2,1,-114.221),(0,3,-32.391),(1,0,-0.705),(3,1,-2.340),(1,3,-0.608),(0,2,-0.008),(2,3,0.148)]
Sp=[(1,0,309056.544),(0,2,3638.893),(2,0,73.077),(1,2,-157.984),(3,0,59.788),(0,1,0.433),(2,2,-6.439),(1,1,-0.032),(0,4,0.092),(1,4,-0.054)]
RX=155000+sum(c*dphi**p*dlam**q for p,q,c in Rp); RY=463000+sum(c*dphi**p*dlam**q for p,q,c in Sp)
col=(RX-131100)/0.5-0.5; row=(407250-RY)/0.5-0.5
c0=np.floor(col).astype(int); r0=np.floor(row).astype(int); fc=col-c0; fr=row-r0
def g(r,c): return F[np.clip(r,0,F.shape[0]-1),np.clip(c,0,F.shape[1]-1)]
H=(g(r0,c0)*(1-fc)*(1-fr)+g(r0,c0+1)*fc*(1-fr)+g(r0+1,c0)*(1-fc)*fr+g(r0+1,c0+1)*fc*fr)
M=(np.isnan(A[np.clip(np.round(row).astype(int),0,A.shape[0]-1),np.clip(np.round(col).astype(int),0,A.shape[1]-1)]))
np.save(f"{S}/ahn/lokaal_H.npy",H); np.save(f"{S}/ahn/lokaal_gat.npy",M)
json.dump({"X0":X0,"X1":X1,"Y0":Y0,"Y1":Y1,"res":1.0},open(f"{S}/ahn/lokaal_meta.json","w"))
# punten
pts=[]
for r in csv.DictReader(open(f"{R}/reference/data/efteling_objecten_meters.csv")):
    if r["naam"].startswith("Muzikale Paddenstoel") or r["naam"]=="Sprookjesboom":
        x,y=float(r["x_min"]),float(r["y_min"]); pts.append((r["naam"],x,y))
def hat(x,y):
    i=int(round(Y1-y)); j=int(round(x-X0)); return float(H[i,j])
for n,x,y in pts: print(f"{n:24s} x={x:7.1f} y={y:7.1f} h={hat(x,y):6.2f} m NAP")
# OSM paden
tree=ET.parse(f"{R}/reference/data/efteling_osm.xml").getroot()
nodes={n.get('id'):(float(n.get('lat')),float(n.get('lon'))) for n in tree.iter('node')}
ways=[];names=[]
for w in tree.iter('way'):
    tags={t.get('k'):t.get('v') for t in w.iter('tag')}
    if 'highway' in tags or 'building' in tags or tags.get('natural')=='water' or tags.get('water'):
        pl=[((nodes[n.get('ref')][1]-LON0)*KX,(nodes[n.get('ref')][0]-LAT0)*KY) for n in w.iter('nd') if n.get('ref') in nodes]
        kind='pad' if 'highway' in tags else ('gebouw' if 'building' in tags else 'water')
        ways.append((kind,pl,tags.get('name','')))
# render: hillshade + kleur op hoogte
lo,hi=np.percentile(H,1),np.percentile(H,99)
dy,dx=np.gradient(H); sh=np.clip(0.6+ (-dx*0.7+dy*0.7)*1.2,0,1)
t=np.clip((H-lo)/(hi-lo),0,1)
rgb=np.stack([0.25+0.7*t,0.55+0.25*t,0.3-0.1*t],-1)*sh[...,None]
img=Image.fromarray((np.clip(rgb,0,1)*255).astype(np.uint8)).resize((900,960),Image.BILINEAR)
sc=2.0; d=ImageDraw.Draw(img)
def P(x,y): return ((x-X0)*sc,(Y1-y)*sc)
# hoogtelijnen per 0.5 m
import itertools
lv=np.arange(np.floor(lo),hi,0.5)
for L in lv:
    b=(H>=L)
    e=(b[1:,1:]!=b[:-1,1:])|(b[1:,1:]!=b[1:,:-1])
    ys_,xs_=np.nonzero(e)
    c=(255,255,255) if abs(L-round(L))<1e-6 else (200,200,200)
    for yy,xx in zip(ys_,xs_): d.point(((xx+1)*sc,(yy+1)*sc),fill=c)
for kind,pl,nm in ways:
    q=[P(x,y) for x,y in pl]
    if len(q)<2: continue
    if kind=='pad': d.line(q,fill=(240,200,120),width=2)
    elif kind=='gebouw': d.line(q,fill=(60,60,60),width=1)
    else: d.line(q,fill=(60,120,255),width=2)
for n,x,y in pts:
    px,py=P(x,y); r=7 if n=="Sprookjesboom" else 4
    d.ellipse((px-r,py-r,px+r,py+r),fill=(255,0,0) if n!="Sprookjesboom" else (255,0,255),outline="black")
    d.text((px+6,py-6),"BOOM" if n=="Sprookjesboom" else n.split()[-1],fill="white")
# legenda
d.rectangle((0,0,300,40),fill=(0,0,0)); d.text((5,4),f"AHN4 DTM {lo:.1f}..{hi:.1f} m NAP, lijnen 0.5 m (wit=hele m)",fill="white"); d.text((5,20),"raster 1 px=0.5 m, x -150..300, y -150..330",fill="white")
for gxl in range(-100,301,100):
    d.line([P(gxl,Y0),P(gxl,Y1)],fill=(0,0,0),width=1)
for gyl in range(-100,331,100):
    d.line([P(X0,gyl),P(X1,gyl)],fill=(0,0,0),width=1)
img.save(f"{S}/ahn/reliëf_overzicht.jpg",quality=82)
