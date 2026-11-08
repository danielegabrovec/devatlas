"""Keep verification only while every asset still matches the checked source."""
import hashlib,json
from catalog_support import ROOT
CACHE=ROOT/'tools/expansion-frameworks-verification.json'

def apply_errors(book):
    for recipe in book.recipes:
        if recipe.get('errors'):continue
        if book.stack in ('vue','svelte','angular'):
            errors=['Import o plugin non risolto: eseguire npm install nella radice con package.json e rispettare le versioni del manifest, senza sostituirle con il latest globale.','Porta del server occupata: scegliere una porta locale libera con npm run dev -- --port 5180 e aggiornare l’URL del debugger alla stessa porta.']
            if recipe['section']=='Distribuzione':errors.append('Asset404 dopo la consegna: allineare base/base-href e sottocartella del server; distribuire l’output dist, non i sorgenti src.')
        elif book.stack=='spring':
            errors=['UnsupportedClassVersionError o release21 non supportata: confrontare java -version con mvn --version e usare un JDK21+ anche in JAVA_HOME.','Port8086 already in use: arrestare il proprio precedente processo del laboratorio oppure usare --server.port=8087, aggiornando gli URL delle richieste.']
            if recipe['section']=='Codice applicativo':errors.append('HTTP400: verificare nomi dei parametri, Content-Type application/json e vincoli del DTO; il fallimento di @Valid non èun errore della connessione HTTP.')
        elif book.stack=='flutter':
            errors=['Target of URI does not exist per flutter/material.dart: eseguire bootstrap e flutter pub get nel progetto app generato, non direttamente nella cartella recipe.','Build Windows senza compilatore: risolvere flutter doctor installando il workload Desktop development with C++ di Visual Studio; la sola estensione VS Code non fornisce il toolchain.','No supported devices connected: controllare flutter devices e selezionare una destinazione predisposta; Android richiede SDK/licenze ed emulatore o dispositivo, iOS richiede macOS/Xcode.']
        elif book.stack=='tauri':
            errors=['link.exe o Windows SDK non trovato: usare RustMSVC e il workload C++ Visual Studio richiesti; una toolchain GNU non equivale al target MSVC del progetto.','Comando window non consentito: verificare nella capability della finestra main il permesso core specifico, senza disabilitare tutte le restrizioni.','window.__TAURI__ assente: avviare npm run dev dalla radice Tauri e mantenere withGlobalTauri, invece di aprire index.html in un browser ordinario.']
        elif book.stack=='mongodb':errors=['Connessione rifiutata: verificare il processo didattico su127.0.0.1:27018, senza sostituire la URL con un database reale.','Schema o indice incompatibile: controllare nome del database atlas_demo e oggetti della sola prova; preservare i dati prima di adattare uno script che contiene drop.']
        else:errors=['Connessione rifiutata: verificare il solo processo didattico su127.0.0.1:6381.','WRONGTYPE o altro errore Redis: controllare TYPE e namespace della chiave; i wrapper redis-cli usano -e perché set -e della shell da solo non converte una risposta Redis di errore in fallimento.']
        recipe['errors']=errors

def save_book(book):
    apply_errors(book)
    cached=json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
    for recipe in book.recipes:
        row=cached.get(recipe['id'])
        current={asset['id']:hashlib.sha256(asset['content'].encode()).hexdigest() for asset in recipe['assets']}
        if row and row.get('hashes')==current:
            recipe['verification']=row['verification']
    book.save()

def capture(stacks):
    data=json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
    for stack in stacks:
        for path in (ROOT/'catalog'/stack).glob('*/recipe.json'):
            recipe=json.loads(path.read_text(encoding='utf-8'))
            data[recipe['id']]={'hashes':{asset['id']:asset['sha256'] for asset in recipe['assets']},'verification':recipe['verification']}
    CACHE.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
