-- Kleine Boodschap (1952): kaboutertje op bakstenen sokkel achter een waterbak met bakstenen rand, U-haag, hekje, begoniarand, grindplein. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = OSM-node Kleine Boodschap = studs (-46.68, -92.28); model +X = noord, -Y = oost (kijkrichting, naar het pad); z 0 = maaiveld (Y 2).
local ID = 113409895976612
local COLL = {{0, -0.35, 0.18, 3.8, 2.4, 0.36, 0.0},{0, 0.53, 0.4, 1.6, 0.7, 0.8, 0.0},{0, 2.3, 1.0, 7.6, 1.2, 2.0, 0.0},{-3.8, -0.3, 1.0, 0.9, 2.8, 2.0, 0.0},{3.8, -0.3, 1.0, 0.9, 2.8, 2.0, 0.0},{-2.75, -1.725, 0.3, 1.481, 0.12, 0.6, -78.311},{-1.3, -2.6, 0.3, 2.617, 0.12, 0.6, -6.582},{1.3, -2.6, 0.3, 2.617, 0.12, 0.6, 6.582},{2.75, -1.725, 0.3, 1.481, 0.12, 0.6, 78.311}}
local PLEIN = {{-5.2, -7.9}, {4.8, -7.9}, {4.6, -3.0}, {3.0, -2.3}, {2.7, -2.4}, {0.0, -2.72}, {-2.7, -2.4}, {-3.0, -2.3}, {-5.4, -3.6}}
local F = Vector3.new(1, 0, 0)
local ORIGIN = CFrame.new(-46.68, 2.0, -92.28) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	baksteen = {Color3.fromRGB(150, 138, 124), "Brick"}, water = {Color3.fromRGB(90, 110, 104), "Glass"}, haag = {Color3.fromRGB(34, 66, 26), "LeafyGrass"}, hout = {Color3.fromRGB(84, 62, 44), "Wood"},
	huid = {Color3.fromRGB(238, 196, 160), "SmoothPlastic"}, blauw = {Color3.fromRGB(52, 92, 120), "SmoothPlastic"}, shirt = {Color3.fromRGB(196, 182, 128), "SmoothPlastic"},
	rood = {Color3.fromRGB(186, 40, 28), "SmoothPlastic"}, ruit = {Color3.fromRGB(226, 200, 196), "SmoothPlastic"}, haar = {Color3.fromRGB(232, 196, 110), "SmoothPlastic"},
	zwart = {Color3.fromRGB(10, 10, 10), "SmoothPlastic"}, grind = {Color3.fromRGB(235, 228, 214), "Pebble"}, modder = {Color3.fromRGB(46, 34, 24), "Mud"},
}
local objs = game:GetObjects("rbxassetid://" .. ID)
local oud = workspace:FindFirstChild("KleineBoodschap"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "KleineBoodschap"
for _, o in ipairs(objs) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = workspace; m:ScaleTo(S)
local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
m:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
local bots = Instance.new("Folder"); bots.Name = "Botsing"; bots.Parent = m
local onb = {}
for _, p in ipairs(m:GetChildren()) do
	if not p:IsA("BasePart") then continue end
	p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = false
	if string.match(p.Name, "^COLL_") or string.match(p.Name, "^LAMP_") then p:Destroy()
	else
		local key = string.match(p.Name, "__MAT_([%w_]-)_%d+$")
		if key and M[key] then
			p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
			if key == "grind" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end); p.CanQuery = true; pcall(function() p.MaterialVariant = "VV_Grind" end) end
			if key == "water" then p.Transparency = 0.25; p.Reflectance = 0.1; p.CastShadow = false end
			if key == "huid" or key == "blauw" or key == "shirt" or key == "rood" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end) end
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
for gx = -6, 6, 4 / S do for gy = -9, 3, 4 / S do
	local w = (ORIGIN * CFrame.new(-gx * S, 0, gy * S)).Position
	local X, Z = math.floor(w.X / 4) * 4 + 2, math.floor(w.Z / 4) * 4 + 2
	local l = ORIGIN:PointToObjectSpace(Vector3.new(X, ORIGIN.Position.Y, Z)); local x, y = -l.X / S, l.Z / S
	if inside(x, y, PLEIN) then
		local r = Region3.new(Vector3.new(X - 2, -4, Z - 2), Vector3.new(X + 2, 4, Z + 2)):ExpandToGrid(4)
		for _, mat in ipairs({Enum.Material.Grass, Enum.Material.LeafyGrass, Enum.Material.Mud}) do T:ReplaceMaterial(r, 4, mat, Enum.Material.Ground) end
		n += 1
	end
end end
local weg = 0
for _, f in ipairs(workspace:GetChildren()) do
	if (f:IsA("Folder") or f:IsA("Model")) and (string.find(f.Name, "Groen$") or string.find(f.Name, "Bos$")) and f.Name ~= "KleineBoodschapGroen" or f.Name == "VillaVoltaHorizon" then
		for _, c in ipairs(f:GetChildren()) do
			local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
			if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
				local nm = string.lower(c.Name); local boom = string.find(nm, "^beuk") or string.find(nm, "^eik") or string.find(nm, "^berk") or string.find(nm, "^den") or string.find(nm, "^kastanje")
				if inside(x, y, PLEIN) or (math.abs(x) < 4.4 and y > -3.0 and y < 3.0) or (boom and x > -7 and x < 7 and y > -9.5 and y < 4.5) then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do if string.lower(d.Name) == "kleine boodschap" then d:Destroy(); labels += 1 end end end
return string.format("%d delen; grondcellen %d; planten weg %d; labels %d; onbekend %s", #m:GetChildren(), n, weg, labels, #onb > 0 and table.concat(onb, ",") or "-")
