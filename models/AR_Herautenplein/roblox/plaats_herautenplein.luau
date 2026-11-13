-- Herautenplein + Kikkerkoningfontein. Asset uit build/bouw_alles.sh. Zelfde frame als de Prinsenpoort:
-- oorsprong OSM (50.53, 76.22) = studs (151.58, -228.65), grond Y=2, -Y = van de poort het plein op. Kikkers: plaats_kikkers.luau. Groen: plaats_herautenplein_groen.luau.
local MODEL = 121494619592510
local TEX = {baksteen_bakken = {127855816549370, 122906145682863}, baksteen_fontein = {86692309367866, 79219781188509}, steen = {89179325609814}}
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
			if key == "gras" or key == "kassei" or key == "taxus" or key == "haag" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end) end   -- grote vlakken verdwijnen anders op afstand
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
-- layout-blokken en planten/bomen van andere scenes binnen de pleinomtrek (OSM-relatie 2907394) weghalen; terrein eronder Ground, bosje Grass
local OMTREK = {{17.45, -53.31}, {16.21, -50.38}, {15.12, -46.05}, {15.8, -15.1}, {17.68, -15.16}, {17.69, -12.65}, {19.69, -12.7}, {19.8, -7.07}, {18.2, -5.37}, {11.29, -5.21}, {11.22, -6.96}, {8.88, -6.8}, {8.83, -8.53}, {-0.11, -8.43}, {-18.9, -8.38}, {-19.22, -25.89}, {-16.72, -25.93}, {-16.84, -32.91}, {-19.04, -32.87}, {-19.05, -33.66}, {-19.21, -38.58}, {-20.68, -41.35}, {-20.64, -43.73}, {-19.39, -44.44}, {-16.13, -46.28}, {-16.42, -52.14}, {-16.7, -57.46}, {-17.01, -61.54}, {-15.72, -61.59}, {-14.57, -61.68}, {-13.41, -63.48}, {-12.5, -63.92}, {-11.74, -64.39}, {-11.09, -64.91}, {-10.49, -65.48}, {-9.92, -66.17}, {-9.52, -66.75}, {-9.09, -67.54}, {-8.7, -68.56}, {-8.47, -69.42}, {-6.78, -71.07}, {-7.61, -72.13}, {-8.44, -73.17}, {-6.59, -77.12}, {-6.12, -76.34}, {-5.18, -75.81}, {-3.77, -75.99}, {-2.96, -76.52}, {-2.76, -78.01}, {2.42, -80.74}, {2.78, -80.04}, {4.85, -81.13}, {6.96, -82.24}, {5.22, -85.57}, {8.0, -86.56}, {12.54, -86.37}, {10.92, -84.01}, {9.64, -83.94}, {8.72, -82.41}, {8.21, -80.99}, {9.17, -80.2}, {10.14, -79.41}, {12.15, -79.33}, {12.29, -79.64}, {18.72, -75.22}, {20.55, -73.97}, {20.14, -62.83}}
local BOSJE = {{-6.5, -62.66}, {-5.36, -57.87}, {-3.2, -55.31}, {-3.61, -54.16}, {-13.44, -54.03}, {-13.77, -57.2}, {-10.34, -61.27}, {-7.37, -63.68}}
local function inpoly(poly, x, y)
	local c = false; local j = #poly
	for i = 1, #poly do local a, b = poly[i], poly[j]
		if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c
end
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do local n = string.lower(d.Name)
	if string.find(n, "kikker") or string.find(n, "heraut") then d:Destroy() end end end
local weg = 0
for _, f in ipairs(workspace:GetChildren()) do
	local n = f.Name
	if f ~= m and (string.find(n, "Groen") or string.find(n, "Bos") or string.find(n, "Horizon") or string.find(n, "Oever")) and n ~= "HerautenpleinGroen" then
		for _, t in ipairs(f:GetChildren()) do
			local p = t:IsA("Model") and t:GetPivot().Position or (t:IsA("BasePart") and t.Position)
			if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
				if inpoly(OMTREK, x, y) or (math.abs(x) < 1.7 and y < -4.2 and y > -8.6) then t:Destroy(); weg += 1 end end
		end
	end
end
do local T = workspace.Terrain
	for x = -22, 21, 1 do for y = -4, -88, -1 do
		local onder = inpoly(OMTREK, x, y) or (math.abs(x) < 1.7 and y < -4.2)
		if onder then local p = lokaal(x, y, 0).Position
			local r = Region3.new(Vector3.new(p.X - 0.5, -4, p.Z - 0.5), Vector3.new(p.X + 0.5, 4, p.Z + 0.5)):ExpandToGrid(4)
			if inpoly(BOSJE, x, y) then T:ReplaceMaterial(r, 4, Enum.Material.Ground, Enum.Material.LeafyGrass)
			else T:ReplaceMaterial(r, 4, Enum.Material.Grass, Enum.Material.Ground); T:ReplaceMaterial(r, 4, Enum.Material.LeafyGrass, Enum.Material.Ground) end
		end
	end end
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
