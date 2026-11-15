-- Draak Lichtgeraakt (1979): pilaarmuurtje met pannendakjes, draak bovenop de middenpijler, schatkist op breuksteen-eilandje, water in twee lobben, rood Pieck-hek, groen hekje. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = zwaartepunt OSM 55423757 = studs (363.72, -40.38), -Y = naar het plein (W), z 0 = maaiveld (Y 2).
local ID = 94874425561025
local TEX = {breuksteen = {117377235157913, 104739601077160}, pannen = {94307032340895}, stuc_A = {106117570432752, 119588516060539}, stuc_L = {121917386305361, 124801379667941}, stuc_R = {80634223575757, 137767525518384}, stuc_V = {89624476223298, 110913820934000}}
local COLL = {{0.05, 2.5, 1.5, 8.8, 0.9, 3.0, 0.0},{-0.15, -1.25, 0.5, 1.1, 0.7, 1.0, 8},{-1.1, -3.775, 0.5, 1.346, 0.15, 1.0, 58.671},{-0.1, -3.2, 0.5, 1.3, 0.15, 1.0, 0.0},{0.95, -3.775, 0.5, 1.401, 0.15, 1.0, -55.176},{5.217, 1.568, 0.5, 1.918, 0.15, 1.0, -24.451},{5.079, -0.822, 0.5, 4.471, 0.15, 1.0, -116.892},{2.614, -3.357, 0.5, 3.103, 0.15, 1.0, -159.584},{-2.438, -3.091, 0.5, 3.061, 0.15, 1.0, 147.97},{-4.648, -0.498, 0.5, 4.003, 0.15, 1.0, 117.124},{-4.876, 1.623, 0.5, 1.529, 0.15, 1.0, 26.383},{5.6, -3.4, 0.5, 0.7, 0.5, 1.0, 40}}
local PLEIN = {{-6.7, 2.4}, {-6.3, -2.4}, {-4.2, -4.6}, {-1.3, -5.2}, {1.2, -5.2}, {4.2, -4.7}, {6.6, -2.4}, {7.3, 1.5}, {6.4, 2.6}}
local WATER = {{-0.15, -2.45}, {2.94, -1.36}, {4.48, 2.21}, {6.37, 1.16}, {4.27, -3.01}, {1.26, -4.16}, {-0.16, -2.97}, {-1.29, -4.14}, {-3.95, -2.46}, {-5.84, 1.26}, {-4.34, 2.2}, {-2.93, -0.6}}
local F = Vector3.new(-0.965, 0, 0.264)
local ORIGIN = CFrame.new(363.72, 2.0, -40.38) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(232, 232, 224), "Plastic"}, natuursteen = {Color3.fromRGB(170, 170, 165), "Concrete"}, rots = {Color3.fromRGB(95, 98, 98), "Rock"},
	breuksteen = {Color3.fromRGB(160, 160, 165), "Slate"}, water = {Color3.fromRGB(30, 40, 26), "SmoothPlastic"}, modder = {Color3.fromRGB(34, 28, 20), "Mud"},
	ijzer = {Color3.fromRGB(22, 24, 24), "Metal"}, leuning = {Color3.fromRGB(52, 92, 96), "SmoothPlastic"}, huid = {Color3.fromRGB(236, 200, 168), "SmoothPlastic"},
	haar = {Color3.fromRGB(220, 182, 110), "SmoothPlastic"}, staart = {Color3.fromRGB(80, 140, 116), "SmoothPlastic"}, vin = {Color3.fromRGB(236, 214, 150), "SmoothPlastic"},
	vis = {Color3.fromRGB(236, 222, 140), "SmoothPlastic"}, visrug = {Color3.fromRGB(80, 140, 150), "SmoothPlastic"}, oog = {Color3.fromRGB(242, 216, 50), "Neon"},
	waterstraal = {Color3.fromRGB(200, 222, 232), "Glass"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"}, rood = {Color3.fromRGB(160, 28, 26), "SmoothPlastic"},
	grind = {Color3.fromRGB(235, 228, 214), "Pebble"}, pannen = {Color3.fromRGB(158, 72, 40), "Slate"}, rand = {Color3.fromRGB(128, 128, 126), "Slate"},
	draak = {Color3.fromRGB(46, 110, 62), "SmoothPlastic"}, buik = {Color3.fromRGB(150, 165, 90), "SmoothPlastic"}, stekel = {Color3.fromRGB(120, 52, 120), "SmoothPlastic"},
	bek = {Color3.fromRGB(180, 50, 50), "SmoothPlastic"}, tand = {Color3.fromRGB(242, 238, 218), "SmoothPlastic"}, zwart = {Color3.fromRGB(10, 10, 10), "SmoothPlastic"},
	vleugel = {Color3.fromRGB(40, 86, 54), "SmoothPlastic"}, kist = {Color3.fromRGB(110, 50, 30), "Wood"}, goud = {Color3.fromRGB(222, 170, 60), "Metal"},
	juweel = {Color3.fromRGB(60, 130, 230), "Glass"}, tak = {Color3.fromRGB(76, 62, 48), "Wood"}, klimop = {Color3.fromRGB(40, 70, 32), "LeafyGrass"},
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
				if key == "water" then p.Transparency = 0.08; p.Reflectance = 0.05; p.CastShadow = false; pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end) end
				if key == "klimop" then p.CastShadow = false end
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
local m, onb = plaats(ID, "DraakLichtgeraakt", TEX, COLL)
do local b = Instance.new("Part"); b.Name = "VijverBodem"; b.Anchored = true; b.Transparency = 1; b.CanTouch = false; b.Size = Vector3.new(12 * S, 0.6, 7 * S); b.CFrame = lokaal(0.3, -1.0, -0.45); b.Parent = m.Botsing end

local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local T = workspace.Terrain; local n = 0
for gx = -5.8, 6.4, 0.45 do for gy = -4.2, 2.2, 0.45 do                                -- vijvertje zacht uitgraven (FillBall per punt binnen de OSM-vorm)
	if inside(gx, gy, WATER) then T:FillBall(lokaal(gx, gy, -0.2).Position, 2.2, Enum.Material.Air) end
end end
for gx = -7.5, 7.5, 4 / S do
	for gy = -6, 4, 4 / S do
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
	if (f:IsA("Folder") or f:IsA("Model")) and string.find(f.Name, "Groen$") or f.Name == "VillaVoltaHorizon" then
		for _, c in ipairs(f:GetChildren()) do
			local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
			if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
				if inside(x, y, PLEIN) or inside(x, y, WATER) or inside(x, y, {{-4.6, 3.4}, {4.6, 3.4}, {4.6, 2.0}, {-4.6, 2.0}}) then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do local nm = string.lower(d.Name); if nm == "de draak" or string.find(nm, "lichtgeraakt") then d:Destroy(); labels += 1 end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", sp.CFrame) end; sp.CFrame = lokaal(0.0, -4.8, 0.2) * CFrame.Angles(0, math.pi, 0) end
local ok = 0
pcall(function() local dec = {}; for _, id in ipairs(preload) do local d = Instance.new("Decal"); d.Texture = id; table.insert(dec, d) end
	game:GetService("ContentProvider"):PreloadAsync(dec, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end) end)
return string.format("%d delen; grondcellen %d; planten weg %d; labels %d; texturen %d/%d; onbekend %s", #m:GetChildren(), n, weg, labels, ok, #preload, #onb > 0 and table.concat(onb, ",") or "-")
