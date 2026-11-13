#!/bin/zsh
# upload.sh: model + texturen naar Roblox (ongewijzigde texturen houden hun id via textures/hashes.txt). Draaien vanuit de repo-root via zsh -ic.
D=${0:A:h:h}
: > $D/textures/hashes.nieuw
id=$(tools/upload_asset.sh $D/exports/AR_Prinsenpoort.fbx 'Prinsenpoort' 'Efteling Prinsenpoort: poort, torens, brug, grachtje' Model); echo "MODEL $id" > $D/textures/asset_ids.txt
for f in $D/textures/PP_*.png; do
  n=$(basename $f .png); h=$(md5 -q $f); oud=$(grep "^$n " $D/textures/hashes.txt 2>/dev/null | grep " $h\$" | cut -d' ' -f2)
  if [ -n "$oud" ]; then id=$oud; else id=$(tools/upload_asset.sh $f "$n" 'Efteling Prinsenpoort textuur' Image); fi
  echo "$n $id" >> $D/textures/asset_ids.txt; echo "$n $id $h" >> $D/textures/hashes.nieuw
done
mv $D/textures/hashes.nieuw $D/textures/hashes.txt
cat $D/textures/asset_ids.txt
