## Obiettivo
Progetto: API spese con validazione e riepilogo.

GET/api/expenses mostra elementi e totale; POST con {name,amount} aggiunge. Persistenza solo nel processo locale: riavvio azzera, deployment multiprocesso non condivide dati.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
GET/api/expenses mostra elementi e totale; POST con {name,amount} aggiunge. Persistenza solo nel processo locale: riavvio azzera, deployment multiprocesso non condivide dati.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.

## Percorsi Windows
Su Windows esporta il progetto in un percorso breve, per esempio C:\Dev. I percorsi annidati generati da Next.js possono superare i limiti di alcuni ambienti Windows e causare EPERM durante il prerender: il QA del catalogo è riuscito usando un percorso breve.