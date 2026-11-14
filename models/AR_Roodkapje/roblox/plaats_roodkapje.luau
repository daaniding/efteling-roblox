-- Roodkapje: huisje van grootmoeder (op het maaiveld) + vlak grindpad + vennetje. Gegenereerd door maak_plaatsscript.py.
-- Modelframe: oorsprong = midden BAG 50911608, -Y = voorkant (noord, naar het pad), +X = west, z = 0 padniveau voor het huisje
-- (= maaiveld + 1.9 m, dus Roblox Y 7.7). Botsing = Parts uit de json (geen geexporteerde schuine botsmeshes).
local HUIS, OMG = 138826522235983, 77138895088158
local TEX = {RK = {hout = {104281696098715, 73417955614127}, lei = {129100276385293, 77568180060232}, natuursteen = {121115756980472, 123584062912286}, stuc = {123643345611514, 113459759803224}}, RO = {}}
local COLL = {huisje = {{0, 0.1, 0.225, 4.7, 4.6, 4.25, 0.0}, {-3.225, 1.843, -1.036, 0.95, 0.285, 1.727, 0.0}, {-3.225, 2.128, -1.123, 0.95, 0.285, 1.555, 0.0}, {-3.225, 2.414, -1.209, 0.95, 0.285, 1.382, 0.0}, {-3.225, 2.699, -1.295, 0.95, 0.285, 1.209, 0.0}, {-3.225, 2.985, -1.382, 0.95, 0.285, 1.036, 0.0}, {-3.225, 3.27, -1.468, 0.95, 0.285, 0.864, 0.0}, {-3.225, 3.555, -1.555, 0.95, 0.285, 0.691, 0.0}, {-3.225, 3.841, -1.641, 0.95, 0.285, 0.518, 0.0}, {-3.225, 4.126, -1.727, 0.95, 0.285, 0.345, 0.0}, {-3.225, 4.412, -1.814, 0.95, 0.285, 0.173, 0.0}, {-3.225, 4.697, -1.9, 0.95, 0.285, 0.0, 0.0}, {-3.05, -0.675, -0.98, 1.4, 4.75, 1.84, 0.0}, {-3.69, -0.3, 0.5, 0.1, 4.0, 1.0, 0.0}, {-3.38, -3.01, 0.5, 0.7, 0.08, 1.0, 0.0}, {-3.6, -2.65, 1.0, 0.2, 0.2, 2.0, 0.0}, {2.05, 2.35, 1.85, 1.8, 1.8, 7.5, 0.0}, {2.55, -0.25, 1.7, 0.6, 1.4, 7.2, 0.0}}, omgeving = {}}
local SEG = {{-18.08, 0.99, 0.0, -6.64, -4.19, 0.0, 4.2}, {-6.64, -4.19, 0.0, -3.7, -4.27, 0.0, 4.2}, {-3.7, -4.27, 0.0, 3.43, -4.44, 0.0, 4.2}, {3.43, -4.44, 0.0, 11.05, 0.05, 0.0, 4.2}, {11.05, 0.05, 0.0, 13.36, 0.44, 0.0, 4.2}, {13.36, 0.44, 0.0, 18.63, -1.34, 0.0, 4.2}}
local POLY = {{-17.37, 2.54}, {-16.42, 2.1}, {-15.1, 1.48}, {-13.53, 0.74}, {-11.83, -0.05}, {-10.11, -0.85}, {-8.48, -1.58}, {-7.09, -2.18}, {-6.04, -2.6}, {-5.4, -2.82}, {-5.1, -2.9}, {-5.18, -2.89}, {-5.48, -2.95}, {-5.48, -2.93}, {-5.04, -2.74}, {-4.4, -2.6}, {-3.66, -3.1}, {-2.84, -3.1}, {-2.0, -2.3}, {-1.14, -2.3}, {-0.26, -2.3}, {0.61, -2.3}, {1.45, -2.3}, {2.24, -2.3}, {2.95, -2.81}, {3.7, -2.53}, {4.6, -2.07}, {5.58, -1.48}, {6.6, -0.82}, {7.6, -0.13}, {8.56, 0.52}, {9.46, 1.11}, {10.24, 1.55}, {10.81, 1.84}, {11.21, 2.03}, {11.6, 2.2}, {12.15, 2.33}, {12.73, 2.32}, {13.1, 2.25}, {13.34, 2.18}, {13.73, 2.1}, {14.36, 1.95}, {15.11, 1.73}, {15.9, 1.46}, {16.71, 1.17}, {17.5, 0.89}, {18.2, 0.62}, {18.78, 0.41}, {19.2, 0.26}, {18.06, -2.94}, {17.62, -2.78}, {17.02, -2.56}, {16.32, -2.3}, {15.56, -2.02}, {14.8, -1.75}, {14.08, -1.51}, {13.47, -1.33}, {12.98, -1.22}, {12.58, -1.13}, {12.3, -1.06}, {12.28, -1.05}, {12.55, -1.05}, {12.74, -1.01}, {12.65, -1.05}, {12.32, -1.21}, {11.85, -1.44}, {11.23, -1.79}, {10.45, -2.31}, {9.52, -2.94}, {8.48, -3.65}, {7.39, -4.36}, {6.25, -5.04}, {5.09, -5.63}, {3.92, -6.07}, {2.74, -6.33}, {1.58, -6.43}, {0.47, -6.42}, {-0.59, -6.34}, {-1.56, -6.22}, {-2.44, -6.1}, {-3.18, -6.01}, {-3.74, -5.97}, {-4.02, -5.98}, {-4.02, -5.99}, {-3.99, -5.99}, {-4.32, -6.14}, {-5.02, -6.29}, {-5.71, -6.24}, {-6.39, -6.07}, {-7.24, -5.78}, {-8.4, -5.32}, {-9.86, -4.69}, {-11.52, -3.94}, {-13.26, -3.14}, {-14.98, -2.34}, {-16.55, -1.6}, {-17.86, -0.98}, {-18.79, -0.55}}
local F = Vector3.new(0.098, 0, -0.995)
local ORIGIN = CFrame.new(228.0, 7.7, 137.85) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local ZG = -1.9
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(228, 224, 214), "Plastic"}, natuursteen = {Color3.fromRGB(150, 146, 136), "Plastic"}, lei = {Color3.fromRGB(92, 66, 48), "Slate"},
	hout = {Color3.fromRGB(60, 40, 26), "Wood"}, balk = {Color3.fromRGB(66, 42, 26), "Wood"}, zuil = {Color3.fromRGB(198, 160, 82), "Wood"},
	venster = {Color3.fromRGB(14, 16, 18), "SmoothPlastic"}, kijkglas = {Color3.fromRGB(200, 210, 210), "SmoothPlastic"},
	glasoranje = {Color3.fromRGB(255, 176, 90), "Neon"}, ijzer = {Color3.fromRGB(22, 22, 22), "Metal"}, pieckblauw = {Color3.fromRGB(46, 92, 136), "WoodPlanks"},
	tegel = {Color3.fromRGB(168, 72, 44), "Brick"}, rood = {Color3.fromRGB(160, 26, 20), "SmoothPlastic"}, geel = {Color3.fromRGB(220, 170, 40), "SmoothPlastic"},
	groen = {Color3.fromRGB(34, 98, 54), "WoodPlanks"}, goud = {Color3.fromRGB(205, 160, 60), "Metal"}, klimop = {Color3.fromRGB(36, 64, 26), "Grass"},
	brandhout = {Color3.fromRGB(128, 92, 58), "Wood"}, zink = {Color3.fromRGB(150, 154, 154), "Metal"}, interieur = {Color3.fromRGB(80, 54, 38), "Wood"},
	gordijn = {Color3.fromRGB(150, 28, 26), "Fabric"}, glaslamp = {Color3.fromRGB(255, 220, 160), "Neon"},
	grind = {Color3.fromRGB(235, 228, 214), "Pebble"}, flagstone = {Color3.fromRGB(150, 140, 128), "Slate"}, rots = {Color3.fromRGB(150, 150, 146), "Rock"},
}
local TINT = {stuc = Color3.fromRGB(236, 234, 228)}
local preload = {}

local function plaats(id, naam, pre, coll, org)
	org = org or ORIGIN
	local objs = game:GetObjects("rbxassetid://" .. id)
	local oud = workspace:FindFirstChild(naam); if oud then oud:Destroy() end
	local m = Instance.new("Model"); m.Name = naam
	for _, o in ipairs(objs) do o.Parent = m end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
	for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
	m.Parent = workspace; m:ScaleTo(S)
	local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "MAT_anker") then anker = p end end
	m:PivotTo(org * CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
	local bots = Instance.new("Folder"); bots.Name = "Botsing"; bots.Parent = m
	local lampen = Instance.new("Folder"); lampen.Name = "Lampen"; lampen.Parent = m
	local onbekend = {}
	for _, p in ipairs(m:GetChildren()) do
		if not p:IsA("BasePart") then continue end
		p.Anchored = true; p.CanTouch = false; p.CanCollide = false; p.CanQuery = false
		if string.match(p.Name, "^COLL_") then p:Destroy()
		elseif string.match(p.Name, "^LAMP_") then
			p.Transparency = 1; p.CastShadow = false; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Name = "Lamp"; p.Parent = lampen
			local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 176, 96); pl.Range = 12; pl.Brightness = 1.2; pl.Shadows = true; pl.Parent = p
		else
			local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$"); local key = string.match(p.Name, "__MAT_([%w_]-)_%d+$")
			if tex and TEX[pre][tex] then
				p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
				local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[pre][tex][1]
				if TEX[pre][tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[pre][tex][2] end
				if TINT[tex] then sa.Color = TINT[tex] end
				sa.Parent = p; table.insert(preload, sa.ColorMap)
				if tex == "rots" then p.CanQuery = true end
			elseif key and M[key] then
				p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
				if key == "glasoranje" or key == "glaslamp" then p.Transparency = 0.15; p.CastShadow = false end
				if key == "kijkglas" then p.Transparency = 0.93; p.CastShadow = false end
				if key == "grind" or key == "flagstone" then
					pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end); p.CanQuery = true
					pcall(function() p.MaterialVariant = key == "grind" and "VV_Grind" or "" end)
				end
			else table.insert(onbekend, p.Name) end
		end
	end
	for _, c in ipairs(coll) do                                                   -- botsblokken: [cx, cy, cz, sx, sy, sz, hoek om z]
		local b = Instance.new("Part"); b.Name = "Bots"; b.Anchored = true; b.Transparency = 1; b.CastShadow = false; b.CanTouch = false
		b.Size = Vector3.new(c[4] * S, math.max(c[6] * S, 0.05), c[5] * S)
		b.CFrame = lokaal(c[1], c[2], c[3]) * CFrame.Angles(0, math.rad(c[7]), 0); b.Parent = bots
	end
	m.WorldPivot = ORIGIN
	return m, onbekend
end

local mh, oh = plaats(HUIS, "Roodkapje", "RK", COLL.huisje)
local PADO = ORIGIN - Vector3.new(0, 1.9 * S, 0)                               -- Daan: grindpad gewoon vlak op het maaiveld (Y 2)
local mo, oo = plaats(OMG, "RoodkapjeOmgeving", "RO", COLL.omgeving, PADO)
-- kaars achter het gevelraam flakkert licht (2016)
for _, l in ipairs(mh.Lampen:GetChildren()) do
	local pl = l:FindFirstChildOfClass("PointLight"); local lp = ORIGIN:PointToObjectSpace(l.Position)
	if lp.Y / S > 4 then pl.Range = 8; pl.Brightness = 0.8; pl.Shadows = false
	elseif lp.Y / S > 1.5 and lp.Y / S < 2.2 then pl.Range = 10; pl.Brightness = 0.6 end   -- kamer achter de kijkramen
end

-- terrein (Daan): overal vlak maaiveld (oppervlak Y 2), huisje staat er op volle hoogte op; vennetje (OSM 766787195)
local T = workspace.Terrain; local oc = ORIGIN.Position
T:FillBlock(CFrame.new(oc.X, 20, oc.Z), Vector3.new(170, 40, 170), Enum.Material.Air)
T:FillBlock(CFrame.new(oc.X, -4, oc.Z), Vector3.new(170, 8, 170), Enum.Material.LeafyGrass)
local vc = lokaal(-13.8, 8.8, ZG).Position
T:FillCylinder(CFrame.new(vc.X, -4.5, vc.Z), 5, 3.6 * S, Enum.Material.Ground)
T:FillCylinder(CFrame.new(vc.X, -0.6, vc.Z), 3.6, 3.25 * S, Enum.Material.Water)
local nT = 0
-- layout-label weg, spawn op het kijkplein (oude plek bewaard)
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do if d.Name == "Roodkapje" then d:Destroy() end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then
	if sp:GetAttribute("OudeCFrame") == nil then sp:SetAttribute("OudeCFrame", tostring(sp.CFrame)) end
	sp.CFrame = (PADO * CFrame.new(0.6 * S, 0.3, -6.5 * S)) * CFrame.Angles(0, math.pi, 0)
end
-- texturen voorladen
local ok = 0
pcall(function()
	local dec = {}; for _, id in ipairs(preload) do local d = Instance.new("Decal"); d.Texture = id; table.insert(dec, d) end
	game:GetService("ContentProvider"):PreloadAsync(dec, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end)
end)
local function onb(t) return #t > 0 and table.concat(t, ",") or "-" end
return string.format("huisje %d delen, omgeving %d; terrein %d kolommen; texturen %d/%d; onbekend %s %s", #mh:GetChildren(), #mo:GetChildren(), nT, ok, #preload, onb(oh), onb(oo))
