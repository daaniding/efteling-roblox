# Grond en gras in Studio (16 nov 2026)
- MaterialService: `EF_Gras` (Grass, Grass004, ColorMap = `GR_gras004_kleurdeel` 107303354599469, Normal 97601381872596,
  Roughness 86471509335412, StudsPerTile 7, Organic) en `EF_Grond` (Ground, forrest_ground_01, ColorMap 124967250191490,
  Normal 96219268407404, Roughness 94933588063798, StudsPerTile 8, Organic). Beide als BaseMaterialOverride.
- Roblox vermenigvuldigt de ColorMap met Terrain:GetMaterialColor. Daarom is de kleurkaart = foto / tint (build/01_texturen.py).
  Terreinkleuren: Grass (98, 110, 56) (iets donkerder dan de tint 119,130,69 zodat de bodem bij de 3D-sprieten past),
  Ground (139, 124, 100).
- Terrain.Decoration (Roblox-sprieten) staat UIT: te plat en cartoonachtig. Alleen Daan kan dat vinkje zetten.
- 3D-gras: ReplicatedStorage.Gras.plukje0-2 (assets 111175948320411 / 98038054688851 / 129479706379170, x3 geschaald,
  TextureID GR_sprietkleur 126762741933227, Plastic, DoubleSided, CastShadow uit) + `speler/GrasRondSpeler.client.luau`
  (alleen op terrein-gras, straal 16 stud, cel 0,9 stud, 3 plukjes/cel binnen 9 stud, 1 daarbuiten, krimpt aan de rand).
  Gemeten: ~1.600 zichtbare plukjes (250 driehoeken elk), ~62 fps in Studio.
