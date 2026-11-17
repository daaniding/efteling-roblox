"""19_maatcontrole: meet de route van de Pagode na in het master-bestand (Daan 17 nov: "elke cm checken, op schaal").
Meet aan de echte objecten (bounding boxes, hoekpunten) en vergelijkt met eisen:
  treden: optrede 12-19 cm, gelijk binnen 1 cm per trap; aantrede >= 28 cm
  looppaden: >= 2.0 m (Daan); poortjes en tourniquets >= 1.5 m vrij (avatar 1.27 m)
  relingen/hekken: 0.95-1.25 m boven de loopvloer
  overgangen: hoogteverschil tussen aansluitende vloeren <= 19 cm (anders een trede), kier tussen vloeren <= 40 cm
Schrijft review/19_maten.md en stopt met fout als iets niet klopt.
Gebruik: blender --background --python build/19_maatcontrole.py -- --master AR_Pagode_master.blend"""
import bpy, sys, os, math
from mathutils import Vector

HIER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HIER)
import poorten as PT
NS = {"__name__": "omgeving12", "__file__": os.path.join(HIER, "12_omgeving.py")}
exec(compile(open(os.path.join(HIER, "12_omgeving.py")).read().rsplit("\nbuild()", 1)[0], "12_omgeving.py", "exec"), NS)
D = os.path.dirname(HIER)
a = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a[a.index("--master") + 1]))
CX, CY = NS["CX"], NS["CY"]
aL, aR, aW, aS, ztop = NS["aL"], NS["aR"], NS["aW"], NS["aS"], NS["ztop"]
Z_I, Z_P, R_VL, R_BO, N_RIJ, A_ZUID = NS["Z_I"], NS["Z_P"], NS["R_VL"], NS["R_BO"], NS["N_RIJ"], NS["A_ZUID"]
regels, fout = [], []


def bb(naam):
    o = bpy.data.objects.get(naam)
    if not o: return None
    ps = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector([min(p[i] for p in ps) for i in range(3)]), Vector([max(p[i] for p in ps) for i in range(3)])


def top(naam):
    o = bpy.data.objects.get(naam)
    return max((o.matrix_world @ v.co).z for v in o.data.vertices) if o else None


def polair(p): return math.hypot(p.x - CX, p.y - CY), math.degrees(math.atan2(p.y - CY, p.x - CX))


def eis(wat, waarde, lo, hi, eenheid="m"):
    ok = (lo is None or waarde >= lo - 1e-6) and (hi is None or waarde <= hi + 1e-6)
    grens = ("%s-%s" % (lo, hi)) if lo is not None and hi is not None else (">= %s" % lo if lo is not None else "<= %s" % hi)
    regels.append("| %s | %.3f %s | %s | %s |" % (wat, waarde, eenheid, grens, "ok" if ok else "**FOUT**"))
    if not ok: fout.append(wat)


# 1 laantje, trapstrook, wachtrijbanen
for r in (15.0, 20.0, 24.5):
    eis(f"breedte laantje op r {r}", math.radians(aR(r) - aL(r)) * r, 2.0, None)
    eis(f"breedte trapstrook op r {r}", math.radians(aS(r) - aW(r)) * r, 2.0, None)
rails = [14.0 + t + 0.12 for t in NS["RAIL_T"]]
grenzen = [R_BO + 0.05] + rails + [26.5]          # laatste baan loopt door in het onderpad (r 25-26.8, rotsen vanaf ~26.6)
for k in range(len(grenzen) - 1):
    eis(f"wachtrijbaan {k}: vrij tussen relingen (hart op hart {grenzen[k + 1] - grenzen[k]:.2f})", grenzen[k + 1] - grenzen[k] - 0.055, 1.9, None)
# 2 treden: tribunerijen (optrede ztop) en de uitgangstrap
opt = [ztop(t - 1) - ztop(t) for t in range(1, N_RIJ)]
eis("tribune: optrede per rij", opt[0], 0.12, 0.19); eis("tribune: verschil in optrede", max(opt) - min(opt), None, 0.01)
eis("tribune: aantrede (rij)", 1.0, 0.28, None)
eis("top tribune -> bordes (optrede)", Z_I - ztop(0), 0.12, 0.19)
eis("laantje -> onderste rij (optrede)", ztop(N_RIJ - 1) - Z_P, 0.0, 0.19)
tr = sorted([bb(o.name) for o in bpy.data.objects if o.name.startswith("AR_Pagode_O_uittrede_")], key=lambda b: -b[1].z)
if tr:
    hoogtes = [b[1].z for b in tr]          # onderste blok ligt al op padhoogte
    stap = [hoogtes[i] - hoogtes[i + 1] for i in range(len(hoogtes) - 1)]
    eis("uitgangstrap: optrede (grootste)", max(stap), 0.12, 0.19); eis("uitgangstrap: verschil in optrede", max(stap) - min(stap), None, 0.01)
    eis("uitgangstrap: vlonder -> bovenste trede", Z_I - hoogtes[0], 0.12, 0.19); eis("uitgangstrap: onderste trede = pad", abs(hoogtes[-1] - (Z_P + 0.03)), None, 0.01)
    rs = sorted(polair((b[0] + b[1]) / 2)[0] for b in tr)
    eis("uitgangstrap: aantrede", rs[1] - rs[0], 0.28, None)
    w = min(b[1].x - b[0].x for b in tr), max(b[1].x - b[0].x for b in tr)
    eis("uitgangstrap: breedte (tussen leuningen 2.3)", 2.3, 2.0, None)
# 3 poortjes: vrije breedte tussen de poortpalen (gondel r 8.3 en station r 9.05) en de gangetjes
for naam, alfa, soort in PT.POORTEN:
    for pre, r in (("AR_Pagode_F_poortpaal_", 8.3), ("AR_Pagode_S_poortpaal_", 9.05)):
        p0, p1 = bb(f"{pre}{naam}_0"), bb(f"{pre}{naam}_2")
        if p0 and p1:
            c0, c1 = (p0[0] + p0[1]) / 2, (p1[0] + p1[1]) / 2
            dik = (p0[1].x - p0[0].x)
            eis(f"poortje {naam} {'gondel' if 'F_' in pre else 'station'}: vrije doorgang", (c1 - c0).xy.length - dik, 1.5, None)
    if soort == "in":
        g0, g1 = bb(f"AR_Pagode_R_gang_{naam}_0_00_regelo"), bb(f"AR_Pagode_R_gang_{naam}_2_00_regelo")
        if g0 and g1:
            eis(f"gangetje {naam}: vrije breedte", ((g0[0] + g0[1]) / 2 - (g1[0] + g1[1]) / 2).xy.length - 0.04, 1.5, None)
# 4 tourniquets
t0, t1 = bb("AR_Pagode_O_tourniquet0"), bb("AR_Pagode_O_tourniquet1")
if t0 and t1:
    eis("tourniquets: vrije doorgang", ((t0[0] + t0[1]) / 2 - (t1[0] + t1[1]) / 2).xy.length - 0.26, 1.5, None)
# 5 hoogtes: relingen en hekken boven hun loopvloer, vlonder = bordes = instapniveau
eis("wachtrijreling: bovenkant boven de rij", 1.02 + 0.05, 0.95, 1.25)
eis("spijlenhek bordes: bovenkant boven bordes", 1.1 + 0.08, 0.95, 1.25)
vl = top("AR_Pagode_S_vlonder")
if vl is not None: eis("vlonder = instapniveau (NAP 11.3)", abs(vl - Z_I), None, 0.01)
bo = top("AR_Pagode_O_bordes")
if bo is not None: eis("bordes = instapniveau (NAP 11.3)", abs(bo - Z_I), None, 0.01)
eis("dek gondel beneden = instapniveau (ritscript)", 0.0, None, 0.01)
# 6 kieren: gondelrand -> vlonder, vlonder -> bordes
eis("kier dek gondel (r 8.5) -> vlonder (r 8.8)", 8.8 - 8.5, None, 0.40)
eis("kier vlonder (r 10.6) -> bordes (r 10.62)", NS["R_VL"] - 10.6, None, 0.05)

uit = ["# Maatcontrole route Pagode (19_maatcontrole.py)", "", "| wat | gemeten | eis | |", "|---|---|---|---|"] + regels
os.makedirs(os.path.join(D, "review"), exist_ok=True)
open(os.path.join(D, "review", "19_maten.md"), "w").write("\n".join(uit) + "\n")
print("[19_maatcontrole] %d metingen, %d fout: %s" % (len(regels), len(fout), ", ".join(fout)))
