## Risultato

Crea una struttura bin/lib e verifica il manifest con Cargo offline.

## Prerequisiti e procedura

1. Installa Rust tramite rustup e verifica il target host.
2. I file esportati rappresentano lo scheletro iniziale; in una cartella vuota l'alternativa è cargo new.
3. Scegli un nome identificatore minuscolo con underscore per mantenere valido l'import della libreria.
4. cargo check controlla il codice senza generare l'eseguibile finale, run compila e avvia.

## Verifica

Ciao Ada; non viene scaricata alcuna crate perché dependencies è vuoto.

## Problemi frequenti

Se cargo non trova Cargo.toml, apri il terminale nella radice esportata. Un nuovo target installato può richiedere un linker di sistema separato.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
