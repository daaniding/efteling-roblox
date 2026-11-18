--!strict
-- ParkBezoekers (ModuleScript in ServerScriptService): alle NPC-bezoekers van het park en hun rondgang.
-- Daan 17 nov: "over heel het park gaat iedereen 1 voor 1 elke attractie langs: begin je bij de Pagode, dan ga je door naar de
-- volgende; begin je bij de attractie vóór de Pagode, dan ga je daarna naar de Pagode" en "elke attractie spawnt aan het begin
-- van de server zoveel mensen als past bij hoe groot ze is".
--
-- Werking:
--   VOLGORDE  = de vaste rondgang door het park (namen); na de laatste weer de eerste. Nieuwe attractie: op haar plek invoegen.
--   aantal()  = hoeveel bezoekers een attractie bij de serverstart neerzet (basis x DICHTHEID).
--   maak()    = één bezoeker (willekeurig sjabloon uit ServerStorage.PagodeBezoekers), klaar om te lopen.
--   registreer(naam, {ingang, ontvang}) = attractie doet mee; ontvang(model) neemt een aankomende bezoeker over (rij, rit, uitgang).
--   naarVolgende(naam, model) = na de uitgang: lopen (pathfinding) naar de ingang van de volgende attractie en daar afgeven.
-- Bezoekers verdwijnen niet; het aantal in het park blijft dus gelijk.
local ServerStorage = game:GetService("ServerStorage")
local PathfindingService = game:GetService("PathfindingService")

local M = {}
M.DICHTHEID = 1.0                 -- één knop voor het hele park (bijv. 0.6 als het op zwakke apparaten te zwaar wordt)
M.SNELHEID = 6.5                  -- bezoekers en spelers lopen precies even snel (studs/s)
M.VOLGORDE = {"Pagode", "Sirocco"} -- rondgang (Daan: de Sirocco na de Pagode); nieuwe attractie op haar plek invoegen
local ANIM = {loop = "rbxassetid://913402848", stil = "rbxassetid://507766388"}   -- standaard R15 lopen / stilstaan

type Info = {ingang: Vector3, ontvang: (Model) -> ()}
local attracties: {[string]: Info} = {}

local onderweg = workspace:FindFirstChild("BezoekersOnderweg") or Instance.new("Folder")
onderweg.Name = "BezoekersOnderweg"; onderweg.Parent = workspace

function M.aantal(basis: number): number
	return math.max(1, math.floor(basis * M.DICHTHEID + 0.5))
end

function M.registreer(naam: string, info: Info)
	attracties[naam] = info
end

function M.animeer(hum: Humanoid)
	local animator = hum:FindFirstChildOfClass("Animator") or Instance.new("Animator", hum)
	local function laad(id: string)
		local a = Instance.new("Animation"); a.AnimationId = id
		return (animator :: Animator):LoadAnimation(a)
	end
	local loop, stil = laad(ANIM.loop), laad(ANIM.stil)
	stil.Looped = true; loop.Looped = true; stil:Play()
	hum.Running:Connect(function(v)
		if v > 0.5 then
			if not loop.IsPlaying then stil:Stop(0.3); loop:Play(0.3) end
			loop:AdjustSpeed(v / 8)
		elseif loop.IsPlaying then loop:Stop(0.3); stil:Play(0.3) end
	end)
end

-- één nieuwe bezoeker op plek cf, in map (de map van de attractie waar hij begint)
function M.maak(cf: CFrame, map: Instance): Model?
	local bron = ServerStorage:FindFirstChild("PagodeBezoekers")
	local lijst = {}
	if bron then for _, m in bron:GetChildren() do if m:IsA("Model") and m:FindFirstChildOfClass("Humanoid") then table.insert(lijst, m) end end end
	if #lijst == 0 then return nil end
	local m = lijst[math.random(#lijst)]:Clone()
	local hum = m:FindFirstChildOfClass("Humanoid")
	if not hum then m:Destroy(); return nil end
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			d.Anchored = false; d.CollisionGroup = "Bezoekers"; d.CanTouch = false
			d.CustomPhysicalProperties = PhysicalProperties.new(100, 0.4, 0.3)     -- zwaar: een speler duwt ze niet weg
		end
		if d:IsA("Script") or d:IsA("LocalScript") then d:Destroy() end
	end
	hum.WalkSpeed = M.SNELHEID
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	m:PivotTo(cf)
	m.Parent = map
	for _, d in m:GetDescendants() do if d:IsA("BasePart") then pcall(function() d:SetNetworkOwner(nil) end) end end
	M.animeer(hum)
	return m
end

-- lopen naar doel: pathfinding (om hekken en gebouwen heen), anders rechtdoor; vloeiend van punt naar punt
local function loopNaar(m: Model, doel: Vector3)
	local hum = m:FindFirstChildOfClass("Humanoid")
	local h = m:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not hum or not h then return end
	local pad = PathfindingService:CreatePath({AgentRadius = 2, AgentHeight = 6, AgentCanJump = false, WaypointSpacing = 8})
	local ok = pcall(function() pad:ComputeAsync(h.Position, doel) end)
	local punten: {Vector3} = {}
	if ok and pad.Status == Enum.PathStatus.Success then
		for _, w in pad:GetWaypoints() do table.insert(punten, w.Position) end
	else
		punten = {doel}
	end
	for i, p in punten do
		hum:MoveTo(p)
		local t0 = os.clock()
		local marge = if i == #punten then 1.5 else 3
		while m.Parent and os.clock() - t0 < 10 and Vector3.new(h.Position.X - p.X, 0, h.Position.Z - p.Z).Magnitude > marge do
			task.wait(0.1)
		end
	end
end

-- na de uitgang van 'huidig': naar de volgende attractie in de rondgang (bij één attractie: weer dezelfde)
function M.naarVolgende(huidig: string, m: Model)
	local n = #M.VOLGORDE
	local i = table.find(M.VOLGORDE, huidig) or 0
	for k = 1, n do
		local naam = M.VOLGORDE[(i + k - 1) % n + 1]
		local a = attracties[naam]
		if a then
			m.Parent = onderweg
			loopNaar(m, a.ingang)
			if m.Parent then a.ontvang(m) end
			return
		end
	end
end

function M.totaal(): number
	local n = #onderweg:GetChildren()
	for _, d in workspace:GetChildren() do if d:IsA("Folder") and string.find(d.Name, "BezoekersActief") then n += #d:GetChildren() end end
	return n
end

return M
