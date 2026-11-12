-- Assepoester v2: huis met gebakken texturen (05_bake) + binnenplaats/tuin (04_omgeving). Beide assets uit build/09_export_roblox.py.
-- Blender: gevel kijkt naar -Y (west), +X = zuid, oorsprong = voorkant uitgangsportiek, midden gevel, z=0 = maaiveld.
-- OSM-kalibratie: modeloorsprong = OSM (-3.18, 95.15) m = studs (-9.54, -285.44); kijkrichting Roblox (-0.983, 0, 0.185); grond Y=2.
-- Botsing: onzichtbare COLL_-blokken (map Botsing), de meshes zelf botsen niet (deuropeningen blijven open). Lampen: LAMP_-punten.
local HUIS = 90187101137664   -- v2: gebakken texturen (05_bake), binnenroute, botsblokken + lampen
local OMG = 107962207315554
local TEX = {groen = {81834719569516}, omlijsting = {87948221887360}, pannen_hoofd = {77636042874488, 106283833457150}, pannen_laag = {122713295976618, 96717225369930}, plint = {119922222348627}, stuc_achter = {133546970680659, 92636686440629}, stuc_binnen = {74215830399290, 88768649560193}, stuc_noord = {91966066380851, 115711031846310}, stuc_voor = {136554997230084, 109895420988954}, stuc_zuid = {73175908141281, 118117389474333}}   -- groep -> {kleur, normaal}, textures/asset_ids.txt
local F = Vector3.new(-0.9828, 0, 0.1846)
local ORIGIN = CFrame.new(-9.54, 2.0, -285.44) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {   -- {kleur, materiaal, variant}; getemperd (WERKWIJZE)
	stuc = {Color3.fromRGB(186, 183, 170), "Plaster", "VV_Pleister"}, omlijsting = {Color3.fromRGB(204, 200, 186), "Limestone", "VV_Steen"},
	plint = {Color3.fromRGB(150, 148, 140), "Concrete"}, groen = {Color3.fromRGB(58, 98, 98), "Wood"},
	pannen = {Color3.fromRGB(150, 92, 72), "ClayRoofTiles"}, baksteen = {Color3.fromRGB(140, 70, 52), "Brick"},
	hout = {Color3.fromRGB(104, 56, 34), "Wood"}, glas = {Color3.fromRGB(26, 32, 34), "SmoothPlastic"},
	lood = {Color3.fromRGB(52, 54, 56), "Metal"}, zink = {Color3.fromRGB(96, 112, 118), "Metal"},
	kozijn = {Color3.fromRGB(220, 212, 190), "SmoothPlastic"}, donker = {Color3.fromRGB(8, 8, 8), "SmoothPlastic"},
	achter = {Color3.fromRGB(140, 140, 132), "Concrete"}, venster = {Color3.fromRGB(200, 214, 218), "Glass"},
	vloer = {Color3.fromRGB(88, 62, 54), "Brick"}, plavuis = {Color3.fromRGB(78, 72, 66), "Slate"},   -- binnen gedempt
	balk = {Color3.fromRGB(78, 50, 30), "Wood"}, vuur = {Color3.fromRGB(255, 150, 60), "Neon"},
	doek = {Color3.fromRGB(150, 180, 210), "SmoothPlastic"}, pompoen = {Color3.fromRGB(214, 112, 30), "SmoothPlastic"},
	ketel = {Color3.fromRGB(32, 32, 32), "Metal"},
	haag = {Color3.fromRGB(255, 255, 255), "Plastic"}, buxus = {Color3.fromRGB(255, 255, 255), "Plastic"},   -- als Villa Volta: SA op Plastic
	klinker = {Color3.fromRGB(235, 228, 214), "Pebble", "VV_Grind"}   -- Daan: wit grind zoals Villa Volta, band = {Color3.fromRGB(128, 126, 120), "Concrete"},
	ijzer = {Color3.fromRGB(24, 26, 26), "Metal"}, aarde = {Color3.fromRGB(70, 52, 38), "Ground"},
	lamp = {Color3.fromRGB(226, 222, 206), "Glass"}, rots = {Color3.fromRGB(150, 140, 126), "Rock"},
	kist = {Color3.fromRGB(92, 58, 36), "Wood"}, papier = {Color3.fromRGB(232, 218, 176), "SmoothPlastic"},
	goud = {Color3.fromRGB(190, 150, 70), "Metal"}, mand = {Color3.fromRGB(150, 112, 64), "WoodPlanks"},
}
local HAAG_SA = {kleur = "rbxassetid://73997585762296", normaal = "rbxassetid://114509386598524"}   -- textures/haag, opnieuw geupload (oude 1078.../8046... renderen wit)
local TINT = {stuc = Color3.fromRGB(214, 210, 200), pannen = Color3.fromRGB(176, 150, 140), groen = Color3.fromRGB(200, 205, 205), omlijsting = Color3.fromRGB(222, 218, 208), plint = Color3.fromRGB(200, 196, 188)}   -- SurfaceAppearance.Color: bake iets temperen zonder nieuwe bake
local GEEN_SCHADUW = {lamp = true, vuur = true, donker = true, venster = true, papier = true, goud = true, lood = true}

local function plaats(asset, naam, binnen)
	local oud = workspace:FindFirstChild(naam); if oud then oud:Destroy() end
	local m = Instance.new("Model"); m.Name = naam
	for _, o in ipairs(game:GetObjects("rbxassetid://" .. asset)) do o.Parent = m end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
	for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
	m.Parent = workspace; m:ScaleTo(S)
	local anker
	for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
	assert(anker, "geen anker in " .. naam)
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
			local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 120); pl.Range = binnen and 14 or 16
			pl.Brightness = binnen and 1.4 or 2; pl.Shadows = false; pl.Parent = p
			if binnen then p:SetAttribute("Binnen", true) end
		else
			local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$")
			local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
			if tex and TEX[tex] then
				local role = string.match(tex, "^(%a+)")
				local s = M[role] or M.stuc
				p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material[s[2]]
				local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
				if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
				if TINT[role] then sa.Color = TINT[role] end
				if tex == "stuc_binnen" then sa.Color = Color3.fromRGB(150, 144, 134) end   -- binnen donkerder: lampjes en vuur gaan werken
				sa.Parent = p
			elseif key and M[key] then
				local s = M[key]; p.Color = s[1]; p.Material = Enum.Material[s[2]]; if s[3] then p.MaterialVariant = s[3] end
				if key == "haag" or key == "buxus" then
					local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = HAAG_SA.kleur; sa.NormalMap = HAAG_SA.normaal
					if key == "buxus" then pcall(function() sa.Color = Color3.fromRGB(220, 240, 200) end) end
					sa.Parent = p
				end
				if key == "glas" then p.Reflectance = 0.12 end
				if key == "venster" then p.Transparency = 0.7; p.Reflectance = 0.08 end
				if key == "lamp" then p.Transparency = 0.25 end
				if GEEN_SCHADUW[key] then p.CastShadow = false end
			else table.insert(onbekend, p.Name) end
		end
	end
	m.WorldPivot = ORIGIN
	return m, onbekend
end

local huis, o1 = plaats(HUIS, "Assepoester", true)
local omg, o2 = plaats(OMG, "AssepoesterOmgeving", false)
-- binnenplaats en tuin vrij van de horizonbomen van Villa Volta (die stonden er voor de tuin er was)
local weg = 0
local hor = workspace:FindFirstChild("VillaVoltaHorizon")
if hor then
	for _, t in ipairs(hor:GetChildren()) do
		local p = t:IsA("Model") and t:GetPivot().Position or (t:IsA("BasePart") and t.Position)
		if p then
			local l = ORIGIN:PointToObjectSpace(p); local bx, by = -l.X / S, l.Z / S
			if bx > -14.5 and bx < 16.5 and by > -9 and by < 15 then t:Destroy(); weg += 1 end
		end
	end
end
-- spawn bij de tuiningang, kijkend naar het huis (oude plek in attribuut OudeCFrame)
local sp = workspace:FindFirstChildWhichIsA("SpawnLocation", true)
if sp then
	if sp:GetAttribute("OudeCFrame") == nil then sp:SetAttribute("OudeCFrame", sp.CFrame) end
	local y = 0.2 + sp.Size.Y / 2
	sp.CFrame = CFrame.lookAt(lokaal(-5.3, -11.5, 0).Position + Vector3.new(0, y, 0), lokaal(-4.5, 0, 0).Position + Vector3.new(0, y, 0))
end
return string.format("huis %d, omgeving %d delen; %d horizonbomen weg; onbekend: %s %s", #huis:GetChildren(), #omg:GetChildren(), weg,
	table.concat(o1, ","), table.concat(o2, ","))
