-- De Magische Klok: beplanting in workspace.MagischeKlokGroen (wind via StarterPlayerScripts.Wind MAPPEN).
-- Indeling (Herauten-overzicht-okt2009, MagischeKloktotaal, Boekloc): strook langs de noordmuur tot het plein met varens/bodembedekkers,
-- westoever van de gracht licht begroeid (varens, riet), rozen in het perk, varens om de voet van de toren, achter de muren hoge heesters
-- (laurier/rododendron/taxus) die boven de kantelen uitkomen. Grasveld blijft open. Plein (klinkers, muurtje, haag) vrij.
local F = Vector3.new(-0.855, 0, -0.518)
local ORIGIN = CFrame.new(169.32, 2.0, -159.75) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local rng = Random.new(1952)
local ss = game:GetService("ServerStorage")
local V3, ECHT, VV = ss.BomenBronV3, ss.VVEchtePlanten, ss.VVPlanten
local groen = workspace:FindFirstChild("MagischeKlokGroen") or Instance.new("Folder"); groen.Name = "MagischeKlokGroen"; groen.Parent = workspace; groen:ClearAllChildren()
local params = RaycastParams.new(); params.FilterType = Enum.RaycastFilterType.Exclude
params.FilterDescendantsInstances = {groen, workspace.MagischeKlok.Botsing}
local function onder(x, y) local p = lokaal(x, y, 0).Position; return workspace:Raycast(p + Vector3.new(0, 40, 0), Vector3.new(0, -60, 0), params) end
local ARMS = {
	{Vector2.new(-1.33, -2.96) - Vector2.new(0.7149, -0.6997) * 1.2, Vector2.new(-0.6997, -0.7149), Vector2.new(0.7149, -0.6997), 14.45},
	{Vector2.new(0.96, -3.07) - Vector2.new(-0.7154, -0.6986) * 1.2, Vector2.new(0.6986, -0.7154), Vector2.new(-0.7154, -0.6986), 17.25},
}
local function armst(x, y, a) local d = Vector2.new(x, y) - a[1]; return d:Dot(a[2]), d:Dot(a[3]) end   -- s langs de muur, t naar het plein
local PA, PB, PR = Vector2.new(-0.719, -7.198), Vector2.new(-7.016, -13.632), 2.9 + 1.7   -- plein + haag (exports/klok_extra.json)
local function inPlein(x, y)
	local q = Vector2.new(x, y); local ab = PB - PA; local t = math.clamp((q - PA):Dot(ab) / ab:Dot(ab), 0, 1)
	local d = (q - (PA + ab * t)).Magnitude
	if d < 2.9 + 0.3 then return true end                                                                  -- plein + muurtje
	return d < PR and (q - PA):Dot(ARMS[1][3]) > 0                                                         -- haag alleen aan de graskant
end
local function vrijGrond(x, y, r, opPerk)
	if inPlein(x, y) then return false end
	if Vector2.new(x, y).Magnitude < 2.1 + r then return false end                                         -- toren
	for _, a in ipairs(ARMS) do
		local s, t = armst(x, y, a)
		local tmax = (a == ARMS[2]) and 2.45 or 0.95                                                           -- west: muur+sokkels+gracht, noord: muur+sokkels
		if s > -4 and s < a[4] + 0.4 and t > -0.75 - r and t < tmax + r then return false end
	end
	for _, d in ipairs({{0, 0}, {r, 0}, {-r, 0}, {0, r}, {0, -r}}) do
		local hit = onder(x + d[1], y + d[2]); if not hit then return false end
		if opPerk then if not hit.Instance.Name:find("bodem") then return false end elseif hit.Instance ~= workspace.Terrain then return false end
	end
	return true
end
local klein = {}
local function vrij(x, y, r) for _, q in ipairs(klein) do if (q[1] - x) ^ 2 + (q[2] - y) ^ 2 < ((q[3] + r) * 0.7) ^ 2 then return false end end; return true end
local function zet(bronM, x, y, schaal, schaduw, opPerk)
	local c = bronM:Clone(); c:ScaleTo(c:GetScale() * schaal)
	local cf, size = c:GetBoundingBox(); local r = math.max(size.X, size.Z) / S * 0.45
	if not vrij(x, y, r) or not vrijGrond(x, y, r * 0.5, opPerk) then c:Destroy(); return false end
	local h = onder(x, y); local gy = h and h.Position.Y or 2
	c:PivotTo(CFrame.new(Vector3.new(lokaal(x, y, 0).Position.X, gy + size.Y / 2 - 0.15, lokaal(x, y, 0).Position.Z)) * CFrame.Angles(0, rng:NextNumber(0, 6.28), 0) * cf:ToObjectSpace(c:GetPivot()))
	for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") then d.Anchored = true; d.CanCollide = false; d.CanTouch = false; if not schaduw then d.CastShadow = false; d.CanQuery = false end end end
	c.Parent = groen; table.insert(klein, {x, y, r}); return true
end
local function vul(n, gebied, lijst, sMin, sMax, schaduw, pogingen, opPerk)
	local k = 0
	for i = 1, pogingen or n * 30 do
		if k >= n then break end
		local x, y = gebied()
		if x and zet(lijst[rng:NextInteger(1, #lijst)], x, y, rng:NextNumber(sMin, sMax), schaduw, opPerk) then k += 1 end
		if i % 200 == 0 then task.wait() end
	end
	return k
end
local function pick(folder, pat) local t = {}; for _, c in ipairs(folder:GetChildren()) do if c.Name:find(pat) then table.insert(t, c) end end; return t end
local function langs(tMin, tMax)   -- willekeurig punt langs een arm, op afstand t (negatief = achter de muur)
	return function()
		local a = ARMS[rng:NextInteger(1, 2)]; local s = rng:NextNumber(-1.5, a[4] + 1.0); local t = rng:NextNumber(tMin, tMax)
		local p = a[1] + a[2] * s + a[3] * t; return p.X, p.Y
	end
end
local function voorstrook() return rng:NextNumber(-12, 12), rng:NextNumber(-14.5, -2.5) end
local VAREN = pick(ECHT, "fern"); table.insert(VAREN, VV.varen0); table.insert(VAREN, VV.varen1)
local BODEM = pick(ECHT, "periwinkle"); for _, c in ipairs(pick(ECHT, "sorrel")) do table.insert(BODEM, c) end; table.insert(BODEM, VV.bodem0); table.insert(BODEM, VV.bodem1)
local STRUIK = pick(ECHT, "shrub_0")
local function noordstrook(tMin, tMax)
	return function() local a = ARMS[1]; local s = rng:NextNumber(0.6, a[4]); local t = rng:NextNumber(tMin, tMax); local p = a[1] + a[2] * s + a[3] * t; return p.X, p.Y end
end
local function west(tMin, tMax)
	return function() local a = ARMS[2]; local s = rng:NextNumber(1.0, a[4]); local t = rng:NextNumber(tMin, tMax); local p = a[1] + a[2] * s + a[3] * t; return p.X, p.Y end
end
-- 1. strook langs de noordmuur tot het plein: bodembedekkers, varens, enkele lage struiken
local nb = vul(150, noordstrook(1.0, 2.0), BODEM, 1.2, 1.8, false, 6000)
local nv = vul(45, noordstrook(1.0, 2.0), VAREN, 1.5, 2.3, false, 3000)
local ns = vul(10, noordstrook(1.2, 1.9), STRUIK, 1.2, 1.7, false, 1500)
-- 2. westoever van de gracht: varens en wat lage planten, spaarzaam (overzicht-okt2009)
local nw = vul(30, west(2.5, 3.3), VAREN, 1.3, 2.0, false, 2000)
local nw2 = vul(30, west(2.5, 3.2), BODEM, 1.0, 1.5, false, 2000)
-- 3. rozen in het perk
local pc = Vector2.new(4.718, -14.075); local uW = ARMS[2][2]; local nW = ARMS[2][3]
local nr = vul(46, function() local q = pc + uW * rng:NextNumber(-1.9, 1.9) + nW * rng:NextNumber(-0.9, 0.9); return q.X, q.Y end,
	{VV.bloem_rood, VV.bloem_rood, VV.bloem_roze, VV.bloem_wit}, 1.3, 1.6, false, 2000, true)
-- 4. voet van de toren
local function toren() local a = rng:NextNumber(0, math.tau); local r = rng:NextNumber(2.1, 3.0); return r * math.cos(a), r * math.sin(a) end
local nt = vul(22, toren, VAREN, 1.6, 2.4, false, 1500)
-- 5. achter de muren: hoge heesters die boven de kantelen uitkomen
local nh = vul(40, langs(-6.0, -1.2), {V3.rododendron0, V3.rododendron1, V3.taxus0, V3.taxus1, V3.struik0, V3.struik1}, 2.8, 3.8, true, 6000)
local nh2 = vul(10, function() local a = rng:NextNumber(math.rad(20), math.rad(160)); local r = rng:NextNumber(3.5, 7); return r * math.cos(a), r * math.sin(a) end,
	{V3.rododendron0, V3.taxus0, V3.struik1}, 3.0, 3.8, true, 1500)
return string.format("noordstrook %d/%d/%d, gracht %d/%d, rozen %d, toren %d, heesters %d+%d", nb, nv, ns, nw, nw2, nr, nt, nh, nh2)
