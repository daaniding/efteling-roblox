--!strict
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
