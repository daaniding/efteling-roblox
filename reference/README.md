# Efteling referentiemap voor Roblox/Blender

## Plattegronden (`plattegrond/`)
| Bestand | Wat | Schaal |
|---|---|---|
| `Efteling_op_schaal_OSM_4px_per_m.png` | Eigen render uit OpenStreetMap: gebouwen, attracties (oranje), water, paden, met namen en 100 m-raster | **4 px = 1 m**, oorsprong (0,0) = midden park |
| `OSM_tegels_Efteling_z17.png` | Standaard OSM-kaart met straatnamen, paden en alle attractienamen | 0,741 m per px |
| `Efteling-Map-2025.png` / `.pdf` | Officiële getekende parkkaart 2025 (sfeer, niet op schaal) | n.v.t. |

## Data (`data/`)
- `efteling_objecten_meters.csv` — 851 objecten met naam, type, centrum, breedte × diepte in meters. **Dit is je maatvoering.**
- `efteling_objecten_meters.json` — zelfde, plus alle hoekpunten van elke footprint.
- `efteling_footprints.obj` — alle footprints als platte vlakken, 1 unit = 1 m. Blender: File > Import > Wavefront OBJ, zet **Forward = Y, Up = Z**. Dan heb je het hele park als blauwdruk onder je model.
- `plaats_markers_roblox.luau` — zet 315 gelabelde placeholder-parts op de juiste plek in Studio. `SCALE = 1` is 1 stud per meter; zet op 3 voor normale personageschaal.
- `efteling_osm.xml` — ruwe OpenStreetMap-data (ODbL, bron vermelden).

Assenstelsel: x = oost, y = noord, in meters. Roblox: `X = x`, `Z = -y`.

## Schaal in Roblox
- Een Roblox-personage is ~5 studs; een mens is ~1,75 m. **3 studs per meter** voelt realistisch.
- Park zonder parkeerplaats is ongeveer 1 100 m × 900 m = **3 300 × 2 700 studs**. Dat past in één place. Streamingenabled aanzetten.
- Bij 1 stud = 1 m wordt alles te klein voor het personage, maar het is handig voor de eerste blokkering.

## Belangrijkste maten (bron: OSM-footprints + nl.wikipedia)
| Attractie | Footprint (b × d) | Hoogte / baan |
|---|---|---|
| Baron 1898 | centrum (370, -194) | 30 m hoog, val 37,5 m (7,5 m ondergronds), baan 501 m, 90 km/h |
| Python | centrum (555, -352) | 29 m hoog, baan 750 m, 2 loops + 2 kurkentrekkers |
| Joris en de Draak | centrum (479, -348) | 25 m hoog, 2 × 810 m baan, draak 9 m |
| Vogel Rok | 62 × 102 m | gebouw, baan ~415 m binnen |
| De Vliegende Hollander | gebouw 42 × 70 m | ca. 22 m hoog |
| Max & Moritz | centrum (130, -213) | 2 × 360 m, ca. 7 m hoog |
| Pagode | 17 m doorsnede | 45 m hoog, tempel 16 m doorsnede |
| Symbolica | centrum (327, 8) | hoogste toren 29,8 m |
| Huis van de Vijf Zintuigen | 62 × 47 m | ~43 m hoog, rieten dak 4 500 m² |
| Droomvlucht | 81 × 61 m | gebouw |
| Carnaval Festival | 87 × 59 m | gebouw |
| Fata Morgana | centrum (-29, -321) | gebouw |
| Aquanura | vijver 113 × 112 m | fonteinen |
| Piraña | 200 × 135 m parcours | |
| Carrouselpaleis | 90 × 71 m | |
| Raveleijn | 96 × 75 m | |
| Villa Volta | 18,5 × 33,5 m | |
| Volk van Laaf | 120 × 91 m | |
| Danse Macabre | centrum (207, -138) | gebied 17 000 m² |

Hoogtes van de meeste gebouwen staan niet in OSM. Schat ze van de foto's met een mens (1,75 m) of een deur (2,1 m) als maatstaf.

## Foto's (`fotos/`)
Per attractie een map met 4 foto's van Wikimedia Commons. Licenties en auteurs staan in `fotos/BRONNEN.txt`. Mapnaam = Commons-categorie.

## Bronnen
OpenStreetMap-contributors (ODbL), nl.wikipedia.org, themeparkbrochures.net (kaart 2025), Wikimedia Commons.
