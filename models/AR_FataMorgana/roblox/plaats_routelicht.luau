-- plaats_routelicht: eenvoudig werklicht in de (nog kale) vaarroute, zodat je de route en kamers ziet (18_route). Elke ~7 m boven de
-- vaargoot op z -1,2 een warme PointLight. Punten uit ref/route_plan.npz ("lichten"). Opnieuw draaien vervangt de oude.
local PUNTEN = {{-36.0,-304.0},{-29.0,-304.0},{-22.0,-304.0},{-64.0,-311.0},{-57.0,-311.0},{-36.0,-311.0},{-29.0,-311.0},{-15.0,-311.0},{-8.0,-311.0},{-1.0,-311.0},{6.0,-311.0},{-64.0,-318.0},{-50.0,-318.0},{-43.0,-318.0},{-36.0,-318.0},{-22.0,-318.0},{6.0,-318.0},{-64.0,-325.0},{-57.0,-325.0},{-36.0,-325.0},{-8.0,-325.0},{-64.0,-332.0},{-57.0,-332.0},{-43.0,-332.0},{-15.0,-346.0},{-8.0,-346.0}}
local fm = workspace.FataMorgana
local oud = fm:FindFirstChild("Routelicht"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Routelicht"
for _, q in PUNTEN do
	local p = Instance.new("Part"); p.Name = "Werklicht"; p.Size = Vector3.new(0.3, 0.3, 0.3); p.Transparency = 1
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.Locked = true; p.CastShadow = false
	p.Position = Vector3.new(3 * q[1], 0.91 + 3 * -1.2, -3 * q[2])
	local l = Instance.new("PointLight"); l.Brightness = 0.5; l.Range = 26; l.Color = Color3.fromRGB(255, 214, 170); l.Shadows = true; l.Parent = p
	p.Parent = m
end
m.Parent = fm
return #m:GetChildren() .. " werklichten"
