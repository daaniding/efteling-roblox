# De Magische Klok — asset-brief

Bronnen: 56 Eftepedia-plaatjes (`ref/eftepedia/`, contactbladen `review/contact_*.jpg`), lemma-tekst (`ref/lemma.html`),
OSM 55424253 (L-vormig: toren + twee muurarmen), Prinsenpoort 967458492, paden (`ref/osm_lokaal.json`, `build/01_osm_lokaal.py`).
Primaire foto `ref/front.jpg` = Boekloc_MagischeKlok.jpg (2016, recht voor de toren). Kale bouwfoto: Herauttechniek_2023.jpg.
Daan (13 nov): Herautenplein (grind, bankjes, galgenlantaarn, hagen) komt LATER; herauten NU in Blender maken.

## Modelframe
Meters, Z op, z=0 = maaiveld voor de muren. Oorsprong = midden klokkentoren = OSM-lokaal (4.2, -2.3) t.o.v. het footprint-midden
= OSM-park (56.44, 53.25) m = studs (169.32, -159.75), grond Y=2.
Klok kijkt naar -Y = OSM (-0.855, 0.518) (WNW, bissectrice van de L, naar het plein). +X = OSM (-0.518, -0.855) (ZZW), +Y = OSM (0.855, -0.518).
Roblox-kijkrichting van de klok = (-0.855, 0, -0.518).
- Muurarm N (links, naar de Prinsenpoort): binnenvlak van (-1.33, -2.96) richting (-0.700, -0.715), ~14.4 m. Plein-normaal (0.715, -0.700).
- Muurarm W (rechts, naar een kleiner torentje): binnenvlak van (0.96, -3.07) richting (0.699, -0.715), ~17.2 m. Plein-normaal (-0.715, -0.699).
- Binnenhoek (snijpunt binnenvlakken) (-0.24, -1.84); binnenvlakken liggen 1.12 m van het torenmidden -> de toren steekt ~1 m voor de muren uit.
- OSM-footprint is van boven getekend: dakrand toren r 2.5; muren 2 m dik incl. klimop en de gang erachter (Trekkabels_2023).

## Maten (m) — front.jpg op dakdiepte 44 px/m (dak 220 px = 5.0 m)
- Toren: bakstenen romp r 2.08 tot 3.35 (bovenste rollaag uitgekraagd); ruiterband 3.35..3.95 (smallere grijze kern r 1.75, 8 dunne
  ijzeren staanders, 8 ruitertjes: wit paard met rood-wit gestreept dekkleed, ridder met lans).
  Dak (leien/houten schijfjes, grijsbruin) dakvoet r 2.55 op 3.95 tot r 0.72 op 5.9, licht bolle klok-vorm.
  Twee loden trommels (r 0.72 / 0.6, 5.9..6.3), klokkenstoel met 4 krulstijlen 6.3..7.0, brons klokje, Slimme Toon (zit op een krul,
  groen jak, rode broek, muts met veer), rood pannen kegeldakje r 0.55 7.0..7.55, gouden bol + windvaan tot ~7.9.
- Uurwerk: vierkant, 1.5 breed x 1.45 hoog, midden op 2.5, Piecksblauw (groenblauw) met witte Romeinse cijfers, rode bloempjes in de stijlen,
  gouden wijzers, kroonlijstje erboven. Kijkt naar -Y. Achterkant: groene rondboogdeur (Achterdeklok.jpg).
- Muren: stuc (zand/grijs, verweerd, veel klimop), 0.5 dik, 2.8 hoog, kantelen 0.6 breed / 0.5 gat / 0.5 hoog; lisenen 0.7 breed bij elke
  heraut (tot kantelhoogte). Op de bouwfoto 2023: beige stuc, kantelen op het hele bovenvlak.
- Slotgrachtje voor de muren: bodem -0.4, water -0.15, 1.3 breed, 1.0..2.3 voor het binnenvlak (Herauten-okt2009 / overzicht-okt2009).
- Herauten (6, drie per arm): ~2.0 m (blond, zwart hoedje met grote rode veer, rode maillot, zwarte schoenen, zwart-goud gestreepte rok
  met riem, rode mouwen, witte kraag, medaillon met Brabantse leeuw, trompet met vaandel, andere hand in de zij). Op bakstenen sokkel
  0.7 x 0.7 x 0.35 + steenplaat 0.08, tegen de muur. Achter elke heraut een rood schildje met Franse lelie (luidspreker).
  Posities langs elke arm op ~3.2 / 6.0 / 8.8 m van de binnenhoek.
- Voorgrond (front.jpg): gebogen laag muurtje van baksteen met grove natuursteen-afdekking (h ~0.55) om een klinkerhalfrond,
  sprookjesboek op standaard ervoor. Tussen muurtje en muren: bodembedekkers, varens, klimop.

## Conflicten / aannames
- Bouwfoto 2023 (beige, kaal) vs 2016 (grijs met klimop): 2016-look met klimop aangehouden (= huidige stand na het terugplanten).
- Kleiner torentje aan het eind van arm W: geen bruikbare foto -> muur eindigt met een pijler (later aanvullen).
