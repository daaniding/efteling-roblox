---
name: efteling-sprookje
description: Werkwijze om een stuk van de Efteling (Sprookjesbos-sprookje, figuur, pad, bos of scène) 1-op-1 en realistisch in de Roblox-game (place 126519985893990, repo daaniding/efteling-roblox) te bouwen. Gebruik bij elke bouw- of verbeterstap in de Efteling Roblox game, ook als alleen "maak X echter", "pad", "bos", "scène", "figuur", "reus", "Monstervis" of een sprookjesnaam genoemd wordt.
---

# Efteling 1-op-1 (Sprookjesbos)

Lees EERST in de repo: `WERKWIJZE.md` (lessen + techniek), `STATUS.md` (wat staat waar), `PLAN_REALISME.md` (het plan,
met BOUWVOLGORDE onderaan). Deze skill is de korte versie; bij twijfel wint WERKWIJZE.md/Daan.

## Harde afspraken (Daan)
- Volgorde: eerst ALLES buiten (terrein, paden, bos, water, scène), dan attracties 1-op-1, dan interieurs, dan leven/geluid.
- Alleen bouwen wat gevraagd is. Bij twijfel over omvang of interpretatie: eerst de 2 opties voorleggen.
- Nog NIET animeren. Geen NPC-bezoekers, geen first-person, geen zwevende tekst.
- Lighting.Technology zet Daan zelf. Downloads/installaties (yt-dlp, ffmpeg, ...) pas na toestemming.
- Na elke afgeronde stap: STATUS.md (+ WERKWIJZE.md bij een les) bijwerken, committen, pushen.
- Figuren/gebouwen via Blender (modelleren naar echte foto's, MeshParts). Nooit losse Studio-parts, nooit code-boetseren
  (klei), nooit Roblox generate_mesh voor figuren (chibi), nooit een ontwerpschets als hoofdreferentie.
- Geluid: echte Efteling-geluiden mag (besluit Daan), met `audio/BRON.txt` en een reserve per geluid; pas als het park staat.

## Coördinaten
Parkmeters x = oost, y = noord, oorsprong 51.6500 N / 5.0455 E. Roblox X = 3x, Z = -3y (3 studs = 1 m).
`tools/geo.py` (park <-> RD <-> WGS <-> studs). Maaiveld-NAP per plek: `reference/ahn_sprookjesbos/` (DTM/DSM 0,5 m).

## Zeven stappen per onderdeel (elke stap een keuring met beeld, niet met woorden)
1. **Verzamelen**: `python3 tools/uitsnede.py <naam> studs <X> <Z> [straal]` -> luchtfoto 5 cm/px, hoogte, OSM-overlay.
   Plus alle Eftepedia + Commons (+ videoframes zodra yt-dlp/ffmpeg mag). Hoofdreferentie = echte foto, liefst recent.
   Daan ziet één overzichtsblad.
2. **Elementenlijst** per foto: grond, randen, keien, planten per soort, water, hekjes, bordjes, lantaarns, figuur,
   zicht vanaf het pad. Alles op de lijst moet terugkomen.
3. **Plattegrond op de cm**: luchtfoto overtrekken (niet de grove OSM-lijn), AHN-hoogte erbij.
   Keuring: bovenaanzicht over de luchtfoto.
4. **3D**: gebouwen uit foto-maten (deur 3 m, horizon-methode, solve_cam) + BAG/OSM; figuren via de figuren-pijplijn
   (PLAN_REALISME.md: fotogrammetrie of multi-view image-to-3D uit echte foto's -> passen op 3-5 fotocamera's tot
   >95% silhouet-overlap -> strakke plooien -> foto-projectie). Keuring: overlay op elke foto + close-ups gezicht/handen.
5. **Materiaal**: 4 PBR-kaarten (SurfaceAppearance), CC0-scans (Poly Haven/ambientCG) i.p.v. procedureel, slijtage,
   grondcontact, polyester figuren satijnglans (roughness 0,35-0,45). Keuring: kleur/helderheid gemeten tegen de foto.
6. **Scène**: drie lagen (detail langs het pad / plantenwand / alleen kruinen), onzichtbare botsrand, licht, water.
   Natuur alleen waar je hem ziet (96% van het Sprookjesbos ligt binnen 20 m van een pad).
7. **Wandeltest**: dezelfde route als een YouTube-wandelvideo, frames naast elkaar, plus fps-test in Play.

## Kits (één keer goed, overal hergebruiken; elk door de kwaliteitslat)
Grond (gras, bosbodem, modder, blad), padranden/keien, verharding (klinkers, grind), straatmeubilair (lantaarn, bank,
"Papier hier"-bak, hekjes, bordjes), water (oevers, riet, kroos, rimpels), natuur (boomsoorten, struiken, plantenwanden,
stenen), licht-preset. Bestaande `BomenBronV3`/oude planten zijn NIET goed genoeg: vervangen door Blender-kit.

## Prestaties
Instancing (zelfde MeshId + SurfaceAppearance), alpha-cutout blad, CastShadow uit op klein spul, CollisionFidelity Box
+ COLL_-blokken, client-afstandsculling, ≤ ~20k driehoeken per mesh, alleen bomen in de zichtzone volledig.
