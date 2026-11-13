-- De Magische Klok: klokkentoren + kantelenmuren + slotgrachtje + sokkels + voorgrondmuurtje. Asset uit build/09_export_roblox.py.
-- Model: klok kijkt naar -Y (WNW), +X = ZZW, oorsprong = midden toren, z=0 maaiveld (asset-brief.md).
-- Kalibratie: oorsprong = OSM (56.44, 53.25) m = studs (169.32, -159.75); kijkrichting Roblox (-0.855, 0, -0.518); grond Y=2.
-- Botsing: onzichtbare COLL_-blokken (map Botsing). Herauten: aparte map Herauten (zelfde asset, groep heraut).
local MODEL = 90334417357517
local COLL = {{1.653, 0.0, 2.2, 0.85, 0.5, 4.4, 90.0}, {1.5268499999999998, 0.63249, 2.2, 0.85, 0.5, 4.4, 112.5}, {1.16928, 1.16928, 2.2, 0.85, 0.5, 4.4, 135.0}, {0.63249, 1.5268499999999998, 2.2, 0.85, 0.5, 4.4, 157.5}, {0.0, 1.653, 2.2, 0.85, 0.5, 4.4, 180.0}, {-0.63249, 1.5268499999999998, 2.2, 0.85, 0.5, 4.4, 202.5}, {-1.16928, 1.16928, 2.2, 0.85, 0.5, 4.4, 225.0}, {-1.5268499999999998, 0.63249, 2.2, 0.85, 0.5, 4.4, 247.5}, {-1.653, 0.0, 2.2, 0.85, 0.5, 4.4, 270.0}, {-1.5268499999999998, -0.63249, 2.2, 0.85, 0.5, 4.4, 292.5}, {-1.16928, -1.16928, 2.2, 0.85, 0.5, 4.4, 315.0}, {-0.63249, -1.5268499999999998, 2.2, 0.85, 0.5, 4.4, 337.5}, {-0.0, -1.653, 2.2, 0.85, 0.5, 4.4, 360.0}, {0.63249, -1.5268499999999998, 2.2, 0.85, 0.5, 4.4, 382.5}, {1.16928, -1.16928, 2.2, 0.85, 0.5, 4.4, 405.0}, {1.5268499999999998, -0.63249, 2.2, 0.85, 0.5, 4.4, 427.5}, {-5.953, -5.609, 2.0, 18.65, 0.6, 4.0, -134.384}, {6.556, -6.725, 2.0, 21.45, 0.6, 4.0, -45.681}, {3.518, -13.469, 1.3, 1.144, 0.4, 2.6, 117.5}, {2.924, -12.621, 1.3, 1.144, 0.4, 2.6, 132.5}, {2.131, -11.955, 1.3, 1.144, 0.4, 2.6, 147.5}, {1.193, -11.518, 1.3, 1.144, 0.4, 2.6, 162.5}, {0.173, -11.338, 1.3, 1.144, 0.4, 2.6, 177.5}, {-0.858, -11.428, 1.3, 1.144, 0.4, 2.6, -167.5}, {-1.831, -11.782, 1.3, 1.144, 0.4, 2.6, -152.5}, {-2.679, -12.376, 1.3, 1.144, 0.4, 2.6, -137.5}, {-3.345, -13.169, 1.3, 1.144, 0.4, 2.6, -122.5}}   -- [cx, cy, cz, sx, sy, sz, hoek] in modelmeters, ingevuld uit exports/klok_extra.json (maak_plaatsscript.py)
local TEX = {baksteen_detail = {108979434028974, 112282749940764}, baksteen_toren = {70970170035341, 98757760719558}, klok = {127168149551485}, leien = {113242851985008, 91109038076936}, ruiter = {117001844464393}, steen = {82997977649814}, stuc_N = {111877303736600, 119192160525210}, stuc_W = {87242237772715, 76750031041242}}   -- wordt ingevuld door roblox/maak_plaatsscript.py
local F = Vector3.new(-0.855, 0, -0.518)
local ORIGIN = CFrame.new(169.32, 2.0, -159.75) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	kern = {Color3.fromRGB(138, 140, 138), "Plaster"}, lood = {Color3.fromRGB(112, 116, 118), "Metal"}, ijzer = {Color3.fromRGB(26, 30, 30), "Metal"},
	brons = {Color3.fromRGB(110, 90, 58), "Metal"}, goud = {Color3.fromRGB(214, 168, 72), "Metal"}, pannen = {Color3.fromRGB(150, 84, 64), "ClayRoofTiles"},
	klokhout = {Color3.fromRGB(46, 86, 82), "Wood"}, hout = {Color3.fromRGB(36, 78, 60), "Wood"}, rood = {Color3.fromRGB(176, 34, 28), "SmoothPlastic"},
	bodem = {Color3.fromRGB(70, 58, 42), "Ground"}, water = {Color3.fromRGB(46, 56, 36), "Glass"}, klinker = {Color3.fromRGB(128, 122, 114), "Cobblestone", "EftelingKlinkers"},
	toon_groen = {Color3.fromRGB(70, 112, 96), "SmoothPlastic"}, toon_rood = {Color3.fromRGB(190, 92, 70), "SmoothPlastic"},
	huid = {Color3.fromRGB(226, 182, 150), "SmoothPlastic"}, haar = {Color3.fromRGB(214, 168, 90), "SmoothPlastic"},
}
local GEEN_SCHADUW = {water = true, bodem = true, klinker = true, ijzer = true}
local BOTSEN = {klinker = true}

local function plaats(asset, naam)
	local oud = workspace:FindFirstChild(naam); if oud then oud:Destroy() end
	local m = Instance.new("Model"); m.Name = naam
	for _, o in ipairs(game:GetObjects("rbxassetid://" .. asset)) do o.Parent = m end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
	for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
	m.Parent = workspace; m:ScaleTo(S)
	local anker
	for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
	local told = CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0))
	m:PivotTo(ORIGIN * told:Inverse() * m:GetPivot()); anker:Destroy()
	local bots = Instance.new("Folder"); bots.Name = "Botsing"; bots.Parent = m
	local onbekend = {}
	for _, p in ipairs(m:GetChildren()) do
		if not p:IsA("BasePart") then continue end
		p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = true
		if string.match(p.Name, "^COLL_") then
			p.Transparency = 1; p.CanCollide = true; p.CastShadow = false; p.Parent = bots
			if p:IsA("MeshPart") then p.CollisionFidelity = Enum.CollisionFidelity.Box end
		else
			local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$")
			local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
			if tex and TEX[tex] then
				p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
				local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
				if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
				if tex == "ruiter" then sa.AlphaMode = Enum.AlphaMode.Transparency; p.CastShadow = false end
				sa.Parent = p
			elseif key and M[key] then
				local s = M[key]; p.Color = s[1]; p.Material = Enum.Material[s[2]]; if s[3] then p.MaterialVariant = s[3] end
				if GEEN_SCHADUW[key] then p.CastShadow = false end
				if BOTSEN[key] then p.CanCollide = true; if p:IsA("MeshPart") then p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end end
				if key == "water" then p.Transparency = 0.2; p.Reflectance = 0.15 end
			else table.insert(onbekend, p.Name) end
		end
	end
	m.WorldPivot = ORIGIN
	return m, onbekend
end

local klok, o1 = plaats(MODEL, "MagischeKlok")
-- botsblokken als echte Parts (een geexporteerde schuine kubus wordt in Roblox een rechte doos om de hele diagonaal)
klok.Botsing:ClearAllChildren()
for i, c in ipairs(COLL) do
	local b = Instance.new("Part"); b.Name = "COLL_" .. i; b.Anchored = true; b.CanCollide = true; b.CanTouch = false; b.CanQuery = false
	b.Transparency = 1; b.CastShadow = false; b.Size = Vector3.new(c[4] * S, c[6] * S, c[5] * S)
	b.CFrame = lokaal(c[1], c[2], c[3]) * CFrame.Angles(0, math.rad(c[7]) + math.pi, 0)   -- model-hoek a: lokaal X-as = (-cos a, 0, sin a)
	b.Parent = klok.Botsing
end
-- stucmuren, sokkels en muurtje botsen ook op de mesh (naast de hoge COLL-blokken)
for _, p in ipairs(klok:GetChildren()) do
	if p:IsA("MeshPart") and (string.find(p.Name, "TEX_stuc") or string.find(p.Name, "TEX_baksteen") or string.find(p.Name, "TEX_steen")) then
		p.CanCollide = true; p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition
	end
end
-- geen zwevend layout-label bij gebouwde dingen (Daan)
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do if d:IsA("BillboardGui") and d.Parent and string.find(string.lower(d.Parent.Name), "klok") then d:Destroy() end end end
-- bomen/planten van andere scenes en de horizon in het gebied weghalen
local weg = 0
local function binnen(p) local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S; return x > -15 and x < 17 and y > -20 and y < 6 end
for _, naam in ipairs({"VillaVoltaHorizon", "HansEnGrietjeGroen", "AssepoesterGroen", "SneeuwwitjeGroen"}) do
	local f = workspace:FindFirstChild(naam)
	if f then for _, t in ipairs(f:GetChildren()) do
		local p = t:IsA("Model") and t:GetPivot().Position or (t:IsA("BasePart") and t.Position)
		if p and binnen(p) then t:Destroy(); weg += 1 end
	end end
end
-- terrein: gracht uitgraven (lucht boven de grachtbak), gras onder muren/gracht/klinkers -> Ground
local T = workspace.Terrain
local ARMS = {
	N = {Vector2.new(-1.33, -2.96), Vector2.new(-0.6997, -0.7149), Vector2.new(0.7149, -0.6997), 14.45},
	W = {Vector2.new(0.96, -3.07), Vector2.new(0.6986, -0.7154), Vector2.new(-0.7154, -0.6986), 17.25},
}
for _, a in pairs(ARMS) do
	local p0 = a[1] - a[3] * 1.2; local u, n, L = a[2], a[3], a[4]
	local g0, g1 = 1.4, L - 0.4
	local c = p0 + u * ((g0 + g1) / 2) + n * 1.65
	local cf = lokaal(c.X, c.Y, -0.1) * CFrame.Angles(0, math.atan2(-u.Y, -u.X), 0)   -- lokaal X = -model x, lokaal Z = model y
	T:FillBlock(cf * CFrame.new(0, 0.6, 0), Vector3.new((g1 - g0) * S, 4.4, math.max(1.45 * S, 4.4)), Enum.Material.Air)   -- terreinraster is 4 studs: ruim uitgraven
end
for x = -15, 17, 1.3 do for y = -20, 4, 1.3 do
	local p = lokaal(x, y, 0).Position
	local r = Region3.new(Vector3.new(p.X - 2, -4, p.Z - 2), Vector3.new(p.X + 2, 4, p.Z + 2)):ExpandToGrid(4)
	T:ReplaceMaterial(r, 4, Enum.Material.Grass, Enum.Material.Ground); T:ReplaceMaterial(r, 4, Enum.Material.LeafyGrass, Enum.Material.Ground)
end end
local ids = {}
for _, sa in ipairs(klok:GetDescendants()) do if sa:IsA("SurfaceAppearance") then
	for _, id in ipairs({sa.ColorMap, sa.NormalMap}) do if id ~= "" then local d = Instance.new("Decal"); d.Texture = id; table.insert(ids, d) end end end end
task.spawn(function() pcall(function() game:GetService("ContentProvider"):PreloadAsync(ids) end) end)
return string.format("klok %d delen, botsblokken %d, %d planten weg; onbekend: %s", #klok:GetChildren(), #klok.Botsing:GetChildren(), weg, table.concat(o1, ","))
