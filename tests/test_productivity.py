"""Ricerche e confronti su dati sintetici, senza eseguire il codice mostrato."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import unicodedata

import pytest
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox, QMenu, QDialog
from shiboken6 import isValid

from devatlas.app import MainWindow, SAVED_SEARCH_KEY, validate_saved_searches
from devatlas.catalog import Catalog
from devatlas.codewidgets import ComparisonDialog, compare_preflight, line_differences, MAX_COMPARE_BYTES, MAX_COMPARE_LINES
from devatlas.models import Recipe
from devatlas.personal import PersonalStore
from devatlas.theme import apply_theme
from test_core import sample
from test_ui_extended import compact_window, small_catalog

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def unexpected_dialogs_fail(monkeypatch):
    monkeypatch.setattr(QMessageBox, "warning", lambda parent, title, text: pytest.fail(title + ": " + text))


def saved_entry(name="Lavoro", rid="a" * 32):
    return {"id": rid, "name": name, "text": "json", "filters": {"scope": "code"}, "navigation": {"special": "personal"}}


def pair():
    left, right = sample("python-old"), sample("python-new")
    left.update(title="Versione iniziale")
    right.update(title="Versione aggiornata")
    left["assets"][0]["content"] = "name='{{project_name}}'\nkeep=1\nremove_me=2\nstable=3\nold=4\nfinish=5\n"
    right["assets"][0]["content"] = "name='{{project_name}}'\nkeep=1\nstable=3\nnew=5\nfinish=5\nextra=6\n"
    return {left["id"]: Recipe(left), right["id"]: Recipe(right)}


@pytest.fixture
def comparison(qtbot):
    dialog = ComparisonDialog(pair(), {"python": {"label": "Python"}}, left_id="python-old", right_id="python-new")
    qtbot.addWidget(dialog)
    dialog.resize(1000, 650)
    dialog.show()
    qtbot.waitUntil(lambda: dialog.diff_result is not None, timeout=5000)
    yield dialog
    dialog.reject()


def test_saved_validation_normalizes_names_without_mutation():
    item = saved_entry("  Caffe\u0301  ")
    value = {"version": 1, "items": [item]}
    result = validate_saved_searches(value)
    assert result[0]["name"] == "Caffé"
    assert item["name"] == "  Caffe\u0301  "
    with pytest.raises(ValueError, match="già"):
        validate_saved_searches({"version": 1, "items": [saved_entry("CAFÉ"), saved_entry("cafe\u0301", "b" * 32)]})


@pytest.mark.parametrize("change", [
    {"name": ""}, {"name": "x" * 81}, {"name": "a\nb"}, {"text": "x" * 2001},
    {"filters": {"scope": "unknown"}}, {"navigation": {"ids": ["personal-gone"]}},
    {"navigation": {"only_projects": 1}}, {"navigation": {"special": "unknown"}},
])
def test_saved_preflight_rejects_invalid_payload(change):
    with pytest.raises(ValueError):
        validate_saved_searches({"version": 1, "items": [{**saved_entry(), **change}]})


def test_saved_limits_count_and_encoded_size():
    rows = [saved_entry("Ricerca " + str(i), f"{i:032x}") for i in range(100)]
    assert len(validate_saved_searches({"version": 1, "items": rows})) == 100
    with pytest.raises(ValueError):
        validate_saved_searches({"version": 1, "items": rows + [saved_entry("Ultima", "f" * 32)]})
    for row in rows:
        row["text"] = "☕" * 2000
    with pytest.raises(ValueError, match="512"):
        validate_saved_searches({"version": 1, "items": rows})


def test_saved_ui_crud_restores_text_scope_and_navigation(compact_window, qtbot, monkeypatch):
    w = compact_window
    w.search_edit.setText("json")
    w.selection_filter = {"only_projects": True}
    w.filters["scope"].setCurrentIndex(w.filters["scope"].findData("code"))
    w.filters["os"].setCurrentIndex(w.filters["os"].findData("Linux"))
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Progetti JSON", True))
    w.save_current_search()
    rid = w.active_saved_search
    assert w.navigation_item({"saved_search": rid})
    w.reset_filters()
    w.restore_saved_search(rid)
    assert w.search_edit.text() == "json"
    assert w.query().scope == "code"
    assert w.query().only_projects
    assert w.query().os == "Linux"
    w.search_edit.setText("aggiornata")
    w.update_saved_search()
    assert w.saved_searches()[0]["text"] == "aggiornata"
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Rinominata", True))
    w.rename_saved_search()
    assert w.saved_searches()[0]["name"] == "Rinominata"
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)
    w.delete_saved_search()
    assert w.saved_searches() == []
    assert w.search_edit.text() == "aggiornata"


def test_saved_missing_collection_and_deleted_personal_are_safe(compact_window, qtbot):
    w = compact_window
    cid = w.store.create_collection("Temporanea")
    entry = saved_entry()
    entry["navigation"] = {"collection": cid}
    w.write_saved_searches([entry])
    w.store.delete_collection(cid)
    w.restore_saved_search(entry["id"])
    assert w.selection_filter == {}
    assert "raccolta" in w.notice_label.text()
    data = sample("personal-removed")
    w.store.save_recipe(data)
    w.store.delete_recipe("personal-removed")
    entry["navigation"] = {"special": "personal"}
    w.write_saved_searches([entry])
    w.restore_saved_search(entry["id"])
    assert w.query().ids == []


def test_saved_corrupt_json_is_not_overwritten(compact_window, monkeypatch):
    w = compact_window
    raw = "{broken"
    with w.store.connect() as db:
        db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (SAVED_SEARCH_KEY, raw))
    errors = []
    monkeypatch.setattr(w, "show_error", lambda title, error: errors.append(str(error)))
    w.save_current_search()
    assert errors
    with w.store.connect() as db:
        assert db.execute("SELECT value FROM settings WHERE key=?", (SAVED_SEARCH_KEY,)).fetchone()[0] == raw
    assert w.saved_searches() == []
    assert "conservati" in w.notice_label.text()


def test_saved_persistence_and_backup_collection_remapping(tmp_path):
    source = PersonalStore(tmp_path / "source.sqlite")
    cid = source.create_collection("Corso")
    entry = saved_entry()
    entry["navigation"] = {"collection": cid}
    source.set_setting(SAVED_SEARCH_KEY, {"version": 1, "items": [entry]})
    reopened = PersonalStore(tmp_path / "source.sqlite")
    assert reopened.setting(SAVED_SEARCH_KEY)["items"][0]["name"] == "Lavoro"
    destination = PersonalStore(tmp_path / "destination.sqlite")
    destination.restore_data(source.backup_data())
    restored_cid = destination.collections()[0][0]
    assert destination.setting(SAVED_SEARCH_KEY)["items"][0]["navigation"]["collection"] == restored_cid


def test_dynamic_systems_scope_layout_and_personal_os(compact_window, qtbot):
    w = compact_window
    data = sample("personal-mobile")
    data.update(os=["Windows", "Android", "iOS", "Web", "FreeBSD"], personal=True)
    w.store.save_recipe(data)
    w.reload_personal()
    qtbot.waitUntil(lambda: w.index_ready, timeout=3000)
    choices = [w.filters["os"].itemData(i) for i in range(1, w.filters["os"].count())]
    assert choices == ["Windows", "Linux", "Android", "iOS", "Web", "FreeBSD"]
    grid = w.filter_panel.layout()
    scope_row = grid.getItemPosition(grid.indexOf(w.filters["scope"]))[0]
    reset_row = grid.getItemPosition(grid.count() - 1)[0]
    assert reset_row > scope_row


def test_all_46_stacks_have_dynamic_paths(qtbot, tmp_path):
    stacks, rows = {}, []
    for i in range(46):
        stack = f"tech{i:02}"
        stacks[stack] = {"label": "Tecnologia " + str(i), "group": "Ambienti aggiuntivi"}
        for j in range(2):
            data = sample(f"{stack}-{j}", stack=stack)
            data["section"] = "Inizializzazione" if j == 0 else "Codice applicativo"
            rows.append(data)
    path = tmp_path / "46.json"
    path.write_text(json.dumps({"format": "RecipeBundle", "version": 1, "stacks": stacks, "recipes": rows}), encoding="utf8")
    w = MainWindow(Catalog(path), tmp_path / "profile")
    qtbot.addWidget(w)
    paths = next(w.tree.topLevelItem(i) for i in range(w.tree.topLevelItemCount()) if w.tree.topLevelItem(i).text(0) == "Percorsi guidati")
    assert paths.childCount() == 46
    assert "46 percorsi" in w.library_summary.text()
    assert any(w.tree.topLevelItem(i).text(0) == "Ambienti aggiuntivi" for i in range(w.tree.topLevelItemCount()))
    w.close()


@pytest.mark.parametrize("left,right,added,removed,changed", [
    ("", "", 0, 0, 0), ("", "a\n", 1, 0, 0), ("a\n", "", 0, 1, 0),
    ("a\nb\n", "a\nc\n", 0, 0, 1), ("a\n", "a", 0, 0, 1), ("☕\n", "☕\n😀\n", 1, 0, 0),
])
def test_line_diff_semantics(left, right, added, removed, changed):
    result = line_differences(left, right)
    assert (result["added"], result["removed"], result["changed"]) == (added, removed, changed)
    assert result["identical"] == (left == right)


def test_diff_preflight_limits_and_worst_case_inputs():
    with pytest.raises(ValueError):
        compare_preflight("x" * (MAX_COMPARE_BYTES + 1))
    with pytest.raises(ValueError):
        compare_preflight("😀" * (MAX_COMPARE_BYTES // 4 + 1))
    with pytest.raises(ValueError):
        compare_preflight("a\n" * (MAX_COMPARE_LINES + 1))
    before = time.perf_counter()
    same_prefix = line_differences("same\n" * 5000 + "old\n", "same\n" * 5000 + "new\n")
    alternate = line_differences("a\nb\n" * 10000, "b\na\n" * 10000)
    assert same_prefix["changed"] == 1
    assert not alternate["identical"]
    assert time.perf_counter() - before < 5


def test_comparison_highlights_and_independent_parameter_copy(comparison, qtbot):
    d = comparison
    assert d.left.editor.isReadOnly() and d.right.editor.isReadOnly()
    assert d.diff_result["added"] == d.diff_result["removed"] == d.diff_result["changed"] == 1
    assert len(d.left.editor.extraSelections()) == 2
    assert len(d.right.editor.extraSelections()) == 2
    d.left.parameter_edits["project_name"].setText("../bad")
    assert not d.left.copy_button.isEnabled()
    assert not d.left.editor.isEnabled()
    assert d.right.copy_button.isEnabled()
    qtbot.mouseClick(d.right.copy_button, Qt.MouseButton.LeftButton)
    assert QApplication.clipboard().text() == d.right.rendered_asset["content"]
    d.left.parameter_edits["project_name"].setText("Sinistra")
    qtbot.waitUntil(lambda: d.left.valid and d.diff_result is not None, timeout=3000)
    qtbot.mouseClick(d.left.copy_button, Qt.MouseButton.LeftButton)
    assert "Sinistra" in QApplication.clipboard().text()
    assert "esempio" in d.right.rendered_asset["content"]


def test_comparison_selection_commands_and_unmatched_typed_text(comparison, qtbot):
    d = comparison
    d.left.asset_combo.setCurrentIndex(1)
    qtbot.waitUntil(lambda: d.diff_result is not None, timeout=3000)
    assert d.left.rendered_asset["role"] == "command"
    selected = d.left.recipe_combo.currentIndex()
    text = d.left.recipe_combo.itemText(selected)
    d.left.recipe_combo.setEditText("ricerca non selezionata")
    assert not d.left.valid
    assert d.right.copy_button.isEnabled()
    d.left.recipe_combo.setEditText(text)
    qtbot.waitUntil(lambda: d.left.valid, timeout=3000)


def test_comparison_identical_selection_clears_previous_highlights(comparison, qtbot):
    d = comparison
    d.right.recipe_combo.setCurrentIndex(d.right.recipe_combo.findData("python-old"))
    qtbot.waitUntil(lambda: d.diff_result is not None and d.diff_result["identical"], timeout=3000)
    assert d.left.editor.extraSelections() == []
    assert d.right.editor.extraSelections() == []


def test_comparison_scroll_sync_can_be_disabled(qtbot):
    recipes = pair()
    for recipe in recipes.values():
        recipe.data["assets"][0]["content"] = "\n".join("riga " + str(i) for i in range(250))
    d = ComparisonDialog(recipes, {"python": {"label": "Python"}}, left_id="python-old", right_id="python-new")
    qtbot.addWidget(d)
    d.resize(950, 600)
    d.show()
    qtbot.waitUntil(lambda: d.diff_result is not None, timeout=3000)
    d.left.editor.verticalScrollBar().setValue(30)
    assert d.right.editor.verticalScrollBar().value() == 30
    d.sync_scroll.setChecked(False)
    d.left.editor.verticalScrollBar().setValue(50)
    assert d.right.editor.verticalScrollBar().value() == 30
    d.reject()


def test_main_comparison_dialog_does_not_modify_reader_parameters(compact_window, qtbot):
    w = compact_window
    w.open_recipe("python-copy")
    original = dict(w.current_parameters)
    def interact():
        d = QApplication.activeModalWidget()
        assert isinstance(d, ComparisonDialog)
        d.left.parameter_edits["project_name"].setText("SoloConfronto")
        d.reject()
    QTimer.singleShot(0, interact)
    w.compare_current()
    assert w.current_parameters == original


@pytest.mark.parametrize("method", ["compare_current", "edit_recipe", "edit_note", "show_help"])
def test_main_modal_dialogs_release_native_resources(compact_window, qtbot, method):
    w = compact_window
    w.open_recipe("python-copy")
    seen = []
    def close():
        dialog = QApplication.activeModalWidget()
        assert isinstance(dialog, QDialog)
        seen.append(dialog)
        if hasattr(dialog, "dirty"):
            dialog.dirty = False
        dialog.reject()
    QTimer.singleShot(0, close)
    getattr(w, method)(w.current_recipe) if method == "edit_recipe" else getattr(w, method)()
    assert len(seen) == 1
    QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert not isValid(seen[0])


@pytest.mark.parametrize("kind", ["collection", "saved_search"])
def test_ephemeral_context_menus_release_native_resources(compact_window, qtbot, kind):
    w = compact_window
    if kind == "collection":
        value = w.store.create_collection("Menu sintetico")
    else:
        value = "a" * 32
        w.write_saved_searches([saved_entry()])
    w.rebuild_navigation()
    item = w.navigation_item({kind: value})
    w.tree.setCurrentItem(item)
    w.tree.scrollToItem(item)
    qtbot.wait(20)
    seen = []
    def close():
        menu = QApplication.activePopupWidget()
        assert isinstance(menu, QMenu)
        seen.append(menu)
        menu.close()
    QTimer.singleShot(0, close)
    w.collection_context_menu(w.tree.visualItemRect(item).center())
    assert len(seen) == 1
    QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert not isValid(seen[0])


def test_comparison_never_executes_assets(qtbot, tmp_path):
    recipes = pair()
    target = tmp_path / "must-not-exist.txt"
    recipes["python-old"].data["assets"][0]["content"] = f"from pathlib import Path\nPath({str(target)!r}).write_text('eseguito')\n"
    d = ComparisonDialog(recipes, {"python": {"label": "Python"}}, left_id="python-old", right_id="python-new")
    qtbot.addWidget(d)
    d.show()
    qtbot.waitUntil(lambda: d.diff_result is not None, timeout=3000)
    d.left.copy()
    assert not target.exists()
    d.reject()


def test_comparison_large_asset_and_expansion_are_rejected(qtbot):
    recipes = pair()
    recipes["python-old"].data["assets"][0]["content"] = "x\n" * (MAX_COMPARE_LINES + 1)
    d = ComparisonDialog(recipes, {"python": {"label": "Python"}}, left_id="python-old", right_id="python-new")
    qtbot.addWidget(d)
    assert not d.left.valid and d.right.valid
    assert "20.000" in d.left.error_label.text()
    d.reject()
    recipes = pair()
    recipes["python-old"].data["parameters"] = [{"name": "note", "label": "Nota", "type": "string", "default": "x" * 1000}]
    recipes["python-old"].data["assets"][0].update(path="demo.txt", content="{{note}}" * 5000)
    d = ComparisonDialog(recipes, {"python": {"label": "Python"}}, left_id="python-old", right_id="python-new")
    qtbot.addWidget(d)
    assert not d.left.valid and "2 MiB" in d.left.error_label.text()
    d.reject()


def test_diff_worker_is_responsive_and_discards_stale_results(qtbot, monkeypatch):
    from devatlas import codewidgets as module
    original = module.line_differences
    started, release = threading.Event(), threading.Event()
    calls = []
    def slow(left, right):
        calls.append((left, right))
        if len(calls) == 1:
            started.set()
            assert release.wait(5)
        return original(left, right)
    monkeypatch.setattr(module, "line_differences", slow)
    d = ComparisonDialog(pair(), {"python": {"label": "Python"}}, left_id="python-old", right_id="python-new")
    qtbot.addWidget(d)
    d.show()
    qtbot.waitUntil(started.is_set, timeout=3000)
    pings = []
    QTimer.singleShot(0, lambda: pings.append(True))
    qtbot.waitUntil(lambda: bool(pings), timeout=1000)
    d.right.parameter_edits["project_name"].setText("Aggiornato")
    qtbot.waitUntil(lambda: d.right.valid, timeout=3000)
    release.set()
    qtbot.waitUntil(lambda: d.diff_result is not None, timeout=3000)
    assert d.diff_result == original(d.left.rendered_asset["content"], d.right.rendered_asset["content"])
    assert "Aggiornato" in d.right.rendered_asset["content"]
    d.reject()


def test_comparison_theme_and_screenshot(comparison, qtbot):
    d = comparison
    output = ROOT / "reports/ui-state/1.2-offscreen"
    output.mkdir(parents=True, exist_ok=True)
    for theme in ("light", "dark"):
        apply_theme(QApplication.instance(), theme)
        qtbot.wait(40)
        assert d.grab().save(str(output / f"comparison-{theme}.png"))
        assert all(p.copy_button.geometry().bottom() <= p.height() for p in (d.left, d.right))
    apply_theme(QApplication.instance(), "light")


def test_saved_search_screenshot_and_small_layout(compact_window, qtbot, monkeypatch):
    w = compact_window
    w.search_edit.setText("json")
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Ricerca JSON", True))
    w.save_current_search()
    w.resize(800, 600)
    w.filter_panel.show()
    qtbot.wait(150)
    assert w.width() == 800
    assert w.save_search_button.isVisible()
    assert w.save_search_button.geometry().right() <= w.save_search_button.parentWidget().width()
    output = ROOT / "reports/ui-state/1.2-offscreen"
    output.mkdir(parents=True, exist_ok=True)
    assert w.grab().save(str(output / "saved-searches-800.png"))
    w.resize(1280, 800)
    w.filter_panel.hide()
    qtbot.wait(100)
    assert w.grab().save(str(output / "saved-searches-1280.png"))


@pytest.mark.parametrize("scale", ["1.5", "2"])
def test_comparison_qt_dpi_layout(scale, tmp_path):
    script = r'''
import sys,json
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root));sys.path.insert(0,str(root/'tests'))
from devatlas.qt_bootstrap import configure_qt_plugins
configure_qt_plugins()
from PySide6.QtWidgets import QApplication,QDialogButtonBox
from PySide6.QtCore import QTimer
from devatlas.codewidgets import ComparisonDialog
from test_productivity import pair
app=QApplication([])
d=ComparisonDialog(pair(),{'python':{'label':'Python'}},left_id='python-old',right_id='python-new')
d.resize(950,650);d.show()
def finish():
    if d.diff_result is None: return
    buttons=d.findChild(QDialogButtonBox)
    assert buttons.geometry().bottom()<=d.height()
    output=root/'reports/ui-state/1.2-offscreen';output.mkdir(parents=True,exist_ok=True)
    assert d.grab().save(str(output/('comparison-dpi-'+sys.argv[2]+'.png')))
    print(json.dumps({'dpr':d.devicePixelRatioF(),'width':d.width()}))
    d.reject();app.quit()
timer=QTimer();timer.timeout.connect(finish);timer.start(50)
QTimer.singleShot(10000,app.quit)
app.exec()
assert d.diff_result is not None
'''
    result = subprocess.run([sys.executable, "-c", script, str(ROOT), scale], cwd=ROOT,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen", "QT_SCALE_FACTOR": scale, "PYTHONIOENCODING": "utf8"},
        capture_output=True, text=True, encoding="utf8", timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout.strip().splitlines()[-1])
    assert data["dpr"] == pytest.approx(float(scale))
    assert data["width"] == 950
