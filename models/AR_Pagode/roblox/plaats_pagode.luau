-- De Pagode plaatsen (gegenereerd door models/AR_Pagode/roblox/maak_plaatsscript.py). Stand OMHOOG, statisch.
-- Gondel+arm+voet: oorsprong = draaias, op park (320.5, 58.5), 4.2 m boven de grond, draaiing 164.44 graden.
-- Station: oorsprong = middelpunt bak, park (360.0, 47.5); 180 graden gedraaid (Blender x oost/y noord -> Roblox).
-- Hoogte: NAP 10.0 = Roblox Y 2. Terrein uit AHN (x 300..385, y 15..80), materiaal uit de luchtfoto.
local ID = {AR_Pagode_gondel = 80470568889612, AR_Pagode_station = 123102938730600, pannen_kleur = 113862951849627, pannen_normaal = 135305032497691, sierveld_kleur = 92806080990483, sierveld_normaal = 75982823389914, windveer_kleur = 105110194440006, windveer_normaal = 129813406208116, trommel_kleur = 94643214361680, trommel_normaal = 105998268539020, sierrand_kleur = 114707188453195, sierrand_normaal = 98163589145950, kernwand_kleur = 118948255846476, kernwand_normaal = 77932851706654, arm_kleur = 125000713070178, arm_normaal = 115276388154879, natuursteen_kleur = 93634200024177, natuursteen_normaal = 71110702105863, vlonder_kleur = 114168670349764, vlonder_normaal = 105858881415149, klinker_kleur = 76036336782300, klinker_normaal = 132177172189347, bord_kleur = 107214009738343, AR_Pagode_omgeving = 85135125783257, ingangsbord_kleur = 106758910462500, uitgangsbord_kleur = 71715100841980, breuksteen_kleur = 74939119820853, breuksteen_normaal = 96183299144764, bamboe_kleur = 100311851570971, blad_kleur = 75105356130828, spar_kleur = 91377517844234, naald_kleur = 72168876031761, haag_kleur = 97966661994557, bloem_kleur = 71396169120830, schors_kleur = 139686993244290, tokorand_kleur = 115150839917312, tokopaneel_kleur = 109978993367892, parasol_kleur = 116141934527280, wilg_kleur = 100412416431599, steen_kleur = 116600353020198, steen_normaal = 95927671453559, pluk_kleur = 82875106386837, huisrand_kleur = 74245754818603, AR_Pagode_arm = 88039896274620, AR_Pagode_voet = 79185188175320}
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

for _, n in ipairs({"Pagode", "PagodeStation", "PagodeOmgeving"}) do local o = workspace:FindFirstChild(n); if o then o:Destroy() end end
local gondel = laad(ID.AR_Pagode_gondel, "Pagode"); aankleden(gondel, true)
gondel:PivotTo(CFrame.new(park(320.5, 58.5, 10 + 4.199)) * CFrame.Angles(0, math.rad(164.4385), 0))
local station = laad(ID.AR_Pagode_station, "PagodeStation"); aankleden(station, true)
station:PivotTo(CFrame.new(park(360.0, 47.5, 10)) * CFrame.Angles(0, math.pi, 0))
local omgeving = laad(ID.AR_Pagode_omgeving, "PagodeOmgeving"); aankleden(omgeving, true)
omgeving:PivotTo(CFrame.new(park(360.0, 47.5, 10)) * CFrame.Angles(0, math.pi, 0))

-- terrein (AHN, 1 m) met uitsparingen
local A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local IDX = {}; for i = 1, #A do IDX[A:sub(i, i)] = i - 1 end
local function b64(s)
  local out = {}
  for i = 1, #s, 4 do
    local n, pad = 0, 0
    for k = 0, 3 do local c = s:sub(i + k, i + k); if c == "=" then pad += 1; n = n * 64 else n = n * 64 + IDX[c] end end
    table.insert(out, string.char(bit32.extract(n, 16, 8))); if pad < 2 then table.insert(out, string.char(bit32.extract(n, 8, 8))) end
    if pad < 1 then table.insert(out, string.char(bit32.extract(n, 0, 8))) end
  end
  return table.concat(out)
end
local HB = b64("VFRUVldYV1ZVUk9KRD05ODc3Nzg6PkFFSUxOT09KRkdMUlNRT01MTU9PTk5QUVFRUVFSUlNUU1JOS0pLTExMTEtLSklJSUlJSUpKS0tKSkhGRURERFVUVFVWVlZVVVJPS0dAOzo5OTk6PEBDRklMTlBQS0ZFSlBRUU9OTU1OT09PT1BPT09PUFFSU1JQTEpKS0xMTExLS0pJSUlJSUlJSkpKSklHRkVERERWVlVVVVVUVFRRT0xKRUA+PT09PkBCREZJS05QUEpFQ0dNUFFQT01NTU1NT09PTUxNTU5PUVFQTUtJSktLTExMS0tLSkpKSkpJSUlJSUhHRkVEREREVlZWVVVUU1NSUU9OTElGRENDQ0RERERERkdKS0tGQ0FESk5RT05NTEtKS01OTUxLTExNTlBQTktKSkpLS01OTk1LS0tLSkpKSklJSUhHRkVERERERFdXVlZVVVRTUlBPTk1MS0lISEdHRURCQUJDRUVEQUBAQklOUU9NTEtJSElLTU5NTE1OTk9QTkxKSkpLS01PUlJQTEtLS0pKSkpJSEhHRkVERERERERaWVhXVlVVU1JRUE9OTUxMSkpJR0VDQkBAQEBAPz49PkBHTVBPTEtIR0dIS01OTk9QUVFRT01LSkpKS0tNUVVXU05LS0tLSkpJSUhHRkZFREREQ0NDX11aWFdXV1VUUlFPTk1NTEtKSEZFRERCQUBAPz8+PT4/RUtQT0xJR0dISkxOUFJTVFRTUU9OTEtLS0tMTVBTVVJPTEtLSkpJSUhHRkZFRERDQ0JCQmJgXFlYWFlXVVJRUE9OTUxKSUhHR0dGRUJCQUFAPj09PkNITU1KR0dISktNT1FUVVVTUlBOTk5NTEtLTExOT1FQTkxLS0pJSUhIR0ZFRENDQkFBQEBjYV5bWVtcWlZSUU9OTkxLSklJSEhHRkRCQkJBQT89PT9DSExMSkdISktMTk9TVlZUUE9PTlBSUU1KS0tMTExNTUxMS0tKSUhHR0ZFRERCQUFAQEBAY2FfXVxfXlpUUVBPTk1MS0pJSUdGRURDQkJBQUA+PT1ARUpNTEpJSUtNT1BSVVZUUU9PTk5RVFNPSkpLS0tLTExMTEtLSklIR0ZFRENDQkBAPz9AQWNiYWBgYl9ZUlBPT05NTEtJSEdGREJCQUFBQEA/Pj0+QUdLTk1MS0tMTlFTVVVUU1NUU1FPUlZYUkxKSkpKS0tLS0xMS0pJSEZFRENCQUA/Pz9AQkNjZGRlZWVhWlNRUFBQT01LSUdGREJBQEBAPz8+Pj09P0NJTE5OTk1NTlFUVVZVVVZXWlxYUlFWWldQS0lJSkpKSktLS0tKSUhGRURCQUA/Pz9AQkRFZWZnaGhnY15ZVlRTVFJPS0lHREJBQEA/Pz8+Pj49PkFGTE9QUFBPUFJVVlZVVVdaXmNlXlVPVVpbVlBLSUlJSkpKSktKSklHRkRDQkA/Pj5AQkRGR2dpa2tra2llYV1aWVhWU05LSEVCQEBAQUFAPj09PT9FTFFSUVJSUlRWV1ZVVVhdYWZqb2tgU1NYXVpXUk9NS0lJSUpKSklIR0VEQkFAPz4/QUNFR0hpa21ubm5ubGpnZWJgXVlVUU1KRkJCQ0RFQ0A9PT1ASFFVVVNTVFZYWFdVVVleZGlvdHl4aVlPVFpcXFlWU1BPTUtJSUlIR0ZFQ0FAPz8/QUNFR0hKa21wcXJycnFvbm5saWZjX1tXU01IRkhOU05GPTw9QUlTV1ZUVFZYWVdVVVlfZWxxd3yDh35pVVFXXF1eXFlWVFBMSUhIR0ZFREJAPz9AQUNFR0hKS2xvcnN0dHRzc3NzcnFubGpnY15YU1JWXGNdUEI+PkJJUldXVlZZWlhVVVlfZm1zeX+Fi5CNdV1NUlZYV1ZVVVVRTElIR0ZFREJBPz4/QUNERkhKS0xscHR1dHR0dHNzdHR1dHNyb25qZGBgZGtwbF5ORUJDSlNYWFhaW1pXVlhfZm10eoGHjZOZno9yVk1QUVBPTk9OTEpIR0ZGRENCQD49P0FERkdJS0xNa3B1dXV1dHNzc3R0dXZ2dXRzcW5sbnFyc3FpXVFJR0tSWFpbXFxZVlheZW10e4KIjpWboaahhmZTV19iYWFhWVBIR0dGRENCQT8+PkBDRUdJSkxNTmluc3V1dHRzcnNzdHV3d3Z1dXV0c3R0dHRzcGleVE1MUFVZW11aV1dcZGxze4KJkJedo6qutKONen6GiYmIh39pVUdGRURCQUA/Pz9BREZISktNSEJobXN1dXVzc3Nzc3R0dnZ3dnZ2dXV1dnV1dHNuZ1xUTk5QVltcWVdaYGlxeoGJkJeepauxtbmzqaKmrrGxsa+gfVtHRkRDQkFAPz9BQ0VHSUtNTkc/aW1ydHV0c3NzdHN0dHV2d3d3dnV1dnZ2dXV0cGlhWVRQTlJWWVdYXWZvd4CHj5efpqyytrq8v8DBwcHBwMC/rYhfSUZFREJBQEBAQkRGSEpNTk5GPWptcXN0dHR0c3RzdHR2d3h4d3Z2dXZ2dXV1c29oYV1aV1NSU1VWWmBqc32FjZWdpayyt7q8vsHCw8LCwsHBvqSBXlBLSEZDQkBAQkNFR0pMTk9OS0hsbW9wcnN0c3NycnN0dXZ3d3h4d3Z2dXV1dXNvaGNfXlxXUlFUWF5lbneBiZKao6uxtrm8vb7Cw8TCv7y4urWfgmlfWE9JRUNCQkNFR0hLTU5PTUtKbW1ub3Byc3JxcHFxcnN0dXZ4eXl4d3Z2dXVyb2llYWBeWU5GQkZMWmp6g4yVnqivtLi7vL6/wbuvopeTjJCMgHJubWhbUUlEQ0NERkhJS01PT01MTGtsbW5vb3Bwb25ub29xcnN1d3h4eHh3dnZ1c29rZ2NgXVhJOzEzN0NPXG+Dl5+psLa5u72+v7KdgnVrZl9jYV5aaHJ2aFxQSUVERUdJSkxOT09NTExoaWprampqa2pra2xtbm9xcnR1dnZ2dXV1dXNwbWlkYF1XQzAfHh8oMj1MXW+FnLG2ubu9vrOWclVIQT88Pj8/QlJhbWtmW1BJRkZISkxNT09PTUxMZmVlZGRkZGVmZ2hpamttbm9wcHFxcnJzc3NycW9rZmJfWkw+MzIsJB0cKTZFWGx/i5+yvK+Wa009PDw7PDs8PDxFTVpiZ2RXTUhISkxNTk9QT01MS2VjYV5eXl9gYWNlZ2hpamtsbGxtbW5vb29vcHFwbWhkYl5WT0lIQjowKSIcGys8TFZoeoqDbU49PDs7Ozs7Ozs8PD1DV2ZsX1NLSkxNT1BQUFBNTEtlY2BdXFxdXmBhY2RlZmdoaGhoaWtsbW1sa2xtbWtoZmVkYmFgX1lSR0A4MikhGhghMkJQPy4jLjs7Ojo6Ojs7Ozs8PE1fbGVXT0xNT1BTVFNRTkxMZWNhX15eXl5fX2BhYmNkZGVlZmhpampqamloaGhnZmZnZ2dmZWRjYl9YUEpANy8sJRwUEgYAARoxOjk5OTo6Ojs7OzxHWmhpXFNOT1BSVVZVUU5NTGRjYmBfX2BfX15eXl9gYmJjZGVnaGlpaWhmZGRkZGRlZ2doaGdmZWVkY2FfWE9HRDwzKx8LAAAaMDk4ODk5Ojo7Ozs8QFNjbF9VT1BRU1ZXVlFPTUxkZGNhYF9gYGBfXl5eX2FjY2RlZmdoaGhmZGJiYmJjZGVmZ2dmZWVlZWVkYV9eXlxUS0M2JxoaJzA5ODc4ODk6Ojs7PDxQYW5hV1BRUlJVVVRRUE5MZWRjYmBeXl5fXl9fYGJkZmdmZmZmZ2hnZWJgYWFhYWJjY2RkY2NiY2VlY2FgX2BeXl1cUkc9PDs6OTg3ODg5Ojs7PDw9UWJvYlhRUVJSU1JSUVFPTWVkZGNhYF5eXl5eYGJnbG9wbWtpaGhnZmRiYGBgYWFhYWBgYGBgX2BiYmBdXV5fX19eXVNIPz08Ozo5ODg5Ojo7PDw9PVFhbWBYUlJSU1JSUlJRUE5kZGRjYmFfXl1dXWFlbXV7fXl0b2xraWhlYmFhYWFhYWBeXl5fX11dXl5dWVpcX19hYWBYTUQ/PTs6Ojo6Ojs7PDw9PkdbaWpdVlJSU1NTUlJSUVBPZGRkY2JhYF9dXFxfZXB7hYqIgXp1cW9raGVkY2JhYGBfXl1dX2BeXFxbWldZWl5gZGVlX1NIQD48Ozs7Ozs8PDw9PUdZbXFoXFZTU1NTU1NTUlJRUGNjY2NiYV9dXFpaXGNueYeSl5KJgnt3cm5qaWZkYWBfX15dXV9fXltbW1pZWltgZGlqamhgUkU9PDw8PDw8PD09PUted354aF1XVVNTU1NTU1NSUVBjY2NjYmBfXVxaWlpganaHlZ+elo+Ignt0cG1pZWNiYWBeXV1fX15cW1tcXF1dYmZsb3NzcGZURT09PT09PT09PkxpgoqBdGhfWldUU1NTVFRTUlFQY2NjYmFgX11cW1paXWdyhJSkp6Gbk4yEfHZxbGlnZWRiYF5eXl1cW1tbXF5fYGRrcnZ5foOBdWhUST09PT5NXGp5lJ6Ue29oYV1aVlRTU1RUU1JRUGNjY2JhYF9eXVxbWltkcIKUpKunop2VjIN8eHRxbWpnY2BgX15dXFtbW11fYGJmbnV8gYmQmJSOem9maWtreoiWo7CrkXhtaGNgXFhVU1NUVFRSUVBjY2NiYWBgX15dXFtaYG2Bl6euq6ehmpCJhIJ+e3RuZ2NgYF9eXFxdXV1eYGJmanJ5gYiQmaOqr6OXjpKXl6WzwL62o4t4bmpmYl5aVlRTU1NTUlFQY2NjYmFhYF9eXl1bW15qf5emrKuoo5uSi4qLh4F3cGZiX19fX19gYWNjZGVna291fYePl6Cqsre3t7m9wsHBv7qzp5eFeHBsaGRgXVpXVFNTU1JRUGNjY2JhYWBfX15dXFpcZ3ySoKWmo5+XjoiHh4N9dW5lYV5fYGJkZ2lqbG1vcXN3fISOlp2mr7i9vr28vb6+u7evppeMgHlzbmpnZGJfW1ZUU1NSUVBjY2NiYWFgYF9fXl1bXGV2iZecnZuYkYmBf3x6dXBqY19eYGNnbHF1d3h6fH5/gYaNlZ2jrLW+wcG/vb28ubSuo5mPh4B6dXqBiIeHeWlXVFNTUlFQY2NiYmFhYGBfX15dXFxjcICLkJCQj4d+c29qaGhoZF9bXGFobnV7gYSFh4qMjY+TmJ2kq7O8wsTBvr28ubStpZyVjYeBfX2LnKqqrJ+EZVRTU1JRUGJiYmFhYWBgX19eXVxeZG96goSDg4B3b2ZjX19gYV9cWlxianV/h4yPkpSWmJqbn6OmrLK4v8PDv728urawqaKblY+KjJCbrcDOz9LGnnNUU1JSUVBiYmFhYWFgYF9fXl1cXmJobnJzcnJvaGFcXFtbXF1cWlpcY258iZKVl5udoKKkpqmtsLW6v8PCwr++u7i0rqminJeXmaSru8XP1NTW06l9VFNSUVBPYmJhYWFhYGBgX15dXF5gY2VmZ2ZlYl9cXF1dXl9fXl5fYWd0hJGZm56ipqmpq62wtLe8wMPEwsPDwsC8urezrquoq7C9ydbb29nX19KofFRTUlFQT2JiYWFhYWBgYF9fXl1dXV5fYGBgYGBfX19fYGFhYmJiY2VseoqWnaClqaytr7Gztrq+w8fLyMPCxcbEwsLAvry5uL7FztTa3t7d2dbPsYdhUlFQT05hYWFhYWBgYGBgYGBgX15fYGFhYmJiYmFhYWFiY2RkZWZpb36OmJ6jq7CxsbK0trq/wsjM0crDv8HDwsPGyMnJysvMztHY3OHg3trW0LqSalNQT05MYWFhYWBgYGBhYWJjY2FgYGFiY2NkZGRjYmFhYmNkZGVmaXB/jpmiqrK0tLO0tri8wcXLz9HGu7S2uLi6vsPJzM/Q0dPV2t7h4d7b1tC8lG1TUE5NTGBhYWFgYGBhYWJkZWViYGBhYmNjZGRkY2JiYWJjZGRlZmlwf5CeqrK2t7W0tLa4vL/DxcXCubCpqqmrrLK+x87S1dbX2N3h4uDd2tbRs4pjVFFOTEtgYWFhYGBgYWFiZGVlY2FgYWJjY2RkZGNjYmFiY2RkZWZpcH+SpLG2uLi3trW1trq8vbu3saefmJqboKOruMTN0dXX2dbZ29/d2tfV0q6EXFRQTUtKYGFhYWBgYGFhYmRlZWNhYGFiY2NkZGRkY2JhYmNkZGVmaXB/lai1uLi4t7a0tLa4ubezqaGYkouJh4qNnK/Cy8/T1tXGwsfW29nW1MaieVtTT0xKSWBhYWFgYGBhYWJkZWVjYWBhYmNjZGRkZGNiYWJjZGRlZmlwf5eqt7i4uLe2tbW2t7ezr6Wcj4d9eHV2eYSSobPC0dTOtKOmwtHWyb2kiWpXUU5MSkhgYWFhYGBgYWFiZGVlY2FgYWJjY2RkZGRjYmFiY2RkZWZpcH+Xqre4uLe3t7e3t7i1sauek4Z+dm9qZ2Ztd4KSn66xq5WEh52us6ibgG1aU1BOTEpIYGFhYWBgYGFhYmRlZWNhYGFiY2NkZGRkY2JhYmNkZGVmaXGCm664ubi4uLi5uLm5ta+ilYl/eXBqZWNiYWFib3yKjYl/dHR+iY6DdGNbVVFPTktJSGBhYWFgYGBhYWJkZWVjYWBhYmNjZGRkZGNiYWJjZGRlZml4jqezurq6ubq6urq7urKnlYp/eXNsZmFgYF9fYGNjZGZoamtra2tpZmFbVlJQT01LSklgYWFhYGBgYWFiZGVlY2FgYWJjY2RkZGRjYmFiY2RkZWZpfpmzuLu7u7u7u7u7vsG2po+FfXhwaGJfXl5dXl9hYGBgYWNkZmdmY19aVlNRUE5NTEtLYGFhYWBgYGFhYmRlZWNhYGFiY2NkZGRkY2JhYmNkZGVmdaDM6urq6urq6urq6+3r0K2NiYR9bmRfXFxcXF1eX11dXF1eX2BiYF5aV1VTUVBOTEtLTGBhYWFgYGBhYWJkZWVjYWBhYmNjZGRkZGNiYWJjZGRldaDf//////////////////rLpp+WhW5fW1lZWlxeXl1cW1tbW1tcXFtaV1ZVU1JQTkxKSUlgYWFhYGBgYWFiZGVlY2FgYWJjY2RkZGRjYmFiY2RkdaXv////////////////////6cK1pI5xYFlWVlleYGBdXFtbW1tbWlpZWFdWVVRSUE5MSUZEYGFhYWBgYGFhYmRlZWNhYGFiY2NkZGRkY2JhYmNkdan8///////////////////////02rydg29jWFdaYGNiX11cW1tbW1paWVhXVlVTUlBOTUlFQWBhYWFgYGBhYWJkZWVjYWBhYmNjZGRkZGNiYWJjZIfd//////////////////////////DKq5SDb11aXWNlZGBeXFtbW1taWVhXV1VUU1JQT01KRUE=")
local MB = b64("4AAAAAAAAH/////AAAAAAAAH/////wAAHAAAAB+8///7RQzAAAAA+uf//944b4wAAB+Hf//++f5+wAAA/j/////H4/gAAA//8////j/+QAAC//8/v//5//aAADv8f//7/8f/IAAF/+P//8b+P/8CACfP///+A/H78CAD/nv///Afh3/wAHvz////gAAd/4AH/4////wAAH/4AH/8P///4AAB/8AH//Ef//wAAA/8AH//qL//wAAAPBAH//gP//4AAACAgK//gB9/4gAAAAKEP/Asf/EwAAAAAGH/j//SgYAABgADB+5//FiYAAC8ABAf8//gTMAADkAAAH/f9BhGAAA+AAAA//+AYiAAA+wAAAH//QIhCAB/2AAAB//4DUgAB4OgAAAf/8CSQAB4BwAAAP3/B4sAA4AUAAAD5/w+WAAcAkAAAAe/4cFcAcHigAAAHv4OC/gOF5QAAA///Hyf8HH04AAAf/+D9//Dv+UAAAP/mF+//hQ/KAAAB/wH///44/HAAAAe4B///8OOHAAAAHMA////ngHgAAABgAf///5+PgAAAAAAf///4d/AAAAAAEP///4F+gAAAACAH//AAAFAAAAABAB5/gAAAAAAAAAAAAfwAAAAAAAAAAAAf4AAAAAAAAAAAA/8AAAAAAAAAAAAD+AAAAAAAAAAAABfAAAAAAAAAAAAAfgAAAAAAAAAAAC/wAAAAAwAAAAAAz4AAAAAeAAAAAAT8AAAwABgAAAAAB+ccAAAAYAAAAAB/OAAAQAOAAAAAA3mAAAAGBwAAAAAZzAAAAPAcAAAAAaZgAGAHwHAAAAA/4gADwDwA4AAAA/4QAB4A4AMAABg/uIAAcAAAGAAD9/7kAAAAAADAAB///3AAAAAABgAB///4gAAAQAAwAA///8QAAAMAAYAAf/v+A==")
local NX, NY = 85, 65
local function hoogte(i, j) return 8.5 + string.byte(HB, j * NX + i + 1) * 0.015 end
local function verhard(i, j) local k = j * NX + i; return bit32.btest(string.byte(MB, k // 8 + 1), bit32.lshift(1, 7 - k % 8)) end
local t = workspace.Terrain
t:FillBlock(CFrame.new(((300 + 385) / 2) * S, 6, -((15 + 80) / 2) * S), Vector3.new(85 * S, 112, 65 * S), Enum.Material.Air)   -- hele hoogte leeg (oude fout: alleen onder Y -8)
local ASX, ASY = 320.5, 58.5
local ux, uy = math.cos(math.rad(-15.5615)), math.sin(math.rad(-15.5615))
local n = 0
for j = 0, NY - 1 do
  for i = 0, NX - 1 do
    local x, y = 300 + i + 0.5, 80 - j - 0.5
    local nap = hoogte(i, j)
    local dx, dy = x - 360.0, y - 47.5; local r = math.sqrt(dx * dx + dy * dy); local a = math.deg(math.atan2(dy, dx)) % 360
    local lx, ly = (x - ASX) * ux + (y - ASY) * uy, -(x - ASX) * uy + (y - ASY) * ux    -- langs/dwars de arm vanaf de as
    local weg = r < 9.0 or (lx > -9.8 and lx < 6.8 and math.abs(ly) < 3.6) or (lx > 6.5 and lx < 30.0 and math.abs(ly) < 1.5)
    if not weg then
      -- onder alle eigen bestrating/tribune/bordes ruim weg: terreinvoxels (4 stud) bollen anders door de klinkers heen
      local aL = 104.0 + (r - 14.2) * 0.95 - math.deg(1.5 / math.max(r, 1))                  -- tuinkant laantje (12_omgeving)
      local bebouwd = r < 11.2
        or (r < 27.2 and a > aL - 1.0 and a < 157.5)                                         -- bordes, tribune, laantje, onderpad
        or (r < 14.4 and a > 52 and a < 157.5)                                               -- bloemenperk + pleinmuur
        or (r < 14.6 and (a > 306 or a < 1.5))                                               -- uitgangspad oost (pad_oost0/1)
        or (r < 17.9 and a >= 87.5 and a < aL)                                               -- aanlooppad naar het laantje
      if bebouwd then nap = math.min(nap, 8.0)
      elseif r < 29 and a > 85 and a < 160 then nap = math.min(nap, 8.95) end              -- tuin: zichtbaar net onder de klinkers (terrein tekent ~0.6 m hoger dan nap; raycast meet lager dan je ziet)
      local top = G + (nap - 10) * S - 2     -- terrein rendert ~2 stud boven de FillBlock-bovenkant (voxelraster)
      t:FillBlock(CFrame.new(x * S, (top + (G - 30)) / 2, -y * S), Vector3.new(S, top - (G - 30), S), Enum.Material.Grass)   -- Ground zag eruit als zand
      n += 1
      if n % 400 == 0 then task.wait() end
    end
  end
end
-- rand rondom het AHN-stuk (oost en noord, achter de Toko): vlak gras op NAP 9.5, behalve onder terras/kiosk
do
  local tp, bd = G + (9.5 - 10) * S - 2, G - 30
  local function vul(x0, x1, y0, y1)
    t:FillBlock(CFrame.new((x0 + x1) / 2 * S, (tp + bd) / 2, -(y0 + y1) / 2 * S), Vector3.new((x1 - x0) * S, tp - bd, (y1 - y0) * S), Enum.Material.Grass)
  end
  vul(385, 430, 15, 112); vul(300, 385, 80, 112)
end
-- spawn bij de Pagode (oude spawn bewaard in attribuut)
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then
  if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", tostring(sp.CFrame)) end
  sp.CFrame = CFrame.new(park(362.9, 68.3, 9.75)) * CFrame.Angles(0, math.rad(137), 0)   -- open plein, kijkt naar het ingangsbord (zuidwest)
end
return "Pagode geplaatst, terrein " .. n .. " kolommen"
