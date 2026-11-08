## Test d'integrazione
Lo script usa soltanto atlas_demo:tests:count e controlla valore e presenza della scadenza. Richiede il processo dedicato già avviato. Con set -euo pipefail gli errori della shell interrompono il test; le risposte logiche vengono confrontate esplicitamente.

## Attestazione
Un controllo sintattico bash -n non esegue questi test e non dimostra la disponibilità di Redis.