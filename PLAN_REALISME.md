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

### Natuur: alleen bouwen wat je ziet
- Je kunt niet het bos in: **onzichtbare botsrand langs elk pad** (achter de keienrand). Dan geldt:
  1. **Strook 0-5 m van het pad**: maximaal detail. Echte plantscans, varens, ondergroei, bosgrond met blad, wortels,
     keien met mos, takken. Hier kijkt de speler; hier gaat het budget heen.
  2. **5-20 m**: een dichte **plantenwand** (rododendron, taxus, coniferen, hulst) die het zicht afsluit, zoals in het echt.
     Minder driehoeken, geen schaduw op kleine planten.
  3. **Erachter**: alleen boomkruinen tegen de lucht (AHN-posities, lichte LOD of bladkaarten) + nevel.
     Geen stammen, geen ondergroei: niemand komt daar.
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

## Volgorde
Fase A → Fase C → Fase B per sprookje → Fase D over het hele bos. Eerste proef: **Klein Duimpje + Monstervis** opnieuw (meeste winst, duidelijkste fouten).

## Usage
Zwaar rekenwerk (downloads, fotogrammetrie, bakes) draait lokaal = bijna geen usage. Duur is plaatjes bekijken:
één verkleind blad per fase. Verwachting: minder rondes (v1..v5) per sprookje, dus per saldo goedkoper.
