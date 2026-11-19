"""18h_hoogte: hoe hoog mag elke kamer van de vaarroute worden (Daan 19 nov: "misschien moeten de kamers hoger en zal er het een en
ander weggehaald moeten worden zoals de vloer die er nu door komt").
Per rastercel (0,25 m, raster van 18p/route_plan.npz, kamers + vaargoot) een straal omhoog vanaf z -2:
  - eerste raakvlak = de onderkant van een dicht gebouwblok (bodemvlak rond z 0, normaal omlaag, deel in BLOK): dat bodemvlak mag weg
    (18k_knip) en de kamer gaat door tot onder het dak van dat blok: plafond = volgende raakvlak - 0,25 m (max ZMAX)
  - eerste raakvlak hoger dan z 1 in een gebouwblok (holle ruimte onder een dak): plafond = dat vlak - 0,25 m
  - eerste raakvlak iets anders (vloer van de gang/het koepelgebouw, waar je loopt): plafond blijft laag, net onder dat vlak
Uit: ref/route_hoogte.npz (plafond z per cel, NaN buiten de route; knip = cellen waar het bodemvlak weg mag) + review/18h_hoogte.png.
Gebruik: blender --background AR_FataMorgana_master.blend --python build/18h_hoogte.py"""
import bpy, numpy as np, os, collections
from mathutils import Vector
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F6 = os.path.join(D, "build", "06_kantelen.py"); G6 = {"__file__": F6, "__name__": "lib"}
exec(compile(open(F6).read().rsplit("\nmain()", 1)[0], F6, "exec"), G6); L = G6["G3"]["L"]
BLOK = {"noordgevel", "achterkant", "westkant", "kantelen", "zuidvleugel", "toren"}
ZMAX, ZLAAG = 9.0, -0.05
for o in bpy.data.objects:
    if o.type == "MESH" and o.get("deel") in ("route", "boten"): o.hide_viewport = True
dg = bpy.context.evaluated_depsgraph_get()
P = np.load(os.path.join(D, "ref", "route_plan.npz"))
uni = P["blauw"] | P["zand"]; S = 0.25; X0, Y1 = -74.0, -294.0
plaf = np.full(uni.shape, np.nan); knip = np.zeros(uni.shape, bool); wat = collections.Counter(); lz = collections.Counter()
sc = bpy.context.scene
for r, c in zip(*np.nonzero(uni)):
    x, y = X0 + (c + .5) * S, Y1 - (r + .5) * S
    o = L(x, y)
    hit, loc, n, i, ob, m = sc.ray_cast(dg, o + Vector((0, 0, -2.0)), Vector((0, 0, 1)))
    if not hit: plaf[r, c] = ZLAAG; wat["leeg"] += 1; continue
    if ob.get("deel") in BLOK and abs(loc.z) < 0.35 and n.z < -0.5:
        h2, l2, n2, *_ = sc.ray_cast(dg, loc + Vector((0, 0, 0.02)), Vector((0, 0, 1)))
        top = l2.z if h2 else ZMAX + 0.25
        plaf[r, c] = min(ZMAX, top - 0.25); knip[r, c] = True; wat["hoog " + ob["deel"]] += 1
    elif loc.z > 1.0 and ob.get("deel") in BLOK:                                # geen bodem: holle ruimte tot de onderkant van het dak
        plaf[r, c] = min(ZMAX, loc.z - 0.25); wat["hoog (hol) " + ob["deel"]] += 1
    else:
        plaf[r, c] = min(ZLAAG, loc.z - 0.03); wat["laag %s/%s" % (ob.get("deel"), ob.get("rol"))] += 1
        lz["%s z%.1f n%.1f" % (ob.get("deel"), loc.z, n.z)] += 1
# opschonen: losse lage strepen/punten in een hoge kamer (straal precies op een naad) en randcellen zonder dak erboven
rr, cc = np.nonzero(uni); nieuw = plaf.copy()
for r, c in zip(rr, cc):
    w = plaf[max(0, r - 2):r + 3, max(0, c - 2):c + 3]; w = w[~np.isnan(w)]
    hoog = w[w > 1.0]
    if plaf[r, c] < 1.0 and len(hoog) >= 0.7 * len(w): nieuw[r, c] = np.median(hoog); knip[r, c] = True
    elif plaf[r, c] >= ZMAX - 0.01 and len(w) > 1: nieuw[r, c] = np.median(w)
plaf = np.where(nieuw > 1.0, np.minimum(np.floor(nieuw * 4) / 4, 7.5), np.minimum(nieuw, ZLAAG))        # hoge plafonds op 0,25 m omlaag afgerond
np.savez_compressed(os.path.join(D, "ref", "route_hoogte.npz"), plafond=plaf, knip=knip, X0=X0, Y1=Y1, S=S)
v = plaf[~np.isnan(plaf)]
print("[18h_hoogte]", sorted(wat.items(), key=lambda t: -t[1])[:14])
print("[18h_hoogte] plafond percentielen", np.round(np.percentile(v, [5, 25, 50, 75, 95]), 2), "hoog", knip.sum(), "van", uni.sum())
print("[18h_hoogte] laag:", lz.most_common(12))
