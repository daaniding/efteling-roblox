-- De Indische Waterlelies: boomvarens in de borders langs de witte muren en in het plantenbed, bomen buiten de muren en rond de rotstunnel, hoge bomen
-- rond de groene showloods (verstopt de loods); plein, vijver, gaanderij, loods, Zwavelstokjes (noord) en Assepoester/Herautenplein (west/zuid) vrij.
local F = Vector3.new(0.213, 0, 0.977)
local ORIGIN = CFrame.new(109.98, 2.0, -351.87) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local PLEIN = {{9.19, 5.12}, {9.57, -9.21}, {9.61, -10.92}, {15.66, -12.72}, {15.55, -15.8}, {-16.43, -15.97}, {-16.48, -8.1}, {-16.5, 5.1}, {-9.78, 5.1}, {-7.67, 5.11}, {7.83, 5.12}}
local LOODS = {{4.4, 10.0}, {4.4, 30.2}, {19.66, 31.24}, {31.66, 31.24}, {31.71, 19.15}, {8.32, 11.63}, {8.32, 10.0}}
local GANG = {{31.71, 19.15}, {42.0, 19.9}, {42.0, 16.9}, {38.2, 16.4}, {41.1, 15.6}, {47.1, 10.6}, {48.4, 10.56}, {54.6, 6.3}, {58.9, 5.3}, {58.9, 2.35}, {55.7, 2.5}, {48.9, 7.2}, {46.9, 7.35}, {41.1, 11.3}, {39.4, 11.66}, {23.86, 11.64}, {15.51, 11.64}, {8.32, 11.63}}
local PAD = {{21.5, -40}, {21.66, -22.2}, {22.02, -18.25}, {22.33, -14.81}, {15.59, -14.15}, {-2.72, -11.05}, {-9.68, -7.02}, {-9.78, 5.1}, {-9.74, 7.52}, {6.29, 7.59}}
local PAD2 = {{58.9, 3.8}, {66, 2}, {75, 4}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function lijnd(x, y, p) local best = 1e9
	for i = 1, #p - 1 do local a, b = p[i], p[i + 1]; local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function bezet(x, y, m)
	if inside(x, y, PLEIN) or x > -16.8 and x < 16 and y > -16.3 and y < 11 then return true end              -- plein + gaanderij + muren
	if x > 9 and x < 25.8 and y > -19.2 and y < -8.5 then return true end                                       -- rotstunnel
	if inside(x, y, LOODS) or inside(x, y, GANG) then return true end
	if lijnd(x, y, PAD) < 2.2 + m * 0.5 or lijnd(x, y, PAD2) < 2.2 + m * 0.5 then return true end
	if y > 31.5 and x < 32 then return true end                                                                 -- Zwavelstokjes
	if x < -21 and y < 4 then return true end                                                                   -- Assepoester / Herautenplein
	return false
end
local R = Random.new(1966)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L, bomen = {}, {}
for _ = 1, 9000 do
	local x, y = U(-24, 64), U(-26, 36)
	if not bezet(x, y, 2.6) then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 18 then ok = false; break end end
		if ok and #bomen < 75 then table.insert(bomen, {x, y}); local s = {"beuk0", "beuk1", "eik0", "beuk1", "eik1", "den0", "kastanje0", "den1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(1.05, 1.45), 30}) end
	end
end
for _ = 1, 3500 do
	local x, y = U(-24, 64), U(-26, 36)
	if not bezet(x, y, 0.7) and R:NextNumber() < 0.45 then local s = {"rododendron0", "rododendron1", "taxus0", "PH_shrub_03_1", "rododendron1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.9, 1.3), 17}) end
end
for x = -15.6, 13.6, 1.3 do table.insert(L, {(R:NextNumber() < 0.5) and "varen0" or "varen1", x + U(-0.2, 0.2), -15.25 + U(-0.1, 0.1), U(1.8, 2.4), 99, 0.12}) end    -- boomvarens langs de zuidmuur
for y = -14.2, 4.4, 1.3 do table.insert(L, {(R:NextNumber() < 0.5) and "varen0" or "varen1", -15.7 + U(-0.1, 0.1), y + U(-0.2, 0.2), U(1.8, 2.4), 99, 0.12}) end      -- en de westmuur
for gx = -15.8, -12.9, 0.7 do for gy = -6.2, 3.1, 0.7 do                                                       -- dicht plantenbed (voorplein-mei09)
	local s = {"PH_shrub_02_0", "varen0", "PH_periwinkle_plant_1", "bodem1", "PH_shrub_03_1"}; table.insert(L, {s[R:NextInteger(1, #s)], gx + U(-0.2, 0.2), gy + U(-0.2, 0.2), U(0.8, 1.2), 99, 0.45})
end end
for _, p in ipairs({{-5.5, -6.2}, {3.6, -6.4}, {9.0, 4.0}, {-13.5, -9.0}}) do table.insert(L, {"taxus0", p[1], p[2], 0.75, 99}) end                       -- bolconifeertjes in potten
for _ = 1, 5000 do
	local x, y = U(-24, 64), U(-26, 36)
	if not bezet(x, y, 0.3) and R:NextNumber() < 0.45 then local s = {"PH_fern_02_0", "PH_fern_02_3", "varen0", "PH_fern_02_2", "PH_periwinkle_plant_1", "bodem1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2), 8}) end
end
do local L2 = {}                                                                                                -- snoeien op padafstand (scene blijft)
	for _, p in ipairs(L) do local x, y = p[2], p[3]
		if (x > -20 and x < 30 and y > -22 and y < 14) or math.min(lijnd(x, y, PAD), lijnd(x, y, PAD2)) <= p[5] or (p[1]:sub(1, 4) == "beuk" or p[1]:sub(1, 3) == "eik" or p[1]:sub(1, 3) == "den" or p[1]:sub(1, 8) == "kastanje") and (inside(x - 4, y, LOODS) or inside(x + 4, y, LOODS) or inside(x, y - 4, LOODS) or inside(x, y + 4, LOODS) or inside(x, y - 4, GANG) or inside(x, y + 4, GANG)) then table.insert(L2, p) end end
	L = L2 end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), workspace:FindFirstChild("HansEnGrietjeGroen"), workspace:FindFirstChild("RodeSchoentjesGroen"), workspace:FindFirstChild("RoodkapjeGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("WaterleliesGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "WaterleliesGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local klein = {PH_fern_02_0 = true, PH_fern_02_3 = true, PH_fern_02_2 = true, bodem1 = true, PH_periwinkle_plant_1 = true}
local n, mis = 0, {}
local buf = Instance.new("Folder")
for i, p in ipairs(L) do
	local t = bron(p[1]); if not t then mis[p[1]] = true; continue end
	local c = t:Clone(); local pos = (ORIGIN * CFrame.new(-p[2] * S, 0, p[3] * S)).Position
	local hit = workspace:Raycast(pos + Vector3.new(0, 30, 0), Vector3.new(0, -60, 0), rp); local y = (hit and hit.Position.Y or 2) + (p[6] or 0) * S
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
local w = game.StarterPlayer.StarterPlayerScripts:FindFirstChild("Wind"); local ok = false
if w and not string.find(w.Source, "WaterleliesGroen") then local s2, k = string.gsub(w.Source, '"KleineBoodschapGroen" }', '"KleineBoodschapGroen", "WaterleliesGroen" }', 1); w.Source = s2; ok = k > 0 end
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
return string.format("%d planten (%d bomen); wind %s; ontbrekend: %s", n, #bomen, tostring(ok), table.concat(mm, ","))
