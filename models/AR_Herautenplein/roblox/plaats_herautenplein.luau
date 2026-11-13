-- Herautenplein + Kikkerkoningfontein. Asset uit build/bouw_alles.sh. Zelfde frame als de Prinsenpoort:
-- oorsprong OSM (50.53, 76.22) = studs (151.58, -228.65), grond Y=2, -Y = van de poort het plein op. Kikkers: aparte map (generate_mesh).
local MODEL = 81541689190400
local TEX = {baksteen_bakken = {134648861752621, 76042344713901}, baksteen_fontein = {86692309367866, 79219781188509}, steen = {102331535557394}}
local HAAG = {73997585762296, 114509386598524}
local F = Vector3.new(-0.968, 0, 0.250)
local ORIGIN = CFrame.new(151.58, 2.0, -228.65) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	kassei = {Color3.fromRGB(235, 228, 214), "Pebble", "VV_Grind"}, plavuis = {Color3.fromRGB(235, 228, 214), "Pebble", "VV_Grind"}, gras = {Color3.fromRGB(104, 124, 72), "LeafyGrass"},
	haag = {Color3.fromRGB(255, 255, 255), "Plastic"}, taxus = {Color3.fromRGB(255, 255, 255), "Plastic"}, bodem = {Color3.fromRGB(70, 56, 40), "Ground"},
	water = {Color3.fromRGB(52, 62, 40), "SmoothPlastic"}, rots = {Color3.fromRGB(58, 48, 42), "Basalt"}, goud = {Color3.fromRGB(214, 168, 72), "Metal"},
	hek = {Color3.fromRGB(30, 70, 56), "Metal"}, hout = {Color3.fromRGB(36, 78, 60), "Wood"}, paal = {Color3.fromRGB(70, 46, 30), "Wood"},
	ijzer = {Color3.fromRGB(26, 30, 30), "Metal"}, glaslamp = {Color3.fromRGB(255, 226, 170), "Glass"}, kant_papier = {Color3.fromRGB(236, 228, 204), "SmoothPlastic"},
	rood = {Color3.fromRGB(176, 34, 28), "SmoothPlastic"}, ruwsteen = {Color3.fromRGB(150, 146, 136), "Slate"}, binnenbak = {Color3.fromRGB(150, 160, 156), "SmoothPlastic"},
}
local GEEN_SCHADUW = {water = true, kassei = true, plavuis = true, gras = true, ijzer = true}
local BOTSEN = {kassei = true, plavuis = true, gras = true}
local oud = workspace:FindFirstChild("Herautenplein"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Herautenplein"
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
		p.Transparency = 1; p.CanCollide = true; p.CastShadow = false; p.CanQuery = false; p.CollisionFidelity = Enum.CollisionFidelity.Box; p.Parent = bots
	else
		local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$")
		local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
		if tex and TEX[tex] then
			p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
			if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
			if tex == "steen" then sa.Color = Color3.fromRGB(210, 204, 190) end
			sa.Parent = p; p.CanCollide = true; p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition
		elseif key and M[key] then
			local s = M[key]; p.Color = s[1]; p.Material = Enum.Material[s[2]]; if s[3] then p.MaterialVariant = s[3] end
			if GEEN_SCHADUW[key] then p.CastShadow = false end
			if BOTSEN[key] then p.CanCollide = true; p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end
			if key == "water" then p.Transparency = 0.05; p.Reflectance = 0 end
			if key == "haag" or key == "taxus" then
				local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. HAAG[1]; sa.NormalMap = "rbxassetid://" .. HAAG[2]
				sa.Color = key == "haag" and Color3.fromRGB(150, 175, 130) or Color3.fromRGB(105, 130, 95); sa.Parent = p
				p.CanCollide = true; p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition
			end
		else table.insert(onbekend, p.Name) end
	end
end
m.WorldPivot = ORIGIN
-- layout-blokken en planten/bomen van andere scenes op het plein weghalen
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do local n = string.lower(d.Name)
	if string.find(n, "kikker") or string.find(n, "heraut") then d:Destroy() end end end
local weg = 0
local function binnen(pos) local l = ORIGIN:PointToObjectSpace(pos); local x, y = -l.X / S, l.Z / S
	return math.abs(x) < 16 and y < -8.0 and y > -48.8 end
for _, f in ipairs(workspace:GetChildren()) do
	local n = f.Name
	if f ~= m and (string.find(n, "Groen") or string.find(n, "Bos") or string.find(n, "Horizon") or string.find(n, "Oever")) then
		for _, t in ipairs(f:GetChildren()) do
			local p = t:IsA("Model") and t:GetPivot().Position or (t:IsA("BasePart") and t.Position)
			if p and binnen(p) then t:Destroy(); weg += 1 end
		end
	end
end
-- terrein: grachtje rond de fontein uitgraven
local T = workspace.Terrain
for x = -3.6, 3.21, 0.6 do for y = -24.9, -32.1, -0.6 do
	local p = lokaal(x, y, 0).Position
	T:FillBlock(CFrame.new(p.X, 0.5, p.Z), Vector3.new(3.4, 9, 3.4), Enum.Material.Air)
end end
local ids = {}
for _, sa in ipairs(m:GetDescendants()) do if sa:IsA("SurfaceAppearance") then
	for _, id in ipairs({sa.ColorMap, sa.NormalMap}) do if id ~= "" then local d = Instance.new("Decal"); d.Texture = id; table.insert(ids, d) end end end end
local ok = 0
game:GetService("ContentProvider"):PreloadAsync(ids, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end)
return string.format("plein %d delen, botsing %d, %d planten weg, textures %d/%d; onbekend: %s", #m:GetChildren(), #bots:GetChildren(), weg, ok, #ids, table.concat(onbekend, ","))
