"""Verify the complete content contract, exports and executable syntax."""
from __future__ import annotations
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from devatlas.catalog import Catalog
from devatlas.bundles import export_files, validate_recipe
from devatlas.templating import render_recipe
from tools.catalog_support import STACKS, EXPECTED_RECIPES, EXPECTED_PROJECTS, PROJECT_TARGETS
from devatlas.models import SECTIONS


def main():
    catalog = Catalog()
    failures, warnings, snippets, duplicates = [], [], [], {}
    counts, statuses, projects = Counter(), Counter(), Counter()
    syntax = Counter()
    start = time.perf_counter()
    for recipe in catalog.recipes.values():
        counts[recipe.stack] += 1
        statuses[recipe.verification.get("status")] += 1
        if recipe.project:
            projects[recipe.group] += 1
        try:
            validate_recipe(recipe.data)
            if recipe.section not in SECTIONS:
                failures.append([recipe.id, "Sezione sconosciuta: " + recipe.section])
            exported = export_files(recipe.data)
            rendered = render_recipe(recipe.data)
            for field in ("guide", "expected", "versions", "prerequisites"):
                if not recipe.data.get(field, "").strip():
                    failures.append([recipe.id, "Campo mancante: " + field])
            if not recipe.sources or not all(re.match(r"https://[^\s]+$", s) for s in recipe.sources):
                failures.append([recipe.id, "Fonte ufficiale HTTPS mancante o non valida"])
            if not recipe.errors:
                failures.append([recipe.id, "Errori frequenti mancanti"])
            for related in recipe.related:
                if related not in catalog.recipes:
                    failures.append([recipe.id, "Collegamento mancante: " + related])
            if recipe.project and len([a for a in recipe.assets if a["role"] == "file"]) < 2:
                failures.append([recipe.id, "Progetto completo con meno di due file"])
            body = "\n".join(a["content"] for a in rendered["assets"])
            digest = hashlib.sha256(body.encode()).hexdigest()
            duplicates.setdefault(digest, []).append(recipe.id)
            for asset in rendered["assets"]:
                content = asset["content"]
                if asset.get("role") == "snippet":
                    snippets.append([recipe.id, asset["path"]])
                    continue
                if asset["path"].endswith(".py") and asset["role"] == "file":
                    ast.parse(content, filename=asset["path"])
                    syntax["python_ast"] += 1
                if asset["path"].endswith(".json") and asset["role"] == "file":
                    try:
                        json.loads(content)
                        syntax["json"] += 1
                    except json.JSONDecodeError:
                        # VS Code .vscode/*.json may intentionally use JSONC comments.
                        if ".vscode/" in asset["path"] and ("//" in content or "/*" in content):
                            warnings.append([recipe.id, "JSONC IDE: " + asset["path"]])
                        else:
                            raise
        except Exception as error:
            failures.append([recipe.id, str(error)])
    for stack, spec in STACKS.items():
        if counts[stack] != spec[2]:
            failures.append([stack, f"Quota {counts[stack]} anziché {spec[2]}"])
    if sum(counts.values()) != EXPECTED_RECIPES:
        failures.append(["catalogo", f"Il totale deve essere {EXPECTED_RECIPES}"])
    if sum(projects.values()) != EXPECTED_PROJECTS:
        failures.append(["catalogo", f"I progetti completi devono essere {EXPECTED_PROJECTS}"])
    for stack, target in PROJECT_TARGETS.items():
        actual = sum(r.stack == stack and r.project for r in catalog.recipes.values())
        if actual != target:
            failures.append([stack, f"Progetti completi: {actual} anziché {target}"])
    baseline = ROOT / "catalog/baseline-1.1.json"
    if baseline.exists():
        for rid, expected in json.loads(baseline.read_text(encoding="utf-8"))["recipes"].items():
            if rid not in catalog.recipes:
                failures.append([rid, "Scheda precedente rimossa"])
                continue
            actual = {a["id"]: a.get("sha256") for a in catalog.recipes[rid].assets}
            if actual != expected["assets"]:
                failures.append([rid, "Codice di una scheda precedente modificato durante l'ampliamento"])
            if expected.get("asset_paths") and {a["id"]: a["path"] for a in catalog.recipes[rid].assets} != expected["asset_paths"]:
                failures.append([rid, "Percorsi di esportazione di una scheda precedente modificati"])
            if catalog.recipes[rid].project != expected["project"]:
                failures.append([rid, "Classificazione di un progetto precedente modificata"])
    duplicate_groups = [group for group in duplicates.values() if len(group) > 1]
    if duplicate_groups:
        failures.extend(["duplicati", group] for group in duplicate_groups)
    report = {"catalog_sha256": catalog.fingerprint, "recipes": sum(counts.values()), "stacks": len(counts), "counts": dict(counts), "projects": dict(projects),
              "verification": dict(statuses), "syntax_checks": dict(syntax), "failures": failures, "warnings": warnings,
              "snippets": len(snippets), "duplicate_groups": duplicate_groups, "elapsed_s": time.perf_counter() - start}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports/catalog-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("counts",)}, ensure_ascii=False, indent=2))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())

