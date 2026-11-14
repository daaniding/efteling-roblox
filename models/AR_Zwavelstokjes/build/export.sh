#!/bin/zsh
# export.sh: decor (gebakken) + omgeving naar FBX met botsblokken en lichtpunten (--extra)
D=${0:A:h:h}; cd $D; B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b -P build/09_export_roblox.py -- --master MZ_stadje_baked.blend --out exports/MZ_stadje.fbx --extra exports/stadje_extra.json 2>&1 | grep EXPORT
