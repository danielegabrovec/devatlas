"""Riprova i limiti sandbox e consolida soltanto verifiche delle fonti correnti."""
import ast,hashlib,json,os,sqlite3,subprocess,sys,time,urllib.request,urllib.error
from pathlib import Path
from qa_web_database import ROOT,CACHE,run

def main():
    report=json.loads((ROOT/'reports/web-database-qa.json').read_text(encoding='utf8'))
    lifecycle=json.loads((ROOT/'reports/web-lifecycle-qa.json').read_text(encoding='utf8'))
    verification=json.loads((ROOT/'tools/web_verification.json').read_text(encoding='utf8'))
    verification.update(json.loads((CACHE/'lifecycle-verification.json').read_text(encoding='utf8')))
    records={}
    stacks=['nodejs','react','nextjs','aspnet','fastapi','html-css','django','sql','sqlite','postgresql','mysql']
    for stack in stacks:
        for p in (ROOT/'catalog'/stack).glob('*/recipe.json'):
            r=json.loads(p.read_text(encoding='utf8'))
            for a in r['assets']:a['content']=(p.parent/a['source']).read_text(encoding='utf8')
            records[r['id']]=r
    report['historical_removed_checks']=[c for c in report['checks'] if c['id'] not in records and c['id'] not in('all',*stacks)]
    report['checks']=[c for c in report['checks'] if c not in report['historical_removed_checks']]
    report['retry_history']=report.get('retry_history',[])+report['failures']
    def replace(rid,kind,ok,detail):
        for c in report['checks']:
            if c['id']==rid and c['kind']==kind:c.update(passed=ok,details=detail[-4000:]);return
        report['checks'].append({'id':rid,'kind':kind,'passed':ok,'details':detail[-4000:]})
    def export(r,parent,name=None):
        d=parent/(name or r['id']);d.mkdir(parents=True,exist_ok=True)
        for a in r['assets']:
            if a['role']=='command':continue
            p=d/a['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(a['content'],encoding='utf8')
        return d
    env={**os.environ,'PYTHONPATH':str(CACHE/'python'),'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','PYTHONIOENCODING':'utf8','NEXT_TELEMETRY_DISABLED':'1'}
    (CACHE/'pytest.ini').write_text('[pytest]\n',encoding='utf8')
    # HTTP in loopback, senza rete esterna.
    rid='nodejs-progetto-api-locale-catalogo-prodotti';r=records[rid];d=export(r,CACHE/'retry','api')
    p=d/'src/server.mjs';p.write_text(p.read_text(encoding='utf8').replace('s.listen(3000,','s.listen(39080,'),encoding='utf8')
    proc=subprocess.Popen(['node','src/server.mjs'],cwd=d,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        data=None
        for _ in range(50):
            try:
                with urllib.request.urlopen('http://127.0.0.1:39080/products',timeout=1) as response:data=json.load(response)
                break
            except Exception:time.sleep(.1)
        assert data is not None and len(data)==2
        try:urllib.request.urlopen('http://127.0.0.1:39080/products/9');raise AssertionError('404 atteso')
        except urllib.error.HTTPError as e:assert e.code==404
        replace(rid,'node-api-http',True,'GET/products=200 con2prodotti e GET/products/9=404 su loopback39080, fuori dal blocco rete del sandbox.')
    except Exception as e:replace(rid,'node-api-http',False,str(e))
    finally:proc.terminate();proc.wait(timeout=10)
    # Percorso corto per non urtare MAX_PATH durante il prerender di Next.
    rid='nextjs-progetto-dashboard-server-con-ricerca-e-pagina';r=records[rid];d=export(r,CACHE/'next/p','dash')
    ok,out=run(['node',str(CACHE/'next/node_modules/next/dist/bin/next'),'build'],d,180,env)
    replace(rid,'next-build',ok,out)
    if ok:verification[rid]={'status':'compilato','date':'2026-10-29','details':'Build produzione Next16.4.3/React19.3 completata su Windows in percorso QA corto; nessuna pubblicazione remota.'}
    print('Retry Node e Next',ok,flush=True)
    # Test HTTP ASGI con versioni isolate e temp sotto workspace.
    for i,r in enumerate(x for x in records.values() if x['stack']=='fastapi' and(x['project'] or 'inizializzare-ambiente' in x['id'] or 'debug-test-e-produzione' in x['id'])):
        d=export(r,CACHE/'retry',f'fast{i}')
        if r['project'] or 'debug-test' in r['id']:
            args=[sys.executable,'-m','pytest','-q','-c',str(CACHE/'pytest.ini'),'--basetemp',str(d/'pytest-temp')]
        else:args=[sys.executable,'-c',"from fastapi.testclient import TestClient;from app import app;assert TestClient(app).get('/health').json()=={'ok':True};print('health200')"]
        ok,out=run(args,d,90,env)
        if r['project']:replace(r['id'],'fastapi-pytest',ok,out)
        else:
            for c in lifecycle['checks']:
                if c['id']==r['id'] and c['kind']=='fastapi-testclient':c.update(passed=ok,details=out[-4000:])
        if ok:verification[r['id']]={'status':'eseguito','date':'2026-10-29','details':'TestClient/pytest superati su FastAPI0.115.12,Pydantic2.11.7,Httpx0.28.1 isolati nella cache, Windows; SQLite temporaneo nei test del repository.'}
        print('Retry',r['id'],ok,flush=True)
    # Riconvalida sintassi delle fonti attuali e SQL modificato dopo il primo snapshot.
    syntax={'python':0,'json':0};js=[];static_bad=[]
    for r in records.values():
        for a in r['assets']:
            if a['role']=='command':continue
            try:
                if a['path'].endswith('.py'):ast.parse(a['content']);syntax['python']+=1
                if a['path'].endswith('.json'):json.loads(a['content']);syntax['json']+=1
            except Exception as e:static_bad.append({'id':r['id'],'path':a['path'],'error':str(e)})
            if a['path'].endswith(('.js','.mjs','.jsx')):js.append({'id':r['id'],'path':a['path'],'code':a['content']})
        if r['stack'] in('sql','sqlite') and not r['project']:
            with sqlite3.connect(':memory:') as db:
                for name in('fixture.sql','query.sql'):db.executescript(next(a['content'] for a in r['assets'] if a['path']==name))
    (CACHE/'js-sources-current.json').write_text(json.dumps(js),encoding='utf8')
    ok,out=run(['node',str(CACHE/'parse.cjs'),str(CACHE/'js-sources-current.json')],ROOT)
    replace('all','current-javascript-jsx-parse',ok,out);replace('all','current-python-json',not static_bad,json.dumps({'counts':syntax,'failures':static_bad}))
    # Lo smoke browser è già stato ripetuto dopo la correzione del capstone TSV.
    browser=json.loads((ROOT/'reports/web-browser-smoke.json').read_text(encoding='utf8'))
    for c in browser:
        rid=c['id'] if c['id']!='html-library' else 'html-css-progetto-biblioteca-responsive-con-filtri-locali'
        replace(rid,'browser-smoke',c['passed'],c['details'])
        if c['passed']:
            previous=verification.get(rid,{'status':'eseguito','date':'2026-10-29','details':''})
            previous['status']='eseguito';previous['details']+=' Smoke UI Chromium su localhost: ricerca/filtri, persistenza o importazione secondo il progetto; nessun errore JavaScript.';verification[rid]=previous
    for r in records.values():
        if r['id'] not in verification and r['stack'] in('nodejs','react','nextjs','fastapi','django') and not static_bad and ok:
            verification[r['id']]={'status':'statico','date':'2026-10-29','details':'Sintassi dei file Python o JavaScript/JSX e JSON controllata sulle fonti correnti; esecuzione di questa singola ricetta non attestata.'}
        if r['id'] in verification:
            if r['stack']=='nextjs' and 'Build produzione' in verification[r['id']]['details']:verification[r['id']]['status']='compilato'
            verification[r['id']]['files_sha256']={a['path']:hashlib.sha256((a['content'].rstrip()+'\n').encode()).hexdigest() for a in r['assets'] if a['role']!='command'}
    verification={rid:v for rid,v in verification.items() if rid in records}
    lifecycle['failures']=[c for c in lifecycle['checks'] if not c['passed']]
    report['lifecycle']=lifecycle
    report['failures']=[c for c in report['checks'] if not c['passed']]+lifecycle['failures']
    report['current_source_counts']=dict(__import__('collections').Counter(r['stack'] for r in records.values()))
    report['current_static']=dict(syntax,javascript_jsx=len(js))
    report['environment'].update({'node':'24.15.0','aspnet_sdk':'10.0.401','fastapi_test':'0.115.12','pydantic_test':'2.11.7','django_test':'5.2.6','sqlite':sqlite3.sqlite_version})
    report['summary']={'recipes':len(records),'projects':sum(r['project'] for r in records.values()),'checks':len(report['checks'])+len(lifecycle['checks']),'failures':len(report['failures']),'attested':len(verification)}
    (ROOT/'reports/web-database-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'reports/web-lifecycle-qa.json').write_text(json.dumps(lifecycle,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'tools/web_verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report['summary']),flush=True)
    for f in report['failures']:print(json.dumps(f,ensure_ascii=True),flush=True)

if __name__=='__main__':main()
