"""Validate only the 27 added operational workflows; do not rerun historical recipes."""
import ast
import concurrent.futures
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tomllib
import xml.etree.ElementTree as ET
from validate_languages import ROOT,WORK,extract,run


def main():
    recipes=[item for item in extract() if "-workflow-" in item[0]["id"]]
    assert len(recipes)==27 and not any(item[0]["project"] for item in recipes)
    results=[];jobs=[]
    for data,folder,files in recipes:
        rid,stack=data["id"],data["stack"]
        for file in files:
            suffix=file.suffix
            try:
                if suffix==".py":ast.parse(file.read_text(encoding="utf-8"));kind="Python AST"
                elif suffix==".json":json.loads(file.read_text(encoding="utf-8"));kind="JSON parse"
                elif suffix==".toml":tomllib.loads(file.read_text(encoding="utf-8"));kind="TOML parse"
                elif suffix==".csproj":ET.fromstring(file.read_text(encoding="utf-8"));kind="MSBuild XML parse"
                else:continue
                results.append({"id":rid,"file":str(file.relative_to(folder)),"check":kind,"ok":True})
            except Exception as error:results.append({"id":rid,"check":"source parse","ok":False,"output":str(error)})
        if stack=="javascript":
            for file in files:
                if file.suffix==".mjs":jobs.append((rid,["node","--check",str(file)],folder))
        elif stack=="typescript":jobs.append((rid,[shutil.which("tsc.cmd") or shutil.which("tsc"),"-p","tsconfig.json","--noEmit"],folder))
        elif stack in ("cpp","c"):
            sources=[str(file) for file in files if file.suffix in (".cpp",".c")]
            jobs.append((rid,["g++" if stack=="cpp" else "gcc","-std=c++20" if stack=="cpp" else "-std=c17","-fsyntax-only","-Iinclude",*sources],folder))
        elif stack=="csharp":
            jobs.append((rid,["dotnet","build","App.csproj","-v:q","--nologo"],folder))
            if (folder/"tests"/"Smoke.csproj").exists():jobs.append((rid,["dotnet","build","tests/Smoke.csproj","-v:q","--nologo"],folder))
        elif stack=="rust":jobs.append((rid,["cargo","check","--offline"],folder))
        elif stack=="go":jobs.append((rid,["go","test","./..."],folder))
        elif stack=="java":
            (folder/"classes").mkdir(exist_ok=True)
            jobs.append((rid,["javac","-encoding","UTF-8","--release","17","-d","classes",*[str(file) for file in files if file.suffix==".java"]],folder))
    def check(job):
        rid,command,folder=job
        result=run(command,folder,timeout=60);result.update(id=rid,check="source compiler")
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(check,jobs):
            results.append(result)
            if not result["ok"]:print("FAIL",result["id"],result["output"][-1600:],flush=True)
    report={"platform":"Windows x64","date":"2026-10-29","recipes":27,"checks":len(results),"failures":sum(not item["ok"] for item in results),"limitations":"Validazione sorgenti e configurazioni; workflow interattivi di debug, creazione venv, acquisizione pacchetti e distribuzione completa non eseguiti.","results":results}
    (ROOT/"reports"/"languages-workflows-validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({key:value for key,value in report.items() if key!="results"}))
    if report["failures"]:raise SystemExit(1)
    evidence_path=ROOT/"tools"/"languages_verification.json"
    evidence=json.loads(evidence_path.read_text(encoding="utf-8"))
    removed=json.loads((ROOT/"reports"/"languages-replaced-ids.json").read_text(encoding="utf-8"))
    for rid in removed:evidence.pop(rid,None)
    for data,_,_ in recipes:
        rid=data["id"]
        path=ROOT/"catalog"/data["stack"]/rid/"recipe.json"
        hashes={asset["path"]:hashlib.sha256((path.parent/asset["source"]).read_text(encoding="utf-8").encode()).hexdigest() for asset in data["assets"] if asset["role"]=="file"}
        checks=sorted({item["check"] for item in results if item["id"]==rid})
        verification={"status":"statico","date":"2026-10-29","details":"Sorgenti e configurazioni verificati su Windows x64: "+", ".join(checks)+". Report: reports/languages-workflows-validation.json. Non attestati sessioni interattive di debug, installazioni di dipendenze o distribuzione completa del workflow; nessuna esecuzione Linux/macOS."}
        evidence[rid]={"assets":hashes,"verification":verification}
        data["verification"]=verification
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__":main()
