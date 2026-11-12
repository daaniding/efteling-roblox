#!/bin/zsh
# bouw_alles.sh: 03 vormen -> 04 tuin -> 05 bake -> export huis + tuin -> upload model(len) + texturen -> textures/asset_ids.txt + exports/omgeving_id.txt
set -e
B=/Applications/Blender.app/Contents/MacOS/Blender; D=${0:A:h:h}; R=${D:h:h}; M=$D/AR_Assepoester_master.blend
$B --background --python $D/build/03_forms.py -- --master $M 2>&1 | grep -E "built|Error|Traceback"
$B --background --python $D/build/04_omgeving.py -- --master $M 2>&1 | grep -E "objects|Error|Traceback"
$B --background --python $D/build/05_bake.py -- --master $M --samples 16 2>&1 | grep -E "KLAAR|Error|Traceback"
$B --background --python $D/build/09_export_roblox.py -- --master $D/AR_Assepoester_baked.blend --out $D/exports/AR_Assepoester_huis.fbx --extra $D/exports/huis_extra.json 2>&1 | grep -E "EXPORT|Error"
$B --background --python $D/build/09_export_roblox.py -- --master $M --col OMGEVING --out $D/exports/AR_Assepoester_omgeving.fbx --extra $D/exports/omgeving_extra.json 2>&1 | grep -E "EXPORT|Error"
cd $R
zsh -ic "
id=\$(tools/upload_asset.sh $D/exports/AR_Assepoester_huis.fbx 'Assepoester huis' 'Efteling Assepoester huis' Model); echo \"MODEL \$id\" > $D/textures/asset_ids.txt
for f in $D/textures/Assepoester_*.png; do n=\$(basename \$f .png); id=\$(tools/upload_asset.sh \$f \"\$n\" 'Efteling Assepoester textuur' Image); echo \"\$n \$id\" >> $D/textures/asset_ids.txt; done
tools/upload_asset.sh $D/exports/AR_Assepoester_omgeving.fbx 'Assepoester omgeving' 'Efteling Assepoester tuin' Model > $D/exports/omgeving_id.txt"
cat $D/textures/asset_ids.txt $D/exports/omgeving_id.txt
