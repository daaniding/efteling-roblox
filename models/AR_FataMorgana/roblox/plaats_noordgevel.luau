-- plaats_noordgevel: Fata Morgana stap 2, de gevel aan het meer links en rechts van de toren (ids in exports/asset_ids.txt).
-- Zelfde oorsprong als de toren: park (-40; -295) op het maaiveld (Y 0,91). Terrein: bestrating achter de waterlijn (AHN: kade
-- tot y -286,5 voor de oostvleugel, -292,6 elders), meerwater ervoor (Y ~0,35), x -76 .. -4.
local S = 3
local VOET = Vector3.new(-40 * S, 0.91, 295 * S)
local ID = {gevel = 94151690417229, stuc_kleur = 101580183795505, stuc_normaal = 93453765359013, lijst_kleur = 126497920557085}
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
}
-- 1 terrein
local t = workspace.Terrain
local x0 = math.floor(-76 * S / 4) * 4; local x1 = math.ceil(-4 * S / 4) * 4
local z0 = math.floor(276 * S / 4) * 4; local z1 = math.ceil(310 * S / 4) * 4
local nx, nz = (x1 - x0) / 4, (z1 - z0) / 4
local M, O = {}, {}
for ix = 1, nx do
	M[ix], O[ix] = {}, {}
	for iy = 1, 9 do M[ix][iy], O[ix][iy] = {}, {} end
	local px = (x0 + (ix - 0.5) * 4) / S
	for iz = 1, nz do
		local py = -(z0 + (iz - 0.5) * 4) / S
		local water = (px > -38 and py > -286.5) or (px <= -38 and py > -292.6)
		for iy = 1, 9 do
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
-- 2 gevel
local fm = workspace:FindFirstChild("FataMorgana") or Instance.new("Model")
fm.Name = "FataMorgana"; fm.Parent = workspace; fm.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
local oud = fm:FindFirstChild("Noordgevel"); if oud then oud:Destroy() end
local m = Instance.new("Model"); m.Name = "Noordgevel"
for _, o in ipairs(game:GetObjects("rbxassetid://" .. ID.gevel)) do o.Parent = m end
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
	if r[6] then p.Reflectance = r[6] end
	if p.CanCollide then pcall(function() p.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition end) end
end
return "noordgevel geplaatst: " .. #m:GetChildren() .. " delen" .. (#onbekend > 0 and (", onbekend: " .. table.concat(onbekend, ", ")) or "")
