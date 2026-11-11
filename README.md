# Hanoi Tornyai RT

Hanoi tornyai játék Androidra, valós idejű sugárkövetéssel (WebGL fragment shader raytracer, WebView-ban).

![preview](preview.png)

## Funkciók
- Analitikus sugárkövetés: korongok, rudak, talapzat; tükröződés, lágy árnyék, ambient occlusion
- Progresszív élsimítás állóképen, adaptív felbontás mozgás közben
- 6 nehézségi szint (3–8 korong), csillagos értékelés, rekordok
- Visszavonás, tipp (optimális következő lépés bármely állásból), automatikus bemutató
- Hang, rezgés, kameraforgatás húzással

## Telepítés
APK: lásd a Releases oldalt. Android 7.0+ (minSdk 24).

## Build (Gradle nélkül)
`build.sh`: javac → dx → aapt2 link → 4 bájtos igazítás + APK Signature Scheme v2 (`tools/apkfinish.py`).
Szükséges: `android.jar` (API 33), `aapt2`, `dx` – az elérési utakat a `build.sh` elején kell beállítani.
Az aláíró kulcs a `keys/` mappába kerül (nincs verziókezelve).

## Szerző
Sisak László (helmetsoft.com)
