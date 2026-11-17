-- De Pagode plaatsen (gegenereerd door models/AR_Pagode/roblox/maak_plaatsscript.py). Stand OMHOOG, statisch.
-- Gondel+arm+voet: oorsprong = draaias, op park (320.5, 58.5), 4.2 m boven de grond, draaiing 164.44 graden.
-- Station: oorsprong = middelpunt bak, park (360.0, 47.5); 180 graden gedraaid (Blender x oost/y noord -> Roblox).
-- Hoogte: NAP 10.0 = Roblox Y 2. Terrein uit AHN (x 300..385, y 15..80), materiaal uit de luchtfoto.
local ID = {AR_Pagode_gondel = 80470568889612, AR_Pagode_station = 118332205413998, pannen_kleur = 113862951849627, pannen_normaal = 135305032497691, sierveld_kleur = 92806080990483, sierveld_normaal = 75982823389914, windveer_kleur = 105110194440006, windveer_normaal = 129813406208116, trommel_kleur = 94643214361680, trommel_normaal = 105998268539020, sierrand_kleur = 114707188453195, sierrand_normaal = 98163589145950, kernwand_kleur = 118948255846476, kernwand_normaal = 77932851706654, arm_kleur = 125000713070178, arm_normaal = 115276388154879, natuursteen_kleur = 93634200024177, natuursteen_normaal = 71110702105863, vlonder_kleur = 114168670349764, vlonder_normaal = 105858881415149, klinker_kleur = 76036336782300, klinker_normaal = 132177172189347, bord_kleur = 107214009738343, AR_Pagode_omgeving = 77125367267740, ingangsbord_kleur = 106758910462500, uitgangsbord_kleur = 71715100841980, breuksteen_kleur = 74939119820853, breuksteen_normaal = 96183299144764, bamboe_kleur = 100311851570971, blad_kleur = 75105356130828, spar_kleur = 91377517844234, naald_kleur = 72168876031761, haag_kleur = 97966661994557, bloem_kleur = 71396169120830, schors_kleur = 139686993244290, tokorand_kleur = 115150839917312, tokopaneel_kleur = 109978993367892, parasol_kleur = 116141934527280, wilg_kleur = 100412416431599, steen_kleur = 116600353020198, steen_normaal = 95927671453559, pluk_kleur = 82875106386837, huisrand_kleur = 74245754818603, AR_Pagode_arm = 88039896274620, AR_Pagode_voet = 79185188175320, gazon_kleur = 138637810636041, gazon_normaal = 84279641416348, uitgangsboog_kleur = 98360375455954}
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
  natuursteen = true, vlonder = true, klinker = true, bord = true, ingangsbord = true, uitgangsbord = true, uitgangsboog = true, breuksteen = true,
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
local POORT_ALFA = {147.2727, 163.6364, 0.0000, -16.3636}       -- poorten.py: gondelhoek alfa
local DRAAI, BREED_POORT = 15.5615, 1.7
local HALF_POORT = math.deg((BREED_POORT + 0.1) / 2 / 8.3)
local function inpoort(alfa, r) local h = math.deg((BREED_POORT + 0.1) / 2 / r); for _, a in ipairs(POORT_ALFA) do if math.abs((alfa - a + 180) % 360 - 180) < h then return true end end; return false end
local HEKKEN = {{368.200, 58.786, 1.550, 366.492, 59.848, 1.550, 1.18}, {366.492, 59.848, 1.550, 364.649, 60.653, 1.550, 1.18}, {364.649, 60.653, 1.550, 362.709, 61.184, 1.550, 1.18}, {362.709, 61.184, 1.550, 360.713, 61.432, 1.550, 1.18}, {360.713, 61.432, 1.550, 358.702, 61.390, 1.550, 1.18}, {358.702, 61.390, 1.550, 356.719, 61.059, 1.550, 1.18}, {356.719, 61.059, 1.550, 354.803, 60.446, 1.550, 1.18}, {354.952, 60.719, 1.550, 354.794, 61.033, 1.450, 1.18}, {354.794, 61.033, 1.450, 354.305, 61.916, 1.300, 1.18}, {354.305, 61.916, 1.300, 353.786, 62.785, 1.150, 1.18}, {353.786, 62.785, 1.150, 353.237, 63.640, 1.000, 1.18}, {353.237, 63.640, 1.000, 352.658, 64.481, 0.850, 1.18}, {352.658, 64.481, 0.850, 352.050, 65.306, 0.700, 1.18}, {352.050, 65.306, 0.700, 351.413, 66.115, 0.550, 1.18}, {351.413, 66.115, 0.550, 350.747, 66.907, 0.400, 1.18}, {350.747, 66.907, 0.400, 350.052, 67.681, 0.250, 1.18}, {350.052, 67.681, 0.250, 349.330, 68.438, 0.100, 1.18}, {349.330, 68.438, 0.100, 348.580, 69.175, -0.050, 1.18}, {348.580, 69.175, -0.050, 348.194, 69.537, -0.050, 1.18}, {356.296, 64.859, -0.380, 355.221, 66.405, -0.380, 1.07}, {355.221, 66.405, -0.380, 353.526, 68.526, -0.380, 1.07}, {353.526, 68.526, -0.380, 351.254, 70.920, -0.380, 1.07}, {351.826, 61.394, 0.850, 350.162, 60.270, 0.850, 1.07}, {350.162, 60.270, 0.850, 348.651, 58.948, 0.850, 1.07}, {348.651, 58.948, 0.850, 347.316, 57.448, 0.850, 1.07}, {347.316, 57.448, 0.850, 346.177, 55.794, 0.850, 1.07}, {349.076, 61.957, 0.550, 347.333, 60.457, 0.550, 1.07}, {347.333, 60.457, 0.550, 345.794, 58.748, 0.550, 1.07}, {345.794, 58.748, 0.550, 344.483, 56.858, 0.550, 1.07}, {344.483, 56.858, 0.550, 343.423, 54.817, 0.550, 1.07}, {349.530, 64.681, 0.250, 347.839, 63.528, 0.250, 1.07}, {347.839, 63.528, 0.250, 346.273, 62.210, 0.250, 1.07}, {346.273, 62.210, 0.250, 344.849, 60.738, 0.250, 1.07}, {344.849, 60.738, 0.250, 343.582, 59.130, 0.250, 1.07}, {343.582, 59.130, 0.250, 342.485, 57.402, 0.250, 1.07}, {346.572, 65.078, -0.050, 344.872, 63.638, -0.050, 1.07}, {344.872, 63.638, -0.050, 343.326, 62.035, -0.050, 1.07}, {343.326, 62.035, -0.050, 341.948, 60.284, -0.050, 1.07}, {341.948, 60.284, -0.050, 340.754, 58.403, -0.050, 1.07}, {340.754, 58.403, -0.050, 339.755, 56.412, -0.050, 1.07}, {346.789, 67.680, -0.350, 344.863, 66.279, -0.350, 1.07}, {344.863, 66.279, -0.350, 343.085, 64.694, -0.350, 1.07}, {343.085, 64.694, -0.350, 341.471, 62.942, -0.350, 1.07}, {341.471, 62.942, -0.350, 340.039, 61.040, -0.350, 1.07}, {340.039, 61.040, -0.350, 338.801, 59.005, -0.350, 1.07}, {351.826, 61.394, 0.850, 351.085, 62.559, 0.700, 1.07}, {351.085, 62.559, 0.700, 350.515, 63.383, 0.550, 1.07}, {350.515, 63.383, 0.550, 349.916, 64.190, 0.400, 1.07}, {349.916, 64.190, 0.400, 349.289, 64.979, 0.250, 1.07}, {349.289, 64.979, 0.250, 348.634, 65.750, 0.100, 1.07}, {348.634, 65.750, 0.100, 347.952, 66.502, -0.050, 1.07}, {347.952, 66.502, -0.050, 347.242, 67.236, -0.200, 1.07}, {347.242, 67.236, -0.200, 346.506, 67.949, -0.350, 1.07}, {346.506, 67.949, -0.350, 346.166, 68.264, -0.350, 1.07}, {352.801, 59.565, 1.300, 350.829, 58.144, 1.300, 1.18}, {350.829, 58.144, 1.300, 349.132, 56.404, 1.300, 1.18}, {349.132, 56.404, 1.300, 347.759, 54.397, 1.300, 1.18}, {354.891, 59.996, 1.300, 354.720, 60.736, 1.300, 1.08}, {353.223, 59.176, 1.300, 352.741, 59.763, 1.300, 1.08}, {355.791, 58.985, 1.300, 357.483, 59.470, 1.300, 2.60}, {357.483, 59.470, 1.300, 357.913, 57.970, 1.300, 2.60}, {357.913, 57.970, 1.300, 356.221, 57.485, 1.300, 2.60}, {356.221, 57.485, 1.300, 355.791, 58.985, 1.300, 2.60}, {366.706, 39.009, 1.420, 368.355, 40.625, 1.420, 1.18}, {368.355, 40.625, 1.420, 369.624, 42.555, 1.420, 1.18}, {370.551, 45.102, 1.420, 370.815, 47.175, 1.420, 1.18}, {370.815, 47.175, 1.420, 370.676, 49.261, 1.420, 1.18}, {370.676, 49.261, 1.420, 370.138, 51.280, 1.420, 1.18}, {370.138, 51.280, 1.420, 369.222, 53.159, 1.420, 1.18}, {369.222, 53.159, 1.420, 367.963, 54.826, 1.420, 1.18}, {367.963, 54.826, 1.420, 366.406, 56.220, 1.420, 1.18}, {369.586, 42.787, 1.300, 372.405, 41.761, -0.380, 1.00}, {369.624, 42.555, 1.420, 369.586, 42.787, 1.300, 1.00}, {370.373, 44.948, 1.300, 373.192, 43.922, -0.380, 1.00}, {370.551, 45.102, 1.420, 370.373, 44.948, 1.300, 1.00}, {354.604, 54.907, 1.300, 352.288, 57.505, 1.300, 1.08}, {353.260, 53.709, 1.300, 350.944, 56.307, 1.300, 1.08}, {352.735, 53.087, 1.300, 349.782, 54.927, 1.300, 1.08}, {351.784, 51.559, 1.300, 348.830, 53.399, 1.300, 1.08}, {360.527, 65.242, -0.380, 359.462, 65.242, -0.380, 1.08}, {359.462, 65.242, -0.380, 358.400, 65.178, -0.380, 1.08}, {358.400, 65.178, -0.380, 357.343, 65.050, -0.380, 1.08}, {357.343, 65.050, -0.380, 356.296, 64.859, -0.380, 1.08}, {351.254, 70.920, -0.380, 350.571, 72.747, -0.380, 1.08}, {350.571, 72.747, -0.380, 349.617, 72.370, -0.380, 1.08}, {349.617, 72.370, -0.380, 348.678, 71.956, -0.380, 1.08}, {348.678, 71.956, -0.380, 347.755, 71.508, -0.380, 1.08}, {347.755, 71.508, -0.380, 346.851, 71.024, -0.380, 1.08}, {346.851, 71.024, -0.380, 345.965, 70.507, -0.380, 1.08}, {345.965, 70.507, -0.380, 345.099, 69.956, -0.380, 1.08}, {345.099, 69.956, -0.380, 344.255, 69.372, -0.380, 1.08}, {344.255, 69.372, -0.380, 343.434, 68.757, -0.380, 1.08}, {343.434, 68.757, -0.380, 342.637, 68.111, -0.380, 1.08}, {342.637, 68.111, -0.380, 341.865, 67.436, -0.380, 1.08}, {341.865, 67.436, -0.380, 341.119, 66.731, -0.380, 1.08}, {341.119, 66.731, -0.380, 340.401, 65.998, -0.380, 1.08}, {340.401, 65.998, -0.380, 339.711, 65.239, -0.380, 1.08}, {339.711, 65.239, -0.380, 339.051, 64.454, -0.380, 1.08}, {339.051, 64.454, -0.380, 338.421, 63.644, -0.380, 1.08}, {338.421, 63.644, -0.380, 337.822, 62.811, -0.380, 1.08}, {337.822, 62.811, -0.380, 337.255, 61.956, -0.380, 1.08}, {337.255, 61.956, -0.380, 336.721, 61.079, -0.380, 1.08}, {336.721, 61.079, -0.380, 336.221, 60.184, -0.380, 1.08}, {336.221, 60.184, -0.380, 335.756, 59.269, -0.380, 1.08}, {335.756, 59.269, -0.380, 335.325, 58.338, -0.380, 1.08}, {335.325, 58.338, -0.380, 337.132, 57.552, -0.350, 1.08}, {337.132, 57.552, -0.350, 338.012, 57.170, -0.350, 1.08}, {338.012, 57.170, -0.350, 338.049, 57.154, -0.200, 1.08}, {338.049, 57.154, -0.200, 338.929, 56.771, -0.200, 1.08}, {338.929, 56.771, -0.200, 338.966, 56.755, -0.050, 1.08}, {338.966, 56.755, -0.050, 339.846, 56.372, -0.050, 1.08}, {339.846, 56.372, -0.050, 339.883, 56.356, 0.100, 1.08}, {339.883, 56.356, 0.100, 340.763, 55.973, 0.100, 1.08}, {340.763, 55.973, 0.100, 340.800, 55.957, 0.250, 1.08}, {340.800, 55.957, 0.250, 341.681, 55.575, 0.250, 1.08}, {341.681, 55.575, 0.250, 341.717, 55.559, 0.400, 1.08}, {341.717, 55.559, 0.400, 342.598, 55.176, 0.400, 1.08}, {342.598, 55.176, 0.400, 342.634, 55.160, 0.550, 1.08}, {342.634, 55.160, 0.550, 343.515, 54.777, 0.550, 1.08}, {343.515, 54.777, 0.550, 343.551, 54.761, 0.700, 1.08}, {343.551, 54.761, 0.700, 344.432, 54.378, 0.700, 1.08}, {344.432, 54.378, 0.700, 344.468, 54.362, 0.850, 1.08}, {344.468, 54.362, 0.850, 345.349, 53.980, 0.850, 1.08}, {345.349, 53.980, 0.850, 345.386, 53.964, 1.000, 1.08}, {345.386, 53.964, 1.000, 346.266, 53.581, 1.000, 1.08}, {346.266, 53.581, 1.000, 346.303, 53.565, 1.150, 1.08}, {346.303, 53.565, 1.150, 347.183, 53.182, 1.150, 1.08}, {347.183, 53.182, 1.150, 347.156, 53.194, 1.300, 1.08}, {348.048, 69.401, -0.350, 346.166, 68.264, -0.350, 1.08}, {347.759, 54.397, 1.300, 347.156, 53.194, 1.300, 1.08}, {347.156, 53.194, 1.300, 351.727, 51.168, 1.300, 1.08}, {351.034, 48.728, 1.300, 349.399, 48.952, 1.300, 1.08}, {349.399, 48.952, 1.300, 349.301, 47.368, 1.300, 1.08}, {349.301, 47.368, 1.300, 349.438, 45.787, 1.300, 1.08}, {349.438, 45.787, 1.300, 349.808, 44.244, 1.300, 1.08}, {349.808, 44.244, 1.300, 350.401, 42.772, 1.300, 1.08}, {350.401, 42.772, 1.300, 351.206, 41.404, 1.300, 1.08}, {351.206, 41.404, 1.300, 352.205, 40.170, 1.300, 1.08}, {352.205, 40.170, 1.300, 353.375, 39.098, 1.300, 1.08}, {353.375, 39.098, 1.300, 354.690, 38.210, 1.300, 1.08}, {354.690, 38.210, 1.300, 356.123, 37.527, 1.300, 1.08}, {356.123, 37.527, 1.300, 357.641, 37.063, 1.300, 1.08}, {357.641, 37.063, 1.300, 359.211, 36.829, 1.300, 1.08}, {359.211, 36.829, 1.300, 360.798, 36.830, 1.300, 1.08}, {360.798, 36.830, 1.300, 362.367, 37.065, 1.300, 1.08}, {362.367, 37.065, 1.300, 363.885, 37.530, 1.300, 1.08}, {363.885, 37.530, 1.300, 365.317, 38.214, 1.300, 1.08}, {365.317, 38.214, 1.300, 366.632, 39.103, 1.300, 1.08}, {358.491, 56.423, 1.300, 358.224, 58.001, 1.300, 1.08}, {366.305, 56.083, 1.300, 364.855, 56.979, 1.300, 1.08}, {364.855, 56.979, 1.300, 363.280, 57.632, 1.300, 1.08}, {363.280, 57.632, 1.300, 361.622, 58.026, 1.300, 1.08}, {361.622, 58.026, 1.300, 359.922, 58.150, 1.300, 1.08}, {359.922, 58.150, 1.300, 358.224, 58.001, 1.300, 1.08}, {358.224, 58.001, 1.300, 357.632, 61.501, 1.300, 1.08}, {366.376, 56.341, -0.380, 368.306, 59.017, -0.380, 1.08}, {354.952, 60.719, 1.550, 355.018, 60.514, 1.550, 1.18}, {348.194, 69.537, -0.050, 348.048, 69.401, -0.050, 1.18}, {352.801, 59.565, 1.300, 352.862, 59.616, 1.300, 1.18}, {354.720, 60.736, 1.300, 354.898, 60.826, 1.300, 1.08}, {352.741, 59.763, 1.300, 352.801, 59.565, 1.300, 1.08}, {366.706, 39.009, 1.420, 366.632, 39.103, 1.420, 1.18}, {366.406, 56.220, 1.420, 366.305, 56.083, 1.420, 1.18}, {348.048, 69.401, -0.350, 348.194, 69.537, -0.350, 1.08}, {366.632, 39.103, 1.300, 366.715, 39.018, 1.300, 1.08}, {366.305, 56.083, 1.300, 366.418, 56.209, 1.300, 1.08}, {357.632, 61.501, 1.300, 357.679, 61.219, 1.300, 1.08}}
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
for i = 0, 255 do
  local a0, a1 = i / 256 * 2 * math.pi, (i + 1) / 256 * 2 * math.pi
  local p0, p1 = B(8.32 * math.cos(a0), 8.32 * math.sin(a0), 2.85).Position, B(8.32 * math.cos(a1), 8.32 * math.sin(a1), 2.85).Position
  deel(inpoort(math.deg(a0 + a1) / 2, 8.32) and "poortreling" or "reling", CFrame.lookAt((p0 + p1) / 2, p1), Vector3.new(0.6, 1.3 * S, (p1 - p0).Magnitude + 0.3), ONZ)
end
for _, p in ipairs(g:GetChildren()) do
  if p:IsA("BasePart") and string.match(p.Name, "^PG_kernwand") then p.CanCollide = true end
end
-- reling bakrand (station: r 8.95 rond (360, 47.5), instapniveau NAP 11.3), behalve bij de sleuf (164.4 +- 7.5 graden)
for i = 0, 287 do
  local a0, a1 = math.rad(i * 1.25), math.rad(i * 1.25 + 1.25)
  local m = (i * 1.25 + 0.625)
  if not (m > 156.9 and m < 171.9) then
    local function w(a) return Vector3.new((360 + 8.95 * math.cos(a)) * S, 2 + (1.3 + 0.55) * S, -(47.5 + 8.95 * math.sin(a)) * S) end
    local p0, p1 = w(a0), w(a1)
    deel(inpoort(m + DRAAI, 8.95) and "bakpoort" or "bakreling", CFrame.lookAt((p0 + p1) / 2, p1), Vector3.new(0.6, 1.1 * S, (p1 - p0).Magnitude + 0.3), ONZ)
  end
end

-- 2 ronde plafondlampjes (22, r 6.9, onder het plafond op z 4.58) met warm licht
for i = 0, 21 do
  local a = (i + 0.5) / 22 * 2 * math.pi
  local cf = B(6.9 * math.cos(a), 6.9 * math.sin(a), 4.57)
  local l = deel("plafondlamp", cf, Vector3.new(0.12 * S, 0.9 * S, 0.9 * S),
    {Shape = Enum.PartType.Cylinder, Material = Enum.Material.SmoothPlastic, Color = Color3.fromRGB(236, 220, 186), CanCollide = false, CanQuery = false})   -- mat, geen Neon: overbelichtte (Daan 17 nov)
  l.CFrame = cf * CFrame.Angles(0, 0, math.pi / 2)
  if i % 3 == 0 then   -- rijdende gondel = bewegend object zonder eigen schaduw: 8 zachte lichten met schaduw, anders lekt het licht naar buiten
    local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 190, 120); pl.Brightness = 0.12; pl.Range = 12; pl.Shadows = true; pl.Parent = l
  end
end

-- 3 lichtsnoeren langs de windveren (warm wit, Pagode-donker.jpg) en lampjes op de gevelpunten
local N, R, Z0, Z1 = 22, 8.4, 4.8, 6.8
local hw = math.pi * R / N
local LICHT = {Material = Enum.Material.Neon, Color = Color3.fromRGB(190, 150, 100), Transparency = 0.4, CanCollide = false, CanQuery = false}   -- getemperd (bloom)
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
local LAMPEN = {{351.98, 64.73, 3.32}, {349.33, 67.88, 2.72}, {351.79, 61.46, 4.13}, {350.46, 63.47, 3.83}, {349.43, 56.37, 4.22}, {370.20, 42.08, 2.57}}   -- = exports/omgeving_lampen.json
for i, l in ipairs(LAMPEN) do
  local p = Instance.new("Part"); p.Name = "lantaarnlicht"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
  p.Transparency = 1; p.Size = Vector3.new(0.3, 0.3, 0.3); p.Position = Vector3.new(l[1] * S, 2 + l[3] * S, -l[2] * S); p.Parent = map
  local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 128); pl.Brightness = 1.4; pl.Range = 18; pl.Shadows = true; pl.Parent = p
end


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
    for _, sz in ipairs({-1, 1}) do
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
-- klaphekjes in het stationshek (Daan 17 nov: "als de attractie omhoog is hoort niemand erdoor te kunnen; als hij er is gaan
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
      muziek = 1840841073,   -- APM "Fortune's Smiling" (wachtrij, gekozen door Daan met MuziekKiezer 6/12, 173 s)
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
    -- verstopte speaker (Daan 17 nov: "speakers kunnen een beetje weggestopt worden"): klein stenen kastje laag bij de voet van
    -- een lantaarnpaal, natuursteenkleur, alleen een donkere grille naar de wachtrij
    local function box(naam, voet, kijk)
      local dir = Vector3.new(kijk.X - voet.X, 0, kijk.Z - voet.Z).Unit
      local m = Instance.new("Model"); m.Name = naam; m.Parent = fg
      local function stuk(nm, cf, size, kleur, mat)
        local p = Instance.new("Part"); p.Name = nm; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
        p.Size = size; p.Color = kleur; p.Material = mat; p.CFrame = cf; p.Parent = m; return p
      end
      local c = CFrame.lookAt(voet, voet + dir) * CFrame.new(0, 0.3, -0.55) * CFrame.Angles(math.rad(12), 0, 0)
      local k = stuk("kast", c, Vector3.new(0.95, 0.7, 0.75), Color3.fromRGB(122, 112, 100), Enum.Material.Slate)
      stuk("grill", c * CFrame.new(0, 0.02, -0.38), Vector3.new(0.6, 0.42, 0.03), Color3.fromRGB(34, 34, 32), Enum.Material.DiamondPlate)
      m.PrimaryPart = k
      return k
    end
    -- speakers bij de voet van de lantaarnpalen langs de wachtrij (exports/omgeving_lampen.json: x, y, z van de kap);
    -- grond onder de paal via een straal omlaag naast de paal, kastje richting de wachtrij (het stationsmidden)
    local LAMPEN = {{351.98, 64.73, 3.32}, {349.33, 67.88, 2.72}, {351.79, 61.46, 4.13}, {350.46, 63.47, 3.83}, {349.43, 56.37, 4.22}}
    local rpG = RaycastParams.new(); rpG.FilterType = Enum.RaycastFilterType.Include
    rpG.FilterDescendantsInstances = {workspace:FindFirstChild("PagodeOmgeving"), workspace:FindFirstChild("PagodeStation"), workspace.Terrain}
    local VLOER = {klinker = true, graniet = true, natuursteen = true, vlonder = true, breuksteen = true, steen = true, voeg = true, beton_groen = true, grind = true}
    local function grond(van)          -- eerste vloer onder een punt (lantaarnkap, reling en hekken overslaan)
      local o = van
      for _ = 1, 10 do
        local h = workspace:Raycast(o, Vector3.new(0, -25, 0), rpG)
        if not h then return nil end
        local rol = h.Instance:IsA("Terrain") and "terrein" or string.match(h.Instance.Name, "^PG_(.-)_%d+")
        if rol == "terrein" or VLOER[rol] then return h.Position.Y end
        o = h.Position - Vector3.new(0, 0.05, 0)
      end
    end
    for i, l in ipairs(LAMPEN) do
      local kop = Vector3.new(l[1] * S, 2 + l[3] * S, -l[2] * S)
      local naar = Vector3.new(360 * S - kop.X, 0, -47.5 * S - kop.Z).Unit
      local gy = grond(kop + naar * 0.9 + Vector3.new(0, 3, 0))
      local voet = Vector3.new(kop.X, gy or kop.Y - 9.6, kop.Z)
      local sp = box("speaker" .. i, voet, kop + naar * 10)
      local so = snd(sp, "muziek", GELUID.muziek, 0.4, 4, 50, true)        -- realistisch: 1/afstand vanaf 1.3 m, stil na ~17 m
      so.RollOffMode = Enum.RollOffMode.Inverse; so.Playing = true
    end
    -- machinegeluid bij de draaias van de arm en de cilinders; bel en hekjes bij het station
    local as = Instance.new("Part"); as.Name = "machine"; as.Anchored = true; as.CanCollide = false; as.CanQuery = false; as.CanTouch = false
    as.Transparency = 1; as.Size = Vector3.new(1, 1, 1); as.CFrame = PIV; as.Parent = fg
    snd(as, "brom", GELUID.brom, 0, 20, 160, true)
    local st0 = Instance.new("Part"); st0.Name = "station"; st0.Anchored = true; st0.CanCollide = false; st0.CanQuery = false; st0.CanTouch = false
    st0.Transparency = 1; st0.Size = Vector3.new(1, 1, 1); st0.Position = W(9.3, math.rad(140), 12.5); st0.Parent = fg
    snd(st0, "bel", GELUID.bel, 0.45, 12, 110, false)
    snd(st0, "hek", GELUID.hek, 0.4, 8, 60, false)
    -- geroezemoes: wachtende mensen (PSE walla), drie bronnen, hoorbaar tot ~20 m
    for _, w in ipairs({{"tribune", 20.0, 136, 0.6, 9112787259, 0.22}, {"laantje", 18.0, 108, -0.38, 9112766358, 0.18}, {"bordes", 12.6, 132, 1.3, 9112766358, 0.15}}) do
      local p = Instance.new("Part"); p.Name = "praten_" .. w[1]; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
      p.Transparency = 1; p.Size = Vector3.new(1, 1, 1); p.Position = W(w[2], math.rad(w[3]), 10 + w[4] + 1.2); p.Parent = fg
      local so = snd(p, "praten", w[5], w[6], 8, 60, true); so.Playing = true
      if w[1] == "bordes" then so.TimePosition = 17 end
    end
    -- zacht lopende en pratende mensen (PSE street crowd: walla, voetstappen, kinderen, vogels, geen verkeer)
    for _, w in ipairs({{"aanloop", 16.3, 95, -0.38, 9112879470, 0.16, 0}, {"onderpad", 26.0, 135, -0.38, 9112879448, 0.14, 11}}) do
      local p = Instance.new("Part"); p.Name = "lopen_" .. w[1]; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
      p.Transparency = 1; p.Size = Vector3.new(1, 1, 1); p.Position = W(w[2], math.rad(w[3]), 10 + w[4] + 1.0); p.Parent = fg
      local so = snd(p, "lopen", w[5], w[6], 8, 55, true); so.Playing = true; so.TimePosition = w[7]
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
end
-- onzichtbare botsing langs alle hekken en relingen (12_omgeving / 18_route -> exports/omgeving_hekken.json)
do
  -- onzichtbare muren tot 24 studs boven de vloer: niet over hekken springen, je MOET de route volgen (Daan 17 nov).
  -- Groep Routemuur botst niet met Rijdend (wie meerijdt, zie PagodeRitClient): de gondel zwaait door de stationshekken.
  local PS = game:GetService("PhysicsService")
  for _, g in ipairs({"Routemuur", "Rijdend"}) do if not PS:IsCollisionGroupRegistered(g) then PS:RegisterCollisionGroup(g) end end
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
-- interieur gondel (Daan 17 nov: "kan de Pagode van binnen meer detail hebben"; video instappen + Pagode-binnenzijde):
-- witte zitrand rondom de kern, gouden randen om de plafondlampen, mintgroene bordjes met gouden lijst op de kernwand
-- (UITGANG bij de uitstappoortjes). Alles in Gondel.Interieur: beweegt mee (PagodeRitClient verplaatst alle gondeldelen).
do
  local gondel = workspace.Pagode.Gondel
  local K = gondel.Kern.CFrame
  local oudI = gondel:FindFirstChild("Interieur"); if oudI then oudI:Destroy() end
  local map = Instance.new("Folder"); map.Name = "Interieur"; map.Parent = gondel
  local DEK, R_KERN = 6.6, 16.2
  local function deel(naam, cf, size, kleur, mat, botst)
    local p = Instance.new("Part"); p.Name = naam; p.Anchored = true; p.CanCollide = botst; p.CanTouch = false; p.CanQuery = botst
    p.Size = size; p.Color = kleur; p.Material = mat; p.CFrame = cf; p.TopSurface = Enum.SurfaceType.Smooth; p.Parent = map; return p
  end
  -- 1 witte zitrand: 48 gebogen stukken, 1.5 studs diep, 1.35 hoog (0.45 m), met een smalle bovenrand
  local N = 48
  for i = 0, N - 1 do
    local t = (i + 0.5) / N * 2 * math.pi
    local r = R_KERN + 0.75
    local L = 2 * math.pi * r / N + 0.15
    local c = K * CFrame.new(r * math.cos(t), DEK + 0.675, r * math.sin(t)) * CFrame.Angles(0, -t, 0)
    deel("zitrand", c, Vector3.new(1.5, 1.35, L), Color3.fromRGB(236, 232, 222), Enum.Material.SmoothPlastic, true)
    deel("zitrandkap", K * CFrame.new((r + 0.1) * math.cos(t), DEK + 1.4, (r + 0.1) * math.sin(t)) * CFrame.Angles(0, -t, 0),
      Vector3.new(1.75, 0.12, L), Color3.fromRGB(246, 244, 238), Enum.Material.SmoothPlastic, false)
  end
  -- 2 gouden rand om elke plafondlamp
  for _, p in ipairs(gondel:GetDescendants()) do
    if p:IsA("BasePart") and p.Name == "plafondlamp" then
      local ring = deel("lamprand", p.CFrame * CFrame.new(0.03, 0, 0), Vector3.new(p.Size.X * 0.6, p.Size.Y + 0.5, p.Size.Z + 0.5),
        Color3.fromRGB(205, 160, 70), Enum.Material.Metal, false)
      ring.Shape = Enum.PartType.Cylinder; ring.Reflectance = 0.1
    end
  end
  -- 3 bordjes op de kernwand (mintgroen, gouden lijst); kernhoek = 180 - gondelhoek alfa
  local function bord(theta, regel1, regel2)
    local t = math.rad(theta)
    local r = R_KERN + 0.08
    local c = K * CFrame.new(r * math.cos(t), DEK + 6.2, r * math.sin(t)) * CFrame.Angles(0, -t - math.pi / 2, 0)
    deel("bordlijst", c, Vector3.new(4.6, 2.0, 0.12), Color3.fromRGB(205, 160, 70), Enum.Material.Metal, false)
    local b = deel("bord", c * CFrame.new(0, 0, -0.08), Vector3.new(4.2, 1.6, 0.08), Color3.fromRGB(150, 205, 180), Enum.Material.SmoothPlastic, false)
    local sg = Instance.new("SurfaceGui"); sg.Face = Enum.NormalId.Front; sg.CanvasSize = Vector2.new(420, 160); sg.LightInfluence = 0.6; sg.Parent = b
    local t1 = Instance.new("TextLabel"); t1.BackgroundTransparency = 1; t1.Size = UDim2.new(1, 0, 0.62, 0); t1.Font = Enum.Font.Bodoni
    t1.TextScaled = true; t1.TextColor3 = Color3.fromRGB(28, 70, 52); t1.Text = regel1; t1.AutoLocalize = false; t1.Parent = sg
    local t2 = Instance.new("TextLabel"); t2.BackgroundTransparency = 1; t2.Position = UDim2.new(0, 0, 0.62, 0); t2.Size = UDim2.new(1, 0, 0.3, 0)
    t2.Font = Enum.Font.Bodoni; t2.TextScaled = true; t2.TextColor3 = Color3.fromRGB(28, 70, 52); t2.Text = regel2; t2.AutoLocalize = false; t2.Parent = sg
  end
  bord(188, "UITGANG", "Exit · Ausgang · Sortie")        -- tussen uit0 (180) en uit1 (196)
  bord(24.5, "PAGODE", "Efteling · 1987")                  -- tussen in1 (16) en in0 (33)
  bord(106, "PAGODE", "Efteling · 1987")
  bord(286, "PAGODE", "Efteling · 1987")
end

-- botsrand van de groene balustrade opnieuw t.o.v. de kern (Daan 17 nov: "ik kan door de groene hekjes"): de reling-delen uit
-- de afwerking stonden ~120 studs te hoog (oud draaipunt van de gondel). 256 stukken op r 8.32 m vanaf het dek, 24 studs hoog;
-- in de poortjes (kernhoek = 180 - gondelhoek alfa) heten ze poortreling en wisselen ze met de hekjes (PagodeRitClient)
do
  for _, p in ipairs(gondel:GetDescendants()) do if p:IsA("BasePart") and (p.Name == "reling" or p.Name == "poortreling") then p:Destroy() end end
  local K = kern.CFrame
  local oudR = gondel:FindFirstChild("Randbotsing"); if oudR then oudR:Destroy() end
  local map = Instance.new("Folder"); map.Name = "Randbotsing"; map.Parent = gondel
  local HALF = math.deg((BREED_POORT + 0.1) / 2 / 8.32)
  local R, Y0, H, N = 8.32 * S, 6.58, 24, 256
  local function inpoort2(t) for _, a in ipairs(POORT_ALFA) do if math.abs((t - (180 - a) + 180) % 360 - 180) < HALF then return true end end return false end
  for i = 0, N - 1 do
    local t0, t1 = i / N * 2 * math.pi, (i + 1) / N * 2 * math.pi
    local p0 = K:PointToWorldSpace(Vector3.new(R * math.cos(t0), Y0 + H / 2, R * math.sin(t0)))
    local p1 = K:PointToWorldSpace(Vector3.new(R * math.cos(t1), Y0 + H / 2, R * math.sin(t1)))
    local p = Instance.new("Part"); p.Name = inpoort2(math.deg((t0 + t1) / 2)) and "poortreling" or "reling"
    p.Anchored = true; p.Transparency = 1; p.CanCollide = true; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
    p.Size = Vector3.new(0.6, H, (p1 - p0).Magnitude + 0.3)
    p.CFrame = CFrame.lookAt((p0 + p1) / 2, p1, K.UpVector); p.Parent = map
  end
end
-- ritscript
local sc = Instance.new("Script"); sc.Name = "PagodeRit"; sc.Source = [==[--!strict
-- PagodeRit (server): stuurt alleen de ritklok (attribuut RitStart, servertijd). De beweging zelf draait op elke client
-- (PagodeRitClient.client.luau, StarterPlayerScripts) met workspace:GetServerTimeNow(): iedereen ziet dezelfde stand,
-- zonder netwerkvertraging. Daan 17 nov: de server-gestuurde gondel trilde, belichting bleekte uit (losse physics-delen) en
-- spelers zakten weg. Nu blijft alles verankerd.
-- Wachten op passagiers (Daan 17 nov: "op het begin haal ik het niet om op de Pagode te komen"): zolang er niemand op het
-- dek staat, houdt de server de klok vast op WACHT_TC (instappen, hekjes open). Stapt er iemand in, dan loopt de klok door:
-- nog T_IN - WACHT_TC seconden instappen, dan sluiten en de rit. Fasen moeten gelijk zijn aan PagodeRitClient.
local Players = game:GetService("Players")

local S = 3
local T_IN = 60                                -- = PagodeRitClient T_IN
local WACHT_TC = 40                            -- hier wacht hij (uitstappers hebben dan 40 s gehad); daarna nog 20 s
local CYCLUS = T_IN + 5 + 55 + 200 + 55        -- = som van FASEN in PagodeRitClient
local MIDDEN = Vector3.new(360.0 * S, 0, -47.5 * S)
local Y_DEK = 2 + 1.3 * S                      -- instapniveau (NAP 11.3)
local R_DEK = 8.2 * S                          -- binnen de groene rand van de gondel

local pag = workspace:WaitForChild("Pagode") :: Model
pag:SetAttribute("RitStart", workspace:GetServerTimeNow())

local function iemandAanBoord(): boolean
	for _, plr in Players:GetPlayers() do
		local ch = plr.Character
		local hrp = ch and ch:FindFirstChild("HumanoidRootPart") :: BasePart?
		local hum = ch and ch:FindFirstChildOfClass("Humanoid")
		if hrp and hum and hum.Health > 0 then
			local p = hrp.Position
			local r = (Vector3.new(p.X, 0, p.Z) - MIDDEN).Magnitude
			if r < R_DEK and p.Y > Y_DEK and p.Y < Y_DEK + 9 then return true end
		end
	end
	return false
end

while true do
	task.wait(0.25)
	local nu = workspace:GetServerTimeNow()
	local start = pag:GetAttribute("RitStart") :: number
	local tc = (nu - start) % CYCLUS
	if tc >= WACHT_TC and tc < WACHT_TC + 1 and not iemandAanBoord() then
		pag:SetAttribute("RitStart", nu - WACHT_TC)          -- klok vasthouden: hekjes blijven open tot er iemand instapt
	end
	pag:SetAttribute("Wacht", tc >= WACHT_TC and tc < WACHT_TC + 1)
end
]==]; sc.Parent = game:GetService("ServerScriptService")
local sps = game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts")
local oudC = sps:FindFirstChild("PagodeRitClient"); if oudC then oudC:Destroy() end
local lc = Instance.new("LocalScript"); lc.Name = "PagodeRitClient"; lc.Source = [==[--!strict
-- PagodeRitClient (StarterPlayerScripts): laat de Pagode rijden op deze client.
-- Ritverloop naar de on-ride video _Wz0aORIVaM en de echte ritduur 5:10 (coaster.cloud): instappen 60 s (Daan), sluiten 5 s, omhoog 55 s, boven 200 s,
-- omlaag 55 s; twee volle draaien over de rit. De arm draait om de draaias (AsFrame, lokale Z-as), de gondel blijft waterpas.
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
local poorten = gondel:WaitForChild("Poorten")
local gDelen, gRel = {}, {}
for _, p in gondel:GetDescendants() do
	if p:IsA("BasePart") and not p:IsDescendantOf(poorten) then p.Anchored = true; table.insert(gDelen, p); table.insert(gRel, K0:ToObjectSpace(p.CFrame)) end
end
-- klaphekjes: per blad een scharnier (t.o.v. de kern) en de delen t.o.v. het scharnier; draaien naar binnen open bij het instappen
type Blad = {sch: CFrame, teken: number, delen: {BasePart}, rel: {CFrame}}
local bladen: {Blad} = {}
for _, f in poorten:GetChildren() do
	local b: Blad = {sch = f:GetAttribute("Scharnier") :: CFrame, teken = f:GetAttribute("Teken") :: number, delen = {}, rel = {}}
	for _, p in f:GetChildren() do
		if p:IsA("BasePart") then table.insert(b.delen, p); table.insert(b.rel, p:GetAttribute("Rel") :: CFrame) end
	end
	table.insert(bladen, b)
end
local A0 = PIV
local aDelen, aRel = {}, {}
for _, p in arm:GetDescendants() do
	if p:IsA("BasePart") then p.Anchored = true; table.insert(aDelen, p); table.insert(aRel, A0:ToObjectSpace(p.CFrame)) end
end
-- botsing die met de poortjes meewisselt: reling in de poortopening (gondel), bakrand in de opening (station), dichte bladen
local poortBots: {BasePart} = {}
for _, p in gDelen do if p.Name == "poortreling" then table.insert(poortBots, p) end end
local st = pag:FindFirstChild("Station")
if st then for _, p in st:GetDescendants() do if p:IsA("BasePart") and p.Name == "bakpoort" then table.insert(poortBots, p) end end end
-- klaphekjes in het stationshek (maak_ritscript: Station.Stationpoorten), scharnier in wereldcoordinaten
local stBladen: {Blad} = {}
local stMap = st and st:FindFirstChild("Stationpoorten")
if stMap then
	for _, f in stMap:GetChildren() do
		local b: Blad = {sch = f:GetAttribute("Scharnier") :: CFrame, teken = f:GetAttribute("Teken") :: number, delen = {}, rel = {}}
		for _, p in f:GetChildren() do
			if p:IsA("BasePart") then table.insert(b.delen, p); table.insert(b.rel, p:GetAttribute("Rel") :: CFrame) end
		end
		table.insert(stBladen, b)
	end
end
local bladBots: {BasePart} = {}
for _, b in bladen do for _, p in b.delen do if p.Name == "poortblad" then table.insert(bladBots, p) end end end
for _, b in stBladen do for _, p in b.delen do if p.Name == "poortblad" then table.insert(bladBots, p) end end end

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

local T_IN = 60                                       -- instappen: hekjes open (Daan 17 nov: "doe maar zestig")
local FASEN = {{"instappen", T_IN}, {"sluiten", 5}, {"omhoog", 55}, {"boven", 200}, {"omlaag", 55}}
local CYCLUS, T_RIT = 0, 55 + 200 + 55
local RONDJES = 2                                   -- twee hele rondjes per rit (Daan: "moet hij niet wat draaien"); heel getal: poortjes eindigen weer voor het station
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
			if naam == "omhoog" or naam == "boven" or naam == "omlaag" then phi = RONDJES * 2 * math.pi * e((t_rit + tc - t0) / T_RIT) end
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
local eenrichting = pag:FindFirstChild("Eenrichting")
local schotT = eenrichting and eenrichting:FindFirstChild("tourniquet") :: BasePart?
local schotU = eenrichting and eenrichting:FindFirstChild("uitgang") :: BasePart?
local voorbijT, voorbijU = false, true
-- geluid (maak_ritscript: Pagode.Geluid): machinebrom volgt de armsnelheid, bel bij vertrek, hekjes bij open/dicht, wind hoog
local geluid = pag:FindFirstChild("Geluid")
local brom = geluid and geluid:FindFirstChild("machine") and geluid.machine:FindFirstChild("brom") :: Sound?
local bel = geluid and geluid:FindFirstChild("station") and geluid.station:FindFirstChild("bel") :: Sound?
local hekG = geluid and geluid:FindFirstChild("station") and geluid.station:FindFirstChild("hek") :: Sound?
local wind = geluid and geluid:FindFirstChild("wind") :: Sound?
if brom then brom:Play() end
if wind then wind:Play() end
local vorigeFase, vorigOpen, thVorig = "", false, TH_D
local huidigeGroep = "Default"
plr.CharacterAdded:Connect(function() huidigeGroep = "Default" end)
local cfs = table.create(#gDelen)
local acfs = table.create(#aDelen)

RunService.PreSimulation:Connect(function(dtF: number)
	local start = pag:GetAttribute("RitStart") :: number?
	if not start then return end
	local tc = (workspace:GetServerTimeNow() - start) % CYCLUS
	local th, phi, naam = stand(tc)
	local A = PIV * CFrame.Angles(0, 0, th)
	local nieuwK = CFrame.new(Jw(th) + schuif(th)) * PIV.Rotation * CFrame.Angles(0, phi, 0)
	-- speler op het dek: meenemen met de verplaatsing van de gondel
	local ch = plr.Character
	local hrp = ch and ch:FindFirstChild("HumanoidRootPart") :: BasePart?
	-- alleen als de gondel echt beweegt: elk frame de CFrame zetten (ook bij stilstand) blokkeert het lopen op het dek
	local delta = gK:ToObjectSpace(nieuwK)
	local _, draai = delta:ToAxisAngle()
	local beweegt = delta.Position.Magnitude > 1e-5 or math.abs(draai) > 1e-7   -- ook de langzame draai (twee rondjes) telt mee
	local rijdt = false
	if hrp and beweegt then
		local r = workspace:Raycast(hrp.Position, Vector3.new(0, -6, 0), ray)
		if r then hrp.CFrame = (nieuwK * gK:Inverse()) * hrp.CFrame; rijdt = true end
	end
	-- wie meerijdt botst niet met de onzichtbare routemuren (de gondel zwaait door de stationshekken)
	local groep = rijdt and "Rijdend" or "Default"
	if ch and groep ~= huidigeGroep then
		for _, p in ch:GetDescendants() do if p:IsA("BasePart") then p.CollisionGroup = groep end end
		huidigeGroep = groep
	end
	for i, rel in gRel do cfs[i] = nieuwK * rel end
	workspace:BulkMoveTo(gDelen, cfs, Enum.BulkMoveMode.FireCFrameChanged)
	for i, rel in aRel do acfs[i] = A * rel end
	workspace:BulkMoveTo(aDelen, acfs, Enum.BulkMoveMode.FireCFrameChanged)
	for _, c in cils do
		local k = A:PointToWorldSpace(c.kop); local u = (k - c.voet).Unit
		staaf(c.huis, c.voet, u, c.Lh); staaf(c.stang, k, -u, c.Ls)
	end
	-- klaphekjes: 2 s open aan het begin van het instappen, 2 s dicht aan het eind (instappen = eerste fase, tc 0..T_IN)
	local open = 0
	if naam == "instappen" then open = math.clamp(math.min(tc / 2, (T_IN - tc) / 2), 0, 1) end
	local hoek = math.rad(85) * e(open)
	for _, b in bladen do
		local scharnier = nieuwK * b.sch * CFrame.Angles(0, b.teken * hoek, 0)
		for i, p in b.delen do p.CFrame = scharnier * b.rel[i] end
	end
	for _, b in stBladen do                        -- stationshekjes: vast in de wereld, gaan tegelijk open
		local scharnier = b.sch * CFrame.Angles(0, b.teken * hoek, 0)
		for i, p in b.delen do p.CFrame = scharnier * b.rel[i] end
	end
	local dicht = open < 0.5
	for _, p in poortBots do p.CanCollide = dicht end
	for _, p in bladBots do p.CanCollide = dicht end
	-- eenrichting: een schot is alleen dicht als je er al voorbij bent (niet terug door de tourniquets, niet terug de uitgang op)
	if hrp and eenrichting then
		local x, y = hrp.Position.X / S - 360, -hrp.Position.Z / S - 47.5
		local r, a = math.sqrt(x * x + y * y), math.deg(math.atan2(y, x))
		-- schakelaar: dicht zodra je voorbij bent, pas weer open als je echt aan de goede kant terug bent (teleport/respawn)
		if r < 12.9 and a > 95 and a < 160 then voorbijT = true elseif r > 14.2 or a < 90 or a > 165 then voorbijT = false end
		-- uitgang: standaard dicht (ook niet van buitenaf de uitgang op), alleen open als je boven op de vlonder staat
		if r > 11.6 then voorbijU = true elseif r < 10.6 and a > -40 and a < 0 then voorbijU = false end
		if schotT then schotT.CanCollide = voorbijT end
		if schotU then schotU.CanCollide = voorbijU end
	end
	-- geluid
	local snel = math.abs(th - thVorig) / math.max(dtF, 1 / 240)                      -- hoeksnelheid arm (rad/s)
	thVorig = th
	if brom then
		local doel = math.clamp(snel / 0.05, 0, 1)                                     -- 0.05 rad/s = volle beweging
		brom.Volume = brom.Volume + (0.5 * doel - brom.Volume) * 0.05
		brom.PlaybackSpeed = 0.55 + 0.25 * doel
	end
	if naam ~= vorigeFase then
		if naam == "sluiten" and bel then bel:Play() end
		vorigeFase = naam
	end
	local nuOpen = open > 0.02
	if nuOpen ~= vorigOpen and hekG then hekG:Play() end
	vorigOpen = nuOpen
	if wind then
		local hoog = rijdt and math.clamp((nieuwK.Position.Y - K0.Position.Y) / 90, 0, 1) or 0
		wind.Volume = wind.Volume + (0.3 * hoog - wind.Volume) * 0.03
	end
	gK = nieuwK
	pag:SetAttribute("FaseLokaal", naam)
end)
]==]; lc.Parent = sps
for _, n in ipairs({"Voetstappen", "MuziekKiezer", "PagodeBeleving"}) do local o = sps:FindFirstChild(n); if o then o:Destroy() end end
local lv = Instance.new("LocalScript"); lv.Name = "Voetstappen"; lv.Source = [==[--!strict
-- Voetstappen (StarterPlayerScripts): het standaard loopgeluid (RbxCharacterSounds, Sound "Running" in de HumanoidRootPart)
-- krijgt een opname die bij de ondergrond past (Daan 17 nov: "mijn loop sound moet realistischer"). Ondergrond via een
-- straal omlaag: rol van het Pagode-onderdeel (PG_<rol>_n) of het terreinmateriaal (gras).
local Players = game:GetService("Players")
local STAP = {
	steen = "rbxassetid://91557584218550",   -- "Brick Footsteps": klinkers, natuursteen, graniet, beton
	hout = "rbxassetid://6506537704",        -- "Floor Footsteps": vlonder, gondeldek
	metaal = "rbxassetid://6362185620",      -- "Concrete Footsteps": roosters, staal
	gras = "rbxassetid://106672010112184",   -- "walk_grass": terrein (Roblox-standaard klinkt als plastic)
}
local ROL = {klinker = "steen", natuursteen = "steen", breuksteen = "steen", graniet = "steen", voeg = "steen", steen = "steen",
	beton_groen = "steen", beton_groen_licht = "steen", beton_licht = "steen", asfalt = "steen", grind = "steen",
	vlonder = "hout", dek = "hout", rooster = "metaal", staal = "metaal"}
local plr = Players.LocalPlayer
local ray = RaycastParams.new(); ray.FilterType = Enum.RaycastFilterType.Exclude

local function soort(hit: RaycastResult?): string?
	if not hit then return nil end
	local inst = hit.Instance
	if inst:IsA("Terrain") then return hit.Material == Enum.Material.Grass and "gras" or "steen" end
	local rol = string.match(inst.Name, "^PG_(.-)_%d+")
	return rol and ROL[rol] or "steen"
end

local function volg(ch: Model)
	local hrp = ch:WaitForChild("HumanoidRootPart", 10) :: BasePart?
	if not hrp then return end
	local run = hrp:WaitForChild("Running", 10) :: Sound?
	if not run then return end
	local standaard = run.SoundId
	ray.FilterDescendantsInstances = {ch}
	local huidig = ""
	while ch.Parent do
		local s = soort(workspace:Raycast(hrp.Position, Vector3.new(0, -6, 0), ray))
		local id = s and STAP[s] or standaard
		if id ~= huidig then run.SoundId = id; huidig = id end
		task.wait(0.15)
	end
end
plr.CharacterAdded:Connect(volg)
if plr.Character then task.spawn(volg, plr.Character) end
]==]; lv.Parent = sps
local lm = Instance.new("LocalScript"); lm.Name = "MuziekKiezer"; lm.Source = [==[--!strict
-- MuziekKiezer (StarterPlayerScripts, alleen in Studio): druk M om de wachtrijmuziek op alle Pagode-speakers te wisselen,
-- naam linksboven. Alleen lokaal; de gekozen ID daarna vastzetten in maak_ritscript (GELUID.muziek).
local RunService = game:GetService("RunService")
if not RunService:IsStudio() then return end
local UIS = game:GetService("UserInputService")
local LIJST = {
	{"Fortune's Smiling (gekozen)", 1840841073}, {"One World (a)", 1839842602}, {"Cultures And Colours (A)", 1840397475}, {"World Of Wonder", 1836330626},
	{"The Legend of the Monkey King", 1837190707}, {"Kawachi Ondo (c)", 1842506077},
	{"Lightly Magical", 1837777641}, {"Fairy Doll", 1846356693}, {"The Carousel Waltz", 132619984017094},
	{"Outward Bound", 1842179736}, {"Plum Blossoms", 1845854732}, {"Peach Blossom Spring", 1840540291},
}
local gui = Instance.new("ScreenGui"); gui.Name = "MuziekKiezer"; gui.ResetOnSpawn = false
local lab = Instance.new("TextLabel"); lab.Size = UDim2.fromOffset(460, 34); lab.Position = UDim2.fromOffset(12, 12)
lab.BackgroundTransparency = 0.35; lab.BackgroundColor3 = Color3.fromRGB(20, 20, 24); lab.TextColor3 = Color3.new(1, 1, 1)
lab.Font = Enum.Font.GothamMedium; lab.TextSize = 16; lab.TextXAlignment = Enum.TextXAlignment.Left; lab.Parent = gui
gui.Parent = game.Players.LocalPlayer:WaitForChild("PlayerGui")
local pag = workspace:WaitForChild("Pagode"); local g = pag:WaitForChild("Geluid")
local i = 1
local function zet()
	local naam, id = LIJST[i][1], LIJST[i][2]
	for _, s in g:GetDescendants() do
		if s:IsA("Sound") and s.Name == "muziek" then s.SoundId = "rbxassetid://" .. id; s.TimePosition = 0; s:Play() end
	end
	lab.Text = string.format("  Muziek %d/%d: %s  (%d)   [M = volgende]", i, #LIJST, naam, id)
end
UIS.InputBegan:Connect(function(inp, bezet)
	if bezet or inp.KeyCode ~= Enum.KeyCode.M then return end
	i = i % #LIJST + 1; zet()
end)
task.wait(2); zet()
]==]; lm.Parent = sps
local lb = Instance.new("LocalScript"); lb.Name = "PagodeBeleving"; lb.Source = [==[--!strict
-- PagodeBeleving (StarterPlayerScripts): tekst in beeld voor wie op de gondel staat (Daan 17 nov: "gewoon in het beeld,
-- iets vets en natuurlijk, in het Engels en dan vertalen"). Bij het instappen een titel: groot PAGODE in goudkleurige
-- schreefletters met daaronder "Welcome aboard"; vlak voor vertrek "Gates closing"; na de rit "Exit: follow the signs".
-- Teksten zijn Engels; de vertaling (nl) staat in LocalizationService.PagodeTeksten (maak_ritscript), Roblox vertaalt
-- automatisch naar de taal van de speler (AutoLocalize). Leest Pagode.FaseLokaal en Gondel.Kern; verandert niets aan de rit.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local S = 3
local pag = workspace:WaitForChild("Pagode") :: Model
local kern = (pag:WaitForChild("Gondel") :: Model):WaitForChild("Kern") :: BasePart
local plr = Players.LocalPlayer

local GOUD = Color3.fromRGB(232, 196, 120)
local gui = Instance.new("ScreenGui"); gui.Name = "PagodeOmroep"; gui.ResetOnSpawn = false; gui.IgnoreGuiInset = true

local function label(tekst: string, font: Enum.Font, grootte: number, y: number, kleur: Color3): TextLabel
	local l = Instance.new("TextLabel"); l.AnchorPoint = Vector2.new(0.5, 0.5); l.Position = UDim2.new(0.5, 0, y, 0)
	l.Size = UDim2.new(1, 0, 0, grootte + 8); l.BackgroundTransparency = 1; l.Font = font; l.TextSize = grootte
	l.TextColor3 = kleur; l.TextStrokeColor3 = Color3.new(0, 0, 0); l.TextStrokeTransparency = 1; l.TextTransparency = 1
	l.Text = tekst; l.Parent = gui
	return l
end
-- titel (eigennaam, niet vertalen) en onderregel; korte meldingen onderin
local titel = label("P A G O D E", Enum.Font.Bodoni, 64, 0.30, GOUD); titel.AutoLocalize = false
local onder = label("Welcome aboard", Enum.Font.Bodoni, 26, 0.30 + 0.075, Color3.fromRGB(250, 244, 230))
local melding = label("", Enum.Font.SourceSansSemibold, 24, 0.84, Color3.new(1, 1, 1))
gui.Parent = plr:WaitForChild("PlayerGui")

local volg = 0
local function toon(labels: {TextLabel}, duur: number)
	volg += 1; local mijn = volg
	for k, l in labels do
		local inn = TweenInfo.new(1.2, Enum.EasingStyle.Sine, Enum.EasingDirection.Out, 0, false, (k - 1) * 0.5)
		TweenService:Create(l, inn, {TextTransparency = 0, TextStrokeTransparency = 0.75}):Play()
	end
	task.delay(duur, function()
		if mijn ~= volg then return end
		for _, l in labels do
			TweenService:Create(l, TweenInfo.new(1.0, Enum.EasingStyle.Sine, Enum.EasingDirection.In), {TextTransparency = 1, TextStrokeTransparency = 1}):Play()
		end
	end)
end
local function meld(tekst: string) melding.Text = tekst; toon({melding}, 3.5) end

-- staat de speler op het dek? (binnen de rand, op dekhoogte t.o.v. de kern)
local function opDek(): boolean
	local ch = plr.Character
	local hrp = ch and ch:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not hrp then return false end
	local rel = kern.CFrame:PointToObjectSpace(hrp.Position)
	return math.sqrt(rel.X * rel.X + rel.Z * rel.Z) < 8.3 * S and rel.Y > 6 and rel.Y < 16
end

local vorige, welkomGezegd, gereden = "", false, false
RunService.Heartbeat:Connect(function()
	local fase = pag:GetAttribute("FaseLokaal") :: string?
	if not fase then return end
	local aanBoord = opDek()
	if fase == "instappen" then
		if vorige ~= "instappen" then welkomGezegd = false end
		if aanBoord and not welkomGezegd then
			welkomGezegd = true
			if gereden then meld("Exit: follow the signs") else toon({titel, onder}, 4.5) end
		end
		if not aanBoord then gereden = false end
	elseif fase ~= vorige and aanBoord then
		if fase == "sluiten" then meld("Gates closing") end
		if fase == "omhoog" then gereden = true end
	end
	vorige = fase
end)
]==]; lb.Parent = sps
-- vertalingen voor de Engelse teksten in PagodeBeleving (Roblox vertaalt automatisch naar de taal van de speler)
do
  local LS = game:GetService("LocalizationService")
  local oudT = LS:FindFirstChild("PagodeTeksten"); if oudT then oudT:Destroy() end
  local lt = Instance.new("LocalizationTable"); lt.Name = "PagodeTeksten"; lt.SourceLocaleId = "en-us"
  lt:SetEntries({
    {Key = "", Source = "Welcome aboard", Context = "", Values = {nl = "Welkom aan boord"}},
    {Key = "", Source = "Gates closing", Context = "", Values = {nl = "De hekjes gaan dicht"}},
    {Key = "", Source = "Exit: follow the signs", Context = "", Values = {nl = "Uitgang: volg de borden"}},
  })
  lt.Parent = LS
end
local n = 0; for _, p in ipairs(gondel:GetDescendants()) do if p:IsA("BasePart") then n += 1 end end
return "Pagode rijklaar: gondel " .. n .. " delen, cilinders " .. #cils:GetChildren()
