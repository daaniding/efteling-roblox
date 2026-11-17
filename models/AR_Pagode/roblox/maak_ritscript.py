"""maak_ritscript: schrijft roblox/pagode_rit.luau (opzet van de rijdende Pagode in Studio).
- laadt voet, arm en gondel (exports via build/11_export.py, ids in exports/asset_ids.json) met dezelfde aankleding als plaats_pagode.luau
- workspace.Pagode = Model met Voet, Arm, Gondel, Cilinders, Station; AsFrame (CFrameValue, draaias stand omhoog)
- afwerking (afwerking_pagode.luau) in de gondel, behalve de bakreling en de lantaarnlichten (Station)
- gondel: alles verankerd, Kern = draaipunt; de beweging draait op de client (StarterPlayerScripts.PagodeRitClient,
  bron roblox/PagodeRitClient.client.luau), de server zet alleen de starttijd (ServerScriptService.PagodeRit)
Draai NA maak_plaatsscript.py (gebruikt de kop van plaats_pagode.luau). Gebruik: python3 roblox/maak_ritscript.py"""
import os, json

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(D, 'roblox')
info = json.load(open(os.path.join(D, 'exports', 'export_info.json')))
kop = open(os.path.join(R, 'plaats_pagode.luau')).read().split('\n')[:76]
assert kop[-1].strip() == 'end', 'kop van plaats_pagode.luau veranderd'
plaats = open(os.path.join(R, 'plaats_pagode.luau')).read()
import re
regel = next(r for r in plaats.split('\n') if r.startswith('gondel:PivotTo('))
PIV = regel[len('gondel:PivotTo('):-1]
AS = info['draaias_lokaal']
JL = (-(0 - AS[0]) * 3, (0 - AS[2]) * 3, 0.0)          # gondelmidden (Blender 0,0,0) t.o.v. de as, lokaal in stud


def L(b): return 'Vector3.new(%.4f, %.4f, %.4f)' % (-b[0] * 3, b[2] * 3, b[1] * 3)


afw = open(os.path.join(R, 'afwerking_pagode.luau')).read()
afw = afw.replace('local g = workspace:WaitForChild("Pagode")', 'local g = gondel')
afw = afw.replace('return "afwerking: " .. #map:GetChildren() .. " onderdelen"', '')
_r1 = 'deel("reling", CFrame.lookAt((p0 + p1) / 2, p1), Vector3.new(0.6, 1.3 * S, (p1 - p0).Magnitude + 0.3), ONZ)'
assert _r1 in afw
afw = afw.replace(_r1, 'deel(inpoort(math.deg(a0 + a1) / 2, 8.32) and "poortreling" or "reling", CFrame.lookAt((p0 + p1) / 2, p1), Vector3.new(0.6, 1.3 * S, (p1 - p0).Magnitude + 0.3), ONZ)')
afw = afw.replace('for i = 0, 63 do\n  local a0, a1 = i / 64 * 2 * math.pi, (i + 1) / 64 * 2 * math.pi', 'for i = 0, 255 do\n  local a0, a1 = i / 256 * 2 * math.pi, (i + 1) / 256 * 2 * math.pi')
afw = afw.replace('for i = 0, 71 do\n  local a0, a1 = math.rad(i * 5), math.rad(i * 5 + 5)\n  local m = (i * 5 + 2.5)', 'for i = 0, 287 do\n  local a0, a1 = math.rad(i * 1.25), math.rad(i * 1.25 + 1.25)\n  local m = (i * 1.25 + 0.625)')
assert 'i = 0, 255' in afw and 'i = 0, 287' in afw, 'fijne reling niet toegepast'
_r2 = 'deel("bakreling", CFrame.lookAt((p0 + p1) / 2, p1), Vector3.new(0.6, 1.1 * S, (p1 - p0).Magnitude + 0.3), ONZ)'
assert _r2 in afw
afw = afw.replace(_r2, 'deel(inpoort(m + DRAAI, 8.95) and "bakpoort" or "bakreling", CFrame.lookAt((p0 + p1) / 2, p1), Vector3.new(0.6, 1.1 * S, (p1 - p0).Magnitude + 0.3), ONZ)')
import sys as _sys; _sys.path.insert(0, os.path.join(D, 'build')); import poorten as PT
hek = json.load(open(os.path.join(D, 'exports', 'omgeving_hekken.json')))
cil = '\n'.join(
    f'''do local f = Instance.new("Folder"); f.Name = "Cil{k}"; f.Parent = cils
  f:SetAttribute("Voet", {L(c["voet"])}); f:SetAttribute("Kop", {L(c["kop"])})
  for _, d in ipairs({{{{"Huis", 0.72, Color3.fromRGB(228, 222, 206), Enum.Material.SmoothPlastic}}, {{"Stang", 0.34, Color3.fromRGB(205, 205, 210), Enum.Material.Metal}}}}) do
    local p = Instance.new("Part"); p.Name = d[1]; p.Shape = Enum.PartType.Cylinder; p.Anchored = true; p.CanCollide = false; p.CanTouch = false
    p.Size = Vector3.new(1, d[2] * S, d[2] * S); p.Color = d[3]; p.Material = d[4]; p.Parent = f
  end
end''' for k, c in enumerate(info['cilinders']))

bron = open(os.path.join(R, 'PagodeRit.server.luau')).read()
bronc = open(os.path.join(R, 'PagodeRitClient.client.luau')).read()
luau = '\n'.join(kop) + f'''

-- ===== rijdende Pagode: opzet (gegenereerd door roblox/maak_ritscript.py) =====
local PIV = {PIV}
local POORT_ALFA = {{{', '.join('%.4f' % p[1] for p in PT.POORTEN)}}}       -- poorten.py: gondelhoek alfa
local DRAAI, BREED_POORT = {PT.DRAAI}, {PT.BREED}
local HALF_POORT = math.deg((BREED_POORT + 0.1) / 2 / 8.3)
local function inpoort(alfa, r) local h = math.deg((BREED_POORT + 0.1) / 2 / r); for _, a in ipairs(POORT_ALFA) do if math.abs((alfa - a + 180) % 360 - 180) < h then return true end end; return false end
local HEKKEN = {{{', '.join('{%.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.2f}' % (h[0][0], h[0][1], h[0][2], h[1][0], h[1][1], h[1][2], h[2]) for h in hek)}}}
local oudS = game:GetService("ServerScriptService"):FindFirstChild("PagodeRit"); if oudS then oudS:Destroy() end
local oud = workspace:FindFirstChild("Pagode"); if oud then oud:Destroy() end
local pag = Instance.new("Model"); pag.Name = "Pagode"; pag.Parent = workspace
pag.ModelStreamingMode = Enum.ModelStreamingMode.Persistent       -- place streamt: anders mist de client delen van de gondel
local av = Instance.new("CFrameValue"); av.Name = "AsFrame"; av.Value = PIV; av.Parent = pag
pag:SetAttribute("GondelLokaal", Vector3.new({JL[0]:.4f}, {JL[1]:.4f}, {JL[2]:.4f}))
local function zet(id, naam) local m = laad(id, naam); aankleden(m, true); m:PivotTo(PIV); m.Parent = pag; return m end
local voet = zet(ID.AR_Pagode_voet, "Voet")
local arm = zet(ID.AR_Pagode_arm, "Arm")
local gondel = zet(ID.AR_Pagode_gondel, "Gondel")
for _, p in ipairs(arm:GetChildren()) do if p:IsA("BasePart") then p.CanCollide = false end end
-- afwerking (lampjes, lichtsnoeren, reling) in de gondel
do
{afw}
end
local station = Instance.new("Folder"); station.Name = "Station"; station.Parent = pag
for _, p in ipairs(gondel:GetDescendants()) do
  if p:IsA("BasePart") and (p.Name == "bakreling" or p.Name == "bakpoort" or p.Name == "lantaarnlicht") then p.Parent = station end
end
-- klaphekjes in de balustrade (poorten.py): twee bladen per poortje, scharnier aan de poortpaal, draaien naar binnen open
do
  local S = 3
  local PIVg = gondel:GetPivot()
  local function B(x, y, z) return PIVg * CFrame.new(-(x - 0.5) * S, (z + 38.6) * S, y * S) end
  local K0 = CFrame.new(PIV:PointToWorldSpace(pag:GetAttribute("GondelLokaal"))) * PIV.Rotation
  local map = Instance.new("Folder"); map.Name = "Poorten"; map.Parent = gondel
  local GROEN = Color3.fromRGB(22, 112, 86)
  for _, pa in ipairs(POORT_ALFA) do
    local a = math.rad(pa); local h = math.rad(HALF_POORT)
    local Cp = B(8.3 * math.cos(a), 8.3 * math.sin(a), 2.2 + 0.12).Position
    for _, sz in ipairs({{-1, 1}}) do
      local Hp = B(8.3 * math.cos(a + sz * h), 8.3 * math.sin(a + sz * h), 2.2 + 0.12).Position
      local hcf = CFrame.lookAt(Hp, Vector3.new(Cp.X, Hp.Y, Cp.Z))
      local blad = Instance.new("Folder"); blad.Name = "Blad"; blad.Parent = map
      blad:SetAttribute("Scharnier", K0:ToObjectSpace(hcf))
      local L = (BREED_POORT / 2) * S
      local function stuk(naam, c, size, zicht)
        local p = Instance.new("Part"); p.Name = naam; p.Anchored = true; p.Size = size; p.Color = GROEN; p.Material = Enum.Material.SmoothPlastic
        p.CanTouch = false; p.CastShadow = zicht; p.CanCollide = false; p.Transparency = zicht and 0 or 1; p.CanQuery = zicht
        p.CFrame = hcf * c; p:SetAttribute("Rel", c); p.Parent = blad; return p
      end
      stuk("regel", CFrame.new(0, 1.2 * S, -L / 2), Vector3.new(0.2, 0.2, L), true)
      stuk("regel", CFrame.new(0, 0.12 * S, -L / 2), Vector3.new(0.2, 0.2, L), true)
      stuk("stijl", CFrame.new(0, 0.66 * S, -L + 0.1), Vector3.new(0.2, 1.1 * S, 0.2), true)
      for k = 1, 5 do stuk("spijl", CFrame.new(0, 0.66 * S, -L * k / 6), Vector3.new(0.08, 1.05 * S, 0.08), true) end
      stuk("poortblad", CFrame.new(0, 0.66 * S, -L / 2), Vector3.new(0.4, 1.3 * S, L), false)
      -- naar binnen open: kies de draairichting waarbij het einde van het blad dichter bij het gondelmidden komt
      local eind0 = (hcf * CFrame.Angles(0, math.rad(80), 0) * CFrame.new(0, 0, -L)).Position
      local eind1 = (hcf * CFrame.Angles(0, math.rad(-80), 0) * CFrame.new(0, 0, -L)).Position
      local M = K0.Position
      blad:SetAttribute("Teken", ((eind0 - M) * Vector3.new(1, 0, 1)).Magnitude < ((eind1 - M) * Vector3.new(1, 0, 1)).Magnitude and 1 or -1)
    end
  end
end
-- onzichtbare botsing langs alle hekken en relingen (12_omgeving / 18_route -> exports/omgeving_hekken.json)
do
  local f = Instance.new("Folder"); f.Name = "Hekken"; f.Parent = pag
  for _, h in ipairs(HEKKEN) do
    local a = Vector3.new(h[1] * 3, 2 + h[3] * 3, -h[2] * 3); local b = Vector3.new(h[4] * 3, 2 + h[6] * 3, -h[5] * 3)
    local hoog = h[7] * 3 + 0.6
    local m = (a + b) / 2 + Vector3.new(0, hoog / 2, 0)
    local p = Instance.new("Part"); p.Name = "hekbotsing"; p.Anchored = true; p.Transparency = 1; p.CanCollide = true; p.CanQuery = false
    p.CanTouch = false; p.Size = Vector3.new(0.4, hoog, (b - a).Magnitude + 0.2)
    p.CFrame = CFrame.lookAt(m, m + Vector3.new(b.X - a.X, 0, b.Z - a.Z)) * CFrame.Angles(0, 0, 0); p.Parent = f
  end
end
-- hefcilinders (bewegen mee met de arm, zie PagodeRit)
local cils = Instance.new("Folder"); cils.Name = "Cilinders"; cils.Parent = pag
{cil}
-- gondel: alle delen verankerd; de client verplaatst ze (PagodeRitClient). Kern = draaipunt van de gondel.
local kern = Instance.new("Part"); kern.Name = "Kern"; kern.Size = Vector3.new(2, 2, 2); kern.Transparency = 1; kern.CanCollide = false
kern.CanQuery = false; kern.CanTouch = false; kern.Anchored = true
kern.CFrame = CFrame.new(PIV:PointToWorldSpace(pag:GetAttribute("GondelLokaal"))) * PIV.Rotation; kern.Parent = gondel
gondel.PrimaryPart = kern
-- ritscript
local sc = Instance.new("Script"); sc.Name = "PagodeRit"; sc.Source = [==[{bron}]==]; sc.Parent = game:GetService("ServerScriptService")
local sps = game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts")
local oudC = sps:FindFirstChild("PagodeRitClient"); if oudC then oudC:Destroy() end
local lc = Instance.new("LocalScript"); lc.Name = "PagodeRitClient"; lc.Source = [==[{bronc}]==]; lc.Parent = sps
local n = 0; for _, p in ipairs(gondel:GetDescendants()) do if p:IsA("BasePart") then n += 1 end end
return "Pagode rijklaar: gondel " .. n .. " delen, cilinders " .. #cils:GetChildren()
'''
open(os.path.join(R, 'pagode_rit.luau'), 'w').write(luau)
print('pagode_rit.luau', len(luau), 'tekens; PIV', PIV, 'JL', JL)
