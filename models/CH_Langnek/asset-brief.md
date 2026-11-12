ASSET      CH_Langnek (Langnek uit De Zes Dienaren, Sprookjesbos): reus zittend op een kunstrots, nek schuift als geheel omhoog uit de kraag. Plus scène direct eromheen: rots, halve-maanvijver met natuurstenen rand, kronkelend hekje, beplanting.
CATEGORY   character (biped, zittend, statische pose) + environment (kunstrots, vijver)
VIEWS      ref/front.jpg = Eftepedia "Langnek2013.jpg" 1000x1333: perspectief vanaf het plein, azimut ~0 (recht van voren), elevatie ~ +5 (ooghoogte 1.6 m, horizon op py 615 van 900), lens ~28 mm (telefoon). Onderwerp vult 0.75 van de beeldhoogte; nek volledig uit.
           ref/top_front.jpg = Eftepedia "Langnek_overview2014.jpg": van schuin boven (~35 graden), toont vijver (halve maan) + rots + pose; alleen silhouet/opbouw.
           eftepedia/Winterlangnek.jpg, Langnekaugustus1998.jpg: zelfde pose, andere jaren; detail kleding/hoofd.
           eftepedia/Langnek_technisch_ontwerp.jpg: doorsnede nekmechaniek (nek zakt in een geleidebuis door lichaam en rots), alleen principe.
           ref/osm_lokaal.json: rots- en watercontour (OSM, meters t.o.v. het Langnek-punt).
SCALE      Horizon-methode: horizon = 1.6 m ooghoogte (py 615). Op het vlak van de figuur 55 px/m (rotsvoet py 705 -> (705-615)/1.6 = 56). Controle: zichtbare nek 270 px = 4.9 m, Eftepedia noemt een nek van 4.8 m -> klopt. Rots uit OSM: 9.2 m (O-W) x 8.6 m (N-Z).
PROPORTIONS (meters boven het pleinmaaiveld, z=0)
           zitvlak z 2.90 | voetrichels z 1.70 | riem z 4.05 | onderrand cape z 4.70 | schouders (cape) z 5.55, breedte 2.40 | kraagtop z 5.85, kraag-diameter 0.75
           nek diameter 0.38, zichtbare lengte uit 4.90, in-stand 0.35 (slag 4.55) | hoofd hoogte 1.22, breedte 1.05 (1.32 met oren), kaal, eivorm smal onder
           knieën x +-2.25 z 3.35 (wijdbeens) | voeten x +-1.85, laars lang 1.00 | handen x +-2.10 z 2.95, plat op de rots naast/achter de heupen
           tuniek-rok valt tussen de dijen tot z 2.95 | mouwen geel, schouder->hand
           hoofdtop (nek uit) z 12.0; hoofdtop (nek in) z 7.45
PARTS      1 GEO_rots (kunstrots, gelaagde platen, zitplateau achter, voetrichels voor) — statisch
           2 GEO_vijverrand (platte natuurstenen, halve maan) + GEO_water (donker, troebel) — statisch
           3 GEO_hekje (kronkelend, donkergroen smeedijzer, 0.8 m, langs de buitenrand van de vijver) — statisch
           4 lichaam (gefuseerd: romp + dijen + onderbenen) broek groenblauw — statisch
           5 tuniek (mosterdgeel, rok met plooien, riem bruin + gesp), mouwen geel, handen huid — statisch
           6 cape rood met hoge opstaande kraag + touwknoop (beige touw) — statisch
           7 laarzen rood met veters, puntneus — statisch
           8 NEK (huidkleur, recht, rigide) — beweegt verticaal (slag 4.55 m), pivot = kraagcentrum
           9 HOOFD: schedel + kaak (gefuseerd), neus groot, oren groot, ogen (wit + bruine iris + pupil, apart), oogleden, wenkbrauwen, plukken donker haar opzij, mond met hangende hoeken — draait om de nekas (yaw +-40), ogen bewegen apart (yaw +-20)
SILHOUETTE extreem lange dunne nek met klein kaal hoofd erop; rode cape-schouders met kraag; wijde knieën met rode puntlaarzen; brede grijze rots; vijver als donkere halve maan ervoor
MATERIALS  huid perzik-oranje (0.86,0.58,0.42) ruw 0.45 | tuniek mosterdgeel (0.85,0.65,0.18) ruw 0.6 | broek groenblauw (0.18,0.36,0.38) ruw 0.5 | cape rood (0.66,0.16,0.10) ruw 0.5 | laarzen rood (0.70,0.18,0.12) ruw 0.4 | riem bruin (0.32,0.18,0.08) | touw beige (0.80,0.70,0.50) | haar donkerbruin (0.15,0.10,0.07) | ogen wit, iris bruin (0.35,0.18,0.06) | rots koel grijs (0.48,0.50,0.50) ruw 0.9 met donkere voegen en lichte randen | water donker troebel groenbruin | hek donkergroen (0.10,0.18,0.12) metaal 0.6
ARTICULATION geen skelet; drie rigide delen voor script-animatie in Roblox: NEK (verticaal), HOOFD (yaw + verticaal met nek), OGEN (yaw). Groepering via anim-tag (neck / head / eyes / body / static).
INFERRED   achterkant van figuur en cape (symmetrie + stof naar beneden); achterkant rots (OSM-contour, hoogte aflopend); diepte-maten van romp (0.9 m); exacte nekslag (afgeleid 4.55 m); hekje-vorm (kronkelend volgens Eftepedia-tekst, foto toont lage stenen rand); beplanting achter (naaldbomen, rododendron, bamboe uit foto's).
TARGET     Roblox, FBX (1 unit = 1 m, in Studio ScaleTo(3)), hero-figuur <= 40k tris, scène <= 40k tris; 3e-persoonscamera; figuur ~350 px hoog op scherm vanaf het plein.
           Plaatsing: OSM-punt (145.91, -33.66) m -> Roblox (437.7, 2, 101.0). Gezicht kijkt naar ZZO (OSM-richting (0.6, -0.8)), over de vijver naar het plein / Kogeloog.
