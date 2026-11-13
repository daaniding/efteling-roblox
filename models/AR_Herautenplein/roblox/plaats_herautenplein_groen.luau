-- Herautenplein groen: bloemen in de 4 bloembakken voor de taxusblokken (paars/roze, Herautenplein2010), rode bloemen in de gebogen
-- vakken rond het Ezeltje (Herautenplein99), bomen in het bosje (OSM 505382909). Bronmodellen: bestaande bloem_*/beuk/eik in de place.
-- Map workspace.HerautenpleinGroen. Coordinaten uit exports/plein_extra.json (frame Prinsenpoort/Herautenplein).
local F = Vector3.new(-0.968, 0, 0.250); local O = CFrame.new(151.58, 2.0, -228.65) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local function L(x, y, z) return (O * CFrame.new(-x * 3, z * 3, y * 3)).Position end
local VAKKEN = {{{1.98, -57.78}, {1.12, -55.97}, {3.54, -54.82}, {7.37, -54.63}, {10.97, -55.96}, {11.95, -56.87}, {10.59, -58.33}, {9.9, -57.69}, {7.05, -56.65}, {4.02, -56.79}}, {{1.47, -73.01}, {2.4, -71.2}, {-0.03, -69.26}, {-1.49, -66.51}, {-1.75, -63.41}, {-3.77, -63.18}, {-3.43, -67.1}, {-1.59, -70.57}}, {{14.78, -63.48}, {14.81, -65.76}, {13.77, -68.54}, {11.6, -70.71}, {9.82, -71.6}, {10.71, -73.39}, {12.83, -72.15}, {15.23, -69.62}, {16.5, -66.22}, {16.68, -63.58}}}
local BOSJE = {{-6.5, -62.66}, {-5.36, -57.87}, {-3.2, -55.31}, {-3.61, -54.16}, {-13.44, -54.03}, {-13.77, -57.2}, {-10.34, -61.27}, {-7.37, -63.68}}
local BAKKEN = { {11.75, -26.48, -15.39}, {11.68, -41.47, -30.48}, {-12.16, -26.48, -15.48}, {-12.2, -41.47, -30.48} }   -- buitenrand x, y van, y tot
local function bron(naam)
	for _, f in ipairs({"HansEnGrietjeGroen", "AssepoesterGroen", "MagischeKlokBos", "VillaVoltaGroen"}) do
		local m = workspace:FindFirstChild(f)
		if m then for _, c in ipairs(m:GetChildren()) do if string.match(c.Name, "^" .. naam) then return c end end end
	end
end
local SRC = {roze = bron("bloem_roze"), paars = bron("bloem_paars"), rood = bron("bloem_rood"), beuk = bron("beuk"), eik = bron("eik")}
local oud = workspace:FindFirstChild("HerautenpleinGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "HerautenpleinGroen"
local rnd = Random.new(1952); local n = 0
local function zet(src, p, schaal)
	local c = src:Clone(); c:PivotTo(CFrame.new(p) * CFrame.Angles(0, rnd:NextNumber(0, math.pi * 2), 0))
	if schaal then c:ScaleTo(c:GetScale() * schaal) end
	for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") then d.Anchored = true; d.CanCollide = false; d.CanTouch = false end end
	c.Parent = map; n += 1
end
-- bloembakken: 2 rijen, afwisselend paars/roze
for _, b in ipairs(BAKKEN) do
	local sx = b[1] > 0 and 1 or -1
	for _, dx in ipairs({0.3, 0.62}) do
		local y = b[2] + 0.45
		while y < b[3] - 0.45 do
			zet(rnd:NextNumber() < 0.5 and SRC.paars or SRC.roze, L(b[1] + sx * dx, y + rnd:NextNumber(-0.05, 0.05), 0.33), rnd:NextNumber(0.85, 1.05)); y += 0.38
		end
	end
end
-- gebogen vakken: rood, raster met punt-in-veelhoek, 0.25 van de rand
local function binnen(poly, x, y)
	local c = false; local j = #poly
	for i = 1, #poly do
		local a, b = poly[i], poly[j]
		if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end
		j = i
	end
	return c
end
local function randafstand(poly, x, y)
	local best = 1e9
	for i = 1, #poly do
		local a, b = poly[i], poly[i % #poly + 1]
		local ax, ay, bx, by = a[1], a[2], b[1], b[2]; local dx, dy = bx - ax, by - ay
		local t = math.clamp(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0, 1)
		best = math.min(best, math.sqrt((ax + t * dx - x) ^ 2 + (ay + t * dy - y) ^ 2))
	end
	return best
end
for _, poly in ipairs(VAKKEN) do
	local x0, x1, y0, y1 = 1e9, -1e9, 1e9, -1e9
	for _, p in ipairs(poly) do x0 = math.min(x0, p[1]); x1 = math.max(x1, p[1]); y0 = math.min(y0, p[2]); y1 = math.max(y1, p[2]) end
	for x = x0, x1, 0.4 do for y = y0, y1, 0.4 do
		local jx, jy = x + rnd:NextNumber(-0.08, 0.08), y + rnd:NextNumber(-0.08, 0.08)
		if binnen(poly, jx, jy) and randafstand(poly, jx, jy) > 0.28 then zet(SRC.rood, L(jx, jy, 0.33), rnd:NextNumber(0.85, 1.05)) end
	end end
end
-- bosje: 3 bomen + ondergroei
local bc = {0, 0}; for _, p in ipairs(BOSJE) do bc[1] += p[1] / #BOSJE; bc[2] += p[2] / #BOSJE end
for i, off in ipairs({{-2.2, 1.2}, {1.8, 0.6}, {-0.3, -2.0}}) do
	local src = (i % 2 == 1) and SRC.beuk or SRC.eik
	if src then zet(src, L(bc[1] + off[1], bc[2] + off[2], 0)) end
end
map.Parent = workspace
return "groen " .. n
