-- Realistisch daglicht voor de Efteling (Kaatsheuvel, 51,65 N), 16 nov 2026. Draai in Studio (Edit) via execute_luau of de Command Bar.
-- LightingStyle / PrioritizeLightingQuality stelt Daan zelf in (nu Realistic + kwaliteit aan = de oude 'Future').
-- Bronnen: create.roblox.com/docs/environment/lighting, .../atmosphere, .../post-processing-effects en de tutorial
-- 'Enhance outdoor environments' (Realistic, Environment*Scale 1, Atmosphere-dichtheid 0,27-0,39).
-- Lucht: echte foto-HDRI (Poly Haven, CC0, zie ../BRON.txt), omgezet door ../build/01_skybox.py. De zon op de foto
-- staat op 47,9 graden; ClockTime 14.1839 geeft in Roblox exact die zonnehoogte en de skybox is zo gedraaid dat de
-- Roblox-zon precies op de zon van de foto valt (gecontroleerd). Verandert de tijd, dan klopt de lucht niet meer.
-- Gemeten in de proefscène: schaduw op gras = 17% van zonlicht (echt 15-25%), wit in de zon niet uitgebrand.
local L = game:GetService("Lighting")
local W = {
	GeographicLatitude = 51.65,
	ClockTime = 14.1839,
	Brightness = 3,
	ExposureCompensation = 0,
	Ambient = Color3.fromRGB(18, 20, 24),          -- binnen: bijna donker, licht komt van ramen/lampen
	OutdoorAmbient = Color3.fromRGB(106, 108, 114), -- buiten in de schaduw; het blauw komt al uit de lucht (EnvironmentDiffuse)
	EnvironmentDiffuseScale = 1,
	EnvironmentSpecularScale = 1,
	GlobalShadows = true,
	ShadowSoftness = 0.12,
	ColorShift_Top = Color3.fromRGB(0, 0, 0),
	ColorShift_Bottom = Color3.fromRGB(0, 0, 0),
	FogEnd = 100000,
}
for k, v in pairs(W) do L[k] = v end

local function maak(klasse, naam, props)
	local o = L:FindFirstChild(naam) or Instance.new(klasse)
	o.Name = naam
	for k, v in pairs(props) do o[k] = v end
	o.Parent = L
	return o
end

local ID = { Ft = 107557028958026, Bk = 116621794851780, Lf = 112911982748978, Rt = 80272611932800, Up = 113896343777797, Dn = 103186968486026 }
local lucht = maak("Sky", "Lucht", { CelestialBodiesShown = true, SunAngularSize = 8, MoonAngularSize = 9, StarCount = 3000 })
for k, v in pairs(ID) do lucht["Skybox" .. k] = "rbxassetid://" .. v end

-- nevel in de verte; lichte kleuren, anders ontstaat er een donkerblauwe band boven de horizon
maak("Atmosphere", "Atmosfeer", {
	Density = 0.25, Offset = 0.5,
	Color = Color3.fromRGB(226, 230, 238), Decay = Color3.fromRGB(196, 204, 218),
	Glare = 0.2, Haze = 0.8,
})

-- nabewerking: subtiel, zoals een camera
maak("ColorGradingEffect", "Tonemapper", { TonemapperPreset = Enum.TonemapperPreset.Default })
maak("ColorCorrectionEffect", "Kleur", {
	Brightness = 0, Contrast = 0.08, Saturation = -0.06, TintColor = Color3.fromRGB(255, 251, 245),
})
maak("BloomEffect", "Gloed", { Intensity = 0.5, Size = 28, Threshold = 1.8 })
maak("SunRaysEffect", "Zonnestralen", { Intensity = 0.04, Spread = 0.55 })
maak("DepthOfFieldEffect", "Scherptediepte", {
	FarIntensity = 0.08, FocusDistance = 40, InFocusRadius = 70, NearIntensity = 0,
})

-- de wolken zitten in de foto-lucht; de Roblox-wolken zouden dubbel zijn
local wolk = workspace.Terrain:FindFirstChildOfClass("Clouds")
if wolk then wolk.Enabled = false end

return "licht ingesteld"
