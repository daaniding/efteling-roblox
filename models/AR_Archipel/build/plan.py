"""plan: plattegrond van de Archipel (watervariant 2022-2023) in parkmeters (x oost, y noord), overgetrokken van
ref/luchtfoto_2022 (droog voor de opening, beton en EPDM scherp) en ref/luchtfoto_2022/luchtfoto_2023 (met water).
Modelstelsel van alle build-scripts: meters t.o.v. OORSPRONG (park), z = 0 = waterpeil (gelijk aan de Sirocco: het bassin
loopt onder de wachtrijbrug door naar de Sirocco-vijver, lemma). Roblox: X = 3 * park_x, Z = -3 * park_y, Y = 0.35 + 3 z.
Geen spiegeling (tools/uitsnede.py is sinds 18 nov goed)."""
import math

OORSPRONG = (452.0, 160.0)

# kademuur: buitenrand van de betonnen bak (2022: grens beton / aarde; 2023: de bruine kantlijn)
KADE = [(446.3, 170.2), (449.0, 170.3), (452.0, 170.3), (455.2, 170.2), (456.8, 169.4), (458.4, 168.2), (459.1, 166.4),
        (459.8, 164.6), (460.6, 166.6), (461.3, 169.0), (461.0, 171.4), (461.8, 173.8), (462.4, 175.0),
        (465.5, 175.0), (465.4, 173.0), (466.2, 170.2), (467.3, 167.6), (467.2, 165.0), (466.6, 163.0),
        (467.1, 160.8), (467.2, 158.0), (466.6, 155.2), (465.3, 152.8), (463.5, 151.2), (461.0, 150.5), (458.0, 150.2),
        (456.4, 149.6), (454.0, 148.5), (452.0, 147.5), (450.0, 146.7), (448.0, 146.2), (445.5, 146.2), (444.2, 146.7),
        (443.6, 148.2), (443.3, 150.0), (442.4, 151.4), (441.0, 152.6), (439.9, 154.3), (439.4, 156.6), (439.5, 159.0),
        (440.0, 161.6), (441.0, 163.8), (442.6, 165.6), (444.3, 167.4), (445.4, 168.9)]

# waterlijn (2023): binnen deze lijn ligt de bodem onder water; daarbuiten droog strand op +0,1 m
WATER = [(446.8, 170.0), (449.0, 170.0), (452.0, 170.0), (454.9, 169.9), (454.9, 168.4), (454.3, 166.6), (454.7, 165.0),
         (456.6, 164.3), (459.4, 163.9), (460.3, 166.0), (461.0, 168.8), (460.6, 171.4), (461.6, 174.0), (462.3, 175.0),
         (465.4, 175.0), (465.1, 172.8), (465.9, 169.8), (466.6, 167.2), (466.3, 164.4), (466.2, 161.0), (466.1, 158.0),
         (465.3, 155.6), (463.8, 154.1), (461.6, 153.7), (459.6, 154.2), (458.0, 153.3), (456.0, 152.4), (454.0, 151.4),
         (452.0, 150.6), (449.8, 150.4), (447.4, 150.9), (445.4, 151.5), (443.4, 152.2), (441.4, 153.6), (440.7, 156.0),
         (440.7, 159.0), (441.3, 161.6), (442.7, 163.7), (444.3, 165.8), (445.6, 168.0)]

# diepe zone: turquoise EPDM rond de paalhutten (2022, blauwgroen) en de schotel van het wrak (2022, rond)
DIEP = [(450.0, 165.2), (451.4, 163.6), (452.0, 162.0), (452.5, 160.6), (453.3, 159.6), (455.0, 158.9), (455.6, 157.9),
        (455.0, 157.0), (453.5, 156.6), (453.2, 155.0), (453.6, 153.5), (453.0, 152.4), (451.5, 151.8), (450.0, 151.4),
        (448.5, 151.7), (447.4, 152.7), (445.6, 153.6), (444.6, 155.0), (444.4, 157.0), (444.8, 159.2), (445.6, 160.8),
        (446.2, 162.4), (446.8, 163.8), (447.8, 164.9)]
SCHOTEL = (462.6, 158.8, 2.9)          # middelpunt + straal van de ronde diepe kom bij het wrak (2022: 460-465,5 x 156-162)

DIEPTE_ONDIEP = 0.18                   # m water boven het beton (rand -> 1,2 m binnen de waterlijn)
DIEPTE_WATER = 0.30
DIEPTE_DIEP = 0.48                     # EPDM-zone: kniediep voor een kind (lemma: "dieper naar achteren")
Z_STRAND = 0.10                        # droog beton boven het waterpeil
Z_MAAIVELD = 0.20                      # aarde/plantvak buiten de kade (Roblox Y ~0,95 = Sirocco-gras)

# vijf vissershutten (lemma, doorsnede-paalvissers): middelpunt dak (2022); rot = draaiing van het lokale stelsel (graden),
# deur/gevelopening aan lokaal +y = (-sin rot, cos rot): -90 = deur naar het oosten (strand, Archipel-alle-huisjes.jpg)
HUTTEN = [
    dict(naam="hut1", c=(446.2, 148.2), rot=-60, palen=True, droog=True, spitsen=2, b=3.0, d=3.0, vloer=1.1, klimtouw=True),
    dict(naam="hut2", c=(450.8, 154.4), rot=-80, palen=True, spitsen=1, b=2.8, d=2.8, vloer=1.3, balkon=True, windvaan="zeeslang"),
    dict(naam="hut3", c=(443.6, 157.6), rot=-95, palen=True, spitsen=1, b=3.0, d=3.0, vloer=1.4, klimtouw=True),
    dict(naam="hut4", c=(448.2, 164.2), rot=-125, palen=True, spitsen=1, b=2.8, d=2.8, vloer=1.3, windvaan="monstervis"),
]
RONDE_HUT = dict(naam="hut5", c=(456.6, 166.6), r=1.75)     # op de grond, rieten kegel (2022: grijze cirkel 3,5 m)

# loopbruggen tussen de paalhutten (2022: donkere lijnen), via een vlonder in het midden
VLONDER_MIDDEN = (449.4, 158.8)
LOOPBRUGGEN = [((449.4, 158.8), (450.6, 155.9)), ((449.4, 158.8), (448.6, 162.6)), ((449.4, 158.8), (445.2, 157.9))]

# wrak (Archipel-boot.jpg, 2022: balk oost-west op y 158,5 van x 460,3 tot 465)
WRAK = dict(achtersteven=(460.6, 157.3, 15), voorsteven=(464.4, 160.4, -60), balk=((460.2, 158.7), (465.0, 158.4)),
            mast=(462.7, 159.0, 9.0))
PAALVISSER = (452.6, 160.4, 5.6)       # paal met figuur (Archipel_paalvisser.jpg), hoogte zitplank
KLIMPALEN = [(447.0, 161.4, 4.2), (451.6, 157.4, 3.8), (446.4, 155.2, 4.0)]
# vaste kisten en tonnen in het water (2022: rijtjes donkere blokjes langs het strand)
KISTEN = [(454.6, 163.2, 15), (455.4, 161.0, -10), (455.8, 159.6, 30), (456.2, 157.4, 5), (455.6, 155.6, -20),
          (454.4, 153.4, 40), (452.6, 152.6, 10), (457.6, 162.4, -35), (458.2, 160.6, 20), (457.8, 156.0, 0),
          (459.0, 154.8, 25), (457.0, 153.6, -15)]
TONNEN = [(456.8, 158.6), (453.8, 161.8), (458.6, 158.0), (454.0, 157.6)]      # 4 bubbelende tonnen (lemma)
SCHATKIST = (458.8, 162.6, -20)

# ingang (Archipel-na-ingang.jpg, 2022/2023: houten vlonder over de geul van de parkpaden zuidoost naar het strand)
INGANG_VLONDER = [(455.0, 146.0), (455.6, 148.4), (456.2, 150.6)]
INGANG_BREEDTE = 2.6


KANAAL_EIND_Y = 174.9                  # kade-randen met beide punten hierboven: open naar de Sirocco-vijver (geen kade/aarde)


def m(p):
    """park -> model"""
    return (p[0] - OORSPRONG[0], p[1] - OORSPRONG[1])


def binnen(x, y, P):
    c = False; j = len(P) - 1
    for i in range(len(P)):
        a, b = P[i], P[j]
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]: c = not c
        j = i
    return c


def afstand(x, y, P):
    d = 1e9; j = len(P) - 1
    for i in range(len(P)):
        ax, ay = P[j]; bx, by = P[i]; vx, vy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy + 1e-12)))
        d = min(d, math.hypot(x - ax - t * vx, y - ay - t * vy)); j = i
    return d


def glad(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def bodem(x, y):
    """bovenkant beton (park-coordinaten, z t.o.v. waterpeil); None buiten de kade"""
    if not binnen(x, y, KADE): return None
    if not binnen(x, y, WATER):
        return Z_STRAND
    dw = afstand(x, y, WATER)
    z = Z_STRAND - (Z_STRAND + DIEPTE_ONDIEP) * glad(dw / 0.9) - (DIEPTE_WATER - DIEPTE_ONDIEP) * glad((dw - 0.9) / 1.5)
    diep = 0.0
    if binnen(x, y, DIEP): diep = glad(afstand(x, y, DIEP) / 0.8)
    sx, sy, sr = SCHOTEL
    ds = math.hypot(x - sx, y - sy)
    if ds < sr: diep = max(diep, glad((sr - ds) / 0.8))
    return z - (DIEPTE_DIEP - DIEPTE_WATER) * diep


def is_epdm(x, y):
    sx, sy, sr = SCHOTEL
    return binnen(x, y, DIEP) or math.hypot(x - sx, y - sy) < sr
