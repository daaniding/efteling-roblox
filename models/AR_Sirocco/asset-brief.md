# AR_Sirocco — asset-brief (17 nov 2026)

Daan: "doe maar Monsieur Cannibale" -> die bestaat sinds 2021 niet meer; op dezelfde plek staat Sirocco (opening 26 jan 2022,
technisch dezelfde rit, gebouw van 1988). Daan koos: "Ja, Sirocco + foto's", daarna "en natuurlijk de video's" en
"zoek ook nog blueprints".

```text
ASSET      AR_Sirocco — draaimolen met 12 handelsscheepjes (teacup, MACK Rides) onder een rond rieten dak, op een eiland
CATEGORY   architecture (gebouw + draaischijf) + props (12 boten, handelswaar, hangende schalen) + scène (water, wachtrij, haven)
VIEWS      ref/eftepedia/Sirocco_doorsnede.jpg: doorsnede B-B, vrijwel orthografisch (ontwerptekening), maatlijnen onleesbaar
           ref/luchtfoto/luchtfoto.jpg: PDOK 7,5 cm, noord boven, 1 px = 5 cm (tools/uitsnede.py, midden 455,188, r 35)
           ref/eftepedia_mc/Wolmonsieurcannibale.jpg: bovenaanzicht draaischijf (indeling boten)
           ref/eftepedia_mc/Cannibale_bouw1/2.jpg: stalen frame draaischijf; Monsieur_Cannibale_dakloos + Monsieurdakbedekking:
           dakconstructie zonder riet; overige foto's en 6 video's (ref/video/frames, elke 2 s) voor detail
SCALE      draaischijf 14 m doorsnede (lemma) = 850 px op de doorsnede -> 60,7 px/m
           dak 17,7 m doorsnede (luchtfoto, 1 m = 20 px); doorsnede-tekening totaal ~18,5 m tussen buitenste maatlijnen
PROPORTIONS (doorsnede, t.o.v. waterlijn/platform)
           nok ~11,6 m; dakrand achter ~3,0 m; dakvleugel voorkant krult op tot ~7,4 m; 5 rijen staanders zichtbaar
           (buitenring + ring op de draaischijfrand + middenpaal); platform ligt op waterpeil, kelder eronder
PLACE      dakmidden park (456,5; 191,2) m (luchtfoto; OSM-dak 1004958316 ligt ~4 m verschoven) -> Roblox (1369,5; -573,6)
           voorkant (opengekrulde dakvleugel, steiger/uitgangsbrug) naar het ZZW (~-124 gr parkhoek), haven met Sindbads boot
           daarvoor; plein met beeld Sindbad (461,4;194,7) en springfontein (462,9;181,4) (OSM); maaiveld NAP 8,3-8,7 (AHN)
PARTS      1 gebouw: houten staanders + kapconstructie (spanten, ringbalk), rieten kegeldak met opgekrulde vleugel voorzijde,
             open zijkanten, reling rond het platform (vast)
           2 draaischijf 14 m (draait), 3 kleine schijven met elk 3 boten (draaien tegen in), 3 losse boten op de grote schijf,
             ton in het midden ("dobbert in de woelige baren")
           3 12 identieke handelsscheepjes: houtsnijwerk buitenkant (blauw/rood/goud), bakje handelswaar achterop (sinaasappels,
             flessen), deurtje; draaien aan een stuurwiel (in het echt draaien de bezoekers zelf)
           4 kap-interieur: tientallen hangende schalen/netten met handelswaar, lampen, handelaar aan een touwladder in het midden
           5 scène: waterring om het eiland, meerpalen, boeien (geel/blauw), steiger/uitgangsbrug, wachtrij-vlonder met turquoise
             zeiloverkapping (oostkant, buigt mee met de draaischijf), controlehokje links naast de ingang, ingang gedeeld met
             Archipel, lampen in de wachtrij (Wachtrij-sirocco-lamp.jpg), Sindbads zeilboot in de haven
SILHOUETTE rond rieten puntdak met naar voren opgekrulde vleugel; open onderbouw met houten palen; water rondom; turquoise zeilkap
MATERIALS  riet (grijsbruin, verweerd), donker hout (staanders, spanten), bamboe/touw (relingen, wachtrij), turquoise zeil,
           blauw platform met golfpatroon, boten: blauw/rood geschilderd snijwerk met gouden krullen
ARTICULATION draaischijf + 3 subschijven + 12 boten (later; NIET animeren tot Daan erom vraagt)
INFERRED   hoogtes van de kapconstructie binnen (uit doorsnede + video), dikte riet (~0,4 m), aantal staanders (uit dakloos-foto
           en video tellen), kelder/fundering (niet zichtbaar, niet bouwen)
TARGET     Roblox, FBX, per deel een asset (gebouw / draaischijf+boten / scène), schaal 3 stud/m, eerste persoon
```

## Volgorde (WERKWIJZE)
1. Brief (dit) + plan op de luchtfoto (`build/01_plan.py`), alles in parkmeters.
2. Blockout gebouw + draaischijf in Blender (`build/02_blockout.py`), overlay op doorsnede en luchtfoto (gate).
3. Vormen, boten, kap-interieur; texturen; export; plaatsen; looptest.
4. Wachtrij, water, haven; bezoekers (Park.registreer, VOLGORDE na de Pagode).
