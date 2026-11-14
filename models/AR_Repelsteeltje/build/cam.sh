#!/bin/zsh
# cam.sh <tag> <x,y,z,lens> <yaw> <pitch> <shiftx,shifty> : overlay op ref/eftepedia/Repelsteeltje_exterieur.jpg -> review/<tag>/compare_clay.jpg
D=${0:A:h:h}
/Applications/Blender.app/Contents/MacOS/Blender --background --python $D/build/cam_match.py -- --master $D/RS_huisje_master.blend --out $D/review/$1 --cols FORMS --mode clay --cam $2 --yaw $3 --pitch $4 --shift $5 --res 640x480 --sensor 24 2>&1 | grep -E "Error|Traceback" -A3
python3 $D/build/cam_match.py --compose $D/review/$1 $D/ref/eftepedia/Repelsteeltje_exterieur.jpg clay >/dev/null
