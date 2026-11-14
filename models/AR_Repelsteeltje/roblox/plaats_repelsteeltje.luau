-- Repelsteeltje (1998): huisje met boomstronk, tuintje, flagstone-pad, rook uit de schoorsteen. Gegenereerd door maak_plaatsscript.py.
-- Modelframe: oorsprong = OSM-zwaartepunt 55424159, voorkant (lange zijde naar het pad) = -Y, x = noordwest, z = 0 maaiveld.
local HUIS = 117899351879218
local TEX = {hout = {99082309397853, 115019765819126}, lei = {131914434331664, 114556734739171}, natuursteen = {111335625044990, 83334889747680}, schors = {139396603556077, 121169761742180}, stuc = {115920716872165, 129410613250780}}
local F = Vector3.new(0.533, 0, -0.846)
local ORIGIN = CFrame.new(351.75, 2.0, -425.94) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local M = {
	stuc = {Color3.fromRGB(220, 216, 206), "Plastic"}, natuursteen = {Color3.fromRGB(150, 146, 136), "Plastic"}, lei = {Color3.fromRGB(90, 84, 76), "Slate"},
	hout = {Color3.fromRGB(56, 38, 26), "Wood"}, schors = {Color3.fromRGB(110, 84, 60), "Wood"}, blauwgroen = {Color3.fromRGB(46, 92, 96), "WoodPlanks"},
	venster = {Color3.fromRGB(14, 16, 18), "Glass"}, glasoranje = {Color3.fromRGB(255, 170, 80), "Neon"}, ijzer = {Color3.fromRGB(20, 20, 20), "Metal"},
	zink = {Color3.fromRGB(158, 162, 162), "Metal"}, deurgroen = {Color3.fromRGB(30, 72, 56), "WoodPlanks"}, flagstone = {Color3.fromRGB(176, 140, 128), "Slate"},
	papier = {Color3.fromRGB(236, 222, 186), "Fabric"}, rood = {Color3.fromRGB(140, 32, 22), "SmoothPlastic"}, baksteen = {Color3.fromRGB(150, 96, 72), "Brick"}, lei2 = {Color3.fromRGB(104, 92, 84), "Slate"}, mos = {Color3.fromRGB(80, 104, 46), "Grass"},
	gordijn = {Color3.fromRGB(220, 206, 172), "Fabric"}, klimop = {Color3.fromRGB(40, 70, 30), "Grass"}, brandhout = {Color3.fromRGB(120, 86, 56), "Wood"},
}
local TINT = {stuc = Color3.fromRGB(232, 230, 222), natuursteen = Color3.fromRGB(196, 190, 180)}
local objs = game:GetObjects("rbxassetid://" .. HUIS)
local oud = workspace:FindFirstChild("RepelsteeltjeHuisje"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "RepelsteeltjeHuisje"
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
		local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 176, 96); pl.Range = 12; pl.Brightness = 1.2; pl.Shadows = true; pl.Parent = p
	else
		local tex = string.match(p.Name, "__TEX_([%w_]+)_%d+$"); local key = string.match(p.Name, "__MAT_([%a_]+)_%d+$")
		if tex and TEX[tex] then
			p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.Plastic
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. TEX[tex][1]
			if TEX[tex][2] then sa.NormalMap = "rbxassetid://" .. TEX[tex][2] end
			if TINT[tex] then sa.Color = TINT[tex] end
			sa.Parent = p
		elseif key and M[key] then
			p.Color = M[key][1]; p.Material = Enum.Material[M[key][2]]
			if key == "glasoranje" then p.Transparency = 0.2; p.CastShadow = false end
			if key == "flagstone" then pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end); p.CFrame = p.CFrame + Vector3.new(0, 0.3, 0) end   -- net boven het terreinoppervlak
		else table.insert(onbekend, p.Name) end
	end
end
m.WorldPivot = ORIGIN
-- rook uit de schoorsteen (lemma: "uit het schoorsteentje komt rook")
local rp_ = Instance.new("Part"); rp_.Name = "Rook"; rp_.Anchored = true; rp_.CanCollide = false; rp_.CanQuery = false; rp_.CanTouch = false
rp_.Transparency = 1; rp_.Size = Vector3.new(0.3, 0.3, 0.3); local r = {2.9400000000000004, 0.9100000000000001, 5.9}; rp_.CFrame = lokaal(r[1], r[2], r[3]); rp_.Parent = m
local e = Instance.new("ParticleEmitter"); e.Texture = "rbxasset://textures/particles/smoke_main.dds"; e.Color = ColorSequence.new(Color3.fromRGB(200, 198, 196))
e.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.6), NumberSequenceKeypoint.new(1, 4.5)})
e.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.55), NumberSequenceKeypoint.new(0.6, 0.8), NumberSequenceKeypoint.new(1, 1)})
e.Speed = NumberRange.new(2, 3.5); e.SpreadAngle = Vector2.new(12, 12); e.Lifetime = NumberRange.new(4, 6); e.Rate = 6; e.Acceleration = Vector3.new(1.2, 0.4, 0.5)
e.RotSpeed = NumberRange.new(-20, 20); e.Rotation = NumberRange.new(0, 360); e.LightInfluence = 0.9; e.Parent = rp_
local function onb(t) return #t > 0 and table.concat(t, ",") or "-" end
return string.format("huisje %d (botsing %d, lampen %d); onbekend %s", #m:GetChildren(), #bots:GetChildren(), #lampen:GetChildren(), onb(onbekend))
