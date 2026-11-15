"""Frames uit een (wandel)video + overzichtsbladen met tijdstempels.
Gebruik: .venv-video/bin/python tools/video_frames.py video.mp4 uitmap [elke_s=5] [breedte=960]
Uit: uitmap/f_<sec>.jpg en uitmap/blad_XX.jpg (6 x 8 kleine beelden, tijd linksboven). ffmpeg uit imageio-ffmpeg."""
import sys, os, glob, subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
video, uit = sys.argv[1], sys.argv[2]
elk = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
breed = int(sys.argv[4]) if len(sys.argv) > 4 else 960
os.makedirs(uit, exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()
if not glob.glob(os.path.join(uit, 'f_*.jpg')):
    subprocess.run([ff, '-loglevel', 'error', '-i', video, '-vf', f'fps=1/{elk},scale={breed}:-2', '-q:v', '3',
                    os.path.join(uit, 'r_%05d.jpg')], check=True)
    for p in sorted(glob.glob(os.path.join(uit, 'r_*.jpg'))):
        n = int(os.path.basename(p)[2:7]); t = int((n - 1) * elk)
        os.rename(p, os.path.join(uit, f'f_{t:05d}.jpg'))
fr = sorted(glob.glob(os.path.join(uit, 'f_*.jpg')))
try: font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 18)
except Exception: font = None
TW, TH, C, R = 300, 169, 6, 8
for b in range(0, len(fr), C * R):
    sheet = Image.new('RGB', (TW * C, TH * R), 'black'); d = ImageDraw.Draw(sheet)
    for k, p in enumerate(fr[b:b + C * R]):
        im = Image.open(p).convert('RGB').resize((TW, TH)); x, y = (k % C) * TW, (k // C) * TH
        sheet.paste(im, (x, y)); t = int(os.path.basename(p)[2:7])
        d.text((x + 4, y + 2), f'{t // 3600}:{t // 60 % 60:02d}:{t % 60:02d}', fill='yellow', font=font, stroke_width=2, stroke_fill='black')
    sheet.save(os.path.join(uit, f'blad_{b // (C * R):02d}.jpg'), quality=80)
print(len(fr), 'frames,', (len(fr) + C * R - 1) // (C * R), 'bladen')
