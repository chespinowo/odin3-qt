"""Widgets customizados: caixa de status do slot e barra de progresso."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import QWidget

STATES = {
    "idle": ("#e1e1e1", "#000000"),
    "connected": ("#e1e1e1", "#000000"),
    "flashing": ("#2f8fdc", "#ffffff"),
    "pass": ("#2fa84f", "#ffffff"),
    "fail": ("#d9322b", "#ffffff"),
}


class SlotBox(QWidget):
    """Caixa grande de status (PASS! / FAIL! / nome da partição)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "idle"
        self.text = ""

    def set_state(self, state, text=""):
        self.state, self.text = state, text
        self.update()

    def paintEvent(self, _):
        bg, fg = STATES[self.state]
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(bg))
        p.setPen(QPen(QColor("#d0d0d0")))
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        if self.text:
            f = QFont(self.font())
            f.setBold(True)
            f.setPixelSize(16 if self.state in ("pass", "fail") else 12)
            p.setFont(f)
            p.setPen(QColor(fg))
            p.drawText(self.rect().adjusted(4, 0, -4, 0), Qt.AlignCenter | Qt.TextWordWrap, self.text)


class SlotBar(QWidget):
    """Barra fina de progresso abaixo de cada slot."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.text = ""

    def set_value(self, value, text=""):
        self.value, self.text = max(0, min(100, value)), text
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#e1e1e1"))
        if self.value:
            p.fillRect(1, 1, int((self.width() - 2) * self.value / 100), self.height() - 2,
                       QColor("#3b9be0"))
        p.setPen(QPen(QColor("#d0d0d0")))
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        if self.text:
            p.setPen(QColor("#000000"))
            p.drawText(self.rect(), Qt.AlignCenter, self.text)
