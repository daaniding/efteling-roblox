-- Zichtrand (models/VG_Bomen/build/04_zichtrand.py): struikenstrook langs elke padrand, zodat je vanaf een pad geen ander pad ziet.
-- Data: ServerStorage.BomenVB.Zichtrand (per plek 8 tekens base64, 43 bit: rij 1 | maat 4 | draaiing 6 | Z 16 | X 16 (0,1 stud, +2000)).
-- Een plek vervalt als er al een rododendron/taxus/struik binnen 6 stud (2 m) staat. Struiken 2,2-3,2 m hoog (boven ooghoogte).
-- Rij 1 (naast het pad): vooral rododendron; rij 2: mix. Uit: workspace.SprookjesbosZichtrand.
local A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local IDX = {}; for i = 1, #A do IDX[A:sub(i, i)] = i - 1 end
local bron = game.ServerStorage.BomenBronV3
local RIJ1 = {"rododendron0", "rododendron1", "rododendron0", "rododendron1", "taxus0", "taxus1"}
local RIJ2 = {"rododendron0", "taxus0", "taxus1", "struik0", "struik1", "rododendron1"}
-- bestaande struiken (raster 6 stud)
local raster = {}
local function sleutel(x, z) return math.floor(x / 6) .. "," .. math.floor(z / 6) end
for _, d in ipairs(workspace:GetDescendants()) do
	if d:IsA("Model") and (d.Name:match("^rododendron%d*$") or d.Name:match("^taxus%d*$") or d.Name:match("^struik%d*$")) then
		local p = d:GetPivot().Position; local k = sleutel(p.X, p.Z); raster[k] = raster[k] or {}; table.insert(raster[k], p)
	end
end
local function bezet(x, z)
	local cx, cz = math.floor(x / 6), math.floor(z / 6)
	for i = -1, 1 do for j = -1, 1 do
		for _, p in ipairs(raster[(cx + i) .. "," .. (cz + j)] or {}) do if (p.X - x) ^ 2 + (p.Z - z) ^ 2 < 36 then return true end end
	end end
	return false
end
local t = workspace.Terrain
local rt = RaycastParams.new(); rt.FilterType = Enum.RaycastFilterType.Include; rt.FilterDescendantsInstances = {t}; rt.IgnoreWater = true
local oud = workspace:FindFirstChild("SprookjesbosZichtrand"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "SprookjesbosZichtrand"; map.Parent = workspace
local data = game.ServerStorage.BomenVB.Zichtrand.Value
local n, over = 0, 0
for i = 1, #data, 8 do
	local b = {}
	for c = 1, 8 do local v = IDX[data:sub(i + c - 1, i + c - 1)]; for j = 0, 5 do b[(c - 1) * 6 + j] = bit32.extract(v, j) end end
	local function veld(o, k) local s = 0; for j = k - 1, 0, -1 do s = s * 2 + b[o + j] end; return s end
	local rij, maat, rot, Z, X = veld(0, 1), veld(1, 4), veld(5, 6), veld(11, 16) / 10 - 2000, veld(27, 16) / 10 - 2000
	if bezet(X, Z) then over += 1 else
		local lijst = rij == 0 and RIJ1 or RIJ2
		local sj = bron[lijst[(maat % #lijst) + 1]]; local m = sj:Clone()
		local _, sz = m:GetBoundingBox()
		local doel = 6.6 + maat / 15 * 3.0      -- 2,2 .. 3,2 m
		m:ScaleTo(m:GetScale() * doel / sz.Y)
		local g = workspace:Raycast(Vector3.new(X, 200, Z), Vector3.new(0, -400, 0), rt)
		local y = (g and g.Position.Y or 0)
		local cf, sz2 = m:GetBoundingBox()
		local onder = cf.Position.Y - sz2.Y / 2
		m:PivotTo(CFrame.new(X, m:GetPivot().Position.Y - onder + y - 0.3, Z) * CFrame.Angles(0, rot / 64 * 2 * math.pi, 0))
		m.Parent = map; n += 1
		local k = sleutel(X, Z); raster[k] = raster[k] or {}; table.insert(raster[k], Vector3.new(X, y, Z))
	end
	if (n + over) % 80 == 0 then task.wait() end
end
return n .. " struiken geplaatst, " .. over .. " plekken hadden al een struik"
