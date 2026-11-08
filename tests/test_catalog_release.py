import hashlib
import json
from copy import deepcopy
from pathlib import Path
import pytest
from devatlas.catalog import Catalog
from test_core import sample


def write_catalog(tmp_path, **changes):
    data = {"format": "RecipeBundle", "version": 1, "stacks": {"python": {"label": "Python", "group": "Linguaggi"}}, "recipes": [sample()]}
    data.update(changes)
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.mark.parametrize("records", [None, {}, [sample(), sample()], [{"id": "broken"}]])
def test_catalog_rejects_malformed_records(tmp_path, records):
    with pytest.raises(ValueError):
        Catalog(write_catalog(tmp_path, recipes=records))


def test_catalog_rejects_unknown_technology(tmp_path):
    record = sample()
    record["stack"] = "missing"
    with pytest.raises(ValueError, match="Tecnologia"):
        Catalog(write_catalog(tmp_path, recipes=[record]))


def test_catalog_boolean_is_not_a_valid_format_version(tmp_path):
    with pytest.raises(ValueError, match="Formato"):
        Catalog(write_catalog(tmp_path, version=True))


def test_catalog_rejects_tampered_source(tmp_path):
    record = sample()
    record["assets"][0]["sha256"] = hashlib.sha256(b"different source").hexdigest()
    with pytest.raises(ValueError, match="checksum"):
        Catalog(write_catalog(tmp_path, recipes=[record]))


def test_catalog_rejects_duplicate_keys_and_nonfinite_numbers(tmp_path):
    path = write_catalog(tmp_path)
    text = path.read_text(encoding="utf-8").replace('"version": 1', '"version": 2, "version": 1', 1)
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicato"):
        Catalog(path)
    with pytest.raises(ValueError, match="JSON"):
        Catalog(write_catalog(tmp_path, unexpected=float("nan")))


def test_invalid_personal_record_is_preserved_and_reported_without_overriding_catalog(tmp_path):
    catalog = Catalog(write_catalog(tmp_path))
    broken = sample()
    valid = sample("personal-valid")
    original = deepcopy([broken, valid])
    merged = catalog.merged([broken, valid])
    assert set(merged) == {"python-json", "personal-valid"}
    assert catalog.personal_errors and catalog.personal_errors[0]["id"] == "python-json"
    assert [broken, valid] == original
    assert not merged["python-json"].personal

