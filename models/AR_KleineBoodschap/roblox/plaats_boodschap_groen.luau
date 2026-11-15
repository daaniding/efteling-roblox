-- Kleine Boodschap: begonia's in de rand rond de waterbak, struiken en varens rond de U-haag (binnen 12 m); paden, plein en de Herberg (noord) vrij.
local F = Vector3.new(1, 0, 0)
local ORIGIN = CFrame.new(-46.68, 2.0, -92.28) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local PLEIN = {{-5.2, -7.9}, {4.8, -7.9}, {4.6, -3.0}, {3.0, -2.3}, {2.7, -2.4}, {0.0, -2.72}, {-2.7, -2.4}, {-3.0, -2.3}, {-5.4, -3.6}}
local RAND = {{-2.75, -0.9}, {-2.45, -2.3}, {0.0, -2.6}, {2.45, -2.3}, {2.75, -0.9}, {2.4, 0.2}, {2.0, -0.2}, {1.9, -1.4}, {0.0, -1.95}, {-1.9, -1.4}, {-2.0, -0.2}, {-2.4, 0.2}}
local BAK = {}; for k = 0, 31 do local a = k * math.pi * 2 / 32; table.insert(BAK, {-1.85 * math.cos(a) * ((math.sin(a) < 0) and 1.0 or 0.92), ((math.sin(a) < 0) and 1.55 or 0.75) * math.sin(a) - 0.35}) end
local PAD = {{-7.21, 4.91}, {-4.99, -3.71}, {-3.55, -7.04}, {6, -7.2}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function lijnd(x, y, p) local best = 1e9
	for i = 1, #p - 1 do local a, b = p[i], p[i + 1]; local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local R = Random.new(1952)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L = {}
for gx = -2.8, 2.8, 0.3 do for gy = -2.65, 0.25, 0.3 do
	local x, y = gx + U(-0.08, 0.08), gy + U(-0.08, 0.08)
	if inside(x, y, RAND) and not inside(x, y, BAK) then local s = {"bloem_roze", "bloem_wit", "bloem_roze", "bloem_rood"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.7, 0.95), 0.3}) end
end end
for _ = 1, 900 do
	local x, y = U(-11, 11), U(-6, 11)
	local vrij = not inside(x, y, PLEIN) and not (math.abs(x) < 4.6 and y > -3.0 and y < 3.4) and lijnd(x, y, PAD) > 2.2 and not (x > 2.5 and y > -1 and y < 10)
	if vrij then
		if R:NextNumber() < 0.35 then local s = {"rododendron0", "rododendron1", "taxus0", "PH_shrub_03_1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2), 0})
		elseif R:NextNumber() < 0.5 then local s = {"varen0", "PH_fern_02_0", "bodem1", "PH_periwinkle_plant_1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.1), 0}) end
	end
end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), workspace:FindFirstChild("HansEnGrietjeGroen"), workspace:FindFirstChild("RodeSchoentjesGroen"), workspace:FindFirstChild("RoodkapjeGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("KleineBoodschapGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "KleineBoodschapGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local n, mis = 0, {}
for _, p in ipairs(L) do
	local t = bron(p[1]); if not t then mis[p[1]] = true; continue end
	local c = t:Clone(); local pos = (ORIGIN * CFrame.new(-p[2] * S, 0, p[3] * S)).Position
	local hit = workspace:Raycast(pos + Vector3.new(0, 30, 0), Vector3.new(0, -60, 0), rp); local y = (hit and hit.Position.Y or 2) + p[5]
	local rot = CFrame.Angles(0, R:NextNumber() * math.pi * 2, 0)
	if c:IsA("Model") then
		if p[4] ~= 1 then c:ScaleTo(c:GetScale() * p[4]) end
		local cf, sz = c:GetBoundingBox(); c:PivotTo(CFrame.new(pos.X, y + (c:GetPivot().Position.Y - (cf.Position.Y - sz.Y / 2)) - 0.15, pos.Z) * rot)
	elseif c:IsA("BasePart") then c.Size = c.Size * p[4]; c.CFrame = CFrame.new(pos.X, y + c.Size.Y / 2 - 0.15, pos.Z) * rot end
	for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") and p[4] < 1.0 then d.CastShadow = false end end
	c.Parent = map; n += 1
end
map.Parent = workspace
local w = game.StarterPlayer.StarterPlayerScripts:FindFirstChild("Wind")
if w and not string.find(w.Source, "KleineBoodschapGroen") then w.Source = string.gsub(w.Source, '"VrouwHolleGroen" }', '"VrouwHolleGroen", "KleineBoodschapGroen" }', 1) end
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
return string.format("%d planten; ontbrekend: %s", n, table.concat(mm, ","))
