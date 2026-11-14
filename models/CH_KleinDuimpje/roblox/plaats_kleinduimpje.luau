-- Klein Duimpje (1998): slapende reus (build/03a_reus.py, gebakken in 04_bake_reus.py) op een rotseiland met gracht (build/03b_omgeving.py).
-- Modelframe: oorsprong = OSM-punt Klein Duimpje (studs 435.33, -378.66), voorkant (rotsrand naar het plein, ZO) = -Y, x = lichaamsas (hoofd NO).
-- OSM voorkant (0.43, -0.90) -> Roblox F = (0.43, 0, 0.90). Grond Y = 2. Gracht = terreinwater (zelfde look als De Zes Zwanen).
local REUS = 118052864567342
local OMG = 124180200669734
local TEX = {lijf = 109002925862949, hoofd = 97456089053146}
local TEXO = {kalksteen = {76818249518539}, natuursteen = {83025593121539, 103046195882958}, schors = {125096061636527, 131548344593770}}
local F = Vector3.new(0.43, 0, 0.90).Unit
local ORIGIN = CFrame.new(435.33, 2.0, -378.66) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	messing = {Color3.fromRGB(196, 156, 76), "Metal"}, koper = {Color3.fromRGB(184, 128, 64), "Metal"}, papier = {Color3.fromRGB(232, 220, 186), "Fabric"},
	ijzer = {Color3.fromRGB(24, 24, 24), "Metal"}, bordgroen = {Color3.fromRGB(32, 76, 52), "WoodPlanks"}, binnen = {Color3.fromRGB(14, 10, 8), "SmoothPlastic"},
	water = {Color3.fromRGB(30, 40, 26), "SmoothPlastic"}, modder = {Color3.fromRGB(40, 32, 24), "Ground"}, hout = {Color3.fromRGB(70, 50, 34), "Wood"},
	kalksteen = {Color3.fromRGB(196, 186, 168), "Limestone"}, natuursteen = {Color3.fromRGB(150, 146, 136), "Slate"}, schors = {Color3.fromRGB(92, 76, 60), "Wood"},
}

local function laad(id, naam)
	local oud = workspace:FindFirstChild(naam); if oud then oud:Destroy() end
	local m = Instance.new("Model"); m.Name = naam
	for _, o in ipairs(game:GetObjects("rbxassetid://" .. id)) do o.Parent = m end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
	for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
	m.Parent = workspace; m:ScaleTo(S)
	local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
	if anker then m:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
	else m:PivotTo(ORIGIN) end
	return m
end

local function kleur(m, texmap)
	local bots = Instance.new("Folder"); bots.Name = "Botsing"; bots.Parent = m
	local onbekend = {}
	for _, p in ipairs(m:GetChildren()) do
		if not p:IsA("BasePart") then continue end
		p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = false
		if string.match(p.Name, "^COLL_") then
			p.Transparency = 1; p.CanCollide = true; p.CanQuery = true; p.CastShadow = false; p.Parent = bots
			if p:IsA("MeshPart") then p.CollisionFidelity = Enum.CollisionFidelity.Box end
			continue
		end
		local tex = string.match(p.Name, "__TEX_([%w_]-)_%d+$"); local key = string.match(p.Name, "__MAT_([%w_]-)_%d+$")
		if tex and texmap[tex] then
			p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.SmoothPlastic
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. texmap[tex][1]
			if texmap[tex][2] then sa.NormalMap = "rbxassetid://" .. texmap[tex][2] end
			sa.Parent = p
			pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end)
		elseif key and M[key] then
			p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
			if key == "water" or key == "modder" then p.Transparency = 1; p.CastShadow = false end   -- gracht = terreinwater
		else table.insert(onbekend, p.Name) end
	end
	return bots, onbekend
end

-- 1) reus (lijf + hoofd gebakken) en omgeving
local reus = laad(REUS, "KleinDuimpjeReus")
reus:PivotTo(ORIGIN * CFrame.new(-0.6 * S, 0, 0) * ORIGIN:Inverse() * reus:GetPivot())   -- 0.6 m naar het hoofdeinde: verste laars op de rotsen, niet in de gracht
local TR = {}; for k, v in pairs(TEX) do TR[k] = {v} end
local _, o1 = kleur(reus, TR)
for _, p in ipairs(reus:GetChildren()) do if p:IsA("MeshPart") then p.CanCollide = true; p.CanQuery = true; p.CollisionFidelity = Enum.CollisionFidelity.Hull end end
local omg = laad(OMG, "KleinDuimpjeOmgeving")
local bots, o2 = kleur(omg, TEXO)
reus.WorldPivot = ORIGIN * CFrame.new(-0.6 * S, 0, 0); omg.WorldPivot = ORIGIN

-- 2) gracht: terrein onder het OSM-waterpolygoon weg en terreinwater erin (oppervlak ~0.33 m onder het maaiveld)
local WATER = {{-3.31, -3.47}, {-6.26, -2.46}, {-4.72, 3.22}, {0.21, 5.82}, {5.61, 3.90}, {7.59, -1.95}, {4.16, -2.14}, {3.37, 2.00}, {0.40, 3.42}, {-2.96, 1.56}}   -- ref/osm_model.json (ring om het eiland)
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local T = workspace.Terrain; local cel = {}
for x = -8, 8, 0.4 do for y = -8, 8, 0.4 do
	if inside(x, y, WATER) then local p = lokaal(x, y, 0).Position; cel[math.floor(p.X / 4) .. "," .. math.floor(p.Z / 4)] = true end end end
local nw = 0
for k in pairs(cel) do local i, j = string.match(k, "(-?%d+),(-?%d+)"); i, j = tonumber(i), tonumber(j)
	T:FillBlock(CFrame.new(i * 4 + 2, 4, j * 4 + 2), Vector3.new(4, 16, 4), Enum.Material.Air)
	T:FillBlock(CFrame.new(i * 4 + 2, -1.5, j * 4 + 2), Vector3.new(4, 5, 4), Enum.Material.Water)
	T:FillBlock(CFrame.new(i * 4 + 2, -6, j * 4 + 2), Vector3.new(4, 4, 4), Enum.Material.Ground); nw += 1 end

-- 3) layout-label weg, texturen voorladen
local L = workspace:FindFirstChild("EftelingLayout"); local mk = L and L:FindFirstChild("Klein Duimpje", true)
if mk then mk:Destroy() end
local decs = {}
for _, t in pairs(TEX) do local d = Instance.new("Decal"); d.Texture = "rbxassetid://" .. t; table.insert(decs, d) end
for _, t in pairs(TEXO) do for _, id in ipairs(t) do local d = Instance.new("Decal"); d.Texture = "rbxassetid://" .. id; table.insert(decs, d) end end
pcall(function() game:GetService("ContentProvider"):PreloadAsync(decs) end)
local function onb(t) return #t > 0 and table.concat(t, ",") or "-" end
return string.format("reus %d delen, omgeving %d (botsing %d), gracht %d cellen; onbekend %s %s", #reus:GetChildren(), #omg:GetChildren(), #bots:GetChildren(), nw, onb(o1), onb(o2))
