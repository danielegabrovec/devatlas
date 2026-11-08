## Scopo
Usare pip freeze come fotografia dell'ambiente e non come promessa di lock multipiattaforma.

## Prerequisiti
Ambiente virtuale Python dedicato, PowerShell 7. Il risultato dipende dall'ambiente corrente.

## Avvio
Salva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.

## Controllo dell'artefatto
Usare pip freeze come fotografia dell'ambiente e non come promessa di lock multipiattaforma. Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.