# Efteling in Roblox — status en overdracht (12 nov 2026)

**Nieuwe chat: lees eerst WERKWIJZE.md (lessen + Daans wensen) en dan dit bestand. Werk na elke stap STATUS.md en het geheugen bij.**

Lees dit eerst in een nieuwe sessie. Repo: https://github.com/daaniding/efteling-roblox

## Doel en kwaliteitslat
Daan bouwt de Efteling realistisch en op schaal na in Roblox, met modellen uit Blender. De lat ligt hoog:
procedurele blokkeringen worden afgekeurd. Werkwijze die wél werkt (skill `blender-image-to-3d`):
foto's → maatbrief (`asset-brief.md`) → blokkering naast de foto → vormen → export → Studio. Pas tonen als een
render naast de foto standhoudt. Liever iets kleins perfect dan iets groots half.
Usage sparen: foto's verkleind bekijken (`sips -Z 700`), één vergelijkingsblad per fase, geen losse screenshots.

## Schaal en coördinaten
- 3 studs = 1 m. Oorsprong (0,0) = midden park (51.6500 N, 5.0455 E). Roblox X = OSM-oost (m×3), Z = −OSM-noord (m×3).
- Blender: meters, Z op, voorkant −Y. FBX komt in Roblox binnen als 1 unit = 1 stud → `Model:ScaleTo(3)`. Blender −Y wordt Roblox −Z.
- Alle footprints/posities: `reference/data/efteling_objecten_meters.csv|json`, OBJ-blauwdruk `efteling_footprints.obj`.

## Pijplijn (werkt)
- Blender headless: `/Applications/Blender.app/Contents/MacOS/Blender --background --python <script> -- --master <blend>`.
  De Blender-MCP valt weg zodra een script een nieuw bestand opent; headless is betrouwbaar. Absolute paden gebruiken.
- Upload: `tools/upload_asset.sh <bestand> "Naam" "Omschrijving" Model|Image|Decal` via `zsh -ic` (sleutel ROBLOX_API_KEY in ~/.zshrc, nooit printen).
- Studio: Roblox Studio MCP (`execute_luau`). Invoegen met `game:GetObjects("rbxassetid://ID")`, dan `ScaleTo(3)`, kleuren/materialen op naam (`MAT_*`).
- Export per materiaal in stukken ≤ 9000 driehoeken: zie `models/CH_HolleBolleGijs/build/09_export_roblox.py` (groepeert op `anim__MAT`).
- Grote data naar Studio zonder HTTP: in PNG coderen (2 RGBA-pixels per record), uploaden als Image, lezen met
  `AssetService:CreateEditableImageAsync` + `ReadPixelsBuffer`. HTTP naar 127.0.0.1 wordt door de Assistant-allowlist geweigerd.
- Texturen: `SurfaceAppearance` (ColorMap = Image-asset); terrein: `MaterialService` MaterialVariant + `SetBaseMaterialOverride`.

## Wat er staat (Roblox-assets)
| Wat | Asset-id | Staat |
|---|---|---|
| Entreegebouw (Huis v.d. Vijf Zintuigen) blokkering | 128928417227160 | placeholder, afgekeurd, later opnieuw |
| Hans en Grietje v1 | 134881477873995 | scriptmatig, afgekeurd als eindniveau; .blend in `models/HansGrietje_wip.blend` |
| Holle Bolle Gijs v2 (huisje + Gijs + animatie) | 133621430486686 | goedgekeurd als richting; animatie in `models/CH_HolleBolleGijs/roblox/GijsAnimatie.server.luau` |
| Bomen v2 (zwaar) | 110183678792616 | 5 soorten + 3 struiken met texturen |
| Bomen v3 (licht) | 131773367492573 | zelfde look, helft driehoeken |
| Boom-texturen (12) | zie `park/trees/v2/asset_ids.txt` | blad/naald met alpha, schors |
| Klinkers visgraat kleur/normaal/ruwheid | 127799853003036 / 90400093022626 / 111212196344944 | MaterialVariant "EftelingKlinkers" op Cobblestone |
| Boom- en struikposities als data-PNG | 108552680128597 | 15.805 records |

In Studio (place 126519985893990, "Place2") staan nu: Gijs, Hans en Grietje, entree-blokkering, gedimde layout-markers
(`EftelingLayout`, 316 stuks), vlak grasterrein. Park (terrein, bomen, hagen) is op Daans verzoek weggehaald: eerst de dingen maken.
Het park is in 1 minuut terug: `park/park_raster.py` → ServerStorage.ParkBuilder (Terrain) + BomenPlaatser (bomen via data-PNG).

## Gijs: wat nog beter moet
Mond groter/natuurlijker, blos minder als schijfjes, den-achtige krullen oké; figuur op het dak + lantaarn + gotisch bord ontbreken;
geluid "Papier hier!" ontbreekt (Sound-objecten SndRoep/SndEet staan klaar in MouthHole).

## Villa Volta (v4: maten uit OSM + DRDB-plattegrond, zijgevel en rij naar foto's)
Bronnen in `models/AR_VillaVolta/ref/`: `drdb_plattegrond.jpg` (Dark Ride Database 2022: hele gebouw van boven: terras, uitgang,
rij, voorshows, tourniquet), `drdb_tekening_buiten.jpg` (vroege tekening Ton van de Ven), `eftepedia_wachtrij_2022.jpg`, zijfoto
`Villa_Volta_DSCF5860_JPG.jpg` (oostkant), `osm_lokaal.json` (alle OSM-punten in modelcoordinaten).
DRDB-maten: hoofdgebouw ~20 m diep, 14 m breed, ~14 m hoog; achterbouw ~10x16 m, half zo hoog; trommel zeskant 10.8 m, schommel 4x20.
Gekozen (meters, oorsprong midden gevel risaliet): risaliet 7.8 breed, 5.5 diep, 3.15 voor de vleugels; hoofdgebouw x +-6.75 tot y=18.5;
achterbouw x -9..6.85, y 18.5..31.2, 6.2 hoog. Hoogtes uit front.jpg (deur 3.0 m): kroonlijst 8.6, nok 10.75, beeld tot 12.7 boven maaiveld
(DRDB zegt ~14 m: verschil niet opgelost, foto aangehouden).
- Gevel kijkt ZZW naar het Ton van de Venplein. Oorsprong = studs (365.9, 1.95, -1005.3), draaiing 169.5 graden, grond Y=2.
- Villa v4 **136382357585295**, tuin + wachtrij v4 **111180154136708**. Plaatsen: `roblox/maak_plaatsscript.py VILLA OMG` maakt
  `roblox/plaats_villavolta.luau` (template `plaats_template.luau`), plakken in Studio (HTTP naar GitHub is geblokkeerd).
- Wachtrij zoals Eftepedia-foto 2022: overdekte galerij tegen de oostgevel, dichte stucmuur met 4 bokkenhuiden in houten lijst,
  open zuilengang op lage borstwering met vaasjes op de dakrand, wit plafond met ronde lampjes, rode klinkers, grijsgroene hekken met bol,
  groene afvalbakken met gouden bies, RVS-tourniquets voor de dubbele deur, perkament met dolk; ingangsgang met lage witte muurtjes (plattegrond).
- Z-fighting: paden elk eigen hoogte, haag/muurstukken verspringen 12 mm, hoekblokken/postamenten/pilasters niet meer samenvallend.
- Rij verbreed voor Roblox-schaal (Daan: benauwd): galerij 8.9 m, banen 1.6 m, plafond 3.9 m, haag buiten 1.4 m; afvalbakken uit de looproute.
  Laatste assets: villa **99373517894794**, omgeving **134354426343629** (paden als meshes met opsluitbanden, open lantaarns, UV's). Paden + plein zijn terreinmateriaal, bomen/struiken in `VillaVoltaGroen`, licht ingesteld:
  zie `models/AR_VillaVolta/roblox/README_studio.md`.
- Villa Volta buitenkant AF volgens Daan (12 nov): symmetrische tuin, echte plantscans, haag met diepte, CC0-texturen; zie roblox/README_studio.md.
- Interieur komt pas als heel de Efteling staat (Daan). Plein (Ton van de Venplein) ook later. Nu: meer detail/realisme buiten.

## Huidige stand (einde chat 12 nov)
Villa Volta buitenkant KLAAR volgens Daan. Open bij Villa Volta: geluid (later), interieur (later), prestaties testen in Play.
Volgende chat: de volgende attractie uit de lijst hieronder (Sprookjesboom + paddenstoelen of Langnek), met dezelfde werkwijze.

## Sprookjesbos: reliëf + Sprookjesboom (12 nov, chat 3)
Daan koos de Sprookjesboom. Alleen het object (boom, paddenstoelen, grond), nog geen show/geluid/bewegende ogen.
- Reliëf uit **AHN4 DTM 0,5 m** (PDOK, CC0): `park/relief/` (script, `hoogte_lokaal_mm.png` = mm NAP per 1 m, x -150..300, y -150..330).
  Sprookjesbos zacht aflopend 9,3 (zuid) -> 8,2 m NAP (noord), mediane helling 3 gr, lokaal steile wallen. Rond de boom vlak, beekje ervoor.
  **Nog niet in Studio-terrein** (terrein is vlak Y=2).
- **Sprookjesboom v1 staat in Studio** (`Workspace.Sprookjesboom`), map `models/PR_Sprookjesboom/` (asset-brief.md = alle maten).
  Bronnen: Eftepedia 9 m hoog, 13 m breed; foto's ref/front.jpg (camera ~20 gr rechts van het gezicht!), front_wide.jpg (hele boom), front_high.jpg.
  Kijkt naar het zuiden (+Z) naar het pleintje met bankjes; OSM-stamhart (40.48, 198.19) m = studs (121.44, -594.57).
  Pijplijn: `build/02_blockout.py` -> `03_forms_stam.py` (stam als loft met wortellobben, gezicht gesculpt, schors = Voronoi-platen in rijen,
  mond/gaten uitgesneden, ogen met ooglidschillen, neus = takstomp met jaarringen) -> `03_forms_kruin.py` (takken + bladkaarten)
  -> `04_low.py` (26k tris) -> bake_maps (2048 normal/ao/kleur/ruwheid) -> `09_export_roblox.py` (UV's behouden) -> `roblox/maak_plaatsscript.py`.
  Review: `build/cam_match.py` rendert door de fotocamera en legt de render over de foto (`review/03`, `review/05`).
- Assets: boom **119271916330812** (stam 3 delen + takken + blad + ogen + holtes, 38k tris), stamtextures kleur **71879589522107**,
  normaal **122522185781721**, ruwheid **90259338261512**; takken schors_eik 99288067092575; blad = goedgekeurde bladtros 136241132523803.
  Paddenstoel klein **125821121621263** (12 rond de voet, x1.4), muzikale paddenstoel **76565275730007** (18 OSM-plekken, Y=2). Ids: `roblox/asset_ids.json`.
- **Omgeving staat** (Daan: "water tussen pad en boom, plantjes erachter, boompjes"): `build/06_omgeving_data.py` (shapely-venv) leest OSM ->
  `exports/omgeving_data.json` -> `06_omgeving.py` (Blender: plein+paden 3.4 m met opsluitband, geul als hoogteveld + water op -0.32 m,
  wortel de oever in + wortel met klauwen aan de pleinkant (front_wide.jpg), 7 lage bankjes (OSM, zonder rugleuning), rieten prullenbak)
  -> asset **121627114001594**; keien 6 prototypes **83462996132840**; posities als data-PNG **101104526038282** (`07_data_png.py`).
  Studio: `roblox/plaats_omgeving.luau` (terrein onder de geul leeg, 900 oeverstenen/keien, 2259 planten uit VVEchtePlanten + BomenBronV3
  rododendrons/taxus, 8 OSM-horizonbomen in de weg -> ServerStorage.SprookjesboomWeggehaald). Beek uit OSM is een smalle waterloop (1.45 m)
  die om het pleintje kronkelt en recht voor de boom langs loopt.
- Open punten Sprookjesboom: mond iets kleiner dan foto; gat rechts leest als gleuf i.p.v. ronde ring; blad = netelvormige tros (echte eikentros
  renderen = Poly Haven-download, eerst vragen); gezicht staat in de kruinschaduw (zonnestand/licht); beekje met rotsige geul + wortels erover
  naar het pad, rododendrons erachter, (beek/plein/bankjes/planten staan nu); nog: tonderzwam-roeptoeter op de wortel, dieren (eekhoorn, specht), stoomtreinspoor achter de boom, reliëf van heel het Sprookjesbos in het terrein.

## Daarna (volgorde met Daan afgesproken)
1. Villa Volta afmaken (KLAAR). 2. Sprookjesboom + paddenstoelen (v1 staat), Langnek. 3. Lantaarnpaal/bankje/prullenbak. 4. Gijs afmaken.
5. Park terugzetten en mooier (den-lagen, kleinere bladkaarten, gras/bosgrondtexturen, opsluitbanden, oevers). 6. Grote gebouwen (entree, Symbolica).
Kaatsheuvel eromheen: later.

## Geïnstalleerde skills (in ~/.claude/skills)
blender-image-to-3d (kern), blender-cinematic-modeling, blender-core, blender-texturing, blender-texture-baking, blender-asset-qa,
blender-export-pipelines, blender-hardsurface-modeling, blender-retopology-uv, blender-game-optimization, blender-environment-kits,
blender-pipeline-automation, roblox-animation, roblox-texture-gen, roblox-vfx, roblox-3d-model, roblox-skills-setup.
