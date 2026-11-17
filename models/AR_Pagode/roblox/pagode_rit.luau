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
-- gondel als een losse groep: alles gelast aan de kern, kern gestuurd door starre Align-constraints
local kern = Instance.new("Part"); kern.Name = "Kern"; kern.Size = Vector3.new(2, 2, 2); kern.Transparency = 1; kern.CanCollide = false
kern.CanQuery = false; kern.CanTouch = false; kern.Anchored = false
kern.CFrame = CFrame.new(PIV:PointToWorldSpace(pag:GetAttribute("GondelLokaal"))) * PIV.Rotation; kern.Parent = gondel
for _, p in ipairs(gondel:GetDescendants()) do
  if p:IsA("BasePart") and p ~= kern then
    p.Anchored = false; p.Massless = true
    local w = Instance.new("WeldConstraint"); w.Part0 = kern; w.Part1 = p; w.Parent = p
  end
end
gondel.PrimaryPart = kern
local at = Instance.new("Attachment"); at.Name = "Doel"; at.Parent = kern
local ap = Instance.new("AlignPosition"); ap.Mode = Enum.PositionAlignmentMode.OneAttachment; ap.Attachment0 = at
ap.RigidityEnabled = true; ap.Position = kern.Position; ap.Parent = kern
local ao = Instance.new("AlignOrientation"); ao.Mode = Enum.OrientationAlignmentMode.OneAttachment; ao.Attachment0 = at
ao.RigidityEnabled = true; ao.CFrame = kern.CFrame.Rotation; ao.Parent = kern
-- ritscript
local sc = Instance.new("Script"); sc.Name = "PagodeRit"; sc.Source = [==[--!strict
-- PagodeRit: laat de Pagode rijden (Daan 17 nov: "laat eerst de attractie werken"). Hoort in ServerScriptService.
-- Ritverloop naar de on-ride video _Wz0aORIVaM (5 min): instappen in de bak, stijgen (~55 s), boven ~1 volle draai (~180 s),
-- dalen (~55 s). De arm draait om de draaias; de gondel blijft waterpas en draait om zijn eigen as.
-- De gondel is een losse (niet verankerde) groep, gestuurd met starre AlignPosition/AlignOrientation: zo beweegt hij met echte
-- snelheid en rijden spelers die erop staan mee. Arm en hefcilinders zijn verankerd en worden elk frame neergezet.
-- Opzet (modellen, lassen, cilinders): roblox/pagode_rit.luau. Maten: Blender-meters x 3 = stud.
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local PhysicsService = game:GetService("PhysicsService")

local S = 3
local pag = workspace:WaitForChild("Pagode") :: Model
local arm = pag:WaitForChild("Arm") :: Model
local gondel = pag:WaitForChild("Gondel") :: Model
local kern = gondel:WaitForChild("Kern") :: BasePart
local ap = kern:WaitForChild("AlignPosition") :: AlignPosition
local ao = kern:WaitForChild("AlignOrientation") :: AlignOrientation
local PIV = (pag:WaitForChild("AsFrame") :: CFrameValue).Value          -- draaias, stand omhoog
local JL = pag:GetAttribute("GondelLokaal") :: Vector3                     -- gondelmidden t.o.v. de as (lokaal, stud)
local Y_INSTAP = 2 + 1.3 * S                                               -- vlonder/instapniveau NAP 11.3
local DEK = 2.2 * S                                                        -- dek boven het gondelmidden
local BAK = Vector3.new(360.0 * S, 0, -47.5 * S)                           -- bakmidden

-- botsgroepen: de gondel botst niet met de wereld (hij zakt in de bak en de put), wel met spelers
pcall(function() PhysicsService:RegisterCollisionGroup("PagodeGondel") end)
pcall(function() PhysicsService:RegisterCollisionGroup("PagodeSpeler") end)
PhysicsService:CollisionGroupSetCollidable("PagodeGondel", "Default", false)
PhysicsService:CollisionGroupSetCollidable("PagodeGondel", "PagodeSpeler", true)
for _, p in gondel:GetDescendants() do if p:IsA("BasePart") then p.CollisionGroup = "PagodeGondel" end end
local function speler(ch: Model)
	for _, p in ch:GetDescendants() do if p:IsA("BasePart") then p.CollisionGroup = "PagodeSpeler" end end
	ch.DescendantAdded:Connect(function(p) if p:IsA("BasePart") then p.CollisionGroup = "PagodeSpeler" end end)
end
for _, pl in Players:GetPlayers() do if pl.Character then speler(pl.Character) end; pl.CharacterAdded:Connect(speler) end
Players.PlayerAdded:Connect(function(pl) pl.CharacterAdded:Connect(speler) end)

-- stand beneden: hoek waarbij het dek op instapniveau ligt (bisectie)
local function Jw(th: number): Vector3 return (PIV * CFrame.Angles(0, 0, th)):PointToWorldSpace(JL) end
local lo, hi = math.rad(70), math.rad(120)
for _ = 1, 50 do
	local m = (lo + hi) / 2
	if Jw(m).Y + DEK > Y_INSTAP then lo = m else hi = m end
end
local TH_D = (lo + hi) / 2
-- de armmaat uit de foto komt ~2.7 m tekort voor het bakmidden: kleine schuif die pas onderin meetelt
local jd = Jw(TH_D)
local CORR = Vector3.new(BAK.X - jd.X, 0, BAK.Z - jd.Z)
local function schuif(th: number): Vector3 local t = math.clamp(th / TH_D, 0, 1); return CORR * t ^ 4 end
pag:SetAttribute("HoekBeneden", math.deg(TH_D)); pag:SetAttribute("SchuifBeneden", CORR.Magnitude / S)

-- hefcilinders: voet vast in de put, kop op de arm; huis schuift over de zuigerstang
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
local function staaf(p: BasePart, a: Vector3, richting: Vector3, L: number)
	p.Size = Vector3.new(L, p.Size.Y, p.Size.Z)
	p.CFrame = CFrame.lookAt(a + richting * (L / 2), a + richting * L) * CFrame.Angles(0, math.pi / 2, 0)
end

-- hekken: open bij het instappen (reling op de gondel en rond de bak), dicht tijdens de rit
local function hekken(open: boolean)
	for _, p in gondel:GetDescendants() do if p:IsA("BasePart") and p.Name == "reling" then p.CanCollide = not open end end
	local st = pag:FindFirstChild("Station")
	if st then for _, p in st:GetDescendants() do if p:IsA("BasePart") and p.Name == "bakreling" then p.CanCollide = not open end end end
end

local FASEN = {{"instappen", 25}, {"sluiten", 5}, {"omhoog", 55}, {"boven", 180}, {"omlaag", 55}}
local T_RIT = 55 + 180 + 55
local function e(t: number): number return (1 - math.cos(math.pi * math.clamp(t, 0, 1))) / 2 end

local function stand(th: number, phi: number)
	arm:PivotTo(PIV * CFrame.Angles(0, 0, th))
	local rot = PIV.Rotation * CFrame.Angles(0, phi, 0)
	ap.Position = Jw(th) + schuif(th)
	ao.CFrame = rot
	local A = PIV * CFrame.Angles(0, 0, th)
	for _, c in cils do
		local k = A:PointToWorldSpace(c.kop); local u = (k - c.voet).Unit
		staaf(c.huis, c.voet, u, c.Lh)
		staaf(c.stang, k, -u, c.Ls)
	end
end

-- beginnen in de bak
local rot0 = PIV.Rotation
kern.CFrame = CFrame.new(Jw(TH_D) + schuif(TH_D)) * rot0
stand(TH_D, 0)
pcall(function() kern:SetNetworkOwner(nil) end)
pag:SetAttribute("Fase", "instappen")

while true do
	local t_rit = 0
	for _, f in FASEN do
		local naam, duur = f[1] :: string, f[2] :: number
		pag:SetAttribute("Fase", naam)
		hekken(naam == "instappen")
		local t0 = os.clock()
		while os.clock() - t0 < duur do
			local t = (os.clock() - t0) / duur
			local th = TH_D
			if naam == "omhoog" then th = TH_D * (1 - e(t))
			elseif naam == "boven" then th = 0
			elseif naam == "omlaag" then th = TH_D * e(t) end
			local phi = 0
			if naam == "omhoog" or naam == "boven" or naam == "omlaag" then
				phi = 2 * math.pi * e((t_rit + (os.clock() - t0)) / T_RIT)       -- een volle draai over de hele rit, zacht in/uit
			end
			stand(th, phi)
			RunService.Heartbeat:Wait()
		end
		if naam == "omhoog" or naam == "boven" or naam == "omlaag" then t_rit += duur end
	end
end
]==]; sc.Parent = game:GetService("ServerScriptService")
local n = 0; for _, p in ipairs(gondel:GetDescendants()) do if p:IsA("BasePart") then n += 1 end end
return "Pagode rijklaar: gondel " .. n .. " delen, cilinders " .. #cils:GetChildren()
