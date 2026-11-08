## Risultato

Produce JavaScript e .d.ts, verifica il codice emesso e prepara il tarball distribuibile.

## Prerequisiti e procedura

1. Installa il compilatore dichiarato e compila prima dei test.
2. Il test importa dist/index.js, quindi verifica il risultato effettivamente distribuibile.
3. declaration genera i tipi per i consumatori TypeScript.
4. Verifica il contenuto con pack --dry-run e genera il tarball locale.

## Verifica

Un test passa; dist contiene index.js, source map e index.d.ts; npm pack genera catalog-ts-area-0.1.0.tgz.

## Problemi frequenti

ERR_MODULE_NOT_FOUND su dist indica una build mancante. Tenere coerenti exports, percorso emesso e tipo module; non consegnare soltanto il sorgente.ts a un consumatore JavaScript.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
