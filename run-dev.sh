#!/bin/sh
# Executa o programa direto do código-fonte, sem instalar o .deb.
set -e
cd "$(dirname "$0")"
if [ ! -d build/dev ]; then
    QT_QPA_PLATFORM=offscreen python3 tools/gen_assets.py build/dev
fi
ODIN3_QT_IMAGES="$PWD/build/dev/usr/share/odin3-qt/images" exec python3 -m odin3_qt "$@"
