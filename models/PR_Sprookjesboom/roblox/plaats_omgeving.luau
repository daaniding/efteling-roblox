-- Omgeving van de Sprookjesboom plaatsen (na plaats_sprookjesboom.luau). In Studio (Edit) uitvoeren via de Assistant/MCP.
-- Data: exports/omgeving_data.png (asset DATA) = 06_omgeving_data.py via 07_data_png.py; meshes: OMG (plein, paden, band, geul,
-- water, wortels, bankjes, prullenbak), STEEN (6 keien). Planten uit ServerStorage.VVEchtePlanten en BomenBronV3 (Villa Volta).
-- Terrein: origineel vlak = voxels vol tot Y=0 (rendert op Y=2). Onder de geul (< 1.15 m van de beek) alleen vol tot Y=-4.
local DATA, OMG, STEEN = 91704590749799, 131889710342801, 90280289121540
local S = 3
local O = Vector3.new(121.44, 1.95, -594.57)                    -- stamhart (OSM 40.48, 198.19 m)
local ORIGIN = CFrame.new(O) * CFrame.Angles(0, math.pi, 0)
local function W(x, y) return Vector3.new(O.X + x * S, 0, O.Z - y * S) end

-- data inlezen: 2 pixels per record {soort, x, y, schaal, draai, groep}
local img = game:GetService("AssetService"):CreateEditableImageAsync(Content.fromAssetId(DATA))
local buf = img:ReadPixelsBuffer(Vector2.zero, img.Size)
local recs, poly = {}, {}
for i = 0, (img.Size.X * img.Size.Y) // 2 - 1 do
  local o = i * 8; local g = buffer.readu8(buf, o + 7); if g < 200 then break end
  local xi = buffer.readu8(buf, o + 1) * 256 + buffer.readu8(buf, o + 2); local yi = buffer.readu8(buf, o + 3) * 256 + buffer.readu8(buf, o + 4)
  local r = {buffer.readu8(buf, o), (xi - 40000) / 100, (yi - 40000) / 100, buffer.readu8(buf, o + 5) / 100, buffer.readu8(buf, o + 6) / 255 * 360, g - 200}
  table.insert(recs, r); if r[6] == 4 then table.insert(poly, Vector2.new(r[2], r[3])) end
end

-- 1. terrein onder de geul leeg
local function sdist(p)
  local inside, dmin = false, math.huge; local n = #poly
  for i = 1, n do
    local a, b = poly[i], poly[i % n + 1]
    if ((a.Y > p.Y) ~= (b.Y > p.Y)) and (p.X < (b.X - a.X) * (p.Y - a.Y) / (b.Y - a.Y) + a.X) then inside = not inside end
    local ab = b - a; local L = ab:Dot(ab); local t = L > 0 and math.clamp((p - a):Dot(ab) / L, 0, 1) or 0
    dmin = math.min(dmin, (a + ab * t - p).Magnitude)
  end
  return inside and -dmin or dmin
end
local xmin, xmax, ymin, ymax = math.huge, -math.huge, math.huge, -math.huge
for _, p in ipairs(poly) do xmin = math.min(xmin, p.X); xmax = math.max(xmax, p.X); ymin = math.min(ymin, p.Y); ymax = math.max(ymax, p.Y) end
local T = workspace.Terrain
local reg = Region3.new(Vector3.new(O.X + (xmin - 3) * S, -12, O.Z - (ymax + 3) * S), Vector3.new(O.X + (xmax + 3) * S, 8, O.Z - (ymin - 3) * S)):ExpandToGrid(4)
local mats, occs = T:ReadVoxels(reg, 4)
local sz = mats.Size; local lo = reg.CFrame.Position - reg.Size / 2
for i = 1, sz.X do for k = 1, sz.Z do
  local d = sdist(Vector2.new((lo.X + (i - 0.5) * 4 - O.X) / S, -(lo.Z + (k - 0.5) * 4 - O.Z) / S))
  if d < 1.15 then
    for j = 1, sz.Y do
      local full = lo.Y + (j - 1) * 4 < -4
      mats[i][j][k] = full and Enum.Material.Mud or Enum.Material.Air; occs[i][j][k] = full and 1 or 0
    end
  end
end end
T:WriteVoxels(reg, 4, mats, occs)
task.wait(2)                                                      -- terreinbotsing wordt pas later bijgewerkt

-- 2. meshes
local function laad(id, naam)
  local m = Instance.new("Model"); m.Name = naam
  for _, o in ipairs(game:GetObjects("rbxassetid://" .. id)) do o.Parent = m end
  for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
  for _, d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
  m:ScaleTo(S)
  local anker; for _, p in ipairs(m:GetChildren()) do if string.find(p.Name, "anker") then anker = p end end
  m:PivotTo(CFrame.new(anker.Position + Vector3.new(0, 2 * S, 0)):Inverse() * m:GetPivot()); anker:Destroy()
  for _, p in ipairs(m:GetChildren()) do p.Anchored = true; p.CanTouch = false end
  m.WorldPivot = CFrame.new(); return m
end
for _, n in ipairs({"SprookjesboomOmgeving", "SprookjesboomStenen", "SprookjesboomPlanten"}) do local o = workspace:FindFirstChild(n); if o then o:Destroy() end end
local om = laad(OMG, "SprookjesboomOmgeving")
-- klinker: rode klinkers (Sprookjesboomopening.jpg); water: troebel olijfbruin (Boom_wortels.jpg)
local ST = {klinker = {Color3.fromRGB(150, 88, 68), Enum.Material.Pavement, true}, band = {Color3.fromRGB(118, 116, 110), Enum.Material.Concrete, true},
  branch = {Color3.fromRGB(118, 110, 98), Enum.Material.Wood, true}, hout = {Color3.fromRGB(92, 64, 42), Enum.Material.Wood, true},
  hout_kops = {Color3.fromRGB(128, 98, 68), Enum.Material.Wood, true}, riet = {Color3.fromRGB(160, 124, 74), Enum.Material.Wood, true},
  ijzer = {Color3.fromRGB(26, 28, 27), Enum.Material.Metal, true}, hollow_dark = {Color3.fromRGB(12, 10, 8), Enum.Material.SmoothPlastic, false},
  beekbodem = {Color3.fromRGB(58, 48, 38), Enum.Material.Mud, true}, oever = {Color3.fromRGB(96, 112, 64), Enum.Material.Grass, true},
  gras = {T:GetMaterialColor(Enum.Material.Grass), Enum.Material.Grass, true}, water = {Color3.fromRGB(66, 60, 38), Enum.Material.SmoothPlastic, false},
  zwam = {Color3.fromRGB(150, 118, 84), Enum.Material.Sand, true}, zwam_rand = {Color3.fromRGB(222, 206, 176), Enum.Material.Sand, false},
  lampglas = {Color3.fromRGB(240, 226, 176), Enum.Material.SmoothPlastic, false}}
for _, p in ipairs(om:GetChildren()) do
  local key = string.match(p.Name, "^(.-)_%d+$"); local s = key and ST[key]
  if s then p.Color = s[1]; p.Material = s[2]; p.CanCollide = s[3] end
  if key == "branch" then local sa = Instance.new("SurfaceAppearance"); sa.ColorMap = "rbxassetid://99288067092575"; sa.Parent = p end
  if key == "klinker" or key == "band" or key == "gras" or key == "beekbodem" or key == "oever" then p.CastShadow = false end
  if key == "water" then p.Transparency = 0.06; p.Reflectance = 0.10; p.CastShadow = false end   -- Glass spiegelde blauw
end
om:PivotTo(ORIGIN); om.Parent = workspace
local hit = {T}
for _, p in ipairs(om:GetChildren()) do local k = string.match(p.Name, "^(.-)_%d+$"); if k == "beekbodem" or k == "oever" or k == "gras" or k == "klinker" then table.insert(hit, p) end end
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = hit
local function grond(v) local r = workspace:Raycast(Vector3.new(v.X, 30, v.Z), Vector3.new(0, -60, 0), rp); return r and r.Position.Y or 2 end

-- 3. oeverstenen (groep 1) en keien (groep 2)
local proto = laad(STEEN, "Proto"); local P = {}
for _, p in ipairs(proto:GetChildren()) do local k = tonumber(string.match(p.Name, "steen(%d)")); if k then P[k] = p end end
local fs = Instance.new("Model"); fs.Name = "SprookjesboomStenen"
for _, r in ipairs(recs) do
  if r[6] == 1 or r[6] == 2 then
    local c = (P[r[1]] or P[0]):Clone(); local diam = r[4] * 2 * S
    c.Size = c.Size * (diam / 3)
    local v = W(r[2], r[3]); local gy = grond(v)
    c.CFrame = CFrame.new(v.X, gy - diam * 0.15, v.Z) * CFrame.Angles(math.rad(math.random(-12, 12)), math.rad(r[5]), math.rad(math.random(-12, 12))) * CFrame.new(0, c.Size.Y / 2, 0)
    local PC = {[0] = Color3.fromRGB(178, 181, 186), Color3.fromRGB(158, 163, 173), Color3.fromRGB(189, 186, 181), Color3.fromRGB(143, 148, 158), Color3.fromRGB(199, 199, 201), Color3.fromRGB(168, 168, 168)}
    c.Color = (PC[r[1]] or PC[0]):Lerp(Color3.fromRGB(96, 100, 106), math.random() * 0.35):Lerp(Color3.fromRGB(110, 112, 114), 0.25)     -- lichte blauwgrijze breuksteen, wisselend
    c.Material = Enum.Material.Rock; c.CanCollide = (r[6] == 2); c.CanTouch = false; c.CastShadow = c.Size.Magnitude >= 3; c.Parent = fs   -- kleine stenen geen schaduw (prestaties: +17 fps)
  end
end
fs.Parent = workspace; proto:Destroy(); task.wait()

-- 4. planten (groep 0): soort 0 rodo, 1 taxus, 2 struik, 3 varen, 4 brandnetel, 5 maagdenpalm, 6 zuring, 7 struikje, 8 gras
local SS = game:GetService("ServerStorage"); local VE = SS.VVEchtePlanten; local V3 = SS.BomenBronV3
local function pre(p, n) local t = {}; for i = 0, n do local c = VE:FindFirstChild(p .. i); if c then table.insert(t, c) end end; return t end
local SRC = {[0] = {V3.rododendron0, V3.rododendron1}, [1] = {V3.taxus0, V3.taxus1}, [2] = pre("PH_shrub_02_", 3), [3] = pre("PH_fern_02_", 3),
  [4] = pre("PH_nettle_plant_", 3), [5] = pre("PH_periwinkle_plant_", 5), [6] = pre("PH_shrub_sorrel_01_", 10),
  [7] = {VE.PH_shrub_03_0, VE.PH_shrub_03_1, VE.PH_shrub_03_2, VE.PH_shrub_03_3, VE.PH_shrub_04_0}, [8] = pre("PH_grass_bermuda_01_", 20)}
local fp = Instance.new("Model"); fp.Name = "SprookjesboomPlanten"; fp.Parent = workspace
local np, batch = 0, Instance.new("Folder")
for _, r in ipairs(recs) do
  if r[6] == 0 then
    local lst = SRC[r[1]]; local c = lst[math.random(1, #lst)]:Clone()
    local v = W(r[2], r[3]); local gy = grond(v)
    if c:IsA("Model") then
      c:ScaleTo(c:GetScale() * r[4])
      local cf, size = c:GetBoundingBox(); local off = c:GetPivot().Y - (cf.Y - size.Y / 2)
      c:PivotTo(CFrame.new(v.X, gy + off - 0.1, v.Z) * CFrame.Angles(0, math.rad(r[5]), 0))
      local laag = not (r[1] == 0 or r[1] == 1)          -- alleen rododendron/taxus werpen schaduw
      for _, d in ipairs(c:GetDescendants()) do if d:IsA("BasePart") then d.Anchored = true; d.CanCollide = false; d.CanTouch = false; if laag then d.CastShadow = false end end end
    else
      c.Size = c.Size * r[4]; c.Anchored = true; c.CanCollide = false; c.CanTouch = false; c.CastShadow = false
      c.CFrame = CFrame.new(v.X, gy + c.Size.Y / 2 - 0.08, v.Z) * CFrame.Angles(0, math.rad(r[5]), 0)
    end
    c.Parent = batch; np += 1
    if np % 400 == 0 then batch.Parent = fp; batch = Instance.new("Folder"); task.wait() end
  end
end
batch.Parent = fp

-- 5. horizonbomen (echte OSM-bomen) die op pad/plein/beek staan of door de Sprookjesboom groeien -> ServerStorage
local vrij = {}
for _, r in ipairs(recs) do if r[6] == 3 then table.insert(vrij, Vector2.new(r[2], r[3])) end end
local bak = SS:FindFirstChild("SprookjesboomWeggehaald") or Instance.new("Folder", SS); bak.Name = "SprookjesboomWeggehaald"
for _, m in ipairs(bak:GetChildren()) do m.Parent = workspace.VillaVoltaHorizon end   -- eerst alles terug, dan opnieuw beoordelen
for _, m in ipairs(workspace.VillaVoltaHorizon:GetChildren()) do
  local p = m:GetPivot().Position; local q = Vector2.new((p.X - O.X) / S, -(p.Z - O.Z) / S)
  if q.Magnitude < 45 then
    local big = not (string.find(m.Name, "struik") or string.find(m.Name, "rodo") or string.find(m.Name, "taxus"))
    local bad = (big and q.Magnitude < 8.0) or (not big and q.Magnitude < 3.2)
    if not bad then for _, f in ipairs(vrij) do if (f - q).Magnitude < 1.6 then bad = true; break end end end
    if bad then m.Parent = bak end
  end
end
-- 6. paddenstoeltjes op de grond, hoed roder (Sprookjesboomoverview.jpg)
for _, c in ipairs(workspace.SprookjesboomPaddenstoelen:GetChildren()) do
  local p = c:GetPivot(); local gy = grond(p.Position); c:PivotTo(p - Vector3.new(0, p.Y - gy + 0.05, 0))
  for _, d in ipairs(c:GetChildren()) do if string.match(d.Name, "^hoed_") then d.Color = Color3.fromRGB(204, 82, 70) end end
end
return ("omgeving %d delen, %d stenen, %d planten"):format(#om:GetChildren(), #fs:GetChildren(), np)
