## Scopo
Produrre un publish leggero richiedendo il runtime sul computer destinazione.

## Prerequisiti
.NET 10 SDK; .NET 10 runtime sulla destinazione.

## Avvio
Salva tutti i file esportati preservando i percorsi relativi. Esegui i comandi dalla directory che contiene il manifest o lo script principale. Usa un ambiente virtuale dedicato per non modificare le dipendenze di altri progetti.

## Controllo dell'artefatto
Produrre un publish leggero richiedendo il runtime sul computer destinazione. Il successo del comando di build non attesta l'avvio su un computer pulito: avvia il risultato sulla destinazione prevista prima di consegnarlo. Questo esempio non pubblica pacchetti né firma eseguibili.