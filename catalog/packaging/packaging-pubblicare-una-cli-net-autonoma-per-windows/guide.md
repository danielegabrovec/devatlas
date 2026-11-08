## Scopo
Includere il runtime .NET nel publish scegliendo win-x64.

## Prerequisiti
.NET 10 SDK, download runtime pack possibile durante restore.

## Avvio
Salva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.

## Controllo dell'artefatto
Includere il runtime .NET nel publish scegliendo win-x64. Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.