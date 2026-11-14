#!/bin/zsh
# upload.sh: modellen decor + omgeving en KD_-texturen (ongewijzigde bestanden houden hun id via de hash)
D=${0:A:h:h}; R=${D:h:h}; cd $R
touch $D/textures/hashes.txt; : > $D/textures/hashes.nieuw; : > $D/textures/asset_ids.nieuw
for deel in stadje; do
  f=$D/exports/MZ_$deel.fbx; h=$(md5 -q $f); oud=$(grep "^MODEL_$deel " $D/textures/hashes.txt | grep " $h\$" | cut -d' ' -f2)
  if [ -n "$oud" ]; then id=$oud; else for poging in 1 2 3; do id=$(tools/upload_asset.sh $f "Zwavelstokjes $deel" "Efteling Het Meisje met de Zwavelstokjes $deel" Model); [ -n "$id" ] && break; sleep 5; done; fi
  [ -z "$id" ] && { echo "UPLOAD MISLUKT $deel" >&2; exit 1; }
  echo "MODEL_$deel $id" >> $D/textures/asset_ids.nieuw; echo "MODEL_$deel $id $h" >> $D/textures/hashes.nieuw
done
for f in $D/textures/MZ_*.png; do
  n=$(basename $f .png); h=$(md5 -q $f); oud=$(grep "^$n " $D/textures/hashes.txt | grep " $h\$" | cut -d' ' -f2)
  if [ -n "$oud" ]; then id=$oud; else for poging in 1 2 3; do id=$(tools/upload_asset.sh $f "$n" 'Efteling Zwavelstokjes textuur' Image); [ -n "$id" ] && break; sleep 5; done; fi
  [ -z "$id" ] && { echo "UPLOAD MISLUKT $n" >&2; exit 1; }
  echo "$n $id" >> $D/textures/asset_ids.nieuw; echo "$n $id $h" >> $D/textures/hashes.nieuw
done
mv $D/textures/hashes.nieuw $D/textures/hashes.txt; mv $D/textures/asset_ids.nieuw $D/textures/asset_ids.txt; cat $D/textures/asset_ids.txt
