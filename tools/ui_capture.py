"""Deterministic widget captures and layout checks on the actual Qt application."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from devatlas.qt_bootstrap import configure_qt_plugins
configure_qt_plugins()
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from devatlas.app import MainWindow
from devatlas.catalog import Catalog


def main():
    app = QApplication([])
    suffix = os.environ.get("DEVATLAS_CAPTURE_SUFFIX", "")
    directory = ROOT / ".cache/ui-capture" / (suffix or "default")
    window = MainWindow(Catalog(), directory)
    window.resize(1620, 1000)
    window.sidebar.show()
    window.splitter.setSizes([230, 380, 900])
    window.show()
    output = ROOT / "reports/screenshots" / suffix
    output.mkdir(parents=True, exist_ok=True)
    results = []
    started = time.monotonic()

    def capture(name):
        QTest.qWait(200)
        app.processEvents()
        window.grab().save(str(output / f"{name}.png"))
        results.append({"name": name, "width": window.width(), "height": window.height(), "dpr": window.devicePixelRatioF(),
                        "search_visible": window.search_edit.isVisible(), "reader_visible": window.reader_scroll.isVisible(),
                        "code_blocks": len(window.code_blocks), "theme": app.property("devatlasTheme")})

    def run():
        if time.monotonic() - started > 25:
            print("L'interfaccia non ha completato la preparazione dei risultati per la cattura.", file=sys.stderr)
            window.close()
            app.exit(1)
            return
        if not window.index_ready or window.last_search_request != window.request or window.workers:
            QTimer.singleShot(100, run)
            return
        window.theme_combo.setCurrentIndex(window.theme_combo.findData("light"))
        window.show_welcome()
        capture("01-biblioteca-chiaro")
        candidates = [r for r in window.recipes.values() if r.stack == "pyside6" and not r.project]
        if candidates:
            window.mode_combo.setCurrentIndex(0)
            window.open_recipe(candidates[0].id)
        capture("02-ricetta-chiaro")
        window.theme_combo.setCurrentIndex(window.theme_combo.findData("dark"))
        window.mode_combo.setCurrentIndex(1)
        capture("03-guida-scuro")
        window.resize(960, 600)
        app.processEvents()
        capture("04-finestra-compatta")
        window.close()
        (ROOT / "reports" / ("ui-captures" + ("-" + suffix if suffix else "") + ".json")).write_text(json.dumps(results, indent=2), encoding="utf-8")
        app.quit()
    QTimer.singleShot(400, run)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

