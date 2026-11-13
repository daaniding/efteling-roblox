#!/bin/zsh
# upload.sh: model + texturen naar Roblox (ongewijzigde texturen houden hun id via textures/hashes.txt). Draaien vanuit de repo-root via zsh -ic.
D=${0:A:h:h}
: > $D/textures/hashes.nieuw
id=$(tools/upload_asset.sh $D/exports/AR_MagischeKlok.fbx 'Magische Klok' 'Efteling De Magische Klok: toren, muren, gracht, herauten' Model); echo "MODEL $id" > $D/textures/asset_ids.txt
for f in $D/textures/MK_*.png; do
  n=$(basename $f .png); h=$(md5 -q $f); oud=$(grep "^$n " $D/textures/hashes.txt 2>/dev/null | grep " $h\$" | cut -d' ' -f2)
  if [ -n "$oud" ]; then id=$oud; else id=$(tools/upload_asset.sh $f "$n" 'Efteling Magische Klok textuur' Image); fi
  echo "$n $id" >> $D/textures/asset_ids.txt; echo "$n $id $h" >> $D/textures/hashes.nieuw
done
mv $D/textures/hashes.nieuw $D/textures/hashes.txt
cat $D/textures/asset_ids.txt
