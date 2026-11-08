"""Verify the four real asyncio exports with the application's Python interpreter."""
import json
import os
from pathlib import Path
import sys
from validate_languages import ROOT,WORK,run


def main():
    interpreter=ROOT/".venv"/"Scripts"/"python.exe"
    scratch=WORK/"temp";scratch.mkdir(exist_ok=True)
    for key in ("TEMP","TMP","TMPDIR"):os.environ[key]=str(scratch)
    report_path=ROOT/"reports"/"languages-runtime-validation.json"
    report=json.loads(report_path.read_text(encoding="utf-8"))
    failures=[item for item in report["results"] if not item["ok"]]
    assert all(item["id"].startswith("python-") for item in failures)
    results=[]
    for item in failures:
        folder=WORK/"python"/item["id"]
        result=run([str(interpreter),"main.py"],folder,timeout=8)
        result.update(id=item["id"],check="execute Python3.13 application venv",python="3.13")
        results.append(result)
        print(item["id"],result["ok"],result["output"][-300:],flush=True)
    (ROOT/"reports"/"languages-asyncio-recheck.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")


if __name__=="__main__":main()
