-- Sprookjesboom + paddenstoelen plaatsen (gegenereerd door maak_plaatsscript.py uit plaats_template.luau).
-- Blender-oorsprong = stamhart op maaiveld; gezicht kijkt naar het zuiden (+Z). OSM (40.48, 198.19) m -> studs (121.44, -594.57).
-- Import geeft Blender (x,y,z) als (-x,z,y)*S; 180 graden draaien zet het gezicht op het zuiden. Grond Y = 2 (vlak terrein; AHN-reliëf later).
local ID = __IDS__
local S = 3
local GROUND = 1.95
local ORIGIN = CFrame.new(121.44, GROUND, -594.57) * CFrame.Angles(0, math.pi, 0)
local KLEIN = __KLEIN__        -- {x, y, schaal, draaiing} in boom-meters (Blender: x oost, y noord)
local MUZIEK = __MUZIEK__      -- {studsX, studsZ, draaiing} uit OSM
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end

local function laad(id, naam, parent)
  local m = Instance.new("Model"); m.Name = naam
  for _, o in ipairs(game:GetObjects("rbxassetid://" .. id)) do o.Parent = m end
  for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
  for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
  m.Parent = parent; m:ScaleTo(S)
  local anker
  for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
  assert(anker, "geen anker in " .. naam)
  local told = CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0))
  m:PivotTo(CFrame.new() * told:Inverse() * m:GetPivot())   -- oorsprong naar (0,0,0), daarna per kopie plaatsen
  anker:Destroy()
  for _, p in ipairs(m:GetChildren()) do p.Anchored = true; p.CanTouch = false end
  m.WorldPivot = CFrame.new()
  return m
end

local function sa(p, kleur, normaal, ruw, alpha)
  local s = Instance.new("SurfaceAppearance")
  if kleur then s.ColorMap = "rbxassetid://" .. kleur end
  if normaal then s.NormalMap = "rbxassetid://" .. normaal end
  if ruw then s.RoughnessMap = "rbxassetid://" .. ruw end
  if alpha then s.AlphaMode = Enum.AlphaMode.Transparency end
  s.Parent = p
end

-- oude versie weg
for _, n in ipairs({"Sprookjesboom", "SprookjesboomPaddenstoelen", "MuzikalePaddenstoelen"}) do
  local o = workspace:FindFirstChild(n); if o then o:Destroy() end
end

-- de boom
local boom = laad(ID.boom, "Sprookjesboom", workspace)
local kleuren = {
  Oogwit = Color3.fromRGB(230, 224, 209), Iris = Color3.fromRGB(168, 107, 51), Pupil = Color3.fromRGB(8, 8, 8),
  hollow_dark = Color3.fromRGB(10, 8, 6),
}
for _, p in ipairs(boom:GetChildren()) do
  local n = string.lower(p.Name)
  p.CanCollide = false; p.CastShadow = true
  if string.find(n, "stam_baked") then
    p.CanCollide = true; sa(p, ID.stam_kleur, ID.stam_normaal, ID.stam_ruw)
  elseif string.find(n, "branch") then
    sa(p, ID.schors, nil, nil); p.Color = Color3.fromRGB(150, 140, 125)
  elseif string.find(n, "leaf") then
    sa(p, ID.blad, nil, nil, true); p.CastShadow = true
  elseif string.find(n, "eye_white") then p.Color = kleuren.Oogwit; p.Material = Enum.Material.SmoothPlastic
  elseif string.find(n, "eye_iris") then p.Color = kleuren.Iris; p.Material = Enum.Material.SmoothPlastic
  elseif string.find(n, "eye_pupil") then p.Color = kleuren.Pupil; p.Material = Enum.Material.SmoothPlastic
  elseif string.find(n, "hollow_dark") then p.Color = kleuren.hollow_dark; p.Material = Enum.Material.SmoothPlastic; p.CastShadow = false
  end
end
boom:PivotTo(ORIGIN)

-- paddenstoelen: kleur per onderdeel
local PAD = {
  hoed = {Color3.fromRGB(219, 120, 117), Enum.Material.SmoothPlastic}, stip = {Color3.fromRGB(242, 237, 229), Enum.Material.Plastic},
  steel = {Color3.fromRGB(237, 232, 219), Enum.Material.Plastic}, plaatjes = {Color3.fromRGB(224, 204, 178), Enum.Material.Plastic},
}
local PADM = {
  hoed = {Color3.fromRGB(158, 38, 18), Enum.Material.SmoothPlastic}, stip = {Color3.fromRGB(235, 230, 217), Enum.Material.Sand},
  steel = {Color3.fromRGB(219, 212, 191), Enum.Material.Concrete}, plaatjes = {Color3.fromRGB(204, 189, 163), Enum.Material.Plastic},
}
local function kleur(m, tabel, botsen)
  for _, p in ipairs(m:GetChildren()) do
    local key = string.match(p.Name, "^(%a+)_%d+$")
    local s = key and tabel[key]
    if s then p.Color = s[1]; p.Material = s[2] end
    p.CanCollide = botsen
  end
end
local klein = laad(ID.klein, "PaddenstoelKlein", nil); kleur(klein, PAD, false)
local fk = Instance.new("Model"); fk.Name = "SprookjesboomPaddenstoelen"
for i, k in ipairs(KLEIN) do
  local c = klein:Clone(); c.Name = "Paddenstoel" .. i
  c:ScaleTo(S * k[3]); c:PivotTo(lokaal(k[1], k[2], 0) * CFrame.Angles(0, math.rad(k[4]), 0)); c.Parent = fk
end
fk.Parent = workspace
local muz = laad(ID.muziek, "MuzikalePaddenstoel", nil); kleur(muz, PADM, true)
local fm = Instance.new("Model"); fm.Name = "MuzikalePaddenstoelen"
for i, k in ipairs(MUZIEK) do
  local c = muz:Clone(); c.Name = "MuzikalePaddenstoel" .. i
  c:PivotTo(CFrame.new(k[1], GROUND, k[2]) * CFrame.Angles(0, math.rad(k[3]), 0)); c.Parent = fm
end
fm.Parent = workspace
klein:Destroy(); muz:Destroy()
return ("boom %d delen, %d kleine en %d muzikale paddenstoelen"):format(#boom:GetChildren(), #KLEIN, #MUZIEK)
