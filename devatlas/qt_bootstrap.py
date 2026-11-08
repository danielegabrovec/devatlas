"""Resolve Qt plugins explicitly, including Windows paths containing commas.

Qt's generated qt.conf can interpret an unquoted comma as a string-list separator.
Do not depend on that inferred prefix for either a venv or a frozen distribution.
"""
from pathlib import Path
import PySide6
from PySide6.QtCore import QCoreApplication


def configure_qt_plugins():
    package = Path(PySide6.__file__).resolve().parent
    candidates = [package / "plugins", package / "qt-plugins", package / "Qt" / "plugins"]
    for candidate in candidates:
        if (candidate / "platforms").is_dir():
            QCoreApplication.setLibraryPaths([str(candidate)])
            return


def load_bundled_fonts():
    from PySide6.QtGui import QFontDatabase
    assets = Path(__file__).resolve().parent / "assets"
    for filename in ("Inter.ttf", "JetBrainsMono.ttf"):
        path = assets / filename
        if path.exists():
            QFontDatabase.addApplicationFont(str(path))


def install_italian_translation(app):
    from PySide6.QtCore import QTranslator
    if getattr(app, "devatlas_translator", None) is not None:
        return
    translator = QTranslator(app)
    if translator.load(str(Path(__file__).resolve().parent / "assets/qtbase_it.qm")):
        app.installTranslator(translator)
        app.devatlas_translator = translator

