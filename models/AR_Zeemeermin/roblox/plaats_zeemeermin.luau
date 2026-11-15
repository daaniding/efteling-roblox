-- De Kleine Zeemeermin (1970): vijvertje met rotsstapel, meermin + spuwende vis, barok decor met Cupido, hekjes. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = OSM-node 7161344475 = studs (361.59, 67.68), model = OSM-assen, -Y = zuid (naar het pad), z 0 = maaiveld (Y 2).
local ID = 101300529925530
local TEX = {breuksteen = {117429902431031, 127790353719886}, natuursteen = {139104017222641, 91582413346514}, rots = {98845458811444, 107998784980920}, stuc_A = {73766662634199, 105515873493925}, stuc_L = {108746240218311, 116781967282476}, stuc_R = {109694693724017, 140643195612615}, stuc_V = {132701173095430, 76460171245120}}
local COLL = {{0.03, -0.07, 0.5, 2.0, 2.0, 1.0, 0.0}, {-1.18, 2.51, 0.9, 2.04, 0.3, 1.8, 0.0}, {1.79, 2.51, 0.9, 1.42, 0.3, 1.8, 0.0}, {0.46, 2.49, 1.5, 1.3, 0.35, 3.0, 0.0}, {-2.508, 0.668, 0.5, 3.362, 0.15, 1.0, -100.57}, {2.446, 0.248, 0.5, 4.146, 0.15, 1.0, -91.503}, {-1.678, -1.68, 0.5, 2.887, 0.15, 1.0, -26.46}, {1.066, -2.123, 0.5, 2.93, 0.15, 1.0, 7.869}, {-2.6, -2.3, 0.5, 0.7, 0.5, 1.0, 30}}
local PLEIN = {{-3.4, -1.2}, {-0.4, -2.75}, {2.7, -2.25}, {3.2, -3.4}, {-0.95, -4.5}, {-3.8, -3.0}}
local WATER = {{-0.32, 2.24}, {1.24, 2.21}, {2.14, -1.63}, {-0.32, -1.97}, {-2.51, -0.88}}
local F = Vector3.new(0, 0, 1)
local ORIGIN = CFrame.new(361.59, 2.0, 67.68) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(232, 232, 224), "Plastic"}, natuursteen = {Color3.fromRGB(170, 170, 165), "Concrete"}, rots = {Color3.fromRGB(95, 98, 98), "Rock"},
	breuksteen = {Color3.fromRGB(160, 160, 165), "Slate"}, water = {Color3.fromRGB(30, 40, 26), "SmoothPlastic"}, modder = {Color3.fromRGB(34, 28, 20), "Mud"},
	ijzer = {Color3.fromRGB(22, 24, 24), "Metal"}, leuning = {Color3.fromRGB(52, 92, 96), "SmoothPlastic"}, huid = {Color3.fromRGB(236, 200, 168), "SmoothPlastic"},
	haar = {Color3.fromRGB(220, 182, 110), "SmoothPlastic"}, staart = {Color3.fromRGB(80, 140, 116), "SmoothPlastic"}, vin = {Color3.fromRGB(236, 214, 150), "SmoothPlastic"},
	vis = {Color3.fromRGB(236, 222, 140), "SmoothPlastic"}, visrug = {Color3.fromRGB(80, 140, 150), "SmoothPlastic"}, oog = {Color3.fromRGB(14, 14, 14), "SmoothPlastic"},
	waterstraal = {Color3.fromRGB(200, 222, 232), "Glass"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"}, rood = {Color3.fromRGB(160, 28, 26), "SmoothPlastic"},
	grind = {Color3.fromRGB(235, 228, 214), "Pebble"},
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
local m, onb = plaats(ID, "KleineZeemeermin", TEX, COLL)
do local b = Instance.new("Part"); b.Name = "VijverBodem"; b.Anchored = true; b.Transparency = 1; b.CanTouch = false; b.Size = Vector3.new(4.2 * S, 0.6, 3.8 * S); b.CFrame = lokaal(0.0, 0.1, -0.5); b.Parent = m.Botsing end

local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local T = workspace.Terrain; local n = 0
for gx = -2.6, 2.3, 0.45 do for gy = -2.1, 2.3, 0.45 do                                -- vijvertje zacht uitgraven (FillBall per punt binnen de OSM-vorm)
	if inside(gx, gy, WATER) then T:FillBall(lokaal(gx, gy, -0.2).Position, 2.2, Enum.Material.Air) end
end end
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
				if inside(x, y, PLEIN) or inside(x, y, WATER) or inside(x, y, {{-0.6, 2.9}, {3.0, 2.9}, {3.0, 2.0}, {-2.6, 2.0}}) then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do local nm = string.lower(d.Name); if string.find(nm, "zeemeermin") then d:Destroy(); labels += 1 end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", sp.CFrame) end; sp.CFrame = lokaal(-0.4, -4.4, 0.2) * CFrame.Angles(0, math.pi, 0) end
local ok = 0
pcall(function() local dec = {}; for _, id in ipairs(preload) do local d = Instance.new("Decal"); d.Texture = id; table.insert(dec, d) end
	game:GetService("ContentProvider"):PreloadAsync(dec, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end) end)
return string.format("%d delen; grondcellen %d; planten weg %d; labels %d; texturen %d/%d; onbekend %s", #m:GetChildren(), n, weg, labels, ok, #preload, #onb > 0 and table.concat(onb, ",") or "-")
