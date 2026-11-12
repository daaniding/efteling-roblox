--!strict
-- Langnek: de nek rijst en daalt in een rustig tempo uit de kraag. Net als de echte is hij niet telescopisch:
-- de hele nek schuift (geleidebuis door lichaam en rots). Hoofd en ogen kijken heen en weer, los van elkaar (Eftepedia).
-- Het model staat in Studio met de nek UIT (zoals ref/front.jpg); NekOmlaag = slag in studs, OogStraal = iris -> oogcentrum.
local RunService = game:GetService("RunService")

local model = script.Parent :: Model
local OMLAAG = (model:GetAttribute("NekOmlaag") :: number?) or 16.65
local OOG_R = (model:GetAttribute("OogStraal") :: number?) or 0.49
local FWD = model.WorldPivot.LookVector

local nek, hoofd, irisL, irisR = {} :: { BasePart }, {} :: { BasePart }, {} :: { BasePart }, {} :: { BasePart }
for _, p in model:GetChildren() do
	if p:IsA("BasePart") then
		local g = p:GetAttribute("Groep")
		if g == "neck" then table.insert(nek, p)
		elseif g == "head" then table.insert(hoofd, p)
		elseif g == "irisL" then table.insert(irisL, p)
		elseif g == "irisR" then table.insert(irisR, p) end
	end
end
assert(#nek > 0 and #hoofd > 0, "Langnek: nek/hoofd-delen niet gevonden")

local orig: { [BasePart]: CFrame } = {}
for _, lijst in { nek, hoofd, irisL, irisR } do
	for _, p in lijst do orig[p] = p.CFrame end
end
-- draaipunt hoofd: op de nekas, op de hoogte van het grootste huiddeel van het hoofd
local groot = hoofd[1]
for _, p in hoofd do if p.Size.Magnitude > groot.Size.Magnitude then groot = p end end
local as = nek[1].Position
local P0 = Vector3.new(as.X, groot.Position.Y, as.Z)
local function oogMidden(lijst: { BasePart }): Vector3
	for _, p in lijst do
		if string.find(p.Name, "MAT_iris") then return p.Position - FWD * OOG_R end
	end
	return P0
end
local EL, ER = oogMidden(irisL), oogMidden(irisR)

local function zacht(t: number): number return t * t * (3 - 2 * t) end
-- cyclus (s): boven blijven 9, zakken 7, beneden 5, rijzen 7
local BOVEN, ZAK, BENEDEN, RIJS = 9, 7, 5, 7
local PERIODE = BOVEN + ZAK + BENEDEN + RIJS
local function rek(t: number): number
	local f = t % PERIODE
	if f < BOVEN then return 1 end
	f -= BOVEN
	if f < ZAK then return 1 - zacht(f / ZAK) end
	f -= ZAK
	if f < BENEDEN then return 0 end
	f -= BENEDEN
	return zacht(f / RIJS)
end

local parts: { BasePart } = {}
for p in orig do table.insert(parts, p) end
local groepen: { string } = {}
for i, p in parts do groepen[i] = p:GetAttribute("Groep") :: string end
local cfs: { CFrame } = table.create(#parts)
local t0 = os.clock()

RunService.Heartbeat:Connect(function()
	local t = os.clock() - t0
	local off = (rek(t) - 1) * OMLAAG
	local omhoog = Vector3.new(0, off, 0)
	-- hoofd: langzaam heen en weer; ogen: sneller en met een andere fase
	local yaw = math.rad(34) * math.sin(t * 0.42) + math.rad(6) * math.sin(t * 1.3)
	local oog = math.rad(16) * math.sin(t * 0.95 + 2.1)
	local T = CFrame.new(P0 + omhoog) * CFrame.Angles(0, yaw, 0) * CFrame.new(-P0)
	local TL = T * CFrame.new(EL) * CFrame.Angles(0, oog, 0) * CFrame.new(-EL)
	local TR = T * CFrame.new(ER) * CFrame.Angles(0, oog, 0) * CFrame.new(-ER)
	for i, p in parts do
		local g = groepen[i]
		if g == "neck" then cfs[i] = orig[p] + omhoog
		elseif g == "irisL" then cfs[i] = TL * orig[p]
		elseif g == "irisR" then cfs[i] = TR * orig[p]
		else cfs[i] = T * orig[p] end
	end
	workspace:BulkMoveTo(parts, cfs, Enum.BulkMoveMode.FireCFrameChanged)
end)
