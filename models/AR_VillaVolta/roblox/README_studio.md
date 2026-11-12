# Villa Volta in Studio — volgorde
1. `plaats_villavolta.luau` (genereer met `maak_plaatsscript.py VILLA OMG`): villa + tuin/rij, botsblokken, lampen, teksten.
2. (VERVALLEN, te grof: 4-stud voxels) Paden in het terrein schilderen. Nu: paden + plein zijn meshes uit
   `build/05_paden_polygonen.py` (shapely-venv: samengevoegd per materiaal, opsluitbanden op elke rand/overgang) -> 04_omgeving.
   Stijl: grind Pebble (190,176,148), plein/klinker Cobblestone (visgraat-variant), rode klinker Brick (86,50,42), band Concrete (176,174,168).
   Oude notitie terreinschilderen: ReadVoxels/WriteVoxels, alleen materiaal,
   vlakke grond = voxels vol tot Y=0, leeg erboven (oppervlak Y=2). Grind = Pavement (184,170,142), klinker/plein = Cobblestone
   (MaterialVariant EftelingKlinkers), rij-aanloop = Brick (96,56,46). Paddata staat in `exports/omgeving_data.json` -> "paden";
   pleinvorm = OSM 55344641 (zie STATUS). FillBlock/FillCylinder NIET gebruiken: die verhogen het maaiveld.
3. Groen: map `VillaVoltaGroen`, klonen uit ServerStorage.BomenBronV3 (beuk/eik/kastanje/berk + rododendron/taxus/struik), seed 1996.
4. Licht: ClockTime 14.2, Brightness 3, Atmosphere density 0.28, ColorCorrection, DoF uit, Terrain.Decoration uit (gemaaid gras).
   Lighting.Technology = Future moet Daan zelf zetten (Assistant mag dat niet).
5. Kleuren na plaatsen: klinkerrood (86,50,42), rvs (132,136,140) Metal.

6. Terrein rond de villa (lokaal x -40..40, y -85..55): gazon (Grass 84,118,54) alleen binnen de tuin (polygoon tussen beukenhagen en terras),
   daarbuiten bosgrond: LeafyGrass (66,92,44) en Ground (74,58,42) via math.noise. Daarna 172 heesters in groepjes + 24 bosrandbomen (seed 51),
   vrij van paden/plein/gebouw. Laatste assets: villa **99373517894794**, omgeving **134354426343629** (met UV's: export doet kubusprojectie 1 UV = 2 m).
7. Sfeer (Daan: "voelt niet alsof ik in de game loop", "overbelicht"):
   - Lighting: Brightness 2.2, ExposureCompensation -0.25, Ambient (52,54,62), OutdoorAmbient (98,102,114), EnvDiffuse 0.8, EnvSpecular 0.5,
     ClockTime 15.3; Atmosphere density 0.33 haze 1.6 glare 0.08; Bloom 0.22/20/2.4; ColorCorrection contrast 0.14 sat 0.04 bright -0.03.
   - Materiaalkleuren getemperd (stuc 205,188,150; steen 182,174,154; grind 148,134,112 Pebble; klinker/plein 122,94,78; band 118,116,110).
   - Boomschaduw AAN in VillaVoltaGroen (BomenBronV3 had bladschaduw uit voor parkprestaties).
   - StarterPlayer.CharacterWalkSpeed = 10 (16 = 5.3 m/s op 3 studs/m: draven).
   - SoundService: VV_Vogels 9113444360 (vol 0.35), VV_Publiek 9112766533 (vol 0.08), ProSoundEffects.
   - Opsluitband alleen nog op de buitenrand; paden lopen zonder band in elkaar over. Omgeving-asset **81904859328304**.
   - Lighting.Technology = Future: door Daan zelf te zetten.
8. Alle paden hetzelfde lichte grind (ook naar de rij); plein blijft kasseien, rijvloer rode klinkers. Omgeving-asset **76728015894633**.
   ServerScriptService.SpelerSchaal: speler 0.9x (char:ScaleTo bij CharacterAppearanceLoaded).
9. Plein: MeshPart-materiaal Pavement (visgraatklinkers, schaal goed) kleur (178,162,140) i.p.v. Cobblestone+variant (te donker, te fijn).
10. Plein weggehaald (later met heel het Ton van de Venplein). Rijvloer = grind. Lantaarnpalen verplaatst naar exports/lampposten.json (naast het pad, vrij van hagen; gezocht met shapely). Omgeving-asset **109033549155370**.
11. Beplanting: `build/07_planten.py` -> asset **111885456628958** (15 prototypes: gras0-2, siergras0-1, varen0-1, bloem_rood/geel/paars/wit/roze,
    lavendel, bodem0-1; 3.3k tris). In Studio als ServerStorage.VVPlanten (Model per prototype, pivot op de grond).
    workspace.VillaVoltaPlanten: borders 0.4-1.1 m van hagen/terras in de tuin (lavendel, siergras, bloemen, bodem; seed 2026),
    5% losse plukjes in het gazon, bosgrond in groepjes van dezelfde soort (seed 2026, 420 groepen). Paden/gebouw/rij/plein vrij.
    Tweede bosbodemlaag gedaan (varens 1.4-2.1x, 650 groepen, seed 77): totaal 5943 plantmodellen. Let op prestaties (LOD/streaming later).
12. Echte texturen (ambientCG CC0, `textures/ambientcg/`, ids in asset_ids.txt) als MaterialVariants in MaterialService:
    VV_Gazon (Grass, Grass005, 7 studs/tegel) = override terreingras; VV_Bosgrond (Mud, Ground037, 10) = override, bosgrond-voxels
    LeafyGrass -> Mud omgezet (zodat hagen LeafyGrass houden); VV_Bosbodem (Ground, Ground076, 10) = override;
    VV_Grind (Pebble, Ground091 aangestampt grind; Gravel023 was te wit/vlak) expliciet op MAT_grind-MeshParts, kleur (235,228,214).
    Terreinkleuren: Grass (215,230,200), Mud (200,200,190), Ground (190,180,170). Nieuwe Images laden in Studio pas na enkele minuten.
    Bloemperken: oude icosphere-blokjes (MAT_bloem_*) verwijderd, 398 echte bloemen in kleurbanden met bodembedekkerrand (seed 5).
    Daan: "het is een pretpark, felle kleuren mogen" -> ColorCorrection saturation 0.18.
13. Echte planten (Poly Haven CC0, `build/08_polyhaven_planten.py`, texturen `textures/polyhaven/`, ids in
    `exports/polyhaven/asset_ids.txt`): 80 varianten als ServerStorage.VVEchtePlanten (MeshPart + SurfaceAppearance; kleurtexturen
    ~60% helderder gemaakt `*_diffhelder`, scans waren te donker). workspace.VillaVoltaPlantenEcht vervangt de nepplanten
    (oude in ServerStorage.VillaVoltaPlanten_oud): gras -> grass_bermuda, perken -> gazania/ursinia (dicht, 1.4-1.9x),
    borders -> periwinkle/sorrel/shrub_03, bos -> fern/nettle/weed/dandelion + 97 grote struiken (shrub_02/04).
    Nieuwe Images zichtbaar maken: eerst via Decal preloaden (ContentProvider) en ColorMap opnieuw zetten.
14. Haag met diepte: `04_omgeving.py` haag() = doorlopende vorm met ronde bovenkant en ruis-bobbels; textuur
    `build/10_haagtextuur.py` (gerenderd uit 650 echte shrub_02-takjes, naadloos 2x2 m) -> kleur 107834399804087, normaal 80469356130057
    als SurfaceAppearance op MAT_beuk/buxus/haag. Export knipt nu grote meshes in stukken i.p.v. decimeren.
    Omgeving-asset **107244417789180**. Proef met losse haagtakjes (te sprieterig) staat in ServerStorage.VillaVoltaHaagschil_proef.
15. Symmetrische tuin (Daan): superellips (n=2.6, midden (0,-15.3)) voor het lus-pad (a10 b8.8) en de beukenbogen (a12.9 b11.4)
    tot pilaren op (+-2.5,-26.65); gespiegelde bladperken + binnenbogen, middengroep 0.8x naar het midden (0.7 m vrij van het pad);
    zijpaden als Catmull-Rom-krommes. Omgeving-asset **75132263450665** (met COLL_/LAMP_-onderdelen: geen datalijsten meer plakken;
    Studio: COLL_ -> map Botsing, onzichtbaar, CollisionFidelity Box; LAMP_ -> map Lampen met PointLight).
    Planten in de tuin opnieuw verspreid (seed 2027/2028). Terrein: gazon = superellips a13.6 b12.1; gras buiten de tuin
    (VV_Bosgrond, base Mud) nu Grass005 op 11 studs/tegel, kleur (232,244,212) = lichter parkgras. MAT_aarde DoubleSided.
16. Realisme-ronde (Daan: "fix alles behalve first person en geluid"):
    - grasbosjes -> plantgroepjes (seed 606); lantaarns dag/nacht: ServerScriptService.LantaarnsDagNacht (rij-lampen attribuut Binnen = altijd aan)
    - lucht: Terrain.Clouds (cover 0.62, density 0.72) + nevelige Atmosphere
    - villa PBR (ambientCG CC0): VV_Pleister (Plaster002) op stuc, VV_Steen (pleisterkleur + Concrete012-relief) op steen,
      VV_Lei (RoofingTiles001) op lei, VV_Wit (PaintedPlaster017) op wit; glas = donker SmoothPlastic, reflectance 0.12
    - bomen: bladkaarten vervangen door echte bladtrossen (`build/11_bladkaarten.py`, `textures/bomen/asset_ids.txt`)
    - horizon: 1548 echte OSM-bomen/struiken tot 300 m (data-PNG asset 76283368076918, map VillaVoltaHorizon)
    - beweging: StarterPlayerScripts.Wind (BulkMoveTo, 45 m rond camera) + bladval-ParticleEmitters onder 24 bomen
    - bezoekers: ServerScriptService.Bezoekers (10 R15-figuren, wandelen over het ovale pad, 2 kijkers bij de zonnewijzer)
    - galerij: lambrisering, pilasters, kroonlijst, plafondbalken, panelen in de borstwering, paneeldeuren met glas/bovenlicht/klinken.
      Omgeving-asset **76111214657159**.
