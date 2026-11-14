-- De Zes Zwanen (2019): kasteel + rots, omgeving (vijvers, oevers, pad, kade, hokje, hekken, lantaarns) en 6 zwanenboten.
-- Gegenereerd door roblox/maak_plaatsscript.py. Modelframe: voorkant naar de vijver = -Y, oorsprong = midden kasteel-footprint (OSM 961616753).
local KASTEEL, OMG, ZWAAN = @KASTEEL@, @OMG@, @ZWAAN@
local TEXK = @TEXK@
local TEXO = @TEXO@
local TEXZ = @TEXZ@
local SJERP = @SJERP@
local F = Vector3.new(@FX@, 0, @FZ@)
local ORIGIN = CFrame.new(@OX@, 2.0, @OZ@) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S, WL = 3, -0.35
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(214, 210, 200), "Plastic"}, natuursteen = {Color3.fromRGB(190, 180, 160), "Plastic"}, rots = {Color3.fromRGB(150, 148, 140), "Plastic"},
	pannen = {Color3.fromRGB(150, 80, 60), "Plastic"}, leien = {Color3.fromRGB(120, 70, 50), "Plastic"}, oeversteen = {Color3.fromRGB(196, 178, 150), "Plastic"},
	venster = {Color3.fromRGB(20, 22, 24), "SmoothPlastic"}, glasoranje = {Color3.fromRGB(255, 170, 80), "Neon"}, ijzer = {Color3.fromRGB(24, 26, 26), "Metal"},
	goud = {Color3.fromRGB(214, 168, 72), "Metal"}, glaslamp = {Color3.fromRGB(255, 226, 170), "Glass"}, donker = {Color3.fromRGB(6, 6, 6), "SmoothPlastic"},
	water = {Color3.fromRGB(52, 64, 42), "SmoothPlastic"}, bodem = {Color3.fromRGB(34, 30, 24), "Mud"}, grond = {Color3.fromRGB(70, 62, 44), "Ground"},
	beton = {Color3.fromRGB(118, 92, 74), "Concrete"}, steentjes = {Color3.fromRGB(196, 166, 104), "Brick"}, bordeaux = {Color3.fromRGB(112, 20, 26), "WoodPlanks"},
	creme = {Color3.fromRGB(230, 214, 178), "SmoothPlastic"}, dak = {Color3.fromRGB(40, 40, 44), "Slate"}, hekblauw = {Color3.fromRGB(72, 102, 106), "Metal"},
	hout = {Color3.fromRGB(92, 58, 36), "Wood"}, zwaan = {Color3.fromRGB(238, 230, 210), "SmoothPlastic"}, snavel = {Color3.fromRGB(232, 112, 40), "SmoothPlastic"},
	zwart = {Color3.fromRGB(16, 16, 16), "SmoothPlastic"}, oog = {Color3.fromRGB(8, 8, 8), "Glass"}, kuip = {Color3.fromRGB(128, 26, 24), "SmoothPlastic"}, kern = {Color3.fromRGB(30, 30, 30), "Rock"},
	klinker = {Color3.fromRGB(110, 58, 44), "Brick"}, doek = {Color3.fromRGB(236, 232, 222), "Fabric"}, deurgroen = {Color3.fromRGB(56, 96, 96), "WoodPlanks"},
}
local GEEN_SCHADUW = {glasoranje = true, goud = true, donker = true}
-- loopvlakken en massieve delen krijgen echte mesh-botsing (pad lag 1 stud boven het terrein: voeten zakten erin; vijverkuil: je viel erdoor)
local MASSIEF = {oeversteen = true, rots = true, kern = true, steentjes = true, stuc = true, natuursteen = true}   -- pad/oever/bodem: rasterblokken (COLL_) i.p.v. mesh-botsing

local function plaats(asset, naam, TEX)
	local oud = workspace:FindFirstChild(naam); if oud then oud:Destroy() end
	local m = Instance.new("Model"); m.Name = naam
	for _, o in ipairs(game:GetObjects("rbxassetid://" .. asset)) do o.Parent = m end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
	for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
	m.Parent = workspace; m:ScaleTo(S)
	local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
	m:PivotTo(ORIGIN * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
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
			local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 120); pl.Range = 16; pl.Brightness = 1.2; pl.Shadows = false; pl.Parent = p
		else
			local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$"); local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
			if tex and TEX and TEX[tex] then
				p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
				local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
				if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
				local TINT = {rots = Color3.fromRGB(170, 168, 160), stuc = Color3.fromRGB(215, 212, 204), natuursteen = Color3.fromRGB(225, 220, 208)}
				if TINT[tex] then sa.Color = TINT[tex] end
				sa.Parent = p
			elseif tex == "sjerp" or key == "sjerptex" then
				p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic; p:SetAttribute("Sjerp", true)
			elseif key and M[key] then
				p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
				if GEEN_SCHADUW[key] then p.CastShadow = false end
				if key == "water" then p.Transparency = 0.05; p.Reflectance = 0; p.CastShadow = false end   -- troebel, geen blauwe luchtspiegeling
				if key == "glasoranje" then p.Transparency = 0.25 end
			else table.insert(onbekend, p.Name) end
		end
	end
	m.WorldPivot = ORIGIN
	return m, onbekend
end

-- oude bomen/struiken en layout-labels op de plek weg (alles binnen de scene-rechthoek x -13..22, y -28..9)
local weg = 0
for _, f in ipairs(workspace:GetChildren()) do
	if string.find(f.Name, "Groen") or string.find(f.Name, "Bos") or string.find(f.Name, "Horizon") then
		for _, t in ipairs(f:GetChildren()) do
			local p = t:IsA("Model") and t:GetPivot().Position or (t:IsA("BasePart") and t.Position)
			if p then
				local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
				if x > -13 and x < 22 and y > -28 and y < 9 then t:Destroy(); weg += 1 end
			end
		end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do if string.find(string.lower(d.Name), "zwanen") then d:Destroy() end end end

-- terrein: graven onder de vijvers, Ground onder pad en oevergrond
local T = workspace.Terrain
local ng, nb = 0, 0
for c in string.gmatch("@GRAAF@", "[^;]+") do
	local i, j = string.match(c, "(-?%d+),(-?%d+)")
	T:FillBlock(CFrame.new(i * 4 + 2, -2, j * 4 + 2), Vector3.new(4, 12, 4), Enum.Material.Air); ng += 1
end
for c in string.gmatch("@GROND@", "[^;]+") do
	local i, j = string.match(c, "(-?%d+),(-?%d+)")
	T:ReplaceMaterial(Region3.new(Vector3.new(i * 4, -8, j * 4), Vector3.new(i * 4 + 4, 8, j * 4 + 4)):ExpandToGrid(4), 4, Enum.Material.Grass, Enum.Material.Ground); nb += 1
end

local k, o1 = plaats(KASTEEL, "ZesZwanenKasteel", TEXK)
local om, o2 = plaats(OMG, "ZesZwanenOmgeving", TEXO)
-- zwanenboten (de attractie zelf) staan er voorlopig niet in (Daan): alleen de scene eromheen
local oudb = workspace:FindFirstChild("ZesZwanenBoten"); if oudb then oudb:Destroy() end
local map = {GetChildren = function() return {} end}; local o3 = {}
local ids = {}
for _, t in ipairs({TEXK, TEXO, TEXZ}) do for _, v in pairs(t) do for _, id in ipairs(v) do local d = Instance.new("Decal"); d.Texture = "rbxassetid://" .. id; table.insert(ids, d) end end end
for _, id in ipairs(SJERP) do local d = Instance.new("Decal"); d.Texture = "rbxassetid://" .. id; table.insert(ids, d) end
local ok = 0; game:GetService("ContentProvider"):PreloadAsync(ids, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end)
local function onb(t) return #t > 0 and table.concat(t, ",") or "-" end
return string.format("kasteel %d, omgeving %d, zwanen %d; gegraven %d cellen, ground %d; %d bomen weg; tex %d/%d; onbekend %s %s %s",
	#k:GetChildren(), #om:GetChildren(), #map:GetChildren(), ng, nb, weg, ok, #ids, onb(o1), onb(o2), onb(o3))
