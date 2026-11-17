"""Maakt roblox/plaats_pagode.luau: modellen laden, materialen, plaatsing op de echte plek, en een stuk terrein uit AHN.
Hoogte: NAP 10.0 = Roblox Y 2 (vlak-terreinafspraak van het project). Park (x oost, y noord) m -> studs (3x, -3y).
Terrein: AHN dtm (ref/ahn/dtm_park_300_385_15_80.npy, 0.25 m) per 1 m, 1 byte (NAP 8.5 + v * 0.015); materiaal uit de
luchtfoto (verhard = licht/grauw, gras = groen of donker onder bomen). Uitsparingen: bak, sleuf, put; onder vlonder/tribune lager.
Gebruik: python3 roblox/maak_plaatsscript.py  (vanuit models/AR_Pagode)"""
import os, json, math, base64
import numpy as np
from PIL import Image

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ids = json.load(open(os.path.join(D, 'exports', 'asset_ids.json')))
info = json.load(open(os.path.join(D, 'exports', 'export_info.json')))
H = np.load(os.path.join(D, 'ref', 'ahn', 'dtm_park_300_385_15_80.npy'))       # rij 0 = y 80, kolom 0 = x 300, 0.25 m
X0, X1, Y0, Y1 = 300, 385, 15, 80
NX, NY = X1 - X0, Y1 - Y0
# 1 m-raster: mediaan van 4x4, gaten opvullen met buren
hm = np.full((NY, NX), np.nan)
for j in range(NY):
    for i in range(NX):
        blok = H[j * 4:(j + 1) * 4, i * 4:(i + 1) * 4]; v = blok[~np.isnan(blok)]
        if v.size: hm[j, i] = np.median(v)
for _ in range(20):
    nan = np.isnan(hm)
    if not nan.any(): break
    p = np.pad(hm, 1, constant_values=np.nan)
    buren = np.nanmean(np.stack([p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]]), 0)
    hm[nan] = buren[nan]
# lichte afvlakking (3x3)
p = np.pad(hm, 1, mode='edge'); hm = sum(p[a:a + NY, b:b + NX] for a in range(3) for b in range(3)) / 9
# materiaal uit de luchtfoto (pagode_10cm.jpg: x 290..440, y -20..110, 0.1 m)
lf = np.asarray(Image.open(os.path.join(D, 'ref', 'luchtfoto', 'pagode_10cm.jpg')).convert('RGB')).astype(float)
mat = np.zeros((NY, NX), int)
for j in range(NY):
    for i in range(NX):
        x, y = X0 + i, Y1 - j
        c = lf[int((110 - y) * 10):int((110 - y) * 10) + 10, int((x - 290) * 10):int((x - 290) * 10) + 10].reshape(-1, 3).mean(0)
        r, g, b = c; L = c.mean(); sat = c.max() - c.min()
        mat[j, i] = 1 if (L > 105 and g < r + 6 and sat < 70) else 0      # 1 = verhard pad, 0 = gras
q = np.clip(np.round((hm - 8.5) / 0.015), 0, 255).astype(np.uint8)
h_b64 = base64.b64encode(q.tobytes()).decode()
m_b64 = base64.b64encode(np.packbits(mat.astype(np.uint8)).tobytes()).decode()

AS_PARK = (320.5, 58.5)
AS_HOOGTE = info["draaias_lokaal"][2] - (2.2 - 45.0)      # boven de grond
theta = math.degrees(math.atan2(47.5 - AS_PARK[1], 360.0 - AS_PARK[0]))     # richting as -> bak (park)
rot_y = 180.0 + theta                                      # lokale +x (import -X) -> richting bak

luau = f'''-- De Pagode plaatsen (gegenereerd door models/AR_Pagode/roblox/maak_plaatsscript.py). Stand OMHOOG, statisch.
-- Gondel+arm+voet: oorsprong = draaias, op park ({AS_PARK[0]}, {AS_PARK[1]}), {AS_HOOGTE:.1f} m boven de grond, draaiing {rot_y:.2f} graden.
-- Station: oorsprong = middelpunt bak, park (360.0, 47.5); 180 graden gedraaid (Blender x oost/y noord -> Roblox).
-- Hoogte: NAP 10.0 = Roblox Y 2. Terrein uit AHN (x {X0}..{X1}, y {Y0}..{Y1}), materiaal uit de luchtfoto.
local ID = {json.dumps(ids).replace(":", " =").replace('"', '')}
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
local TEX = {{pannen = true, sierveld = true, windveer = true, trommel = true, sierrand = true, kernwand = true, arm = true,
  natuursteen = true, vlonder = true, klinker = true, bord = true, ingangsbord = true, uitgangsbord = true, breuksteen = true,
  bamboe = true, blad = true, spar = true, naald = true, haag = true, bloem = true, schors = true, tokorand = true, tokopaneel = true, parasol = true, wilg = true, steen = true, pluk = true, huisrand = true}}
local ALPHA = {{bamboe = true, blad = true, spar = true, wilg = true, pluk = true}}       -- bladkaarten: transparantie uit de textuur
local EFFEN = {{
  groen = {{Color3.fromRGB(22, 112, 86), Enum.Material.SmoothPlastic}}, rib = {{Color3.fromRGB(232, 228, 216), Enum.Material.SmoothPlastic}},
  vlam = {{Color3.fromRGB(236, 232, 220), Enum.Material.SmoothPlastic}}, goud = {{Color3.fromRGB(214, 168, 70), Enum.Material.Metal}},
  rood = {{Color3.fromRGB(112, 20, 24), Enum.Material.SmoothPlastic}}, onderkant = {{Color3.fromRGB(40, 14, 14), Enum.Material.SmoothPlastic}},
  dek = {{Color3.fromRGB(96, 82, 66), Enum.Material.WoodPlanks}}, wit = {{Color3.fromRGB(230, 230, 222), Enum.Material.SmoothPlastic}},
  armzijde = {{Color3.fromRGB(216, 202, 176), Enum.Material.SmoothPlastic}}, beton_groen = {{Color3.fromRGB(46, 70, 50), Enum.Material.Concrete}},
  beton_donker = {{Color3.fromRGB(42, 42, 42), Enum.Material.Concrete}}, rooster = {{Color3.fromRGB(72, 74, 76), Enum.Material.DiamondPlate}},
  hek = {{Color3.fromRGB(22, 22, 22), Enum.Material.Metal}}, staal = {{Color3.fromRGB(92, 94, 98), Enum.Material.Metal}},
  chroom = {{Color3.fromRGB(205, 205, 210), Enum.Material.Metal}}, wit_glans = {{Color3.fromRGB(228, 222, 206), Enum.Material.SmoothPlastic}},
  grind = {{Color3.fromRGB(84, 76, 66), Enum.Material.Pebble}}, beton_groen_licht = {{Color3.fromRGB(78, 104, 82), Enum.Material.Concrete}},
  staal_groen = {{Color3.fromRGB(24, 62, 44), Enum.Material.Metal}}, hek_open = {{Color3.fromRGB(24, 62, 44), Enum.Material.Metal}},
  brons = {{Color3.fromRGB(64, 46, 30), Enum.Material.Metal}}, lamp = {{Color3.fromRGB(255, 214, 150), Enum.Material.Neon}},
  lamp_groen = {{Color3.fromRGB(70, 255, 120), Enum.Material.Neon}}, glas = {{Color3.fromRGB(150, 172, 176), Enum.Material.Glass}},
  dak_donker = {{Color3.fromRGB(46, 46, 50), Enum.Material.Slate}}, aarde = {{Color3.fromRGB(58, 40, 28), Enum.Material.Ground}},
  reling = {{Color3.fromRGB(20, 36, 26), Enum.Material.Metal}}, bord_blauw = {{Color3.fromRGB(128, 196, 212), Enum.Material.SmoothPlastic}},
  bamboestam = {{Color3.fromRGB(118, 122, 52), Enum.Material.SmoothPlastic}},
  dak_toko = {{Color3.fromRGB(86, 88, 94), Enum.Material.Slate}}, rotan = {{Color3.fromRGB(150, 112, 64), Enum.Material.Fabric}},
  rood_hek = {{Color3.fromRGB(150, 22, 28), Enum.Material.SmoothPlastic}}, beton_licht = {{Color3.fromRGB(150, 144, 132), Enum.Material.Concrete}},
  asfalt = {{Color3.fromRGB(70, 70, 72), Enum.Material.Asphalt}},
  voeg = {{Color3.fromRGB(52, 46, 40), Enum.Material.Slate}}, graniet = {{Color3.fromRGB(112, 110, 104), Enum.Material.Granite}},
  naald_donker = {{Color3.fromRGB(18, 32, 18), Enum.Material.Grass}},
}}
local LOOP = {{dek = true, vlonder = true, klinker = true, rooster = true, beton_groen = true, beton_groen_licht = true, natuursteen = true, grind = true,
  breuksteen = true, aarde = true, bloem = true, beton_licht = true, asfalt = true, voeg = true, graniet = true}}

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

for _, n in ipairs({{"Pagode", "PagodeStation", "PagodeOmgeving"}}) do local o = workspace:FindFirstChild(n); if o then o:Destroy() end end
local gondel = laad(ID.AR_Pagode_gondel, "Pagode"); aankleden(gondel, true)
gondel:PivotTo(CFrame.new(park({AS_PARK[0]}, {AS_PARK[1]}, 10 + {AS_HOOGTE:.3f})) * CFrame.Angles(0, math.rad({rot_y:.4f}), 0))
local station = laad(ID.AR_Pagode_station, "PagodeStation"); aankleden(station, true)
station:PivotTo(CFrame.new(park(360.0, 47.5, 10)) * CFrame.Angles(0, math.pi, 0))
local omgeving = laad(ID.AR_Pagode_omgeving, "PagodeOmgeving"); aankleden(omgeving, true)
omgeving:PivotTo(CFrame.new(park(360.0, 47.5, 10)) * CFrame.Angles(0, math.pi, 0))

-- terrein (AHN, 1 m) met uitsparingen
local A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local IDX = {{}}; for i = 1, #A do IDX[A:sub(i, i)] = i - 1 end
local function b64(s)
  local out = {{}}
  for i = 1, #s, 4 do
    local n, pad = 0, 0
    for k = 0, 3 do local c = s:sub(i + k, i + k); if c == "=" then pad += 1; n = n * 64 else n = n * 64 + IDX[c] end end
    table.insert(out, string.char(bit32.extract(n, 16, 8))); if pad < 2 then table.insert(out, string.char(bit32.extract(n, 8, 8))) end
    if pad < 1 then table.insert(out, string.char(bit32.extract(n, 0, 8))) end
  end
  return table.concat(out)
end
local HB = b64("{h_b64}")
local MB = b64("{m_b64}")
local NX, NY = {NX}, {NY}
local function hoogte(i, j) return 8.5 + string.byte(HB, j * NX + i + 1) * 0.015 end
local function verhard(i, j) local k = j * NX + i; return bit32.btest(string.byte(MB, k // 8 + 1), bit32.lshift(1, 7 - k % 8)) end
local t = workspace.Terrain
t:FillBlock(CFrame.new((({X0} + {X1}) / 2) * S, 6, -(({Y0} + {Y1}) / 2) * S), Vector3.new({NX} * S, 112, {NY} * S), Enum.Material.Air)   -- hele hoogte leeg (oude fout: alleen onder Y -8)
local ASX, ASY = {AS_PARK[0]}, {AS_PARK[1]}
local ux, uy = math.cos(math.rad({theta:.4f})), math.sin(math.rad({theta:.4f}))
local n = 0
for j = 0, NY - 1 do
  for i = 0, NX - 1 do
    local x, y = {X0} + i + 0.5, {Y1} - j - 0.5
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
        or (r < 24.6 and (a < 89 or a > 306))                                                -- plein en oostpad
        or (r < 17.9 and a >= 87.5 and a < aL)                                               -- aanlooppad naar het laantje
        or (r < 41.2 and a > 41 and a < 89)                                                  -- terras en Toko Pagode (15_toko)
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
  vul({X1}, 430, 15, 112); vul({X0}, {X1}, {Y1}, 112)
end
-- spawn bij de Pagode (oude spawn bewaard in attribuut)
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then
  if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", tostring(sp.CFrame)) end
  sp.CFrame = CFrame.new(park(362.9, 68.3, 9.75)) * CFrame.Angles(0, math.rad(137), 0)   -- open plein, kijkt naar het ingangsbord (zuidwest)
end
return "Pagode geplaatst, terrein " .. n .. " kolommen"
'''
open(os.path.join(D, 'roblox', 'plaats_pagode.luau'), 'w').write(luau)
print('plaats_pagode.luau', len(luau), 'tekens; draaias', AS_PARK, 'hoogte %.2f' % AS_HOOGTE, 'rot_y %.2f' % rot_y, 'verhard %.0f%%' % (mat.mean() * 100))
