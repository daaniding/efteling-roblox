"""10_haagtextuur: naadloze textuur van een geschoren haag, gerenderd uit echte bladtakjes (Poly Haven shrub_02, CC0).
Strooit takjes dicht in lagen op een tegel van TILE x TILE m (met kopieen over de randen voor naadloosheid), rendert
van bovenaf (orthografisch): kleur (met zachte hemelbelichting = diepte) en normalen -> tangent-space normal map.
Gebruik: blender --background --python 10_haagtextuur.py -- --src <polyhaven_dl> --out <map>"""
import bpy, glob, os, sys, math, random
from mathutils import Vector, Matrix, Euler
a=sys.argv[sys.argv.index("--")+1:]; SRC=a[a.index("--src")+1]; OUT=a[a.index("--out")+1]; os.makedirs(OUT,exist_ok=True)
TILE=2.0; RES=1024; N=650; rnd=random.Random(3)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
bpy.ops.import_scene.gltf(filepath=glob.glob(os.path.join(SRC,"shrub_02","*.gltf"))[0])
bron=[o for o in bpy.data.objects if o.type=="MESH"]
for o in bron:
    mw=o.matrix_world.copy(); o.parent=None; o.matrix_world=mw
    o.data=o.data.copy(); o.data.transform(o.matrix_world); o.matrix_world.identity()
    vs=[v.co for v in o.data.vertices]; c=Vector((sum(v.x for v in vs)/len(vs),sum(v.y for v in vs)/len(vs),min(v.z for v in vs)))
    o.data.transform(Matrix.Translation(-c)); h=max(v.co.z for v in o.data.vertices)
    o.data.transform(Matrix.Scale(0.45/h,4))     # takje ~45 cm: blaadjes ~3-5 cm, zoals beuk/buxus van dichtbij
    o.hide_render=True; o.location=(0,0,-50)
# donkere binnenkant onder de bladeren
bpy.ops.mesh.primitive_plane_add(size=TILE*3,location=(0,0,-0.05))
grond=bpy.context.active_object; gm=bpy.data.materials.new("binnen"); gm.diffuse_color=(0.02,0.05,0.015,1)
gm.use_nodes=True; next(n for n in gm.node_tree.nodes if n.type=="BSDF_PRINCIPLED").inputs["Base Color"].default_value=(0.02,0.05,0.015,1)
grond.data.materials.append(gm)
col=bpy.data.collections.new("takjes"); sc.collection.children.link(col)
def plaats(src,x,y,z,rot,s):
    for dx in (-TILE,0,TILE):
        for dy in (-TILE,0,TILE):
            if abs(x+dx)>TILE*0.5+0.35 or abs(y+dy)>TILE*0.5+0.35: continue
            o=bpy.data.objects.new("t",src.data); col.objects.link(o)
            o.location=(x+dx,y+dy,z); o.rotation_euler=rot; o.scale=(s,s,s)
for i in range(N):
    src=rnd.choice(bron); x=rnd.uniform(-TILE/2,TILE/2); y=rnd.uniform(-TILE/2,TILE/2)
    z=rnd.uniform(-0.25,0.0)                                   # lagen: buitenste blaadjes vormen het oppervlak
    rot=Euler((rnd.uniform(0.6,1.4)*rnd.choice((1,-1)),rnd.uniform(-0.6,0.6),rnd.uniform(0,math.tau)))
    plaats(src,x,y,z,rot,rnd.uniform(0.7,1.3))
# camera + licht
cam=bpy.data.objects.new("cam",bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera=cam
cam.data.type="ORTHO"; cam.data.ortho_scale=TILE; cam.location=(0,0,3); cam.rotation_euler=(0,0,0)
cam.data.clip_end=10
w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True
bg=next(n for n in w.node_tree.nodes if n.type=="BACKGROUND"); bg.inputs[0].default_value=(1,1,1,1); bg.inputs[1].default_value=1.0
sun=bpy.data.objects.new("zon",bpy.data.lights.new("zon","SUN")); sun.data.energy=1.2; sun.rotation_euler=(math.radians(25),0,math.radians(30)); sc.collection.objects.link(sun)
sc.render.engine="CYCLES"; sc.cycles.samples=48; sc.cycles.use_denoising=True
try: sc.cycles.device="CPU"
except Exception: pass
sc.render.resolution_x=RES; sc.render.resolution_y=RES; sc.render.film_transparent=False
sc.view_settings.view_transform="Standard"
sc.render.filepath=os.path.join(OUT,"haag_kleur.png"); sc.render.image_settings.file_format="PNG"
bpy.ops.render.render(write_still=True)
# reliefkaart: tweede render met een materiaal dat de normaal (in camera-/tangentruimte, camera kijkt recht omlaag) als kleur uitstraalt
nm=bpy.data.materials.new("normaal"); nm.use_nodes=True; t=nm.node_tree
for n in list(t.nodes): t.nodes.remove(n)
geo=t.nodes.new("ShaderNodeNewGeometry"); vm=t.nodes.new("ShaderNodeVectorMath"); vm.operation="MULTIPLY_ADD"
vm.inputs[1].default_value=(0.5,0.5,0.5); vm.inputs[2].default_value=(0.5,0.5,0.5)
em=t.nodes.new("ShaderNodeEmission"); outn=t.nodes.new("ShaderNodeOutputMaterial")
t.links.new(geo.outputs["Normal"],vm.inputs[0]); t.links.new(vm.outputs[0],em.inputs["Color"]); t.links.new(em.outputs[0],outn.inputs["Surface"])
sc.view_layers[0].material_override=nm
bg.inputs[1].default_value=0.0; sun.hide_render=True
sc.cycles.samples=16; sc.render.filepath=os.path.join(OUT,"haag_normaal.png")
bpy.ops.render.render(write_still=True)
print("HAAG klaar", len(col.objects), "takjes")
