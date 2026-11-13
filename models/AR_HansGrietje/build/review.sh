#!/bin/zsh
# review.sh <map> [cols]: overlay door de fotocamera (clay) + kleur: voor (foto), ZW (Hghuis0), NW (Boekloc) -> review/<map>/sheet.jpg
B=/Applications/Blender.app/Contents/MacOS/Blender; D=${0:A:h:h}; M="$D/AR_HansGrietje_master.blend"; R="$D/review/$1"; C=${2:-FORMS}; mkdir -p "$R"
CAM="--cam -0.3,-8.6,1.6,26 --sensor 25.4 --pitch 8 --res 1000x1000"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols $C ${=CAM} 2>&1 | grep -E "Error|Traceback"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols $C ${=CAM} --mode mat 2>&1 | grep -E "Error|Traceback"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols $C --cam -0.47,-8.59,1.6,24 --pitch 6 --yaw 38.7 --tag _zw --res 1000x750 --mode mat 2>&1 | grep -E "Error|Traceback"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols $C --cam -0.71,-12.0,1.7,24 --pitch 5 --yaw -45 --tag _nw --res 1000x750 --mode mat 2>&1 | grep -E "Error|Traceback"
python3 $D/build/cam_match.py --compose "$R" "$D/ref/front.jpg" clay >/dev/null
python3 - "$R" <<'PY'
import sys; from PIL import Image
R=sys.argv[1]
def flat(p,w,h):
    im=Image.open(p).convert('RGBA'); bg=Image.new('RGB',im.size,(150,170,150)); bg.paste(im,mask=im.split()[3]); bg.thumbnail((w,h)); return bg
a=Image.open(R+'/compare_clay.jpg'); a.thumbnail((2400,800))
s=Image.new('RGB',(2400,a.height+610),'white'); s.paste(a,(0,0)); y=a.height+5
s.paste(flat(R+'/render_mat.png',800,600),(0,y)); s.paste(flat(R+'/render_mat_zw.png',800,600),(800,y)); s.paste(flat(R+'/render_mat_nw.png',800,600),(1600,y))
s.save(R+'/sheet.jpg',quality=82)
PY
echo $R/sheet.jpg
