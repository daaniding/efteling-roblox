#!/bin/zsh
# review.sh <map> [cols]: overlay door de fotocamera (clay) + kleur vooraanzicht, NW-driekwart en close-up entree -> review/<map>/sheet.jpg
B=/Applications/Blender.app/Contents/MacOS/Blender; D=${0:A:h:h}; M="$D/AR_Assepoester_master.blend"; R="$D/review/$1"; C=${2:-FORMS}; mkdir -p "$R"
CAM="--cam 0.07,-299.1,1.6,1061 --pitch 0.37 --res 1000x665"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols $C ${=CAM} 2>&1 | grep -E "Error|Traceback"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols $C ${=CAM} --mode mat 2>&1 | grep -E "Error|Traceback"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols $C --cam 5,-19,1.7,26 --pitch 8 --yaw -40 --tag _nw --res 1000x750 --mode mat 2>&1 | grep -E "Error|Traceback"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols $C --cam -3.2,-5.5,1.6,24 --pitch 6 --yaw 0 --tag _entree --res 1000x750 --mode mat 2>&1 | grep -E "Error|Traceback"
python3 $D/build/cam_match.py --compose "$R" "$D/ref/front.jpg" clay >/dev/null
python3 - "$R" <<'PY'
import sys; from PIL import Image
R=sys.argv[1]
def flat(p,w,h):
    im=Image.open(p).convert('RGBA'); bg=Image.new('RGB',im.size,(196,206,214)); bg.paste(im,mask=im.split()[3]); bg.thumbnail((w,h)); return bg
a=Image.open(R+'/compare_clay.jpg'); a.thumbnail((2400,600))
s=Image.new('RGB',(2400,a.height+610),'white'); s.paste(a,(0,0)); y=a.height+5
s.paste(flat(R+'/render_mat.png',800,600),(0,y)); s.paste(flat(R+'/render_mat_nw.png',800,600),(800,y)); s.paste(flat(R+'/render_mat_entree.png',800,600),(1600,y))
s.save(R+'/sheet.jpg',quality=82)
PY
echo $R/sheet.jpg
