-- plaats_modellen: alle Fata Morgana-modellen (toren, noordgevel, ...) opnieuw laden met één materiaaltabel. Terrein staat in
-- plaats_toren.luau / plaats_noordgevel.luau (alleen nodig bij een lege plek). Ids: exports/asset_ids.txt.
-- Oorsprong van alle delen: park (-40; -295) op het maaiveld Y 0,91. Verwering = losse overlays (vlek1..4, streep, voet) met alfa.
local S = 3
local VOET = Vector3.new(-40 * S, 0.91, 295 * S)
local DELEN = {Toren = 78216314839709, Noordgevel = 94005171015350, Minaret = 101506104399502}
local ID = {stuc_kleur = 87378813833395, stuc_normaal = 93453765359013, lijst_kleur = 84200753761674,
	vlek1 = 139447230717275, vlek2 = 130335827998969, vlek3 = 89523083759406, vlek4 = 71188191265340,
	streep = 137986762588861, voet = 96092065348033, naald = 72168876031761,
	zellige = 112364982933611, zigzag = 94009043451472, balkon = 115587625989953}   -- naald: Pagode (dennennaalden)
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
	rood = {nil, nil, Color3.fromRGB(168, 46, 36), Enum.Material.SmoothPlastic, true},
	donker = {nil, nil, Color3.fromRGB(30, 40, 56), Enum.Material.SmoothPlastic, true},
	zellige = {"zellige", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true, 0.06},
	zigzag = {"zigzag", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
	balkon = {"balkon", nil, Color3.new(1, 1, 1), Enum.Material.SmoothPlastic, true},
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
return "Fata Morgana: " .. n .. " delen" .. (#onbekend > 0 and (", onbekend: " .. table.concat(onbekend, ", ")) or "")
