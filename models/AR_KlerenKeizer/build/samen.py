"""samen.py: decor + omgeving in KK_samen.blend (alleen voor review-renders)."""
import bpy, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(D, "KK_decor_master.blend"))
forms = bpy.data.collections["FORMS"]
with bpy.data.libraries.load(os.path.join(D, "KK_omgeving_master.blend"), link=False) as (src, dst):
    dst.objects = [n for n in src.objects]
for o in dst.objects:
    if o is not None and o.type == "MESH": forms.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "KK_samen.blend"))
print("SAMEN", len(forms.objects))
