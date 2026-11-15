-- De toren van Raponsje (2001): stucschacht, vakwerk, spanendak, windvaan, vlecht, sokkel + ruinemuur, vijvertje met leuning. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = midden OSM 55423664 = studs (252.09, 25.68), model = OSM-assen, -Y = zuid (raam naar het pad), z 0 = maaiveld (Y 2).
local ID = 133725694471918
local TEX = {baksteen = {116946198038945, 96253942642622}, hout = {100387462456356, 85958568004477}, lei = {78009180373703, 129519389554076}, rots = {75175000855758, 76180916570642}, stuc_A = {114383021587706, 129721109767444}, stuc_L = {129452929019851, 118012363179156}, stuc_R = {131568779107939, 138881643464665}, stuc_V = {118776866598692, 88360062391440}, vakvlak = {84610677000760}}
local COLL = {{0, 0, 3.4, 2.34, 2.34, 6.0, 0.0}, {-0.07, -1.78, 0.9, 2.75, 0.4, 1.8, 0.0}, {-2.704, 1.352, 0.45, 1.583, 0.15, 0.9, -131.643}, {-3.355, -0.082, 0.45, 1.702, 0.15, 0.9, -98.426}, {-2.957, -1.853, 0.45, 2.133, 0.15, 0.9, -60.631}, {-1.247, -3.157, 0.45, 2.49, 0.15, 0.9, -17.495}, {0.772, -3.282, 0.45, 1.736, 0.15, 0.9, 16.667}, {2.047, -2.431, 0.45, 1.495, 0.15, 0.9, 53.588}, {-3.4, -3.9, 0.5, 0.7, 0.5, 1.0, -25}}
local PLEIN = {{-4.4, -2.6}, {-3.5, -3.3}, {-0.2, -3.75}, {1.6, -3.3}, {2.8, -2.3}, {3.6, -3.4}, {2.6, -4.9}, {-0.4, -5.1}, {-4.6, -4.6}}
local WATER = {{-1.43, 1.16}, {-1.96, 1.55}, {-2.85, 0.52}, {-3.03, -0.92}, {-2.12, -2.46}, {-0.15, -3.09}, {1.28, -2.72}, {2.06, -1.7}, {1.53, -1.2}, {1.03, -1.63}, {0.41, -1.86}, {-0.24, -1.87}, {-0.87, -1.66}, {-1.38, -1.24}, {-1.71, -0.71}, {-1.84, -0.07}, {-1.74, 0.58}}
local F = Vector3.new(0, 0, 1)
local ORIGIN = CFrame.new(252.09, 2.0, 25.68) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(228, 226, 220), "Plastic"}, baksteen = {Color3.fromRGB(150, 86, 64), "Brick"}, hout = {Color3.fromRGB(70, 48, 32), "Wood"},
	vakvlak = {Color3.fromRGB(226, 222, 210), "Plastic"}, lei = {Color3.fromRGB(120, 96, 70), "WoodPlanks"}, rots = {Color3.fromRGB(150, 148, 140), "Rock"},
	ijzer = {Color3.fromRGB(26, 26, 26), "Metal"}, glas = {Color3.fromRGB(150, 168, 100), "Glass"}, venster = {Color3.fromRGB(14, 14, 14), "SmoothPlastic"},
	vlecht = {Color3.fromRGB(236, 210, 140), "Fabric"}, klimop = {Color3.fromRGB(40, 70, 32), "LeafyGrass"}, rank = {Color3.fromRGB(70, 56, 42), "Wood"},
	water = {Color3.fromRGB(30, 40, 26), "SmoothPlastic"}, modder = {Color3.fromRGB(34, 28, 20), "Mud"}, leuning = {Color3.fromRGB(52, 92, 96), "SmoothPlastic"},
	papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"}, rood = {Color3.fromRGB(160, 28, 26), "SmoothPlastic"}, grind = {Color3.fromRGB(235, 228, 214), "Pebble"},
}
local TINT = {stuc_V = Color3.fromRGB(232, 222, 200), stuc_L = Color3.fromRGB(232, 222, 200), stuc_R = Color3.fromRGB(232, 222, 200), stuc_A = Color3.fromRGB(232, 222, 200), vakvlak = Color3.fromRGB(226, 214, 190)}
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
local m, onb = plaats(ID, "Raponsje", TEX, COLL)
do local b = Instance.new("Part"); b.Name = "VijverBodem"; b.Anchored = true; b.Transparency = 1; b.CanTouch = false; b.Size = Vector3.new(4.6 * S, 0.6, 4.2 * S); b.CFrame = lokaal(-0.6, -1.2, -0.45); b.Parent = m.Botsing end

local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local T = workspace.Terrain; local n = 0
for gx = -3.2, 2.3, 0.45 do for gy = -3.2, 1.7, 0.45 do                                -- vijvertje zacht uitgraven (FillBall per punt binnen de OSM-vorm)
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
				if inside(x, y, PLEIN) or inside(x, y, WATER) or x * x + y * y < 2.0 * 2.0 then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do local nm = string.lower(d.Name); if string.find(nm, "raponsje") then d:Destroy(); labels += 1 end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", sp.CFrame) end; sp.CFrame = lokaal(0.4, -5.5, 0.2) * CFrame.Angles(0, math.pi, 0) end
local ok = 0
pcall(function() local dec = {}; for _, id in ipairs(preload) do local d = Instance.new("Decal"); d.Texture = id; table.insert(dec, d) end
	game:GetService("ContentProvider"):PreloadAsync(dec, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end) end)
return string.format("%d delen; grondcellen %d; planten weg %d; labels %d; texturen %d/%d; onbekend %s", #m:GetChildren(), n, weg, labels, ok, #preload, #onb > 0 and table.concat(onb, ",") or "-")
