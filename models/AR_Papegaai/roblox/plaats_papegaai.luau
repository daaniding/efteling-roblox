-- De Sprekende Papegaai (Het Stoute Prinsesje, 1952): muurtje met nis, pannendakje, ara op een tak, plantvak met leuning. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = midden OSM 55423808 = studs (177.51, 28.92), -Y = naar het pad (ZW), z 0 = maaiveld (Y 2).
local ID = 136319841903954
local TEX = {baksteen = {77017915924985, 98037918917658}, hout = {94049813111973, 138595962280281}, pannen = {122723268795674, 124567169586192}, schors = {77748798275240, 125051992651991}, stuc_A = {90763398124353, 111399283095934}, stuc_L = {94664145618709, 117655440231084}, stuc_R = {87793944403953, 122178254460947}, stuc_V = {137727481037901, 98969738828603}}
local COLL = {{0, 2.57, 1.7, 3.2, 0.75, 3.4, 0.0}, {-2.32, 0.789, 0.55, 2.821, 0.15, 1.1, -105.208}, {-2.653, -0.711, 0.55, 0.288, 0.15, 1.1, -75.0}, {-2.564, -0.984, 0.55, 0.288, 0.15, 1.1, -69.0}, {-2.447, -1.247, 0.55, 0.288, 0.15, 1.1, -63.0}, {-2.303, -1.496, 0.55, 0.288, 0.15, 1.1, -57.0}, {-2.134, -1.728, 0.55, 0.288, 0.15, 1.1, -51.0}, {-1.942, -1.942, 0.55, 0.288, 0.15, 1.1, -45.0}, {-1.728, -2.134, 0.55, 0.288, 0.15, 1.1, -39.0}, {-1.496, -2.303, 0.55, 0.288, 0.15, 1.1, -33.0}, {-1.247, -2.447, 0.55, 0.288, 0.15, 1.1, -27.0}, {-0.984, -2.564, 0.55, 0.288, 0.15, 1.1, -21.0}, {-0.711, -2.653, 0.55, 0.288, 0.15, 1.1, -15.0}, {-0.43, -2.712, 0.55, 0.288, 0.15, 1.1, -9.0}, {-0.144, -2.742, 0.55, 0.288, 0.15, 1.1, -3.0}, {0.144, -2.742, 0.55, 0.288, 0.15, 1.1, 3.0}, {0.43, -2.712, 0.55, 0.288, 0.15, 1.1, 9.0}, {0.711, -2.653, 0.55, 0.288, 0.15, 1.1, 15.0}, {0.984, -2.564, 0.55, 0.288, 0.15, 1.1, 21.0}, {1.247, -2.447, 0.55, 0.288, 0.15, 1.1, 27.0}, {1.496, -2.303, 0.55, 0.288, 0.15, 1.1, 33.0}, {1.728, -2.134, 0.55, 0.288, 0.15, 1.1, 39.0}, {1.942, -1.942, 0.55, 0.288, 0.15, 1.1, 45.0}, {2.134, -1.728, 0.55, 0.288, 0.15, 1.1, 51.0}, {2.303, -1.496, 0.55, 0.288, 0.15, 1.1, 57.0}, {2.447, -1.247, 0.55, 0.288, 0.15, 1.1, 63.0}, {2.564, -0.984, 0.55, 0.288, 0.15, 1.1, 69.0}, {2.653, -0.711, 0.55, 0.288, 0.15, 1.1, 75.0}, {2.32, 0.789, 0.55, 2.821, 0.15, 1.1, 105.208}}
local PLEIN = {{-4.4, 1.6}, {-3.0, 2.2}, {3.0, 2.2}, {4.4, 1.6}, {4.6, -2.6}, {2.2, -4.7}, {-0.6, -5.0}, {-3.2, -3.8}, {-4.8, -1.4}}
local F = Vector3.new(-0.6, 0, 0.8)
local ORIGIN = CFrame.new(177.51, 2.0, 28.92) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	baksteen = {Color3.fromRGB(150, 86, 64), "Brick"}, stuc = {Color3.fromRGB(224, 220, 206), "Plastic"}, pannen = {Color3.fromRGB(150, 82, 56), "ClayRoofTiles"},
	hout = {Color3.fromRGB(70, 48, 32), "Wood"}, schors = {Color3.fromRGB(120, 112, 96), "Wood"}, rood = {Color3.fromRGB(214, 56, 30), "SmoothPlastic"},
	geel = {Color3.fromRGB(232, 184, 50), "SmoothPlastic"}, blauw = {Color3.fromRGB(34, 108, 160), "SmoothPlastic"}, groen = {Color3.fromRGB(44, 92, 52), "LeafyGrass"},
	wit = {Color3.fromRGB(236, 232, 222), "SmoothPlastic"}, zwart = {Color3.fromRGB(16, 16, 16), "SmoothPlastic"}, snavel = {Color3.fromRGB(222, 212, 190), "SmoothPlastic"},
	oogrood = {Color3.fromRGB(255, 30, 20), "Neon"}, bord = {Color3.fromRGB(236, 226, 196), "SmoothPlastic"}, ijzer = {Color3.fromRGB(20, 22, 22), "Metal"},
	leuning = {Color3.fromRGB(42, 78, 70), "SmoothPlastic"}, grind = {Color3.fromRGB(235, 228, 214), "Pebble"}, aarde = {Color3.fromRGB(58, 42, 30), "Ground"},
	rots = {Color3.fromRGB(120, 120, 114), "Rock"},
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
local m, onb = plaats(ID, "SprekendePapegaai", TEX, COLL)
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local T = workspace.Terrain; local n = 0
for gx = -6, 6, 4 / S do
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
				if inside(x, y, PLEIN) then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do local nm = string.lower(d.Name); if string.find(nm, "papegaai") or string.find(nm, "stoute prinses") then d:Destroy(); labels += 1 end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", sp.CFrame) end; sp.CFrame = lokaal(0, -4.3, 0.2) * CFrame.Angles(0, math.pi, 0) end
local ok = 0
pcall(function() local dec = {}; for _, id in ipairs(preload) do local d = Instance.new("Decal"); d.Texture = id; table.insert(dec, d) end
	game:GetService("ContentProvider"):PreloadAsync(dec, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end) end)
return string.format("%d delen; grondcellen %d; planten weg %d; labels %d; texturen %d/%d; onbekend %s", #m:GetChildren(), n, weg, labels, ok, #preload, #onb > 0 and table.concat(onb, ",") or "-")
