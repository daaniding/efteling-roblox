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

## Checklist VOOR je iets aan Daan laat zien (uit Sneeuwwitje v1-v4: dit moest elke keer achteraf; nu meteen goed doen)
**Texturen**
- Vanaf de eerste versie gebakken texturen per materiaalrol (05_bake): baksteen met metselverband per gevelrichting, steen, pannen, rots, ruine.
  Nooit kale Roblox-materialen opleveren ("het mist textures").
- Na het plaatsen texturen voorladen (Decals + PreloadAsync) en wachten tot alles geladen is (Success = aantal texturen) vóór de screenshot.
- Rots: grijsgroen met mos/korstmos, geen golvende strepen of lagen, AO-vloer ~0.3; tint wit laten (kleur zit in de textuur).
- Baksteen licht geel/roze gemeleerd zoals de foto; binnenkant donkerder tint. Oude textuur rendert wit -> opnieuw uploaden.
**Geen gaten / alles sluit aan**
- Gebouwdelen die elkaar raken (toren tegen romp, weergang tegen toren, muur tegen rots) laten OVERLAPPEN, nooit tegen elkaar leggen;
  gevelvulling (wig) waar een schuin vlak aansluit. Check van boven en van opzij op kieren.
- Plint/sokkel en ringen om torens alleen aan de BUITENkant en open bij deuren; banken/richels nooit in de looproute (je loopt erdoorheen = "verhoging").
- Kunstrots: dikte boven een tunnel afdwingen (min ~0.95 m boven de tunnelboog), tunnel ≥0.7 m van de buitenrand, rots vol hoog tegen muren
  en ingangsmuren, bij de uitgang de rots wel laten aflopen (anders vlakke gele wand).
- Klei-renders in Blender vanuit vaste checkstanden (tunnel van binnen, gang, achterkant, elke aansluiting, in- en uitgang) en kijken naar
  lucht/licht door de wanden, vóór elke upload.
**Looproute vrij**
- Geen bloembakken, klimop, banken, boekstandaard of potten vóór deuren/tunnelmonden of op een pad. Paden als strook vierhoeken (geen triangle_fill: zwarte driehoeken).
- Een vloer/pad dat net boven terrein ligt: terreingras eronder vervangen door Ground (grassprieten prikken anders door de vloer).
- Wandeltest van de hele route (alleen als Daan niet in Play is) en layout-labels/horizonbomen in het gebied weghalen.

## Sneller werken met hetzelfde of beter resultaat (Daan: "het duurt elke keer zo lang")
1. Grote attracties vanaf het begin als losse assets per deel (bv. kasteel / grot / omgeving), elk met een eigen bouw/bake/upload (`bouw_deel.sh`).
   Een fix aan één deel bakt en uploadt alleen dat deel en vervangt in Studio alleen dat model.
2. Texturen alleen opnieuw bakken/uploaden als hun mesh veranderde (hash per bakegroep; ongewijzigd = oude asset-id houden).
3. Automatische check vóór Studio: één script met de vaste klei-checkstanden + gatenmeting (stralen vanuit tunnel/binnenruimte naar buiten
   mogen de lucht niet raken). Fouten vinden voordat Daan ze ziet.
4. Kleine dingen (tint, licht, terrein, een plant/bak verzetten) direct in Studio doen én in het plaatsscript zetten, geen herbouw.
5. Bij het plaatsen alleen het veranderde deel vervangen, niet ook alle planten opnieuw.
6. Studio MCP is vaak "Target is not reachable": plaatsing lukt meestal toch, controleren met een korte query in plaats van alles opnieuw.

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

## Lessen Langnek (12 nov, chat 4)
- **Nog niet animeren** (Daan): alleen het object + scène bouwen, geen show/beweging tot hij erom vraagt. Animatiescript ligt klaar in
  `models/CH_Langnek/roblox/LangnekAnimatie.server.luau` (NIET in de game).
- Altijd via de Blender-pijplijn (blender-image-to-3d), nooit losse Studio-parts; de eerste snelle parts-versie werd terecht afgekeurd.
- Schaal uit een straatfoto zonder maatstok: **horizon-methode** (horizon = ooghoogte ~1.6 m; px/m op een vlak = (grondlijn - horizon) / 1.6).
  Fotocamera namaken in `build/cam_match.py` met `--pitch` en staande foto (sensor verticaal 36 mm, telefoon ~28 mm).
- OSM -> Blender: figuur kijkt naar -Y, dus zijn RECHTERhand is -X. Fout gemapt = gespiegelde rots/vijver; controleer met de overlay.
- Bronnen kunnen botsen (Eftepedia nek 4.8 m, foto 5.9 m; OSM-rots 20% breder dan de foto): foto aangehouden, conflict in de brief noteren.
- Kunstrots: hoogteveld binnen de contour met een DICHTE onderkant (holes_fill) -> voxel remesh -> grote Voronoi-blokken + plaatselijke richels
  (overal gelijke richels ogen als een volantrok). Voetrichels/zitplateau in het hoogteveld zetten waar de figuur zit.
- Export (`09_export_roblox.py`): loop over `list(low.all_objects)` en depsgraph per object opnieuw ophalen (decimeren maakt hem ongeldig);
  driehoekenplafond per object (hoofd 9k, broek 6k, rots 12k). Anker-blokje op z=-2 voor de oorsprong in Studio.
- Water als vlak heeft dikte nodig (Roblox toont alleen voorkanten). Water net boven het maaiveld (Y 2.12) = geen terrein uitgraven.
- Levend water hergebruiken: Kroos-decals (140434402386473) en Rimpelbron-emitters klonen uit `SprookjesboomWater`.
- Beplanting: `ServerStorage.BomenBronV3` (den, taxus, rododendron, eik, beuk; ScaleTo x3) + `VVEchtePlanten` (varens); nieuwe map toevoegen
  aan `MAPPEN` in StarterPlayerScripts.Wind zodat hij meewiegt.
- Let op bij tekstvervanging in scripts: een commentaar midden in een regel zette `smooth_obj(...)` uit (oogleden zonder materiaal).
- Objecten draaien om hun EIGEN middelpunt: gefuseerde objecten hebben de oorsprong op (0,0,0); `rotation_euler` draait dan om de wereld
  en het deel zweeft los (Langnek-oren). Gebruik `matrix_world = T(c) @ R @ T(-c) @ matrix_world`.
- Gezicht beoordelen onder de fotohoek (`build/gezicht_review.sh`): een figuur hoog boven de bezoekers kijkt vaak omlaag (Langnek 25 graden).
- Bake (`build/04_bake.py`, ~2.5 min): EMIT-bake van Studio-kleur x AO x variatie per groep; daarna export (knippen, niet decimeren) en
  model + texturen opnieuw uploaden. Daan vindt de keten traag: bij kleine wijzigingen alleen de veranderde groep opnieuw bakken/uploaden.
- Meer bomen achter een attractie: Daan wil een vol bos als achtergrond (Langnek: 57 planten in LangnekGroen).
- Normal-map-bron (hoge versie) NIET zichtbaar laten tijdens de kleur/AO-bake: AO botst op de dubbele vorm -> camouflagevlekken (Langnek-rots).
  Normal map van een ruisige rots is in Roblox te hard: blur + ~45% sterkte (`textures/Langnek_rots_normaal_zacht.png`).
- Kleine textuurfix zonder nieuwe bake: plaatje met PIL aanpassen, alleen dat plaatje uploaden en de SurfaceAppearance in Studio vervangen (~30 s).
- Pad bij een attractie zoals bij de Sprookjesboom: klinkerstrook 3 cm boven maaiveld, opsluitband alleen buiten; planten waarvan de voet
  of kruinrand boven het pad komt automatisch weglaten (raycast op de padmesh).
- Daan wil spawnen bij wat we net bouwden om het te bekijken; oude spawn bewaren in een attribuut.
- Langnek v4: echte attracties in het Sprookjesbos staan in DICHT bos (struiken + ondergroei tot aan het water), paden zijn er kort.
  Bos procedureel in ringen met tussenafstanden per soort (struiken mogen onder bomen); kleine planten CastShadow uit = +6 fps.
- Snelle deel-export: `09_export_roblox.py --alleen <naam-begin,...>` + losse asset, in Studio alleen die delen vervangen (geen bake nodig).
- Gezicht realistischer: oogleden, wallen, neus en lippen als ellipsoiden MEE fuseren in de hoofdmassa en daarna openingen uitgraven
  (push met direction); losse buisjes/ringen ogen cartoon. Te zware bovenleden = boze blik: leden hoog genoeg, ruime oogopening.
- Plooien: per ring van de loft duwen met kleine sterkte (doorlopend); om de ring duwen met grote sterkte geeft een kralenketting.

## Lessen Assepoester (12 nov, chat 5)
- Eftepedia-lemma in een keer binnenhalen: thumb-src uit de html halen en `/lemma/images/X/XY/naam.jpg` (zonder thumb/) downloaden; contactblad van 6 kolommen.
- BAG-footprints zijn rechthoekig en betrouwbaar voor maten (+-0.5 m), maar onderlinge verspringingen kunnen afwijken van de foto: zichtbare gevel = foto.
- Oriëntatie uit OSM-entrances halen (`entrance=main/exit`) voordat je de kijkrichting kiest.
- Een frontale gevelfoto kan vrijwel orthografisch zijn (rechtgetrokken of telelens): test dat door de px/m van twee vlakken op verschillende diepte
  te vergelijken. Gelijk -> camera ~300 m ver met lens ~1000 mm (cam_match: clip_end opgehoogd naar 2000).
- Horizontale verschuiving van achterliggende vlakken in de overlay eerst als plattegrondfout zien, niet meteen als camerayaw: yaw maakt de zijgevel zichtbaar.
- Beloopbaar gebouw: binnenruimtes als snijvolumes in dezelfde boolean als de ramen, met use_self + use_hole_tolerant (overlappende muurblokken),
  anders blijven openingen dicht. Botsing via onzichtbare COLL_-blokken, niet via mesh-botsing (Default-hull sluit deuropeningen).
- Bake van een gebouw: onzichtbare vlakken (onderkanten op maaiveld, muurtoppen onder daken, onderkant daken) eerst weghalen, anders
  gaat de helft van de 1024-textuur naar zwarte vlakken. Muren per gevelrichting splitsen = meer pixels per gevel.
- Als een oude SurfaceAppearance-textuur ineens wit rendert: opnieuw uploaden en ids vervangen (haagtextuur, nov 2026).
- Wandeltest zonder navigatietool: in de Client Humanoid:MoveTo per waypoint + MoveToFinished, afstand tot doel loggen (betrouwbaarder;
  character_navigation kan in de wachtrij blijven hangen en later het personage wegsturen).
- Layout-labels (EftelingLayout) nooit AlwaysOnTop: dan zie je namen van andere attracties door muren heen (Daan).
- Daken die elkaar raken mogen niet overlappen (flikkeren): laat het ene dak beginnen waar het andere eindigt.
- Snijvolumes (boolean) mogen elkaar niet precies raken of vlakken delen: laten overlappen, anders blijft er soms een muur staan
  die je wel ziet maar door kunt lopen (botsblokken zeggen open) -> Daan: "glitcht".
- Bij een melding van Daan eerst zelf op zijn plek kijken (screenshot op zijn camerastand) voordat je iets verandert; niet gokken welke muur.
- Kleine fix = klein houden: niet de hele keten draaien als het om 1 onderdeel gaat. bouw_alles.sh hergebruikt nu ongewijzigde texturen (md5).
- Niet met MoveTo/teleport testen terwijl Daan zelf in Play is: dan stuur je zijn personage.
- Kunstrots met een tunnel erdoor: tunnel minstens ~0.7 m van de buitenkant houden (anders breekt de rots open = gaten, Daan). Rots tegen
  aansluitende muren vol hoog laten doorlopen (randafstand niet meten tot randen langs muren).
- Geen klimopvlakken bij in- en uitgangen; bladplakkaten alleen op torens/hoge muren.
- Grote attracties in losse assets per deel (kasteel / grot / omgeving), zodat een fix aan een deel niet alles opnieuw bakt en uploadt.
- Python-tekstvervanging in scripts: nooit op 'def build(master):' ankeren (staat ook in de exec-regel bovenaan); gebruik '\ndef build(master):\n'.

## Lessen Hans en Grietje (13 nov, chat 6)
- **Fotocamera terugrekenen:** met de cam_match-camera een pixel uit front.jpg omzetten naar een straal en die tegen de muur-BVH schieten
  (`ray900` / `at_plane` in `03_forms.py`). Zo staan harten, koeken, deur, ramen en luiken precies waar ze op de foto zitten.
- **Pannenkoekendak:** losse 8-hoekige schijven met vaste UV's naar een 2x2-atlas (geen bake nodig). Pannenkoeken die over de rand vallen
  buigen (`edge_bend`). Per rij gelijk verdelen met een pannenkoek op beide randen, anders krijgt één windveer geen rand.
- **Atlas-objecten** (naam `BAKE_...` met eigen UV) slaan de bake over. Alleen het stuc wordt gebakken (1:40 min).
- **Organisch stuc:** primitieven samen -> voxel remesh 0.05 -> uitlopende voet + ruis -> decimeren (0.14) -> openingen pas daarna met booleans
  (strakke randen, ~21k tris).
- **04 importeert 03 als module:** de templatefuncties houden de owner-tag van 03, dus de tuinobjecten zelf hertaggen, anders ruimt 03 ze op.
- **Eerst alle foto's op muren/hekken bekijken, ook die van opzij:** de voorkant bleek een groene buisleuning, de witte muurtjes lopen links
  om de hoek en rechts langs het grindpad (HGoverzicht2016). Een hek over het grindpad hoorde er niet.
- **Daan:** hoofdpad van grind, en het pad volgen zoals OSM (splitsingen en aansluitingen mee) in plaats van alleen een recht stuk voor de
  attractie. Meer bos tot ~25 m rondom, ook tussen en langs de paden.
- **Figuren via generate_mesh** komen er chibi/cartoon uit, ook met "realistic proportions". Daan: Hans en Grietje komen later. Kleine dingen
  (vogels, windvaan) werken wel. `plaats()` bewaart nu de map Figuren als het huis opnieuw geplaatst wordt.
- **FPS meten:** meet ook een referentieplek elders. Studio kan als geheel throttlen (alles ~15 fps), dan zegt het verschil meer dan het getal.
- **Afbakening = het perceel, niet de paden (Daan):** "afbakenen" betekent het perceel van de attractie rondom dichtzetten in de stijl die er al
  staat (hier de lage witte muurtjes), niet hekjes langs alle padranden. Bij twijfel over vorm/stijl eerst vragen.
- **Meubilair (lantaarns, bankjes, prullenbakken) komt later (Daan, 13 nov):** niet vanzelf oppakken.
- **Na een sessie in Studio de place opslaan (Daan vragen):** bij Hans en Grietje waren de perkplanten weg na een herstart van Studio.
  Bij twijfel eerst tellen per map (bloem_* in ...Groen) voordat je iets plaatst.
- **Schuine botsblokken niet als mesh exporteren:** Roblox maakt van een gedraaide kubus-mesh een rechte doos om de hele diagonaal
  (Magische Klok: 13 x 13 m in plaats van een dunne muur). Botsblokken als Parts in het plaatsscript maken (tabel uit *_extra.json, CFrame met hoek+pi).
  Let op bij oudere scenes met schuine COLL_ (Hans en Grietje-muurtjes, Sneeuwwitje-torenring): die zijn ook dozen.
- **Terrein uitgraven:** FillBlock Air werkt per cel van 4 studs en alleen als het celmidden binnen het blok valt; graaf diep genoeg (tot Y -4) met rechte blokken.
- **Tele-foto's:** als muren die een hoek maken op de foto in een lijn lijken te staan, is de foto van ver met een lange lens genomen (cam ~30 m, 55 mm).
- **Glass in Roblox weerspiegelt de lucht (felblauw):** troebel water als SmoothPlastic donkergroen met weinig transparantie.
- **Eerst de echte indeling (Daan, Magische Klok):** overzichtsfoto's + OSM-paden/-punten in het modelframe tekenen (`01b_plan.py`) en per element
  een bron hebben (aantal figuren, waar het water loopt, wat ervoor ligt: gras/plein/perk). Een tekst als "gracht voor de muren" kan maar voor één muur gelden.
- **Mud in deze place = VV_Bosgrond (felgroen):** niet gebruiken voor oevers.
- **Terrein herstellen:** WriteVoxels per 4-stud-cel met (Ground 1, Ground 1, Air 0) op Y -8..4 geeft weer maaiveld op Y=2 (zo ligt het ongerepte terrein).
- **Herauten/figuren zonder generator:** skin-modifier (gewrichten + stralen) + subsurf 2 voor het lichaam, kleding als lofts met strepen per segment,
  gezichtsdelen meeschalen met het hoofd (anders verdwijnen ze erin). generate_3d vraagt een generator-sleutel in de Blender-addon.
- **Daken: onderkant van een overstek niet wegbakken.** Roblox-meshes zijn enkelzijdig; zonder onderkant kijk je van dichtbij onder de dakrand door het dak.
- **Alle foto's van een plein bekijken vóór de vorm kiezen** (Magische Klok: de totaalfoto liet de echte vorm zien, de andere twee foto's waren uitsneden).
- **Loopvlakken altijd met de bovenkant naar boven** (los vlak / ear-clip kan omgedraaid uitkomen; Roblox toont dan het terrein eronder) en ~10 cm boven het maaiveld.
- **Niets hoogs in het zicht vóór een voorstelling** (bomen/struiken tussen kijkplek en figuren weghalen na het beplanten).
- **Bij twijfel over wat Daan bedoelt: eerst de 2 interpretaties voorleggen** in plaats van te bouwen (Magische Klok: "langs de rand" = smal randpad, niet alles grind).


## Lessen Magische Klok v11 (13 nov)
- **"Geen bruikbare foto" eerst opnieuw checken met uitsneden:** het torentje stond gewoon op Magischeklok1976 (rechterrand) en Herauten-okt2009;
  de ontwerpschets (rond torentje met spits) week af van wat gebouwd is. Foto gaat voor schets.
- **Kleine figuur op hoogte (Slimme Toon):** eerst de kijkrichting van de foto nadoen. Vanaf de voorkant naar de klok kijkend zag je zijn rug;
  hij moet links van de klok zitten en opzij kijken, dan staat hij net als op de foto in profiel. Een eigen zitkrul voorkomt dat hij zweeft.
- **Alleen het model vervangen:** het plaatsscript graaft ook terrein/vervangt gras; bij een modelupdate alleen plaats() + botsing + voorladen draaien.
- **Bij alleen-model-vervangen in Studio ook LAMP_ en COLL_ afhandelen** (lampen -> PointLight, geexporteerde COLL_-meshes weg; botsing = Parts uit COLL).
- **Herauten v12:** eerst een close-up render naast de foto zetten maakt de verschillen meteen duidelijk (hoed zweefde, haar te kort, vaandel onleesbaar).
  Vaandel/leeuw/lelie als uitgesneden plaat (`plaat()` met EAR_CLIP-triangulatie): concave n-hoeken anders verkeerd getrianguleerd bij export.

## Lessen Prinsenpoort (13 nov)
- **Plek bewijzen met meerdere bronnen** (Daan vroeg "staat het echt hier?"): OSM-naam, OSM-pad door de doorgang, een foto waarop het buurobject
  te zien is, en een routebeschrijving uit de lemma-tekst tegen OSM leggen. Zet dat bewijs in STATUS.md.
- **Maten van een gebouw uit een oude frontfoto:** schaal via mensen die IN de boog staan (zelfde diepte), niet via mensen op de voorgrond.
  OSM-footprints van kleine gebouwen zijn ruw (hier 12.3 m i.p.v. 8.7 m breed); diepte uit OSM, breedte uit de foto.
- **Terrein uitgraven graaft cellen van 4 studs:** daarna de cellen buiten het gewenste gat terugzetten (WriteVoxels Ground 1/1/0 op Y -8..4)
  en oevers als mesh tot ~1 m buiten het water laten lopen zodat ze het gat afdekken.
- **Struiken/taxussen vóór een nieuwe attractie weghalen** (zicht vanaf het pad); zoeken op BaseParts met Size.Y > 5 in het gebied.

## Lessen Herautenplein (13 nov)
- **Paden altijd het lichte grind** (Pebble + VV_Grind 235,228,214), ook als de foto keien laat zien (Daan, opnieuw bevestigd).
- **Nieuwe scene naast een oude: de paden laten aansluiten** (gat tussen MK-randpad en ringpad dichtzetten met hetzelfde grind) en de kale
  grond die de oude scene achterliet weer gras maken.
- **ReplaceMaterial Ground->Grass nooit blind over een groot gebied:** onder paden/vloeren moet Ground blijven (grassprieten). Eerst de open
  stukken bepalen, alleen daar gras.
- **generate_mesh-kikkers** worden hurkend beter met "crouching, low flat body, no base, no lily pad"; kleur zit in de textuur (geen
  SurfaceAppearance), dus tinten lukt niet. Grootte opgeven werkt in studs, daarna ScaleTo.
- **Dieren die op een foto moeten lijken (kikkers): zelf in Blender beter dan generate_mesh.** Overlappende ellipsoiden/buizen ->
  voxel-remesh (unie) -> Smooth-modifier (vloeiende overgangen) -> decimate geeft in 1 script een organisch dier; huid procedureel
  bakken (ruisvlekken + buik via normaal-Z) naar een BAKE_-object met eigen UV. Pupillen plat in de oogbol, anders "googly eyes".
