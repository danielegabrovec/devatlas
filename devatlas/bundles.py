from __future__ import annotations
import json
import os
import tempfile
import zipfile
import shutil
from pathlib import Path
from devatlas.templating import render_recipe, safe_relative, check_file_paths

MAX_BUNDLE_BYTES = 100 * 1024 * 1024


def readme(recipe):
    text = f"# {recipe['title']}\n\n{recipe.get('summary', '')}\n\n"
    text += "## Prerequisiti\n\n" + recipe.get("prerequisites", "") + "\n\n"
    text += "Versioni di riferimento: " + recipe.get("versions", "") + "\n\n"
    text += "## Procedura\n\n" + recipe.get("guide", "") + "\n\n"
    for asset in recipe.get("assets", []):
        if asset.get("role") == "command":
            text += f"### {asset.get('shell', 'Terminale')} · {asset.get('os', 'Tutti')}\n\nDirectory: `{asset.get('cwd', '.')}`\n\n```{asset.get('language', '')}\n{asset['content']}```\n\n"
        elif asset.get("role") == "snippet":
            text += f"### Frammento: {asset['path']}\n\nVedi la guida per il punto di inserimento.\n\n"
    text += "## Risultato atteso\n\n" + recipe.get("expected", "") + "\n\n"
    if recipe.get("errors"):
        text += "## Errori frequenti\n\n" + "\n".join("- " + e for e in recipe["errors"]) + "\n\n"
    status = recipe.get("verification", {})
    text += f"## Verifica\n\n{status.get('status', 'documentato')}: {status.get('details', '')}\n\n"
    text += "## Fonti\n\n" + "\n".join("- " + url for url in recipe.get("sources", [])) + "\n"
    text += "\nIl catalogo è offline. Toolchain e dipendenze dei progetti devono essere predisposte separatamente.\n"
    return text


def export_files(data: dict, parameters=None):
    recipe = render_recipe(data, parameters)
    files = {}
    for asset in recipe.get("assets", []):
        if asset.get("role") == "command":
            continue
        path = safe_relative(asset["path"])
        try:
            asset["content"].encode("utf-8")
        except UnicodeError as error:
            raise ValueError(f"Il file {path} contiene Unicode non valido.") from error
        files[path] = asset["content"]
    for readme_name in ("README.md", "README-DEVATLAS.md"):
        try:
            check_file_paths([*files, readme_name])
        except ValueError:
            continue
        files[readme_name] = readme(recipe)
        break
    else:
        raise ValueError("Il progetto contiene già README.md e README-DEVATLAS.md o cartelle con questi nomi.")
    return files


def _publish_file(temporary, destination):
    """Publish on the same filesystem without ever replacing an existing file."""
    if os.name == "nt":
        os.rename(temporary, destination)  # Windows rename fails if target exists.
    else:
        os.link(temporary, destination)  # Atomic exclusive creation on POSIX.


def _write_archive(destination, write):
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Il file esiste già. Scegli un nuovo nome.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".devatlas-", suffix=".tmp", delete=False) as output:
        temporary = Path(output.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            write(archive)
        _publish_file(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def export_project(data, destination: Path, *, parameters=None, zipped=False):
    files = export_files(data, parameters)
    destination = Path(destination)
    if zipped:
        def write(archive):
            for path, content in files.items():
                archive.writestr(path, content.encode("utf-8"))
        _write_archive(destination, write)
    else:
        if destination.is_symlink() or getattr(destination, "is_junction", lambda: False)():
            raise ValueError("Scegli una cartella reale, non un collegamento o una junction.")
        existed = destination.exists()
        if existed and (not destination.is_dir() or any(destination.iterdir())):
            raise FileExistsError("La cartella contiene già file. Scegli una cartella vuota.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(dir=destination.parent, prefix=".devatlas-export-"))
        parent = destination.parent.resolve()
        try:
            for path, content in files.items():
                target = stage / path
                if not target.resolve().is_relative_to(stage.resolve()):
                    raise ValueError("Il percorso esce dalla cartella di destinazione.")
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("x", encoding="utf-8", newline="") as stream:
                    stream.write(content)
            if existed:
                destination.rmdir()  # Fails safely if it acquired any user files.
            try:
                os.rename(stage, destination)
            except OSError:
                if existed and not destination.exists():
                    destination.mkdir()
                raise
        finally:
            if stage.exists():
                # Only our sibling staging directory may be recursively removed.
                if stage.resolve().parent != parent or not stage.name.startswith(".devatlas-export-") or stage.is_symlink():
                    raise ValueError("Percorso temporaneo inatteso: pulizia interrotta.")
                shutil.rmtree(stage)
    return len(files)


def save_bundle(path: Path, recipes: list[dict], personal=None):
    payload = {"format": "RecipeBundle", "version": 1, "recipes": recipes}
    if personal is not None:
        payload["personal"] = personal
    raw = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8")
    if len(raw) > MAX_BUNDLE_BYTES:
        raise ValueError("Pacchetto troppo grande (limite 100 MiB).")
    _write_archive(Path(path), lambda archive: archive.writestr("bundle.json", raw))


def load_bundle(path: Path):
    try:
        if Path(path).stat().st_size > MAX_BUNDLE_BYTES + 1024 * 1024:
            raise ValueError("Archivio troppo grande (limite circa 101 MiB).")
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) != 1 or infos[0].filename != "bundle.json" or infos[0].is_dir():
                raise ValueError("Il pacchetto deve contenere soltanto bundle.json.")
            if infos[0].flag_bits & 1:
                raise ValueError("I pacchetti cifrati non sono supportati.")
            if infos[0].file_size > MAX_BUNDLE_BYTES:
                raise ValueError("Pacchetto troppo grande (limite 100 MiB).")
            with archive.open(infos[0]) as stream:
                raw = stream.read(MAX_BUNDLE_BYTES + 1)
            if len(raw) > MAX_BUNDLE_BYTES:
                raise ValueError("Pacchetto troppo grande.")
        def unique_pairs(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"Chiave JSON duplicata: {key}")
                result[key] = value
            return result
        def no_constant(value):
            raise ValueError(f"Valore numerico JSON non valido: {value}")
        payload = json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=no_constant)
    except (zipfile.BadZipFile, UnicodeError, json.JSONDecodeError, RecursionError, RuntimeError, NotImplementedError) as error:
        raise ValueError("Il pacchetto ZIP o il documento JSON non è valido.") from error
    if not isinstance(payload, dict) or payload.get("format") != "RecipeBundle" or type(payload.get("version")) is not int or payload["version"] != 1:
        raise ValueError("Versione del pacchetto non supportata.")
    recipes = payload.get("recipes", [])
    if not isinstance(recipes, list) or len(recipes) > 10000:
        raise ValueError("Elenco delle schede non valido.")
    _validate_recipe_list(recipes)
    personal = payload.get("personal")
    if personal is not None:
        validate_personal_data(personal)
        if {recipe["id"]: recipe for recipe in recipes} != {recipe["id"]: recipe for recipe in personal.get("recipes", [])}:
            raise ValueError("Le schede del backup non corrispondono al contenuto personale.")
    return payload


def validate_recipe(recipe):
    if not isinstance(recipe, dict) or not all(isinstance(recipe.get(k), str) and recipe[k].strip() for k in ("id", "title", "stack", "summary")):
        raise ValueError("Ogni scheda richiede ID, titolo, tecnologia e obiettivo.")
    if not isinstance(recipe.get("assets"), list) or not recipe["assets"]:
        raise ValueError("Ogni scheda richiede almeno un blocco di codice o comando.")
    for key in ("os", "ide", "tags", "related", "errors", "sources"):
        if not isinstance(recipe.get(key, []), list) or not all(isinstance(v, str) for v in recipe.get(key, [])):
            raise ValueError(f"Il campo {key} deve essere una lista di testi.")
    for key in ("guide", "expected", "prerequisites", "versions", "section", "difficulty", "group", "reviewed"):
        if not isinstance(recipe.get(key, ""), str):
            raise ValueError(f"Il campo {key} deve essere testo.")
    if not isinstance(recipe.get("verification", {}), dict):
        raise ValueError("Stato di verifica non valido.")
    rid = safe_relative(recipe["id"])
    if "/" in rid:
        raise ValueError("L'ID della scheda deve essere un nome semplice, senza cartelle.")
    for field in ("project", "personal"):
        if field in recipe and not isinstance(recipe[field], bool):
            raise ValueError(f"Il campo {field} deve essere booleano.")
    for field in ("status", "details", "date"):
        if field in recipe.get("verification", {}) and not isinstance(recipe["verification"][field], str):
            raise ValueError("I dettagli di verifica devono essere testo.")
    variants = recipe.get("variants", [])
    if not isinstance(variants, list) or any(not isinstance(v, dict) for v in variants):
        raise ValueError("Le varianti devono essere una lista di oggetti.")
    asset_ids = set()
    for asset in recipe["assets"]:
        if not isinstance(asset, dict) or not isinstance(asset.get("content"), str) or not isinstance(asset.get("path"), str) or not asset["path"].strip():
            raise ValueError("Blocco di codice non valido.")
        if asset.get("role") not in ("file", "snippet", "command"):
            raise ValueError("Ruolo del blocco non valido.")
        if "id" in asset:
            if not isinstance(asset["id"], str) or not asset["id"] or asset["id"] in asset_ids:
                raise ValueError("Gli ID dei blocchi devono essere testi univoci.")
            asset_ids.add(asset["id"])
        for field in ("language", "shell", "os", "cwd"):
            if field in asset and not isinstance(asset[field], str):
                raise ValueError(f"Il campo {field} del blocco deve essere testo.")
        if asset.get("role") == "command" and (not asset.get("cwd", ".").strip() or any(ord(c) < 32 for c in asset.get("cwd", "."))):
            raise ValueError("La directory dei comandi deve essere un percorso su una sola riga.")
    try:
        json.dumps(recipe, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as error:
        raise ValueError("La scheda contiene dati non serializzabili o Unicode non valido.") from error
    render_recipe(recipe)


def _validate_recipe_list(recipes, *, personal=False):
    if not isinstance(recipes, list) or len(recipes) > 10000:
        raise ValueError("Elenco delle schede non valido (massimo 10000).")
    ids = set()
    for recipe in recipes:
        validate_recipe(recipe)
        if recipe["id"] in ids:
            raise ValueError("Identificatori duplicati nel pacchetto.")
        ids.add(recipe["id"])
        if personal and not recipe["id"].startswith("personal-"):
            raise ValueError("Il backup contiene ID personali non validi.")


def validate_personal_data(data):
    """Validate a v1 personal backup before any database mutation."""
    from devatlas.personal import validate_setting
    if not isinstance(data, dict):
        raise ValueError("Backup personale non valido.")
    _validate_recipe_list(data.get("recipes", []), personal=True)
    for field in ("annotations", "collections", "collection_items"):
        if not isinstance(data.get(field, []), list) or len(data.get(field, [])) > 100000:
            raise ValueError(f"Elenco {field} del backup non valido.")
    annotations = set()
    for item in data.get("annotations", []):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"] or not isinstance(item.get("note", ""), str) or type(item.get("favorite", False)) not in (bool, int) or item.get("favorite", False) not in (0, 1):
            raise ValueError("Annotazione non valida.")
        if item["id"] in annotations:
            raise ValueError("Annotazioni duplicate nel backup.")
        annotations.add(item["id"])
    collections, names = set(), set()
    for item in data.get("collections", []):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"] or not isinstance(item.get("name"), str) or not item["name"].strip():
            raise ValueError("Raccolta non valida.")
        if item["id"] in collections or item["name"] in names:
            raise ValueError("Raccolte duplicate nel backup.")
        collections.add(item["id"]); names.add(item["name"])
    for item in data.get("collection_items", []):
        if not isinstance(item, (list, tuple)) or len(item) != 2 or not all(isinstance(s, str) and s for s in item) or item[0] not in collections:
            raise ValueError("Riferimento alla raccolta non valido.")
    settings = data.get("settings", {})
    if not isinstance(settings, dict):
        raise ValueError("Le impostazioni del backup devono essere un oggetto.")
    for key, value in settings.items():
        validate_setting(key, value)
    recovered = data.get("recipes_recovery", [])
    if not isinstance(recovered, list) or len(recovered) > 10000:
        raise ValueError("Elenco delle schede da recuperare non valido.")
    recovery_ids = set()
    for item in recovered:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"] or not isinstance(item.get("payload"), str) or item["id"] in recovery_ids:
            raise ValueError("Scheda da recuperare non valida o duplicata.")
        recovery_ids.add(item["id"])
    try:
        json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as error:
        raise ValueError("Il backup contiene dati non serializzabili o Unicode non valido.") from error

