-- De Vliegende Fakir: wit paleis (gaanderij met ezelsrugbogen, kantelenmuur, twee torens met uikoepels) + voortuin met water, fontein, tulpen, waterbak en plein. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = zwaartepunt OSM 50911617 = studs (240.66, -638.46); model = OSM -7.3 graden; -Y = zuid (plein), z 0 = maaiveld (Y 2).
local ID = 127156784409342
local TEX = {pannen = {101402303599146}, stuc_A = {135577368241410, 100937170250790}, stuc_L = {75083962363711, 84313423899052}, stuc_R = {89065881158661, 125689406350992}, stuc_V = {140129254805054, 74073807160029}}
local COLL = {{-0.305, 2.3, 1.8, 15.81, 4.6, 3.6, 0.0},{-0.305, 4.175, 3.2, 16.61, 0.85, 6.4, 0.0},{-10.36, -1.41, 2.0, 4.12, 3.82, 4.0, 0.0},{10.57, -1.025, 2.0, 3.84, 4.01, 4.0, 0.0},{-0.42, -6.46, 0.6, 0.8, 0.8, 1.2, 0.0},{-15.6, -9.8, 1.0, 0.2, 2.4, 2.0, 0.0},{15.6, -9.8, 1.0, 0.2, 2.4, 2.0, 0.0},{-12.0, -19.6, 0.5, 0.6, 0.5, 1.0, 0.0},{0.445, -16.265, 0.2, 22.93, 2.49, 0.4, 0.0}}
local PLEIN = {{-10.14, -33.85}, {-10.55, -30.95}, {-16.15, -26.9}, {-15.6, -18.4}, {16.5, -18.4}, {13.31, -27.18}, {13.71, -29.46}, {-9.19, -35.97}}
local PLEIN2 = {{-15.61, 1.6}, {-15.6, -18.4}, {16.5, -18.4}, {16.3, 1.6}}
local PLEIN3 = {{-12.5, 0.0}, {12.6, 0.0}, {12.6, 5.0}, {-12.5, 5.0}}
local F = Vector3.new(0.127, 0, 0.992)
local ORIGIN = CFrame.new(240.66, 2.0, -638.46) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(236, 236, 230), "Plastic"}, pannen = {Color3.fromRGB(160, 70, 52), "Slate"}, water = {Color3.fromRGB(110, 170, 200), "Glass"}, bassin = {Color3.fromRGB(110, 178, 214), "SmoothPlastic"}, rand = {Color3.fromRGB(196, 192, 182), "Limestone"}, gras = {Color3.fromRGB(58, 110, 36), "Grass"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"}, ijzer = {Color3.fromRGB(22, 24, 24), "Metal"}, loods = {Color3.fromRGB(40, 66, 46), "CorrodedMetal"}, wit = {Color3.fromRGB(242, 240, 232), "SmoothPlastic"}, zwart = {Color3.fromRGB(10, 10, 10), "SmoothPlastic"}, huid = {Color3.fromRGB(216, 158, 102), "SmoothPlastic"}, blauw = {Color3.fromRGB(52, 90, 140), "SmoothPlastic"}, baksteen = {Color3.fromRGB(130, 70, 50), "Brick"}, natuursteen = {Color3.fromRGB(196, 178, 140), "Limestone"}, dakhout = {Color3.fromRGB(56, 48, 40), "WoodPlanks"}, goud = {Color3.fromRGB(226, 172, 60), "Foil"}, pek = {Color3.fromRGB(6, 6, 6), "Glass"}, modder = {Color3.fromRGB(46, 34, 24), "Mud"}, haan = {Color3.fromRGB(140, 64, 26), "SmoothPlastic"}, breuksteen = {Color3.fromRGB(120, 114, 104), "Slate"}, riet = {Color3.fromRGB(110, 88, 64), "Fabric"}, pannen = {Color3.fromRGB(168, 78, 46), "Slate"},
	groen = {Color3.fromRGB(30, 76, 56), "SmoothPlastic"}, venster = {Color3.fromRGB(150, 98, 46), "SmoothPlastic"}, glas = {Color3.fromRGB(60, 66, 58), "Glass"}, hout = {Color3.fromRGB(84, 62, 44), "Wood"},
	rood = {Color3.fromRGB(168, 36, 26), "SmoothPlastic"}, ijzer = {Color3.fromRGB(22, 24, 24), "Metal"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"},
	grind = {Color3.fromRGB(235, 228, 214), "Pebble"}, doek = {Color3.fromRGB(222, 214, 190), "Fabric"}, donker = {Color3.fromRGB(46, 46, 46), "SmoothPlastic"}, touw = {Color3.fromRGB(140, 115, 80), "Fabric"},
}
local objs = game:GetObjects("rbxassetid://" .. ID)
local oud = workspace:FindFirstChild("VliegendeFakir"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "VliegendeFakir"
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
			if key == "water" then p.Transparency = 0.25; p.Reflectance = 0.15; p.CastShadow = false end
			if key == "gras" then p.CanQuery = true end
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
for gx = -17, 17, 4 / S do
	for gy = -37, 6, 4 / S do
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
local weg = 0
for _, f in ipairs(workspace:GetChildren()) do
	if (f:IsA("Folder") or f:IsA("Model")) and (string.find(f.Name, "Groen$") or string.find(f.Name, "Bos$")) or f.Name == "VillaVoltaHorizon" then
		for _, c in ipairs(f:GetChildren()) do
			local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
			if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
				if inside(x, y, PLEIN) or inside(x, y, PLEIN2) or inside(x, y, PLEIN3) or (x > -16.4 and x < 17 and y > -37 and y < 5.2) then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do local nm = string.lower(d.Name); if nm == "de tuinman en de fakir" or nm == "vliegende fakir" then d:Destroy(); labels += 1 end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", sp.CFrame) end; sp.CFrame = lokaal(1.0, -24.0, 0.2) end
return string.format("%d delen (tex %d); grondcellen %d; planten weg %d; labels %d; onbekend %s", #m:GetChildren(), ntex, n, weg, labels, #onb > 0 and table.concat(onb, ",") or "-")
