#!/bin/zsh
# bouw_alles.sh Herautenplein: 03 vormen -> 03c klimop -> 05 bake -> export -> upload. Daarna: python3 roblox/maak_plaatsscript.py + roblox/plaats_prinsenpoort.luau in Studio.
B=/Applications/Blender.app/Contents/MacOS/Blender; D=${0:A:h:h}; R=${D:h:h}; M=$D/AR_Herautenplein_master.blend
$B --background --python $D/build/03_forms.py -- --master $M 2>&1 | grep -E "\[03|Traceback" || true
$B --background --python $D/build/05_bake.py -- --master $M --samples 16 2>&1 | grep -E "KLAAR|Traceback" || true
$B --background --python $D/build/09_export_roblox.py -- --master $D/AR_Herautenplein_baked.blend --out $D/exports/AR_Herautenplein.fbx --extra $D/exports/plein_extra.json 2>&1 | grep -E "EXPORT|Traceback" || true
cd $R && zsh -ic "zsh $D/build/upload.sh"
