-- De Chinese Nachtegaal (1999-2026): ommuurd Ming-paleis met pagodetorentje, ingangsuitbouw, voortuin met maanpoort, lavarotsen en vijvertje, waterval, uitgangspoortje. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = zwaartepunt OSM 50911622 = studs (400.32, -526.62); model = OSM -8.2 graden; -Y = zuid, z 0 = maaiveld (Y 2).
local ID = 107212116677114
local TEX = {baksteen = {107064359452932}, rots = {127736975209159, 99888780557489}, stuc_A = {134835626789012, 87736035536806}, stuc_L = {123693994484750, 132286004384175}, stuc_R = {83816172553891, 81560210141172}, stuc_V = {125369380430741, 88440540856110}}
local COLL = {{3.5, -0.75, 3.7, 18.0, 16.0, 7.4, 0.0},{-6.53, 2.93, 1.5, 2.26, 2.6, 3.0, 0.0},{-6.53, -2.47, 1.5, 2.26, 2.6, 3.0, 0.0},{-11.79, 11.98, 1.3, 13.343, 0.45, 2.6, 178.798},{-21.485, 9.865, 1.3, 2.558, 0.45, 2.6, -143.265},{-21.855, 1.45, 1.1, 15.356, 0.4, 2.3, -85.106},{-13.35, -6.2, 1.1, 15.7, 0.4, 2.3, 0.0},{-5.1, 9.55, 1.3, 0.42, 4.6, 2.6, 0.0},{-20.3, -0.02, 0.2, 0.5, 1.6, 0.42, 0.0},{-13.0, -4.26, 0.2, 1.6, 0.5, 0.42, 0.0},{1.0, 8.5, 1.2, 7.2, 2.4, 2.4, 0.0},{19.404, 15.193, 1.2, 4.788, 0.4, 2.4, 175.381},{12.095, 15.46, 1.2, 8.25, 0.4, 2.4, 179.861},{7.995, 13.79, 1.2, 3.36, 0.4, 2.4, -89.147}}
local PLEIN = {{-22.51, 9.1}, {-20.46, 10.63}, {-18.46, 12.12}, {-5.12, 11.84}, {-5.1, 7.26}, {-5.1, 4.17}, {-7.66, 4.17}, {-7.66, -3.71}, {-5.5, -3.7}, {-5.5, -6.2}, {-21.2, -6.2}}
local PLEIN2 = {{-5.5, -8.78}, {9.3, -8.77}, {9.27, 1.67}, {12.53, 1.68}, {12.53, 7.29}, {-5.11, 7.26}, {-5.1, 4.17}, {-5.5, 4.17}}
local PLEIN3 = {{12.5, 3.2}, {17.4, 3.2}, {17.4, 15.6}, {15.0, 15.6}, {15.0, 5.5}, {12.5, 5.5}}
local F = Vector3.new(0.143, 0, 0.990)
local ORIGIN = CFrame.new(400.32, 2.0, -526.62) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(196, 182, 146), "Plastic"}, baksteen = {Color3.fromRGB(120, 112, 98), "Brick"}, fries = {Color3.fromRGB(64, 128, 122), "SmoothPlastic"}, roze = {Color3.fromRGB(216, 158, 152), "SmoothPlastic"}, blauwdak = {Color3.fromRGB(52, 108, 140), "Slate"}, groendak = {Color3.fromRGB(76, 108, 92), "Slate"}, rots = {Color3.fromRGB(34, 32, 32), "Basalt"}, zwartgrind = {Color3.fromRGB(26, 26, 26), "Pebble"}, hout = {Color3.fromRGB(92, 66, 42), "Wood"}, pot = {Color3.fromRGB(22, 32, 78), "Glass"}, steen = {Color3.fromRGB(154, 148, 138), "Concrete"}, lamp = {Color3.fromRGB(255, 220, 150), "Neon"}, pannen = {Color3.fromRGB(160, 70, 52), "Slate"}, water = {Color3.fromRGB(30, 52, 52), "Glass"}, bassin = {Color3.fromRGB(110, 178, 214), "SmoothPlastic"}, rand = {Color3.fromRGB(196, 192, 182), "Limestone"}, gras = {Color3.fromRGB(58, 110, 36), "Grass"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"}, ijzer = {Color3.fromRGB(22, 24, 24), "Metal"}, loods = {Color3.fromRGB(40, 66, 46), "CorrodedMetal"}, wit = {Color3.fromRGB(242, 240, 232), "SmoothPlastic"}, zwart = {Color3.fromRGB(10, 10, 10), "SmoothPlastic"}, huid = {Color3.fromRGB(216, 158, 102), "SmoothPlastic"}, blauw = {Color3.fromRGB(52, 90, 140), "SmoothPlastic"}, baksteen = {Color3.fromRGB(130, 70, 50), "Brick"}, natuursteen = {Color3.fromRGB(196, 178, 140), "Limestone"}, dakhout = {Color3.fromRGB(56, 48, 40), "WoodPlanks"}, goud = {Color3.fromRGB(226, 172, 60), "Foil"}, pek = {Color3.fromRGB(6, 6, 6), "Glass"}, modder = {Color3.fromRGB(46, 34, 24), "Mud"}, haan = {Color3.fromRGB(140, 64, 26), "SmoothPlastic"}, breuksteen = {Color3.fromRGB(120, 114, 104), "Slate"}, riet = {Color3.fromRGB(110, 88, 64), "Fabric"}, pannen = {Color3.fromRGB(168, 78, 46), "Slate"},
	groen = {Color3.fromRGB(30, 76, 56), "SmoothPlastic"}, venster = {Color3.fromRGB(150, 98, 46), "SmoothPlastic"}, glas = {Color3.fromRGB(60, 66, 58), "Glass"}, hout = {Color3.fromRGB(84, 62, 44), "Wood"},
	rood = {Color3.fromRGB(168, 36, 26), "SmoothPlastic"}, ijzer = {Color3.fromRGB(22, 24, 24), "Metal"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"},
	grind = {Color3.fromRGB(235, 228, 214), "Pebble"}, doek = {Color3.fromRGB(222, 214, 190), "Fabric"}, donker = {Color3.fromRGB(46, 46, 46), "SmoothPlastic"}, touw = {Color3.fromRGB(140, 115, 80), "Fabric"},
}
local objs = game:GetObjects("rbxassetid://" .. ID)
local oud = workspace:FindFirstChild("ChineseNachtegaal"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "ChineseNachtegaal"
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
			if tex == "rots" then sa.Color = Color3.fromRGB(70, 68, 68) end; sa.Parent = p
		elseif key and M[key] then
			p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
			if key == "grind" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end); p.CanQuery = true; pcall(function() p.MaterialVariant = "VV_Grind" end) end
			if key == "venster" or key == "glas" or key == "doek" then p.CastShadow = false end
			if key == "lamp" then p.CastShadow = false end
			if key == "water" then p.Transparency = 0.15; p.Reflectance = 0.15; p.CastShadow = false end
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
for gx = -23, 18, 4 / S do
	for gy = -12, 16, 4 / S do
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
				if inside(x, y, PLEIN) or inside(x, y, PLEIN2) or inside(x, y, PLEIN3) or inside(x, y, PLEIN3) or (x > -6 and x < 13.2 and y > -12 and y < 11.5) then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do local nm = string.lower(d.Name); if string.find(nm, "nachtegaal") then d:Destroy(); labels += 1 end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", sp.CFrame) end; sp.CFrame = lokaal(-24.0, 13.5, 0.2) end
return string.format("%d delen (tex %d); grondcellen %d; planten weg %d; labels %d; onbekend %s", #m:GetChildren(), ntex, n, weg, labels, #onb > 0 and table.concat(onb, ",") or "-")
