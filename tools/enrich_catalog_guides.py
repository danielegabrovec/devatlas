"""Apply source-derived editorial details without altering any code assets."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.catalog_support import enrich_editorial


def main():
    changed = []
    for path in sorted((ROOT / "catalog").glob("*/*/recipe.json")):
        original = json.loads(path.read_text(encoding="utf-8"))
        data = dict(original)
        data["guide"] = (path.parent / original["guide_path"]).read_text(encoding="utf-8")
        before = {}
        data["assets"] = []
        for asset in original["assets"]:
            source = path.parent / asset["source"]
            before[asset["source"]] = hashlib.sha256(source.read_bytes()).hexdigest()
            data["assets"].append({**asset, "content": source.read_text(encoding="utf-8")})
        if not enrich_editorial(data):
            continue
        original.update(summary=data["summary"], editorial=data["editorial"])
        path.write_text(json.dumps(original, ensure_ascii=False, indent=2), encoding="utf-8")
        (path.parent / original["guide_path"]).write_text(data["guide"], encoding="utf-8")
        assert before == {name: hashlib.sha256((path.parent / name).read_bytes()).hexdigest() for name in before}
        changed.append(data["id"])
    report = {"changed_recipes": len(changed), "ids": changed, "code_assets_unchanged": True,
              "verification_records_unchanged": True, "method": "Solo fatti presenti negli asset: endpoint, hook, handler, API, proprietà CSS e metodi ORM."}
    (ROOT / "reports/editorial-improvements.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Descrizioni specifiche aggiornate: {len(changed)}; codice invariato.")


if __name__ == "__main__":
    main()

