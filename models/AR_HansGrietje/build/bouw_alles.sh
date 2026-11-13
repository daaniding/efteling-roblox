#!/bin/zsh
# bouw_alles.sh: 03a atlassen -> 03 huis -> 04 tuin -> 05 bake -> export huis + tuin -> upload modellen + texturen (ongewijzigde texturen houden hun id)
# Daarna: python3 roblox/maak_plaatsscript.py en roblox/plaats_hansgrietje.luau in Studio.
set -e
B=/Applications/Blender.app/Contents/MacOS/Blender; D=${0:A:h:h}; R=${D:h:h}; M=$D/AR_HansGrietje_master.blend
python3 $D/build/03a_atlas.py
$B --background --python $D/build/03_forms.py -- --master $M 2>&1 | grep -E "\[03|Error|Traceback" || true
$B --background --python $D/build/04_omgeving.py -- --master $M 2>&1 | grep -E "omgeving|Error|Traceback" || true
$B --background --python $D/build/05_bake.py -- --master $M --samples 16 2>&1 | grep -E "KLAAR|Error|Traceback" || true
$B --background --python $D/build/09_export_roblox.py -- --master $D/AR_HansGrietje_baked.blend --out $D/exports/AR_HansGrietje_huis.fbx --extra $D/exports/huis_extra.json 2>&1 | grep -E "EXPORT|Error" || true
$B --background --python $D/build/09_export_roblox.py -- --master $D/AR_HansGrietje_baked.blend --col OMGEVING --out $D/exports/AR_HansGrietje_omgeving.fbx --extra $D/exports/omgeving_extra.json 2>&1 | grep -E "EXPORT|Error" || true
cd $R
zsh -ic "
rm -f $D/textures/hashes.nieuw; id=\$(tools/upload_asset.sh $D/exports/AR_HansGrietje_huis.fbx 'Hans en Grietje huis' 'Efteling Hans en Grietje snoephuisje' Model); echo \"MODEL \$id\" > $D/textures/asset_ids.txt
for f in $D/textures/HG_*.png; do n=\$(basename \$f .png); h=\$(md5 -q \$f); oud=\$(grep \"^\$n \" $D/textures/hashes.txt 2>/dev/null | grep \" \$h\$\" | cut -d' ' -f2)
  if [ -n \"\$oud\" ]; then id=\$oud; else id=\$(tools/upload_asset.sh \$f \"\$n\" 'Efteling Hans en Grietje textuur' Image); fi
  echo \"\$n \$id\" >> $D/textures/asset_ids.txt; echo \"\$n \$id \$h\" >> $D/textures/hashes.nieuw; done
mv $D/textures/hashes.nieuw $D/textures/hashes.txt
tools/upload_asset.sh $D/exports/AR_HansGrietje_omgeving.fbx 'Hans en Grietje tuin' 'Efteling Hans en Grietje voortuin' Model > $D/exports/omgeving_id.txt"
cat $D/textures/asset_ids.txt $D/exports/omgeving_id.txt
