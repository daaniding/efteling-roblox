-- Realistisch licht voor de Efteling (Kaatsheuvel, 51,65 N). Draai in Studio (Edit) via execute_luau of de Command Bar.
-- Kies de stand hieronder: "schemering" (Daans keuze 16 nov: "echt die dusk") of "middag".
-- LightingStyle / PrioritizeLightingQuality stelt Daan zelf in (Realistic + kwaliteit aan = de oude 'Future').
-- Lucht = echte foto-HDRI (Poly Haven CC0, ../BRON.txt), omgezet door ../build/01_skybox.py en zo gedraaid dat de zon op
-- de foto in de richting van de Roblox-zon staat. Verander de tijd dus niet los van de lucht.
-- Let op (gemeten 16 nov): onder ~5 graden zonnehoogte kleurt Roblox de skybox zelf oranje/rood in. Daan koos juist dat
-- beeld (zon op de horizon, gouden streep, eerste sterren, geen Atmosphere). Een pastel-lila versie kan met ClockTime 17.3.
local STAND = "schemering"

local L = game:GetService("Lighting")
local STANDEN = {
	middag = {   -- kloofendal_48d_partly_cloudy_puresky; zon 47,9 graden
		lucht = { Ft = 107557028958026, Bk = 116621794851780, Lf = 112911982748978, Rt = 80272611932800, Up = 113896343777797, Dn = 103186968486026 },
		zon = 8, sterren = 3000,
		licht = { ClockTime = 14.1839, Brightness = 3, ExposureCompensation = 0, Ambient = Color3.fromRGB(18, 20, 24), OutdoorAmbient = Color3.fromRGB(106, 108, 114) },
		atmosfeer = { Density = 0.25, Offset = 0.5, Color = Color3.fromRGB(226, 230, 238), Decay = Color3.fromRGB(196, 204, 218), Glare = 0.2, Haze = 0.8 },
		kleur = { Contrast = 0.08, Saturation = -0.06, TintColor = Color3.fromRGB(255, 251, 245) },
		gloed = { Intensity = 0.5, Size = 28, Threshold = 1.8 },
		stralen = { Intensity = 0.04, Spread = 0.55 },
		verte = 0.08,
	},
	schemering = {   -- belfast_sunset_puresky; zon op de foto 2,1 graden, Roblox-zon 2,1 graden (ClockTime 17.8439)
		lucht = { Ft = 106457871100289, Bk = 133107173128123, Lf = 130881222383257, Rt = 127070471178195, Up = 118986672181749, Dn = 130111079083953 },
		zon = 10, sterren = 3000,
		licht = { ClockTime = 17.8439, Brightness = 2.2, ExposureCompensation = 0.85, Ambient = Color3.fromRGB(40, 30, 54), OutdoorAmbient = Color3.fromRGB(168, 128, 205) },   -- lichter en paars (Daan)
		atmosfeer = nil,   -- zonder nevel: dan blijft de gouden horizonstreep zichtbaar
		kleur = { Contrast = 0.04, Saturation = 0.04, TintColor = Color3.fromRGB(236, 220, 255) },   -- paarse waas
		gloed = { Intensity = 0.8, Size = 40, Threshold = 1.2 },
		stralen = { Intensity = 0.12, Spread = 0.8 },
		verte = 0.15,
	},
}
local S = STANDEN[STAND]

local vast = { GeographicLatitude = 51.65, EnvironmentDiffuseScale = 1, EnvironmentSpecularScale = 1, GlobalShadows = true,
	ShadowSoftness = 0.12, ColorShift_Top = Color3.new(0, 0, 0), ColorShift_Bottom = Color3.new(0, 0, 0), FogEnd = 100000 }
for k, v in pairs(vast) do L[k] = v end
for k, v in pairs(S.licht) do L[k] = v end

local function maak(klasse, naam, props)
	local o = L:FindFirstChild(naam) or Instance.new(klasse)
	o.Name = naam
	for k, v in pairs(props) do o[k] = v end
	o.Parent = L
	return o
end

local lucht = maak("Sky", "Lucht", { CelestialBodiesShown = true, SunAngularSize = S.zon, MoonAngularSize = 9, StarCount = S.sterren })
for k, v in pairs(S.lucht) do lucht["Skybox" .. k] = "rbxassetid://" .. v end

local atm = L:FindFirstChildOfClass("Atmosphere")
if S.atmosfeer then maak("Atmosphere", "Atmosfeer", S.atmosfeer) elseif atm then atm:Destroy() end

maak("ColorGradingEffect", "Tonemapper", { TonemapperPreset = Enum.TonemapperPreset.Default })
maak("ColorCorrectionEffect", "Kleur", { Brightness = 0, Contrast = S.kleur.Contrast, Saturation = S.kleur.Saturation, TintColor = S.kleur.TintColor })
maak("BloomEffect", "Gloed", S.gloed)
maak("SunRaysEffect", "Zonnestralen", S.stralen)
maak("DepthOfFieldEffect", "Scherptediepte", { FarIntensity = S.verte, FocusDistance = 40, InFocusRadius = 70, NearIntensity = 0 })

local wolk = workspace.Terrain:FindFirstChildOfClass("Clouds")
if wolk then wolk.Enabled = false end   -- de wolken zitten in de foto-lucht

return "licht: " .. STAND
