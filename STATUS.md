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

## Huidige stand (einde chat 5)
Villa Volta, Sprookjesboom, Langnek (statisch) en Assepoester (buitenkant + route) KLAAR. Aansluitingen (paden, hek naar de Kleyne Klaroen) komen
met de paden van het Sprookjesbos. Volgende: zie 'Daarna'.

## Stand einde chat 3, 12 nov
Villa Volta buitenkant KLAAR. **Sprookjesboom + scène KLAAR** (zie sectie hierboven en `models/PR_Sprookjesboom/`).
Later (Daan): geluid/show, paden door het park, eventueel StreamingEnabled (prestaties).
**Volgende chat: de Langnek** — alleen de Langnek + scène direct eromheen, eerst Eftepedia-foto's, zelfde pijplijn
(asset-brief -> blokkering naast foto -> vormen -> LOW + bake -> export -> Studio -> scène -> close-ups + Play-test -> tips vastleggen).

## Langnek (chat 4, 12 nov) — KLAAR (statisch, nek uit zoals de foto)
Map `models/CH_Langnek/`. Bronnen: Eftepedia-lemma Langnek (`ref/eftepedia/`), OSM rots + vijver (`ref/osm_lokaal.json`), brief `asset-brief.md`.
Bouw: `build/02_blockout.py`, `03a_forms_figuur.py` (figuur), `03b_forms_rots.py` (rots, vijver, randstenen, keien, hekje), `09_export_roblox.py`.
Roblox-asset v2 **116930509474793** (gebakken texturen via `build/04_bake.py`: lijf 98796211691962, hoofd 101183919857164, nek 109436001826060, rots 114370744521597, rand 123245105248243; v1 106939403351913 (88.8k tris, 28 meshdelen, anim-groepen body/neck/head/irisL/irisR/static in de namen).
Plaatsen: `roblox/plaats_langnek.luau` (kleuren, water, kroos/rimpels, beplanting in `LangnekGroen`, wind). Play-test: 43 fps met / 46 zonder.
Oude Langnek uit losse Studio-parts is vervangen. Layout-label weg.
NIET gedaan (Daan: nog niet animeren): `roblox/LangnekAnimatie.server.luau` ligt klaar (nek schuift als geheel, hoofd/ogen los), niet geplaatst.
v2 (Daan: "veel mooier"): gezicht naar foto (bolle ogen met huidring, open grimas, rimpels, kijkt 25 graden omlaag), geschilderde bake (AO, blos, stof, betonscan + mos), extra bos erachter (57 planten).
v3 (Daan): keien weg, klinkerpad (~5 m breed) in een boog voor de vijver met opsluitband, spawn op het pad (oude plek in attribuut
SpawnLocation.OudeCFrame), rots met normal map van de hoge rots (zacht gemaakt), bomen dichtbij naast het pad (61 planten totaal).
Model v3 **90664955604649**; texturen lijf 104740173738608, hoofd 129806446727609, nek 91441792849484, rots 90579127698807 (+normaal 109618118831941), rand 74303124237918.
v4 (Daan, naar de foto's): vijver loopt ~50 graden verder om de rots, pad alleen recht voor Langnek (~3.5 m), veel dichter bos
(26 dennen, 12 loofbomen, ~20 struiken, ~120 varens/ondergroei; kleine planten zonder schaduw: 49 fps met / 54 zonder).
Omgevingsasset **80458281867517**; draai `roblox/plaats_langnek_v4_omgeving.luau` na `plaats_langnek.luau`.
v5 (Daan: cape, gezicht, nek): nek 4.8 m (Eftepedia), gezicht minder cartoon (oogleden/wallen, neus en lippen mee in de huid
gesculpt, wijd open ogen, open grimas met dikke onderlip), cape met zware golvende zoom + lange plooien + dikke omgeslagen kraag,
plooien in rok/mouwen/boven de riem. Figuur-asset **128729459556621** (lijf 138231693611234, hoofd 127597747578678, nek 96605081719069);
in Studio alleen de delen met Groep body/head/neck/iris vervangen (export `--alleen BAKE_lijf,BAKE_hoofd,BAKE_nek,...`).

## Assepoester (chat 5, 12 nov) — KLAAR (buitenkant, tuin, beloopbare route); interieur later
Map `models/AR_Assepoester/`. Bronnen: 53 Eftepedia-plaatjes (`ref/eftepedia/`), BAG/OSM-footprint + omgeving (`ref/osm_lokaal.json`,
`ref/osm_overzicht.png`, gemaakt met `build/01_osm_lokaal.py`), brief `asset-brief.md`. Primaire foto `ref/front.jpg` (= Assevoorgevel.jpg).
- Gevel kijkt WEST (10.6 graden naar ZW gedraaid); main-ingang NW, uitgang ZW. Model: -Y = west, +X = zuid, y=0 = voorkant portiek.
  Oorsprong OSM-meters (4.08, 97.11) = studs (12.24, -291.34) is het midden van de BAG-footprint (NIET de modeloorsprong; omrekenen bij plaatsen).
- Blokkering `build/02_blockout.py`, overlay `build/cam_match.py` met `--cam 0.07,-299.1,1.6,1061 --pitch 0.37 --res 1000x665`
  (front.jpg is vrijwel zonder perspectief: vleugel en hoofdhuis hebben dezelfde px/m). Review: `review/02/sheet_02_blockout.jpg`.
- Conflict: hoofdhuis/toren/portiek staan op de foto 0.6 m zuidelijker t.o.v. de entreevleugel dan BAG -> foto aangehouden.
  Hoofddak: dakrand op 6.5 m (foto) -> steile kraag met plat bovendak (inferred). Toren x 2.42..5.19, spits tot 7.65, makelaar 8.0.
- Vormen `build/03_forms.py` (pannenrijen als zaagtand via tiled_roof(), rondboogramen met omlijsting/glas-in-lood/luiken, kuifjes,
  kroonlijsten, dakkapellen met makelaar, plankengordijn op plint, portiek). Review `build/review.sh 03` -> `review/03/sheet.jpg`.
- Export `build/09_export_roblox.py` (kopie Villa Volta): v1 **108022246144519** (11k tris, 13 delen). Plaatsen: `roblox/plaats_assepoester.luau`
  (MaterialVariants VV_Pleister/VV_Steen hergebruikt; pannen = ClayRoofTiles (150,92,72)). Layout-label weg, spawn op de binnenplaats.
- In de buurt staan VillaVoltaHorizon-bomen; 4 staan op de binnenplaats (den/beuk, model y -10..-4) -> weghalen bij de scène.
- v2 (Daan: "ziet er niet echt uit", tuin erbij, je moet naar binnen kunnen):
  * Binnenroute volgens OSM-voetpad 1255787234: entree (rondboog verbreed naar 1.45 x 2.38 voor spelers) -> hal in de vleugel ->
    gaanderijgang (plankenwand, schuin plankenplafond, balken, wandlampjes, 3 kijkramen) -> portiek -> buiten. Keuken alleen door de ramen.
    Botsing = onzichtbare COLL_-blokken (huis_extra.json / omgeving_extra.json), meshes botsen niet. INTERIEUR KOMT LATER (Daan): keuken is basis.
  * Tuin `build/04_omgeving.py`: klinkerbinnenplaats, middenperk met buxusrand + lantaarns, taxushagen langs OSM, tuiningang met
    vaaspijlers + smeedijzeren hek, dienstpoort, grafje met vleugels, kisten, boekstandaard, pompoenen, uitgangspad met galgje-lantaarn,
    rotsjes en stucboog in het parkhek. Omgeving-asset **112815934285553**.
  * Verwering `build/05_bake.py`: 10 texturen (stuc per gevel, pannen, groen, omlijsting, plint) + normal maps, ids in textures/asset_ids.txt.
    Huis v2 **118744140638270**. Tint achteraf via SurfaceAppearance.Color (TINT in plaats_assepoester.luau).
  * Beplanting `build/06_planten.py` -> workspace.AssepoesterGroen (277: rozen in het perk, paars bij het grafje, varens/heesters/rododendrons,
    16 bomen); toegevoegd aan Wind-MAPPEN. LantaarnsDagNacht doet nu ook Assepoester + AssepoesterOmgeving.
  * LET OP: haagtextuur 107834399804087 rendert wit (ook bij Villa Volta!). Opnieuw geupload: kleur 73997585762296, normaal 114509386598524.
  * v3 (Daan): gat in de achterwand van het portiek dicht, portiekdak overlapt de gaanderij niet meer (flikkerde), haag rond het
    dienstplaatsje doorgetrokken tot de vleugel, ondergrond = wit grind (Pebble + VV_Grind, 235,228,214). Huis **90187101137664**,
    omgeving **107962207315554**. Hele keten: `build/bouw_alles.sh` (03 -> 04 -> 05 bake -> export -> upload) en dan
    `python3 roblox/maak_plaatsscript.py` (vult ids in) en `roblox/plaats_assepoester.luau` in Studio.
  * Wandeltest in Play (Humanoid:MoveTo): tuinpoort -> entree -> hal -> gang -> portiek -> buiten -> uitgangsboog -> parkpad: alles OK, 52 fps.
  * EftelingLayout-labels (255) stonden AlwaysOnTop met bereik 600 -> door muren zichtbaar. Nu AlwaysOnTop uit, MaxDistance 150.
  * v4 (Daan): de muur aan het eind van de gang (laatste 1 m tot het portiek) was nooit uitgesneden -> nu open; je loopt rechtdoor het
    portiek in en naar buiten. Een per ongeluk gemaakte deur in de zuidmuur van het portiek is teruggedraaid. Huis **79510654585922**,
    omgeving **125652696529990**. EftelingLayout-labels staan weer zoals ze waren (AlwaysOnTop, 600).
  * Interieur (keukenscène, figuren, geschilderd doek) komt later (Daan).
  (binnenplaats met klinkers, buxusperk + lantaarns, hagen, hekpijlers met vazen, dienstpoort, grafje, kisten, pompoenen, boekstandaard).

## Sneeuwwitje (chat 5, 12 nov) — in Studio gezet (kasteel + grot + plein + beplanting); nog: wandeltest + close-ups
Map `models/AR_Sneeuwwitje/`. Bronnen: 74 Eftepedia-plaatjes, OSM (Kasteel Sneeuwwitje 60095998 + grot 60095997, rotsen, entrances), brief `asset-brief.md`.
Model: gevel kijkt OOST (-Y, 13.3 graden naar ZO), +X = noord; omrekening in `ref/model_frame.json`. front.jpg = Sneeuwwitjekasteelzomer.jpg,
overlay `build/cam_match.py --cam -0.35,-39.5,1.6,121 --pitch 3.9 --res 1000x665`. Route: kasteelingang (zuid) -> spiegelzaal -> uitgang ronde toren
-> grotingang (ruinemuur) -> tunnel langs de glazen kist -> grotuitgang. Straatmeubilair: later (Daan), refs in models/PR_Straatmeubilair/ref.
- Vormen: `build/03_forms.py` (kasteel; spitsbogen, kegeldaken met pannenrijen, uitgekraagde torentjes, kantelen, boogfries, schilden),
  `build/03b_grot.py` (kunstrots = blokken + voxel remesh + naden, boogtunnel langs de buitenbocht, ruinemuren + ruinetoren met klimop;
  eigen owner-tag phase:03b_grot), lage ruinemuur verbindt de ronde toren met de grotingang (Daan: "zitten de stenen en het kasteel niet aan elkaar").
  `build/04_omgeving.py` (wit grind plein + OSM-paden als strook, perken 505382907/908, bloembak, potten, boekstandaard).
  `build/05_bake.py` (baksteen per gevel met metselverband, steen, pannen, rots a/b, ruine). Keten: `build/bouw_alles.sh` + `roblox/maak_plaatsscript.py`.
- Assets: kasteel+grot **110658384004768** (46k tris, 100+ COLL_), omgeving **120339991780257**. Plaatsen: `roblox/plaats_sneeuwwitje.luau`
  (oorsprong studs (-75.65, 2, -167.32), kijkrichting (0.9731, 0, 0.2306)); beplanting `build/06_planten.py` -> workspace.SneeuwwitjeGroen (344).
  Wind + LantaarnsDagNacht doen ook Sneeuwwitje. Label 'Sneeuwwitje'/'Kasteel Sneeuwwitje' weg, spawn op het voorplein.
- LET OP: Studio herstartte tijdens het plaatsen (Assistant-plugin bijgewerkt). Als Sneeuwwitje/SneeuwwitjeGroen ontbreken: plaats_sneeuwwitje.luau
  + de plantentabel opnieuw draaien.

## Daarna (volgorde met Daan afgesproken)
1. Villa Volta (KLAAR). 2. Sprookjesboom + paddenstoelen (KLAAR), Langnek (KLAAR, statisch), Assepoester (KLAAR, interieur later). 3. Lantaarnpaal/bankje/prullenbak. 4. Gijs afmaken.
5. Park terugzetten en mooier (den-lagen, kleinere bladkaarten, gras/bosgrondtexturen, opsluitbanden, oevers). 6. Grote gebouwen (entree, Symbolica).
Kaatsheuvel eromheen: later.

## Geïnstalleerde skills (in ~/.claude/skills)
blender-image-to-3d (kern), blender-cinematic-modeling, blender-core, blender-texturing, blender-texture-baking, blender-asset-qa,
blender-export-pipelines, blender-hardsurface-modeling, blender-retopology-uv, blender-game-optimization, blender-environment-kits,
blender-pipeline-automation, roblox-animation, roblox-texture-gen, roblox-vfx, roblox-3d-model, roblox-skills-setup.
