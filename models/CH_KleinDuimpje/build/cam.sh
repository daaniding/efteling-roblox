#!/bin/zsh
# cam.sh <tag> <x,y,z,lens> <yaw> <pitch> <shiftx,shifty> [ref] : reus + omgeving door de fotocamera -> review/<tag>/compare_clay.jpg
D=${0:A:h:h}; REF=${6:-Kduimpje_reus_zijaanzicht.jpg}
W=$(python3 -c "from PIL import Image; print('%dx%d'%Image.open('$D/ref/eftepedia/$REF').size)")
/Applications/Blender.app/Contents/MacOS/Blender --background --python $D/build/cam_match.py -- --master $D/CH_KleinDuimpje_master.blend --append $D/KD_omgeving_master.blend --out $D/review/$1 --cols LOW --mode clay --cam $2 --yaw $3 --pitch $4 --shift $5 --res $W --sensor 24 2>&1 | grep -E "Error|Traceback" -A3
python3 $D/build/cam_match.py --compose $D/review/$1 $D/ref/eftepedia/$REF clay >/dev/null
