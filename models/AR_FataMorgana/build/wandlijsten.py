"""wandlijsten: gedeelde helper voor binnenwanden (Daan 18 nov: "de muren moeten veel gedetailleerder"): plint, groene
lambriseringslijst, pilasters, kroonlijst en een indirecte lichtlijst bovenin (zoals de gang op de video 2020). Wordt met exec
geladen door 05_ingang en 07_koepelgebouw; verwacht L en prisma in de globals."""


def wandlijsten(X0, Y0, X1, Y1, plafond, gaten=None, pil=2.4, geen_lambrisering=None):
    """binnenrechthoek X0..X1, Y0..Y1 (binnenkant muren); gaten = {"N": [(a, b)], "Z": .., "W": .., "O": ..} langs x (N/Z) of y (W/O)
    met (a, b, hoogte) voor deuropeningen; geen_lambrisering idem voor stukken achter kasten"""
    gaten = gaten or {}; geen = geen_lambrisering or {}
    def box(rol, x0, y0, x1, y1, z0, z1): prisma(rol, [L(x0, y0), L(x1, y0), L(x1, y1), L(x0, y1)], z0, z1)
    zijden = {"N": (X0, X1), "Z": (X0, X1), "W": (Y0, Y1), "O": (Y0, Y1)}
    def stukken(lo, hi, gs, z):
        uit, u = [], lo
        for g in sorted(gs):
            a, b = g[0], g[1]; h = g[2] if len(g) > 2 else 99
            if z > h: continue
            if a > u: uit.append((u, a))
            u = max(u, b)
        if hi > u: uit.append((u, hi))
        return uit
    def plaats(zijde, a, b, rol, z0, z1, d):
        if zijde == "N": box(rol, a, Y1 - d, b, Y1 + 0.01, z0, z1)
        elif zijde == "Z": box(rol, a, Y0 - 0.01, b, Y0 + d, z0, z1)
        elif zijde == "W": box(rol, X0 - 0.01, a, X0 + d, b, z0, z1)
        else: box(rol, X1 - d, a, X1 + 0.01, b, z0, z1)
    for zijde, (lo, hi) in zijden.items():
        gs = gaten.get(zijde, [])
        for (rol, z0, z1, d) in (("onderwand", 0.12, 0.28, 0.03), ("groen", 0.95, 1.0, 0.04),
                                 ("balmuur", plafond - 0.14, plafond - 0.04, 0.09), ("groen", plafond - 0.17, plafond - 0.14, 0.06),
                                 ("lichtlijst", plafond - 0.04, plafond - 0.01, 0.06)):
            for a, b in stukken(lo, hi, gs, (z0 + z1) / 2):
                if rol == "groen" and z0 < 1.1:
                    for a2, b2 in stukken(a, b, geen.get(zijde, []), 1.0): plaats(zijde, a2, b2, rol, z0, z1, d)
                else:
                    plaats(zijde, a, b, rol, z0, z1, d)
        # pilasters (niet in of naast deuren)
        n = max(1, round((hi - lo) / pil))
        for i in range(1, n):
            u = lo + (hi - lo) * i / n
            if any(g[0] - 0.4 < u < g[1] + 0.4 for g in gs) or any(g[0] - 0.2 < u < g[1] + 0.2 for g in geen.get(zijde, [])): continue
            plaats(zijde, u - 0.13, u + 0.13, "balmuur", 0.28, plafond - 0.17, 0.05)
            plaats(zijde, u - 0.17, u + 0.17, "balmuur", plafond - 0.4, plafond - 0.17, 0.075)
