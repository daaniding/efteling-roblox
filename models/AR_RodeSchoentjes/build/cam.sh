#!/bin/zsh
# cam.sh <tag> <x,y,z,lens> <yaw> <pitch> [shift] [clay|mat] : overlay op ref/front.jpg (Boekloc_RodeSchoentjes, 1000x665)
D=${0:A:h:h}; MODE=${6:-clay}
/Applications/Blender.app/Contents/MacOS/Blender --background --python $D/build/cam_match.py -- --master $D/RD_master.blend --out $D/review/$1 --cols FORMS --mode $MODE --cam $2 --yaw $3 --pitch $4 --shift ${5:-0,0} --res 800x532 --sensor 24 2>&1 | grep -E "Error|Traceback" -A3
python3 $D/build/cam_match.py --compose $D/review/$1 $D/ref/${FOTO:-front.jpg} $MODE >/dev/null
