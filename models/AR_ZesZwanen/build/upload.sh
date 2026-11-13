#!/bin/zsh
# upload.sh: 3 modellen (kasteel, omgeving, zwaan) + alle ZK_/ZO_/ZW_-texturen (ongewijzigde texturen houden hun id via de hash)
D=${0:A:h:h}; R=${D:h:h}; cd $R
: > $D/textures/hashes.nieuw; : > $D/textures/asset_ids.nieuw
for deel in kasteel omgeving zwaan; do
  f=$D/exports/ZZ_$deel.fbx; h=$(md5 -q $f); oud=$(grep "^MODEL_$deel " $D/textures/hashes.txt 2>/dev/null | grep " $h\$" | cut -d' ' -f2)
  if [ -n "$oud" ]; then id=$oud; else id=$(tools/upload_asset.sh $f "Zes Zwanen $deel" "Efteling De Zes Zwanen $deel" Model); fi
  echo "MODEL_$deel $id" >> $D/textures/asset_ids.nieuw; echo "MODEL_$deel $id $h" >> $D/textures/hashes.nieuw
done
for f in $D/textures/Z[KOW]_*.png; do
  n=$(basename $f .png); h=$(md5 -q $f); oud=$(grep "^$n " $D/textures/hashes.txt 2>/dev/null | grep " $h\$" | cut -d' ' -f2)
  if [ -n "$oud" ]; then id=$oud; else id=$(tools/upload_asset.sh $f "$n" 'Efteling De Zes Zwanen textuur' Image); fi
  echo "$n $id" >> $D/textures/asset_ids.nieuw; echo "$n $id $h" >> $D/textures/hashes.nieuw
done
mv $D/textures/hashes.nieuw $D/textures/hashes.txt; mv $D/textures/asset_ids.nieuw $D/textures/asset_ids.txt; cat $D/textures/asset_ids.txt
