"""08_polyhaven_planten: Poly Haven-plantscans (CC0) -> lichte Roblox-prototypes.
Elk bronbestand bevat meerdere varianten naast elkaar; elk object wordt een eigen prototype 'PH_<id>_<k>' met oorsprong
in het midden van de voet, gedecimeerd tot een doel-aantal driehoeken. Schrijft per model een FBX en kopieert de texturen
(diff, nor_gl, ruwheid uit arm.G) naar textures/polyhaven/<id>/.
Gebruik: blender --background --python 08_polyhaven_planten.py -- --src <polyhaven_dl> --out <exports/polyhaven> --tex <textures/polyhaven>"""
import bpy, bmesh, sys, os, glob, json, math
from mathutils import Vector
a=sys.argv[sys.argv.index("--")+1:]
SRC=a[a.index("--src")+1]; OUT=a[a.index("--out")+1]; TEX=a[a.index("--tex")+1]
os.makedirs(OUT,exist_ok=True); os.makedirs(TEX,exist_ok=True)
DOEL={"shrub_02":6000,"shrub_03":2000,"shrub_04":8000,"fern_02":1600,"periwinkle_plant":2500,"nettle_plant":2500,
      "weed_plant_02":2200,"dandelion_01":2500,"shrub_sorrel_01":400,"flower_gazania":1800,"flower_ursinia":2500,"grass_bermuda_01":100}
info={}
for pid,doel in DOEL.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glob.glob(os.path.join(SRC,pid,"*.gltf"))[0])
    obs=[o for o in bpy.data.objects if o.type=="MESH"]
    keep=[]
    for k,o in enumerate(sorted(obs,key=lambda o:(o.matrix_world.translation.x,o.name))):
        # transformaties vastleggen, ouder los
        mw=o.matrix_world.copy(); o.parent=None; o.matrix_world=mw
        o.data=o.data.copy(); o.data.transform(o.matrix_world); o.matrix_world.identity()
        tris=sum(len(p.vertices)-2 for p in o.data.polygons)
        if tris>doel:
            d=o.modifiers.new("dec","DECIMATE"); d.ratio=max(0.02,doel/tris); d.use_collapse_triangulate=True
            dg=bpy.context.evaluated_depsgraph_get(); me=bpy.data.meshes.new_from_object(o.evaluated_get(dg))
            o.modifiers.clear(); o.data=me
        # oorsprong: midden van de voet
        vs=[v.co for v in o.data.vertices]; mn=Vector((min(v.x for v in vs),min(v.y for v in vs),min(v.z for v in vs)))
        mx=Vector((max(v.x for v in vs),max(v.y for v in vs),max(v.z for v in vs)))
        base=Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z)); o.data.transform(__import__("mathutils").Matrix.Translation(-base))
        o.name=f"PH_{pid}_{k}"; o.data.name=o.name
        for p in o.data.polygons: p.use_smooth=True
        keep.append((o.name,sum(len(p.vertices)-2 for p in o.data.polygons),[round(mx[i]-mn[i],3) for i in range(3)],[m.name for m in o.data.materials]))
        o.location=(0,0,0)
    for o in bpy.data.objects: o.select_set(o.type=="MESH")
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,pid+".fbx"),use_selection=True,global_scale=1.0,apply_scale_options='FBX_SCALE_ALL',
                             apply_unit_scale=True,axis_forward='-Z',axis_up='Y',object_types={'MESH'},mesh_smooth_type='FACE',add_leaf_bones=False)
    # texturen per materiaal
    mats={}
    for m in bpy.data.materials:
        if not m.node_tree: continue
        imgs={}
        for n in m.node_tree.nodes:
            if n.type=="TEX_IMAGE" and n.image:
                fp=bpy.path.abspath(n.image.filepath); nm=os.path.basename(fp).lower()
                kind="diff" if "diff" in nm else "nor" if "nor" in nm else "arm" if "arm" in nm else None
                if kind: imgs[kind]=fp
        td=os.path.join(TEX,pid); os.makedirs(td,exist_ok=True)
        for kind,fp in imgs.items():
            img=bpy.data.images.load(fp); img.scale(min(1024,img.size[0]),min(1024,img.size[1]))
            if kind=="arm":   # ruwheid = groen kanaal
                px=list(img.pixels); r=[0.0]*len(px)
                for i in range(0,len(px),4): g=px[i+1]; r[i]=r[i+1]=r[i+2]=g; r[i+3]=1.0
                img.pixels=r; kind="rough"
            img.filepath_raw=os.path.join(td,f"{m.name}_{kind}.png"); img.file_format="PNG"; img.save()
        mats[m.name]=sorted(imgs.keys())
    info[pid]={"objects":keep,"materials":mats}
    print("PH",pid,len(keep),"varianten",[k[1] for k in keep],"tris; mats",mats)
json.dump(info,open(os.path.join(OUT,"polyhaven_info.json"),"w"),indent=1)
