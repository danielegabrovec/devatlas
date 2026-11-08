"""Native library UX: layout, contrast and complete keyboard workflows."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPalette, QDesktopServices
from PySide6.QtWidgets import QApplication, QFileDialog, QInputDialog

from devatlas.app import MainWindow
from devatlas.theme import THEMES, apply_theme, technology_tone
from devatlas.ui_components import wrapped_lines
from test_ui_extended import compact_window, small_catalog

ROOT = Path(__file__).resolve().parents[1]


def ready(window, qtbot):
    qtbot.waitUntil(lambda: window.results_are_current(), timeout=5000)


def ratio(first, second):
    def luminance(value):
        color = QColor(value)
        channels = [color.redF(), color.greenF(), color.blueF()]
        linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
        return sum(a * b for a, b in zip(linear, [.2126, .7152, .0722]))
    a, b = sorted([luminance(first), luminance(second)])
    return (b + .05) / (a + .05)


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_semantic_contrasts_and_opaque_placeholder(compact_window, qtbot, theme):
    w = compact_window
    w.theme_combo.setCurrentIndex(w.theme_combo.findData(theme))
    qtbot.wait(30)
    token = THEMES[theme]
    for fg, bg in (("text", "surface"), ("muted", "raised"), ("accent_text", "selection")):
        assert ratio(token[fg], token[bg]) >= 4.5
    assert ratio(token["scroll_thumb"], token["raised"]) >= 3
    actual = w.search_edit.palette().color(QPalette.ColorRole.PlaceholderText)
    assert actual.alpha() == 255
    assert ratio(actual, token["raised"]) >= 4.5
    for group in ("Linguaggi", "Desktop e GUI", "Web e backend", "Database", "Strumenti"):
        fg, bg = technology_tone(group, theme)
        assert ratio(fg, bg) >= 4.5


def test_card_title_wraps_two_lines_unicode_and_density(compact_window):
    w = compact_window
    font = QFont(QApplication.font())
    text = "Una guida Python ☕ con un titolo lungo che resta leggibile e viene troncato soltanto oltre la seconda riga"
    lines = wrapped_lines(text, font, 180, 2)
    assert len(lines) == 2 and "☕" in " ".join(lines)
    assert all(QFontMetricsF(font).horizontalAdvance(line) <= 181 for line in lines)
    assert "\ufffd" not in "".join(lines)
    from PySide6.QtWidgets import QStyleOptionViewItem
    option = QStyleOptionViewItem()
    before = w.result_delegate.sizeHint(option, w.model.index(0)).height()
    w.change_density("compact")
    assert w.result_delegate.sizeHint(option, w.model.index(0)).height() < before
    assert w.store.setting("density") == "compact"


def test_active_filter_chip_removes_effective_filter_and_is_readable(compact_window, qtbot):
    w = compact_window
    w.selection_filter = {"stack": "fastapi"}
    w.filters["os"].setCurrentIndex(w.filters["os"].findData("Linux"))
    w.schedule_search()
    ready(w, qtbot)
    chip = w.active_chip_buttons["os"]
    assert "Sistema" in chip.text()
    assert chip.width() > 80
    qtbot.mouseClick(chip, Qt.MouseButton.LeftButton)
    ready(w, qtbot)
    assert w.query().os == ""
    assert "stack" in w.active_chip_buttons and "os" not in w.active_chip_buttons
    qtbot.mouseClick(w.active_chip_buttons["stack"], Qt.MouseButton.LeftButton)
    ready(w, qtbot)
    assert w.selection_filter == {}
    assert not w.active_chip_scroll.isVisible()


def test_empty_state_action_resets_search_and_filters(compact_window, qtbot):
    w = compact_window
    w.search_edit.setText("zzzzimpossibilezzzz")
    ready(w, qtbot)
    assert w.results_state == "empty"
    assert w.result_state_panel.button.isVisible()
    qtbot.mouseClick(w.result_state_panel.button, Qt.MouseButton.LeftButton)
    ready(w, qtbot)
    assert w.search_edit.text() == "" and w.model.ids
    assert w.results_state == "results"


def test_enter_opens_latest_query_down_transfers_focus_and_escape_keeps_app(compact_window, qtbot):
    w = compact_window
    w.activateWindow()
    w.search_edit.setFocus()
    w.search_edit.setText("nonpresentezzzz")
    w.search_edit.setText("json")
    qtbot.keyClick(w.search_edit, Qt.Key.Key_Return)
    qtbot.waitUntil(lambda: w.current_recipe is not None and w.results_are_current(), timeout=5000)
    assert w.current_recipe.id == w.model.ids[0]
    w.search_edit.setFocus()
    qtbot.keyClick(w.search_edit, Qt.Key.Key_Down)
    assert w.results_list.hasFocus()
    qtbot.keyClick(w, Qt.Key.Key_Escape)
    assert w.isVisible()


def test_sort_is_forwarded_recent_ids_only_when_needed_and_saved(compact_window, qtbot, monkeypatch):
    w = compact_window
    w.open_recipe("python-copy")
    w.sort_combo.setCurrentIndex(w.sort_combo.findData("recent"))
    assert w.query().sort == "recent" and w.query().recent_ids[0] == "python-copy"
    w.sort_combo.setCurrentIndex(w.sort_combo.findData("title"))
    assert w.query().sort == "title" and w.query().recent_ids is None
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Ordine salvato", True))
    w.save_current_search()
    sid = w.active_saved_search
    w.sort_combo.setCurrentIndex(0)
    w.restore_saved_search(sid)
    assert w.query().sort == "title"


def test_focus_returns_layout_and_restart_does_not_collapse_library(compact_window, qtbot, tmp_path):
    w = compact_window
    w.resize(1280, 800)
    w.open_recipe("python-copy")
    qtbot.wait(30)
    before = w.splitter.sizes()
    w.toggle_focus_mode(True)
    assert not w.sidebar.isVisible() and not w.splitter.widget(1).isVisible()
    assert w.focus_button.isVisible() and w.focus_button.isEnabled()
    w.toggle_focus_mode(False)
    assert w.splitter.widget(1).isVisible()
    w.toggle_focus_mode(True)
    w.close()
    assert all(n > 0 for n in w.store.setting("splitter"))
    assert w.store.setting("panels_visibility")["results"]
    reopened = MainWindow(w.catalog, w.directory)
    qtbot.addWidget(reopened)
    reopened.show()
    assert not reopened.focus_mode and reopened.splitter.widget(1).isVisible()
    reopened.close()


def test_focus_keyboard_escape_and_zoom_compact_layout(compact_window, qtbot):
    w = compact_window
    w.resize(800, 600)
    w.open_recipe("python-copy")
    w.activateWindow()
    qtbot.keyClick(w, Qt.Key.Key_F8)
    assert w.focus_mode
    qtbot.keyClick(w, Qt.Key.Key_Escape)
    assert not w.focus_mode and w.isVisible()
    w.adjust_zoom(5)
    qtbot.wait(60)
    assert w.width() == 800
    for button in (w.export_button, w.focus_button, w.recipe_menu_button):
        assert button.geometry().right() <= button.parentWidget().width()


def test_find_outside_code_preserves_search_across_third_asset(compact_window, qtbot, monkeypatch):
    w = compact_window
    source = deepcopy(w.recipes["python-copy"].data)
    source["id"] = "python-three"
    source["assets"].insert(1, {"id": "second", "role": "file", "path": "second.py", "language": "python", "content": "second_asset = 2\n"})
    source["assets"].insert(2, {"id": "third", "role": "file", "path": "third.py", "language": "python", "content": "only_third_asset = 3\n"})
    from devatlas.models import Recipe
    w.recipes[source["id"]] = Recipe(source)
    w.open_recipe(source["id"])
    w.search_edit.setFocus()
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("only_third_asset", True))
    w.find_in_recipe()
    matched = next(block for block in w.code_blocks if block.asset["id"] == "third")
    assert matched.editor.textCursor().selectedText() == "only_third_asset"


def test_export_destination_opens_only_after_explicit_click(compact_window, qtbot, tmp_path, monkeypatch):
    w = compact_window
    w.open_recipe("python-copy")
    target = tmp_path / "exports"
    target.mkdir()
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: str(target))
    opened = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: opened.append(url.toLocalFile()))
    w.export_current(False)
    assert w.destination_notice.isVisible() and opened == []
    qtbot.mouseClick(w.destination_button, Qt.MouseButton.LeftButton)
    assert len(opened) == 1 and Path(opened[0]) == (target / "python-copy").resolve()


def test_palette_is_bounded_and_registered_with_ctrl_p(compact_window):
    w = compact_window
    commands = w.palette_commands()
    assert len(commands) <= 250 and len({c.id for c in commands}) == len(commands)
    assert w.command_action.shortcut().toString() == "Ctrl+P"
    assert any(c.id == "technology:python" for c in commands)


@pytest.mark.parametrize("width,height", [(1540, 940), (950, 650), (800, 520)])
def test_filters_compact_panel_keeps_controls_reachable(compact_window, qtbot, width, height):
    w = compact_window
    w.resize(width, height)
    qtbot.mouseClick(w.filters_button, Qt.MouseButton.LeftButton)
    qtbot.wait(40)
    assert w.filter_panel.isVisible()
    if width < 1100 or height < 720:
        assert not w.results_stack.isVisible()
    w.filter_panel.ensureWidgetVisible(w.reset_filters_button)
    assert w.reset_filters_button.isVisible()
    qtbot.mouseClick(w.filters_button, Qt.MouseButton.LeftButton)
    assert w.results_stack.isVisible()
    assert w.width() <= width and w.height() <= height


@pytest.mark.parametrize("scale", ["1", "1.5", "2"])
def test_full_native_capture_matrix(scale, tmp_path):
    script = r'''
import sys,json
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root))
from devatlas.qt_bootstrap import configure_qt_plugins
configure_qt_plugins()
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer,QEventLoop
from devatlas.app import MainWindow
from devatlas.catalog import Catalog
app=QApplication([])
w=MainWindow(Catalog(),Path(sys.argv[2]));w.show()
def wait(predicate):
    loop=QEventLoop();poll=QTimer();poll.setInterval(15)
    poll.timeout.connect(lambda:loop.quit() if predicate() else None)
    timeout=QTimer();timeout.setSingleShot(True);timeout.timeout.connect(loop.quit)
    poll.start();timeout.start(15000);loop.exec();poll.stop();timeout.stop()
    assert predicate()
wait(w.results_are_current)
w.search_edit.setText('python json');wait(w.results_are_current)
rid=w.model.ids[0]
output=root/'reports/ui-state/1.3-offscreen';output.mkdir(parents=True,exist_ok=True)
rows=[]
for theme in ('light','dark'):
    w.theme_combo.setCurrentIndex(w.theme_combo.findData(theme))
    for width,height in ((1540,940),(950,650),(800,520)):
        w.resize(width,height)
        w.show_welcome() if width==1540 else w.open_recipe(rid)
        loop=QEventLoop();QTimer.singleShot(80,loop.quit);loop.exec()
        assert w.width()<=width and w.height()<=height
        name=f'library-{theme}-{width}-dpi{sys.argv[3]}.png'
        assert w.grab().save(str(output/name))
        rows.append({'image':name,'width':w.width(),'height':w.height(),'dpr':w.devicePixelRatioF(),'ready':w.results_are_current()})
print(json.dumps(rows));w.close()
'''
    result = subprocess.run([sys.executable, "-c", script, str(ROOT), str(tmp_path / "profile"), scale], cwd=ROOT,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen", "QT_SCALE_FACTOR": scale, "PYTHONIOENCODING": "utf8"},
        capture_output=True, text=True, encoding="utf8", timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    captures = json.loads(result.stdout.strip().splitlines()[-1])
    assert len(captures) == 6 and all(c["dpr"] == pytest.approx(float(scale)) for c in captures)
    assert all(c["ready"] for c in captures)
