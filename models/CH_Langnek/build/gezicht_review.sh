#!/bin/zsh
# gezicht_review.sh <map>: hoofd onder de fotohoek + van voren (Cycles) naast de foto-uitsneden -> /private/tmp/claude-501/ln/gezicht_<map>.jpg
B=/Applications/Blender.app/Contents/MacOS/Blender; D=${0:A:h:h}; M="$D/CH_Langnek_master.blend"; R="$D/review/$1"; mkdir -p "$R"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols LOW --cam 0,-12.4,1.6,190 --pitch 37.0 --tag _foto --res 600x600 --mode mat 2>&1 | grep -E "Error|Traceback"
$B --background --python $D/build/cam_match.py -- --master "$M" --out "$R" --cols LOW --cam 0,-4.2,11.45,50 --pitch 0 --tag _voor --res 600x600 --mode mat 2>&1 | grep -E "Error|Traceback"
python3 - "$R" "$D" "$1" <<'PY'
import sys; from PIL import Image
R,D,tag=sys.argv[1:4]
a=Image.open(D+'/ref/front.jpg'); w,h=a.size
crop=a.crop((int(w*.40),int(h*.025),int(w*.60),int(h*.15))).resize((600,375))
b=Image.open(D+'/ref/eftepedia/Winterlangnek.jpg'); w2,h2=b.size
crop2=b.crop((int(w2*.39),int(h2*.0),int(w2*.6),int(h2*.13))); crop2=crop2.resize((600,int(600*crop2.height/crop2.width)))
out=Image.new('RGB',(2400,620),'white'); out.paste(crop,(0,0)); out.paste(crop2,(600,0))
for i,t in enumerate(['_foto','_voor']):
    im=Image.open(R+'/render_mat%s.png'%t).convert('RGBA'); bg=Image.new('RGB',im.size,(170,190,215)); bg.paste(im,mask=im.split()[3]); out.paste(bg,(1200+i*600,0))
out.save('/private/tmp/claude-501/ln/gezicht_%s.jpg'%tag,quality=85)
PY
