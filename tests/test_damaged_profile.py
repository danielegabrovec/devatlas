import json
from copy import deepcopy
from devatlas.catalog import Catalog
from devatlas.personal import PersonalStore
from devatlas.bundles import load_bundle, save_bundle
from test_core import sample


def test_one_damaged_personal_payload_does_not_hide_healthy_recipes_or_destroy_data(tmp_path):
    store = PersonalStore(tmp_path / "personali.sqlite")
    good = store.save_recipe(sample())
    broken_id = "personal-broken"
    raw = '{"title": "incompleto"'
    with store.connect() as db:
        db.execute("INSERT INTO recipes VALUES (?,?)", (broken_id, raw))
    store.annotate(broken_id, note="Nota da conservare")
    catalog_file = tmp_path / "catalog.json"
    catalog_file.write_text(json.dumps({"format": "RecipeBundle", "version": 1, "stacks": {"python": {"label": "Python"}}, "recipes": [sample()]}), encoding="utf-8")
    catalog = Catalog(catalog_file)
    merged = catalog.merged(store.list_recipes())
    assert good in merged and broken_id not in merged
    assert catalog.personal_errors[0]["id"] == broken_id
    with store.connect() as db:
        assert db.execute("SELECT payload FROM recipes WHERE id=?", (broken_id,)).fetchone()[0] == raw
    assert store.annotation(broken_id)[1] == "Nota da conservare"


def test_backup_preserves_bad_payload_text_but_restores_only_valid_recipes(tmp_path):
    store = PersonalStore(tmp_path / "source.sqlite")
    good = store.save_recipe(sample())
    raw = 'not valid JSON\\nwith original text'
    with store.connect() as db:
        db.execute("INSERT INTO recipes VALUES ('personal-broken',?)", (raw,))
    backup = store.backup_data()
    assert [r["id"] for r in backup["recipes"]] == [good]
    assert backup["recipes_recovery"] == [{"id": "personal-broken", "payload": raw}]
    bundle = tmp_path / "backup.zip"
    save_bundle(bundle, backup["recipes"], personal=backup)
    recovered = load_bundle(bundle)["personal"]
    assert recovered["recipes_recovery"][0]["payload"] == raw
    target = PersonalStore(tmp_path / "target.sqlite")
    target.restore_data(recovered)
    assert [r["id"] for r in target.list_recipes()] == [good]

