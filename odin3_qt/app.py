"""Janela principal - réplica do layout do Odin3 v3.14 em PyQt5.

As coordenadas abaixo foram medidas na captura de tela original (872x649,
com 31px de barra de título que no Linux fica por conta do gerenciador de janelas).
"""

import os
import re
import sys

from PyQt5.QtCore import QProcess, QRect, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen
from PyQt5.QtWidgets import (QApplication, QCheckBox, QFileDialog, QLabel, QLineEdit,
                             QMessageBox, QPlainTextEdit, QPushButton, QTabWidget, QWidget)

from . import __version__, backend
from .banner import Banner
from .widgets import SlotBar, SlotBox

IMG_DIR = os.environ.get("ODIN3_QT_IMAGES", "/usr/share/odin3-qt/images")
BG = "#f0f0f0"
FILE_FILTER = ("Odin Files (*.tar *.tar.md5 *.md5 *.bin *.img *.lz4 *.zip);;"
               "All Files (*)")

ROWS = [("BL", 321), ("AP", 356), ("CP", 392), ("CSC", 428), ("USERDATA", 465)]

QSS = """
* { font-size: 12px; }
QWidget#main { background: %(bg)s; }
QPushButton { background: #e1e1e1; border: 1px solid #adadad; padding: 0; color: #000; }
QPushButton:hover { background: #e5f1fb; border: 1px solid #0078d7; }
QPushButton:pressed { background: #cce4f7; border: 1px solid #005499; }
QPushButton:disabled { background: #cccccc; border: 1px solid #bfbfbf; color: #838383; }
QPushButton[primary="true"] { border: 1px solid #0078d7; }
QLineEdit { background: #f5f5f5; border: 1px solid #7a7a7a; padding: 0 3px; color: #000; }
QCheckBox::indicator { width: 13px; height: 13px; border: 1px solid #333333; background: #ffffff; }
QCheckBox::indicator:hover { border: 1px solid #0078d7; }
QCheckBox::indicator:checked { image: url(%(img)s/check.png); }
QTabWidget::pane { border: 1px solid #d9d9d9; background: %(bg)s; top: -1px; }
QTabBar::tab { background: %(bg)s; border: 1px solid #d9d9d9; border-bottom: none;
               padding: 0 6px; height: 16px; margin-right: -1px; }
QTabBar::tab:selected { background: #ffffff; height: 18px; }
QTabBar::tab:hover:!selected { background: #eaf3fb; border-color: #7eb4ea; }
QPlainTextEdit { background: #ffffff; border: 1px solid #828790; }
QScrollBar:vertical { background: #f0f0f0; width: 16px; margin: 17px 0 17px 0; border: none; }
QScrollBar::handle:vertical { background: #cdcdcd; min-height: 20px; margin: 0 1px; }
QScrollBar::handle:vertical:hover { background: #a6a6a6; }
QScrollBar::handle:vertical:disabled { background: #f0f0f0; }
QScrollBar::add-line:vertical { height: 17px; subcontrol-position: bottom;
                                subcontrol-origin: margin; background: #f0f0f0; border: none; }
QScrollBar::sub-line:vertical { height: 17px; subcontrol-position: top;
                                subcontrol-origin: margin; background: #f0f0f0; border: none; }
QScrollBar::up-arrow:vertical { image: url(%(img)s/arrow_up.png); }
QScrollBar::down-arrow:vertical { image: url(%(img)s/arrow_down.png); }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: #f0f0f0; }
QToolTip { background: #ffffff; border: 1px solid #767676; color: #000; }
""" % {"bg": BG, "img": IMG_DIR}


def place(widget, x, y, w, h):
    widget.setGeometry(x, y, w, h)
    return widget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("main")
        self.setWindowTitle("Odin3 v%s" % __version__)
        self.setFixedSize(872, 619)
        icon = QIcon.fromTheme("odin3-qt")
        if not icon.isNull():
            self.setWindowIcon(icon)

        self.slot_of = {}      # nome sysfs -> índice do slot
        self.known = {}        # nome sysfs -> info do dispositivo
        self.procs = {}        # índice do slot -> QProcess
        self.results = {}      # índice do slot -> True/False
        self.md5 = None
        self.running = False
        self.rows = {}

        self._build_banner_and_slots()
        self._build_log_tabs()
        self._build_tips_and_rows()
        self._build_buttons()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_devices)
        self.timer.start(1000)
        self.poll_devices()

    # ------------------------------------------------------------------ UI
    def _build_banner_and_slots(self):
        place(Banner(self), 14, 8, 856, 71)

        self.boxes, self.bars, self.coms = [], [], []
        for i in range(backend.MAX_SLOTS):
            x = 22 + i * 105
            self.boxes.append(place(SlotBox(self), x, 90, 103, 64))
            self.bars.append(place(SlotBar(self), x, 160, 103, 21))
            com = QLabel("", self)
            com.setAlignment(Qt.AlignCenter)
            place(com, x, 205, 103, 21)
            self.coms.append(com)
            self._style_com(i, False)

        lbl = QLabel("ID:COM", self)
        lbl.setStyleSheet("background:%s;" % BG)
        place(lbl, 20, 188, 48, 16)

    def _style_com(self, i, connected, text=""):
        bg = "#8fcdf2" if connected else "#e1e1e1"
        self.coms[i].setStyleSheet("background:%s;border:1px solid #d0d0d0;" % bg)
        self.coms[i].setText(text)

    def _build_log_tabs(self):
        tabs = QTabWidget(self)
        place(tabs, 22, 255, 313, 334)
        tabs.tabBar().setExpanding(False)
        tabs.tabBar().setDrawBase(False)
        self.tabs = tabs

        # Log
        log_page = QWidget()
        self.log = QPlainTextEdit(log_page)
        self.log.setReadOnly(True)
        self.log.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.log.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        place(self.log, 4, 6, 302, 299)
        tabs.addTab(log_page, "Log")

        # Options
        opt_page = QWidget()
        self.opt_auto = QCheckBox("Auto Reboot", opt_page)
        self.opt_auto.setChecked(True)
        self.opt_repart = QCheckBox("Re-Partition", opt_page)
        self.opt_freset = QCheckBox("F. Reset Time", opt_page)
        self.opt_freset.setChecked(True)
        self.opt_erase = QCheckBox("Nand Erase All", opt_page)
        for k, cb in enumerate((self.opt_auto, self.opt_repart, self.opt_freset, self.opt_erase)):
            place(cb, 14, 14 + k * 24, 200, 18)
        self.opt_freset.setToolTip("Apenas informativo nesta versão.")
        self.opt_repart.setToolTip("Requer arquivo PIT; não suportado pelo backend odin4.")
        self.opt_erase.setToolTip("Repassa a opção -e ao odin4 (apaga a NAND). Use com cuidado.")
        tabs.addTab(opt_page, "Options")

        # Pit
        pit_page = QWidget()
        pit_btn = QPushButton("PIT", pit_page)
        place(pit_btn, 14, 14, 70, 24)
        self.pit_field = QLineEdit(pit_page)
        self.pit_field.setReadOnly(True)
        place(self.pit_field, 92, 12, 208, 28)
        pit_btn.clicked.connect(lambda: self._pick(self.pit_field, None))
        tabs.addTab(pit_page, "Pit")

        link = QLabel('Odin Community : <a href="http://mobilerndhub.sec.samsung.net/hub/site/odin/" '
                      'style="color:#0066cc;">http://mobilerndhub.sec.samsung.net/hub/site/odin/</a>', self)
        link.setOpenExternalLinks(True)
        place(link, 11, 595, 420, 18)

    def _build_tips_and_rows(self):
        title = QLabel("Tips - How to download HOME binary", self)
        title.setStyleSheet("background:%s;" % BG)
        place(title, 349, 239, 260, 16)
        for text, x, y in (
            ('OLD model : Download one binary    "(BUILD_VER)_XXX_HOME.tar.md5"', 396, 256),
            ("ex) G925FXXU3DPA5_G925FOXA3DPA5_G925FXXU3DPA5_HOME.tar.md5", 424, 270),
            ("NEW model : Download BL + AP + CP + HOME_CSC", 396, 284),
        ):
            place(QLabel(text, self), x, y - 1, 474, 16)

        for name, fy in ROWS:
            cb = QCheckBox(self)
            place(cb, 360, fy + 9, 14, 14)
            btn = QPushButton(name, self)
            place(btn, 388, fy + 3, 90, 26)
            if name == "BL":
                btn.setProperty("primary", True)
            field = QLineEdit(self)
            field.setReadOnly(True)
            place(field, 488, fy, 376 if name != "USERDATA" else 375, 30)
            btn.clicked.connect(lambda _=False, f=field, c=cb: self._pick(f, c))
            self.rows[name] = (cb, field)

    def _build_buttons(self):
        mass = QPushButton("Mass D/L ?", self)
        place(mass, 768, 504, 89, 26)
        mass.clicked.connect(self.on_mass)

        self.btn_start = QPushButton("Start", self)
        place(self.btn_start, 458, 556, 120, 33)
        self.btn_reset = QPushButton("Reset", self)
        place(self.btn_reset, 589, 556, 119, 33)
        self.btn_exit = QPushButton("Exit", self)
        place(self.btn_exit, 737, 556, 120, 33)
        self.btn_start.clicked.connect(self.on_start)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_exit.clicked.connect(self.close)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setPen(QPen(QColor("#dcdcdc")))
        p.drawRect(14, 83, 851, 152)            # moldura dos slots
        p.drawLine(14, 195, 865, 195)           # topo do grupo ID:COM
        p.drawRect(343, 246, 527, 66)           # moldura das dicas
        p.setPen(QPen(QColor("#a0a0a0")))
        p.drawLine(352, 541, 860, 541)          # separador acima de Start/Reset/Exit
        p.setPen(QPen(QColor("#ffffff")))
        p.drawLine(352, 542, 860, 542)

    # ----------------------------------------------------------------- log
    def log_line(self, text):
        self.log.appendPlainText(text)
        sb = self.log.verticalScrollBar()
        sb.setValue(sb.maximum())

    # -------------------------------------------------------------- actions
    def _pick(self, field, checkbox):
        path, _ = QFileDialog.getOpenFileName(self, "Open", os.path.expanduser("~"), FILE_FILTER)
        if path:
            field.setText(path)
            field.setCursorPosition(0)
            if checkbox is not None:
                checkbox.setChecked(True)

    def on_mass(self):
        QMessageBox.information(
            self, "Mass D/L",
            "O Start grava em paralelo todos os aparelhos detectados (até 8 slots).\n"
            "Conecte os aparelhos em Download Mode e use Start.")

    def on_reset(self):
        if self.running:
            return
        for cb, field in self.rows.values():
            cb.setChecked(False)
            field.clear()
        self.pit_field.clear()
        self.log.clear()
        for i in range(backend.MAX_SLOTS):
            self.boxes[i].set_state("idle")
            self.bars[i].set_value(0)

    def selected_files(self):
        return {name: field.text() for name, (cb, field) in self.rows.items()
                if cb.isChecked() and field.text()}

    def on_start(self):
        if self.running:
            return
        files = self.selected_files()
        if not files:
            self.log_line("<OSM> No file selected.")
            return
        if not self.known:
            self.log_line("<OSM> No device connected. Put the phone in Download Mode first.")
            return
        for path in files.values():
            if not os.path.isfile(path):
                self.log_line("<OSM> File not found: %s" % path)
                return
        if self.opt_repart.isChecked():
            QMessageBox.warning(self, "Odin3", "Re-Partition (PIT) não é suportado pelo backend "
                                "odin4. Desmarque a opção para continuar.")
            return
        self.odin4 = backend.find_odin4()
        if not self.odin4:
            self.log_line("<OSM> odin4 binary not found (set ODIN4=/path/to/odin4 or put it in PATH).")
            QMessageBox.critical(self, "Odin3", "O binário 'odin4' não foi encontrado.\n\n"
                                 "Instale o odin4 da Samsung em /usr/local/bin ou defina a "
                                 "variável de ambiente ODIN4.")
            return
        self._files = files
        self.set_running(True)
        for i in self.slot_of.values():
            self.boxes[i].set_state("flashing", "Checking")
            self.bars[i].set_value(0)
        self.md5 = backend.Md5Worker(list(files.values()), self)
        self.md5.log.connect(self.log_line)
        self.md5.finished_ok.connect(self.on_md5_done)
        self.md5.start()

    def set_running(self, flag):
        self.running = flag
        self.btn_start.setEnabled(not flag)
        self.btn_reset.setEnabled(not flag)

    def on_md5_done(self, ok):
        if not ok:
            for i in self.slot_of.values():
                self.boxes[i].set_state("fail", "FAIL!")
            self.set_running(False)
            return
        self.results = {}
        for name, i in sorted(self.slot_of.items(), key=lambda kv: kv[1]):
            dev = self.known.get(name)
            if not dev:
                continue
            self.start_flash(i, dev)
        if not self.procs:
            self.set_running(False)

    def _tag(self, dev):
        return "<ID:0/%03d>" % dev["dev"]

    def start_flash(self, i, dev):
        tag = self._tag(dev)
        args = backend.build_args(self.odin4, self._files, dev["path"],
                                  erase=self.opt_erase.isChecked(),
                                  reboot=self.opt_auto.isChecked())
        for line in ("Odin engine v(ID:3.1401)..", "File analysis..", "SetupConnection..",
                     "Initialzation..", "Firmware update start.."):
            self.log_line("%s %s" % (tag, line))
        self.boxes[i].set_state("flashing", "Flashing")
        proc = QProcess(self)
        proc.setProcessChannelMode(QProcess.MergedChannels)
        proc.readyRead.connect(lambda p=proc, i=i, t=tag: self.on_output(p, i, t))
        proc.finished.connect(lambda code, _st, i=i, t=tag: self.on_finished(i, t, code))
        proc.errorOccurred.connect(lambda _e, i=i, t=tag: self.on_finished(i, t, -1))
        self.procs[i] = proc
        proc.start(args[0], args[1:])

    def on_output(self, proc, i, tag):
        data = bytes(proc.readAll()).decode("utf-8", "replace")
        for line in re.split(r"[\r\n]+", data):
            line = line.strip()
            if not line:
                continue
            m = re.search(r"(\d{1,3})\s*%", line)
            if m:
                self.bars[i].set_value(int(m.group(1)), "%s%%" % m.group(1))
            else:
                self.log_line("%s %s" % (tag, line))

    def on_finished(self, i, tag, code):
        if i not in self.procs:
            return
        self.procs.pop(i).deleteLater()
        ok = code == 0
        self.results[i] = ok
        if ok:
            self.log_line("%s Complete(Write) operation successfully." % tag)
            self.boxes[i].set_state("pass", "PASS!")
            self.bars[i].set_value(100)
        else:
            self.log_line("%s Complete(Write) operation failed." % tag)
            self.boxes[i].set_state("fail", "FAIL!")
        if not self.procs:
            good = sum(1 for v in self.results.values() if v)
            self.log_line("<OSM> All threads completed. (succeed %d / failed %d)"
                          % (good, len(self.results) - good))
            self.set_running(False)

    # ------------------------------------------------------------- devices
    def poll_devices(self):
        current = {d["name"]: d for d in backend.scan_devices()}
        for name, dev in current.items():
            if name not in self.known:
                used = set(self.slot_of.values())
                idx = next(k for k in range(backend.MAX_SLOTS) if k not in used)
                self.slot_of[name] = idx
                self._style_com(idx, True, "%d:[%s]" % (idx, name))
                self.log_line("%s Added!!" % self._tag(dev))
        for name in list(self.known):
            if name not in current:
                idx = self.slot_of.pop(name)
                if not self.running and idx not in self.results:
                    self.boxes[idx].set_state("idle")
                self._style_com(idx, False)
                self.log_line("%s Removed!!" % self._tag(self.known[name]))
        self.known = current

    def closeEvent(self, event):
        if self.running:
            ans = QMessageBox.question(self, "Odin3", "A gravação está em andamento. Sair mesmo assim?")
            if ans != QMessageBox.Yes:
                event.ignore()
                return
            for proc in list(self.procs.values()):
                proc.kill()
        event.accept()


def main(argv):
    render = None
    if "--render" in argv:
        render = argv[argv.index("--render") + 1]
    app = QApplication(argv[:1])
    app.setApplicationName("odin3-qt")
    app.setDesktopFileName("odin3-qt")
    font = QFont()
    font.setFamilies(["Segoe UI", "Noto Sans", "DejaVu Sans", "Liberation Sans"])
    font.setPixelSize(12)
    app.setFont(font)
    app.setStyle("Fusion")
    app.setStyleSheet(QSS)
    win = MainWindow()
    win.show()
    if render:
        def grab():
            win.grab().save(render)
            app.quit()
        QTimer.singleShot(300, grab)
    return app.exec_()
