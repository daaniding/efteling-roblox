#!/bin/zsh
# export.sh [huis|omgeving|alles]
D=${0:A:h:h}; cd $D; B=/Applications/Blender.app/Contents/MacOS/Blender; W=${1:-alles}
[[ $W == huis || $W == alles ]] && $B -b -P build/09_export_roblox.py -- --master PE_huis_baked.blend --out exports/PE_huis.fbx --extra exports/huis_extra.json 2>&1 | grep EXPORT
[[ $W == omgeving || $W == alles ]] && $B -b -P build/09_export_roblox.py -- --master PE_omgeving_baked.blend --out exports/PE_omgeving.fbx --extra exports/omgeving_extra.json 2>&1 | grep EXPORT
