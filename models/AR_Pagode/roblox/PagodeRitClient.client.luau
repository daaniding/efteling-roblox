--!strict
-- PagodeRitClient (StarterPlayerScripts): laat de Pagode rijden op deze client.
-- Ritverloop naar de on-ride video _Wz0aORIVaM: instappen 60 s (Daan), sluiten 5 s, omhoog 35 s, boven 70 s, omlaag 35 s
-- (echte rit 5:10, ingekort: Daan 17 nov "elke draai duurt echt heel lang"); twee volle draaien over de rit. De arm draait om de draaias (AsFrame, lokale Z-as), de gondel blijft waterpas.
-- Alles verankerd en verplaatst met BulkMoveTo; de stand volgt uit workspace:GetServerTimeNow() - RitStart (zelfde voor iedereen).
-- Wie op het dek staat wordt elk frame met de gondel meegenomen (geen wegzakken, geen trillen).
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

local S = 3
local pag = workspace:WaitForChild("Pagode") :: Model
local arm = pag:WaitForChild("Arm") :: Model
local gondel = pag:WaitForChild("Gondel") :: Model
local kern = gondel:WaitForChild("Kern") :: BasePart
local PIV = (pag:WaitForChild("AsFrame") :: CFrameValue).Value
local JL = pag:GetAttribute("GondelLokaal") :: Vector3
local Y_INSTAP = 2 + 1.3 * S
local DEK = 2.2 * S
local BAK = Vector3.new(360.0 * S, 0, -47.5 * S)

local function Jw(th: number): Vector3 return (PIV * CFrame.Angles(0, 0, th)):PointToWorldSpace(JL) end
local lo, hi = math.rad(70), math.rad(120)
for _ = 1, 50 do
	local m = (lo + hi) / 2
	if Jw(m).Y + DEK > Y_INSTAP then lo = m else hi = m end
end
local TH_D = (lo + hi) / 2
local jd = Jw(TH_D)
local CORR = Vector3.new(BAK.X - jd.X, 0, BAK.Z - jd.Z)        -- restafwijking; ~0 sinds de arm 2.71 m langer is (maak_ritscript ArmFactor)
local function schuif(th: number): Vector3 local t = math.clamp(th / TH_D, 0, 1); return CORR * t ^ 4 end

-- delen en hun vaste ligging t.o.v. arm-frame en gondelkern (eenmalig)
local K0 = kern.CFrame
local K_ONDER = CFrame.new(Jw(TH_D) + schuif(TH_D)) * PIV.Rotation      -- stationsstand (= servergondel, PagodeRit)
local poorten = gondel:WaitForChild("Poorten")
local gDelen, gRel = {}, {}
for _, p in gondel:GetDescendants() do
	if p:IsA("BasePart") and not p:IsDescendantOf(poorten) then p.Anchored = true; table.insert(gDelen, p); table.insert(gRel, K0:ToObjectSpace(p.CFrame)) end
end
-- klaphekjes: per blad een scharnier (t.o.v. de kern) en de delen t.o.v. het scharnier; draaien naar binnen open bij het instappen
type Blad = {sch: CFrame, teken: number, delen: {BasePart}, rel: {CFrame}}
local bladen: {Blad} = {}
for _, f in poorten:GetChildren() do
	local b: Blad = {sch = f:GetAttribute("Scharnier") :: CFrame, teken = f:GetAttribute("Teken") :: number, delen = {}, rel = {}}
	for _, p in f:GetChildren() do
		if p:IsA("BasePart") then table.insert(b.delen, p); table.insert(b.rel, p:GetAttribute("Rel") :: CFrame) end
	end
	table.insert(bladen, b)
end
local A0 = PIV
local aDelen, aRel = {}, {}
for _, p in arm:GetDescendants() do
	if p:IsA("BasePart") then p.Anchored = true; table.insert(aDelen, p); table.insert(aRel, A0:ToObjectSpace(p.CFrame)) end
end
-- botsing die met de poortjes meewisselt: reling in de poortopening (gondel), bakrand in de opening (station), dichte bladen
local poortBots: {BasePart} = {}
for _, p in gDelen do if p.Name == "poortreling" then table.insert(poortBots, p) end end
local st = pag:FindFirstChild("Station")
if st then for _, p in st:GetDescendants() do if p:IsA("BasePart") and p.Name == "bakpoort" then table.insert(poortBots, p) end end end
-- klaphekjes in het stationshek (maak_ritscript: Station.Stationpoorten), scharnier in wereldcoordinaten
local stBladen: {Blad} = {}
local stMap = st and st:FindFirstChild("Stationpoorten")
if stMap then
	for _, f in stMap:GetChildren() do
		local b: Blad = {sch = f:GetAttribute("Scharnier") :: CFrame, teken = f:GetAttribute("Teken") :: number, delen = {}, rel = {}}
		for _, p in f:GetChildren() do
			if p:IsA("BasePart") then table.insert(b.delen, p); table.insert(b.rel, p:GetAttribute("Rel") :: CFrame) end
		end
		table.insert(stBladen, b)
	end
end
local bladBots: {BasePart} = {}
for _, b in bladen do for _, p in b.delen do if p.Name == "poortblad" then table.insert(bladBots, p) end end end
for _, b in stBladen do for _, p in b.delen do if p.Name == "poortblad" then table.insert(bladBots, p) end end end

type Cil = {voet: Vector3, kop: Vector3, huis: BasePart, stang: BasePart, Lh: number, Ls: number}
local cils: {Cil} = {}
for _, c in (pag:WaitForChild("Cilinders") :: Folder):GetChildren() do
	if c:IsA("Folder") then
		local v, k = c:GetAttribute("Voet") :: Vector3, c:GetAttribute("Kop") :: Vector3
		local Lup = (k - v).Magnitude
		table.insert(cils, {voet = PIV:PointToWorldSpace(v), kop = k, huis = c:WaitForChild("Huis") :: BasePart,
			stang = c:WaitForChild("Stang") :: BasePart, Lh = 0.62 * Lup + 0.9, Ls = 0.38 * Lup + 0.6})
	end
end
local function staaf(p: BasePart, a: Vector3, r: Vector3, L: number)
	p.Size = Vector3.new(L, p.Size.Y, p.Size.Z)
	p.CFrame = CFrame.lookAt(a + r * (L / 2), a + r * L) * CFrame.Angles(0, math.pi / 2, 0)
end

local T_IN = 60                                       -- instappen: hekjes open (Daan 17 nov: "doe maar zestig")
local FASEN = {{"instappen", T_IN}, {"sluiten", 5}, {"omhoog", 35}, {"boven", 70}, {"omlaag", 35}}   -- = PagodeRit en PagodeBezoekers
local CYCLUS, T_RIT = 0, 35 + 70 + 35
local RONDJES = 2                                   -- twee hele rondjes per rit (Daan: "moet hij niet wat draaien"); heel getal: poortjes eindigen weer voor het station
for _, f in FASEN do CYCLUS += f[2] :: number end
local function e(t: number): number return (1 - math.cos(math.pi * math.clamp(t, 0, 1))) / 2 end

local function stand(tc: number): (number, number, string)
	local t0, t_rit = 0, 0
	for _, f in FASEN do
		local naam, duur = f[1] :: string, f[2] :: number
		if tc < t0 + duur then
			local t = (tc - t0) / duur
			local th = TH_D
			if naam == "omhoog" then th = TH_D * (1 - e(t)) elseif naam == "boven" then th = 0 elseif naam == "omlaag" then th = TH_D * e(t) end
			local phi = 0
			if naam == "omhoog" or naam == "boven" or naam == "omlaag" then phi = RONDJES * 2 * math.pi * e((t_rit + tc - t0) / T_RIT) end
			return th, phi, naam
		end
		t0 += duur
		if naam == "omhoog" or naam == "boven" or naam == "omlaag" then t_rit += duur end
	end
	return TH_D, 0, "instappen"
end

local plr = Players.LocalPlayer
local ray = RaycastParams.new(); ray.FilterType = Enum.RaycastFilterType.Include; ray.FilterDescendantsInstances = {gondel}
local gK = K0
local eenrichting = pag:FindFirstChild("Eenrichting")
local schotT = eenrichting and eenrichting:FindFirstChild("tourniquet") :: BasePart?
local schotU = eenrichting and eenrichting:FindFirstChild("uitgang") :: BasePart?
local voorbijT, voorbijU = false, true
-- geluid (maak_ritscript: Pagode.Geluid): machinebrom volgt de armsnelheid, bel bij vertrek, hekjes bij open/dicht, wind hoog
local geluid = pag:FindFirstChild("Geluid")
local brom = geluid and geluid:FindFirstChild("machine") and geluid.machine:FindFirstChild("brom") :: Sound?
local bel = geluid and geluid:FindFirstChild("station") and geluid.station:FindFirstChild("bel") :: Sound?
local hekG = geluid and geluid:FindFirstChild("station") and geluid.station:FindFirstChild("hek") :: Sound?
local wind = geluid and geluid:FindFirstChild("wind") :: Sound?
if brom then brom:Play() end
if wind then wind:Play() end
local vorigeFase, vorigOpen, thVorig = "", false, TH_D
local huidigeGroep = ""
plr.CharacterAdded:Connect(function() huidigeGroep = "" end)
local cfs = table.create(#gDelen)
-- NPC-bezoekers die meerijden (PagodeBezoekers: attribuut Rijdt, verankerd op de servergondel in de stationsstand = K_ONDER)
local meeRel: {[Model]: CFrame} = {}      -- geen zwakke sleutels: Instance-sleutels worden dan weggegooid (rel drijft weg)
local acfs = table.create(#aDelen)

RunService.PreSimulation:Connect(function(dtF: number)
	local start = pag:GetAttribute("RitStart") :: number?
	if not start then return end
	local tc = (workspace:GetServerTimeNow() - start) % CYCLUS
	local th, phi, naam = stand(tc)
	local A = PIV * CFrame.Angles(0, 0, th)
	local nieuwK = CFrame.new(Jw(th) + schuif(th)) * PIV.Rotation * CFrame.Angles(0, phi, 0)
	-- speler op het dek: meenemen met de verplaatsing van de gondel
	local ch = plr.Character
	local hrp = ch and ch:FindFirstChild("HumanoidRootPart") :: BasePart?
	-- alleen als de gondel echt beweegt: elk frame de CFrame zetten (ook bij stilstand) blokkeert het lopen op het dek
	local delta = gK:ToObjectSpace(nieuwK)
	local _, draai = delta:ToAxisAngle()
	local beweegt = delta.Position.Magnitude > 1e-5 or math.abs(draai) > 1e-7   -- ook de langzame draai (twee rondjes) telt mee
	local rijdt = false
	if hrp and beweegt then
		local r = workspace:Raycast(hrp.Position, Vector3.new(0, -6, 0), ray)
		if r then hrp.CFrame = (nieuwK * gK:Inverse()) * hrp.CFrame; rijdt = true end
	end
	-- wie meerijdt botst niet met de onzichtbare routemuren (de gondel zwaait door de stationshekken)
	local groep = rijdt and "Rijdend" or "Spelers"                -- Spelers: NPC-bezoekers lopen erdoorheen (PagodeBezoekers)
	if ch and groep ~= huidigeGroep then
		for _, p in ch:GetDescendants() do if p:IsA("BasePart") then p.CollisionGroup = groep end end
		huidigeGroep = groep
	end
	for i, rel in gRel do cfs[i] = nieuwK * rel end
	workspace:BulkMoveTo(gDelen, cfs, Enum.BulkMoveMode.FireCFrameChanged)
	local bezoekers = workspace:FindFirstChild("PagodeBezoekersActief")
	if bezoekers then
		for _, m in bezoekers:GetChildren() do
			if m:IsA("Model") and m:GetAttribute("Rijdt") then
				local rel = meeRel[m]
				if not rel then rel = K_ONDER:ToObjectSpace(m:GetPivot()); meeRel[m] = rel end
				m:PivotTo(nieuwK * rel)
			elseif m:IsA("Model") and meeRel[m] then meeRel[m] = nil end
		end
		for m in meeRel do if m.Parent ~= bezoekers then meeRel[m] = nil end end
	end
	for i, rel in aRel do acfs[i] = A * rel end
	workspace:BulkMoveTo(aDelen, acfs, Enum.BulkMoveMode.FireCFrameChanged)
	for _, c in cils do
		local k = A:PointToWorldSpace(c.kop); local u = (k - c.voet).Unit
		staaf(c.huis, c.voet, u, c.Lh); staaf(c.stang, k, -u, c.Ls)
	end
	-- klaphekjes: 2 s open aan het begin van het instappen, 2 s dicht aan het eind (instappen = eerste fase, tc 0..T_IN)
	local open = 0
	if naam == "instappen" then open = math.clamp(math.min(tc / 2, (T_IN - tc) / 2), 0, 1) end
	local hoek = math.rad(85) * e(open)
	for _, b in bladen do
		local scharnier = nieuwK * b.sch * CFrame.Angles(0, b.teken * hoek, 0)
		for i, p in b.delen do p.CFrame = scharnier * b.rel[i] end
	end
	for _, b in stBladen do                        -- stationshekjes: vast in de wereld, gaan tegelijk open
		local scharnier = b.sch * CFrame.Angles(0, b.teken * hoek, 0)
		for i, p in b.delen do p.CFrame = scharnier * b.rel[i] end
	end
	local dicht = open < 0.5
	for _, p in poortBots do p.CanCollide = dicht end
	for _, p in bladBots do p.CanCollide = dicht end
	-- eenrichting: een schot is alleen dicht als je er al voorbij bent (niet terug door de tourniquets, niet terug de uitgang op)
	if hrp and eenrichting then
		local x, y = hrp.Position.X / S - 360, -hrp.Position.Z / S - 47.5
		local r, a = math.sqrt(x * x + y * y), math.deg(math.atan2(y, x))
		-- schakelaar: dicht zodra je voorbij bent, pas weer open als je echt aan de goede kant terug bent (teleport/respawn)
		if r < 12.9 and a > 95 and a < 160 then voorbijT = true elseif r > 14.2 or a < 90 or a > 165 then voorbijT = false end
		-- uitgang: standaard dicht (ook niet van buitenaf de uitgang op), alleen open als je boven op de vlonder staat
		if r > 11.6 then voorbijU = true elseif r < 10.6 and a > -40 and a < 0 then voorbijU = false end
		if schotT then schotT.CanCollide = voorbijT end
		if schotU then schotU.CanCollide = voorbijU end
	end
	-- geluid
	local snel = math.abs(th - thVorig) / math.max(dtF, 1 / 240)                      -- hoeksnelheid arm (rad/s)
	thVorig = th
	if brom then
		local doel = math.clamp(snel / 0.05, 0, 1)                                     -- 0.05 rad/s = volle beweging
		brom.Volume = brom.Volume + (0.5 * doel - brom.Volume) * 0.05
		brom.PlaybackSpeed = 0.55 + 0.25 * doel
	end
	if naam ~= vorigeFase then
		if naam == "sluiten" and bel then bel:Play() end
		vorigeFase = naam
	end
	local nuOpen = open > 0.02
	if nuOpen ~= vorigOpen and hekG then hekG:Play() end
	vorigOpen = nuOpen
	if wind then
		local hoog = rijdt and math.clamp((nieuwK.Position.Y - K0.Position.Y) / 90, 0, 1) or 0
		wind.Volume = wind.Volume + (0.3 * hoog - wind.Volume) * 0.03
	end
	gK = nieuwK
	pag:SetAttribute("FaseLokaal", naam)
end)
