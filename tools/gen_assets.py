"""Gera PNGs/SVG usados pelo pacote. Uso: gen_assets.py <raiz-do-pacote>"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPen, QPolygonF

root = sys.argv[1]
app = QGuiApplication([])


def canvas(w, h, bg=None):
    img = QImage(w, h, QImage.Format_ARGB32)
    img.fill(QColor(bg) if bg else Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    return img, p


img_dir = os.path.join(root, "usr/share/odin3-qt/images")
os.makedirs(img_dir, exist_ok=True)

# check
img, p = canvas(11, 11, "white")
pen = QPen(QColor("#111111"), 1.6)
pen.setCapStyle(Qt.RoundCap)
pen.setJoinStyle(Qt.RoundJoin)
p.setPen(pen)
p.drawPolyline(QPolygonF([QPointF(2, 5.5), QPointF(4.6, 8.2), QPointF(9, 2.6)]))
p.end()
img.save(os.path.join(img_dir, "check.png"))

# setas da barra de rolagem
for name, pts in (("arrow_up", [(1, 6), (4.5, 2), (8, 6)]), ("arrow_down", [(1, 2), (4.5, 6), (8, 2)])):
    img, p = canvas(9, 8)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#606060"))
    p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))
    p.end()
    img.save(os.path.join(img_dir, name + ".png"))


# ícone do aplicativo
def draw_icon(p, s):
    g = QLinearGradient(0, 0, 0, s)
    g.setColorAt(0, QColor("#4a9bd0"))
    g.setColorAt(1, QColor("#1f5fae"))
    p.setPen(Qt.NoPen)
    p.setBrush(g)
    p.drawRoundedRect(QRectF(s * .04, s * .04, s * .92, s * .92), s * .16, s * .16)
    p.setBrush(QColor("white"))
    cx = s / 2
    p.drawRect(QRectF(cx - s * .09, s * .18, s * .18, s * .28))
    p.drawPolygon(QPolygonF([QPointF(cx - s * .24, s * .44), QPointF(cx + s * .24, s * .44),
                             QPointF(cx, s * .66)]))
    p.drawRect(QRectF(s * .22, s * .72, s * .56, s * .07))


for size in (48, 256):
    img, p = canvas(size, size)
    draw_icon(p, size)
    p.end()
    d = os.path.join(root, "usr/share/icons/hicolor/%dx%d/apps" % (size, size))
    os.makedirs(d, exist_ok=True)
    img.save(os.path.join(d, "odin3-qt.png"))

svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4a9bd0"/><stop offset="1" stop-color="#1f5fae"/></linearGradient></defs>
  <rect x="10" y="10" width="236" height="236" rx="41" fill="url(#g)"/>
  <rect x="105" y="46" width="46" height="72" fill="#fff"/>
  <polygon points="67,113 189,113 128,169" fill="#fff"/>
  <rect x="56" y="184" width="144" height="18" fill="#fff"/>
</svg>
"""
d = os.path.join(root, "usr/share/icons/hicolor/scalable/apps")
os.makedirs(d, exist_ok=True)
with open(os.path.join(d, "odin3-qt.svg"), "w") as f:
    f.write(svg)
print("assets ok")
