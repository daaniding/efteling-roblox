-- De Magische Klok: bos eromheen in workspace.MagischeKlokBos (foto's: hoge beuken/eiken boven de muren en het plein, schaduw, ondergroei).
-- Grote loofbomen (schaal 4-5.5 = 20-28 m) achter de muren en langs de randen van het pleinvierkant, nooit op muur/gracht/plein/grasveld/pad;
-- heesters (rododendron/taxus/hulst-achtig) aan de randen zodat het vierkant besloten is; varens en bodembedekkers onder de bomen.
local F = Vector3.new(-0.855, 0, -0.518)
local ORIGIN = CFrame.new(169.32, 2.0, -159.75) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local rng = Random.new(1955)
local ss = game:GetService("ServerStorage")
local V3, ECHT, VV = ss.BomenBronV3, ss.VVEchtePlanten, ss.VVPlanten
local bos = workspace:FindFirstChild("MagischeKlokBos") or Instance.new("Folder"); bos.Name = "MagischeKlokBos"; bos.Parent = workspace; bos:ClearAllChildren()
local params = RaycastParams.new(); params.FilterType = Enum.RaycastFilterType.Exclude
params.FilterDescendantsInstances = {bos, workspace.MagischeKlok.Botsing, workspace:FindFirstChild("MagischeKlokGroen")}
local function onder(x, y) local p = lokaal(x, y, 0).Position; return workspace:Raycast(p + Vector3.new(0, 120, 0), Vector3.new(0, -160, 0), params) end
local ARMS = {
	{Vector2.new(-1.33, -2.96) - Vector2.new(0.7149, -0.6997) * 1.2, Vector2.new(-0.6997, -0.7149), Vector2.new(0.7149, -0.6997), 14.45},
	{Vector2.new(0.96, -3.07) - Vector2.new(-0.7154, -0.6986) * 1.2, Vector2.new(0.6986, -0.7154), Vector2.new(-0.7154, -0.6986), 17.25},
}
local PAD = {Vector2.new(-18.67, -33.94), Vector2.new(-9.13, -24.32), Vector2.new(0.65, -14.48), Vector2.new(13.54, -27.2)}   -- OSM 1169014962
local PA, PB = Vector2.new(-0.719, -7.198), Vector2.new(-7.016, -13.632)
local function segd(q, a, b) local ab = b - a; local t = math.clamp((q - a):Dot(ab) / ab:Dot(ab), 0, 1); return (q - (a + ab * t)).Magnitude end
local function padAfst(q) local d = 1e9; for i = 1, #PAD - 1 do d = math.min(d, segd(q, PAD[i], PAD[i + 1])) end; return d end
local function binnenVierkant(q)   -- tussen de muren en het pad (plein, grasveld, gracht)
	local tN = (q - ARMS[1][1]):Dot(ARMS[1][3]); local tW = (q - ARMS[2][1]):Dot(ARMS[2][3])
	local sN = (q - ARMS[1][1]):Dot(ARMS[1][2]); local sW = (q - ARMS[2][1]):Dot(ARMS[2][2])
	if tN < -0.2 or tW < -0.2 then return false end
	local Pm = PAD[3]; local inner = (q - Pm):Dot((Vector2.new(0, 0) - Pm).Unit) > -0.5   -- aan de torenkant van de V
	return inner and (sN < ARMS[1][4] + 3 or sW < ARMS[2][4] + 3)
end
local function vrij(q, r, boom)
	if q.Magnitude < 3.5 then return false end
	if binnenVierkant(q) then return false end
	if padAfst(q) < (boom and 2.8 or 1.6) then return false end
	local sN, tN = (q - ARMS[1][1]):Dot(ARMS[1][2]), (q - ARMS[1][1]):Dot(ARMS[1][3]); local sW, tW = (q - ARMS[2][1]):Dot(ARMS[2][2]), (q - ARMS[2][1]):Dot(ARMS[2][3])
	if (tN > 2.2 and tN < 9.5 and sN < 13.5 and tW > 2.3) or (tW > 2.4 and tW < 9.5 and sW < 11 and tN > 2.2) then return false end   -- plein v3 + haag
	for _, a in ipairs(ARMS) do
		local s = (q - a[1]):Dot(a[2]); local t = (q - a[1]):Dot(a[3])
		if s > -4 and s < a[4] + 1 and t > -(boom and 2.2 or 1.2) and t < 0.2 then return false end   -- direct achter de muur (gang/mechaniek)
	end
	local hit = onder(q.X, q.Y); return hit and hit.Instance == workspace.Terrain
end
local geplaatst = {}
local function zet(bron, q, schaal, schaduw, afst)
	local groot = schaal > 2.5 and afst > 5
	for _, g in ipairs(geplaatst) do
		local nodig = (groot and g[3]) and math.max(afst, g[2]) or (g[3] and 1.6) or (groot and 1.6) or math.max(afst, g[2])
		if (g[1] - q).Magnitude < nodig then return false end
	end
	if not vrij(q, afst, schaal > 2.5) then return false end
	local c = bron:Clone(); c:ScaleTo(c:GetScale() * schaal)
	local cf, size = c:GetBoundingBox(); local hit = onder(q.X, q.Y); local gy = hit and hit.Position.Y or 2
	c:PivotTo(CFrame.new(Vector3.new(lokaal(q.X, q.Y, 0).Position.X, gy + size.Y / 2 - 0.3, lokaal(q.X, q.Y, 0).Position.Z)) * CFrame.Angles(0, rng:NextNumber(0, 6.28), 0) * cf:ToObjectSpace(c:GetPivot()))
	for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") then d.Anchored = true; d.CanCollide = false; d.CanTouch = false; if not schaduw then d.CastShadow = false; d.CanQuery = false end end end
	c.Parent = bos; table.insert(geplaatst, {q, afst, groot}); return true
end
local function vul(n, rMin, rMax, lijst, sMin, sMax, schaduw, afst, pogingen)
	local k = 0
	for i = 1, pogingen do
		if k >= n then break end
		local a = rng:NextNumber(0, math.tau); local r = rng:NextNumber(rMin, rMax)
		if zet(lijst[rng:NextInteger(1, #lijst)], Vector2.new(r * math.cos(a), r * math.sin(a)), rng:NextNumber(sMin, sMax), schaduw, afst) then k += 1 end
		if i % 150 == 0 then task.wait() end
	end
	return k
end
local function pick(folder, pat) local t = {}; for _, c in ipairs(folder:GetChildren()) do if c.Name:find(pat) then table.insert(t, c) end end; return t end
local LOOF = {V3.beuk0, V3.beuk1, V3.beuk0, V3.eik0, V3.eik1, V3.kastanje0, V3.kastanje1}
-- 1. bosreuzen: eerst dichtbij (boven de muren uit), dan verder weg
local b1 = vul(10, 5, 13, LOOF, 4.2, 5.4, true, 7.5, 3000)
local b2 = vul(16, 13, 28, LOOF, 3.8, 5.0, true, 8.5, 4000)
local b3 = vul(4, 8, 26, {V3.berk0, V3.berk1, V3.den0}, 3.2, 4.0, true, 7, 1500)
-- 2. heesters aan de randen (besloten vierkant, zoals de foto's)
local h = vul(45, 6, 24, {V3.rododendron0, V3.rododendron1, V3.taxus0, V3.taxus1}, 2.2, 3.4, true, 2.6, 6000)   -- geen 'struik': kale sprieten
-- 3. ondergroei onder de bomen
local VAREN = pick(ECHT, "fern"); table.insert(VAREN, VV.varen0); table.insert(VAREN, VV.varen1)
local BODEM = pick(ECHT, "periwinkle"); for _, c in ipairs(pick(ECHT, "shrub_0")) do table.insert(BODEM, c) end; table.insert(BODEM, VV.bodem0)
local v = vul(110, 4, 24, VAREN, 1.6, 2.6, false, 1.1, 6000)
local o = vul(90, 4, 24, BODEM, 1.3, 2.0, false, 1.0, 5000)
-- 4. rand aan de buitenkant van het pad (sluit de blik naar het lege park af); Prinsenpoort-plek vrij (komt later)
local PRINSC = Vector2.new(-16.5, -17.0)
for i = 1, 4000 do
	local seg = rng:NextInteger(1, 3); local a, b = PAD[seg], PAD[seg + 1]
	local dir = (b - a).Unit; local nrm = Vector2.new(-dir.Y, dir.X); if nrm:Dot(Vector2.new(0, 0) - a) > 0 then nrm = -nrm end
	local boom = rng:NextNumber() < 0.18
	local q = a:Lerp(b, rng:NextNumber()) + nrm * rng:NextNumber(boom and 4 or 1.8, boom and 9 or 5)
	if (q - PRINSC).Magnitude > 7 then
		zet(boom and LOOF[rng:NextInteger(1, #LOOF)] or ({V3.rododendron0, V3.rododendron1, V3.taxus0})[rng:NextInteger(1, 3)], q,
			boom and rng:NextNumber(3.8, 5.0) or rng:NextNumber(2.3, 3.4), true, boom and 7 or 2.2)
	end
	if i % 200 == 0 then task.wait() end
end
-- plein: grijs grind (Cobblestone is in deze place overschreven door de rode visgraatklinkers)
for _, p in ipairs(workspace.MagischeKlok:GetChildren()) do if p:IsA("BasePart") and p.Name:find("MAT_klinker") then p.Material = Enum.Material.Pebble; p.MaterialVariant = ""; p.Color = Color3.fromRGB(158, 152, 142) end end
-- grasveld: LeafyGrass (natuurlijker dan het strakke VV_Gazon)
local T = workspace.Terrain
for x = -15, 17, 1.3 do for y = -22, 4, 1.3 do
	local p = lokaal(x, y, 0).Position
	T:ReplaceMaterial(Region3.new(Vector3.new(p.X - 2, -4, p.Z - 2), Vector3.new(p.X + 2, 4, p.Z + 2)):ExpandToGrid(4), 4, Enum.Material.Grass, Enum.Material.LeafyGrass)
end end
return string.format("bomen %d+%d+%d, heesters %d, varens %d, bodem %d", b1, b2, b3, h, v, o)
