-- Sneeuwwitje: kasteel + grot (gebakken texturen, 05_bake) en voorplein/perken (04_omgeving). Assets uit build/09_export_roblox.py.
-- Model: gevel kijkt naar -Y (oost), +X = noord, oorsprong = midden gevel op de voorkant van de ronde toren, z=0 = plein.
-- Kalibratie (ref/model_frame.json): oorsprong = OSM (-25.22, 55.77) m = studs (-75.65, -167.32); kijkrichting Roblox (0.9731, 0, 0.2306); grond Y=2.
-- Botsing: onzichtbare COLL_-blokken (map Botsing). Lampen: LAMP_ -> PointLight (binnen = attribuut Binnen).
local HUIS = 117515855048104
local OMG = 72248096298132
local TEX = {baksteen_achter = {71167782720034, 103548644498884}, baksteen_binnen = {88488081647481, 75776817875430}, baksteen_detail = {94758440972061, 123171850485068}, baksteen_noord = {92777226090361, 129321328063071}, baksteen_voor = {101665828334331, 77786143033371}, baksteen_zuid = {110206829329078, 122757706854953}, pannen_daken = {111520594999462, 125385647833484}, pannen_torens = {98996464531535, 125943015442544}, rots_a = {70419789476254, 97525175297854}, rots_b = {82975567935403, 90203113846092}, ruine = {92870556806499, 90835585673068}, steen = {98747270364092}}   -- wordt ingevuld door roblox/maak_plaatsscript.py
local F = Vector3.new(0.9731, 0, 0.2306)
local ORIGIN = CFrame.new(-75.65, 2.0, -167.32) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	baksteen = {Color3.fromRGB(204, 172, 146), "Brick"}, steen = {Color3.fromRGB(216, 208, 188), "Limestone", "VV_Steen"},
	pannen = {Color3.fromRGB(150, 88, 66), "ClayRoofTiles"}, rots = {Color3.fromRGB(138, 144, 130), "Rock"}, ruine = {Color3.fromRGB(178, 120, 90), "Brick"},
	zink = {Color3.fromRGB(92, 102, 108), "Metal"}, goud = {Color3.fromRGB(200, 158, 60), "Metal"}, hout = {Color3.fromRGB(92, 52, 32), "Wood"},
	donker = {Color3.fromRGB(8, 8, 8), "SmoothPlastic"}, glas = {Color3.fromRGB(26, 32, 34), "SmoothPlastic"}, lood = {Color3.fromRGB(52, 54, 56), "Metal"},
	vloer = {Color3.fromRGB(96, 88, 80), "Slate"}, schild = {Color3.fromRGB(28, 34, 34), "SmoothPlastic"}, rood = {Color3.fromRGB(160, 32, 26), "SmoothPlastic"},
	ijzer = {Color3.fromRGB(24, 26, 26), "Metal"}, klimop = {Color3.fromRGB(46, 78, 34), "LeafyGrass"}, pad = {Color3.fromRGB(150, 142, 130), "Pebble", "VV_Grind"},
	klinker = {Color3.fromRGB(235, 228, 214), "Pebble", "VV_Grind"}, band = {Color3.fromRGB(128, 126, 120), "Concrete"},
	aarde = {Color3.fromRGB(104, 80, 60), "Ground"}, papier = {Color3.fromRGB(232, 218, 176), "SmoothPlastic"}, terracotta = {Color3.fromRGB(160, 88, 60), "Concrete"},
}
local TINT = {baksteen = Color3.fromRGB(235, 230, 222), steen = Color3.fromRGB(230, 226, 216), pannen = Color3.fromRGB(190, 168, 158), rots = Color3.fromRGB(255, 255, 255), ruine = Color3.fromRGB(235, 232, 228)}
local GEEN_SCHADUW = {donker = true, papier = true, goud = true, lood = true, klimop = true}

local function plaats(asset, naam, binnen)
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
	local lampen = Instance.new("Folder"); lampen.Name = "Lampen"; lampen.Parent = m
	local onbekend = {}
	for _, p in ipairs(m:GetChildren()) do
		if not p:IsA("BasePart") then continue end
		p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = false
		if string.match(p.Name, "^COLL_") then
			p.Transparency = 1; p.CanCollide = true; p.CanQuery = true; p.CastShadow = false; p.Parent = bots
			if p:IsA("MeshPart") then p.CollisionFidelity = Enum.CollisionFidelity.Box end
		elseif string.match(p.Name, "^LAMP_") then
			p.Transparency = 1; p.CastShadow = false; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Name = "Lamp"; p.Parent = lampen
			local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 120); pl.Range = 14; pl.Brightness = 1.4; pl.Shadows = false; pl.Parent = p
			if binnen then p:SetAttribute("Binnen", true) end
		else
			local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$")
			local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
			if tex and TEX[tex] then
				local role = string.match(tex, "^(%a+)")
				local s = M[role] or M.baksteen
				p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material[s[2]]
				local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
				if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
				if TINT[role] then sa.Color = TINT[role] end
				if string.find(tex, "binnen") then sa.Color = Color3.fromRGB(150, 140, 128) end
				sa.Parent = p
			elseif key and M[key] then
				local s = M[key]; p.Color = s[1]; p.Material = Enum.Material[s[2]]; if s[3] then p.MaterialVariant = s[3] end
				if GEEN_SCHADUW[key] then p.CastShadow = false end
				if key == "klimop" then   -- bladplakkaten met de haagtextuur (opnieuw geupload, textures/haag)
					p.Material = Enum.Material.Plastic; p.Color = Color3.new(1, 1, 1); p.DoubleSided = true
					local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://73997585762296"; sa.NormalMap = "rbxassetid://114509386598524"
					pcall(function() sa.Color = Color3.fromRGB(150, 190, 120) end); sa.Parent = p
				end
			else table.insert(onbekend, p.Name) end
		end
	end
	m.WorldPivot = ORIGIN
	return m, onbekend
end

local huis, o1 = plaats(HUIS, "Sneeuwwitje", true)
local omg, o2 = plaats(OMG, "SneeuwwitjeOmgeving", false)
-- geen zwevend layout-label bij gebouwde dingen (Daan)
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do if d:IsA("BillboardGui") and d.Parent and (d.Parent.Name == "Sneeuwwitje" or d.Parent.Name == "Kasteel Sneeuwwitje") then d:Destroy() end end end
-- horizonbomen en Assepoester-planten die nu in kasteel, grot of op het plein zouden staan weghalen
local weg = 0
local GEBIED = {{-8.0, 7.8, -0.2, 9.5}, {9.5, 24.2, -8.2, 2.8}, {-10.5, 11.0, -11.0, 1.0}}   -- x0, x1, y0, y1 (model)
local function binnenGebied(p)
	local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
	for _, g in ipairs(GEBIED) do if x > g[1] and x < g[2] and y > g[3] and y < g[4] then return true end end
	return false
end
for _, naam in ipairs({"VillaVoltaHorizon", "AssepoesterGroen"}) do
	local f = workspace:FindFirstChild(naam)
	if f then for _, t in ipairs(f:GetChildren()) do
		local p = t:IsA("Model") and t:GetPivot().Position or (t:IsA("BasePart") and t.Position)
		if p and binnenGebied(p) then t:Destroy(); weg += 1 end
	end end
end
-- spawn op het voorplein, kijkend naar het kasteel (oude plek in attribuut OudeCFrame)
local sp = workspace:FindFirstChildWhichIsA("SpawnLocation", true)
if sp then
	if sp:GetAttribute("OudeCFrame") == nil then sp:SetAttribute("OudeCFrame", sp.CFrame) end
	local y = 0.2 + sp.Size.Y / 2
	sp.CFrame = CFrame.lookAt(lokaal(0, -8, 0).Position + Vector3.new(0, y, 0), lokaal(0, 0, 0).Position + Vector3.new(0, y, 0))
end
local ids = {}
for _, m in ipairs({huis, omg}) do for _, sa in ipairs(m:GetDescendants()) do if sa:IsA("SurfaceAppearance") then
	for _, id in ipairs({sa.ColorMap, sa.NormalMap}) do if id ~= "" then local d = Instance.new("Decal"); d.Texture = id; table.insert(ids, d) end end end end end
task.spawn(function() pcall(function() game:GetService("ContentProvider"):PreloadAsync(ids) end) end)
return string.format("kasteel %d, omgeving %d; %d bomen/planten weg; onbekend: %s %s", #huis:GetChildren(), #omg:GetChildren(), weg, table.concat(o1, ","), table.concat(o2, ","))
