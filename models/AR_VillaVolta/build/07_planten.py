"""07_planten: kleine beplanting (grasbossen, siergras, varens, bloemen, lavendel, bodembedekkers) als losse prototypen.
Elk prototype = objecten 'PL_<naam>__<mat>' met oorsprong op de grond (0,0,0), meters, Z op.
Export: elk object apart (geen samenvoegen per materiaal), zodat Studio ze per prototype kan groeperen en verspreiden.
Gebruik: blender --background --python 07_planten.py -- --out <fbx>"""
import bpy, bmesh, sys, math, random
from mathutils import Vector, Matrix
args=sys.argv[sys.argv.index("--")+1:]; OUT=args[args.index("--out")+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
rnd=random.Random(7)
MATS={"blad":(0.16,0.32,0.10),"blad_donker":(0.09,0.20,0.07),"blad_licht":(0.30,0.46,0.16),"gras_droog":(0.52,0.50,0.30),
      "varen":(0.14,0.34,0.09),"bloem_rood":(0.72,0.07,0.08),"bloem_geel":(0.92,0.74,0.10),"bloem_paars":(0.42,0.20,0.62),
      "bloem_wit":(0.92,0.90,0.84),"bloem_roze":(0.90,0.45,0.62),"lavendel":(0.50,0.42,0.78),"hart":(0.85,0.62,0.10)}
def mat(n):
    m=bpy.data.materials.get("MAT_"+n) or bpy.data.materials.new("MAT_"+n); m.diffuse_color=(*MATS[n],1); return m
BMS={}
def bm_for(proto,m):
    k=(proto,m)
    if k not in BMS: BMS[k]=bmesh.new()
    return BMS[k]
def blade(bm,base,h,w,ang,lean,curl=0.35,seg=4):
    """getaperde, doorbuigende grasspriet/blad als strook"""
    d=Vector((math.cos(ang),math.sin(ang),0)); side=Vector((-d.y,d.x,0))
    prev=None
    for i in range(seg+1):
        t=i/seg; z=h*t*(1-0.25*curl*t); off=d*(lean*h*t+curl*h*t*t)
        c=Vector(base)+off+Vector((0,0,z)); ww=w*(1-t)
        if i<seg: pair=(bm.verts.new(c-side*ww/2),bm.verts.new(c+side*ww/2))
        else: pair=(bm.verts.new(c),)
        if prev:
            if len(pair)==2: bm.faces.new((prev[0],prev[1],pair[1],pair[0]))
            else: bm.faces.new((prev[0],prev[1],pair[0]))
        prev=pair
def disc(bm,c,r,n=6,tilt=0.0):
    vs=[bm.verts.new(Vector(c)+Vector((r*math.cos(k*math.tau/n),r*math.sin(k*math.tau/n),tilt*math.sin(k*math.tau/n)))) for k in range(n)]
    bm.faces.new(vs)
def blob(bm,c,r,sz=0.7):
    t=bmesh.new(); bmesh.ops.create_icosphere(t,subdivisions=1,radius=r); bmesh.ops.scale(t,vec=(1,1,sz),verts=t.verts)
    bmesh.ops.translate(t,vec=c,verts=t.verts)
    me=bpy.data.meshes.new("_t"); t.to_mesh(me); t.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
# ---- grasbossen ----
for v,(h,n,m) in enumerate(((0.32,18,"blad"),(0.45,22,"blad_licht"),(0.25,14,"blad_donker"))):
    bm=bm_for(f"gras{v}",m)
    for i in range(n):
        r=rnd.uniform(0,0.07); a=rnd.uniform(0,math.tau)
        blade(bm,(r*math.cos(a),r*math.sin(a),0),h*rnd.uniform(0.7,1.15),rnd.uniform(0.012,0.02),a,rnd.uniform(0.1,0.35))
# ---- siergras (pluimen) ----
for v,(h,m) in enumerate(((0.75,"gras_droog"),(0.6,"blad_licht"))):
    bm=bm_for(f"siergras{v}",m)
    for i in range(30):
        r=rnd.uniform(0,0.1); a=rnd.uniform(0,math.tau)
        blade(bm,(r*math.cos(a),r*math.sin(a),0),h*rnd.uniform(0.75,1.1),0.016,a,rnd.uniform(0.15,0.4),0.5)
    bp=bm_for(f"siergras{v}","gras_droog")
    for i in range(7):
        a=rnd.uniform(0,math.tau); x,y=0.12*math.cos(a),0.12*math.sin(a)
        blade(bp,(x*0.3,y*0.3,0.2),h*0.85,0.03,a,0.25,0.2,3)
# ---- varens ----
for v,(L,n) in enumerate(((0.55,7),(0.4,6))):
    bm=bm_for(f"varen{v}","varen")
    for i in range(n):
        a=i*math.tau/n+rnd.uniform(-0.2,0.2); d=Vector((math.cos(a),math.sin(a),0)); side=Vector((-d.y,d.x,0))
        pts=[d*L*t*0.85+Vector((0,0,L*0.55*math.sin(math.pi*t*0.8))) for t in [k/6 for k in range(7)]]
        for k in range(6):   # nerf + blaadjes
            p,q=pts[k],pts[k+1]; w=0.06*(1-k/6)+0.01
            for s in (-1,1):
                bm.faces.new((bm.verts.new(p),bm.verts.new(q),bm.verts.new((p+q)/2+side*s*w*1.6-Vector((0,0,0.02)))))
# ---- bloemen: blad onderin + stelen met bloemhoofdjes ----
for kleur in ("bloem_rood","bloem_geel","bloem_paars","bloem_wit","bloem_roze"):
    bl=bm_for(kleur,"blad"); bf=bm_for(kleur,kleur); bh=bm_for(kleur,"hart")
    for i in range(10):
        a=rnd.uniform(0,math.tau); blade(bl,(0.04*math.cos(a),0.04*math.sin(a),0),0.16,0.03,a,0.45,0.4,3)
    for i in range(rnd.randint(6,9)):
        a=rnd.uniform(0,math.tau); r=rnd.uniform(0.02,0.12); h=rnd.uniform(0.28,0.45)
        top=Vector((r*math.cos(a)+0.03*math.cos(a),r*math.sin(a)+0.03*math.sin(a),h))
        blade(bl,(r*0.5*math.cos(a),r*0.5*math.sin(a),0),h,0.008,a,0.08,0.1,3)
        for k in range(5):   # bloemblaadjes
            pa=k*math.tau/5; c=top+Vector((0.025*math.cos(pa),0.025*math.sin(pa),0))
            disc(bf,c,0.022,5,0.01)
        disc(bh,top+Vector((0,0,0.004)),0.012,5)
# ---- lavendel ----
bm=bm_for("lavendel","blad_licht"); bf=bm_for("lavendel","lavendel")
for i in range(26):
    a=rnd.uniform(0,math.tau); r=rnd.uniform(0,0.16); h=rnd.uniform(0.35,0.5)
    blade(bm,(r*0.4*math.cos(a),r*0.4*math.sin(a),0),h,0.01,a,r*1.2,0.1,3)
    top=Vector((r*0.4*math.cos(a),r*0.4*math.sin(a),0))+Vector((math.cos(a),math.sin(a),0))*(r*1.2*h)+Vector((0,0,h))
    blob(bf,top+Vector((0,0,0.04)),0.025,2.4)
# ---- bodembedekkers (lage kussens) ----
for v,m in enumerate(("blad_donker","blad")):
    bm=bm_for(f"bodem{v}",m)
    for i in range(9):
        a=rnd.uniform(0,math.tau); r=rnd.uniform(0,0.22)
        blob(bm,(r*math.cos(a),r*math.sin(a),0.05),rnd.uniform(0.07,0.11),0.6)
# ---- objecten + export (elk apart) ----
col=bpy.context.scene.collection
for (proto,m),bm in BMS.items():
    me=bpy.data.meshes.new(f"PL_{proto}__{m}"); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    me.materials.append(mat(m)); ob=bpy.data.objects.new(f"PL_{proto}__{m}",me); col.objects.link(ob)
tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in col.objects)
for o in col.objects: o.select_set(True)
bpy.ops.export_scene.fbx(filepath=OUT,use_selection=True,global_scale=1.0,apply_scale_options='FBX_SCALE_ALL',apply_unit_scale=True,
                         axis_forward='-Z',axis_up='Y',object_types={'MESH'},mesh_smooth_type='FACE',add_leaf_bones=False)
print("PLANTEN",len(col.objects),"objecten",tris,"tris; protos",sorted({k[0] for k in BMS}))
