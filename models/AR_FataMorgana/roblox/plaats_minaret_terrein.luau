-- plaats_minaret_terrein: alleen grond direct onder de minaret (Daan 18 nov: "niet een heel plein maken, gewoon alles wat te maken
-- heeft met het uiterlijk van de fata morgana"); de rest van het vak (park x 2..40, y -346..-312) blijft leeg.
local S = 3
local t = workspace.Terrain
local x0 = math.floor(2 * S / 4) * 4; local x1 = math.ceil(40 * S / 4) * 4
local z0 = math.floor(312 * S / 4) * 4; local z1 = math.ceil(346 * S / 4) * 4
local nx, nz = (x1 - x0) / 4, (z1 - z0) / 4
local M, O = {}, {}
for ix = 1, nx do
	M[ix], O[ix] = {}, {}
	for iy = 1, 9 do M[ix][iy], O[ix][iy] = {}, {} end
	local px = (x0 + (ix - 0.5) * 4) / S
	for iz = 1, nz do
		local py = -(z0 + (iz - 0.5) * 4) / S
		local onder = math.abs(px - 19.5) < 3.6 and math.abs(py + 329) < 3.6
		for iy = 1, 9 do
			if onder and iy <= 7 then M[ix][iy][iz], O[ix][iy][iz] = Enum.Material.Ground, 1
			elseif onder and iy == 8 then M[ix][iy][iz], O[ix][iy][iz] = Enum.Material.Pavement, 0.725
			else M[ix][iy][iz], O[ix][iy][iz] = Enum.Material.Air, 0 end
		end
	end
end
t:WriteVoxels(Region3.new(Vector3.new(x0, -32, z0), Vector3.new(x1, 4, z1)), 4, M, O)
return "grond onder de minaret ok"
