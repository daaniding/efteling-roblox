#!/bin/zsh
# cam.sh <tag> <x,y,z,lens> <yaw> <pitch> [shift] [clay|mat] [sensor] [res]: overlay op ref/$FOTO (default front.jpg)
D=${0:A:h:h}; MODE=${6:-clay}; MASTER=${MASTER:-$D/DR_master.blend}
/Applications/Blender.app/Contents/MacOS/Blender --background --python $D/build/cam_match.py -- --master $MASTER --out $D/review/$1 --cols FORMS --mode $MODE --cam $2 --yaw $3 --pitch $4 --shift ${5:-0,0} --res ${8:-1100x733} --sensor ${7:-8.8} 2>&1 | grep -E "Error|Traceback" -A3
python3 $D/build/cam_match.py --compose $D/review/$1 $D/ref/${FOTO:-front.jpg} $MODE >/dev/null
