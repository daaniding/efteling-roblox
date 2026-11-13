#!/bin/zsh
D=${0:A:h:h}
: > $D/textures/hashes.nieuw
id=$(tools/upload_asset.sh $D/exports/AR_Herberg.fbx 'Herberg De Ersteling' 'Efteling Herberg De Ersteling' Model); echo "MODEL $id" > $D/textures/asset_ids.txt
for f in $D/textures/HB_*.png; do
  n=$(basename $f .png); h=$(md5 -q $f); oud=$(grep "^$n " $D/textures/hashes.txt 2>/dev/null | grep " $h\$" | cut -d' ' -f2)
  if [ -n "$oud" ]; then id=$oud; else id=$(tools/upload_asset.sh $f "$n" 'Efteling Herberg textuur' Image); fi
  echo "$n $id" >> $D/textures/asset_ids.txt; echo "$n $id $h" >> $D/textures/hashes.nieuw
done
mv $D/textures/hashes.nieuw $D/textures/hashes.txt
cat $D/textures/asset_ids.txt
