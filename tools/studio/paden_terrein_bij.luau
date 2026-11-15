-- PadenTerreinBij (ServerStorage.AHN_Delta.PadenTerreinBij): terrein en paden laten aansluiten, met een vaste marge.
-- Glad terrein van Roblox bolt boven een opgevuld blok iets uit en middelt met de kolommen ernaast; daarom twee grenzen
-- met speling ertussen, zodat uitsnijden en opvullen elkaar niet tegenwerken:
--   uitsnijden: grond hoger dan het pad (+0,02)          -> weg tot 1,0 stud onder het pad (FillBlock Air)
--   opvullen:   grond meer dan 2,0 stud onder het pad    -> aanvullen tot 1,2 stud onder het pad (FillBlock Ground)
--   stoeprand:  grond meer dan 1,6 stud onder de rand    -> aanvullen tot 1,2 stud onder de rand
-- De rokken onder de stoeprand gaan 1,8 stud omlaag (02_mesh.py SKIRT), dus die marge is nergens als kier te zien.
-- Gebruik (Studio, Edit): local f = require(game.ServerStorage.AHN_Delta.PadenTerreinBij); print(f.ronde(-760, 250)); print(f.meet())
local t = workspace.Terrain
local M = {}
local AF, OP, KANT = 1.0, 1.2, 1.2

local function params()
	local m = workspace.SprookjesbosPaden
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {m}
	local rt = RaycastParams.new(); rt.FilterType = Enum.RaycastFilterType.Include; rt.FilterDescendantsInstances = {t}
	return rp, rt
end

function M.ronde(z0, z1)
	local rp, rt = params(); local weg, bij = 0, 0
	for z = z0, z1, 2 do
		for x = -200, 560, 2 do
			local hit = workspace:Raycast(Vector3.new(x, 200, z), Vector3.new(0, -400, 0), rp)
			local mat = hit and hit.Instance:GetAttribute("Padmateriaal")
			if hit and mat ~= "rand" then
				local y = hit.Position.Y; local kant = mat == "kantsteen"
				local th = workspace:Raycast(Vector3.new(x, y + 8, z), Vector3.new(0, -48, 0), rt)
				local g = th and th.Position.Y or y - 40
				if g > y + 0.02 then
					t:FillBlock(CFrame.new(x, y - AF + 12, z), Vector3.new(2, 24, 2), Enum.Material.Air); weg += 1
				elseif (not kant and g < y - 2.0) or (kant and g < y - 1.6) then
					local top = y - (kant and KANT or OP)
					t:FillBlock(CFrame.new(x, (top + g - 1) / 2, z), Vector3.new(2, top - g + 1, 2), Enum.Material.Ground); bij += 1
				end
			end
		end
		if z % 20 == 0 then task.wait() end
	end
	return weg, bij
end

function M.meet()
	local rp, rt = params(); local n, boven, b05, randn, kier, diep = 0, 0, 0, 0, 0, 0
	for z = -760, 250, 2 do
		for x = -200, 560, 2 do
			local hit = workspace:Raycast(Vector3.new(x, 200, z), Vector3.new(0, -400, 0), rp)
			if hit then
				local mat = hit.Instance:GetAttribute("Padmateriaal")
				local th = workspace:Raycast(Vector3.new(x, hit.Position.Y + 8, z), Vector3.new(0, -48, 0), rt)
				local dd = th and (th.Position.Y - hit.Position.Y) or -99
				if mat == "kantsteen" then randn += 1; if dd < -1.8 then kier += 1 end
				elseif mat ~= "rand" then n += 1
					if dd > 0.02 then boven += 1; if dd > 0.5 then b05 += 1 end end
					if dd < -2.0 then diep += 1 end
				end
			end
		end
		if z % 40 == 0 then task.wait() end
	end
	return string.format("padpunten %d | grond boven pad %d (%.2f%%), >0,5 stud %d | grond >2 stud onder pad %d | stoeprand %d, kier (grond >1,8 lager) %d",
		n, boven, boven / n * 100, b05, diep, randn, kier)
end

return M
