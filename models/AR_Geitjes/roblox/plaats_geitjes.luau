-- De Wolf en de Zeven Geitjes (1957): rietgedekt huisje met krulgevels, bebaard gezicht, gaanderij, achtertuin met put, afdakje moeder geit. Gegenereerd; plakken in Studio.
-- Modelframe: oorsprong = zwaartepunt OSM 55423662 = studs (300.3, -127.23); model = OSM +7.27 graden; +Y = noord (hoofdpad), z 0 = maaiveld (Y 2).
local ID = 105264275416277
local TEX = {breuksteen = {76303995099562, 77820789908383}, pannen = {73271465989100}, riet = {133873106157266}, stuc_A = {124505227154784, 130203403115187}, stuc_L = {109891979087171, 121628352848818}, stuc_R = {120029442660817, 133183812126329}, stuc_V = {91958858585945, 71570955215000}}
local COLL = {{0.53, -2.155, 1.5, 8.46, 3.61, 3.0, 0.0},{1.235, 2.365, 1.5, 7.05, 2.23, 3.0, 0.0},{-4.55, 2.4, 0.5, 0.15, 1.9, 1.0, 0.0},{1.6, -8.2, 0.5, 1.6, 1.6, 1.0, 0.0},{3.7, -9.4, 1.2, 0.3, 0.3, 2.4, 0.0},{13.3, -1.1, 0.5, 2.4, 1.8, 1.0, -48},{10.5, 1.25, 0.5, 3.183, 0.15, 1.0, -46.273},{12.6, -1.3, 0.5, 3.441, 0.15, 1.0, -54.462},{14.6, -4.0, 0.5, 3.28, 0.15, 1.0, -52.431},{16.4, -6.35, 0.5, 2.64, 0.15, 1.0, -52.696}}
local PLEIN = {{-12.5, 3.0}, {-7.6, -0.75}, {-4.9, -0.75}, {-4.9, -0.4}, {5.4, -0.4}, {5.4, -0.8}, {7.2, -0.9}, {11.3, 0.9}, {12.2, 2.1}, {8.8, 5.4}, {2.0, 7.8}, {-4.6, 7.7}}
local F = Vector3.new(0.1265, 0, 0.992)
local ORIGIN = CFrame.new(300.3, 2.0, -127.23) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(214, 212, 196), "Plastic"}, breuksteen = {Color3.fromRGB(120, 114, 104), "Slate"}, riet = {Color3.fromRGB(110, 88, 64), "Fabric"}, pannen = {Color3.fromRGB(168, 78, 46), "Slate"},
	groen = {Color3.fromRGB(30, 66, 56), "SmoothPlastic"}, venster = {Color3.fromRGB(150, 98, 46), "SmoothPlastic"}, glas = {Color3.fromRGB(60, 66, 58), "Glass"}, hout = {Color3.fromRGB(84, 62, 44), "Wood"},
	rood = {Color3.fromRGB(168, 36, 26), "SmoothPlastic"}, ijzer = {Color3.fromRGB(22, 24, 24), "Metal"}, papier = {Color3.fromRGB(236, 222, 186), "SmoothPlastic"},
	grind = {Color3.fromRGB(235, 228, 214), "Pebble"}, doek = {Color3.fromRGB(222, 214, 190), "Fabric"}, donker = {Color3.fromRGB(12, 10, 8), "SmoothPlastic"}, touw = {Color3.fromRGB(140, 115, 80), "Fabric"},
}
local objs = game:GetObjects("rbxassetid://" .. ID)
local oud = workspace:FindFirstChild("ZevenGeitjes"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "ZevenGeitjes"
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
for gx = -13, 13, 4 / S do
	for gy = -12, 9, 4 / S do
		local w = (ORIGIN * CFrame.new(-gx * S, 0, gy * S)).Position
		local X, Z = math.floor(w.X / 4) * 4 + 2, math.floor(w.Z / 4) * 4 + 2
		local l = ORIGIN:PointToObjectSpace(Vector3.new(X, ORIGIN.Position.Y, Z)); local x, y = -l.X / S, l.Z / S
		local huis = x > -4 and x < 5 and y > -4.3 and y < 3.8
		local tuin = x > -4 and x < 7.5 and y > -11.5 and y < -4.3
		if inside(x, y, PLEIN) or huis or tuin then
			local r = Region3.new(Vector3.new(X - 2, -4, Z - 2), Vector3.new(X + 2, 4, Z + 2)):ExpandToGrid(4)
			for _, mat in ipairs({Enum.Material.Grass, Enum.Material.LeafyGrass}) do T:ReplaceMaterial(r, 4, mat, (inside(x, y, PLEIN) or huis) and Enum.Material.Ground or Enum.Material.Mud) end
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
				if inside(x, y, PLEIN) or (x > -5.5 and x < 6 and y > -11.5 and y < 4.2) or (x - 13.3) ^ 2 + (y + 1.1) ^ 2 < 6 then c:Destroy(); weg += 1 end end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout"); local labels = 0
if lay then for _, d in ipairs(lay:GetDescendants()) do if string.lower(d.Name) == "de wolf en de zeven geitjes" then d:Destroy(); labels += 1 end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then if not sp:GetAttribute("OudeCFrame") then sp:SetAttribute("OudeCFrame", sp.CFrame) end; sp.CFrame = lokaal(1.0, 5.6, 0.2) end
return string.format("%d delen (tex %d); grondcellen %d; planten weg %d; labels %d; onbekend %s", #m:GetChildren(), ntex, n, weg, labels, #onb > 0 and table.concat(onb, ",") or "-")
