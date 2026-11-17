-- plaats_sirocco: Sirocco in Studio neerzetten (bron models/AR_Sirocco; ids in exports/asset_ids.txt). Plakken in de Studio-commandbalk.
-- Plek: dakmidden park (456,5; 191,2) m (luchtfoto) -> Roblox X = 3x, Z = -3y. Hoogte zoals de Pagode: gras NAP 9,8 (Y 1,4),
-- water 0,4 m lager (Y 0,2) = z 0 van het model; dek van de rit op Y 1,1.
-- Doet: terrein (vlak gras rond de vijver, vijver leeg in de vorm uit de luchtfoto), gebouw + rit + omgeving (FBX, ScaleTo 3, anker),
-- materialen per rol (SurfaceAppearance of kleur), lichtpunten in de lantaarns, waterplaat (vijvervorm) + onzichtbare bodem.
-- De lampen- en vijverlijst worden ingevuld door build/12_plak.py (uit exports/export_info.json en exports/omgeving_info.json).
local S = 3
local CX, CY = 456.5, 191.2
local Y_WATER = 0.2
local MIDDEN = Vector3.new(CX * S, Y_WATER, -CY * S)
local ID = {gebouw = 131869393173401, rit = 83505201461300, omgeving = 82705200382373, bord_kleur = 138476476235233,
	riet_kleur = 122992305053489, riet_normaal = 107154390027579, platform_kleur = 137087869566165, romp_kleur = 137095365073521,
	romp_hout_kleur = 92929270438539, schubben_kleur = 92127248105221, sierpaneel_kleur = 111038031156474, mand_kleur = 112674595994674,
	net_kleur = 123171354911724, beschot_kleur = 124186550110005, stam_kleur = 86277939897558, stam_normaal = 85501756974124,
	romp_blauw_kleur = 81733490640030, vlonder_kleur = 114168670349764, vlonder_normaal = 105858881415149, bamboe_kleur = 100311851570971}
local LAMPEN = {{-0.378, -2.162, 4.128}, {-2.531, -2.386, 5.705}, {-1.067, 5.067, 3.649}, {-4.839, 3.619, 3.350}, {5.678, -2.567, 3.350}, {17.080, 6.000, 2.300}, {16.676, 9.948, 2.300}, {14.330, 12.497, 2.300}, {10.894, 12.943, 2.300}, {7.976, 11.075, 2.300}, {6.951, 7.717, 2.300}, {8.257, 3.384, 2.300}, {8.881, 0.874, 2.300}, {8.759, -1.710, 2.300}, {7.900, -4.150, 2.300}, {6.378, -6.242, 2.300}, {7.865, -16.795, 4.590}, {8.330, -16.690, 4.280}, {8.826, -16.578, 4.976}}     -- export_info.json + omgeving_info.json, modelmeters (x oost, y noord, z boven water)
local VIJVER = {{10.500, 10.800}, {8.600, 11.100}, {7.000, 10.600}, {5.000, 11.250}, {1.750, 12.600}, {-2.000, 12.500}, {-5.500, 11.900}, {-6.200, 12.600}, {-7.200, 13.300}, {-8.900, 13.500}, {-10.600, 13.200}, {-11.600, 12.400}, {-11.800, 11.200}, {-11.200, 10.000}, {-10.600, 8.900}, {-11.000, 7.600}, {-11.800, 6.000}, {-12.800, 4.000}, {-13.300, 2.500}, {-14.600, 1.000}, {-14.900, 0.000}, {-14.600, -0.900}, {-14.000, -1.800}, {-13.200, -3.200}, {-12.600, -4.800}, {-12.000, -6.000}, {-11.200, -7.600}, {-11.600, -8.800}, {-12.600, -10.000}, {-13.800, -11.600}, {-14.600, -12.300}, {-13.000, -13.400}, {-11.000, -14.800}, {-9.800, -15.200}, {-9.600, -13.600}, {-8.800, -12.000}, {-7.500, -11.000}, {-3.500, -11.000}, {-3.400, -13.300}, {7.500, -13.300}, {10.000, -11.500}, {12.250, -9.250}, {14.000, -6.250}, {14.800, -2.500}, {14.800, 1.250}, {14.300, 3.800}, {12.600, 4.000}, {11.600, 6.000}, {11.300, 9.300}}     -- vijverrand (luchtfoto), modelmeters
local KLASSEN = {"gvvvvvvvvvvvvvvvvvvgggggzzzvvvzzzzzzzvvggggggvvvvvvvvvvvvvvvvvgggggggg", "vvvvvvvvvvvvvvvvvvvggggggvvvvzzzzzzvvggggggggvvvvvvvvvvvvvvvvvvvvggvgg", "vvvvvvvvvvvvvvvvvvvvvvvggggvvzzzzzvvgggggggggvvvvvvvvvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvggggzzzzzvggggggggggvvvvvvvvvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvggggvzvvvvggggggggggvvvvvvvvvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvgggggvgggggggggggggvvvvvvvvvvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvgggggggggggvggggggvvvvvvvvvvvvvvggggvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvgvvvvvvgggvvvvvvvvvvvvvvvggggggggvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvgggggggg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzzzzzzvvvgvvvggg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvgggvvvzzzzzzzzzzzvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvggggvvvzzzzzvvvvzzzvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzzzvvgggvvvzzzzzvvvvvvzzvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzzzzvvgvvzzzzzzvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzzzzvvzzzzzzzzzzvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzzzzvvzzzzzzzzzzvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzzzvvvzzzzzzzzggvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzvvvvvgvzzzvvgggvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvaaaaavvvvvvvvvvvvvvvvvvvggzvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvaaaaaagggggggggggvvvvvvvvvvvvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvaaaaaagggggggggggggvvvvvvvvvvvvvvvvvvvvvvvvgg", "gggggggvvvvvvvvvvvvvvvvggaaaaaaggggggggggggggvvvvvvvvvvvvvvvvvvvvvvvgg", "gggggggvvvvvvvvvvvvvvvgvggaaaaaggggggggggggggggvvvvvvvvvvvvvvvvvvvvvgg", "gggggggvvvvvvvvvvvvzzvvvgggaaaagggggggggggggggggvvvvvvvggvvvvvvvvvvvgg", "vvggggggvvvvvvvvvvzzzzvvggggggggggggggggggggggggvvvvvgggggvvvvvvvvvvgg", "vvvgggggvvvvvvvvvvzzzzzvgggggggggggggggggggggggggggggggggggvvvvvvvvvgg", "vvvgggvvvvvvvvvvvvzzzzzvgggggggggggggggggggggggggggggggggggvvvvvvvvvgg", "vvvgggvvvvvvvvvvvvzzzzzzggggggggggggggggggggggggggggggggggvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvzzzzzvggggggggggggggggggggggggggggggggggvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvzzzzvgggggggggggggggggggggggggggggggvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvgggggggggggggggggggggggggggggggvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvgggggggggggggggggggggggggggggvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvggggggggggggggggggggggggggggvvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvggggggggggggggggggggggggggggvvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvggggggggggggggggggggggggggggvvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvggggggggggggggggggggggggggggvvvvvvvvvvvvvggvgg", "vvvvvvvvvvvvvvvvvvvvvvvvggggggggggggggggggggggggggggvvvvvvvvvvvggggvgg", "vvvvvvvvvvvvvvvvvvvvvvvvggggggggggggggggggggggggggggvvvvvvvvvvvgggvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvggggggggggggggggggggggggggggvvvgggvvvvvvggvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvgggggggggggggggggggggggggggvvvvgggvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvgvvvvvgggggggggggggggggggggggggggggvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvggvvvvvggggggggggggggggggggggggggggggvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvvggggggggggggggggggggggggggggggggggvggggvvvvvvvggvvvvgg", "vvvvvvvvvvvvvvvvggggggggggggggggggggggggggggggggggvggggvvvvvvvgggvvvgg", "vvvvvvvvvvvvvvvggggggggggggggggggggggggggggggggggvvggvvvvvvvvvggvvvvgg", "vvvvvvvvvvvvvvvgggggggggggggggggggggggggggggggggvvgggvvvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvgggggggggggggggggggggggggggggggggvggggggvvvvvvvvvvvvvgg", "vvvvvvvvvvvvvvvggggggggggggggggggggggggggggggggggggggggggvvvvzzvvggggg", "vvvvvvvvvvvvvvvgggggggggggggggggggggggggggggggggggggggggggggggvggggggg", "vvvvvvvvvvvvvvvggggggggggvgggggggggggggggggggggggggggggggggggggggggggg", "vvvvvvvvvvvvvvvvggggggggggggggggggggggggggvvvvvvvggggggggggggggggggggg", "vvvvvvvvvvvvvvvvvgggggggggggggggggggggggvvvvvvvvvvvvvvgggggggggggggggg", "vvvvvvvvvvvvvvvvvgggggggggggggggggggggvvvvvvvvvvvvvvvvvggggggggggggggg", "vvvvvvvvvvvvvvvvvvgggggggggggggggggvvvvvvvvvvvvvvvvvvvvvvgvggggggggggg", "vvvvvvvvvvvvvvvvvvvggggggggggvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvgggggggggg", "vvvvvvvvvvvvvvvvvvvvvvggggggggvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvggggg", "vvvvvvvvvvvvvvvvvvvvvvvvggggggvvvvvvvvvvvvvvvvvvggggvvvvvvvvvvvvvggggg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvggggggvvvvvvvvvvgggggg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvggggggggvvvvvvvgggggg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvgggvvgggvvvvvvvvgggg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzzzzvgvvgggggvvvvvvvggg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzzvvvggggggggvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzzzvvvggggggggvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzzzzzvvggggggggvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzvvvvvvvzzzvvvvvvgggggggggvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzvvvvvvvzzvvvvvvvgggggggggvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzvvvvvvvvvvvvvvggggggggggvvvvvvvvvgg", "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvzzvvvvvvvvvvvvvvggggggggggvvvvvvvvvgg", "gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg", "gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"}   -- per m (rij = model-y -35..34, teken = model-x -35..34): v verhard plein, g plantvak, z zand, a aarde (luchtfoto)
local MAT = {v = Enum.Material.Pavement, g = Enum.Material.Grass, z = Enum.Material.Sand, a = Enum.Material.Ground}

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
	-- omgeving (07_omgeving)
	zeil_turkoois = {nil, nil, Color3.fromRGB(38, 150, 140), Enum.Material.Fabric, false},   -- turquoise zeilkap (Sirocco-meandering.jpg)
	zeilrand = {nil, nil, Color3.fromRGB(26, 112, 108), Enum.Material.Fabric, false},
	bamboewand = {nil, nil, Color3.fromRGB(190, 160, 105), Enum.Material.Wood, true},
	raam = {nil, nil, Color3.fromRGB(22, 18, 16), Enum.Material.SmoothPlastic, false},
	bestrating = {nil, nil, Color3.fromRGB(150, 140, 128), Enum.Material.Cobblestone, true},
	muur = {nil, nil, Color3.fromRGB(140, 128, 112), Enum.Material.Slate, true},
	afdek = {nil, nil, Color3.fromRGB(172, 162, 146), Enum.Material.Concrete, true},
	steen = {nil, nil, Color3.fromRGB(122, 116, 106), Enum.Material.Rock, true},
	boei_geel = {nil, nil, Color3.fromRGB(240, 200, 40), Enum.Material.SmoothPlastic, false},
	boei_blauw = {nil, nil, Color3.fromRGB(40, 80, 170), Enum.Material.SmoothPlastic, false},
	bord = {nil, nil, Color3.fromRGB(110, 78, 48), Enum.Material.Wood, true},
	dhow = {nil, nil, Color3.fromRGB(112, 80, 50), Enum.Material.Wood, false},
	zeil_dhow = {nil, nil, Color3.fromRGB(236, 220, 170), Enum.Material.Fabric, false},
	water = {nil, nil, Color3.fromRGB(32, 52, 44), Enum.Material.SmoothPlastic, false, "water"},
	-- ingangsbord (07_omgeving.ingangsbord, atlas 07t_bord.py)
	paalmetaal = {nil, nil, Color3.fromRGB(86, 54, 44), Enum.Material.Metal, true},
	lamp_groen = {nil, nil, Color3.fromRGB(52, 112, 98), Enum.Material.Metal, false},
	lamp_rood = {nil, nil, Color3.fromRGB(150, 44, 38), Enum.Material.Metal, false},
	bordrand = {nil, nil, Color3.fromRGB(160, 120, 62), Enum.Material.Wood, false},
	bordvlak = {"bord_kleur", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, false},
	-- Sindbads boot (07_omgeving.dhow_sindbad); romp/schubben/sierpaneel gebruiken de rittexturen, eigen UV's
	dhowdek = {nil, nil, Color3.fromRGB(130, 92, 58), Enum.Material.WoodPlanks, false},
	baal = {nil, nil, Color3.fromRGB(226, 212, 178), Enum.Material.Fabric, false},
	kruik = {nil, nil, Color3.fromRGB(168, 96, 58), Enum.Material.SmoothPlastic, false},
	-- zandstrand west van de haven (07_omgeving.strand)
	zand = {nil, nil, Color3.fromRGB(218, 198, 158), Enum.Material.Sand, true},
	kei = {nil, nil, Color3.fromRGB(168, 146, 136), Enum.Material.Slate, true},
	-- witte plantvakrand en zandstenen havenmuur (07_omgeving.vijverrand / havenmuur)
	witrand = {nil, nil, Color3.fromRGB(228, 226, 218), Enum.Material.Concrete, true},
	zandsteen = {nil, nil, Color3.fromRGB(212, 186, 146), Enum.Material.Sandstone, true},
	afdek_zand = {nil, nil, Color3.fromRGB(226, 208, 172), Enum.Material.Sandstone, true},
	muursteen = {nil, nil, Color3.fromRGB(150, 132, 112), Enum.Material.Slate, false},
	boog = {nil, nil, Color3.fromRGB(18, 16, 14), Enum.Material.SmoothPlastic, false},
	zandsteenvlak = {nil, nil, Color3.fromRGB(212, 186, 146), Enum.Material.Sandstone, true},
	blauwglas = {nil, nil, Color3.fromRGB(90, 200, 225), Enum.Material.Neon, false},
	-- bedieningshuisje (07_omgeving.hutje)
	raamglas = {nil, nil, Color3.fromRGB(170, 205, 215), Enum.Material.Glass, false, "ruit"},
	deur = {nil, nil, Color3.fromRGB(92, 62, 40), Enum.Material.WoodPlanks, true},
	beschot_om = {nil, nil, Color3.fromRGB(52, 48, 44), Enum.Material.Wood, false},
}

local function inVijver(x, y)          -- punt-in-veelhoek (even-oneven)
	local binnen, j = false, #VIJVER
	for i = 1, #VIJVER do
		local a, b = VIJVER[i], VIJVER[j]
		if (a[2] > y) ~= (b[2] > y) and x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1] then binnen = not binnen end
		j = i
	end
	return binnen
end

-- 1 terrein: vlak in een vierkant van 70 m; per vierkante meter plein (Pavement), plantvak (gras) of zand zoals op de luchtfoto;
-- de vijver (vorm uit de luchtfoto) leeg tot ver onder het water
local t = workspace.Terrain
-- Daan 17 nov: "gewoon de ondergrond plat, niet dit rare relief". Terrein op het voxelraster (4 studs) met volle voxels, dus
-- vlak. Gemeten: bovenkant = 4 * (bezetting bovenste laag - 0,5); bezetting 0,725 -> grond Y 0,9-1,0, net onder de wachtrijvlonder
-- (1,1) en de brug (1,16), boven het water (0,35). Vijverkolommen: bovenste laag leeg (bodem Y -2).
t:FillBlock(CFrame.new(MIDDEN.X, 40, MIDDEN.Z), Vector3.new(70 * S + 8, 80, 70 * S + 8), Enum.Material.Air)
local x0 = math.floor((MIDDEN.X - 35 * S) / 4) * 4; local z0 = math.floor((MIDDEN.Z - 35 * S) / 4) * 4
local nx = math.ceil((MIDDEN.X + 35 * S - x0) / 4); local nz = math.ceil((MIDDEN.Z + 35 * S - z0) / 4)
local NY = 8                                     -- lagen van Y -32 tot 0
local mat, occ = {}, {}
for ix = 1, nx do
	mat[ix], occ[ix] = {}, {}
	local cx = x0 + (ix - 0.5) * 4
	for iy = 1, NY do mat[ix][iy], occ[ix][iy] = {}, {} end
	for iz = 1, nz do
		local cz = z0 + (iz - 0.5) * 4
		local x, y = (cx - MIDDEN.X) / S, -(cz - MIDDEN.Z) / S
		local water = inVijver(x, y)
		local rij = KLASSEN[math.clamp(math.floor(y) + 36, 1, 70)]
		local k = string.sub(rij, math.clamp(math.floor(x) + 36, 1, 70), math.clamp(math.floor(x) + 36, 1, 70))
		for iy = 1, NY do
			local vol = not (water and iy == NY)
			mat[ix][iy][iz] = vol and (iy == NY and (MAT[k] or Enum.Material.Grass) or Enum.Material.Ground) or Enum.Material.Air
			occ[ix][iy][iz] = vol and (iy == NY and 0.725 or 1) or 0
		end
	end
end
t:WriteVoxels(Region3.new(Vector3.new(x0, -32, z0), Vector3.new(x0 + nx * 4, 0, z0 + nz * 4)), 4, mat, occ)

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
for naam, id in pairs({Gebouw = ID.gebouw, Rit = ID.rit, Omgeving = ID.omgeving}) do
	local m = laad(id, naam)
	for _, p in ipairs(m:GetChildren()) do
		local rol = string.match(p.Name, "^SI_(.-)_%d+_%a+$") or "?"
		local r = R[rol]
		p.Anchored = true; p.CanTouch = false
		pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end)   -- anders vallen kleine delen (schubben, golf, fruit) op afstand weg
		if not r then table.insert(onbekend, p.Name); continue end
		p.Color = r[3]; p.Material = r[4]; p.CanCollide = r[5]; p.CanQuery = r[5]
		p.CastShadow = rol ~= "net" and rol ~= "lantaarnglas" and rol ~= "blauwglas" and rol ~= "raamglas"
		if r[1] then
			local sa = Instance.new("SurfaceAppearance")
			sa.ColorMap = "rbxassetid://" .. ID[r[1]]
			if r[2] then sa.NormalMap = "rbxassetid://" .. ID[r[2]] end
			if r[6] == "alfa" then sa.AlphaMode = Enum.AlphaMode.Transparency end
			sa.Color = r[3]
			sa.Parent = p
		end
		if r[6] == "glas" then p.Transparency = 0.15 end
		if r[6] == "ruit" then p.Transparency = 0.45; p.Reflectance = 0.15 end
		if r[6] == "water" then p.Transparency = 0.12; p.Reflectance = 0.05; p.CastShadow = false; p.Position += Vector3.new(0, 0.27, 0) end   -- Y 0,35: vrij boven het vlakke terrein
		if naam == "Omgeving" and rol == "net" then p.CanCollide = true; p.CanQuery = true end
		if naam == "Omgeving" and rol == "vlonder" then p.Color = Color3.fromRGB(205, 190, 168); p:FindFirstChildOfClass("SurfaceAppearance").Color = p.Color end   -- wachtrijvlonder lichter   -- wachtrijhek: niet doorheen lopen
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

-- 4 water: de waterplaat zit in de omgeving (vijvervorm, donker en troebel; Glass spiegelt de lucht, WERKWIJZE); hier alleen een
-- onzichtbare bodem onder de hele vijver zodat je niet wegvalt
local b = Instance.new("Part"); b.Name = "Vijverbodem"; b.Anchored = true; b.Transparency = 1; b.CanCollide = true; b.CanQuery = false
b.Size = Vector3.new(32 * S, 1, 32 * S); b.CFrame = CFrame.new(MIDDEN - Vector3.new(0, 4.7, 0)); b.Parent = sir

local n = 0
for _, d in ipairs(sir:GetDescendants()) do if d:IsA("BasePart") then n += 1 end end
return "Sirocco geplaatst: " .. n .. " delen" .. (#onbekend > 0 and (", onbekende rol: " .. table.concat(onbekend, ", ")) or "")
