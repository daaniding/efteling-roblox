-- De Kleine Zeemeermin: dichte rododendrons achter het decor en langs de zijkanten (Boekloc), hoge bomen; zicht vanaf de driesprong (zuid) vrij.
local F = Vector3.new(0, 0, 1)
local ORIGIN = CFrame.new(361.59, 2.0, 67.68) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local PLEIN = {{-3.4, -1.2}, {-0.4, -2.75}, {2.7, -2.25}, {3.2, -3.4}, {-0.95, -4.5}, {-3.8, -3.0}}
local WATER = {{-0.32, 2.24}, {1.24, 2.21}, {2.14, -1.63}, {-0.32, -1.97}, {-2.51, -0.88}}
local BORDER = {{0, 0}, {0.01, 0}, {0, 0.01}}
local PAD = {{-19.57, -0.57}, {-0.95, -3.2}, {3.78, -3.86}, {7.85, 3.49}, {9.97, 11.29}, {9.99, 15.28}, {9.68, 18.75}}
local PAD2 = {{-0.95, -3.2}, {-12.51, -32.91}}
local MUREN = {}
local BED = {{100, 100}, {101, 100}, {100, 101}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function lijnd(x, y, p, dicht) local best = 1e9; local n = #p
	for i = 1, (dicht and n or n - 1) do local a, b = p[i], p[(i % n) + 1]
		local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function bezet(x, y, m)
	if inside(x, y, PLEIN) or lijnd(x, y, PLEIN, true) < m then return true end
	if inside(x, y, BORDER) or lijnd(x, y, BORDER, true) < m * 0.5 then return true end
	if lijnd(x, y, PAD, false) < 2.4 + m * 0.5 or lijnd(x, y, PAD2, false) < 2.4 + m * 0.5 then return true end
	if x > -3.0 and x < 3.0 and y > -2.2 and y < 3.0 then return true end                 -- vijver + decor
	for _, w in ipairs(MUREN) do if lijnd(x, y, w, false) < 0.45 + m * 0.3 then return true end end
	return false
end
local function zicht(x, y) return y < -1.8 and x > -6 and x < 6 end
local R = Random.new(2025)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L, bomen = {}, {}
for _ = 1, 6000 do
	local x, y = U(-26, 26), U(-22, 22)
	if not bezet(x, y, 2.6) and not zicht(x, y) and not inside(x, y, BED) then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 16 then ok = false; break end end
		if ok and #bomen < 55 then table.insert(bomen, {x, y}); local s = {"beuk0", "beuk1", "beuk0", "eik0", "beuk1", "eik1", "den0", "kastanje0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.95, 1.35)}) end
	end
end
for _ = 1, 3200 do
	local x, y = U(-24, 24), U(-20, 20)
	local d = lijnd(x, y, PLEIN, true)
	if not bezet(x, y, 0.7) and not inside(x, y, BED) and R:NextNumber() < (d < 6 and 0.75 or 0.3) and not zicht(x, y) then
		local s = {"rododendron0", "rododendron1", "rododendron0", "rododendron1", "taxus0", "PH_shrub_03_1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.25)})
	end
end
for gx = -4.5, 4.5, 0.85 do for gy = 2.9, 6.0, 0.85 do                -- dichte plantenwand achter het decor (Boekloc)
	table.insert(L, {(R:NextNumber() < 0.6) and "rododendron1" or "rododendron0", gx + U(-0.3, 0.3), gy + U(-0.3, 0.3), U(1.2, 1.6)})
end end
for gx = 2.9, 5.6, 0.85 do for gy = -1.4, 3.0, 0.85 do                 -- rododendronmassa rechts naast het hek (Boekloc)
	table.insert(L, {(R:NextNumber() < 0.6) and "rododendron1" or "rododendron0", gx + U(-0.3, 0.3), gy + U(-0.3, 0.3), U(1.1, 1.5)})
end end
for _ = 1, 4000 do
	local x, y = U(-24, 24), U(-20, 20)
	if not bezet(x, y, 0.3) and R:NextNumber() < 0.45 then
		local s = {"PH_fern_02_0", "PH_fern_02_3", "varen0", "PH_fern_02_2", "PH_periwinkle_plant_1", "bodem1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2)})
	end
end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), workspace:FindFirstChild("HansEnGrietjeGroen"), workspace:FindFirstChild("HerautenpleinGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("KleineZeemeerminGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "KleineZeemeerminGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local klein = {PH_fern_02_0 = true, PH_fern_02_3 = true, PH_fern_02_2 = true, varen0 = true, bodem1 = true, PH_periwinkle_plant_1 = true, siergras0 = true,
	bloem_rood = true, bloem_wit = true, bloem_roze = true, PH_flower_ursinia_4 = true, PH_shrub_sorrel_01_9 = true}
local n, mis = 0, {}
local buf = Instance.new("Folder")
for i, p in ipairs(L) do
	local t = bron(p[1]); if not t then mis[p[1]] = true; continue end
	local c = t:Clone(); local pos = (ORIGIN * CFrame.new(-p[2] * S, 0, p[3] * S)).Position
	local y
	if p[5] then y = 2 + p[5] * S else local hit = workspace:Raycast(pos + Vector3.new(0, 30, 0), Vector3.new(0, -60, 0), rp); y = hit and hit.Position.Y or 2 end
	local rot = CFrame.Angles(0, R:NextNumber() * math.pi * 2, 0)
	if c:IsA("Model") then
		if p[4] ~= 1 then c:ScaleTo(c:GetScale() * p[4]) end
		local cf, sz = c:GetBoundingBox(); c:PivotTo(CFrame.new(pos.X, y + (c:GetPivot().Position.Y - (cf.Position.Y - sz.Y / 2)) - 0.15, pos.Z) * rot)
	elseif c:IsA("BasePart") then c.Size = c.Size * p[4]; c.CFrame = CFrame.new(pos.X, y + c.Size.Y / 2 - 0.15, pos.Z) * rot end
	if klein[p[1]] then for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") then d.CastShadow = false end end end
	c.Parent = buf; n += 1
	if i % 150 == 0 then buf.Parent = map; buf = Instance.new("Folder"); task.wait() end
end
buf.Parent = map
for _, f in ipairs(map:GetChildren()) do for _, c in ipairs(f:GetChildren()) do c.Parent = map end; f:Destroy() end
map.Parent = workspace
local w = game.StarterPlayer.StarterPlayerScripts:FindFirstChild("Wind")
if w and not string.find(w.Source, "KleineZeemeerminGroen") then w.Source = string.gsub(w.Source, '"SprekendePapegaaiGroen" }', '"SprekendePapegaaiGroen", "KleineZeemeerminGroen" }', 1) end
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
return string.format("%d planten (%d bomen); ontbrekend: %s", n, #bomen, table.concat(mm, ","))
