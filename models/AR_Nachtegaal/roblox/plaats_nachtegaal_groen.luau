-- De Chinese Nachtegaal: voortuin met rododendrons/azalea's langs de muren, siergras-pollen (bamboe-effect) en varens tussen de lavarotsen; bos buiten
-- de tuinmuren en het raamwerk, bomen rond het paleisblok; paleis, pad, vijver (noord), Siertuin (oost) en Repelsteeltje (zuidwest) vrij.
local F = Vector3.new(0.143, 0, 0.990)
local ORIGIN = CFrame.new(400.32, 2.0, -526.62) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local TUIN = {{-22.51, 9.1}, {-20.46, 10.63}, {-18.46, 12.12}, {-5.12, 11.84}, {-5.1, 7.26}, {-5.1, 4.17}, {-7.66, 4.17}, {-7.66, -3.71}, {-5.5, -3.7}, {-5.5, -6.2}, {-21.2, -6.2}}
local PAD = {{-20.46, 10.63}, {-18.63, 8.1}, {-17.82, 5.44}, {-18.07, 2.22}, {-18.23, -0.19}, {-17.7, -2.3}, {-15.84, -2.61}, {-13.4, -1.47}, {-11.1, -0.73}, {-7.66, -0.03}}
local BUITEN = {{-28.21, 16.49}, {-20.46, 10.63}}
local LUS = {{15.93, -29.07}, {12.53, -26.63}, {8.23, -25.88}, {-6.1, -30.75}, {-9.72, -31.03}, {-14.58, -28.97}, {-25.79, -19.87}, {-34.47, 17.11}, {-28.21, 16.49}, {-17.87, 18.16}, {-14.16, 17.97}, {-11.18, 19.02}, {-0.48, 22.38}, {8.12, 23.66}}
local UIT = {{12.53, 4.37}, {14.95, 4.36}, {16.19, 6.4}, {16.22, 15.45}, {16.13, 24.19}}
local VIJVER = {{5.7, 26.6}, {8.09, 20.81}, {6.87, 18.29}, {4.11, 15.96}, {-1.6, 15.46}, {-5.84, 15.52}, {-6.92, 17.38}, {-9.36, 22.26}, {-8.31, 28.19}, {-6.02, 31.59}, {-3.61, 31.58}, {-1.53, 31.23}, {0.52, 30.77}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function lijnd(x, y, p) local best = 1e9
	for i = 1, #p - 1 do local a, b = p[i], p[i + 1]; local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function bezet(x, y, m)
	if x > -6.0 and x < 13.2 and y > -12.0 and y < 7.8 then return true end                  -- paleisblok + achterterrein
	if inside(x, y, TUIN) then return true end
	if x > -3 and x < 5 and y > 7 and y < 11.4 then return true end                           -- rotsen + waterval
	if inside(x, y, VIJVER) or lijnd(x, y, VIJVER) < m * 0.5 + 0.6 then return true end
	if lijnd(x, y, UIT) < 1.8 + m * 0.5 or lijnd(x, y, LUS) < 2.0 + m * 0.5 or lijnd(x, y, BUITEN) < 2.0 + m * 0.5 then return true end
	if x > 18 and y > 10 then return true end                                                  -- Siertuin
	if x < -12 and y < -22 then return true end                                                -- Repelsteeltje
	return false
end
local R = Random.new(1999)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L, bomen = {}, {}
for _ = 1, 6000 do
	local x, y = U(-34, 24), U(-28, 34)
	if not bezet(x, y, 2.4) then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 14 then ok = false; break end end
		if ok and #bomen < 55 then table.insert(bomen, {x, y}); local s = {"beuk0", "beuk1", "den0", "eik0", "den1", "kastanje0", "berk0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(1.05, 1.45), 30}) end
	end
end
for _ = 1, 2600 do
	local x, y = U(-34, 24), U(-28, 34)
	if not bezet(x, y, 0.7) and R:NextNumber() < 0.45 then local s = {"rododendron0", "rododendron1", "taxus0", "PH_shrub_03_1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.9, 1.3), 17}) end
end
for _ = 1, 900 do                                                                                  -- voortuin: langs de muren azalea's en siergras (bamboe)
	local x, y = U(-22.4, -5.6), U(-6.0, 11.6)
	if inside(x, y, TUIN) and lijnd(x, y, PAD) > 1.6 and not ((x + 14.6) ^ 2 + (y - 1.95) ^ 2 < 4.5) and not (x > -9.6 and y > -4 and y < 4.4) then
		local rand = math.min(math.abs(y - 11.6), math.abs(y + 6.0), math.abs(x + 22) , math.abs(x + 5.4))
		if rand < 1.6 and R:NextNumber() < 0.5 then local s = {"rododendron1", "siergras1", "siergras0", "rododendron0", "siergras1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(1.1, 1.6), 99})
		elseif R:NextNumber() < 0.12 then local s = {"varen0", "PH_fern_02_0", "bodem1", "siergras0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.1), 99}) end
	end
end
for _ = 1, 3000 do
	local x, y = U(-34, 24), U(-28, 34)
	if not bezet(x, y, 0.3) and R:NextNumber() < 0.45 then local s = {"PH_fern_02_0", "varen0", "PH_fern_02_2", "PH_periwinkle_plant_1", "bodem1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2), 8}) end
end
do local L2 = {}
	for _, p in ipairs(L) do local x, y = p[2], p[3]
		if (x > -26 and x < 18 and y > -14 and y < 16) or math.min(lijnd(x, y, LUS), lijnd(x, y, UIT), lijnd(x, y, BUITEN)) <= p[5] then table.insert(L2, p) end end
	L = L2 end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), workspace:FindFirstChild("HansEnGrietjeGroen"), workspace:FindFirstChild("RodeSchoentjesGroen"), workspace:FindFirstChild("RoodkapjeGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("NachtegaalGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "NachtegaalGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local klein = {PH_fern_02_0 = true, PH_fern_02_2 = true, bodem1 = true, PH_periwinkle_plant_1 = true}
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
if w and not string.find(w.Source, "NachtegaalGroen") then local s2, k = string.gsub(w.Source, '"FakirGroen" }', '"FakirGroen", "NachtegaalGroen" }', 1); w.Source = s2; ok = k > 0 end
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
local function L3(x, y, z) local q = (ORIGIN * CFrame.new(-x * 3, z * 3, y * 3)).Position; return string.format("[%.1f, %.1f, %.1f]", q.X, q.Y, q.Z) end
return string.format("%d planten (%d bomen); wind %s; ontbrekend: %s | tuin %s -> %s | noord %s -> %s", n, #bomen, tostring(ok), table.concat(mm, ","), L3(-15.5, -3.6, 1.7), L3(-7, 1, 2.5), L3(-1, 21, 1.7), L3(4, 2, 6))
