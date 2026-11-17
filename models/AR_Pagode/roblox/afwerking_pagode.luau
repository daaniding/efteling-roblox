-- Afwerking Pagode (na plaats_pagode.luau): botsing, plafondlampjes, lichtsnoeren langs de gevels, rode ring onder het platform.
-- Maten = Blender-maten (build/02-03): RAND 1.5, dek 2.2, goot 4.8, gevelpunt 6.8, gevelfront r 8.4, 22 gevels, as (0.5, 0, -38.6).
-- Blender-lokaal (x, y, z) -> Roblox: Pagode:GetPivot() * CFrame.new(-(x - 0.5) * 3, (z + 38.6) * 3, y * 3)
-- Bronnen: Pagode-donker.jpg (lichtsnoeren langs de gevels, rode lijn onder het platform), video 6:45 (ronde plafondlampjes).
local S = 3
local g = workspace:WaitForChild("Pagode")
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
local LAMPEN = {{352.53, 64.97, 3.32}, {349.87, 68.15, 2.72}, {353.80, 60.55, 4.43}, {352.23, 63.18, 3.98}, {342.14, 56.76, 3.17}, {349.43, 56.37, 4.22}, {360.29, 63.95, 2.54}, {370.20, 42.08, 2.57}, {371.38, 49.51, 2.57}}
for i, l in ipairs(LAMPEN) do
  local p = Instance.new("Part"); p.Name = "lantaarnlicht"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
  p.Transparency = 1; p.Size = Vector3.new(0.3, 0.3, 0.3); p.Position = Vector3.new(l[1] * S, 2 + l[3] * S, -l[2] * S); p.Parent = map
  local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 128); pl.Brightness = 1.4; pl.Range = 18; pl.Shadows = true; pl.Parent = p
end
return "afwerking: " .. #map:GetChildren() .. " onderdelen"
