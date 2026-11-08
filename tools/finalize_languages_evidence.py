"""Keep historical runs distinct from the final 473+27 coverage split."""
import collections
import json
from pathlib import Path
from validate_languages import ROOT,STACKS


def main():
    removed=json.loads((ROOT/"reports"/"languages-replaced-ids.json").read_text(encoding="utf-8"))
    runtime_path=ROOT/"reports"/"languages-runtime-validation.json"
    runtime=json.loads(runtime_path.read_text(encoding="utf-8"))
    rechecks=json.loads((ROOT/"reports"/"languages-asyncio-recheck.json").read_text(encoding="utf-8"))
    assert len(rechecks)==4 and all(item["ok"] for item in rechecks)
    failures=[item for item in runtime["results"] if not item["ok"]]
    if failures:
        assert {item["id"] for item in failures}=={item["id"] for item in rechecks}
        runtime["sandbox_failed_checks"]=failures
        runtime["results"]=[item for item in runtime["results"] if item["ok"]]+rechecks
    runtime["checks"]=len(runtime["results"]);runtime["failures"]=sum(not item["ok"] for item in runtime["results"])
    runtime["catalog_snapshot"]="Inventario originale di500ricette prima della sostituzione operativa di27schede;473ricette conservate nel catalogo finale."
    runtime["replaced_ids"]=removed
    runtime["runtime_note"]="Il passaggio Python3.13.13 fuori dal sandbox ha risolto i4timeout asyncio; i precedenti limiti sono conservati nella cronologia. Il nuovo catalogo include27workflow controllati separatamente, senza attribuirgli l'esecuzione dei precedenti27esempi."
    runtime_path.write_text(json.dumps(runtime,ensure_ascii=False,indent=2),encoding="utf-8")
    source_path=ROOT/"reports"/"languages-source-validation.json"
    source=json.loads(source_path.read_text(encoding="utf-8"))
    source["catalog_snapshot"]="Inventario originale; per le27sostituzioni operative usare languages-workflows-validation.json."
    source["replaced_ids"]=removed
    source_path.write_text(json.dumps(source,ensure_ascii=False,indent=2),encoding="utf-8")
    rows=[]
    for stack,count in STACKS.items():
        selected=[json.loads(path.read_text(encoding="utf-8")) for path in (ROOT/"catalog"/stack).glob("*/recipe.json")]
        assert len(selected)==count
        rows.extend(selected)
    counts=dict(collections.Counter(item["verification"]["status"] for item in rows))
    assert counts=={"eseguito":473,"statico":27},counts
    assert sum(item["project"] for item in rows)==9
    summary={"recipes":500,"projects":9,"status":counts,"platform":"Windows x64","date":"2026-10-29","retained_runtime_recipes":473,"new_operational_workflows":27,"historical_original_recipes_executed":500,"source_checks_original":source["checks"],"source_failures_original":source["failures"],"workflow_checks":json.loads((ROOT/"reports"/"languages-workflows-validation.json").read_text(encoding="utf-8"))["checks"],"evidence":["reports/languages-source-validation.json","reports/languages-runtime-validation.json","reports/languages-asyncio-recheck.json","reports/languages-workflows-validation.json"],"note":"Il catalogo finale conserva473esempi eseguiti e27nuoveprocedure con sorgenti/configurazioni controllati staticamente. Le sessioni interattive di debug e l'intera consegna dei27workflow non sono attestate. Il builder preserva i badge soltanto per file con hash identici alla prova registrata. Nessun collaudo Linux/macOS."}
    (ROOT/"reports"/"languages-verification-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))


if __name__=="__main__":main()
