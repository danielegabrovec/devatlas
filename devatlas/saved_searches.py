"""Modello delle ricerche salvate: validazione condivisa senza dipendenze Qt."""
from __future__ import annotations
import json
import uuid
import unicodedata

SAVED_SEARCH_KEY = "saved_searches"
SAVED_SEARCH_FILTERS = {"section", "difficulty", "os", "shell", "ide", "status", "scope", "sort"}
SAVED_SEARCH_NAVIGATION = {"stack", "group", "section", "special", "collection", "guided", "only_projects"}
MAX_SAVED_SEARCHES = 100


def validate_saved_searches(value):
    """Validate before writing; unsupported data stays intact in the profile."""
    from copy import deepcopy
    if not isinstance(value, dict) or set(value) != {"version", "items"} or type(value["version"]) is not int or value["version"] != 1:
        raise ValueError("Formato delle ricerche salvate non supportato.")
    items = deepcopy(value["items"])
    if not isinstance(items, list) or len(items) > MAX_SAVED_SEARCHES:
        raise ValueError(f"Puoi conservare al massimo {MAX_SAVED_SEARCHES} ricerche salvate.")
    ids, names = set(), set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {"id", "name", "text", "filters", "navigation"}:
            raise ValueError("Ricerca salvata incompleta o non valida.")
        rid, name, text = item["id"], item["name"], item["text"]
        if not isinstance(rid, str) or len(rid) != 32 or any(c not in "0123456789abcdef" for c in rid) or rid in ids:
            raise ValueError("Identificatore della ricerca non valido o duplicato.")
        if not isinstance(name, str) or any(ord(c) < 32 for c in name):
            raise ValueError("Usa un nome da 1 a 80 caratteri su una sola riga.")
        name = unicodedata.normalize("NFC", name.strip())
        if not name or len(name) > 80:
            raise ValueError("Usa un nome da 1 a 80 caratteri su una sola riga.")
        item["name"] = name
        if name.casefold() in names:
            raise ValueError("Esiste già una ricerca salvata con questo nome.")
        if not isinstance(text, str) or len(text) > 2000 or any(ord(c) < 32 for c in text):
            raise ValueError("La ricerca deve essere su una sola riga, con al massimo 2.000 caratteri.")
        filters, navigation = item["filters"], item["navigation"]
        if not isinstance(filters, dict) or not set(filters) <= SAVED_SEARCH_FILTERS or any(not isinstance(v, str) or len(v) > 256 or any(ord(c) < 32 for c in v) for v in filters.values()):
            raise ValueError("Filtri della ricerca salvata non validi.")
        if filters.get("scope", "") not in ("", "code", "title"):
            raise ValueError("Ambito della ricerca non valido.")
        if filters.get("sort", "relevance") not in ("", "relevance", "title", "difficulty", "recent"):
            raise ValueError("Ordinamento della ricerca salvata non valido.")
        if not isinstance(navigation, dict) or not set(navigation) <= SAVED_SEARCH_NAVIGATION:
            raise ValueError("Navigazione della ricerca salvata non valida.")
        for key, entry in navigation.items():
            if key in ("guided", "only_projects"):
                if type(entry) is not bool:
                    raise ValueError("Le opzioni del percorso e dei progetti devono essere booleane.")
            elif not isinstance(entry, str) or len(entry) > 256 or any(ord(c) < 32 for c in entry):
                raise ValueError("Riferimento della ricerca salvata non valido.")
        if navigation.get("special", "") not in ("", "favorites", "history", "personal"):
            raise ValueError("Biblioteca della ricerca salvata non riconosciuta.")
        ids.add(rid)
        names.add(name.casefold())
    try:
        raw = json.dumps({"version": 1, "items": items}, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, UnicodeError) as error:
        raise ValueError("Le ricerche salvate contengono testo non valido.") from error
    if len(raw) > 512 * 1024:
        raise ValueError("L’archivio delle ricerche supera 512 KiB. Riduci il testo prima di salvare.")
    return deepcopy(items)


def merge_saved_searches(current, incoming):
    """Preserve both sets of user content; never silently exceed UI limits."""
    existing = validate_saved_searches(current)
    additions = validate_saved_searches(incoming)
    ids = {item["id"] for item in existing}
    names = {item["name"].casefold() for item in existing}
    for item in additions:
        original = next((entry for entry in existing if entry["id"] == item["id"]), None)
        if original == item:
            continue
        if len(existing) >= MAX_SAVED_SEARCHES:
            raise ValueError("Il ripristino supera 100 ricerche salvate: libera spazio prima di importare il backup. Nessun contenuto è stato sostituito.")
        if item["id"] in ids:
            for _ in range(8):
                candidate = uuid.uuid4().hex
                if candidate not in ids:
                    item["id"] = candidate
                    break
            else:
                raise ValueError("Impossibile assegnare un ID univoco alla ricerca importata.")
        base = item["name"]
        number = 1
        while item["name"].casefold() in names:
            suffix = " (importata)" if number == 1 else f" (importata {number})"
            item["name"] = base[:80-len(suffix)].rstrip() + suffix
            number += 1
        existing.append(item)
        ids.add(item["id"])
        names.add(item["name"].casefold())
    result = {"version": 1, "items": existing}
    validate_saved_searches(result)
    return result
