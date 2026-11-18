-- plaats_toren: Fata Morgana stap 1, de grote toren aan het meer (bron models/AR_FataMorgana; ids in exports/asset_ids.txt).
-- Plek: voet park (-40; -295) (AHN-top) -> X = 3x, Z = -3y; maaiveld Y 0,91 (parkhoogte), terreinwater Y ~0,35 voor de toren.
-- Doet: terrein (vlak maaiveld 36 x 30 m, ten noorden van y -292,6 water zoals de inham op Fata2013.jpg), toren (FBX, ScaleTo 3,
-- anker), materialen per rol.
local S = 3
local VOET = Vector3.new(-40 * S, 0.91, 295 * S)
local ID = {toren = 100954996943491, stuc_kleur = 101580183795505, stuc_normaal = 93453765359013, lijst_kleur = 126497920557085}
local R = {
	stuc = {"stuc_kleur", "stuc_normaal", Color3.new(1, 1, 1), Enum.Material.Plaster, true},
	lijst = {"lijst_kleur", "stuc_normaal", Color3.new(1, 1, 1), Enum.Material.Plaster, true},
	raam = {nil, nil, Color3.fromRGB(26, 26, 32), Enum.Material.SmoothPlastic, true},
	deur = {nil, nil, Color3.fromRGB(78, 52, 34), Enum.Material.Wood, true},
	koepel = {nil, nil, Color3.fromRGB(40, 176, 186), Enum.Material.SmoothPlastic, true, "glans"},
	goud = {nil, nil, Color3.fromRGB(214, 168, 72), Enum.Material.Metal, false},
}
-- 1 terrein
local t = workspace.Terrain
local x0 = math.floor(-58 * S / 4) * 4; local x1 = math.ceil(-22 * S / 4) * 4
local z0 = math.floor(280 * S / 4) * 4; local z1 = math.ceil(310 * S / 4) * 4
local nx, nz = (x1 - x0) / 4, (z1 - z0) / 4
local M, O = {}, {}
for ix = 1, nx do
	M[ix], O[ix] = {}, {}
	for iy = 1, 9 do M[ix][iy], O[ix][iy] = {}, {} end
	for iz = 1, nz do
		local py = -(z0 + (iz - 0.5) * 4) / S
		local water = py > -292.6
		for iy = 1, 9 do                                    -- lagen Y -32 .. 4
			local m, o = Enum.Material.Ground, 1
			if water then
				if iy == 9 then m, o = Enum.Material.Water, 0.1
				elseif iy == 8 then m, o = Enum.Material.Water, 1
				elseif iy == 7 then m, o = Enum.Material.Mud, 1 end
			else
				if iy == 8 then m, o = Enum.Material.Pavement, 0.725
				elseif iy == 9 then m, o = Enum.Material.Air, 0 end
			end
			M[ix][iy][iz], O[ix][iy][iz] = m, o
		end
	end
end
t:WriteVoxels(Region3.new(Vector3.new(x0, -32, z0), Vector3.new(x1, 4, z1)), 4, M, O)
-- 2 toren
local fm = workspace:FindFirstChild("FataMorgana") or Instance.new("Model")
fm.Name = "FataMorgana"; fm.Parent = workspace; fm.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
local oud = fm:FindFirstChild("Toren"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Toren"
for _, o in ipairs(game:GetObjects("rbxassetid://" .. ID.toren)) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m.Parent = fm; m:ScaleTo(S)
local anker
for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
m:PivotTo(CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot())
anker:Destroy(); m.WorldPivot = CFrame.new()
m:PivotTo(CFrame.new(VOET) * CFrame.Angles(0, math.pi, 0))
local onbekend = {}
for _, p in ipairs(m:GetChildren()) do
	local rol = string.match(p.Name, "^FM_(.-)_%d+_%a+$") or "?"
	local r = R[rol]
	p.Anchored = true; p.CanTouch = false
	pcall(function() p.RenderFidelity = Enum.RenderFidelity.Precise end)
	if not r then table.insert(onbekend, p.Name); continue end
	p.Color = r[3]; p.Material = r[4]; p.CanCollide = r[5]; p.CanQuery = r[5]
	if r[1] then
		local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://" .. ID[r[1]]
		if r[2] then sa.NormalMap = "rbxassetid://" .. ID[r[2]] end
		sa.Color = r[3]; sa.Parent = p
	end
	if r[6] == "glans" then p.Reflectance = 0.2 end
	if p.CanCollide then pcall(function() p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end) end
end
return "toren geplaatst: " .. #m:GetChildren() .. " delen" .. (#onbekend > 0 and (", onbekend: " .. table.concat(onbekend, ", ")) or "")
