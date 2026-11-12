-- Extra's bij de Sprookjesboom (na plaats_sprookjesboom.luau en plaats_omgeving.luau).
-- EXTRA = build/08_extra.py (weerstation + rododendron-bloemtros; de zelfgemaakte dieren daarin worden NIET gebruikt).
-- Dieren = Roblox AI-meshes (generate_mesh, getextureerd): eekhoorn, konijn, specht (Eftepedia: "rode eekhoorn, wild konijn, grote bonte specht").
-- Showlamp op het gezicht (de kruin zet het gezicht anders in de schaduw), licht in de 2 lantaarns. Layout-labels van gebouwde dingen weg (Daan).
local EXTRA = 109536072791154
local DIER = {Eekhoorn = {138758101831485, 1.3}, Konijn = {76196046627133, 1.1}, Specht = {71184715344811, 1.3}}
local S = 3
local O = Vector3.new(121.44, 1.95, -594.57)
local ORIGIN = CFrame.new(O) * CFrame.Angles(0, math.pi, 0)
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x * S, z * S, y * S) end
local old = workspace:FindFirstChild("SprookjesboomExtra"); if old then old:Destroy() end
local ex = Instance.new("Model"); ex.Name = "SprookjesboomExtra"; ex.Parent = workspace

local m = Instance.new("Model")
for _, o in ipairs(game:GetObjects("rbxassetid://" .. EXTRA)) do o.Parent = m end
for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
m:ScaleTo(S)
local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
m:PivotTo(CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
local KL = {weer_metaal = {Color3.fromRGB(140, 145, 148), Enum.Material.Metal}, weer_wit = {Color3.fromRGB(230, 230, 224), Enum.Material.SmoothPlastic},
  weer_groen = {Color3.fromRGB(38, 66, 46), Enum.Material.Metal}, tros_lila = {Color3.fromRGB(176, 112, 196), Enum.Material.SmoothPlastic}, tros_hart = {Color3.fromRGB(110, 46, 104), Enum.Material.SmoothPlastic}}
local function groep(prefix, naam)
  local g = Instance.new("Model"); g.Name = naam
  for _, p in ipairs(m:GetChildren()) do
    if string.sub(p.Name, 1, #prefix) == prefix then
      local k = string.match(p.Name, "^(.-)_%d+$"); if KL[k] then p.Color = KL[k][1]; p.Material = KL[k][2] end
      p.Parent = g; p.Anchored = true; p.CanTouch = false
    end
  end
  g.WorldPivot = CFrame.new(); return g
end
local weer = groep("weer", "Weerstation"); local tros = groep("tros", "Bloemtros"); m:Destroy()
weer:PivotTo(lokaal(2.3, 4.0, 0) * CFrame.Angles(0, math.rad(25), 0)); weer.Parent = ex

-- bloemtrossen op de rododendrons (straal naar willekeurige punten in de struik)
local fb = Instance.new("Folder"); fb.Name = "Rododendronbloemen"; fb.Parent = ex
for _, f in ipairs(workspace.SprookjesboomPlanten:GetDescendants()) do
  if f:IsA("Model") and string.find(f.Name, "rododendron") then
    local cf, size = f:GetBoundingBox()
    local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {f}
    local got, tries = 0, 0
    while got < 30 and tries < 200 do
      tries += 1
      local tgt = cf.Position + Vector3.new((math.random() - 0.5) * size.X * 0.7, (math.random() - 0.2) * size.Y * 0.6, (math.random() - 0.5) * size.Z * 0.7)
      local a = math.random() * math.pi * 2; local el = math.rad(math.random(-5, 65))
      local from = tgt + Vector3.new(math.cos(a) * math.cos(el), math.sin(el), math.sin(a) * math.cos(el)) * size.Magnitude
      local r = workspace:Raycast(from, (tgt - from) * 1.2, rp)
      if r then
        local c = tros:Clone(); c:ScaleTo(math.random(85, 125) / 100)
        c:PivotTo(CFrame.lookAt(r.Position, r.Position + r.Normal) * CFrame.Angles(math.rad(-90), 0, math.rad(math.random(0, 360))) * CFrame.new(0, -0.05, 0))
        for _, p in ipairs(c:GetChildren()) do p.CanCollide = false; p.CastShadow = false end
        c.Parent = fb; got += 1
      end
    end
  end
end
tros:Destroy()

-- licht
local lp = Instance.new("Part"); lp.Name = "Gezichtslamp"; lp.Anchored = true; lp.CanCollide = false; lp.CanQuery = false; lp.Transparency = 1; lp.Size = Vector3.new(0.3, 0.3, 0.3)
lp.CFrame = CFrame.lookAt(lokaal(0.9, -3.4, 0.25).Position, lokaal(0, -0.9, 2.15).Position); lp.Parent = ex
local sl = Instance.new("SpotLight"); sl.Face = Enum.NormalId.Front; sl.Angle = 38; sl.Range = 24; sl.Brightness = 1.6; sl.Color = Color3.fromRGB(255, 232, 200); sl.Shadows = true; sl.Parent = lp
for _, xy in ipairs({{-3.85, -11.85}, {5.11, -11.61}}) do
  local p = Instance.new("Part"); p.Name = "LantaarnLicht"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.Transparency = 1; p.Size = Vector3.new(0.2, 0.2, 0.2)
  p.CFrame = lokaal(xy[1], xy[2], 2.74); p.Parent = ex
  local pl = Instance.new("PointLight"); pl.Range = 14; pl.Brightness = 1; pl.Color = Color3.fromRGB(255, 222, 170); pl.Parent = p
end

-- dieren
local D = Instance.new("Model"); D.Name = "Dieren"; D.Parent = ex
local function dier(naam)
  local m2 = Instance.new("Model"); m2.Name = naam
  for _, o in ipairs(game:GetObjects("rbxassetid://" .. DIER[naam][1])) do o.Parent = m2 end
  m2:ScaleTo(m2:GetScale() * DIER[naam][2])
  for _, d in ipairs(m2:GetDescendants()) do if d:IsA("BasePart") then d.Anchored = true; d.CanCollide = false; d.CanTouch = false end end
  local cf, size = m2:GetBoundingBox(); m2.WorldPivot = CFrame.new(cf.Position - Vector3.new(0, size.Y / 2, 0)); m2.Parent = D; return m2
end
local hout = {}; for _, p in ipairs(workspace.Sprookjesboom:GetChildren()) do if not string.find(string.lower(p.Name), "leaf") then table.insert(hout, p) end end
local rpB = RaycastParams.new(); rpB.FilterType = Enum.RaycastFilterType.Include; rpB.FilterDescendantsInstances = hout
local gp = {workspace.Terrain}; for _, p in ipairs(workspace.SprookjesboomOmgeving:GetChildren()) do table.insert(gp, p) end
local rpG = RaycastParams.new(); rpG.FilterType = Enum.RaycastFilterType.Include; rpG.FilterDescendantsInstances = gp
local r = workspace:Raycast(lokaal(-1.75, -0.2, 5.2).Position, Vector3.new(0, -20, 0), rpB)                    -- linker lage tak
dier("Eekhoorn"):PivotTo(CFrame.new(r.Position) * CFrame.Angles(0, math.rad(200), 0))
local kp = lokaal(-2.2, -2.6, 0).Position; local g = workspace:Raycast(kp + Vector3.new(0, 20, 0), Vector3.new(0, -40, 0), rpG)  -- oever links voor
dier("Konijn"):PivotTo(CFrame.new(kp.X, g.Position.Y, kp.Z) * CFrame.Angles(0, math.rad(150), 0))
local az = math.rad(-31)                                                                                        -- uilengat
local buiten = lokaal(math.sin(az) * 3, -math.cos(az) * 3, 3.70).Position; local as = lokaal(0, 0, 3.70).Position
local h = workspace:Raycast(buiten, as - buiten, rpB); local flat = Vector3.new(h.Normal.X, 0, h.Normal.Z).Unit
dier("Specht"):PivotTo(CFrame.lookAt(h.Position + flat * 0.12, h.Position + flat * 0.12 + flat:Cross(Vector3.yAxis)))

-- zwevende layout-labels weg bij alles wat gebouwd is
for _, gui in ipairs(workspace.EftelingLayout:GetDescendants()) do
  if gui:IsA("BillboardGui") then
    local n = string.lower(gui.Parent.Name)
    for _, b in ipairs({"villa volta", "sprookjesboom", "muzikale paddenstoel", "holle bolle gijs", "hans en grietje"}) do
      if string.find(n, b, 1, true) then gui:Destroy(); break end
    end
  end
end
return "extra's geplaatst"
