-- Pinokkio (2016): La Bottega di Geppetto, poort, nis met tonnen, haventje met de Monstervis. Gegenereerd (zie AR_Pinokkio/roblox).
-- Modelframe: oorsprong = zwaartepunt BAG 405610268 = studs (149.16, 182.31), -Y = voorkant (NNW), +X rechts, z 0 = maaiveld (Y 2).
local DECOR, VIS = 78091187202022, 107964315615239
local TEX = {hout = {135398517813701, 100765783346756}, natuursteen = {103639676208001, 76435187966873}, pannen = {96109976006370, 102725977247735}, stuc = {139546814490719, 113074033279602}}
local COLL = {{-0.35, 0.44, 1.6, 4.9, 3.28, 3.2, 0.0}, {-2.31, -2.52, 1.275, 0.36, 0.36, 2.55, 0.0}, {-1.15, -2.52, 1.275, 0.36, 0.36, 2.55, 0.0}, {0.5, -2.52, 1.275, 0.36, 0.36, 2.55, 0.0}, {1.61, -2.52, 1.275, 0.36, 0.36, 2.55, 0.0}, {3.262, 1.571, 1.0, 2.34, 0.35, 2.0, 2.934}, {6.044, 1.717, 1.0, 0.428, 0.35, 2.0, 3.173}, {6.79, 1.773, 1.0, 1.068, 0.35, 2.0, 4.731}, {7.595, 1.184, 1.0, 1.378, 0.35, 2.0, -66.648}, {5.13, 1.67, 1.0, 2.4, 0.3, 2.0, 0.0}, {8.13, -0.07, 1.3, 1.7, 1.0, 2.6, -30}, {7.197, -0.686, 0.475, 0.64, 0.64, 0.95, 0.0}, {7.703, -1.209, 0.427, 0.576, 0.576, 0.855, 0.0}, {8.441, -1.231, 0.522, 0.704, 0.704, 1.045, 0.0}, {6.527, -0.646, 0.404, 0.544, 0.544, 0.807, 0.0}, {7.713, -1.792, 0.38, 0.512, 0.512, 0.76, 0.0}, {7.157, -1.356, 0.475, 0.64, 0.64, 0.95, 0.0}, {8.469, -1.882, 0.427, 0.576, 0.576, 0.855, 0.0}, {6.507, 0.198, 0.6, 3.101, 0.15, 1.2, -80.739}, {6.88, -1.509, 0.6, 0.433, 0.15, 1.2, -55.044}, {7.255, -1.731, 0.6, 0.51, 0.15, 1.2, -10.044}, {7.833, -1.571, 0.6, 0.772, 0.15, 1.2, 32.073}, {8.387, -1.224, 0.6, 0.536, 0.15, 1.2, 31.99}, {13.199, -2.053, 0.6, 1.428, 0.15, 1.2, -66.354}, {13.436, -3.353, 0.6, 1.296, 0.15, 1.2, -94.317}, {12.987, -4.6, 0.6, 1.443, 0.15, 1.2, -123.754}, {11.804, -5.484, 0.6, 1.664, 0.15, 1.2, -160.007}, {10.379, -5.668, 0.6, 1.3, 0.15, 1.2, 171.079}, {9.472, -5.93, 0.6, 0.9, 0.15, 1.2, -126.163}, {9.394, -6.335, 0.6, 0.385, 0.15, 1.2, -12.382}, {13.036, -8.757, 0.6, 8.389, 0.15, 1.2, -34.579}}
local VIJVER = {{9.96, -5.99}, {9.58, -6.38}, {16.49, -11.14}, {16.71, -10.88}, {19.86, -12.5}, {21.78, -13.08}, {23.08, -13.14}, {24.33, -13.01}, {25.53, -12.47}, {26.05, -11.14}, {26.5, -9.67}, {27.92, -8.55}, {29.59, -8.43}, {30.5, -7.5}, {30.61, -6.14}, {29.96, -5.09}, {28.93, -4.62}, {27.51, -3.98}, {26.25, -2.98}, {25.73, -1.38}, {22.42, -0.42}, {22.4, -1.77}, {21.51, -2.96}, {20.35, -3.16}, {19.55, -2.91}, {18.67, -1.83}, {17.95, -0.74}, {17.17, -0.01}, {15.92, 0.48}, {14.54, 0.32}, {13.76, -0.49}, {13.78, -1.62}, {14.09, -3.47}, {13.82, -4.49}, {13.12, -5.43}, {12.31, -5.98}, {11.39, -6.29}, {9.96, -5.99}}
local PLEIN = {{9.21, -6.29}, {9.74, -5.57}, {11.02, -5.77}, {12.59, -5.2}, {13.39, -4.0}, {13.49, -2.71}, {12.91, -1.4}, {11.93, -0.61}, {10.61, -0.38}, {9.28, -0.68}, {8.61, -1.08}, {8.16, -1.37}, {7.51, -1.78}, {7.0, -1.69}, {6.76, -1.33}, {6.26, 1.73}, {5.13, 1.67}, {2.09, 1.51}, {2.1, -0.08}, {2.12, -2.7}, {-2.79, -2.7}, {-2.81, -0.18}, {-4.32, -0.67}, {-5.93, -1.77}, {-6.22, -3.44}, {-5.12, -5.52}, {-2.18, -6.9}, {-0.38, -8.36}, {-0.05, -10.2}, {1.23, -9.95}, {3.04, -9.0}, {6.87, -9.24}, {8.09, -7.49}, {9.21, -6.29}}
local F = Vector3.new(-0.364, 0, -0.931)
local ORIGIN = CFrame.new(149.16, 2.0, 182.31) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(226, 214, 190), "Plastic"}, pannen = {Color3.fromRGB(150, 86, 60), "ClayRoofTiles"}, hout = {Color3.fromRGB(62, 42, 28), "Wood"}, balk = {Color3.fromRGB(58, 40, 28), "Wood"},
	teal = {Color3.fromRGB(70, 122, 122), "WoodPlanks"}, venster = {Color3.fromRGB(14, 16, 18), "SmoothPlastic"}, glasoranje = {Color3.fromRGB(255, 180, 100), "Neon"},
	ijzer = {Color3.fromRGB(22, 22, 22), "Metal"}, natuursteen = {Color3.fromRGB(196, 188, 170), "Limestone"}, flagstone = {Color3.fromRGB(176, 160, 140), "Slate"},
	baksteen = {Color3.fromRGB(150, 82, 60), "Brick"}, goud = {Color3.fromRGB(205, 160, 60), "Metal"}, bord = {Color3.fromRGB(222, 196, 146), "SmoothPlastic"},
	touw = {Color3.fromRGB(160, 132, 90), "Fabric"}, vat = {Color3.fromRGB(110, 74, 42), "Wood"}, wit = {Color3.fromRGB(236, 236, 230), "SmoothPlastic"},
	blauw = {Color3.fromRGB(52, 108, 180), "SmoothPlastic"}, grind = {Color3.fromRGB(235, 228, 214), "Pebble"}, rood = {Color3.fromRGB(180, 40, 28), "SmoothPlastic"},
	visoranje = {Color3.fromRGB(222, 108, 58), "SmoothPlastic"}, vislicht = {Color3.fromRGB(240, 156, 104), "SmoothPlastic"}, mond = {Color3.fromRGB(205, 90, 92), "SmoothPlastic"},
	keel = {Color3.fromRGB(70, 16, 16), "SmoothPlastic"}, tand = {Color3.fromRGB(244, 240, 222), "SmoothPlastic"}, oog = {Color3.fromRGB(240, 214, 50), "SmoothPlastic"},
	pupil = {Color3.fromRGB(8, 8, 8), "SmoothPlastic"}, water = {Color3.fromRGB(34, 46, 32), "SmoothPlastic"},
}
local TINT = {stuc = Color3.fromRGB(240, 234, 222)}
local preload = {}
local function plaats(id, naam, coll)
	local objs = game:GetObjects("rbxassetid://" .. id)
	local oud = workspace:FindFirstChild(naam); if oud then oud:Destroy() end
	local m = Instance.new("Model"); m.Name = naam
	for _, o in ipairs(objs) do o.Parent = m end
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
		if string.match(p.Name, "^COLL_") then p:Destroy()
		elseif string.match(p.Name, "^LAMP_") then
			p.Transparency = 1; p.CastShadow = false; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Name = "Lamp"; p.Parent = lampen
			local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 176, 96); pl.Range = 9; pl.Brightness = 0.7; pl.Shadows = false; pl.Parent = p
		else
			local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$"); local key = string.match(p.Name, "__MAT_([%w_]-)_%d+$")
			if tex and TEX[tex] then
				p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
				local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
				if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
				if TINT[tex] then sa.Color = TINT[tex] end
				sa.Parent = p; table.insert(preload, sa.ColorMap)
			elseif key and M[key] then
				p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
				if key == "grind" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end); p.CanQuery = true; pcall(function() p.MaterialVariant = "VV_Grind" end) end
				if key == "water" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end); p.Reflectance = 0.08; p.CastShadow = false end
				if key == "visoranje" or key == "vislicht" then p.CanCollide = false end
			else table.insert(onbekend, p.Name) end
		end
	end
	for _, c in ipairs(coll) do
		local b = Instance.new("Part"); b.Name = "Bots"; b.Anchored = true; b.Transparency = 1; b.CastShadow = false; b.CanTouch = false
		b.Size = Vector3.new(c[4] * S, math.max(c[6] * S, 0.05), c[5] * S)
		b.CFrame = lokaal(c[1], c[2], c[3]) * CFrame.Angles(0, math.rad(c[7]), 0); b.Parent = bots
	end
	m.WorldPivot = ORIGIN
	return m, onbekend
end
local md, od = plaats(DECOR, "Pinokkio", COLL)
local mv, ov = plaats(VIS, "PinokkioMonstervis", {})
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
-- terrein: vijver uitgraven (oppervlak zakt naar Y -2, de waterplaat ligt op Y 1.55), elders vlak maaiveld
local T = workspace.Terrain; local n = 0
for gx = -6, 34, 4 / S do
	for gy = -18, 8, 4 / S do
		local w = (ORIGIN * CFrame.new(-gx * S, 0, gy * S)).Position
		local X, Z = math.floor(w.X / 4) * 4 + 2, math.floor(w.Z / 4) * 4 + 2
		local l = ORIGIN:PointToObjectSpace(Vector3.new(X, ORIGIN.Position.Y, Z)); local x, y = -l.X / S, l.Z / S
		if inside(x, y, VIJVER) then T:FillBlock(CFrame.new(X, 2, Z), Vector3.new(4, 12, 4), Enum.Material.Air); T:FillBlock(CFrame.new(X, -6, Z), Vector3.new(4, 4, 4), Enum.Material.Ground); n += 1 end
	end
	task.wait()
end
-- planten van Roodkapje die op het plein of in de vijver staan weghalen; layout-label weg; spawn op het plein
local weg = 0
for _, f in ipairs({workspace:FindFirstChild("RoodkapjeGroen")}) do
	for _, c in ipairs(f:GetChildren()) do
		local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
		if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
			if inside(x, y, VIJVER) or inside(x, y, PLEIN) or (x > -3.5 and x < 9.5 and y > -3.2 and y < 2.6) then c:Destroy(); weg += 1 end end
	end
end
local lay = workspace:FindFirstChild("EftelingLayout")
if lay then for _, d in ipairs(lay:GetDescendants()) do if d.Name == "Pinokkio" or d.Name == "Monstervis" or d.Name == "La Bottega di Geppetto" then d:Destroy() end end end
local sp = workspace:FindFirstChildOfClass("SpawnLocation")
if sp then sp.CFrame = lokaal(0, -7.5, 0.15) * CFrame.Angles(0, math.pi, 0) end
local ok = 0
pcall(function()
	local dec = {}; for _, id in ipairs(preload) do local d = Instance.new("Decal"); d.Texture = id; table.insert(dec, d) end
	game:GetService("ContentProvider"):PreloadAsync(dec, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end)
end)
local function onb(t) return #t > 0 and table.concat(t, ",") or "-" end
return string.format("decor %d, vis %d; vijvercellen %d; planten weg %d; texturen %d/%d; onbekend %s %s", #md:GetChildren(), #mv:GetChildren(), n, weg, ok, #preload, onb(od), onb(ov))
