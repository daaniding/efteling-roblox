-- Snoeien (hele map): planten die je vanaf de paden (OSM footway/path/pedestrian/service...) toch niet ziet weghalen. Bodem > 8 m, struiken > 17 m, bomen > 30 m van het pad.
local LIJNEN = require(game.ServerStorage.PadNetOSM)   -- padennet (Douglas-Peucker 4 studs) staat als ModuleScript in ServerStorage; bron: reference/data/efteling_osm.xml
local SEG = {}
for _, l in ipairs(LIJNEN) do for k = 1, #l - 3, 2 do table.insert(SEG, l[k]); table.insert(SEG, l[k + 1]); table.insert(SEG, l[k + 2]); table.insert(SEG, l[k + 3]) end end
local CEL = 60
local grid = {}
local function key(i, j) return i * 100000 + j end
for s = 1, #SEG, 4 do
	local ax, az, bx, bz = SEG[s], SEG[s + 1], SEG[s + 2], SEG[s + 3]
	local L = math.sqrt((bx - ax) ^ 2 + (bz - az) ^ 2); local n = math.max(1, math.ceil(L / (CEL / 2)))
	local done = {}
	for k = 0, n do local x, z = ax + (bx - ax) * k / n, az + (bz - az) * k / n
		local i, j = math.floor(x / CEL), math.floor(z / CEL); local kk = key(i, j)
		if not done[kk] then done[kk] = true; grid[kk] = grid[kk] or {}; table.insert(grid[kk], s) end end
end
local function afstand(x, z, maxd)
	local best = 1e9; local r = math.ceil(maxd / CEL); local ci, cj = math.floor(x / CEL), math.floor(z / CEL); local seen = {}
	for i = ci - r, ci + r do for j = cj - r, cj + r do local g = grid[key(i, j)]
		if g then for _, s in ipairs(g) do if not seen[s] then seen[s] = true
			local ax, az, bx, bz = SEG[s], SEG[s + 1], SEG[s + 2], SEG[s + 3]; local dx, dz = bx - ax, bz - az; local L2 = math.max(dx * dx + dz * dz, 1e-6)
			local t = math.clamp(((x - ax) * dx + (z - az) * dz) / L2, 0, 1); local d = math.sqrt((x - ax - t * dx) ^ 2 + (z - az - t * dz) ^ 2)
			if d < best then best = d end end end end end end
	return best
end
local function soort(nm)
	nm = string.lower(nm)
	for _, p in ipairs({"beuk", "eik", "den", "kastanje", "berk"}) do if string.sub(nm, 1, #p) == p then return 90 end end
	for _, p in ipairs({"rododendron", "taxus", "struik", "ph_shrub_02", "ph_shrub_03", "ph_shrub_04", "lavendel"}) do if string.sub(nm, 1, #p) == p then return 51 end end
	return 24
end
local prot = {}; local skip = {SprookjesboomPlanten = true, SprookjesboomStenen = true, MuzikalePaddenstoelen = true}
for _, c in ipairs(workspace:GetChildren()) do                                       -- alles binnen 15 m van een attractiemodel hoort bij de scene en blijft
	if c:IsA("Model") and not skip[c.Name] then local cf, sz = c:GetBoundingBox()
		table.insert(prot, {cf.Position.X - sz.X / 2 - 45, cf.Position.X + sz.X / 2 + 45, cf.Position.Z - sz.Z / 2 - 45, cf.Position.Z + sz.Z / 2 + 45}) end
end
local function scene(x, z) for _, b in ipairs(prot) do if x > b[1] and x < b[2] and z > b[3] and z < b[4] then return true end end return false end
local weg, over, per = 0, 0, {}
for _, f in ipairs(workspace:GetChildren()) do
	if f:IsA("Folder") and (string.find(f.Name, "Groen$") or f.Name == "MagischeKlokBos" or f.Name == "HerautenpleinBos" or f.Name == "VillaVoltaPlantenEcht" or f.Name == "VillaVoltaHorizon") then
		local w = 0
		for _, c in ipairs(f:GetChildren()) do local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
			if p then local m = soort(c.Name)
				if not scene(p.X, p.Z) and afstand(p.X, p.Z, m) > m then c:Destroy(); w += 1 else over += 1 end end
		end
		weg += w; if w > 0 then table.insert(per, f.Name .. " -" .. w) end
		task.wait()
	end
end
return string.format("weg %d, over %d\n%s", weg, over, table.concat(per, ", "))
