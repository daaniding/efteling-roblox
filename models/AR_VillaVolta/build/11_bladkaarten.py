"""11_bladkaarten: echte bladtrossen van bovenaf op transparante achtergrond (512x512) als vervanging van de getekende
bladkaart-texturen van de bomenset. Groot blad = 9 brandneteltakken (Poly Haven nettle_plant, CC0) radiaal schuin uitgelegd;
klein blad = gekruiste takken van shrub_02. Gebruik: blender -b -P 11_bladkaarten.py -- --src <polyhaven_dl> --out <map>"""
import bpy, glob, os, sys, math, random
from mathutils import Vector, Matrix, Euler
a=sys.argv[sys.argv.index("--")+1:]; SRC=a[a.index("--src")+1]; OUT=a[a.index("--out")+1]; os.makedirs(OUT,exist_ok=True)
rnd=random.Random(9)
def laad(pid):
    bpy.ops.import_scene.gltf(filepath=glob.glob(os.path.join(SRC,pid,"*.gltf"))[0])
    obs=[o for o in bpy.data.objects if o.type=="MESH" and o.get("_g") is None]
    for o in obs:
        mw=o.matrix_world.copy(); o.parent=None; o.matrix_world=mw; o.data=o.data.copy(); o.data.transform(o.matrix_world); o.matrix_world.identity()
        vs=[v.co for v in o.data.vertices]; c=Vector((sum(v.x for v in vs)/len(vs),sum(v.y for v in vs)/len(vs),min(v.z for v in vs)))
        o.data.transform(Matrix.Translation(-c)); o["_g"]=1; o.hide_render=True
    return obs
def render(naam,span):
    sc=bpy.context.scene
    cam=bpy.data.objects.new("c",bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera=cam
    cam.data.type="ORTHO"; cam.data.ortho_scale=span; cam.location=(0,0,6); cam.rotation_euler=(0,0,0)
    w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True
    bg=next(n for n in w.node_tree.nodes if n.type=="BACKGROUND"); bg.inputs[0].default_value=(1,1,1,1); bg.inputs[1].default_value=0.9
    sun=bpy.data.objects.new("zon",bpy.data.lights.new("zon","SUN")); sun.data.energy=2.2; sun.rotation_euler=(math.radians(30),0,math.radians(40)); sc.collection.objects.link(sun)
    sc.render.engine="CYCLES"; sc.cycles.samples=48; sc.render.film_transparent=True
    sc.render.resolution_x=sc.render.resolution_y=512; sc.view_settings.view_transform="Standard"
    sc.render.image_settings.file_format="PNG"; sc.render.image_settings.color_mode="RGBA"
    sc.render.filepath=os.path.join(OUT,naam+".png"); bpy.ops.render.render(write_still=True); print("BLAD",naam)
# groot blad
bpy.ops.wm.read_factory_settings(use_empty=True)
src=laad("nettle_plant")
for k in range(9):
    s=rnd.choice(src); o=bpy.data.objects.new("t",s.data); bpy.context.scene.collection.objects.link(o)
    ang=k*math.tau/9+rnd.uniform(-0.2,0.2); tilt=math.radians(rnd.uniform(55,75))
    o.rotation_euler=Euler((0,tilt,ang),"XYZ"); o.scale=(1,1,1)
    o.location=(0,0,rnd.uniform(-0.02,0.02))
render("tros_groot",0.4)
# klein blad
bpy.ops.wm.read_factory_settings(use_empty=True)
src=laad("shrub_02")
for k in range(3):
    s=src[k%len(src)]; o=bpy.data.objects.new("t",s.data); bpy.context.scene.collection.objects.link(o)
    o.rotation_euler=Euler((0,0,k*2.1),"XYZ"); o.location=(0,0,-1.2)
render("tros_klein",1.6)
