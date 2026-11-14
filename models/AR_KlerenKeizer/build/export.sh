#!/bin/zsh
# export.sh: decor (gebakken) + omgeving naar FBX met botsblokken en lichtpunten (--extra)
D=${0:A:h:h}; cd $D; B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b -P build/09_export_roblox.py -- --master KK_decor_baked.blend --out exports/KK_decor.fbx --extra exports/decor_extra.json 2>&1 | grep EXPORT
$B -b -P build/09_export_roblox.py -- --master KK_omgeving_master.blend --out exports/KK_omgeving.fbx --extra exports/omgeving_extra.json 2>&1 | grep EXPORT
