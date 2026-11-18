-- plaats_minaret_terrein: plein onder en rond de minaret (park x 2..40, y -346..-312), bestrating op parkhoogte Y 0,91.
local S = 3
local t = workspace.Terrain
local x0 = math.floor(2 * S / 4) * 4; local x1 = math.ceil(40 * S / 4) * 4
local z0 = math.floor(312 * S / 4) * 4; local z1 = math.ceil(346 * S / 4) * 4
local nx, nz = (x1 - x0) / 4, (z1 - z0) / 4
local M, O = {}, {}
for ix = 1, nx do
	M[ix], O[ix] = {}, {}
	for iy = 1, 9 do
		M[ix][iy], O[ix][iy] = {}, {}
		for iz = 1, nz do
			if iy <= 7 then M[ix][iy][iz], O[ix][iy][iz] = Enum.Material.Ground, 1
			elseif iy == 8 then M[ix][iy][iz], O[ix][iy][iz] = Enum.Material.Pavement, 0.725
			else M[ix][iy][iz], O[ix][iy][iz] = Enum.Material.Air, 0 end
		end
	end
end
t:WriteVoxels(Region3.new(Vector3.new(x0, -32, z0), Vector3.new(x1, 4, z1)), 4, M, O)
return "plein minaret ok"
