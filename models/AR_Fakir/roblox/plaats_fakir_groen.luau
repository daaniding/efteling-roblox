-- De Vliegende Fakir: dichte plantenwand + hoge bomen achter de kantelenmuur (Fakirpaleis: donker bos achter het paleis), rododendrons naast de
-- oosterse hekjes (Boekloc), tulpen in de randen (wit links - geel ontbreekt in de bron -, rood rechts); plein, tuin, Sprookjesboom (west), Siertuin (oost) en station (noord) vrij.
local F = Vector3.new(0.127, 0, 0.992)
local ORIGIN = CFrame.new(240.66, 2.0, -638.46) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local PAD = {{-22.83, 2.08}, {-17.67, 4.68}, {-11.27, 8.47}, {-2.17, 9.99}, {11.72, 9.35}, {24.69, 4.52}}
local PAD2 = {{-20.39, -32.81}, {-24.58, -23.97}, {-25.37, -17.33}, {-24.8, -12.06}, {-24.21, -6.32}, {-22.83, 2.08}}
local WATER_W = {{-12.85, -7.26}, {-12.1, -7.86}, {-8.94, -7.85}, {-7.83, -7.06}, {-7.89, -0.07}, {-8.35, -0.08}, {-8.3, -3.29}, {-12.4, -3.35}, {-12.45, 0.48}, {-12.97, 0.47}}
local WATER_O = {{8.12, -6.87}, {8.2, -0.11}, {8.65, -0.12}, {8.65, -3.02}, {12.48, -3.04}, {12.5, 0.96}, {13.03, 0.96}, {13.04, -7.09}, {12.68, -7.61}, {8.65, -7.44}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function lijnd(x, y, p) local best = 1e9
	for i = 1, #p - 1 do local a, b = p[i], p[i + 1]; local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function bezet(x, y, m)
	if x > -16.2 and x < 16.8 and y < 5.2 then return true end                       -- paleis, tuin, gras, waterbak, plein (alles ten zuiden van de muur)
	if y < -18 and x > -18 and x < 18 then return true end
	if lijnd(x, y, PAD) < 2.0 + m * 0.5 or lijnd(x, y, PAD2) < 2.0 + m * 0.5 then return true end
	if x < -26 then return true end                                                 -- Sprookjesboom
	if x > 24 then return true end                                                  -- Siertuin
	if y > 14 then return true end                                                  -- spoor / station Marerijk
	return false
end
local R = Random.new(1965)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L, bomen = {}, {}
for _ = 1, 5000 do
	local x, y = U(-26, 24), U(-36, 14)
	if not bezet(x, y, 2.4) then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 14 then ok = false; break end end
		if ok and #bomen < 40 then table.insert(bomen, {x, y}); local s = {"den0", "den1", "beuk0", "eik0", "beuk1", "den0", "kastanje0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(1.1, 1.5), 30}) end
	end
end
for gx = -9.0, 8.5, 0.85 do for gy = 5.3, 8.2, 0.85 do                                    -- plantenwand achter de kantelenmuur
	if lijnd(gx, gy, PAD) > 1.8 then table.insert(L, {(R:NextNumber() < 0.6) and "rododendron1" or "rododendron0", gx + U(-0.3, 0.3), gy + U(-0.3, 0.3), U(1.2, 1.6), 99}) end
end end
for _, sx in ipairs({-1, 1}) do for gx = 16.4, 20.5, 0.85 do for gy = -13, 4, 0.85 do       -- rododendronmassa naast de hekjes (Boekloc)
	if lijnd(sx * gx, gy, PAD) > 2.0 and lijnd(sx * gx, gy, PAD2) > 2.0 then table.insert(L, {(R:NextNumber() < 0.6) and "rododendron1" or "rododendron0", sx * gx + U(-0.3, 0.3), gy + U(-0.3, 0.3), U(1.1, 1.5), 99}) end
end end end
local function rand(G, W, bloem)                                                               -- tulpen in de randen om het L-water
	for gx = G[1], G[2], 0.32 do for gy = G[3], G[4], 0.32 do
		if not inside(gx, gy, W) then table.insert(L, {bloem, gx + U(-0.08, 0.08), gy + U(-0.08, 0.08), U(0.75, 0.95), 99, 0.12}) end
	end end
end
rand({-13.3, -7.6, -9.5, 0.3}, WATER_W, "bloem_wit"); rand({7.8, 13.5, -9.2, 0.8}, WATER_O, "bloem_rood")
for _ = 1, 2500 do
	local x, y = U(-26, 24), U(-36, 14)
	if not bezet(x, y, 0.3) and R:NextNumber() < 0.45 then local s = {"PH_fern_02_0", "varen0", "PH_fern_02_2", "PH_periwinkle_plant_1", "bodem1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2), 8}) end
end
do local L2 = {}
	for _, p in ipairs(L) do local x, y = p[2], p[3]
		if (x > -20 and x < 22 and y > -20 and y < 13) or math.min(lijnd(x, y, PAD), lijnd(x, y, PAD2)) <= p[5] then table.insert(L2, p) end end
	L = L2 end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), workspace:FindFirstChild("HansEnGrietjeGroen"), workspace:FindFirstChild("RodeSchoentjesGroen"), workspace:FindFirstChild("RoodkapjeGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("FakirGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "FakirGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local klein = {PH_fern_02_0 = true, PH_fern_02_2 = true, bodem1 = true, PH_periwinkle_plant_1 = true, bloem_wit = true, bloem_rood = true}
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
if w and not string.find(w.Source, "FakirGroen") then local s2, k = string.gsub(w.Source, '"WaterleliesGroen" }', '"WaterleliesGroen", "FakirGroen" }', 1); w.Source = s2; ok = k > 0 end
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
local function L3(x, y, z) local q = (ORIGIN * CFrame.new(-x * 3, z * 3, y * 3)).Position; return string.format("[%.1f, %.1f, %.1f]", q.X, q.Y, q.Z) end
return string.format("%d planten (%d bomen); wind %s; ontbrekend: %s | cam %s -> %s", n, #bomen, tostring(ok), table.concat(mm, ","), L3(1.5, -27, 1.7), L3(0, 0, 3.5))
