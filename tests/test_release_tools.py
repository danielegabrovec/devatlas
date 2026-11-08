import json
from pathlib import Path
import pytest
from tools import build_windows, release_support


def test_stale_application_cannot_be_packaged_as_current(tmp_path):
    (tmp_path / "devatlas").mkdir()
    (tmp_path / "reports").mkdir()
    (tmp_path / "build/run_devatlas.dist").mkdir(parents=True)
    source = tmp_path / "devatlas/app.py"
    source.write_text("old = True", encoding="utf-8")
    binary = tmp_path / "build/run_devatlas.dist/DevAtlas.exe"
    binary.write_bytes(b"compiled old")
    state = {"version": release_support.VERSION, "source_hashes": release_support.code_state(tmp_path),
             "executable_sha256": release_support.sha256(binary)}
    (tmp_path / "reports/build-state.json").write_text(json.dumps(state), encoding="utf-8")
    release_support.assert_build_current(tmp_path)
    source.write_text("old = False", encoding="utf-8")
    with pytest.raises(ValueError, match="sorgenti"):
        release_support.assert_build_current(tmp_path)


def test_checksum_manifest_detects_modification_missing_and_unexpected_files(tmp_path):
    (tmp_path / "dist").mkdir()
    files = release_support.release_files(tmp_path)
    for index, file in enumerate(files):
        file.write_bytes(bytes([index]))
    release_support.write_checksums(tmp_path)
    assert release_support.verify_checksums(tmp_path)
    files[0].write_bytes(b"modified")
    with pytest.raises(ValueError, match="Checksum"):
        release_support.verify_checksums(tmp_path)


def test_clean_release_preserves_portable_profile_and_keeps_previous_tree(tmp_path, monkeypatch):
    monkeypatch.setattr(build_windows, "ROOT", tmp_path)
    stage = tmp_path / ".cache/stage/new"
    stage.mkdir(parents=True)
    (stage / "DevAtlas.exe").write_bytes(b"new")
    destination = tmp_path / "dist" / release_support.RELEASE_NAME
    (destination / "dati-personali").mkdir(parents=True)
    (destination / "DevAtlas.exe").write_bytes(b"old")
    (destination / "obsolete.dll").write_bytes(b"stale")
    (destination / "dati-personali/personali.sqlite").write_bytes(b"personal data")
    backup = build_windows.publish(stage, destination)
    assert (destination / "DevAtlas.exe").read_bytes() == b"new"
    assert (destination / "dati-personali/personali.sqlite").read_bytes() == b"personal data"
    assert not (destination / "obsolete.dll").exists()
    assert (Path(backup) / "obsolete.dll").read_bytes() == b"stale"


def test_publish_refuses_a_live_profile_without_moving_anything(tmp_path, monkeypatch):
    from PySide6.QtCore import QLockFile
    monkeypatch.setattr(build_windows, "ROOT", tmp_path)
    stage = tmp_path / ".cache/stage/new"
    stage.mkdir(parents=True)
    destination = tmp_path / "dist" / release_support.RELEASE_NAME
    profile = destination / "dati-personali"
    profile.mkdir(parents=True)
    active = QLockFile(str(profile / "devatlas.lock"))
    assert active.tryLock(0)
    try:
        with pytest.raises(ValueError, match="chiudi"):
            build_windows.publish(stage, destination)
        assert stage.is_dir() and destination.is_dir()
    finally:
        active.unlock()


def test_publication_refuses_computed_paths_outside_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(build_windows, "ROOT", tmp_path / "project")
    with pytest.raises(ValueError, match="fuori"):
        build_windows.publish(tmp_path / "unrelated", tmp_path / "unrelated-destination")


def test_legacy_profile_migration_copies_consistent_database_without_changing_original(tmp_path, monkeypatch):
    import sqlite3
    monkeypatch.setattr(build_windows, "ROOT", tmp_path)
    legacy = tmp_path / "dist/DevAtlas/dati-personali"
    legacy.mkdir(parents=True)
    database = legacy / "personali.sqlite"
    with sqlite3.connect(database) as db:
        db.execute("CREATE TABLE example(note TEXT)")
        db.execute("INSERT INTO example VALUES ('nota personale')")
    before = database.read_bytes()
    stage = tmp_path / ".cache/stage/new"
    stage.mkdir(parents=True)
    destination = tmp_path / "dist" / release_support.RELEASE_NAME
    assert build_windows.migrate_legacy_profile(stage, destination)
    with sqlite3.connect(stage / "dati-personali/personali.sqlite") as db:
        assert db.execute("SELECT note FROM example").fetchone()[0] == "nota personale"
    assert database.read_bytes() == before
    destination.mkdir()
    (destination / "dati-personali").mkdir()
    assert not build_windows.migrate_legacy_profile(stage, destination)


def test_legacy_catalog_migration_keeps_only_actual_local_overrides(tmp_path, monkeypatch):
    import sqlite3
    from copy import deepcopy
    from test_core import sample
    monkeypatch.setattr(build_windows, "ROOT", tmp_path)
    legacy = tmp_path / "dist/DevAtlas/dati-personali"
    legacy.mkdir(parents=True)
    with sqlite3.connect(legacy / "personali.sqlite") as db:
        db.execute("CREATE TABLE example(note TEXT)")
    old = {"format": "RecipeBundle", "version": 1, "stacks": {"python": {"label": "Python", "group": "Linguaggi"}}, "recipes": [sample(), sample("python-other")]}
    local, current = deepcopy(old), deepcopy(old)
    local["recipes"][1]["title"] = "Modifica locale da conservare"
    current["recipes"][0]["title"] = "Descrizione nuova della versione 1.1"
    for path, payload in ((tmp_path / "dist/DevAtlas/devatlas/data/catalog.json", old),
                          (legacy / "catalogo-locale.json", local), (tmp_path / "devatlas/data/catalog.json", current)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
    stage = tmp_path / ".cache/stage/new"
    stage.mkdir(parents=True)
    assert build_windows.migrate_legacy_profile(stage, tmp_path / "dist" / release_support.RELEASE_NAME)
    migrated = json.loads((stage / "dati-personali/catalogo-locale.json").read_text(encoding="utf-8"))
    titles = {r["id"]: r["title"] for r in migrated["recipes"]}
    assert titles["python-json"] == "Descrizione nuova della versione 1.1"
    assert titles["python-other"] == "Modifica locale da conservare"


def test_profile_upgrade_uses_latest_prior_version_and_preserves_originals(tmp_path, monkeypatch):
    import sqlite3
    monkeypatch.setattr(build_windows, "ROOT", tmp_path)
    for folder, value in (("DevAtlas", "old"), ("DevAtlas-1.1.0", "intermediate"), ("DevAtlas-1.2.0", "latest")):
        profile = tmp_path / "dist" / folder / "dati-personali"
        profile.mkdir(parents=True)
        with sqlite3.connect(profile / "personali.sqlite") as db:
            db.execute("CREATE TABLE example(note TEXT)")
            db.execute("INSERT INTO example VALUES (?)", (value,))
    stage = tmp_path / ".cache/stage/new"
    stage.mkdir(parents=True)
    assert build_windows.migrate_legacy_profile(stage, tmp_path / "dist/DevAtlas-1.3.0")
    with sqlite3.connect(stage / "dati-personali/personali.sqlite") as db:
        assert db.execute("SELECT note FROM example").fetchone()[0] == "latest"
    assert (tmp_path / "dist/DevAtlas-1.2.0/dati-personali/personali.sqlite").exists()

