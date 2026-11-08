"""Execute exported language programs and project tests in isolated scratch folders."""
from __future__ import annotations
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import sys
from validate_languages import ROOT, WORK, extract, run


def main():
    # Keep generated temporary data inside the explicitly writable workspace.
    scratch=WORK/"temp"
    scratch.mkdir(parents=True,exist_ok=True)
    os.environ["TEMP"]=str(scratch)
    os.environ["TMP"]=str(scratch)
    os.environ["TMPDIR"]=str(scratch)
    recipes=extract()
    results=[]
    # Emit all TypeScript once, preserving recipe directory boundaries.
    config={"compilerOptions":{"target":"ES2022","module":"NodeNext","moduleResolution":"NodeNext","strict":True,"outDir":"typescript-runtime","rootDir":"typescript","lib":["ES2022","DOM"]},"include":["typescript/**/*.ts"]}
    (WORK/"typescript-runtime.json").write_text(json.dumps(config),encoding="utf-8")
    (WORK/"typescript-runtime").mkdir(exist_ok=True)
    (WORK/"typescript-runtime"/"package.json").write_text('{"type":"module"}',encoding="utf-8")
    result=run([shutil.which("tsc.cmd") or shutil.which("tsc"),"-p","typescript-runtime.json"],WORK)
    result.update(id="typescript-emit-all55",check="emit");results.append(result)
    jobs=[]
    for data,folder,files in recipes:
        stack=data["stack"];project=data["project"];rid=data["id"]
        phases=[]
        if stack=="python":
            if project:phases=[[sys.executable,"-m","unittest","-v"],[sys.executable,"main.py","add","viti","3"],[sys.executable,"main.py","list"]]
            else:phases=[[sys.executable,"main.py"]]
        elif stack=="javascript":
            if project:phases=[["node","--test","expenses.test.mjs"],["node","main.mjs"]]
            else:phases=[["node","main.mjs"]]
        elif stack=="typescript":
            emitted=WORK/"typescript-runtime"/rid
            if project:phases=[["node",str(emitted/"test.js")],["node",str(emitted/"main.js")]]
            else:phases=[["node",str(emitted/"main.js")]]
        elif stack=="csharp":
            if project:phases=[["dotnet","run","--project","Example.csproj","--no-restore"]]
            else:continue
        elif stack=="cpp":
            if project:phases=[["g++","-std=c++20","main.cpp","contacts.cpp","-o","demo.exe"],["g++","-std=c++20","test.cpp","contacts.cpp","-o","tests.exe"],[str(folder/"tests.exe")],[str(folder/"demo.exe")]]
            else:phases=[["g++","-std=c++20","-pthread","main.cpp","-o","demo.exe"],[str(folder/"demo.exe")]]
        elif stack=="c":
            if project:phases=[["gcc","-std=c17","main.c","stats.c","-o","demo.exe"],["gcc","-std=c17","test.c","stats.c","-o","tests.exe"],[str(folder/"tests.exe")],[str(folder/"demo.exe")]]
            else:phases=[["gcc","-std=c17","main.c","-o","demo.exe"],[str(folder/"demo.exe")]]
        elif stack=="rust":
            if project:phases=[["cargo","test","--offline"],["cargo","run","--offline"]]
            elif "test-integrati" in rid:phases=[["rustc","--edition=2021","--test","main.rs","-o","tests.exe"],[str(folder/"tests.exe")]]
            else:phases=[["rustc","--edition=2021","main.rs","-o","demo.exe"],[str(folder/"demo.exe")]]
        elif stack=="go":
            if project:phases=[["go","test","./..."],["go","run","."]]
            elif "test-tabellari" in rid:phases=[["go","test","-v","."]]
            else:phases=[["go","run","."]]
        elif stack=="java":
            if project:phases=[["java","InventoryTest"],["java","Main"]]
            else:phases=[["java","Main"]]
        jobs.append((rid,folder,phases))
    # The 69 regular C# programs have already been compiled under isolated namespaces.
    aggregate=WORK/"csharp-combined"
    runner='''using System.Reflection;
using System.Threading.Tasks;
public static class Runner{public static async Task Main(){int count=0;foreach(var type in typeof(Runner).Assembly.GetTypes().Where(type=>type.Name=="Program"&&type.Namespace!=null&&type.Namespace.StartsWith("Check."))){Console.WriteLine("RUN "+type.Namespace);var method=type.GetMethod("Main",BindingFlags.Public|BindingFlags.Static)!;await (Task)method.Invoke(null,new object[]{Array.Empty<string>()})!;count++;}Console.WriteLine("CSharp programs executed="+count);}}
'''
    (aggregate/"Runner.cs").write_text(runner,encoding="utf-8")
    (aggregate/"Checks.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><StartupObject>Runner</StartupObject><TargetFramework>net8.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><LangVersion>12</LangVersion></PropertyGroup></Project>',encoding="utf-8")
    jobs.append(("csharp-all69-runtime",aggregate,[["dotnet","run","--project","Checks.csproj","--no-restore"]]))
    def check(job):
        rid,folder,phases=job;records=[]
        for command in phases:
            result=run(command,folder,timeout=8 if command[0]==sys.executable else 90);result.update(id=rid,check="execute" if command[0] not in ("gcc","g++","rustc","tsc") else "build")
            records.append(result)
            if not result["ok"]:
                print("FAIL",rid,result["output"][-1200:],flush=True)
                break
        return records
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for records in pool.map(check,jobs):results.extend(records)
    report={"platform":sys.platform,"date":"2026-10-29","recipes":500,"projects":9,"checks":len(results),"failures":sum(not item["ok"] for item in results),"results":results}
    output=ROOT/"reports"/"languages-runtime-validation.json";output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({key:value for key,value in report.items() if key!="results"}))
    raise SystemExit(1 if report["failures"] else 0)


if __name__=="__main__":main()
