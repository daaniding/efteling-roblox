-- sirocco_rit: maakt de Sirocco rijklaar in Studio (Edit), NA plaats_sirocco (Rit met onderdelen SI_<rol>_<n>_rt<groep>).
-- - attributen op Rit: Midden, P_sa..sc (midden subschijf), P_ba..bl (midden voet van elke boot), Delen (aantal onderdelen)
-- - per boot 1 onzichtbare Seat "Stoel_rt<b>" op de bank achterin (tegen het sierpaneel), kijkend naar de boeg, met
--   ProximityPrompt "Board [E]" (Style Custom: eigen knop in SiroccoRitClient); geen aanraak-zitten (CanTouch uit), instappen alleen via de prompt (server)
-- - Sirocco.RitAfsluiting: 2 onzichtbare schotten in de openingen van het gaashek (-62 instap, -106 uitstap), dicht tijdens de rit
-- - LocalizationService.SiroccoTeksten: nl-vertaling van de Engelse teksten
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

-- vertaling (Engels -> nl), Roblox vertaalt de teksten automatisch naar de taal van de speler (zoals PagodeTeksten)
local LS = game:GetService("LocalizationService")
local oudT = LS:FindFirstChild("SiroccoTeksten"); if oudT then oudT:Destroy() end
local lt = Instance.new("LocalizationTable"); lt.Name = "SiroccoTeksten"; lt.SourceLocaleId = "en-us"
local T = {
	{"Board", "Instappen"}, {"Welcome aboard, sailor", "Welkom aan boord, zeeman"}, {"Hold on tight!", "Hou je goed vast!"},
	{"Welcome back in port", "Welkom terug in de haven"}, {"Please leave your boat  -  exit via the bridge", "Stap maar uit je boot  -  uitgang via de brug"},
	{"The attendant walks you to the exit", "De medewerker brengt je naar de uitgang"},
	{"Take a seat in a boat to ride", "Neem plaats in een boot om mee te varen"},
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
return "Sirocco rijklaar: " .. n .. " delen, 12 stoelen"
