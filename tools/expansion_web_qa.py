"""Compile new framework examples with one isolated SDK cache per framework."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from catalog_support import ROOT, DATE

def run_web():
    report={"date":DATE,"node":"","checks":[],"failures":[],"limits":["Build del frontend e test del modello su Windows; nessuna sessione browser interattiva attestata.","Le dipendenze sono installate una volta in .cache/expansion-frameworks, non nei progetti dell'utente."]}
    report["node"]=subprocess.check_output(['node','--version'],text=True).strip()
    def process(stack):
        sdk=ROOT/'.cache/expansion-frameworks'/stack
        paths=sorted((ROOT/'catalog'/stack).glob('*/recipe.json'))
        checks=[];previous=[]
        cli=sdk/'node_modules'/('@angular/cli/bin/ng.js' if stack=='angular' else 'vite/bin/vite.js')
        for path in paths:
            data=json.loads(path.read_text(encoding='utf-8'))
            for old in previous:
                assert old.resolve().is_relative_to(sdk.resolve())
                if old.is_file():old.unlink()
            previous=[]
            for asset in data['assets']:
                if asset['role']!='file':continue
                target=sdk/asset['path'];assert target.resolve().is_relative_to(sdk.resolve())
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text((path.parent/asset['source']).read_text(encoding='utf-8'),encoding='utf-8')
                previous.append(target)
            start=time.perf_counter()
            args=['node',str(cli),'build']+(['--configuration','development','--no-progress'] if stack=='angular' else ['--logLevel','error'])
            try:
                result=subprocess.run(args,cwd=sdk,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=75)
                record={'id':data['id'],'stack':stack,'build_ok':result.returncode==0,'seconds':round(time.perf_counter()-start,3),'output':(result.stdout+result.stderr)[-3500:]}
            except subprocess.TimeoutExpired:record={'id':data['id'],'stack':stack,'build_ok':False,'output':'build timeout75s'}
            if data['project'] or data['id'].endswith('-test'):
                result=subprocess.run(['node','--test'],cwd=sdk,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=20)
                record['model_tests_ok']=result.returncode==0;record['test_output']=(result.stdout+result.stderr)[-2500:]
            if record['build_ok'] and record.get('model_tests_ok',True):
                data['verification']={'status':'compilato','date':DATE,'details':f"Build reale {stack} su Node{report['node']}/Windows con dipendenze del manifest. "+('Test node --test del modello superati. ' if 'model_tests_ok' in record else '')+"Interazioni browser e hosting non attestati. Report: reports/expansion-web-qa.json."}
                path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
            checks.append(record)
        return checks
    with ThreadPoolExecutor(max_workers=3) as pool:
        for records in pool.map(process,['vue','svelte','angular']):
            report['checks'].extend(records)
    report['failures']=[r for r in report['checks'] if not r['build_ok'] or not r.get('model_tests_ok',True)]
    report['summary']={'recipes':len(report['checks']),'builds_passed':sum(r['build_ok'] for r in report['checks']),'model_test_suites':sum('model_tests_ok' in r for r in report['checks']),'failures':len(report['failures'])}
    (ROOT/'reports/expansion-web-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report['summary']),flush=True)
    for row in report['failures']:print(json.dumps(row,ensure_ascii=False),flush=True)
    return report

if __name__=='__main__':sys.exit(bool(run_web()['failures']))
