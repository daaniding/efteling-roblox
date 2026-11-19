-- plaats_s1c: sectie 1c (jungle met fata morgana) in Studio zetten (Daan 19 nov: "Ja, 1c"). Video POV 2025 129-140 s.
--  1. model Junglegroen (22_s1c_jungle, asset hieronder) met bladtexturen (alfa) uit 22t_s1c_texturen
--  2. Achterdoek: plat paneel op de westwand (x -11,45) met de geschilderde lucht als zelflichtende afbeelding (SurfaceGui, weinig
--     lichtinvloed: in de video gloeit het doek paars/oranje in een verder donkere jungle)
--  3. Paleis: klein paneel net voor het doek (y -326,2, 1,6 x 1,2 m, onderkant z -2,75); FataMorganaS1Paleis laat het verschijnen
--     als een sloep uit de grot komt en weer verdwijnen in de bocht ("even te zien, dat ook snel weer verdwijnt", Eftepedia)
--  4. licht: oranje van onder op de bamboe en de grote stam, groengeel van boven, rood laag, paarse gloed van het doek
local S = 3
local VOET = Vector3.new(-40 * S, 0.91, 295 * S)
local ID = {model = 127687374489355, achterdoek = 128378863936010, paleis = 98008676791415, palmblad = 109569546046403,
	bamboeblad = 83792121693498, breedblad = 137518965679118, liaan = 85371245112909, heliconia = 73349063077042}
local fm = workspace:WaitForChild("FataMorgana")
local function W(x, y, z) return Vector3.new(S * x, 0.91 + S * z, -S * y) end   -- modelmeters -> studs

local oud = fm:FindFirstChild("Junglegroen"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Junglegroen"
for _, o in ipairs(game:GetObjects("rbxassetid://" .. ID.model)) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = fm; m:ScaleTo(S)
local anker
for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
m:PivotTo(CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot())
anker:Destroy(); m.WorldPivot = CFrame.new()
m:PivotTo(CFrame.new(VOET) * CFrame.Angles(0, math.pi, 0))
local VAST = {stam = {Color3.fromRGB(92, 98, 58), Enum.Material.Wood}, bamboe = {Color3.fromRGB(200, 150, 82), Enum.Material.Wood},
	oever = {Color3.fromRGB(46, 38, 28), Enum.Material.Ground}}
for _, p in m:GetChildren() do
	local rol = string.match(p.Name, "^FM_(.-)_%d+_%a+$")
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.Locked = true
	pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end)
	if VAST[rol] then
		p.Color = VAST[rol][1]; p.Material = VAST[rol][2]
	elseif ID[rol] then
		p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.SmoothPlastic; p.CastShadow = false
		local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. ID[rol]; sa.AlphaMode = Enum.AlphaMode.Transparency; sa.Parent = p
	end
end

local function paneel(naam, x, y0, y1, z0, z1, beeld, transp)
	local p = Instance.new("Part"); p.Name = naam; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.CastShadow = false; p.Locked = true; p.Color = Color3.new(0, 0, 0); p.Material = Enum.Material.SmoothPlastic
	p.Size = Vector3.new(0.2, S * (z1 - z0), S * (y1 - y0)); p.Transparency = transp and 1 or 0
	p.CFrame = CFrame.new(W(x, (y0 + y1) / 2, (z0 + z1) / 2))
	local sg = Instance.new("SurfaceGui"); sg.Face = Enum.NormalId.Right; sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 40; sg.LightInfluence = 0.1; sg.Brightness = 1.1; sg.Parent = p
	local im = Instance.new("ImageLabel"); im.Name = "Beeld"; im.Size = UDim2.fromScale(1, 1); im.BackgroundTransparency = 1
	im.Image = "rbxassetid://" .. beeld; im.ScaleType = Enum.ScaleType.Stretch; im.Parent = sg
	p.Parent = m
	return p, im
end
paneel("Achterdoek", -11.45, -329.1, -320.1, -3.4, 4.4, ID.achterdoek, false)
local pal, pim = paneel("Paleis", -11.3, -327.0, -325.4, -2.75, -1.55, ID.paleis, true)
pim.ImageTransparency = 1; pal:SetAttribute("Zichtbaar", 0.05)

local function lamp(naam, van, naar, kleur, helderheid, bereik, hoek)
	local p = Instance.new("Part"); p.Name = naam; p.Size = Vector3.new(0.4, 0.4, 0.4); p.Transparency = 1; p.Anchored = true
	p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false; p.Locked = true
	p.CFrame = CFrame.lookAt(W(table.unpack(van)), W(table.unpack(naar)))
	local l = hoek and Instance.new("SpotLight") or Instance.new("PointLight")
	if hoek then l.Face = Enum.NormalId.Front; l.Angle = hoek end
	l.Color = kleur; l.Brightness = helderheid; l.Range = bereik; l.Shadows = false; l.Parent = p
	p.Parent = m
end
lamp("LichtBamboe", {-6.6, -327.6, -2.9}, {-8.2, -328.6, 1.5}, Color3.fromRGB(255, 150, 60), 1.3, 18, 50)
lamp("LichtStam", {-6.2, -327.2, -2.5}, {-9.0, -325.8, 0.8}, Color3.fromRGB(255, 180, 100), 0.8, 20, 40)
lamp("LichtBoven", {-8.5, -323.0, 4.2}, {-8.5, -324.5, -2.5}, Color3.fromRGB(150, 210, 110), 0.6, 22, 60)
lamp("LichtRood", {-10.0, -321.4, -2.9}, {-10.6, -322.0, 1.0}, Color3.fromRGB(255, 60, 40), 1.0, 14, 55)
lamp("LichtRoodZuid", {-9.5, -328.6, -2.9}, {-10.5, -328.8, 0.5}, Color3.fromRGB(255, 80, 40), 0.8, 12, 55)
lamp("GloedDoek", {-10.6, -326.2, 0.5}, {-8.0, -326.2, -1.0}, Color3.fromRGB(190, 110, 255), 0.7, 16, nil)
lamp("GloedHorizon", {-10.9, -326.2, -2.6}, {-8.0, -326.2, -2.0}, Color3.fromRGB(255, 150, 70), 0.6, 12, nil)
return "ok"
