from copy import deepcopy
import json

import pytest
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox, QTextEdit

from devatlas.app import MainWindow
from devatlas.bundles import export_files, save_bundle
from devatlas.catalog import Catalog
from devatlas.personal import PersonalStore
from devatlas.templating import render_recipe
from test_core import sample


@pytest.fixture
def small_window(qtbot, tmp_path):
    catalog_file = tmp_path / "catalog.json"
    catalog_file.write_text(json.dumps({
        "format": "RecipeBundle", "version": 1,
        "stacks": {"python": {"label": "Python", "group": "Linguaggi"}},
        "recipes": [sample()],
    }), encoding="utf-8")
    window = MainWindow(Catalog(catalog_file), tmp_path / "user")
    qtbot.addWidget(window)
    window.show()
    qtbot.waitUntil(lambda: window.count_label.text().endswith("risultati"), timeout=10000)
    yield window
    window.close()


def linked_recipes():
    first = sample("personal-first", title="Prima ricetta")
    second = sample("personal-second", title="Seconda ricetta")
    first.update(personal=True, related=["personal-second"])
    second.update(personal=True, related=["personal-first", "python-json"])
    return [first, second]


def test_editing_a_plain_text_note_preserves_html_like_source(small_window, monkeypatch):
    window = small_window
    window.open_recipe("python-json")
    note = "<b>TODO</b>\n<p>Un frammento HTML & il suo significato</p>"
    window.store.annotate("python-json", note=note)
    observed = []

    class AcceptNote(QDialog):
        def exec(self):
            observed.append(self.findChild(QTextEdit).toPlainText())
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr("devatlas.app.QDialog", AcceptNote)
    window.edit_note()
    assert observed == [note]
    assert window.store.annotation("python-json")[1] == note


def test_bundle_import_preserves_internal_links_and_existing_catalog_links(
        small_window, tmp_path, monkeypatch):
    recipes = linked_recipes()
    original = deepcopy(recipes)
    path = tmp_path / "linked.devatlas.zip"
    save_bundle(path, recipes)
    monkeypatch.setattr("devatlas.app.QFileDialog.getOpenFileName", lambda *args: (str(path), ""))
    monkeypatch.setattr("devatlas.app.QMessageBox.question", lambda *args: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(small_window, "show_error", lambda title, error: pytest.fail(f"{title}: {error}"))
    small_window.import_bundle()
    imported = {r["title"]: r for r in small_window.store.list_recipes()}
    first, second = imported["Prima ricetta"], imported["Seconda ricetta"]
    assert first["id"] != "personal-first"
    assert second["id"] != "personal-second"
    assert first["related"] == [second["id"]]
    assert second["related"] == [first["id"], "python-json"]
    assert all(rid in small_window.recipes for rid in first["related"] + second["related"])
    assert recipes == original


def test_backup_duplicates_remap_links_annotations_and_collection_membership(tmp_path):
    store = PersonalStore(tmp_path / "personal.sqlite")
    originals = linked_recipes()
    for recipe in originals:
        store.save_recipe(recipe)
    store.annotate("personal-second", favorite=True, note="<b>nota letterale</b>")
    store.annotate("python-json", favorite=True, note="Nota sul catalogo")
    cid = store.create_collection("Lezione")
    store.add_to_collection(cid, "personal-second")
    store.add_to_collection(cid, "python-json")
    backup = store.backup_data()
    backup_before = deepcopy(backup)
    store.restore_data(backup, duplicate=True)
    rows = store.list_recipes()
    copies = {r["title"]: r for r in rows if r["id"] not in {"personal-first", "personal-second"}}
    first, second = copies["Prima ricetta"], copies["Seconda ricetta"]
    assert first["related"] == [second["id"]]
    assert second["related"] == [first["id"], "python-json"]
    assert store.annotation(second["id"]) == (True, "<b>nota letterale</b>")
    assert store.annotation("python-json") == (True, "Nota sul catalogo")
    assert set(store.collection_ids(cid)) == {"personal-second", second["id"], "python-json"}
    assert next(r for r in rows if r["id"] == "personal-first")["related"] == ["personal-second"]
    assert backup == backup_before


def test_command_directory_is_rendered_in_preview_and_export_without_changing_source():
    data = sample()
    data["assets"][1]["cwd"] = "src/{{project_name}}"
    rendered = render_recipe(data, {"project_name": "Nuovo"})
    assert rendered["assets"][1]["cwd"] == "src/Nuovo"
    assert data["assets"][1]["cwd"] == "src/{{project_name}}"
    assert "Directory: `src/Nuovo`" in export_files(data, {"project_name": "Nuovo"})["README.md"]


def test_parameter_refresh_updates_reader_text_and_preserves_input_focus(small_window, qtbot):
    window = small_window
    data = window.recipes["python-json"].data
    data.update(summary="Crea {{project_name}}", prerequisites="Prepara {{project_name}}",
                guide="# Procedura\nApri {{project_name}} e prosegui.")
    data["assets"][1]["cwd"] = "src/{{project_name}}"
    window.open_recipe("python-json")
    window.mode_combo.setCurrentIndex(1)
    edit = window.parameter_edits["project_name"]
    edit.setFocus()
    qtbot.waitUntil(lambda: QApplication.focusWidget() is edit)
    edit.setText("Nuovo")
    qtbot.waitUntil(lambda: window.summary_label.text() == "Crea Nuovo", timeout=2000)
    assert window.parameter_edits["project_name"] is edit
    assert QApplication.focusWidget() is edit
    assert window.prerequisites_label.text() == "Prepara Nuovo"
    assert "Apri Nuovo e prosegui." in window.guide_browser.toPlainText()
    assert "{{project_name}}" not in window.guide_browser.toPlainText()
    command = next(block for block in window.code_blocks if block.asset["role"] == "command")
    assert command.asset["cwd"] == "src/Nuovo"
