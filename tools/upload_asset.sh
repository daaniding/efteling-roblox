#!/usr/bin/env bash
# Upload naar Roblox Open Cloud: Model (fbx), Image (png, voor texturen/SurfaceAppearance) of Decal (png).
# Sleutel uit ROBLOX_API_KEY (zet in ~/.zshrc); wordt nooit geprint. Gebruik: zsh -ic 'tools/upload_asset.sh bestand "Naam" "Omschrijving" Image'
set -euo pipefail
FILE="$1"; NAME="$2"; DESCRIPTION="${3:-Efteling asset}"; TYPE="${4:-Model}"
case "$TYPE" in Model) MIME="model/fbx";; Image|Decal) MIME="image/png";; *) echo "Onbekend type $TYPE" >&2; exit 1;; esac
CREATOR_ID="11801607078"
[ -z "${ROBLOX_API_KEY:-}" ] && { echo "ROBLOX_API_KEY niet gezet" >&2; exit 1; }
REQUEST=$(printf '{"assetType":"%s","displayName":"%s","description":"%s","creationContext":{"creator":{"userId":"%s"}}}' "$TYPE" "$NAME" "$DESCRIPTION" "$CREATOR_ID")
RESPONSE=$(curl -s -X POST "https://apis.roblox.com/assets/v1/assets" -H "x-api-key: $ROBLOX_API_KEY" -F "request=$REQUEST" -F "fileContent=@$FILE;type=$MIME")
OPERATION=$(printf '%s' "$RESPONSE" | python3 -I -c 'import json,sys; d=json.load(sys.stdin); print(d.get("path") or d.get("operationId") or "")' 2>/dev/null || true)
[ -z "$OPERATION" ] && { echo "Upload mislukt: $RESPONSE" >&2; exit 1; }
OPERATION="${OPERATION#operations/}"
for _ in $(seq 1 30); do
  sleep 2
  STATUS=$(curl -s "https://apis.roblox.com/assets/v1/operations/$OPERATION" -H "x-api-key: $ROBLOX_API_KEY")
  DONE=$(printf '%s' "$STATUS" | python3 -I -c 'import json,sys; d=json.load(sys.stdin); print("1" if d.get("done") else "0")')
  if [ "$DONE" = "1" ]; then printf '%s' "$STATUS" | python3 -I -c 'import json,sys; d=json.load(sys.stdin); r=d.get("response") or {}; print(r.get("assetId") or json.dumps(d))'; exit 0; fi
done
echo "Nog bezig na 60 s (operation $OPERATION)" >&2; exit 1
