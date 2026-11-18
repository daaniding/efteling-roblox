-- sirocco_rit: maakt de Sirocco rijklaar in Studio (Edit), NA plaats_sirocco (Rit met onderdelen SI_<rol>_<n>_rt<groep>).
-- - attributen op Rit: Midden, P_sa..sc (midden subschijf), P_ba..bl (midden voet van elke boot), Delen (aantal onderdelen)
-- - per boot 1 onzichtbare Seat "Stoel_rt<b>" op de bank achterin (tegen het sierpaneel), kijkend naar de boeg, met
--   ProximityPrompt "Board [E]" (Style Custom: eigen knop in SiroccoRitClient); geen aanraak-zitten (CanTouch uit), instappen alleen via de prompt (server)
-- - Sirocco.RitAfsluiting: 2 onzichtbare schotten in de openingen van het gaashek (-62 instap, -106 uitstap), dicht tijdens de rit
-- - Scharnier/Hoek op de klapdeuren SI_poort_*_0_om (Omgeving)
-- - Sirocco.Geluid: gepraat in de rij (3x), gegil en kreten tijdens de rit, wachtrijmuziek (speakers langs de rij), muziek in de attractie (dak), water (3x op de vijver), kolkend water + brom (schijf), wind, bel (hutje), hekjes
-- - LocalizationService.SiroccoTeksten: nl-vertaling van de Engelse teksten
-- - ReplicatedStorage.SiroccoDraai (RemoteEvent, maakt SiroccoRit zelf aan als hij ontbreekt)
-- - scripts: ServerScriptService.SiroccoRit en StarterPlayerScripts.SiroccoRitClient (bron: roblox/*.luau, ingevuld door maak_rit.py)
local S = 3
local sir = workspace:WaitForChild("Sirocco")
local rit = sir:WaitForChild("Rit")
local MIDDEN = Vector3.new(451.8 * S, 0.2, -186.5 * S)
-- Spiegeling (18 nov): bouwdata in het oude (gespiegelde) modelstelsel; naar Roblox: oud (x, y) -> MIDDEN + (-3y, 3z, 3x)
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
	local p = MIDDEN + Vector3.new(-r * math.sin(t) * S, 0.3 * S + 6, r * math.cos(t) * S)
	local dir = Vector3.new(-math.sin(t), 0, math.cos(t))
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
local function W(x, y) return MIDDEN + Vector3.new(-y * S, 0, x * S) end
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

-- geluid (Daan 18 nov: "bel en water"): gelicentieerde Pro Sound Effects (Creator Store), afgespeeld door SiroccoRitClient
local GELUID = {
	water = 9120570661,    -- PSE "Water Lap Active 2": kabbelend water, kleine golfjes (vijver)
	was = 9112871350,      -- PSE "Ship Stern Wash 2": kolkend water (draaiende schijf, volume volgt de snelheid)
	brom = 9125767459,     -- PSE machinetoon (zelfde als de Pagode), zacht onder de schijf
	wind = 9112777914,     -- PSE wind (zelfde als de Pagode), 2D voor wie in een boot zit
	bel = 9119642644,      -- PSE dubbele bel (vertrek, zelfde als de Pagode)
	hek = 9116875342,      -- PSE hekje open/dicht
}
local oudG = sir:FindFirstChild("Geluid"); if oudG then oudG:Destroy() end
local fg = Instance.new("Folder"); fg.Name = "Geluid"; fg.Parent = sir
local function bron(naam, x, y, z)
	local p = Instance.new("Part"); p.Name = naam; p.Size = Vector3.new(0.5, 0.5, 0.5); p.Transparency = 1
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.Position = MIDDEN + Vector3.new(-y * S, (z or 0.5) * S, x * S); p.Parent = fg
	return p
end
local function snd(ouder, naam, id, vol, minA, maxA, lus)
	local so = Instance.new("Sound"); so.Name = naam; so.SoundId = "rbxassetid://" .. id; so.Volume = vol; so.Looped = lus
	so.RollOffMode = Enum.RollOffMode.InverseTapered; so.RollOffMinDistance = minA; so.RollOffMaxDistance = maxA; so.Parent = ouder
	return so
end
for i, p in {{-1.0, 11.5}, {-11.0, 2.0}, {-6.0, -9.8}} do                 -- noord, west, haven bij Sindbads boot (op het water)
	local w = snd(bron("water" .. i, p[1], p[2], 0.1), "water", GELUID.water, 0.15, 8, 70, true)
	w.TimePosition = i * 7                                                   -- niet allemaal tegelijk dezelfde golf
end
local midden = bron("schijf", 0, 0, 0.6)
snd(midden, "was", GELUID.was, 0, 15, 140, true)
snd(midden, "brom", GELUID.brom, 0, 10, 90, true)
local w = Instance.new("Sound"); w.Name = "wind"; w.SoundId = "rbxassetid://" .. GELUID.wind; w.Volume = 0; w.Looped = true; w.Parent = fg
snd(bron("hut", 0.7, -9.45, 1.5), "bel", GELUID.bel, 0.3, 10, 120, false)
snd(bron("poortIn", 4.0, -7.5, 0.8), "hekIn", GELUID.hek, 0.25, 6, 60, false)
snd(bron("poortUit", -2.0, -8.6, 0.8), "hekUit", GELUID.hek, 0.25, 6, 60, false)

-- muziek (Daan 18 nov: "de wachtrij muziek en de muziek in de attractie"); echte Efteling-muziek mag niet (auteursrecht), dus
-- gelicentieerde APM-muziek uit de Creator Store, te wisselen met SiroccoMuziekKiezer (Studio: K = wachtrij, L = attractie)
local MUZIEK = {rij = 1836725599, rit = 1840889607}   -- APM "Desert Sands" (wachtrij), APM "Land Of Adventure" (attractie)
local RIJ_SPEAKERS = {{5.8, -15.8}, {11.0, -11.9}, {15.6, -6.5}, {15.9, 3.0}, {15.75, 8.0}, {11.35, 11.69}, {8.88, 5.12}, {10.23, -0.6}, {8.22, -6.12}, {3.51, -9.63}}   -- langs 07_omgeving.WACHTRIJ, om de ~5 m
for i, p in RIJ_SPEAKERS do
	local m = snd(bron("speaker" .. i, p[1], p[2], 0.45), "muziekRij", MUZIEK.rij, 0.05, 10, 55, true)
	m:SetAttribute("Speaker", true)
end
snd(bron("dakmuziek", 0, 0, 5.5), "muziekRit", MUZIEK.rit, 0.04, 20, 120, true)          -- vanuit het dak boven de schijf

-- mensen (Daan 18 nov: "gepraat in de wachtrij, geschreeuw een beetje in de attractie"): PSE-walla zonder verstaanbare woorden.
-- Volumes naar gemeten bronluidheid (PlaybackLoudness bij volume 1: muziek ~300, kreet 57, gegil 20, gepraat 11): Daan "ik hoor ze niet"
local MENSEN = {gepraat1 = 9112787259, gepraat2 = 9112766358, gegil = 9112811007, kreet = 9114775800}
for i, p in {{12.0, -11.0, 1}, {12.0, 11.2, 2}, {9.6, -3.5, 1}} do       -- begin van de rij, haarspeld, boog bij de schijf
	local s2 = snd(bron("gepraat" .. i, p[1], p[2], 0.6), "gepraat", p[3] == 1 and MENSEN.gepraat1 or MENSEN.gepraat2, 1.4, 8, 50, true)
	s2.TimePosition = i * 9
end
snd(midden, "gegil", MENSEN.gegil, 0, 15, 110, true)                                   -- joelende kinderen, volume volgt de rit
snd(bron("kreetbron", 0, 0, 1.0), "kreet", MENSEN.kreet, 0.35, 12, 90, false)              -- losse kreet, de client verplaatst de bron

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
	local p = MIDDEN + Vector3.new(-y * S, 0.25 * S + 3.2, x * S)          -- oud (x, y) -> echt park (spiegeling 18 nov)
	return CFrame.lookAt(p, p + Vector3.new(1, 0, 0))                       -- de brug af (oud -y)
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
local stoelen: {BasePart} = {}
for _, p in rit:GetChildren() do
	if p:IsA("BasePart") then
		local g = p.Name:match("_rt(%a+)$")
		if g and groepen[g] then
			p.Anchored = true
			table.insert(delen, p); table.insert(rust, p.CFrame); table.insert(groepVan, g)
		end
		local pr = p:FindFirstChildOfClass("ProximityPrompt")
		if pr then table.insert(prompts, pr) end
		if p:IsA("Seat") then table.insert(stoelen, p) end
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
local muren = sir:WaitForChild("Routemuren", 10)
local schotUit = muren and muren:FindFirstChild("eenrichting_uit") :: BasePart?
-- ===== geluid (Daan 18 nov: "voeg ook geluid toe, bel en water"; Sirocco.Geluid uit sirocco_rit.luau, PSE-geluiden) =====
-- water rond de vijver (altijd), kolkend water + machinebrom bij de schijf (volume volgt de ritsnelheid), wind voor wie in een
-- boot zit, vertrekbel bij het hutje vlak voordat de instappoort dichtgaat, hekgeluid bij open/dicht van de deuren
local geluid = sir:WaitForChild("Geluid", 10)
local function snd(naam: string): Sound? return geluid and geluid:FindFirstChild(naam, true) :: Sound? end
local sWas, sBrom, sWind, sBel, sHekIn, sHekUit = snd("was"), snd("brom"), snd("wind"), snd("bel"), snd("hekIn"), snd("hekUit")
if geluid then for _, d in geluid:GetDescendants() do if d:IsA("Sound") and d.Name == "water" then d:Play() end end end
for _, x in {sWas, sBrom, sWind} do if x then x.Volume = 0; x:Play() end end
local vorigTc, vorigIn, vorigUit = -1, false, false
-- muziek: alle wachtrijspeakers tegelijk starten (synchroon); de muziek in de attractie is zacht tijdens het instappen en vol
-- tijdens de rit (volume volgt de ritsnelheid); Daan 18 nov "het staat te hard": alles ongeveer gehalveerd
local sRitMuziek = snd("muziekRit")
if geluid then for _, d in geluid:GetDescendants() do if d:IsA("Sound") and d.Name == "muziekRij" then d.TimePosition = 0; d:Play() end end end
if sRitMuziek then sRitMuziek:Play() end
-- mensen: gepraat in de rij (altijd), joelen tijdens de rit (volume volgt de snelheid), af en toe een losse kreet uit een boot
local sGegil, sKreet = snd("gegil"), snd("kreet")
local kreetBron = geluid and geluid:FindFirstChild("kreetbron") :: BasePart?
if geluid then for _, d in geluid:GetDescendants() do if d:IsA("Sound") and d.Name == "gepraat" then d:Play() end end end
if sGegil then sGegil.Volume = 0; sGegil:Play() end
local volgendeKreet = 0

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
	if not aan then                                   -- na de medewerker: camera de brug af (SiroccoRit.uitPlek); het
		local hrp = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart") :: BasePart?   -- lichaam volgt in 1e persoon de camera
		if hrp then
			local cam = workspace.CurrentCamera
			local oog = hrp.Position + Vector3.new(0, 1.5, 0)
			cam.CFrame = CFrame.lookAt(oog, oog + Vector3.new(1, -0.15, 0))   -- de brug af (oud -y, na spiegeling +X)
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
	-- uitgang eenrichting (Daan 18 nov: "regel de barriers", "ik kan via de uitgang alsnog naar binnen"): wie op de brug staat,
	-- voorbij de uitstapdeur (y -8,6), kan niet terug naar binnen. Een open deur staat tegen de brugmuur en blokkeert de doorgang
	-- dus niet: daarom een onzichtbaar schot dwars over de opening (Routemuren.eenrichting_uit), alleen dicht voor wie op de brug
	-- staat (lokaal); bezoekers lopen er altijd door (groep Routemuur)
	local hrpE = ch and ch:FindFirstChild("HumanoidRootPart") :: BasePart?
	local opBrug = false
	if hrpE then
		local mx, my = (hrpE.Position.Z - MIDDEN.Z) / 3, -(hrpE.Position.X - MIDDEN.X) / 3   -- oud modelstelsel (spiegeling)
		opBrug = my < -8.75 and math.abs(mx + 2) < 1.6
	end
	if schotUit then schotUit.CanCollide = opBrug end
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
	-- geluid
	local tSnel = rijdt and v or 0
	if sWas then sWas.Volume += (0.22 * tSnel - sWas.Volume) * 0.05 end
	if sBrom then sBrom.Volume += (0.15 * tSnel - sBrom.Volume) * 0.05; sBrom.PlaybackSpeed = 0.6 + 0.35 * tSnel end
	if sWind then sWind.Volume += ((inBoot and 0.18 * tSnel or 0) - sWind.Volume) * 0.05 end
	if sRitMuziek then sRitMuziek.Volume += ((0.04 + 0.08 * tSnel) - sRitMuziek.Volume) * 0.03 end
	if sGegil then sGegil.Volume += (1.0 * tSnel - sGegil.Volume) * 0.04 end     -- bron is zacht (luidheid 20)
	if sKreet and kreetBron and tSnel > 0.6 and os.clock() > volgendeKreet then
		local st = stoelen[math.random(#stoelen)]
		kreetBron.Position = st.Position + Vector3.new(0, 2, 0)
		sKreet.PlaybackSpeed = 0.9 + math.random() * 0.3
		sKreet:Play()
		volgendeKreet = os.clock() + 4 + math.random() * 6
	end
	if sBel and vorigTc >= 0 and vorigTc < T_IN - 1.5 and tc >= T_IN - 1.5 and tc < T_IN then sBel:Play() end    -- vertrekbel
	vorigTc = tc
	local nuIn, nuUit = openIn > 0.02, openUit > 0.02
	if nuIn ~= vorigIn and sHekIn then sHekIn:Play() end
	if nuUit ~= vorigUit and sHekUit then sHekUit:Play() end
	vorigIn, vorigUit = nuIn, nuUit
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
zet(game:GetService("ServerScriptService"), "Script", "SiroccoBezoekers", [==[--!strict
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
-- oud (gespiegeld) modelstelsel -> echt park (18 nov): (x, y) -> MIDDEN + (-3y, 3z, 3x)
local function W(x: number, y: number, z: number?): Vector3 return MIDDEN + Vector3.new(-y * S, (z or Z_DEK) * S, x * S) end
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
local function modelVan(p: Vector3): (number, number) return (p.Z - MIDDEN.Z) / S, -(p.X - MIDDEN.X) / S end
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
-- volume per opname (gemeten bronluidheid bij volume 1: hout 6, steen 37): Daan 18 nov "ik hoor het geloop niet"
local STAPVOL = {hout = 2.0, steen = 0.35, gras = 0.8}
local function stappen(m: Model, hum: Humanoid, hrp: BasePart)
	if hrp:FindFirstChild("Stappen") then return end
	local so = Instance.new("Sound"); so.Name = "Stappen"; so.Looped = true; so.Volume = STAPVOL.hout
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
				if so.SoundId ~= STAP[soort] then so.SoundId = STAP[soort]; so.Volume = STAPVOL[soort] end
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
]==])
zet(game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts"), "LocalScript", "SiroccoMuziekKiezer", [==[--!strict
-- SiroccoMuziekKiezer (StarterPlayerScripts, alleen in Studio): K = volgend nummer voor de wachtrijspeakers, L = volgend nummer
-- voor de muziek in de attractie; naam linksboven (onder die van de Pagode-kiezer). Alleen lokaal: de gekozen ID daarna
-- vastzetten in roblox/sirocco_rit.luau (MUZIEK.rij / MUZIEK.rit). Allemaal gelicentieerde Creator Store-muziek.
local RunService = game:GetService("RunService")
if not RunService:IsStudio() then return end
local UIS = game:GetService("UserInputService")
local RIJ = {
	{"Desert Sands (APM)", 1836725599}, {"Sand Dance (APM)", 1836357161}, {"Temple Dance (APM)", 1836376446},
	{"Arabian Dance - Notenkraker (APM)", 1836281829}, {"Lanterns in the Sand", 111877745518357},
	{"Mystic Sunset in the Arabian Desert", 138183693923881}, {"Sahara By Night", 92883899625211},
	{"Arabian Sands Reverie", 103198544664262},
}
local RIT = {
	{"Land Of Adventure (APM)", 1840889607}, {"Arabian Nightride", 106593797194565}, {"Arabian Nights", 134897287500569},
	{"Desert Sands (APM)", 1836725599}, {"Sand Dance (APM)", 1836357161},
}
local gui = Instance.new("ScreenGui"); gui.Name = "SiroccoMuziekKiezer"; gui.ResetOnSpawn = false
local function regel(y: number): TextLabel
	local l = Instance.new("TextLabel"); l.Size = UDim2.fromOffset(520, 30); l.Position = UDim2.fromOffset(12, y)
	l.BackgroundTransparency = 0.35; l.BackgroundColor3 = Color3.fromRGB(20, 20, 24); l.TextColor3 = Color3.new(1, 1, 1)
	l.Font = Enum.Font.GothamMedium; l.TextSize = 15; l.TextXAlignment = Enum.TextXAlignment.Left; l.Parent = gui
	return l
end
local labRij, labRit = regel(50), regel(84)
gui.Parent = game.Players.LocalPlayer:WaitForChild("PlayerGui")
local g = workspace:WaitForChild("Sirocco"):WaitForChild("Geluid")
local iRij, iRit = 1, 1
local function zet(naam: string, lijst: {{any}}, i: number, lab: TextLabel, wat: string, toets: string)
	local id = lijst[i][2] :: number
	for _, s in g:GetDescendants() do
		if s:IsA("Sound") and s.Name == naam then s.SoundId = "rbxassetid://" .. id; s.TimePosition = 0; s:Play() end
	end
	lab.Text = string.format("  Sirocco %s %d/%d: %s  (%d)   [%s = volgende]", wat, i, #lijst, lijst[i][1] :: string, id, toets)
end
UIS.InputBegan:Connect(function(inp, bezet)
	if bezet then return end
	if inp.KeyCode == Enum.KeyCode.K then iRij = iRij % #RIJ + 1; zet("muziekRij", RIJ, iRij, labRij, "wachtrij", "K")
	elseif inp.KeyCode == Enum.KeyCode.L then iRit = iRit % #RIT + 1; zet("muziekRit", RIT, iRit, labRit, "attractie", "L") end
end)
task.wait(2)
labRij.Text = string.format("  Sirocco wachtrij 1/%d: %s   [K = volgende]", #RIJ, RIJ[1][1] :: string)
labRit.Text = string.format("  Sirocco attractie 1/%d: %s   [L = volgende]", #RIT, RIT[1][1] :: string)
]==])
return "Sirocco rijklaar: " .. n .. " delen, 12 stoelen"
