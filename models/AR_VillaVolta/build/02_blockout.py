"""02_blockout Villa Volta: meters, Z op, voorgevel op y=0 naar -Y, grond z=0 = terrasvloer? Nee: z=0 = maaiveld; terras 0.75 hoog."""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix
PHASE="02_blockout"; OWNER_TAG="phase:"+PHASE
TEMPLATE=os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src=open(TEMPLATE).read().split("# ARGS AND FILE HANDLING",1)[1]
_ns={"bpy":bpy,"bmesh":bmesh,"sys":sys,"os":os,"math":math,"Vector":Vector,"Matrix":Matrix,"PHASE":PHASE,"OWNER_TAG":OWNER_TAG}
exec(_src,_ns); globals().update({k:v for k,v in _ns.items() if callable(v)})
T=0.8           # terrashoogte, 4 treden van ~0.2 (front.jpg)
MW,MD=8.0,10.0  # hoofdblok: 8.0 breed (front.jpg 205-500 px @37px/m), diepte inferred
WW,WD=2.6,6.0   # zijvleugel: 2.6 breed (front.jpg 115-205 px), diepte inferred
def build(master):
    open_master(master); clear_owned(); L="LOW"
    CM,CW=7.8,6.9   # kroonlijst hoofdblok / vleugel boven terrasvloer (front.jpg y220 / y250)
    # terras 17 breed + 4 treden die naar onder breder worden (front.jpg)
    box("BLK_terras",(17.0,5.0,T),L,(0,-2.5,0),base_at_origin=True)
    for i in range(4):
        box(f"BLK_trede_{i}",(9.5+2.4*(3-i),0.35,T*(i+1)/4),L,(0,-5.0-0.35*(3-i)-0.175,0),base_at_origin=True)
    box("BLK_hoofdblok",(MW,MD,CM),L,(0,MD/2,T),base_at_origin=True)
    for s in (-1,1):
        box("BLK_vleugel%+d"%s,(WW,WD,CW),L,(s*(MW/2+WW/2),WD/2+0.4,T),base_at_origin=True)
        box("BLK_rustica%+d"%s,(0.6,0.2,CM),L,(s*(MW/2-0.3),-0.1,T),base_at_origin=True)
        box("BLK_rustica_v%+d"%s,(0.5,0.2,CW),L,(s*(MW/2+WW-0.25),0.3,T),base_at_origin=True)
    # hal erachter: niet zichtbaar boven de vleugels in front.jpg -> laag en ver weg (inferred)
    box("BLK_hal",(18.5,23.0,6.5),L,(0,MD+11.5,0),base_at_origin=True)
    def mansard(name,w,d,y0,z0,z1,z2,inset1,inset2):
        bm=bmesh.new()
        def ring(wx,dy,z,o): return [bm.verts.new(p) for p in ((-wx,y0-o,z),(wx,y0-o,z),(wx,y0+dy+o,z),(-wx,y0+dy+o,z))]
        r0=ring(w/2+0.3,d,z0,0.3); r1=ring(w/2-inset1,d,z1,0.3-inset1); r2=ring(w/2-inset2,d,z2,0.3-inset2)
        for a,b in ((r0,r1),(r1,r2)):
            for i in range(4): bm.faces.new((a[i],a[(i+1)%4],b[(i+1)%4],b[i]))
        bm.faces.new(r2); bm.faces.new(list(reversed(r0)))
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces); return new_mesh_object(name,bm,L)
    # mansarde hoofdblok: steil 7.9->9.6, flauw tot 9.9 (front.jpg y210/y150/y140)
    mansard("BLK_dak_hoofd",MW,MD,0,T+CM,T+9.7,T+9.9,1.6,2.0)
    for s in (-1,1):
        o=mansard("BLK_dak_vleugel%+d"%s,WW,WD,0.4,T+CW,T+8.1,T+8.4,0.5,0.9); o.location.x=s*(MW/2+WW/2)
        box("BLK_dakraam_v%+d"%s,(0.8,0.6,1.0),L,(s*(MW/2+WW/2),0.0,T+CW+0.3),base_at_origin=True)
    # dakkapel 2.9 breed tot 9.8, fronton tot 10.6, beeld 1.3 hoog tot 11.9 (front.jpg)
    box("BLK_dakkapel",(2.9,1.4,2.0),L,(0,0.3,T+CM),base_at_origin=True)
    box("BLK_fronton",(3.3,0.5,0.8),L,(0,-0.3,T+9.8),base_at_origin=True)
    cylinder("BLK_beeld",0.35,1.3,L,segments=12,location=(0,-0.1,T+10.6+0.65))
    # zuilen hart-op-hart 7.3, d 0.4, tot balkon 4.4; balkon 7.6 breed 4.4-4.8, balustrade tot 5.9
    for s in (-1,1):
        cylinder("BLK_zuil%+d"%s,0.2,4.4,L,segments=16,location=(s*3.65,-1.4,T+2.2))
    box("BLK_balkon",(7.6,1.8,0.4),L,(0,-0.9,T+4.4),base_at_origin=True)
    box("BLK_balustrade",(7.6,0.25,1.1),L,(0,-1.65,T+4.8),base_at_origin=True)
    box("BLK_balkondeur",(1.6,0.1,1.6),L,(0,-0.05,T+4.8),base_at_origin=True)
    box("BLK_opschrift",(3.4,0.15,0.4),L,(0,-0.08,T+6.5),base_at_origin=True)
    box("BLK_kroonlijst",(MW+0.6,0.6,0.4),L,(0,-0.1,T+CM-0.4),base_at_origin=True)
    # deur 2.4 x 3.05, omlijsting 3.3 breed tot 3.8 (front.jpg)
    box("BLK_deur",(2.4,0.1,3.05),L,(0,-0.05,T),base_at_origin=True)
    box("BLK_deur_ornament",(3.3,0.15,0.75),L,(0,-0.08,T+3.05),base_at_origin=True)
    for s in (-1,1):
        x=s*(MW/2+WW/2)
        box("BLK_raam_bg%+d"%s,(0.6,0.1,1.0),L,(x,0.35,T+1.1),base_at_origin=True)
        box("BLK_raam_1e%+d"%s,(0.6,0.1,1.0),L,(x,0.35,T+4.7),base_at_origin=True)
        # terrasbalustrade 2.6 lang, 0.8 hoog, vazen 1.0 erop
        box("BLK_terrasbal%+d"%s,(2.6,0.3,0.8),L,(s*(MW/2+WW+1.3),-0.5,T),base_at_origin=True)
        for k in range(3):
            cylinder("BLK_vaas%+d_%d"%(s,k),0.25,1.0,L,segments=10,location=(s*(MW/2+WW+0.2+k*1.1),-0.5,T+0.8+0.5))
    save_master(master); log("built",len([o for o in bpy.data.objects if o.get("owner")==OWNER_TAG]))
if __name__=="__main__":
    a=argv_after_dashes(); m=a[a.index("--master")+1] if "--master" in a else None
    if m: build(m)
