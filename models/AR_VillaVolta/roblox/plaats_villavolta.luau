-- Villa Volta plaatsen (gegenereerd door maak_plaatsscript.py). Blender-oorsprong = midden gevel, voetlijn.
-- OSM-kalibratie: oorsprong op OSM (121.97, 335.09) m -> studs (365.9, -1005.3); gevel kijkt zuid-zuidwest (169.5 graden); grond Y=2.
local VILLA, OMGEVING = 136382357585295, 109507507043736
local ORIGIN = CFrame.new(365.9, 1.95, -1005.3) * CFrame.Angles(0, math.rad(169.5), 0)
local S = 3
local COLL = {{0,-0.925,0.4,17.2,8.15,0.8,0},{0,-5.7,0.1,16.7,1.4,0.2,0},{0,-5.525,0.2,14.3,1.05,0.4,0},{0,-5.35,0.3,11.9,0.7,0.6,0},{0,-5.175,0.4,9.5,0.35,0.8,0},{0,2.75,4.7,7.8,5.5,7.8,0},{0,10.825,3.85,13.5,15.35,7.7,0},{-1.075,24.85,3.1,15.85,12.7,6.2,0},{-6.2,-0.4,1.2,4.6,0.35,0.8,0},{-8.2,1.3,1.2,0.35,3.7,0.8,0},{-3.65,-1.4,3,0.6,0.6,4.4,0},{-1.75,-0.1,2.3,0.55,0.4,3,0},{-2.45,-1,1.7,0.45,0.45,1.8,0},{6.2,-0.4,1.2,4.6,0.35,0.8,0},{8.2,1.3,1.2,0.35,3.7,0.8,0},{3.65,-1.4,3,0.6,0.6,4.4,0},{1.75,-0.1,2.3,0.55,0.4,3,0},{2.45,-1,1.7,0.45,0.45,1.8,0},{-3.92,-26.65,0.55,2.375,0.7,1.1,176.035},{-5.975,-26.32,0.55,2.504,0.7,1.1,166.028},{-7.78,-25.53,0.55,2.203,0.7,1.1,145.109},{-9.215,-24.415,0.55,2.136,0.7,1.1,139.086},{-10.45,-23.255,0.55,1.955,0.7,1.1,134.243},{-11.465,-22.015,0.55,1.962,0.7,1.1,124.38},{-12.32,-19.805,0.55,3.542,0.7,1.1,104.515},{-12.88,-16.68,0.55,3.526,0.7,1.1,95.782},{-12.95,-13.52,0.55,3.515,0.7,1.1,86.74},{-12.86,-10.37,0.55,3.49,0.7,1.1,90},{11.445,-8.77,0.55,4.06,0.7,1.1,-80.538},{11.86,-11.78,0.55,2.72,0.7,1.1,-84.674},{11.975,-14.005,0.55,2.44,0.7,1.1,-89.726},{11.775,-16.425,0.55,3.13,0.7,1.1,-98.48},{11.185,-19.07,0.55,3.004,0.7,1.1,-106.865},{10.135,-21.23,0.55,2.572,0.7,1.1,-126.767},{8.655,-22.91,0.55,2.62,0.7,1.1,-135.892},{7.155,-24.215,0.55,2.064,0.7,1.1,-143.063},{5.635,-25.145,0.55,2.215,0.7,1.1,-153.572},{3.23,-25.885,0.55,3.557,0.7,1.1,-168.305},{4.145,-12.385,0.25,2.119,0.35,0.5,-83.204},{4.385,-14.145,0.25,1.785,0.35,0.5,-81.064},{4.675,-15.71,0.25,1.75,0.35,0.5,-77.905},{5.11,-17.325,0.25,1.949,0.35,0.5,-72.28},{5.545,-18.55,0.25,1.004,0.35,0.5,-66.529},{6.02,-18.67,0.25,0.984,0.35,0.5,39.987},{6.705,-17.895,0.25,1.449,0.35,0.5,53.94},{7.345,-16.81,0.25,1.432,0.35,0.5,65.066},{7.725,-15.59,0.25,1.495,0.35,0.5,79.967},{7.89,-14.05,0.25,1.958,0.35,0.5,86.785},{7.85,-12.64,0.25,1.23,0.35,0.5,99.819},{7.61,-11.55,0.25,1.354,0.35,0.5,104.744},{7.19,-10.315,0.25,1.61,0.35,0.5,112.098},{6.565,-9.075,0.25,1.527,0.35,0.5,121.691},{6.01,-8.965,0.25,1.187,0.35,0.5,-113.273},{5.65,-9.785,0.25,0.954,0.35,0.5,-114.261},{5.26,-10.455,0.25,0.955,0.35,0.5,-126.135},{4.53,-11.095,0.25,1.368,0.35,0.5,-146.976},{-6.47,-8.71,0.25,1.286,0.35,0.5,-66.666},{-5.965,-9.605,0.25,1.133,0.35,0.5,-53.489},{-4.99,-10.62,0.25,2.044,0.35,0.5,-42.397},{-3.94,-11.47,0.25,1.019,0.35,0.5,-31.43},{-3.72,-12.28,0.25,1.388,0.35,0.5,-103.349},{-4.07,-13.495,0.25,1.494,0.35,0.5,-108.572},{-4.475,-14.635,0.25,1.276,0.35,0.5,-110.739},{-4.965,-15.705,0.25,1.432,0.35,0.5,-117.992},{-5.6,-16.805,0.25,1.46,0.35,0.5,-121.958},{-6.415,-17.87,0.25,1.584,0.35,0.5,-132.41},{-7.17,-17.795,0.25,1.49,0.35,0.5,115.201},{-7.685,-16.555,0.25,1.548,0.35,0.5,110.019},{-8.04,-15.45,0.25,1.126,0.35,0.5,104.621},{-8.215,-14.49,0.25,1.181,0.35,0.5,96.277},{-8.29,-13.44,0.25,1.276,0.35,0.5,92.083},{-8.3,-12.345,0.25,1.265,0.35,0.5,88.949},{-8,-10.845,0.25,2.171,0.35,0.5,73.108},{-7.2,-9.045,0.25,2.149,0.35,0.5,58.887},{-1.97,-12.54,0.25,1.143,0.35,0.5,-18.06},{-1.135,-12.73,0.25,0.929,0.35,0.5,-6.089},{-0.33,-12.74,0.25,1.037,0.35,0.5,3.991},{0.525,-12.655,0.25,1.032,0.35,0.5,7.374},{1.46,-12.485,0.25,1.221,0.35,0.5,12.707},{2.475,-12.135,0.25,1.289,0.35,0.5,24.955},{2.98,-12.405,0.25,1.185,0.35,0.5,-90},{3.015,-13.465,0.25,1.287,0.35,0.5,-86.392},{3.125,-14.605,0.25,1.355,0.35,0.5,-82.694},{3.3,-15.89,0.25,1.589,0.35,0.5,-81.87},{3.585,-17.28,0.25,1.604,0.35,0.5,-74.991},{-7.685,-16.555,0.25,1.548,0.35,0.5,-69.981},{-7.17,-17.795,0.25,1.49,0.35,0.5,-64.799},{-6.365,-18.915,0.25,1.66,0.35,0.5,-45},{-5.145,-19.885,0.25,1.826,0.35,0.5,-32.631},{-3.73,-20.65,0.25,1.751,0.35,0.5,-23.962},{-2.23,-21.125,0.25,1.766,0.35,0.5,-11.239},{-0.665,-21.325,0.25,1.748,0.35,0.5,-3.281},{0.85,-21.295,0.25,1.643,0.35,0.5,5.866},{2.285,-21.03,0.25,1.635,0.35,0.5,15.083},{3.48,-20.555,0.25,1.309,0.35,0.5,30.184},{4.375,-19.96,0.25,1.195,0.35,0.5,37.432},{-2.91,-26.72,1.8,1.15,1.15,3.6,0},{1.66,-26.21,1.8,1.15,1.15,3.6,0},{0,-17,1,0.5,0.5,2,0},{-2.6,-8.9,0.9,0.6,0.6,1.8,0},{2.6,-8.9,0.9,0.6,0.6,1.8,0},{-9.9,-6.2,1.2,0.4,0.4,2.4,0},{9.6,-6.2,1.2,0.4,0.4,2.4,0},{-11.9,-13,1.2,0.4,0.4,2.4,0},{10.6,-14,1.2,0.4,0.4,2.4,0},{18.6,-50.2,1.75,2.3,3.9,3.5,0},{12,5.775,0.45,6.275,0.25,0.9,90},{14.2,5.775,0.45,6.275,0.25,0.9,90},{6.93,19.775,1.95,22,0.3,3.9,-90},{11.365,30.7,1.95,9.02,0.3,3.9,180},{9.465,8.85,0.5,5.22,0.3,1,0},{15,8.85,0.5,1.75,0.3,1,0},{15.8,18.525,0.5,19.5,0.3,1,90},{7.08,8.85,1.95,0.3,0.3,3.9,0},{9.5,8.85,1.95,0.3,0.3,3.9,0},{12,8.85,1.95,0.3,0.3,3.9,0},{14.2,8.85,1.95,0.3,0.3,3.9,0},{15.8,8.85,1.95,0.3,0.3,3.9,0},{15.8,11.6,1.95,0.3,0.3,3.9,0},{15.8,14.35,1.95,0.3,0.3,3.9,0},{15.8,17.1,1.95,0.3,0.3,3.9,0},{15.8,19.85,1.95,0.3,0.3,3.9,0},{15.8,22.6,1.95,0.3,0.3,3.9,0},{15.8,25.35,1.95,0.3,0.3,3.9,0},{15.8,28.1,1.95,0.3,0.3,3.9,0},{15.8,30.7,1.95,0.3,0.3,3.9,0},{11.34,10.6,0.6,5.32,0.12,1,0},{9.74,12.2,0.6,5.32,0.12,1,0},{11.34,13.8,0.6,5.32,0.12,1,0},{9.74,15.4,0.6,5.32,0.12,1,0},{11.34,17,0.6,5.32,0.12,1,0},{9.74,18.6,0.6,5.32,0.12,1,0},{11.34,20.2,0.6,5.32,0.12,1,0},{9.74,21.8,0.6,5.32,0.12,1,0},{11.34,23.4,0.6,5.32,0.12,1,0},{14,13.4,0.6,6.4,0.12,1,90},{14,20.7,0.6,5.8,0.12,1,90},{9.74,25,0.6,5.32,0.12,1,0},{13.1,27.1,0.6,5,0.12,1,0},{15.3,30.2,0.6,0.6,0.6,1.1,0},{15.2,7.65,0.6,0.6,0.6,1.1,0},{10.5,7.85,0.6,0.6,0.6,1.1,0},{9.13,25.5,0.6,0.9,0.22,1,0},{9.13,26.05,0.6,0.9,0.22,1,0},{9.13,26.6,0.6,0.9,0.22,1,0},{16.75,2,0.7,2.894,0.6,1.4,27.553},{17.9,16.85,0.7,28.8,0.6,1.4,90},{17,31.1,0.7,2.1,0.6,1.4,180}}
local LAMPS = {{-2.91,-26.72,4.4},{1.66,-26.21,4.4},{-10.35,-6.2,2.55},{-9.45,-6.2,2.55},{-9.9,-6.2,2.65},{9.15,-6.2,2.55},{10.05,-6.2,2.55},{9.6,-6.2,2.65},{-12.35,-13,2.55},{-11.45,-13,2.55},{-11.9,-13,2.65},{10.15,-14,2.55},{11.05,-14,2.55},{10.6,-14,2.65},{11.37,10.2,3.55},{11.37,12.8,3.55},{11.37,15.4,3.55},{11.37,18,3.55},{11.37,20.6,3.55},{11.37,23.2,3.55},{11.37,25.8,3.55},{11.37,28.4,3.55}}
local HUIDEN = {{7.12,15.2,1.85},{7.12,16.15,1.85},{7.12,17.1,1.85},{7.12,18.05,1.85}}
local INGANG = {{13.1,10.55,0.75}}
local BORD = {{18.6,-50.2}}
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
