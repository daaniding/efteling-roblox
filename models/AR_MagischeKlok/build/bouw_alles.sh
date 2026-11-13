#!/bin/zsh
# bouw_alles.sh: 03a atlassen -> 03 vormen -> 03b herauten -> 05 bake -> export -> upload model + texturen (ongewijzigde texturen houden hun id)
# Daarna: python3 roblox/maak_plaatsscript.py en roblox/plaats_magischeklok.luau in Studio.
B=/Applications/Blender.app/Contents/MacOS/Blender; D=${0:A:h:h}; R=${D:h:h}; M=$D/AR_MagischeKlok_master.blend
python3 $D/build/03a_atlas.py
$B --background --python $D/build/03_forms.py -- --master $M 2>&1 | grep -E "\[03|Traceback" || true
[ -f $D/build/03b_heraut.py ] && { $B --background --python $D/build/03b_heraut.py -- --master $M 2>&1 | grep -E "\[03b|Traceback" || true; }
$B --background --python $D/build/05_bake.py -- --master $M --samples 16 2>&1 | grep -E "KLAAR|Traceback" || true
$B --background --python $D/build/09_export_roblox.py -- --master $D/AR_MagischeKlok_baked.blend --out $D/exports/AR_MagischeKlok.fbx --extra $D/exports/klok_extra.json 2>&1 | grep -E "EXPORT|Traceback" || true
cd $R && zsh -ic "zsh $D/build/upload.sh"
