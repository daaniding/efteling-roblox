-- De Prinses op de Erwt (2025): huisje (dependance Grand Hotel) + pleintje. Gegenereerd door maak_plaatsscript.py; plakken in Studio execute_luau.
-- Modelframe: oorsprong = midden OSM 1406396369 = studs (-4.23, 41.58), -Y = voorkant (NO), -X = kijkraam (ZO), z 0 = maaiveld (Y 2).
local HUIS, OMG = @HUIS@, @OMG@
local TEXH = @TEXH@
local TEXO = @TEXO@
local COLLH = @COLLH@
local COLLO = @COLLO@
local PLEIN = @PLEIN@
local F = Vector3.new(0.524, 0, -0.851)
local ORIGIN = CFrame.new(-4.23, 2.0, 41.58) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(226, 214, 190), "Plastic"}, natuursteen = {Color3.fromRGB(196, 178, 140), "Limestone"}, koper = {Color3.fromRGB(96, 150, 130), "Metal"},
	goud = {Color3.fromRGB(205, 160, 60), "Metal"}, deur = {Color3.fromRGB(34, 70, 70), "SmoothPlastic"}, venster = {Color3.fromRGB(16, 22, 24), "SmoothPlastic"},
	ijzer = {Color3.fromRGB(20, 22, 22), "Metal"}, glaslamp = {Color3.fromRGB(248, 244, 232), "SmoothPlastic"}, lantaarnrood = {Color3.fromRGB(220, 60, 30), "Neon"},
	paneel = {Color3.fromRGB(76, 128, 128), "SmoothPlastic"}, rood = {Color3.fromRGB(160, 28, 26), "SmoothPlastic"}, huid = {Color3.fromRGB(226, 176, 140), "SmoothPlastic"},
	zwart = {Color3.fromRGB(14, 14, 14), "SmoothPlastic"}, creme = {Color3.fromRGB(232, 220, 190), "SmoothPlastic"}, hout = {Color3.fromRGB(94, 60, 36), "Wood"},
	baksteen = {Color3.fromRGB(150, 86, 64), "Brick"}, grind = {Color3.fromRGB(235, 228, 214), "Pebble"}, tegelzwart = {Color3.fromRGB(18, 18, 18), "SmoothPlastic"},
	tegelwit = {Color3.fromRGB(236, 236, 232), "SmoothPlastic"}, groen = {Color3.fromRGB(42, 78, 70), "SmoothPlastic"}, aarde = {Color3.fromRGB(58, 42, 30), "Ground"},
	papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"},
}
local TINT = {}
local preload = {}
local function plaats(id, naam, TEX, coll)
	local objs = game:GetObjects("rbxassetid://" .. id)
	local oud = workspace:FindFirstChild(naam); if oud then oud:Destroy() end
	local m = Instance.new("Model"); m.Name = naam
	for _, o in ipairs(objs) do o.Parent = m end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
	for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
	m.Parent = workspace; m:ScaleTo(S)
	local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
	m:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
	local bots = Instance.new("Folder"); bots.Name = "Botsing"; bots.Parent = m
	local lampen = Instance.new("Folder"); lampen.Name = "Lampen"; lampen.Parent = m
	local onbekend = {}
	for _, p in ipairs(m:GetChildren()) do
		if not p:IsA("BasePart") then continue end
		p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = false
		if string.match(p.Name, "^COLL_") then p:Destroy()
		elseif string.match(p.Name, "^LAMP_") then
			p.Transparency = 1; p.CastShadow = false; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Name = "Lamp"; p.Parent = lampen
			local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 130); pl.Range = 10; pl.Brightness = 0.7; pl.Shadows = false; pl.Parent = p
		else
			local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$"); local key = string.match(p.Name, "__MAT_([%w_]-)_%d+$")
			if tex and TEX[tex] then
				p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
				local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
				if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
				if TINT[tex] then sa.Color = TINT[tex] end
				sa.Parent = p; table.insert(preload, sa.ColorMap)
			elseif key and M[key] then
				p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
				if key == "grind" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end); p.CanQuery = true; pcall(function() p.MaterialVariant = "VV_Grind" end) end
				if key == "lantaarnrood" or key == "glaslamp" then p.CastShadow = false end
				if key == "venster" then p.Reflectance = 0 end
			else table.insert(onbekend, p.Name) end
		end
	end
	for _, c in ipairs(coll) do
		local b = Instance.new("Part"); b.Name = "Bots"; b.Anchored = true; b.Transparency = 1; b.CastShadow = false; b.CanTouch = false
		b.Size = Vector3.new(c[4] * S, math.max(c[6] * S, 0.05), c[5] * S)
		b.CFrame = lokaal(c[1], c[2], c[3]) * CFrame.Angles(0, math.rad(c[7]), 0); b.Parent = bots
	end
	m.WorldPivot = ORIGIN
	return m, onbekend
end
local mh, oh = plaats(HUIS, "PrinsesOpDeErwt", TEXH, COLLH)
task.wait()
local mo, oo = plaats(OMG, "PrinsesOpDeErwtPlein", TEXO, COLLO)
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
-- terrein: onder plein en huis Ground (grassprieten prikken anders door het grind); maaiveld blijft vlak
local T = workspace.Terrain; local n = 0
for gx = -13, 13, 4 / S do
	for gy = -10, 5, 4 / S do
		local w = (ORIGIN * CFrame.new(-gx * S, 0, gy * S)).Position
		local X, Z = math.floor(w.X / 4) * 4 + 2, math.floor(w.Z / 4) * 4 + 2
		local l = ORIGIN:PointToObjectSpace(Vector3.new(X, ORIGIN.Position.Y, Z)); local x, y = -l.X / S, l.Z / S
		if inside(x, y, PLEIN) then
			local r = Region3.new(Vector3.new(X - 2, -4, Z - 2), Vector3.new(X + 2, 4, Z + 2)):ExpandToGrid(4)
			for _, mat in ipairs({Enum.Material.Grass, Enum.Material.LeafyGrass, Enum.Material.Mud}) do T:ReplaceMaterial(r, 4, mat, Enum.Material.Ground) end
			n += 1
		end
	end
	task.wait()
end
-- planten/bomen die op het plein of in het huis staan weghalen; layout-label weg; spawn op het plein (oude plek bewaren)
local weg = 0
for _, f in ipairs(workspace:GetChildren()) do
	if (f:IsA("Folder") or f:IsA("Model")) and string.find(f.Name, "Groen$") or f.Name == "VillaVoltaHorizon" then
		for _, c in ipairs(f:GetChildren()) do
			local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
			if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
				if inside(x, y, PLEIN) then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do if d.Name == "De Prinses op de Erwt" then d:Destroy() end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then
	if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", sp.CFrame) end
	sp.CFrame = lokaal(2.2, -4.6, 0.2) * CFrame.Angles(0, math.pi, 0)
end
local ok = 0
pcall(function()
	local dec = {}; for _, id in ipairs(preload) do local d = Instance.new("Decal"); d.Texture = id; table.insert(dec, d) end
	game:GetService("ContentProvider"):PreloadAsync(dec, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end)
end)
local function onb(t) return #t > 0 and table.concat(t, ",") or "-" end
return string.format("huis %d delen, plein %d; grondcellen %d; planten weg %d; texturen %d/%d; onbekend %s %s", #mh:GetChildren(), #mo:GetChildren(), n, weg, ok, #preload, onb(oh), onb(oo))
