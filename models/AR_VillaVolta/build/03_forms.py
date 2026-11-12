"""03_forms Villa Volta: echte vormen over de goedgekeurde blokkering (02b).
Meters, Z op, voorgevel hoofdblok op y=0 naar -Y, z=0 maaiveld, terrasvloer z=T.
Maten uit ref/front.jpg op 37 px/m (zie asset-brief.md); diepte en zijgevels inferred.
Elk onderdeel wordt in een bmesh verzameld en als object VV_<deel>__<materiaal> in collectie FORMS gezet."""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix
PHASE="03_forms"; OWNER_TAG="phase:"+PHASE
TEMPLATE=os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src=open(TEMPLATE).read().split("# ARGS AND FILE HANDLING",1)[1]
_ns={"bpy":bpy,"bmesh":bmesh,"sys":sys,"os":os,"math":math,"Vector":Vector,"Matrix":Matrix,"PHASE":PHASE,"OWNER_TAG":OWNER_TAG}
exec(_src,_ns); globals().update({k:v for k,v in _ns.items() if callable(v)})

# ---- maten (front.jpg, 37 px/m, terrasvloer y507) ----
T=0.8                 # terras
MW,MD=8.0,10.0        # hoofdblok breed (205-500 px) / diep (inferred)
WW,WD,WY=2.6,6.0,0.4  # vleugel breed (115-205 px), diep (inferred), terugsprong t.o.v. hoofdblok (inferred)
CM,CW=7.8,6.9         # bovenkant kroonlijst hoofdblok / vleugel boven terrasvloer
ENT_M,ENT_W=0.7,0.6   # hoogte hoofdgestel
COLX,COLY=3.65,-1.4   # zuilen hart-op-hart 7.3 (225/493 px)
BAL_Z0,BAL_Z1,BAL_TOP=4.4,4.8,5.9   # balkon onderkant/vloer, balustrade top
DOOR_W,DOOR_H=2.4,3.05
HX=MW/2; WX=HX+WW     # buitenkant vleugel x=6.6

MATS={
 "stuc":((0.84,0.75,0.56,1),0.9),  "steen":((0.80,0.77,0.68,1),0.8), "wit":((0.90,0.89,0.84,1),0.7),
 "lei":((0.24,0.25,0.28,1),0.75),  "zink":((0.47,0.50,0.52,1),0.5),  "groen":((0.08,0.20,0.15,1),0.45),
 "glas":((0.06,0.08,0.10,1),0.15), "kozijn":((0.93,0.93,0.90,1),0.5), "letter":((0.10,0.16,0.13,1),0.4),
 "hal":((0.28,0.30,0.27,1),0.9),
}
PARTS={}
def put(part,mat,bm,M=None):
    if M is not None: bmesh.ops.transform(bm,matrix=M,verts=bm.verts)
    key=(part,mat)
    if key not in PARTS: PARTS[key]=bmesh.new()
    me=bpy.data.meshes.new("_t"); bm.to_mesh(me); bm.free()
    PARTS[key].from_mesh(me); bpy.data.meshes.remove(me)

def TR(x=0,y=0,z=0,rz=0): return Matrix.Translation((x,y,z))@Matrix.Rotation(math.radians(rz),4,"Z")

# ---- primitieven (bmesh) ----
def bbox(sx,sy,sz,cx=0,cy=0,cz=0,ch=0.0):
    bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0); bmesh.ops.scale(bm,vec=(sx,sy,sz),verts=bm.verts)
    if ch>0:
        try: bmesh.ops.bevel(bm,geom=list(bm.edges),offset=min(ch,sx/3,sy/3,sz/3),segments=1,affect="EDGES",profile=0.5)
        except TypeError: bmesh.ops.bevel(bm,geom=list(bm.edges),offset=min(ch,sx/3,sy/3,sz/3),segments=1,vertex_only=False,profile=0.5)
    bmesh.ops.translate(bm,vec=(cx,cy,cz),verts=bm.verts); return bm
def bzbox(sx,sy,x0,x1,y0,y1,z0,z1,ch=0.0):   # box tussen grenzen
    return bbox(x1-x0,y1-y0,z1-z0,(x0+x1)/2,(y0+y1)/2,(z0+z1)/2,ch)
def blathe(profile,segs=12,cap=True):
    bm=bmesh.new(); vs=[bm.verts.new((max(r,0.0),0,z)) for r,z in profile]
    es=[bm.edges.new((vs[i],vs[i+1])) for i in range(len(vs)-1)]
    bmesh.ops.spin(bm,geom=vs+es,cent=(0,0,0),axis=(0,0,1),angle=math.tau,steps=segs,use_merge=True)
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); return bm
def bsweep(profile,x0,x1,y0,y1,z0,back=True,caps=False):
    """profiel [(uitsteek,z)] rond rechthoek x0..x1, y0..y1 (voor = y0). back=False: alleen voor+zijkanten."""
    bm=bmesh.new(); rings=[]
    for o,z in profile:
        if back: pts=[(x0-o,y0-o),(x1+o,y0-o),(x1+o,y1+o),(x0-o,y1+o)]
        else:    pts=[(x0-o,y1),(x0-o,y0-o),(x1+o,y0-o),(x1+o,y1)]
        rings.append([bm.verts.new((px,py,z0+z)) for px,py in pts])
    n=len(rings[0])
    for a,b in zip(rings,rings[1:]):
        for i in range(n if back else n-1):
            j=(i+1)%n
            try: bm.faces.new((a[i],a[j],b[j],b[i]))
            except ValueError: pass
    if caps:   # alleen zonder kern eronder: anders samenvallende vlakken (zwart in Cycles)
        bm.faces.new(rings[-1]); bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces); return bm
def boutline(pts_xz,y0,depth):
    """gesloten omtrek in het XZ-vlak (vooraanzicht) op y0, geextrudeerd naar +Y over depth"""
    bm=bmesh.new(); vs=[bm.verts.new((x,y0,z)) for x,z in pts_xz]; f=bm.faces.new(vs)
    r=bmesh.ops.extrude_face_region(bm,geom=[f]); top=[g for g in r["geom"] if isinstance(g,bmesh.types.BMVert)]
    bmesh.ops.translate(bm,vec=(0,depth,0),verts=top); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); return bm
def btube(points,r,segs=6):
    bm=bmesh.new(); P=[Vector(p) for p in points]; rings=[]; up=Vector((0,0,1))
    for i,p in enumerate(P):
        t=(P[min(i+1,len(P)-1)]-P[max(i-1,0)]).normalized()
        a=t.cross(up);
        if a.length<1e-4: a=t.cross(Vector((1,0,0)))
        a.normalize(); b=t.cross(a)
        rings.append([bm.verts.new(p+(a*math.cos(k*math.tau/segs)+b*math.sin(k*math.tau/segs))*r) for k in range(segs)])
    for A,B in zip(rings,rings[1:]):
        for k in range(segs): bm.faces.new((A[k],A[(k+1)%segs],B[(k+1)%segs],B[k]))
    bm.faces.new(rings[0]); bm.faces.new(list(reversed(rings[-1])))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces); return bm
def arc(cx,cz,r,a0,a1,n):
    return [(cx+r*math.cos(math.radians(a0+(a1-a0)*i/n)),cz+r*math.sin(math.radians(a0+(a1-a0)*i/n))) for i in range(n+1)]
def spiral(cx,cy,cz,r0,turns,n,plane="XZ",sign=1):
    pts=[]
    for i in range(n+1):
        t=i/n; a=sign*t*turns*math.tau; r=r0*(1-0.8*t)
        if plane=="XZ": pts.append((cx+r*math.cos(a),cy,cz+r*math.sin(a)))
        else: pts.append((cx,cy+r*math.cos(a),cz+r*math.sin(a)))
    return pts

URN=[(0,0),(0.13,0),(0.13,0.06),(0.07,0.09),(0.06,0.16),(0.10,0.22),(0.19,0.36),(0.21,0.48),(0.18,0.56),(0.21,0.60),(0.21,0.65),(0.12,0.68),(0.06,0.76),(0.03,0.86),(0,0.88)]
BALUSTER=[(0,0),(0.07,0),(0.07,0.05),(0.05,0.08),(0.05,0.12),(0.085,0.26),(0.09,0.34),(0.06,0.48),(0.035,0.56),(0.05,0.60),(0.05,0.64),(0.07,0.66),(0.07,0.70),(0,0.70)]
def urn(part,x,y,z,s=1.0,mat="wit"):
    put(part,mat,blathe([(r*s,h*s) for r,h in URN],12),TR(x,y,z))
    put(part,mat,bbox(0.3*s,0.3*s,0.06*s,x,y,z+0.03*s))   # voetplaat

def balustrade(part,x0,x1,y,z0,height,mat="wit",pedestals=(),depthwise=False):
    """balustrade langs x (of langs y als depthwise) met voetregel, balusters, dekplaat en postamenten"""
    L=x1-x0; h_b=height-0.30; s=h_b/0.70
    put(part,mat,bzbox(0,0,x0,x1,y-0.13,y+0.13,z0,z0+0.12) if not depthwise else bzbox(0,0,y-0.13,y+0.13,x0,x1,z0,z0+0.12))
    for (a,b,c) in ((0.17,z0+height-0.18,z0+height-0.06),(0.20,z0+height-0.06,z0+height)):
        put(part,mat,bzbox(0,0,x0-0.02,x1+0.02,y-a,y+a,b,c) if not depthwise else bzbox(0,0,y-a,y+a,x0-0.02,x1+0.02,b,c))
    occupied=[(p-0.25,p+0.25) for p in pedestals]
    n=max(1,int(L/0.2)); step=L/n
    for i in range(n):
        u=x0+step*(i+0.5)
        if any(a<u<b for a,b in occupied): continue
        bm=blathe([(r*0.78,h*s) for r,h in BALUSTER],8)   # slank: breedte niet meeschalen
        M=TR(u,y,z0+0.12) if not depthwise else TR(y,u,z0+0.12)
        put(part,mat,bm,M)
    for p in pedestals:
        cx,cy=(p,y) if not depthwise else (y,p)
        put(part,mat,bbox(0.42,0.42,height-0.1,cx,cy,z0+(height-0.1)/2,0.01))
        put(part,mat,bbox(0.5,0.5,0.1,cx,cy,z0+height-0.05,0.01))
        put(part,mat,bbox(0.48,0.48,0.12,cx,cy,z0+0.06,0.01))

def window(face_M,x,z0,w,h,kind,cutters):
    """raam in een wand; lokaal: wandvlak y=0, buiten = -Y. kind: 'fronton','oor','gewoon'"""
    zc=z0+h/2
    cutters.append((bzbox(0,0,x-w/2,x+w/2,-0.2,0.25,z0,z0+h),face_M))
    put("ramen_glas","glas",bzbox(0,0,x-w/2,x+w/2,0.16,0.18,z0,z0+h),face_M)
    k=0.05   # kozijn
    for b in (bzbox(0,0,x-w/2,x-w/2+k,0.10,0.16,z0,z0+h),bzbox(0,0,x+w/2-k,x+w/2,0.10,0.16,z0,z0+h),
              bzbox(0,0,x-w/2,x+w/2,0.10,0.16,z0,z0+k),bzbox(0,0,x-w/2,x+w/2,0.10,0.16,z0+h-k,z0+h),
              bzbox(0,0,x-0.02,x+0.02,0.11,0.16,z0,z0+h),bzbox(0,0,x-w/2,x+w/2,0.11,0.16,z0+h*0.62-0.02,z0+h*0.62+0.02)):
        put("ramen_kozijn","kozijn",b,face_M)
    # roeden
    for fz in (0.31,):
        put("ramen_kozijn","kozijn",bzbox(0,0,x-w/2,x+w/2,0.12,0.16,z0+h*fz-0.012,z0+h*fz+0.012),face_M)
    s=0.13  # stenen omlijsting
    for b in (bzbox(0,0,x-w/2-s,x-w/2,-0.05,0.05,z0,z0+h),bzbox(0,0,x+w/2,x+w/2+s,-0.05,0.05,z0,z0+h),
              bzbox(0,0,x-w/2-s,x+w/2+s,-0.05,0.05,z0+h,z0+h+s)):
        put("omlijsting","steen",b,face_M)
    put("omlijsting","steen",bzbox(0,0,x-w/2-0.2,x+w/2+0.2,-0.10,0.06,z0-0.09,z0,0.01),face_M)   # dorpel
    put("omlijsting","steen",bzbox(0,0,x-0.1,x+0.1,-0.07,0.05,z0+h-0.02,z0+h+s+0.04),face_M)     # sluitsteen
    if kind=="oor":
        for sx in (-1,1):
            xa,xb=x+sx*(w/2+s),x+sx*(w/2+s+0.07)
            put("omlijsting","steen",bzbox(0,0,min(xa,xb),max(xa,xb),-0.05,0.05,z0+h-0.15,z0+h+s),face_M)
        put("omlijsting","steen",bzbox(0,0,x-w/2-0.3,x+w/2+0.3,-0.14,0.05,z0+h+s,z0+h+s+0.08,0.01),face_M)
    if kind=="fronton":
        zb=z0+h+s; ww=w/2+0.3
        put("omlijsting","steen",bzbox(0,0,x-ww,x+ww,-0.14,0.05,zb,zb+0.07,0.01),face_M)
        tri=[(x-ww,zb+0.07),(x+ww,zb+0.07),(x,zb+0.07+0.38)]
        put("omlijsting","steen",boutline(tri,-0.12,0.17),face_M)

def build(master):
    open_master(master); clear_owned()
    for n,(c,r) in MATS.items(): material("MAT_"+n,c,r)
    cutters=[]
    FRONT=Matrix.Identity(4)
    # ---------------- terras, trappen, borstweringen ----------------
    put("terras","steen",bzbox(0,0,-8.6,8.6,-5.0,6.4,0,T-0.12))
    put("terras","steen",bsweep([(0.0,0),(0.08,0.02),(0.08,0.12),(0,0.12)],-8.6,8.6,-5.0,6.4,T-0.12))
    put("terras","steen",bzbox(0,0,-8.55,8.55,-4.95,6.35,T-0.12,T))
    for i in range(4):   # treden: onderste het breedst (front.jpg 50-695 px)
        w=9.5+2.4*(3-i); y0=-5.0-0.35*(4-i); zt=T*(i+1)/4
        put("trap","steen",bzbox(0,0,-w/2,w/2,y0,-5.0,0,zt-0.04))
        put("trap","steen",bzbox(0,0,-w/2-0.03,w/2+0.03,y0-0.04,-5.0,zt-0.05,zt,0.01))   # neus
    for s in (-1,1):
        # borstwering langs de vleugel (front.jpg 20-205 px, 0.8 hoog) + zijkant terras
        put("borstwering","steen",bzbox(0,0,min(s*4.6,s*8.5),max(s*4.6,s*8.5),-0.55,-0.25,T,T+0.68))
        put("borstwering","steen",bzbox(0,0,min(s*4.55,s*8.55),max(s*4.55,s*8.55),-0.62,-0.18,T+0.68,T+0.8,0.01))
        put("borstwering","steen",bzbox(0,0,min(s*8.25,s*8.55),max(s*8.25,s*8.55),-0.55,6.4,T,T+0.8,0.01))
        for px in (4.6,6.7,8.4):
            put("borstwering","steen",bbox(0.5,0.5,0.95,s*px,-0.4,T+0.475,0.015))
            urn("vazen",s*px,-0.4,T+0.95,1.05)
        # plantvazen voor de deurpijlers (front.jpg 262/445 px)
        put("borstwering","steen",bbox(0.45,0.45,0.75,s*2.45,-1.0,T+0.375,0.015))
        urn("vazen",s*2.45,-1.0,T+0.75,1.0)
    # ---------------- muren met raamgaten ----------------
    wall=bmesh.new()
    def addwall(bm):
        me=bpy.data.meshes.new("_w"); bm.to_mesh(me); bm.free(); wall.from_mesh(me); bpy.data.meshes.remove(me)
    addwall(bzbox(0,0,-HX,HX,0,MD,T,T+CM-ENT_M+0.02))
    for s in (-1,1):
        addwall(bzbox(0,0,min(s*HX,s*WX),max(s*HX,s*WX),WY,WY+WD,T,T+CW-ENT_W+0.02))
    # sokkel + waterlijst
    put("sokkel","steen",bsweep([(0.06,0),(0.06,0.45),(0.03,0.5),(0,0.5)],-HX,HX,0,MD,T))
    for s in (-1,1):
        put("sokkel","steen",bsweep([(0.06,0),(0.06,0.45),(0.03,0.5),(0,0.5)],min(s*HX,s*WX),max(s*HX,s*WX),WY,WY+WD,T))
    # cordonlijst eerste verdieping (balkonhoogte)
    for x0,x1,y0,y1 in ((-HX,HX,0,MD),(-WX,-HX,WY,WY+WD),(HX,WX,WY,WY+WD)):
        put("lijsten","steen",bsweep([(0,0),(0.07,0.02),(0.07,0.16),(0.04,0.2),(0,0.2)],x0,x1,y0,y1,T+BAL_Z0))
    # hoekblokken (rustica), om en om lang/kort, 0.45 hoog
    def quoins(x,y,sx,z_top,face_y_dir=-1):
        z=T+0.5; i=0
        while z+0.42<=z_top:
            lw=0.62 if i%2==0 else 0.42
            put("hoekblokken","steen",bzbox(0,0,min(x,x-sx*lw),max(x,x-sx*lw),y-0.06,y+0.3,z,z+0.41,0.025))
            put("hoekblokken","steen",bzbox(0,0,min(x,x+sx*0.06),max(x,x+sx*0.06),y-0.06,y+(0.42 if i%2==0 else 0.62),z,z+0.41,0.025))
            z+=0.45; i+=1
    for s in (-1,1):
        quoins(s*HX,0,s,T+CM-ENT_M)
        quoins(s*WX,WY,s,T+CW-ENT_W)
        # pilasters achter de zuilen
        put("pilasters","steen",bzbox(0,0,s*COLX-0.28,s*COLX+0.28,-0.08,0.02,T+0.5,T+BAL_Z0,0.01))
    # ramen vleugels (front.jpg: bg 0.6x1.0 op 1.1 met fronton, 1e 0.6x1.0 op 4.7 met oren)
    for s in (-1,1):
        x=s*(HX+WW/2)
        Mf=TR(0,WY,0)
        window(Mf,x,T+1.1,0.62,1.05,"fronton",cutters)
        window(Mf,x,T+4.75,0.62,1.05,"oor",cutters)
        # zijgevels (inferred): vleugel buitenzijde, hoofdblok achter de vleugel
        Ms=TR(s*WX,0,0,90 if s>0 else -90)
        for yy in (2.4,4.6):
            u=yy if s>0 else -yy   # R(+90) zet lokaal x op wereld +y
            window(Ms,u,T+1.1,0.62,1.05,"fronton",cutters); window(Ms,u,T+4.75,0.62,1.05,"oor",cutters)
        Mh=TR(s*HX,0,0,90 if s>0 else -90)
        for yy in (7.6,):
            u=yy if s>0 else -yy
            window(Mh,u,T+1.1,0.9,1.6,"fronton",cutters); window(Mh,u,T+4.75,0.9,1.5,"oor",cutters)
    # balkondeur (front.jpg 315-385 px, 4.9-6.4)
    window(FRONT,0,T+BAL_Z1+0.05,1.7,1.55,"gewoon",cutters)
    # voordeur: rondboog, 2.4 x 3.05
    R=DOOR_W/2; zs=T+DOOR_H-R
    door_outline=[(-R,T),(R,T)]+[(x,z) for x,z in arc(0,zs,R,0,180,16)]
    cutters.append((boutline([(x,z) for x,z in door_outline],-0.2,0.45),FRONT))
    # muren + gaten
    me=bpy.data.meshes.new("VV_muren__stuc"); wall.to_mesh(me); wall.free()
    wob=bpy.data.objects.new("VV_muren__stuc",me); col("FORMS").objects.link(wob); own(wob); assign(wob,bpy.data.materials["MAT_stuc"])
    cut=bmesh.new()
    for bm,M in cutters:
        bmesh.ops.transform(bm,matrix=M,verts=bm.verts); m2=bpy.data.meshes.new("_c"); bm.to_mesh(m2); bm.free(); cut.from_mesh(m2); bpy.data.meshes.remove(m2)
    cme=bpy.data.meshes.new("_cutter"); cut.to_mesh(cme); cut.free()
    cob=bpy.data.objects.new("_cutter",cme); col("FORMS").objects.link(cob)
    b=wob.modifiers.new("cut","BOOLEAN"); b.object=cob; b.operation="DIFFERENCE"; b.solver="EXACT"
    apply_all_modifiers(wob); bpy.data.objects.remove(cob,do_unlink=True); bpy.data.meshes.remove(cme)
    # deurvleugels, glas, omlijsting, ornament
    put("deur","groen",boutline([(x*0.99,z) for x,z in door_outline],0.18,0.08))
    for sx in (-1,1):
        x0=sx*0.08; x1=sx*(R-0.12)
        put("deur_glas","glas",bzbox(0,0,min(x0+sx*0.14,x1),max(x0+sx*0.14,x1),0.15,0.18,T+1.35,T+2.35))
        for k in range(3):   # roeden
            zz=T+1.35+k*0.333
            put("deur_roeden","kozijn",bzbox(0,0,min(x0+sx*0.14,x1),max(x0+sx*0.14,x1),0.13,0.15,zz-0.015,zz+0.015))
        xm=(x0+sx*0.14+x1)/2
        put("deur_roeden","kozijn",bzbox(0,0,xm-0.015,xm+0.015,0.13,0.15,T+1.35,T+2.35))
        for (za,zb) in ((T+0.25,T+1.15),):   # paneel onder
            put("deur","groen",bzbox(0,0,min(x0+sx*0.14,x1),max(x0+sx*0.14,x1),0.13,0.18,za,zb,0.02))
    put("deur","groen",bzbox(0,0,-0.03,0.03,0.12,0.18,T,zs+R-0.05))
    ro,ri=R+0.22,R
    ring=[(-ro,T),(-ri,T)]+[(x,z) for x,z in arc(0,zs,ri,180,0,16)]+[(ri,T),(ro,T)]+[(x,z) for x,z in arc(0,zs,ro,0,180,16)]
    put("deur_omlijsting","steen",boutline(ring,-0.07,0.12))
    put("deur_omlijsting","steen",boutline([(-0.16,zs+R-0.05),(0.16,zs+R-0.05),(0.22,zs+R+0.32),(-0.22,zs+R+0.32)],-0.14,0.16))   # sluitsteen
    # pijlers naast de deur (287-305 / 393-410 px) met rustica-blokken en vazen erop
    for s in (-1,1):
        xc=s*1.75
        put("deur_omlijsting","steen",bzbox(0,0,xc-0.24,xc+0.24,-0.16,0.02,T,T+2.85,0.01))
        z=T+0.15
        while z<T+2.6:
            put("deur_omlijsting","steen",bzbox(0,0,xc-0.27,xc+0.27,-0.21,-0.1,z,z+0.3,0.03)); z+=0.36
        put("deur_omlijsting","steen",bzbox(0,0,xc-0.32,xc+0.32,-0.24,0.02,T+2.85,T+3.0,0.015))
        urn("vazen",xc,-0.1,T+3.0,0.65,"steen")
    # cartouche boven de deur (front.jpg 330-370 px, tot 3.8): schelp + voluten
    zc=T+DOOR_H+0.32
    for k in range(9):
        a=math.radians(15+k*18.75)
        ray=btube([(0,-0.12,zc),(0.42*math.cos(a),-0.16,zc+0.42*math.sin(a))],0.045,5)
        put("ornament","steen",ray)
    for sx in (-1,1):
        put("ornament","steen",btube(spiral(sx*0.5,-0.13,zc+0.05,0.16,1.4,18,"XZ",sx),0.035,5))
    put("ornament","steen",bbox(1.1,0.1,0.08,0,-0.1,zc-0.02,0.01))
    # ---------------- zuilen (ionisch) ----------------
    SHAFT=[(0,0),(0.3,0),(0.3,0.06),(0.26,0.09),(0.27,0.15),(0.23,0.2),(0.21,0.24),(0.205,1.4),(0.195,2.8),(0.175,3.95),
           (0.2,3.98),(0.2,4.03),(0.18,4.05),(0.22,4.13),(0.25,4.2),(0,4.2)]
    for s in (-1,1):
        put("zuilen","steen",bbox(0.62,0.62,0.22,s*COLX,COLY,T+0.11,0.015))
        put("zuilen","steen",blathe(SHAFT,16),TR(s*COLX,COLY,T+0.22-0.02))
        put("zuilen","steen",bbox(0.6,0.6,0.08,s*COLX,COLY,T+BAL_Z0-0.04,0.01))
        for vx in (-1,1):
            put("zuilen","steen",btube(spiral(s*COLX+vx*0.24,COLY-0.27,T+BAL_Z0-0.17,0.1,1.25,14,"XZ",-vx) ,0.03,5))
            put("zuilen","steen",bbox(0.16,0.54,0.16,s*COLX+vx*0.22,COLY,T+BAL_Z0-0.17,0.05))
    # ---------------- balkon ----------------
    BX=3.85; BY=-1.85
    put("balkon","steen",bzbox(0,0,-BX,BX,BY,0,T+BAL_Z0+0.12,T+BAL_Z1))
    put("balkon","steen",bsweep([(-0.25,0),(-0.1,0.02),(-0.04,0.07),(0,0.12),(0.06,0.14),(0.06,0.24),(0.03,0.28),(0.06,0.32),(0.06,0.40),(0,0.4)],-BX,BX,BY,0.0,T+BAL_Z0,back=False))
    # consoles onder het balkon tussen de zuilen
    for x in (-2.2,-0.75,0.75,2.2):
        put("balkon","steen",boutline([(x-0.12,T+BAL_Z0-0.45),(x+0.12,T+BAL_Z0-0.45),(x+0.12,T+BAL_Z0+0.12),(x-0.12,T+BAL_Z0+0.12)],-0.05,0.07))
        put("balkon","steen",bzbox(0,0,x-0.1,x+0.1,BY+0.25,0,T+BAL_Z0-0.08,T+BAL_Z0+0.12,0.02))
    balustrade("balkon_balustrade",-BX+0.05,BX-0.05,BY+0.18,T+BAL_Z1,BAL_TOP-BAL_Z1,"wit",pedestals=(-COLX,-1.15,1.15,COLX))
    for s in (-1,1):
        balustrade("balkon_balustrade",BY+0.18,-0.05,s*COLX,T+BAL_Z1,BAL_TOP-BAL_Z1,"wit",pedestals=(),depthwise=True)
        urn("vazen",s*COLX,BY+0.18,T+BAL_TOP,1.1)
    # ---------------- opschrift (285-410 px, 6.5-6.9) ----------------
    put("opschrift","steen",bzbox(0,0,-1.75,1.75,-0.08,0.02,T+6.45,T+6.95,0.015))
    for sx in (-1,1):
        put("opschrift","steen",btube(spiral(sx*1.95,-0.06,T+6.7,0.2,1.3,16,"XZ",sx),0.035,5))
    cu=bpy.data.curves.new("_txt","FONT"); cu.body="VILLA VOLTA"; cu.size=0.33; cu.extrude=0.015; cu.align_x="CENTER"; cu.align_y="CENTER"
    tob=bpy.data.objects.new("_txt",cu); col("FORMS").objects.link(tob)
    tob.rotation_euler=(math.radians(90),0,0); tob.location=(0,-0.1,T+6.7)
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get(); tme=bpy.data.meshes.new_from_object(tob.evaluated_get(dg))
    tbm=bmesh.new(); tbm.from_mesh(tme); bmesh.ops.transform(tbm,matrix=tob.matrix_world,verts=tbm.verts)
    bpy.data.objects.remove(tob,do_unlink=True); bpy.data.curves.remove(cu); bpy.data.meshes.remove(tme)
    put("letters","letter",tbm)
    # ---------------- hoofdgestellen ----------------
    ENT=[(0,0),(0.05,0),(0.05,0.10),(0.02,0.12),(0.02,0.38),(0.07,0.40),(0.10,0.44),(0.12,0.46),(0.26,0.53),(0.32,0.58),(0.32,0.66),(0.36,0.68),(0.36,0.7),(0,0.7)]
    put("hoofdgestel","steen",bsweep(ENT,-HX,HX,0,MD,T+CM-ENT_M))
    for s in (-1,1):
        x0,x1=min(s*HX,s*WX),max(s*HX,s*WX)
        put("hoofdgestel","steen",bsweep([(o*0.86,z*ENT_W/ENT_M) for o,z in ENT],x0,x1,WY,WY+WD,T+CW-ENT_W))
    # tandlijst (consoles) onder de kroonlijst hoofdblok, voorgevel
    for i in range(23):
        x=-HX+0.2+i*(MW-0.4)/22
        put("hoofdgestel","steen",bzbox(0,0,x-0.05,x+0.05,-0.26,0,T+CM-0.26,T+CM-0.14))
    # ---------------- mansardedaken ----------------
    def mansard(part,x0,x1,y0,y1,z0,z1,z2,i1,i2,o=0.25):
        bm=bmesh.new()
        def ring(off,z): return [bm.verts.new(p) for p in ((x0-off,y0-off,z),(x1+off,y0-off,z),(x1+off,y1+off,z),(x0-off,y1+off,z))]
        r0=ring(o,z0); r1=ring(o-i1,z1); r2=ring(o-i2,z2)
        for a,b in ((r0,r1),(r1,r2)):
            for i in range(4): bm.faces.new((a[i],a[(i+1)%4],b[(i+1)%4],b[i]))
        bm.faces.new(r2); bm.faces.new(list(reversed(r0)))
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces); put(part,"lei",bm)
        cr=lambda r:[v.co.copy() for v in r]
        return [ (x0-o,y0-o,z0),(x1+o,y0-o,z0),(x1+o,y1+o,z0),(x0-o,y1+o,z0)], \
               [ (x0-o+i1,y0-o+i1,z1),(x1+o-i1,y0-o+i1,z1),(x1+o-i1,y1+o-i1,z1),(x0-o+i1,y1+o-i1,z1)], \
               [ (x0-o+i2,y0-o+i2,z2),(x1+o-i2,y0-o+i2,z2),(x1+o-i2,y1+o-i2,z2),(x0-o+i2,y1+o-i2,z2)]
    # hoofdblok: steil 7.8->9.7, flauw tot 9.9; knik 1.6 naar binnen (overlay 02b)
    r0,r1,r2=mansard("daken",-HX,HX,0,MD,T+CM,T+9.7,T+9.95,1.55,2.2)
    for a,b in zip(r0,r1): put("dak_lood","zink",btube([a,b],0.06,6))
    for a,b in zip(r1,r2): put("dak_lood","zink",btube([a,b],0.05,6))
    loop=r1+[r1[0]]; put("dak_lood","zink",btube(loop,0.05,6))
    loop2=r2+[r2[0]]; put("dak_lood","zink",btube(loop2,0.05,6))
    for p in r1[:2]:   # siervazen op de knik voor (front.jpg 270/415 px)
        urn("dak_vazen",p[0],p[1],p[2],0.75,"steen")
    for p in r2:       # pinakels op de nok
        put("dak_lood","zink",blathe([(0,0),(0.08,0),(0.08,0.08),(0.03,0.12),(0.05,0.2),(0.012,0.5),(0,0.55)],8),TR(*p))
    for s in (-1,1):
        x0,x1=min(s*HX,s*WX),max(s*HX,s*WX)
        q0,q1,q2=mansard("daken",x0,x1,WY,WY+WD,T+CW,T+8.1,T+8.4,0.5,0.95,0.2)
        for a,b in zip(q0,q1): put("dak_lood","zink",btube([a,b],0.05,6))
        put("dak_lood","zink",btube(q1+[q1[0]],0.04,6))
        for p in (q2[0],q2[1]) if s<0 else (q2[0],q2[1]):
            put("dak_lood","zink",blathe([(0,0),(0.06,0),(0.06,0.06),(0.02,0.1),(0.04,0.16),(0.01,0.38),(0,0.42)],8),TR(*p))
        # dakraam vleugel met rondboog (front.jpg 165-185 px, 7.5-8.1)
        xc=s*(HX+WW/2); zb=T+CW+0.05
        put("dakkapel_v","stuc",bzbox(0,0,xc-0.45,xc+0.45,WY-0.05,WY+0.9,zb,zb+0.8))
        put("dakkapel_v","steen",boutline([(xc-0.5,zb+0.8)]+[(x,z) for x,z in arc(xc,zb+0.8,0.5,180,0,10)][0:] ,WY-0.12,1.05))
        put("ramen_glas","glas",bzbox(0,0,xc-0.25,xc+0.25,WY-0.08,WY-0.06,zb+0.12,zb+0.95))
        for b in (bzbox(0,0,xc-0.3,xc+0.3,WY-0.12,WY-0.05,zb+0.07,zb+0.12),bzbox(0,0,xc-0.3,xc-0.25,WY-0.12,WY-0.05,zb+0.07,zb+0.95),bzbox(0,0,xc+0.25,xc+0.3,WY-0.12,WY-0.05,zb+0.07,zb+0.95)):
            put("dakkapel_v","steen",b)
    # ---------------- dakkapel hoofdblok (295-400 px, tot 9.8, fronton tot 10.6) ----------------
    DZ0=T+CM; DZ1=T+9.8; DW=1.45
    put("dakkapel","stuc",bzbox(0,0,-DW,DW,-0.05,1.9,DZ0,DZ1))
    for s in (-1,1):   # pilasters met rustica
        put("dakkapel","steen",bzbox(0,0,s*DW-0.18,s*DW+0.18,-0.15,0.1,DZ0,DZ1,0.01))
        put("dakkapel","steen",bzbox(0,0,s*(DW-0.55)-0.14,s*(DW-0.55)+0.14,-0.12,0.1,DZ0+0.1,DZ1,0.01))
        put("ornament","steen",btube(spiral(s*(DW+0.32),-0.05,DZ0+0.35,0.28,1.2,18,"XZ",-s),0.05,6))   # voluut opzij
        put("ornament","steen",btube([(s*(DW+0.18),-0.05,DZ0+0.6),(s*(DW+0.55),-0.05,DZ0+0.25),(s*(DW+0.62),-0.05,DZ0)],0.06,6))
    window(TR(0,-0.05,0),0,DZ0+0.35,0.82,1.2,"gewoon",[])
    put("ramen_glas","glas",bzbox(0,0,-0.41,0.41,-0.06,-0.04,DZ0+0.35,DZ0+1.55))
    # gebogen fronton (segmentboog) + kroonlijst
    put("dakkapel","steen",bzbox(0,0,-DW-0.3,DW+0.3,-0.3,0.3,DZ1-0.12,DZ1,0.015))
    seg=[(x,z) for x,z in arc(0,DZ1-1.9,2.7,math.degrees(math.acos((DW+0.3)/2.7)),180-math.degrees(math.acos((DW+0.3)/2.7)),16)]
    put("dakkapel","steen",boutline([(DW+0.3,DZ1)]+seg[1:-1]+[(-DW-0.3,DZ1)],-0.3,0.6))
    inner=[(x*0.85,DZ1+0.06+(z-DZ1)*0.78) for x,z in seg]
    put("dakkapel","stuc",boutline([(DW*0.85+0.25,DZ1+0.06)]+inner[1:-1]+[(-DW*0.85-0.25,DZ1+0.06)],-0.33,0.05))
    # cartouche in het fronton
    cart=blathe([(0,0),(0.3,0.0),(0.32,0.03),(0.26,0.07),(0,0.08)],14); bmesh.ops.scale(cart,vec=(0.8,1.15,1),verts=cart.verts)   # ovaal schild
    put("ornament","steen",cart,TR(0,-0.3,DZ1+0.36)@Matrix.Rotation(math.radians(90),4,"X"))
    for sx in (-1,1):
        put("ornament","steen",btube(spiral(sx*0.42,-0.36,DZ1+0.25,0.14,1.3,14,"XZ",sx),0.03,5))
    # ---------------- beeld (front.jpg 320-370 px, 10.6-11.9) ----------------
    zb=DZ1+0.82
    put("beeld","wit",bbox(0.5,0.5,0.25,0,0.0,zb+0.125,0.02))
    put("beeld","wit",blathe([(0,0),(0.24,0),(0.22,0.1),(0.17,0.35),(0.13,0.55),(0.12,0.62),(0,0.64)],12),TR(0,0,zb+0.25))
    fig=skin_chain("_fig",{"romp":[(0,0,zb+0.8,0.1),(0,0,zb+1.0,0.09),(0,0,zb+1.1,0.05)],
                            "armL":[(0,0,zb+1.0,0.09),(-0.12,0,zb+1.03,0.045),(-0.28,0,zb+1.12,0.035),(-0.38,0,zb+1.3,0.03),(-0.42,0,zb+1.4,0.025)],
                            "armR":[(0,0,zb+1.0,0.09),(0.12,0,zb+1.03,0.045),(0.28,0,zb+1.12,0.035),(0.38,0,zb+1.3,0.03),(0.42,0,zb+1.4,0.025)]},"FORMS",subdiv=1)
    apply_all_modifiers(fig); fbm=bmesh.new(); fbm.from_mesh(fig.data); bmesh.ops.transform(fbm,matrix=fig.matrix_world,verts=fbm.verts)
    fd=fig.data; bpy.data.objects.remove(fig,do_unlink=True); bpy.data.meshes.remove(fd)
    put("beeld","wit",fbm)
    hb=bmesh.new(); bmesh.ops.create_uvsphere(hb,u_segments=10,v_segments=8,radius=0.085); bmesh.ops.translate(hb,vec=(0,0,zb+1.2),verts=hb.verts); put("beeld","wit",hb)
    # ---------------- hal achter (inferred, laag gehouden: niet zichtbaar in front.jpg) ----------------
    put("hal","hal",bzbox(0,0,-9.25,9.25,MD,MD+23,0,6.5))
    put("hal","hal",bzbox(0,0,-9.35,9.35,MD-0.1,MD+23.1,6.5,6.7))
    # ---------------- objecten maken ----------------
    n=0; tris=0
    for (part,mat),bm in PARTS.items():
        bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5)
        ob=new_mesh_object(f"VV_{part}__{mat}",bm,"FORMS"); assign(ob,bpy.data.materials["MAT_"+mat])
        if mat in ("wit","zink") or part in ("zuilen","ornament","vazen","dak_vazen","beeld"): shade_smooth(ob,math.radians(40))
        n+=1; tris+=sum(len(p.vertices)-2 for p in ob.data.polygons)
    tris+=sum(len(p.vertices)-2 for p in wob.data.polygons)
    # blokkering verbergen in render
    lc=bpy.context.view_layer.layer_collection.children.get("LOW")
    if lc: lc.exclude=False
    save_master(master); log("objects",n+1,"tris~",tris)
if __name__=="__main__":
    a=argv_after_dashes(); m=a[a.index("--master")+1] if "--master" in a else None
    if m: build(m)
