## Schema ripetibile
Lo script ricrea soltanto inventory nel database atlas_demo_schema, quindi elimina i dati di quella collezione. La validazione impone sku testuale e quantità numerica non negativa; l'indice univoco protegge il codice.

## Integrazione
In una migrazione su dati da conservare non usare drop: pianifica collMod e la pulizia dei dati incompatibili. Questa ricetta è un bootstrap di laboratorio da eseguire su un processo locale dedicato.