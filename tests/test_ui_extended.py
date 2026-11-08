"""Workflow UI con profili sintetici; nessuna finestra o dato personale del PC."""
from copy import deepcopy
import json
from pathlib import Path
import os
import subprocess
import sys
import threading

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QInputDialog, QMessageBox, QFileDialog, QTextEdit

from devatlas.app import MainWindow, ProfileInstance, startup_catalog
from devatlas.catalog import Catalog
from devatlas.editor import RecipeEditor
from devatlas.codewidgets import CodeEditor
from devatlas.theme import apply_theme
from devatlas.bundles import load_bundle
from test_core import sample


ROOT = Path(__file__).resolve().parents[1]


def small_catalog(path):
    rows = []
    for rid, section, title, project in (
        ("fastapi-init", "Inizializzazione", "Avviare il server", False),
        ("fastapi-data", "Codice applicativo", "Leggere i dati", False),
        ("fastapi-debug", "Debug", "Impostare un breakpoint", False),
        ("fastapi-project", "Codice applicativo", "Progetto completo", True),
        ("python-copy", "Codice applicativo", "Copiare Unicode", False),
    ):
        data = sample(rid, "python" if rid.startswith("python") else "fastapi", title)
        data.update(section=section, project=project, versions="Python 3.13", guide="# Procedura\n\nApri il file e avvia i comandi.",
                    verification={"status": "statico", "date": "2026-10-29", "details": "Controllo sintetico della sintassi; esecuzione non attestata."})
        rows.append(data)
    path.write_text(json.dumps({"format": "RecipeBundle", "version": 1,
        "stacks": {"python": {"label": "Python", "group": "Linguaggi"}, "fastapi": {"label": "FastAPI", "group": "Web e backend"}}, "recipes": rows}), encoding="utf8")
    return Catalog(path)


@pytest.fixture
def compact_window(qtbot, tmp_path):
    catalog = small_catalog(tmp_path / "catalog.json")
    window = MainWindow(catalog, tmp_path / "profile")
    qtbot.addWidget(window)
    window.resize(1100, 700)
    window.show()
    qtbot.waitUntil(lambda: window.count_label.text().endswith("risultati"), timeout=10000)
    yield window
    window.close()


def test_editor_add_commands_and_remove_parameter_are_unsaved_changes(qtbot):
    editor = RecipeEditor({"python": {"label": "Python"}}, sample())
    qtbot.addWidget(editor)
    assert not editor.dirty
    editor.add_command()
    assert editor.dirty
    assert editor.assets[-1]["role"] == "command"
    editor.dirty = False
    editor.parameter_table.selectRow(0)
    editor.remove_parameter()
    assert editor.dirty
    assert editor.parameter_table.rowCount() == 0
    editor.dirty = False
    editor.reject()


def test_editor_new_file_language_and_live_title(qtbot, monkeypatch):
    editor = RecipeEditor({"python": {"label": "Python"}}, sample())
    qtbot.addWidget(editor)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("src/query.sql", True))
    editor.add_file()
    assert editor.dirty
    editor.language_edit.setCurrentText("sql")
    assert editor.code_edit.highlighter.language == "sql"
    editor.path_edit.setText("src/select.sql")
    assert editor.asset_list.currentItem().text() == "src/select.sql"
    editor.dirty = False
    editor.reject()


def test_editor_optional_parameter_and_project_roundtrip(qtbot):
    data = sample()
    data["parameters"].append({"name": "note", "label": "Nota", "type": "string", "default": "", "required": False})
    editor = RecipeEditor({"python": {"label": "Python"}}, data)
    qtbot.addWidget(editor)
    editor.project_edit.setChecked(True)
    editor.save()
    assert editor.result_recipe["parameters"][1]["required"] is False
    assert editor.result_recipe["project"] is True
    assert data.get("project") is None


def test_new_parameter_type_changes_are_tracked(qtbot):
    editor = RecipeEditor({"python": {"label": "Python"}}, sample())
    qtbot.addWidget(editor)
    editor.add_parameter({"name": "port", "type": "port", "default": "8000"})
    editor.dirty = False
    editor.parameter_table.cellWidget(1, 2).setCurrentText("string")
    assert editor.dirty
    editor.dirty = False
    editor.reject()


def test_command_shell_language_and_metadata_roundtrip(qtbot):
    editor = RecipeEditor({"python": {"label": "Python"}}, sample())
    qtbot.addWidget(editor)
    editor.asset_list.setCurrentRow(1)
    editor.shell_edit.setCurrentText("Bash")
    editor.command_os.setCurrentText("Linux")
    editor.cwd_edit.setText("src")
    editor.code_edit.setPlainText("python3 esempio.py\n")
    assert editor.code_edit.highlighter.language == "bash"
    editor.save()
    command = editor.result_recipe["assets"][1]
    assert (command["shell"], command["language"], command["os"], command["cwd"]) == ("Bash", "bash", "Linux", "src")
    assert command["content"] == "python3 esempio.py\n"


def test_code_highlighting_tracks_language_and_theme(qtbot):
    editor = CodeEditor("select 1;", "text", readonly=False)
    qtbot.addWidget(editor)
    editor.set_language("sql")
    assert "sql" in editor.highlighter.lexer.aliases
    apply_theme(QApplication.instance(), "dark")
    qtbot.waitUntil(lambda: editor.highlighter.dark)
    editor.set_language("not-a-real-lexer")
    assert editor.highlighter.lexer.name == "Text only"
    apply_theme(QApplication.instance(), "light")


def test_line_numbers_expand_when_document_grows(qtbot):
    editor = CodeEditor("riga", "text")
    qtbot.addWidget(editor)
    editor.show()
    before = editor.numbers.width()
    editor.setPlainText("\n".join("riga" for _ in range(1200)))
    qtbot.waitUntil(lambda: editor.numbers.width() > before)
    assert editor.numbers.width() == editor.number_width()


def test_collection_rename_delete_preserves_sheets_favorite_note(compact_window, qtbot, monkeypatch):
    w = compact_window
    rid = "python-copy"
    w.open_recipe(rid)
    w.store.annotate(rid, favorite=True, note="Appunto sintetico")
    cid = w.store.create_collection("Lezioni")
    w.store.add_to_collection(cid, rid)
    w.selection_filter = {"collection": cid}
    w.rebuild_navigation()
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Corso", True))
    w.rename_collection()
    assert dict(w.store.collections())[cid] == "Corso"
    assert w.tree.currentItem().text(0) == "Corso"
    assert w.rename_collection_action.isEnabled()
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)
    w.delete_collection()
    assert not w.store.collections()
    assert rid in w.recipes
    assert w.store.annotation(rid) == (True, "Appunto sintetico")
    assert w.selection_filter == {}
    assert not w.delete_collection_action.isEnabled()


def test_guided_path_has_real_order_completion_and_resume(compact_window, qtbot):
    w = compact_window
    item = w.navigation_item({"stack": "fastapi", "guided": True})
    w.tree.setCurrentItem(item)
    assert w.current_recipe.id == "fastapi-init"
    ids = w.guided_ids()
    assert ids[-1] == "fastapi-project"
    assert w.guided_toolbar.isVisible()
    assert not w.guided_previous.isEnabled()
    qtbot.mouseClick(w.guided_completed, Qt.MouseButton.LeftButton)
    assert "fastapi-init" in w.store.setting("guided_progress")["fastapi"]
    qtbot.mouseClick(w.guided_next, Qt.MouseButton.LeftButton)
    assert w.current_recipe.id == ids[1]
    w.tree.setCurrentItem(w.tree.topLevelItem(0))
    assert not w.guided_toolbar.isVisible()
    w.tree.setCurrentItem(item)
    assert w.current_recipe.id == ids[1]
    assert "1 completati" in w.guided_label.text()


def test_invalid_parameters_disable_keyboard_copy_and_resume_navigation(compact_window, qtbot):
    w = compact_window
    w.open_recipe("python-copy")
    w.parameter_edits["project_name"].setText("../bad")
    assert not w.code_blocks[0].copy_button.isEnabled()
    assert not w.code_blocks[0].editor.isEnabled()
    qtbot.waitUntil(lambda: not w.parameter_error.isHidden(), timeout=2000)
    w.parameter_edits["project_name"].setText("Valido")
    qtbot.waitUntil(lambda: w.export_button.isEnabled(), timeout=2000)
    qtbot.mouseClick(w.code_blocks[0].copy_button, Qt.MouseButton.LeftButton)
    assert QApplication.clipboard().text() == w.code_blocks[0].asset["content"]
    w.open_recipe("fastapi-data")
    w.navigate(-1)
    assert w.current_recipe.id == "python-copy"
    assert w.parameter_edits["project_name"].text() == "Valido"


def test_verification_details_available_without_guided_mode(compact_window, qtbot):
    w = compact_window
    w.open_recipe("python-copy")
    assert w.mode_combo.currentIndex() == 0
    assert w.verification_details.isHidden()
    qtbot.mouseClick(w.verification_toggle, Qt.MouseButton.LeftButton)
    assert not w.verification_details.isHidden()
    assert "esecuzione non attestata" in w.verification_details.text()


def test_invalid_cached_parameter_does_not_leave_deleted_code_widgets(compact_window, qtbot):
    w = compact_window
    w.open_recipe("python-copy")
    w.parameter_edits["project_name"].setText("../bad")
    qtbot.waitUntil(lambda: not w.parameter_error.isHidden(), timeout=2000)
    w.open_recipe("fastapi-data")
    w.navigate(-1)
    assert not w.export_button.isEnabled()
    assert w.code_blocks == []
    qtbot.wait(150)
    w.parameter_edits["project_name"].setText("Corretto")
    qtbot.waitUntil(lambda: bool(w.code_blocks) and w.export_button.isEnabled(), timeout=2000)


@pytest.mark.parametrize("scale", ["1", "1.5", "2"])
def test_qt_scale_factors_and_editor_capture(scale, tmp_path):
    script = r'''
import json,sys
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root));sys.path.insert(0,str(root/'tests'))
from devatlas.qt_bootstrap import configure_qt_plugins
configure_qt_plugins()
from PySide6.QtWidgets import QApplication,QDialogButtonBox
from PySide6.QtTest import QTest
from devatlas.app import MainWindow
from devatlas.editor import RecipeEditor
from test_ui_extended import small_catalog
from test_core import sample
app=QApplication([])
directory=Path(sys.argv[2]);directory.mkdir(parents=True,exist_ok=True)
w=MainWindow(small_catalog(directory/'catalog.json'),directory/'profile')
w.resize(950,650);w.show();w.open_recipe('python-copy');QTest.qWait(250)
output=root/'reports/ui-state/1.1-offscreen';output.mkdir(parents=True,exist_ok=True)
assert w.grab().save(str(output/('dpi-'+sys.argv[3]+'.png')))
editor=RecipeEditor(w.catalog.stacks,sample());editor.resize(850,500);editor.show();QTest.qWait(100)
buttons=editor.findChild(QDialogButtonBox)
assert buttons.geometry().bottom()<=editor.height()
assert editor.grab().save(str(output/('editor-dpi-'+sys.argv[3]+'.png')))
print(json.dumps({'dpr':w.devicePixelRatioF(),'width':w.width(),'height':w.height(),'editor_height':editor.height()}))
editor.dirty=False;editor.reject();w.close()
'''
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "QT_SCALE_FACTOR": scale, "PYTHONIOENCODING": "utf8"}
    result = subprocess.run([sys.executable, "-c", script, str(ROOT), str(tmp_path / "dpi"), scale],
                            cwd=ROOT, env=env, text=True, encoding="utf8", capture_output=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout.strip().splitlines()[-1])
    assert data["dpr"] == pytest.approx(float(scale))
    assert data["width"] == 950


def test_keyboard_search_replaces_previous_query(compact_window, qtbot):
    w = compact_window
    w.search_edit.setText("vecchia ricerca")
    w.activateWindow()
    w.results_list.setFocus()
    qtbot.keyClick(w, Qt.Key.Key_K, modifier=Qt.KeyboardModifier.ControlModifier)
    qtbot.keyClicks(w.search_edit, "json")
    assert w.search_edit.text() == "json"


def test_export_and_import_personal_ui_workflow(compact_window, qtbot, tmp_path, monkeypatch):
    w = compact_window
    w.open_recipe("python-copy")
    w.parameter_edits["project_name"].setText("Esportato")
    qtbot.waitUntil(lambda: w.export_button.isEnabled(), timeout=2000)
    target = tmp_path / "export"
    target.mkdir()
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: str(target))
    w.export_current(False)
    assert (target / "python-copy/src/Esportato.py").read_text(encoding="utf8") == w.code_blocks[0].asset["content"]
    bundle = tmp_path / "recipe.devatlas.zip"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(bundle), ""))
    w.export_recipe_bundle()
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(bundle), ""))
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Ok)
    w.import_bundle()
    assert len(w.store.list_recipes()) == 1
    assert w.store.list_recipes()[0]["id"].startswith("personal-")


def test_notes_dialog_saves_plain_text_and_reader_updates(compact_window, qtbot):
    w = compact_window
    w.open_recipe("python-copy")
    def fill():
        dialog = QApplication.activeModalWidget()
        dialog.findChild(QTextEdit).setPlainText("Nota sintetica <b>testo letterale</b>")
        qtbot.mouseClick(dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Save), Qt.MouseButton.LeftButton)
    QTimer.singleShot(0, fill)
    w.edit_note()
    assert w.store.annotation("python-copy")[1] == "Nota sintetica <b>testo letterale</b>"


def test_create_and_edit_personal_recipe_dialog_preserves_identity(compact_window, qtbot):
    w = compact_window
    original = w.recipes["python-copy"].to_dict()
    def create():
        editor = QApplication.activeModalWidget()
        editor.title_edit.setText("La mia scheda")
        editor.code_edit.setPlainText("print('modificato')\n")
        editor.save()
    QTimer.singleShot(0, create)
    w.edit_recipe(w.recipes["python-copy"])
    rid = w.current_recipe.id
    assert rid.startswith("personal-")
    assert w.recipes["python-copy"].to_dict() == original
    def edit():
        editor = QApplication.activeModalWidget()
        editor.title_edit.setText("Titolo aggiornato")
        editor.save()
    QTimer.singleShot(0, edit)
    w.edit_recipe(w.current_recipe)
    assert w.current_recipe.id == rid
    assert len(w.store.list_recipes()) == 1
    assert w.current_recipe.title == "Titolo aggiornato"


def test_collection_export_and_backup_restore_ui(compact_window, qtbot, tmp_path, monkeypatch):
    w = compact_window
    personal = sample("personal-backup")
    personal["personal"] = True
    w.store.save_recipe(personal)
    w.reload_personal()
    qtbot.waitUntil(lambda: w.index_ready, timeout=3000)
    w.store.annotate("python-copy", favorite=True, note="Appunto da backup")
    cid = w.store.create_collection("Backup sintetico")
    w.store.add_to_collection(cid, "python-copy")
    w.store.add_to_collection(cid, "personal-backup")
    w.selection_filter = {"collection": cid}
    w.rebuild_navigation()
    target = tmp_path / "collection.zip"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(target), ""))
    w.export_collection()
    assert {r["id"] for r in load_bundle(target)["recipes"]} == {"python-copy", "personal-backup"}
    backup = tmp_path / "backup.zip"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(backup), ""))
    w.backup_personal()
    restored = MainWindow(w.catalog, tmp_path / "restored")
    qtbot.addWidget(restored)
    restored.show()
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(backup), ""))
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Ok)
    restored.import_bundle()
    assert restored.store.annotation("python-copy") == (True, "Appunto da backup")
    assert len(restored.store.list_recipes()) == 1
    collections = restored.store.collections()
    assert len(collections) == 1 and collections[0][1] == "Backup sintetico"
    assert len(restored.store.collection_ids(collections[0][0])) == 2
    restored.close()


@pytest.mark.parametrize("theme,width,height", [("light", 1540, 940), ("dark", 950, 650), ("light", 800, 520)])
def test_responsive_toolbar_and_widget_capture(compact_window, qtbot, theme, width, height):
    w = compact_window
    w.theme_combo.setCurrentIndex(w.theme_combo.findData(theme))
    w.tree.setCurrentItem(w.navigation_item({"stack": "fastapi", "guided": True}))
    w.resize(width, height)
    qtbot.wait(100)
    assert w.width() <= width
    for button in (w.back_button, w.forward_button, w.export_button, w.recipe_menu_button):
        assert button.geometry().right() <= w.reader_toolbar.width()
    assert w.search_edit.isVisible()
    qtbot.waitUntil(lambda: w.model.ids == w.guided_ids(), timeout=3000)
    output = ROOT / "reports/ui-state/1.1-offscreen"
    output.mkdir(parents=True, exist_ok=True)
    assert w.grab().save(str(output / f"workflow-{theme}-{width}.png"))


def test_rebuild_navigation_keeps_expansion_and_selection(compact_window):
    w = compact_window
    group = next(w.tree.topLevelItem(i) for i in range(w.tree.topLevelItemCount()) if w.tree.topLevelItem(i).text(0) == "Web e backend")
    group.setExpanded(False)
    w.tree.setCurrentItem(w.navigation_item({"stack": "python"}))
    w.rebuild_navigation()
    assert w.tree.currentItem().data(0, Qt.ItemDataRole.UserRole) == {"stack": "python"}
    group = next(w.tree.topLevelItem(i) for i in range(w.tree.topLevelItemCount()) if w.tree.topLevelItem(i).text(0) == "Web e backend")
    assert not group.isExpanded()


def test_profile_lock_is_per_directory_and_second_launch_activates(qtbot, tmp_path):
    first = ProfileInstance(tmp_path)
    second = ProfileInstance(tmp_path)
    other_path = tmp_path / "other"
    other_path.mkdir()
    other = ProfileInstance(other_path)
    assert first.acquire()
    with qtbot.waitSignal(first.activated, timeout=2000):
        assert second.acquire() is False
    assert other.acquire()
    first.close()
    assert second.acquire()
    second.close()
    other.close()


def test_startup_local_corruption_falls_back_preserving_original(tmp_path):
    local = tmp_path / "catalogo-locale.json"
    local.write_text("{invalid", encoding="utf8")
    before = local.read_bytes()
    catalog, notice = startup_catalog(tmp_path)
    assert catalog.recipes
    assert "conservati" in notice
    assert local.read_bytes() == before
    with pytest.raises(ValueError):
        startup_catalog(tmp_path, explicit=local)


def test_startup_directory_error_has_visible_message(qtbot, monkeypatch):
    from devatlas import app as module
    messages = []
    def unavailable():
        raise PermissionError("Cartella di prova non scrivibile")
    monkeypatch.setattr(module, "user_directory", unavailable)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: messages.append(a[2]))
    original_hook = sys.excepthook
    try:
        assert module.main([]) == 1
    finally:
        sys.excepthook = original_hook
    assert "Cartella di prova non scrivibile" in messages[0]
    assert "permessi" in messages[0]


def test_startup_log_error_is_handled_before_profile_mutation(qtbot, tmp_path, monkeypatch):
    from devatlas import app as module
    marker = tmp_path / "original.txt"
    marker.write_text("conservato", encoding="utf8")
    messages = []
    monkeypatch.setattr(module, "user_directory", lambda: tmp_path)
    def failed_log(*a, **k):
        raise PermissionError("Registro non scrivibile")
    monkeypatch.setattr(module.logging, "basicConfig", failed_log)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: messages.append(a[2]))
    original_hook = sys.excepthook
    try:
        assert module.main([]) == 1
    finally:
        sys.excepthook = original_hook
    assert "Registro non scrivibile" in messages[0]
    assert marker.read_text(encoding="utf8") == "conservato"


def test_personal_invalid_record_notice_is_nonblocking(qtbot, tmp_path):
    catalog = small_catalog(tmp_path / "catalog.json")
    profile = tmp_path / "profile"
    from devatlas.personal import PersonalStore
    store = PersonalStore(profile / "personali.sqlite")
    with store.connect() as db:
        db.execute("INSERT INTO recipes VALUES (?,?)", ("personal-bad", json.dumps({"id": "personal-bad"})))
    w = MainWindow(catalog, profile)
    qtbot.addWidget(w)
    w.show()
    assert w.notice_frame.isVisible()
    assert "1 schede" in w.notice_label.text()
    with store.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM recipes").fetchone()[0] == 1
    w.close()


def test_index_worker_keeps_ui_responsive_and_coalesces_edits(compact_window, qtbot):
    w = compact_window
    original = w.index.rebuild
    started = threading.Event()
    release = threading.Event()
    calls = []
    def slow(recipes, fingerprint, *, force=False):
        calls.append(set(recipes))
        if len(calls) == 1:
            started.set()
            assert release.wait(5)
        original(recipes, fingerprint, force=force)
    w.index.rebuild = slow
    w.rebuild_index()
    qtbot.waitUntil(started.is_set)
    assert not w.index_ready
    assert not w.export_collection_action.isEnabled()
    pings = []
    QTimer.singleShot(0, lambda: pings.append(True))
    qtbot.waitUntil(lambda: bool(pings), timeout=1000)
    w.open_recipe("python-copy")
    assert w.current_recipe.id == "python-copy"
    for n in range(2):
        data = sample("personal-async" + str(n))
        data["personal"] = True
        w.store.save_recipe(data)
        w.reload_personal()
    release.set()
    qtbot.waitUntil(lambda: w.index_ready, timeout=5000)
    assert len(calls) == 2
    assert {"personal-async0", "personal-async1"} <= calls[-1]
    assert w.current_recipe.id == "python-copy"
    assert w.export_collection_action.isEnabled()


def test_index_failure_is_nonblocking_and_retry_recovers(compact_window, qtbot):
    w = compact_window
    original = w.index.rebuild
    def broken(*a, **k):
        raise OSError("Indice sintetico non scrivibile")
    w.index.rebuild = broken
    w.rebuild_index()
    qtbot.waitUntil(lambda: w.index_job is None, timeout=3000)
    assert not w.index_ready
    assert "Indice sintetico" in w.notice_label.text()
    w.open_recipe("python-copy")
    assert w.code_blocks
    w.index.rebuild = original
    w.rebuild_index()
    qtbot.waitUntil(lambda: w.index_ready, timeout=3000)
    assert not w.notice_frame.isVisible()


def test_cli_smoke_waits_for_background_index_and_real_query(tmp_path):
    path = tmp_path / "catalog.json"
    small_catalog(path)
    script = r'''
import sys,time
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from devatlas.qt_bootstrap import configure_qt_plugins
configure_qt_plugins()
from devatlas.search import SearchIndex
original=SearchIndex.rebuild
def slow(self,*args,**kwargs):
    time.sleep(.5)
    return original(self,*args,**kwargs)
SearchIndex.rebuild=slow
from devatlas.app import main
raise SystemExit(main(['--catalog',sys.argv[2],'--data-dir',sys.argv[3],'--smoke-test']))
'''
    profile = tmp_path / "profile"
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "PYTHONIOENCODING": "utf8"}
    result = subprocess.run([sys.executable, "-c", script, str(ROOT), str(path), str(profile)], cwd=ROOT,
                            env=env, capture_output=True, text=True, encoding="utf8", timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((profile / "smoke-test.json").read_text(encoding="utf8"))
    assert data["status"] == "passed"
    assert data["index_ready"]
    assert data["results"] > 0
    assert data["recipe"]
    assert data["code_blocks"] > 0
    assert data["elapsed_ms"] >= 500


def test_cli_smoke_fails_when_query_has_no_results(tmp_path):
    path = tmp_path / "catalog.json"
    catalog = small_catalog(path)
    data = catalog.recipes["python-copy"].to_dict()
    data.update(id="cpp-zebra", stack="cpp", title="Zebra", summary="Zebra", tags=["zebra"], guide="Zebra", errors=[], prerequisites="Zebra")
    data["assets"] = [{"id": "main", "path": "zebra.txt", "role": "file", "language": "text", "content": "Zebra"}]
    data["parameters"] = []
    path.write_text(json.dumps({"format": "RecipeBundle", "version": 1, "stacks": {"cpp": {"label": "C++", "group": "Linguaggi"}}, "recipes": [data]}), encoding="utf8")
    profile = tmp_path / "profile"
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen", "PYTHONIOENCODING": "utf8"}
    result = subprocess.run([sys.executable, "run_devatlas.py", "--catalog", str(path), "--data-dir", str(profile), "--smoke-test"], cwd=ROOT,
                            env=env, capture_output=True, text=True, encoding="utf8", timeout=30)
    assert result.returncode == 1, result.stdout + result.stderr
    data = json.loads((profile / "smoke-test.json").read_text(encoding="utf8"))
    assert data["status"] == "failed"
    assert data["results"] == 0
