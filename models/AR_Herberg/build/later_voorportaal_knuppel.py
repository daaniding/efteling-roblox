# CONCEPT (niet gebruikt): voorportaal met Knuppel uit de zak voor het latere interieur. Hoort in build() van 03_forms.py v\u00f3\u00f3r de botsing;
# daarna de hal met een boolean (EXACT) uit muren/dak/gevel snijden en de deur-venster weghalen. Bronnen: ref/Knuppelenzak, Herbergfris2-3, Knuppeltje, KnuppelVerbeterd.
    # ================= VOORPORTAAL met de knuppel (lemma: "voorvertrek waar de magische knuppel hangt"; foto's Knuppelenzak,
    #                   Herbergfris2 (wand met kooi tussen 2 lampen, geel-groen raam, balkenplafond), Herbergfris3 (doorkijk gelagkamer met hekje)) =====
    HX0, HX1, HY0, HY1, HZ = 0.3, 4.2, 0.0, 3.0, 2.45         # binnenmaten hal (inferred binnen de BAG-voet, x 0..4.25 / y 0..6.1)
    RX0, RX1, RY1 = 0.75, 2.65, 4.3                            # doorkijk-nis naar de gelagkamer achter de achterwand
    # vloer: rode plavuizen 0.3 m met voeg (Herbergfris3)
    put("hal", "voeg", bz(HX0 - 0.02, HX1 + 0.02, GY - 0.36, HY1, -0.06, 0.0)); put("hal", "voeg", bz(RX0, RX1, HY1 - 0.05, RY1, -0.06, 0.0))
    yy = GY - 0.35
    while yy < RY1 - 0.05:
        xx = HX0 if yy < HY1 else RX0
        while xx < (HX1 if yy < HY1 else RX1) - 0.05:
            put("hal", "tegels", bz(xx + 0.008, min(xx + 0.3, HX1 if yy < HY1 else RX1) - 0.008, yy + 0.008, yy + 0.292, -0.02, 0.012 + RNG.uniform(-0.004, 0.004)))
            xx += 0.3
        yy += 0.3
    # plafond: donkere planken + zware balken dwars op korbelen (Herbergfris2)
    put("hal", "hout", bz(HX0 - 0.05, HX1 + 0.05, GY - 0.3, RY1 + 0.05, HZ, HZ + 0.07))
    for yb in (0.35, 1.15, 1.95, 2.75):
        put("hal", "hout", organisch(bz(HX0 - 0.02, HX1 + 0.02, yb - 0.11, yb + 0.11, HZ - 0.24, HZ + 0.01), 0.025, 3, 0.5, 0.012, 3.0, 0.4))
        for xw, s_ in ((HX0, 1), (HX1, -1)):
            kb = merge(bz(min(xw, xw + s_ * 0.3), max(xw, xw + s_ * 0.3), yb - 0.08, yb + 0.08, HZ - 0.36, HZ - 0.24),
                       bz(min(xw, xw + s_ * 0.14), max(xw, xw + s_ * 0.14), yb - 0.08, yb + 0.08, HZ - 0.6, HZ - 0.36))
            put("hal", "hout", organisch(kb, 0.02, 3, 0.5, 0.0))
    # ---- linkerwand (x = HX0, kijkt +x): geel-groen raam met diepe bank, plank met doek, kapstok/pannenrek, ketel, vaten (Herbergfris2) ----
    WY0, WY1, WZ0, WZ1 = 0.75, 1.45, 0.95, 2.05
    put("hal", "glasgeel", bz(HX0 - 0.04, HX0 + 0.01, WY0, WY1, WZ0, WZ1))
    for (a0, a1, b0, b1) in ((WY0 - 0.08, WY0, WZ0 - 0.08, WZ1 + 0.08), (WY1, WY1 + 0.08, WZ0 - 0.08, WZ1 + 0.08), (WY0, WY1, WZ0 - 0.08, WZ0), (WY0, WY1, WZ1, WZ1 + 0.08)):
        put("hal", "hout", bz(HX0, HX0 + 0.06, a0, a1, b0, b1))
    put("hal", "hout", bz(HX0, HX0 + 0.04, (WY0 + WY1) / 2 - 0.015, (WY0 + WY1) / 2 + 0.015, WZ0, WZ1))
    for k in range(1, 5): zz = WZ0 + (WZ1 - WZ0) * k / 5; put("hal", "hout", bz(HX0, HX0 + 0.04, WY0, WY1, zz - 0.013, zz + 0.013))
    put("hal", "natuursteen", bz(HX0, HX0 + 0.22, WY0 - 0.12, WY1 + 0.12, WZ0 - 0.16, WZ0 - 0.08, 0.01))
    put("hal", "hout", organisch(bz(HX0 - 0.02, HX0 + 0.28, 0.15, 2.3, 2.02, 2.16), 0.025, 3, 0.5, 0.01, 3.0, 0.4))         # balk/plank boven het raam
    put("hal", "doek", organisch(merge(ell((HX0 + 0.18, 0.55, 2.2), (0.12, 0.22, 0.06), 16, 8), ell((HX0 + 0.27, 0.62, 2.07), (0.05, 0.16, 0.12), 12, 8)), 0.02, 6, 0.6, 0.012, 5.0, 0.35))
    put("hal", "hout", bz(HX0, HX0 + 0.05, 1.6, 2.55, 1.72, 1.8))                                                               # kapstok met pinnen
    for k in range(6): yk = 1.67 + k * 0.16; put("hal", "hout", btube([(HX0 + 0.05, yk, 1.76), (HX0 + 0.17, yk, 1.79)], 0.014, 6))
    put("hal", "koper", blathe([(0, 0), (0.08, 0.005), (0.13, 0.06), (0.14, 0.13), (0.11, 0.2), (0.06, 0.22), (0.07, 0.25), (0, 0.25)], 16), TR(HX0 + 0.2, 2.1, 1.47))
    put("hal", "ijzer", btube([(HX0 + 0.2, 1.98, 1.69), (HX0 + 0.2, 2.1, 1.82), (HX0 + 0.2, 2.22, 1.69)], 0.008, 5))
    put("hal", "ijzer", btube([(HX0 + 0.2, 2.1, 1.82), (HX0 + 0.2, 2.1, 2.02)], 0.006, 4))
    put("hal", "koper", btube([(HX0 + 0.33, 2.03, 1.6), (HX0 + 0.45, 1.98, 1.58)], 0.012, 6))                                    # tuit
    for (yv, s_) in ((0.95, 0.55), (1.45, 0.5)):
        put("hal", "vat", blathe([(0, 0), (0.33 * s_, 0), (0.39 * s_, 0.24 * s_), (0.41 * s_, 0.47 * s_), (0.39 * s_, 0.7 * s_), (0.33 * s_, 0.94 * s_), (0, 0.94 * s_)], 16), TR(HX0 + 0.3, yv))
        for zz in (0.1, 0.33, 0.6, 0.83): put("hal", "ijzer", blathe([(0.355 * s_ + 0.06 * math.sin(zz * math.pi / 0.94) * s_, zz * s_ - 0.02), (0.37 * s_ + 0.06 * math.sin(zz * math.pi / 0.94) * s_, zz * s_), (0.355 * s_ + 0.06 * math.sin(zz * math.pi / 0.94) * s_, zz * s_ + 0.02)], 16), TR(HX0 + 0.3, yv))
        coll_box(HX0 + 0.3, yv, 0.26 * s_ / 0.55, 0.45 * s_ / 0.55, 0.45 * s_ / 0.55, 0.52 * s_ / 0.55)
    # ---- rechterwand (x = HX1, kijkt -x): lamp, KNUPPEL IN KOOI, lamp, deur met ruitjes (Knuppelenzak) ----
    def wand(y, d=0.0):   # lokaal: x = langs de wand (= wereld y), y = de kamer in (= wereld -x), z = hoogte
        return Matrix.Translation((HX1 - d, y, 0)) @ Matrix.Rotation(math.radians(90), 4, "Z")
    KY = 1.05
    for ly in (KY - 0.62, KY + 0.62):                                                                  # wandlampen: kom + kooiglas met oranje gloed
        M_ = wand(ly)
        put("hal", "ijzer", bz(-0.07, 0.07, 0.0, 0.03, 1.55, 1.75), M_)
        put("hal", "ijzer", btube([(0, 0.02, 1.62), (0, 0.13, 1.6)], 0.012, 5), M_)
        put("hal", "ijzer", blathe([(0, 1.5), (0.04, 1.5), (0.12, 1.56), (0.15, 1.63), (0.15, 1.66), (0, 1.66)], 14), M_ @ Matrix.Translation((0, 0.16, 0)))
        put("hal", "glaslamp", blathe([(0, 1.64), (0.1, 1.64), (0.1, 1.75), (0.07, 1.81), (0, 1.83)], 14), M_ @ Matrix.Translation((0, 0.16, 0)))
        for k in range(6):
            a = k * math.tau / 6; c_, s_ = math.cos(a), math.sin(a)
            put("hal", "ijzer", btube([(0.105 * c_, 0.16 + 0.105 * s_, 1.65), (0.105 * c_, 0.16 + 0.105 * s_, 1.75), (0.075 * c_, 0.16 + 0.075 * s_, 1.81), (0, 0.16, 1.84)], 0.006, 4), M_)
        LAMPS_.append([round(HX1 - 0.16, 2), round(ly, 2), 1.72])
    # achterbord: doodskistvorm met ronde kop (0.62 breed, onder 0.36), donker eiken met ijzeren randbeslag
    bord_pts = [(-0.18, 0.72)] + [(0.31 * math.cos(math.radians(a)), 2.06 + 0.31 * math.sin(math.radians(a))) for a in range(0, 181, 12)][::-1][::-1]
    bord_pts = [(0.18, 0.72)] + [(0.31 * math.cos(math.radians(a)), 2.06 + 0.31 * math.sin(math.radians(a))) for a in range(0, 181, 12)] + [(-0.18, 0.72)]
    put("hal", "hout", boutline(bord_pts, 0.0, 0.07), wand(KY) @ Matrix.Rotation(0, 4, "Z"))
    def bw(z):  # halve breedte van het bord op hoogte z
        return 0.31 if z >= 2.06 else 0.18 + (0.31 - 0.18) * (z - 0.72) / (2.06 - 0.72)
    # kooi: 5 gebogen staven die van het bord naar voren bollen en over de kop samenkomen, 4 banden, hangsloten aan de zijkant
    for u in (-0.8, -0.4, 0.0, 0.4, 0.8):
        pts = []
        for i in range(15):
            z = 0.82 + (2.3 - 0.82) * i / 14; t = i / 14
            w = bw(min(z, 2.06)) * 0.82 * (1 if z <= 2.06 else math.sqrt(max(0.0, 1 - ((z - 2.06) / 0.27) ** 2)))
            pts.append((u * w, 0.07 + 0.12 * math.sin(math.pi * min(1, t * 1.05)) + 0.02, z))
        put("hal", "ijzer", btube(pts, 0.011, 5), wand(KY))
    for zb in (1.0, 1.38, 1.76, 2.06):
        w = bw(zb) * 0.82; dpt = 0.07 + 0.12 * math.sin(math.pi * (zb - 0.82) / 1.48) + 0.02
        put("hal", "ijzer", btube([(-w - 0.06, 0.06, zb), (-w, dpt, zb), (0, dpt + 0.01, zb), (w, dpt, zb), (w + 0.06, 0.06, zb)], 0.012, 5), wand(KY))
        for s_ in (-1, 1):                                                                               # hangslot aan elke band
            put("hal", "ijzer", bz(s_ * (w + 0.06) - 0.03, s_ * (w + 0.06) + 0.03, 0.05, 0.08, zb - 0.1, zb - 0.03), wand(KY))
            put("hal", "ijzer", btube([(s_ * (w + 0.06) - 0.02, 0.065, zb - 0.03), (s_ * (w + 0.06), 0.065, zb + 0.0), (s_ * (w + 0.06) + 0.02, 0.065, zb - 0.03)], 0.005, 4), wand(KY))
    for k in range(9):                                                                                   # ketting onder de kooi
        z = 0.78 - k * 0.07
        put("hal", "ijzer", ell((0, 0.09, z), (0.012 if k % 2 else 0.028, 0.028 if k % 2 else 0.012, 0.042), 8, 6), wand(KY))
    # DE KNUPPEL: brons, kop met gezicht (Knuppeltje: stekels op de kruin, grote blauwe ogen, lange neus, open mond met tanden), steel 1.2 m (KnuppelVerbeterd)
    KZ = 1.98
    kop = merge(ell((0, 0.09, KZ), (0.1, 0.095, 0.13), 20, 14),                          # schedel
                ell((0, 0.165, KZ + 0.03), (0.085, 0.035, 0.03), 14, 8),                 # wenkbrauwboog
                ell((-0.05, 0.155, KZ - 0.05), (0.04, 0.035, 0.04), 10, 8), ell((0.05, 0.155, KZ - 0.05), (0.04, 0.035, 0.04), 10, 8),   # wangen
                ell((0, 0.21, KZ - 0.02), (0.022, 0.065, 0.026), 12, 8),                 # lange neus
                ell((0, 0.255, KZ - 0.045), (0.018, 0.022, 0.02), 10, 6),                # neuspunt
                ell((0, 0.135, KZ - 0.135), (0.065, 0.06, 0.045), 14, 8),                # onderkaak
                ell((-0.1, 0.07, KZ + 0.0), (0.022, 0.025, 0.06), 8, 6), ell((0.1, 0.07, KZ + 0.0), (0.022, 0.025, 0.06), 8, 6),   # oren
                ell((0, 0.08, KZ - 0.2), (0.06, 0.06, 0.1), 12, 8))                      # hals naar de steel
    put("knuppel", "brons", organisch(kop, 0.009, 6, 0.6, 0.004, 25.0, 0.35), wand(KY))
    put("knuppel", "brons", blathe([(0, 0.88), (0.04, 0.88), (0.05, 0.92), (0.032, 0.96), (0.03, 1.3), (0.038, 1.6), (0.05, 1.75), (0.058, 1.85), (0, 1.86)], 14), wand(KY) @ Matrix.Translation((0, 0.08, 0)))
    for k in range(7):                                                                                   # stekels op de kruin
        a = math.radians(-70 + k * 23.3)
        put("knuppel", "brons", blathe([(0, 0), (0.016, 0), (0.0, 0.07)], 8), wand(KY) @ Matrix.Translation((0.075 * math.sin(a), 0.09 - 0.02 * math.cos(a), KZ + 0.11 + 0.02 * math.cos(a))) @ Matrix.Rotation(a, 4, "Y"))
    for s_ in (-1, 1):                                                                                   # ogen: wit, blauwe iris, pupil
        put("knuppel", "oogwit", ell((s_ * 0.042, 0.168, KZ - 0.005), (0.028, 0.02, 0.022), 12, 8), wand(KY))
        put("knuppel", "iris", ell((s_ * 0.042, 0.186, KZ - 0.005), (0.013, 0.005, 0.013), 10, 6), wand(KY))
        put("knuppel", "venster", ell((s_ * 0.042, 0.19, KZ - 0.005), (0.006, 0.003, 0.006), 8, 4), wand(KY))
    put("knuppel", "venster", ell((0, 0.17, KZ - 0.1), (0.045, 0.03, 0.022), 12, 6), wand(KY))     # open mond
    for k in range(6):
        xt = -0.035 + k * 0.014; put("knuppel", "tand", bz(xt - 0.005, xt + 0.005, 0.185, 0.193, KZ - 0.1, KZ - 0.08), wand(KY))
    # deur met ruitjes rechts van de kooi (bovenhelft 2x3 matte ruiten met licht erachter, onderhelft donkere planken)
    DY0, DY1 = 1.95, 2.7
    M_ = wand((DY0 + DY1) / 2)
    put("hal", "hout", bz(-0.42, 0.42, -0.02, 0.06, 0.0, 2.12), M_)
    put("hal", "deur", bz(-0.36, 0.36, 0.0, 0.07, 0.02, 0.98), M_)
    for k in range(6): xx = -0.3 + k * 0.12; put("hal", "deur", bz(xx - 0.004, xx + 0.004, 0.07, 0.075, 0.05, 0.95), M_)
    put("hal", "glasmat", bz(-0.3, 0.3, 0.0, 0.03, 1.05, 1.95), M_)
    put("hal", "hout", bz(-0.36, 0.36, 0.03, 0.08, 0.98, 1.06), M_); put("hal", "hout", bz(-0.36, 0.36, 0.03, 0.08, 1.94, 2.02), M_)
    for xx in (-0.33, 0.0, 0.33): put("hal", "hout", bz(xx - 0.03, xx + 0.03, 0.03, 0.08, 1.05, 1.95), M_)
    for zz in (1.35, 1.65): put("hal", "hout", bz(-0.3, 0.3, 0.03, 0.07, zz - 0.015, zz + 0.015), M_)
    for zz in (0.3, 1.7): put("hal", "ijzer", bz(0.22, 0.36, 0.07, 0.085, zz - 0.02, zz + 0.02), M_)
    put("hal", "ijzer", btube([(-0.3, 0.09, 1.05), (-0.3, 0.14, 1.05), (-0.22, 0.14, 1.05)], 0.01, 5), M_)    # klink
    # ---- achterwand (y = HY1): doorkijk naar de gelagkamer met open glasdeuren en spijlenhekje (Herbergfris3) ----
    for xp in (RX0 - 0.08, RX1 + 0.08): put("hal", "hout", organisch(bz(xp - 0.08, xp + 0.08, HY1 - 0.1, HY1 + 0.08, 0.0, 2.25), 0.025, 3, 0.5, 0.012, 3.0, 0.4))
    put("hal", "hout", organisch(bz(RX0 - 0.2, RX1 + 0.2, HY1 - 0.12, HY1 + 0.08, 2.1, 2.32), 0.025, 3, 0.5, 0.012, 3.0, 0.4))
    hek = bmesh.new()
    put("hal", "hout", bz(RX0, RX1, HY1 - 0.06, HY1 + 0.02, 0.88, 0.95, 0.01)); put("hal", "hout", bz(RX0, RX1, HY1 - 0.05, HY1 + 0.01, 0.08, 0.14))
    for k in range(10):
        xb = RX0 + 0.1 + k * (RX1 - RX0 - 0.2) / 9
        put("hal", "hout", blathe([(0, 0.14), (0.03, 0.14), (0.03, 0.22), (0.045, 0.3), (0.025, 0.42), (0.04, 0.6), (0.022, 0.78), (0.03, 0.88), (0, 0.88)], 8), TR(xb, HY1 - 0.02))
    coll_box((RX0 + RX1) / 2, HY1 + 0.02, 1.2, RX1 - RX0, 0.12, 2.4)                                  # niet over het hekje
    for (xh, sgn) in ((RX0, 1), (RX1, -1)):                                                           # open glasdeuren, 70 graden de hal in
        Md = TR(xh, HY1 - 0.05, 0, sgn * -70) if sgn > 0 else TR(xh, HY1 - 0.05, 0, 180 + 70)
        w_ = (RX1 - RX0) / 2 - 0.05
        for (a0, a1, b0, b1) in ((0, w_, 0.0, 0.1), (0, w_, 2.0, 2.08), (0, 0.07, 0.0, 2.08), (w_ - 0.07, w_, 0.0, 2.08), (0, w_, 0.9, 0.98)):
            put("hal", "hout", bz(a0, a1, -0.025, 0.025, b0, b1), Md)
        put("hal", "glasmat", bz(0.07, w_ - 0.07, -0.006, 0.006, 0.98, 2.0), Md)
        put("hal", "deur", bz(0.07, w_ - 0.07, -0.015, 0.015, 0.1, 0.9), Md)
        for k in range(1, 4): zz = 0.98 + 1.02 * k / 4; put("hal", "hout", bz(0.07, w_ - 0.07, -0.015, 0.015, zz - 0.012, zz + 0.012), Md)
        put("hal", "hout", bz(w_ / 2 - 0.012, w_ / 2 + 0.012, -0.015, 0.015, 0.98, 2.0), Md)
    # gelagkamer-doorkijk: warme lamp, tafel met kruik, bank, schoorsteenmantel (Herbergfris3/4)
    put("hal", "hout", bz(1.2, 2.2, 3.55, 4.05, 0.72, 0.78, 0.01))
    for (xl, yl) in ((1.28, 3.62), (2.12, 3.62), (1.28, 3.98), (2.12, 3.98)): put("hal", "hout", bz(xl - 0.03, xl + 0.03, yl - 0.03, yl + 0.03, 0.0, 0.72))
    put("hal", "aardewerk", blathe([(0, 0), (0.06, 0), (0.09, 0.07), (0.09, 0.13), (0.05, 0.19), (0.04, 0.23), (0, 0.23)], 12), TR(1.55, 3.8, 0.78))
    put("hal", "hout", bz(1.2, 2.2, 4.08, 4.25, 0.42, 0.47)); put("hal", "stuc", organisch(bz(RX0, RX0 + 0.5, 3.4, 4.3, 0.0, 2.2), 0.04, 6, 0.6, 0.03, 1.5, 0.3))
    for k in range(3): put("hal", "ijzer", bz(RX1 - 0.2, RX1 - 0.04, RY1 - 0.06, RY1, 1.55 + 0.0 * k, 1.7))
    put("hal", "glaslamp", blathe([(0, 0), (0.06, 0), (0.06, 0.14), (0, 0.16)], 8), TR(RX1 - 0.12, RY1 - 0.14, 1.6))
    LAMPS_.append([round(RX1 - 0.12, 2), round(RY1 - 0.14, 2), 1.7])
    # belkoord van het plafond (Herbergfris3) en de vitrine met de zak van de knuppel (lemma) in de hoek rechtsachter
    put("hal", "touw", btube([(1.05, 2.45, HZ - 0.24), (1.05, 2.45, 1.35)], 0.016, 6)); put("hal", "touw", organisch(ell((1.05, 2.45, 1.28), (0.035, 0.035, 0.09), 10, 8), 0.012, 4, 0.5, 0.008, 8.0))
    VX0, VX1, VY0, VY1 = 3.3, 4.12, 2.48, 2.95
    put("hal", "hout", organisch(bz(VX0, VX1, VY0, VY1, 0.0, 0.85), 0.02, 3, 0.5, 0.008, 4.0, 0.4)); put("hal", "hout", bz(VX0 - 0.03, VX1 + 0.03, VY0 - 0.03, VY1 + 0.02, 0.85, 0.9, 0.01))
    put("hal", "glas", bz(VX0 + 0.03, VX1 - 0.03, VY0 + 0.02, VY1 - 0.02, 0.9, 1.3))
    for (a0, a1, b0, b1) in ((VX0 + 0.02, VX0 + 0.05, VY0 + 0.01, VY0 + 0.04), (VX1 - 0.05, VX1 - 0.02, VY0 + 0.01, VY0 + 0.04), (VX0 + 0.02, VX0 + 0.05, VY1 - 0.04, VY1 - 0.01), (VX1 - 0.05, VX1 - 0.02, VY1 - 0.04, VY1 - 0.01)):
        put("hal", "hout", bz(a0, a1, b0, b1, 0.9, 1.3))
    put("hal", "hout", bz(VX0 + 0.02, VX1 - 0.02, VY0 + 0.01, VY1 - 0.01, 1.3, 1.33))
    put("hal", "doek", bz(VX0 + 0.05, VX1 - 0.05, VY0 + 0.04, VY1 - 0.04, 0.9, 0.93))                                      # kussen
    zb_ = bmesh.new(); bmesh.ops.create_uvsphere(zb_, u_segments=24, v_segments=12, radius=1.0, calc_uvs=True)
    for v in zb_.verts:
        x0, y0, z0 = v.co; v.co = Vector((x0 * 0.28, y0 * 0.13, max(z0, -0.35) * 0.09 + (0.02 * math.sin(x0 * 6) if z0 > 0 else 0)))
    bmesh.ops.translate(zb_, vec=((VX0 + VX1) / 2, (VY0 + VY1) / 2, 1.02), verts=zb_.verts)
    me = bpy.data.meshes.new("BAKE_zak"); zb_.to_mesh(me); zb_.free(); ob = bpy.data.objects.new("BAKE_zak", me); col("FORMS").objects.link(ob); own(ob)
    mt = bpy.data.materials.get("MAT_zaktex") or bpy.data.materials.new("MAT_zaktex"); ob.data.materials.append(mt)
    for p_ in ob.data.polygons: p_.use_smooth = True
    put("hal", "touw", btube([(VX0 + 0.62, (VY0 + VY1) / 2, 1.05), (VX0 + 0.68, (VY0 + VY1) / 2 - 0.05, 1.08), (VX0 + 0.7, (VY0 + VY1) / 2, 1.0)], 0.006, 5))
    coll_box((VX0 + VX1) / 2, (VY0 + VY1) / 2, 0.65, VX1 - VX0, VY1 - VY0, 1.3)
    # ---- botsing rond de hal (vervangt de dichte blokken van gevel en linkerdeel) ----
    coll_box(0.1, 2.875, 1.2, 0.4, 6.45, 2.4)                              # linkerwand
    coll_box(0.375, 4.55, 1.2, 0.75, 3.1, 2.4); coll_box(3.45, 4.55, 1.2, 1.6, 3.1, 2.4); coll_box(1.7, 5.2, 1.2, 1.9, 1.8, 2.4)   # achter de hal
    coll_box(4.85, 3.05, 1.2, 1.3, 6.1, 2.4)                               # rechterwand + middendeel-voor
    coll_box(0.555, GY / 2 - 0.02, 1.2, 1.11, -GY + 0.04, 2.4); coll_box(3.825, GY / 2 - 0.02, 1.2, 2.55, -GY + 0.04, 2.4)          # gevel naast de deur
    coll_box(1.83, GY / 2, 2.2, 1.44, -GY, 0.6)                             # boven de deur
    coll_box(2.25, 1.5, -0.05, 4.0, 4.0, 0.1)                               # vloer
