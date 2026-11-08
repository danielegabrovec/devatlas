from __future__ import annotations
import json
import sqlite3
import uuid
import re
import unicodedata
import base64
from copy import deepcopy
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


def validate_setting(key, value):
    if not isinstance(key, str) or not key:
        raise ValueError("Nome dell'impostazione non valido.")
    valid = True
    if key == "theme":
        valid = isinstance(value, str) and value in {"system", "light", "dark"}
    elif key == "zoom":
        valid = type(value) is int and -2 <= value <= 5
    elif key == "reader_mode":
        valid = type(value) is int and value in (0, 1)
    elif key == "splitter":
        valid = isinstance(value, list) and len(value) == 3 and all(type(v) is int and 0 <= v <= 100000 for v in value)
    elif key == "geometry":
        valid = isinstance(value, str)
        if valid:
            try:
                base64.b64decode(value, validate=True)
            except (ValueError, UnicodeError):
                valid = False
    elif key == "saved_searches":
        from devatlas.saved_searches import validate_saved_searches
        validate_saved_searches(value)
    if not valid:
        raise ValueError(f"Valore non valido per l'impostazione {key}.")
    try:
        json.dumps({key: value}, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as error:
        raise ValueError(f"L'impostazione {key} non è serializzabile.") from error


def import_recipes(recipes, *, existing_ids=(), duplicate=True, force_new=False):
    """Prepare personal copies and remap internal recipe references in two passes."""
    prepared = deepcopy(list(recipes))
    from devatlas.bundles import _validate_recipe_list
    _validate_recipe_list(prepared)
    existing_ids = set(existing_ids)
    allocated = existing_ids | {recipe["id"] for recipe in prepared}
    mapping = {}
    for recipe in prepared:
        old = recipe["id"]
        if old in mapping:
            raise ValueError("Identificatori duplicati nel pacchetto personale.")
        new = old
        if force_new or not old.startswith("personal-") or duplicate and old in existing_ids:
            new = "personal-" + uuid.uuid4().hex
            attempts = 0
            while new in allocated and attempts < 8:
                new = "personal-" + uuid.uuid4().hex
                attempts += 1
            if new in allocated:
                raise ValueError("Non è stato possibile generare un ID personale univoco.")
        allocated.add(new)
        mapping[old] = new
        recipe["id"] = new
        recipe["personal"] = True
    for recipe in prepared:
        recipe["related"] = [mapping.get(rid, rid) for rid in recipe.get("related", [])]
        # Markdown recipe links are references too; source assets stay byte-identical.
        def remap_link(match):
            return match[1] + mapping.get(match[2], match[2])
        if "guide" in recipe:
            recipe["guide"] = re.sub(r"(recipe:(?://|/)?)([^\s)\]<>#?]+)", remap_link, recipe["guide"])
    return prepared, mapping


class PersonalStore:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version > 1:
                raise ValueError("Questo profilo è stato creato da una versione più recente di DevAtlas; i dati non sono stati modificati.")
            db.executescript("""
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS recipes(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS annotations(id TEXT PRIMARY KEY,favorite INTEGER NOT NULL DEFAULT 0,note TEXT NOT NULL DEFAULT '');
            CREATE TABLE IF NOT EXISTS collections(id TEXT PRIMARY KEY,name TEXT NOT NULL UNIQUE);
            CREATE TABLE IF NOT EXISTS collection_items(collection_id TEXT NOT NULL,recipe_id TEXT NOT NULL,PRIMARY KEY(collection_id,recipe_id));
            CREATE TABLE IF NOT EXISTS recent(id TEXT PRIMARY KEY,visited TEXT NOT NULL);
            PRAGMA user_version=1;
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            with db:
                yield db
        finally:
            db.close()

    def setting(self, key, default=None):
        with self.connect() as db:
            row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        if not row:
            return deepcopy(default)
        try:
            value = json.loads(row[0])
            validate_setting(key, value)
            return value
        except (ValueError, TypeError):
            # Keep the original row for recovery; a damaged preference must not block startup.
            return deepcopy(default)

    def set_setting(self, key, value):
        validate_setting(key, value)
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, json.dumps(value, ensure_ascii=False)))

    def list_recipes(self):
        with self.connect() as db:
            return [self._decode_record(rid, raw) for rid, raw in db.execute("SELECT id,payload FROM recipes ORDER BY rowid DESC")]

    @staticmethod
    def _decode_record(rid, raw):
        try:
            value = json.loads(raw)
            if not isinstance(value, dict) or value.get("id") != rid:
                raise ValueError("Il contenuto non corrisponde all'identificatore della scheda.")
            return value
        except (ValueError, TypeError):
            # Catalog.merged reports this placeholder visibly. The original row
            # remains untouched, and backup_data keeps its exact text separately.
            return {"id": rid, "record_error": "Contenuto personale non leggibile; originale conservato nel profilo."}

    def save_recipe(self, data):
        data = deepcopy(data)
        from devatlas.bundles import validate_recipe
        validate_recipe(data)
        if not data.get("id", "").startswith("personal-"):
            data["id"] = "personal-" + uuid.uuid4().hex
        data["personal"] = True
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO recipes VALUES (?,?)", (data["id"], json.dumps(data, ensure_ascii=False)))
        return data["id"]

    def import_recipes(self, recipes):
        """Import a recipe bundle atomically as new personal content."""
        prepared, mapping = import_recipes(recipes, force_new=True)
        with self.connect() as db:
            for recipe in prepared:
                db.execute("INSERT INTO recipes VALUES (?,?)",
                           (recipe["id"], json.dumps(recipe, ensure_ascii=False)))
        return mapping

    def delete_recipe(self, rid):
        if not rid.startswith("personal-"):
            raise ValueError("Il catalogo incluso è di sola lettura.")
        with self.connect() as db:
            db.execute("DELETE FROM recipes WHERE id=?", (rid,))
            db.execute("DELETE FROM annotations WHERE id=?", (rid,))
            db.execute("DELETE FROM collection_items WHERE recipe_id=?", (rid,))
            db.execute("DELETE FROM recent WHERE id=?", (rid,))

    def annotation(self, rid):
        with self.connect() as db:
            row = db.execute("SELECT favorite,note FROM annotations WHERE id=?", (rid,)).fetchone()
        return (bool(row[0]), row[1]) if row else (False, "")

    def annotate(self, rid, *, favorite=None, note=None):
        if not isinstance(rid, str) or not rid or note is not None and not isinstance(note, str):
            raise ValueError("Annotazione non valida.")
        if favorite is not None and (type(favorite) not in (bool, int) or favorite not in (0, 1)):
            raise ValueError("Il preferito deve essere booleano.")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT favorite,note FROM annotations WHERE id=?", (rid,)).fetchone()
            current_favorite, current_note = row if row else (False, "")
            db.execute("INSERT OR REPLACE INTO annotations VALUES (?,?,?)",
                       (rid, int(current_favorite if favorite is None else favorite), current_note if note is None else note))

    def favorites(self):
        with self.connect() as db:
            return [r[0] for r in db.execute("SELECT id FROM annotations WHERE favorite=1")]

    def visit(self, rid):
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO recent VALUES (?,?)", (rid, datetime.now(timezone.utc).isoformat()))
            db.execute("DELETE FROM recent WHERE id NOT IN (SELECT id FROM recent ORDER BY visited DESC LIMIT 200)")

    def history(self):
        with self.connect() as db:
            return [r[0] for r in db.execute("SELECT id FROM recent ORDER BY visited DESC")]

    def collections(self):
        with self.connect() as db:
            return list(db.execute("SELECT id,name FROM collections ORDER BY name COLLATE NOCASE"))

    def create_collection(self, name):
        name = self._collection_name(name)
        cid = uuid.uuid4().hex
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._check_collection_name(db, name)
            db.execute("INSERT INTO collections VALUES (?,?)", (cid, name))
        return cid

    @staticmethod
    def _collection_name(name):
        if not isinstance(name, str) or not name.strip() or any(ord(c) < 32 for c in name):
            raise ValueError("Inserisci un nome della raccolta su una sola riga.")
        return name.strip()

    @staticmethod
    def _check_collection_name(db, name, excluding=None):
        key = unicodedata.normalize("NFC", name).casefold()
        for cid, existing in db.execute("SELECT id,name FROM collections"):
            if cid != excluding and unicodedata.normalize("NFC", existing).casefold() == key:
                raise ValueError("Esiste già una raccolta con questo nome.")

    def rename_collection(self, cid, name):
        name = self._collection_name(name)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if not db.execute("SELECT 1 FROM collections WHERE id=?", (cid,)).fetchone():
                raise ValueError("La raccolta non esiste più.")
            self._check_collection_name(db, name, excluding=cid)
            db.execute("UPDATE collections SET name=? WHERE id=?", (name, cid))

    def delete_collection(self, cid):
        with self.connect() as db:
            if not db.execute("SELECT 1 FROM collections WHERE id=?", (cid,)).fetchone():
                raise ValueError("La raccolta non esiste più.")
            db.execute("DELETE FROM collection_items WHERE collection_id=?", (cid,))
            db.execute("DELETE FROM collections WHERE id=?", (cid,))

    def collection_ids(self, cid):
        with self.connect() as db:
            return [r[0] for r in db.execute("SELECT recipe_id FROM collection_items WHERE collection_id=?", (cid,))]

    def add_to_collection(self, cid, rid):
        with self.connect() as db:
            if not db.execute("SELECT 1 FROM collections WHERE id=?", (cid,)).fetchone():
                raise ValueError("La raccolta non esiste più.")
            db.execute("INSERT OR IGNORE INTO collection_items VALUES (?,?)", (cid, rid))

    def remove_from_collection(self, cid, rid):
        with self.connect() as db:
            db.execute("DELETE FROM collection_items WHERE collection_id=? AND recipe_id=?", (cid, rid))

    def backup_data(self):
        from devatlas.bundles import validate_recipe
        with self.connect() as db:
            db.execute("BEGIN")
            records = list(db.execute("SELECT id,payload FROM recipes ORDER BY rowid DESC"))
            data = {"recipes": [],
                    "annotations": [dict(zip(("id", "favorite", "note"), r)) for r in db.execute("SELECT * FROM annotations")],
                    "collections": [dict(zip(("id", "name"), r)) for r in db.execute("SELECT * FROM collections")],
                    "collection_items": [list(r) for r in db.execute("SELECT * FROM collection_items")],
                    "settings": {}}
            damaged = []
            for rid, raw in records:
                recipe = self._decode_record(rid, raw)
                try:
                    validate_recipe(recipe)
                    if not rid.startswith("personal-"):
                        raise ValueError("ID non personale.")
                    data["recipes"].append(recipe)
                except (ValueError, TypeError, KeyError):
                    damaged.append({"id": rid, "payload": raw})
            if damaged:
                data["recipes_recovery"] = damaged
            recovery = {}
            for key, raw in db.execute("SELECT * FROM settings"):
                try:
                    value = json.loads(raw)
                    validate_setting(key, value)
                    data["settings"][key] = value
                except (ValueError, TypeError):
                    recovery[key] = raw
            if recovery:
                data["settings_recovery"] = recovery
            return data

    def restore_data(self, data, *, duplicate=True):
        """Merge atomically; preserve existing personal content on ID conflicts."""
        from devatlas.bundles import validate_personal_data
        validate_personal_data(data)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing_ids = {row[0] for row in db.execute("SELECT id FROM recipes")}
            prepared, mapping = import_recipes(data.get("recipes", []), existing_ids=existing_ids,
                                              duplicate=duplicate)
            for recipe in prepared:
                db.execute("INSERT OR REPLACE INTO recipes VALUES (?,?)", (recipe["id"], json.dumps(recipe, ensure_ascii=False)))
            for item in data.get("annotations", []):
                rid = mapping.get(item["id"], item["id"])
                existing = db.execute("SELECT favorite,note FROM annotations WHERE id=?", (rid,)).fetchone()
                note = item.get("note", "")
                if existing and duplicate:
                    note = existing[1] + ("\n\n" + note if note and note != existing[1] else "")
                favorite = bool(item.get("favorite")) or bool(existing and existing[0])
                db.execute("INSERT OR REPLACE INTO annotations VALUES (?,?,?)", (rid, int(favorite), note))
            collection_mapping = {}
            for item in data.get("collections", []):
                current = db.execute("SELECT id FROM collections WHERE name=?", (item["name"],)).fetchone()
                cid = current[0] if current else uuid.uuid4().hex
                collection_mapping[item["id"]] = cid
                db.execute("INSERT OR IGNORE INTO collections VALUES (?,?)", (cid, item["name"]))
            for cid, rid in data.get("collection_items", []):
                db.execute("INSERT OR IGNORE INTO collection_items VALUES (?,?)", (collection_mapping.get(cid, cid), mapping.get(rid, rid)))
            for key, value in data.get("settings", {}).items():
                if key == "saved_searches" and isinstance(value, dict) and isinstance(value.get("items"), list):
                    value = deepcopy(value)
                    for search in value["items"]:
                        navigation = search.get("navigation") if isinstance(search, dict) else None
                        if isinstance(navigation, dict) and isinstance(navigation.get("collection"), str) and navigation["collection"] in collection_mapping:
                            navigation["collection"] = collection_mapping[navigation["collection"]]
                    row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
                    if row:
                        from devatlas.saved_searches import merge_saved_searches
                        try:
                            current = json.loads(row[0])
                            value = merge_saved_searches(current, value)
                        except (ValueError, TypeError) as error:
                            raise ValueError("Le ricerche salvate non possono essere unite: " + str(error)) from error
                    db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, json.dumps(value, ensure_ascii=False)))
                    continue
                db.execute("INSERT OR IGNORE INTO settings VALUES (?,?)", (key, json.dumps(value, ensure_ascii=False)))
        return len(data.get("recipes", []))

