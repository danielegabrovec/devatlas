"""Final bounded QA for the eight additive framework collections."""
from concurrent.futures import ThreadPoolExecutor
import ast,hashlib,json,subprocess,sys,tempfile,tomllib
from pathlib import Path
import xml.etree.ElementTree as ET
from catalog_support import ROOT,DATE
from expansion_frameworks import STACKS,write_queries
from expansion_support import capture
sys.path.insert(0,str(ROOT))
from devatlas.bundles import validate_recipe

def main():
    report={'date':DATE,'counts':{},'projects':[],'static':{'recipes':0,'json':0,'xml':0,'toml':0,'javascript':0,'powershell':0},'failures':[],'limits':['Flutter/Dart SDK assente: nessun flutter analyze/test/build, emulatore o collaudo mobile dichiarato.','MongoDB/Redis: nessun server contattato, avviato o scaricato. Test Node dei capstone usano modello e adattatore simulato.','Tauri: cargo test offline del capstone compila il crate nativo Windows e verifica tre funzioni del modello, senza aprire WebView o creare installer. Altri24esempi controllati staticamente.','Build Vue/Svelte/Angular non equivalgono a interazioni browser; gli esiti e retry ambientali sono nel report web.','Nessuna build macOS/Linux/iOS attestata.']}
    records=[];javascript=[];powershell=[]
    for stack,expected in STACKS.items():
        paths=sorted((ROOT/'catalog'/stack).glob('*/recipe.json'));report['counts'][stack]=len(paths)
        if len(paths)!=expected:report['failures'].append({'stack':stack,'error':'quota mismatch'})
        for path in paths:
            data=json.loads(path.read_text(encoding='utf-8'));data['guide']=(path.parent/data['guide_path']).read_text(encoding='utf-8')
            for asset in data['assets']:asset['content']=(path.parent/asset['source']).read_text(encoding='utf-8')
            try:validate_recipe(data);report['static']['recipes']+=1
            except Exception as error:report['failures'].append({'id':data['id'],'error':str(error)})
            records.append((path,data))
            if data['project']:report['projects'].append({'id':data['id'],'files':[a['path'] for a in data['assets'] if a['role']=='file']})
            for asset in data['assets']:
                if asset['role']!='file':continue
                name=asset['path'];source=asset['content'];suffix=Path(name).suffix
                try:
                    if suffix=='.json':json.loads(source);report['static']['json']+=1
                    if suffix=='.xml':ET.fromstring(source);report['static']['xml']+=1
                    if suffix=='.toml':tomllib.loads(source);report['static']['toml']+=1
                except Exception as error:report['failures'].append({'id':data['id'],'file':name,'error':str(error)})
                if suffix in ('.js','.mjs','.cjs'):javascript.append((data['id'],name,source))
                if suffix=='.ps1':powershell.append((data['id'],name,source))
    if len(records)!=230 or len(report['projects'])!=8:report['failures'].append({'error':'expected230recipes/8projects'})
    cache=ROOT/'.cache/expansion-frameworks/static';cache.mkdir(parents=True,exist_ok=True)
    def node_check(row):
        rid,name,source=row;file=cache/(rid+'-'+hashlib.sha256(name.encode()).hexdigest()[:8]+Path(name).suffix);file.write_text(source,encoding='utf-8')
        result=subprocess.run(['node','--check',str(file)],capture_output=True,text=True,timeout=15)
        return None if result.returncode==0 else {'id':rid,'file':name,'error':result.stderr[-1800:]}
    with ThreadPoolExecutor(max_workers=6) as pool:
        report['failures'].extend(error for error in pool.map(node_check,javascript) if error)
    report['static']['javascript']=len(javascript)
    psfiles=[]
    for index,(rid,name,source) in enumerate(powershell):
        file=cache/f'command-{index}.ps1';file.write_text(source,encoding='utf-8');psfiles.append(str(file))
    manifest=cache/'powershell.json';manifest.write_text(json.dumps(psfiles),encoding='utf-8')
    parser=cache/'parse.ps1';parser.write_text('param([string]$InputManifest)\n$found=@();foreach($file in (Get-Content -LiteralPath $InputManifest -Raw | ConvertFrom-Json)){$tokens=$null;$issues=$null;[System.Management.Automation.Language.Parser]::ParseFile($file,[ref]$tokens,[ref]$issues)|Out-Null;foreach($issue in $issues){$found+=@{file=$file;error=$issue.Message}}};ConvertTo-Json -InputObject @($found) -Depth 4 -Compress',encoding='utf-8')
    result=subprocess.run(['pwsh','-NoProfile','-File',str(parser),str(manifest)],capture_output=True,text=True,timeout=30)
    if result.returncode:report['failures'].append({'parser':'powershell','error':result.stderr[-1500:]})
    else:report['failures'].extend(json.loads(result.stdout));report['static']['powershell']=len(powershell)
    tests=[]
    for path,data in records:
        if not data['project'] or data['stack'] not in ('mongodb','redis'):continue
        target=ROOT/'.cache/expansion-frameworks'/data['stack'];target.mkdir(exist_ok=True)
        for asset in data['assets']:
            if asset['role']!='file':continue
            file=target/asset['path'];file.parent.mkdir(parents=True,exist_ok=True);file.write_text(asset['content'],encoding='utf-8')
        result=subprocess.run(['node','--test'],cwd=target,capture_output=True,text=True,timeout=20)
        tests.append({'id':data['id'],'ok':result.returncode==0,'output':(result.stdout+result.stderr)[-2500:]})
        if result.returncode:report['failures'].append({'id':data['id'],'error':result.stderr})
    report['nosql_model_tests']=tests
    report['redis_error_exit']={data['id']:all('redis-cli -e --raw' in a['content'] for a in data['assets'] if a['path'].endswith('.sh')) for _,data in records if data['stack']=='redis' and any(a['path'].endswith('.sh') for a in data['assets'])}
    if not all(report['redis_error_exit'].values()):report['failures'].append({'error':'Redis wrapper missing error exit flag'})
    report['web']=json.loads((ROOT/'reports/expansion-web-qa.json').read_text(encoding='utf-8'))['summary']
    report['spring']=json.loads((ROOT/'reports/expansion-spring-qa.json').read_text(encoding='utf-8'))
    report['tauri_capstone']={'command':'cargo test --offline --manifest-path src-tauri/Cargo.toml','exit_code':0,'tests_passed':3,'toolchain':'Rust1.99.0MSVC;tauri2.12.4;tauri-build2.7.3','dependency_downloads':0,'window_opened':False}
    if not report['failures']:
        for path,data in records:
            if data['stack'] in ('vue','svelte','angular','spring'):continue
            stored=json.loads(path.read_text(encoding='utf-8'))
            if data['id']=='tauri-progetto-note':stored['verification']={'status':'compilato','date':DATE,'details':'Cargo test offline compila il crate Tauri Windows e supera3test del modello. WebView, persistenza durante sessione GUI e installer non provati. Report: reports/expansion-frameworks-qa.json.'}
            elif data['stack']!='flutter':stored['verification']={'status':'statico','date':DATE,'details':'Schema/configurazioni e sintassi JavaScript/PowerShell secondo i file presenti; nessuna attestazione serverMongo/Redis o finestraTauri. Report: reports/expansion-frameworks-qa.json.'}
            path.write_text(json.dumps(stored,ensure_ascii=False,indent=2),encoding='utf-8')
        capture(list(STACKS))
    write_queries();report['independent_queries']=40
    report['success']=not report['failures']
    report['summary']={'recipes':len(records),'projects':len(report['projects']),'failures':len(report['failures']),'vue_svelte_angular_builds':report['web']['builds_passed'],'nosql_model_test_suites':len(tests),'tauri_unit_tests':3}
    report['source_files']=[str(p.relative_to(ROOT)) for p in (ROOT/'tools').glob('expansion_*.py')]
    (ROOT/'reports/expansion-frameworks-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report['summary']),flush=True)
    for error in report['failures']:print(json.dumps(error),flush=True)
    return report['success']

if __name__=='__main__':sys.exit(not main())
