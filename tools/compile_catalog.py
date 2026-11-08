"""Compile canonical authoring sources into the app's offline RecipeBundle."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.catalog_support import STACKS, SECTION_ALIASES, PROJECT_TARGETS, EXPECTED_RECIPES, EXPECTED_PROJECTS
from devatlas import __version__
from devatlas.bundles import validate_recipe
from devatlas.catalog import Catalog
from devatlas.templating import safe_relative


def read_source(directory, relative):
    path = directory / safe_relative(relative)
    if not path.resolve().is_relative_to(directory.resolve()) or not path.is_file():
        raise ValueError(f"Sorgente fuori dalla scheda o mancante: {relative}")
    return path.read_text(encoding="utf-8")


def compile_catalog():
    recipes = []
    for path in sorted((ROOT / "catalog").glob("*/*/recipe.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("section") in SECTION_ALIASES:
            data["section"] = SECTION_ALIASES[data["section"]]
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        data["guide"] = read_source(path.parent, data.pop("guide_path"))
        for asset in data["assets"]:
            asset["content"] = read_source(path.parent, asset.pop("source"))
        validate_recipe(data)
        recipes.append(data)
    # Content navigation is materialized into the editable metadata, not an
    # invisible UI-only relation: author-provided links always take precedence.
    import re
    stop = {"un", "una", "con", "per", "del", "della", "da", "di", "in", "il", "la", "e", "creare", "usare"}
    def terms(recipe):
        return set(re.findall(r"\w+", (recipe["title"] + " " + " ".join(recipe["tags"])).lower())) - stop
    stack_recipes = {}
    known_ids = {r["id"] for r in recipes}
    for recipe in recipes:
        stack_recipes.setdefault(recipe["stack"], []).append(recipe)
    for recipe in recipes:
        old_related = recipe.get("related", [])
        recipe["related"] = [rid for rid in old_related if rid in known_ids and rid != recipe["id"]]
        if recipe["related"] != old_related:
            metadata = ROOT / "catalog" / recipe["stack"] / recipe["id"] / "recipe.json"
            source = json.loads(metadata.read_text(encoding="utf-8"))
            source["related"] = recipe["related"]
            metadata.write_text(json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8")
        if recipe.get("related"):
            continue
        own = terms(recipe)
        candidates = [r for r in stack_recipes[recipe["stack"]] if r["id"] != recipe["id"]]
        candidates.sort(key=lambda r: (-len(own & terms(r)), r["section"] != recipe["section"], not r["project"], r["id"]))
        recipe["related"] = [r["id"] for r in candidates[:3]]
        metadata = ROOT / "catalog" / recipe["stack"] / recipe["id"] / "recipe.json"
        source = json.loads(metadata.read_text(encoding="utf-8"))
        source["related"] = recipe["related"]
        metadata.write_text(json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8")
    bundle = {"format": "RecipeBundle", "version": 1,
              "catalog_version": __version__, "expected_recipes": EXPECTED_RECIPES, "expected_projects": EXPECTED_PROJECTS,
              "stacks": {s: {"label": v[0], "group": v[1], "target": v[2], "project_target": PROJECT_TARGETS[s]} for s, v in STACKS.items()},
              "recipes": recipes}
    destination = ROOT / "devatlas" / "data" / "catalog.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not recipes and destination.exists():
        raise ValueError("Il catalogo sorgente è vuoto: il catalogo precedente viene conservato.")
    temporary = destination.with_name("catalog-" + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_text(json.dumps(bundle, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        Catalog(temporary)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Catalogo: {len(recipes)} schede, {sum(r['project'] for r in recipes)} progetti — {destination.stat().st_size:,} byte")
    return bundle


if __name__ == "__main__":
    compile_catalog()

