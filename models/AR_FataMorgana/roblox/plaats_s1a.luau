-- plaats_s1a: sectie 1a (gordijn naar de jungle) afmaken NA plaats_modellen (Daan 19 nov: "maak de gordijnen de kleur die ze in het
-- echt hebben en zorg dat het bordje goed zichtbaar is").
--  - gordijnkleur: in de POV-video (122,5 s) onder het warme hallicht mediaan RGB (94, 57, 45) = neutraal lichtgrijs/beige doek
--    (Eftepedia: "beige gordijn") -> Color (205, 193, 180), Fabric
--  - warme spot onder de westgaanderij op het gordijn (in de video is het gordijn lichter dan de muren eromheen)
--  - bordje: SurfaceGui met tekst (licht, weinig lichtinvloed) op het bordvlak, kant hal, i.p.v. alleen een textuur in het donker
local fm = workspace:WaitForChild("FataMorgana")
local g = fm:WaitForChild("Junglegordijn")
for _, naam in {"FM_gordijn_l_0_junglegordijn", "FM_gordijn_r_0_junglegordijn"} do
	local p = g[naam]; p.Color = Color3.fromRGB(205, 193, 180); p.Material = Enum.Material.Fabric
end
g.FM_gordijnrail_0_junglegordijn.Color = Color3.fromRGB(196, 186, 172)

local oud = g:FindFirstChild("Gordijnlicht"); if oud then oud:Destroy() end
local l = Instance.new("Part"); l.Name = "Gordijnlicht"; l.Size = Vector3.new(0.4, 0.4, 0.4); l.Transparency = 1
l.Anchored = true; l.CanCollide = false; l.CanQuery = false; l.CanTouch = false; l.CastShadow = false
local DOEL = Vector3.new(3 * -3.62, 0.91 + 3 * -1.8, 3 * 326.5)
l.CFrame = CFrame.lookAt(Vector3.new(3 * -1.4, 0.91 + 3 * -0.6, 3 * 326.5), DOEL)
local s = Instance.new("SpotLight"); s.Face = Enum.NormalId.Front; s.Angle = 75; s.Range = 18; s.Brightness = 1.6
s.Color = Color3.fromRGB(255, 206, 160); s.Shadows = false; s.Parent = l
l.Parent = g

local bord = g.FM_s1_bord_0_junglegordijn
for _, c in bord:GetChildren() do c:Destroy() end
bord.Transparency = 0; bord.Color = Color3.fromRGB(34, 62, 50); bord.Material = Enum.Material.SmoothPlastic
local face, best = Enum.NormalId.Right, -2
for _, f in {Enum.NormalId.Right, Enum.NormalId.Left} do
	local n = bord.CFrame:VectorToWorldSpace(Vector3.FromNormalId(f))
	if n.X > best then best = n.X; face = f end                              -- de hal ligt aan de +X-kant
end
local sg = Instance.new("SurfaceGui"); sg.Name = "Tekst"; sg.Face = face; sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
sg.PixelsPerStud = 60; sg.LightInfluence = 0.15; sg.Brightness = 1.4; sg.AlwaysOnTop = false; sg.Parent = bord
local fr = Instance.new("Frame"); fr.Size = UDim2.fromScale(1, 1); fr.BackgroundColor3 = Color3.fromRGB(30, 58, 46); fr.BorderSizePixel = 0; fr.Parent = sg
for i, t in {"Niet schommelen // Nicht schaukeln", "No rocking // Interdit de se balancer"} do
	local tl = Instance.new("TextLabel"); tl.BackgroundTransparency = 1; tl.Size = UDim2.fromScale(0.96, 0.42)
	tl.Position = UDim2.fromScale(0.02, i == 1 and 0.06 or 0.52); tl.Text = t; tl.TextScaled = true
	tl.Font = Enum.Font.GothamBold; tl.TextColor3 = Color3.fromRGB(246, 224, 150); tl.Parent = fr
end
return face.Name
