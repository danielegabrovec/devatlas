"""Thirty real Spring builds and isolated loopback checks, no external database."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from catalog_support import ROOT,DATE

WORK=ROOT/".cache/expansion-spring"
REPO=ROOT/".cache/expansion-frameworks/maven-repo"
SETTINGS=ROOT/".cache/expansion-frameworks/maven-settings.xml"
MVN=Path("C:/Tools/apache-maven-3.9.16/bin/mvn.cmd")
JAVA=Path("C:/Program Files/Eclipse Adoptium/jdk-21.0.12.101-hotspot/bin/java.exe")
NS={"m":"http://maven.apache.org/POM/4.0.0"}


def run(command,folder,timeout=240):
    started=time.perf_counter()
    try:
        result=subprocess.run([str(item) for item in command],cwd=folder,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout)
        return {"ok":result.returncode==0,"returncode":result.returncode,"seconds":round(time.perf_counter()-started,3),"command":[str(item) for item in command],"output":(result.stdout+result.stderr)[-12000:]}
    except Exception as error:return {"ok":False,"seconds":round(time.perf_counter()-started,3),"command":[str(item) for item in command],"output":str(error)}


def maven(*extra):
    return [str(MVN),"--no-transfer-progress","--settings",str(SETTINGS),"-Dmaven.repo.local="+str(REPO),"-q",*extra]


def prepare():
    WORK.mkdir(parents=True,exist_ok=True)
    records=[]
    for path in sorted((ROOT/"catalog/spring").glob("*/recipe.json")):
        data=json.loads(path.read_text(encoding="utf-8"));folder=WORK/data["id"];folder.mkdir(exist_ok=True)
        for asset in data["assets"]:
            if asset["role"]!="file":continue
            target=folder/asset["path"];assert target.resolve().is_relative_to(WORK.resolve())
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text((path.parent/asset["source"]).read_text(encoding="utf-8"),encoding="utf-8")
        original=(folder/"pom.xml").read_text(encoding="utf-8")
        assert original.count("<artifactId>spring-lab</artifactId>")==1
        ET.fromstring(original)
        (folder/"pom.xml").write_text(original.replace("<artifactId>spring-lab</artifactId>","<artifactId>"+data["id"]+"</artifactId>"),encoding="utf-8")
        records.append((data,path,folder))
    assert len(records)==30 and sum(data["project"] for data,_,_ in records)==1
    (WORK/"pom.xml").write_text('<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>it.atlas.qa</groupId><artifactId>spring-reactor</artifactId><version>1.0.0</version><packaging>pom</packaging><modules>'+''.join('<module>'+data['id']+'</module>' for data,_,_ in records)+'</modules></project>',encoding="utf-8")
    return records


def free_port():
    with socket.socket() as stream:stream.bind(("127.0.0.1",0));return stream.getsockname()[1]


def request(base,path,method="GET",payload=None,headers=None):
    data=json.dumps(payload).encode() if payload is not None else None
    actual_headers={"Content-Type":"application/json"} if data else {}
    actual_headers.update(headers or {})
    req=urllib.request.Request(base+path,data=data,method=method,headers=actual_headers)
    try:response=urllib.request.urlopen(req,timeout=10)
    except urllib.error.HTTPError as error:response=error
    with response:
        body=response.read().decode("utf-8")
        try:parsed=json.loads(body)
        except (json.JSONDecodeError,TypeError):parsed=body
        return response.status,dict(response.headers),parsed


def http_check(record,classpath):
    data,path,folder=record;rid=data['id'];key=rid.removeprefix('spring-');port=free_port();base=f"http://127.0.0.1:{port}"
    command=[str(JAVA),"-Xmx384m","-cp",str(folder/"target/classes")+os.pathsep+classpath,"it.atlas.Application",f"--server.port={port}","--server.address=127.0.0.1","--spring.main.banner-mode=off","--logging.level.root=WARN"]
    if key in {"profile","deploy"}:command.append("--spring.profiles.active=demo")
    if key=="value-config":command.append("--atlas.channel=qa")
    if key=="config-properties":command.append("--atlas.limit=37")
    log_path=folder/"http.log";started=time.perf_counter();checks=[]
    def check(label,condition):
        if not condition:raise AssertionError(label)
        checks.append(label)
    with log_path.open("w",encoding="utf-8") as log:
        process=subprocess.Popen(command,cwd=folder,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
        try:
            for _ in range(200):
                if process.poll() is not None:raise RuntimeError("ApplicationContext terminato prima delle richieste")
                try:
                    with socket.create_connection(("127.0.0.1",port),timeout=.1):break
                except OSError:time.sleep(.1)
            else:raise TimeoutError("Server non pronto entro20s")
            get=lambda route,**kwargs:request(base,route,**kwargs)
            if key in {"setup","build","debug","test","get"}:
                status,_,body=get('/hello');check('GET /hello:200 JSON',status==200 and body.get('message')=='Ciao Spring')
            elif key=='deploy':
                status,_,body=get('/channel');check('profilo demo property binding',status==200 and body.get('channel')=='didattico')
            elif key=='path-variable':
                status,_,body=get('/items/7');check('path numerico',status==200 and body.get('id')==7);check('path invalido:400',get('/items/bad')[0]==400)
            elif key=='request-param':
                status,_,body=get('/hello?name=Ada');check('query name',status==200 and body.get('message')=='Ciao Ada');check('default query',get('/hello')[2].get('message')=='Ciao Ospite')
            elif key=='body':
                payload={'title':'demo','quantity':2};status,_,body=get('/items',method='POST',payload=payload);check('record JSON roundtrip',status==200 and body==payload)
            elif key=='created':
                status,headers,body=get('/items',method='POST',payload={'id':77,'title':'demo'});check('201 Location/body',status==201 and headers.get('Location')=='/items/1' and body.get('id')==1 and body.get('title')=='demo')
            elif key=='header':
                status,_,body=get('/language',headers={'X-Language':'fr'});check('header personalizzato',status==200 and body.get('language')=='fr');check('header default',get('/language')[2].get('language')=='it')
            elif key=='cookie':
                status,_,body=get('/theme',headers={'Cookie':'theme=dark'});check('cookie facoltativo',status==200 and body.get('theme')=='dark');check('cookie default',get('/theme')[2].get('theme')=='light')
            elif key=='validation':
                check('DTO valido',get('/items',method='POST',payload={'title':'ok','quantity':1})[0]==200);check('Bean Validation:400',get('/items',method='POST',payload={'title':'','quantity':0})[0]==400)
            elif key=='problem-detail':
                status,headers,body=get('/problem');check('409 ProblemDetail',status==409 and body.get('title')=='Prenotazione rifiutata' and body.get('detail')=='Stock insufficiente');check('content-type problema','application/problem+json' in headers.get('Content-Type',''))
            elif key=='advice':
                status,_,body=get('/failure');check('advice400',status==400 and body.get('detail')=='Dato non valido')
            elif key=='pagination':
                check('pagina Grace',get('/people?offset=1&limit=1')[2]==['Grace']);check('offset negativo400',get('/people?offset=-1')[0]==400);check('limite eccessivo400',get('/people?limit=101')[0]==400);check('pagina oltre fine vuota',get('/people?offset=99')[2]==[])
            elif key=='not-found':
                check('presente200',get('/items/1')[0]==200);check('assente404',get('/items/2')[0]==404)
            elif key=='media-type':
                status,headers,body=get('/plain');check('text/plain UTF8',status==200 and 'text/plain' in headers.get('Content-Type','') and 'città' in body)
            elif key=='value-config':check('Value override',get('/channel')[2].get('channel')=='qa')
            elif key=='profile':check('profilo attivo',get('/channel')[2]=='didattico')
            elif key=='config-properties':check('ConfigurationProperties binding',get('/options')[2].get('limit')==37)
            elif key=='constructor-di':check('servizio iniettato',get('/hello')[2].get('message')=='Ciao Ada')
            elif key=='qualifier':check('Qualifier risolve bean',get('/channel')[2]=='demo')
            elif key=='cache-control':check('Cache-Control', 'max-age=60' in get('/info')[1].get('Cache-Control',''))
            elif key=='cors-local':
                status,headers,_=get('/info',headers={'Origin':'http://127.0.0.1:5173'});check('CORS origine permessa',status==200 and headers.get('Access-Control-Allow-Origin')=='http://127.0.0.1:5173');check('CORS altra origine respinta',get('/info',headers={'Origin':'http://example.invalid'})[0]==403)
            elif key=='filter':check('filtro header',get('/info')[1].get('X-Lab')=='atlas')
            elif key=='interceptor':check('interceptor header',get('/info')[1].get('X-Controller-Path')=='/info')
            elif key=='async-response':check('CompletableFuture response',get('/async')[2].get('answer')==42)
            elif key=='jdbc-transaction':
                check('stock8->6',get('/reserve?n=2',method='POST')[2].get('qty')==6);check('quantita0:400',get('/reserve?n=0',method='POST')[0]==400);check('oltrestock:409',get('/reserve?n=999',method='POST')[0]==409);check('fallimento non altera stock',get('/reserve?n=6',method='POST')[2].get('qty')==0)
            elif key=='progetto-attivita':
                check('lista iniziale vuota',get('/tasks')[2]==[])
                status,headers,body=get('/tasks',method='POST',payload={'title':' prima '});check('creazione201 trim/id',status==201 and body.get('id')==1 and body.get('title')=='prima' and headers.get('Location')=='/tasks/1')
                check('secondo ID',get('/tasks',method='POST',payload={'title':'seconda'})[2].get('id')==2)
                check('input vuoto400',get('/tasks',method='POST',payload={'title':''})[0]==400)
                def add(n):return get('/tasks',method='POST',payload={'title':f'parallela{n}'})
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:parallel=list(pool.map(add,range(12)))
                check('12 ID concorrenti distinti',all(row[0]==201 for row in parallel) and len({row[2]['id'] for row in parallel})==12)
                check('lista14 dopo richieste parallele',len(get('/tasks')[2])==14)
            else:raise AssertionError('Caso HTTP non mappato: '+key)
            result={'id':rid,'ok':True,'checks':checks,'command':command}
        except Exception as error:result={'id':rid,'ok':False,'checks':checks,'output':str(error),'command':command}
        finally:
            process.terminate()
            try:process.wait(timeout=8)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=3)
    result['seconds']=round(time.perf_counter()-started,3)
    if not result['ok']:result['server_log']=log_path.read_text(encoding='utf-8',errors='replace')[-10000:]
    print('HTTP',rid,result['ok'],flush=True)
    return result


def main():
    records=prepare()
    report={'date':DATE,'platform':'Windows x64','version':'Spring Boot4.1.2, Maven3.9.16, JDK21.0.12.1, target21','recipes':30,'projects':1,'limits':['Maven repository/settings solo in .cache; nessun database esterno.','ArtifactId resi unici soltanto nei POM di cache per compilare i30progetti nello stesso reactor; i POM canonici restano invariati.','Sessione interattiva JDWP e hosting esterno non attestati.']}
    build=run(maven('-T2','--fail-at-end','test'),WORK)
    report['maven_reactor']=build
    compile_records=[]
    for data,path,folder in records:
        sources=list((folder/'src/main/java').rglob('*.java'))
        classes=[folder/'target/classes'/source.relative_to(folder/'src/main/java').with_suffix('.class') for source in sources]
        tests=[]
        for xml in (folder/'target/surefire-reports').glob('TEST-*.xml'):
            suite=ET.parse(xml).getroot();tests.append({'name':suite.attrib.get('name'),'tests':int(suite.attrib.get('tests',0)),'failures':int(suite.attrib.get('failures',0)),'errors':int(suite.attrib.get('errors',0))})
        compile_records.append({'id':data['id'],'ok':build['ok'] and all(item.exists() for item in classes),'java_sources':len(sources),'classes':len(classes),'junit':tests})
    report['compilation']=compile_records
    if not build['ok']:
        report['failures']=[{'stage':'maven','output':build['output']}]
        (ROOT/'reports/expansion-spring-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(build['output']);raise SystemExit(1)
    classpaths={}
    for key in ('get','jdbc-transaction'):
        output=WORK/(key+'.classpath')
        result=run(maven('-f',str(WORK/('spring-'+key)/'pom.xml'),'dependency:build-classpath','-Dmdep.outputFile='+str(output)),WORK)
        if not result['ok']:raise RuntimeError(result['output'])
        classpaths[key]=output.read_text(encoding='utf-8').strip()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        http=list(pool.map(lambda record:http_check(record,classpaths['jdbc-transaction' if record[0]['id']=='spring-jdbc-transaction' else 'get']),records))
    report['http']=http
    report['summary']={'compiled':sum(item['ok'] for item in compile_records),'http_passed':sum(item['ok'] for item in http),'http_assertions':sum(len(item['checks']) for item in http),'junit_tests':sum(suite['tests'] for item in compile_records for suite in item['junit']),'junit_failures':sum(suite['failures']+suite['errors'] for item in compile_records for suite in item['junit'])}
    report['failures']=[item for item in compile_records+http if not item['ok']]
    (ROOT/'reports/expansion-spring-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report['summary']),flush=True)
    if report['failures']:raise SystemExit(1)
    manifest={}
    for data,path,folder in records:
        data['verification']={'status':'eseguito','date':DATE,'details':'Compilazione Maven reale e richieste HTTP su loopback/Windows, Spring Boot4.1.2, JDK21.0.12.1. '+('Test JUnit del capstone superati, inclusi snapshot e ID;12POST concorrenti con ID distinti. ' if data['project'] else '')+'Report: reports/expansion-spring-qa.json. Sessioni JDWP interattive, hosting esterno e altri OS non attestati.'}
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        manifest[data['id']]={'hashes':{asset['id']:asset['sha256'] for asset in data['assets']},'verification':data['verification']}
    (ROOT/'tools/expansion-spring-verification.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':main()
