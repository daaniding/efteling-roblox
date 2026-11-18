-- plaats_archipel: Archipel (watervariant 2022) in Studio neerzetten (bron models/AR_Archipel; ids in exports/asset_ids.txt).
-- Plakken in de Studio-commandbalk als roblox/plaats_archipel_plak.luau (build/12_plak.py vult __KADE__ en __LAMPEN__ in).
-- Plek: plan.OORSPRONG park (452; 160) m -> Roblox X = 3x, Z = -3y; z 0 van het model = waterpeil = Y 0,3 (gelijk aan het
-- terreinwater van de Sirocco: het bassin loopt onder de wachtrijbrug door naar de Sirocco-vijver, lemma).
-- Doet: 1 terrein (zuid van de Sirocco-terreinvierkant aanvullen met maaiveld, onder het bad + 2 m eromheen uitgraven),
--       2 modellen bad / hutten / decor (FBX, ScaleTo 3, anker), materialen per rol (SurfaceAppearance of kleur),
--       3 helder water (doorzichtige plaat, licht turquoise), lantaarnlichten, onzichtbare veiligheidsbodem.
local S = 3
local OX, OY = 452.0, 160.0
local Y_WATER = 0.3
local MIDDEN = Vector3.new(OX * S, Y_WATER, -OY * S)
local ID = {bad = 87930230245683, hutten = 89842596638249, decor = 118897396045673,
	bamboe_kleur = 89297020656114, bamboe_normaal = 75619166799939, beton_kleur = 87816252063293, beton_normaal = 72004645257573,
	epdm_kleur = 75224572213473, epdm_normaal = 102928600834174, krul_kleur = 116067981025114, plank_kleur = 107984478123281,
	plank_normaal = 137730226067081, riet_kleur = 127354412668466, riet_normaal = 98365109290797, stam_kleur = 84797547258242,
	stam_normaal = 97259270336681,
	-- Sirocco (zelfde Sindbad-stijl)
	romp_kleur = 137095365073521, schubben_kleur = 92127248105221, net_kleur = 123171354911724, mand_kleur = 112674595994674}
local KADE = __KADE__         -- plan.KADE, parkmeters
local LAMPEN = __LAMPEN__     -- export_info.json, modelmeters (x oost, y noord, z boven water)
local KANAAL_EIND_Y = 174.9

-- rol -> {textuur, normaal, kleur (tint of effen), materiaal, botsen, extra}
local R = {
	beton = {"beton_kleur", "beton_normaal", Color3.new(1, 1, 1), Enum.Material.Concrete, true},
	kade = {"beton_kleur", "beton_normaal", Color3.fromRGB(240, 236, 228), Enum.Material.Concrete, true},
	epdm = {"epdm_kleur", "epdm_normaal", Color3.new(1, 1, 1), Enum.Material.Fabric, true},
	aarde = {nil, nil, Color3.fromRGB(86, 70, 52), Enum.Material.Ground, true},
	water = {nil, nil, Color3.fromRGB(96, 196, 200), Enum.Material.Glass, false, "water"},
	riet = {"riet_kleur", "riet_normaal", Color3.new(1, 1, 1), Enum.Material.Fabric, true},
	bamboe = {"bamboe_kleur", "bamboe_normaal", Color3.new(1, 1, 1), Enum.Material.Wood, true},
	raam = {nil, nil, Color3.fromRGB(22, 17, 13), Enum.Material.SmoothPlastic, false},
	stam = {"stam_kleur", "stam_normaal", Color3.new(1, 1, 1), Enum.Material.Wood, true},
	plank = {"plank_kleur", "plank_normaal", Color3.new(1, 1, 1), Enum.Material.WoodPlanks, true},
	touw = {"mand_kleur", nil, Color3.fromRGB(242, 218, 180), Enum.Material.Fabric, false},
	net = {"net_kleur", nil, Color3.fromRGB(230, 205, 160), Enum.Material.Fabric, true, "alfa"},
	piron = {nil, nil, Color3.fromRGB(46, 44, 48), Enum.Material.Metal, false},
	romp = {"romp_kleur", nil, Color3.fromRGB(184, 128, 108), Enum.Material.Wood, true},
	schubben = {"schubben_kleur", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	krul = {"krul_kleur", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	goud = {nil, nil, Color3.fromRGB(214, 168, 72), Enum.Material.Metal, false},
	mast = {"stam_kleur", "stam_normaal", Color3.fromRGB(128, 92, 72), Enum.Material.Wood, true},
	vlag = {nil, nil, Color3.fromRGB(178, 38, 30), Enum.Material.Fabric, false},
	lantaarn = {nil, nil, Color3.fromRGB(78, 56, 32), Enum.Material.Metal, false},
	lantaarnglas = {nil, nil, Color3.fromRGB(255, 176, 90), Enum.Material.Neon, false, "glas"},
	kist_blauw = {"plank_kleur", "plank_normaal", Color3.fromRGB(184, 242, 255), Enum.Material.WoodPlanks, true},
	kist_rood = {"plank_kleur", "plank_normaal", Color3.fromRGB(255, 184, 153), Enum.Material.WoodPlanks, true},
	kist_hout = {"plank_kleur", "plank_normaal", Color3.fromRGB(255, 242, 217), Enum.Material.WoodPlanks, true},
	ijzer = {nil, nil, Color3.fromRGB(46, 43, 41), Enum.Material.Metal, false},
	ton = {"plank_kleur", "plank_normaal", Color3.fromRGB(255, 204, 153), Enum.Material.Wood, true},
	tondeksel = {nil, nil, Color3.fromRGB(178, 56, 40), Enum.Material.SmoothPlastic, true},
	huid = {nil, nil, Color3.fromRGB(196, 146, 112), Enum.Material.SmoothPlastic, false},
	tulband = {nil, nil, Color3.fromRGB(236, 226, 200), Enum.Material.Fabric, false},
	baard = {nil, nil, Color3.fromRGB(190, 188, 184), Enum.Material.Fabric, false},
	hemd = {nil, nil, Color3.fromRGB(30, 52, 108), Enum.Material.Fabric, false},
	sjerp = {nil, nil, Color3.fromRGB(216, 108, 38), Enum.Material.Fabric, false},
	broek = {nil, nil, Color3.fromRGB(114, 30, 42), Enum.Material.Fabric, false},
	hengel = {nil, nil, Color3.fromRGB(40, 28, 18), Enum.Material.Wood, false},
	vis = {nil, nil, Color3.fromRGB(230, 128, 50), Enum.Material.SmoothPlastic, false},
}

local function binnen(x, y, P)
	local c, j = false, #P
	for i = 1, #P do
		local a, b = P[i], P[j]
		if (a[2] > y) ~= (b[2] > y) and x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1] then c = not c end
		j = i
	end
	return c
end
local function afstand(x, y, P)
	local d, j = 1e9, #P
	for i = 1, #P do
		local ax, ay, bx, by = P[j][1], P[j][2], P[i][1], P[i][2]
		local vx, vy = bx - ax, by - ay
		local t = math.clamp(((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy + 1e-9), 0, 1)
		d = math.min(d, math.sqrt((x - ax - t * vx) ^ 2 + (y - ay - t * vy) ^ 2)); j = i
	end
	return d
end

-- 1 terrein ------------------------------------------------------------------------------------------------------------
-- a) zuid van y 151,5 is er nog niets: maaiveld zoals de Sirocco (voxels vol tot Y 0, laag [0,4] bezetting 0,725 -> Y 0,9-1,0)
-- b) onder het bad en 2 m eromheen leeg tot Y -4 (de modelbodem ligt tot Y -1,2; de maaiveldrand dekt de rand van de cellen)
--    behalve in het kanaal voorbij KANAAL_EIND_Y (Sirocco-vijver)
local t = workspace.Terrain
local x0 = math.floor(432 * S / 4) * 4; local x1 = math.ceil(474 * S / 4) * 4
local z0 = math.floor(-179 * S / 4) * 4; local z1 = math.ceil(-136 * S / 4) * 4
local nx, nz = (x1 - x0) / 4, (z1 - z0) / 4
local NY = 9                                     -- Y -32 .. 4
local curM, curO = t:ReadVoxels(Region3.new(Vector3.new(x0, -32, z0), Vector3.new(x1, 4, z1)), 4)
local mat, occ = {}, {}
local nUit, nNieuw = 0, 0
for ix = 1, nx do
	mat[ix], occ[ix] = {}, {}
	for iy = 1, NY do mat[ix][iy], occ[ix][iy] = {}, {} end
	for iz = 1, nz do
		local cx, cz = x0 + (ix - 0.5) * 4, z0 + (iz - 0.5) * 4
		local px, py = cx / S, -cz / S
		local inBad = py < KANAAL_EIND_Y and (binnen(px, py, KADE) or afstand(px, py, KADE) < 2.0)
		local leeg = curO[ix][NY - 1][iz] < 0.05 and curO[ix][NY][iz] < 0.05 and curO[ix][NY - 2][iz] < 0.05
		for iy = 1, NY do
			local m, o = curM[ix][iy][iz], curO[ix][iy][iz]
			if leeg and py < 152.5 then                -- nieuw maaiveld (Ground eronder, LeafyGrass bovenop)
				if iy <= NY - 2 then m, o = Enum.Material.Ground, 1
				elseif iy == NY - 1 then m, o = Enum.Material.LeafyGrass, 1
				else m, o = Enum.Material.LeafyGrass, 0.725 end
				nNieuw += iy == NY and 1 or 0
			end
			if inBad then
				if iy >= NY - 1 then m, o = Enum.Material.Air, 0
				elseif iy == NY - 2 then m, o = Enum.Material.Ground, 0.5 end
				nUit += iy == NY and 1 or 0
			end
			mat[ix][iy][iz], occ[ix][iy][iz] = m, o
		end
	end
end
t:WriteVoxels(Region3.new(Vector3.new(x0, -32, z0), Vector3.new(x1, 4, z1)), 4, mat, occ)

-- 2 modellen -----------------------------------------------------------------------------------------------------------
local oud = workspace:FindFirstChild("Archipel"); if oud then oud:Destroy() end
local arch = Instance.new("Model"); arch.Name = "Archipel"; arch.Parent = workspace
arch.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
local function laad(id, naam)
	local m = Instance.new("Model"); m.Name = naam
	for _, o in ipairs(game:GetObjects("rbxassetid://" .. id)) do o.Parent = m end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
	for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
	m.Parent = arch; m:ScaleTo(S)
	local anker
	for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
	m:PivotTo(CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot())
	anker:Destroy(); m.WorldPivot = CFrame.new()
	m:PivotTo(CFrame.new(MIDDEN) * CFrame.Angles(0, math.pi, 0))
	return m
end
local onbekend = {}
for naam, id in pairs({Bad = ID.bad, Hutten = ID.hutten, Decor = ID.decor}) do
	local m = laad(id, naam)
	for _, p in ipairs(m:GetChildren()) do
		local rol = string.match(p.Name, "^AR_(.-)_%d+_%a+$") or "?"
		local r = R[rol]
		p.Anchored = true; p.CanTouch = false
		pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end)
		if not r then table.insert(onbekend, p.Name); continue end
		p.Color = r[3]; p.Material = r[4]; p.CanCollide = r[5]; p.CanQuery = r[5]
		p.CastShadow = rol ~= "net" and rol ~= "lantaarnglas" and rol ~= "water"
		if r[1] then
			local sa = Instance.new("SurfaceAppearance")
			sa.ColorMap = "rbxassetid://" .. ID[r[1]]
			if r[2] then sa.NormalMap = "rbxassetid://" .. ID[r[2]] end
			if r[6] == "alfa" then sa.AlphaMode = Enum.AlphaMode.Transparency end
			sa.Color = r[3]
			sa.Parent = p
		end
		if r[6] == "glas" then p.Transparency = 0.15 end
		if r[6] == "water" then p.Transparency = 0.55; p.Reflectance = 0.12; p.Name = "Water" end
		if p.CanCollide then pcall(function() p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end) end
	end
end

-- 3 lichten in de lantaarns (warm, zwak) en een onzichtbare veiligheidsbodem onder het hele bad -----------------------
local lichten = Instance.new("Folder"); lichten.Name = "Lichten"; lichten.Parent = arch
for _, l in ipairs(LAMPEN) do
	local p = Instance.new("Part"); p.Name = "lantaarnlicht"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.Transparency = 1; p.Size = Vector3.new(0.3, 0.3, 0.3)
	p.Position = MIDDEN + Vector3.new(l[1] * S, l[3] * S, -l[2] * S); p.Parent = lichten
	local pl = Instance.new("PointLight"); pl.Color = Color3.fromRGB(255, 180, 110); pl.Brightness = 0.7; pl.Range = 12; pl.Shadows = true; pl.Parent = p
end
local b = Instance.new("Part"); b.Name = "Veiligheidsbodem"; b.Anchored = true; b.Transparency = 1; b.CanCollide = true; b.CanQuery = false
b.Size = Vector3.new(29 * S, 1, 26 * S); b.CFrame = CFrame.new(Vector3.new(453.5 * S, -2.0, -157 * S)); b.Parent = arch   -- bovenkant Y -1,5 (diepste bodem Y -1,14), niet onder de Sirocco-vijver

local n = 0
for _, d in ipairs(arch:GetDescendants()) do if d:IsA("BasePart") then n += 1 end end
return string.format("Archipel geplaatst: %d delen, terrein: %d kolommen uitgegraven, %d nieuw maaiveld%s", n, nUit, nNieuw,
	#onbekend > 0 and (", onbekende rol: " .. table.concat(onbekend, ", ")) or "")
