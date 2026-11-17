-- De Pagode plaatsen (gegenereerd door models/AR_Pagode/roblox/maak_plaatsscript.py). Stand OMHOOG, statisch.
-- Gondel+arm+voet: oorsprong = draaias, op park (320.5, 58.5), 4.2 m boven de grond, draaiing 164.44 graden.
-- Station: oorsprong = middelpunt bak, park (360.0, 47.5); 180 graden gedraaid (Blender x oost/y noord -> Roblox).
-- Hoogte: NAP 10.0 = Roblox Y 2. Terrein uit AHN (x 300..385, y 15..80), materiaal uit de luchtfoto.
local ID = {AR_Pagode_gondel = 87895236112943, AR_Pagode_station = 124320247767428, pannen_kleur = 113862951849627, pannen_normaal = 135305032497691, sierveld_kleur = 92806080990483, sierveld_normaal = 75982823389914, windveer_kleur = 105110194440006, windveer_normaal = 129813406208116, trommel_kleur = 94643214361680, trommel_normaal = 105998268539020, sierrand_kleur = 114707188453195, sierrand_normaal = 98163589145950, kernwand_kleur = 118948255846476, kernwand_normaal = 77932851706654, arm_kleur = 125000713070178, arm_normaal = 115276388154879, natuursteen_kleur = 93634200024177, natuursteen_normaal = 71110702105863, vlonder_kleur = 114168670349764, vlonder_normaal = 105858881415149, klinker_kleur = 76036336782300, klinker_normaal = 132177172189347, bord_kleur = 107214009738343, AR_Pagode_omgeving = 114216309813465, ingangsbord_kleur = 106758910462500, uitgangsbord_kleur = 71715100841980, breuksteen_kleur = 74939119820853, breuksteen_normaal = 96183299144764, bamboe_kleur = 100311851570971, blad_kleur = 75105356130828, spar_kleur = 91377517844234, naald_kleur = 72168876031761, haag_kleur = 97966661994557, bloem_kleur = 71396169120830, schors_kleur = 139686993244290, tokorand_kleur = 115150839917312, tokopaneel_kleur = 109978993367892, parasol_kleur = 116141934527280, wilg_kleur = 100412416431599, steen_kleur = 116600353020198, steen_normaal = 95927671453559, pluk_kleur = 82875106386837, huisrand_kleur = 74245754818603, AR_Pagode_arm = 88039896274620, AR_Pagode_voet = 79185188175320}
local S = 3
local G = 2                                   -- Roblox Y van NAP 10.0
local function park(x, y, nap) return Vector3.new(x * S, G + (nap - 10) * S, -y * S) end

local function laad(id, naam)
  local m = Instance.new("Model"); m.Name = naam
  for _, o in ipairs(game:GetObjects("rbxassetid://" .. id)) do o.Parent = m end
  for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
  for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
  m.Parent = workspace; m:ScaleTo(S)
  local anker
  for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
  assert(anker, "geen anker in " .. naam)
  local told = CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0))
  m:PivotTo(told:Inverse() * m:GetPivot()); anker:Destroy()
  m.WorldPivot = CFrame.new()
  return m
end

-- rol -> textuur (SurfaceAppearance) of effen kleur + materiaal
local TEX = {pannen = true, sierveld = true, windveer = true, trommel = true, sierrand = true, kernwand = true, arm = true,
  natuursteen = true, vlonder = true, klinker = true, bord = true, ingangsbord = true, uitgangsbord = true, breuksteen = true,
  bamboe = true, blad = true, spar = true, naald = true, haag = true, bloem = true, schors = true, tokorand = true, tokopaneel = true, parasol = true, wilg = true, steen = true, pluk = true, huisrand = true}
local ALPHA = {bamboe = true, blad = true, spar = true, wilg = true, pluk = true}       -- bladkaarten: transparantie uit de textuur
local EFFEN = {
  groen = {Color3.fromRGB(22, 112, 86), Enum.Material.SmoothPlastic}, rib = {Color3.fromRGB(232, 228, 216), Enum.Material.SmoothPlastic},
  vlam = {Color3.fromRGB(236, 232, 220), Enum.Material.SmoothPlastic}, goud = {Color3.fromRGB(214, 168, 70), Enum.Material.Metal},
  rood = {Color3.fromRGB(112, 20, 24), Enum.Material.SmoothPlastic}, onderkant = {Color3.fromRGB(40, 14, 14), Enum.Material.SmoothPlastic},
  dek = {Color3.fromRGB(96, 82, 66), Enum.Material.WoodPlanks}, wit = {Color3.fromRGB(230, 230, 222), Enum.Material.SmoothPlastic},
  armzijde = {Color3.fromRGB(216, 202, 176), Enum.Material.SmoothPlastic}, beton_groen = {Color3.fromRGB(46, 70, 50), Enum.Material.Concrete},
  beton_donker = {Color3.fromRGB(42, 42, 42), Enum.Material.Concrete}, rooster = {Color3.fromRGB(72, 74, 76), Enum.Material.DiamondPlate},
  hek = {Color3.fromRGB(22, 22, 22), Enum.Material.Metal}, staal = {Color3.fromRGB(92, 94, 98), Enum.Material.Metal},
  chroom = {Color3.fromRGB(205, 205, 210), Enum.Material.Metal}, wit_glans = {Color3.fromRGB(228, 222, 206), Enum.Material.SmoothPlastic},
  grind = {Color3.fromRGB(84, 76, 66), Enum.Material.Pebble}, beton_groen_licht = {Color3.fromRGB(78, 104, 82), Enum.Material.Concrete},
  staal_groen = {Color3.fromRGB(24, 62, 44), Enum.Material.Metal}, hek_open = {Color3.fromRGB(24, 62, 44), Enum.Material.Metal},
  brons = {Color3.fromRGB(64, 46, 30), Enum.Material.Metal}, lamp = {Color3.fromRGB(255, 214, 150), Enum.Material.Neon},
  lamp_groen = {Color3.fromRGB(70, 255, 120), Enum.Material.Neon}, glas = {Color3.fromRGB(150, 172, 176), Enum.Material.Glass},
  dak_donker = {Color3.fromRGB(46, 46, 50), Enum.Material.Slate}, aarde = {Color3.fromRGB(58, 40, 28), Enum.Material.Ground},
  reling = {Color3.fromRGB(20, 36, 26), Enum.Material.Metal}, bord_blauw = {Color3.fromRGB(128, 196, 212), Enum.Material.SmoothPlastic},
  bamboestam = {Color3.fromRGB(118, 122, 52), Enum.Material.SmoothPlastic},
  dak_toko = {Color3.fromRGB(86, 88, 94), Enum.Material.Slate}, rotan = {Color3.fromRGB(150, 112, 64), Enum.Material.Fabric},
  rood_hek = {Color3.fromRGB(150, 22, 28), Enum.Material.SmoothPlastic}, beton_licht = {Color3.fromRGB(150, 144, 132), Enum.Material.Concrete},
  asfalt = {Color3.fromRGB(70, 70, 72), Enum.Material.Asphalt},
  voeg = {Color3.fromRGB(52, 46, 40), Enum.Material.Slate}, graniet = {Color3.fromRGB(112, 110, 104), Enum.Material.Granite},
  naald_donker = {Color3.fromRGB(18, 32, 18), Enum.Material.Grass},
}
local LOOP = {dek = true, vlonder = true, klinker = true, rooster = true, beton_groen = true, beton_groen_licht = true, natuursteen = true, grind = true,
  breuksteen = true, aarde = true, bloem = true, beton_licht = true, asfalt = true, voeg = true, graniet = true}

local function aankleden(m, opstaan)
  for _, p in ipairs(m:GetChildren()) do
    local rol = string.match(p.Name, "^PG_(.-)_%d+") or "rood"   -- ook met .001-achtervoegsel
    p.Anchored = true; p.CanTouch = false; p.CastShadow = true
    p.CanCollide = opstaan and LOOP[rol] == true
    if p.CanCollide then pcall(function() p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end) end
    if TEX[rol] then
      local s = Instance.new("SurfaceAppearance")
      s.ColorMap = "rbxassetid://" .. ID[rol .. "_kleur"]
      if ID[rol .. "_normaal"] then s.NormalMap = "rbxassetid://" .. ID[rol .. "_normaal"] end
      if rol == "klinker" then s.Color = Color3.fromRGB(200, 194, 186) end      -- tegen het paarse schemerlicht in (video = daglicht)
      if rol == "breuksteen" or rol == "steen" then s.Color = Color3.fromRGB(206, 204, 180) end
      if ALPHA[rol] then s.AlphaMode = Enum.AlphaMode.Transparency; p.CastShadow = true end
      s.Parent = p
    elseif EFFEN[rol] then
      p.Color = EFFEN[rol][1]; p.Material = EFFEN[rol][2]
      if rol == "chroom" then p.Reflectance = 0.15 end
      if rol == "glas" then p.Transparency = 0.55 end
      if rol == "lamp" or rol == "lamp_groen" then p.CastShadow = false end
    end
  end
end

-- ===== rijdende Pagode: opzet (gegenereerd door roblox/maak_ritscript.py) =====
local PIV = CFrame.new(park(320.5, 58.5, 10 + 4.199)) * CFrame.Angles(0, math.rad(164.4385), 0)
local oudS = game:GetService("ServerScriptService"):FindFirstChild("PagodeRit"); if oudS then oudS:Destroy() end
local oud = workspace:FindFirstChild("Pagode"); if oud then oud:Destroy() end
local pag = Instance.new("Model"); pag.Name = "Pagode"; pag.Parent = workspace
pag.ModelStreamingMode = Enum.ModelStreamingMode.Persistent       -- place streamt: anders mist de client delen van de gondel
local av = Instance.new("CFrameValue"); av.Name = "AsFrame"; av.Value = PIV; av.Parent = pag
pag:SetAttribute("GondelLokaal", Vector3.new(1.5000, 115.8020, 0.0000))
local function zet(id, naam) local m = laad(id, naam); aankleden(m, true); m:PivotTo(PIV); m.Parent = pag; return m end
local voet = zet(ID.AR_Pagode_voet, "Voet")
local arm = zet(ID.AR_Pagode_arm, "Arm")
local gondel = zet(ID.AR_Pagode_gondel, "Gondel")
for _, p in ipairs(arm:GetChildren()) do if p:IsA("BasePart") then p.CanCollide = false end end
-- afwerking (lampjes, lichtsnoeren, reling) in de gondel
do
-- Afwerking Pagode (na plaats_pagode.luau): botsing, plafondlampjes, lichtsnoeren langs de gevels, rode ring onder het platform.
-- Maten = Blender-maten (build/02-03): RAND 1.5, dek 2.2, goot 4.8, gevelpunt 6.8, gevelfront r 8.4, 22 gevels, as (0.5, 0, -38.6).
-- Blender-lokaal (x, y, z) -> Roblox: Pagode:GetPivot() * CFrame.new(-(x - 0.5) * 3, (z + 38.6) * 3, y * 3)
-- Bronnen: Pagode-donker.jpg (lichtsnoeren langs de gevels, rode lijn onder het platform), video 6:45 (ronde plafondlampjes).
local S = 3
local g = gondel
local st = workspace:WaitForChild("PagodeStation")
local PIV = g:GetPivot()
local function B(x, y, z) return PIV * CFrame.new(-(x - 0.5) * S, (z + 38.6) * S, y * S) end
local oud = g:FindFirstChild("Afwerking"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "Afwerking"; map.Parent = g
local function deel(naam, cf, size, eig)
  local p = Instance.new("Part"); p.Name = naam; p.Anchored = true; p.CanTouch = false; p.CastShadow = false
  p.Size = size; p.CFrame = cf
  for k, v in pairs(eig) do p[k] = v end
  p.Parent = map; return p
end
local function staaf(naam, a, b, dikte, eig)   -- a, b: Roblox-posities
  local d = b - a
  return deel(naam, CFrame.lookAt((a + b) / 2, b), Vector3.new(dikte, dikte, d.Magnitude), eig)
end
local ONZ = {Transparency = 1, CanCollide = true, CanQuery = false}

-- 1 botsing: reling gondel (r 8.3, dek 2.2 -> 3.5), binnenwand (r 5.4) wordt muur
for i = 0, 63 do
  local a0, a1 = i / 64 * 2 * math.pi, (i + 1) / 64 * 2 * math.pi
  local p0, p1 = B(8.32 * math.cos(a0), 8.32 * math.sin(a0), 2.85).Position, B(8.32 * math.cos(a1), 8.32 * math.sin(a1), 2.85).Position
  deel("reling", CFrame.lookAt((p0 + p1) / 2, p1), Vector3.new(0.6, 1.3 * S, (p1 - p0).Magnitude + 0.3), ONZ)
end
for _, p in ipairs(g:GetChildren()) do
  if p:IsA("BasePart") and string.match(p.Name, "^PG_kernwand") then p.CanCollide = true end
end
-- reling bakrand (station: r 8.95 rond (360, 47.5), instapniveau NAP 11.3), behalve bij de sleuf (164.4 +- 7.5 graden)
for i = 0, 71 do
  local a0, a1 = math.rad(i * 5), math.rad(i * 5 + 5)
  local m = (i * 5 + 2.5)
  if not (m > 156.9 and m < 171.9) then
    local function w(a) return Vector3.new((360 + 8.95 * math.cos(a)) * S, 2 + (1.3 + 0.55) * S, -(47.5 + 8.95 * math.sin(a)) * S) end
    local p0, p1 = w(a0), w(a1)
    deel("bakreling", CFrame.lookAt((p0 + p1) / 2, p1), Vector3.new(0.6, 1.1 * S, (p1 - p0).Magnitude + 0.3), ONZ)
  end
end

-- 2 ronde plafondlampjes (22, r 6.9, onder het plafond op z 4.58) met warm licht
for i = 0, 21 do
  local a = (i + 0.5) / 22 * 2 * math.pi
  local cf = B(6.9 * math.cos(a), 6.9 * math.sin(a), 4.57)
  local l = deel("plafondlamp", cf, Vector3.new(0.12 * S, 0.9 * S, 0.9 * S),
    {Shape = Enum.PartType.Cylinder, Material = Enum.Material.Neon, Color = Color3.fromRGB(255, 214, 150), CanCollide = false, CanQuery = false})
  l.CFrame = cf * CFrame.Angles(0, 0, math.pi / 2)
  local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 190, 120); pl.Brightness = 1.2; pl.Range = 14; pl.Shadows = false; pl.Parent = l
end

-- 3 lichtsnoeren langs de windveren (warm wit, Pagode-donker.jpg) en lampjes op de gevelpunten
local N, R, Z0, Z1 = 22, 8.4, 4.8, 6.8
local hw = math.pi * R / N
local LICHT = {Material = Enum.Material.Neon, Color = Color3.fromRGB(255, 226, 170), CanCollide = false, CanQuery = false}
for i = 0, N - 1 do
  local h = i / N * 2 * math.pi
  local c, s = math.cos(h), math.sin(h)
  -- gevel-lokaal (x raaklijn, -y naar buiten) -> Blender: draai (h + 90 graden) en schuif naar r 8.4
  local function gl(x, y, z)
    local rx = x * math.cos(h + math.pi / 2) - y * math.sin(h + math.pi / 2)
    local ry = x * math.sin(h + math.pi / 2) + y * math.cos(h + math.pi / 2)
    return B(R * c + rx, R * s + ry, z).Position
  end
  local top = gl(0, -0.16, Z1 + 0.14)
  for k, sx in ipairs({-1, 1}) do
    staaf("lichtsnoer", gl(sx * (hw + 0.1), -0.16, Z0 - 0.04), top, 0.22, LICHT)
  end
end
-- rode lichtlijn onder het platform (onderrand sierrand, r 8.52)
for i = 0, 47 do
  local a0, a1 = i / 48 * 2 * math.pi, (i + 1) / 48 * 2 * math.pi
  staaf("rodelijn", B(8.55 * math.cos(a0), 8.55 * math.sin(a0), 1.54).Position, B(8.55 * math.cos(a1), 8.55 * math.sin(a1), 1.54).Position, 0.25,
    {Material = Enum.Material.Neon, Color = Color3.fromRGB(255, 40, 40), CanCollide = false, CanQuery = false})
end
-- 4 lantaarns van de omgeving (12_omgeving.py -> exports/omgeving_lampen.json, park x, y, z = NAP - 10): warm licht
local LAMPEN = {{351.98, 64.73, 3.32}, {349.33, 67.88, 2.72}, {352.65, 59.94, 4.43}, {351.08, 62.56, 3.98}, {342.14, 56.76, 3.17}, {349.43, 56.37, 4.22}, {360.31, 65.30, 2.54}, {370.20, 42.08, 2.57}, {371.38, 49.51, 2.57}}
for i, l in ipairs(LAMPEN) do
  local p = Instance.new("Part"); p.Name = "lantaarnlicht"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
  p.Transparency = 1; p.Size = Vector3.new(0.3, 0.3, 0.3); p.Position = Vector3.new(l[1] * S, 2 + l[3] * S, -l[2] * S); p.Parent = map
  local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 128); pl.Brightness = 1.4; pl.Range = 18; pl.Shadows = true; pl.Parent = p
end


end
local station = Instance.new("Folder"); station.Name = "Station"; station.Parent = pag
for _, p in ipairs(gondel:GetDescendants()) do
  if p:IsA("BasePart") and (p.Name == "bakreling" or p.Name == "lantaarnlicht") then p.Parent = station end
end
-- hefcilinders (bewegen mee met de arm, zie PagodeRit)
local cils = Instance.new("Folder"); cils.Name = "Cilinders"; cils.Parent = pag
do local f = Instance.new("Folder"); f.Name = "Cil0"; f.Parent = cils
  f:SetAttribute("Voet", Vector3.new(-19.5000, -20.1000, -2.8500)); f:SetAttribute("Kop", Vector3.new(-0.8005, 8.3618, -2.8500))
  for _, d in ipairs({{"Huis", 0.72, Color3.fromRGB(228, 222, 206), Enum.Material.SmoothPlastic}, {"Stang", 0.34, Color3.fromRGB(205, 205, 210), Enum.Material.Metal}}) do
    local p = Instance.new("Part"); p.Name = d[1]; p.Shape = Enum.PartType.Cylinder; p.Anchored = true; p.CanCollide = false; p.CanTouch = false
    p.Size = Vector3.new(1, d[2] * S, d[2] * S); p.Color = d[3]; p.Material = d[4]; p.Parent = f
  end
end
do local f = Instance.new("Folder"); f.Name = "Cil1"; f.Parent = cils
  f:SetAttribute("Voet", Vector3.new(-19.5000, -20.1000, 2.8500)); f:SetAttribute("Kop", Vector3.new(-0.8005, 8.3618, 2.8500))
  for _, d in ipairs({{"Huis", 0.72, Color3.fromRGB(228, 222, 206), Enum.Material.SmoothPlastic}, {"Stang", 0.34, Color3.fromRGB(205, 205, 210), Enum.Material.Metal}}) do
    local p = Instance.new("Part"); p.Name = d[1]; p.Shape = Enum.PartType.Cylinder; p.Anchored = true; p.CanCollide = false; p.CanTouch = false
    p.Size = Vector3.new(1, d[2] * S, d[2] * S); p.Color = d[3]; p.Material = d[4]; p.Parent = f
  end
end
-- gondel: alle delen verankerd; de client verplaatst ze (PagodeRitClient). Kern = draaipunt van de gondel.
local kern = Instance.new("Part"); kern.Name = "Kern"; kern.Size = Vector3.new(2, 2, 2); kern.Transparency = 1; kern.CanCollide = false
kern.CanQuery = false; kern.CanTouch = false; kern.Anchored = true
kern.CFrame = CFrame.new(PIV:PointToWorldSpace(pag:GetAttribute("GondelLokaal"))) * PIV.Rotation; kern.Parent = gondel
gondel.PrimaryPart = kern
-- ritscript
local sc = Instance.new("Script"); sc.Name = "PagodeRit"; sc.Source = [==[--!strict
-- PagodeRit (server): zet alleen de starttijd van de ritcyclus (servertijd). De beweging zelf draait op elke client
-- (PagodeRitClient.client.luau, StarterPlayerScripts) met workspace:GetServerTimeNow(): iedereen ziet dezelfde stand,
-- zonder netwerkvertraging. Daan 17 nov: de server-gestuurde gondel trilde, belichting bleekte uit (losse physics-delen) en
-- spelers zakten weg. Nu blijft alles verankerd.
local pag = workspace:WaitForChild("Pagode") :: Model
pag:SetAttribute("RitStart", workspace:GetServerTimeNow())
]==]; sc.Parent = game:GetService("ServerScriptService")
local sps = game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts")
local oudC = sps:FindFirstChild("PagodeRitClient"); if oudC then oudC:Destroy() end
local lc = Instance.new("LocalScript"); lc.Name = "PagodeRitClient"; lc.Source = [==[--!strict
-- PagodeRitClient (StarterPlayerScripts): laat de Pagode rijden op deze client.
-- Ritverloop naar de on-ride video _Wz0aORIVaM (5 min): instappen 25 s (hekken open), sluiten 5 s, omhoog 55 s, boven 180 s,
-- omlaag 55 s; een volle draai over de rit. De arm draait om de draaias (AsFrame, lokale Z-as), de gondel blijft waterpas.
-- Alles verankerd en verplaatst met BulkMoveTo; de stand volgt uit workspace:GetServerTimeNow() - RitStart (zelfde voor iedereen).
-- Wie op het dek staat wordt elk frame met de gondel meegenomen (geen wegzakken, geen trillen).
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

local S = 3
local pag = workspace:WaitForChild("Pagode") :: Model
local arm = pag:WaitForChild("Arm") :: Model
local gondel = pag:WaitForChild("Gondel") :: Model
local kern = gondel:WaitForChild("Kern") :: BasePart
local PIV = (pag:WaitForChild("AsFrame") :: CFrameValue).Value
local JL = pag:GetAttribute("GondelLokaal") :: Vector3
local Y_INSTAP = 2 + 1.3 * S
local DEK = 2.2 * S
local BAK = Vector3.new(360.0 * S, 0, -47.5 * S)

local function Jw(th: number): Vector3 return (PIV * CFrame.Angles(0, 0, th)):PointToWorldSpace(JL) end
local lo, hi = math.rad(70), math.rad(120)
for _ = 1, 50 do
	local m = (lo + hi) / 2
	if Jw(m).Y + DEK > Y_INSTAP then lo = m else hi = m end
end
local TH_D = (lo + hi) / 2
local jd = Jw(TH_D)
local CORR = Vector3.new(BAK.X - jd.X, 0, BAK.Z - jd.Z)        -- armmaat uit de foto komt 2.7 m tekort: schuif die pas onderin telt
local function schuif(th: number): Vector3 local t = math.clamp(th / TH_D, 0, 1); return CORR * t ^ 4 end

-- delen en hun vaste ligging t.o.v. arm-frame en gondelkern (eenmalig)
local K0 = kern.CFrame
local gDelen, gRel = {}, {}
for _, p in gondel:GetDescendants() do
	if p:IsA("BasePart") then p.Anchored = true; table.insert(gDelen, p); table.insert(gRel, K0:ToObjectSpace(p.CFrame)) end
end
local A0 = PIV
local aDelen, aRel = {}, {}
for _, p in arm:GetDescendants() do
	if p:IsA("BasePart") then p.Anchored = true; table.insert(aDelen, p); table.insert(aRel, A0:ToObjectSpace(p.CFrame)) end
end
local relingen: {BasePart} = {}
for _, p in gDelen do if p.Name == "reling" then table.insert(relingen, p) end end
local st = pag:FindFirstChild("Station")
if st then for _, p in st:GetDescendants() do if p:IsA("BasePart") and p.Name == "bakreling" then table.insert(relingen, p) end end end

type Cil = {voet: Vector3, kop: Vector3, huis: BasePart, stang: BasePart, Lh: number, Ls: number}
local cils: {Cil} = {}
for _, c in (pag:WaitForChild("Cilinders") :: Folder):GetChildren() do
	if c:IsA("Folder") then
		local v, k = c:GetAttribute("Voet") :: Vector3, c:GetAttribute("Kop") :: Vector3
		local Lup = (k - v).Magnitude
		table.insert(cils, {voet = PIV:PointToWorldSpace(v), kop = k, huis = c:WaitForChild("Huis") :: BasePart,
			stang = c:WaitForChild("Stang") :: BasePart, Lh = 0.62 * Lup + 0.9, Ls = 0.38 * Lup + 0.6})
	end
end
local function staaf(p: BasePart, a: Vector3, r: Vector3, L: number)
	p.Size = Vector3.new(L, p.Size.Y, p.Size.Z)
	p.CFrame = CFrame.lookAt(a + r * (L / 2), a + r * L) * CFrame.Angles(0, math.pi / 2, 0)
end

local FASEN = {{"instappen", 25}, {"sluiten", 5}, {"omhoog", 55}, {"boven", 180}, {"omlaag", 55}}
local CYCLUS, T_RIT = 0, 55 + 180 + 55
for _, f in FASEN do CYCLUS += f[2] :: number end
local function e(t: number): number return (1 - math.cos(math.pi * math.clamp(t, 0, 1))) / 2 end

local function stand(tc: number): (number, number, string)
	local t0, t_rit = 0, 0
	for _, f in FASEN do
		local naam, duur = f[1] :: string, f[2] :: number
		if tc < t0 + duur then
			local t = (tc - t0) / duur
			local th = TH_D
			if naam == "omhoog" then th = TH_D * (1 - e(t)) elseif naam == "boven" then th = 0 elseif naam == "omlaag" then th = TH_D * e(t) end
			local phi = 0
			if naam == "omhoog" or naam == "boven" or naam == "omlaag" then phi = 2 * math.pi * e((t_rit + tc - t0) / T_RIT) end
			return th, phi, naam
		end
		t0 += duur
		if naam == "omhoog" or naam == "boven" or naam == "omlaag" then t_rit += duur end
	end
	return TH_D, 0, "instappen"
end

local plr = Players.LocalPlayer
local ray = RaycastParams.new(); ray.FilterType = Enum.RaycastFilterType.Include; ray.FilterDescendantsInstances = {gondel}
local gK = K0
local fase = ""
local cfs = table.create(#gDelen)
local acfs = table.create(#aDelen)

RunService.PreSimulation:Connect(function()
	local start = pag:GetAttribute("RitStart") :: number?
	if not start then return end
	local tc = (workspace:GetServerTimeNow() - start) % CYCLUS
	local th, phi, naam = stand(tc)
	local A = PIV * CFrame.Angles(0, 0, th)
	local nieuwK = CFrame.new(Jw(th) + schuif(th)) * PIV.Rotation * CFrame.Angles(0, phi, 0)
	-- speler op het dek: meenemen met de verplaatsing van de gondel
	local ch = plr.Character
	local hrp = ch and ch:FindFirstChild("HumanoidRootPart") :: BasePart?
	if hrp then
		local r = workspace:Raycast(hrp.Position, Vector3.new(0, -6, 0), ray)
		if r then hrp.CFrame = (nieuwK * gK:Inverse()) * hrp.CFrame end
	end
	for i, rel in gRel do cfs[i] = nieuwK * rel end
	workspace:BulkMoveTo(gDelen, cfs, Enum.BulkMoveMode.FireCFrameChanged)
	for i, rel in aRel do acfs[i] = A * rel end
	workspace:BulkMoveTo(aDelen, acfs, Enum.BulkMoveMode.FireCFrameChanged)
	for _, c in cils do
		local k = A:PointToWorldSpace(c.kop); local u = (k - c.voet).Unit
		staaf(c.huis, c.voet, u, c.Lh); staaf(c.stang, k, -u, c.Ls)
	end
	gK = nieuwK
	pag:SetAttribute("FaseLokaal", naam)
	if naam ~= fase then
		fase = naam
		for _, p in relingen do p.CanCollide = naam ~= "instappen" end
	end
end)
]==]; lc.Parent = sps
local n = 0; for _, p in ipairs(gondel:GetDescendants()) do if p:IsA("BasePart") then n += 1 end end
return "Pagode rijklaar: gondel " .. n .. " delen, cilinders " .. #cils:GetChildren()
