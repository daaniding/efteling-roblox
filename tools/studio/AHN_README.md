# AHN-terrein in Studio (15 nov, keuze B: echte hoogte)

Staat in Studio onder `ServerStorage.AHN_Delta`:
- `rle` (StringValue): het verschuivingsveld, 8-stud-raster vanaf X0=-280, Z0=-796, 117 x 145 punten.
  Zelfde inhoud als `reference/ahn_sprookjesbos/delta_8studs_rle.txt`. Codering: per rij (Z), `!` + 2 tekens waarde + 1 teken
  aantal (herhaling), anders 1 teken = verschil + 32; base64-alfabet; waarde 500 = 0; eenheid 0,1 stud.
- `Veld` (ModuleScript): `dy(X, Z)` in studs (bilineair). Gebruik dit voor ALLES wat je later neerzet: `Y = 2 + Veld.dy(X, Z)`
  is het maaiveld (was overal Y=2).
- `Schuif` (ModuleScript): verschuift terreinkolommen (occupancy lineair verschoven; vijvers en uitgravingen schuiven mee).
  Gemeten: oppervlak = bovenkant laatste volle voxel + 2 + 4*occupancy van de voxel erboven.
- `Objecten` (ModuleScript): kleine v1-modellen als geheel (plateau per cluster), grote v1-modellen per onderdeel (mediaan
  over het voetvlak), bomen/planten per stuk op hun eigen plek. Elk verschoven object heeft attribuut `AHN_dY`.
- `Terugdraaien` (ModuleScript): zet terrein terug uit `ServerStorage.Backup_Terrein_voor_AHN_15nov` en alle objecten met `AHN_dY`.

Het veld wordt gemaakt door `tools/hoogteveld.py` (AHN4 DTM 0,5 m, gaten opgevuld, sigma 1,5 m, referentie NAP 8,89 m = Y 2,
uitlopend naar 0 op 30 m buiten het Sprookjesbos). Max +12,4 studs (Doornroosje-heuvel), min -6,6.
Studio mag niet van GitHub downloaden (Assistant-HTTP-allowlist): data als gecomprimeerde string in de code plakken (~16 KB).
