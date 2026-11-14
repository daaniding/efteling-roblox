#!/bin/zsh
D=${0:A:h:h}; cd $D; B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b -P build/09_export_roblox.py -- --master RD_baked.blend --out exports/RD_loggia.fbx --extra exports/loggia_extra.json 2>&1 | grep EXPORT
