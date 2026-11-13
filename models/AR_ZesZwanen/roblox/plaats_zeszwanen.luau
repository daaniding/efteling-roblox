-- De Zes Zwanen (2019): kasteel + rots, omgeving (vijvers, oevers, pad, kade, hokje, hekken, lantaarns) en 6 zwanenboten.
-- Gegenereerd door roblox/maak_plaatsscript.py. Modelframe: voorkant naar de vijver = -Y, oorsprong = midden kasteel-footprint (OSM 961616753).
local KASTEEL, OMG, ZWAAN = 100541413989663, 125064138686858, 111482698984449
local TEXK = {leien = {136857157459933, 106272441850742}, natuursteen = {100525327843346, 94033619716350}, pannen = {75582792207909, 135122716948075}, rots = {131558635905721, 123387295689380}, stuc = {76972134369003, 91547575648048}}
local TEXO = {hout = {128603993024151, 72551041755026}, oeversteen = {92532153830281, 116485451469003}, rots = {112972812786899, 76425319520050}}
local SJERP = {87532223374208, 93147302769265}
local F = Vector3.new(0.1076, 0, 0.9942)
local ORIGIN = CFrame.new(-108.77, 2.0, -301.0) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
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
}
local GEEN_SCHADUW = {glasoranje = true, goud = true, donker = true}

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
			local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 120); pl.Range = 16; pl.Brightness = 1.4; pl.Shadows = false; pl.Parent = p
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
for c in string.gmatch("-32,-65;-32,-64;-32,-63;-31,-72;-31,-71;-31,-70;-31,-69;-31,-68;-31,-66;-31,-65;-31,-64;-30,-71;-30,-70;-30,-69;-30,-68;-30,-67;-30,-66;-30,-65;-29,-71;-29,-70;-29,-69;-29,-68;-29,-67;-29,-66;-28,-71;-28,-70;-28,-69;-28,-68;-28,-67;-28,-66;-27,-72;-27,-71;-27,-70;-27,-69;-27,-68;-27,-67;-26,-74;-26,-73;-26,-72;-26,-71;-26,-70;-26,-69;-26,-68;-26,-67;-26,-61;-26,-60;-25,-74;-25,-73;-25,-72;-25,-71;-25,-70;-25,-69;-25,-68;-25,-67;-25,-61;-25,-60;-24,-74;-24,-73;-24,-72;-24,-71;-24,-70;-24,-69;-24,-68;-24,-67;-24,-62;-24,-61;-24,-60;-23,-75;-23,-74;-23,-73;-23,-72;-23,-71;-23,-70;-23,-69;-23,-68;-23,-67;-23,-62;-23,-61;-23,-60;-22,-75;-22,-74;-22,-73;-22,-72;-22,-71;-22,-70;-22,-69;-22,-68;-22,-63;-22,-62;-22,-61;-22,-60;-21,-74;-21,-73;-21,-72;-21,-71;-21,-70;-21,-69;-21,-64;-21,-63;-21,-62;-21,-61;-20,-64;-20,-63;-20,-62;-20,-61;-19,-64;-19,-63;-19,-62;-18,-64;-18,-63;-17,-78;-17,-77;-17,-64;-17,-63;-16,-78;-15,-78;-14,-78;-14,-77;-14,-76;-13,-77;-13,-76", "[^;]+") do
	local i, j = string.match(c, "(-?%d+),(-?%d+)")
	T:FillBlock(CFrame.new(i * 4 + 2, -2, j * 4 + 2), Vector3.new(4, 12, 4), Enum.Material.Air); ng += 1
end
for c in string.gmatch("-33,-72;-33,-71;-33,-70;-33,-68;-33,-66;-33,-65;-33,-64;-33,-63;-33,-62;-32,-73;-32,-72;-32,-71;-32,-70;-32,-69;-32,-68;-32,-67;-32,-66;-32,-62;-31,-73;-31,-67;-31,-63;-31,-62;-30,-73;-30,-72;-30,-64;-30,-63;-30,-62;-30,-61;-30,-60;-30,-59;-30,-58;-29,-73;-29,-72;-29,-65;-29,-64;-29,-63;-29,-62;-29,-61;-29,-60;-29,-59;-29,-58;-29,-57;-29,-56;-28,-74;-28,-73;-28,-72;-28,-65;-28,-64;-28,-63;-28,-62;-28,-61;-28,-60;-28,-59;-28,-58;-28,-57;-28,-56;-27,-75;-27,-74;-27,-73;-27,-66;-27,-65;-27,-64;-27,-63;-27,-62;-27,-61;-27,-60;-27,-59;-27,-58;-27,-57;-26,-75;-26,-66;-26,-65;-26,-64;-26,-63;-26,-62;-26,-59;-26,-58;-25,-80;-25,-79;-25,-75;-25,-66;-25,-65;-25,-64;-25,-63;-25,-62;-25,-59;-25,-58;-24,-81;-24,-80;-24,-79;-24,-76;-24,-75;-24,-66;-24,-65;-24,-64;-24,-63;-24,-59;-24,-58;-23,-81;-23,-80;-23,-79;-23,-78;-23,-77;-23,-76;-23,-66;-23,-65;-23,-64;-23,-63;-23,-59;-23,-58;-22,-81;-22,-80;-22,-79;-22,-78;-22,-77;-22,-76;-22,-67;-22,-66;-22,-65;-22,-64;-22,-59;-21,-81;-21,-80;-21,-79;-21,-78;-21,-77;-21,-76;-21,-75;-21,-68;-21,-67;-21,-66;-21,-65;-21,-60;-21,-59;-20,-80;-20,-79;-20,-78;-20,-77;-20,-76;-20,-75;-20,-74;-20,-73;-20,-72;-20,-71;-20,-70;-20,-69;-20,-68;-20,-67;-20,-66;-20,-65;-20,-60;-20,-59;-19,-79;-19,-78;-19,-77;-19,-76;-19,-75;-19,-74;-19,-73;-19,-72;-19,-71;-19,-70;-19,-69;-19,-68;-19,-67;-19,-66;-19,-65;-19,-61;-19,-60;-18,-79;-18,-78;-18,-77;-18,-76;-18,-75;-18,-74;-18,-73;-18,-72;-18,-71;-18,-70;-18,-69;-18,-68;-18,-67;-18,-66;-18,-65;-18,-62;-18,-61;-17,-80;-17,-79;-17,-76;-17,-75;-17,-74;-17,-73;-17,-72;-17,-71;-17,-70;-17,-69;-17,-67;-17,-66;-17,-65;-17,-62;-16,-80;-16,-79;-16,-77;-16,-76;-16,-74;-16,-73;-16,-72;-16,-65;-16,-64;-16,-63;-16,-62;-15,-80;-15,-79;-15,-77;-15,-76;-15,-75;-15,-74;-15,-73;-15,-65;-15,-64;-15,-63;-14,-80;-14,-79;-14,-75;-14,-74;-14,-73;-13,-79;-13,-78;-13,-75;-13,-74;-13,-73;-12,-79;-12,-78;-12,-77;-12,-76;-12,-75;-12,-74;-12,-73;-11,-77;-11,-76;-11,-75;-11,-74;-10,-75;-10,-74;-9,-75;-9,-74;-8,-75;-8,-74;-7,-75;-7,-74", "[^;]+") do
	local i, j = string.match(c, "(-?%d+),(-?%d+)")
	T:ReplaceMaterial(Region3.new(Vector3.new(i * 4, -8, j * 4), Vector3.new(i * 4 + 4, 8, j * 4 + 4)):ExpandToGrid(4), 4, Enum.Material.Grass, Enum.Material.Ground); nb += 1
end

local k, o1 = plaats(KASTEEL, "ZesZwanenKasteel", TEXK)
local om, o2 = plaats(OMG, "ZesZwanenOmgeving", TEXO)
local zw, o3 = plaats(ZWAAN, "ZesZwanenZwaan", nil)
local map = workspace:FindFirstChild("ZesZwanenBoten"); if map then map:Destroy() end
map = Instance.new("Model"); map.Name = "ZesZwanenBoten"; map.Parent = workspace
for i, z in ipairs({{-0.92, -11.65, 0.898, -0.439}, {0.88, -12.17, 0.989, -0.151}, {2.76, -12.14, 0.987, 0.164}, {7.92, -6.84, 0.143, 0.99}, {6.22, -1.67, -0.722, 0.692}, {-4.46, -7.16, 0.156, -0.988}}) do
	local c = zw:Clone(); c.Name = "Zwaan" .. i
	local th = math.atan2(z[3], -z[4])
	c:PivotTo(lokaal(z[1], z[2], WL) * CFrame.Angles(0, th, 0))
	for _, p in ipairs(c:GetDescendants()) do
		if p:IsA("BasePart") and p:GetAttribute("Sjerp") then
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. SJERP[(i % 2) + 1]; sa.Parent = p
		end
	end
	c.Parent = map
end
zw:Destroy()
local ids = {}
for _, t in ipairs({TEXK, TEXO}) do for _, v in pairs(t) do for _, id in ipairs(v) do local d = Instance.new("Decal"); d.Texture = "rbxassetid://" .. id; table.insert(ids, d) end end end
for _, id in ipairs(SJERP) do local d = Instance.new("Decal"); d.Texture = "rbxassetid://" .. id; table.insert(ids, d) end
local ok = 0; game:GetService("ContentProvider"):PreloadAsync(ids, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end)
local function onb(t) return #t > 0 and table.concat(t, ",") or "-" end
return string.format("kasteel %d, omgeving %d, zwanen %d; gegraven %d cellen, ground %d; %d bomen weg; tex %d/%d; onbekend %s %s %s",
	#k:GetChildren(), #om:GetChildren(), #map:GetChildren(), ng, nb, weg, ok, #ids, onb(o1), onb(o2), onb(o3))
