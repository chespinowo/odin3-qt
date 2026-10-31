"""Banner superior "Odin3" desenhado com QPainter (sem imagens externas)."""

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import (QBrush, QColor, QFont, QLinearGradient, QPainter,
                         QPainterPath, QPen, QPolygonF)
from PyQt5.QtWidgets import QWidget, QSizePolicy

CONTINENTS = [
    # Américas
    [(402, 12), (440, 6), (472, 20), (456, 34), (441, 46), (426, 62), (410, 48), (414, 30)],
    # Europa / Ásia
    [(522, 18), (560, 8), (640, 6), (720, 10), (790, 20), (802, 36), (762, 42),
     (722, 48), (690, 40), (650, 54), (620, 44), (580, 36), (546, 30)],
    # África
    [(540, 38), (582, 38), (602, 54), (586, 71), (560, 68), (545, 54)],
    # Oceania
    [(760, 54), (802, 50), (810, 66), (776, 71)],
]


def _poly(points):
    return QPolygonF([QPointF(x, y) for x, y in points])


class Banner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(71)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _icon(self, p, x, y, w, h, c1, c2):
        g = QLinearGradient(x, y, x, y + h)
        g.setColorAt(0, QColor(c1))
        g.setColorAt(1, QColor(c2))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(g))
        p.drawRoundedRect(QRectF(x, y, w, h), 3, 3)
        # balãozinho
        tail = _poly([(x + w * 0.42, y + h), (x + w * 0.5, y + h + h * 0.18), (x + w * 0.58, y + h)])
        p.drawPolygon(tail)
        # seta de download + barra
        p.setBrush(QColor("white"))
        cx = x + w / 2
        sw = w * 0.14
        top = y + h * 0.16
        p.drawRect(QRectF(cx - sw, top, sw * 2, h * 0.30))
        p.drawPolygon(_poly([(cx - sw * 2.2, y + h * 0.46), (cx + sw * 2.2, y + h * 0.46),
                             (cx, y + h * 0.66)]))
        p.drawRect(QRectF(x + w * 0.22, y + h * 0.74, w * 0.56, h * 0.07))

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(self.width() / 856.0, self.height() / 71.0)
        w, h = 856, 71

        bg = QLinearGradient(0, 0, w, 0)
        bg.setColorAt(0.0, QColor("#3c86b8"))
        bg.setColorAt(0.42, QColor("#d3ebee"))
        bg.setColorAt(1.0, QColor("#a2cbea"))
        p.fillRect(self.rect(), bg)

        # mapa-múndi estilizado
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(104, 160, 212, 150))
        for c in CONTINENTS:
            p.drawPolygon(_poly(c))

        # faixa laranja (borda inferior/direita do painel azul)
        og = QLinearGradient(0, 59, 380, 0)
        og.setColorAt(0, QColor("#d98a2b"))
        og.setColorAt(1, QColor("#f2b44f"))
        p.setBrush(QBrush(og))
        p.drawPolygon(_poly([(366, 0), (381, 0), (314, 71), (0, 71), (0, 59), (300, 59)]))

        # painel azul com o logo
        pg = QLinearGradient(0, 0, 0, 59)
        pg.setColorAt(0, QColor("#4a9bd0"))
        pg.setColorAt(1, QColor("#2b78ad"))
        p.setBrush(QBrush(pg))
        p.drawPolygon(_poly([(0, 0), (366, 0), (300, 59), (0, 59)]))

        f = QFont("DejaVu Sans")
        f.setBold(True)
        f.setPixelSize(30)
        p.setFont(f)
        p.setPen(QColor(0, 0, 0, 70))
        p.drawText(QPointF(59, 47), "Odin3")
        p.setPen(QColor("white"))
        p.drawText(QPointF(58, 46), "Odin3")

        # ícones à direita
        self._icon(p, 537, 14, 47, 36, "#5fc23b", "#3a9a22")
        self._icon(p, 691, 10, 30, 23, "#b377d9", "#8a4fb8")
        self._icon(p, 733, 6, 110, 52, "#3b8fdc", "#1f5fae")
