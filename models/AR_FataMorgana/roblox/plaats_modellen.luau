-- plaats_modellen: alle Fata Morgana-modellen (toren, noordgevel, ...) opnieuw laden met één materiaaltabel. Terrein staat in
-- plaats_toren.luau / plaats_noordgevel.luau (alleen nodig bij een lege plek). Ids: exports/asset_ids.txt.
-- Oorsprong van alle delen: park (-40; -295) op het maaiveld Y 0,91. Verwering = losse overlays (vlek1..4, streep, voet) met alfa.
local S = 3
local VOET = Vector3.new(-40 * S, 0.91, 295 * S)
local DELEN = {Toren = 110489236755029, Noordgevel = 123092455544461, Minaret = 104784345799444, Ingang = 128192677817318, Kantelen = 122963827182511, Koepelgebouw = 71346500842552, Zuidvleugel = 75793335061309, Westkant = 113707068029447, Achterkant = 75413093437862, Veranda = 105227491479681, Instaphal = 123463686820231, Boten = 88656466555036, Route = 92807235297587, Junglegordijn = 78226160726058, Junglerots = 78718607249001}   -- 1c/1d: plaats_s1c.luau en plaats_s1d.luau (eigen texturen/licht)
local ID = {stuc_kleur = 87378813833395, stuc_normaal = 93453765359013, lijst_kleur = 84200753761674,
	vlek1 = 139447230717275, vlek2 = 130335827998969, vlek3 = 89523083759406, vlek4 = 71188191265340,
	streep = 137986762588861, voet = 96092065348033, naald = 72168876031761,
	zellige = 112364982933611, zigzag = 94009043451472, balkon = 115587625989953, fries = 96873829333423,
	vloertegel = 112689883777106, schildering = 119976189330229, bord = 99448957611155,
	tegelhal = 73063474660484, deurblad = 79743845630448, balustrade = 99934946723999, parket = 120995854106325, bootplaket = 71844881657698, draaischijf = 126431821387104, s1_bord = 132430278150557}   -- naald: Pagode (dennennaalden)
-- rol -> {textuur, normaal, kleur, materiaal, botsen, reflectie, alfa}
local R = {
	stuc = {"stuc_kleur", "stuc_normaal", Color3.new(1, 1, 1), Enum.Material.Plaster, true},
	lijst = {"lijst_kleur", "stuc_normaal", Color3.new(1, 1, 1), Enum.Material.Plaster, true},
	raam = {nil, nil, Color3.fromRGB(26, 26, 32), Enum.Material.SmoothPlastic, true},
	deur = {nil, nil, Color3.fromRGB(78, 52, 34), Enum.Material.Wood, true},
	koepel = {nil, nil, Color3.fromRGB(40, 176, 186), Enum.Material.SmoothPlastic, true, 0.2},
	koepel_wit = {nil, nil, Color3.fromRGB(240, 238, 232), Enum.Material.SmoothPlastic, true, 0.1},
	koepel_grijs = {nil, nil, Color3.fromRGB(214, 214, 220), Enum.Material.SmoothPlastic, true, 0.12},
	goud = {nil, nil, Color3.fromRGB(222, 172, 82), Enum.Material.Metal, true},
	pannen = {nil, nil, Color3.fromRGB(34, 112, 84), Enum.Material.Slate, true},
	kade = {"lijst_kleur", "stuc_normaal", Color3.fromRGB(255, 252, 246), Enum.Material.Plaster, true},
	dak = {nil, nil, Color3.fromRGB(58, 58, 60), Enum.Material.Asphalt, true},
	lampmetaal = {nil, nil, Color3.fromRGB(86, 42, 32), Enum.Material.Metal, true},
	lampglas = {nil, nil, Color3.fromRGB(255, 236, 200), Enum.Material.Glass, false, nil, nil, 0.25},
	cipres = {"naald", nil, Color3.fromRGB(215, 240, 190), Enum.Material.Grass, false},
	hout = {nil, nil, Color3.fromRGB(86, 56, 34), Enum.Material.Wood, true},
	stucvlak = {"stuc_kleur", "stuc_normaal", Color3.new(1, 1, 1), Enum.Material.Plaster, true},
	tegel = {nil, nil, Color3.fromRGB(176, 104, 76), Enum.Material.Slate, true},
	-- minaret (04_minaret)
	zandsteen = {"lijst_kleur", "stuc_normaal", Color3.fromRGB(240, 222, 192), Enum.Material.Sandstone, true},
	wit = {"lijst_kleur", "stuc_normaal", Color3.fromRGB(255, 253, 248), Enum.Material.Plaster, true},
	rood = {nil, nil, Color3.fromRGB(186, 66, 42), Enum.Material.SmoothPlastic, true},
	-- ingangsgebouw (05_ingang)
	witvlak = {"lijst_kleur", "stuc_normaal", Color3.fromRGB(255, 253, 248), Enum.Material.Plaster, true},
	koepel_blauw = {nil, nil, Color3.fromRGB(104, 172, 214), Enum.Material.SmoothPlastic, true, 0.15},
	koepel_creme = {nil, nil, Color3.fromRGB(236, 220, 180), Enum.Material.SmoothPlastic, true, 0.1},
	donker = {nil, nil, Color3.fromRGB(30, 40, 56), Enum.Material.SmoothPlastic, true},
	zellige = {"zellige", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true, 0.06},
	zigzag = {"zigzag", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	balkon = {"balkon", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	fries = {"fries", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	-- ingangspoort minaret (04_minaret): donkere doorgang en witte neggen
	poort = {nil, nil, Color3.fromRGB(14, 14, 18), Enum.Material.SmoothPlastic, true},
	poortrand = {nil, nil, Color3.fromRGB(244, 240, 230), Enum.Material.Plaster, false},
	-- wachtrijhal (08_zuidvleugel)
	vloertegel = {"vloertegel", nil, Color3.new(1, 1, 1), Enum.Material.Slate, true},
	matglas = {nil, nil, Color3.fromRGB(236, 240, 242), Enum.Material.SmoothPlastic, true},
	schildering = {"schildering", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	hekgroen = {nil, nil, Color3.fromRGB(64, 92, 82), Enum.Material.Metal, true},
	bord = {"bord", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	bollamp = {nil, nil, Color3.fromRGB(176, 104, 48), Enum.Material.Neon, false},   -- warm geelbruin gloeiende bollampen in de wachtrijhal
	-- zijdeur + halletje minaret (04_minaret): gevelvlakken botsen niet, onzichtbare botsblokken wel
	zandvlak = {"lijst_kleur", "stuc_normaal", Color3.fromRGB(240, 222, 192), Enum.Material.Sandstone, false},
	tegelhal = {"tegelhal", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, false},
	deurblad = {"deurblad", nil, Color3.new(1, 1, 1), Enum.Material.Wood, false},
	botsing = {nil, nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true, nil, nil, 1},
	-- gang naar de instaphal (15_binnen) en groene kielbogen
	groen = {nil, nil, Color3.fromRGB(118, 172, 158), Enum.Material.SmoothPlastic, false},
	groenneg = {nil, nil, Color3.fromRGB(118, 172, 158), Enum.Material.SmoothPlastic, false},
	gangwand = {"stuc_kleur", "stuc_normaal", Color3.fromRGB(236, 218, 186), Enum.Material.Plaster, false},   -- oud beige pleister (gangkant boog)
	gangmuur = {"stuc_kleur", "stuc_normaal", Color3.fromRGB(236, 218, 186), Enum.Material.Plaster, true},    -- oud beige pleister (gangmuren, botsen)
	gangpleister = {"stuc_kleur", "stuc_normaal", Color3.fromRGB(236, 218, 186), Enum.Material.Plaster, false},   -- zwikken boven de gangboog
	-- instaphal (16_instaphal)
	water = {nil, nil, Color3.fromRGB(30, 56, 66), Enum.Material.Glass, false, 0.25, nil, 0.15},
	dekhout = {"draaischijf", nil, Color3.new(1, 1, 1), Enum.Material.WoodPlanks, true},   -- bovenblad draaischijf (1 textuur = hele schijf)
	dekrand = {nil, nil, Color3.fromRGB(40, 40, 46), Enum.Material.SmoothPlastic, true},   -- rand en onderkant draaischijf
	plafond = {nil, nil, Color3.fromRGB(52, 42, 36), Enum.Material.SmoothPlastic, false},
	rozet = {nil, nil, Color3.fromRGB(110, 70, 44), Enum.Material.SmoothPlastic, false},
	gordijn = {nil, nil, Color3.fromRGB(214, 196, 160), Enum.Material.Fabric, true},
	groenhek = {nil, nil, Color3.fromRGB(118, 172, 158), Enum.Material.Metal, true},
	balustrade = {"balustrade", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, false},
	balmuur = {"stuc_kleur", "stuc_normaal", Color3.fromRGB(236, 224, 202), Enum.Material.Plaster, true},
	onderwand = {nil, nil, Color3.fromRGB(92, 70, 52), Enum.Material.Wood, true},
	donkervloer = {nil, nil, Color3.fromRGB(78, 58, 44), Enum.Material.Slate, true},
	lichtlijst = {nil, nil, Color3.fromRGB(255, 196, 120), Enum.Material.Neon, false},
	witlijn = {nil, nil, Color3.fromRGB(240, 240, 232), Enum.Material.SmoothPlastic, false},
	lat = {nil, nil, Color3.fromRGB(158, 122, 86), Enum.Material.Wood, false},
	soffit = {nil, nil, Color3.fromRGB(46, 34, 28), Enum.Material.Wood, false},   -- donker plafond/band boven de gaanderij
	boogvul = {nil, nil, Color3.fromRGB(40, 30, 25), Enum.Material.SmoothPlastic, false},   -- donker boven de kielbogen van de gaanderij
	boogcreme = {"stuc_kleur", "stuc_normaal", Color3.fromRGB(236, 224, 202), Enum.Material.Plaster, false},   -- crème zwikken controlehok
	kegel = {"stuc_kleur", "stuc_normaal", Color3.fromRGB(240, 230, 210), Enum.Material.Plaster, true},   -- crème trompet onder het controlehok
	-- sloep (17_boten, sjabloon voor FataMorganaVaart)
	boot_rood = {nil, nil, Color3.fromRGB(150, 32, 28), Enum.Material.SmoothPlastic, true, 0.05},
	boot_wit = {nil, nil, Color3.fromRGB(242, 236, 224), Enum.Material.SmoothPlastic, true, 0.03},
	boot_vloer = {nil, nil, Color3.fromRGB(112, 22, 24), Enum.Material.Fabric, true},
	boot_bank = {nil, nil, Color3.fromRGB(242, 236, 224), Enum.Material.SmoothPlastic, true, 0.03},
	boot_plaket = {"bootplaket", nil, Color3.new(1, 1, 1), Enum.Material.Metal, false},
	boot_kop = {nil, nil, Color3.fromRGB(150, 32, 28), Enum.Material.SmoothPlastic, false, 0.1},
	boot_kopring = {nil, nil, Color3.fromRGB(242, 236, 224), Enum.Material.SmoothPlastic, false},
	-- vaarroute met kamers, nog kaal (18_route)
	routebodem = {nil, nil, Color3.fromRGB(22, 24, 26), Enum.Material.Slate, true},
	toneel = {nil, nil, Color3.fromRGB(82, 70, 58), Enum.Material.Concrete, true},
	routewand = {nil, nil, Color3.fromRGB(30, 27, 25), Enum.Material.Plaster, false},   -- donker (darkride), 19 nov
	routeplafond = {nil, nil, Color3.fromRGB(8, 8, 9), Enum.Material.Fabric, false},   -- mat zwart (glans van spots, 1d)
	plafondtrede = {nil, nil, Color3.fromRGB(8, 8, 9), Enum.Material.Fabric, false},   -- treden tussen plafondhoogtes; muren/plafond niet botsen (de botsvorm zou boven het maaiveld uitsteken)
	-- sectie 1a: gordijn naar de jungle (20_s1a_gordijn; FataMorganaS1Gordijn schuift de helften open)
	gordijn_l = {nil, nil, Color3.fromRGB(170, 156, 138), Enum.Material.Fabric, false},
	gordijn_r = {nil, nil, Color3.fromRGB(170, 156, 138), Enum.Material.Fabric, false},
	gordijnrail = {nil, nil, Color3.fromRGB(184, 170, 150), Enum.Material.Metal, false},
	s1_bord = {"s1_bord", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, false},
	-- sectie 1b: rotsgrot achter het gordijn (21_s1b_rotsboog)
	rots = {nil, nil, Color3.fromRGB(80, 79, 80), Enum.Material.Rock, false},
}
for _, r in {"vlek1", "vlek2", "vlek3", "vlek4", "streep", "voet"} do
	R[r] = {r, nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, false, nil, true}
end
local fm = workspace:FindFirstChild("FataMorgana") or Instance.new("Model")
fm.Name = "FataMorgana"; fm.Parent = workspace; fm.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
local onbekend, n = {}, 0
for naam, id in pairs(DELEN) do
	local oud = fm:FindFirstChild(naam); if oud then oud:Destroy() end
	local m = Instance.new("Model"); m.Name = naam
	for _, o in ipairs(game:GetObjects("rbxassetid://" .. id)) do o.Parent = m end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
	for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
	m.Parent = fm; m:ScaleTo(S)
	local anker
	for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
	m:PivotTo(CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot())
	anker:Destroy(); m.WorldPivot = CFrame.new()
	m:PivotTo(CFrame.new(VOET) * CFrame.Angles(0, math.pi, 0))
	for _, p in ipairs(m:GetChildren()) do
		local rol = string.match(p.Name, "^FM_(.-)_%d+_%a+$") or "?"
		local r = R[rol]
		p.Anchored = true; p.CanTouch = false; n += 1
		pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end)
		if not r then table.insert(onbekend, p.Name); continue end
		p.Color = r[3]; p.Material = r[4]; p.CanCollide = r[5]; p.CanQuery = r[5]
		if r[1] then
			local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. ID[r[1]]
			if r[2] then sa.NormalMap = "rbxassetid://" .. ID[r[2]] end
			if r[7] then sa.AlphaMode = Enum.AlphaMode.Transparency end
			sa.Color = r[3]; sa.Parent = p
		end
		if r[6] then p.Reflectance = r[6] end
		if r[7] then p.CastShadow = false end
		if r[8] then p.Transparency = r[8] end
		if p.CanCollide then pcall(function() p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end) end
	end
end
-- draaischijf los van de instaphal (FataMorganaDraaischijf.server.luau laat hem ronddraaien)
if fm:FindFirstChild("Instaphal") then
	local ds = fm:FindFirstChild("Draaischijf"); if ds then ds:Destroy() end
	ds = Instance.new("Model"); ds.Name = "Draaischijf"; ds.Parent = fm
	for _, p in fm.Instaphal:GetChildren() do
		if p.Name:find("^FM_dekhout") or p.Name:find("^FM_dekrand") or p.Name:find("^FM_witlijn") then p.Parent = ds end
	end
end
return "Fata Morgana: " .. n .. " delen" .. (#onbekend > 0 and (", onbekend: " .. table.concat(onbekend, ", ")) or "")
