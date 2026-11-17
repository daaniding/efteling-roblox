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
stpoort = """-- klaphekjes in het stationshek (Daan 17 nov: "als de attractie omhoog is hoort niemand erdoor te kunnen; als hij er is gaan
-- er 2 hekjes open, die van de attractie en die van de wachtrij"): per poortje twee bladen op de poortpalen (r 9.05), draaien
-- naar buiten open (het gangetje / de vlonder in), tegelijk met de bladen van de gondel; vast in de wereld
do
  local S = 3
  local function W(r, a, nap) return Vector3.new((360 + r * math.cos(a)) * S, 2 + (nap - 10) * S, -(47.5 + r * math.sin(a)) * S) end
  local M = W(0, 0, 11.3)
  local PS = game:GetService("PhysicsService")
  for _, g in ipairs({"Routemuur", "Rijdend"}) do if not PS:IsCollisionGroupRegistered(g) then PS:RegisterCollisionGroup(g) end end
  PS:CollisionGroupSetCollidable("Routemuur", "Rijdend", false)
  -- onzichtbare botsing van bakrand en gondelbalustrade 24 studs hoog (niet de bak in springen, niet over de balustrade);
  -- bakrand in groep Routemuur (de gondel zwaait met meerijders laag over de bak), balustrade gewoon (houdt meerijders binnen)
  local station0 = pag:FindFirstChild("Station") or pag
  for _, p in ipairs(station0:GetDescendants()) do
    if p:IsA("BasePart") and (p.Name == "bakreling" or p.Name == "bakpoort") then
      local onder = p.CFrame * CFrame.new(0, -p.Size.Y / 2, 0); p.Size = Vector3.new(p.Size.X, 24, p.Size.Z); p.CFrame = onder * CFrame.new(0, 12, 0)
      p.CollisionGroup = "Routemuur"
    end
  end
  for _, p in ipairs(gondel:GetDescendants()) do
    if p:IsA("BasePart") and (p.Name == "reling" or p.Name == "poortreling") then
      local onder = p.CFrame * CFrame.new(0, -p.Size.Y / 2, 0); p.Size = Vector3.new(p.Size.X, 24, p.Size.Z); p.CFrame = onder * CFrame.new(0, 12, 0)
    end
  end
  -- gondel dicht (Daan 17 nov: "je kan door het midden en als je springt door het dak"): massieve kern en een plafond,
  -- onzichtbaar, bewegen mee (PagodeRitClient verplaatst alle delen van de gondel)
  do
    local K = gondel:FindFirstChild("Kern") and gondel.Kern.CFrame or (CFrame.new(PIV:PointToWorldSpace(pag:GetAttribute("GondelLokaal"))) * PIV.Rotation)
    for _, d in ipairs({{"kernbots", 16.4, 6.4, 24.0}, {"plafondbots", 26.5, 14.0, 14.8}}) do
      local oud = gondel:FindFirstChild(d[1]); if oud then oud:Destroy() end
      local p = Instance.new("Part"); p.Name = d[1]; p.Shape = Enum.PartType.Cylinder; p.Anchored = true; p.Transparency = 1
      p.CanCollide = true; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
      p.Size = Vector3.new(d[4] - d[3], d[2] * 2, d[2] * 2)
      p.CFrame = K * CFrame.new(0, (d[3] + d[4]) / 2, 0) * CFrame.Angles(0, 0, math.pi / 2); p.Parent = gondel
    end
  end
  -- eenrichting (Daan 17 nov: "zorg dat je niet via de ingang eruit kan"): schotten die de client alleen dichtzet als je er
  -- al voorbij bent (PagodeRitClient): tourniquets (r 13.5) en de kop van de uitgangstrap (r 10.95, -20 gr)
  do
    local oudE = pag:FindFirstChild("Eenrichting"); if oudE then oudE:Destroy() end
    local fe = Instance.new("Folder"); fe.Name = "Eenrichting"; fe.Parent = pag
    local a_t = 104.0 + math.deg(1.5 / 14.2) + math.deg(0.42 / 14.2) + math.deg(2.2 / 14.2) / 2
    local d = math.deg(0.93 / 13.5)
    local schotten = {
      {"tourniquet", W(13.5, math.rad(a_t - d), 11.3), W(13.5, math.rad(a_t + d), 11.3)},
      {"uitgang", W(10.95, math.rad(-20), 11.3) + Vector3.new(-math.sin(math.rad(-20)), 0, -math.cos(math.rad(-20))) * 1.45 * S,
                  W(10.95, math.rad(-20), 11.3) - Vector3.new(-math.sin(math.rad(-20)), 0, -math.cos(math.rad(-20))) * 1.45 * S},
    }
    for _, sc in ipairs(schotten) do
      local pa, pb = sc[2], sc[3]; local c = (pa + pb) / 2 + Vector3.new(0, 11.5, 0)
      local p = Instance.new("Part"); p.Name = sc[1]; p.Anchored = true; p.Transparency = 1; p.CanCollide = false; p.CanQuery = false
      p.CanTouch = false; p.Size = Vector3.new(0.4, 24, (pb - pa).Magnitude)
      p.CFrame = CFrame.lookAt(c, c + Vector3.new(pb.X - pa.X, 0, pb.Z - pa.Z)); p.Parent = fe
    end
  end
  -- geluid (Daan 17 nov: "het geluid uit boxen, zodat je het aan de andere kant van het park niet meer hoort"): alles
  -- ruimtelijk (InverseTapered, harde grens RollOffMaxDistance). Gelicentieerde Creator Store-audio (APM / ProSoundEffects);
  -- vervangen = alleen de ID hieronder aanpassen. De client (PagodeRitClient) speelt de ritgeluiden synchroon met de rit.
  do
    local GELUID = {
      muziek = 1839842602,   -- APM "One World (a)" (wachtrij, levendig, etnische instrumenten, 201 s); kiezen met MuziekKiezer (M)
      brom = 9125767459,     -- PSE constante machinetoon (hydrauliek arm), toonhoogte/volume volgen de armsnelheid
      hek = 9116875342,      -- PSE metalen hekje open/dicht
      bel = 9119642644,      -- PSE dubbele bel (vertrek)
      wind = 9112777914,     -- PSE wind (alleen voor meerijders, hoog)
    }
    local oudG = pag:FindFirstChild("Geluid"); if oudG then oudG:Destroy() end
    local fg = Instance.new("Folder"); fg.Name = "Geluid"; fg.Parent = pag
    local function snd(ouder, naam, id, vol, minA, maxA, lus)
      local so = Instance.new("Sound"); so.Name = naam; so.SoundId = "rbxassetid://" .. id; so.Volume = vol; so.Looped = lus
      so.RollOffMode = Enum.RollOffMode.InverseTapered; so.RollOffMinDistance = minA; so.RollOffMaxDistance = maxA; so.Parent = ouder
      return so
    end
    local function box(naam, pos, kijk)
      local p = Instance.new("Part"); p.Name = naam; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
      p.Size = Vector3.new(0.75, 1.05, 0.6); p.Color = Color3.fromRGB(28, 28, 30); p.Material = Enum.Material.SmoothPlastic
      p.CFrame = CFrame.lookAt(pos, Vector3.new(kijk.X, pos.Y, kijk.Z)); p.Parent = fg
      local d = Instance.new("Part"); d.Name = "grill"; d.Anchored = true; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false
      d.Size = Vector3.new(0.62, 0.9, 0.05); d.Color = Color3.fromRGB(55, 55, 58); d.Material = Enum.Material.DiamondPlate
      d.CFrame = p.CFrame * CFrame.new(0, 0, -0.31); d.Parent = p
      return p
    end
    -- speakers langs de wachtrij aan de lantaarnpalen (LAMPEN uit omgeving_lampen.json, 0.7 m onder de kap), naar het pad gericht
    local LAMPEN = {{351.98, 64.73, 3.32}, {349.33, 67.88, 2.72}, {352.65, 59.94, 4.43}, {351.08, 62.56, 3.98}, {342.14, 56.76, 3.17}, {349.43, 56.37, 4.22}}
    for i, l in ipairs(LAMPEN) do
      local pos = Vector3.new(l[1] * S, 2 + (l[3] - 0.95) * S, -l[2] * S)
      local sp = box("speaker" .. i, pos + Vector3.new(0.45, 0, 0), Vector3.new(360 * S, 0, -47.5 * S))
      snd(sp, "muziek", GELUID.muziek, 0.55, 10, 75, true).Playing = true      -- ~25 m hoorbaar, daarna stil
    end
    -- machinegeluid bij de draaias van de arm en de cilinders; bel en hekjes bij het station
    local as = Instance.new("Part"); as.Name = "machine"; as.Anchored = true; as.CanCollide = false; as.CanQuery = false; as.CanTouch = false
    as.Transparency = 1; as.Size = Vector3.new(1, 1, 1); as.CFrame = PIV; as.Parent = fg
    snd(as, "brom", GELUID.brom, 0, 20, 160, true)
    local st0 = Instance.new("Part"); st0.Name = "station"; st0.Anchored = true; st0.CanCollide = false; st0.CanQuery = false; st0.CanTouch = false
    st0.Transparency = 1; st0.Size = Vector3.new(1, 1, 1); st0.Position = W(9.3, math.rad(140), 12.5); st0.Parent = fg
    snd(st0, "bel", GELUID.bel, 0.8, 12, 110, false)
    snd(st0, "hek", GELUID.hek, 0.7, 8, 60, false)
    -- geroezemoes: wachtende mensen (PSE walla), drie bronnen, hoorbaar tot ~20 m
    for _, w in ipairs({{"tribune", 20.0, 136, 0.6, 9112787259, 0.45}, {"laantje", 18.0, 108, -0.38, 9112766358, 0.35}, {"bordes", 12.6, 132, 1.3, 9112766358, 0.3}}) do
      local p = Instance.new("Part"); p.Name = "praten_" .. w[1]; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
      p.Transparency = 1; p.Size = Vector3.new(1, 1, 1); p.Position = W(w[2], math.rad(w[3]), 10 + w[4] + 1.2); p.Parent = fg
      local so = snd(p, "praten", w[5], w[6], 8, 60, true); so.Playing = true
      if w[1] == "bordes" then so.TimePosition = 17 end
    end
    local wind = Instance.new("Sound"); wind.Name = "wind"; wind.SoundId = "rbxassetid://" .. GELUID.wind; wind.Volume = 0; wind.Looped = true; wind.Parent = fg
  end
  local station = pag:FindFirstChild("Station") or pag
  local oud = station:FindFirstChild("Stationpoorten"); if oud then oud:Destroy() end
  local map = Instance.new("Folder"); map.Name = "Stationpoorten"; map.Parent = station
  local GROEN = Color3.fromRGB(22, 112, 86)
  local h = 0.85 / 9.05
  for _, pa in ipairs(POORT_ALFA) do
    local c = math.rad(pa - DRAAI)
    local Cp = W(9.05, c, 11.3)
    for _, sz in ipairs({-1, 1}) do
      local Hp = W(9.05, c + sz * h, 11.3)
      local hcf = CFrame.lookAt(Hp, Vector3.new(Cp.X, Hp.Y, Cp.Z))
      local L = (Hp - Cp).Magnitude - 0.1
      local blad = Instance.new("Folder"); blad.Name = "Blad"; blad.Parent = map
      blad:SetAttribute("Scharnier", hcf)
      local function stuk(naam, cf, size, zicht)
        local p = Instance.new("Part"); p.Name = naam; p.Anchored = true; p.Size = size; p.Color = GROEN; p.Material = Enum.Material.SmoothPlastic
        p.CanTouch = false; p.CastShadow = zicht; p.CanCollide = not zicht; p.Transparency = zicht and 0 or 1; p.CanQuery = zicht
        p.CFrame = hcf * cf; p:SetAttribute("Rel", cf); p.Parent = blad; return p
      end
      stuk("regel", CFrame.new(0, 1.1 * S, -L / 2), Vector3.new(0.2, 0.2, L), true)
      stuk("regel", CFrame.new(0, 0.12 * S, -L / 2), Vector3.new(0.2, 0.2, L), true)
      stuk("stijl", CFrame.new(0, 0.6 * S, -L + 0.1), Vector3.new(0.2, 1.0 * S, 0.2), true)
      for k = 1, 5 do stuk("spijl", CFrame.new(0, 0.6 * S, -L * k / 6), Vector3.new(0.08, 0.98 * S, 0.08), true) end
      stuk("poortblad", CFrame.new(0, 12, -L / 2), Vector3.new(0.4, 24, L), false).CollisionGroup = "Routemuur"   -- hoog: niet overheen springen
      -- naar buiten open: het einde van het blad gaat van het stationsmidden af
      local e0 = (hcf * CFrame.Angles(0, math.rad(80), 0) * CFrame.new(0, 0, -L)).Position
      local e1 = (hcf * CFrame.Angles(0, math.rad(-80), 0) * CFrame.new(0, 0, -L)).Position
      blad:SetAttribute("Teken", ((e0 - M) * Vector3.new(1, 0, 1)).Magnitude > ((e1 - M) * Vector3.new(1, 0, 1)).Magnitude and 1 or -1)
    end
  end
end"""
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
bronv = open(os.path.join(R, 'Voetstappen.client.luau')).read()
bronm = open(os.path.join(R, 'MuziekKiezer.client.luau')).read()
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
      stuk("poortblad", CFrame.new(0, 12, -L / 2), Vector3.new(0.4, 24, L), false)   -- hoog: niet over het dichte hekje springen
      -- naar binnen open: kies de draairichting waarbij het einde van het blad dichter bij het gondelmidden komt
      local eind0 = (hcf * CFrame.Angles(0, math.rad(80), 0) * CFrame.new(0, 0, -L)).Position
      local eind1 = (hcf * CFrame.Angles(0, math.rad(-80), 0) * CFrame.new(0, 0, -L)).Position
      local M = K0.Position
      blad:SetAttribute("Teken", ((eind0 - M) * Vector3.new(1, 0, 1)).Magnitude < ((eind1 - M) * Vector3.new(1, 0, 1)).Magnitude and 1 or -1)
    end
  end
end
{stpoort}
-- onzichtbare botsing langs alle hekken en relingen (12_omgeving / 18_route -> exports/omgeving_hekken.json)
do
  -- onzichtbare muren tot 24 studs boven de vloer: niet over hekken springen, je MOET de route volgen (Daan 17 nov).
  -- Groep Routemuur botst niet met Rijdend (wie meerijdt, zie PagodeRitClient): de gondel zwaait door de stationshekken.
  local PS = game:GetService("PhysicsService")
  for _, g in ipairs({{"Routemuur", "Rijdend"}}) do if not PS:IsCollisionGroupRegistered(g) then PS:RegisterCollisionGroup(g) end end
  PS:CollisionGroupSetCollidable("Routemuur", "Rijdend", false)
  local f = Instance.new("Folder"); f.Name = "Hekken"; f.Parent = pag
  for _, h in ipairs(HEKKEN) do
    local a = Vector3.new(h[1] * 3, 2 + h[3] * 3, -h[2] * 3); local b = Vector3.new(h[4] * 3, 2 + h[6] * 3, -h[5] * 3)
    local hoog = 24 + math.abs(a.Y - b.Y)
    local m = (a + b) / 2 + Vector3.new(0, hoog / 2 - 0.5 - math.abs(a.Y - b.Y) / 2, 0)
    local p = Instance.new("Part"); p.Name = "hekbotsing"; p.Anchored = true; p.Transparency = 1; p.CanCollide = true; p.CanQuery = false
    p.CanTouch = false; p.CollisionGroup = "Routemuur"; p.Size = Vector3.new(0.4, hoog, Vector3.new(b.X - a.X, 0, b.Z - a.Z).Magnitude + 0.2)
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
for _, n in ipairs({{"Voetstappen", "MuziekKiezer"}}) do local o = sps:FindFirstChild(n); if o then o:Destroy() end end
local lv = Instance.new("LocalScript"); lv.Name = "Voetstappen"; lv.Source = [==[{bronv}]==]; lv.Parent = sps
local lm = Instance.new("LocalScript"); lm.Name = "MuziekKiezer"; lm.Source = [==[{bronm}]==]; lm.Parent = sps
local n = 0; for _, p in ipairs(gondel:GetDescendants()) do if p:IsA("BasePart") then n += 1 end end
return "Pagode rijklaar: gondel " .. n .. " delen, cilinders " .. #cils:GetChildren()
'''
open(os.path.join(R, 'pagode_rit.luau'), 'w').write(luau)
print('pagode_rit.luau', len(luau), 'tekens; PIV', PIV, 'JL', JL)
