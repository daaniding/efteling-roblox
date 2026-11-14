-- Terrein rond Het Meisje met de Zwavelstokjes (Daan: "de scene goed met hoogteverschillen"): de kunstheuvel loopt aan de zijkanten en achter
-- zacht uit in het maaiveld (geen harde plaatranden meer), golvende bosgrond met lage bulten rondom, paden blijven vlak en zakken er
-- vloeiend in, oevers van het vijvertje lopen naar het water af. Alleen terrein erbij (FillBlock), niets weggehaald. Modelframe als plaats_zwavelstokjes.luau.
local F = Vector3.new(-0.233, 0, -0.972)
local ORIGIN = CFrame.new(120.36, 2.0, -466.71) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S, HM = 3, 0.9
local HEUVEL = {{-12.6, -1.4}, {-10.4, -5.4}, {-6.9, -3.45}, {3.3, -3.45}, {3.3, -4.35}, {8.25, -4.35}, {8.25, 1.2}, {10.2, 1.2}, {10.2, 6.6}, {-8.3, 6.6}, {-8.3, -0.6}}
local VIJ = {{-1.88, -3.8}, {-2.22, -7.12}, {-3.35, -10.07}, {-5.32, -11.15}, {-8.64, -11.08}, {-10.49, -10.44}, {-10.72, -8.82}, {-8.75, -8.16}, {-5.78, -7.49}, {-4.32, -5.39}, {-3.59, -3.8}}
local PADEN = {{{-1.4, -4.45}, {12.0, -4.45}, {12.0, -11.4}, {-1.4, -11.4}}, {{-17.0, -11.4}, {12.0, -11.4}, {12.0, -14.5}, {-17.0, -14.5}},
	{{-17.0, -11.4}, {-11.0, -11.4}, {-11.0, -6.2}, {-13.4, -3.0}, {-17.0, -3.0}}}
local OPRIT = {{-11.6, -3.9}, {-12.7, -2.1}, {-15.6, -4.3}, {-14.0, -7.1}}           -- oprit + trap: niet ophogen
local TRAP = {{7.6, 1.3}, {10.6, 1.3}, {10.6, -4.6}, {7.6, -4.6}}     -- trap + aanloop: vlak op padhoogte
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function segd(x, y, p) local best = 1e9; local n = #p
	for i = 1, n do local a, b = p[i], p[(i % n) + 1]
		local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function paddist(x, y)
	local d = 1e9
	for _, p in ipairs(PADEN) do if inside(x, y, p) then return 0 end; d = math.min(d, segd(x, y, p)) end
	return d
end
local function glad(t) t = math.clamp(t, 0, 1); return t * t * (3 - 2 * t) end
local T = workspace.Terrain
local n = 0
for gx = -26, 24, 4 / S do
	for gy = -16, 20, 4 / S do
		local wpos = (ORIGIN * CFrame.new(-gx * S, 0, gy * S)).Position
		local X, Z = math.floor(wpos.X / 4) * 4 + 2, math.floor(wpos.Z / 4) * 4 + 2
		local l = ORIGIN:PointToObjectSpace(Vector3.new(X, 0, Z)); local x, y = -l.X / S, l.Z / S
		if inside(x, y, VIJ) or inside(x, y, OPRIT) or inside(x, y, TRAP) then continue end
		local h = 0
		if inside(x, y, HEUVEL) then h = HM - 0.05
		else
			local d = segd(x, y, HEUVEL)
			local voor = y < -1.8 and x > -11.2 and x < 8.6                                                    -- voorkant: keermuur blijft zichtbaar
			if not voor then h = HM * glad(1 - d / 5.5) end
			local bult = 0.35 * math.noise(x / 7.5, y / 7.5, 4.1) + 0.2 * math.noise(x / 3.2, y / 3.2, 9.7)  -- golvende bosgrond
			h = math.max(h, 0.28 + bult)
			local dv = segd(x, y, VIJ); h = math.min(h, -0.05 + dv * 0.35)                                       -- oever loopt af naar het water
			local dp = paddist(x, y); h = h * glad(dp / 2.2)                                                      -- paden vlak, vloeiend aansluiten
			if voor then h = math.min(h, 0.15) end
		end
		if h > 0.04 then
			local top = 2 + h * S
			local mat = (segd(x, y, HEUVEL) < 2.5 and not inside(x, y, HEUVEL)) and Enum.Material.LeafyGrass or Enum.Material.Grass
			T:FillBlock(CFrame.new(X, (top - 6) / 2, Z), Vector3.new(4, top + 6, 4), mat); n += 1
		end
	end
	task.wait()
end
for x = 7.6, 10.6, 0.5 do for y = -4.6, -1.6, 0.5 do                                -- voet van de trap vrij (eerder opgehoogd terrein weg)
	local p = (ORIGIN * CFrame.new(-x * S, 0, y * S)).Position
	T:FillBlock(CFrame.new(math.floor(p.X / 4) * 4 + 2, 6, math.floor(p.Z / 4) * 4 + 2), Vector3.new(4, 8, 4), Enum.Material.Air) end end
return "terreincellen opgehoogd: " .. n
