from copy import deepcopy
import json
from pathlib import Path
import zipfile
import pytest
from devatlas.bundles import export_project, export_files, load_bundle, save_bundle
from devatlas.models import Recipe, SearchQuery
from devatlas.personal import PersonalStore
from devatlas.search import SearchIndex
from devatlas.templating import render_recipe, safe_relative


def sample(rid="python-json", stack="python", title="Leggere un file JSON"):
    return {"id": rid, "stack": stack, "title": title, "summary": "Aprire un file JSON e gestire gli errori",
        "section": "Codice applicativo", "difficulty": "Base", "os": ["Windows", "Linux"], "ide": ["VS Code"],
        "guide": "Leggi un file con json.load.", "tags": ["read", "open", "json"], "group": "Linguaggi",
        "assets": [{"id": "main", "path": "src/{{project_name}}.py", "role": "file", "language": "python", "content": "print('caffè ☕')\n"},
                   {"id": "command", "path": "Comandi", "role": "command", "shell": "PowerShell", "os": "Windows", "cwd": ".", "language": "powershell", "content": "python src/{{project_name}}.py\n"}],
        "parameters": [{"name": "project_name", "label": "Nome progetto", "type": "identifier", "default": "esempio", "required": True}],
        "verification": {"status": "documentato"}, "sources": [], "expected": "caffè ☕", "prerequisites": "Python 3.13"}


@pytest.mark.parametrize("path", ["../fuori.txt", "/tmp/fuori", "C:\\temp\\x.txt", "\\\\server\\share\\x", "a/../../b", "CON.txt", "a/aux", "a/b:stream", "a./b", "foo\x00bar", "a\\..\\x"])
def test_paths_cannot_escape_or_use_windows_reserved_names(path):
    with pytest.raises(ValueError):
        safe_relative(path)


def test_render_export_and_copy_source_are_identical(tmp_path):
    data = sample()
    rendered = render_recipe(data, {"project_name": "Esempio"})
    assert rendered["assets"][0]["path"] == "src/Esempio.py"
    assert data["assets"][0]["path"] == "src/{{project_name}}.py"
    target = tmp_path / "cartella con spazi è"
    export_project(data, target, parameters={"project_name": "Esempio"})
    assert (target / "src/Esempio.py").read_bytes() == rendered["assets"][0]["content"].encode()
    assert "PowerShell" in (target / "README.md").read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        export_project(data, target)
    zipped = tmp_path / "esempio.zip"
    export_project(data, zipped, parameters={"project_name": "Esempio"}, zipped=True)
    with zipfile.ZipFile(zipped) as archive:
        assert archive.read("src/Esempio.py") == rendered["assets"][0]["content"].encode()
    with pytest.raises(FileExistsError):
        export_project(data, zipped, zipped=True)


@pytest.mark.parametrize("value", ["bad-name", "1start", "$(whoami)", "CON", "../fuori", "x\ny"])
def test_identifier_parameter_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        render_recipe(sample(), {"project_name": value})


def test_context_specific_quoting():
    data = sample()
    data["parameters"] = [{"name": "value", "type": "string", "default": "L'unità $(echo secret)"}]
    data["assets"] = [{"id": "x", "path": "x.txt", "role": "file", "content": "{{value|json}}\n{{value|powershell}}\n{{value|bash}}"}]
    text = render_recipe(data)["assets"][0]["content"]
    assert json.loads(text.splitlines()[0]) == data["parameters"][0]["default"]
    assert "'L''unità $(echo secret)'" in text


def test_framework_template_variables_are_preserved():
    data = sample()
    data["assets"][0]["content"] = "{{ host }} {{project_name}} {{ request.user }}"
    assert render_recipe(data)["assets"][0]["content"] == "{{ host }} esempio {{ request.user }}"


def test_bundle_roundtrip_and_untrusted_zip_rejected(tmp_path):
    path = tmp_path / "raccolta.zip"
    save_bundle(path, [sample()])
    assert load_bundle(path)["recipes"][0] == sample()
    malicious = tmp_path / "malicious.zip"
    with zipfile.ZipFile(malicious, "w") as archive:
        archive.writestr("../x", "no")
    with pytest.raises(ValueError):
        load_bundle(malicious)
    data = sample()
    data["assets"][0]["path"] = "../bad.py"
    bad = tmp_path / "bad.zip"
    save_bundle(bad, [data])
    with pytest.raises(ValueError):
        load_bundle(bad)
    assert not (tmp_path.parent / "bad.py").exists()


def test_case_insensitive_export_collision_rejected():
    data = sample()
    data["assets"].append({"id": "other", "path": "SRC/esempio.py", "role": "file", "content": "different"})
    with pytest.raises(ValueError):
        export_files(data)


def test_personal_backup_conflicts_and_annotations_preserved(tmp_path):
    store = PersonalStore(tmp_path / "personal.sqlite")
    rid = store.save_recipe(sample())
    store.annotate(rid, favorite=True, note="mia nota")
    cid = store.create_collection("Preferite per il corso")
    store.add_to_collection(cid, rid)
    store.visit(rid)
    store.set_setting("theme", "dark")
    backup = store.backup_data()
    assert len(backup["recipes"]) == 1
    store.restore_data(backup, duplicate=True)
    assert len(store.list_recipes()) == 2
    assert store.annotation(rid) == (True, "mia nota")
    assert len(store.collections()) == 1
    assert len(store.collection_ids(cid)) == 2
    assert store.history() == [rid]
    reopened = PersonalStore(store.path)
    assert reopened.setting("theme") == "dark"
    assert len(reopened.list_recipes()) == 2


def test_search_symbolic_languages_filters_and_ordinary_punctuation(tmp_path):
    items = [sample(), sample("cpp-build", "cpp", "Compilare un progetto C++ con CMake"),
             sample("csharp-build", "csharp", "Compilare un progetto C#"), sample("c-build", "c", "Compilare un progetto C")]
    for item in items[1:]:
        item["summary"] = item["title"]
        item["guide"] = "Build compile compilazione"
        item["tags"] = ["build", "compile"]
    index = SearchIndex(tmp_path / "search.sqlite")
    index.rebuild({r["id"]: Recipe(r) for r in items}, "test-v1")
    assert index.search(SearchQuery("c++ compilare")).ids == ["cpp-build"]
    assert index.search(SearchQuery("c# build")).ids == ["csharp-build"]
    assert index.search(SearchQuery("c compilare")).ids == ["c-build"]
    assert index.search(SearchQuery("python leggere json", stack="python")).ids == ["python-json"]
    assert not index.search(SearchQuery("json", os="macOS")).ids
    assert not index.search(SearchQuery("json", ids=[])).ids
    for text in ['"', '" OR * NOT )', "C++ std::vector<T>", "c# [x]", "àéìòù", "😀", "'; DROP TABLE search; --"]:
        index.search(SearchQuery(text))
    assert index.search(SearchQuery("json")).ids == ["python-json"]
    suggestion = index.search(SearchQuery("pythno json"))
    assert suggestion.suggestions
    assert suggestion.ids == ["python-json"]


def test_index_rebuild_preserves_personal_store_and_stable_ids(tmp_path):
    store = PersonalStore(tmp_path / "personal.sqlite")
    store.annotate("python-json", favorite=True, note="resta")
    index = SearchIndex(tmp_path / "search.sqlite")
    recipes = {"python-json": Recipe(sample())}
    index.rebuild(recipes, "one")
    recipes["python-json"].data["title"] = "Importare dati JSON"
    index.rebuild(recipes, "two")
    assert store.annotation("python-json") == (True, "resta")
    assert index.search(SearchQuery("importare")).ids == ["python-json"]

