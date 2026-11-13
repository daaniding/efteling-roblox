-- Prinsenpoort: middenpoort + 2 torens + bruggetje + grachtje. Asset uit build/09_export_roblox.py (bouw_alles.sh).
-- Model: -Y = voorkant (plein), +X = OSM (0.250, -0.968), oorsprong = midden OSM-footprint = studs (151.58, -228.65), grond Y=2 (asset-brief.md).
local MODEL = 74186202233056
local TEX = {baksteen_poort = {100203940861419, 116169477876700}, baksteen_torens = {71030263605060, 74001330732660}, klimop = {88314417435691},
	leien = {121136605195305, 114227496015116}, steen = {116865063925741}}
local COLL = {}   -- ingevuld hieronder uit exports/poort_extra.json (zelfde volgorde)
local F = Vector3.new(-0.968, 0, 0.250)
local ORIGIN = CFrame.new(151.58, 2.0, -228.65) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	kassei = {Color3.fromRGB(150, 146, 138), "Cobblestone"}, goud = {Color3.fromRGB(214, 168, 72), "Metal"}, ijzer = {Color3.fromRGB(26, 30, 30), "Metal"},
	hout = {Color3.fromRGB(46, 96, 72), "Wood"}, venster = {Color3.fromRGB(14, 14, 14), "SmoothPlastic"}, glaslamp = {Color3.fromRGB(255, 226, 170), "Glass"},
	brons = {Color3.fromRGB(110, 90, 58), "Metal"}, water = {Color3.fromRGB(38, 46, 30), "SmoothPlastic"}, bodem = {Color3.fromRGB(70, 56, 40), "Ground"},
	gras = {Color3.fromRGB(104, 124, 72), "LeafyGrass"}, kraai = {Color3.fromRGB(10, 10, 12), "SmoothPlastic"}, snavel = {Color3.fromRGB(40, 34, 26), "SmoothPlastic"},
}
local GEEN_SCHADUW = {water = true, bodem = true, kassei = true, ijzer = true}
local BOTSEN = {kassei = true}

local oud = workspace:FindFirstChild("Prinsenpoort"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Prinsenpoort"
for _, o in ipairs(game:GetObjects("rbxassetid://" .. MODEL)) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = workspace; m:ScaleTo(S)
local anker
for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
m:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
local bots = Instance.new("Folder"); bots.Name = "Botsing"; bots.Parent = m
local onbekend = {}
for _, p in ipairs(m:GetChildren()) do
	if not p:IsA("BasePart") then continue end
	p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = true
	if string.match(p.Name, "^LAMP_") then
		p.Transparency = 1; p.CastShadow = false; p.CanQuery = false; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Name = "Lamp"
		local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 120); pl.Range = 14; pl.Brightness = 1.2; pl.Shadows = false; pl.Parent = p
	elseif string.match(p.Name, "^COLL_") then
		table.insert(COLL, p.CFrame); p.Transparency = 1; p.CanCollide = true; p.CastShadow = false; p.CanQuery = false
		p.CollisionFidelity = Enum.CollisionFidelity.Box; p.Parent = bots
	else
		local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$")
		local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
		if tex and TEX[tex] then
			p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
			if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
			if tex == "klimop" then sa.AlphaMode = Enum.AlphaMode.Transparency; p.CastShadow = false end
			if tex == "leien" then sa.Color = Color3.fromRGB(196, 150, 124) elseif tex == "steen" then sa.Color = Color3.fromRGB(170, 166, 158) end
			sa.Parent = p
			if string.find(tex, "baksteen") or tex == "steen" then p.CanCollide = true; p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end
		elseif key and M[key] then
			local s = M[key]; p.Color = s[1]; p.Material = Enum.Material[s[2]]; if s[3] then p.MaterialVariant = s[3] end
			if GEEN_SCHADUW[key] then p.CastShadow = false end
			if BOTSEN[key] then p.CanCollide = true; p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end
			if key == "water" then p.Transparency = 0.05; p.Reflectance = 0 end
		else table.insert(onbekend, p.Name) end
	end
end
m.WorldPivot = ORIGIN
-- layout-blok en zwevend label weg
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do if string.find(string.lower(d.Name), "prinsen") then d:Destroy() end end end
-- planten/bomen van andere scenes in de poort, op de brug en in het grachtje weghalen
local weg = 0
local function binnen(pos) local l = ORIGIN:PointToObjectSpace(pos); local x, y = -l.X / S, l.Z / S
	return (math.abs(x) < 4.5 and y > -2.3 and y < 2.4) or (math.abs(x) < 5.6 and y < -2.2 and y > -4.3) end
for _, f in ipairs(workspace:GetChildren()) do
	local n = f.Name
	if f ~= m and (string.find(n, "Groen") or string.find(n, "Bos") or string.find(n, "Horizon") or string.find(n, "Oever")) then
		for _, t in ipairs(f:GetChildren()) do
			local p = t:IsA("Model") and t:GetPivot().Position or (t:IsA("BasePart") and t.Position)
			if p and binnen(p) then t:Destroy(); weg += 1 end
		end
	end
end
-- terrein: grachtje uitgraven (cellen van 4 studs, alleen cellen met het midden in het blok) en gras onder de oevers
local T = workspace.Terrain
for x = -4.3, 4.31, 0.6 do for y = -2.65, -3.76, -0.55 do
	local p = lokaal(x, y, 0).Position
	T:FillBlock(CFrame.new(p.X, 0.5, p.Z), Vector3.new(3.4, 9, 3.4), Enum.Material.Air)
end end
local ids = {}
for _, sa in ipairs(m:GetDescendants()) do if sa:IsA("SurfaceAppearance") then
	for _, id in ipairs({sa.ColorMap, sa.NormalMap}) do if id ~= "" then local d = Instance.new("Decal"); d.Texture = id; table.insert(ids, d) end end end end
local ok = 0
game:GetService("ContentProvider"):PreloadAsync(ids, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end)
return string.format("poort %d delen, botsing %d, %d planten weg, textures %d/%d; onbekend: %s", #m:GetChildren(), #bots:GetChildren(), weg, ok, #ids, table.concat(onbekend, ","))
