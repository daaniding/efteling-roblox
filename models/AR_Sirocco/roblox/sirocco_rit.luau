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
	p.Position = MIDDEN + Vector3.new(x * S, (z or 0.5) * S, -y * S); p.Parent = fg
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

-- mensen (Daan 18 nov: "gepraat in de wachtrij, geschreeuw een beetje in de attractie"): PSE-walla zonder verstaanbare woorden
local MENSEN = {gepraat1 = 9112787259, gepraat2 = 9112766358, gegil = 9112811007, kreet = 9114775800}
for i, p in {{12.0, -11.0, 1}, {12.0, 11.2, 2}, {9.6, -3.5, 1}} do       -- begin van de rij, haarspeld, boog bij de schijf
	local s2 = snd(bron("gepraat" .. i, p[1], p[2], 0.6), "gepraat", p[3] == 1 and MENSEN.gepraat1 or MENSEN.gepraat2, 0.12, 8, 50, true)
	s2.TimePosition = i * 9
end
snd(midden, "gegil", MENSEN.gegil, 0, 15, 110, true)                                   -- joelende kinderen, volume volgt de rit
snd(bron("kreetbron", 0, 0, 1.0), "kreet", MENSEN.kreet, 0.25, 12, 90, false)              -- losse kreet, de client verplaatst de bron

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
zet(game:GetService("ServerScriptService"), "Script", "SiroccoRit", [==[__SERVER__]==])
zet(game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts"), "LocalScript", "SiroccoRitClient", [==[__CLIENT__]==])
zet(game:GetService("ServerScriptService"), "Script", "SiroccoBezoekers", [==[__BEZOEKERS__]==])
zet(game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts"), "LocalScript", "SiroccoMuziekKiezer", [==[__KIEZER__]==])
return "Sirocco rijklaar: " .. n .. " delen, 12 stoelen"
