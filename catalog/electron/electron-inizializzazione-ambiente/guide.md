## Ambiente e manifest
Installa Node.js 24 LTS con npm, esporta i quattro file in una cartella e apri lì PowerShell. package.json definisce l'entry point main.cjs e blocca Electron alla versione 45.1.0. npm install crea package-lock.json: conservalo e usa npm ci nelle installazioni successive dello stesso progetto.

## Primi processi
main.cjs crea la BrowserWindow dopo app.whenReady. index.html carica un renderer separato; contextIsolation e sandbox restano attivi e nodeIntegration è disabilitato. Per questo contatore basta il DOM: non occorre esporre API native né installare un server web.

## Verifica
Premi Incrementa e osserva il contatore. Chiudendo la finestra termina questa app Windows dimostrativa. Non è una build del framework Electron da sorgenti: il manifest scarica il runtime precompilato della versione indicata. Non vengono attestati avvii macOS o Linux.