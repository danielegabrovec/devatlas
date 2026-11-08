## Obiettivo
Inizializzare ambiente e progetto aspnet.

global.json seleziona una feature bandSDK10 senza scaricarla automaticamente. Il progetto Web include soltanto il framework condiviso ASP.NET. Dopo restore avvia e richiama GET/health: ricevi ok=true. Per Linux/macOS usa gli stessi comandi dotnet nel terminale disponibile.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
L’applicazione si avvia localmente con il file di configurazione fornito. La versione della toolchain è verificabile dai comandi iniziali.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.