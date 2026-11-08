## Scopo
Installare soltanto nell'area utente senza richiedere privilegi amministrativi.

## Prerequisiti
Windows, Inno Setup 6 installato nel percorso indicato. L'installer è non firmato; la ricetta non lo esegue.

## Avvio
Salva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.

## Controllo dell'artefatto
Installare soltanto nell'area utente senza richiedere privilegi amministrativi. Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.