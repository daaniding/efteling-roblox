"""Tegelbare visgraat-klinkertextuur (Efteling-paden): kleur, normaal, ruwheid. Gerenderd uit echte geometrie (orthografisch, van boven)."""
import bpy, bmesh, math, random, sys, os
from mathutils import Vector
OUT=sys.argv[sys.argv.index("--")+1]; os.makedirs(OUT,exist_ok=True)
random.seed(4)
bpy.ops.wm.read_homefile(use_empty=True); sc=bpy.context.scene
SIZE=2048
U=0.10+0.008
TILE=3*4*math.sqrt(2)*U  # 1.833 m, exact tegelbaar
# visgraat: stenen 0.20 x 0.10 x 0.06, voeg 0.008, 45 graden
BL,BW,J=0.20,0.10,0.008
mat=bpy.data.materials.new("brick"); mat.use_nodes=True; nt=mat.node_tree
b=next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED")
oi=nt.nodes.new("ShaderNodeObjectInfo"); ramp=nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color=(0.26,0.11,0.08,1); ramp.color_ramp.elements[1].color=(0.50,0.26,0.19,1)
e=ramp.color_ramp.elements.new(0.5); e.color=(0.40,0.19,0.13,1)
noi=nt.nodes.new("ShaderNodeTexNoise"); noi.inputs["Scale"].default_value=60; noi.inputs["Detail"].default_value=6
mix=nt.nodes.new("ShaderNodeMixRGB"); mix.blend_type="MULTIPLY"; mix.inputs["Fac"].default_value=0.35
nt.links.new(oi.outputs["Random"],ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"],mix.inputs[1]); nt.links.new(noi.outputs["Color"],mix.inputs[2]); nt.links.new(mix.outputs["Color"],b.inputs["Base Color"])
bump=nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=0.3; noi2=nt.nodes.new("ShaderNodeTexNoise"); noi2.inputs["Scale"].default_value=120
nt.links.new(noi2.outputs["Fac"],bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"],b.inputs["Normal"]); b.inputs["Roughness"].default_value=0.75
mort=bpy.data.materials.new("mortar"); mort.use_nodes=True; bm_=next(n for n in mort.node_tree.nodes if n.type=="BSDF_PRINCIPLED"); bm_.inputs["Base Color"].default_value=(0.16,0.14,0.12,1); bm_.inputs["Roughness"].default_value=1.0
# voegbed
bm=bmesh.new(); bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=TILE*1.5); me=bpy.data.meshes.new("bed"); bm.to_mesh(me); bm.free(); me.materials.append(mort)
bed=bpy.data.objects.new("bed",me); sc.collection.objects.link(bed); bed.location=(0,0,-0.03)
# stenen in visgraat, over een gebied iets groter dan de tegel (periodiek: patroonperiode = (BL+BW+2J)*sqrt2 ... we kiezen tegelmaat als veelvoud)
P=(BL+J+BW+J)  # 0.316 ... periode langs diagonaal
import itertools
def brick(cx,cy,ang):
    tmp=bmesh.new(); bmesh.ops.create_cube(tmp,size=1.0)
    bmesh.ops.scale(tmp,vec=(BL-J,BW-J,0.06),verts=tmp.verts)
    bmesh.ops.bevel(tmp,geom=tmp.verts[:]+tmp.edges[:],offset=0.006,segments=2,affect="EDGES")
    # lichte scheefstand/hoogteverschil
    import mathutils
    rot=mathutils.Matrix.Rotation(ang+random.uniform(-0.01,0.01),4,"Z")@mathutils.Matrix.Rotation(random.uniform(-0.01,0.01),4,"X")
    bmesh.ops.transform(tmp,matrix=mathutils.Matrix.Translation((cx,cy,random.uniform(-0.003,0.003)))@rot,verts=tmp.verts)
    m2=bpy.data.meshes.new("b"); tmp.to_mesh(m2); tmp.free(); m2.materials.append(mat)
    o=bpy.data.objects.new("b",m2); sc.collection.objects.link(o)
    for p in m2.polygons: p.use_smooth=False
    return o
# visgraat: eenheidscellen U; horizontale steen op (x,y) als (x+y)%4==0, verticale als (x+y)%4==2; daarna 45 graden draaien
s=math.sqrt(0.5); n=0
for x in range(-22,23):
    for y in range(-22,23):
        v=(x+y)%4
        if v==0: cx,cy,ang=(x+1.0)*U,(y+0.5)*U,0.0          # horizontaal: cellen (x,y),(x+1,y)
        elif v==2: cx,cy,ang=(x+0.5)*U,(y+1.0)*U,math.pi/2 # verticaal: cellen (x,y),(x,y+1)
        else: continue
        rx=(cx-cy)*s; ry=(cx+cy)*s
        if abs(rx)<TILE*0.62 and abs(ry)<TILE*0.62:
            brick(rx,ry,ang+math.pi/4); n+=1
print("bricks",n)
cam=bpy.data.objects.new("C",bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera=cam
cam.data.type="ORTHO"; cam.data.ortho_scale=TILE; cam.location=(0,0,3)
sc.render.resolution_x=SIZE; sc.render.resolution_y=SIZE; sc.render.engine="BLENDER_EEVEE"
sc.view_settings.view_transform="Standard"; sc.render.image_settings.color_mode="RGB"
w=bpy.data.worlds.new("W"); sc.world=w; w.use_nodes=True; bg=next(nn for nn in w.node_tree.nodes if nn.type=="BACKGROUND"); bg.inputs[0].default_value=(0,0,0,1); bg.inputs[1].default_value=0.0
# drie passes via emissie-materialen die we op alle objecten zetten
def emission_variant(src, mode):
    m=src.copy(); nt=m.node_tree
    out=next(n for n in nt.nodes if n.type=="OUTPUT_MATERIAL"); bsdf=next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED")
    em=nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value=1.0
    if mode=="color":
        link=next((l for l in nt.links if l.to_node==bsdf and l.to_socket.name=="Base Color"),None)
        if link: nt.links.new(link.from_socket, em.inputs["Color"])
        else: em.inputs["Color"].default_value=bsdf.inputs["Base Color"].default_value
    elif mode=="normal":
        geo=nt.nodes.new("ShaderNodeNewGeometry"); vt=nt.nodes.new("ShaderNodeVectorMath"); vt.operation="MULTIPLY_ADD"
        vt.inputs[1].default_value=(0.5,0.5,0.5); vt.inputs[2].default_value=(0.5,0.5,0.5)
        # bump meenemen: gebruik de normal-input van de bsdf als die gekoppeld is
        nt.links.new(geo.outputs["Normal"], vt.inputs[0]); nt.links.new(vt.outputs[0], em.inputs["Color"])
    else:
        r=bsdf.inputs["Roughness"].default_value; em.inputs["Color"].default_value=(r,r,r,1)
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"]); return m
originals={}
for o in sc.objects:
    if o.type=="MESH" and o.data.materials: originals[o.name]=o.data.materials[0]
for mode,name in (("color","klinkers_color"),("normal","klinkers_normal"),("rough","klinkers_rough")):
    cache={}
    for o in sc.objects:
        if o.name in originals:
            src=originals[o.name]
            if src.name not in cache: cache[src.name]=emission_variant(src,mode)
            o.data.materials[0]=cache[src.name]
    try: sc.view_settings.view_transform="Standard" if mode=="color" else "Raw"
    except TypeError: sc.view_settings.view_transform="Standard"
    sc.render.filepath=os.path.join(OUT,name+".png"); bpy.ops.render.render(write_still=True)
# beauty ter controle
for o in sc.objects:
    if o.name in originals: o.data.materials[0]=originals[o.name]
bg.inputs[0].default_value=(1,1,1,1); bg.inputs[1].default_value=1.0
sun=bpy.data.objects.new("S",bpy.data.lights.new("S","SUN")); sc.collection.objects.link(sun); sun.rotation_euler=(math.radians(45),0,math.radians(30)); sun.data.energy=2
sc.view_settings.view_transform="Standard"; sc.render.filepath=os.path.join(OUT,"klinkers_beauty.png"); bpy.ops.render.render(write_still=True)
print("DONE", sorted(os.listdir(OUT)))
