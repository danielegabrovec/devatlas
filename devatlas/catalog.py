from __future__ import annotations
import hashlib
import json
from pathlib import Path
from devatlas.bundles import validate_recipe
from devatlas.models import Recipe
from devatlas.paths import PACKAGE


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Campo JSON duplicato nel catalogo: {key}")
        value[key] = item
    return value


def _reject_constant(value):
    raise ValueError(f"Valore JSON non valido nel catalogo: {value}")


class Catalog:
    def __init__(self, path: Path | None = None):
        self.path = path or PACKAGE / "data" / "catalog.json"
        with self.path.open("rb") as stream:
            raw = stream.read(100 * 1024 * 1024 + 1)
        if len(raw) > 100 * 1024 * 1024:
            raise ValueError("Il catalogo supera il limite di 100 MiB.")
        bundle = json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
        if not isinstance(bundle, dict) or bundle.get("format") != "RecipeBundle" or type(bundle.get("version")) is not int or bundle["version"] != 1:
            raise ValueError("Formato del catalogo non supportato.")
        self.fingerprint = hashlib.sha256(raw).hexdigest()
        stacks = bundle.get("stacks")
        records = bundle.get("recipes")
        if not isinstance(stacks, dict) or not stacks:
            raise ValueError("Il catalogo richiede un elenco di tecnologie.")
        self.stacks = {}
        for key, spec in stacks.items():
            if not isinstance(key, str) or not key.strip() or not isinstance(spec, dict) or not isinstance(spec.get("label"), str) or not spec["label"].strip():
                raise ValueError("Tecnologia non valida nel catalogo.")
            if not isinstance(spec.get("group", "Personali"), str):
                raise ValueError("Gruppo della tecnologia non valido.")
            self.stacks[key] = {**spec, "group": spec.get("group", "Personali")}
        if not isinstance(records, list) or len(records) > 10000:
            raise ValueError("Elenco delle schede non valido (massimo 10.000).")
        self.recipes = {}
        for record in records:
            validate_recipe(record)
            if record["stack"] not in self.stacks:
                raise ValueError(f"Tecnologia sconosciuta nella scheda: {record['id']}")
            if record["id"] in self.recipes or record["id"].startswith("personal-"):
                raise ValueError("Il catalogo contiene identificatori duplicati o riservati alle schede personali.")
            for asset in record["assets"]:
                expected = asset.get("sha256")
                if expected and hashlib.sha256(asset["content"].encode("utf-8")).hexdigest() != expected:
                    raise ValueError(f"Il codice della scheda {record['id']} non corrisponde al checksum dichiarato.")
            self.recipes[record["id"]] = Recipe(record)
        self.personal_errors = []

    def merged(self, personal: list[dict]):
        result = dict(self.recipes)
        self.personal_errors = []
        for item in personal:
            try:
                validate_recipe(item)
                if not item["id"].startswith("personal-") or item["stack"] not in self.stacks or item["id"] in result:
                    raise ValueError("Identificatore o tecnologia personale non valido.")
                data = dict(item)
                data["personal"] = True
                result[data["id"]] = Recipe(data)
            except (ValueError, TypeError, KeyError) as error:
                rid = item.get("id", "senza ID") if isinstance(item, dict) else "senza ID"
                self.personal_errors.append({"id": rid, "error": str(error)})
        return result

