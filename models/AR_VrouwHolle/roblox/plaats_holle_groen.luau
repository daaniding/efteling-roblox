-- Vrouw Holle: bos rond het huisje (midden op het pad) en het ronde putpleintje; rododendrons langs de paden; Herautenplein (noord), Trollenkoning (zuid) en Ezeltje/Herberg (west) vrij; meteen gesnoeid op padafstand.
local F = Vector3.new(0.1184, 0, 0.993)
local ORIGIN = CFrame.new(2.73, 2.0, -90.69) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local PLEIN = {{-10.7, -2.0}, {-10.5, 4.9}, {-6.0, 13.6}, {0.9, 10.3}, {4.1, 6.7}, {7.1, 0.9}, {7.2, -6.2}, {5.3, -13.9}, {-0.6, -12.3}, {-4.6, -10.0}, {-6.6, -8.8}, {-9.2, -5.7}}
local PUT = {10.5, -19.1, 5.9}
local WATER = {{100, 100}, {101, 100}, {100, 101}}
local BORDER = {{0, 0}, {0.01, 0}, {0, 0.01}}
local PAD = {{3.8, 19.57}, {-5.53, 12.41}, {-9.37, 4.66}, {-9.72, -1.88}, {-8.22, -5.2}, {-5.85, -7.98}, {-4.16, -8.96}, {-0.25, -11.22}, {4.25, -12.84}, {9.27, -13.59}, {11.81, -15.0}, {13.78, -16.89}, {15.56, -19.69}, {17.76, -20.87}, {24.0, -24.0}}
local PAD2 = {{4.25, -12.84}, {5.96, -6.06}, {5.9, 0.71}, {3.18, 6.18}, {0.56, 9.17}, {-5.53, 12.41}}
local PAD3 = {{15.56, -19.69}, {13.6, -23.55}, {10.13, -24.52}, {6.89, -23.19}, {5.72, -20.65}, {4.94, -17.98}, {4.25, -12.84}}
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
	if (x - PUT[1]) ^ 2 + (y - PUT[2]) ^ 2 < (PUT[3] + m) ^ 2 then return true end
	if lijnd(x, y, PAD, false) < 2.4 + m * 0.5 or lijnd(x, y, PAD2, false) < 2.4 + m * 0.5 or lijnd(x, y, PAD3, false) < 2.4 + m * 0.5 then return true end
	if y > 14 and x > -8 then return true end                                                -- Herautenplein
	if x < -13 and y > 2 then return true end                                                -- Ezeltje / Herberg
	if (x - 10.7) ^ 2 + (y + 37.7) ^ 2 < 120 then return true end                            -- Trollenkoning
	return false
end
local function zicht(x, y) return false end
local R = Random.new(2025)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L, bomen = {}, {}
for _ = 1, 6000 do
	local x, y = U(-26, 28), U(-34, 16)
	if not bezet(x, y, 2.6) and not zicht(x, y) and not inside(x, y, BED) then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 16 then ok = false; break end end
		if ok and #bomen < 55 then table.insert(bomen, {x, y}); local s = {"beuk0", "beuk1", "beuk0", "eik0", "beuk1", "eik1", "den0", "kastanje0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.95, 1.35), 30}) end
	end
end
for _ = 1, 3200 do
	local x, y = U(-24, 26), U(-32, 16)
	local d = lijnd(x, y, PLEIN, true)
	if not bezet(x, y, 0.7) and not inside(x, y, BED) and R:NextNumber() < (d < 6 and 0.75 or 0.3) and not zicht(x, y) then
		local s = {"rododendron0", "rododendron1", "rododendron0", "rododendron1", "taxus0", "PH_shrub_03_1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.25), 17})
	end
end
for k = 0, 23 do local a = k * math.pi * 2 / 24                               -- rododendronkrans om het putpleintje (Holleput), opening naar de paden
	local x, y = PUT[1] + (PUT[3] + 1.6) * math.cos(a), PUT[2] + (PUT[3] + 1.6) * math.sin(a)
	if lijnd(x, y, PAD, false) > 2.6 and lijnd(x, y, PAD3, false) > 2.6 then table.insert(L, {(R:NextNumber() < 0.6) and "rododendron1" or "rododendron0", x + U(-0.4, 0.4), y + U(-0.4, 0.4), U(1.0, 1.4), 99}) end
end
for gx = -5.0, 1.6, 0.42 do for gy = -8.2, -5.9, 0.42 do                              -- tulpen in het voortuintje (Boekloc); p[6] = ophoging (modderbed)
	if math.abs(gx + 1.8) > 0.6 or gy < -7.6 then local s = {"bloem_rood", "bloem_wit", "bloem_rood", "bloem_roze"}; table.insert(L, {s[R:NextInteger(1, #s)], gx + U(-0.12, 0.12), gy + U(-0.12, 0.12), U(0.8, 1.1), 99, 0.36}) end
end end
for _ = 1, 4000 do
	local x, y = U(-24, 26), U(-32, 16)
	if not bezet(x, y, 0.3) and R:NextNumber() < 0.45 then
		local s = {"PH_fern_02_0", "PH_fern_02_3", "varen0", "PH_fern_02_2", "PH_periwinkle_plant_1", "bodem1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2), 8})
	end
end
-- snoeien: wat je vanaf het pad toch niet ziet niet plaatsen (scene rond huis + tuin + moeder geit blijft); p[5] = max. afstand tot het pad (m)
do local L2 = {}
	for _, p in ipairs(L) do local x, y = p[2], p[3]
		if (x > -13 and x < 19 and y > -27 and y < 14) or math.min(lijnd(x, y, PAD, false), lijnd(x, y, PAD2, false), lijnd(x, y, PAD3, false)) <= p[5] then table.insert(L2, p) end end
	L = L2 end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), workspace:FindFirstChild("HansEnGrietjeGroen"), workspace:FindFirstChild("HerautenpleinGroen"), workspace:FindFirstChild("RodeSchoentjesGroen"), workspace:FindFirstChild("RoodkapjeGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("VrouwHolleGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "VrouwHolleGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local klein = {PH_fern_02_0 = true, PH_fern_02_3 = true, PH_fern_02_2 = true, varen0 = true, bodem1 = true, PH_periwinkle_plant_1 = true, siergras0 = true, bloem_geel = true,
	bloem_rood = true, bloem_wit = true, bloem_roze = true, PH_flower_ursinia_4 = true, PH_shrub_sorrel_01_9 = true}
local n, mis = 0, {}
local buf = Instance.new("Folder")
for i, p in ipairs(L) do
	local t = bron(p[1]); if not t then mis[p[1]] = true; continue end
	local c = t:Clone(); local pos = (ORIGIN * CFrame.new(-p[2] * S, 0, p[3] * S)).Position
	local y
	if false then y = 2 else local hit = workspace:Raycast(pos + Vector3.new(0, 30, 0), Vector3.new(0, -60, 0), rp); y = (hit and hit.Position.Y or 2) + (p[6] or 0) end
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
if w and not string.find(w.Source, "VrouwHolleGroen") then w.Source = string.gsub(w.Source, '"GeitjesGroen" }', '"GeitjesGroen", "VrouwHolleGroen" }', 1) end
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
return string.format("%d planten (%d bomen); ontbrekend: %s", n, #bomen, table.concat(mm, ","))
