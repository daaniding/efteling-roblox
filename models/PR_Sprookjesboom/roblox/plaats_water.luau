-- Levend, modderig water in het beekje (na plaats_omgeving.luau). Textures: build/11_water.py -> textures/water/.
-- Wateroppervlak troebel olijfbruin + 3 Texture-lagen (slib traag, 2x rimpels sneller; geanimeerd door BeekStroming.client.luau),
-- rimpelringen (particles) bij de wortelvingers in het water en in drie bochten, 14 kroosplukjes tegen de oevers, natte stenen.
-- Middellijn (exports/beek_middellijn.json) als Vector3Values voor de drijvende blaadjes. Het LocalScript zelf: zie BeekStroming.client.luau.
local S = 3
local O = Vector3.new(121.44, 1.95, -594.57)
local WY = O.Y + (-0.32 * S)
local function W(x, y, h) return Vector3.new(O.X + x * S, h or WY, O.Z - y * S) end
local IDS = {rimpel = 140312724930432, slib = 88421652502854, ring = 77074338755113, kroos = 140434402386473, blad = 90885613744350}
local CL = {{-10.45, -9.52}, {-10.5, -9.07}, {-12.65, -6.97}, {-13.0, -6.47}, {-13.45, -5.02}, {-13.35, -4.12}, {-12.9, -3.17}, {-11.9, -2.47}, {-10.75, -1.17}, {-10.15, 0.18}, {-9.7, 2.18}, {-9.35, 2.88}, {-8.2, 3.98}, {-7.5, 4.18}, {-7.1, 4.18}, {-5.95, 3.73}, {-5.15, 2.93}, {-4.8, 2.23}, {-4.4, -0.62}, {-3.35, -3.07}, {-1.15, -4.82}, {0.25, -5.42}, {1.7, -5.42}, {5.35, -4.52}, {7.35, -4.37}, {8.45, -4.47}, {9.05, -4.67}, {10.65, -6.37}, {11.1, -7.27}, {11.25, -8.77}, {11.7, -9.17}}
local water; for _, p in ipairs(workspace.SprookjesboomOmgeving:GetChildren()) do if string.match(p.Name, "^water_") then water = p end end
water.Color = Color3.fromRGB(62, 57, 36); water.Transparency = 0.04; water.Reflectance = 0.05; water.Material = Enum.Material.SmoothPlastic
for _, t in ipairs(water:GetChildren()) do if t:IsA("Texture") then t:Destroy() end end
local function tex(id, name, su, sv, tr)
  local t = Instance.new("Texture"); t.Name = name; t.Face = Enum.NormalId.Top; t.Texture = "rbxassetid://" .. id
  t.StudsPerTileU = su; t.StudsPerTileV = sv; t.Transparency = tr; t.Parent = water
end
tex(IDS.slib, "Slib", 14, 11.2, 0.1); tex(IDS.rimpel, "Rimpels", 9, 7, 0.62); tex(IDS.rimpel, "Rimpels2", 13, 10, 0.8)
local old = workspace:FindFirstChild("SprookjesboomWater"); if old then old:Destroy() end
local F = Instance.new("Folder"); F.Name = "SprookjesboomWater"; F.Parent = workspace
local mid = Instance.new("Folder"); mid.Name = "Middellijn"; mid.Parent = F
for i, p in ipairs(CL) do local v = Instance.new("Vector3Value"); v.Name = string.format("%02d", i); v.Value = W(p[1], p[2]); v.Parent = mid end
F:SetAttribute("BladTextuur", "rbxassetid://" .. IDS.blad); F:SetAttribute("WaterY", WY); F:SetAttribute("Punten", #CL)
local function rimpels(x, y, rate, maxSize)
  local p = Instance.new("Part"); p.Name = "Rimpelbron"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
  p.Transparency = 1; p.Size = Vector3.new(0.4, 0.05, 0.4); p.CFrame = CFrame.new(W(x, y, WY + 0.04)); p.Parent = F
  local e = Instance.new("ParticleEmitter"); e.Texture = "rbxassetid://" .. IDS.ring
  e.Orientation = Enum.ParticleOrientation.VelocityPerpendicular; e.EmissionDirection = Enum.NormalId.Top
  e.Speed = NumberRange.new(0.01); e.Lifetime = NumberRange.new(1.8, 2.6); e.Rate = rate; e.Rotation = NumberRange.new(0, 360)
  e.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.15), NumberSequenceKeypoint.new(1, maxSize)})
  e.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.45), NumberSequenceKeypoint.new(1, 1)})
  e.Color = ColorSequence.new(Color3.fromRGB(210, 214, 200)); e.LightInfluence = 1; e.Parent = p
end
for _, xy in ipairs({{-2.05, -4.05}, {-2.35, -3.85}, {-1.85, -4.3}}) do rimpels(xy[1], xy[2], 0.9, 2.6) end   -- vingers in het water
rimpels(1.7, -5.42, 0.4, 2.0); rimpels(-4.4, -0.62, 0.35, 1.8); rimpels(9.05, -4.67, 0.35, 1.8)
local rnd = Random.new(9)
for i = 1, 14 do
  local k = rnd:NextInteger(2, #CL - 1); local a, b = CL[k], CL[k + 1]; local t = rnd:NextNumber()
  local x, y = a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t
  local dx, dy = b[1] - a[1], b[2] - a[2]; local L = math.sqrt(dx * dx + dy * dy); local side = rnd:NextNumber() < 0.5 and -1 or 1
  x, y = x - dy / L * side * rnd:NextNumber(0.45, 0.75), y + dx / L * side * rnd:NextNumber(0.45, 0.75)
  local s = rnd:NextNumber(0.6, 1.3) * S
  local p = Instance.new("Part"); p.Name = "Kroos"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
  p.Transparency = 1; p.Size = Vector3.new(s, 0.02, s * rnd:NextNumber(0.6, 1)); p.CFrame = CFrame.new(W(x, y, WY + 0.02)) * CFrame.Angles(0, rnd:NextNumber(0, 6.28), 0)
  local d = Instance.new("Decal"); d.Face = Enum.NormalId.Top; d.Texture = "rbxassetid://" .. IDS.kroos; d.Color3 = Color3.fromRGB(150, 165, 120); d.Transparency = 0.1; d.Parent = p; p.Parent = F
end
for _, c in ipairs(workspace.SprookjesboomStenen:GetChildren()) do
  if c.Position.Y - c.Size.Y / 2 < WY + 0.5 then
    if not c:GetAttribute("DroogKleur") then c:SetAttribute("DroogKleur", c.Color) end
    c.Color = c:GetAttribute("DroogKleur"):Lerp(Color3.fromRGB(58, 60, 58), 0.45); c.Reflectance = 0.06
  end
end
return "water opgebouwd (zet daarna BeekStroming.client.luau als LocalScript in StarterPlayerScripts)"
