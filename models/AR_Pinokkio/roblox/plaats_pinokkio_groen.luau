-- Pinokkio: bos rond het plein en het haventje (Pinokkiototaal, Monstervis-achter: rododendrons, varens, hoge bomen; riet en lissen langs de oever).
local F = Vector3.new(-0.364, 0, -0.931)
local ORIGIN = CFrame.new(149.16, 2.0, 182.31) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local PLEIN = {{9.21, -6.29}, {9.74, -5.57}, {11.02, -5.77}, {12.59, -5.2}, {13.39, -4.0}, {13.49, -2.71}, {12.91, -1.4}, {11.93, -0.61}, {10.61, -0.38}, {9.28, -0.68}, {8.61, -1.08}, {8.16, -1.37}, {7.51, -1.78}, {7.0, -1.69}, {6.76, -1.33}, {6.26, 1.73}, {5.13, 1.67}, {2.09, 1.51}, {2.1, -0.08}, {2.12, -2.7}, {-2.79, -2.7}, {-2.81, -0.18}, {-4.32, -0.67}, {-5.93, -1.77}, {-6.22, -3.44}, {-5.12, -5.52}, {-2.18, -6.9}, {-0.38, -8.36}, {-0.05, -10.2}, {1.23, -9.95}, {3.04, -9.0}, {6.87, -9.24}, {8.09, -7.49}, {9.21, -6.29}}
local VIJVER = {{9.96, -5.99}, {9.58, -6.38}, {16.49, -11.14}, {16.71, -10.88}, {19.86, -12.5}, {21.78, -13.08}, {23.08, -13.14}, {24.33, -13.01}, {25.53, -12.47}, {26.05, -11.14}, {26.5, -9.67}, {27.92, -8.55}, {29.59, -8.43}, {30.5, -7.5}, {30.61, -6.14}, {29.96, -5.09}, {28.93, -4.62}, {27.51, -3.98}, {26.25, -2.98}, {25.73, -1.38}, {22.42, -0.42}, {22.4, -1.77}, {21.51, -2.96}, {20.35, -3.16}, {19.55, -2.91}, {18.67, -1.83}, {17.95, -0.74}, {17.17, -0.01}, {15.92, 0.48}, {14.54, 0.32}, {13.76, -0.49}, {13.78, -1.62}, {14.09, -3.47}, {13.82, -4.49}, {13.12, -5.43}, {12.31, -5.98}, {11.39, -6.29}, {9.96, -5.99}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function polyd(x, y, p) local best = 1e9; local n = #p
	for i = 1, n do local a, b = p[i], p[(i % n) + 1]
		local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function bezet(x, y, m) return inside(x, y, PLEIN) or polyd(x, y, PLEIN) < m or (x > -3.4 and x < 3.0 and y > -3.3 and y < 2.8) or (x > 1.8 and x < 9.2 and y > -2.2 and y < 2.3) end
local R = Random.new(2016)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L, bomen = {}, {}
for _ = 1, 5000 do
	local x, y = U(-22, 40), U(-24, 22)
	if not bezet(x, y, 2.0) and not inside(x, y, VIJVER) and polyd(x, y, VIJVER) > 2.2 then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 15 then ok = false; break end end
		if ok and #bomen < 70 then table.insert(bomen, {x, y}); local s = {"beuk0", "eik0", "den0", "den1", "kastanje0", "berk0", "beuk0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.95, 1.3)}) end
	end
end
for _ = 1, 3500 do
	local x, y = U(-20, 38), U(-22, 20)
	local dp = polyd(x, y, PLEIN)
	if not bezet(x, y, 0.5) and not inside(x, y, VIJVER) and polyd(x, y, VIJVER) > 0.9 and R:NextNumber() < (dp < 4 and 0.55 or 0.2) then
		local s = {"rododendron0", "rododendron1", "taxus0", "PH_shrub_03_1", "rododendron0", "PH_shrub_02_3"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.25)})
	end
end
for _ = 1, 4500 do
	local x, y = U(-20, 38), U(-22, 20)
	if not bezet(x, y, 0.3) and not inside(x, y, VIJVER) and polyd(x, y, VIJVER) > 0.5 and R:NextNumber() < 0.45 then
		local s = {"PH_fern_02_0", "PH_fern_02_3", "varen1", "PH_fern_02_2"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2)})
	end
end
local oever = {}
for i = 1, #VIJVER - 1 do
	local a, b = VIJVER[i], VIJVER[i + 1]; local Ls = math.sqrt((b[1] - a[1]) ^ 2 + (b[2] - a[2]) ^ 2)
	for k = 0, math.floor(Ls / 0.9) do
		local t = k / math.max(1, math.floor(Ls / 0.9)); local x, y = a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t
		if polyd(x, y, PLEIN) > 1.5 and R:NextNumber() < 0.75 then table.insert(oever, {x + U(-0.25, 0.25), y + U(-0.25, 0.25)}) end
	end
end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), workspace:FindFirstChild("HerautenpleinGroen"), workspace:FindFirstChild("HansEnGrietjeGroen"), workspace:FindFirstChild("KleinDuimpjeWater")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("PinokkioGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "PinokkioGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local klein = {PH_fern_02_0 = true, PH_fern_02_3 = true, PH_fern_02_2 = true, varen1 = true, siergras0 = true, siergras1 = true, bloem_geel = true}
for _, o in ipairs(oever) do table.insert(L, {(R:NextNumber() < 0.3) and "bloem_geel" or ((R:NextNumber() < 0.5) and "siergras0" or "siergras1"), o[1], o[2], U(0.8, 1.2), true}) end
local n, mis = 0, {}
for i, p in ipairs(L) do
	local t = bron(p[1]); if not t then mis[p[1]] = true; continue end
	local c = t:Clone(); local pos = (ORIGIN * CFrame.new(-p[2] * S, 0, p[3] * S)).Position
	local y = 2
	if not p[5] then local hit = workspace:Raycast(pos + Vector3.new(0, 30, 0), Vector3.new(0, -60, 0), rp); y = hit and hit.Position.Y or 2 end
	local rot = CFrame.Angles(0, R:NextNumber() * math.pi * 2, 0)
	if c:IsA("Model") then
		if p[4] ~= 1 then c:ScaleTo(c:GetScale() * p[4]) end
		local cf, sz = c:GetBoundingBox(); c:PivotTo(CFrame.new(pos.X, y + (c:GetPivot().Position.Y - (cf.Position.Y - sz.Y / 2)) - 0.15, pos.Z) * rot)
	elseif c:IsA("BasePart") then c.Size = c.Size * p[4]; c.CFrame = CFrame.new(pos.X, y + c.Size.Y / 2 - 0.15, pos.Z) * rot end
	if klein[p[1]] then for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") then d.CastShadow = false end end end
	c.Parent = map; n += 1
	if i % 150 == 0 then task.wait() end
end
map.Parent = workspace
local w = game.StarterPlayer.StarterPlayerScripts:FindFirstChild("Wind")
if w and not string.find(w.Source, "PinokkioGroen") then w.Source = string.gsub(w.Source, '"RoodkapjeGroen" }', '"RoodkapjeGroen", "PinokkioGroen" }', 1) end
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
return string.format("%d planten (%d bomen, %d oever); ontbrekend: %s", n, #bomen, #oever, table.concat(mm, ","))
