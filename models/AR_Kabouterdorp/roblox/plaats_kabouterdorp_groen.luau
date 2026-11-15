-- Het Kabouterdorp: bos tussen de paddenstoelenhuisjes (hoge bomen, rododendrons, varens, bodemplanten); paden, vijvers, beek en huisjes vrij;
-- de Draak (zuidwest) en Doornroosje (noord) laten we met rust.
local F = Vector3.new(0, 0, 1)
local ORIGIN = CFrame.new(458.25, 2.0, -63.78) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local HOOFDPAD = {{-8.11, 36.56}, {-5.82, 31.33}, {-4.82, 29.28}, {-3.59, 19.72}, {-3.25, 14.84}, {-2.22, 6.19}, {-2.4, 3.97}, {4.66, -5.64}, {5.73, -9.14}, {8.73, -29.62}}
local ZIJ = {
	{{-3.59, 19.72}, {-8.84, 19.77}, {-16.23, 21.93}, {-18.77, 22.24}, {-21.42, 22.7}, {-22.33, 22.8}},
	{{-3.25, 14.84}, {3.01, 16.22}, {10.68, 17.37}}, {{-2.22, 6.19}, {3.66, 6.92}, {6.86, 7.58}}, {{-0.32, 29.72}, {3.96, 29.5}, {6.72, 27.79}},
	{{-2.4, 3.97}, {-5.31, -0.87}, {-6.52, -3.35}, {-6.67, -4.37}, {-5.55, -8.41}, {-1.67, -9.36}, {2.08, -9.52}, {5.73, -9.14}},
	{{3.66, 6.92}, {7.15, 1.93}, {6.39, -2.97}, {4.66, -5.64}}, {{12.6, 23.4}, {13.4, 19.5}, {13.9, 16.4}, {13.4, 14.2}}}
local VIJVERS = {
	{{-6.9, 28.13}, {-5.98, 23.11}, {-10.56, 23.26}, {-18.06, 24.59}, {-14.73, 26.98}},
	{{13.45, 12.25}, {13.2, 14.38}, {10.34, 13.06}, {7.94, 10.57}, {7.33, 8.89}, {8.56, 4.93}, {11.57, 3.42}, {15.25, 3.87}, {17.75, 6.21}, {18.56, 8.49}, {16.59, 9.26}},
	{{-8.83, -4.93}, {-10.27, -3.46}, {-6.83, -1.44}, {-4.15, -1.56}, {-1.46, -3.36}, {0.66, -5.98}, {1.19, -8.92}, {1.14, -12.16}, {-2.15, -13.36}, {-5.29, -13.0}, {-5.33, -10.18}, {-1.67, -9.36}, {-4.04, -4.62}, {-7.18, -3.01}}}
local HUIZEN = {{-17.55, 21.5, 2.7}, {-22.4, 22.6, 2.1}, {-13.8, 19.3, 1.6}, {-11.0, 18.0, 1.5}, {-11.1, 21.2, 1.3}, {-6.64, 16.95, 3.2}, {10.4, 5.4, 2.4},
	{13.4, 9.0, 3.4}, {9.27, 24.84, 5.3}, {15.6, 18.2, 2.6}, {13.2, 21.0, 1.7}, {-5.0, -6.9, 4.4}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function lijnd(x, y, p) local best = 1e9
	for i = 1, #p - 1 do local a, b = p[i], p[i + 1]; local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function bezet(x, y, m)
	if lijnd(x, y, HOOFDPAD) < 2.0 + m * 0.5 then return true end
	for _, z in ipairs(ZIJ) do if lijnd(x, y, z) < 1.2 + m * 0.5 then return true end end
	for _, v in ipairs(VIJVERS) do if inside(x, y, v) then return true end end
	for _, h in ipairs(HUIZEN) do if (x - h[1]) ^ 2 + (y - h[2]) ^ 2 < (h[3] + m * 0.6) ^ 2 then return true end end
	if x < -26 and y < 6 then return true end                                                   -- Draak Lichtgeraakt
	if y > 37 then return true end                                                              -- Doornroosje
	return false
end
local R = Random.new(1952)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L, bomen = {}, {}
for _ = 1, 7000 do
	local x, y = U(-28, 24), U(-28, 37)
	if not bezet(x, y, 2.4) then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 16 then ok = false; break end end
		if ok and #bomen < 60 then table.insert(bomen, {x, y}); local s = {"beuk0", "eik0", "beuk1", "den0", "eik1", "kastanje0", "den1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(1.05, 1.45), 30}) end
	end
end
for _ = 1, 3000 do
	local x, y = U(-28, 24), U(-28, 37)
	if not bezet(x, y, 0.8) and R:NextNumber() < 0.42 then local s = {"rododendron0", "rododendron1", "taxus0", "PH_shrub_03_1", "PH_shrub_02_0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.25), 17}) end
end
for _ = 1, 5500 do
	local x, y = U(-28, 24), U(-28, 37)
	if not bezet(x, y, 0.25) and R:NextNumber() < 0.5 then local s = {"PH_fern_02_0", "varen0", "varen1", "PH_fern_02_3", "PH_periwinkle_plant_1", "bodem1", "bodem1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2), 8}) end
end
do local L2 = {}                                                                              -- snoeien: het hele dorp is scene, daarbuiten op padafstand
	for _, p in ipairs(L) do local x, y = p[2], p[3]
		if (x > -24 and x < 20 and y > -26 and y < 34) or lijnd(x, y, HOOFDPAD) <= p[5] then table.insert(L2, p) end end
	L = L2 end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), workspace:FindFirstChild("HansEnGrietjeGroen"), workspace:FindFirstChild("RodeSchoentjesGroen"), workspace:FindFirstChild("RoodkapjeGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("KabouterdorpGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "KabouterdorpGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local klein = {PH_fern_02_0 = true, PH_fern_02_3 = true, bodem1 = true, PH_periwinkle_plant_1 = true}
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
if w and not string.find(w.Source, "KabouterdorpGroen") then local s2, k = string.gsub(w.Source, '"NachtegaalGroen" }', '"NachtegaalGroen", "KabouterdorpGroen" }', 1); w.Source = s2; ok = k > 0 end
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
local function L3(x, y, z) local q = (ORIGIN * CFrame.new(-x * 3, z * 3, y * 3)).Position; return string.format("[%.1f, %.1f, %.1f]", q.X, q.Y, q.Z) end
return string.format("%d planten (%d bomen); wind %s; ontbrekend: %s | parcours %s -> %s | zwam %s -> %s | huis %s -> %s", n, #bomen, tostring(ok), table.concat(mm, ","),
	L3(-4.2, 18.5, 1.7), L3(-17, 21.5, 2), L3(2.5, 14.5, 1.7), L3(11, 22, 3), L3(3.4, -2.2, 1.7), L3(-5, -7, 2))
