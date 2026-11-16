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
		zon = 8, sterren = 3000, gras = Color3.fromRGB(98, 110, 56),
		licht = { ClockTime = 14.1839, Brightness = 3, ExposureCompensation = 0, Ambient = Color3.fromRGB(18, 20, 24), OutdoorAmbient = Color3.fromRGB(106, 108, 114) },
		atmosfeer = { Density = 0.25, Offset = 0.5, Color = Color3.fromRGB(226, 230, 238), Decay = Color3.fromRGB(196, 204, 218), Glare = 0.2, Haze = 0.8 },
		kleur = { Contrast = 0.08, Saturation = -0.06, TintColor = Color3.fromRGB(255, 251, 245) },
		gloed = { Intensity = 0.5, Size = 28, Threshold = 1.8 },
		stralen = { Intensity = 0.04, Spread = 0.55 },
		verte = 0.08,
	},
	schemering = {   -- belfast_sunset_puresky; zon op de foto 2,1 graden, Roblox-zon 2,1 graden (ClockTime 17.8439)
		-- v4: anti-zonkant opgehelderd + paars in de lucht zelf (01_skybox.py ... -0.88096 0.03602 0.47181 -0.3 2.2 0.86 0.82 1.12)
		lucht = { Ft = 129297966488534, Bk = 75659856270740, Lf = 115529229283104, Rt = 98242062795457, Up = 125287541652465, Dn = 80340274035280 },
		zon = 5, sterren = 0, gras = Color3.fromRGB(80, 116, 60),   -- kleine zon (gloed doet het werk), geen sterren zolang de zon op is, koeler gras
		licht = { ClockTime = 17.8439, Brightness = 3, ExposureCompensation = 1.5, Ambient = Color3.fromRGB(54, 46, 42), OutdoorAmbient = Color3.fromRGB(196, 158, 214) },   -- licht, gezellig, warm-paars (Daan)
		-- dunne nevel = dromerige, lichtende lila horizon (zonder nevel: gouden horizonstreep, Daans eerdere keuze)
		atmosfeer = { Density = 0.1, Offset = 0.8, Color = Color3.fromRGB(246, 204, 160), Decay = Color3.fromRGB(214, 196, 226), Glare = 1.8, Haze = 0.5 },
		kleur = { Brightness = 0.04, Contrast = -0.06, Saturation = 0.08, TintColor = Color3.fromRGB(255, 248, 240) },   -- bijna neutraal: het paars zit in lucht + schaduwlicht, interieurs blijven warm wit
		gloed = { Intensity = 1.4, Size = 56, Threshold = 0.95 },
		stralen = { Intensity = 0.18, Spread = 0.9 },
		verte = 0.12, focus = 30, scherp = 50,
	},
}
local S = STANDEN[STAND]

local vast = { GeographicLatitude = 51.65, EnvironmentDiffuseScale = 1, EnvironmentSpecularScale = 1, GlobalShadows = true,
	ShadowSoftness = 0.12, ColorShift_Top = Color3.new(0, 0, 0), ColorShift_Bottom = Color3.new(0, 0, 0), FogEnd = 100000 }
for k, v in pairs(vast) do L[k] = v end
for k, v in pairs(S.licht) do L[k] = v end
-- graskleur hoort bij de stand (Roblox vermenigvuldigt de grasfoto met deze kleur; zie models/LI_Grond)
workspace.Terrain:SetMaterialColor(Enum.Material.Grass, S.gras)

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
maak("ColorCorrectionEffect", "Kleur", { Brightness = S.kleur.Brightness or 0, Contrast = S.kleur.Contrast, Saturation = S.kleur.Saturation, TintColor = S.kleur.TintColor })
maak("BloomEffect", "Gloed", S.gloed)
maak("SunRaysEffect", "Zonnestralen", S.stralen)
maak("DepthOfFieldEffect", "Scherptediepte", { FarIntensity = S.verte, FocusDistance = S.focus or 40, InFocusRadius = S.scherp or 70, NearIntensity = 0 })

local wolk = workspace.Terrain:FindFirstChildOfClass("Clouds")
if wolk then wolk.Enabled = false end   -- de wolken zitten in de foto-lucht

return "licht: " .. STAND
