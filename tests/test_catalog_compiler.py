import hashlib
import json
import pytest
from tools import compile_catalog
from test_core import sample


def canonical(tmp_path, *, tamper=False):
    recipe = sample()
    root = tmp_path / "catalog/python" / recipe["id"]
    root.mkdir(parents=True)
    recipe["guide_path"] = "guide.md"
    (root / "guide.md").write_text(recipe.pop("guide"), encoding="utf-8")
    recipe["related"] = ["python-json"]
    for index, asset in enumerate(recipe["assets"]):
        text = asset.pop("content")
        asset["source"] = f"source-{index}.txt"
        asset["sha256"] = hashlib.sha256(text.encode()).hexdigest()
        (root / asset["source"]).write_text(text + ("changed" if tamper and not index else ""), encoding="utf-8")
    metadata = root / "recipe.json"
    metadata.write_text(json.dumps(recipe), encoding="utf-8")
    return metadata


def test_bad_catalog_build_keeps_previous_runtime_file(tmp_path, monkeypatch):
    monkeypatch.setattr(compile_catalog, "ROOT", tmp_path)
    canonical(tmp_path, tamper=True)
    runtime = tmp_path / "devatlas/data/catalog.json"
    runtime.parent.mkdir(parents=True)
    runtime.write_bytes(b"previous good catalog")
    with pytest.raises(ValueError, match="checksum"):
        compile_catalog.compile_catalog()
    assert runtime.read_bytes() == b"previous good catalog"
    assert not list(runtime.parent.glob("catalog-*.tmp"))


def test_canonical_sources_cannot_reference_a_parent_file(tmp_path, monkeypatch):
    monkeypatch.setattr(compile_catalog, "ROOT", tmp_path)
    metadata = canonical(tmp_path)
    recipe = json.loads(metadata.read_text())
    recipe["guide_path"] = "../outside.md"
    metadata.write_text(json.dumps(recipe), encoding="utf-8")
    with pytest.raises(ValueError):
        compile_catalog.compile_catalog()

