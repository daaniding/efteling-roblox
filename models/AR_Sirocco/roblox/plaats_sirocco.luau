-- plaats_sirocco: Sirocco in Studio neerzetten (bron models/AR_Sirocco; ids in exports/asset_ids.txt). Plakken in de Studio-commandbalk.
-- Plek: dakmidden park (456,5; 191,2) m (luchtfoto) -> Roblox X = 3x, Z = -3y. Hoogte zoals de Pagode: gras NAP 9,8 (Y 1,4),
-- water 0,4 m lager (Y 0,2) = z 0 van het model; dek van de rit op Y 1,1.
-- Doet: terrein (vlak gras rond de vijver, vijver leeg), gebouw + rit (FBX, ScaleTo 3, anker), materialen per rol (SurfaceAppearance
-- of kleur), lichtpunten in de lantaarns, waterplaat + onzichtbare bodem.
local S = 3
local CX, CY = 456.5, 191.2
local Y_WATER = 0.2
local MIDDEN = Vector3.new(CX * S, Y_WATER, -CY * S)
local ID = {gebouw = 130218947819308, rit = 118252639030237,
	riet_kleur = 122992305053489, riet_normaal = 107154390027579, platform_kleur = 137087869566165, romp_kleur = 137095365073521,
	romp_hout_kleur = 92929270438539, schubben_kleur = 92127248105221, sierpaneel_kleur = 111038031156474, mand_kleur = 112674595994674,
	net_kleur = 123171354911724, beschot_kleur = 124186550110005, stam_kleur = 86277939897558, stam_normaal = 85501756974124,
	romp_blauw_kleur = 81733490640030, vlonder_kleur = 114168670349764, vlonder_normaal = 105858881415149, bamboe_kleur = 100311851570971}
local LAMPEN = __LAMPEN__     -- exports/export_info.json, modelmeters (x oost, y noord, z boven water)

-- rol -> {textuur, normaal, kleur (tint of effen), materiaal, botsen, extra}
local R = {
	riet = {"riet_kleur", "riet_normaal", Color3.fromRGB(205, 198, 186), Enum.Material.Fabric, true},
	beschot = {"beschot_kleur", nil, Color3.new(1, 1, 1), Enum.Material.Wood, false},
	stam = {"stam_kleur", "stam_normaal", Color3.new(1, 1, 1), Enum.Material.Wood, true},
	vlonder = {"vlonder_kleur", "vlonder_normaal", Color3.fromRGB(150, 140, 130), Enum.Material.WoodPlanks, true},
	platform = {"platform_kleur", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	subschijf = {"platform_kleur", nil, Color3.fromRGB(225, 235, 255), Enum.Material.SmoothPlastic, true},
	romp = {"romp_kleur", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	romp_hout = {"romp_hout_kleur", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	romp_blauw = {"romp_blauw_kleur", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	rood = {nil, nil, Color3.fromRGB(168, 34, 30), Enum.Material.SmoothPlastic, false},       -- rode rand, banden, voorsteven
	binnen = {nil, nil, Color3.fromRGB(92, 18, 20), Enum.Material.SmoothPlastic, true},      -- donkerrode binnenkant en bank
	golf = {nil, nil, Color3.fromRGB(232, 240, 248), Enum.Material.SmoothPlastic, false},    -- witte golf aan de boeg
	schubben = {"schubben_kleur", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	sierpaneel = {"sierpaneel_kleur", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, false},
	mand = {"mand_kleur", nil, Color3.new(1, 1, 1), Enum.Material.Fabric, false},
	net = {"net_kleur", nil, Color3.new(1, 1, 1), Enum.Material.Metal, false, "alfa"},
	bamboe = {nil, nil, Color3.fromRGB(196, 160, 96), Enum.Material.Wood, true},   -- effen (de Pagode-textuur is een plant met blaadjes)
	voet = {nil, nil, Color3.fromRGB(32, 78, 150), Enum.Material.SmoothPlastic, true},
	goud = {nil, nil, Color3.fromRGB(205, 160, 64), Enum.Material.Metal, false},
	zeil = {nil, nil, Color3.fromRGB(214, 200, 172), Enum.Material.Fabric, false},
	mast = {nil, nil, Color3.fromRGB(110, 78, 48), Enum.Material.Wood, false},
	touw = {nil, nil, Color3.fromRGB(176, 158, 120), Enum.Material.Fabric, false},
	kist = {nil, nil, Color3.fromRGB(96, 70, 46), Enum.Material.Wood, false},
	ton = {nil, nil, Color3.fromRGB(120, 82, 50), Enum.Material.Wood, true},
	fles = {nil, nil, Color3.fromRGB(92, 50, 20), Enum.Material.Glass, false},
	fruit_oranje = {nil, nil, Color3.fromRGB(240, 128, 20), Enum.Material.SmoothPlastic, false},
	fruit_geel = {nil, nil, Color3.fromRGB(240, 205, 40), Enum.Material.SmoothPlastic, false},
	fruit_groen = {nil, nil, Color3.fromRGB(70, 140, 40), Enum.Material.SmoothPlastic, false},
	lampion_oranje = {nil, nil, Color3.fromRGB(235, 120, 30), Enum.Material.SmoothPlastic, false},
	lampion_rood = {nil, nil, Color3.fromRGB(180, 35, 30), Enum.Material.SmoothPlastic, false},
	lampion_petrol = {nil, nil, Color3.fromRGB(30, 100, 110), Enum.Material.SmoothPlastic, false},
	lantaarn = {nil, nil, Color3.fromRGB(150, 110, 50), Enum.Material.Metal, false},
	lantaarnglas = {nil, nil, Color3.fromRGB(255, 170, 80), Enum.Material.Neon, false, "glas"},
}

-- 1 terrein: vlak gras (zoals bij de Pagode) in een vierkant van 70 m, de vijver (r 13.3 m) leeg tot ver onder het water
local t = workspace.Terrain
local G = 2
local top = G + (9.8 - 10) * S - 2
t:FillBlock(CFrame.new(MIDDEN.X, 6, MIDDEN.Z), Vector3.new(70 * S, 112, 70 * S), Enum.Material.Air)
for i = -35, 34 do
	for j = -35, 34 do
		local x, y = i + 0.5, j + 0.5
		if math.sqrt(x * x + y * y) > 13.6 then
			t:FillBlock(CFrame.new(MIDDEN.X + x * S, (top + (G - 30)) / 2, MIDDEN.Z - y * S), Vector3.new(S, top - (G - 30), S), Enum.Material.Grass)
		end
	end
end

-- 2 modellen
local oud = workspace:FindFirstChild("Sirocco"); if oud then oud:Destroy() end
local sir = Instance.new("Model"); sir.Name = "Sirocco"; sir.Parent = workspace
sir.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
local function laad(id, naam)
	local m = Instance.new("Model"); m.Name = naam
	for _, o in ipairs(game:GetObjects("rbxassetid://" .. id)) do o.Parent = m end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
	for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
	m.Parent = sir; m:ScaleTo(S)
	local anker
	for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
	m:PivotTo(CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot())
	anker:Destroy(); m.WorldPivot = CFrame.new()
	m:PivotTo(CFrame.new(MIDDEN) * CFrame.Angles(0, math.pi, 0))
	return m
end
local onbekend = {}
for naam, id in pairs({Gebouw = ID.gebouw, Rit = ID.rit}) do
	local m = laad(id, naam)
	for _, p in ipairs(m:GetChildren()) do
		local rol = string.match(p.Name, "^SI_(.-)_%d+_%a+$") or "?"
		local r = R[rol]
		p.Anchored = true; p.CanTouch = false
		pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end)   -- anders vallen kleine delen (schubben, golf, fruit) op afstand weg
		if not r then table.insert(onbekend, p.Name); continue end
		p.Color = r[3]; p.Material = r[4]; p.CanCollide = r[5]; p.CanQuery = r[5]
		p.CastShadow = rol ~= "net" and rol ~= "lantaarnglas"
		if r[1] then
			local sa = Instance.new("SurfaceAppearance")
			sa.ColorMap = "rbxassetid://" .. ID[r[1]]
			if r[2] then sa.NormalMap = "rbxassetid://" .. ID[r[2]] end
			if r[6] == "alfa" then sa.AlphaMode = Enum.AlphaMode.Transparency end
			sa.Color = r[3]
			sa.Parent = p
		end
		if r[6] == "glas" then p.Transparency = 0.15 end
		if p.CanCollide then pcall(function() p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end) end
	end
end

-- 3 lichtpunten in de lantaarns (warm, zwak, met schaduw; Pagode-les: niet overbelichten)
local lichten = Instance.new("Folder"); lichten.Name = "Lichten"; lichten.Parent = sir
for _, l in ipairs(LAMPEN) do
	local p = Instance.new("Part"); p.Name = "lantaarnlicht"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.Transparency = 1; p.Size = Vector3.new(0.3, 0.3, 0.3)
	p.Position = Vector3.new(MIDDEN.X + l[1] * S, MIDDEN.Y + l[3] * S, MIDDEN.Z - l[2] * S); p.Parent = lichten
	local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 180, 110); pl.Brightness = 0.8; pl.Range = 14; pl.Shadows = true; pl.Parent = p
end

-- 4 water: donkere troebele plaat (Glass spiegelt de lucht; WERKWIJZE) tot onder de grasrand, en een onzichtbare bodem
local w = Instance.new("Part"); w.Name = "Water"; w.Shape = Enum.PartType.Cylinder; w.Anchored = true; w.CanCollide = false; w.CanQuery = false
w.Size = Vector3.new(0.2, 14.2 * 2 * S, 14.2 * 2 * S); w.CFrame = CFrame.new(MIDDEN - Vector3.new(0, 0.1, 0)) * CFrame.Angles(0, 0, math.rad(90))
w.Material = Enum.Material.SmoothPlastic; w.Color = Color3.fromRGB(32, 52, 44); w.Transparency = 0.12; w.Reflectance = 0.05; w.Parent = sir
local b = w:Clone(); b.Name = "Vijverbodem"; b.Transparency = 1; b.CanCollide = true; b.Size = Vector3.new(1, 14.2 * 2 * S, 14.2 * 2 * S)
b.CFrame = CFrame.new(MIDDEN - Vector3.new(0, 4, 0)) * CFrame.Angles(0, 0, math.rad(90)); b.Parent = sir

local n = 0
for _, d in ipairs(sir:GetDescendants()) do if d:IsA("BasePart") then n += 1 end end
return "Sirocco geplaatst: " .. n .. " delen" .. (#onbekend > 0 and (", onbekende rol: " .. table.concat(onbekend, ", ")) or "")
