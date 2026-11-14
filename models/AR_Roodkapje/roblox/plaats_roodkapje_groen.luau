-- Roodkapje: dicht bos rond het grindpad omhoog (Pad_naar_roodkapje, Roodkapje_vanuit_bos_2009, Roodkapje_frisse_vijver_2023):
-- hoge beuken/eiken/dennen, rododendrons en taxussen tegen de rotsmuren, varens en bodembedekkers, oevergroen rond het vennetje.
-- Pad, kijkplein, bordes, trap en het zicht vanaf het pad op de voorgevel blijven vrij. Modelframe als plaats_roodkapje.luau.
local F = Vector3.new(0.098, 0, -0.995)
local ORIGIN = CFrame.new(228.0, 2.15, 137.85) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local POLY = {{-17.37, 2.54}, {-16.42, 2.1}, {-15.1, 1.48}, {-13.53, 0.74}, {-11.83, -0.05}, {-10.11, -0.85}, {-8.48, -1.58}, {-7.09, -2.18}, {-6.04, -2.6}, {-5.4, -2.82}, {-5.1, -2.9}, {-5.18, -2.89}, {-5.48, -2.95}, {-5.48, -2.93}, {-5.04, -2.74}, {-4.4, -2.6}, {-3.66, -3.1}, {-2.84, -3.1}, {-2.0, -2.3}, {-1.14, -2.3}, {-0.26, -2.3}, {0.61, -2.3}, {1.45, -2.3}, {2.24, -2.3}, {2.95, -2.81}, {3.7, -2.53}, {4.6, -2.07}, {5.58, -1.48}, {6.6, -0.82}, {7.6, -0.13}, {8.56, 0.52}, {9.46, 1.11}, {10.24, 1.55}, {10.81, 1.84}, {11.21, 2.03}, {11.6, 2.2}, {12.15, 2.33}, {12.73, 2.32}, {13.1, 2.25}, {13.34, 2.18}, {13.73, 2.1}, {14.36, 1.95}, {15.11, 1.73}, {15.9, 1.46}, {16.71, 1.17}, {17.5, 0.89}, {18.2, 0.62}, {18.78, 0.41}, {19.2, 0.26}, {18.06, -2.94}, {17.62, -2.78}, {17.02, -2.56}, {16.32, -2.3}, {15.56, -2.02}, {14.8, -1.75}, {14.08, -1.51}, {13.47, -1.33}, {12.98, -1.22}, {12.58, -1.13}, {12.3, -1.06}, {12.28, -1.05}, {12.55, -1.05}, {12.74, -1.01}, {12.65, -1.05}, {12.32, -1.21}, {11.85, -1.44}, {11.23, -1.79}, {10.45, -2.31}, {9.52, -2.94}, {8.48, -3.65}, {7.39, -4.36}, {6.25, -5.04}, {5.09, -5.63}, {3.92, -6.07}, {2.74, -6.33}, {1.58, -6.43}, {0.47, -6.42}, {-0.59, -6.34}, {-1.56, -6.22}, {-2.44, -6.1}, {-3.18, -6.01}, {-3.74, -5.97}, {-4.02, -5.98}, {-4.02, -5.99}, {-3.99, -5.99}, {-4.32, -6.14}, {-5.02, -6.29}, {-5.71, -6.24}, {-6.39, -6.07}, {-7.24, -5.78}, {-8.4, -5.32}, {-9.86, -4.69}, {-11.52, -3.94}, {-13.26, -3.14}, {-14.98, -2.34}, {-16.55, -1.6}, {-17.86, -0.98}, {-18.79, -0.55}}
local VEN = {-13.8, 8.8}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local function polyd(x, y, p) local best = 1e9; local n = #p
	for i = 1, n do local a, b = p[i], p[(i % n) + 1]
		local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function huis(x, y, m) m = m or 0   -- huisje + toren + schoorsteen, bordes, trap
	return (x > -2.6 - m and x < 3.3 + m and y > -3.4 - m and y < 3.5 + m) or (x > -4.4 - m and x < -2.2 and y > -3.2 - m and y < 5.4 + m)
end
local function zicht(x, y) return y < -5.0 and y > -16 and x > -7 and x < 7 end      -- vanaf het pad/de overkant op de voorgevel
local function ven(x, y) return math.sqrt((x - VEN[1]) ^ 2 + (y - VEN[2]) ^ 2) end
local R = Random.new(1960)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L, bomen = {}, {}
for _ = 1, 4000 do                                                                      -- hoge bomen
	local x, y = U(-26, 26), U(-20, 18)
	local d = polyd(x, y, POLY)
	if not inside(x, y, POLY) and d > 1.6 and not huis(x, y, 2.2) and not zicht(x, y) and ven(x, y) > 4.2 then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 14 then ok = false; break end end
		if ok and #bomen < 58 then table.insert(bomen, {x, y}); local s = {"beuk0", "eik0", "den0", "den1", "beuk0", "kastanje0", "berk0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.95, 1.3)}) end
	end
end
for _ = 1, 3000 do                                                                      -- rododendrons/taxus/heesters tegen de muren en onder de bomen
	local x, y = U(-24, 24), U(-18, 16)
	local d = polyd(x, y, POLY)
	if not inside(x, y, POLY) and d > 0.7 and d < 9 and not huis(x, y, 0.6) and ven(x, y) > 3.8 and R:NextNumber() < (d < 3 and 0.5 or 0.18) then
		if zicht(x, y) and (d < 3 or R:NextNumber() < 0.7) then continue end              -- in het zicht alleen verder weg
		local s = {"rododendron0", "rododendron1", "taxus0", "PH_shrub_03_1", "rododendron0", "PH_shrub_02_3"}
		table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.25)})
	end
end
for _ = 1, 4200 do                                                                      -- varens en bodembedekkers
	local x, y = U(-24, 24), U(-18, 16)
	local d = polyd(x, y, POLY)
	if not inside(x, y, POLY) and d > 0.45 and not huis(x, y, 0.3) and ven(x, y) > 3.35 and R:NextNumber() < 0.45 then
		local s = {"PH_fern_02_0", "PH_fern_02_3", "varen1", "PH_fern_02_2", "PH_fern_02_0"}
		table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.8, 1.2)})
	end
end
for k = 1, 40 do                                                                        -- oevergroen rond het vennetje
	local a = k / 40 * math.pi * 2 + U(-0.05, 0.05); local r = U(3.35, 4.1)
	local s = {"PH_fern_02_0", "PH_shrub_02_3", "bloem_paars", "varen1"}
	table.insert(L, {s[R:NextInteger(1, #s)], VEN[1] + r * math.cos(a), VEN[2] + r * math.sin(a), U(0.7, 1.0)})
end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), game.ServerStorage:FindFirstChild("VVPlanten"), workspace:FindFirstChild("HerautenpleinGroen"), workspace:FindFirstChild("HansEnGrietjeGroen")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("RoodkapjeGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "RoodkapjeGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}; rp.IgnoreWater = false
local n, mis, klein = 0, {}, {PH_fern_02_0 = true, PH_fern_02_3 = true, PH_fern_02_2 = true, varen1 = true, bloem_paars = true, PH_shrub_02_3 = true}
for i, p in ipairs(L) do
	local t = bron(p[1])
	if not t then mis[p[1]] = true; continue end
	local c = t:Clone()
	local pos = (ORIGIN * CFrame.new(-p[2] * S, 0, p[3] * S)).Position
	local hit = workspace:Raycast(pos + Vector3.new(0, 30, 0), Vector3.new(0, -60, 0), rp)
	if hit and hit.Material == Enum.Material.Water then c:Destroy(); continue end
	local y = hit and hit.Position.Y or 2
	local rot = CFrame.Angles(0, R:NextNumber() * math.pi * 2, 0)
	if c:IsA("Model") then
		if p[4] ~= 1 then c:ScaleTo(c:GetScale() * p[4]) end
		local cf, sz = c:GetBoundingBox(); local onder = cf.Position.Y - sz.Y / 2
		c:PivotTo(CFrame.new(pos.X, y + (c:GetPivot().Position.Y - onder) - 0.15, pos.Z) * rot)
	elseif c:IsA("BasePart") then
		c.Size = c.Size * p[4]; c.CFrame = CFrame.new(pos.X, y + c.Size.Y / 2 - 0.15, pos.Z) * rot
	end
	if klein[p[1]] then for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") then d.CastShadow = false end end; if c:IsA("BasePart") then c.CastShadow = false end end
	c.Parent = map; n += 1
	if i % 150 == 0 then task.wait() end
end
map.Parent = workspace
local mm = {}; for k in pairs(mis) do table.insert(mm, k) end
return string.format("%d planten (%d bomen); ontbrekend: %s", n, #bomen, table.concat(mm, ","))
