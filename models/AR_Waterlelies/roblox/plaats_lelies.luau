-- De Indische Waterlelies: wit oosters voorplein met vijver + gouden lotusfontein, tempelwachters, gaanderij onder rotsmassa, Simurgh-deur, rotstunnel, groene showloods. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = midden vijver = studs (109.98, -351.87); model = OSM -12.3 graden; +Y = noord (gaanderij), z 0 = maaiveld (Y 2).
local ID = 97150565042611
local TEX = {rots = {123678431564376, 83353192357556}, stuc_A = {123530596008801, 105177099737382}, stuc_L = {75082062525082, 136219849937179}, stuc_R = {81787058951264, 140192421049632}, stuc_V = {77333190804551, 125242336730983}}
local COLL = {{-0.025, -5.2, 0.25, 16.05, 0.5, 0.5, 0.0},{7.8, -0.04, 0.25, 10.72, 0.5, 0.5, 90.0},{-0.025, 5.12, 0.25, 16.05, 0.5, 0.5, 180.0},{-7.85, -0.04, 0.25, 10.72, 0.5, 0.5, -90.0},{-0.6, 0.23, 0.6, 0.6, 0.6, 1.2, 0.0},{-11.9, 5.4, 1.3, 0.45, 0.45, 2.6, 0.0},{-8.483, 5.4, 1.3, 0.45, 0.45, 2.6, 0.0},{-5.067, 5.4, 1.3, 0.45, 0.45, 2.6, 0.0},{-1.65, 5.4, 1.3, 0.45, 0.45, 2.6, 0.0},{1.767, 5.4, 1.3, 0.45, 0.45, 2.6, 0.0},{5.183, 5.4, 1.3, 0.45, 0.45, 2.6, 0.0},{8.6, 5.4, 1.3, 0.45, 0.45, 2.6, 0.0},{-1.65, 10.4, 2.5, 22.7, 1.2, 5.0, 0.0},{-14.7, 7.7, 1.8, 4.6, 6.2, 3.6, 0.0},{-13.0, 4.25, 1.0, 2.0, 2.0, 2.0, 0.0},{-8.55, 4.55, 1.0, 2.0, 2.0, 2.0, 0.0},{-16.5, 0.45, 1.2, 0.5, 9.1, 2.4, 0.0},{-16.5, -11.45, 1.2, 0.5, 9.1, 2.4, 0.0},{-16.5, -5.5, 1.5, 0.6, 2.8, 3.0, 0.0},{-0.5, -16.0, 1.2, 32.0, 0.5, 2.4, 0.0},{-12.0, -15.2, 0.25, 2.0, 0.6, 0.5, 0.0},{-6.0, -15.2, 0.25, 2.0, 0.6, 0.5, 0.0},{0.0, -15.2, 0.25, 2.0, 0.6, 0.5, 0.0},{6.0, -15.2, 0.25, 2.0, 0.6, 0.5, 0.0},{-14.3, -1.55, 0.3, 3.8, 10.1, 0.6, 0.0},{15.3, -17.15, 2.0, 11.4, 2.9, 4.0, 0.0},{17.0, -10.7, 2.0, 15.2, 3.8, 4.0, 0.0},{24.45, -15.8, 2.0, 2.3, 6.4, 4.0, 0.0},{18.0, 21.0, 3.5, 26.0, 18.0, 7.0, 0.0}}
local PLEIN = {{9.19, 5.12}, {9.57, -9.21}, {9.61, -10.92}, {15.66, -12.72}, {15.55, -15.8}, {-16.43, -15.97}, {-16.48, -8.1}, {-16.5, 5.1}, {-9.78, 5.1}, {-7.67, 5.11}, {7.83, 5.12}}
local PLEIN2 = {{9.0, -19.2}, {25.8, -19.2}, {25.8, -8.5}, {9.0, -8.5}}
local PLEIN3 = {{4.4, 10.0}, {4.4, 30.2}, {19.66, 31.24}, {31.66, 31.24}, {31.71, 19.15}, {8.32, 11.63}, {8.32, 10.0}}
local F = Vector3.new(0.213, 0, 0.977)
local ORIGIN = CFrame.new(109.98, 2.0, -351.87) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(236, 236, 230), "Plastic"}, rots = {Color3.fromRGB(100, 102, 102), "Rock"}, water = {Color3.fromRGB(80, 104, 92), "Glass"}, loods = {Color3.fromRGB(40, 66, 46), "CorrodedMetal"}, wit = {Color3.fromRGB(242, 240, 232), "SmoothPlastic"}, zwart = {Color3.fromRGB(10, 10, 10), "SmoothPlastic"}, huid = {Color3.fromRGB(216, 158, 102), "SmoothPlastic"}, blauw = {Color3.fromRGB(52, 90, 140), "SmoothPlastic"}, baksteen = {Color3.fromRGB(130, 70, 50), "Brick"}, natuursteen = {Color3.fromRGB(196, 178, 140), "Limestone"}, dakhout = {Color3.fromRGB(56, 48, 40), "WoodPlanks"}, goud = {Color3.fromRGB(226, 172, 60), "Foil"}, pek = {Color3.fromRGB(6, 6, 6), "Glass"}, modder = {Color3.fromRGB(46, 34, 24), "Mud"}, haan = {Color3.fromRGB(140, 64, 26), "SmoothPlastic"}, breuksteen = {Color3.fromRGB(120, 114, 104), "Slate"}, riet = {Color3.fromRGB(110, 88, 64), "Fabric"}, pannen = {Color3.fromRGB(168, 78, 46), "Slate"},
	groen = {Color3.fromRGB(30, 76, 56), "SmoothPlastic"}, venster = {Color3.fromRGB(150, 98, 46), "SmoothPlastic"}, glas = {Color3.fromRGB(60, 66, 58), "Glass"}, hout = {Color3.fromRGB(84, 62, 44), "Wood"},
	rood = {Color3.fromRGB(168, 36, 26), "SmoothPlastic"}, ijzer = {Color3.fromRGB(22, 24, 24), "Metal"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"},
	grind = {Color3.fromRGB(235, 228, 214), "Pebble"}, doek = {Color3.fromRGB(222, 214, 190), "Fabric"}, donker = {Color3.fromRGB(46, 46, 46), "SmoothPlastic"}, touw = {Color3.fromRGB(140, 115, 80), "Fabric"},
}
local objs = game:GetObjects("rbxassetid://" .. ID)
local oud = workspace:FindFirstChild("IndischeWaterlelies"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "IndischeWaterlelies"
for _, o in ipairs(objs) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = workspace; m:ScaleTo(S)
local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
m:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
local bots = Instance.new("Folder"); bots.Name = "Botsing"; bots.Parent = m
local onb, ntex = {}, 0
for _, p in ipairs(m:GetChildren()) do
	if not p:IsA("BasePart") then continue end
	p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = false
	if string.match(p.Name, "^COLL_") or string.match(p.Name, "^LAMP_") then p:Destroy()
	else
		local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$"); local key = string.match(p.Name, "__MAT_([%w_]-)_%d+$")
		if tex and TEX[tex] then
			p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic; ntex += 1
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
			if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
			if tex == "rots" then sa.Color = Color3.fromRGB(205, 208, 208) end; sa.Parent = p
		elseif key and M[key] then
			p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
			if key == "grind" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end); p.CanQuery = true; pcall(function() p.MaterialVariant = "VV_Grind" end) end
			if key == "venster" or key == "glas" or key == "doek" then p.CastShadow = false end
			if key == "water" then p.Transparency = 0.15; p.Reflectance = 0.15; p.CastShadow = false end
			if key == "goud" or key == "huid" or key == "rood" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end) end
		else table.insert(onb, p.Name) end
	end
end
for _, c in ipairs(COLL) do
	local b = Instance.new("Part"); b.Name = "Bots"; b.Anchored = true; b.Transparency = 1; b.CastShadow = false; b.CanTouch = false
	b.Size = Vector3.new(c[4] * S, math.max(c[6] * S, 0.05), c[5] * S); b.CFrame = lokaal(c[1], c[2], c[3]) * CFrame.Angles(0, math.rad(c[7]), 0); b.Parent = bots
end
m.WorldPivot = ORIGIN
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local T = workspace.Terrain; local n = 0
for gx = -18, 27, 4 / S do
	for gy = -20, 12, 4 / S do
		local w = (ORIGIN * CFrame.new(-gx * S, 0, gy * S)).Position
		local X, Z = math.floor(w.X / 4) * 4 + 2, math.floor(w.Z / 4) * 4 + 2
		local l = ORIGIN:PointToObjectSpace(Vector3.new(X, ORIGIN.Position.Y, Z)); local x, y = -l.X / S, l.Z / S
		if inside(x, y, PLEIN) or inside(x, y, PLEIN2) or inside(x, y, PLEIN3) then
			local r = Region3.new(Vector3.new(X - 2, -4, Z - 2), Vector3.new(X + 2, 4, Z + 2)):ExpandToGrid(4)
			for _, mat in ipairs({Enum.Material.Grass, Enum.Material.LeafyGrass, Enum.Material.Mud}) do T:ReplaceMaterial(r, 4, mat, Enum.Material.Ground) end
			n += 1
		end
	end
	task.wait()
end
local weg = 0
for _, f in ipairs(workspace:GetChildren()) do
	if (f:IsA("Folder") or f:IsA("Model")) and (string.find(f.Name, "Groen$") or string.find(f.Name, "Bos$")) or f.Name == "VillaVoltaHorizon" then
		for _, c in ipairs(f:GetChildren()) do
			local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
			if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
				if inside(x, y, PLEIN) or inside(x, y, PLEIN2) or inside(x, y, PLEIN3) or (x > -16.8 and x < 16 and y > -16.3 and y < 11) then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do local nm = string.lower(d.Name); if nm == "de indische waterlelies" or nm == "indische waterlelies" then d:Destroy(); labels += 1 end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", sp.CFrame) end; sp.CFrame = lokaal(0.0, -10.5, 0.2) end
return string.format("%d delen (tex %d); grondcellen %d; planten weg %d; labels %d; onbekend %s", #m:GetChildren(), ntex, n, weg, labels, #onb > 0 and table.concat(onb, ",") or "-")
