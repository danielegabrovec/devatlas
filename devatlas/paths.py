from __future__ import annotations
import os
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def user_directory() -> Path:
    override = os.environ.get("DEVATLAS_DATA_DIR")
    executable = Path(sys.executable).resolve().parent
    if override:
        root = Path(override)
    elif (executable / "portable.flag").exists():
        root = executable / "dati-personali"
    else:
        root = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share"))) / "DevAtlas"
    root.mkdir(parents=True, exist_ok=True)
    return root

