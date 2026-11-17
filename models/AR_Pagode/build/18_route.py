"""18_route: alleen de route van de Pagode overhouden (Daan 17 nov: "niet dat plein, haal dat allemaal weg; gewoon een ingang
en een uitgang die gebruikt kunnen worden, elke cm checken, op schaal"). Draai NA 12, 14, 15, 16, 17 en VOOR 05.
Weg: plein (behalve het aanlooppad naar het laantje), bankjes, pot, pleinbak, pleinlantaarn, plantvak, tuin (14), Toko en terras
(15), Gondoletta (16), pad oost voorbij de uitgang. Blijft: aanlooppad, PAGODE-bord, laantje met muren, tribune-wachtrij,
trapstrook, tourniquets, controlehuisje, bordes, station, uitgangsmuur, uitgangstrap en het pad tot 25 graden voorbij.
Nieuw: per instappoortje (poorten.py) een gangetje van zwarte hekjes (1.0 m hoog) over vlonder en bordes, recht op het poortje.
Schrijft exports/omgeving_lampen.json en omgeving_meubilair.json opnieuw (zonder de weggehaalde stukken).
Gebruik: blender --background --python build/18_route.py -- --master AR_Pagode_master.blend"""
import bpy, sys, os, math, json
from mathutils import Vector

HIER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HIER)
import poorten as PT
NS = {"__name__": "omgeving12", "__file__": os.path.join(HIER, "12_omgeving.py")}
bron = open(os.path.join(HIER, "12_omgeving.py")).read().rsplit("\nbuild()", 1)[0]
exec(compile(bron, "12_omgeving.py", "exec"), NS)
OWNER = "phase:18_route"; NS["OWNER"] = OWNER
D = os.path.dirname(HIER)
CX, CY, Z_I = NS["CX"], NS["CY"], NS["Z_I"]

WEG_12 = ("AR_Pagode_O_plein0", "AR_Pagode_O_plein1", "AR_Pagode_O_plein2", "AR_Pagode_O_plein3", "AR_Pagode_O_plein4",
          "AR_Pagode_O_bank", "AR_Pagode_O_pot", "AR_Pagode_O_bak_plein", "AR_Pagode_O_lamp_plein", "AR_Pagode_O_band_tuin",
          "AR_Pagode_O_pad_oost2", "AR_Pagode_O_pad_oost3", "AR_Pagode_O_lamp_uit1")
WEG_17 = ("AR_Pagode_S_pleinvoor", "AR_Pagode_S_plantvak", "AR_Pagode_S_tuinrotsen")
WEG_EIGENAAR = ("phase:14_planten", "phase:15_toko", "phase:16_gondoletta")


def build():
    a = sys.argv[sys.argv.index("--") + 1:]
    m = os.path.abspath(a[a.index("--master") + 1])
    bpy.ops.wm.open_mainfile(filepath=m)
    for o in [o for o in bpy.data.objects if o.get("owner") == OWNER]:
        bpy.data.objects.remove(o, do_unlink=True)
    n = 0
    for o in list(bpy.data.objects):
        e = o.get("owner", "")
        if e in WEG_EIGENAAR or (e == "phase:12_omgeving" and o.name.startswith(WEG_12)) or (e == "phase:17_steenwerk" and o.name.startswith(WEG_17)):
            bpy.data.objects.remove(o, do_unlink=True); n += 1
    # gangetjes naar de instappoortjes: twee zwarte hekjes (1.0 m) van de stationsrand (r 9.25) tot r 12.6, BREED + 0.1 uit elkaar
    for naam, alfa, soort in PT.POORTEN:
        if soort != "in": continue
        c = math.radians(PT.park(alfa)); u = Vector((math.cos(c), math.sin(c), 0)); t = Vector((-u.y, u.x, 0))
        for s in (-1, 1):
            off = t * s * (PT.BREED / 2 + 0.05)
            p0 = Vector((CX, CY, Z_I)) + u * 9.25 + off; p1 = Vector((CX, CY, Z_I)) + u * 12.6 + off
            NS["spijlenhek"](f"AR_Pagode_R_gang_{naam}_{s + 1}", [p0, p1], h=1.0)
    # lampen en meubilair zonder de weggehaalde stukken
    def bestaat(x, y): return any(o.name.startswith("AR_Pagode_O_lamp") and (Vector((x, y)) - o.matrix_world.translation.xy).length < 0.6
                                  for o in bpy.data.objects)
    lp = os.path.join(D, "exports", "omgeving_lampen.json")
    lampen = [l for l in json.load(open(lp)) if any(o.name.startswith("AR_Pagode_O_lamp") and o.name.endswith(("_voet", "_plint"))
              and (Vector((l[0], l[1])) - Vector(sum((o.matrix_world @ Vector(b) for b in o.bound_box), Vector()).xy / 8)).length < 0.6
              for o in bpy.data.objects)]
    json.dump(lampen, open(lp, "w"))
    hp = os.path.join(D, "exports", "omgeving_hekken.json")
    hek = json.load(open(hp))
    # hekken van weggehaalde delen eruit (niets op het plein), gangetjes erbij
    hek = [h for h in hek if not (math.hypot(h[0][0] - CX, h[0][1] - CY) > 17.6 and math.degrees(math.atan2(h[0][1] - CY, h[0][0] - CX)) < 88)]
    hek += [[list(a_), list(b_), hh] for a_, b_, hh in NS["HEKKEN"]]
    json.dump(hek, open(hp, "w"))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=m)
    print("[18_route] %d objecten weg, %d lantaarns over, gangetjes voor %d poortjes" % (n, len(lampen), sum(1 for p in PT.POORTEN if p[2] == "in")))


build()
