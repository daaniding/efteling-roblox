-- De Zes Dienaren: Kogeloog-gebouwtje (witte arcade, pannendak, krulgevel met buste, schilderijen van de dienaren, horecaluik) + plein tegenover Langnek. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = zwaartepunt OSM 50911609 = studs (485.37, 150.69); model = OSM-assen (x oost, y noord); z 0 = maaiveld (Y 2). Langnek zelf: models/CH_Langnek.
local ID = 111628397476125
local TEX = {baksteen = {131254949742173}, pannen = {72892713912978}, stuc_A = {131397330681191, 76202370628382}, stuc_L = {123165906024655, 74475274903880}, stuc_R = {99148545811735, 82344221848110}, stuc_V = {73491163315533, 137713553982599}}
local COLL = {{-9.1, -3.81, 1.2, 0.5, 0.5, 2.4, 23.538},{-6.797, -2.807, 1.2, 0.5, 0.5, 2.4, 23.538},{-4.493, -1.803, 1.2, 0.5, 0.5, 2.4, 23.538},{-2.19, -0.8, 1.2, 0.5, 0.5, 2.4, 23.538},{-4.185, -5.656, 1.5, 7.537, 0.4, 3.0, 23.538},{-2.19, -0.8, 1.2, 0.5, 0.5, 2.4, 36.453},{-0.2, 0.67, 1.2, 0.5, 0.5, 2.4, 36.453},{1.79, 2.14, 1.2, 0.5, 0.5, 2.4, 36.453},{2.144, -2.503, 1.5, 4.948, 0.4, 3.0, 36.453},{1.79, 2.14, 1.2, 0.5, 0.5, 2.4, 57.746},{3.05, 4.137, 1.2, 0.5, 0.5, 2.4, 57.746},{4.31, 6.133, 1.2, 0.5, 0.5, 2.4, 57.746},{5.57, 8.13, 1.2, 0.5, 0.5, 2.4, 57.746},{6.627, 3.275, 1.5, 7.083, 0.4, 3.0, 57.746}}
local PLEIN = {{5.57, 8.13}, {-0.38, 13.38}, {-5.51, 17.12}, {-9.35, 16.31}, {-9.88, 13.83}, {-11.33, 11.74}, {-13.48, 10.37}, {-15.99, 9.93}, {-18.48, 10.46}, {-19.82, 2.8}, {-19.45, -2.61}, {-19.13, -5.16}, {-16.79, -4.6}, {-15.24, -4.24}, {-15.01, -5.27}, {-12.38, -8.22}, {-8.16, -7.01}, {-9.1, -3.81}, {-2.19, -0.8}, {1.79, 2.14}}
local GEBOUW = {{-8.16, -7.01}, {-9.1, -3.81}, {-2.19, -0.8}, {1.79, 2.14}, {5.57, 8.13}, {8.3, 6.35}, {3.76, -1.13}, {0.03, -3.87}}
local F = Vector3.new(0, 0, 1)
local ORIGIN = CFrame.new(485.37, 2.0, 150.69) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	tegel = {Color3.fromRGB(150, 70, 50), "Brick"}, blauw = {Color3.fromRGB(40, 80, 160), "SmoothPlastic"}, huid = {Color3.fromRGB(230, 190, 160), "SmoothPlastic"}, zwart = {Color3.fromRGB(14, 14, 14), "SmoothPlastic"}, lamp = {Color3.fromRGB(255, 220, 150), "Neon"}, goud = {Color3.fromRGB(226, 172, 60), "Foil"}, schilderij = {Color3.fromRGB(196, 160, 96), "SmoothPlastic"}, rood = {Color3.fromRGB(170, 34, 26), "SmoothPlastic"}, wit = {Color3.fromRGB(244, 242, 232), "SmoothPlastic"}, plaat = {Color3.fromRGB(220, 200, 160), "SmoothPlastic"},
	hout = {Color3.fromRGB(84, 60, 40), "Wood"}, donker = {Color3.fromRGB(14, 12, 10), "SmoothPlastic"}, groen = {Color3.fromRGB(46, 92, 52), "SmoothPlastic"}, ijzer = {Color3.fromRGB(22, 24, 24), "Metal"},
	lood = {Color3.fromRGB(96, 98, 104), "Metal"}, water = {Color3.fromRGB(32, 46, 40), "Glass"}, modder = {Color3.fromRGB(36, 28, 20), "Mud"}, grind = {Color3.fromRGB(235, 228, 214), "Pebble"},
	glas = {Color3.fromRGB(120, 150, 110), "Glass"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"}, doek = {Color3.fromRGB(220, 206, 180), "Fabric"}, breuksteen = {Color3.fromRGB(128, 122, 112), "Slate"},
}
local objs = game:GetObjects("rbxassetid://" .. ID)
local oud = workspace:FindFirstChild("Kogeloog"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Kogeloog"
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
			if key == "water" then p.Transparency = 0.15; p.Reflectance = 0.1; p.CastShadow = false; pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end) end
			if key == "rood" or key == "steel" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end) end
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
local function _lijnd(x, y, p) local best = 1e9
	for i = 1, #p - 1 do local a, b = p[i], p[i + 1]; local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local T = workspace.Terrain; local n = 0
for gx = -21, 10, 4 / S do
	for gy = -10, 18, 4 / S do
		local w = (ORIGIN * CFrame.new(-gx * S, 0, gy * S)).Position
		local X, Z = math.floor(w.X / 4) * 4 + 2, math.floor(w.Z / 4) * 4 + 2
		local l = ORIGIN:PointToObjectSpace(Vector3.new(X, ORIGIN.Position.Y, Z)); local x, y = -l.X / S, l.Z / S
		if inside(x, y, PLEIN) or inside(x, y, GEBOUW) then
			local r = Region3.new(Vector3.new(X - 2, -4, Z - 2), Vector3.new(X + 2, 4, Z + 2)):ExpandToGrid(4)
			for _, mat in ipairs({Enum.Material.Grass, Enum.Material.LeafyGrass, Enum.Material.Mud}) do T:ReplaceMaterial(r, 4, mat, Enum.Material.Ground) end
			n += 1
		end
	end
	task.wait()
end
local weg = 0
for _, f in ipairs(workspace:GetChildren()) do
	if (f:IsA("Folder") or f:IsA("Model")) and (string.find(f.Name, "Groen$") or string.find(f.Name, "Bos$")) and f.Name ~= "LangnekGroen" or f.Name == "VillaVoltaHorizon" then
		for _, c in ipairs(f:GetChildren()) do
			local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
			if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
				local raak = inside(x, y, PLEIN) or inside(x, y, GEBOUW)
				if raak then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do local nm = string.lower(d.Name); if string.find(nm, "zes dienaren") or string.find(nm, "kogeloog") then d:Destroy(); labels += 1 end end end
return string.format("%d delen (tex %d); grondcellen %d; planten weg %d; labels %d; onbekend %s", #m:GetChildren(), ntex, n, weg, labels, #onb > 0 and table.concat(onb, ",") or "-")
