#!/bin/zsh
# cam.sh <tag> <x,y,z,lens> <yaw> <shiftx> [master] [mode] : overlay op ref/hoofdfoto.jpg -> review/<tag>/compare_<mode>.jpg
D=${0:A:h:h}; M=${5:-$D/ZZ_kasteel_master.blend}; MODE=${6:-clay}
/Applications/Blender.app/Contents/MacOS/Blender --background --python $D/build/cam_match.py -- --master $M --out $D/review/$1 --cols FORMS --mode $MODE --cam $2 --yaw $3 --pitch 0 --shift $4,0.3 --res 1000x750 2>&1 | grep -E "Error|Traceback" -A3
python3 $D/build/cam_match.py --compose $D/review/$1 $D/ref/hoofdfoto.jpg $MODE >/dev/null
