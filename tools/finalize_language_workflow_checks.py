"""Check the previously untested command syntax and TS test runner, then finalize evidence."""
import hashlib
import json
from pathlib import Path
from validate_languages import ROOT,WORK,run


def main():
    report_path=ROOT/"reports"/"languages-workflows-validation.json"
    report=json.loads(report_path.read_text(encoding="utf-8"))
    known={(item["id"],item["check"]) for item in report["results"]}
    recipes=[]
    for path in (ROOT/"catalog").glob("*/**/recipe.json"):
        data=json.loads(path.read_text(encoding="utf-8"))
        if "-workflow-" in data["id"] and data["stack"] in ("python","cpp","csharp","javascript","typescript","rust","go","java","c"):recipes.append((data,path))
    assert len(recipes)==27
    for data,path in recipes:
        folder=WORK/data["stack"]/data["id"]
        command_path=folder/"workflow-commands.ps1"
        commands="\n".join((path.parent/asset["source"]).read_text(encoding="utf-8") for asset in data["assets"] if asset["role"]=="command")
        command_path.write_text(commands,encoding="utf-8")
        if (data["id"],"PowerShell parser") not in known:
            script="$taskTokens=$null;$taskErrors=$null;[void][System.Management.Automation.Language.Parser]::ParseFile($args[0],[ref]$taskTokens,[ref]$taskErrors);if($taskErrors.Count){$taskErrors|ForEach-Object{$_.Message};exit 1}"
            # -Command arguments differ across shells; a literal script file receives the path reliably.
            parser=WORK/"parse-workflow.ps1"
            parser.write_text("param([string]$TaskFile)\n$taskTokens=$null\n$taskErrors=$null\n[void][System.Management.Automation.Language.Parser]::ParseFile($TaskFile,[ref]$taskTokens,[ref]$taskErrors)\nif($taskErrors.Count){$taskErrors|ForEach-Object{$_.Message};exit 1}\n",encoding="utf-8")
            result=run(["powershell.exe","-NoProfile","-ExecutionPolicy","Bypass","-File",str(parser),str(command_path)],folder,timeout=15)
            result.update(id=data["id"],check="PowerShell parser");report["results"].append(result)
        if data["stack"]=="typescript":
            for asset in data["assets"]:
                if asset["role"]=="file" and asset["path"].endswith(".mjs") and (data["id"],"JS test runner syntax") not in known:
                    result=run(["node","--check",str(folder/asset["path"])],folder)
                    result.update(id=data["id"],check="JS test runner syntax");report["results"].append(result)
    report["checks"]=len(report["results"]);report["failures"]=sum(not item["ok"] for item in report["results"])
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    assert report["failures"]==0,[item for item in report["results"] if not item["ok"]]
    evidence_path=ROOT/"tools"/"languages_verification.json"
    evidence=json.loads(evidence_path.read_text(encoding="utf-8"))
    for data,path in recipes:
        verification=data["verification"]
        checks=sorted({item["check"] for item in report["results"] if item["id"]==data["id"]})
        verification["details"]="Sorgenti e configurazioni verificati su Windows x64: "+", ".join(checks)+". Report: reports/languages-workflows-validation.json. Non attestati sessioni interattive di debug, installazioni di dipendenze o distribuzione completa del workflow; nessuna esecuzione Linux/macOS."
        evidence[data["id"]]["verification"]=verification
        data["verification"]=verification
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Workflow checks",report["checks"],"failures",report["failures"])


if __name__=="__main__":main()
