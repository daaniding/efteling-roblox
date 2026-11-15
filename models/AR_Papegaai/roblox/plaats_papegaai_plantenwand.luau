-- De Sprekende Papegaai: dichte plantenwand achter en naast het muurtje + groenbulten tegen de pijlers (Daan: "erachter zit een muur aan planten";
-- eind60/1973). Draaien NA plaats_papegaai_groen.luau. Zicht vanaf het pad (linksvoor, y < -0.6) blijft vrij van hoge struiken.
local F = Vector3.new(-0.6, 0, 0.8)
local ORIGIN = CFrame.new(177.51, 2.0, 28.92) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local map = workspace.SprekendePapegaaiGroen
local R = Random.new(1952)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local function bron(naam) local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then local v = game.ServerStorage:FindFirstChild("VVEchtePlanten"); if v then for _, c in ipairs(v:GetChildren()) do if string.sub(c.Name, 1, #naam) == naam then t = c; break end end end end
	return t end
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local function zone(x, y)
	if y > 2.75 and y < 6.0 and math.abs(x) < 5.2 then return "achter" end
	if math.abs(x) > 1.75 and math.abs(x) < 4.6 and y > -0.8 and y <= 2.75 and x * x + y * y > 3.15 * 3.15 then return "zij" end
end
local L = {}
for gx = -5.2, 5.2, 0.85 do for gy = -0.8, 6.0, 0.85 do
	local x, y = gx + U(-0.3, 0.3), gy + U(-0.3, 0.3); local z = zone(x, y)
	if z then local s = (z == "achter" and y > 3.6) and {"rododendron1", "taxus1", "rododendron0", "PH_shrub_03_1", "taxus0"} or {"rododendron0", "rododendron1", "PH_shrub_03_1", "PH_shrub_02_3"}
		table.insert(L, {s[R:NextInteger(1, #s)], x, y, (z == "achter") and U(1.2, 1.7) or U(0.9, 1.3)}) end
end end
for _, p in ipairs({{-3.2, 5.6}, {0.4, 6.4}, {3.6, 5.4}, {-4.6, 3.2}, {4.7, 2.6}}) do table.insert(L, {(R:NextNumber() < 0.5) and "beuk0" or "berk0", p[1], p[2], U(0.9, 1.2)}) end
for _, s in ipairs({-1, 1}) do                                                  -- groenbulten tegen de pijlers en de muurzijden
	for _, p in ipairs({{1.75, 1.75, 1.0}, {1.55, 1.3, 0.85}, {2.0, 2.5, 1.2}, {2.1, 3.1, 1.3}, {1.95, 1.95, 1.1}}) do table.insert(L, {"rododendron0", s * p[1], p[2], p[3]}) end
	for _, p in ipairs({{1.6, 1.85}, {1.85, 1.5}, {1.45, 1.6}}) do table.insert(L, {"PH_shrub_03_1", s * p[1], p[2], U(1.1, 1.4)}) end
end
for _ = 1, 110 do                                                               -- rechts naast de leuning tot het pad: lagere struiken en varens
	local x, y = U(3.5, 7.0), U(-3.6, 0.6)
	if x * x + y * y > 3.3 * 3.3 then local k = R:NextNumber(); table.insert(L, {k < 0.35 and "rododendron0" or (k < 0.55 and "PH_shrub_03_1" or (k < 0.75 and "PH_fern_02_0" or "rododendron1")), x, y, U(0.8, 1.2)}) end
end
for _, c in ipairs(map:GetChildren()) do                                         -- klein spul in de wandzone weg
	local p = c:IsA("Model") and c:GetPivot().Position or (c:IsA("BasePart") and c.Position)
	if p then local l = ORIGIN:PointToObjectSpace(p); local x, y = -l.X / S, l.Z / S
		if zone(x, y) and (c:IsA("BasePart") or c:GetExtentsSize().Y < 6) then c:Destroy() end end
end
local n = 0
for i, p in ipairs(L) do
	local t = bron(p[1]); if not t then continue end
	local c = t:Clone(); local pos = (ORIGIN * CFrame.new(-p[2] * S, 0, p[3] * S)).Position
	local hit = workspace:Raycast(pos + Vector3.new(0, 30, 0), Vector3.new(0, -60, 0), rp); local y = hit and hit.Position.Y or 2
	local rot = CFrame.Angles(0, R:NextNumber() * math.pi * 2, 0)
	if c:IsA("Model") then c:ScaleTo(c:GetScale() * p[4]); local cf, sz = c:GetBoundingBox(); c:PivotTo(CFrame.new(pos.X, y + (c:GetPivot().Position.Y - (cf.Position.Y - sz.Y / 2)) - 0.15, pos.Z) * rot)
	elseif c:IsA("BasePart") then c.Size = c.Size * p[4]; c.CFrame = CFrame.new(pos.X, y + c.Size.Y / 2 - 0.15, pos.Z) * rot end
	c.Parent = map; n += 1
	if i % 60 == 0 then task.wait() end
end
return n .. " planten in de wand"
