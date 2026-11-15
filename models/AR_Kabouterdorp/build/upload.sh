#!/bin/zsh
D=${0:A:h:h}; R=${D:h:h}; cd $R
touch $D/textures/hashes.txt; : > $D/textures/hashes.nieuw; : > $D/textures/asset_ids.nieuw
f=$D/exports/KD_kabouterdorp.fbx; h=$(md5 -q $f); oud=$(grep "^MODEL_kabouterdorp " $D/textures/hashes.txt | grep " $h\$" | cut -d' ' -f2)
if [ -n "$oud" ]; then id=$oud; else for p in 1 2 3; do id=$(tools/upload_asset.sh $f "Kabouterdorp" "Efteling Het Kabouterdorp" Model); [ -n "$id" ] && break; sleep 5; done; fi
[ -z "$id" ] && { echo "UPLOAD MISLUKT model" >&2; exit 1; }
echo "MODEL_kabouterdorp $id" >> $D/textures/asset_ids.nieuw; echo "MODEL_kabouterdorp $id $h" >> $D/textures/hashes.nieuw
for f in $D/textures/KD_*.png; do
  n=$(basename $f .png); h=$(md5 -q $f); oud=$(grep "^$n " $D/textures/hashes.txt | grep " $h\$" | cut -d' ' -f2)
  if [ -n "$oud" ]; then id=$oud; else for p in 1 2 3; do id=$(tools/upload_asset.sh $f "$n" 'Efteling Kabouterdorp textuur' Image); [ -n "$id" ] && break; sleep 5; done; fi
  [ -z "$id" ] && { echo "UPLOAD MISLUKT $n" >&2; exit 1; }
  echo "$n $id" >> $D/textures/asset_ids.nieuw; echo "$n $id $h" >> $D/textures/hashes.nieuw
done
mv $D/textures/hashes.nieuw $D/textures/hashes.txt; mv $D/textures/asset_ids.nieuw $D/textures/asset_ids.txt; cat $D/textures/asset_ids.txt
