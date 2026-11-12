-- Langnek v4 (Daan: "veel dichter bebost, pad loopt niet zo ver, water loopt verder door"). Draaien NA plaats_langnek.luau.
-- 1) vervangt water, randstenen, hek, pad en opsluitband door asset OMG (03b: vijver ~50 graden verder om de rots, pad alleen
--    recht voor Langnek ~3.5 m breed; export: 09_export_roblox.py --alleen GEO_water,GEO_randstenen,GEO_hek,GEO_pad,GEO_opsluitband)
-- 2) kroos/rimpels opnieuw op het water
-- 3) dicht bos (Langnek_overview2014.jpg): ringen dennen / loof / struiken / ondergroei, nooit op pad, water, rand of bovenop de rots,
--    recht voor Langnek blijft open. Kleine planten zonder schaduw (fps 49 met / 54 zonder bos).
local OMG = 80458281867517
local m = workspace.Langnek
local ORIGIN = m.WorldPivot
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
for _, p in ipairs(m:GetChildren()) do
	if p.Name:find("MAT_water") or p.Name:find("TEX_rand") or p.Name:find("MAT_hek") or p.Name:find("MAT_klinker") or p.Name:find("MAT_band") or p.Name:find("MAT_randsteen") then p:Destroy() end
end
local tmp = Instance.new("Model")
for _, o in ipairs(game:GetObjects("rbxassetid://" .. OMG)) do o.Parent = tmp end
for _, d in ipairs(tmp:GetDescendants()) do if d:IsA("BasePart") then d.Parent = tmp end end
for _, d in ipairs(tmp:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
tmp.Parent = workspace; tmp:ScaleTo(S)
local anker; for _, p in ipairs(tmp:GetChildren()) do if p.Name:find("MAT_anker") then anker = p end end
tmp:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * tmp:GetPivot()); anker:Destroy()
local M = {water = {Color3.fromRGB(34, 40, 26), Enum.Material.SmoothPlastic}, randsteen = {Color3.fromRGB(170, 164, 150), Enum.Material.Limestone},
	hek = {Color3.fromRGB(28, 46, 32), Enum.Material.Metal}, klinker = {Color3.fromRGB(164, 152, 138), Enum.Material.Pavement}, band = {Color3.fromRGB(118, 116, 110), Enum.Material.Concrete}}
local water
for _, p in ipairs(tmp:GetChildren()) do
	local key = p.Name:match("__MAT_([%a_]+)_%d+$")
	p.Anchored = true; p.CanTouch = false; p.Color = M[key][1]; p.Material = M[key][2]
	p.CanCollide = key ~= "water"; p.CanQuery = true
	p:SetAttribute("Groep", "static")
	if key == "water" then water = p; p.Reflectance = 0.15; p.CastShadow = false; p.CFrame = p.CFrame + Vector3.new(0, 2.12 - p.Size.Y / 2 - p.Position.Y, 0) end
	if key == "klinker" or key == "band" then p.CastShadow = false end
	p.Parent = m
end
tmp:Destroy()
local wf = workspace.LangnekWater; wf:ClearAllChildren()
local bron = workspace.SprookjesboomWater
local kroosT, rimpelT = bron.Kroos, bron.Rimpelbron
local rng = Random.new(2013)
local scene = {}
for _, p in ipairs(m:GetChildren()) do if p:IsA("BasePart") and (p.Name:find("water") or p.Name:find("klinker") or p.Name:find("band") or p.Name:find("rots") or p.Name:find("randsteen") or p.Name:find("hek")) then table.insert(scene, p) end end
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = scene
local function onder(x, y) return workspace:Raycast(lokaal(x, y, 6).Position, Vector3.new(0, -30, 0), rp) end
local kn, rn = 0, 0
for _ = 1, 600 do
	local x, y = rng:NextNumber(-8, 8), rng:NextNumber(-8, 8)
	local h = onder(x, y)
	if h and h.Instance == water then
		if kn < 30 then
			local k = kroosT:Clone(); k.Anchored = true; k.CanCollide = false; k.CanQuery = false; k.CanTouch = false
			k.Size = Vector3.new(rng:NextNumber(1.6, 3.6), 0.02, rng:NextNumber(1.4, 3.0))
			k.CFrame = CFrame.new(h.Position + Vector3.new(0, 0.03, 0)) * CFrame.Angles(0, rng:NextNumber(0, 6.28), 0); k.Parent = wf; kn += 1
		elseif rn < 6 then
			local r = rimpelT:Clone(); r.Anchored = true; r.CFrame = CFrame.new(h.Position + Vector3.new(0, 0.05, 0)); r.Parent = wf; rn += 1
		end
	end
end
-- ===== dicht bos
local groen = workspace.LangnekGroen; groen:ClearAllChildren()
local V3 = game:GetService("ServerStorage").BomenBronV3; local ECHT = game:GetService("ServerStorage").VVEchtePlanten
local stammen, klein = {}, {}
local function grondVrij(x, y, r)
	for _, d in ipairs({{0, 0}, {r, 0}, {-r, 0}, {0, r}, {0, -r}}) do
		local h = onder(x + d[1], y + d[2])
		if h then
			local n = h.Instance.Name
			if n:find("klinker") or n:find("band") or n:find("water") or n:find("randsteen") or n:find("hek") then return false end
			if n:find("rots") and h.Position.Y > 2 + 1.5 * S then return false end
		end
	end
	return true
end
local function vrij(x, y, r, boom)
	for _, q in ipairs(stammen) do if (q[1] - x) ^ 2 + (q[2] - y) ^ 2 < (boom and q[3] or 0.9) ^ 2 then return false end end
	if not boom then for _, q in ipairs(klein) do if (q[1] - x) ^ 2 + (q[2] - y) ^ 2 < ((q[3] + r) * 0.75) ^ 2 then return false end end end
	return true
end
local function zet(bronM, x, y, schaal, boomAfst)
	local c = bronM:Clone(); c:ScaleTo(c:GetScale() * schaal)
	local cf, size = c:GetBoundingBox()
	local r = math.max(size.X, size.Z) / S * 0.45
	if not vrij(x, y, r, boomAfst ~= nil) or not grondVrij(x, y, boomAfst and 0.8 or r * 0.6) then c:Destroy(); return false end
	c:PivotTo(CFrame.new(lokaal(x, y, 0).Position + Vector3.new(0, size.Y / 2 - 0.15, 0)) * CFrame.Angles(0, rng:NextNumber(0, 6.28), 0) * cf:ToObjectSpace(c:GetPivot()))
	for _, d in ipairs(c:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Anchored = true; d.CanCollide = false; d.CanTouch = false
			if size.Y < 12 then d.CastShadow = false; d.CanQuery = false end   -- kleine planten zonder schaduw (fps)
		end
	end
	c.Parent = groen
	if boomAfst then table.insert(stammen, {x, y, boomAfst}) else table.insert(klein, {x, y, r}) end
	return true
end
local function vrijZicht(x, y) return not (y < -2 and math.abs(x) < 7.5) end
local function ring(n, rMin, rMax, lijst, sMin, sMax, boomAfst, pogingen)
	local k = 0
	for i = 1, pogingen do
		if k >= n then break end
		local a = rng:NextNumber(0, 2 * math.pi); local r = rng:NextNumber(rMin, rMax)
		local x, y = math.cos(a) * r, 0.3 + math.sin(a) * r
		if vrijZicht(x, y) and zet(lijst[rng:NextInteger(1, #lijst)], x, y, rng:NextNumber(sMin, sMax), boomAfst) then k += 1 end
		if i % 300 == 0 then task.wait() end
	end
	return k
end
local onderL = {}
for _, c in ipairs(ECHT:GetChildren()) do if c.Name:find("fern") or c.Name:find("shrub_03") or c.Name:find("shrub_02") or c.Name:find("shrub_04") then table.insert(onderL, c) end end
local nd = ring(26, 7.5, 17, {V3.den0, V3.den1}, 2.6, 3.4, 3.2, 2000)
local nl = ring(12, 13, 22, {V3.eik0, V3.eik1, V3.beuk0, V3.beuk1, V3.kastanje0, V3.kastanje1, V3.berk0, V3.berk1}, 2.8, 3.2, 5.0, 1500)
local ns = ring(55, 5.0, 12, {V3.taxus0, V3.taxus1, V3.rododendron0, V3.rododendron1, V3.struik0, V3.struik1}, 2.4, 3.2, nil, 4000)
local no = ring(120, 4.3, 13, onderL, 2.6, 3.8, nil, 6000)
print(string.format("Langnek v4: kroos %d rimpels %d; dennen %d loof %d struiken %d ondergroei %d", kn, rn, nd, nl, ns, no))
