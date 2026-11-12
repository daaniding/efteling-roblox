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
    for i,(p,q) in enumerate(zip(pts,pts[1:])):
        L=seglen(p,q)
        if L<0.05: continue
        a=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0])); mx,my=(p[0]+q[0])/2,(p[1]+q[1])/2
        dz=0.012*(i%2)   # om en om iets hoger/breder: overlappende stukken hebben geen samenvallende vlakken
        put(part,mat,bbox(L+ext,w+dz,h+dz,0,0,z0+(h+dz)/2,ch),TR(mx,my,0,a))
        if collide: coll(mx,my,z0+h/2,L+ext,w,h,a)
PADEN=[]
def path(mat,pts,w,z=0.06):
    """paden worden in Roblox in het terrein geschilderd (geen platen: geen hoogteverschil, geen gras-kier, geen z-fighting)"""
    PADEN.append({"mat":mat,"w":w,"pts":[[round(x,3),round(y,3)] for x,y in pts]})
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
    """open lantaarn: glas zichtbaar tussen vier stijltjes (eerder zat het glas binnen een dichte kap)"""
    put("lantaarns","ijzer",blathe([(0,0),(0.06*s,0),(0.1*s,0.04*s),(0.13*s,0.06*s),(0.13*s,0.08*s),(0,0.08*s)],8),TR(x,y,z))
    for k in range(4):
        a=math.radians(45+90*k); r=0.13*s
        put("lantaarns","ijzer",btube([(x+r*math.cos(a),y+r*math.sin(a),z+0.07*s),(x+r*1.15*math.cos(a),y+r*1.15*math.sin(a),z+0.37*s)],0.012*s,4))
    put("lantaarns","lamp",blathe([(0,0.08*s),(0.1*s,0.08*s),(0.125*s,0.36*s),(0,0.36*s)],8),TR(x,y,z))
    put("lantaarns","ijzer",blathe([(0,0.36*s),(0.19*s,0.36*s),(0.19*s,0.39*s),(0.11*s,0.48*s),(0.04*s,0.55*s),(0.03*s,0.6*s),(0.05*s,0.64*s),(0,0.7*s)],8),TR(x,y,z))
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
    coll(0,(-5.0+WY)/2,T/2,17.2,5.0+WY,T)                         # terras
    for i in range(4):
        w=9.5+2.4*(3-i); y0=-5.0-0.35*(4-i); zt=T*(i+1)/4; coll(0,(y0-5.0)/2,zt/2,w,-5.0-y0,zt)
    coll(0,MD/2,(T+T+CM)/2,MW,MD,CM)                                # middenrisaliet
    coll(0,(WY+BACK)/2,(T+CW)/2,2*WX,BACK-WY,T+CW)                   # hoofdgebouw
    coll((AX0+AX1)/2,(BACK+AY1)/2,AH/2,AX1-AX0,AY1-BACK,AH)          # achterbouw
    for s in (-1,1):
        coll(s*(HX+8.5)/2,-0.4,T+0.4,8.5-HX,0.35,0.8); coll(s*8.2,(WY-0.55)/2,T+0.4,0.35,WY+0.55,0.8)
        coll(s*COLX,COLY,T+BAL_Z0/2,0.6,0.6,BAL_Z0); coll(s*1.75,-0.1,T+1.5,0.55,0.4,3.0); coll(s*2.45,-1.0,T+0.9,0.45,0.45,1.8)
    # ---------------- tuin ----------------
    # voorpad langs het terras + ovaal rond de tuin + as naar het plein (OSM 444834329)
    loop=[(8.54,-6.58),(-8.83,-6.54),(-10.94,-12.95),(-8.92,-19.92),(-5.11,-22.18),(-0.07,-24.09),(5.68,-21.09),(9.13,-16.98),(8.54,-6.58)]
    path("grind",loop,2.6)
    path("grind",[(-0.07,-24.09),(-0.64,-30.29),(1.23,-45.78)],4.0,0.075)
    path("grind",[(-8.83,-6.54),(-9.39,2.07),(-7.19,9.44)],2.2,0.07)                 # uitgangspad west
    path("klinker",[(8.54,-6.58),(11.29,-0.1),(13.1,1.3),(13.1,2.2)],2.4)   # naar de rij-ingang (OSM 1165997610)   # naar de rij-ingang
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
    # ---------------- wachtrij (Eftepedia-foto 'De wachtrij' 2022 + OSM) ----------------
    # overdekte meandering: west dichte stucmuur met bokkenhuiden, oost open zuilengang op lage borstwering,
    # wit vlak plafond met ronde lampjes, roodbruine klinkervloer, grijsgroene hekpaaltjes met bol, groene afvalbakken,
    # RVS-tourniquets voor de dubbele deur, perkament met dolk. Ingangsgang tussen twee muren (OSM muur_a/b).
    MATS.update({"plafond":((0.93,0.92,0.88,1),0.8),"rvs":((0.72,0.73,0.74,1),0.3),"hout":((0.28,0.18,0.11,1),0.9),
                 "huid":((0.86,0.80,0.66,1),0.9),"perkament":((0.88,0.80,0.60,1),0.9),"rijhek":((0.24,0.28,0.25,1),0.45),"klinkerrood":((0.45,0.24,0.18,1),0.9),"oranje":((0.85,0.42,0.10,1),0.5)})
    for n_,(c_,r_) in MATS.items(): material("MAT_"+n_,c_,r_)
    # Breedte aangepast voor Roblox (Daan: rij te smal/benauwd): galerij 8.9 m i.p.v. 6.2, banen 1.6 m, doorloop 1.8 m, gang 2.2 m.
    # Volgorde en vorm zoals echt (plattegrond/OSM/Eftepedia): gang -> zigzag dwars op de galerij -> doorloop met poortjes -> tourniquets -> dubbele deur.
    GW=WX+0.18; GE=15.8; GY0,GY1=8.85,30.7; CX0,CX1=12.0,14.2      # galerij west/oost, gang
    def wx(y): return GW
    def ex(y): return GE
    H=3.9   # hoger plafond: minder benauwd (Daan)
    for xg in (CX0,CX1):   # ingangsgang: lage witte muurtjes met pijlertjes (DRDB-plattegrond)
        pts=[(xg,2.7),(xg,GY0)]; strip("rij_muren","wit",pts,0.25,0.9,ch=0.02)
        strip("rij_muren","wit",pts,0.36,0.08,0.9,ch=0.02,collide=False)
        for i in range(5):
            y=2.7+(GY0-2.7)*i/4
            put("rij_muren","wit",bbox(0.36,0.36,1.15,xg,y,0.575,0.02)); put("rij_muren","wit",blathe([(0,0),(0.12,0),(0.06,0.08),(0.09,0.16),(0,0.24)],8),TR(xg,y,1.15))
    path("klinkerrood",[((CX0+CX1)/2,1.6),((CX0+CX1)/2,GY0+0.3)],CX1-CX0-0.2)
    put("rijhal_vloer","klinkerrood",bzbox(0,0,GW-0.1,GE+0.2,GY0,GY1,0.0,0.095))
    for w in ([(GW,GY1),(GW,GY0)],[(GE,GY1),(GW,GY1)]):            # westmuur + noordmuur dicht
        strip("rijhal","stuc",w,0.3,H,ch=0.01); strip("rijhal","steen",w,0.38,0.3,0.0,collide=False)
    for w in ([(GW,GY0),(CX0,GY0)],[(CX1,GY0),(GE,GY0)],[(GE,GY0),(GE,28.2)]):   # lage borstwering zuid (met gang-opening) en oost
        strip("rijhal","stuc",w,0.3,1.0,ch=0.01); strip("rijhal","steen",w,0.45,0.1,1.0,ch=0.01,collide=False)
    COL=[(0,0),(0.13,0),(0.13,0.08),(0.1,0.12),(0.09,0.2),(0.075,1.9),(0.1,1.98),(0.13,2.04),(0.13,2.1),(0,2.1)]
    zuilen=[(GW+0.15,GY0),(9.5,GY0),(CX0,GY0),(CX1,GY0)]+[(GE,GY0+i*2.75) for i in range(8)]+[(GE,GY1)]
    for (x,y) in zuilen:
        k_=(H-1.22)/2.1; put("zuilen_rij","wit",blathe([(r,z*k_) for r,z in COL],10),TR(x,y,1.1)); coll(x,y,H/2,0.3,0.3,H)
    for w in ([(GW,GY0),(GE,GY0)],[(GE,GY0),(GE,GY1)]):          # architraaf + kroonlijst, plafond, plat dak
        strip("rijhal","wit",w,0.32,0.32,H-0.12,collide=False); strip("rijhal","wit",w,0.62,0.16,H+0.2,collide=False)
    for (x,y) in zuilen: urn("vazen",x,y,H+0.36,0.42,"wit")       # zijfoto: vaasjes op de dakrand boven de zuilen
    cb=bmesh.new(); vs=[cb.verts.new(p) for p in ((GW-0.1,GY0-0.15,H-0.1),(GE+0.3,GY0-0.15,H-0.1),(GE+0.3,GY1+0.15,H-0.1),(GW-0.1,GY1+0.15,H-0.1))]
    cb.faces.new(vs); bmesh.ops.reverse_faces(cb,faces=cb.faces); put("rijhal","plafond",cb)
    put("rijhal","zink",bzbox(0,0,GW-0.15,GE+0.45,GY0-0.2,GY1+0.25,H+0.21,H+0.33))
    for y in [10.2+i*2.6 for i in range(8)]:
        for xm in ((GW+GE)/2-2.0,(GW+GE)/2+2.0):
            put("plafondlampen","lamp",blathe([(0,0),(0.14,0),(0.12,0.04),(0,0.05)],10),TR(xm,y,H-0.16))
        LAMPS.append(((GW+GE)/2,y,H-0.35))
    for y in (12.0,19.8,27.0):
        put("speakers","groen",bbox(0.18,0.25,0.2,GW+0.25,y,H-0.35,0.02))
    put("logo","oranje",blathe([(0,0),(0.6,0),(0.6,0.06),(0,0.06)],20),TR(9.5,GY0-0.23,2.35)@Matrix.Rotation(math.radians(90),4,"X"))
    put("logo","goud",btube([(9.5,GY0-0.25,2.95),(9.5,GY0-0.25,H-0.12)],0.02,5))

    def hek(p,q,h=1.0):
        L=seglen(p,q); n=max(1,math.ceil(L/1.5)); a=math.degrees(math.atan2(q[1]-p[1],q[0]-p[0]))
        for zz,r in ((h*0.5,0.02),(h-0.04,0.022)):
            put("hekken","rijhek",btube([(p[0],p[1],zz),(q[0],q[1],zz)],r,6))
        for i in range(n+1):
            t=i/n; x=p[0]+(q[0]-p[0])*t; y=p[1]+(q[1]-p[1])*t
            put("hekken","rijhek",blathe([(0,0),(0.07,0),(0.07,0.03),(0.03,0.05),(0.028,h),(0.045,h+0.02),(0.05,h+0.06),(0.04,h+0.1),(0,h+0.11)],8),TR(x,y,0.1))
        coll((p[0]+q[0])/2,(p[1]+q[1])/2,h/2+0.1,L,0.12,h,a)
    # zigzag: 10 banen van 1.6 m dwars op de galerij, afwisselend open aan west/oost
    LX0,LX1=GW+0.15,GE-1.8; Y0,BW,NB=GY0+0.15,1.6,10
    for i in range(1,NB):
        y=Y0+i*BW
        if i%2==1: hek((LX0+1.6,y),(LX1,y))       # baan i en i+1 verbonden aan de westkant
        else:      hek((LX0,y),(LX1-1.6,y))       # verbonden aan de oostkant
    YE=Y0+NB*BW                                    # einde zigzag (~24.9)
    hek((LX1,Y0+1.2),(LX1,16.6)); hek((LX1,17.8),(LX1,YE-1.4))   # scheiding met de doorloop, poortjes ertussen
    hek((LX0,YE),(LX1-1.6,YE))                     # laatste baan loopt oost de doorloop in, dan west naar de tourniquets
    hek((10.6,YE+2.1),(GE-0.2,YE+2.1))             # noordkant uitgang-gang; erachter het rolstoelpad naar deur 2
    # afvalbakken: uit de looproute, in de hoeken
    for (x,y) in ((GE-0.5,GY1-0.5),(CX1+1.0,GY0-1.2),(CX0-1.5,GY0-1.0)):   # hoek + buiten naast de ingang
        put("afvalbakken","groen",bbox(0.55,0.55,1.0,x,y,0.6,0.02)); put("afvalbakken","groen",bbox(0.62,0.62,0.08,x,y,1.14,0.02))
        for (dx,dy) in ((1,0),(-1,0),(0,1),(0,-1)):          # dunne gouden lijst op elke zijde (foto)
            fx,fy=x+dx*0.283,y+dy*0.283
            for (u,zl,zh) in ((-0.19,0.3,0.95),(0.19,0.3,0.95)):
                put("afvalbakken","goud",bzbox(0,0,fx+(u if dy else 0)-0.015-(0.006 if dx else 0),fx+(u if dy else 0)+0.015+(0.006 if dx else 0),fy+(u if dx else 0)-0.015-(0.006 if dy else 0),fy+(u if dx else 0)+0.015+(0.006 if dy else 0),zl,zh))
            for zl in (0.3,0.92):
                put("afvalbakken","goud",bzbox(0,0,fx-(0.006 if dx else 0.205),fx+(0.006 if dx else 0.205),fy-(0.006 if dy else 0.205),fy+(0.006 if dy else 0.205),zl,zl+0.03))
        coll(x,y,0.6,0.6,0.6,1.1)
    # dubbel tourniquet (RVS) voor de dubbele deur, perkament met dolk
    TX=GW+2.2; TY=YE+1.05
    for y in (TY-0.55,TY,TY+0.55):
        put("tourniquets","rvs",bbox(0.9,0.22,1.0,TX,y,0.6,0.03)); put("tourniquets","rvs",bbox(0.95,0.26,0.04,TX,y,1.12,0.01)); coll(TX,y,0.6,0.9,0.22,1.0)
    for y in (TY-0.28,TY+0.28):
        for a in (0,120,240):
            d=Vector((0,math.cos(math.radians(a)),math.sin(math.radians(a))))*0.22
            put("tourniquets","rvs",btube([(TX+0.1,y-0.1,0.95),(TX+0.1,y-0.1+d.y,0.95+d.z)],0.02,6))
    for y in (TY,GY1-1.6):
        X=GW+0.16
        put("deuren","groen",bbox(0.08,1.8,2.4,X,y,1.3,0.01)); put("deuren","steen",bbox(0.12,2.3,0.3,X,y,2.65,0.02))
        for dy in (-1.05,1.05): put("deuren","steen",bbox(0.12,0.3,2.5,X,y+dy,1.35,0.01))
        put("deuren","rvs",bbox(0.06,0.04,0.4,X+0.06,y-0.12,1.2)); put("deuren","rvs",bbox(0.06,0.04,0.4,X+0.06,y+0.12,1.2))
    put("perkament","perkament",bbox(0.02,0.45,0.6,GW+0.17,TY+1.4,1.75,0.0))
    put("perkament","rvs",btube([(GW+0.15,TY+1.4,2.05),(GW+0.35,TY+1.4,2.0)],0.012,5)); put("perkament","hout",btube([(GW+0.35,TY+1.4,2.0),(GW+0.5,TY+1.4,1.98)],0.022,6))
    # vier bokkenhuiden in een ruw houten lijst op de westmuur
    HUID=[(-0.3,-0.45),(-0.1,-0.5),(0.12,-0.46),(0.3,-0.5),(0.36,-0.3),(0.3,0.0),(0.38,0.32),(0.28,0.45),(0.08,0.4),(-0.12,0.46),(-0.3,0.42),(-0.36,0.25),(-0.3,0.0),(-0.4,-0.3)]
    y0,zc=15.2,1.85
    for k in range(4):
        yc=y0+0.95*k; X=wx(yc)+0.17
        hb=bmesh.new(); vs=[hb.verts.new((0,u*1.0,v*1.1)) for u,v in HUID]; f=hb.faces.new(vs)
        r=bmesh.ops.extrude_face_region(hb,geom=[f]); bmesh.ops.translate(hb,vec=(0.015,0,0),verts=[g for g in r["geom"] if isinstance(g,bmesh.types.BMVert)])
        bmesh.ops.recalc_face_normals(hb,faces=hb.faces); put("bokkenhuiden","huid",hb,TR(X,yc,zc))
    X=wx(16.6)+0.2
    for zz_ in (zc-0.68,zc+0.68):
        put("bokkenhuiden","hout",btube([(X,y0-0.62,zz_+0.03),(X,y0+0.6,zz_-0.02),(X,y0+1.9,zz_+0.02),(X,y0+3.47,zz_-0.03)],0.04,6))
    for yy in (y0-0.55,y0+0.47,y0+1.42,y0+2.37,y0+3.4):
        put("bokkenhuiden","hout",btube([(X,yy,zc-0.8),(X,yy+0.03,zc),(X,yy-0.02,zc+0.8)],0.035,6))
    # buitenpad (rolstoel/single rider) langs de oostkant met haag, komt aan de noordkant de galerij in
    path("klinkerrood",[(CX1+0.5,1.6),(GE+1.0,2.4),(GE+1.0,29.3),(GE-0.5,29.3)],1.2)
    strip("hagen","haag",[(CX1+1.4,1.4),(GE+2.1,2.6),(GE+2.1,GY1+0.4),(GE+0.3,GY1+0.4)],0.6,1.4,ch=0.15)
    # ---------------- paden: samengevoegde vlakken + opsluitbanden (exports/paden_poly.json) ----------------
    MATS.update({"plein":((0.62,0.50,0.42,1),0.9),"band":((0.70,0.69,0.66,1),0.85)})
    for n_,(c_,r_) in MATS.items(): material("MAT_"+n_,c_,r_)
    PP=json.load(open(os.path.join(HERE,"..","exports","paden_poly.json")))
    def slab(poly,zt,mat):
        bm=bmesh.new(); edges=[]
        for ring in [poly["ext"]]+poly["holes"]:
            vs=[bm.verts.new((x,y,zt)) for x,y in ring]
            edges+=[bm.edges.new((vs[i],vs[(i+1)%len(vs)])) for i in range(len(vs))]
        bmesh.ops.triangle_fill(bm,use_beauty=True,use_dissolve=False,edges=edges)
        bnd=[e for e in bm.edges if e.is_boundary]
        r=bmesh.ops.extrude_edge_only(bm,edges=bnd)
        bmesh.ops.translate(bm,vec=(0,0,-zt-0.05),verts=[g for g in r["geom"] if isinstance(g,bmesh.types.BMVert)])
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        put("paden",mat,bm)
    for m_,zt in (("grind",0.05),("klinker",0.05),("klinkerrood",0.05),("plein",0.05),("band",0.075)):
        for poly in PP[m_]: slab(poly,zt,m_)
    # ---------------- objecten ----------------
    n=0; tris=0
    for (part,mat),bm in PARTS.items():
        bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5)
        ob=new_mesh_object(f"VO_{part}__{mat}",bm,"OMGEVING"); assign(ob,bpy.data.materials["MAT_"+mat])
        if mat in ("ijzer","zink","wit","lamp","beuk","haag","buxus") or part in ("bloemen","vazen","tuinbeelden"): shade_smooth(ob,math.radians(40))
        n+=1; tris+=sum(len(p.vertices)-2 for p in ob.data.polygons)
    out=os.path.join(HERE,"..","exports"); os.makedirs(out,exist_ok=True)
    json.dump({"colliders":COLL,"lamps":[[round(v,2) for v in l] for l in LAMPS],
               "doors":[[7.33,26.03],[7.36,28.93]],"wachtbord":[bx,by],"ingangbord":[13.1,10.55,0.75],"logo":[9.3,8.55,2.35],"paden":PADEN,"huiden":[[round(GW+0.19,3),round(15.2+0.95*k,3),1.85] for k in range(4)]},open(os.path.join(out,"omgeving_data.json"),"w"))
    save_master(master); log("objects",n,"tris~",tris,"colliders",len(COLL),"lamps",len(LAMPS))
if __name__=="__main__":
    a=argv_after_dashes(); m=a[a.index("--master")+1] if "--master" in a else None
    if m: build(m)
