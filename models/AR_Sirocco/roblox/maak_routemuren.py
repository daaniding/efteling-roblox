"""maak_routemuren: onzichtbare route-muren voor spelers langs de Sirocco (Daan 18 nov: "regel ook ff de barriers weer", zoals de
Routemuur van de Pagode): de relingen (1,15 m), het gaas en de brugmuurtjes zijn met een Roblox-sprong (7 studs) over te springen.
Muren staan precies op de hek- en relinglijnen uit build/07_omgeving.py en 04_decor.py (zelfde constanten), 14 studs hoog,
groep Routemuur (bezoekers lopen erdoorheen, spelers niet).
  - wachtrij: beide relingen (strookranden op +-B_RIJ/2), binnenrand open bij de instap-zijtak (-62 +- asin(1/9.25)),
    buitenrand aan het eind dicht; zijtak: twee relingen 9.2u+-tg -> 8.49u+-tg
  - dekhek r 8.55 behalve OPEN_INSTAP en OPEN_UITSTAP; gaashek r 7.25 behalve -62 en -106 (+-9 graden)
  - brugmuurtjes x = -2 +- 1.35 van de dekrand tot het plein
Schrijft roblox/sirocco_routemuren.luau (plakken in Studio, Edit). Gebruik: python3 roblox/maak_routemuren.py"""
import os, math

R = os.path.dirname(os.path.abspath(__file__))
B_RIJ = 2.0
WACHTRIJ = [(5.8, -15.8), (8.0, -13.9), (11.0, -11.9), (13.8, -9.6), (15.6, -6.5), (15.9, -2.0), (15.9, 3.0), (15.75, 6.0)]
for a in range(0, 181, 20):
    WACHTRIJ.append((12.0 + 3.75 * math.cos(math.radians(a)), 8.0 + 3.75 * math.sin(math.radians(a))))
I_BOOG = len(WACHTRIJ)
for k in range(13):
    a = 30 - k * 100 / 12
    WACHTRIJ.append((10.25 * math.cos(math.radians(a)), 10.25 * math.sin(math.radians(a))))
DEK_HEK_R = 8.55
OPEN_INSTAP = (-62 - math.degrees(math.asin(1.0 / DEK_HEK_R)), -62 + math.degrees(math.asin(1.0 / DEK_HEK_R)))
OPEN_UITSTAP = (-math.degrees(math.acos(-3.35 / DEK_HEK_R)), -math.degrees(math.acos(-0.65 / DEK_HEK_R)))
UITGANG_X = -2.0


def randen(pts, breedte):
    """zelfde als 07_omgeving.strook: links/rechts op +-breedte/2"""
    L, Rr = [], []
    for i, (x, y) in enumerate(pts):
        p = (x, y)
        d0 = (x - pts[i - 1][0], y - pts[i - 1][1]) if i > 0 else (pts[1][0] - x, pts[1][1] - y)
        d1 = (pts[i + 1][0] - x, pts[i + 1][1] - y) if i < len(pts) - 1 else d0
        n0 = math.hypot(*d0); n1 = math.hypot(*d1)
        t = (d0[0] / n0 + d1[0] / n1, d0[1] / n0 + d1[1] / n1); nt = math.hypot(*t); t = (t[0] / nt, t[1] / nt)
        n = (-t[1], t[0])
        L.append((x + n[0] * breedte / 2, y + n[1] * breedte / 2)); Rr.append((x - n[0] * breedte / 2, y - n[1] * breedte / 2))
    return L, Rr


def pol(r, a): return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))


def boog(r, a0, a1, stap=5.0):
    n = max(1, int(abs(a1 - a0) / stap + 0.999))
    return [pol(r, a0 + (a1 - a0) * k / n) for k in range(n + 1)]


lijnen = []                                          # polylijnen in modelmeters
links, rechts = randen(WACHTRIJ, B_RIJ)
mid = I_BOOG + 6
binnen, buiten = (links, rechts) if math.hypot(*links[mid]) < math.hypot(*rechts[mid]) else (rechts, links)
h_open = math.degrees(math.asin(1.0 / 9.25))
hk = [30 - k * 100 / 12 for k in range(13)]
lijnen.append(binnen[:I_BOOG] + [pol(9.25, a) for a in hk if a > -62 + h_open] + [pol(9.25, -62 + h_open)])
lijnen.append([pol(9.25, -62 - h_open)] + [pol(9.25, a) for a in hk if a < -62 - h_open])
lijnen.append(buiten + [binnen[-1]])                 # buitenrand + dicht eind
u = (math.cos(math.radians(-62)), math.sin(math.radians(-62))); tg = (-u[1], u[0])
for zij in (-1, 1):
    lijnen.append([(9.2 * u[0] + zij * tg[0], 9.2 * u[1] + zij * tg[1]), (8.49 * u[0] + zij * tg[0], 8.49 * u[1] + zij * tg[1])])
# dekhek: van de instapopening tegen de klok in naar de uitstapopening en verder rond
i0, i1 = OPEN_INSTAP; u0, u1 = OPEN_UITSTAP        # u0 < u1 < i0 < i1 (graden, -180..180)
lijnen.append(boog(DEK_HEK_R, i1, u0 + 360))        # -55 .. 245 (= -115): de lange kant
lijnen.append(boog(DEK_HEK_R, u1, i0))              # -97 .. -69: tussen uitstap en instap (hutje)
# gaashek om de draaischijf
lijnen.append(boog(7.25, -62 + 9, -106 + 360 - 9))
lijnen.append(boog(7.25, -106 + 9, -62 - 9))
# brugmuurtjes
for zij in (-1, 1):
    x = UITGANG_X + zij * 1.35
    lijnen.append([(x, -math.sqrt(DEK_HEK_R ** 2 - x ** 2)), (x, -17.3)])

# plafond onder de zeilkap (Daan 18 nov: "zorg dat ik niet door het blauwe heen kan klimmen"): over het overdekte deel van de
# rij (07_omgeving: zeilkap over WACHTRIJ[ZEIL_VANAF:-2], doek op 2,55-2,75 m), 2,3 m boven de vlonder, net breder dan de baan
ZEIL_VANAF = 7
dak = []
for a, b in zip(WACHTRIJ[ZEIL_VANAF:], WACHTRIJ[ZEIL_VANAF + 1:]):
    dak.append((a[0], a[1], b[0], b[1]))
seg = []
for l in lijnen:
    for a, b in zip(l, l[1:]):
        if math.hypot(b[0] - a[0], b[1] - a[1]) > 0.02: seg.append((a[0], a[1], b[0], b[1]))
rijen = ',\n'.join('\t{%.3f, %.3f, %.3f, %.3f}' % s for s in seg)
dakrijen = ',\n'.join('\t{%.3f, %.3f, %.3f, %.3f}' % s for s in dak)
# oevermuren (Daan 18 nov: "barieres bij het water, niemand mag het water in"): langs de hele vijverrand (omgeving_info "vijver"),
# open waar de wachtrij (binnen 1,05 m van de middellijn = de relinglijn) en de uitgangsbrug over het water gaan;
# exports/oevermuren.json (berekend met dezelfde regels, zie STATUS)
import json as _json
oever = _json.load(open(os.path.join(os.path.dirname(R), 'exports', 'oevermuren.json')))
oeverrijen = ',\n'.join('\t{%.3f, %.3f, %.3f, %.3f}' % tuple(s) for s in oever)
luau = f'''-- sirocco_routemuren (gemaakt door roblox/maak_routemuren.py): onzichtbare route-muren voor spelers (groep Routemuur; bezoekers
-- lopen erdoor). {len(seg)} stukken in modelmeters (x0, y0, x1, y1); 14 studs hoog vanaf het dek.
local S = 3
local MIDDEN = Vector3.new(456.5 * S, 0.2, -191.2 * S)
local Y0, H, DIK = MIDDEN.Y + 0.25 * S, 14, 0.6
local SEG = {{
{rijen}
}}
local PS = game:GetService("PhysicsService")
for _, g in {{"Routemuur", "Bezoekers"}} do if not PS:IsCollisionGroupRegistered(g) then PS:RegisterCollisionGroup(g) end end
PS:CollisionGroupSetCollidable("Bezoekers", "Routemuur", false)
local sir = workspace:WaitForChild("Sirocco")
local oud = sir:FindFirstChild("Routemuren"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "Routemuren"; map.Parent = sir
for i, s in SEG do
	local a = MIDDEN + Vector3.new(s[1] * S, 0, -s[2] * S)
	local b = MIDDEN + Vector3.new(s[3] * S, 0, -s[4] * S)
	local L = (b - a).Magnitude
	local p = Instance.new("Part"); p.Name = "routemuur"
	p.Size = Vector3.new(DIK, H, L + DIK)
	p.CFrame = CFrame.lookAt((a + b) / 2, b) + Vector3.new(0, Y0 + H / 2 - MIDDEN.Y, 0)
	p.Anchored = true; p.CanCollide = true; p.CanQuery = false; p.CanTouch = false; p.Transparency = 1; p.CastShadow = false
	p.CollisionGroup = "Routemuur"; p.Parent = map
end
-- plafond onder de zeilkap: niet bovenop de zeilkap klimmen (via schoren en balken) en dan over de muren
local DAK = {{
{dakrijen}
}}
for _, s in DAK do
	local a = MIDDEN + Vector3.new(s[1] * S, 0, -s[2] * S)
	local b = MIDDEN + Vector3.new(s[3] * S, 0, -s[4] * S)
	local p = Instance.new("Part"); p.Name = "plafond"
	p.Size = Vector3.new(2.7 * S, 0.4, (b - a).Magnitude + 1.2)
	p.CFrame = CFrame.lookAt((a + b) / 2, b) + Vector3.new(0, Y0 + 2.3 * S - MIDDEN.Y, 0)
	p.Anchored = true; p.CanCollide = true; p.CanQuery = false; p.CanTouch = false; p.Transparency = 1; p.CastShadow = false
	p.CollisionGroup = "Routemuur"; p.Parent = map
end
-- oevermuren: niemand het water in (vanaf waterpeil 14 studs hoog)
local OEVER = {{
{oeverrijen}
}}
for _, s in OEVER do
	local a = MIDDEN + Vector3.new(s[1] * S, 0, -s[2] * S)
	local b = MIDDEN + Vector3.new(s[3] * S, 0, -s[4] * S)
	local p = Instance.new("Part"); p.Name = "oever"
	p.Size = Vector3.new(DIK, H, (b - a).Magnitude + DIK)
	p.CFrame = CFrame.lookAt((a + b) / 2, b) + Vector3.new(0, H / 2, 0)
	p.Anchored = true; p.CanCollide = true; p.CanQuery = false; p.CanTouch = false; p.Transparency = 1; p.CastShadow = false
	p.CollisionGroup = "Routemuur"; p.Parent = map
end
-- eenrichting bij de uitgang: schot dwars over de deuropening (y -8,6), standaard open; SiroccoRitClient zet het dicht voor wie
-- op de brug staat (een opengeslagen deur staat tegen de muur en houdt niemand tegen)
local a, b = MIDDEN + Vector3.new(-3.2 * S, 0, 8.6 * S), MIDDEN + Vector3.new(-0.8 * S, 0, 8.6 * S)
local e = Instance.new("Part"); e.Name = "eenrichting_uit"; e.Size = Vector3.new(DIK, H, (b - a).Magnitude)
e.CFrame = CFrame.lookAt((a + b) / 2, b) + Vector3.new(0, Y0 + H / 2 - MIDDEN.Y, 0)
e.Anchored = true; e.CanCollide = false; e.CanQuery = false; e.CanTouch = false; e.Transparency = 1; e.CastShadow = false
e.CollisionGroup = "Routemuur"; e.Parent = map
return "routemuren: " .. #map:GetChildren()
'''
open(os.path.join(R, 'sirocco_routemuren.luau'), 'w').write(luau)
print('[maak_routemuren]', len(seg), 'stukken')
