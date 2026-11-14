-- Klein Duimpje gracht aankleden (Efteling_sleeping_ogre: groen kroosdek; Efteling_-_48113963417: riet en gele lissen langs de rand).
-- Kroos/rimpels gekloond uit SprookjesboomWater, riet = siergras (hoog geschaald), lissen = bloem_geel. Draai na plaats_kleinduimpje.luau.
local F = Vector3.new(0.43, 0, 0.90).Unit
local ORIGIN = CFrame.new(435.33, 2.0, -378.66) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local EILAND = {{-2.96, 1.56}, {0.40, 3.42}, {3.37, 2.00}, {4.16, -2.14}, {-3.31, -3.47}}
local WATER = {{-3.31, -3.47}, {-6.26, -2.46}, {-4.72, 3.22}, {0.21, 5.82}, {5.61, 3.90}, {7.59, -1.95}, {4.16, -2.14}, {3.37, 2.00}, {0.40, 3.42}, {-2.96, 1.56}}
local BUITEN = {{-3.31, -3.47}, {-6.26, -2.46}, {-4.72, 3.22}, {0.21, 5.82}, {5.61, 3.90}, {7.59, -1.95}}
local function inside(x, y, p) local c = false; local j = #p
	for i = 1, #p do local a, b = p[i], p[j]; if ((a[2] > y) ~= (b[2] > y)) and (x < (b[1] - a[1]) * (y - a[2]) / (b[2] - a[2]) + a[1]) then c = not c end; j = i end
	return c end
local oud = workspace:FindFirstChild("KleinDuimpjeWater"); if oud then oud:Destroy() end
local wf = Instance.new("Folder"); wf.Name = "KleinDuimpjeWater"
local R = Random.new(4019)
local function U(a, b) return a + (b - a) * R:NextNumber() end
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local function wateroppervlak(x, y)
	local p = lokaal(x, y, 0).Position
	local h = workspace:Raycast(p + Vector3.new(0, 20, 0), Vector3.new(0, -40, 0), rp)
	if h and h.Material == Enum.Material.Water then return h.Position end
end
-- 1) kroos (dicht groen dek, Efteling_sleeping_ogre) en een paar rimpelbronnen
local bron = workspace:FindFirstChild("SprookjesboomWater") or workspace:FindFirstChild("LangnekWater")
local kroosT = bron and bron:FindFirstChild("Kroos"); local rimpelT = bron and bron:FindFirstChild("Rimpelbron")
local nk, nr = 0, 0
for _ = 1, 900 do
	local x, y = U(-6.5, 7.8), U(-5, 6)
	if inside(x, y, WATER) and R:NextNumber() < 0.55 then
		local p = wateroppervlak(x, y)
		if p and kroosT then
			local k = kroosT:Clone(); local s = U(0.8, 1.6)
			if k:IsA("BasePart") then k.Size = k.Size * s; k.CFrame = CFrame.new(p + Vector3.new(0, 0.03, 0)) * CFrame.Angles(0, U(0, 6.28), 0)
			elseif k:IsA("Model") then k:ScaleTo(k:GetScale() * s); k:PivotTo(CFrame.new(p + Vector3.new(0, 0.03, 0)) * CFrame.Angles(0, U(0, 6.28), 0)) end
			k.Parent = wf; nk += 1
		end
	end
end
for i = 1, 5 do
	local x, y = U(-5.5, 7), U(-4, 5.5)
	if inside(x, y, WATER) and rimpelT then local p = wateroppervlak(x, y)
		if p then local r = rimpelT:Clone(); if r:IsA("BasePart") then r.CFrame = CFrame.new(p) elseif r:IsA("Model") then r:PivotTo(CFrame.new(p)) end; r.Parent = wf; nr += 1 end end
end
-- 2) riet en gele lissen langs de buitenrand van de gracht (pollen)
local function plant(naam, pos, schaal)
	local t
	for _, f in ipairs({game.ServerStorage:FindFirstChild("VVPlanten"), game.ServerStorage:FindFirstChild("VVEchtePlanten")}) do
		if f then t = f:FindFirstChild(naam); if t then break end end end
	if not t then return false end
	local c = t:Clone()
	if c:IsA("Model") then c:ScaleTo(c:GetScale() * schaal); local cf, sz = c:GetBoundingBox()
		c:PivotTo(CFrame.new(pos.X, pos.Y + (c:GetPivot().Position.Y - (cf.Position.Y - sz.Y / 2)) - 0.3, pos.Z) * CFrame.Angles(0, U(0, 6.28), 0))
		for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") then d.CastShadow = false end end
	end
	c.Parent = wf; return true
end
local rpG = RaycastParams.new(); rpG.FilterType = Enum.RaycastFilterType.Include
local omg = workspace:FindFirstChild("KleinDuimpjeOmgeving"); rpG.FilterDescendantsInstances = omg and {workspace.Terrain, omg} or {workspace.Terrain}
local nriet = 0
for i = 1, #BUITEN - 1 do
	local a, b = BUITEN[i], BUITEN[i + 1]; local L = math.sqrt((b[1] - a[1]) ^ 2 + (b[2] - a[2]) ^ 2); local k = U(0.3, 1.5)
	while k < L do
		local t = k / L; local x, y = a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t
		local nx, ny = -(b[2] - a[2]) / L, (b[1] - a[1]) / L                         -- zijwaarts: net buiten/op de rand
		for j = 1, R:NextInteger(4, 9) do
			local px, py = x + nx * U(-0.5, 0.6) + U(-0.4, 0.4), y + ny * U(-0.5, 0.6) + U(-0.4, 0.4)
			local p = lokaal(px, py, 0).Position; local h = workspace:Raycast(p + Vector3.new(0, 20, 0), Vector3.new(0, -40, 0), rpG)
			if h then
				local naam = R:NextNumber() < 0.25 and "bloem_geel" or (R:NextNumber() < 0.5 and "siergras0" or "siergras1")
				if plant(naam, h.Position, naam == "bloem_geel" and U(1.6, 2.2) or U(1.8, 2.6)) then nriet += 1 end
			end
		end
		k += U(1.2, 2.6)
	end
end
wf.Parent = workspace
return string.format("kroos %d, rimpels %d, riet/lissen %d", nk, nr, nriet)
