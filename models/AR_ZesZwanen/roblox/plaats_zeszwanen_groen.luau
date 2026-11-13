-- De Zes Zwanen: bos rond de open plek, ondergroei, asters langs het water, varens bij de rotsen (zelfde regels als roblox/maak_groen.py)
local F = Vector3.new(0.1076, 0, 0.9942)
local ORIGIN = CFrame.new(-108.77, 2.0, -301.0) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local VIJ = {{{-5.47,-3.96},{-6.33,-5.8},{-5.74,-7.56},{-6.2,-9.15},{-5.23,-10.76},{-5.78,-12.03},{-6.19,-13.01},{-7.39,-13.66},{-7.82,-15.28},{-7.84,-16.83},{-6.61,-16.58},{-5.17,-15.7},{-3.85,-13.81},{-2.89,-13.55},{-0.95,-13.14},{-0.87,-12.52},{1.88,-12.9},{1.83,-13.24},{4.07,-13.27},{6.05,-12.52},{7.65,-11.13},{8.63,-9.39},{9.13,-7.56},{9.18,-6.41},{9.23,-5.5},{8.76,-3.33},{7.84,-1.54},{7.1,0.31},{5.53,-2.45},{1.84,-2.46},{0.53,-3.49},{0.76,-3.82},{-0.68,-5.16},{-1.88,-5.43},{-3.13,-5.09}},{{-1.6,-20.6},{0.67,-22.64},{2.51,-22.21},{3.89,-22.42},{5.5,-22.25},{6.76,-21.77},{8.09,-21.12},{9.75,-19.65},{11.57,-18.83},{12.7,-18.79},{13.75,-18.16},{13.68,-17.21},{12.75,-17.12},{12.14,-16.32},{10.99,-15.72},{9.4,-15.88},{6.98,-16.36},{3.31,-18.17},{0.76,-18.96}},{{13.53,0.46},{13.8,1.33},{14.54,2},{15.93,2.52},{17.93,2.3},{19.4,1.51},{20.22,0.08},{20.71,-1.05},{19.97,-2.11},{19.46,-3.02},{18.36,-3.02},{17.78,-1.94},{17.81,-0.66},{16.72,0.1},{15.96,0.21},{14.92,-0.59},{13.85,-0.42}}}
local PAD = {{-3.83,-14.63},{-4.84,-16.7},{-5.27,-19.85},{-5.45,-23.25},{-4.18,-26.33},{-2.45,-26.3},{-0.56,-25.34},{-1.33,-23.53},{-1.6,-20.6},{0.76,-18.96},{3.31,-18.17},{6.98,-16.36},{9.4,-15.88},{11.93,-13.94},{12.86,-10.41},{13.35,-9.36},{14.51,-8.08},{15.63,-7.57},{14.56,-4.84},{14.92,-0.59},{13.85,-0.42},{13.53,0.46},{11.55,4.59},{10.16,6.33},{4.22,6.57},{3.81,5.47},{2.97,4.14},{3.96,3.13},{5.55,3.02},{6.41,1.58},{6.98,0.63},{7.1,0.31},{7.84,-1.54},{8.76,-3.33},{9.23,-5.5},{9.18,-6.41},{11.93,-6.66},{11.72,-7.53},{11.52,-8.43},{10.81,-10.04},{9.88,-11.72},{8.33,-13.52},{6.41,-14.26},{4.71,-14.71},{3.17,-14.88},{2.91,-16.65},{-1.02,-16.44},{-2.12,-17.32}}
local KAS = {{1.68,-2.53},{1,-1.57},{1.37,-1.31},{2.29,-2.42},{5.54,-2.43},{7.1,0.31},{6.98,0.63},{6.41,1.58},{5.55,3.02},{3.96,3.13},{2.97,4.14},{3.81,5.47},{4.22,6.57},{1.63,7.77},{-2,4.83},{-3.71,6.86},{-8.27,3.23},{-6.62,1.19},{-6.8,-0.31},{-6.62,-1.42},{-6.2,-2.53},{-5.36,-3.6},{-4.4,-4.3},{-3.17,-4.81},{-1.87,-5.37},{-0.49,-4.29},{-0.22,-4.55},{0.71,-3.78},{0.5,-3.49}}
local VOET = {{{10.59,-13.04},{6.79,-15.49},{3.02,-17.39},{-1.79,-18.41},{-2.92,-21.13},{-3.22,-22.59},{-2.69,-24.45},{-4.09,-24.81},{-4.88,-22.9},{-4.6,-20.46},{-4,-18.93},{-2.9,-17.13},{-1.17,-15.65},{2.28,-15.9},{2.57,-13.95},{4.64,-13.96},{6.11,-13.46},{7.94,-12.35},{9.05,-10.9},{9.97,-9.11},{10.3,-7.39},{11.72,-7.53},{12.73,-7.58}},{{12.98,-4.78},{10.81,0.48},{7.99,3.8}},{{14.56,-4.84},{12.98,-4.78},{12.73,-7.58},{12.17,-10.18},{10.59,-13.04}},{{11.93,-13.94},{10.59,-13.04}},{{14.56,-4.84},{19.66,-4.49},{26.59,-4.83}}}
local ROTS = {{{0.76,-5.5},{1.6,-4.55},{3.35,-4.37},{4.17,-5.16},{4.98,-5.21},{5.43,-6.02},{4.36,-6.78},{4.37,-7.82},{3.25,-8.52},{1.33,-7.62},{0.94,-6.72}},{{-6.38,-3.51},{-5.47,-3.96},{-6.33,-5.8},{-5.74,-7.56},{-6.2,-9.15},{-5.23,-10.76},{-5.78,-12.03},{-6.69,-11.93},{-7.65,-11.04},{-8.06,-8.23},{-8.01,-4.62},{-7.23,-3.53}}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function segd(x, y, p, ring) local best = 1e9; local n = #p
	for i = 1, (ring and n or n - 1) do local a, b = p[i], p[(i % n) + 1]
		local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = dx * dx + dy * dy; if L2 == 0 then L2 = 1e-9 end
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function dwater(x, y) local d = 1e9; local inn = false
	for _, v in ipairs(VIJ) do d = math.min(d, segd(x, y, v, true)); if inside(x, y, v) then inn = true end end
	return inn and -d or d end
local function dpad(x, y) if inside(x, y, PAD) then return -1 end
	local d = segd(x, y, PAD, true); for _, f in ipairs(VOET) do d = math.min(d, segd(x, y, f, false) - 0.95) end; return d end
local function inrots(x, y) for _, r in ipairs(ROTS) do if inside(x, y, r) then return true end end; return false end
local function vrij(x, y, mw, mp, mk) return dwater(x, y) > mw and dpad(x, y) > mp and not inside(x, y, KAS) and segd(x, y, KAS, true) > mk and not inrots(x, y) end
local R = Random.new(2019)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L = {}
local bomen = {}
for _ = 1, 6000 do
	local x, y = U(-15, 24), U(-31, 12)
	local voor = y > -22 and y < 2 and x > -9 and x < 14
	if not voor and vrij(x, y, 2.5, 1.8, 2.5) then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 9 then ok = false; break end end
		if ok then table.insert(bomen, {x, y}); local s = {"den0", "den0", "den1", "den1", "beuk0", "beuk1", "kastanje0", "eik0", "eik0", "berk0"}
			table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.85, 1.15)}) end
	end
end
for _ = 1, 2500 do
	local x, y = U(-15, 24), U(-31, 12)
	if vrij(x, y, 1.2, 0.6, 1.0) and dpad(x, y) < 5.5 and R:NextNumber() < 0.35 then
		local s = {"rododendron0", "rododendron1", "taxus0", "taxus1", "struik0", "struik1", "PH_shrub_03_1", "PH_shrub_02_3"}
		table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2)}) end
end
for _ = 1, 9000 do
	local x, y = U(-15, 24), U(-31, 12); local dw = dwater(x, y)
	if dw > 0.25 and dw < 1.6 and dpad(x, y) > 0.25 and not inside(x, y, KAS) and segd(x, y, KAS, true) > 0.6 and not inrots(x, y) and R:NextNumber() < 0.35 then
		table.insert(L, {"bloem_paars", x, y, U(0.9, 1.3)}) end
end
for _, r in ipairs({ROTS[1], ROTS[2], KAS}) do
	for _ = 1, 400 do
		local x, y = U(-12, 12), U(-18, 8); local d = segd(x, y, r, true)
		if d > 0.1 and d < 1.2 and dwater(x, y) > 0.2 and dpad(x, y) > 0.3 and not inside(x, y, KAS) and R:NextNumber() < 0.55 then
			local s = {"PH_fern_02_0", "PH_fern_02_2", "PH_fern_02_3", "varen1"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.9, 1.3)}) end
	end
end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), game.ServerStorage:FindFirstChild("VVPlanten"), workspace:FindFirstChild("HerautenpleinGroen"), workspace:FindFirstChild("HansEnGrietjeGroen")}) do
		if f and f:FindFirstChild(naam) then t = f:FindFirstChild(naam); break end end end
	return t
end
local oud = workspace:FindFirstChild("ZesZwanenGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "ZesZwanenGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include
rp.FilterDescendantsInstances = {workspace.Terrain, workspace:FindFirstChild("ZesZwanenOmgeving")}
local n, mis = 0, {}
for i, p in ipairs(L) do
	local t = bron(p[1])
	if not t then mis[p[1]] = true; continue end
	local c = t:Clone()
	local pos = (ORIGIN * CFrame.new(-p[2] * S, 0, p[3] * S)).Position
	local hit = workspace:Raycast(pos + Vector3.new(0, 20, 0), Vector3.new(0, -40, 0), rp)
	local y = hit and hit.Position.Y or 2
	local rot = CFrame.Angles(0, R:NextNumber() * math.pi * 2, 0)
	if c:IsA("Model") then
		if p[4] ~= 1 then c:ScaleTo(c:GetScale() * p[4]) end
		local cf, sz = c:GetBoundingBox(); local onder = cf.Position.Y - sz.Y / 2
		c:PivotTo(CFrame.new(pos.X, y + (c:GetPivot().Position.Y - onder), pos.Z) * rot)
	elseif c:IsA("BasePart") then
		c.Size = c.Size * p[4]; c.CFrame = CFrame.new(pos.X, y + c.Size.Y / 2, pos.Z) * rot
	end
	c.Parent = map; n += 1
	if i % 150 == 0 then task.wait() end
end
map.Parent = workspace
local m = {}; for k in pairs(mis) do table.insert(m, k) end
return string.format("%d planten (%d bomen); ontbrekend: %s", n, #bomen, table.concat(m, ","))
