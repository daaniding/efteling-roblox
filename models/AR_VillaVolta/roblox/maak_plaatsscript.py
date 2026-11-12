"""Maakt plaats_villavolta.luau uit exports/omgeving_data.json. Gebruik: python3 maak_plaatsscript.py VILLA_ID OMGEVING_ID"""
import json,os,sys
V=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
villa,omg=sys.argv[1],sys.argv[2]
d=json.load(open(os.path.join(V,"exports","omgeving_data.json")))
tbl=lambda rows:"{"+",".join("{"+",".join(f"{v:g}" for v in r)+"}" for r in rows)+"}"
tpl=open(os.path.join(V,"roblox","plaats_template.luau")).read()
out=(tpl.replace("__VILLA__",villa).replace("__OMG__",omg).replace("__COLL__",tbl(d["colliders"])).replace("__LAMPS__",tbl(d["lamps"]))
        .replace("__HUIDEN__",tbl(d["huiden"])).replace("__INGANG__",tbl([d["ingangbord"]])).replace("__BORD__",tbl([d["wachtbord"]])))
open(os.path.join(V,"roblox","plaats_villavolta.luau"),"w").write(out); print(len(out))
