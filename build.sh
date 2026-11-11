#!/bin/bash
# Build HanoiTornyaiRT.apk without Gradle: javac -> dx -> aapt2 -> align + v2 sign
set -euo pipefail
cd "$(dirname "$0")"
T=/tmp/dl
ANDROID_JAR=$T/android.jar
AAPT2=$T/aaptjs3/package/bin/x64/linux/aapt2
D2J=$(echo $T/d2j/*/lib)
B=build; rm -rf $B; mkdir -p $B/classes $B/res
javac -nowarn --release 8 -cp "$ANDROID_JAR" -d $B/classes app/src/com/helmetsoft/hanoi/*.java 2>&1 | grep -v JAVA_TOOL || true
java -cp "$D2J/dx-30.0.2.jar" com.android.dx.command.Main --dex --min-sdk-version=24 --output=$B/classes.dex $B/classes 2>&1 | grep -v JAVA_TOOL || true
$AAPT2 compile --dir app/res -o $B/res.zip
$AAPT2 link -o $B/base.apk -I "$ANDROID_JAR" --manifest app/AndroidManifest.xml -A app/assets \
  --min-sdk-version 24 --target-sdk-version 33 --version-code 1 --version-name 1.0 $B/res.zip
(cd $B && zip -q -j base.apk classes.dex)
python3 tools/apkfinish.py $B/base.apk HanoiTornyaiRT.apk keys
ls -la HanoiTornyaiRT.apk
