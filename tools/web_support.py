"""Wrapper di esempio condivisi; gli inventari descrivono operazioni curate."""
import json,hashlib
from pathlib import Path
from catalog_support import Book,slug

def verification(stack,title,files=None):
    path=Path(__file__).with_name('web_verification.json')
    result=json.loads(path.read_text(encoding='utf8')).get(stack+'-'+slug(title)) if path.exists() else None
    if result and files is not None and result.get('files_sha256'):
        current={name:hashlib.sha256((text.rstrip()+'\n').encode()).hexdigest() for name,text in files.items()}
        if current!=result['files_sha256']:return None
    return result

REACT_PACKAGE=json.dumps({"name":"atlas-react-example","version":"1.0.0","private":True,"type":"module","scripts":{"dev":"vite --host 127.0.0.1","build":"vite build","preview":"vite preview"},"dependencies":{"react":"19.1.1","react-dom":"19.1.1"},"devDependencies":{"vite":"7.1.7"}},indent=2)
REACT_IMPORT="import React, {useState,useEffect,useMemo,useRef,useReducer,useId,useContext,createContext,useCallback,useLayoutEffect,useTransition,useDeferredValue,useSyncExternalStore,useImperativeHandle,forwardRef,memo,lazy,Suspense,Component} from 'react';\nimport {createPortal} from 'react-dom';\n"
HTML='<!doctype html><html lang="it"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Esempio</title></head><body><div id="root"></div><script type="module" src="/src/main.jsx"></script></body></html>'
STYLE="body{font:16px system-ui;margin:2rem;background:#f5f7fb;color:#172033}button,input,select,textarea{font:inherit;padding:.5rem;margin:.3rem}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #1769c5;outline-offset:3px}label{display:block;margin:.5rem 0}pre{white-space:pre-wrap}table{border-collapse:collapse}td,th{padding:.5rem;border:1px solid #bbc}"

def react_files(code):
    return {"package.json":REACT_PACKAGE,"index.html":HTML,"src/main.jsx":"import React from 'react';import{createRoot}from'react-dom/client';import App from './App.jsx';import './style.css';createRoot(document.getElementById('root')).render(<React.StrictMode><App/></React.StrictMode>);","src/App.jsx":REACT_IMPORT+code,"src/style.css":STYLE}

NEXT_PACKAGE=json.dumps({"name":"atlas-next-example","private":True,"version":"1.0.0","scripts":{"dev":"next dev --hostname 127.0.0.1","build":"next build","start":"next start --hostname 127.0.0.1"},"dependencies":{"next":"16.4.3","react":"19.3.0","react-dom":"19.3.0"}},indent=2)
def next_files(files):
    return {"package.json":NEXT_PACKAGE,"app/layout.js":"import './globals.css';export const metadata={title:'Laboratorio Next.js'};export default function Layout({children}){return <html lang=\"it\"><body><nav><a href=\"/\">Home</a></nav><main>{children}</main></body></html>}","app/page.js":"export default function Page(){return <h1>Laboratorio Next.js</h1>}","app/globals.css":STYLE,**files}

def add(b,title,codefiles,*,note="",expected="",commands="",project=False,parameters=None,tags=None,section="Codice applicativo"):
    # I progetti si filtrano con project=True; section mantiene il vocabolario dell'app.
    if section=='Progetti completi':section='Codice applicativo'
    if project and isinstance(commands,str) and b.stack in ('react','nextjs','fastapi','django','aspnet'):
        port={'react':5173,'nextjs':3000,'fastapi':8000,'django':8000,'aspnet':5000}[b.stack]
        parameters=parameters or [{'name':'port','label':'Porta locale','type':'port','default':port,'required':True}]
        if b.stack in ('react','nextjs'):
            commands=commands.replace('npm run dev','npm run dev -- --port {{port}}')
        elif b.stack=='fastapi':commands=commands.replace('--port 8000','--port {{port}}')
        else:commands=commands.replace('127.0.0.1:'+str(port),'127.0.0.1:{{port}}')
    b.add(title,title,note or title+" con esempio completo esportabile.",codefiles,section=section,project=project,parameters=parameters,
          commands=commands,tags=tags or [b.stack,"example",*title.lower().split()[:4]],
          expected=expected or "Il risultato mostra il comportamento descritto nel titolo; i dati dimostrativi sono inclusi nel sorgente.",
          explanation=f"## Obiettivo\n{title}.\n\n{note}\n\n## Procedura\nEsporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.\n\n## Controllo\n{expected or 'Interagisci con il controllo o richiama la rotta indicata nel sorgente e osserva il risultato. Confronta gli input validi e invalidi prima di integrare il codice.'}\n\n## Integrazione\nLe risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.",
          verification=verification(b.stack,title,codefiles),errors=["Comando non trovato: installare la toolchain elencata nei prerequisiti.","Dipendenza mancante: eseguire l'installazione nella radice esportata, senza cambiare le versioni dichiarate."])
