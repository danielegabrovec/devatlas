## Scopo
Produrre una distribuzione installabile con build backend dichiarato.

## Prerequisiti
Python 3.12+ e pip; backend scaricato da Internet durante la build isolata.

## Avvio
Salva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.

## Controllo dell'artefatto
Produrre una distribuzione installabile con build backend dichiarato. Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.