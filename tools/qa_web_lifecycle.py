"""Verifiche mirate sulle14guide lifecycle aggiunte dopo l'audit iniziale."""
import ast,json,os,subprocess,sys
from pathlib import Path
from qa_web_database import ROOT,CACHE,export,run

def main():
    records=[];checks=[];verified={}
    def record(r,kind,ok,out=''):
        checks.append({'id':r['id'],'kind':kind,'passed':ok,'details':out[-4000:]})
        print(r['id'],kind,ok,flush=True)
    for stack in ['nodejs','react','nextjs','aspnet','fastapi','html-css','django']:
        for key in ['inizializzare-ambiente-e-progetto-','debug-test-e-produzione-']:
            p=ROOT/'catalog'/stack/(stack+'-'+key+stack)/'recipe.json'
            r=json.loads(p.read_text(encoding='utf8'))
            for a in r['assets']:a['content']=(p.parent/a['source']).read_text(encoding='utf8')
            records.append(r)
    env={**os.environ,'PYTHONPATH':str(CACHE/'python'),'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','NEXT_TELEMETRY_DISABLED':'1'}
    for r in records:
        errors=[]
        for a in r['assets']:
            if a['role']=='command':continue
            try:
                if a['path'].endswith('.py'):ast.parse(a['content'])
                if a['path'].endswith('.json'):json.loads(a['content'])
            except Exception as e:errors.append(str(e))
        record(r,'static-files',not errors,';'.join(errors))
        stack=r['stack'];isdebug='debug-test' in r['id']
        parent=CACHE/('node' if stack=='react' else 'next' if stack=='nextjs' else 'lifecycle')/'lifecycle'
        dest=export(r,parent)
        results=[]
        if stack in ('nodejs','html-css'):
            args=['node','--test'] if isdebug else ['node','src/main.mjs'] if stack=='nodejs' else ['node','--check','app.js']
            ok,out=run(args,dest);record(r,'node-test-or-check',ok,out);results.append(ok)
        if stack=='react':
            ok,out=run(['node',str(CACHE/'node/node_modules/vite/bin/vite.js'),'build'],dest);record(r,'vite-build',ok,out);results.append(ok)
            if isdebug:
                ok,out=run(['node','--test'],dest);record(r,'node-tests',ok,out);results.append(ok)
        if stack=='nextjs':
            ok,out=run(['node',str(CACHE/'next/node_modules/next/dist/bin/next'),'build'],dest,180,env);record(r,'next-build',ok,out);results.append(ok)
            if isdebug:
                ok,out=run(['node','--test'],dest);record(r,'node-tests',ok,out);results.append(ok)
        if stack=='aspnet':
            (dest/'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>',encoding='utf8')
            ok,out=run(['dotnet','build','Demo.csproj','--nologo','--verbosity','quiet'],dest,120,env);record(r,'dotnet-build',ok,out);results.append(ok)
            if isdebug:
                ok,out=run(['dotnet','run','--project','tests/Checks.csproj'],dest,120,env);record(r,'dotnet-tests',ok,out);results.append(ok)
        if stack=='fastapi':
            args=[sys.executable,'-m','pytest','-q'] if isdebug else [sys.executable,'-c',"from fastapi.testclient import TestClient;from app import app;assert TestClient(app).get('/health').json()=={'ok':True};print('health200')"]
            ok,out=run(args,dest,90,env);record(r,'fastapi-testclient',ok,out);results.append(ok)
        if stack=='django':
            ok,out=run([sys.executable,'manage.py','check'],dest,90,env);record(r,'django-check',ok,out);results.append(ok)
            if isdebug:
                ok,out=run([sys.executable,'manage.py','test','notes'],dest,90,env);record(r,'django-tests',ok,out);results.append(ok)
        if not errors and results and all(results):
            verified[r['id']]={'status':'compilato' if stack in('react','nextjs','aspnet') else 'statico' if stack=='html-css' and not isdebug else 'eseguito','date':'2026-10-29','details':'Verifiche lifecycle su Windows: '+', '.join(c['kind'] for c in checks if c['id']==r['id'])+'. Configurazione debugger controllata come JSON; sessione F5 e distribuzione remota non attestate.'}
    report={'date':'2026-10-29','recipes':len(records),'checks':checks,'failures':[c for c in checks if not c['passed']],'limits':['Breakpoint VSCode configurati ma nessuna sessione F5 attestata.','Processi di produzione descritti; nessuna distribuzione pubblica.','Django check --deploy segnala intenzionalmente la configurazione locale da sostituire.']}
    (ROOT/'reports/web-lifecycle-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    (CACHE/'lifecycle-verification.json').write_text(json.dumps(verified,ensure_ascii=False,indent=2),encoding='utf8')
    print('Lifecycle failures',len(report['failures']),flush=True)

if __name__=='__main__':main()
