## Obiettivo
Debug test e produzione fastapi.

In VSCode seleziona l’interprete .venv e installa l’estensione Python/Debugpy. F5 avvia uvicorn senza reload per mantenere il processo del debugger; imposta un breakpoint nella rotta quote. pytest usa TestClient senza server pubblico. Per un avvio multiprocesso locale usa --workers2 e nessun --reload; reverse proxy, TLS e gestione del servizio dipendono dall’ambiente di distribuzione.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
I test inclusi completano con esito positivo. La configurazione VSCode permette breakpoint sul sorgente; i comandi distinguono verifica, build e avvio di produzione.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.