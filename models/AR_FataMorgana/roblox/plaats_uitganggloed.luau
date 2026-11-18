-- plaats_uitganggloed: FataMorgana.Uitganggloed = onzichtbare strips 0,15 m voor de wanden net onder de lichtlijst, met een
-- SurfaceLight naar beneden (crème-amber), zodat de wanden van het uitganghalletje en De Bazaar gloeien zoals de gang op de
-- video 2020. Opnieuw draaien vervangt de oude.
local fm = workspace.FataMorgana
local oud = fm:FindFirstChild("Uitganggloed"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Uitganggloed"
local function W(x, y, z) return Vector3.new(3 * x, 0.91 + 3 * z, -3 * y) end
local function strip(a, b, z)
	local n = math.max(1, math.floor((b - a).Magnitude / 4 + 0.5))
	for i = 0, n - 1 do
		local p0 = a + (b - a) * (i / n); local p1 = a + (b - a) * ((i + 1) / n)
		local P0, P1 = W(p0.X, p0.Y, z), W(p1.X, p1.Y, z)
		local p = Instance.new("Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.Locked = true
		p.Transparency = 1; p.CastShadow = false; p.Name = "Gloed"
		p.Size = Vector3.new((P1 - P0).Magnitude, 0.2, 0.2); p.CFrame = CFrame.lookAt((P0 + P1) / 2, P1) * CFrame.Angles(0, math.pi / 2, 0)
		local l = Instance.new("SurfaceLight"); l.Face = Enum.NormalId.Bottom; l.Angle = 120; l.Range = 9; l.Brightness = 2
		l.Color = Color3.fromRGB(255, 205, 150); l.Shadows = false; l.Parent = p
		p.Parent = m
	end
end
local d = 0.15
-- halletje (x 12,9..17,5, y -315,6..-301,3, plafond 2,45)
strip(Vector2.new(12.9 + d, -315.6 + d), Vector2.new(12.9 + d, -301.3 - d), 2.3)
strip(Vector2.new(17.5 - d, -315.6 + d), Vector2.new(17.5 - d, -301.3 - d), 2.3)
-- De Bazaar (x 17,83..24,17, y -313,67..-301,33, plafond 2,9)
strip(Vector2.new(17.83 + d, -313.67 + d), Vector2.new(17.83 + d, -301.33 - d), 2.75)
strip(Vector2.new(24.17 - d, -313.67 + d), Vector2.new(24.17 - d, -301.33 - d), 2.75)
strip(Vector2.new(17.83 + d, -301.33 - d), Vector2.new(24.17 - d, -301.33 - d), 2.75)
strip(Vector2.new(17.83 + d, -313.67 + d), Vector2.new(24.17 - d, -313.67 + d), 2.75)
m.Parent = fm
return #m:GetChildren() .. " gloedstrips"
