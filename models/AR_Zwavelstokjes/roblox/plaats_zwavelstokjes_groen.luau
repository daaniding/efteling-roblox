-- Het Meisje met de Zwavelstokjes: groen zoals op Meisjezij/Zwavelstokjes4b: gras/riet langs het vijvertje, varens en heesters voor de keermuur,
-- rododendrons bij de trap en de oprit, bomen rondom (achter en naast het stadje, niet ervoor). Kloont bestaande sjablonen (BomenBronV3,
-- VVEchtePlanten/VVPlanten, HerautenpleinGroen). Modelframe als plaats_zwavelstokjes.luau.
local F = Vector3.new(-0.233, 0, -0.972)
local ORIGIN = CFrame.new(120.36, 2.0, -466.71) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local VIJ = {{-1.88, -3.8}, {-2.22, -7.12}, {-3.35, -10.07}, {-5.32, -11.15}, {-8.64, -11.08}, {-10.49, -10.44}, {-10.72, -8.82}, {-8.75, -8.16}, {-5.78, -7.49}, {-4.32, -5.39}, {-3.59, -3.8}}
local HEUVEL = {{-12.6, -1.4}, {-10.4, -5.4}, {-6.9, -3.45}, {3.3, -3.45}, {3.3, -4.35}, {8.25, -4.35}, {8.25, 1.2}, {10.2, 1.2}, {10.2, 6.6}, {-8.3, 6.6}, {-8.3, -0.6}}
local PADEN = {{{-1.4, -4.45}, {12.0, -4.45}, {12.0, -11.4}, {-1.4, -11.4}}, {{-17.0, -11.4}, {12.0, -11.4}, {12.0, -14.5}, {-17.0, -14.5}},
	{{-17.0, -11.4}, {-11.0, -11.4}, {-11.0, -6.2}, {-13.4, -3.0}, {-17.0, -3.0}}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function segd(x, y, p) local best = 1e9; local n = #p
	for i = 1, n do local a, b = p[i], p[(i % n) + 1]
		local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function oppad(x, y) for _, p in ipairs(PADEN) do if inside(x, y, p) then return true end end; return false end
local R = Random.new(1845)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L = {}
-- 1) gras/riet en asters langs het water (buiten het water, niet op het pad)
for _ = 1, 2500 do
	local x, y = U(-12, 0), U(-12.5, -3)
	local d = segd(x, y, VIJ)
	if not inside(x, y, VIJ) and d < 1.0 and not oppad(x, y) and R:NextNumber() < 0.45 then
		local s = {"PH_grass_bermuda_01", "riet", "gras", "PH_fern_02_2", "bloem_paars"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.9, 1.4)}) end
end
-- 2) varens en heesters voor de keermuur (strook tussen muur en vijver/pad) en bovenop de heuvel voor de gevel
for _ = 1, 1500 do
	local x, y = U(-12, 8.5), U(-6, -2.8)
	local voor = not inside(x, y, HEUVEL) and segd(x, y, HEUVEL) < 1.2
	local top = inside(x, y, HEUVEL) and y < -2.85 and y > -3.4
	if (voor or top) and not inside(x, y, VIJ) and not oppad(x, y) and R:NextNumber() < 0.5 then
		local s = top and {"PH_fern_02_0", "varen1", "PH_grass_bermuda_01"} or {"PH_fern_02_0", "PH_fern_02_3", "varen1", "PH_shrub_02_3", "struik0"}
		table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.85, 1.3)}) end
end
-- 3) rododendrons bij de trap en naast de oprit (Meisjezij rechts, Boekloc)
for _, c in ipairs({{7.6, -4.9}, {10.6, -3.4}, {10.8, -1.2}, {-12.3, -6.0}, {-14.6, -2.6}, {-9.6, -6.3}}) do
	for _ = 1, 3 do local x, y = c[1] + U(-0.7, 0.7), c[2] + U(-0.7, 0.7)
		if not oppad(x, y) and not inside(x, y, VIJ) then local s = {"rododendron0", "rododendron1", "taxus0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.15)}) end end
end
-- 4) bomen rondom: naast en achter het stadje (niet in het zicht vanaf het pad voor de gevel)
local bomen = {}
for _ = 1, 3000 do
	local x, y = U(-24, 22), U(-14, 18)
	local vrij = not inside(x, y, HEUVEL) and segd(x, y, HEUVEL) > 2.2 and not inside(x, y, VIJ) and segd(x, y, VIJ) > 1.5 and not oppad(x, y)
	local zicht = y < -3 and x > -12 and x < 12
	if vrij and not zicht then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 10 then ok = false; break end end
		if ok and #bomen < 40 then table.insert(bomen, {x, y}); local s = {"eik0", "eik0", "beuk0", "beuk1", "berk0", "den0", "kastanje0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.85, 1.15)}) end
	end
end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), game.ServerStorage:FindFirstChild("VVPlanten"), workspace:FindFirstChild("HerautenpleinGroen"), workspace:FindFirstChild("HansEnGrietjeGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("ZwavelstokjesGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "ZwavelstokjesGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include
local grond = {workspace.Terrain}                                                   -- alleen op terrein, heuvel en paden (niet op daken/torens)
for _, p in ipairs(workspace.ZwavelstokjesStadje:GetChildren()) do if p:IsA("BasePart") and (string.find(p.Name, "MAT_grond") or string.find(p.Name, "MAT_klinker")) then table.insert(grond, p) end end
rp.FilterDescendantsInstances = grond
local VRIJ = {{-10.96, -3.28, 2.2}, {-12.4, -4.2, 1.6}, {8.9, 1.5, 1.6}, {8.9, -0.5, 1.4}}   -- poort, oprit, uitgang, trap vrijhouden
local n, mis = 0, {}
for i, p in ipairs(L) do
	local blok = false; for _, v in ipairs(VRIJ) do if (p[2] - v[1]) ^ 2 + (p[3] - v[2]) ^ 2 < v[3] ^ 2 then blok = true end end
	if blok then continue end
	local t = bron(p[1])
	if not t then mis[p[1]] = true; continue end
	local c = t:Clone()
	local pos = (ORIGIN * CFrame.new(-p[2] * S, 0, p[3] * S)).Position
	local hit = workspace:Raycast(pos + Vector3.new(0, 25, 0), Vector3.new(0, -50, 0), rp)
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
