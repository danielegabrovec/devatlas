## Scopo
Usare electron-builder --dir per revisionare il contenuto prima di creare installer.

## Prerequisiti
Node.js 24, Electron 45.1.0 e electron-builder 26.0.12; download dei tool di packaging richiesto. Nessuna firma o pubblicazione automatica.

## Avvio
Salva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.

## Controllo dell'artefatto
Usare electron-builder --dir per revisionare il contenuto prima di creare installer. Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.