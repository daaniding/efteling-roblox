#!/bin/zsh
# bouw_deel.sh grot|kasteel|omgeving : alleen dat deel opnieuw bouwen, bakken, exporteren en uploaden (Daan: "het duurt elke keer zo lang").
# grot: 03b -> bake alleen rots/ruine -> export grot -> upload grot + zijn texturen (ids in textures/asset_ids_grot.txt)
# kasteel: 03 -> bake alleen kasteel -> export -> upload (textures/asset_ids_kasteel.txt); omgeving: 04 -> export -> upload (exports/omgeving_id.txt)
set -e
DEEL=$1; B=/Applications/Blender.app/Contents/MacOS/Blender; D=${0:A:h:h}; R=${D:h:h}; M=$D/AR_Sneeuwwitje_master.blend
case $DEEL in
  grot)     $B --background --python $D/build/03b_grot.py -- --master $M 2>&1 | grep -E "rots tris|Traceback" ;;
  kasteel)  $B --background --python $D/build/03_forms.py -- --master $M 2>&1 | grep -E "built|Traceback" ;;
  omgeving) $B --background --python $D/build/04_omgeving.py -- --master $M 2>&1 | grep -E "omgeving|Traceback"
            $B --background --python $D/build/09_export_roblox.py -- --master $M --col OMGEVING --out $D/exports/AR_Sneeuwwitje_omgeving.fbx --extra $D/exports/omgeving_extra.json 2>&1 | grep -E "EXPORT"
            cd $R; zsh -ic "tools/upload_asset.sh $D/exports/AR_Sneeuwwitje_omgeving.fbx 'Sneeuwwitje omgeving' 'Efteling Sneeuwwitje plein' Model" > $D/exports/omgeving_id.txt; cat $D/exports/omgeving_id.txt; exit 0 ;;
esac
$B --background --python $D/build/05_bake.py -- --master $M --deel $DEEL --samples 12 2>&1 | grep -E "KLAAR|Traceback"
EX=$D/exports/kasteel_extra.json; [ $DEEL = grot ] && EX=$D/exports/grot_extra.json
$B --background --python $D/build/09_export_roblox.py -- --master $D/AR_Sneeuwwitje_baked_$DEEL.blend --out $D/exports/AR_Sneeuwwitje_$DEEL.fbx --extra $EX 2>&1 | grep -E "EXPORT"
cd $R
PRE=Sneeuwwitje_; [ $DEEL = grot ] && PATS="rots ruine grot_" || PATS="baksteen steen pannen"
zsh -ic "
id=\$(tools/upload_asset.sh $D/exports/AR_Sneeuwwitje_$DEEL.fbx 'Sneeuwwitje $DEEL' 'Efteling Sneeuwwitje $DEEL' Model); echo \"MODEL \$id\" > $D/textures/asset_ids_$DEEL.txt
for p in $PATS; do for f in $D/textures/Sneeuwwitje_\$p*.png(N); do n=\$(basename \$f .png); id=\$(tools/upload_asset.sh \$f \"\$n\" 'Efteling Sneeuwwitje textuur' Image); echo \"\$n \$id\" >> $D/textures/asset_ids_$DEEL.txt; done; done"
cat $D/textures/asset_ids_$DEEL.txt
