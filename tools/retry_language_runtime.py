"""Repeat only failed runtime checks after confining TEMP to the workspace."""
import json
import os
from pathlib import Path
import sys
from validate_languages import ROOT,WORK,extract,run


def main():
    report_path=ROOT/"reports"/"languages-runtime-validation.json"
    report=json.loads(report_path.read_text(encoding="utf-8"))
    original=[item for item in report["results"] if not item["ok"]]
    temporary=WORK/"temp";temporary.mkdir(exist_ok=True)
    for key in ("TEMP","TMP","TMPDIR"):os.environ[key]=str(temporary)
    recipes={data["id"]:(data,folder) for data,folder,_ in extract()}
    retried=[]
    for item in original:
        rid=item["id"];data,folder=recipes[rid]
        assert data["stack"]=="python"
        if data["project"]:
            commands=[[sys.executable,"-m","unittest","-v"],[sys.executable,"main.py","add","viti","3"],[sys.executable,"main.py","list"]]
        else:commands=[[sys.executable,"main.py"]]
        for command in commands:
            result=run(command,folder,timeout=8)
            result.update(id=rid,check="execute retry workspace TEMP")
            retried.append(result)
            if not result["ok"]:
                # Capture an explicit interpreter stack as diagnostic evidence.
                diagnosis=run([sys.executable,"-c","import faulthandler,runpy; faulthandler.dump_traceback_later(3,exit=True); runpy.run_path('main.py',run_name='__main__')"],folder,timeout=6)
                result["diagnostic"]=diagnosis["output"]
                print("FAILED",rid,result["output"][-500:],flush=True)
                break
            print("PASS",rid,flush=True)
    failed_ids={item["id"] for item in original}
    report["initial_failed_checks"]=original
    report["results"]=[item for item in report["results"] if item["id"] not in failed_ids]+retried
    report["checks"]=len(report["results"])
    report["failures"]=sum(not item["ok"] for item in report["results"])
    report["runtime_note"]="I controlli falliti sono ripetuti con TEMP/TMP confinati al workspace; eventuali timeout conservano una diagnostica faulthandler. Nessuna esecuzione Linux/macOS attestata."
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Final runtime failures",report["failures"])


if __name__=="__main__":main()
