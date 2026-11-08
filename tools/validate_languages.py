"""Actual Windows source checks; reports evidence, never upgrades recipe badges implicitly."""
from __future__ import annotations
import ast
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/".cache"/"languages-validation"
STACKS={"python":120,"cpp":80,"csharp":70,"javascript":55,"typescript":55,"rust":35,"go":30,"java":30,"c":25}


def run(command,cwd,timeout=90):
    start=time.monotonic()
    try:
        result=subprocess.run(command,cwd=cwd,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout)
        return {"ok":result.returncode==0,"command":command,"seconds":round(time.monotonic()-start,3),"output":(result.stdout+result.stderr)[-6000:]}
    except (OSError,subprocess.TimeoutExpired) as error:
        return {"ok":False,"command":command,"seconds":round(time.monotonic()-start,3),"output":str(error)}


def extract():
    recipes=[]
    for stack,count in STACKS.items():
        paths=sorted((ROOT/"catalog"/stack).glob("*/recipe.json"))
        assert len(paths)==count,(stack,len(paths),count)
        assert sum(json.loads(path.read_text(encoding="utf-8"))["project"] for path in paths)==1
        for path in paths:
            data=json.loads(path.read_text(encoding="utf-8"))
            folder=WORK/stack/data["id"]
            folder.mkdir(parents=True,exist_ok=True)
            files=[]
            for asset in data["assets"]:
                if asset["role"]!="file":continue
                content=(path.parent/asset["source"]).read_text(encoding="utf-8")
                destination=asset["path"]
                for parameter in data["parameters"]:
                    needle="{{"+parameter["name"]+"}}"
                    content=content.replace(needle,str(parameter["default"]))
                    destination=destination.replace(needle,str(parameter["default"]))
                target=folder/destination
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(content,encoding="utf-8")
                files.append(target)
            recipes.append((data,folder,files))
    return recipes


def main():
    WORK.mkdir(parents=True,exist_ok=True)
    recipes=extract()
    requested=set(sys.argv[1:]) or set(STACKS)
    results=[];jobs=[]
    for data,folder,files in recipes:
        stack=data["stack"]
        if stack not in requested:continue
        if stack=="python":
            for file in files:
                if file.suffix!=".py":continue
                try:ast.parse(file.read_text(encoding="utf-8"),filename=str(file));results.append({"id":data["id"],"file":str(file),"check":"ast","ok":True})
                except SyntaxError as error:results.append({"id":data["id"],"check":"ast","ok":False,"output":str(error)})
        elif stack=="javascript":
            for file in files:
                if file.suffix==".mjs":jobs.append((data["id"],"node syntax",["node","--check",str(file)],folder))
        elif stack in ("cpp","c"):
            sources=[str(file) for file in files if file.suffix in (".c",".cpp")]
            jobs.append((data["id"],"compiler syntax",["g++" if stack=="cpp" else "gcc","-std=c++20" if stack=="cpp" else "-std=c17","-fsyntax-only",*sources],folder))
        elif stack=="rust":
            jobs.append((data["id"],"cargo check" if data["project"] else "rustc metadata",["cargo","check","--offline"] if data["project"] else ["rustc","--edition=2021","--emit=metadata","main.rs"],folder))
        elif stack=="go":jobs.append((data["id"],"go test",["go","test","./..."],folder))
        elif stack=="java":jobs.append((data["id"],"javac",["javac","-encoding","UTF-8","--release","17",*[str(file) for file in files if file.suffix==".java"]],folder))
    if "typescript" in requested:
        config={"compilerOptions":{"target":"ES2022","module":"NodeNext","moduleResolution":"NodeNext","strict":True,"noEmit":True,"lib":["ES2022","DOM"]},"include":["typescript/**/*.ts"]}
        (WORK/"typescript-check.json").write_text(json.dumps(config),encoding="utf-8")
        command=shutil.which("tsc.cmd") or shutil.which("tsc")
        jobs.append(("typescript-all55","tsc strict",[command,"-p","typescript-check.json"],WORK))
    if "csharp" in requested:
        aggregate=WORK/"csharp-combined";aggregate.mkdir(exist_ok=True)
        for index,(data,folder,files) in enumerate(recipes):
            if data["stack"]!="csharp":continue
            if data["project"]:
                jobs.append((data["id"],"dotnet build",["dotnet","build","Example.csproj","--nologo","-v:q"],folder));continue
            source=(folder/"Program.cs").read_text(encoding="utf-8")
            (aggregate/f"R{index}.cs").write_text(f"namespace Check.R{index}{{\n"+source+"\n}\n",encoding="utf-8")
        (aggregate/"Checks.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><LangVersion>12</LangVersion></PropertyGroup></Project>',encoding="utf-8")
        jobs.append(("csharp-all69","dotnet build",["dotnet","build","Checks.csproj","--nologo","-v:q"],aggregate))
    def check(job):
        rid,kind,command,folder=job
        result=run(command,folder)
        result.update(id=rid,check=kind)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(check,jobs):
            results.append(result)
            if not result["ok"]:print("FAIL",result["id"],result["output"][-1000:],flush=True)
    report={"platform":sys.platform,"date":"2026-10-29","recipes":len(recipes),"requested":sorted(requested),"checks":len(results),"failures":sum(not result["ok"] for result in results),"results":results}
    (WORK/"results.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({key:value for key,value in report.items() if key!="results"},ensure_ascii=False))
    raise SystemExit(1 if report["failures"] else 0)


if __name__=="__main__":main()
