"""Janela principal - réplica do layout do Odin3 v3.14 em PyQt5.

As coordenadas abaixo foram medidas na captura de tela original (872x649,
com 31px de barra de título que no Linux fica por conta do gerenciador de janelas).
"""

import os
import re
import sys
import shutil

from PyQt5.QtCore import QProcess, QRect, Qt, QTimer, QSettings
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (QApplication, QCheckBox, QFileDialog, QLabel, QLineEdit,
                             QMessageBox, QPlainTextEdit, QPushButton, QTabWidget, QWidget,
                             QGroupBox, QComboBox)

from . import __version__, backend
from .banner import Banner
from .widgets import SlotBar, SlotBox

IMG_DIR = os.environ.get("ODIN3_QT_IMAGES", "/usr/share/odin3-qt/images")
BG = "#f0f0f0"
FILE_FILTER = ("Odin Files (*.tar *.tar.md5 *.md5 *.bin *.img *.lz4 *.zip);;"
               "All Files (*)")

ROWS = [("BL", 321), ("AP", 356), ("CP", 392), ("CSC", 428), ("USERDATA", 465)]

APP_LANG = "pt"
TRANSLATIONS = {
    "pt": {
        "No device connected": "Nenhum dispositivo conectado", "Choose device image": "Escolha a foto do dispositivo",
        "Fetch device info": "Buscar dados do dispositivo", "Choose image…": "Escolher imagem…",
        "Waiting for device": "Aguardando dispositivo", "Connected device": "Dispositivo conectado",
        "Auto Reboot": "Reinício automático", "Re-Partition": "Reparticionar",
        "F. Reset Time": "Redefinir tempo F.", "Nand Erase All": "Apagar NAND",
        "Options": "Opções", "Tips - How to download HOME binary": "Dicas - Como baixar o HOME binary",
        "OLD model : Download one binary  (BUILD_VER)_XXX_HOME.tar.md5": "Modelo antigo: baixe um binary (BUILD_VER)_XXX_HOME.tar.md5",
        "NEW model : Download BL + AP + CP + HOME_CSC": "Modelo novo: baixe BL + AP + CP + HOME_CSC",
        "ADB / RECOVERY ACTIONS": "AÇÕES ADB / RECOVERY",
        "Requires an authorized Android or recovery session.": "Requer uma sessão Android ou recovery autorizada.",
        "List devices": "Listar dispositivos", "Reboot recovery": "Reiniciar em recovery",
        "Reboot download": "Reiniciar em download", "ADB sideload…": "ADB sideload…",
        "Push ROM / ZIP…": "Enviar ROM / ZIP…", "Reboot system": "Reiniciar sistema",
        "Mass D/L ?": "Download em massa?", "Start": "Iniciar", "Reset": "Redefinir", "Exit": "Sair",
        "Language": "Idioma", "English": "Inglês", "Português": "Português", "Español": "Espanhol",
        "No device": "Nenhum dispositivo", "Connected": "Conectado",
        "No device connected": "Nenhum dispositivo conectado",
        "Devices connected: %d": "Dispositivos conectados: %d",
        "Samsung Download Mode · USB device %s": "Samsung em Download Mode · dispositivo USB %s",
        "ADB unauthorized · unlock the phone and accept the USB debugging prompt": "ADB não autorizado · desbloqueie o telefone e aceite o aviso de depuração USB",
        "No authorized ADB device · Download Mode is detected through Odin USB": "Nenhum dispositivo ADB autorizado · o Download Mode é detectado pelo USB do Odin",
        "Android device connected · model property is unavailable": "Dispositivo Android conectado · modelo indisponível",
        "ADB unavailable · install platform-tools to fetch device details": "ADB indisponível · instale platform-tools para buscar os dados",
        "ADB scan: ": "Busca ADB: ", "Android device · ": "Dispositivo Android · ",
        "Only informational in this version.": "Apenas informativo nesta versão.",
        "PIT/Re-Partition is not supported by the odin4 backend.": "PIT/Re-Partition não é compatível com o backend odin4.",
        "Passes -e to odin4 and erases NAND.": "Repassa -e ao odin4 e apaga a NAND.",
        "Choose device image": "Escolher imagem do dispositivo", "Select ROM / recovery package": "Selecionar pacote ROM / recovery",
        "Select file to push": "Selecionar arquivo para enviar", "Open": "Abrir",
        "The flash is in progress. Exit anyway?": "A gravação está em andamento. Sair mesmo assim?",
        "Re-Partition (PIT) is not supported by the odin4 backend. Uncheck the option to continue.": "Re-Partition (PIT) não é compatível com o backend odin4. Desmarque a opção para continuar.",
        "The 'odin4' binary was not found.\n\nInstall odin4 in /usr/local/bin or set the ODIN4 environment variable.": "O binário 'odin4' não foi encontrado.\n\nInstale o odin4 em /usr/local/bin ou defina a variável de ambiente ODIN4.",
        "Connect a Samsung device in Download Mode.": "Conecte um dispositivo Samsung em Download Mode.",
        "No file selected.": "Nenhum arquivo selecionado.", "No device connected. Put the phone in Download Mode first.": "Nenhum dispositivo conectado. Coloque o telefone em Download Mode.",
        "The Start button flashes all detected devices in parallel (up to 8 slots).\nConnect devices in Download Mode and press Start.": "O botão Iniciar grava em paralelo todos os dispositivos detectados (até 8 slots).\nConecte os dispositivos em Download Mode e pressione Iniciar.",
    },
    "es": {
        "No device connected": "Ningún dispositivo conectado", "Choose device image": "Elige la foto del dispositivo",
        "Fetch device info": "Obtener datos del dispositivo", "Choose image…": "Elegir imagen…",
        "Waiting for device": "Esperando dispositivo", "Connected device": "Dispositivo conectado",
        "Auto Reboot": "Reinicio automático", "Re-Partition": "Reparticionar",
        "F. Reset Time": "Restablecer tiempo F.", "Nand Erase All": "Borrar NAND",
        "Options": "Opciones", "Tips - How to download HOME binary": "Consejos - Cómo descargar HOME binary",
        "OLD model : Download one binary  (BUILD_VER)_XXX_HOME.tar.md5": "Modelo antiguo: descarga un binary (BUILD_VER)_XXX_HOME.tar.md5",
        "NEW model : Download BL + AP + CP + HOME_CSC": "Modelo nuevo: descarga BL + AP + CP + HOME_CSC",
        "ADB / RECOVERY ACTIONS": "ACCIONES ADB / RECOVERY",
        "Requires an authorized Android or recovery session.": "Requiere una sesión Android o recovery autorizada.",
        "List devices": "Listar dispositivos", "Reboot recovery": "Reiniciar en recovery",
        "Reboot download": "Reiniciar en download", "ADB sideload…": "ADB sideload…",
        "Push ROM / ZIP…": "Enviar ROM / ZIP…", "Reboot system": "Reiniciar sistema",
        "Mass D/L ?": "Descarga masiva?", "Start": "Iniciar", "Reset": "Restablecer", "Exit": "Salir",
        "Language": "Idioma", "English": "Inglés", "Português": "Portugués", "Español": "Español",
        "No device": "Sin dispositivo", "Connected": "Conectado",
        "No device connected": "Ningún dispositivo conectado",
        "Devices connected: %d": "Dispositivos conectados: %d",
        "Samsung Download Mode · USB device %s": "Samsung en Download Mode · dispositivo USB %s",
        "ADB unauthorized · unlock the phone and accept the USB debugging prompt": "ADB no autorizado · desbloquea el teléfono y acepta el aviso de depuración USB",
        "No authorized ADB device · Download Mode is detected through Odin USB": "No hay dispositivo ADB autorizado · Odin detecta Download Mode por USB",
        "Android device connected · model property is unavailable": "Dispositivo Android conectado · modelo no disponible",
        "ADB unavailable · install platform-tools to fetch device details": "ADB no disponible · instala platform-tools para obtener los datos",
        "ADB scan: ": "Búsqueda ADB: ", "Android device · ": "Dispositivo Android · ",
        "Only informational in this version.": "Solo informativo en esta versión.",
        "PIT/Re-Partition is not supported by the odin4 backend.": "El backend odin4 no admite PIT/Re-Partition.",
        "Passes -e to odin4 and erases NAND.": "Pasa -e a odin4 y borra la NAND.",
        "Choose device image": "Elegir imagen del dispositivo", "Select ROM / recovery package": "Seleccionar paquete ROM / recovery",
        "Select file to push": "Seleccionar archivo para enviar", "Open": "Abrir",
        "The flash is in progress. Exit anyway?": "El flasheo está en curso. ¿Salir de todos modos?",
        "Re-Partition (PIT) is not supported by the odin4 backend. Uncheck the option to continue.": "El backend odin4 no admite Re-Partition (PIT). Desmarca la opción para continuar.",
        "The 'odin4' binary was not found.\n\nInstall odin4 in /usr/local/bin or set the ODIN4 environment variable.": "No se encontró el binario 'odin4'.\n\nInstala odin4 en /usr/local/bin o define la variable de entorno ODIN4.",
        "Connect a Samsung device in Download Mode.": "Conecta un dispositivo Samsung en Download Mode.",
        "No file selected.": "No se seleccionó ningún archivo.", "No device connected. Put the phone in Download Mode first.": "No hay dispositivo conectado. Primero pon el teléfono en Download Mode.",
        "The Start button flashes all detected devices in parallel (up to 8 slots).\nConnect devices in Download Mode and press Start.": "El botón Iniciar flashea en paralelo todos los dispositivos detectados (hasta 8 slots).\nConecta los dispositivos en Download Mode y pulsa Iniciar.",
    },
    "en": {},
}


def tr(text, language=None):
    return TRANSLATIONS.get(language or APP_LANG, {}).get(text, text)

QSS = """
* { font-size: 12px; color: #111; }
QWidget#main { background: %(bg)s; }
QGroupBox { background: #f0f0f0; border: 1px solid #c8c8c8; margin-top: 10px; padding: 8px; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; color: #333; }
QPushButton { background: #e9e9e9; border: 1px solid #aaa; border-radius: 0; padding: 3px 8px; color: #111; }
QPushButton:hover { background: #e5f1fb; border-color: #0078d7; }
QPushButton:pressed { background: #cce4f7; }
QPushButton:disabled { background: #ddd; color: #888; }
QPushButton[primary="true"] { border: 1px solid #0078d7; }
QLineEdit, QComboBox { background: #f7f7f7; border: 1px solid #888; border-radius: 0; padding: 3px 5px; color: #111; }
QCheckBox { spacing: 5px; color: #111; }
QCheckBox::indicator { width: 13px; height: 13px; border: 1px solid #333; background: #fff; }
QCheckBox::indicator:checked { background: #1683d8; }
QTabWidget::pane { border: 1px solid #c8c8c8; background: #f0f0f0; top: -1px; }
QTabBar::tab { background: #f0f0f0; border: 1px solid #c8c8c8; border-bottom: none; padding: 3px 9px; margin-right: -1px; }
QTabBar::tab:selected { background: #fff; }
QPlainTextEdit { background: #fff; border: 1px solid #888; padding: 3px; color: #111; font-family: 'DejaVu Sans Mono'; font-size: 11px; }
QScrollBar:vertical { background: #f0f0f0; width: 15px; margin: 0; }
QScrollBar::handle:vertical { background: #ccc; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QToolTip { background: #fff; border: 1px solid #888; color: #111; }
""" % {"bg": BG, "img": IMG_DIR}


def place(widget, x, y, w, h):
    widget.setGeometry(x, y, w, h)
    if isinstance(widget, (QLabel, QPushButton, QCheckBox)):
        source = widget.text()
        widget.setProperty("_i18n_source", source)
        widget.setText(tr(source))
    elif isinstance(widget, QGroupBox):
        source = widget.title()
        widget.setProperty("_i18n_source", source)
        widget.setTitle(tr(source))
    return widget


class MainWindow(QWidget):
    def __init__(self):
        global APP_LANG
        super().__init__()
        APP_LANG = QSettings("Odin3Qt", "Odin3Qt").value("language", "pt")
        self.setObjectName("main")
        self.setWindowTitle("Odin3 v%s" % __version__)
        self.setMinimumSize(1100, 800)
        self.resize(1120, 830)
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
        self._build_buttons()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_devices)
        self.timer.start(1000)
        self.poll_devices()

    # ------------------------------------------------------------------ UI
    def _build_banner_and_slots(self):
        # The reference layout is a narrow banner followed by eight Odin status slots.
        place(Banner(self), 14, 8, 856, 71)
        self.boxes, self.bars, self.coms = [], [], []
        for i in range(backend.MAX_SLOTS):
            x = 22 + i * 135
            self.boxes.append(place(SlotBox(self), x, 91, 128, 62))
            self.bars.append(place(SlotBar(self), x, 159, 128, 20))
            com = QLabel("", self)
            com.setAlignment(Qt.AlignCenter)
            place(com, x, 215, 128, 21)
            self.coms.append(com)
            self._style_com(i, False)
        place(QLabel("ID:COM", self), 20, 195, 52, 17)
        self.language_label = QLabel("Language", self)
        place(self.language_label, 885, 12, 60, 25)
        self.language_box = QComboBox(self)
        for label, lang in (("Português", "pt"), ("Español", "es"), ("English", "en")):
            self.language_box.addItem(label, lang)
        self.language_box.setCurrentIndex(max(0, self.language_box.findData(APP_LANG)))
        place(self.language_box, 945, 10, 145, 28)
        self.language_box.currentIndexChanged.connect(self.set_language)
        self.header_status = QLabel("No device connected", self)
        self.header_status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.header_status.setStyleSheet("color:#666;background:#f7f7f7;border:1px solid #ccc;padding:3px")
        place(self.header_status, 885, 50, 205, 20)

    def _style_com(self, i, connected, text=""):
        color = "#13823b" if connected else "#777"
        bg = "#bfe7fb" if connected else "#e1e1e1"
        self.coms[i].setStyleSheet("background:%s;color:%s;border:1px solid #ccc" % (bg, color))
        self.coms[i].setText(text or ("%d:[COM%d]" % (i, i + 1) if connected else ""))

    def _build_log_tabs(self):
        # Device preview sits slightly right of the Odin log, like the requested
        # earlier composition, while firmware slots stay aligned on the right.
        self.device_card = QGroupBox("Connected device", self)
        place(self.device_card, 22, 255, 313, 210)
        self.device_art = QLabel(self.device_card)
        self.device_art.setAlignment(Qt.AlignCenter)
        self.device_art.setStyleSheet("background:#f7f7f7;border:1px solid #c3c3c3;color:#666")
        self.device_art.setText("Choose device image")
        place(self.device_art, 12, 24, 126, 132)
        self.btn_fetch = QPushButton("Fetch device info", self.device_card)
        place(self.btn_fetch, 148, 37, 147, 30)
        self.btn_fetch.clicked.connect(self.fetch_device_info)
        self.btn_image = QPushButton("Choose image…", self.device_card)
        place(self.btn_image, 148, 76, 147, 30)
        self.btn_image.clicked.connect(self.choose_device_image)
        self.device_info = QLabel("Waiting for device", self.device_card)
        self.device_info.setWordWrap(True)
        place(self.device_info, 12, 164, 283, 32)

        self.tabs = QTabWidget(self)
        place(self.tabs, 22, 474, 313, 278)
        self.tabs.tabBar().setExpanding(False)
        log_page = QWidget()
        self.log = QPlainTextEdit(log_page)
        self.log.setReadOnly(True)
        self.log.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        place(self.log, 5, 6, 302, 235)
        self.tabs.addTab(log_page, tr("Log"))
        options_page = QWidget()
        self.opt_auto = QCheckBox("Auto Reboot", options_page); self.opt_auto.setChecked(True)
        self.opt_repart = QCheckBox("Re-Partition", options_page)
        self.opt_freset = QCheckBox("F. Reset Time", options_page); self.opt_freset.setChecked(True)
        self.opt_erase = QCheckBox("Nand Erase All", options_page)
        for i, cb in enumerate((self.opt_auto, self.opt_repart, self.opt_freset, self.opt_erase)):
            place(cb, 14, 18 + i * 28, 210, 22)
        self.opt_freset.setToolTip(tr("Only informational in this version."))
        self.opt_repart.setToolTip(tr("PIT/Re-Partition is not supported by the odin4 backend."))
        self.opt_erase.setToolTip(tr("Passes -e to odin4 and erases NAND."))
        self.tabs.addTab(options_page, tr("Options"))
        pit_page = QWidget()
        pit_btn = QPushButton("PIT", pit_page); place(pit_btn, 12, 15, 70, 25)
        self.pit_field = QLineEdit(pit_page); self.pit_field.setReadOnly(True)
        place(self.pit_field, 90, 14, 204, 27)
        pit_btn.clicked.connect(lambda: self._pick(self.pit_field, None))
        self.tabs.addTab(pit_page, tr("Pit"))
        adb_page = QWidget()
        self._build_adb_panel(adb_page)
        self.tabs.addTab(adb_page, tr("ADB"))
        self._tab_sources = ["Log", "Options", "Pit", "ADB"]
        self.log_line("<OSM> Odin3 Qt v%s ready. %s" % (__version__, tr("Connect a Samsung device in Download Mode.")))

        # Original Odin tips block and five firmware rows on the right.
        place(QLabel("Tips - How to download HOME binary", self), 350, 242, 340, 16)
        for text, y in (("OLD model : Download one binary  (BUILD_VER)_XXX_HOME.tar.md5", 261),
                        ("NEW model : Download BL + AP + CP + HOME_CSC", 281)):
            place(QLabel(text, self), 388, y, 660, 17)
        self.rows = {}
        for i, name in enumerate(("BL", "AP", "CP", "CSC", "USERDATA")):
            y = 321 + i * 45
            cb = QCheckBox(self); place(cb, 360, y + 8, 18, 18)
            btn = QPushButton(name, self); place(btn, 388, y, 108, 34)
            field = QLineEdit(self); field.setReadOnly(True)
            place(field, 506, y, 572, 34)
            btn.clicked.connect(lambda _=False, f=field, c=cb: self._pick(f, c))
            self.rows[name] = (cb, field)

    def _build_adb_panel(self, page):
        place(QLabel("ADB / RECOVERY ACTIONS", page), 12, 12, 240, 20)
        place(QLabel("Requires an authorized Android or recovery session.", page), 12, 38, 270, 36)
        buttons = [("List devices", self.adb_list), ("Reboot recovery", lambda: self.adb_run(["reboot", "recovery"])),
                   ("Reboot download", lambda: self.adb_run(["reboot", "download"])),
                   ("ADB sideload…", self.adb_sideload), ("Push ROM / ZIP…", self.adb_push),
                   ("Reboot system", lambda: self.adb_run(["reboot"]))]
        for i, (label, callback) in enumerate(buttons):
            btn = QPushButton(label, page)
            place(btn, 12 + (i % 2) * 145, 91 + (i // 2) * 46, 135, 32)
            btn.clicked.connect(callback)

    def set_language(self, index):
        global APP_LANG
        APP_LANG = self.language_box.itemData(index) or "pt"
        for widget in self.findChildren(QWidget):
            source = widget.property("_i18n_source")
            if source is not None:
                if widget is self.device_art and not widget.pixmap().isNull():
                    continue
                suffix = widget.property("_i18n_suffix") or ""
                rendered = tr(source)
                rendered = rendered % suffix if "%s" in rendered else rendered + suffix
                if hasattr(widget, "setText"):
                    widget.setText(rendered)
                elif hasattr(widget, "setTitle"):
                    widget.setTitle(rendered)
        for tab_index, source in enumerate(getattr(self, "_tab_sources", [])):
            self.tabs.setTabText(tab_index, tr(source))
        self.language_label.setText(tr("Language"))
        self.header_status.setText("●  " + (tr("Devices connected: %d") % len(self.known)) if self.known
                                   else "●  " + tr("No device connected"))
        self.opt_freset.setToolTip(tr("Only informational in this version."))
        self.opt_repart.setToolTip(tr("PIT/Re-Partition is not supported by the odin4 backend."))
        self.opt_erase.setToolTip(tr("Passes -e to odin4 and erases NAND."))
        QSettings("Odin3Qt", "Odin3Qt").setValue("language", APP_LANG)

    def _build_buttons(self):
        mass = QPushButton("Mass D/L ?", self)
        place(mass, 967, 707, 111, 31)
        mass.clicked.connect(self.on_mass)
        self.btn_start = QPushButton("Start", self)
        place(self.btn_start, 588, 758, 154, 38)
        self.btn_reset = QPushButton("Reset", self)
        place(self.btn_reset, 754, 758, 154, 38)
        self.btn_exit = QPushButton("Exit", self)
        place(self.btn_exit, 924, 758, 154, 38)
        self.btn_start.clicked.connect(self.on_start)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_exit.clicked.connect(self.close)

    def set_device_info(self, source, suffix=""):
        self.device_info.setProperty("_i18n_source", source)
        self.device_info.setProperty("_i18n_suffix", suffix)
        rendered = tr(source)
        self.device_info.setText(rendered % suffix if "%s" in rendered else rendered + suffix)

    def choose_device_image(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("Choose device image"), os.path.expanduser("~"), "Images (*.png *.jpg *.jpeg *.webp)")
        if path:
            pix = QPixmap(path)
            if not pix.isNull():
                self.device_art.setPixmap(pix.scaled(self.device_art.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.device_art.setText("")

    def fetch_device_info(self):
        adb = shutil.which("adb")
        if not adb:
            self.log_line("<ADB> adb not found. Install Android platform-tools to fetch device details.")
            self.set_device_info("ADB unavailable · install platform-tools to fetch device details")
            return
        self.adb_run(["devices", "-l"], fetch="devices")

    def adb_list(self):
        adb = shutil.which("adb")
        if not adb:
            self.log_line("<ADB> adb not found. Install Android platform-tools.")
            return
        self.adb_process = QProcess(self)
        self.adb_process.setProcessChannelMode(QProcess.MergedChannels)
        self.adb_process.readyRead.connect(lambda: self.log_line("<ADB> " + bytes(self.adb_process.readAll()).decode("utf-8", "replace").strip()))
        self.adb_process.start(adb, ["devices", "-l"])

    def adb_run(self, args, fetch=False):
        adb = shutil.which("adb")
        if not adb:
            self.log_line("<ADB> adb not found. Install Android platform-tools.")
            return
        self.adb_process = QProcess(self)
        proc = self.adb_process
        if fetch:
            self._adb_capture = ""
        proc.setProcessChannelMode(QProcess.MergedChannels)
        proc.readyRead.connect(lambda p=proc, f=fetch: self._adb_output(p, f))
        proc.finished.connect(lambda code, _status, f=fetch: self._adb_finished(code, f))
        proc.start(adb, args)
        self.log_line("<ADB> adb " + " ".join(args))

    def _adb_output(self, proc, fetch):
        out = bytes(proc.readAll()).decode("utf-8", "replace").strip()
        if out:
            if fetch:
                self._adb_capture = getattr(self, "_adb_capture", "") + out + "\n"
            self.log_line("<ADB> " + out)
            if fetch == "devices":
                self.set_device_info("ADB scan: ", out.replace("\n", " · ")[:150])
            elif fetch == "model":
                self.set_device_info("Android device · ", out.replace("\n", " · ")[:160])

    def _adb_finished(self, code, fetch):
        if not fetch:
            return
        if fetch == "devices":
            states = [line.split()[1] for line in getattr(self, "_adb_capture", "").splitlines()
                      if len(line.split()) > 1 and not line.startswith("List of")]
            if "device" in states and code == 0:
                self.adb_run(["shell", "getprop", "ro.product.model"], fetch="model")
            elif "unauthorized" in states:
                self.set_device_info("ADB unauthorized · unlock the phone and accept the USB debugging prompt")
            else:
                self.set_device_info("No authorized ADB device · Download Mode is detected through Odin USB")
        elif fetch == "model" and code == 0 and not getattr(self, "_adb_capture", "").strip():
            self.set_device_info("Android device connected · model property is unavailable")

    def adb_sideload(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("Select ROM / recovery package"), os.path.expanduser("~"), "ZIP packages (*.zip);;All Files (*)")
        if path:
            self.adb_run(["sideload", path])

    def adb_push(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("Select file to push"), os.path.expanduser("~"), "Packages (*.zip *.img);;All Files (*)")
        if path:
            self.adb_run(["push", path, "/sdcard/Download/" + os.path.basename(path)])

    # ----------------------------------------------------------------- log
    def log_line(self, text):
        self.log.appendPlainText(text)
        sb = self.log.verticalScrollBar()
        sb.setValue(sb.maximum())

    # -------------------------------------------------------------- actions
    def _pick(self, field, checkbox):
        path, _ = QFileDialog.getOpenFileName(self, tr("Open"), os.path.expanduser("~"), FILE_FILTER)
        if path:
            field.setText(path)
            field.setCursorPosition(0)
            if checkbox is not None:
                checkbox.setChecked(True)

    def on_mass(self):
        QMessageBox.information(
            self, "Mass D/L",
            tr("The Start button flashes all detected devices in parallel (up to 8 slots).\n"
               "Connect devices in Download Mode and press Start."))

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
            self.log_line("<OSM> " + tr("No file selected."))
            return
        if not self.known:
            self.log_line("<OSM> " + tr("No device connected. Put the phone in Download Mode first."))
            return
        for path in files.values():
            if not os.path.isfile(path):
                self.log_line("<OSM> File not found: %s" % path)
                return
        if self.opt_repart.isChecked():
            QMessageBox.warning(self, "Odin3", tr("Re-Partition (PIT) is not supported by the odin4 backend. Uncheck the option to continue."))
            return
        self.odin4 = backend.find_odin4()
        if not self.odin4:
            self.log_line("<OSM> odin4 binary not found (set ODIN4=/path/to/odin4 or put it in PATH).")
            QMessageBox.critical(self, "Odin3", tr("The 'odin4' binary was not found.\n\nInstall odin4 in /usr/local/bin or set the ODIN4 environment variable."))
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
        if current:
            self.header_status.setText("●  " + (tr("Devices connected: %d") % len(current)))
            self.header_status.setStyleSheet("color:#12638a;background:#e4f5ff;border:1px solid #8abbd6;padding:3px")
            first = next(iter(current.values()))
            self.set_device_info("Samsung Download Mode · USB device %s", first["name"])
        else:
            self.header_status.setText("●  " + tr("No device connected"))
            self.header_status.setStyleSheet("color:#666;background:#f7f7f7;border:1px solid #ccc;padding:3px")

    def closeEvent(self, event):
        if self.running:
            ans = QMessageBox.question(self, "Odin3", tr("The flash is in progress. Exit anyway?"))
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
