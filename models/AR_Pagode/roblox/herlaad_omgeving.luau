-- Alleen de omgeving opnieuw laden (zelfde laad/aankleden als plaats_pagode.luau).
-- De Pagode plaatsen (gegenereerd door models/AR_Pagode/roblox/maak_plaatsscript.py). Stand OMHOOG, statisch.
-- Gondel+arm+voet: oorsprong = draaias, op park (320.5, 58.5), 4.2 m boven de grond, draaiing 164.44 graden.
-- Station: oorsprong = middelpunt bak, park (360.0, 47.5); 180 graden gedraaid (Blender x oost/y noord -> Roblox).
-- Hoogte: NAP 10.0 = Roblox Y 2. Terrein uit AHN (x 300..385, y 15..80), materiaal uit de luchtfoto.
local ID = {AR_Pagode_gondel = 136098683069651, AR_Pagode_station = 124320247767428, pannen_kleur = 113862951849627, pannen_normaal = 135305032497691, sierveld_kleur = 92806080990483, sierveld_normaal = 75982823389914, windveer_kleur = 105110194440006, windveer_normaal = 129813406208116, trommel_kleur = 94643214361680, trommel_normaal = 105998268539020, sierrand_kleur = 114707188453195, sierrand_normaal = 98163589145950, kernwand_kleur = 118948255846476, kernwand_normaal = 77932851706654, arm_kleur = 125000713070178, arm_normaal = 115276388154879, natuursteen_kleur = 93634200024177, natuursteen_normaal = 71110702105863, vlonder_kleur = 114168670349764, vlonder_normaal = 105858881415149, klinker_kleur = 76036336782300, klinker_normaal = 132177172189347, bord_kleur = 107214009738343, AR_Pagode_omgeving = 122540641504294, ingangsbord_kleur = 106758910462500, uitgangsbord_kleur = 71715100841980, breuksteen_kleur = 74939119820853, breuksteen_normaal = 96183299144764, bamboe_kleur = 100311851570971, blad_kleur = 75105356130828, spar_kleur = 91377517844234, naald_kleur = 72168876031761, haag_kleur = 97966661994557, bloem_kleur = 71396169120830, schors_kleur = 139686993244290, tokorand_kleur = 115150839917312, tokopaneel_kleur = 109978993367892, parasol_kleur = 116141934527280, wilg_kleur = 100412416431599, steen_kleur = 116600353020198, steen_normaal = 95927671453559, pluk_kleur = 82875106386837, huisrand_kleur = 74245754818603}
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

local oud = workspace:FindFirstChild("PagodeOmgeving"); if oud then oud:Destroy() end
local omgeving = laad(ID.AR_Pagode_omgeving, "PagodeOmgeving"); aankleden(omgeving, true)
omgeving:PivotTo(CFrame.new(park(360.0, 47.5, 10)) * CFrame.Angles(0, math.pi, 0))
return "omgeving: " .. #omgeving:GetChildren() .. " delen"
