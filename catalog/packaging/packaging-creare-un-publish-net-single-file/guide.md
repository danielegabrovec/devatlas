## Scopo
Abilitare PublishSingleFile per una CLI con runtime incluso.

## Prerequisiti
.NET 10 SDK; alcune risorse/native library possono richiedere estrazione o restare esterne secondo le dipendenze.

## Avvio
Salva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.

## Controllo dell'artefatto
Abilitare PublishSingleFile per una CLI con runtime incluso. Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.