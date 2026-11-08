from devatlas.personal import PersonalStore
from test_core import sample
import json
import pytest
from devatlas.saved_searches import merge_saved_searches


def test_saved_search_collection_reference_survives_backup_restore_with_new_ids(tmp_path):
    source = PersonalStore(tmp_path / "source.sqlite")
    rid = source.save_recipe(sample())
    cid = source.create_collection("Corso API")
    source.add_to_collection(cid, rid)
    source.set_setting("saved_searches", {"version": 1, "items": [{"id": "a" * 32, "name": "Nel corso", "text": "json",
        "filters": {"scope": "code"}, "navigation": {"collection": cid}}]})
    target = PersonalStore(tmp_path / "target.sqlite")
    target.restore_data(source.backup_data())
    restored_id = target.collections()[0][0]
    saved = target.setting("saved_searches")["items"][0]
    assert restored_id != cid
    assert saved["navigation"]["collection"] == restored_id
    assert target.collection_ids(restored_id) == [rid]
    assert source.setting("saved_searches")["items"][0]["navigation"]["collection"] == cid


def test_unknown_saved_preference_shape_does_not_abort_restoring_healthy_recipes(tmp_path):
    source = PersonalStore(tmp_path / "source.sqlite")
    rid = source.save_recipe(sample())
    with source.connect() as db:
        db.execute("INSERT INTO settings VALUES ('saved_searches',?)", (json.dumps({"version": 1, "items": [{"navigation": {"collection": []}}]}),))
    target = PersonalStore(tmp_path / "target.sqlite")
    target.restore_data(source.backup_data())
    assert target.list_recipes()[0]["id"] == rid


def search(rid, name, text="json"):
    return {"id": rid, "name": name, "text": text, "filters": {}, "navigation": {}}


def test_saved_search_merge_preserves_both_versions_of_colliding_content():
    current = {"version": 1, "items": [search("a"*32, "Corso", "python")]}
    incoming = {"version": 1, "items": [search("a"*32, "corso", "php")]}
    result = merge_saved_searches(current, incoming)
    assert len(result["items"]) == 2
    assert result["items"][0]["text"] == "python" and result["items"][1]["text"] == "php"
    assert result["items"][0]["id"] != result["items"][1]["id"]
    assert result["items"][1]["name"].endswith("(importata)")
    assert len(merge_saved_searches(current, current)["items"]) == 1


def test_restore_merges_searches_but_keeps_existing_other_preferences(tmp_path):
    source, target = PersonalStore(tmp_path/"s.sqlite"), PersonalStore(tmp_path/"t.sqlite")
    source.set_setting("saved_searches", {"version":1,"items":[search("b"*32,"Nuova")]})
    target.set_setting("saved_searches", {"version":1,"items":[search("a"*32,"Esistente")]})
    source.set_setting("theme","light")
    target.set_setting("theme","dark")
    target.restore_data(source.backup_data())
    assert len(target.setting("saved_searches")["items"]) == 2
    assert target.setting("theme") == "dark"


def test_limit_failure_rolls_back_recipe_restore_instead_of_dropping_searches(tmp_path):
    source, target = PersonalStore(tmp_path/"s.sqlite"), PersonalStore(tmp_path/"t.sqlite")
    source.save_recipe(sample())
    source.set_setting("saved_searches", {"version":1,"items":[search("f"*32,"Aggiunta")]})
    target.set_setting("saved_searches", {"version":1,"items":[search(f"{i:032x}",f"Ricerca {i}") for i in range(100)]})
    with pytest.raises(ValueError, match="100"):
        target.restore_data(source.backup_data())
    assert target.list_recipes() == []
    assert len(target.setting("saved_searches")["items"]) == 100

