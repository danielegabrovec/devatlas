from __future__ import annotations
import re
import unicodedata
import math
from copy import deepcopy
from pathlib import PurePosixPath, PureWindowsPath

PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z_]\w*)(?:\|(json|powershell|bash))?\s*\}\}")
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
RESERVED.update(prefix + suffix for prefix in ("COM", "LPT") for suffix in "¹²³")
PARAMETER_TYPES = {"identifier", "namespace", "port", "path", "string"}


def safe_relative(path: str) -> str:
    if not isinstance(path, str):
        raise ValueError("Il percorso deve essere testo.")
    try:
        path.encode("utf-8")
    except UnicodeError as error:
        raise ValueError("Il percorso contiene caratteri Unicode non validi.") from error
    win = PureWindowsPath(path)
    normalized = path.replace("\\", "/")
    posix = PurePosixPath(normalized)
    if not path or win.is_absolute() or win.drive or posix.is_absolute() or any(p in ("..", ".", "") for p in normalized.split("/")):
        raise ValueError(f"Percorso non valido per l'esportazione: {path}")
    for component in posix.parts:
        if any(c in component for c in '<>:"|?*\x00') or any(ord(c) < 32 for c in component) or component.endswith((" ", ".")):
            raise ValueError(f"Nome di file non valido: {component}")
        if component.split(".")[0].rstrip().upper() in RESERVED:
            raise ValueError(f"Nome riservato da Windows: {component}")
        if len(component.encode("utf-16-le")) // 2 > 255:
            raise ValueError("Un componente del percorso supera 255 caratteri UTF-16.")
    return str(posix)


def check_file_paths(paths):
    """Reject portable filename, directory and Unicode-normalization collisions."""
    files, directories = set(), set()
    for path in paths:
        key = unicodedata.normalize("NFC", safe_relative(path)).casefold()
        if key in files or key in directories:
            raise ValueError(f"File duplicato o in conflitto con una cartella: {path}")
        parts = key.split("/")
        parents = {"/".join(parts[:index]) for index in range(1, len(parts))}
        if parents & files:
            raise ValueError(f"Una cartella coincide con un altro file: {path}")
        files.add(key)
        directories.update(parents)


def parameter_definitions(data):
    definitions = data.get("parameters", [])
    if not isinstance(definitions, list) or len(definitions) > 200:
        raise ValueError("L'elenco dei parametri non è valido (massimo 200).")
    names = set()
    for parameter in definitions:
        if not isinstance(parameter, dict):
            raise ValueError("Ogni parametro deve essere un oggetto.")
        name = parameter.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_]\w*", name) or name in names:
            raise ValueError("I nomi dei parametri devono essere identificatori univoci.")
        names.add(name)
        if parameter.get("type", "string") not in PARAMETER_TYPES:
            raise ValueError(f"Tipo del parametro {name} non supportato.")
        if not isinstance(parameter.get("label", name), str) or not isinstance(parameter.get("required", True), bool):
            raise ValueError(f"Etichetta o obbligatorietà del parametro {name} non valida.")
        default = parameter.get("default", "")
        if not isinstance(default, (str, int, float)) or isinstance(default, bool):
            raise ValueError(f"Valore iniziale del parametro {name} non valido.")
        if isinstance(default, float) and not math.isfinite(default):
            raise ValueError(f"Valore iniziale del parametro {name} non finito.")
    return definitions


def validate_parameter(parameter: dict, value: str) -> str:
    kind = parameter.get("type", "string")
    name = parameter.get("label", parameter["name"])
    if not value and parameter.get("required", True):
        raise ValueError(f"{name}: inserisci un valore.")
    if len(value) > 1024 or any(ord(c) < 32 for c in value):
        raise ValueError(f"{name}: il valore contiene caratteri di controllo o è troppo lungo.")
    if not value and not parameter.get("required", True):
        return ""
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise ValueError(f"{name}: caratteri Unicode non validi.") from error
    if kind == "identifier" and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError(f"{name}: usa lettere ASCII, cifre e underscore; inizia con una lettera.")
    if kind == "namespace" and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*", value):
        raise ValueError(f"{name}: inserisci un namespace come Azienda.Progetto.")
    if kind == "port" and (not re.fullmatch(r"[0-9]+", value) or not 1 <= int(value) <= 65535):
        raise ValueError(f"{name}: la porta deve essere fra 1 e 65535.")
    if kind == "path":
        if not value or any(c in value for c in '\x00<>"|?*') or ".." in PureWindowsPath(value).parts:
            raise ValueError(f"{name}: percorso non valido.")
    if kind == "identifier" and value.upper() in RESERVED:
        raise ValueError(f"{name}: il nome è riservato da Windows.")
    return value


def render_recipe(data: dict, values: dict[str, str] | None = None) -> dict:
    import json
    import shlex
    if not isinstance(data, dict):
        raise ValueError("La scheda deve essere un oggetto.")
    if values is not None and not isinstance(values, dict):
        raise ValueError("I valori dei parametri devono essere un oggetto.")
    definitions = parameter_definitions(data)
    rendered = deepcopy(data)
    supplied = values or {}
    if set(supplied) - {p["name"] for p in definitions}:
        raise ValueError("Sono stati forniti parametri non dichiarati dalla scheda.")
    if any(not isinstance(value, (str, int, float)) or isinstance(value, bool) or isinstance(value, float) and not math.isfinite(value) for value in supplied.values()):
        raise ValueError("I parametri richiedono testi o numeri finiti.")
    parameters = {p["name"]: validate_parameter(p, str(supplied.get(p["name"], p.get("default", "")))) for p in definitions}

    def substitute(text):
        if not isinstance(text, str):
            raise ValueError("Il contenuto da personalizzare deve essere testo.")
        def replace(match):
            name, quoting = match.group(1), match.group(2)
            if name not in parameters:
                # Django/Jinja/Handlebars also use {{name}}. Only declared DevAtlas
                # parameters belong to our renderer; framework templates stay literal.
                return match.group(0)
            value = parameters[name]
            if quoting == "json":
                return json.dumps(value, ensure_ascii=False)
            if quoting == "powershell":
                return "'" + value.replace("'", "''") + "'"
            if quoting == "bash":
                return shlex.quote(value)
            return value
        return PLACEHOLDER.sub(replace, text)

    assets = rendered.get("assets", [])
    if not isinstance(assets, list) or any(not isinstance(asset, dict) for asset in assets):
        raise ValueError("I blocchi della scheda devono essere oggetti.")
    for asset in assets:
        asset["content"] = substitute(asset["content"])
        if asset.get("role") != "command":
            asset["path"] = safe_relative(substitute(asset["path"]))
        else:
            cwd = asset.get("cwd", ".")
            if not isinstance(cwd, str):
                raise ValueError("La directory dei comandi deve essere testo.")
            asset["cwd"] = substitute(cwd)
    for name in ("guide", "expected", "summary", "prerequisites"):
        rendered[name] = substitute(rendered.get(name, ""))
    check_file_paths(asset["path"] for asset in assets if asset.get("role") != "command")
    return rendered
