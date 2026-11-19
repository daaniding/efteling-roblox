-- plaats_s1d: sectie 1d (donkere jungle met slangen) in Studio zetten (Daan 19 nov: "Ja, 1d"). Video POV 2025 141-174 s.
--  1. model Junglenacht (23_s1d_jungle) met dezelfde bladtexturen als 1c + slangenhuid en rode bloemtrossen
--  2. licht zoals in de video: rood/oranje op het overhangende bamboeblad, blauw op de rotspartijen, groenblauw accent op de
--     varenpalmen, roze op de lianen, warm rood op de knoestboom; alles verder donker
--  3. vuurschalen: Fire + flakkerend licht (FataMorganaS1Slangen laat ook de vlammen flakkeren)
local S = 3
local VOET = Vector3.new(-40 * S, 0.91, 295 * S)
local ID = {model = 124230487417588, palmblad = 109569546046403, bamboeblad = 83792121693498, breedblad = 137518965679118,
	liaan = 85371245112909, bloemrood = 125918842490881, slanga = 133491784805467, slangb = 133491784805467, slangc = 133491784805467}
local fm = workspace:WaitForChild("FataMorgana")
local function W(x, y, z) return Vector3.new(S * x, 0.91 + S * z, -S * y) end

local oud = fm:FindFirstChild("Junglenacht"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Junglenacht"
for _, o in ipairs(game:GetObjects("rbxassetid://" .. ID.model)) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = fm; m:ScaleTo(S)
local anker
for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
m:PivotTo(CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot())
anker:Destroy(); m.WorldPivot = CFrame.new()
m:PivotTo(CFrame.new(VOET) * CFrame.Angles(0, math.pi, 0))
local VAST = {stam = {Color3.fromRGB(80, 86, 50), Enum.Material.Wood}, bamboe = {Color3.fromRGB(190, 140, 78), Enum.Material.Wood},
	oever = {Color3.fromRGB(40, 33, 25), Enum.Material.Ground}, rots = {Color3.fromRGB(70, 72, 80), Enum.Material.Rock},
	boom = {Color3.fromRGB(72, 52, 38), Enum.Material.Wood}, schaal = {Color3.fromRGB(90, 78, 66), Enum.Material.Slate}}
for _, p in m:GetChildren() do
	local rol = string.match(p.Name, "^FM_(.-)_%d+_%a+$")
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.Locked = true
	pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end)
	if VAST[rol] then p.Color = VAST[rol][1]; p.Material = VAST[rol][2]
	elseif ID[rol] then
		p.Color = Color3.new(1, 1, 1); p.Material = Enum.Material.SmoothPlastic; p.CastShadow = string.sub(rol, 1, 5) == "slang"
		local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. ID[rol]
		if string.sub(rol, 1, 5) ~= "slang" then sa.AlphaMode = Enum.AlphaMode.Transparency end
		sa.Parent = p
	end
	if rol and string.sub(rol, 1, 5) == "slang" then p.Name = "Slang_" .. string.sub(rol, 6) end
end

local function lamp(naam, van, naar, kleur, helderheid, bereik, hoek)
	local p = Instance.new("Part"); p.Name = naam; p.Size = Vector3.new(0.4, 0.4, 0.4); p.Transparency = 1; p.Anchored = true
	p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false; p.Locked = true
	p.CFrame = CFrame.lookAt(W(table.unpack(van)), W(table.unpack(naar)))
	local l = hoek and Instance.new("SpotLight") or Instance.new("PointLight")
	if hoek then l.Face = Enum.NormalId.Front; l.Angle = hoek end
	l.Color = kleur; l.Brightness = helderheid; l.Range = bereik; l.Shadows = false; l.Parent = p
	p.Parent = m
	return p
end
lamp("RoodBladA", {0.5, -320.4, -2.9}, {1.5, -321.8, -0.4}, Color3.fromRGB(255, 50, 30), 1.4, 14, 60)
lamp("RoodBladB", {5.5, -318.4, -2.9}, {7.0, -320.0, 1.8}, Color3.fromRGB(255, 70, 30), 1.4, 18, 55)
lamp("OranjeBamboe", {3.6, -318.0, -2.8}, {4.6, -317.2, 1.5}, Color3.fromRGB(255, 140, 50), 1.1, 16, 45)
lamp("BlauwRotsA", {2.6, -319.6, -1.4}, {4.2, -321.6, -1.6}, Color3.fromRGB(70, 90, 255), 1.6, 14, 55)
lamp("BlauwRotsB", {9.6, -314.4, -1.0}, {12.0, -315.6, -1.2}, Color3.fromRGB(70, 90, 255), 1.4, 14, 55)
lamp("Groenblauw", {8.0, -318.2, 2.5}, {9.2, -319.4, -1.4}, Color3.fromRGB(60, 255, 200), 0.9, 14, 40)
lamp("RozeLianen", {6.0, -317.0, 3.6}, {6.0, -317.0, 0.0}, Color3.fromRGB(255, 90, 170), 0.8, 18, 80)
lamp("RoodBoom", {9.0, -316.6, -2.8}, {10.6, -318.2, 2.0}, Color3.fromRGB(255, 60, 40), 1.3, 18, 50)
lamp("Slangenlicht", {8.3, -315.2, -0.4}, {9.0, -317.0, 1.3}, Color3.fromRGB(255, 190, 120), 0.9, 12, 45)

-- vuurschalen: vlam boven elke schaal
local sch = m:FindFirstChild("FM_schaal_0_junglenacht")
if sch then
	sch.CanQuery = true
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {sch}
	for i, xy in {{3.2, -317.6}, {6.3, -319.9}, {11.4, -317.2}} do
		local hit = workspace:Raycast(W(xy[1], xy[2], 3), Vector3.new(0, -60, 0), rp)
		if hit then
			local v = Instance.new("Part"); v.Name = "Vuur" .. i; v.Size = Vector3.new(0.6, 0.6, 0.6); v.Transparency = 1; v.Anchored = true
			v.CanCollide = false; v.CanQuery = false; v.CanTouch = false; v.Locked = true; v.CFrame = CFrame.new(hit.Position + Vector3.new(0, 0.5, 0))
			local f = Instance.new("Fire"); f.Size = 2.2; f.Heat = 6; f.Color = Color3.fromRGB(255, 140, 40); f.SecondaryColor = Color3.fromRGB(255, 60, 20); f.Parent = v
			local l = Instance.new("PointLight"); l.Name = "Vlamlicht"; l.Color = Color3.fromRGB(255, 140, 50); l.Brightness = 1.4; l.Range = 10; l.Parent = v
			v.Parent = m
		end
	end
	sch.CanQuery = false
end
return "ok"
