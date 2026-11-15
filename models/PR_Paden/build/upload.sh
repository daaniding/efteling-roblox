#!/bin/zsh
# upload.sh: PD_paden.fbx + PD_-texturen naar Roblox (ongewijzigde bestanden houden hun id via de hash)
D=${0:A:h:h}; R=${D:h:h}; cd $R
touch $D/textures/hashes.txt; : > $D/textures/hashes.nieuw; : > $D/textures/asset_ids.nieuw
f=$D/exports/PD_paden.fbx; h=$(md5 -q $f); oud=$(grep "^MODEL_paden " $D/textures/hashes.txt | grep " $h\$" | cut -d' ' -f2)
if [ -n "$oud" ]; then id=$oud; else for poging in 1 2 3; do id=$(tools/upload_asset.sh $f "Efteling paden Sprookjesbos" "Efteling Sprookjesbos paden (BGT, AHN)" Model); [ -n "$id" ] && break; sleep 5; done; fi
[ -z "$id" ] && { echo "UPLOAD MISLUKT model" >&2; exit 1; }
echo "MODEL_paden $id" >> $D/textures/asset_ids.nieuw; echo "MODEL_paden $id $h" >> $D/textures/hashes.nieuw
for f in $D/textures/PD_*.png; do
  n=$(basename $f .png); h=$(md5 -q $f); oud=$(grep "^$n " $D/textures/hashes.txt | grep " $h\$" | cut -d' ' -f2)
  if [ -n "$oud" ]; then id=$oud; else for poging in 1 2 3; do id=$(tools/upload_asset.sh $f "$n" 'Efteling paden textuur' Image); [ -n "$id" ] && break; sleep 5; done; fi
  [ -z "$id" ] && { echo "UPLOAD MISLUKT $n" >&2; exit 1; }
  echo "$n $id" >> $D/textures/asset_ids.nieuw; echo "$n $id $h" >> $D/textures/hashes.nieuw
done
mv $D/textures/hashes.nieuw $D/textures/hashes.txt; mv $D/textures/asset_ids.nieuw $D/textures/asset_ids.txt; cat $D/textures/asset_ids.txt
