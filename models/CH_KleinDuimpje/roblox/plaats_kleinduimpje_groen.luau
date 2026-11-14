-- Klein Duimpje groen (Commons 4019765619 / 2011 / sleeping_ogre): eiland vol varens rond en tussen de laarzen, rododendrons en
-- coniferen achter de gracht, bosgrond (geen gras) op het eiland en het rotsbed. Draai na plaats_kleinduimpje.luau.
local F = Vector3.new(0.43, 0, 0.90).Unit
local ORIGIN = CFrame.new(435.33, 2.0, -378.66) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local EILAND = {{-2.96, 1.56}, {0.40, 3.42}, {3.37, 2.00}, {4.16, -2.14}, {-3.31, -3.47}}
local WATER = {{-3.31, -3.47}, {-6.26, -2.46}, {-4.72, 3.22}, {0.21, 5.82}, {5.61, 3.90}, {7.59, -1.95}, {4.16, -2.14}, {3.37, 2.00}, {0.40, 3.42}, {-2.96, 1.56}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function voorbed(x, y) return y < -2.0 and y > -5.6 and x > -6.5 and x < 6.5 and not inside(x, y, WATER) end
-- 1) bosgrond op eiland en rotsbed
local T = workspace.Terrain
for x = -7, 8, 1 do for y = -6, 4, 1 do
	if inside(x, y, EILAND) or voorbed(x, y) then
		local p = lokaal(x, y, 0).Position
		for _, mt in ipairs({Enum.Material.Grass, Enum.Material.LeafyGrass}) do
			T:ReplaceMaterial(Region3.new(p - Vector3.new(4, 8, 4), p + Vector3.new(4, 2, 4)):ExpandToGrid(4), 4, mt, Enum.Material.Ground) end
	end end end
-- 2) planten
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), game.ServerStorage:FindFirstChild("VVPlanten"), workspace:FindFirstChild("HerautenpleinGroen"), workspace:FindFirstChild("HansEnGrietjeGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("KleinDuimpjeGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "KleinDuimpjeGroen"
local reus = workspace:FindFirstChild("KleinDuimpjeReus"); local omg = workspace:FindFirstChild("KleinDuimpjeOmgeving")
local grond = {T}; if omg then table.insert(grond, omg) end
local rpG = RaycastParams.new(); rpG.FilterType = Enum.RaycastFilterType.Include; rpG.FilterDescendantsInstances = grond
local rpR = RaycastParams.new(); rpR.FilterType = Enum.RaycastFilterType.Include; rpR.FilterDescendantsInstances = reus and {reus} or {}
local R = Random.new(1998)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L = {}
for _ = 1, 2600 do                                                         -- varens: dicht op het eiland en in het voorbed
	local x, y = U(-6.5, 6), U(-5.6, 3.6)
	local op = inside(x, y, EILAND); local vb = voorbed(x, y)
	if (op and R:NextNumber() < 0.5) or (vb and y > -3.2 and R:NextNumber() < 0.16) then   -- voorbed vrij: zicht op de reus vanaf het plein
		local s = {"PH_fern_02_0", "PH_fern_02_2", "PH_fern_02_3", "varen1"}
		table.insert(L, {s[R:NextInteger(1, #s)], x, y, y < -1.5 and U(1.6, 2.4) or U(2.2, 3.2), true}) end
end
for _ = 1, 1400 do                                                         -- achter de gracht: rododendrons, taxus, coniferen
	local x, y = U(-10, 11), U(2.5, 11)
	if not inside(x, y, WATER) and not inside(x, y, EILAND) and y > 3.5 and R:NextNumber() < 0.08 then
		local s = y > 6.5 and {"den0", "den1", "taxus0", "rododendron0", "rododendron1"} or {"rododendron0", "rododendron1", "struik0", "taxus0", "PH_shrub_03_1"}
		table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.9, 1.3), false}) end
end
local n, mis, weg = 0, {}, 0
for i, p in ipairs(L) do
	local pos = lokaal(p[2], p[3], 0).Position
	local hit = workspace:Raycast(pos + Vector3.new(0, 40, 0), Vector3.new(0, -80, 0), rpG)
	if not hit or hit.Material == Enum.Material.Water then continue end
	if reus then                                                            -- niet op of vlak onder de reus
		local hr = workspace:Raycast(pos + Vector3.new(0, 40, 0), Vector3.new(0, -80, 0), rpR)
		if hr and hr.Position.Y - hit.Position.Y < 4.5 then weg += 1; continue end
	end
	local t = bron(p[1]); if not t then mis[p[1]] = true; continue end
	local c = t:Clone(); local rot = CFrame.Angles(0, R:NextNumber() * math.pi * 2, 0)
	if c:IsA("Model") then
		if p[4] ~= 1 then c:ScaleTo(c:GetScale() * p[4]) end
		local cf, sz = c:GetBoundingBox(); local onder = cf.Position.Y - sz.Y / 2
		c:PivotTo(CFrame.new(pos.X, hit.Position.Y + (c:GetPivot().Position.Y - onder) - 0.2, pos.Z) * rot)
		if p[5] then for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") then d.CastShadow = false end end end
	elseif c:IsA("BasePart") then c.Size = c.Size * p[4]; c.CFrame = CFrame.new(pos.X, hit.Position.Y + c.Size.Y / 2, pos.Z) * rot end
	c.Parent = map; n += 1
	if i % 150 == 0 then task.wait() end
end
map.Parent = workspace
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
return string.format("%d planten, %d overgeslagen onder de reus; ontbrekend: %s", n, weg, table.concat(mm, ","))
