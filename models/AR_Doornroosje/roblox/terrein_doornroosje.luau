-- Doornroosje terrein: heuvel tot de kasteelvloer (Z0 = 4.5 m), grond onder beide trappen op traphoogte, steile rotskant naar de vijver,
-- vijver (OSM 763240416) als terreinwater. Modelframe = OSM-assen: lokaal(x, y, z) = (OX + 3x, 2 + 3z, OZ - 3y).
local OX, OZ, S, Z0 = 362.96, -262.92, 3, 4.5
local function W(x, y) return OX + S * x, OZ - S * y end
local KERN = {{-9.0, 1.5}, {-7.5, -2.5}, {-4.4, -7.6}, {1.8, -7.8}, {2.6, -4.2}, {6.0, -0.5}, {6.2, 4.8}, {1.8, 6.8}, {-3.8, 6.9}, {-8.2, 4.4}}
local WEST = {{-17.15, 1.69}, {-13.65, -3.62}, {-11.43, -4.66}, {-7.61, -4.99}, {-6.07, -4.48}, {-5.16, -3.43}, {-4.87, 1.04}}
local OOST = {{1.47, 1.69}, {1.35, -2.06}, {2.12, -3.65}, {2.48, -4.94}, {7.35, -5.14}, {10.44, -7.13}, {13.3, -10.24}, {15.35, -13.35}}
local VIJVER = {{-10.97, 6.71}, {-9.00, 11.86}, {-5.24, 15.15}, {0.44, 16.42}, {5.52, 17.29}, {8.13, 16.07}, {10.81, 16.57}, {13.62, 15.93}, {14.02, 12.45}, {17.40, 12.82}, {18.51, 10.05}, {23.05, 3.70}, {25.46, 2.23}, {27.18, 0.95}, {29.72, -2.96}, {30.33, -6.05}, {30.65, -8.48}, {27.64, -11.38}, {26.66, -13.04}, {25.09, -14.42}, {23.34, -13.95}, {22.55, -11.89}, {22.31, -9.45}, {20.60, -5.35}, {19.16, -3.28}, {17.04, -1.90}, {15.41, -0.16}, {14.30, 2.74}, {13.10, 4.26}, {12.68, 6.83}, {12.22, 8.36}, {11.61, 11.16}, {9.38, 12.85}, {6.16, 14.16}, {2.81, 13.92}, {1.77, 11.81}, {2.61, 9.55}, {5.03, 7.98}, {5.43, 6.76}, {2.56, 6.13}, {-4.11, 6.07}, {-8.06, 4.84}}   -- OSM 763240416
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function segd(x, y, p, closed)
	local best = 1e9; local n = #p
	for i = 1, closed and n or n - 1 do local a, b = p[i], p[(i % n) + 1]
		local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function langs(x, y, p, za, zb)                       -- afstand tot de trap + hoogte op het dichtstbijzijnde punt (lineair over de lengte)
	local tot, acc = 0, {}; for i = 1, #p - 1 do acc[i] = tot; tot += math.sqrt((p[i + 1][1] - p[i][1]) ^ 2 + (p[i + 1][2] - p[i][2]) ^ 2) end
	local best, bz = 1e9, za
	for i = 1, #p - 1 do local a, b = p[i], p[i + 1]; local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); local d = math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)
		if d < best then best = d; bz = za + (zb - za) * (acc[i] + t * math.sqrt(L2)) / tot end end
	return best, bz end
local function glad(t) t = math.clamp(t, 0, 1); return t * t * (3 - 2 * t) end
local T = workspace.Terrain; local n, nw = 0, 0
for gx = -24, 22, 4 / S do
	for gy = -18, 22, 4 / S do
		local wx, wz = W(gx, gy); local X, Z = math.floor(wx / 4) * 4 + 2, math.floor(wz / 4) * 4 + 2
		local x, y = (X - OX) / S, -(Z - OZ) / S
		if inside(x, y, VIJVER) then
			T:FillBlock(CFrame.new(X, 4, Z), Vector3.new(4, 24, 4), Enum.Material.Air)
			T:FillBlock(CFrame.new(X, -1, Z), Vector3.new(4, 4, 4), Enum.Material.Water)
			T:FillBlock(CFrame.new(X, -6, Z), Vector3.new(4, 6, 4), Enum.Material.Ground); nw += 1
		else
			local dk = inside(x, y, KERN) and 0 or segd(x, y, KERN, true)
			local h = Z0 * glad(1 - dk / 7.5) - 0.3                                   -- heuvel, ~7.5 m uitloop
			local dw, zw = langs(x, y, WEST, 0.4, Z0); local do_, zo = langs(x, y, OOST, Z0, 0.0)
			if dw < 1.3 then h = zw - 0.45 elseif dw < 4 then h = math.max(h, zw - 0.45) * glad((4 - dw) / 2.7) + h * (1 - glad((4 - dw) / 2.7)) end
			if do_ < 1.4 then h = zo - 0.45 elseif do_ < 4 then h = math.max(h, zo - 0.45) * glad((4 - do_) / 2.6) + h * (1 - glad((4 - do_) / 2.6)) end
			h += 0.25 * math.noise(x / 4, y / 4, 1.7)
			if h > 0.05 then
				local top = 2 + h * S
				local steil = y > 3 and segd(x, y, VIJVER, true) < 5                         -- vijverkant: rots
				T:FillBlock(CFrame.new(X, (top - 6) / 2, Z), Vector3.new(4, top + 6, 4), steil and Enum.Material.Rock or Enum.Material.Ground); n += 1
			end
		end
	end
	task.wait()
end
local L = workspace:FindFirstChild("EftelingLayout"); local mk = L and L:FindFirstChild("Doornroosje", true); if mk then mk:Destroy() end
return string.format("heuvel %d cellen, vijver %d cellen", n, nw)
