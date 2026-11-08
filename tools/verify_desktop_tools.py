"""Bounded verification of the desktop/tools catalog; never run catalog shell commands."""
from __future__ import annotations
import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
STACKS={"pyside6":100,"pyqt6":60,"qt-cpp":60,"electron":40,"avalonia":35,"maui":30,"winui":25,"powershell":30,"bash":20,"git":40,"cmake":25,"docker":35,"cicd":30,"packaging":20}

def check_all():
    report={"date":"2026-10-29","scope":STACKS,"counts":{},"projects":[],"static":{"python":0,"json":0,"xml":0,"javascript":0,"powershell":0,"bash":0,"csharp_string_checks":0,"hashes":0},"errors":[],"qt_smoke":[],"limitations":["Offscreen smoke tests only construct each PySide6 window and run its event loop for 150 ms; no user dialogs, clipboard, network, printer or installer are activated.","PyQt6 examples receive Python AST checks; runtime PyQt6 is not installed in the PySide6 environment.","Qt smoke redirects QSettings and QStandardPaths to a temporary directory and sets the Qt plugin path explicitly for Windows paths containing commas.","C++/.NET compilation, actual Docker/CI jobs and packaging/signing are not claimed verified by this report.","C# string scanning and XML parsing detect structural mistakes, but are not a C# compiler or XAML compiler."]}
    recipes=[]
    js=[]
    ps=[]
    bash=[]
    for stack,expected in STACKS.items():
        paths=sorted((ROOT/"catalog"/stack).glob("*/recipe.json"))
        report["counts"][stack]=len(paths)
        if len(paths)!=expected:report["errors"].append({"stack":stack,"error":f"Expected {expected}, found {len(paths)}"})
        for path in paths:
            item=json.loads(path.read_text(encoding="utf-8"));recipes.append((path,item))
            if item["project"]:report["projects"].append({"id":item["id"],"files":[a["path"] for a in item["assets"] if a["role"]=="file"],"verification":"manifest-and-static-syntax-only"})
            for asset in item["assets"]:
                source=path.parent/asset["source"]
                content=source.read_text(encoding="utf-8")
                digest=hashlib.sha256(content.encode()).hexdigest()
                report["static"]["hashes"]+=1
                if digest!=asset["sha256"]:report["errors"].append({"id":item["id"],"path":asset["path"],"error":"digest mismatch"})
                ext=Path(asset["path"]).suffix
                if asset["role"]=="file":
                    try:
                        if ext==".py":ast.parse(content,filename=asset["path"]);report["static"]["python"]+=1
                        if ext==".json":json.loads(content);report["static"]["json"]+=1
                        if ext in {".csproj",".xaml",".xml",".ui"}:ET.fromstring(content);report["static"]["xml"]+=1
                        if ext==".cs":
                            quoted=False;escaped=False
                            for char in content:
                                if quoted:
                                    if char=="\n":raise ValueError("Newline inside a regular C# string")
                                    if escaped:escaped=False
                                    elif char=="\\":escaped=True
                                    elif char=='"':quoted=False
                                elif char=='"':quoted=True
                            if quoted:raise ValueError("Unterminated C# string")
                            report["static"]["csharp_string_checks"]+=1
                    except (SyntaxError,ValueError,ET.ParseError) as exc:report["errors"].append({"id":item["id"],"path":asset["path"],"error":str(exc)})
                    if ext in {".js",".cjs",".mjs"}:js.append((item["id"],asset["path"],content))
                    if ext==".ps1":ps.append((item["id"],asset["path"],content))
                    if ext==".sh":bash.append((item["id"],asset["path"],content))
            if item["project"]:
                names={a["path"] for a in item["assets"] if a["role"]=="file"}
                required={"pyside6":{"main.py","requirements.txt"},"pyqt6":{"main.py","requirements.txt"},"qt-cpp":{"main.cpp","CMakeLists.txt"},"electron":{"package.json","main.cjs","preload.cjs","index.html","renderer.js"},"avalonia":{"RecipeApp.csproj","Program.cs"},"maui":{"RecipeApp.csproj","App.cs","MainPage.cs","MauiProgram.cs","Platforms/Windows/App.xaml","Platforms/Windows/App.xaml.cs"},"winui":{"RecipeApp.csproj","App.xaml","App.xaml.cs","MainWindow.cs"},"git":{"lab.ps1"},"cmake":{"CMakeLists.txt","include/calc.hpp","src/calc.cpp","tests/calc_test.cpp"},"docker":{"Dockerfile","app.py","compose.yaml"}}[stack]
                if not required.issubset(names):report["errors"].append({"id":item["id"],"error":f"Project files missing: {required-names}"})
    node=shutil.which("node")
    (ROOT/"reports").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="desktop-qa-",dir=ROOT/"reports") as tmp:
        scratch=Path(tmp)
        assert scratch.resolve().is_relative_to((ROOT/"reports").resolve())
        if node:
            for index,(rid,name,content) in enumerate(js):
                file=scratch/f"js-{index}{Path(name).suffix}";file.write_text(content,encoding="utf-8")
                result=subprocess.run([node,"--check",str(file)],capture_output=True,text=True,timeout=15)
                report["static"]["javascript"]+=1
                if result.returncode:report["errors"].append({"id":rid,"path":name,"error":result.stderr.strip()})
        git_bash=Path("C:/Program Files/Git/bin/bash.exe")
        if git_bash.exists():
            for index,(rid,name,content) in enumerate(bash):
                file=scratch/f"bash-{index}.sh";file.write_text(content,encoding="utf-8",newline="\n")
                result=subprocess.run([str(git_bash),"-n",str(file)],capture_output=True,text=True,timeout=15)
                if result.returncode and "NtCreateDirectoryObject" in result.stderr:
                    report["limitations"].append("Bash syntax checking unavailable: Git Bash cannot initialize its MSYS shared object in the sandbox (NtCreateDirectoryObject access denied). No Bash parser success is claimed; Bash recipes retain documented status.")
                    report["bash_unavailable"]={"reason":result.stderr.strip(),"skipped":len(bash)-index}
                    break
                report["static"]["bash"]+=1
                if result.returncode:report["errors"].append({"id":rid,"path":name,"error":result.stderr.strip()})
        pwsh=shutil.which("pwsh")
        if pwsh:
            manifest=[]
            for index,(rid,name,content) in enumerate(ps):
                file=scratch/f"ps-{index}.ps1";file.write_text(content,encoding="utf-8");manifest.append({"id":rid,"name":name,"path":str(file)})
            data=scratch/"powershell.json";data.write_text(json.dumps(manifest),encoding="utf-8")
            checker=scratch/"parse.ps1"
            checker.write_text('''param([string]$Manifest)
$issues=@()
foreach($row in (Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json)){
 $tokens=$null;$parseErrors=$null
 [System.Management.Automation.Language.Parser]::ParseFile($row.path,[ref]$tokens,[ref]$parseErrors) | Out-Null
 foreach($issue in $parseErrors){$issues+=@{id=$row.id;path=$row.name;error=$issue.Message}}
}
ConvertTo-Json -InputObject @($issues) -Depth 6 -Compress
''',encoding="utf-8")
            result=subprocess.run([pwsh,"-NoProfile","-File",str(checker),str(data)],capture_output=True,text=True,timeout=60)
            report["static"]["powershell"]=len(ps)
            if result.returncode:report["errors"].append({"error":result.stderr})
            else:report["errors"].extend(json.loads(result.stdout))
        python=ROOT/".venv"/"Scripts"/"python.exe"
        if not python.exists():report["errors"].append({"error":"Local PySide6 venv unavailable"})
        else:
            work=[]
            for path,item in recipes:
                if item["stack"]!="pyside6":continue
                sys.path.insert(0,str(ROOT))
                from devatlas.templating import render_recipe
                run_data=dict(item)
                run_data["assets"]=[{**asset,"content":(path.parent/asset["source"]).read_text(encoding="utf-8")} for asset in item["assets"]]
                rendered=render_recipe(run_data)
                asset=next(a for a in rendered["assets"] if a["path"]=="main.py")
                code=asset["content"]
                folder=scratch/item["id"];folder.mkdir()
                for extra in rendered["assets"]:
                    if extra["role"]!="file" or extra["path"]=="main.py":continue
                    target=folder/extra["path"]
                    assert target.resolve().is_relative_to(folder.resolve())
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_text(extra["content"],encoding="utf-8")
                # Add a bounded event-loop timer without changing source assets.
                code=code.replace("app = QApplication(sys.argv)","app = QApplication(sys.argv)\n    QTimer.singleShot(150, app.quit)")
                harness='''import sys,os,tempfile
sys.path.insert(0,ROOT_PATH)
os.environ["QT_QPA_PLATFORM"]="offscreen"
os.environ["TEMP"]=TEMP_PATH
os.environ["TMP"]=TEMP_PATH
tempfile.tempdir=TEMP_PATH
from devatlas.qt_bootstrap import configure_qt_plugins
configure_qt_plugins()
from PySide6.QtCore import QTimer,QSettings,QStandardPaths
QSettings.setDefaultFormat(QSettings.Format.IniFormat)
QSettings.setPath(QSettings.Format.IniFormat,QSettings.Scope.UserScope,TEMP_PATH)
QStandardPaths.writableLocation=staticmethod(lambda *args:TEMP_PATH)
'''.replace("ROOT_PATH",repr(str(ROOT))).replace("TEMP_PATH",repr(str(folder)))
                file=folder/"smoke.py";file.write_text(harness+code,encoding="utf-8")
                work.append((item["id"],file,folder))
            def run_one(task):
                rid,file,folder=task
                try:
                    result=subprocess.run([str(python),str(file)],cwd=folder,capture_output=True,text=True,timeout=15)
                    return {"id":rid,"ok":result.returncode==0,"exit_code":result.returncode,"stderr":result.stderr.strip()[:2500]}
                except subprocess.TimeoutExpired:return {"id":rid,"ok":False,"error":"timeout"}
            with ThreadPoolExecutor(max_workers=6) as pool:
                report["qt_smoke"]=list(pool.map(run_one,work))
            for row in report["qt_smoke"]:
                if not row["ok"]:report["errors"].append({"id":row["id"],"error":row.get("stderr",row.get("error"))})
    report["success"]=not report["errors"]
    report["project_count"]=len(report["projects"])
    out=ROOT/"reports"/"desktop-tools-qa.json";out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    if report["success"]:
        smoke_ids={r["id"] for r in report["qt_smoke"] if r["ok"]}
        for path,item in recipes:
            if item["id"] in smoke_ids:
                item["verification"]={"status":"eseguito","details":"Avvio reale Windows con PySide6 6.12.0, piattaforma offscreen, costruzione finestra e ciclo eventi 150 ms. Interazioni e altri sistemi non verificati. Report: reports/desktop-tools-qa.json.","date":"2026-10-29"}
            elif item["stack"] in {"pyqt6","electron","powershell","avalonia","maui","winui","cicd","packaging","git","docker"} or item["stack"]=="bash" and report["static"]["bash"]==20:
                item["verification"]={"status":"statico","details":"Controlli statici sui sorgenti: AST Python, parser PowerShell/Bash dove disponibili, node --check per JavaScript, JSON e XML secondo i file presenti. Nessuna compilazione C#/XAML/C++ né esecuzione Docker/CI/packaging attestata. Report: reports/desktop-tools-qa.json.","date":"2026-10-29"}
            path.write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"counts":report["counts"],"static":report["static"],"projects":len(report["projects"]),"qt_ok":sum(x["ok"] for x in report["qt_smoke"]),"qt_total":len(report["qt_smoke"]),"errors":report["errors"]},ensure_ascii=False,indent=2))
    return report

if __name__=="__main__":sys.exit(not check_all()["success"])
