-- Sprookjesbos-paden (models/PR_Paden): BGT-padvlakken op het AHN-veld, gebakken in Blender (04_blender.py). Vervangt workspace.SprookjesbosPaden.
-- Terrein eronder (0,5 stud omlaag + Ground) doet ServerStorage.AHN_Delta.PadenTerrein, eenmalig (attribuut PadenTerreinBanden).
local MODEL = 84917456870593
local IDS = {
 klinker={92043763234790,94005482950689,115939889177642},
 grijs={135645898189680,105581428619780,80924239132213},
 keitjes={112953952434700,93626348792730,105883840162032},
 platen={129218182294488,139257616200558,121128759487580},
 kassei={127574960591258,77871033037157,120119392898514},
 asfalt={85404863396414,125247639465688,117362102891321},
 kantsteen={79255050163796,89521820345427,117750992401457},
 rand={116026820112420,138155942636706,91900900245966},
 waaier={87300606792458,86312279132384,91757189376028},
 roze={116686057231173,127698793851907,83976370345614},
 plavuis={118160700412498,83533569345776,77470067210237}}
local objs = game:GetObjects("rbxassetid://" .. MODEL)
local oud = workspace:FindFirstChild("SprookjesbosPaden"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "SprookjesbosPaden"
for _, o in ipairs(objs) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = workspace; m:ScaleTo(3)
local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
m:PivotTo(CFrame.new(anker.Position + Vector3.new(0, 6, 0)):Inverse() * m:GetPivot()); anker:Destroy()
local n = 0
for _, p in ipairs(m:GetChildren()) do
	local mat = p.Name:match("^PD_(%a+)_"); local ids = IDS[mat]
	if p:IsA("MeshPart") and ids then
		p.Anchored = true; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic; p.Color = Color3.new(1, 1, 1)
		local sa = Instance.new("SurfaceAppearance")
		sa.ColorMap = "rbxassetid://" .. ids[1]; sa.NormalMap = "rbxassetid://" .. ids[2]; sa.RoughnessMap = "rbxassetid://" .. ids[3]
		if mat == "rand" then sa.AlphaMode = Enum.AlphaMode.Transparency; p.CanCollide = false; p.CanQuery = false
		else p.CanCollide = true; p.CanQuery = true; p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end
		sa.Parent = p; p:SetAttribute("Padmateriaal", mat); n += 1
		if n % 30 == 0 then task.wait() end
	end
end
-- Herautenplein: de zones (waaier/roze/plavuis) vervangen de oude v1-bestrating; die gaat naar ServerStorage (terug te zetten)
local bak = game.ServerStorage:FindFirstChild("V1PadVervangen") or Instance.new("Folder", game.ServerStorage); bak.Name = "V1PadVervangen"
local hp = workspace:FindFirstChild("Herautenplein")
if hp then
	for _, p in ipairs(hp:GetDescendants()) do
		if p:IsA("MeshPart") and (p.Name:find("MAT_plavuis") or p.Name:find("MAT_kassei") or p.Name:find("MAT_bodem")) then p:SetAttribute("Herkomst", p:GetFullName()); p.Parent = bak end
	end
end
-- Paden die bij de v1-assets hoorden: ze liggen (grotendeels) op de nieuwe paden en staken erdoorheen -> ServerStorage (terug te zetten via attribuut Herkomst).
-- Gekozen op materiaal (pad) en overlap >= 25% met de nieuwe paden; vijverbodems, water, siergrind en delen naast de paden blijven staan.
local ASSETPADEN = {
	"SneeuwwitjeOmgeving.static__MAT_aarde_0", "SneeuwwitjeOmgeving.static__MAT_klinker_0", "SneeuwwitjeOmgeving.static__MAT_band_0",
	"Assepoester.static__MAT_vloer_0", "AssepoesterOmgeving.static__MAT_band_0", "AssepoesterOmgeving.static__MAT_klinker_0",
	"Ezeltje.static__MAT_ijssel_0", "HansEnGrietjeOmgeving.static__MAT_aarde_0", "HansEnGrietjeOmgeving.static__MAT_snoeppad_0",
	"KlerenKeizerOmgeving.static__MAT_klinker_0", "KlerenKeizerOmgeving.static__MAT_tegels_0", "Langnek.static__MAT_klinker_0",
	"Pinokkio.static__MAT_flagstone_0", "PrinsesOpDeErwtPlein.static__MAT_aarde_0", "PrinsesOpDeErwtPlein.static__MAT_grind_0",
	"PrinsesOpDeErwtPlein.static__MAT_tegelwit_0", "PrinsesOpDeErwtPlein.static__MAT_tegelzwart_0", "RepelsteeltjeHuisje.static__MAT_flagstone_0",
	"RodeSchoentjes.static__MAT_grind_0", "Sneeuwwitje.static__MAT_pad_0", "SprekendePapegaai.static__MAT_grind_0", "SprookjesboomOmgeving.band_0",
	"VliegendeFakir.static__MAT_grind_0", "VrouwHolle.static__MAT_grind_0", "ZesZwanenOmgeving.static__MAT_klinker_0",
	"ZevenGeitjes.static__MAT_grind_0", "ZwavelstokjesStadje.static__MAT_klinker_0",
	"TrollenkoningPlein.static__MAT_grind_0"}  -- grindpleintje: vervangen door het platenplein (extra_vlakken)
for _, pad in ipairs(ASSETPADEN) do
	local mdl, nm = pad:match("^(.-)%.(.+)$")
	local p = workspace:FindFirstChild(mdl) and workspace[mdl]:FindFirstChild(nm, true)
	if p then p:SetAttribute("Herkomst", p:GetFullName()); p.Parent = bak end
end
return n .. " paddelen geplaatst"
