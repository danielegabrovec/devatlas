from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import gc
from pathlib import Path
import threading
import weakref

import pytest

from devatlas.models import Recipe, SearchQuery
from devatlas.search import SearchIndex
from test_core import sample


def item(rid, title, difficulty="Base", code="oldneedle"):
    data = sample(rid, title=title)
    data.update(difficulty=difficulty, parameters=[])
    data["assets"] = [{"id": "file", "path": "main.txt", "role": "file", "content": code}]
    return Recipe(data)


def old_rows():
    return {"a": item("a", "Zulu JSON", "Avanzato"), "b": item("b", "Alpha JSON"),
            "gone": item("gone", "Gamma JSON", "Intermedio")}


def new_rows():
    return {"a": item("a", "Alpha JSON", code="newneedle"),
            "b": item("b", "Zulu JSON", "Avanzato", "newneedle"),
            "new": item("new", "Beta JSON", "Intermedio", "newneedle")}


def test_shared_rebuild_invalidates_other_engine_cache_and_all_sort_metadata(tmp_path):
    path = tmp_path / "shared.sqlite"
    first = SearchIndex(path)
    first.rebuild(old_rows(), "old")
    title = SearchQuery("json", sort="title", limit=2)
    assert first.search(title).ids == ["b", "gone"]
    assert first.search(SearchQuery("oldneedle", scope="code")).total == 3
    second = SearchIndex(path)
    assert second.generation == first.generation == 1
    second.rebuild(new_rows(), "new")
    assert first.generation == second.generation == 2
    expected = ["a", "new", "b"]
    assert first.search(title).ids + first.search(replace(title, offset=2)).ids == expected
    assert first.search(SearchQuery("", sort="title")).ids == expected
    assert first.search(SearchQuery("json", sort="difficulty")).ids == expected
    assert not first.search(SearchQuery("oldneedle", scope="code")).ids
    assert first.search(SearchQuery("newneedle", scope="code")).total == 3
    for order in ("relevance", "title", "difficulty", "recent"):
        query = SearchQuery("json", sort=order, recent_ids=["b", "b", "new"])
        assert first.search(query).ids == second.search(query).ids


def test_new_engine_search_adopts_existing_committed_snapshot_without_own_rebuild(tmp_path):
    first = SearchIndex(tmp_path / "shared.sqlite")
    first.rebuild(new_rows(), "new")
    second = SearchIndex(first.path)
    assert second.search(SearchQuery("json", sort="title")).ids == ["a", "new", "b"]
    assert second.search(SearchQuery("json", sort="difficulty")).ids == ["a", "new", "b"]
    assert second.features is first.features
    with pytest.raises(TypeError):
        second.sort_info["a"] = ("corrupted", 99)
    with pytest.raises(TypeError):
        second.field_frequency[("python", 0)]["json"] = 0


@pytest.mark.parametrize("stage", ["vocabulary", "snapshot", "publish"])
def test_failed_shared_rebuild_preserves_database_generation_and_other_cache(tmp_path, monkeypatch, stage):
    first, second = SearchIndex(tmp_path / "shared.sqlite"), SearchIndex(tmp_path / "shared.sqlite")
    first.rebuild(old_rows(), "old")
    expected = first.search(SearchQuery("json", sort="title")).ids
    generation = first.generation
    if stage == "vocabulary":
        monkeypatch.setattr(second, "_vocab", lambda path=None: (_ for _ in ()).throw(OSError("vocabulary failed")))
    elif stage == "snapshot":
        monkeypatch.setattr(second, "_freeze_snapshot", lambda: (_ for _ in ()).throw(OSError("snapshot failed")))
    else:
        original = Path.replace
        def fail(path, target):
            if path.suffix == ".building":raise OSError("publish failed")
            return original(path, target)
        monkeypatch.setattr(Path, "replace", fail)
    with pytest.raises(OSError):
        second.rebuild(new_rows(), "new", force=True)
    assert first.generation == second.generation == generation
    # Cached and fresh SQL paths both still read the previous committed corpus.
    assert first.search(SearchQuery("json", sort="title")).ids == expected
    assert second.search(SearchQuery("", sort="title")).ids == expected
    assert second.search(SearchQuery("oldneedle", scope="code")).total == 3
    assert not list(tmp_path.glob("*.building"))


def test_stale_engine_failed_rebuild_does_not_restore_a_preceding_shared_snapshot(tmp_path):
    first, second = SearchIndex(tmp_path / "shared.sqlite"), SearchIndex(tmp_path / "shared.sqlite")
    first.rebuild(old_rows(), "old")
    first.search(SearchQuery("oldneedle"))
    second.rebuild(new_rows(), "new")
    malformed = item("broken", "Broken")
    malformed.data["summary"] = None
    with pytest.raises(TypeError):
        first.rebuild({"broken": malformed}, "bad")
    assert first.generation == second.generation == 2
    assert first.search(SearchQuery("json", sort="title")).ids == ["a", "new", "b"]
    assert not first.search(SearchQuery("oldneedle", scope="code")).ids


def test_shared_generation_reads_are_immediate_and_committed_during_rebuild(tmp_path, monkeypatch):
    first, second = SearchIndex(tmp_path / "shared.sqlite"), SearchIndex(tmp_path / "shared.sqlite")
    first.rebuild(old_rows(), "old")
    generation = first.generation
    entered, release = threading.Event(), threading.Event()
    original = second._rebuild
    def paused(*args, **kwargs):
        entered.set()
        assert release.wait(5)
        return original(*args, **kwargs)
    monkeypatch.setattr(second, "_rebuild", paused)
    with ThreadPoolExecutor(max_workers=2) as pool:
        writer = pool.submit(second.rebuild, new_rows(), "new")
        try:
            assert entered.wait(3)
            result = pool.submit(lambda: (first.generation, second.generation)).result(timeout=1)
            assert result == (generation, generation)
        finally:
            release.set()
        writer.result(timeout=5)
    assert first.generation == second.generation == generation + 1
    assert first.search(SearchQuery("json", sort="title")).ids == ["a", "new", "b"]


def test_shared_snapshot_registry_does_not_keep_engines_or_state_alive(tmp_path):
    first, second = SearchIndex(tmp_path / "weak.sqlite"), SearchIndex(tmp_path / "weak.sqlite")
    first.rebuild(old_rows(), "old")
    assert first._state is second._state
    state = weakref.ref(first._state)
    del first, second
    gc.collect()
    assert state() is None
