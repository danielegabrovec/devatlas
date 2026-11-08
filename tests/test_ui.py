from pathlib import Path
from copy import deepcopy
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from devatlas.app import MainWindow
from devatlas.catalog import Catalog
from devatlas.codewidgets import CodeBlock
from devatlas.editor import RecipeEditor
from devatlas.models import Recipe, SearchQuery
from test_core import sample


@pytest.fixture
def window(qtbot, tmp_path):
    app = QApplication.instance()
    app.setProperty("devatlasTheme", "light")
    window = MainWindow(Catalog(), tmp_path)
    qtbot.addWidget(window)
    window.show()
    qtbot.waitUntil(lambda: window.count_label.text().endswith("risultati"), timeout=15000)
    yield window
    window.close()


def test_search_selection_copy_modes_and_theme(window, qtbot):
    window.search_edit.setText("python json")
    qtbot.waitUntil(lambda: bool(window.model.ids) and window.search_edit.text() == "python json" and
        all(window.recipes[rid].stack in ("python", "packaging") for rid in window.model.ids), timeout=10000)
    window.results_list.setCurrentIndex(window.model.index(0))
    assert window.current_recipe
    assert window.code_blocks
    block = window.code_blocks[0]
    assert block.height() >= block.editor.height()
    qtbot.mouseClick(block.copy_button, Qt.MouseButton.LeftButton)
    assert QApplication.clipboard().text() == block.asset["content"]
    window.mode_combo.setCurrentIndex(1)
    assert window.current_recipe.id
    window.theme_combo.setCurrentIndex(window.theme_combo.findData("dark"))
    assert QApplication.instance().property("devatlasTheme") == "dark"
    assert window.code_blocks[0].editor.highlighter.dark
    window.resize(950, 650)
    qtbot.wait(80)
    assert not window.sidebar.isVisible()
    assert window.search_edit.isVisible()


def test_stale_search_cannot_replace_new_results(window):
    from devatlas.models import SearchResult
    before = list(window.model.ids)
    window.request = 100
    window.search_finished(99, SearchResult(["not-a-real-id"], 1), "", False)
    assert window.model.ids == before


def test_parameters_update_preview_and_disable_invalid_copy(window, qtbot):
    recipe = Recipe(sample())
    window.recipes[recipe.id] = recipe
    window.open_recipe(recipe.id)
    assert window.code_blocks[0].asset["path"] == "src/esempio.py"
    window.parameter_edits["project_name"].setText("Nuovo")
    qtbot.waitUntil(lambda: window.code_blocks[0].asset["path"] == "src/Nuovo.py", timeout=2000)
    window.parameter_edits["project_name"].setText("../invalid")
    qtbot.waitUntil(lambda: not window.export_button.isEnabled(), timeout=2000)
    assert not window.code_blocks[0].copy_button.isEnabled()


def test_personal_editor_creates_independent_copy(qtbot):
    original = sample()
    editor = RecipeEditor({"python": {"label": "Python"}}, original)
    qtbot.addWidget(editor)
    editor.title_edit.setText("La mia ricetta")
    editor.code_edit.setPlainText("print('personale')\n")
    editor.save()
    result = editor.result_recipe
    assert result["id"].startswith("personal-")
    assert result["title"] == "La mia ricetta"
    assert result["assets"][0]["content"] == "print('personale')\n"
    assert original["title"] == "Leggere un file JSON"
    assert original["assets"][0]["content"] == "print('caffè ☕')\n"


def test_editor_highlighting_and_file_navigation_do_not_create_unsaved_changes(qtbot, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    data = sample()
    editor = RecipeEditor({"python": {"label": "Python"}}, data)
    qtbot.addWidget(editor)
    editor.show()
    qtbot.wait(180)
    editor.asset_list.setCurrentRow(1)
    qtbot.wait(180)
    assert not editor.dirty
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: pytest.fail("Una semplice apertura non deve chiedere di scartare modifiche"))
    editor.reject()


def test_editor_actions_remain_reachable_on_small_logical_screens(qtbot):
    from PySide6.QtWidgets import QDialogButtonBox, QScrollArea
    editor = RecipeEditor({"python": {"label": "Python"}}, sample())
    qtbot.addWidget(editor)
    editor.resize(850, 500)
    editor.show()
    qtbot.wait(50)
    assert editor.height() <= 500
    buttons = editor.findChild(QDialogButtonBox)
    assert buttons.geometry().bottom() <= editor.height()
    editor.tabs.widget(0).ensureWidgetVisible(editor.sources_edit)
    qtbot.wait(50)
    assert editor.sources_edit.mapTo(editor, editor.sources_edit.rect().bottomRight()).y() < buttons.geometry().top()
    editor.tabs.setCurrentIndex(1)
    qtbot.wait(50)
    assert buttons.geometry().bottom() <= editor.height()
    editor.dirty = False
    editor.reject()


def test_navigation_favorites_and_collections(window, qtbot):
    rid = next(iter(window.recipes))
    window.open_recipe(rid)
    window.toggle_favorite()
    assert rid in window.store.favorites()
    cid = window.store.create_collection("Corso")
    window.store.add_to_collection(cid, rid)
    window.selection_filter = {"collection": cid}
    assert window.index.search(window.query()).ids == [rid]
    window.rebuild_index()
    assert window.store.annotation(rid)[0]
    assert window.store.collection_ids(cid) == [rid]


def test_guided_reader_keeps_all_code_blocks_inside_the_scroll_content(window, qtbot):
    recipe = next(r for r in window.recipes.values() if r.stack == "pyside6" and not r.project)
    window.mode_combo.setCurrentIndex(1)
    window.open_recipe(recipe.id)
    qtbot.waitUntil(lambda: window.preview_container.height() >= sum(b.minimumHeight() for b in window.code_blocks), timeout=3000)
    blocks = window.code_blocks
    for earlier, later in zip(blocks, blocks[1:]):
        assert earlier.geometry().bottom() < later.geometry().top()
    assert blocks[-1].geometry().bottom() <= window.preview_container.height()

