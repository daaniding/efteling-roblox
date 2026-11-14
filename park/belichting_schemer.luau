-- Belichting "schemer" voor het hele park (Daan: realistischer, schemerig). Late namiddag/schemering in Kaatsheuvel (51.6 N):
-- lage warme zon met lange zachte schaduwen, nevel tussen de bomen, iets meer contrast, lantaarns en ramen gloeien.
-- Uitvoeren in de Command Bar of via MCP (Edit). Terugdraaien: dezelfde waarden van de vorige stand staan onderaan in een commentaar.
local L = game:GetService("Lighting")
L.ClockTime = 17.85               -- zonsondergang: roze-violette sprookjeslucht (18.7 werd nacht met sterren)
L.GeographicLatitude = 51.6
L.Brightness = 2.8
L.ExposureCompensation = 0.35
L.Ambient = Color3.fromRGB(52, 48, 58)
L.OutdoorAmbient = Color3.fromRGB(138, 124, 130)
L.ColorShift_Top = Color3.fromRGB(255, 214, 170)
L.ColorShift_Bottom = Color3.fromRGB(60, 56, 72)
L.EnvironmentDiffuseScale = 1
L.EnvironmentSpecularScale = 1
L.ShadowSoftness = 0.35
L.GlobalShadows = true

local function effect(cls, naam)
	local e = L:FindFirstChild(naam) or L:FindFirstChildOfClass(cls)
	if not e then e = Instance.new(cls); e.Name = naam; e.Parent = L end
	return e
end
local a = effect("Atmosphere", "Atmosphere")
a.Density = 0.33; a.Offset = 0.2; a.Haze = 2.6; a.Glare = 1.2
a.Color = Color3.fromRGB(226, 196, 176); a.Decay = Color3.fromRGB(150, 112, 140)
-- lucht: geschilderde skybox eruit (Roblox-standaard, door de Atmosphere roze/violet gekleurd), geen sterren, zachte warme wolken
local sky = L:FindFirstChildOfClass("Sky") or Instance.new("Sky", L)
for _, k in ipairs({"SkyboxBk", "SkyboxDn", "SkyboxFt", "SkyboxLf", "SkyboxRt", "SkyboxUp"}) do sky[k] = "" end   -- was rbxassetid://6444884337 e.a.
sky.StarCount = 0; sky.SunAngularSize = 14
local cl = workspace.Terrain:FindFirstChildOfClass("Clouds") or Instance.new("Clouds", workspace.Terrain)
cl.Cover = 0.5; cl.Density = 0.55; cl.Color = Color3.fromRGB(255, 238, 222)
local cc = effect("ColorCorrectionEffect", "ColorCorrection")
cc.Enabled = true; cc.Brightness = 0.0; cc.Contrast = 0.12; cc.Saturation = -0.02; cc.TintColor = Color3.fromRGB(255, 238, 220)
local bl = effect("BloomEffect", "Bloom")
bl.Enabled = true; bl.Intensity = 0.7; bl.Size = 30; bl.Threshold = 1.5
local sr = effect("SunRaysEffect", "SunRays")
sr.Enabled = true; sr.Intensity = 0.07; sr.Spread = 0.55
local dof = effect("DepthOfFieldEffect", "DepthOfField")
dof.Enabled = true; dof.FarIntensity = 0.12; dof.NearIntensity = 0; dof.FocusDistance = 70; dof.InFocusRadius = 90

-- lantaarns iets feller nu het schemert (alle PointLights in de attractie-mappen "Lampen")
local n = 0
for _, d in ipairs(workspace:GetDescendants()) do
	if d:IsA("PointLight") and d.Parent and d.Parent.Parent and d.Parent.Parent.Name == "Lampen" then
		d.Brightness = 1.2; d.Range = 16; n += 1
	end
end
return "schemer-belichting gezet; lampen " .. n

-- vorige stand (13 nov): ClockTime 15.3, Brightness 2.2, Ambient (52,54,62), OutdoorAmbient (98,102,114),
-- EnvironmentDiffuseScale 0.8, EnvironmentSpecularScale 0.5, ShadowSoftness 0.12, ExposureCompensation -0.25
