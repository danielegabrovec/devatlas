## Scopo
Congelare una piccola CLI Python lasciando visibili le risorse del pacchetto.

## Prerequisiti
Python 3.12/3.13 e PyInstaller 6.16.0. Costruire sul sistema di destinazione.

## Avvio
Salva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.

## Controllo dell'artefatto
Congelare una piccola CLI Python lasciando visibili le risorse del pacchetto. Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.