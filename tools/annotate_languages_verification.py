"""Attach the actual source/runtime evidence to the exact exported source hashes."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COUNTS={"python":120,"cpp":80,"csharp":70,"javascript":55,"typescript":55,"rust":35,"go":30,"java":30,"c":25}
ENVIRONMENTS={
 "python":"CPython 3.11.15, libreria standard",
 "cpp":"GCC/g++ 16.2.0 MSYS2 UCRT64, C++20",
 "csharp":"SDK .NET 10.0.401, C#12, target net8.0, runtime .NET8.0.31",
 "javascript":"Node.js24.15.0, moduli ESM",
 "typescript":"TypeScript6.0.3 strict, target ES2022, Node.js24.15.0",
 "rust":"rustc1.99.0, edition2021, Cargo offline e std",
 "go":"Go1.27.0 windows/amd64, libreria standard",
 "java":"JDK25.0.4.1, compilazione --release17",
 "c":"GCC16.2.0 MSYS2 UCRT64, ISO C17",
}


def main():
    runtime_path=ROOT/"reports"/"languages-runtime-validation.json"
    runtime=json.loads(runtime_path.read_text(encoding="utf-8"))
    rechecks=json.loads((ROOT/"reports"/"languages-asyncio-recheck.json").read_text(encoding="utf-8"))
    assert len(rechecks)==4 and all(item["ok"] for item in rechecks)
    asyncio_ids={item["id"] for item in rechecks}
    failed={item["id"] for item in runtime["results"] if not item["ok"]}
    assert failed==asyncio_ids
    aggregate=next(item for item in runtime["results"] if item["id"]=="csharp-all69-runtime")
    assert aggregate["ok"] and "CSharp programs executed=69" in aggregate["output"]
    passed={item["id"] for item in runtime["results"] if item["ok"]}|asyncio_ids
    proof={}
    count=0;projects=0
    for stack,quota in COUNTS.items():
        paths=sorted((ROOT/"catalog"/stack).glob("*/recipe.json"))
        assert len(paths)==quota
        for path in paths:
            data=json.loads(path.read_text(encoding="utf-8"));rid=data["id"]
            assert rid in passed or (stack=="csharp" and not data["project"]),rid
            environment="CPython3.13.13 della .venv applicazione; esecuzione locale fuori dal sandbox" if rid in asyncio_ids else ENVIRONMENTS[stack]
            verification={"status":"eseguito","details":f"Eseguito su Windows x64 il 29/10/2026. Ambiente: {environment}. Sorgenti compilati/controllati e programmi eseguiti; per i progetti sono stati eseguiti anche i test inclusi. Report: reports/languages-source-validation.json e reports/languages-runtime-validation.json"+("; conferma runtime asyncio: reports/languages-asyncio-recheck.json." if rid in asyncio_ids else ".")+" Linux e macOS non eseguiti.","date":"2026-10-29"}
            hashes={asset["path"]:hashlib.sha256((path.parent/asset["source"]).read_text(encoding="utf-8").encode()).hexdigest() for asset in data["assets"] if asset["role"]=="file"}
            proof[rid]={"assets":hashes,"verification":verification}
            data["verification"]=verification
            path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
            count+=1;projects+=data["project"]
    assert count==500 and projects==9
    (ROOT/"tools"/"languages_verification.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding="utf-8")
    summary={"recipes":count,"projects":projects,"status":{"eseguito":count},"platform":"Windows x64","date":"2026-10-29","environments":ENVIRONMENTS,"asyncio_environment":"CPython3.13.13 fuori dal sandbox,4/4eseguiti","evidence":["reports/languages-source-validation.json","reports/languages-runtime-validation.json","reports/languages-asyncio-recheck.json"],"note":"I timeout storici asyncio nel sandbox sono conservati nel report runtime e risolti dal passaggio locale registrato nel report recheck. Nessun collaudo Linux/macOS attestato. Il builder conserva badge soltanto quando coincidono gli hash dei file sorgenti esportati."}
    (ROOT/"reports"/"languages-verification-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print("500 badges eseguito attached to source hashes;9completeprojects")


if __name__=="__main__":main()
