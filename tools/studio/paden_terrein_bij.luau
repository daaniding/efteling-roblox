-- PadenTerreinBij (ServerStorage.AHN_Delta.PadenTerreinBij): terrein en paden op elkaar laten aansluiten, herhaalbaar.
-- 1) uitsnijden: waar de grond door het pad steekt (vooral v1-heuvels bij Klein Duimpje/Repelsteeltje) wordt alles vanaf
--    0,5 stud onder het pad weggehaald met FillBlock(Air).
--    LET OP: niet herhalen bij Doornroosje/Zwavelstokjes: daar ligt het pad onder een v1-plateau en snijdt elke ronde verder
--    in de heuvel (meting 15 nov: 669, 248, 265 plekken). Daar moet de padhoogte het model volgen (stap 5), niet de heuvel weg.
-- 2) kieren: waar de grond onder de stoeprand meer dan 1 stud lager ligt, wordt hij opgevuld tot 0,6 stud onder de rand.
-- Gebruik (Studio, Edit): local f = require(game.ServerStorage.AHN_Delta.PadenTerreinBij); print(f.uitsnijden(-760, 250)); print(f.kieren(-760, 250))
-- Let op: ReadVoxels/WriteVoxels-verschuiven werkt hier niet herhaalbaar (glad terrein middelt met de kolommen ernaast).
local t = workspace.Terrain
local M = {}

local function params()
	local m = workspace.SprookjesbosPaden
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {m}
	local rt = RaycastParams.new(); rt.FilterType = Enum.RaycastFilterType.Include; rt.FilterDescendantsInstances = {t}
	return rp, rt
end

function M.uitsnijden(z0, z1, breed)
	local rp, rt = params(); local n = 0; breed = breed or 2.2
	for z = z0, z1, 2 do
		for x = -200, 560, 2 do
			local hit = workspace:Raycast(Vector3.new(x, 150, z), Vector3.new(0, -300, 0), rp)
			if hit and hit.Instance:GetAttribute("Padmateriaal") ~= "rand" then
				local th = workspace:Raycast(Vector3.new(x, hit.Position.Y + 8, z), Vector3.new(0, -30, 0), rt)
				if th and th.Position.Y > hit.Position.Y + 0.02 then   -- alleen waar de grond echt boven het pad uitkomt
					t:FillBlock(CFrame.new(x, hit.Position.Y - 0.5 + 8, z), Vector3.new(breed, 16, breed), Enum.Material.Air); n += 1
				end
			end
		end
		if z % 20 == 0 then task.wait() end
	end
	return n
end

function M.kieren(z0, z1)
	local rp, rt = params(); local n = 0
	for z = z0, z1, 2 do
		for x = -200, 560, 2 do
			local hit = workspace:Raycast(Vector3.new(x, 150, z), Vector3.new(0, -300, 0), rp)
			if hit and hit.Instance:GetAttribute("Padmateriaal") == "kantsteen" then
				local th = workspace:Raycast(Vector3.new(x, hit.Position.Y + 8, z), Vector3.new(0, -30, 0), rt)
				local dd = th and (th.Position.Y - hit.Position.Y) or -99
				if dd < -1.0 and dd > -12 then
					local top = hit.Position.Y - 0.6; local bodem = th.Position.Y - 1
					t:FillBlock(CFrame.new(x, (top + bodem) / 2, z), Vector3.new(2.2, top - bodem, 2.2), Enum.Material.Ground); n += 1
				end
			end
		end
		if z % 20 == 0 then task.wait() end
	end
	return n
end

return M
