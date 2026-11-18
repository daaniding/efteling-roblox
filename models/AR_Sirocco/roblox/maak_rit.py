"""maak_rit: vult sirocco_rit.luau met de bron van SiroccoRit.server.luau en SiroccoRitClient.client.luau -> sirocco_rit_plak.luau
(plakken in Studio, Edit). Gebruik: python3 roblox/maak_rit.py"""
import os
R = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(R, 'sirocco_rit.luau')).read()
for k, f in (('__SERVER__', 'SiroccoRit.server.luau'), ('__CLIENT__', 'SiroccoRitClient.client.luau')):
    bron = open(os.path.join(R, f)).read()
    assert ']==]' not in bron
    s = s.replace(k, bron)
open(os.path.join(R, 'sirocco_rit_plak.luau'), 'w').write(s)
print('[maak_rit] roblox/sirocco_rit_plak.luau', len(s), 'tekens')
