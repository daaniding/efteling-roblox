-- plaats_instaphalgloed: FataMorgana.Instaphalgloed = onzichtbare strips 0,15 m voor de achterwanden op z 3,15 met een SurfaceLight
-- naar beneden (amber), zodat de wanden achter de gaanderij gloeien zoals op de video. Opnieuw draaien vervangt de oude.
local fm = workspace.FataMorgana
local oud = fm:FindFirstChild("Instaphalgloed"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Instaphalgloed"
local function W(x, y, z) return Vector3.new(3 * x, 0.91 + 3 * z, -3 * y) end
local XW, XE, YS, YN = -3.5, 16.6, -348.4, -323.6
local function strip(a, b)
	local n = math.max(1, math.floor((b - a).Magnitude / 5 + 0.5))
	for i = 0, n - 1 do
		local p0 = a + (b - a) * (i / n); local p1 = a + (b - a) * ((i + 1) / n)
		local P0, P1 = W(p0.X, p0.Y, 3.15), W(p1.X, p1.Y, 3.15)
		local p = Instance.new("Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.Locked = true
		p.Transparency = 1; p.CastShadow = false; p.Name = "Gloed"
		p.Size = Vector3.new((P1 - P0).Magnitude, 0.2, 0.2); p.CFrame = CFrame.lookAt((P0 + P1) / 2, P1) * CFrame.Angles(0, math.pi / 2, 0)
		local l = Instance.new("SurfaceLight"); l.Face = Enum.NormalId.Bottom; l.Angle = 120; l.Range = 10; l.Brightness = 2.5
		l.Color = Color3.fromRGB(255, 168, 90); l.Shadows = false; l.Parent = p
		p.Parent = m
	end
end
local d = 0.15
strip(Vector2.new(XW + d, YN - d), Vector2.new(13.2, YN - d)); strip(Vector2.new(15.0, YN - d), Vector2.new(XE - d, YN - d))
strip(Vector2.new(XW + d, YS + d), Vector2.new(XE - d, YS + d))
strip(Vector2.new(XW + d, YS + d), Vector2.new(XW + d, YN - d))
strip(Vector2.new(XE - d, YS + d), Vector2.new(XE - d, -330.0)); strip(Vector2.new(XE - d, -328.0), Vector2.new(XE - d, YN - d))
m.Parent = fm
return #m:GetChildren() .. " gloedstrips"
