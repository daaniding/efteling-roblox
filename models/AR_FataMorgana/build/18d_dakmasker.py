"""18d_dakmasker: welke rastercellen (0,25 m, zelfde raster als 18p_routeplan) liggen onder een dak/gebouwdeel van Fata Morgana
(straal van z 60 omlaag raakt iets boven z 2). Uit: ref/route_dak.npy. De vaarroute (18_route) blijft binnen dit masker zodat er
buiten geen gat of plaat in de grond komt. Gebruik: blender --background AR_FataMorgana_master.blend --python build/18d_dakmasker.py"""
import bpy, numpy as np, os
from mathutils import Vector
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py"); G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6); L = G6["G3"]["L"]
for o in bpy.data.objects:
    if o.type == "MESH" and o.get("deel") in ("route", "boten"): o.hide_viewport = True
dg = bpy.context.evaluated_depsgraph_get()
S = 0.25; X0, X1, Y0, Y1 = -74.0, 13.0, -352.0, -294.0
xs = np.arange(X0 + S / 2, X1, S); ys = np.arange(Y1 - S / 2, Y0, -S)
dak = np.zeros((len(ys), len(xs)), bool)
for r, y in enumerate(ys):
    for c, x in enumerate(xs):
        hit, loc, *_ = bpy.context.scene.ray_cast(dg, L(x, y) + Vector((0, 0, 60)), Vector((0, 0, -1)))
        dak[r, c] = hit and loc.z > 2.0
np.save(os.path.join(D, "ref", "route_dak.npy"), dak)
print("[18d_dakmasker] onder dak: %.0f m2" % (dak.sum() * S * S))
