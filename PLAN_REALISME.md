# Plan: realisme Sprookjesbos (voor LATER, na de laatste 5 attracties)

Opgesteld 15 nov 2026. Niets hiervan is uitgevoerd. Pas starten als Daan zegt "nu".

## Het kernprobleem
De AI **raadt** vormen uit een paar foto's en boetseert ze met code (gefuseerde volumes + voxel remesh + ruis).
Dat geeft klei, geen beeldhouwwerk. Een betere skill lost dat niet op: we moeten van **raden** naar **meten**.

## Diagnose 1: Klein Duimpje (reus)
Vergeleken: `models/CH_KleinDuimpje/review/b5/compare_mat.jpg`, `c5h`, `c6b` met `ref/commons/Klein_Duimpje__4019765619_.jpg`.

| Wat | Echt (foto) | Ons model |
|---|---|---|
| Massa | Dik, zwaar, ronde buik, dikke dijen | Mager en lang, te weinig volume |
| Houding | Voorste knie hoog opgetrokken (hoogste punt midden), onderbeen eronder gevouwen | Benen lager en rechter, silhouet plat |
| Oppervlak | Glad gelakt polyester met **strakke, bewust gezette** plooien | Bobbelig, deuken van de remesh, plooien als regelmatige ringen (broek lijkt een harmonica, jas gebreid) |
| Laarzen | Grote ronde leren laarzen, omgeslagen kraag, dikke zool, neus omhoog | Buizen met platte afgesneden uiteinden, golvende ring als kraag |
| Hoofd | Strakke kale schedel, zware wenkbrauwen, krullende snor, puntige wigbaard | Bolletjes-neus, platte oor, baard als zwarte klonterige plaat |
| Handen | Vingers in elkaar op de buik | Worstjes/blokjes |
| Afwerking | Satijnglans, airbrush-overgangen, vuil in de plooien | Vlakke kleur, overal dezelfde ruwheid |
| Scène | Grote ronde grijze zwerfkeien | Plat strooisel van kleine steentjes |

## Diagnose 2: Monstervis (Pinokkio)
Vergeleken: `models/AR_Pinokkio/review/v2/sheet.jpg` met `ref/eftepedia/Pinokkio_monstervis.jpg`.
Let op: als hoofdreferentie werd ook een **schets** gebruikt (`Pinokkio_monstervis_rjj.jpg`), niet het echte beeld.

| Wat | Echt (foto) | Ons model |
|---|---|---|
| Bek | Enorme dikke bovenlip die naar voren steekt, vooruitstekende onderkaak, kromme slagtanden, Pinokkio + Geppetto in de bek | Ronde donut-ring als mond |
| Oog | Geelgroen, zwaar half dichtgezakt ooglid, boos | Klein bolletje |
| Stekels | Dikke oranje kromme hoorns met knop/krul aan het eind | Dunne rietjes |
| Huid | Ronde schubknobbels (keitjes) op de kop, oranje/zalm met donkere vlekken, natte glans | Bruin, vlak, nauwelijks schubben |
| Houding | Ligt tot de nek in het water, staart/vinnen komen ernaast boven | Staat als een blob op de rand |

## Wat dit gemeen heeft (en dus de echte oplossing)
1. **Vormen uit code-boetseren halen het nooit** voor figuren. Nodig: een basis-mesh die al lijkt (scan of image-to-3D).
2. **Verkeerde of te weinig referentie** (schets i.p.v. foto, één hoofdhoek).
3. **Geen echte texturen/glans**: geschilderde bake met vlakke kleur.
4. **Geen keuring per detail**: vergelijkingsblad op afstand verbergt dat bek, ogen, handen, laarzen niet kloppen.

## Overzicht: waar staat elke boom, struik en decoratie? (bronnen)
Eén bestaand "inventaris"-bestand van de Efteling is niet openbaar. Wel te combineren:
- **OSM (al in `reference/data/efteling_osm.xml`)**: 411 losse bomen, 108 hagen, 257 lantaarns, 220 bankjes,
  123 afvalbakken, 113 bosvlakken, en per pad de verharding (444 klinkers, 275 asfalt, 36 kasseien/sett, 31 fijn grind,
  36 hout, ...). De 15.805 boomrecords die we nu plaatsen zijn grotendeels **verzonnen binnen bosvlakken**, niet gemeten.
- **AHN-laserscan**: elke boomkruin met plek, hoogte en kroonbreedte (ook in het dichte bos). Vervangt de verzonnen bomen.
- **Boomregister.nl** (AHN + luchtfoto, alle bomen van NL incl. particulier terrein): zelfde idee, kant-en-klaar;
  toegang/licentie nog uitzoeken.
- **PDOK-luchtfoto 7,5 cm**: struiken, rododendronmassa's, perken, keienranden en grote decoratie zijn van boven zichtbaar.
- **Video-frames**: wat er onder de bomen staat (varens, hulst, keien, bordjes, hekjes) per stuk pad.
Resultaat: één kaartlaag per soort (boom/struik/haag/lantaarn/bank/bak/kei/pad-verharding) in studs, als data-PNG.

### Waar loopt welk pad (OSM, `reference/padkaart_sprookjesbos.png`)
- Alle paden staan in OSM (729 footways, 277 pedestrian), inclusief verharding. In het Sprookjesbos: **hoofdlus en
  bijna alle paden = klinkers (paving_stones)**, **kasseien (sett)** op een paar zijpaadjes (Doornroosje, Roodkapje ->
  Pinokkio, Zwavelstokjes, Kikkerkoning-tuin, Kabouterdorp), **hout** bij bruggetjes, beton/grijs bij De Zes Zwanen.
- Let op: op de foto bij Klein Duimpje lijkt het hoofdpad glad grijsbruin. Luchtfoto + video-frames beslissen
  welk klinkerverband/kleur het echt is (OSM zegt alleen "klinkers").
- Correctie op Fase D hieronder: hoofdpad = klinkers volgens OSM, niet asfalt; nog checken op beeld.

### Hoeveel bomen?
- OSM heeft in het Sprookjesbos maar **~11 losse bomen** getekend; het bos zelf is niet als bosvlak getagd.
- De sprookjes zelf liggen binnen ~4 ha; met het bos eromheen is het Sprookjesbos grofweg **8-10 ha**.
- Oud loofbos/parkbos: ~150-250 grote bomen per ha -> **ruwweg 1.200-2.500 echte bomen**. AHN geeft het exacte
  aantal, met plek, hoogte en kroonbreedte.
- In Roblox niet allemaal vol: de paden liggen zo dicht op elkaar dat bijna elke boom ergens van een pad te zien is,
  dus winst zit vooral in **wat onder en achter** zit: volle boom (stam + kroon) alleen waar je de stam ziet
  (schatting 600-1.000), de rest **alleen kroon** (lichte LOD) + plantenwanden ertussen. Ondergroei alleen in de
  strook langs het pad.

### Hoogteverschillen (AHN, opgehaald 15 nov: `reference/ahn_sprookjesbos/`)
- Het Sprookjesbos is **niet vlak**: maaiveld 6,1 tot 14,4 m NAP; meeste grond tussen 7,5 en 10,1 m (ruim 2,5 m verschil).
- Duidelijk te zien (`maaiveld_hillshade.png`): **heuvels/wallen** (o.a. de heuvel bij Doornroosje, wallen langs
  de vijvers en paden), **verdiepte vijvers**, paden die licht insnijden, en het terrein loopt op naar het zuidoosten.
- Ook in de data: ~3.300 boomtoppen > 6 m in het hele vak (incl. randen buiten het bos); boomkronen tot ~22 m hoog.
- **Hoogte per attractie** staat in `reference/ahn_sprookjesbos/hoogte_attracties.csv` (maaiveld in m NAP en
  t.o.v. de parkoorsprong, 9,02 m NAP). Opvallend: Doornroosje +4,7 m (op de heuvel; nakijken: AHN-gat onder het
  kasteel is bijgevuld), Langnek +1,4 m, Kabouterdorp/Roodkapje/De Draak ~+0,9 m, Tuinman en Fakir/Magische Klok/
  Repelsteeltje/Sprookjesboom/Klein Duimpje -0,5 tot -1,0 m. Alles staat nu op dezelfde hoogte in Studio.
- Toepassen: AHN-maaiveld als terrein-hoogtekaart (blender-environment-kits), elke attractie op de echte hoogte
  zetten (nu staat alles op Y=2 = vlak). Let op: 27% van het maaiveld is een gat onder dicht blad/gebouwen en is
  bijgevuld; bij vijvers en heuvels nakijken met foto's.

## De scène rond elke attractie (hier gaat nu veel mis)
Per attractie een vaste **scène-inventaris** vóór het bouwen, uit alle foto's/video-frames van alle kanten:
- Grond: wat ligt er (gras, bosgrond, grind, mos, schors, klinkers), waar gaat het over in elkaar.
- Randen: keien, hekjes (vorm, kleur, hoogte), borders, opsluitbanden of juist niet.
- Planten per soort en plek (varens, hulst, rododendron, taxus, buxus), hoogte en dichtheid; wat staat er ACHTER.
- Water: vorm, oever (kei/riet/beton), kleur, troebelheid.
- Decoratie: bordjes, lantaarns, bankjes, prullenbakken, boekstandaard, de sprookjesboek-stoel, enz. (OSM + foto).
- Hoogte: ligt het sprookje in een kuil, op een heuvel, tegen een wal (AHN).
- Wat de bezoeker vanaf het pad ziet: kijkrichting(en), wat moet achter de attractie dicht zijn.
Keuring: dezelfde camera als 3+ foto's (vooraanzicht, schuin, vanaf het pad) en een bovenaanzicht naast de
luchtfoto. Elk punt van de inventaris afvinken.

## Figuren 1 op 1 (reus, Monstervis, Magische Klok, Langnek, ...)
Code-boetseren haalt het niet. Werkwijze in volgorde van kwaliteit:
1. **Multi-view uit video's**: 30-100 frames rond de figuur (meerdere video's/jaren) -> fotogrammetrie (COLMAP /
   RealityScan) of **3D Gaussian Splatting -> mesh**. Bij figuren waar je omheen kijkt (vis, klok) werkt dit goed;
   bij een figuur die je maar van één kant ziet, alleen de zichtbare kant betrouwbaar.
2. **Image-to-3D met meerdere echte foto's** (skill `roblox-3d-model` / Hi3DGen, of Hunyuan3D/Tripo multi-view):
   echte foto's van voor/zij/achter erin, nooit een schets of AI-concept. Geeft direct een vorm die lijkt.
3. **Bijwerken in Blender**: schaal uit AHN/foto (maatstok: deur 3 m, bezoekers 1,7 m), houding via cam_match op
   2-3 fotocamera's tegelijk (multiview-fit-loop), gezicht/handen/voeten apart verfijnen, plooien strak (creases).
4. **Kleur van de foto**: foto's projecteren op het model (meerdere camera's, schaduw eruit), naden bijwerken.
5. **Materiaal**: satijnglans polyester (roughness ~0.35-0.45), airbrush-overgangen, vuil/groen in holtes.
6. **Keuring per detail**: overlay-render op elke foto + close-ups gezicht/handen/voeten/bek/ogen; pas naar Studio
   als het silhouet op alle foto's dekt (bv. > 95% overlap van het silhouet).

## Licht 1 op 1
- **Echte zonrichting**: Roblox `GeographicLatitude` = 51,65 en noord goed zetten (parkcoördinaten: -Z = noord),
  zodat zon en schaduwen vallen zoals in Kaatsheuvel. Tijd standaard rond 14:00 in de zomer.
- **Bos donker, open plekken licht**: onder het bladerdak minder licht (Atmosphere/ambient per zone of zachte
  ColorCorrection die meeloopt) en lichtvlekken op de grond (gerenderde lichtvlek-decals of SunRays door gaten).
- **Kalibreren op foto's**: met `reference-look-calibration` helderheid, verzadiging en kleurtint van een
  Roblox-screenshot meten tegen echte foto's vanaf dezelfde plek, en Lighting/ColorCorrection daarop afstellen.
- **Texturen zonder ingebakken zon**: foto-texturen eerst egaal maken (delighting), anders dubbele schaduw.
- Lantaarns/attractielicht: warm (2700 K), 's avonds aan; vijvers met reflectie (Water/Glass + Future).
- Future-belichting zet Daan zelf (staat in WERKWIJZE).

## Skills die helpen (gezocht 15 nov)
Al geïnstalleerd en direct bruikbaar:
- **roblox-3d-model**: foto -> high-poly mesh (Hi3DGen via Hugging Face) -> Blender decimate/UV/normal bake ->
  Roblox MeshPart. Bedoeld voor tekst->concept->3D, maar je kunt een **echte foto** als input geven. Kandidaat voor
  de figuren (reus, vis, draak). Eén per keer; HF-voorwaarden nog checken. Kaggle staat uit (skill zegt dat zelf).
- **blender-environment-kits**: terrein uit hoogtekaart (AHN!) + planten verspreiden op helling/hoogte/masker.
- **reference-look-calibration**: kleur/licht/verzadiging meten tegen de echte foto (tegen "te fel / te grijs").
- **blender-texture-baking** + **blender-game-optimization**: scan/AI-mesh naar Roblox-budget, LOD's voor bomen.
- **blender-lighting**: licht in de review-renders lijkt dan op Roblox-licht.
- **multiview-fit-loop / reference-to-3d**: vorm passen aan meerdere foto's tegelijk.
Online gevonden en **geïnstalleerd 15 nov** in `~/.claude/skills/` (alle MIT, alleen markdown, gecontroleerd; bron in BRON.txt):
- Uit tabooharmony/roblox-brain: **roblox-lighting** (Lighting/Atmosphere/post-processing, naar de officiële docs),
  **roblox-building**, **roblox-audio**.
- Uit arjun988/blender-skills: **vegetation-artist** (bomen, bladkaarten, kroon-LOD's), **set-dressing**,
  **scene-assembly**, **lookdev**, **creature-artist** (vis/draak), **character-artist** (reus), **collision-proxy**
  (onzichtbare botsranden), **biome-worlds**.
- Uit pjt222/agent-almanac: **create-3d-scene**.
- Extra uit roblox-brain (15 nov): **roblox-camera**, **roblox-studio-mcp**, **roblox-animation-vfx** (pas voor later,
  animeren mag nog niet). Niet geïnstalleerd: roblox-performance (dubbel met roblox-dev:roblox-performance) en
  onbekende losse Roblox-skills van skills.sh (niet te controleren).
- **Al ingebouwd in de Roblox Studio MCP** (niets te installeren, oproepen via de Studio-skilltool):
  **rbx-import-asset** (Blender/FBX/GLB -> Studio met controle op geometrie, texturen, kleur, schaal, oriëntatie),
  **rbx-scene-analysis** (render/geheugen/instanties per scène), **rbx-perf-profiling** (MicroProfiler: CPU/GPU-
  pieken), **rbx-docs-search** (actuele Roblox-docs), rbx-debug, rbx-unit-test, rbx-device-simulator-lua.
Geen kant-en-klare skill gevonden die Roblox + realistisch licht + Blender samen doet -> onze eigen
"efteling-sprookje"-skill (Fase C) bundelt deze.

## Fase A: fundament voor het hele Sprookjesbos (eenmalig)
1. Gebied bepalen uit `reference/data/efteling_osm.xml`.
2. **PDOK-luchtfoto 7,5 cm/px**: alle paden, randen, perken overtrekken (vervangt de scheve OSM-lijnen).
3. **AHN (DTM + DSM, 0,5 m)**: echt hoogteverschil in het bos + **elke boom** (plek, hoogte, kroonbreedte) uit DSM - DTM.
4. Omrekenen naar studs/parkoorsprong (51.6500 N, 5.0455 E), als data-PNG zoals de bomen nu.
5. Boomsoorten toewijzen (beuk, eik, den, rododendron, taxus) uit luchtfoto + video; `BomenBronV3` gebruiken.
6. Bosbodem: CC0-scans van blad, mos, wortels, schaduwgras; echte padranden.

## Fase B: per sprookje/figuur meten in plaats van raden
7. **Bronnen met minimum**: alle Eftepedia + Commons + frames uit 4K-wandelvideo's (YouTube), meerdere jaren/kanten.
   Altijd een **echte foto** als hoofdreferentie, nooit een ontwerpschets.
8. **Video → frames → fotogrammetrie** (COLMAP/RealityScan) lokaal op de Mac. Scripts kiezen scherpe frames zonder mensen;
   Claude ziet alleen één verkleind overzichtsblad (usage).
9. **Figuren (reus, vis, draak, meermin, ...): image-to-3D** (Blender MCP `generate_3d` / Hunyuan3D / Tripo, multi-view uit
   de video-frames) als basis-mesh. Daarna in Blender: maat uit de foto, houding via cam_match, strakke plooien
   (subdivision + creases, geen ruis), gezicht/handen/laarzen apart verfijnen.
10. **Foto-projectie als textuur**: `cam_match.py` uitbreiden zodat de echte foto op het model geprojecteerd wordt
    (schaduw eruit), rest aanvullen.
11. **Materiaal**: polyester figuren satijnglans (roughness ~0.35-0.45), airbrush-overgangen, vuil in holtes; Roblox
    SurfaceAppearance met RoughnessMap.
12. Scan/AI-mesh → opschonen → LOW → bake → export via de bestaande keten.

## Fase C: skill "efteling-sprookje" met strenge keuring
13. Eén skill die vastlegt: minimum bronnen, elementenlijst per foto, hoofdreferentie = echte foto, basis-mesh uit
    scan/image-to-3D voor figuren, verplichte texturen + glans.
14. **Keuring per detail**: render vanuit de fotocamera naast de foto, PLUS close-ups van gezicht, handen, voeten, bek/ogen.
    Pas naar Studio als elke close-up standhoudt.
15. Alle lessen uit WERKWIJZE.md erin, zodat elke nieuwe chat op dit niveau begint.

## Fase D: het gevoel dat je er echt bent (onderzoek 15 nov)

### Paden zoals op de foto's (bekeken: Roodkapje-pad, kijkplein, pad naar Pinokkio, overzicht Klein Duimpje)
- **Hoofdpad**: breed, bochtig, **grijsbruin asfalt met grindachtige toplaag** (geen strak zwart asfalt, geen los grind),
  randen zacht in de bosgrond, blad en dennennaalden erop.
- **Zijpaden naar sprookjes**: **grijsbruine kasseien in gebogen rijen/waaiers**, licht bol, mos in de voegen.
- **Pleintjes bij sprookjes**: **flagstone (onregelmatige platen)** zoals bij Roodkapje, of rode klinkers bij een stoep.
- **Rand**: geen strakke opsluitband maar een **rij grote ronde grijze zwerfkeien**, daarachter direct varens, hulst,
  rododendron. Lantaarns (zwart, klassiek) langs het pad. Wortels en bladhopen tegen de randen.
- Bocht na bocht: je ziet nooit ver vooruit. Het volgende sprookje verschijnt pas om de hoek.
- Exacte loop: luchtfoto (Fase A) is leidend; kasseien/flagstone als gebakken textuur met normal map (CC0-scan als basis).

### Paden echt maken in Blender (Daan: verharding ziet er nu het minst realistisch uit)
Geen terreinmateriaal of tegelende textuur meer voor paden. Elk pad wordt in Blender gebouwd:
1. **Referentie per padtype**: close-up frames/foto's van elk type (klinkers hoofdpad, kasseien zijpaden,
   flagstone pleintjes, houten bruggetjes): steenmaat, kleurmenging, verband (keperverband/halfsteens/waaier),
   voegbreedte en -vulling, slijtage. Maatstok: schoen/bezoeker of bekende klinkermaat (~21x10,5 cm).
2. **Padvorm**: middellijn + breedte uit luchtfoto/OSM als curve, op AHN-hoogte, licht bol (afwatering), randen
   iets lager; bochten vloeiend.
3. **Stenen als echte geometrie** (Geometry Nodes/bpy): elke klinker/kassei apart, **verband volgt de bocht van
   het pad** (kasseien in bogen/waaiers, klinkers mee de bocht in), per steen kleine afwijking in maat, hoogte,
   draaiing, afgeronde/afgesleten randen, enkele scheve of gebroken stenen, kleurvariatie per steen.
4. **Voegen**: zand/aarde, mos en grassprietjes in de voegen (meer aan de randen, minder in de looplijn), blad en
   naalden erin.
5. **Slijtage en vuil**: donkerder en gladder in de looplijn, vuil en algen aan de schaduwkant, natte plekken,
   kauwgom-/vlekjes zeer spaarzaam, putdeksels/afvoerroosters waar OSM/foto ze toont.
6. **Rand**: opsluitband alleen waar de foto die toont; anders randkeien (kit) en de overgangsstrook naar bosgrond.
7. **Naar Roblox**: hoge versie (alle stenen) **bakken** naar kleur + normal + roughness + AO op een lage padstrook
   (UV's volgen het pad, dus het patroon loopt mee met de bocht, geen tegelherhaling). Pad in stukken van ~10-20 m,
   1024 px per stuk (± 1-2 px per mm-voeg: scherp genoeg). Dicht bij pleintjes eventueel echte reliëf-stenen als mesh.
8. **Keuring**: render op ooghoogte naast een video-frame van hetzelfde stuk pad (kleur, steengrootte, verband,
   voegen, slijtage) + bovenaanzicht naast de luchtfoto; in Studio van dichtbij en van ver (geen moiré/glinstering).

### Het bos per stuk pad (Daan: hoe het bos eruitziet bij elk stuk lopen is belangrijk)
Het bos is niet overal hetzelfde: open en licht bij vijvers, donker onder dennen, rododendronwanden, beukenlanen.
Daarom het hele padennet opdelen in **trajecten** (tussen twee kruisingen, of elke ~20 m) en per traject een
**trajectkaart** maken:
1. **Video-frames op de kaart zetten**: wandelvideo's lopen de paden af; met herkenningspunten (sprookjes,
   kruisingen, lantaarns uit OSM) en loopsnelheid (~1,2 m/s) krijgt elk frame een plek op het pad. Per traject
   frames vooruit, links en rechts (beide looprichtingen).
2. **Meten uit AHN per traject, links en rechts apart**: kroonbedekking (open/gesloten bladerdak -> licht),
   boomhoogte, waar open plekken zijn, helling/wal/kuil naast het pad, afstand tot water. Waar het open is ook
   lage begroeiing (0,5-3 m). Onder een dicht bladerdak ziet AHN de ondergroei niet -> daar beslissen de frames.
3. **Trajectkaart** (één blad per traject): kaartje + frames + per kant: boomsoorten en dichtheid, ondergroei
   (rododendron/taxus/hulst/varens/klimop), plantenwand ja/nee en hoe hoog, grond (blad/naalden/gras/mos),
   keien/hekje/lantaarn/bank, helling, licht (open/halfschaduw/donker), wat je in de verte ziet (zichtlijn,
   lokkertje), seizoensbeeld zomer.
4. **Bouwen per traject** met de kits volgens die kaart; overgangen tussen trajecten geleidelijk.
5. **Keuring per traject**: in Studio op dezelfde plek en kijkrichting als de frames een screenshot, naast elkaar.
   Klopt de "sfeer" (licht/donker, open/dicht, soort groen)? Pas dan het volgende traject.
Script maakt de trajecten en AHN-cijfers automatisch; Claude ziet per traject één verkleind blad (usage).

### Natuur: alleen bouwen wat je ziet
- Je kunt niet het bos in: **onzichtbare botsrand langs elk pad** (achter de keienrand). Dan geldt:
  1. **Strook 0-5 m van het pad**: maximaal detail. Echte plantscans, varens, ondergroei, bosgrond met blad, wortels,
     keien met mos, takken. Hier kijkt de speler; hier gaat het budget heen.
  2. **5-20 m**: een dichte **plantenwand** (rododendron, taxus, coniferen, hulst) die het zicht afsluit, zoals in het echt.
     Minder driehoeken, geen schaduw op kleine planten.
  3. **Erachter**: alleen boomkruinen tegen de lucht (AHN-posities, lichte LOD of bladkaarten) + nevel.
     Geen stammen, geen ondergroei: niemand komt daar.
- **Gemeten (15 nov, `tools/zichtzone.py`, `reference/ahn_sprookjesbos/zichtzone.png`)**: Sprookjesbos-gebied
  7,8 ha met ~1.950 boomtoppen (AHN). Afstand tot het dichtstbijzijnde pad: 0-5 m = 54% van de grond (~1.000 bomen),
  5-20 m = 42% (~900 bomen), 20-40 m = 4% (~40 bomen), verder dan 40 m = niets. De paden liggen dus zo dicht op
  elkaar dat **binnen het Sprookjesbos bijna alles binnen 20 m van een pad ligt**.
  Gevolg: niet minder bomen, wel **minder per boom** buiten de looproute: voorbij de plantenwand zie je geen grond
  en geen onderstam -> daar alleen kruin + bovenste stam, geen ondergroei, geen schaduw van kleine dingen.
  **Buiten het Sprookjesbos** (achter de randen, richting andere parkdelen/buitenwereld): alleen een rand van
  kruinen tegen de lucht tot waar je kijkt, verder niets.
- Bomen die vanaf geen enkel pad zichtbaar zijn: weglaten. Script dat vanaf punten op het pad zichtlijnen test en
  onzichtbare bomen schrapt (bespaart veel fps; Roblox occlusion culling werkt slecht op gestreamde bomen).
- Bos van het Sprookjesbos: **oude beuken en eiken** (hoge rechte stammen, kroondak boven), daaronder rododendron,
  taxus, coniferen, varens, hulst. Lichtvlekken op de grond door het bladerdak.
- Leven: wind in bladeren (heb je al), vallende blaadjes, stofjes in lichtbundels, af en toe een vogel, water dat stroomt.

### Licht en lucht in Roblox
- Future-belichting (Daan zet die zelf), Atmosphere met lichte nevel in het bos, SunRays door het bladerdak, zachte
  ColorCorrection (iets groener/warmer, niet verzadigd), Bloom subtiel, DepthOfField heel licht voor diepte.
- Donkerder onder de bomen dan op open plekken: het contrast maakt het echt. Niet overbelichten (staat al in WERKWIJZE).
- Lantaarns 's avonds aan (warm), overdag uit.

### Geluid (pas als het park staat, Daan)
- Lagen: vogels, wind in de bomen, ritselende blaadjes, water bij vijvers, en **per sprookje de eigen muziek/stem** die
  aanzwelt als je dichterbij komt en wegvalt als je verder loopt. Geluid is de helft van het gevoel.

### Hoe pretparken het magisch maken (Imagineering-principes, toepasbaar op Roblox)
- **Zichtlijnen**: je ziet nooit het hele gebied tegelijk; bochten en plantenwanden geven steeds een nieuwe onthulling.
- **Weenie / lokkertje**: iets hoogs in de verte dat je naar zich toe trekt (kasteeltorentje Doornroosje, Sprookjesboom).
- **Forced perspective**: hoge dingen naar boven toe iets kleiner maken = lijkt hoger/verder.
- **Geen "achterkant" zichtbaar**: geen kale achterzijdes, randen van de map of lege vlakken in beeld.
- **Overgangen**: elk gebied heeft zijn eigen sfeer; de poort/brug ertussen is de overgang.
- **Details op ooghoogte**: waar je dichtbij komt (bordjes, hekjes, stenen) moet het het mooist zijn.

## Nog meer realisme (brainstorm 15 nov)
- **Ouderdom/slijtage**: mos en groene aanslag noordkant/onderkant muren, regenstrepen onder dakranden, verbleekte
  verf, afgebladderde hoekjes, roest op hekken, donkere looplijn midden op paden, blad in hoeken. Niets perfect recht.
- **Grondcontact**: AO-randje + vuil waar alles de grond raakt, pollen gras/mos tegen de voet, nooit zweven/prikken.
- **Geen herhaling**: kleurvariatie per tegel/plant, vlekken/blad/vocht-decals over grote vlakken.
- **Bewegend licht**: bewegende bladschaduw op het pad, stofjes in lichtbundels, nevel tussen boomlagen.
- **Geluid**: voetstappen per ondergrond (klinkers, kasseien, hol hout, grind), bos-galm (SoundService reverb),
  eenden, wind. Echte Efteling-muziek mag niet geüpload worden (auteursrecht): eigen muziek in die sfeer.
- **Efteling-huisstijl als set**: exacte kleuren (Efteling-groen), lettertype bordjes, lantaarn-, bank- en
  prullenbakmodel één keer perfect, overal hergebruiken.
- **Leven**: eenden, opvliegende vogel, vlinders/libellen bij water, stromend water met schuim (geen NPC-bezoekers).
- **Lucht/horizon**: Hollandse lucht, nergens een lege rand, één seizoen (zomer).
- **Prestaties = realisme**: geen haperingen of LOD-popping.
- **Wandeltest naast een YouTube-wandeling**: zelfde route in Roblox lopen, om de paar seconden frames naast elkaar.
  Belangrijkste keuring in de skill.

## Hoe andere Roblox-pretparken en realistische games het doen (onderzoek 15 nov)
- **Bestaande pretpark-recreaties** (Disney Parks Roblox, een fan-"Efteling Theme Park", diverse Disney/Universal-
  parken): bouwen uit referentiefoto's en online plaatjes, met een team incl. een vaste "reference consultant".
  Geen enkele beschrijft metingen (AHN/luchtfoto/scans). Met meetdata + scans + foto-keuring zit dit project
  boven wat er nu bestaat; de "reference consultant"-rol = onze elementenlijst + keuring.
- **Realistische Roblox-showcases** (DevForum "Basics of Realism", Roblox' eigen Mystery of Duvall Drive):
  alles MeshParts (geen parts/unions), naadloze texturen max 1024, <10k driehoeken per mesh, "alles wat geluid
  moet maken, maakt geluid", eigen client-culling i.p.v. alleen StreamingEnabled: detail-objecten getagd met een
  zichtafstand (klein 200, groot 400 studs), interieurs pas tonen binnen ~50 studs, bomen = helft van de driehoeken
  -> boom-LOD's nodig, CastShadow uit op kleine dingen en dingen in de schaduw, alles verankerd, draaiende dingen
  in LocalScripts. Elk model een PrimaryPart.
- **Nieuw van Roblox (dec 2025): SLIM** maakt automatisch lichte versies (samenvoegen + LOD) van objecten per apparaat;
  later ook "hiërarchisch" voor groepen zoals bossen. Testen op de bomen/planten-modellen voordat we zelf LOD's bouwen.
- **Officiële Environmental Art-voorbeeldplaces** van Roblox (Construct Your World, asset-bibliotheek,
  Optimize Your Experience): gratis te openen in Studio om te zien hoe Roblox zelf terrein, licht en materialen opzet.
- Betaalde realistische bos-maps (BuiltByBit) bestaan; niet nodig, wel goede vergelijking voor sfeer en fps.
Bronnen: devforum.roblox.com/t/the-basics-of-realism-mastering-immersion/1435459,
devforum.roblox.com/t/optimizing-roblox-without-streamingenabled-the-mystery-of-duvall-drive/2060659,
gamesbeat.com (SLIM, 5 dec 2025), create.roblox.com/docs/tutorials/curriculums/environmental-art/construct-your-world,
devforum.roblox.com/t/disney-parks-roblox-development-credits/1516766, roblox.com/games/9695230318.

## Nog meer gevonden (onderzoek 15 nov, ronde 3)
**Licht dat Roblox niet zelf kan**
- Roblox heeft **geen echte global illumination** (indirect licht/terugkaatsing); ook niet op de officiële roadmap 2026.
  Dus faken: (1) **licht inbakken** in de kleurtextuur in Blender (AO + zachte terugkaatsing van de omgeving, wat we
  deels al doen), (2) **verborgen zwakke PointLights zonder schaduw** als terugkaatsing (onder een afdak, in een nis,
  tegen een lichte muur), (3) zones onder het bladerdak donkerder via Ambient/ColorCorrection.
- Roadmap: betere PBR-lichtreactie (specular, huid) pas medio 2027; niet op wachten.

**Materialen: alle vier PBR-kaarten**
- SurfaceAppearance kan **Color + Normal + Roughness + Metalness**. Nu bakken we vooral kleur(+AO). Overal ook
  normal + roughness: natte stenen en vijverranden glanzend, gelakte figuren satijn, hout en stuc mat, metaal hekken
  licht metallic. Dit is een grote stap voor weinig moeite.
- Unified Mesh Importer neemt mesh + PBR-kaarten in één keer mee; **reimport** houdt eigenschappen (botsing,
  RenderFidelity) en vervangt texturen op bestandsnaam -> snellere rondes.
- Meshes > ~20k driehoeken worden door Roblox zelf gedecimeerd: zelf knippen (doen we al) om controle te houden.

**Grond en randen (uit game-environment-art)**
- Tegel-herhaling breken: grote **macro-variatie** over het hele terrein (vlekken, lichter/donkerder), kleurruis,
  en **decals** (vocht, modder, blad) over herhaalde vlakken.
- **Overgangsstroken** pad -> gras/bosgrond: aparte randmesh met blend-textuur (grind/blad dat de grond in loopt),
  schaduwrandje onder de padrand, puin/blad in hoeken, vuil in kieren (vertex color in Blender).
- Terreingras: alleen GrassLength instelbaar, geen eigen grasmodellen in terrein -> langs het pad **gras- en
  varenkaarten als mesh** (dicht bij de speler), verder terreingras.

**Schaal en camera**
- De Roblox-camera laat dingen kleiner/groter lijken dan echt. Standaard FieldOfView 70 houden en de **review-renders
  in Blender met dezelfde FOV** maken (cam_match), dan vergelijk je eerlijk. Spelersschaal 0,9 en deuren 3 m als
  maatstok blijven; check of de bezoekershoogte tegen de figuren klopt (reus moet echt groot voelen).

**Efteling/Anton Pieck-gevoel**
- Pieck: organische lijnen, niets strak, "poëtische details", ~1500 schetsen voor het Sprookjesbos. Dus: scheve
  daken, ongelijke stenen, krommende hekjes, en per sprookje **kleine verborgen details** (zoals elders in het park een
  kabouter achter een raam of een slapende kat) die je pas ziet als je goed kijkt.
- Ontwerptekeningen van Pieck (veel op Eftepedia) als extra bron naast foto's, alleen voor vorm/sfeer; maat = foto.

Bronnen: create.roblox.com/updates/roadmap, devforum.roblox.com/t/global-illumination-research/4894935,
create.roblox.com/docs/art/modeling/surface-appearance, create.roblox.com/docs/art/modeling/reimport,
devforum.roblox.com/t/full-release-enabling-grasslength/3064300, strayspark.studio (environment art pipeline),
80.lv (forest trail vegetation), efteling.com/nl/blog/backstage/20200712-interview-sander-de-bruijn-wonder,
efteling.com/nl/over-de-efteling/sprookjes/ontwerpers, devforum.roblox.com/t/real-world-fov-field-of-view/2009285.

## WERKWIJZE 1-OP-1 PER SPROOKJE (7 stappen, elke stap een keuring)
1. **Verzamelen** (scripts): Eftepedia + Commons + 3-5 YouTube-wandelvideo's -> scherpe frames zonder mensen;
   luchtfoto/AHN/OSM-uitsnede. Daan ziet één overzichtsblad.
2. **Elementenlijst**: grond, randen, keien, planten per soort, water, hekjes, bordjes, lantaarns, figuur, zicht vanaf pad.
3. **Plattegrond op de cm**: luchtfoto overtrekken + AHN-hoogte. Keuring: bovenaanzicht over de luchtfoto.
4. **Gebouw/figuur in 3D**: zie figuren-pijplijn hieronder; gebouwen uit foto-maten (deur 3 m) + OSM/BAG.
   Keuring: silhouet op 3-5 foto's vanuit dezelfde camera + close-ups.
5. **Texturen/materiaal**: foto-projectie zonder schaduw, 4 PBR-kaarten, slijtage, grondcontact.
   Keuring: kleur/helderheid gemeten tegen de foto (reference-look-calibration).
6. **Scène**: alles van de lijst, drie lagen (detail langs pad / plantenwand / alleen kruinen), botsrand, licht, water.
   Keuring: lijst afvinken.
7. **Wandeltest**: zelfde route als een YouTube-video lopen, frames naast elkaar. Verschil -> terug naar die stap.
Eenmalig vooraf: fundament (AHN-terrein, paden, bomen), Efteling-set (lantaarn/bank/bak/hekjes/bordjes), skill
"efteling-sprookje". Eerste proef: Klein Duimpje, daarna Monstervis.

## FIGUREN-PIJPLIJN (reus, Monstervis, Magische Klok, ...): hoe we beelden echt namaken
Uitgangspunt: een beeld is een **vast, glad, beschilderd object** -> ideaal voor fotogrammetrie en image-to-3D.
Wat níet werkt (bewezen): boetseren met code (klei), Roblox generate_mesh (chibi), één foto + gokken.

**Deze Mac** (gecheckt 15 nov): Apple A18 Pro, 8 GB geheugen, macOS 26.5, Blender aanwezig; geen colmap/ffmpeg/
yt-dlp/brew. Zware AI-modellen lokaal draaien gaat niet (geen NVIDIA, weinig geheugen) -> die via online diensten.
Fotogrammetrie kan wel lokaal via Apple's ingebouwde **Object Capture** (RealityKit PhotogrammetrySession), mits
`isSupported` true geeft op deze chip; anders online fotogrammetrie of kleiner aantal frames.

**A. Beelden van alle kanten verzamelen**
- yt-dlp + ffmpeg installeren (pip/statische binaries; vraagt toestemming). Per figuur 3-8 video's (verschillende
  jaren/seizoenen/looprichtingen), elke 0,3 s een frame rond het stuk waar de figuur in beeld is.
- Script kiest: scherp (Laplace-variantie), figuur groot in beeld, geen mensen ervoor; maskers om achtergrond en
  bezoekers weg te halen. Doel 60-150 frames met overlap.
- Eerlijk: bij Klein Duimpje kijk je vanaf het pad, dus de video's dekken ~120-180 graden. De achterkant komt uit
  Eftepedia-zijfoto's, onderhoudsfoto's (Kduimpje_reusonderhoud, Bouwreus1998) en de maquette (Model_reus.jpg).
  De Monstervis en Magische Klok zie je van meer kanten -> beter te scannen.

**B. Route 1: fotogrammetrie (eerste keus als er genoeg hoeken zijn)**
- Object Capture (lokaal) of COLMAP/RealityScan, met de maskers. Uitkomst: dicht model + kleur uit de foto's.
- Video-frames hebben bewegingsonscherpte en wisselend licht: alleen de beste frames, één video per keer proberen,
  dan combineren.

**C. Route 2: image-to-3D met meerdere echte foto's (als scannen gaten geeft)**
- 3-4 beste echte foto's (voor, schuin, zij, eventueel achter) in een multi-view model: Rodin (Blender-MCP
  `generate_3d`, kost credits), Hi3DGen (skill `roblox-3d-model`, Hugging Face), of Hunyuan3D/Trellis (online).
  Geeft in minuten een vorm die al op het beeld lijkt, inclusief de kant die je niet goed ziet.
- Nooit schetsen of AI-concepten als input; alleen foto's van het echte beeld.

**D. Passen op de foto's (de 1-op-1-stap)**
- Model in Blender, 3-5 foto's als camera's nagemaakt (cam_match: positie, richting, lens; horizon-methode).
- Silhouet van het model vs. silhouet op elke foto meten (overlap %). Verschillen wegwerken met lattice/
  proportionele bewerking/sculpt, tot **>95% overlap op elke foto** (skill multiview-fit-loop).
- Maat: bezoekers (~1,7 m), deuren, of AHN-hoogte van het beeld zelf.

**E. Fijn detail**
- Ruis/hobbels van scan of AI wegwerken (glad remeshen), dan **strakke plooien en randen** opnieuw zetten
  zoals op de foto (creases, geen ruis). Gezicht, handen, voeten, bek/ogen apart met de close-up-foto's
  (bv. KleinDuimpjeHoofd.jpg, Kduimpje_duimcloseup.jpg, Monstervis_oog_2021.jpg).

**F. Klaar voor Roblox**
- LOW-versie per deel (≤ ~20k driehoeken per mesh, figuur in delen), normal map gebakken van de hoge versie.
- Kleur: foto's van alle camera's op het model projecteren, mengen op kijkhoek, schaduw eruit (delighting),
  onzichtbare plekken bijschilderen in dezelfde kleur. Roughness ~0.35-0.45 (gelakt), vuil/groen in holtes.
- 4 PBR-kaarten in SurfaceAppearance.

**G. Keuring**
- Overlay-render op elke foto + close-ups; Daan beoordeelt pas als alle overlays dekken.
- Daarna in Studio vanuit de looprichting(en) van het pad vergelijken met video-frames (wandeltest).

## HERBRUIKBARE ASSET-KIT (één keer perfect, overal gebruiken)
Elk item: echte foto's als bron, 4 PBR-kaarten, LOD, botsing apart (COLL_), in ServerStorage als bron + ScaleTo.
**Daan (15 nov): de bestaande assets zijn NIET goed genoeg; elke asset wordt opnieuw en beter gemaakt.**
`BomenBronV3`, `VVEchtePlanten`, `EftelingKlinkers`, `VV_Pleister`, `VV_Steen`, kroos/rimpels gelden alleen als
tijdelijke placeholder tot de nieuwe versie de keuring haalt; daarna overal vervangen.
Refs afvalbakken: `models/PR_Straatmeubilair/ref/commons` (Papier hier, Sprookjesbos-afvalmand).

**Kwaliteitslat per asset (keuring vóór het in de kit mag)**
- Gemaakt naar **echte foto's van het Efteling-exemplaar** (lantaarn, bank, hek, bak) of van de echte soort
  (beuk, eik, rododendron uit het Sprookjesbos-beeld), niet een generiek model.
- Naast 2+ foto's gerenderd onder dezelfde hoek en licht: vorm, kleur en glans kloppen; close-up houdt stand.
- Volledige PBR (kleur, normal, roughness, metalness), slijtage/vuil passend bij de plek, geen zichtbare herhaling.
- Bomen/planten: gescande bladeren/schors (CC0: Poly Haven, ambientCG) of eigen bladkaarten uit echte bladtrossen,
  natuurlijke takstructuur, kroonvorm volgens AHN-hoogte/breedte, 3 LOD's zonder zichtbaar wisselen, wind.
- In Roblox getest: van dichtbij (pad) en van ver, en fps gemeten met 100+ exemplaren.
- Pas als een asset dit haalt gaat hij in de kit; bestaande scènes worden daarna in één keer bijgewerkt.

1. **Straatmeubilair (Efteling-huisstijl)**: lantaarns (alle typen langs de paden; OSM: 257 stuks), bankjes,
   afvalbakken (Sprookjesbos-mand, "Papier hier"), hekjes/leuningen in elk type (Efteling-groen met bol, houten
   knuppel, smeedijzer, touwnet), paaltjes, wegwijzers en naambordjes (Efteling-lettertype), sprookjesboek-
   standaard (staat bij veel sprookjes), wachtrij-/kijkleuningen.
2. **Pad-kit**: klinkerstrook in het Efteling-verband, kasseien in bogen, flagstone, houten bruggetje-dek, set van
   ~12 ronde **randkeien** met mos (varianten in maat/draaiing), overgangsrand pad->bosgrond, afvoerrooster/putdeksel.
3. **Natuur-kit**: bomen uit AHN-maten (beuk, eik, den, conifeer, berk) elk in 3 LOD's + "alleen kroon"-versie;
   struiken (rododendron, taxus, hulst, buxus), **plantenwand-modules** (2/4/8 m, zichtafsluitend), varens, klimop
   voor muren, mos-plakken, bladhopen, wortels die over de grond lopen, stronken, takken, paddenstoelen, gras- en
   varenkaarten voor langs het pad.
4. **Water-kit**: vijveroever (kei, riet, beton-met-mos), riet, gele lissen, kroos, rimpels, druppelende/stromende
   waterval, fonteinstraal, natte-steen-materiaal.
5. **Gebouw-kit**: pannen (rood/oud), leien, riet, stuc (oud, met regenstrepen), vakwerk, baksteen in verbanden,
   ramen (glas-in-lood, luiken), deuren, schoorstenen, dakgoten, windvanen, makelaars. (Huizen gaan al redelijk;
   dit maakt ze consistenter en sneller.)
6. **Materialen- en decalbibliotheek**: CC0-scans als MaterialVariants/SurfaceAppearance (bosgrond met blad, mos,
   schors, grind, klinkers, kasseien, natuursteen, stuc, hout), plus decals: vocht, modder, regenstrepen, roest,
   vuil-in-hoeken, blad op pad, grondcontact-AO.
7. **Licht-kit**: lantaarn-licht (warm 2700 K, aan/uit per tijd), verborgen terugkaats-lampjes, licht-zones onder
   het bladerdak (Ambient/ColorCorrection), lichtvlek-decals, Lighting/Atmosphere-preset "Sprookjesbos zomer".
8. **Geluid-kit** (later): voetstappen per ondergrond, vogels, wind, water, eenden, bos-galm, zone-script dat
   sprookjesmuziek laat aanzwellen.
9. **Leven/VFX-kit**: vallende blaadjes (deels aanwezig), stofjes in zonlicht, vlinders, libellen, eenden op vijvers.
10. **Systemen**: onzichtbare botsrand langs paden, zichtafstand-culling per objectsoort (klein 200 / groot 400
    studs), wind voor planten (`StarterPlayerScripts.Wind`, bestaat al), lantaarns-overdag-uit (bestaat al).
Volgorde: 1 + 2 + 3 eerst (zie je overal), dan 6 en 7, dan 4 en 5, geluid en leven als laatste.

### Planten- en stenen-kit: ALLES eerst als Blender-asset (Daan: struiken zijn ook belangrijk)
Geen enkele boom, struik of steen meer direct in Studio of als snel model. Eerst in Blender als asset, door de
kwaliteitslat, dan pas in de kit:
- **Bomen**: beuk, eik, grove den, fijnspar/conifeer, berk, taxus-boom; jong/volwassen/oud; vol + "alleen kruin".
- **Struiken (eigen categorie, net zo belangrijk)**: rododendron (groot, bloeiend en niet bloeiend), taxus
  (vrij en geschoren), hulst, buxus (bol en haag), laurierkers, hortensia, varens (adelaarsvaren, mannetjesvaren),
  klimop als bodembedekker en tegen stammen, hosta's bij water, braam/ruigte aan randen. Elk in 2-3 maten en
  vormen, zodat herhaling niet opvalt.
- **Stenen**: ronde grijze zwerfkeien (randkeien, 12+ varianten), mosstenen, kalksteenblokken, kunstrots-stukken,
  oeverstenen met algenrand, grind/kiezels voor tussen de stenen.
- **Werkwijze per asset**: echte foto's van die soort in het Sprookjesbos (frames) -> CC0-scans als basis
  (Poly Haven/ambientCG: schors, blad, steen) of eigen bladkaarten uit echte bladtrossen -> takstructuur/vorm naar
  de foto -> PBR-bake -> 3 LOD's (dichtbij / middel / ver, onzichtbaar wisselen) -> wind (planten) -> keuring naast
  foto's + fps-test met 100+ stuks. Skills: vegetation-artist, blender-environment-kits, blender-texture-baking,
  blender-game-optimization, blender-asset-qa.

### Grond-kit: alles wat op de grond ligt (Daan: gras, modder enz. moeten ook assets worden)
Niets meer met kaal terreinmateriaal. Elke ondergrond = eigen PBR-materiaal (CC0-scan als basis, getint naar
Sprookjesbos-foto's) + losse 3D-stukken erop waar je dichtbij komt.
- **Bosgrond onder beuken/eiken**: bruin blad, beukennootjes, takjes, stukjes kale aarde; donkerder onder dennen
  (naalden, kale plekken). Losse **bladhopen** en takken als mesh langs randen en tegen stammen.
- **Gras**: drie soorten: (1) verzorgd gazon bij pleintjes, (2) schaduwgras/pollen half kaal onder bomen,
  (3) ruig gras met onkruid aan bosranden. Langs het pad als **graskaarten/pollen-meshes** (terreingras alleen ver weg).
- **Modder en kaal**: vertrapte stukken bij hoeken van paden en bij hekjes, modder rond vijvers, natte donkere aarde
  in kuilen, **plassen** (spiegelend vlakje, alleen in kuilen van paden/aarde).
- **Mos**: plakken op grond, stenen, stammen, muren (noordkant); mos in voegen van kasseien en klinkers.
- **Wortels** die over de grond lopen bij oude bomen, **stronken**, **omgevallen tak**.
- **Overgangen** (de belangrijkste): pad->blad, blad->gras, gras->modder->water. Altijd een overgangsstrook met
  blend-textuur + losse stukjes (blad op het pad, grassprietjes tussen keien), nooit een harde lijn.
- **Grondcontact**: donkere AO-vlek + ophoping (blad/aarde) aan de voet van alles.
- Bron per stuk grond: luchtfoto (gras of bos?), video-frames (wat ligt er precies), AHN (kuil/heuvel = nat/droog).

### Water-kit: vijvers en beekjes, alles erop en eraan
Bijna elk sprookje heeft water. Uit de foto's (Langnek, Klein Duimpje, Doornroosje, Zeemeermin, Pinokkio):
- **Water zelf**: troebel groenbruin, je ziet de bodem alleen aan de rand; spiegeling van bomen en lucht; bij
  fonteinen/watervallen beweging en schuim. Niet helder blauw.
- **Oevers** per type: (a) natuurkei met mos en algen (meeste sprookjes), (b) betonrand/kademuurtje met groene
  aanslag en waterlijn (Pinokkio, Zeemeermin), (c) rotsbed (kunstrots), (d) zachte oever met riet en modder.
  Altijd een **natte donkere strook** boven de waterlijn en een **algenrand** op de waterlijn.
- **Planten**: riet, gele lis, waterlelies/blad (Indische Waterlelies, vijvers), kroos in stille hoeken, varens
  en hosta's aan de oever, overhangende takken.
- **Leven/detail**: drijvende blaadjes, rimpelringen, insecten boven het water, eenden, druppelende fonteintjes,
  bubbels waar water instroomt, stroming in beekjes (bewegende textuur in één richting).
- **Vorm en hoogte**: contour uit OSM (`natural=water`), oever en waterpeil uit AHN (laser kaatst niet op water ->
  gat in AHN = waterlijn; peil = laagste oeverhoogte), diepte ondiep (~0,3-0,8 m) met bodem aflopend.

**Hoe in Roblox (afweging)**
- **Terreinwater**: echte golven/spiegeling/breking, botsing en zwemmen; maar kleur/transparantie/golven
  (`Terrain.WaterColor`, `WaterTransparency`, `WaterReflectance`, `WaterWaveSize/Speed`) gelden voor **het hele park**,
  en voxels (1,33 m) zijn te grof voor smalle beekjes en strakke kademuren.
- **Mesh-water** (gebruikt bij Langnek): per vijver eigen kleur, strakke randen, smalle beekjes; spiegeling minder
  echt, heeft dikte nodig (Roblox toont alleen voorkanten), stroming via bewegende textuur/decals.
- Voorstel: **terreinwater voor grote vijvers** (één vaste troebele parkkleur, kleine golven, weinig transparant)
  + **mesh-water voor beekjes, fonteinbekkens en kademuren**; oevers, algenrand, natte strook, planten en drijvende
  dingen altijd als mesh/decal erbovenop. Bodem: donker modder-materiaal zodat troebel water klopt.
- Keuring: render naast oeverfoto's vanaf het pad (kleur water, natte strook, plantdichtheid) + Studio-check op
  spiegeling met Future-belichting.

## Volgorde
Fase A → Fase C → Fase B per sprookje → Fase D over het hele bos.

## PRESTATIES: HOE HET NIET GAAT LAGGEN
Huidige metingen zijn al krap (Langnek 43-54 fps in Studio op deze Mac). Met een heel bos erbij moet prestatie
vanaf het begin in de werkwijze zitten, niet achteraf.
**Doel**: 60 fps op een gemiddelde laptop, speelbaar (30+) op telefoon/tablet. Testen op deze Mac (A18 Pro, 8 GB =
goede "zwakke" testmachine) + Studio Device Simulator (telefoon).

**1. Weinig unieke assets, veel hergebruik**
- Roblox tekent dezelfde MeshPart (zelfde MeshId + zelfde SurfaceAppearance) veel goedkoper als hij vaak voorkomt
  (instancing). Dus: een kit van ~10-15 boomvarianten, ~20 struikvarianten, ~15 stenen, herhaald met draaiing/
  schaal/tint (tint via SurfaceAppearance.Color, geen nieuwe textuur).
- Texturen delen: gedeelde materialen (schors, blad, steen, klinker) en atlassen i.p.v. per object eigen 1024-kaarten.
  Texturegeheugen is op telefoons de eerste grens.

**2. Detail alleen waar je kijkt (LOD + zichtafstand)**
- Elke asset 3 LOD's; eigen LOD-wissel per afstand (en/of Roblox SLIM testen) zodat je niet ziet dat hij wisselt.
- Client-culling per tag (zoals Roblox' Duvall Drive): klein detail (stenen, varens, bladhopen) weg na ~60-100 studs,
  struiken na ~200, bomen worden "alleen kruin" ver weg. Interieurs alleen binnen ~50 studs (later).
- Achter plantenwanden/buiten het Sprookjesbos: alleen kruinen (zie zichtzone).
- StreamingEnabled met Model-streaming voor grote delen; attracties als "persistent" waar nodig. Testen wat beter is.

**3. Bladeren: grootste valkuil**
- Bladkaarten met transparantie = veel "overdraw" (pixels die vaak getekend worden). Dus: alpha-cutout i.p.v.
  half-doorzichtig, niet te veel lagen kaarten over elkaar, kruin van ver als dichte vorm met weinig kaarten.
- Varens/gras alleen in de strook langs het pad.

**4. Schaduw en licht**
- CastShadow uit op alles kleins (varens, stenen < 1 m, bladhopen, gras) en op alles dat al in schaduw staat.
- Maximaal een handvol schaduw-gevende lampen tegelijk in beeld; lantaarns zonder schaduw.

**5. Botsing en fysica**
- Decoratie: CanCollide/CanTouch/CanQuery uit, CollisionFidelity Box; botsing alleen via eenvoudige onzichtbare
  COLL_-blokken en de botsrand langs het pad. Alles Anchored. Geen unions.

**6. Scripts en effecten**
- Wind alleen voor planten dicht bij de camera (BulkMoveTo, zoals nu), lage update-frequentie verder weg.
- Particles (blaadjes, stofjes) laag aantal, alleen rond de speler. Draaiende/bewegende dingen in LocalScripts.

**7. Budget per traject + meten na elke stap**
- Per traject een budget (bv. max driehoeken en aantal unieke meshes in beeld); script telt het vóór plaatsen.
- Na elke scène: fps-test in Play (met/zonder), `rbx-scene-analysis` (wat kost geheugen/render), `rbx-perf-profiling`
  (MicroProfiler: waar zit de piek), Device Simulator telefoon. Zakt het onder het doel -> eerst oplossen, dan verder.
- Grafische kwaliteit van de speler: bij lage instelling automatisch minder detail (minder varens/struiken, kortere
  zichtafstand) via een eigen kwaliteitsschakelaar.

## BOUWVOLGORDE NA DE V1'S (buiten naar binnen, grof naar fijn)
Regel: eerst wat de plek van al het andere bepaalt (grond, hoogte, paden, water), dan wat erop komt. Anders moet
elke attractie opnieuw geplaatst/aangesloten worden als het terrein verandert.
0. **Voorbereiden** (1x): skill "efteling-sprookje", scripts (frames uit video's, luchtfoto/AHN-uitsnede, overlay).
1. **Fundament hele Sprookjesbos**: AHN-terrein (heuvels, kuilen, vijverbodems), waterpeilen, alle paden uit
   luchtfoto+OSM als echte padmeshes met de juiste verharding, onzichtbare botsrand langs de paden.
   Keuring: bovenaanzicht over de luchtfoto + wandeling over alle paden.
2. **Kits** (parallel aan 1 te maken): grond-kit, pad-randen (keien), straatmeubilair, water-kit, natuur-kit
   (bomen/struiken/plantenwanden), licht-preset. Elk door de kwaliteitslat.
3. **Bomenlaag**: alle bomen uit AHN op hun plek (volle boom waar je de stam ziet, anders alleen kroon).
   Dan klopt het silhouet van het bos en het licht onder het bladerdak al vóór de details.
**Daan (15 nov): eerst ALLES buiten (scène, paden, bos, water), de attracties zelf en interieurs komen DAARNA.**
De v1-attracties blijven staan als plaatshouder (alleen op de AHN-hoogte zetten en op het pad aansluiten).
4. **Bos per traject** (trajectkaarten): plantenwanden, ondergroei, grond-overgangen, zichtlijnen, lantaarns/
   bankjes/bakken op de OSM-plekken.
5. **Scène rond elke attractie** (elementenlijst): grond, randen, water/oevers, planten, decoratie rond de
   v1-plaatshouder, zodat de omgeving al 1-op-1 klopt.
6. **Licht, lucht en water fijn afstellen** op het geheel (zones onder bladerdak, terugkaats-lampjes, waterkleur).
7. **Wandeltest buiten** over de hele route naast YouTube-video's + fps-test.
8. **DAARNA: attracties 1-op-1** (gebouwen + figuren-pijplijn: reus, vis, klok, ...), één voor één in de al
   kloppende scène; proef Klein Duimpje.
9. **DAARNA: interieurs** (Villa Volta, Assepoester, Doornroosje, ...).
10. **Leven en geluid** (geluid pas als Daan zegt dat het mag), laatste wandeltest. Eerste proef: **Klein Duimpje + Monstervis** opnieuw (meeste winst, duidelijkste fouten).

## Usage
Zwaar rekenwerk (downloads, fotogrammetrie, bakes) draait lokaal = bijna geen usage. Duur is plaatjes bekijken:
één verkleind blad per fase. Verwachting: minder rondes (v1..v5) per sprookje, dus per saldo goedkoper.
