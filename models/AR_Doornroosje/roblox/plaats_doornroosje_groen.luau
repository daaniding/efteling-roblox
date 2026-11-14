-- Doornroosje groen (Doornroosje-2024-15/-01/_Rozen/_Luchtfoto): rododendrons en taxus op de heuvel, varens langs de vijver, rode rozen
-- (de "doornhaag") langs de muren, bomen eromheen. Trappen, terras en kasteel blijven vrij. Draai na plaats_doornroosje + terrein_doornroosje.
local OX, OZ, S = 362.96, -262.92, 3
local function W(x, y) return Vector3.new(OX + S * x, 0, OZ - S * y) end
local WEST = {{-17.15, 1.69}, {-13.65, -3.62}, {-11.43, -4.66}, {-7.61, -4.99}, {-6.07, -4.48}, {-5.16, -3.43}, {-4.87, 1.04}}
local OOST = {{1.47, 1.69}, {1.35, -2.06}, {2.12, -3.65}, {2.48, -4.94}, {7.35, -5.14}, {10.44, -7.13}, {13.3, -10.24}, {15.35, -13.35}}
local TERRAS = {{-4.87, 1.04}, {-4.44, 2.56}, {-3.12, 3.65}, {-0.98, 3.92}, {0.96, 2.92}, {1.47, 1.69}}
local NOORDPAD = {{39.46, 27.57}, {30.8, 22.45}, {15.5, 23.49}, {-0.82, 21.44}, {-11.12, 19.58}, {-14.33, 19.48}, {-16.94, 19.56}, {-19.9, 19.14}}
local function segd(x, y, p)
	local best = 1e9
	for i = 1, #p - 1 do local a, b = p[i], p[i + 1]; local dx, dy = b[1] - a[1], b[2] - a[2]; local L2 = math.max(dx * dx + dy * dy, 1e-9)
		local t = math.clamp(((x - a[1]) * dx + (y - a[2]) * dy) / L2, 0, 1); best = math.min(best, math.sqrt((x - a[1] - t * dx) ^ 2 + (y - a[2] - t * dy) ^ 2)) end
	return best end
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), game.ServerStorage:FindFirstChild("VVPlanten")}) do
		if f then for _, c in ipairs(f:GetChildren()) do if c.Name == naam or string.sub(c.Name, 1, #naam) == naam then t = c; break end end end
		if t then break end end end
	return t
end
local oud = workspace:FindFirstChild("DoornroosjeGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "DoornroosjeGroen"
local bouw = {}; for _, n in ipairs({"DoornroosjeKasteel", "DoornroosjeOmgeving"}) do local m = workspace:FindFirstChild(n); if m then table.insert(bouw, m) end end
local rpT = RaycastParams.new(); rpT.FilterType = Enum.RaycastFilterType.Include; rpT.FilterDescendantsInstances = {workspace.Terrain}
local rpB = RaycastParams.new(); rpB.FilterType = Enum.RaycastFilterType.Include; rpB.FilterDescendantsInstances = bouw
local R = Random.new(1952)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local L = {}
for _ = 1, 4200 do
	local x, y = U(-24, 30), U(-18, 21)
	local vrij = segd(x, y, WEST) > 1.9 and segd(x, y, OOST) > 2.0 and segd(x, y, TERRAS) > 1.6 and segd(x, y, NOORDPAD) > 2.2
	if vrij and R:NextNumber() < 0.22 then
		local r = R:NextNumber(); local s, sc, schaduw
		if r < 0.42 then s = {"rododendron0", "rododendron1", "taxus0", "struik0", "struik1", "PH_shrub_03_1"}; sc = U(0.7, 1.15); schaduw = true
		elseif r < 0.7 then s = {"PH_fern_02_0", "PH_fern_02_2", "PH_fern_02_3", "varen1"}; sc = U(2.0, 3.0); schaduw = false
		elseif r < 0.82 then s = {"bloem_rood"}; sc = U(1.6, 2.4); schaduw = false
		else s = {"PH_shrub_02_3", "PH_periwinkle_plant_1", "PH_weed_plant_02_2"}; sc = U(1.4, 2.2); schaduw = false end
		table.insert(L, {s[R:NextInteger(1, #s)], x, y, sc, schaduw})
	end
end
local bomen = {}
for _ = 1, 3000 do                                                                   -- bomen rondom (niet op de heuvel, niet in de zichtlijn vanaf het noordpad)
	local x, y = U(-34, 40), U(-28, 32)
	local d = math.sqrt(x * x + y * y)
	local zicht = y > 5 and y < 20 and x > -14 and x < 14
	if d > 13 and not zicht and segd(x, y, WEST) > 4 and segd(x, y, OOST) > 4 and segd(x, y, NOORDPAD) > 4 then
		local ok = true; for _, b in ipairs(bomen) do if (x - b[1]) ^ 2 + (y - b[2]) ^ 2 < 40 then ok = false; break end end
		if ok and #bomen < 34 then table.insert(bomen, {x, y}); local s = {"beuk0", "beuk1", "eik0", "eik1", "den0", "den1", "berk0", "kastanje0"}; table.insert(L, {s[R:NextInteger(1, #s)], x, y, U(0.9, 1.25), true}) end
	end
end
local n, weg = 0, 0
for i, p in ipairs(L) do
	local pos = W(p[2], p[3])
	local hit = workspace:Raycast(pos + Vector3.new(0, 80, 0), Vector3.new(0, -160, 0), rpT)
	if not hit or hit.Material == Enum.Material.Water then continue end
	local hb = workspace:Raycast(pos + Vector3.new(0, 80, 0), Vector3.new(0, -160, 0), rpB)
	if hb and hb.Position.Y > hit.Position.Y - 0.5 then weg += 1; continue end            -- onder/op een gebouw, trap of muur: overslaan
	local t = bron(p[1]); if not t then continue end
	local c = t:Clone(); local rot = CFrame.Angles(0, R:NextNumber() * math.pi * 2, 0)
	if c:IsA("Model") then
		if p[4] ~= 1 then c:ScaleTo(c:GetScale() * p[4]) end
		local cf, sz = c:GetBoundingBox(); local onder = cf.Position.Y - sz.Y / 2
		c:PivotTo(CFrame.new(pos.X, hit.Position.Y + (c:GetPivot().Position.Y - onder) - 0.25, pos.Z) * rot)
		if not p[5] then for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") then d.CastShadow = false end end end
	end
	c.Parent = map; n += 1
	if i % 150 == 0 then task.wait() end
end
map.Parent = workspace
return string.format("%d planten (%d bomen), %d overgeslagen bij gebouwen", n, #bomen, weg)
