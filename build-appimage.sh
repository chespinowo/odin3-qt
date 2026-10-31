#!/bin/sh
# Build a PyInstaller-backed AppImage. Requires python3-venv, curl, and mksquashfs.
set -eu
cd "$(dirname "$0")"

VERSION=$(sed -n 's/^Version: //p' packaging/DEBIAN/control)
ARCH=$(uname -m)
WORK=build/appimage
VENV="$WORK/venv"
APPDIR="$WORK/AppDir"
PYINSTALLER="$VENV/bin/pyinstaller"
APPIMAGETOOL="$WORK/appimagetool.AppImage"

if [ "$ARCH" != "x86_64" ]; then
    echo "AppImage build currently supports x86_64; detected $ARCH" >&2
    exit 1
fi

python3 -c 'import PyQt5' || {
    echo "PyQt5 is required to build the AppImage (install python3-pyqt5)." >&2
    exit 1
}

if [ ! -x "$PYINSTALLER" ]; then
    python3 -m venv --system-site-packages "$VENV"
    "$VENV/bin/pip" install pyinstaller
fi

if [ ! -x "$APPIMAGETOOL" ]; then
    curl -fL --retry 3 \
        https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage \
        -o "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
fi

rm -rf "$WORK/dist" "$WORK/work" "$APPDIR"
mkdir -p "$APPDIR/usr/lib/odin3-qt" "$APPDIR/usr/bin"
"$PYINSTALLER" --noconfirm --clean --windowed \
    --name odin3-qt --paths . --distpath "$WORK/dist" --workpath "$WORK/work" \
    --specpath "$WORK" \
    tools/appimage_entry.py
cp -a "$WORK/dist/odin3-qt/." "$APPDIR/usr/lib/odin3-qt/"
ln -s ../lib/odin3-qt/odin3-qt "$APPDIR/usr/bin/odin3-qt"

QT_QPA_PLATFORM=offscreen python3 tools/gen_assets.py "$APPDIR"
sed 's/^Exec=.*/Exec=AppRun/' packaging/odin3-qt.desktop > "$APPDIR/odin3-qt.desktop"
cp "$APPDIR/usr/share/icons/hicolor/256x256/apps/odin3-qt.png" "$APPDIR/odin3-qt.png"
cat > "$APPDIR/AppRun" <<'APPRUN'
#!/bin/sh
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export ODIN3_QT_IMAGES="$HERE/usr/share/odin3-qt/images"
exec "$HERE/usr/bin/odin3-qt" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

APPIMAGE_EXTRACT_AND_RUN=1 ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" \
    "build/odin3-qt_${VERSION}_x86_64.AppImage"
echo "AppImage gerado: build/odin3-qt_${VERSION}_x86_64.AppImage"
