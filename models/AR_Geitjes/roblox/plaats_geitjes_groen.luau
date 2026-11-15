-- De Wolf en de Zeven Geitjes: bos rond het huisje, rododendrons langs het pad en het hek, plantenwand achter de achtertuin (zuid); zicht vanaf het hoofdpad (noord/oost) op huis, gezicht en tuin vrij.
local F = Vector3.new(0.1265, 0, 0.992)
local ORIGIN = CFrame.new(300.3, 2.0, -127.23) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local PLEIN = {{-12.5, 3.0}, {-7.6, -0.75}, {-4.9, -0.75}, {-4.9, -0.4}, {5.4, -0.4}, {5.4, -0.8}, {7.2, -0.9}, {11.3, 0.9}, {12.2, 2.1}, {8.8, 5.4}, {2.0, 7.8}, {-4.6, 7.7}}
local WATER = {{100, 100}, {101, 100}, {100, 101}}
local BORDER = {{0, 0}, {0.01, 0}, {0, 0.01}}
local PAD = {{18.28, -5.95}, {11.59, 1.81}, {8.52, 4.49}, {1.93, 6.77}, {-4.46, 6.65}, {-11.96, 2.89}, {-14.56, 1.37}, {-17.58, -0.95}, {-23.15, -5.4}}
local PAD2 = {{11.59, 1.81}, {7.17, -0.09}, {4.76, 0.02}}
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
	if x > -5.2 and x < 5.8 and y > -4.6 and y < 4.2 then return true end                 -- huisje
	if x > -4.0 and x < 7.2 and y > -11.2 and y < -4.6 and m > 0.5 then return true end     -- achtertuin (put, puthaal, wiel, waslijn): open, alleen bodem
	if (x - 13.3) ^ 2 + (y + 1.1) ^ 2 < 7 then return true end                             -- afdakje moeder geit
	if x > 24 then return true end                                                           -- Kabouterdorp (oost) vrij
	for _, w in ipairs(MUREN) do if lijnd(x, y, w, false) < 0.45 + m * 0.3 then return true end end
	return false
end
local function zicht(x, y) return x > 6.5 and x < 12 and y > -9 and y < 0.5 end
local R = Random.new(2025)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L, bomen = {}, {}
for _ = 1, 6000 do
	local x, y = U(-26, 26), U(-22, 11)
	if not bezet(x, y, 2.6) and not zicht(x, y) and not inside(x, y, BED) then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 16 then ok = false; break end end
		if ok and #bomen < 55 then table.insert(bomen, {x, y}); local s = {"beuk0", "beuk1", "beuk0", "eik0", "beuk1", "eik1", "den0", "kastanje0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.95, 1.35), 30}) end
	end
end
for _ = 1, 3200 do
	local x, y = U(-24, 24), U(-20, 11)
	local d = lijnd(x, y, PLEIN, true)
	if not bezet(x, y, 0.7) and not inside(x, y, BED) and R:NextNumber() < (d < 6 and 0.75 or 0.3) and not zicht(x, y) then
		local s = {"rododendron0", "rododendron1", "rododendron0", "rododendron1", "taxus0", "PH_shrub_03_1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.25), 17})
	end
end
for gx = -6.5, 9.5, 0.85 do for gy = -14.5, -11.8, 0.85 do              -- plantenwand achter de achtertuin
	table.insert(L, {(R:NextNumber() < 0.6) and "rododendron1" or "rododendron0", gx + U(-0.3, 0.3), gy + U(-0.3, 0.3), U(1.3, 1.8), 99})
end end
for gx = 9.0, 11.5, 0.85 do for gy = -5.5, -1.5, 0.85 do                -- rododendrons achter het afdakje van moeder geit (Moeder-geit)
	table.insert(L, {(R:NextNumber() < 0.6) and "rododendron1" or "rododendron0", gx + U(-0.3, 0.3), gy + U(-0.3, 0.3), U(1.0, 1.4), 99})
end end
for _ = 1, 4000 do
	local x, y = U(-24, 24), U(-20, 11)
	if not bezet(x, y, 0.3) and R:NextNumber() < 0.45 then
		local s = {"PH_fern_02_0", "PH_fern_02_3", "varen0", "PH_fern_02_2", "PH_periwinkle_plant_1", "bodem1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2), 8})
	end
end
-- snoeien: wat je vanaf het pad toch niet ziet niet plaatsen (scene rond huis + tuin + moeder geit blijft); p[5] = max. afstand tot het pad (m)
do local L2 = {}
	for _, p in ipairs(L) do local x, y = p[2], p[3]
		if (x > -9 and x < 17 and y > -15 and y < 9) or math.min(lijnd(x, y, PAD, false), lijnd(x, y, PAD2, false)) <= p[5] then table.insert(L2, p) end end
	L = L2 end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), workspace:FindFirstChild("HansEnGrietjeGroen"), workspace:FindFirstChild("HerautenpleinGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("GeitjesGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "GeitjesGroen"
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
if w and not string.find(w.Source, "GeitjesGroen") then w.Source = string.gsub(w.Source, '"DraakGroen" }', '"DraakGroen", "GeitjesGroen" }', 1) end
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
return string.format("%d planten (%d bomen); ontbrekend: %s", n, #bomen, table.concat(mm, ","))
