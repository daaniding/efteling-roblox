-- plaats_instaphalwater: echt Terrain-water in het bassin van de instaphal (Daan 18 nov: "maak het ook echt water").
-- Binnenkant hal x -3,5..16,6, y -348,4..-323,6 (modelstelsel); waterspiegel op z -3,2 (Y = 0,91 + 3z = -8,69), onderkant Y -16.
-- De bovenste voxellaag (Y -12..-8) krijgt bezetting 0,83 zodat de spiegel op -8,69 ligt. Het terrein in de hal was eerder leeg.
local T = workspace.Terrain
local x0, x1 = 3 * -3.5, 3 * 16.6
local z0, z1 = 3 * 323.6, 3 * 348.4
local ytop = 0.91 + 3 * -3.2
local ybot = -16
T:FillBlock(CFrame.new((x0 + x1) / 2, (ybot + ytop) / 2, (z0 + z1) / 2), Vector3.new(x1 - x0, ytop - ybot, z1 - z0), Enum.Material.Water)
return "water gevuld"
