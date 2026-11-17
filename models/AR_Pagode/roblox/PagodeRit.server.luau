--!strict
-- PagodeRit (server): stuurt alleen de ritklok (attribuut RitStart, servertijd). De beweging zelf draait op elke client
-- (PagodeRitClient.client.luau, StarterPlayerScripts) met workspace:GetServerTimeNow(): iedereen ziet dezelfde stand,
-- zonder netwerkvertraging. Daan 17 nov: de server-gestuurde gondel trilde, belichting bleekte uit (losse physics-delen) en
-- spelers zakten weg. Nu blijft alles verankerd.
-- Wachten op passagiers (Daan 17 nov: "op het begin haal ik het niet om op de Pagode te komen"): zolang er niemand op het
-- dek staat, houdt de server de klok vast op WACHT_TC (instappen, hekjes open). Stapt er iemand in, dan loopt de klok door:
-- nog T_IN - WACHT_TC seconden instappen, dan sluiten en de rit. Fasen moeten gelijk zijn aan PagodeRitClient.
local Players = game:GetService("Players")

local S = 3
local T_IN = 60                                -- = PagodeRitClient T_IN
local WACHT_TC = 40                            -- hier wacht hij (uitstappers hebben dan 40 s gehad); daarna nog 20 s
local CYCLUS = T_IN + 5 + 35 + 70 + 35         -- = som van FASEN in PagodeRitClient
local MIDDEN = Vector3.new(360.0 * S, 0, -47.5 * S)
local Y_DEK = 2 + 1.3 * S                      -- instapniveau (NAP 11.3)
local R_DEK = 8.2 * S                          -- binnen de groene rand van de gondel

local pag = workspace:WaitForChild("Pagode") :: Model

pag:SetAttribute("RitStart", workspace:GetServerTimeNow())

local function opDek(plr: Player): BasePart?
	local ch = plr.Character
	local hrp = ch and ch:FindFirstChild("HumanoidRootPart") :: BasePart?
	local hum = ch and ch:FindFirstChildOfClass("Humanoid")
	if hrp and hum and hum.Health > 0 then
		local p = hrp.Position
		local r = (Vector3.new(p.X, 0, p.Z) - MIDDEN).Magnitude
		if r < R_DEK and p.Y > Y_DEK and p.Y < Y_DEK + 9 then return hrp end
	end
	return nil
end

local function iemandAanBoord(): boolean
	for _, plr in Players:GetPlayers() do if opDek(plr) then return true end end
	-- NPC-bezoekers op het dek tellen ook (PagodeBezoekers: attribuut OpDek)
	local b = workspace:FindFirstChild("PagodeBezoekersActief")
	if b then for _, m in b:GetChildren() do if m:GetAttribute("OpDek") then return true end end end
	return false
end

-- Uitstappen na de rit (Daan 17 nov: "ja bouw het zo"): wie de rit heeft meegemaakt (op het dek tijdens sluiten/rijden) moet
-- er bij het instappen weer af. Attribuut Uitstappen op de speler (PagodeBeleving toont de melding):
--   1 vanaf tc 14: "Please exit the gondola" (nl: Graag uitstappen)
--   2 vanaf tc 25: de medewerker brengt je naar de uitgang: beeld zwart, onder aan de uitgangstrap, beeld weer open
-- Zolang zo iemand op het dek staat, vertrekt de gondel niet (klok blijft op WACHT_TC). Opnieuw rijden = opnieuw de rij in.
local MELDING_TC, BEGELEID_TC = 14, 25
local UIT_PLEK = Vector3.new((360.0 + 15.2 * math.cos(math.rad(-20))) * S, 2 + -0.38 * S + 3.2, -(47.5 + 15.2 * math.sin(math.rad(-20))) * S)
local UIT_KIJK = Vector3.new(math.cos(math.rad(-20)), 0, -math.sin(math.rad(-20)))
local gereden: {[Player]: boolean} = {}
Players.PlayerRemoving:Connect(function(plr) gereden[plr] = nil end)

local function begeleid(plr: Player)
	plr:SetAttribute("Uitstappen", 2)
	task.wait(0.6)                                         -- client maakt het beeld zwart
	local ch = plr.Character
	if ch then ch:PivotTo(CFrame.lookAt(UIT_PLEK, UIT_PLEK + UIT_KIJK)) end
	gereden[plr] = nil
	task.wait(0.4)
	plr:SetAttribute("Uitstappen", 0)
end

local function uitstappen(tc: number): boolean
	local wacht = false
	for _, plr in Players:GetPlayers() do
		local hrp = opDek(plr)
		if tc >= T_IN then
			if hrp then gereden[plr] = true end                 -- rijdt mee
		elseif gereden[plr] then
			if not hrp then
				gereden[plr] = nil; plr:SetAttribute("Uitstappen", 0)   -- netjes uitgestapt
			else
				wacht = true
				local stand = plr:GetAttribute("Uitstappen") or 0
				if tc >= BEGELEID_TC and stand < 2 then task.spawn(begeleid, plr)
				elseif tc >= MELDING_TC and stand < 1 then plr:SetAttribute("Uitstappen", 1) end
			end
		end
	end
	return wacht
end

while true do
	task.wait(0.25)
	local nu = workspace:GetServerTimeNow()
	local start = pag:GetAttribute("RitStart") :: number
	local tc = (nu - start) % CYCLUS
	local blijvers = uitstappen(tc)
	if tc >= WACHT_TC and tc < WACHT_TC + 1 and (blijvers or not iemandAanBoord()) then
		pag:SetAttribute("RitStart", nu - WACHT_TC)          -- klok vasthouden: hekjes open tot er iemand instapt / tot de blijvers eruit zijn
	end
	pag:SetAttribute("Wacht", tc >= WACHT_TC and tc < WACHT_TC + 1)
end
