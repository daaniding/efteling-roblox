import sys, json, numpy as np
sys.path.insert(0,'/Users/daaniding/RobloxProjects/efteling-roblox/tools'); import geo
from PIL import Image
from scipy import ndimage
S=sys.argv[1]; ROOT='/Users/daaniding/RobloxProjects/efteling-roblox'  # S = werkmap met units.json (kopie: reference/ahn_sprookjesbos/units_studio.json)
D=np.array(Image.open(f'{ROOT}/reference/ahn_sprookjesbos/dtm_05m.tif'),dtype=np.float32)
D[(D>1e30)|(D<-100)]=np.nan; gat=np.isnan(D)
bx=list(map(float,open(f'{ROOT}/reference/ahn_sprookjesbos/bbox.txt').read().split()))
F=D.copy(); F[gat]=np.nanmean(D)
for _ in range(500):
    P=np.pad(F,1,mode='edge'); F[gat]=((P[:-2,1:-1]+P[2:,1:-1]+P[1:-1,:-2]+P[1:-1,2:])/4)[gat]
F=ndimage.gaussian_filter(F,3)  # sigma 1.5 m
# grid in studs, 4-stud cells
X0,X1,Z0,Z1=-400,760,-900,440
xs=np.arange(X0,X1,4)+2; zs=np.arange(Z0,Z1,4)+2
GX,GZ=np.meshgrid(xs,zs)  # [iz,ix]
px,py=GX/3.0,-GZ/3.0
o=np.array(geo.park_to_rd(0,0)); ex=np.array(geo.park_to_rd(1,0))-o; ey=np.array(geo.park_to_rd(0,1))-o
RX=o[0]+px*ex[0]+py*ey[0]; RY=o[1]+px*ex[1]+py*ey[1]
c=(RX-bx[0])/0.5-0.5; r=(bx[3]-RY)/0.5-0.5
inside=(c>=0)&(c<F.shape[1]-1)&(r>=0)&(r<F.shape[0]-1)
H=ndimage.map_coordinates(F,[r,c],order=1,mode='nearest')
units=json.load(open(f'{S}/units.json'))
rig=[u for u in units if u[1]=='R']
# clusters by bbox overlap (+3 studs)
m=3; par=list(range(len(rig)))
def f(i):
    while par[i]!=i: i=par[i]
    return i
for i in range(len(rig)):
    for j in range(i+1,len(rig)):
        a,b=rig[i],rig[j]
        if a[2]-m<b[4] and b[2]-m<a[4] and a[3]-m<b[5] and b[3]-m<a[5]: par[f(i)]=f(j)
cl={}
for i,u in enumerate(rig): cl.setdefault(f(i),[]).append(u)
# core mask: all units expanded 45 studs (15 m)
core=np.zeros(GX.shape,bool)
for u in units:
    core|=(GX>=u[2]-45)&(GX<=u[4]+45)&(GZ>=u[3]-45)&(GZ<=u[5]+45)
dist=ndimage.distance_transform_edt(~core)*4  # studs
w=np.clip(1-dist/90,0,1); w=w*w*(3-2*w)  # fade over 30 m
REF=float(np.median(H[core&inside]))
raw=3*(H-REF)*w
raw[~inside]=0
# --- Keuze B (Daan 15 nov): echte hoogte overal; alleen kleine v1-modellen (<= 90 studs) krijgen een eigen vlak plateau.
GROOT=90
small=[u for u in rig if max(u[4]-u[2],u[5]-u[3])<=GROOT]; big=[u for u in rig if u not in small]
par=list(range(len(small)))
def f(i):
    while par[i]!=i: i=par[i]
    return i
for i in range(len(small)):
    for j in range(i+1,len(small)):
        a,b=small[i],small[j]
        if a[2]-m<b[4] and b[2]-m<a[4] and a[3]-m<b[5] and b[3]-m<a[5]: par[f(i)]=f(j)
cl={}
for i,u in enumerate(small): cl.setdefault(f(i),[]).append(u)
dmin=np.full(GX.shape,1e9); pl_val=np.zeros(GX.shape); info=[]
for k,us in cl.items():
    msk=np.zeros(GX.shape,bool)
    for u in us: msk|=(GX>=u[2])&(GX<=u[4])&(GZ>=u[3])&(GZ<=u[5])
    v=float(np.median(raw[msk])); spread=float(np.percentile(raw[msk],95)-np.percentile(raw[msk],5))
    for u in us: u.append(v)
    info.append(dict(units=[u[0] for u in us],dy=round(v,2),spread=round(spread,2)))
    d=ndimage.distance_transform_edt(~msk)*4
    upd=d<dmin; dmin[upd]=d[upd]; pl_val[upd]=v
t=np.clip((dmin-4)/24,0,1); t=t*t*(3-2*t)
delta=pl_val*(1-t)+raw*t
for u in big:
    msk=(GX>=u[2])&(GX<=u[4])&(GZ>=u[3])&(GZ<=u[5])
    u.append(float(np.median(delta[msk])))
    info.append(dict(units=[u[0]],dy=round(u[-1],2),groot=True,spread=round(float(np.percentile(delta[msk],95)-np.percentile(delta[msk],5)),2)))
np.save(f'{S}/delta.npy',delta.astype(np.float32))
json.dump(dict(X0=X0,Z0=Z0,cell=4,nx=len(xs),nz=len(zs),REF=REF,units={u[0]:round(u[-1],2) for u in rig}),open(f'{S}/delta_meta.json','w'),indent=0)
for i in info: print(i)
print('REF NAP',REF,'delta range',delta.min(),delta.max())
