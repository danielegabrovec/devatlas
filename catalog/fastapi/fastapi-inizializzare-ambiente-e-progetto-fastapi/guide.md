## Obiettivo
Inizializzare ambiente e progetto fastapi.

Crea il venv e installa le versioni dichiarate senza modificare Python globale. app:app significa modulo app.py e istanza app. /docs espone OpenAPI; /health restituisce ok=true. Su Linux/macOS il Python del venv si trova in .venv/bin/python. --reload serve soltanto durante lo sviluppo.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
L’applicazione si avvia localmente con il file di configurazione fornito. La versione della toolchain è verificabile dai comandi iniziali.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.