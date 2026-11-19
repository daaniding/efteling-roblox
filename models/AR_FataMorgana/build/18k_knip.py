"""18k_knip: bodemvlakken van de dichte gebouwblokken boven de vaarroute weghalen (Daan 19 nov: "de vloer die er nu door komt"), zodat de
kamers door kunnen lopen tot onder het dak (18h_hoogte -> ref/route_hoogte.npz, knip = cellen waar dat mag).
Weg: vlakken van deel in BLOK met normaal omlaag, alle hoekpunten rond z 0 (-0,4..0,4), waarvan de 2D-omhullende een knip-cel raakt.
Een gebouwbodem ziet niemand van buiten (staat op de grond), dus dit is alleen van binnen de route te merken.
LET OP: na het opnieuw draaien van een bouwscript van zo'n deel (03 noordgevel, 09 westkant, ...) deze stap opnieuw draaien.
Gebruik: blender --background --python build/18k_knip.py"""
import bpy, bmesh, os, numpy as np
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py"); G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6); T = G6["T"]; L = G6["G3"]["L"]
BLOK = {"noordgevel", "achterkant", "westkant", "kantelen", "zuidvleugel", "toren", "koepelgebouw"}   # koepelgebouw: het lage blok boven de jungle is dicht; de gang waar je loopt (halletje, binnenplaatsje) ligt bij x > 12,5, buiten de route
bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
H = np.load(os.path.join(D, "ref", "route_hoogte.npz")); K = H["knip"]; X0, Y1, S = float(H["X0"]), float(H["Y1"]), float(H["S"])
# modelmeters (park) uit wereld: L(x, y) is lineair; inverse via twee punten
o0 = L(0, 0); ex = L(1, 0) - o0; ey = L(0, 1) - o0
M = np.array([[ex.x, ey.x], [ex.y, ey.y]]); Mi = np.linalg.inv(M)
def park(v):
    q = Mi @ np.array([v.x - o0.x, v.y - o0.y]); return q[0], q[1]
def raakt(xs, ys):
    c0, c1 = int((min(xs) - X0) / S), int((max(xs) - X0) / S) + 1
    r0, r1 = int((Y1 - max(ys)) / S), int((Y1 - min(ys)) / S) + 1
    c0, r0 = max(c0, 0), max(r0, 0)
    return K[r0:r1, c0:c1].any()
tot = {}
for ob in bpy.data.objects:
    if ob.type != "MESH" or ob.get("deel") not in BLOK: continue
    mw = ob.matrix_world; bm = bmesh.new(); bm.from_mesh(ob.data)
    weg = []
    for f in bm.faces:
        n = (mw.to_3x3() @ f.normal)
        if n.z > -0.9: continue
        ws = [mw @ v.co for v in f.verts]
        if any(abs(w.z) > 0.4 for w in ws): continue
        pk = [park(w) for w in ws]
        if raakt([p[0] for p in pk], [p[1] for p in pk]): weg.append(f)
    if weg:
        bmesh.ops.delete(bm, geom=weg, context="FACES_ONLY"); bm.to_mesh(ob.data); ob.data.update()
        tot[ob.name] = len(weg)
    bm.free()
bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
print("[18k_knip] weg:", tot)
