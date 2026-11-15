-- Vrouw Holle: rietgedekt huisje midden op het pad (boogdeurtjes met gezichtjes, luikenraam, voortuintje) + de put met houten pannendak op het ronde pleintje. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = zwaartepunt OSM 1109001371 = studs (2.73, -90.69); model = OSM -6.8 graden; -Y = zuid (bezoekersgevel/put), z 0 = maaiveld (Y 2).
local ID = 96855803143714
local TEX = {baksteen = {102619184086793}, riet = {79608095896850}, stuc_A = {128347504384339, 82490102701858}, stuc_L = {86299655122730, 138491204909988}, stuc_R = {77380597289131, 117294965402186}, stuc_V = {104246629049377, 71923007525048}}
local COLL = {{-1.795, -1.105, 1.5, 6.17, 8.85, 3.0, 0.0},{1.995, 1.1, 1.0, 1.41, 3.7, 2.0, 0.0},{-5.28, -7.115, 0.4, 3.195, 0.35, 0.8, -97.192},{-3.915, -8.85, 0.4, 3.144, 0.35, 0.8, -5.475},{0.47, -8.875, 0.4, 3.449, 0.35, 0.8, 4.157},{2.19, -6.94, 0.4, 3.62, 0.35, 0.8, 90.0},{3.0, -9.6, 0.5, 0.6, 0.5, 1.0, 20},{10.15, -20.4, 0.5, 2.0, 2.0, 1.0, 0.0},{8.7, -20.4, 1.5, 0.3, 0.3, 3.0, 0.0},{11.6, -20.4, 1.5, 0.3, 0.3, 3.0, 0.0},{11.65, -21.65, 0.5, 1.2, 0.6, 1.0, 0.0}}
local PLEIN = {{-10.7, -2.0}, {-10.5, 4.9}, {-6.0, 13.6}, {0.9, 10.3}, {4.1, 6.7}, {7.1, 0.9}, {7.2, -6.2}, {5.3, -13.9}, {-0.6, -12.3}, {-4.6, -10.0}, {-6.6, -8.8}, {-9.2, -5.7}}
local PLEIN2 = {{16.4, -19.1}, {16.2, -17.57}, {15.61, -16.15}, {14.67, -14.93}, {13.45, -13.99}, {12.03, -13.4}, {10.5, -13.2}, {8.97, -13.4}, {7.55, -13.99}, {6.33, -14.93}, {5.39, -16.15}, {4.8, -17.57}, {4.6, -19.1}, {4.8, -20.63}, {5.39, -22.05}, {6.33, -23.27}, {7.55, -24.21}, {8.97, -24.8}, {10.5, -25.0}, {12.03, -24.8}, {13.45, -24.21}, {14.67, -23.27}, {15.61, -22.05}, {16.2, -20.63}}
local PLEIN3 = {{3.0, -12.2}, {6.4, -12.6}, {7.3, -15.6}, {4.4, -16.6}}
local F = Vector3.new(0.1184, 0, 0.993)
local ORIGIN = CFrame.new(2.73, 2.0, -90.69) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(218, 216, 204), "Plastic"}, baksteen = {Color3.fromRGB(130, 70, 50), "Brick"}, natuursteen = {Color3.fromRGB(196, 178, 140), "Limestone"}, dakhout = {Color3.fromRGB(56, 48, 40), "WoodPlanks"}, goud = {Color3.fromRGB(230, 180, 50), "Metal"}, pek = {Color3.fromRGB(6, 6, 6), "Glass"}, modder = {Color3.fromRGB(46, 34, 24), "Mud"}, haan = {Color3.fromRGB(140, 64, 26), "SmoothPlastic"}, breuksteen = {Color3.fromRGB(120, 114, 104), "Slate"}, riet = {Color3.fromRGB(110, 88, 64), "Fabric"}, pannen = {Color3.fromRGB(168, 78, 46), "Slate"},
	groen = {Color3.fromRGB(32, 78, 78), "SmoothPlastic"}, venster = {Color3.fromRGB(150, 98, 46), "SmoothPlastic"}, glas = {Color3.fromRGB(60, 66, 58), "Glass"}, hout = {Color3.fromRGB(84, 62, 44), "Wood"},
	rood = {Color3.fromRGB(168, 36, 26), "SmoothPlastic"}, ijzer = {Color3.fromRGB(22, 24, 24), "Metal"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"},
	grind = {Color3.fromRGB(235, 228, 214), "Pebble"}, doek = {Color3.fromRGB(222, 214, 190), "Fabric"}, donker = {Color3.fromRGB(12, 10, 8), "SmoothPlastic"}, touw = {Color3.fromRGB(140, 115, 80), "Fabric"},
}
local objs = game:GetObjects("rbxassetid://" .. ID)
local oud = workspace:FindFirstChild("VrouwHolle"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "VrouwHolle"
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
			if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end; sa.Parent = p
		elseif key and M[key] then
			p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
			if key == "grind" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end); p.CanQuery = true; pcall(function() p.MaterialVariant = "VV_Grind" end) end
			if key == "venster" or key == "glas" or key == "doek" then p.CastShadow = false end
			if key == "glas" then p.Transparency = 0.35 end
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
for gx = -13, 18, 4 / S do
	for gy = -27, 15, 4 / S do
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
	if (f:IsA("Folder") or f:IsA("Model")) and string.find(f.Name, "Groen$") or f.Name == "VillaVoltaHorizon" then
		for _, c in ipairs(f:GetChildren()) do
			local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
			if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
				if inside(x, y, PLEIN) or inside(x, y, PLEIN2) or inside(x, y, PLEIN3) then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do local nm = string.lower(d.Name); if nm == "vrouw holle" or nm == "de put van vrouw holle" then d:Destroy(); labels += 1 end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", sp.CFrame) end; sp.CFrame = lokaal(3.6, -11.2, 0.2) end
return string.format("%d delen (tex %d); grondcellen %d; planten weg %d; labels %d; onbekend %s", #m:GetChildren(), ntex, n, weg, labels, #onb > 0 and table.concat(onb, ",") or "-")
