"""22_bezoekersroute: looproute voor NPC-bezoekers door de wachtrij (Daan 17 nov: mensen in de rij), parkframe zoals 12_omgeving.
Aanloop -> laantje af -> onderpad -> zigzag omhoog (baan voor baan tot het keerpunt) -> trapkop -> tourniquets -> bordes.
Punten midden in de banen (tussen de relingen) zodat niemand tegen een reling loopt. Schrijft exports/bezoekersroute.json:
[[x, y, z], ...] (z = vloer t.o.v. NAP 10). Gebruik: python3 build/22_bezoekersroute.py"""
import math, json, os
CX, CY = 360.0, 47.5
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B_LAAN, B_TRAP = 1.5, 2.2
def a_c(r): return 104 + (r - 14.2) * 0.95
def aL(r): return a_c(r) - math.degrees(B_LAAN / r)
def aR(r): return a_c(r) + math.degrees(B_LAAN / r)
def aW(r): return aR(r) + math.degrees(0.42 / r)
def aS(r): return aW(r) + math.degrees(B_TRAP / r)
def ztop(t): return 1.3 - 0.15 * (t + 1)
Z_P, Z_I, A_ZUID = -0.38, 1.3, 156.5
def pt(r, a, z): return [round(CX + r * math.cos(math.radians(a)), 3), round(CY + r * math.sin(math.radians(a)), 3), round(z, 3)]
def zrij(r): t = max(0, min(10, int(r - 14.0))); return ztop(t)

route = []
# aanloop (vanaf de ingang aan de oostkant) en het laantje af (midden, a_c)
route += [pt(30.0, 76.0, Z_P), pt(22.0, 82.0, Z_P), pt(16.4, 86.0, Z_P), pt(16.4, 95.0, Z_P), pt(15.6, a_c(15.6) - 0.5, Z_P)]   # van verder weg aanlopen
r = 15.6
while r < 24.6:
    r = min(24.6, r + 1.5); route.append(pt(r, a_c(r), Z_P))
# onderpad (r 25.8) naar de zuidkant: daar begint de onderste baan (open naar het onderpad)
for a in (118, 128, 138, 148):
    route.append(pt(25.8, a, Z_P))
# zigzag: banen tussen de relingen (rails op r 16.12 .. 24.12); keerpunten: rail t=2,6,10 open aan de zuidkant,
# t=4,8 open aan de noordkant (bij de trapreling)
banen = [(25.1, 'zuid'), (23.1, 'noord'), (21.1, 'zuid'), (19.1, 'noord'), (17.1, 'zuid'), (15.1, 'noord')]
# onderste baan (24.12-26.5) loopt over het onderpad door: eerst naar het zuidelijke keerpunt van rail 10
for k, (rb, kant) in enumerate(banen):
    rz = zrij(rb)
    zuid = A_ZUID - math.degrees(1.1 / rb)
    noord = aS(rb) + math.degrees(1.1 / rb)
    if kant == 'zuid':
        a_start = math.degrees(math.atan2(route[-1][1] - CY, route[-1][0] - CX))
        for i in range(1, 7):                              # boog langs de baan naar het zuidelijke keerpunt
            route.append(pt(rb, a_start + (zuid - a_start) * i / 6, rz))
        if k + 1 < len(banen): route.append(pt(banen[k + 1][0], zuid, zrij(banen[k + 1][0])))
    else:
        steps = 6
        a0, a1 = A_ZUID - math.degrees(1.1 / rb), noord
        for i in range(1, steps + 1):                      # boog langs de baan naar het noordelijke keerpunt
            route.append(pt(rb, a0 + (a1 - a0) * i / steps, rz))
        if k + 1 < len(banen): route.append(pt(banen[k + 1][0], noord, zrij(banen[k + 1][0])))
    if kant == 'zuid' and k + 1 < len(banen):
        pass
# bovenste baan eindigt bij de trapkop (opening tussen bordeshek en rail 2), dan de tourniquets en het bordes
a_t = (aW(14.2) + aS(14.2)) / 2
route += [pt(15.0, aS(15.0) - 1.0, ztop(0)), pt(14.6, a_t, Z_I), pt(13.5, a_t, Z_I), pt(12.6, a_t + 4, Z_I), pt(12.4, 128.0, Z_I),
          pt(11.6, 131.71, Z_I), pt(9.6, 131.71, Z_I), pt(7.4, 131.71, Z_I)]   # gangetje in0 en de gondel op (laatste 2: alleen bij open hekjes)
json.dump(route, open(os.path.join(D, "exports", "bezoekersroute.json"), "w"))
print("[22] %d punten" % len(route))
