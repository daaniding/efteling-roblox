"""03b_poorten: openingen voor de in- en uitstappoortjes in de balustrade van de gondel (poorten.py). Draai NA 03_forms.py.
Knipt de drie regels (boven, midden, onder) en de spijlen weg in elke opening (BREED + 2 x 5 cm) en zet aan beide kanten een
poortpaal (groen, 6 cm). De klaphekjes zelf worden in Roblox gebouwd (bewegen: open bij het instappen).
Gondelframe: Blender-lokaal rond (0, 0), hoek alfa = atan2(y, x). Gebruik: blender --background --python build/03b_poorten.py -- --master AR_Pagode_master.blend"""
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix

HIER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HIER)
import poorten as PT

OWNER = "phase:03b_poorten"
RB = 8.3                    # straal balustrade (03_forms)
DEK = 1.5 + 0.7             # dek boven de onderkant (03_forms: RAND + 0.7)
DELEN = ("AR_Pagode_F_hek_boven", "AR_Pagode_F_hek_onder", "AR_Pagode_F_hek_midden", "AR_Pagode_F_hek_spijlen")


def in_opening(alfa_graden):
    for _, a, _ in PT.POORTEN:
        if abs((alfa_graden - a + 180) % 360 - 180) < PT.half_hoek(RB, 0.1): return True
    return False


def build():
    a = sys.argv[sys.argv.index("--") + 1:]
    m = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=m)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    weg = 0
    for naam in DELEN:
        ob = bpy.data.objects.get(naam)
        if not ob: continue
        bm = bmesh.new(); bm.from_mesh(ob.data)
        doel = [f for f in bm.faces if in_opening(math.degrees(math.atan2(f.calc_center_median().y, f.calc_center_median().x)))]
        weg += len(doel)
        bmesh.ops.delete(bm, geom=doel, context="FACES")
        bm.to_mesh(ob.data); bm.free()
    col = bpy.data.collections["LOW"]
    for naam, alfa, soort in PT.POORTEN:
        h = math.radians(PT.half_hoek(RB, 0.1))
        for s in (-1, 1):
            ang = math.radians(alfa) + s * h
            p = Vector((RB * math.cos(ang), RB * math.sin(ang), 0))
            bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.05, radius2=0.05, depth=1.36)
            bmesh.ops.translate(bm, vec=p + Vector((0, 0, DEK + 0.68)), verts=bm.verts)
            me = bpy.data.meshes.new(f"AR_Pagode_F_poortpaal_{naam}_{s + 1}"); bm.to_mesh(me); bm.free()
            o = bpy.data.objects.new(me.name, me); col.objects.link(o); o["rol"] = "groen"; o["owner"] = OWNER
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=m)
    print("[03b_poorten] %d vlakken weggeknipt, %d poortpalen" % (weg, 2 * len(PT.POORTEN)))


build()
