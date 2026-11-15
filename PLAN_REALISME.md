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

## Volgorde
Fase A → Fase C → Fase B per sprookje → Fase D over het hele bos. Eerste proef: **Klein Duimpje + Monstervis** opnieuw (meeste winst, duidelijkste fouten).

## Usage
Zwaar rekenwerk (downloads, fotogrammetrie, bakes) draait lokaal = bijna geen usage. Duur is plaatjes bekijken:
één verkleind blad per fase. Verwachting: minder rondes (v1..v5) per sprookje, dus per saldo goedkoper.
