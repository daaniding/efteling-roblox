#!/bin/zsh
# export.sh: decor (gebakken) + omgeving naar FBX met botsblokken en lichtpunten (--extra)
D=${0:A:h:h}; cd $D; B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b -P build/09_export_roblox.py -- --master RS_huisje_baked.blend --out exports/RS_huisje.fbx --extra exports/huisje_extra.json 2>&1 | grep EXPORT
