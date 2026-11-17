--!strict
-- ParkBezoekers (ModuleScript in ServerScriptService): één budget voor alle NPC-bezoekers in het hele park (Daan 17 nov:
-- "hoe zorgen we dat er niet te veel mensen komen, met veel attracties wordt het te veel").
-- Elke attractie met NPC's (nu: PagodeBezoekers) registreert zich en vraagt vóór elke nieuwe bezoeker magErBij().
-- Regels:
--   1 parklimiet: BASIS + PER_SPELER per speler, nooit boven MAX (alle attracties samen);
--   2 per attractie een eigen maximum (een drukke attractie kan niet het hele budget opeten);
--   3 park-breed hooguit één nieuwe bezoeker per SPAWN_TUSSEN seconden (geen golf mensen tegelijk);
--   4 alleen bij een attractie waar binnen ZICHT studs een speler is (geen rekenkracht waar niemand kijkt).
-- Bezoekers verdwijnen niet; ze lopen na de rit verder (later: naar een andere attractie via bestemming()).
local Players = game:GetService("Players")

local M = {}
M.BASIS = 20
M.PER_SPELER = 8
M.MAX = 60
M.SPAWN_TUSSEN = 3
M.ZICHT = 450

type Attractie = {map: Instance, max: number, plek: Vector3}
local attracties: {[string]: Attractie} = {}
local laatste = -math.huge

function M.registreer(naam: string, map: Instance, maxEigen: number, plek: Vector3)
	attracties[naam] = {map = map, max = maxEigen, plek = plek}
end

function M.limiet(): number
	return math.min(M.MAX, M.BASIS + M.PER_SPELER * #Players:GetPlayers())
end

function M.totaal(): number
	local n = 0
	for _, a in attracties do n += #a.map:GetChildren() end
	return n
end

local function spelerInBuurt(p: Vector3): boolean
	for _, plr in Players:GetPlayers() do
		local h = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart") :: BasePart?
		if h and (h.Position - p).Magnitude < M.ZICHT then return true end
	end
	return false
end

function M.magErBij(naam: string): boolean
	local a = attracties[naam]
	if not a then return false end
	if #a.map:GetChildren() >= a.max then return false end
	if M.totaal() >= M.limiet() then return false end
	if os.clock() - laatste < M.SPAWN_TUSSEN then return false end
	if not spelerInBuurt(a.plek) then return false end
	laatste = os.clock()
	return true
end

return M
