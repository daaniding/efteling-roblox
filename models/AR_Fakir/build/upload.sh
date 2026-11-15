#!/bin/zsh
D=${0:A:h:h}; R=${D:h:h}; cd $R
touch $D/textures/hashes.txt; : > $D/textures/hashes.nieuw; : > $D/textures/asset_ids.nieuw
f=$D/exports/FK_fakir.fbx; h=$(md5 -q $f); oud=$(grep "^MODEL_fakir " $D/textures/hashes.txt | grep " $h\$" | cut -d' ' -f2)
if [ -n "$oud" ]; then id=$oud; else for p in 1 2 3; do id=$(tools/upload_asset.sh $f "Vliegende Fakir" "Efteling De Vliegende Fakir paleis" Model); [ -n "$id" ] && break; sleep 5; done; fi
[ -z "$id" ] && { echo "UPLOAD MISLUKT model" >&2; exit 1; }
echo "MODEL_fakir $id" >> $D/textures/asset_ids.nieuw; echo "MODEL_fakir $id $h" >> $D/textures/hashes.nieuw
for f in $D/textures/FK_*.png; do
  n=$(basename $f .png); h=$(md5 -q $f); oud=$(grep "^$n " $D/textures/hashes.txt | grep " $h\$" | cut -d' ' -f2)
  if [ -n "$oud" ]; then id=$oud; else for p in 1 2 3; do id=$(tools/upload_asset.sh $f "$n" 'Efteling Vliegende Fakir textuur' Image); [ -n "$id" ] && break; sleep 5; done; fi
  [ -z "$id" ] && { echo "UPLOAD MISLUKT $n" >&2; exit 1; }
  echo "$n $id" >> $D/textures/asset_ids.nieuw; echo "$n $id $h" >> $D/textures/hashes.nieuw
done
mv $D/textures/hashes.nieuw $D/textures/hashes.txt; mv $D/textures/asset_ids.nieuw $D/textures/asset_ids.txt; cat $D/textures/asset_ids.txt
