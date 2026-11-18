-- plaats_wachtrijlicht: warm geelbruin licht onder de bollampen in de wachtrijhal (Daan 18 nov: "de lichtsfeer een beetje geel
-- bruinig ... ik bedoelde de lichten bij de wachtrij"). Posities = 08_zuidvleugel (rijen y -342,0 en -345,6; x 19,2 + 3,4 k tot
-- 57; bolmidden 2,78 m). Onzichtbare ankertjes met een PointLight in FataMorgana.Wachtrijlicht. Opnieuw draaien = vervangen.
local S, Y0 = 3, 0.91
local fm = workspace:WaitForChild("FataMorgana")
local oud = fm:FindFirstChild("Wachtrijlicht"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "Wachtrijlicht"; map.Parent = fm
local n = 0
for _, y in ipairs({-342.0, -345.6}) do
	local x = 17.2 + 2.0
	while x < 58.0 - 1.0 do
		local p = Instance.new("Part")
		p.Name = "Lamp"; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Transparency = 1; p.Anchored = true; p.Locked = true
		p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
		p.Position = Vector3.new(x * S, Y0 + 2.6 * S, -y * S)
		local l = Instance.new("PointLight")
		l.Color = Color3.fromRGB(255, 186, 112); l.Brightness = 0.45; l.Range = 11; l.Shadows = false; l.Parent = p
		p.Parent = map; n += 1
		x += 3.4
	end
end
return "wachtrijlicht: " .. n .. " lampen"
