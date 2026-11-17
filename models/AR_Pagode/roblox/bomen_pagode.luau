-- bomen rond de Pagode (21_bomen.py -> exports/bomen.json; maak_bomenscript.py)
local S = 3
local BOMEN = {{329.21,38.08,1,22.0,3.48},{383.87,46.78,0,19.5,1.56},{356.29,12.19,0,18.8,0.61},{378.18,68.14,0,18.5,3.26},{353.16,84.72,1,19.1,3.95},{340.57,32.18,1,20.2,0.32},{339.77,72.98,0,22.1,5.61},{375.94,38.23,0,21.3,1.20},{349.76,81.64,0,22.1,1.13},{385.71,33.17,0,19.9,2.49},{347.06,15.63,0,22.2,3.10},{353.75,79.25,0,21.0,1.23},{334.77,77.47,1,22.8,4.65},{386.48,22.78,0,20.0,4.73},{376.38,13.93,0,18.4,3.83},{335.19,64.76,0,17.2,5.70},{352.32,28.07,0,19.5,1.77},{376.12,59.77,0,19.1,1.41},{387.21,40.10,0,16.1,4.49},{361.94,67.20,0,20.5,4.56},{327.97,71.09,0,21.1,4.54},{392.39,28.62,0,21.9,5.01},{348.14,76.49,0,20.5,2.08},{380.25,26.92,0,16.5,0.84},{343.92,43.70,1,25.3,2.69},{323.17,36.36,1,20.0,5.20},{363.76,73.47,0,17.3,2.03},{372.73,25.35,1,19.7,4.48},{360.03,84.31,0,21.8,1.27},{375.19,30.38,0,20.6,6.16},{385.38,65.35,0,16.6,0.45},{377.46,44.97,0,22.3,1.34},{371.70,81.51,0,16.4,3.43},{371.36,69.38,0,21.1,1.41},{356.54,32.55,1,24.8,6.13},{345.32,32.73,1,24.1,1.51},{360.97,21.83,1,23.3,4.20},{345.37,25.29,1,25.0,2.45},{343.33,82.10,1,20.0,4.87},{365.45,86.99,0,16.8,1.82},{333.36,34.46,1,21.8,6.26},{355.34,22.09,1,23.0,5.60},{329.06,63.96,0,18.2,6.20},{366.53,21.76,0,17.0,5.09},{335.08,72.41,1,23.2,3.40},{327.10,33.86,1,21.0,3.50},{339.11,68.10,0,17.7,2.16},{370.29,85.92,0,22.7,4.33},{391.22,67.25,0,18.3,4.30},{363.16,16.21,0,21.9,1.59},{348.27,21.63,1,20.2,2.91},{368.42,11.44,0,16.1,4.96},{351.38,18.36,1,19.4,0.40},{357.89,71.73,0,16.2,3.77},{339.32,36.65,1,27.3,1.92},{364.15,79.84,0,22.6,2.64},{377.03,23.67,0,22.8,2.07},{338.60,79.85,1,21.8,4.07},{381.33,19.31,0,19.2,3.06},{377.59,53.22,0,22.0,1.10}}
local bron = game.ServerStorage:WaitForChild("BoomBronnen")
local DEN, EIK = {}, {}
for _, c in bron.Dennen:GetDescendants() do if c:IsA("Model") and c:FindFirstChildWhichIsA("MeshPart") then table.insert(DEN, c) end end
for _, c in bron.Eiken:GetDescendants() do if c:IsA("Model") and c:FindFirstChildWhichIsA("MeshPart") then table.insert(EIK, c) end end
local function rechtop(m)
  local cf, s = m:GetBoundingBox()
  local as = (s.Z >= s.X and s.Z >= s.Y) and cf.LookVector or ((s.Y >= s.X) and cf.UpVector or cf.RightVector)
  local blad, nb = Vector3.zero, 0
  for _, q in m:GetDescendants() do
    if q:IsA("MeshPart") then local sa = q:FindFirstChildOfClass("SurfaceAppearance"); if sa and sa.AlphaMode == Enum.AlphaMode.Transparency then blad += q.Position; nb += 1 end end
  end
  if nb > 0 and (blad / nb - cf.Position):Dot(as) < 0 then as = -as end
  m:PivotTo(CFrame.new(cf.Position) * CFrame.fromRotationBetweenVectors(as, Vector3.yAxis) * CFrame.new(-cf.Position) * m:GetPivot())
end
local oud = workspace:FindFirstChild("PagodeBomen"); if oud then oud:Destroy() end
local map = Instance.new("Folder"); map.Name = "PagodeBomen"
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
for i, b in ipairs(BOMEN) do
  local lijst = b[3] == 1 and DEN or EIK
  local m = lijst[(i * 7) % #lijst + 1]:Clone(); m.Name = (b[3] == 1 and "den" or "eik") .. i
  rechtop(m)
  local _, s = m:GetBoundingBox()
  m:ScaleTo(m:GetScale() * (b[4] * S) / math.max(s.X, s.Y, s.Z))
  local c = m:GetBoundingBox()
  m:PivotTo(CFrame.new(c.Position) * CFrame.Angles(0, b[5], 0) * CFrame.new(-c.Position) * m:GetPivot())
  local c2, s2 = m:GetBoundingBox()
  local x, z = b[1] * S, -b[2] * S
  local h = workspace:Raycast(Vector3.new(x, 80, z), Vector3.new(0, -160, 0), rp)
  local grond = (h and h.Position.Y or 0.5) - 0.6
  m:PivotTo(m:GetPivot() + Vector3.new(x - c2.Position.X, grond - (c2.Position.Y - s2.Y / 2), z - c2.Position.Z))
  for _, q in m:GetDescendants() do
    if q:IsA("BasePart") then q.Anchored = true; q.CanCollide = false; q.CanTouch = false; q.CanQuery = false; q.CastShadow = true end
  end
  m.Parent = map
  if i % 10 == 0 then task.wait() end
end
map.Parent = workspace
return "bomen: " .. #map:GetChildren()
