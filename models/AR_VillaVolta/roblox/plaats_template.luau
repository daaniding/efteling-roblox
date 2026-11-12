-- Villa Volta plaatsen (gegenereerd door maak_plaatsscript.py). Blender-oorsprong = midden gevel, voetlijn.
-- OSM-kalibratie: oorsprong op OSM (121.97, 335.09) m -> studs (365.9, -1005.3); gevel kijkt zuid-zuidwest (169.5 graden); grond Y=2.
local VILLA, OMGEVING = __VILLA__, __OMG__
local ORIGIN = CFrame.new(365.9, 1.95, -1005.3) * CFrame.Angles(0, math.rad(169.5), 0)
local S = 3
local COLL = __COLL__
local LAMPS = __LAMPS__
local HUIDEN = __HUIDEN__
local INGANG = __INGANG__
local BORD = __BORD__
local function mat(n) local ok,e=pcall(function() return Enum.Material[n] end); return ok and e or Enum.Material.SmoothPlastic end
local M = {
 stuc={Color3.fromRGB(226,210,172),"Plaster"}, steen={Color3.fromRGB(204,196,173),"Limestone"}, wit={Color3.fromRGB(232,229,218),"SmoothPlastic"},
 lei={Color3.fromRGB(62,64,72),"Slate"}, zink={Color3.fromRGB(120,127,133),"Metal"}, groen={Color3.fromRGB(20,64,42),"SmoothPlastic"},
 glas={Color3.fromRGB(16,20,26),"Glass"}, kozijn={Color3.fromRGB(237,237,230),"SmoothPlastic"}, letter={Color3.fromRGB(26,41,33),"Metal"},
 haag={Color3.fromRGB(34,64,28),"LeafyGrass"}, beuk={Color3.fromRGB(40,78,32),"LeafyGrass"}, buxus={Color3.fromRGB(42,86,34),"LeafyGrass"},
 grind={Color3.fromRGB(196,182,152),"Pebble"}, klinker={Color3.fromRGB(150,124,104),"Cobblestone"}, klinkerrood={Color3.fromRGB(104,58,46),"Brick"},
 ijzer={Color3.fromRGB(18,36,26),"Metal"}, rijhek={Color3.fromRGB(62,72,64),"Metal"}, rvs={Color3.fromRGB(190,192,194),"Metal"},
 plafond={Color3.fromRGB(238,236,228),"SmoothPlastic"}, hout={Color3.fromRGB(72,46,28),"Wood"}, huid={Color3.fromRGB(222,206,172),"Fabric"},
 perkament={Color3.fromRGB(226,206,156),"Fabric"},
 bloem_rood={Color3.fromRGB(190,25,30),"SmoothPlastic"}, bloem_wit={Color3.fromRGB(235,232,220),"SmoothPlastic"}, bloem_paars={Color3.fromRGB(110,45,150),"SmoothPlastic"},
 aarde={Color3.fromRGB(70,48,32),"Ground"}, oranje={Color3.fromRGB(222,110,28),"SmoothPlastic"}, lamp={Color3.fromRGB(255,232,190),"Neon"}, bord={Color3.fromRGB(14,48,32),"SmoothPlastic"}, goud={Color3.fromRGB(200,160,72),"Metal"},
}
local unknown = {}
local function laad(id, naam)
  local old = workspace:FindFirstChild(naam); if old then old:Destroy() end
  local m = Instance.new("Model"); m.Name = naam
  for _,o in ipairs(game:GetObjects("rbxassetid://"..id)) do o.Parent = m end
  for _,d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Parent = m end end
  for _,d in ipairs(m:GetChildren()) do if not d:IsA("BasePart") then d:Destroy() end end
  m.Parent = workspace; m:ScaleTo(S)
  local anker
  for _,p in ipairs(m:GetChildren()) do if string.find(p.Name,"MAT_anker") then anker = p end end
  assert(anker, "geen anker in "..naam)
  local told = CFrame.new(anker.Position + Vector3.new(0, 2*S, 0))   -- Blender (x,y,z) komt binnen als (-x,z,y)*S, anker op z=-2
  m:PivotTo(ORIGIN * told:Inverse() * m:GetPivot())
  anker:Destroy()
  for _,p in ipairs(m:GetChildren()) do
    p.Anchored = true; p.CanCollide = false; p.CanTouch = false
    local key = string.match(p.Name, "MAT_([%a_]+)_%d+$")
    local s = key and M[key]
    if s then p.Color = s[1]; p.Material = mat(s[2]) else table.insert(unknown, p.Name) end
    if key == "glas" then p.Reflectance = 0.25 end
    p.CastShadow = not (key == "glas" or key == "lamp" or key == "grind" or key == "klinker" or key == "klinkerrood" or key == "aarde" or key == "plafond")
  end
  return m
end
local function lokaal(x, y, z) return ORIGIN * CFrame.new(-x*S, z*S, y*S) end
local villa = laad(VILLA, "VillaVolta")
local omg = laad(OMGEVING, "VillaVoltaOmgeving")
local f = Instance.new("Folder"); f.Name = "Botsing"; f.Parent = omg
for _,c in ipairs(COLL) do
  local p = Instance.new("Part"); p.Anchored = true; p.Transparency = 1; p.CanCollide = true; p.CastShadow = false
  p.Size = Vector3.new(c[4]*S, c[6]*S, c[5]*S); p.CFrame = lokaal(c[1], c[2], c[3]) * CFrame.Angles(0, math.rad(c[7]), 0)
  p.Name = "Botsing"; p.Parent = f
end
local lf = Instance.new("Folder"); lf.Name = "Lampen"; lf.Parent = omg
for _,l in ipairs(LAMPS) do
  local p = Instance.new("Part"); p.Anchored = true; p.Transparency = 1; p.CanCollide = false; p.CanQuery = false; p.Size = Vector3.new(0.2,0.2,0.2)
  p.CFrame = lokaal(l[1], l[2], l[3]); p.Name = "Lamp"; p.Parent = lf
  local pl = Instance.new("PointLight"); pl.Range = 14; pl.Brightness = 1; pl.Color = Color3.fromRGB(255,222,170); pl.Shadows = false; pl.Parent = p
end
local function tekst(cf, size, faces, regels, kleur, font, bg)
  local p = Instance.new("Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.Transparency = 1; p.Size = size; p.CFrame = cf; p.Name = "Tekst"; p.Parent = omg
  for _,fc in ipairs(faces) do
    local g = Instance.new("SurfaceGui"); g.Face = fc; g.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud; g.PixelsPerStud = 50; g.LightInfluence = 0.4; g.Parent = p
    if bg then local fr = Instance.new("Frame"); fr.Size = UDim2.fromScale(1,1); fr.BackgroundColor3 = bg[1]; fr.BorderSizePixel = 0; fr.Parent = g
      local st = Instance.new("UIStroke"); st.Color = bg[2]; st.Thickness = 6; st.ApplyStrokeMode = Enum.ApplyStrokeMode.Border; st.Parent = fr; g = fr end
    local lay = Instance.new("UIListLayout"); lay.VerticalAlignment = Enum.VerticalAlignment.Center; lay.HorizontalAlignment = Enum.HorizontalAlignment.Center; lay.Parent = g
    for i,r in ipairs(regels) do
      local t = Instance.new("TextLabel"); t.BackgroundTransparency = 1; t.Size = UDim2.fromScale(0.9, r[2]); t.Text = r[1]; t.TextScaled = true
      t.Font = font; t.TextColor3 = kleur; t.LayoutOrder = i; t.Name = r[3] or ("Regel"..i); t.Parent = g
    end
  end
  return p
end
-- wacht- en showtijdenbord op het plein
local b = BORD[1]
tekst(lokaal(b[1], b[2], 2.25), Vector3.new(0.3*S+0.06, 1.85*S, 3.0*S), {Enum.NormalId.Left, Enum.NormalId.Right},
  {{"Villa Volta",0.36},{"Wachttijd",0.2},{"15 min",0.3,"Wachttijd"}}, Color3.fromRGB(226,190,96), Enum.Font.Fantasy)
-- INGANG-bordje (wit met blauwe rand) aan het hek bij het begin van de meandering
local ig = INGANG[1]
local bordje = tekst(lokaal(ig[1], ig[2], ig[3]), Vector3.new(0.55*S, 0.16*S, 0.06), {Enum.NormalId.Front, Enum.NormalId.Back},
  {{"INGANG",0.8}}, Color3.fromRGB(28,52,120), Enum.Font.GothamBold, {Color3.fromRGB(246,246,242), Color3.fromRGB(28,52,120)})
bordje.Transparency = 0; bordje.Color = Color3.fromRGB(246,246,242); bordje.Material = Enum.Material.SmoothPlastic
-- teksten op de vier bokkenhuiden (eigen korte samenvatting, vier talen)
local TALEN = {
 {"Hugo van den Loonsche Duynen","Roofridder en bokkenrijder. Zijn villa werd vervloekt: alleen wie zonder zonden is, kan de ban breken."},
 {"Hugo van den Loonsche Duynen","Robber knight and goat rider. His villa was cursed: only one without sin can break the spell."},
 {"Hugo van den Loonsche Duynen","Raubritter und Bockreiter. Seine Villa wurde verflucht: nur wer ohne Sünde ist, kann den Bann brechen."},
 {"Hugo van den Loonsche Duynen","Chevalier brigand. Sa villa fut maudite : seul celui qui est sans péché peut briser le sort."},
}
for k,h in ipairs(HUIDEN) do
  local cf = lokaal(h[1], h[2], h[3]) * CFrame.Angles(0, math.rad(90), 0)   -- voorkant naar de gang (Blender +x)
  tekst(cf, Vector3.new(0.62*S, 0.75*S, 0.05), {Enum.NormalId.Front}, {{TALEN[k][1],0.2},{TALEN[k][2],0.6}}, Color3.fromRGB(60,36,22), Enum.Font.Fantasy)
end
-- spawn op het plein, kijkend naar de villa
local sp = workspace:FindFirstChild("SpawnLocation")
if sp then local c = lokaal(4, -36, 0); local pos = c.Position + Vector3.new(0, sp.Size.Y/2 + 0.05, 0)
  sp.CFrame = CFrame.lookAt(pos, pos + c:VectorToWorldSpace(Vector3.new(0,0,1))) end
return "villa "..#villa:GetChildren().." | omgeving "..#omg:GetChildren().." | botsing "..#COLL.." | lampen "..#LAMPS.." | onbekend: "..table.concat(unknown, ",")
