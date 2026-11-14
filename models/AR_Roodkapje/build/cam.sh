#!/bin/zsh
# cam.sh <tag> <x,y,z,lens> <yaw> <pitch> [shiftx,shifty] [foto] : klei-overlay op een foto -> review/<tag>/compare_clay.jpg
D=${0:A:h:h}; F=${6:-Grootmoedershuisje_herbouwd.jpg}
R=$(python3 -c "from PIL import Image; w,h=Image.open('$D/ref/eftepedia/$F').size; print('%dx%d'%(800,round(800*h/w)))")
/Applications/Blender.app/Contents/MacOS/Blender --background --python $D/build/cam_match.py -- --master $D/RK_huisje_master.blend --out $D/review/$1 --cols FORMS --mode clay --cam $2 --yaw $3 --pitch $4 --shift ${5:-0,0} --res $R --sensor 24 2>&1 | grep -E "Error|Traceback" -A3
python3 $D/build/cam_match.py --compose $D/review/$1 $D/ref/eftepedia/$F clay >/dev/null
