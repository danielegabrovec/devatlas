## Obiettivo
Progetto: mini blog statico con metadata.

La home elenca2articoli; link,404 e metadata funzionano. npm run build produce out per hosting statico.

## Procedura
Esporta tutti i file mantenendo i percorsi indicati. Il codice è completo; esegui i comandi dalla radice esportata. L'installazione iniziale delle dipendenze richiede rete o una cache già disponibile. I contenuti e l'esportazione dal catalogo funzionano offline.

## Controllo
La home elenca2articoli; link,404 e metadata funzionano. npm run build produce out per hosting statico.

## Integrazione
Le risorse in memoria e i dati sintetici servono alla dimostrazione. Per usarli in un progetto esistente conserva il confine tra logica, stato e risorse esterne mostrato dall'esempio.

## Percorsi Windows
Su Windows esporta il progetto in un percorso breve, per esempio C:\Dev. I percorsi annidati generati da Next.js possono superare i limiti di alcuni ambienti Windows e causare EPERM durante il prerender: il QA del catalogo è riuscito usando un percorso breve.