--!strict
-- SiroccoRit (server, ServerScriptService): ritklok, instappen, uitstappen. De beweging zelf draait op elke client
-- (SiroccoRitClient.client.luau) uit workspace:GetServerTimeNow() - RitStart: zelfde stand voor iedereen, geen schokken
-- (Pagode-les: niets bewegen vanaf de server). Daan 18 nov: 1 zitplaats per boot, boot draait vanzelf, "moet echt sneller",
-- "uitstappen moet vetter, Engels of vertaald", "als er iemand is ingestapt kan jij natuurlijk niet instappen".
-- Ronde: instappen T_IN s (eigen prompt "Board" per boot, alleen als de boot vrij is), rit T_RIT s, uitstappen T_UIT s:
-- stoel los, zelf uit je boot stappen naar de brug; wie na T_BEGELEID s nog op de schijf staat brengt de medewerker weg
-- (beeld zwart). Teksten Engels, vertaling in LocalizationService.SiroccoTeksten (sirocco_rit.luau).
-- Zolang niemand zit houdt de server de klok vast op WACHT (instappen blijft open); daarna nog T_IN - WACHT s.
-- Fasen moeten gelijk zijn aan SiroccoRitClient.
local Players = game:GetService("Players")

local S = 3
local T_IN, T_RIT, T_UIT = 15, 60, 14          -- = SiroccoRitClient
local WACHT = 5
local T_BEGELEID = 9                           -- s na het einde van de rit: wie dan nog op de schijf staat, wordt weggebracht
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

-- uitgang: op het dek bij de uitstapopening (-104 graden, richting brug), plekken naast elkaar zodat niemand op elkaar landt
local function uitPlek(k: number): CFrame
	local a = math.rad(-104 + ((k % 5) - 2) * 2.6)
	local r = 7.7 + (k // 5 % 2) * 0.45
	local p = MIDDEN + Vector3.new(r * math.cos(a) * S, 0.3 * S + 3.2, -r * math.sin(a) * S)
	return CFrame.lookAt(p, p + Vector3.new(math.cos(a), 0, -math.sin(a)))
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
	task.wait(0.9)
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

local function iemandAanBoord(): boolean
	for _, st in stoelen do if st.Occupant then return true end end
	return false
end

local vorige = ""
local weggebracht = false
while true do
	task.wait(0.2)
	local tc, nu = klok()
	if tc >= WACHT and tc < WACHT + 1 and not iemandAanBoord() then
		rit:SetAttribute("RitStart", nu - WACHT)                 -- klok vasthouden: instappen blijft open tot er iemand zit
		tc = WACHT
	end
	local f = fase(tc)
	rit:SetAttribute("Wacht", tc >= WACHT and tc < WACHT + 1)
	if f ~= vorige then
		if f == "rit" then
			wegVanDeSchijf("Take a seat in a boat to ride", false)   -- wie los op de schijf staat, mag niet mee draaien
		elseif f == "uitstappen" then
			weggebracht = false
			task.delay(2.5, function()                              -- eerst de titel, dan de stoelen los: zelf uitstappen
				for _, st in stoelen do
					local hum = st.Occupant
					if hum then losVanStoel(hum) end
				end
			end)
		end
		vorige = f
		bijwerken(f)
	end
	if f == "uitstappen" and not weggebracht and tc >= T_IN + T_RIT + T_BEGELEID then
		weggebracht = true
		wegVanDeSchijf("The attendant walks you to the exit", true)
	end
end
