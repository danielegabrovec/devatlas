## Risultato

Compila sorgenti UTF-8 separando sorgenti e classi senza richiedere Maven o Gradle.

## Prerequisiti e procedura

1. Installa JDK17+; javac e java devono appartenere a toolchain coerenti.
2. src contiene i sorgenti, bin soltanto .class.
3. --release17 seleziona API e bytecode compatibili con Java17.
4. Su Bash sostituisci New-Item con `mkdir -p bin`; compilazione e avvio restano uguali.

## Verifica

JDK pronto; bin/Main.class è separato dal sorgente.

## Problemi frequenti

UnsupportedClassVersionError indica runtime più vecchio del bytecode; verificare java -version e target --release. Non basta installare il solo JRE per compilare.

Esporta i file mantenendo cartelle e nomi indicati. Tutti i comandi partono dalla radice esportata. L'app consulta ed esporta offline; l'acquisizione iniziale di SDK, estensioni e pacchetti può richiedere rete. I comandi di debug interattivo restano in attesa finché colleghi il debugger. Le istruzioni Windows sono distinte dalle eventuali differenze per Linux/macOS descritte qui. Nessun comando pubblica artefatti su servizi esterni.
