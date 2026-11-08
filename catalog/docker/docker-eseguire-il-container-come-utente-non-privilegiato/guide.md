## Obiettivo
Impostare UID e GID numerici per un'app che non scrive nei sorgenti.

## Cartella di lavoro
Salva Dockerfile, app.py, compose.yaml e gli eventuali file aggiuntivi nella stessa cartella. Avvia i comandi da quella cartella. Il servizio ascolta sulla porta 8000 interna; soltanto 127.0.0.1:8089 viene pubblicata sull'host.

## Controllo
Apri http://127.0.0.1:8089 dopo l'avvio e leggi i log in caso di errore. Impostare UID e GID numerici per un'app che non scrive nei sorgenti.

## Arresto
Usa docker compose down dalla stessa cartella. I volumi nominati sono conservati; nessun comando di questa ricetta esegue prune globale. Esecuzione container e compatibilità macOS non attestate.