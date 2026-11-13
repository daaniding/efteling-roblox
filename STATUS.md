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
| Hans en Grietje v1 | 134881477873995 | VERVANGEN door v2 (models/AR_HansGrietje, nov 13) |
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

## Sneeuwwitje (chat 5, 12-13 nov) — v4 in Studio; nog: tunnelvloer/-wanden, wandeltest v4, interieur later
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
- v2 (Daan: niet mooi, stenen zitten niet goed in elkaar, missende texturen): grot opnieuw = hoogteveld binnen de OSM-vorm + twee rijen grove
  blokken langs de voorkant (icosphere sub 1 -> voxel remesh 0.09 -> weinig gladstrijken -> ribbel-plooien), ruinemuren als doorlopend metselwerk
  met getrapte breukrand, holle ruinetoren met raamgaten, klimop als bladplakkaten met de haagtextuur; baksteen lichter geel/roze gemeleerd.
  Kasteel+grot **120497972212126**, omgeving **132399062872581**. Tints: rots (245,245,218), ruine (205,200,200).
  v3 (Daan: klimop voor de ingang, stenen sluiten niet aan, gaten in de steen, pad niet vrij): klimop alleen nog op de toren; rots vol tegen de
  ruinemuren (randen langs de ruines tellen niet mee in het hoogteveld); tunnel naar het midden van de rots (aan de buitenkant brak hij open);
  nieuwe rotstextuur grijsgroen + mos, geen strepen; bloembak van voor de uitgangsdeur naar de zuidkant van het plein; perkaarde lichter.
  Kasteel+grot **86201030345062**, omgeving **99053383937028**. Wandeltest Play: hele route OK (ingang -> zaal -> gang -> ronde toren -> uitgang
  -> grotingang -> tunnel -> grotuitgang -> parkpad).
  Sneller werken (Daan: "het duurt elke keer zo lang"): `build/bouw_deel.sh grot|kasteel|omgeving` bouwt/bakt/upload alleen dat deel
  (05_bake --deel). Nog niet in gebruik: eerste keer moet plaats_sneeuwwitje.luau kasteel en grot als twee assets plaatsen.
  v4 (Daan: "nog meer gaten", gat tussen ronde toren en rechter kasteel, verhoging in het kasteel waar je doorheen loopt): weergang doorgetrokken
  tot de ronde toren + gevelvulling (geen kier meer), plint alleen aan de buitenkant en de torenring open bij de deuren (geen richel binnen),
  boogbankjes naar buiten; rots boven de tunnel altijd min. 0.95 m dik + uitloop bij de grotuitgang hersteld (geen gele vlakke wand).
  Kasteel+grot **117515855048104**, omgeving **72248096298132** (31 texturen geladen). Blender-klei-check tunnel/gang/achterkant: dicht.
  Studio: geen gaten, toren sluit aan. Terreingras prikte door de tunnelvloer -> terrein onder de tunnel Ground (in plaats_sneeuwwitje.luau).
- Valkuil: bouw_alles.sh met set -e stopt als een grep niets vindt (04 meldt 'omgeving'); wachtlussen niet op 'Error' laten matchen (staat in de scriptregel).
- LET OP: Studio herstartte tijdens het plaatsen (Assistant-plugin bijgewerkt). Als Sneeuwwitje/SneeuwwitjeGroen ontbreken: plaats_sneeuwwitje.luau
  + de plantentabel opnieuw draaien.

## Hans en Grietje (chat 6, 13 nov) — v1 staat in Studio; figuren Hans/Grietje komen later (Daan)
Map `models/AR_HansGrietje/`. Bronnen: 87 Eftepedia-plaatjes (herbouw 2024 = nagenoeg 2016, pannenkoeken hangen over de dakrand), OSM/BAG 50911615,
tuin 766787177, paadjes 766787178/9 (`ref/osm_model.json/png` in modelframe), brief `asset-brief.md`. front.jpg = Hghuis-vk.jpeg.
Model: gevel kijkt WNW (-Y), +X = ZZO; oorsprong midden BAG = studs (200.43, -82.44), kijkrichting Roblox (-0.944, 0, -0.332), grond Y=2.
Fotocamera: `cam_match.py --cam -0.3,-8.6,1.6,26 --sensor 25.4 --pitch 8 --res 1000x1000`. Review: `build/review.sh <map>`.
- Keten: `build/03a_atlas.py` (pannenkoek- en snoepatlas) -> `03_forms.py` (stucmassa, pannenkoekendaken, snoep, deur/luiken/tralies, steunbalken,
  taartlampen) -> `04_omgeving.py` (grindpad volgens OSM met splitsing, witte muurtjes links om de hoek en rechts langs het witte grindpad, leuning +
  tuinhek met kruk, binnenhek met krulpoortje, snoeppad, perken, 2 limonadefonteintjes, taarten/puddingen op pijlers, sprookjesboek, potten, oven,
  houtstapel, tegels voor de kooi) -> `05_bake.py` (stuc per gevel + tuin) -> `09_export_roblox.py`. Alles: `build/bouw_alles.sh`, dan
  `python3 roblox/maak_plaatsscript.py` en `roblox/plaats_hansgrietje.luau`; beplanting `roblox/plaats_hansgrietje_groen.luau` (HansEnGrietjeGroen,
  ~1040 planten: begonia's, bodembedekkers, 42 bomen, 95 heesters, ~390 varens/struiken tot ~25 m).
- Assets: huis **139382073870455** (83k tris), tuin **98956237263382** (23k); texturen in `textures/asset_ids.txt` (tuin-stuc 108259494727642 / 97917567891523).
- In Studio: HansEnGrietje (+ map Figuren: witte vogel op de stapel 117860705892867, zwarte vogel windvaan 83043200989950 via generate_mesh),
  HansEnGrietjeOmgeving, HansEnGrietjeGroen. Oude v1 weg, label weg, spawn op het grindpad voor het tuinhek. Wind + LantaarnsDagNacht doen mee.
- NIET gedaan: figuren Hans en Grietje (Daan: later; generate_mesh gaf chibi-poppen), heks achter het luikje en de kat (horen bij de show), animatie.
- v1.2 (Daan: hekjes langs de paden "zien er niet uit", het ging om het perceel): hekjes weer weg. Het perceel is nu rondom afgebakend met
  dezelfde lage witte muurtjes (ronde kap, 0.6 m): links door naar achteren, achter het huis langs, rechts langs het zijpad (OSM 55340110 =
  echt klinkerpad, tussen tuin en pad bosjes) en voor tot de puddingpijler (grindpad dicht). Eigen mesh `HO_muurrond__stuc` (lichter gedecimeerd,
  6.9k tris), onzichtbare botsblokken 2.6 m langs alle muurtjes (niet eroverheen springen). Omgeving **86649982613073**
  (tuin-stuc 97840886839892 / 105162864177043). Begonia's/perkplanten ontbraken in Studio (waarschijnlijk niet opgeslagen voordat Studio dicht ging): `plaats_hansgrietje_groen.luau` opnieuw gedraaid (begonia 352, binnen 50, linkerperk 110, bos 527). Review `review/06/sheet.jpg`; staat in Studio.
- Play-test 13 nov: Studio liep overal ~15 fps (ook bij Sneeuwwitje, venster niet vooraan); met de scène in beeld 12, zonder 15. Opnieuw meten als Studio vooraan staat.

## De Magische Klok (chat 7, 13 nov) — v2 in Studio: indeling volgens overzichtsfoto 2009 + OSM, met plein, herauten, klimop
Map `models/AR_MagischeKlok/`. Bronnen: 56 Eftepedia-plaatjes, lemma-tekst, OSM 55424253 (toren + 2 muurarmen), pleinpad 1169014962, lantaarnpunt;
plattegrond `build/01b_plan.py` -> `review/plan_osm.png`. Brief `asset-brief.md`. Vergelijking `review/vergelijking_v2.jpg`.
- Model: klok kijkt -Y (WNW), +X = ZZW, oorsprong = midden toren = studs (169.32, -159.75), kijkrichting Roblox (-0.855, 0, -0.518), grond Y=2.
- Indeling (Herauten-overzicht-okt2009, MagischeKloktotaal, Boekloc 2016): westmuur 3 herauten dicht bij de toren (s 2.8/5.3/7.8), gracht ALLEEN langs
  de westmuur (natuurlijk slootje), gras + rozenperk ervoor; noordmuur 3 herauten ver uit elkaar (3.8/8/11.8), strook planten, dan het Herautenplein:
  langwerpig evenwijdig aan de noordmuur, rond eind naar de toren (= gebogen muurtje Boekloc), grijze klinkers, laag bakstenen muurtje met grove
  afdekstenen, 2 openingen aan de graskant, 3 groene bankjes, buxushaag (haagtextuur); galgenlantaarn op het OSM-punt; sprookjesboek bij het ronde eind.
- Fotocamera front.jpg: `cam_match.py --cam 0,-30,1.6,55 --sensor 24 --pitch 3 --res 1000x665` (tele). Toren K=0.87, romp 4.07, klok 2.75..3.92.
- Keten: `build/bouw_alles.sh` = 03a_atlas (wijzerplaat, ruitertje, klimop) -> 03_forms -> 03b_heraut (6x, skin-modifier lichaam) -> 03c_klimop
  (7000 bladkaarten) -> 05_bake -> 09_export -> upload.sh; dan `python3 roblox/maak_plaatsscript.py` + `roblox/plaats_magischeklok.luau`
  + `roblox/plaats_magischeklok_groen.luau` (MagischeKlokGroen). Asset v2 **84133768551001** (112k tris, waarvan herauten 83k).
- Terrein: gras op het grasveld, Ground langs de muren; westgracht uitgegraven; oude kuil langs de noordmuur hersteld met WriteVoxels (Ground 1/1/0).
- LET OP: Mud heeft in deze place een MaterialVariant VV_Bosgrond (felgroen) -> geen Mud gebruiken. Herauten-generatie via generate_3d kon niet
  (geen generator-sleutels in de Blender-addon); ze zijn zelf gemodelleerd.
- v3 sfeer/bos (Daan): `roblox/plaats_magischeklok_bos.luau` -> workspace.MagischeKlokBos: 23 bosreuzen (beuk/eik/kastanje schaal 4-5.4 = 20-27 m)
  achter de muren en rond het pleinvierkant, 45 rododendron/taxus, 110 varens, 90 bodembedekkers, rand heesters buiten het pad; grasveld LeafyGrass
  (Grass = VV_Gazon, te strak), plein grijs grind (Pebble: Cobblestone = EftelingKlinkers rood). 'struik'-modellen niet gebruiken (kale sprieten).
  Screenshots `review/studio_v3_*.jpg`.
- v4 herauten (Daan): gezicht gemodelleerd (oogkassen, wenkbrauwboog, neus, jukbeenderen, lippen, kin; ogen in de kassen), handen met 4 vingers
  + duim (links in de zij, rechts om de trompet), 22 haarlokken (bob), kreukels in de mouwen, diepere rokplooien. Asset **76477453584742**
  (154k tris, herauten ~21k per stuk). Render `review/06/heraut_sheet.jpg`, Studio `review/studio_v4_herauten.jpg`. Place opgeslagen (versie 92, voor v4).
- Toegang plein: twee openingen (1.6 m) in muurtje en haag aan de graskant (s 4.9-6.5 en 8.7-10.3 langs de noordmuur), klinkerstrook erdoor.
  Wandeltest in Play (Humanoid:MoveTo): gras -> haag -> muur -> plein -> tweede opening -> gras, en naar het ronde eind: alles OK. Haag botst precies
  (PreciseConvexDecomposition, anders kan Roblox de openingen dichtplakken). Er loopt nog geen pad van het OSM-pad naar de openingen (paden later).
- v5 grasoevers (Daan): `roblox/plaats_magischeklok_oever.luau` -> MagischeKlokOever: grachtstrook LeafyGrass, 260 riet/siergras op de waterranden,
  70 varens + 120 bodembedekkers op de oevers en tussen de sokkels, 40 kroosplekken (SprookjesboomWater.Kroos), 100 donkere ronde blaadjes.
  Screenshot `review/studio_v5_oever.jpg`.
- v6 plein opnieuw (Daan: "ziet het plein er echt zo uit?" -> nee): naar MagischeKloktotaal + overzicht-okt2009 + Boekloc: grindband langs beide
  muren (t 2.6..7.5) met achter een laag muurtje van ruwe natuursteen (bocht om de toren, uitloop in de gracht), voor een buxushaag in chevron
  evenwijdig aan het pad met lange lage groene bankjes erachter, 4 rieten manden, galgenlantaarn op de hoek bij de open noordingang, ingang west
  tussen haag en grachtmuurtje, rozenperk voorbij het westeinde. Asset **133609116330457**. Render naast de foto `review/plein_v3_vs_totaal.jpg`.
  In Studio geplaatst: asset **71191317351708** (dakonderkant bewaard in 05_bake: van dichtbij keek je door het dak). 111 planten van het plein weg,
  48 rozen in het nieuwe perk. Wandeltest Play: noordingang -> grind -> bocht bij de toren -> manden -> westingang -> gras -> terug: alles OK.
  Screenshot `review/studio_v6_plein.jpg`.
- v7 paden (Daan): OSM 1169014962 (V om het pleinvierkant, ~10.6 m voor de muren) + 967458491/490 (doorgang Prinsenpoort), 3.2 m, mesh
  'padklinker' = Cobblestone -> EftelingKlinkers (zoals de parkpaden). Asset **124674002080571**. 19 planten van het pad weg. Wandeltest: pad west ->
  knik bij de haag -> pad noord -> Prinsenpoort -> over het gras het plein op: OK. Tussen pad en pleiningangen ligt gras (OSM heeft daar geen pad).
- v8 (Daan): ALTIJD grind (Pebble + VV_Grind, kleur 235,228,214 = het lichte grind van Sneeuwwitje/Assepoester/Villa Volta), geen tuin, geen haag, geen manden, geen V-pad. Grind = het plein + een randpad
  langs de herauten: west langs de gracht (t 2.35..5.4) tot sW 22, noord langs de verhoogde strook tot voorbij de Prinsenpoort + de doorgang.
  Herauten op een verhoging: noord begroeide strook achter het keermuurtje (0.42 m), west grasoever boven de gracht (0.30 m); sokkels/herauten mee omhoog.
  Loopvlakken: bovenkant naar boven (omhoog()), 10-11 cm boven maaiveld (anders prikt bladgras erdoor). Vrijgekomen grond = bos (geen bomen of hoge
  struiken in het zicht voor het plein). Asset **95617904563293**. Wandeltest randpad west -> plein -> randpad noord -> Prinsenpoort: OK.
  Screenshot `review/studio_v8_randpad.jpg`.
- v9 (Daan): stenen rand doorgetrokken tot het eind van beide kasteelmuren en daar tegen de muur afgesloten (west langs de gracht tot sW 17.75,
  noord langs de verhoogde strook tot sN 14.75); verhoogde strook noord op volle hoogte tot de eindrand. Asset **85276771159667**
  (`review/eindranden.jpg`). Grind 235,228,214 zoals Sneeuwwitje. Nog te plaatsen als Daan uit Play is.
- v10 (Daan: "je hebt water toegevoegd maar dat moet gras zijn"): GEEN gracht meer. Westkant = dezelfde verhoogde begroeide strook (0.42 m) als noord,
  achter het doorgetrokken stenen randje; herauten west ook op 0.42. MagischeKlokOever (riet/kroos/blaadjes) verwijderd, strook west beplant (150).
  Asset **108564933546713**. Screenshot `review/studio_v10.jpg`. (Het grachtterrein onder de strook is nog uitgegraven; de strook dekt het af.)
- v11 (Daan: "Magische Klok afmaken"): **torentje** aan het eind van de westmuur naar Magischeklok1976 (rechts) + Herauten-okt2009: vierkant
  ruw stuc 1.6 x 1.6 m, lijst op 3.15 m, vier hoekkantelen tot 3.7 m (~0.8 m boven de muurkantelen), botsblok in COLL. **Slimme Toon** opnieuw
  (`build/03d_toon.py`, na 03b in bouw_alles.sh): skin-modifier-figuur x1.35 (~0.42 m zittend), zit op een eigen loden zitkrul links van de klok,
  voor de stijl linksvoor, kijkt opzij naar de klok (vanaf het plein in profiel zoals Slimme-Toon.jpg), trekt met beide handen aan het touw;
  groen jak met rode puntkraag en riem, rode maillot, zwarte puntschoenen, blond pagekopje, grijsgroen hoedje met rode krulveer (MAT toon_hoed).
  Asset **134679544462063**. Geplaatst zonder terreinstappen (alleen model + botsing + texturen voorladen). Screenshots `review/studio_v11_*.jpg`.
- v12 herauten (Daan: "ja, alle vijf"), naar Intro_magischeklok + MagischeKlokheraut: zachte zwarte baret op het hoofd met band en een dikke
  rozet van gekrulde donkerrode veren; vol golvend blond haar tot op de kraag (32 lokken); grote geschulpte kanten kraag + wijde kanten manchetten;
  medaillon groter met klimmende leeuw; trompet met grote beker + ring; vaandel hangt recht onder de trompet: paars met gouden leeuw (beide kanten),
  brede oranje rand, donkere franje, stok en oranje lussen; wandschildjes met echte Franse lelie en brede gouden rand. Nieuwe MAT oranje/franje,
  vaandel nu paars (62,34,96). Herauten ~31k tris per stuk (asset 238k). Asset **107392453250241**. `review/v12_heraut_vs_foto.jpg`, `review/studio_v12_heraut.jpg`.
- NOG/kan beter: gezicht nog stijf (glimlach, oogleden), pluim meer als één krullende veer,
  Prinsenpoort (aparte attractie) ontbreekt links.

## Daarna (volgorde met Daan afgesproken)
1. Villa Volta (KLAAR). 2. Sprookjesboom + paddenstoelen (KLAAR), Langnek (KLAAR, statisch), Assepoester (KLAAR, interieur later). 3. Lantaarnpaal/bankje/prullenbak. 4. Gijs afmaken. Hans en Grietje: figuren later (huis + tuin KLAAR v1).
5. Park terugzetten en mooier (den-lagen, kleinere bladkaarten, gras/bosgrondtexturen, opsluitbanden, oevers). 6. Grote gebouwen (entree, Symbolica).
Kaatsheuvel eromheen: later.

## Geïnstalleerde skills (in ~/.claude/skills)
blender-image-to-3d (kern), blender-cinematic-modeling, blender-core, blender-texturing, blender-texture-baking, blender-asset-qa,
blender-export-pipelines, blender-hardsurface-modeling, blender-retopology-uv, blender-game-optimization, blender-environment-kits,
blender-pipeline-automation, roblox-animation, roblox-texture-gen, roblox-vfx, roblox-3d-model, roblox-skills-setup.
