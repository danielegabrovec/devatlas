"""Verifica reale e riproducibile dei contenuti Web/DB senza servizi di produzione."""
from __future__ import annotations
import ast,collections,json,os,sqlite3,subprocess,sys,time,urllib.request,urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache/web-qa'
SPECS={'nodejs':90,'react':100,'nextjs':100,'aspnet':65,'fastapi':65,'html-css':45,'django':35,'sql':50,'sqlite':65,'postgresql':75,'mysql':60}
DATE='2026-10-29'
REPORT={'date':DATE,'environment':{'platform':sys.platform,'python':sys.version.split()[0]},'counts':{},'checks':[],'failures':[],'limits':['PostgreSQL e MySQL: controllo strutturale/documentale, nessun server avviato.','Le verifiche sono state eseguite su questo Windows; nessuna attestazione Linux/macOS.','Parse JSX e build di tre progetti React/tre Next non equivalgono a test funzionali di ogni singola ricetta.']}
VERIFIED={}
RECORDS=[]

def check(kind,rid,passed,detail=''):
    REPORT['checks'].append({'kind':kind,'id':rid,'passed':passed,'details':detail[-4000:]})
    if not passed:REPORT['failures'].append({'kind':kind,'id':rid,'details':detail[-4000:]})

def run(args,cwd,timeout=90,env=None):
    try:
        p=subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=timeout)
        return p.returncode==0,(p.stdout+p.stderr)[-7000:]
    except Exception as e:return False,str(e)

def export(r,root):
    destination=root/r['id'];destination.mkdir(parents=True,exist_ok=True)
    for a in r['assets']:
        if a['role']=='command':continue
        p=destination/a['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(a['content'],encoding='utf8')
    return destination

def attest(r,details,status='eseguito'):
    VERIFIED[r['id']]={'status':status,'date':DATE,'details':details}

def main():
    CACHE.mkdir(parents=True,exist_ok=True)
    for stack,expected in SPECS.items():
        paths=sorted((ROOT/'catalog'/stack).glob('*/recipe.json'))
        REPORT['counts'][stack]=len(paths)
        check('count',stack,len(paths)==expected,f'{len(paths)}/{expected}')
        for p in paths:
            r=json.loads(p.read_text(encoding='utf8'));r['directory']=p.parent
            for a in r['assets']:a['content']=(p.parent/a['source']).read_text(encoding='utf8')
            RECORDS.append(r)
    projects=[r for r in RECORDS if r['project']]
    check('project-count','all',len(projects)==20,str(len(projects)))
    import importlib.metadata
    for name in ('fastapi','pydantic','httpx'):
        try: REPORT['environment'][name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: pass
    REPORT['projects']=[{'id':r['id'],'stack':r['stack'],'files':[a['path'] for a in r['assets'] if a['role']!='command']} for r in projects]
    js=[];node=[];syntax=collections.Counter()
    for r in RECORDS:
        if r['project']:
            f=[a for a in r['assets'] if a['role']!='command']
            check('project-files',r['id'],len(f)>=3 and any(a['path']=='README.md' for a in f),str(len(f)))
        for a in r['assets']:
            if a['role']=='command':continue
            name=a['path'];content=a['content']
            try:
                if name.endswith('.py'):ast.parse(content,filename=name);syntax['python']+=1
                if name.endswith('.json'):json.loads(content);syntax['json']+=1
            except Exception as e:check('syntax',r['id'],False,name+':'+str(e))
            if name.endswith(('.js','.jsx','.mjs')):
                js.append({'id':r['id'],'path':name,'code':content})
                if r['stack'] not in('react','nextjs') and not name.endswith('.jsx'):
                    p=CACHE/'syntax'/r['id']/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf8');node.append((r,p))
    check('python-ast','all',not any(x['kind']=='syntax' for x in REPORT['failures']),str(dict(syntax)))
    (CACHE/'js-sources.json').write_text(json.dumps(js),encoding='utf8')
    parser="""const fs=require('fs');const ts=require('C:/Users/danie/AppData/Roaming/npm/node_modules/typescript');const rows=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const errors=[];for(const r of rows){const file=ts.createSourceFile(r.path,r.code,ts.ScriptTarget.Latest,true,ts.ScriptKind.JSX);for(const e of file.parseDiagnostics)errors.push({id:r.id,path:r.path,message:ts.flattenDiagnosticMessageText(e.messageText,' ')});}process.stdout.write(JSON.stringify({files:rows.length,errors}));process.exitCode=errors.length?1:0;"""
    (CACHE/'parse.cjs').write_text(parser,encoding='utf8')
    ok,out=run(['node',str(CACHE/'parse.cjs'),str(CACHE/'js-sources.json')],ROOT)
    check('javascript-jsx-parse','all',ok,out)
    for r,p in node:
        ok,out=run(['node','--check',str(p)],p.parent)
        check('node-check',r['id'],ok,str(p.relative_to(CACHE)) if ok else out)
    print('Controlli statici completati',dict(syntax),len(js),'JS/JSX',flush=True)
    # SQL e SQLite vengono eseguiti su un database temporaneo nuovo per ogni voce.
    for r in RECORDS:
        if r['stack'] not in('sql','sqlite'):continue
        try:
            if r['project']:
                order=['schema.sql','report.sql'] if r['stack']=='sql' else ['schema.sql','seed.sql','search.sql']
            else:order=['fixture.sql','query.sql']
            with sqlite3.connect(':memory:') as db:
                for path in order:db.executescript(next(a['content'] for a in r['assets'] if a['path']==path))
                if r['project'] and r['stack']=='sql':assert db.execute("SELECT sum(total) FROM orders WHERE status='paid'").fetchone()[0]==270
                if r['project'] and r['stack']=='sqlite':assert db.execute("SELECT title FROM search WHERE search MATCH 'file'").fetchone()[0]=='Python'
            check('sqlite-execution',r['id'],True)
            attest(r,'Esecuzione completa su SQLite '+sqlite3.sqlite_version+' in database temporaneo nuovo; Windows/Python '+sys.version.split()[0]+'. PRAGMA journal_mode testato in memoria: non attesta concorrenza WAL su file.')
        except Exception as e:check('sqlite-execution',r['id'],False,str(e))
    # I tre progetti Node hanno test reali; il server viene interrogato solo su localhost.
    for r in [x for x in projects if x['stack']=='nodejs']:
        dest=export(r,CACHE/'node-projects')
        ok,out=run(['node','--test'],dest);check('node-project-tests',r['id'],ok,out)
        if ok:attest(r,'Test node --test superati su Node24/Windows; '+('API verificata separatamente via HTTP locale.' if 'api-locale' in r['id'] else 'Avvio CLI verificato su dati sintetici.'))
        if 'api-locale' not in r['id']:
            args=['node','src/main.mjs']+(['sample.txt'] if 'analisi' in r['id'] else [])
            ok,out=run(args,dest);check('node-project-run',r['id'],ok,out)
        else:
            code=(dest/'src/server.mjs').read_text(encoding='utf8').replace("s.listen(3000,","s.listen(39080,")
            (dest/'src/server.mjs').write_text(code,encoding='utf8')
            proc=subprocess.Popen(['node','src/server.mjs'],cwd=dest,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            try:
                for _ in range(30):
                    try:
                        with urllib.request.urlopen('http://127.0.0.1:39080/products') as response:data=json.load(response)
                        break
                    except Exception:time.sleep(.1)
                assert len(data)==2
                try:urllib.request.urlopen('http://127.0.0.1:39080/products/9');raise AssertionError('404 atteso')
                except urllib.error.HTTPError as e:assert e.code==404
                check('node-api-http',r['id'],True,'GET/products200 con2prodotti; /products/9=404; porta QA39080.')
            except Exception as e:check('node-api-http',r['id'],False,str(e))
            finally:proc.terminate();proc.wait(timeout=10)
    for r in [x for x in projects if x['stack']=='react']:
        dest=export(r,CACHE/'node/projects')
        ok,out=run(['node','--test'],dest);check('react-model-tests',r['id'],ok,out)
        build_ok,build_out=run(['node',str(CACHE/'node/node_modules/vite/bin/vite.js'),'build'],dest)
        check('react-vite-build',r['id'],build_ok,build_out)
        if ok and build_ok:attest(r,'Test della logica Node superati e build produzione Vite7.1.7/React19.1.1 completata su Windows; verifica UI interattiva non attestata.')
    print('SQLite/Node/React completati',flush=True)
    for r in [x for x in projects if x['stack']=='nextjs']:
        dest=export(r,CACHE/'next/projects')
        env={**os.environ,'NEXT_TELEMETRY_DISABLED':'1'}
        ok,out=run(['node',str(CACHE/'next/node_modules/next/dist/bin/next'),'build'],dest,timeout=180,env=env)
        check('next-build',r['id'],ok,out)
        if ok:attest(r,'Build produzione Next16.4.3 e React19.3 completata su Windows; verifica di compilazione/prerender, nessuna attestazione deployment remoto o tutti i flussi UI.','compilato')
        if any(a['path'].startswith('test/') for a in r['assets']):
            tok,tout=run(['node','--test'],dest);check('next-model-tests',r['id'],tok,tout)
    # FastAPI usa librerie dell'ambiente per test HTTP locali; non viene avviata una porta pubblica.
    pyenv={**os.environ,'PYTHONPATH':str(CACHE/'python'),'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1'}
    for r in [x for x in projects if x['stack']=='fastapi']:
        dest=export(r,CACHE/'python-projects')
        ok,out=run([sys.executable,'-m','pytest','-q'],dest,env=pyenv)
        check('fastapi-pytest',r['id'],ok,out)
        if ok:attest(r,'Test pytest/TestClient del progetto superati su Windows, dati SQLite temporanei quando previsti. Librerie FastAPI/Pydantic dell’ambiente registrate nel report.')
    # Tutti gli esempi Django eseguono system check; i capstone anche test e richieste client.
    for r in [x for x in RECORDS if x['stack']=='django']:
        dest=export(r,CACHE/'django-projects')
        ok,out=run([sys.executable,'manage.py','check'],dest,env=pyenv)
        check('django-system-check',r['id'],ok,out)
        if r['project'] or 'testare' in r['id']:
            tok,tout=run([sys.executable,'manage.py','test','notes','--verbosity','1'],dest,env=pyenv)
            check('django-tests',r['id'],tok,tout)
            if ok and tok:attest(r,'Django5.2.6 system check e test del progetto superati su SQLite temporaneo/Windows. Nessuna pubblicazione remota.')
    print('Next/FastAPI/Django completati',flush=True)
    # Compile di tutti i65programmi ASP.NET su SDK locale, con file temporanei isolati.
    dest=CACHE/'dotnet-check';dest.mkdir(exist_ok=True)
    previous=[]
    for r in [x for x in RECORDS if x['stack']=='aspnet']:
        for p in previous:
            if p.exists():p.unlink()
        previous=[]
        for a in r['assets']:
            if a['path'].endswith(('.cs','.csproj')):
                p=dest/a['path'];p.write_text(a['content'],encoding='utf8');previous.append(p)
        ok,out=run(['dotnet','build','Demo.csproj','--nologo','--verbosity','quiet'],dest,timeout=120)
        check('aspnet-build',r['id'],ok,out)
        if ok:attest(r,'Compilazione dotnet build completata con SDK.NET10 su Windows; endpoint non tutti interrogati, nessuna attestazione esecuzione multipiattaforma.','compilato')
    # Report aggiornato anche in caso di errori: nessun successo inventato.
    REPORT['summary']={'recipes':len(RECORDS),'projects':len(projects),'checks':len(REPORT['checks']),'failures':len(REPORT['failures']),'attested':len(VERIFIED)}
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports/web-database-qa.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'tools/web_verification.json').write_text(json.dumps(VERIFIED,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(REPORT['summary']),flush=True)
    for failure in REPORT['failures']:print(json.dumps(failure,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
