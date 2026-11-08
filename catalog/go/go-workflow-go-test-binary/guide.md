## Risultato

Usa test incorporati e build trimpath per ottenere una consegna locale riproducibile rispetto ai percorsi.

## Prerequisiti e procedura

1. Esegui i test nel modulo.
2. Crea dist e compila con trimpath per rimuovere i percorsi locali dagli artefatti di build.
3. Esegui il binario e consegnalo per il medesimo GOOS/GOARCH.
4. Per questi sorgenti puri Go il cross-compiling può usare GOOS/GOARCH; dipendenze cgo richiederebbero toolchain aggiuntive e un nuovo collaudo.

## Verifica

Il test passa e dist/app.exe stampa10; su Linux/macOS usare un nome senza .exe.

## Problemi frequenti

Una race non viene rilevata da go test ordinario: usare -race solo su piattaforme e toolchain supportate. trimpath non sostituisce il controllo delle versioni della toolchain.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
