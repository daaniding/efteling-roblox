"""maak_bomenscript: roblox/bomen_pagode.luau uit exports/bomen.json. Bronmodellen (Creator Store, gecontroleerd: geen scripts):
ServerStorage.BoomBronnen.Dennen (Ponderosa Pine Pack 130515502281374, 12 varianten) en .Eiken (Realistic Oak Trees Pack
114023396228594, 3 varianten). Per boom: kloon, rechtop (bladkant omhoog), schalen naar hoogte, draaien, op het terrein zetten."""
import json, os
R = os.path.dirname(os.path.abspath(__file__)); D = os.path.dirname(R)
p = json.load(open(os.path.join(D, "exports", "bomen.json")))
lijst = "{" + ",".join("{%.2f,%.2f,%d,%.1f,%.2f}" % (x, y, 1 if s == "den" else 0, h, d) for x, y, s, h, d in p) + "}"
lua = '''-- bomen rond de Pagode (21_bomen.py -> exports/bomen.json; maak_bomenscript.py)
local S = 3
local BOMEN = %s
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
  local m = lijst[(i * 7) %% #lijst + 1]:Clone(); m.Name = (b[3] == 1 and "den" or "eik") .. i
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
  if i %% 10 == 0 then task.wait() end
end
map.Parent = workspace
return "bomen: " .. #map:GetChildren()
''' % lijst
open(os.path.join(R, "bomen_pagode.luau"), "w").write(lua)
print("bomen_pagode.luau", len(lua), "tekens,", len(p), "bomen")
