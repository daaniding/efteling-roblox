"""combo.py: huis-master + omgeving-master samen in review/combo.blend (alleen voor renders). Blender -b -P combo.py"""
import bpy, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(R, "TK_boom_master.blend"))
with bpy.data.libraries.load(os.path.join(R, "TK_omgeving_master.blend")) as (src, dst):
    dst.objects = [n for n in src.objects if n.startswith("TO_")]
forms = bpy.data.collections["FORMS"]
for o in dst.objects:
    if o: forms.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R, "review", "combo.blend"))
print("COMBO", len(dst.objects))
