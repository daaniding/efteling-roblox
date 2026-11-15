#!/bin/zsh
# export.sh [boom|omgeving|alles]
D=${0:A:h:h}; cd $D; B=/Applications/Blender.app/Contents/MacOS/Blender; W=${1:-alles}
[[ $W == boom || $W == alles ]] && $B -b -P build/09_export_roblox.py -- --master TK_boom_baked.blend --out exports/TK_boom.fbx --extra exports/boom_extra.json 2>&1 | grep EXPORT
[[ $W == omgeving || $W == alles ]] && $B -b -P build/09_export_roblox.py -- --master TK_omgeving_baked.blend --out exports/TK_omgeving.fbx --extra exports/omgeving_extra.json 2>&1 | grep EXPORT
