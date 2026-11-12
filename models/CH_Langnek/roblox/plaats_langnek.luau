-- Langnek plaatsen (asset uit build/09_export_roblox.py). Blender-oorsprong = Langnek-punt op pleinhoogte; figuur kijkt naar Blender -Y.
-- OSM-kalibratie: oorsprong OSM (145.91, -33.66) m -> studs (437.7, 101.0); kijkt ZZO (OSM (0.6,-0.8) -> Roblox (0.6,0,0.8)); grond Y=2.
-- Daarna: water net boven het maaiveld, kroos + rimpels (klonen uit SprookjesboomWater), beplanting in LangnekGroen (wind doet mee).
local ASSET = 106939403351913
local ORIGIN = CFrame.new(437.7, 2.0, 101.0) * CFrame.Angles(0, math.atan2(-0.6, -0.8), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end   -- Blender (x,y,z) meters -> wereld
local function mat(n) local ok, e = pcall(function() return Enum.Material[n] end); return ok and e or Enum.Material.SmoothPlastic end
local M = {   -- getemperde kleuren (WERKWIJZE), naar ref/front.jpg
	huid = {Color3.fromRGB(212, 156, 122), "SmoothPlastic"}, lip = {Color3.fromRGB(150, 76, 62), "SmoothPlastic"},
	tuniek = {Color3.fromRGB(204, 158, 66), "Fabric"}, broek = {Color3.fromRGB(54, 92, 96), "Fabric"},
	cape = {Color3.fromRGB(150, 48, 34), "Fabric"}, laars = {Color3.fromRGB(156, 54, 38), "SmoothPlastic"},
	riem = {Color3.fromRGB(84, 50, 26), "Leather"}, gesp = {Color3.fromRGB(150, 118, 64), "Metal"},
	touw = {Color3.fromRGB(196, 176, 134), "Fabric"}, haar = {Color3.fromRGB(44, 32, 24), "Fabric"},
	oogwit = {Color3.fromRGB(236, 232, 222), "SmoothPlastic"}, iris = {Color3.fromRGB(92, 50, 22), "SmoothPlastic"},
	pupil = {Color3.fromRGB(12, 12, 12), "SmoothPlastic"}, binnen = {Color3.fromRGB(30, 14, 10), "SmoothPlastic"},
	rots = {Color3.fromRGB(122, 126, 124), "Rock"}, randsteen = {Color3.fromRGB(170, 164, 150), "Limestone"},
	kei = {Color3.fromRGB(150, 144, 134), "Slate"}, water = {Color3.fromRGB(34, 40, 26), "SmoothPlastic"},
	hek = {Color3.fromRGB(28, 46, 32), "Metal"},
}
local BOTSING = {rots = true, randsteen = true, hek = true, kei = true}

for _, n in ipairs({"Langnek", "LangnekGroen", "LangnekWater"}) do local o = workspace:FindFirstChild(n); if o then o:Destroy() end end
local m = Instance.new("Model"); m.Name = "Langnek"
for _, o in ipairs(game:GetObjects("rbxassetid://" .. ASSET)) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = workspace; m:ScaleTo(S)
local anker
for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
assert(anker, "geen anker")
local told = CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0))   -- Blender (x,y,z) komt binnen als (-x,z,y)*S, anker op z=-2
m:PivotTo(ORIGIN * told:Inverse() * m:GetPivot())
anker:Destroy()
local onbekend, water = {}, nil
for _, p in ipairs(m:GetChildren()) do
	p.Anchored = true; p.CanTouch = false
	local groep, key = string.match(p.Name, "^(%w+)__MAT_([%a_]+)_%d+$")
	local s = key and M[key]
	if s then p.Color = s[1]; p.Material = mat(s[2]) else table.insert(onbekend, p.Name) end
	p.CanCollide = BOTSING[key] == true
	p.CanQuery = BOTSING[key] == true
	if key == "water" then
		water = p
		p.Reflectance = 0.15; p.CastShadow = false
		p.CFrame = p.CFrame + Vector3.new(0, 2.12 - p.Size.Y / 2 - p.Position.Y, 0)   -- spiegel net boven het maaiveld
	end
	p:SetAttribute("Groep", groep)
end
m:SetAttribute("NekOmlaag", 5.55 * S)          -- slag: zichtbare nek 5.90 m uit -> 0.35 m in
m:SetAttribute("OogStraal", 0.163 * S)         -- iris ligt 0.163 m voor het oogcentrum
m.WorldPivot = ORIGIN
local marker = workspace:FindFirstChild("EftelingLayout") and workspace.EftelingLayout:FindFirstChild("Langnek", true)
if marker then for _, c in ipairs(marker:GetChildren()) do if c:IsA("BillboardGui") then c:Destroy() end end end

-- ===== levend water: kroos en rimpels (zelfde bronnen als de Sprookjesboom-vijver)
local wf = Instance.new("Folder"); wf.Name = "LangnekWater"; wf.Parent = workspace
local bron = workspace:FindFirstChild("SprookjesboomWater")
local kroosT = bron and bron:FindFirstChild("Kroos"); local rimpelT = bron and bron:FindFirstChild("Rimpelbron")
local rng = Random.new(1952)
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include
water.CanQuery = true
rp.FilterDescendantsInstances = {m}
local function opWater(x, y)
	local cf = lokaal(x, y, 3)
	local hit = workspace:Raycast(cf.Position, Vector3.new(0, -20, 0), rp)
	return hit and hit.Instance == water and hit.Position or nil
end
local kroosN, rimpelN = 0, 0
for _ = 1, 400 do
	local x, y = rng:NextNumber(-7, 7), rng:NextNumber(-7, 7)
	local pos = opWater(x, y)
	if pos and kroosT and kroosN < 22 then
		local k = kroosT:Clone(); k.Anchored = true; k.CanCollide = false; k.CanQuery = false; k.CanTouch = false
		k.Size = Vector3.new(rng:NextNumber(1.6, 3.6), 0.02, rng:NextNumber(1.4, 3.0))
		k.CFrame = CFrame.new(pos + Vector3.new(0, 0.03, 0)) * CFrame.Angles(0, rng:NextNumber(0, math.pi * 2), 0)
		k.Parent = wf; kroosN += 1
	elseif pos and rimpelT and rimpelN < 5 then
		local r = rimpelT:Clone(); r.Anchored = true; r.CFrame = CFrame.new(pos + Vector3.new(0, 0.05, 0)); r.Parent = wf; rimpelN += 1
	end
end
water.CanQuery = false

-- ===== beplanting achter en naast de rots (front.jpg / overview: sparren, taxus, rododendron, varens)
local ss = game:GetService("ServerStorage")
local V3 = ss:FindFirstChild("BomenBronV3"); local ECHT = ss:FindFirstChild("VVEchtePlanten")
local groen = Instance.new("Folder"); groen.Name = "LangnekGroen"; groen.Parent = workspace
local function zet(bronModel, x, y, schaal, draai)
	if not bronModel then return end
	local c = bronModel:Clone()
	c:ScaleTo(c:GetScale() * schaal)
	local cf, size = c:GetBoundingBox()
	local voet = lokaal(x, y, 0).Position
	c:PivotTo(CFrame.new(voet + Vector3.new(0, size.Y / 2 - 0.15, 0)) * CFrame.Angles(0, draai or rng:NextNumber(0, 6.28), 0) * cf:ToObjectSpace(c:GetPivot()))
	for _, d in ipairs(c:GetDescendants()) do
		if d:IsA("BasePart") then d.Anchored = true; d.CanCollide = false; d.CanTouch = false end
	end
	c.Parent = groen
	return c
end
local P = {   -- {bron, x, y, schaal}  (Blender-meters: +y = achter de figuur, +x = links van de figuur)
	{"den0", -3.5, 7.5, 3.0}, {"den1", 4.0, 8.5, 3.2}, {"den0", 0.8, 11.0, 3.4},
	{"taxus0", -5.6, 4.0, 3.0}, {"taxus1", 5.6, 4.6, 3.0}, {"taxus0", -1.6, 6.2, 3.2}, {"taxus1", 2.6, 6.0, 3.0},
	{"rododendron0", -6.9, 1.2, 3.0}, {"rododendron1", 7.0, 1.8, 3.2}, {"rododendron1", -4.9, 6.4, 3.0}, {"rododendron0", 4.7, 6.8, 2.8},
	{"eik0", -9.5, 11.5, 3.0}, {"beuk1", 9.0, 12.5, 3.0},
}
for _, e in ipairs(P) do zet(V3 and V3:FindFirstChild(e[1]), e[2], e[3], e[4]) end
local varens = {}
if ECHT then for _, c in ipairs(ECHT:GetChildren()) do if c.Name:find("fern") or c.Name:find("shrub_03") then table.insert(varens, c) end end end
local rotsMid = lokaal(0, 0.3, 0).Position
for i = 1, 34 do
	if #varens == 0 then break end
	local a = rng:NextNumber(math.rad(-25), math.rad(205)); local r = rng:NextNumber(3.9, 5.6)
	local x, y = math.cos(a) * r, 0.4 + math.sin(a) * r
	if y > 0.5 then zet(varens[rng:NextInteger(1, #varens)], x, y, 3.0 * rng:NextNumber(0.8, 1.3)) end
end
-- wind laat ook deze map wiegen
local wind = game:GetService("StarterPlayer").StarterPlayerScripts:FindFirstChild("Wind")
if wind and not wind.Source:find("LangnekGroen") then
	wind.Source = wind.Source:gsub('"VillaVoltaHorizon" }', '"VillaVoltaHorizon", "LangnekGroen" }', 1)
end
print("Langnek geplaatst:", #m:GetChildren(), "delen, kroos", kroosN, "rimpels", rimpelN, "groen", #groen:GetChildren(), "onbekend:", table.concat(onbekend, ", "))
