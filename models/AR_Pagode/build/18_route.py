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
            p0 = Vector((CX, CY, Z_I)) + u * 9.12 + off; p1 = Vector((CX, CY, Z_I)) + u * 12.6 + off   # tot tegen het stationshek (r 9.05)
            NS["spijlenhek"](f"AR_Pagode_R_gang_{naam}_{s + 1}", [p0, p1], h=1.0)
    # omheining: de route moet aan alle kanten dicht zijn (Daan: "hekjes soms en dan kan je er nog langs"); zwart spijlenhek 1.0 m
    aL, A_ZUID, R_BO, A_RAIL, Z_P, N_RIJ = NS["aL"], NS["A_ZUID"], NS["R_BO"], NS["A_RAIL"], NS["Z_P"], NS["N_RIJ"]
    pt, boog, hek = NS["pt"], NS["boog"], NS["spijlenhek"]
    # 1 aanlooppad: buitenrand (achter de granieten band) van de oostkant tot de reling langs het laantje; ingang = de oostkant (88 gr)
    hek("AR_Pagode_R_om_aanloop", boog(17.75, 88.3, aL(17.75) - math.degrees(0.15 / 17.75), Z_P, 1.0), h=1.0)
    # 2 eind laantje -> onderpad -> zuidkant tribune: buitenrand onderpad (r 26.95) en de zuidrand (A_ZUID) tot het bordes
    a_onder = aL(25.0) - math.degrees(0.15 / 25.0)          # recht onder het eind van de reling langs het laantje
    hek("AR_Pagode_R_om_laaneind", [pt(25.0, a_onder, Z_P), pt(26.95, a_onder, Z_P)], h=1.0)
    hek("AR_Pagode_R_om_onderpad", boog(26.95, a_onder, A_ZUID - math.degrees(0.1 / 26.95), Z_P, 1.0), h=1.0)
    # op de rand van de rijen (10 cm binnen A_ZUID), niet ernaast op het gras; per rij een knik zodat de voet op de rij staat
    zuid = [pt(26.95, A_ZUID - math.degrees(0.1 / 26.95), Z_P)]
    for t in range(N_RIJ - 1, -1, -1):
        for r in (14.0 + t + 0.98, 14.0 + t + 0.02):
            zuid.append(pt(r, A_ZUID - math.degrees(0.1 / r), NS["ztop"](t)))
    zuid.append(pt(R_BO + 0.05, A_ZUID - math.degrees(0.1 / 14.05), Z_I))
    hek("AR_Pagode_R_om_zuid", zuid, h=1.0)
    # 3 bordes: hek tussen bordes en tribune doortrekken tot de zuidrand (anders langs de tourniquets via het zuidstrookje)
    a_kop = A_ZUID - math.degrees(0.1 / 14.05)
    hek("AR_Pagode_R_om_bordeszuid", boog(R_BO + 0.05, A_RAIL - 2.0, a_kop, Z_I, 1.0), h=1.0)
    hek("AR_Pagode_R_om_bordeskop", [pt(R_BO + 0.05, a_kop, Z_I), pt(9.05, a_kop, Z_I)], h=1.0)     # dwars over bordes en vlonder tot het stationshek (r 9.05)
    hek("AR_Pagode_R_om_sleufzuid", [pt(9.05, 172.2, Z_I), pt(10.7, 172.2, Z_I)], h=1.0)            # andere kant van de armsleuf
    # 4 vlonder zuid/west (tussen sleuf en uitgangsmuur): open buitenrand -> hek op r 10.7
    hek("AR_Pagode_R_om_vlonderzuid", boog(10.7, 172.2, 308.3, Z_I, 1.5), h=1.0)                      # tot het begin van het oosthek
    # 5 uitgangskant en instapkant scheiden: dwars over de vlonder op 99.6 graden, en het perk afschermen (r 10.65, 54-99.6)
    hek("AR_Pagode_R_om_scheiding", [pt(9.05, 99.6, Z_I), pt(10.65, 99.6, Z_I)], h=1.0)
    hek("AR_Pagode_R_om_perk", boog(10.65, 53.7, 99.6, Z_I, 1.5), h=1.0)                               # vanaf het eind van het oosthek
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
