"""02_blockout Villa Volta: meters, Z op, voorgevel op y=0 naar -Y, grond z=0 = terrasvloer? Nee: z=0 = maaiveld; terras 0.75 hoog."""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix
PHASE="02_blockout"; OWNER_TAG="phase:"+PHASE
TEMPLATE=os.path.expanduser("~/.claude/skills/blender-image-to-3d/assets/build_template.py")
_src=open(TEMPLATE).read().split("# ARGS AND FILE HANDLING",1)[1]
_ns={"bpy":bpy,"bmesh":bmesh,"sys":sys,"os":os,"math":math,"Vector":Vector,"Matrix":Matrix,"PHASE":PHASE,"OWNER_TAG":OWNER_TAG}
exec(_src,_ns); globals().update({k:v for k,v in _ns.items() if callable(v)})
T=0.75          # terrashoogte; gevelmaten zijn t.o.v. terrasvloer
MW,MD=8.4,10.0  # hoofdblok
WW,WD=3.1,6.0   # zijvleugel
def build(master):
    open_master(master); clear_owned(); L="LOW"
    # terras + 4 treden (voorkant -Y)
    box("BLK_terras",(15.0,5.0,T),L,(0,-2.5,0),base_at_origin=True)
    for i in range(4):
        box(f"BLK_trede_{i}",(9.0,0.35,T*(i+1)/4),L,(0,-5.0-0.35*(3-i)-0.175,0),base_at_origin=True)
    # hoofdblok tot kroonlijst 7.2, zijvleugels 6.2
    box("BLK_hoofdblok",(MW,MD,7.2),L,(0,MD/2,T),base_at_origin=True)
    for s in (-1,1):
        box("BLK_vleugel%+d"%s,(WW,WD,6.2),L,(s*(MW/2+WW/2),WD/2,T),base_at_origin=True)
    # hal erachter
    box("BLK_hal",(18.5,23.0,8.0),L,(0,MD+11.5,0),base_at_origin=True)
    # mansardedak hoofdblok: onderste steile deel 70 graden tot 9.0, bovendeel tot nok 10.0
    def mansard(name,w,d,y0,z0,z1,z2,inset1,inset2):
        bm=bmesh.new()
        def ring(wx,dy,z): return [bm.verts.new(p) for p in ((-wx,y0-0.3,z),(wx,y0-0.3,z),(wx,y0+dy+0.3,z),(-wx,y0+dy+0.3,z))]
        r0=ring(w/2+0.3,d,z0); r1=ring(w/2-inset1,d-0.0,z1); r2=ring(w/2-inset2,d,z2)
        for a,b in ((r0,r1),(r1,r2)):
            for i in range(4): bm.faces.new((a[i],a[(i+1)%4],b[(i+1)%4],b[i]))
        bm.faces.new(r2); bm.faces.new(list(reversed(r0)))
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces); return new_mesh_object(name,bm,L)
    mansard("BLK_dak_hoofd",MW,MD,0,T+7.2,T+9.0,T+10.0,1.0,3.6)
    for s in (-1,1):
        o=mansard("BLK_dak_vleugel%+d"%s,WW,WD,0,T+6.2,T+7.6,T+8.2,0.6,1.3); o.location.x=s*(MW/2+WW/2)
    # dakkapel + fronton + beeld
    box("BLK_dakkapel",(4.0,1.6,2.4),L,(0,0.5,T+7.2),base_at_origin=True)
    box("BLK_fronton",(4.4,0.4,0.8),L,(0,-0.1,T+9.6),base_at_origin=True)
    cylinder("BLK_beeld",0.45,1.9,L,segments=12,location=(0,0.3,T+10.4+0.95))
    # middenrisaliet: zuilen, balkon, balustrade, opschriftband
    for s in (-1,1):
        cylinder("BLK_zuil%+d"%s,0.25,4.0,L,segments=16,location=(s*3.3,-1.3,T+2.0))
    box("BLK_balkon",(7.2,1.6,0.35),L,(0,-0.8,T+4.3))
    box("BLK_balustrade",(7.2,0.25,1.0),L,(0,-1.5,T+4.5),base_at_origin=True)
    box("BLK_opschrift",(4.3,0.1,0.6),L,(0,-0.05,T+5.2),base_at_origin=True)
    # deur + ornament
    box("BLK_deur",(2.4,0.1,3.0),L,(0,-0.05,T),base_at_origin=True)
    box("BLK_deur_ornament",(3.2,0.15,0.8),L,(0,-0.08,T+3.0),base_at_origin=True)
    # ramen (zijvleugels + eerste verdieping hoofdblok naast risaliet)
    for s in (-1,1):
        x=s*(MW/2+WW/2)
        box("BLK_raam_bg%+d"%s,(0.9,0.1,1.0),L,(x,-0.05,T+1.6),base_at_origin=True)
        box("BLK_raam_1e%+d"%s,(0.9,0.1,1.4),L,(x,-0.05,T+4.6),base_at_origin=True)
        box("BLK_raam_dak%+d"%s,(0.8,0.1,1.0),L,(x,0.3,T+6.5),base_at_origin=True)
    # balustrade terras met vazen
    for s in (-1,1):
        box("BLK_terrasbal%+d"%s,(2.6,0.3,0.9),L,(s*6.0,-4.8,T),base_at_origin=True)
        for k in range(3):
            cylinder("BLK_vaas%+d_%d"%(s,k),0.3,0.9,L,segments=10,location=(s*(4.9+k*1.1),-4.8,T+0.9+0.45))
    save_master(master); log("built",len([o for o in bpy.data.objects if o.get("owner")==OWNER_TAG]))
if __name__=="__main__":
    a=argv_after_dashes(); m=a[a.index("--master")+1] if "--master" in a else None
    if m: build(m)
