#!/usr/bin/env zsh
# Upload Pagode-modellen en -texturen naar Roblox; schrijft models/AR_Pagode/exports/asset_ids.json. Draai vanuit de repo-root.
set -e
D=models/AR_Pagode
typeset -A IDS
for m in AR_Pagode_gondel AR_Pagode_station; do
  IDS[$m]=$(tools/upload_asset.sh $D/exports/$m.fbx "$m" "Efteling De Pagode ($m)" Model | tail -1)
  echo "$m ${IDS[$m]}"
done
for t in pannen sierveld windveer trommel sierrand kernwand arm natuursteen vlonder klinker; do
  for k in kleur normaal; do
    IDS[${t}_$k]=$(tools/upload_asset.sh $D/textures/PG_${t}_$k.png "PG_${t}_$k" "Efteling Pagode textuur" Image | tail -1)
    echo "${t}_$k ${IDS[${t}_$k]}"
  done
done
IDS[bord_kleur]=$(tools/upload_asset.sh $D/textures/PG_bord_kleur.png "PG_bord_kleur" "Efteling Pagode bord" Image | tail -1)
echo "bord_kleur ${IDS[bord_kleur]}"
for k v in ${(kv)IDS}; do echo "$k $v"; done | python3 -c "import json,sys; json.dump({l.split()[0]: int(l.split()[1]) for l in sys.stdin if l.strip()}, open('$D/exports/asset_ids.json','w'), indent=1)"
