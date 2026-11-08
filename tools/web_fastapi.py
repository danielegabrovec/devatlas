from catalog_support import Book
from web_support import add

PRE="""from typing import Annotated, Literal
from enum import Enum
from uuid import UUID
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path as FilePath
import asyncio, json, os, secrets, time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Path, Body, Header, Cookie, Response, HTTPException, Depends, Request, APIRouter, BackgroundTasks, File, UploadFile, Form
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse, RedirectResponse, StreamingResponse, FileResponse
from pydantic import BaseModel, Field, ConfigDict, field_validator
app = FastAPI(title='Laboratorio')
"""
REQ='fastapi==0.115.12\nuvicorn==0.34.3\npydantic==2.11.7\npython-multipart==0.0.20\nhttpx==0.28.1\npytest==8.4.1\n'
ROWS=[
("Definire endpoint GET JSON","@app.get('/demo')\ndef demo():\n    return {'ok': True}\n"),
("Convertire un parametro percorso intero","@app.get('/items/{item_id}')\ndef item(item_id: int):\n    return {'id': item_id}\n"),
("Limitare intervallo del parametro percorso","@app.get('/items/{item_id}')\ndef item(item_id: Annotated[int, Path(ge=1, le=1000)]):\n    return {'id': item_id}\n"),
("Usare enum per un parametro percorso","class Size(str, Enum):\n    small='small'\n    large='large'\n@app.get('/sizes/{size}')\ndef size(size: Size):\n    return {'size': size.value}\n"),
("Vincolare query a valori Literal","@app.get('/demo')\ndef demo(sort: Literal['name','price']='name'):\n    return {'sort': sort}\n"),
("Gestire query opzionale","@app.get('/demo')\ndef demo(q: str | None=None):\n    return {'query': q}\n"),
("Validare lunghezza e pattern di ricerca","@app.get('/demo')\ndef demo(q: Annotated[str, Query(min_length=2,max_length=30,pattern='^[a-zA-Z ]+$')]):\n    return {'query': q}\n"),
("Leggere query ripetute come lista","@app.get('/demo')\ndef demo(tag: Annotated[list[str], Query()]=[]):\n    return {'tags': tag}\n"),
("Convertire flag booleano da query","@app.get('/demo')\ndef demo(active: bool=False):\n    return {'active': active}\n"),
("Mappare un alias di query","@app.get('/demo')\ndef demo(page_size: Annotated[int, Query(alias='page-size',ge=1,le=100)]=20):\n    return {'size': page_size}\n"),
("Documentare query deprecata","@app.get('/demo')\ndef demo(old: Annotated[str | None, Query(deprecated=True)]=None):\n    return {'old': old}\n"),
("Validare UUID nel percorso","@app.get('/items/{item_id}')\ndef demo(item_id: UUID):\n    return {'id': item_id}\n"),
("Validare una data ISO","@app.get('/demo')\ndef demo(day: date):\n    return {'day': day}\n"),
("Leggere header con nome esplicito","@app.get('/demo')\ndef demo(request_id: Annotated[str | None, Header(alias='X-Request-ID')]=None):\n    return {'request_id': request_id}\n"),
("Leggere header ripetuti","@app.get('/demo')\ndef demo(x_tag: Annotated[list[str] | None, Header()]=None):\n    return {'tags': x_tag or []}\n"),
("Leggere un cookie facoltativo","@app.get('/demo')\ndef demo(theme: Annotated[str | None, Cookie()]=None):\n    return {'theme': theme or 'light'}\n"),
("Validare un body con modello Pydantic","class Item(BaseModel):\n    name: str\n    price: Annotated[Decimal, Field(ge=0)]\n@app.post('/items')\ndef create(item: Item):\n    return item\n"),
("Validare modelli annidati","class Address(BaseModel):\n    city: str\nclass Person(BaseModel):\n    name: str\n    address: Address\n@app.post('/people')\ndef create(person: Person):\n    return person\n"),
("Accettare una lista di modelli","class Row(BaseModel):\n    id: int\n    name: str\n@app.post('/batch')\ndef batch(rows: list[Row]):\n    return {'count': len(rows)}\n"),
("Normalizzare un campo con field_validator","class Item(BaseModel):\n    name: str\n    @field_validator('name')\n    @classmethod\n    def clean(cls,v):\n        v=v.strip()\n        if not v: raise ValueError('nome vuoto')\n        return v\n@app.post('/items')\ndef create(item: Item):\n    return item\n"),
("Rifiutare campi extra nel body","class Item(BaseModel):\n    model_config=ConfigDict(extra='forbid')\n    name: str\n@app.post('/items')\ndef create(item: Item):\n    return item\n"),
("Limitare lunghezze e quantità nel modello","class Item(BaseModel):\n    name: str=Field(min_length=1,max_length=80)\n    quantity: int=Field(ge=1,le=100)\n@app.post('/items')\ndef create(item: Item):\n    return item\n"),
("Fornire esempi nello schema OpenAPI","class Item(BaseModel):\n    name: str=Field(examples=['Tastiera'])\n    price: float=Field(ge=0,examples=[50])\n@app.post('/items')\ndef create(item: Item):\n    return item\n"),
("Separare modello interno e risposta pubblica","class Public(BaseModel):\n    name: str\n@app.get('/demo',response_model=Public)\ndef demo():\n    return {'name':'Ada','internal_secret':'non esposto'}\n"),
("Escludere valori non impostati dalla risposta","class Item(BaseModel):\n    name: str\n    note: str | None=None\n@app.get('/demo',response_model=Item,response_model_exclude_unset=True)\ndef demo():\n    return {'name':'Tastiera'}\n"),
("Restituire status201 con Location","@app.post('/items',status_code=201)\ndef create(response: Response):\n    response.headers['Location']='/items/1'\n    return {'id':1}\n"),
("Restituire204 senza contenuto","@app.delete('/items/{item_id}',status_code=204)\ndef remove(item_id: int):\n    return Response(status_code=204)\n"),
("Generare errore404 strutturato","@app.get('/items/{item_id}')\ndef item(item_id: int):\n    if item_id!=1: raise HTTPException(404,detail='Elemento assente')\n    return {'id':1}\n"),
("Gestire eccezione di dominio","class DomainError(Exception):\n    pass\n@app.exception_handler(DomainError)\nasync def handle(request: Request,error: DomainError):\n    return JSONResponse(status_code=409,content={'error':str(error)})\n@app.get('/demo')\ndef demo():\n    raise DomainError('Operazione in conflitto')\n"),
("Riutilizzare una dipendenza di paginazione","def pagination(skip: int=0,limit: Annotated[int,Query(ge=1,le=100)]=20):\n    return {'skip':max(skip,0),'limit':limit}\n@app.get('/demo')\ndef demo(page: Annotated[dict,Depends(pagination)]):\n    return page\n"),
("Rilasciare risorse con dipendenza yield","def resource():\n    handle={'open':True}\n    try: yield handle\n    finally: handle['open']=False\n@app.get('/demo')\ndef demo(handle: Annotated[dict,Depends(resource)]):\n    return {'open':handle['open']}\n"),
("Comporre sottodipendenze","def language(accept_language: Annotated[str,Header()]='it'):\n    return accept_language.split(',')[0]\ndef greeting(lang: Annotated[str,Depends(language)]):\n    return 'Ciao' if lang.startswith('it') else 'Hello'\n@app.get('/demo')\ndef demo(message: Annotated[str,Depends(greeting)]):\n    return {'message':message}\n"),
("Verificare una API key da ambiente","def authorize(x_api_key: Annotated[str,Header()]):\n    expected=os.environ.get('DEMO_API_KEY')\n    if not expected: raise HTTPException(503,'Configurare DEMO_API_KEY')\n    if not secrets.compare_digest(x_api_key,expected): raise HTTPException(403,'Chiave invalida')\n@app.get('/demo',dependencies=[Depends(authorize)])\ndef demo():\n    return {'ok':True}\n"),
("Organizzare API tramite APIRouter","router=APIRouter(prefix='/v1',tags=['catalogo'])\n@router.get('/items')\ndef items():\n    return [{'id':1}]\napp.include_router(router)\n"),
("Applicare dipendenza a tutte le rotte router","def valid_header(x_client: Annotated[str,Header()]):\n    if x_client!='atlas': raise HTTPException(400,'X-Client richiesto')\nrouter=APIRouter(prefix='/v1',dependencies=[Depends(valid_header)])\n@router.get('/demo')\ndef demo():\n    return {'ok':True}\napp.include_router(router)\n"),
("Configurare CORS con origine precisa","from fastapi.middleware.cors import CORSMiddleware\napp.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173'],allow_methods=['GET','POST'],allow_headers=['Content-Type'])\n@app.get('/demo')\ndef demo():\n    return {'ok':True}\n"),
("Rifiutare Host inattesi","from fastapi.middleware.trustedhost import TrustedHostMiddleware\napp.add_middleware(TrustedHostMiddleware,allowed_hosts=['localhost','127.0.0.1','testserver'])\n@app.get('/demo')\ndef demo():\n    return {'ok':True}\n"),
("Comprimere risposte grandi con GZip","from fastapi.middleware.gzip import GZipMiddleware\napp.add_middleware(GZipMiddleware,minimum_size=500)\n@app.get('/demo')\ndef demo():\n    return {'text':'esempio '*1000}\n"),
("Aggiungere middleware tempo richiesta","@app.middleware('http')\nasync def timing(request: Request,call_next):\n    start=time.perf_counter()\n    response=await call_next(request)\n    response.headers['X-Process-Time']=str(time.perf_counter()-start)\n    return response\n@app.get('/demo')\ndef demo():\n    return {'ok':True}\n"),
("Propagare request ID tramite middleware","@app.middleware('http')\nasync def request_id(request: Request,call_next):\n    from uuid import uuid4\n    request.state.request_id=str(uuid4())\n    response=await call_next(request)\n    response.headers['X-Request-ID']=request.state.request_id\n    return response\n@app.get('/demo')\ndef demo(request: Request):\n    return {'id':request.state.request_id}\n"),
("Eseguire attività breve dopo la risposta","def record(message):\n    with open('events.log','a',encoding='utf8') as f: f.write(message+'\\n')\n@app.post('/demo',status_code=202)\ndef demo(tasks: BackgroundTasks):\n    tasks.add_task(record,'evento didattico')\n    return {'queued':True}\n"),
("Caricare risorse nel lifespan","@asynccontextmanager\nasync def lifespan(app):\n    app.state.catalog=['Python','SQL']\n    yield\n    app.state.catalog=[]\napp=FastAPI(lifespan=lifespan)\n@app.get('/demo')\ndef demo():\n    return app.state.catalog\n"),
("Accettare un form HTML","@app.post('/demo')\ndef demo(name: Annotated[str,Form(min_length=1)]):\n    return {'name':name}\n"),
("Leggere metadati upload multipart","@app.post('/upload')\nasync def upload(file: UploadFile):\n    try: return {'name':file.filename,'type':file.content_type}\n    finally: await file.close()\n"),
("Limitare dimensione upload leggendo chunk","@app.post('/upload')\nasync def upload(file: UploadFile):\n    size=0\n    try:\n        while chunk:=await file.read(65536):\n            size+=len(chunk)\n            if size>1048576: raise HTTPException(413,'Massimo1MiB')\n        return {'bytes':size}\n    finally: await file.close()\n"),
("Accettare file e campo form insieme","@app.post('/upload')\nasync def upload(label: Annotated[str,Form()],file: UploadFile):\n    try: return {'label':label,'name':file.filename}\n    finally: await file.close()\n"),
("Restituire HTML esplicito","@app.get('/demo',response_class=HTMLResponse)\ndef demo():\n    return '<!doctype html><html lang=\"it\"><title>Demo</title><h1>Ciao</h1></html>'\n"),
("Restituire testo semplice","@app.get('/demo',response_class=PlainTextResponse)\ndef demo():\n    return 'Testo semplice'\n"),
("Scaricare un CSV generato","@app.get('/export')\ndef export():\n    return Response('nome,totale\\nAda,42\\n',media_type='text/csv',headers={'Content-Disposition':'attachment; filename=report.csv'})\n"),
("Trasmettere righe con StreamingResponse","@app.get('/stream')\ndef stream():\n    def rows():\n        for n in range(3): yield f'{n}\\n'\n    return StreamingResponse(rows(),media_type='text/plain')\n"),
("Restituire redirect303 dopo POST","@app.post('/submit')\ndef submit():\n    return RedirectResponse('/result',status_code=303)\n@app.get('/result')\ndef result():\n    return {'saved':True}\n"),
("Impostare cookie sicuro per preferenze","@app.post('/theme')\ndef theme(response: Response):\n    response.set_cookie('theme','dark',httponly=True,samesite='lax',secure=False)\n    return {'local_http_demo':True}\n"),
("Eliminare cookie con stesso percorso","@app.post('/logout')\ndef logout(response: Response):\n    response.delete_cookie('theme',path='/')\n    return {'ok':True}\n"),
("Gestire richiesta condizionale con ETag","@app.get('/demo')\ndef demo(if_none_match: Annotated[str | None,Header()]=None):\n    tag='\"v1\"'\n    if if_none_match==tag: return Response(status_code=304)\n    return JSONResponse({'version':1},headers={'ETag':tag})\n"),
("Impostare cache della risposta","@app.get('/demo')\ndef demo(response: Response):\n    response.headers['Cache-Control']='public,max-age=60'\n    return {'version':1}\n"),
("Controllare l'host client della richiesta","@app.get('/demo')\ndef demo(request: Request):\n    return {'host':request.client.host if request.client else None,'path':request.url.path}\n"),
("Nascondere una rotta dalla documentazione","@app.get('/internal',include_in_schema=False)\ndef internal():\n    return {'note':'nascosta dai docs, non protetta'}\n"),
("Documentare status alternativi della rotta","@app.get('/items/{item_id}',responses={404:{'description':'Elemento assente'}},summary='Leggi elemento',tags=['catalogo'])\ndef item(item_id: int):\n    if item_id!=1: raise HTTPException(404,'Assente')\n    return {'id':1}\n"),
("Personalizzare titolo e percorso OpenAPI","app=FastAPI(title='Catalogo API',version='1.0.0',docs_url='/reference',openapi_url='/schema.json')\n@app.get('/demo')\ndef demo():\n    return {'ok':True}\n"),
("Disattivare documentazione automatica","app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)\n@app.get('/demo')\ndef demo():\n    return {'ok':True}\n"),
("Servire file statici da directory dedicata","from fastapi.staticfiles import StaticFiles\nFilePath('public').mkdir(exist_ok=True)\nFilePath('public/demo.txt').write_text('Ciao',encoding='utf8')\napp.mount('/static',StaticFiles(directory='public'),name='static')\n"),
("Definire un endpoint health minimale","@app.get('/health')\ndef health():\n    return {'status':'ok','time':datetime.now(timezone.utc)}\n"),
("Eseguire lavoro bloccante fuori event loop","@app.get('/demo')\nasync def demo():\n    def blocking():\n        time.sleep(0.02)\n        return 42\n    return {'result':await asyncio.to_thread(blocking)}\n"),
]

def files(code):return {'app.py':PRE+code,'requirements.txt':REQ}
COMMAND='python -m venv .venv\n.venv\\Scripts\\python -m pip install -r requirements.txt\n.venv\\Scripts\\python -m uvicorn app:app --host 127.0.0.1 --port 8000'

def build_all():
    b=Book('fastapi','FastAPI0.115.12; Pydantic2.11.7; Python3.11+',['https://fastapi.tiangolo.com/','https://docs.pydantic.dev/latest/'],'Python3.11+ con venv; porta8000 libera. Dipendenze in requirements.txt; /docs permette di provare le rotte. Database e autenticazione di produzione non sono inclusi negli esempi in memoria.')
    for title,code in ROWS:
        add(b,title,files(code),commands=COMMAND,note='app.py contiene applicazione e rotta completa. Apri http://127.0.0.1:8000/docs e usa Try it out sulla rotta indicata dal decoratore; confronta input validi e invalidi. I vincoli dichiarati nei tipi diventano validazione e schema OpenAPI.')
    projects=[
      ('Progetto: API attività con repository SQLite',{'repository.py':"import sqlite3\nfrom contextlib import contextmanager\nfrom pathlib import Path\nDB=Path('tasks.sqlite')\n@contextmanager\ndef connect():\n    c=sqlite3.connect(DB)\n    c.row_factory=sqlite3.Row\n    c.execute('CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY,title TEXT NOT NULL,done INTEGER NOT NULL DEFAULT 0)')\n    try:\n        with c: yield c\n    finally: c.close()\ndef list_tasks():\n    with connect() as c: return [dict(x) for x in c.execute('SELECT * FROM tasks ORDER BY id')]\ndef create(title):\n    with connect() as c:\n        cursor=c.execute('INSERT INTO tasks(title) VALUES(?)',(title,))\n        return {'id':cursor.lastrowid,'title':title,'done':0}\ndef finish(task_id):\n    with connect() as c: return c.execute('UPDATE tasks SET done=1 WHERE id=?',(task_id,)).rowcount\n",'app.py':"from fastapi import FastAPI,HTTPException\nfrom pydantic import BaseModel,Field\nimport repository as repo\napp=FastAPI()\nclass NewTask(BaseModel):\n    title:str=Field(min_length=1,max_length=100)\n@app.get('/tasks')\ndef tasks(): return repo.list_tasks()\n@app.post('/tasks',status_code=201)\ndef create(task:NewTask): return repo.create(task.title)\n@app.patch('/tasks/{task_id}')\ndef finish(task_id:int):\n    if not repo.finish(task_id): raise HTTPException(404,'Task assente')\n    return {'done':True}\n",'test_app.py':"from fastapi.testclient import TestClient\nfrom app import app\nimport repository\ndef test_flow(tmp_path,monkeypatch):\n    monkeypatch.setattr(repository,'DB',tmp_path/'test.sqlite')\n    with TestClient(app) as c:\n        row=c.post('/tasks',json={'title':'Prova'}).json()\n        assert c.patch('/tasks/'+str(row['id'])).status_code==200\n        assert c.get('/tasks').json()[0]['done']==1\n"},'POST/tasks crea; GET/tasks elenca; PATCH/tasks/id completa. SQLite persiste dopo riavvio; il test usa una cartella temporanea.'),
      ('Progetto: API preventivi con validazione e test',{'pricing.py':"from decimal import Decimal,ROUND_HALF_UP\ndef quote(price:Decimal,quantity:int,discount:Decimal):\n    if price<0 or quantity<1 or not 0<=discount<=100: raise ValueError('Valori invalidi')\n    return (price*quantity*(1-discount/100)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)\n",'app.py':"from decimal import Decimal\nfrom fastapi import FastAPI\nfrom pydantic import BaseModel,Field\nfrom pricing import quote\napp=FastAPI()\nclass Request(BaseModel):\n    price:Decimal=Field(ge=0)\n    quantity:int=Field(ge=1)\n    discount:Decimal=Field(ge=0,le=100,default=0)\n@app.post('/quote')\ndef calculate(q:Request): return {'total':str(quote(q.price,q.quantity,q.discount))}\n",'test_pricing.py':"from decimal import Decimal\nfrom pricing import quote\nfrom fastapi.testclient import TestClient\nfrom app import app\ndef test_total(): assert quote(Decimal('10'),3,Decimal('10'))==Decimal('27.00')\ndef test_invalid(): assert TestClient(app).post('/quote',json={'price':-1,'quantity':1}).status_code==422\n"},'POST/quote con prezzo10,quantità3,sconto10 restituisce27.00; campi invalidi ricevono422. Calcolo Decimal separato dalla rotta.')]
    for title,extra,note in projects:
        f={**extra,'requirements.txt':REQ,'README.md':'# '+title+'\n'+note+'\nInstallare requirements, eseguire python -m pytest, avviare uvicorn app:app su localhost8000. Solo dati sintetici.'}
        add(b,title,f,commands=COMMAND,project=True,section='Progetti completi',note=note,expected=note)
    from web_lifecycle import apply
    apply(b)
    assert len(b.recipes)==65,len(b.recipes)
    b.save()

if __name__=='__main__':build_all()
