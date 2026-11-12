# Villa Volta in Studio — volgorde
1. `plaats_villavolta.luau` (genereer met `maak_plaatsscript.py VILLA OMG`): villa + tuin/rij, botsblokken, lampen, teksten.
2. Paden + Ton van de Venplein worden in het **terrein** geschilderd (geen meshes): ReadVoxels/WriteVoxels, alleen materiaal,
   vlakke grond = voxels vol tot Y=0, leeg erboven (oppervlak Y=2). Grind = Pavement (184,170,142), klinker/plein = Cobblestone
   (MaterialVariant EftelingKlinkers), rij-aanloop = Brick (96,56,46). Paddata staat in `exports/omgeving_data.json` -> "paden";
   pleinvorm = OSM 55344641 (zie STATUS). FillBlock/FillCylinder NIET gebruiken: die verhogen het maaiveld.
3. Groen: map `VillaVoltaGroen`, klonen uit ServerStorage.BomenBronV3 (beuk/eik/kastanje/berk + rododendron/taxus/struik), seed 1996.
4. Licht: ClockTime 14.2, Brightness 3, Atmosphere density 0.28, ColorCorrection, DoF uit, Terrain.Decoration uit (gemaaid gras).
   Lighting.Technology = Future moet Daan zelf zetten (Assistant mag dat niet).
5. Kleuren na plaatsen: klinkerrood (86,50,42), rvs (132,136,140) Metal.
