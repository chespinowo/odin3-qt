#!/bin/sh
# Gera build/odin3-qt_<versao>_all.deb a partir do código-fonte.
# Requer: python3, python3-pyqt5 (para gerar os ícones) e dpkg-deb.
set -e
cd "$(dirname "$0")"

VERSION=$(sed -n 's/^Version: //p' packaging/DEBIAN/control)
ROOT=build/pkg

mkdir -p build
rm -rf "$ROOT"
mkdir -p "$ROOT/DEBIAN" "$ROOT/usr/bin" "$ROOT/usr/lib/odin3-qt" \
         "$ROOT/usr/lib/udev/rules.d" "$ROOT/usr/share/applications" \
         "$ROOT/usr/share/doc/odin3-qt"

cp -r odin3_qt "$ROOT/usr/lib/odin3-qt/"
find "$ROOT" -name __pycache__ -type d -prune -exec rm -rf {} +
cp packaging/bin/odin3-qt "$ROOT/usr/bin/"
cp packaging/odin3-qt.desktop "$ROOT/usr/share/applications/"
cp packaging/60-odin3-qt.rules "$ROOT/usr/lib/udev/rules.d/"
cp packaging/copyright packaging/README.Debian "$ROOT/usr/share/doc/odin3-qt/"
gzip -9nc packaging/changelog.Debian > "$ROOT/usr/share/doc/odin3-qt/changelog.Debian.gz"
cp packaging/DEBIAN/postinst packaging/DEBIAN/postrm "$ROOT/DEBIAN/"

QT_QPA_PLATFORM=offscreen python3 tools/gen_assets.py "$ROOT"

find "$ROOT" -type d -exec chmod 755 {} +
find "$ROOT" -type f -exec chmod 644 {} +
chmod 755 "$ROOT/usr/bin/odin3-qt" "$ROOT/DEBIAN/postinst" "$ROOT/DEBIAN/postrm"

SIZE=$(du -sk --exclude=DEBIAN "$ROOT" | cut -f1)
sed "s/^Version:.*/&\nInstalled-Size: $SIZE/" packaging/DEBIAN/control > "$ROOT/DEBIAN/control"
(cd "$ROOT" && find usr -type f -print0 | sort -z | xargs -0 md5sum) > "$ROOT/DEBIAN/md5sums"

dpkg-deb --root-owner-group --build "$ROOT" "build/odin3-qt_${VERSION}_all.deb"
echo "Pacote gerado: build/odin3-qt_${VERSION}_all.deb"
