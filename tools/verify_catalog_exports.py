"""Write and round-trip every recipe ZIP and every complete project directory."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import time
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from devatlas.catalog import Catalog
from devatlas.bundles import export_files, export_project


def main():
    catalog = Catalog()
    directory = ROOT / ".cache/export-audit" / uuid.uuid4().hex[:8]
    directory.mkdir(parents=True)
    failures = []
    total_files = total_projects = parameterized = 0
    start = time.perf_counter()
    for recipe in catalog.recipes.values():
        try:
            expected = export_files(recipe.data)
            target = directory / (recipe.id + ".zip")
            export_project(recipe.data, target, zipped=True)
            with zipfile.ZipFile(target) as archive:
                if archive.testzip() or set(archive.namelist()) != set(expected):
                    raise AssertionError("File ZIP mancanti, inattesi o danneggiati")
                for name, content in expected.items():
                    if archive.read(name) != content.encode("utf-8"):
                        raise AssertionError("Codice modificato durante l'export: " + name)
            total_files += len(expected)
            if recipe.project:
                project = directory / "progetti con spazi è" / recipe.id
                export_project(recipe.data, project)
                for name, content in expected.items():
                    if (project / name).read_bytes() != content.encode("utf-8"):
                        raise AssertionError("Contenuto della cartella diverso dal sorgente")
                total_projects += 1
            if recipe.parameters:
                values = {p["name"]: ("42123" if p.get("type") == "port" else "Verifica123" if p.get("type") == "identifier"
                          else "Verifica.Progetto" if p.get("type") == "namespace" else "cartella_esempio") for p in recipe.parameters}
                export_files(recipe.data, values)
                parameterized += 1
        except Exception as error:
            failures.append({"id": recipe.id, "error": str(error)})
    report = {"catalog_sha256": catalog.fingerprint, "recipes": len(catalog.recipes), "zip_roundtrips": len(catalog.recipes)-len(failures),
              "files_verified": total_files, "complete_project_directories": total_projects, "parameterized_recipes": parameterized,
              "elapsed_s": time.perf_counter()-start, "failures": failures, "success": not failures}
    (ROOT / "reports/catalog-export-roundtrip.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())

