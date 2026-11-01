"""PinLock — extensão do Nautilus para proteger pastas com PIN.

A pasta mantém sempre o mesmo nome. Menu de contexto:
  * pasta comum         -> "Proteger com PIN…"
  * pasta bloqueada     -> "Desbloquear com PIN…" / "Remover proteção por PIN…"
  * pasta desbloqueada  -> "Bloquear pasta" / "Remover proteção por PIN…"
Também no fundo da pasta aberta (clicar no vazio): desbloquear / bloquear.
"""
import os
import shutil
import subprocess
from urllib.parse import unquote, urlparse

import gi

for _v in ("4.1", "4.0", "3.0"):
    try:
        gi.require_version("Nautilus", _v)
        break
    except ValueError:
        continue
from gi.repository import GObject, Nautilus  # noqa: E402

SUFFIX = ".pinlock"
HELPER = shutil.which("pinlock-helper") or os.path.expanduser(
    "~/.local/share/pinlock/pinlock-helper"
)


def _path(file_info):
    if file_info.get_uri_scheme() != "file":
        return None
    return unquote(urlparse(file_info.get_uri()).path).rstrip("/") or "/"


def _hidden_for(path):
    d, n = os.path.split(path)
    return os.path.join(d, "." + n + SUFFIX)


def _is_cipher(path):
    return os.path.isfile(os.path.join(path, "gocryptfs.conf")) and os.path.isfile(
        os.path.join(path, "gocryptfs.diriv")
    )


def _is_internal(path):
    n = os.path.basename(path)
    return n.startswith(".") and (n.endswith(SUFFIX) or ".pinlock-" in n)


def _state(path):
    if os.path.ismount(path):
        return "unlocked" if _is_cipher(_hidden_for(path)) else "mount"
    if _is_cipher(_hidden_for(path)):
        return "stale"
    if _is_cipher(path):
        return "locked"
    return "plain"


def _run(action, path):
    subprocess.Popen([HELPER, action, path], stdin=subprocess.DEVNULL, start_new_session=True)


class PinLockExtension(GObject.GObject, Nautilus.MenuProvider):
    def _item(self, key, label, action, path):
        item = Nautilus.MenuItem(name=f"PinLock::{key}", label=label)
        item.connect("activate", lambda *_: _run(action, path))
        return item

    def _items_for(self, path, background=False):
        if _is_internal(path):
            return []
        st = _state(path)
        sfx = "_bg" if background else ""
        unlock = self._item("unlock" + sfx, "Desbloquear com PIN…", "unlock", path)
        lock = self._item("lock" + sfx, "Bloquear pasta", "lock", path)
        remove = self._item("remove" + sfx, "Remover proteção por PIN…", "remove", path)
        if st == "locked":
            return [unlock] if background else [unlock, remove]
        if st == "unlocked":
            return [lock] if background else [lock, remove]
        if st == "stale":
            return [unlock, lock]
        if st == "plain" and not background:
            return [self._item("protect", "Proteger com PIN…", "protect", path)]
        return []

    # Nautilus 4.x: get_file_items(files) | Nautilus 3.x: get_file_items(window, files)
    def get_file_items(self, *args):
        files = args[-1]
        if len(files) != 1 or not files[0].is_directory():
            return []
        path = _path(files[0])
        return self._items_for(path) if path else []

    def get_background_items(self, *args):
        path = _path(args[-1])
        return self._items_for(path, background=True) if path else []
