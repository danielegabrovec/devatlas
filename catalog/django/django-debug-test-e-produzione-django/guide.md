## Obiettivo
Debug test e produzione django.

In VSCode seleziona .venv e Python/Debugpy; F5 avvia Django senza reloader e senza thread aggiuntivi. I test usano SQLite separato. check --deploy segnala esplicitamente DEBUG e chiave del laboratorio: prima di esporre pubblicamente imposta DEBUG=False, SECRET_KEY da ambiente e ALLOWED_HOSTS reali. collectstatic prepara gli asset; Waitress dimostra il processo WSGI locale, mentre TLS/statici pubblici richiedono il server previsto dal deployment.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
I test inclusi completano con esito positivo. La configurazione VSCode permette breakpoint sul sorgente; i comandi distinguono verifica, build e avvio di produzione.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.