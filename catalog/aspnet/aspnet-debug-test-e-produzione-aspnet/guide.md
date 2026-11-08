## Obiettivo
Debug test e produzione aspnet.

VSCode richiede l’estensione C# con debugger coreclr. F5 esegue il task build e avvia Demo.dll; metti un breakpoint in Pricing.Total e visita /quote?price=10&qty=3. Il piccolo runner tests/Checks.csproj verifica totale e quantità invalida senza NuGet aggiuntivi. Publish produce artifacts/publish: l’eseguibile framework dependent richiede runtime.NET10 sul computer di destinazione.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
I test inclusi completano con esito positivo. La configurazione VSCode permette breakpoint sul sorgente; i comandi distinguono verifica, build e avvio di produzione.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.