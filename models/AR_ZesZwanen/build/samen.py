"""samen.py: kasteel + omgeving + 6 zwanen (op de vaarbaan, OSM 837234781) in een preview-bestand ZZ_samen.blend (alleen voor review)."""
import bpy, os, math, json
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(D, os.environ.get("ZZ_K", "ZZ_kasteel_master.blend")))
forms = bpy.data.collections["FORMS"]
def haal(blend):
    with bpy.data.libraries.load(os.path.join(D, blend), link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    out = []
    for o in dst.objects:
        if o is None or o.type != "MESH": continue
        forms.objects.link(o); out.append(o)
    return out
haal(os.environ.get("ZZ_O", "ZZ_omgeving_master.blend"))
zw = haal("ZZ_zwaan_master.blend")
ZWANEN = json.load(open(os.path.join(D, "exports", "zwanen.json")))
WL = -0.35
for i, (x, y, dx, dy) in enumerate(ZWANEN):
    th = math.atan2(dx, -dy)
    for o in zw:
        c = o if i == 0 else o.copy()
        if i: forms.objects.link(c)
        c.location = (x, y, WL); c.rotation_euler = (0, 0, th)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "ZZ_samen.blend"))
print("SAMEN", len(forms.objects))
