-- De Zes Dienaren / Kogeloog: bos en rododendrons achter (ZO) en naast het Kogeloog-gebouwtje (Kogeloog2010: bomen erachter); plein, Langnek (rots + vijver, NW)
-- en de paden vrij.
local F = Vector3.new(0, 0, 1)
local ORIGIN = CFrame.new(485.37, 2.0, 150.69) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local PLEIN = {{5.57, 8.13}, {-0.38, 13.38}, {-5.51, 17.12}, {-9.35, 16.31}, {-9.88, 13.83}, {-11.33, 11.74}, {-13.48, 10.37}, {-15.99, 9.93}, {-18.48, 10.46}, {-19.82, 2.8}, {-19.45, -2.61}, {-19.13, -5.16}, {-16.79, -4.6}, {-15.24, -4.24}, {-15.01, -5.27}, {-12.38, -8.22}, {-8.16, -7.01}, {-9.1, -3.81}, {-2.19, -0.8}, {1.79, 2.14}}
local GEBOUW = {{-8.16, -7.01}, {-9.1, -3.81}, {-2.19, -0.8}, {1.79, 2.14}, {5.57, 8.13}, {8.3, 6.35}, {3.76, -1.13}, {0.03, -3.87}}
local PADEN = {{{2.91, 24.12}, {1.7, 19.07}, {-0.38, 13.38}, {-5.84, 4.57}, {-19.45, -2.61}}, {{7.78, -21.91}, {10.4, -10.46}, {13.05, 0.07}, {20.11, 10.32}}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function lijnd(x, y, p) local best = 1e9
	for i = 1, #p - 1 do local a, b = p[i], p[i + 1]; local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function bezet(x, y, m)
	if inside(x, y, PLEIN) or lijnd(x, y, PLEIN) < m * 0.6 then return true end
	if inside(x, y, GEBOUW) or lijnd(x, y, GEBOUW) < 0.9 + m * 0.6 then return true end
	for _, p in ipairs(PADEN) do if lijnd(x, y, p) < 2.0 + m * 0.5 then return true end end
	if x < -8 and y > 6 then return true end                                                     -- Langnek (rots + vijver)
	if (x - 1.8) ^ 2 + (y + 12) ^ 2 < 9 then return true end                                    -- Vlederikenfontein
	return false
end
local R = Random.new(1952)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L, bomen = {}, {}
for _ = 1, 4000 do
	local x, y = U(-20, 18), U(-20, 14)
	if not bezet(x, y, 2.4) then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 14 then ok = false; break end end
		if ok and #bomen < 28 then table.insert(bomen, {x, y}); local s = {"den0", "beuk0", "eik0", "den1", "beuk1", "berk0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(1.05, 1.4)}) end
	end
end
for _ = 1, 1600 do
	local x, y = U(-20, 18), U(-20, 14)
	local achter = lijnd(x, y, GEBOUW) < 4.5 and not inside(x, y, PLEIN)
	if not bezet(x, y, 0.8) and R:NextNumber() < (achter and 0.8 or 0.3) then local s = {"rododendron0", "rododendron1", "taxus0", "PH_shrub_03_1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.9, 1.3)}) end
end
for _ = 1, 2200 do
	local x, y = U(-20, 18), U(-20, 14)
	if not bezet(x, y, 0.3) and R:NextNumber() < 0.45 then local s = {"PH_fern_02_0", "varen0", "PH_periwinkle_plant_1", "bodem1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2)}) end
end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), workspace:FindFirstChild("HansEnGrietjeGroen"), workspace:FindFirstChild("RodeSchoentjesGroen"), workspace:FindFirstChild("RoodkapjeGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("KogeloogGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "KogeloogGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local klein = {PH_fern_02_0 = true, bodem1 = true, PH_periwinkle_plant_1 = true}
local n, mis = 0, {}
for i, p in ipairs(L) do
	local t = bron(p[1]); if not t then mis[p[1]] = true; continue end
	local c = t:Clone(); local pos = (ORIGIN * CFrame.new(-p[2] * S, 0, p[3] * S)).Position
	local hit = workspace:Raycast(pos + Vector3.new(0, 30, 0), Vector3.new(0, -60, 0), rp); local y = hit and hit.Position.Y or 2
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
local w = game.StarterPlayer.StarterPlayerScripts:FindFirstChild("Wind"); local ok = false
if w and not string.find(w.Source, "KogeloogGroen") then local s2, k = string.gsub(w.Source, '"KabouterdorpGroen" }', '"KabouterdorpGroen", "KogeloogGroen" }', 1); w.Source = s2; ok = k > 0 end
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
return string.format("%d planten (%d bomen); wind %s; ontbrekend: %s", n, #bomen, tostring(ok), table.concat(mm, ","))
