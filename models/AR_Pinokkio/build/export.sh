#!/bin/zsh
D=${0:A:h:h}; cd $D; B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b -P build/09_export_roblox.py -- --master PK_decor_baked.blend --out exports/PK_decor.fbx --extra exports/decor_extra.json 2>&1 | grep EXPORT
$B -b -P build/09_export_roblox.py -- --master PK_vis_master.blend --out exports/PK_vis.fbx --extra exports/vis_extra.json 2>&1 | grep EXPORT
