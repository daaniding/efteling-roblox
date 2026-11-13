-- De Magische Klok: grasoevers langs de westgracht (Herauten-overzicht-okt2009: begroeide oevers, riet in het water, blad en kroos op het water).
-- Terrein in de grachtstrook Ground -> LeafyGrass; riet/siergras op de waterrand, varens en bodembedekkers op de oevers en tussen de sokkels,
-- kroosplekken (bron SprookjesboomWater.Kroos, zoals Langnek) en gevallen blaadjes op het water. Map workspace.MagischeKlokOever.
local F = Vector3.new(-0.855, 0, -0.518)
local ORIGIN = CFrame.new(169.32, 2.0, -159.75) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local rng = Random.new(2009)
local ss = game:GetService("ServerStorage"); local ECHT, VV = ss.VVEchtePlanten, ss.VVPlanten
local f = workspace:FindFirstChild("MagischeKlokOever") or Instance.new("Folder"); f.Name = "MagischeKlokOever"; f.Parent = workspace; f:ClearAllChildren()
local p0 = Vector2.new(0.96, -3.07) - Vector2.new(-0.7154, -0.6986) * 1.2; local u, n = Vector2.new(0.6986, -0.7154), Vector2.new(-0.7154, -0.6986)
local L = 17.25; local HER = {2.8, 5.3, 7.8}
local function P(s, t) local q = p0 + u * s + n * t; return q end
local WATER_Y = 2 + (-0.2) * S
-- 1. terrein: grasoevers
local T = workspace.Terrain
for s = -0.5, L + 1, 1.0 do for t = -0.3, 4.2, 1.0 do
	local q = P(s, t); local p = lokaal(q.X, q.Y, 0).Position
	local r = Region3.new(Vector3.new(p.X - 2, -8, p.Z - 2), Vector3.new(p.X + 2, 4, p.Z + 2)):ExpandToGrid(4)
	T:ReplaceMaterial(r, 4, Enum.Material.Ground, Enum.Material.LeafyGrass); T:ReplaceMaterial(r, 4, Enum.Material.Mud, Enum.Material.LeafyGrass)
end end
local params = RaycastParams.new(); params.FilterType = Enum.RaycastFilterType.Include; params.FilterDescendantsInstances = {T}
local function grond(q) local p = lokaal(q.X, q.Y, 0).Position; local h = workspace:Raycast(p + Vector3.new(0, 20, 0), Vector3.new(0, -40, 0), params); return h and h.Position.Y or WATER_Y end
local function zet(bron, q, schaal, y)
	local c = bron:Clone(); c:ScaleTo(c:GetScale() * schaal); local cf, size = c:GetBoundingBox()
	local p = lokaal(q.X, q.Y, 0).Position
	c:PivotTo(CFrame.new(Vector3.new(p.X, (y or grond(q)) + size.Y / 2 - 0.12, p.Z)) * CFrame.Angles(0, rng:NextNumber(0, 6.28), 0) * cf:ToObjectSpace(c:GetPivot()))
	for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") then d.Anchored = true; d.CanCollide = false; d.CanTouch = false; d.CastShadow = false; d.CanQuery = false end end
	c.Parent = f
end
local function pick(folder, pat) local t = {}; for _, c in ipairs(folder:GetChildren()) do if c.Name:find(pat) then table.insert(t, c) end end; return t end
local RIET = {VV.siergras0, VV.siergras1, VV.siergras0}; for _, c in ipairs(pick(ECHT, "bermuda")) do table.insert(RIET, c) end
local VAREN = pick(ECHT, "fern"); table.insert(VAREN, VV.varen0); table.insert(VAREN, VV.varen1)
local BODEM = pick(ECHT, "periwinkle"); table.insert(BODEM, VV.bodem0); table.insert(BODEM, VV.bodem1); for _, c in ipairs(pick(ECHT, "nettle")) do table.insert(BODEM, c) end
local nR, nV, nB = 0, 0, 0
-- 2. riet in pollen op beide waterranden (het water loopt van t 1.05 tot 2.25)
for i = 1, 70 do
	local s = rng:NextNumber(1.3, L - 0.6); local kant = rng:NextNumber() < 0.6 and 2.15 or 1.15
	for k = 1, rng:NextInteger(2, 5) do
		zet(RIET[rng:NextInteger(1, #RIET)], P(s + rng:NextNumber(-0.25, 0.25), kant + rng:NextNumber(-0.1, 0.1)), rng:NextNumber(1.3, 2.1), WATER_Y - 0.1); nR += 1
	end
end
-- 3. varens en bodembedekkers op de pleinoever (t 2.4..3.6) en tussen de sokkels (t 0.2..0.95), sokkels vrij
for i = 1, 500 do
	local s = rng:NextNumber(0.6, L); local t = rng:NextNumber() < 0.65 and rng:NextNumber(2.4, 3.6) or rng:NextNumber(0.25, 0.95)
	local vrij = true; if t < 1 then for _, h in ipairs(HER) do if math.abs(s - h) < 0.6 then vrij = false end end end
	if vrij then
		if rng:NextNumber() < 0.4 then if nV < 70 then zet(VAREN[rng:NextInteger(1, #VAREN)], P(s, t), rng:NextNumber(1.3, 2.0)); nV += 1 end
		elseif nB < 120 then zet(BODEM[rng:NextInteger(1, #BODEM)], P(s, t), rng:NextNumber(1.0, 1.6)); nB += 1 end
	end
	if i % 100 == 0 then task.wait() end
end
-- 4. kroos en gevallen blaadjes op het water
local bron = workspace:FindFirstChild("SprookjesboomWater"); local kroosT = bron and bron:FindFirstChild("Kroos")
local nK, nL = 0, 0
for i = 1, 40 do
	local q = P(rng:NextNumber(1.6, L - 0.8), rng:NextNumber(1.2, 2.1)); local p = lokaal(q.X, q.Y, 0).Position
	local k
	if kroosT then k = kroosT:Clone() else k = Instance.new("Part"); k.Material = Enum.Material.Grass; k.Color = Color3.fromRGB(86, 112, 44) end
	k.Anchored = true; k.CanCollide = false; k.CanQuery = false; k.CanTouch = false; k.CastShadow = false
	k.Size = Vector3.new(rng:NextNumber(0.8, 2.6), 0.02, rng:NextNumber(0.6, 1.6))
	k.CFrame = CFrame.new(p.X, WATER_Y + 0.03, p.Z) * CFrame.Angles(0, rng:NextNumber(0, 6.28), 0); k.Parent = f; nK += 1
end
local KLEUR = {Color3.fromRGB(96, 70, 36), Color3.fromRGB(112, 84, 40), Color3.fromRGB(78, 58, 32), Color3.fromRGB(80, 88, 40)}
for i = 1, 100 do                                                            -- kleine donkere ronde blaadjes (geen felle vierkantjes)
	local q = P(rng:NextNumber(1.4, L - 0.6), rng:NextNumber(1.1, 2.2)); local p = lokaal(q.X, q.Y, 0).Position; local d = rng:NextNumber(0.16, 0.3)
	local b = Instance.new("Part"); b.Anchored = true; b.CanCollide = false; b.CanQuery = false; b.CanTouch = false; b.CastShadow = false
	b.Shape = Enum.PartType.Cylinder; b.Material = Enum.Material.SmoothPlastic; b.Color = KLEUR[rng:NextInteger(1, #KLEUR)]
	b.Size = Vector3.new(0.02, d, d * rng:NextNumber(0.6, 0.85))
	b.CFrame = CFrame.new(p.X, WATER_Y + 0.04, p.Z) * CFrame.Angles(0, rng:NextNumber(0, 6.28), 0) * CFrame.Angles(0, 0, math.rad(90)); b.Name = "Blad"; b.Parent = f; nL += 1
end
return string.format("riet %d, varens %d, bodem %d, kroos %d (%s), blaadjes %d", nR, nV, nB, nK, kroosT and "bron" or "eigen", nL)
