## Risultato

Definisce punto d'ingresso e script npm per una CLI senza dipendenze.

## Prerequisiti e procedura

1. Installa Node.js22+ con npm; verifica i due comandi di versione.
2. Il package.json esportato sostituisce la configurazione iniziale di npm init.
3. type module rende esplicito ESM; .mjs lo richiederebbe comunque.
4. npm start -- Luca inoltra Luca allo script senza installare dipendenze.

## Verifica

Ciao Luca; npm aggiunge il proprio intestazione prima dell'output dello script.

## Problemi frequenti

Cannot find module indica directory di lavoro errata o file non esportati. Non mescolare require CommonJS con import ESM senza una scelta esplicita.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
