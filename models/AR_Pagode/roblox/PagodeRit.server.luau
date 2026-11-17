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

-- gondel op de server in de stationsstand zetten (zelfde berekening als PagodeRitClient, stand "instappen"): de clients
-- laten hem rijden, maar NPC-bezoekers (PagodeBezoekers) lopen op de server en hebben daar een vloer nodig.
-- De bouwstand hangt hoog in de lucht; zonder dit zakten de bezoekers door de gondel (Daan 17 nov).
do
	local gondel = pag:WaitForChild("Gondel") :: Model
	local kern = gondel:WaitForChild("Kern") :: BasePart
	local PIV = (pag:WaitForChild("AsFrame") :: CFrameValue).Value
	local JL = pag:GetAttribute("GondelLokaal") :: Vector3
	local DEK = 2.2 * S
	local function Jw(th: number): Vector3 return (PIV * CFrame.Angles(0, 0, th)):PointToWorldSpace(JL) end
	local lo, hi = math.rad(70), math.rad(120)
	for _ = 1, 50 do
		local m = (lo + hi) / 2
		if Jw(m).Y + DEK > Y_DEK then lo = m else hi = m end
	end
	local TH_D = (lo + hi) / 2
	local jd = Jw(TH_D)
	local CORR = Vector3.new(MIDDEN.X - jd.X, 0, MIDDEN.Z - jd.Z)
	local onder = CFrame.new(jd + CORR) * PIV.Rotation
	local delta = onder * kern.CFrame:Inverse()
	local delen, cfs = {}, {}
	for _, d in gondel:GetDescendants() do
		if d:IsA("BasePart") then d.Anchored = true; table.insert(delen, d); table.insert(cfs, delta * d.CFrame) end
	end
	workspace:BulkMoveTo(delen, cfs, Enum.BulkMoveMode.FireCFrameChanged)
end

pag:SetAttribute("RitStart", workspace:GetServerTimeNow())

local function iemandAanBoord(): boolean
	for _, plr in Players:GetPlayers() do
		local ch = plr.Character
		local hrp = ch and ch:FindFirstChild("HumanoidRootPart") :: BasePart?
		local hum = ch and ch:FindFirstChildOfClass("Humanoid")
		if hrp and hum and hum.Health > 0 then
			local p = hrp.Position
			local r = (Vector3.new(p.X, 0, p.Z) - MIDDEN).Magnitude
			if r < R_DEK and p.Y > Y_DEK and p.Y < Y_DEK + 9 then return true end
		end
	end
	-- NPC-bezoekers op het dek tellen ook (PagodeBezoekers: attribuut OpDek)
	local b = workspace:FindFirstChild("PagodeBezoekersActief")
	if b then for _, m in b:GetChildren() do if m:GetAttribute("OpDek") then return true end end end
	return false
end

while true do
	task.wait(0.25)
	local nu = workspace:GetServerTimeNow()
	local start = pag:GetAttribute("RitStart") :: number
	local tc = (nu - start) % CYCLUS
	if tc >= WACHT_TC and tc < WACHT_TC + 1 and not iemandAanBoord() then
		pag:SetAttribute("RitStart", nu - WACHT_TC)          -- klok vasthouden: hekjes blijven open tot er iemand instapt
	end
	pag:SetAttribute("Wacht", tc >= WACHT_TC and tc < WACHT_TC + 1)
end
