#!/bin/zsh
# review.sh <map>: overlay door fotocamera + close-ups hoofd, lijf en rots -> /private/tmp/claude-501/ln/sheet_<map>.jpg
B=/Applications/Blender.app/Contents/MacOS/Blender; D=${0:A:h:h}; M="$D/CH_Langnek_master.blend"; R="$D/review/$1"; mkdir -p "$R"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols LOW 2>&1 | grep -E "Error|Traceback"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols LOW --cam 0,-4.2,12.45,50 --pitch 0 --tag _hoofd --res 700x700 2>&1 | grep -E "Error|Traceback"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols LOW --cam 0,-10,4.2,40 --pitch 0 --yaw -30 --tag _lijf --res 800x700 2>&1 | grep -E "Error|Traceback"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols LOW --cam 0,-16,6,28 --pitch -12 --yaw 35 --tag _rots --res 800x700 2>&1 | grep -E "Error|Traceback"
python3 $D/build/cam_match.py --compose "$R" "$D/ref/front.jpg" clay >/dev/null
python3 - "$R" "$1" <<'PY'
import sys; from PIL import Image
R=sys.argv[1]
a=Image.open(R+'/compare_clay.jpg'); a.thumbnail((1500,700))
s=Image.new('RGB',(1500,700+470),'white'); s.paste(a,(0,0))
for i,t in enumerate(['_hoofd','_lijf','_rots']):
    im=Image.open(R+'/render_clay%s.png'%t).convert('RGBA'); bg=Image.new('RGB',im.size,(200,210,220)); bg.paste(im,mask=im.split()[3]); bg.thumbnail((495,465)); s.paste(bg,(i*500,705))
s.save('/private/tmp/claude-501/ln/sheet_%s.jpg'%sys.argv[2],quality=82)
PY
