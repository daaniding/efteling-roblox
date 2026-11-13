-- Hans en Grietje: snoephuisje (stuc gebakken per gevel, pannenkoekatlas, snoepatlas) + voortuin. Assets uit build/09_export_roblox.py.
-- Model: gevel kijkt naar -Y (WNW), +X = rechts (ZZO), oorsprong = midden BAG-footprint, z=0 maaiveld.
-- Kalibratie (asset-brief.md): oorsprong = OSM (66.81, 27.48) m = studs (200.43, -82.44); kijkrichting Roblox (-0.944, 0, -0.332); grond Y=2.
-- Botsing: onzichtbare COLL_-blokken (map Botsing). Lampen: LAMP_ -> PointLight.
local HUIS = 139382073870455
local OMG = 88575539670713
local TEX = {pannenkoek = {75733789969526}, snoep = {116416741730115}, snoepomg = {116416741730115}, stuc_achter = {92015225526568, 128901005308082}, stuc_noord = {104906801297171, 109862843342181}, stuc_tuin = {115467324969473, 103737251238288}, stuc_voor = {109318122648105, 104324566879797}, stuc_zuid = {137577513753329, 126230881043910}}   -- wordt ingevuld door roblox/maak_plaatsscript.py
local F = Vector3.new(-0.944, 0, -0.332)
local ORIGIN = CFrame.new(200.43, 2.0, -82.44) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	dakbasis = {Color3.fromRGB(142, 88, 46), "SmoothPlastic"}, ijzer = {Color3.fromRGB(40, 52, 50), "Metal"}, glas = {Color3.fromRGB(30, 36, 34), "Glass"},
	lood = {Color3.fromRGB(58, 60, 60), "Metal"}, donker = {Color3.fromRGB(8, 7, 6), "SmoothPlastic"}, vuur = {Color3.fromRGB(255, 130, 40), "Neon"},
	teal = {Color3.fromRGB(60, 94, 90), "SmoothPlastic"}, pad = {Color3.fromRGB(150, 142, 130), "Pebble", "VV_Grind"},
	aarde = {Color3.fromRGB(96, 72, 52), "Ground"}, grind = {Color3.fromRGB(235, 228, 214), "Pebble", "VV_Grind"},
	tegels = {Color3.fromRGB(150, 146, 136), "Slate"}, steen = {Color3.fromRGB(168, 166, 160), "Concrete"}, limonade = {Color3.fromRGB(196, 40, 50), "Glass"},
	pannen = {Color3.fromRGB(150, 78, 58), "ClayRoofTiles"}, hout = {Color3.fromRGB(96, 64, 40), "Wood"}, papier = {Color3.fromRGB(236, 226, 196), "SmoothPlastic"},
	snoeppad = {Color3.fromRGB(238, 232, 218), "Plaster"}, reling = {Color3.fromRGB(40, 78, 66), "Metal"}, terracotta = {Color3.fromRGB(170, 92, 62), "Concrete"},
	hekwit = {Color3.fromRGB(238, 236, 228), "Wood"},
}
local GEEN_SCHADUW = {donker = true, vuur = true, papier = true, lood = true, glas = true, pad = true, aarde = true, grind = true, snoeppad = true, tegels = true}
local BOTSEN = {pad = true, grind = true, tegels = true, snoeppad = true}   -- loopvlakken (meshes zijn dun)

local function plaats(asset, naam)
	local oud = workspace:FindFirstChild(naam); local figuren = oud and oud:FindFirstChild("Figuren")   -- vogels (generate_mesh) bewaren
	if figuren then figuren.Parent = nil end
	if oud then oud:Destroy() end
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
	local lampen = Instance.new("Folder"); lampen.Name = "Lampen"; lampen.Parent = m
	local onbekend = {}
	for _, p in ipairs(m:GetChildren()) do
		if not p:IsA("BasePart") then continue end
		p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = true
		if string.match(p.Name, "^COLL_") then
			p.Transparency = 1; p.CanCollide = true; p.CastShadow = false; p.Parent = bots
			if p:IsA("MeshPart") then p.CollisionFidelity = Enum.CollisionFidelity.Box end
		elseif string.match(p.Name, "^LAMP_") then
			p.Transparency = 1; p.CastShadow = false; p.CanQuery = false; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Name = "Lamp"; p.Parent = lampen
			local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 120); pl.Range = 12; pl.Brightness = 1.2; pl.Shadows = false; pl.Parent = p
		else
			local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$")
			local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
			if tex and TEX[tex] then
				p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
				local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
				if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
				if tex == "pannenkoek" then sa.Color = Color3.fromRGB(236, 218, 200) end   -- iets minder fel (Daan-check foto)
				sa.Parent = p
				if tex == "snoep" or tex == "snoepomg" then p.CastShadow = false end
			elseif key and M[key] then
				local s = M[key]; p.Color = s[1]; p.Material = Enum.Material[s[2]]; if s[3] then p.MaterialVariant = s[3] end
				if GEEN_SCHADUW[key] then p.CastShadow = false end
				if BOTSEN[key] then p.CanCollide = true; if p:IsA("MeshPart") then p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end end
				if key == "limonade" then p.Transparency = 0.15; p.Reflectance = 0.1 end
				if key == "glas" then p.Transparency = 0.1; p.Reflectance = 0.15 end
			else table.insert(onbekend, p.Name) end
		end
	end
	m.WorldPivot = ORIGIN
	if figuren then figuren.Parent = m end
	return m, onbekend
end

-- oude Hans en Grietje v1 (scriptmatig, afgekeurd) weg
local v1 = workspace:FindFirstChild("HansEnGrietje"); if v1 then v1:Destroy() end
local huis, o1 = plaats(HUIS, "HansEnGrietje")
local omg, o2 = plaats(OMG, "HansEnGrietjeOmgeving")
-- tuinmuur, pijlers, oven en stucmuurtjes botsen (stuc_tuin), huis via COLL_
for _, p in ipairs(omg:GetChildren()) do if p:IsA("BasePart") and string.find(p.Name, "TEX_stuc_tuin") then p.CanCollide = true; if p:IsA("MeshPart") then p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end end end
-- geen zwevend layout-label bij gebouwde dingen (Daan)
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do if d:IsA("BillboardGui") and d.Parent and string.find(string.lower(d.Parent.Name), "hans") then d:Destroy() end end end
-- horizonbomen in het gebied weghalen
local weg = 0
local function binnen(p) local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S; return x > -13 and x < 9 and y > -15 and y < 7 end
for _, naam in ipairs({"VillaVoltaHorizon", "AssepoesterGroen", "SneeuwwitjeGroen"}) do
	local f = workspace:FindFirstChild(naam)
	if f then for _, t in ipairs(f:GetChildren()) do
		local p = t:IsA("Model") and t:GetPivot().Position or (t:IsA("BasePart") and t.Position)
		if p and binnen(p) then t:Destroy(); weg += 1 end
	end end
end
-- terreingras prikt door paden, perken en snoeppad: onder de tuin gras -> Ground
for x = -19, 20, 1.3 do for y = -20, 13, 1.3 do
	local p = lokaal(x, y, 0).Position
	local r = Region3.new(Vector3.new(p.X - 2, -4, p.Z - 2), Vector3.new(p.X + 2, 4, p.Z + 2)):ExpandToGrid(4)
	workspace.Terrain:ReplaceMaterial(r, 4, Enum.Material.Grass, Enum.Material.Ground); workspace.Terrain:ReplaceMaterial(r, 4, Enum.Material.LeafyGrass, Enum.Material.Ground)
end end
-- lantaarns dag/nacht: lampen in de taartlampen meenemen
local ldn = game:GetService("ServerScriptService"):FindFirstChild("LantaarnsDagNacht")
-- spawn op het hoofdpad voor het tuinhek, kijkend naar het huisje (oude plek in attribuut OudeCFrame)
local sp = workspace:FindFirstChildWhichIsA("SpawnLocation", true)
if sp then
	if sp:GetAttribute("OudeCFrame") == nil then sp:SetAttribute("OudeCFrame", sp.CFrame) end
	local y = 0.25 + sp.Size.Y / 2
	sp.CFrame = CFrame.lookAt(lokaal(-1.6, -13.4, 0).Position + Vector3.new(0, y, 0), lokaal(-0.6, 0, 0).Position + Vector3.new(0, y, 0))
end
local ids = {}
for _, m in ipairs({huis, omg}) do for _, sa in ipairs(m:GetDescendants()) do if sa:IsA("SurfaceAppearance") then
	for _, id in ipairs({sa.ColorMap, sa.NormalMap}) do if id ~= "" then local d = Instance.new("Decal"); d.Texture = id; table.insert(ids, d) end end end end end
task.spawn(function() pcall(function() game:GetService("ContentProvider"):PreloadAsync(ids) end) end)
return string.format("huis %d, tuin %d; %d bomen weg; LantaarnsDagNacht %s; onbekend: %s %s", #huis:GetChildren(), #omg:GetChildren(), weg, tostring(ldn ~= nil), table.concat(o1, ","), table.concat(o2, ","))
