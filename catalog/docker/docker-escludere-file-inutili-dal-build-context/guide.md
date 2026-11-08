## Obiettivo
Usare dockerignore per tenere ambienti virtuali e repository fuori dall'immagine.

## Cartella di lavoro
Salva Dockerfile, app.py, compose.yaml e gli eventuali file aggiuntivi nella stessa cartella. Avvia i comandi da quella cartella. Il servizio ascolta sulla porta 8000 interna; soltanto 127.0.0.1:8089 viene pubblicata sull'host.

## Controllo
Apri http://127.0.0.1:8089 dopo l'avvio e leggi i log in caso di errore. Usare dockerignore per tenere ambienti virtuali e repository fuori dall'immagine.

## Arresto
Usa docker compose down dalla stessa cartella. I volumi nominati sono conservati; nessun comando di questa ricetta esegue prune globale. Esecuzione container e compatibilità macOS non attestate.