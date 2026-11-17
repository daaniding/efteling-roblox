-- interieur gondel (Daan 17 nov: "kan de Pagode van binnen meer detail hebben"; video instappen + Pagode-binnenzijde):
-- witte zitrand rondom de kern, gouden randen om de plafondlampen, mintgroene bordjes met gouden lijst op de kernwand
-- (UITGANG bij de uitstappoortjes). Alles in Gondel.Interieur: beweegt mee (PagodeRitClient verplaatst alle gondeldelen).
do
  local gondel = workspace.Pagode.Gondel
  local K = gondel.Kern.CFrame
  local oudI = gondel:FindFirstChild("Interieur"); if oudI then oudI:Destroy() end
  local map = Instance.new("Folder"); map.Name = "Interieur"; map.Parent = gondel
  local DEK, R_KERN = 6.6, 16.2
  local function deel(naam, cf, size, kleur, mat, botst)
    local p = Instance.new("Part"); p.Name = naam; p.Anchored = true; p.CanCollide = botst; p.CanTouch = false; p.CanQuery = botst
    p.Size = size; p.Color = kleur; p.Material = mat; p.CFrame = cf; p.TopSurface = Enum.SurfaceType.Smooth; p.Parent = map; return p
  end
  -- 1 witte zitrand: 48 gebogen stukken, 1.5 studs diep, 1.35 hoog (0.45 m), met een smalle bovenrand
  local N = 48
  for i = 0, N - 1 do
    local t = (i + 0.5) / N * 2 * math.pi
    local r = R_KERN + 0.75
    local L = 2 * math.pi * r / N + 0.15
    local c = K * CFrame.new(r * math.cos(t), DEK + 0.675, r * math.sin(t)) * CFrame.Angles(0, -t, 0)
    deel("zitrand", c, Vector3.new(1.5, 1.35, L), Color3.fromRGB(236, 232, 222), Enum.Material.SmoothPlastic, true)
    deel("zitrandkap", K * CFrame.new((r + 0.1) * math.cos(t), DEK + 1.4, (r + 0.1) * math.sin(t)) * CFrame.Angles(0, -t, 0),
      Vector3.new(1.75, 0.12, L), Color3.fromRGB(246, 244, 238), Enum.Material.SmoothPlastic, false)
  end
  -- 2 gouden rand om elke plafondlamp
  for _, p in ipairs(gondel:GetDescendants()) do
    if p:IsA("BasePart") and p.Name == "plafondlamp" then
      local ring = deel("lamprand", p.CFrame * CFrame.new(0.03, 0, 0), Vector3.new(p.Size.X * 0.6, p.Size.Y + 0.5, p.Size.Z + 0.5),
        Color3.fromRGB(205, 160, 70), Enum.Material.Metal, false)
      ring.Shape = Enum.PartType.Cylinder; ring.Reflectance = 0.1
    end
  end
  -- 3 bordjes op de kernwand (mintgroen, gouden lijst); kernhoek = 180 - gondelhoek alfa
  local function bord(theta, regel1, regel2)
    local t = math.rad(theta)
    local r = R_KERN + 0.08
    local c = K * CFrame.new(r * math.cos(t), DEK + 6.2, r * math.sin(t)) * CFrame.Angles(0, -t - math.pi / 2, 0)
    deel("bordlijst", c, Vector3.new(4.6, 2.0, 0.12), Color3.fromRGB(205, 160, 70), Enum.Material.Metal, false)
    local b = deel("bord", c * CFrame.new(0, 0, -0.08), Vector3.new(4.2, 1.6, 0.08), Color3.fromRGB(150, 205, 180), Enum.Material.SmoothPlastic, false)
    local sg = Instance.new("SurfaceGui"); sg.Face = Enum.NormalId.Front; sg.CanvasSize = Vector2.new(420, 160); sg.LightInfluence = 0.6; sg.Parent = b
    local t1 = Instance.new("TextLabel"); t1.BackgroundTransparency = 1; t1.Size = UDim2.new(1, 0, 0.62, 0); t1.Font = Enum.Font.Bodoni
    t1.TextScaled = true; t1.TextColor3 = Color3.fromRGB(28, 70, 52); t1.Text = regel1; t1.AutoLocalize = false; t1.Parent = sg
    local t2 = Instance.new("TextLabel"); t2.BackgroundTransparency = 1; t2.Position = UDim2.new(0, 0, 0.62, 0); t2.Size = UDim2.new(1, 0, 0.3, 0)
    t2.Font = Enum.Font.Bodoni; t2.TextScaled = true; t2.TextColor3 = Color3.fromRGB(28, 70, 52); t2.Text = regel2; t2.AutoLocalize = false; t2.Parent = sg
  end
  bord(188, "UITGANG", "Exit · Ausgang · Sortie")        -- tussen uit0 (180) en uit1 (196)
  bord(24.5, "PAGODE", "Efteling · 1987")                  -- tussen in1 (16) en in0 (33)
  bord(106, "PAGODE", "Efteling · 1987")
  bord(286, "PAGODE", "Efteling · 1987")
end
