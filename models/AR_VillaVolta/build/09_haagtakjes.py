"""09_haagtakjes: lichte bladtakjes voor de haagschil uit Poly Haven shrub_02 (kleine blaadjes aan twijgen) en shrub_03.
Elk variant gedecimeerd tot ~900 (shrub_02) / ~500 (shrub_03) driehoeken, oorsprong midden voet. Export: exports/polyhaven/haag.fbx"""
import bpy, glob, os, sys
from mathutils import Vector, Matrix
a=sys.argv[sys.argv.index("--")+1:]; SRC=a[a.index("--src")+1]; OUT=a[a.index("--out")+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
for pid,doel in (("shrub_02",900),("shrub_03",500)):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glob.glob(os.path.join(SRC,pid,"*.gltf"))[0])
    new=sorted([o for o in bpy.data.objects if o not in before and o.type=="MESH"],key=lambda o:o.matrix_world.translation.x)
    for k,o in enumerate(new):
        mw=o.matrix_world.copy(); o.parent=None; o.matrix_world=mw
        o.data=o.data.copy(); o.data.transform(o.matrix_world); o.matrix_world.identity()
        t=sum(len(p.vertices)-2 for p in o.data.polygons)
        d=o.modifiers.new("d","DECIMATE"); d.ratio=min(1,doel/t); d.use_collapse_triangulate=True
        dg=bpy.context.evaluated_depsgraph_get(); me=bpy.data.meshes.new_from_object(o.evaluated_get(dg)); o.modifiers.clear(); o.data=me
        vs=[v.co for v in me.vertices]
        base=Vector(((min(v.x for v in vs)+max(v.x for v in vs))/2,(min(v.y for v in vs)+max(v.y for v in vs))/2,min(v.z for v in vs)))
        me.transform(Matrix.Translation(-base)); o.name=f"HG_{pid}_{k}"; me.name=o.name
        for p in me.polygons: p.use_smooth=True
        print("HG",o.name,sum(len(p.vertices)-2 for p in me.polygons))
for o in bpy.data.objects: o.select_set(o.type=="MESH")
bpy.ops.export_scene.fbx(filepath=OUT,use_selection=True,global_scale=1.0,apply_scale_options='FBX_SCALE_ALL',apply_unit_scale=True,
                         axis_forward='-Z',axis_up='Y',object_types={'MESH'},mesh_smooth_type='FACE',add_leaf_bones=False)
