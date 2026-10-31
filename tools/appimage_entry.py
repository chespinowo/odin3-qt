"""PyInstaller entry point for the Odin3 Qt AppImage."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from odin3_qt.app import main

raise SystemExit(main(sys.argv))
