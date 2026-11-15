"""Gedeelde omrekeningen voor het hele park.

Parkmeters: x = oost, y = noord, oorsprong 51.6500 N / 5.0455 E (zelfde vlakke projectie als reference/data/build_maps.py).
Roblox studs: X = x*3, Z = -y*3.  RD = Rijksdriehoek (EPSG:28992), benaderingsformule (< 1 m fout).
"""
import math

LAT0, LON0 = 51.6500, 5.0455
KX = 111320 * math.cos(math.radians(LAT0))
KY = 110574
STUDS = 3.0


def wgs_to_rd(lat, lon):
    dphi = 0.36 * (lat - 52.15517440); dlam = 0.36 * (lon - 5.38720621)
    Rp = [(0, 1, 190094.945), (1, 1, -11832.228), (2, 1, -114.221), (0, 3, -32.391), (1, 0, -0.705), (3, 1, -2.340),
          (1, 3, -0.608), (0, 2, -0.008), (2, 3, 0.148)]
    Sp = [(1, 0, 309056.544), (0, 2, 3638.893), (2, 0, 73.077), (1, 2, -157.984), (3, 0, 59.788), (0, 1, 0.433),
          (2, 2, -6.439), (1, 1, -0.032), (0, 4, 0.092), (1, 4, -0.054)]
    return (155000 + sum(c * dphi ** p * dlam ** q for p, q, c in Rp),
            463000 + sum(c * dphi ** p * dlam ** q for p, q, c in Sp))


def park_to_wgs(x, y):
    return LAT0 + y / KY, LON0 + x / KX


def wgs_to_park(lat, lon):
    return (lon - LON0) * KX, (lat - LAT0) * KY


def park_to_rd(x, y):
    return wgs_to_rd(*park_to_wgs(x, y))


def rd_to_park(rx, ry, it=6):
    """Omgekeerd via Newton op de (bijna lineaire) afbeelding park -> RD."""
    x, y = rx - 131351.6, ry - 406851.6
    for _ in range(it):
        ex, ey = park_to_rd(x, y)
        x += rx - ex; y += ry - ey
    return x, y


def park_to_studs(x, y):
    return x * STUDS, -y * STUDS


def studs_to_park(X, Z):
    return X / STUDS, -Z / STUDS
