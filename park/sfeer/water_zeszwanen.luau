-- Spiegelend terreinwater in de vijvers van De Zes Zwanen (i.p.v. de vlakke waterplaat): kasteel, lucht en lantaarns spiegelen, rimpelingen.
-- Waterpeil = WL -0.35 m = Y 0.95. Terrein onder de vijvers was al weggegraven (plaats_zeszwanen.luau). De waterplaat-meshes worden onzichtbaar.
local F = Vector3.new(0.1076, 0, 0.9942)
local ORIGIN = CFrame.new(-108.77, 2.0, -301.0) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local VIJ = {{{-5.47,-3.96},{-6.33,-5.8},{-5.74,-7.56},{-6.2,-9.15},{-5.23,-10.76},{-5.78,-12.03},{-6.19,-13.01},{-7.39,-13.66},{-7.82,-15.28},{-7.84,-16.83},{-6.61,-16.58},{-5.17,-15.7},{-3.85,-13.81},{-2.89,-13.55},{-0.95,-13.14},{-0.87,-12.52},{1.88,-12.9},{1.83,-13.24},{4.07,-13.27},{6.05,-12.52},{7.65,-11.13},{8.63,-9.39},{9.13,-7.56},{9.18,-6.41},{9.23,-5.5},{8.76,-3.33},{7.84,-1.54},{7.1,0.31},{5.53,-2.45},{1.84,-2.46},{0.53,-3.49},{0.76,-3.82},{-0.68,-5.16},{-1.88,-5.43},{-3.13,-5.09}},{{-1.6,-20.6},{0.67,-22.64},{2.51,-22.21},{3.89,-22.42},{5.5,-22.25},{6.76,-21.77},{8.09,-21.12},{9.75,-19.65},{11.57,-18.83},{12.7,-18.79},{13.75,-18.16},{13.68,-17.21},{12.75,-17.12},{12.14,-16.32},{10.99,-15.72},{9.4,-15.88},{6.98,-16.36},{3.31,-18.17},{0.76,-18.96}},{{13.53,0.46},{13.8,1.33},{14.54,2},{15.93,2.52},{17.93,2.3},{19.4,1.51},{20.22,0.08},{20.71,-1.05},{19.97,-2.11},{19.46,-3.02},{18.36,-3.02},{17.78,-1.94},{17.81,-0.66},{16.72,0.1},{15.96,0.21},{14.92,-0.59},{13.85,-0.42}}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local T = workspace.Terrain
local PEIL, BODEM = 0.95, -6
local n = 0
for i = -36, -10 do
	for j = -86, -55 do
		local X, Z = i * 4 + 2, j * 4 + 2
		local l = ORIGIN:PointToObjectSpace(Vector3.new(X, 0, Z)); local mx, my = -l.X / 3, l.Z / 3
		local nat = false; for _, v in ipairs(VIJ) do if inside(mx, my, v) then nat = true; break end end
		if nat then T:FillBlock(CFrame.new(X, (BODEM + PEIL) / 2, Z), Vector3.new(4, PEIL - BODEM, 4), Enum.Material.Water); n += 1 end
	end
end
T.WaterColor = Color3.fromRGB(22, 32, 22)       -- donker troebel groenbruin (foto's); hoge reflectie maakte het melkig-beige door de lichte lucht
T.WaterReflectance = 0.18; T.WaterTransparency = 0.04; T.WaterWaveSize = 0.03; T.WaterWaveSpeed = 3
local om = workspace:FindFirstChild("ZesZwanenOmgeving")
if om then for _, p in ipairs(om:GetChildren()) do if p:IsA("BasePart") and string.find(p.Name, "MAT_water") then p.Transparency = 1 end end end
return "watercellen " .. n
