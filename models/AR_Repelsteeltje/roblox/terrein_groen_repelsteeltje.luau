-- Repelsteeltje: terrein (golvende bosgrond, huisje op een lage verhoging, pad vlak) + groen (lemma: "slingerend pad tussen het jonge groen";
-- foto's: rododendrons, varens en klimop rond het huisje, hoge bomen erachter). Modelframe als plaats_repelsteeltje.luau.
local F = Vector3.new(0.533, 0, -0.846)
local ORIGIN = CFrame.new(351.75, 2.0, -425.94) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local HUIS = {{-2.6, -2.15}, {3.75, -2.15}, {3.75, 2.45}, {-2.6, 2.45}}
local PAD = {{-14.0, -4.0}, {-3.5, -3.7}, {11.0, -3.6}, {11.0, -6.9}, {-3.5, -7.0}, {-9.0, -8.6}, {-14.0, -9.0}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function segd(x, y, p) local best = 1e9; local n = #p
	for i = 1, n do local a, b = p[i], p[(i % n) + 1]
		local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function glad(t) t = math.clamp(t, 0, 1); return t * t * (3 - 2 * t) end
-- 1) terrein
local T = workspace.Terrain; local nT = 0
for gx = -20, 20, 4 / S do
	for gy = -12, 18, 4 / S do
		local wpos = (ORIGIN * CFrame.new(-gx * S, 0, gy * S)).Position
		local X, Z = math.floor(wpos.X / 4) * 4 + 2, math.floor(wpos.Z / 4) * 4 + 2
		local l = ORIGIN:PointToObjectSpace(Vector3.new(X, 0, Z)); local x, y = -l.X / S, l.Z / S
		if inside(x, y, HUIS) then continue end
		local h = 0.3 + 0.32 * math.noise(x / 6.5, y / 6.5, 2.3) + 0.18 * math.noise(x / 2.8, y / 2.8, 7.1)
		h = math.max(h, 0.25 * glad(1 - segd(x, y, HUIS) / 3))                       -- huisje staat op een lage verhoging
		local dp = inside(x, y, PAD) and 0 or segd(x, y, PAD); h = h * glad(dp / 2.0)   -- pad vlak, vloeiende rand
		if y < -2.2 and y > -3.8 and x > -3 and x < 4.5 then h = math.min(h, 0.12) end  -- tuintje voor het kijkvenster laag
		if h > 0.04 then
			local top = 2 + h * S
			T:FillBlock(CFrame.new(X, (top - 6) / 2, Z), Vector3.new(4, top + 6, 4), segd(x, y, HUIS) < 2.5 and Enum.Material.Ground or Enum.Material.LeafyGrass); nT += 1
		end
	end
	task.wait()
end
-- 1b) rond het huisje en voor de deur exact op maaiveld (laag 0..4 leeg = oppervlak Y 2; opgehoogd terrein bedekte de onderkant van de deur)
local vlak = {}
for gx = -8, 9, 0.6 do for gy = -5, 6, 0.6 do
	if segd(gx, gy, HUIS) < 1.4 or (gx < -2.3 and gx > -6.0 and gy > -2.0 and gy < 2.2) then
		local p = (ORIGIN * CFrame.new(-gx * S, 0, gy * S)).Position; vlak[math.floor(p.X / 4) .. "," .. math.floor(p.Z / 4)] = true end end end
for k in pairs(vlak) do local i, j = string.match(k, "(-?%d+),(-?%d+)"); T:FillBlock(CFrame.new(tonumber(i) * 4 + 2, 6, tonumber(j) * 4 + 2), Vector3.new(4, 12, 4), Enum.Material.Air) end
-- 1c) onder het pad geen grassprieten: Grass/LeafyGrass -> Ground
for x = -15, 12, 0.7 do for y = -10, -3, 0.7 do
	if inside(x, y, PAD) then local p = (ORIGIN * CFrame.new(-x * S, 0, y * S)).Position; local X, Z = math.floor(p.X / 4) * 4, math.floor(p.Z / 4) * 4
		for _, mt in ipairs({Enum.Material.Grass, Enum.Material.LeafyGrass}) do T:ReplaceMaterial(Region3.new(Vector3.new(X - 4, -8, Z - 4), Vector3.new(X + 8, 8, Z + 8)):ExpandToGrid(4), 4, mt, Enum.Material.Ground) end end end end
-- 2) groen
local R = Random.new(1812)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L = {}
for _ = 1, 1800 do                                                                      -- heesters, varens, rododendrons rond het huisje (niet op het pad, niet voor het venster)
	local x, y = U(-9, 10), U(-3.6, 9)
	local d = segd(x, y, HUIS)
	local venster = (y < -1.9 and x > -2.6 and x < 3.9) or (x < -2.3 and x > -6.5 and y > -3.6 and y < 2.6)   -- venstertuin en deurgevel vrij
	if not inside(x, y, HUIS) and d > 0.25 and d < 4.5 and not inside(x, y, PAD) and not venster and R:NextNumber() < 0.35 then
		local s = d < 1.3 and {"PH_fern_02_0", "PH_fern_02_3", "varen1", "PH_shrub_02_3"} or {"rododendron0", "rododendron1", "struik0", "struik1", "taxus0", "PH_shrub_03_1", "PH_fern_02_2"}
		table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2)}) end
end
for _ = 1, 900 do                                                                       -- jong groen langs het slingerende pad (aan de overkant)
	local x, y = U(-14, 11), U(-11, -6.9)
	if not inside(x, y, PAD) and segd(x, y, PAD) < 2.5 and R:NextNumber() < 0.3 then
		local s = {"struik0", "struik1", "PH_shrub_03_1", "PH_fern_02_0", "rododendron0", "bloem_paars"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2)}) end
end
local bomen = {}
for _ = 1, 2500 do                                                                      -- hoge bomen achter en naast het huisje
	local x, y = U(-20, 20), U(-12, 18)
	local vrij = not inside(x, y, HUIS) and segd(x, y, HUIS) > 3 and not inside(x, y, PAD) and segd(x, y, PAD) > 1.5
	local zicht = y < -1 and y > -12 and x > -6 and x < 9
	if vrij and not zicht then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 12 then ok = false; break end end
		if ok and #bomen < 26 then table.insert(bomen, {x, y}); local s = {"den0", "den1", "eik0", "beuk0", "berk0", "kastanje0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.9, 1.2)}) end
	end
end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), game.ServerStorage:FindFirstChild("VVPlanten"), workspace:FindFirstChild("HerautenpleinGroen"), workspace:FindFirstChild("HansEnGrietjeGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("RepelsteeltjeGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "RepelsteeltjeGroen"
local grond = {workspace.Terrain}
local hm = workspace:FindFirstChild("RepelsteeltjeHuisje")
if hm then for _, p in ipairs(hm:GetChildren()) do if p:IsA("BasePart") and string.find(p.Name, "MAT_flagstone") then table.insert(grond, p) end end end
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = grond
local n, mis = 0, {}
for i, p in ipairs(L) do
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
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
return string.format("terrein %d cellen; %d planten (%d bomen); ontbrekend: %s", nT, n, #bomen, table.concat(mm, ","))
