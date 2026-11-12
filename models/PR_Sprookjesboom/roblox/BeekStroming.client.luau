-- StarterPlayer.StarterPlayerScripts.BeekStroming (LocalScript). Geplaatst door plaats_water.luau.
-- Beekje bij de Sprookjesboom: stromende rimpel-/sliblagen en drijvende eikenblaadjes (alleen bij de speler, geen netwerk).
local RS = game:GetService("RunService")
local F = workspace:WaitForChild("SprookjesboomWater")
local om = workspace:WaitForChild("SprookjesboomOmgeving")
local water
repeat   -- onderdelen komen pas na het starten binnen (replicatie)
  for _, p in ipairs(om:GetChildren()) do if string.match(p.Name, "^water_") then water = p end end
  if not water then task.wait(0.5) end
until water
local lagen = {Slib = {0.10, 0.03}, Rimpels = {0.55, 0.08}, Rimpels2 = {0.35, -0.05}}   -- studs/s in U en V
local pts = {}
local mid = F:WaitForChild("Middellijn")
while #mid:GetChildren() < (F:GetAttribute("Punten") or 2) do task.wait(0.5) end
local kids = mid:GetChildren()
table.sort(kids, function(a, b) return a.Name < b.Name end)
for _, v in ipairs(kids) do table.insert(pts, v.Value) end
local cum = {0}
for i = 2, #pts do cum[i] = cum[i - 1] + (pts[i] - pts[i - 1]).Magnitude end
local total = cum[#cum]
local function op(s)
  s = s % total
  for i = 2, #pts do
    if s <= cum[i] then local t = (s - cum[i - 1]) / (cum[i] - cum[i - 1]); return pts[i - 1]:Lerp(pts[i], t), (pts[i] - pts[i - 1]).Unit end
  end
  return pts[#pts], (pts[#pts] - pts[#pts - 1]).Unit
end
local WY = F:GetAttribute("WaterY")
local tex = F:GetAttribute("BladTextuur")
local bladeren = {}
local rnd = Random.new()
for i = 1, 12 do
  local p = Instance.new("Part"); p.Name = "DrijvendBlad"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
  p.CastShadow = false; p.Transparency = 1; local s = rnd:NextNumber(0.35, 0.55); p.Size = Vector3.new(s * 0.7, 0.02, s)
  local d = Instance.new("Decal"); d.Face = Enum.NormalId.Top; d.Texture = tex; d.Parent = p
  p.Parent = workspace
  table.insert(bladeren, {part = p, s = rnd:NextNumber(0, total), lat = rnd:NextNumber(-0.9, 0.9), spd = rnd:NextNumber(0.25, 0.45),
    rot = rnd:NextNumber(0, 6.28), rs = rnd:NextNumber(-0.25, 0.25), fase = rnd:NextNumber(0, 6.28)})
end
local t = 0
RS.RenderStepped:Connect(function(dt)
  t += dt
  for _, tx in ipairs(water:GetChildren()) do
    local l = tx:IsA("Texture") and lagen[tx.Name]
    if l then tx.OffsetStudsU = (tx.OffsetStudsU + l[1] * dt) % tx.StudsPerTileU; tx.OffsetStudsV = (tx.OffsetStudsV + l[2] * dt) % tx.StudsPerTileV end
  end
  for _, b in ipairs(bladeren) do
    b.s += b.spd * dt
    if b.s > total - 0.5 then b.s = 0; b.lat = rnd:NextNumber(-0.9, 0.9) end      -- terug naar bovenstrooms
    local pos, dir = op(b.s)
    local side = Vector3.new(-dir.Z, 0, dir.X)
    b.rot += b.rs * dt
    local deining = math.sin(t * 1.3 + b.fase) * 0.015
    b.part.CFrame = CFrame.new(Vector3.new(pos.X, WY + 0.03 + deining, pos.Z) + side * b.lat) * CFrame.Angles(0, b.rot, math.sin(t + b.fase) * 0.05)
  end
end)
