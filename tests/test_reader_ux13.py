import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QTextCursor
from PySide6.QtWidgets import QApplication, QDialog, QInputDialog, QMessageBox, QPushButton, QVBoxLayout, QWidget

from devatlas.app import MainWindow
from devatlas.catalog import Catalog
from devatlas.codewidgets import (CodeBlock, CodeEditor, ComparisonDialog, color_contrast,
                                  readable_token, source_selection)
from devatlas.editor import RecipeEditor, language_for_path
from devatlas.models import Recipe
from devatlas.theme import apply_theme
from test_core import sample

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def clean_wrap_cache(qapp, monkeypatch):
    qapp.setProperty("devatlasCodeWrap", {})
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Discard)
    yield
    qapp.setProperty("devatlasCodeWrap", {})


def block(qtbot, text="alpha beta\nAlpha gamma\nalpha end\n", language="text"):
    widget = CodeBlock({"path": "src/main.txt", "content": text, "role": "file", "language": language})
    qtbot.addWidget(widget)
    widget.resize(650, widget.minimumHeight())
    widget.show()
    return widget


def test_local_find_counts_wraps_and_respects_case_without_changing_source(qtbot):
    widget = block(qtbot)
    original = widget.asset["content"]
    widget.show_find()
    find = widget.find_bar
    find.search_edit.setText("alpha")
    assert find.count_label.text() == "1/3"
    assert widget.editor.textCursor().selectionStart() == 0
    find.find_next()
    assert find.count_label.text() == "2/3"
    find.find_next(True)
    assert find.count_label.text() == "1/3"
    find.find_next(True)
    assert find.count_label.text() == "3/3"
    find.case_button.setChecked(True)
    assert find.count_label.text() == "1/2"
    find.search_edit.setText("not present")
    assert find.count_label.text() == "Nessun risultato"
    assert not find.next_button.isEnabled()
    assert not widget.editor.textCursor().hasSelection()
    assert widget.asset["content"] == original
    assert widget.editor.toPlainText() == original


def test_find_is_literal_for_api_symbols_and_large_match_counts(qtbot):
    widget = block(qtbot, "std::vector<T> [x].*\n" * 1100)
    widget.show_find()
    widget.find_bar.search_edit.setText("[x].*")
    assert widget.find_bar.count_label.text() == "1000+ risultati"
    for _ in range(3):widget.find_bar.find_next()
    assert widget.editor.textCursor().selectedText() == "[x].*"


def test_copy_all_selection_and_keyboard_preserve_crlf_unicode_and_no_line_numbers(qtbot):
    original = "ab\r\n😀x\r\nz\u00a0fine\n"
    widget = block(qtbot, original)
    widget.editor.selectAll()
    qtbot.mouseClick(widget.selection_button, Qt.MouseButton.LeftButton)
    assert QApplication.clipboard().text() == original
    cursor = widget.editor.textCursor()
    cursor.setPosition(3)
    cursor.setPosition(6, QTextCursor.MoveMode.KeepAnchor)
    widget.editor.setTextCursor(cursor)
    assert source_selection(original, cursor) == "😀x"
    qtbot.keyClick(widget.editor, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
    assert QApplication.clipboard().text() == "😀x"
    qtbot.mouseClick(widget.copy_button, Qt.MouseButton.LeftButton)
    assert QApplication.clipboard().text() == original
    assert widget.copy_button.text() == "Copiato"
    assert widget.copy_button.accessibleName() == "Codice copiato"
    assert widget.copy_timer.parent() is widget
    widget.reset_copy_feedback()
    assert widget.copy_button.text() == "Copia"
    assert widget.copy_button.accessibleName().startswith("Copia src/")


def test_invalid_parameter_copy_gate_also_blocks_selection_and_ctrl_c(qtbot):
    widget = block(qtbot)
    widget.editor.selectAll()
    widget.copy_button.setEnabled(False)
    assert not widget.selection_button.isEnabled()
    QApplication.clipboard().setText("keep clipboard")
    widget.editor.copy()
    widget.copy()
    qtbot.keyClick(widget.editor, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
    assert QApplication.clipboard().text() == "keep clipboard"


def test_readonly_code_does_not_trap_tab_keyboard_navigation(qtbot):
    frame = QWidget()
    layout = QVBoxLayout(frame)
    editor = CodeEditor("original text")
    next_button = QPushButton("Passo successivo")
    layout.addWidget(editor)
    layout.addWidget(next_button)
    qtbot.addWidget(frame)
    frame.show()
    editor.setFocus()
    qtbot.waitUntil(lambda: QApplication.focusWidget() is editor)
    qtbot.keyClick(editor, Qt.Key.Key_Tab)
    assert QApplication.focusWidget() is next_button
    assert editor.toPlainText() == "original text"


def test_wrap_is_remembered_and_long_block_height_tracks_zoom_and_find(qtbot):
    original = "long_api_call(" + "argument, " * 80 + ")\n" + "line\n" * 80
    widget = block(qtbot, original)
    collapsed = widget.editor.height()
    widget.toggle_expanded()
    qtbot.waitUntil(lambda: widget.editor.height() > collapsed)
    expanded = widget.editor.height()
    widget.editor.zoomIn(2)
    qtbot.waitUntil(lambda: widget.editor.height() >= expanded)
    assert widget.editor.numbers.width() == widget.editor.number_width()
    widget.wrap_button.setChecked(True)
    assert widget.editor.lineWrapMode() == CodeEditor.LineWrapMode.WidgetWidth
    other = block(qtbot, original)
    assert other.wrap_button.isChecked()
    widget.show_find()
    qtbot.wait(30)
    assert widget.minimumHeight() >= widget.editor.height() + widget.find_bar.height()
    assert widget.asset["content"] == original


def test_ctrl_f_inside_mainwindow_opens_local_bar_before_window_shortcut(qtbot, tmp_path, monkeypatch):
    data = sample()
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps({"format": "RecipeBundle", "version": 1,
        "stacks": {"python": {"label": "Python", "group": "Linguaggi"}}, "recipes": [data]}), encoding="utf-8")
    window = MainWindow(Catalog(path), tmp_path / "profile")
    qtbot.addWidget(window)
    window.show()
    qtbot.waitUntil(lambda: window.count_label.text().endswith("risultati"), timeout=10000)
    window.open_recipe(data["id"])
    widget = window.code_blocks[0]
    monkeypatch.setattr(QInputDialog, "getText", lambda *args: pytest.fail("Ctrl+F locale non deve aprire un dialogo modale"))
    widget.editor.setFocus()
    qtbot.keyClick(widget.editor, Qt.Key.Key_F, Qt.KeyboardModifier.ControlModifier)
    qtbot.waitUntil(widget.find_bar.isVisible)
    assert QApplication.focusWidget() is widget.find_bar.search_edit
    qtbot.keyClicks(widget.find_bar.search_edit, "print")
    assert widget.editor.textCursor().selectedText() == "print"
    qtbot.keyClick(widget.find_bar.search_edit, Qt.Key.Key_Escape)
    assert not widget.find_bar.isVisible()
    assert window.isVisible()
    window.close()


def test_find_in_editor_is_not_a_data_change_and_escape_does_not_close_dialog(qtbot):
    editor = RecipeEditor({"python": {"label": "Python"}}, sample())
    qtbot.addWidget(editor)
    editor.show()
    editor.show_code_find()
    editor.code_find.search_edit.setText("print")
    editor.wrap_edit.setChecked(True)
    assert not editor.dirty
    qtbot.keyClick(editor.code_find.search_edit, Qt.Key.Key_Escape)
    assert editor.isVisible()
    assert not editor.code_find.isVisible()
    editor.reject()


@pytest.mark.parametrize("path,language", [("Dockerfile", "dockerfile"), ("CMakeLists.txt", "cmake"),
    ("src/Widget.svelte", "svelte"), ("src/Main.cs", "csharp"), ("src/main.rs", "rust")])
def test_infer_file_language(path, language):
    assert language_for_path(path) == language


def test_new_file_models_are_explicit_and_never_replace_existing_code(qtbot, monkeypatch):
    editor = RecipeEditor({"python": {"label": "Python"}}, sample())
    qtbot.addWidget(editor)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args: ("src/main.rs", True))
    editor.add_file()
    assert editor.language_edit.currentText() == "rust"
    assert editor.code_edit.toPlainText() == ""
    assert editor.template_button.isEnabled()
    editor.insert_template()
    original = editor.code_edit.toPlainText()
    assert "fn main" in original
    assert not editor.template_button.isEnabled()
    editor.insert_template()
    assert editor.code_edit.toPlainText() == original
    editor.language_edit.setCurrentText("sql")
    editor.path_edit.setText("renamed.py")
    assert editor.language_edit.currentText() == "sql"
    editor.dirty = False
    editor.reject()


def test_metadata_only_save_keeps_original_code_and_parameter_metadata(qtbot):
    data = sample()
    original = "print('caffè')\r\n# nonbreaking\u00a0space 😀\r\n"
    data["assets"][0].update(content=original, sha256=hashlib.sha256(original.encode()).hexdigest(), custom="keep")
    data["parameters"].append({"name": "port", "type": "port", "default": 8000, "required": False, "help": "keep"})
    data["sources"] = ["https://example.invalid/query?a=1,2"]
    data["ide"] = ["IDE, con virgola"]
    data["assets"][1]["os"] = "Windows (WSL)"
    editor = RecipeEditor({"python": {"label": "Python"}}, data)
    qtbot.addWidget(editor)
    editor.title_edit.setText("Titolo modificato")
    editor.asset_list.setCurrentRow(1)
    assert editor.command_os.currentText() == "Windows (WSL)"
    editor.save()
    result = editor.result_recipe
    assert result["assets"][0]["content"] == original
    assert result["assets"][0]["sha256"] == data["assets"][0]["sha256"]
    assert result["assets"][0]["custom"] == "keep"
    assert result["parameters"][1] == data["parameters"][1]
    assert result["sources"] == data["sources"]
    assert result["ide"] == data["ide"]
    assert result["assets"][1]["os"] == "Windows (WSL)"


def test_inline_validation_identifies_required_field_and_invalid_path(qtbot):
    editor = RecipeEditor({"python": {"label": "Python"}}, sample())
    qtbot.addWidget(editor)
    editor.show()
    editor.title_edit.clear()
    editor.save()
    assert editor.result_recipe is None
    assert editor.validation_label.isVisible()
    assert editor.title_edit.property("invalid")
    qtbot.waitUntil(lambda: QApplication.focusWidget() is editor.title_edit)
    editor.title_edit.setText("Valid title")
    editor.path_edit.setText("../escape.py")
    editor.save()
    assert editor.tabs.currentIndex() == 1
    assert editor.result_recipe is None
    assert editor.path_edit.property("invalid")
    qtbot.waitUntil(lambda: QApplication.focusWidget() is editor.path_edit)
    editor.dirty = False
    editor.reject()


def test_diff_search_keeps_comparison_highlights_and_copy_exact(qtbot):
    left, right = sample("left"), sample("right")
    left["assets"][0]["content"] = "print('left')\r\n"
    right["assets"][0]["content"] = "print('right')\r\n"
    dialog = ComparisonDialog({"left": Recipe(left), "right": Recipe(right)}, {"python": {"label": "Python"}}, "left", "right")
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitUntil(lambda: dialog.diff_result is not None, timeout=5000)
    before = len(dialog.left.editor.extraSelections())
    dialog.left.editor.show_find()
    dialog.left.find_bar.search_edit.setText("print")
    assert len(dialog.left.editor.extraSelections()) == before > 0
    assert dialog.left.editor.textCursor().selectedText() == "print"
    dialog.left.copy()
    assert QApplication.clipboard().text() == "print('left')\r\n"
    dialog.reject()


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_syntax_colors_have_readable_contrast(qtbot, theme):
    apply_theme(QApplication.instance(), theme)
    editor = CodeEditor("# comment\nvalue = 'string'\nif value:\n    print(value)\n", "python")
    qtbot.addWidget(editor)
    editor.show()
    qtbot.wait(30)
    editor.highlighter.refresh()
    background = editor.palette().color(QPalette.ColorRole.Base)
    for _, _, fmt in editor.highlighter.spans:
        if fmt.foreground().style() != Qt.BrushStyle.NoBrush:
            assert color_contrast(fmt.foreground().color(), background) >= 4.5
    apply_theme(QApplication.instance(), "light")


def test_translucent_gutter_color_is_composited_before_contrast_correction():
    background = QColor("#f3f6fc")
    foreground = QColor("#18243a")
    foreground.setAlpha(128)
    corrected = readable_token(foreground, background, QColor("#18243a"))
    assert corrected.alpha() == 255
    assert color_contrast(corrected, background) >= 4.5


@pytest.mark.parametrize("scale", ["1", "1.5", "2"])
def test_reader_editor_qt_dpi_and_theme_screenshots(scale, tmp_path):
    script = r'''
import sys,json
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root));sys.path.insert(0,str(root/'tests'))
from devatlas.qt_bootstrap import configure_qt_plugins,load_bundled_fonts
configure_qt_plugins()
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout
from PySide6.QtTest import QTest
from devatlas.codewidgets import CodeBlock
from devatlas.editor import RecipeEditor
from devatlas.theme import apply_theme
from test_core import sample
app=QApplication([]);load_bundled_fonts()
out=root/'reports/ui-state/1.3-reader-offscreen';out.mkdir(parents=True,exist_ok=True)
for theme in ('light','dark'):
 apply_theme(app,theme)
 view=QWidget();layout=QVBoxLayout(view)
 text='# Commento leggibile\n'+('def funzione():\n    return "dati locali"\n'*20)
 block=CodeBlock({'path':'src/modulo_lungo.py','role':'file','language':'python','content':text})
 layout.addWidget(block);layout.addStretch();view.resize(700,700);view.show();block.editor.zoomIn(2);block.show_find();block.find_bar.search_edit.setText('return');QTest.qWait(100)
 assert block.copy_button.geometry().right()<=block.width()
 assert block.editor.geometry().bottom()<=block.height()
 assert block.editor.numbers.width()==block.editor.number_width()
 assert view.grab().save(str(out/f'reader-{theme}-dpi-{sys.argv[2]}.png'))
 editor=RecipeEditor({'python':{'label':'Python'}},sample());editor.resize(850,650);editor.show();editor.show_code_find();editor.code_find.search_edit.setText('print');QTest.qWait(70)
 assert editor.grab().save(str(out/f'editor-{theme}-dpi-{sys.argv[2]}.png'))
 editor.dirty=False;editor.reject();view.close()
print(json.dumps({'dpr':view.devicePixelRatioF(),'scale':sys.argv[2]}))
'''
    result = subprocess.run([sys.executable, "-c", script, str(ROOT), scale], cwd=ROOT,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen", "QT_SCALE_FACTOR": scale, "PYTHONIOENCODING": "utf8"},
        capture_output=True, text=True, encoding="utf8", timeout=25)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout.strip().splitlines()[-1])["dpr"] == pytest.approx(float(scale))
