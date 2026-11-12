"""04_omgeving Villa Volta: tuin + wachtrij zoals in de Efteling, uit OSM (ref/osm_lokaal.json, modelcoordinaten:
x langs de gevel naar oost, y naar achter/noord, oorsprong = midden gevel op terrashoogte-voetlijn).
Bronnen: OSM-ways rond Villa Volta (hagen, paden, muren, rij-overkapping, zigzag, poortjes, tourniquets, deuren, lantaarns),
darkridedatabase.com: 'twee grote pilaren aan het Ton van de Venplein, tuin tussen bezoeker en villa'.
Inferred: hoogtes van hagen/muren/dak, uiterlijk van de rijhal, positie zonnewijzer en plantvazen, bloemen.
Schrijft ook colliders (onzichtbare blokken voor Roblox) naar exports/colliders.json."""
import bpy, bmesh, sys, os, math, json
from mathutils import Vector, Matrix
HERE=os.path.dirname(os.path.abspath(__file__))
_src=open(os.path.join(HERE,"03_forms.py")).read().split("def build(master):")[0]
_src=_src.replace('PHASE="03_forms"','PHASE="04_omgeving"')
exec(_src)
OSM=json.load(open(os.path.join(HERE,"..","ref","osm_lokaal.json")))
MATS.update({
 "haag":((0.10,0.22,0.08,1),0.9), "beuk":((0.13,0.27,0.10,1),0.9), "buxus":((0.14,0.30,0.11,1),0.9),
 "grind":((0.76,0.70,0.58,1),0.95), "klinker":((0.50,0.34,0.27,1),0.9), "ijzer":((0.06,0.13,0.09,1),0.4),
 "bloem_rood":((0.75,0.08,0.10,1),0.7), "bloem_wit":((0.92,0.90,0.85,1),0.7), "bloem_paars":((0.40,0.15,0.55,1),0.7),
 "aarde":((0.22,0.15,0.10,1),1.0), "lamp":((1.0,0.85,0.55,1),0.3), "bord":((0.05,0.18,0.12,1),0.5), "goud":((0.78,0.62,0.28,1),0.35),
})
COLL=[]
def coll(cx,cy,cz,sx,sy,sz,a=0.0): COLL.append([round(v,3) for v in (cx,cy,cz,sx,sy,sz,a)])
def seglen(p,q): return math.hypot(q[0]-p[0],q[1]-p[1])

def strip(part,mat,pts,w,h,z0=0.0,ch=0.0,collide=True,extend=None):
    """box per segment langs een polylijn (hagen, muren, paden)"""
    ext=w*0.5 if extend is None else extend
    for p,q in zip(pts,pts[1:]):
        L=seglen(p,q)
        if L<0.05: continue
        a=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0])); mx,my=(p[0]+q[0])/2,(p[1]+q[1])/2
        put(part,mat,bbox(L+ext,w,h,0,0,z0+h/2,ch),TR(mx,my,0,a))
        if collide: coll(mx,my,z0+h/2,L+ext,w,h,a)
def path(mat,pts,w,z=0.06):
    strip("paden",mat,pts,w,z,0.0,collide=False,extend=0.0)
    for p in pts: put("paden",mat,blathe([(0,0),(w/2,0),(w/2,z-0.006),(0,z-0.006)],14),TR(p[0],p[1],0))   # iets lager: geen samenvallende vlakken
def rail(p,q,h=1.0,posts=True):
    L=seglen(p,q); n=max(1,int(L/1.6)); a=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]))
    for zz,r in ((h*0.45,0.022),(h-0.03,0.03)):
        put("hekken","ijzer",btube([(p[0],p[1],zz),(q[0],q[1],zz)],r,6))
    if posts:
        for i in range(n+1):
            t=i/n; x=p[0]+(q[0]-p[0])*t; y=p[1]+(q[1]-p[1])*t
            put("hekken","ijzer",blathe([(0,0),(0.06,0),(0.06,0.05),(0.035,0.08),(0.035,h-0.02),(0.05,h),(0.04,h+0.06),(0.015,h+0.1),(0,h+0.12)],8),TR(x,y,0))
    mx,my=(p[0]+q[0])/2,(p[1]+q[1])/2; coll(mx,my,h/2,L,0.12,h,a)
def lantern_head(x,y,z,s=1.0):
    put("lantaarns","ijzer",blathe([(0,0),(0.09*s,0),(0.13*s,0.06*s),(0.15*s,0.36*s),(0.2*s,0.4*s),(0.12*s,0.5*s),(0.03*s,0.58*s),(0.02*s,0.66*s),(0,0.68*s)],6),TR(x,y,z))
    put("lantaarns","lamp",blathe([(0,0.07*s),(0.12*s,0.08*s),(0.135*s,0.36*s),(0,0.37*s)],6),TR(x,y,z))
LAMPS=[]
def lamppost(x,y):
    put("lantaarns","ijzer",blathe([(0,0),(0.2,0),(0.2,0.12),(0.14,0.2),(0.12,0.45),(0.07,0.6),(0.06,2.2),(0.08,2.3),(0.05,2.4),(0,2.4)],10),TR(x,y,0))
    for sx in (-1,1):
        put("lantaarns","ijzer",btube([(x,y,2.25),(x+sx*0.3,y,2.45),(x+sx*0.45,y,2.42)],0.025,6))
        lantern_head(x+sx*0.45,y,2.3,0.8); LAMPS.append((x+sx*0.45,y,2.55))
    lantern_head(x,y,2.4,0.9); LAMPS.append((x,y,2.65)); coll(x,y,1.2,0.4,0.4,2.4)
def inside(px,py,poly):
    c=False; j=len(poly)-1
    for i in range(len(poly)):
        xi,yi=poly[i]; xj,yj=poly[j]
        if (yi>py)!=(yj>py) and px<(xj-xi)*(py-yi)/(yj-yi)+xi: c=not c
        j=i
    return c
def flowerbed(poly,step=0.45,inset_poly=None):
    xs=[p[0] for p in poly]; ys=[p[1] for p in poly]; k=0
    y=min(ys)+step/2
    while y<max(ys):
        x=min(xs)+step/2
        while x<max(xs):
            if inside(x,y,poly) and min(math.hypot(x-p[0],y-p[1]) for p in poly)>0.35:
                col_=("bloem_rood","bloem_wit","bloem_paars")[(int(x/step)+int(y/step)*2)%3]
                bm=bmesh.new(); bmesh.ops.create_icosphere(bm,subdivisions=1,radius=0.17); bmesh.ops.scale(bm,vec=(1,1,0.7),verts=bm.verts)
                put("bloemen",col_,bm,TR(x+0.07*math.sin(k*1.7),y+0.07*math.cos(k*2.3),0.2)); k+=1
            x+=step
        y+=step
    # aarde: kleine plaat onder het bed
    bm=bmesh.new(); vs=[bm.verts.new((p[0],p[1],0.05)) for p in poly]
    try: bm.faces.new(vs); put("paden","aarde",bm)
    except ValueError: bm.free()

def build(master):
    open_master(master); clear_owned()
    for n,(c,r) in MATS.items(): material("MAT_"+n,c,r)
    # ---------------- villa-colliders (maten uit 03_forms) ----------------
    coll(0,0.7,T/2,17.2,11.4,T)                                   # terras
    for i in range(4):
        w=9.5+2.4*(3-i); y0=-5.0-0.35*(4-i); zt=T*(i+1)/4; coll(0,(y0-5.0)/2,zt/2,w,-5.0-y0,zt)
    coll(0,MD/2,T+CM/2,MW,MD,CM);
    for s in (-1,1):
        coll(s*(HX+WW/2),WY+WD/2,T+CW/2,WW,WD,CW)
        coll(s*6.55,-0.4,T+0.4,3.9,0.35,0.8); coll(s*8.2,1.1,T+0.4,0.35,3.4,0.8)
        coll(s*COLX,COLY,T+BAL_Z0/2,0.6,0.6,BAL_Z0); coll(s*1.75,-0.1,T+1.5,0.55,0.4,3.0); coll(s*2.45,-1.0,T+0.9,0.45,0.45,1.8)
    # ---------------- tuin ----------------
    # voorpad langs het terras + ovaal rond de tuin + as naar het plein (OSM 444834329)
    loop=[(8.54,-6.58),(-8.83,-6.54),(-10.94,-12.95),(-8.92,-19.92),(-5.11,-22.18),(-0.07,-24.09),(5.68,-21.09),(9.13,-16.98),(8.54,-6.58)]
    path("grind",loop,2.6)
    path("grind",[(-0.07,-24.09),(-0.64,-30.29),(1.23,-45.78)],4.0)
    path("grind",[(-8.83,-6.54),(-9.39,2.07),(-7.19,9.44)],2.2)                 # uitgangspad west
    path("klinker",[(8.54,-6.58),(11.29,-0.1),(12.52,0.62),(13.76,1.34),(16.88,3.16),(18.35,4.7),(19.73,10.04)],2.4)   # naar de rij-ingang
    # grote hagen (beuk, oranje in front.jpg) in twee bogen naar de pilaren
    strip("hagen","beuk",[(-2.91,-26.72),(-4.93,-26.58),(-7.02,-26.06),(-8.54,-25.0),(-9.89,-23.83),(-11.01,-22.68),(-11.92,-21.35),(-12.72,-18.26),(-13.04,-15.1),(-12.86,-11.94),(-12.86,-8.8)],0.7,1.1,ch=0.15)
    strip("hagen","beuk",[(11.14,-6.94),(11.75,-10.6),(11.97,-12.96),(11.98,-15.05),(11.57,-17.8),(10.8,-20.34),(9.47,-22.12),(7.84,-23.7),(6.47,-24.73),(4.8,-25.56),(1.66,-26.21)],0.7,1.1,ch=0.15)
    # bladvormige buxushagen met bloemen erin + binnenboog
    for key in ("haag_tuin_o","haag_tuin_w"):
        poly=[tuple(p) for p in OSM[key]]
        strip("hagen","buxus",poly,0.35,0.5,ch=0.08); flowerbed(poly[:-1])
    strip("hagen","buxus",[(-2.43,-12.39),(-1.51,-12.69),(-0.76,-12.77),(0.1,-12.71),(0.95,-12.6),(1.97,-12.37),(2.98,-11.9),(2.98,-12.91),(3.05,-14.02),(3.2,-15.19),(3.4,-16.59),(3.77,-17.97)],0.35,0.5,ch=0.08)
    strip("hagen","buxus",[(-7.92,-15.91),(-7.45,-17.2),(-6.89,-18.39),(-5.84,-19.44),(-4.45,-20.33),(-3.01,-20.97),(-1.45,-21.28),(0.12,-21.37),(1.58,-21.22),(2.99,-20.84),(3.97,-20.27),(4.78,-19.65)],0.35,0.5,ch=0.08)
    # pilaren aan het plein met lantaarns (OSM street_lamp op 2.91,-26.72 en 1.66,-26.21)
    for (x,y) in ((-2.91,-26.72),(1.66,-26.21)):
        put("pilaren","steen",bbox(1.1,1.1,0.4,x,y,0.2,0.02))
        put("pilaren","steen",bbox(0.9,0.9,2.6,x,y,1.7,0.02))
        z=0.6
        while z<2.8: put("pilaren","steen",bbox(0.98,0.98,0.32,x,y,z+0.16,0.04)); z+=0.45
        put("pilaren","steen",bbox(1.15,1.15,0.18,x,y,3.09,0.02)); put("pilaren","steen",bbox(0.8,0.8,0.25,x,y,3.3,0.02))
        put("lantaarns","ijzer",blathe([(0,0),(0.1,0),(0.07,0.1),(0.05,0.5),(0.08,0.6),(0,0.62)],8),TR(x,y,3.42))
        lantern_head(x,y,4.0,1.3); LAMPS.append((x,y,4.4)); coll(x,y,1.8,1.15,1.15,3.6)
    # zonnewijzer (armillair) op balusterzuil op de tuinas, plantvazen aan het voorpad (inferred uit front.jpg)
    put("tuinbeelden","wit",blathe([(r*1.6,h*1.6) for r,h in BALUSTER],12),TR(0,-17.0,0))
    put("tuinbeelden","wit",bbox(0.45,0.45,0.08,0,-17.0,1.16))
    zc=1.62
    for M in (Matrix.Identity(4),Matrix.Rotation(math.radians(90),4,"X"),Matrix.Rotation(math.radians(52),4,"Y")):
        pts=[tuple((M@Vector((0.36*math.cos(t*math.tau/24),0.36*math.sin(t*math.tau/24),0)))+Vector((0,-17.0,zc))) for t in range(25)]
        put("tuinbeelden","zink",btube(pts,0.018,6))
    ax=Matrix.Rotation(math.radians(38),4,"X")@Vector((0,0,0.5))
    put("tuinbeelden","zink",btube([(-ax.x,-17.0-ax.y,zc-ax.z),(ax.x,-17.0+ax.y,zc+ax.z)],0.012,6))
    put("tuinbeelden","zink",btube([(0,-17.0,1.2),(0,-17.0,zc-0.36)],0.03,6)); coll(0,-17.0,1.0,0.5,0.5,2.0)
    for sx in (-1,1):
        put("tuinbeelden","steen",bbox(0.55,0.55,0.8,sx*2.6,-8.9,0.4,0.02)); urn("tuinbeelden",sx*2.6,-8.9,0.8,1.1)
        for k in range(6):
            bm=bmesh.new(); bmesh.ops.create_icosphere(bm,subdivisions=1,radius=0.2)
            put("bloemen","bloem_paars" if k%2 else "buxus",bm,TR(sx*2.6+0.18*math.cos(k),-8.9+0.18*math.sin(k),1.75+0.05*(k%3)))
        coll(sx*2.6,-8.9,0.9,0.6,0.6,1.8)
    for (x,y) in ((-9.9,-6.2),(9.6,-6.2),(-11.9,-13.0),(10.6,-14.0)):
        lamppost(x,y)
    # wacht- en showtijdenbord op het plein (OSM 460832618)
    bx,by=18.6,-50.2
    put("bord","steen",bbox(2.3,3.9,0.4,bx,by,0.2,0.02))
    for dy in (-1.6,1.6): put("bord","ijzer",blathe([(0,0),(0.12,0),(0.08,0.15),(0.06,3.2),(0.1,3.3),(0,3.5)],8),TR(bx,by+dy,0.4))
    put("bord","bord",bbox(0.25,3.1,1.9,bx,by,2.25,0.03))
    put("bord","goud",bbox(0.3,3.25,0.12,bx,by,3.26,0.02)); put("bord","goud",bbox(0.3,3.25,0.1,bx,by,1.26,0.02))
    seg=[(x,z) for x,z in arc(0,2.4,1.6,25,155,12)]
    put("bord","goud",boutline([(1.45,3.3)]+[(x,z+0.9) for x,z in seg][1:-1]+[(-1.45,3.3)],-0.1,0.2),TR(bx,by,0,90))
    coll(bx,by,1.75,2.3,3.9,3.5)
    # ---------------- wachtrij ----------------
    # ingangsgang tussen muur_a en muur_b (x 10.9-12.5, y 2.7-8.85)
    for key in ("muur_a","muur_b"):
        pts=OSM[key]; strip("rij_muren","stuc",pts,0.3,2.4,ch=0.02)
        strip("rij_muren","steen",pts,0.42,0.12,2.4,ch=0.02,collide=False)
        strip("rij_muren","steen",pts,0.38,0.35,0.0,collide=False)
    for x in (10.9,12.3):   # poortpijlers met vazen aan de ingang
        put("rij_muren","steen",bbox(0.6,0.6,2.9,x,2.55,1.45,0.02)); put("rij_muren","steen",bbox(0.72,0.72,0.15,x,2.55,2.95,0.02))
        urn("vazen",x,2.55,3.02,0.8,"steen"); coll(x,2.55,1.5,0.6,0.6,3.0)
    # poortboog met naambord + 'INGANG'
    put("rij_bord","goud",btube([(10.9,2.55,2.9)]+[(11.6+0.7*math.cos(math.radians(a)),2.55,2.9+0.55*math.sin(math.radians(a))) for a in range(170,9,-20)]+[(12.3,2.55,2.9)],0.04,6))
    put("rij_bord","bord",bbox(1.15,0.08,0.38,11.6,2.5,3.2,0.02))
    path("klinker",[(11.6,1.2),(11.6,2.6),(11.7,8.9)],1.4)
    # overdekte rijhal (OSM dak 7.1-13.1 x 8.85-30.7)
    H=3.3
    walls=[[(7.14,9.02),(11.07,8.85)],[(12.52,8.82),(13.06,28.9),(13.11,30.61)],[(13.11,30.61),(7.38,30.74)],[(7.38,30.74),(7.14,9.02)]]
    for w in walls:
        strip("rijhal","stuc",w,0.3,H,ch=0.01)
        strip("rijhal","steen",w,0.42,0.45,0.0,collide=False); strip("rijhal","steen",w,0.5,0.25,H-0.15,collide=False)
    for (y0,y1) in ((12,13),(16,17),(20,21),(24,25)):   # pilasters + blinde nissen aan de oostgevel
        for x in (13.2,):
            put("rijhal","steen",bbox(0.12,0.55,H-0.6,x+0.05*(y0-12)/18+0.02,y0+0.5,0.45+(H-0.6)/2,0.01))
    # dak (leien, schilddak)
    rb=bmesh.new()
    ring=lambda o,z:[rb.verts.new(p) for p in ((7.1-o,8.8-o,z),(13.15+o,8.8-o,z),(13.15+o,30.75+o,z),(7.1-o,30.75+o,z))]
    r0=ring(0.45,H); r1=ring(-2.4,H+1.7)
    for i in range(4): rb.faces.new((r0[i],r0[(i+1)%4],r1[(i+1)%4],r1[i]))
    rb.faces.new(r1); rb.faces.new(list(reversed(r0))); bmesh.ops.recalc_face_normals(rb,faces=rb.faces); put("rijhal","lei",rb)
    put("rijhal","zink",btube([(9.55,11.2,H+1.72),(10.7,11.2,H+1.72)] if False else [(9.55,11.25,H+1.72),(9.55,28.3,H+1.72)],0.06,6))
    path("klinker",[(10.1,9.2),(10.1,30.4)],5.6)
    # zigzag (OSM 1427152769): hekken tussen de banen, open aan de keerkant
    zz=[tuple(p) for p in OSM["zigzag"]]
    WEST,EAST=7.45,11.55
    for p,q in zip(zz,zz[1:]):
        if abs(q[0]-p[0])<0.2 and abs(q[1]-p[1])>0.5:      # keerstuk
            ym=(p[1]+q[1])/2; xt=p[0]
            if xt<9.5: rail((xt+0.85,ym),(EAST,ym))
            else: rail((WEST,ym),(xt-0.85,ym))
    rail((EAST,9.95),(EAST,16.75)); rail((EAST,17.55),(EAST,23.85))          # bypass-scheiding met poortjes op 17.15 en 24.22 (OSM)
    rail((WEST,24.8),(11.9,24.8)); rail((7.9,26.85),(12.0,26.85))
    for (x,y) in ((12.02,17.15),(12.22,24.22),(12.32,27.44),(8.85,27.44),(11.79,9.39)):   # poortjes
        put("hekken","ijzer",bbox(0.04,0.04,1.0,x,y-0.38,0.5)); put("hekken","ijzer",bbox(0.04,0.04,1.0,x,y+0.38,0.5))
    for (x,y) in ((9.21,26.3),(9.22,25.73)):   # tourniquets
        put("tourniquets","zink",blathe([(0,0),(0.18,0),(0.18,0.85),(0.12,0.95),(0,0.95)],10),TR(x,y,0))
        for a in (0,120,240):
            d=Vector((math.cos(math.radians(a)),0,math.sin(math.radians(a))))*0.45
            put("tourniquets","zink",btube([(x,y,0.85),(x+d.x,y,0.85+d.z*0.3)],0.025,6))
    # entree-deuren in de westwand (OSM main 7.33,26.03 en 7.36,28.93)
    for y in (26.03,28.93):
        put("deuren","groen",bbox(0.1,1.8,2.5,7.33,y,1.25,0.01))
        put("deuren","steen",bbox(0.2,2.3,0.3,7.32,y,2.65,0.02))
        for dy in (-1.05,1.05): put("deuren","steen",bbox(0.2,0.3,2.5,7.32,y+dy,1.25,0.01))
        put("deuren","zink",bbox(0.06,0.04,0.4,7.25,y-0.15,1.1)); put("deuren","zink",bbox(0.06,0.04,0.4,7.25,y+0.15,1.1))
    for (x,y) in ((10.97,22.82),(10.84,14.45),(11.13,27.64)):   # afvalbakken (OSM)
        put("afvalbakken","groen",blathe([(0,0),(0.22,0),(0.24,0.75),(0.26,0.8),(0.2,0.86),(0.05,0.95),(0,0.95)],10),TR(x,y,0)); coll(x,y,0.45,0.45,0.45,0.9)
    # wandlantaarns in de hal
    for y in (11,15,19,23,27):
        for x,dx in ((7.32,0.25),(12.75+0.03*(y-9)/20,-0.25)):
            put("lantaarns","ijzer",btube([(x,y,2.6),(x+dx,y,2.65)],0.025,6)); lantern_head(x+dx,y,2.2,0.7); LAMPS.append((x+dx,y,2.4))
    # buitenpad (rolstoel/single rider) en hoge haag erlangs
    path("klinker",[(13.15,2.59),(13.61,19.45),(13.86,28.87),(13.06,28.9)],1.0)
    strip("hagen","haag",[tuple(p) for p in OSM["haag_oost"]],0.6,2.2,ch=0.15)
    strip("rij_muren","stuc",[tuple(p) for p in OSM["muur_c"]],0.3,2.4,ch=0.02)
    # ---------------- objecten ----------------
    n=0; tris=0
    for (part,mat),bm in PARTS.items():
        bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5)
        ob=new_mesh_object(f"VO_{part}__{mat}",bm,"OMGEVING"); assign(ob,bpy.data.materials["MAT_"+mat])
        if mat in ("ijzer","zink","wit","lamp","beuk","haag","buxus") or part in ("bloemen","vazen","tuinbeelden"): shade_smooth(ob,math.radians(40))
        n+=1; tris+=sum(len(p.vertices)-2 for p in ob.data.polygons)
    out=os.path.join(HERE,"..","exports"); os.makedirs(out,exist_ok=True)
    json.dump({"colliders":COLL,"lamps":[[round(v,2) for v in l] for l in LAMPS],
               "doors":[[7.33,26.03],[7.36,28.93]],"wachtbord":[bx,by],"rijbord":[11.6,2.45,3.2]},open(os.path.join(out,"omgeving_data.json"),"w"))
    save_master(master); log("objects",n,"tris~",tris,"colliders",len(COLL),"lamps",len(LAMPS))
if __name__=="__main__":
    a=argv_after_dashes(); m=a[a.index("--master")+1] if "--master" in a else None
    if m: build(m)
