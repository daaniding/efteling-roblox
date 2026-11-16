"""07_zfighting: zoekt vlakken van verschillende onderdelen die (bijna) samenvallen en dezelfde kant op kijken (= z-fighting).
Per vlak: kleine straal vanuit het vlakmidden langs de normaal (voor- en achteruit, 2 mm) tegen alle andere onderdelen;
treffer met een parallelle normaal (zelfde richting) = probleem. Tegengestelde normaal (twee delen die tegen elkaar liggen)
wordt apart geteld (meestal onzichtbaar, maar beter vermijden).
Gebruik: blender --background --python build/07_zfighting.py -- --master AR_Pagode_master.blend"""
import bpy, bmesh, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a[a.index("--master") + 1]))
dg = bpy.context.evaluated_depsgraph_get()
obs = [o for o in bpy.data.objects if o.name.startswith("AR_Pagode") and o.type in ("MESH", "CURVE")]
data = []
for o in obs:
    me = o.evaluated_get(dg).to_mesh()
    bm = bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); bm.normal_update()
    data.append((o.name, bm, BVHTree.FromBMesh(bm)))
    o.evaluated_get(dg).to_mesh_clear()
EPS = 0.002
zelfde, tegen = {}, {}
for i, (na, bma, _) in enumerate(data):
    for f in bma.faces:
        if f.calc_area() < 1e-4: continue
        c, n = f.calc_center_median(), f.normal
        for j, (nb, bmb, tb) in enumerate(data):
            if i == j: continue
            for s in (1, -1):
                hit = tb.ray_cast(c - n * s * EPS, n * s, 2 * EPS)
                if hit[0] is not None:
                    d = hit[1].dot(n)
                    if d > 0.98: zelfde[(na, nb)] = zelfde.get((na, nb), 0) + 1
                    elif d < -0.98: tegen[(na, nb)] = tegen.get((na, nb), 0) + 1
                    break
print("[zfighting] ZELFDE RICHTING (zichtbaar flikkeren):", len(zelfde))
for k, v in sorted(zelfde.items(), key=lambda x: -x[1])[:40]: print("   ", k, v)
print("[zfighting] tegen elkaar (meestal onzichtbaar):", len(tegen))
for k, v in sorted(tegen.items(), key=lambda x: -x[1])[:25]: print("   ", k, v)
