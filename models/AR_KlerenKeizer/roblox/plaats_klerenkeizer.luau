-- De Nieuwe Kleren van de Keizer (2012): decor (paleismuur, poort, theekoepel, voorbak, vijver) + paleistuin. Gegenereerd door maak_plaatsscript.py.
-- Modelframe: oorsprong = midden lange vijver, voorkant (naar de bezoekers) = -Y, z = 0 bezoekerspad, decorpeil 0.6 m.
local DECOR, OMG = 126400976252556, 128394215565121
local TEXD = {pleister = {80279594059020, 136901809327662}}
local HAAG = {73997585762296, 114509386598524}      -- haagtextuur (Herautenplein/Villa Volta)
local F = Vector3.new(0.116, 0, -0.993)
local ORIGIN = CFrame.new(-48.81, 2.0, -401.85) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	ornament = {Color3.fromRGB(244, 240, 228), "SmoothPlastic"}, goud = {Color3.fromRGB(214, 168, 72), "Metal"}, koepelglas = {Color3.fromRGB(132, 150, 176), "Glass"},
	venster = {Color3.fromRGB(28, 32, 40), "Glass"}, raamhout = {Color3.fromRGB(240, 236, 224), "SmoothPlastic"}, gordijn = {Color3.fromRGB(226, 218, 190), "Fabric"},
	water = {Color3.fromRGB(24, 32, 28), "Glass"}, bodem = {Color3.fromRGB(14, 14, 14), "SmoothPlastic"}, ijzer = {Color3.fromRGB(18, 18, 18), "Metal"},
	glaslamp = {Color3.fromRGB(255, 226, 170), "Glass"}, donker = {Color3.fromRGB(10, 10, 10), "SmoothPlastic"}, pleister = {Color3.fromRGB(236, 228, 208), "Plastic"},
	gras = {Color3.fromRGB(84, 120, 52), "Grass"}, tegels = {Color3.fromRGB(206, 196, 176), "Concrete"}, klinker = {Color3.fromRGB(214, 200, 176), "Cobblestone"},
	hout = {Color3.fromRGB(56, 88, 62), "WoodPlanks"}, beton = {Color3.fromRGB(160, 156, 148), "Concrete"}, aarde = {Color3.fromRGB(70, 56, 40), "Ground"}, boekband = {Color3.fromRGB(96, 52, 30), "Leather"}, papier = {Color3.fromRGB(236, 222, 186), "Fabric"},
}
local function plaats(asset, naam, TEX)
	local objs = game:GetObjects("rbxassetid://" .. asset)
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
		if string.match(p.Name, "^COLL_") then
			p.Transparency = 1; p.CanCollide = true; p.CanQuery = true; p.CastShadow = false; p.Parent = bots
			if p:IsA("MeshPart") then p.CollisionFidelity = Enum.CollisionFidelity.Box end
		elseif string.match(p.Name, "^LAMP_") then
			p.Transparency = 1; p.CastShadow = false; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Name = "Lamp"; p.Parent = lampen
			local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 196, 130); pl.Range = 10; pl.Brightness = 0.9; pl.Shadows = false; pl.Parent = p
		else
			local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$"); local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
			if tex and TEX and TEX[tex] then
				p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
				local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
				if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
				sa.Parent = p
			elseif key == "haag" then
				p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
				local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. HAAG[1]; sa.NormalMap = "rbxassetid://" .. HAAG[2]
				sa.Color = Color3.fromRGB(150, 175, 130); sa.Parent = p
				pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end)
			elseif key and M[key] then
				p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
				if key == "water" then p.Transparency = 0.15; p.Reflectance = 0.25; p.CastShadow = false end
				if key == "koepelglas" then p.Transparency = 0.15; p.Reflectance = 0.35 end
				if key == "venster" then p.Reflectance = 0.2 end
				if key == "gras" or key == "klinker" or key == "tegels" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end) end
				if key == "klinker" and game.MaterialService:FindFirstChild("EftelingKlinkers") then p.MaterialVariant = "EftelingKlinkers" end   -- beige visgraat (Boekloc)
			else table.insert(onbekend, p.Name) end
		end
	end
	m.WorldPivot = ORIGIN
	return m, onbekend
end

-- oude bomen/struiken binnen het decor en het kijkplein weg (rechthoek x -18..21, y -11..14)
local weg = 0
for _, f in ipairs(workspace:GetChildren()) do
	if string.find(f.Name, "Groen") or string.find(f.Name, "Bos") or string.find(f.Name, "Horizon") then
		for _, t in ipairs(f:GetChildren()) do
			local p = t:IsA("Model") and t:GetPivot().Position or (t:IsA("BasePart") and t.Position)
			if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
				if x > -18 and x < 21 and y > -11 and y < 14 then t:Destroy(); weg += 1 end end
		end
	end
end
-- terrein: Ground i.p.v. Grass onder het hele decor + plein (geen grassprieten door bestrating en gazon-platen)
local T = workspace.Terrain
local a, b = lokaal(-19, -12, 0).Position, lokaal(22, 15, 0).Position
local c1, c2 = lokaal(-19, 15, 0).Position, lokaal(22, -12, 0).Position
local mn = Vector3.new(math.min(a.X, b.X, c1.X, c2.X), -8, math.min(a.Z, b.Z, c1.Z, c2.Z))
local mx = Vector3.new(math.max(a.X, b.X, c1.X, c2.X), 6, math.max(a.Z, b.Z, c1.Z, c2.Z))
T:ReplaceMaterial(Region3.new(mn, mx):ExpandToGrid(4), 4, Enum.Material.Grass, Enum.Material.Ground)

local d, o1 = plaats(DECOR, "KlerenKeizerDecor", TEXD)
local om, o2 = plaats(OMG, "KlerenKeizerOmgeving", nil)
-- fonteinen: waterstralen (hoogte in m), zachte nevel aan de voet
local fm = Instance.new("Folder"); fm.Name = "Fonteinen"; fm.Parent = d
for i, f in ipairs({{-2.953, 9.138, 1.1, 0.9}, {3.153, 9.138, 1.1, 0.9}, {-6.6, 2.7, 1.2, 1.2}, {0.03, 2.2, 1.02, 1.4}, {-8.1, 0.0, 0.52, 1.6}, {8.0, 0.0, 0.52, 1.6}}) do
	local p = Instance.new("Part"); p.Name = "Fontein" .. i; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.Transparency = 1; p.Size = Vector3.new(0.3, 0.3, 0.3); p.CFrame = lokaal(f[1], f[2], f[3]); p.Parent = fm
	local h = f[4] * S; local g = workspace.Gravity; local v = math.sqrt(2 * g * h)
	local e = Instance.new("ParticleEmitter"); e.Name = "Straal"
	e.Texture = "rbxasset://textures/particles/smoke_main.dds"; e.Color = ColorSequence.new(Color3.fromRGB(235, 242, 248))
	e.LightEmission = 0.25; e.LightInfluence = 0.9; e.Orientation = Enum.ParticleOrientation.VelocityParallel
	e.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.25), NumberSequenceKeypoint.new(0.6, 0.45), NumberSequenceKeypoint.new(1, 0.7)})
	e.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.35), NumberSequenceKeypoint.new(0.7, 0.55), NumberSequenceKeypoint.new(1, 1)})
	e.EmissionDirection = Enum.NormalId.Top; e.Speed = NumberRange.new(v * 0.92, v); e.SpreadAngle = Vector2.new(4, 4)
	e.Acceleration = Vector3.new(0, -g, 0); e.Lifetime = NumberRange.new(2 * v / g * 0.95, 2 * v / g); e.Rate = 70; e.Drag = 0
	e.Parent = p
	local sp = Instance.new("ParticleEmitter"); sp.Name = "Spat"
	sp.Texture = "rbxasset://textures/particles/smoke_main.dds"; sp.Color = ColorSequence.new(Color3.fromRGB(240, 244, 248))
	sp.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.6), NumberSequenceKeypoint.new(1, 1.6)})
	sp.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.7), NumberSequenceKeypoint.new(1, 1)})
	sp.Speed = NumberRange.new(1, 3); sp.SpreadAngle = Vector2.new(80, 80); sp.Lifetime = NumberRange.new(0.6, 1.0); sp.Rate = 18; sp.LightInfluence = 0.9
	sp.Parent = p
end
local ids = {}
for _, v in pairs(TEXD) do for _, id in ipairs(v) do local dd = Instance.new("Decal"); dd.Texture = "rbxassetid://" .. id; table.insert(ids, dd) end end
for _, id in ipairs(HAAG) do local dd = Instance.new("Decal"); dd.Texture = "rbxassetid://" .. id; table.insert(ids, dd) end
local ok = 0; pcall(function() game:GetService("ContentProvider"):PreloadAsync(ids, function(_, st) if st == Enum.AssetFetchStatus.Success then ok += 1 end end) end)
local function onb(t) return #t > 0 and table.concat(t, ",") or "-" end
return string.format("decor %d (botsing %d), omgeving %d (botsing %d), fonteinen %d, bomen weg %d, tex %d/%d; onbekend %s %s",
	#d:GetChildren(), #d.Botsing:GetChildren(), #om:GetChildren(), #om.Botsing:GetChildren(), #fm:GetChildren(), weg, ok, #ids, onb(o1), onb(o2))
