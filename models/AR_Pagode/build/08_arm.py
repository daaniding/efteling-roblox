"""08_arm: hefarm van de Pagode in de stand OMHOOG (Daan). Draai NA 02/03; daarna 05_materials (rol 'arm'/'armzijde').
Maten uit ref/eftepedia/Pagode_tech.png (gondel 152 px = 17 m -> 8.94 px/m) en Eftepedia-tekst:
  - naaf (aangrijppunt) midden in de holle onderkant, RAND + 3.8 (02_blockout NAAF)
  - kort stuk naaf -> knik: 9.3 m, 43.5 graden uit het lood (schema 83 px)
  - lang stuk knik -> draaias: 36.5 m, 9.3 graden uit het lood, terug richting de as (schema 326 px)
  - gondelmidden staat vrijwel recht boven de draaias (schema: 492 vs 490 px); as -> gondel ~42 m (Eftepedia 43 m)
  - onder de draaias loopt de arm 5 m door naar het contragewicht (stukje 5)
Doorsnede: 1.6 m in het buigvlak (ref/zijkant_onder.jpg: ~80 px bij 50 px/m), 1.2 m dwars (inferred).
Lokaal frame = gondelframe (z=0 onderkant oude schotel, dek op 2.2); de arm buigt in het x-z-vlak naar +x.
Gebruik: blender --background --python build/08_arm.py -- --master AR_Pagode_master.blend"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

RAND, NAAF = 1.5, 2.5
# foto (ref/eftepedia/Pagode.jpg) gaat voor op het schema: kort stuk ~34 graden, knik ~4 m naast de as (schema: 9.3 m / 43.5)
L_KORT, A_KORT = 7.2, math.radians(34.0)
L_LANG = 37.0
X_AS = 0.5                 # draaias vrijwel recht onder het gondelmidden (schema)
A_LANG = math.asin((L_KORT * math.sin(A_KORT) - X_AS) / L_LANG)
L_ONDER = 5.0
BOOG = 2.5                 # knikstraal (foto van onder: vloeiende S, inferred)
B_VLAK, B_DWARS = 1.6, 1.2


def pad():
    H = Vector((0, 0, RAND + NAAF + 0.2))   # 20 cm in de naaf
    d1 = Vector((math.sin(A_KORT), 0, -math.cos(A_KORT)))
    B = H + d1 * L_KORT
    d2 = Vector((-math.sin(A_LANG), 0, -math.cos(A_LANG)))
    P = B + d2 * L_LANG
    E = P + d2 * L_ONDER
    # afronding van de knik: raakpunten op BOOG * tan(half) van B
    hoek = math.acos(max(-1, min(1, d1.dot(d2))))
    t = BOOG * math.tan(hoek / 2)
    T1, T2 = B - d1 * t, B + d2 * t
    pts = []
    for i in range(12): pts.append(H + (T1 - H) * (i / 12))
    for i in range(13):    # kwadratische bezier T1 - B - T2 benadert de boog
        u = i / 12; pts.append(T1 * (1 - u) ** 2 + B * 2 * u * (1 - u) + T2 * u * u)
    for i in range(1, 31): pts.append(T2 + (E - T2) * (i / 30))
    return pts, P, B


def build():
    a = sys.argv[sys.argv.index("--") + 1:]
    m = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=m)
    for ob in [o for o in bpy.data.objects if o.name.startswith("AR_Pagode_arm")]:
        bpy.data.objects.remove(ob, do_unlink=True)
    pts, P, B = pad()
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
    rings, s_acc, s = [], [], 0.0
    for i, p in enumerate(pts):
        if i: s += (p - pts[i - 1]).length
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        n = Vector((-t.z, 0, t.x)); b = Vector((0, 1, 0))
        hv, hd = B_VLAK / 2, B_DWARS / 2
        rings.append([bm.verts.new(p + n * x + b * y) for x, y in ((-hv, -hd), (hv, -hd), (hv, hd), (-hv, hd))])
        s_acc.append(s)
    # zijden: 0 = -y (sier), 1 = +n (rand), 2 = +y (sier), 3 = -n (rand)
    for i in range(len(rings) - 1):
        for k in range(4):
            a0, a1 = rings[i][k], rings[i][(k + 1) % 4]
            b0, b1 = rings[i + 1][k], rings[i + 1][(k + 1) % 4]
            f = bm.faces.new((a0, a1, b1, b0))
            f.material_index = 0 if k in (0, 2) else 1
            for l, (su, sv) in zip(f.loops, ((s_acc[i], 0), (s_acc[i], 1), (s_acc[i + 1], 1), (s_acc[i + 1], 0))):
                l[uv].uv = (su / B_VLAK, sv)
    for ring in (rings[0], rings[-1]):
        f = bm.faces.new(ring); f.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("AR_Pagode_arm"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("AR_Pagode_arm", me)
    (bpy.data.collections.get("LOW") or bpy.context.scene.collection).objects.link(ob)
    ob["rol"] = "arm"; ob["owner"] = "phase:08_arm"
    ob["draaias"] = list(P); ob["knik"] = list(B)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=m)
    print("[08_arm] arm: lengte %.1f m, draaias op (%.2f, %.2f), knik op (%.2f, %.2f); dek -> as %.1f m"
          % (s, P.x, P.z, B.x, B.z, 2.2 - P.z))


build()
