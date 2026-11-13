-- Hans en Grietje: beplanting in workspace.HansEnGrietjeGroen (wind doet mee via StarterPlayerScripts.Wind MAPPEN).
-- Voortuin (Hghuis5): perken vol begonia's rood/roze/wit tot de leuning, binnen het binnenhek lage bloemen en grassen.
-- Linkerperk (Boekloc): lage bodembedekkers tussen de potten. Rondom en achter: dicht Sprookjesbos (dennen/beuken/eiken, rododendron, taxus, varens).
-- Planten alleen op MAT_aarde (perken) of op terrein buiten de tuin; nooit op snoeppad, grind, klinkers, muren of hekken.
local F = Vector3.new(-0.944, 0, -0.332)
local ORIGIN = CFrame.new(200.43, 2.0, -82.44) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local rng = Random.new(1955)
local ss = game:GetService("ServerStorage")
local V3, ECHT, VV = ss.BomenBronV3, ss.VVEchtePlanten, ss.VVPlanten
local groen = workspace:FindFirstChild("HansEnGrietjeGroen") or Instance.new("Folder"); groen.Name = "HansEnGrietjeGroen"; groen.Parent = workspace; groen:ClearAllChildren()
local params = RaycastParams.new(); params.FilterType = Enum.RaycastFilterType.Exclude; params.FilterDescendantsInstances = {groen}
local function onder(x, y) local p = lokaal(x, y, 0).Position; return workspace:Raycast(p + Vector3.new(0, 40, 0), Vector3.new(0, -60, 0), params) end
local HUIS = {{-3.7, 1.8, -2.6, 3.0}, {1.2, 3.8, -0.4, 2.6}, {-0.6, 1.6, -2.7, -1.0}, {5.0, 6.8, 0.0, 1.6}, {4.0, 6.8, 0.3, 1.3}}   -- x0, x1, y0, y1 (huis, kooi, trap, oven, houtstapel)
local GROND = 1   -- 1 = alleen perk (MAT_aarde), 2 = alleen terrein
local function vrijGrond(x, y, r, soort)
	for _, h in ipairs(HUIS) do if x > h[1] - r and x < h[2] + r and y > h[3] - r and y < h[4] + r then return false end end
	for _, d in ipairs({{0, 0}, {r, 0}, {-r, 0}, {0, r}, {0, -r}}) do
		local hit = onder(x + d[1], y + d[2]); if not hit then return false end
		local n = hit.Instance.Name
		if soort == 1 and not n:find("MAT_aarde") then return false end
		if soort == 2 and hit.Instance ~= workspace.Terrain then return false end
	end
	return true
end
local klein, stammen = {}, {}
local function vrij(x, y, r, boom)
	for _, q in ipairs(stammen) do if (q[1] - x) ^ 2 + (q[2] - y) ^ 2 < (boom and q[3] or 1.0) ^ 2 then return false end end
	if not boom then for _, q in ipairs(klein) do if (q[1] - x) ^ 2 + (q[2] - y) ^ 2 < ((q[3] + r) * 0.72) ^ 2 then return false end end end
	return true
end
local function zet(bronM, x, y, schaal, soort, boomAfst)
	local c = bronM:Clone(); c:ScaleTo(c:GetScale() * schaal)
	local cf, size = c:GetBoundingBox()
	local r = math.max(size.X, size.Z) / S * 0.45
	if not vrij(x, y, r, boomAfst ~= nil) or not vrijGrond(x, y, boomAfst and 0.8 or r * 0.55, soort) then c:Destroy(); return false end
	local h = onder(x, y); local gy = h and h.Position.Y or 2
	c:PivotTo(CFrame.new(Vector3.new(lokaal(x, y, 0).Position.X, gy + size.Y / 2 - 0.12, lokaal(x, y, 0).Position.Z)) * CFrame.Angles(0, rng:NextNumber(0, 6.28), 0) * cf:ToObjectSpace(c:GetPivot()))
	for _, d in ipairs(c:GetDescendants()) do
		if d:IsA("BasePart") then d.Anchored = true; d.CanCollide = false; d.CanTouch = false; if size.Y < 12 then d.CastShadow = false; d.CanQuery = false end end
	end
	c.Parent = groen
	if boomAfst then table.insert(stammen, {x, y, boomAfst}) else table.insert(klein, {x, y, r}) end
	return true
end
local function vul(n, x0, x1, y0, y1, lijst, sMin, sMax, soort, boomAfst, filter, pogingen)
	local k = 0
	for i = 1, pogingen or n * 25 do
		if k >= n then break end
		local x, y = rng:NextNumber(x0, x1), rng:NextNumber(y0, y1)
		if (not filter or filter(x, y)) and zet(lijst[rng:NextInteger(1, #lijst)], x, y, rng:NextNumber(sMin, sMax), soort, boomAfst) then k += 1 end
		if i % 250 == 0 then task.wait() end
	end
	return k
end
local function pick(folder, pat) local t = {}; for _, c in ipairs(folder:GetChildren()) do if c.Name:find(pat) then table.insert(t, c) end end; return t end
-- 1. voortuin: begonia's (meest rood, dan roze en wit) dicht tot aan de leuning
local BEGONIA = {VV.bloem_rood, VV.bloem_rood, VV.bloem_rood, VV.bloem_roze, VV.bloem_roze, VV.bloem_wit}
local nb = vul(520, -6.5, 3.6, -11.0, -4.9, BEGONIA, 1.15, 1.45, 1, nil, nil, 9000)
-- 2. binnen het binnenhek (Hghuis-vk): roze bloemen, siergras, varentjes
local nbin = vul(70, -4.2, 3.4, -4.6, -1.3, {VV.bloem_roze, VV.bloem_wit, VV.siergras0, VV.siergras1, VV.varen0}, 1.0, 1.35, 1, nil, nil, 2500)
-- 3. linkerperk tussen de potten (Boekloc): lage bodembedekkers en wat oranje bloemetjes
local LAAG = pick(ECHT, "periwinkle"); for _, c in ipairs(pick(ECHT, "ursinia")) do table.insert(LAAG, c) end; table.insert(LAAG, VV.bodem0); table.insert(LAAG, VV.bodem1)
local nl = vul(110, -10.3, -4.0, -10.3, 0.4, LAAG, 1.2, 1.8, 1, nil, function(x, y) return x < -6.2 or y > -4.9 end, 4000)
-- 4. dicht bos rondom tot ~25 m, ook tussen en langs de paden (Daan: meer bebossen). Paden/tuin vallen af via de grondtest (alleen terrein).
local function bos(x, y)
	if y < -4.4 and y > -11.3 and x > -10.9 and x < 4.4 then return false end   -- voortuin open
	return true
end
local nd = vul(18, -26, 26, -26, 24, {V3.den0, V3.den1}, 2.7, 3.5, 2, 3.2, function(x, y) return bos(x, y) and (y > 4 or x > 7 or x < -8 or y < -14) end, 3000)
local nloof = vul(24, -28, 28, -28, 26, {V3.beuk0, V3.beuk1, V3.eik0, V3.eik1, V3.kastanje0, V3.kastanje1, V3.berk0, V3.berk1}, 2.8, 3.4, 2, 4.2, function(x, y) return bos(x, y) and (y > 5 or x > 8 or x < -9 or y < -14.5) end, 3000)
local nr = vul(95, -24, 24, -24, 20, {V3.rododendron0, V3.rododendron1, V3.taxus0, V3.taxus1, V3.struik0, V3.struik1}, 2.2, 3.1, 2, nil, bos, 9000)
local ONDER = pick(ECHT, "fern"); for _, p in ipairs({"shrub_02", "shrub_03", "shrub_04", "sorrel"}) do for _, c in ipairs(pick(ECHT, p)) do table.insert(ONDER, c) end end
if #ONDER == 0 then ONDER = {VV.varen0, VV.varen1} end
local no = vul(260, -24, 24, -24, 20, ONDER, 2.4, 3.6, 2, nil, bos, 14000)
local nv = vul(130, -22, 22, -22, 18, {VV.varen0, VV.varen1}, 1.4, 2.2, 2, nil, bos, 7000)
return string.format("begonia %d, binnen %d, linkerperk %d, dennen %d, loof %d, heesters %d, ondergroei %d, varens %d", nb, nbin, nl, nd, nloof, nr, no, nv)
