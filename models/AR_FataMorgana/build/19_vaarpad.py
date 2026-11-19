"""19_vaarpad: het vaarpad van de sloepen (Daan 19 nov: "zorg nu ook echt even dat de boten varen dan kan ik de route checken").
Gesloten lus in modelmeters, daarna Roblox-studs (X = 3x, Z = -3y):
  1. de route-middellijn (rode stippels van de Eftepedia-plattegrond, ref/route_plan.npz, van de westdoorvaart van de hal
     tot de doorvaart hal-zuidwest)
  2. de hal in door de zuidwestdoorvaart, naar de ring om de draaischijf (r 8,65 rond C0)
  3. tegen de klok in om de schijf: zuid, langs de instap aan de oostkant, noord
  4. via het noordkanaal naar de westdoorvaart van de hal (-4; -326,5) en terug de route in
Glad gemaakt (cirkelgemiddelde over ~4 m) en elke 1 m herbemonsterd. Schrijft roblox/FataMorganaVaart.server.luau (punten ingevuld
in het sjabloon roblox/vaart_sjabloon.luau). Gebruik: python3 build/19_vaarpad.py"""
import os, math
import numpy as np

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C0, RB = np.array([6.3, -335.8]), 8.65


def ring(a0, a1, n):
    a = np.radians(np.linspace(a0, a1, n)); return C0 + RB * np.c_[np.cos(a), np.sin(a)]


route = np.load(os.path.join(D, "ref", "route_plan.npz"))["middellijn"]
# 18p begint de stippels bij (-2; -322) en loopt eerst de verkeerde kant op: stippels 0..15 zijn de bocht vanaf de westdoorvaart
# van de hal (-4; -326,5) naar het noorden; die omdraaien, dan loopt alles in vaarvolgorde
route = np.vstack([[[-4.6, -326.5], [-5.4, -326.45]], route[13::-1], route[16:]])   # recht door de grot tot x -5,7
lus = np.vstack([
    route,
    [[-2.0, -344.5], [0.5, -344.6]],          # zuidwestdoorvaart de hal in
    ring(-112, 98, 60),                        # tegen de klok in om de schijf (instap oost)
    [[1.0, -326.6], [-2.0, -326.5], [-3.0, -326.5]],   # noordkanaal naar de westdoorvaart, recht door het gordijn en de grot (1a/1b)
])


def herbemonster(p, stap):
    q = np.vstack([p, p[:1]]); s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(q, axis=0).T))])
    t = np.arange(0, s[-1], stap); return np.c_[np.interp(t, s, q[:, 0]), np.interp(t, s, q[:, 1])]


p = herbemonster(lus, 0.25)
k = 9                                           # ~2 m venster, 2x (19 nov: met 4 m sneed de haarspeldbocht na de grot (1b) zo af dat de sloep in de grot al draaide)
for _ in range(2):
    p = np.mean([np.roll(p, i, axis=0) for i in range(-(k // 2), k // 2 + 1)], axis=0)
p = herbemonster(p, 1.0)
lengte = len(p)
print("[19_vaarpad] lus %d m" % lengte)

pts = ",".join("%.2f,%.2f" % (3 * x, -3 * y) for x, y in p)
sj = open(os.path.join(D, "roblox", "vaart_sjabloon.luau")).read()
open(os.path.join(D, "roblox", "FataMorganaVaart.server.luau"), "w").write(sj.replace("--[[PUNTEN]]", pts).replace("--[[LENGTE]]", str(lengte)))
