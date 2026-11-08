"""Measure independently authored retrieval cases and engine performance."""
from __future__ import annotations
from dataclasses import replace
import json
from pathlib import Path
import statistics
import sys
import time
import concurrent.futures
import hashlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from devatlas.catalog import Catalog
from devatlas.models import SearchQuery
from devatlas.search import SearchIndex


def main():
    catalog = Catalog()
    index = SearchIndex(ROOT / ".cache/search-evaluation.sqlite")
    index.rebuild(catalog.recipes, catalog.fingerprint)
    cases = []
    for path in sorted((ROOT / "reports").glob("search-cases-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        cases.extend({**case, "source": path.name} for case in (data if isinstance(data, list) else data["cases"]))
    results = []
    for case in cases:
        query = SearchQuery(case["query"], limit=3)
        result = index.search(query)
        relevant = set(case["expected_ids"])
        missing = relevant - catalog.recipes.keys()
        success = bool(relevant & set(result.ids))
        results.append({**case, "top3": result.ids, "success": success, "elapsed_ms": result.elapsed_ms, "missing_expected_ids": list(missing), "suggestions": result.suggestions})
    # Measure ranking work and cached requests separately. A cache hit must not
    # be presented as the cost of answering a new question.
    durations, warm = [], []
    for _ in range(3):
        for case in cases:
            with index._lock:
                index._cache.clear()
                index._suggestions.clear()
            started = time.perf_counter()
            index.search(SearchQuery(case["query"], limit=50))
            durations.append((time.perf_counter() - started) * 1000)
    for case in cases:
        index.search(SearchQuery(case["query"], limit=50))
        for _ in range(3):
            started = time.perf_counter()
            index.search(SearchQuery(case["query"], limit=50))
            warm.append((time.perf_counter() - started) * 1000)
    durations.sort()
    p95 = durations[min(len(durations)-1, int(len(durations)*.95))] if durations else None
    passed = sum(r["success"] for r in results)
    report = {"catalog_sha256": catalog.fingerprint, "cases": len(results), "passed": passed, "top3_rate": passed / len(results) if results else 0,
              "p95_ms": p95, "cold_p95_ms": p95, "warm_p95_ms": sorted(warm)[min(len(warm)-1, int(len(warm)*.95))] if warm else None,
              "original_cases": sum(c["source"] != "search-cases-extended.json" and not c["source"].startswith("search-cases-expansion-") for c in cases),
              "original_passed": sum(r["success"] and r["source"] != "search-cases-extended.json" and not r["source"].startswith("search-cases-expansion-") for r in results),
              "expansion_cases": sum(c["source"].startswith("search-cases-expansion-") for c in cases),
              "expansion_passed": sum(r["success"] and r["source"].startswith("search-cases-expansion-") for r in results),
              "heldout_cases": sum(c["source"] == "search-cases-extended.json" for c in cases),
              "heldout_passed": sum(r["success"] and r["source"] == "search-cases-extended.json" for r in results),
              "max_ms": max(durations) if durations else None,
              "method": "Cold: cache ranking/suggerimenti svuotata prima di ogni richiesta; timer esterno include attesa lock. Warm: ogni query preparata e ripetuta subito tre volte, per evitare eviction quando i casi superano la capacità della cache. Stemming e preparazione dell'indice esclusi dalla latenza query.", "results": results}
    (ROOT / "reports/search-evaluation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    improvement_path = ROOT / "reports/search-improvement.json"
    if improvement_path.exists():
        improvement = json.loads(improvement_path.read_text(encoding="utf-8"))
        for key in ("catalog_sha256", "cases", "passed", "original_cases", "original_passed", "heldout_cases", "heldout_passed", "expansion_cases", "expansion_passed", "results", "method"):
            improvement[key] = report[key]
        def stats(values):
            values = sorted(values)
            return {"samples": len(values), "median_ms": statistics.median(values), "p95_ms": values[min(len(values)-1, int(len(values)*.95))], "max_ms": max(values)}
        improvement["cold_query"], improvement["warm_query"] = stats(durations), stats(warm)
        improvement["search_source_sha256"] = hashlib.sha256((ROOT / "devatlas/search.py").read_bytes()).hexdigest()
        def run_parallel(case):
            return bool(set(index.search(SearchQuery(case["query"], limit=3)).ids) & set(case["expected_ids"]))
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            parallel = list(pool.map(run_parallel, cases * 3))
        improvement["parallel_correct"] = all(parallel)
        improvement["parallel_checks"] = len(parallel)
        improvement.pop("parallel_warm_8_workers", None)
        improvement_path.write_text(json.dumps(improvement, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, indent=2))
    for result in results:
        if not result["success"]:
            print(result["query"], "=>", result["top3"], "expected", result["expected_ids"])
    return not (len(results) >= 100 and report["top3_rate"] >= .9 and p95 < 150 and not any(r["missing_expected_ids"] for r in results))


if __name__ == "__main__":
    raise SystemExit(main())

