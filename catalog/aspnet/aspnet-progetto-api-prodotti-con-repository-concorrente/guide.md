## Obiettivo
Progetto: API prodotti con repository concorrente.

POST/products crea, GET elenca e legge per ID. Repository thread safe ma volatile: riavvio azzera. requests.http contiene prove ripetibili.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
POST/products crea, GET elenca e legge per ID. Repository thread safe ma volatile: riavvio azzera. requests.http contiene prove ripetibili.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.