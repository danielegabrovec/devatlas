## Risultato

Dichiara il module path e avvia una console senza dipendenze esterne.

## Prerequisiti e procedura

1. Installa Go1.22+ nel PATH.
2. I file esportati includono già go.mod; in una cartella realmente vuota il comando iniziale sarebbe `go mod init example.test/go_starter`.
3. go env GOMOD deve puntare al file esportato.
4. go run . compila temporaneamente e avvia il package main.

## Verifica

Modulo Go pronto; GOMOD individua la radice corretta.

## Problemi frequenti

go.mod file not found indica directory errata. Non creare moduli annidati senza voler separare i package in progetti distinti.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
