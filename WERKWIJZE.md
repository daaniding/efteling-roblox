# Efteling in Roblox — werkwijze en lessen (lees dit samen met STATUS.md)

Opgebouwd tijdens Villa Volta (12 nov 2026). Dit zijn Daans wensen en wat technisch werkt. Na ELKE stap: STATUS.md + geheugen bijwerken.

## Afspraken met Daan (Sprookjesboom, 12 nov) — gelden voor elke volgende attractie
- **Alleen bouwen wat gevraagd is:** de attractie + de scène direct eromheen (~15 m). Geen paden door het park, geen andere gebieden
  "alvast" meenemen ("niet overal het pad, dat vroeg ik niet"). Paden komen later, apart. Bij twijfel over de omvang: eerst vragen.
- **Na elke build de tips vastleggen** (dit bestand + geheugen), niet alleen de status.
- **Eerst kijken hoe de scène er echt uitziet:** alle Eftepedia-plaatjes van de attractie downloaden (lemma-pagina, `ref/eftepedia/`), op één
  blad bekijken en elk zichtbaar element terug laten komen (stenen, water, hekjes, lantaarns, bankjes, planten, figuren).
- **Dieren/figuren:** geen zelfgeboetseerde bolletjes; Roblox generate_mesh (AI, getextureerd) geeft het gevraagde detail.
- **Water:** mag modderig/troebel en moet leven (stromende lagen, drijvende blaadjes, rimpelringen, kroos, natte stenen).
- **Kleur/tint achteraf** via SurfaceAppearance.Color (stam "iets donkerder") zonder nieuwe bake.
- **Geen zwevende tekst** (layout-labels, tekstballonnen) bij gebouwde dingen; scripts die op zo'n label wachten aanpassen.
- **Altijd checken:** close-ups in Studio (facetten, gaten, zwevers) en een prestatietest in Play (fps met en zonder de nieuwe scène).

## Eerst bronnen, dan bouwen ("zoals in de Efteling", niet verzinnen)
- OSM (`reference/data/efteling_osm.xml`): footprints, paden, hagen, muren, wachtrij-zigzag, poortjes, deuren, lantaarns, bomen.
  Omrekenen naar modelcoordinaten per attractie (zie `models/AR_VillaVolta/ref/osm_lokaal.json`).
- Plattegronden/tekeningen: darkridedatabase.com (bv. "Madhouses II" met plattegrond en maten), eftepedia.nl (foto's wachtrij, details),
  Wikimedia Commons (foto's van alle kanten, ook zijkant/achterkant). Maten uit foto's: deur = 3,0 m als maatstok.
- Echte bouwtekeningen zijn niet openbaar; combineer plattegrond + OSM + foto's.
- OSM-vormen zijn scheef getekend: tuinen symmetrisch maken en paden vloeiend rond (superellips / Catmull-Rom), geen hoeken.

## Speelbaarheid en gevoel (Daan)
- 3 studs = 1 m, maar looproutes ~1,5x breder dan echt (wachtrijbanen 1,6 m, galerij breder, paden ~3,4 m). Niets in de looproute.
- Hagen/perken nooit tegen of door een pad; ~0,7 m gras ertussen. Groene stroken langs paden altijd beplanten (borders).
- WalkSpeed 10 (16 = draven), speler 0,9x (ServerScriptService.SpelerSchaal). GEEN first-person. GEEN NPC-bezoekers.
- Geluid en interieurs komen pas later (als het hele park staat).
- Pretpark: felle kleuren mogen, maar materialen moeten echt ogen. Niet overbelichten (Brightness ~2,2, exposure negatief).
- Lighting.Technology = Future moet Daan zelf zetten (Assistant mag het niet).

## Realisme: wat werkt
- Standaard Roblox-materialen ogen nep -> CC0-scans als MaterialVariants (ambientCG: gras, grind, pleister, steen, leien).
  Download pas na toestemming van Daan. Bron vermelden in `textures/*/BRON.txt`.
- Planten: Poly Haven-scans (CC0) via headless Blender gedecimeerd (`build/08_polyhaven_planten.py`), SurfaceAppearance;
  scans zijn donker -> kleurtextuur ~60% ophelderen. Bomen: bladkaarten met gerenderde echte bladtrossen (`build/11_bladkaarten.py`).
- Hagen: bobbelige vorm (ruis, ronde bovenkant) + textuur gerenderd uit echte takjes (`build/10_haagtextuur.py`). Losse takjes = sprieterig.
- Paden: meshes samengevoegd met shapely (`build/05_paden_polygonen.py`), alles een hoogte, randsteen alleen aan de buitenkant.
  Terrein-voxels (4 studs) zijn te grof voor paden; FillBlock verhoogt het maaiveld (vlak = vol tot Y=0, leeg erboven, oppervlak Y=2).
- Horizon: echte OSM-bomen tot 300 m terugzetten (data-PNG + EditableImage). Wolken (Terrain.Clouds) + nevel.
- Beweging: lokale wind (BulkMoveTo rond de camera), bladval-particles. Lantaarns overdag uit (script).

## Techniek / valkuilen
- Export: grote meshes knippen i.p.v. decimeren (`09_export_roblox.py`), UV's kubusprojectie 1 UV = 2 m, botsblokken (COLL_) en
  lichtpunten (LAMP_) als losse onderdelen in het model -> geen lange datalijsten plakken in Studio.
- Studio: HTTP naar GitHub/localhost geblokkeerd; data via PNG (EditableImage) of plakken. Nieuwe Images pas zichtbaar na Decal-preload
  (ContentProvider) en ColorMap opnieuw zetten. execute_luau time-out = vaak toch klaar: daarna controleren. In Play-modus kan niets in Edit.
- Een anker-blokje op z=-2 in elke export geeft de modeloorsprong terug in Studio (Blender (x,y,z) -> Roblox (-x,z,y)*3).
- Shapely staat in een venv in de scratchpad; opnieuw maken met `python3 -m venv ... && pip install shapely`.

## Lessen Sprookjesboom (12 nov, chat 3)
- Foto's eerst op kijkhoek controleren: front.jpg bleek ~20 graden van rechts genomen (gezicht 0.33 m links van het stamhart). `build/cam_match.py`
  rendert door de fotocamera (positie, yaw, lens) en legt de render over de foto; close-up van het gezicht is de eerlijkste check.
- Schors van de Sprookjesboom = blokplaten in golvende rijen (krokodillenhuid), geen ribbels/kasseien: Voronoi alleen langs de rij, rijgrenzen doorlopend.
- Mond/gaten: uitsnijden vóór de laatste remesh (strakke, gladde randen) + donker binnenvlak in de vorm van de opening.
- Bake: AO met de kruin in de scène wordt veel te donker; alleen het fijne AO-detail gebruiken (AO / vervaagde AO). Roblox: kleur 1024 px, AO in kleur.
- Export met gebakken textures: UV's behouden (`models/PR_Sprookjesboom/build/09_export_roblox.py`), niet de kubusprojectie van Villa Volta.
- Terrein: vlak maaiveld = voxels vol tot Y=0 en leeg erboven, rendert op Y=2. Smalle dingen (beek 1.5 m) niet in voxels (1.33 m) maken maar als mesh,
  terrein eronder leeg (vol tot Y=-4). Terreinbotsing wordt na WriteVoxels pas later bijgewerkt: task.wait() voor raycasts.
- Data-PNG: alpha-kanaal nooit 0 laten (groep = 200 + n).
- Geen zwevende tekst bij gebouwde dingen: na plaatsen het EftelingLayout-label (BillboardGui) met dezelfde naam verwijderen (Daan).
- UV van gebakken LOW-meshes: uitvouwen op de GLADDE vorm (vóór schors/ruis), anders duizenden piepkleine eilanden -> facetten in Roblox.
- Dieren/figuren: Roblox generate_mesh (AI, getextureerd) is veel gedetailleerder dan zelf geboetseerde bollen; Daan wil detail.
- Geul-mesh moet verder reiken dan de uitgegraven terreinvoxels (kolom + halve voxel 0.67 m), anders kuilen naast de geul.
