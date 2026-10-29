"""Backend: detecção de aparelhos em Download Mode, verificação MD5 e comando odin4."""

import glob
import hashlib
import os
import re
import shutil

from PyQt5.QtCore import QThread, pyqtSignal

SAMSUNG_VID = "04e8"
DOWNLOAD_PIDS = {"685d", "6601"}  # Samsung em Download Mode
SYS_USB = "/sys/bus/usb/devices"
MAX_SLOTS = 8


def _read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return ""


def scan_devices():
    """Lista aparelhos Samsung em Download Mode via sysfs (sem dependências)."""
    found = []
    for d in sorted(glob.glob(os.path.join(SYS_USB, "*"))):
        if _read(d + "/idVendor").lower() != SAMSUNG_VID:
            continue
        if _read(d + "/idProduct").lower() not in DOWNLOAD_PIDS:
            continue
        try:
            bus = int(_read(d + "/busnum"))
            dev = int(_read(d + "/devnum"))
        except ValueError:
            continue
        found.append({
            "name": os.path.basename(d),
            "bus": bus,
            "dev": dev,
            "path": "/dev/bus/usb/%03d/%03d" % (bus, dev),
        })
    return found[:MAX_SLOTS]


def find_odin4():
    """Procura o binário odin4 (Samsung) no sistema."""
    env = os.environ.get("ODIN4")
    if env and os.access(env, os.X_OK):
        return env
    found = shutil.which("odin4")
    if found:
        return found
    for cand in ("/usr/local/bin/odin4", "/opt/odin4/odin4", "/usr/bin/odin4",
                 os.path.expanduser("~/.local/bin/odin4")):
        if os.access(cand, os.X_OK):
            return cand
    return None


def build_args(odin4, files, device_path, erase=False, reboot=True):
    flags = {"BL": "-b", "AP": "-a", "CP": "-c", "CSC": "-s", "USERDATA": "-u"}
    args = [odin4]
    for key in ("BL", "AP", "CP", "CSC", "USERDATA"):
        if key in files:
            args += [flags[key], files[key]]
    if erase:
        args.append("-e")
    if reboot:
        args.append("--reboot")
    args += ["-d", device_path]
    return args


def check_tar_md5(path, progress=None):
    """Valida um .tar.md5 da Samsung (hash na última linha do arquivo).

    Retorna True/False, ou None se o arquivo não tiver hash embutido.
    """
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        f.seek(max(0, size - 512))
        tail = f.read()
        # O rodapé "<md5>  <nome>.tar\n" vem colado ao fim do tar, sem \n antes dele.
        m = re.search(rb"([0-9a-fA-F]{32})[ \t]+\*?[^\r\n]+\r?\n?$", tail)
        if not m:
            return None
        body_len = size - len(tail) + m.start()
        md5 = hashlib.md5()
        f.seek(0)
        left = body_len
        while left > 0:
            chunk = f.read(min(1 << 20, left))
            if not chunk:
                break
            md5.update(chunk)
            left -= len(chunk)
            if progress:
                progress(int(100 * (body_len - left) / max(1, body_len)))
    return md5.hexdigest().lower() == m.group(1).decode().lower()


class Md5Worker(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished_ok = pyqtSignal(bool)

    def __init__(self, paths, parent=None):
        super().__init__(parent)
        self.paths = paths

    def run(self):
        self.log.emit("<OSM> Enter CS for MD5..")
        self.log.emit("<OSM> Check MD5.. Do not unplug the cable..")
        self.log.emit("<OSM> Please wait..")
        ok = True
        for p in self.paths:
            name = os.path.basename(p)
            if not p.lower().endswith(".md5"):
                self.log.emit("<OSM> %s has no MD5 hash, skipping check." % name)
                continue
            try:
                res = check_tar_md5(p, self.progress.emit)
            except OSError as exc:
                self.log.emit("<OSM> %s: %s" % (name, exc))
                ok = False
                break
            if res is None:
                self.log.emit("<OSM> %s has no MD5 hash, skipping check." % name)
            elif res:
                self.log.emit("<OSM> %s is valid." % name)
            else:
                self.log.emit("<OSM> %s is invalid." % name)
                ok = False
                break
        if ok:
            self.log.emit("<OSM> Checking MD5 finished successfully..")
        else:
            self.log.emit("<OSM> MD5 error!! Aborting.")
        self.log.emit("<OSM> Leave CS..")
        self.finished_ok.emit(ok)
