import sys
from PIL import Image
d=sys.argv[1]; im=Image.open(d+'/compare_clay.jpg'); W=im.width//3
im.crop((2*W+int(W*0.3),0,2*W+int(W*0.75),int(im.height*0.8))).resize((720,int(im.height*0.8*720/(W*0.45)))).save(d+'/crop.jpg')
