#!/bin/zsh
D=${0:A:h:h}; R=${D:h:h}; cd $R
touch $D/textures/hashes.txt; : > $D/textures/hashes.nieuw; : > $D/textures/asset_ids.nieuw
f=$D/exports/CN_nachtegaal.fbx; h=$(md5 -q $f); oud=$(grep "^MODEL_nachtegaal " $D/textures/hashes.txt | grep " $h\$" | cut -d' ' -f2)
if [ -n "$oud" ]; then id=$oud; else for p in 1 2 3; do id=$(tools/upload_asset.sh $f "Chinese Nachtegaal" "Efteling De Chinese Nachtegaal paleis 1999" Model); [ -n "$id" ] && break; sleep 5; done; fi
[ -z "$id" ] && { echo "UPLOAD MISLUKT model" >&2; exit 1; }
echo "MODEL_nachtegaal $id" >> $D/textures/asset_ids.nieuw; echo "MODEL_nachtegaal $id $h" >> $D/textures/hashes.nieuw
for f in $D/textures/CN_*.png; do
  n=$(basename $f .png); h=$(md5 -q $f); oud=$(grep "^$n " $D/textures/hashes.txt | grep " $h\$" | cut -d' ' -f2)
  if [ -n "$oud" ]; then id=$oud; else for p in 1 2 3; do id=$(tools/upload_asset.sh $f "$n" 'Efteling Chinese Nachtegaal textuur' Image); [ -n "$id" ] && break; sleep 5; done; fi
  [ -z "$id" ] && { echo "UPLOAD MISLUKT $n" >&2; exit 1; }
  echo "$n $id" >> $D/textures/asset_ids.nieuw; echo "$n $id $h" >> $D/textures/hashes.nieuw
done
mv $D/textures/hashes.nieuw $D/textures/hashes.txt; mv $D/textures/asset_ids.nieuw $D/textures/asset_ids.txt; cat $D/textures/asset_ids.txt
