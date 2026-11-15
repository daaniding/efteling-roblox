-- Het Kabouterdorp: paddenstoelenparcours, kabouterboom, loze vissertje + morieljehuis, grote vliegenzwam, huisje met waterrad, Grote Kabouterhuis, paden, vijvers. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = zwaartepunt OSM 55423167 = studs (458.25, -63.78); model = OSM-assen (x oost, y noord); z 0 = maaiveld (Y 2).
local ID = 91847710808274
local TEX = {pannen = {90654345963797}, riet = {74149770223555}, schors = {118241977111659}, zwam = {130549076518715}, stuc_A = {133537347280308, 129439300675414}, stuc_L = {113986458173427, 97372319425606}, stuc_R = {132533217956334, 97759382151312}, stuc_V = {138787119131602, 126222652488854}}
local COLL = {{-17.55, 21.5, 1.15, 2.52, 2.52, 2.3, 0.0},{-22.4, 22.6, 0.95, 1.8, 1.8, 1.9, 0.0},{-14.45, 19.3, 0.8, 0.3, 1.4, 1.6, 0.0},{-13.15, 19.3, 0.8, 0.3, 1.4, 1.6, 0.0},{-6.64, 16.95, 2.0, 2.4, 2.4, 4.0, 0.0},{9.3, 4.9, 0.8, 1.2, 1.2, 1.6, 0.0},{13.562, 8.083, 1.0, 4.0, 4.0, 2.0, 0.0},{9.27, 24.84, 2.2, 5.6, 5.6, 4.4, 0.0},{15.6, 18.2, 1.0, 3.2, 2.4, 2.0, -8},{-8.3, -6.9, 1.3, 1.2, 4.0, 2.6, 0.0},{-4.6, -9.8, 1.3, 3.5, 0.6, 2.6, 0.0},{-2.6, -6.2, 1.3, 1.0, 3.2, 2.6, 30}}
local VIJVERS = {
	{{-6.9, 28.13}, {-5.98, 23.11}, {-10.56, 23.26}, {-18.06, 24.59}, {-14.73, 26.98}},
	{{13.45, 12.25}, {13.2, 14.38}, {10.34, 13.06}, {7.94, 10.57}, {7.33, 8.89}, {8.56, 4.93}, {11.57, 3.42}, {15.25, 3.87}, {17.75, 6.21}, {18.56, 8.49}, {16.59, 9.26}},
	{{-8.83, -4.93}, {-10.27, -3.46}, {-6.83, -1.44}, {-4.15, -1.56}, {-1.46, -3.36}, {0.66, -5.98}, {1.19, -8.92}, {1.14, -12.16}, {-2.15, -13.36}, {-5.29, -13.0}, {-5.33, -10.18}, {-1.67, -9.36}, {-4.04, -4.62}, {-7.18, -3.01}}}
local HOOFDPAD = {{-8.11, 36.56}, {-5.82, 31.33}, {-4.82, 29.28}, {-3.59, 19.72}, {-3.25, 14.84}, {-2.22, 6.19}, {-2.4, 3.97}, {4.66, -5.64}, {5.73, -9.14}, {8.73, -29.62}}
local HUIZEN = {{-17.55, 21.5, 2.7}, {-22.4, 22.6, 2.1}, {-13.8, 19.3, 1.6}, {-11.0, 18.0, 1.5}, {-6.64, 16.95, 3.0}, {10.4, 5.4, 2.4}, {13.4, 9.0, 3.4}, {9.27, 24.84, 5.0}, {15.6, 18.2, 2.6}, {13.2, 21.0, 1.7}, {-5.0, -6.9, 4.4}}
local F = Vector3.new(0, 0, 1)
local ORIGIN = CFrame.new(458.25, 2.0, -63.78) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	steel = {Color3.fromRGB(232, 224, 204), "Plastic"}, rood = {Color3.fromRGB(190, 32, 22), "SmoothPlastic"}, wit = {Color3.fromRGB(244, 242, 232), "SmoothPlastic"}, plaat = {Color3.fromRGB(220, 200, 160), "SmoothPlastic"},
	hout = {Color3.fromRGB(84, 60, 40), "Wood"}, donker = {Color3.fromRGB(14, 12, 10), "SmoothPlastic"}, groen = {Color3.fromRGB(46, 92, 52), "SmoothPlastic"}, ijzer = {Color3.fromRGB(22, 24, 24), "Metal"},
	lood = {Color3.fromRGB(96, 98, 104), "Metal"}, water = {Color3.fromRGB(32, 46, 40), "Glass"}, modder = {Color3.fromRGB(36, 28, 20), "Mud"}, grind = {Color3.fromRGB(235, 228, 214), "Pebble"},
	glas = {Color3.fromRGB(120, 150, 110), "Glass"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"}, doek = {Color3.fromRGB(220, 206, 180), "Fabric"}, breuksteen = {Color3.fromRGB(128, 122, 112), "Slate"},
}
local objs = game:GetObjects("rbxassetid://" .. ID)
local oud = workspace:FindFirstChild("Kabouterdorp"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Kabouterdorp"
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
local function lijnd(x, y, p) local best = 1e9
	for i = 1, #p - 1 do local a, b = p[i], p[i + 1]; local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local T = workspace.Terrain; local gat = 0
for _, v in ipairs(VIJVERS) do                                                                -- vijvers zacht uitgraven (onzichtbare bodem eronder)
	local x0, x1, y0, y1 = 1e9, -1e9, 1e9, -1e9
	for _, p in ipairs(v) do x0 = math.min(x0, p[1]); x1 = math.max(x1, p[1]); y0 = math.min(y0, p[2]); y1 = math.max(y1, p[2]) end
	for gx = x0, x1, 0.45 do for gy = y0, y1, 0.45 do if inside(gx, gy, v) then T:FillBall(lokaal(gx, gy, -0.25).Position, 2.0, Enum.Material.Air); gat += 1 end end end
	local b = Instance.new("Part"); b.Name = "VijverBodem"; b.Anchored = true; b.Transparency = 1; b.CanTouch = false; b.Size = Vector3.new((x1 - x0) * S, 0.6, (y1 - y0) * S)
	b.CFrame = lokaal((x0 + x1) / 2, (y0 + y1) / 2, -0.45); b.Parent = bots
end
local n = 0
for gx = -26, 22, 4 / S do
	for gy = -30, 37, 4 / S do
		local w = (ORIGIN * CFrame.new(-gx * S, 0, gy * S)).Position
		local X, Z = math.floor(w.X / 4) * 4 + 2, math.floor(w.Z / 4) * 4 + 2
		local l = ORIGIN:PointToObjectSpace(Vector3.new(X, ORIGIN.Position.Y, Z)); local x, y = -l.X / S, l.Z / S
		if lijnd(x, y, HOOFDPAD) < 2.2 then
			local r = Region3.new(Vector3.new(X - 2, -4, Z - 2), Vector3.new(X + 2, 4, Z + 2)):ExpandToGrid(4)
			for _, mat in ipairs({Enum.Material.Grass, Enum.Material.LeafyGrass}) do T:ReplaceMaterial(r, 4, mat, Enum.Material.Ground) end
			n += 1
		end
	end
	task.wait()
end
local weg = 0
for _, f in ipairs(workspace:GetChildren()) do
	if (f:IsA("Folder") or f:IsA("Model")) and (string.find(f.Name, "Groen$") or string.find(f.Name, "Bos$")) and f.Name ~= "KabouterdorpGroen" or f.Name == "VillaVoltaHorizon" then
		for _, c in ipairs(f:GetChildren()) do
			local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
			if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
				local raak = lijnd(x, y, HOOFDPAD) < 2.0
				for _, v in ipairs(VIJVERS) do if inside(x, y, v) then raak = true end end
				for _, h in ipairs(HUIZEN) do if (x - h[1]) ^ 2 + (y - h[2]) ^ 2 < h[3] ^ 2 then raak = true end end
				if raak then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do local nm = string.lower(d.Name); if string.find(nm, "kabouterdorp") then d:Destroy(); labels += 1 end end end
return string.format("%d delen (tex %d); vijvergat %d; grondcellen %d; planten weg %d; labels %d; onbekend %s", #m:GetChildren(), ntex, gat, n, weg, labels, #onb > 0 and table.concat(onb, ",") or "-")
