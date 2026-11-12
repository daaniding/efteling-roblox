-- Assepoester plaatsen (asset uit build/09_export_roblox.py). Blender: gevel kijkt naar -Y (west), +X = zuid,
-- oorsprong = voorkant uitgangsportiek, midden gevel; z=0 = maaiveld. OSM-kalibratie zie STATUS.md:
-- modeloorsprong = OSM (-3.18, 95.15) m = studs (-9.54, -285.44); kijkrichting Roblox (-0.983, 0, 0.185); grond Y=2.
local ASSET = 108022246144519   -- v1: vormen (03_forms), kubus-UV's 1 UV = 2 m
local F = Vector3.new(-0.9828, 0, 0.1846)
local ORIGIN = CFrame.new(-9.54, 2.0, -285.44) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end   -- Blender (x,y,z) meters -> wereld
local M = {   -- {kleur, materiaal, variant} naar ref/front.jpg, getemperd (WERKWIJZE)
	stuc = {Color3.fromRGB(186, 183, 170), "Plaster", "VV_Pleister"}, omlijsting = {Color3.fromRGB(204, 200, 186), "Limestone", "VV_Steen"},
	plint = {Color3.fromRGB(150, 148, 140), "Concrete"}, groen = {Color3.fromRGB(58, 98, 98), "Wood"},
	pannen = {Color3.fromRGB(150, 92, 72), "ClayRoofTiles"},   -- VV_Lei (leien-textuur) was bijna zwart baksteen = {Color3.fromRGB(140, 70, 52), "Brick"},
	hout = {Color3.fromRGB(104, 56, 34), "Wood"}, glas = {Color3.fromRGB(26, 32, 34), "SmoothPlastic"},
	lood = {Color3.fromRGB(52, 54, 56), "Metal"}, zink = {Color3.fromRGB(96, 112, 118), "Metal"},
	kozijn = {Color3.fromRGB(220, 212, 190), "SmoothPlastic"}, donker = {Color3.fromRGB(8, 8, 8), "SmoothPlastic"},
	achter = {Color3.fromRGB(140, 140, 132), "Concrete"},
}
local BOTSING = {stuc = true, omlijsting = true, plint = true, groen = true, achter = true, hout = true, donker = true}

local oud = workspace:FindFirstChild("Assepoester"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Assepoester"
for _, o in ipairs(game:GetObjects("rbxassetid://" .. ASSET)) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = workspace; m:ScaleTo(S)
local anker
for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
assert(anker, "geen anker")
local told = CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0))   -- anker op Blender z=-2
m:PivotTo(ORIGIN * told:Inverse() * m:GetPivot())
anker:Destroy()
local onbekend = {}
for _, p in ipairs(m:GetChildren()) do
	p.Anchored = true; p.CanTouch = false
	local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
	local s = key and M[key]
	if s then
		p.Color = s[1]; p.Material = Enum.Material[s[2]]; if s[3] then p.MaterialVariant = s[3] end
	else table.insert(onbekend, p.Name) end
	if key == "glas" then p.Reflectance = 0.12 end
	p.CanCollide = BOTSING[key] == true; p.CanQuery = p.CanCollide
	p.CastShadow = key ~= "donker"
end
m.WorldPivot = ORIGIN
-- geen zwevend layout-label bij gebouwde dingen (Daan)
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do if d:IsA("BillboardGui") and d.Parent and d.Parent.Name == "Assepoester" then d:Destroy() end end end
-- spawn op de binnenplaats, 12 m voor de gevel, kijkend naar het huis (oude plek blijft in het attribuut OudeCFrame)
local sp = workspace:FindFirstChildWhichIsA("SpawnLocation", true)
if sp then
	if sp:GetAttribute("OudeCFrame") == nil then sp:SetAttribute("OudeCFrame", sp.CFrame) end
	local pos = lokaal(-1.5, -12, 0).Position
	sp.CFrame = CFrame.lookAt(pos + Vector3.new(0, 0.2 + sp.Size.Y / 2, 0), lokaal(-1.5, 0, 0).Position + Vector3.new(0, 0.2 + sp.Size.Y / 2, 0))
end
return string.format("Assepoester: %d delen, onbekend: %s", #m:GetChildren(), table.concat(onbekend, ","))
