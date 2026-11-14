-- Sfeer Sprookjesbos (Daan: "vetter, realistisch en dromerig, alsof je echt in die wereld zit").
-- Bovenop park/belichting_schemer.luau: zonnestralen door de bomen, gloed, warme kleur, zachte verte, zwevend sprookjesstof
-- (gouden stofjes/vuurvliegjes) en lage nevel boven gras en water. Alleen ingebouwde Roblox-texturen (rbxasset://), geen externe assets.
-- Gebied: rond De Zes Zwanen (uitbreiden door GEBIEDEN aan te vullen). Uitvoeren in Edit (Command Bar of MCP).
local L = game:GetService("Lighting")
-- nieuwe Roblox-belichting: stijl Realistic + kwaliteit voorrang (Technology is hiermee vervangen; scripts mogen Technology niet zetten)
L.LightingStyle = Enum.LightingStyle.Realistic
L.PrioritizeLightingQuality = true

-- zon en lucht: iets hoger zodat er gouden licht tussen de stammen valt, met lange schaduwen
L.ClockTime = 17.6
L.Brightness = 3.2
L.ExposureCompensation = 0.3
L.EnvironmentDiffuseScale = 1; L.EnvironmentSpecularScale = 1
L.ShadowSoftness = 0.25
L.ColorShift_Top = Color3.fromRGB(255, 205, 150)
local a = L:FindFirstChildOfClass("Atmosphere")
a.Density = 0.38; a.Offset = 0.25; a.Haze = 2.4; a.Glare = 1.6
a.Color = Color3.fromRGB(232, 200, 172); a.Decay = Color3.fromRGB(158, 116, 142)
local sr = L:FindFirstChildOfClass("SunRaysEffect"); sr.Intensity = 0.16; sr.Spread = 0.75
local bl = L:FindFirstChildOfClass("BloomEffect"); bl.Intensity = 1.1; bl.Size = 42; bl.Threshold = 1.15
local cc = L:FindFirstChildOfClass("ColorCorrectionEffect"); cc.Contrast = 0.16; cc.Saturation = 0.1; cc.TintColor = Color3.fromRGB(255, 236, 214); cc.Brightness = 0.02
local dof = L:FindFirstChildOfClass("DepthOfFieldEffect"); dof.FarIntensity = 0.28; dof.FocusDistance = 45; dof.InFocusRadius = 55; dof.NearIntensity = 0

-- lantaarns: warmer, iets groter bereik, schaduwen aan (zichtbaar met Lighting.Technology = Future)
for _, d in ipairs(workspace:GetDescendants()) do
	if d:IsA("PointLight") and d.Parent and d.Parent.Parent and d.Parent.Parent.Name == "Lampen" then
		d.Color = Color3.fromRGB(255, 184, 104); d.Brightness = 1.6; d.Range = 18; d.Shadows = true
	end
end

-- zwevend sprookjesstof en lage nevel
local F = Vector3.new(0.1076, 0, 0.9942)
local ORIGIN = CFrame.new(-108.77, 2.0, -301.0) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local GEBIEDEN = {   -- {naam, middelpunt (modelframe m), grootte (m)}
	{"ZesZwanen", Vector3.new(4, -9, 0), Vector3.new(36, 40, 0)},
}
local oud = workspace:FindFirstChild("Sfeer"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "Sfeer"
local function bron(naam, cf, size)
	local p = Instance.new("Part"); p.Name = naam; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.Transparency = 1; p.CastShadow = false; p.Size = size; p.CFrame = cf; p.Parent = map; return p
end
for _, g in ipairs(GEBIEDEN) do
	local c = ORIGIN * CFrame.new(-g[2].X * 3, 0, g[2].Y * 3)
	local sx, sz = g[3].X * 3, g[3].Y * 3
	-- gouden stofjes: traag zwevend, licht gevend, flonkerend
	local s = bron(g[1] .. "_stof", c * CFrame.new(0, 7, 0), Vector3.new(sx, 10, sz))
	local e = Instance.new("ParticleEmitter"); e.Name = "Sprookjesstof"
	e.Texture = "rbxasset://textures/particles/sparkles_main.dds"
	e.Color = ColorSequence.new(Color3.fromRGB(255, 222, 150), Color3.fromRGB(255, 190, 120))
	e.LightEmission = 1; e.LightInfluence = 0; e.Brightness = 2.5
	e.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.2, 0.22), NumberSequenceKeypoint.new(0.8, 0.18), NumberSequenceKeypoint.new(1, 0)})
	e.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.25, 0.15), NumberSequenceKeypoint.new(0.75, 0.3), NumberSequenceKeypoint.new(1, 1)})
	e.Lifetime = NumberRange.new(6, 10); e.Rate = 26; e.Speed = NumberRange.new(0.2, 0.7); e.SpreadAngle = Vector2.new(180, 180)
	e.Acceleration = Vector3.new(0, 0.08, 0); e.Drag = 0.6; e.RotSpeed = NumberRange.new(-40, 40); e.Rotation = NumberRange.new(0, 360)
	e.Shape = Enum.ParticleEmitterShape.Box; e.ShapeInOut = Enum.ParticleEmitterShapeInOut.Outward; e.ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume
	e.Parent = s
	-- lage nevel: grote zachte wolkjes vlak boven de grond en het water
	local n = bron(g[1] .. "_nevel", c * CFrame.new(0, 1.5, 0), Vector3.new(sx, 1, sz))
	local m = Instance.new("ParticleEmitter"); m.Name = "Nevel"
	m.Texture = "rbxasset://textures/particles/smoke_main.dds"
	m.Color = ColorSequence.new(Color3.fromRGB(236, 222, 214))
	m.LightEmission = 0.15; m.LightInfluence = 0.8
	m.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 6), NumberSequenceKeypoint.new(1, 12)})
	m.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.35, 0.86), NumberSequenceKeypoint.new(0.7, 0.88), NumberSequenceKeypoint.new(1, 1)})
	m.Lifetime = NumberRange.new(14, 20); m.Rate = 4; m.Speed = NumberRange.new(0.1, 0.4); m.SpreadAngle = Vector2.new(180, 10)
	m.RotSpeed = NumberRange.new(-6, 6); m.Rotation = NumberRange.new(0, 360); m.Drag = 0.3
	m.Shape = Enum.ParticleEmitterShape.Box; m.ShapeStyle = Enum.ParticleEmitterShapeStyle.Volume
	m.Parent = n
end
map.Parent = workspace
return "sfeer gezet"
