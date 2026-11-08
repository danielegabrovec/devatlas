"""Smoke UI locali dei tre capstone React e della biblioteca HTML."""
import functools,http.server,json,subprocess,sys,threading
from pathlib import Path
from catalog_support import ROOT

CACHE=ROOT/'.cache/web-qa'

def export_html():
    p=next((ROOT/'catalog/html-css').glob('html-css-progetto-*/recipe.json'))
    data=json.loads(p.read_text(encoding='utf8'));dest=CACHE/'html-project';dest.mkdir(exist_ok=True)
    for a in data['assets']:
        if a['role']=='command':continue
        (dest/a['path']).write_text((p.parent/a['source']).read_text(encoding='utf8'),encoding='utf8')
    return dest

def main():
    targets=[];servers=[]
    for path in sorted((CACHE/'node/projects').glob('react-progetto-*')):
        targets.append((path.name,path/'dist'))
    targets.append(('html-library',export_html()))
    for name,folder in targets:
        handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(folder))
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        servers.append(server)
    tests=[{'id':name,'url':'http://127.0.0.1:'+str(server.server_port)} for(name,_),server in zip(targets,servers)]
    script=r"""const{chromium}=require('C:/Users/danie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');const fs=require('fs');(async()=>{const tests=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});const results=[];try{for(const t of tests){const context=await browser.newContext({viewport:{width:1000,height:800}});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));try{await page.goto(t.url);if(t.id.includes('lista-attivita')){await page.getByLabel('Nuova attività').fill('Prova automatica');await page.getByRole('button',{name:'Aggiungi'}).click();await page.getByText('Prova automatica',{exact:true}).waitFor();await page.getByRole('checkbox').check();await page.reload();if(!await page.getByRole('checkbox').isChecked())throw Error('Persistenza checkbox assente');}else if(t.id.includes('catalogo-con-ricerca')){await page.getByLabel('Cerca',{exact:true}).fill('Mouse');if(!await page.getByRole('status').textContent().then(x=>x.includes('1')))throw Error('Filtro non applicato');await page.getByLabel('Disponibili').check();if(!await page.getByRole('status').textContent().then(x=>x.includes('0')))throw Error('Filtro stock non applicato');}else if(t.id.includes('tabella-importazione')){await page.getByRole('button',{name:'Analizza'}).click();await page.getByText('Totale:30').waitFor();await page.getByLabel('Dati',{exact:true}).fill('nome\timporto\nAda\tx');await page.getByRole('button',{name:'Analizza'}).click();if(!await page.getByRole('alert').textContent().then(x=>x.includes('Riga invalida')))throw Error('Errore importazione mancante');}else{if(await page.locator('#cards article').count()!==3)throw Error('Tre card attese');await page.getByLabel('Cerca ricette').fill('file');if(await page.locator('#cards article').count()!==1)throw Error('Ricerca file');await page.getByLabel('Cerca ricette').fill('');await page.getByLabel('Tecnologia').selectOption('SQL');if(await page.locator('#cards article').count()!==1)throw Error('Filtro SQL');await page.getByRole('button',{name:'Cambia tema'}).click();if(!await page.locator('body').evaluate(e=>e.classList.contains('dark')))throw Error('Tema non cambiato');}if(errors.length)throw Error(errors.join(';'));results.push({id:t.id,passed:true,details:'Flusso browser Chromium/Windows su localhost; nessun errore JS.'});}catch(e){results.push({id:t.id,passed:false,details:String(e)})}await context.close();}}finally{await browser.close()}fs.writeFileSync(process.argv[3],JSON.stringify(results,null,2));console.log(JSON.stringify(results));process.exitCode=results.some(r=>!r.passed)?1:0;})();"""
    (CACHE/'browser-smoke.cjs').write_text(script,encoding='utf8')
    (CACHE/'browser-targets.json').write_text(json.dumps(tests),encoding='utf8')
    try:
        p=subprocess.run(['node',str(CACHE/'browser-smoke.cjs'),str(CACHE/'browser-targets.json'),str(ROOT/'reports/web-browser-smoke.json')],capture_output=True,text=True,timeout=120)
        print(p.stdout);print(p.stderr)
    finally:
        for server in servers:server.shutdown();server.server_close()

if __name__=='__main__':main()
