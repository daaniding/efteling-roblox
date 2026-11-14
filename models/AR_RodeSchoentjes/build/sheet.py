import os, sys
from PIL import Image, ImageDraw
d = sys.argv[1]; fs = [os.path.join(d, n + '.png') for n in "oost west deurzijde achter boven kijkplein".split()]
ims = [Image.open(f).convert('RGB') for f in fs]; W, H = ims[0].size
s = Image.new('RGB', (W * 3, H * 2), 'white')
for i, (im, f) in enumerate(zip(ims, fs)): s.paste(im, ((i % 3) * W, (i // 3) * H)); ImageDraw.Draw(s).text(((i % 3) * W + 8, (i // 3) * H + 8), os.path.basename(f), fill='black')
s.thumbnail((2100, 2100)); s.save(os.path.join(d, 'sheet.jpg'), quality=82); print("SHEET")
