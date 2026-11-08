from contextlib import contextmanager
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import zipfile

import pytest

from devatlas import bundles
from devatlas.bundles import export_files, export_project, load_bundle, save_bundle, validate_recipe
from devatlas.personal import PersonalStore, import_recipes
from devatlas.templating import render_recipe, safe_relative
from test_core import sample


def write_payload(path, payload):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr("bundle.json", json.dumps(payload, ensure_ascii=False))


def personal_recipe(rid="personal-example"):
    data = sample(rid)
    data["personal"] = True
    return data


@pytest.mark.parametrize("path", [".", "a/./b", "a//b", "a/", "NUL .txt", "COM¹.log", None])
def test_ambiguous_or_windows_device_paths_are_rejected(path):
    with pytest.raises(ValueError):
        safe_relative(path)


@pytest.mark.parametrize("paths", [["src", "src/main.py"], ["SRC/main.py", "src"],
                                 ["café.py", "cafe\u0301.py"], ["Code.py", "code.py"]])
def test_file_directory_and_unicode_collisions_fail_before_export(tmp_path, paths):
    data = sample()
    data["assets"] = [{"path": path, "role": "file", "content": "original"} for path in paths]
    with pytest.raises(ValueError):
        export_project(data, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_readme_name_does_not_conflict_with_an_exported_directory():
    data = sample()
    data["assets"][0]["path"] = "README.md/original.txt"
    files = export_files(data)
    assert "README.md/original.txt" in files
    assert "README-DEVATLAS.md" in files


@pytest.mark.parametrize("kind", ["identifier", "namespace", "port", "path", "string"])
def test_empty_optional_parameters_are_supported(kind):
    data = sample()
    data["parameters"] = [{"name": "optional", "type": kind, "required": False, "default": ""}]
    data["assets"][0].update(path="plain.txt", content="before{{optional}}after")
    assert render_recipe(data)["assets"][0]["content"] == "beforeafter"


@pytest.mark.parametrize("definition", [{"name": "x", "type": "unsupported"},
    {"name": "x", "required": "false"}, {"name": "x", "default": float("nan")}, "x"])
def test_invalid_parameter_definitions_have_readable_errors(definition):
    data = sample()
    data["parameters"] = [definition]
    with pytest.raises(ValueError):
        render_recipe(data)


@pytest.mark.parametrize("value", ["²", "٣٠٠٠", "0", "65536"])
def test_port_parameters_require_an_ascii_port_number(value):
    data = sample()
    data["parameters"] = [{"name": "port", "type": "port", "default": "8000"}]
    with pytest.raises(ValueError):
        render_recipe(data, {"port": value})


def test_duplicate_parameters_unknown_values_and_bad_unicode_are_rejected():
    data = sample()
    data["parameters"] *= 2
    with pytest.raises(ValueError, match="univoci"):
        render_recipe(data)
    with pytest.raises(ValueError, match="non dichiarati"):
        render_recipe(sample(), {"wrong_name": "x"})
    data = sample()
    data["assets"][0]["content"] = "invalid \ud800"
    with pytest.raises(ValueError, match="Unicode"):
        validate_recipe(data)


@pytest.mark.parametrize("change", [lambda d: d.update(assets=[None]),
    lambda d: d.update(variants=["wrong"]), lambda d: d.update(group=[]),
    lambda d: d.update(verification={"details": []}), lambda d: d.update(project="yes"),
    lambda d: d["assets"][1].update(cwd="first\nsecond")])
def test_nested_recipe_schema_rejected_before_persistence(tmp_path, change):
    store = PersonalStore(tmp_path / "personal.sqlite")
    store.save_recipe(sample())
    before = store.backup_data()
    data = personal_recipe()
    change(data)
    with pytest.raises(ValueError):
        store.save_recipe(data)
    assert store.backup_data() == before


@pytest.mark.parametrize("payload", [[], {"format": "RecipeBundle", "version": True},
    {"format": "RecipeBundle", "version": 1, "recipes": [], "personal": {"annotations": [None]}},
    {"format": "RecipeBundle", "version": 1, "recipes": [], "personal": {"settings": {"zoom": "huge"}}},
    {"format": "RecipeBundle", "version": 1, "recipes": [], "personal": {"collections": [], "collection_items": [["missing", "python-json"]]}}])
def test_malformed_bundle_schema_is_reported_as_value_error(tmp_path, payload):
    path = tmp_path / "invalid.zip"
    write_payload(path, payload)
    with pytest.raises(ValueError):
        load_bundle(path)


def test_duplicate_json_keys_and_crc_damage_are_rejected(tmp_path):
    duplicate = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(duplicate, "w") as archive:
        archive.writestr("bundle.json", '{"format":"RecipeBundle","version":1,"version":2,"recipes":[]}')
    with pytest.raises(ValueError, match="duplicata"):
        load_bundle(duplicate)
    damaged = tmp_path / "crc.zip"
    write_payload(damaged, {"format": "RecipeBundle", "version": 1, "recipes": []})
    raw = damaged.read_bytes().replace(b"RecipeBundle", b"RecipeBunXle", 1)
    damaged.write_bytes(raw)
    with pytest.raises(ValueError, match="ZIP"):
        load_bundle(damaged)


def test_duplicate_recipe_ids_and_disagreeing_backup_sections_fail(tmp_path):
    data = personal_recipe()
    path = tmp_path / "duplicate.zip"
    write_payload(path, {"format": "RecipeBundle", "version": 1, "recipes": [data, data]})
    with pytest.raises(ValueError, match="duplicati"):
        load_bundle(path)
    other = tmp_path / "mismatch.zip"
    write_payload(other, {"format": "RecipeBundle", "version": 1, "recipes": [], "personal": {"recipes": [data]}})
    with pytest.raises(ValueError, match="corrispondono"):
        load_bundle(other)


def test_bundle_size_limit_is_applied_before_json_import(tmp_path, monkeypatch):
    path = tmp_path / "large.zip"
    write_payload(path, {"format": "RecipeBundle", "version": 1, "recipes": [sample()]})
    monkeypatch.setattr(bundles, "MAX_BUNDLE_BYTES", 100)
    with pytest.raises(ValueError, match="grande"):
        load_bundle(path)


@pytest.mark.parametrize("bundle", [False, True])
def test_failed_zip_write_never_leaves_a_partial_destination(tmp_path, monkeypatch, bundle):
    target = tmp_path / "export.zip"
    original = zipfile.ZipFile.writestr
    calls = 0
    def fail(archive, *args, **kwargs):
        nonlocal calls
        calls += 1
        if bundle or calls == 2:
            raise OSError("simulated disk failure")
        return original(archive, *args, **kwargs)
    monkeypatch.setattr(zipfile.ZipFile, "writestr", fail)
    with pytest.raises(OSError):
        if bundle:
            save_bundle(target, [sample()])
        else:
            export_project(sample(), target, zipped=True)
    assert not target.exists()
    assert not list(tmp_path.glob(".devatlas-*"))


@pytest.mark.parametrize("existing", [False, True])
def test_failed_directory_export_keeps_destination_absent_or_empty(tmp_path, monkeypatch, existing):
    target = tmp_path / "export"
    if existing:
        target.mkdir()
    data = sample()
    data["assets"] = [{"path": "one.txt", "role": "file", "content": "first"},
                      {"path": "two.txt", "role": "file", "content": "second"}]
    original = Path.open
    def fail(path, *args, **kwargs):
        if path.name == "two.txt" and args and args[0] == "x":
            raise OSError("simulated full disk")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", fail)
    with pytest.raises(OSError):
        export_project(data, target)
    assert target.exists() == existing
    assert not existing or list(target.iterdir()) == []
    assert not list(tmp_path.glob(".devatlas-export-*"))


def test_failed_directory_publication_restores_preexisting_empty_folder(tmp_path, monkeypatch):
    target = tmp_path / "export"
    target.mkdir()
    monkeypatch.setattr(bundles.os, "rename", lambda *args: (_ for _ in ()).throw(OSError("rename failed")))
    with pytest.raises(OSError):
        export_project(sample(), target)
    assert target.is_dir() and not list(target.iterdir())
    assert not list(tmp_path.glob(".devatlas-export-*"))


def test_archive_publication_does_not_replace_a_file_created_during_export(tmp_path, monkeypatch):
    target = tmp_path / "export.zip"
    original = bundles._publish_file
    def concurrent_file(temporary, destination):
        destination.write_bytes(b"another writer")
        return original(temporary, destination)
    monkeypatch.setattr(bundles, "_publish_file", concurrent_file)
    with pytest.raises(FileExistsError):
        save_bundle(target, [sample()])
    assert target.read_bytes() == b"another writer"
    assert not list(tmp_path.glob(".devatlas-*"))


def test_import_remaps_markdown_links_but_preserves_sources_and_builtin_links():
    first, second = personal_recipe("personal-first"), personal_recipe("personal-second")
    first["related"] = [second["id"], "python-json"]
    first["guide"] = "[Seconda](recipe://personal-second) [Catalogo](recipe://python-json)"
    first["assets"][0]["content"] = "recipe://personal-second"
    before = deepcopy([first, second])
    rows, mapping = import_recipes([first, second], force_new=True)
    assert rows[0]["related"] == [mapping["personal-second"], "python-json"]
    assert f"recipe://{mapping['personal-second']}" in rows[0]["guide"]
    assert "recipe://python-json" in rows[0]["guide"]
    assert rows[0]["assets"][0]["content"] == "recipe://personal-second"
    assert [first, second] == before


def test_import_and_restore_failures_roll_back_all_changes(tmp_path):
    store = PersonalStore(tmp_path / "personal.sqlite")
    store.save_recipe(sample())
    before = store.backup_data()
    invalid = personal_recipe("personal-invalid")
    invalid["assets"] = []
    with pytest.raises(ValueError):
        store.import_recipes([personal_recipe(), invalid])
    assert store.backup_data() == before
    with store.connect() as db:
        db.execute("CREATE TRIGGER fail_note BEFORE INSERT ON annotations WHEN NEW.note='fail' BEGIN SELECT RAISE(ABORT,'simulated failure'); END")
    data = {"recipes": [personal_recipe()], "annotations": [{"id": "personal-example", "note": "fail", "favorite": 1}], "settings": {"theme": "dark"}}
    with pytest.raises(sqlite3.IntegrityError):
        store.restore_data(data)
    assert store.backup_data() == before


def test_corrupt_settings_fall_back_without_rewriting_or_bricking_profile(tmp_path):
    store = PersonalStore(tmp_path / "personal.sqlite")
    with store.connect() as db:
        db.execute("INSERT INTO settings VALUES ('zoom','\"bad\"')")
    assert store.setting("zoom", 0) == 0
    with store.connect() as db:
        assert db.execute("SELECT value FROM settings WHERE key='zoom'").fetchone()[0] == '"bad"'
    with pytest.raises(ValueError):
        store.restore_data({"settings": {"zoom": "still bad"}})
    assert store.setting("zoom", 0) == 0
    store.set_setting("future-option", {"text": "Caffè ☕", "values": [1, 2]})
    assert store.setting("future-option")["text"] == "Caffè ☕"


def test_future_schema_version_is_not_silently_downgraded(tmp_path):
    path = tmp_path / "future.sqlite"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE sentinel(value TEXT)")
        db.execute("INSERT INTO sentinel VALUES ('preserve')")
        db.execute("PRAGMA user_version=99")
    with pytest.raises(ValueError, match="recente"):
        PersonalStore(path)
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 99
        assert db.execute("SELECT value FROM sentinel").fetchone()[0] == "preserve"


def test_backup_recovers_content_despite_legacy_corrupt_preferences_without_mutating_db(tmp_path):
    store = PersonalStore(tmp_path / "source.sqlite")
    rid = store.save_recipe(sample())
    store.annotate(rid, favorite=True, note="Nota da preservare ☕")
    store.set_setting("theme", "dark")
    with store.connect() as db:
        db.executemany("INSERT INTO settings VALUES (?,?)", [("zoom", '"bad"'), ("broken-json", "{not JSON")])
    backup = store.backup_data()
    assert backup["settings"] == {"theme": "dark"}
    assert backup["settings_recovery"] == {"zoom": '"bad"', "broken-json": "{not JSON"}
    with store.connect() as db:
        assert dict(db.execute("SELECT key,value FROM settings")) == {"theme": '"dark"', "zoom": '"bad"', "broken-json": "{not JSON"}
    path = tmp_path / "recovery.zip"
    save_bundle(path, backup["recipes"], personal=backup)
    loaded = load_bundle(path)
    assert loaded["personal"]["settings_recovery"] == backup["settings_recovery"]
    restored = PersonalStore(tmp_path / "restored.sqlite")
    restored.restore_data(loaded["personal"])
    assert len(restored.list_recipes()) == 1
    assert restored.annotation(rid) == (True, "Nota da preservare ☕")
    assert restored.setting("theme") == "dark"
    assert restored.setting("zoom", 0) == 0


def test_collection_rename_delete_and_rollback_preserve_recipe_data(tmp_path):
    store = PersonalStore(tmp_path / "personal.sqlite")
    rid = store.save_recipe(sample())
    store.annotate(rid, favorite=True, note="preserve")
    first, second = store.create_collection("Café"), store.create_collection("Altro")
    store.add_to_collection(first, rid)
    with pytest.raises(ValueError, match="già"):
        store.rename_collection(second, "CAFE\u0301")
    with pytest.raises(ValueError):
        store.rename_collection(first, " \n ")
    store.rename_collection(first, "Rinominata")
    with store.connect() as db:
        db.execute("CREATE TRIGGER fail_delete BEFORE DELETE ON collections BEGIN SELECT RAISE(ABORT,'simulated failure'); END")
    with pytest.raises(sqlite3.IntegrityError):
        store.delete_collection(first)
    assert store.collection_ids(first) == [rid]
    with store.connect() as db:
        db.execute("DROP TRIGGER fail_delete")
    store.delete_collection(first)
    assert store.collection_ids(first) == []
    assert len(store.list_recipes()) == 1
    assert store.annotation(rid) == (True, "preserve")
    with pytest.raises(ValueError, match="non esiste"):
        store.add_to_collection(first, rid)


def test_backup_is_one_consistent_snapshot_during_concurrent_writes(tmp_path, monkeypatch):
    store = PersonalStore(tmp_path / "personal.sqlite")
    other = PersonalStore(store.path)
    rid = store.save_recipe(sample(title="old"))
    store.annotate(rid, note="old")
    with store.connect() as db:
        db.execute("PRAGMA journal_mode=WAL")
    original_connect = store.connect
    fired = False
    @contextmanager
    def hooked_connect():
        nonlocal fired
        with original_connect() as db:
            def trace(sql):
                nonlocal fired
                if "SELECT * FROM annotations" in sql and not fired:
                    fired = True
                    data = other.list_recipes()[0]
                    data["title"] = "new"
                    other.save_recipe(data)
                    other.annotate(rid, note="new")
            db.set_trace_callback(trace)
            yield db
    monkeypatch.setattr(store, "connect", hooked_connect)
    backup = store.backup_data()
    assert fired
    assert backup["recipes"][0]["title"] == "old"
    assert backup["annotations"][0]["note"] == "old"
    assert other.list_recipes()[0]["title"] == "new"
    assert other.annotation(rid)[1] == "new"


def test_unicode_filename_and_content_are_identical_in_folder_zip_and_bundle(tmp_path):
    data = sample()
    filename = "src/Δοκιμή ☕😀.txt"
    content = "café cafe\u0301 漢字 👩‍💻\r\nseconda riga\n"
    data["assets"] = [{"path": filename, "role": "file", "content": content}]
    export_project(data, tmp_path / "folder")
    assert (tmp_path / "folder" / filename).read_bytes() == content.encode("utf-8")
    export_project(data, tmp_path / "project.zip", zipped=True)
    with zipfile.ZipFile(tmp_path / "project.zip") as archive:
        assert archive.read(filename) == content.encode("utf-8")
    save_bundle(tmp_path / "recipe.zip", [data])
    assert load_bundle(tmp_path / "recipe.zip")["recipes"][0]["assets"][0]["content"] == content


def test_directory_publication_preserves_files_created_by_another_writer(tmp_path, monkeypatch):
    target = tmp_path / "export"
    original = bundles.os.rename
    def concurrent_directory(stage, destination):
        destination.mkdir()
        (destination / "preserve.txt").write_text("another writer", encoding="utf-8")
        original(stage, destination)
    monkeypatch.setattr(bundles.os, "rename", concurrent_directory)
    with pytest.raises(OSError):
        export_project(sample(), target)
    assert (target / "preserve.txt").read_text(encoding="utf-8") == "another writer"
    assert list(target.iterdir()) == [target / "preserve.txt"]
    assert not list(tmp_path.glob(".devatlas-export-*"))


def test_legacy_v0_profile_is_upgraded_without_resetting_existing_content(tmp_path):
    path = tmp_path / "legacy.sqlite"
    store = PersonalStore(path)
    rid = store.save_recipe(sample())
    store.annotate(rid, favorite=True, note="Preserva la nota")
    store.set_setting("theme", "dark")
    with store.connect() as db:
        db.execute("PRAGMA user_version=0")
    reopened = PersonalStore(path)
    assert reopened.list_recipes()[0]["id"] == rid
    assert reopened.annotation(rid) == (True, "Preserva la nota")
    assert reopened.setting("theme") == "dark"
    with reopened.connect() as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 1


def test_v1_backup_accepts_different_recipe_order_and_preserves_future_metadata(tmp_path):
    first, second = personal_recipe("personal-first"), personal_recipe("personal-second")
    payload = {"format": "RecipeBundle", "version": 1, "recipes": [first, second],
               "personal": {"recipes": [second, first], "settings": {"future-option": {"value": "caffè"}}},
               "future_metadata": {"description": "compatibilità"}}
    path = tmp_path / "v1.zip"
    write_payload(path, payload)
    assert load_bundle(path) == payload
