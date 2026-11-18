-- sirocco_rit: maakt de Sirocco rijklaar in Studio (Edit), NA plaats_sirocco (Rit met onderdelen SI_<rol>_<n>_rt<groep>).
-- - attributen op Rit: Midden, P_sa..sc (midden subschijf), P_ba..bl (midden voet van elke boot), Delen (aantal onderdelen)
-- - per boot 1 onzichtbare Seat "Stoel_rt<b>" op de bank achterin (tegen het sierpaneel), kijkend naar de boeg, met
--   ProximityPrompt "Board [E]" (Style Custom: eigen knop in SiroccoRitClient); geen aanraak-zitten (CanTouch uit), instappen alleen via de prompt (server)
-- - Sirocco.RitAfsluiting: 2 onzichtbare schotten in de openingen van het gaashek (-62 instap, -106 uitstap), dicht tijdens de rit
-- - Scharnier/Hoek op de klapdeuren SI_poort_*_0_om (Omgeving)
-- - LocalizationService.SiroccoTeksten: nl-vertaling van de Engelse teksten
-- - ReplicatedStorage.SiroccoDraai (RemoteEvent, maakt SiroccoRit zelf aan als hij ontbreekt)
-- - scripts: ServerScriptService.SiroccoRit en StarterPlayerScripts.SiroccoRitClient (bron: roblox/*.luau, ingevuld door maak_rit.py)
local S = 3
local sir = workspace:WaitForChild("Sirocco")
local rit = sir:WaitForChild("Rit")
local MIDDEN = Vector3.new(456.5 * S, 0.2, -191.2 * S)
rit:SetAttribute("Midden", MIDDEN)
for _, p in rit:GetChildren() do if p:IsA("Seat") then p:Destroy() end end
local function deel(naam)
	for _, p in rit:GetChildren() do if p.Name:match("^" .. naam) then return p end end
	error("ontbreekt: " .. naam)
end
for _, s in {"sa", "sb", "sc"} do rit:SetAttribute("P_" .. s, deel("SI_subschijf_0_rt" .. s .. "$").Position) end
local LETTERS = "abcdefghijkl"
for i = 1, 12 do
	local b = "b" .. LETTERS:sub(i, i)
	local voet = deel("SI_voet_0_rt" .. b .. "$")
	local sier = deel("SI_sierpaneel_0_rt" .. b .. "$")
	local c = voet.Position
	rit:SetAttribute("P_" .. b, c)
	local d = Vector3.new(c.X - sier.Position.X, 0, c.Z - sier.Position.Z).Unit      -- naar de boeg
	local top = c.Y + voet.Size.Y / 2 + 0.45 * S                                      -- bovenkant bank (03_forms: Z_VOET + 0.45)
	local pos = Vector3.new(c.X, top - 0.2, c.Z) - d * (0.6 * S)
	local st = Instance.new("Seat"); st.Name = "Stoel_rt" .. b
	st.Size = Vector3.new(2, 0.4, 1.6); st.CFrame = CFrame.lookAt(pos, pos + d)
	st.Anchored = true; st.CanCollide = false; st.CanTouch = false; st.CanQuery = false; st.Transparency = 1
	local pr = Instance.new("ProximityPrompt"); pr.ActionText = "Board"; pr.ObjectText = "Sirocco"; pr.Style = Enum.ProximityPromptStyle.Custom
	pr.KeyboardKeyCode = Enum.KeyCode.E; pr.MaxActivationDistance = 9; pr.RequiresLineOfSight = false; pr.HoldDuration = 0.35
	pr.Parent = st
	st.Parent = rit
end
local n = 0
for _, p in rit:GetChildren() do if p:IsA("BasePart") then n += 1 end end
rit:SetAttribute("Delen", n)

local oud = sir:FindFirstChild("RitAfsluiting"); if oud then oud:Destroy() end
local afs = Instance.new("Folder"); afs.Name = "RitAfsluiting"; afs.Parent = sir
for _, a in {-62, -106} do
	local t = math.rad(a); local r = 7.25
	local p = MIDDEN + Vector3.new(r * math.cos(t) * S, 0.3 * S + 6, -r * math.sin(t) * S)
	local dir = Vector3.new(math.cos(t), 0, -math.sin(t))
	local b = Instance.new("Part"); b.Name = a == -62 and "instap" or "uitstap"
	b.Size = Vector3.new(8.5, 12, 1); b.CFrame = CFrame.lookAt(p, p + dir)
	b.Anchored = true; b.CanCollide = false; b.CanQuery = false; b.CanTouch = false; b.Transparency = 1; b.CastShadow = false
	b.Parent = afs
end

-- klapdeuren (07_omgeving.poorten, exports/omgeving_info.json: scharnier, vrij eind dicht, eind open; modelmeters): attributen
-- Scharnier (wereld) en Hoek (+-90 graden, de kant waar het eind naar het open-punt draait) voor SiroccoRitClient
local POORTEN = {
	poort_in_l = {4.8694, -7.0279, 4.0394, -7.4692, 4.4281, -6.1979},
	poort_in_r = {3.1035, -7.9669, 3.9335, -7.5256, 2.6622, -7.1369},
	poort_uit_l = {-3.17, -8.6, -2.05, -8.6, -3.17, -9.72},
	poort_uit_r = {-0.83, -8.6, -1.95, -8.6, -0.83, -9.72},
}
local om = sir:WaitForChild("Omgeving")
local function W(x, y) return MIDDEN + Vector3.new(x * S, 0, -y * S) end
for naam, v in POORTEN do
	local p = om:FindFirstChild("SI_" .. naam .. "_0_om")
	if p then
		local H, E, O = W(v[1], v[2]), W(v[3], v[4]), W(v[5], v[6])
		local best, hoek = math.huge, 0
		for _, h in {math.pi / 2, -math.pi / 2} do
			local d = ((CFrame.Angles(0, h, 0) * (E - H)) - (O - H)).Magnitude
			if d < best then best, hoek = d, h end
		end
		p:SetAttribute("Scharnier", Vector3.new(H.X, p.Position.Y, H.Z)); p:SetAttribute("Hoek", hoek)
		p.CanCollide = true; p.CanQuery = true
	end
end

-- vertaling (Engels -> nl), Roblox vertaalt de teksten automatisch naar de taal van de speler (zoals PagodeTeksten)
local LS = game:GetService("LocalizationService")
local oudT = LS:FindFirstChild("SiroccoTeksten"); if oudT then oudT:Destroy() end
local lt = Instance.new("LocalizationTable"); lt.Name = "SiroccoTeksten"; lt.SourceLocaleId = "en-us"
local T = {
	{"Board", "Instappen"}, {"Welcome aboard, sailor", "Welkom aan boord, zeeman"}, {"Hold on tight!", "Hou je goed vast!"},
	{"Welcome back in port", "Welkom terug in de haven"},
	{"The attendant walks you to the exit", "De medewerker brengt je naar de uitgang"},
	{"Take a seat in a boat to ride", "Neem plaats in een boot om mee te varen"},
	{"Spin your boat: A / D", "Draai je boot: A / D"}, {"Spin your boat with the arrows", "Draai je boot met de pijltjes"},
}
local entries = {}
for _, t in T do table.insert(entries, {Key = "", Source = t[1], Context = "", Values = {nl = t[2]}}) end
lt:SetEntries(entries); lt.Parent = LS

local function zet(ouder, klasse, naam, bron)
	local o = ouder:FindFirstChild(naam); if o then o:Destroy() end
	local s = Instance.new(klasse); s.Name = naam; s.Source = bron; s.Parent = ouder
end
zet(game:GetService("ServerScriptService"), "Script", "SiroccoRit", [==[--!strict
-- SiroccoRit (server, ServerScriptService): ritklok, instappen, uitstappen. De beweging zelf draait op elke client
-- (SiroccoRitClient.client.luau) uit workspace:GetServerTimeNow() - RitStart: zelfde stand voor iedereen, geen schokken
-- (Pagode-les: niets bewegen vanaf de server). Daan 18 nov: 1 zitplaats per boot, boot draait vanzelf, "moet echt sneller",
-- "uitstappen moet vetter, Engels of vertaald", "als er iemand is ingestapt kan jij natuurlijk niet instappen".
-- Ronde: instappen T_IN s (eigen prompt "Board" per boot, alleen als de boot vrij is; instappoort open), rit T_RIT s,
-- uitstappen T_UIT s: direct zwart beeld "Welcome back in port" en je staat op de brug voorbij de uitstappoort (Daan 18 nov:
-- "doe gewoon gelijk zwart beeld"). Teksten Engels, vertaling in LocalizationService.SiroccoTeksten (sirocco_rit.luau).
-- Zelf draaien: client stuurt (hoek, snelheid) van zijn eigen boot via RemoteEvent ReplicatedStorage.SiroccoDraai; de server
-- controleert dat je echt in die boot zit en dat de rit draait, en zet X_<boot> = (hoek, snelheid, servertijd) op Rit.
-- Wacht ook op de NPC-bezoekers: vertrek pas als iedereen die kan instappen zit, deuren pas dicht als iedereen eruit is.
-- Zolang niemand zit houdt de server de klok vast op WACHT (instappen blijft open); daarna nog T_IN - WACHT s.
-- Fasen moeten gelijk zijn aan SiroccoRitClient.
local Players = game:GetService("Players")

local S = 3
local T_IN, T_RIT, T_UIT = 15, 60, 16          -- = SiroccoRitClient; uitstappen 16 s: de uitgangsdeur blijft open tot iedereen eruit is
local WACHT = 5
local CYCLUS = T_IN + T_RIT + T_UIT
local R_SCHIJF = 7.25                          -- gaashek rond de draaischijf (m)

local sir = workspace:WaitForChild("Sirocco") :: Model
local rit = sir:WaitForChild("Rit") :: Model
local MIDDEN = rit:GetAttribute("Midden") :: Vector3
local Y_DEK = MIDDEN.Y + 0.3 * S               -- bovenkant vlonderdek / draaischijf

local stoelen: {Seat} = {}
for _, p in rit:GetChildren() do if p:IsA("Seat") then table.insert(stoelen, p) end end
table.sort(stoelen, function(a, b) return a.Name < b.Name end)
local blokken: {BasePart} = {}
local afs = sir:FindFirstChild("RitAfsluiting")
if afs then for _, p in afs:GetChildren() do if p:IsA("BasePart") then table.insert(blokken, p) end end end

rit:SetAttribute("RitStart", workspace:GetServerTimeNow())

local function fase(tc: number): string
	if tc < T_IN then return "instappen" elseif tc < T_IN + T_RIT then return "rit" end
	return "uitstappen"
end

local function klok(): (number, number)
	local nu = workspace:GetServerTimeNow()
	return (nu - (rit:GetAttribute("RitStart") :: number)) % CYCLUS, nu
end

-- uitgang: op de brug voorbij de uitstappoort (07_omgeving: brug x -2, poort y -8,6), naast elkaar, kijkend naar het zuiden
local function uitPlek(k: number): CFrame
	local x, y = -2 + ((k % 3) - 1) * 0.7, -10.2 - (k // 3 % 4) * 0.8
	local p = MIDDEN + Vector3.new(x * S, 0.25 * S + 3.2, -y * S)
	return CFrame.lookAt(p, p + Vector3.new(0, 0, 1))
end

local function opSchijf(ch: Model): boolean
	local hrp = ch:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not hrp then return false end
	local p = hrp.Position
	return (Vector3.new(p.X, MIDDEN.Y, p.Z) - MIDDEN).Magnitude < R_SCHIJF * S and p.Y > Y_DEK - 1 and p.Y < Y_DEK + 10
end

local function losVanStoel(hum: Humanoid)
	local zit = hum.SeatPart
	if zit then
		local w = zit:FindFirstChild("SeatWeld"); if w then w:Destroy() end
		hum.Sit = false
	end
end

local bezig: {[Player]: boolean} = {}
Players.PlayerRemoving:Connect(function(plr) bezig[plr] = nil end)

-- de medewerker brengt je weg: beeld zwart (client: attribuut SiroccoUit = 2), naar de uitgang, beeld weer open
local function begeleid(plr: Player, k: number, tekst: string)
	if bezig[plr] then return end
	bezig[plr] = true
	plr:SetAttribute("SiroccoTekst", tekst)
	plr:SetAttribute("SiroccoUit", 2)
	task.wait(0.6)
	local ch = plr.Character
	local hum = ch and ch:FindFirstChildOfClass("Humanoid")
	if ch and hum then
		losVanStoel(hum)
		task.wait(0.1)
		ch:PivotTo(uitPlek(k))
	end
	task.wait(1.6)
	plr:SetAttribute("SiroccoUit", 0)
	bezig[plr] = nil
end

local function wegVanDeSchijf(tekst: string, ookZittend: boolean)
	local k = 0
	for _, plr in Players:GetPlayers() do
		local ch = plr.Character
		if ch and opSchijf(ch) then
			local hum = ch:FindFirstChildOfClass("Humanoid")
			local zit = hum and hum.SeatPart
			if ookZittend or not (zit and zit:IsDescendantOf(rit)) then
				task.spawn(begeleid, plr, k, tekst); k += 1
			end
		end
	end
end

-- instappen: prompt per stoel, alleen tijdens het instappen en als de boot vrij is
local function bijwerken(f: string)
	for _, st in stoelen do
		local pr = st:FindFirstChildOfClass("ProximityPrompt")
		if pr then pr.Enabled = f == "instappen" and st.Occupant == nil end
	end
	for _, b in blokken do b.CanCollide = f == "rit" end      -- openingen in het gaashek dicht tijdens de rit
end

for _, st in stoelen do
	local pr = st:FindFirstChildOfClass("ProximityPrompt")
	if not pr then continue end
	pr.Triggered:Connect(function(plr: Player)
		local tc = klok()
		if fase(tc) ~= "instappen" or st.Occupant then return end      -- bezet: niemand anders erin
		local ch = plr.Character
		local hum = ch and ch:FindFirstChildOfClass("Humanoid")
		local hrp = ch and ch:FindFirstChild("HumanoidRootPart") :: BasePart?
		if not (hum and hrp) or hum.Health <= 0 or hum.SeatPart then return end   -- zit al: niet nog een boot
		if (hrp.Position - st.Position).Magnitude > 16 then return end
		st:Sit(hum)
	end)
	st:GetPropertyChangedSignal("Occupant"):Connect(function() bijwerken(fase((klok()))) end)
end

-- zelf draaien
local draaiEvent = game:GetService("ReplicatedStorage"):FindFirstChild("SiroccoDraai") :: RemoteEvent?
if not draaiEvent then
	local re = Instance.new("RemoteEvent"); re.Name = "SiroccoDraai"; re.Parent = game:GetService("ReplicatedStorage"); draaiEvent = re
end
local laatst: {[Player]: number} = {}
Players.PlayerRemoving:Connect(function(plr) laatst[plr] = nil end)
;(draaiEvent :: RemoteEvent).OnServerEvent:Connect(function(plr: Player, hoek: unknown, w: unknown)
	if typeof(hoek) ~= "number" or typeof(w) ~= "number" or hoek ~= hoek or w ~= w or math.abs(hoek) > 1e4 then return end
	local nu = workspace:GetServerTimeNow()
	if nu - (laatst[plr] or 0) < 0.05 then return end
	laatst[plr] = nu
	if fase((klok())) ~= "rit" then return end
	local ch = plr.Character
	local hum = ch and ch:FindFirstChildOfClass("Humanoid")
	local zit = hum and hum.SeatPart
	if not (zit and zit:IsDescendantOf(rit)) then return end
	local boot = zit.Name:match("_rt(%a+)$")
	if boot then rit:SetAttribute("X_" .. boot, Vector3.new(hoek, math.clamp(w, -3, 3), nu)) end
end)
local function draaiWissen()
	for naam in rit:GetAttributes() do if naam:sub(1, 2) == "X_" then rit:SetAttribute(naam, nil) end end
end

local function iemandAanBoord(): boolean
	for _, st in stoelen do if st.Occupant then return true end end
	return false
end

-- wachten op de bezoekers (SiroccoBezoekers: attributen NpcInstap en NpcUit). Wachtvensters liggen 3 s voor het einde van de
-- fase, zodat de deuren dan nog helemaal open staan (SiroccoRitClient: 1,5 s open/dicht); hooguit MAX_HOUD s per venster.
local IN_HOUD, UIT_HOUD, MAX_HOUD = T_IN - 3, CYCLUS - 3, 40
local houdSinds: number? = nil
local vorige = ""
while true do
	task.wait(0.2)
	local tc, nu = klok()
	if tc >= WACHT and tc < WACHT + 1 and not iemandAanBoord() then
		rit:SetAttribute("RitStart", nu - WACHT)                 -- klok vasthouden: instappen blijft open tot er iemand zit
		tc = WACHT
	end
	local venster: number? = nil
	if tc >= IN_HOUD and tc < IN_HOUD + 1 and rit:GetAttribute("NpcInstap") == true then venster = IN_HOUD end
	if tc >= UIT_HOUD and tc < UIT_HOUD + 1 and ((rit:GetAttribute("NpcUit") :: number?) or 0) > 0 then venster = UIT_HOUD end
	if venster then
		houdSinds = houdSinds or nu
		if nu - (houdSinds :: number) < MAX_HOUD then rit:SetAttribute("RitStart", nu - venster); tc = venster end
	else
		houdSinds = nil
	end
	local f = fase(tc)
	rit:SetAttribute("Wacht", tc >= WACHT and tc < WACHT + 1)
	if f ~= vorige then
		if f == "rit" then
			draaiWissen()
			wegVanDeSchijf("Take a seat in a boat to ride", false)   -- wie los op de schijf staat, mag niet mee draaien
		elseif f == "uitstappen" then
			wegVanDeSchijf("Welcome back in port", true)                -- direct zwart beeld en naar de brug
			draaiWissen()
		end
		vorige = f
		bijwerken(f)
	end
end
]==])
zet(game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts"), "LocalScript", "SiroccoRitClient", [==[--!strict
-- SiroccoRitClient (StarterPlayerScripts): laat de Sirocco draaien op deze client (Pagode-methode: alles verankerd, BulkMoveTo
-- in PreSimulation, stand uit workspace:GetServerTimeNow() - RitStart, dus iedereen ziet hetzelfde).
-- Drie bewegingen opgeteld: hoofdschijf (m) om het midden, subschijven (sa..sc) tegen de draairichting in om hun eigen midden,
-- elke boot (ba..bl) om zijn voet, plus licht dobberen. Onderdelen heten ..._rt<groep> (11_export); draaipunten als attribuut
-- P_<groep> op Rit (sirocco_rit.luau). Hele omwentelingen per rit: na de rit staat alles weer in de instapstand.
-- Wie in een boot zit hangt met een SeatWeld aan de (verankerde) stoel en gaat vanzelf mee; de camera draait mee.
-- Beleving (Daan 18 nov): titel bij het instappen, "Hold on tight!" bij vertrek, na de rit direct zwart (server); eigen
-- instapknop (ProximityPrompt Style Custom); klapdeuren bij instap (open tijdens het instappen) en uitstap (open tijdens het
-- uitstappen), scharnier + hoek als attribuut op de deur (sirocco_rit.luau). Teksten Engels, nl in SiroccoTeksten.
-- Zelf draaien (Daan 18 nov: "kan ik mijn karretje zelf laten draaien"): tijdens de rit A/D (pijltjes, L1/R1, op telefoon twee
-- eigen knoppen onderin het midden) geeft je boot extra draai met vaart en uitlopen. Je eigen boot reageert direct; de stand gaat via RemoteEvent
-- SiroccoDraai naar de server, die hem als attribuut X_<boot> = (hoek, snelheid, servertijd) op Rit zet voor de anderen.
-- Bij het uitlopen draait elke boot terug naar een hele omwenteling, zodat hij weer in de instapstand eindigt.
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local PPS = game:GetService("ProximityPromptService")
local CAS = game:GetService("ContextActionService")
local UIS = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local T_IN, T_RIT, T_UIT, RAMP = 15, 60, 16, 5     -- = SiroccoRit; RAMP = optrekken / uitlopen (s)
local CYCLUS = T_IN + T_RIT + T_UIT
local OMW_M, OMW_S = 5, -11                         -- hele omwentelingen per rit: hoofdschijf, subschijf (t.o.v. de hoofdschijf)
local I_TOT = T_RIT - RAMP

local sir = workspace:WaitForChild("Sirocco") :: Model
local rit = sir:WaitForChild("Rit") :: Model
local MIDDEN = rit:GetAttribute("Midden") :: Vector3
local nDelen = (rit:GetAttribute("Delen") :: number?) or 0
local tel = 0
repeat
	tel = 0
	for _, p in rit:GetChildren() do if p:IsA("BasePart") then tel += 1 end end
	if tel < nDelen then task.wait(0.5) end
until tel >= nDelen

type Groep = {naam: string, ouder: string?, P: Vector3, i: number}
local NAMEN = {"m", "sa", "sb", "sc"}
local LETTERS = "abcdefghijkl"
for i = 1, 12 do table.insert(NAMEN, "b" .. LETTERS:sub(i, i)) end
local groepen: {[string]: Groep} = {}
for _, n in NAMEN do
	local g: Groep = {naam = n, ouder = nil, P = MIDDEN, i = 0}
	if n:sub(1, 1) == "s" then
		g.ouder = "m"; g.P = rit:GetAttribute("P_" .. n) :: Vector3
	elseif n:sub(1, 1) == "b" then
		local i = (LETTERS:find(n:sub(2, 2)) :: number) - 1    -- boot00..11 (03_forms: per subschijf 3 boten, dan 1 op de hoofdschijf)
		g.i = i
		g.ouder = (i % 4 == 3) and "m" or ("s" .. ("abc"):sub(i // 4 + 1, i // 4 + 1))
		g.P = rit:GetAttribute("P_" .. n) :: Vector3
	end
	groepen[n] = g
end

local delen: {BasePart} = {}
local rust: {CFrame} = {}
local groepVan: {string} = {}
local prompts: {ProximityPrompt} = {}
for _, p in rit:GetChildren() do
	if p:IsA("BasePart") then
		local g = p.Name:match("_rt(%a+)$")
		if g and groepen[g] then
			p.Anchored = true
			table.insert(delen, p); table.insert(rust, p.CFrame); table.insert(groepVan, g)
		end
		local pr = p:FindFirstChildOfClass("ProximityPrompt")
		if pr then table.insert(prompts, pr) end
	end
end

-- klapdeuren (07_omgeving.poorten): attribuut Scharnier (wereld) en Hoek (rad, dicht -> open) op elk blad
type Deur = {p: BasePart, rust: CFrame, H: Vector3, hoek: number, uit: boolean}
local deuren: {Deur} = {}
local om = sir:WaitForChild("Omgeving")
for _, naam in {"poort_in_l", "poort_in_r", "poort_uit_l", "poort_uit_r"} do
	local p = om:WaitForChild("SI_" .. naam .. "_0_om", 10) :: BasePart?
	if p and p:GetAttribute("Scharnier") then
		table.insert(deuren, {p = p, rust = p.CFrame, H = p:GetAttribute("Scharnier") :: Vector3, hoek = p:GetAttribute("Hoek") :: number,
			uit = naam:find("uit") ~= nil})
	end
end
local deurStand = {in_ = -1, uit = -1}

local function e(x: number): number return (1 - math.cos(math.pi * math.clamp(x, 0, 1))) / 2 end
local function opgebouwd(x: number): number return RAMP * (x - math.sin(math.pi * x) / math.pi) / 2 end   -- integraal van e
local function voortgang(t: number): (number, number)       -- 0..1 over de rit + huidige snelheid 0..1
	t = math.clamp(t, 0, T_RIT)
	local I, v
	if t < RAMP then I = opgebouwd(t / RAMP); v = e(t / RAMP)
	elseif t <= T_RIT - RAMP then I = RAMP / 2 + (t - RAMP); v = 1
	else I = I_TOT - opgebouwd((T_RIT - t) / RAMP); v = e((T_RIT - t) / RAMP) end
	return I / I_TOT, v
end
local function draai(P: Vector3, th: number): CFrame return CFrame.new(P) * CFrame.Angles(0, th, 0) * CFrame.new(-P) end
local TAU = 2 * math.pi
local function bootHoek(i: number, F: number): number
	local richting = (i % 2 == 0) and 1 or -1
	return richting * (6 + i % 3) * TAU * F + 0.9 * math.sin(TAU * (1 + i % 2) * F)   -- vrij draaiend, elke boot anders
end
local function dobber(i: number, t: number, v: number): CFrame              -- golfjes: rol en stamp, alleen tijdens het varen
	local a = math.rad(3.2) * v
	return CFrame.Angles(a * math.sin(t * 2.1 + i * 1.7), 0, a * 0.8 * math.sin(t * 1.6 + i * 2.3))
end

local plr = Players.LocalPlayer
local GOUD = Color3.fromRGB(232, 190, 96)
local NACHT = Color3.fromRGB(18, 30, 62)
-- knoppen in de stijl van het ingangsbord (07t_bord: perkament, goudbruine houten rand, blauwe schreefletters); Daan 18 nov:
-- de blauw-gouden gloedknoppen waren "teveel AI"
local PERK, HOUT, INKT = Color3.fromRGB(230, 216, 180), Color3.fromRGB(120, 86, 46), Color3.fromRGB(36, 64, 128)

-- ===== beeld: titel, meldingen, zwart bij de medewerker =====
local gui = Instance.new("ScreenGui"); gui.Name = "SiroccoBeeld"; gui.IgnoreGuiInset = true; gui.ResetOnSpawn = false; gui.DisplayOrder = 50
local function label(tekst: string, font: Enum.Font, grootte: number, y: number, kleur: Color3): TextLabel
	local l = Instance.new("TextLabel"); l.AnchorPoint = Vector2.new(0.5, 0.5); l.Position = UDim2.new(0.5, 0, y, 0)
	l.Size = UDim2.new(1, 0, 0, grootte + 10); l.BackgroundTransparency = 1; l.Font = font; l.TextSize = grootte
	l.TextColor3 = kleur; l.TextStrokeColor3 = Color3.fromRGB(20, 10, 0); l.TextStrokeTransparency = 1; l.TextTransparency = 1
	l.Text = tekst; l.ZIndex = 3; l.Parent = gui
	return l
end
local titel = label("S I R O C C O", Enum.Font.Fantasy, 70, 0.28, GOUD); titel.AutoLocalize = false
local titelSchaal = Instance.new("UIScale"); titelSchaal.Parent = titel
local onder = label("", Enum.Font.Fantasy, 28, 0.28 + 0.08, Color3.fromRGB(250, 240, 220))
local lijn = Instance.new("Frame"); lijn.AnchorPoint = Vector2.new(0.5, 0.5); lijn.Position = UDim2.new(0.5, 0, 0.28 + 0.045, 0)
lijn.Size = UDim2.new(0, 0, 0, 2); lijn.BackgroundColor3 = GOUD; lijn.BorderSizePixel = 0; lijn.BackgroundTransparency = 0.2; lijn.Parent = gui
local melding = label("", Enum.Font.Fantasy, 30, 0.82, Color3.new(1, 1, 1))
local zwart = Instance.new("Frame"); zwart.Size = UDim2.fromScale(1, 1); zwart.BackgroundColor3 = Color3.new(0, 0, 0)
zwart.BackgroundTransparency = 1; zwart.BorderSizePixel = 0; zwart.ZIndex = 5; zwart.Parent = gui
local zwartTekst = label("", Enum.Font.Fantasy, 30, 0.5, Color3.fromRGB(240, 226, 190)); zwartTekst.ZIndex = 6
gui.Parent = plr:WaitForChild("PlayerGui")

local volg = 0
local function toonTitel(sub: string, duur: number)
	volg += 1; local mijn = volg
	onder.Text = sub
	titelSchaal.Scale = 1.25
	TweenService:Create(titelSchaal, TweenInfo.new(1.1, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {Scale = 1}):Play()
	TweenService:Create(titel, TweenInfo.new(0.9, Enum.EasingStyle.Sine), {TextTransparency = 0, TextStrokeTransparency = 0.6}):Play()
	TweenService:Create(lijn, TweenInfo.new(1.0, Enum.EasingStyle.Quart, Enum.EasingDirection.Out, 0, false, 0.3), {Size = UDim2.new(0, 420, 0, 2)}):Play()
	TweenService:Create(onder, TweenInfo.new(0.9, Enum.EasingStyle.Sine, Enum.EasingDirection.Out, 0, false, 0.6), {TextTransparency = 0, TextStrokeTransparency = 0.7}):Play()
	task.delay(duur, function()
		if mijn ~= volg then return end
		local uit = TweenInfo.new(0.9, Enum.EasingStyle.Sine, Enum.EasingDirection.In)
		for _, l in {titel, onder} do TweenService:Create(l, uit, {TextTransparency = 1, TextStrokeTransparency = 1}):Play() end
		TweenService:Create(lijn, uit, {Size = UDim2.new(0, 0, 0, 2)}):Play()
	end)
end
local mvolg = 0
local function meld(tekst: string, duur: number)
	mvolg += 1; local mijn = mvolg
	melding.Text = tekst; melding.Position = UDim2.new(0.5, 0, 0.79, 0)        -- boven de draaiknoppen (telefoon)
	TweenService:Create(melding, TweenInfo.new(0.6, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {Position = UDim2.new(0.5, 0, 0.76, 0), TextTransparency = 0, TextStrokeTransparency = 0.6}):Play()
	task.delay(duur, function()
		if mijn ~= mvolg then return end
		TweenService:Create(melding, TweenInfo.new(0.7, Enum.EasingStyle.Sine), {TextTransparency = 1, TextStrokeTransparency = 1}):Play()
	end)
end
plr:GetAttributeChangedSignal("SiroccoUit"):Connect(function()
	local aan = (plr:GetAttribute("SiroccoUit") or 0) == 2
	zwartTekst.Text = (plr:GetAttribute("SiroccoTekst") :: string?) or ""
	local info = TweenInfo.new(aan and 0.5 or 0.9, Enum.EasingStyle.Sine)
	TweenService:Create(zwart, info, {BackgroundTransparency = aan and 0 or 1}):Play()
	TweenService:Create(zwartTekst, info, {TextTransparency = aan and 0 or 1}):Play()
	if not aan then                                   -- na de medewerker: camera de brug af (zuid = +Z, SiroccoRit.uitPlek); het
		local hrp = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart") :: BasePart?   -- lichaam volgt in 1e persoon de camera
		if hrp then
			local cam = workspace.CurrentCamera
			local oog = hrp.Position + Vector3.new(0, 1.5, 0)
			cam.CFrame = CFrame.lookAt(oog, oog + Vector3.new(0, -0.15, 1))
		end
	end
end)

-- ===== instapknop (ProximityPrompt Style Custom): perkamenten bordje, houten rand, toets, vasthoudbalk =====
local knoppen: {[ProximityPrompt]: BillboardGui} = {}
local function toetsTekst(pr: ProximityPrompt, invoer: Enum.ProximityPromptInputType): string
	if invoer == Enum.ProximityPromptInputType.Touch then return "TAP" end
	if invoer == Enum.ProximityPromptInputType.Gamepad then return "X" end
	return pr.KeyboardKeyCode.Name
end
PPS.PromptShown:Connect(function(pr: ProximityPrompt, invoer: Enum.ProximityPromptInputType)
	if pr.Style ~= Enum.ProximityPromptStyle.Custom or not pr:IsDescendantOf(rit) then return end
	local bb = Instance.new("BillboardGui"); bb.Name = "SiroccoKnop"; bb.Adornee = pr.Parent :: BasePart
	bb.Size = UDim2.fromOffset(230, 70); bb.StudsOffset = Vector3.new(0, 4.2, 0); bb.AlwaysOnTop = true; bb.Active = true
	bb.ResetOnSpawn = false
	local schaal = Instance.new("UIScale"); schaal.Scale = 0.85; schaal.Parent = bb
	local pil = Instance.new("TextButton"); pil.Size = UDim2.fromScale(1, 1); pil.BackgroundColor3 = PERK; pil.BackgroundTransparency = 1
	pil.AutoButtonColor = false; pil.Text = ""; pil.Parent = bb
	Instance.new("UICorner", pil).CornerRadius = UDim.new(0, 6)
	local rand = Instance.new("UIStroke"); rand.Color = HOUT; rand.Thickness = 4; rand.Transparency = 1; rand.ApplyStrokeMode = Enum.ApplyStrokeMode.Border; rand.Parent = pil
	local toets = Instance.new("TextLabel"); toets.AnchorPoint = Vector2.new(0, 0.5); toets.Position = UDim2.new(0, 10, 0.5, 0)
	toets.Size = UDim2.fromOffset(50, 50); toets.BackgroundColor3 = HOUT; toets.BackgroundTransparency = 1; toets.Font = Enum.Font.Garamond
	toets.TextSize = 26; toets.TextColor3 = PERK; toets.TextTransparency = 1; toets.AutoLocalize = false
	toets.Text = toetsTekst(pr, invoer); toets.Parent = pil
	Instance.new("UICorner", toets).CornerRadius = UDim.new(0, 5)
	local ring = Instance.new("UIStroke"); ring.Color = HOUT; ring.Thickness = 0; ring.Transparency = 1; ring.Parent = toets
	local actie = Instance.new("TextLabel"); actie.Position = UDim2.new(0, 72, 0, 10); actie.Size = UDim2.new(1, -86, 0, 30)
	actie.BackgroundTransparency = 1; actie.Font = Enum.Font.Garamond; actie.TextSize = 32; actie.TextColor3 = INKT
	actie.TextXAlignment = Enum.TextXAlignment.Left; actie.TextTransparency = 1; actie.Text = pr.ActionText; actie.Parent = pil
	local obj = Instance.new("TextLabel"); obj.Position = UDim2.new(0, 73, 0, 40); obj.Size = UDim2.new(1, -86, 0, 18)
	obj.BackgroundTransparency = 1; obj.Font = Enum.Font.Garamond; obj.TextSize = 16; obj.TextColor3 = HOUT; obj.AutoLocalize = false
	obj.TextXAlignment = Enum.TextXAlignment.Left; obj.TextTransparency = 1; obj.Text = "Sirocco"; obj.Parent = pil
	local balk = Instance.new("Frame"); balk.AnchorPoint = Vector2.new(0, 1); balk.Position = UDim2.new(0, 72, 1, -8)
	balk.Size = UDim2.new(0, 0, 0, 3); balk.BackgroundColor3 = INKT; balk.BorderSizePixel = 0; balk.Parent = pil
	Instance.new("UICorner", balk).CornerRadius = UDim.new(1, 0)
	bb.Parent = plr:WaitForChild("PlayerGui")
	knoppen[pr] = bb
	local IN = TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	TweenService:Create(schaal, IN, {Scale = 1}):Play()
	TweenService:Create(pil, IN, {BackgroundTransparency = 0}):Play()
	TweenService:Create(rand, IN, {Transparency = 0}):Play()
	TweenService:Create(toets, IN, {BackgroundTransparency = 0, TextTransparency = 0}):Play()
	TweenService:Create(ring, IN, {Transparency = 0.3}):Play()
	TweenService:Create(actie, IN, {TextTransparency = 0}):Play()
	TweenService:Create(obj, IN, {TextTransparency = 0}):Play()
	-- vasthouden: balk loopt vol; tikken/klikken op de knop werkt ook (touch)
	local verb: {RBXScriptConnection} = {}
	table.insert(verb, pr.PromptButtonHoldBegan:Connect(function()
		TweenService:Create(balk, TweenInfo.new(pr.HoldDuration, Enum.EasingStyle.Linear), {Size = UDim2.new(1, -86, 0, 3)}):Play()
		TweenService:Create(schaal, TweenInfo.new(0.12), {Scale = 0.95}):Play()
	end))
	table.insert(verb, pr.PromptButtonHoldEnded:Connect(function()
		TweenService:Create(balk, TweenInfo.new(0.15), {Size = UDim2.new(0, 0, 0, 3)}):Play()
		TweenService:Create(schaal, TweenInfo.new(0.2, Enum.EasingStyle.Back), {Scale = 1}):Play()
	end))
	table.insert(verb, pr.Triggered:Connect(function()
		TweenService:Create(toets, TweenInfo.new(0.25, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {Size = UDim2.fromOffset(58, 58)}):Play()
	end))
	table.insert(verb, pil.InputBegan:Connect(function(io)
		if io.UserInputType == Enum.UserInputType.Touch or io.UserInputType == Enum.UserInputType.MouseButton1 then pr:InputHoldBegin() end
	end))
	table.insert(verb, pil.InputEnded:Connect(function(io)
		if io.UserInputType == Enum.UserInputType.Touch or io.UserInputType == Enum.UserInputType.MouseButton1 then pr:InputHoldEnd() end
	end))
	pr.PromptHidden:Once(function()
		for _, c in verb do c:Disconnect() end
		knoppen[pr] = nil
		local UIT = TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		TweenService:Create(schaal, UIT, {Scale = 0.5}):Play()
		TweenService:Create(pil, UIT, {BackgroundTransparency = 1}):Play()
		for _, l in {toets, actie, obj} do TweenService:Create(l, UIT, {TextTransparency = 1, BackgroundTransparency = 1}):Play() end
		TweenService:Create(rand, UIT, {Transparency = 1}):Play()
		task.delay(0.25, function() bb:Destroy() end)
	end)
end)

-- camera draait mee met je boot (Pagode-methode: draaiing om het focuspunt, rondkijken blijft gewoon werken)
local meeDraai = 0
RunService:BindToRenderStep("SiroccoMeedraaien", Enum.RenderPriority.Camera.Value + 2, function()
	if meeDraai == 0 then return end
	local cam = workspace.CurrentCamera
	local f = cam.Focus.Position
	cam.CFrame = CFrame.new(f) * CFrame.Angles(0, meeDraai, 0) * CFrame.new(-f) * cam.CFrame
	meeDraai = 0
end)

local cfs = table.create(#delen) :: {CFrame}
local T: {[string]: CFrame} = {}
local vorigF, vorigV = -1, -1
local vorigStoel: CFrame? = nil
local springUit = false
local vorigeFase = ""
local wasInBoot = false
local gemeld = false
plr.CharacterAdded:Connect(function() springUit = false; vorigStoel = nil; wasInBoot = false end)

-- ===== zelf draaien =====
local draaiEvent = ReplicatedStorage:WaitForChild("SiroccoDraai") :: RemoteEvent
local MAX_W, VERSNEL, REM = 2.6, 3.2, 1.6          -- rad/s extra draai, rad/s2 aandrijven, rad/s2 uitlopen
local eigenBoot: string? = nil
local eigenX, eigenW = 0, 0
local links, rechts = false, false
local gebonden = false
local verzonden, vorigZend = 0, 0
local gladX: {[string]: number} = {}
local function knop(naam: string, state: Enum.UserInputState): Enum.ContextActionResult
	local aan = state == Enum.UserInputState.Begin
	if state == Enum.UserInputState.Cancel then aan = false end
	if naam == "SiroccoLinks" then links = aan else rechts = aan end
	return Enum.ContextActionResult.Sink
end
-- telefoon/tablet: eigen draaiknoppen onderin het midden (links zit de joystick, rechts de springknop), zelfde stijl als de
-- instapknop (perkament, houten rand, blauwe pijl); indrukken = iets kleiner
local knopGui = Instance.new("ScreenGui"); knopGui.Name = "SiroccoDraaiKnoppen"; knopGui.ResetOnSpawn = false; knopGui.Enabled = false
knopGui.DisplayOrder = 40; knopGui.Parent = plr:WaitForChild("PlayerGui")
local function draaiKnop(teken: string, x: number, zet: (boolean) -> ())
	local b = Instance.new("TextButton"); b.AnchorPoint = Vector2.new(0.5, 1); b.Position = UDim2.new(0.5, x, 1, -28)
	b.Size = UDim2.fromOffset(88, 88); b.BackgroundColor3 = PERK; b.BackgroundTransparency = 0; b.AutoButtonColor = false
	b.Text = ""; b.Parent = knopGui
	Instance.new("UICorner", b).CornerRadius = UDim.new(0, 8)
	local r = Instance.new("UIStroke"); r.Color = HOUT; r.Thickness = 4; r.ApplyStrokeMode = Enum.ApplyStrokeMode.Border; r.Parent = b
	local pijl = Instance.new("TextLabel"); pijl.Size = UDim2.fromScale(1, 1); pijl.BackgroundTransparency = 1; pijl.Text = teken
	pijl.Font = Enum.Font.Garamond; pijl.TextSize = 84; pijl.TextColor3 = INKT; pijl.AutoLocalize = false; pijl.Parent = b
	local sc = Instance.new("UIScale"); sc.Parent = b
	local function druk(aan: boolean)
		zet(aan)
		TweenService:Create(sc, TweenInfo.new(0.08), {Scale = aan and 0.94 or 1}):Play()
		TweenService:Create(pijl, TweenInfo.new(0.12), {TextColor3 = aan and HOUT or INKT}):Play()
	end
	b.InputBegan:Connect(function(io)
		if io.UserInputType == Enum.UserInputType.Touch or io.UserInputType == Enum.UserInputType.MouseButton1 then druk(true) end
	end)
	b.InputEnded:Connect(function(io)
		if io.UserInputType == Enum.UserInputType.Touch or io.UserInputType == Enum.UserInputType.MouseButton1 then druk(false) end
	end)
end
draaiKnop("<", -56, function(a) links = a end)
draaiKnop(">", 56, function(a) rechts = a end)
local function binden(aan: boolean)
	if aan == gebonden then return end
	gebonden = aan
	if aan then
		CAS:BindActionAtPriority("SiroccoLinks", knop, false, 3000, Enum.KeyCode.A, Enum.KeyCode.Left, Enum.KeyCode.ButtonL1)
		CAS:BindActionAtPriority("SiroccoRechts", knop, false, 3000, Enum.KeyCode.D, Enum.KeyCode.Right, Enum.KeyCode.ButtonR1)
	else
		CAS:UnbindAction("SiroccoLinks"); CAS:UnbindAction("SiroccoRechts")
		links, rechts = false, false
	end
	knopGui.Enabled = aan and UIS.TouchEnabled
end
local function extraVan(n: string, nu: number, dt: number): number
	if n == eigenBoot then return eigenX end
	local x = rit:GetAttribute("X_" .. n) :: Vector3?
	local doel = 0
	if x then doel = x.X + x.Y * math.clamp(nu - x.Z, 0, 0.3) end
	local g = gladX[n] or doel
	if math.abs(doel - g) > 3 then g = doel end
	g += (doel - g) * math.min(1, dt * 10)
	gladX[n] = g
	return g
end

RunService.PreSimulation:Connect(function(dt: number)
	local start = rit:GetAttribute("RitStart") :: number?
	if not start then return end
	local nu = workspace:GetServerTimeNow()
	local tc = (nu - start) % CYCLUS
	local rijdt = tc >= T_IN and tc < T_IN + T_RIT
	local F, v = 0, 0
	if rijdt then F, v = voortgang(tc - T_IN) end
	local ch = plr.Character
	local hum = ch and ch:FindFirstChildOfClass("Humanoid")
	local zit = hum and hum.SeatPart
	local inBoot = zit ~= nil and zit:IsDescendantOf(rit)
	-- eigen boot: aandrijven alleen op volle vaart (niet bij optrekken/uitlopen), daarna uitlopen
	eigenBoot = inBoot and zit and zit.Name:match("_rt(%a+)$") or nil
	local mag = inBoot and rijdt and tc - T_IN > RAMP and tc - T_IN < T_RIT - RAMP
	binden(mag)
	if eigenBoot and rijdt then
		local invoer = mag and ((rechts and 1 or 0) - (links and 1 or 0)) or 0
		if invoer ~= 0 then eigenW = math.clamp(eigenW + invoer * VERSNEL * dt, -MAX_W, MAX_W)
		else eigenW -= math.sign(eigenW) * math.min(math.abs(eigenW), REM * dt) end
		eigenX += eigenW * dt
		if nu - verzonden > 0.1 and (math.abs(eigenX - vorigZend) > 1e-3 or eigenW ~= 0) then
			draaiEvent:FireServer(eigenX, eigenW); verzonden = nu; vorigZend = eigenX
		end
	else
		eigenX, eigenW, vorigZend = 0, 0, 0
	end
	if rijdt or F ~= vorigF or v ~= vorigV then
		T.m = draai(MIDDEN, OMW_M * TAU * F)
		local uitloop = rijdt and tc - T_IN > T_RIT - RAMP
		for _, n in NAMEN do
			local g = groepen[n]
			if n:sub(1, 1) == "s" then T[n] = T.m * draai(g.P, OMW_S * TAU * F)
			elseif n:sub(1, 1) == "b" then
				local P = g.P
				local x = rijdt and extraVan(n, nu, dt) or 0
				if uitloop then local doel = math.round(x / TAU) * TAU; x = doel + (x - doel) * v end   -- terug naar instapstand
				T[n] = T[g.ouder :: string] * CFrame.new(P) * CFrame.Angles(0, bootHoek(g.i, F) + x, 0) * dobber(g.i, tc, v) * CFrame.new(-P)
			end
		end
		for k, p in delen do cfs[k] = T[groepVan[k]] * rust[k] end
		workspace:BulkMoveTo(delen, cfs, Enum.BulkMoveMode.FireCFrameChanged)
		vorigF, vorigV = F, v
	end
	-- klapdeuren: 1,5 s open/dicht aan begin en eind van hun fase
	local openIn = tc < T_IN and e(math.min(tc, T_IN - tc) / 1.5) or 0
	local tu = tc - T_IN - T_RIT
	local openUit = tu >= 0 and e(math.min(tu - 0.5, T_UIT - tu) / 1.5) or 0
	if openIn ~= deurStand.in_ or openUit ~= deurStand.uit then
		for _, d in deuren do
			local f = d.uit and openUit or openIn
			d.p.CFrame = CFrame.new(d.H) * CFrame.Angles(0, d.hoek * f, 0) * CFrame.new(-d.H) * d.rust
			d.p.CanCollide = f < 0.5
		end
		deurStand.in_, deurStand.uit = openIn, openUit
	end
	-- eigen speler in een boot: camera mee, niet uit de boot springen tot het uitstappen, geen andere instapknoppen
	if inBoot and zit then
		local cf = zit.CFrame
		if vorigStoel then
			local _, dy, _ = (cf.Rotation * vorigStoel.Rotation:Inverse()):ToEulerAnglesYXZ()
			meeDraai += dy
		end
		vorigStoel = cf
		for _, pr in prompts do if pr.Enabled then pr.Enabled = false end end      -- alleen lokaal: je zit al
	else
		vorigStoel = nil
	end
	local blokkeer = inBoot
	if hum and blokkeer ~= springUit then
		hum:SetStateEnabled(Enum.HumanoidStateType.Jumping, not blokkeer)
		springUit = blokkeer
	end
	-- beleving
	local f = tc < T_IN and "instappen" or (rijdt and "rit" or "uitstappen")
	if inBoot and not wasInBoot and f == "instappen" then toonTitel("Welcome aboard, sailor", 4) end
	if f ~= vorigeFase then
		if f == "rit" and inBoot then meld("Hold on tight!", 2.5) end
		gemeld = false
		vorigeFase = f
	end
	if mag and not gemeld then                        -- uitleg zodra je zelf mag draaien
		gemeld = true
		local touch = UIS.TouchEnabled and not UIS.KeyboardEnabled
		meld(touch and "Spin your boat with the arrows" or "Spin your boat: A / D", 5)
	end
	wasInBoot = inBoot
end)
]==])
return "Sirocco rijklaar: " .. n .. " delen, 12 stoelen"
