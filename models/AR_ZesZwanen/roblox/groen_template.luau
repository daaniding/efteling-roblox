-- De Zes Zwanen: bos, ondergroei, asters en varens (gegenereerd door roblox/maak_groen.py). Kloont bestaande planten-sjablonen.
local F = Vector3.new(0.1076, 0, 0.9942)
local ORIGIN = CFrame.new(-108.77, 2.0, -301.0) * CFrame.Angles(0, math.atan2(-F.X, -F.Z), 0)
local S = 3
local function bron(naam)
	local b = game.ServerStorage:FindFirstChild("BomenBronV3"); local t = b and b:FindFirstChild(naam)
	if not t then for _, f in ipairs({game.ServerStorage:FindFirstChild("VVEchtePlanten"), game.ServerStorage:FindFirstChild("VVPlanten"), workspace:FindFirstChild("HerautenpleinGroen"), workspace:FindFirstChild("HansEnGrietjeGroen")}) do
		if f and f:FindFirstChild(naam) then t = f:FindFirstChild(naam); break end end end
	return t
end
local oud = workspace:FindFirstChild("ZesZwanenGroen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "ZesZwanenGroen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include
rp.FilterDescendantsInstances = {workspace.Terrain, workspace:FindFirstChild("ZesZwanenOmgeving")}
local n, mis = 0, {}
for i, p in ipairs(@PLANTEN@) do
	local t = bron(p[1])
	if not t then mis[p[1]] = true; continue end
	local c = t:Clone()
	local pos = (ORIGIN * CFrame.new(-p[2] * S, 0, p[3] * S)).Position
	local hit = workspace:Raycast(pos + Vector3.new(0, 20, 0), Vector3.new(0, -40, 0), rp)
	local y = hit and hit.Position.Y or 2
	if c:IsA("Model") then
		if p[5] ~= 1 then c:ScaleTo(c:GetScale() * p[5]) end
		local cf, sz = c:GetBoundingBox()
		local onder = cf.Position.Y - sz.Y / 2
		c:PivotTo(CFrame.new(pos.X, y + (c:GetPivot().Position.Y - onder), pos.Z) * CFrame.Angles(0, math.rad(p[4]), 0))
	elseif c:IsA("BasePart") then
		c.Size = c.Size * p[5]
		c.CFrame = CFrame.new(pos.X, y + c.Size.Y / 2, pos.Z) * CFrame.Angles(0, math.rad(p[4]), 0)
	end
	c.Parent = map; n += 1
	if i % 150 == 0 then task.wait() end
end
map.Parent = workspace
local m = {}; for k in pairs(mis) do table.insert(m, k) end
return string.format("%d planten geplaatst; ontbrekende sjablonen: %s", n, table.concat(m, ","))
