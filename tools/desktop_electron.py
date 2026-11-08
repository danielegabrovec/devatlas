"""Electron 45 original, isolated-renderer examples."""
import json
from catalog_support import Book
from desktop_tools_common import save_book

TOPICS = [
("versions","Leggere versioni Electron, Chromium e Node","Esporre soltanto un oggetto di versioni tramite IPC, senza abilitare Node nel renderer.",'return {electron:process.versions.electron,chrome:process.versions.chrome,node:process.versions.node};'),
("user-data","Individuare la cartella dati dell'app","Usare app.getPath per conservare dati fuori dalla directory di installazione.",'return {userData:app.getPath("userData"),documents:app.getPath("documents")};'),
("clipboard-write","Copiare testo negli appunti dal processo principale","Tenere l'accesso agli appunti dietro una funzione IPC specifica.",'clipboard.writeText("Codice pronto da incollare"); return "Testo copiato";'),
("clipboard-read","Leggere gli appunti soltanto su richiesta","Effettuare la lettura al clic del pulsante senza osservare gli appunti in background.",'return clipboard.readText();'),
("file-open","Aprire un file scelto con dialogo nativo","Leggere solo il percorso restituito dal selettore e gestire Annulla.",'const choice=await dialog.showOpenDialog(win,{properties:["openFile"],filters:[{name:"Testo",extensions:["txt","md"]}]}); if(choice.canceled) return "Annullato"; const stat=await fs.stat(choice.filePaths[0]); if(stat.size>1000000) throw new Error("File oltre 1 MB"); return await fs.readFile(choice.filePaths[0],"utf8");'),
("file-save","Salvare un testo con dialogo nativo","Scrivere UTF-8 dopo la conferma del percorso di destinazione.",'const choice=await dialog.showSaveDialog(win,{defaultPath:"appunto.txt"}); if(choice.canceled || !choice.filePath) return "Annullato"; await fs.writeFile(choice.filePath,"Appunto Electron\\n","utf8"); return choice.filePath;'),
("folder","Scegliere una cartella esistente","Mostrare un selettore di cartella senza modificare i contenuti.",'const choice=await dialog.showOpenDialog(win,{properties:["openDirectory"]}); return choice.canceled?"Annullato":choice.filePaths[0];'),
("message-box","Richiedere una conferma con dialogo nativo","Definire pulsante predefinito e annullamento sulla scelta conservativa.",'const answer=await dialog.showMessageBox(win,{type:"question",message:"Confermare l’operazione dimostrativa?",buttons:["Annulla","Conferma"],defaultId:0,cancelId:0}); return answer.response===1?"Confermato":"Annullato";'),
("native-theme","Leggere la preferenza di tema del sistema","Interrogare nativeTheme senza dipendere da CSS per conoscere il tema OS.",'return {dark:nativeTheme.shouldUseDarkColors,highContrast:nativeTheme.shouldUseHighContrastColors};'),
("theme-override","Impostare il tema nativo dell'app","Alternare themeSource tra dark e light su comando esplicito.",'nativeTheme.themeSource=nativeTheme.themeSource==="dark"?"light":"dark"; return nativeTheme.themeSource;'),
("screens","Elencare schermi e fattori di scala","Usare screen.getAllDisplays senza assumere un solo monitor.",'return screen.getAllDisplays().map(display=>({id:display.id,bounds:display.bounds,scale:display.scaleFactor}));'),
("window-title","Aggiornare il titolo della finestra","Impostare il titolo nel main process invece di esporre BrowserWindow al renderer.",'win.setTitle("Documento locale — salvato"); return win.getTitle();'),
("window-size","Impostare dimensioni minime e dimensioni correnti","Rendere la finestra ridimensionabile entro un limite sensato.",'win.setMinimumSize(600,400); win.setSize(900,600); return win.getSize();'),
("window-center","Centrare la finestra sullo schermo","Usare center dopo avere scelto le dimensioni.",'win.center(); return win.getBounds();'),
("window-minimize","Minimizzare una finestra","Invocare minimize da un canale IPC dedicato.",'win.minimize(); return "Finestra minimizzata";'),
("window-maximize","Alternare massimizzazione e ripristino","Verificare isMaximized prima di scegliere l'operazione.",'if(win.isMaximized()) win.unmaximize(); else win.maximize(); return {maximized:win.isMaximized()};'),
("fullscreen","Alternare la modalità schermo intero","Cambiare full screen mantenendo la gestione nel main process.",'win.setFullScreen(!win.isFullScreen()); return "Modalità alternata";'),
("progress","Mostrare avanzamento nella barra applicazioni","Impostare un progresso compreso tra zero e uno e rimuoverlo con -1.",'win.setProgressBar(0.65); setTimeout(()=>{if(!win.isDestroyed()) win.setProgressBar(-1);},2000); return "Avanzamento 65% per due secondi";'),
("flash","Richiamare l'attenzione sulla finestra","Attivare flashFrame per una breve notifica locale.",'win.flashFrame(true); setTimeout(()=>{if(!win.isDestroyed()) win.flashFrame(false);},1500); return "Richiesta di attenzione inviata";'),
("zoom","Cambiare lo zoom dei contenuti","Usare setZoomFactor senza ridimensionare la finestra.",'const factor=win.webContents.getZoomFactor()===1?1.25:1; win.webContents.setZoomFactor(factor); return {zoom:factor};'),
("pdf","Esportare la pagina corrente in PDF","Creare il PDF solo dopo la scelta del percorso e senza avviare una stampa fisica.",'const choice=await dialog.showSaveDialog(win,{defaultPath:"pagina.pdf",filters:[{name:"PDF",extensions:["pdf"]}]}); if(choice.canceled || !choice.filePath) return "Annullato"; const data=await win.webContents.printToPDF({printBackground:true,pageSize:"A4"}); await fs.writeFile(choice.filePath,data); return choice.filePath;'),
("capture","Salvare una schermata della finestra","Usare capturePage per il contenuto della sola BrowserWindow.",'const choice=await dialog.showSaveDialog(win,{defaultPath:"finestra.png"}); if(choice.canceled || !choice.filePath) return "Annullato"; const image=await win.webContents.capturePage(); await fs.writeFile(choice.filePath,image.toPNG()); return choice.filePath;'),
("notification","Mostrare una notifica locale di sistema","Verificare il supporto API prima di creare Notification.",'if(!Notification.isSupported()) return "Notifiche non supportate"; new Notification({title:"Ricettario",body:"Operazione locale completata"}).show(); return "Notifica richiesta al sistema";'),
("app-menu","Creare un menu nativo con scorciatoie","Costruire Menu da template usando ruoli standard.",'const menu=Menu.buildFromTemplate([{label:"File",submenu:[{role:"close"}]},{label:"Modifica",submenu:[{role:"copy"},{role:"paste"},{role:"selectAll"}]}]); Menu.setApplicationMenu(menu); return "Menu installato";'),
("context-menu","Aprire un menu contestuale nativo","Usare popup sulla finestra proprietaria e azioni circoscritte.",'const menu=Menu.buildFromTemplate([{label:"Copia esempio",click:()=>clipboard.writeText("Esempio")},{role:"selectAll"}]); menu.popup({window:win}); return "Menu aperto";'),
("external-url","Aprire soltanto un collegamento esterno autorizzato","Controllare protocollo e hostname prima di shell.openExternal.",'const url=new URL("https://www.electronjs.org/docs/latest/"); if(url.protocol!=="https:" || url.hostname!=="www.electronjs.org") throw new Error("URL non consentito"); await shell.openExternal(url.href); return "Documentazione aperta nel browser";'),
("memory","Leggere le metriche dei processi dell'app","Usare app.getAppMetrics per una diagnostica locale.",'return app.getAppMetrics().map(({pid,type,memory})=>({pid,type,memory}));'),
("locale","Leggere lingua e lingue preferite","Distinguere locale dell'app ed elenco delle lingue del sistema.",'return {locale:app.getLocale(),preferred:app.getPreferredSystemLanguages()};'),
("idle","Misurare inattività del sistema","Usare powerMonitor dopo app.whenReady.",'return {idleSeconds:powerMonitor.getSystemIdleTime(),state:powerMonitor.getSystemIdleState(60)};'),
("app-version","Leggere la versione dal manifest applicativo","Usare app.getVersion per mostrare la versione distribuita.",'return {name:app.getName(),version:app.getVersion(),packaged:app.isPackaged};'),
("temp-file","Scrivere un file temporaneo dedicato","Creare una cartella nuova senza sovrascrivere documenti dell'utente.",'const folder=await fs.mkdtemp(path.join(app.getPath("temp"),"recipe-")); const target=path.join(folder,"report.txt"); await fs.writeFile(target,"Report locale\\n","utf8"); return target;'),
("log-file","Aggiungere una riga a un log locale","Registrare data e messaggio in userData senza contenuti sensibili.",'const folder=app.getPath("userData"); await fs.mkdir(folder,{recursive:true}); const file=path.join(folder,"demo.log"); await fs.appendFile(file,new Date().toISOString()+" azione dimostrativa\\n","utf8"); return file;'),
("permissions","Rifiutare richieste permessi del renderer","Installare un permissionRequestHandler conservativo nella sessione.",'win.webContents.session.setPermissionRequestHandler((_contents,_permission,callback)=>callback(false)); return "Nuove richieste di permessi rifiutate";'),
("spellcheck","Disattivare la correzione ortografica nel codice","Impostare il correttore a livello di sessione per un editor di sorgenti.",'win.webContents.session.setSpellCheckerEnabled(false); return "Correttore ortografico disattivato";'),
("find-in-page","Cercare un termine nel contenuto della pagina","Avviare la ricerca Chromium con findInPage.",'return {requestId:win.webContents.findInPage("Ricetta",{forward:true,findNext:false})};'),
("stop-find","Chiudere la ricerca nella pagina","Rimuovere selezioni e stato della ricerca Chromium.",'win.webContents.stopFindInPage("clearSelection"); return "Ricerca chiusa";'),
("relaunch","Preparare un riavvio con conferma","Richiedere un sì esplicito prima di rilanciare il processo applicativo.",'const answer=await dialog.showMessageBox(win,{message:"Riavviare questa app dimostrativa?",buttons:["Annulla","Riavvia"],defaultId:0,cancelId:0}); if(answer.response===1){app.relaunch();app.exit(0);} return "Annullato";'),
("devtools","Aprire strumenti di debug soltanto in sviluppo","Impedire l'apertura del pannello quando app.isPackaged è vero.",'if(app.isPackaged) return "Debug disabilitato nel pacchetto"; win.webContents.openDevTools({mode:"detach"}); return "DevTools aperti";'),
("content-bounds","Distinguere area contenuti e bordi della finestra","Leggere getContentBounds anziché sottrarre dimensioni presunte della cornice.",'return {window:win.getBounds(),content:win.getContentBounds()};'),
]

INDEX = '''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'"><title>Ricetta Electron</title><link rel="stylesheet" href="style.css"></head><body><h1>Ricetta Electron</h1><button id="run">Esegui dimostrazione</button><pre id="result"></pre><script src="renderer.js"></script></body></html>\n'''
CSS='body{font:16px system-ui;margin:32px;background:#162030;color:#eef3fa}button{padding:12px;border:0;border-radius:8px;background:#7dcce5;color:#102030}pre{white-space:pre-wrap;overflow-wrap:anywhere}\n'
MAIN='''const {app,BrowserWindow,ipcMain,dialog,clipboard,nativeTheme,Menu,screen,shell,Notification,powerMonitor}=require('electron');
const fs=require('node:fs/promises');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
let win;
app.whenReady().then(async()=>{
 win=new BrowserWindow({width:900,height:620,webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true}});
 win.webContents.setWindowOpenHandler(()=>({action:'deny'}));
 win.webContents.on('will-navigate',event=>event.preventDefault());
 ipcMain.handle('demo:run',async(event)=>{
  if(event.senderFrame?.url!==pathToFileURL(path.join(__dirname,'index.html')).href) throw new Error('Origine IPC non consentita');
  BODY
 });
 await win.loadFile('index.html');
});
app.on('window-all-closed',()=>{if(process.platform!=='darwin') app.quit();});
app.on('activate',()=>{if(BrowserWindow.getAllWindows().length===0) app.relaunch(),app.exit(0);});
'''
PRELOAD="const {contextBridge,ipcRenderer}=require('electron');\ncontextBridge.exposeInMainWorld('recipe',{run:()=>ipcRenderer.invoke('demo:run')});\n"
RENDERER="document.querySelector('#run').addEventListener('click',async()=>{const output=document.querySelector('#result');try{output.textContent=JSON.stringify(await window.recipe.run(),null,2);}catch(error){output.textContent=error.message;}});\n"

def files(body):
    return {"package.json":json.dumps({"name":"ricetta-electron","version":"1.0.0","private":True,"main":"main.cjs","scripts":{"start":"electron ."},"devDependencies":{"electron":"45.1.0"}},indent=2),"main.cjs":MAIN.replace("BODY",body),"preload.cjs":PRELOAD,"index.html":INDEX,"style.css":CSS,"renderer.js":RENDERER}

def build_all():
    assert len(TOPICS)==39,len(TOPICS)
    book=Book("electron","Electron 45.1.0; Node.js 24 LTS per npm",["https://www.electronjs.org/docs/latest/","https://www.electronjs.org/docs/latest/tutorial/security","https://releases.electronjs.org/"],"Node.js 24 con npm; ambiente desktop. L'installazione scarica il runtime Electron. Nessuna esecuzione attestata su Linux/macOS.")
    for key,title,description,body in TOPICS:
        book.add(key,title,description,files(body),commands="npm install\nnpm start",explanation=f"## Obiettivo\n{description}\n\n## Uso\nSalva i sei file nella stessa cartella. Avvia npm install e npm start da quella cartella, poi premi Esegui dimostrazione. Il corpo specifico si trova nel gestore demo:run di main.cjs. La Promise restituisce un dato serializzabile mostrato nel pannello.\n\n## Architettura\nIl renderer non usa require: contextIsolation e sandbox restano attivi. Il preload espone una sola funzione senza passare ipcRenderer. Il main verifica l'origine del frame e gestisce dialoghi, filesystem e finestre. Navigazioni e popup non richiesti vengono bloccati.\n\n## Risultato\n{description} Se la piattaforma limita una funzione nativa, l'esito dipende dal supporto del sistema; non è attestata una prova multipiattaforma.",expected=description,tags=[key,"IPC","desktop","contextIsolation"],errors=["Electron non si avvia: verificare il download del runtime e avviare da una sessione desktop.","Errore IPC nel pannello: leggere il messaggio; Annulla nei dialoghi non è un errore."])
    project=files('return "Note locali";')
    project["main.cjs"]='''const {app,BrowserWindow,ipcMain}=require('electron');
const fs=require('node:fs/promises');const path=require('node:path');const {pathToFileURL}=require('node:url');
let win;
app.whenReady().then(async()=>{
 const folder=app.getPath('userData');await fs.mkdir(folder,{recursive:true});const file=path.join(folder,'notes.json');
 let notes=[];try{notes=JSON.parse(await fs.readFile(file,'utf8'));if(!Array.isArray(notes)||!notes.every(v=>typeof v==='string')) throw new Error('Formato note non valido');}catch(error){if(error.code!=='ENOENT') throw error;}
 win=new BrowserWindow({width:800,height:550,webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true}});
 function validate(event){if(event.senderFrame?.url!==pathToFileURL(path.join(__dirname,'index.html')).href) throw new Error('Origine non consentita');}
 ipcMain.handle('notes:list',event=>{validate(event);return notes;});
 let writing=false;
 ipcMain.handle('notes:add',async(event,value)=>{validate(event);if(writing) throw new Error('Salvataggio in corso');if(typeof value!=='string'||!value.trim()||value.length>2000) throw new Error('Nota non valida');writing=true;try{const next=[...notes,value.trim()];await fs.writeFile(file+'.tmp',JSON.stringify(next,null,2),'utf8');await fs.rename(file+'.tmp',file);notes=next;return notes;}finally{writing=false;}});
 win.webContents.setWindowOpenHandler(()=>({action:'deny'}));win.webContents.on('will-navigate',e=>e.preventDefault());
 await win.loadFile('index.html');
}).catch(error=>{console.error(error);app.quit();});
app.on('window-all-closed',()=>app.quit());
'''
    project["preload.cjs"]="const {contextBridge,ipcRenderer}=require('electron');contextBridge.exposeInMainWorld('notes',{list:()=>ipcRenderer.invoke('notes:list'),add:value=>ipcRenderer.invoke('notes:add',value)});\n"
    project["index.html"]=INDEX.replace('<button id="run">Esegui dimostrazione</button><pre id="result"></pre>','<input id="note" maxlength="2000" aria-label="Nota"><button id="add">Aggiungi</button><p id="status"></p><ul id="notes"></ul>')
    project["renderer.js"]='''const list=document.querySelector('#notes'),input=document.querySelector('#note'),button=document.querySelector('#add'),status=document.querySelector('#status');
function render(rows){list.replaceChildren(...rows.map(text=>{const item=document.createElement('li');item.textContent=text;return item;}));}
window.notes.list().then(render).catch(error=>status.textContent=error.message);
button.addEventListener('click',async()=>{button.disabled=true;try{render(await window.notes.add(input.value));input.value='';status.textContent='Salvato';}catch(error){status.textContent=error.message;}finally{button.disabled=false;}});
'''
    project["README.md"]="# Note Electron\nInstallare e avviare con npm. Le note sono conservate in userData/notes.json. Nessun contenuto della nota viene interpretato come HTML.\n"
    book.add("progetto-note","Progetto completo: note Electron con IPC isolato","Conservare note JSON usando renderer isolato, validazione IPC e scrittura serializzata.",project,project=True,section="Progetti completi",commands="npm install\nnpm start",explanation="## Avvio\nSalva i sette file e avvia dal manifest package.json. Inserisci due note, chiudi e riapri. Il main conserva il file JSON nella cartella userData; la UI usa textContent e non esegue il contenuto delle note. La funzione IPC valida tipo, lunghezza e origine del frame.\n\n## Errori\nUn JSON non valido interrompe l'avvio e stampa un errore nel terminale senza sovrascriverlo. Una scrittura non riuscita viene mostrata nello stato; l'input resta disponibile per riprovare. Il pulsante evita salvataggi contemporanei.\n\n## Verifica\nEsempio documentato, non dichiarato eseguito su altri sistemi.",expected="Due note salvate ricompaiono dopo il riavvio; HTML digitato compare come testo.",tags=["project","IPC","JSON","security"],errors=["notes.json malformato: salvare una copia prima di correggerlo.","Cartella userData non scrivibile: la nota non viene aggiunta."])
    assert len(book.recipes)==40
    save_book(book)

if __name__=="__main__":build_all()
