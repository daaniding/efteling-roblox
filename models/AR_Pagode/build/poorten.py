"""poorten: in- en uitstappoortjes van de Pagode (gedeeld door 03b_poorten, 10_station, 18_route en de Roblox-scripts).
Video fmEZsIkqsl8: instappen 0:48-0:56 via een gangetje van zwarte hekjes over het bordes naar een groen klaphekje in de
balustrade van de gondel; uitstappen 6:10-6:20 via zo'n hekje aan de oostkant naar de vlonder en de uitgangstrap (-20 graden).
Poortjes liggen MIDDEN tussen twee rode palen van de gondel (palen op (i + 0.5) / 22 * 360 graden in het gondelframe).
Gondelframe (Blender, hoek alfa) -> park: park = alfa - DRAAI, met DRAAI = 15.5615 (gondel staat in Roblox 164.4385 gedraaid).
De gondel draait elke rit precies een keer rond, dus beneden staan de poortjes altijd weer op dezelfde parkhoek."""
import math

DRAAI = 15.5615                 # alfa (gondel) = park + DRAAI
STAP = 360.0 / 22               # tussen twee palen
BREED = 1.7                     # vrije doorgang in m (echt ~1.2 m; Daan: looppaden minstens 2 m, poortje 1.7 voor de avatar van 1.27 m)
# (naam, gondelhoek alfa in graden, soort)
POORTEN = [("in0", 9 * STAP, "in"), ("in1", 10 * STAP, "in"), ("uit0", 0 * STAP, "uit"), ("uit1", -1 * STAP, "uit")]


def park(alfa): return alfa - DRAAI


def half_hoek(r, extra=0.0):
    """halve openingshoek (graden) op straal r voor een doorgang van BREED + extra meter."""
    return math.degrees((BREED + extra) / 2 / r)


def in_poort(park_hoek, r, extra=0.0):
    for _, alfa, _ in POORTEN:
        d = (park_hoek - park(alfa) + 180) % 360 - 180
        if abs(d) < half_hoek(r, extra): return True
    return False
