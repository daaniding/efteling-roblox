"""pad_einden: zoekt de einden van het padennet (hartlijn via Zhang-Suen-verdunning op 0,25 m) en zegt per einde of het aan de rand van het Sprookjesbos of bij een attractie ligt. Gebruik: .venv/bin/python tools/pad_einden.py (schrijft doodlopend.json in de huidige map)."""
import json, numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import shape, Point, box
R='/Users/daaniding/RobloxProjects/efteling-roblox/'
d=json.load(open(R+'models/PR_Paden/exports/paden_mesh.json'))
rand=shape(json.load(open(R+'models/PR_Paden/ref_zones.json'))['rand_sprookjesbos']['poly'])
RS=0.25; x0,y0,x1,y1=-60,-80,190,250
W=int((x1-x0)/RS); H=int((y1-y0)/RS)
mk=Image.new('L',(W,H),0); dr=ImageDraw.Draw(mk)
for k,st in d.items():
    if st['mat']=='rand': continue
    P=np.array(st['tri']).reshape(-1,3,3)
    for t in P: dr.polygon([((-p[0]-x0)/RS,(y1+p[1])/RS) for p in t],fill=1)
A=np.array(mk,dtype=np.uint8)
# Zhang-Suen
def nb(I):
    p=np.pad(I,1)
    return [p[:-2,1:-1],p[:-2,2:],p[1:-1,2:],p[2:,2:],p[2:,1:-1],p[2:,:-2],p[1:-1,:-2],p[:-2,:-2]]
I=A.copy()
while True:
    ch=0
    for step in (0,1):
        N=nb(I); B=sum(n.astype(int) for n in N)
        Aa=sum(((N[i]==0)&(N[(i+1)%8]==1)).astype(int) for i in range(8))
        if step==0: c=(N[0]*N[2]*N[4]==0)&(N[2]*N[4]*N[6]==0)
        else: c=(N[0]*N[2]*N[6]==0)&(N[0]*N[4]*N[6]==0)
        rm=(I==1)&(B>=2)&(B<=6)&(Aa==1)&c
        I[rm]=0; ch+=rm.sum()
    if ch==0: break
N=nb(I); B=sum(n.astype(int) for n in N)
ends=np.argwhere((I==1)&(B==1))
junc=(I==1)&(B>=3)
# spoorlengte van eindpunt tot knoop
res=[]
for r,c in ends:
    seen={(r,c)}; cur=(r,c); L=0
    while True:
        rr,cc=cur
        if junc[rr,cc] and L>0: break
        nxt=None
        for dr_,dc in ((-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)):
            q=(rr+dr_,cc+dc)
            if 0<=q[0]<H and 0<=q[1]<W and I[q] and q not in seen: nxt=q; break
        if nxt is None: break
        seen.add(nxt); cur=nxt; L+=1
        if L>400: break
    x=x0+(c+0.5)*RS; y=y1-(r+0.5)*RS
    res.append((x,y,L*RS))
units=json.load(open(R+'reference/ahn_sprookjesbos/units_studio.json'))
ub=[(u[0],box(u[2]/3,-u[5]/3,u[4]/3,-u[3]/3)) for u in units if not any(w in u[0] for w in ('Water','Planten','Stenen','Extra'))]
out=[]
for x,y,L in res:
    if L<5: continue   # stompjes van pleinhoeken
    p=Point(x,y); drand=rand.exterior.distance(p)
    att=[n for n,b in ub if b.buffer(4).contains(p)]
    out.append({'x':round(x,1),'y':round(y,1),'L':round(L,1),'rand':round(drand,1),'bij':att[:3]})
json.dump(out,open('doodlopend.json','w'))
for o in out: print(o)
