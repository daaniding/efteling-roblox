"""Drie low-poly bomen (loofboom rond, eik breed, den) voor Roblox: stam + kroon als aparte materialen. 1 unit = 1 m."""
import bpy, bmesh, math, random, sys, os
random.seed(2)
bpy.ops.wm.read_homefile(use_empty=True)
sc=bpy.context.scene
def mat(n,rgb):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=next(x for x in m.node_tree.nodes if x.type=="BSDF_PRINCIPLED"); b.inputs["Base Color"].default_value=(*rgb,1); b.inputs["Roughness"].default_value=0.9; return m
M_trunk=mat("MAT_trunk",(0.30,0.20,0.12)); M_leaf=mat("MAT_leaf",(0.22,0.42,0.16)); M_pine=mat("MAT_pine",(0.12,0.30,0.16))
def obj(name,bm,m):
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces); me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o=bpy.data.objects.new(name,me); sc.collection.objects.link(o); me.materials.append(m)
    for p in me.polygons: p.use_smooth=True
    return o
def blob(bm,c,r,segs=10,rings=6,scale=(1,1,1),noise=0.12):
    tmp=bmesh.new(); bmesh.ops.create_uvsphere(tmp,u_segments=segs,v_segments=rings,radius=r)
    for v in tmp.verts:
        v.co.x*=scale[0]; v.co.y*=scale[1]; v.co.z*=scale[2]; v.co*= (1+random.uniform(-noise,noise))
        v.co+=c
    me=bpy.data.meshes.new("t"); tmp.to_mesh(me); tmp.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
def trunk(bm,h,r0,r1,lean=(0,0)):
    tmp=bmesh.new(); rings=[]
    for k in range(5):
        t=k/4; z=h*t; rr=r0*(1-t)+r1*t; cx=lean[0]*t*t; cy=lean[1]*t*t
        rings.append([tmp.verts.new((cx+rr*math.cos(a),cy+rr*math.sin(a),z)) for a in [i*2*math.pi/8 for i in range(8)]])
    for a,b in zip(rings,rings[1:]):
        for i in range(8): tmp.faces.new((a[i],a[(i+1)%8],b[(i+1)%8],b[i]))
    tmp.faces.new(list(reversed(rings[0])))
    me=bpy.data.meshes.new("t"); tmp.to_mesh(me); tmp.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
from mathutils import Vector
# 0: ronde loofboom 9 m
bm=bmesh.new(); trunk(bm,4.2,0.28,0.18,(0.2,0.1)); obj("tree0__MAT_trunk",bm,M_trunk)
bm=bmesh.new()
for c,r in [((0.2,0.1,5.6),2.4),((-1.2,0.6,5.0),1.7),((1.4,-0.8,5.2),1.6),((0.3,1.3,6.6),1.5),((0.0,-1.0,6.9),1.6)]: blob(bm,Vector(c),r)
obj("tree0__MAT_leaf",bm,M_leaf)
# 1: brede eik 13 m
bm=bmesh.new(); trunk(bm,5.0,0.45,0.3,(0.3,-0.2))
for ang in (0.5,2.5,4.4):
    tmp=bmesh.new(); 
    pts=[Vector((0.3*t*t,-0.2*t*t,5.0*t)) for t in (1,)]
    tmp.free()
obj("tree1__MAT_trunk",bm,M_trunk)
bm=bmesh.new()
for c,r in [((0.3,-0.2,8.0),3.4),((-2.6,0.8,7.2),2.3),((2.8,1.0,7.0),2.2),((0.5,-2.6,7.4),2.1),((0.0,0.0,10.0),2.3),((-1.5,-1.5,9.2),1.9),((1.8,2.0,9.0),1.9)]: blob(bm,Vector(c),r,noise=0.15)
obj("tree1__MAT_leaf",bm,M_leaf)
# 2: den 14 m
bm=bmesh.new(); trunk(bm,9.0,0.3,0.12,(0.1,0.0)); obj("tree2__MAT_trunk",bm,M_trunk)
bm=bmesh.new()
for k,(z,r) in enumerate([(6.0,2.6),(7.6,2.2),(9.0,1.8),(10.3,1.4),(11.5,1.0),(12.6,0.6)]):
    tmp=bmesh.new(); bmesh.ops.create_cone(tmp,cap_ends=True,segments=9,radius1=r,radius2=0.05,depth=2.6)
    for v in tmp.verts: v.co.z+=z+1.3; v.co.x*=1+random.uniform(-0.1,0.1); v.co.y*=1+random.uniform(-0.1,0.1)
    me=bpy.data.meshes.new("t"); tmp.to_mesh(me); tmp.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
obj("tree2__MAT_pine",bm,M_pine)
for o in sc.objects: o.select_set(True)
out=sys.argv[sys.argv.index("--")+1]
bpy.ops.export_scene.fbx(filepath=out,use_selection=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH'},mesh_smooth_type='FACE',add_leaf_bones=False)
print("TREES", sum(len(o.data.polygons) for o in sc.objects), "faces", os.path.getsize(out))
