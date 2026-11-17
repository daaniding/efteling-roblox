--!strict
-- PagodeBezoekers (ServerScriptService): NPC-bezoekers die blijven leven (Daan 17 nov, laag 1 + "ze blijven gewoon bezoekers,
-- spawnen niet zomaar, gaan daarna naar een andere attractie; bij elke attractie komen er nieuwe bij").
-- Rij: iedereen heeft een plek op de looplijn, recht achter zijn voorganger; de rij vult van voren naar achteren en schuift
-- op als er ruimte is (Daan 17 nov: "een wachtrij vullen dan de ander, recht erin staan", "het stoppen om te draaien is irritant").
-- Levensloop: rij (exports/bezoekersroute.json via maak_bezoekers.py: aanloop, laantje, onderpad, zigzag baan voor baan,
-- trapkop, tourniquets, bordes, gangetje) -> eigen plek op het dek -> meerijden -> uitstappen via uit0 en de uitgangstrap ->
-- door het park naar de volgende attractie (nu alleen de Pagode: een ommetje en weer achter in de rij).
-- Er komen nieuwe bezoekers bij tot er MAX_BEZOEKERS rondlopen; niemand verdwijnt meer.
-- Meerijden: de gondel beweegt alleen op de clients (PagodeRitClient). De server zet een meerijder vast (HumanoidRootPart
-- verankerd, attribuut Rijdt) op zijn plek op de stilstaande servergondel; elke client neemt hem dan mee met zijn gondel.
-- Botsen niet met spelers (groep Bezoekers vs Spelers); door poortjes en onzichtbare routemuren lopen ze heen (ze volgen de route).
local Players = game:GetService("Players")
local PhysicsService = game:GetService("PhysicsService")
local ServerStorage = game:GetService("ServerStorage")

local S = 3
local CX, CY = 360.0, 47.5
local Z_I, Z_P = 1.3, -0.38
local ROUTE: {{number}} = {{367.26,76.61,-0.38},{363.06,69.29,-0.38},{361.14,63.86,-0.38},{358.57,63.84,-0.38},{356.01,62.58,-0.38},{355.07,63.87,-0.38},{354.20,65.17,-0.38},{353.26,66.44,-0.38},{352.25,67.66,-0.38},{351.18,68.85,-0.38},{350.04,69.99,-0.38},{347.89,70.28,-0.38},{344.12,67.83,-0.38},{340.83,64.76,-0.38},{338.12,61.17,-0.38},{338.49,60.43,-0.35},{338.26,60.05,-0.35},{338.05,59.67,-0.35},{337.84,59.29,-0.35},{337.64,58.90,-0.35},{337.44,58.51,-0.35},{339.24,57.63,-0.20},{340.19,59.38,-0.20},{341.24,60.98,-0.20},{342.41,62.48,-0.20},{343.71,63.87,-0.20},{345.11,65.16,-0.20},{346.62,66.33,-0.20},{347.78,64.70,0.10},{346.41,63.64,0.10},{345.14,62.48,0.10},{343.96,61.22,0.10},{342.90,59.86,0.10},{341.95,58.42,0.10},{341.12,56.91,0.10},{342.90,56.02,0.40},{343.73,57.51,0.40},{344.63,58.84,0.40},{345.64,60.09,0.40},{346.75,61.25,0.40},{347.95,62.32,0.40},{349.23,63.28,0.40},{350.36,61.62,0.70},{349.22,60.78,0.70},{348.16,59.84,0.70},{347.18,58.82,0.70},{346.29,57.72,0.70},{345.49,56.55,0.70},{344.79,55.31,0.70},{346.57,54.40,1.00},{347.23,55.56,1.00},{347.92,56.56,1.00},{348.69,57.51,1.00},{349.53,58.38,1.00},{350.44,59.19,1.00},{351.41,59.92,1.00},{352.61,60.56,1.15},{353.56,60.60,1.30},{354.04,59.62,1.30},{353.67,58.39,1.30},{352.37,57.27,1.30},{352.28,56.16,1.30},{353.61,54.67,1.30},{355.08,53.02,1.30}}
local MAX_BEZOEKERS = 14
local SPELER_SNELHEID = 6.5                      -- spelers lopen even snel als de bezoekers (5.5-7.5)
local TUSSENPOOS = {6, 12}                       -- seconden tussen nieuwe bezoekers (tot MAX_BEZOEKERS)
local ANIM = {loop = "rbxassetid://913402848", stil = "rbxassetid://507766388"}   -- standaard R15 lopen / stilstaan

-- ritklok: gelijk aan PagodeRitClient (instappen T_IN, sluiten 5, omhoog 35, boven 70, omlaag 35)
local T_IN, CYCLUS = 60, 60 + 5 + 35 + 70 + 35
local A_UIT0 = 0 - 15.5615                       -- uitstappoortje uit0 (poorten.py: park = alfa - DRAAI)
local A_IN0 = 9 * 360 / 22 - 15.5615             -- instappoortje in0 (131.71)
local A_TRAP = -20.0                             -- uitgangstrap (12_omgeving A_UIT)

local function pp(r: number, a: number, z: number): {number}
	return {CX + r * math.cos(math.rad(a)), CY + r * math.sin(math.rad(a)), z}
end
-- uitstappen: van de dekplek naar het poortje uit0, over de vlonder naar de trap, trap af, het pad op
local UIT: {{number}} = {pp(7.2, A_UIT0, Z_I), pp(9.6, A_UIT0, Z_I), pp(10.25, A_UIT0, Z_I), pp(10.25, A_TRAP, Z_I),
	pp(11.6, A_TRAP, 0.75), pp(13.2, A_TRAP, 0.0), pp(14.6, A_TRAP, Z_P)}
-- ommetje door het park terug naar het begin van de aanloop (later: naar een andere attractie)
local OMMETJE: {{number}} = {pp(18.0, -8.0, Z_P), pp(23.0, 20.0, Z_P), pp(28.0, 48.0, Z_P), pp(31.0, 66.0, Z_P)}

local pag = workspace:WaitForChild("Pagode") :: Model
for _, g in {"Bezoekers", "Spelers", "Rijdend", "Routemuur", "Poortdeel"} do
	if not PhysicsService:IsCollisionGroupRegistered(g) then PhysicsService:RegisterCollisionGroup(g) end
end
PhysicsService:CollisionGroupSetCollidable("Bezoekers", "Spelers", false)
PhysicsService:CollisionGroupSetCollidable("Bezoekers", "Rijdend", false)
PhysicsService:CollisionGroupSetCollidable("Bezoekers", "Bezoekers", false)
PhysicsService:CollisionGroupSetCollidable("Bezoekers", "Routemuur", false)
PhysicsService:CollisionGroupSetCollidable("Bezoekers", "Poortdeel", false)
PhysicsService:CollisionGroupSetCollidable("Poortdeel", "Rijdend", true)
for _, p in pag:GetDescendants() do
	if p:IsA("BasePart") and (p.Name == "poortreling" or p.Name == "poortblad") and p.CollisionGroup == "Default" then p.CollisionGroup = "Poortdeel" end
end
-- eenrichtingsschotten (tourniquet, kop uitgangstrap) gelden voor spelers, niet voor bezoekers
local eenrichting = pag:FindFirstChild("Eenrichting")
if eenrichting then for _, p in eenrichting:GetDescendants() do if p:IsA("BasePart") and p.CollisionGroup == "Default" then p.CollisionGroup = "Poortdeel" end end end

-- dekvloer alleen voor bezoekers: de gondel zelf blijft op de server in de bouwstand (de clients laten hem rijden; de
-- servergondel verplaatsen gaf een losse arm als de client hem half-verplaatst inlas, Daan 17 nov). Onzichtbare schijf op
-- instaphoogte (NAP 11.3) in het station, botst alleen met groep Bezoekers.
if not PhysicsService:IsCollisionGroupRegistered("Bezoekersvloer") then PhysicsService:RegisterCollisionGroup("Bezoekersvloer") end
for _, g in PhysicsService:GetRegisteredCollisionGroups() do
	if g.name ~= "Bezoekersvloer" then PhysicsService:CollisionGroupSetCollidable("Bezoekersvloer", g.name, g.name == "Bezoekers") end
end
do
	local oud = workspace:FindFirstChild("PagodeBezoekersDek"); if oud then oud:Destroy() end
	local d = Instance.new("Part"); d.Name = "PagodeBezoekersDek"; d.Shape = Enum.PartType.Cylinder
	d.Size = Vector3.new(1, 8.3 * 2 * S, 8.3 * 2 * S); d.Anchored = true; d.Transparency = 1; d.CanQuery = false; d.CanTouch = false
	d.CastShadow = false; d.CollisionGroup = "Bezoekersvloer"
	d.CFrame = CFrame.new(CX * S, 2 + Z_I * S - 0.5, -CY * S) * CFrame.Angles(0, 0, math.rad(90))
	d.Parent = workspace
end

local function wereld(p: {number}): Vector3
	return Vector3.new(p[1] * S, 2 + p[3] * S + 3, -p[2] * S)
end

local map = workspace:FindFirstChild("PagodeBezoekersActief") or Instance.new("Folder")
map.Name = "PagodeBezoekersActief"; map.Parent = workspace

type Bezoeker = {model: Model, hum: Humanoid, s: number, nr: number, fase: string}
local rij: {Bezoeker} = {}
local teller = 0

local function tc(): number
	local start = pag:GetAttribute("RitStart") :: number?
	if not start then return 0 end
	return (workspace:GetServerTimeNow() - start) % CYCLUS
end
-- hekjes open: instappen; de eerste en laatste 2-3 s gaan ze open/dicht
local function hekjesOpen(): boolean
	local t = tc()
	return t > 2 and t < T_IN - 3
end

local function sjablonen(): {Model}
	local bron = ServerStorage:FindFirstChild("PagodeBezoekers")
	local lijst = {}
	if bron then for _, m in bron:GetChildren() do if m:IsA("Model") and m:FindFirstChildOfClass("Humanoid") then table.insert(lijst, m) end end end
	return lijst
end

local function animeer(hum: Humanoid)
	local animator = hum:FindFirstChildOfClass("Animator") or Instance.new("Animator", hum)
	local function laad(id: string)
		local a = Instance.new("Animation"); a.AnimationId = id
		return (animator :: Animator):LoadAnimation(a)
	end
	local loop, stil = laad(ANIM.loop), laad(ANIM.stil)
	stil.Looped = true; loop.Looped = true; stil:Play()
	hum.Running:Connect(function(v)
		if v > 0.5 then
			if not loop.IsPlaying then stil:Stop(0.3); loop:Play(0.3) end
			loop:AdjustSpeed(v / 8)
		elseif loop.IsPlaying then loop:Stop(0.3); stil:Play(0.3) end
	end)
end

-- looplijnen: polylijn in studs met afgelegde lengte, zodat iedereen een plek OP de lijn heeft (s = afstand vanaf het begin)
type Lijn = {p: {Vector3}, l: {number}, L: number}
local function lijn(pts: {Vector3}): Lijn
	local l = {0}
	for i = 2, #pts do l[i] = l[i - 1] + Vector3.new(pts[i].X - pts[i - 1].X, 0, pts[i].Z - pts[i - 1].Z).Magnitude end
	return {p = pts, l = l, L = l[#pts]}
end
local function opLijn(ln: Lijn, s: number): Vector3
	s = math.clamp(s, 0, ln.L)
	for i = 2, #ln.p do
		if s <= ln.l[i] then
			local t = (s - ln.l[i - 1]) / math.max(ln.l[i] - ln.l[i - 1], 1e-6)
			return ln.p[i - 1]:Lerp(ln.p[i], t)
		end
	end
	return ln.p[#ln.p]
end
-- dichtstbijzijnde s rond de huidige (venster: een baan verderop ligt maar 2 m naast je, maar 10+ m verder op de lijn)
local function projecteer(ln: Lijn, pos: Vector3, s0: number): number
	local best, bestD = s0, math.huge
	for i = 2, #ln.p do
		if ln.l[i] >= s0 - 3 and ln.l[i - 1] <= s0 + 8 then
			local a, b = ln.p[i - 1], ln.p[i]
			local ab = Vector2.new(b.X - a.X, b.Z - a.Z); local ap = Vector2.new(pos.X - a.X, pos.Z - a.Z)
			local len2 = ab:Dot(ab)
			local t = if len2 > 0 then math.clamp(ap:Dot(ab) / len2, 0, 1) else 0
			local s = ln.l[i - 1] + t * (ln.l[i] - ln.l[i - 1])
			local d = (ap - ab * t).Magnitude
			if d < bestD and s >= s0 - 3 and s <= s0 + 8 then best, bestD = s, d end
		end
	end
	return best
end
local RIJ_S = (function()
	local pts = {}
	for i = 1, #ROUTE - 3 do pts[i] = wereld(ROUTE[i]) end      -- tot de splitsing op het bordes (r 12.4, 128 gr)
	return lijn(pts)
end)()
local GAT = 0.85 * S              -- hart op hart in de rij: recht achter elkaar
local OPSCHUIVEN = 2.2 * S        -- pas opschuiven als er zoveel ruimte is (niet bij elke centimeter)
local VOORUIT = 4                 -- studs vooruit mikken: vloeiend door de bochten, niet stoppen op elk punt

-- een lijn aflopen; grens() = tot waar je nu mag (in de rij: tot achter je voorganger)
local function volg(b: Bezoeker, ln: Lijn, grens: () -> number, klaar: () -> boolean)
	local m, hum = b.model, b.hum
	local staat = false
	while m.Parent do
		local h = m:FindFirstChild("HumanoidRootPart") :: BasePart?
		if not h then return end
		b.s = math.max(b.s, projecteer(ln, h.Position, b.s))
		if klaar() then return end
		local g = math.min(grens(), ln.L)
		local ruimte = g - b.s
		if staat then staat = ruimte < OPSCHUIVEN and not (g >= ln.L and ruimte > 0.6) else staat = ruimte < 0.6 end
		if staat then hum:Move(Vector3.zero) else hum:MoveTo(opLijn(ln, math.min(b.s + VOORUIT, g))) end
		task.wait(0.1)
	end
end

-- wie staat direct voor je in dezelfde rij (rij, gang1, gang2): verder op de lijn (gelijk: wie eerder aansloot)
local function voorganger(b: Bezoeker): Bezoeker?
	local voor: Bezoeker? = nil
	for _, o in rij do
		if o ~= b and o.fase == b.fase and o.model.Parent and (o.s > b.s or (o.s == b.s and o.nr < b.nr)) then
			if voor == nil or o.s < voor.s or (o.s == voor.s and o.nr > voor.nr) then voor = o end
		end
	end
	return voor
end
-- laatste in een gangetje (om te kiezen waar je aansluit)
local function staart(fase: string): (number, number)
	local n, laagste = 0, math.huge
	for _, o in rij do if o.fase == fase and o.model.Parent then n += 1; laagste = math.min(laagste, o.s) end end
	return n, laagste
end

local function zetVast(b: Bezoeker, vast: boolean)
	local h = b.model:FindFirstChild("HumanoidRootPart") :: BasePart?
	if h then h.Anchored = vast end
	if not vast then   -- na het verankeren geeft Roblox het eigenaarschap aan de dichtstbijzijnde speler: terugpakken
		for _, d in b.model:GetDescendants() do if d:IsA("BasePart") then pcall(function() d:SetNetworkOwner(nil) end) end end
	end
	b.model:SetAttribute("Rijdt", vast)
end

local function vrijLopen(b: Bezoeker, pts: {{number}})
	local h = b.model:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not h then return end
	local w = {h.Position}
	for _, q in pts do table.insert(w, wereld(q)) end
	local ln = lijn(w)
	b.s = 0
	volg(b, ln, function() return ln.L end, function() return b.s > ln.L - 1.5 end)
end

-- over het dek altijd met een boog om de kern heen (rechtdoor = door de kern en op de zitrand blijven hangen)
local function boog(a0: number, a1: number, r: number): {{number}}
	local d = (a1 - a0 + 180) % 360 - 180
	local pts = {}
	local n = math.max(1, math.ceil(math.abs(d) / 12))
	for k = 1, n do table.insert(pts, pp(r, a0 + d * k / n, Z_I)) end
	return pts
end
local function hoekNu(b: Bezoeker): number
	local h = b.model:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not h then return 0 end
	return math.deg(math.atan2(-h.Position.Z / S - CY, h.Position.X / S - CX))
end

-- twee gangetjes vanaf de splitsing op het bordes (Daan: "ze gebruiken de tweede ingang niet"); in1 via een boog buiten
-- het hekje van in0 om (die hekjes lopen tot r 12.6)
local A_IN1 = 10 * 360 / 22 - 15.5615            -- 148.07
local A_UIT1 = -360 / 22 - 15.5615               -- -31.93
local SPLITS = ROUTE[#ROUTE - 3]
local GANG = {
	{poort = A_IN0, ln = lijn({wereld(SPLITS), wereld(pp(11.6, A_IN0, Z_I)), wereld(pp(9.6, A_IN0, Z_I))})},
	{poort = A_IN1, ln = lijn({wereld(SPLITS), wereld(pp(13.1, A_IN0, Z_I)), wereld(pp(13.1, 140, Z_I)), wereld(pp(12.9, A_IN1, Z_I)),
		wereld(pp(11.6, A_IN1, Z_I)), wereld(pp(9.6, A_IN1, Z_I))})},
}
-- plekken aan de reling rondom de hele gondel, elk 1 bezoeker (Daan: "verspreid dat meer"); niet in de poortjes
local PLEKKEN: {{a: number, b: Bezoeker?}} = {}
for k = 0, 39 do
	local a = k * 9 + 4.5 - 180
	local vrij = true
	for _, pa in {A_IN0, A_IN1, A_UIT0, A_UIT1} do if math.abs((a - pa + 180) % 360 - 180) < 6 then vrij = false end end
	if vrij then table.insert(PLEKKEN, {a = a}) end
end

local function rijEnRit(b: Bezoeker)
	local m, hum = b.model, b.hum
	-- 1 de rij tot de splitsing op het bordes: recht op de lijn, vult van voren naar achteren
	b.fase = "rij"; b.s = 0
	local keus = 1
	volg(b, RIJ_S, function()
		local voor = voorganger(b)
		return if voor then voor.s - GAT else RIJ_S.L
	end, function()
		if b.s < RIJ_S.L - 1.5 or voorganger(b) ~= nil then return false end
		-- vooraan: naar het gangetje met de minste mensen, als daar achteraan plek is
		local n1, s1 = staart("gang1"); local n2, s2 = staart("gang2")
		keus = if n2 < n1 then 2 else 1
		local laagste = if keus == 1 then s1 else s2
		return laagste > GAT + 1
	end)
	if not m.Parent then return end
	-- 2 het gangetje in tot het poortje; instappen als het dek ruim voor het sluiten gehaald wordt
	local gang = GANG[keus]
	b.fase = "gang" .. keus; b.s = 0
	volg(b, gang.ln, function()
		local voor = voorganger(b)
		return if voor then voor.s - GAT else gang.ln.L
	end, function()
		local t = tc()
		return b.s > gang.ln.L - 1.5 and voorganger(b) == nil and t > 2 and t < T_IN - 8
	end)
	if not m.Parent then return end
	-- 3 over het dek naar een vrije plek aan de reling (willekeurig rondom), naar buiten kijken
	b.fase = "dek"; m:SetAttribute("OpDek", true)
	local vrije = {}
	for _, p in PLEKKEN do if p.b == nil or not p.b.model.Parent or p.b.fase ~= "dek" and p.b.fase ~= "rit" then p.b = nil; table.insert(vrije, p) end end
	local plek = if #vrije > 0 then vrije[math.random(#vrije)] else PLEKKEN[math.random(#PLEKKEN)]
	plek.b = b
	local naarPlek = {pp(7.4, gang.poort, Z_I)}
	for _, q in boog(gang.poort, plek.a, 7.4) do table.insert(naarPlek, q) end
	table.insert(naarPlek, pp(7.3 + math.random() * 0.4, plek.a, Z_I))
	vrijLopen(b, naarPlek)
	hum:Move(Vector3.zero)
	task.wait(0.6)
	local hh = m:FindFirstChild("HumanoidRootPart") :: BasePart?
	if hh then
		local uit = Vector3.new(hh.Position.X - CX * S, 0, hh.Position.Z + CY * S).Unit
		hum.AutoRotate = false
		hh.CFrame = CFrame.lookAt(hh.Position, hh.Position + uit)
	end
	while m.Parent and tc() < T_IN do task.wait(0.25) end
	zetVast(b, true)                                               -- vast op de servergondel; de clients nemen hem mee
	b.fase = "rit"
	while m.Parent and tc() >= T_IN do task.wait(0.25) end      -- sluiten, omhoog, boven, omlaag
	while m.Parent and not hekjesOpen() do task.wait(0.25) end
	if not m.Parent then return end
	zetVast(b, false); m:SetAttribute("OpDek", false)
	hum.AutoRotate = true
	-- 4 uitstappen via het dichtstbijzijnde uitstappoortje en de uitgangstrap, ommetje, weer achter in de rij
	b.fase = "uit"; plek.b = nil
	task.wait(math.random() * 4)
	local a = hoekNu(b)
	local poort = if math.abs((a - A_UIT0 + 180) % 360 - 180) <= math.abs((a - A_UIT1 + 180) % 360 - 180) then A_UIT0 else A_UIT1
	local uitweg = boog(a, poort, 7.3)
	for _, q in {pp(9.6, poort, Z_I), pp(10.25, poort, Z_I)} do table.insert(uitweg, q) end
	for k = 4, #UIT do table.insert(uitweg, UIT[k]) end
	vrijLopen(b, uitweg)
	b.fase = "park"
	vrijLopen(b, OMMETJE)
	if m.Parent then hum:Move(Vector3.zero); task.wait(5 + math.random() * 25) end      -- even rondkijken
	vrijLopen(b, {ROUTE[1]})
end

local function nieuw()
	local lijst = sjablonen()
	if #lijst == 0 then return end
	local m = lijst[math.random(#lijst)]:Clone()
	local hum = m:FindFirstChildOfClass("Humanoid") :: Humanoid
	if not hum then m:Destroy(); return end
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then d.Anchored = false; d.CollisionGroup = "Bezoekers"; d.CanTouch = false end
		if d:IsA("Script") or d:IsA("LocalScript") then d:Destroy() end
	end
	hum.WalkSpeed = 5.5 + math.random() * 2
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	m:PivotTo(CFrame.new(wereld(ROUTE[1])))
	m.Parent = map
	for _, d in m:GetDescendants() do if d:IsA("BasePart") then pcall(function() d:SetNetworkOwner(nil) end) end end
	animeer(hum)
	teller += 1
	local b: Bezoeker = {model = m, hum = hum, s = 0, nr = teller, fase = "rij"}
	table.insert(rij, b)
	task.spawn(function()
		while m.Parent do
			rijEnRit(b)
			teller += 1; b.nr = teller          -- weer achter in de rij aansluiten
		end
	end)
end

-- spelers in hun eigen botsgroep (bezoekers lopen er doorheen; PagodeRitClient wisselt tussen Spelers en Rijdend)
local function speler(plr: Player)
	plr.CharacterAdded:Connect(function(ch)
		task.wait(0.5)
		for _, d in ch:GetDescendants() do if d:IsA("BasePart") then d.CollisionGroup = "Spelers" end end
		local h = ch:FindFirstChildOfClass("Humanoid")
		if h then h.WalkSpeed = SPELER_SNELHEID end      -- Daan: "laat mij even snel lopen als zij"
		ch.DescendantAdded:Connect(function(d) if d:IsA("BasePart") then d.CollisionGroup = "Spelers" end end)
	end)
end
for _, p in Players:GetPlayers() do speler(p) end
Players.PlayerAdded:Connect(speler)

while true do
	for k = #rij, 1, -1 do if not rij[k].model.Parent then table.remove(rij, k) end end
	if #rij < MAX_BEZOEKERS then nieuw() end
	task.wait(TUSSENPOOS[1] + math.random() * (TUSSENPOOS[2] - TUSSENPOOS[1]))
end
