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
