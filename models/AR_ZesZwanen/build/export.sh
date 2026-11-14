#!/bin/zsh
# export.sh: gebakken kasteel + omgeving (+ zwaan-master) naar FBX, MET botsblokken en lichtpunten (--extra; zonder vallen ze weg)
D=${0:A:h:h}; cd $D; B=/Applications/Blender.app/Contents/MacOS/Blender
for d in kasteel omgeving; do $B -b -P build/09_export_roblox.py -- --master ZZ_${d}_baked.blend --out exports/ZZ_$d.fbx --extra exports/${d}_extra.json 2>&1 | grep EXPORT; done
