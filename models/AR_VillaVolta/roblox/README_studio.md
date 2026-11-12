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
