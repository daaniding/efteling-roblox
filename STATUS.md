# Efteling in Roblox — status en overdracht (12 nov 2026)

**Nieuwe chat: lees eerst WERKWIJZE.md (lessen + Daans wensen) en dan dit bestand. Werk na elke stap STATUS.md en het geheugen bij.**

Lees dit eerst in een nieuwe sessie. Repo: https://github.com/daaniding/efteling-roblox

## OPNIEUW BEGINNEN (16 nov 2026) — de place is helemaal leeg (daarna: licht, en nu de Pagode)
Daan: "echt alles bij 0 beginnen", daarna ook het licht en het archief weg. In Studio is gewist: alle attracties, paden,
water, bomen/groen, het terrein, het licht (Lighting op Roblox-standaard, Technology niet aangeraakt), heel ServerStorage
(ook de terrein-backups), alle scripts (ServerScriptService en StarterPlayerScripts), geluiden en MaterialVariants.
Er staan alleen nog Camera, het lege terrein, SpawnLocation en de standaard-chatinstellingen.
- **Niet meer met het Sprookjesbos beginnen** (Daan). De BOUWVOLGORDE in PLAN_REALISME.md (Sprookjesbos eerst) geldt niet meer;
  waar we wél beginnen, beslist Daan.
- De bronbestanden in de repo (models/, tools/, reference/) zijn er nog. Alles hieronder is de stand van vóór 16 nov.
- Tot Daan de place opslaat, staat de oude versie nog online (en daarna in de versiegeschiedenis van Roblox).

## Lichtproef (16 nov 2026) — weggehaald (Daan), bevindingen hieronder
22 blokbomen tussen camera en zon, huisje (deur naar de zon, raam zuid, warm PointLight binnen met schaduw), lantaarn
(PointLight 20 stud, schaduw) en een witte muur. Bevindingen bij de schemering:
- Lage zon geeft lange schaduwstrepen van stammen met zonlicht ertussen: werkt mooi. In een echt bos ligt bijna alles in
  de schaduw; daar per plek nog kijken.
- Lantaarn en verlicht raam geven precies het warme avondgevoel (lichtvlek + schaduw van de paal). Lampen met schaduw
  alleen waar je dichtbij komt (kosten).
- De paarse kleurwaas (ColorCorrection) kleurt alles, ook interieurs en bruine stammen roze. Later misschien het paars
  meer in lucht/schaduwlicht leggen en de waas neutraler, zodra er echte materialen staan.
- Roblox kaatst geen licht terug van muren; waar nodig nabootsen met zwakke lampjes.

## Schemering (16 nov 2026) — Daans keuze: "echt die dusk"
- Lichtstand `schemering` in `models/LI_Licht/roblox/licht.luau` (middag blijft als tweede stand). Echte foto-lucht
  belfast_sunset_puresky (CC0), zon op de horizon (2,1 graden, ClockTime 17.8439), gouden horizonstreep, eerste sterren,
  GEEN Atmosphere (die maakte de horizon melkwit), meer gloed en zonnestralen, iets verte-waas.
  Daarna (Daan: "net iets te donker, denk aan paars"): belichting +0,85, paarse OutdoorAmbient en een paarse kleurwaas.
  Daarna ("dromeriger en iets lichter"): belichting +1,15, zacht contrast, sterke gloed, meer verte-waas en een dunne
  nevel -> lichtende lila horizon (de gouden streep is daardoor lila; terug = atmosfeer op nil in licht.luau).
  Daarna mijn voorstellen (Daan: "doe"): geen sterren zolang de zon op is, kleinere zon, koeler groen gras (graskleur
  hoort nu bij de lichtstand), minder verte-waas, lichtere paarse waas (zonbeschenen kanten werden fel roze).
  Daarna ("iets paarser nog"): kleurwaas (224,212,255) -> mauve lucht i.p.v. zalmroze.
  Daarna ("te donker, het moet echt gezellig zijn en dromerig"): belichting +1,5, Brightness 3, warm-lila schaduwlicht,
  warmere kleurwaas met iets meer kleur.
  Daarna ("aan de ene kant goed, andere kant te donker"): schemerlucht v3, de lucht tegenover de zon in de skybox x2,2
  opgehelderd (vloeiend naar 1 bij de zon; 01_skybox.py kreeg een 'ophelder'-argument).
  Daarna (lichtproef: alles werd roze, ook binnen): het paars zit nu in de lucht zelf (skybox v4, kleurfilter 0.86/0.82/1.12)
  en in het buitenschaduwlicht; de kleurwaas over het beeld is bijna neutraal en het binnenlicht warm. Interieurs blijven
  warm wit, buiten blijft het paars-dromerig.
  Daarna ("soms overbelicht"): belichting 1,25, gloed alleen boven drempel 1,5, minder glare. Gemeten richting zon:
  bijna-witte lucht 8,8% -> 3,4%, gras even licht. Dit is de huidige schemering.
  Later: warme lantaarns/verlichte ramen tegen de paarse lucht zodra er paden en gebouwen staan.
- Gemeten: onder ~5 graden kleurt Roblox de skybox zelf oranje/rood. Daan koos juist dat beeld. Een pastel-lila
  variant (ClockTime 17.3) staat klaar in textures/schemering/asset_ids.txt.
- Gras: ruwheid Grass004 was te glad (0,26: nat-asfalt-streep bij lage zon) -> nu 0,75-0,95 (GR_gras004_ruwheid_mat).

## Gras en grond (16 nov 2026)
Daan: "gras is echt heel onrealistisch in roblox ... echt grasprietjes". Zie `models/LI_Grond/roblox/README_studio.md`.
- Bodem: echte CC0-fotoscans als MaterialVariant (gras Grass004, bosgrond forrest_ground_01), patroon Organic (geen tegels).
  De oude ambientCG-texturen (Grass001/005) vond Daan lelijk en laadden niet meer.
- Roblox' eigen grassprieten (Terrain.Decoration) uit: plat en cartoonachtig. In plaats daarvan eigen 3D-grasplukjes
  (Blender, 50 dunne gebogen sprieten, kleur gemeten uit de foto) die een clientscript alleen rond de speler neerzet.
- Proefveld (terrein: gras, 2 heuveltjes, grindstrook) staat nog in de wereld om rond te lopen; weghalen na Daans oordeel.
- Nog te doen: ruig/lang gras voor randen, bloemetjes/klaver, en de overgang 3D-gras -> foto nog zachter.

## De Pagode (16 nov 2026) — eerste attractie van de nieuwe opbouw, stukje voor stukje (models/AR_Pagode)
Daan: proef-attractie buiten het Sprookjesbos, "met al je tactieken", stand OMHOOG, statisch. STAAT IN STUDIO (workspace.Pagode + PagodeStation); Daan moet de place nog opslaan.
Grond/gras/3D-gras zijn uit Studio gehaald (Daan niet tevreden over de grond); bestanden staan nog in models/LI_Grond.
- Bronnen: 63 Eftepedia-plaatjes (ref/eftepedia, lemma.txt met alle maten), 4 Wikimedia-foto's, 3 YouTube-video's
  (on-ride Efteling _Wz0aORIVaM, 4K POV 5spp16f9Dfg, "Ontdek de Efteling - Pagode" fmEZsIkqsl8; frames in de scratchpad,
  tools/video_frames.py). Geen openbare bouwtekeningen gevonden; wel het schema Pagode_tech.png en de Intamin-productmaten.
- Maten (asset-brief.md): tempel 17 m doorsnede, 15 m hoog (schotel 1.5 + 13.7 tot de naald), platform omhoog 45 m,
  arm 43 m van as tot gondel, contragewicht 8 m achter de as, put 10 m. Boven het dek (video 6:40-6:50, vrouw als maatstok):
  balustrade 1.3, plafond 2.4, gevelvoet 2.6, gevelpunt 4.6, palen om de 2.4 m (~21 gevels). Dek 0.7 boven de schotelrand.
- Stukje 1 (gondel) BLOKKERING klaar: build/02_blockout.py -> AR_Pagode_master.blend; vergelijking review/02_blockout/blad.jpg.
  Silhouet hoogte/breedte 0.747 (foto 0.778, -4%: binnen de 5% voor blokkering). Schotel-onderkant 0.130 vs 0.152: kijkhoek
  van de foto onzeker, niet de vorm.
- Stukje 2 (vormen gondel) klaar: build/03_forms.py (draaien NA 02_blockout.py), 394 objecten met een 'rol' per onderdeel
  voor de materialen. 22 dakkapellen (telling zijfoto 12 punten/180 graden) met sierveld, brede rode windveren, groene
  binnenlijst, hol pannendak, nok, witte vlam (zwiept naar buiten), witte haken + gouden kielhanger; groene goot, ringdak,
  groene schutting (onder de gevelpunten: van opzij niet zichtbaar, van boven wel), rood ribbendak, 16-hoekige trommel met
  pilasters, drie klokdaken met ribben en 8 witte hoorns, open groen hek met spijlen, 24 ribben onder de schotel.
  Vergelijking: review/03_forms/blad.jpg (video-still, foto van onder, luchtfoto).
- Stukje 3 (kleur en textuur gondel) klaar: build/04_texturen.py + 04b_fototexturen.py (sierveld uit video 6:45, trommel uit
  Pagode-toren-close.jpg: Daan koos foto's; bronnen in models/AR_Pagode/BRON.txt), build/05_materials.py (14 rollen, UV per soort:
  driehoek, veer, paneel per trommelzijde, cilinder, doos), build/06_render.py (Cycles onder de echte HDRI-lucht, Standard-weergave;
  AgX bleekt rood/oranje uit). Trommel is ACHThoekig en onder wijder (close-up), niet 16-hoekig.
- Z-fighting (Daan: "geen z-fighting"): build/07_zfighting.py zoekt samenvallende vlakken tussen onderdelen. Opgelost: krullen van
  buurgevels vielen samen, pilasterdoppen op trommel/band, spijlen in palen, palen/bank/trommeltjes/spits precies tegen vlakken
  (nu 3-8 cm overlap). Uitslag: 0 zichtbaar; 24 'tegen elkaar' = ribben die in het dak zakken (binnenin, onzichtbaar).
  LET OP: geen commentaar midden in een regel zetten bij tekstvervanging (brak twee keer een aanroep).
- Stukje 4 (arm) klaar: build/08_arm.py. Ontdekt: de onderkant is een HOLLE paraplu (schema + foto van onder: de arm verdwijnt
  achter de voorrand), geen bolle schotel; naaf 2.5 m boven de rand. Arm = kokerbalk 1.6 x 1.2 m, creme met oranje randstrepen en
  een rij spitse oranje bladmotieven (Pagode.jpg). Kort stuk 7.2 m onder 34 graden (FOTO gaat voor; schema zei 9.3 m / 43.5),
  vloeiende knik (r 2.5), lang stuk 37 m naar de draaias recht onder het gondelmidden, daaronder 5 m door naar het contragewicht.
  Draaias 40.8 m onder het dek; met platform op 45 m ligt de as ~4.2 m boven de grond (schema ~3 m): voetstuk bepaalt dit.
  Z-fighting na de arm: 0 zichtbaar. Vergelijking: models/AR_Pagode/review/08_arm/blad.jpg.
- Stukje 5 (voet) klaar: build/09_voet.py. Put 16 x 6 x 10 m (groene wanden, roosters, zwarte hekken), pijlers, as en lagers,
  2 witte hefcilinders met chromen zuigerstang (Pagode_tech.png), groen contragewicht 6 x 4.2 x 5.6 m, sleuf naar de bak.
  Plek uit luchtfoto PDOK 10 cm + AHN (ref/luchtfoto, ref/ahn): draaias park (320.5, 58.5), bakmidden (360.0, 47.5).
  LET OP: de luchtfoto toont de opgeheven gondel 10 m naar het zuiden verschoven (reliefverplaatsing); de as staat waar de sleuf eindigt.
- Stukje 6 (station) klaar: build/10_station.py (eigen frame, collectie STATION): bak met natuurstenen wand, vlonder met groen hek,
  8 klinkertreden van de tribune, stalen kolom met bordes en trap, bord PAGODE.
- Export: build/11_export.py -> exports/AR_Pagode_gondel.fbx (26 delen, 54.480 driehoeken) en AR_Pagode_station.fbx (12 delen,
  11.328). Per materiaal samengevoegd, max 9.500 driehoeken per deel, bochten grover (125k -> 54k). Ids in exports/asset_ids.json.
- In Studio: roblox/maak_plaatsscript.py schrijft roblox/plaats_pagode.luau (laden, aankleden met texturen/kleuren, plaatsen,
  terrein uit de AHN-DTM met gras/verhard uit de luchtfoto, spawn op de tribune). roblox/afwerking_pagode.luau: onzichtbare
  reling op de gondel en bij de bak, kernwand botst, 22 ronde plafondlampjes met warm licht, lichtsnoeren langs de 44 windveren,
  rode lichtlijn onder het platform. Klinkers iets gedempt (gloeiden onder belichting 1.25 + bloom).
- Gecontroleerd: tribune en vlonder vrij van terrein, onderkant van onder leesbaar (hol, rode rand), speltest 58 fps bij het
  station (GPU 7.5 ms).
- Nog open (later, als Daan wil): zwarte stalen liggers onder de loopgang.
- RIT WERKT (17 nov), Daan: "laat eerst de attractie werken, de scène later". Ritverloop uit de on-ride video _Wz0aORIVaM:
  instappen 25 s (hekken open), sluiten 5 s, omhoog 55 s, boven 180 s, omlaag 55 s; een volle draai over de rit (~1.9 gr/s boven).
  - 11_export splitst LOW in AR_Pagode_gondel / _arm (arm, contragewicht, cilinderkoppen) / _voet; hefcilinders in Roblox als
    huis + zuigerstang die meeschuiven (export_info.json "cilinders"). Ids in exports/asset_ids.json.
  - roblox/maak_ritscript.py -> pagode_rit.luau (opzet: workspace.Pagode = Voet, Arm, Gondel, Cilinders, Station, AsFrame) en
    zet ServerScriptService.PagodeRit (bron roblox/PagodeRit.server.luau). Gondel = losse groep gelast aan "Kern", gestuurd met
    starre AlignPosition/AlignOrientation (echte snelheid: spelers rijden mee); arm verankerd, elk frame PivotTo om de draaias.
  - Stand beneden: 98.3 gr gedraaid (dek op instapniveau NAP 11.3); de armmaat uit de foto komt 2.74 m tekort tot het bakmidden:
    kleine schuif die pas onderin meetelt (t^4). Gondel botst niet met de wereld (botsgroep PagodeGondel), wel met spelers (PagodeSpeler).
  - Getest in Play: gondel exact in de bak (0.00 m), dek NAP 11.30 -> boven NAP 55.0, waterpas (0.000 gr), speler op het dek rijdt
    mee (op de client: vloer WoodPlanks, 1.0 m boven het dek); na de rit terug op dezelfde plek en stand, hekken weer open.
  - Herzien (17 nov), Daan: "super overbelicht, hij trilt en ik zak weg". Oorzaken: losse physics-gondel wordt door Roblox anders
    belicht (onderkant uitgebleekt), servergestuurde beweging komt met vertraging bij de client (trillen, speler loopt achter).
    Nu: alles verankerd; ServerScriptService.PagodeRit zet alleen RitStart (servertijd); StarterPlayerScripts.PagodeRitClient
    (bron roblox/PagodeRitClient.client.luau) rekent de stand uit GetServerTimeNow(), verplaatst gondel/arm met BulkMoveTo
    (PreSimulation) en neemt de eigen speler mee als die op het dek staat (raycast omlaag). Pagode-model op
    ModelStreamingMode Persistent (de place streamt; anders kwamen cilinders/gondeldelen niet op de client).
    Getest in Play: speler blijft op 6.90 m uit het midden (was 1 m schuiven), 0.92-1.00 m boven het dek, max 5 cm per frame;
    onderkant weer donker. Nog geen geluid of ritbediening.
  - Lichten (17 nov), Daan: "als die aangaat overbelichten die lichten heel erg". Een rijdende gondel is voor Roblox een
    bewegend object zonder eigen schaduw: de 22 plafondlampjes (PointLight 1.2, bereik 14, geen schaduw) straalden door het dak
    naar buiten, binnenwerk gloeide oranje. Nu 8 zachte lichten (0.6, bereik 9) MET schaduw, lichtsnoeren getemperd
    (Transparency 0.35, warmer). In afwerking_pagode.luau en daarmee pagode_rit.luau vastgelegd; in Studio toegepast.
- Ingang en uitgang op maat, plein weg (17 nov), Daan: "niet dat plein, haal dat allemaal weg; ingang en uitgang die gebruikt
  kunnen worden, elke cm checken, op schaal" (keuze: echte route; echte maten, looppaden minstens 2 m).
  - build/poorten.py: 4 poortjes tussen de rode palen van de gondel: in0/in1 (park 131.7 en 148.1 graden, bordeskant),
    uit0/uit1 (-15.6 en -31.9, naast de uitgangstrap op -20); 1.7 m vrij. Gondel draait per rit precies 1x: poortjes komen terug.
  - build/03b_poorten.py knipt de balustrade open + poortpalen; 10_station: openingen in het stationshek; 18_route.py haalt plein,
    Toko, terras, Gondoletta, tuin, banken, pot en pleinlantaarn weg en zet gangetjes van zwarte hekjes naar in0/in1.
  - Route: wachtrij bovenaan via de trapstrook door de tourniquets (bordeshek dicht tot de trapstrook, hekjes naast de
    tourniquets); tourniquets 1.60 m vrij.
  - build/19_maatcontrole.py -> review/19_maten.md: 41 metingen, 0 fout (treden tribune 15 cm/1.0 m, uitgangstrap 18.3/33 cm,
    poortjes 1.70/1.58 m, gangetjes 1.76 m, relingen 1.07-1.18 m, vlonder = bordes = dek = NAP 11.3, kieren 0.30/0.02 m).
    Bewuste afwijking: wachtrijbanen 1.945 m vrij (2.0 hart op hart; tribune ligt vast op 11 rijen van 1 m uit de AHN).
  - Onzichtbare botsing langs alle hekken/relingen (exports/omgeving_hekken.json, 67 stukken) en klaphekjes in de gondel die bij
    het instappen 85 graden naar binnen draaien (PagodeRitClient); reling/bakrand in 1.25-graden-stukken met poortopeningen.
  - Blokkade bij het poortje was het meeneemscript: het zette elk frame de CFrame van de speler op het dek, ook bij stilstand,
    en dat blokkeert lopen. Nu alleen als de gondel echt beweegt.
  - Getest in Play, ALLES OK: spawn -> aanlooppad -> onder het bord -> laantje -> onderpad -> trapstrook -> tourniquets -> bordes
    -> gangetje in0 -> poortje (hekjes open) -> dek rond -> uitstappoortje uit0 -> vlonder -> uitgangstrap -> uitgangspad.
    Met dichte hekjes kom je de gondel niet uit; tijdens het stijgen staat de speler 0.97 m boven het dek (rijdt mee).
  - Omheining (17 nov), Daan: "gaten, slecht afgewerkt, hekjes soms en dan kan je er nog langs". 18_route zet nu hekken langs:
    buitenrand aanlooppad, eind laantje -> onderpad -> zuidrand tribune, bordes-zuid tot de sleuf (dicht langs de tourniquets),
    vlonder zuid/west (open rand), scheiding uitgangs-/instapkant op de vlonder (99.6 gr) en het perk. 124 hekbotsingen.
    Gecontroleerd in Studio: gatenscan (1245 punten, vloer overal op hoogte; meldingen alleen meetartefacten bij muur en trap),
    ontsnappingsscan (vanuit het laantje 1250 cellen bereikbaar, 0 op gras behalve via ingang/uitgang) en sluiproutescan
    (tourniquets virtueel dicht -> bordes, poortjes, vlonder en uitgang onbereikbaar: geen weg om de tourniquets heen).
  - Afwerking (17 nov), Daan: "er komt nog steeds gras doorheen en de hekjes connecten niet met de muur". Laantje is nu EEN
    doorlopende klinkerstrook met vloeiende randen (losse stukken per rij gaven zaagtanden met gras ertussen), tuinkant 0.6 m door
    tot onder rotsen en reling; onderpad tot r 27.15 onder het buitenhek; terrein daaronder omlaag (maak_plaatsscript: aL - 3 gr).
    Zuidhek op de rand van de rijen (was 15 cm ernaast op het gras); hekeinden aansluitend gemaakt (gangetjes tot het stationshek,
    hek op de laanmuur en trapreling tot r 25, uitgangstrap-leuningen met botsing en aansluiting op het muurhek, afsluiting aan de
    andere kant van de armsleuf). Controle losse hekeinden (script): alleen nog bewuste openingen. Scans opnieuw: 0 lekken, geen
    sluiproute langs de tourniquets.
  - Wachtrijrelingen (17 nov), Daan: "deze moet aan rechts connecten, anders kan je er langs met een shortcut". De zigzagrelingen
    liepen tot 152.6 gr; nu tot tegen het zuidhek (A_ZUID - 10 cm), keerpunten van 2 m om en om. Aansluitstukjes automatisch
    (18_route: hekeinden 2-60 cm van een ander hek). Omgeving 119771598110089, 150 hekbotsingen. Loopscan (BFS 0.5 m, 3 hoogtes):
    rij r 20.5 pas na 68 m lopen bereikbaar, 0 lekken naar het gras. Trapstrook (onderpad -> recht omhoog naar de tourniquets)
    is open zoals in het echt (zigzag = drukte-wachtrij); dichtzetten is een keuze voor Daan.
  - Trapstrook onderaan dicht (17 nov, Daan: "ja, dichtzetten"): hek op r 24.95 van laanmuur tot trapreling (18_route
    om_trapdicht). Iedereen loopt nu de hele zigzag. Omgeving 137933384153007, 151 hekbotsingen. Loopscan: rijen op volgorde
    bereikbaar (38, 42.5, 68, 71, 92.5, 94.5 m), tourniquets pas na 106 m, 0 lekken.
  - Onzichtbare muren (17 nov, Daan: "je moet echt de route volgen"): alle hekbotsingen 24 studs hoog (niet meer over
    hekken springen), groep Routemuur; wie meerijdt krijgt groep Rijdend (PagodeRitClient) en botst er niet mee, want de
    gondel zwaait door de stationshekken. Springscan (BFS, springen over alles < 7 studs): vanuit de wachtrij met ingang en
    tourniquets virtueel dicht onbereikbaar: bordes, vlonder, uitgang, gras. Vanaf het gras en vanaf de uitgang de wachtrij
    en de instapkant niet in. Play: springen tegen reling, zuidhek, onderpadhek en bordeshek houdt overal stand.
  - Trapkop (17 nov, Daan: "lastig om doorheen te komen en ik kom gelijk tegen dat huisje aan"): de opening van de bovenste
    baan naar de tourniquets was 1 m met de bronzen lantaarn erin; nu de hele baan open (2.0 m, trapreling begint op de
    rail van rij 2), lantaarns op r 16.2 en 18.6 op de trapreling. Controlehuisje uit de looplijn: naast de tourniquets
    (r 11.42, 106 gr, recht op het station), 1.2 m vrij, met botsing rondom. Play: avatar loopt bovenste rij -> trapkop ->
    tourniquets -> gangetje -> poortje zonder vast te lopen; meerijden met de nieuwe muren: drift < 0.1 stud.
    Omgeving 83791895400022.
  - Laanmond (17 nov, Daan: "die paaltjes weg en die fence moet niet zo ver doorlopen"): de twee paaltjes in de mond van
    het laantje weg; tuinreling begint nu op de hoek met het aanloophek (r 17.75, was r 16 en stak de doorgang in).
    Omgeving 87273054965086.
  - Poortjes (17 nov, Daan: "als de attractie omhoog is hoort niemand erdoor te kunnen; als hij er is gaan er 2 hekjes open,
    die van de attractie en die van de wachtrij"): klaphekjes in het stationshek (Station.Stationpoorten, 2 bladen per poortje
    op de poortpalen r 9.05, draaien naar buiten het gangetje/de vlonder in), open en dicht tegelijk met de gondelhekjes
    (alleen tijdens het instappen). Botsing van bakrand, stationsbladen (groep Routemuur) en gondelbalustrade + gondelbladen
    nu 24 studs hoog: niet meer de bak in springen of over de balustrade. Play: gondel omhoog -> door poortje lopen/springen
    stopt op r 9.45 (in0, uit0, westkant); gondel beneden -> beide hekjes 85 gr open, avatar loopt in 1.4 s het dek op;
    meerijden: drift 0.1 stud.
  - Terrein vlak (17 nov, Daan: "waarom staat die niet gewoon op een recht stuk" / "mooi donker groenig gras"): AHN-bulten weg,
    vlak gras op NAP 9.8 (meet ~9.4-9.6, voxelraster) rond de Pagode en in de rand; uitsparingen onder bestrating en de
    armsleuf ongewijzigd. Uiteindelijk (Daan: "fris lichtgroen", "doe gewoon plat"): effen Grass, kleur 96,170,64, geen sprieten. LeafyGrass
    (roze vlekjes) en een eigen gazontextuur (build/20_gazon.py, MaterialVariant) geprobeerd en weer weggehaald. maak_plaatsscript: VLAK = true.
  - Verbeterpunten (17 nov, Daan): (1) perk/modder ook aan de zijkanten dicht (18_route om_perk_bordes 99.6 gr en
    om_perk_uitgang 54.2 gr); (2) controlehuisje naar video 0:44: getrapt kroondak (groen/rood/goud), groene koepel met gouden
    spits, witte vlamhoorns op de hoeken, witte binnenlijsten, binnen lessenaar met knoppen, scherm, stoel en lamp (geen dichte
    blok meer); (3) stalen trap + bordes midden in de bak weg (10_station; de gondel ging erdoorheen); (4) gondel dicht:
    onzichtbare massieve kern (r 16.4 studs) en plafondschijf op dek + 7.4 studs, bewegen mee; (5) uitgang duidelijk: poort
    met breed UITGANG-bord + groene pijlen over de uitgangstrap (04c PG_uitgangsboog), tweede staand bord bij uit0;
    (6) eenrichting (PagodeRitClient, map Pagode.Eenrichting): schot bij de tourniquets gaat dicht zodra je erdoor bent,
    schot op de kop van de uitgangstrap is standaard dicht en alleen open als je boven op de vlonder staat; (7) ritduur naar
    de echte 5:10 (coaster.cloud): boven 200 s (was 180). Play (met echte sprongen): plafond houdt sprong op 3 studs, kern
    stopt op r 5.8, terug door tourniquets / terug de uitgang op / van buitenaf de uitgang op / perk in: allemaal
    geblokkeerd; meerijden drift 0.1 stud. Omgeving 115622496482577, station 118332205413998.
  - Plafondlampen gondel (17 nov, Daan: "overbelicht"): mat creme i.p.v. Neon, PointLights 0.12 / bereik 12 (waren 0.6 / 9);
    lichtsnoeren gedempt (190,150,100, transp 0.4). Lighting zelf (Brightness 3, Exposure 1.25, Bloom 0.9) is van Daan.
  - Geluid (17 nov, Daan: "het echte geluid ... uit boxen, niet aan de andere kant van het park"): de echte Efteling-audio
    (muziek/opnames uit video's) mag niet geupload worden (auteursrecht, Roblox-moderatie); daarom gelicentieerde Creator
    Store-audio, vervangbaar via de ID's in maak_ritscript (GELUID-tabel). Pagode.Geluid: 6 zwarte speakerkastjes aan de
    lantaarnpalen langs de wachtrij met muziek (APM "Milarepa" 1837145328, InverseTapered 10-75 studs = stil na ~25 m,
    synchroon), machinebrom bij de draaias (PSE 9125767459, volume/toonhoogte volgen de armsnelheid, tot 160 studs), bel bij
    vertrek (PSE 9119642644, begin "sluiten") en hekgeluid bij open/dicht (PSE 9116875342) bij het station, wind voor
    meerijders hoog (PSE 9112777914, 2D). Play: alles geladen, bel en hek op tc 25, brom 0 -> 0.88 tijdens omhoog,
    speakers binnen 0.06 s gelijk. Daan moet de muziekkeuze nog beluisteren.
  - Wachtrijmuziek (17 nov): echte Pagode-muziek niet bruikbaar (auteursrecht). Meting van de video-audio (scratch
    analyse.py): pentatonisch F-G-A-C-D (F groot / D klein), ~88 bpm met doortikkende achtsten, hoge melodie C5-A5, lage
    drone C2/D2, warm (energie < 2 kHz). Gekozen uit de gelicentieerde APM-bibliotheek: "Peach Blossom Spring" 1840540291
    (280 s). Alternatieven (laden allemaal): Plum Blossoms 1845854732 (165 s), Faint Moonlight 1845854743 (142 s), Kinuta
    1845854711 (155 s), Fantasy Of Waves 1845916643 (138 s), Monkey King 1837190707 (108 s), Mandala 1840706030 (114 s),
    Lightly Magical 1837777641 (149 s), Fairy Doll 1846356693 (156 s), World Of Wonder 1836330626 (143 s).
  - Geluid deel 2 (17 nov, Daan: "moet echt andere muziek, niet zo rustig", "mensen horen praten", "loop sound
    realistischer"): MuziekKiezer (LocalScript, alleen in Studio): in Play M = volgend nummer op alle speakers, naam
    linksboven; 12 levendigere APM-nummers, start op "One World (a)" 1839842602 (ook in maak_ritscript). Geroezemoes
    (PSE walla, 8-60 studs): tribune families 9112787259, laantje en bordes crowd mumble 9112766358 (verschoven start).
    Voetstappen (LocalScript): Running-geluid per ondergrond via straal omlaag: klinkers/steen "Brick Footsteps"
    91557584218550, vlonder/dek "Floor Footsteps" 6506537704, metaal "Concrete Footsteps" 6362185620, gras "walk_grass"
    106672010112184 (standaard klonk als plastic). Getest in Play: wisselt correct, alles geladen. Volumes gehalveerd
    (Daan: "te hard"): muziek 0.25, praten 0.15-0.22, brom max 0.5, bel 0.45, hek 0.4, wind 0.3.
  - Muziek gekozen (17 nov, Daan: "6/12"): APM "Fortune's Smiling" 1840841073 (173 s), ook eerste in de MuziekKiezer.
    Zacht lopende en pratende mensen: PSE "Street Crowd" (walla, voetstappen, kinderen, vogels, geen verkeer) bij de
    aanloop (9112879470, vol 0.16) en het onderpad (9112879448, vol 0.14, start 11 s), 8-55 studs.
  - Speakers (17 nov, Daan: "zwarte kubussen in de lucht", "moet echt uit de speakers komen", "mogen weggestopt"):
    stonden op oude lantaarnposities (sierlantaarns verplaatst). Nu verstopte stenen kastjes (natuursteenkleur, donkere
    grille, 0.3 m) laag aan de voet van de 6 lantaarnpalen (posities = exports/omgeving_lampen.json, vloer via straal),
    muziek RollOffMode Inverse 4-50 studs (1/afstand vanaf 1.3 m, stil na ~17 m), vol 0.4. Twee lantaarnlichten
    (afwerking LAMPEN) ook naar de nieuwe sierlantaarnposities.
  - 17 nov (Daan: "haal deze lantaarnpaal weg", "ik hoor de lopende en pratende mensen nog niet", "lucht blijer maar
    wel schemeren en realistisch"): lamp_zuid (r 20.12 op de rail, stond midden tussen de rijen) weg uit 12_omgeving, met
    speaker en licht; omgeving 98408927485280. Mensen harder: praten 0.45-0.6, lopen 0.5-0.55 (alles laadt en speelt).
    Lucht (place-instellingen in Studio, geen script): ClockTime 17.8, Exposure 0.5, OutdoorAmbient (140,122,118),
    Atmosfeer Color (255,184,132) Decay (72,96,150) Glare 1.4 Haze 0.9 Density 0.28 Offset 0.2, Sky "Lucht" = standaard
    Roblox-lucht zonder sterren, wolken (255,214,190) cover 0.5. Oude avondlucht: skybox in ServerStorage.Lucht_oud_avond,
    oude waarden als attributen Oud_* op Lighting.
  - Groene hekjes gondel (17 nov, Daan: "ik kan nog steeds door de groene hekjes"): de onzichtbare botsrand (reling/
    poortreling uit afwerking_pagode) stond ~120 studs boven de gondel (oud draaipunt). Nu herbouwd t.o.v. de kern
    (maak_ritscript na de Kern, map Gondel.Randbotsing): 256 delen op r 8.32 m vanaf het dek (6.58 studs), 24 hoog;
    poortjes op kernhoek 180 - alfa (gemeten aan de scharnieren). Play: rand stopt op r 7.9-8.0 (120/250/40 gr), poortjes
    in0 en in1 open tijdens instappen in beide richtingen, dicht tijdens de rit.
  - Draaien (17 nov, Daan: "moet de pagode niet een beetje draaien", keuze aan Claude): twee hele rondjes per rit
    (RONDJES = 2 in PagodeRitClient; heel getal zodat de poortjes weer voor het station eindigen), piek ~3.6 gr/s
    halverwege. Meenemen van meerijders: de "beweegt"-check zag de langzame draai als stilstand; nu exact via
    ToObjectSpace + ToAxisAngle (drempel 1e-5 stud / 1e-7 rad). Play: drift 0.1 stud tijdens omhoog met draaien.
  - Bomen (17 nov, Daan: "bomen, maar het moet echt realistisch", "kijk ook in video's"): build/21_bomen.py haalt
    posities uit de luchtfoto (groene kronen + kale loofkronen: de foto is van de winter; geen water, daken van
    buurattracties, route, station, armsleuf, hekken +1.5 m), 63 bomen (24 dennen, 39 loof) binnen 40 m, plus de grote eik
    aan het oostpad. Video: sparren naast het station 24-30 m (zo hoog als de gondel), loofbomen 16-23 m. Gondelbaan-check:
    geen boom raakt de gondel. Modellen: Creator Store PBR-packs van Letaij (Ponderosa Pine 130515502281374, Realistic Oak
    Trees 114023396228594), gecontroleerd: geen scripts; bron in ServerStorage.BoomBronnen; plaatsen = roblox/
    bomen_pagode.luau (maak_bomenscript.py). Play: 55-60 fps. Dennen minstens 4.5 m van hekken/paden (tot onderaan breed,
    hingen over de aanloop), loofbomen 1.5 m: nu 60 bomen (20 den, 40 loof).
  - Tuin terug (17 nov, Daan: "ja, doe dat" = bamboe en gesnoeide dennen langs het laantje): 18_route bewaart uit 14_planten
    bamboe, niwaki 0-2 (tuin), struiken, tuinstenen, hagen langs de sleuf en het bloemenperk (vult de "modder" naast het
    huisje); weg: oude bomen, pot-bamboe, niwaki 3-4 (stonden op het uitgangspad). Keten nu 12, 14, 17, 18, 05, 19.
    Omgeving 77125367267740 (43 delen, 141k driehoeken). Terrein in de tuin naar NAP 9.8 (was 8.95, planten zweefden);
    maak_plaatsscript: tuincap alleen als niet VLAK. Vergelijking video 0:20: laanmuur, niwaki, struiken, bamboewand, bomen
    erboven klopt. fps-meting in Studio onbetrouwbaar (venster niet in focus: 15 fps-rem).
  - Bak (17 nov, Daan: "het midden hoeft geen gat te zijn"): bakvloer van NAP 9.35 naar 10.45 (10_station Z_VLOER 0.45),
    10 cm onder de laagste onderkant van de gondel in het station (gemeten: PG_onderkant NAP 10.55; arm komt niet lager
    boven de bak). Station 103886626413495.
  - LATER (Daan: "de bebossing is voor nu goed, maar moet later misschien beter"): bomen verfijnen (meer soorten, beuken,
    exacte posities/hoogtes uit AHN-boomhoogtes of een zomerluchtfoto, ondergroei).
  - Wachttijd beneden (17 nov, Daan: "doe maar zestig"): instappen 60 s (was 25; T_IN in PagodeRitClient, hekjes en bel
    volgen mee) + 5 s sluiten; cyclus nu 375 s. Play: hekjes dicht op tc 59, bel op 60, omhoog op 65.
  - Wachten op passagiers (17 nov, Daan: "op het begin haal ik het niet om op de Pagode te komen"): PagodeRit (server)
    houdt de ritklok vast op tc 40 (instappen, hekjes open) zolang niemand op het dek staat (r < 8.2 m, dekhoogte); stapt
    iemand in, dan nog 20 s instappen, 5 s sluiten, rit. Play: zonder passagier na 45 s en 60 s nog op tc 40 (wacht=true);
    met passagier vertrokken. Attribuut Pagode.Wacht = true tijdens het wachten.
  - Bomen tijdelijk uit (Daan: "haal voor nu de bebossing weg"): workspace.PagodeBomen -> ServerStorage.PagodeBomen_uit
    (terugzetten = map terug naar workspace, of bomen_pagode.luau opnieuw draaien). Tuin langs het laantje blijft.
  - Rit-ervaring (17 nov, Daan): PagodeBeleving (LocalScript, roblox/PagodeBeleving.client.luau): omroepteksten onderin
    beeld voor wie op het dek staat. Na Daan ("camera niet top", "tekst te AI, gewoon alleen de tekst"): camera-effect weg;
    alleen tekst in beeld. Daarna (Daan: "iets vets en natuurlijk, in het Engels en dan vertalen"): bij het instappen een
    titel "P A G O D E" (Bodoni, goud, 64) met "Welcome aboard"; "Gates closing" voor vertrek; "Exit: follow the signs"
    na de rit. Engels als bron, vertaling nl in LocalizationService.PagodeTeksten (AutoLocalize). Play: titel zichtbaar
    bij instappen, nl-vertaling werkt ("Welkom aan boord", "De hekjes gaan dicht"). Geen zitbanken: in de on-ride video staan mensen langs de
    reling. Fotomoment: pas als het uitzicht (buurattracties) er is. Echte omroepstem: niet mogelijk (geen TTS in Roblox).
  - Interieur gondel (17 nov, Daan: "kan de Pagode van binnen meer detail hebben"; video instappen, Pagode-binnenzijde):
    roblox/interieur_gondel.luau (in maak_ritscript na de Kern), map Gondel.Interieur (beweegt mee): witte zitrand rondom
    de kern (0.45 m hoog, 0.5 m diep, botst; in de video loopt onderaan de rode wand zo'n witte rand), gouden randen om de
    22 plafondlampen, mintgroene bordjes met gouden lijst op de kernwand: UITGANG (bij uit0/uit1) en 3x "PAGODE - Efteling -
    1987". Kernwand-textuur (04_texturen kernwand, Daan: "ja, doe dat"): naar video loop_in s_055-s_058 geribbelde
    rode planken met donkere naden, op elke tweede plank een kolom oranje klokornamenten (knop + spits, klokvormig lijf,
    uitwaaierende vleugels, druppel) over de hele hoogte; kleur 136078988623224, normaal 86029428553252.
  - Muziek aan boord (17 nov, Daan: "waar is de muziek in de Pagode zelf"): PagodeBeleving maakt per client een Sound
    "RitMuziek" aan de Gondel.Kern (reist mee), zelfde nummer als de wachtrij: APM "Fortune's Smiling" 1840841073 (Daan),
    InverseTapered 30-90 studs; volume zwelt aan bij sluiten (0.25), rijden 0.4-0.45, sterft weg bij aankomst.
    Play: geladen, 0.24 bij sluiten, 0.45 tijdens omhoog. Start synchroon met de wachtrijspeakers (verschil 0.09 s).
  - Rit korter (17 nov, Daan: "elke draai duurt echt heel lang"): omhoog 35 s, boven 70 s, omlaag 35 s (was 55/200/55);
    cyclus 205 s. Staat gelijk in PagodeRitClient (FASEN), PagodeRit (CYCLUS) en PagodeBezoekers (CYCLUS).
  - Servergondel in de stationsstand: PagodeRit zet bij de start de hele Gondel (BulkMoveTo) van de bouwstand (hoog in de
    lucht, kern Y 130) naar de instapstand (kern Y -0.7, dek op NAP 11.3), zelfde berekening als de client. Nodig voor NPC's.
  - NPC-bezoekers (17 nov, Daan: "mensen in de rij", "ze blijven gewoon bezoekers, gaan daarna naar een andere attractie",
    "een wachtrij vullen dan de ander, recht erin staan", "het stoppen om te draaien is irritant"):
    ServerScriptService.PagodeBezoekers (bron roblox/PagodeBezoekers.server.luau + route build/22_bezoekersroute.py ->
    exports/bezoekersroute.json, samengevoegd met roblox/maak_bezoekers.py -> PagodeBezoekers.luau). Uiterlijk: 9 R15-modellen
    in ServerStorage.PagodeBezoekers (HumanoidDescription, gratis catalogusitems). Tot 14 bezoekers, die blijven leven:
    rij -> eigen plek op het dek, kijken naar buiten -> meerijden -> uitstappen via uit0 en de uitgangstrap -> ommetje door het
    park -> weer achter in de rij (later: naar een andere attractie). De rij is een looplijn met afgelegde lengte: iedereen
    staat 0.85 m achter zijn voorganger op de middellijn van de baan, vult van het poortje naar achteren, schuift pas op bij
    2.2 m ruimte; sturen 4 studs vooruit (vloeiend door de bochten). Gangetje in alleen als het dek ruim voor het sluiten
    gehaald wordt (tc < T_IN - 8). Op het dek altijd met een boog om de kern (rechtdoor = op de zitrand vast); plek aan de
    reling (r 7.1-7.7 m, binnen 35 graden van in0), draaien naar buiten. Na het losmaken SetNetworkOwner(nil) opnieuw (anders
    neemt de client ze over en lopen ze vast op het eenrichtingsschot); Eenrichting-schotten in groep Poortdeel. Meerijden: server verankert de HumanoidRootPart (attribuut Rijdt), elke client zet ze elk frame op
    K_onder -> nieuwK (PagodeRitClient). NPC op het dek (OpDek) laat de ritklok ook doorlopen. Botsgroep Bezoekers botst niet
    met Spelers, Rijdend, Bezoekers, Routemuur, Poortdeel. Play: afwijking van de looplijn max 0.44 m; rij staat ~0.9 m hart op hart vanaf het poortje; meerijders vast op r 6.4 m,
    hoogte 9.70 boven de kern, kijkrichting 1.00 naar buiten; uitstappen -> trap -> park -> ommetje -> terug bij de aanloop.

### Scène rond de Pagode (16 nov 2026), Daan: "hoe het zit met erin gaan en hoe het eruit ziet", "zou vooral video's kijken"
- Bron: video fmEZsIkqsl8 (iemand loopt de hele route; frames elke seconde: 0:03-1:02 in, 5:55-6:57 uit), Pagode-landing.jpg,
  luchtfoto, AHN. Alles in models/AR_Pagode/scene-brief.md.
- Route zoals echt: plein (NAP 9.6) -> blauw bord PAGODE -> verdiept laantje langs de keermuur (bonsai, rotsen, bamboe) ->
  tribune (11 klinkerrijen met wachtrijrelingen, trapstrook met lantaarns) -> bordes (11.3) met dubbele tourniquet en
  controlehuisje -> instappen. Uit: andere kant, vlonder, trap naar het oostpad (UITGANG-bord), eik, sparren.
- Scripts: build/12_omgeving.py (wachtrij, muren, hekken, huisje, borden, lantaarns, uitgang), 14_planten.py (bamboe, niwaki,
  haag langs de sleuf, bloemenperk, eik, Douglassparren, loofbomen), 04c/04d (bord- en planttexturen getekend),
  13_review_omgeving.py (renders vanaf de videoplekken). Tribune en bord zijn uit 10_station.py gehaald.
- Export: AR_Pagode_omgeving.fbx (26 delen, 45k driehoeken) + station opnieuw; ids in exports/asset_ids.json.
- In Studio: workspace.PagodeOmgeving + nieuw PagodeStation, 9 lantaarnlichten in Pagode.Afwerking, spawn op het plein.
- Terreinfout opgelost: het leegmaken haalde alleen terrein onder Y -8 weg, dus het oude (hogere) terrein bleef staan en
  stak als "zand" (Ground) door de klinkers. Nu: hele hoogte leeg, onder alle bestrating terrein op NAP 8.0, alleen gras.
- Ronde "muur en klinkers fijner" (16 nov): kleuren gemeten in de video (muur gem. (98, 94, 97), klinkers (120, 106, 114)).
  Klinkers nu VISGRAAT onder 45 graden zoals op het plein en in het laantje (~18 x 9 cm, mauve-bruin); breuksteen fijner
  (8 x 22 stenen per 2 m), grijs/grijsgroen/mauve/roest met smalle voegen. In Studio een warme tint (klinker 214,200,172;
  muur 206,204,180) tegen het paarse schemerlicht in. Muren krijgen de textuur langs de muur (boog of hoofdrichting).
  Driehoeken op de klinkers opgelost: (1) textuur herhaalde niet in kleur -> stenen wisselden op de tegelrand halverwege van
  kleur; (2) UV's in parkmaat (~350) te groot voor Roblox -> nu per object en projectierichting een geheel getal eraf.
- Toko Pagode + terras (16 nov): build/15_toko.py naar video 1:02 (ref/video_toko_102.jpg) en luchtfoto. Achthoekige kiosk
  (midden park (380.6, 79.3), ~12 m), laag grijs dak, creme dakrand met rode zigzag, bolle lampjes, rode palen met groene
  kapitelen, verkoopramen met toonbank en groene bloempanelen, witte klokkoepel met gouden band en spits; keuken erachter;
  4 statafels; terras met 3 rode parasols, ronde tafels en rieten stoelen; klinkers tot r 41 (42-88 graden). Texturen
  getekend in 04e_texturen_toko.py. Achter de Toko eindigde de wereld (AHN-stuk tot x 385 / y 80): nu vlak gras eromheen.
- Gondoletta-oever + bomen (16 nov): build/16_gondoletta.py naar video 4:10-5:10 (vanuit de tempel) en luchtfoto. Rond
  havenbekken (midden (397, 52.5), kade r 14.5, platform r 8.7), witte vakwerkloopbrug, rood-witte balustrades, uitstapsteiger
  met vlonder en wit hokje, 8 Gondolettabootjes, asfalt paden langs het water, 2 eilandjes, treurwilgen (PG_wilg getekend),
  bomenrand oost/noord/west. De witte tentkap van de luchtfoto staat NIET in de video (nieuwer): weggelaten.
  Water = terrein (roblox/gondoletta_water.luau, draaien NA plaats_pagode.luau). Gemeten: water rendert niet +2 stud zoals
  grond; bovenkant Y +0.28 geeft peil ~NAP 9.3.
  Studio viel weg (instantie gesloten/gecrasht) voordat ik screenshots kon maken; render-check in Studio nog te doen.
  Omgeving nu 84k driehoeken (40 delen): fps opnieuw meten.
- Ingang en wachtrij opnieuw op attractieniveau (17 nov), Daan: "de scene is zo niet het niveau van wat ik wil, de attractie wel".
  build/17_steenwerk.py (na 12 en 14, voor 05): breuksteenmuren als LOSSE 3D-stenen in horizontale lagen (maatmix 9-50 cm,
  vulstenen in de rest van de laag, 0-4.5 cm uitstekend, rafelige dekstenen), steenatlas 4x4 (04f_texturen_steen.py), gladde muren
  van 12 = donkere achterwand (rol voeg). Plantvak voor de pleinmuur (lage voormuur 0.5 m, video 0:05), rotsrijen langs het laantje en
  het onderpad, rotsen in de tuin, grijze natuurstenen neuzen op de tribunerijen (0:39). 14_planten: niwaki = scheve stam, kale
  takken, wolken van naaldplukken (PG_pluk) met donkere kern; bamboe als doorlopende wand 4-5 m (fijnere bladveren); lage struiken.
  Klinkers valer (video). Bank en pot naar voren (r 15.7). Vergelijk: models/AR_Pagode/review/17_steen/vergelijk.jpg (v005, v021).
  In Studio geladen (omgeving 54 delen, 183k driehoeken, waarvan ~82k stenen): roblox/herlaad_omgeving.luau laadt alleen de
  omgeving. Fps nog niet gemeten. Gondoletta-water staat nog op het oude peil (raycast NAP ~8.6): gondoletta_water.luau opnieuw draaien.
- Meubilair ingang/wachtrij secuur geplaatst en verfijnd (17 nov), Daan: "zet ze secuur neer, soms staan lantaarnpalen op het pad".
  12_omgeving heeft nu een looppadcontrole: elk meubelstuk wordt met vrij() geregistreerd en getoetst tegen laantje, trapstrook,
  banen tussen de wachtrijrelingen, bordes, onderpad en pad langs de uitgangsmuur; de build stopt bij een treffer (vond er 6).
  Plekken uit de video: klassieke zwarte lantaarns op de trapstrook tegen het hek op de laanmuur (0:18-0:24), sierlijke bronzen
  lantaarns in de lijn van de trapreling (0:39-0:46), lantaarn op de hoek plein/tuin (0:02), lantaarns uitgang aan de muurvoet;
  tuinlantaarn en tweede pleinlantaarn weg (niet in de video). PAGODE-bord met de voorkant naar het plein (je loopt westwaarts
  onder het bord door en slaat dan rechtsaf het laantje in), pot links ervoor tegen de pleinmuur, hoge groene bak rechts,
  3 zwarte paaltjes in de mond van het laantje. Tourniquets recht boven de trapstrook, controlehuisje er vlak achter (nieuw model:
  groen frame, rode panelen, glas met roeden, opengeklapt raam, toonbank, kroonrand PG_huisrand, gouden knoppen, plat dak).
  Palen met voetplaat/kraag/hals/bol, dubbele bovenregel op de spijlenhekken, spijlenpaneel langs de trapstrook, afvalbakken
  met lijsten en embleem, banken met latten en gietijzeren zijstukken. Rotsen ontwijken het meubilair (exports/omgeving_meubilair.json).
  Lichten in Studio bijgewerkt (afwerking_pagode.luau LAMPEN). Vergelijk: models/AR_Pagode/review/18_meubilair/.
  Omgeving 58 delen, 191k driehoeken; fps nog niet gemeten.
- Looppaden breder voor Roblox-avatars (17 nov), Daan: "ik kom niet door de ingang, breder en goed afgewerkt". Avatar is 3.8 stud
  = 1.27 m breed (echt mens ~0.5 m): laantje 1.8 -> 3.0 m (B_LAAN), trapstrook 1.5 -> 2.2 m (B_TRAP), wachtrijreling op elke tweede
  rij (banen ~2 m, keerpunten 2 m), tourniquets 1.6 m uit elkaar, huisje 1.2 m erachter, 2 paaltjes 1.6 m uit elkaar.
  Aanlooppad plein -> laantje nu een brede klinkerstrook (r 14.15-17.5) met granieten opsluitbanden langs het gras; lantaarn,
  bak, pot en bordpalen in de randstroken (looppadcontrole kent nu ook "aanlooppad"). Bamboe pas vanaf r 22.5, struiken en
  tuinrotsen vanaf r 18.2, randrotsen pas na het aanlooppad. Spawn stond tussen een terrastafel met stoelen: nu op het open
  plein (362.9, 68.3), kijkend naar het bord; derde parasol naar het terras (372.5, 68.9). Gondoletta-water opnieuw: peil NAP 9.43.
  Looptest in Play met Humanoid:MoveTo: spawn -> aanlooppad -> onder het bord -> laantje -> onderpad -> trapstrook -> tourniquets ->
  bordes: alles bereikt. Fps: Studio meet 15.0 als het venster niet vooraan staat (rem); echte meting met Shift+F5 door Daan.
  Let op: de hele PagodeOmgeving stond geselecteerd en was ~13 m verschoven; teruggezet op pivot (1080, 2, -142.5), 180 graden.
- Nog te doen: rieten stoelen netter (nu blokjes), koepel iets minder spits, onzichtbare botsing langs de hekken. Eerder genoemd nog open:
  met terras, Gondoletta-oever, onzichtbare botsing langs de hekken en relingen (nu loop je erdoor).

## Licht (16 nov 2026) — eerste stap van de nieuwe opbouw
Daan: "we beginnen met de lighting ... ultra realistisch". Script: `models/LI_Licht/roblox/licht.luau` (opnieuw toe te passen).
- LightingStyle Realistic + PrioritizeLightingQuality (= oude Future, door Daan gezet). Kaatsheuvel 51,65 N, ClockTime 14,184.
- Echte lucht: Poly Haven CC0-HDRI kloofendal_48d_partly_cloudy_puresky -> 6 skyboxvlakken (`build/01_skybox.py`, ACES-tonemap,
  onder de horizon nevel i.p.v. gespiegelde 'zee'). Skyboxvlakken gemeten met testplaatjes: Lf=+X, Rt=-X, Ft=-Z, Bk=+Z.
  De skybox is gedraaid zodat de Roblox-zon precies op de zon van de foto valt (gecontroleerd met een shot recht in de zon).
- Atmosphere licht van kleur (donkere Decay gaf een blauwe band boven de horizon), ColorGrading Default, lichte ColorCorrection,
  Bloom alleen op hele heldere dingen, subtiele SunRays en scherptediepte. Roblox-wolken uit (wolken zitten in de foto).
- Gemeten: schaduw op gras 17% van zonlicht (echt 15-25%); wit in de zon niet uitgebrand; metaal weerspiegelt de echte lucht.
- First person (Daan): StarterPlayer.CameraMode LockFirstPerson, eigen lichaam zichtbaar, FOV 78, lichte loopbeweging,
  WalkSpeed 10. Script ook in `speler/EerstePersoon.client.luau`.
- Daan keurde het licht goed ("Goed, proefplek weg"); proefplek en proefterrein zijn weggehaald. De wereld is weer leeg
  (alleen SpawnLocation, zichtbaar en botsend zodat je bij Play niet valt) met het nieuwe licht.

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
- v13/v14 (Daan: foto van de hoek, `ref/hoek_daan.webp`): randpaden voorbij de herauten weg (OSM: alleen een uitsteeksel voor de herauten).
  Hoek nu als de foto: bestrating (grind) voor de noordarm en in de hoek voor de toren; voor de westarm een gazon (s 2.4..12.3) met een laag
  bakstenen randje langs de bestrating; zigzagbank op de grens + buxuskegel; lantaarn met krularm (grijze paal, één vierkante lantaarn) aan de
  gazonrand i.p.v. de galgenlantaarn. Geen kantelenmuren rond het plein (alleen 1952-~1960). Asset **83896085574394**.
  Screenshot `review/studio_v14_hoek.jpg` (zelfde standpunt als de foto).
- NOG/kan beter: gezicht nog stijf (glimlach, oogleden), pluim meer als één krullende veer,
  Prinsenpoort (aparte attractie) ontbreekt links.

## Prinsenpoort (chat 8, 13 nov) — v1 in Studio
Map `models/AR_Prinsenpoort/`. Bronnen: 22 Eftepedia-plaatjes (lemma's Prinsenpoort + Herautenplein), OSM 967458492; brief `asset-brief.md`.
Plek gecontroleerd: OSM-footprint, OSM-pad 967458491/490 door de doorgang, toren met gouden prins aan het eind van de noordmuur op
Herauten-overzicht-okt2009, en "na de poort links naar de Indische Waterlelies" (62 m noord) klopt.
- Frame: oorsprong OSM (50.53, 76.22) = studs (151.58, -228.65), grond Y=2; -Y = voorkant naar het plein, F roblox (-0.968, 0, 0.250).
- Maten uit de 1957-foto (bezoekers in de boog): middenpoort 4.9 x 4.4 (diepte = OSM), dakvoet 3.5, rondboog 3.1 breed / 2.85 hoog,
  schilddak met nok tot 6.0 + klokkentorentje met spits 7.4; torens r 1.0 op x ±3.35, muur 4.05, kegeldak tot 6.75 + gouden prins te paard.
  Lantaarn links van de boog, groen luik in de doorgang, vogelkooi met kraai aan de linkertoren, steen schildje boven de boog
  (wapen Loon op Zand nog neutraal: kleuren niet zeker). Klimop (2003): rechtertoren bijna dicht, linker grotendeels, zijkanten.
- Daan: grachtje + bruggetje zoals de foto: water x ±4.8, y -2.45..-3.95, grasoevers, terrein uitgegraven; brug met keien, lage bakstenen
  muurtjes, grove natuursteen en eindstenen. MK-randpad noord gaat voor de poort nu langs de plein-oever (t >= 4.35), MK-doorgangspad alleen
  nog achter de poort (MK asset **106308506735113**). Te diep gegraven cellen onder het pad hersteld (WriteVoxels Ground 1/1/0).
- Keten `build/bouw_alles.sh` (03_forms -> 03c_klimop -> 05_bake -> 09_export -> upload), plaatsen met `roblox/plaats_prinsenpoort.luau`.
  Asset **74186202233056** (15.9k tris). 8 struiken/taxussen voor de poort weg (MagischeKlokBos), layout-blok Prinsenpoort weg.
  Screenshots `review/studio_v1_voor.jpg`, `review/studio_v1_schuin.jpg`, klei naast foto `review/v1_klei_vs_foto.jpg`.
- NOG: wandeltest in Play (brug -> doorgang -> achterkant), put achter de rechtertoren (PrinsenpoortPut), riet/kroos in het grachtje,
  natuursteen-look van de torens (1957 grijs, 2003 baksteen: nu baksteen).

## Herautenplein + Kikkerkoning (chat 8, 13 nov) — v1 in Studio
Map `models/AR_Herautenplein/`, brief `asset-brief.md`, plan `review/plan_osm.png`. Zelfde frame als de Prinsenpoort. Daan: "precies na, je mag
iets weghalen" + "paden weer dat grind, pad bij de Magische Klok goed".
- Indeling 1:1 uit OSM: ringpad, 4 getrapte tuinvakken (gazon, buxusrand, taxusblok + bakstenen bloembak, spiraaltopiary), ruwe stenen muurtjes
  langs het middenkruis, fonteinpleintje met 4 bankjes, 4 galgenlantaarns op de OSM-punten, Kikkerkoningfontein (grachtje + hek, gemetselde bak,
  rotsblokken, gouden bal, sprookjesboek). Asset **81541689190400** (42k tris). Plaatsen: `roblox/plaats_herautenplein.luau`.
- Paden licht grind (Pebble + VV_Grind 235,228,214). Grindstroken sluiten het plein aan op het MK-randpad (west en noord), dus nu één grindvlak
  van de herauten tot de tuinen. 144 planten/struiken van MK-bos/-groen van het plein gehaald; layout-blokken kikker/heraut weg.
- Terrein: grachtje uitgegraven; onder alle paden/vloeren Ground (gras prikt anders door), open stukken (naast de poort, zuid van het MK-randpad) Grass.
- Kikkers v2 (Daan: "betere kikkers"): zelf gemodelleerd in Blender (`build/03e_kikker.py` -> `AR_Kikker.blend`, `exports/AR_Kikker.fbx`)
  naar Kikkerkoningontwerp2 (Pieck), Kikker1973 en Kikkers-tuinslang 2023: zittende waterkikker (gestrekte voorpoten, kop omhoog,
  opgevouwen achterpoten, rugwallen, trommelvlies), lijf = overlappende ellipsoiden -> voxel-remesh 8 mm -> smooth -> decimate (7k tris);
  huid gebakken (geelgroen met olijfgroene vlekken, lichtere buik), ogen crème ring + platte zwarte pupil. Asset **70914706705065**,
  textuur **75961250645608** (SA.Color 205,205,178). Geplaatst met `roblox/plaats_kikkers.luau`: x1.25, op de binnenhoeken, kijken naar de
  rotsen. generate_mesh-kikkers verwijderd. `review/kikker_vs_foto.jpg`, `review/studio_v2_kikkers.jpg`.
- Screenshots `review/studio_v1_overzicht.jpg`, `review/studio_v1_fontein.jpg`.
- v3 (Daan: "het is gewoon een uitsteekseltje, doe onderzoek, muren?, 100x vetter"): OSM-relatie 2907394 (highway=pedestrian, name=Herautenplein)
  gevonden: outer 369580589 + 12 inners (`ref/plein_relatie.json`, plan `review/plan_plein_relatie.png`). Het plein heeft maar 1 uitsteeksel: in de
  MK-hoek voor de 6 herauten (x 8.8..19.8, y -5.2..-15.2). MK-randpaden voorbij de herauten en mijn aansluitstroken bestonden niet -> weg
  (MK v13, asset **80714108634542**; terrein daar weer gras). Het plein loopt verder west (x -19, inham bij de Kleyne Klaroen) en zuid tot y -87:
  2 hagen (1 m), gebogen bloemvakken met laag bakstenen muurtje + rode bloemen + bankjes rond het Ezeltje (Herautenplein99), bosje met 3 bomen.
  Grind = hele omtrek (boolean-gaten voor grachtje en bosje). Gazons nu als rechthoeken (oorknippen gaf driehoeken buiten de haag) en
  RenderFidelity Precise (verdwenen anders van bovenaf). 480 bloemen/bomen in `HerautenpleinGroen` (`roblox/plaats_herautenplein_groen.luau`).
  Muren: in OSM en op foto's 2009/2010 geen; de witte kantelenmuren rond het plein waren er 1952-~1960. Asset **130206013763885**.
  Screenshots `review/studio_v3_*.jpg`.
- v4 (Daan stuurde een luchtfoto, 225 px, Nick Ringelberg): indeling klopt met de OSM-relatie (rechthoek, 4 tuinvakken, fontein, rond pleintje
  aan de korte kant); het plein ligt helemaal in het bos. 59 bomen in een band van 1.2-15 m rond de omtrek (`roblox/plaats_herautenplein_bos.luau`,
  `exports/bosrand.json`). Bovenaanzicht `review/studio_v4_bovenaanzicht.jpg`. Grotere versie van de luchtfoto nodig voor details.
- v5 (Daan: "kijk linksboven op de luchtfoto, het stuk plein bij de MK"): het uitsteeksel bij de MK is helemaal bestraat tot in de hoek bij de
  toren (MK v15 asset **126060859233156**: MK-gazon voor de westarm weg, bestrating weer over de hele band, lantaarn met krularm naar het begin
  van de gazonstrook). Daarna een lange open gazonstrook langs de oostrand van het plein (x 15.1..20.5, y -15.2..-42) met laag bakstenen randje
  = de groene band op de luchtfoto. 18 bosrandbomen op/achter die strook weg. Plein asset **100856002577530**. `review/studio_v5_mkhoek_boven.jpg`.
- v6 (Daan: "haal die bankjes weg, hagen om de grasstukken, dan zijn we klaar"): zigzagbank + buxuskegel in de MK-hoek weg (MK v16 asset
  **139174637289363**). Taxushagen 0.9 m tussen bestrating en gras: noordrand plein (bij de Prinsenpoort/brug), langs de aanloop naar de brug,
  westrand plein, om de gazonstrook oostzijde. Plein asset **121494619592510**. `review/studio_v6_hagen.jpg`. Herautenplein KLAAR (Daan).
- NOG: Ezeltje-strek-je zelf (beeld op sokkel, aparte attractie), waterstralen (pas als Daan animatie wil),
  wandeltest, oude MK-onderdelen op het plein nalopen (MK-galgenlantaarn bij de poort staat er nog).

## Ezeltje Strek Je (chat 8, 13 nov) — v1 in Studio
Map `models/AR_Ezeltje/`. Bronnen: Eftepedia-lemma Tafeltje Dek Je, Ezeltje Strek Je (60 plaatjes in `ref/eftepedia/`). Alleen de ezel op de sokkel
(herberg De Ersteling + knuppel/tafeltje = later). Plek: OSM 55423191 = midden van het ronde pleintje op het Herautenplein (5.96, -64.45),
kop naar de Prinsenpoort (lemma). Bloemenborders met banken eromheen stonden er al (Herautenplein).
- `build/03_ezel.py`: sokkel (ijsselsteentjes-basis, sierbeton met krullen op de hoeken, cartouches "Ezeltje strekje" op de lange zijden,
  muntdeurtje achter, dekplaat met rode rand, bovenkant 1.66 m); ezel in gestrekte houding (ellipsoiden/buizen -> voxel-remesh -> smooth,
  gebakken grijze huid met lichtere buik/snuit), rood tuig met gouden nagels, dekje met Pieck-ornament en zigzagfranje (PIL-textuur),
  ogen, manen, hoeven. Asset **117994407314720**; texturen ezel 113321106189533, dekje 112437444046680, bord 128244839705244.
  Plaatsen: `roblox/plaats_ezeltje.luau`. Screenshot `review/studio_v1.jpg`.
- v2 (Daan: "moet echt mooier, gedetailleerder en realistischer"): ezel opnieuw in Blender (`build/ezel_anatomie.py`, ge-exec'd door 03_ezel.py):
  romp uit echte doorsneden, hals/kop als loft langs hun as, benen met knie/kogel/hak, spieren (hals, triceps, borst, onderarm, hamstrings,
  schenkel, heupknobbels, ruggengraat), kop met kaakspier, wenkbrauwbogen, oogleden + wimpers, neusvleugels, lippen, open mond, voorlok,
  44 manenplukjes, holle oren met rand en haren, staart met 22 strengen; gestrekte pose (voorbenen ver naar voren, achterbenen ver naar achter),
  sokkel langer (1.8 m dekplaat). Hoog model (voxel 4.5 mm + vachtruis) -> normal map 2048 op het spelmodel (36k tris), AO in de kleur gebakken.
  Dekje naar de foto: rood middenpaneel met wit ornament, zwart-zilveren zigzagrand; brede rode singel met gouden nagels.
  Asset **81767048492683**, kleur 104013001055875, normal 131210851252410, dekje 89288262847523. SA.Color 228,220,208. `review/studio_v2_detail.jpg`.
- v3 kop (Daan): kop ~20% groter/langer en hoger (hangt vrij boven de sokkel, wijst meer naar voren), zware ronde kaken, mond verder open met
  hangende onderlip, groot oog met wit rondom + bruine iris + lichtglans, grote ovale neusgaten met dikke vleugels, oren 0.4 m rechtop.
  Asset **79079378764880**, kleur 119585118176594, normal 139416635340800. `review/studio_v3_kop.jpg`, `review/v3_kop_vs_foto.jpg`.
  Let op: een net geuploade textuur toont even wit in Studio (verwerking); ColorMap opnieuw zetten of even wachten.
- NOG: kaak/staart bewegen bij muntinworp (pas als Daan animatie wil), ezel nog wat stijf (hoofd/oren), herberg De Ersteling.

## Herberg De Ersteling (chat 8-9, 13 nov) — buitenkant KLAAR (Daan: "hij is goed"), interieur later
Map `models/AR_Herberg/`, brief `asset-brief.md`. Bronnen: ontwerptekening Knoet (ref/Herberg.jpg), foto's 2009, BAG-plattegrond (OSM 55447978).
- `build/03_forms.py`: gevelbaai met rieten zadeldak (profiel geextrudeerd + bevel, geen subsurf: die blies het dak op), schilddak riet (2 delen),
  wenkbrauwdakkapel, toren (achthoek, stuc/plankwerk/pannen + spits), schoorstenen, ramen met luiken, deuren met boog, lantaarn, uithangbord
  (PIL-textuur), vaten, bankje. `05_bake.py` met nieuwe rollen riet (strengen langs de helling + mos), natuursteen (oker verband), hout
  (verticale planken), pannen, stuc (crème). Keten `build/bouw_alles.sh`, plaatsen `roblox/plaats_herberg.luau`. Asset **97498436658390**.
  Staat tussen het Ezeltje-pleintje en het kasteel van Sneeuwwitje, toren rechts (zoals Herberg_exterieur). Screenshot `review/studio_v1.jpg`.
- NOG: interieur (Herberginterieur-ontwerp: haard, balkenplafond, jongen aan tafel, waard, hondje), kozijnen/roeden fijner, wenkbrauw-textuur.
- v2 (Daan: "niet mooi", "lijkt niet op het echt", "heb je geen blueprints"): opnieuw volgens blender-image-to-3d met fotocamera-overlay.
  Echte bouwtekeningen zijn niet openbaar; maten uit: Intro_tafeltjedekje (87.5 px/m op de gevel, `cam_match.py --cam 4.86,-30,1.14,94.5 --shift 0,0.19`),
  ontwerptekening Knoet ("6m" = ketel), BAG-footprint (gevel 10.0 m tot de toren, toren 1.4 m voor de gevel) en de schone frontfoto
  `ref/Herbergfris1.jpg` (persoon bij de torendeur: toren voet r 1.95, plankwerk 2.5-4.6 m, deur 0.92x2.24).
  Klein huisje: muur 2.05 m, gevelkap-top 5.6, ketel 6.5, nok 4.45 met rode vorsten, schoorsteen 6.4 + leien kap 7.4, toren tot 8.4.
  Gevelkap uit gemeten randpunten (KO/KIL/KIR), wenkbrauw als brede golf, zijkap links, schilddak + achtervleugel. Texturen: Poly Haven CC0
  `riet_01` (riet) en `stone_wall` (gevelveld) in `textures/polyhaven/`, torendak eigen rol leien (grijsbruine spanen). 65k tris.
  Asset **126789978359252** (ids in `textures/asset_ids.txt`, plaatsen `roblox/plaats_herberg.luau`). Reviews `review/v2b..v3e`, `review/studio_v2.jpg`.
- v3 details uit Herbergfris1 (x = 7.85 + (px-768)/112): boomstambank (grijze verweerde stam, gevorkte poten), jutezak tegen de muur + liggende zak,
  bootvormige uitgeholde trog, vaten (groot bij de deur, klein + hoog op de overgang, klein bij de toren), kruik, smal boograampje echt 0.36x1.15 m
  met tralies. Nieuwe kleurmaterialen jute/stamhout/aardewerk in `plaats_herberg.luau`. Asset **112518972306080**, 72.5k tris. `review/studio_v3_details.jpg`.
- Knuppel uit de zak hangt BINNEN (lemma: voorportaal van de herberg, kooi aan de wand tussen 2 lampen, vitrine met de zak) -> komt met het
  interieur. Concept-code voorportaal + knuppel klaar in `build/later_voorportaal_knuppel.py`, foto's in `ref/` (Knuppelenzak, Knuppeltje, Herbergfris2-5).
- KLAAR volgens Daan (13 nov). Later: binnenkant (Herberginterieur-ontwerp + Herbergfris2-5: balkenplafond, haard, jongen aan tafel, waard), wandeltest.

## De Zes Zwanen (chat 9, 13-14 nov) — v4 in Studio (achterbouw op OSM-maat, scene, wachtrij, botsing, sfeer/dagritme; zwanen/interieur later)
Map `models/AR_ZesZwanen/`, brief `asset-brief.md`. Bronnen: 78 Eftepedia-plaatjes (`ref/eftepedia/`), Efteling-blog/pers (`ref/efteling_blog/`:
zwaan zijaanzicht + 3D-model, staalskelet, bouwfeiten: toren 15 m, slot 350 m2, vijver 75.000 l). Echte bouwtekeningen niet openbaar (vergunningen/ride-databases
nagezocht). Plattegrond = OSM: gebouw 961616753, vijvers 961616757/758/760, vaarbaan 837234781 (lus, tegen de klok in: in door de poort rechts, uit via de grot
links), rotsen 961616756 (eiland) / 961616759, controlehokje 961616755, pad 961616754, hek 1255787244. Modelframe `ref/model_frame.json` (voorkant -Y = naar de vijver).
- Hoofdfoto `ref/hoofdfoto.jpg` (D6z_exterieur_totaal) als overlay: `build/cam.sh <tag> 0.18,-22.68,1.7,47 30 0.075 [master] [clay|mat]` (camera ZZO, 30 graden).
  Gemeten: vleugel (5.25x2.6, gevel evenwijdig aan de poortvoorzijde) op de rots z 3.6, goot 5.8, nok 6.9; toren rode ring 7.3, donkere leien band 8.4, kop met
  neus 8.4-9.45, hoedendak 9.4, pannenkap tot 12.1, ui 2 tot 13.0, spits 14.3, vaan 15; poort kantelen 4.35, spitsboog-waterpoort in de schuine zijde.
- Delen met eigen master/bake/upload: `build/03_kasteel.py` (ZZ_kasteel), `03_omgeving.py` (ZZ_omgeving), `03_zwaan.py` (ZZ_zwaan, 1x gemaakt, 6x geplaatst
  op de vaarbaan: `exports/zwanen.json`). Gedeelde helpers `build/zz_helpers.py` (spitsboog, kantelen, gelaagde kunstrots `rotsblokken`, `snij`).
  Bake `05_bake.py --pre ZK|ZO` met Poly Haven CC0: plastered_stone_wall (stuc), castle_wall_varriation (natuursteen), cliff_side (rots), clay_roof_tiles_02 (pannen).
  Sjerpen `build/02_sjerp.py` (rood/teal). Upload `build/upload.sh`, plaatsen `roblox/maak_plaatsscript.py` -> `plaats_zeszwanen.luau` (graaft terrein onder de vijvers,
  Ground onder pad/oevergrond), groen `roblox/plaats_zeszwanen_groen.luau` (76 bomen, ondergroei, asters langs het water, varens; kloont BomenBronV3/VVEchtePlanten).
- v3 (14 nov, Daan: "zwanen voorlopig weg, scene eromheen echt, niet meer doorheen vallen, licht realistischer"):
  - Zwanenboten uit Studio en uit het plaatsscript (de attractie zelf komt later). Interieurs en de vaarbeweging ook later.
  - Stuc: scherpe afgebladderde plekken met bruingrijs metselwerk (stacked_stone_wall) + donkere breukrand, regenstrepen, vocht onderaan (05_bake rol stuc).
  - Wachtrij naar D6z_vaart_wachtrij: lage Pieck-blauwe buisleuning met krullen i.p.v. sierhek op OSM 1255787244, oranje-bruine kalksteenbrokken langs de rij,
    ingangsbord (groene paal, gouden bol), kade in rode klinkers, dichtgeklapte witte parasol, blauwgroene deur aan het hokje.
  - Botsing: pad lag 1 stud boven het terrein zonder botsing (voeten zakten erin) en de vijverbodem botste niet (je viel in de kuil). Mesh-botsing
    (PreciseConvexDecomposition) op de concave pad-/oeverplaat spande OVER het water (onzichtbare vloer, weggedrukt worden) -> nu 209 rasterblokken
    (0.5 m cellen, samengevoegd) voor pad/oever/kade en vijverbodems; mesh-botsing alleen op rots/oeverstenen/stuc/natuursteen. Play-test: pad, wachtrij,
    kade en oever Y 4.9 stabiel, vijvers: je staat op de bodem (waadt), niet meer weggedrukt.
  - Export altijd via `build/export.sh` (met --extra: anders vallen botsblokken en lampen weg).
  - Belichting voor het hele park: `park/belichting_schemer.luau` (zonsondergang 17.85, roze-violette sprookjeslucht via Atmosphere, geschilderde skybox
    eruit, geen sterren, zachte wolken, zachtere schaduwen, Env-schalen 1, bloom/zonnestralen/dof licht, lantaarns 1.2/16).
  - Maten nagemeten: hoogte 15.0 m = Efteling; vijver 227 m2 x 75 m3 = 33 cm diep (klopt). Kasteel 14.6 x 10.7 m tegen OSM 15.4 x 13.1: ~5% te smal en
    de achteruitbouw (~2.5 m, binnenscene Elisa, achter de bomen) ontbreekt nog. Zwanen waarschijnlijk 10-15% te hoog (kop 2.1 m i.p.v. ~1.8 m boven water).
- Assets v3: kasteel **123826992475315**, omgeving **99634573159616** (ids in `textures/asset_ids.txt`).
- v4 (14 nov): ACHTERBOUW volgens de OSM-omtrek: rechts gepleisterde kantelenmuur met natuurstenen pijlers, ingang wandelgang (houten afdak,
  rode lantaarns), lage uitgangspoort (gebogen pannenkap, bollen), groene houten afscheiding; links lager blok bruine natuursteen met kantelen
  (D6z_wandelingang_slot, D6z_landschap_ingang_slot, D6z_ontwerp_aanzicht_links). Binnenplaats in rode klinkers. Gemeten in Studio: gebouw x -8.5..7.1
  (15.6 m, OSM 15.4), achterkant y 8.1 (OSM 7.8), top 15.0 m. Muren als COLL-blokken (geen mesh-botsing op het concave kasteel).
  Assets: kasteel **109146562516265**, omgeving **121393338574060**. Let op: verse uploads geven soms even HTTP 503 bij GetObjects (later opnieuw).
- Belichting/sfeer (Daan: "vetter, realistisch en dromerig"), alles in `park/` en `park/sfeer/`:
  - LightingStyle = Realistic + PrioritizeLightingQuality (stonden al aan; Technology mag een script niet zetten).
  - `sfeer_sprookjesbos.luau`: gloed, warme kleur, zachte verte (DoF), zwevend sprookjesstof (gouden stofjes) en lage nevel (rbxasset-texturen).
  - `sfeer/water_zeszwanen.luau`: spiegelend terreinwater in de vijvers (peil Y 0.95), waterplaat onzichtbaar; donker troebel (reflectie 0.18,
    hoger werd melkig-beige van de lichte lucht). In het water zwem je nu (niet meer doorheen vallen).
  - `sfeer/Dagritme.server.luau` (ServerScriptService.Dagritme): ochtend -> dag -> gouden uur -> roze zonsondergang -> blauw uur -> sterrennacht,
    30 min per dag (attributen op Lighting: DagritmeAan, DagMinuten, StartTijd 17.0). Lantaarns + gloeiend glas aan in de schemering, sprookjesstof
    wordt 's nachts vuurvliegjes, 18 lichtbundels (Beams) door de bosrand die de zon volgen.
  - `sfeer/SfeerZones.client.luau` (StarterPlayerScripts.SfeerZones): onder het bladerdak donkerder/koeler/groener, open plekken warm (eigen
    ColorCorrection "ZoneKleur").
  - Lantaarns: PointLight + SpotLight naar beneden (lichtcirkel op het pad, schaduwen), raamlicht bij vleugel- en torenvensters (in het plaatsscript).
- Fps-test (Play in Studio, Studio op de achtergrond bestuurd via MCP): 12 fps, en dat blijft 10-12 met lampschaduwen, lampen, stof/nevel,
  dof/bloom/zonnestralen en zonschaduw UIT -> de sfeer kost niets meetbaars; de lage fps komt van de rest (28.6k instances, hele park, 5.6 GB,
  Studio niet op de voorgrond). Daan zelf meten met Shift+F5 met Studio op de voorgrond.
- Het rode vlak naast het hokje was de achtergebleven SchaalPop (testpop) -> verwijderd. Studio-texturen wit = Roblox/Studio-laadprobleem
  ("No asset content representation found ... do_not_fallback_to_baseline"), vanzelf over na herstart/ander netwerk.
- NOG: zwanen terug (12% kleiner) en fijner, Elisa + interieur later, bruggetje/beekje, sprookjesboek.

## De Nieuwe Kleren van de Keizer (chat 9, 14 nov) — v1 in Studio (decor + paleistuin; figuren/schimmenspel later, statisch)
Map `models/AR_KlerenKeizer/`, brief `asset-brief.md`. **Echte bouwtekeningen gevonden** op Eftelist (`ref/tekeningen/`, bron in BRON.txt):
plattegrond met maten in mm (vijver 20000x2500, hekwerk 21365, voorbak 1770/1200/1770), aanzichten met peilen (muur 2850+P, koepel 3050+P,
hagen 1800/3000+P, pad 600-P, vijverbodem 900-P), poortdetail; plus maquette en 33 Eftepedia-foto's (`ref/eftepedia/`). OSM: `build/01_osm_lokaal.py`.
- Modelframe: oorsprong = midden lange vijver (OSM lokaal (1.2, 4.37) t.o.v. attractievlak 50911607), voorkant naar de bezoekers (noord) = -Y,
  z 0 = bezoekerspad, decorpeil 0.6. Roblox-oorsprong studs (-48.81, 2, -401.85), F (0.116, 0, -0.993). Controle: OSM-muur 767716987 valt op y 11.2
  (tekening 11.3), koepel OSM 591202406 ~1 m van de tekening.
- `build/03_decor.py`: middenpoort 1.93 x 4.4 m met doorgang 1.07 x 3.5 en grote kuif, medaillonpijlers (oeil-de-boeuf + guirlande), schuine
  nispijlers met kuif en fonteintje, achtermuur met paneelvelden en urnpijlers, lakei- & poorthuizen (kruisplattegrond), gouden poort,
  linkerfonteinbak met voluten, achthoekige theekoepel (vensters met roedes + vitrage, blauwe glazen koepel met ribben, gouden theepot),
  voorbak met 8 postamenten + overloop, lange vijver met zwarte rand. `03_omgeving.py`: gazon op decorpeil met glooiing, hagen (1.15 voor
  de muur, 3.0 achter, 1.8 zij/pad), bolstruiken, lichte rijvloer, laag zwart hekwerk met insprong, klinkerplein, 4 groene bankjes.
- Bake rol `pleister` (strak roomwit paleisstuc) in `05_bake.py --pre KD`. Keten: 03_decor/03_omgeving -> 05_bake -> `build/export.sh` ->
  `build/upload.sh` -> `python3 roblox/maak_plaatsscript.py` -> `roblox/plaats_klerenkeizer.luau` (fonteinen als ParticleEmitter-stralen,
  haagtextuur, Ground onder het decor).
- Assets: decor **129960133990936**, omgeving **119903777125541**, pleister 134788731347178/136901809327662.
- v2 (14 nov, Daan: "refine"): kuiven gebeeldhouwd (`kuif2`: bollen langs spiralen + cartouche, samengesmolten met organisch() tot acanthus-
  krullen) met gouden medaillon, gouden kronen op de nispijlers en gouden guirlandes met kwasten (Intro_nieuwekleren/Kleermakers); haag voor de
  muur 1.7 m (verbergt de rijbaan zoals op de foto's); lage haag achter het hekwerk op de zijstukken; vijverwater hoger; visgraat-klinkers
  (MaterialVariant EftelingKlinkers); grijzer koepelglas; sprookjesboek op smeedijzeren standaard bij de ingang (Boekloc).
  Wandeltest in Play: plein links/midden/rechts Y 4.8 stabiel, lopen naar het decor stopt bij het hekwerk (y -3.1).
  Assets v2: decor **126400976252556**, omgeving **128394215565121**. upload.sh probeert nu 3x (Open Cloud gaf af en toe een lege respons).
- NOG: figuren (keizer, lakeien, hofdames, kleermakers) en schimmenspel later; klinkers zijn rood-bruin (variant), foto is beige.

## Het Meisje met de Zwavelstokjes (chat 9, 14 nov) — v1 in Studio (buitenkant; binnen/diorama/show later)
Map `models/AR_Zwavelstokjes/`, brief `asset-brief.md`. Bronnen: 43 Eftepedia-foto's (`ref/eftepedia/`: Maquette_Mmdzs = indeling van boven,
Meisjezij, Zwavelstokjes4b, Mmdz_bouw_stucwerk), Eftelist-ontwerpschetsen (`ref/tekeningen/`, geen maatvoering), OSM 279667968 (`build/01_osm_lokaal.py`,
modelframe in `ref/osm_model.json`: x = west, y = zuid, gevelrichting 13.5 graden). Roblox-oorsprong studs (120.36, 2, -466.71), F (-0.233, 0, -0.972).
- `build/03_stadje.py`: heuvel 0.9 m met natuurstenen keermuur, vijvertje (OSM 767716993) met stenen, oprit met lage gebogen stucmuurtjes, poort
  tussen twee ronde torentjes (getande lijst, kegeldak), hoge ronde toren, kantelentorentje, gaanderij met 3 rondbogen op zuiltjes, middenblok
  met kantelen en spitsboogramen, grote topgevel met blinde spitsboog en twee torentjes op consoles, rechtervleugel + uitgang met trap (OSM exit),
  hoge kantelenmuur achter met hoektorens (verbergt de loods van de Indische Waterlelies), klinkerpaden. 55k tris.
- Bake (rollen stuc = afgebladderd met baksteen, pannen, natuursteen, hout; `--pre MZ`), `build/export.sh`, `build/upload.sh`,
  `roblox/maak_plaatsscript.py` -> `plaats_zwavelstokjes.luau` (spiegelend terreinwater in het vijvertje, Ground onder het geheel).
- Asset: stadje **133813796196568** (texturen in textures/asset_ids.txt).
- v2 (klaar, nog plaatsen zodra Studio open is): sprookjesboek aan de voet van de oprit (Boekloc), 2 groene bankjes (OSM bench), daken
  donkerder/bemost via TINT (vergelijking met Meisjezij: onze pannen waren te oranje-roze). Planten: `roblox/plaats_zwavelstokjes_groen.luau`
  (gras/riet + asters langs het vijvertje, varens/heesters voor de keermuur en op de heuvelrand, rododendrons bij trap en oprit, 40 bomen
  naast/achter het stadje, niet in het zicht vanaf het pad). Asset v2: stadje **109477760100605**.
- v2 geplaatst (14 nov) + terrein met hoogteverschillen (Daan): `roblox/terrein_zwavelstokjes.luau` laat de kunstheuvel aan zijkanten/achter
  zacht uitlopen (5.5 m), golvende bosgrond (noise 0.3-0.6 m), oevers naar het vijvertje, paden vlak met vloeiende aansluiting, voorkant laag
  (keermuur zichtbaar), voet van de trap vrij. 545 planten -> 318 na opschonen (planten landden op torendaken: raycast nu alleen op terrein,
  heuvel en paden; poort/oprit/uitgang/trap vrij). 'riet' bestaat niet als sjabloon. Wandeltest: oprit -> poort (0.92 m) en trap af OK.
- NOG: binnenkant later; gaanderij lager/kleiner zoals Meisjezij; riet-sjabloon maken.

## Repelsteeltje (chat 9, 14 nov) — v1 in Studio (buitenkant; lakei/Repelsteeltje en interieur later)
Map `models/AR_Repelsteeltje/`, brief `asset-brief.md`. Geen bouwtekeningen (Eftelist heeft geen pagina); 24 Eftepedia-foto's, OSM 55424159 (5.8 x 4.1 m),
modelframe `ref/osm_model.json` (voorkant = lange noordoostzijde naar het pad = -Y, x = noordwest). Roblox-oorsprong (351.75, 2, -425.94), F (0.533, 0, -0.846).
- Camera-overlay op Repelsteeltje_exterieur (`build/cam.sh`, camera rechtsvoor op de hoek: -0.43,-11.6,1.5 lens 28 yaw 34): goot 2.5, nok 4.6, stronk tot
  6.0, schoorsteen 5.0 + pijp; venster links van het midden.
- `build/03_huisje.py` (Daan: "te weinig detail", "stronken in het dak", "verhogingen in het dak"): losse leitjes in verspringende rijen (lei/lei2) op
  een dak dat opzwelt over elke wortel en rond de stronk (`dakbult`), wortels precies op het leienoppervlak (`dakz`) en langs de keienhoeken omlaag,
  stronk met schorsgroeven + kraag op het dak + jaarringenschijf, gebogen houten hoed (laag eind links), rondboogdeur van planken met hengsels,
  klopring, natuurstenen omlijsting en stoepsteen, rond raampje met stenen bloem, kijkvenster 2x 3x3 ruitjes + gordijn, luiken van planken met
  Z-schoor, hengsels en hartje, losse keien op de hoeken, stenen plint, afgevallen stuc met verdiept metselwerk (6 plekken), sporenkoppen,
  windveer, nokvorst, klimop, houtstapel, emmer, bolderkar, hark, blauwgroen hekje, flagstone-pad, sprookjesboek. ~97k tris.
- Bake rollen stuc/natuursteen/hout + nieuw `lei` (grijsbruin met veel mos) en `schors`. Plaatsen: `roblox/plaats_repelsteeltje.luau` (rook uit de
  schoorsteen), `roblox/terrein_groen_repelsteeltje.luau` (golvende bosgrond, rond huis en deur exact op maaiveld, 430 planten, 26 bomen).
- Asset: huisje **77559737160973**.
- Hekje (Daan: "je moet in het huis kunnen kijken"): volgens Repelreus/Repelensteel2024 staat het hek NIET voor het kijkvenster; links langs de
  deurtuin tot de hoedpoot, rechts vanaf de stronk-hoek naar voren, krulletje aan het hekeinde. Keien alleen bij de hoeken, venster vrij.
- Pad: oude flagstone-plaat blijft (Daan: "het pad was goed"). Proef met losse flagstones (`build/03_pad.py`, `roblox/plaats_pad.luau`) afgekeurd;
  paden doen we later. Wel: de flagstone-plaat loopt nu tussen de hekeinden door tot tegen het kijkvenster (PAD-polygoon in 03_huisje.py en
  terrein_groen_repelsteeltje.luau gelijk, terrein eronder vlak). Huisje nu **111707359870289**. Later: herringbone-klinkers ernaast.
- LES terrein: vlak maaiveld = voxellaag 0..4 LEEG (oppervlak Y 2). Ground vullen tot Y 2 maakt laag 0..4 half vol en tilt het oppervlak naar Y 4.

## Klein Duimpje (chat 9, 14 nov) — v2 in Studio, NOG NIET AF (Daan: realisme en detail ontbreken)
Map `models/CH_KleinDuimpje/`. Bronnen: 33 Eftepedia-foto's, 9 Commons-foto's (`ref/commons/BRON.txt`, hoofdreferentie 4019765619 3840px),
OSM eiland 55424075 + gracht 767716994 (`ref/osm_lokaal.json`, `ref/osm_model.json`). Geen bouwtekeningen (Eftelist heeft geen pagina), geen
downloadbaar 3D-model (Sketchfab/MakerWorld/Creator Store gezocht). Roblox generate_mesh gaf een chibi-pop: afgekeurd.
- Maat: reus ~8.5 m lang (Duimpje haalt de halve laarsschacht, past op het 8 m-eiland); Eftepedia's "vier meter" klopt niet met de foto's.
- `build/03a_reus.py`: gesculpt uit gefuseerde volumes (voxel remesh) + plooien; houding naar de foto-overlay (`build/cam_match.py`, camera
  -0.8,-15.5,1.3 lens 40 op `ref/front_4019.jpg`). Hoofd in profiel recht omhoog, open mond, donkere wigbaard over de borst, hangsnor,
  veterlaars (achter) met haken/tong, omgeslagen kraag (voor), tas met gespen, rode bies aan de mouwen.
- `build/03b_omgeving.py`: rotsbed (kalksteen + grijze zwerfkeien), gracht (terreinwater in Studio), stronk achter het hoofd, praatstronk met
  hoorn, bordje. Bake: `04_bake_reus.py` (geschilderd: kleur x AO x blos/stof), `05_bake_omgeving.py`; export `09_export_*`; `upload.sh`.
- Studio: `roblox/plaats_kleinduimpje.luau` (reus 0.6 m naar het hoofdeinde, gracht = terreinwater), `plaats_kleinduimpje_groen.luau`
  (bosgrond, ~380 varens op het eiland, rododendrons/coniferen achter de gracht). Assets: zie `textures/asset_ids.txt`.
- v3 scène (Daan: "reus verbeteren we later, ga verder met de scène"): keienheuvel van grijsblauwe zwerfkeien onder de reus en onder de
  verste laars aan de grachtrand, grijze kalksteenrand (Roblox Slate; 900 stenen op één atlas gaf witte vlakken + zwarte naden), Duimpje
  bij de veters, sprookjesboek op een lessenaar (2017), praatstronk links voor; gracht met kroos + rimpels en riet/gele lissen langs de
  buitenrand (`roblox/plaats_kleinduimpje_water.luau`); varens alleen op het eiland, voorbed vrij voor het zicht.
- Reus: handen met kootjes/knokkels/nagels, plooien nu als doorlopende groeven (lijn op het oppervlak geprojecteerd, numpy-afstandsveld
  in `apply_plooien`; losse push-punten gaven putjes). NOG TE DOEN (later met Daan): gezicht en laarzen fijner, herringbone-plein voor (paden later).
- LES bake: 05_bake haalde onderkanten bij z<0.1 weg (voor paden) -> gaten in schuine losse stenen; voor stenen `dead = []`.

## Doornroosje (chat 9, 14 nov) — v1 in Studio (buitenkant; figuren/interieur later)
Map `models/AR_Doornroosje/`, brief `asset-brief.md`. 158 Eftepedia-foto's met ontwerptekeningen van Anton Pieck (aanzichten, plattegrond-
schetsen), luchtfoto en meetlatfoto; OSM (`ref/osm_lokaal.json`, frame = OSM-assen x oost / y noord, oorsprong zwaartepunt 55423166 =
studs (362.96, -262.92); Roblox: ORIGIN met 180 graden draaiing). Eftelist heeft geen pagina.
- `build/03_kasteel.py`: zaal met trapgevel + arcade (zuid), binnenplaats met kantelen, slanke vierkante toren met tentdak + lagere aanbouw,
  ronde torens 407/408/409 + binnenplaatstoren met uitlopende kegeldaken van pannenrijen en gouden windvanen. Kasteelvloer Z0 = 4.5 m
  (rotsheuvel boven de vijver). Stuc via `organisch()` (voxel 0.04, bobbels, decimate) + bollend/scheef torenprofiel (Daan: "lelijk" bij
  strakke cilinders). Overlay: noordfoto `ref/noord_2024_15.jpg` en luchtfoto `ref/lucht.jpg` (`build/cam_match.py`).
- `build/03_omgeving.py`: beide trappen (OSM steps) met muurtjes, terraspad, poortgebouwen 414/415, rotswand aan de vijverkant.
- Bake `05_bake.py` (Zes Zwanen-rollen; stuc met weinig afbladderplekken, groenige vochtrand), export `09_export_roblox.py`, `upload.sh`.
- Studio: `roblox/plaats_doornroosje.luau`, `roblox/terrein_doornroosje.luau` (heuvel tot Z0, grond onder de trappen, vijver uit OSM als
  terreinwater, rots aan de vijverkant), `roblox/plaats_doornroosje_groen.luau` (~650 planten + 34 bomen; daarna nog ~800 rododendrons/
  varens op de noordhelling, de rotswand en de rotshelling, direct in Studio). Assets: zie `textures/asset_ids.txt`.
- v2 (Daan: "mooier en gedetailleerder, die steps moeten echt pad zijn"): trappen opnieuw als echt pad (Doornroosje_2026_Trap_*,
  _Trap_2022): doorlopend keienpad met brede treden en lage optreden (~0.14 m), lage crème muurtjes (~0.75 m) die de helling glad
  volgen met een onregelmatige rij dekstenen, zwarte lantaarnpalen met licht; pad/muur/dekstenen als Roblox-materiaal (Slate/Limestone,
  geen bake). Oosttrap komt uit bij een rondboogpoort naar de binnenplaats (poortgebouw verlegd, zaal smaller). Kasteel: glas-in-lood
  ramen (amber + roeden), klimop als plat bladtapijt aan de torenvoeten, wandlantaarns, wapenschilden op de poortgebouwen.
- NOG TE DOEN: waterval naast de westtrap, kraaien/wachter/koks (figuren later), plein/paden rondom later.
- LES: raycasts raken alleen onderdelen met CanQuery = true (geplaatste meshes staan uit): voor planten op een mesh tijdelijk aanzetten.

## Roodkapje (chat 10, 14 nov) — v1 in Studio (huisje + vlak grindpad + bos + vennetje; figuren/interieur later)
Map `models/AR_Roodkapje/`. Bronnen: 96 Eftepedia-plaatjes (`ref/eftepedia/`) met bouwtekeningen: `Aanzichten_Roodkapje.jpeg` (4 aanzichten +
plattegrond + doorsnede 1:100, ~30 px/m, GESPIEGELD t.o.v. de bouw; maat '180' = pad boven de kelder), `Zijaanzicht_Roodkapje_2016.png`
(bordes, kelderdeur + houtgewelf, trap), `RK-plattegrond.jpg` (interieur 1:20). OSM 50911608 (BAG 4.7 x 6.1), bordes-pad 766787193, trap 766787194,
poortje 7161368031, lamp 7165020178, pad 1074487763, vennetje 766787195 (`build/01_osm_lokaal.py` -> `ref/osm_lokaal.json`, `review/osm.png`).
- Frame: oorsprong = midden BAG = studs (228.0, 137.85), -Y = voorkant (noord, naar het pad), +X = west, F (0.098, 0, -0.995).
  Huisje: z 0 = vloer kamer grootmoeder = maaiveld (Roblox Y 2.15); kelder z -1.9 ligt onder de grond.
- `build/03_huisje.py`: stucmuren, 3 kijkramen tussen 4 bolle okerzuilen + bloemenband + dikke balk (2016), overstek 1.1 m met vakwerkgevel en
  raam met kaarslicht, brede windveren + houten spits (top 7.1 m, foto 2016 is hoger/spitser dan de schets uit 1959: foto aangehouden), dak in
  bruine schubben, klokgevel met venster + windwijzer boven de Pieckblauwe voordeur (stenen omlijsting, afdakje, bel), bordes met oranjerode tegels,
  leuning met krullen, poortje, kelderdeur + houtgewelf met brandhout, trap naar achter (OSM), vogelhuisje van Krakeeltje op klimoppaal,
  gietijzeren hoeklamp, ronde toren met kegeldak + windwijzer, schoorsteen met zinken pijp, platte dakkapel ("oog").
  Camera-overlay op Grootmoedershuisje_herbouwd: `build/cam.sh <tag> 0,-15,1.5,30 -21 8 -0.07,0.06`. Review: `build/review.py` (+ sheet.py).
- `build/03_omgeving.py`: alleen nog het grindpad (3.4 m, vloeiende OSM-as, dichte plaat 12 cm). Bake `05_bake.py --pre RK` (stuc zonder
  afbladderplekken, bruine dakschubben). Export `build/export.sh`, upload `build/upload.sh`, plaatsen `roblox/maak_plaatsscript.py` ->
  `roblox/plaats_roodkapje.luau`; bos `roblox/plaats_roodkapje_groen.luau` (RoodkapjeGroen, 1961 planten, 58 bomen; in Wind-MAPPEN, Roodkapje in LantaarnsDagNacht).
- Assets: huisje **137968515638209** (88k tris), pad **77138895088158**; texturen in `models/AR_Roodkapje/textures/asset_ids.txt`.
- Daan (14 nov): eerst rotsblokmuren + dijk zoals de Efteling 2016 -> "ziet er niet uit", "moet niet deze hoogte", "huis staat in de grond".
  Daan stuurde de foto: "zelfde hoogte als echt, maar zonder de stenen". Nu: terrein overal vlak (Y 2), vloer kamer grootmoeder = maaiveld
  (ORIGIN Y 2.15), kijkramen 0.7 m boven het grindpad zoals op de foto; kelderdeur, houtgewelf en trap zitten onder de grond (blijven in het model).
- Scène (Daan: "dan dus ff de scene"): terrein buiten de scène gewoon Grass, rond het huisje bosgrond (LeafyGrass) met rafelige rand en lichte
  glooiing ver van pad/huis; vennetje = waterplaat (SmoothPlastic donkergroen, terreinwater blijft hier niet staan: FillBlock Water geeft Ground terug)
  + riet/lissen/kroos/rimpels gekloond van KleinDuimpjeWater -> workspace.RoodkapjeWater. Planten weer op het terrein gezet (1956).
- NOG: Roodkapje + Krakeeltje (figuren later), wolf/interieur (later), wegwijzer met reliëf (OSM 7165020183, 31 m oost), Play-wandeltest, place opslaan.

## Pinokkio (chat 10, 14 nov) — v1 in Studio (werkplaats, poort, nis, haventje met Monstervis, plein, bos); verbeteren later (Daan)
Map `models/AR_Pinokkio/`. Bronnen: 61 Eftepedia-plaatjes (`ref/eftepedia/`, o.a. Pinokkio_ontwerp_huisje = vooraanzicht, Pinokkiowerkplaats,
Pinokkiototaal, Pinokkio_monstervis_rjj, Monstervis-achter, Pinokkiohelevis), OSM 405610268 (bottega), 405610269 (nis), 405610270 (vijver),
766787185/186 (hekken), 766787189 (muur), 405610267 (plein), node Monstervis (`build/01_osm_lokaal.py` -> `ref/osm_lokaal.json`).
- Frame: oorsprong = zwaartepunt BAG 405610268 = studs (149.16, 182.31), -Y = voorkant (NNW, naar het plein), F (-0.364, 0, -0.931), z 0 = maaiveld (Y 2).
  OSM -> model: X = -0.931*ox - 0.364*oy ; Y = 0.364*ox - 0.931*oy.
- `build/03_decor.py` (PK_decor): bottega (stuc, boogramen, dubbele deur met CHIUSO-bordje, zijdeur met uithangbord, luifel op 4 gesneden
  uilenkolommen met booguilen, naambord met echte letters, golvend pannendak met opkrullende randen, blauwgroene dakkapel, schoorsteen,
  windwijzer), muur + groene poort op de OSM-dienstingang, nis met dakje en 7 tonnen, touwnet-hekken (OSM), kademuurtje, boei, meerpaal, grindplein.
  `build/03_vis.py` (PK_vis): Monstervis (kop met open bek, lippen, haaktanden, gele ogen, 13 tentakels, schubben via voronoi, stekelige
  rugvinnen, krulstaart met waaiervin) + waterplaat in de vorm van de OSM-vijver (terrein eronder uitgegraven).
- Bake `05_bake.py --pre PK`, `build/export.sh`, `build/upload.sh`; plaatsen `roblox/plaats_pinokkio.luau`, bos `roblox/plaats_pinokkio_groen.luau`
  (PinokkioGroen, 2536 planten, 70 bomen, riet/lissen langs de oever; in Wind-MAPPEN). Assets: decor **78091187202022**, vis **107964315615239**.
- NOG (later): Vos en Kat, muizen/interieur werkplaats, boei-banden mooier, fijnere vis (kleurverloop), Play-wandeltest, place opslaan.

## De Rode Schoentjes (chat 10, 14 nov) — v1 in Studio (verbeteren later)
Map `models/AR_RodeSchoentjes/`. Bronnen: 27 Eftepedia-plaatjes (Boekloc_RodeSchoentjes = hoofdfoto, Intro, Karen2016, Ontwerp_muurschildering),
OSM 50911610 (7.45 x 4.96 m incl. rots), pad 405848924. `build/03_loggia.py`: open loggia (2 rondbogen op 3 gele zuilen, laag pannendak met
groene boeiboord en klossen), muurschildering (eigen getekende textuur `build/mural.py`, vrij naar Pieck), kaarsen op krularmen, kroonluchter,
verhoogde dansvloer met geruite glastegels en zigzagrand, 2 rode schoentjes, groen hekje met medaillon, bakstenen vloer, kunstrots links/achter
(rotsblokken) met 2 schildjes met Franse lelie, sprookjesboek, grindpleintje. Model **130309942322628**, zie `roblox/README_studio.md`.
- v2 (Daan: "kijk goed", "gebruik je skills", "rechte muur van steen die gewoon doorloopt", "zoek een andere hoek"): volgens blender-image-to-3d
  met fotocamera-overlays op 2 foto's (`build/cam.sh`, FOTO=voor.jpg = Rode-Schoentjes-weg vooraanzicht; Boekloc schuin): loggia 3.6 x 2.6 m,
  4 zuilen 2.45 m, brede lage segmentboog voor (kruin 3.35) + segmentbogen links/rechts, schildering + kaarsen op de ACHTERwand, rechte stenen
  muur van grote vlakke blokken in lagen achter de loggia, **symmetrisch** rond het midden (x -3.74..7.34): links en rechts even laag aflopend, in het midden boven het dak uit (Daan, 15 nov). Model **119368979582374** (grindplein ook links en rechts langs de loggia tot de muur, staan bij de zijrailingen) (dansvloer 1.5 m breed met rondom ~0.6 m bakstenen looppad binnen het hekje, hekje langs de zuilen, bordje op de kist — Rode-Schoentjes-weg.jpg) (incl. OSM-voetpad 405848924 van het Pinokkio-plein langs de loggia tot de splitsing naar De Prinses op de Erwt, 3.2 m grind); plaatsscript `models/AR_RodeSchoentjes/roblox/plaats_rodeschoentjes.luau`.
  Vergelijkbladen `review/d3/compare_clay.jpg` (voor) en `review/d4/compare_clay.jpg` (schuin).
- NOG (later): muurschildering mooier, kruisgewelf binnen, dansende schoentjes (animatie later).

## De Prinses op de Erwt (chat 11, 15 nov) — v1 in Studio (huisje + pleintje + bos; interieur/Adinda/matrassen later)
Map `models/AR_PrinsesErwt/`, brief `asset-brief.md`. Bronnen: 61 Eftepedia-plaatjes (`ref/eftepedia/`, contactblad `review/contact.jpg`), ontwerp-vooraanzicht
Sander de Bruijn (`Theekoepeltje.jpeg`, onderste helft), OSM 1406396369 (5.44 x 4.89 m incl. pijler), border 1406396363, paden 1406396370/68, 6 banken.
Echte bouwtekeningen niet openbaar (geen Eftelist-pagina, geen vergunning online).
- Frame: oorsprong = midden OSM-vorm = studs (-4.23, 41.58); -Y = voorkant (NO, naar het pad + border), -X = ZO (kijkraam), +X = blinde zijgevel (NW);
  OSM -> model: X = -0.851*ox + 0.524*oy ; Y = -0.524*ox - 0.851*oy. Roblox F = (0.524, 0, -0.851), grond Y 2.
- Maten uit OPGELOSTE fotocamera's (`build/solve_cam.py`: camera uit OSM-grondpunten, hoogtes terugrekenen) + man van 1.78 m bij de deur (Aanloop):
  voorgevel 4.62 m + pijler 0.75 = OSM-breedte; kroonlijst 5.5, nok 7.95, klokgeveltop 8.7, spits 10.3; deur 2.33 x 4.1 (spitse segmentboog);
  kijkraam 2.0 x 2.56 (4 x 5 ruiten) vanaf 1.14 m; pijler 0.85 x 1.3, verspringing 4.15 met koperen kap, schoorsteen tot 8.0 + hert-windvaan.
  Pleintje.jpg: `cam.sh <tag> -0.38,-17.01,1.55,8.8 -63.3 8.5`; Exterieur: `FOTO=exterieur.jpg cam.sh <tag> 0.15,-24.15,3.47,23.6 -48.4 3.1 0,0 clay 13.2 733x1100`.
- Delen: `build/03_huis.py` (PE_huis_master) en `build/04_omgeving.py` (PE_omgeving_master: grindplein, stucmuurtjes met kap + hekje, kwartronde
  oplopende aansluiting, 3 bakstenen pijlers met knopbol, 4 Pieckbankjes, border met bakstenen rand, schaakbordtegels voor raam en deur, groen
  kastje met lantaarn, sprookjesboek + buisleuning). Review samen: `build/combo.py` -> review/combo.blend (zelfde OWNER_TAG: altijd aparte masters).
- Bake `build/05_bake.py --pre PE|PO` (stuc per gevelrichting V/L/R/A met haarscheurtjes, natuursteen, koper, baksteen), export `build/export.sh huis|omgeving`,
  upload `zsh -ic build/upload.sh`, plaatsen `python3 roblox/maak_plaatsscript.py` -> `roblox/plaats_prinseserwt.luau`; bos `roblox/plaats_prinseserwt_groen.luau`.
- Assets: huis **139451136573282** (8.6k tris), plein **120932882084389** (7.2k); texturen in `textures/asset_ids.txt`.
- Studio: PrinsesOpDeErwt, PrinsesOpDeErwtPlein, PrinsesOpDeErwtGroen (2127 planten, 55 bomen; zicht vanaf de paden vrij; in Wind-MAPPEN).
  Ground onder het plein, layout-label weg, spawn op het plein (OudeCFrame bewaard). Wandeltest Play: plein, hekje, bankjes, achter de pijler: OK,
  Y stabiel 4.7. Fps 14-15 op het plein en elders (Studio op de achtergrond). Screenshots `review/studio_v1_*.jpg`. Place opgeslagen (Team Create).
- NOG (later): interieur (hemelbed met 8 matrassen, Adinda, kaptafel, lampetkan; door de glasdeuren + kijkraam), klokgevel-voluten voller
  (dikkere krullen/consoles zoals Kamerheer), herringbone-paden (later, met de paden), hotelhek/poort (buiten 15 m), meubilair (lantaarns) later.

## De Trollenkoning (chat 11, 15 nov) — v1 in Studio (stronk + vijvertje + plein + bos; trol/uiltje/gordijnbeweging later). Daan: "voor nu prima, later finetunen"
Map `models/AR_Trollenkoning/`, brief `asset-brief.md`. Bronnen: 36 Eftepedia-plaatjes (`ref/eftepedia/`, contactblad `review/contact.jpg`), OSM 766787184 (stronk r 1.4),
55423661 (vijver r 2.9), paden 405848924 / 1406396368. Geen bouwtekeningen.
- Frame: oorsprong = midden 766787184 = studs (48.09, 17.88); -Y = holte (ZZO, naar de kruising van de twee paden); OSM -> model: X = 0.94*ox + 0.34*oy ;
  Y = -0.34*ox + 0.94*oy; Roblox F = (0.34, 0, 0.94).
- `build/03_boom.py` (TK_boom_master): stam als ringen met 9 wortelribben + wortels -> organisch(), afgebroken top met splinters + klimop, holte (spitsboog
  1.5 x 0.5..4.0 m) met DICHT rood gordijn (zo staat hij als niemand een sterrenbeeld kiest) boven de troonkist, 3 reuzenzwammen (bolle hoed + plaatjes),
  trapje zwammetjes rechts omlaag, tak met bel + touw, hoekige stenen in het water. Klei-overlay op Boomtrollenkoning: `build/cam.sh <tag> 0,-6.3,1.3,20 0 16 0,0 clay 36 669x1000`.
- `build/04_omgeving.py` (TK_omgeving_master): vijver (waterplaat + modderbodem + oeverwand), keienrand + groene buisleuning langs het plein, plein in licht
  grind (wig tussen de paden) met 13 verzonken dierenriem-medaillons, wijzersteen met bronzen wijzerplaat rechts op de rand (2023) + trilsteen, sprookjesboek.
- Bake `05_bake.py --pre TK --res 2048` / `--pre TO` (schors grijsgroen, zwam, zwamplaat, rots), `build/export.sh`, `zsh -ic build/upload.sh`,
  `python3 roblox/maak_plaatsscript.py` -> `plaats_trollenkoning.luau` + `plaats_trollenkoning_groen.luau`.
- Assets: boom **82116469856189** (55k tris), plein **120296597517083** (11k). Studio: Trollenkoning, TrollenkoningPlein, TrollenkoningGroen (1850 planten,
  55 bomen, beuk/rododendron; zicht voor vrij; De Prinses op de Erwt-gebied overgeslagen; in Wind-MAPPEN). Vijver zacht uitgegraven (FillCylinder),
  onzichtbare vijverbodem (je waadt), label weg, spawn op het plein. Wandeltest: plein OK, leuning houdt je bij r 3.1. Screenshots `review/studio_v1_*.jpg`.
- NOG (finetunen later, Daan): schors/zwammen realistischer (kleur, detail), trol + uiltje in de holte (figuren later), herringbone-paden, Muzikale Paddenstoel 7
  staat er al (niet van ons), camera-oplossing op de schuine foto's klopte niet (zwamhoogtes vs frontale foto) -> plaatsing wijzersteen/boek op foto-verhoudingen.

## De Sprekende Papegaai / Het Stoute Prinsesje (chat 11, 15 nov) — v1 in Studio (scene; finetunen later)
Map `models/AR_Papegaai/`, brief `asset-brief.md`. Bronnen: 15 Eftepedia-plaatjes (Intro_papegaai = frontaal, eind60/70 schuin met mensen,
Papegaai_totaal = ontwerp met gebogen hek, jaren-50 foto's), OSM 55423808 (plantvak/hek r 2.7), pad 405848924. Dak = rode pannen (foto), niet leien (lemma).
- Frame: oorsprong = midden 55423808 = studs (177.51, 28.92); -Y = naar het pad (ZW); OSM -> model: X = 0.8*ox - 0.6*oy ; Y = 0.6*ox + 0.8*oy; F = (-0.6, 0, 0.8).
- `build/03_papegaai.py` (PA_master, een asset): bakstenen muur 3.2 x 3.4 m met pijlers, rondboognis (wit stuc) tot 3.2 m, pannendak ~30 graden met 0.75 overstek
  op zware gebogen consoles, knoestige tak, ara (lijf organisch, opgeheven vleugels, lange staart, rood oog) schuin zoals Intro, bordje, klimop, plantvak met
  stenen, gebogen groene leuning, strook licht grind tot het pad. Klei-overlay: `build/cam.sh <tag> 0,-3.9,1.7,35 0 13 0,0 clay 36 1000x1000`.
- Bake `05_bake.py --pre PA`, export `exports/PA_papegaai.fbx`, `zsh -ic build/upload.sh`; plaatsen `roblox/plaats_papegaai.luau`, groen
  `roblox/plaats_papegaai_groen.luau` (SprekendePapegaaiGroen: 2380 planten, 55 bomen; in Wind-MAPPEN). Asset **136319841903954** (13k tris). Place opgeslagen (v199).
- v2 (Daan: "erachter zit een muur aan planten"): dichte plantenwand achter en naast de muur + groenbulten tegen de pijlers + struiken rechts naast de
  leuning (`roblox/plaats_papegaai_plantenwand.luau`, na het groenscript; zicht vanaf het pad linksvoor vrij), klimop 3x dichter, grind nu een strook tussen
  leuning en pad i.p.v. een achthoek (oude kale grond weer gras). Asset **89594139123073**. Screenshot `review/studio_v2_plantenwand.jpg`.
- NOG (later): ara mooier (veren, kop), dak/consoles fijner, nis-stuc met afgebladderde randen (foto), herringbone-pad, wandeltest.

## Raponsje (chat 11, 15 nov) — v1 in Studio (toren + vijvertje + bos; figuren Raponsje/heks later, finetunen later)
Map `models/AR_Raponsje/`, brief `asset-brief.md`. Bronnen: 16 Eftepedia-plaatjes; **Tvdv_raponsje = ontwerptekening (vrijwel orthografisch, 98 px/m)** als
blueprint, lemma: toren precies 10.01 m incl. windvaan. OSM 55423664 (toren r ~1.9), 766787183 (vijvertje), pad 405848924 (zuid), sluiproute 55340110.
- Frame: oorsprong = midden 55423664 = studs (252.09, 25.68); model = OSM-assen (X oost, Y noord), -Y = zuid (raam naar het pad); Roblox F = (0, 0, 1).
- `build/03_toren.py` (RA_master, een asset): achtkantige gegroefde stucschacht (2.33 -> 2.25 m, tot 5.9) met spitsboogfries en baksteenplekken, overkragende
  vakwerkverdieping 6.2-7.4 (raam met glas-in-lood boogje, plank, open luik, haak), spanendak tot 8.6, bol 9.1, windvaan (vogel + pijl) tot 10.01, vlecht tot ~1.9 m,
  rotsige sokkel + stucen ruinemuur, klimopranken met blad alleen langs de ranken, vijvertje (water + modder) met keienrand en blauwgroene buisleuning,
  sprookjesboek, grindstrook tot het pad. Klei-overlay op de tekening: `build/cam.sh <tag> 0,-300,5.0,1059 0 0 0,0 clay 36 666x1000` (orthografisch nagedaan).
- Bake `05_bake.py --pre RA`, export `exports/RA_toren.fbx`, `zsh -ic build/upload.sh`, plaatsen `roblox/plaats_raponsje.luau` (vijver zacht uitgegraven met
  FillBall), groen `roblox/plaats_raponsje_groen.luau` (RaponsjeGroen 1927 planten, 55 bomen; Papegaai-gebied overgeslagen; daarna 42 planten tussen pad en voet weg
  zodat vijver/leuning zichtbaar zijn zoals Boekloc). Asset **138467979361401** (24k tris). Screenshot `review/studio_v1.jpg`.
- v2 (Daan: "mag echt iets beter, je hebt de blueprints"): echte diepe rondboognissen (2 per zijde) in de schachttop via boolean (gespiegelde snijmatrix was de
  fout: determinant -1 = binnenstebuiten normalen = niets gesneden), klein boograampje met steen op de ZO-zijde, handgemaakte bobbels + scherpere groeven in de
  schacht, grotere baksteenplekken onderaan, vakwerk met dikke vierkante verweerde balken (stijlen, regels, middenstijl, schoren), dubbele vloerbalk, zware
  consoles, boeiplank langs de dakrand, grote bleke stapelstenen + stenen in de ruinemuur, klimop dun langs de ranken, stuc creme getint. Asset
  **133725694471918** (29k tris). `review/m3/pair.jpg` (materiaal vs tekening), `review/studio_v2.jpg`.
- NOG (later): figuren Raponsje (in het raam) en de heks (aan de vlecht), klimopblad groter/zichtbaarder, vakwerkvakken strakker, wandeltest.

## De Kleine Zeemeermin (chat 11, 15 nov) — v1 in Studio (scene; beeld grof, finetunen later)
Map `models/AR_Zeemeermin/`. Bronnen: 26 Eftepedia-plaatjes (Boekloc = overzicht, Kzmm = frontaal beeld, Zeemeermin-leeg = vijver + decor zonder beeld,
Zeemeermin2024, Cupido-close), lemma (decor = muur van de oude Liefdesbron, vijvertje uit 1954, beeld Ton van de Ven 1970), OSM node 7161344475, vijver/plek
55423759, rots 766787182, pad 405848924 (driesprong zuid) + sluippad 55444222. Geen bouwtekening.
- Frame: oorsprong = node 7161344475 = studs (361.59, 67.68); model = OSM-assen, -Y = zuid (naar het pad); Roblox F = (0, 0, 1).
- `build/03_zeemeermin.py` (ZM_master, een asset): vijfhoekig vijvertje (OSM) met betonnen binnenrand, water + modder, rotsstapel met ring van stenen,
  zittende meermin (lijf/hoofd/armen organisch, lang blond haar, groene staart met gele vin, schaal 1.35) met de grote spuwende vis kop-omlaag naast haar,
  wit barok decor aan de achterrand (middenpaneel met krullen en profiellijst, dolfijn-relief, schelpbekken op console + straal, Cupido), lage golvende
  vleugelmuren, smeedijzeren hekjes langs de zijkanten, breukstenen rand + lage blauwgroene leuning aan de padkant, sprookjesboek, grindstrook.
- Bake `--pre ZM` (stuc, natuursteen, rots, breuksteen), export `exports/ZM_zeemeermin.fbx`, plaatsen `roblox/plaats_zeemeermin.luau` (vijver zacht uitgegraven,
  onzichtbare bodem), groen `roblox/plaats_zeemeermin_groen.luau` (KleineZeemeerminGroen ~2320 planten, 55 bomen, plantenwand achter het decor en rechts naast het
  hek; in Wind-MAPPEN). Asset **101300529925530** (42k tris). Screenshot `review/studio_v1.jpg` (vanaf het Boekloc-standpunt).
- NOG (later): meermin realistischer (gezicht, schubben, staartkrul naar links-omlaag zoals Kzmm), vis met schubben/kleurverloop, Cupido fijner, waterstralen.

## Draak Lichtgeraakt (chat 11, 15 nov) — v1 in Studio (scene; draak grof, statisch; finetunen later)
Map `models/AR_Draak/`. Bronnen: 45 Eftepedia-plaatjes (Overzicht = frontaal, Boekloc_Draak2017/Overzicht_2020 = schuin, Kop/Ruststand = draak, Storing = muur,
Schatkist), lemma (muurtje 1952 van de Chinese Nachtegaal, draak 1979), OSM eiland 55423757, water 766787180, muur 766787181 (8.8 m), pad 405848924.
- Frame: oorsprong = zwaartepunt 55423757 = studs (363.72, -40.38); X = 0.264*ox - 0.965*oy, Y = 0.965*ox + 0.264*oy; -Y = naar het plein (W); Roblox F = (-0.965, 0, 0.264).
- `build/03_draak.py` (DR_master, een asset): pilaarmuurtje naar Overzicht (middenpijler 3.2 m breed x 4.6 m hoog iets terug, zijpilaren 3.4 m, buitenpilaren 2.1 m)
  met rode pannendakjes (holle pannen + nokpannen), gouden ornamentjes, takken + klimop, draak gehurkt bovenop (kop recht naar voren, open bek met tanden en
  gevorkte tong, gele ogen, paarse stekels/hoorns, wijde vleugels met vingers + vlies, staart rechts omlaag met speerpunt; schaal 1.25), breuksteen-eilandje
  met halfopen schatkist (dukaten, juwelen, kroon), water in twee lobben + modder + randstenen, rood Pieck-hek om de plein-tong, laag groen hekje langs de
  buitenrand, sprookjesboek, grindplein (tessellate_polygon met de waterrand als gat).
- Bake `--pre DR` (stuc per gevel, breuksteen, pannen), export `exports/DR_draak.fbx`, `build/upload.sh`, plaatsen `roblox/plaats_draak.luau` (vijver zacht
  uitgegraven, onzichtbare VijverBodem, label "De Draak" weg, spawn op het plein), groen `roblox/plaats_draak_groen.luau` (DraakGroen, plantenwand achter en
  naast het muurtje, Kabouterdorp (noord, y > 13) vrij; in Wind-MAPPEN). Screenshot `review/studio_v1.jpg`.
- NOG (later): draak realistischer (schubben, kop naar Kop-foto, vleugelvlies dunner/gerafeld), muur beige verweerd met vlekken, rookpluim/animatie (Daan).

## Snoeien onzichtbare planten (15 nov, Daan: "haal wat planten weg die je toch niet ziet vanaf het pad")
`tools/snoei_onzichtbaar.luau`: OSM-padennet (footway/path/pedestrian/steps/service..., Douglas-Peucker 4 studs) in het script; per plant in alle *Groen/*Bos
mappen de afstand tot het dichtstbijzijnde pad: bodem/bloemen > 8 m, struiken > 17 m, bomen > 30 m weg. Eerste run: 6487 weg, 17801 over. Opnieuw draaien na
nieuwe groen-scripts. Daarna ook over de hele map (Daan: "tenzij het bij de scene hoort"): VillaVoltaPlantenEcht -387, VillaVoltaHorizon -298,
SprookjesboomPlanten 0; alles binnen 15 m van een attractiemodel blijft staan. Padennet staat als `ServerStorage.PadNetOSM` (ModuleScript).

## De Wolf en de Zeven Geitjes (chat 11, 15 nov) — v1 in Studio (huisje + tuin + scene; geiten/wolf/moeder geit en interieur later)
Map `models/AR_Geitjes/`. Bronnen: 51 Eftepedia-plaatjes (7GeitjesAvond = padzijde met gezicht + gaanderij, ext1981 = poortgevel, ZevenGeitjes_Achterkant,
Voorstudiegeitjes = plattegrondschets met put/puthaal/wiel/waslijn, Boekloc + Moeder-geit = afdakje aan het pad, Dewolf, gevel-negentig = nis met schildje),
lemma. OSM gebouw 55423662 (8.45 x 7.45 m, uitsparing NW), voetpad 397496612/397496610/55539213 (door het huisje), hoofdpad 405848924 (noord + oost).
- Frame: oorsprong = zwaartepunt 55423662 = studs (300.3, -127.23); model = OSM +7.27 graden (gevels assen-recht); +Y = noord (hoofdpad), -Y = achtertuin;
  Roblox F = (0.1265, 0, 0.992) (= model -Y).
- `build/03_geitjes.py` (GT_master): zuidblok + noordblok met overdekte doorgang (boog in de oostgevel), krullende Pieck-gevels boven het riet uit
  (daklijn + 0.55 m, schouders, kopje), riet met golvende nok + rode nokpannen, dakkapel, hoge schoorsteen met windvaan, nis met rood knolraapschildje,
  boogvensters met warm licht, breuksteen in het stuc, bebaard gezicht op de NW-hoek, gaanderij met groene zuiltjes + lessenaarsdakje + leuning in de
  uitsparing (wolfdeur + kijkvenster), achterdeur met spitse kap, achtertuin (put, puthaal met emmer, rood wagenwiel, vogelhuisje, waslijn), afdakje van
  moeder geit met lage stucmuur, plankenhek langs het pad, sprookjesboek, grindplein. Muur-remesh gedecimeerd: 97k tris.
- Bake `--pre GT` (stuc per gevel, breuksteen, riet, pannen), export `exports/GT_geitjes.fbx`, plaatsen `roblox/plaats_geitjes.luau` (label weg, grond
  onder plein/huis, modder in de tuin, spawn op het plein), groen `roblox/plaats_geitjes_groen.luau` (GeitjesGroen ~1760 planten, 55 bomen, plantenwand
  achter de tuin, rododendrons achter moeder geit, meteen gesnoeid op padafstand; in Wind-MAPPEN). Screenshots `review/studio_v1.jpg`, `studio_v1_west.jpg`.
- NOG (later): figuren (moeder geit, wolf in rokkostuum, geitjes binnen), interieur (woonkamer met klok, slaapkamer), gezicht fijner (Avond), stuc groenig verweerd.

## Vrouw Holle (chat 11, 15 nov) — v1 in Studio (huisje + voortuin + put; Vrouw Holle-figuur/kussen/sneeuw en dia's in de put later)
Map `models/AR_VrouwHolle/`. Bronnen: 61 Eftepedia-plaatjes (Boekloc = bezoekersgevel met tuintje, Vrouwholletotaal, Huisje-holle-2010, Holleput,
Sprookjesmuseum = noordgevel met dubbele deur, VrouwHollestenen = boogstenen met gezichtjes, herbouw 2022), lemma. OSM huis 1109001371, put 55424650,
paden 1001200259/1116332898 (lus om het huis), 1054471996/1074489754 (lus om de put).
- Frame: oorsprong = zwaartepunt 1109001371 = studs (2.73, -90.69); model = OSM -6.8 graden; -Y = zuid (bezoekersgevel, put op (10.15, -20.4));
  Roblox F = (0.1184, 0, 0.993).
- `build/03_holle.py` (VH_master): steil rietdak (nok 5.7, overstek 0.9) met rietrollen over de windveren en nokrol, wit stuc met bolle hoeksteunen,
  bezoekersgevel met twee boogdeurtjes (natuursteen boogstenen, 3 loerende gezichtjes per deur), raam met bloembak, open luikenraam, spoor van goud en pek,
  noordgevel met dubbele boogdeur + rond raampje, aanbouw oost met dwarsdakje, schoorsteen, haan op de nok, voortuintje (laag bakstenen muurtje,
  smeedijzeren hekje + poortje, emmer met mattenklopper, modderbed met tulpen), put (baksteen, natuurstenen rand, stalen kijkrooster, houten pannendak op
  twee staanders met schoren, heksen-windvanen, groene projectorkist), 3 grindvlakken (huis, rond putpleintje, verbindingsstrook), sprookjesboek. 55k tris.
- Bake `--pre VH` (stuc per gevel, riet, baksteen), export `exports/VH_holle.fbx`, plaatsen `roblox/plaats_holle.luau` (labels "Vrouw Holle" + "De Put van
  Vrouw Holle" weg), groen `roblox/plaats_holle_groen.luau` (VrouwHolleGroen ~1400, rododendronkrans om het putpleintje, tulpen in de voortuin, gesnoeid;
  Herautenplein/Trollenkoning/Ezeltje vrij; in Wind-MAPPEN). Screenshots `review/studio_v1.jpg`, `studio_v1_put.jpg`.
- NOG (later): Vrouw Holle met kussen in het luikenraam + sneeuw (animatie), dia-voorstelling in de put, gevels organischer (bolle Pieck-vormen).

## Kleine Boodschap (chat 11, 15 nov) — v1 in Studio (beeld + waterbak + haag; armbeweging later)
Map `models/AR_KleineBoodschap/`. Bronnen: 31 Eftepedia-plaatjes (Intro/Boodschap = beeld close-up, Kbvijver = waterbak met haag en bloemen), lemma.
OSM-node Kleine Boodschap (tussen toiletgebouw, Vrouw Holle en Herberg), vijvertje 625505853.
- Frame: oorsprong = node = studs (-46.68, -92.28); model +X = noord, -Y = oost (kijkrichting, naar pad 1001200259); Roblox F = (1, 0, 0).
- `build/03_boodschap.py` (KB_master, geen bake: Roblox-materialen): niervormige waterbak met gemetselde rand, bakstenen muurtje (1.6 m) aan de achterrand,
  kabouter v1 (groot hoofd, blonde lokken, blauwe krulmuts met rode veer, capeje, geblokte zakdoek, rechtervoet op de muur, duim omhoog, linkerhand op de
  rand), hoge U-haag (geremeshte blokken), laag houten hekje, modderbed, grindplein tot het hekje. 70k tris.
- Plaatsen `roblox/plaats_boodschap.luau` (ook bomen uit HerautenpleinBos binnen de scene weg), groen `roblox/plaats_boodschap_groen.luau`
  (KleineBoodschapGroen: begoniarand + struiken/varens; in Wind-MAPPEN). Screenshot `review/studio_v1.jpg`.
- NOG (later): kabouter realistischer (gezicht naar Intro, stoffen plooien), wijzende armbeweging (animatie), haag fijner.

## De Indische Waterlelies (chat 11, 15 nov) — v1 in Studio (voorplein, wachters, gaanderij, tunnel, loods-schil; grot/show en interieur later)
Map `models/AR_Waterlelies/`. Bronnen: 129 Eftepedia-plaatjes (Waterlelies_Voorplein_2024, Indischewaterlelies-voorplein-mei09 = wachters + gaanderij,
Iwplein77, Lelies_ansicht, IndelingIW = plattegrondschets, Rolschaats = luchtfoto, Waterlelies_Ingang_2024), lemma. OSM: attractie 279667940, gebouw
1395767223 (incl. gaanderijstrook), vijver 55441202, plein 55441203, rotstunnel 556674121, paden 767397166/767397167.
- Frame: oorsprong = midden vijver = studs (109.98, -351.87); model = OSM -12.3 graden; +Y = noord (gaanderij); Roblox F = (0.213, 0, 0.977).
- `build/03_lelies.py` (WL_master): vijver 15.6 x 10.3 m met witte rand + gouden lotusfontein + gouden reigerbeeldje, gaanderij met 7 witte zuilen,
  donkere achterwand met rood-gouden leeuwenschilden en deur naar de grot, overhangende grijze rotsmassa (geremeshte blokken), 2 tempelwachters v1
  (goud/rood, gelaagde kroon, slagtanden, knots), verhoogd wit plantenbed, witte muren met Simurgh-deur (west), bankjes + varenborder (zuid),
  rotstunnel met gouden naambord, groene showloods (279667940) als schil, grindplein met gat voor de vijver. 74k tris.
- Bake `--pre WL` (stuc per gevel, rots; rots in Studio getint 205,208,208), plaatsen `roblox/plaats_lelies.luau`, groen
  `roblox/plaats_lelies_groen.luau` (WaterleliesGroen ~1080: boomvarens langs de muren, plantenbed, bomen rond tunnel en loods, gesnoeid; in Wind-MAPPEN).
  Screenshots `review/studio_v1.jpg`, `studio_v1_wachters.jpg`.
- NOG (later): grot met tribune en de show (elfjes, kikkerorkest, heks, lelies), wachters gedetailleerder (schubben, gezicht), rotsen grilliger,
  wegwijzer met witte vogel, gevlamd natuurstenen plaveisel.

## De Vliegende Fakir (chat 11, 15 nov) — v1 in Studio (paleis + voortuin; fakirs, vliegend tapijt en bloeiende tulpen later)
Map `models/AR_Fakir/`. Bronnen: 58 Eftepedia-plaatjes (Fakirpaleis = frontaal, Intro_fakir/Fakirvliegt = toren close-up, Fakir_1981, Boekloc = hekje
naast het plein), lemma. OSM: paleis 50911617, middenvijver 184688429, L-water 184688431/432, tulpenranden 556546221/222, gras 55441538, lange
waterbak 184688428, plein 55350040.
- Frame: oorsprong = zwaartepunt 50911617 = studs (240.66, -638.46); model = OSM -7.3 graden; -Y = zuid (plein); Roblox F = (0.127, 0, 0.992).
- `build/03_fakir.py` (FK_master, strakke architectuur zonder remesh: 6.6k tris): gaanderij met 5 gekartelde ezelsrugbogen + motiefjeswand, laag rood
  schilddak met gouden randen, kantelenmuur (16 kantelen, voegenlijnen), 2 torens (benedenverdieping met ezelsrugraam en sierpanelen, brede rode luifel,
  bovenverdieping met raam + rood kleed, rood dak, achtkantige trommel met boogjes, uikoepel, gouden spits, rafel-arm), middenvijver met gouden
  fonteinvaas, L-water om de torens, tulpenbedden, geplaveide binnentuin (licht grind), grasrand, lange waterbak, oosterse roosterhekjes, sprookjesboek, plein.
- Bake `--pre FK` (stuc per gevel, pannen), plaatsen `roblox/plaats_fakir.luau` (label "De Tuinman en de Fakir" weg), groen `roblox/plaats_fakir_groen.luau`
  (FakirGroen ~1220: plantenwand achter de kantelenmuur, rododendrons naast de hekjes, tulpen wit/rood (geel ontbreekt in de plantbron), bomen; gesnoeid;
  in Wind-MAPPEN). Screenshot `review/studio_v1.jpg`.
- NOG (later): fakirs in de torens + vliegend tapijt (animatie), gele tulpen (bron toevoegen), motiefjes/schilderingen fijner, dakpannen strakker.

## De Chinese Nachtegaal (chat 11, 15 nov) — v1 in Studio: versie 1999-2026 (Daan koos het paleis; echt gebouw gesloopt sept. 2026, nieuwe versie 2027)
Map `models/AR_Nachtegaal/`. Bronnen: 111 Eftepedia-plaatjes (Intro_nachtegaal, Chineseachtergaal1 = hellende muren + balustrade, Voortuin_Overzicht,
Nachtegaalingang, Ingang-cn-boog = maanpoort, Chinese_Nachtegaal_Sneeuw, Vogelperspectief-2027), lemma. OSM: paleis 50911622, achterterrein 961616762,
tuinmuur 767716980 met maanpoort-ingang, tuinpad 55350038, vijvertje 961616761, uitgangsmuur 556546231, grote vijver 86734294 (noord).
- Frame: oorsprong = zwaartepunt 50911622 = studs (400.32, -526.62); model = OSM -8.2 graden; -Y = zuid; Roblox F = (0.143, 0, 0.990).
- `build/03_nachtegaal.py` (CN_master, 26k tris): beige blok 7.4 m met licht hellende muren, blauwgroene friesband met gouden panelen, dakrandlijst +
  roze balustrade, bakstenen hoektanding en doorpiepende bakstenen, pagodetorentje boven de uitgang (rode zuiltjes, fries, 2 blauwe krulpannendaken,
  roze balustrade, gouden spits + draakjes), ingangsuitbouw (grijsgroen pannendak met nokornament, groene ornamentrand, donkere deur, blauwe potten,
  lampjes), noordmuur met maanpoort (groene pannenkap, pilaren met lantaarns), west/zuid muurtje met houten raamwerk, rode dienstdeur, zwart grind,
  kronkelpad (licht grind), lavarotsen, vijvertje, lantaarns, stenen lantaarn, bankjes, potten, sprookjesboek, rotsen + watervalletje (noord),
  uitgangsmuur met poortje + uitgangspad.
- Bake `--pre CN` (stuc per gevel, baksteen, rots; rots in Studio getint 70,68,68), plaatsen `roblox/plaats_nachtegaal.luau`, groen
  `roblox/plaats_nachtegaal_groen.luau` (NachtegaalGroen ~1350: azalea's + siergras langs de tuinmuren, bos rondom, gesnoeid; in Wind-MAPPEN).
  Screenshots `review/studio_v1.jpg` (noordkant), `studio_v1_tuin.jpg`.
- TWIJFEL: torentje staat volgens OSM boven de uitgang (oost); op de sneeuwfoto lijkt het meer naar rechts te staan - nakijken met Daan.
- NOG (later): interieur/show (keizer, Dood, mechanische en echte nachtegaal), bamboe, kersenbloesem, scheurtjes in het stuc, draakjes fijner.

## Het Kabouterdorp (chat 11, 15 nov) — v1 in Studio (alle huisjes + paden + vijvers + bos; kabouters, waterradbeweging, bel en show later)
Map `models/AR_Kabouterdorp/`. Bronnen: 84 Eftepedia-plaatjes + lemma (beschrijving per onderdeel). OSM: dorp 55423167, hoofdpad 1074483532, zwammetjes
55444984/55445041, grote zwam 763240405 (+ ring 763240404), morieljehuis 55444985, Grote Kabouterhuis 55444983, vijvers 767397170/763240399/763240398,
beekje 767397169, boom "De Gouden Stemvork" = Kabouterboom, Muzikale Paddenstoel 1.
- Frame: oorsprong = zwaartepunt 55423167 = studs (458.25, -63.78); model = OSM-assen (x oost, y noord); Roblox F = (0, 0, 1).
- `build/03_kabouterdorp.py` (KD_master, 70k tris): paddenstoelenparcours (2 vliegenzwammen met lage doorgangen, raampjes met hartjesluiken,
  lantaarntjes, schoorsteentje, morielje-doorloop, bruggetje over het beekje, tafeltje + 4 krukjes, waslijntje, laag poortje met hartjesbord),
  Kabouterboom (holle stam + wortels + dikke takken, gezicht, kijkruitjes, deurtje), loze vissertje (overhangende zwam over de oostvijver, bootje,
  hengel met dennenappel, bordje), morieljehuis (gestucte voet + lange morieljehoed, deur, raam, trapje), grote vliegenzwam (steel r 3 m, hoed r 4.75 m,
  luikenraam, bovendeur + bordes + trap op, houten trap omlaag naar het beekje), huisje met waterrad (pannendak, klokgevel, morieljehoed rechts,
  waterrad, bruggetje, hekje, stro-afdakje met tobbe), Grote Kabouterhuis (organische muren op OSM, morieljekegel, vliegenzwamdak, 2 doorloop-poortjes,
  hoefijzer, traliewerk, balkonnetje, klokkentorentje, loden schoorsteentje, windvaantjes), vijvers met steenrand, paden (licht grind), sprookjesboek.
- Bake `--pre KD` (stuc per gevel, zwam, schors, riet, pannen), plaatsen `roblox/plaats_kabouterdorp.luau` (3 vijvers uitgegraven + onzichtbare bodem,
  grond onder het hoofdpad), groen `roblox/plaats_kabouterdorp_groen.luau` (KabouterdorpGroen ~2310: bos tussen de huisjes; in Wind-MAPPEN).
  Screenshots `review/studio_v1.jpg` (grote zwam + waterrad), `studio_v1_parcours.jpg`, `studio_v1_grotehuis.jpg`.
- NOG (later): kabouters (muziek, vissertje, pijproker, schrijver met eekhoorn, deurkabouter, wasvrouwtje, rustende kabouters), witte stippen groter,
  interieurs (schrijfkamer, kachel, slaapkamer), waterrad laten draaien, kijkbuizen, bordjes met rijmpjes, morielje-ribbels fijner.

## De Zes Dienaren (chat 11, 15 nov) — v1 in Studio: Kogeloog-gebouwtje (arcade), Langnek stond er al (CH_Langnek)
- Blender: models/AR_ZesDienaren/build/03_kogeloog.py (master KG_master.blend, 12.7k tris). Geknikte witte arcade over 3 segmenten langs de OSM-gevellijn,
  rondbogen op Toscaanse zuilen, bakstenen kopgevels, achterwand, tegelvloer, houten plafond, zadeldak met rode pannen; ovale schilderijen, bankjes, lantaarns.
  Midden: barokke dakgevel met blauw schild, gouden lint en buste van Kogeloog (rode jas, blinddoek, steek met veren), vazen, kiosk-luik.
- Plein: OSM plaza 766787197, licht grind (terrein onder plein → Ground).
- Studio: roblox/plaats_kogeloog.luau (asset 111628397476125, frame studs (485.37, 150.69), F=(0,0,1)); 2 oude labels weg.
- Groen: roblox/plaats_kogeloog_groen.luau → workspace.KogeloogGroen (812 planten, 28 bomen; rododendrons dicht achter het gebouw), Langnek-hoek en paden vrij; Wind-keten + KogeloogGroen.
- Later: andere dienaren (Breedkop, Scherpoor, Dikke, Lange, Kogeloog-animatie), interieur-schilderingen finetunen.
- Screenshot: models/AR_ZesDienaren/review/studio_v1.jpg

## Sprookjesbos — alle attracties staan als v1 in Studio (15 nov)
Volgende stap alleen op verzoek van Daan: finetunen, figuren, interieurs, animaties.

## Daarna (volgorde met Daan afgesproken)
1. Villa Volta (KLAAR). 2. Sprookjesboom + paddenstoelen (KLAAR), Langnek (KLAAR, statisch), Assepoester (KLAAR, interieur later). 3. Lantaarnpaal/bankje/prullenbak. 4. Gijs afmaken. Hans en Grietje: figuren later (huis + tuin KLAAR v1).
5. Park terugzetten en mooier (den-lagen, kleinere bladkaarten, gras/bosgrondtexturen, opsluitbanden, oevers). 6. Grote gebouwen (entree, Symbolica).
Kaatsheuvel eromheen: later.

## Geïnstalleerde skills (in ~/.claude/skills)
blender-image-to-3d (kern), blender-cinematic-modeling, blender-core, blender-texturing, blender-texture-baking, blender-asset-qa,
blender-export-pipelines, blender-hardsurface-modeling, blender-retopology-uv, blender-game-optimization, blender-environment-kits,
blender-pipeline-automation, roblox-animation, roblox-texture-gen, roblox-vfx, roblox-3d-model, roblox-skills-setup.

## Realisme-plan gestart (15 nov) — stap 0 klaar, stap 1a (AHN-terrein) klaar in Studio
- `PLAN_REALISME.md` staat in main (bouwvolgorde onderaan). Skill `skills/efteling-sprookje/` (ook in ~/.claude/skills).
- `tools/geo.py` (park-m <-> RD <-> WGS <-> studs), `tools/uitsnede.py` (luchtfoto 5 cm/px + AHN-hoogte + OSM-overlay per plek).
- **Terrein Sprookjesbos op echte hoogte (keuze B, Daan liet het aan mij):** maaiveld uit AHN4 (NAP 8,89 = Y 2), -6,6 tot +12,4 studs,
  loopt 30 m buiten het Sprookjesbos weer naar Y 2. Terreinkolommen verschoven (vijvers/uitgravingen mee), ~31.000 objecten mee
  verschoven (attribuut `AHN_dY`): kleine v1-modellen als geheel op een plateau, grote v1-modellen per onderdeel, bomen/planten per stuk.
  Doornroosje staat nu op zijn heuvel (+11,3). Alles in `ServerStorage.AHN_Delta` (Veld/Schuif/Objecten/Terugdraaien) + backup
  `ServerStorage.Backup_Terrein_voor_AHN_15nov`; uitleg `tools/studio/AHN_README.md`.
- **Nieuw maaiveld voor alles wat je hierna plaatst: `Y = 2 + require(ServerStorage.AHN_Delta.Veld).dy(X, Z)`** (niet meer vast Y 2).
- Bekend: grote vlakke v1-grond/padmeshes kantelen niet mee; op hellingen steken randen iets in/uit het terrein. Wordt opgelost in
  stap 1b (paden opnieuw in Blender op dit terrein) en stap 5 (scène per attractie). Place nog NIET opgeslagen (vraag Daan).

## Stap 1b: paden Sprookjesbos (15 nov) — in Studio als workspace.SprookjesbosPaden
Map `models/PR_Paden/`. Bron padvormen: **BGT wegdeel** (PDOK OGC API, actuele vlakken, cm-nauwkeurig; `reference/paden/bgt_*.json`),
aangevuld met OSM-paden die > 3 m van een BGT-pad liggen (2,2 m / 3,5 m breed). Luchtfoto 10 cm: `reference/paden/luchtfoto_10cm.jpg`.
- `build/01_vlakken.py` (venv met shapely) -> `ref_paden.json`: klinker 12.800 m2, kassei 1.350 m2 (alleen zijpaden met OSM surface=sett,
  grens langs de rand van het klinkerpad), asfalt 490 m2.
- `build/02_mesh.py`: driehoeken per tegel van 24 m op het AHN-veld (`tools/veld.py` = exact het Studio-veld), looplaag +0,18 stud,
  bolling 2,5 cm, kantsteenrij 0,22 m binnen de rand, bosgrondstrook 0,8 m buiten de rand (alfa), rok 0,3 m omlaag.
  **Verband:** halfsteens, rijen haaks op de looprichting, via een vloeiend richtingsveld (OSM-stukken samengevoegd tot 79 doorlopende
  paden, gericht, gewogen gemiddeld) + Poisson-oplossing voor u/v -> geen naden, waaiert uit bij vorken; brede pleinen recht langs de lange as.
- `build/03_texturen.py`: klinker/kassei/kantsteen per steen opgebouwd (kleuren uit Kabouterdorp_pad.jpg, diepe donkere voegen, AO,
  normal 4-5), asfalt = ambientCG Ground091, rand = ambientCG Ground076 (CC0). `build/04_blender.py`: Blender, renders, FBX. `build/upload.sh`.
- Studio: `roblox/plaats_paden.luau` (model 132911656696735; 419 MeshParts, ~91k driehoeken, PreciseConvexDecomposition, rand zonder botsing).
  Terrein onder de looplaag 0,5 stud omlaag + Ground, onder de rand Ground (`ServerStorage.AHN_Delta.PadenTerrein`, banden gedaan:
  attribuut PadenTerreinBanden — niet opnieuw draaien).
- Opgeruimd (terug te zetten, attribuut Herkomst): 4.812 v1-planten/bomen die OP het pad stonden -> `ServerStorage.OpPadVerwijderd`;
  16 v1-grind/klinkervlakken die >= 75% onder het nieuwe pad lagen -> `ServerStorage.V1PadVervangen`; 8 deels overlappende (o.a.
  Herautenplein plavuis/kassei) 0,25 stud lager (attribuut PadLager).
- NOG / bekend: overal hetzelfde klinkertype (BGT zegt bijna overal betonstraatstenen); variatie per stuk (flagstone-pleintjes, houten
  bruggetjes, trappen, keien i.p.v. kantsteen, kleurverschillen, roze Herautenplein) volgt uit video-frames per traject (stap 4, yt-dlp/ffmpeg
  vragen). Kabouterdorp-tonnetje staat op het pad (v1-plaatsing, stap 5). Herautenplein: lappendeken v1-plavuis + nieuw pad (stap 5).
  Place nog niet opgeslagen na de paden.

### Paden, ronde 2 (15 nov avond) — Daan: "echt alsof je het zelf legt; nu gaat het vaak mis bij rondjes"
- Legwijze per soort stuk (stratenmaker): doorlopend verband langs elk pad (OSM-stukken samengevoegd), langste pad gaat door
  kruisingen (zijpad sluit aan met snijlijn langs de rand van het hoofdpad), **verbredingen** (halve breedte > 1,9 m) herkend:
  rond -> ringen om het middelpunt (18 stuks), anders recht langs de lange as (38). Geen wervelingen meer.
- **Zones** (`models/PR_Paden/ref_zones.json`, per plek soort + richting + bron): Herautenplein = grijze kasseien in waaierverband
  (lanen + rond het plein), roze klinkers in ringen (rond plein), lichte platen rond de fontein (luchtfoto + Eftepedia-foto's).
  Oude v1-bestrating Herautenplein (plavuis/kassei) -> ServerStorage.V1PadVervangen.
- Naden tussen BGT-vlakken tot 1 m gesloten. Controle: bovenaanzicht-atlas van het hele net (`review/atlas_*.jpg`, 48 vakken van 40 m).
- Studio: model 117439322924252, 431 delen. Place nog opslaan.
- NOG: terrein onder de net gesloten naadjes (< 1 m) is niet verlaagd (kan hier en daar door het pad prikken: controleren);
  soort bestrating per traject uit de video (yt-dlp/ffmpeg staan in `.venv-video`, video "Alone in the Efteling Fairy Tale Forest"
  2:23 u -> 1.724 frames elke 5 s in de scratchpad; `tools/video_frames.py`); kasseizones nu alleen waar OSM surface=sett zegt.

## Paden, ronde 3: bestrating per stuk uit de video (15 nov 2026)
- Bron: wandelvideo "Alone in the Efteling Fairy Tale Forest" (2,5 uur, frames om de 5 s), route langs de attracties gevolgd en per stuk pad de bestrating vastgesteld. Bewijsbeelden: models/PR_Paden/review/video_bewijs_*.jpg, kaart met soorten: review/soorten_kaart.jpg.
- Bevinding: bijna alle bospaden zijn **klinkers in visgraatverband** (niet halfsteens). Kleur: verweerd roodbruin/roze-grijs (noorden, oosten, Kabouterdorp-Langnek, Vrouw Holle, Zevengeitjes) of grijs (zuidelijk bos: Trollenkoning, Rapunzel, Zeemeermin, Draak, Langnek-Roodkapje, Rode Schoentjes, Hans en Grietje).
- Nieuwe texturen (03_texturen.py): `klinker` = roodbruine visgraat (nieuw), `grijs` = grijze visgraat, `keitjes` = lichte keitjes (Kabouterdorp). Visgraat is een echt 90-graden-rooster (steen 2:1) onder 45 graden met het pad, naadloos per 2 m.
- Zones (ref_zones.json): Zuidbos_grijs (alleen klinker vervangen), Kabouterdorp_keitjes; Herautentuin nu glad grijs (asfalt) in plaats van waaier (video 90:00/97:40). Kasseipaden (Roodkapje, Pinokkio, Rode Schoentjes, Doornroosje) en de waaier rond het Herautenplein (video 65:20) blijven.
- 02_mesh.py: zones kunnen `alleen` (welke soorten ze vervangen) en `uv: veld` (verband blijft het pad volgen).
- Studio: MODEL 80732356672347, 448 delen met textuur (klinker 99, grijs 33, keitjes 5, kassei 17, waaier 8, roze 3, plavuis 4, asfalt 18). Place nog niet opgeslagen.
- Nog open: Trollenkoningplein lijkt in de video grote grijze platen (nu grijze visgraat); bij Assepoester/Zes Zwanen staat een roodbruin plein met kasseirand (video 77:10) dat nu BGT-asfalt is; ronde verbredingen in Kabouterdorp tonen zichtbare ringen.

### Ronde 3b (15 nov 2026): de drie open plekken
- Trollenkoningplein: nieuwe textuur `platen` (lichtgrijze betonplaten 40 x 40 cm, video 35:00-35:10) op het BGT-plein ten zuiden van de boom, randen haaks op de padmonden.
- Rond plein Herautenplein: de "Assepoester-plek" uit video 77:10 bleek dit plein te zijn (Kikkerkoning-fontein erachter). Roodbruine ringen klopten al; roze textuur bruiner gemaakt en een cirkel grijze kasseien (r 2,5 m) rond de sokkel toegevoegd (76:55). Asfalt bij Assepoester/Zes Zwanen klopt wel (video 77:45-78:15).
- Kabouterdorp-keitjes nu recht gelegd (hoek 90), geen ringen meer.
- In Studio lagen v1-delen over de nieuwe paden en staken erdoorheen (beige vlakken op het ronde plein): Herautenplein.MAT_bodem, SneeuwwitjeOmgeving.MAT_aarde/MAT_klinker/MAT_band -> ServerStorage.V1PadVervangen (attribuut Herkomst, terug te zetten). plaats_paden.luau doet dit nu ook.
- Studio: MODEL 93309456015457, 451 delen met textuur. Place nog niet opgeslagen.
- Open (stap 5): voor de Trollenkoning-boom ligt nog het beige v1-pleintje van TrollenkoningPlein met een strook gras tot het platenplein; in het echt staat de boom aan het platenplein.

### Ronde 3c (15 nov 2026): geen gare overgangen
- Daan: overal hetzelfde pad aanhouden als een overgang lelijk wordt; alleen het Herautenplein houdt eigen bestrating.
- Zones `Zuidbos_grijs` en `Kabouterdorp_keitjes` zijn nu `per_pad`: elk pad wordt op zijn kruisingen in stukken geknipt, stukken zonder zichtbare aansluiting (bestrating daar niet breder dan het pad) worden samengevoegd tot een route, en een route krijgt in zijn geheel een soort (meerderheid van de lengte in de zone). Verbredingen stemmen mee met de paden die erdoorheen lopen. De soort wisselt dus alleen waar een zijpad echt aansluit of een plein begint.
- Platen op het Trollenkoningplein weer weg (rechte snijlijn); daar loopt de grijze visgraat door.
- Gevolg: het pad langs Zevengeitjes is nu ook grijs (loopt zonder kruising door in de grijze lus), het hoofdpad door Kabouterdorp is roodbruin met keitjes op de zijpaden/pleintjes.
- Studio: MODEL 129106712042227, 447 delen met textuur. Place nog niet opgeslagen.

### Ronde 3d (15 nov 2026): paden van de v1-assets weg
- Daan: bij de assets zat al pad, dat gaf de fouten. Alle v1-delen gemeten (631 platte delen in het Sprookjesbos): welk deel ligt op de plek van een nieuw pad. Op materiaal geselecteerd (klinker, grind, flagstone, tegels, ijsselsteen, vloer, band, snoeppad, aarde) en overlap >= 25%.
- 24 asset-paden (plus eerder 4: Herautenplein.MAT_bodem en Sneeuwwitje-omgeving aarde/klinker/band) staan nu in ServerStorage.V1PadVervangen met attribuut Herkomst; plaats_paden.luau verplaatst ze bij een nieuwe plaatsing ook.
- Bewust blijven staan: vijver-/podiumbodems, water en modder, siergrind Chinese tuin, Villa Volta, Sneeuwwitje-vloer, delen die naast de paden liggen (bv. grindpleintje voor de Trollenkoning-boom, Kogeloog- en Roodkapje-tegels, Kleine Zeemeermin-grind).
- Place nog niet opgeslagen.

### Ronde 3e (15 nov 2026): strepen weg, Trollenkoningplein
- Strepen in de bestrating (Daan, screenshot bij park 26.6,2.4): fout in lijn_uv. De langsrichting was s - v*theta met theta de opgetelde draaiing van het hele pad; op lange kronkelpaden (de grote keten is 1,5 km) gaf dat afschuiving tot 16x uitgerekt. Nu u = booglengte langs de middellijn. Uitgerekte driehoeken (verhouding > 1,6): klinker 5%, grijs 8% (krappe binnenbochten); eerder 28-36% boven 2,5.
- Trollenkoningplein: het v1-grindpleintje is vervangen door een extra bestraat vlak (ref_zones.json 'extra_vlakken', vorm uit Studio) met lichtgrijze platen (video 35:00); de grasstrook tot het pad is gedicht, alleen strookjes die aan het plein grenzen, en het bestaande pad blijft grijze visgraat (pleinrand langs de padrand). TrollenkoningPlein.MAT_grind_0 -> V1PadVervangen.
- Studio: MODEL 132138991118243, 451 delen met textuur (speltest gestopt om in Edit te plaatsen). Place nog niet opgeslagen.
- Nog open: ronde verbredingen en het roze rondplein houden wat uitrekking (ringen); niet in Studio op screenshot gecontroleerd (capture reageerde niet), wel in Blender.

### Ronde 3f (15 nov 2026): overal dezelfde visgraat
- Daan: overal de gelegde steentjes, alleen het oranje rondje bij het plein niet. Nu: alle padvlakken grijze visgraatklinkers (`eenheid: grijs` in ref_zones.json, 02_mesh.py voegt alle soorten samen), ook waar eerder asfalt, kasseien, keitjes, waaier, platen (fontein, Trollenkoningplein) en de Herautentuin lagen. Alleen het rondje op het Herautenplein (roze ringen + kasseicirkel rond de sokkel) wijkt af.
- De video-indeling (rood/grijs, kasseien, keitjes, waaier) staat nog in git-geschiedenis en de bouwcode (per_pad-zones, texturen) als het ooit terug moet.
- Studio: MODEL 73836082264416, 395 delen met textuur. Niet op screenshot gecontroleerd in Studio (capture reageerde niet), wel in Blender. Place nog niet opgeslagen.

### Ronde 3g (15 nov 2026): een samenhangend padennet, alleen het Sprookjesbos
- Daan: paden moeten op elkaar aansluiten, geen pad dat nergens op uitkomt (behalve aan begin/eind van het Sprookjesbos); dingen in de hoeken die niet bij het bos horen moeten weg.
- `rand_sprookjesbos` (ref_zones.json): alle bestrating buiten de rand weg (promenade zuid, driehoeksplein zuidoost, strook langs het kasteelgebouw, oprit hotel, servicewegen west/oost, parkeerterrein). Paden die de rand kruisen eindigen daar (in-/uitgang).
- `losse_stukken`: losse padstukken binnen de rand worden aangesloten langs het OSM-looppad door het gat (anders kortste lijn): noordelijk deel (Sprookjesboom/Fakir/Chinese Nachtegaal, 5,6 m), tuinpad noord, stukjes Kabouterdorp, stukje Roodkapje. Weg: strook over een gebouwdak, snippers, smalle strook naast het pad bij Kabouterdorp-noord. Handmatige brug: twee padstukken bij Holle Bolle Gijs.
- Controle: het net is een geheel (1 stuk, 12.652 m2). tools/pad_einden.py vindt 7 einden: 2 aan de rand, 5 bij een attractie (Sprookjesboom, Klein Duimpje, Zes Zwanen, Sneeuwwitje, Vrouw Holle). Kaart: models/PR_Paden/review/padennet_rand.jpg.
- Studio: MODEL 89495355370457, 322 delen met textuur. Niet op screenshot gecontroleerd. Place nog niet opgeslagen.
- Nog open: het terrein onder de nieuwe aansluitstukjes is niet verlaagd (PadenTerrein liep eenmalig); kan hier en daar door het pad prikken.

### Ronde 3h (15 nov 2026): draaikolken weg, terrein bij de paden
- Daan (screenshot): draaikolk op een Y-kruising. Oorzaak 1: verbredingen die als 'rond' werden herkend kregen ringen; nu worden alle verbredingen recht gelegd langs hun lange as (alleen het oranje rondje heeft eigen ringen). Oorzaak 2: buiten een knik in de middellijn vallen alle punten op hetzelfde hoekpunt (zelfde u -> veeg); nu telt de langs-component altijd mee. Oorzaak 3: brede onregelmatige pleinen; vervormde stukken (verhouding > 2) worden als plein recht gelegd langs de looprichting van het dichtstbijzijnde pad. Resultaat grijs: 0,7% > 1,5, 10 gedegenereerd (was 4% en 124).
- Terrein: ServerStorage.AHN_Delta.PadenTerreinBij (bron tools/studio/paden_terrein_bij.luau). Eerst een voxel-verschuiving (3775 kolommen, niet herhaalbaar door glad terrein), daarna uitsnijden met FillBlock(Air) waar de grond door het pad stak (1318 + 376 plekken) en kieren onder de stoeprand gevuld (266). Grond boven het pad: van 4,4% naar 0,9% van de padpunten.
- Over: Doornroosje (pad door de kasteelheuvel, tot 7,8 stud onder het plateau; er is een geul zichtbaar waar het pad de heuvel in gaat) en Zwavelstokjesstadje (tot 1,8 stud). Daar moet het pad het v1-model volgen of anders lopen (stap 5); niet verder graven.
- Studio: MODEL 84917456870593, 322 delen. Place nog niet opgeslagen.

### Ronde 3i (15 nov 2026): pad over de heuvels, terrein met vaste marge
- Daan koos "pad over de heuvel" bij Doornroosje. tools/heuvels.py: de v1-heuvels (Doornroosje-kasteelheuvel tot ~28 stud, Zwavelstokjes-plateau ~10 stud) gemeten in Studio naast de paden (reference/ahn_sprookjesbos/heuvels_studio.txt), gladgestreken (sigma 6 stud) en als aanvulling op het AHN-veld gebruikt: pad = max(AHN, heuvel) met 9 stud overgang. Binnen de kasteelmuren van Doornroosje geen pad (model heeft een eigen vloer; uitsparing in ref_zones.json). Een variant die steile stukken uitspaarde liet het net uiteenvallen en is teruggedraaid.
- Stoeprand-rokken nu 1,8 stud diep (SKIRT). Terrein: ServerStorage.AHN_Delta.PadenTerreinBij (bron tools/studio/paden_terrein_bij.luau) met vaste marge: grond boven het pad -> weg tot 1,0 onder; grond >2,0 onder -> aanvullen tot 1,2 onder; stoeprand idem met 1,6/1,2. De geul in de Doornroosjeheuvel is weer dicht.
- Meting na 3 rondes: net = 1 geheel, 7 einden (2 rand, 5 attractie). Grond boven het pad 0,68% van de padpunten (43 punten > 0,5 stud), kier onder de stoeprand 16 van 5366, uitgerekte stenen 0,72% (10 gedegenereerd). Rond de 300 plekken blijven per ronde heen en weer gaan (glad terrein); verder draaien heeft geen zin.
- Studio: MODEL 136307310662075, 322 delen. Place nog niet opgeslagen.

## Stap 1c: water (15 nov 2026, klaar voor stap 1)
- Daan: botsrand langs de paden later (bij de scene per attractie, want daar loop je vaak dichter naar de attractie); eerst het water.
- Overzicht: reference/paden/water_park.json (BGT-watervlakken in park-m, 9 binnen de rand). v1-waterdelen per attractie gemeten: wateroppervlak, oeverhoogte, bodem.
- AHN-terrein ligt in een vijver vlak op ongeveer waterhoogte; daardoor drie soorten fouten:
  - water onder de grond (Kleine Zeemeermin, Raponsje, Trollenkoning): terrein binnen de wateromtrek weggegraven tot net onder de VijverBodem van het model -> water en modderbodem weer zichtbaar (Zeemeermin in Studio gecontroleerd).
  - oever lager dan het water (randje waterplaat zweefde): lage oever aangelegd in een ring rond het water tot 0,35 stud boven het water (alleen terrein, waterdelen/kroos niet verplaatst), max 1,2 stud ophogen: Vliegende Fakir 290 cellen, Roodkapje 105, Kabouterdorp 29, Kleine Zeemeermin 28, Zwavelstokjes 24, Kleine Boodschap 22, Draak 20, Pinokkio 20, Chinese Nachtegaal 11, overige < 6.
  - klopt al (rand van het model houdt het water): Langnek, Prinsenpoort, Sprookjesboom, Indische Waterlelies, Zes Zwanen, Raponsje.
- Naar stap 5 (scene per attractie, Daan 15 nov): Kleren van de Keizer (waterplaat zweeft ~1,5 stud boven de grond, video 119:40-123:00 = vijver met fontein in een tuin), Kabouterdorp-beekje (water 4,7, grond deels 2,1), restplekken Klein Duimpje/Pinokkio/Zwavelstokjes (verschil > 1,2 stud). BGT-water zonder water in Studio: Prinsenpoort-gracht (48,84), vijvertje Doornroosje (134,69). Magische Klok bewust droog (Daan: gras). Chinese Nachtegaal (130,199): pad over de koivijver = houten vlonder (video 141:40), later hout.
- Alleen Studio-terrein gewijzigd; place nog niet opgeslagen.

## Stap 3: bomenlaag + zichtrand (15 nov 2026)
- Daan: alle bomen weg, nieuwe in verschillende soorten, slim (weinig bomen kosten), en vanaf geen enkel pad een ander pad zien (behalve begin/eind).
- Bomen uit AHN: tools/bomen_ahn.py (DSM - DTM = boomhoogte, toppen = lokale maxima met venster dat met de hoogte meegroeit, kronen via watershed, minstens 0,28 x hoogte; luchtfoto april: alleen echt donkergroen = naaldboom). reference/bomen/bomen.json + bomen_kaart.jpg. 1.821 bomen, na stam-van-pad/vijver-schuiven 1.803 (300 geschoven, 18 weg).
- Soorten (models/VG_Bomen): beuk, eik, kastanje, berk, den, spar; per soort 1 stam-mesh (schors) + 1 kroon-mesh (dubbelzijdige bladkaarten, alfa), 2.000-3.600 driehoeken. Texturen procedureel (build/01_texturen.py: bladtwijg per soort, schors in de lengte, berk dwarse lenticellen). build/02_bomen.py (Blender, 15 m), review/render_bomen.png. Elke boom = kopie van dezelfde 2 meshes, geschaald op AHN-hoogte/kroonstraal, willekeurig gedraaid (goedkoop: instancing).
- Studio: ServerStorage.BomenVB (12 sjablonen + StringValue Plaatsing/Zichtrand, compact base64), roblox/plaats_bomen.luau -> workspace.SprookjesbosBomen (1.803). 983 oude v1-bomen -> ServerStorage.OudeBomen (attribuut Herkomst). Villa Volta-bomen niet aangeraakt. Bestaande struiken/varens blijven.
- Zichtrand: build/04_zichtrand.py: 2 rijen struiken op 1,9 en 3,2 m achter elke padrand (niet in attractiescenes, niet tussen dicht naast elkaar liggende paden, niet in water) = 2.335 plekken; roblox/plaats_zichtrand.luau slaat een plek over als er al een struik binnen 2 m staat -> 791 nieuwe struiken (BomenBronV3 rododendron/taxus/struik, 2,2-3,2 m) in workspace.SprookjesbosZichtrand.
- Meting (ooghoogte, padpunt naar padpunt 13-65 m, lijn door het bos): buiten het Herautenplein 8 van 746 zichtlijnen vrij (1,1%), alle bij attractiescenes (Magische Klok/Prinsenpoort, Doornroosje, Kogeloog/Langnek, Trollenkoning) -> stap 5. Herautenplein zelf is een open plein met tuinen.
- NOG: in Studio overdag bekijken (alleen avond-screenshots), fps-test in Play, de soortverdeling is benaderd (luchtfoto april onderscheidt loofsoorten niet). Place nog niet opgeslagen.
