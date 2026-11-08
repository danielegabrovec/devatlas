## Scopo
Rifiutare percorsi che escono dalla cartella e digest non corrispondenti.

## Prerequisiti
Python 3.12+. Il manifest è un controllo d'integrità, non sostituisce una firma attendibile.

## Avvio
Salva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.

## Controllo dell'artefatto
Rifiutare percorsi che escono dalla cartella e digest non corrispondenti. Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.