# Efteling in Roblox — status en overdracht (12 nov 2026)

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
| Hans en Grietje v1 | 134881477873995 | scriptmatig, afgekeurd als eindniveau; .blend in `models/HansGrietje_wip.blend` |
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

## Villa Volta (v1 in Studio)
`models/AR_VillaVolta/`: blokkering gecorrigeerd op front.jpg (`review/02b/overlay_edges.png`: randen van de render op de foto,
37 px/m, terrasvloer y507). Vormen in `build/03_forms.py` (collectie FORMS, 33 onderdelen, ~33k driehoeken): rustica-hoekblokken,
sokkel, cordonlijst, hoofdgestel met tandlijst, ionische zuilen met voluten, balkon op consoles met balusters en vazen,
opschrift VILLA VOLTA als 3D-tekst, rondboogdeur met glas/roeden, pijlers met vazen, schelp-cartouche, ramen met omlijsting/fronton/oren
(zijgevels inferred), mansardedaken met loodslabben en pinakels, dakkapel met gebogen fronton en cartouche, beeld, terras met trappen,
borstwering en vazen, hal erachter (eenvoudig, inferred).
Export `build/09_export_roblox.py` -> `exports/AR_VillaVolta.fbx` -> **asset 100590688288228**. In Studio als `Workspace.VillaVolta`
(ScaleTo 3, gevel naar noord/−Z, achterkant op OSM y=334 → Z=−1002, midden X=376.8). Materialen per naam MAT_*.
Nog te doen: texturen (stuc met vlekken, leien), lantaarns, hal mooier, interieur (kantelende kamer) later.

## Daarna (volgorde met Daan afgesproken)
1. Villa Volta afmaken. 2. Sprookjesboom + paddenstoelen, Langnek. 3. Lantaarnpaal/bankje/prullenbak. 4. Gijs afmaken.
5. Park terugzetten en mooier (den-lagen, kleinere bladkaarten, gras/bosgrondtexturen, opsluitbanden, oevers). 6. Grote gebouwen (entree, Symbolica).
Kaatsheuvel eromheen: later.

## Geïnstalleerde skills (in ~/.claude/skills)
blender-image-to-3d (kern), blender-cinematic-modeling, blender-core, blender-texturing, blender-texture-baking, blender-asset-qa,
blender-export-pipelines, blender-hardsurface-modeling, blender-retopology-uv, blender-game-optimization, blender-environment-kits,
blender-pipeline-automation, roblox-animation, roblox-texture-gen, roblox-vfx, roblox-3d-model, roblox-skills-setup.
