"""18k_knip: bodemvlakken van de dichte gebouwblokken boven de vaarroute weghalen (Daan 19 nov: "de vloer die er nu door komt"), zodat de
kamers door kunnen lopen tot onder het dak (18h_hoogte -> ref/route_hoogte.npz, knip = cellen waar dat mag).
Weg: vlakken van deel in BLOK met normaal omlaag, alle hoekpunten rond z 0 (-0,4..0,4), waarvan de 2D-omhullende een knip-cel raakt.
Een gebouwbodem ziet niemand van buiten (staat op de grond), dus dit is alleen van binnen de route te merken.
LET OP: na het opnieuw draaien van een bouwscript van zo'n deel (03 noordgevel, 09 westkant, ...) deze stap opnieuw draaien.
Gebruik: blender --background --python build/18k_knip.py"""
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py"); G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6); T = G6["T"]; L = G6["G3"]["L"]
BLOK = {"noordgevel", "achterkant", "westkant", "kantelen", "zuidvleugel", "toren", "koepelgebouw"}   # koepelgebouw: het lage blok boven de jungle is dicht; de gang waar je loopt (halletje, binnenplaatsje) ligt bij x > 12,5, buiten de route
bpy.ops.wm.open_mainfile(filepath=T["MASTER"])
H = np.load(os.path.join(D, "ref", "route_hoogte.npz")); K = H["knip"] | (np.nan_to_num(H["plafond"], nan=-9) > 1.0); X0, Y1, S = float(H["X0"]), float(H["Y1"]), float(H["S"])   # K: alle hoge kamercellen (bodems ziet niemand)
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
# 2) binnenmuren/overlays die IN een hoge kamer staan (19 nov: kantelen-binnenmuur en verweringsplaat in de jungle, sectie 1c):
#    vlakken van BLOK-delen waarvan het midden binnen een hoge kamercel ligt (0,3 m van de kamerrand af) en tussen z 0,05 en het
#    plafond van die cel; gevels (buitenrand van het gebouw) liggen buiten de kamers en blijven
PL = H["plafond"]; hoog = np.nan_to_num(PL, nan=-9) > 1.0
er = hoog.copy()
for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    sh = np.zeros_like(hoog); sh[max(dr, 0):hoog.shape[0] + min(dr, 0), max(dc, 0):hoog.shape[1] + min(dc, 0)] = hoog[max(-dr, 0):hoog.shape[0] + min(-dr, 0), max(-dc, 0):hoog.shape[1] + min(-dc, 0)]
    er &= sh
# alleen vlakken die helemaal onder een dak liggen (ref/route_dak.npy, zelfde raster)
dak = np.load(os.path.join(D, "ref", "route_dak.npy")); binnen = dak.copy()
for _ in range(0):                                                       # geen marge meer: de voorkanttest (1 m) beschermt de gevels
    b2 = binnen.copy()
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        sh = np.zeros_like(binnen); sh[max(dr, 0):binnen.shape[0] + min(dr, 0), max(dc, 0):binnen.shape[1] + min(dc, 0)] = binnen[max(-dr, 0):binnen.shape[0] + min(-dr, 0), max(-dc, 0):binnen.shape[1] + min(-dc, 0)]
        b2 &= sh
    binnen = b2
def diep_binnen(w):
    x, y = park(w); r, c = int((Y1 - y) / S), int((x - X0) / S)
    return 0 <= r < binnen.shape[0] and 0 <= c < binnen.shape[1] and binnen[r, c]
from mathutils import Vector
for o in bpy.data.objects:
    if o.type == "MESH" and o.get("deel") in ("route", "boten", "junglegroen", "junglerots", "junglegordijn", "junglenacht"): o.hide_viewport = True
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
tot2 = {}
for ob in bpy.data.objects:
    if ob.type != "MESH" or ob.get("deel") not in BLOK: continue
    mw = ob.matrix_world; bm = bmesh.new(); bm.from_mesh(ob.data); weg = []
    # grote vlakken die deels in een hoge kamer staan eerst opknippen (1 m-raster in parkmeters), dan per stuk beslissen
    mi = mw.inverted()
    def kandidaat(f):
        """raakt (een hoekpunt of het midden van) dit grote vlak een hoge kamer onder het plafond? dan opknippen"""
        if f.calc_area() <= 1.0: return False
        ws = [mw @ v.co for v in f.verts]; c = mw @ f.calc_center_median(); zmin = min(w.z for w in ws)
        if max(c.z, zmin + 0.05) <= 0.05: return False
        for w in ws + [c]:
            x, y = park(w); r, k = int((Y1 - y) / S), int((x - X0) / S)
            for rr in (r - 1, r, r + 1):
                for kk in (k - 1, k, k + 1):
                    if 0 <= rr < er.shape[0] and 0 <= kk < er.shape[1] and er[rr, kk] and zmin < PL[rr, kk] - 0.05: return True
        return False
    for as_ in (0, 1):
        groot = [f for f in bm.faces if kandidaat(f)]
        if not groot: continue
        ws = [park(mw @ v.co) for f in groot for v in f.verts]
        lo, hi = math.floor(min(w[as_] for w in ws)), math.ceil(max(w[as_] for w in ws))
        nrm = (ex if as_ == 0 else ey).copy(); nrm.z = 0; nrm.normalize()
        for k in range(lo + 1, hi):
            co = o0 + (ex * k if as_ == 0 else ey * k)
            geo = [f for f in bm.faces if kandidaat(f)]
            geom = list({v for f in geo for v in f.verts}) + list({e for f in geo for e in f.edges}) + geo
            if geom: bmesh.ops.bisect_plane(bm, geom=geom, plane_co=mi @ co, plane_no=(mi.to_3x3() @ nrm).normalized())
    groot = [f for f in bm.faces if kandidaat(f)]                       # ook in de hoogte (per meter): het deel boven een lager dak blijft
    if groot:
        zs = [(mw @ v.co).z for f in groot for v in f.verts]
        for k in range(math.floor(min(zs)) + 1, math.ceil(max(zs))):
            geo = [f for f in bm.faces if kandidaat(f)]
            geom = list({v for f in geo for v in f.verts}) + list({e for f in geo for e in f.edges}) + geo
            if geom: bmesh.ops.bisect_plane(bm, geom=geom, plane_co=mi @ Vector((0, 0, k)), plane_no=(mi.to_3x3() @ Vector((0, 0, 1))).normalized())
    for f in bm.faces:
        c = mw @ f.calc_center_median()
        x, y = park(c); col_ = int((x - X0) / S); row = int((Y1 - y) / S)
        if not (0 <= row < er.shape[0] and 0 <= col_ < er.shape[1]) or not er[row, col_]: continue
        if ob.get("deel") == "koepelgebouw" and math.hypot(x + 4.0, y + 310.6) < 3.5 and c.z > 8.0: continue   # hoektorentje: open stage met bogen boven z 8,7 (dichte voet eronder)
        zlaag = min((mw @ v.co).z for v in f.verts)
        if 0.05 < c.z and zlaag < PL[row, col_] - 0.05 and all(diep_binnen(mw @ v.co) for v in f.verts):
            # nooit iets dat van buiten te zien is: vóór het vlak (langs de normaal, 1 m) moet er een dak boven zitten
            nw = (mw.to_3x3() @ f.normal).normalized(); open_lucht = False
            for kant in (1,):                                                    # alleen de voorkant: een vlak zie je alleen van de kant waar het naar wijst
                for v in f.verts:                                            # elk hoekpunt: een vlak kan boven een lager dak uitsteken
                    w = mw @ v.co; q = w + (c - w) * 0.15 + nw * 1.0 * kant + Vector((0, 0, 0.02))   # 1 m: over dikke muren en smalle spleten tussen blokken heen
                    hit, *_ = sc.ray_cast(dg, q, Vector((0, 0, 1)))
                    q2 = w + (c - w) * 0.15 + nw * 0.3 * kant; x2, y2 = park(q2); r2, c2 = int((Y1 - y2) / S), int((x2 - X0) / S)
                    kamer = 0 <= r2 < er.shape[0] and 0 <= c2 < er.shape[1] and er[r2, c2] and q2.z < PL[r2, c2]
                    if not hit and not kamer: open_lucht = True; break         # wijst het vlak de kamer in (0,3 m), dan zie je het alleen van binnen
            if not open_lucht: weg.append(f)
    if weg:
        bmesh.ops.delete(bm, geom=weg, context="FACES"); bm.to_mesh(ob.data); ob.data.update(); tot2[ob.name] = len(weg)
    bm.free()
for o in bpy.data.objects:
    if o.type == "MESH" and o.get("deel") in ("route", "boten", "junglegroen", "junglerots", "junglegordijn", "junglenacht"): o.hide_viewport = False
bpy.ops.wm.save_as_mainfile(filepath=T["MASTER"])
print("[18k_knip] weg:", tot, "| binnen hoge kamers:", tot2)
