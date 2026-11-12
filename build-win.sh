#!/bin/bash
# Windows x64 portable build (Electron) – Linuxon is fut, wine nélkül.
set -euo pipefail
cd "$(dirname "$0")"
VER=1.1.0
EZIP=/tmp/dl/electron-win.zip
OUT=dist/HanoiTornyaiRT-win-x64
rm -rf "$OUT"; mkdir -p "$OUT"
unzip -q "$EZIP" -d "$OUT"
mv "$OUT/electron.exe" "$OUT/HanoiTornyaiRT.exe"
rm -f "$OUT/resources/default_app.asar"
mkdir -p "$OUT/resources/app/game"
cp desktop/package.json desktop/main.js desktop/preload.js desktop/icon.png "$OUT/resources/app/"
cp app/assets/index.html "$OUT/resources/app/game/"
(cd /tmp/rtool && node patch.mjs "$OLDPWD/$OUT/HanoiTornyaiRT.exe" icon.ico $VER)
(cd dist && rm -f HanoiTornyaiRT-win-x64.zip && zip -q -r -9 HanoiTornyaiRT-win-x64.zip HanoiTornyaiRT-win-x64)
ls -la dist/*.zip
