--!strict
-- SiroccoBezoekers (ServerScriptService): NPC-bezoekers bij de Sirocco (Daan 18 nov: "voeg de mensen toe, ze moeten instappen en
-- allemaal een eigen karretje kiezen aan het begin al"; "wat doen we als er meer mensen zijn dan karretjes").
-- Levensloop: rij (07_omgeving.WACHTRIJ t/m de boog bij -62 graden, dan het instapstuk tot voor de instappoort) -> zodra het
-- instappen begint kiest wie vooraan staat een eigen vrije boot (gereserveerd, iedereen een andere), loopt erheen en gaat zitten
-- -> rijdt mee (Seat: de client neemt hem mee met de boot, net als een speler) -> uitstappen: uit de boot, door de uitstapopening,
-- over de brug naar het plein -> Park.naarVolgende (rondgang door het park, ParkBezoekers.VOLGORDE).
-- Meer mensen dan boten: niemand loopt terug; wie geen boot heeft blijft vooraan in de rij voor de dichte poort staan en gaat
-- de volgende ronde mee (zo werkt het in het park ook). Neemt een speler de gekozen boot, dan kiest de bezoeker een andere;
-- is er geen meer vrij, dan gaat hij weer vooraan in de rij staan.
-- Klok en fasen gelijk aan SiroccoRit (instappen T_IN, rit T_RIT, uitstappen T_UIT). Poorten en schotten zijn voor bezoekers
-- geen obstakel (groep Poortdeel): op de server staan ze altijd in de rustand, alleen de clients laten ze bewegen.
local PhysicsService = game:GetService("PhysicsService")
local PathfindingService = game:GetService("PathfindingService")
local SSS = game:GetService("ServerScriptService")
local Park = require(SSS:WaitForChild("ParkBezoekers")) :: any

local S = 3
local T_IN, T_RIT, T_UIT = 15, 60, 16         -- = SiroccoRit
local CYCLUS = T_IN + T_RIT + T_UIT
local MAX_BEZOEKERS = 16                       -- 12 boten + een paar die op de volgende ronde wachten
local SP = 0.85 * S                            -- afstand hart op hart in de rij
local Z_DEK, Z_PLEIN = 0.3, 0.27
local INSTAP_TOT = T_IN - 2                    -- = einde van het wachtvenster van SiroccoRit (IN_HOUD + 1): tot dan mag je naar een boot
-- SiroccoRit wacht op de bezoekers (Daan 18 nov: "hij mag pas beginnen als elke npc een plekje heeft, tenzij er geen meer over is,
-- en de uitgangsdeuren mogen pas dicht als elke npc weg is"): attributen op Rit, elke 0,2 s bijgewerkt
--   NpcInstap = er loopt nog iemand naar een boot, of er staat iemand in de rij terwijl er een boot vrij is
--   NpcUit    = aantal uitstappers dat nog niet voorbij het begin van de brug is
local VERTREK = 0.35                           -- s tussen twee bezoekers die naar hun boot gaan

local sir = workspace:WaitForChild("Sirocco") :: Model
local rit = sir:WaitForChild("Rit") :: Model
local MIDDEN = rit:GetAttribute("Midden") :: Vector3
local function W(x: number, y: number, z: number?): Vector3 return MIDDEN + Vector3.new(x * S, (z or Z_DEK) * S, -y * S) end
local function pol(r: number, a: number, z: number?): Vector3 return W(r * math.cos(math.rad(a)), r * math.sin(math.rad(a)), z) end

-- botsgroepen (zoals PagodeBezoekers): poortbladen en schotten zijn voor bezoekers geen obstakel
for _, g in {"Bezoekers", "Spelers", "Poortdeel"} do
	if not PhysicsService:IsCollisionGroupRegistered(g) then PhysicsService:RegisterCollisionGroup(g) end
end
PhysicsService:CollisionGroupSetCollidable("Bezoekers", "Poortdeel", false)
local om = sir:WaitForChild("Omgeving")
for _, p in om:GetChildren() do if p:IsA("BasePart") and p.Name:match("^SI_poort_") then p.CollisionGroup = "Poortdeel" end end
local afs = sir:FindFirstChild("RitAfsluiting")
if afs then for _, p in afs:GetChildren() do if p:IsA("BasePart") then p.CollisionGroup = "Poortdeel" end end end

-- ===== looplijn van de rij (omgeving_info.json "wachtrij" t/m index 29 = -61,7 graden op de boog, dan radiaal naar de poort) =====
local RIJ_M = {{5.8, -15.8}, {8.0, -13.9}, {11.0, -11.9}, {13.8, -9.6}, {15.6, -6.5}, {15.9, -2.0}, {15.9, 3.0}, {15.75, 6.0},
	{15.75, 8.0}, {15.52, 9.28}, {14.87, 10.41}, {13.88, 11.25}, {12.65, 11.69}, {11.35, 11.69}, {10.12, 11.25}, {9.13, 10.41},
	{8.48, 9.28}, {8.25, 8.0}, {8.88, 5.12}, {9.53, 3.78}, {9.97, 2.36}, {10.21, 0.89}, {10.23, -0.6}, {10.04, -2.07},
	{9.63, -3.51}, {9.02, -4.86}, {8.22, -6.12}, {7.25, -7.25}, {6.12, -8.22}, {4.86, -9.02}}
local lijn: {Vector3} = {}
for i, p in RIJ_M do table.insert(lijn, W(p[1], p[2], i == 1 and Z_PLEIN or Z_DEK)) end
table.insert(lijn, pol(9.45, -62)); table.insert(lijn, pol(8.95, -62))      -- instapstuk; vooraan = net voor de poort (r 8,55)
local cum: {number} = {0}
for i = 2, #lijn do cum[i] = cum[i - 1] + (Vector3.new(lijn[i].X - lijn[i - 1].X, 0, lijn[i].Z - lijn[i - 1].Z)).Magnitude end
local L_TOT = cum[#cum]
local function op(s: number): Vector3
	s = math.clamp(s, 0, L_TOT)
	for i = 2, #lijn do
		if s <= cum[i] then
			local t = (s - cum[i - 1]) / math.max(1e-6, cum[i] - cum[i - 1])
			return lijn[i - 1]:Lerp(lijn[i], t)
		end
	end
	return lijn[#lijn]
end

-- naar binnen: door de poort en de opening in het gaashek; naar buiten: opening -106, dek, uitstappoort, brug, plein
local IN_ROUTE = {pol(8.2, -62), pol(7.6, -62), pol(6.4, -64)}      -- laatste punt: vrij op de schijf (getoetst, alle boten bereikbaar)
local UIT_ROUTE = {pol(7.6, -106), pol(8.0, -101), W(-2.0, -8.4), W(-2.0, -12.0), W(-2.0, -16.8), W(-2.0, -19.5, Z_PLEIN)}

-- ===== stoelen en boten =====
local stoelen: {Seat} = {}
for _, p in rit:GetChildren() do if p:IsA("Seat") then table.insert(stoelen, p) end end
local gereserveerd: {[Seat]: boolean} = {}
local function bootVan(st: Seat): string return st.Name:match("_rt(%a+)$") :: string end
local function midden(st: Seat): Vector3 return rit:GetAttribute("P_" .. bootVan(st)) :: Vector3 end
local function vrijeStoel(): Seat?
	local vrij = {}
	for _, st in stoelen do if not st.Occupant and not gereserveerd[st] then table.insert(vrij, st) end end
	if #vrij == 0 then return nil end
	return vrij[math.random(#vrij)]
end
-- ===== looproutes op de draaischijf: A* op een raster van 0,25 m. Roblox-pathfinding werkt met cellen van 4 studs (1,33 m)
-- en vindt de gangetjes tussen de boten niet (Daan 18 nov: "ze lopen er niet goed uit"). Obstakels: boten in de rustand
-- (cirkel BOOT_R), de tonnen in het midden, de rand van de schijf; AGENT = halve breedte van een bezoeker. =====
local CEL, RMAX = 0.25, 7.0
local NC = math.ceil(2 * RMAX / CEL)
local BOOT_R, AGENT = 1.2, 0.35
local function celXY(i: number, j: number): (number, number) return -RMAX + (i + 0.5) * CEL, -RMAX + (j + 0.5) * CEL end
local function celVan(x: number, y: number): (number, number) return math.floor((x + RMAX) / CEL), math.floor((y + RMAX) / CEL) end
local function modelVan(p: Vector3): (number, number) return (p.X - MIDDEN.X) / S, -(p.Z - MIDDEN.Z) / S end
local obst: {{number}} = {{0, 0, 0.55}, {0.85, 0.3, 0.35}, {-0.5, 0.75, 0.32}}      -- tonnen (03_forms.platform)
for _, st in stoelen do local x, y = modelVan(midden(st)); table.insert(obst, {x, y, BOOT_R}) end
local vrijCel: {boolean} = {}
for i = 0, NC - 1 do
	for j = 0, NC - 1 do
		local x, y = celXY(i, j)
		local ok = math.sqrt(x * x + y * y) < RMAX - 0.3
		if ok then for _, o in obst do if (x - o[1]) ^ 2 + (y - o[2]) ^ 2 < (o[3] + AGENT) ^ 2 then ok = false; break end end end
		vrijCel[i * NC + j + 1] = ok
	end
end
local function isVrij(i: number, j: number): boolean return i >= 0 and j >= 0 and i < NC and j < NC and vrijCel[i * NC + j + 1] end
local function dichtstVrij(x: number, y: number): (number, number)
	local ci, cj = celVan(x, y)
	for r = 0, 16 do
		local best, bi, bj = math.huge, -1, -1
		for i = ci - r, ci + r do
			for j = cj - r, cj + r do
				if math.max(math.abs(i - ci), math.abs(j - cj)) == r and isVrij(i, j) then
					local cx, cy = celXY(i, j)
					local d = (cx - x) ^ 2 + (cy - y) ^ 2
					if d < best then best, bi, bj = d, i, j end
				end
			end
		end
		if bi >= 0 then return bi, bj end
	end
	return ci, cj
end
local function zicht(ax: number, ay: number, bx: number, by: number): boolean
	local n = math.max(1, math.ceil(math.sqrt((bx - ax) ^ 2 + (by - ay) ^ 2) / (CEL * 0.5)))
	for k = 0, n do
		local t = k / n
		local i, j = celVan(ax + (bx - ax) * t, ay + (by - ay) * t)
		if not isVrij(i, j) then return false end
	end
	return true
end
-- route (wereldpunten, ingekort tot rechte stukken) van model (ax, ay) naar (bx, by); nil als er geen is
local function route(ax: number, ay: number, bx: number, by: number): {Vector3}?
	local si, sj = dichtstVrij(ax, ay)
	local gi, gj = dichtstVrij(bx, by)
	local start, doel = si * NC + sj, gi * NC + gj
	local g: {[number]: number} = {[start] = 0}
	local van: {[number]: number} = {}
	local dicht: {[number]: boolean} = {}
	local heap: {{number}} = {{0, start}}
	local function push(f: number, k: number)
		table.insert(heap, {f, k})
		local c = #heap
		while c > 1 do
			local p = c // 2
			if heap[p][1] <= heap[c][1] then break end
			heap[p], heap[c] = heap[c], heap[p]; c = p
		end
	end
	local function pop(): number
		local top = heap[1]
		local last = table.remove(heap) :: {number}
		if #heap > 0 then
			heap[1] = last
			local c = 1
			while true do
				local l, r, m = 2 * c, 2 * c + 1, c
				if l <= #heap and heap[l][1] < heap[m][1] then m = l end
				if r <= #heap and heap[r][1] < heap[m][1] then m = r end
				if m == c then break end
				heap[m], heap[c] = heap[c], heap[m]; c = m
			end
		end
		return top[2]
	end
	local gevonden = false
	while #heap > 0 do
		local k = pop()
		if k == doel then gevonden = true; break end
		if not dicht[k] then
			dicht[k] = true
			local i, j = k // NC, k % NC
			for di = -1, 1 do
				for dj = -1, 1 do
					if (di ~= 0 or dj ~= 0) and isVrij(i + di, j + dj) and (di == 0 or dj == 0 or (isVrij(i + di, j) and isVrij(i, j + dj))) then
						local n = (i + di) * NC + (j + dj)
						local ng = g[k] + ((di ~= 0 and dj ~= 0) and 1.4142 or 1)
						if not g[n] or ng < g[n] then
							g[n] = ng; van[n] = k
							push(ng + math.sqrt((gi - i - di) ^ 2 + (gj - j - dj) ^ 2), n)
						end
					end
				end
			end
		end
	end
	if not gevonden then return nil end
	local pts: {{number}} = {}
	local k: number? = doel
	while k do
		local x, y = celXY(k // NC, k % NC)
		table.insert(pts, 1, {x, y})
		k = van[k]
	end
	local uit: {Vector3} = {}
	local a = 1
	while a < #pts do                                  -- inkorten: steeds het verste punt dat je in een rechte lijn ziet
		local b2 = #pts
		while b2 > a + 1 and not zicht(pts[a][1], pts[a][2], pts[b2][1], pts[b2][2]) do b2 -= 1 end
		table.insert(uit, W(pts[b2][1], pts[b2][2])); a = b2
	end
	return uit
end
-- plek op de schijf net naast de boot, aan de kant van 'naar' (vrije cel van het raster)
local function naast(st: Seat, naar: Vector3): Vector3
	local cx, cy = modelVan(midden(st))
	local nx, ny = modelVan(naar)
	local d = math.max(1e-3, math.sqrt((nx - cx) ^ 2 + (ny - cy) ^ 2))
	local i, j = dichtstVrij(cx + (nx - cx) / d * 1.6, cy + (ny - cy) / d * 1.6)
	local x, y = celXY(i, j)
	return W(x, y)
end

local function klok(): number
	return (workspace:GetServerTimeNow() - (rit:GetAttribute("RitStart") :: number)) % CYCLUS
end
local function fase(tc: number): string
	if tc < T_IN then return "instappen" elseif tc < T_IN + T_RIT then return "rit" end
	return "uitstappen"
end

-- ===== bezoekers =====
type B = {m: Model, hum: Humanoid, hrp: BasePart, fase: string, s: number, stoel: Seat?, zitAnim: AnimationTrack?, buiten: boolean}
-- zitten: het parksysteem haalt het Animate-script weg, dus zelf de R15-zitanimatie afspelen (Daan 18 nov: "de zit animatie is
-- niet goed": ze stonden rechtop in de boot)
local ZIT_ANIM = "rbxassetid://2506281703"
local map = workspace:FindFirstChild("SiroccoBezoekersActief") or Instance.new("Folder")
map.Name = "SiroccoBezoekersActief"; map.Parent = workspace
local rij: {B} = {}                     -- volgorde in de rij, vooraan = 1
local alle: {[Model]: B} = {}

local function eigenaar(b: B)
	for _, d in b.m:GetDescendants() do if d:IsA("BasePart") then pcall(function() d:SetNetworkOwner(nil) end) end end
end
local function plat(a: Vector3, b: Vector3): number return Vector3.new(a.X - b.X, 0, a.Z - b.Z).Magnitude end
-- lopen naar p; vastloopcontrole: komt hij 1,5 s niet vooruit (tegen gaas of boot: de doorgangen op de schijf zijn smaller dan
-- het pathfinding-raster van 4 studs), of haalt hij het niet binnen max s, dan staat hij meteen op p (niemand blijft hangen)
local function loop(b: B, p: Vector3, marge: number?, max: number?)
	b.hum:MoveTo(p)
	local t0, tGoed, pGoed = os.clock(), os.clock(), b.hrp.Position
	while b.m.Parent and plat(b.hrp.Position, p) > (marge or 1.5) do
		task.wait(0.1)
		if (b.hrp.Position - pGoed).Magnitude > 1 then pGoed = b.hrp.Position; tGoed = os.clock()
		elseif os.clock() - tGoed > 1.5 or os.clock() - t0 > (max or 8) then
			local r = Vector3.new(p.X - b.hrp.Position.X, 0, p.Z - b.hrp.Position.Z)
			local kijk = r.Magnitude > 0.1 and r.Unit or b.hrp.CFrame.LookVector
			b.m:PivotTo(CFrame.lookAt(p + Vector3.new(0, 3, 0), p + Vector3.new(0, 3, 0) + kijk))
			return
		end
		if os.clock() - t0 > 1 and (os.clock() - t0) % 2 < 0.1 then b.hum:MoveTo(p) end      -- MoveTo verloopt na 8 s
	end
end
local function padNaar(b: B, doel: Vector3)
	local ax, ay = modelVan(b.hrp.Position)
	local bx, by = modelVan(doel)
	local pts = route(ax, ay, bx, by)
	if pts then for _, p in pts do loop(b, p, 1.4, 5) end end
	loop(b, doel, 1.0, 4)
end

local function inRij(b: B, vooraan: boolean)
	b.fase = "rij"; b.stoel = nil; b.m:SetAttribute("Fase", "rij")
	if vooraan then table.insert(rij, 1, b) else table.insert(rij, b) end
end

-- voetstappen (Daan 18 nov: "ik mis andere voetstappen"): elke bezoeker een loopgeluid dat bij de ondergrond past (zelfde
-- opnames als Voetstappen.client.luau van de spelers), speelt alleen als hij loopt
local STAP = {hout = "rbxassetid://6506537704", steen = "rbxassetid://91557584218550", gras = "rbxassetid://106672010112184"}
local function stappen(m: Model, hum: Humanoid, hrp: BasePart)
	if hrp:FindFirstChild("Stappen") then return end
	local so = Instance.new("Sound"); so.Name = "Stappen"; so.Looped = true; so.Volume = 0.22
	so.RollOffMode = Enum.RollOffMode.InverseTapered; so.RollOffMinDistance = 4; so.RollOffMaxDistance = 28
	so.SoundId = STAP.hout; so.Parent = hrp
	local ray = RaycastParams.new(); ray.FilterType = Enum.RaycastFilterType.Exclude; ray.FilterDescendantsInstances = {m}
	task.spawn(function()
		while m.Parent and hrp.Parent do
			local loopt = hrp.AssemblyLinearVelocity.Magnitude > 2 and not hum.SeatPart
			if loopt then
				local hit = workspace:Raycast(hrp.Position, Vector3.new(0, -6, 0), ray)
				local soort = "steen"
				if hit then
					if hit.Instance:IsA("Terrain") then soort = hit.Material == Enum.Material.Grass and "gras" or "steen"
					elseif hit.Instance.Name:match("vlonder") or hit.Instance.Name:match("platform") or hit.Instance.Name:match("subschijf") then soort = "hout" end
				end
				if so.SoundId ~= STAP[soort] then so.SoundId = STAP[soort] end
				so.PlaybackSpeed = math.clamp(hrp.AssemblyLinearVelocity.Magnitude / 7, 0.8, 1.2)
			end
			if loopt ~= so.IsPlaying then if loopt then so:Play() else so:Stop() end end
			task.wait(0.3)
		end
	end)
end

local function nieuw(m: Model, s: number)
	local hum = m:FindFirstChildOfClass("Humanoid")
	local hrp = m:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not hum or not hrp then return end
	m.Parent = map
	local b: B = {m = m, hum = hum, hrp = hrp, fase = "rij", s = s, stoel = nil, zitAnim = nil, buiten = false}
	alle[m] = b
	stappen(m, hum, hrp)
	inRij(b, false)
end

-- naar de gekozen boot en instappen; lukt het niet (boot bezet, te laat), dan weer vooraan in de rij
local function naarBoot(b: B, st: Seat)
	b.fase = "naarBoot"; b.stoel = st; gereserveerd[st] = true; b.m:SetAttribute("Fase", "naarBoot")
	for _, p in IN_ROUTE do loop(b, p, 1.5, 5) end
	local function kies(): Seat?
		if b.stoel and not b.stoel.Occupant then return b.stoel end
		if b.stoel then gereserveerd[b.stoel] = nil end
		local ander = vrijeStoel()
		if ander then gereserveerd[ander] = true end
		b.stoel = ander
		return ander
	end
	for _ = 1, 3 do
		local doel = kies()
		if not doel or fase(klok()) ~= "instappen" then break end
		padNaar(b, naast(doel, IN_ROUTE[#IN_ROUTE]))
		if fase(klok()) ~= "instappen" then break end
		if not doel.Occupant then
			doel:Sit(b.hum)
			task.wait(0.3)
			gereserveerd[doel] = nil
			if doel.Occupant == b.hum then
				b.fase = "zit"; eigenaar(b); b.m:SetAttribute("Fase", "zit")
				local an = b.hum:FindFirstChildOfClass("Animator")
				if an and not b.zitAnim then
					local a = Instance.new("Animation"); a.AnimationId = ZIT_ANIM
					local tr = an:LoadAnimation(a); tr.Priority = Enum.AnimationPriority.Action; tr.Looped = true
					b.zitAnim = tr
				end
				if b.zitAnim then b.zitAnim:Play(0.2) end
				return
			end
		end
	end
	-- niet gelukt: terug naar de kop van de rij (voor de poort)
	if b.stoel then gereserveerd[b.stoel] = nil end
	b.stoel = nil
	if fase(klok()) == "rit" then b.m:PivotTo(CFrame.new(op(L_TOT) + Vector3.new(0, 3, 0))) end   -- niet op een draaiende schijf blijven
	for i = #IN_ROUTE, 1, -1 do loop(b, IN_ROUTE[i], 1.5, 5) end
	b.s = L_TOT
	inRij(b, true)
end

-- uitstappen: uit de boot (naast de boot aan de kant van de uitgang), door de opening, over de brug, naar de volgende attractie
local function uitstappen(b: B)
	local st = b.stoel
	b.fase = "uit"; b.m:SetAttribute("Fase", "uit")
	task.wait(math.random() * 1.5)
	if st then
		local w = st:FindFirstChild("SeatWeld"); if w then w:Destroy() end
		b.hum.Sit = false
		if b.zitAnim then b.zitAnim:Stop(0.1) end
		task.wait(0.1)
		b.m:PivotTo(CFrame.new(naast(st, UIT_ROUTE[1]) + Vector3.new(0, 3, 0)))
	end
	b.stoel = nil
	eigenaar(b)
	padNaar(b, pol(6.4, -111))                     -- vrij punt in de uitstapopening (-115..-97; boot bl staat bij -94)
	for i, p in UIT_ROUTE do
		loop(b, p, 1.6, 8)
		if i == 4 then b.buiten = true end              -- voorbij de uitgangsdeur en het begin van de brug
	end
	alle[b.m] = nil
	if b.m.Parent then Park.naarVolgende("Sirocco", b.m) end
end

-- ===== rij laten opschuiven en instappen =====
local vorigeFase = ""
local laatsteVertrek = 0
task.spawn(function()
	while true do
		task.wait(0.2)
		local tc = klok()
		local f = fase(tc)
		-- iedereen in de rij: plek k = L_TOT - (k-1)*SP; sturen 3 studs vooruit langs de lijn (vloeiend door de bochten)
		for k, b in rij do
			if not b.m.Parent then continue end
			local doel = math.max(0, L_TOT - (k - 1) * SP)
			if b.s < doel - 0.05 then
				if plat(b.hrp.Position, op(b.s)) < 2.5 then b.s = math.min(doel, b.s + 3) end
				b.hum:MoveTo(op(b.s))
			elseif plat(b.hrp.Position, op(doel)) > 1.5 then
				b.hum:MoveTo(op(doel))
			end
		end
		-- instappen: wie vooraan staat kiest een eigen vrije boot (om de VERTREK s een volgende)
		local voor = rij[1]
		if f == "instappen" and tc < INSTAP_TOT and voor and voor.m.Parent and os.clock() - laatsteVertrek > VERTREK
			and voor.s >= L_TOT - 0.1 and plat(voor.hrp.Position, op(L_TOT)) < 3.5 then
			local st = vrijeStoel()
			if st then
				table.remove(rij, 1)
				laatsteVertrek = os.clock()
				task.spawn(naarBoot, voor, st)
			end
		end
		-- na de rit: alle zittende bezoekers stappen uit
		if f ~= vorigeFase then
			if f == "uitstappen" then
				for _, b in alle do if b.fase == "zit" then task.spawn(uitstappen, b) end end
			end
			vorigeFase = f
		end
		-- doorgeven aan SiroccoRit: nog bezig met instappen / uitstappen?
		local naarBoot, uit = 0, 0
		for _, b in alle do
			if b.fase == "naarBoot" then naarBoot += 1 elseif b.fase == "uit" and not b.buiten then uit += 1 end
		end
		rit:SetAttribute("NpcInstap", naarBoot > 0 or (#rij > 0 and vrijeStoel() ~= nil))
		rit:SetAttribute("NpcUit", uit)
		-- opruimen: wie weg is (verwijderd), uit de rij
		for k = #rij, 1, -1 do if not rij[k].m.Parent then alle[rij[k].m] = nil; table.remove(rij, k) end end
	end
end)

-- ===== start: de rij vol bezoekers, achter elkaar vanaf de poort =====
local AANTAL = Park.aantal(MAX_BEZOEKERS)
for k = 1, AANTAL do
	local s = math.max(0, L_TOT - (k - 1) * SP)
	local p = op(s)
	local r = p - op(s - 1)                                -- kijkrichting = looprichting van de rij
	r = Vector3.new(r.X, 0, r.Z).Magnitude > 1e-3 and Vector3.new(r.X, 0, r.Z).Unit or Vector3.new(1, 0, 0)
	local m = Park.maak(CFrame.lookAt(p + Vector3.new(0, 3, 0), p + Vector3.new(0, 3, 0) + r), map)
	if m then nieuw(m, s) end
end
-- wie van een andere attractie komt (Park.naarVolgende), sluit achteraan aan
Park.registreer("Sirocco", {ingang = lijn[1], ontvang = function(m: Model) nieuw(m, 0) end})
