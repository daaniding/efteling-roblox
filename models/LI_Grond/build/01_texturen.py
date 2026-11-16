"""01_texturen: CC0-scans -> Roblox MaterialVariant-texturen (1024 px PNG). AO wordt in de kleur gebakken (diepte tussen de sprieten).
Gebruik: python3 01_texturen.py <downloadmap> <uitmap>"""
import sys, os
from PIL import Image, ImageChops
src, uit = sys.argv[1], sys.argv[2]; os.makedirs(uit, exist_ok=True)
SETS = {
    'GR_gras004': ('Grass004/Grass004_2K-JPG_{}.jpg', {'kleur': 'Color', 'normaal': 'NormalGL', 'ruwheid': 'Roughness', 'ao': 'AmbientOcclusion'}),
    'GR_gras002': ('Grass002/Grass002_2K-JPG_{}.jpg', {'kleur': 'Color', 'normaal': 'NormalGL', 'ruwheid': 'Roughness', 'ao': 'AmbientOcclusion'}),
    'GR_bosgrond': ('forrest_ground_01/forrest_ground_01_{}_2k.jpg', {'kleur': 'diff', 'normaal': 'nor_gl', 'ruwheid': 'rough', 'ao': 'ao'}),
}
N = 1024
for naam, (pat, k) in SETS.items():
    lees = lambda s: Image.open(os.path.join(src, pat.format(k[s])))
    kleur = lees('kleur').convert('RGB').resize((N, N), Image.LANCZOS)
    ao = lees('ao').convert('L').resize((N, N), Image.LANCZOS)
    ao = ao.point(lambda v: int(255 - (255 - v) * 0.7))          # AO 70% sterk
    kleur = ImageChops.multiply(kleur, Image.merge('RGB', (ao, ao, ao)))
    kleur.save(os.path.join(uit, f'{naam}_kleur.png'))
    lees('normaal').convert('RGB').resize((N, N), Image.LANCZOS).save(os.path.join(uit, f'{naam}_normaal.png'))
    lees('ruwheid').convert('L').resize((N, N), Image.LANCZOS).save(os.path.join(uit, f'{naam}_ruwheid.png'))
    print(naam, 'klaar')

# Roblox vermenigvuldigt de ColorMap van een terrein-MaterialVariant met Terrain:GetMaterialColor (en die kleur kleurt ook de
# grassprieten). Daarom: tint = 92e percentiel van de textuur; kleurkaart = textuur / tint. Dan is bodem = foto, sprieten = tint.
import numpy as np, json
tints = {}
for naam in SETS:
    p = os.path.join(uit, f'{naam}_kleur.png')
    a = np.asarray(Image.open(p)).astype(np.float32)
    tint = np.percentile(a.reshape(-1, 3), 92, axis=0)
    Image.fromarray(np.clip(a / tint * 255, 0, 255).astype(np.uint8)).save(os.path.join(uit, f'{naam}_kleurdeel.png'))
    tints[naam] = [int(round(v)) for v in tint]
json.dump(tints, open(os.path.join(uit, 'tints.json'), 'w'))
print('tints', tints)
